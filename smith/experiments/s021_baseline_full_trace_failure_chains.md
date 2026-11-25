# S021 — baseline full-trace recovery and confirmed FAIL chains

UTC: 2026-11-25T09:25:00Z

## Evidence

- Official baseline run: https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/actions/runs/45277650243
- Artifact: `smith-candidate-31b-evidence`, ID `14870772625`
- GitHub artifact digest: `sha256:25bfe6869bafaacf95781291451c0fb08a2ba232c2697e1bc49118e6be13e79b`
- Unlike repeat run 45332756251, this baseline artifact contains all six full trace JSON files under `output/results/traces/`.
- Model path recorded in traces: `/kaggle/input/models/google/gemma-4/other/gemma-4-31b-it-qat-w4a16-ct/2`.
- Official baseline verdict: 1/6 PASS (`rich_3454`). FAIL: `fastapi_14609`, `requests_7328`, `rich_3063`, `fastapi_15763`, `requests_7309`.

The artifact still lacks exact repository base commits and raw pre-export `result.agent_patch` bytes. Its `predictions.jsonl` is an exported copy and is not sufficient for exact-base replay.

## Reconstructed chains

| Task | Search / first located file | First confirmed production edit | edit/write errors | Verification before submit | Final diff / application evidence | Official verdict | First confirmed failure mechanism | Missing data |
|---|---|---:|---:|---|---|---|---|---|
| `fastapi_14609` | `fastapi/_compat/main.py`, `may_v1.py`, `v2.py`; 14 calls before first production edit | 158.8 s | 5 consecutive `edit_file` schema failures, all missing `old_string`, starting 283.1 s | No test; call budget exhausted | submit at 350.7 s, 3 production files, 5,561 bytes | FAIL, verifier exit 2 | Confirmed workflow failure: repeated invalid edit arguments consumed remaining budget and agent explicitly submitted an incomplete patch. Verifier's first failing test/collection error is not present. | verifier traceback; raw patch bytes; exact base commit/snapshot |
| `requests_7328` | `src/requests/sessions.py`; 16 calls before first production edit | 285.9 s | 0 | Agent's own reproduction still failed at 421.9 s and showed response B present in its own history; then budget exhausted | submit at 450.1 s, one production file, 885 bytes | FAIL, verifier exit 1 | Confirmed semantic failure before submission: the changed code did not eliminate the self-reference in the agent's reproduction. | official verifier traceback; raw patch; exact base |
| `rich_3063` | `rich/markup.py` read, but no production edit | none | 0 schema errors; repeated scratch writes | Last scratch check became a SyntaxError at 278.5 s; budget exhausted | submit at 309.4 s; exported diff contains only `reproduce_issue.py`, no production code | FAIL, verifier exit 1 | Confirmed absence of a production fix; only scratch/debug file was submitted. | official verifier traceback; raw patch; exact base |
| `fastapi_15763` | `fastapi/routing.py`; 15 calls before first production edit | 79.3 s | malformed `write_file` at 50.1 s; malformed `edit_file` at 172.9 s | After removing the guard, reproduction returned 404 instead of expected 200; no successful corrective edit before submit | submit at 181.4 s; production deletion plus `reproduce_issue.py` | FAIL, verifier exit 1 | Confirmed semantic failure before submission: the agent's own expected-behaviour reproduction failed (404). | official verifier traceback; raw patch; exact base |
| `requests_7309` | `src/requests/utils.py`, `tests/test_utils.py`; 10 calls before first production edit | 67.3 s | 0 | First pytest used installed package and failed; corrected `PYTHONPATH=src pytest tests/test_utils.py` passed 206/206 with 13 skipped at 162.4 s | submit at 165.1 s; production change plus tracked `repro.py` contamination | FAIL, verifier exit 1 | No semantic verifier cause is proven. The trace proves focused public tests passed; scratch contamination is real but not proven causal. | official failing assertion/traceback; raw patch; exact base |
| `rich_3454` | `rich/highlighter.py`; 14 calls before first production edit | 112.6 s | 1 malformed `edit_file` before recovery | `pytest tests/test_highlighter.py` passed | submit at 136.7 s | PASS | N/A | exact base/raw patch still absent for replay |

## Phase timing and call-budget facts

| Task | Calls observed in trace | Time to first production edit | Time to submit | Calls before first production edit | Invalid edit/write calls |
|---|---:|---:|---:|---:|---:|
| fastapi_14609 | 31 events including uncounted/error events | 158.8 s | 350.7 s | 14 | 5 |
| requests_7328 | 26 | 285.9 s | 450.1 s | 16 | 0 |
| rich_3063 | 25 | none | 309.4 s | 25 | 0 |
| fastapi_15763 | 27 | 79.3 s | 181.4 s | 15 | 2 |
| requests_7309 | 23 | 67.3 s | 165.1 s | 10 | 0 |
| rich_3454 | 26 | 112.6 s | 136.7 s | 14 | 1 |

Trace event count can exceed the configured 24 counted calls because terminal submission and rejected/budget events are represented separately. Do not interpret it as the harness accepting more than 24 counted tool calls.

## Decisions supported by evidence

1. **Argument reliability is the first isolated change for `fastapi_14609`.** Five consecutive missing-`old_string` failures are confirmed. The existing CPU preflight regression already rejects missing, non-string and ambiguous arguments.
2. **Search cap is supported for `requests_7328` and `rich_3063`.** They reached the first production edit at 285.9 s or never edited production. A bounded locate→edit transition is measurable; it must be a separate ablation from argument changes.
3. **Do not tune `requests_7309` semantically yet.** Its public suite passed. Without the official failing assertion, changing logic would be speculation.
4. **Trace preservation is mandatory in the next runner.** Copy actual trace JSONs, preserve raw `result.agent_patch` bytes before any `.strip()`, record SHA-256, model/evaluator/image versions and task timing. Exact-base `git apply --check` remains impossible until private base commit and snapshot access are available.

## Verification performed this cycle

- Downloaded artifact 14870772625 and verified it contains six non-empty trace JSONs.
- Parsed every tool call, elapsed time, arguments, observation status, first production edit and terminal submission.
- Cross-checked exported diffs against trace operations.
- No GPU, paid runtime, endpoint, submission or historical-version mutation was used.
- No new official evaluation was run; last confirmed development result remains 2/6 on the later repeat candidate.
