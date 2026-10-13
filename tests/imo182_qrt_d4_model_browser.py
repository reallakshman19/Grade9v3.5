"""Real Chromium evidence from the sole registered renderer, MODEL-D4 only."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

folder=Path("build/imo182-qrt/d4/model").resolve()
receipt=json.loads((folder/"render-receipt.json").read_text())
assert receipt["gaps"]==[],receipt["gaps"]
screens=folder/"browser";screens.mkdir(exist_ok=True)
prior_role_cues={}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for role in ("core1","core1a","core1b","core2a","core2b"):
        page=browser.new_page(viewport={"width":1280,"height":900})
        page.goto((folder/(role+".html")).as_uri())
        assert page.locator("body").inner_text().strip(),role
        assert page.locator("[data-blueprint-ref]").count()>0,role
        page.screenshot(path=str(screens/(role+".png")),full_page=True)
        if role in ("core1a", "core1b"):
            text=page.locator("body").inner_text()
            ax=page.locator("body").aria_snapshot()
            phrases={
                "core1a": ("reserve a count c", "sealed empty courtyard"),
                "core1b": ("unreachable center", "corrected model"),
            }[role]
            prior_role_cues[role]={
                "visible_cues":[phrase for phrase in phrases if phrase in text.lower()],
                "ax_cues":[phrase for phrase in phrases if phrase in ax.lower()],
                "academic_verdict":"PENDING_QUALIFIED_REVIEW",
            }

        if role=="core1b":
            assert page.locator('[data-g9-attempt-stage="boundary"] textarea[data-g9-attempt]').count()==1
            assert page.locator('details[data-g9-attempt-stage="boundary"][data-requires-attempt]').count()==1
        if role=="core2a":
            html=page.content()
            assert 'data-g9-payload="CORE2A-Q-D4-MODEL-MAIN-after-attempt-hint-3"' in html
            assert "data-g9-after-attempt-hint" in html
            assert page.locator("[data-requires-attempt]").count()>0
            assert not any(loc.is_visible() for loc in page.get_by_text("Only AFTER a written attempt",exact=False).all()),"H3 visible preattempt"
            # Verify actual pre-commit H2 and its accessibility projection, not only source JSON.
            ladder=page.locator("[data-g9-ladder]").first
            assert "What quantity does that subtraction count" not in ladder.inner_text()
            page.locator("button[data-g9-next-rung]").first.click()
            assert "What quantity does that subtraction count" in ladder.inner_text()
            visible=page.locator("body").inner_text()
            exposed=page.locator("body").aria_snapshot()
            for text in (visible,exposed):
                assert "Are all remaining unshared edges necessarily reachable?" not in text
                assert "A=4n−2e−c" not in text
            assert "What quantity does that subtraction count" in exposed
            ladder_ax=ladder.aria_snapshot().casefold()
            for cue in ("courtyard", "inaccessible", "sealed", "cavity",
                        "inner void", "subtract c", "hole correction"):
                assert cue not in ladder.inner_text().casefold(),("H2_WORDING_LEAK",cue)
                assert cue not in ladder_ax,("H2_AX_LEAK",cue)
            page.locator('[data-g9-attempt-box] button[data-g9-commit]').first.click()
            article=page.locator("article[data-g9-unit]").first
            assert article.get_attribute("data-attempted")!="1","Blank attempt erroneously accepted"
            attempt=page.locator('[data-g9-attempt-box] textarea[data-g9-attempt]').first
            attempt.fill("I counted the occupied tables and the full shared seams. I need a model that separates unshared edges from edges facing an inaccessible courtyard.")
            page.locator('[data-g9-attempt-box] button[data-g9-commit]').first.click()
            assert article.get_attribute("data-attempted")=="1","Committed attempt missing"
            after=page.locator('details[data-g9-payload-ref="CORE2A-Q-D4-MODEL-MAIN-after-attempt-hint-3"]')
            assert after.count()==1
            after.locator("summary").click()
            assert after.locator("[data-g9-after-attempt-hint]").count()==1
            assert after.locator("[data-g9-after-attempt-hint]").is_visible()
            page.screenshot(path=str(screens/"core2a-after-attempt.png"),full_page=True)
        page.close()
    browser.close()
(screens/"prior-role-w-cue-risk.json").write_text(json.dumps({
    "cell":"QRT-MODEL-D4", "source":"actual Chromium native five-role output",
    "status":"OBSERVED_CUES_PENDING_QUALIFIED_ACADEMIC_JUDGMENT",
    "roles":prior_role_cues, "academic_verdict":None, "owner_decision_id":None,
},indent=2))
print("MODEL_D4_CHROMIUM_FIVE_ROLES_H3_BOUNDARY_PASS")
