#!/usr/bin/env python3
"""Narrow pinned-main comparison: generated-file drift and existing HTML parity.

Two separate checkouts must be provided; this NEVER certifies the global suite.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PINNED = "778eb35a70517a46108ad0a5dc01dfc89f61c0e3"
MANIFESTS = [
    "golden/units/G-CORE2-R2/manifest.json",
    "golden/units/G-MATH-LINEAR-CONSTRAINT/manifest.json",
    "products/physics/phy-kin-2d-motion.manifest.json",
]

def execute(root: Path, command: list[str], timeout: int = 180):
    return subprocess.run(command, cwd=root, capture_output=True, text=True,
                          check=False, timeout=timeout)

def generator(root: Path):
    p = execute(root, [sys.executable, "Shared/tools/build_manifest.py", "--check"])
    text = p.stdout + "\n" + p.stderr
    stale = sorted(set(re.findall(r"^generated file is stale: (.+)$", text, re.M)))
    return {
        "exit_code": p.returncode,
        "stale_paths": stale,
        "architecture_drift": "architecture manifest has drifted" in text,
        "other_failure": p.returncode != 0 and not stale and
                         "architecture manifest has drifted" not in text,
        "tail": text[-1500:],
    }

def render(root: Path, manifest: str, output: Path):
    p = execute(root, [sys.executable, "Shared/tools/render_core.py", "build",
                       "--manifest", manifest, "--out", str(output),
                       "--draft", "--reference"])
    if p.returncode:
        raise RuntimeError(manifest + ": " + (p.stdout + p.stderr)[-1200:])
    files = list(output.glob("*.html"))
    if not files:
        raise RuntimeError(manifest + ": no rendered HTML pages")
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}

def main(args: list[str]):
    if len(args) != 3:
        raise SystemExit("usage: <main-tree> <candidate-tree> <receipt.json>")
    main_root, candidate, receipt = (Path(v).resolve() for v in args)
    pinned_sha = execute(main_root, ["git", "rev-parse", "HEAD"]).stdout.strip()
    head_sha = execute(candidate, ["git", "rev-parse", "HEAD"]).stdout.strip()
    if pinned_sha != PINNED or not head_sha or head_sha == PINNED:
        raise SystemExit("Checkouts not pinned to distinct commits")
    old = generator(main_root)
    new = generator(candidate)
    r = {
        "schema": "imo-164-baseline-differential/1",
        "pinned_main": pinned_sha,
        "candidate": head_sha,
        "scope": "NARROW_GENERATOR_CHECK_AND_HTML_PARITY",
        "global_ci_equivalence": "NOT_ESTABLISHED",
        "generator": {
            "baseline": old,
            "candidate": new,
            "new_stale_paths": sorted(set(new["stale_paths"]) - set(old["stale_paths"])),
        },
        "html": [],
        "errors": [],
    }
    if old["other_failure"] or new["other_failure"]:
        r["errors"].append("GENERATOR_UNEXPECTED_ERROR")
    with tempfile.TemporaryDirectory(prefix="imo-164-parity-") as tmp:
        for n, manifest in enumerate(MANIFESTS):
            try:
                a = render(main_root, manifest, Path(tmp) / ("main-" + str(n)))
                b = render(candidate, manifest, Path(tmp) / ("pr-" + str(n)))
                diff = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
                r["html"].append({"manifest": manifest,
                                  "pages": len(b), "changed_pages": diff,
                                  "identical": not diff})
                if diff:
                    r["errors"].append("EXISTING_HTML_CHANGED " + manifest)
            except Exception as exc:
                r["errors"].append("RENDER_FAILURE " + manifest + ": " + str(exc))
    r["parity_pass"] = not r["errors"]
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(r, indent=2) + "\n")
    print("PINNED_MAIN_DIFFERENTIAL", json.dumps({
        "head": head_sha, "new_stale_paths": r["generator"]["new_stale_paths"],
        "main_architecture_drift": old["architecture_drift"],
        "candidate_architecture_drift": new["architecture_drift"],
        "pages": r["html"], "parity_pass": r["parity_pass"],
        "errors": r["errors"],
    }))
    if r["errors"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
