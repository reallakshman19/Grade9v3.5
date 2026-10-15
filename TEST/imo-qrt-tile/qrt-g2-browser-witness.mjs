// Real Chromium witness for QRT-RETRIEVE-D1 at a frozen coder SHA.
// Validator-owned, local-only. No academic/source-rights acceptance or publication.
// Run: QRT_SOURCE_SHA=<40 hex> QRT_BASE_URL=http://127.0.0.1:8777 node <this file>
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";
import { q022HintPreservesProtectedWork, katexWitnessPasses, coreRouteVisible } from "./qrt-g2-browser-predicates.mjs";

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
    katexQuestionNodes: document.querySelectorAll("#tab-core2 .qb-question .katex").length,
    katexQuestionErrors: document.querySelectorAll("#tab-core2 .qb-question .katex-error").length,
  }));
  report.initial_dom = init;
  add("BROWSER_TABS_AND_QUESTION_RENDER", init.core2 && init.core1 && init.questions >= 12,
      "Core1A/Core2 tabs and 12+ rendered questions");
  add("BROWSER_KATEX_RUNTIME", katexWitnessPasses(init),
      "renderMathInElement="+init.katexApi+"; rendered KaTeX spans="+init.katexNodes+
      "; question spans="+init.katexQuestionNodes+"; question errors="+init.katexQuestionErrors);
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
      // Evaluate attribute equality without CSS string escaping ambiguity.
      const targetCount = await page.evaluate(key =>
        [...document.querySelectorAll("#tab-core1-all .topic-module-card")]
          .filter(el => el.getAttribute("data-package-id") === key).length, unitId);
      if (targetCount !== 1) throw Error("target package count=" + targetCount);
      await nav.focus();
      await page.keyboard.press("Enter");
      // The card can be scrolled into view asynchronously; wait for its
      // actual viewport intersection, not merely an inline display attribute.
      await page.waitForFunction(key => {
        const tab = document.querySelector("#tab-core1-all");
        const card = [...document.querySelectorAll("#tab-core1-all .topic-module-card")]
          .find(el => el.getAttribute("data-package-id") === key);
        if (!tab?.classList.contains("active") || !card?.classList.contains("highlighted")) return false;
        const r = card.getBoundingClientRect();
        if (!(r.width > 0 && r.height > 0 && r.bottom > 0 && r.right > 0 &&
              r.top < innerHeight && r.left < innerWidth)) return false;
        for (let el = card; el; el = el.parentElement) {
          const css = getComputedStyle(el);
          if (css.display === "none" || css.visibility === "hidden" ||
              css.visibility === "collapse" || Number(css.opacity) === 0) return false;
        }
        return true;
      }, unitId, {timeout: 7000});
      const visibility = await page.evaluate(key => {
        const tab = document.querySelector("#tab-core1-all");
        const card = [...document.querySelectorAll("#tab-core1-all .topic-module-card")]
          .find(el => el.getAttribute("data-package-id") === key);
        const ancestorStyles = [];
        for (let el = card; el; el = el.parentElement) {
          const css = getComputedStyle(el);
          ancestorStyles.push({display:css.display,visibility:css.visibility,opacity:css.opacity});
        }
        const r = card.getBoundingClientRect();
        return { tabActive:tab?.classList.contains("active") === true,
          highlighted:card?.classList.contains("highlighted") === true,
          ancestorStyles,
          rect:{top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height},
          viewport:{width:innerWidth,height:innerHeight}
        };
      }, unitId);
      if (!coreRouteVisible(visibility)) throw Error("DESTINATION_NOT_COMPUTED_VISIBLE_IN_VIEWPORT: "+JSON.stringify(visibility));
      row.verdict = "PASS";
      row.detail = "native Enter, Core tab, unique package, computed visible, layout and viewport intersection";
      row.visibility = {rect:visibility.rect,viewport:visibility.viewport,ancestors:visibility.ancestorStyles.length};
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

  const hintTier = card.locator("[id=" + JSON.stringify("hint2-"+qid) + "]");
  await hintTier.locator("> summary").click();
  const hintText = await hintTier.locator(".ladder-rung").innerText();
  add("BROWSER_Q022_REVISED_HINT_LEAVES_VALUE_TO_LEARNER",
      q022HintPreservesProtectedWork(hintText),
      "Method cue without keyed numeric/classification disclosure: "+hintText.slice(0,220));
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
