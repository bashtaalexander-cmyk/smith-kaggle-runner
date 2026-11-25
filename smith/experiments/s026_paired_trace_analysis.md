# S026 — paired trace metrics: baseline vs repeat candidate

UTC: 2026-11-25T14:20:00Z

Official arms on the same six tasks and Gemma 4 31B QAT:

- baseline run 45277650243: 1/6 PASS (`rich_3454`)
- repeat run 45332756251: 2/6 PASS (`rich_3454`, `rich_3063`)

The extractor counts only confirmed native `edit_file`/`write_file` changes to production paths. Shell-based modifications are not guessed; therefore `fastapi_15763` repeat is reported as no confirmed native edit even though its trace proves a later shell helper modified production at 280.3 s.

| Task | Baseline verdict | Repeat verdict | Baseline first native production edit | Repeat first native production edit | Delta | Rejected edit/write baseline→repeat | Tests baseline→repeat |
|---|---|---|---:|---:|---:|---:|---:|
| fastapi_14609 | FAIL | FAIL | 158.8 s | 276.7 s | +117.9 s slower | 5→0 | 0→0 |
| fastapi_15763 | FAIL | FAIL | 79.3 s | none (shell edit 280.3 s) | not comparable | 2→11 | 0→0 |
| requests_7309 | FAIL | FAIL | 67.3 s | 98.0 s | +30.7 s slower | 0→1 | 5→2 |
| requests_7328 | FAIL | FAIL | 285.9 s | 97.9 s | −188.0 s faster | 0→0 | 0→4 |
| rich_3063 | FAIL | PASS | none | 397.0 s | new production edit | 0→4 | 0→2 |
| rich_3454 | PASS | PASS | 112.6 s | 92.3 s | −20.3 s faster | 1→11 | 3→0 |

Aggregate rejected `edit_file`/`write_file` events increased from **8 to 27**. The repeat candidate improved official PASS from 1/6 to 2/6 with no PASS regression, but did **not** improve argument reliability globally. `rich_3063` is the only FAIL→PASS transition; `rich_3454` stayed PASS. Four tasks remained FAIL.

Evidence-led conclusions:

1. The current repeat candidate is the best measured development result, but its mechanism is mixed. Do not attribute the PASS gain to fewer argument errors.
2. S023/S025 exact-recovery remains justified as an isolated next test because `fastapi_15763` had 11 rejections and required a late shell edit.
3. A search cap could help `fastapi_14609`, but must remain a later separate ablation. Its first native production edit regressed by 117.9 s.
4. Faster first edit alone did not solve `requests_7328`; it improved by 188.0 s but remained FAIL. Semantic verifier evidence is still required.
5. Do not tune `requests_7309` semantics: focused tests passed in both evidence reviews while official verifier failed, and its traceback remains unavailable.

Artifacts:

- extractor: https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/blob/68034cd3c49d3fd7fcf7c6330bca5a691bbbedbf/smith/experiments/s026_trace_metrics.py
- raw paired CSV: https://github.com/bashtaalexander-cmyk/smith-kaggle-runner/blob/d983295ffff4a7b26a117b6f87b088a9772951fb/smith/experiments/s026_paired_trace_metrics.csv
- CSV SHA-256: `6c87e9954e35eff15ae31d63ab80d5fda4f73dc0c09671c9c68b59502c95a3c9`
- extractor SHA-256: `45483833fd8dc4feba75c2e5d75a04a4c9732b6aa0a43b4471e20c5d7867d8a2`

No new GPU run, payment, submission or historical mutation occurred.
