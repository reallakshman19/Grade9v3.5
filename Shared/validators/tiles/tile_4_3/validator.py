#!/usr/bin/env python3
"""Tile (4, 3): QRT-APPLY-D4 Smart Validator.

Enforces Blueprint Contract rules T01 through T14:
- Pre-commit protected work W preservation (no option styling leaks, no summary leaks, locked solution)
- 5-Factor difficulty scoring bounds: Band D4 score in [9, 10]
- 5-Core semantic linkage: Core 2 custody, Core 1A anti-leak, Core 1B gated reconstruction, Core 2A navigation
- Progressive hints: H1 foundation nudge -> H2 tactical master formulation step
"""
from __future__ import annotations

import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TILE_ID = "tile_4_3"
QRT_CELL = "QRT-APPLY-D4"
BAND = "D4"
DEMAND = "APPLY"
SCORE_MIN = 9
SCORE_MAX = 10

OPTION_LEAK_PATTERN = re.compile(r'(?:--success|correct_style|data-correct|data-answer|\bis_correct\b)', re.I)
SUMMARY_ANSWER_PATTERN = re.compile(r'\b(?:answer|choice|correct\s+option)\s*[:=\-]\s*\(?([A-D])\)?', re.I)
KATEX_ERROR_PATTERN = re.compile(r'class="katex-error"|\\(?:text|mathrm)\{[^}]*%[^\\]', re.I)


class CardHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.text_by_id: dict[str, str] = {}
        self.stack: list[tuple[str, str | None]] = []
        self.fragments: dict[str, list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        self.elements.append((tag, a))
        ident = a.get("id")
        if tag in {"br", "hr", "img", "input", "meta", "link", "source", "wbr"}:
            return
        self.stack.append((tag, ident))
        if ident:
            self.fragments.setdefault(ident, [])
        for _, parent_id in self.stack:
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

    def get_element_by_id(self, ident: str) -> tuple[str, dict[str, str | None]] | None:
        return next(((tag, attrs) for tag, attrs in self.elements if attrs.get("id") == ident), None)

    def get_text_by_id(self, ident: str) -> str:
        return html.unescape(" ".join(self.fragments.get(ident, []))).strip()


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", html.unescape(text)).casefold()
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\\(?:left|right|mathrm|text)\b", "", text)
    return re.sub(r"[\s$\{\}\\]", "", text)


def is_answer_leaked_in_text(hint_text: str, answer_val: str, answer_choice: str = "") -> bool:
    if not hint_text:
        return False
    norm_hint = normalize_text(hint_text)
    norm_val = normalize_text(answer_val)

    if norm_val and len(norm_val) > 4:
        if norm_val in norm_hint:
            return True
        if len(norm_hint) >= 20 and norm_hint in norm_val:
            return True
        if len(norm_val) >= 20:
            step = 8
            for i in range(0, len(norm_val) - 19, step):
                window = norm_val[i:i+20]
                if window in norm_hint:
                    return True

    if norm_val and len(norm_val) <= 4:
        val_regex = re.compile(r'(?:answer|result|value|equals|=|isalways)\s*[:=]?\s*' + re.escape(norm_val) + r'(?![0-9])', re.I)
        boundary_regex = re.compile(r'\b' + re.escape(norm_val) + r'\b', re.I)
        if val_regex.search(norm_hint) or boundary_regex.search(hint_text):
            return True

    if answer_choice and re.search(rf"\b(?:option|choice|answer)\s*[:=\-]?\s*{re.escape(answer_choice)}\b", hint_text, re.I):
        return True

    return False


def validate_card(
    question: dict[str, Any],
    html_snippet: str,
    core_context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate a single question card against Blueprint Contract rules T01 to T14."""
    qid = question.get("id", "UNKNOWN")
    findings: list[dict[str, str]] = []
    holds: list[str] = []

    def fail(rule: str, element: str, detail: str) -> None:
        findings.append({"rule": rule, "element": element, "detail": detail})

    # T14: Source Custody Integrity
    if not qid or qid == "UNKNOWN":
        fail("T14_SOURCE_CUSTODY_INTEGRITY", "question.id", "Missing question identifier")

    # T04: Difficulty Score Bounds [9, 10] for Band D4
    cog = question.get("cognitive_classification", {})
    score = cog.get("difficulty_score")
    band = cog.get("difficulty_band")
    if not isinstance(score, int) or isinstance(score, bool) or score < SCORE_MIN or score > SCORE_MAX:
        fail("T04_SCORE_OUT_OF_BOUNDS", "cognitive_classification.difficulty_score",
             f"Score {score} out of bounds [{SCORE_MIN}, {SCORE_MAX}] for Band {BAND}")

    if band != BAND:
        fail("T04_SCORE_OUT_OF_BOUNDS", "cognitive_classification.difficulty_band",
             f"Band '{band}' does not match tile band '{BAND}'")

    components = cog.get("difficulty_components", {})
    if isinstance(components, dict) and components:
        comp_sum = sum(components.values())
        if comp_sum != score:
            fail("T04_SCORE_OUT_OF_BOUNDS", "cognitive_classification.difficulty_components",
                 f"Component sum {comp_sum} does not match total score {score}")

    # T05: Crux Move Signature
    crux = cog.get("crux_move") or question.get("answer", {}).get("crux_move_ref")
    if not crux or not str(crux).strip():
        fail("T05_CRUX_MOVE_REF_MISSING", "cognitive_classification.crux_move",
             "Question must declare a non-empty crux_move reference")

    # Parse HTML representation
    parser = CardHTMLParser()
    try:
        parser.feed(html_snippet)
    except Exception as e:
        fail("T06_KATEX_RENDER_DEFECT", "html_snippet", f"HTML parsing error: {e}")

    # T06: KaTeX render defects
    if KATEX_ERROR_PATTERN.search(html_snippet):
        fail("T06_KATEX_RENDER_DEFECT", "span.katex-error", "KaTeX rendering defect or unescaped % symbol found")

    # T01: Pre-commit Option Styling Disclosure
    for tag, attrs in parser.elements:
        if tag in {"button", "div", "input", "span"} and ("opt-" in str(attrs.get("id", "")) or "qb-option" in str(attrs.get("class", ""))):
            cls_str = str(attrs.get("class", ""))
            attr_keys = " ".join(attrs.keys())
            if OPTION_LEAK_PATTERN.search(cls_str) or OPTION_LEAK_PATTERN.search(attr_keys):
                fail("T01_PRECOMMIT_OPTION_STYLING", f"#{attrs.get('id', 'option')}",
                     "Pre-commit option styling discloses the keyed answer via classes/attributes")

    # T02: Summary Answer Leak
    summary_matches = re.findall(r'<summary[^>]*>(.*?)</summary>', html_snippet, re.IGNORECASE | re.DOTALL)
    for sum_text in summary_matches:
        if SUMMARY_ANSWER_PATTERN.search(sum_text):
            fail("T02_SUMMARY_ANSWER_LEAK", "summary",
                 "Pre-commit summary discloses the answer letter/key")

    # T03: Solution Pre-commit Unlocked
    sol_matches = re.finditer(r'<details\s+([^>]*)class="[^"]*qb-solution[^"]*"([^>]*)>', html_snippet, re.IGNORECASE)
    for m in sol_matches:
        combined_attrs = m.group(1) + " " + m.group(2)
        if "inert" not in combined_attrs or "hidden" not in combined_attrs:
            fail("T03_SOLUTION_PRECOMMIT_UNLOCKED", "details.qb-solution",
                 "Pre-commit solution container must carry inert and hidden attributes")

    # T10 & T11: Hint ladder evaluation
    hints = question.get("hint_ladder", {})
    h1 = hints.get("hint1_conceptual_nudge", "")
    h2 = hints.get("hint2_tactical_step", "")
    ans_val = str(question.get("answer", {}).get("value", ""))
    ans_choice = str(question.get("answer", {}).get("choice", ""))

    if not h1.strip():
        fail("T10_EMPTY_HINT", "hint_ladder.hint1_conceptual_nudge", "Hint 1 conceptual nudge must not be empty")
    elif is_answer_leaked_in_text(h1, ans_val, ans_choice):
        fail("T11_PRECOMMIT_PROTECTED_W_LEAK", "hint_ladder.hint1",
             "Hint 1 discloses the final model answer W")

    if not h2.strip():
        fail("T10_EMPTY_HINT", "hint_ladder.hint2_tactical_step", "Hint 2 tactical step must not be empty")
    elif is_answer_leaked_in_text(h2, ans_val, ans_choice):
        fail("T11_PRECOMMIT_PROTECTED_W_LEAK", "hint_ladder.hint2",
             "Hint 2 discloses the final model answer W")

    # T13: Progressive Hint Sequence Presence in HTML
    h1_elem = parser.get_element_by_id(f"hint1-{qid}")
    h2_elem = parser.get_element_by_id(f"hint2-{qid}")
    if not h1_elem or not h2_elem:
        fail("T13_HINT_PROGRESSIVE_SEQUENCE_MISSING", ".qb-support-container",
             f"HTML missing progressive hint elements (#hint1-{qid} and #hint2-{qid})")

    # T09 / T12: Core Unit Navigation Binding
    unit_targets = set(re.findall(r'data-core-unit-id="([^"]+)"', html_snippet))
    expected_unit = question.get("core_links", {}).get("core1a_unit_id")
    if not unit_targets:
        fail("T12_CORE_P2_TOPIC_ONLY_NO_QUESTION_UNIT", "[data-core-unit-id]",
             "HTML must declare a question-specific Core1 unit navigation target")
    elif expected_unit and expected_unit not in unit_targets:
        fail("T12_CORE_P2_TOPIC_ONLY_NO_QUESTION_UNIT", "[data-core-unit-id]",
             f"HTML target {unit_targets} does not match expected unit '{expected_unit}'")

    # T07: Core 1A Anti-Leak Check
    if core_context and "core1a" in core_context:
        c1a_text = json.dumps(core_context["core1a"], ensure_ascii=False)
        if is_answer_leaked_in_text(c1a_text, ans_val, ans_choice):
            fail("T07_CORE1A_PARAMETER_LEAK", "core_context.core1a",
                 "Core 1A declarative study text leaks the exact question parameter/answer")

    # T08: Core 1B Elicitation Check
    if core_context and "core1b" in core_context:
        c1b = core_context["core1b"]
        if c1b.get("answer_before_attempt") != "FORBIDDEN":
            fail("T08_CORE1B_PRECOMMIT_ANSWER_LEAK", "core_context.core1b.answer_before_attempt",
                 "Core 1B must enforce answer_before_attempt: 'FORBIDDEN'")

    # Qualitative holds
    holds.append("QRT_APPLY_D4_DECISIVE_ACT_REVIEW_REQUIRED")
    holds.append("AUTHORED_FACTORS_ACADEMIC_HOLD")

    verdict = "FAIL" if findings else "PASS"

    return {
        "id": qid,
        "tile": TILE_ID,
        "qrt_cell": QRT_CELL,
        "verdict": verdict,
        "findings": findings,
        "holds": holds
    }


def audit_tile(root_path: Path | None = None, source_commit: str | None = None) -> dict[str, Any]:
    """Scan and audit questions mapped to QRT-APPLY-D4 across golden fixtures."""
    fixtures = ["golden_fixture.json", "golden_fixture_2.json", "golden_fixture_3.json"]
    records = []
    statuses = []

    for fix_name in fixtures:
        p = Path(__file__).parent / fix_name
        if p.is_file():
            golden = json.loads(p.read_text(encoding="utf-8"))
            res = validate_card(
                golden["source_question"],
                golden["html_representation"],
                golden.get("core_context")
            )
            records.append(res)
            statuses.append(res["verdict"])

    overall_status = "PASS" if records and all(s == "PASS" for s in statuses) else "FAIL"

    return {
        "schema": "imo-qrt-tile-audit/v1",
        "tile_id": TILE_ID,
        "qrt_cell": QRT_CELL,
        "source_commit": source_commit or "LOCAL_UNCOMMITTED",
        "golden_status": overall_status,
        "fixture_count": len(records),
        "records": records,
        "academic_approval": "REVIEW_REQUIRED"
    }


if __name__ == "__main__":
    result = audit_tile()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["golden_status"] == "PASS" else 1)
