# AST-1018 — Dispatch running requested resume tasks despite the auto = false

<!-- linear-archive: AST-1018 archived 2026-08-05 -->

## Linear archive (AST-1018)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1018/dispatch-running-requested-resume-tasks-despite-the-auto-false  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Scheduled Actions shows AUTO off for candidate stage-dispatch rows (`candidate_requested_resume` / `candidate_requested_artifacts`), but the dispatcher still starts those tasks (tick or equivalent auto path). Operators must be able to park stage work on CLICK-only without the scheduler waking it. This restores the AUTO contract so false means “do not auto-run,” while explicit Run still works.

## Functional scope

1. **AUTO false is honored end-to-end.** When a `dispatch_task` row for `candidate_requested_resume` or `candidate_requested_artifacts` has AUTO off, the scheduler must not start that row. No “Dispatching candidate_requested_* …” (or equivalent spawn) for that row unless Susan explicitly Runs it.
2. **CLICK / Run still works.** With AUTO off, admin Run (or equivalent CLICK path) may still claim eligible candidates and execute the stage workers. Missing candidate/API key skips remain as today.
3. **AUTO on still works.** Rows with AUTO on continue to be eligible for the tick when they have enough available work.
4. **Operator toggle sticks.** Turning AUTO off (or on) in Scheduled Actions persists for that row. Boot-time stage provision, template sync, or other automatic writers must not silently flip AUTO back on for an existing row Susan already configured.
5. **New stage rows seed AUTO off.** Newly provisioned `candidate_requested_resume` / `candidate_requested_artifacts` rows default to AUTO **off** (CLICK until Susan turns them on) — Susan confirmed.
6. **Both stage keys.** Same contract for `candidate_requested_resume` and `candidate_requested_artifacts` (both appear in the failing log).
7. **Debug when** `debug=True`**.** On touched backend `debug=` dispatch paths, when a row is not auto-spawned because AUTO is off, log what was found (row identity / task key / candidate) and that it was skipped for AUTO off — Style D index headers + `|` detail; long payloads truncated per AST-538. No new debug requirements on React/UI.

## Architectural definition

* **Patterns to reuse**
  * `pattern.batch.entity-claim-process-release` — stage dispatch still claims/processes/releases entities; AUTO gating must not bypass claim-release discipline when a row *does* run.
  * `pattern.config.config-block` — stage-task defaults and orchestration knobs stay config/registry-driven, not ad-hoc literals scattered in callers.
  * `pattern.layers.import-discipline` — fix stays in allowed layers (core/data/utils as ownership requires); no cross-layer shortcuts.
* **New patterns proposed:** none.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — AUTO seed/default and operator toggle behavior must not invent a second source of truth.
  * `astral.standards.debug-contract-gated` — AUTO-off skip traces only when `debug=True`, Style D + detail prefix.
  * `astral.standards.logging-via-utils` — logging via utils logger helpers.
  * `astral.standards.in-scope-only` — do not touch unrelated dispatch keys or candidate craft workers.
  * `astral.standards.no-hardcoded-sets` — no new inline state/task-key sets; use config registries.
  * `astral.batch.claim-process-release` — when AUTO-on / CLICK does run, claim/process/release remains intact.
  * `astral.layers.import-direction` — respect layer import direction on any touched modules.
  * Full active `tier: universal` statute set (plan/code consumers) — product-code change; plan-child/review-child load the universal set per canon README.

## Boundaries

