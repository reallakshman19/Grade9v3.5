"""
Quality Governance Test: Mathematics, KaTeX Syntax, Typography Floor, and Responsive Layout Integrity.
Enforces:
1. Zero KaTeX parse errors (no #cc0000 error spans)
2. Zero unmatched $ delimiters or broken delimiter escapes
3. Zero HTML entity leaks inside LaTeX math ($x &lt; 0$)
4. Zero unescaped % comments in LaTeX formulas
5. Strict font floor compliance (>= 14px / 0.88rem)
6. Zero responsive layout collisions (flex-wrap on disclosure summaries, word-break safety)
"""
from __future__ import annotations

import unittest
from Shared.tools.audit_math_and_fonts import run_comprehensive_audit

class MathAndFontQualityTests(unittest.TestCase):
    def test_zero_math_syntax_and_font_findings(self):
        findings, count = run_comprehensive_audit()
        if count > 0:
            error_msgs = []
            for f in findings:
                loc = f.get("file", "")
                if "line" in f: loc += f":{f['line']}"
                elif "qid" in f: loc += f" ({f['qid']})"
                error_msgs.append(f"[{f['rule']}] {loc} -> {f['detail']}")
            self.fail(f"Found {count} mathematics/font quality lapses:\n" + "\n".join(error_msgs))
        self.assertEqual(count, 0)

if __name__ == "__main__":
    unittest.main()
