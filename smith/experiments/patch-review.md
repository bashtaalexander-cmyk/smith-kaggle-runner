# SMITH experiment checkpoint

Baseline: 1/6 verified PASS on Gemma 4 31B. The baseline workflow and artifacts are preserved.
- Baseline evidence (official logs, traces, six full patches, agent ZIP): https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/actions/runs/45277650243/artifacts/14870772625
- Paired patch-review variant: https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/actions/runs/45284947369
- Frozen panel: rich_3454, fastapi_14609, requests_7328, rich_3063, fastapi_15763, requests_7309.

Baseline findings from traces and exported diffs:
- rich_3454 passed with a single production file in the submitted diff.
- rich_3063 submitted only reproduce_issue.py, without the intended production fix.
- fastapi_15763 and requests_7309 submitted a production file and a debug script. This is a confirmed patch hygiene defect; the evaluator exit alone does not prove it caused both failures.
- fastapi_14609 ended with three partially migrated compatibility modules and reported unfinished follow-up cleanup; evaluator exit 2.
- requests_7328 submitted while its local reproduction was still failing; evaluator exit 1.

Patch-review variant keeps the same model, task order, runtime configuration and tool budgets. It changes instructions to protect the production diff, check the import source, reserve final tool calls, and do one focused correction after a failing check. No benchmark-specific answers are embedded.

Public references: [Hanh Tran Kaggle baseline](https://www.kaggle.com/code/honghanhhh/gemma-4-baseline) (the Kaggle page shows 0.13 public and 0.18 best V3), [SWE-agent](https://github.com/SWE-agent/SWE-agent) (purpose-built tool interface), [Agentless](https://github.com/OpenAutoCoder/Agentless) (localization, repair, then validation), [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) (small tool interface). Public results do not establish any SMITH PASS. No external agent code was copied.
