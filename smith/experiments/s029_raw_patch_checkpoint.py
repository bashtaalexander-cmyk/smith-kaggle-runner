#!/usr/bin/env python3
"""Checkpoint evaluator agent_patch strings as exact UTF-8 bytes.

This is evidence infrastructure, not an evaluator or an agent improvement.
It intentionally never strips, normalizes, or applies a patch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def checkpoint(rows: list[dict], output: Path) -> list[dict]:
    seen: set[str] = set()
    prepared: list[tuple[str, bytes, str]] = []
    for row in rows:
        task_id = row.get("id") or row.get("instance_id")
        if not isinstance(task_id, str) or not SAFE_ID.fullmatch(task_id):
            raise ValueError("unsafe or missing task id")
        if task_id in seen:
            raise ValueError(f"duplicate task id: {task_id}")
        seen.add(task_id)
        raw = row.get("agent_patch", row.get("prediction"))
        if raw is not None and not isinstance(raw, str):
            raise ValueError(f"agent_patch must be string or null: {task_id}")
        payload = b"" if raw is None else raw.encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        prepared.append((task_id, payload, digest))

    # Validate the complete batch before writing any output.
    output.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    for task_id, payload, digest in prepared:
        atomic_write(output / f"{task_id}.patch", payload)
        atomic_write(output / f"{task_id}.sha256", (digest + "\n").encode("ascii"))
        manifest.append(
            {
                "id": task_id,
                "byte_length": len(payload),
                "patch_sha256": digest,
                "patch_nonempty": bool(payload),
            }
        )
    atomic_write(
        output / "manifest.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return manifest


def self_test() -> None:
    samples = {
        "lf": "diff --git a/a b/a\n+line\n",
        "crlf": "diff --git a/a b/a\r\n+line  \r\n\r\n",
        "unicode": "diff --git a/a b/a\n+é漢字\n",
        "spaces": " \t\r\n",
        "empty": "",
        "null": None,
    }
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        rows = [{"id": key, "agent_patch": value} for key, value in samples.items()]
        manifest = checkpoint(rows, root / "raw_patches")
        assert len(manifest) == len(samples)
        for key, value in samples.items():
            expected = b"" if value is None else value.encode("utf-8")
            actual = (root / "raw_patches" / f"{key}.patch").read_bytes()
            assert actual == expected
            digest = hashlib.sha256(expected).hexdigest()
            assert (root / "raw_patches" / f"{key}.sha256").read_text().strip() == digest

        before = sorted(p.name for p in (root / "raw_patches").iterdir())
        for bad_rows in (
            [{"id": "../escape", "agent_patch": "x"}],
            [{"id": "dup", "agent_patch": "x"}, {"id": "dup", "agent_patch": "y"}],
            [{"id": "badtype", "agent_patch": 7}],
        ):
            try:
                checkpoint(bad_rows, root / "should_not_write")
            except ValueError:
                pass
            else:
                raise AssertionError("invalid batch accepted")
            assert not (root / "should_not_write").exists()
        assert before == sorted(p.name for p in (root / "raw_patches").iterdir())
    print("9/9 raw patch checkpoint regressions passed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path, nargs="?")
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.jsonl is None or args.output is None:
        parser.error("jsonl and output are required unless --self-test is used")
    rows = [json.loads(line) for line in args.jsonl.read_text(encoding="utf-8").splitlines() if line]
    manifest = checkpoint(rows, args.output)
    print(json.dumps({"task_count": len(manifest), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
