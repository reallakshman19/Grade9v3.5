// QRT-B3-SEMANTIC-TRIAGE-1: synthetic routing tests, NOT academic oracle data.
// Run: node --test TEST/imo-qrt-tile/qrt-semantic-triage.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { triagePrecommitHint, TRIAGE_DECISION, TRIAGE_SCOPE } from './qrt-semantic-triage.mjs';

const SOURCE = '6ad5c73cfee80b75efffd219eb1b14886ca18c10';
const CONTEXT = 'a'.repeat(64); // Synthetic full-context digest, NOT actual fixture provenance.
const QID = 'SOF-IMO-G09-L1-2024-25-B-Q022';
const hint = 'Carry out the difference of squares yourself, then decide if the result is rational.';
const base = Object.freeze({
  questionId: QID, sourceSha: SOURCE, contextSchema: 'QRT-PRECOMMIT-SURFACE-V1',
  contextDigest: CONTEXT, stage: 'PRECOMMIT', precommitText: hint,
});
const leak = Object.freeze({
  decision: 'LEAK', stage: 'PRECOMMIT', questionId: QID, sourceSha: SOURCE,
  contextSchema: base.contextSchema, contextDigest: CONTEXT,
  reviewId: 'review-001', reviewerId: 'reviewer-opaque-001', reviewerScope: 'Q022-W',
  reviewedAt: '2026-10-15T15:00:00Z', proofRef: 'private-proof-001', proofType: 'EXPLICIT',
  wComponents: ['W_N', 'W_C'],
});
// A synthetic *test double* for a trusted external verifier; no real reviewer
// attested any case. Never deploy a flag-only stub as an evidence verifier.
const attest = ev => ({
  status: 'VERIFIED_PRECOMMIT_LEAK', reviewId: ev.reviewId, questionId: ev.questionId,
  sourceSha: ev.sourceSha, contextDigest: ev.contextDigest,
  reviewerAuthorityVerified: true, precommitExposureVerified: true,
  completeContextVerified: true, proofVerified: true, conflictsResolved: true,
});
const trustedForTest = { verifyLeakEvidence: attest };
const checkReview = (candidate, reason) => {
  const result = triagePrecommitHint(candidate, trustedForTest);
  assert.equal(result.decision, TRIAGE_DECISION.REVIEW_REQUIRED);
  assert.equal(result.needsHumanReview, true);
  assert.notEqual(result.decision, 'PASS');
  if (reason) assert.equal(result.reasonCode, reason);
  return result;
};

