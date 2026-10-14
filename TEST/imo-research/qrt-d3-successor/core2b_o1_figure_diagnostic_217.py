#!/usr/bin/env python3
"""O1 protected-W-safe preattempt SVG label review on genuine native Core pages.

The renderer INTENTIONALLY scrubs whole-SVG title/description before attempts
because they may contain the protected learner move W. This proves whether
authored stage labels provide a meaningful safe fallback, without requesting
unsafe metadata restoration or claiming academic/Owner acceptance.
Never edits renderer, source, registry or frozen Owner golden.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import threading
import xml.etree.ElementTree as ET
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright
from browser_stage_217 import RootHandler

ROOT = Path(__file__).resolve().parents[3]
BUILD = ROOT / "build/imo182-qrt/d3/explain"
OUT = ROOT / "build/imo182-qrt/d3-successor/o1-core2-figure-diagnostic"
LOCKED = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
MANIFEST = ROOT / "TEST/products/imo182-qrt-d3-explain.manifest.json"
SOURCE = ROOT / "TEST/imo-research/qrt-d3/explain.v1.json"
REGISTRY = ROOT / "Shared/web/interactive-page-blueprints.v1.json"
SOURCE_FIGURES = {
    "core1a": ("qrt-d3-explain-construct.svg", "BP-CORE1A-CONSTRUCTION@1.8.0"),
    "core2a": ("qrt-d3-explain-attempt.svg", "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0"),
    "core2b": ("qrt-d3-explain-transfer.svg", "BP-CORE2B-TRANSFER@1.1.0"),
}
ORIGINAL_SVG_BLOBS = {
    "core1a": "d410fb1f3b0e34a9f759dc4a843c5a92b7d8d2a5",
    "core2a": "69358bf93fd2c0a064a93a1ef4d9572a7eaa7bec",
    "core2b": "0a8ca742d37c84863e55322f77199e852feeefeb",
}
SRC_SHA = "32fad7e3be4f806e43e5f44942434842ad10c25a"
MAN_SHA = "2c74ef14eff21a756e5bf3c6b87f3f9a0447d04e"
REG_SHA = "591ba061b8771c30fdffc4506aa720ca9ba89335"
LOCK_SHA = "888678554c41257e6d96c802f0009983ccbb5328"
SVG_NS = "{http://www.w3.org/2000/svg}"

def require(x, why):
    if not x:
        raise AssertionError(why)

def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def blob(path: Path):
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True
    ).strip()

def source_label(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()
    title = root.find(SVG_NS + "title")
    desc = root.find(SVG_NS + "desc")
    return {
        "source_aria_label": root.attrib.get("aria-label", ""),
        "source_title": (title.text or "").strip() if title is not None else "",
        "source_description": (desc.text or "").strip() if desc is not None else "",
        "source_svg_git_blob": blob(path),
    }

def browser_probe():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(RootHandler, directory=str(ROOT)))
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    observations = []
    package = json.loads(SOURCE.read_text())
    try:
        with sync_playwright() as pl:
            browser = pl.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for role, (filename, bp) in SOURCE_FIGURES.items():
                    src = ROOT / "TEST/library/figures" / filename
                    source = source_label(src)
                    require(source["source_svg_git_blob"] == ORIGINAL_SVG_BLOBS[role],
                            f"{role} original authored figure drift")
                    require(source["source_title"] and source["source_description"],
                            f"source figure missing description; attribution differs {role}")
                    require(source["source_aria_label"] == source["source_title"],
                            f"unexpected source accessible name {role}")
                    rep = next((r for r in package["representations"]
                                if src.relative_to(ROOT).as_posix() in r.get("rendered_asset_refs", [])), None)
                    require(rep is not None, f"{role} source figure not bound to representation")
                    stage_labels = {stage["id"]: stage["label"] for stage in rep.get("reveal_stages", [])}
                    for width in (390, 768, 1280):
                        page = browser.new_page(viewport={"width": width, "height": 900})
                        errors, failed = [], []
                        page.on("pageerror", lambda exc: errors.append(str(exc)))
                        page.on("requestfailed", lambda req: failed.append(req.url))
                        page.on("response", lambda resp: failed.append(f"{resp.status} {resp.url}")
                                if resp.status >= 400 and
                                urlsplit(resp.url).path.endswith((".css", ".js", ".svg", ".png"))
                                else None)
                        url = f"http://127.0.0.1:{srv.server_port}/build/imo182-qrt/d3/explain/{role}.html"
                        response = page.goto(url, wait_until="load")
                        require(response is not None and response.status == 200,
                                f"{role}/{width} actual Core page failed")
                        require(page.locator("body[data-blueprint-ref]").get_attribute("data-blueprint-ref")==bp,
                                f"{role}/{width} not registered blueprint")
                        styles = page.evaluate(
                            "() => [...document.querySelectorAll('link[rel=stylesheet]')].map(e=>Boolean(e.sheet))")
                        require(len(styles) >= 2 and all(styles), "original linked CSS didn't load")
                        stages = page.locator("article[data-g9-unit] svg[role=img]").evaluate_all(
                            """nodes=>nodes.map(n=>({
                                name:n.getAttribute('aria-label')||'',
                                title:n.querySelector('title')?.textContent||'',
                                description:n.querySelector('desc')?.textContent||'',
                                stage_ids:[...n.querySelectorAll('[data-g9-stage-id]')].map(e=>e.getAttribute('data-g9-stage-id'))
                            }))""")
                        require(stages and all(s["stage_ids"] for s in stages),
                                f"{role}/{width} missing actual instructional stages")
                        metrics = page.evaluate("()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth})")
                        require(metrics["scroll"]<=width+2, f"{role}/{width} page overflow")
                        require(not errors and not failed, f"{role}/{width} JS/HTTP errors {errors} {failed}")
                        observational = {
                          "role": role.upper(), "width": width, "source_figure": src.relative_to(ROOT).as_posix(),
                          "source_metadata": source, "actual_native_figure": stages,
                          "authored_safe_stage_labels": stage_labels,
                          "original_site_CSS_loaded": all(styles),
                          "source_description_preserved": any(s["description"]==source["source_description"]
                                                              for s in stages),
                          "source_title_preserved": any(s["title"]==source["source_title"] for s in stages),
                          "source_label_preserved": any(s["name"]==source["source_aria_label"] for s in stages),
                        }
                        observations.append(observational)
                        page.close()
            finally:
                browser.close()
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join(timeout=5)
    return observations

def main():
    require(blob(SOURCE)==SRC_SHA and blob(MANIFEST)==MAN_SHA and blob(REGISTRY)==REG_SHA,
            "pinned author/manifest/registry drift")
    require(blob(LOCKED / "snapshot-lock.json")==LOCK_SHA, "frozen Owner golden drift")
    receipt=json.loads((BUILD/"render-receipt.json").read_text())
    require(receipt["renderer"]=="render_core/2" and receipt["gaps"]==[],
            "cannot diagnose without sole native renderer zero-gap output")
    lock=json.loads((LOCKED/"snapshot-lock.json").read_text())
    receipts={}
    for role in SOURCE_FIGURES:
        p=BUILD/f"{role}.html"
        require(p.is_file() and sha(p)==receipt["page_sha256"][f"{role}.html"],
                f"{role}: native HTML receipt SHA not verified")
        frozen=next(x for x in lock["snapshots"] if x["role"]==role.upper())
        require(sha(LOCKED/frozen["path"])==frozen["sha256"],
                f"{role} immutable Owner comparator changed")
        receipts[role]={"actual_native_sha256":sha(p),"owner_original_role_sha256":frozen["sha256"],
                        "native_receipt_matches":True}
    probes=browser_probe()
    byrole={role:[p for p in probes if p["role"]==role.upper()] for role in SOURCE_FIGURES}
    require(all(len(a)==3 for a in byrole.values()),"not all real learner viewports checked")
    # The Core1A teaching-path control retains whole-SVG metadata; Core2A/B
    # are PRE_ATTEMPT graphics and deliberately scrub potentially revealing
    # whole-figure title/desc. The safe FALLBACK stage labels are the issue.
    require(all(p["source_description_preserved"] for p in byrole["core1a"]),
            "control Core1A source description missing; broader problem, update diagnosis")
    for role in ("core2a","core2b"):
        require(all(not p["source_description_preserved"] and
                        not p["source_title_preserved"] and
                        not p["source_label_preserved"] for p in byrole[role]),
                f"{role} preattempt protected-move scrub changed; review intent")
        require(all(len(p["actual_native_figure"])==1 and
                        p["actual_native_figure"][0]["name"]==
                        p["authored_safe_stage_labels"][p["actual_native_figure"][0]["stage_ids"][0]]
                        for p in byrole[role]),
                f"{role} native accessible name not derived from authored safe stage label")
        require(all(p["actual_native_figure"][0]["name"]=="Stage 1" for p in byrole[role]),
                f"{role} generic stage label has changed; re-evaluate risk")
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    result={
        "schema":"imo217-owner-o1-preattempt-stage-label-review/v1",
        "aim_version":"v3.1.0","label_sha":"2ff9246","outcome":"O1 prerequisite",
        "cell":"QRT-EXPLAIN-D3","source_head":head,"qrt_accepted":False,
        "verdict":"SAFE_PREATTEMPT_SCRUB_EXPECTED__AUTHORED_STAGE_LABEL_GENERIC",
        "checker_success_means_authoring_label_risk_reproduced_not_page_accepted":True,
        "input_source_and_renderer_authority":"TEST_AUTHORED_SVG_SHARED_REGISTERED_RENDERER",
        "source_blob":SRC_SHA,"manifest_blob":MAN_SHA,"registry_blob":REG_SHA,
        "owner_golden_lock_blob":LOCK_SHA,
        "native_and_original_owner_golden_receipts":receipts,
        "actual_http_chromium_source_to_native_observations":probes,
        "diagnosis":{
            "control":"CORE1A teaching-path SVG retains original title and desc",
            "protected_move_rule":"Shared/tools/render_core.py figure() intentionally removes original whole-SVG title/desc for PRE_ATTEMPT staged graphics, even a single permitted stage, to avoid leaking W",
            "authoring_risk":"CORE2A and CORE2B authored reveal_stages[].label is just Stage 1. Renderer safely uses this text as preattempt accessible name, but it does not name the visible graph",
            "owner":"AUTHORED_TEST_REVEAL_STAGE_LABEL; separately consult Shared owner for possible safe stage-specific descriptions",
            "renderer_fix_authorized_here":False,
            "blueprint_O3_gap_demonstrated":False,
            "source_authoring_label_gap_observed":True,
            "owner_golden_snapshot_unchanged":True,
            "accessibility_policy":"Shared/web/interactive-page-blueprints.v1.json representation_accessibility_policy requires names and descriptions; preattempt solution safety also mandatory",
            "required_fix":"Review a non-answer-revealing replacement for two authored reveal_stages[].label strings with an independent W check before a separately pinned source overlay; DO NOT restore whole-SVG title/desc or show purposes preattempt",
        },
        "academic_reviewer":"UNASSIGNED",
        "academic_qrt_owner_decision_id":None,
        "source_rights":False,"publish_merge_release":False
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"core2-preattempt-safe-stage-label-review.v1.json").write_text(json.dumps(result,indent=2)+"\n")
    print("O1 SAFE REDACTION CONFIRMED: CORE2A/CORE2B PRE_ATTEMPT intentionally scrub")
    print("whole-figure title/desc to protect W; authored stage labels are generic Stage 1.")
    print("AUTHORING LABEL RISK ONLY; do not restore unsafe SVG metadata or self-accept QRT.")

if __name__=="__main__":
    main()
