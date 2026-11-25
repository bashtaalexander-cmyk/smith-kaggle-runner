#!/usr/bin/env python3
"""Extract comparable phase metrics from official swegemma trace JSON files."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


SCRATCH_RE = re.compile(
    r"(^|/)(repro|reproduce|debug|test_|fix_routing)"
)
SEARCH_COMMAND_RE = re.compile(r"\b(git grep|grep|rg|find|ls)\b")
TEST_COMMAND_RE = re.compile(r"\b(pytest|python(?:3)?\s+[^ ]*(?:repro|test|debug))\b")


def observation(step: dict) -> dict:
    raw = (step.get("observation") or {}).get("content", "")
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}


def is_success(value: dict) -> bool:
    return value.get("status") == "ok"


def is_production_path(path: str) -> bool:
    if not path or SCRATCH_RE.search(path):
        return False
    return not path.startswith(("tests/", "test/", "docs/", "examples/"))


def iter_calls(trace: dict):
    for step in trace.get("steps", []):
        obs = observation(step)
        for call in step.get("tool_calls") or []:
            yield {
                "time": (call.get("extra") or {}).get("elapsed_s"),
                "name": call.get("function_name", ""),
                "args": call.get("arguments") or {},
                "obs": obs,
            }


def metrics(path: Path, arm: str) -> dict:
    trace = json.loads(path.read_text(encoding="utf-8"))
    calls = list(iter_calls(trace))
    task_id = path.stem.removeprefix("trace_")

    confirmed_edits = []
    edit_attempts = 0
    edit_rejections = 0
    missing_argument_rejections = 0
    search_calls = 0
    read_calls = 0
    test_calls = 0
    tests_ok = 0
    submit_time = None
    submit_patch_size = None

    for call in calls:
        name, args, obs = call["name"], call["args"], call["obs"]
        command = str(args.get("command", ""))
        if name == "read_file":
            read_calls += 1
        if name == "run_command" and SEARCH_COMMAND_RE.search(command):
            search_calls += 1
        if name == "run_command" and TEST_COMMAND_RE.search(command):
            test_calls += 1
            tests_ok += int(is_success(obs))
        if name in {"edit_file", "write_file"}:
            edit_attempts += 1
            if not is_success(obs):
                edit_rejections += 1
                error = str(obs.get("error") or obs.get("error_message") or "")
                missing_argument_rejections += int("mandatory input parameters" in error)
            elif is_production_path(str(args.get("filepath", ""))):
                confirmed_edits.append(call)
        if name == "submit_patch":
            submit_time = call["time"]
            submit_patch_size = obs.get("patch_size")

    first_edit = confirmed_edits[0]["time"] if confirmed_edits else None
    pre_edit_calls = (
        sum(1 for call in calls if call["time"] is not None and call["time"] < first_edit)
        if first_edit is not None
        else len(calls)
    )

    return {
        "arm": arm,
        "task_id": task_id,
        "trace_steps": len(trace.get("steps", [])),
        "tool_events": len(calls),
        "search_calls": search_calls,
        "read_calls": read_calls,
        "edit_attempts": edit_attempts,
        "edit_rejections": edit_rejections,
        "missing_argument_rejections": missing_argument_rejections,
        "first_confirmed_native_production_edit_s": first_edit,
        "calls_before_first_confirmed_edit": pre_edit_calls,
        "test_calls": test_calls,
        "tests_ok": tests_ok,
        "submit_time_s": submit_time,
        "submit_patch_size": submit_patch_size,
    }


def trace_paths(root: Path) -> list[Path]:
    candidates = [
        root / "results" / "traces",
        root / "output" / "results" / "traces",
    ]
    for directory in candidates:
        paths = sorted(directory.glob("trace_*.json"))
        if paths:
            return paths
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", action="append", nargs=2, metavar=("NAME", "ROOT"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for name, root in args.arm:
        paths = trace_paths(Path(root))
        if not paths:
            raise SystemExit(f"{name}: no traces")
        rows.extend(metrics(path, name) for path in paths)

    fields = list(rows[0])
    if args.output:
        with args.output.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(rows, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
