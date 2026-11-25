# S029 — lossless raw-patch checkpoint infrastructure

UTC: 2026-11-25

## Confirmed gap

`s018_patch_export.py` preserves an `agent_patch` string inside JSON, but it does not create the `raw_patches/<id>.patch` and `.sha256` files required by `s022_evidence_contract.py`. Therefore the evidence contract and exporter were not connected end-to-end.

## Implemented infrastructure-only fix

Added `s029_raw_patch_checkpoint.py`. It:

- accepts `agent_patch` (or legacy `prediction`) without `.strip()` or newline normalization;
- encodes the evaluator-provided Python string exactly once as UTF-8;
- writes `<id>.patch`, `<id>.sha256`, and a manifest atomically with `fsync`;
- validates the complete batch before writing;
- rejects unsafe task IDs, duplicates, and non-string patches;
- treats `None` as an explicit zero-byte checkpoint and records byte length separately from semantic patch validity.

This is evidence infrastructure. It cannot change an official verdict and is not part of S023.

## CPU regression result

`python s029_raw_patch_checkpoint.py --self-test`

Result: **9/9 PASS**. Exact byte equality was checked for LF, CRLF plus trailing spaces/blank lines, Unicode, whitespace-only, empty string, and null. Three fail-closed cases covered path traversal, duplicate IDs, and invalid patch type. Source SHA-256:

`367938bc036804639611d3a8eb802f8118d82c1ebf8abb87ce33e84b203e8021`

## Historical bundle replay

The script checkpointed all six prediction strings from both available artifacts:

- baseline reconstructed manifest: 6 patches, 10,925 bytes, manifest SHA-256 `97b3d125efedc0444dbccb20784cf603a2f5fa417b99df8d3911eb67cf469848`;
- repeat reconstructed manifest: 6 patches, 26,663 bytes, manifest SHA-256 `38c3fdab34922d9395c38d6fca29c917385b1aa735999fe093771d5b4e3ca74d`.

These are explicitly **reconstructed checkpoints from `predictions.jsonl`**, not proof of the original pre-export `agent_patch` bytes. Exact historical rawness cannot be recovered after the fact. Future runner integration must call the checkpoint before any transformation and before artifact packaging.

## Causality boundary

No evidence shows that `.strip()` caused an evaluator FAIL. Official verification occurred before this evidence export path. The change only improves auditability and exact-base replay readiness for future runs.

## Remaining blocker for exact-base replay

`git apply --check` against the exact repository state still requires the private base commit for each task and a clean checkout at that commit. Those values are absent from the two public artifacts, so only patch-format/checkpoint tests are currently justified.
