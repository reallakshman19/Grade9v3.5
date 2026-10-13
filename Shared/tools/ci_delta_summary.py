#!/usr/bin/env python3
"""Informational exact-ID CI diagnosis; never a replacement for required gates.

Reads run_test_ids.py records. The optional test_ids field proves a
matched collection only when both sides measured the same IDs and both runs
executed their entire collection without loader errors.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


def read_record(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or type(data.get("ran")) is not int or data["ran"] < 0:
        raise ValueError(f"{path}: invalid ran count")
    for field in ("failed", "load_errors"):
        if not isinstance(data.get(field), list) or not all(isinstance(x, str) for x in data[field]):
            raise ValueError(f"{path}: invalid {field}")
    ids = data.get("test_ids")
    if ids is not None and (not isinstance(ids, list) or not all(isinstance(x, str) for x in ids)):
        raise ValueError(f"{path}: invalid test_ids")
    return data


def compare(head: dict, base: dict) -> dict:
    h, b = set(head["failed"]), set(base["failed"])
    hi, bi = head.get("test_ids"), base.get("test_ids")
    issues = []
    if hi is None or bi is None:
        issues.append("TEST_IDS_NOT_RECORDED_ON_BOTH_SIDES")
    else:
        if Counter(hi) != Counter(bi):
            issues.append("TEST_COLLECTION_CHANGED")
        if len(hi) != head["ran"] or len(bi) != base["ran"]:
            issues.append("COLLECTION_EXECUTION_COUNTS_DIFFER")
    if head["ran"] == 0 or base["ran"] == 0:
        issues.append("EMPTY_TEST_RUN")
    if head["load_errors"] or base["load_errors"]:
        issues.append("TEST_MODULE_LOAD_ERRORS")
    return {
        "base_tests_run": base["ran"], "head_tests_run": head["ran"],
        "base_failing_ids": len(b), "head_failing_ids": len(h),
        "new_failing_ids": sorted(h-b), "fixed_ids": sorted(b-h),
        "inherited_failing_ids": sorted(h & b),
        "new_load_error_ids": sorted(set(head["load_errors"])-set(base["load_errors"])),
        "head_load_error_ids": sorted(set(head["load_errors"])),
        "base_load_error_ids": sorted(set(base["load_errors"])),
        "collection_comparable": not issues,
        "comparability_limitations": issues,
        "classification": (
            "NEW_FAILING_IDS_OBSERVED" if h-b else
            "NO_NEW_FAILING_IDS_OBSERVED_NOT_A_GREEN_CI_RESULT"
        ),
    }


def build(head: dict, base: dict, pinned_main: dict, *, checkout_sha: str = "", expected_sha: str = "") -> dict:
    tree_relation = (
        "MATCH" if checkout_sha and expected_sha and checkout_sha == expected_sha else
        "MISMATCH_ACTUAL_CHECKOUT_NOT_EXPECTED_PR_HEAD" if checkout_sha and expected_sha else
        "UNKNOWN_SHA_NOT_SUPPLIED"
    )
    return {
        "schema": "canonical-exact-id-diagnostic/v1", "gate_policy": "INFORMATION_ONLY_EXISTING_GATES_UNCHANGED",
        "absolute_ci": "NOT_EVALUATED_HERE_CHECK_CANONICAL_AND_GUARDRAILS_CONCLUSIONS",
        "checkout_sha": checkout_sha or None, "expected_pr_head_sha": expected_sha or None,
        "checkout_relation": tree_relation,
        "stacked_base": compare(head, base),
        "pinned_main": compare(head, pinned_main),
        "guardrails": "NOT_COMPARED_SEPARATE_REQUIRED_WORKFLOW",
    }


def markdown(report: dict) -> str:
    lines = ["### Exact-ID CI diagnostic (informational; not a gate exemption)", "",
             "All required CI conclusions remain authoritative, including canonical assurance and guardrails.",
             f"Actual checkout vs expected source head: **{report['checkout_relation']}**.", "",
             "| Comparator | Head/base tests | Head/base failed IDs | New | Fixed | Inherited | Same complete test collection? |",
             "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for label in ("stacked_base", "pinned_main"):
        v = report[label]
        complete = "YES" if v["collection_comparable"] else "NO — " + ", ".join(v["comparability_limitations"])
        lines.append(f"| {label.replace('_',' ')} | {v['head_tests_run']}/{v['base_tests_run']} | "
                     f"{v['head_failing_ids']}/{v['base_failing_ids']} | {len(v['new_failing_ids'])} | "
                     f"{len(v['fixed_ids'])} | {len(v['inherited_failing_ids'])} | {complete} |")
        for kind in ("new_failing_ids", "new_load_error_ids"):
            if v[kind]:
                lines.append(f"- **{label} {kind}**: " + ", ".join(chr(96) + t + chr(96) for t in v[kind][:8])
                             + (f" (and {len(v[kind])-8} more)" if len(v[kind]) > 8 else ""))
    lines.extend(["", "**No new observed failures** never means green or release-ready. "
                  "When test populations differ, the exact-ID comparison is diagnostic, not a proof "
                  "that the same coverage was exercised. This tool does not compare guardrail failures "
                  "or override an existing red job."])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    cli.add_argument("--head", required=True)
    cli.add_argument("--base", required=True)
    cli.add_argument("--pinned-main", required=True)
    cli.add_argument("--output", required=True, type=Path)
    cli.add_argument("--summary", type=Path)
    cli.add_argument("--checkout-sha", default="")
    cli.add_argument("--expected-head-sha", default="")
    a = cli.parse_args(argv)
    report = build(read_record(a.head), read_record(a.base), read_record(a.pinned_main),
                   checkout_sha=a.checkout_sha, expected_sha=a.expected_head_sha)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    msg = markdown(report)
    if a.summary:
        with a.summary.open("a", encoding="utf-8") as out:
            out.write(msg)
    else:
        print(msg)
    return 0  # Informational by design; only broken inputs cause nonzero.


if __name__ == "__main__":
    raise SystemExit(main())
