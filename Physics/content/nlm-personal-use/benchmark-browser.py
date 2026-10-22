#!/usr/bin/env python3
"""B1 scripted synthetic UI interactions. These are NOT student attempts or transfer evidence.
Launch: python Physics/content/nlm-personal-use/benchmark-browser.py
Requires: pip install playwright; playwright chromium or system Chromium.
"""
from __future__ import annotations
import json
import shutil
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
VIEW = (HERE / "../../../standalone/practice/nlm-core2-first-slice.html").resolve()

def check(ok, name):
    if not ok:
        raise AssertionError(name)
    print("PASS", name, flush=True)

def main():
    check(VIEW.is_file(), "entrypoint exists")
    with sync_playwright() as p:
        system_chrome = shutil.which("chromium") or shutil.which("google-chrome")
        browser = p.chromium.launch(headless=True, executable_path=system_chrome,
                                    args=["--no-sandbox"] if system_chrome else [])
        context = browser.new_context(accept_downloads=True, viewport={"width": 850, "height": 900})
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(VIEW.as_uri())
        check(page.get_by_text("Unaided diagnostic 1 of 2").is_visible(), "first diagnostic rendered")
        check(page.get_by_text("Teacher answer revealed").count() == 0, "initially no answer panel")
        check(page.locator("#hint").count() == 0, "no hint control before two baselines")
        check(page.get_by_text("A. Toward the roof.").count() == 1, "final 001 adaptation displayed")
        page.locator("input[name=choice][value=A]").check()
        page.locator("textarea[name=explanation]").fill("Synthetic benchmark probe 001: sign of change in velocity.")
        page.locator("select[name=confidence]").select_option("unsure")
        page.get_by_role("button", name="Save unaided answer and continue").click()
        check(page.get_by_text("Unaided diagnostic 2 of 2").is_visible(), "second diagnostic gated after first save")
        check(page.locator("#hint").count() == 0, "no premature hints on second diagnostic")
        check(page.get_by_text("C. A pulls the strap; the strap pulls A.").count() == 1, "final 002 adaptation displayed")
        page.locator("input[name=choice][value=B]").check()
        page.locator("textarea[name=explanation]").fill("Synthetic benchmark probe 002: compare body owners.")
        page.locator("select[name=confidence]").select_option("somewhat")
        page.get_by_role("button", name="Save unaided answer and continue").click()
        check(page.get_by_text("Supported return · already seen, NOT an unseen retry").is_visible(), "supported stage after exactly two baseline saves")
        for n in [1, 2, 3]:
            page.locator("#hint").click()
            check(page.get_by_text(f"H{n} ·", exact=False).count() >= 1, f"authored H{n} help shown")
        check(page.locator("#hint").is_disabled(), "hint ladder hard-stops at H3")
        page.locator("input[name=choice][value=B]").check()
        page.locator("textarea[name=explanation]").fill("Synthetic benchmark supported attempt after hints.")
        page.locator("select[name=confidence]").select_option("sure")
        page.get_by_role("button", name="Save supported attempt").click()
        check(page.get_by_text("Feedback on the selected option").count() >= 1, "selected-option feedback after supported attempt")
        page.locator("#reveal").click()
        check(page.get_by_text("Full teacher answer · deliberately revealed").is_visible(), "deliberate reveal")
        check(page.get_by_text("Original authored bank hints").is_visible(), "source hint provenance is separately labeled")
        with page.expect_download() as info:
            page.get_by_role("button", name="Download my session answers (.json)").click()
        d = info.value
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "session.json"
            d.save_as(str(f))
            record = json.loads(f.read_text(encoding="utf8"))
        check(len(record["baseline"]) == 2 and all(x["assisted"] is False for x in record["baseline"]), "two baseline records explicitly unassisted")
        check(len(record["supported"]) == 1 and record["supported"][0]["assisted"] is True, "hinted repeat recorded assisted, not independent")
        check(record["supported"][0]["choice"] == "B" and record["supported"][0]["hints_seen_at_attempt"] == 3, "answer/hint state captured")
        check(record["answer_revealed"] and any(e["kind"] == "deliberate_full_teacher_reveal" for e in record["help_events"]), "reveal event recorded")
        page.once("dialog", lambda dialog: dialog.accept())
        page.get_by_role("button", name="Reset this session").click()
        check(page.get_by_text("Unaided diagnostic 1 of 2").is_visible(), "explicit reset returns first diagnostic")
        check(not errors, "zero browser script exceptions: " + repr(errors))
        context.close()
        browser.close()
    print("RESULT: browser flow PASS (synthetic only; not learner validation)", flush=True)

if __name__ == "__main__":
    main()
