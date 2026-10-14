#!/usr/bin/env python3
"""Owner sticky v3.1.0 O1: actual Core2B transfer vs immutable golden.

Cross-question registered-blueprint technique and real changed-case learner
attempt.  Source, golden, renderer and registry are read-only. The script is
NOT a QRT/academic verdict or accessibility approval. Only sole-renderer HTML.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

from core1a_o1_benchmark_217 import ROOT, LOCKED, SOURCE, MANIFEST, REGISTRY, sha, gitblob, load, parse
from browser_stage_217 import RootHandler

BUILD = ROOT / "build/imo182-qrt/d3/explain"
NATIVE = BUILD / "core2b.html"
RECEIPT = BUILD / "render-receipt.json"
OUT = ROOT / "build/imo182-qrt/d3-successor/o1-core2b"
CELL = "QRT-EXPLAIN-D3"
BP = "BP-CORE2B-TRANSFER@1.1.0"
QUESTION = "Q-TEST-QRT-EXPLAIN-D3-BOUNDARY"
PRIMARY = "Q-TEST-QRT-EXPLAIN-D3-CLASSIFY"
SOURCE_BLOB = "32fad7e3be4f806e43e5f44942434842ad10c25a"
MANIFEST_BLOB = "2c74ef14eff21a756e5bf3c6b87f3f9a0447d04e"
REGISTRY_BLOB = "591ba061b8771c30fdffc4506aa720ca9ba89335"
GOLDEN_LOCK_BLOB = "888678554c41257e6d96c802f0009983ccbb5328"
BLOCKS = [
    "provenance","stem","lineage","conditions","stage_caption","safe_support",
    "lineage_check","invariant_changed","changed_demand","protected_move",
    "answer","rubric","independent_check","repair"
]

def require(value, message):
    if not value:
        raise AssertionError(message)

def check_math():
    # Exact arithmetic: the two given candidate roots of
    # t+5=(t-1)**2 are -1,4; both satisfy the changed ORIGINAL but not
    # the original signed RHS. This checks answer truth, not cognitive
    # demand or adequacy of hints.
    checks=[]
    for t in (-1, 4):
        radicand=t+5
        require(radicand>=0, "unexpected root domain")
        root=math.isqrt(radicand)
        require(root*root==radicand, "candidate radical not integral as expected")
        check={"candidate":t,"left_principal_root":root,
               "original_signed_rhs":t-1,"changed_absolute_rhs":abs(t-1),
               "original_signed_equality":root==t-1,
               "changed_absolute_equality":root==abs(t-1)}
        checks.append(check)
    require([c["original_signed_equality"] for c in checks]==[False,True],
            "main and transfer lose their distinctive admission condition")
    require(all(c["changed_absolute_equality"] for c in checks),
            "changed absolute-value radical does not admit both candidates")
    # Necessity: squaring changed original implies a quadratic with
    # factored (t-4)(t+1). No further real roots can appear.
    require((-1-4)*(-1+1)==0 and (4-4)*(4+1)==0,
            "changed squared algebraic candidate factorization not true")
    return checks

def screenshot(page, filename):
    p=OUT/"screenshots"/filename
    p.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(p),full_page=True,animations="disabled")
    return {"file":p.relative_to(ROOT).as_posix(),"sha256":sha(p)}

def observe_browser():
    server=ThreadingHTTPServer(("127.0.0.1",0),
        partial(RootHandler,directory=str(ROOT)))
    worker=threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    observations=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for width in (390,768,1280):
                    page=browser.new_page(viewport={"width":width,"height":900},
                                          device_scale_factor=1)
                    failures=[];errors=[]
                    page.on("requestfailed",lambda req:failures.append(req.url))
                    page.on("response",lambda res:failures.append(str(res.status)+" "+res.url)
                            if res.status>=400 and urlsplit(res.url).path.endswith(
                                (".css",".js",".svg",".png",".jpg",".woff",".woff2")) else None)
                    page.on("pageerror",lambda e:errors.append(str(e)))
                    url=f"http://127.0.0.1:{server.server_port}/build/imo182-qrt/d3/explain/core2b.html"
                    response=page.goto(url,wait_until="load")
                    require(response is not None and response.status==200,
                            f"CORE2B native HTTP page broken at {width}")
                    require(page.locator("html[data-g9-role='CORE2B']").count()==1,
                            "wrong native role")
                    require(page.locator("body[data-blueprint-ref]").get_attribute("data-blueprint-ref")==BP,
                            "not registered transfer blueprint")
                    article=page.locator("article[data-g9-unit]").first
                    require(article.is_visible(), "no learner article")
                    require(QUESTION in article.locator("[data-g9-block='stem']").inner_text()
                            or "sqrt(t+5)=|t-1|" in article.locator("[data-g9-block='stem']").inner_text(),
                            "actual changed-case question not visible")
                    require("sqrt(t+5)=|t-1|" in article.locator("[data-g9-block='stem']").inner_text(),
                            "incorrect transfer original equation")
                    require(article.locator("[data-g9-block='lineage']").is_visible(),
                            "transfer must connect to first case")
                    require(article.locator("[data-g9-block='safe_support']").is_visible(),
                            "learner support absent")
                    css=page.evaluate(
                        "() => [...document.querySelectorAll('link[rel=stylesheet]')].map(e=>Boolean(e.sheet))")
                    require(len(css)>=2 and all(css), f"{width}: original CSS not loaded")
                    scroll=page.evaluate(
                        "() => ({viewport:innerWidth,html:document.documentElement.scrollWidth})")
                    require(scroll["html"]<=width+2, f"{width}: horizontal overflow")
                    svg=article.locator("svg[role=img]").evaluate_all(
                        """nodes => nodes.map(n=>({
                           name:n.getAttribute('aria-label')||'',
                           desc:n.querySelector('desc')?.textContent||'',
                           stage_ids:[...n.querySelectorAll('[data-g9-stage-id]')]
                             .map(e=>e.getAttribute('data-g9-stage-id'))
                        }))""")
                    require(len(svg)>=1 and all(x["name"] and x["stage_ids"] for x in svg),
                            "unidentified native graph role/stage")
                    # Known *risk* "Stage 1" is recorded, not counted as
                    # an accessibility pass, nor unsafely repaired by restoring
                    # whole-SVG preattempt metadata.
                    gate=article.locator("details[data-g9-reveal][data-requires-attempt]").first
                    text=article.locator("[data-g9-attempt]").first
                    commit=article.locator("[data-g9-commit]").first
                    require(gate.count()==1 and text.count()==1 and commit.count()==1,
                            "core2b independent review gate or attempt absent")
                    slot=gate.locator("[data-g9-payload-slot]").first
                    require(slot.count()==1 and not slot.inner_text().strip(),
                            "changed-case full answer already in DOM before attempt")
                    require(not gate.evaluate("(e) => e.open"),
                            "changed-case full answer gate open precommit")
                    # Markup under the closed post-attempt gate must not be visible.
                    for block in ("invariant_changed","changed_demand","protected_move",
                                  "answer","rubric","independent_check","repair"):
                        require(not article.locator(f"[data-g9-block='{block}']").is_visible(),
                                f"{block} is learner-visible before attempt at {width}")
                    visible=article.inner_text()
                    require("Both t=-1 and t=4 solve" not in visible,
                            "transfer exact answer leaked to visible preattempt text")
                    snap=screenshot(page,f"core2b-{width}-initial.png")
                    row={"role":"CORE2B","cell":CELL,"viewport":width,
                         "registered_blueprint":BP,"loaded_original_site_css":css,
                         "outer_overflow":False,"visible_graph":svg,
                         "known_authored_stage_label_risk":"Stage 1" if
                         any(x["name"]=="Stage 1" for x in svg) else None,
                         "initial_screenshot":snap}
                    if width==390:
                        commit.click()
                        require(article.get_attribute("data-attempted")!="1",
                                "blank changed-case attempt wrongly committed")
                        gate.locator("summary").click()
                        require(not gate.evaluate("(e)=>e.open"),
                                "blank attempt incorrectly revealed review")
                        require(not slot.inner_text().strip(),
                                "blank attempt populated protected answer")
                        row["blank_transfer_commit_blocked"]=True
                        text.fill("The squared candidates stay -1 and 4. Absolute value makes the changed RHS nonnegative, so both can pass the original equation: 2=2 and 3=3.")
                        commit.click()
                        require(article.get_attribute("data-attempted")=="1",
                                "nonblank transfer explanation not committed")
                        gate.locator("summary").click()
                        require(gate.evaluate("(e)=>e.open"), "review did not open after response")
                        answer=slot.inner_text()
                        require("Both t=-1 and t=4 solve" in answer,
                                "native transfer does not reveal correct changed case")
                        require("sqrt4=2" in answer and "|-2|=2" in answer
                                and "sqrt9=3" in answer and "|3|=3" in answer,
                                "changed ORIGINAL equation checks not present")
                        require("nonnegative" in answer.lower() and "reversed" in answer.lower(),
                                "protected justification of reversibility absent from feedback")
                        for block in ("invariant_changed","changed_demand","protected_move",
                                      "answer","rubric","independent_check","repair"):
                            require(article.locator(f"[data-g9-block='{block}']").is_visible(),
                                    f"{block} did not become visible postattempt")
                        row["after_written_attempt_changed_case_answer_pass"]=True
                        row["model_answer_sha256"]=hashlib.sha256(answer.encode()).hexdigest()
                        row["postattempt_screenshot"]=screenshot(page,"core2b-390-review-open.png")
                    require(not failures and not errors,
                            f"{width}: actual native page asset/script errors {failures} {errors}")
                    observations.append(row)
                    page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
    return observations

def main():
    pack=load(SOURCE)
    manifest=load(MANIFEST)
    lock=load(LOCKED/"snapshot-lock.json")
    receipt=load(RECEIPT)
    require(gitblob(SOURCE)==SOURCE_BLOB and gitblob(MANIFEST)==MANIFEST_BLOB,
            "pinned source/manifest changed")
    require(gitblob(REGISTRY)==REGISTRY_BLOB and
            gitblob(LOCKED/"snapshot-lock.json")==GOLDEN_LOCK_BLOB,
            "registered blueprint or original Owner golden lock drift")
    require(pack["extensions"]["grade9v3:qrt_admitted"] is False,
            "no QRT acceptance may be inferred")
    require(manifest["selection"]["core2"]==[] and
            manifest["selection"]["core2b"]==[QUESTION] and
            manifest["selection"]["core2a"]==[PRIMARY],
            "not the intended authored TEST main and changed transfer selection")
    q=next(x for x in pack["questions"] if x["id"]==QUESTION)
    require(q["transfer"]["builds_on"]==[PRIMARY] and
            q["transfer"]["protected_move_ref"]=="MOVE-EXPLAIN-D3-ABS-TRANSFER",
            "not the distinct protected transfer")
    require(q["difficulty"]["band"]=="D3","wrong proposed QRT band")
    require(receipt["renderer"]=="render_core/2" and receipt["mode"]=="PAGES"
            and receipt["gaps"]==[], "actual sole renderer build not proven")
    require(NATIVE.is_file() and sha(NATIVE)==receipt["page_sha256"]["core2b.html"],
            "actual native Core2B HTML not receipt-pinned")
    ref=next(x for x in lock["snapshots"] if x["role"]=="CORE2B")
    old=LOCKED/ref["path"]
    require(sha(old)==ref["sha256"],"Owner original Core2B HTML bytes mutated")
    want=parse(old)
    have=parse(NATIVE)
    require(want.blueprint_refs==[BP] and have.blueprint_refs==[BP],
            "native/Owner role registered blueprint disagree")
    require(have.slots==want.slots==["identity","attempt","post_attempt"],
            "Core2B transfer blueprint identity/attempt/review slot mismatch")
    require(have.blocks==want.blocks==BLOCKS,
            "Core2B native teaching, independent-transfer or review blocks differ from Owner technique")
    checks=check_math()
    observed=observe_browser()
    require(len(observed)==3,"not all actual learner widths reviewed")
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    result={
      "schema":"imo217-owner-v310-o1-core2b-real-transfer-golden/v1",
      "aim_version":"v3.1.0","label_sha":"2ff9246","outcome":"O1",
      "cell":CELL,"question":QUESTION,"main_question":PRIMARY,
      "registered_blueprint":BP,"source_head":head,
      "source_blob":gitblob(SOURCE),"manifest_blob":gitblob(MANIFEST),
      "registry_blob":gitblob(REGISTRY),
      "owner_golden_lock_blob":gitblob(LOCKED/"snapshot-lock.json"),
      "original_owner_snapshot_sha256":ref["sha256"],
      "native_core2b_html":NATIVE.relative_to(ROOT).as_posix(),
      "native_core2b_sha256":sha(NATIVE),
      "receipt_page_sha256_matches":True,"renderer_gaps":[],
      "golden_comparison_kind":"REGISTERED_ROLE_SLOT_AND_BLOCK_TECHNIQUE_NOT_CROSS_QUESTION_HTML_BYTE_EQUALITY",
      "blueprint_slots":have.slots,
      "blocks_in_same_order_as_frozen_golden":have.blocks,
      "exact_changed_equation_math_checks":checks,
      "real_browser_learner_observations":observed,
      "result":"TECHNICAL_GOLDEN_ORDER_AND_CHANGED_CASE_ATTEMPT_GATE_PASS",
      "known_unresolved_accessibility_risk":"Authored stage ED3-ABS label Stage 1; meaningfully descriptive preattempt safe wording still requires protected-W review",
      "qualifications":{"independent_qrt_academic_review":"PENDING",
                        "all_twelve_HSPM":"PENDING",
                        "owner_qrt_decision_id":None,
                        "owner_visual_pedagogical_equivalence":"PENDING",
                        "real_learner_study":"NOT_PERFORMED",
                        "A4":"NOT_PERFORMED"},
      "source_rights":False,"blueprint_O3_change":False,
      "public_route_or_release":False,"merge_authorized":False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"core2b-explain-o1-golden-transfer.v1.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("O1 CORE2B NATIVE TRANSFER/GOLDEN TECHNIQUE: 3 slots, 14 blocks,")
    print("real 390/768/1280 CSS Chromium, main->changed-case math (-1,4), protected answer gate.")
    print("SOURCE stage label Stage 1 still generic; no accessibility, QRT or Owner acceptance.")

if __name__=="__main__":
    main()
