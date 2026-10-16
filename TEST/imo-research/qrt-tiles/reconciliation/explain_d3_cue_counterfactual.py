#!/usr/bin/env python3
"""Test only: EXPLAIN-D3 preattempt cue counterfactual, not an adopted source fix.

Run against an exact, disposable #224 author checkout. Source is restored after
native rendering. No algorithmic Mathematics grader or academic approval exists.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright
from o1_explain_d3_proposed_labels import (
    SOURCE_COMMIT, SOURCE_BLOB, MANIFEST_BLOB, REGISTRY_BLOB,
    LOCK_BLOB, gitblob, sha, ensure,
)

QUESTION = "Q-TEST-QRT-EXPLAIN-D3-BOUNDARY"
OLD_CONDITION = "Absolute-value bars make the whole RHS nonnegative."
OLD_HINT = ("The absolute-value operation changes the RANGE of an entire "
            "expression. What sign fact is different now?")
NEW_HINT = ("Compare the changed equation with the earlier one. "
            "Which earlier reasoning step needs re-examination?")
SOURCE_PATH = "TEST/imo-research/qrt-d3/explain.v1.json"
MANIFEST = "TEST/products/imo182-qrt-d3-explain.manifest.json"
ARCHIVED_CORE2B_SHA = "cb16c27aba85008888466c705d1580772515f890ce51887b49cdd8341016972a"


def proposal(source: dict) -> tuple[dict, list[dict]]:
    changed = copy.deepcopy(source)
    matches = [q for q in changed.get("questions", []) if q.get("id") == QUESTION]
    ensure(len(matches) == 1, "TARGET_QUESTION_NOT_UNIQUE")
    q = matches[0]
    ensure(q.get("status") == "CANDIDATE" and q.get("origin") == "AUTHORED",
           "DO_NOT_EDIT_NONTEST_OR_APPROVED")
    conditions = q["conditions"]
    ensure(conditions.count(OLD_CONDITION) == 1, "SOURCE_CONDITION_DRIFT")
    hints = q["hints"]
    ensure(len(hints) == 1 and hints[0]["text"] == OLD_HINT, "SOURCE_HINT_DRIFT")
    q["conditions"] = [v for v in conditions if v != OLD_CONDITION]
    q["hints"][0]["text"] = NEW_HINT
    edits = [
        {"path": "questions[Q-TEST-QRT-EXPLAIN-D3-BOUNDARY].conditions",
         "removed": OLD_CONDITION},
        {"path": "questions[Q-TEST-QRT-EXPLAIN-D3-BOUNDARY].hints[0].text",
         "old": OLD_HINT, "proposed": NEW_HINT},
    ]
    # Negative-control verification: the only changes are the two intended
    # source fields. All answers, hashes, IDs and neighboring questions retain
    # the exact original values.
    reverse = copy.deepcopy(changed)
    target = next(q for q in reverse["questions"] if q["id"] == QUESTION)
    target["conditions"] = list(conditions)
    target["hints"][0]["text"] = OLD_HINT
    ensure(reverse == source, "UNAUTHORIZED_OTHER_SOURCE_MUTATION")
    return changed, edits


def native_build(root: Path, name: str) -> tuple[Path, dict]:
    out = root / ("build/imo182-qrt/d3/" + name)
    subprocess.run([
        sys.executable, "Shared/tools/render_core.py", "build",
        "--manifest", MANIFEST, "--out", str(out.relative_to(root)),
        "--mode", "PAGES", "--reference", "--draft"
    ], check=True, cwd=root)
    receipt = json.loads((out / "render-receipt.json").read_text(encoding="utf-8"))
    ensure(receipt["renderer"] == "render_core/2" and not receipt["gaps"]
           and receipt["mode"] == "PAGES", "NATIVE_RENDER_INVALID")
    for filename, expected in receipt["page_sha256"].items():
        ensure(sha(out / filename) == expected, "NATIVE_RECEIPT_SHA_MISMATCH")
    return out, receipt


def run(root: Path, ledger_root: Path) -> dict:
    source = root / SOURCE_PATH
    original_raw = source.read_bytes()
    originals = {
        SOURCE_PATH: SOURCE_BLOB,
        MANIFEST: MANIFEST_BLOB,
        "Shared/web/interactive-page-blueprints.v1.json": REGISTRY_BLOB,
        "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json": LOCK_BLOB,
    }
    ensure(subprocess.check_output(["git", "rev-parse", "HEAD"],
                                   cwd=root, text=True).strip() == SOURCE_COMMIT,
           "SOURCE_HEAD_DRIFT")
    for filename, expected in originals.items():
        ensure(gitblob(root, root / filename) == expected, "PINNED_BLOB_DRIFT:" + filename)
    ledger = json.loads((ledger_root /
        "TEST/imo-research/qrt-tiles/reconciliation/r5-01-28-artifact-adoption.v1.json"
    ).read_text(encoding="utf-8"))
    row = [r for r in ledger["rows"] if r["cell_id"] == "QRT-EXPLAIN-D3"]
    ensure(len(row) == 1 and row[0]["source"]["git_blob_sha"] == SOURCE_BLOB,
           "TEST_LEDGER_SOURCE_DRIFT")
    changed, edits = proposal(json.loads(original_raw))
    baseline, baseline_receipt = native_build(root, "explain-cue-original")
    ensure(baseline_receipt["page_sha256"]["core2b.html"] == ARCHIVED_CORE2B_SHA
           and row[0]["artifact"]["native_html_sha256"] == baseline_receipt["page_sha256"],
           "BASELINE_SIX_ARTIFACTS_NOT_REPRODUCED")
    overlay = root / "build/imo182-qrt/d3-explain-cue-counterfactual"
    overlay.mkdir(parents=True, exist_ok=True)
    try:
        source.write_text(json.dumps(changed, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        candidate_blob = gitblob(root, source)
        candidate, receipt = native_build(root, "explain-cue-proposed")
    finally:
        source.write_bytes(original_raw)
    ensure(gitblob(root, source) == SOURCE_BLOB, "SOURCE_NOT_BYTE_RESTORED")
    ensure(receipt["page_sha256"]["core2b.html"] != ARCHIVED_CORE2B_SHA,
           "CUE_CHANGE_NOT_PROJECTED_TO_NATIVE_PAGE")
    # Native pages include package provenance: a one-question source edit may
    # legitimately change the HTML *bytes* for ALL roles, not just Core2B.
    # Record hashes; compare the OTHER roles' actual learner-visible content
    # and registered blueprint/role sequences instead of claiming byte parity.
    role_native_changed = {
        role: (receipt["page_sha256"][role] != baseline_receipt["page_sha256"][role])
        for role in ("core1.html", "core1a.html", "core1b.html", "core2a.html",
                     "core2b.html", "index.html")
    }
    ensure(role_native_changed["core2b.html"], "TARGET_PAGE_SHA_NOT_CHANGED")

    sys.path.insert(0, str(root / "TEST/imo-research/qrt-d3-successor"))
    from browser_stage_217 import RootHandler
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(RootHandler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    records = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for width in (390, 768, 1280):
                    for other_role in ("core1", "core1a", "core1b", "core2a"):
                        observed = []
                        for kind, path in (("baseline", baseline),
                                           ("proposal", candidate)):
                            other = browser.new_page(
                                viewport={"width": width, "height": 900})
                            url = ("http://127.0.0.1:" + str(server.server_port)
                                   + "/" + str((path / (other_role + ".html")).relative_to(root)))
                            reply = other.goto(url, wait_until="load")
                            ensure(reply and reply.status == 200,
                                   "NON_TARGET_NATIVE_HTTP_FAILED")
                            observed.append({
                                "visible": other.locator("main").inner_text(),
                                "slots": other.locator("[data-blueprint-slot]").evaluate_all(
                                    "els => els.map(e=>e.getAttribute('data-blueprint-slot'))"),
                                "blocks": other.locator("[data-g9-block]").evaluate_all(
                                    "els => els.map(e=>e.getAttribute('data-g9-block'))"),
                                "role": other.locator("html").get_attribute("data-g9-role")
                            })
                            other.close()
                        ensure(observed[0] == observed[1],
                               f"UNEXPECTED_NON_TARGET_LEARNER_SEMANTIC_CHANGE:{other_role}/{width}")
                    for kind, path in (("baseline", baseline), ("proposal", candidate)):
                        page = browser.new_page(viewport={"width": width, "height": 900})
                        errors = []
                        page.on("pageerror", lambda e: errors.append(str(e)))
                        url = ("http://127.0.0.1:" + str(server.server_port)
                               + "/" + str((path / "core2b.html").relative_to(root)))
                        response = page.goto(url, wait_until="load")
                        ensure(response and response.status == 200, "NATIVE_HTTP_NOT_200")
                        article = page.locator(
                            "article[data-g9-unit='Q-TEST-QRT-EXPLAIN-D3-BOUNDARY']")
                        ensure(article.count() == 1 and article.is_visible(),
                               "WRONG_CORE2B_QUESTION")
                        visible = article.inner_text()
                        ensure("sqrt(t+5)=|t-1|" in visible, "STEM_WAS_LOST")
                        old_condition_visible = OLD_CONDITION in visible
                        old_hint_visible = OLD_HINT in visible
                        new_hint_visible = NEW_HINT in visible
                        if kind == "baseline":
                            ensure(old_condition_visible and old_hint_visible
                                   and not new_hint_visible,
                                   "EXACT_BASELINE_CUES_ABSENT")
                        else:
                            ensure(not old_condition_visible and not old_hint_visible
                                   and new_hint_visible,
                                   "PROPOSAL_CUE_REDUCTION_NOT_APPLIED")
                        gated = article.locator(
                            "details[data-g9-reveal][data-requires-attempt]")
                        slot = gated.locator("[data-g9-payload-slot]").first
                        ensure(gated.count() == 1 and not gated.evaluate("(e)=>e.open")
                               and not slot.inner_text().strip(),
                               "PREATTEMPT_SOLUTION_DISCLOSED")
                        attempt = article.locator("[data-g9-attempt]").first
                        ensure(attempt.count() == 1, "RESPONSE_CONTROL_MISSING")
                        btn = article.locator("[data-g9-commit]").first
                        ensure(btn.count() == 1 and btn.is_visible(),
                               "COMMIT_CONTROL_MISSING")
                        await_value = ("I will examine whether reversing the square "
                                       "operation is valid for this changed equation.")
                        attempt.fill(await_value)
                        btn.click()
                        gated.locator("summary").click()
                        ensure(gated.evaluate("(e)=>e.open")
                               and slot.inner_text().strip(),
                               "POSTATTEMPT_REVIEW_NOT_REVEALED")
                        ensure(not errors, "CHROMIUM_ERRORS:" + str(errors))
                        shot = overlay / "screenshots" / f"{kind}-{width}-postattempt.png"
                        shot.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(shot), full_page=True,
                                        animations="disabled")
                        records.append({
                            "kind": kind, "width": width, "native_http": True,
                            "old_condition_visible": old_condition_visible,
                            "old_hint_visible": old_hint_visible,
                            "new_hint_visible": new_hint_visible,
                            "precommit_review_sealed": True,
                            "postcommit_review_available": True,
                            "screenshot_sha256": sha(shot),
                        })
                        page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    ensure(len(records) == 6, "BROWSER_6_CASES_INCOMPLETE")
    result = {
        "schema": "imo182-explain-d3-cue-counterfactual/test-only-v1",
        "cell": "QRT-EXPLAIN-D3", "question_id": QUESTION,
        "source_commit": SOURCE_COMMIT, "original_source_blob": SOURCE_BLOB,
        "candidate_temporary_source_blob": candidate_blob,
        "original_source_byte_restored": True,
        "source_only_edits": edits,
        "baseline_native_sha256": baseline_receipt["page_sha256"],
        "candidate_native_sha256": receipt["page_sha256"],
        "package_wide_html_hash_changed": role_native_changed,
        "non_target_4_core_role_visible_content_and_structure_equal":
            "PASS_REAL_CHROMIUM_3_VIEWPORTS",
        "browser_cases": records,
        "technical_verdict": "PROPOSED_CUE_REDUCTION_RENDERED_AND_ATTEMPT_GATED",
        "semantic_independent_transfer": "NOT_DEMONSTRATED_BY_THIS_TEST",
        "right_answer_alternatives_graded": "NO_GRADER_ON_NATIVE_FREE_RESPONSE_PAGE",
        "qualified_reviewer": "UNASSIGNED",
        "owner_accepted": False, "source_adopted": False, "release": "HOLD"
    }
    target = overlay / "explain-d3-cue-counterfactual.v1.json"
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("D3 cue counterfactual: source restored; baseline/proposal 6 real Chromium cases PASS")
    print("NOT academic/QRT approval; report " + str(target))
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--ledger-root", type=Path, default=Path.cwd())
    a = ap.parse_args()
    run(a.repo.resolve(), a.ledger_root.resolve())
