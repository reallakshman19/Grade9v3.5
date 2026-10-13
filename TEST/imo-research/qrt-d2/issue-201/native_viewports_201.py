"""#201: native-renderer visual evidence at phone, tablet, and desktop widths.

This is source-safe AUTHORED TEST evidence only. Automated geometry and
runtime checks are not a visual-design, cognitive, print, or Owner acceptance.
Do not run on a private/authentic Core2 source without explicit authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

DEMANDS = ("retrieve", "explain", "apply", "model", "represent", "synthesize", "justify")
ROLES = ("core1", "core1a", "core1b", "core2a", "core2b")
WIDTHS = (390, 768, 1280)


def main() -> int:
    args = argparse.ArgumentParser()
    args.add_argument("--render-root", type=Path, required=True)
    args.add_argument("--screenshots", type=Path, required=True)
    options = args.parse_args()
    path = options.screenshots
    path.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "imo-qrt-d2-visual-browser-evidence/v1",
        "source": "AUTHORED_TEST_ONLY",
        "device_widths_px": list(WIDTHS),
        "human_visual_review": "PENDING_INDEPENDENT",
        "owner_approval": "NOT_GRANTED",
        "checks": [],
        "failures": [],
    }
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for demand in DEMANDS:
                receipt_file = options.render_root / demand / "render-receipt.json"
                receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
                assert receipt["gaps"] == [], f"{demand}: nonzero renderer depth gaps"
                for role in ROLES:
                    filepath = options.render_root / demand / f"{role}.html"
                    html_bytes = filepath.read_bytes()
                    assert hashlib.sha256(html_bytes).hexdigest() == receipt["page_sha256"][f"{role}.html"], (
                        f"{demand}:{role}: HTML != renderer receipt"
                    )
                    for width in WIDTHS:
                        ctx = browser.new_context(
                            viewport={"width":width,"height":900},
                            device_scale_factor=1,
                            reduced_motion="reduce",
                        )
                        page = ctx.new_page()
                        js_errors = []
                        page.on("pageerror", lambda exc: js_errors.append(str(exc)))
                        try:
                            page.set_content(html_bytes.decode("utf-8"),wait_until="load")
                            dims = page.evaluate("""() => ({
                              page_width: document.documentElement.scrollWidth,
                              viewport_width: window.innerWidth,
                              content_height: document.documentElement.scrollHeight
                            })""")
                            assert dims["page_width"] <= dims["viewport_width"], (
                                f"HORIZONTAL_OVERFLOW:{demand}:{role}:{width}px:"
                                f'{dims["page_width"]}>{dims["viewport_width"]}'
                            )
                            assert not js_errors, (
                                f"JS_ERROR:{demand}:{role}:{width}px:{js_errors[:2]}"
                            )
                            filename = f"{role}-{width}px-pre-attempt.png"
                            target = path / demand / filename
                            target.parent.mkdir(parents=True,exist_ok=True)
                            page.screenshot(path=str(target),full_page=True,animations="disabled")
                            report["checks"].append({
                                "demand":demand.upper(),
                                "role":role.upper(),
                                "width_px":width,
                                **dims,
                                "js_page_errors":0,
                                "screenshot_path":str(target.relative_to(path.parent)),
                                "screenshot_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
                                "state":"INITIAL_PRE_ATTEMPT",
                                "status":"VIEWPORT_BROWSER_PASS",
                            })
                        except Exception as exc:
                            report["failures"].append({
                                "demand":demand.upper(),"role":role.upper(),
                                "width_px":width,"reason":str(exc),
                            })
                        finally:
                            ctx.close()
        finally:
            browser.close()
    report["expected_checks"] = len(DEMANDS)*len(ROLES)*len(WIDTHS)
    report["observed_checks"] = len(report["checks"])
    report["status"] = ("PASS" if not report["failures"] and
                         report["observed_checks"]==report["expected_checks"] else "FAIL")
    (path.parent / "viewport-evidence.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8"
    )
    print(f'{report["status"]}: {report["observed_checks"]}/{report["expected_checks"]} '
          f'phone/tablet/desktop native page views; failures={len(report["failures"])}')
    for failure in report["failures"][:15]:
        print(failure)
    return 0 if report["status"]=="PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
