// Browser witness contract, deliberately pure for negative mutation tests.
// Static token checks do not replace a human protected-W semantic review.
export function q022HintPreservesProtectedWork(text) {
  if (typeof text !== "string") return false;
  const hint = text.normalize("NFKC").replace(/[\u200B-\u200D\uFEFF]/g, "");
  if (!hint.includes("Carry out the difference of squares yourself")) return false;
  // Q022's keyed numerical answer must be learner-computed, independently of
  // whether the original 9-2=7 expansion string appears verbatim.
  if (/\b7\b/.test(hint)) return false;
  // A classifier sentence giving the keyed category is also protected W.
  if (/\b(?:the\s+)?(?:answer|result|value|product|number|it|this|which)\s+(?:is|equals|=|:)\s+(?:a\s+)?rational(?:\s+number)?\b/i.test(hint)) return false;
  if (/\brational(?:\s+number)?\s+(?:is\s+)?(?:the\s+)?(?:answer|choice)\b/i.test(hint)) return false;
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
