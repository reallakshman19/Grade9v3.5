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
import tempfile
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading

from playwright.sync_api import sync_playwright

DEMANDS = ("retrieve", "explain", "apply", "model", "represent", "synthesize", "justify")
ROLES = ("core1", "core1a", "core1b", "core2a", "core2b")
WIDTHS = (390, 768, 1280)


@contextmanager
def loopback_site(directory: Path):
    """Exercise the native pages with real HTTP origins and relative assets."""
    class QuietHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


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
        "browser_source": "LOOPBACK_HTTP_WITH_ACTUAL_DOCS_CSS_JS",
        "required_stylesheets": ["modern-learner.css", "tablet-12-7.css"],
        "required_scripts": ["display-controls.js", "site-header.js"],
        "human_visual_review": "PENDING_INDEPENDENT",
        "owner_approval": "NOT_GRANTED",
        "checks": [],
        "failures": [],
    }
    # Generated role HTML contains ../../../css and ../../../js asset links.
    # Recreate its production-relative depth under a temporary docs/ tree;
    # Real loopback HTTP avoids both about:blank and file:// origin artifacts.
    with tempfile.TemporaryDirectory(prefix="imo201-site-assets-") as scratch:
        site_docs = Path(scratch) / "docs"
        site_docs.mkdir()
        for directory in ("css", "js"):
            original = (Path(__file__).resolve().parents[4] / "docs" / directory).resolve()
            assert original.is_dir(), f"REQUIRED_PRODUCTION_ASSET_DIR_MISSING:{original}"
            (site_docs / directory).symlink_to(original, target_is_directory=True)
        with loopback_site(site_docs) as site_origin:
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
                            destination = site_docs / "test" / "qrt-d2" / demand / f"{role}.html"
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            destination.write_bytes(html_bytes)
                            for width in WIDTHS:
                                ctx = browser.new_context(
                                    viewport={"width":width,"height":900},
                                    device_scale_factor=1,
                                    reduced_motion="reduce",
                                )
                                page = ctx.new_page()
                                js_errors = []
                                request_failures = []
                                status_failures = []
                                page.on("pageerror", lambda exc: js_errors.append(str(exc)))
                                page.on("requestfailed", lambda req: request_failures.append(req.url))
                                page.on("response", lambda response: status_failures.append(
                                    f"{response.status}:{response.url}"
                                ) if response.status >= 400 and response.url.startswith(site_origin) else None)
                                try:
                                    page.goto(
                                        site_origin + "/" + destination.relative_to(site_docs).as_posix(),
                                        wait_until="load",
                                    )
                                    assets = page.evaluate("""() => ({
                                      css: [...document.querySelectorAll('link[rel="stylesheet"]')]
                                        .map(link => ({href:link.getAttribute('href'), loaded:!!link.sheet})),
                                      js: [...document.querySelectorAll('script[src]')]
                                        .map(script => script.getAttribute('src'))
                                    })""")
                                    assert len(assets["css"]) >= 2, (
                                        f"NOT_ENOUGH_SITE_STYLESHEETS:{demand}:{role}"
                                    )
                                    for stylesheet in ("modern-learner.css", "tablet-12-7.css"):
                                        matches = [link for link in assets["css"]
                                                   if link["href"].endswith(stylesheet)]
                                        assert len(matches) == 1 and matches[0]["loaded"], (
                                            f"STYLESHEET_NOT_LOADED:{demand}:{role}:{stylesheet}"
                                        )
                                    for script in ("display-controls.js", "site-header.js"):
                                        assert sum(src.endswith(script) for src in assets["js"]) == 1, (
                                            f"REQUIRED_SCRIPT_MISSING:{demand}:{role}:{script}"
                                        )
                                    assert not status_failures, (
                                        f"ASSET_HTTP_ERROR:{demand}:{role}:{status_failures[:3]}"
                                    )
                                    assert not request_failures, (
                                        f"ASSET_REQUEST_FAILED:{demand}:{role}:{request_failures[:3]}"
                                    )
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
                                    target.parent.mkdir(parents=True, exist_ok=True)
                                    page.screenshot(path=str(target), full_page=True, animations="disabled")
                                    report["checks"].append({
                                        "demand":demand.upper(),
                                        "role":role.upper(),
                                        "width_px":width,
                                        **dims,
                                        "js_page_errors":0,
                                        "site_assets": assets,
                                        "asset_http_errors": 0,
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
