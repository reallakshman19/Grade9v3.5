#!/usr/bin/env python3
"""Independent QRT-RETRIEVE-D1 tile audit: source and actual research HTML.

Hard FAILs are actionable; unreviewed academic scoring, Core admission, and
browser runtime are separately recorded. No source, scores, or HTML are mutated.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Shared.tools import question_difficulty
from Shared.tools import question_review_matrix as qrt
from Shared.tools.imo_qrt_core_relationships import audit as audit_core
from Shared.tools.imo_qrt_validator import BANKS, BANK_DIR
from Shared.tools.imo_qrt_standalone_gate import ENDPOINTS

TILE = "QRT-RETRIEVE-D1"
SCHEMA = "imo-qrt-tile-validator/v1"
CARD = re.compile(r'<article class="qb-question"\s+id="q-([^"]+)"([^>]*)>(.*?)</article>', re.S)
SHA = re.compile(r"^[a-f0-9]{40}$")
OPTION_GOOD = re.compile(r'(?:--success|correct_style|data-correct|data-answer)', re.I)


class Elements(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.attrs: list[tuple[str, dict[str, str | None]]] = []
        self.current: list[str] = []
        self.text_by_id: dict[str, str] = {}
        self.stack: list[tuple[str, str | None]] = []
        self.fragments: dict[str, list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        self.attrs.append((tag, a))
        ident = a.get("id")
        self.stack.append((tag, ident))
        if ident:
            self.fragments.setdefault(ident, [])
        for parent_tag, parent_id in self.stack:
            if parent_id:
                self.fragments.setdefault(parent_id, []).append("<" + tag + ">")

    def handle_data(self, data: str) -> None:
        for _, ident in self.stack:
            if ident:
                self.fragments.setdefault(ident, []).append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.stack:
            while self.stack:
                t, _ = self.stack.pop()
                if t == tag:
                    break

    def element(self, ident: str) -> tuple[str, dict[str, str | None]] | None:
        return next(((tag, attrs) for tag, attrs in self.attrs
                     if attrs.get("id") == ident), None)

    def text(self, ident: str) -> str:
        return unescape(" ".join(self.fragments.get(ident, [])))


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKC", unescape(text)).casefold()
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\\(?:left|right|mathrm|text)\b", "", text)
    return re.sub(r"[\s$\{\}\\]", "", text)


def answer_leaked(hint: str, answer: str) -> bool:
    """An exact answer in pre-commit support is a defect, including short answers.

    For a single digit, require an answer-definition context; do not flag any
    incidental 0 in an example. Semantic paraphrases remain a human review.
    """
    a = normalized(answer)
    h = normalized(hint)
    if not a:
        return False
    if len(a) == 1:
        return bool(re.search(r"(?:identity|answer|isalways|equals|mustbe|=\s*)[:=]?" +
                              re.escape(a) + r"(?![0-9])", h))
    if len(a) <= 3 and a.isdigit():
        return bool(re.search(r"(?:answer|result|equals|is|=)" + re.escape(a) + r"(?![0-9])", h))
    return a in h


def inspect_card(question: dict[str, Any], attrs: str, body: str, *,
                 core_review: dict[str, Any], global_guard: bool) -> dict[str, Any]:
    qid = question["id"]
    cls = question["cognitive_classification"]
    elem = Elements()
    elem.feed(body)
    findings: list[dict[str, str]] = []
    holds: list[str] = []

    def fail(rule: str, element: str, detail: str) -> None:
        findings.append({"rule": rule, "element": element, "detail": detail})

    band = cls["difficulty_band"]
    demand = cls["primary_demand"]
    if not re.search(r'data-band="' + re.escape(band) + '"', attrs) or not re.search(
        r'data-demand="' + re.escape(demand) + '"', attrs
    ) or TILE not in body:
        fail("T01_DECLARED_CELL_HTML_MISMATCH", "article[data-band][data-demand] .qb-badge-qrt",
             "Rendered tile/band/demand must match immutable source QRT-RETRIEVE-D1")
    options = [a for tag, a in elem.attrs if "qb-option-card" in (a.get("class") or "").split()]
    if len(options) != 4:
        fail("T02_OPTION_CARD_COUNT", ".qb-options-grid .qb-option-card",
             f"Expected four source-ordered options, found {len(options)}")
    elif any(OPTION_GOOD.search(str(a)) for a in options):
        fail("T03_PREATTEMPT_OPTION_STYLING", ".qb-options-grid .qb-option-card",
             "Correct answer is marked before a committed attempt")
    ids = [a.get("id") for _, a in elem.attrs if a.get("id")]
    if len(ids) != len(set(ids)):
        fail("T04_DUPLICATE_CARD_DOM_ID", "article", "Duplicate id within question card")
    for kind, tag in (("att-", "textarea"), ("commit-", "button"), ("feedback-", "p"),
                      ("hint1-", "details"), ("hint2-", "details"), ("sol-disc-", "details"),
                      ("diag-disc-", "details")):
        item = elem.element(kind + qid)
        if not item or item[0] != tag:
            fail("T05_ATTEMPT_OR_SUPPORT_ELEMENT_MISSING", "#" + kind + qid,
                 "Expected exactly one " + tag + " with stable source question ID")
    for kind in ("hint2-", "sol-disc-", "diag-disc-"):
        item = elem.element(kind + qid)
        if item:
            a = item[1]
            if "hidden" not in a or "inert" not in a or "open" in a:
                fail("T06_PRECOMMIT_DISCLOSURE_UNLOCKED", "#" + kind + qid,
                     "Tier2/solution/diagnosis must initially be hidden inert and not open")
    sol = elem.element("sol-disc-" + qid)
    if sol and not re.search(r"Verified Answer:\s*Option\s*\(" +
                             re.escape(question["answer"]["choice"]) + r"\)", elem.text("sol-disc-" + qid)):
        fail("T07_POSTCOMMIT_CHECK_MISSING", "#sol-disc-" + qid,
             "Post-commit solution must contain source answer/check; this does not certify math")
    button = elem.element("commit-" + qid)
    if button and ("commitResearchAttempt(" not in (button[1].get("onclick") or "")
                   or button[1].get("aria-controls") != "sol-disc-" + qid):
        fail("T08_COMMIT_WIRING_MISSING", "#commit-" + qid,
             "Button must connect the attempt to hidden solution")
    if not global_guard:
        fail("T09_GLOBAL_GUARD_OR_MATH_VENDOR_MISSING", "script#offline-katex-core, commitResearchAttempt",
             "Offline KaTeX + pre-commit write guard must be available")
    ladder = question.get("hint_ladder") or {}
    for kind, key in (("hint1-", "hint1_conceptual_nudge"), ("hint2-", "hint2_tactical_step")):
        source_hint = str(ladder.get(key) or "")
        rendered_hint = elem.text(kind + qid)
        if not source_hint.strip() or not rendered_hint.strip():
            fail("T10_EMPTY_HINT", "#" + kind + qid,
                 "Hint tier must preserve a meaningful question-specific clue")
        elif answer_leaked(source_hint, str(question["answer"]["value"])) or answer_leaked(
                rendered_hint, str(question["answer"]["value"])):
            fail("T11_PRECOMMIT_PROTECTED_W_LEAK", "#" + kind + qid,
                 "Pre-commit support discloses the final retrieval/classification answer")
    if core_review.get("same_inferential_jump_proven") is not True:
        fail("T12_CORE_P2_CRUX_BRIDGE_UNPROVEN",
             "article .qb-badge[onclick*='jumpToCore1']",
             core_review.get("code", "NO_EXPLICIT_CRUX_LINK") +
             ": topic routing/unit declaration does not evidence an exact concept bridge")
    if not elem.element("hint1-" + qid) or not elem.element("hint2-" + qid):
        fail("T13_HINT_PROGRESSIVE_SEQUENCE_MISSING", ".qb-support-container",
             "H1 conceptual → H2 tactical support stages not present")
    holds.append("V06_AUTHORED_FACTORS_ACADEMIC_UNREVIEWED")
    holds.append("QRT_RETRIEVE_DECISIVE_ACT_AND_W_SEMANTIC_REVIEW_REQUIRED")
    holds.append("BROWSER_KATEX_RENDER_AND_COMMIT_INTERACTION_NOT_RUN_STATIC_ONLY")
    factors = cls.get("difficulty_components")
    numerical = {"stored_score": cls.get("difficulty_score"),
                 "stored_band": band, "derived_score": None, "derived_band": None,
                 "consistency": "NOT_DERIVABLE"}
    if isinstance(factors, dict) and set(factors) == set(question_difficulty.COMPONENT_KEYS) and all(
            type(x) is int and 0 <= x <= 2 for x in factors.values()):
        derived = sum(factors.values())
        derived_band = question_difficulty.band_for_score(derived)
        numerical.update({"derived_score": derived, "derived_band": derived_band,
                          "consistency": "MATCH" if (
                              cls.get("difficulty_score") == derived and band == derived_band
                          ) else "FINDING_ONLY_NO_SILENT_RECLASSIFICATION"})
    else:
        holds.append("FIVE_FACTOR_MISSING_OR_INVALID")
    return {
        "id": qid, "tile": TILE,
        "verdict": "FAIL" if findings else "PASS",
        "html_anchor": "#q-" + qid,
        "source_cell": cls.get("qrt_cell"),
        "findings": findings, "numerical": numerical, "holds": holds,
        "core_review": core_review,
    }


def inspect_tile(*, root: Path, source_commit: str) -> dict[str, Any]:
    if not SHA.fullmatch(source_commit):
        raise ValueError("EXACT_SOURCE_SHA_REQUIRED")
    matrix = qrt.load(root / "Shared/quality/question-demand-matrix.v1.json")
    vocab = qrt.load(root / "Shared/vocabularies/cognitive-demand.v1.json")
    templates = qrt.compile_templates(matrix, vocab)
    model = next(t for t in templates if t["template_id"] == TILE)
    if model["demand"] != "RETRIEVE" or model["band"] != "D1" or not model["slots"]["W"]:
        raise ValueError("CANONICAL_QRT_RETRIEVE_D1_TEMPLATE_MISMATCH")
    found = {}
    for filename in BANKS:
        for q in json.loads((root / BANK_DIR.relative_to(ROOT) / filename).read_text(encoding="utf-8"))["questions"]:
            if q.get("cognitive_classification", {}).get("qrt_cell") == TILE:
                if q["id"] in found:
                    raise ValueError("DUPLICATE_SOURCE_TILE_QUESTION_ID:" + q["id"])
                found[q["id"]] = q
    core = audit_core(root=root, baseline_sha=source_commit)
    relationships = {x["question_id"]: x for x in core["relationship_review_queue"]}
    htmls = []
    for relative in ENDPOINTS:
        path = root / relative
        if not path.is_file():
            htmls.append({"path": relative, "sha256": None})
        else:
            htmls.append({"path": relative, "sha256": sha256(path.read_bytes()).hexdigest()})
    if None in [h["sha256"] for h in htmls] or len({h["sha256"] for h in htmls}) != 1:
        raise ValueError("FOUR_HTML_ENDPOINTS_MISSING_OR_DIVERGENT")
    path = root / ENDPOINTS[0]
    source = path.read_text(encoding="utf-8")
    matches = list(CARD.finditer(source))
    cards: dict[str, tuple[str, str]] = {}
    for m in matches:
        if m.group(1) in cards:
            raise ValueError("DUPLICATE_HTML_QUESTION:" + m.group(1))
        cards[m.group(1)] = (m.group(2), m.group(3))
    global_guard = (all(x in source for x in ('id="offline-katex-core"',
                    'id="offline-katex-css"', 'id="offline-katex-auto"',
                    'function commitResearchAttempt(', 'attempt.value.trim()',
                    'solution.hidden = false;', "solution.removeAttribute('inert')",
                    'function unlockResearchHint(', 'renderMathInElement(')))
    rows = []
    for qid, q in sorted(found.items()):
        if qid not in cards:
            rows.append({"id": qid, "tile": TILE, "verdict": "FAIL",
                         "html_anchor": "#q-" + qid, "source_cell": TILE,
                         "findings": [{"rule": "T00_HTML_CARD_MISSING",
                                       "element": "#q-" + qid,
                                       "detail": "Source question not found in generated HTML"}],
                         "holds": ["ACADEMIC_REVIEW_REQUIRED"]})
        else:
            attrs, body = cards[qid]
            rows.append(inspect_card(q, attrs, body, core_review=relationships.get(qid, {}),
                                     global_guard=global_guard))
    return {"schema": SCHEMA, "source_commit": source_commit, "scope": "RESEARCH_HTML_NOT_NATIVE_CORE",
            "tile": TILE, "template": {"decisive_act": model["decisive_act"],
                      "protected_work": model["band_policy"]["protected_work"],
                      "hint1": model["review"]["H1"]["question"],
                      "hint2": model["review"]["H2"]["question"],
                      "hint3": model["review"]["H3"]["question"],
                      "core_p2": model["review"]["P2"]["question"]},
            "html": {"path": ENDPOINTS[0], "sha256": htmls[0]["sha256"],
                     "endpoint_receipts": htmls, "rendered_total": len(cards),
                     "math_vendor_and_script_static_guard": global_guard},
            "source_count": len(found), "records": rows,
            "counts": dict(Counter(x["verdict"] for x in rows)),
            "finding_counts": dict(sorted(Counter(f["rule"] for row in rows
                                                 for f in row["findings"]).items())),
            "academic_approval": "NOT_GRANTED", "native_core_admission": "NOT_GRANTED",
            "browser_test": "NOT_RUN"}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    result = inspect_tile(root=args.root, source_commit=args.source_commit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tile": TILE, "source_commit": result["source_commit"],
                      "counts": result["counts"], "finding_counts": result["finding_counts"],
                      "html": result["html"]["path"], "academic": result["academic_approval"]}, indent=2))
    return 1 if result["counts"].get("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
