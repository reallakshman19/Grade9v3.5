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
            # Owner v3.1 O1: this is the actual registered Core1A learner
            # page and independent exit, not a separate hand-composed preview.
            if cell == "retrieve" and role == "core1a" and width == 1280:
                assert page.locator('body[data-blueprint-ref="BP-CORE1A-CONSTRUCTION@1.8.0"]').count() == 1
                assert page.locator('[data-g9-component="CONSTRUCTION_STEPS"]').count() >= 1
                assert page.locator('[data-g9-component="STAGED_VISUAL"]').count() >= 1
                assert page.locator('[data-g9-component="EXIT_RECALL"]').count() == 1
                exit_card = page.locator('[data-g9-component="EXIT_RECALL"]').first
                response = exit_card.locator('textarea[data-g9-attempt]').first
                commit_exit = exit_card.locator('button[data-g9-commit]').first
                locked_answer = exit_card.locator('details[data-requires-attempt]').first
                assert locked_answer.count() == 1
                answer_payload = locked_answer.locator('[data-g9-payload-slot]').first
                # The collapsed "Model answer" summary is a valid visible control;
                # it is NOT a disclosure. Check actual contents, not is_visible().
                assert locked_answer.get_attribute("open") is None
                assert not answer_payload.text_content().strip(), "Core1A exit payload existed before attempt"
                commit_exit.click()
                assert not answer_payload.text_content().strip(), "Core1A blank exit hydrated answer"
                assert locked_answer.get_attribute("open") is None, "Blank exit opened answer"
                response.fill("Odd squares modulo16 are 1 or 9; 9 has an odd root and 5 does not. Both reduce to1 modulo4.")
                commit_exit.click()
                assert "9 is an odd square modulo16" in answer_payload.text_content(), "Nonblank exit did not hydrate answer"
                assert locked_answer.get_attribute("open") is None, "Core1A answer opened without explicit choice"
                locked_answer.locator("summary").click()
                assert locked_answer.get_attribute("open") is not None, "Model answer not disclosed on learner request"
                assert "9 is an odd square modulo16" in locked_answer.inner_text()
                page.screenshot(path=str(screens/"core1a-after-attempt.png"),full_page=True)
            # Owner v3.1 O1: preserve Core1B's already-done blueprint/golden
            # reconstruction with independent main and boundary attempt gates.
            if cell == "retrieve" and role == "core1b" and width == 1280:
                assert page.locator('body[data-blueprint-ref="BP-CORE1B-RECONSTRUCTION@1.1.0"]').count() == 1
                slots = page.locator('section.blueprint-slot')
                assert slots.count() == 3
                assert [slots.nth(i).get_attribute("data-blueprint-slot") for i in range(3)] == [
                    "identity", "attempt", "reconstruction"
                ]
                first = page.locator('[data-g9-attempt-box]:not([data-g9-attempt-stage])').first
                reconstruct = page.locator(
                    'details[data-requires-attempt][data-g9-payload-ref="CORE1B-MIC-D4-RETRIEVE-reconstruct"]'
                )
                assert reconstruct.count() == 1
                main_payload = reconstruct.locator('[data-g9-payload-slot]')
                assert not main_payload.text_content().strip()
                first.locator('button[data-g9-commit]').click()
                assert not main_payload.text_content().strip(), "Blank reconstruction attempt hydrated answer"
                first.locator('textarea[data-g9-attempt]').fill(
                    "Odd squares are 1 modulo8, so 5 is not an odd square there; modulo4, 5 is 1."
                )
                first.locator('button[data-g9-commit]').click()
                assert "every odd square equals1 modulo8" in main_payload.inner_text().casefold()
                assert reconstruct.get_attribute("open") is None
                reconstruct.locator("summary").click()
                assert reconstruct.get_attribute("open") is not None

                boundary = page.locator('[data-g9-attempt-box][data-g9-attempt-stage="boundary"]')
                boundary_answer = page.locator(
                    'details[data-requires-attempt][data-g9-attempt-stage="boundary"]'
                )
                boundary_payload = boundary_answer.locator('[data-g9-payload-slot]')
                assert boundary.count() == 1 and boundary_answer.count() == 1
                assert not boundary_payload.text_content().strip()
                boundary.locator('button[data-g9-commit]').click()
                assert not boundary_payload.text_content().strip(), "Blank boundary attempt hydrated answer"
                boundary.locator('textarea[data-g9-attempt]').fill(
                    "a=5 is an odd square modulo4; it fails modulo8 and modulo16."
                )
                boundary.locator('button[data-g9-commit]').click()
                assert "modulo4" in boundary_payload.inner_text()
                assert "modulo16" in boundary_payload.inner_text()
                assert boundary_answer.get_attribute("open") is None
                boundary_answer.locator("summary").click()
                assert boundary_answer.get_attribute("open") is not None
                page.screenshot(path=str(screens/"core1b-after-boundary-attempt.png"), full_page=True)
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
