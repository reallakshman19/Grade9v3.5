#!/usr/bin/env python3
"""Independent real-Chromium witness for Grade9 research repair PR #259.

Executes learner-facing page JavaScript only in an isolated, read-only CI job.
Never executes candidate Python, mutates source, or certifies academic/QRT claims.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from playwright.sync_api import sync_playwright

RELATIVE = "public/test/imo-grade9/core2.html"
WIDTHS = (320, 390, 768, 1280)
SCHEMA = "imo-qrt-independent-browser/v1"


def _head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   text=True).strip()


def _run_one(browser, html_path: Path, width: int, out: Path) -> dict:
    page = browser.new_page(viewport={"width": width, "height": 860})
    page.set_default_timeout(15000)
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    try:
        page.goto(html_path.as_uri(), wait_until="domcontentloaded")
        page.locator(".qb-question").first.wait_for()
        card_count = page.locator(".qb-question").count()
        if card_count != 260:
            raise AssertionError(f"Rendered card denominator {card_count} instead of 260")

        # Whole corpus first-view gate: no programmatically visible teacher
        # solutions, diagnosis, answer-highlight markup or pre-committed state.
        corpus = page.evaluate("""() => {
          const cards = Array.from(document.querySelectorAll('.qb-question'));
          return {
            count: cards.length,
            protected: cards.filter(c => {
              const id = c.id.slice(2);
              const solution = document.getElementById('sol-disc-'+id);
              const diag = document.getElementById('diag-disc-'+id);
              const button = document.getElementById('commit-'+id);
              const notes = document.getElementById('att-'+id);
              const opts = c.querySelectorAll('.qb-option-card');
              if (!solution || !diag || !button || !notes || opts.length!==4) return false;
              const hidden = el => el.hasAttribute('hidden') &&
                el.hasAttribute('inert') && getComputedStyle(el).display==='none';
              return hidden(solution) && hidden(diag) &&
                button.getAttribute('aria-expanded')==='false' &&
                Array.from(opts).every(o => !o.hasAttribute('style') &&
                  !o.hasAttribute('data-correct'));
            }).length
          };
        }""")
        if corpus["protected"] != 260:
            raise AssertionError(f"First-load hidden-state protection {corpus['protected']}/260")

        # Independently execute early, central, and late learner journeys. A
        # browser reload must not carry a prior answer reveal into a fresh visit.
        paths = []
        for index in (0, 130, 259):
            card = page.locator(".qb-question").nth(index)
            qid = card.get_attribute("id")[2:]
            solution = page.locator("#sol-disc-" + qid)
            diagnosis = page.locator("#diag-disc-" + qid)
            button = page.locator("#commit-" + qid)
            notes = page.locator("#att-" + qid)
            if solution.is_visible() or diagnosis.is_visible():
                raise AssertionError("Uncommitted solution is visible: " + qid)
            first_hint = page.locator("#hint1-" + qid)
            second_hint = page.locator("#hint2-" + qid)
            if first_hint.get_attribute("hidden") is not None:
                raise AssertionError("Tier1 incorrectly hidden at load: " + qid)
            if second_hint.get_attribute("hidden") is None or second_hint.is_visible():
                raise AssertionError("Tier2 available without Tier1: " + qid)
            card.scroll_into_view_if_needed()
            ladder = card.locator(".qb-support-container > details.qb-disclosure").first
            ladder.locator("summary").first.click()
            if not first_hint.is_visible() or second_hint.is_visible():
                raise AssertionError("Initial hint ladder role drift: " + qid)
            first_hint.locator("summary").click()
            second_hint.wait_for(state="visible")
            if solution.is_visible() or diagnosis.is_visible():
                raise AssertionError("Hint rung bypassed attempt gate: " + qid)
            second_hint.locator("summary").click()
            if second_hint.get_attribute("open") is None:
                raise AssertionError("Tier2 expansion failed: " + qid)
            if solution.is_visible() or diagnosis.is_visible():
                raise AssertionError("Tier2 revealed solution before commit: " + qid)
            button.focus()
            page.keyboard.press("Enter")
            if solution.is_visible() or notes.get_attribute("aria-invalid") != "true":
                raise AssertionError("Empty keyboard commit bypass: " + qid)
            notes.fill("...  !?")
            button.click()
            if solution.is_visible():
                raise AssertionError("Punctuation-only attempt bypass: " + qid)
            notes.fill("I first choose option A and will compare the stated relations.")
            button.click()
            if not solution.is_visible() or not diagnosis.is_visible():
                raise AssertionError("Solution failed to unlock after typed working: " + qid)
            if notes.get_attribute("readonly") is None or button.get_attribute("aria-expanded") != "true":
                raise AssertionError("Commit state missing: " + qid)
            summary = solution.locator("summary")
            if not summary.evaluate("(e) => e === document.activeElement"):
                raise AssertionError("Solution keyboard focus not transferred: " + qid)
            summary.press("Enter")
            if solution.get_attribute("open") is not None:
                raise AssertionError("Keyboard details-close ineffective: " + qid)
            summary.press("Enter")
            if solution.get_attribute("open") is None:
                raise AssertionError("Keyboard details-reopen ineffective: " + qid)
            paths.append({"index": index, "question_id": qid, "empty_refused": True,
                          "punctuation_refused": True, "committed_reveal": True,
                          "keyboard_toggle": True,
                          "tier1_to_tier2": True, "precommit_solution_hidden_after_hints": True})

        page.wait_for_function("document.querySelectorAll('.katex').length > 0",
                               timeout=12000)
        math_count = page.locator(".katex").count()
        page_overflow = page.evaluate(
            "document.documentElement.scrollWidth > window.innerWidth")
        overflow_candidates = page.evaluate("""() => Array.from(document.querySelectorAll('body *'))
          .filter(el => {
            const r=el.getBoundingClientRect();
            const cs=getComputedStyle(el);
            return r.width>0 && r.right>innerWidth+2 && cs.display!=='none' &&
              cs.visibility!=='hidden';
          }).map(el => {
            const r=el.getBoundingClientRect();
            const svg=el.closest('svg');
            const q=el.closest('.qb-question');
            const katex=el.closest('.katex');
            const parent=el.parentElement;
            const root=svg ? svg.getBoundingClientRect() : null;
            return {tag:el.tagName, id:String(el.id).slice(0,75),
              class_name:String(el.className).slice(0,110),
              right:Math.round(r.right), width:Math.round(r.width),
              question_id:q ? q.id : null,
              inside_katex:!!katex,
              root_svg_id:svg ? svg.id : null,
              svg_width:root ? Math.round(root.width) : null,
              svg_viewbox:svg ? svg.getAttribute('viewBox') : null,
              svg_parent_class:svg && svg.parentElement ?
                  String(svg.parentElement.className).slice(0,110) : null,
              parent_tag:parent ? parent.tagName : null,
              parent_class:parent ? String(parent.className).slice(0,100) : null};
          }).sort((a,b) => b.right - a.right).slice(0,16)""") if page_overflow else []
        # Isolation probes detect what actually expands document scrollWidth.
        # Giant path geometry inside a tiny clipped KaTeX svg can be a false
        # culprit; hiding groups temporarily is a diagnosis, never a source edit.
        overflow_isolation = page.evaluate("""() => {
          const groups = {
            katex_svg: '.katex svg',
            katex_whole: '.katex',
            question_cards: '.qb-question',
            core_topic_cards: '.topic-module-card',
            sticky_topic_nav: '.topic-sticky-bar',
            active_tab: '.tab-content.active',
            all_svg: 'svg',
            page_header: 'header',
            header_shell: '.g9-shell',
            header_inner: '.shell-inner',
            header_brand: '.shell-inner .brand',
            header_nav: '.nav-tabs',
            header_actions: '.header-actions',
            page_main: 'main',
            page_footer: 'footer',
            root_body_children: 'body > *'
          };
          const base = document.documentElement.scrollWidth;
          const result = {viewport:innerWidth, document_scroll_width:base, groups:{},
            top_level: Array.from(document.body.children).map(el=>{
              const r=el.getBoundingClientRect();
              return {tag:el.tagName, id:el.id, class_name:String(el.className).slice(0,70),
                left:Math.round(r.left), right:Math.round(r.right),
                width:Math.round(r.width), scroll_width:el.scrollWidth,
                min_width:getComputedStyle(el).minWidth,
                position:getComputedStyle(el).position};
            })};
          for (const [name,selector] of Object.entries(groups)) {
            const elems = Array.from(document.querySelectorAll(selector));
            const prior = elems.map(el=>el.getAttribute('style'));
            elems.forEach(el=>el.style.setProperty('display','none','important'));
            result.groups[name] = {elements:elems.length,
              width_without:document.documentElement.scrollWidth};
            elems.forEach((el,i)=>{
              if (prior[i]===null) el.removeAttribute('style');
              else el.setAttribute('style',prior[i]);
            });
          }
          return result;
        }""") if page_overflow else {}
        if errors:
            raise AssertionError("Uncaught learner-side JavaScript errors: "+repr(errors[:5]))
        out.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(out / f"independent-width-{width}.png"), full_page=False)
        page.reload(wait_until="domcontentloaded")
        first = page.locator(".qb-question").first.get_attribute("id")[2:]
        if page.locator("#sol-disc-" + first).is_visible():
            raise AssertionError("Answer visible after reload")
        return {"viewport": width, "corpus_questions": card_count,
                "first_view_protected": corpus["protected"],
                "attempt_paths": paths, "math_katex_nodes": math_count,
                "document_horizontal_overflow": page_overflow,
                "overflow_candidates": overflow_candidates,
                "overflow_isolation": overflow_isolation,
                "behavior_verdict": "FAIL_DOCUMENT_HORIZONTAL_OVERFLOW" if page_overflow else "PASS",
                "javascript_errors": [], "reload_protection": "PASS"}
    finally:
        page.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate-root", type=Path, required=True)
    ap.add_argument("--candidate-sha", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--screenshots", type=Path, required=True)
    args = ap.parse_args(argv)
    root = args.candidate_root.resolve()
    report = {
        "schema": SCHEMA, "candidate_sha": args.candidate_sha,
        "scope": "RESEARCH_STANDALONE_BROWSER_ONLY",
        "status": "NOT_RUN", "academic_verdict": "REVIEW_REQUIRED",
        "source_rights": "NOT_VERIFIED", "native_core_admission": "NOT_GRANTED",
        "observations": [], "failures": [],
    }
    status = 1
    try:
        if _head(root) != args.candidate_sha:
            raise ValueError("CANDIDATE_EXACT_SHA_MISMATCH")
        html_path = root / RELATIVE
        report["html_sha256"] = sha256(html_path.read_bytes()).hexdigest()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for width in WIDTHS:
                    report["observations"].append(
                        _run_one(browser, html_path, width, args.screenshots))
            finally:
                browser.close()
        overflowing = [x["viewport"] for x in report["observations"]
                       if x["document_horizontal_overflow"]]
        if overflowing:
            report["status"] = "FAIL"
            report["failures"].append("DOCUMENT_HORIZONTAL_OVERFLOW_AT_VIEWPORTS:" +
                                      ",".join(map(str, overflowing)))
            status = 1
        else:
            report["status"] = "BROWSER_BEHAVIOR_VERIFIED_UNREVIEWED"
            status = 0
    except Exception as exc:
        report["status"] = "FAIL"
        report["failures"].append(type(exc).__name__ + ": " + str(exc)[:800])
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n",
                               encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
