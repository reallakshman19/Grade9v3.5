#!/usr/bin/env python3
"""Issue #182 R8: copy-on-write TEST-only Core2A -> Core1A -> same-question proof.

This is an isolated NONPRODUCTION experiment; NOT a change to render_core.py
or the frozen reference. It requires P1 provenance/role-page SHA evidence,
refuses any missing or mismatched question/microtopic, copies the original pages
into a new build-only directory, and marks every generated page HELD.

The adapter never supplies the target answer, auto-commits an attempt, opens a
solution, claims independent credit, or declares academic/Owner acceptance.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from qrt_intent_contract import (
    BP, ROLES, ContractError, blob_hash, ensure, read_json, resolve_under, sha256
)

SAFE = re.compile(r"^[A-Za-z0-9_-]+$")
ROLES_AND_INDEX = ["index.html", *(r.lower() + ".html" for r in ROLES)]
BANNER = ('<aside data-g9-held-banner role="status" '
          'style="background:#fff1d6;color:#4d2600;padding:1rem">'
          'TEST-ONLY UNAPPROVED NAVIGATION PROOF — NOT FOR LEARNER RELEASE'
          '</aside>')


class Shell(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html = []
        self.body = []
        self.meta = 0
        self.articles = []
        self.ids = []
        self.base = 0
        self.duplicate_attrs = False

    def handle_starttag(self, tag, pairs):
        names = [a for a, _ in pairs]
        if len(names) != len(set(names)):
            self.duplicate_attrs = True
        a = dict(pairs)
        if tag == "html":
            self.html.append(a)
        if tag == "body":
            self.body.append(a)
        if tag == "meta" and a.get("name") == "g9-render":
            self.meta += 1
        if tag == "base":
            self.base += 1
        if tag == "article" and a.get("data-g9-unit"):
            self.articles.append(a)
        if a.get("id"):
            self.ids.append(a["id"])


def shell_check(html: str, role: str, product_id: str,
                original: bool = True) -> Shell:
    parser = Shell()
    parser.feed(html)
    parser.close()
    ensure(not parser.duplicate_attrs and parser.base == 0,
           "HELD_DUPLICATE_ATTR_OR_FOREIGN_BASE", role)
    ensure(len(parser.html) == len(parser.body) == parser.meta == 1,
           "HELD_AMBIGUOUS_NATIVE_SHELL", role)
    h, b = parser.html[0], parser.body[0]
    ensure(h.get("data-g9-shell") is None and "data-g9-shell" in h and
           h.get("data-g9-role") == role and
           h.get("data-g9-mode") == "PAGES" and
           h.get("data-g9-product") == product_id and
           bool(h.get("data-g9-render-digest")) and
           b.get("data-core") == role and
           b.get("data-blueprint-ref") == BP[role],
           "HELD_NATIVE_PRODUCT_OR_BLUEPRINT_DRIFT", role)
    ensure(len(set(parser.ids)) == len(parser.ids), "HELD_DUPLICATE_DOM_ID", role)
    if original:
        ensure("data-g9-held-adapter" not in html and
               "data-g9-held-nav" not in html and
               "data-g9-held-banner" not in html,
               "HELD_INPUT_ALREADY_ADAPTED", role)
    return parser


def _json_js(value: str) -> str:
    ensure(isinstance(value, str) and SAFE.fullmatch(value),
           "HELD_UNSAFE_ID", str(value)[:80])
    return json.dumps(value)


def source_runtime(qid: str, mic: str) -> str:
    q, m = _json_js(qid), _json_js(mic)
    return ("""<script data-g9-held-nav="CORE2A">
