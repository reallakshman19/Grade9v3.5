"""Offline HTTP integration and negative tests for actual Pages readback."""
from __future__ import annotations

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import subprocess
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from Shared.tools import pages_deployed_readback as audit

SHA = "a" * 40
ROUTE = "mathematics/imo-grade9/index.html"
BODY = b"<!doctype html><title>Grade9 IMO smoke fixture</title>"


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        self.server.calls.append(self.path)
        status, mime, content, headers = self.server.responses.get(path, (404, "text/html", b"missing", {}))
        # Allow tests to simulate an asynchronous deployment across polling rounds.
        if callable(content):
            content = content(self.path, self.server.calls)
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


class ReadbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        page = self.repo / "docs" / ROUTE
        page.parent.mkdir(parents=True)
        page.write_bytes(BODY)
        manifest = {"schema_version": "grade9v3-pages-mirror-v1",
                    "files": [{"source": "public/" + ROUTE, "target": ROUTE}]}
        (self.repo / "docs/.pages-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        self.server.calls = []
        self.server.responses = {"/Grade9v3.5/" + ROUTE: (200, "text/html; charset=utf-8", BODY, {})}
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}/Grade9v3.5/"
        # Loopback HTTP is enabled only for the test API, never the CLI.
        self.assertEqual(audit.valid_base(self.base, allow_loopback=True), self.base)
        with self.assertRaises(ValueError):
            audit.valid_base(self.base)

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.temp.cleanup()

    def check(self, *, attempts=1):
        return audit.audit(self.repo, self.base, expected_sha=SHA, paths=[ROUTE],
                           attempts=attempts, allow_loopback=True, fixture_only=True)

    def test_success_checks_default_and_cache_busted_bytes(self):
        result = self.check()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(self.server.calls), 2)
        self.assertIn("?g9_readback=" + SHA, self.server.calls[1])
        self.assertEqual(result["paths"][0]["expected_sha256"], hashlib.sha256(BODY).hexdigest())

    def test_missing_route_404_is_failure_even_when_html_returned(self):
        self.server.responses.clear()
        self.assertEqual(self.check()["paths"][0]["observations"]["normal"]["status"], 404)
        self.assertEqual(self.check()["status"], "FAIL")

    def test_wrong_bytes_or_mime_fails(self):
        key = "/Grade9v3.5/" + ROUTE
        self.server.responses[key] = (200, "text/html", b"outdated", {})
        self.assertEqual(self.check()["status"], "FAIL")
        self.server.responses[key] = (200, "text/plain", BODY, {})
        self.assertEqual(self.check()["status"], "FAIL")

    def test_redirect_is_not_mistaken_for_actual_page(self):
        key = "/Grade9v3.5/" + ROUTE
        self.server.responses[key] = (302, "text/html", b"", {"Location": "/Grade9v3.5/index.html"})
        self.assertEqual(self.check()["status"], "FAIL")
        self.assertEqual(len(self.server.calls), 2)

    def test_cache_busted_success_does_not_hide_stale_normal_url(self):
        key = "/Grade9v3.5/" + ROUTE
        self.server.responses[key] = (200, "text/html",
            lambda url, calls: BODY if "g9_readback=" in url else b"stale", {})
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["paths"][0]["checks"]["normal"])
        self.assertTrue(result["paths"][0]["checks"]["cache_busted"])

    def test_bounded_retry_can_observe_propagation(self):
        key = "/Grade9v3.5/" + ROUTE
        self.server.responses[key] = (200, "text/html",
            lambda url, calls: BODY if len(calls) > 2 else b"old", {})
        result = self.check(attempts=2)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["paths"][0]["attempts"], 2)

    def test_missing_manifest_target_rejected_before_http(self):
        (self.repo / "docs/.pages-manifest.json").write_text(
            json.dumps({"schema_version": "grade9v3-pages-mirror-v1", "files": []}))
        with self.assertRaisesRegex(ValueError, "not present"):
            self.check()
        self.assertEqual(self.server.calls, [])

    def test_expected_sha_and_path_validation(self):
        with self.assertRaisesRegex(ValueError, "exact 40-character SHA"):
            audit.audit(self.repo, self.base, expected_sha="wrong", paths=[ROUTE])
        for bad in ("../../secret.html", "/root.html", "evil.html?token=x",
                    "sub/%2e%2e/file.html", "sub\\file.html", "foo//bar.html"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                audit.valid_route(bad)

    def test_external_origin_must_be_project_github_pages(self):
        for bad in ("http://example.org/Grade9v3.5/",
                    "https://evil.example/Grade9v3.5/",
                    "https://x.github.io/../../secret/",
                    "https://x.github.io/Grade9v3.5/?test=1"):
            with self.subTest(url=bad), self.assertRaises(ValueError):
                audit.valid_base(bad)
        self.assertEqual(audit.valid_base("https://reallakshman19.github.io/Grade9v3.5/"),
                         "https://reallakshman19.github.io/Grade9v3.5/")


    def test_exact_head_binding_rejects_forged_sha_and_dirty_docs(self):
        def git(*args):
            proc = subprocess.run(["git", "-C", str(self.repo), *args],
                                  capture_output=True, check=True)
            return proc.stdout.decode("utf-8").strip()
        git("init", "-q")
        git("add", "docs")
        git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "test fixture")
        true_sha = git("rev-parse", "HEAD")
        with self.assertRaisesRegex(ValueError, "checkout SHA mismatch"):
            audit.audit(self.repo, self.base, expected_sha=SHA, paths=[ROUTE],
                        allow_loopback=True)
        self.assertEqual(self.server.calls, [], "incorrect commit must fail before HTTP")
        observed = audit.audit(self.repo, self.base, expected_sha=true_sha,
                               paths=[ROUTE], allow_loopback=True)
        self.assertEqual(observed["status"], "PASS")
        self.assertEqual(observed["expected_commit_sha"], true_sha)
        (self.repo / "docs" / ROUTE).write_bytes(b"uncommitted tampering")
        with self.assertRaisesRegex(ValueError, "working-tree Pages route differs"):
            audit.audit(self.repo, self.base, expected_sha=true_sha, paths=[ROUTE],
                        allow_loopback=True)

    def test_no_network_is_failure_not_a_success_or_not_run(self):
        with patch.object(audit, "_get", return_value={
            "url": self.base, "status": None, "content_type": None,
            "sha256": None, "bytes": None, "error": "NETWORK_URLError"}):
            self.assertEqual(self.check()["status"], "FAIL")

    def test_optional_deep_routes_checked_when_committed(self):
        opt = "mathematics/number-systems/index-laws/index.html"
        page = self.repo / "docs" / opt
        page.parent.mkdir(parents=True)
        page.write_bytes(BODY)
        manifest = json.loads((self.repo / "docs/.pages-manifest.json").read_text())
        manifest["files"].append({"source": "public/" + opt, "target": opt})
        (self.repo / "docs/.pages-manifest.json").write_text(json.dumps(manifest))
        selected = audit.route_inventory(self.repo, requested=[ROUTE, opt])
        self.assertEqual(selected, [ROUTE, opt])


if __name__ == "__main__":
    unittest.main()
