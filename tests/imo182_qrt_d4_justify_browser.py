"""Actual Chromium inspection of sole-renderer generated D4 learner HTML.

QA evidence is TEST-only and cannot assign QRT/Owner acceptance.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

folder=Path("build/imo182-qrt/d4/justify").resolve()
receipt=json.loads((folder/"render-receipt.json").read_text())
assert receipt["gaps"]==[], receipt["gaps"]
screens=folder/"browser"
screens.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for role in ("core1","core1a","core1b","core2a","core2b"):
        page=browser.new_page(viewport={"width":1280,"height":900})
        page.goto((folder/(role+".html")).as_uri())
        assert page.locator('body').inner_text().strip(),role
        assert page.locator('[data-blueprint-ref]').count()>0,role
        page.screenshot(path=str(screens/(role+".png")), full_page=True)
        if role=="core2a":
            gated=page.locator('[data-g9-after-attempt-hint]')
            assert gated.count()==1,"H3 gate missing"
            assert not gated.is_visible(),"H3 shown before attempt"
            assert not page.get_by_text("After recording your first attempt",exact=False).is_visible(),"H3 visible preattempt"
            # No learner answer is entered: preattempt gate must remain closed.
            assert page.locator("[data-requires-attempt]").count()>0
        page.close()
    browser.close()
print("CHROMIUM_FIVE_ROLES_AND_INITIAL_H3_GUARD_PASS")
