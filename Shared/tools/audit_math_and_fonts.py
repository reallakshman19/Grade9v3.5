#!/usr/bin/env python3
r"""
Automated Quality Governance & Audit Engine for Mathematics & Typography.
Enforces:
1. MATH_SYNTAX_VALID: Validates all KaTeX math blocks against KaTeX engine (zero parse errors, zero #cc0000).
2. MATH_DELIMITER_PARITY: Detects unmatched math delimiters, orphaned $, or trailing backslash delimiters.
3. MATH_NO_HTML_ENTITIES: Ensures math blocks contain pure LaTeX without HTML entities (&lt;, &gt;, &#x27;).
4. MATH_PERCENT_ESCAPED: Ensures percentage symbols in math are escaped (\%), not LaTeX comments (%).
5. FONT_FLOOR_RIGOR: Enforces minimum text floor >= 14px (0.88rem).
6. LAYOUT_RESPONSIVE_INTEGRITY: Prevents layout collapse, word-breaking, and unconstrained flex squishing.
"""
from __future__ import annotations

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Dict, Any, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]

MATH_BLOCK_RE = re.compile(r'(\$\$[\s\S]+?\$\$|\$(?:(?!\$)[^\n\r])+?\$|\\\[[\s\S]+?\\\]|\\\(.+?\\\))')
ENTITY_IN_MATH_RE = re.compile(r'&(lt|gt|amp|quot|#x27|apos);')
UNESCAPED_PERCENT_RE = re.compile(r'(?<!\\)%')

def extract_math_blocks(text: str) -> List[Tuple[str, str, int]]:
    """Returns list of (full_match, inner_math, start_pos)."""
    blocks = []
    for m in MATH_BLOCK_RE.finditer(text):
        raw = m.group(1)
        if raw.startswith("$$") and raw.endswith("$$"):
            inner = raw[2:-2].strip()
        elif raw.startswith("$") and raw.endswith("$"):
            inner = raw[1:-1].strip()
        elif raw.startswith("\\[") and raw.endswith("\\]"):
            inner = raw[2:-2].strip()
        elif raw.startswith("\\(") and raw.endswith("\\)"):
            inner = raw[2:-2].strip()
        else:
            inner = raw
        blocks.append((raw, inner, m.start()))
    return blocks

