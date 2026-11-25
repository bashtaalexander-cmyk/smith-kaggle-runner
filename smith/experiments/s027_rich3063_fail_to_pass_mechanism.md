# S027 — `rich_3063` FAIL→PASS evidence audit

UTC: 2026-11-25

## Scope

Paired comparison of the same task and official Gemma 4 31B QAT evaluator configuration:

- frozen baseline: GitHub Actions run `45277650243`, official **FAIL**;
- repeat candidate: GitHub Actions run `45332756251`, official **PASS**.

This audit identifies the first confirmed behavioral difference. It does not claim that any prompt rule caused the PASS, and it does not expose the task patch to the agent.

## Confirmed chain

| Stage | Baseline | Repeat candidate |
|---|---|---|
| Locate | `rich/markup.py`, `escape_backslashes` found immediately | same file and symbol found immediately |
| First successful production edit | **none** | `rich/markup.py` at 390.4 s from first tool call |
| Edit failures before production edit | none (no production edit attempted) | 3 missing `old_string`; then 1 old-string mismatch |
| Final submitted files | only `reproduce_issue.py` | `rich/markup.py` plus `repro.py` and `debug_escape.py` |
| Production diff | empty | non-empty change in `rich/markup.py` |
| Post-edit checking | scratch experiments only; final experiment ended in syntax error | targeted scripts exercised trailing-backslash output; one repro raised a traceback, later debug check printed transformed output |
| Submit | 309.4 s, 1 file, 457 bytes | first submit 578.7 s, 3 files, 2365 bytes |
| Official verdict | FAIL | PASS |

## First confirmed reason for the baseline FAIL

The baseline never modified tracked production code. Its exported patch contained only a new reproduction script, so it could not fix the reported library behavior. This is directly confirmed by the raw prediction diff and full trace. The official verifier does not expose a more granular assertion, but none is needed to establish this first failure.

## What changed in the PASS run

The repeat run recovered after four failed `edit_file` attempts and produced a non-empty production diff. The official evaluator then returned PASS. This establishes a transition from **no production edit** to **accepted production edit** on this task. It does **not** establish that the higher-level prompt, the precise implementation, or the extra scratch files generalize.

## Negative findings

- Lower edit-error count is not the mechanism: rejected edit/write calls increased on this task from 0 to 4.
- Speed is not the mechanism: first production edit occurred very late (390.4 s), and submission was later than baseline.
- Verification quality remained weak: no narrow repository test was run after the production edit, and scratch files contaminated the submitted patch.
- The PASS therefore supports edit recovery as a necessary capability here, not the full repeat scaffold as a clean solution.

## Action justified by evidence

Keep S023's one-variable edit-recovery experiment: after two repeated argument-shape failures, perform one fail-closed exact replacement with path containment and exactly-one-match checks. Do not add task-specific code. The next official paired run must use the same six IDs, weights, sampling, and limits and must report FAIL→PASS and PASS→FAIL transitions.

Separately, add a submission hygiene guard that excludes untracked scratch/debug/repro files unless explicitly required by the issue. This is a distinct ablation and must not be combined with edit recovery in the first paired test.

## Missing evidence

- exact private verifier assertions and per-test output;
- exact clean base commit needed for `git apply --check` replay;
- raw unmodified `agent_patch` bytes (the artifact exposes JSONL prediction text, not a separately checksummed raw patch stream);
- an official S023 evaluation, blocked by the confirmed Kaggle weekly GPU quota error.

## Evidence locations

- baseline artifact `14870772625`, `output/results/traces/trace_rich_3063.json`, `output/predictions.jsonl`;
- repeat artifact `14895580037`, same relative paths;
- paired metrics: `smith/experiments/s026_paired_trace_metrics.csv`.
