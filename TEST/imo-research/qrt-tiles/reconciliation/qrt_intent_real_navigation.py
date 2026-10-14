#!/usr/bin/env python3
"""Issue 182 R8 P2 extension: actual cross-role browser navigation and assistance audit.

Real Chromium clicks actual five-Core renderer-owned shell links. Separately
probe source-bound CORE2A concept-link / CORE1A practice-return / assistance
state. Absence is an observed engineering gap, never a QRT semantic MATCH.

Does not alter source content, frozen golden, roles, renderer or UI itself.
"""
from __future__ import annotations

import argparse
import json
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

from qrt_intent_contract import BP, ROLES, blob_hash, ensure, read_json, resolve_under, sha256
from qrt_intent_w_path_audit import RootAssets

NAV_ROUTES = {
    "ORIENTATION_LEARN_APPLY": ("CORE1", "CORE1A", "CORE2A"),
    "REPAIR_LEARN_RECONSTRUCT_APPLY": ("CORE1", "CORE1A", "CORE1B", "CORE2A"),
    "APPLY_LEARN_ASSISTED_RETURN": ("CORE2A", "CORE1A", "CORE2A"),
    "APPLY_TRANSFER": ("CORE2A", "CORE2B"),
}


def classify_assisted_return(navigation: dict) -> list[str]:
    """Discriminating fail-closed predicates. No inference of mastery."""
    hits = []
    if not navigation["context_link_at_source"]:
        hits.append("CORE2A_MISSING_CONTEXT_BOUND_CONCEPT_LINK")
    if not navigation["return_link_at_concept"]:
        hits.append("CORE1A_MISSING_TARGETED_CORE2A_RETURN_LINK")
    if not navigation["return_state_assisted"]:
        hits.append("CORE2A_ASSISTED_RETURN_NOT_MARKED")
    if not navigation["source_attempt_restored"]:
        hits.append("CORE2A_SOURCE_ATTEMPT_NOT_RESTORED_ON_RETURN")
    return hits



def _same_local_anchor(href: str | None, filename: str, unit_id: str) -> bool:
    """Require a local role file and exact selected record fragment."""
    if not isinstance(href, str) or not isinstance(unit_id, str):
        return False
    target = urlsplit(href)
    return (not target.scheme and not target.netloc
            and target.path in (filename, "./" + filename)
            and unquote(target.fragment) == unit_id)


def classify_target_identity(observed: dict) -> list[str]:
    """One-way falsifiers: a link's existence never proves a safe return.

    These checks are conditional on an actual native link being present; when
    a link is entirely absent, classify_assisted_return reports that gap.
    No human-academic / independent-work verdict is inferred.
    """
    problems = []
    qid = observed["expected_primary_question_id"]
    concept = observed["expected_concept_id"]
    if observed["source_question_id"] != qid:
        problems.append("NAV_SOURCE_QUESTION_ID_DRIFT")
    if observed["observed_concept_id"] != concept:
        problems.append("NAV_CONCEPT_ID_NOT_PINNED_SELECTION")
    if observed["context_link_present"] and (
            observed["context_link_count"] != 1
            or observed["context_concept_ref"] != concept
            or not _same_local_anchor(
                observed["context_href"], "core1a.html", concept)):
        problems.append("NAV_CONTEXT_LINK_WRONG_CONCEPT_OR_ORIGIN")
    if observed["return_link_present"] and (
            observed["return_link_count"] != 1
            or observed["return_question_ref"] != qid
            or not _same_local_anchor(
                observed["return_href"], "core2a.html", qid)):
        problems.append("NAV_RETURN_LINK_WRONG_QUESTION_OR_ORIGIN")
    if observed["return_state_assisted"] and observed["return_state_independent"]:
        problems.append("NAV_ASSISTED_RETURN_FALSE_INDEPENDENT_CREDIT")
    return problems


def verify_role(page, role: str) -> None:
    ensure(page.locator("html").get_attribute("data-g9-role") == role,
           "P2_NAV_REAL_ROLE_NOT_REACHED", role)
    ensure(page.locator("body").get_attribute("data-blueprint-ref") == BP[role],
           "P2_NAV_BLUEPRINT_WRONG", role)
    ensure(page.locator("article[data-g9-unit]").first.is_visible(),
           "P2_NAV_ROLE_ARTICLE_NOT_VISIBLE", role)


