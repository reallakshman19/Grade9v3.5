#!/usr/bin/env python3
"""IMO #182 Agent A: MODEL-D2 five-role real Core blueprint/golden/W benchmark.

Run on the exact (unmerged) #245 source checkout, NOT on #230 integration
checkout. Native learner pages are made by Shared/tools/render_core.py first.
No manual HTML, no Shared renderer/registry/golden mutation, no QRT acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import threading
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

SOURCE_HEAD="d450d0f0cda25c51c0232db31e6592588634a90b"
SOURCE_BLOB="db87b5a4a7bc807e0680a64417f2c6ca5ca08cf3"
MANIFEST_BLOB="313320473b91968f599424b30561f035e9089aa8"
REGISTRY_BLOB="591ba061b8771c30fdffc4506aa720ca9ba89335"
LOCK_BLOB="888678554c41257e6d96c802f0009983ccbb5328"
ROLES=("core1","core1a","core1b","core2a","core2b")
BP={"core1":"BP-CORE1-ORIENTATION@1.1.0",
    "core1a":"BP-CORE1A-CONSTRUCTION@1.8.0",
    "core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0",
    "core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
    "core2b":"BP-CORE2B-TRANSFER@1.1.0"}
TECH={"core1":["T14"],"core1a":["T02","T03","T11"],
      "core1b":["T06","T10","T12"],"core2a":["T05","T07"],
      "core2b":["T08","T09"]}
PRIMARY="Q-TEST-QRT-MODEL-D2-PRIMARY"
TRANSFER="Q-TEST-QRT-MODEL-D2-TRANSFER"
# These are *only* known full answer/model sentinels in a learner's
# precommit page. They are not a semantic theorem prover for protected W.
PRIMARY_LEAK=("four large", "five small", "x=4 large", "x=5 small",
              "4(9−x)+7x=48", "4x+7(9−x)=48", "36+3x=48")
TRANSFER_LEAK=("74 is impossible","74 impossible","closest valid totals",
               "71 below", "75 above", "19/4","4.75")

def require(x,why):
    if not x: raise AssertionError(why)

def read(path): return json.loads(path.read_text(encoding="utf-8"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def blob(root,path):
    return subprocess.check_output(["git","hash-object",str(path.relative_to(root))],
                                   cwd=root,text=True).strip()

class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slots=[];self.blocks=[];self.components=[];self.bps=[];self.roles=[]
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        for key,dest in (
            ("data-blueprint-slot",self.slots),
            ("data-g9-block",self.blocks),
            ("data-g9-component",self.components),
            ("data-blueprint-ref",self.bps),
            ("data-g9-role",self.roles)):
            if data.get(key):dest.append(data[key])
def structural(path):
    parser=Blocks();parser.feed(path.read_text(encoding="utf-8"));return parser

class RootAssets(SimpleHTTPRequestHandler):
    """Serve actual source checkout; map /build/css/js to actual /public assets."""
    def translate_path(self,path):
        uri=unquote(urlsplit(path).path)
        for prefix in ("css","js","images","img","fonts","assets"):
            marker=f"/build/{prefix}/"
            if uri.startswith(marker):
                rel=uri[len("/build/"):]
                candidate=(self.directory_root/"public"/rel).resolve()
                if candidate.is_relative_to((self.directory_root/"public").resolve()):
                    return str(candidate)
        return super().translate_path(path)
    def __init__(self,*args,directory_root=None,**kwargs):
        self.directory_root=Path(directory_root)
        super().__init__(*args,directory=str(self.directory_root),**kwargs)
    def log_message(self,*args):pass

def verify_source(root):
    path=root/"TEST/imo-research/qrt-d2/model.v1.json"
    manifest=root/"TEST/products/imo182-qrt-d2-model.manifest.json"
    registry=root/"Shared/web/interactive-page-blueprints.v1.json"
    lock=root/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json"
    for p,want in ((path,SOURCE_BLOB),(manifest,MANIFEST_BLOB),
                   (registry,REGISTRY_BLOB),(lock,LOCK_BLOB)):
        require(blob(root,p)==want,f"pinned {p} changed, stop instead of repin silently")
    require(subprocess.check_output(["git","rev-parse","HEAD"],
                   cwd=root,text=True).strip()==SOURCE_HEAD,
            "not source author #245 exact commit")
    package,prod,reg,frozen=map(read,(path,manifest,registry,lock))
    require(prod["subject"]=="TEST" and prod["selection"]["core2"]==[]
           and tuple(r.lower() for r in prod["output_roles"])==ROLES,
           "source not 5 authorized TEST roles")
    require(prod["selection"]["core2a"]==[PRIMARY]
           and prod["selection"]["core2b"]==[TRANSFER],
           "wrong D2 candidate selected")
    require(package["extensions"]["grade9v3:qrt_admitted"] is False,
           "unreviewed QRT cell must not be admitted")
    require(reg["registry_version"]=="1.17.0" and
            frozen["fixture_id"]=="G-IMO-G9-FIVE-CORE-20261012",
            "registry or frozen fixture identity changed")
    qs={q["id"]:q for q in package["questions"]}
    a,b=qs[PRIMARY],qs[TRANSFER]
    require("Decide which cup-size count your variable represents" in a["stem"],
            "old predetermined-cup-variable source reappeared")
    require("variable for the LARGE-cup count" not in a["stem"],
            "source regressed to preselected large-count variable")
    require(a["extensions"]["grade9v3:cognitive_demand"]["primary"]=="MODEL" and
            a["difficulty"]["band"]=="D2", "unexpected claimed cell identity")
    require(a["answer"]["crux_move_ref"]=="MOVE-TEST-QRT-MODEL-D2-COUNT-TO-COST",
            "model-choice protected W drift")
    require(b["transfer"]["builds_on"]==[PRIMARY],
            "transfer not tied to main")
    return package,prod,reg,frozen

def independent_math():
    # Complete integer enumeration, both permissible choices of x, and
    # exact transfer adjacency (no floating-point selection).
    large=[(x,9-x) for x in range(10) if 7*x+4*(9-x)==48]
    small=[(x,9-x) for x in range(10) if 4*x+7*(9-x)==48]
    require(large==[(4,5)] and small==[(5,4)],
            "two valid variable descriptions do not yield correct quantities")
    require(4*5+7*4==48 and 4+5==9,"primary solution doesn't meet both givens")
    targets=[(n,11-n,5*(11-n)+9*n) for n in range(12)]
    exact=[row for row in targets if row[2]==74]
    below=max((row for row in targets if row[2]<74),key=lambda row:row[2])
    above=min((row for row in targets if row[2]>74),key=lambda row:row[2])
    require(not exact and below==(4,7,71) and above==(5,6,75),
            "integer transfer/adjacent feasible revenue wrong")
    require((74-55)%4!=0 and (74-55)==19,
            "missing transfer integrality contradiction")
    return {"primary_x_large":large,"primary_x_small":small,
            "primary_verification":"4+5=9; 4*5+7*4=48",
            "transfer_integer_enumerated_count":len(targets),
            "claimed_74_feasible":False,"nearest_below":below,
            "nearest_above":above,
            "not_human_qrt_or_demand_classification":True}

def native_inventory(root,reg,frozen):
    output=root/"build/imo182-qrt/d2/model"
    receipt=read(output/"render-receipt.json")
    require(receipt["renderer"]=="render_core/2"
            and receipt["mode"]=="PAGES"
            and receipt["held_to"]=="REFERENCE"
            and receipt["gaps"]==[],
            "not actual zero-gap sole renderer reference pages")
    bpdict={v["id"]:v for v in reg["blueprints"]}
    results=[]
    for role in ROLES:
        path=output/f"{role}.html"
        row=next(x for x in frozen["snapshots"] if x["role"]==role.upper())
        golden=root/"golden/units/G-IMO-G9-FIVE-CORE-20261012"/row["path"]
        require(sha(golden)==row["sha256"],
                f"{role}: original Owner snapshot changed")
        require(sha(path)==receipt["page_sha256"][f"{role}.html"],
                f"{role}: actual new native page != original renderer receipt")
        actual,locked=structural(path),structural(golden)
        bp_id,version=BP[role].split("@")
        bp=bpdict[bp_id]
        require(bp["version"]==version and bp["status"]=="ACTIVE"
                and bp["core_roles"]==[role.upper()], "blueprint changed")
        require(actual.roles[:1]==locked.roles[:1]==[role.upper()]
                and actual.bps==locked.bps==[BP[role]],
                f"{role}: role/registered blueprint differs from Owner frozen role")
        require(actual.slots==locked.slots and len(actual.slots)>=2,
                f"{role}: blueprint required slot order differs from Owner original")
        require(actual.components==locked.components,
                f"{role}: component sequence differs from frozen technique")
        # Core1B reconstruction is a structurally locked exact teaching route;
        # other role-specific blocks may be semantically contextual.
        if role=="core1b":
            require(actual.blocks==locked.blocks and len(actual.blocks)==13,
                    "Core1B registered reconstruction 13-block golden order mismatch")
        results.append({
            "role":role.upper(),"blueprint":BP[role],
            "sha256":sha(path),"receipt_sha256_equal":True,
            "original_owner_role_sha256":row["sha256"],
            "owner_snapshot_sha256_unchanged":True,
            "golden_slot_sequence":"MATCH",
            "golden_component_sequence":"MATCH",
            "golden_block_sequence":(
                "MATCH_EXACT" if actual.blocks==locked.blocks else
                "CONTEXTUAL_DIFFERENCE_NEEDS_SEMANTIC_REVIEW"),
            "active_technique_ids":TECH[role],
            "academic_role_semantic_verdict":"PENDING_QUALIFIED_REVIEW",
        })
    index=output/"index.html"
    require(index.exists() and sha(index)==receipt["page_sha256"]["index.html"],
            "native index missing or receipt mismatch")
    return results,receipt

def in_viewport(root,reportdir):
    http=ThreadingHTTPServer(
        ("127.0.0.1",0),partial(RootAssets,directory_root=root))
    t=threading.Thread(target=http.serve_forever,daemon=True);t.start()
    observations=[]
    try:
        with sync_playwright() as pw:
            b=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for role in ROLES:
                    for width in (390,768,1280):
                        page=b.new_page(viewport={"width":width,"height":900})
                        errors=[];failed=[]
                        page.on("pageerror",lambda e:errors.append(str(e)))
                        page.on("requestfailed",lambda req:failed.append(req.url))
                        page.on("response",lambda resp:failed.append(f"{resp.status} {resp.url}")
                                if resp.status>=400 and urlsplit(resp.url).path.lower().endswith(
                                    (".css",".js",".svg",".png",".woff",".woff2")) else None)
                        url=f"http://127.0.0.1:{http.server_port}/build/imo182-qrt/d2/model/{role}.html"
                        res=page.goto(url,wait_until="load")
                        require(res is not None and res.status==200,
                                f"{role}/{width}: native learner page HTTP failure")
                        require(page.locator(f"html[data-g9-role='{role.upper()}']").count()==1
                                and page.locator("body[data-blueprint-ref]").get_attribute(
                                    "data-blueprint-ref")==BP[role],
                                f"{role}/{width}: wrong registered role")
                        article=page.locator("article[data-g9-unit]").first
                        require(article.count()==1 and article.is_visible(),
                                f"{role}/{width}: learner article not visible")
                        styles=page.evaluate("""() => [...document.querySelectorAll(
                          'link[rel=stylesheet]')].map(x=>Boolean(x.sheet))""")
                        require(len(styles)>=2 and all(styles),
                                f"{role}/{width}: original CSS not loaded")
                        require(page.evaluate(
                            "() => document.documentElement.scrollWidth <= innerWidth + 2"),
                            f"{role}/{width}: document overflows screen")
                        svg=article.locator("svg[role=img]").evaluate_all(
                            """nodes=>nodes.map(x=>({
                             name:x.getAttribute('aria-label')||'',
                             title:x.querySelector('title')?.textContent||'',
                             desc:x.querySelector('desc')?.textContent||'',
                             stages:[...x.querySelectorAll('[data-g9-stage-id]')]
                               .map(s=>s.getAttribute('data-g9-stage-id'))
                            }))""")
                        require(all(s["name"] or s["title"] for s in svg),
                                f"{role}/{width}: graphic not accessible by name")
                        result={"role":role.upper(),"viewport":width,
                                "native_real_HTTP":True,"original_CSS_loaded":True,
                                "svg_accessibility":svg,"page_overflow":False}
                        if role=="core1":
                            for needed in ("scope","hard_transition","representation_bridge",
                                           "governing_relation","compact_anchor","exit_prompt"):
                                require(article.locator(
                                    f"[data-g9-block='{needed}']").count()>=1,
                                    f"Core1 missing required orienting {needed}")
                            result["prerequisite_not_model_answer"] = "SOURCE_SPECIFIC_REVIEW_PENDING"
                        if role=="core1a":
                            exitarea=article.locator("[data-g9-block='exit_task']")
                            require(exitarea.count()>=1
                                    and "seven" in exitarea.inner_text().lower()
                                    and "47" in exitarea.inner_text(),
                                    "Core1A missing independent 7-badge 47-credit exit")
                            result["independent_changed_numbers_exit_present"]=True
                        if role=="core1b":
                            require(article.locator(
                                "[data-g9-block='boundary_test']").count()>=1,
                                "Core1B distinct 49-credit impossible boundary absent")
                        if role in ("core2a","core2b"):
                            initial=article.inner_text()
                            metadata=" ".join(s["name"]+" "+s["title"]+" "+s["desc"]
                                              for s in svg)
                            combined=(initial+" "+metadata).lower()
                            banned=PRIMARY_LEAK if role=="core2a" else TRANSFER_LEAK
                            require(not any(s in combined for s in banned),
                                    f"{role}/{width}: known protected answer/model precommit sentinel leaked")
                            result["precommit_answer_sentinels_absent"]=True
                            if role=="core2a":
                                stem=article.locator("[data-g9-block='stem']").first.inner_text()
                                require("Decide which cup-size count your variable represents" in stem,
                                        "actual native core2a stem still fixes count variable")
                                result["learner_variable_role_choice_visible"]=True
                        if width==390 and role!="core1":
                            gates=article.locator("details[data-g9-reveal][data-requires-attempt]")
                            require(gates.count()>=1,
                                    f"{role}: no gated learner response at original source")
                            require(all(not x.strip() for x in
                                        gates.locator("[data-g9-payload-slot]").all_inner_texts()),
                                    f"{role}: protected payload materialised before attempt")
                            require(all(gates.nth(i).get_attribute("data-locked") is not None
                                        for i in range(gates.count())),
                                    f"{role}: gate not initially locked")
                            main_attempt=article.locator(
                                "[data-g9-attempt-box]:not([data-g9-attempt-stage='boundary'])").first
                            if not main_attempt.count():
                                main_attempt=article
                            commit=main_attempt.locator("button[data-g9-commit]").first
                            answer=main_attempt.locator("textarea[data-g9-attempt]").first
                            require(commit.count()==1 and answer.count()==1,
                                    f"{role}: no accessible written attempt")
                            if role=="core2a":
                                initial=article.inner_text()
                                hint=article.get_by_role("button",name="Next hint")
                                require(hint.count()==1,"MODEL-D2 H2 trigger missing")
                                hint.click()
                                exposed=article.inner_text()
                                delta=[line.strip() for line in exposed.splitlines()
                                       if len(line.strip())>20 and line.strip() not in initial.splitlines()]
                                require(bool(delta),"H2 did not progressively reveal any text")
                                require(not any(s in exposed.lower() for s in PRIMARY_LEAK),
                                        "MODEL-D2 precommit H2 supplies known model/answer")
                                result["h2_text_before_attempt"]=delta
                                h3=article.locator(
                                    'details[data-g9-payload-ref*="after-attempt-hint-3"]')
                                require(h3.count()==1 and h3.get_attribute("data-locked") is not None,
                                        "H3 method not deferred")
                            commit.click()
                            require(all(gates.nth(i).get_attribute("data-locked") is not None
                                        for i in range(gates.count())),
                                    f"{role}: blank attempt unlocked protected help")
                            result["blank_commit_blocked"]=True
                            answer.fill(
                                "I choose the two type counts, derive the complement, "
                                "link their prices, and test integer feasibility.")
                            commit.click()
                            primarygate=gates.first
                            require(primarygate.get_attribute("data-locked") is None,
                                    f"{role}: substantive written commit does not unlock response")
                            result["nonblank_committed"]=True
                            if role=="core1b":
                                boundary=article.locator(
                                    "details[data-g9-attempt-stage='boundary'][data-requires-attempt]")
                                b_box=article.locator(
                                    "[data-g9-attempt-box][data-g9-attempt-stage='boundary']")
                                require(boundary.count()==1 and b_box.count()==1,
                                        "Core1B independent 49-credit boundary controls missing")
                                require(boundary.get_attribute("data-locked") is not None,
                                        "main attempt unlocked separate boundary answer")
                                b_box.locator("button[data-g9-commit]").click()
                                require(boundary.get_attribute("data-locked") is not None,
                                        "blank Core1B boundary committed")
                                b_box.locator("textarea[data-g9-attempt]").fill(
                                    "The revenue equation yields a fractional item, "
                                    "so no whole-number mixture satisfies 49.")
                                b_box.locator("button[data-g9-commit]").click()
                                require(boundary.get_attribute("data-locked") is None,
                                        "Core1B independent boundary not unlocked after response")
                                result["separate_boundary_attempt_protected"]=True
                            if role=="core2a":
                                require(h3.get_attribute("data-locked") is None,
                                        "after response H3 still locked")
                                h3.locator("summary").click()
                                require(article.locator(
                                    "[data-g9-after-attempt-hint]").is_visible(),
                                    "after-response H3 not displayed")
                                result["postattempt_h3"]=True
                        require(not errors and not failed,
                                f"{role}/{width}: actual CSS/runtime requests/errors {errors} {failed}")
                        snap=reportdir/"screenshots"/f"{role}-{width}-initial.png"
                        snap.parent.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(snap),full_page=True,animations="disabled")
                        result["screenshot_sha256"]=sha(snap)
                        observations.append(result)
                        page.close()
            finally:b.close()
    finally:
        http.shutdown();http.server_close();t.join(timeout=5)
    require(len(observations)==15,"not all 5 real Core roles × 3 viewports")
    return observations

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",type=Path,required=True)
    args=parser.parse_args()
    root=args.repo.resolve()
    pkg,product,reg,locked=verify_source(root)
    roles,receipt=native_inventory(root,reg,locked)
    math=independent_math()
    reportdir=root/"build/imo182-qrt/d2-model-five-core"
    browser=in_viewport(root,reportdir)
    report={
        "schema":"imo182-model-d2-five-native-core-golden-math-w/v1",
        "authority":"IMO-CORE-BLUEPRINTS v3.1.0 label_sha 2ff9246",
        "cell":"QRT-MODEL-D2",
        "proposed_primary_cognitive_demand":"MODEL",
        "strongest_undecided_rival":"APPLY",
        "source_commit":SOURCE_HEAD,"source_git_blob":SOURCE_BLOB,
        "manifest_git_blob":MANIFEST_BLOB,
        "blueprint_registry_git_blob":REGISTRY_BLOB,
        "frozen_owner_golden_lock_blob":LOCK_BLOB,
        "original_owner_golden_unchanged":True,
        "renderer":"render_core/2",
        "native_html_receipt_page_sha256":receipt["page_sha256"],
        "native_six_html_sha_verified":True,
        "five_registered_roles":roles,
        "independent_computed_math":math,
        "native_http_browser":browser,
        "question_first_w_hypothesis":
          "Learner chooses count variable and constructs count-to-price relation. "
          "Core1A already teaches complement modelling; determine whether core2a "
          "still requires genuine governing model construction vs APPLY.",
        "known_preattempt_full_answer_sentinels_absent":True,
        "independent_W_semantic_review":"PENDING_QUALIFIED_REVIEW",
        "all_12_HSPM":"PENDING_QUALIFIED_REVIEW",
        "difficulty_five_factors":"AUTHOR_PROPOSAL_NOT_INDEPENDENT",
        "candidate_fix":"NONE_AUTHORIZED_SOURCE_CURRENT",
        "owner_qrt_decision_id":None,"owner_accepted":False,
        "owner_golden_designation":None,
        "o3_blueprint_gap_demonstrated":False,
        "source_original_exam_rights_granted":False,
        "original_core2_admitted":0,
        "product_public_release_authorized":False,
        "comparison_kind":"REGISTERED_ROLE_STRUCTURE_AND_TESTED_LEARNER_BEHAVIOR_NOT_RAW_CROSS_QUESTION_BYTE_PARITY",
    }
    reportdir.mkdir(parents=True,exist_ok=True)
    path=reportdir/"model-d2-five-core-golden-w.v1.json"
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("O1 MODEL-D2: exact #245 source + five registered blueprint roles and frozen golden slots/components PASS")
    print("O1 MODEL-D2: six actual native hashes PASS; main both-variable and integer transfer math PASS")
    print("O1 MODEL-D2: 15 real native HTML/CSS browser probes PASS; academic MODEL vs APPLY still HOLD")
    print("REPORT "+str(path))

if __name__=="__main__":
    main()
