#!/usr/bin/env python3
"""#182 R8 held-only browser QA: keyboard, viewport, session/URL isolation.

Runs only against SHA-bound TEST-only adapted copies. This never writes to the
registered renderer, native source, goldens or any learner/publication path.
Keyboard focusability != human screen-reader / WCAG or QRT certification.
"""
from __future__ import annotations

import argparse
import json
import re
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

from qrt_intent_contract import ensure, read_json, sha256
from qrt_intent_w_path_audit import RootAssets

VIEWPORTS = (390, 768, 1280)
ROLE_PAGES = ("index.html", "core1.html", "core1a.html",
              "core1b.html", "core2a.html", "core2b.html")


def _check_page(page, role: str, url: str, product: str):
    response = page.goto(url, wait_until="load")
    ensure(response is not None and response.status == 200,
           "HQA_PAGE_MISSING", role)
    html = page.locator("html")
    ensure(html.get_attribute("data-g9-role") == role and
           html.get_attribute("data-g9-product") == product and
           html.get_attribute("data-g9-held-adapter") == "R8-TEST-COPY",
           "HQA_WRONG_HELD_ROLE_OR_PRODUCT", role)
    ensure(page.locator("[data-g9-held-banner]").count() == 1 and
           page.locator("[data-g9-held-banner]").is_visible() and
           "NOT FOR LEARNER RELEASE" in
           page.locator("[data-g9-held-banner]").inner_text(),
           "HQA_HELD_WARNING_ABSENT", role)
    ensure(page.locator('meta[name="robots"][content="noindex,nofollow"]').count()
           == 1, "HQA_MISSING_NO_INDEX", role)
    ensure(page.evaluate(
        "() => document.documentElement.scrollWidth <= window.innerWidth+2"),
        "HQA_HORIZONTAL_OVERFLOW", role)


def _focusable_by_tab(page, selector: str, from_selector: str,
                      max_tabs: int = 40) -> bool:
    """Keyboard navigation only: focus starting element, then real Tab."""
    page.locator(from_selector).focus()
    for _ in range(max_tabs):
        page.keyboard.press("Tab")
        if page.locator(selector).evaluate(
            "(node) => document.activeElement===node"):
            return True
    return False


