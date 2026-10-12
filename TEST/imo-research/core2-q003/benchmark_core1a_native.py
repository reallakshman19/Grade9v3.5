#!/usr/bin/env python3
"""Native Core1A Q003 versus G-MATH-LINEAR-CONSTRAINT: source-safe structure only.

This script never composes HTML. Both outputs use Shared/tools/render_core.py.
The original and all generated pages remain ignored on the secure operator's host.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAGE = HERE / ".private" / "core1a"
GOLDEN = ROOT / "golden" / "units" / "G-MATH-LINEAR-CONSTRAINT" / "rendered"


class Markers(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.components = Counter()
        self.roles = Counter()
        self.attempts = 0
        self.commits = 0

    def handle_starttag(self, tag, attrs) -> None:
        values = dict(attrs)
        if "data-g9-component" in values:
            self.components[values["data-g9-component"]] += 1
        if "data-g9-role" in values:
            self.roles[values["data-g9-role"]] += 1
        if "data-g9-attempt-box" in values:
            self.attempts += 1
        if "data-g9-commit" in values:
            self.commits += 1


def snapshot(path: Path) -> dict:
    raw = path.read_bytes()
    html = raw.decode("utf-8")
    parser = Markers()
    parser.feed(html)
    return {
        "sha256": sha256(raw).hexdigest(), "bytes": len(raw),
        "registered_blueprint_marker": "BP-CORE1A-CONSTRUCTION" in html,
        "core1a_role": parser.roles["CORE1A"] > 0,
        "attempt_box_count": parser.attempts,
        "typed_commit_count": parser.commits,
        "components": sorted(parser.components),
        "component_counts": dict(sorted(parser.components.items())),
    }


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--private-input", required=True, type=Path)
    ap.add_argument("--custody-receipt", type=Path)
    args = ap.parse_args()
    if not (ROOT / "Shared/tools/render_core.py").is_file():
        ap.error("BLOCKED: full native checkout and Shared/tools/render_core.py required")
    command = [sys.executable, "-I", str(HERE / "build_private_core1a.py"),
               "--private-input", str(args.private_input.resolve())]
    if args.custody_receipt:
        command += ["--custody-receipt", str(args.custody_receipt.resolve())]
    run(command)  # emits only native Core1A via the registered renderer
    run([sys.executable, "-I", str(ROOT / "Shared/tools/build_golden.py"),
         "--id", "G-MATH-LINEAR-CONSTRAINT"])  # same registered renderer
    private_dir, golden_dir = STAGE / "rendered", GOLDEN
    private = snapshot(private_dir / "core1a.html")
    golden = snapshot(golden_dir / "core1a.html")
    native_receipts = {
        "Q003_CORE1A": json.loads((private_dir / "render-receipt.json").read_text(encoding="utf-8")),
        "G_MATH_LINEAR_CONSTRAINT": json.loads((golden_dir / "render-receipt.json").read_text(encoding="utf-8"))
    }
    for name, snap in (("Q003_CORE1A", private), ("G_MATH_LINEAR_CONSTRAINT", golden)):
        snap["structural_role_ok"] = (snap["registered_blueprint_marker"] and snap["core1a_role"]
                                       and snap["attempt_box_count"] >= 1 and snap["typed_commit_count"] >= 1)
    gaps = {name: len(receipt.get("gaps", [])) for name, receipt in native_receipts.items()}
    status = ("STRUCTURAL_CHECK_ONLY"
              if all(gap == 0 for gap in gaps.values()) and
              private["structural_role_ok"] and golden["structural_role_ok"]
              else "NATIVE_GAPS_OR_STRUCTURE_FINDINGS")
    report = {
        "issue": 183, "task": "183-T4-G2-W1", "aim": "v3.1.0", "outcome": "O2",
        "source": "NATIVE_ONLY: build_private_core1a.py and build_golden.py use Shared/tools/render_core.py",
        "source_original_privacy": "PRIVATE_INPUT_AND_HTML_NOT_PUBLISHED",
        "golden": "G-MATH-LINEAR-CONSTRAINT",
        "golden_status": "CANDIDATE_NOT_OWNER_BLESSED",
        "original_question_id": "SOF-IMO-G09-L1-2023-24-A-Q003",
        "original_input_sha256": "b263644cd1dd8aca689582232c9b8495f05ec07f3ffeaff3a18f414e6e1227f9",
        "author_input_sha256": sha256((HERE / "core1a-authored.v1.json").read_bytes()).hexdigest(),
        "renderer_digest": {k: v.get("digest") for k, v in native_receipts.items()},
        "renderer_version": {k: v.get("renderer") for k, v in native_receipts.items()},
        "gaps": gaps, "pages": {"Q003_CORE1A": private, "G_MATH_LINEAR_CONSTRAINT": golden},
        "golden_components_absent_from_Q003": sorted(set(golden["components"]) - set(private["components"])),
        "Q003_components_absent_from_golden": sorted(set(private["components"]) - set(golden["components"])),
        "scope": "Native structural benchmark, NOT browser/pixel/A4/academic/QRT approval",
        "status": status, "owner_qrt_accepted": False, "same_page_a4": "NOT_RUN",
        "rights_granted": False, "published": False
    }
    STAGE.mkdir(parents=True, exist_ok=True)
    path = STAGE / "native-core1a-golden-comparison.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("CORE1A_NATIVE_GOLDEN_COMPARISON " + status)
    print("source-safe receipt: " + str(path))
    return 0 if status == "STRUCTURAL_CHECK_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
