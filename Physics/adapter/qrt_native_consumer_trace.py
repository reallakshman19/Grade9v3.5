"""Read-only, single-question native source-to-learner evidence probe.

Does not generate publication files, launch a browser, certify science, or
authorize content. Reuses Shared.tools.render_core.build() in memory when
--render is selected. Each unproven join stays NOT_RUN or UNVERIFIED.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

from Physics.adapter.qrt_crosswalk import ROOT as REPO

QUESTION_ID = "Q-PHY-NLM-2B-FRICTION-STATE-01"
SOURCE = "Physics/library/phy-nlm-first-law.v1.json"
MANIFEST = "products/physics/phy-nlm-first-law.manifest.json"
GOLDEN = "golden/units/G-CORE2-R2/manifest.json"
PUBLIC = "public/products/physics/phy-nlm-first-law"
EXPECTED_ROLE = "CORE2B"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class _Article(HTMLParser):
    """Observe only the selected canonical article in the in-memory HTML."""
    def __init__(self, question: str):
        super().__init__(convert_charrefs=True)
        self.question = question
        self.active = False
        self.matches = 0
        self.template_depth = 0
        self.seen = {"attempt": 0, "commit": 0, "gated_reveal": 0,
                     "payload": 0, "lineage_links": 0}
        self.visible: list[str] = []
        self.payload: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and attrs.get("data-g9-unit") == self.question:
            self.matches += 1
            self.active = True
            if attrs.get("data-g9-role") != EXPECTED_ROLE:
                self.seen["wrong_role"] = 1
        if not self.active:
            return
        if tag == "template" and "data-g9-payload" in attrs:
            self.template_depth += 1
            self.seen["payload"] += 1
        if "data-g9-attempt-box" in attrs:
            self.seen["attempt"] += 1
        if "data-g9-commit" in attrs:
            self.seen["commit"] += 1
        if tag == "details" and "data-requires-attempt" in attrs:
            self.seen["gated_reveal"] += 1
        if tag == "a" and "data-g9-lineage" in attrs:
            self.seen["lineage_links"] += 1

    def handle_data(self, data):
        if self.active:
            (self.payload if self.template_depth else self.visible).append(data)

    def handle_endtag(self, tag):
        if not self.active:
            return
        if tag == "template" and self.template_depth:
            self.template_depth -= 1
        elif tag == "article":
            self.active = False


def inspect_rendered_html(html: str, question: str, protected_move: str) -> dict:
    probe = _Article(question)
    probe.feed(html)
    seen = probe.seen
    hidden = "".join(probe.payload)
    visible = "".join(probe.visible)
    problems = []
    if probe.matches != 1:
        problems.append("RENDER_QUESTION_CARDINALITY")
    if seen.get("wrong_role"):
        problems.append("RENDER_CORE_ROLE")
    for field in ("attempt", "commit", "gated_reveal", "payload"):
        if seen[field] < 1:
            problems.append("RENDER_MISSING_" + field.upper())
    if protected_move not in hidden:
        problems.append("PROTECTED_MOVE_NOT_IN_GATED_PAYLOAD")
    if protected_move in visible:
        problems.append("PROTECTED_MOVE_IN_INITIAL_ARTICLE_TEXT")
    return {
        "status": "STATIC_STRUCTURE_OBSERVED" if not problems else "STRUCTURE_DEFECT",
        "problems": problems,
        "matched_articles": probe.matches,
        "observed": seen,
        "protected_move_in_template": protected_move in hidden,
        "protected_move_in_initial_article_text": protected_move in visible,
        "javascript_enforced": "NOT_RUN",
        "visual_browser_checked": "NOT_RUN",
    }


def trace(*, root: Path = REPO, render: bool = False) -> dict:
    checks: list[dict] = []
    result = {
        "schema": "physics-qrt.native-consumer-trace/v1",
        "question_id": QUESTION_ID,
        "source_class": "AUTHOR_CREATED_CANDIDATE",
        "checks": checks,
        "science_verdict": "REVIEW_REQUIRED",
        "qrt_verdict": "NOT_RUN",
        "browser_verdict": "NOT_RUN",
        "learner_verdict": "NOT_ATTESTED",
        "publication_verdict": "NOT_ATTESTED",
        "owner_work_lock": "DRAFT_HOLD",
        "release_verdict": "HOLD",
    }

    def add(name: str, status: str, evidence: dict | str):
        checks.append({"join": name, "status": status, "evidence": evidence})

    try:
        source_path = root / SOURCE
        src = json.loads(source_path.read_text(encoding="utf-8"))
        matches = [q for q in src.get("questions", []) if isinstance(q, dict)
                   and q.get("id") == QUESTION_ID]
        if len(matches) != 1:
            add("CANONICAL_SOURCE", "FAIL", {"matches": len(matches)})
            return _finish(result)
        q = matches[0]
        move_ref = (q.get("transfer") or {}).get("protected_move_ref")
        routes = [x for x in (q.get("answer") or {}).get("reasoning_route", [])
                  if isinstance(x, dict) and x.get("id") == move_ref]
        if len(routes) != 1:
            add("CANONICAL_SOURCE", "FAIL", "PROTECTED_MOVE_NOT_UNIQUE")
            return _finish(result)
        move_action = routes[0].get("action") or ""
        if not move_action:
            add("CANONICAL_SOURCE", "FAIL", "PROTECTED_MOVE_EMPTY")
            return _finish(result)
        add("CANONICAL_SOURCE", "PASS", {
            "path": SOURCE, "sha256": _sha(source_path),
            "origin": q.get("origin"), "status": q.get("status"),
            "transfer_dimension": (q.get("transfer") or {}).get("dimension"),
            "protected_move_ref": move_ref,
        })
    except (OSError, ValueError, TypeError) as exc:
        add("CANONICAL_SOURCE", "FAIL", {"error": str(exc)})
        return _finish(result)

    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        refs = (manifest.get("selection") or {}).get("core2b") or []
        selected = refs.count(QUESTION_ID)
        source_ref = (manifest.get("package_refs") or []).count(SOURCE)
        if selected != 1 or source_ref != 1:
            add("PRODUCT_SELECTION", "FAIL", {"question_matches": selected, "source_matches": source_ref})
            return _finish(result)
        parent = (q.get("transfer") or {}).get("builds_on") or []
        available = {p.get("id") for p in src.get("questions", []) if isinstance(p, dict)}
        preceding = set((manifest.get("selection") or {}).get("core2a") or [])
        missing = [p for p in parent if p not in available or p not in preceding]
        add("PRODUCT_SELECTION", "PASS" if not missing else "FAIL", {
            "path": MANIFEST, "sha256": _sha(root / MANIFEST),
            "parent_refs": parent, "missing_selected_prerequisites": missing
        })
        if missing:
            return _finish(result)
    except (OSError, ValueError, TypeError) as exc:
        add("PRODUCT_SELECTION", "FAIL", {"error": str(exc)})
        return _finish(result)

    try:
        golden = json.loads((root / GOLDEN).read_text(encoding="utf-8"))
        count = ((golden.get("selection") or {}).get("core2b") or []).count(QUESTION_ID)
        add("GOLDEN_SELECTION_CANDIDATE", "PASS" if count == 1 else "FAIL",
            {"path": GOLDEN, "sha256": _sha(root / GOLDEN),
             "matches": count, "academic_approval": "NOT_ESTABLISHED"})
    except (OSError, ValueError, TypeError) as exc:
        add("GOLDEN_SELECTION_CANDIDATE", "NOT_RUN", {"error": str(exc)})

    if render:
        if root.resolve() != REPO.resolve():
            add("NATIVE_IN_MEMORY_RENDER", "NOT_RUN", "TEST_FIXTURE_CANNOT_INVOKE_REPOSITORY_RENDERER")
        else:
            try:
                from Shared.tools import render_core
                pages, gaps, digest = render_core.build(root / MANIFEST, mode="PAGES")
                html = pages.get("core2b.html")
                if not isinstance(html, str):
                    add("NATIVE_IN_MEMORY_RENDER", "FAIL", {
                        "error": "NO_CORE2B_PAGE", "page_names": sorted(pages)})
                else:
                    inspected = inspect_rendered_html(html, QUESTION_ID, move_action)
                    add("NATIVE_IN_MEMORY_RENDER",
                        "PASS" if inspected["status"] == "STATIC_STRUCTURE_OBSERVED" else "FAIL",
                        {"renderer_digest": digest, "core2b_html_sha256":
                            hashlib.sha256(html.encode("utf-8")).hexdigest(),
                         "render_gaps": len(gaps), "related_gaps": [g for g in gaps
                            if g.get("record") == QUESTION_ID][:10],
                         "inspected": inspected})
            except (ImportError, ModuleNotFoundError) as exc:
                add("NATIVE_IN_MEMORY_RENDER", "NOT_RUN", {"missing_dependency": str(exc)})
            except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
                add("NATIVE_IN_MEMORY_RENDER", "FAIL", {"error": str(exc)})
    else:
        add("NATIVE_IN_MEMORY_RENDER", "NOT_RUN", "USE_--render_ON_EXACT_CHECKOUT")

    # A manifest, a generated HTML string, and a released page are different.
    public = root / PUBLIC
    receipt = public / "render-receipt.json"
    if not receipt.is_file():
        add("OWNER_ACCEPTED_PUBLIC_RENDER", "NOT_RUN", "NO_COMMITTED_PUBLIC_RENDER_RECEIPT")
    else:
        try:
            from Shared.tools.accept_product import verify_render
            recorded = verify_render(public)
            add("OWNER_ACCEPTED_PUBLIC_RENDER", "PASS", {
                "path": PUBLIC, "digest": recorded["digest"],
                "question_selected_in_manifest": True,
                "content_consumer_browser_checked": False,
            })
        except (ValueError, OSError, KeyError, RuntimeError) as exc:
            add("OWNER_ACCEPTED_PUBLIC_RENDER", "FAIL", {"error": str(exc)})
    add("BROWSER_PRE_ATTEMPT_AND_CHANGED_DEMAND", "NOT_RUN",
        "REQUIRES_ACTUAL_CHROMIUM_AND_QUALIFIED_REVIEW; HTML_SOURCE_IS_NOT_BROWSER_OR_PEDAGOGICAL_PROOF")
    return _finish(result)


def _finish(result: dict) -> dict:
    checks = result["checks"]
    first = next((c for c in checks if c["status"] != "PASS"), None)
    result["first_unproven_join"] = first["join"] if first else "NONE_IN_THIS_BOUNDED_PROBE"
    result["static_chain_status"] = "STRUCTURAL_CHECKS_ONLY"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="Run native renderer in memory (no files written)")
    args = parser.parse_args()
    packet = trace(render=args.render)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 1 if any(c["status"] == "FAIL" for c in packet["checks"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
