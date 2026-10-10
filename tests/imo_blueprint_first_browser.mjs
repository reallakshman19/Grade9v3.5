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
          if (variant === 'boundary') {
            const figure = article.locator('figure[data-g9-stage="PRE_ATTEMPT"]').first();
            const chips = figure.locator('button[data-g9-stage-goto]');
            assert.equal(await chips.count(), 2, 'boundary requires two learner-selectable safe stages');
            assert.equal(await chips.nth(0).getAttribute('aria-pressed'), 'true');
            await chips.nth(1).focus();
            await page.keyboard.press('Enter');
            assert.equal(await chips.nth(1).getAttribute('aria-pressed'), 'true',
              'keyboard stage selection must activate the alternative stage');
            assert.equal(await chips.nth(0).getAttribute('aria-pressed'), 'false');
            assert.ok(await figure.locator('[data-g9-stage-id="BOUNDARY-TARGET-12"]').isVisible(),
              'target-question stage not shown');
            assert.ok(!(await figure.locator('[data-g9-stage-id="BOUNDARY-TRIPLE-FACTORS"]').isVisible()),
              'REPLACE mode must hide the prior stage');
            assert.ok(!(await article.innerText()).includes('n mod 4 != 1'),
              'changing safe stages revealed the protected exception');
            await chips.nth(0).focus();
            await page.keyboard.press('Enter');
            assert.equal(await chips.nth(0).getAttribute('aria-pressed'), 'true');
          }
        }
        await commit.click();
        assert.ok((await gates.first().getAttribute('data-locked')) !== null,
          'blank commitment unlocked ' + role);
        await field.fill(role === 'core2a'
          ? 'Three examples are not a universal proof. I must consider arbitrary m and all residues.'
          : 'For any n, prove four factors give 24 and five factors give 5; combine coprime divisors.');
        if (role === 'core2b' && width === 390) {
          await commit.focus();
          assert.ok(await commit.evaluate(el => el === document.activeElement),
            'commit control cannot receive keyboard focus');
          await page.keyboard.press('Enter');
        } else {
          await commit.click();
        }
        assert.equal(await gates.first().getAttribute('data-locked'), null,
          'valid typed commitment did not unlock ' + role);
        if (role === 'core2b') {
          const hintReveal = article.locator('details[data-g9-reveal]').filter({
            has: page.locator('summary:text-is("Hints after your first attempt")')
          }).first();
          assert.equal(await hintReveal.count(), 1, 'missing post-commit progressive hint disclosure');
          await hintReveal.locator('summary').click();
          assert.ok(await hintReveal.evaluate(el => el.open), 'post-commit hints should open');
          const ladder = hintReveal.locator('.g9-ladder');
          assert.equal(await ladder.locator('li[data-g9-rung]').count(), 1,
            'only the orientation rung should be revealed initially');
          const nextHint = ladder.locator('button[data-g9-next-rung]');
          await nextHint.focus();
          await page.keyboard.press('Enter');
          assert.equal(await ladder.locator('li[data-g9-rung]').count(), 2,
            'keyboard activation must progressively reveal the second rung');
          await nextHint.click();
          assert.equal(await ladder.locator('li[data-g9-rung]').count(), 3,
            'third rung should appear after a separate request');
          assert.ok(await nextHint.isDisabled(), 'third hint must be the last rung');
          assert.ok(!(await article.innerText()).includes(variant === 'boundary' ? 'n mod 4 != 1' : 'gcd(24,5)=1'),
            'progressive hint revealed the protected proof');
          assert.ok(await article.locator('a[href^="core1a.html#"]').count() > 0,
            'post-attempt concept-repair navigation is missing');
        }
        const solutionGate = role === 'core2b'
          ? article.locator('details[data-g9-reveal]').filter({
              has: page.locator('summary:text-is("Review and solution")'),
            }).first()
          : gates.first();
        assert.equal(await solutionGate.count(), 1, 'cannot identify complete solution disclosure');
        await solutionGate.locator('summary').click();
        assert.ok(await solutionGate.evaluate(element => element.open),
          role + ' solution disclosure cannot open after commitment');
        await page.emulateMedia({ media: 'print' });
        assert.ok((await article.count()) === 1, 'print media discarded learner question');
        if (role === 'core2b' && width === 390) {
          const pdfPath = path.join(evidenceDir, 'core2b-A4-after-commit.pdf');
          const bytes = await page.pdf({
            path: pdfPath, format: 'A4', printBackground: true, preferCSSPageSize: false,
          });
          assert.ok(bytes.subarray(0, 5).toString() === '%PDF-', 'no actual Chromium PDF');
          assert.ok(bytes.length > 2000, 'unexpectedly empty A4 print');
          result.print = { path: path.basename(pdfPath), bytes: bytes.length, format: 'A4',
            state: 'AFTER_LEARNER_COMMIT_AND_SOLUTION_OPEN', status: 'PENDING_PDF_STRUCTURE_CHECK' };
        }
        await page.emulateMedia({ media: 'screen' });
        if (role === 'core2b' && width === 390) {
          await page.reload();
          const resetArticle = page.locator('article[data-g9-role="CORE2B"]').first();
          assert.ok(await resetArticle.locator('details[data-requires-attempt][data-locked]').count() > 0,
            'Core2B refresh must not silently unlock a previous commitment');
          const freshText = await resetArticle.innerText();
          assert.ok(!freshText.includes(variant === 'boundary' ? 'n mod 4 != 1' : 'gcd(24,5)=1'),
            'Core2B refresh disclosed a previously viewed protected solution');
          result.refresh = 'CORE2B_FAILS_CLOSED_AND_REQUIRES_A_NEW_ATTEMPT';
        }
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