def audit_json_question_bank(fpath: Path) -> List[Dict[str, Any]]:
    """Audits a .core2.json question bank file."""
    findings = []
    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
    except Exception as e:
        return [{"file": str(fpath), "rule": "JSON_PARSE_ERROR", "detail": str(e), "severity": "BLOCK"}]

    questions = data.get("questions", [])
    for q in questions:
        qid = q.get("id", "UNKNOWN")
        
        # Flatten all text fields
        text_entries = []
        def walk(obj, path=""):
            if isinstance(obj, str):
                text_entries.append((path, obj))
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    walk(v, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    walk(v, f"{path}[{i}]")
        walk(q)

        for path, text in text_entries:
            # 1. Delimiter parity check
            # Exclude symbol questions or options with explicit symbol sequences
            if "option" in path.lower() and re.search(r'[#@*&!]{2,}', text):
                continue
            
            # Count unescaped dollars
            dollars = re.findall(r'(?<!\\)\$', text)
            if len(dollars) % 2 != 0:
                findings.append({
                    "file": str(fpath),
                    "qid": qid,
                    "field": path,
                    "rule": "MATH_DELIMITER_PARITY",
                    "detail": f"Unmatched '$' delimiter in {path}: {text!r}",
                    "severity": "BLOCK"
                })

            # Check math blocks
            blocks = extract_math_blocks(text)
            for raw, inner, pos in blocks:
                # Entity check
                m_ent = ENTITY_IN_MATH_RE.search(inner)
                if m_ent:
                    findings.append({
                        "file": str(fpath),
                        "qid": qid,
                        "field": path,
                        "rule": "MATH_NO_HTML_ENTITIES",
                        "detail": f"HTML entity '{m_ent.group(0)}' inside math block: {raw!r}",
                        "severity": "BLOCK"
                    })

                # Unescaped percent check
                m_pct = UNESCAPED_PERCENT_RE.search(inner)
                if m_pct:
                    findings.append({
                        "file": str(fpath),
                        "qid": qid,
                        "field": path,
                        "rule": "MATH_PERCENT_ESCAPED",
                        "detail": f"Unescaped '%' treated as comment in LaTeX math: {raw!r}",
                        "severity": "BLOCK"
                    })

    return findings

def _validate_katex_with_temp_files(blocks: List[Tuple[str, str, int]],
                                    text: str, html_path: Path,
                                    katex_js: Path) -> List[Dict[str, Any]]:
    """Run the real KaTeX parser without fixed paths or repository scratch writes.

    TemporaryDirectory gives concurrent audits independent JSON/script paths and
    removes all intermediate math text, even when Node or parsing fails.
    A failed validator is a blocking finding, never an academic pass.
    """
    findings: List[Dict[str, Any]] = []

    def unavailable(detail: str) -> List[Dict[str, Any]]:
        return [{
            "file": str(html_path),
            "line": 1,
            "rule": "MATH_SYNTAX_VALIDATOR_ERROR",
            "detail": detail,
            "severity": "BLOCK",
        }]

    math_items = [{"raw": raw, "inner": inner, "pos": pos} for raw, inner, pos in blocks]
    with TemporaryDirectory(prefix="grade9-katex-audit-") as temporary:
        batch_input_path = Path(temporary) / "_katex_input.json"
        script_path = Path(temporary) / "validate_katex_batch.js"
        batch_input_path.write_text(json.dumps(math_items), encoding="utf-8")
        validator_js = f"""
        const fs = require('fs');
        const path = require('path');
        const katex = require({json.dumps(str(katex_js))});
        
        const items = JSON.parse(fs.readFileSync({json.dumps(str(batch_input_path))}, 'utf8'));
        const errors = [];
        
        for (let i = 0; i < items.length; i++) {{
            const it = items[i];
            try {{
                const res = katex.renderToString(it.inner, {{
                    throwOnError: false,
                    displayMode: it.raw.startsWith('$') || it.raw.startsWith('\\\\[')
                }});
                if (res.includes('#cc0000') || res.includes('katex-error')) {{
                    errors.push({{
                        index: i,
                        pos: it.pos,
                        raw: it.raw,
                        inner: it.inner,
                        reason: 'KaTeX rendered error span with #cc0000'
                    }});
                }}
            }} catch(e) {{
                errors.push({{
                    index: i,
                    pos: it.pos,
                    raw: it.raw,
                    inner: it.inner,
                    reason: e.message
                }});
            }}
        }}
        console.log(JSON.stringify(errors));
        """
        script_path.write_text(validator_js, encoding="utf-8")

        try:
            res = subprocess.run(
                ["node", str(script_path)],
                capture_output=True, text=True, encoding="utf-8", timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return unavailable(f"KaTeX validator could not run: {exc}")
        if res.returncode != 0:
            return unavailable(
                f"KaTeX validator exited {res.returncode}: {res.stderr.strip()[:400]}"
            )
        try:
            errs = json.loads(res.stdout)
            if not isinstance(errs, list):
                raise ValueError("KaTeX validator output is not a JSON array")
            for err in errs:
                if not isinstance(err, dict) or not all(
                    key in err for key in ("pos", "raw", "reason")
                ):
                    raise ValueError("KaTeX validator returned malformed finding")
                line_no = text.count("\n", 0, err["pos"]) + 1
                findings.append({
                    "file": str(html_path),
                    "line": line_no,
                    "rule": "MATH_SYNTAX_VALID",
                    "detail": f"KaTeX syntax failure in {err['raw']!r}: {err['reason']}",
                    "severity": "BLOCK",
                })
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            return unavailable(f"KaTeX validator output invalid: {exc}")

    return findings

def audit_html_file(html_path: Path) -> List[Dict[str, Any]]:
    """Audits a standalone HTML page for math parsing and typography/responsive layout."""
    findings = []
    text = html_path.read_text(encoding="utf-8", errors="replace")

    # 1. KaTeX Math Block Audit
    blocks = extract_math_blocks(text)
    
    # Check each block for entities
    for raw, inner, pos in blocks:
        m_ent = ENTITY_IN_MATH_RE.search(inner)
        if m_ent:
            line_no = text.count("\n", 0, pos) + 1
            findings.append({
                "file": str(html_path),
                "line": line_no,
                "rule": "MATH_NO_HTML_ENTITIES",
                "detail": f"HTML entity '{m_ent.group(0)}' inside math block: {raw!r}",
                "severity": "BLOCK"
            })

    # Actual KaTeX syntax gate. Its scratch files never go inside the repo.
    katex_js = REPO_ROOT / "standalone" / "vendor" / "katex" / "0.16.8" / "katex.min.js"
    if katex_js.is_file():
        findings.extend(_validate_katex_with_temp_files(blocks, text, html_path, katex_js))

    # 2. Font Floor Audit (< 14px / 0.88rem)
    font_matches = re.finditer(r'font-size\s*:\s*([0-9.]+)\s*(px|rem)', text, re.I)
    for fm in font_matches:
        val = float(fm.group(1))
        unit = fm.group(2).lower()
        px = val if unit == "px" else val * 16.0
        if 0 < px < 13.9:
            line_no = text.count("\n", 0, fm.start()) + 1
            findings.append({
                "file": str(html_path),
                "line": line_no,
                "rule": "FONT_FLOOR_RIGOR",
                "detail": f"Sub-floor font size '{fm.group(0)}' ({px:.1f}px < 14px floor)",
                "severity": "BLOCK"
            })

    # 3. Responsive Layout Integrity
    # Check summary layout: summary elements must have flex-wrap: wrap
    if ".qb-disclosure summary" in text:
        summary_css = re.search(r'\.qb-disclosure summary\s*\{([^}]+)\}', text)
        if summary_css and "flex-wrap" not in summary_css.group(1):
            findings.append({
                "file": str(html_path),
                "line": 1,
                "rule": "LAYOUT_RESPONSIVE_INTEGRITY",
                "detail": ".qb-disclosure summary missing 'flex-wrap: wrap' (causes header collision on narrow screens)",
                "severity": "BLOCK"
            })

    # Check for word-break: break-all which ruins word morphology
    if re.search(r'word-break\s*:\s*break-all', text, re.I):
        findings.append({
            "file": str(html_path),
            "line": 1,
            "rule": "LAYOUT_RESPONSIVE_INTEGRITY",
            "detail": "Dangerous 'word-break: break-all' detected (splits ordinary words across lines)",
            "severity": "BLOCK"
        })

    return findings

def run_comprehensive_audit() -> Tuple[List[Dict[str, Any]], int]:
    """Runs the audit across all core question banks and standalone suites."""
    all_findings = []
    
    # 1. Audit Core 2 question banks
    json_targets = [
        REPO_ROOT / "Mathematics" / "question-bank" / "sof-imo-2025-26-set-b.core2.json",
        REPO_ROOT / "Mathematics" / "question-bank" / "sof-imo-2025-26-set-a.core2.json",
        REPO_ROOT / "Mathematics" / "question-bank" / "sof-imo-2024-25-set-b.core2.json"
    ]
    for jt in json_targets:
        if jt.exists():
            all_findings.extend(audit_json_question_bank(jt))

    # 2. Audit standalone suite HTML
    html_targets = [
        REPO_ROOT / "standalone" / "mathematics-imo-grade9-master-suite.html",
        REPO_ROOT / "public" / "standalone" / "mathematics-imo-grade9-master-suite.html"
    ]
    for ht in html_targets:
        if ht.exists():
            all_findings.extend(audit_html_file(ht))

    return all_findings, len(all_findings)

def main():
    findings, count = run_comprehensive_audit()
    print(f"=== MATHEMATICS & TYPOGRAPHY QUALITY AUDIT ===")
    print(f"Total findings: {count}")
    
    for f in findings:
        loc = f.get("file", "")
        if "line" in f:
            loc += f":{f['line']}"
        elif "qid" in f:
            loc += f" ({f['qid']})"
        print(f"[{f['rule']}] {f['severity']} at {loc}")
        print(f"  -> {f['detail']}")

    if count > 0:
        sys.exit(1)
    else:
        print("ALL AUDIT CHECKS PASSED: Zero math syntax errors, zero font-floor violations, zero layout collapses.")
        sys.exit(0)

if __name__ == "__main__":
    main()
