# Astral Consult

**Draft** — living overview of the Consult feature track. Adjust as the Linear program and code evolve.

## Role in the System

Consult is the **job-evaluation and artifact-generation brain** for a candidate’s pipeline. Given a job listing (often after Gazer has captured structured text) and a candidate profile, Consult runs configured **agent tasks** — prompts resolved through `do_task()` — to score fit, extract structured answers, draft materials, and persist results back into candidate/job records. It does not own scheduling (Dispatcher) or first-pass company qualification (Roster); it consumes their outputs and produces graded, schema-shaped data the Interface can render.

## What It Owns

- Orchestration in `**src/core/consult.py`** (and closely related helpers): which tasks run for which job states, how outputs merge into `candidate_data`, and how consult interacts with tracker/state transitions when configured to do so.
- **Semantic contracts** for consult outputs: response schemas, encoded vs decoded storage choices, rubric vectors, importance factors, and any migration notes when those contracts change.
- **Quality and cost awareness** at the call boundary: model selection via agent rows, token usage, and consistency with Foundation’s universal response envelope.

## What It Does Not Own

- **TASK_CONFIG**, token registries, and global model tables — those live in Foundation (`config.py`) and are *consumed* by Consult, not duplicated.
- **Dispatch batching and claim semantics** — Dispatcher decides when consult batches run; Consult implements the work units.
- **UI layout and admin affordances** — Interface presents consult-derived data; Consult does not embed React or Flask view logic.

## Design Principles

- **Single front door for LLM calls** — Prefer routing consult work through `**do_task()`** so model params, schemas, retries, and logging stay aligned with Administrator’s agent/task configuration.
- **Schema-first outputs** — Task definitions and response schemas are the contract; callers should not parse free-form prose when a structured field exists.
- **Persist deliberately** — Writes to `candidate_data`, job rows, and agent response logs should be traceable to a ticket and a plan section (what changed, why, and how rollback/migration is handled).

## Key Files (non-exhaustive)


| Area                 | Typical paths                                                   |
| -------------------- | --------------------------------------------------------------- |
| Core orchestration   | `src/core/consult.py`                                           |
| Task execution / LLM | `src/core/agent.py` (`do_task`, prompt resolution)              |
| Config & schemas     | `src/utils/config.py` (`TASK_CONFIG`, `TOKEN_SOURCES`, schemas) |
| Persistence          | `src/data/database.py` (consult-related saves and migrations)   |
| Feature docs         | `docs/features/consult/` (this tree)                            |


## Pointers

- Board and label rules: [orientation.md](orientation.md)
- New ticket writeup skeleton: [FEATURE_DOC_TEMPLATE.md](FEATURE_DOC_TEMPLATE.md)