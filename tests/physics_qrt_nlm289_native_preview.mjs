#!/usr/bin/env node
/**
 * Issue #289 read-only temporary Chromium comparison of actual native rendering:
 * original source versus proposed in-memory #295 NLM content.
 * Source, QRT, grading, independent-transfer and release all remain unapproved.
 */
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {createReadStream, readFileSync, writeFileSync, existsSync} from 'node:fs';
import {resolve, join, extname, sep} from 'node:path';
const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const root = resolve(process.cwd());
const flag = process.argv.indexOf('--render-dir');
if (flag < 0 || !process.argv[flag+1]) throw new Error('TEMP_RENDER_DIR_REQUIRED');
const folder = resolve(process.argv[flag+1]);
if (!folder.startsWith(root + sep + 'build' + sep)) throw new Error('OUTSIDE_BUILD_REFUSED');
const preview = JSON.parse(readFileSync(join(folder, 'preview-report.json'), 'utf8'));
if (preview.preview_only !== true || preview.release !== 'HOLD') throw new Error('NOT_A_HELD_PREVIEW');
const id = 'Q-PHY-NLM-2B-FRICTION-STATE-01';
const siblingId = 'Q-PHY-NLM-2B-FRICTION-ANGLED-THRESHOLD-04';
const report = {
  schema: 'physics-qrt.nlm289-native-chromium/v1', source: preview.source_commit,
  proposal: preview.proposal_commit, question_id:id, controls:[],
  academic_verdict:'NOT_ATTESTED', novelty_verdict:'NOT_ESTABLISHED',
  science_grader:'NOT_PRESENT_IN_NATIVE_FREE_RESPONSE', release:'HOLD',
  known_gaps:['CORE2B_H2_H3_NOT_RENDERED','D5_INDEPENDENT_NOVELTY_NOT_REVIEWED',
              'D2_ACTUAL_SCIENCE_GRADER_NOT_PROVEN','HUMAN_SCIENCE_NOT_AUTHENTICATED']
};
const add = (name, pass, detail) => {
  report.controls.push({name, status:pass?'PASS':'FAIL', detail});
  if (!pass) report.failed = true;
};
const mime = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript',
              '.svg':'image/svg+xml','.json':'application/json'};
