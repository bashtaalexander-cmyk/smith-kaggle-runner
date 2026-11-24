# SMITH evidence-to-experiment matrix
2026-11-24 UTC. Estimates describe experiment design, not measured speedups. No external code imported.

| Source / license | Transferable method | Integration and cost | Measurable hypothesis |
|---|---|---|---|
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) / MIT | Explicit editing interface and observable failures | Existing edit_file, no new callback; schema example in prompt, one retry | Fewer repeated missing-argument rejections and more successful production edits |
| [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) / MIT | Small tool surface and explicit state | Existing allowed run_command; use only after two equivalent edit errors; one focused edit and diff check | Shorter recovery time without extra invalid calls |
| [Agentless](https://github.com/OpenAutoCoder/Agentless) / MIT | File-to-symbol localization and targeted patch validation | Existing bounded reads or one shell test; no hidden test access | Lower first-edit latency or higher PASS in separate ablations; prior advisory experiments each scored 1/6, so no promotion |
| [AutoCodeRover](https://github.com/AutoCodeRoverSG/auto-code-rover) / Sonar Source-Available v1.0 | Rank symbols using program structure | Independent AST shortlist only, no code reuse; offline CPU, report wall time and shortlist recall | Fewer wrong-file first edits; test only after traces support localization as a bottleneck |
| [SebAustin](https://github.com/SebAustin/gemma4-developer-agent) / Apache-2.0 | Freeze splits and preserve run evidence | Runner-side only; hashing and JSONL checkpoints; no additional model calls | Identical normalized source hashes and usable partial evidence after interruption |
| [Hanh Tran](https://www.kaggle.com/code/honghanhhh/gemma-4-baseline) / Apache-2.0 per notebook | Prioritize a reproducible Kaggle runtime | Compare starter inputs and metadata; public notebook score does not measure SMITH | Offline native startup succeeds on the tested image; already observed for the official starter route |

Next eligible GPU test is the existing recovery workflow, blocked before notebook execution by weekly quota. Use the original development panel. Prespecify equivalent-error streak by normalized missing parameter set, recovery time from rejection observation to first confirmed production change, and paired official PASS. Separate structural recovery from semantic correctness. Baseline 1/6; argument variant 2/6 twice on development and 2/6 versus 1/6 on exploratory data. No clean holdout claim.
