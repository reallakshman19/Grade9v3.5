// Real Chromium witness for QRT-RETRIEVE-D1 at a frozen coder SHA.
// Validator-owned, local-only. No academic/source-rights acceptance or publication.
// Run: QRT_SOURCE_SHA=<40 hex> QRT_BASE_URL=http://127.0.0.1:8777 node <this file>
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const qrtSha = process.env.QRT_SOURCE_SHA;
const base = process.env.QRT_BASE_URL || "http://127.0.0.1:8777";
const evidenceDir = process.env.QRT_EVIDENCE_DIR || "build/qrt-g2";
const ledger = JSON.parse(fs.readFileSync(
  "TEST/imo-qrt-tile/qrt-retrieve-d1-semantic-desk-review.v1.json", "utf8"
));
if (!/^[0-9a-f]{40}$/.test(qrtSha || "") || ledger.source_commit !== qrtSha) {
  throw new Error("BROWSER_SOURCE_LEDGER_SHA_NOT_FROZEN");
}
fs.mkdirSync(evidenceDir, { recursive: true });
const report = {
  schema: "qrt-g2-browser-witness/v1",
  source_commit: qrtSha,
  status: "NOT_RUN",
  browser: "playwright chromium",
  html: "standalone/mathematics-imo-grade9-master-suite.html",
  academic_approval: "NOT_GRANTED",
  source_rights: "NOT_VERIFIED",
  assertions: [],
  navigation: [],
  page_errors: [],
};
const add = (id, pass, detail) => {
  report.assertions.push({ id, verdict: pass ? "PASS" : "FAIL", detail });
};
let browser;
try {
  browser = await chromium.launch({ headless: true, args: ["--disable-dev-shm-usage"] });
  const page = await browser.newPage({ viewport: { width: 1366, height: 854 } });
  page.setDefaultTimeout(12000);
  page.on("pageerror", err => report.page_errors.push(String(err?.message || err)));
  await page.goto(base + "/standalone/mathematics-imo-grade9-master-suite.html", {
    waitUntil: "domcontentloaded", timeout: 60000,
  });
  const init = await page.evaluate(() => ({
    core2: !!document.querySelector("#tab-core2"),
    core1: !!document.querySelector("#tab-core1-all"),
    questions: document.querySelectorAll(".qb-question").length,
    packages: document.querySelectorAll("#tab-core1-all .topic-module-card[data-package-id]").length,
    katexApi: typeof window.renderMathInElement,
    katexNodes: document.querySelectorAll(".katex").length,
  }));
  report.initial_dom = init;
  add("BROWSER_TABS_AND_QUESTION_RENDER", init.core2 && init.core1 && init.questions >= 12,
      "Core1A/Core2 tabs and 12+ rendered questions");
  add("BROWSER_KATEX_RUNTIME", init.katexApi === "function",
      "renderMathInElement="+init.katexApi+"; rendered KaTeX spans="+init.katexNodes);
  const known = new Set(ledger.core_links.map(x => x.question_id));
  add("BROWSER_EXACT_12_QUESTION_IDS", known.size === 12,
      "Review ledger question IDs="+known.size);

  // A real native-button Enter key must activate a rendered, unique Core1A
  // package target. This is stronger than the static JS/data-package-id check.
  for (const qid of known) {
    const row = { question_id: qid, verdict: "FAIL", route: null };
    try {
      await page.evaluate(() => switchTab("core2"));
      const nav = page.locator("[id=" + JSON.stringify("q-" + qid) + "] button.qb-core-nav");
      if (await nav.count() !== 1) throw Error("native Core button not unique");
      const handler = await nav.getAttribute("onclick");
      const match = handler?.match(/jumpToCoreUnit\('([^']+)'\)/);
      if (!match) throw Error("no declared direct jumpToCoreUnit package ID");
      const unitId = match[1];
      row.route = unitId;
      const declared = await page.evaluate(key =>
        document.querySelectorAll("#tab-core1-all .topic-module-card[data-package-id=" +
          CSS.escape(JSON.stringify(key)) + "]").length, unitId);
      // Evaluate attribute equality without CSS string escaping ambiguity.
      const targetCount = await page.evaluate(key =>
        [...document.querySelectorAll("#tab-core1-all .topic-module-card")]
          .filter(el => el.getAttribute("data-package-id") === key).length, unitId);
      if (targetCount !== 1) throw Error("target package count=" + targetCount);
      await nav.focus();
      await page.keyboard.press("Enter");
      await page.waitForFunction(key => {
        const tab = document.querySelector("#tab-core1-all");
        const card = [...document.querySelectorAll("#tab-core1-all .topic-module-card")]
          .find(el => el.getAttribute("data-package-id") === key);
        return !!(tab?.classList.contains("active") &&
          card && card.classList.contains("highlighted") &&
          card.style.display !== "none");
      }, unitId, {timeout: 5000});
      row.verdict = "PASS";
      row.detail = "native Enter, Core tab, unique declared package, visible highlighted destination";
    } catch (err) {
      row.detail = String(err?.message || err).slice(0, 1000);
    }
    report.navigation.push(row);
  }
  add("BROWSER_12_DIRECT_CORE_KEYBOARD_ROUTES",
      report.navigation.length === 12 &&
      report.navigation.every(x => x.verdict === "PASS"),
      "Passed "+report.navigation.filter(x => x.verdict === "PASS").length+"/12 direct Enter routes");

  // Q022 is the previously leaked compound answer. Probe gating in the live
  // DOM; a source-string check alone cannot attest active browser behavior.
  const qid = "SOF-IMO-G09-L1-2024-25-B-Q022";
  await page.evaluate(() => switchTab("core2"));
  const card = page.locator("[id=" + JSON.stringify("q-" + qid) + "]");
  const get = async suffix => await page.evaluate(({qid,suffix}) => {
    const el = document.getElementById(suffix+"-"+qid);
    return !el ? null : { hidden: el.hidden, inert: el.hasAttribute("inert"),
      open: el.open ?? null, disabled: el.disabled ?? null,
      state: el.dataset.state || "" };
  }, {qid,suffix});
  const before = { hint2: await get("hint2"), sol: await get("sol-disc"),
    diagnosis: await get("diag-disc") };
  report.attempt_gate = { before };
  add("BROWSER_PREATTEMPT_SECOND_HINT_LOCK",
      before.hint2?.hidden === true && before.hint2?.inert === true,
      JSON.stringify(before.hint2));
  add("BROWSER_PREATTEMPT_SOLUTION_DIAGNOSIS_LOCK",
      before.sol?.hidden === true && before.sol?.inert === true &&
      before.diagnosis?.hidden === true && before.diagnosis?.inert === true,
      JSON.stringify({sol:before.sol,diagnosis:before.diagnosis}));
  const commitButton = card.locator("[id=" + JSON.stringify("commit-"+qid) + "]");
  await commitButton.click();
  const invalid = {feedback:await card.locator("[id=" +
      JSON.stringify("feedback-"+qid) + "]").getAttribute("data-state"),
    solution:await get("sol-disc")};
  report.attempt_gate.empty = invalid;
  add("BROWSER_EMPTY_COMMIT_REFUSED",
      invalid.feedback === "invalid" && invalid.solution?.hidden === true,
      JSON.stringify(invalid));
  // Open conceptual gate and first tier by actual user clicks.
  await card.locator(".qb-support-container > details.qb-disclosure > summary").first().click();
  await card.locator("[id=" + JSON.stringify("hint1-"+qid) + "] > summary").click();
  await page.waitForFunction(q => {
    const e = document.getElementById("hint2-"+q);
    return e && !e.hidden && !e.hasAttribute("inert");
  }, qid, {timeout:3000});
  const afterHint = {hint2:await get("hint2"),solution:await get("sol-disc")};
  report.attempt_gate.hint1_open = afterHint;
  add("BROWSER_TIER2_PROGRESSIVE_UNLOCK",
      afterHint.hint2?.hidden === false && afterHint.hint2?.inert === false &&
      afterHint.solution?.hidden === true, JSON.stringify(afterHint));

  const hintText = await card.locator("[id=" + JSON.stringify("hint2-"+qid) + "]").innerText();
  add("BROWSER_Q022_REVISED_HINT_LEAVES_VALUE_TO_LEARNER",
      hintText.includes("Carry out the difference of squares yourself") &&
      !/9\s*[-−]\s*2\s*=\s*7/.test(hintText),
      "Method-only hint present; numeric equation not present: "+hintText.slice(0,160));
  await card.locator("[id=" + JSON.stringify("att-"+qid) + "]")
    .fill("I will apply the difference-of-squares identity and test whether the result is rational.");
  await commitButton.focus();
  await page.keyboard.press("Enter");
  const afterCommit={solution:await get("sol-disc"),
    diagnosis:await get("diag-disc"),button:await get("commit"),
    feedback:await card.locator("[id=" + JSON.stringify("feedback-"+qid) + "]").getAttribute("data-state")};
  report.attempt_gate.committed = afterCommit;
  add("BROWSER_VALID_KEYBOARD_COMMIT_UNLOCKS_POSTATTEMPT",
      afterCommit.solution?.hidden === false && afterCommit.solution?.open === true &&
      afterCommit.diagnosis?.hidden === false && afterCommit.button?.disabled === true &&
      afterCommit.feedback === "committed", JSON.stringify(afterCommit));
  add("BROWSER_NO_UNCAUGHT_JS_PAGE_ERRORS", report.page_errors.length === 0,
      JSON.stringify(report.page_errors.slice(0,6)));
} catch (err) {
  add("BROWSER_HARNESS_RUNTIME", false, String(err?.stack || err).slice(0,2800));
} finally {
  if (browser) await browser.close().catch(()=>{});
  report.status = report.assertions.every(a=>a.verdict==="PASS")?"PASS":"FAIL";
  report.passed = report.assertions.filter(a=>a.verdict==="PASS").length;
  report.failed = report.assertions.filter(a=>a.verdict==="FAIL").length;
  fs.writeFileSync(path.join(evidenceDir,"tile1-browser.json"),
    JSON.stringify(report,null,2)+"\n");
  console.log(JSON.stringify({
    source_commit:report.source_commit, status:report.status,
    passed:report.passed,failed:report.failed,
    nav_pass:report.navigation.filter(x=>x.verdict==="PASS").length,
    assertions:report.assertions,
  },null,2));
  if(report.status!=="PASS") process.exitCode=1;
}