const server = createServer((req,res) => {
  try {
    const path = resolve(root, '.' + decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname));
    if (path !== root && !path.startsWith(root + sep)) {res.writeHead(403);res.end();return;}
    if (!existsSync(path)) {res.writeHead(404);res.end();return;}
    res.writeHead(200, {'Content-Type':mime[extname(path)]||'application/octet-stream',
                        'Cache-Control':'no-store'});
    createReadStream(path).pipe(res);
  } catch (e) {res.writeHead(400);res.end();}
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const base = 'http://127.0.0.1:' + server.address().port + '/';
const pageUrl = version => base + folder.slice(root.length+1).split(sep).join('/') + '/' +
                           version + '/core2b.html#' + id;
let browser;
try {
  browser = await chromium.launch({headless:true});
  report.browser_version = browser.version();
  for (const viewport of [{width:1366,height:854},{width:390,height:844}]) {
    const ctx = await browser.newContext({viewport});
    const page = await ctx.newPage();
    const errors = [], external = [];
    page.on('pageerror', err=>errors.push(err.message));
    await page.route('**/*', route=>{
      if (route.request().url().startsWith(base)) return route.continue();
      external.push(route.request().url());return route.abort();
    });
    // Positive control: original canonical question really leaks model instructions.
    await page.goto(pageUrl('original'),{waitUntil:'load'});
    const old = page.locator('article[data-g9-unit="'+id+'"][data-g9-role="CORE2B"]');
    add('original_article_unique_'+viewport.width, await old.count()===1,await old.count());
    if (await old.count()===1) {
      const visible = await old.innerText();
      add('original_visible_model_instruction_'+viewport.width,
          visible.includes('Resolve each pull into horizontal and vertical components.') &&
          visible.includes('do not take N = mg'), 'original learner-visible conditions expose model choices');
    }

    // Proposed correction: still the actual shared native renderer, but source patch is in-memory.
    await page.goto(pageUrl('candidate'),{waitUntil:'load'});
    const candidate = page.locator('article[data-g9-unit="'+id+'"][data-g9-role="CORE2B"]');
    add('proposed_article_unique_'+viewport.width,await candidate.count()===1,await candidate.count());
    const sibling = page.locator('article[data-g9-unit="'+siblingId+'"][data-g9-role="CORE2B"]');
    add('sibling_still_selected_'+viewport.width,await sibling.count()===1,await sibling.count());
    if (await candidate.count()!==1) {await ctx.close();continue;}
    const visible = await candidate.innerText();
    add('proposed_d1_no_explicit_model_cues_'+viewport.width,
        !visible.includes('Resolve each pull into horizontal and vertical components.') &&
        !visible.includes('do not take N = mg') &&
        !visible.includes('Write N from the vertical balance') &&
        !visible.includes('75/(cos'), 'learner-visible article before commitment');
    add('proposed_h1_orientation_visible_'+viewport.width,
        visible.includes('Which external forces act on the crate'),
        'the native renderer projects the ORIENT rung');
    const diagram = candidate.locator('figure[data-g9-stage="PRE_ATTEMPT"] svg');
    const present = await diagram.count()===1;
    const stageIds = present ? await diagram.locator('[data-g9-stage-id]').evaluateAll(
      els=>els.map(el=>el.getAttribute('data-g9-stage-id'))) : [];
    add('proposed_only_safe_v0_'+viewport.width,
        present && stageIds.length===1 && stageIds[0]==='VIS-NLM-CRATE3DIR-V0',
        stageIds);
    const svgText = present ? await diagram.evaluate(el=>el.outerHTML) : '';
    add('svg_has_no_solution_metadata_'+viewport.width,
        present && !svgText.includes('N = 100 − P sin') &&
        !svgText.includes('P cos θ = 0.75') &&
        !svgText.includes('62.5 N') &&
        !svgText.includes('Stage 4:'),
        'pre-attempt DOM SVG excludes V1-V3 and original answer-containing desc');
    // Known deficiency: the current native Core2B page only projects H1.
    add('identified_unrendered_h2_h3_'+viewport.width,
        (await candidate.locator('[data-g9-next-rung]').count())===0,
        'DETECTED GAP, not a functioning H2/H3 hint-ladder PASS');
    const review = candidate.locator('details[data-requires-attempt]');
    const commit = candidate.locator('[data-g9-attempt-box] [data-g9-commit]');
    add('candidate_locked_initially_'+viewport.width,
        (await review.count())===1 &&
        (await review.getAttribute('data-locked'))!==null &&
        (await candidate.getAttribute('data-attempted'))===null,
        'protected solution remains unattempted');
    await commit.click();
    add('candidate_empty_commit_rejected_'+viewport.width,
        (await candidate.getAttribute('data-attempted'))===null,
        'no response cannot unlock the protected solution');
    const answer = candidate.locator('[data-g9-attempt-box] [data-g9-attempt]').first();
    add('candidate_free_response_present_'+viewport.width,(await answer.count())===1,await answer.count());
    if(await answer.count()===1) {
      // Deliberately wrong scientific model: current submit gate accepts any nonempty prose.
      await answer.fill('N = mg = 100 N for every angle. The largest angle must always win.');
      await commit.click();
      add('known_no_science_marking_'+viewport.width,
          (await candidate.getAttribute('data-attempted'))==='1',
          'INVALID PHYSICS response unlocks attempt state; NOT graded as correct');
      await review.locator('summary').click();
      const slot = review.locator('[data-g9-payload-slot]');
      add('candidate_answer_only_after_attempt_'+viewport.width,
          (await review.evaluate(el=>el.open)) &&
          (await slot.innerText()).includes('62.5 N'),
          'protected answer materialized only after nonempty commitment');
      if(await sibling.count()===1) {
        add('sibling_remains_unattempted_'+viewport.width,
            (await sibling.getAttribute('data-attempted'))===null,
            'one question does not claim sibling learner attempt');
      }
    }

    if(viewport.width===1366){
      const cases=[
        {id:"TP1",expected:'VALID',response:"N=100-P sin(theta), Pcos(theta)<=0.75N, hence Pcrit=0.75mg/(cos(theta)+0.75sin(theta)). Values: 75 N, 60 N, 62.5 N. At 61 N only the 37-degree direction exceeds its threshold; equality can still be static equilibrium."},
        {id:"TP2",expected:'VALID',response:"Using an equivalent expression, Pcrit=mg/(sin(theta)+cos(theta)/mu_s) with mu_s=0.75. This gives 75 N, 60 N and 62.5 N for horizontal, 37 and 53 degrees. Thus only 37 degrees can initiate motion at 61 N."},
        {id:"TP3",expected:'VALID',response:"Choose downward as positive: mg-N-Psin(theta)=0 so N=mg-Psin(theta). Choose friction positive left, balancing the rightward component by -f+Pcos(theta)=0. Then f=Pcos(theta)<=mu_sN, giving 75 N, 60 N, 62.5 N and 37 degrees at 61 N."},
        {id:"TP4",expected:'VALID',response:"At 37 degrees with P=60 N, horizontal demand is 48 N and static limit is 0.75(100-36)=48 N: the crate can still be in limiting equilibrium. At P=61 N, need=48.8 N and limit=47.55 N, so rest is impossible. Other critical pulls are 75 N and 62.5 N, so choose only 37 degrees."},
        {id:"FP1",expected:'INVALID_OR_REQUIRES_HUMAN_QUALIFICATION',response:"For every angle N=mg=100 N, because weight determines the normal unconditionally; the angled pulls do not change friction capacity."},
        {id:"FP2",expected:'INVALID_OR_REQUIRES_HUMAN_QUALIFICATION',response:"The 53-degree pull is best because the steepest upward pull reduces the normal force most, so the worker should always choose 53 degrees."},
        {id:"FP3",expected:'INVALID_OR_REQUIRES_HUMAN_QUALIFICATION',response:"The horizontal driving force on the crate is exactly P even for an angled rope, so P=mu_s N is the threshold equation."},
        {id:"FP4",expected:'INVALID_OR_REQUIRES_HUMAN_QUALIFICATION',response:"The crate must already be sliding when P equals its critical value. Equality guarantees movement rather than possible limiting static equilibrium."},
        {id:"FP5",expected:'INVALID_OR_REQUIRES_HUMAN_QUALIFICATION',response:"A very tall narrow real crate with a high pulling point can never tip, because the sliding-threshold formula also applies to all rigid geometries without checking rotation."},
      ];
      const outcomes=[];
      for(const row of cases){
        // Exercise each student response against the actual native input/commit path,
        // NEVER a fabricated semantic scorer. Reload so every case is isolated.
        await page.goto(pageUrl('candidate'),{waitUntil:'load'});
        const item=page.locator('article[data-g9-unit="'+id+'"][data-g9-role="CORE2B"]');
        const answer=item.locator('[data-g9-attempt-box] [data-g9-attempt]').first();
        await answer.fill(row.response);
        await item.locator('[data-g9-commit]').click();
        const attempted=(await item.getAttribute('data-attempted'))==='1';
        const review=item.locator('details[data-requires-attempt]');
        await review.locator('summary').click();
        const reveal=(await review.evaluate(el=>el.open)) &&
          (await review.locator('[data-g9-payload-slot]').innerText()).includes('62.5 N');
        outcomes.push({case_id:row.id,physics_class:row.expected,
                       registered_attempt:attempted,review_unlocked:reveal,
                       academically_marked:null});
      }
      report.assessment_corpus={
        scope:'REAL_NATIVE_ATTEMPT_GATE_NOT_PHYSICS_MARKING',
        total:outcomes.length,
        proposed_positive:cases.filter(x=>x.expected==='VALID').length,
        proposed_wrong_or_qualified:cases.filter(x=>x.expected!=='VALID').length,
        registered_attempts:outcomes.filter(x=>x.registered_attempt).length,
        solution_reveals:outcomes.filter(x=>x.review_unlocked).length,
        semantic_true_positive_count:null,
        semantic_true_negative_count:null,
        warning:'All claims are text examples from draft PR295 review categories, NOT human-validated independent marks.',
        outcomes
      };
      add('nine_case_attempt_gate_not_grader',
        outcomes.length===9 && outcomes.every(x=>x.registered_attempt&&x.review_unlocked),
        'All 4 proposed-valid and 5 proposed-invalid text responses unlock the same review; neither pass/fail nor diagnosis is computed.');
    }

    add('no_javascript_errors_'+viewport.width,errors.length===0,errors);
    add('no_external_requests_'+viewport.width,external.length===0,external);
    await ctx.close();
  }
} catch(e) {
  report.failed=true;report.fatal=String(e);report.stack=String(e.stack||'').slice(0,1800);
} finally {
  await browser?.close();
  await new Promise(resolve=>server.close(resolve));
}
report.browser_control_verdict=report.failed?'FAIL':'PASS_MECHANICS_AND_GAPS_DETECTED';
writeFileSync(join(folder,'chromium-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(report.failed) process.exitCode=1;
