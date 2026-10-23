import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import assert from 'node:assert';
import { execSync } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Locate playwright from NODE_PATH or global npm root
let chromium;
try {
  const pw = await import('playwright');
  chromium = pw.chromium;
} catch {
  let globalRoot = process.env.NODE_PATH;
  if (!globalRoot) {
    try {
      globalRoot = execSync('npm.cmd root -g', { encoding: 'utf8' }).trim();
    } catch {
      globalRoot = 'C:/Users/reall/AppData/Local/pdfhub-node22/node-v22.23.2-win-x64/node_modules';
    }
  }
  const req = createRequire(path.join(globalRoot, 'index.js'));
  chromium = req('playwright').chromium;
}

const htmlFilePath = path.resolve(__dirname, '../nlm-p1.html');
const shotsDir = path.resolve(__dirname, 'shots');
if (!fs.existsSync(shotsDir)) {
  fs.mkdirSync(shotsDir, { recursive: true });
}

const FORBIDDEN_WORDS_REGEX = /\b(source|provenance|adaptation|adapted|transfer|assisted|diagnostic|custody|falsifier)\b|PHYS-/i;

async function assertNoForbiddenWords(page, screenName) {
  const visibleText = await page.evaluate(() => document.body.innerText);
  const match = visibleText.match(FORBIDDEN_WORDS_REGEX);
  assert.strictEqual(
    match,
    null,
    `Forbidden review word or PHYS- ID "${match ? match[0] : ''}" found on visible screen "${screenName}"`
  );
}

async function assertNoHorizontalScroll(page, screenName) {
  const hasScroll = await page.evaluate(() => {
    return document.documentElement.scrollWidth > document.documentElement.clientWidth;
  });
  assert.strictEqual(
    hasScroll,
    false,
    `Horizontal scroll detected on 390px viewport during screen "${screenName}"`
  );
}

