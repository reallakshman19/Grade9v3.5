#!/usr/bin/env python3
"""Issue 182 O1: five genuine EXPLAIN-D3 Core pages vs frozen Owner golden.

This verifier is run ON a pinned D3 author checkout, not in the integration
branch (which deliberately has no D3 source or manifest). It never renders
a learner page itself: CI invokes Shared/tools/render_core.py first.

It tests byte/provenance truth, registered blueprint structure, main/transfer
math and actual browser behavior for previously unbenchmarked Core1/Core2A.
It archives remaining educational and accessibility defects honestly; it
DOES NOT award QRT, Owner, rights, or visual/pedagogical approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import threading
from functools import partial
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

SOURCE_REF = "dfe4bb6766b87132423b01ffaa914ade1145424f"
SOURCE_BLOB = "32fad7e3be4f806e43e5f44942434842ad10c25a"
MANIFEST_BLOB = "2c74ef14eff21a756e5bf3c6b87f3f9a0447d04e"
REGISTRY_BLOB = "591ba061b8771c30fdffc4506aa720ca9ba89335"
LOCK_BLOB = "888678554c41257e6d96c802f0009983ccbb5328"
ROLES = ("core1", "core1a", "core1b", "core2a", "core2b")
EXPECTED_BLUEPRINTS = {
    "core1": "BP-CORE1-ORIENTATION@1.1.0",
    "core1a": "BP-CORE1A-CONSTRUCTION@1.8.0",
    "core1b": "BP-CORE1B-RECONSTRUCTION@1.1.0",
    "core2a": "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
    "core2b": "BP-CORE2B-TRANSFER@1.1.0",
}
TECHNIQUES = {
    "core1": ("T14",),
    "core1a": ("T02", "T03", "T11"),
    "core1b": ("T06", "T10", "T12"),
    "core2a": ("T05", "T07"),
    "core2b": ("T08", "T09"),
}

def ensure(value, message: str):
    if not value:
        raise AssertionError(message)

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def gitblob(root: Path, path: Path):
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(root))],
        text=True, cwd=root,
    ).strip()

class NativeStructure(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slots = []
        self.blocks = []
        self.components = []
        self.roles = []
        self.blueprints = []
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        for key, collector in (
            ("data-blueprint-slot", self.slots),
            ("data-g9-block", self.blocks),
            ("data-g9-component", self.components),
            ("data-g9-role", self.roles),
            ("data-blueprint-ref", self.blueprints),
        ):
            if data.get(key):
                collector.append(data[key])

def structure(path: Path):
    obj = NativeStructure()
    obj.feed(path.read_text(encoding="utf-8"))
    return obj

def role_inventory(root: Path):
    source = root / "TEST/imo-research/qrt-d3/explain.v1.json"
    manifest = root / "TEST/products/imo182-qrt-d3-explain.manifest.json"
    registry = root / "Shared/web/interactive-page-blueprints.v1.json"
    lock_path = root / "golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json"
    fixture = lock_path.parent
    output = root / "build/imo182-qrt/d3/explain"
    receipt = load(output / "render-receipt.json")
    lock = load(lock_path)
    product = load(manifest)
    package = load(source)
    reg = load(registry)

    for path, expected in (
        (source, SOURCE_BLOB), (manifest, MANIFEST_BLOB),
        (registry, REGISTRY_BLOB), (lock_path, LOCK_BLOB)
    ):
        ensure(gitblob(root, path) == expected,
               f"pinned source/manifest/blueprint/golden changed: {path}")
    ensure(subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip() == SOURCE_REF, "D3 checkout is not the exact pinned source commit")
    ensure(reg["registry_version"] == "1.17.0", "blueprint registry version drift")
    ensure(product["subject"] == "TEST"
           and product["selection"]["core2"] == []
           and set(product["output_roles"]) == {x.upper() for x in ROLES},
           "unsafe authentic Core2 or wrong five-role manifest")
    ensure(package["extensions"]["grade9v3:qrt_admitted"] is False,
           "author-created TEST unexpectedly promoted into QRT")
    ensure(receipt["renderer"] == "render_core/2"
           and receipt["mode"] == "PAGES"
           and receipt["gaps"] == []
           and receipt["held_to"] == "REFERENCE",
           "not zero-gap sole-renderer reference evidence")
    ensure(lock["fixture_id"] == "G-IMO-G9-FIVE-CORE-20261012"
           and lock["snapshot_page_count"] == 5, "wrong Owner exact fixture")

    known = {r["id"]: r for r in reg["blueprints"]}
    results = []
    for role in ROLES:
        path = output / (role + ".html")
        frozen = next(x for x in lock["snapshots"] if x["role"] == role.upper())
        immutable = fixture / frozen["path"]
        ensure(sha(immutable) == frozen["sha256"],
               f"frozen Owner {role} HTML bytes no longer match snapshot-lock")
        ensure(sha(path) == receipt["page_sha256"][role + ".html"],
               f"{role}: generated HTML not pinned to real renderer receipt")
        current, golden = structure(path), structure(immutable)
        expected = EXPECTED_BLUEPRINTS[role]
        bp_id, version = expected.split("@")
        bp = known[bp_id]
        ensure(bp["version"] == version and bp["status"] == "ACTIVE"
               and bp["core_roles"] == [role.upper()], f"{role}: inactive registered BP")
        ensure(current.blueprints == golden.blueprints == [expected]
               and current.roles[:1] == golden.roles[:1] == [role.upper()],
               f"{role}: golden and generated native BP/role differ")
        for key in ("slots", "blocks"):
            ensure(getattr(current, key) == getattr(golden, key)
                   and len(getattr(current, key)) > 0,
                   f"{role}: actual registered instructional {key} diverge from Owner technique")
        results.append({
            "role": role.upper(),
            "blueprint": expected,
            "native_sha256": sha(path),
            "receipt_sha256_match": True,
            "immutable_original_golden_sha256": frozen["sha256"],
            "original_frozen_sha256_match": True,
            "comparison_kind": "CROSS_QUESTION_REGISTERED_ROLE_ORDER_NOT_HTML_BYTE_PARITY",
            "slot_order": current.slots,
            "block_order": current.blocks,
            "technique_ids_to_review": list(TECHNIQUES[role]),
            "structural_comparison": "MATCH",
            "educational_golden_semantics": "PENDING_INDEPENDENT_REVIEW",
        })
    index = output / "index.html"
    ensure(index.exists() and sha(index) == receipt["page_sha256"]["index.html"],
           "actual sixth native index not tied to renderer receipt")
    return results, output, receipt, package, product

def math_witness():
    main = []
    transfer = []
    for x in (-1, 4):
        lhs = math.sqrt(x + 5)
        main.append({"x": x, "lhs": lhs, "rhs": x-1,
                     "holds": math.isclose(lhs, x-1)})
        transfer.append({"t": x, "lhs": lhs, "rhs": abs(x-1),
                         "holds": math.isclose(lhs, abs(x-1))})
    ensure([x["holds"] for x in main] == [False, True],
           "signed-root original discriminant wrong")
    ensure([x["holds"] for x in transfer] == [True, True],
           "absolute-root changed-case discriminant wrong")
    # Both equations square to (x-4)(x+1)=0 and no additional reals solve.
    return {"original_signed": main, "absolute_transfer": transfer,
            "necessity_factorization": "(x-4)(x+1)=0",
            "review_scope": "MATH_CHECK_ONLY_NOT_SIGNED_QRT"}

def browser_roles(root: Path, out: Path):
    successor = root / "TEST/imo-research/qrt-d3-successor"
    import sys
    sys.path.insert(0, str(successor))
    from browser_stage_217 import RootHandler

    http = ThreadingHTTPServer(("127.0.0.1", 0),
                               partial(RootHandler, directory=str(root)))
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    observations = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for role in ("core1", "core2a"):
                    for width in (390, 768, 1280):
                        page = browser.new_page(viewport={"width": width, "height": 900})
                        failures, js_errors = [], []
                        page.on("requestfailed", lambda req: failures.append(req.url))
                        page.on("pageerror", lambda exc: js_errors.append(str(exc)))
                        page.on("response", lambda resp: failures.append(f"{resp.status} {resp.url}")
                                if resp.status >= 400 and urlsplit(resp.url).path.lower().endswith(
                                    (".css", ".js", ".svg", ".png", ".jpg", ".woff", ".woff2"))
                                else None)
                        route = f"/build/imo182-qrt/d3/explain/{role}.html"
                        response = page.goto(
                            f"http://127.0.0.1:{http.server_port}{route}", wait_until="load")
                        ensure(response is not None and response.status == 200,
                               f"{role}/{width}: native learner HTTP route unavailable")
                        ensure(page.locator(f"html[data-g9-role='{role.upper()}']").count() == 1,
                               f"{role}: not actual registered Core role")
                        ensure(page.locator("body[data-blueprint-ref]").get_attribute(
                            "data-blueprint-ref") == EXPECTED_BLUEPRINTS[role],
                            f"{role}: not live registered blueprint")
                        article = page.locator("article[data-g9-unit]").first
                        ensure(article.is_visible(), f"{role}: actual learner unit absent")
                        css = page.evaluate("""() => [...document.querySelectorAll(
                              'link[rel=stylesheet]')].map(x => Boolean(x.sheet))""")
                        ensure(len(css) >= 2 and all(css),
                               f"{role}/{width}: real CSS missing")
                        scroll = page.evaluate("""() => ({
                            viewport: innerWidth, doc: document.documentElement.scrollWidth
                        })""")
                        ensure(scroll["doc"] <= width + 2,
                               f"{role}/{width}: horizontal overflow {scroll}")
                        ensure(not failures and not js_errors,
                               f"{role}/{width}: native dependency/JS failures {failures} {js_errors}")
                        labels = article.locator("svg[role=img]").evaluate_all(
                            """nodes => nodes.map(n=>({
                               name: n.getAttribute('aria-label')||'',
                               title: n.querySelector('title')?.textContent||'',
                               desc: n.querySelector('desc')?.textContent||'',
                               stages: [...n.querySelectorAll('[data-g9-stage-id]')]
                                 .map(x=>x.getAttribute('data-g9-stage-id'))
                            }))""")
                        ensure(all(s["name"] or s["title"] for s in labels),
                               f"{role}/{width}: unnamed instructional figure")
                        shot = out / "screenshots" / f"{role}-{width}-initial.png"
                        shot.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(shot), full_page=True, animations="disabled")
                        rec = {"role": role.upper(), "viewport": width,
                               "site_assets_loaded": True,
                               "horizontal_overflow": False,
                               "real_native_http": True,
                               "figure_accessibility": labels,
                               "initial_screenshot_sha256": sha(shot),
                               "initial_visible_sha256": hashlib.sha256(
                                   article.inner_text().encode()).hexdigest()}
                        if role == "core1":
                            for block in ("scope", "hard_transition", "representation_bridge",
                                          "governing_relation", "compact_anchor", "exit_prompt"):
                                ensure(article.locator(f"[data-g9-block='{block}']").count() >= 1,
                                       f"Core1 missing orientation technique block {block}")
                            initial = article.inner_text().lower()
                            # This compares source-specific likely *answer* tokens,
                            # not all mathematics that Core1 is allowed to teach.
                            ensure("only x=4" not in initial
                                   and "x=-1 is extraneous" not in initial
                                   and "both x=4 and x=-1" not in initial,
                                   "Core1 orientation announces the target answer")
                            rec["source_specific_answer_sentinel_absent"] = True
                            rec["t14_prerequisite_bridge_exists"] = True
                        else:
                            ensure(article.locator("[data-g9-ladder]").count() > 0,
                                   "Core2A hint ladder does not use registered support")
                            ensure(article.locator("[data-g9-attempt]").count() > 0
                                   and article.locator("[data-g9-commit]").count() > 0,
                                   "Core2A lacks live written attempt")
                            # Safe scrubbing of original whole-figure SVG title/desc
                            # is intentionally preserved; the generic AUTHORED
                            # reveal-stage label is a tracked human-visible defect.
                            stage_labels = [e["name"] for e in labels if e["stages"]]
                            rec["precommit_stage_label_status"] = (
                                "DEFECT_AUTHORED_GENERIC_STAGE_LABEL" if
                                any(e.strip().lower() == "stage 1" for e in stage_labels)
                                else "DESCRIPTION_W_AND_ACCESSIBILITY_REVIEW_PENDING"
                            )
                            if width == 390:
                                text_box = article.locator("[data-g9-attempt]").first
                                commit = article.locator("[data-g9-commit]").first
                                commit.click()
                                ensure(article.get_attribute("data-attempted") != "1",
                                       "Core2A blank attempt unlocks")
                                rung = article.locator("[data-g9-ladder]").first
                                ensure(rung.locator('[data-g9-rung="1"]').count() >= 1
                                       and rung.locator('[data-g9-rung="2"]').count() >= 1,
                                       "Core2A H1/H2 absent")
                                rec["h1_text"] = rung.locator(
                                    '[data-g9-rung="1"]').first.inner_text()
                                advance = article.locator("[data-g9-next-rung]").first
                                ensure(advance.count() == 1, "Core2A progressive H2 absent")
                                advance.click()
                                rec["h2_precommit_text"] = rung.locator(
                                    '[data-g9-rung="2"]').first.inner_text()
                                gate = article.locator("details[data-requires-attempt]").filter(
                                    has=page.locator('summary:text-is("Hint 3 · after your attempt")'))
                                ensure(gate.count() == 1 and not gate.evaluate("(e)=>e.open"),
                                       "Core2A H3 not sealed before learner commitment")
                                gate.locator("summary").click()
                                ensure(not gate.evaluate("(e)=>e.open"),
                                       "Core2A H3 opened after blank attempt")
                                rec["blank_commit_and_h3_gate"] = "PASS"
                                text_box.fill(
                                    "Squaring gives candidates, but the principal root has a "
                                    "nonnegative value. Check both in the original equality.")
                                commit.click()
                                ensure(article.get_attribute("data-attempted") == "1",
                                       "Core2A nonblank learner response did not commit")
                                gate.locator("summary").click()
                                ensure(gate.evaluate("(e)=>e.open"),
                                       "Core2A postattempt H3 cannot open")
                                content = gate.locator("[data-g9-after-attempt-hint]").first
                                ensure(content.is_visible(), "Core2A H3 text not learner-visible")
                                rec["h3_postcommit_text"] = content.inner_text()
                                rec["h3_after_nonblank_attempt"] = "PASS"
                                after = out / "screenshots/core2a-390-postcommit-h3.png"
                                page.screenshot(path=str(after),full_page=True,animations="disabled")
                                rec["postcommit_screenshot_sha256"] = sha(after)
                        observations.append(rec)
                        page.close()
            finally:
                browser.close()
    finally:
        http.shutdown()
        http.server_close()
        worker.join(timeout=5)
    ensure(len(observations) == 6, "not six actual Core1/Core2A viewport observations")
    return observations

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path,
                        help="Pinned D3 author checkout, NOT integrator checkout")
    args = parser.parse_args()
    root = args.repo.resolve()
    ensure(root.is_dir(), "author checkout not found")
    output = root / "build/imo182-qrt/d3-o1-five-core-integrator"
    output.mkdir(parents=True, exist_ok=True)
    roles, directory, receipt, source, manifest = role_inventory(root)
    math = math_witness()
    browser = browser_roles(root, output)
    for role in roles:
        if role["role"] in ("CORE1", "CORE2A"):
            role["new_integration_browser_probes"] = [
                x for x in browser if x["role"] == role["role"]
            ]
        else:
            # Actual scripts run in CI in same pinned source checkout;
            # this aggregator never misattributes its new checks to them.
            role["prior_owner_o1_benchmark_scripts_to_run"] = {
                "CORE1A": "core1a_o1_benchmark_217.py",
                "CORE1B": "core1b_o1_benchmark_217.py",
                "CORE2B": "core2b_o1_benchmark_217.py",
            }[role["role"]]
    defects = [
        {"role": "CORE2A", "type": "AUTHOR_STAGE_LABEL_INSUFFICIENT_CONTEXT",
         "source_stage": "ED3-GRAPH", "actual_native_label": "Stage 1",
         "owner": "D3_SOURCE_AUTHOR_PLUS_INDEPENDENT_PROTECTED_W_REVIEWER",
         "safe_fix": "Improve authored stage label after W review; do not restore "
                     "pre-attempt whole-SVG title or desc from original asset.",
         "blueprint_gap_proved": False}
    ] if any(r["precommit_stage_label_status"].startswith("DEFECT")
             for r in browser if r["role"] == "CORE2A") else []
    report = {
        "schema": "imo182-o1-explain-d3-five-role-native-golden-integration/v1",
        "authority": "IMO-CORE-BLUEPRINTS v3.1.0 label_sha 2ff9246",
        "cell": "QRT-EXPLAIN-D3", "source_ref": SOURCE_REF,
        "source_blob": SOURCE_BLOB, "manifest_blob": MANIFEST_BLOB,
        "registry_blob": REGISTRY_BLOB, "owner_golden_lock_blob": LOCK_BLOB,
        "fixture": "G-IMO-G9-FIVE-CORE-20261012",
        "source_type": "WHOLLY_AUTHORED_TEST",
        "native_renderer": receipt["renderer"],
        "native_six_page_hashes_verified": True,
        "math_independent_check": math,
        "roles": roles, "new_browser_observations": browser,
        "open_defects": defects,
        "registered_blueprint_modified": False,
        "golden_html_modified": False,
        "core2_original_admitted": 0,
        "qualified_independent_semantic_review": "PENDING",
        "full_12_HSPM_independent_review": "PENDING",
        "owner_QRT_decision_id": None,
        "owner_acceptance": False,
        "o3_gap_demonstrated": False,
        "release_authorized": False,
        "scope": "O1 technical comparator; semantic academic signoff NOT implied"
    }
    location = output / "explain-d3-five-role-integrator-o1.v1.json"
    location.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n",
                        encoding="utf-8")
    print("O1 NATIVE EXPLAIN-D3: five blueprint+frozen-golden role sequences PASS, "
          "six native page SHA receipts PASS, two roles actual HTTP/Chromium x3 PASS")
    print(f"AUTHORED ACCESSIBILITY RISKS: {len(defects)}; signed QRT and Owner 0/28")
    print("REPORT " + str(location))

if __name__ == "__main__":
    main()
