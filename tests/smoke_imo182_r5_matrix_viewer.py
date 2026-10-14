"""Browser smoke of a source-safe ADMIN evidence viewer, not native learner HTML."""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "TEST/imo-research/qrt-tiles/reconciliation/index.html"
LEDGER = ROOT / "TEST/imo-research/qrt-tiles/reconciliation/r5-01-28-artifact-adoption.v1.json"
REPO = "https://github.com/reallakshman19/Grade9v3.5"
DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
BANDS = ("D1", "D2", "D3", "D4")


def expected_evidence_links(row):
    source_prefix = f"{REPO}/blob/{row['source']['commit']}/"
    urls = [row["artifact"]["url"]]
    if row["artifact"].get("scoped_native_url"):
        urls.append(row["artifact"]["scoped_native_url"])
    urls.extend([
        source_prefix + row["source"]["path"],
        source_prefix + row["manifest"]["path"],
        row["review_url"],
        f"{REPO}/issues/{row['independent_reviewer_nomination_issue']}",
    ])
    if row.get("ai_content_review"):
        urls.append(row["ai_content_review"]["source"])
    if row.get("source_supersession_watch"):
        urls.append(row["source_supersession_watch"]["successor_pr_url"])
    urls.extend([
        f"{REPO}/issues/{row['issue']}",
        f"{REPO}/blob/{row['frozen_golden']['commit']}/golden/units/{row['frozen_golden']['id']}/GOLDEN.md",
    ])
    return urls


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    records = {row["cell_id"]: row for row in ledger["rows"]}
    assert len(records) == 28
    script = re.search(
        r'<script id="qrt-evidence" type="application/json">(.+?)</script>',
        VIEWER.read_text(encoding="utf-8"), re.S
    )
    assert script, "missing source-safe HTML review evidence data"
    projections = {r["id"]: r for r in json.loads(script.group(1))}
    assert set(projections) == set(records)
    for cell, r in records.items():
        v = projections[cell]
        assert v["artifact"]["native_html_sha256"] == r["artifact"]["native_html_sha256"]
        assert v["artifact"]["url"] == r["artifact"]["url"]
        assert v["source"] == r["source"]
        assert v["manifest"] == r["manifest"]
        assert v["classification_hold"] == r["critical_educational_review_hold"]
        assert v.get("d4_retrieve_leak_repair_provenance") == r.get("d4_retrieve_leak_repair_provenance")
        assert v["review_url"].startswith(REPO + "/blob/")
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
                    row = projections[cell]
                    actual = page.locator("#source-links a").evaluate_all(
                        "(items) => items.map(a => a.getAttribute('href'))"
                    )
                    assert actual == expected_evidence_links(row), (
                        f"{cell} at {width}px: evidence links differ from pinned ledger: "
                        f"actual={actual}, expected={expected_evidence_links(row)}"
                    )
                    assert page.locator("#hashes tr td:nth-child(2)").all_text_contents() == [
                        row["artifact"]["native_html_sha256"][name] for name in
                        ("core1.html", "core1a.html", "core1b.html", "core2a.html", "core2b.html", "index.html")
                    ]
                    assert page.locator("#selected-description").inner_text().startswith(
                        "Technical artifact verified;" if row["classification_hold"] else
                        "Technical artifact pinned."
                    )
                    if row.get("source_supersession_watch"):
                        assert "two-field source" in page.locator("#blockers").inner_text()
                    if row.get("ai_content_review"):
                        assert "qualification PENDING" in page.locator("#overview").inner_text()
                    assert "0 / 28" in page.locator(".summary").inner_text()
                    assert page.locator("#q003-guard").is_visible() == (cell == "QRT-MODEL-D2")
                    assert "/artifacts/" in page.locator("#source-links a").first.get_attribute("href")
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"outer document overflow at {width}"
            page.close()
        browser.close()
    assert not errors, "JavaScript errors: " + "; ".join(errors)
    print("PASS: 84/84 QRT row selections across 390/768/1280px; each has 6 exact ledger hashes, 12 academic asks, all dynamic source/reviewer/ZIP links, Q003 private guard; no JS errors or outer overflow")


if __name__ == "__main__":
    main()
