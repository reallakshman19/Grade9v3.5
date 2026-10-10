#!/usr/bin/env python3
"""Read back actual GitHub Pages bytes for selected routes; not a release grant.

The repository's docs/ directory is the expected source and GitHub Pages is
a separate observable deployment. This audit verifies sampled HTTP pages,
not the entire deployment or academic/Owner approval.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

REPO = Path(__file__).resolve().parents[2]
DEFAULT_URL = "https://reallakshman19.github.io/Grade9v3.5/"
DEFAULT_PATHS = (
    "index.html",
    "mathematics/index.html",
    "mathematics/imo-grade9/index.html",
)
OPTIONAL_ROUTES = (
    "mathematics/number-systems/index.html",
    "mathematics/number-systems/index-laws/index.html",
)
SHA = re.compile(r"^[0-9a-f]{40}$")
MAX_BYTES = 4 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = build_opener(NoRedirect)


def valid_route(path: str) -> str:
    if not isinstance(path, str) or not path or "\\" in path or "%" in path:
        raise ValueError("route must be a plain relative path")
    parsed = urlsplit(path)
    parts = PurePosixPath(path).parts
    if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
        or path.startswith("/") or ".." in parts or "." in parts
        or not path.endswith(".html") or path.endswith("//")
        or any(x in {"", ".", ".."} for x in path.split("/"))):
        raise ValueError("unsafe or unsupported route")
    return path


def valid_base(url: str, *, allow_loopback: bool = False) -> str:
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    if (not url.endswith("/") or parsed.username or parsed.password
        or parsed.query or parsed.fragment or not parsed.path.startswith("/")
        or not parsed.path.endswith("/") or "//" in parsed.path or
        any(x in {".", ".."} for x in parsed.path.split("/"))):
        raise ValueError("invalid Pages project-base URL")
    # Loopback is an explicit API-only fixture feature; the CLI has no flag
    # exposing it to a production workflow.
    if allow_loopback and parsed.scheme == "http" and host in {"127.0.0.1", "localhost"}:
        return url
    if parsed.port or parsed.scheme != "https" or not host.endswith(".github.io"):
        raise ValueError("external verification requires a HTTPS github.io Pages origin")
    if not re.fullmatch(r"/[A-Za-z0-9_.-]+/", parsed.path):
        raise ValueError("project Pages URL must be an explicit single project path")
    if parsed.path.lower().startswith("/../"):
        raise ValueError("path traversal")
    return url


def route_inventory(repo: Path, requested: list[str] | None = None) -> list[str]:
    docs = repo / "docs"
    manifest = json.loads((docs / ".pages-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "grade9v3-pages-mirror-v1":
        raise ValueError("missing or unexpected Pages projection manifest")
    indexed = {r["target"] for r in manifest["files"] if isinstance(r, dict) and isinstance(r.get("target"), str)}
    routes = list(requested) if requested else list(DEFAULT_PATHS) + [
        r for r in OPTIONAL_ROUTES if (docs / r).is_file()
    ]
    if not routes:
        raise ValueError("at least one route required")
    if len(set(routes)) != len(routes):
        raise ValueError("duplicate route in audit")
    for route in routes:
        valid_route(route)
        if route not in indexed or not (docs / route).is_file():
            raise ValueError(f"route is not present in the committed Pages manifest and docs: {route}")
        if not (docs / route).resolve().is_relative_to(docs.resolve()):
            raise ValueError("route symlink escapes docs/")
    return routes


def _get(url: str, *, bypass: bool, max_bytes: int = MAX_BYTES) -> dict:
    headers = {"Accept": "text/html", "Accept-Encoding": "identity",
               "User-Agent": "Grade9V35-Pages-Readback/1"}
    if bypass:
        headers["Cache-Control"] = "no-cache"
    request = Request(url, headers=headers)
    observation = {"url": url, "status": None, "content_type": None,
                   "sha256": None, "bytes": None, "error": None}
    try:
        with _OPENER.open(request, timeout=12) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower().strip()
            encoding = response.headers.get("Content-Encoding", "identity").lower().strip()
            content = response.read(max_bytes + 1)
            observation.update(status=status, content_type=content_type,
                               bytes=len(content),
                               sha256=hashlib.sha256(content).hexdigest(),
                               cache_control=response.headers.get("Cache-Control"),
                               age=response.headers.get("Age"),
                               etag=response.headers.get("ETag"))
            if response.geturl() != url:
                observation["error"] = "REDIRECTED"
            elif encoding not in {"", "identity"}:
                observation["error"] = "ENCODED_RESPONSE_NOT_EXACT_BYTES"
            elif len(content) > max_bytes:
                observation["error"] = "OVERSIZED_RESPONSE"
    except HTTPError as exc:
        observation["status"] = exc.code
        observation["error"] = "HTTP_" + str(exc.code)
    except (URLError, OSError, TimeoutError, ValueError) as exc:
        observation["error"] = "NETWORK_" + type(exc).__name__
    return observation


def audit(repo: Path = REPO, base_url: str = DEFAULT_URL, *,
          expected_sha: str, paths: list[str] | None = None,
          attempts: int = 1, delay: float = 0,
          allow_loopback: bool = False) -> dict:
    if not SHA.fullmatch(expected_sha):
        raise ValueError("expected commit must be an exact 40-character SHA")
    valid_base(base_url, allow_loopback=allow_loopback)
    if not 1 <= attempts <= 20 or not 0 <= delay <= 60:
        raise ValueError("invalid retry settings")
    repo = Path(repo)
    routes = route_inventory(repo, paths)
    rows = {}
    pending = set(routes)
    for attempt in range(1, attempts + 1):
        for route in routes:
            if route not in pending:
                continue
            expected = (repo / "docs" / route).read_bytes()
            digest = hashlib.sha256(expected).hexdigest()
            url = base_url + "/".join(quote(part, safe="-._~") for part in route.split("/"))
            # Busted URL never substitutes for a valid ordinary learner URL.
            bust_url = url + "?g9_readback=" + expected_sha
            standard = _get(url, bypass=False)
            bypass = _get(bust_url, bypass=True)
            checks = {}
            for mode, observed in (("normal", standard), ("cache_busted", bypass)):
                checks[mode] = (
                    observed.get("status") == 200 and
                    observed.get("content_type") == "text/html" and
                    observed.get("sha256") == digest and
                    observed.get("bytes") == len(expected) and
                    observed.get("error") is None
                )
            passed = all(checks.values())
            rows[route] = {
                "path": route, "status": "PASS" if passed else "FAIL",
                "attempts": attempt, "expected_sha256": digest,
                "expected_bytes": len(expected), "checks": checks,
                "observations": {"normal": standard, "cache_busted": bypass}
            }
            if passed:
                pending.remove(route)
        if not pending:
            break
        if attempt < attempts and delay:
            time.sleep(delay)
    return {
        "schema": "grade9v35-deployed-pages-readback/v1",
        "scope": "SELECTED_ROUTES_ONLY_NOT_RELEASE_AUTHORITY",
        "status": "PASS" if not pending else "FAIL",
        "expected_commit_sha": expected_sha,
        "base_url": base_url,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "paths": [rows[p] for p in routes],
        "failed_routes": sorted(pending)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default=DEFAULT_URL)
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--path", action="append", dest="paths",
                        help="selected docs HTML path; repeat for multiple")
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0)
    parser.add_argument("--output", type=Path, default=Path("build/pages-readback/report.json"))
    args = parser.parse_args()
    try:
        result = audit(args.root, args.base_url, expected_sha=args.expected_sha,
                       paths=args.paths, attempts=args.attempts, delay=args.delay)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {"schema": "grade9v35-deployed-pages-readback/v1", "status": "FAIL",
                  "scope": "SELECTED_ROUTES_ONLY_NOT_RELEASE_AUTHORITY",
                  "expected_commit_sha": args.expected_sha,
                  "base_url": args.base_url,
                  "error": "CONFIG_" + type(exc).__name__ + ": " + str(exc),
                  "paths": []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
