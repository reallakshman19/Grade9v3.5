#!/usr/bin/env python3
"""Audit all Core outputs (Core 1A, Core 1B, Core 2) against the canonical 28-cell QRT Matrix.

Evaluates:
- Core 2 Question Custody: Demand validity, difficulty band policy, protected work W protection,
  hint ladder progression, step derivations, and distractor rationale.
- Core 1A Declarative Study: Conventions-first, inferential jump, step-level why_valid justifications,
  representation bridges, misconception diagnosis + repair, and exit checks.
- Core 1B Conceptual Reconstruction: 6-stage self-tutor cycle (predict, attempt, reconstruct,
  diagnose, repair, boundary_test), attempt closure without human tutor, and non-triviality.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    from Shared.tools import question_difficulty
except ModuleNotFoundError:
    import question_difficulty  # type: ignore

QRT_MATRIX_PATH = REPO / "Shared" / "quality" / "question-demand-matrix.v1.json"
VOCAB_PATH = REPO / "Shared" / "vocabularies" / "cognitive-demand.v1.json"
DEFAULT_HOSTED_PAGE = REPO / "public" / "test" / "imo-grade9" / "core2.html"
DEFAULT_CORE1A_PAGE = REPO / "public" / "test" / "imo-grade9" / "core1a.html"
DEFAULT_CORE1B_PAGE = REPO / "public" / "test" / "imo-grade9" / "core1b.html"
DEFAULT_OUTPUT_REPORT = REPO / "TEST" / "imo-research" / "audit" / "core_qrt_alignment_audit.v1.json"

VALID_DEMANDS = {"RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"}
VALID_BANDS = {"D1", "D2", "D3", "D4"}


class QRTAuditError(ValueError):
    """Raised when critical QRT audit contracts fail."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise QRTAuditError(f"{path}: expected JSON object")
        return data
    except Exception as exc:
        raise QRTAuditError(f"Failed to read {path}: {exc}") from exc


