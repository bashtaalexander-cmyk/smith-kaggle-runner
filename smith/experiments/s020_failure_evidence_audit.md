# S020 failure evidence audit and CPU edit preflight

UTC 2026-11-25T08:24:42Z

Source run: https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/actions/runs/45332756251  
Artifact: `smith-edit-args-31b-evidence`, ID 14895580037, digest `sha256:e41ca50cf0afc5081a6d7ad666a8b354ab98336b3b49995fc5ee8cbca9639802`  
Candidate SHA-256: `89d20b0bce4413459a18cdb4f89c4d726897d3e7a3dfad9df1f72e18e27e9c1a`

## Verified official result

| task | verdict | test exit | calls | seconds | patch SHA-256 |
|---|---:|---:|---:|---:|---|
| rich_3454 | PASS | 0 | 21 | 235.3 | d5605880e59a82543e422f8323801ee3b72449bdcad01d38af5e407ddaa4b613 |
| fastapi_14609 | FAIL | 2 | 24 | 354.6 | 0c3ec01149706c28a16ae2f22756b44c981822864ca46de3d526e87d0d291690 |
| requests_7328 | FAIL | 1 | 19 | 304.5 | 15995da9ed071ddad239645658c4ccea15d4a4223662b1b5d887add9bb8d2bcc |
| rich_3063 | PASS | 0 | 23 | 591.7 | faeed148d6a2f84253fd0d72fcad2c803d04e38db66b39ab53ad4e028235d220 |
| fastapi_15763 | FAIL | 1 | 24 | 307.6 | 5da36e1ffd83a581b9c81a734bcd8594896d6b5a1cf4d322baaa3f0668a65d4f |
| requests_7309 | FAIL | 1 | 24 | 149.1 | 404f3eb296b52214e4846d57a41360a91029ef96beaa26d8b3e114d9cb0dc659 |

## Required FAIL chain audit

The artifact records `trace_path` for every task but does not contain any `results/traces/*.json` file. The notebook log contains task boundaries, two missing-tool warnings and final verdict summaries. It does not contain read/edit/test call payloads. Consequently, file discovery, first successful edit, edit_file failures, final submit call and test traceback cannot be reconstructed for four FAIL tasks from this artifact.

| task | first confirmed failure evidence | confirmed chain evidence | data required to establish the underlying cause |
|---|---|---|---|
| fastapi_14609 | At 98.3 s after task start, `grep_search` was called twice although it was not registered. Harness listed only run_command, read_file, edit_file, write_file and submit_patch. Official verification later exited 2. | Final patch changed three compatibility files, used all 24 calls and removed broad Pydantic v1 support. | Original trace JSON, Phase-2 traceback, timestamps for search/read/edit/test/submit, exact raw agent_patch and base_commit. |
| requests_7328 | Official verification exited 1 after a one-line production patch. | 19 calls, 304.5 s, no scratch file in exported diff. | Original trace JSON and Phase-2 failing assertion are required. The semantic cause is unknown. |
| fastapi_15763 | Official verification exited 1. Exported diff includes `fix_routing.py` and `reproduce_issue.py` alongside production code. | Used all 24 calls in 307.6 s. Scratch contamination is confirmed, but it does not prove why tests failed. | Original trace JSON, Phase-2 traceback, raw patch, base_commit and submit timestamp. |
| requests_7309 | Official verification exited 1. Exported diff includes `reproduce_issue.py`. | Used all 24 calls in 149.1 s. Scratch contamination is confirmed, while the failing assertion is unavailable. | Original trace JSON, Phase-2 traceback, raw patch, base_commit and submit timestamp. |

## CPU checks performed

1. `s020_edit_preflight.py --self-test` passed 6/6 cases.
2. The edit validator accepts one exact match and rejects a missing argument, absent match, ambiguous match, absolute path and non-string argument.
3. The verdict audit reads all six saved rows, hashes patch text, lists touched files and identifies scratch files.
4. `git apply --stat -` returned exit 128 for all six exported `prediction` strings. This proves the JSONL exporter did not preserve a parseable unified diff. It does not invalidate official PASS/FAIL because Phase 2 ran before JSONL export.
5. Previous byte-level regression showed that `.strip()` can remove significant trailing context. Exact replay of these six exported strings is therefore blocked until raw `result.agent_patch` is captured before normalization.
6. Exact-base `git apply --check --index` remains blocked because this artifact lacks `base_commit` and snapshots.

CPU tool: https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/blob/f3725ac9527fc8c0d0a17d789d620157136861fd/smith/experiments/s020_edit_preflight.py

## Next bounded change

The next runner must copy each actual trace JSON into evidence, save raw `result.agent_patch` unchanged with SHA-256, record base_commit privately, and record monotonic timestamps for first tool, first read, first successful edit, first non-empty production diff, test start, submit and verdict. Apply `.strip()` only to the boolean empty check.

No agent behavior change is justified from this artifact alone. The only confirmed agent-side defect tied to the call sequence is use of the unavailable `grep_search` tool in fastapi_14609. A one-variable prompt ablation may explicitly enumerate the five registered tools and prohibit any other tool name, but it requires the same official panel to measure a PASS delta.

No new official evaluator task was run in this CPU audit.
