# AST-856 — check_cover_letter not recognized as a valid task_key

<!-- linear-archive: AST-856 archived 2026-08-02 -->

## Linear archive (AST-856)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan administers dispatch through Scheduled Actions as the sole admin user. Saving a row for `check_cover_letter` fails with HTTP 400 even though that key appears in the task_key picker — a second, narrower allowlist blocks save while the dropdown lists every registered task key. Misapplied dispatch config should surface on the first run of the task, not as a UI barrier at save time. This ticket removes that save-time gate so picker and Save accept the same registered task keys.

## Functional scope

* Scheduled Actions task_key picker continues to list every registered task key; no additional allowlist filtering on what appears in the dropdown.
* Creating or updating a Scheduled Action accepts any task_key that is a registered task key — Save must not reject keys solely because they sit outside a separate "schedulable" allowlist (Susan's repro: `check_cover_letter`).
* Form defaults (entity type, trigger state, grouping metadata) may still be derived from the task registry and existing agent-task rows; Save must not require membership in that separate allowlist.
* First-run / dispatch execution remains the correctness check: a bad trigger state or entity pairing fails when the row runs, not when Susan clicks Save.
* Susan's repro (`check_cover_letter` selected, Save returns *Unknown or non-schedulable task_key*) is fixed without manually curating a second allowlist for each new artifact hop.

## Boundaries

* Admin-only Scheduled Actions surface — no change to Manage Tasks Run Next authoring.
* Does not remove the task registry itself or change prompt / run-next content.
* Does not add ordered pipeline step lists or new chain choreography.
* May retain blocking of explicitly **retired** dispatch keys (dead runtime paths) — not the artifact-hop allowlist gap Susan hit.
* Does not change dispatcher claim logic, Execution History, or debug logging beyond what is required to honor saved rows.
* Must not break save/run for existing dispatch rows already on `dev`.
* Code Rules §2.1 (config as single source of truth): Save acceptance for this admin surface must align with the same registered task catalog the picker already uses — dual catalogs for the same decision are out of scope to retain.

## Acceptance criteria

1. Susan can create a Scheduled Action dispatch row with `task_key=check_cover_letter` for candidate `somerset` without HTTP 400 — the error from the original brief no longer occurs.
2. Any other registered task key visible in the picker can be saved the same way (no *Unknown or non-schedulable task_key* for registered task keys).
3. Saving `check_job_resume` and `finalize_job_resume` continues to work unchanged.
4. A deliberately misconfigured row (wrong trigger state for the chosen task_key) is rejected or fails at **run** time, not at Save time — observable on first Run, not blocked at Save for merely being outside a separate schedulable allowlist.
5. Automated coverage asserts admin create acceptance for `check_cover_letter` and at least one regression case for an already-schedulable key.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Align Scheduled Actions Save with task_key picker | Admin create/update accepts every registered task key the picker already offers (except explicitly retired keys). Fixes Susan's `check_cover_letter` 400; leaves run-time validation as the place misconfigured trigger/entity pairings fail. Does not own Manage Tasks, chain choreography, or dispatcher claim changes. | Ada | — |

**Monolith check:** Functional scope has 5 capabilities; one child is intentional — one inseparable vertical slice (Save validation + admin create acceptance + regression coverage) must ship atomically for UAT.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) (parent) | ftr/AST-856-check-cover-letter-not-recognized |
| [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) | sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker |
| [AST-962](https://linear.app/astralcareermatch/issue/AST-962/uat-check-cover-letter-save-still-400-karfo) | sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo |

**Epic worktree:** `astral-AST-856/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 90d48e90-33af-4daa-b277-8bf96f33ceb6 |
| Betty | qa | 8749f09d-0270-4111-a466-ef7b3f18c8f2 |
| Radia | review | 3de309e0-3c3a-4280-ab6d-c24c6f866db5 |

---

## Original brief

```
Astral error diagnostic
timestamp: 2026-07-10T16:08:04.219Z
message: Unknown or non-schedulable task_key: 'check_cover_letter'
route: /admin/scheduled_actions
astral_candidate_id: somerset
api_path: /api/admin/dispatch_tasks
http_method: POST
http_status: 400
response_body:
{
  "error": "Unknown or non-schedulable task_key: 'check_cover_letter'"
}
```

It was in the dropdown list.

### Comments

#### chuckles — 2026-07-23T19:01:50.303Z
[check-linear] User Testing — regression still open (check_cover_letter task_key); @susan

— Chuckles

#### chuckles — 2026-07-23T18:34:20.125Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-962** | check_cover_letter Save still 400 (karfo) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-962** — _check_cover_letter Save still 400 (karfo)_
- **Issue reported:** On staging after the first ship, saving a Scheduled Action with `task_key=check_cover_letter` still returns HTTP 400:
- **Should now:** `POST /api/admin/dispatch_tasks` accepts `check_cover_letter` for any candidate (including `karfo`) without *Unknown or non-schedulable task_key* — same as any other registered task key visible in the picker. Misapplied trigger/entity should fail at first Run, not at Save for all
- **Quick check (this fix only):**
  1. Open `/admin/scheduled_actions` for candidate `karfo` (or any candidate).
  2. Add/Save a dispatch row with `task_key=check_cover_letter` and a valid job trigger state from the form.
  3. Observe HTTP 400 with `Unknown or non-schedulable task_key: 'check_cover_letter'`.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-23T18:11:17.811Z
@chuckles This issue is still occuring.

```
Astral error diagnostic
timestamp: 2026-07-23T18:10:33.974Z
message: Unknown or non-schedulable task_key: 'check_cover_letter'
route: /admin/scheduled_actions
astral_candidate_id: karfo
api_path: /api/admin/dispatch_tasks
http_method: POST
http_status: 400
response_body:
{
  "error": "Unknown or non-schedulable task_key: 'check_cover_letter'"
}
```

#### chuckles — 2026-07-22T22:34:31.808Z
@susan datt cannot run — parent is **Discussion** (not **Todo**), and Description still has no **## Proposed child tickets**. Paste the table from the prior comment, then move to **Todo** + Chuckles when ready.

— Chuckles

#### chuckles — 2026-07-22T22:07:56.481Z
@susan Still blocked — Description has no **## Proposed child tickets**. Todo + Chuckles alone is not enough (`dispatch-parent` §4). Paste the table from my prior comment (or your edit) under Open questions, keep **Todo** + Chuckles, then re-invoke.

— Chuckles

#### chuckles — 2026-07-22T22:06:25.735Z
@susan Dispatch blocked — parent Description has no **## Proposed child tickets** table (`dispatch-parent` §4). Cannot create children without your approved decomposition.

Proposed for this Bug (single coherent slice — save-time allowlist removal):

| Working title | What it delivers | Agent | Sequencing |
|---------------|------------------|-------|------------|
| Remove Scheduled Actions save-time schedulable allowlist | Drop `DISPATCH_SCHEDULABLE_TASK_KEYS` gate on `POST /api/admin/dispatch_tasks` so any `TASK_CONFIG` key in the picker can be saved; keep retired-key blocks; first-run remains the correctness check | Ada | alone |

If that row is right: paste it into Description as **## Proposed child tickets** (after Open questions), leave assignee Chuckles + **Todo**, and I will dispatch. Or edit the table / add rows if you want a split.

— Chuckles

#### chuckles — 2026-07-12T00:07:26.425Z
[check-linear] Discussion — scope aligned (@susan)

You're right — save-time rejection via **`dispatch_task_admin_defaults`** / **`DISPATCH_SCHEDULABLE_TASK_KEYS`** is what this ticket removes. **`finalize_job_resume`** and **`check_job_resume`** are already allowlisted; keys like **`check_cover_letter`** should save without that gate.

**Agreed scope:** picker = all **`TASK_CONFIG`** keys; **POST/PUT** accept any **`TASK_CONFIG`** key; drop allowlist membership and excessive save-time validation; misconfig surfaces on first dispatch run.

Definition already matches — approve/move to **Todo** when ready and I'll dispatch.

— Chuckles

#### susan — 2026-07-10T17:35:36.164Z
If that's the case, this is still wrong, because "finalize_job_resume" and "check_job_resume" were deemed "schedulable tasks".  Please remove this excessive data validation to avoid stupid UI barriers where if the config is misapplied, it will be instantly seen in the first run of the task.  THAT should be the scope of this ticket.  Populate the dropdown with all the tasks in TASK_CONFIG, no precious filtering.  The admin is the only user using this screen, and we don't need full belt-and-suspenders validation.

#### chuckles — 2026-07-10T16:47:09.638Z
[check-linear]

**Why `DISPATCH_SCHEDULABLE_TASK_KEYS` is separate from `TASK_CONFIG`**

They serve different jobs:

- **`TASK_CONFIG`** — runtime task registry: every `task_key` `do_task` may run, with `response_schema`, entity metadata, graded/scored flags, etc. Includes hops that exist only for **Manage Tasks / `run_next` chaining** (registry-only artifact hops), candidate-prep tasks (`craft_resume_base`), and other keys Susan authors but never schedules as a standalone dispatch row.

- **`DISPATCH_SCHEDULABLE_TASK_KEYS`** — **Scheduled Actions allowlist only**: keys that may appear on a `dispatch_task` DB row. Membership means config can supply **`dispatch_task_admin_defaults`** for that key — `entity_type`, `trigger_state`, `sort_by`, `batch_call_mode` — so the dispatcher knows **what queue to claim** and **which task_key to run first**.

**Not every `TASK_CONFIG` key belongs on that allowlist.** Example: `anticipate_scan` is in `TASK_CONFIG` (chain hop) but deliberately **not** in `DISPATCH_SCHEDULABLE_TASK_KEYS` (AST-520) — Susan wires it via `run_next`, not as a default schedulable row. Conversely, **`prefilter`** is schedulable but its dispatch metadata comes from **`ROSTER_CONFIG`**, not a `TASK_CONFIG` entry — so it can be in the allowlist without being in `TASK_CONFIG`.

**This bug:** `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses` were registered in `TASK_CONFIG` (AST-450) and should be schedulable mid-chain hops like `check_job_resume`, but were **never added** to `DISPATCH_SCHEDULABLE_TASK_KEYS`. The dropdown lists all `TASK_CONFIG` keys; save checks the allowlist — hence the mismatch.

**Fix for devs (unchanged):** add those three keys to `DISPATCH_SCHEDULABLE_TASK_KEYS` with the same BUILD_ARTIFACTS dispatch defaults as sibling resume hops — not collapse the two registries into one.

#### susan — 2026-07-10T16:33:30.944Z
Why does `DISPATCH_SCHEDULABLE_TASK_KEYS` exist independently from TASK_CONFIG?  @chuckles

#### chuckles — 2026-07-10T16:14:16.258Z
[check-linear]

**Scheduled Actions task_key dropdown** (`/admin/scheduled_actions` → Add/Edit form):

The picker is populated from **`GET /api/admin/dispatch_tasks/task_keys`**, which builds its key set in this order:

1. **Every key in `TASK_CONFIG`** via `get_task_keys()` (all entries in `config.py` `TASK_CONFIG` dict).
2. Plus any key in **`DISPATCH_SCHEDULABLE_TASK_KEYS`** not already in `TASK_CONFIG` (e.g. roster keys like `prefilter` that are not TASK_CONFIG entries).
3. Plus any **`task_key` already on an existing `dispatch_task` row** in the DB.
4. Minus **`admin_hidden_dispatch_task_keys()`** and **`DISPATCH_RETIRED_TASK_KEYS`**.

So the dropdown is **TASK_CONFIG-broad**, not limited to schedulable keys.

**Save validation is narrower:** **`POST /api/admin/dispatch_tasks`** accepts only keys in **`DISPATCH_SCHEDULABLE_TASK_KEYS`** (via `dispatch_task_admin_defaults`). That is why `check_cover_letter` appears in the picker (it is in `TASK_CONFIG`) but save returns *Unknown or non-schedulable task_key* (it is not yet in `DISPATCH_SCHEDULABLE_TASK_KEYS`).

**Not the same control as Manage Tasks → Run Next**, which uses a different admin surface (agent_task / save_agent_task validation).

**AST-856 fix scope:** add the missing BUILD_ARTIFACTS chain hops (`check_cover_letter`, `finalize_cover_letter`, `propose_application_responses`) to the schedulable set so picker and save align for those keys — not a one-off UI list.

#### susan — 2026-07-10T16:12:18.773Z
@chuckles Please let me know what determines the contents of the dropdown list on the UI, and whether it is definitively sourced by the TASK_CONFIG content, or if it is a one-off in config.py or otherwise.

Then confirm the source of truth used by the validation rules and confirm whether or not they are the same, and if not, where that source is determined.  Do that in the discussion phase of this bug so that the devs can simply fix it.

---

_Implementation detail may live in git history on `origin/dev`._
