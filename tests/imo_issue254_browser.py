"""Real Chromium smoke test of the Issue 254 source research portal (non-validator).

Run: python tests/imo_issue254_browser.py
Requires: pip install playwright; python -m playwright install chromium
"""
from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "public/test/imo-grade9/core2.html"
OUT = ROOT / "TEST/imo-qrt-repair/browser-evidence"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    observations = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        for width in (320, 390, 768, 1280):
            page = browser.new_page(viewport={"width": width, "height": 900})
            errors = []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.goto(HTML.as_uri(), wait_until="domcontentloaded")
            page.locator(".qb-question").first.wait_for()
            cards = page.locator(".qb-question")
            assert cards.count() == 260, f"{width}: missing questions"
            for index in (0, 259):
                card = cards.nth(index)
                qid = card.get_attribute("id")[2:]
                solution = page.locator("#sol-disc-" + qid)
                diagnosis = page.locator("#diag-disc-" + qid)
                button = page.locator("#commit-" + qid)
                attempt = page.locator("#att-" + qid)
                assert solution.get_attribute("hidden") is not None
                assert diagnosis.get_attribute("hidden") is not None
                assert not solution.is_visible()
                assert not diagnosis.is_visible()
                first_hint = page.locator("#hint1-" + qid)
                second_hint = page.locator("#hint2-" + qid)
                assert first_hint.get_attribute("hidden") is None, qid
                assert second_hint.get_attribute("hidden") is not None, qid
                assert not second_hint.is_visible(), qid
                card.scroll_into_view_if_needed()
                # The ladder itself starts closed: first open the outer disclosure,
                # then confirm Tier 1 is available while Tier 2 is still protected.
                card.locator(".qb-disclosure").first.locator("summary").first.click()
                assert first_hint.is_visible(), qid
                assert not second_hint.is_visible(), qid
                first_hint.locator("summary").click()
                second_hint.wait_for(state="visible")
                assert not solution.is_visible(), qid
                button.click()
                assert not solution.is_visible(), f"{qid} leaked on empty commitment"
                assert attempt.get_attribute("aria-invalid") == "true"
                attempt.fill("I choose option A; I need to compare the given relationships.")
                button.click()
                assert solution.is_visible() and diagnosis.is_visible(), qid
                assert solution.get_attribute("open") is not None, qid
                assert attempt.get_attribute("readonly") is not None, qid
                assert button.get_attribute("aria-expanded") == "true"
                summary = solution.locator("summary")
                assert summary.evaluate("(e) => e === document.activeElement"), qid
                summary.press("Enter")
                assert solution.get_attribute("open") is None, qid
                summary.press("Enter")
                assert solution.get_attribute("open") is not None, qid
            # Navigation and filter should remain functional with committed responses.
            page.evaluate("switchTab('core1-all')")
            assert page.locator("#tab-core1-all").evaluate("(e) => e.classList.contains('active')")
            page.evaluate("switchTab('core2')")
            # Record viewport overflow, KaTeX rendering and console failures rather than concealing them.
            katex = page.locator(".katex").count()
            overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            offenders = page.evaluate("""() => Array.from(document.querySelectorAll('body *'))
              .filter(el => {
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.right > innerWidth + 2 &&
                       getComputedStyle(el).display !== 'none';
              }).map(el => {
                const r = el.getBoundingClientRect();
                return {tag: el.tagName, cls: String(el.className).slice(0, 70),
                        id: el.id, right: Math.round(r.right), width: Math.round(r.width)};
              }).sort((a, b) => b.right - a.right).slice(0, 12)""")
            layout = page.evaluate("""() => {
              const root = document.documentElement;
              const roots = ['.g9-shell', '.shell-inner', 'main.container', '#tab-core2',
                '.qb-filter-panel', '.qb-question', '.qb-stem-box', '.qb-support-container',
                '.qb-disclosure', '.qb-disclosure summary', '.qb-options-grid'];
              const boxes = roots.map(sel => {
                const el = document.querySelector(sel);
                if (!el) return {selector: sel, found: false};
                const b = el.getBoundingClientRect();
                return {selector: sel, right: Math.round(b.right), left: Math.round(b.left),
                  width: Math.round(b.width), scroll: el.scrollWidth, client: el.clientWidth,
                  overflowX: getComputedStyle(el).overflowX};
              });
              const spill = Array.from(document.querySelectorAll('body *'))
                .filter(el => !(el instanceof SVGElement) && !el.closest('.katex'))
                .map(el => {const b=el.getBoundingClientRect();
                  return {el, b, css:getComputedStyle(el)};})
                .filter(x => x.b.width > 0 && x.b.right > innerWidth + 3 &&
                   x.css.display !== 'none' && x.css.visibility !== 'hidden')
                .sort((a,b) => a.b.width-b.b.width).slice(0,30)
                .map(x => ({tag:x.el.tagName,id:x.el.id,cls:String(x.el.className).slice(0,90),
                   right:Math.round(x.b.right),width:Math.round(x.b.width),
                   overflowX:x.css.overflowX,whiteSpace:x.css.whiteSpace}));
              return {windowWidth:innerWidth,rootScroll:root.scrollWidth,
                rootClient:root.clientWidth,bodyScroll:document.body.scrollWidth,
                boxes,spill};
            }""")
            print("LAYOUT " + json.dumps({"width": width, "layout": layout}), flush=True)
            print("DIAGNOSTIC " + json.dumps({"width": width, "katex": katex,
                "overflow": overflow, "offenders": offenders}), flush=True)
            assert katex > 0, f"{width}: math was not rendered by KaTeX"
            # Genuine narrow-screen containment: retain local scrolling for long
            # formulae and the tab strip, but forbid document-wide overflow.
            assert not overflow, f"{width}: document overflow: {layout}"
            page.locator(".qb-question").first.scroll_into_view_if_needed()
            page.screenshot(path=str(OUT / f"research-attempt-{width}.png"), full_page=False)
            observations.append({"viewport": width, "question_count": cards.count(),
                "first_last_commit": "PASS", "keyboard": "PASS",
                "navigation": "PASS", "katex_nodes": katex,
                "horizontal_overflow": overflow, "page_errors": errors})
            assert not errors, f"{width}: {errors}"
            page.reload(wait_until="domcontentloaded")
            first_qid = cards.first.get_attribute("id")[2:]
            assert not page.locator("#sol-disc-" + first_qid).is_visible(), "reload leakage"
            page.close()
        browser.close()
    print(json.dumps({"scope": "RESEARCH_HTML_ONLY", "status": "PASS",
        "observations": observations}, indent=2))
    (OUT / "browser-evidence.json").write_text(json.dumps(observations, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
