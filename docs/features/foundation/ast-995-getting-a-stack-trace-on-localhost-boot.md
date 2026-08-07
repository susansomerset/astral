# AST-995 — getting a stack trace on localhost boot

<!-- linear-archive: AST-995 archived 2026-08-05 -->

## Linear archive (AST-995)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-995/getting-a-stack-trace-on-localhost-boot  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Localhost boot prints a stack trace during scheduler start: candidate stage-dispatch provisioning (from [AST-972](https://linear.app/astralcareermatch/issue/AST-972/dispatch-and-stale-eligibility-for-candidate-stages-candidate-state)) calls a data-layer helper that is missing on the tree Susan runs. Flask still comes up, but the failure is noisy, breaks trust in local boot, and means stage-dispatch rows are not provisioned at start. Restore a clean boot where that provision path runs without AttributeError and matches the AST-972 contract already expected by the dispatcher and component tests.

## Functional scope

* **Boot-time stage provision without AttributeError.** On localhost (and any environment that starts the scheduler), candidate stage-dispatch provisioning completes without raising AttributeError for a missing candidate-id listing helper.
* **Listing helper contract restored.** The data layer again exposes the listing of candidate ids that already own at least one dispatch_task row, so provision can iterate those candidates as designed by AST-972.
* **Scheduler continues cleanly.** After provision, the scheduler still starts on its normal tick; success or intentional empty provision does not leave a traceback in boot logs.

## Boundaries

