#!/usr/bin/env python3
"""Issue #217 M2: native-page HTTP/Chromium observation, never QRT acceptance."""
from __future__ import annotations

import hashlib
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "TEST/imo-research/qrt-d3-successor/m0-adoption.v1.json"
OUT = ROOT / "build/imo182-qrt/d3-successor/m2"
ROLES = ["core1", "core1a", "core1b", "core2a", "core2b"]
WIDTHS = [390, 768, 1280]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


class RootHandler(SimpleHTTPRequestHandler):
    """Serve real build pages and the real site assets under their render links.

    Renderer output in build/ references ../../../css and ../../../js, which
    resolve to /build/css and /build/js. Map those to PUBLIC files without
    rewriting authored HTML or faking their dependencies.
    """

    def translate_path(self, path: str) -> str:
        uri = unquote(urlsplit(path).path)
        for prefix in ("css", "js", "images", "img", "fonts", "assets"):
            marker = f"/build/{prefix}/"
            if uri.startswith(marker):
                rest = uri[len("/build/"):]
                safe = (ROOT / "public" / rest).resolve()
                if safe.is_relative_to((ROOT / "public").resolve()):
                    return str(safe)
        return super().translate_path(path)

    def log_message(self, format: str, *args) -> None:
        pass


def evidence_screenshot(page, location: Path) -> dict:
    location.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(location), full_page=True, animations="disabled")
    return {"file": location.relative_to(ROOT).as_posix(), "sha256": sha256(location)}


def svg_accessibility_observation(page):
    return page.locator("svg[role='img']").evaluate_all("""nodes => nodes.map((node) => ({
        label: node.getAttribute('aria-label') || '',
        title: node.querySelector('title')?.textContent || '',
        desc: node.querySelector('desc')?.textContent || '',
        stage_count: node.querySelectorAll('[data-g9-stage-id]').length
    }))""")


