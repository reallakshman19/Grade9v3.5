#!/usr/bin/env python3
"""Issue #182: D4 RETRIEVE old-leak negative control vs corrected native pages.

Runs on TWO distinct, exact source-author checkouts, supplied by CI. The old
#210 source must expose the complete mod-2^k sufficiency cue in real Core1A;
the corrected #242 source must not expose that cue anywhere in prerequisite
Core1/Core1A/Core1B visible/ARIA output or main Core2A preattempt support.
Uses only renderer-produced TEST HTML, original frozen Owner goldens and actual
Chromium. Old pages are QUARANTINED controls, never adopted for QRT.
Human Y prior knowledge, RETRIEVE-vs-APPLY and D4 band all remain unresolved.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import threading
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

OLD_REF="9faa52d499e071e9e6d4c419b5afdf5fbc044455"
CLEAN_REF="fa0b34d1a5ee0a8a7188c2c4871854e0b087d75c"
OLD_BLOB="27791fbd4735ecdbfda107b0087c16a68bfd8753"
CLEAN_BLOB="b9de3db24eb414075a50d0b36298a6306f26056b"
MANIFEST_BLOB="c4ed1576da7880c9aaf04cfb1cdb2c775e1f9d12"
REGISTRY_BLOB="591ba061b8771c30fdffc4506aa720ca9ba89335"
GOLDEN_BLOB="888678554c41257e6d96c802f0009983ccbb5328"
ROLES=("core1","core1a","core1b","core2a","core2b")
BP={
    "core1":"BP-CORE1-ORIENTATION@1.1.0",
    "core1a":"BP-CORE1A-CONSTRUCTION@1.8.0",
    "core1b":"BP-CORE1B-RECONSTRUCTION@1.1.0",
    "core2a":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
    "core2b":"BP-CORE2B-TRANSFER@1.1.0",
}
TEACH={
 "core1":["T14"],"core1a":["T02","T03","T11"],
 "core1b":["T06","T10","T12"],"core2a":["T05","T07"],
 "core2b":["T08","T09"]
}
OLD_DIFFERENCE_PATHS={
 "/buckets/0/conventions/1/statement",
 "/microtopics/0/inferential_jump",
 "/microtopics/0/teaching_path/2/action",
 "/microtopics/0/misconceptions/0/repair",
 "/microtopics/0/misconceptions/1/repair",
 "/relations/0/conditions/1",
 "/relations/0/derivation/2/action",
}

def check(value,why):
    if not value:raise AssertionError(why)

def load(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gitblob(root,path):
    return subprocess.check_output(
        ["git","hash-object",str(path.relative_to(root))],
        cwd=root,text=True).strip()
def rev(root):
    return subprocess.check_output(
        ["git","rev-parse","HEAD"],cwd=root,text=True).strip()

def changed_leaves(a,b,p=""):
    if a==b:return []
    if not isinstance(a,(list,dict)) or not isinstance(b,type(a)):
        return [p]
    if isinstance(a,list):
        if len(a)!=len(b):return [p]
        return [leaf for i,(x,y) in enumerate(zip(a,b))
                for leaf in changed_leaves(x,y,f"{p}/{i}")]
    if a.keys()!=b.keys():return [p]
    return [leaf for k in a for leaf in changed_leaves(a[k],b[k],f"{p}/{k}")]

class RoleDOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.roles=[];self.blueprints=[];self.slots=[];self.blocks=[];self.components=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        for key,dest in (
          ("data-g9-role",self.roles),
          ("data-blueprint-ref",self.blueprints),
          ("data-blueprint-slot",self.slots),
          ("data-g9-block",self.blocks),
          ("data-g9-component",self.components)
        ):
            if d.get(key):dest.append(d[key])
def parse(path):
    x=RoleDOM()
    x.feed(path.read_text(encoding="utf-8"))
    return x

def audit_checkout(root,kind):
    expected_ref=OLD_REF if kind=="old" else CLEAN_REF
    expected_blob=OLD_BLOB if kind=="old" else CLEAN_BLOB
    check(rev(root)==expected_ref,f"{kind}: not exact source-author commit")
    paths={
     "source":root/"TEST/imo-research/qrt-d4/retrieve-d4.package.json",
     "manifest":root/"TEST/products/imo203-qrt-d4-retrieve.manifest.json",
     "registry":root/"Shared/web/interactive-page-blueprints.v1.json",
     "golden":root/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json"}
    for name,expected in (
      ("source",expected_blob),("manifest",MANIFEST_BLOB),
      ("registry",REGISTRY_BLOB),("golden",GOLDEN_BLOB)):
        check(gitblob(root,paths[name])==expected,
              f"{kind}: source/manifest/registry/Owner golden drift {name}")
    package,manifest,registry,lock=map(load,paths.values())
    check(package["subject"]=="TEST" and package["status"]=="CANDIDATE",
          "not untouched authored TEST candidate")
    check(package.get("extensions",{}).get("grade9v3:qrt_admitted") is False,
          "unreviewed corrected/old TEST unexpectedly admitted")
    check(manifest["subject"]=="TEST"
          and manifest["selection"]["core2"]==[]
          and [x.lower() for x in manifest["output_roles"]]==list(ROLES),
          "wrong or authentic source selection")
    check(registry["registry_version"]=="1.17.0"
          and lock["fixture_id"]=="G-IMO-G9-FIVE-CORE-20261012",
          "not original registered blueprint or snapshot fixture")
    location=root/"build/imo182/qrt-d4-retrieve"/kind
    receipt=load(location/"render-receipt.json")
    check(receipt["renderer"]=="render_core/2" and receipt["mode"]=="PAGES"
          and receipt["gaps"]==[], "not zero-gap actual renderer")
    byid={x["id"]:x for x in registry["blueprints"]}
    evidence=[]
    for role in ROLES:
        path=location/(role+".html")
        original=next(x for x in lock["snapshots"] if x["role"]==role.upper())
        golden=paths["golden"].parent/original["path"]
        check(sha(golden)==original["sha256"],
              f"{kind}/{role}: original Owner snapshot bytes mutated")
        check(sha(path)==receipt["page_sha256"][role+".html"],
              f"{kind}/{role}: native HTML != renderer receipt")
        a,g=parse(path),parse(golden)
        bp_id,version=BP[role].split("@")
        bp=byid[bp_id]
        check(bp["status"]=="ACTIVE" and bp["version"]==version
              and bp["core_roles"]==[role.upper()],
              f"{kind}/{role}: blueprint no longer registered")
        check(a.blueprints==g.blueprints==[BP[role]]
              and a.roles[:1]==g.roles[:1]==[role.upper()],
              f"{kind}/{role}: role/blueprint not matching Owner original")
        check(a.slots==g.slots and a.components==g.components,
              f"{kind}/{role}: registered slot/component order differs from original")
        if role=="core1b":
            check(a.blocks==g.blocks and len(a.blocks)==13,
                  "Core1B teaching block order diverges")
        evidence.append({
          "role":role.upper(),"registered_blueprint":BP[role],
          "real_native_sha256":sha(path),
          "frozen_original_owner_sha256":original["sha256"],
          "native_receipt_match":True,"golden_slot_component_match":True,
          "technique_ids_to_review":TEACH[role],
          "human_golden_semantic_acceptance":"PENDING"})
    index=location/"index.html"
    check(sha(index)==receipt["page_sha256"]["index.html"],
          "sixth native index not matched by real render receipt")
    return package,manifest,receipt,evidence,location

class AssetServer(SimpleHTTPRequestHandler):
    def __init__(self,*args,repo_root=None,**kwargs):
        self.repo_root=Path(repo_root)
        super().__init__(*args,directory=str(self.repo_root),**kwargs)
    def translate_path(self,path):
        uri=unquote(urlsplit(path).path)
        for prefix in ("css","js","img","images","fonts","assets"):
            marker=f"/build/{prefix}/"
            if uri.startswith(marker):
                resolved=(self.repo_root/"public"/uri[len("/build/"):]).resolve()
                if resolved.is_relative_to((self.repo_root/"public").resolve()):
                    return str(resolved)
        return super().translate_path(path)
    def log_message(self,*args):pass

def save_screenshot(root,page,label,role,width,post=False):
    out=root/"build/imo182/qrt-d4-retrieve"/label/"protected-w-audit"
    out.mkdir(parents=True,exist_ok=True)
    dest=out/f"{role}-{width}" + ("-post" if post else "") # no Path + str
    return dest

def math_proof():
    def classes(n):
        return sorted({(k*k)%n for k in range(1,n,2)})
    sets={str(n):classes(n) for n in (4,8,16,128)}
    check(sets["4"]==[1] and sets["8"]==[1],
          "odd square small exponent wrong")
    check(sets["16"]==[1,9], "odd square modulo16 incorrect")
    check(sets["128"]==list(range(1,128,8)),
          "odd-square class iff modulo128 has wrong 16 classes")
    main=(9,17,33,49)
    check(all(x in sets["128"] for x in main),
          "stated main example correct roots absent")
    check(all(x%4 in sets["4"] for x in (5,9,13))
          and 5%8 not in sets["8"],
          "new Core2B mod4 transfer exception wrong")
    return {"odd_square_classes":sets,
            "main_sample_mod128":list(main),
            "transfer_mod4":[5,9,13],
            "5_not_square_mod8":True,
            "educational_prior_Y":"UNKNOWN",
            "academic_RETRIEVE_D4":"HOLD"}

def browser(root,kind,guard,reportdir):
    http=ThreadingHTTPServer(("127.0.0.1",0),
                             partial(AssetServer,repo_root=root))
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    views=[]
    old_leaks=[]
    try:
        with sync_playwright() as pw:
            b=pw.chromium.launch(headless=True,args=["--no-sandbox"])
            try:
                for role in ROLES:
                    for width in (390,768,1280):
                        page=b.new_page(viewport={"width":width,"height":900})
                        errors=[]
                        page.on("pageerror",lambda e:errors.append(str(e)))
                        page.on("requestfailed",lambda r:errors.append(r.url))
                        page.on("response",lambda r:errors.append(f"{r.status} {r.url}")
                                if r.status>=400 and urlsplit(r.url).path.lower().endswith(
                                    (".css",".js",".svg",".png",".jpg",".woff",".woff2")) else None)
                        url=f"http://127.0.0.1:{http.server_port}/build/imo182/qrt-d4-retrieve/{kind}/{role}.html"
                        response=page.goto(url,wait_until="load")
                        check(response is not None and response.status==200,
                              f"{kind}/{role}/{width}: source-real learner HTTP failure")
                        check(page.locator(f"html[data-g9-role='{role.upper()}']").count()==1
                              and page.locator("body[data-blueprint-ref]").get_attribute(
                                  "data-blueprint-ref")==BP[role],
                              f"{kind}/{role}: not original registered BP")
                        article=page.locator("article[data-g9-unit]").first
                        check(article.is_visible(),"no genuine learner article")
                        css=page.evaluate("""() => [...document.querySelectorAll(
                          'link[rel=stylesheet]')].map(e=>Boolean(e.sheet))""")
                        check(len(css)>=2 and all(css),f"{kind}/{role}: real CSS not loaded")
                        check(page.evaluate(
                          "() => document.documentElement.scrollWidth <= innerWidth + 2"),
                          f"{kind}/{role}/{width} learner horizontal overflow")
                        check(not errors,f"{kind}/{role}/{width}: CSS/JS error {errors}")
                        visible=article.inner_text()
                        aria=article.aria_snapshot()
                        matches=guard.cue_matches(visible+" "+aria)
                        observation={"role":role.upper(),"width":width,
                          "real_renderer_page":True,"site_stylesheets_loaded":True,
                          "golden_blueprint_ref":BP[role],
                          "protected_iff_cues":matches}
                        if role in ("core1","core1a","core1b"):
                            if kind=="old" and role=="core1a":
                                if matches:old_leaks.append((role,width,matches))
                                observation["source_old_negative_control"] = (
                                    "EXPECTED_PROTECTED_THEOREM_LEAK" if matches else
                                    "NEGATIVE_CONTROL_NOT_REPRODUCED")
                            elif kind=="corrected":
                                check(not matches,
                                      f"CORRECTED {role}/{width} LEAKED FULL HIGH-POWER IFF {matches}")
                                observation["prequestion_protected_iff"] = "NOT_EXPOSED"
                        if kind=="corrected" and role=="core2a":
                            check(not matches,
                                  f"CORRECTED Core2A before attempt leaks iff {matches}")
                            h2=article.get_by_role("button",name="Next hint")
                            check(h2.count()==1,"Core2A H2 learner trigger missing")
                            h2.click()
                            after_h2=article.inner_text()
                            after_ax=article.aria_snapshot()
                            check(not guard.cue_matches(after_h2+" "+after_ax),
                                  "Core2A H2 leak of full iff theorem")
                            observation["h2_protected_iff"]="NOT_EXPOSED"
                            gated=article.locator(
                               'details[data-g9-payload-ref*="after-attempt-hint-3"]')
                            check(gated.count()==1 and gated.get_attribute(
                                  "data-locked") is not None,
                                  "Core2A H3 not gated")
                            text=article.locator("textarea[data-g9-attempt]").first
                            commit=article.locator("button[data-g9-commit]").first
                            check(text.count()==1 and commit.count()==1,
                                  "Core2A lacks independent attempt")
                            commit.click()
                            check(gated.get_attribute("data-locked") is not None,
                                  "blank attempt unlocked H3")
                            text.fill("The odd-square necessary condition modulo8 "
                                      "may not suffice at every higher modulus; "
                                      "test the requested cases independently.")
                            commit.click()
                            check(gated.get_attribute("data-locked") is None,
                                  "written attempt did not unlock H3")
                            gated.locator("summary").click()
                            check(article.locator("[data-g9-after-attempt-hint]").is_visible(),
                                  "H3 did not appear after written attempt")
                            observation["blank_gate"]="PASS"
                            observation["written_attempt_h3"]="PASS"
                        if kind=="corrected" and role=="core1a" and width==390:
                            exit_card=article.locator(
                                '[data-g9-component="EXIT_RECALL"]').first
                            check(exit_card.count()==1 and "5 and9" in exit_card.inner_text(),
                                  "Core1A independent changed-modulus exit absent")
                            reply=exit_card.locator('textarea[data-g9-attempt]').first
                            gate=exit_card.locator("details[data-requires-attempt]").first
                            commit=exit_card.locator("button[data-g9-commit]").first
                            check(reply.count() and commit.count() and gate.count(),
                                  "Core1A independent exit commitment missing")
                            check(not gate.locator("[data-g9-payload-slot]").inner_text().strip(),
                                  "Core1A answer prematurely materialized")
                            commit.click()
                            check(gate.get_attribute("data-locked") is not None,
                                  "blank Core1A exit released answer")
                            reply.fill("Modulo16 residues 5 and 9 require separate existence checking.")
                            commit.click()
                            check(gate.get_attribute("data-locked") is None,
                                  "Core1A written exit didn't unlock")
                            observation["independent_exit"]="PASS"
                        if kind=="corrected" and role=="core1b" and width==390:
                            main=article.locator(
                                'details[data-g9-payload-ref*="reconstruct"]').first
                            boundary=article.locator(
                                'details[data-g9-attempt-stage="boundary"]').first
                            check(main.count()==1 and boundary.count()==1,
                                  "Core1B two independent reconstructions missing")
                            observation["two_separate_attempt_reveals_present"]=True
                        if kind=="corrected" and role=="core2b" and width==390:
                            check("The modulus is now 4 instead of 128" in visible
                                  and "a=5,9,13" in visible,
                                  "true changed modulus transfer not present")
                            gate=article.locator(
                                'details[data-g9-payload-ref="CORE2B-Q-D4-RETRIEVE-TRANSFER-review"]').first
                            check(gate.count() and not gate.locator(
                                '[data-g9-payload-slot]').inner_text().strip(),
                                "Core2B preattempt transfer answer leaked")
                            box=article.locator("[data-g9-attempt-box]").first
                            reply=box.locator("textarea[data-g9-attempt]").first
                            commit=box.locator("button[data-g9-commit]").first
                            commit.click()
                            check(gate.get_attribute("data-locked") is not None,
                                  "Core2B blank attempt unlocked transfer")
                            reply.fill("Every odd-square residue modulo4 is 1; "
                                      "5,9,13 qualify modulo4 but 5 fails modulo8.")
                            commit.click()
                            check(gate.get_attribute("data-locked") is None,
                                  "Core2B written transfer did not unlock")
                            gate.locator("summary").click()
                            check("5,9,13" in gate.locator(
                                  "[data-g9-payload-slot]").inner_text(),
                                  "Core2B changed boundary answer not verified")
                            observation["blank_and_written_transfer"]="PASS"
                        # Screenshot actual native pages, NOT a hand-crafted mock.
                        folder=reportdir/"old_negative_control" if kind=="old" else reportdir/"corrected"
                        filename=folder/f"{role}-{width}.png"
                        filename.parent.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(filename),full_page=True,animations="disabled")
                        observation["screenshot_sha256"]=sha(filename)
                        views.append(observation)
                        page.close()
            finally:b.close()
    finally:
        http.shutdown();http.server_close();thread.join(timeout=5)
    check(len(views)==15,f"{kind}: not 15 genuine native viewport observations")
    if kind=="old":
        check(len(old_leaks)==3,
              f"old SHA-VALID Core1A failure not reproduced at three widths: {old_leaks}")
    else:
        check(not old_leaks,"corrected baseline shouldn't reproduce prior leak")
    return views,old_leaks

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--old",required=True,type=Path)
    ap.add_argument("--corrected",required=True,type=Path)
    args=ap.parse_args()
    old=args.old.resolve();corrected=args.corrected.resolve()
    package_old,manold,recold,roleold,_=audit_checkout(old,"old")
    package_new,mannew,recnew,rolenew,_=audit_checkout(corrected,"corrected")
    changed=set(changed_leaves(package_old,package_new))
    check(changed==OLD_DIFFERENCE_PATHS,
          "old-to-corrected source edit scope changed: "+repr(changed))
    check(manold==mannew,"negative control changed manifest not only teaching source")
    # Reuse the source author's own pinned protected-W safety oracle, not
    # another quietly invented definition of what counts as a leaked iff.
    guard_path=corrected/"tests/imo203_d4_w_guard.py"
    check(gitblob(corrected,guard_path)=="1b4fd7ec2547070f5bdbeb44b3c15e21eab09017",
          "guard version drift: rerun explicit W review")
    spec=importlib.util.spec_from_file_location("imo203_d4_w_guard",guard_path)
    guard=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    out=corrected/"build/imo182/qrt-d4-retrieve/r7-crossrole-w"
    math=math_proof()
    old_pages,old_leaks=browser(old,"old",guard,out)
    current_pages,_=browser(corrected,"corrected",guard,out)
    receipt_deltas={role:(
        recold["page_sha256"][role+".html"],
        recnew["page_sha256"][role+".html"]
    ) for role in ROLES}
    check(any(a!=b for a,b in receipt_deltas.values()),
          "corrected native roles unexpectedly byte-equal to old leaky bundle")
    report={
      "schema":"imo182-retrieve-d4-old-vs-repaired-native-w/v1",
      "cell":"QRT-RETRIEVE-D4",
      "old_source_commit":OLD_REF,
      "old_source_blob":OLD_BLOB,
      "old_artifact_id":11823696124,
      "old_status":"DO_NOT_QRT_ADOPT_VALID_SHA_BUT_THEOREM_LEAK",
      "repaired_source_commit":CLEAN_REF,
      "repaired_source_blob":CLEAN_BLOB,
      "repaired_native_prior_artifact_id":11842190265,
      "unchanged_manifest_git_blob":MANIFEST_BLOB,
      "unchanged_blueprint_registry_git_blob":REGISTRY_BLOB,
      "unchanged_exact_owner_golden_lock_blob":GOLDEN_BLOB,
      "exactly_seven_source_semantic_edits":sorted(changed),
      "old_six_native_hashes":recold["page_sha256"],
      "corrected_six_native_hashes":recnew["page_sha256"],
      "old_five_golden_role_snapshots":roleold,
      "corrected_five_golden_role_snapshots":rolenew,
      "old_native_core1a_accessible_full_iff_negative_control":old_leaks,
      "old_precommit_native_15_browser_viewports":old_pages,
      "repaired_precommit_native_15_browser_viewports":current_pages,
      "independent_integer_modular_math":math,
      "structural_golden_not_sufficient":"TRUE_OLD_LEAK_WITH_VALID_ROLE_STRUCTURE",
      "qualified_academic_retrieve_vs_apply_justify_explain":"PENDING",
      "independent_prior_learning_Y":"UNKNOWN",
      "all_12_HSPM":"PENDING_QUALIFIED_REVIEW",
      "owner_qrt_decision_id":None,
      "owner_accepted":False,
      "o3_blueprint_defect_demonstrated":False,
      "old_source_adoptable":False,
      "corrected_source_academically_accepted":False,
      "original_exam_core2_admitted":0,
      "fixture_changed":False,
      "release_authorized":False,
    }
    out.mkdir(parents=True,exist_ok=True)
    dest=out/"retrieve-d4-real-old-vs-corrected-native-w.v1.json"
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                    encoding="utf-8")
    print("O1 RETRIEVE-D4: old registered/Core1A native SHA-VALID negative control "
          "reproduced full theorem leak at three viewport sizes")
    print("O1 RETRIEVE-D4: corrected five registered roles, exact Owner frozen "
          "slot/component goldens, 6 native SHA receipts, 15 Chromium viewports PASS")
    print("O1 RETRIEVE-D4: source 7 semantic edits verified; H2/AX W protected "
          "by tested guard, main/transfer math PASS, Y UNKNOWN")
    print("ACADEMIC RETRIEVE-D4/QRT/OWNER remains HOLD: 0/28 accepted")
    print("REPORT "+str(dest))

if __name__=="__main__":
    main()
