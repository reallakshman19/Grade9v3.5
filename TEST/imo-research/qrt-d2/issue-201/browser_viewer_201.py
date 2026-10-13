"""Issue #201: actual Chromium smoke test for the source-safe 7x4 review viewer."""
from pathlib import Path
import json
import re
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[4]
HTML = ROOT / "TEST/imo-research/qrt-d2/issue-201/index.html"
LEDGER = HTML.with_name("evidence.v1.json")
EXPECTED = ("RETRIEVE","EXPLAIN","APPLY","MODEL","REPRESENT","SYNTHESIZE","JUSTIFY")

def main():
    # The self-contained HTML embeds rows for offline/file:// review. Enforce that
    # those rows match the canonical ledger whenever it changes.
    html_text = HTML.read_text(encoding="utf-8")
    match = re.search(r"const rows=(.*?);\s*const bands=", html_text, flags=re.DOTALL)
    assert match, "VIEWER_MISSING_EMBEDDED_LEDGER"
    embedded = json.loads(match.group(1))
    canonical = json.loads(LEDGER.read_text(encoding="utf-8"))["rows"]
    assert embedded == canonical, "VIEWER_EMBEDDED_LEDGER_STALE"
    errors = []
    output = {"schema": "imo-qrt-d2-viewer-browser-smoke/v1", "viewer": str(HTML.relative_to(ROOT)),
              "checked": [], "status": "FAIL"}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(HTML.as_uri(), wait_until="load")
            assert page.locator("#matrix tr").count() == 7, "NOT_SEVEN_DEMAND_ROWS"
            assert page.locator("button.tile").count() == 7, "NOT_SEVEN_D2_BUTTONS"
            assert page.locator("#matrix a[href*='/issues/']").count() == 21, "MISSING_OTHER_BAND_ISSUE_LINKS"
            for demand in EXPECTED:
                button=page.get_by_role("button",name=f"QRT-{demand}-D2")
                button.click()
                assert page.locator("#cell").inner_text() == f"QRT-{demand}-D2"
                assert button.get_attribute("aria-pressed") == "true"
                assert page.locator("#five-roles tr").count() == 5, "MISSING_ROLE_LOCKS"
                assert page.locator("#twelve-checks tr").count() == 12, "MISSING_12_REVIEW_ASKS"
                assert "PENDING" in page.locator("#owner").inner_text()
                links = page.locator("#links a")
                assert links.count() >= 8, "MISSING_EVIDENCE_OR_ACADEMIC_REVIEW_LINKS"
                review_id = 211 if demand in ("RETRIEVE", "MODEL") else 214
                packet = ("ACADEMIC-REVIEW-REQUEST.md" if review_id == 211
                          else "OTHER-FIVE-ACADEMIC-REVIEW.md")
                assert links.filter(has_text=f"Qualified academic review request · #{review_id}").count() == 1, (
                    f"WRONG_QUALIFIED_REVIEW_ISSUE:{demand}:{review_id}"
                )
                assert page.locator(f'#links a[href$="/issues/{review_id}"]').count() == 1, (
                    f"MISSING_UNIQUE_ACADEMIC_ISSUE_TARGET:{demand}"
                )
                assert page.locator(f'#links a[href$="{packet}"]').count() == 1, (
                    f"ACADEMIC_PACKET_NOT_LINKED:{demand}:{packet}"
                )
                assert page.locator('#links a[href*="/actions/runs/38426896089/artifacts/11829196580"]').count() == 1, (
                    f"LATEST_VERIFIED_ARTIFACT_NOT_LINKED:{demand}"
                )
                assert "AUTHORED TEST" in page.locator("#rights").inner_text()
                output["checked"].append(f"QRT-{demand}-D2")
            assert not errors, f"JS_ERRORS:{errors}"
            assert not page.evaluate("document.documentElement.scrollWidth > window.innerWidth"), "VIEWER_HORIZONTAL_OVERFLOW_390PX"
            output["status"] = "PASS"
            output["other_band_links"]=21
            output["semantics_per_tile"]=12
            output["role_locks_per_tile"]=5
        finally:
            browser.close()
    report = ROOT / "build/imo201/d2/viewer-smoke.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
