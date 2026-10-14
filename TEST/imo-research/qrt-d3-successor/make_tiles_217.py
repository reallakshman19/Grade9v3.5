#!/usr/bin/env python3
"""Generate seven unsigned D3 protocol tiles, academic packets and linked 7x4 review.
Administrative review HTML only; never a replacement Core renderer.
"""
import hashlib
import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "TEST/imo-research/qrt-d3-successor"
OUT = ROOT / "build/imo182-qrt/d3-successor/m3"
REPO = "https://github.com/reallakshman19/Grade9v3.5"
ROLES = ["CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"]
DEMANDS = ["RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"]
ASKS = ["H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3"]
BANDS = {"D1":200,"D2":201,"D3":217,"D4":203}
BP = {"CORE1":"BP-CORE1-ORIENTATION@1.1.0",
      "CORE1A":"BP-CORE1A-CONSTRUCTION@1.8.0",
      "CORE1B":"BP-CORE1B-RECONSTRUCTION@1.1.0",
      "CORE2A":"BP-CORE2A-SUPPORTED-APPLICATION@1.1.0",
      "CORE2B":"BP-CORE2B-TRANSFER@1.1.0"}
CRUX = {
 "retrieve":("most-specific classification from sufficient diagonal certificates",
             "APPLY-D2: the stem gives diagonal test method",
             "Rhombus, not square; transfer square iff p=4"),
 "explain":("connect sign-loss under squaring to original principal-root range",
            "EXPLAIN-D2: stem names causal ingredients",
            "Only x=4; absolute-value transfer x=-1,4"),
 "apply":("combine per-prime ceiling thresholds from two distinct powers",
          "APPLY-D2 if learnt valuation rule makes route routine",
          "least n=60; swapped powers h=90"),
 "model":("independently formulate common positive power and multiplier equation",
          "APPLY-D2: stem announces shared quantity and offset multiplier",
          "u=3/2; real transfer solution iff c>0"),
 "represent":("translate spatial reachability to intersection of path sets",
              "APPLY-D2 if set model is supplied; SYNTHESIZE secondary",
              "19 avoid both; moved-Q transfer 10"),
 "synthesize":("join AP/digit-sum/divisibility bounds in nonoverlapping cases",
               "APPLY-D2 if case model is scripted",
               "14 divisible by9; 20 divisible by6"),
 "justify":("reject 6 implies 12 and prove exact iff modular warrant",
            "JUSTIFY-D2 if residue argument routine; D4 if novel warrant",
            "12|P iff n mod4 !=1; 24|P iff n even or n mod8=7")
}
COGNITIVE_MOVES = {
 "retrieve":{"X":"Classifying by appearance or treating perpendicular diagonals alone as sufficient for square",
             "Z":"Prove both diagonals bisect; establish rhombus from perpendicular bisectors and exclude square using unequal diagonal lengths",
             "W":"Independently select sufficient diagonal certificates and exclude the narrower square class"},
 "explain":{"X":"Treating a root of the squared equation as automatically solving the original",
            "Z":"Show squaring is one-way here; apply principal-root range and verify candidates in original",
            "W":"Explain the exact sign/implication failure and reject x=-1 on the unsquared equation"},
 "apply":{"X":"Applying an lcm of divisors directly to n or ignoring distinct powers n² and n³",
          "Z":"Derive prime valuation ceilings separately and combine maximum lower bounds for leastness",
          "W":"Choose and intersect both power-dependent per-prime lower bound conditions; prove leastness"},
 "model":{"X":"Missing the linked exponential bases and additive offset model",
          "Z":"Choose t=16^u=4^(2u)>0, form 4t=t+192 and reverse-map/check",
          "W":"Independently identify the common positive power and coefficient relationship: this is compromised by the original stem cue"},
 "represent":{"X":"Subtracting through-point route families twice without accounting for paths through both",
               "Z":"Use reachability/order to decide whether the two path sets intersect; count intersection then complement",
               "W":"Independently translate checkpoint geometry into path-family intersection/disjointness"},
 "synthesize":{"X":"Omitting decreasing or constant AP digits, admitting leading zero, or misapplying digit-sum divisibility",
                "Z":"Relate AP to H+U=2T and digit sum=3T; enumerate signed gaps under all decimal bounds",
                "W":"Combine three constraints into a complete disjoint signed-gap count and verify boundaries"},
 "justify":{"X":"Inferring 12-divisibility from guaranteed divisibility by 6 for three consecutive factors",
             "Z":"Provide n=1 counterexample, then prove an iff condition by modulo-4 / powers-of-two cases",
             "W":"Derive necessary and sufficient residue classes for 12 | n(n+1)(n+2), not merely counterexamples"}
}
REVIEW_HELP = {
 "H1":"Clarifies X","H2":"Connects X to demonstrated Y",
 "H3":"Opens Z after commitment while preserving W",
 "S1":"Shows X safely","S2":"Shows Y in target representation",
 "S3":"Approaches Z without W","P1":"Before-attempt W protection",
 "P2":"Concept links teach X/Y","P3":"Move validity and independent check",
 "M1":"Plausible misconception","M2":"Diagnose misconception versus slip",
 "M3":"Shows wrong-route failure and replacement"
}

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def blob(p):
    return subprocess.check_output(["git","hash-object",str(p.relative_to(ROOT))],
                                   cwd=ROOT, text=True).strip()