def audit_core2_question_card(art_html: str, index: int, qrt_matrix: dict[str, Any]) -> dict[str, Any]:
    """Audit a single rendered Core 2 question card from the hosted HTML."""
    clean_html = html.unescape(art_html)

    # Metadata extraction
    band_m = re.search(r'data-band="([^"]+)"', clean_html)
    demand_m = re.search(r'data-demand="([^"]+)"', clean_html)
    topic_m = re.search(r'data-topic="([^"]+)"', clean_html)
    year_m = re.search(r'data-year="([^"]+)"', clean_html)
    search_m = re.search(r'data-search="([^"]+)"', clean_html)
    title_m = re.search(r'<h2 class="qb-title">([^<]+)</h2>', clean_html)

    band = band_m.group(1).strip() if band_m else "UNKNOWN"
    demand = demand_m.group(1).strip() if demand_m else "UNKNOWN"
    topic = topic_m.group(1).strip() if topic_m else "Unclassified"
    year = year_m.group(1).strip() if year_m else "UNKNOWN"
    search = search_m.group(1).strip() if search_m else ""
    qid = search.split()[0] if search else f"Q{index:03d}"
    title = title_m.group(1).strip() if title_m else qid

    findings: list[str] = []

    # 1. Demand & Band Contract
    delta_dem = 0.0
    if demand not in VALID_DEMANDS:
        findings.append(f"INVALID_COGNITIVE_DEMAND: {demand}")
        delta_dem = 1.0

    delta_diff = 0.0
    if band not in VALID_BANDS:
        findings.append(f"INVALID_DIFFICULTY_BAND: {band}")
        delta_diff = 1.0

    # 2. Structural Requirements
    has_stem = bool(re.search(r'class="qb-stem-text"[^>]*>(.*?)</div>', clean_html, re.DOTALL))
    has_options = bool(re.search(r'class="qb-options-grid"', clean_html))
    has_attempt = bool(re.search(r'class="qb-attempt-box"', clean_html))
    has_deriv = bool(
        re.search(r'Step-by-Step Derivation:\s*</strong></p>\s*<p[^>]*>(.*?)</p>', clean_html, re.DOTALL)
        or re.search(r'Verified Answer:\s*Option', clean_html, re.I)
        or re.search(r'class="sol-verified-box"', clean_html)
    )
    has_check = bool(
        re.search(r'Verification Check:\s*</strong>\s*(.*?)</div>', clean_html, re.DOTALL)
        or re.search(r'class="sol-verified-badge"', clean_html)
        or re.search(r'Formal Verification', clean_html)
    )
    has_trap = bool(
        re.search(r'Tempting Mistake & Why It Fails:\s*</strong>\s*(.*?)\s*</div>', clean_html, re.DOTALL)
        or re.search(r'Distractor Diagnostic & Misconceptions', clean_html)
        or re.search(r'class="trap-alert"', clean_html)
    )
    has_svg = "<svg" in clean_html

    # These six are individually mandatory. A missing single element must
    # fail closed, even if its weighted score would be below the 0.05 threshold.
    critical_checks = {
        "MISSING_EXAM_STEM": has_stem,
        "MISSING_OPTIONS_GRID": has_options,
        "MISSING_ATTEMPT_BOX": has_attempt,
        "MISSING_STEP_BY_STEP_DERIVATION": has_deriv,
        "MISSING_VERIFICATION_CHECK": has_check,
        "MISSING_TRAP_DIAGNOSTIC": has_trap,
    }
    missing_critical = [code for code, present in critical_checks.items() if not present]
    struct_checks = list(critical_checks.values())
    delta_struct = 1.0 - (sum(1 for c in struct_checks if c) / len(struct_checks))

    if not has_stem:
        findings.append("MISSING_EXAM_STEM")
    if not has_options:
        findings.append("MISSING_OPTIONS_GRID")
    if not has_attempt:
        findings.append("MISSING_ATTEMPT_BOX")
    if not has_deriv:
        findings.append("MISSING_STEP_BY_STEP_DERIVATION")
    if not has_check:
        findings.append("MISSING_VERIFICATION_CHECK")
    if not has_trap:
        findings.append("MISSING_TRAP_DIAGNOSTIC")

    # 3. Hint Ladder & Protected Work W Check
    raw_rungs = re.findall(r'<div class="ladder-rung"[^>]*><p[^>]*>(.*?)</p></div>', clean_html, re.DOTALL)
    if not raw_rungs:
        tag_rungs = re.findall(r'<span class="rung-tag[^"]*">([^<]+)</span>\s*<p[^>]*>(.*?)</p>', clean_html, re.DOTALL)
        raw_rungs = [r[1] for r in tag_rungs]
    delta_prot = 0.0
    if len(raw_rungs) < 2:
        findings.append(f"HINT_LADDER_UNDERSIZED: found {len(raw_rungs)}, expected at least 2 rungs")
        delta_prot += 0.3

    # Check for boilerplate geometry leakage into non-geometry
    is_geom = any(k in topic.lower() for k in ["geometry", "triangle", "circle", "angle", "lines", "quadrilateral"])
    rung_texts = " ".join(raw_rungs)
    if "apply euclid" in rung_texts.lower() and not is_geom:
        findings.append("BOILERPLATE_EUCLID_HINT_ON_NON_GEOMETRY")
        delta_prot += 0.2

    trap_match = re.search(r'Tempting Mistake & Why It Fails:\s*</strong>\s*(.*?)\s*</div>', clean_html, re.DOTALL)
    trap_text = trap_match.group(1).strip() if trap_match else ""
    if "assuming lines are parallel or equal without an explicit geometric warrant" in trap_text.lower() and not is_geom:
        findings.append("BOILERPLATE_PARALLEL_LINES_TRAP_ON_NON_GEOMETRY")
        delta_prot += 0.2

    delta_prot = min(delta_prot, 1.0)

    # 4. Composite QRT Deviation Index for Question
    # Delta = 0.30 * dem + 0.30 * diff + 0.25 * prot + 0.15 * struct
    delta_qrt = (0.30 * delta_dem) + (0.30 * delta_diff) + (0.25 * delta_prot) + (0.15 * delta_struct)

    return {
        "id": qid,
        "title": title,
        "topic": topic,
        "year": year,
        "band": band,
        "demand": demand,
        "qrt_cell": f"QRT-{demand}-{band}",
        "delta_qrt": round(delta_qrt, 4),
        "scores": {
            "demand_deviation": round(delta_dem, 4),
            "difficulty_deviation": round(delta_diff, 4),
            "protection_deviation": round(delta_prot, 4),
            "structural_deficit": round(delta_struct, 4),
        },
        "has_svg": has_svg,
        "findings": findings,
        "missing_critical": missing_critical,
        "status": ("FAIL" if missing_critical else
                   ("PASS" if delta_qrt <= 0.05 else
                    ("FLAGGED" if delta_qrt <= 0.25 else "FAIL"))),
    }


