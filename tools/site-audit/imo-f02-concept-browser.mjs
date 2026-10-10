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
const result = { schema: 'imo-f02-concept-first-chromium/v1', source: 'TEST_CANDIDATE',
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
    await page.locator('[data-g9-concept-option][value="FACTOR"]').check();
    await page.locator('[data-g9-concept-reason]').fill('I guess the answer but cannot justify it.');
    await submit.click();
    assert(await targets.first().isHidden(), width + ': insufficient rule explanation unblocked construction');
    await page.locator('[data-g9-concept-reason]').fill(
      'The exponent law multiplies the earlier power by one factor of the base, not an addition.');
    await submit.click();
    assert(await targets.first().isVisible(), width + ': valid explanation failed to reveal construction');
    assert(await page.locator('article[data-g9-role="CORE1A"]').getAttribute('data-g9-concept-check-completed') === 'formative_only',
      width + ': wrong evidence state (must remain formative only)');
    const focused = await page.evaluate(() => document.activeElement?.tagName || '');
    assert(['H3', 'H4'].includes(focused), width + ': focus not moved to revealed section heading');
    if (width === 1280) {
      await page.pdf({ path: path.join(out, 'core1a-print.pdf'), printBackground: true });
      const stat = fs.statSync(path.join(out, 'core1a-print.pdf'));
      result.printed_pdf = { bytes: stat.size, status: stat.size > 1000 ? 'GENERATED_NOT_MANUALLY_INSPECTED' : 'INVALID' };
      assert(stat.size > 1000, 'print PDF is unexpectedly small');
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
