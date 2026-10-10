#!/usr/bin/env python3
"""Replay all executable Guardrails steps on two checkouts in ONE runner.

The native guardrails workflow retains sole authority for absolute PASS/FAIL.
This is a same-runner full run-command differential, not a replacement for
GitHub Actions setup/checkout/upload actions, release or academic review.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BASE_SHA = "778eb35a70517a46108ad0a5dc01dfc89f61c0e3"
WORKFLOW_BLOB = "ac1397685bf522ccbaed9df88af6e52496fdf5f6"
WORKFLOW_PATH = ".github/workflows/guardrails.yml"
ALLOWED_ACTIONS = {
    "actions/checkout@v4", "actions/setup-python@v5",
    "actions/upload-artifact@v4",
}
HEADER = re.compile(r"^(?:FAIL|ERROR):\s+.+", re.M)


def demand(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=root, check=True,
                       capture_output=True, text=True)
    return p.stdout.strip()


def load_steps(root: Path) -> list[tuple[str, str]]:
    # Only paired-replay CI needs PyYAML; ordinary research test discovery does not.
    import yaml
    path = root / WORKFLOW_PATH
    demand(git(root, "hash-object", WORKFLOW_PATH) == WORKFLOW_BLOB,
           "guardrails.yml blob changed; cannot replay under approved contract")
    source = yaml.safe_load(path.read_text(encoding="utf-8"))
    demand(isinstance(source, dict), "guardrails workflow not a mapping")
    jobs = source.get("jobs", {})
    demand(isinstance(jobs, dict) and set(jobs) == {"guardrails"},
           "unexpected guardrails job topology")
    job = jobs["guardrails"]
    demand(isinstance(job, dict), "invalid guardrails job")
    demand(job.get("runs-on") == "ubuntu-latest",
           "native runner topology differs")
    steps = job.get("steps")
    demand(isinstance(steps, list), "missing guardrails steps")
    scripts = []
    for i, step in enumerate(steps):
        demand(isinstance(step, dict), f"step {i}: not a mapping")
        unsupported = ("env", "working-directory", "continue-on-error",
                       "shell", "timeout-minutes")
        demand(not any(k in step for k in unsupported)
               and not ("run" in step and "with" in step),
               f"step {i}: unsupported semantics for replay")
        if "uses" in step:
            demand(step["uses"] in ALLOWED_ACTIONS,
                   f"step {i}: unsupported external action {step['uses']}")
            continue
        demand(isinstance(step.get("name"), str)
               and isinstance(step.get("run"), str),
               f"step {i}: missing run script/name")
        conditional = step.get("if")
        demand(conditional is None or (
            isinstance(conditional, str)
            and conditional.strip().endswith("!cancelled() }}")),
            f"step {i}: condition not faithfully replayable")
        scripts.append((step["name"], step["run"]))
    demand(len(scripts) >= 40, "Guardrails command coverage unexpectedly small")
    demand(len({name for name, _ in scripts}) == len(scripts),
           "duplicate guardrails step names")
    return scripts


def headers(text: str) -> list[str]:
    return sorted(line.strip() for line in text.splitlines()
                  if HEADER.match(line.strip()))


def compare(base: list[dict], head: list[dict]) -> dict:
    demand(len(base) == len(head) and len(base) >= 40,
           "missing full step coverage")
    demand([x["name"] for x in base] == [x["name"] for x in head],
           "named step list differs")
    demand(all(isinstance(row.get("exit_code"), int)
               and isinstance(row.get("failure_headers"), list)
               for row in base + head), "invalid step receipt")
    old = Counter(f'{row["name"]} :: {identity}'
                  for row in base for identity in row["failure_headers"])
    new = Counter(f'{row["name"]} :: {identity}'
                  for row in head for identity in row["failure_headers"])
    introduced = sorted((new - old).elements())
    resolved = sorted((old - new).elements())
    unchanged = sorted((new & old).elements())
    old_failed = set(x["name"] for x in base if x["exit_code"] != 0)
    new_failed = set(x["name"] for x in head if x["exit_code"] != 0)
    introduced_steps = sorted(new_failed - old_failed)
    resolved_steps = sorted(old_failed - new_failed)
    return {
        "baseline_failing_step_names": sorted(old_failed),
        "candidate_failing_step_names": sorted(new_failed),
        "introduced_failing_steps": introduced_steps,
        "resolved_failing_steps": resolved_steps,
        "baseline_header_count": sum(old.values()),
        "candidate_header_count": sum(new.values()),
        "introduced_failure_ids": introduced,
        "resolved_failure_ids": resolved,
        "unchanged_failure_ids": unchanged,
        "absolute_baseline": "FAIL" if old_failed else "PASS",
        "absolute_candidate": "FAIL" if new_failed else "PASS",
        "differential_status": (
            "INTRODUCED_FAILURE_HOLD" if introduced or introduced_steps
            else "NO_NEW_FAILURE_IDENTITIES_OR_STEPS"
        ),
    }


def replay(root: Path, scripts: list[tuple[str, str]], logs: Path) -> list[dict]:
    logs.mkdir(parents=True, exist_ok=True)
    temp = logs / "runner-temp"
    temp.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["GITHUB_WORKSPACE"] = str(root.resolve())
    env["TMPDIR"] = str(temp.resolve())
    env["TMP"] = env["TMPDIR"]
    env["TEMP"] = env["TMPDIR"]
    rows = []
    for n, (name, script) in enumerate(scripts, 1):
        path = logs / f"step-{n:02d}.sh"
        log = logs / f"step-{n:02d}.log"
        path.write_text(script + "\n", encoding="utf-8")
        begun = time.monotonic()
        try:
            p = subprocess.run(
                ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail",
                 str(path.resolve())],
                cwd=root, capture_output=True, text=True, errors="replace",
                env=env, timeout=1200,
            )
            status = p.returncode
            combined = p.stdout + "\n" + p.stderr
        except subprocess.TimeoutExpired as exc:
            status = 124
            out = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            combined = out + "\n" + err + "\nSTEP_TIMED_OUT"
        log.write_text(combined, encoding="utf-8")
        row = {
            "name": name, "exit_code": status, "elapsed_s": round(time.monotonic()-begun, 1),
            "log": log.name, "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
            "failure_headers": headers(combined),
        }
        rows.append(row)
        print("GUARDRAILS_PAIRED_STEP", json.dumps({
            "checkout": root.name, "number": n, "total": len(scripts),
            "step": name, "exit_code": status,
            "failure_headers": len(row["failure_headers"]),
        }), flush=True)
    return rows


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        raise SystemExit(
            "usage: <pinned-main-tree> <exact-pr-tree> <exact-pr-sha> <output-dir>"
        )
    baseline, candidate, sha, output = (
        Path(argv[0]).resolve(), Path(argv[1]).resolve(), argv[2],
        Path(argv[3]).resolve()
    )
    demand(bool(re.fullmatch("[0-9a-f]{40}", sha)) and sha != BASE_SHA,
           "invalid candidate SHA")
    demand(baseline != candidate and git(baseline, "rev-parse", "HEAD") == BASE_SHA
           and git(candidate, "rev-parse", "HEAD") == sha,
           "incorrect independent checkout SHAs")
    scripts = load_steps(baseline)
    demand(load_steps(candidate) == scripts, "baseline/HEAD command drift")
    output.mkdir(parents=True, exist_ok=True)
    base_rows = replay(baseline, scripts, output/"main")
    head_rows = replay(candidate, scripts, output/"candidate")
    delta = compare(base_rows, head_rows)
    summary = {
        "schema": "imo-164-full-guardrails-paired-replay/1",
        "pinned_main": BASE_SHA, "candidate_head": sha,
        "workflow_git_blob": WORKFLOW_BLOB,
        "environment": {
            "runner_image_os": os.environ.get("ImageOS", "UNKNOWN"),
            "runner_image_version": os.environ.get("ImageVersion", "UNKNOWN"),
            "python": sys.version.split()[0],
        },
        "scope": "SAME_RUNNER_ALL_EXECUTABLE_GUARDRAILS_STEPS",
        "native_action_equivalence": "NOT_CLAIMED_CHECKOUT_SETUP_AND_UPLOAD_ACTIONS_NOT_REPLAYED",
        "commands_executed_each": len(scripts), "main": base_rows,
        "head": head_rows, "delta": delta,
        "native_guardrails_pass": "NOT_SUBSTITUTED",
        "release_state": "HOLD",
        "source_core2_admission": "NOT_GRANTED",
        "qrt_acceptance": "NOT_GRANTED",
        "owner_publication_approval": "NOT_GRANTED",
    }
    (output/"paired-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print("GUARDRAILS_PAIRED_SUMMARY", json.dumps({
        "main": BASE_SHA, "head": sha,
        "steps_per_checkout": len(scripts),
        "main_failing_steps": len(delta["baseline_failing_step_names"]),
        "head_failing_steps": len(delta["candidate_failing_step_names"]),
        "main_fail_ids": delta["baseline_header_count"],
        "head_fail_ids": delta["candidate_header_count"],
        "new_fail_ids": len(delta["introduced_failure_ids"]),
        "new_failed_steps": len(delta["introduced_failing_steps"]),
        "delta": delta["differential_status"],
        "absolute_head": delta["absolute_candidate"],
        "release_state": "HOLD",
    }, sort_keys=True))
    return 0 if delta["differential_status"] == "NO_NEW_FAILURE_IDENTITIES_OR_STEPS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError,
            ImportError) as exc:
        print("GUARDRAILS_PAIRED_INVALID", exc, file=sys.stderr)
        raise SystemExit(2)
