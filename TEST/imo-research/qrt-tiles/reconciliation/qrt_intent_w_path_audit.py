#!/usr/bin/env python3
"""#182 R8 P2/P3: live native preattempt cross-Core W exposure, with bad mutations.

Five Core learner surfaces are observed in real Chromium against only files made
by Shared/tools/render_core.py. This cannot prove cognitive independence or all
possible paraphrases; confirmed cue/leaks remain HOLD, other paths REVIEW_REQUIRED.
No generic academic judgement, source rewrite, golden mutation or Owner acceptance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

from qrt_intent_contract import BP, ContractError, ROLES, ensure, read_json, sha256

PATHS = {
    "DIRECT_CORE2A": ("CORE2A",),
    "CORE1_TO_CORE1A_TO_CORE2A": ("CORE1", "CORE1A", "CORE2A"),
    "CORE1_REPAIR_CORE1B_CORE2A": ("CORE1", "CORE1A", "CORE1B", "CORE2A"),
    "CORE2A_TO_CORE1A_ASSISTED_RETURN": ("CORE2A", "CORE1A", "CORE2A"),
    "CORE2A_TO_CORE2B_TRANSFER": ("CORE2A", "CORE2B"),
}
MODEL_EQ = re.compile(
    r"(?:4\s*\(\s*9\s*[-−]\s*x\s*\)\s*\+\s*7\s*x|"
    r"7\s*x\s*\+\s*4\s*\(\s*9\s*[-−]\s*x\s*\)|"
    r"4\s*x\s*\+\s*7\s*\(\s*9\s*[-−]\s*x\s*\))\s*=\s*48", re.I
)
D4_IFF = re.compile(r"(?:iff|if\s+and\s+only\s+if|necessary\s+and\s+sufficient)", re.I)
D4_DOMAIN = re.compile(r"(?:k\s*(?:>=|≥|\\ge)\s*3|powers?\s+of\s+two.*(?:at\s+least|from)\s*8)", re.I)
D4_CLASS = re.compile(r"(?:1\s*(?:mod|modulo)\s*8|1\s*\\pmod\{8\}|[≡=]\s*1.*(?:mod|modulo)\s*8)", re.I)


class RootAssets(SimpleHTTPRequestHandler):
    def __init__(self, *args, source_root: Path, **kwargs):
        self.source_root = source_root.resolve()
        super().__init__(*args, directory=str(source_root), **kwargs)

    def translate_path(self, path):
        uri = unquote(urlsplit(path).path)
        for prefix in ("css", "js", "images", "img", "fonts", "assets"):
            marker = "/build/" + prefix + "/"
            if uri.startswith(marker):
                candidate = (self.source_root / "public" /
                             uri[len("/build/"):]).resolve()
                if candidate.is_relative_to((self.source_root / "public").resolve()):
                    return str(candidate)
        return super().translate_path(path)

    def log_message(self, *args):
        pass


def only_preattempt_text(state: dict) -> str:
    return "\n".join(str(state.get(k, "")) for k in (
        "visible", "h2_visible", "accessible_svg", "semantic_labels", "stem"
    ))


def known_exposure(cell: str, role: str, state: dict) -> list[str]:
    """Narrow known-bad semantic oracles; absence NEVER means QRT accepted."""
    text = only_preattempt_text(state)
    compact = re.sub(r"\s+", " ", text)
    hits = []
    if cell == "QRT-MODEL-D2" and MODEL_EQ.search(text):
        hits.append("MODEL_D2_TARGET_WEIGHTED_EQUATION_DISCLOSED")
    if cell == "QRT-EXPLAIN-D3":
        # The target candidate plus the full sign-based exclusion in one
        # accessible/visible precommit surface; generic sign concept is allowed.
        chunks = (state.get("accessible_svg", "").split("\n") +
                  state.get("semantic_labels", "").split("\n") +
                  state.get("visible", "").split("\n"))
        for chunk in chunks:
            low = chunk.casefold().replace("−", "-")
            if (re.search(r"(?:x\s*=\s*-1|-1\s+candidate)", low) and
                ("reject" in low or "extraneous" in low) and
                ("negative" in low or "nonnegative" in low or "sign" in low) and
                ("sqrt" in low or "square root" in low)):
                hits.append("EXPLAIN_D3_TARGET_SIGN_VERDICT_DISCLOSED")
                break
    if cell == "QRT-RETRIEVE-D4":
        # Conjunction ensures a modulo8 necessity anchor alone is not flagged.
        for chunk in (state.get("visible", "").split("\n") +
                      state.get("accessible_svg", "").split("\n") +
                      state.get("semantic_labels", "").split("\n")):
            if (D4_IFF.search(chunk) and D4_DOMAIN.search(chunk) and
                D4_CLASS.search(chunk)):
                hits.append("RETRIEVE_D4_FULL_THRESHOLD_IFF_PREATTEMPT")
                break
    if cell == "QRT-RETRIEVE-D2" and role == "CORE2A":
        stem = state.get("stem", "")
        if re.search(r"\bretrieve\b.{0,50}\bright.triangle distance relation\b",
                     stem, re.I):
            hits.append("RETRIEVE_D2_METHOD_SELECTION_ALREADY_CUED")
    return list(dict.fromkeys(hits))


def transfer_novelty(cell: str, primary_stem: str,
                     transfer_stem: str) -> dict:
    """Source-specific discriminators do not purport to prove independent skill."""
    p = re.sub(r"\s+", " ", primary_stem).casefold().strip()
    t = re.sub(r"\s+", " ", transfer_stem).casefold().strip()
    ensure(len(p) >= 50 and len(t) >= 40, "TRANSFER_STEMS_NOT_OBSERVED")
    if p == t:
        return {"sufficient_novelty_evidence": False,
                "reason": "TRANSFER_EXACT_PRIMARY_CLONE"}
    checks = {
        "QRT-EXPLAIN-D3": (r"\|t\s*[-−]\s*1\|", r"\b(?:change|changed|different)\b"),
        "QRT-MODEL-D2": (r"\b(?:possible|impossible|feasib)\w*\b",
                         r"\b(?:below|above)\b"),
        "QRT-RETRIEVE-D2": (r"\b(?:reverse|in\s+reverse)\b",
                            r"\b(?:missing|unknown)\s+side\b"),
        "QRT-RETRIEVE-D4": (r"\bmodulus\s+is\s+now\s+4\b",
                            r"\bmodulo\s*8\b")
    }
    ensure(cell in checks, "UNSUPPORTED_TRANSFER_ORACLE", cell)
    absent = [regex for regex in checks[cell] if not re.search(regex, t, re.I)]
    return {
        "sufficient_novelty_evidence": not absent,
        "reason": ("QUALITATIVE_CHANGE_MARKERS_PRESENT_NOT_MASTERY_PROOF"
                   if not absent else "TRANSFER_CHANGE_OR_DECISION_MISSING"),
        "missing_markers": absent,
        "source_stem_changed": p != t
    }


def gate_check(gates: dict) -> list[str]:
    hits = []
    if gates.get("core1b_main_attempt_unlocked_boundary") is True:
        hits.append("CORE1B_BOUNDARY_UNLOCKED_BY_MAIN_COMMIT")
    if gates.get("core1b_blank_boundary_unlocked") is True:
        hits.append("CORE1B_BLANK_BOUNDARY_UNLOCKED")
    if gates.get("core2a_h3_unlocked_before_commit") is True:
        hits.append("CORE2A_H3_PREATTEMPT_UNLOCKED")
    if gates.get("precommit_payload_materialized") is True:
        hits.append("PRECOMMIT_PROTECTED_PAYLOAD_MATERIALIZED")
    if gates.get("blank_main_unlocked") is True:
        hits.append("BLANK_MAIN_UNLOCKED_PROTECTED_PAYLOAD")
    return hits


def evaluate_paths(cell: str, states: dict, gates: dict) -> dict:
    ensure(set(states) == set(ROLES), "P2_FIVE_NATIVE_SURFACES_REQUIRED")
    all_findings = []
    per_path = {}
    for key, roles in PATHS.items():
        found = []
        for role in dict.fromkeys(roles):
            for hit in known_exposure(cell, role, states[role]):
                found.append({"role": role, "finding": hit})
        per_path[key] = {
            "roles": list(roles),
            "source": "SIMULATED_CUMULATIVE_PAGE_EXPOSURE_NOT_CLICK_THROUGH",
            "findings": found,
            "automated_review_status": ("KNOWN_DEFECT_OR_METHOD_CUE"
                                        if found else "REVIEW_REQUIRED_NO_KNOWN_LEAK"),
            "independent_evidence": (
                False if key == "CORE2A_TO_CORE1A_ASSISTED_RETURN" else
                "NOT_ESTABLISHED_BY_BROWSER"
            )
        }
        all_findings.extend({"path": key, **f} for f in found)
    novelty = transfer_novelty(cell, states["CORE2A"]["stem"],
                              states["CORE2B"]["stem"])
    if not novelty["sufficient_novelty_evidence"]:
        all_findings.append({"path": "CORE2A_TO_CORE2B_TRANSFER",
                             "role": "CORE2B",
                             "finding": novelty["reason"]})
    for issue in gate_check(gates):
        all_findings.append({"path": "GATING", "role": "CORE1B" if
                             issue.startswith("CORE1B") else "CORE2A",
                             "finding": issue})
    return {
        "paths": per_path,
        "transfer": novelty,
        "gate_findings": gate_check(gates),
        "all_finding_ids": sorted(set(f["finding"] for f in all_findings)),
        "all_findings": all_findings,
        "semantic_verdict": "HOLD_REVIEW_REQUIRED",
        "automated_qrta_acceptance": False,
        "limitations": (
            "Five real native surfaces are inspected in Chromium; path aggregation "
            "is a simulated cumulative exposure, not a click-through navigation "
            "or evidence of learner mastery. Known sentinel absence cannot certify "
            "absence of semantic paraphrases; source-specific novelty markers "
            "cannot establish transfer competence."
        ),
    }


def capture(browser, source_root: Path, output: Path) -> tuple[dict, dict, list]:
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(RootAssets, source_root=source_root)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    states, records = {}, []
    gates = {
        "core1b_main_attempt_unlocked_boundary": False,
        "core1b_blank_boundary_unlocked": False,
        "core2a_h3_unlocked_before_commit": False,
        "precommit_payload_materialized": False,
        "blank_main_unlocked": False,
    }
    try:
        rel = output.resolve().relative_to(source_root.resolve()).as_posix()
        for role in ROLES:
            widths = (390, 768, 1280) if role in ("CORE2A", "CORE2B") else (390,)
            for width in widths:
                page = browser.new_page(viewport={"width": width, "height": 900})
                try:
                    errors = []
                    page.on("pageerror", lambda exc: errors.append(str(exc)))
                    resp = page.goto(
                        f"http://127.0.0.1:{server.server_port}/{rel}/{role.lower()}.html",
                        wait_until="load")
                    ensure(resp is not None and resp.status == 200,
                           "P2_NATIVE_HTTP", f"{role}/{width}")
                    ensure(page.locator(f"html[data-g9-role='{role}']").count() == 1
                           and page.locator("body[data-blueprint-ref]").get_attribute(
                               "data-blueprint-ref") == BP[role],
                           "P2_ROLE_BLUEPRINT", f"{role}/{width}")
                    article = page.locator("article[data-g9-unit]").first
                    ensure(article.count() == 1 and article.is_visible(),
                           "P2_ARTICLE_MISSING", f"{role}/{width}")
                    styles = page.evaluate("""() => [...document.querySelectorAll(
                        'link[rel=stylesheet]')].map(x=>Boolean(x.sheet))""")
                    ensure(len(styles) >= 2 and all(styles),
                           "P2_REAL_CSS_NOT_LOADED", f"{role}/{width}")
                    ensure(page.evaluate(
                        "() => document.documentElement.scrollWidth <= innerWidth + 2"),
                        "P2_OVERFLOW", f"{role}/{width}")
                    svg_names = article.locator("svg[role=img]").evaluate_all(
                        """nodes => nodes.map(x => ({
                           name:x.getAttribute('aria-label')||'',
                           title:x.querySelector('title')?.textContent||'',
                           desc:x.querySelector('desc')?.textContent||''
                        }))"""
                    )
                    ensure(all(x["name"] or x["title"] for x in svg_names),
                           "P2_UNNAMED_SVG", f"{role}/{width}")
                    payloads = article.locator(
                        "details[data-g9-reveal][data-requires-attempt]")
                    materialized = any(s.strip() for s in
                                       payloads.locator("[data-g9-payload-slot]").all_inner_texts())
                    gates["precommit_payload_materialized"] |= materialized
                    stemloc = article.locator("[data-g9-block='stem']").first
                    stem = stemloc.inner_text() if stemloc.count() else ""
                    if role in ("CORE2A", "CORE2B"):
                        ensure(stem.strip(), "P2_QUESTION_STEM_MISSING", role)
                    initial = article.inner_text()
                    state = {
                        "role": role,
                        "visible": initial,
                        "stem": stem,
                        "h2_visible": "",
                        "accessible_svg": "\n".join(
                            " ".join(x.values()) for x in svg_names),
                        "semantic_labels": "\n".join(article.locator(
                            "[aria-label]").evaluate_all(
                            "nodes => nodes.map(x => x.getAttribute('aria-label')||'')"
                        )),
                    }
                    if role == "CORE2A" and width == 390:
                        hint = article.get_by_role("button", name="Next hint")
                        ensure(hint.count() == 1, "P2_H2_CONTROL_MISSING")
                        hint.click()
                        state["h2_visible"] = article.inner_text()
                        h3 = article.locator(
                            'details[data-g9-payload-ref*="after-attempt-hint-3"]')
                        ensure(h3.count() == 1, "P2_H3_NOT_DEFINED")
                        gates["core2a_h3_unlocked_before_commit"] = (
                            h3.get_attribute("data-locked") is None
                        )
                    if width == 390 and role in ("CORE1B", "CORE2A", "CORE2B"):
                        ensure(payloads.count() >= 1, "P2_ATTEMPT_GATES_MISSING", role)
                        ensure(all(payloads.nth(i).get_attribute("data-locked") is not None
                                   for i in range(payloads.count())),
                               "P2_GATE_INITIAL_UNLOCKED", role)
                        attempt = article.locator(
                            "[data-g9-attempt-box]:not([data-g9-attempt-stage='boundary'])").first
                        if not attempt.count():
                            attempt = article
                        commit = attempt.locator("button[data-g9-commit]").first
                        answer = attempt.locator("textarea[data-g9-attempt]").first
                        ensure(commit.count() == 1 and answer.count() == 1,
                               "P2_COMMIT_CONTROLS_MISSING", role)
                        commit.click()
                        gates["blank_main_unlocked"] |= any(
                            payloads.nth(i).get_attribute("data-locked") is None
                            for i in range(payloads.count())
                        )
                        answer.fill("I will form my own reasoned decision for this new problem.")
                        commit.click()
                        ensure(payloads.first.get_attribute("data-locked") is None,
                               "P2_MAIN_COMMIT_DID_NOT_UNLOCK", role)
                        if role == "CORE1B":
                            boundary = article.locator(
                                "details[data-g9-attempt-stage='boundary'][data-requires-attempt]")
                            box = article.locator(
                                "[data-g9-attempt-box][data-g9-attempt-stage='boundary']")
                            ensure(boundary.count() == 1 and box.count() == 1,
                                   "P2_BOUNDARY_GATE_MISSING")
                            gates["core1b_main_attempt_unlocked_boundary"] = (
                                boundary.get_attribute("data-locked") is None)
                            box.locator("button[data-g9-commit]").click()
                            gates["core1b_blank_boundary_unlocked"] = (
                                boundary.get_attribute("data-locked") is None)
                    ensure(not errors, "P2_PAGE_JS_ERROR", repr(errors))
                    if width == 390:
                        states[role] = state
                    records.append({
                        "role": role, "viewport": width, "http": 200,
                        "original_stylesheets_loaded": True,
                        "named_svg_count": len(svg_names),
                        "horizontal_overflow": False,
                        "live_browser_gate_tested": (
                            width == 390 and role in ("CORE1B", "CORE2A", "CORE2B")),
                        "native_sha256": sha256(output / (role.lower() + ".html"))
                    })
                finally:
                    page.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
    return states, gates, records


def mutants(cell, states, gates) -> list[dict]:
    """Run five deliberate defects through the SAME decision engine."""
    cases = []
    if cell == "QRT-MODEL-D2":
        s = copy.deepcopy(states)
        s["CORE2A"]["stem"] += (
            " Let x be the large-cup count and use 4(9−x)+7x=48."
        )
        cases.append(("MODEL_PRESELECTED_EQUATION",
                      "MODEL_D2_TARGET_WEIGHTED_EQUATION_DISCLOSED", s, gates))
    if cell == "QRT-EXPLAIN-D3":
        s = copy.deepcopy(states)
        s["CORE2A"]["accessible_svg"] += (
            "\nStage SVG aria-label: Reject x=-1 because sqrt is nonnegative"
            " while x-1 is negative: that sign contradiction makes it extraneous."
        )
        cases.append(("EXPLAIN_SVG_ACCESSIBLE_VERDICT",
                      "EXPLAIN_D3_TARGET_SIGN_VERDICT_DISCLOSED", s, gates))
    if cell == "QRT-RETRIEVE-D4":
        s = copy.deepcopy(states)
        s["CORE1A"]["visible"] += (
            "\nFor k>=3 an odd residue is an odd-square iff a≡1 mod8."
        )
        cases.append(("D4_RESTORE_FULL_PRIOR_THEOREM",
                      "RETRIEVE_D4_FULL_THRESHOLD_IFF_PREATTEMPT", s, gates))
    if cell == "QRT-RETRIEVE-D2":
        s = copy.deepcopy(states)
        # A numerical clone using changed side lengths but the same forward
        # diagonal method must NOT count as independent inverse-relation work.
        s["CORE2B"]["stem"] = (
            "A rectangle has perpendicular sides 12m and 16m; retrieve the"
            " distance relation and calculate both routes with a new cap."
        )
        cases.append(("TRANSFER_NUMERIC_CLONE",
                      "TRANSFER_CHANGE_OR_DECISION_MISSING", s, gates))
        g = copy.deepcopy(gates)
        g["core1b_main_attempt_unlocked_boundary"] = True
        cases.append(("CORE1B_BOUNDARY_PREMATURE_UNLOCK",
                      "CORE1B_BOUNDARY_UNLOCKED_BY_MAIN_COMMIT", states, g))
    checks = []
    for name, expected, s, g in cases:
        result = evaluate_paths(cell, s, g)
        ensure(expected in result["all_finding_ids"],
               "P3_MUTANT_ESCAPED", f"{cell}:{name} expected {expected}")
        checks.append({"name": name, "injected_defect": expected,
                       "caught_by_same_path_engine": True,
                       "test_only_mutation": True})
    return checks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--native-contract", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--native-output", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--run-mutants", action="store_true")
    args = ap.parse_args()
    evidence = read_json(args.native_contract)
    ensure(evidence.get("native_evidence", {}).get("all_role_structure") == "PASS",
           "P2_P1_PROOF_REQUIRED")
    cell = evidence["cell_id"]
    # P2 refuses stale pages after P1 if even one native page was changed.
    for role, row in evidence["native_evidence"]["roles"].items():
        ensure(sha256(args.native_output / (role.lower() + ".html")) ==
               row["native_sha256"], "P2_NATIVE_P1_SHA_CHANGED", role)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            states, gates, browser_checks = capture(browser, args.source_root,
                                                    args.native_output)
        finally:
            browser.close()
    # Hash-only report of extracted learner-visible content to avoid
    # duplicating authored question source in evidence reports.
    summarized = {
        role: {
            "sha256_initial_visible": hashlib.sha256(
                state["visible"].encode("utf-8")).hexdigest(),
            "sha256_svg_accessibility": hashlib.sha256(
                state["accessible_svg"].encode("utf-8")).hexdigest(),
            "initial_visible_chars": len(state["visible"]),
            "svg_accessible_chars": len(state["accessible_svg"]),
            "h2_visible_chars": len(state["h2_visible"]),
        } for role, state in states.items()
    }
    audit = evaluate_paths(cell, states, gates)
    mutation_results = mutants(cell, states, gates) if args.run_mutants else []
    evidence["whole_journey_W"] = {
        "status": "KNOWN_METHOD_CUE_HOLD" if
        "RETRIEVE_D2_METHOD_SELECTION_ALREADY_CUED" in audit["all_finding_ids"]
        else "REVIEW_REQUIRED",
        "paths_checked": list(PATHS),
        "assisted_retry_is_independent": False,
        "known_finding_ids": audit["all_finding_ids"],
    }
    evidence["p2_p3_live_evidence"] = {
        "live_browser": True,
        "browser_learner_role_viewports": browser_checks,
        "initial_content_hashes": summarized,
        "attempt_gate_states": gates,
        "known_exposure": audit,
        "source_specific_mutants": mutation_results,
        "mutants_rejected": len(mutation_results),
        "academic_verdict": "PENDING",
        "owner_qrt_accepted": False,
        "external_semantic_review": "REQUIRED",
        "claim_boundary": "Known leak detectors, not a proof of complete W preservation"
    }
    evidence["native_evidence"]["browser_and_AX"] = "P2_LIVE_SCOPED_CHECKS_PASS"
    evidence["native_evidence"]["cross_core_W"] = (
        "KNOWN_METHOD_CUE_OR_HOLD_REVIEW_REQUIRED"
    )
    # QRT semantic and academic status deliberately never promoted.
    ensure(all(evidence["roles"][r]["semantic"] == "NOT_RUN"
               for r in ROLES), "P2_AUTO_SEMANTIC_PROMOTION")
    ensure(evidence["owner_qrt_acceptance"] == "PENDING",
           "P2_OWNER_ACCEPTANCE_FORBIDDEN")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"{cell}: P2 {len(browser_checks)} live viewport probes, "
          f"{len(PATHS)} simulated learner paths, "
          f"P3 {len(mutation_results)} bad mutants REJECTED; "
          f"findings={audit['all_finding_ids']}; academic+Owner HOLD")


if __name__ == "__main__":
    main()
