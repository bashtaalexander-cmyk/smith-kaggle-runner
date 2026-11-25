#!/usr/bin/env python3
"""CPU regression for the fail-closed replacement prescribed by S023."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path, PurePosixPath


class ReplaceRejected(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_replace(workspace: Path, relative: str, old: bytes, new: bytes) -> dict:
    path_spec = PurePosixPath(relative)
    if path_spec.is_absolute() or ".." in path_spec.parts or not path_spec.parts:
        raise ReplaceRejected("path must be workspace-relative without traversal")
    if not isinstance(old, bytes) or not isinstance(new, bytes) or not old:
        raise ReplaceRejected("old/new must be bytes and old must be non-empty")

    root = workspace.resolve()
    candidate = root / Path(*path_spec.parts)
    if candidate.is_symlink():
        raise ReplaceRejected("target must not be a symlink")
    target = candidate.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ReplaceRejected("target escaped workspace") from exc
    if not target.is_file():
        raise ReplaceRejected("target must be an existing regular non-symlink file")

    original = target.read_bytes()
    count = original.count(old)
    if count != 1:
        raise ReplaceRejected(f"expected exactly one match, found {count}")

    changed = original.replace(old, new, 1)
    if changed == original:
        raise ReplaceRejected("replacement was a no-op")

    before_mode = target.stat().st_mode
    temp = target.with_name(f".{target.name}.smith-edit-{os.getpid()}.tmp")
    try:
        with temp.open("xb") as stream:
            stream.write(changed)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, before_mode)
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)

    return {
        "relative_path": relative,
        "match_count": count,
        "before_sha256": digest(original),
        "after_sha256": digest(changed),
        "before_size": len(original),
        "after_size": len(changed),
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        def case(name: str, original: bytes, old: bytes, new: bytes) -> dict:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(original)
            return exact_replace(root, name, old, new)

        report = case("one.py", b"a = 1\nb = 2\n", b"b = 2", b"b = 3")
        assert report["match_count"] == 1
        assert (root / "one.py").read_bytes() == b"a = 1\nb = 3\n"

        report = case("crlf.py", b"a = 1\r\nb = 2\r\n", b"b = 2", b"b = 3")
        assert report["match_count"] == 1
        assert (root / "crlf.py").read_bytes() == b"a = 1\r\nb = 3\r\n"

        for name, original, old in [
            ("zero.py", b"a = 1\n", b"missing"),
            ("many.py", b"x\nx\n", b"x"),
        ]:
            path = root / name
            path.write_bytes(original)
            before = digest(path.read_bytes())
            try:
                exact_replace(root, name, old, b"z")
            except ReplaceRejected:
                pass
            else:
                raise AssertionError(f"{name}: rejection expected")
            assert digest(path.read_bytes()) == before

        for bad in ["/tmp/out.py", "../out.py", "nested/../../out.py"]:
            try:
                exact_replace(root, bad, b"x", b"y")
            except ReplaceRejected:
                pass
            else:
                raise AssertionError(f"{bad}: path rejection expected")

        target = root / "real.py"
        target.write_bytes(b"x\n")
        link = root / "link.py"
        link.symlink_to(target)
        try:
            exact_replace(root, "link.py", b"x", b"y")
        except ReplaceRejected:
            pass
        else:
            raise AssertionError("symlink rejection expected")
        assert target.read_bytes() == b"x\n"

    print("8/8 exact-replacement CPU regressions passed")


if __name__ == "__main__":
    self_test()
