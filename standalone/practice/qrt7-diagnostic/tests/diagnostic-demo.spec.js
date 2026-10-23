/**
 * Playwright browser test for G9O5-2a Seven-Question Diagnostic Prototype.
 * Executes in real Chrome via `chromium.launch({ channel: 'chrome' })` over `file://` protocol.
 * Verifies:
 * - Zero console errors.
 * - Responsive at 390px phone width with no horizontal scroll.
 * - Owner demo step 1: 7-question unassisted flow (mix of correct, wrong, no-answer), no hints/cues.
 * - Owner demo step 2: Submission, frozen attempt, 7-row review, distinct no-answer, readable evidence table.
 * - Owner demo step 3: JSON download and reopening, verification of 7 assessed + 21 unassessed cells.
 * - Owner demo step 4: Fresh attempt reset and inactive timing pause verification.
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function runTests() {
  console.log('=== Starting G9O5-2a Real Chrome Browser Test Suite ===');
  let passedCount = 0;
  let failedCount = 0;

  function assert(condition, message) {
    if (!condition) {
      console.error(`  FAIL: ${message}`);
      failedCount++;
      throw new Error(message);
    } else {
      console.log(`  PASS: ${message}`);
      passedCount++;
    }
  }

  const htmlPath = path.resolve(__dirname, '..', 'index.html');
  const fileUrl = 'file:///' + htmlPath.replace(/\\/g, '/');
  const shotsDir = path.resolve(__dirname, 'shots');
  if (!fs.existsSync(shotsDir)) {
    fs.mkdirSync(shotsDir, { recursive: true });
  }

  console.log(`Target Page URL: ${fileUrl}`);

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1200, height: 900 }
  });

  const page = await context.newPage();

  // Track console errors
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.error(`Browser console error: ${msg.text()}`);
      consoleErrors.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    console.error(`Browser page error: ${err.message}`);
    consoleErrors.push(err.message);
  });

  try {
    // -------------------------------------------------------------
    // Test 1: Page load & Initial State Verification
    // -------------------------------------------------------------
    console.log('\n--- Test 1: Page load and initial zero-cue state ---');
    await page.goto(fileUrl, { waitUntil: 'load' });
    await page.waitForTimeout(300);

    assert(consoleErrors.length === 0, 'No console errors on initial page load');
    
    const pageTitle = await page.title();
    assert(pageTitle.includes("Newton's Laws"), `Page title is: ${pageTitle}`);

    const noticeText = await page.textContent('.notice-box');
    assert(noticeText.includes('No hints during these seven questions; answers appear together at the end'),
      'Notice box correctly communicates purpose and no-hint rule');

    const stepCounter = await page.textContent('#step-counter');
    assert(stepCounter.includes('Question 1 of 7'), 'Stepper indicates Question 1 of 7');

    // Confirm NO strategy cues / type names on Question 1 view
    const bodyContent = await page.textContent('#question-view');
    assert(!bodyContent.includes('APPLY') && !bodyContent.includes('SYNTHESIZE'),
      'No cognitive type labels displayed during question view');

    await page.screenshot({ path: path.join(shotsDir, 'shot-01-question1-desktop.png') });

    // -------------------------------------------------------------
    // Test 2: Mobile 390px Viewport & No Horizontal Scroll
    // -------------------------------------------------------------
    console.log('\n--- Test 2: Mobile 390px width check ---');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(200);

    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });
    assert(!hasHorizontalScroll, 'No horizontal scroll at 390px mobile phone width');

    await page.screenshot({ path: path.join(shotsDir, 'shot-05-mobile-390px.png') });

    // Reset viewport to desktop
    await page.setViewportSize({ width: 1200, height: 900 });
    await page.waitForTimeout(200);

    // -------------------------------------------------------------
    // Test 3: Owner Demo Step 1 - Complete 7 questions with synthetic answers
    // -------------------------------------------------------------
    console.log('\n--- Test 3: Owner Demo Step 1 (Synthetic trial flow) ---');

    // Q1: APPLY -> Select D (Correct), Why, Confidence
    await page.locator('.option-card input[value="D"]').click();
    await page.fill('#why-input', 'Synthetic trial: 3rd law action-reaction equal and opposite');
    await page.locator('.confidence-btn[data-val="Sure"]').click();
    await page.locator('#btn-next').click();
    await page.waitForTimeout(200);

    // Q2: SYNTHESIZE -> Select B (Wrong distractor), Why, Confidence
    const q2Counter = await page.textContent('#step-counter');
    assert(q2Counter.includes('Question 2 of 7'), 'Advanced to Question 2 of 7');
    await page.locator('.option-card input[value="B"]').click();
    await page.fill('#why-input', 'Synthetic trial: selecting distractor option B to test wrong answer');
    await page.locator('.confidence-btn[data-val="Unsure"]').click();
    await page.locator('#btn-next').click();
    await page.waitForTimeout(200);

    // Q3: REPRESENT -> Select "I cannot choose yet" (No Answer), Why, Confidence
    const q3Counter = await page.textContent('#step-counter');
    assert(q3Counter.includes('Question 3 of 7'), 'Advanced to Question 3 of 7');
    await page.locator('.option-card input[value="__no_answer__"]').click();
    await page.fill('#why-input', 'Not sure');
    await page.locator('.confidence-btn[data-val="Unsure"]').click();
    await page.locator('#btn-next').click();
    await page.waitForTimeout(200);

    // Q4: MODEL -> Select A (Correct), Why, Confidence
    const q4Counter = await page.textContent('#step-counter');
    assert(q4Counter.includes('Question 4 of 7'), 'Advanced to Question 4 of 7');
    await page.locator('.option-card input[value="A"]').click();
    await page.fill('#why-input', 'Synthetic trial: treat A+B as composite system of 10 kg');
    await page.locator('.confidence-btn[data-val="Sure"]').click();
    await page.locator('#btn-next').click();
    await page.waitForTimeout(200);

    // Q5: EXPLAIN -> Select D (Wrong distractor), Why, Confidence
    const q5Counter = await page.textContent('#step-counter');
    assert(q5Counter.includes('Question 5 of 7'), 'Advanced to Question 5 of 7');
    await page.locator('.option-card input[value="D"]').click();
    await page.fill('#why-input', 'Synthetic trial: testing distractor hypothesis D');
    await page.locator('.confidence-btn[data-val="Guessing"]').click();
    await page.locator('#btn-next').click();
    await page.waitForTimeout(200);

    // Q6: JUSTIFY -> Evidence Table check, Select A (Correct), Why, Confidence
    const q6Counter = await page.textContent('#step-counter');
    assert(q6Counter.includes('Question 6 of 7'), 'Advanced to Question 6 of 7');
    
    // Check evidence table readability
    const tableVisible = await page.locator('.evidence-table').isVisible();
    assert(tableVisible, 'Evidence table is visible on Question 6 (JUSTIFY)');
    const tableText = await page.textContent('.evidence-table');
    assert(tableText.includes('Trial') && tableText.includes('4 N right') && tableText.includes('5 N left'),
      'Evidence table contains trial data columns and rows');
    await page.screenshot({ path: path.join(shotsDir, 'shot-02-question6-evidence-table.png') });

    await page.locator('.option-card input[value="A"]').click();
    await page.fill('#why-input', 'Synthetic trial: measurement table shows magnitude matching for all 3 trials');
    await page.locator('.confidence-btn[data-val="Sure"]').click();
    await page.locator('#btn-next').click();
    await page.waitForTimeout(200);

    // Q7: RETRIEVE -> Question 7 check, Select C (Correct), Why, Confidence
    const q7Counter = await page.textContent('#step-counter');
    assert(q7Counter.includes('Question 7 of 7'), 'Advanced to Question 7 of 7');
    const nextBtnText = await page.textContent('#btn-next');
    assert(nextBtnText.includes('Submit Diagnostic'), 'Final question button reads "Submit Diagnostic"');

    // Confirm no hints or answers have appeared anywhere prior to submission
    const reviewVisibleBeforeSubmit = await page.locator('#review-view').isVisible();
    assert(!reviewVisibleBeforeSubmit, 'Review view remains hidden before submission');

    await page.locator('.option-card input[value="C"]').click();
    await page.fill('#why-input', 'Synthetic trial: Newton third law textbook definition');
    await page.locator('.confidence-btn[data-val="Sure"]').click();

    // -------------------------------------------------------------
    // Test 4: Owner Demo Step 2 - Submit & Review 7 rows
    // -------------------------------------------------------------
    console.log('\n--- Test 4: Owner Demo Step 2 (Submit & Review) ---');
    await page.locator('#btn-next').click();
    await page.waitForTimeout(400);

    const reviewVisibleAfterSubmit = await page.locator('#review-view').isVisible();
    assert(reviewVisibleAfterSubmit, 'Review view is now visible after submission');

    // Check Question 3 (No answer) is distinctly marked as "Not answered"
    const q3ReviewText = await page.textContent('#review-row-3');
    assert(q3ReviewText.includes('Not answered'), 'Question 3 explicitly labeled "Not answered"');
    assert(q3ReviewText.includes('cannot choose yet'), 'Question 3 shows explicit no-answer choice');

    // Check Question 2 (Wrong answer) is marked Incorrect with distractor tag
    const q2ReviewText = await page.textContent('#review-row-2');
    assert(q2ReviewText.includes('Incorrect'), 'Question 2 marked Incorrect');
    assert(q2ReviewText.includes('NET_FORCE_CONFUSED_WITH_CONTACT'),
      'Question 2 displays bank distractor tag NET_FORCE_CONFUSED_WITH_CONTACT');

    // Check Question 1 (Correct)
    const q1ReviewText = await page.textContent('#review-row-1');
    assert(q1ReviewText.includes('Correct'), 'Question 1 marked Correct');

    // Check Question 6 has readable evidence table in review as well
    const q6ReviewText = await page.textContent('#review-row-6');
    assert(q6ReviewText.includes('Trial') && q6ReviewText.includes('4 N right'),
      'Question 6 review displays readable evidence table');

    // Verify 7 total rows rendered
    const rowCount = await page.locator('.review-item-card').count();
    assert(rowCount === 7, `Review screen displays exactly 7 rows (found: ${rowCount})`);

    // Verify 28-cell coverage grid
    const cellBoxes = await page.locator('.cell-box').count();
    assert(cellBoxes === 28, `Coverage grid displays exactly 28 cells (found: ${cellBoxes})`);

    const assessedCount = await page.locator('.cell-box.assessed').count();
    assert(assessedCount === 7, `Coverage grid has exactly 7 assessed D1 cells (found: ${assessedCount})`);

    const unassessedCount = await page.locator('.cell-box.unassessed').count();
    assert(unassessedCount === 21, `Coverage grid has exactly 21 unassessed cells (found: ${unassessedCount})`);

    await page.screenshot({ path: path.join(shotsDir, 'shot-03-review-screen-desktop.png') });
    await page.screenshot({ path: path.join(shotsDir, 'shot-04-coverage-map-28.png') });

    // -------------------------------------------------------------
    // Test 5: Owner Demo Step 3 - Download JSON & Verify Contract
    // -------------------------------------------------------------
    console.log('\n--- Test 5: Owner Demo Step 3 (Download JSON & Verify Contract) ---');
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#btn-download-json').click();
    const download = await downloadPromise;

    const downloadedPath = path.join(shotsDir, download.suggestedFilename());
    await download.saveAs(downloadedPath);
    assert(fs.existsSync(downloadedPath), `JSON file downloaded: ${download.suggestedFilename()}`);

    const fileContent = fs.readFileSync(downloadedPath, 'utf8');
    const jsonRecord = JSON.parse(fileContent);

    assert(jsonRecord.record_version === '1.0', 'Contract record_version is 1.0');
    assert(jsonRecord.phase === 'diagnose', 'Contract phase is diagnose');
    assert(jsonRecord.topic_id === 'newtons-laws.contact-blocks', 'Contract topic_id is correct');
    assert(jsonRecord.bank_id === 'G9V35-QRT-CONTACT-D1', 'Contract bank_id is correct');
    assert(jsonRecord.level === 'D1', 'Contract level is D1');
    assert(jsonRecord.completed === true, 'Contract completed is true');
    assert(Array.isArray(jsonRecord.responses) && jsonRecord.responses.length === 7,
      'Contract contains exactly 7 responses');
    assert(Array.isArray(jsonRecord.coverage_map_28) && jsonRecord.coverage_map_28.length === 28,
      'Contract contains exactly 28-cell coverage map');

    const assessedCells = jsonRecord.coverage_map_28.filter(c => c.status === 'assessed');
    const unassessedCells = jsonRecord.coverage_map_28.filter(c => c.status === 'unassessed');
    assert(assessedCells.length === 7, 'Coverage map has exactly 7 assessed cells');
    assert(unassessedCells.length === 21, 'Coverage map has exactly 21 unassessed cells');

    // Verify Q3 no-answer response integrity
    const q3Resp = jsonRecord.responses[2];
    assert(q3Resp.response_kind === 'no_answer', 'Q3 response_kind is no_answer');
    assert(q3Resp.selected_option_id === null, 'Q3 selected_option_id is null');
    assert(q3Resp.is_correct === null, 'Q3 is_correct is null');

    // Verify Q2 wrong distractor response integrity
    const q2Resp = jsonRecord.responses[1];
    assert(q2Resp.is_correct === false, 'Q2 is_correct is false');
    assert(q2Resp.possible_misconception_tag === 'NET_FORCE_CONFUSED_WITH_CONTACT',
      'Q2 distractor tag preserved');

    // Test in-browser reopening of the JSON file
    console.log('\n--- Reopening downloaded JSON file via UI component ---');
    await page.setInputFiles('#json-file-input', downloadedPath);
    await page.waitForTimeout(300);

    const reopenStatusText = await page.textContent('#reopen-status');
    assert(reopenStatusText.includes('Successfully re-opened saved diagnostic!'),
      'UI confirms successful reopening of saved JSON');
    assert(reopenStatusText.includes('Cells Assessed: 7') && reopenStatusText.includes('Cells Unassessed: 21'),
      'UI verification confirms 7 assessed and 21 unassessed cells');

    await page.screenshot({ path: path.join(shotsDir, 'shot-06-reopen-verification.png') });

    // -------------------------------------------------------------
    // Test 6: Owner Demo Step 4 - Second Attempt & Inactive Time Handling
    // -------------------------------------------------------------
    console.log('\n--- Test 6: Owner Demo Step 4 (Fresh attempt reset & Inactive Timing) ---');
    const firstAttemptId = jsonRecord.attempt_id;

    // Click "Start New Attempt"
    await page.locator('#btn-new-attempt').click();
    await page.waitForTimeout(300);

    const q1VisibleAfterReset = await page.locator('#question-view').isVisible();
    assert(q1VisibleAfterReset, 'Returned to Question 1 after reset');

    const whyCleared = await page.inputValue('#why-input');
    assert(whyCleared === '', 'Why input was reset to empty');

    const anyOptionChecked = await page.locator('.option-card input:checked').count();
    assert(anyOptionChecked === 0, 'All option selections were cleared');

    // Test inactive timing simulation:
    // Window loses focus / document hidden for 1000ms
    console.log('Simulating window blur / switch away for 1000ms...');
    await page.evaluate(() => {
      window.dispatchEvent(new Event('blur'));
      Object.defineProperty(document, 'hidden', { value: true, configurable: true });
      document.dispatchEvent(new Event('visibilitychange'));
    });

    await page.waitForTimeout(1000); // 1000ms away

    // Switch back
    console.log('Simulating return to window focus...');
    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { value: false, configurable: true });
      document.dispatchEvent(new Event('visibilitychange'));
      window.dispatchEvent(new Event('focus'));
    });

    await page.waitForTimeout(400); // 400ms active

    // Complete Q1
    await page.locator('.option-card input[value="D"]').click();
    await page.fill('#why-input', 'Synthetic trial 2: testing reset and blur');
    await page.locator('.confidence-btn[data-val="Sure"]').click();

    // Advance through the remaining 6 questions quickly
    for (let i = 2; i <= 7; i++) {
      await page.locator('#btn-next').click();
      await page.waitForTimeout(150);
      await page.locator('.option-card input[value="A"]').click();
      await page.fill('#why-input', `Synthetic trial 2 reasoning for Q${i}`);
      await page.locator('.confidence-btn[data-val="Sure"]').click();
    }

    // Submit second attempt
    await page.locator('#btn-next').click();
    await page.waitForTimeout(300);

    // Download or inspect second contract
    const secondContractStr = await page.textContent('#json-preview-content');
    const secondContract = JSON.parse(secondContractStr);

    assert(secondContract.attempt_id !== firstAttemptId,
      `Fresh attempt ID generated (First: ${firstAttemptId}, Second: ${secondContract.attempt_id})`);

    const q1SecondAttempt = secondContract.responses[0];
    console.log(`Q1 Active ms: ${q1SecondAttempt.active_ms}, Wall ms: ${q1SecondAttempt.wall_ms}`);
    assert(q1SecondAttempt.wall_ms >= 1200, `Wall ms reflects elapsed duration (${q1SecondAttempt.wall_ms}ms >= 1200ms)`);
    assert(q1SecondAttempt.active_ms < 900,
      `Active ms excludes inactive time (${q1SecondAttempt.active_ms}ms < 900ms despite 1400ms+ total wall time)`);

    // Verify zero console errors throughout the entire suite
    assert(consoleErrors.length === 0, `Zero console errors throughout full test run (found: ${consoleErrors.length})`);

    console.log('\n======================================================');
    console.log(`TEST SUITE FINISHED: ${passedCount} PASSED, ${failedCount} FAILED.`);
    console.log('======================================================\n');

  } catch (err) {
    console.error('Fatal test error:', err);
    failedCount++;
  } finally {
    await browser.close();
  }

  if (failedCount > 0) {
    process.exit(1);
  }
}

runTests();
