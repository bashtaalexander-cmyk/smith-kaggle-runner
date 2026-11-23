# Public references for SMITH

Public search and direct GitHub repository reads. Coverage is limited to the sources below. No third-party code or benchmark fixes were imported.

| Project | Owner or author | License or terms | Relevant idea |
|---|---|---|---|
| [Gemma 4 Baseline](https://www.kaggle.com/code/honghanhhh/gemma-4-baseline) | Hanh Tran | Apache-2.0 per notebook | Public 0.13, best 0.18 V3 per Kaggle. Public score is external evidence, never a SMITH result. |
| [gemma4-developer-agent](https://github.com/SebAustin/gemma4-developer-agent) | SebAustin | Apache-2.0 | Freeze task splits and record compiler and run artifacts. |
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) | SWE-agent project | MIT | Use concise tool outputs and an inspectable tool interface. |
| [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) | SWE-agent project | MIT | Small tool surface, stateless commands and inspectable trajectories. |
| [Agentless](https://github.com/OpenAutoCoder/Agentless) | OpenAutoCoder | MIT | Narrow localization from file to symbol, then apply a repair and use targeted checks. |
| [AutoCodeRover](https://github.com/AutoCodeRoverSG/auto-code-rover) | AutoCodeRoverSG | Sonar Source-Available License v1.0 | AST-based retrieval of relevant methods and classes. Consider an independently written shortlist only if the traces establish localization failures. |

The first paired run changes patch review instructions and retains the same model, tool budget and task order. Consider deterministic shortlisting or a bounded verifier as independent later ablations. Keep the development panel separate from new task IDs used to validate generalization. The published starter had a 12B assignment in its model selection cell; our reproduced official notebook used 31B and the published offline wheelhouse on Kaggle L4×4. No published time or score establishes compatibility on a different image.
