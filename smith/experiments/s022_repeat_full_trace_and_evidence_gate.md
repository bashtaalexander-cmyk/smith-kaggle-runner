# S022 — correction: repeat traces recovered, four FAIL chains, evidence gate

UTC: 2026-11-25T10:20:00Z

## Correction to S020

The extracted official artifact for repeat run 45332756251 **does contain** six non-empty trace JSON files under `output/results/traces/`. The earlier S020 statement that no trace JSON was present was incorrect and is superseded by this report.

Evidence:

- Run: https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/actions/runs/45332756251
- Artifact ID: `14895580037`
- Artifact digest: `sha256:e41ca50cf0afc5081a6d7ad666a8b354ab98336b3b49995fc5ee8cbca9639802`
- Candidate SHA-256: `89d20b0bce4413459a18cdb4f89c4d726897d3e7a3dfad9df1f72e18e27e9c1a`
- Official repeat result: 2/6 PASS — `rich_3454`, `rich_3063`.
- Official FAIL — `fastapi_14609` exit 2, `requests_7328` exit 1, `fastapi_15763` exit 1, `requests_7309` exit 1.
- Model path in traces: `/kaggle/input/models/google/gemma-4/other/gemma-4-31b-it-qat-w4a16-ct/2`.

## Reconstructed repeat FAIL chains

| Task | Locate → file | First successful production modification | edit/write failures | Verification | Submit / diff | Official verdict | First confirmed failure mechanism | Missing data |
|---|---|---:|---:|---|---|---|---|---|
| `fastapi_14609` | listed `fastapi/_compat`; removed `v1.py` and `may_v1.py` at 51.5 s; inspected v2 helpers | 276.7 s, full `write_file` replacement of `fastapi/_compat/main.py` | no schema failures; redundant second `rm` exit 1 | no test. At 337.8 s `grep "_normalize_errors" fastapi/_compat/v2.py` exited 1; no repair before submit | 346.1 s; 19,004-byte diff, 3 files | FAIL, exit 2 | Confirmed workflow defect: destructive deletion preceded the replacement by 225 s, first production write was very late, self-check reported a missing expected helper, and no test was run. Exact verifier root cause is not proven because verifier traceback is absent. | verifier stdout/stderr; raw patch; base commit/snapshot |
| `requests_7328` | `src/requests/sessions.py`, 5 calls before first edit | 97.9 s | 0 | scratch repro: initial run used installed package and passed; two later runs failed; corrected `PYTHONPATH=src python3 repro_test.py` passed at 200.5 s | 229.4 s; one production file, 536 bytes | FAIL, exit 1 | No semantic verifier cause is proven. The final source-directed reproduction passed. Earlier failed runs demonstrate environment confusion, not the official failure cause. | official failing assertion/traceback; raw patch; base |
| `fastapi_15763` | searched `fastapi/routing.py`, identified `self.prefix + path` | 280.3 s via `python3 fix_routing.py` after shell helper write | 10 consecutive `edit_file` calls missing `old_string` from 195.5–271.5 s; final write hit budget | no focused test after production modification | 303.2 s; 2,195-byte diff, 3 files including scratch helpers | FAIL, exit 1 | Confirmed tool-reliability failure: ten identical schema errors delayed the first real production modification until 280.3 s; no post-edit behavioral verification remained. Verifier's semantic cause is not present. | verifier traceback; raw patch; exact base |
| `requests_7309` | `src/requests/utils.py`, tests; 17 calls before first production edit | 98.0 s | one malformed `edit_file` missing both strings at 89.9 s, then recovery | `PYTHONPATH=src pytest tests/test_utils.py` and targeted test both passed at 132.7/137.0 s | 139.6 s; 1,506-byte diff, 2 files; scratch `reproduce_issue.py` included | FAIL, exit 1 | No official semantic cause is proven. Corrected source-directed reproduction and public tests passed; scratch contamination is confirmed but not proven causal. | official assertion/traceback; raw patch; exact base |

## PASS observations relevant to mechanism

- `rich_3063` changed production at 397.0 and 406.0 s after three missing-`old_string` errors and one old-string mismatch, then officially PASS. Slow/fragile editing is real but not necessarily fatal.
- `rich_3454` officially PASS despite 11 rejected edit attempts. Therefore malformed edit count alone does not determine verdict; the ablation should target repeated identical failures and recovery time, not merely count any rejection.

## One-variable experiment choice

1. **First:** schema-grounded edit recovery only. Trigger after two equivalent missing-argument failures; reconstruct the complete `filepath/old_string/new_string` object from the last exact read, or use the already-allowed shell fallback once. Measure rejection streak, time to recovery, first production edit, final diff, official PASS. This is directly supported by `fastapi_15763`.
2. **Later and separate:** search/localization cap. Supported by `fastapi_14609` first production write at 276.7 s and no verification time. Do not combine with edit recovery.
3. Do not tune semantic logic for `requests_7328` or `requests_7309` until official verifier output is preserved.

## CPU evidence contract

Added `s022_evidence_contract.py`, a fail-closed audit for future evidence bundles. It checks:

- unique complete verdict rows;
- non-empty trace per task;
- raw patch file plus SHA-256 sidecar;
- per-task verifier output;
- evaluator/image/model/model-revision/agent/config metadata;
- private exact base commits without printing their values.

Actual audit results:

- Baseline artifact: traces 6/6, but predictions-only rows lack official verdict fields; raw patches 0/6; verifier outputs 0/6; run metadata and private bases missing.
- Repeat artifact: verdict rows complete and traces 6/6; raw patches 0/6; verifier outputs 0/6; run metadata and private bases missing.
- Both bundles correctly fail the completeness gate. This does not alter their official PASS/FAIL.

Script: https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/blob/877171472d70a15b55430768355fef7f77524dc8/smith/experiments/s022_evidence_contract.py

No GPU, endpoint, paid service, submission, or old-version mutation was used. No new official verdict was produced; the last confirmed candidate remains 2/6.
