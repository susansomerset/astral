# AST-371 — [AST-300] tracker persistence + batch trigger integration

**Linear:** [AST-371](https://linear.app/astralcareermatch/issue/AST-371/ast-300-tracker-persistence-batch-trigger-integration)  
**Feature branch:** `<agent>/ast-371-ast-300-tracker-persistence-batch-trigger-integration`  
**Parent:** [AST-300](https://linear.app/astralcareermatch/issue/AST-300)

## Summary

Persist **`job_data.artifacts.resume_content`** using existing **tracker → database** merge semantics when the resume craft pipeline completes. Wire **`dispatch_tasks`** (or equivalent) so the resume artifact batch runs at the **lifecycle state** agreed in **AST-300** after **AST-302** / **AST-303** / **AST-304** prerequisites. Validate **`GET /api/jobs`** and editor payloads expose **`resume_content`** consistently for UI and **`builder._resolve_resume_sections`**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | `save_job_resume_content(job_id, dict)` (name TBD after grep) delegating to canonical job save. | core |
| `src/core/dispatcher.py` | `trigger_state` / task wiring for resume artifact batch. | core |
| `src/utils/config.py` | `dispatch_tasks` seed or `JOB_STATES` references if required for trigger. | utils |
| `src/ui/api/api_jobs.py` | Serialization includes `artifacts.resume_content` when present. | ui |

## Stage 1: Write path

**Done when:** After a simulated craft output dict, `get_job` returns identical keys in `artifacts.resume_content`.

1. Grep `resume_content` in `src/`.
2. Implement or fix merge in tracker layer per **AST-302** helper patterns if those helpers landed first.

## Stage 2: Dispatch trigger

**Done when:** Jobs in the agreed pre-artifact state transition into batch claim for resume craft without double-claim.

1. Read **AST-300** parent issue / plan doc on `dev` if present.
2. Align `dispatch_tasks` row for resume craft (`craft_resume_*` task key — grep actual key on `dev`).

## Stage 3: API + builder read

**Done when:** No shape mismatch between API JSON and `builder` expectations.

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
Dispatch + tracker + API.

**Conf — `LOW`**  
Blocked by **AST-302**, **AST-303**, **AST-304** per Linear.

**Risk — `HIGH`**  
Double dispatch or dropped artifacts.

## Self-review vs ASTRAL_CODE_RULES

§2.4 — preserve `batch_id` claim semantics; no new DB tables without design.

---

## Review (build)

**Branch:** `ftr/AST-371`  
**Commit:** (see Linear build comment)

**Revisions:** `persist_job_artifact_from_parsed` on terminal `do_task` hop; contemplation/resume-cover dispatch chain @ `BUILD_ARTIFACTS`; `run_consult_task` → artifact chains per job (`contemplate_job` / `draft_cover_letter` on integration line).

---

## Radia review (review-astral 2026-05-16)

**Diff:** `origin/dev...origin/ftr/AST-371` (`0ee62f8`)

### What's solid

- `BUILD_ARTIFACTS` routes through resume-first artifact orchestration integrated with AST-369 cover letter hop.
- Dispatch seed aligns with `_DISPATCH_TASK_SEED` (`contemplate_job` @ `BUILD_ARTIFACTS`).
- Shared `persist_job_artifact_from_parsed` + resume/cover shape tests (`TestPersistJobArtifactFromParsed`, `TestAst371ResumeArtifactDispatch`).

### Issues

Historical review items below applied on earlier branch tips — **superseded** on `origin/dev` + `dev-betty` integration (cover chain wired; task keys renamed `contemplate_job` / `draft_cover_letter`).

| Severity | Item |
|----------|------|
| **fix-now** | (Historical) Resume batch vs cover-letter test skew — resolved after AST-369 merge. |
| **discuss** | Lazy import `persist_job_artifact_from_parsed` inside `do_task` — cycle-break comment present in `agent.py`. |

**Counts:** (historical) — Radia

---

## Resolution (resolve-astral 2026-05-17, amended post-merge)

- Integration line carries **both** resume chain + cover letter hop tests; `_INPUT_STATE_TO_TASK` maps `BUILD_ARTIFACTS` / `CANDIDATE_REVIEW` to **`contemplate_job`** / **`draft_cover_letter`**.
- **`persist_job_artifact_from_parsed`** lazy import retained in `do_task` per agent↔tracker cycle break.

— Katherine / Chuckles integration note (2026-05-24)