* Does not redesign the candidate REQUESTED_RESUME / REQUESTED_ARTIFACTS state machine or craft workers ([AST-972](https://linear.app/astralcareermatch/issue/AST-972/dispatch-and-stale-eligibility-for-candidate-stages-candidate-state) stage behavior stays).
* Does not change eligibility/claim rules for those stages beyond AUTO gating.
* Does not rebuild Scheduled Actions UI beyond whatever is required to make the AUTO toggle truthful for these rows.
* Does not change unrelated dispatch task keys unless the same AUTO-leak path is proven shared and fixing it is necessary for this bug.
* Does not reintroduce automatic re-seed of deleted `dispatch_task` rows (AST-745).
* Config-as-source-of-truth (`astral.config.config-source-of-truth`): new stage-row AUTO default is an explicit product choice (AUTO off), not a silent override of operator toggles on existing rows.

## Acceptance criteria

1. With AUTO off on a `candidate_requested_resume` row that has available work, after a scheduler tick (and without clicking Run), logs show no dispatch start for that row.
2. Same as (1) for `candidate_requested_artifacts`.
3. With AUTO off, clicking Run on that row still starts a CLICK dispatch (or skips with the existing no-candidate/API-key message when applicable).
4. With AUTO on and available ≥ min_count, the tick still starts the row as before.
5. After Susan turns AUTO off in Scheduled Actions and restarts (or re-runs provision), that same row remains AUTO off — no silent re-enable.
6. Newly provisioned stage-dispatch rows for these two task keys are created with AUTO **off**.
7. When `debug=True` on a touched path, a skip-for-AUTO-off decision emits Style D index + `|` detail naming the task/candidate and outcome.

## Dependencies and blockers

none. Adjacent history: [AST-972](https://linear.app/astralcareermatch/issue/AST-972/dispatch-and-stale-eligibility-for-candidate-stages-candidate-state) (stage dispatch + provision), AST-995/AST-1000 (boot provision helper restore). Astral Dispatcher board otherwise idle.

## Open questions

none.

## Proposed child tickets

Monolith check: Functional scope has 7 capabilities; one child is intentional — single vertical bug (AUTO gate + persist + seed default + stage keys) must ship together for UAT.

#### 1: **Honor AUTO off for candidate stage dispatch - Ada**

Find and fix why `candidate_requested_resume` / `candidate_requested_artifacts` still auto-dispatch when AUTO is false. Tick must not spawn AUTO-off rows; CLICK Run must still work; existing operator AUTO settings must survive provision/boot; **new** stage rows seed AUTO **off**; debug skip lines when `debug=True`. Does not own craft prompts or candidate state redesign.
**Citations:** `pattern.batch.entity-claim-process-release`, `pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.config.config-source-of-truth`, `astral.standards.debug-contract-gated`, `astral.standards.logging-via-utils`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`, `astral.batch.claim-process-release`, `astral.layers.import-direction` (+ full universal set for plan/code review).

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-1018](https://linear.app/astralcareermatch/issue/AST-1018/dispatch-running-requested-resume-tasks-despite-the-auto-false) (parent) | ftr/AST-1018-honor-auto-off-candidate-stage-dispatch |
| [AST-1022](https://linear.app/astralcareermatch/issue/AST-1022/honor-auto-off-for-candidate-stage-dispatch-dispatch-running-requested) | sub/AST-1018/AST-1022-honor-auto-off-candidate-stage-dispatch |

**Epic worktree:** `astral-AST-1018/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/a8ab9cb9f5a028a4c8ac3f46e952148c/6ff95c7e-f0dd-493d-959d-7dfbeb8956ce/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/b1679cce-4798-4eeb-82be-fff00e29dac6/store.db` |
| Radia | review | `/home/susan/.cursor/chats/a8ab9cb9f5a028a4c8ac3f46e952148c/9c85ea24-3cf8-4467-86cd-59c20896b47e/store.db` |

---

## Original brief

```
Dispatching candidate_requested_resume — 1 available, batch candidate_requested_resume-cf76db59-900c-4d40-aba2-11c7520121c5
Dispatching candidate_requested_artifacts — 1 available, batch candidate_requested_artifacts-63033d4d-b242-4b64-97e3-1525d69c4c41
Skipping candidate_requested_resume/karfo — no candidate or API key
[candidate_requested_resume] thread exited and cleared from registry
Loop mode candidate_requested_artifacts: 0 processed — stopping
Loop mode candidate_requested_resume: 0 processed — stopping
[candidate_requested_artifacts] thread exited and cleared from registry
[candidate_requested_resume] thread exited and cleared from registry
```

### Comments

#### chuckles — 2026-07-29T02:36:54.761Z
[thread-orphan] Cursor chat `2f96bb3a-9e52-4b2a-80a0-b832afadc55f` was not at the expected workspace path on **chuckles** (`/home/susan/.cursor/chats/a8ab9cb9f5a028a4c8ac3f46e952148c/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db`).

Blob-found at `/home/susan/.cursor/chats/0ab2adc851c7f84d4ce4bb00f485d83d/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db` — relocated to `/home/susan/.cursor/chats/a8ab9cb9f5a028a4c8ac3f46e952148c/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db` (same UUID; history kept). Continuing.

— Chuckles

#### chuckles — 2026-07-29T02:34:12.226Z
[thread-missing] Cursor chat `6ff95c7e-f0dd-493d-959d-7dfbeb8956ce` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/a8ab9cb9f5a028a4c8ac3f46e952148c/6ff95c7e-f0dd-493d-959d-7dfbeb8956ce/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `6ff95c7e-f0dd-493d-959d-7dfbeb8956ce`.

— Chuckles

#### susan — 2026-07-29T02:27:10.272Z
@chuckles Please refresh the description.

#### chuckles — 2026-07-29T02:26:42.887Z
@susan

Dispatch rejected — definition incomplete for AST-926 pre-defined contract:

* Missing **## Architectural definition** (pattern ids, or explicit `no established pattern applies` / new-pattern flag)
* Proposed child **#### 1** body missing **Citations** (pattern/statute ids, or `none` + why)

Note: AST-1022 + git refs already exist from an earlier partial dispatch — leave or cancel as you prefer after define refresh.

Please run define refresh, then Todo + assignee Chuckles again.

— Chuckles

#### susan — 2026-07-28T18:11:40.198Z
seed with auto OFF.

#### chuckles — 2026-07-28T17:59:22.394Z
@susan

1. Newly provisioned `candidate_requested_resume` / `candidate_requested_artifacts` rows currently seed with AUTO **on** (AST-972). After this fix, should **new** rows default to AUTO **off** (CLICK until you turn them on), or keep AUTO-on as the seed default and only fix “toggle off must stick / must not auto-run”?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