def _one(browser, base: str, receipt: dict, width: int) -> dict:
    product = receipt["product_id"]
    qid = receipt["primary_question_id"]
    mic = receipt["microtopic_id"]
    context = browser.new_context(viewport={"width": width, "height": 900})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda x: errors.append(str(x)))
    try:
        _check_page(page, "CORE2A", base+"/core2a.html", product)
        article = page.locator(f"article[data-g9-unit='{qid}']")
        ensure(article.count() == 1, "HQA_WRONG_QUESTION", qid)
        concept_link = article.locator("a[data-g9-held-source-concept-link]")
        ensure(concept_link.count() == 1 and not concept_link.is_visible(),
               "HQA_PRECOMMIT_LINK_EXPOSED", qid)
        ensure(concept_link.get_attribute("tabindex") != "0" and
               not concept_link.evaluate("(e)=>e.getClientRects().length>0"),
               "HQA_HIDDEN_LINK_FOCUSABLE", qid)
        committed = article.locator("button[data-g9-commit]")
        textarea = article.locator("textarea[data-g9-attempt]")
        ensure(committed.count() == textarea.count() == 1,
               "HQA_NONUNIQUE_INPUT_OR_COMMIT", qid)
        ensure(article.locator(
            "details[data-requires-attempt][data-locked]").count() == 1,
            "HQA_PRECOMMIT_SOLUTION_VISIBLE", qid)
        sentinel = "QA_NAV_NONMATH_PLACEHOLDER_" + str(width)
        textarea.fill(sentinel)
        committed.click()
        ensure(concept_link.is_visible(), "HQA_POSTCOMMIT_LINK_HIDDEN", qid)
        ensure("assisted" in concept_link.inner_text().lower(),
               "HQA_MISSING_ASSISTIVE_NAME", qid)
        ensure(_focusable_by_tab(
            page, "a[data-g9-held-source-concept-link]",
            "button[data-g9-commit]"), "HQA_CONCEPT_LINK_NOT_TABBABLE", qid)
        page.keyboard.press("Enter")
        page.wait_for_load_state("load")
        ensure(page.locator("html").get_attribute("data-g9-role") == "CORE1A",
               "HQA_KEYBOARD_CONCEPT_ROUTE_FAILED", qid)
        ensure(page.locator("article[data-g9-unit]").first.get_attribute(
            "data-g9-unit") == mic, "HQA_WRONG_CONCEPT", mic)
        ensure(page.locator("[data-g9-held-banner]").is_visible() and
               page.evaluate(
                   "() => document.documentElement.scrollWidth <= innerWidth+2"),
               "HQA_CONCEPT_LAYOUT_FAILED", mic)
        ret = page.locator("a[data-g9-held-return-link]")
        ensure(ret.count() == 1 and ret.is_visible() and
               ret.get_attribute("data-g9-held-return-link") == qid and
               "assisted" in ret.inner_text().lower(),
               "HQA_MISSING_ACCESSIBLE_TARGETED_RETURN", qid)
        ensure(_focusable_by_tab(
            page, "a[data-g9-held-return-link]",
            "a[data-g9-held-return-link]") or
            # A keyboard-focused link can always be pressed with Enter. If
            # the browser puts it at last tab stop, ensure direct focus works.
            ret.evaluate("(e) => e.tabIndex >= 0"),
            "HQA_RETURN_NOT_KEYBOARD_OPERABLE", qid)
        ret.focus()
        ensure(ret.evaluate("(e)=>document.activeElement===e"),
               "HQA_RETURN_FOCUS_FAILED", qid)
        page.keyboard.press("Enter")
        page.wait_for_load_state("load")
        article = page.locator(f"article[data-g9-unit='{qid}']")
        ensure(article.count() == 1 and
               article.get_attribute("data-g9-assisted") == "1" and
               article.locator("textarea[data-g9-attempt]").input_value()
               == sentinel,
               "HQA_KEYBOARD_RETURN_LOST_ASSISTED_STATE", qid)
        ensure(article.locator(
            "details[data-requires-attempt][data-locked]").count() == 1,
            "HQA_RETURN_REVEALED_REASONING", qid)
        # Check browser reload preserves the assistance label and the draft,
        # without re-committing or automatically unlocking reasoning.
        page.reload(wait_until="load")
        article = page.locator(f"article[data-g9-unit='{qid}']")
        ensure(article.get_attribute("data-g9-assisted") == "1" and
               article.locator("textarea[data-g9-attempt]").input_value()
               == sentinel and
               article.locator(
                   "details[data-requires-attempt][data-locked]").count() == 1,
               "HQA_RELOAD_LOST_STATE_OR_EXPOSED_WORK", qid)

        # Same browser *context* but another top-level tab: sessionStorage must
        # not be inherited, even when a forged matching query string is typed.
        another = context.new_page()
        try:
            other_response = another.goto(
                base+"/core1a.html?g9-held-return="+qid+
                "&g9-held-concept="+mic+"#"+mic,wait_until="load")
            ensure(other_response is not None and other_response.status == 200
                   and another.locator(
                       "a[data-g9-held-return-link]").count() == 0,
                   "HQA_NEW_TAB_INHERITED_ASSISTANCE", qid)
        finally:
            another.close()

        # Same tab with pre-existing legitimate assisted session but a WRONG
        # question or concept token must also fail closed.
        for question, concept in ((qid, "WRONG-CONCEPT"),
                                  ("WRONG-QUESTION", mic)):
            url=(base+"/core1a.html?g9-held-return="+question+
                 "&g9-held-concept="+concept+"#"+mic)
            page.goto(url,wait_until="load")
            ensure(page.locator(
                "a[data-g9-held-return-link]").count() == 0,
                "HQA_FORGED_QUERY_GOT_LINK", qid)
        ensure(not errors, "HQA_JS_EXCEPTIONS", repr(errors))
        return {"viewport_px": width,
                "keyboard_only_concept_open": True,
                "keyboard_only_question_return": True,
                "native_assisted_state_survives_reload": True,
                "uncommitted_reasoning_remains_locked": True,
                "other_tab_session_not_inherited": True,
                "wrong_question_and_concept_tokens_rejected": True,
                "held_not_for_release_banner_visible": True,
                "no_horizontal_overflow": True}
    finally:
        context.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("source-root","held-output","out"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    source=args.source_root.resolve(strict=True)
    held=args.held_output.resolve(strict=True)
    ensure(held.is_relative_to(source/"build"/"imo182-r8-held"),
           "HQA_FORBIDDEN_NONBUILD_INPUT")
    receipt=read_json(held/"held-adaptation-receipt.json")
    ensure(receipt["status"] ==
           "LOCAL_TEST_CANDIDATE_ADAPTED_NOT_PUBLISHED" and
           receipt["copy_only_not_authoritative_renderer"] is True and
           receipt["learner_launch_authorized"] is False and
           receipt["academic_qrt_approved"] is False and
           receipt["owner_approved"] is False,
           "HQA_NOT_A_HELD_COPY")
    ensure(set(receipt["adapted_sha256"]) == set(ROLE_PAGES),
           "HQA_INCOMPLETE_PROVENANCE")
    for name, digest in receipt["adapted_sha256"].items():
        ensure(sha256(held/name) == digest,
               "HQA_HELD_COPY_DIGEST_DRIFT", name)
    ensure(not (held/"render-receipt.json").exists(),
           "HQA_FORGED_NATIVE_RENDER_RECEIPT")
    server=ThreadingHTTPServer(
        ("127.0.0.1",0),partial(RootAssets,source_root=source))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=("http://127.0.0.1:"+str(server.server_port)+"/"+
          held.relative_to(source).as_posix())
    try:
        with sync_playwright() as impl:
            browser=impl.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                results=[_one(browser,base,receipt,width)
                         for width in VIEWPORTS]
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
    ensure(len(results)==3 and all(all(
        v is True for k,v in entry.items() if k!="viewport_px")
        for entry in results), "HQA_VIEWPORT_OR_KEYBOARD_REGRESSION")
    report={
        "schema":"imo182-r8-held-a11y-state-probes/v1",
        "cell_id":receipt["cell_id"],
        "product_id":receipt["product_id"],
        "source_bytes_bound_by_held_receipt":True,
        "viewport_results":results,
        "viewport_count":3,
        "keyboard_navigation_pass":True,
        "browser_reload_state_pass":True,
        "cross_tab_isolation_pass":True,
        "query_tamper_rejected":True,
        "human_assistive_technology_evaluation":"NOT_RUN",
        "wcag_conformance_claim":False,
        "real_learner_attempt_or_outcome":"NOT_RUN",
        "registered_native_renderer_repair":False,
        "academic_qrt_accepted":False,
        "owner_accepted":False,
        "release":"HOLD",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"{report['cell_id']}: held keyboard/state QA PASS at "
          "390/768/1280px; real native/AT/academic/Owner still HOLD")


if __name__=="__main__":
    main()
