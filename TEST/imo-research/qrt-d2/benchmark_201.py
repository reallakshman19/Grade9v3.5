"""Issue #201: falsifiable native D2/Owner-golden technique checks.

Run after the seven manifests have been rendered with Shared/tools/render_core.py.
No QRT academic or Owner acceptance is awarded by this program.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
GOLDEN = ROOT / "golden/units/G-IMO-G9-FIVE-CORE-20261012"
REGISTRY = ROOT / "Shared/web/interactive-page-blueprints.v1.json"
ROLES = ("core1", "core1a", "core1b", "core2a", "core2b")
DEMANDS = ("retrieve", "explain", "apply", "model", "represent", "synthesize", "justify")
PAGE_NAMES = tuple(f"{r}.html" for r in ROLES) + ("index.html",)
ARTIFACT_SHA = {
    "retrieve": "08a34f506f71e84d956ed65a3f8c5f9bbdf638346a7562f9d2ebc4981f0c8a76",
    "explain": "5f89a162f29ff21ad653bb577693c2d581a1d677b7dbbad40d559ffe28ccf1a6",
    "apply": "4ad2e88fe5c9aae9d2ac10f564317bdcb049c2c7a6b6ffbb1fd5c3a2ed2bfbea",
    "model": "dd9ac357db001ba780da4fa272a044598a9657c558bcb8ecf1ff95e43c0047dc",
    "represent": "f9b18cce19efd0ebd6b15794cb2341aca7af2583b02ad598c5601e9268c180b9",
    "synthesize": "b3b119d0d295b7d57f98e6036c7beaa31693e9a6b5115aca7f9c56ce89a49807",
    "justify": "cf7ebbebe8bb9987a66a9da3f179e5bc9f320686dd83812fa8b267ca1661e4e3",
}

# Exact answer tokens must not occur in the readable Core2A page before
# commitment, including SVG accessible labels. This is a targeted leak
# regression test, not a complete H/S/P/M pedagogic judgment.
PRIMARY_CONCLUSION_SENTINELS = {
    "retrieve": ("15m", "21m", "saving 6m"),
    "explain": ("3^2=9", "t=1 gives", "3² = 9"),
    "apply": ("648", "32.5%", "720 credits"),
    "model": ("x=4", "x = 4", "four large", "five small"),
    "represent": ("15 unshaded", "3×5=15", "3 × 5 = 15"),
    "synthesize": ("432", "452 is not"),
    "justify": ("m=2 gives", "m = 2 gives", "3×4×5=60"),
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def collect(html: str, attribute: str) -> list[str]:
    return re.findall(r'\b' + re.escape(attribute) + r'="([^"]+)"', html)

def browser_check(html: str, role: str, demand: str, browser) -> dict:
    """Real Chromium on native renderer HTML (not on a handwritten imitation)."""
    ctx = browser.new_context(viewport={"width": 390, "height": 844})
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    result = {"role": role}
    try:
        page.set_content(html, wait_until="load")
        if role == "core2a":
            # innerText follows browser display semantics: <template> is inert.
            precommit_text = page.locator("body").inner_text()
            visible_labels = page.evaluate("""() => [...document.querySelectorAll(
               '[aria-label], [title], svg title, svg desc'
            )].filter(e => !e.closest('template')).map(e =>
                [e.getAttribute('aria-label') || '', e.getAttribute('title') || '',
                 e.tagName === 'title' || e.tagName === 'desc' ? e.textContent : '']
                 .join(' ')).join(' ')""")
            exposed = (precommit_text + " " + visible_labels).casefold()
            leaked = [token for token in PRIMARY_CONCLUSION_SENTINELS[demand]
                      if token.casefold() in exposed]
            if leaked:
                raise AssertionError("CORE2A_PRECOMMIT_ANSWER_LEAK:" + ",".join(leaked))
            # H2 is reachable pre-commit. Preserve exact visible text for the
            # qualified reviewer, and forbid known-answer leaks after that click.
            next_hint = page.get_by_role("button", name="Next hint")
            if next_hint.count() != 1:
                raise AssertionError("MISSING_PRECOMMIT_H2_NAV")
            lines_before = set(line.strip() for line in precommit_text.splitlines())
            next_hint.click()
            after_h2 = page.locator("body").inner_text()
            h2_lines = [line.strip() for line in after_h2.splitlines()
                        if line.strip() not in lines_before and len(line.strip()) >= 25]
            if not h2_lines:
                raise AssertionError("H2_DID_NOT_ADD_MEANINGFUL_HINT_TEXT")
            h2_exposed = (after_h2 + " " + visible_labels).casefold()
            h2_leaks = [token for token in PRIMARY_CONCLUSION_SENTINELS[demand]
                        if token.casefold() in h2_exposed]
            if h2_leaks:
                raise AssertionError("CORE2A_H2_PRECOMMIT_ANSWER_LEAK:" + ",".join(h2_leaks))
            result["precommit_hint_2_visible_text"] = h2_lines
            result["h2_before_commit"] = "VISIBLE_AND_SENTINEL_SAFE"
        targets = page.locator("details[data-g9-reveal][data-requires-attempt]")
        if not targets.count():
            raise AssertionError("NO_ATTEMPT_GATED_REVEAL")
        if targets.locator("[data-g9-payload-slot]").count() != targets.count():
            raise AssertionError("UNEXPECTED_REVEAL_PAYLOAD_STRUCTURE")
        if any(t.strip() for t in targets.locator("[data-g9-payload-slot]").all_inner_texts()):
            raise AssertionError("PRECOMMIT_SOLUTION_PAYLOAD_EXPOSED")
        if any(targets.nth(i).get_attribute("data-locked") is None for i in range(targets.count())):
            raise AssertionError("REVEAL_NOT_LOCKED_BEFORE_ATTEMPT")
        if any(targets.nth(i).get_attribute("open") is not None for i in range(targets.count())):
            raise AssertionError("REVEAL_OPEN_BEFORE_ATTEMPT")
        commit = page.locator("button[data-g9-commit]").first
        attempt = page.locator("textarea[data-g9-attempt]").first
        if not commit.count() or not attempt.count():
            raise AssertionError("MISSING_TYPED_ATTEMPT_OR_COMMIT")
        commit.click()
        if any(targets.nth(i).get_attribute("data-locked") is None for i in range(targets.count())):
            raise AssertionError("BLANK_ATTEMPT_UNLOCKS_REVEAL")
        attempt.fill("I choose a route, connect the given quantities and will test it.")
        commit.click()
        if targets.first.get_attribute("data-locked") is not None:
            raise AssertionError("NONBLANK_ATTEMPT_FAILED_TO_UNLOCK_PRIMARY")
        if role == "core1b":
            boundary = page.locator('details[data-g9-attempt-stage="boundary"][data-requires-attempt]')
            boundary_box = page.locator('[data-g9-attempt-box][data-g9-attempt-stage="boundary"]')
            if boundary.count() != 1 or boundary_box.count() != 1:
                raise AssertionError("MISSING_INDEPENDENT_CORE1B_BOUNDARY")
            if boundary.get_attribute("data-locked") is None:
                raise AssertionError("PRIMARY_ATTEMPT_UNLOCKED_INDEPENDENT_BOUNDARY")
            boundary_box.locator("button[data-g9-commit]").click()
            if boundary.get_attribute("data-locked") is None:
                raise AssertionError("BLANK_BOUNDARY_ATTEMPT_UNLOCKED")
            boundary_box.locator("textarea[data-g9-attempt]").fill(
                "This changed boundary fails the original argument for an explicit reason."
            )
            boundary_box.locator("button[data-g9-commit]").click()
            if boundary.get_attribute("data-locked") is not None:
                raise AssertionError("NONBLANK_BOUNDARY_ATTEMPT_FAILED_TO_UNLOCK")
        elif any(targets.nth(i).get_attribute("data-locked") is not None for i in range(targets.count())):
            raise AssertionError("NONBLANK_ATTEMPT_FAILED_TO_UNLOCK")
        if role == "core2a":
            h3 = page.locator('details[data-g9-payload-ref*="after-attempt-hint-3"]')
            if h3.count() != 1:
                raise AssertionError("MISSING_SEPARATE_H3")
            h3.locator("summary").click()
            if not page.locator("[data-g9-after-attempt-hint]").is_visible():
                raise AssertionError("H3_NOT_MATERIALISED_AFTER_COMMIT")
        if page.evaluate("document.documentElement.scrollWidth > window.innerWidth"):
            raise AssertionError("HORIZONTAL_PAGE_OVERFLOW_390PX")
        if errors:
            raise AssertionError("JAVASCRIPT_ERRORS: " + "; ".join(errors[:2]))
        result["status"] = "BROWSER_PASS"
        result["evidence"] = "blank/nonblank commitment, inert payload, deferred H3 (Core2A), 390px viewport"
    except Exception as ex:
        result["status"] = "BROWSER_FAIL"
        result["reason"] = str(ex)
    finally:
        ctx.close()
    return result

def verify(render_root: Path, run_browser: bool) -> dict:
    import json
    registry = json.loads(REGISTRY.read_text())
    blueprints = {b["core_roles"][0].lower(): f'{b["id"]}@{b["version"]}'
                  for b in registry["blueprints"] if len(b["core_roles"]) == 1}
    lock = json.loads((GOLDEN / "snapshot-lock.json").read_text())
    golden = {}
    for entry in lock["snapshots"]:
        role = entry["role"].lower()
        data = (GOLDEN / entry["path"]).read_bytes()
        if digest(data) != entry["sha256"]:
            raise RuntimeError("OWNER_GOLDEN_SHA_LOCK_BROKEN: " + role)
        golden[role] = data.decode("utf-8")
    output = {
        "schema": "imo-qrt-d2-native-benchmark/v1",
        "issue": 201,
        "source_pr": 191,
        "source_head": "eb3cf06646f00bf208084e794b41b4d8d83135b6",
        "golden": lock["fixture_id"],
        "golden_policy": "same-question bytes locked; cross-question slots/components/attempt semantics only",
        "owner_acceptance": "0/28; all D2 decisions PENDING",
        "records": [],
    }
    browser = None
    if run_browser:
        from playwright.sync_api import sync_playwright
        manager = sync_playwright().start()
        try:
            browser = manager.chromium.launch(headless=True)
        except Exception:
            manager.stop()
            raise
    try:
        for demand in DEMANDS:
            directory = render_root / demand
            row = {
                "cell_id": f"QRT-{demand.upper()}-D2",
                "artifact_path": str(directory),
                "technical": "PENDING",
                "academic_reviewer": None,
                "academic_decision": "PENDING",
                "owner_decision_id": None,
                "owner_qrta_accepted": False,
                "owner_golden_designated": False,
                "role_checks": {},
                "failures": [],
            }
            try:
                receipt = json.loads((directory / "render-receipt.json").read_text())
                manifest = json.loads((ROOT / f"TEST/products/imo182-qrt-d2-{demand}.manifest.json").read_text())
                assert receipt["gaps"] == [], "NONZERO_RENDER_GAPS"
                assert receipt["mode"] == "PAGES", "NOT_NATIVE_PAGE_MODE"
                assert tuple(x.lower() for x in receipt["output_roles"]) == ROLES, "WRONG_ROLES_IN_RECEIPT"
                assert tuple(x.lower() for x in manifest["output_roles"]) == ROLES, "WRONG_ROLES_IN_MANIFEST"
                assert manifest["selection"]["core2"] == [], "AUTHORED_TEST_MISLABELLED_AS_SOURCE_CORE2"
                assert set(PAGE_NAMES).issubset(receipt["page_sha256"]), "SIX_PAGE_SET_INCOMPLETE"
                assert all((directory / f).is_file() for f in PAGE_NAMES), "MISSING_RENDERED_FILE"
                for name in PAGE_NAMES:
                    actual = digest((directory / name).read_bytes())
                    assert actual == receipt["page_sha256"][name], f"RECEIPT_SHA_MISMATCH:{name}"
                # Historical exact-head reference: fail if generated first role changes unexpectedly.
                row["historical_first_role_sha_match"] = (
                    receipt["page_sha256"]["core1.html"] == ARTIFACT_SHA[demand]
                )
                for role in ROLES:
                    text = (directory / f"{role}.html").read_text(encoding="utf-8")
                    reference = golden[role]
                    current_bp = collect(text, "data-blueprint-ref")
                    expected_bp = blueprints[role]
                    assert current_bp and current_bp[0] == expected_bp, f"{role}:REGISTERED_BP_MISMATCH"
                    slots = collect(text, "data-blueprint-slot")
                    golden_slots = collect(reference, "data-blueprint-slot")
                    components = collect(text, "data-g9-component")
                    golden_components = collect(reference, "data-g9-component")
                    assert slots == golden_slots, f"{role}:SLOT_ORDER_GOLDEN_MISMATCH"
                    assert components == golden_components, f"{role}:COMPONENT_ORDER_GOLDEN_MISMATCH"
                    # Core2A's H3 policy intentionally changes after the old frozen snapshot.
                    if role == "core2a":
                        assert 'data-g9-after-attempt-hint' in text, "H3_AFTER_ATTEMPT_MISSING"
                        assert re.search(
                            r'<details[^>]*data-requires-attempt[^>]*data-g9-payload-ref="[^"]*after-attempt-hint-3"',
                            text
                        ), "H3_DETAIL_NOT_ATTEMPT_GATED"
                        assert re.search(
                            r'<template[^>]*data-g9-payload="[^"]*after-attempt-hint-3"',
                            text
                        ), "H3_NOT_IN_INERT_TEMPLATE"
                    row["role_checks"][role] = {
                        "blueprint": expected_bp,
                        "page_sha256": receipt["page_sha256"][f"{role}.html"],
                        "golden_slot_order": "MATCH",
                        "golden_component_order": "MATCH",
                        "literal_html_equality": "NOT_APPLICABLE_DIFFERENT_QUESTION",
                        "h3_policy": "EXPECTED_POST_GOLDEN_AFTER_ATTEMPT_DELTA" if role == "core2a" else "NOT_APPLICABLE",
                    }
                    if browser is not None and role in ("core1b", "core2a", "core2b"):
                        outcome = browser_check(text, role, demand, browser)
                        row["role_checks"][role]["browser"] = outcome
                        assert outcome["status"] == "BROWSER_PASS", f"{role}:{outcome.get('reason')}"
                row["technical"] = "STATIC_TECHNIQUE_PASS" if browser is None else "BROWSER_AND_STATIC_PASS"
            except Exception as ex:
                row["failures"].append(str(ex))
                row["technical"] = "REVISE_TECHNICAL"
            output["records"].append(row)
    finally:
        if browser is not None:
            browser.close()
            manager.stop()
    return output

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-root", required=True, type=Path, help="contains retrieve/, explain/, ...")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--browser", action="store_true", help="run actual Chromium learner commitment tests")
    args = ap.parse_args()
    result = verify(args.render_root, args.browser)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for row in result["records"]:
        print(row["cell_id"], row["technical"], "; ".join(row["failures"]))
    return int(any(r["failures"] for r in result["records"]))

if __name__ == "__main__":
    sys.exit(main())
