# S019 external harness and free-runtime audit

UTC: 2026-11-25T07:05:00Z  
Scope: source/licence/runtime feasibility audit only. No model endpoint, paid resource, Kaggle submission, or official evaluator run was started.

## Verified source facts

### dreamyang-liu/kaggle-gemma-eval

- Source: https://github.com/dreamyang-liu/kaggle-gemma-eval
- Repository metadata: created 2026-10-24; default branch `main`; no repository licence declared and no LICENSE file in the root listing.
- Consequence: source may be inspected, but its code is not copied into SMITH. Any reusable implementation must be clean-room unless the author adds a licence.
- The README describes a Docker replica of Kaggle image v170 and calls the official `swegemma.Evaluator`. Setup requires Docker, accepted Kaggle rules, Kaggle credentials, competition data/wheelhouse, and (for local mode) NVIDIA runtime plus downloaded weights.
- `evaluate.sh` supports either a local vLLM server or an OpenAI-compatible endpoint. Endpoint workers are routed through an internal gateway container.
- The author explicitly warns that hosted Gemma 4 31B is not the Kaggle W4A16 QAT build and that hosted scores are only approximations.
- The author also warns that Docker sandbox FastAPI tasks miss dependencies; `subprocess` is the Kaggle-comparable path.
- Default image is `gemma4-kaggle:v170-plus`, while the README says `v170-plus` adds `inline-snapshot` and `dirty-equals`. This is a diagnostic divergence from the official v170 image and must not be silently mixed into official comparisons.
- Existing SMITH static checks already established that the wrapper compiles, but this Work environment has no Docker/Podman, Kaggle competition mount, GPU or endpoint credentials. Therefore no container or evaluator task was run here.

### TechNaom/gemma4-agentic-swe

- Source: https://github.com/TechNaom/gemma4-agentic-swe
- Author: Manohar Papasani / TechNaom.
- Licence: Apache-2.0 (verified LICENSE file).
- Reported research result: plain agent 34/68 (50%); graph tools 32/68 (47%), p=0.69. This is the author's experiment, not a SMITH result.
- Transferable conclusion for SMITH: do not add graph calls by default. Treat graph retrieval as a measured fallback only; it did not improve the cited experiment.
- Model checkpoint named by the project: `gemma-4-31b-it-qat-w4a16-ct`.

## Exact checkpoint and licence

- Primary model card: https://huggingface.co/google/gemma-4-31B-it-qat-w4a16-ct
- Visible model-card revision: `52f3f65` (full revision previously resolved as `52f3f65bc7a02d555763bc923bd1d9094898219d`).
- Model card declares Apache-2.0 and identifies the w4a16 compressed-tensors checkpoint as the vLLM-oriented QAT format.
- This does **not** establish byte identity with the Kaggle model asset. Required parity check remains: compare Kaggle model manifest and tokenizer/config/weight hashes inside an authorized private Kaggle session.

## Free-provider feasibility, primary-source correction

| Provider | Verified free condition | 31B QAT feasibility conclusion |
|---|---|---|
| Lightning AI | Pricing advertises 5 credits at registration and up to 30 total only after adding a card; GPU jobs consume credits. One 4-CPU Studio is free. | No zero-billing 31B run is authorized. Registration-only 5 credits and available multi-GPU/VRAM were not verified in an account. Do not add a card. |
| Modal | Starter includes $30/month compute, but usage beyond included compute is pay-as-you-go; Model API tokens are billed from the first request. | Potential container/GPU experiment only after account entitlement and a hard zero-spend budget are independently confirmed. No account or endpoint was provisioned. |
| Colab free | GPU type and limits are not guaranteed; free runtimes run at most 12 hours depending on availability. | Cannot promise the exact 4×L4/96 GB topology or QAT parity. No compatible free runtime was confirmed. |

Primary sources:
- https://lightning.ai/docs/platform/overview/faq/billing
- https://platform.lightning.ai/pricing
- https://modal.com/pricing
- https://research.google.com/colaboratory/faq.html

Correction to earlier secondary research: “50 free GPU hours” is not supported by current Lightning primary documentation. The page says up to 30 credits, with only 5 at registration and 25 conditional on adding a card.

## Practical gate for an external run

A run may proceed only when all gates are satisfied:

1. Docker + NVIDIA runtime actually available.
2. Competition rules accepted and authorized Kaggle data/wheelhouse available.
3. Exact checkpoint identity established or result explicitly labelled approximate.
4. Provider confirms sufficient included credit and a hard zero-spend ceiling; no card/billing activation.
5. `subprocess` sandbox and official v170 image used for Kaggle comparability.
6. Six frozen task IDs, same agent/scaffold/settings, full logs and raw `agent_patch` bytes preserved.
7. Official PASS only when `swegemma.Evaluator` phase 2 returns PASS.

## CPU evidence and decision

Existing new SMITH CPU utilities remain the verified preparation path:
- `smith/experiments/s018_patch_export.py`: 5/5 raw patch roundtrip cases, preserving LF/CRLF and SHA-256.
- `smith/experiments/s018_patch_replay.py`: 4/4 synthetic disposable-git cases, rejecting truncated patches, wrong HEAD and dirty trees.

No new official verdict was produced. The latest known official development result remains 2/6. The next useful execution is not another synthetic agent redesign: it is either (a) dispatch the already-created manual Docker CPU workflow, or (b) obtain an authorized private Kaggle CPU session to extract only the exact base commits needed for saved-patch replay. GPU remains gated by free quota.
