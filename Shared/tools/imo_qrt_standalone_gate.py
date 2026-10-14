#!/usr/bin/env python3
"""Source-safe, read-only independent pre-attempt disclosure audit for IMO research HTML.

Observe actual generated HTML; do not infer academic correctness from its structure.
The approved native product remains Shared/tools/render_core.py, NOT this HTML suite.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ENDPOINTS = (
    "standalone/mathematics-imo-grade9-master-suite.html",
    "public/standalone/mathematics-imo-grade9-master-suite.html",
    "public/test/imo-grade9/core2.html",
    "docs/test/imo-grade9/core2.html",
)
SCHEMA = "imo-qrt-standalone-disclosure-audit/v1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ANSWER_RE = re.compile(r"\b(?:answer|correct\s+(?:choice|option))\s*:\s*(?:option\s*)?\(?[A-D]\)?", re.I)
SUCCESS_STYLE = re.compile(r"(?:var\(--success\)|rgba\(\s*52,\s*211,\s*153|border-color\s*:\s*(?:green|#(?:10b981|34d399)))", re.I)


class DisclosureObserver(HTMLParser):
    """One-pass role-specific HTML parser; avoids regex splitting nested HTML."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: list[dict[str, Any]] = []
        self.card: dict[str, Any] | None = None
        self.details: list[tuple[str, bool]] = []
        self.summary: list[str] | None = None
        self.summary_is_solution = False
        self.duplicate_ids: list[str] = []
        self.seen: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        if tag == "article" and "qb-question" in classes:
            if self.card is not None:
                raise ValueError("NESTED_QB_QUESTION_ARTICLE")
            identifier = a.get("id") or ""
            if not identifier.startswith("q-"):
                raise ValueError("QB_QUESTION_ID_MISSING")
            identifier = identifier[2:]
            if identifier in self.seen:
                self.duplicate_ids.append(identifier)
            self.seen.add(identifier)
            self.card = {"id": identifier, "option_count": 0, "attempt_box": False,
                         "solution_details": 0, "findings": []}
            self.details = []
            return
        if self.card is None:
            return
        if tag == "details":
            self.details.append((a.get("id") or "", "open" in a))
            if "open" in a and (a.get("id") or "").startswith("sol-disc-"):
                self.card["findings"].append("SOLUTION_DISCLOSURE_OPEN_BEFORE_ATTEMPT")
        if tag == "summary":
            self.summary = []
            self.summary_is_solution = bool(self.details and
                self.details[-1][0].startswith("sol-disc-"))
        if "qb-option-card" in classes:
            self.card["option_count"] += 1
            style = a.get("style") or ""
            if SUCCESS_STYLE.search(style) or any(
                "correct" in str(k).lower() or "answer" in str(k).lower()
                for k in a if k.startswith("data-")
            ):
                self.card["findings"].append("PREATTEMPT_CORRECT_OPTION_EMPHASIZED")
        if "qb-attempt-box" in classes:
            self.card["attempt_box"] = True
        if tag == "details" and (a.get("id") or "").startswith("sol-disc-"):
            self.card["solution_details"] += 1

    def handle_data(self, data: str) -> None:
        if self.summary is not None:
            self.summary.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.card is None:
            return
        if tag == "summary" and self.summary is not None:
            visible_summary = " ".join("".join(self.summary).split())
            if self.summary_is_solution and ANSWER_RE.search(visible_summary):
                self.card["findings"].append("PREATTEMPT_ANSWER_IN_VISIBLE_SOLUTION_SUMMARY")
            self.summary = None
            self.summary_is_solution = False
        elif tag == "details" and self.details:
            self.details.pop()
        elif tag == "article":
            if self.card["option_count"] != 4:
                self.card["findings"].append("QUESTION_OPTION_CARD_COUNT_NOT_FOUR")
            if not self.card["attempt_box"]:
                self.card["findings"].append("QUESTION_ATTEMPT_BOX_MISSING")
            if self.card["solution_details"] != 1:
                self.card["findings"].append("QUESTION_SOLUTION_DETAILS_COUNT_INVALID")
            self.card["findings"] = sorted(set(self.card["findings"]))
            self.cards.append(self.card)
            self.card = None
            self.details = []
            self.summary = None


