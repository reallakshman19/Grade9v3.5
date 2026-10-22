#!/usr/bin/env node
// B1 self-check; run from any working directory: node Physics/content/nlm-personal-use/benchmark.mjs
// Stronger browser interaction checks are in benchmark-browser.py (if Playwright installed).
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {Script} from 'node:vm';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';

const dir=dirname(fileURLToPath(import.meta.url));
const source=JSON.parse(readFileSync(resolve(dir,'source-rows.v1.json'),'utf8'));
const display=JSON.parse(readFileSync(resolve(dir,'display-variants.v1.json'),'utf8'));
const html=readFileSync(resolve(dir,'../../../standalone/practice/nlm-core2-first-slice.html'),'utf8');
const sourceIDs=['PHYS-NLM-001','PHYS-NLM-002'];
const rowDigests=['d00fe1196ad1f344da0b9560c2068ebcc80db08bddc180fabe7eb492c96a5a52','27e3ce8879503452fcca0521f9dc865234e900486340a8401b7a49c1919f5148'];
const sha=b=>createHash('sha256').update(b).digest('hex');
let passed=0;
function test(name,fn){try{fn();passed++;console.log('PASS',name)}catch(e){console.error('FAIL',name,e.stack||e);process.exitCode=1}}
function verifySource(rows){
 assert.equal(rows.length,2);
 rows.forEach((row,i)=>{assert.equal(row.question_id,sourceIDs[i]);assert.equal(sha(Buffer.from(JSON.stringify(row))),rowDigests[i]);assert.ok(row.provenance&&row.options&&row.figure&&row.progressive_hints&&row.model_proof)});
}
function verifyDisplay(v){
 assert.deepEqual(v.items.map(x=>x.source_id),sourceIDs);
 assert.deepEqual(v.items.map(x=>x.variant_id),['PHYS-NLM-001-PU1','PHYS-NLM-002-PU1']);
 assert.deepEqual(v.items.map(x=>x.key),['A','C']);
 v.items.forEach((x,i)=>{assert.equal(x.stem,source.source_questions[i].stem);assert.deepEqual(x.figure,source.source_questions[i].figure);assert.deepEqual(x.system_parameters,source.source_questions[i].system_parameters);assert.equal(x.origin,'ADAPTED_AUTHORED_PRACTICE');assert.ok(x.changes.length);assert.deepEqual(Object.keys(x.options),['A','B','C','D'])});
 assert.equal(v.exposure.length,3);assert.ok(v.exposure[2].includes('already exposed'));
}
function verifyPreAttempt(txt){
 const shell=txt.split('<script type="application/json" id="nlm-payload">')[0];
 assert.ok(!/Correct adapted option:|answer is [A-D]|Upward net force\./i.test(shell),'initial visible shell leaked answer');
 const start=txt.indexOf('function baselineStage()'),end=txt.indexOf('function showHint()',start);
 assert.ok(start!==-1&&end>start,'baseline stage missing');
 const baseline=txt.slice(start,end);
 assert.ok(!/\.key\b|\.teacher\b|\.feedback\b|source_hints_001|correct adapted option/i.test(baseline),'pre-attempt flow references answer data');
 assert.ok(baseline.includes('state.baseline.push')&&baseline.includes('assisted:false'));
 assert.ok(txt.includes('state.stage<2')&&txt.includes('state.stage++'));
}
test('two authored source IDs + fixed per-row SHA-256, complete custody fields',()=>{assert.equal(source.bank_denominator,39);verifySource(source.source_questions)});
test('variants are exactly two labeled source-backed adaptations; source conditions and figures preserved',()=>verifyDisplay(display));
test('displayed stems and hint provenance bound to source',()=>{assert.equal(display.items[0].scaffolds.length,3);assert.deepEqual(display.items[0].scaffolds.map(s=>s.role),['CLARIFY','CORRELATE','OPEN_THE_WAY']);assert.equal(source.source_questions[0].progressive_hints.length,3)});
test('the standalone payload matches custody and display',()=>{
 const match=html.match(/<script type="application\/json" id="nlm-payload">([\s\S]*?)<\/script>/);
 assert.ok(match,'inline payload not found');const data=JSON.parse(match[1]);
 assert.deepEqual(data.items,display.items);
 assert.deepEqual(data.source_hints_001,source.source_questions[0].progressive_hints);
 assert.equal(data.source_count,39);
});
test('HTML scripts are syntactically valid JavaScript',()=>{
 const scripts=[...html.matchAll(/<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g)];assert.equal(scripts.length,1);new Script(scripts[0][1]);
});
test('no pre-baseline answer/feedback reference; baseline reason+uncertainty capture',()=>{
 verifyPreAttempt(html);
 assert.ok(html.includes('choice,explanation:reason,confidence:certainty'));
 assert.ok(html.includes('correctness_hidden_until_baselines_complete:true'));
});
test('supported hint progression, assistance state, deliberate reveal and reset',()=>{
 ['state.hintLevel++','state.hintLevel>=3','prior_feedback_seen:state.feedbackSeen','answer_seen_at_attempt:state.answerRevealed','kind:"deliberate_full_teacher_reveal"','state=fresh();render()','window.confirm('].forEach(t=>assert.ok(html.includes(t),t));
});
test('negative control: source identity mutation is rejected',()=>{
 const bad=structuredClone(source.source_questions);bad[0].question_id='PHYS-NLM-999';assert.throws(()=>verifySource(bad));
});
test('negative control: source stem mutation is rejected',()=>{
 const bad=structuredClone(source.source_questions);bad[0].stem+=' BROKEN';assert.throws(()=>verifySource(bad));
});
test('negative control: pre-attempt answer disclosure is rejected',()=>{
 const bad=html.replace('<div id="workspace"></div>','<div id="workspace">Correct adapted option: A</div>');
 assert.notEqual(bad,html);assert.throws(()=>verifyPreAttempt(bad));
});
test('negative control: wrong display key is rejected',()=>{
 const bad=structuredClone(display);bad.items[1].key='A';assert.throws(()=>verifyDisplay(bad));
});
const tokens=s=>new Set((s.match(/\p{L}+(?:['’]\p{L}+)*/gu)||[]).map(x=>x.toLowerCase()));
function cue(row){
 const wc={},wordset={},mark={},reason=new Set(['because','therefore','since','thus','hence']);
 for(const [id,s] of Object.entries(row.options)){wc[id]=s.split(/\s+/).length;wordset[id]=tokens(s);mark[id]=[...wordset[id]].filter(x=>reason.has(x))}
 const rest=new Set(Object.entries(wordset).filter(([id])=>id!==row.key).flatMap(([,set])=>[...set]));
 const shared=[...tokens(row.stem)].filter(x=>wordset[row.key].has(x)&&!rest.has(x)).sort();
 const flags=[];
 if(shared.length)flags.push('SHARED_WORD_KEY_ONLY');
 if(wc[row.key]>Math.max(...Object.entries(wc).filter(([id])=>id!==row.key).map(([,n])=>n)))flags.push('LONGEST_KEY');
 if(mark[row.key].length&&!Object.entries(mark).some(([id,a])=>id!==row.key&&a.length))flags.push('REASONING_KEY_ONLY');
 return {id:row.variant_id,word_counts:wc,correct_only_question_words:shared,reasoning_markers:mark,flags};
}
test('cue-equivalent screen (does NOT approve subject quality)',()=>{
 const cues=display.items.map(cue);
 assert.deepEqual(cues.map(x=>x.flags),[['SHARED_WORD_KEY_ONLY'],[]]);
 console.log('CUE_SCREEN',JSON.stringify(cues));
});
try{
 const data=execFileSync('git',['show','455103ad312ab8b6627aa7a1199b0bd7d5b0af8e:TEST/physics-research/question_bank_mechanics_grade9.v1.json'],{encoding:'utf8',maxBuffer:3000000});
 test('full pinned bank SHA-256 and exact selected-row equality',()=>{
 assert.equal(sha(Buffer.from(data,'utf8')),'c87ad141e4db355276b8ae4e2afb925663b12d5b0e55761df763ee1c7b387685');
 const b=JSON.parse(data);assert.equal(b.questions.length,39);
 assert.deepEqual(b.questions.filter(x=>sourceIDs.includes(x.question_id)),source.source_questions);
 });
}catch(e){console.log('NOT_RUN full-bank git-show comparison: pinned object unavailable in this checkout; row-digest checks still ran; '+String(e.message).split('\n')[0])}
console.log('RESULT',passed,'passed;',process.exitCode||0,'exit code. This static suite is not a browser-interaction verdict.');
