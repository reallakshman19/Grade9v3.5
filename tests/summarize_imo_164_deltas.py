#!/usr/bin/env python3
"""Fail-closed, scoped #164 baseline delta receipt; never a release/Guardrails PASS."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

PINNED = "778eb35a70517a46108ad0a5dc01dfc89f61c0e3"
GROUPS = ("canonical_severe", "new_canonical_vs_committed_ledger",
          "all_failure_findings", "worse_page_ledger", "pages_site_check")


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def ids(value, label):
    check(isinstance(value, list) and all(isinstance(x, str) and x for x in value),
          f"{label}: expected list of nonempty IDs")
    check(len(value) == len(set(value)), f"{label}: duplicate IDs")
    return set(value)


def receipt(path):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    check(isinstance(data, dict), "receipt must be JSON object")
    return data, hashlib.sha256(raw).hexdigest()


def summarize(g, a, head):
    check(bool(re.fullmatch(r"[0-9a-f]{40}", head)) and head != PINNED,
          "wrong/missing exact head SHA")
    for label, data in (("generator", g), ("assurance", a)):
        check(data.get("pinned_main") == PINNED and data.get("candidate") == head,
              f"{label}: wrong pinned checkout")
    check(g.get("schema") == "imo-164-baseline-differential/1" and
          g.get("scope") == "NARROW_GENERATOR_CHECK_AND_HTML_PARITY",
          "unexpected generator schema or scope")
    check(a.get("schema") == "imo-164-assurance-baseline/1" and
          a.get("scope") == "ASSURANCE_FINDINGS_AND_PAGES_CHECK_ONLY" and
          a.get("global_guardrails_equivalence") == "NOT_ESTABLISHED",
          "unexpected assurance schema/scope/equivalence")
    result = {}
    for group in GROUPS:
        base = ids(a["original_pinned_main"][group], "main." + group)
        current = ids(a["candidate_head"][group], "head." + group)
        d = a["deltas"][group]
        added, removed, same = current-base, base-current, current & base
        check(ids(d["introduced"], group+".introduced") == added and
              ids(d["resolved"], group+".resolved") == removed and
              d["pinned_main_count"] == len(base) and d["pr_count"] == len(current),
              group+": comparison tampered or invalid")
        result[group] = {
            "main_count": len(base), "head_count": len(current),
            "introduced": {"count": len(added), "ids": sorted(added)},
            "resolved": {"count": len(removed), "ids": sorted(removed)},
            "unchanged": {"count": len(same), "ids": sorted(same)},
        }
    new = sum(v["introduced"]["count"] for v in result.values())
    check(a["new_failure_count"] == new and a["differential_pass"] is (new == 0),
          "assurance count/verdict mismatch")
    gen = g["generator"]
    old_stale = ids(gen["baseline"]["stale_paths"], "old_stale")
    new_stale = ids(gen["candidate"]["stale_paths"], "new_stale")
    added_stale = new_stale - old_stale
    check(ids(gen["new_stale_paths"], "added_stale") == added_stale,
          "generator drift comparison mismatch")
    check(isinstance(g["html"], list) and len(g["html"]) == 3,
          "missing HTML comparison scope")
    changed = []
    for row in g["html"]:
        changed.extend(row["manifest"] + ":" + name
                       for name in sorted(ids(row["changed_pages"], "html_changed")))
        check(row["identical"] is (not row["changed_pages"]), "HTML verdict mismatch")
    errors = ids(g["errors"], "generator_errors")
    check(g["parity_pass"] is (not errors) and
          gen["baseline"]["other_failure"] is False and
          gen["candidate"]["other_failure"] is False,
          "generator error or verdict mismatch")
    regression = bool(new or added_stale or changed or errors or
                      (gen["candidate"]["architecture_drift"] is True and
                       gen["baseline"]["architecture_drift"] is False))
    return {
        "schema": "imo-164-ci-delta-summary/1",
        "pinned_main": PINNED, "candidate_head": head,
        "scope": "GENERATED_HTML_ASSURANCE_FINDING_IDENTITIES_PAGES_ONLY",
        "assurance_id_categories": result,
        "generator": {"main_stale": sorted(old_stale), "head_stale": sorted(new_stale),
                      "introduced_stale": sorted(added_stale),
                      "changed_existing_html": changed, "unexpected_errors": sorted(errors),
                      "main_architecture_drift": gen["baseline"]["architecture_drift"],
                      "head_architecture_drift": gen["candidate"]["architecture_drift"]},
        "scoped_verdict": ("INTRODUCED_FINDINGS_HOLD" if regression
                           else "NO_NEW_FINDINGS_IN_COMPARED_SCOPE"),
        "global_guardrails_full_same_runner": "NOT_ESTABLISHED",
        "global_guardrails_absolute": "NOT_ASSESSED_BY_THIS_RECEIPT",
        "canonical_release_eligibility": "NOT_ASSESSED_BY_THIS_RECEIPT",
        "academic_qrt_acceptance": "NOT_GRANTED",
        "source_core2_admission": "NOT_GRANTED",
        "owner_merge_publication_approval": "NOT_GRANTED",
        "release_state": "HOLD",
    }


def main(argv):
    if len(argv) != 4:
        raise SystemExit("usage: <generator.json> <assurance.json> <head-sha> <out.json>")
    try:
        g, g_sha = receipt(argv[0])
        a, a_sha = receipt(argv[1])
        r = summarize(g, a, argv[2])
        r["input_sha256"] = {"generator": g_sha, "assurance": a_sha}
        out = Path(argv[3])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(r, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        print("IMO_164_CI_DELTA_SUMMARY", json.dumps({
            "main": PINNED, "head": r["candidate_head"],
            "scoped_verdict": r["scoped_verdict"],
            "new_id_counts": {k: v["introduced"]["count"]
                              for k, v in r["assurance_id_categories"].items()},
            "release": "HOLD", "global_guardrails": "NOT_ESTABLISHED",
        }, sort_keys=True))
        return 0 if r["scoped_verdict"] == "NO_NEW_FINDINGS_IN_COMPARED_SCOPE" else 1
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"IMO_164_CI_DELTA_SUMMARY_INVALID: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
