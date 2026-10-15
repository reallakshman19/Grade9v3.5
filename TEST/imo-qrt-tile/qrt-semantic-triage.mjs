/**
 * QRT-B3-SEMANTIC-TRIAGE-1: precommit REVIEW ROUTING, not a semantic detector.
 * No academic PASS is emitted. No source/DOM/attempt-stage authentication occurs here.
 *
 * Only a separately trusted verifier can attest reviewed precommit disclosure.
 * Passing a caller-authored 'verified: true' flag (or an unchecked callback) is NOT
 * verification. The integration providing 'verifyLeakEvidence' must independently
 * authenticate the reviewer, full rendered precommit surface, source revision,
 * protected W, derivation and conflict resolution. None is available by default.
 *
 * Privacy: only references/digests/reason codes are returned, never raw hint,
 * learner data, answer key, reviewed mathematical derivation or secret metadata.
 */

export const TRIAGE_DECISION = Object.freeze({
  REVIEW_REQUIRED: 'REVIEW_REQUIRED',
  REJECT: 'REJECT',
});
export const TRIAGE_SCOPE = Object.freeze({
  PRECOMMIT_ONLY: 'PRECOMMIT_ONLY',
  UNVERIFIED: 'UNVERIFIED',
  OUT_OF_SCOPE: 'OUT_OF_SCOPE',
});

const SURFACE_SCHEMA = 'QRT-PRECOMMIT-SURFACE-V1';
const HEX40 = /^[0-9a-f]{40}$/i;
const HEX64 = /^[0-9a-f]{64}$/i;
const W_COMPONENTS = new Set(['W_N', 'W_C']);
const PROOF_TYPES = new Set(['EXPLICIT', 'EQUIVALENCE', 'ENTAILED']);
const CONCERNS = new Set([
  'POLARITY_DOMAIN_UNVERIFIED',
  'HEDGED_ANSWER_SUSPICION',
  'MATH_CONTRADICTION',
  'WRONG_CONTENT',
  'OPTION_DEPENDENT_ENTAILMENT',
  'SUSPECTED_DISCLOSURE',
]);
const isRecord = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const present = x => typeof x === 'string' && x.trim().length > 0;
const id = x => present(x) && x.length <= 160 && /^[a-zA-Z0-9._:-]+$/.test(x);
const isoDate = x => present(x) && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(x) && Number.isFinite(Date.parse(x));

function response(reasonCode, scopeStatus = TRIAGE_SCOPE.PRECOMMIT_ONLY, details = {}) {
  return Object.freeze({
    decision: TRIAGE_DECISION.REVIEW_REQUIRED,
    scopeStatus,
    reasonCode,
    evidenceKind: 'UNVERIFIED',
    signal: 'NONE',
    needsHumanReview: true,
    supersessionRequired: Object.freeze([]),
    ...details,
  });
}

/**
 * Input describes a CANDIDATE, not independently authenticated runtime state:
 * {questionId, sourceSha, contextDigest, contextSchema, stage, precommitText,
 *  concern?, reviewEvidence?, conflictHistory?}.
 * 'contextDigest' is supposed to identify the COMPLETE versioned precommit
 * surface (stem, options, all accessible hints/Core/alt/MathML, timing), not H2.
 * This helper cannot compute or authenticate that digest from a hint string.
 *
 * 'options.verifyLeakEvidence' is an OPTIONAL externally trusted review adapter.
 * If present, it must independently return a matching, fully attested result:
 * {status:'VERIFIED_PRECOMMIT_LEAK', reviewId, questionId, sourceSha,
 *  contextDigest, reviewerAuthorityVerified:true, precommitExposureVerified:true,
 *  completeContextVerified:true, proofVerified:true, conflictsResolved:true}.
 * Without this trusted boundary, REJECT is unavailable. No PASS path exists.
 * A REJECT does not edit/revoke prior records: it routes identified prior PASS
 * claims for supersession in a separately governed reviewer record system.
 */
