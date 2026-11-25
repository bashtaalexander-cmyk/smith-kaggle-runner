"""Check a saved diff against an explicitly pinned clean Git snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def check(repo: Path, expected: str, patch: bytes) -> dict:
    def git(*args, **kwargs):
        return subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, timeout=30, **kwargs
        )

    if not re.fullmatch(r"[0-9a-f]{40}", expected):
        raise ValueError("Expected a full lowercase base SHA")
    actual = git("rev-parse", "--verify", "HEAD", check=True).stdout.decode().strip()
    if actual != expected:
        raise ValueError("Snapshot HEAD does not match the pinned base")
    if git("status", "--porcelain", check=True).stdout:
        raise ValueError("Snapshot must be clean")
    result = git("apply", "--check", "--index", "-", input=patch)
    return {
        "base_commit": actual,
        "patch_sha256": hashlib.sha256(patch).hexdigest(),
        "apply_exit_code": result.returncode,
        "stderr": result.stderr.decode(errors="replace").strip(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("base_commit")
    parser.add_argument("patch", type=Path)
    args = parser.parse_args()
    result = check(args.repo, args.base_commit, args.patch.read_bytes())
    print(json.dumps(result))
    raise SystemExit(result["apply_exit_code"])
