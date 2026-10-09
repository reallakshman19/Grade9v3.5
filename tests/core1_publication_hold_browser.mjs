// Real HTTP + Chromium denial oracle for the release-HOLD Core public surface.
// This is not positive six-Core learner qualification. The existing positive
// Motion Session journey remains a separate, unsatisfied acceptance contract.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { dirname, extname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const repo = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
};

const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    const source = resolve(repo, "." + pathname);
    assert.ok(source.startsWith(repo + sep), "request escapes repository");
    assert.ok((await stat(source)).isFile(), "not a file");
    response.writeHead(200, {
      "content-type": MIME[extname(source)] || "application/octet-stream",
      "cache-control": "no-store",
    });
    response.end(await readFile(source));
  } catch {
    response.writeHead(404);
    response.end("not found");
  }
});
await new Promise((done) => server.listen(0, "127.0.0.1", done));
const base = `http://127.0.0.1:${server.address().port}`;
let browser;
try {
  const publicBytes = await readFile(resolve(repo, "public/core-learning/data.js"));
  const pagesBytes = await readFile(resolve(repo, "docs/core-learning/data.js"));
  assert.deepEqual(pagesBytes, publicBytes, "public/ and Pages Core bytes diverged");
  const script = publicBytes.toString("utf8");
  const json = JSON.parse(script.slice(script.indexOf("{"), script.lastIndexOf("}") + 1));
  assert.equal(json.publication_gate.status, "HOLD");
  assert.equal(json.publication_gate.code, "NO_INDEPENDENT_CORE_PUBLICATION_GRANT");
  assert.deepEqual(json.core_projections, []);
  assert.deepEqual(json.bucket_availability, []);
  assert.deepEqual(json.findings, []);

  browser = await chromium.launch({ headless: true });
  for (const surface of ["public", "docs"]) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    try {
      const asset = await page.request.get(`${base}/${surface}/core-learning/data.js`);
      assert.equal(asset.status(), 200);
      assert.deepEqual(await asset.body(), publicBytes, surface + " served wrong Core asset");

      // A saved direct link must not bypass the empty authorized public set.
      await page.goto(
        `${base}/${surface}/core-learning/index.html?projection=physics:mic-phy-kin-2d-independent-components:core1b`,
        { waitUntil: "load" },
      );
      await page.waitForFunction(() => window.__coreLearningStaticHostReady === true, null, { timeout: 15000 });
      const host = await page.evaluate(() => ({
        status: document.getElementById("projection-status")?.textContent || "",
        disabled: document.getElementById("projection-select")?.disabled,
        options: document.getElementById("projection-select")?.options.length,
        buttonDisabled: document.getElementById("load-projection")?.disabled,
        rows: window.GRADE9V3_CORE?.core_projections,
        gate: window.GRADE9V3_CORE?.publication_gate?.status,
      }));
      assert.equal(host.gate, "HOLD");
      assert.deepEqual(host.rows, []);
      assert.equal(host.disabled, true, "activity chooser not disabled");
      assert.equal(host.buttonDisabled, true, "load button not disabled");
      assert.equal(host.options, 0, "unauthorized Core activities in chooser");
      assert.match(host.status, /Core learner publication held: NO_INDEPENDENT_CORE_PUBLICATION_GRANT/);
      assert.deepEqual(errors, [], `${surface} Core host JS errors: ${errors.join(" | ")}`);
      console.log(`${surface}/core-learning: HOLD, empty chooser, blocked direct link`);

      // The same public asset also feeds Motion Session. Reject *before*
      // resolving an identity or exposing an interactive study session.
      await page.goto(`${base}/${surface}/motion-session/index.html`, { waitUntil: "load" });
      await page.waitForFunction(
        () => document.querySelector("#session-unavailable [data-error-code]")?.textContent
          === "NO_INDEPENDENT_CORE_PUBLICATION_GRANT",
        null,
        { timeout: 15000 },
      );
      const motion = await page.evaluate(() => ({
        code: document.querySelector("#session-unavailable [data-error-code]")?.textContent,
        holdVisible: !document.querySelector("#session-unavailable")?.hidden,
        sessionHidden: document.querySelector("#session-app")?.hidden,
        ready: window.__motionSessionReady,
        identity: window.__motionSessionIdentity,
        trace: window.__motionSessionTrace || [],
      }));
      assert.equal(motion.code, "NO_INDEPENDENT_CORE_PUBLICATION_GRANT");
      assert.equal(motion.holdVisible, true);
      assert.equal(motion.sessionHidden, true);
      assert.equal(motion.ready, false);
      assert.equal(motion.identity, null);
      assert.ok(motion.trace.some((event) =>
        JSON.stringify(event).includes("NO_INDEPENDENT_CORE_PUBLICATION_GRANT")),
      "Motion Session must preserve the named denial in its trace");
      assert.deepEqual(errors, [], `${surface} Motion Session JS errors: ${errors.join(" | ")}`);
      console.log(`${surface}/motion-session: HOLD before identity and interaction`);

      // Simulate a legacy cached asset that still contains an internal Physics
      // compiler preview and does not carry the new publication_gate. The
      // browser must not interpret a formerly usable projection as released.
      const stalePayload = {
        generated_by: "Shared/tools/build_core_learning_data.py",
        provider_status: "PRODUCTION_COMPILED_CANONICAL",
        core_projections: [{
          id: "physics:mic-phy-kin-2d-independent-components:core1b",
          subject: "Physics",
          source_ref: "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS",
          projection: { core: "CORE1B" },
        }],
        bucket_availability: [],
      };
      const staleScript = "window.GRADE9V3_CORE = " + JSON.stringify(stalePayload) + ";";
      await page.route("**/core-learning/data.js", (route) => route.fulfill({
        status: 200, contentType: "text/javascript", body: staleScript,
      }));
      await page.goto(
        `${base}/${surface}/core-learning/index.html?projection=physics:mic-phy-kin-2d-independent-components:core1b`,
        { waitUntil: "load" },
      );
      await page.waitForFunction(() => window.__coreLearningStaticHostReady === true, null, { timeout: 15000 });
      const stale = await page.evaluate(() => ({
        incomingRows: window.GRADE9V3_CORE?.core_projections?.length,
        choices: document.getElementById("projection-select")?.options.length,
        disabled: document.getElementById("projection-select")?.disabled,
        status: document.getElementById("projection-status")?.textContent || "",
      }));
      assert.equal(stale.incomingRows, 1, "legacy fixture not actually injected");
      assert.equal(stale.choices, 0, "legacy preview reappeared in the public chooser");
      assert.equal(stale.disabled, true, "legacy preview unlocked public chooser");
      assert.match(stale.status, /Core learner publication data unverified: NO_INDEPENDENT_CORE_PUBLICATION_GRANT/);

      await page.goto(`${base}/${surface}/motion-session/index.html`, { waitUntil: "load" });
      await page.waitForFunction(
        () => document.querySelector("#session-unavailable [data-error-code]")?.textContent
          === "NO_INDEPENDENT_CORE_PUBLICATION_GRANT", null, { timeout: 15000 },
      );
      assert.equal(await page.evaluate(() => window.__motionSessionReady), false);
      assert.equal(await page.evaluate(() => window.__motionSessionIdentity), null);
      assert.deepEqual(errors, [], `${surface} legacy-cache JS errors: ${errors.join(" | ")}`);
      // Real Topic Atlas must also deny legacy Core deep links, while its
      // separately governed visual and portable links remain available.
      await page.goto(`${base}/${surface}/physics/motion-2d/atlas.html`, { waitUntil: "load" });
      await page.waitForFunction(
        () => Boolean(window.ATLAS?.__test?.resolveCoreDestinationsFor
          && document.getElementById("card-R1")), null, { timeout: 15000 },
      );
      await page.evaluate(() => window.ATLAS.openRung("R1"));
      await page.waitForFunction(
        () => document.getElementById("card-R1")?.open === true, null, { timeout: 10000 },
      );
      const atlas = await page.evaluate(() => {
        const card = document.getElementById("card-R1");
        return {
          incomingRows: window.GRADE9V3_CORE?.core_projections?.length,
          holdVisible: card?.textContent?.includes(
            "Core publication held: NO_INDEPENDENT_CORE_PUBLICATION_GRANT"),
          coreLinks: card?.querySelectorAll('a[href*="core-learning"][href*="projection="]').length || 0,
          visualLinks: card?.querySelectorAll('a[href*="shared-clock"]').length || 0,
          portableLinks: card?.querySelectorAll('a[href*="portable-workbench"]').length || 0,
        };
      });
      assert.equal(atlas.incomingRows, 1, "legacy preview did not reach Atlas");
      assert.equal(atlas.holdVisible, true, "Atlas did not explain the Core HOLD");
      assert.equal(atlas.coreLinks, 0, "cached compiler preview leaked into Atlas Core links");
      assert.ok(atlas.visualLinks >= 1, "unrelated visual destinations were suppressed");
      assert.ok(atlas.portableLinks >= 1, "unrelated portable destinations were suppressed");
      assert.deepEqual(errors, [], `${surface} legacy-cache Atlas errors: ${errors.join(" | ")}`);
      await page.unroute("**/core-learning/data.js");
      console.log(`${surface}: legacy Core preview withheld; Atlas visual and portable links retained`);
    } finally {
      await context.close();
    }
  }
  console.log("PASS: actual public/Pages browser HTTP denial paths");
} finally {
  if (browser) await browser.close();
  await new Promise((done) => server.close(done));
}
