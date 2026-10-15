"""Read-only real-Chromium QRT-RETRIEVE-D1 per-card disclosure + KaTeX witness.

Run only after exact-source Git checkout. Does not certify academic claims.
Requires playwright Chromium; does not write to source HTML.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "standalone/mathematics-imo-grade9-master-suite.html"
BANK = ROOT / "Mathematics/question-bank"
FILES = (
    "sof-imo-2023-24-set-a.core2.json",
    "sof-imo-2024-25-set-b.core2.json",
    "sof-imo-2025-26-set-a.core2.json",
    "sof-imo-2025-26-set-b.core2.json",
    "sof-imo-hots-olympiad-expansion.core2.json",
    "sof-imo-sample-2026-27.core2.json",
)


def main() -> int:
    ids = sorted(q["id"] for file in FILES
                 for q in json.loads((BANK / file).read_text(encoding="utf-8"))["questions"]
                 if q.get("cognitive_classification", {}).get("qrt_cell") == "QRT-RETRIEVE-D1")
    assert len(ids) == 12, "source tile denominator drift"
    report = {"tile": "QRT-RETRIEVE-D1", "source_sha":
              "90c859705feb0dfcedc6d33a013d9e563b7cac9d",
              "scope": "RESEARCH_STANDALONE_BROWSER_ONLY",
              "viewports": [], "records": [],
              "academic_acceptance": "NOT_GRANTED"}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        for width in (390, 1280):
            page = browser.new_page(viewport={"width": width, "height": 900})
            errors = []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.goto(HTML.as_uri(), wait_until="domcontentloaded")
            page.locator(".qb-question").first.wait_for(timeout=20000)
            page.wait_for_function("document.querySelectorAll('.katex').length > 10",
                                   timeout=20000)
            total = page.locator(".qb-question").count()
            assert total == 260, f"{width}: rendered total {total}"
            katex = page.locator(".katex").count()
            overflow = page.evaluate("document.documentElement.scrollWidth > innerWidth")
            report["viewports"].append({"width": width, "questions": total,
                                        "katex_nodes": katex,
                                        "page_overflow": overflow})
            for qid in ids:
                entry = {"id": qid, "width": width, "verdict": "PASS",
                         "location": "#q-" + qid, "rules": []}
                try:
                    card = page.locator('[id="q-' + qid + '"]')
                    card.wait_for(state="attached", timeout=10000)
                    solution = page.locator('[id="sol-disc-' + qid + '"]')
                    diag = page.locator('[id="diag-disc-' + qid + '"]')
                    tier1 = page.locator('[id="hint1-' + qid + '"]')
                    tier2 = page.locator('[id="hint2-' + qid + '"]')
                    attempt = page.locator('[id="att-' + qid + '"]')
                    commit = page.locator('[id="commit-' + qid + '"]')
                    assert solution.get_attribute("hidden") is not None
                    assert solution.get_attribute("inert") is not None
                    assert diag.get_attribute("hidden") is not None
                    assert tier2.get_attribute("hidden") is not None
                    assert not solution.is_visible()
                    assert not tier2.is_visible()
                    assert not card.locator(".katex-error").count()
                    outer = card.locator(".qb-support-container > details").first
                    outer.locator("summary").first.click()
                    tier1.locator("summary").click()
                    tier2.wait_for(state="visible", timeout=5000)
                    assert not solution.is_visible(), "hint disclosed solution before commit"
                    commit.click()
                    assert not solution.is_visible(), "blank attempt disclosed solution"
                    assert attempt.get_attribute("aria-invalid") == "true"
                    attempt.fill("I identified the criterion and am recording my chosen answer.")
                    commit.click()
                    assert solution.is_visible(), "committed attempt cannot see solution"
                    assert diag.is_visible(), "committed attempt cannot see diagnosis"
                    assert attempt.get_attribute("readonly") is not None
                    assert commit.get_attribute("aria-expanded") == "true"
                    assert not card.locator(".katex-error").count(), "KaTeX parse error in card"
                except Exception as exc:
                    entry["verdict"] = "FAIL"
                    entry["rules"].append("BROWSER_COMMIT_HINT_OR_MATH_" + type(exc).__name__)
                    entry["detail"] = str(exc)[:400]
                report["records"].append(entry)
                print(qid + " | " + entry["verdict"] + " | width " + str(width) +
                      " | " + (",".join(entry["rules"]) or "RENDER_HINT_COMMIT_MATH_PASS"),
                      flush=True)
            report["viewports"][-1]["page_errors"] = errors
            page.close()
        browser.close()
    report["failures"] = sum(x["verdict"] == "FAIL" for x in report["records"]) + sum(
        bool(v["page_errors"]) or v["page_overflow"] or v["katex_nodes"] < 10
        for v in report["viewports"])
    out = ROOT / "build/imo-qrt-249/retrieve-d1-browser.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Browser witness " + json.dumps({"failures": report["failures"],
                                          "widths": report["viewports"]}), flush=True)
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
