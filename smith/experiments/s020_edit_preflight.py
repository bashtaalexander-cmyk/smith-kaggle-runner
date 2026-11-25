"""CPU-only validation for deterministic text edits and saved evaluator rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_EDIT_KEYS = {"filepath", "old_string", "new_string"}


def validate_edit(arguments: Any, file_text: str) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise ValueError("edit arguments must be a JSON object")
    if set(arguments) != REQUIRED_EDIT_KEYS:
        missing = sorted(REQUIRED_EDIT_KEYS - set(arguments))
        extra = sorted(set(arguments) - REQUIRED_EDIT_KEYS)
        raise ValueError(f"edit argument keys mismatch; missing={missing}; extra={extra}")
    if not all(isinstance(arguments[key], str) for key in REQUIRED_EDIT_KEYS):
        raise ValueError("filepath, old_string and new_string must be strings")
    if not arguments["filepath"] or arguments["filepath"].startswith("/"):
        raise ValueError("filepath must be workspace-relative")
    if not arguments["old_string"]:
        raise ValueError("old_string must be non-empty")

    occurrences = file_text.count(arguments["old_string"])
    if occurrences != 1:
        raise ValueError(f"old_string must match exactly once; matches={occurrences}")

    result = file_text.replace(arguments["old_string"], arguments["new_string"], 1)
    return {
        "filepath": arguments["filepath"],
        "old_string_sha256": hashlib.sha256(
            arguments["old_string"].encode("utf-8")
        ).hexdigest(),
        "new_file_sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "changed": result != file_text,
    }


def audit_verdict_rows(path: Path) -> list[dict[str, Any]]:
    audited = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        row = json.loads(line)
        task_id = row.get("id")
        patch = row.get("prediction")
        if not isinstance(task_id, str) or not isinstance(patch, str):
            raise ValueError(f"row {number}: id and prediction must be strings")
        files = []
        for patch_line in patch.splitlines():
            if patch_line.startswith("diff --git a/"):
                parts = patch_line.split()
                if len(parts) != 4:
                    raise ValueError(f"row {number}: malformed diff header")
                files.append(parts[2][2:])
        scratch = [
            name
            for name in files
            if Path(name).name.startswith(("repro", "debug", "fix_", "test"))
        ]
        audited.append(
            {
                "id": task_id,
                "resolved": row.get("resolved"),
                "test_exit_code": row.get("test_exit_code"),
                "duration_seconds": row.get("duration_seconds"),
                "tool_calls": row.get("tool_calls"),
                "patch_sha256": hashlib.sha256(patch.encode("utf-8")).hexdigest(),
                "files": files,
                "scratch_files": scratch,
                "trace_path_recorded": row.get("trace_path"),
            }
        )
    return audited


def self_test() -> None:
    original = "alpha = 1\nbeta = 2\n"
    valid = {
        "filepath": "pkg/module.py",
        "old_string": "beta = 2",
        "new_string": "beta = 3",
    }
    assert validate_edit(valid, original)["changed"]

    invalid = [
        ({"filepath": "pkg/module.py", "old_string": "alpha = 1"}, "keys"),
        (
            {
                "filepath": "pkg/module.py",
                "old_string": "missing",
                "new_string": "replacement",
            },
            "matches=0",
        ),
        (
            {
                "filepath": "pkg/module.py",
                "old_string": "x",
                "new_string": "y",
            },
            "matches=2",
        ),
        (
            {
                "filepath": "/workspace/pkg/module.py",
                "old_string": "alpha = 1",
                "new_string": "alpha = 2",
            },
            "workspace-relative",
        ),
        (
            {
                "filepath": "pkg/module.py",
                "old_string": 1,
                "new_string": "alpha = 2",
            },
            "must be strings",
        ),
    ]
    sources = [original, original, "xx", original, original]
    for (arguments, expected), source in zip(invalid, sources, strict=True):
        try:
            validate_edit(arguments, source)
        except ValueError as error:
            assert expected in str(error), (expected, str(error))
        else:
            raise AssertionError(f"expected validation failure: {arguments}")
    print("6/6 edit preflight CPU cases passed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--verdicts", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.verdicts:
        print(json.dumps(audit_verdict_rows(args.verdicts), indent=2, sort_keys=True))
    if not args.self_test and not args.verdicts:
        parser.error("choose --self-test and/or --verdicts")


if __name__ == "__main__":
    main()
