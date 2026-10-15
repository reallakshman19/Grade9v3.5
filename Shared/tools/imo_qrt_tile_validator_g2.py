#!/usr/bin/env python3
"""Read-only, exact-source QRT tile inspection. Mechanical PASS is not academic approval.

Run from a checkout of the frozen source commit with this validator overlaid.
The HTML fixer owns the question banks, generator and all HTML endpoints.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from typing import Any
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Shared.tools import question_difficulty, question_review_matrix
from Shared.tools import imo_qrt_validator, imo_qrt_standalone_gate
from Shared.tools import imo_qrt_core_relationships

ROOT = Path(__file__).resolve().parents[2]
REVIEW_PATH = ROOT / "TEST/imo-qrt-tile/qrt-retrieve-d1-review.v1.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
TILE_RE = re.compile(r"^QRT-(RETRIEVE|EXPLAIN|APPLY|MODEL|REPRESENT|SYNTHESIZE|JUSTIFY)-(D[1-4])$")


def _emit(out: list[dict[str, str]], *, verdict: str, rule: str, code: str,
          location: str, detail: str = "") -> None:
    out.append({"verdict": verdict, "rule": rule, "code": code,
                "location": location, "detail": detail})


def _article(html: str, qid: str) -> tuple[str, str] | None:
    # Generated question articles cannot nest. Use bounded article extraction,
    # not a regex intended to parse arbitrary HTML trees.
    opener = re.compile(r'<article\b([^>]*\bclass="[^"]*\bqb-question\b[^"]*"[^>]*)>',
                        re.I)
    for match in opener.finditer(html):
        attrs = match.group(1)
        if re.search(r'\bid="q-' + re.escape(qid) + r'"', attrs):
            close = html.find("</article>", match.end())
            if close == -1:
                return attrs, ""
            return attrs, html[match.end():close]
    return None


def _tag_attributes(fragment: str, tag: str, element_id: str) -> dict[str, str | None] | None:
    """Read initial markup attributes of an identified element."""
    for m in re.finditer(r"<" + tag + r"\b([^>]*)>", fragment, re.I | re.S):
        attrs = dict((k.lower(), v) for k, v in re.findall(
            r"""([-\w:]+)\s*=\s*["']([^"']*)["']""", m.group(1)))
        if attrs.get("id") == element_id:
            for k in ("hidden", "inert", "open", "disabled"):
                if re.search(r"\b" + k + r"(?:\s|=|$)", m.group(1), re.I):
                    attrs[k] = ""
            return attrs
    return None


def _mechanical_source(q: dict[str, Any], file: str) -> list[dict[str, str]]:
    loc = f"Mathematics/question-bank/{file}#{q['id']}"
    old = imo_qrt_validator.check_one(q)
    out = []
    for f in old["findings"]:
        if f["verdict"] == "FAIL":
            _emit(out, verdict="FAIL", rule=f["rule"], code=f["evidence"],
                  location=loc + ".cognitive_classification")
    return out


def _html_findings(html: str, q: dict[str, Any],
                   disclosure: dict[str, Any]) -> list[dict[str, str]]:
    qid = q["id"]
    loc = "standalone/mathematics-imo-grade9-master-suite.html#q-" + qid
    found = _article(html, qid)
    out: list[dict[str, str]] = []
    if found is None:
        _emit(out, verdict="FAIL", rule="V02", code="RENDERED_TILE_CARD_MISSING",
              location=loc)
        return out
    attrs, card = found
    cls = q["cognitive_classification"]
    for name, expected in (("data-demand", cls["primary_demand"]),
                           ("data-band", cls["difficulty_band"])):
        if not re.search(r'\b' + name + r'="' + re.escape(expected) + r'"', attrs):
            _emit(out, verdict="FAIL", rule="V08", code="RENDERED_TILE_ATTRIBUTE_MISMATCH",
                  location=loc + "@" + name)
    for rule, idbase in (("V10", "sol-disc-"), ("V10", "diag-disc-"),
                         ("H1-H2", "hint2-")):
        attrs2 = _tag_attributes(card, "details", idbase + qid)
        if attrs2 is None or "hidden" not in attrs2 or "inert" not in attrs2 or "open" in attrs2:
            _emit(out, verdict="FAIL", rule=rule, code="PRECOMMIT_DISCLOSURE_NOT_LOCKED",
                  location=loc + " #" + idbase + qid)
    if _tag_attributes(card, "textarea", "att-" + qid) is None:
        _emit(out, verdict="FAIL", rule="V10", code="ATTEMPT_TEXTAREA_MISSING",
              location=loc + " #att-" + qid)
    if _tag_attributes(card, "button", "commit-" + qid) is None:
        _emit(out, verdict="FAIL", rule="V10", code="KEYBOARD_COMMIT_BUTTON_MISSING",
              location=loc + " #commit-" + qid)
    # Inline spans cannot receive focus or keyboard activation by default.
    if re.search(r'<span\b[^>]*onclick="jumpToCore1\(', card):
        _emit(out, verdict="FAIL", rule="P2", code="CORE_NAV_MOUSE_ONLY_SPAN",
              location=loc + " .qb-badges span[onclick*=jumpToCore1]")
    for problem, ids in (disclosure.get("affected_question_ids") or {}).items():
        if qid in ids:
            _emit(out, verdict="FAIL", rule="V10", code=problem, location=loc)
    return out


def _protected_w(q: dict[str, Any], evidence: dict[str, Any]) -> list[dict[str, str]]:
    """Conservative question-specific inspection of D1 protected final decision.

    A manual witness stays tied to the exact offending authored hint: it ceases
    to be a FAIL when the hint changes, and must then be independently reviewed.
    """
    ref = (evidence.get("cases") or {}).get(q["id"])
    if not ref:
        return []
    h2 = ((q.get("hint_ladder") or {}).get("hint2_tactical_step") or "")
    if not isinstance(h2, str):
        return []
    markers = ref.get("markers", [])
    if not markers or not all(token in h2 for token in markers):
        return []
    out: list[dict[str, str]] = []
    _emit(out, verdict="FAIL", rule="P1/H2/W",
          code="HINT2_REVEALS_D1_PROTECTED_FINAL_DECISION",
          location=f"Mathematics/question-bank/{ref['bank']}#{q['id']}.hint_ladder.hint2_tactical_step",
          detail=ref["why"])
    return out


def inspect(root: Path, *, source_sha: str, tile: str = "QRT-RETRIEVE-D1",
            review: dict[str, Any] | None = None) -> dict[str, Any]:
    if not SHA_RE.fullmatch(source_sha):
        raise ValueError("EXACT_40_CHARACTER_SOURCE_COMMIT_REQUIRED")
    m = TILE_RE.fullmatch(tile)
    if not m:
        raise ValueError("INVALID_QRT_TILE_ID")
    demand, band = m.groups()
    # The selected QRT cell is compiled from the repository's canonical
    # qualitative matrix; never infer cell from percentages or numeric quality.
    templates = question_review_matrix.compile_templates(
        question_review_matrix.load(root / "Shared/quality/question-demand-matrix.v1.json"),
        question_review_matrix.load(root / "Shared/vocabularies/cognitive-demand.v1.json"))
    if len(templates) != 28 or tile not in {t["template_id"] for t in templates}:
        raise ValueError("CANONICAL_QRT_TEMPLATE_NOT_FOUND")
    rubric = json.loads((root / "Shared/vocabularies/learner-question-metadata.v1.json").read_text())
    if tuple(rubric["question_difficulty_component_rubric"]["components"]) != question_difficulty.COMPONENT_KEYS:
        raise ValueError("FIVE_FACTOR_RUBRIC_KEY_DRIFT")
    if review is None:
        review = json.loads((root / "TEST/imo-qrt-tile/qrt-retrieve-d1-review.v1.json").read_text())
    source_qs = []
    for bank in imo_qrt_validator.BANKS:
        data = json.loads((root / "Mathematics/question-bank" / bank).read_text())
        for q in data["questions"]:
            cls = q.get("cognitive_classification") or {}
            if cls.get("primary_demand") == demand and cls.get("difficulty_band") == band:
                source_qs.append((bank, q))
    if not source_qs:
        raise ValueError("EMPTY_TILE_FAIL_CLOSED")
    actual_html_path = root / imo_qrt_standalone_gate.ENDPOINTS[0]
    html = actual_html_path.read_text(encoding="utf-8")
    disclosure = imo_qrt_standalone_gate.inspect_html(html)
    endpoint_bytes = []
    from hashlib import sha256
    for endpoint in imo_qrt_standalone_gate.ENDPOINTS:
        data = (root / endpoint).read_bytes()
        endpoint_bytes.append({"path": endpoint, "sha256": sha256(data).hexdigest(),
                               "bytes": len(data)})
    if len({x["sha256"] for x in endpoint_bytes}) != 1:
        raise ValueError("HTML_FOUR_ENDPOINT_PARITY_FAILED")
    if disclosure["question_count"] != 260 or disclosure["unique_question_ids"] != 260:
        raise ValueError("RENDERED_CORPUS_NOT_260_UNIQUE")
    relationship = imo_qrt_core_relationships.audit(root=root, baseline_sha=source_sha)
    links = {x["id"]: x for x in relationship["questions"]}
    report = []
    for bank, q in source_qs:
        qid = q["id"]
        findings = _mechanical_source(q, bank)
        findings.extend(_html_findings(html, q, disclosure))
        findings.extend(_protected_w(q, review))
        rel = links.get(qid)
        if rel is None or rel["relationship"] != "EXPLICIT_UNIT_ID":
            _emit(findings, verdict="FAIL", rule="P2/V19",
                  code="EXACT_CORE_CONCEPT_LINK_MISSING",
                  location=(f"Mathematics/question-bank/{bank}#{qid}.taxonomy.subtopic"
                            + " → Core1A.linked_core2_refs"),
                  detail=(rel or {}).get("relationship", "NO_LINK_RECORD"))
        else:
            _emit(findings, verdict="REVIEW_REQUIRED", rule="P2/V19",
                  code="CORE_EXPLICIT_LINK_CRUX_MATCH_UNREVIEWED",
                  location=f"Core1A.linked_core2_refs#{qid}")
        # Mechanical scan is not a KaTeX browser proof or semantic judgement.
        if not all(x in html for x in ('id="offline-katex-core"', 'id="offline-katex-auto"',
                                       "renderMathInElement")):
            _emit(findings, verdict="FAIL", rule="V03", code="KATEX_RENDERER_MISSING",
                  location=imo_qrt_standalone_gate.ENDPOINTS[0])
        else:
            _emit(findings, verdict="REVIEW_REQUIRED", rule="S1-S3",
                  code="KATEX_BROWSER_RENDER_NOT_ATTESTED",
                  location=actual_html_path.as_posix() + "#q-" + qid)
        _emit(findings, verdict="REVIEW_REQUIRED", rule="V07/P3/M1-M3",
              code="QRT_SEMANTIC_AND_MATH_JUSTIFICATION_PENDING",
              location=f"Mathematics/question-bank/{bank}#{qid}")
        hard = [f for f in findings if f["verdict"] == "FAIL"]
        report.append({"id": qid, "source": f"Mathematics/question-bank/{bank}",
                       "verdict": "FAIL" if hard else "PASS",
                       "academic_verdict": "REVIEW_REQUIRED",
                       "findings": findings})
    return {
        "schema": "qrt-tile-validator-g2/v1", "source_commit": source_sha,
        "tile": tile, "template": next(t for t in templates if t["template_id"] == tile),
        "question_count": len(report), "fail_questions": sum(q["verdict"] == "FAIL" for q in report),
        "fail_findings": dict(sorted(Counter(f["code"] for q in report
                    for f in q["findings"] if f["verdict"] == "FAIL").items())),
        "html_endpoints": endpoint_bytes, "html_disclosure": disclosure["findings"],
        "academic_approval": "NOT_GRANTED", "source_rights": "NOT_VERIFIED",
        "status": "FAIL" if any(q["verdict"] == "FAIL" for q in report) else "REVIEW_REQUIRED",
        "questions": report,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--tile", default="QRT-RETRIEVE-D1")
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    sha = subprocess.check_output(["git", "-C", str(args.root), "rev-parse", "HEAD"], text=True).strip()
    if sha != args.source_sha:
        raise SystemExit("SOURCE_COMMIT_NOT_PINNED: checked-out=" + sha)
    output = inspect(args.root, source_sha=args.source_sha, tile=args.tile)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: output[k] for k in
          ("schema", "source_commit", "tile", "question_count", "fail_questions",
           "fail_findings", "html_endpoints", "html_disclosure", "academic_approval")}, indent=2))
    print("QUESTION_FINDINGS_BEGIN")
    for row in output["questions"]:
        hard = [f for f in row["findings"] if f["verdict"] == "FAIL"]
        if hard:
            for f in hard:
                print(f"{row['id']} | FAIL | {f['rule']}/{f['code']} | {f['location']}")
        else:
            print(f"{row['id']} | PASS | mechanical checks | {row['source']}#{row['id']}")
    print("QUESTION_FINDINGS_END")
    return 1 if output["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
