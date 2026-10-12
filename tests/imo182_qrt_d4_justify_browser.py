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
            # H3 is in an inert <template>, not a live DOM node before an attempt.
            html=page.content()
            assert "data-g9-after-attempt-hint" in html,"H3 inert payload absent"
            assert 'data-g9-payload="CORE2A-Q-D4-JUSTIFY-24-after-attempt-hint-3"' in html
            assert "data-requires-attempt" in html
            assert not any(loc.is_visible() for loc in page.get_by_text("After recording your first attempt",exact=False).all()),"H3 text visible preattempt"
            # Before a committed answer the complete proof still belongs in gated post-attempt markup.
            assert page.locator("[data-requires-attempt]").count()>0
        page.close()
    browser.close()
print("CHROMIUM_FIVE_ROLES_AND_INITIAL_H3_GUARD_PASS")