test('exports contain no automatic semantic PASS decision', () => {
  assert.deepEqual(Object.values(TRIAGE_DECISION).sort(), ['REJECT', 'REVIEW_REQUIRED']);
});
test('unreviewed method-only cue P01 abstains; not auto-rejected', () => {
  checkReview(base, 'UNREVIEWED_PRECOMMIT_SEMANTICS');
});
test('benign P02 rationality question abstains; no vocabulary ban', () => {
  checkReview({...base, precommitText: 'Ask yourself: is the number rational or irrational?'});
});
test('A01 hedged answer is review, not automatic reject', () => {
  checkReview({...base, precommitText: 'The answer might be seven.', concern: 'HEDGED_ANSWER_SUSPICION'}, 'HEDGED_ANSWER_SUSPICION');
});
test('C01 negated rationality requires human premise/polarity verification', () => {
  checkReview({...base, precommitText: 'It is not an irrational number.', concern: 'POLARITY_DOMAIN_UNVERIFIED'}, 'POLARITY_DOMAIN_UNVERIFIED');
});
test('wrong content X01/X02 cannot become semantic safe', () => {
  for(const text of ['The result is irrational because √2 appears.', 'It is not seven.']) {
    checkReview({...base, precommitText:text, concern:'MATH_CONTRADICTION'}, 'MATH_CONTRADICTION');
  }
});
test('option-dependent O01/O02 require whole-context human entailment', () => {
  for(const text of ['Only A or B could be correct.', 'Eliminate choices B and D.']) {
    checkReview({...base, precommitText:text,concern:'OPTION_DEPENDENT_ENTAILMENT'}, 'OPTION_DEPENDENT_ENTAILMENT');
  }
});
test('four independent unhandled semantic paraphrases remain review, not PASS', () => {
  for(const text of [
    'The computed output belongs to the rationals.',
    'The numerical value equals 14 divided by 2.',
    'The answer is a fraction of two integers.',
    'The computed output is the quotient of two whole numbers.',
  ]) {
    checkReview({...base, precommitText:text,concern:'SUSPECTED_DISCLOSURE'}, 'SUSPECTED_DISCLOSURE');
  }
});
test('A11 postcommit claims are OUT_OF_SCOPE even with forged proof', () => {
  const out = checkReview({...base, stage:'POSTCOMMIT', precommitText:'The result is 7, rational.',reviewEvidence:leak}, 'POSTCOMMIT_NOT_AUTHORIZED');
  assert.equal(out.scopeStatus, TRIAGE_SCOPE.OUT_OF_SCOPE);
});
test('A11 untrusted/unknown stage cannot acquire precommit authority', () => {
  for(const stage of [undefined,'UNKNOWN','committed','POST_COMMIT']) {
    const out=checkReview({...base,stage,reviewEvidence:leak},'STAGE_NOT_ATTESTED');
    assert.equal(out.scopeStatus, TRIAGE_SCOPE.UNVERIFIED);
  }
});
test('null/nonobject candidate abstains', () => {
  for(const x of [null, [], false, 'precommit', 3]) checkReview(x,'INVALID_INPUT');
});
test('missing case identity, source or complete context is never verified', () => {
  for (const patch of [
    {questionId:''},{sourceSha:'a'.repeat(40) + 'x'},{sourceSha:undefined},
    {contextDigest:'bad'},{contextDigest:undefined},{contextSchema:'HINT2-ONLY'},
    {precommitText:' '},
  ]) {
    const out=checkReview({...base,...patch,reviewEvidence:leak},'MISSING_OR_INVALID_FULL_CONTEXT');
    assert.equal(out.scopeStatus,TRIAGE_SCOPE.UNVERIFIED);
  }
});
test('a caller-supplied verified flag, leak text and apparent reviewer never suffice', () => {
  const out = triagePrecommitHint({...base,verified:true,reviewEvidence:{...leak,verified:true}});
  assert.equal(out.decision,'REVIEW_REQUIRED');
  assert.equal(out.reasonCode,'INDEPENDENT_VERIFIER_UNAVAILABLE');
});
test('review evidence missing or incomplete cannot be promoted even by test verifier', () => {
  for(const patch of [
    {questionId:'WRONG'},{sourceSha:'f'.repeat(40)},{contextDigest:'b'.repeat(64)},
    {contextSchema:'H2-ONLY'},{stage:'POSTCOMMIT'},{reviewId:''},
    {reviewerId:undefined},{reviewerScope:undefined},{reviewedAt:'yesterday'},
    {proofRef:undefined},{proofType:'MODEL_ASSERTION'},{wComponents:[]},
    {wComponents:['W_OTHER']},{decision:'PASS'},
  ]) checkReview({...base,reviewEvidence:{...leak,...patch}},'STALE_UNVERIFIED_OR_INCOMPLETE_REVIEW');
});
test('unverified conflicting historic PASS remains review, preserving the dispute', () => {
  const out=triagePrecommitHint({...base,reviewEvidence:leak,conflictHistory:[{reviewId:'old-PASS',decision:'PASS'}]});
  assert.equal(out.decision, 'REVIEW_REQUIRED');
  assert.equal(out.reasonCode, 'INDEPENDENT_VERIFIER_UNAVAILABLE');
  assert.deepEqual(out.supersessionRequired,[]);
});
test('invalid/conflicting review history cannot bypass checks', () => {
  for (const history of ['PASS', [{reviewId:'',decision:'PASS'}], [{reviewId:'r',decision:'SAFE'}]]) {
    checkReview({...base,reviewEvidence:leak,conflictHistory:history},'INVALID_CONFLICT_HISTORY');
  }
});
test('untrusted or missing attestation fails closed', () => {
  for (const verifyLeakEvidence of [undefined,()=>false,()=>({status:'VERIFIED_PRECOMMIT_LEAK'}),
    ()=>({...attest(leak),reviewerAuthorityVerified:false}),
    ()=>({...attest(leak),completeContextVerified:false}),
    ()=>({...attest(leak),conflictsResolved:false}),
    ()=>({...attest(leak),contextDigest:'b'.repeat(64)}),
    ()=>{throw Error('downstream unavailable')},
  ]) {
    const out=triagePrecommitHint({...base,reviewEvidence:leak},{verifyLeakEvidence});
    assert.equal(out.decision,'REVIEW_REQUIRED');
    assert.notEqual(out.reasonCode,'INDEPENDENTLY_VERIFIED_PRECOMMIT_W_LEAK');
  }
});
test('simulated externally attested exact-context precommit disclosure routes REJECT only', () => {
  const out=triagePrecommitHint({...base,precommitText:'The result is 7, rational.',reviewEvidence:leak},trustedForTest);
  assert.equal(out.decision,'REJECT');
  assert.equal(out.scopeStatus,'PRECOMMIT_ONLY');
  assert.equal(out.evidenceKind,'EXTERNALLY_ATTESTED_REVIEW');
  assert.deepEqual(out.wComponents,['W_N','W_C']);
  assert.notEqual(out.decision,'PASS');
});
test('reviewed explicit C01 requires externally attested proof; no negation detector', () => {
  const wC={...leak,proofType:'ENTAILED',wComponents:['W_C'],proofRef:'private-real-domain-and-polarity-proof'};
  const out=triagePrecommitHint({...base,precommitText:'It is not an irrational number.',reviewEvidence:wC},trustedForTest);
  assert.equal(out.decision,'REJECT'); // Test-double attestation, NOT actual expert review.
  assert.deepEqual(out.wComponents,['W_C']);
});
test('D1: independently attested leak wins over previous PASS; supersession is advisory', () => {
  const input={...base,reviewEvidence:leak,conflictHistory:[
    {reviewId:'legacy-PASS-01',decision:'PASS'},
    {reviewId:'legacy-hold',decision:'REVIEW_REQUIRED'},
    {reviewId:'legacy-PASS-01',decision:'PASS'},
  ]};
  const out=triagePrecommitHint(input,trustedForTest);
  assert.equal(out.decision,'REJECT');
  assert.deepEqual(out.supersessionRequired,['legacy-PASS-01']);
  assert.equal(input.conflictHistory[0].decision,'PASS'); // No real record mutated.
});
test('D1: disagreement without conflict-resolution attestation cannot REJECT', () => {
  const out=triagePrecommitHint({...base,reviewEvidence:leak,conflictHistory:[{reviewId:'old-PASS',decision:'PASS'}]},
    {verifyLeakEvidence: ev=>({...attest(ev),conflictsResolved:false})});
  assert.equal(out.decision,'REVIEW_REQUIRED');
  assert.deepEqual(out.supersessionRequired,[]);
});
test('a callback attestation cannot bypass mismatched evidence, source or stage', () => {
  const out=triagePrecommitHint({...base,reviewEvidence:{...leak,sourceSha:'f'.repeat(40)}},trustedForTest);
  assert.equal(out.decision,'REVIEW_REQUIRED');
});
test('result is frozen and excludes private proof, hint and reviewer identity', () => {
  const out=triagePrecommitHint({...base,reviewEvidence:leak},trustedForTest);
  assert.equal(Object.isFrozen(out),true);
  assert.equal(Object.isFrozen(out.wComponents),true);
  const payload=JSON.stringify(out);
  assert.doesNotMatch(payload,/private-proof|reviewer-opaque|Carry out the difference/);
});
