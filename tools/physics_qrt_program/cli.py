#!/usr/bin/env python3
"""Offline deterministic checks; does not publish, merge, classify science or run agents.

Run from repository root, e.g.:
python3 -m tools.physics_qrt_program.cli validate-lock path.json
python3 -m tools.physics_qrt_program.cli validate-receipt --lock path.json receipt.json
python3 -m tools.physics_qrt_program.cli converge --lock path.json receipt1.json ...
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contracts import validate_lock, validate_receipt, converge
from Physics.adapter.qrt_crosswalk import inspect_question
from .bootstrap import assemble, BootstrapError


def _read(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    lock_parser = sub.add_parser("validate-lock")
    lock_parser.add_argument("lock")
    lock_parser.add_argument("--require-authorized", action="store_true")
    sub.add_parser("bootstrap-w0")
    source = sub.add_parser("inspect-question")
    source.add_argument("--package", required=True)
    source.add_argument("--question", required=True)
    for action in ("validate-receipt", "converge"):
        p = sub.add_parser(action)
        p.add_argument("--lock", required=True)
        p.add_argument("receipts", nargs="+")
    args = parser.parse_args(argv)
    try:
        if args.command == "bootstrap-w0":
            result = assemble()
            code = 0  # Source verification only; status still HOLD.
        elif args.command == "inspect-question":
            result = inspect_question(args.package, args.question)
            code = int(bool(result["errors"]))
        elif args.command == "validate-lock":
            errors = validate_lock(_read(args.lock), require_authorized=args.require_authorized)
            result = {"status": "FAIL" if errors else "STRUCTURE_VALID_NOT_PERMISSION", "errors": errors}
            code = int(bool(errors))
        else:
            lock = _read(args.lock)
            receipts = [_read(path) for path in args.receipts]
            if args.command == "validate-receipt":
                checks = [{"path": path, "errors": validate_receipt(row, lock)}
                          for path, row in zip(args.receipts, receipts)]
                code = int(any(row["errors"] for row in checks))
                result = {"status": "INVALID" if code else "ENVELOPES_VALID_ONLY", "checks": checks}
            else:
                result = converge(lock, receipts)
                code = 0 if result["envelope_ready"] else 1
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        result, code = {"status": "FAIL", "errors": [str(exc)]}, 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
