#!/usr/bin/env node
// Track A #173: held Core1B browser evidence. No AT/human or release signoff.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const site = path.resolve(process.argv[2] || '');
const folder = path.resolve(process.argv[3] || '');
const variant = process.argv[4] || 'five';
assert.ok(['five', 'boundary'].includes(variant));
assert.ok(fs.existsSync(path.join(site, 'core1b.html')), 'actual Core1B render required');
fs.mkdirSync(folder, {recursive: true});
const browser = await chromium.launch({headless: true});
const report = {variant, status: 'CANDIDATE_AUTOMATED_BROWSER_ONLY',
  widths: [320, 390, 768, 1280], checks: [], human_acceptance: 'NOT_RUN'};
try {
  for (const width of report.widths) {
    const context = await browser.newContext({
      viewport: {width, height: 900}, reducedMotion: 'reduce',
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(path.join(site, 'core1b.html')).href);
    await page.waitForLoadState('load');
    const main = page.locator('article[data-g9-role="CORE1B"]').first();
    assert.equal(await main.count(), 1, 'wrong role');
    assert.ok(await page.locator('figure[data-g9-stage="PRE_ATTEMPT"]').count() >= 1);
    const attempts = main.locator('[data-g9-attempt-box]');
    const gated = main.locator('details[data-requires-attempt]');
    assert.equal(await attempts.count(), 2, 'reconstruction and boundary need independent attempts');
    assert.equal(await gated.count(), 2, 'both disclosures need independent gates');
    assert.equal(await gated.filter({has: page.locator('summary')}).count(), 2);
    assert.ok((await main.innerText()).includes('Boundary test'));
    const measure = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      scroll: document.documentElement.scrollWidth,
    }));
    assert.ok(measure.scroll <= measure.viewport + 1,
      'Core1B page horizontal overflow ' + width + ' ' + JSON.stringify(measure));
    assert.ok((await gated.first().getAttribute('data-locked')) !== null);
    assert.ok((await gated.nth(1).getAttribute('data-locked')) !== null);
    const visibleBefore = await main.innerText();
    assert.ok(!visibleBefore.includes('No. Three checks are instances'),
      'protected prediction answer visible before attempt');
    assert.ok(!visibleBefore.includes('gcd(24,5)=1'));
    assert.ok(!visibleBefore.includes('n mod 4 != 1'));
    await page.screenshot({path: path.join(folder, 'core1b-' + width + '-before.png'),
      fullPage: true});

    if (width === 390) {
      await page.emulateMedia({media: 'print'});
      try {
        assert.ok(await gated.evaluateAll(nodes => nodes.every(
          el => getComputedStyle(el).display === 'none'
        )), 'locked reconstruction disclosures must not print');
        await page.pdf({path: path.join(folder, 'core1b-A4-before-commit.pdf'),
          format: 'A4', printBackground: true});
      } finally {
        await page.emulateMedia({media: 'screen'});
      }
    }

    const box = attempts.first();
    const field = box.locator('textarea[data-g9-attempt],input[data-g9-attempt]').first();
    const commit = box.locator('[data-g9-commit]').first();
    assert.equal(await field.count(), 1);
    await commit.click();
    assert.ok((await gated.first().getAttribute('data-locked')) !== null,
      'empty reconstruction commitment unlocked proof');
    await field.fill('No. Samples are not a universal proof. One of the consecutive factors is even, all three residues modulo 3 are covered, and coprimality proves divisibility by six for any t.');
    await commit.focus();
    await page.keyboard.press('Enter');
    assert.equal(await gated.first().getAttribute('data-locked'), null,
      'real reconstruction commitment must reveal self-check');
    assert.ok((await gated.nth(1).getAttribute('data-locked')) !== null,
      'main commitment leaked separate boundary answer');
    await gated.first().locator('summary').click();
    assert.ok(await gated.first().evaluate(el => el.open));
    assert.ok((await main.innerText()).includes('No. Three checks are instances'),
      'Core1B reconstruction closure missing after attempt');

    const boundary = attempts.nth(1);
    const boundaryField = boundary.locator(
      'textarea[data-g9-attempt],input[data-g9-attempt]').first();
    const boundaryCommit = boundary.locator('[data-g9-commit]').first();
    await boundaryCommit.click();
    assert.ok((await gated.nth(1).getAttribute('data-locked')) !== null,
      'empty boundary commitment unlocked answer');
    await boundaryField.fill('No: t=2 gives 2, which is not divisible by 6; a two-term product misses a guaranteed multiple of three.');
    await boundaryCommit.click();
    assert.equal(await gated.nth(1).getAttribute('data-locked'), null,
      'separate boundary attempt should reveal closure');
    await gated.nth(1).locator('summary').click();
    assert.ok(await gated.nth(1).evaluate(el => el.open));
    await page.screenshot({path: path.join(folder, 'core1b-' + width + '-after.png'),
      fullPage: true});
    if (width === 390) {
      await page.emulateMedia({media: 'print'});
      try {
        await page.pdf({path: path.join(folder, 'core1b-A4-after-commit.pdf'),
          format: 'A4', printBackground: true});
      } finally {
        await page.emulateMedia({media: 'screen'});
      }
      // Returning to Core2B must NOT inherit reconstructed/Core1B commitments.
      await page.goto(pathToFileURL(path.join(site, 'core2b.html')).href);
      assert.ok(await page.locator('article[data-g9-role="CORE2B"] details[data-requires-attempt][data-locked]').count() > 0,
        'Core1B commitment leaked downstream Core2B answer');
      await page.goto(pathToFileURL(path.join(site, 'core1b.html')).href);
      assert.equal(await page.locator('article[data-g9-role="CORE1B"] details[data-requires-attempt][data-locked]').count(), 2,
        'Core1B refresh must fail closed');
    }
    assert.deepEqual(errors, [], 'uncaught browser errors');
    report.checks.push({width, status: 'PASS_AUTOMATED', no_overflow: true,
      distinct_boundary_gate: true, downstream_fails_closed: width === 390 ? true : 'NOT_RUN'});
    await context.close();
  }
  // Narrow CSS viewport is a zoom stress proxy, NOT a manual 200% browser zoom verdict.
  const context = await browser.newContext({viewport: {width: 195, height: 450}});
  const page = await context.newPage();
  await page.goto(pathToFileURL(path.join(site, 'core1b.html')).href);
  report.zoom_200_proxy = {
    mode: '195_CSS_PX_WIDTH_PROXY_FOR_390_AT_200_PERCENT',
    horizontal_overflow: await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1),
    status: 'AUTOMATED_ONLY',
  };
  await page.screenshot({path: path.join(folder, 'core1b-200pct-proxy.png'), fullPage: true});
  await context.close();
  fs.writeFileSync(path.join(folder, 'core1b-browser-receipt.json'),
    JSON.stringify(report, null, 2) + '\n');
  console.log('TRACK_A_HELD_CORE1B_BROWSER', JSON.stringify(report));
} finally {
  await browser.close();
}