def inspect_html(source: str) -> dict[str, Any]:
    p = DisclosureObserver()
    p.feed(source)
    p.close()
    if p.card is not None:
        raise ValueError("UNCLOSED_QUESTION_ARTICLE")
    counts = Counter(f for card in p.cards for f in card["findings"])
    if p.duplicate_ids:
        counts["DUPLICATE_RENDERED_QUESTION_ID"] += len(p.duplicate_ids)
    return {
        "question_count": len(p.cards),
        "unique_question_ids": len(p.seen),
        "findings": dict(sorted(counts.items())),
        "affected_question_ids": {
            rule: [c["id"] for c in p.cards if rule in c["findings"]]
            for rule in sorted(counts)
        },
    }


def inspect_endpoints(root: Path = ROOT, *, baseline_sha: str, expected_questions: int = 260,
                      endpoints: tuple[str, ...] = ENDPOINTS) -> dict[str, Any]:
    if not SHA_RE.fullmatch(baseline_sha):
        raise ValueError("EXACT_BASELINE_SHA_REQUIRED")
    receipts: list[dict[str, Any]] = []
    missing: list[str] = []
    for rel in endpoints:
        f = root / rel
        if not f.is_file():
            missing.append(rel)
            continue
        raw = f.read_bytes()
        receipts.append({"path": rel, "sha256": sha256(raw).hexdigest(),
                         "bytes": len(raw)})
    issues: list[str] = []
    if missing:
        issues.append("GENERATED_HTML_ENDPOINT_MISSING")
    if len({r["sha256"] for r in receipts}) > 1:
        issues.append("GENERATED_HTML_ENDPOINTS_DIVERGE")
    if not receipts:
        return {"schema": SCHEMA, "baseline_commit": baseline_sha, "status": "FAIL",
                "hard_findings": sorted(set(issues)), "missing": missing,
                "endpoints": receipts, "rendered": None, "academic_verdict": "NOT_RUN"}
    primary = root / next(x["path"] for x in receipts
                          if x["path"] == endpoints[0]) if any(
                              x["path"] == endpoints[0] for x in receipts
                          ) else root / receipts[0]["path"]
    rendered = inspect_html(primary.read_text(encoding="utf-8"))
    if rendered["question_count"] != expected_questions or rendered["unique_question_ids"] != expected_questions:
        issues.append("RENDERED_QUESTION_DENOMINATOR_MISMATCH")
    if rendered["findings"]:
        issues.append("PREATTEMPT_DISCLOSURE_OR_STRUCTURE_FAILURE")
    return {
        "schema": SCHEMA, "baseline_commit": baseline_sha, "status": "FAIL" if issues else "REVIEW_REQUIRED",
        "scope": "RESEARCH_STANDALONE_HTML_ONLY", "academic_verdict": "REVIEW_REQUIRED",
        "source_rights": "NOT_VERIFIED", "native_product_review": "NOT_RUN",
        "hard_findings": sorted(set(issues)), "missing": missing,
        "endpoints": receipts, "rendered": rendered,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--baseline-sha", required=True)
    ap.add_argument("--expected-questions", type=int, default=260)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(argv)
    result = inspect_endpoints(args.root, baseline_sha=args.baseline_sha,
                               expected_questions=args.expected_questions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"schema": result["schema"], "status": result["status"],
                      "hard_findings": result["hard_findings"],
                      "endpoints": result["endpoints"],
                      "rendered_summary": {
                          "question_count": (result["rendered"] or {}).get("question_count", 0),
                          "unique_question_ids": (result["rendered"] or {}).get("unique_question_ids", 0),
                          "findings": (result["rendered"] or {}).get("findings", {})},
                      "academic_verdict": result["academic_verdict"]}, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
