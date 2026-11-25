#!/usr/bin/env python3
"""Independent static verifier for the immutable S023 Drive artifact."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import PurePosixPath
import zipfile

import yaml


EXPECTED = {
    "agent.yaml": "badf35f7a37dc35513c7af73a53452e26ef34359",
    "eval_config.yaml": "43a1b2a4b410cb70b18de52f3175b0af54efc6bb",
    "system.md": "cc4dc3ef7fcc28ccddbc5e3a78d72ab5740bc3c1",
    "README.md": "cf1dd2a6a75c562214387037fd22e73f57d36a92",
}
EXPECTED_ZIP_SHA256 = "7fc91e660435fbc7e7cce1a0f744a77d8628db2b3b21d8f3688876ac298893e7"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def verify(path: str) -> dict:
    raw = open(path, "rb").read()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_ZIP_SHA256
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert set(names) == set(EXPECTED)
        assert names[0] == "agent.yaml"
        for name in names:
            parsed = PurePosixPath(name)
            assert not parsed.is_absolute() and ".." not in parsed.parts
            assert not name.endswith("/")
            assert git_blob_sha(archive.read(name)) == EXPECTED[name]

        class Loader(yaml.SafeLoader):
            pass

        Loader.add_constructor(
            "!include", lambda loader, node: archive.read(loader.construct_scalar(node)).decode()
        )
        agent = yaml.load(archive.read("agent.yaml"), Loader=Loader)
        config = yaml.safe_load(archive.read("eval_config.yaml"))

    assert agent["model"] == "gemma-4-31b-it-qat-w4a16-ct"
    assert agent["tools"] == [
        "run_command", "read_file", "edit_file", "write_file", "submit_patch"
    ]
    instruction = agent["instruction"]
    assert "same argument error occurs a second time" in instruction
    assert "requires old_string to occur exactly once" in instruction
    assert "Never use the fallback for an ambiguous match" in instruction
    limits = config["evaluation"]
    assert limits == {
        "timeout_seconds": 180,
        "verification_timeout_seconds": 180,
        "max_tool_calls": 24,
        "max_time_minutes": 30,
    }
    return {
        "zip_sha256": EXPECTED_ZIP_SHA256,
        "zip_size": len(raw),
        "files": names,
        "model": agent["model"],
        "tools": agent["tools"],
        "limits": limits,
        "source_blob_parity": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("zip")
    args = parser.parse_args()
    import json
    print(json.dumps(verify(args.zip), indent=2, sort_keys=True))
