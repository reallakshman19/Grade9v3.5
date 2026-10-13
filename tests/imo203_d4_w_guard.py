"""Small, explicit RETRIEVE-D4 semantic cue guard (not an academic classifier).

Protect the higher-power *sufficiency/iff* and exponent-specific branch.
The modulo-8 necessary-condition anchor and small a=5 counterexample stay allowed.
"""
import re
import unicodedata
from html import unescape


PATTERNS = {
    "iff_mod8": r"(?:if and only if|\biff\b).{0,85}(?:mod|modulo)\s*8|(?:mod|modulo)\s*8.{0,85}(?:if and only if|\biff\b)",
    "sufficiency_mod8": r"(?:sufficient|guarantees|ensures).{0,80}(?:mod|modulo)\s*8|(?:mod|modulo)\s*8.{0,80}(?:sufficient|guarantees|ensures)",
    "all_classes_lift": r"(?:every|all)\s+(?:odd\s+)?(?:residue|class|number)s?.{0,90}(?:mod|modulo)\s*8.{0,75}(?:square|root|lift)",
    "exact_exponent_rule": r"(?:k\s*>=\s*3|exponent\s*3\s+or\s+(?:higher|more)).{0,65}(?:criterion|condition|rule|use).{0,60}(?:mod|modulo)\s*8",
    "high_power_root": r"(?:1\s*(?:mod|modulo)\s*8|1\s+congruent).{0,80}(?:lifts?\s+to|has\s+a\s+(?:square\s+)?root\s+modulo)",
}


def cue_matches(text):
    value = unicodedata.normalize("NFKC", unescape(text)).casefold()
    value = value.replace("≡", " congruent ").replace("≥", ">=")
    value = re.sub(r"\s+", " ", value)
    return [name for name, rule in PATTERNS.items() if re.search(rule, value)]


def assert_no_protected_iff(text, role):
    cues = cue_matches(text)
    if cues:
        raise AssertionError(f"{role}: protected RETRIEVE-D4 iff cue(s) {cues}")