(()=>{
"use strict";
const question = """ + q + """, concept = """ + m + """;
const a = document.getElementById(question);
if (!a || a.dataset.g9Role !== "CORE2A") return;
const box = a.querySelector("[data-g9-attempt-box]");
const field = box?.querySelector("textarea[data-g9-attempt]");
if (!box || !field || box.querySelectorAll("[data-g9-commit]").length !== 1) return;
const root = document.documentElement;
const key = "r8-held:" + root.dataset.g9Product + ":" +
  root.dataset.g9RenderDigest + ":" + question;
const get = () => {
  try { const v=JSON.parse(sessionStorage.getItem(key)||"null");
    return v&&typeof v==="object" ? v : null; } catch(e){return null;}
};
const put = v => { try {sessionStorage.setItem(key,JSON.stringify(v))}
  catch(e) { /* storage unavailable: no claim of preserved draft */ }};
const prior = get();
if (prior && prior.assisted && prior.committed) {
  a.dataset.g9Assisted="1";
  a.dataset.g9Assistance="CONCEPT_NAV";
  if (typeof prior.draft === "string") field.value=prior.draft;
}
const wrapper = document.createElement("p");
wrapper.dataset.g9HeldSourceConcept="after-attempt-only";
wrapper.hidden = true;
const link = document.createElement("a");
link.dataset.g9HeldSourceConceptLink = concept;
link.href = "core1a.html?g9-held-return="+encodeURIComponent(question)+
  "&g9-held-concept="+encodeURIComponent(concept)+"#"+encodeURIComponent(concept);
link.textContent = "Revisit the related concept (assisted; not independent credit)";
wrapper.append(link);
box.after(wrapper);
const update=()=>{wrapper.hidden = a.dataset.attempted !== "1"};
box.querySelector("[data-g9-commit]").addEventListener("click",
  () => queueMicrotask(update));
link.addEventListener("click",()=>{
  if (a.dataset.attempted !== "1"){wrapper.hidden=true;return;}
  put({committed:true,assisted:true,draft:field.value});
  a.dataset.g9Assisted="1";
  a.dataset.g9Assistance="CONCEPT_NAV";
});
field.addEventListener("input",()=>{
  const v=get();if(v&&v.assisted){v.draft=field.value;put(v);}
});
update();
})();
</script>""")


def concept_runtime(qid: str, mic: str) -> str:
    q, m = _json_js(qid), _json_js(mic)
    return ("""<script data-g9-held-nav="CORE1A">
