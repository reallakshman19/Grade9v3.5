#!/usr/bin/env node
// Run the F02-owned untrusted event trace unchanged in Node/V8.
// This is a fake-DOM/source-contract probe, NEVER real-browser or academic proof.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const QID='Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01';
const MID='MIC-TEST-IMO-G9-COMMON-BASE-RELATION';
const KEY=`f02-trace:f04-vm-digest:${QID}`;
const text=fs.readFileSync(process.argv[2]||'Shared/tools/render_core.py','utf8');
const match=/def f02_local_trace_js\(js: str\) -> str:[\s\S]*?    trace = r"""([\s\S]*?)"""/.exec(text);
if(!match)throw Error('Source-owned F02 trace not found');
const code=match[1],storage=new Map(),SCHEMA='F02_BROWSER_LOCAL_UNTRUSTED_TRACE_V1';
let blocked=false,n=0;const check=(x,reason)=>{assert.ok(x,reason);n++};
class El {
 constructor(data={}){this.dataset={...data};this.listeners=[];this.box=null;this.article=null;this.parent=null;this.textContent=''}
 addEventListener(t,fn){if(t==='click')this.listeners.push(fn)}
 contains(node){return node===this||node.parent===this}
 click(){const event={target:this};this.listeners.forEach(fn=>fn(event));this.parent?.listeners.forEach(fn=>fn(event))}
 closest(selector){return selector==='[data-g9-attempt-box]'?this.box:selector==='article[data-g9-role="CORE1A"]'?this.article:selector==='a[data-g9-repair-ref="TC-02"][data-g9-concept-link]'&&this.isRepairLink?this:null}
}
function visit(role,search='',valid=false){
 const article=new El(role==='CORE2A'?{g9Role:'CORE2A',g9Unit:QID}:{g9Role:'CORE1A'});
 const status=new El(),commit=new El(),repair=new El(),gate=new El(),review=new El(),guided=new El(),back=new El();
 commit.box=new El();gate.article=article;repair.isRepairLink=true;repair.parent=article;
 const q=(selector,root)=>{
  if(selector==='[data-g9-f02-trace-status]')return [status];
  if(selector===`article[data-g9-unit="${QID}"]`)return role==='CORE2A'?[article]:[];
  if(selector===`article[data-g9-role="CORE2A"][data-g9-unit="${QID}"]`)return role==='CORE2A'?[article]:[];
  if(selector==='[data-g9-commit]'&&root===article)return [commit];
  if(selector==='[data-g9-repair-ref="TC-02"][data-g9-concept-link]'&&root===article)return [repair];
  if(selector===`[data-g9-concept-check][data-g9-concept-ref="${MID}"]`)return role==='CORE1A'?[gate]:[];
  if(selector==='[data-g9-concept-review]'&&root===gate)return [review];
  if(selector==='[data-g9-concept-commit]'&&root===gate)return [guided];
  if(selector==='[data-g9-authored-core2a-return]'&&root===article)return [back];
  throw Error('Unexpected DOM query '+selector)
 };
 const store={get:k=>storage.get(k)||null,set:(k,v)=>{if(blocked)return false;storage.set(k,v);return true}};
 vm.runInNewContext(code,{scope:'f04-vm-digest',q,store,validAttempt:()=>valid,window:{location:{search}},URLSearchParams},{timeout:1500});
 return {article,status,commit,repair,review,back}
}
const read=()=>JSON.parse(storage.get(KEY)),events=()=>read().events.map(e=>e.kind);
let page=visit('CORE2A');
check(page.status.dataset.g9F02TraceState==='NOT_RECORDED','empty trace');
page.commit.click();check(!storage.has(KEY),'empty attempt rejected');
page=visit('CORE2A','',true);page.commit.click();
check(events().join()==='ATTEMPT_COMMIT'&&!read().assisted,'commit unassisted');
page.repair.click();check(events().join()==='ATTEMPT_COMMIT,REPAIR_NAV'&&read().assisted,'repair is assisted');
page=visit('CORE1A',`?g9-return=${QID}&g9-concept=${MID}`);
page.article.dataset.g9ConceptAidExposure='guided_study';page.review.click();page.back.click();
check(events().join()==='ATTEMPT_COMMIT,REPAIR_NAV,GUIDED_OPEN,RETURN_CLICK','ordered journey');
page=visit('CORE2A');check(page.article.dataset.g9F02Assisted==='1','new page assisted');
check(read().events.every((e,i)=>e.n===i+1),'monotonic event numbers');
const unchanged=storage.get(KEY);
page=visit('CORE1A',`?g9-return=WRONG&g9-concept=${MID}`);
page.article.dataset.g9ConceptAidExposure='guided_study';page.review.click();page.back.click();
check(storage.get(KEY)===unchanged,'wrong question cannot record return');
page=visit('CORE2A');check(page.article.dataset.g9F02Assisted==='1','wrong query does not clear help');
page=visit('CORE2A','',true);page.commit.click();
check(events().at(-1)==='ASSISTED_ATTEMPT_COMMIT'&&read().assisted,
      'post-help reattempt cannot be relabeled independent');
check(page.status.textContent.includes('remains assisted, not independent transfer'),
      'post-help status tells learner it is assisted practice');
let edited=read();edited.protected_W='SECRET';edited.events[0].response='PII';
storage.set(KEY,JSON.stringify(edited));page=visit('CORE2A');page.repair.click();
check(!storage.get(KEY).includes('SECRET')&&!storage.get(KEY).includes('PII'),'drop extraneous local fields');
storage.set(KEY,'{bad-json');page=visit('CORE2A');
check(page.status.dataset.g9F02TraceState==='INVALID_OR_UNAVAILABLE'&&page.article.dataset.g9F02Assisted==='1','corruption fails closed');
page.commit.click();check(storage.get(KEY)==='{bad-json','do not overwrite invalid state');
storage.delete(KEY);blocked=true;page=visit('CORE2A','',true);page.commit.click();
check(page.status.dataset.g9F02TraceState==='NOT_SAVED'&&!storage.has(KEY),'storage error visible');
blocked=false;storage.set(KEY,JSON.stringify({schema:SCHEMA,events:[{n:2,kind:'RETURN_CLICK'}],assisted:true,overflow:false}));
page=visit('CORE2A');check(page.status.dataset.g9F02TraceState==='INVALID_OR_UNAVAILABLE','bad ordinal denied');
storage.delete(KEY);page=visit('CORE2A','',true);
for(let i=0;i<34;i++)page.commit.click();
check(read().events.length===32&&read().overflow&&page.status.dataset.g9F02TraceState==='INCOMPLETE','overflow held');
console.log(`F04 SOURCE V8 F02 TRACE: ${n}/${n} assertions PASS — fake DOM/storage, not real browser or independent credit`);
