// Browser witness contract, deliberately pure for negative mutation tests.
// This is a bounded lexical tripwire, NOT a semantic proof of protected W.
// A lexical PASS leaves general protected-work equivalence REVIEW_REQUIRED.
export function q022HintPreservesProtectedWork(text) {
  if (typeof text !== "string") return false;
  const hint = text.normalize("NFKC").replace(/[\u200B-\u200D\uFEFF]/g, "");
  if (!hint.includes("Carry out the difference of squares yourself")) return false;
  // Q022's keyed numerical answer must be learner-computed, independently of
  // whether the original 9-2=7 expansion string appears verbatim.
  if (/\b(?:7|seven)\b/i.test(hint)) return false;
  // NFKC maps mathematical double-struck ℚ to Q. Reject unambiguous
  // category labels, while preserving a reviewer requirement for paraphrases.
  if (/[ℚℝ]/u.test(text) || /\\mathbb\s*\{\s*[QR]\s*\}/i.test(text)) return false;
  if (/\bclassification\b\s*(?:is|equals|=|:)\s*(?:a\s+)?rational\b/i.test(hint)) return false;
  // A classifier sentence giving the keyed category is also protected W.
  if (/\b(?:the\s+)?(?:answer|result|value|product|number|it|this|which)\s+(?:is|equals|=|:)\s+(?:a\s+)?rational(?:\s+number)?\b/i.test(hint)) return false;
  if (/\brational(?:\s+number)?\s+(?:is\s+)?(?:the\s+)?(?:answer|choice)\b/i.test(hint)) return false;
  // A stated arithmetic value in number words is still a disclosure even
  // without the digit 7. This is intentionally limited to a completed
  // declarative calculation, not a ban on mathematical vocabulary.
  if (/\b(?:the|your|this)\s+(?:numerical|computed|calculated)?\s*(?:answer|result|value|number)\s+(?:is|equals|=|:)\s+(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s+(?:minus|plus|times|multiplied\s+by|divided\s+by)\s+(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\b/i.test(hint)) return false;
  // Stating that a computed number IS expressible as a quotient discloses
  // the rationality classification. Asking WHETHER it is expressible leaves
  // that decision to the learner, including genuine interrogatives.
  const categoricalQuotient = /\b(?:your|the|this|that|our|its)\s+(?:calculated|computed|resulting)?\s*(?:value|result|answer|number)\s+(?:can|may|must)\s+(?:indeed\s+)?be\s+(?:written|expressed|represented)\s+as\s+(?:a\s+)?(?:ratio|quotient|fraction)\s+of\s+two\s+integers\b/gi;
  for (const match of hint.matchAll(categoricalQuotient)) {
    const prefix = hint.slice(0, match.index);
    const clauseStart = Math.max(prefix.lastIndexOf("."), prefix.lastIndexOf("!"),
      prefix.lastIndexOf("?"), prefix.lastIndexOf(";"));
    if (!/\b(?:whether|if)\s*$/i.test(prefix.slice(clauseStart + 1))) return false;
  }
  return true;
}

export function katexWitnessPasses(facts) {
  return facts?.katexApi === "function" &&
    Number.isInteger(facts.katexNodes) && facts.katexNodes > 0 &&
    Number.isInteger(facts.katexQuestionNodes) && facts.katexQuestionNodes > 0 &&
    Number.isInteger(facts.katexQuestionErrors) && facts.katexQuestionErrors === 0;
}

export function coreRouteVisible(facts) {
  if (!facts?.tabActive || !facts?.highlighted) return false;
  if (!Array.isArray(facts.ancestorStyles) || !facts.ancestorStyles.length) return false;
  if (facts.ancestorStyles.some(s => !s ||
      s.display === "none" ||
      s.visibility === "hidden" ||
      s.visibility === "collapse" ||
      Number(s.opacity) === 0)) return false;
  const r=facts.rect, v=facts.viewport;
  if (!r || !v || ![r.top,r.right,r.bottom,r.left,r.width,r.height,v.width,v.height]
      .every(n=>typeof n==="number" && Number.isFinite(n))) return false;
  if (r.width <= 0 || r.height <= 0 || v.width <= 0 || v.height <= 0) return false;
  const area = Math.max(0, Math.min(r.right,v.width)-Math.max(r.left,0)) *
               Math.max(0, Math.min(r.bottom,v.height)-Math.max(r.top,0));
  return area > 0;
}
