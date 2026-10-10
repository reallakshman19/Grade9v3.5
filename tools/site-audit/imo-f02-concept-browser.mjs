#!/usr/bin/env node
/** #138: TEST-only Chromium witness for neutral Core1A checkpoint, no mastery claim. */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const folder = path.resolve(process.argv[2] || '');
const html = path.join(folder, 'core1a.html');
if (!process.argv[2] || !fs.existsSync(html)) throw new Error('Provide rendered core1a.html directory');
const out = path.join(folder, 'browser-evidence');
fs.mkdirSync(out, { recursive: true });
const result = { schema: 'imo-f02-concept-first-chromium/v2', source: 'TEST_CANDIDATE',
  authentic_core2_admitted: false, mastery_verified: false, human_screen_reader: 'NOT_RUN',
  viewports: [], failures: [], printed_pdf: null };
const assert = (ok, label) => { if (!ok) result.failures.push(label); };
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 390, 768, 1280]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(pathToFileURL(html).href, { waitUntil: 'load' });
    const check = page.locator('[data-g9-concept-check]');
    const targets = page.locator('[data-g9-concept-target]');
    assert(await check.count() === 1, width + ': expected one neutral checkpoint');
    assert(await targets.count() >= 2, width + ': expected hidden worked/exit targets');
    assert(await targets.first().isHidden(), width + ': construction revealed before check');
    const submit = page.locator('[data-g9-concept-commit]');
    await page.locator('[data-g9-concept-option][value="ADD"]').check();
    await page.locator('[data-g9-concept-reason]').fill('An exponent increase multiplies the power by a factor of the base.');
    await submit.click();
    assert(await targets.first().isHidden(), width + ': wrong additive law unblocked construction');
    assert(await page.locator('article[data-g9-role="CORE1A"]').getAttribute('data-g9-concept-progress') === 'needs_review',
      width + ': wrong choice not marked as needs review');
    await page.locator('[data-g9-concept-option][value="FACTOR"]').check();
    await page.locator('[data-g9-concept-reason]').fill('No');
    await submit.click();
    assert(await targets.first().isHidden(), width + ': short reflection unblocked construction');
    assert(await page.locator('article[data-g9-role="CORE1A"]').getAttribute('data-g9-concept-progress') === 'needs_reflection',
      width + ': missing reflection progress not recorded');
    // Mathematical wording without the old keyword list must no longer be rejected.
    await page.locator('[data-g9-concept-reason]').fill(
      'One extra copy of five is attached to the previous group.');
    await submit.click();
    assert(await targets.first().isVisible(), width + ': authored reflection failed to reveal construction');
    assert(await page.locator('article[data-g9-role="CORE1A"]').getAttribute('data-g9-concept-check-completed') === 'formative_only',
      width + ': wrong evidence state (must remain formative only)');
    assert(await page.locator('article[data-g9-role="CORE1A"]').getAttribute('data-g9-concept-progress') === 'guided_example_open',
      width + ': guided study progress not recorded');
    assert((await page.locator('[data-g9-concept-feedback]').innerText()).includes('NOT been graded'),
      width + ': missing explicit warning that free text was not graded');
    const focused = await page.evaluate(() => document.activeElement?.tagName || '');
    assert(['H3', 'H4'].includes(focused), width + ': focus not moved to revealed section heading');
    if (width === 390) {
      const access = await browser.newPage({ viewport: {width:390,height:900}, reducedMotion:'reduce' });
      access.on('pageerror', e => result.failures.push('accessibility probe JS exception: '+String(e)));
      await access.goto(pathToFileURL(html).href, {waitUntil:'load'});
      assert(await access.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches),
        '390: reduced-motion media emulation not enabled');
      const conceptId = await access.locator('[data-g9-concept-check]').getAttribute('data-g9-concept-ref');
      const reasonInput = access.locator('[data-g9-concept-reason]');
      assert(await reasonInput.getAttribute('id') === conceptId + '-concept-reason',
        '390: rationale input does not have microtopic-scoped ID');
      assert(await reasonInput.getAttribute('aria-describedby') === conceptId + '-concept-scope',
        '390: rationale input not programmatically described');
      assert(await access.locator('[id="' + conceptId + '-concept-scope"]').count() === 1,
        '390: accessible description missing or duplicated');
      // CSS zoom is a reflow/keyboard stress test, NOT a claim of native 200% browser zoom.
      await access.evaluate(() => { document.body.style.zoom = '200%'; });
      const guide = access.locator('[data-g9-concept-review]');
      await guide.focus();
      await access.keyboard.press('Enter');
      assert(await access.locator('[data-g9-concept-target]').first().isVisible(),
        '390 CSS 200%: keyboard-guided-study button did not reveal construction');
      assert(await access.locator('article[data-g9-role="CORE1A"]').getAttribute('data-g9-concept-progress') === 'guided_without_check',
        '390 CSS 200%: bypass incorrectly classified as checked');
      assert(await access.locator('article[data-g9-role="CORE1A"]').getAttribute('data-g9-concept-check-completed') === null,
        '390 CSS 200%: bypass falsely marked as completed');
      assert(['H3','H4'].includes(await access.evaluate(() => document.activeElement?.tagName || '')),
        '390 CSS 200%: focus not moved after keyboard reveal');
      await access.screenshot({path:path.join(out,'core1a-390-css-zoom-200.png'),fullPage:true});
      await access.reload();
      assert(await access.locator('[data-g9-concept-target]').first().isHidden(),
        '390: refreshing a page must not retain fake learner progress');
      assert(await access.locator('[data-g9-learning-progress]').getAttribute('data-g9-progress') === 'not_started',
        '390: progress not reset on fresh page visit');
      result.accessibility = {
        css_zoom_200: 'KEYBOARD_PATH_PASS_WHEN_ASSERTIONS_CLEAR',
        browser_native_zoom: 'NOT_RUN', human_screen_reader: 'NOT_RUN',
        reduced_motion_emulated: true, keyboard_enter_guided_bypass: true,
        no_client_persistence_claim: true
      };
      await access.close();
    }
    if (width === 1280) {
      // Real governed learner prints start from a fresh page, with the
      // lesson gated on screen. Print must include the authored construction
      // and re-fit the three SVG stages; no learner concept check is performed.
      const printPage = await browser.newPage({ viewport: { width: 1280, height: 900 } });
      await printPage.goto(pathToFileURL(html).href, { waitUntil: 'load' });
      const untouchedTargets = printPage.locator('[data-g9-concept-target]');
      assert(await untouchedTargets.first().isHidden(),
        'print: guided lesson unexpectedly exposed on fresh interactive page');
      await printPage.emulateMedia({ media: 'print' });
      assert(await untouchedTargets.first().isVisible(),
        'print: guided Core1A construction missing from fresh learner PDF');
      // Media-query change callbacks fire asynchronously in Chromium.
      // Poll the actual geometry rather than sampling before print refit runs.
      let printedStages = {found:false};
      for (let probe = 0; probe < 50; probe++) {
        printedStages = await printPage.locator('figure[data-g9-stage="TEACHING"]').evaluateAll(figures => {
        const target = figures.find(f => f.dataset.g9StagesTotal === '3');
        if (!target) return { found: false };
        const svg = target.querySelector('svg');
        const stages = [...svg.querySelectorAll('g[data-g9-stage-id]')];
        const visible = stages.filter(g => getComputedStyle(g).display !== 'none');
        const b = svg.viewBox.baseVal;
        const fits = visible.every(g => {
          const r = g.getBBox();
          return r.x >= b.x - 1 && r.y >= b.y - 1 &&
            r.x + r.width <= b.x + b.width + 1 &&
            r.y + r.height <= b.y + b.height + 1;
        });
        return { found: true, count: stages.length, visible: visible.length,
          allInsideViewBox: fits, viewBox: [b.x,b.y,b.width,b.height] };
        });
        if (printedStages.found && printedStages.count === 3 &&
            printedStages.visible === 3 && printedStages.allInsideViewBox) break;
        await printPage.waitForTimeout(20);
      }
      assert(printedStages.found && printedStages.count === 3 &&
        printedStages.visible === 3 && printedStages.allInsideViewBox,
        'print: authored three SVG stages are not all visible within print viewBox: ' + JSON.stringify(printedStages));
      result.printed_svg = printedStages;
      await printPage.pdf({ path: path.join(out, 'core1a-print.pdf'), printBackground: true });
      const stat = fs.statSync(path.join(out, 'core1a-print.pdf'));
      result.printed_pdf = { bytes: stat.size, status: stat.size > 1000 ? 'GENERATED_NOT_MANUALLY_INSPECTED' : 'INVALID' };
      assert(stat.size > 1000, 'print PDF is unexpectedly small');
      await printPage.close();
    }
    await page.screenshot({ path: path.join(out, 'core1a-' + width + '.png'), fullPage: true });
    result.viewports.push({ width, focus_after_check: focused, page_errors: errors,
      note: 'TEST-only visible behavior; no learner comprehension claim' });
    assert(errors.length === 0, width + ': uncaught page errors ' + errors.join('; '));
    await page.close();
  }
} finally {
  await browser.close();
  fs.writeFileSync(path.join(out, 'result.json'), JSON.stringify(result, null, 2) + '\n');
}
console.log(JSON.stringify(result, null, 2));
if (result.failures.length) process.exitCode = 1;