def need(ok,why):
    if not ok:
        raise AssertionError(why)

def output_json(p,obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def reviewer_packet(tile,q,t):
    lines=["# "+tile["cell_id"]+" — UNSIGNED independent subject/QRT reviewer packet",
      "Issue #217, source PR #193; TEST-only authored mathematics. No self-signature or acceptance.",
      "Source Git blob: "+tile["source"]["verified_sha"],
      "Manifest Git blob: "+tile["generation"]["manifest_blob_sha"],
      "Candidate competing classification: "+tile["cognitive"]["primary_vs_alternative"],
      "Learner W: "+tile["cognitive"]["W"],
      "Y: NOT_OBSERVED (no actual learner profile).",
      "## Exact authored primary stem",q["stem"],
      "## Author's solution to challenge",q["answer"].get("summary",""),
      *q["answer"].get("reasoning",[]),
      "Independent main check to reproduce: "+q.get("independent_check",{}).get("statement","PENDING"),
      "## Exact authored transfer stem",t["stem"],
      "## Author's transfer solution to challenge",t["answer"].get("summary",""),
      *t["answer"].get("reasoning",[]),
      "Independent transfer check: "+t.get("independent_check",{}).get("statement","PENDING"),
      "## Cognitive demand and difficulty: unaccepted author hypothesis",
      json.dumps(q.get("difficulty",{}),ensure_ascii=False,indent=2),
      "## Role behavior to falsify",
      "Core1 orientation; Core1A independent construction/exit; Core1B fresh reconstruction and changed exception; Core2A H1/H2 precommit, blank attempt blocked, H3 post-nonblank; Core2B genuine changed transfer.",
      "Inspect actual native CSS/JS/SVG, accessible title and descriptions, 390/768/1280 legibility, H1/H2/H3 visible strings, premature W or solution disclosure. Human visual/ARIA/A4 remains pending.",
      "## Independent H/S/P/M twelve judgments — all PENDING",
      *["- [ ] "+a+": "+REVIEW_HELP[a]+" — reviewer verdict/reason: PENDING" for a in ASKS],
      "Reviewer name, qualifications, conflict of interest, independence, date: PENDING.",
      "Independent academic verdict (ACCEPT/REVISE/RECLASSIFY/REJECT): PENDING.",
      "Separate Owner per-cell decision and ID: PENDING / null.",
      "Original golden exact bytes remain immutable. Cross-question semantic technique is not HTML-byte equality.",
      "Rights, new Owner fixture, merge, public release: NOT AUTHORIZED."
    ]
    return "\n\n".join(lines)+"\n"

def viewer(payload):
    data=json.dumps(payload,ensure_ascii=False).replace("<","\\u003c")
    pre="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Issue 217 D3 source-safe QRT 7x4 review</title>
<style>
:root{font:15px/1.5 system-ui,sans-serif;color:#20344a;background:#f4f7fb}*{box-sizing:border-box}
body{margin:0}header,main,footer{max-width:1160px;margin:auto;padding:18px}
h1{font-size:clamp(1.5rem,3vw,2.3rem)}h2{font-size:1.13rem}
a{color:#14638a}a:focus-visible,button:focus-visible{outline:3px solid #b17125;outline-offset:2px}
.notice{background:#fff6e6;border-left:4px solid #ad7626;padding:12px}
.layout{display:grid;grid-template-columns:minmax(460px,1.1fr) minmax(320px,.9fr);gap:16px}
.scroll{overflow:auto}.panel{background:white;border:1px solid #d8e1ea;border-radius:10px;padding:14px}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #d8e1ea;padding:7px;text-align:left}
th{background:#e8eff5}button{font:inherit;cursor:pointer}
.cell{width:100%;min-height:57px;text-align:left;background:#f8fcff;border:1px solid #b4cbdb;border-radius:5px;padding:7px}
.cell[aria-pressed=true]{background:#d9eff7;border-color:#13668d}.cell[data-held=true]{border-left:5px solid #ae782f;background:#fff8eb}
.cell small{display:block;font-size:.73rem;color:#647584}
dt{font-weight:700;color:#536477}dd{margin:0 0 8px;overflow-wrap:anywhere}
.sha{font:12px/1.4 ui-monospace,monospace;overflow-wrap:anywhere}
.role{border:1px solid #d9e2eb;border-radius:6px;padding:9px;margin:7px 0}.role small{display:block}
.links a{display:block;margin:6px 0}.asks{display:grid;grid-template-columns:repeat(4,1fr);gap:5px}
.asks span{background:#edf3f8;border-radius:4px;padding:6px;font-size:.77rem}
footer{border-top:1px solid #d8e1ea;font-size:.85rem;color:#52647a}
@media(max-width:850px){.layout{display:block}.panel{margin-top:16px}}
</style></head><body><header><p>Grade9v3.5 · #182/#202/#217 · TEST-only review index</p>
<h1>QRT seven demands × four bands — D3 successor</h1>
<p class="notice"><strong>No academic or Owner acceptance.</strong> MODEL-D3 and RETRIEVE-D3 remain on semantic hold. Other five are provisional engineering candidates. This navigation does not render learner Core pages.</p>
<p><a href="https://github.com/reallakshman19/Grade9v3.5/issues/217">Successor issue #217</a> · <a href="https://github.com/reallakshman19/Grade9v3.5/pull/224">Draft PR #224</a> · <a href="https://github.com/reallakshman19/Grade9v3.5/blob/agent/182-q003-qrt-golden-tile-6acda00e/TEST/imo-research/qrt-tiles/q003-model-d2/index.html">Existing QRT 7×4 reference</a></p></header>
<main class="layout"><section><h2>Canonical 7×4 matrix</h2><p>D3 buttons open source-pinned evidence; the other 21 cells link to their existing band workstream issues.</p>
<div class="scroll" role="region" aria-label="QRT matrix" tabindex="0"><table><thead><tr><th scope="col">Demand</th><th scope="col">D1</th><th scope="col">D2</th><th scope="col">D3</th><th scope="col">D4</th></tr></thead><tbody id="matrix"></tbody></table></div><p id="selection" aria-live="polite"></p></section>
<section class="panel"><h2 id="selected">Select a D3 candidate</h2><dl>
<dt>Technical status</dt><dd id="status">—</dd>
<dt>Source blob</dt><dd id="source" class="sha">—</dd>
<dt>Manifest blob</dt><dd id="manifest" class="sha">—</dd>
<dt>Protected W</dt><dd id="work">—</dd>
<dt>Alternative</dt><dd id="alternative">—</dd>
<dt>Golden</dt><dd id="golden">—</dd>
<dt>Academic / Owner</dt><dd id="decision">PENDING</dd></dl>
<h2>Five native role SHA-256</h2><div id="roles"></div>
<h2>Primary evidence</h2><div id="links" class="links"></div>
<h2>Twelve review asks</h2><div class="asks" id="asks"></div>
<p>Historical artifacts for held candidates are not current adoption. Distinct D3 questions are benchmarked against original Owner golden pedagogical technique, never byte-equality.</p></section></main>
<footer>All seven TEST only, no source-private Core2, no merge or publication. H1–M3 reviewer verdicts PENDING and Owner decision IDs null.</footer>
<script id="data" type="application/json">"""
    post="""</script><script>
const D=JSON.parse(document.getElementById("data").textContent);
const $=id=>document.getElementById(id);
const demands=["RETRIEVE","EXPLAIN","APPLY","MODEL","REPRESENT","SYNTHESIZE","JUSTIFY"];
const roles=["CORE1","CORE1A","CORE1B","CORE2A","CORE2B"];
const bands={D1:200,D2:201,D3:217,D4:203};
const asks=["H1","H2","H3","S1","S2","S3","P1","P2","P3","M1","M2","M3"];
function add(tag,parent,text){const e=document.createElement(tag);e.textContent=text;parent.append(e);return e;}
function link(parent,text,url){const a=add("a",parent,text);a.href=url;if(url.startsWith("https:")){a.target="_blank";a.rel="noopener noreferrer";}return a;}
function show(cell){const t=D[cell];if(!t)throw Error("Missing D3 tile "+cell);
$("selected").textContent=cell;$("selection").textContent=cell+" · "+t.status_dimensions.technical;
$("status").textContent=t.status_dimensions.technical;$("source").textContent=t.source.verified_sha;
$("manifest").textContent=t.generation.manifest_blob_sha;$("work").textContent=t.cognitive.W;
$("alternative").textContent=t.cognitive.primary_vs_alternative;$("golden").textContent=t.golden.id+" · semantic technique only";
$("decision").textContent="Qualified reviewer PENDING; Owner decision null";
$("roles").replaceChildren();for(const r of roles){const x=t.blueprints.find(z=>z.role===r);const box=add("div",$("roles"),r+" · "+x.registered_blueprint);box.className="role";
const h=add("small",box,x.page_sha256);h.className="sha";
if(x.native_link)link(box,"Open authentic native "+r+" (in extracted artifact)",x.native_link);
else add("small",box,"Held: historical archive only, no new adoption");}
$("links").replaceChildren();
link($("links"),"Pinned original source",t.evidence.source_url);
link($("links"),"Pinned manifest",t.evidence.manifest_url);
link($("links"),"Historical native artifact",t.generation.historical_artifact_url);
link($("links"),"Protocol JSON",t.viewer.tile_json);
link($("links"),"Unsigned academic reviewer packet",t.viewer.packet_url);
link($("links"),"D3 successor issue", "https://github.com/reallakshman19/Grade9v3.5/issues/217");
$("asks").replaceChildren();for(const a of asks)add("span",$("asks"),a+" · PENDING");
for(const b of document.querySelectorAll("button[data-cell]"))b.setAttribute("aria-pressed",String(b.dataset.cell===cell));
}
for(const d of demands){const tr=document.createElement("tr"),heading=add("th",tr,d);heading.scope="row";
for(const band of Object.keys(bands)){const td=document.createElement("td");
if(band==="D3"){const id="QRT-"+d+"-D3",button=add("button",td,d+" D3");button.type="button";button.className="cell";button.dataset.cell=id;button.dataset.held=String(d==="RETRIEVE"||d==="MODEL");button.setAttribute("aria-pressed","false");
add("small",button,button.dataset.held==="true"?"SEMANTIC HOLD":"PROVISIONAL");
button.addEventListener("click",()=>show(id));}
else link(td,band+" #"+bands[band],"https://github.com/reallakshman19/Grade9v3.5/issues/"+bands[band]);
tr.append(td);}$("matrix").append(tr);}
show("QRT-EXPLAIN-D3");
</script></body></html>"""
    return pre+data+post

def main():
    inv=load(SRC/"m0-adoption.v1.json")
    archives=load(SRC/"historical-held-receipts.v1.json")
    m1=load(ROOT/"build/imo182-qrt/d3-successor/m1-evidence.v1.json")
    need(m1["quality_claim"]=="M1_NATIVE_STRUCTURAL_ONLY","M1 not verified")
    lock=load(ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json")
    originals={r["role"]:r for r in lock["snapshots"]}
    for r in lock["snapshots"]:
        need(digest(ROOT/"golden/units/G-IMO-G9-FIVE-CORE-20261012"/r["path"])==r["sha256"],"frozen golden altered")
    need(set(inv["holds"])=={"model","retrieve"},"semantic hold changed")
    m1_by_id={r["cell"]:r for r in m1["evidence"]}
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    view={}
    for row in inv["all_7_cells"]:
        d=row["demand"];cell=row["cell"]
        source=ROOT/row["source_path"];manifest=ROOT/row["manifest_path"]
        need(blob(source)==row["source_blob_sha"],cell+" source changed")
        need(blob(manifest)==row["manifest_blob_sha"],cell+" manifest changed")
        pkg=load(source);man=load(manifest)
        need(man["selection"]["core2"]==[] and pkg["extensions"]["grade9v3:qrt_admitted"] is False,"source custody issue")
        question=next(q for q in pkg["questions"] if q["id"]==row["primary_id"])
        transfer=next(q for q in pkg["questions"] if q["id"]==man["selection"]["core2b"][0])
        held=d in inv["holds"];mr=m1_by_id[cell]
        if held:
            need(mr["build"]=="SEMANTIC_HOLD_NO_RENDER","hold wrongly rendered")
            historical=archives["records"][d]
            need(historical["semantic_hold"]==row["status"],"held status discrepancy")
            hashes=historical["page_sha256"]
            tech="HISTORIC_ARCHIVE_ONLY_SEMANTIC_HOLD"
        else:
            need(mr["build"]=="NATIVE_RENDER_RECEIPT_AND_GOLDEN_SLOT_PASS","native not verified")
            hashes=mr["page_sha256"]
            tech="M1_NATIVE_STRUCTURAL_PASS__ACADEMIC_PENDING"
        need(len(hashes)==6 and all(len(v)==64 for v in hashes.values()),cell+" SHA incomplete")
        roles=[{"role":role,"registered_blueprint":BP[role],
           "page_sha256":hashes[role.lower()+".html"],
           "original_golden_sha256":originals[role]["sha256"],
           "native_link":None if held else "../../d3/"+d+"/"+role.lower()+".html",
           "pedagogical_review":"PENDING_INDEPENDENT"} for role in ROLES]
        c=CRUX[d]
        tile={
          "schema":"imo-qrt-cell-evidence/v1","template":False,
          "cell_id":cell,"band_issue":202,"successor_issue":217,
          "original_question_or_authored_id":question["id"],"primary_demand":d.upper(),"band":"D3",
          "status_dimensions":{"technical":tech,"renderer_verified":not held,
             "technique_review":"STRUCTURAL_ONLY" if not held else "HISTORIC_ONLY",
             "academic_review":"PENDING_INDEPENDENT","owner_qrt_accepted":False,
             "owner_golden_designated":False,"release":"NOT_AUTHORIZED"},
          "source":{"classification":"AUTHORED_TEST","path":row["source_path"],
                    "verified_sha":row["source_blob_sha"],"custody":"WHOLLY_AUTHORED_TEST_ONLY",
                    "rights":"AUTHORED_TEST_ONLY_NO_PUBLIC_CORE2","question_stem_embedded":False},
          "cognitive":{"X":COGNITIVE_MOVES[d]["X"],
                       "Y":"NOT_OBSERVED_NO_LEARNER_PROFILE",
                       "Z":COGNITIVE_MOVES[d]["Z"],"W":COGNITIVE_MOVES[d]["W"],
                       "primary_vs_alternative":c[1],
                       "adjacent_band_reason":"D3 needs unsupplied significant bridge; D2 short connection; D4 novel model or warrant",
                       "difficulty_five_component_evidence":{"author_proposal":question["difficulty"],
                              "qualified_verdict":"PENDING_INDEPENDENT"}},
          "blueprints":roles,
          "generation":{"repo_commit_sha":head if not held else None,
             "source_original_commit_sha":inv["pinned_source_head"],
             "manifest_path":row["manifest_path"],"manifest_blob_sha":row["manifest_blob_sha"],
             "renderer_version":"render_core/2","registry_blob_sha":inv["blueprint_registry_git_blob"],
             "mode":"PAGES","held_to":"REFERENCE","gaps":0 if not held else "HISTORIC_ZERO_GAPS_ONLY",
             "historical_artifact_url":row["historical_scoped_workflow"]+"/artifacts/"+str(row["historical_artifact_id"]),
             "html":[{"name":k,"sha256":v,"verified_context":"M1_CURRENT_NATIVE" if not held else "HISTORIC_PR193_RECEIPT"} for k,v in hashes.items()],
             "six_html_sha_verified":not held},
          "golden":{"kind":"IMMUTABLE_OWNER_SNAPSHOT","id":inv["golden_id"],
                    "lock_git_blob":inv["golden_lock_git_blob"],"role_comparator":"FIVE_ROLE_GOLDEN",
                    "comparison_kind":"SEMANTIC_CROSS_QUESTION_NOT_BYTE_EQUAL",
                    "technique_oracles":["Core role intent","slot/component order","attempt/reveal","independent exit","changed transfer"],
                    "semantic_deltas":["Post-original Owner Core2A H3-after-written-attempt policy"],
                    "actual_html_bytes_independently_verified":not held,
                    "owner_fixture_decision_id":None},
          "review":{**{a:{"qualified_verdict":"PENDING","reviewer_id":None,"reason":None} for a in ASKS},
                    "qualified_reviewer_name":None,"qualifications":None,
                    "conflict_declaration":None,"independent_mathematical_oracle":"PENDING_QUALIFIED",
                    "decision":"PENDING"},
          "owner":{"qrt_decision":"PENDING","qrt_decision_id":None,
                   "golden_scope_decision_id":None,"rights_decision_id":None,
                   "print_visual_decision_id":None,"release_decision_id":None},
          "viewer":{"tile_json":"tiles/"+d+".json",
                    "packet_url":"reviewer-packets/"+d+".md","links_checked":False},
          "evidence":{"source_url":REPO+"/blob/"+inv["pinned_source_head"]+"/"+row["source_path"],
                      "manifest_url":REPO+"/blob/"+inv["pinned_source_head"]+"/"+row["manifest_path"],
                      "math_m0":c[2],"hold":row["status"],
                      "figures":question.get("figure_refs",[])},
          "restrictions":["No original question rewrite","No private Core2","No QRT self-approval",
                          "No golden modification","No release or merge"]
        }
        need(tile["owner"]["qrt_decision_id"] is None and all(tile["review"][a]["qualified_verdict"]=="PENDING" for a in ASKS),"false acceptance")
        output_json(OUT/"tiles"/(d+".json"),tile)
        packet=OUT/"reviewer-packets"/(d+".md")
        packet.parent.mkdir(parents=True,exist_ok=True)
        packet.write_text(reviewer_packet(tile,question,transfer),encoding="utf-8")
        view[cell]=tile
    need(len(view)==7,"seven D3 cells required")
    output_json(OUT/"index.v1.json",{"schema":"imo217-d3-7x4-linked-review/v1",
       "cells":list(view),"band_issues":BANDS,"academic_and_owner":"PENDING",
       "reviewer_independence":"NONE","public_route":False})
    (OUT/"index.html").write_text(viewer(view),encoding="utf-8")
    need(all((OUT/"tiles"/(d.lower()+".json")).is_file() and
       (OUT/"reviewer-packets"/(d.lower()+".md")).is_file() for d in DEMANDS),
       "review packet missing")
    print("M3 7 source-traced tiles, 7 unsigned packets and 7x4 index produced; NO QRT acceptance")

if __name__=="__main__":
    main()
