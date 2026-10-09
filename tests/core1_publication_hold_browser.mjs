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
    } finally {
      await context.close();
    }
  }
  console.log("PASS: actual public/Pages browser HTTP denial paths");
} finally {
  if (browser) await browser.close();
  await new Promise((done) => server.close(done));
}
