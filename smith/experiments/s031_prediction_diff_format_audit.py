#!/usr/bin/env python3
"""Audit exported prediction diff syntax without claiming exact-base applicability."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def parse(payload: bytes) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "apply", "--numstat", "--summary", "--allow-binary", "-"],
        input=payload,
        capture_output=True,
        timeout=10,
    )
    return result.returncode, result.stderr.decode(errors="replace")


def audit(path: Path) -> dict:
    raw = path.read_bytes()
    raw_exit, raw_error = parse(raw)
    repair = None
    # Diagnostic reconstruction only: restore the missing terminal newline and
    # the minimum number of whitespace-only context lines likely removed by a
    # prior string strip. Never overwrite or label this as the original patch.
    for blank_context_lines in range(0, 11):
        reconstructed = raw + b"\n" + (b" \n" * blank_context_lines)
        exit_code, error = parse(reconstructed)
        if exit_code == 0:
            repair = {
                "terminal_newline_added": True,
                "blank_context_lines_added": blank_context_lines,
                "reconstructed_sha256": hashlib.sha256(reconstructed).hexdigest(),
            }
            break
    return {
        "path": str(path),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_bytes": len(raw),
        "raw_ends_newline": raw.endswith(b"\n"),
        "raw_parse_exit": raw_exit,
        "raw_error_first_line": raw_error.splitlines()[0] if raw_error else "",
        "minimal_diagnostic_reconstruction": repair,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("patches", nargs="+", type=Path)
    args = parser.parse_args()
    rows = [audit(path) for path in args.patches]
    print(json.dumps(rows, indent=2, sort_keys=True))
    raise SystemExit(0 if all(row["minimal_diagnostic_reconstruction"] for row in rows) else 2)