async function runTests() {
  console.log('--- Starting Grade 9 P1: Kid Page test suite ---');
  let passed = 0;
  let failed = 0;

  function recordPass(testName) {
    passed++;
    console.log(`PASS [${passed}]: ${testName}`);
  }

  function recordFail(testName, error) {
    failed++;
    console.error(`FAIL [${failed}]: ${testName}`, error);
  }

  // 1. Static and Cue Checks on PHYS-NLM-002
  try {
    const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
    const bankMatch = htmlContent.match(/<script type="application\/json" id="nlm-bank">([\s\S]*?)<\/script>/);
    assert.ok(bankMatch, 'Inline bank JSON payload must exist');
    const bank = JSON.parse(bankMatch[1]);
    const q002 = bank.find(q => q.question_id === 'PHYS-NLM-002');
    assert.ok(q002, 'PHYS-NLM-002 must exist in embedded bank');

    // 002 fix criteria
    assert.ok(
      q002.stem.toLowerCase().includes('light (massless)'),
      '002 stem must state the strap is light (massless)'
    );

    const stem = q002.stem;
    const options = q002.options;
    assert.strictEqual(Object.keys(options).length, 4);

    // Forces with magnitude and direction where physics fixes them
    assert.ok(options.A.includes('40 N') && options.A.includes('left') && options.A.includes('right'));
    assert.ok(options.B.includes('40 N') && options.B.includes('right') && options.B.includes('left'));
    assert.ok(options.C.includes('40 N') && options.C.includes('left') && options.C.includes('right'));
    assert.ok(options.D.includes('40 N') && options.D.includes('right') && options.D.includes('downward'));

    // Check cue checks:
    // a) Number/unit count
    const numCounts = {};
    for (const [k, v] of Object.entries(options)) {
      const matches = v.match(/\b\d+\s*[A-Za-z]+\b/g) || [];
      numCounts[k] = matches.length;
    }
    // A, B, C tie at 2. No option uniquely picked by having the max count.
    const maxNumCount = Math.max(...Object.values(numCounts));
    const maxNumOptions = Object.keys(numCounts).filter(k => numCounts[k] === maxNumCount);
    assert.ok(maxNumOptions.length > 1, 'Key is not uniquely picked by counting numbers/units');
    assert.ok(maxNumOptions.includes('A') && maxNumOptions.includes('B') && maxNumOptions.includes('C'));

    // b) Longest option
    const wordCounts = {};
    for (const [k, v] of Object.entries(options)) {
      wordCounts[k] = v.trim().split(/\s+/).length;
    }
    const maxWords = Math.max(...Object.values(wordCounts));
    const longestOptions = Object.keys(wordCounts).filter(k => wordCounts[k] === maxWords);
    assert.ok(longestOptions.length > 1, 'Key is not uniquely picked by being the longest');
    assert.ok(longestOptions.includes('A') && longestOptions.includes('B') && longestOptions.includes('C'));

    // c) Repeating stem words
    const tokens = s => new Set((s.match(/\p{L}+(?:['’]\p{L}+)*/gu) || []).map(x => x.toLowerCase()));
    const wordset = {};
    for (const [id, s] of Object.entries(options)) wordset[id] = tokens(s);
    const restNonKey = new Set(Object.entries(wordset).filter(([k]) => k !== 'A').flatMap(([, set]) => [...set]));
    const stemTokens = tokens(stem);
    const uniqueStemOverlapWithKey = [...stemTokens].filter(x => wordset.A.has(x) && !restNonKey.has(x));
    assert.strictEqual(
      uniqueStemOverlapWithKey.length,
      0,
      'Key A does not uniquely repeat any words from the stem'
    );

    recordPass('002 cue checks: equal specificity, no cue leak by units, length or word repeat');
  } catch (err) {
    recordFail('002 cue checks', err);
  }

  // Launch browser with system Chrome
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const fileUrl = pathToFileURL(htmlFilePath).href;

  const consoleErrors = [];

  // Helper to setup page with error monitoring
  async function createMonitoredPage(viewport = { width: 1280, height: 800 }) {
    const context = await browser.newContext({ viewport });
    const page = await context.newPage();
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    page.on('pageerror', err => {
      consoleErrors.push(err.message);
    });
    return { context, page };
  }

  // 2. Full Flow: Path miss-001 -> PHYS-NLM-013, Hints, Retry, Full Solution, Results, Save, Reset
  try {
    const { context, page } = await createMonitoredPage();
    await page.goto(fileUrl);

    // Screen 1: Start
    await assertNoForbiddenWords(page, 'Start Screen');
    await page.screenshot({ path: path.join(shotsDir, '01-start-screen.png'), fullPage: true });
    assert.strictEqual(await page.locator('#start-btn').isVisible(), true);
    await page.click('#start-btn');

    // Screen 2: Baseline Q1 (PHYS-NLM-001) - Miss it (choose B)
    await assertNoForbiddenWords(page, 'Baseline Q1');
    await page.screenshot({ path: path.join(shotsDir, '02-baseline-q1.png'), fullPage: true });
    await page.click('label[data-choice="B"]');
    await page.fill('#why-input', 'Downward travel means downward net force');
    await page.selectOption('#confidence-select', 'sure');
    await page.click('#baseline-next-btn');

    // Screen 3: Baseline Q2 (PHYS-NLM-002) - Correct (choose A)
    await assertNoForbiddenWords(page, 'Baseline Q2');
    await page.screenshot({ path: path.join(shotsDir, '03-baseline-q2.png'), fullPage: true });
    await page.click('label[data-choice="A"]');
    await page.selectOption('#confidence-select', 'somewhat');
    await page.click('#baseline-next-btn');

    // Screen 4: Baseline Q3 (PHYS-NLM-012) - Correct (choose A)
    await assertNoForbiddenWords(page, 'Baseline Q3');
    await page.screenshot({ path: path.join(shotsDir, '04-baseline-q3.png'), fullPage: true });
    await page.click('label[data-choice="A"]');
    await page.selectOption('#confidence-select', 'sure');
    await page.click('#baseline-next-btn');

    // Screen 5: Supported Question (missed 001 -> must be PHYS-NLM-013)
    await assertNoForbiddenWords(page, 'Supported Question Initial');
    await page.screenshot({ path: path.join(shotsDir, '05-supported-initial.png'), fullPage: true });
    const suppStem = await page.locator('.question-stem').textContent();
    assert.ok(
      suppStem.includes('momentum is conserved because it is one object'),
      'Missed 001 must route to PHYS-NLM-013'
    );

    // Test staged help: Hint 1
    assert.strictEqual(await page.locator('#hint-btn').isVisible(), true);
    await page.click('#hint-btn');
    await assertNoForbiddenWords(page, 'Hint 1 Prompt');
    await page.screenshot({ path: path.join(shotsDir, '06-supported-hint1-prompt.png'), fullPage: true });
    assert.strictEqual(await page.locator('#hint-tier-1').isVisible(), true);
    assert.strictEqual(await page.locator('#reveal-hint-1-btn').isVisible(), true);
    assert.strictEqual(await page.locator('#hint-tier-1 .hint-reveal-box').count(), 0);

    // Reveal Hint 1
    await page.click('#reveal-hint-1-btn');
    await assertNoForbiddenWords(page, 'Hint 1 Revealed');
    await page.screenshot({ path: path.join(shotsDir, '07-supported-hint1-reveal.png'), fullPage: true });
    assert.strictEqual(await page.locator('#hint-tier-1 .hint-reveal-box').isVisible(), true);
    const h1RevealText = await page.locator('#hint-tier-1 .hint-reveal-box').textContent();
    assert.ok(h1RevealText.includes('Conservation is a property of a specified isolated system'));

    // Open Hint 2
    await page.click('#hint-btn');
    await assertNoForbiddenWords(page, 'Hint 2 Prompt');
    assert.strictEqual(await page.locator('#hint-tier-2').isVisible(), true);
    await page.click('#reveal-hint-2-btn');
    assert.strictEqual(await page.locator('#hint-tier-2 .hint-reveal-box').isVisible(), true);

    // Open Hint 3
    await page.click('#hint-btn');
    await assertNoForbiddenWords(page, 'Hint 3 Prompt');
    assert.strictEqual(await page.locator('#hint-tier-3').isVisible(), true);
    await page.click('#reveal-hint-3-btn');
    assert.strictEqual(await page.locator('#hint-tier-3 .hint-reveal-box').isVisible(), true);
    await page.screenshot({ path: path.join(shotsDir, '08-supported-hints-all.png'), fullPage: true });

    // Submit a wrong answer first (choose B) to test retry
    await page.click('label[data-choice="B"]');
    await page.click('#check-answer-btn');
    await assertNoForbiddenWords(page, 'Supported Wrong Attempt');
    await page.screenshot({ path: path.join(shotsDir, '09-supported-first-wrong.png'), fullPage: true });
    assert.strictEqual(await page.locator('#retry-btn').isVisible(), true);

    // Retry once
    await page.click('#retry-btn');
    await assertNoForbiddenWords(page, 'Supported Retry Active');
    // Select correct answer on retry (choose A)
    await page.click('label[data-choice="A"]');
    await page.click('#check-retry-btn');

    // Show full solution
    assert.strictEqual(await page.locator('#show-solution-btn').isVisible(), true);
    await page.click('#show-solution-btn');
    await assertNoForbiddenWords(page, 'Supported Full Solution');
    await page.screenshot({ path: path.join(shotsDir, '10-supported-solution.png'), fullPage: true });
    assert.strictEqual(await page.locator('#solution-card').isVisible(), true);

    // Navigate to Results Screen
    await page.click('#see-results-btn');
    await assertNoForbiddenWords(page, 'Results Screen');
    await page.screenshot({ path: path.join(shotsDir, '11-results-screen.png'), fullPage: true });

    // Verify Results Screen contents
    const resultsText = await page.locator('.card').innerText();
    assert.ok(resultsText.includes('Warm-up Question 1'));
    assert.ok(resultsText.includes('Warm-up Question 2'));
    assert.ok(resultsText.includes('Warm-up Question 3'));
    assert.ok(resultsText.includes('Practice Question'));
    assert.ok(resultsText.includes('Hints opened: 3 of 3'));

    // Test Save my answers download
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('#save-answers-btn')
    ]);
    const stream = await download.createReadStream();
    const chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const sessionJson = JSON.parse(Buffer.concat(chunks).toString('utf8'));

    // Assert JSON fields per brief
    assert.strictEqual(sessionJson.page_version, '1.0.0');
    assert.ok(sessionJson.saved_at);
    assert.strictEqual(sessionJson.baseline_questions.length, 3);
    assert.strictEqual(sessionJson.baseline_questions[0].question_id, 'PHYS-NLM-001');
    assert.strictEqual(sessionJson.baseline_questions[0].choice, 'B');
    assert.strictEqual(sessionJson.baseline_questions[0].why_text, 'Downward travel means downward net force');
    assert.strictEqual(sessionJson.baseline_questions[0].confidence, 'sure');
    assert.strictEqual(sessionJson.baseline_questions[1].question_id, 'PHYS-NLM-002');
    assert.strictEqual(sessionJson.baseline_questions[2].question_id, 'PHYS-NLM-012');

    assert.strictEqual(sessionJson.supported_question.question_id, 'PHYS-NLM-013');
    assert.strictEqual(sessionJson.supported_question.choice, 'A');
    assert.strictEqual(sessionJson.supported_question.correct, true);
    assert.strictEqual(sessionJson.supported_question.attempts, 2);
    assert.strictEqual(sessionJson.supported_question.hints_opened, 3);
    assert.deepStrictEqual(sessionJson.supported_question.reveal_used, [1, 2, 3]);
    assert.strictEqual(sessionJson.supported_question.solution_viewed, true);

    // Test Start again (clean state)
    await page.click('#start-again-btn');
    await assertNoForbiddenWords(page, 'After Reset');
    assert.strictEqual(await page.locator('#start-btn').isVisible(), true);

    await context.close();
    recordPass('Full flow: miss-001 -> PHYS-NLM-013, hints in order, retry, solution, results, save JSON, start again');
  } catch (err) {
    recordFail('Full flow (miss-001)', err);
  }

  // 3. Path miss-002 -> PHYS-NLM-032
  try {
    const { context, page } = await createMonitoredPage();
    await page.goto(fileUrl);
    await page.click('#start-btn');

    // Q1: Correct (A)
    await page.click('label[data-choice="A"]');
    await page.click('#baseline-next-btn');

    // Q2: Missed (choose B)
    await page.click('label[data-choice="B"]');
    await page.click('#baseline-next-btn');

    // Q3: Correct (A)
    await page.click('label[data-choice="A"]');
    await page.click('#baseline-next-btn');

    // Should reach PHYS-NLM-032
    await assertNoForbiddenWords(page, 'Path miss-002');
    const stem = await page.locator('.question-stem').textContent();
    assert.ok(
      stem.includes('tiny spacecraft docking plates press against each other'),
      'Missed 002 must reach PHYS-NLM-032'
    );
    await context.close();
    recordPass('Routing check: miss-002 reaches PHYS-NLM-032');
  } catch (err) {
    recordFail('Routing check miss-002', err);
  }

  // 4. Path miss-012 -> PHYS-NLM-006
  try {
    const { context, page } = await createMonitoredPage();
    await page.goto(fileUrl);
    await page.click('#start-btn');

    // Q1: Correct (A)
    await page.click('label[data-choice="A"]');
    await page.click('#baseline-next-btn');

    // Q2: Correct (A)
    await page.click('label[data-choice="A"]');
    await page.click('#baseline-next-btn');

    // Q3: Missed (choose B)
    await page.click('label[data-choice="B"]');
    await page.click('#baseline-next-btn');

    // Should reach PHYS-NLM-006
    await assertNoForbiddenWords(page, 'Path miss-012');
    const stem = await page.locator('.question-stem').textContent();
    assert.ok(
      stem.includes('space probe coasts at a fixed speed in a straight line'),
      'Missed 012 must reach PHYS-NLM-006'
    );
    await context.close();
    recordPass('Routing check: miss-012 reaches PHYS-NLM-006');
  } catch (err) {
    recordFail('Routing check miss-012', err);
  }

  // 5. Path all-correct -> PHYS-NLM-021
  try {
    const { context, page } = await createMonitoredPage();
    await page.goto(fileUrl);
    await page.click('#start-btn');

    // Q1: Correct (A)
    await page.click('label[data-choice="A"]');
    await page.click('#baseline-next-btn');

    // Q2: Correct (A)
    await page.click('label[data-choice="A"]');
    await page.click('#baseline-next-btn');

    // Q3: Correct (A)
    await page.click('label[data-choice="A"]');
    await page.click('#baseline-next-btn');

    // Should reach PHYS-NLM-021
    await assertNoForbiddenWords(page, 'Path all-correct');
    const stem = await page.locator('.question-stem').textContent();
    assert.ok(
      stem.includes('4.0 kg sample box lies on a 30° rough slope'),
      'All-correct must reach PHYS-NLM-021'
    );
    await context.close();
    recordPass('Routing check: all-correct reaches PHYS-NLM-021');
  } catch (err) {
    recordFail('Routing check all-correct', err);
  }

  // 6. Mobile 390px Viewport and Tap Targets Check
  try {
    const { context, page } = await createMonitoredPage({ width: 390, height: 844 });
    await page.goto(fileUrl);

    // Screen 1: Start on mobile
    await assertNoHorizontalScroll(page, 'Start Mobile');
    await page.screenshot({ path: path.join(shotsDir, '12-mobile-390px.png'), fullPage: true });

    // Click start
    await page.click('#start-btn');
    await assertNoHorizontalScroll(page, 'Baseline Q1 Mobile');

    // Check tap target sizes
    const labelBox = await page.locator('label.option-label').first().boundingBox();
    assert.ok(labelBox.height >= 48, `Tap target height must be >= 48px, got ${labelBox.height}`);

    const btnBox = await page.locator('#baseline-next-btn').boundingBox();
    assert.ok(btnBox.height >= 48, `Button height must be >= 48px, got ${btnBox.height}`);

    await context.close();
    recordPass('Mobile check: 390px viewport has zero horizontal scroll and large >=48px tap targets');
  } catch (err) {
    recordFail('Mobile check', err);
  }

  // 7. Console errors assertion
  try {
    assert.strictEqual(
      consoleErrors.length,
      0,
      `Zero console errors required, found: ${JSON.stringify(consoleErrors)}`
    );
    recordPass('Console errors: zero console errors across all interactions');
  } catch (err) {
    recordFail('Console errors check', err);
  }

  await browser.close();

  console.log(`\n--- Test Suite Summary: ${passed} passed, ${failed} failed ---`);
  if (failed > 0) {
    process.exit(1);
  }
}

runTests().catch(err => {
  console.error('Unhandled test failure:', err);
  process.exit(1);
});
