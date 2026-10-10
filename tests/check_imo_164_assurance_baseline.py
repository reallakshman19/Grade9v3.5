#!/usr/bin/env python3
"""Compare full, read-only assurance and Pages findings on pinned main versus PR.

This diagnoses inherited debt without updating any ledger, baseline, generated
assets, source custody, QRT, publication route, or protected content. A passing
delta is not a globally passing assurance suite or release clearance.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PINNED = "778eb35a70517a46108ad0a5dc01dfc89f61c0e3"
SNAPSHOT = r'''
import json
import tempfile
from pathlib import Path
from Shared.assurance import baseline, verifiers
from Shared.tools import build_pages_site

repo = Path.cwd()
with tempfile.TemporaryDirectory(prefix="imo-164-assurance-") as temp:
    result = verifiers.run(repo,
        ["Physics/library", "Mathematics/library", "Chemistry/library"],
        ["standalone=standalone"], Path(temp))
    known = baseline.load(repo / "Shared/assurance/baseline.v1.json")
    canonical = baseline.keys(result.evidence)
    new_canonical = baseline.new_findings(result.evidence, known)
    # Include all severities for transparent comparison, not only S0/S1.
    evidence_findings = sorted(set(
        "|".join((e["assurance_type"], e["subject"]["kind"],
                  e["subject"]["id"], f["code"],
                  str(f["subject"]), f["severity"]))
        for e in result.evidence if e["outcome"] == "FAIL"
        for f in e["findings"]
    ))
    statuses = sorted(
        e["assurance_type"] + "|" + e["subject"]["kind"] + ":" +
        e["subject"]["id"] + "|" + e["outcome"]
        for e in result.evidence
    )
    print(json.dumps({
        "canonical_severe": canonical,
        "new_canonical_vs_committed_ledger": new_canonical,
        "all_failure_findings": evidence_findings,
        "outcomes": statuses,
        "worse_page_ledger": sorted(result.ratchet_problems),
        "pages_site_check": sorted(build_pages_site.check(repo)),
        "records": len(result.evidence),
    }, sort_keys=True))
'''

def snapshot(path: Path) -> dict:
    completed = subprocess.run([sys.executable, "-c", SNAPSHOT], cwd=path,
                               capture_output=True, text=True, timeout=240)
    if completed.returncode != 0:
        raise RuntimeError(f"{path.name}: assurance snapshot failed (fail closed): " +
                           (completed.stderr or completed.stdout)[-2500:])
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as exc:
        raise RuntimeError(f"{path.name}: invalid assurance snapshot: " +
                           completed.stdout[-2500:]) from exc

def sha(path: Path) -> str:
    p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path,
                       capture_output=True, text=True, check=True)
    return p.stdout.strip()

def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("usage: <pinned-main-checkout> <exact-pr-checkout> <receipt>")
    main, head, receipt = (Path(x).resolve() for x in argv)
    if sha(main) != PINNED or sha(head) == PINNED:
        raise SystemExit("wrong checked-out commits; no comparison performed")
    baseline, candidate = snapshot(main), snapshot(head)
    groups = (
        "canonical_severe", "new_canonical_vs_committed_ledger",
        "all_failure_findings", "worse_page_ledger", "pages_site_check",
    )
    comparison = {}
    for group in groups:
        old, new = set(baseline[group]), set(candidate[group])
        comparison[group] = {
            "pinned_main_count": len(old),
            "pr_count": len(new),
            "introduced": sorted(new - old),
            "resolved": sorted(old - new),
        }
    # An outcome that worsens from PASS/INCONCLUSIVE to FAIL is included in
    # all_failure_findings; the full status rows are retained for review.
    r = {
        "schema": "imo-164-assurance-baseline/1",
        "pinned_main": sha(main), "candidate": sha(head),
        "scope": "ASSURANCE_FINDINGS_AND_PAGES_CHECK_ONLY",
        "baseline_equivalence": "ONLY_THIS_SCOPED_COMPARISON",
        "global_guardrails_equivalence": "NOT_ESTABLISHED",
        "canonical_assurance_release_pass": False,
        "original_pinned_main": baseline,
        "candidate_head": candidate,
        "deltas": comparison,
        "new_failure_count": sum(len(comparison[g]["introduced"]) for g in groups),
    }
    r["differential_pass"] = r["new_failure_count"] == 0
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    print("PINNED_MAIN_ASSURANCE_DELTA", json.dumps({
        "head": r["candidate"],
        "findings_count_main": len(baseline["canonical_severe"]),
        "findings_count_head": len(candidate["canonical_severe"]),
        "ledger_pages_main": len(baseline["worse_page_ledger"]),
        "ledger_pages_head": len(candidate["worse_page_ledger"]),
        "pages_site_main": len(baseline["pages_site_check"]),
        "pages_site_head": len(candidate["pages_site_check"]),
        "introduced": {g: len(comparison[g]["introduced"]) for g in groups},
        "differential_pass": r["differential_pass"],
        "global_guardrails_equivalence": "NOT_ESTABLISHED",
    }, sort_keys=True))
    return 0 if r["differential_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
