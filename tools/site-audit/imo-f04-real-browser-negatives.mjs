#!/usr/bin/env node
/**
 * F04 independent, TEST-only real Chromium negative probes for F02's generated
 * Core2A page. No authored content changes; no answers or learner text emitted.
 * Chromium success is not source custody, mastery, academic or release proof.
 */
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createServer} from 'node:http';
import {chromium} from 'playwright';

const root = path.resolve(process.argv[2] || '');
const receiptPath = path.resolve(process.argv[3] || '');
const html = path.join(root, 'core2a.html');
const QID = 'Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01';
const INERT_ID = 'CORE2A-' + QID + '-reasoning';
const flags = {
  inert_protected_template: false,
  pre_attempt_repair_absent: false,
  empty_attempt_no_event: false,
  initial_attempt_event_only: false,
  response_text_not_persisted: false,
  post_attempt_repair_created: false,
  corrupt_history_denied: false,
  corrupt_history_not_overwritten: false,
  forged_mastery_event_denied: false,
};
const allowedCodes = new Set([
  'MISSING_CANONICAL_PAGE', 'MISSING_SHELL_ASSET', 'INERT_TEMPLATE_INVALID',
  'PRE_ATTEMPT_REPAIR_PRESENT', 'EMPTY_ATTEMPT_STORED',
  'FIRST_ATTEMPT_NOT_MARKED', 'RESPONSE_PERSISTED',
  'POST_ATTEMPT_REPAIR_ABSENT', 'CORRUPT_HISTORY_ACCEPTED',
  'CORRUPT_HISTORY_OVERWRITTEN', 'FORGED_EVENT_ACCEPTED',
  'BROWSER_NEGATIVE_PROBE_FAILED', 'BROWSER_CLEANUP_FAILED'
]);
const check = (test,code) => {if(!test) throw new Error(code);};
let page=null, browser=null;
const shell=path.resolve('public');
const assets=new Map([
  ['/css/modern-learner.css','css/modern-learner.css'],
  ['/css/tablet-12-7.css','css/tablet-12-7.css'],
  ['/js/display-controls.js','js/display-controls.js'],
  ['/js/site-header.js','js/site-header.js']
].map(([route,rel])=>[route,path.join(shell,rel)]));
const server=createServer((req,res)=>{
  const url=(req.url||'').split(/[?#]/,1)[0];
  const target=url==='/core2a.html'?html:assets.get(url);
  if(!target){res.writeHead(404);res.end('not found');return;}
  const type=url.endsWith('.css')?'text/css':url.endsWith('.js')?'application/javascript':'text/html';
  res.writeHead(200,{'Content-Type':type+'; charset=utf-8','Cache-Control':'no-store'});
  const stream=fs.createReadStream(target);
  stream.on('error',()=>res.destroy());
  stream.pipe(res);
});

let reason=null;
try{
  check(process.argv[2] && process.argv[3] && fs.existsSync(html),'MISSING_CANONICAL_PAGE');
  check([...assets.values()].every(x=>fs.existsSync(x)),'MISSING_SHELL_ASSET');
  browser=await chromium.launch({headless:true});
  await new Promise((resolve,reject)=>{
    server.once('error',reject);
    server.listen(0,'127.0.0.1',resolve);
  });
  const origin='http://127.0.0.1:'+server.address().port;
  page=await browser.newPage({viewport:{width:390,height:900}});
  await page.goto(origin+'/core2a.html',{waitUntil:'load'});
  const article=page.locator('article[data-g9-role="CORE2A"][id="'+QID+'"]');
  const repair=article.locator('a[data-g9-repair-ref="TC-02"][data-g9-concept-link]');
  const textBox=article.locator('[data-g9-attempt-box] textarea[data-g9-attempt]');
  const commit=article.locator('[data-g9-commit]').first();
  const status=page.locator('[data-g9-f02-trace-status]');
  const template=article.locator('template[data-g9-payload="'+INERT_ID+'"]');
  check(await article.count()===1 && await template.count()===1 &&
    await template.evaluate(el=>el.content.nodeType===11),
    'INERT_TEMPLATE_INVALID');
  flags.inert_protected_template=true;
  check(await repair.count()===0 && await article.getAttribute('data-attempted')===null,
    'PRE_ATTEMPT_REPAIR_PRESENT');
  flags.pre_attempt_repair_absent=true;

  const storageKey=await page.evaluate(id=>{
    const d=document.documentElement;
    return 'g9-f02-trace:'+d.dataset.g9Product+':'+d.dataset.g9RenderDigest+':'+id;
  },QID);
  await commit.click();
  const emptyValue=await page.evaluate(k=>localStorage.getItem(k),storageKey);
  check(emptyValue===null && await repair.count()===0, 'EMPTY_ATTEMPT_STORED');
  flags.empty_attempt_no_event=true;

  // A fixed TEST marker is never included in the public receipt.
  const sentinel='F04_SYNTHETIC_PRIVATE_RESPONSE_MARKER';
  await textBox.fill(sentinel);
  await commit.click();
  const recordRaw=await page.evaluate(k=>localStorage.getItem(k),storageKey);
  let history=null;
  try{history=JSON.parse(recordRaw||'null');}catch(_){history=null}
  check(history && history.events?.length===1 &&
    history.events[0].kind==='ATTEMPT_COMMIT' &&
    history.assisted===false &&
    await status.getAttribute('data-g9-f02-trace-state')==='UNTRUSTED_LOCAL_ONLY',
    'FIRST_ATTEMPT_NOT_MARKED');
  flags.initial_attempt_event_only=true;
  check(!recordRaw.includes(sentinel),'RESPONSE_PERSISTED');
  flags.response_text_not_persisted=true;
  check(await repair.count()===1,'POST_ATTEMPT_REPAIR_ABSENT');
  flags.post_attempt_repair_created=true;

  const corrupt='{invalid F04 synthetic storage';
  await page.evaluate(([key,value])=>localStorage.setItem(key,value),[storageKey,corrupt]);
  await page.reload({waitUntil:'load'});
  check(await status.getAttribute('data-g9-f02-trace-state')==='INVALID_OR_UNAVAILABLE'
    && await article.getAttribute('data-g9-f02-assisted')==='1',
    'CORRUPT_HISTORY_ACCEPTED');
  flags.corrupt_history_denied=true;
  await textBox.fill('F04_ANOTHER_SYNTHETIC_RESPONSE');
  await commit.click();
  check(await page.evaluate(k=>localStorage.getItem(k),storageKey)===corrupt,
    'CORRUPT_HISTORY_OVERWRITTEN');
  flags.corrupt_history_not_overwritten=true;

  const forged={
    schema:'F02_BROWSER_LOCAL_UNTRUSTED_TRACE_V1',
    events:[{n:1,kind:'INDEPENDENT_MASTERY_VERIFIED'}],
    assisted:false,overflow:false
  };
  await page.evaluate(([key,value])=>localStorage.setItem(key,value),
    [storageKey,JSON.stringify(forged)]);
  await page.reload({waitUntil:'load'});
  check(await status.getAttribute('data-g9-f02-trace-state')==='INVALID_OR_UNAVAILABLE'
    && await article.getAttribute('data-g9-f02-assisted')==='1',
    'FORGED_EVENT_ACCEPTED');
  flags.forged_mastery_event_denied=true;
}catch(error){
  reason=allowedCodes.has(error?.message)?error.message:'BROWSER_NEGATIVE_PROBE_FAILED';
}finally{
  try{await page?.close();await browser?.close();}catch(_){reason||='BROWSER_CLEANUP_FAILED'}
  try{if(server.listening)await new Promise((resolve,reject)=>
    server.close(e=>e?reject(e):resolve()));}catch(_){reason||='BROWSER_CLEANUP_FAILED'}
}
const status=reason===null && Object.values(flags).every(Boolean)?'NEGATIVE_PROBES_OK':'BLOCKED';
const output={
  schema:'imo-f04-real-browser-negatives/v1',
  source:'TEST_AUTHORED_CORE2A',
  viewport_width:390,
  status,
  flags,
  blocking_codes:reason?[reason]:[],
  // The checkout and runtime are verified separately by the GitHub job.
  chromium_execution_attested:false,
  authentic_core2_admitted:false,
  mastery_verified:false,
  academic_accepted:false,
  release_authorized:false,
  core2a_sha256:fs.existsSync(html)?createHash('sha256').update(fs.readFileSync(html)).digest('hex'):null
};
if(process.argv[3]){
  fs.mkdirSync(path.dirname(receiptPath),{recursive:true});
  fs.writeFileSync(receiptPath,JSON.stringify(output,null,2)+'\n');
}
console.log('F04_REAL_BROWSER_NEGATIVE_'+(status==='NEGATIVE_PROBES_OK'?'STRUCTURE_OK':'BLOCKED')+
  '; ACADEMIC_LEARNER_RELEASE_HOLD');
if(status!=='NEGATIVE_PROBES_OK')process.exitCode=1;