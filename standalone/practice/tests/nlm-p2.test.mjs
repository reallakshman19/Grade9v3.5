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

const htmlFilePath = path.resolve(__dirname, '../nlm-p2-session.html');
const shotsDir = path.resolve(__dirname, 'shots-p2');
if (!fs.existsSync(shotsDir)) {
  fs.mkdirSync(shotsDir, { recursive: true });
}

const FORBIDDEN_WORDS_REGEX = /\b(source|provenance|adaptation|adapted|transfer|assisted|diagnostic|custody|falsifier|review)\b|PHYS-/i;

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
  console.log('--- Starting Grade 9 P2: One Learning Session test suite ---');
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

  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const fileUrl = pathToFileURL(htmlFilePath).href;
  const consoleErrors = [];

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

  let savedSessionFilePath = null;

  // TEST 1: Full flow with help: forces gap, diagram revision, hints, retry, solution, reconstruction, fresh problem with guided repair, save session, and continue from last time
  try {
    const { context, page } = await createMonitoredPage();
    await page.goto(fileUrl);

    // Screen 0: Start Screen
    await assertNoForbiddenWords(page, 'Start Screen');
    await page.screenshot({ path: path.join(shotsDir, '01-start-screen.png'), fullPage: true });
    assert.strictEqual(await page.locator('#start-btn').isVisible(), true);
    await page.click('#start-btn');

    // Screen 1: Warm-ups (Block 1)
    await assertNoForbiddenWords(page, 'Warm-ups Screen');
    await page.screenshot({ path: path.join(shotsDir, '02-warmups-screen.png'), fullPage: true });

    // Verify NO feedback before all 3 warmups are saved
    assert.strictEqual(await page.locator('.alert').count(), 0);
    assert.strictEqual(await page.locator('.badge').count(), 0);

    // Q1: Choose B (miss - forces gap)
    await page.click('label[data-warmup="1"][data-choice="B"]');
    await page.fill('#warmup-1-why', 'B is bigger mass so it resists push');

    // Q2: Choose A (correct)
    await page.click('label[data-warmup="2"][data-choice="A"]');
    await page.fill('#warmup-2-why', 'Act on different bodies so they do not cancel');

    // Q3: Choose A (correct)
    await page.click('label[data-warmup="3"][data-choice="A"]');
    await page.fill('#warmup-3-why', 'a = F / m = 4 / 2 = 2');

    // Still no feedback
    assert.strictEqual(await page.locator('.alert').count(), 0);

    // Submit warmups
    await page.click('#warmups-submit-btn');

    // Screen 2: Teaching Passage (Block 2)
    // Missed Q1 -> forces gap only
    await assertNoForbiddenWords(page, 'Teaching Passage (Forces Gap)');
    await page.screenshot({ path: path.join(shotsDir, '03-teaching-forces-gap.png'), fullPage: true });
    assert.strictEqual(await page.locator('#forces-passage').isVisible(), true);
    assert.strictEqual(await page.locator('#arithmetic-passage').count(), 0);
    assert.strictEqual(await page.locator('#ready-note').count(), 0);

    // Write learner interaction
    await page.fill('#learner-interaction-text', 'When hand pushes block, hand pushes block right and block pushes hand left on different bodies');
    await page.click('#step2-next-btn');

    // Screen 3: Force Diagrams (Block 3)
    await assertNoForbiddenWords(page, 'Force Diagrams Initial');
    await page.screenshot({ path: path.join(shotsDir, '04-diagrams-initial.png'), fullPage: true });

    // Block A: pick a-on-b (wrong receiver!)
    await page.check('input[data-diagram="A"][value="a-on-b"]');
    await page.click('#check-diagram-a-btn');
    await assertNoForbiddenWords(page, 'Diagram A Receiver Error');
    await page.screenshot({ path: path.join(shotsDir, '05-diagrams-a-receiver-error.png'), fullPage: true });

    // Assert receiver question and highlight
    assert.strictEqual(await page.locator('#receiver-feedback-a').isVisible(), true);
    assert.ok(await page.locator('#receiver-feedback-a').innerText().then(t => t.includes('Which body receives this force?')));
    assert.strictEqual(await page.locator('#highlight-receiver-b').isVisible(), true);

    // Revise Block A diagram
    await page.uncheck('input[data-diagram="A"][value="a-on-b"]');
    await page.check('input[data-diagram="A"][value="hand-on-a"]');
    await page.check('input[data-diagram="A"][value="b-on-a"]');
    await page.click('#check-diagram-a-btn');
    assert.strictEqual(await page.locator('#receiver-feedback-a').isVisible(), false);

    // Block B diagram
    await page.check('input[data-diagram="B"][value="a-on-b"]');
    await page.click('#check-diagram-b-btn');

    // Circled boundary explanation
    await page.fill('#internal-forces-reason', 'Contact forces are internal equal and opposite, so they cancel to zero in system sum');
    await page.click('#step3-next-btn');

    // Screen 4: Main Problem (Block 4)
    await assertNoForbiddenWords(page, 'Main Problem Initial');
    await page.screenshot({ path: path.join(shotsDir, '06-main-problem-initial.png'), fullPage: true });

    // Hints in order
    assert.strictEqual(await page.locator('#hint-tier-1').count(), 0);
    await page.click('#hint-btn');
    assert.strictEqual(await page.locator('#hint-tier-1').isVisible(), true);
    assert.strictEqual(await page.locator('#hint-tier-2').count(), 0);

    await page.click('#hint-btn');
    assert.strictEqual(await page.locator('#hint-tier-2').isVisible(), true);
    assert.strictEqual(await page.locator('#hint-tier-3').count(), 0);

    await page.click('#hint-btn');
    assert.strictEqual(await page.locator('#hint-tier-3').isVisible(), true);
    await page.screenshot({ path: path.join(shotsDir, '07-main-problem-hints.png'), fullPage: true });

    // Enter wrong values first to test retry
    await page.fill('#main-accel-val', '5');
    await page.fill('#main-contact-val', '10');
    await page.click('#check-main-btn');

    assert.strictEqual(await page.locator('#retry-main-btn').isVisible(), true);
    await page.screenshot({ path: path.join(shotsDir, '08-main-problem-retry.png'), fullPage: true });

    // Retry once with wrong values to unlock full solution
    await page.click('#retry-main-btn');
    await page.fill('#main-accel-val', '4');
    await page.fill('#main-contact-val', '8');
    await page.click('#check-retry-btn');

    assert.strictEqual(await page.locator('#show-solution-btn').isVisible(), true);
    await page.click('#show-solution-btn');
    assert.strictEqual(await page.locator('#solution-card').isVisible(), true);
    await page.screenshot({ path: path.join(shotsDir, '09-main-problem-solution.png'), fullPage: true });

    // Verify numbers in solution
    const solText = await page.locator('#solution-card').innerText();
    assert.ok(solText.includes('2 m/s²'));
    assert.ok(solText.includes('6 N'));

    // Move to Screen 5: Reconstruction (Block 5)
    await page.click('#step4-next-btn');
    await assertNoForbiddenWords(page, 'Reconstruction (Solution Hidden)');
    await page.screenshot({ path: path.join(shotsDir, '10-reconstruction-solution-hidden.png'), fullPage: true });

    // CRITICAL: Solution must be HIDDEN!
    assert.strictEqual(await page.locator('#solution-card').count(), 0);

    // Focused follow-up
    await page.click('#focused-followup-btn');
    assert.strictEqual(await page.locator('#focused-followup-box').isVisible(), true);

    // Reopen explanation guide (marks block 5 as assisted / with help)
    await page.click('#reopen-explanation-btn');
    assert.strictEqual(await page.locator('#reopened-explanation-box').isVisible(), true);

    await page.fill('#recon-why-6n', '4 N accelerates A (2 kg * 2 m/s^2), so 10 - 4 = 6 N is transmitted to B');
    await page.fill('#recon-why-no-cancel', 'Because B on A acts on A, but A on B acts on B, so they never act on the same body');
    await page.click('#step5-next-btn');

    // Screen 6: Fresh Problem (Block 6)
    await assertNoForbiddenWords(page, 'Fresh Problem Initial');
    await page.screenshot({ path: path.join(shotsDir, '11-fresh-problem-initial.png'), fullPage: true });

    // Fill first attempt
    await page.click('label[data-fresh-pred="smaller"]');
    await page.fill('#fresh-pred-why', 'Push is now on larger block B');
    await page.check('input[data-fresh-b="hand-on-b"]');
    await page.check('input[data-fresh-b="a-on-b"]');
    await page.check('input[data-fresh-a="b-on-a"]');

    // Intentionally enter contact force 6 N on first attempt to test guided repair and preservation of first answer
    await page.fill('#fresh-accel-val', '2');
    await page.selectOption('#fresh-accel-dir', 'left');
    await page.fill('#fresh-accel-why', 'a = 10 / (2+3) = 2 left');
    await page.fill('#fresh-contact-val', '6');
    await page.fill('#fresh-contact-why', 'Predicted 6 N');
    await page.fill('#fresh-equal-why', 'Newton third law pairs are always equal in magnitude');

    // Submit first answer BEFORE feedback
    await page.click('#fresh-submit-btn');

    // Guided repair appears
    assert.strictEqual(await page.locator('#guided-repair-card').isVisible(), true);
    await assertNoForbiddenWords(page, 'Fresh Problem Guided Repair');
    await page.screenshot({ path: path.join(shotsDir, '12-fresh-problem-guided-repair.png'), fullPage: true });

    // Complete guided repair
    await page.click('#guided-repair-btn');
    await page.click('#step6-next-btn');

    // Screen 7: Summary (Block 7)
    await assertNoForbiddenWords(page, 'Summary Screen');
    await page.screenshot({ path: path.join(shotsDir, '13-summary-screen.png'), fullPage: true });

    // Verify skills reflecting with-help path
    const receiverSkill = await page.locator('#skill-names_receivers .skill-badge').innerText();
    assert.strictEqual(receiverSkill.toLowerCase(), 'with help');

    const freshSkill = await page.locator('#skill-changed_problem .skill-badge').innerText();
    assert.strictEqual(freshSkill.toLowerCase(), 'with help');

    await page.fill('#summary-clearer', 'Equal and opposite forces act on different bodies');
    await page.fill('#summary-hard', 'Remembering which block gets isolated when push direction changes');

    // Test Save Session JSON download
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('#save-session-btn')
    ]);
    const stream = await download.createReadStream();
    const chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const sessionJson = JSON.parse(Buffer.concat(chunks).toString('utf8'));

    // Verify JSON contents per brief
    assert.strictEqual(sessionJson.page_version, '2.0.0');
    assert.ok(sessionJson.saved_at);
    assert.strictEqual(sessionJson.baseline_warmups.q1.choice, 'B');
    assert.strictEqual(sessionJson.teaching_passage.gap_identified, 'forces');
    assert.ok(sessionJson.diagrams.diagram_A.first_attempt.includes('a-on-b'));
    assert.ok(sessionJson.diagrams.diagram_A.revised_attempt.includes('hand-on-a'));
    assert.strictEqual(sessionJson.main_problem.hints_opened.length, 3);
    assert.strictEqual(sessionJson.main_problem.solution_opened, true);
    assert.strictEqual(sessionJson.reconstruction.assisted, true);

    // CRITICAL: First answer in fresh problem must be unchanged even after guided repair!
    assert.strictEqual(sessionJson.fresh_problem.first_attempt.contactVal, '6');
    assert.strictEqual(sessionJson.fresh_problem.first_attempt.accelVal, '2');
    assert.strictEqual(sessionJson.fresh_problem.first_attempt.accelDir, 'left');
    assert.strictEqual(sessionJson.fresh_problem.guided_repair_completed, true);
    assert.ok(sessionJson.remaining_gap);
    assert.ok(sessionJson.suggested_opening_check);

    // Save JSON to disk for Continue from last time test
    savedSessionFilePath = path.join(shotsDir, 'test-saved-session.json');
    fs.writeFileSync(savedSessionFilePath, JSON.stringify(sessionJson, null, 2), 'utf8');

    // Test "Continue from last time" on Start Screen
    await page.goto(fileUrl);
    await assertNoForbiddenWords(page, 'Start Screen for Resume');

    // Upload saved session file
    await page.setInputFiles('#load-session-file', savedSessionFilePath);

    assert.strictEqual(await page.locator('#resumed-info-card').isVisible(), true);
    const resumedGap = await page.locator('#resumed-gap').innerText();
    const resumedCheck = await page.locator('#resumed-check').innerText();
    assert.strictEqual(resumedGap, sessionJson.remaining_gap);
    assert.strictEqual(resumedCheck, sessionJson.suggested_opening_check);
    await page.screenshot({ path: path.join(shotsDir, '14-continue-from-last-time.png'), fullPage: true });

    await context.close();
    recordPass('Full flow (with help path): diagram error highlight & revision, hints, retry, solution, hidden solution, first answer preserved after repair, summary labels, save JSON, continue from last time');
  } catch (err) {
    recordFail('Full flow (with help path)', err);
  }

  // TEST 2: All-independent path: all warmups correct -> ready note -> diagrams correct first try -> main correct first try -> fresh problem correct first try -> all 5 skills independent
  try {
    const { context, page } = await createMonitoredPage();
    await page.goto(fileUrl);
    await page.click('#start-btn');

    // Warm-ups: all correct
    await page.click('label[data-warmup="1"][data-choice="C"]');
    await page.click('label[data-warmup="2"][data-choice="A"]');
    await page.click('label[data-warmup="3"][data-choice="A"]');
    await page.click('#warmups-submit-btn');

    // Step 2: "You're ready" note
    await assertNoForbiddenWords(page, 'Teaching (All Correct)');
    assert.strictEqual(await page.locator('#ready-note').isVisible(), true);
    assert.strictEqual(await page.locator('#forces-passage').count(), 0);
    assert.strictEqual(await page.locator('#arithmetic-passage').count(), 0);
    await page.fill('#learner-interaction-text', 'Two skaters pushing each other equal and opposite on each other');
    await page.click('#step2-next-btn');

    // Step 3: Force diagrams correct on first try
    await page.check('input[data-diagram="A"][value="hand-on-a"]');
    await page.check('input[data-diagram="A"][value="b-on-a"]');
    await page.click('#check-diagram-a-btn');
    assert.strictEqual(await page.locator('#receiver-feedback-a').isVisible(), false);

    await page.check('input[data-diagram="B"][value="a-on-b"]');
    await page.click('#check-diagram-b-btn');
    assert.strictEqual(await page.locator('#receiver-feedback-b').isVisible(), false);

    await page.fill('#internal-forces-reason', 'They are internal and cancel within system boundary');
    await page.click('#step3-next-btn');

    // Step 4: Main problem solved on first try without hints or retry
    await page.fill('#main-accel-val', '2');
    await page.selectOption('#main-accel-dir', 'right');
    await page.fill('#main-contact-val', '6');
    await page.click('#check-main-btn');

    assert.strictEqual(await page.locator('.alert-success').isVisible(), true);
    assert.strictEqual(await page.locator('#solution-card').count(), 0);
    await page.click('#step4-next-btn');

    // Step 5: Reconstruction unaided
    await page.fill('#recon-why-6n', '4 N accelerates A, 6 N transmits to B');
    await page.fill('#recon-why-no-cancel', 'Act on different bodies');
    await page.click('#step5-next-btn');

    // Step 6: Fresh problem solved correctly on first try
    await page.click('label[data-fresh-pred="smaller"]');
    await page.check('input[data-fresh-b="hand-on-b"]');
    await page.check('input[data-fresh-b="a-on-b"]');
    await page.check('input[data-fresh-a="b-on-a"]');
    await page.fill('#fresh-accel-val', '2');
    await page.selectOption('#fresh-accel-dir', 'left');
    await page.fill('#fresh-contact-val', '4');
    await page.fill('#fresh-equal-why', 'Reciprocal forces are equal and opposite by Newton third law');
    await page.click('#fresh-submit-btn');

    assert.strictEqual(await page.locator('.alert-success').isVisible(), true);
    assert.strictEqual(await page.locator('#guided-repair-card').count(), 0);
    await page.click('#step6-next-btn');

    // Step 7: Summary - all skills should be independent
    await assertNoForbiddenWords(page, 'Summary All-Independent');
    const skills = await page.locator('.skill-badge').allInnerTexts();
    assert.strictEqual(skills.length, 5);
    for (const s of skills) {
      assert.strictEqual(s.trim().toLowerCase(), 'independent', `Skill expected independent, got: ${s}`);
    }

    await context.close();
    recordPass('All-independent path: all warmups correct -> ready note -> diagrams first try -> main first try -> fresh first try -> all 5 skills independent');
  } catch (err) {
    recordFail('All-independent path', err);
  }

  // TEST 3: Warm-up routing matrix: arithmetic gap & both gaps
  try {
    const { context, page } = await createMonitoredPage();

    // 3A: Arithmetic gap only (Warmup 1 correct C, Warmup 2 correct A, Warmup 3 wrong B)
    await page.goto(fileUrl);
    await page.click('#start-btn');
    await page.click('label[data-warmup="1"][data-choice="C"]');
    await page.click('label[data-warmup="2"][data-choice="A"]');
    await page.click('label[data-warmup="3"][data-choice="B"]'); // wrong
    await page.click('#warmups-submit-btn');

    assert.strictEqual(await page.locator('#arithmetic-passage').isVisible(), true);
    assert.strictEqual(await page.locator('#forces-passage').count(), 0);
    assert.strictEqual(await page.locator('#ready-note').count(), 0);

    // 3B: Both gaps (Warmup 1 wrong A, Warmup 2 correct A, Warmup 3 wrong C)
    await page.goto(fileUrl);
    await page.click('#start-btn');
    await page.click('label[data-warmup="1"][data-choice="A"]'); // wrong
    await page.click('label[data-warmup="2"][data-choice="A"]');
    await page.click('label[data-warmup="3"][data-choice="C"]'); // wrong
    await page.click('#warmups-submit-btn');

    assert.strictEqual(await page.locator('#forces-passage').isVisible(), true);
    assert.strictEqual(await page.locator('#arithmetic-passage').isVisible(), true);
    assert.strictEqual(await page.locator('#ready-note').count(), 0);

    await context.close();
    recordPass('Warm-up routing matrix: arithmetic gap shows arithmetic passage only; both gaps show both passages');
  } catch (err) {
    recordFail('Warm-up routing matrix', err);
  }

  // TEST 4: Number accuracy check across the system (2 m/s^2, 6 N, 4 N)
  try {
    const htmlContent = fs.readFileSync(htmlFilePath, 'utf8');
    // Main problem numbers
    assert.ok(htmlContent.includes('2 m/s²'));
    assert.ok(htmlContent.includes('6 N'));
    // Fresh problem numbers
    assert.ok(htmlContent.includes('4 N'));
    recordPass('Every number on screen matches physics (2 m/s^2, 6 N, 4 N)');
  } catch (err) {
    recordFail('Number accuracy check', err);
  }

  // TEST 5: Mobile 390px Viewport Check & Tap Targets
  try {
    const { context, page } = await createMonitoredPage({ width: 390, height: 844 });
    await page.goto(fileUrl);

    // Start Screen
    await assertNoHorizontalScroll(page, 'Mobile Start Screen');
    await page.screenshot({ path: path.join(shotsDir, '15-mobile-390px.png'), fullPage: true });

    // Tap target check
    const startBtnBox = await page.locator('#start-btn').boundingBox();
    assert.ok(startBtnBox.height >= 48, `Start button height must be >= 48px, got ${startBtnBox.height}`);

    await page.click('#start-btn');
    await assertNoHorizontalScroll(page, 'Mobile Warmups Screen');

    const warmupLabelBox = await page.locator('.option-item').first().boundingBox();
    assert.ok(warmupLabelBox.height >= 48, `Warmup option label height must be >= 48px, got ${warmupLabelBox.height}`);

    const unsureBtnBox = await page.locator('#warmup-1-unsure-btn').boundingBox();
    assert.ok(unsureBtnBox.height >= 48, `Unsure button height must be >= 48px, got ${unsureBtnBox.height}`);

    await context.close();
    recordPass('Mobile check: 390px viewport has zero horizontal scroll and large >=48px tap targets');
  } catch (err) {
    recordFail('Mobile check', err);
  }

  // TEST 6: Zero console errors
  try {
    assert.strictEqual(
      consoleErrors.length,
      0,
      `Zero console errors required, found: ${JSON.stringify(consoleErrors)}`
    );
    recordPass('Console errors: zero console errors across all interactions');
  } catch (err) {
    recordFail('Console errors', err);
  }

  await browser.close();

  // Clean up test session json file
  if (savedSessionFilePath && fs.existsSync(savedSessionFilePath)) {
    try {
      fs.unlinkSync(savedSessionFilePath);
    } catch {
      // ignore
    }
  }

  console.log(`\n--- Test Suite Summary: ${passed} passed, ${failed} failed ---`);
  if (failed > 0) {
    process.exit(1);
  }
}

runTests().catch(err => {
  console.error('Unhandled test failure:', err);
  process.exit(1);
});