(()=>{
"use strict";
const question = """ + q + """, concept = """ + m + """;
const params = new URLSearchParams(location.search);
if (params.get("g9-held-return") !== question ||
    params.get("g9-held-concept") !== concept) return;
const article = document.getElementById(concept);
if (!article || article.dataset.g9Role !== "CORE1A") return;
const root=document.documentElement;
const key="r8-held:"+root.dataset.g9Product+":"+
  root.dataset.g9RenderDigest+":"+question;
let state;
try {state=JSON.parse(sessionStorage.getItem(key)||"null");}
catch(e){return;}
if (!state || state.assisted !== true || state.committed !== true) return;
const p = document.createElement("p");
p.dataset.g9HeldReturn="assisted-only";
const a = document.createElement("a");
a.dataset.g9HeldReturnLink=question;
a.href="core2a.html#"+encodeURIComponent(question);
a.textContent="Return to your same Core2A question (assisted review)";
p.append(a);
article.append(p);
})();
</script>""")


def adapt_pages(native_contract: dict, source_root: Path,
                native_output: Path, manifest: dict, source: dict,
                original: dict[str, str]) -> tuple[dict[str, str], dict]:
    """Pure fail-closed transformation; caller writes only a fresh held build."""
    n = native_contract
    ensure(n.get("native_evidence", {}).get("all_role_structure") == "PASS" and
           n.get("technical_contract") == "VALIDATED_PROPOSAL" and
           n.get("semantic_review") == "HOLD_REVIEW_REQUIRED" and
           n.get("owner_qrt_acceptance") == "PENDING",
           "HELD_P1_UNACCEPTED_PROOF_REQUIRED")
    product = manifest.get("product_id")
    ensure(isinstance(product, str) and SAFE.fullmatch(product),
           "HELD_UNSAFE_PRODUCT")
    ensure(manifest.get("output_roles") == list(ROLES) and
           manifest.get("selection", {}).get("core2") == [],
           "HELD_NATIVE_FIVE_ROLES_ONLY")
    sel = manifest["selection"]
    ensure(len(sel.get("microtopics", [])) == 1 and
           len(sel.get("core2a", [])) == 1,
           "HELD_UNIQUE_SELECTED_CONCEPT_QUESTION")
    qid, mic = sel["core2a"][0], sel["microtopics"][0]
    _json_js(qid)
    _json_js(mic)
    primary = n["source_crux"]["primary"]
    ensure(primary["question_id"] == qid and
           n["provenance"]["source_git_blob"] == blob_hash(
               resolve_under(source_root, n["provenance"]["source_path"])) and
           n["provenance"]["manifest_git_blob"] == blob_hash(
               resolve_under(source_root, n["provenance"]["manifest_path"])),
           "HELD_PROVENANCE_OR_PRIMARY_DRIFT")
    ensure(source.get("subject") == "TEST" and
           source.get("status") == "CANDIDATE" and
           manifest.get("subject") == "TEST",
           "HELD_ONLY_CANDIDATE_TEST")
    questions = [x for x in source.get("questions", []) if x.get("id") == qid]
    topics = [x for x in source.get("microtopics", []) if x.get("id") == mic]
    ensure(len(questions) == len(topics) == 1 and
           questions[0].get("primary_capability_ref") ==
           topics[0].get("primary_capability_ref"),
           "HELD_WRONG_CONCEPT_CAPABILITY_JOIN")
    ensure(set(original) == set(ROLES_AND_INDEX),
           "HELD_ALL_SIX_NATIVE_HTML_REQUIRED")
    for role in ROLES:
        filename = role.lower() + ".html"
        ensure(sha256(native_output / filename) ==
               n["native_evidence"]["roles"][role]["native_sha256"],
               "HELD_NATIVE_FILE_CHANGED_SINCE_P1", role)
        shell = shell_check(original[filename], role, product)
        ensure(len(shell.articles) == 1 and
               shell.articles[0].get("data-g9-unit") ==
               (qid if role == "CORE2A" else
                sel["core2b"][0] if role == "CORE2B" else mic),
               "HELD_NATIVE_ARTICLE_ID_DRIFT", role)
    ensure(original["index.html"] == (native_output / "index.html").read_text(
           encoding="utf-8"), "HELD_INDEX_CHANGED_SINCE_RENDER")
    q_html = original["core2a.html"]
    ensure(q_html.count("data-g9-attempt-box") >= 1 and
           q_html.count('data-g9-payload-ref="CORE2A-'+qid+'-reasoning"') == 1 and
           "data-requires-attempt" in q_html,
           "HELD_ATTEMPT_GATED_REASONING_REQUIRED")
    ensure(original["core1a.html"].count('id="'+mic+'"') == 1,
           "HELD_SELECTED_CONCEPT_ARTICLE_MISSING")
    ensure(original["core2a.html"].count('id="'+qid+'"') == 1,
           "HELD_SELECTED_QUESTION_ARTICLE_MISSING")
    held = {}
    for role in ROLES:
        filename = role.lower() + ".html"
        html = original[filename]
        ensure(html.count("</body>") == 1 and
               html.count("</head>") == 1 and
               html.count("<main>") == 1 and
               html.count("<html ") == 1,
               "HELD_AMBIGUOUS_HTML_INSERTION", role)
        html = html.replace('<html ', '<html data-g9-held-adapter="R8-TEST-COPY" ', 1)
        html = html.replace("</head>",
            '<meta name="robots" content="noindex,nofollow"></head>', 1)
        html = html.replace("<main>", BANNER + "<main>", 1)
        if role == "CORE2A":
            html = html.replace("</body>", source_runtime(qid, mic) + "</body>", 1)
        if role == "CORE1A":
            html = html.replace("</body>", concept_runtime(qid, mic) + "</body>", 1)
        ensure('data-g9-held-adapter="R8-TEST-COPY"' in html and
               html.count("data-g9-held-banner") == 1,
               "HELD_OUTPUT_LABEL_MISSING", role)
        shell_check(html, role, product, original=False)
        held[filename] = html
    # Index receives a conspicuous marker too; it is not a runnable Pages
    # release or a valid renderer receipt after two pages change.
    idx = original["index.html"]
    ensure(idx.count("<main>") == 1 and idx.count("</head>") == 1 and
           idx.count("<html ") == 1,
           "HELD_INDEX_SHELL_DRIFT")
    held["index.html"] = idx.replace('<html ',
             '<html data-g9-held-adapter="R8-TEST-COPY" ', 1).replace(
             "</head>", '<meta name="robots" content="noindex,nofollow"></head>', 1
             ).replace("<main>", BANNER+"<main>",1)
    return held, {
        "schema": "imo182-r8-test-only-native-assisted-copy/v1",
        "status": "LOCAL_TEST_CANDIDATE_ADAPTED_NOT_PUBLISHED",
        "cell_id": n["cell_id"],
        "product_id": product,
        "primary_question_id": qid,
        "microtopic_id": mic,
        "original_sha256": {
            name: sha256(native_output / name) for name in ROLES_AND_INDEX
        },
        "adapted_sha256": {},
        "registered_renderer_receipt_remains_original_only": True,
        "does_not_qualify_as_native_golden_match": True,
        "copy_only_not_authoritative_renderer": True,
        "source_mutated": False,
        "golden_mutated": False,
        "academic_qrt_approved": False,
        "owner_approved": False,
        "learner_launch_authorized": False,
        "independent_credit_authorized": False,
        "real_browser_verified": False,
        "human_qrta_review": "NOT_RUN",
        "release": "HOLD",
    }


def apply(source_root: Path, native_output: Path,
          native_contract_path: Path, output_dir: Path) -> dict:
    root = source_root.resolve(strict=True)
    original_dir = native_output.resolve(strict=True)
    dest = output_dir.resolve()
    ensure(original_dir.is_relative_to(root / "build") and
           dest.is_relative_to(root / "build" / "imo182-r8-held") and
           dest != (root / "build" / "imo182-r8-held").resolve() and
           not dest.is_relative_to(original_dir) and
           not original_dir.is_relative_to(dest) and
           not dest.exists(), "HELD_UNSAFE_OR_EXISTING_OUTPUT_DIRECTORY")
    ensure(all((original_dir / name).is_file() and
               not (original_dir / name).is_symlink()
               for name in ROLES_AND_INDEX),
           "HELD_ORIGINAL_RENDERED_FILES_MISSING")
    n = read_json(native_contract_path)
    source = read_json(resolve_under(root, n["provenance"]["source_path"]))
    manifest = read_json(resolve_under(root, n["provenance"]["manifest_path"]))
    pages = {name: (original_dir / name).read_text(encoding="utf-8")
             for name in ROLES_AND_INDEX}
    held, report = adapt_pages(n, root, original_dir, manifest, source, pages)
    report["adapted_sha256"] = {
        name: __import__("hashlib").sha256(value.encode("utf-8")).hexdigest()
        for name, value in held.items()
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".qrt-held-",dir=dest.parent) as tmp:
        tmp_dir = Path(tmp)
        for name,value in held.items():
            (tmp_dir/name).write_text(value,encoding="utf-8")
        (tmp_dir/"held-adaptation-receipt.json").write_text(
            json.dumps(report,indent=2,ensure_ascii=False)+"\n",
            encoding="utf-8")
        # Do not copy renderer receipt. Changed HTML is NOT renderer-produced.
        os.rename(tmp_dir, dest)
    return report


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root",required=True,type=Path)
    p.add_argument("--native-output",required=True,type=Path)
    p.add_argument("--native-contract",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    report=apply(args.source_root,args.native_output,
                 args.native_contract,args.out)
    print(f"{report['cell_id']}: isolated held-only pages written; "
          "all originals unchanged; browser/academic/Owner/release HOLD")


if __name__=="__main__":
    main()
