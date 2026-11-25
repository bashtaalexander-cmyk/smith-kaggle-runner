# S023 edit-recovery candidate

Parent: repeat candidate from official run 45332756251, candidate SHA-256 `89d20b0bce4413459a18cdb4f89c4d726897d3e7a3dfad9df1f72e18e27e9c1a`.

Single intended change: after two equivalent `edit_file` argument failures, stop repeating the invalid call and use one fail-closed exact-replacement command through the already allowed `run_command` tool.

No search-cap, verification-budget, model, sampling, task-ID, timeout, tool-list or harness change is included.

This candidate is CPU-validated only. It has not been compiled by the official compiler and has no official Evaluator result.
