#!/usr/bin/env python3
"""Fail-closed source-to-learner navigation check for the IMO Index Laws pilot.

This checks the already rendered pages and calls existing release_authority,
not a second canonical, academic, QRT, source-custody or Owner approval engine.
It grants nothing; release is possible only if every independent prerequisite
and exact published artifact is present and current.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
from urllib.parse import urlsplit

from Shared.tools import build_pages_site, release_authority

REPO = Path(__file__).resolve().parents[2]
SUBTOPIC = "NS-INDEX-LAWS"
PAGE = "mathematics/number-systems/index-laws/index.html"
PILOT = "TEST/imo-research/intake/imo-index-laws-subtopic-pilot.v1.json"
ROLES = {
    "CORE1A": ("core1a_product_url", "CANDIDATE_NOT_PUBLISHED", "CORE1A.html"),
    "CORE2A": ("core2a_authored_product_url", "CANDIDATE_NOT_PUBLISHED", "CORE2A.html"),
    "CORE2": ("core2_source_product_url", "SOURCE_CUSTODY_AND_RIGHTS_HOLD", "CORE2.html"),
}
INTERACTIVE = {"a", "button", "input", "select", "textarea", "form"}


class RouteHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main = []
        self.cards = []
        self.current = None
        self.depth = 0
        self.outside_links = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "main":
            self.main.append(attr)
        if tag == "article" and self.current is not None:
            self.depth += 1
        elif tag == "article" and attr.get("data-g9-role"):
            self.current = {"attrs": attr, "actions": []}
            self.cards.append(self.current)
            self.depth = 1
        if self.current is not None:
            if tag in INTERACTIVE or any(k.lower().startswith("on") for k in attr):
                self.current["actions"].append((tag, attr))
        elif tag == "a":
            self.outside_links.append(attr.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "article" and self.current is not None:
            self.depth -= 1
            if self.depth == 0:
                self.current = None


def _within(repo: Path, value: str, prefix: str) -> Path | None:
    """Reject traversal, symlinks, absolute paths and wrong-root receipts."""
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or "." in p.parts or not value.startswith(prefix + "/"):
        return None
    root = repo.resolve()
    result = (root / value).resolve()
    try:
        result.relative_to((root / prefix).resolve())
    except ValueError:
        return None
    return result if result.is_file() else None


def _safe_target(href: str) -> str | None:
    if not isinstance(href, str) or not href or "\\" in href:
        return None
    url = urlsplit(href)
    if url.scheme or url.netloc or url.query or url.fragment or href.startswith("/"):
        return None
    target = posixpath.normpath(posixpath.join(posixpath.dirname(PAGE), url.path))
    if not target.startswith("mathematics/number-systems/index-laws/") or not target.endswith(".html"):
        return None
    return target


def _check_published(repo: Path, role: str, card: dict, pilot: dict) -> list[str]:
    issues = []
    attrs = card["attrs"]
    actions = card["actions"]
    declared, _, role_file = ROLES[role]
    if attrs.get("data-g9-authority") != "RELEASED":
        issues.append(f"{role}: enabled role is not marked RELEASED")
    if pilot.get("scope", {}).get("launch_authorized") is not True:
        issues.append(f"{role}: provisional crosswalk explicitly forbids launch")
    if len(actions) != 1 or actions[0][0] != "a":
        issues.append(f"{role}: enabled role requires exactly one plain anchor, no other controls")
        return issues

    href = actions[0][1].get("href")
    target = _safe_target(href)
    if target is None or pilot.get("routing", {}).get(declared) != "/" + (target or ""):
        issues.append(f"{role}: missing, escaping or unpinned generated learner target")
        return issues

    receipt_path = _within(repo, attrs.get("data-g9-release-receipt", ""), "Releases/receipts")
    if receipt_path is None:
        issues.append(f"{role}: no safe committed release receipt")
        return issues
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        verdict = release_authority.verify_receipt(receipt, repo)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        issues.append(f"{role}: release receipt verification error: {type(exc).__name__}")
        return issues
    if verdict.get("verified") is not True:
        issues.append(f"{role}: release receipt is not current/verified")
        return issues
    if receipt.get("subject") != "Mathematics" or role not in receipt.get("plan", {}).get("products", []):
        issues.append(f"{role}: release receipt subject/role mismatch")
    if receipt.get("validation", {}).get("state") != "RELEASED":
        issues.append(f"{role}: receipt is not a released product")

    pubpath = receipt.get("publication", {}).get("path", "")
    original = _within(repo, pubpath + "/" + role_file, "Mathematics/content")
    visible = receipt.get("publication", {}).get("learner_visible_files", [])
    if original is None or not any(isinstance(row, dict) and row.get("path") == role_file for row in visible):
        issues.append(f"{role}: role artifact absent from authenticated publication")
        return issues
    learner = (repo / "public" / target).resolve()
    mirror = (repo / "docs" / target).resolve()
    try:
        raw = original.read_bytes()
        if learner.read_bytes() != raw:
            issues.append(f"{role}: exposed artifact differs from approved publication bytes")
        if mirror.read_bytes() != build_pages_site._public_payload(target, raw):
            issues.append(f"{role}: Pages projection differs from approved publication bytes")
    except (OSError, ValueError):
        issues.append(f"{role}: generated public/docs artifact missing or invalid")

    if role == "CORE2":
        if not receipt.get("source_receipt"):
            issues.append("CORE2: authentic source receipt missing")
        questions = pilot.get("source_questions", [])
        source_id = attrs.get("data-g9-source-question-id")
        matches = [r for r in questions if r.get("question_id") == source_id]
        if (pilot.get("scope", {}).get("source_core2_admitted", 0) < 1 or
            len(matches) != 1 or
            not matches[0].get("source_core2_admitted") or
            not matches[0].get("source_core2_eligible") or
            matches[0].get("rights_status") not in {"REPRODUCTION_GRANTED", "RIGHTS_CLEARED"}):
            issues.append("CORE2: source identity, fidelity, custody/admission or rights remain held")
    return issues


def findings(repo: Path = REPO, pilot: dict | None = None, html: str | None = None) -> list[str]:
    repo = Path(repo)
    if pilot is None:
        pilot = json.loads((repo / PILOT).read_text(encoding="utf-8"))
    if html is None:
        html = (repo / "public" / PAGE).read_text(encoding="utf-8")
    parsed = RouteHTML()
    parsed.feed(html)
    issues = []
    scope = pilot.get("scope", {})
    if (scope.get("topic_id"), scope.get("subtopic_id")) != ("NS", SUBTOPIC):
        issues.append("pilot academic topic/subtopic identity differs")
    if len(parsed.main) != 1 or parsed.main[0].get("data-g9-subtopic") != SUBTOPIC:
        issues.append("homepage missing/mismatched subtopic identity")
    if len(parsed.cards) != len(ROLES):
        issues.append("exactly three distinct Core roles required")
    roles = [c["attrs"].get("data-g9-role") for c in parsed.cards]
    if len(set(roles)) != len(roles) or set(roles) != set(ROLES):
        issues.append("duplicate, unsupported or missing role")
    for card in parsed.cards:
        role = card["attrs"].get("data-g9-role")
        if role not in ROLES:
            continue
        attrs = card["attrs"]
        active = attrs.get("data-g9-launch-authorized")
        if active == "false":
            if attrs.get("data-g9-authority") != ROLES[role][1]:
                issues.append(f"{role}: held authority label is incorrect")
            if card["actions"]:
                issues.append(f"{role}: held role contains an interactive product action")
            if attrs.get("data-g9-release-receipt"):
                issues.append(f"{role}: held card must not advertise a release receipt")
        elif active == "true":
            issues.extend(_check_published(repo, role, card, pilot))
        else:
            issues.append(f"{role}: missing/invalid explicit launch status")
    # A role may not be smuggled in as an unrelated anchor outside the role cards.
    for href in parsed.outside_links:
        path = urlsplit(href).path.lower()
        if (any(token in path for token in ("core1a.html", "core2a.html", "core2.html", "/products/")) or
            "/test/imo-grade9/" in path):
            issues.append("unprotected Core product/TEST link outside a role card")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--enforce", action="store_true", help="return nonzero when unauthorized actions are found")
    args = parser.parse_args()
    problems = findings()
    print(json.dumps({"route": PAGE, "scope": "RELEASE_GUARD_NO_AUTHORITY_GRANT",
                      "passed": not problems, "findings": problems}, indent=2))
    return 1 if args.enforce and problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
