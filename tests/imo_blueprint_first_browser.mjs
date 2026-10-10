#!/usr/bin/env node
// Issue #164: actual held-page browser smoke, derived from golden T01/T03/T09.
// No publisher source data, page deployment, automated math grading, or sign-off.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const directory = path.resolve(process.argv[2] || '');
const evidenceDir = path.resolve(process.argv[3] || path.join(directory, 'browser-evidence'));
if (!fs.existsSync(path.join(directory, 'core2b.html'))) {
  throw new Error('usage: node tests/imo_blueprint_first_browser.mjs <real-render-output-dir> [evidence-dir]');
}
fs.mkdirSync(evidenceDir, { recursive: true });

const variant = process.argv[4] || 'five';
assert.ok(['five','boundary'].includes(variant), 'unknown transfer variant');
const profiles = [320, 390, 768, 1280];
const result = { status: 'CANDIDATE_BROWSER_SMOKE', variant, widths: profiles, checks: [] };
const browser = await chromium.launch({ headless: true });
try {
  for (const width of profiles) {
    const context = await browser.newContext({
      viewport: { width, height: 900 },
      reducedMotion: 'reduce',
    });
    for (const role of ['core2a', 'core1a', 'core2b']) {
      const page = await context.newPage();
      const errors = [];
      const requests = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('requestfailed', request => requests.push(request.url()));
      await page.goto(pathToFileURL(path.join(directory, role + '.html')).href);
      await page.waitForLoadState('load');
      const dimensions = await page.evaluate(() => ({
        scroll: document.documentElement.scrollWidth,
        client: document.documentElement.clientWidth,
      }));
      assert.ok(dimensions.scroll <= dimensions.client + 1,
        role + ' horizontal overflow at ' + width + ': ' + JSON.stringify(dimensions));
      assert.ok(await page.locator('article[data-g9-role="' + role.toUpperCase() + '"]').count() > 0,
        'wrong page role for ' + role);
      if (role !== 'core1a') {
        const article = page.locator('article[data-g9-role="' + role.toUpperCase() + '"]').first();
        const gates = article.locator('details[data-requires-attempt]');
        assert.ok(await gates.count() > 0, role + ' missing post-attempt disclosure');
        const box = article.locator('[data-g9-attempt-box]').first();
        const commit = box.locator('[data-g9-commit]');
        const field = box.locator('textarea[data-g9-attempt],input[data-g9-attempt]').first();
        assert.ok(await field.count() === 1, role + ' missing typed learner attempt');
        const before = await article.innerText();
        if (role === 'core2b') {
          const secret = variant === 'boundary' ? 'n mod 4 != 1' : 'gcd(24,5)=1';
          assert.ok(!before.includes(secret), 'protected transfer proof is visible before an attempt');
          assert.equal(await article.locator('figure[data-g9-stage="PRE_ATTEMPT"]').count(), 1,
            'missing safe five-factor figure');
        }
        await commit.click();
        assert.ok((await gates.first().getAttribute('data-locked')) !== null,
          'blank commitment unlocked ' + role);
        await field.fill(role === 'core2a'
          ? 'Three examples are not a universal proof. I must consider arbitrary m and all residues.'
          : 'For any n, prove four factors give 24 and five factors give 5; combine coprime divisors.');
        await commit.click();
        assert.equal(await gates.first().getAttribute('data-locked'), null,
          'valid typed commitment did not unlock ' + role);
        if (role === 'core2b') {
          assert.ok(await article.locator('a[href^="core1a.html#"]').count() > 0,
            'post-attempt concept-repair navigation is missing');
        }
        await gates.first().locator('summary').click();
        assert.ok(await gates.first().evaluate(element => element.open),
          role + ' disclosure cannot open after commitment');
        await page.emulateMedia({ media: 'print' });
        assert.ok((await article.count()) === 1, 'print media discarded learner question');
        await page.emulateMedia({ media: 'screen' });
      }
      assert.deepEqual(errors, [], role + ' JS errors at ' + width);
      assert.deepEqual(requests, [], role + ' missing page assets at ' + width);
      if (width === 390 || width === 1280) {
        await page.screenshot({
          path: path.join(evidenceDir, role + '-' + width + '.png'),
          fullPage: true,
        });
      }
      result.checks.push({ role, width, overflow_px: dimensions.scroll - dimensions.client,
        page_errors: errors.length, failed_requests: requests.length, status: 'PASS' });
      await page.close();
    }
    await context.close();
  }
} finally {
  await browser.close();
}
fs.writeFileSync(path.join(evidenceDir, 'browser-receipt.json'),
  JSON.stringify(result, null, 2) + '\n');
console.log('PASS: actual Chromium, 3 Core roles x 4 widths, attempt gates, safe transfer stage, repair route, print media smoke');
