#!/usr/bin/env python3
"""Owner v3.1.0 O1: only the original renderer's EXPLAIN-D3 Core1B reconstruction.

Cross-question *technique* against immutable 12-Oct Owner Core1B golden.
No handwritten learner HTML, blueprint mutation, QRT accept or Owner golden ruling.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright
from browser_stage_217 import RootHandler
from core1a_o1_benchmark_217 import ROOT, LOCKED, SOURCE, MANIFEST, REGISTRY, sha, gitblob, load, parse

PAGE=ROOT/"build/imo182-qrt/d3/explain/core1b.html"
RECEIPT=PAGE.parent/"render-receipt.json"
OUT=ROOT/"build/imo182-qrt/d3-successor/o1-core1b"
BP="BP-CORE1B-RECONSTRUCTION@1.1.0"
CELL="QRT-EXPLAIN-D3"

def require(value, why):
    if not value:
        raise AssertionError(why)

def snap(page, name):
    p=OUT/"screenshots"/name
    p.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(p), full_page=True, animations="disabled")
    return {"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}

def browser_probe():
    srv=ThreadingHTTPServer(("127.0.0.1",0),partial(RootHandler,directory=str(ROOT)))
    thread=threading.Thread(target=srv.serve_forever,daemon=True)
    thread.start()
    evidence=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for width in (390,768,1280):
                    page=browser.new_page(viewport={"width":width,"height":900})
                    errors=[]; assets=[]
                    page.on("pageerror",lambda e:errors.append(str(e)))
                    page.on("requestfailed",lambda req:assets.append(req.url))
                    page.on("response",lambda r:assets.append(f"{r.status} {r.url}")
                            if r.status>=400 and urlsplit(r.url).path.endswith((".css",".js",".svg",".png")) else None)
                    url=f"http://127.0.0.1:{srv.server_port}/build/imo182-qrt/d3/explain/core1b.html"
                    response=page.goto(url,wait_until="load")
                    require(response is not None and response.status==200,f"{width}: not genuine HTTP-native Core1B")
                    require(page.locator("html[data-g9-role='CORE1B']").count()==1,"wrong native role")
                    require(page.locator("body[data-blueprint-ref]").get_attribute("data-blueprint-ref")==BP,
                            "registered Core1B blueprint absent")
                    css=page.evaluate("() => [...document.querySelectorAll('link[rel=stylesheet]')].map(e=>Boolean(e.sheet))")
                    require(len(css)>=2 and all(css),f"{width}: native site styles unavailable")
                    metrics=page.evaluate("() => ({viewport:innerWidth,scroll:document.documentElement.scrollWidth})")
                    require(metrics["scroll"]<=width+2,f"{width}: actual learner horizontal overflow {metrics}")
                    article=page.locator("article[data-g9-unit]").first
                    require(article.is_visible(),"Core1B actual learner reconstruction article missing")
                    require(article.locator("[data-g9-block='predict']").count()==1,
                            "Core1B predict block missing")
                    require(article.locator("[data-g9-block='boundary_test']").count()==1,
                            "Core1B separately changed boundary missing")
                    d=article.locator("details[data-g9-reveal][data-requires-attempt]")
                    commits=article.locator("[data-g9-commit]")
                    fields=article.locator("[data-g9-attempt]")
                    require(d.count()==2 and commits.count()==2 and fields.count()==2,
                            "Core1B must have independent main AND boundary attempt/reveal pairs")
                    require(d.nth(1).get_attribute("data-g9-attempt-stage")=="boundary",
                            "Core1B changed-case must have a separate attempt gate")
                    require(all(d.nth(i).locator("[data-g9-payload-slot]").inner_text().strip()==""
                                for i in (0,1)),f"{width}: precommit source solution leaked into DOM")
                    require(all(not d.nth(i).evaluate("(e)=>e.open") for i in (0,1)),
                            "a Core1B answer was open before any learner response")
                    row={"viewport":width,"role":"CORE1B","cell":CELL,
                         "loaded_site_css":css,"horizontal_overflow":False,
                         "before":snap(page,f"core1b-{width}-initial.png")}
                    if width==390:
                        commits.nth(0).click()
                        require(article.get_attribute("data-attempted")!="1","blank main attempt accepted")
                        d.nth(0).locator("summary").click()
                        require(not d.nth(0).evaluate("(e)=>e.open"),"main reconstruction opened before response")
                        require(d.nth(0).locator("[data-g9-payload-slot]").inner_text().strip()=="",
                                "main reconstruction content leaked")
                        row["blank_main_blocked"]=True
                        fields.nth(0).fill("Squaring equal values can lose opposite signs: 3 and -3 have the same square, but the principal square root is nonnegative.")
                        commits.nth(0).click()
                        require(article.get_attribute("data-attempted")=="1","main written attempt uncommitted")
                        d.nth(0).locator("summary").click()
                        require(d.nth(0).evaluate("(e)=>e.open"),"main afterattempt reconstruction does not open")
                        recon=d.nth(0).locator("[data-g9-payload-slot]").inner_text()
                        for token in ("Check your prediction","Diagnose","Repair","The step you rebuilt"):
                            require(token in recon,f"Core1B reconstruct missing educational {token}")
                        row["main_reconstruction_afterattempt"]=True
                        row["reconstruction_text_sha256"]=hashlib.sha256(recon.encode()).hexdigest()
                        row["reconstruction_screenshot"]=snap(page,"core1b-390-main-reconstructed.png")
                        # Main commitment MUST NOT unlock separate changed boundary answer.
                        require(article.get_attribute("data-g9-boundary-attempted")!="1",
                                "main attempt incorrectly committed the boundary")
                        d.nth(1).locator("summary").click()
                        require(not d.nth(1).evaluate("(e)=>e.open"),
                                "Core1B independent boundary leaked after only main attempt")
                        require(d.nth(1).locator("[data-g9-payload-slot]").inner_text().strip()=="",
                                "unattempted boundary solution exposed")
                        commits.nth(1).click()
                        require(article.get_attribute("data-g9-boundary-attempted")!="1",
                                "blank boundary attempt accepted")
                        fields.nth(1).fill("sqrt(9)=3, never -3. Squaring both sides loses the original sign; reversing the implication is invalid.")
                        commits.nth(1).click()
                        require(article.get_attribute("data-g9-boundary-attempted")=="1",
                                "nonblank distinct boundary attempt not committed")
                        d.nth(1).locator("summary").click()
                        require(d.nth(1).evaluate("(e)=>e.open"),"boundary answer not released after response")
                        answer=d.nth(1).locator("[data-g9-payload-slot]").inner_text()
                        require("sqrt9=3" in answer and "not -3" in answer
                                and "not sufficient" in answer,
                                "distinct Core1B boundary's correct answer missing")
                        row["separate_boundary_afterattempt"]=True
                        row["boundary_answer_sha256"]=hashlib.sha256(answer.encode()).hexdigest()
                        row["boundary_screenshot"]=snap(page,"core1b-390-boundary-revealed.png")
                    require(not errors and not assets,f"{width}: errors in actual site assets/JS {errors} {assets}")
                    evidence.append(row)
                    page.close()
            finally:
                browser.close()
    finally:
        srv.shutdown();srv.server_close();thread.join(timeout=5)
    return evidence

def main():
    pack=load(SOURCE);man=load(MANIFEST);lock=load(LOCKED/"snapshot-lock.json")
    reg=REGISTRY
    require(pack["extensions"]["grade9v3:qrt_admitted"] is False,"unsafe QRT adoption")
    require(gitblob(SOURCE)=="32fad7e3be4f806e43e5f44942434842ad10c25a","source drift")
    require(gitblob(MANIFEST)=="2c74ef14eff21a756e5bf3c6b87f3f9a0447d04e","manifest drift")
    require(gitblob(reg)=="591ba061b8771c30fdffc4506aa720ca9ba89335","blueprint drift")
    require(gitblob(LOCKED/"snapshot-lock.json")=="888678554c41257e6d96c802f0009983ccbb5328",
            "frozen Owner lock changed")
    require(man["selection"]["core2"]==[] and man["selection"]["microtopics"]==["MIC-QRT-EXPLAIN-D3"],
            "not exact TEST source")
    rec=load(RECEIPT)
    require(rec["renderer"]=="render_core/2" and rec["gaps"]==[] and rec["mode"]=="PAGES",
            "not native, zero-gap renderer output")
    require(PAGE.is_file() and rec["page_sha256"]["core1b.html"]==sha(PAGE),
            "Core1B actual HTML not tied to native renderer receipt")
    original=next(z for z in lock["snapshots"] if z["role"]=="CORE1B")
    golden=LOCKED/original["path"]
    require(sha(golden)==original["sha256"],"original Owner CORE1B snapshot mutated")
    want=parse(golden);actual=parse(PAGE)
    require(want.blueprint_refs==[BP] and actual.blueprint_refs==[BP],
            "registered Core1B blueprint differs from golden")
    require(want.slots==actual.slots==["identity","attempt","reconstruction"],
            "Core1B blueprint slot order differs from golden")
    require(want.blocks==actual.blocks and len(actual.blocks)==13,
            f"Core1B reconstruction block order differs from frozen technique: {actual.blocks}")
    observations=browser_probe()
    require(len(observations)==3,"missing real viewport learner states")
    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True,cwd=ROOT).strip()
    summary={
      "schema":"imo217-core1b-o1-blueprint-to-owner-golden/v1",
      "aim_version":"v3.1.0","label_sha":"2ff9246","outcome":"O1",
      "cell":CELL,"role":"CORE1B","academic_acceptance":False,
      "source_head":head,"source_git_blob":gitblob(SOURCE),
      "manifest_git_blob":gitblob(MANIFEST),"registered_blueprint":BP,
      "registry_git_blob":gitblob(reg),
      "golden_id":lock["fixture_id"],"owner_core1b_sha256":original["sha256"],
      "original_lock_git_blob":gitblob(LOCKED/"snapshot-lock.json"),
      "native_page":PAGE.relative_to(ROOT).as_posix(),"native_core1b_sha256":sha(PAGE),
      "renderer_receipt_sha_match":True,"renderer_gaps":rec["gaps"],
      "comparison_kind":"CROSS_QUESTION_BLUEPRINT_TECHNIQUE_NOT_RAW_HTML_BYTE_EQUALITY",
      "blueprint_slots":actual.slots,"golden_blocks_match":True,
      "original_owner_golden_unchanged":True,
      "browser_observations":observations,
      "technical_state":"BLUEPRINT_RECONSTRUCTION_SEQUENCE_AND_SEPARATE_ATTEMPT_GATES_PASS",
      "open_decisions":{"qualified_QRT_review":"PENDING","owner_qrt_decision_id":None,
                        "owner_visual_pedagogical_golden_approval":"PENDING",
                        "independent_real_learner_inputs":"PENDING",
                        "source_rights":False,"release_or_merge":False},
      "no_blueprint_O3_change":True
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"core1b-explain-o1-benchmark.v1.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print("O1 CORE1B NATIVE GOLDEN TECHNIQUE PASS: 3 slots, 13 blocks,")
    print("3 native learner viewport observations; separate main and boundary attempts protected")
    print("Owner visual/pedagogical acceptance and EXPLAIN-D3 academic QRT remain PENDING")

if __name__=="__main__":
    main()
