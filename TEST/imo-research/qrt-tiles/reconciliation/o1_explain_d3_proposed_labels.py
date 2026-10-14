#!/usr/bin/env python3
"""Propose/TEST (do not adopt) answer-safe EXPLAIN-D3 SVG stage labels.

Executed only on a disposable CI checkout of exact D3 #224 author SHA after
baseline source validation. Changes two reveal_stages[].label strings in that
CI worktree, never the author PR or immutable golden. Native renderer + real
Chromium prove the candidate names and pre-attempt DOM guard. An independent
maths/W reviewer must still decide whether wording is educationally safe.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

SOURCE_COMMIT = "dfe4bb6766b87132423b01ffaa914ade1145424f"
SOURCE_BLOB = "32fad7e3be4f806e43e5f44942434842ad10c25a"
REGISTRY_BLOB = "591ba061b8771c30fdffc4506aa720ca9ba89335"
MANIFEST_BLOB = "2c74ef14eff21a756e5bf3c6b87f3f9a0447d04e"
LOCK_BLOB = "888678554c41257e6d96c802f0009983ccbb5328"
CANDIDATE_LABELS = {
    "ED3-GRAPH": "Unmarked principal-root curve and signed right-hand side",
    "ED3-ABS": "Unmarked principal-root curve and absolute-value right-hand side",
}
BY_ROLE = {"core2a": "ED3-GRAPH", "core2b": "ED3-ABS"}

def ensure(cond, message):
    if not cond:
        raise AssertionError(message)

def hashbytes(data: bytes):
    return hashlib.sha256(data).hexdigest()

def sha(path: Path):
    return hashbytes(path.read_bytes())

def gitblob(root: Path, path: Path):
    return subprocess.check_output(
        ["git","hash-object",str(path.relative_to(root))],
        cwd=root, text=True).strip()

def audit_candidate(root: Path):
    source = root/"TEST/imo-research/qrt-d3/explain.v1.json"
    manifest = root/"TEST/products/imo182-qrt-d3-explain.manifest.json"
    reg = root/"Shared/web/interactive-page-blueprints.v1.json"
    golden = root/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json"
    ensure(subprocess.check_output(["git","rev-parse","HEAD"],
            cwd=root,text=True).strip()==SOURCE_COMMIT, "source author commit drift")
    for p, expected in ((source,SOURCE_BLOB),(manifest,MANIFEST_BLOB),
                        (reg,REGISTRY_BLOB),(golden,LOCK_BLOB)):
        ensure(gitblob(root,p)==expected, f"cannot propose against drifted {p}")
    original = json.loads(source.read_text(encoding="utf-8"))
    ensure(original["extensions"]["grade9v3:qrt_admitted"] is False,
           "cannot rewrite an accepted/production source as a candidate")
    changed = copy.deepcopy(original)
    edits = []
    for representation in changed["representations"]:
        for stage in representation.get("reveal_stages", []):
            stage_id=stage.get("id")
            if stage_id not in CANDIDATE_LABELS:
                continue
            ensure(stage["label"] == "Stage 1",
                   f"previous generic label already modified for {stage_id}")
            label = CANDIDATE_LABELS[stage_id]
            # Refuse names encoding the target solution, sign/iff verdict or W.
            prohibited=("x=4","x=-1","t=-1","t=4","solution","candidate accepted",
                        "reject","extraneous","both roots", "sign loss",
                        "intersection at")
            ensure(not any(token in label.lower() for token in prohibited),
                   f"authoring proposal contains a protected-answer keyword: {stage_id}")
            stage["label"]=label
            edits.append({"representation":representation["id"],"stage_id":stage_id,
                          "before":"Stage 1","proposed":label})
    ensure({e["stage_id"] for e in edits}==set(CANDIDATE_LABELS),
           "both targeted source stages not located exactly once")
    reverse = copy.deepcopy(changed)
    for representation in reverse["representations"]:
        for stage in representation.get("reveal_stages", []):
            if stage.get("id") in CANDIDATE_LABELS:
                stage["label"]="Stage 1"
    ensure(reverse==original,
           "candidate overlay changed something beyond two authored stage labels")

    out=root/"build/imo182-qrt/d3-proposed-labels-o1"
    out.mkdir(parents=True, exist_ok=True)
    original_raw=source.read_bytes()
    # Semantic-diff only, disposable source checkout. Preserve original bytes
    # after the render so further run steps or later use cannot mistake overlay
    # for an author commit or exact recorded baseline source blob.
    build=root/"build/imo182-qrt/d3/explain-stage-label-proposed"
    try:
        source.write_text(json.dumps(changed,ensure_ascii=False,indent=2)+"\n",
                          encoding="utf-8")
        proposed_blob=gitblob(root,source)
        cmd=[
            sys.executable, "Shared/tools/render_core.py", "build",
            "--manifest",str(manifest.relative_to(root)),
            "--out",str(build.relative_to(root)),
            "--mode","PAGES","--reference","--draft"
        ]
        subprocess.run(cmd,cwd=root,check=True)
    finally:
        source.write_bytes(original_raw)
    ensure(gitblob(root,source)==SOURCE_BLOB,
           "disposable worktree source was not byte-restored")
    receipt=json.loads((build/"render-receipt.json").read_text())
    ensure(receipt["renderer"]=="render_core/2"
           and receipt["gaps"]==[]
           and receipt["mode"]=="PAGES", "proposed overlay not sole-renderer native")
    for filename, expected in receipt["page_sha256"].items():
        ensure(sha(build/filename)==expected,
               "proposed native output no longer matches renderer receipt: "+filename)

    successor=root/"TEST/imo-research/qrt-d3-successor"
    sys.path.insert(0,str(successor))
    from browser_stage_217 import RootHandler
    http=ThreadingHTTPServer(("127.0.0.1",0),
                             partial(RootHandler,directory=str(root)))
    worker=threading.Thread(target=http.serve_forever,daemon=True)
    worker.start()
    records=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for role, stage_id in BY_ROLE.items():
                    for width in (390,768,1280):
                        page=browser.new_page(viewport={"width":width,"height":900})
                        errors=[]
                        page.on("pageerror",lambda e: errors.append(str(e)))
                        page.on("requestfailed",lambda r: errors.append(r.url))
                        relative=f"/build/imo182-qrt/d3/explain-stage-label-proposed/{role}.html"
                        response=page.goto(
                            f"http://127.0.0.1:{http.server_port}"+relative,
                            wait_until="load")
                        ensure(response and response.status==200,
                               f"candidate {role}/{width} native HTTP fails")
                        ensure(page.locator(f"html[data-g9-role='{role.upper()}']").count()==1,
                               "wrong source role after proposal")
                        styles=page.evaluate("""() => [...document.querySelectorAll(
                             'link[rel=stylesheet]')].map(e=>Boolean(e.sheet))""")
                        ensure(len(styles)>=2 and all(styles),
                               f"{role}/{width} original site CSS missing")
                        ensure(page.evaluate(
                            "() => document.documentElement.scrollWidth <= innerWidth+2"),
                            f"proposed {role}/{width} page overflows")
                        article=page.locator("article[data-g9-unit]").first
                        ensure(article.is_visible(), f"{role}/{width} real learner missing")
                        svg=article.locator("svg[role=img]").evaluate_all(
                            """nodes=>nodes.map(n=>({
                            name:n.getAttribute('aria-label')||'',
                            title:n.querySelector('title')?.textContent||'',
                            desc:n.querySelector('desc')?.textContent||'',
                            stages:[...n.querySelectorAll('[data-g9-stage-id]')]
                              .map(s=>s.getAttribute('data-g9-stage-id'))
                            }))""")
                        expected_name=CANDIDATE_LABELS[stage_id]
                        matched=[s for s in svg if stage_id in s["stages"]]
                        ensure(len(matched)==1 and matched[0]["name"]==expected_name,
                               f"{role}/{width} renderer did not project authored stage label")
                        ensure(not matched[0]["title"] and not matched[0]["desc"],
                               "pre-attempt SVG restore of answer-capable whole-figure metadata")
                        ensure(not errors, f"proposed {role}/{width} browser errors {errors}")
                        # Only static known answer sentinels are machine-testable.
                        # No expert assessment that ALL possible semantic W
                        # disclosures are absent is claimed.
                        name=matched[0]["name"].lower()
                        ensure(not any(s in name for s in
                                   ("x=4","x=-1","t=-1","t=4","both solve")),
                               "pre-attempt label leaks a target root verdict")
                        if role=="core2b":
                            gated=article.locator(
                                "details[data-g9-reveal][data-requires-attempt]").first
                            ensure(gated.count()==1
                                   and not gated.evaluate("(e)=>e.open"),
                                   "proposed source opened Core2B protected transfer")
                            ensure(not gated.locator("[data-g9-payload-slot]").first.inner_text().strip(),
                                   "proposed source materialized full transfer answer before response")
                        else:
                            h3=article.locator("details[data-requires-attempt]").filter(
                                has=page.locator('summary:text-is("Hint 3 · after your attempt")'))
                            ensure(h3.count()==1
                                   and not h3.evaluate("(e)=>e.open"),
                                   "proposed source prematurely opened Core2A H3")
                        shot=out/"screenshots"/f"{role}-{width}-proposed.png"
                        shot.parent.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(shot),full_page=True,animations="disabled")
                        records.append({
                            "role":role.upper(),"viewport":width,"stage_id":stage_id,
                            "native_aria_name":expected_name,
                            "original_svg_whole_title_desc_scrubbed":True,
                            "native_CSS_loaded":True,"horizontal_overflow":False,
                            "precommit_gates_sealed":True,
                            "screenshot_sha256":sha(shot)})
                        page.close()
            finally:
                browser.close()
    finally:
        http.shutdown();http.server_close();worker.join(timeout=5)
    ensure(len(records)==6,"not two proposed real pages x three viewports")
    result={
        "schema":"imo182-explain-d3-authoring-stage-label-proposal/v1",
        "issue":182,"source_issue":217,"author_pr":224,
        "cell":"QRT-EXPLAIN-D3", "source_sha_before":SOURCE_BLOB,
        "source_sha_candidate_in_temporary_worktree":proposed_blob,
        "source_file_restored_to_exact_original_blob":True,
        "registered_blueprint_changed":False,"renderer_changed":False,
        "original_golden_changed":False, "manifest_changed":False,
        "source_author_branch_changed":False,
        "changes_to_source_semantic_fields":edits,
        "new_native_html_sha256":receipt["page_sha256"],
        "three_width_native_browser_evidence":records,
        "precommit_whole_SVG_metadata_safety":"PRESERVED",
        "known_answer_sentinels_not_in_new_staged_labels":True,
        "status":"PROPOSED_TEST_OVERLAY_NONADOPTED",
        "protected_W_complete_educational_review":"PENDING_INDEPENDENT",
        "accessibility_quality_human_review":"PENDING",
        "owner_qrt_decision_id":None,"owner_golden_designation":None,
        "publisher_rights":False,"release":False,
        "next_action":"D3 author / independent W reviewer review label semantics, "
                      "then source-only branch edit and exact-head five-Core replay"
    }
    path=out/"explain-d3-two-stage-label-proposal.v1.json"
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                    encoding="utf-8")
    print("O1 PROPOSED EXPLAIN-D3: two authored preattempt labels rendered via "
          "sole renderer; six live viewport AX names + protected gates PASS")
    print("PROPOSAL ONLY: D3 source restored; author reviewer signature and Owner QRT pending")
    print("REPORT "+str(path))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True,type=Path)
    args=ap.parse_args()
    audit_candidate(args.repo.resolve())