def click_role(page, role: str, base: str) -> dict:
    """Click existing learner shell anchor, not programmatic goto between roles."""
    link = page.locator(
        f".g9-triad-actions a.g9-triad-btn[href='{role.lower()}.html']")
    ensure(link.count() == 1 and link.is_visible(),
           "P2_NAV_SHELL_LINK_MISSING", role)
    link.click()
    page.wait_for_load_state("load")
    ensure(urlsplit(page.url).path == urlsplit(base).path + "/" +
           role.lower() + ".html", "P2_NAV_WRONG_URL", page.url)
    verify_role(page, role)
    return {
        "clicked_actual_shell_anchor": True,
        "role": role,
        "page": role.lower() + ".html",
        "viewport": 390,
        "role_blueprint_checked": True,
    }


def _click_a_route(context, origin: str, steps: tuple[str, ...],
                   base: str) -> dict:
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    route = []
    try:
        response = page.goto(base + "/" + origin.lower() + ".html",
                             wait_until="load")
        ensure(response and response.status == 200,
               "P2_NAV_START_404", origin)
        verify_role(page, origin)
        route.append({"role": origin, "real_http": 200})
        for role in steps[1:]:
            route.append(click_role(page, role, base))
        ensure(not errors, "P2_NAV_JS_EXCEPTION", repr(errors))
        return {
            "actual_click_through": True,
            "route": list(steps),
            "probes": route,
            "independent_learning_proven": False,
        }
    finally:
        page.close()


