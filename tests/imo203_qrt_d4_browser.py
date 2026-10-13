"""Real Chromium D4 learner-attempt checks over native renderer output (not mocked)."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from imo203_d4_w_guard import assert_no_protected_iff

cell=sys.argv[1].lower()
assert cell in ("retrieve","synthesize"),cell
root=Path(f"build/imo203-qrt/d4/{cell}").resolve()
receipt=json.loads((root/"render-receipt.json").read_text())
assert receipt["gaps"]==[],receipt["gaps"]
screens=root/"browser";screens.mkdir(exist_ok=True)
protected={
    "retrieve":["Yes:9,17,33,49","9,17,33,49","criterion for k>=3: odd a≡1","a≡1 mod8",
                "at k>=3 the criterion is1 modulo8","For k>=3 use1 modulo8",
                "the weaker rule is exact only at exponent2"],
    "synthesize":["120384","130284","odd-position and even-position sums both9","odd and even positions each sum9"],
}[cell]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for role in ("core1","core1a","core1b","core2a","core2b"):
        for width in (390,768,1280):
            page=browser.new_page(viewport={"width":width,"height":900})
            page.goto((root/(role+".html")).as_uri())
            assert page.locator("body").inner_text().strip(),(role,width)
            assert page.locator("[data-blueprint-ref]").count()>0,(role,width)
            # Earlier teaching roles must not preview the main/transfer answer,
            # either visibly or through the accessibility projection.
            if role in ("core1","core1a","core1b") and width==1280:
                prior_visible=page.locator("body").inner_text()
                prior_ax=page.locator("body").aria_snapshot()
                if cell == "retrieve":
                    assert_no_protected_iff(prior_visible, role + "-visible")
                    assert_no_protected_iff(prior_ax, role + "-AX")
                for protected_word in protected:
                    assert protected_word not in prior_visible,(cell,role,"VISIBLE_PREVIEW",protected_word)
                    assert protected_word not in prior_ax,(cell,role,"AX_PREVIEW",protected_word)
            page.screenshot(path=str(screens/f"{role}-{width}.png"),full_page=True)
            # Oversized drawings must scroll locally, not make the whole page unusable.
            if role=="core2a" and width==1280:
                html=page.content()
                assert "data-g9-after-attempt-hint" in html
                assert page.locator("[data-requires-attempt]").count()>0
                article=page.locator("article[data-g9-unit]").first
                attempt=page.locator('[data-g9-attempt-box] textarea[data-g9-attempt]').first
                commit=page.locator('[data-g9-attempt-box] button[data-g9-commit]').first
                before=page.locator("body").inner_text()
                accessible=page.locator("body").aria_snapshot()
                if cell == "retrieve":
                    assert_no_protected_iff(before, "core2a-precommit-visible")
                    assert_no_protected_iff(accessible, "core2a-precommit-AX")
                for word in protected:
                    assert word not in before,(cell,"VISIBLE_PREATTEMPT",word)
                    assert word not in accessible,(cell,"AX_PREATTEMPT",word)
                commit.click()
                assert article.get_attribute("data-attempted")!="1","Blank attempt accepted"
                # Explicitly reveal safe H1/H2, without surrendering protected W.
                ladder=page.locator("[data-g9-ladder]").first
                nxt=page.locator("button[data-g9-next-rung]").first
                for _ in range(2):
                    if nxt.count() and nxt.is_enabled():
                        nxt.click()
                current=page.locator("body").inner_text()
                if cell == "retrieve":
                    assert_no_protected_iff(current, "core2a-safe-hints")
                for word in protected:
                    assert word not in current,(cell,"VISIBLE_SAFE_HINT",word)
                attempt.fill("I am checking the defining conditions and keeping the decisive classification or ordering decision for my attempt.")
                commit.click()
                assert article.get_attribute("data-attempted")=="1","Nonblank attempt not recorded"
                payload=page.locator("[data-g9-after-attempt-hint]").first
                assert payload.count()==1
                wrapper=payload.locator("xpath=ancestor::details[1]")
                if wrapper.count() and wrapper.get_attribute('open') is None:
                    wrapper.locator("summary").click()
                assert payload.is_visible(),"Decisive H3 did not unlock after nonblank commitment"
                page.screenshot(path=str(screens/"core2a-after-attempt.png"),full_page=True)
            page.close()
    browser.close()
print("IMO203_D4_NATIVE_BROWSER_PASS",cell)
