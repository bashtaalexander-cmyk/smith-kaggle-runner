#!/usr/bin/env python3
"""Fail-closed audit for SMITH evaluator evidence bundles.

This does not evaluate patches.  It checks whether a completed run preserved
enough evidence to support the required failure analysis and exact-base replay.
It never prints base commit values or patch contents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED_RESULT_KEYS = {
    "id",
    "resolved",
    "test_exit_code",
    "duration_seconds",
    "tool_calls",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_rows(root: Path) -> tuple[list[dict], str]:
    candidates = [
        root / "official-verdicts.jsonl",
        root / "output" / "official-verdicts.jsonl",
    ]
    for path in candidates:
        if path.is_file():
            rows = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            return rows, str(path.relative_to(root))

    # A predictions-only export can identify tasks, but cannot prove verdicts.
    for path in [root / "predictions.jsonl", root / "output" / "predictions.jsonl"]:
        if path.is_file():
            rows = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            return rows, str(path.relative_to(root))
    return [], ""


def find_trace(root: Path, task_id: str) -> Path | None:
    names = [
        root / "results" / "traces" / f"trace_{task_id}.json",
        root / "output" / "results" / "traces" / f"trace_{task_id}.json",
    ]
    return next((path for path in names if path.is_file() and path.stat().st_size), None)


def audit(root: Path) -> dict:
    rows, rows_path = load_rows(root)
    ids = [str(row.get("id") or row.get("instance_id") or "") for row in rows]
    ids = [task_id for task_id in ids if task_id]
    duplicate_ids = sorted({task_id for task_id in ids if ids.count(task_id) > 1})
    unique_ids = sorted(set(ids))

    verdict_rows_complete = bool(rows) and all(
        REQUIRED_RESULT_KEYS.issubset(row) for row in rows
    )
    missing_traces = [task_id for task_id in unique_ids if not find_trace(root, task_id)]

    raw_dir = root / "raw_patches"
    raw_missing: list[str] = []
    raw_hash_mismatch: list[str] = []
    for task_id in unique_ids:
        patch = raw_dir / f"{task_id}.patch"
        sidecar = raw_dir / f"{task_id}.sha256"
        if not patch.is_file() or not sidecar.is_file():
            raw_missing.append(task_id)
            continue
        expected = sidecar.read_text(encoding="ascii").strip().lower()
        if expected != sha256(patch):
            raw_hash_mismatch.append(task_id)

    verifier_dir = root / "verifier"
    missing_verifier = [
        task_id
        for task_id in unique_ids
        if not (verifier_dir / f"{task_id}.json").is_file()
        or not (verifier_dir / f"{task_id}.json").stat().st_size
    ]

    metadata_path = root / "run-metadata.json"
    metadata_ok = False
    metadata_missing_keys: list[str] = []
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        required = {
            "evaluator_version",
            "image_version",
            "model_name",
            "model_revision",
            "agent_sha256",
            "eval_config_sha256",
        }
        metadata_missing_keys = sorted(required - set(metadata))
        metadata_ok = not metadata_missing_keys
    else:
        metadata_missing_keys = ["run-metadata.json"]

    # Exact values stay in a private file.  Only presence/cardinality is reported.
    bases_path = root / "private-base-commits.json"
    bases_ok = False
    if bases_path.is_file():
        bases = json.loads(bases_path.read_text(encoding="utf-8"))
        bases_ok = set(bases) == set(unique_ids) and all(
            isinstance(value, str)
            and len(value) == 40
            and all(ch in "0123456789abcdefABCDEF" for ch in value)
            for value in bases.values()
        )

    failures = []
    if not rows:
        failures.append("missing_result_rows")
    if duplicate_ids:
        failures.append("duplicate_task_ids")
    if not verdict_rows_complete:
        failures.append("verdict_rows_incomplete")
    if missing_traces:
        failures.append("missing_traces")
    if raw_missing:
        failures.append("missing_raw_patches")
    if raw_hash_mismatch:
        failures.append("raw_patch_hash_mismatch")
    if missing_verifier:
        failures.append("missing_verifier_outputs")
    if not metadata_ok:
        failures.append("missing_run_metadata")
    if not bases_ok:
        failures.append("missing_private_base_commits")

    return {
        "root": str(root),
        "rows_path": rows_path,
        "task_count": len(unique_ids),
        "duplicate_ids": duplicate_ids,
        "verdict_rows_complete": verdict_rows_complete,
        "missing_trace_count": len(missing_traces),
        "missing_raw_patch_count": len(raw_missing),
        "raw_patch_hash_mismatch_count": len(raw_hash_mismatch),
        "missing_verifier_count": len(missing_verifier),
        "metadata_ok": metadata_ok,
        "metadata_missing_keys": metadata_missing_keys,
        "private_base_commits_ok": bases_ok,
        "failures": failures,
        "complete": not failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    result = audit(args.bundle.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