export function triagePrecommitHint(candidate, options = {}) {
  if (!isRecord(candidate)) return response('INVALID_INPUT', TRIAGE_SCOPE.UNVERIFIED);
  if (candidate.stage === 'POSTCOMMIT') return response('POSTCOMMIT_NOT_AUTHORIZED', TRIAGE_SCOPE.OUT_OF_SCOPE);
  if (candidate.stage !== 'PRECOMMIT') return response('STAGE_NOT_ATTESTED', TRIAGE_SCOPE.UNVERIFIED);

  if (!id(candidate.questionId) || !HEX40.test(candidate.sourceSha ?? '') ||
      !HEX64.test(candidate.contextDigest ?? '') || candidate.contextSchema !== SURFACE_SCHEMA ||
      !present(candidate.precommitText)) {
    return response('MISSING_OR_INVALID_FULL_CONTEXT', TRIAGE_SCOPE.UNVERIFIED);
  }
  const concern = CONCERNS.has(candidate.concern) ? candidate.concern : null;
  const pending = concern || 'UNREVIEWED_PRECOMMIT_SEMANTICS';
  const history = candidate.conflictHistory;
  if (history !== undefined && (!Array.isArray(history) || history.some(h =>
      !isRecord(h) || !id(h.reviewId) || !['PASS', 'REJECT', 'REVIEW_REQUIRED'].includes(h.decision)))) {
    return response('INVALID_CONFLICT_HISTORY', TRIAGE_SCOPE.UNVERIFIED);
  }
  const priorPassIds = (history ?? []).filter(h => h.decision === 'PASS').map(h => h.reviewId);
  const evidence = candidate.reviewEvidence;
  if (!isRecord(evidence)) return response(pending, TRIAGE_SCOPE.PRECOMMIT_ONLY,
    { signal: concern ? 'REVIEW_CANDIDATE' : 'NONE' });

  // Refuse stale/mismatched or unauditable claims, even if an injected callback
  // would otherwise answer true. Fields are requirements, NOT proof by presence.
  if (evidence.decision !== 'LEAK' || evidence.stage !== 'PRECOMMIT' ||
      evidence.questionId !== candidate.questionId ||
      evidence.sourceSha !== candidate.sourceSha ||
      evidence.contextDigest !== candidate.contextDigest ||
      evidence.contextSchema !== candidate.contextSchema ||
      !id(evidence.reviewId) || !id(evidence.reviewerId) ||
      !id(evidence.reviewerScope) || !isoDate(evidence.reviewedAt) ||
      !id(evidence.proofRef) || !PROOF_TYPES.has(evidence.proofType) ||
      !Array.isArray(evidence.wComponents) || evidence.wComponents.length === 0 ||
      evidence.wComponents.some(w => !W_COMPONENTS.has(w))) {
    return response('STALE_UNVERIFIED_OR_INCOMPLETE_REVIEW', TRIAGE_SCOPE.UNVERIFIED,
      { signal: 'REVIEW_CANDIDATE' });
  }

  if (!isRecord(options) || typeof options.verifyLeakEvidence !== 'function') {
    return response('INDEPENDENT_VERIFIER_UNAVAILABLE', TRIAGE_SCOPE.PRECOMMIT_ONLY,
      { signal: 'REVIEW_CANDIDATE' });
  }
  let attestation;
  try {
    // This callback is an INTEGRATION TRUST BOUNDARY, not a built-in proof.
    // It must validate source, reviewer scope/identity, W and current context.
    attestation = options.verifyLeakEvidence(evidence, candidate);
  } catch {
    return response('INDEPENDENT_VERIFICATION_FAILED', TRIAGE_SCOPE.UNVERIFIED,
      { signal: 'REVIEW_CANDIDATE' });
  }
  if (!isRecord(attestation) ||
      attestation.status !== 'VERIFIED_PRECOMMIT_LEAK' ||
      attestation.reviewId !== evidence.reviewId ||
      attestation.questionId !== candidate.questionId ||
      attestation.sourceSha !== candidate.sourceSha ||
      attestation.contextDigest !== candidate.contextDigest ||
      attestation.reviewerAuthorityVerified !== true ||
      attestation.precommitExposureVerified !== true ||
      attestation.completeContextVerified !== true ||
      attestation.proofVerified !== true ||
      attestation.conflictsResolved !== true) {
    return response('INDEPENDENT_VERIFICATION_NOT_ESTABLISHED', TRIAGE_SCOPE.UNVERIFIED,
      { signal: 'REVIEW_CANDIDATE' });
  }

  // This is a ROUTE based on EXTERNALLY attested evidence, never a detection
  // of disclosure by these regex-free functions. No persisted PASS is changed.
  return Object.freeze({
    decision: TRIAGE_DECISION.REJECT,
    scopeStatus: TRIAGE_SCOPE.PRECOMMIT_ONLY,
    reasonCode: 'INDEPENDENTLY_VERIFIED_PRECOMMIT_W_LEAK',
    evidenceKind: 'EXTERNALLY_ATTESTED_REVIEW',
    signal: 'REVIEWED_W_DISCLOSURE',
    needsHumanReview: false, // the stated leak was externally reviewed; product acceptance remains separate
    wComponents: Object.freeze([...new Set(evidence.wComponents)]),
    reviewId: evidence.reviewId,
    supersessionRequired: Object.freeze([...new Set(priorPassIds)]),
  });
}
