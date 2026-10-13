"""Browser smoke of a source-safe ADMIN evidence viewer, not native learner HTML."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "TEST/imo-research/qrt-tiles/reconciliation/index.html"
DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
BANDS = ("D1", "D2", "D3", "D4")


def main():
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for width in (390, 768, 1280):
            page = browser.new_page(viewport={"width": width, "height": 850})
            page.on("pageerror", lambda error: errors.append(str(error)))
            response = page.goto(VIEWER.as_uri(), wait_until="load")
            assert response and response.ok, f"viewer file did not load at {width}px"
            assert page.locator("#matrix button.cell").count() == 28
            for demand in DEMANDS:
                for band in BANDS:
                    cell = f"QRT-{demand}-{band}"
                    button = page.locator('#matrix button[data-cell="' + cell + '"]')
                    button.click()
                    assert button.get_attribute("aria-pressed") == "true"
                    assert cell in page.locator("#selected-title").inner_text()
                    assert page.locator("#hashes tr").count() == 6
                    assert page.locator("#semantic .check").count() == 12
                    assert page.locator('#source-links a').count() == 6
                    assert "0 / 28" in page.locator(".summary").inner_text()
                    assert page.locator("#q003-guard").is_visible() == (cell == "QRT-MODEL-D2")
                    assert "/artifacts/" in page.locator("#source-links a").first.get_attribute("href")
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"outer document overflow at {width}"
            page.close()
        browser.close()
    assert not errors, "JavaScript errors: " + "; ".join(errors)
    print("PASS: 84/84 QRT row selections across 390/768/1280px; each has 6 hashes, 12 academic asks, live pinned ZIP link, Q003 private guard; no JS errors or outer overflow")


if __name__ == "__main__":
    main()
