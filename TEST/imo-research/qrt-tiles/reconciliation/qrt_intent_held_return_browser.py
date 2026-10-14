#!/usr/bin/env python3
"""R8 held-copy real Chromium assisted-return proof, NO renderer/golden promotion."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import threading
from functools import partial
from http.server import ThreadingHTTPServer

from playwright.sync_api import sync_playwright

from qrt_intent_contract import ContractError, ensure, read_json, sha256
from qrt_intent_w_path_audit import RootAssets
from qrt_intent_held_return_copy import adapt_pages


def browser_proof(browser, source_root: Path, held: Path,
                  native_contract: dict) -> dict:
    receipt = read_json(held / "held-adaptation-receipt.json")
    assert receipt["cell_id"] == native_contract["cell_id"]
    assert receipt["status"] == "LOCAL_TEST_CANDIDATE_ADAPTED_NOT_PUBLISHED"
    for name, digest in receipt["adapted_sha256"].items():
        ensure(sha256(held / name) == digest,
               "HELD_COPY_BYTES_CHANGED", name)
    ensure(not (held/"render-receipt.json").exists(),
           "HELD_COPY_MASQUERADES_AS_NATIVE")
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(RootAssets, source_root=source_root))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    relative = held.resolve().relative_to(source_root.resolve()).as_posix()
    base = f"http://127.0.0.1:{server.server_port}/{relative}"
    context = browser.new_context(viewport={"width":390,"height":900})
    logs = []
    try:
        page=context.new_page()
        page.on("pageerror", lambda e: logs.append(str(e)))
        def visit(url, role):
            resp=page.goto(base+"/"+url, wait_until="load")
            ensure(resp is not None and resp.status==200,
                   "HELD_BROWSER_404", url)
            ensure(page.locator("html").get_attribute("data-g9-role")==role and
                   page.locator("html").get_attribute("data-g9-held-adapter")==
                       "R8-TEST-COPY",
                   "HELD_BROWSER_WRONG_ROLE", role)
            ensure(page.locator("[data-g9-held-banner]").count()==1,
                   "HELD_BANNER_MISSING", role)

        qid=receipt["primary_question_id"]
        mic=receipt["microtopic_id"]
        visit("core2a.html", "CORE2A")
        art=page.locator(f"article[data-g9-unit='{qid}']")
        link=art.locator("[data-g9-held-source-concept-link]")
        ensure(link.count()==1 and not link.is_visible(),
               "HELD_PRECOMMIT_LEAK")
        solution=art.locator("details[data-requires-attempt]").first
        ensure(solution.count()==1 and
               solution.get_attribute("data-locked") is not None,
               "HELD_PRECOMMIT_SOLUTION_UNLOCKED")
        # We do not enter mathematics or award marks. The sentinel only tests
        # draft round-trip storage through real Chromium.
        answer=art.locator("textarea[data-g9-attempt]").first
        commit=art.locator("button[data-g9-commit]").first
        ensure(answer.count()==commit.count()==1,
               "HELD_RESPONSE_CONTROL_NOT_UNIQUE")
        commit.click()
        ensure(not link.is_visible() and
               solution.get_attribute("data-locked") is not None,
               "HELD_BLANK_ATTEMPT_UNLOCKED")
        sentinel="R8_NAV_SENTINEL_NOT_A_MATH_SOLUTION"
        answer.fill(sentinel)
        commit.click()
        ensure(link.is_visible() and
               solution.get_attribute("data-locked") is None,
               "HELD_POSTCOMMIT_CONCEPT_LINK_NOT_VISIBLE")
        ensure("assisted" in link.inner_text().lower(),
               "HELD_CONTEXT_LINK_MISSING_ASSISTANCE_LABEL")
        link.click()
        page.wait_for_load_state("load")
        ensure(page.locator("html").get_attribute("data-g9-role")=="CORE1A",
               "HELD_CONCEPT_NOT_REACHED")
        ensure(page.locator("article").first.get_attribute("data-g9-unit")==mic,
               "HELD_CONCEPT_WRONG_TARGET")
        ensure(page.url.split("#")[-1]==mic,
               "HELD_CONCEPT_FRAGMENT_MISMATCH")
        ret=page.locator("[data-g9-held-return-link]")
        ensure(ret.count()==1 and ret.is_visible() and
               ret.get_attribute("data-g9-held-return-link")==qid and
               "assisted" in ret.inner_text().lower(),
               "HELD_TARGETED_RETURN_MISSING")
        ret.click()
        page.wait_for_load_state("load")
        art=page.locator(f"article[data-g9-unit='{qid}']")
        ensure(page.locator("html").get_attribute("data-g9-role")=="CORE2A" and
               art.count()==1,"HELD_WRONG_RETURN_QUESTION")
        ensure(art.locator("textarea[data-g9-attempt]").first.input_value()==sentinel,
               "HELD_DRAFT_NOT_RESTORED")
        ensure(art.get_attribute("data-g9-assisted")=="1" and
               "CONCEPT_NAV" in (art.get_attribute("data-g9-assistance") or ""),
               "HELD_ASSISTANCE_NOT_RESTORED")
        ensure(art.get_attribute("data-attempted") is None and
               art.locator("details[data-requires-attempt]").first.get_attribute(
                   "data-locked") is not None,
               "HELD_RETURN_PREMATURELY_UNLOCKED_SOLUTION")
        # The return link has not auto-awarded another attempt or release.
        page.close()
        fresh=context.new_page()
        resp=fresh.goto(base+"/core1a.html?g9-held-return="+qid+
                        "&g9-held-concept=WRONG#"+mic, wait_until="load")
        ensure(resp and resp.status==200 and
               fresh.locator("[data-g9-held-return-link]").count()==0,
               "HELD_TAMPERED_CONCEPT_TOKEN_GOT_RETURN")
        fresh.close()
        ensure(not logs,"HELD_JS_PAGEERROR",repr(logs))
        return {
            "schema":"imo182-r8-held-navigation-browser-proof/v1",
            "cell_id":receipt["cell_id"],
            "source_sha256":receipt["original_sha256"],
            "adapted_sha256":receipt["adapted_sha256"],
            "clicks":["blank_attempt_rejected",
                      "valid_attempt_exposes_concept_link",
                      "context_link_to_exact_microtopic",
                      "same_question_assisted_return",
                      "wrong_concept_token_has_no_return"],
            "precommit_link_hidden":True,
            "solution_lock_after_return":True,
            "source_draft_restored":True,
            "return_marked_assisted":True,
            "independent_mastery":False,
            "academic_qrt":"NOT_RUN",
            "owner_acceptance":False,
            "release":"HOLD",
            "role_pages_are_copy_only":True,
        }
    finally:
        context.close()
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def negative_mutations(source_root:Path,original_dir:Path,
                       native_contract:dict) -> dict:
    n=native_contract
    orig={p.name:p.read_text(encoding="utf-8")
          for p in original_dir.glob("*.html")}
    pkg=read_json(source_root/n["provenance"]["source_path"])
    man=read_json(source_root/n["provenance"]["manifest_path"])
    checks=[]
    def expect(label, mutate):
        args=[copy.deepcopy(n),source_root,original_dir,
              copy.deepcopy(man),copy.deepcopy(pkg),dict(orig)]
        mutate(args)
        try:
            adapt_pages(*args)
        except (ContractError, ValueError) as exc:
            checks.append({"name":label,
                           "caught":True,
                           "error_code":str(exc).split(":",1)[0]})
        else:
            raise AssertionError("HELD_BAD_MUTATION_ACCEPTED: "+label)
    expect("changed_original_html",lambda a:a[5].__setitem__(
        "core2a.html",a[5]["core2a.html"].replace(
            "data-g9-attempt-box","data-g9-attempt-box-drift",1)))
    expect("changed_manifest_question",lambda a:a[3]["selection"].__setitem__(
        "core2a",["NONEXISTENT-Q"]))
    expect("swapped_primary_question",lambda a:a[0]["source_crux"]["primary"].__setitem__(
        "question_id","WRONG-PRIMARY"))
    expect("alien_concept_capability",lambda a:a[4]["microtopics"][0].__setitem__(
        "primary_capability_ref","WRONG-CAPABILITY"))
    expect("already_adapted",lambda a:a[5].__setitem__(
        "core1a.html",a[5]["core1a.html"].replace(
            "<html ","<html data-g9-held-adapter=\"ALREADY\" ",1)))
    expect("wrong_selected_role_list",lambda a:a[3].__setitem__(
        "output_roles",["CORE1A","CORE2A"]))
    return {"mutations":checks,"negative_controls_pass":len(checks)==6}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("source-root","native-output","native-contract","held-output","out"):
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    n=read_json(a.native_contract)
    mutations=negative_mutations(a.source_root,a.native_output,n)
    receipt=read_json(a.held_output/"held-adaptation-receipt.json")
    ensure(receipt["cell_id"]==n["cell_id"],"HELD_PROOF_CELL_MISMATCH")
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
        try:
            proof=browser_proof(browser,a.source_root,a.held_output,n)
        finally:
            browser.close()
    proof["negative_mutations"]=mutations
    ensure(proof["independent_mastery"] is False and
           proof["owner_acceptance"] is False and
           proof["academic_qrt"]=="NOT_RUN" and
           proof["release"]=="HOLD",
           "HELD_ACCREDITATION_FORBIDDEN")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(proof,indent=2,ensure_ascii=False)+"\n",
                     encoding="utf-8")
    print(f"{proof['cell_id']}: held-only real assisted return PASS, "
          "six negative mutations caught, native/academic/Owner release HOLD")


if __name__=="__main__":
    main()