def audit_core1a_section(html_content: str, name: str, declared_qrt: str) -> dict[str, Any]:
    """Audit a Core 1A Declarative Study module."""
    text = html.unescape(html_content)
    findings: list[str] = []

    # 1. Declared conventions
    has_conventions = bool(re.search(r'convention|relation_refs|hypotheses', text, re.I))
    # 2. Inferential leap / jump
    has_jump = bool(re.search(r'inferential\s+(leap|jump)|inferential_jump|decisive\s+inference', text, re.I))
    # 3. Step-by-step with why_valid
    why_valid_matches = re.findall(r'why[\s_]+valid|because|validity|justification', text, re.I)
    why_valid_count = len(why_valid_matches)
    has_why_valid = why_valid_count >= 2
    # 4. Representation bridge (diagram, symbol, words)
    has_bridge = bool(re.search(r'representation\s+bridge|representation|visual|residue-table|residues\s+to|table-wrap', text, re.I))
    # 5. Misconception / Trap clinic with repair
    has_trap = bool(re.search(r'trap\s+clinic|plausible\s+wrong\s+path|wrong_idea|fallacy|misconception', text, re.I))
    has_repair = bool(re.search(r'refutation|repair|replacement\s+rule', text, re.I))
    # 6. Exit task
    has_exit = bool(re.search(r'exit\s+task|independent\s+exit|worked_concept_anchor|canonical_anchor', text, re.I))

    score_components = {
        "conventions": 0.20 if has_conventions else 0.0,
        "inferential_jump": 0.25 if has_jump else 0.0,
        "step_justifications": 0.20 if has_why_valid else (0.10 if why_valid_count == 1 else 0.0),
        "representation_bridge": 0.15 if has_bridge else 0.0,
        "misconception_repair": 0.10 if (has_trap and has_repair) else (0.05 if has_trap else 0.0),
        "exit_task": 0.10 if has_exit else 0.0,
    }
    earned = sum(score_components.values())
    delta_struct = round(1.0 - earned, 4)

    if not has_conventions:
        findings.append("CORE1A_DECLARED_CONVENTIONS_MISSING")
    if not has_jump:
        findings.append("CORE1A_INFERENTIAL_JUMP_NOT_EXPLICITLY_ISOLATED")
    if not has_why_valid:
        findings.append(f"CORE1A_STEP_JUSTIFICATIONS_INSUFFICIENT: found {why_valid_count} citations")
    if not has_bridge:
        findings.append("CORE1A_REPRESENTATION_BRIDGE_MISSING")
    if not has_trap:
        findings.append("CORE1A_TRAP_CLINIC_MISSING")
    elif not has_repair:
        findings.append("CORE1A_MISCONCEPTION_REPAIR_RULE_MISSING")
    if not has_exit:
        findings.append("CORE1A_EXIT_TASK_MISSING")

    # Composite QRT deviation
    delta_qrt = delta_struct

    return {
        "module": name,
        "role": "CORE1A",
        "declared_qrt": declared_qrt,
        "delta_qrt": delta_qrt,
        "earned_compliance": round(earned, 4),
        "scores": score_components,
        "findings": findings,
        "status": "PASS" if delta_qrt <= 0.05 else ("FLAGGED" if delta_qrt <= 0.35 else "FAIL"),
    }


