"""Actual Chromium inspection of sole-renderer generated D4 learner HTML.

QA evidence is TEST-only and cannot assign QRT/Owner acceptance.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

folder=Path("build/imo182-qrt/d4/apply").resolve()
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
        if role=="core1b":
            # The changed-given boundary has a SECOND independent written-attempt gate.
            assert page.locator('[data-g9-attempt-stage="boundary"] textarea[data-g9-attempt]').count()==1
            assert page.locator('details[data-g9-attempt-stage="boundary"][data-requires-attempt]').count()==1
        if role=="core2a":
            # H3 is in an inert <template>, not a live DOM node before an attempt.
            html=page.content()
            assert "data-g9-after-attempt-hint" in html,"H3 inert payload absent"
            assert 'data-g9-payload="CORE2A-Q-D4-APPLY-MAIN-after-attempt-hint-3"' in html
            assert "data-requires-attempt" in html
            assert not any(loc.is_visible() for loc in page.get_by_text("Only AFTER your own attempt",exact=False).all()),"H3 text visible preattempt"
            # Before a committed answer the complete proof still belongs in gated post-attempt markup.
            assert page.locator("[data-requires-attempt]").count()>0
            # A blank click may not open H3 or mark this learner attempt as committed.
            page.locator('[data-g9-attempt-box] button[data-g9-commit]').first.click()
            blank_article=page.locator('article[data-g9-unit]').first
            assert blank_article.get_attribute("data-attempted")!="1","Blank attempt improperly accepted"
            # A recorded written attempt must unlock H3; just visiting or requesting H1/H2 must not.
            attempt=page.locator('[data-g9-attempt-box] textarea[data-g9-attempt]').first
            attempt.fill("I compared an L-digit starting value with a one-digit rotation. I think the change in sign of powers of ten may depend on the original length; I still need to apply why odd length differs.")
            page.locator('[data-g9-attempt-box] button[data-g9-commit]').first.click()
            article=page.locator('article[data-g9-unit]').first
            assert article.get_attribute("data-attempted")=="1","Written attempt was not committed"
            after=page.locator('details[data-g9-payload-ref="CORE2A-Q-D4-APPLY-MAIN-after-attempt-hint-3"]')
            assert after.count()==1,"H3 gated details absent"
            after.locator("summary").click()
            assert after.locator("[data-g9-after-attempt-hint]").count()==1,"H3 not materialized after attempt"
            assert after.locator("[data-g9-after-attempt-hint]").is_visible(),"H3 still hidden after attempt"
            page.screenshot(path=str(screens/"core2a-after-attempt.png"),full_page=True)
        page.close()
    browser.close()
print("CHROMIUM_FIVE_ROLES_AND_INITIAL_H3_GUARD_PASS")
