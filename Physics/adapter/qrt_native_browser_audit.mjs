#!/usr/bin/env node
/**
 * Real Chromium witness for one existing Physics Core2B question.
 * Read-only to source and published assets. Serve only a temporary native render.
 * This checks interaction mechanics, NOT scientific, pedagogical or release approval.
 *
 * node Physics/adapter/qrt_native_browser_audit.mjs --render-dir build/physics-qrt-browser
 */
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {readFileSync, existsSync, createReadStream} from 'node:fs';
import {resolve, join, extname, sep} from 'node:path';
import {createServer} from 'node:http';
const require=createRequire(import.meta.url);
const {chromium}=require('playwright');

const root=resolve(process.cwd());
const index=process.argv.indexOf('--render-dir');
if(index<0||!process.argv[index+1])throw new Error('RENDER_DIR_REQUIRED');
const folder=resolve(process.argv[index+1]);
if(!folder.startsWith(root+sep))throw new Error('ONLY_TEMPORARY_WORKSPACE_RENDER_ALLOWED');
const source=JSON.parse(readFileSync(join(root,'Physics/library/phy-nlm-first-law.v1.json'),'utf8'));
const id='Q-PHY-NLM-2B-FRICTION-STATE-01';
const matches=source.questions.filter(q=>q.id===id);
if(matches.length!==1)throw new Error('SOURCE_QUESTION_NOT_UNIQUE');
const question=matches[0];
const parent=question.transfer?.builds_on?.[0];
const decision=question.answer?.reasoning_route?.find(x=>x.id===question.transfer.protected_move_ref)?.action;
if(!parent||!decision)throw new Error('SOURCE_LINEAGE_OR_DECISION_MISSING');
const bytes=readFileSync(join(folder,'core2b.html'));
const sha256=createHash('sha256').update(bytes).digest('hex');
const content=bytes.toString('utf8');
if(!content.includes('data-g9-render-digest='))throw new Error('NO_NATIVE_RENDER_DIGEST_STAMP');
const digest=content.match(/data-g9-render-digest="([0-9a-f]{16})"/)?.[1];
if(!digest)throw new Error('RENDER_DIGEST_MISSING');

const media={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'};
const server=createServer((req,res)=>{
  try{
    const url=new URL(req.url,'http://127.0.0.1');
    const normalized=resolve(root,'.'+decodeURIComponent(url.pathname));
    if(normalized!==root&&!normalized.startsWith(root+sep)){res.writeHead(403);res.end();return;}
    if(!existsSync(normalized)){res.writeHead(404);res.end();return;}
    res.writeHead(200,{'Content-Type':media[extname(normalized)]||'application/octet-stream','Cache-Control':'no-store'});
    createReadStream(normalized).pipe(res);
  }catch(e){res.writeHead(400);res.end();}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const port=server.address().port;
const base='http://127.0.0.1:'+port+'/';
const url=base+folder.slice(root.length+1).split(sep).join('/')+'/core2b.html#'+id;
const report={
  schema:'physics-qrt.chromium-witness/v1', question_id:id, render_sha256:sha256,
  render_digest:digest, browser_engine:'chromium', controls:[],
  scientific_verdict:'REVIEW_REQUIRED', academic_verdict:'NOT_REVIEWED',
  qrt_verdict:'NOT_RUN', publication_verdict:'NOT_ATTESTED',
  learner_mastery:'NOT_ATTESTED', release_verdict:'HOLD'
};
const add=(name,pass,detail)=>{report.controls.push({name,status:pass?'PASS':'FAIL',detail});if(!pass)report.failed=true;};
let browser;
try{
  browser=await chromium.launch({headless:true});
  report.browser_version=browser.version();
  for(const viewport of [{width:1366,height:854},{width:900,height:1440}]){
    const context=await browser.newContext({viewport});
    const page=await context.newPage();
    const errors=[],external=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.route('**/*',route=>{
      const u=route.request().url();
      if(u.startsWith(base))return route.continue();
      external.push(u);return route.abort();
    });
    await page.goto(url,{waitUntil:'load'});
    const article=page.locator('article[data-g9-unit="'+id+'"][data-g9-role="CORE2B"]');
    add('article_unique_'+viewport.width,(await article.count())===1,await article.count());
    if((await article.count())!==1){await context.close();continue;}
    const details=article.locator('details[data-requires-attempt]');
    const box=article.locator('[data-g9-attempt-box]');
    const slot=details.locator('[data-g9-payload-slot]');
    add('initially_gated_'+viewport.width,(await details.count())===1 &&
      !(await details.evaluate(el=>el.open)) &&
      (await slot.innerText()).trim()==='' &&
      !(await article.getAttribute('data-attempted')),
      'review closed, empty payload and not attempted before commitment');
    const firstVisible=await article.innerText();
    add('initially_no_protected_move_'+viewport.width,!firstVisible.includes(decision),
      'protected deciding action absent from visible learner text');
    const summary=details.locator('summary');
    await summary.click();
    await page.waitForTimeout(80);
    add('empty_attempt_still_locked_'+viewport.width,!(await details.evaluate(el=>el.open)) &&
      (await slot.innerText()).trim()==='','clicked review summary before commitment');
    await box.locator('[data-g9-commit]').click();
    add('empty_commit_rejected_'+viewport.width,!(await article.getAttribute('data-attempted')) &&
      (await slot.innerText()).trim()==='','clicked commit with no answer');
    const attempt=box.locator('[data-g9-attempt]').first();
    add('typed_answer_field_'+viewport.width,(await attempt.count())===1,await attempt.count());
    if(await attempt.count()){
      await attempt.fill('I choose a threshold model, then compare directions.');
      await box.locator('[data-g9-commit]').click();
      add('commit_changes_state_'+viewport.width,(await article.getAttribute('data-attempted'))==='1',
          await article.getAttribute('data-attempted'));
      await summary.click();
      add('committed_answer_visible_'+viewport.width,(await details.evaluate(el=>el.open)) &&
        (await slot.innerText()).includes(decision),
        'protected source deciding action appeared only after valid commitment');
    }
    const lineage=article.locator('a[data-g9-lineage][href*="'+parent+'"]');
    add('prior_exposure_link_'+viewport.width,(await lineage.count())===1,
        {parent,links:await article.locator('a[data-g9-lineage]').count()});
    if(await lineage.count()){
      await lineage.click();
      add('prior_exposure_route_'+viewport.width,page.url().includes('core2a.html#'+parent) &&
        (await page.locator('article[data-g9-unit="'+parent+'"][data-g9-role="CORE2A"]').count())===1,
        page.url());
    }
    add('no_runtime_errors_'+viewport.width,errors.length===0,errors);
    add('no_external_requests_'+viewport.width,external.length===0,external);
    await context.close();
  }
}catch(e){report.failed=true;report.fatal_error=String(e);report.stack=(e.stack||'').slice(0,2500);}
finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
report.browser_control_verdict=report.failed?'FAIL':'PASS_MECHANICS_ONLY';
console.log(JSON.stringify(report,null,2));
if(report.failed)process.exitCode=1;
