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
// Geometry in the real rendered DOM, not merely document scrollWidth. The old
// #164 five-factor clipping was invisible to a root overflow-only assertion.
async function geometry(page) {
  return await page.evaluate(() => {
    const viewport = document.documentElement.clientWidth;
    const displayed = el => {
      for (let p = el; p && p.nodeType === 1; p = p.parentElement) {
        if (p.tagName === 'TEMPLATE' || getComputedStyle(p).display === 'none') return false;
      }
      return true;
    };
    const snapshot = el => {
      const r = el.getBoundingClientRect();
      const host = el.closest('figure');
      const h = host?.getBoundingClientRect();
      return {
        tag: el.tagName.toLowerCase(), role: el.getAttribute('data-g9-role'),
        name: (el.getAttribute('class') || '').toString().slice(0, 90),
        dataStage: el.getAttribute('data-g9-stage'),
        right: Math.round(r.right * 10) / 10,
        left: Math.round(r.left * 10) / 10,
        width: Math.round(r.width * 10) / 10,
        overhang: Math.max(0, Math.round((r.right - viewport) * 10) / 10),
        figureRight: h ? Math.round(h.right * 10) / 10 : null,
        figureOverhang: h ? Math.round((r.right - h.right) * 10) / 10 : null,
        cssOverflowX: getComputedStyle(el).overflowX,
        scrollWidth: el.scrollWidth, clientWidth: el.clientWidth,
      };
    };
    const elements = [...document.querySelectorAll('body *')].filter(displayed);
    const clipped = elements.filter(el => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.right > viewport + 1 && r.left < viewport;
    }).map(snapshot).sort((a,b) => b.overhang - a.overhang).slice(0, 15);
    const figures = [...document.querySelectorAll('figure[data-g9-figure]')]
      .filter(displayed).map(f => {
        const host = f.getBoundingClientRect();
        const svg = f.querySelector('svg');
        const shape = svg?.getBoundingClientRect();
        return {figureRight: host.right, figureWidth: host.width,
          svgRight: shape?.right ?? null, svgWidth: shape?.width ?? null,
          locallyClipped: shape ? shape.right > host.right + 2 : null};
      });
    return {viewport, documentScrollWidth: document.documentElement.scrollWidth,
      overflowing: document.documentElement.scrollWidth > viewport + 1,
      offending_elements: clipped, visible_figures: figures};
  });
}

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
    // Collect all four actual role geometries and candidate screenshots at every
    // width, including form hitbox/figure boundaries. These are automated only.
    const beforeGeometry = await geometry(page);
    assert.ok(!beforeGeometry.visible_figures.some(f => f.locallyClipped),
      'Core1B attempt-safe figure clips within its own wrapper at ' + width);
    const roleGeometry = {core1b: beforeGeometry};
    for (const role of ['core2a', 'core1a', 'core2b']) {
      const rolePage = await context.newPage();
      await rolePage.goto(pathToFileURL(path.join(site, role + '.html')).href);
      await rolePage.waitForLoadState('load');
      roleGeometry[role] = await geometry(rolePage);
      assert.ok(!roleGeometry[role].overflowing,
        role + ' document overflow at ' + width);
      assert.ok(!roleGeometry[role].visible_figures.some(f => f.locallyClipped),
        role + ' safe figure clipping at ' + width);
      await rolePage.screenshot({
        path: path.join(folder, role + '-' + width + '-before.png'), fullPage: true
      });
      // An initial stage alone cannot prove that later Core1A construction
      // or Core2B safe figure stages remain visible and uncropped.
      const chips = rolePage.locator('figure[data-g9-figure] [data-g9-stage-goto]');
      const count = await chips.count();
      if (role === 'core1a') {
        assert.equal(count, 3, 'Core1A three construction stages must remain navigable');
      }
      if (count) {
        roleGeometry[role].stages = [];
        for (let i = 0; i < count; i++) {
          await chips.nth(i).click();
          const staged = await geometry(rolePage);
          assert.ok(!staged.overflowing,
            role + ' stage ' + (i+1) + ' document overflow at ' + width);
          assert.ok(!staged.visible_figures.some(f => f.locallyClipped),
            role + ' stage ' + (i+1) + ' locally cropped at ' + width);
          assert.equal(await chips.nth(i).getAttribute('aria-pressed'), 'true',
            role + ' stage ' + (i+1) + ' did not activate');
          roleGeometry[role].stages.push({index: i + 1, status: 'PASS_AUTOMATED',
            figures: staged.visible_figures});
          if (width === 320 || width === 390) {
            await rolePage.screenshot({
              path: path.join(folder, role + '-' + width + '-stage-' + (i+1) + '.png'),
              fullPage: true
            });
          }
        }
      }
      await rolePage.close();
    }
    report.checks.push({width, status: 'PASS_AUTOMATED', geometry: roleGeometry,
      distinct_boundary_gate: true, downstream_fails_closed: width === 390 ? true : 'NOT_RUN'});
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
      // Print the two non-transfer pages as actual A4, without forcing answer unlock.
      for (const role of ['core2a', 'core1a']) {
        const printPage = await context.newPage();
        await printPage.goto(pathToFileURL(path.join(site, role + '.html')).href);
        await printPage.pdf({path: path.join(folder, role + '-A4-preview.pdf'),
          format: 'A4', printBackground: true});
        await printPage.close();
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
    await context.close();
  }
  // Narrow CSS viewport is a zoom stress proxy, NOT a manual 200% browser zoom verdict.
  const context = await browser.newContext({viewport: {width: 195, height: 450}});
  const page = await context.newPage();
  await page.goto(pathToFileURL(path.join(site, 'core1b.html')).href);
  const reflowGeometry = await geometry(page);
  report.zoom_200_proxy = {
    mode: '195_CSS_PX_WIDTH_PROXY_FOR_390_AT_200_PERCENT',
    horizontal_overflow: reflowGeometry.overflowing,
    geometry: reflowGeometry, status: 'AUTOMATED_ONLY_NOT_REAL_BROWSER_ZOOM',
  };
  await page.screenshot({path: path.join(folder, 'core1b-200pct-proxy.png'), fullPage: true});
  await context.close();
  fs.writeFileSync(path.join(folder, 'core1b-browser-receipt.json'),
    JSON.stringify(report, null, 2) + '\n');
  console.log('TRACK_A_HELD_CORE1B_BROWSER', JSON.stringify(report));
} finally {
  await browser.close();
}
