# AST-799 — Over-validation on entity type for candidate

<!-- linear-archive: AST-799 archived 2026-07-22 -->

## Linear archive (AST-799)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-799/over-validation-on-entity-type-for-candidate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Administrators configure automated batch work from Scheduled Actions by pairing a schedulable task_key with a trigger_state on a candidate-scoped dispatch row. Config and the dispatcher already treat **candidate** as a first-class entity type (including weekly **inflow_discovery** at **LIVE_PROMPTS**), but the admin save path rejects those rows with "unsupported entity_type 'candidate'". That blocks configuring roster inflow from the UI and will recur whenever a new candidate-scoped dispatch task is added unless validation stays aligned with config. **Project:** Astral Foundation (config-driven validation domain). This epic makes Scheduled Actions acceptance match **ENTITY_TYPES** and the existing dispatch defaults — one validation story, not parallel job/company-only rules.

## Functional scope

* **Unblock candidate-scoped dispatch saves:** Saving or updating a dispatch task row whose config-derived entity_type is **candidate** (starting with **inflow_discovery**) succeeds from Admin → Scheduled Actions when task_key and trigger_state are valid per config — no "unsupported entity_type" error for types listed in **ENTITY_TYPES**.
* **Candidate trigger_state validation:** trigger_state for candidate entity_type is validated against **CANDIDATE_STATES** using the same pattern already used for job (**JOB_STATES**) and company (**COMPANY_STATES**) rows.
* **Single source of truth for validation:** Admin task_key + trigger_state acceptance is driven by the same config-derived dispatch defaults used when seeding and running tasks, not a separate partial allowlist that omits entity types config already supports.
* **Prevent recurrence:** Adding a schedulable task_key whose entity_type is any member of **ENTITY_TYPES** does not require a one-off admin API branch to become saveable in Scheduled Actions.
* **Admin state options (if needed for edit UX):** If the Scheduled Actions UI relies on state-options for trigger_state dropdowns, candidate states are exposed when editing candidate-scoped rows so **CANDIDATE_STATES** keys (e.g. **LIVE_PROMPTS**) are selectable without manual API calls.

## Boundaries

* Does **not** change inflow discovery search, vet, ingest, or dispatcher batch execution — only admin acceptance of valid dispatch row configuration.
* Does **not** reintroduce retired entity types (e.g. legacy **board_search** rows) as schedulable; AST-781-style tolerant **available** counts for invalid legacy rows remain out of scope unless the same row surfaces a new regression.
* Does **not** redesign Scheduled Actions layout, task grouping, or edit-modal task_key picker (AST-773).
* Must **not** break existing job- or company-scoped dispatch save/update validation.

## Acceptance criteria

1. **Susan's repro cleared:** PUT on an **inflow_discovery** dispatch row for a live candidate (e.g. somerset / id 5373) with trigger_state **LIVE_PROMPTS** returns success — not HTTP 400 with `unsupported entity_type 'candidate'`.
2. **Scheduled Actions edit path:** From Admin → Scheduled Actions, an existing **inflow_discovery** row can be edited and saved without error when values match config defaults.
3. **Invalid candidate state still rejected:** A candidate-scoped task_key with a trigger_state **not** in **CANDIDATE_STATES** is rejected with a clear error (behavior parallel to invalid job/company states).
4. **Regression:** Job- and company-scoped dispatch task save/update behavior unchanged for representative task_keys (e.g. **grade_do**, **vet_inflow_discovery**).
5. **Future-proofing:** A schedulable task_key whose config-derived entity_type is **candidate**, **company**, or **job** per **ENTITY_TYPES** is saveable without adding entity-type-specific branches only in the admin layer.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-799 (parent) | ftr/AST-799-dispatch-task-entity-type-validation |
| AST-804 | sub/AST-799/AST-804-dispatch-task-admin-candidate-entity-validation |
| AST-807 | sub/AST-799/AST-807-uat-prep-uat-merge-ticket-log-rebuild-uses-venv |

