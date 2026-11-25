"""Write lossless JSONL records from evaluator patch results."""
import argparse
import hashlib
import json
import sys


def patch_record(raw: str | None) -> dict:
    return {
        "agent_patch": raw,
        "patch_sha256": None if raw is None else hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "patch_nonempty": bool(raw and raw.strip()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        samples = (None, "", " \r\n", "@@\n x\n \n", "@@\r\n x\r\n \r\n")
        for patch in samples:
            record = json.loads(json.dumps(patch_record(patch)))
            assert record["agent_patch"] == patch
            assert record["patch_nonempty"] == bool(patch and patch.strip())
            expected = None if patch is None else hashlib.sha256(patch.encode("utf-8")).hexdigest()
            assert record["patch_sha256"] == expected
        print(f"{len(samples)}/{len(samples)} raw patch records round-tripped")
        return

    for line in sys.stdin:
        row = json.loads(line)
        raw = row["agent_patch"]
        if raw is not None and not isinstance(raw, str):
            raise ValueError("agent_patch must be a string or null")
        row.update(patch_record(raw))
        print(json.dumps(row))


if __name__ == "__main__":
    main()
