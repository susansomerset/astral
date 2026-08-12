# AST-895 — NEW jobs are going to VALID_TITLE_RETRY state

<!-- linear-archive: AST-895 archived 2026-08-02 -->

## Linear archive (AST-895)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-895/new-jobs-are-going-to-valid-title-retry-state  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

After qualify moved to claim jobs in **NEW** (post **AST-797**), recoverable first-attempt failures from that pipeline still land in **VALID_TITLE_RETRY** — the companion holding state from when qualify triggered on **VALID_TITLE**. That mismatches the current trigger and strands retries under the wrong state name. This epic corrects first-attempt retry routing so jobs that enter qualify from **NEW** get one retry via **NEW_RETRY**, consistent with the primary→`*_RETRY` holding-state pattern used elsewhere.

## Functional scope

* When a job enters `qualify_job_listings` from **NEW** and hits a recoverable first-attempt failure (the same class of failures that today send a job to a retry holding state rather than a terminal qualify error/fail), it transitions to **NEW_RETRY** — not **VALID_TITLE_RETRY**.
* **NEW_RETRY** is a registered job holding state with correct priors so transitions into and out of it are valid.
* Jobs in **NEW_RETRY** are claimed and processed by the primary `qualify_job_listings` dispatch row whose trigger is **NEW** (companion claim), so the second attempt runs without requiring a separate **VALID_TITLE_RETRY**-only schedule.
* A recoverable failure on a job already in **NEW_RETRY** routes to the configured terminal qualify error outcome — no second holding-state hop (one-retry rule).
* On the second attempt from **NEW_RETRY**, only the qualify AI hop runs — title screening does not re-run (title screening already happened before or at the **NEW** entry; Susan decision).
* Successful and non-retryable qualify outcomes (pass, fail grades, invalid title from title screen, hard/terminal errors) stay on their existing destinations; this epic only corrects which holding state receives first-attempt recoverable retries for the **NEW** qualify path.
* Operator-visible job state labels include **NEW_RETRY** so the holding state is recognizable in admin/UI state lists.
* Jobs already in **VALID_TITLE_RETRY** when this ships are left as-is to drain on the existing **VALID_TITLE_RETRY** companion path (Susan: leave it — no migrate-to-**NEW_RETRY** backfill).
* After cutover, **VALID_TITLE_RETRY** is fully retired for new routing: no new transitions into it from the **NEW** qualify path; retire the state/companion schedule for greenfield behavior once drain is complete per plan (Susan: fully retire).

## Boundaries

* Does not change qualify grading math, pass/fail thresholds, or which AI hop decides pass vs fail.
* Does not restore a separate `validate_title` dispatch task; inline title screening for **NEW** remains.
* Does not change other job retry pairs (**JD_READY** / **JD_READY_RETRY**, etc.) or company roster retry holding states.
* Does not redesign the rest of the job state machine beyond what is required for **NEW** ↔ **NEW_RETRY** and retirement of **VALID_TITLE_RETRY** for new traffic.
* Does not migrate existing **VALID_TITLE_RETRY** jobs to **NEW_RETRY** (they drain in place).
* Must not break companion-claim / one-retry contracts from **AST-630** / **AST-642** for other states.
* Config remains source of truth for state names and retry pairing (**ASTRAL_CODE_RULES** §2.1 / **JOB_STATES**).

## Acceptance criteria

1. A job that enters `qualify_job_listings` in **NEW** and suffers a recoverable first-attempt failure ends in **NEW_RETRY** (observable on the job record) — never newly transitioned to **VALID_TITLE_RETRY** by that path.
2. A job in **NEW_RETRY** is included in Available / claim for `qualify_job_listings` when the Scheduled Action trigger is **NEW**.
3. A recoverable failure on a job already in **NEW_RETRY** moves it to the configured terminal qualify error state — it does not remain in or re-enter **NEW_RETRY**.
4. A second attempt from **NEW_RETRY** runs the qualify AI hop without re-running title screening.
5. A clean second-attempt succeed/fail grade path from **NEW_RETRY** still reaches the same pass/fail outcomes as a successful first-attempt qualify (no permanent stuck state solely because the job retried).
6. Admin/UI job state lists that surface configured job states include **NEW_RETRY** with a clear label.
7. After cutover, new recoverable first-attempt failures from the **NEW** qualify path do not enter **VALID_TITLE_RETRY**; that holding state is retired for new traffic (existing **VALID_TITLE_RETRY** jobs may remain until they drain).
8. With `debug=True` on the touched qualify / batch-failure routing path: per-job index headers (Style D) show identity and destination state; working detail lines use `|` and include enough context to see **NEW** → **NEW_RETRY** vs **NEW_RETRY** → terminal.

## Dependencies and blockers

none. Prior cutover **AST-797** (Done) established qualify @ **NEW**; this epic corrects the leftover retry companion naming/routing.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-895 (parent) | ftr/AST-895-new-retry-qualify-holding |
| AST-898 | sub/AST-895/AST-898-new-retry-qualify-holding |

**Epic worktree:** `astral-AST-895/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 0310c1d5-e436-4f0b-a8c8-b3beced515ab |
| Betty | qa | bc2a5982-1de4-4a2b-89b5-a880a6a4e4fc |
| Radia | review | d6e7752d-7cc9-4baf-b018-c49362e01f0c |

---

## Original brief

Should go to NEW_RETRY state.

### Comments

#### chuckles — 2026-07-15T04:32:05.277Z
@susan dispatch blocked — Open questions 1–3 still unanswered (VALID_TITLE_RETRY migrate vs drain; retire vs keep; NEW_RETRY title-screen again?). Answer in Description or comment, then reassign Chuckles on Todo to resume.

— Chuckles

#### chuckles — 2026-07-15T03:41:09.206Z
@susan
1. Jobs already in VALID_TITLE_RETRY when this ships — migrate to NEW_RETRY, drain on the existing companion row, or other?
2. Retire VALID_TITLE_RETRY (state + qualify companions) after cutover, or keep temporarily for drain/legacy?
3. Second attempt from NEW_RETRY — re-run title screening, or only the qualify AI hop?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
