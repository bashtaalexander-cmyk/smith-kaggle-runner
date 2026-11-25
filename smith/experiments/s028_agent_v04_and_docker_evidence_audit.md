# S028 — `agent_v0.4` and Docker execution evidence audit

UTC: 2026-11-25

## Question

Does the project currently contain a verifiable `agent_v0.4` artifact, and was the proposed Docker CPU smoke actually executed?

## `agent_v0.4`

Checked the repository and the shared project folder without relying on names mentioned in plans:

- GitHub branches API: exactly one branch, `main`, current head `e54de177212d91d3228982fd04064eac5efaa737`;
- recursive tree of that head: no path containing `agent_v0.4` or `v0.4`, and no ZIP committed;
- GitHub code search for `agent_v0.4` and `v0.4`: no results;
- GitHub commit-message search for `v0.4`: no results;
- GitHub releases API: empty;
- Google Drive project-folder searches for `agent_v0.4` and `v0.4`: no results.

**Verdict:** no branch, commit, ZIP, SHA-256, or Drive artifact proves that `agent_v0.4` exists. It must not be treated as created, compiled, evaluated, or as a baseline.

The separately evidenced candidate is S023 edit recovery:

- repository path: `smith/candidates/s023_edit_recovery/`;
- deterministic ZIP in Drive: `smith_s023_edit_recovery_cpu_validated.zip`;
- SHA-256: `7fc91e660435fbc7e7cce1a0f744a77d8628db2b3b21d8f3688876ac298893e7`;
- CPU validation only; no official evaluator verdict.

## Docker execution

The repository contains `.github/workflows/smith-docker-cpu-smoke.yml`. Its intended commands check Docker, pull `alpine:3.23`, build a minimal image, and run it with `--network none`.

All 18 repository Actions runs were enumerated through the Actions API. None has:

- workflow path `.github/workflows/smith-docker-cpu-smoke.yml`;
- workflow name `SMITH Docker CPU smoke`;
- Docker smoke logs or an artifact from such a run.

The workflow is `workflow_dispatch` only. Its presence is configuration evidence, not execution evidence.

**Verdict:** no factual Docker run is proven. Therefore external harness feasibility remains static analysis only; no claim about a working free Docker runtime, endpoint, exact QAT checkpoint, or official evaluator compatibility is allowed.

## Preserved baseline and action boundary

- Best official development result remains repeat run `45332756251`: **2/6** (`rich_3454`, `rich_3063`).
- S023 is the separate one-change edit-recovery candidate required by the emergency instruction. It is already packaged and CPU-validated, so no duplicate candidate was created.
- Raw patch export is infrastructure evidence and remains separate from candidate quality.
- No GPU run, submission, paid resource, or quota workaround was attempted in this audit.

## Next falsifiable checks

1. A Docker claim requires a completed run URL plus immutable logs showing `docker run` exit 0 and image digest.
2. An `agent_v0.4` claim requires an immutable branch/tag/commit, ZIP, SHA-256, root `agent.yaml`, compiler log, and evaluator evidence if PASS is claimed.
3. When free Kaggle quota is factually available, run S023 against the frozen six IDs with the exact same 31B QAT weights, sampling, and limits as run `45332756251`.
