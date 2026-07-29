# AST-873 — Add “set dispatch tasks” button

<!-- linear-archive: AST-873 archived 2026-07-29 -->

## Linear archive (AST-873)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-873/add-set-dispatch-tasks-button  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Admin operators need to provision a candidate with the same dispatch schedule that already works for Somerset — without hand-entering dozens of Scheduled Actions rows. Manage Candidates should show how many dispatch tasks each candidate already has and offer one action that materializes the configured template candidate’s full live set onto that candidate, including the AUTO flag and the rest of each row’s scheduling metadata, so the candidate is ready for dispatch without reinventing the schedule.

## Functional scope

* On the Manage Candidates list, each candidate row shows a count of dispatch tasks currently assigned to that candidate.
* Each candidate row exposes a **Set dispatch tasks** control.
* Activating that control upserts, for the chosen candidate, a full set of dispatch-task rows taken from the live set belonging to the **template candidate**. The template candidate id is defined in product config (default **Somerset** / `somerset`) and is looked up at upsert time — not hard-coded in the UI action.
* Upsert identity follows the existing uniqueness of candidate + task key + trigger state: matching rows on the target are updated; missing ones are created.
* After the upsert, any target rows whose (task key, trigger state) are **not** in the template set are **deleted**, so the target’s dispatch-task set matches the template exactly.
* Copied/updated schedule fields include the AUTO flag (`auto_mode`) and all other scheduling metadata on the template rows (entity type, trigger state, sort, batch call mode, frequency, min count, batch size, max runs, score floor, debug, skip cache, and any other persisted schedule fields on those rows). Runtime fields `last_run_at` and `batch_id` on the target are **cleared** (not copied from the template; not preserved from a prior target row).
* The action mirrors the template candidate’s live set — it does not invent a parallel hardcoded task catalog.
* After a successful set, the Manage Candidates count for that candidate reflects the resulting row count via the normal list refresh.
* The action writes schedule rows only; it does not start dispatcher runs.

## Boundaries

* Does not redesign Scheduled Actions UI or the backlog Candidate Actions refactor (**AST-737**).
* Does not add or retire schedulable task keys; does not reintroduce a retired seed dictionary of dispatch defaults (config remains the behavioral source of truth — Code Rules §2.1). Template source is a config-defined candidate id, not a second task catalog.
* Does not copy companies, jobs, dispatch ledger history, agent prompts, or candidate profile/intake data.
* Does not change dispatcher claim/eligibility logic beyond the natural effect of new, updated, or deleted schedule rows.
* Must not break existing per-candidate Scheduled Actions edit and run flows.

## Acceptance criteria

1. Manage Candidates shows an accurate per-candidate count of dispatch-task rows.
2. An admin can run **Set dispatch tasks** for a target candidate and afterward that candidate’s dispatch-task set exactly matches the config template candidate’s set: one row per template (task key, trigger state), with AUTO and other schedule metadata matching the template; extras on the target are gone.
3. After the set, every target row has `last_run_at` and `batch_id` cleared.
4. Re-running the action is idempotent as an upsert-plus-prune: it does not create duplicate (candidate, task key, trigger state) rows and leaves the target matching the template again.
5. The action does not enqueue or execute dispatcher batches by itself.
6. After the set, Scheduled Actions for the target candidate shows the resulting rows with the expected AUTO values and schedule metadata.

## Dependencies and blockers

none.

## Open questions

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-873 (parent) | ftr/AST-873-set-dispatch-tasks-button |
| AST-875 | sub/AST-873/AST-875-template-dispatch-task-set-upsert |
| AST-876 | sub/AST-873/AST-876-manage-candidates-set-dispatch-tasks |

**Epic worktree:** `astral-AST-873/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | fbe69861-b88b-4e4f-8ba3-dd4f05264fcb |
| Katherine | engineer | e82e7284-4367-4dbf-9678-bbd4beada0e4 |
| Betty | qa | ededac8d-0379-4c2e-8972-553d7b5e2a71 |
| Radia | review | d63281e4-c750-4cff-ab2e-2f7823c2b29f |

---

## Original brief

On manage candidate list, show a count of dispatch tasks assigned to the candidate and add a "set dispatch tasks" button that will upsert a full set of dispatch tasks for the candidate in the dispatch-task table, using the set for 'Somerset' as the default set. Include the autoflag setting as well as all other metadata for all records.

### Comments

#### chuckles — 2026-07-12T18:01:24.104Z
@susan

1. If the target already has dispatch-task rows whose (task key, trigger state) are **not** in Somerset’s set, should **Set dispatch tasks** delete those extras so the target matches Somerset exactly, or leave them and only upsert Somerset’s keys?
2. For runtime fields on each row (`last_run_at`, `batch_id`): when upserting onto the target, clear them for the target, copy from Somerset, or leave existing target values unchanged on update?
3. Is the template source always candidate id `somerset`, or should the UI allow choosing another candidate’s set with Somerset as the default?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