def test_navigation(browser, source_root: Path, output: Path,
                    contract: dict) -> dict:
    ensure(contract.get("native_evidence", {}).get("all_role_structure") ==
           "PASS", "P2_NAV_NEEDS_P1_PROOF")
    provenance = contract["provenance"]
    manifest_path = resolve_under(source_root, provenance["manifest_path"])
    ensure(blob_hash(manifest_path) == provenance["manifest_git_blob"],
           "P2_NAV_MANIFEST_SOURCE_SHA_CHANGED")
    manifest = read_json(manifest_path)
    selected = manifest["selection"]["microtopics"]
    ensure(len(selected) == 1 and
           manifest["selection"]["core2a"] ==
           [contract["source_crux"]["primary"]["question_id"]],
           "P2_NAV_SOURCE_MANIFEST_QUESTION_DRIFT")
    expected_concept = selected[0]
    for role in ROLES:
        digest = contract["native_evidence"]["roles"][role]["native_sha256"]
        ensure(sha256(output / (role.lower() + ".html")) == digest,
               "P2_NAV_NATIVE_BYTES_CHANGED", role)

    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                 partial(RootAssets, source_root=source_root))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    rel = output.resolve().relative_to(source_root.resolve()).as_posix()
    base = f"http://127.0.0.1:{server.server_port}/{rel}"
    context = browser.new_context(viewport={"width": 390, "height": 900})
    try:
        path_results = {
            name: _click_a_route(context, path[0], path, base)
            for name, path in NAV_ROUTES.items()
        }
        # Keep session independent of the four generic paths, so that an earlier
        # page navigation cannot cause an accidental "assisted" result.
        context.close()
        context = browser.new_context(viewport={"width": 390, "height": 900})
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        response = page.goto(base + "/core2a.html", wait_until="load")
        ensure(response and response.status == 200,
               "P2_NAV_ASSISTED_START_404")
        verify_role(page, "CORE2A")
        source = page.locator("article[data-g9-unit]").first
        qid = source.get_attribute("data-g9-unit")
        ensure(qid == contract["source_crux"]["primary"]["question_id"],
               "P2_NAV_PRIMARY_QID_NOT_RENDERED")
        links = source.locator("a[data-g9-concept-link]")
        contextual = links.count() > 0
        entry_concept_refs = links.evaluate_all(
            "els => els.map(e => e.getAttribute('data-g9-concept-ref'))"
        )
        context_href = links.first.get_attribute("href") if contextual else None
        # Use a nonanswer placeholder to test browser draft preservation, not
        # mathematical success; writing an answer is NEVER academic evidence.
        draft = "NAVIGATION_SENTINEL_NOT_A_LEARNER_MATH_ANSWER"
        answer = source.locator("textarea[data-g9-attempt]").first
        ensure(answer.count() == 1, "P2_NAV_EXPECTS_TEXT_ATTEMPT")
        answer.fill(draft)
        if contextual:
            links.first.click()
            page.wait_for_load_state("load")
            entry_mode = "CONTEXT_LINK"
        else:
            # Test the ACTUAL selectable header role even when targeted
            # instructional routing is missing; do not fabricate a link.
            click_role(page, "CORE1A", base)
            entry_mode = "SHELL_FALLBACK_NO_CONTEXT_LINK"
        verify_role(page, "CORE1A")
        concept = page.locator("article[data-g9-unit]").first
        concept_id = concept.get_attribute("data-g9-unit")
        targeted = page.locator("a[data-g9-practice-link][data-g9-return-link]")
        targeted_exist = targeted.count() > 0
        return_href = targeted.first.get_attribute("href") if targeted_exist else None
        return_ref = targeted.first.get_attribute("data-g9-return-link") if targeted_exist else None
        practice_count = page.locator("a[data-g9-practice-link]").count()
        if targeted_exist:
            link = targeted.first
            href = link.get_attribute("href") or ""
            if href.startswith("core2a.html"):
                link.click()
                page.wait_for_load_state("load")
                return_mode = "TARGETED_PRACTICE_LINK"
            else:
                click_role(page, "CORE2A", base)
                return_mode = "SHELL_FALLBACK_NON_NATIVE_PRACTICE_LINK"
        else:
            click_role(page, "CORE2A", base)
            return_mode = "SHELL_FALLBACK_NO_TARGETED_RETURN_LINK"
        verify_role(page, "CORE2A")
        source_return = page.locator(f"article[data-g9-unit='{qid}']")
        ensure(source_return.count() == 1,
               "P2_NAV_WRONG_RETURN_QUESTION")
        # This is the native Core2A article's assisted marker, distinct from
        # the legacy CORE2 per-question state shape.
        marked = source_return.get_attribute("data-g9-assisted") == "1"
        independent = source_return.get_attribute("data-g9-independent") == "1"
        restored = source_return.locator("textarea[data-g9-attempt]").first.input_value() == draft
        target_state = {
            "expected_primary_question_id": contract["source_crux"]["primary"]["question_id"],
            "source_question_id": qid,
            "expected_concept_id": expected_concept,
            "observed_concept_id": concept_id,
            "context_link_present": contextual,
            "context_link_count": links.count(),
            "context_concept_ref": entry_concept_refs[0] if contextual else None,
            "context_href": context_href,
            "return_link_present": targeted_exist,
            "return_link_count": targeted.count(),
            "return_question_ref": return_ref,
            "return_href": return_href,
            "return_state_assisted": marked,
            "return_state_independent": independent,
        }
        target_findings = classify_target_identity(target_state)
        # Read only flags, avoid storing learner/proprietary question text.
        contextual_result = {
            "primary_question_id": qid,
            "concept_id_observed": concept_id,
            "entry_mode": entry_mode,
            "return_mode": return_mode,
            "context_link_at_source": contextual,
            "contextual_concept_refs": entry_concept_refs,
            "return_link_at_concept": targeted_exist and
                return_mode == "TARGETED_PRACTICE_LINK",
            "native_concept_practice_link_count": practice_count,
            "return_state_assisted": marked,
            "source_attempt_restored": restored,
            "target_identity_expected_concept": expected_concept,
            "target_identity_findings": target_findings,
            "target_identity_proven": (
                contextual and targeted_exist and not target_findings and marked
                and restored and not independent),
            "attempt_submitted_before_concept_navigation": False,
            "manual_shell_route_is_not_independent_mastery": True,
            "academic_verdict": "NOT_RUN",
        }
        ensure(not errors, "P2_NAV_ASSISTED_JS_EXCEPTION", repr(errors))
        return {
            "schema": "imo182-r8-real-native-navigation/v1",
            "cell_id": contract["cell_id"],
            "native_role_paths": path_results,
            "clicked_actual_role_transitions":
                sum(len(v["route"]) - 1 for v in path_results.values()) + 2,
            "assisted_return": contextual_result,
            "observed_integrity_gaps": classify_assisted_return(contextual_result),
            "target_identity_findings": target_findings,
            "independence_from_return_visit": False,
            "qualified_semantic_review": "NOT_RUN",
            "owner_acceptance": False,
            "status": "HOLD_REVIEW_REQUIRED",
            "limitations": (
                "Real clicked shell routes/actual browser returned roles, but "
                "fallback header navigation does not establish contextual "
                "source-question guidance, learning support, or academic mastery. "
                "Absence of known leak is NOT a semantic proof."
            ),
        }
    finally:
        context.close()
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--native-output", type=Path, required=True)
    p.add_argument("--native-contract", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    contract = read_json(args.native_contract)
    with sync_playwright() as impl:
        browser = impl.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            report = test_navigation(browser, args.source_root,
                                     args.native_output, contract)
        finally:
            browser.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"{report['cell_id']}: {report['clicked_actual_role_transitions']} "
          f"actual cross-Core shell clicks, contextual gap findings="
          f"{report['observed_integrity_gaps']}; semantic/Owner HOLD")


if __name__ == "__main__":
    main()
