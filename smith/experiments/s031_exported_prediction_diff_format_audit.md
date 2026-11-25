# S031 — exported prediction diff format audit

UTC: 2026-11-25

## Scope

Format-only parsing of the 12 patch strings reconstructed from the baseline and repeat `predictions.jsonl` artifacts. Exact base commits are unavailable, so this deliberately does **not** run or claim exact-base `git apply --check`.

Command used for syntax parsing:

`git apply --numstat --summary --allow-binary -`

## Confirmed result

- raw exported patches parsed: **0/12**;
- raw exported patches ending in newline: **0/12**;
- eight became syntactically parseable after diagnostic reconstruction of only the terminal newline;
- two required the terminal newline plus one whitespace-only context line (`rich_3454`, both runs);
- two required the terminal newline plus two whitespace-only context lines (`requests_7309`, both runs).

This pattern is consistent with a prior trailing-whitespace strip on the exported representation: it removes the terminal newline and can also remove final diff context lines that consist of a single prefix space. The reconstruction is stored only as a diagnostic hash; no historical patch is overwritten or relabeled as original.

## Critical causality boundary

This does **not** show that stripping caused any official FAIL. Official evaluation precedes prediction artifact export. In particular, `rich_3454` is an official PASS in both runs even though both exported copies are syntactically truncated. That is direct evidence that the malformed stored representation is an evidence/export defect, not the patch representation used by the verifier.

Consequences:

1. Existing `predictions.jsonl` is adequate for qualitative diff inspection but not byte-exact replay.
2. Historical raw patch bytes cannot be recovered with certainty; reconstructed variants must remain separately labeled.
3. S029 must checkpoint in-memory `agent_patch` before any strip/transformation in future runners.
4. Agent changes and export fixes remain separate experiments.

## Reproducibility

- script: `s031_prediction_diff_format_audit.py`;
- script SHA-256: `8a9ddc47965b5bf095fecfa8c5f28692779e8ed07daa8f435c1ac6db7c3ff5e5`;
- JSON result SHA-256: `0806fffac672e5192853f74d84aa40ab16c6f8697761a46839cd68218dab3712`.

No evaluator, GPU, submission, historical ZIP, or candidate was changed.