def main() -> None:
    catalog = json.loads(CATALOG.read_text())
    selected = catalog["build_selection"]
    assert_true(len(selected) == 5 and set(selected).isdisjoint(catalog["holds"]),
                "M2 cannot inspect held MODEL/RETRIEVE as adoptable")
    http = ThreadingHTTPServer(("127.0.0.1", 0),
        partial(RootHandler, directory=str(ROOT)))
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{http.server_port}"
    observations = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for demand in selected:
                    root = ROOT / "build/imo182-qrt/d3" / demand
                    receipt = json.loads((root / "render-receipt.json").read_text())
                    assert_true(receipt["gaps"] == [] and len(receipt["pages"]) == 6,
                                f"{demand} not a native six-page receipt")
                    for role in ROLES:
                        for width in WIDTHS:
                            page = browser.new_page(viewport={"width": width, "height": 900},
                                                    device_scale_factor=1)
                            failures = []
                            response_errors = []
                            page_errors = []
                            page.on("requestfailed", lambda request: failures.append(
                                request.url + ": " + str(request.failure)))
                            page.on("response", lambda response: response_errors.append(
                                f"{response.status} {response.url}")
                                if response.status >= 400 and
                                urlsplit(response.url).path.lower().endswith(
                                    (".css", ".js", ".svg", ".png", ".jpg", ".woff", ".woff2"))
                                else None)
                            page.on("pageerror", lambda error: page_errors.append(str(error)))
                            relative = f"/build/imo182-qrt/d3/{demand}/{role}.html"
                            response = page.goto(origin + relative, wait_until="load")
                            assert_true(response is not None and response.status == 200,
                                        f"{demand}/{role}/{width}: HTTP page failure")
                            article = page.locator("article[data-g9-unit]").first
                            assert_true(article.count() == 1 and article.is_visible(),
                                        f"{demand}/{role}/{width}: no learner unit")
                            css_count = page.locator("link[rel='stylesheet']").count()
                            assert_true(css_count >= 2, f"{demand}/{role}: site CSS links absent")
                            sheets = page.evaluate("""() => [...document.querySelectorAll('link[rel=stylesheet]')]
                                .map(e => Boolean(e.sheet))""")
                            assert_true(all(sheets), f"{demand}/{role}/{width}: unloaded CSS")
                            metrics = page.evaluate("""() => ({
                                viewport: innerWidth, document: document.documentElement.scrollWidth,
                                body: document.body.scrollWidth
                            })""")
                            assert_true(metrics["document"] <= width + 2,
                                        f"{demand}/{role}/{width}: outer horizontal overflow {metrics}")
                            svg = svg_accessibility_observation(page)
                            for elem in svg:
                                assert_true(bool(elem["label"] or elem["title"]),
                                            f"{demand}/{role}/{width}: unlabeled SVG")
                            line = {
                                "cell": f"QRT-{demand.upper()}-D3", "role": role.upper(),
                                "viewport": width, "origin": "HTTP_LOCAL_NATIVE_WITH_REAL_PUBLIC_ASSETS",
                                "url_path": relative, "metrics": metrics,
                                "svg_accessibility": svg,
                                "loaded_stylesheets": sheets,
                                "initial_visible_text_sha256": hashlib.sha256(
                                    page.locator("body").inner_text().encode()).hexdigest(),
                                "screenshot": evidence_screenshot(
                                    page, OUT / demand / role / f"{width}-initial.png")
                            }
                            if role in ("core2a", "core1b", "core2b") and width == 390:
                                commit = article.locator("[data-g9-commit]").first
                                text_box = article.locator("[data-g9-attempt]").first
                                assert_true(commit.count() == 1 and text_box.count() == 1,
                                            f"{demand}/{role}: no learner attempt controls")
                                commit.click()
                                assert_true(article.get_attribute("data-attempted") != "1",
                                            f"{demand}/{role}: blank attempt unlocked")
                                line["blank_commit_blocked"] = True
                                if role == "core2a":
                                    ladder = article.locator("[data-g9-ladder]").first
                                    h1 = ladder.locator('[data-g9-rung="1"]').first.inner_text()
                                    next_hint = article.locator("[data-g9-next-rung]").first
                                    assert_true(next_hint.count() == 1,
                                                f"{demand}: cannot reveal H2")
                                    next_hint.click()
                                    h2 = ladder.locator('[data-g9-rung="2"]').first.inner_text()
                                    gated = article.locator("details[data-requires-attempt]").filter(
                                        has=page.locator('summary:text-is("Hint 3 · after your attempt")'))
                                    assert_true(gated.count() == 1, f"{demand}: missing gated H3")
                                    assert_true(not gated.evaluate("(e) => e.open"),
                                                f"{demand}: H3 open before attempt")
                                    assert_true(article.get_attribute("data-attempted") != "1",
                                                f"{demand}: H2 erroneously commits")
                                    line["precommit_h1"] = h1
                                    line["precommit_h2"] = h2
                                    line["h2_screenshot"] = evidence_screenshot(
                                        page, OUT / demand / role / "390-h2-precommit.png")
                                text_box.fill("I wrote an independent representation, considered the decisive bridge and checked the boundary.")
                                commit.click()
                                assert_true(article.get_attribute("data-attempted") == "1",
                                            f"{demand}/{role}: nonblank attempt not recorded")
                                line["nonblank_commit_recorded"] = True
                                if role == "core2a":
                                    gated.locator("summary").click()
                                    h3 = gated.locator("[data-g9-after-attempt-hint]").first
                                    assert_true(h3.is_visible(), f"{demand}: H3 fails to open")
                                    line["postcommit_h3"] = h3.inner_text()
                                    line["h3_screenshot"] = evidence_screenshot(
                                        page, OUT / demand / role / "390-h3-postcommit.png")
                                else:
                                    line["commit_screenshot"] = evidence_screenshot(
                                        page, OUT / demand / role / "390-postcommit.png")
                            assert_true(not failures, f"{demand}/{role}/{width}: request failure {failures}")
                            assert_true(not response_errors,
                                        f"{demand}/{role}/{width}: resources {response_errors}")
                            assert_true(not page_errors,
                                        f"{demand}/{role}/{width}: JS errors {page_errors}")
                            observations.append(line)
                            page.close()
            finally:
                browser.close()
    finally:
        http.shutdown()
        http.server_close()
        thread.join(timeout=5)

    assert_true(len(observations) == 5 * 5 * 3, "expected 75 independently observed viewport pages")
    checked = [x for x in observations if x["role"] == "CORE2A" and x["viewport"] == 390]
    assert_true(len(checked) == 5
                and all(x.get("blank_commit_blocked") and x.get("precommit_h2")
                        and x.get("postcommit_h3") for x in checked),
                "not all five H2/H3 and blank cases observed")
    report = {
        "schema": "imo217-d3-m2-http-chromium/v1", "issue": 217,
        "native_source": "sole-renderer output",
        "hosted_browser": "Chromium/Playwright; real CSS and JS via local HTTP",
        "viewports": WIDTHS,
        "native_role_page_viewports": len(observations),
        "held_unadopted": catalog["holds"], "observations": observations,
        "academic_asks_H1_M3": "PENDING_INDEPENDENT_REVIEW",
        "visual_human_review": "PENDING", "aria_semantic_review": "PENDING",
        "golden_semantics": "PENDING_QUALIFIED_REVIEW",
        "owner_decision_ids": None, "qrt_accepted": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "m2-browser-evidence.v1.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"M2 browser engineering evidence PASS: {len(observations)} viewport-page observations; "
          f"{len(checked)} CORE2A H2/H3/blank chains; semantic signoff PENDING")


if __name__ == "__main__":
    main()
