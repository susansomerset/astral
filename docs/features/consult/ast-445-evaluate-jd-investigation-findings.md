# AST-445 — evaluate_jd investigation findings

**Linear:** [AST-445](https://linear.app/astralcareermatch/issue/AST-445/investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan)  
**Parent repro:** [AST-441](https://linear.app/astralcareermatch/issue/AST-441/investigate-suspicious-local-run-of-evaluate-jd)  
**Batch id:** `evaluate_jd-34e38ddb-6801-4202-9634-808338f58fae` (suffix `34e38ddb-6801-4202-9634-808338f58fae`)

## Pipeline trace

| Step | What happens | Code |
|------|----------------|------|
| Claim | Dispatcher claims jobs in `JD_READY` (retry holding state `JD_READY_RETRY` is mapped to the same consult task in `consult.py`). Claim is **state-only** — no read of `job_data.job_description`. | `claim_job_batch()` in `src/data/database.py`; seed row `evaluate_jd` in `dispatch_task_seed_templates()` / `list_dispatch_tasks()` with `trigger_state` `JD_READY` |
| Batch entry | Dispatcher invokes consult for claimed batch. | `run_consult_task()` → `evaluate_jd_batch()` in `src/core/consult.py` |
| Assembly | Live content built from `job_data["job_description"]` per job; **empty strings are still enumerated** into the prompt. | `evaluate_jd_batch` `assemble()` → `enumerate_array("JD LISTINGS", jd_texts, …)` (~646–651) |
| Agent | Single `do_task` for full batch. | `_run_batch_consult()` (~411+) |
| Partial response | IDs in prompt but missing from model output → `missing = sent_ids - received_ids` → `retry_state` or `error_state` (`ERROR_EVALUATE_JD`). | `_run_batch_consult` (~474–487) |

## Repro evidence (AST-441)

Parent ticket documents batch `evaluate_jd-34e38ddb-6801-4202-9634-808338f58fae`: **38** jobs claimed in `JD_READY_RETRY`, live content with **37** empty JD slots and **one** populated listing (`[index=010]`), model graded **one** job, **37** IDs treated as agent omissions → `ERROR_EVALUATE_JD`.

## Root cause (plain language)

1. **Claim was correct per product rules** — jobs were in `JD_READY_RETRY`; claim does not verify JD text.
2. **Assembly forwarded blank JD text** — `evaluate_jd_batch` does not filter jobs before `enumerate_array`, so the model received 37 empty slots plus one real JD.
3. **Outcomes were misleading** — empty inputs were not rubric fails; they were counted as agent “missing” IDs and routed to `ERROR_EVALUATE_JD`, which reads like an agent/parse failure rather than “not ready for evaluate.”

**Per-job history:** Local DB may not retain the repro batch. Where `scripts/spikes/ast445_evaluate_jd_batch_trace.py` cannot load `batch_id`, treat AST-441 description as primary evidence. Likely contributors (cannot prove per ID without DB): manual state reset to `JD_READY*` without re-scrape; JD never written after list pass; coat-check (`get_job_data` self-heal) not invoked on the batch path.

## Verdict

**`ERROR_EVALUATE_JD` for agent “missing” IDs when the input JD slot was empty is not acceptable.**

**Desired behavior (observable):** Before `do_task`, drop jobs without usable JD text from the prompt; assign a **non-error, non-rubric-fail** outcome (return to scrape-eligible state) and do not inflate missing-ID / `ERROR_EVALUATE_JD` counts.

## Fix plan for AST-446 (normative)

Copied from plan doc `ast-445-investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan.md` § Stage 4:

| Item | Decision |
|------|----------|
| Readiness rule | `len(job_description.strip()) >= 80` (`min_jd_chars` in `CONSULT_CONFIG["evaluate_jd"]`) |
| Not-ready outcome | `PASSED_JOBLIST` (re-enters `scrape_jd`) |
| State machine | Extend `JOB_STATES["PASSED_JOBLIST"].prior_states` with `JD_READY`, `JD_READY_RETRY` |
| Persistence | `jd_readiness_skip` blob on `job_data` |
| Agent batch | Only ready jobs in `_run_batch_consult`; skip `do_task` when none ready |

**AST-446** implements this table.