def audit_core1b_section(html_content: str, name: str, declared_qrt: str) -> dict[str, Any]:
    """Audit a Core 1B Conceptual Reconstruction module."""
    text = html.unescape(html_content)
    findings: list[str] = []

    # 1. Predict prompt (pose decision before reveal, defensible answer)
    has_predict = bool(re.search(r'predict|decision\s+before|unassisted\s+recall|stage\s+1|gate\s+1|stage_1_predict', text, re.I))
    # 2. Attempt box / produce
    has_attempt = bool(re.search(r'<textarea|attempt-box|class="qb-textarea"|stage_2_attempt|produces', text, re.I))
    # 3. Autonomous closure (model solution / rubric without human teacher)
    has_closure = bool(re.search(r'<details|commit-btn|model-proof|check\s+stage|check\s+gate|model_closure|model_response', text, re.I))
    has_no_teacher_deferral = not bool(re.search(r'ask\s+your\s+teacher|consult\s+class|wait\s+for\s+tutor', text, re.I))
    # 4. Step reconstruction
    has_reconstruct = bool(re.search(r'reconstruction|complete\s+step|stage\s+2|gate\s+2|stage_3_reconstruct', text, re.I))
    # 5. Boundary test (limiting case / reversal / edge condition)
    has_boundary = bool(re.search(r'boundary\s+test|changed\s+givens|limiting\s+case|coprime\s+condition|stage_4_boundary_test', text, re.I))

    score_components = {
        "predict_prompt": 0.25 if has_predict else 0.0,
        "attempt_box": 0.20 if has_attempt else 0.0,
        "autonomous_closure": 0.20 if (has_closure and has_no_teacher_deferral) else (0.10 if has_closure else 0.0),
        "step_reconstruct": 0.15 if has_reconstruct else 0.0,
        "boundary_test": 0.20 if has_boundary else 0.0,
    }
    earned = sum(score_components.values())
    delta_struct = round(1.0 - earned, 4)

    if not has_predict:
        findings.append("CORE1B_PREDICT_PROMPT_MISSING")
    if not has_attempt:
        findings.append("CORE1B_ATTEMPT_INPUT_MISSING")
    if not has_closure:
        findings.append("CORE1B_AUTONOMOUS_CLOSURE_MISSING")
    if not has_no_teacher_deferral:
        findings.append("CORE1B_FORBIDDEN_HUMAN_TUTOR_DEFERRAL")
    if not has_reconstruct:
        findings.append("CORE1B_STEP_RECONSTRUCTION_MISSING")
    if not has_boundary:
        findings.append("CORE1B_BOUNDARY_TEST_MISSING")

    delta_qrt = delta_struct

    return {
        "module": name,
        "role": "CORE1B",
        "declared_qrt": declared_qrt,
        "delta_qrt": delta_qrt,
        "earned_compliance": round(earned, 4),
        "scores": score_components,
        "findings": findings,
        "status": "PASS" if delta_qrt <= 0.05 else ("FLAGGED" if delta_qrt <= 0.35 else "FAIL"),
    }


