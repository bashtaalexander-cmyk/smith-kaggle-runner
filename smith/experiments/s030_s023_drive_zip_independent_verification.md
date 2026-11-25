# S030 — independent verification of the immutable S023 Drive ZIP

UTC: 2026-11-25

The Drive artifact `smith_s023_edit_recovery_cpu_validated.zip` was downloaded again by file ID and verified independently rather than trusting the creation log.

## Results

- size: 1,755 bytes;
- SHA-256: `7fc91e660435fbc7e7cce1a0f744a77d8628db2b3b21d8f3688876ac298893e7`;
- CRC: all entries valid (`ZipFile.testzip() is None`);
- exact root entries: `agent.yaml`, `eval_config.yaml`, `system.md`, `README.md`;
- no duplicate, absolute, parent-traversal, directory, or extra entries;
- `agent.yaml` is first and at archive root;
- every extracted file's Git blob SHA exactly matches the corresponding file in GitHub commit history;
- `!include system.md` resolves;
- exact model: `gemma-4-31b-it-qat-w4a16-ct`;
- tools: `run_command`, `read_file`, `edit_file`, `write_file`, `submit_patch`;
- limits: 180-second task and verification timeouts, 24 tool calls, 30 minutes;
- prompt contains the single intended change: after a second identical argument error, one allowed `run_command` fallback requiring exactly one match and rejecting ambiguity.

Verifier: `s030_verify_candidate_zip.py`, SHA-256 `e99d26a6abe69133d46920506cb65fe5c28eb2f61f7cb56e0ae92d54589fdc38`.

Captured log SHA-256: `9dc330ad07ac5e45e29c60f9d1d05426add5ac29c057cb0364d59e0494eb8e25`.

## Boundary

This proves Drive/GitHub source parity and static packaging/configuration validity. The official Kaggle compiler is not installed in the current CPU workspace, so this is not an official compile claim. S023 has no official evaluator verdict because the prior GPU push was rejected before execution by the weekly quota.

No S023 bytes or historical artifact were changed.