**Epic worktree:** `astral-AST-799/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | 4c5c67bc-4a28-4b9f-beae-0e2cf7b66ae1 |
| Betty | qa | 4416f98d-0686-4d1c-bc81-69a1db27517c |
| Radia | review | 10258008-af06-4654-bf34-4df7b0168847 |
| Ada | engineer | 3957c0e4-122e-4053-9809-d97983bba2e0 |

---

## Original brief

While in discussion, research the validation logic for the entity types and how and where they are established in the code.  Explain how this is inefficient and difficult to maintain over time, and recommend a change that will correct issues of this kind from occurring in the future, as well as resolving this issue.

Astral error diagnostic

timestamp: 2026-06-25T01:34:25.226Z

message: task_key 'inflow_discovery' has unsupported entity_type 'candidate'

route: /admin/scheduled_actions

astral_candidate_id: somerset

api_path: /api/admin/dispatch_tasks/5373

http_method: PUT

http_status: 400

response_body:

{

"error": "task_key 'inflow_discovery' has unsupported entity_type 'candidate'"

}

### Comments

#### chuckles — 2026-07-03T00:01:32.199Z
[check-linear] Done — finish-up AST-799 still pending (origin/ftr/AST-799-* refs remain) (@susan)

— Chuckles

#### susan — 2026-06-26T02:25:46.459Z
Trying this again…. Go ahead and finish-up, @chuckles.

#### chuckles — 2026-06-26T02:19:29.052Z
[check-linear] PR Ready > finish-up — queued on your signal (@susan)

— Chuckles

#### susan — 2026-06-26T02:12:40.282Z
Please `finish-up AST-799` when you see this, @chuckles.

#### chuckles — 2026-06-26T02:09:03.998Z
[check-linear] PR Ready > finish-up (@susan)

Yes — **finish-up AST-799** is the next step: open ftr→dev PR, land on origin/dev, delete ftr/sub refs, move parent + shipped children to Done. Say **`finish-up AST-799`** in chat or move is already PR Ready with assignee Chuckles for the [wrap] watcher.

— Chuckles

#### susan — 2026-06-26T02:01:44.770Z
@chuckles What's next for this ticket?  can you finish-up?

#### chuckles — 2026-06-26T01:03:19.322Z
[check-linear] PR Ready — confirmed: `origin/ftr/AST-799-dispatch-task-entity-type-validation` is on origin/dev; prep-uat ran (5743c3b). Tooltip gap: later prep-uat(AST-810) rebuild dropped AST-799 from `data/merge_ticket_log.json` on dev (788 remains; 801/799 dropped). AST-811 rebuild fix in User Testing (@susan)

#### chuckles — 2026-06-25T17:31:22.594Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-807** | AST-799 missing from deploy tooltip after prep-uat (record-landed-parent python) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-807** — _AST-799 missing from deploy tooltip after prep-uat (record-landed-parent python)_
- **Issue reported:** After AST-799 prep-uat, Susan reports the parent does not appear in the admin deploy environment label tooltip list of merged UAT tickets (same class as AST-788 / AST-801): *"I don't see this in the list of UAT tickets that have been merged."*
- **Should now:** After prep-uat completes for AST-799, `data/merge_ticket_log.json` on `origin/dev` includes **AST-799** (AST-800 rebuild semantics), and hovering the deploy env label lists AST-799 among User Testing parents whose ftr is on dev.
- **Quick check (this fix only):**
  1. Land AST-799 via prep-uat (`ftr/AST-799-dispatch-task-entity-type-validation` merged to `origin/dev`).
  2. Open Admin (local dev or staging with `LINEAR_API_KEY` set).
  3. Hover the deploy environment label footer tooltip.
  4. **AST-799** is missing from the merge ticket list.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-25T17:01:31.771Z
@chuckles as with 788 and 801, I don't see this in the list of UAT tickets that have been merged.

#### chuckles — 2026-06-25T05:40:01.884Z
[check-linear] answered (@susan)

**Why `dispatch_task.entity_type` exists:** The table is the runtime scheduling source of truth — each row must tell the dispatcher which entity pool to claim from (job / company / candidate) without re-deriving from `task_key` on every due-task scan. Values are copied from config dispatch defaults at seed/save so claim, sort, and eligibility stay aligned with config.

**vs TASK_CONFIG:** `TASK_CONFIG` entity_type applies to agent/consult hops; not every schedulable `task_key` has a TASK_CONFIG row (e.g. `inflow_discovery`). Dispatch routing uses the dispatch-defaults path, not TASK_CONFIG alone.

**This epic:** Keep the column — align admin save validation with those defaults and `ENTITY_TYPES`; do not remove the denormalized field.

#### susan — 2026-06-25T05:37:16.155Z
I have often wondered: why are we storing the entity type on the dispatch task record to begin with? It's already set in config.py for task_config, isn't it? @chuckles

#### chuckles — 2026-06-25T02:00:51.658Z
[check-linear] Discussion — definition updated; Open questions cleared (@susan)

#### susan — 2026-06-25T01:57:00.851Z
Astral Foundation (config-driven validation domain)

#### chuckles — 2026-06-25T01:38:53.104Z
@susan

1. **Linear project:** Ticket currently has no project — assign **Astral Interface** (admin Scheduled Actions) or **Astral Roster** (inflow_discovery domain)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