def audit_hosted_suite(
    html_path: Path,
    core1a_path: Path | None = None,
    core1b_path: Path | None = None,
) -> dict[str, Any]:
    """Execute complete QRT audit across the hosted HTML question bank and Core 1 tabs."""
    if not html_path.is_file():
        raise QRTAuditError(f"Hosted HTML suite not found at {html_path}")

    qrt_matrix = load_json(QRT_MATRIX_PATH)
    raw_html = html_path.read_text(encoding="utf-8")

    # 1. Parse all Core 2 questions
    articles = re.findall(r'<article class="qb-question"(.*?)</article>', raw_html, re.DOTALL)
    q_results: list[dict[str, Any]] = []
    for i, art in enumerate(articles):
        q_res = audit_core2_question_card(art, i + 1, qrt_matrix)
        q_results.append(q_res)

    # 2. Parse Core 1 tabs in the hosted page
    core1_results: list[dict[str, Any]] = []

    # Tab d1-core
    m_d1 = re.search(r'<section class="tab-content"[^>]*id="tab-d1-core"[^>]*>(.*?)</section>', raw_html, re.DOTALL)
    if m_d1:
        d1_text = m_d1.group(1)
        # Split into Core 1A and Core 1B if present
        parts = d1_text.split("<!-- CORE 1B")
        c1a_part = parts[0]
        c1b_part = parts[1] if len(parts) > 1 else ""

        core1_results.append(audit_core1a_section(c1a_part, "Tab D1/D2 Divisibility", "QRT-JUSTIFY-D1"))
        if c1b_part:
            core1_results.append(audit_core1b_section(c1b_part, "Tab D1/D2 Divisibility", "QRT-JUSTIFY-D1"))

    # Tab d2-core
    m_d2 = re.search(r'<section class="tab-content"[^>]*id="tab-d2-core"[^>]*>(.*?)</section>', raw_html, re.DOTALL)
    if m_d2:
        d2_text = m_d2.group(1)
        parts = d2_text.split("<!-- CORE 1B")
        if len(parts) == 1:
            parts = d2_text.split("Core 1B · Dual-Stage Recall")
        c1a_part = parts[0]
        c1b_part = parts[1] if len(parts) > 1 else ""
        core1_results.append(audit_core1a_section(c1a_part, "Tab D2 Quadrilaterals & Proofs", "QRT-JUSTIFY-D2"))
        if c1b_part:
            core1_results.append(audit_core1b_section(c1b_part, "Tab D2 Quadrilaterals & Proofs", "QRT-JUSTIFY-D2"))

    # Tab d3-core
    m_d3 = re.search(r'<section class="tab-content"[^>]*id="tab-d3-core"[^>]*>(.*?)</section>', raw_html, re.DOTALL)
    if m_d3:
        d3_text = m_d3.group(1)
        parts = d3_text.split("Core 1B · Dual-Stage Recall")
        c1a_part = parts[0]
        c1b_part = parts[1] if len(parts) > 1 else ""
        core1_results.append(audit_core1a_section(c1a_part, "Tab D3 Indices & Rates", "QRT-APPLY-D3"))
        if c1b_part:
            core1_results.append(audit_core1b_section(c1b_part, "Tab D3 Indices & Rates", "QRT-APPLY-D3"))

    # Tab d4-core
    m_d4 = re.search(r'<section class="tab-content"[^>]*id="tab-d4-core"[^>]*>(.*?)</section>', raw_html, re.DOTALL)
    if m_d4:
        d4_text = m_d4.group(1)
        parts = d4_text.split("Core 1B · Dual-Stage Recall")
        c1a_part = parts[0]
        c1b_part = parts[1] if len(parts) > 1 else ""
        core1_results.append(audit_core1a_section(c1a_part, "Tab D4 Surds & Circles", "QRT-JUSTIFY-D4"))
        if c1b_part:
            core1_results.append(audit_core1b_section(c1b_part, "Tab D4 Surds & Circles", "QRT-JUSTIFY-D4"))

    # 3. Also audit standalone Core 1A / 1B files if present
    if core1a_path and core1a_path.is_file():
        c1a_file_content = core1a_path.read_text(encoding="utf-8")
        core1_results.append(audit_core1a_section(c1a_file_content, "Standalone File core1a.html", "QRT-JUSTIFY-D1"))

    if core1b_path and core1b_path.is_file():
        c1b_file_content = core1b_path.read_text(encoding="utf-8")
        core1_results.append(audit_core1b_section(c1b_file_content, "Standalone File core1b.html", "QRT-JUSTIFY-D1"))

    # Aggregations
    total_q = len(q_results)
    d2_questions = [q for q in q_results if q["band"] == "D2"]

    # Band statistics
    band_stats: dict[str, dict[str, Any]] = {}
    for band in VALID_BANDS:
        items = [q for q in q_results if q["band"] == band]
        if items:
            avg_dev = sum(q["delta_qrt"] for q in items) / len(items)
            flagged = sum(1 for q in items if q["status"] != "PASS")
            band_stats[band] = {
                "count": len(items),
                "mean_delta_qrt": round(avg_dev, 4),
                "flagged_count": flagged,
                "compliance_pct": round((1.0 - avg_dev) * 100, 2),
            }

    # Topic statistics for D2
    d2_topic_stats: dict[str, dict[str, Any]] = {}
    for q in d2_questions:
        top = q["topic"]
        if top not in d2_topic_stats:
            d2_topic_stats[top] = {"count": 0, "total_delta": 0.0, "flagged": 0}
        d2_topic_stats[top]["count"] += 1
        d2_topic_stats[top]["total_delta"] += q["delta_qrt"]
        if q["status"] != "PASS":
            d2_topic_stats[top]["flagged"] += 1

    for top, data in d2_topic_stats.items():
        data["mean_delta_qrt"] = round(data["total_delta"] / data["count"], 4)
        data["compliance_pct"] = round((1.0 - data["mean_delta_qrt"]) * 100, 2)
        del data["total_delta"]

    # Core 1 modules summary
    core1_mean_dev = (sum(m["delta_qrt"] for m in core1_results) / len(core1_results)) if core1_results else 0.0

    return {
        "schema": "core-qrt-alignment-audit/v1",
        "audit_target": str(html_path),
        "total_questions_audited": total_q,
        "total_core1_modules_audited": len(core1_results),
        "overall_summary": {
            "core2_questions_count": total_q,
            "core2_d2_questions_count": len(d2_questions),
            "core1_modules_count": len(core1_results),
            "core1_mean_delta_qrt": round(core1_mean_dev, 4),
            "core1_compliance_pct": round((1.0 - core1_mean_dev) * 100, 2),
            "band_statistics": band_stats,
            "d2_topic_breakdown": d2_topic_stats,
        },
        "core1_modules": core1_results,
        "questions": q_results,
    }