* Does **not** redesign the candidate state machine ([AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)) or reopen AST-972 / [AST-973](https://linear.app/astralcareermatch/issue/AST-973/legacy-candidate-migration-consumers-and-dispatchtask-config-keys) product scope.
* Does **not** change craft prompts, claim/resolve behavior for REQUESTED_* beyond making provision callable again.
* Does **not** change Stytch, Vite, or unrelated boot messages in the pasted log.
* Does **not** own finish-up of AST-871 (parent is PR Ready separately) — but this gap must be closed on the integration tree so finish-up does not perpetuate the break.
* Code Rules: data layer raises; caller (dispatcher) logs — keep that split; no new hardcoded state sets (§2.1).
* **Assignees:** Child Linear **assignee** is always the implementing engineer in the Proposed table (Ada for #1), with short flips only to Joan / Betty / Radia at their gates. **Never** assign a child to Chuckles. A **sub-chuck** is a Chuckles **Thread** that orchestrates that child's pipeline — it is **not** a Linear assignee and must not replace the engineer on the ticket.

## Acceptance criteria

1. Fresh localhost boot no longer prints `AttributeError: module 'src.data.database' has no attribute 'list_candidate_ids_with_dispatch_tasks'` (or equivalent) during scheduler start.
2. Boot no longer prints `AST-972 stage dispatch provision failed` caused by that missing helper.
3. With at least one candidate that already has a dispatch_task row, boot-time provision can enumerate that candidate and run without the AttributeError.
4. With no such candidates, boot still starts the scheduler without a traceback from this path.
5. Existing component coverage that asserts the listing helper / provision path remains meaningful (green for this contract).

## Dependencies and blockers

* Related cause: helper introduced under AST-972 was dropped on the AST-973 land into the composite tree; AST-871 is PR Ready. None blocking start of this fix.
* Soft adjacency: AST-871 finish-up — prefer this fix on `origin/dev` (and `ftr` if still diverged) before or as part of landing so the shipped candidate epic stays coherent.
* Child already dispatched: [AST-1000](https://linear.app/astralcareermatch/issue/AST-1000/restore-stage-dispatch-provision-helper-getting-a-stack-trace-on) — keep engineer assignee Ada (not Chuckles) when pipeline resumes.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Restore stage-dispatch provision helper | Reintroduce the missing data-layer candidate-id listing used by boot-time stage-dispatch provision; confirm localhost boot no longer AttributeErrors on that path. Does **not** own candidate state vocabulary or AST-973 migration logic beyond not regressing it. **Linear assignee = Ada** (never Chuckles; sub-chuck Thread is separate). | Ada | — |

**Monolith check:** Functional scope has 3 capabilities; 1 proposed child — intentional single vertical slice (helper + boot provision path must ship together for UAT).

**New patterns:** none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-995 (parent) | ftr/AST-995-localhost-boot-stack-trace |
| AST-1000 | sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper |

**Epic worktree:** `astral-AST-995/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files. Engineer / Betty / Radia rows are shared agent Threads — **not** a reason to put Chuckles on the child assignee field.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | f39c0e30-d503-4ccc-bbd5-86dc81618bf7 |
| Betty | qa | 02311ee8-82fb-456f-9595-e566df73b155 |
| Radia | review | dc9419d4-1161-421f-97b8-a5cb11d2b0cf |

---

## Original brief

```
flask-api http://localhost:5001 (Ctrl-C to stop)
tip: vite live-reload at http://localhost:5173 — launch.sh --vite
Stytch auth configured: env=test project_id=project-test-3c7ad997-81ae-4ca1-…
repo_admin_json applied table=agent rows=6
repo_admin_json applied table=agent_task rows=38
AST-972 stage dispatch provision failed
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 956, in start_scheduler
    stats = provision_candidate_stage_dispatch_tasks()
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 202, in provision_candidate_stage_dispatch_tasks
    for cid in database.list_candidate_ids_with_dispatch_tasks():
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'src.data.database' has no attribute 'list_candidate_ids_with_dispatch_tasks'
Scheduler started — tick every 3min, max_auto_threads=3
 * Serving Flask app 'server'
 * Debug mode: on
Dispatching candidate_requested_resume — 1 available, batch candidate_requested_resume-aba13de2-998a-4a04-9b1c-f92a81c4cd29
Dispatching candidate_requested_artifacts — 1 available, batch candidate_requested_artifacts-4d30767a-2d65-41ae-8ff8-460ec9d6ebe9
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5001
Press CTRL+C to quit
 * Restarting with stat
Loop mode candidate_requested_artifacts: 0 processed — stopping
Loop mode candidate_requested_resume: 0 processed — stopping
Stytch auth configured: env=test project_id=project-test-3c7ad997-81ae-4ca1-…
[candidate_requested_resume] thread exited and cleared from registry
[candidate_requested_artifacts] thread exited and cleared from registry
repo_admin_json applied table=agent rows=6
repo_admin_json applied table=agent_task rows=38
AST-972 stage dispatch provision failed
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 956, in start_scheduler
    stats = provision_candidate_stage_dispatch_tasks()
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 202, in provision_candidate_stage_dispatch_tasks
    for cid in database.list_candidate_ids_with_dispatch_tasks():
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'src.data.database' has no attribute 'list_candidate_ids_with_dispatch_tasks'
Scheduler started — tick every 3min, max_auto_threads=3
 * Debugger is active!
 * Debugger PIN: 526-743-827
Dispatching candidate_requested_resume — 1 available, batch candidate_requested_resume-f1b0672e-04e8-49a1-a50c-34fc2c989318
Dispatching candidate_requested_artifacts — 1 available, batch candidate_requested_artifacts-4bcaaa2f-b862-4a5a-822e-b38c59d69a64
Loop mode candidate_requested_artifacts: 0 processed — stopping
Loop mode candidate_requested_resume: 0 processed — stopping
[candidate_requested_artifacts] thread exited and cleared from registry
[candidate_requested_resume] thread exited and cleared from registry
/Users/susan/chuckles/astral/.venv/lib/python3.12/site-packages/stytch/core/client_base.py:86: UserWarning: Test version of Stytch not intended for production use
  warnings.warn("Test version of Stytch not intended for production use")
127.0.0.1 - - [27/Jul/2026 17:30:30] "GET /api/deploy_status HTTP/1.1" 200 -
127.0.0.1 - - [27/Jul/2026 17:30:30] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -
```

### Comments

#### chuckles — 2026-07-28T04:01:35.235Z
@susan Revised Description: Boundaries + Proposed child tickets now state child Linear assignee = Ada (engineer flips only for Joan/Betty/Radia) — never Chuckles; sub-chuck is Thread-only orchestration. Reassigned AST-1000 → Ada.

— Chuckles

#### chuckles — 2026-07-28T04:01:25.739Z
[check-linear] Discussion — AST-1000 is Joan for validate-plan; Proposed implementer Ada (not Chuckles) (@susan)

#### susan — 2026-07-28T03:54:22.608Z
@chuckles We had some confusion here about child issues being run by "sub-Chuck drones" and assigning them to the chuckles user instead of the dev user.  Please revise the description and reassign the child tickets before you proceed.

---

_Implementation detail may live in git history on `origin/dev`._