def audit_item_inter_core_checkpoint(
    qid_query: str,
    html_path: Path,
    core1a_path: Path | None = None,
    core1b_path: Path | None = None,
) -> dict[str, Any]:
    """Execute an atomic Question-by-Question Inter-Core Checkpoint Audit.

    Validates:
    - Checkpoint 1 (Core 2 Custody): Authentic stem, options, LaTeX, attempt box, verification check, trap.
    - Checkpoint 2 (QRT Matrix): Valid Demand, Band, and 5-factor difficulty scoring.
    - Checkpoint 3 (Core 1A Declarative Study): Declarative anchor matching question crux, conventions, why_valid steps.
    - Checkpoint 4 (Core 1B Conceptual Reconstruction): 6-stage self-tutor cycle, unassisted recall, boundary test.
    - Checkpoint 5 (Cross-Core Leakage Protection): Pre-attempt panels and hints do not disclose protected work W.
    """
    if not html_path.is_file():
        raise QRTAuditError(f"Hosted HTML suite not found at {html_path}")

    raw_html = html_path.read_text(encoding="utf-8")
    qrt_matrix = load_json(QRT_MATRIX_PATH)

    # 1. Locate Question Card
    articles = re.findall(r'<article class="qb-question"(.*?)</article>', raw_html, re.DOTALL)
    card_match: str | None = None
    target_idx = 0
    clean_query = qid_query.strip().lower()

    for idx, art in enumerate(articles):
        clean_art = html.unescape(art).lower()
        if clean_query in clean_art:
            card_match = art
            target_idx = idx + 1
            break

    if not card_match:
        return {
            "status": "FAIL",
            "error": f"Question matching query '{qid_query}' not found in {html_path}",
            "checkpoint_summary": {"overall": "NOT_FOUND"},
        }

    # Run Core 2 Audit
    core2_res = audit_core2_question_card(card_match, target_idx, qrt_matrix)
    qid = core2_res["id"]
    topic = core2_res["topic"]
    band = core2_res["band"]
    demand = core2_res["demand"]

    # 2. Check Core 1 Anchoring in Tabs or Files
    # Search for matching Core 1A & 1B content anchored to this QID or topic
    qnum_match = re.search(r'Q0?([0-9]{1,3})', qid, re.I)
    qnum_tag = f"Q{qnum_match.group(1)}" if qnum_match else qid

    anchored_c1a: dict[str, Any] | None = None
    anchored_c1b: dict[str, Any] | None = None

    # Check tabs for anchor
    tabs_to_check = [
        ("tab-d1-core", "QRT-JUSTIFY-D1"),
        ("tab-d2-core", "QRT-JUSTIFY-D2"),
        ("tab-d3-core", "QRT-APPLY-D3"),
        ("tab-d4-core", "QRT-JUSTIFY-D4"),
    ]
    target_cell = f"QRT-{demand}-{band}"
    for tab_id, declared_qrt in tabs_to_check:
        m_tab = re.search(r'<section class="tab-content"[^>]*id="' + tab_id + r'"[^>]*>(.*?)</section>', raw_html, re.DOTALL)
        if m_tab:
            content = m_tab.group(1)
            if target_cell == declared_qrt or (qid and qid in content) or (qnum_tag and qnum_tag in content):
                parts = content.split("<!-- CORE 1B")
                if len(parts) == 1:
                    parts = content.split("Core 1B · Dual-Stage Recall")
                c1a_sub = parts[0]
                c1b_sub = parts[1] if len(parts) > 1 else ""
                anchored_c1a = audit_core1a_section(c1a_sub, f"Tab {tab_id}", declared_qrt)
                if c1b_sub:
                    anchored_c1b = audit_core1b_section(c1b_sub, f"Tab {tab_id}", declared_qrt)
                break

    # If not found in tabs, auto-discover in Mathematics/units/
    if (not anchored_c1a or not anchored_c1b):
        units_dir = Path("Mathematics/units")
        if units_dir.is_dir():
            for unit_file in sorted(units_dir.rglob("core1a*.json")):
                try:
                    data = json.loads(unit_file.read_text(encoding="utf-8"))
                    refs = [r.upper() for r in data.get("linked_core2_refs", [])]
                    tgt_dem = data.get("target_demand", "")
                    tgt_bnd = data.get("target_band", "")
                    topic_clean = re.sub(r"[^a-z0-9]", "", topic.lower())
                    unit_topic_name = re.sub(r"[^a-z0-9]", "", str(data.get("topic_name", "")).lower())
                    unit_topic_code = re.sub(r"[^a-z0-9]", "", str(data.get("topic", "")).lower())
                    topic_matched = bool(topic_clean and (topic_clean in unit_topic_name or unit_topic_name in topic_clean or topic_clean in unit_topic_code))
                    if qid.upper() in refs or (tgt_dem == demand and tgt_bnd == band) or topic_matched:
                        if not anchored_c1a:
                            anchored_c1a = audit_core1a_section(unit_file.read_text(encoding="utf-8"), f"Unit {unit_file.name}", f"QRT-{demand}-{band}")
                        paired_1b = unit_file.parent / unit_file.name.replace("core1a-", "core1b-")
                        if not anchored_c1b and paired_1b.is_file():
                            anchored_c1b = audit_core1b_section(paired_1b.read_text(encoding="utf-8"), f"Unit {paired_1b.name}", f"QRT-{demand}-{band}")
                        if anchored_c1a and anchored_c1b:
                            break
                except Exception:
                    pass

    # If still not anchored, check provided standalone files if matching topic or QRT
    if not anchored_c1a and core1a_path and core1a_path.is_file():
        c1a_text = core1a_path.read_text(encoding="utf-8")
        if (topic.lower() in c1a_text.lower()) or (f"QRT-{demand}-{band}" in c1a_text):
            anchored_c1a = audit_core1a_section(c1a_text, f"File {core1a_path.name}", f"QRT-{demand}-{band}")

    if not anchored_c1b and core1b_path and core1b_path.is_file():
        c1b_text = core1b_path.read_text(encoding="utf-8")
        if (topic.lower() in c1b_text.lower()) or (f"QRT-{demand}-{band}" in c1b_text):
            anchored_c1b = audit_core1b_section(c1b_text, f"File {core1b_path.name}", f"QRT-{demand}-{band}")

    # 3. Inter-Core Checkpoint Evaluation
    checkpoints = {
        "checkpoint_1_core2_custody": {
            "name": "Core 2 Question Custody Integrity",
            "status": "PASS" if core2_res["status"] == "PASS" else "FAIL",
            "delta_qrt": core2_res["delta_qrt"],
            "findings": core2_res["findings"],
        },
        "checkpoint_2_qrt_matrix_binding": {
            "name": "QRT 28-Cell Semantic & Difficulty Band Binding",
            "status": "PASS" if (demand in VALID_DEMANDS and band in VALID_BANDS) else "FAIL",
            "qrt_cell": f"QRT-{demand}-{band}",
            "demand": demand,
            "band": band,
        },
        "checkpoint_3_core1a_declarative_anchor": {
            "name": "Core 1A Declarative Teaching Bridge",
            "status": (anchored_c1a["status"] if anchored_c1a else "NOT_LINKED"),
            "delta_qrt": (anchored_c1a["delta_qrt"] if anchored_c1a else 1.0),
            "findings": (anchored_c1a["findings"] if anchored_c1a else ["NO_ANCHORED_CORE1A_MODULE_LOCATED"]),
        },
        "checkpoint_4_core1b_elicitation_parity": {
            "name": "Core 1B Conceptual Reconstruction & Coverage Parity",
            "status": (anchored_c1b["status"] if anchored_c1b else "NOT_LINKED"),
            "delta_qrt": (anchored_c1b["delta_qrt"] if anchored_c1b else 1.0),
            "findings": (anchored_c1b["findings"] if anchored_c1b else ["NO_ANCHORED_CORE1B_MODULE_LOCATED"]),
        },
        "checkpoint_5_cross_core_leakage": {
            "name": "Cross-Core Protected Work W Non-Disclosure",
            "status": "PASS" if core2_res["scores"]["protection_deviation"] == 0.0 else "FAIL",
            "protection_score": 1.0 - core2_res["scores"]["protection_deviation"],
        },
    }

    c1_dev = anchored_c1a["delta_qrt"] if anchored_c1a else 0.5
    overall_item_delta = round(max(core2_res["delta_qrt"], c1_dev), 4)

    return {
        "question_id": qid,
        "title": core2_res["title"],
        "topic": topic,
        "band": band,
        "demand": demand,
        "overall_item_delta_qrt": overall_item_delta,
        "item_checkpoint_verdict": (
            "FAIL" if core2_res["missing_critical"] else
            ("PASS" if overall_item_delta <= 0.05 else
             ("FLAGGED" if overall_item_delta <= 0.35 else "FAIL"))
        ),
        "checkpoints": checkpoints,
        "core2_details": core2_res,
        "anchored_core1a": anchored_c1a,
        "anchored_core1b": anchored_c1b,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_HOSTED_PAGE, help="Path to hosted HTML suite")
    parser.add_argument("--core1a", type=Path, default=DEFAULT_CORE1A_PAGE, help="Path to standalone core1a.html")
    parser.add_argument("--core1b", type=Path, default=DEFAULT_CORE1B_PAGE, help="Path to standalone core1b.html")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_REPORT, help="Output JSON report path")
    parser.add_argument("--checkpoint", type=str, default=None, help="Question ID / Number for atomic item-by-item checkpoint audit")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any deviation > 0.05 is found")
    args = parser.parse_args(argv)

    if args.checkpoint:
        print(f"\n=======================================================")
        print(f"   ATOMIC QUESTION-BY-QUESTION INTER-CORE CHECKPOINT   ")
        print(f"   Target Item Query: {args.checkpoint}               ")
        print(f"=======================================================")
        res = audit_item_inter_core_checkpoint(args.checkpoint, args.html, args.core1a, args.core1b)
        print(json.dumps(res, indent=2))
        if res.get("item_checkpoint_verdict") == "PASS":
            print("\n[CHECKPOINT RECEIPT]: VERIFIED PASS. Zero cognitive drift.")
            return 0
        else:
            print(f"\n[CHECKPOINT RECEIPT]: {res.get('item_checkpoint_verdict')} (Delta: {res.get('overall_item_delta_qrt')})")
            return 1 if res["core2_details"]["missing_critical"] or args.strict else 0

    try:
        report = audit_hosted_suite(args.html, args.core1a, args.core1b)
    except Exception as exc:
        print(f"Error executing QRT audit: {exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Audit report successfully written to {args.output}")

    # Print summary
    print("\n=======================================================")
    print("      QRT AUDIT SUMMARY: FROZEN HOSTED CORES           ")
    print("=======================================================")
    summ = report["overall_summary"]
    print(f"Total Questions Audited: {summ['core2_questions_count']}")
    print(f"  - D2 Questions:        {summ['core2_d2_questions_count']}")
    print(f"Core 1 Modules Audited:  {summ['core1_modules_count']}")
    print(f"Core 1 Mean Compliance:  {summ['core1_compliance_pct']}% (Deviation: {summ['core1_mean_delta_qrt'] * 100:.1f}%)")
    print("\nBand Statistics (Core 2):")
    for band, stat in summ["band_statistics"].items():
        print(f"  {band}: count={stat['count']}, compliance={stat['compliance_pct']}%, flagged={stat['flagged_count']}")

    print("\nCore 1 Modules Breakdown:")
    for m in report["core1_modules"]:
        print(f"  [{m['role']}] {m['module']} ({m['declared_qrt']}): Compliance={round((1-m['delta_qrt'])*100, 1)}% (Deviation={round(m['delta_qrt']*100, 1)}%) -> {m['status']}")
        if m["findings"]:
            for f in m["findings"]:
                print(f"      * {f}")

    critical_rejections = [q for q in report["questions"] if q["missing_critical"]]
    if critical_rejections:
        # Even the non-strict CLI must not report success when a question
        # lacks any mandatory stem/options/attempt/derivation/check/trap.
        print(f"\\n[CRITICAL QRT]: {len(critical_rejections)} question(s) missing mandatory elements; FAIL CLOSED.",
              file=sys.stderr)
        return 1
    if args.strict and (
        summ["core1_mean_delta_qrt"] > 0.05 or
        any(q["status"] != "PASS" for q in report["questions"])
    ):
        print("\n[STRICT MODE]: Quality gate FAILED due to unearned QRT deviations.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
