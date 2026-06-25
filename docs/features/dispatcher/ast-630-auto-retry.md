# AST-630 — Auto retry

<!-- linear-archive: AST-630 archived 2026-06-23 -->

## Linear archive (AST-630)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-630/auto-retry  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Batch consult steps already route recoverable per-entity failures into companion `*_RETRY` holding states so a second dispatch pass can retry only the affected rows (AST-340). Today each Scheduled Action row claims and counts entities for a single `trigger_state`, so Susan must maintain duplicate dispatch rows (e.g. `qualify_job_listings` at `VALID_TITLE` and at `VALID_TITLE_RETRY`) or retry backlog sits invisible and unprocessed. This feature unifies claim and eligible-count behavior: a row whose input trigger is the primary state automatically includes the paired `trigger_state + "_RETRY"` when that retry state exists in the product registry. Per-entity retry routing must remain correct so a job or company already in a retry holding state cannot loop in retry forever.

## Functional scope

* When a dispatch task row’s `trigger_state` does **not** end with `_RETRY`, eligible-entity counting and batch claim for that row include entities in **both** the configured `trigger_state` and `trigger_state + "_RETRY"` when the suffix state is a valid job or company state in config (e.g. `VALID_TITLE` + `VALID_TITLE_RETRY`, `JD_READY` + `JD_READY_RETRY`, `WEBSITE_FOUND` + `WEBSITE_FOUND_RETRY`).
* When a dispatch task row’s `trigger_state` **already** ends with `_RETRY`, claim and count use **only** that retry state (no double suffix).
* Claim and count honor existing dispatch rules on the row: `candidate_id`, `entity_type`, `task_key`, `sort_by`, `batch_size`, `score_floor` / scored-claim gating (`dispatch_claim_uses_score_floor`), and company scan-interval overrides — applied uniformly across the combined state set.
* Batch consult processing that routes missing or invalid rows to retry vs error evaluates **each entity’s actual current state** when deciding the destination. A row whose trigger is the primary state may claim a mix of primary and retry entities; failures on entities already in `*_RETRY` must route to the configured error outcome, not back into the same retry holding state.
* Scheduled Actions **Available** counts reflect the combined eligible set for primary-trigger rows.
* Existing separate dispatch rows that target only a `*_RETRY` `trigger_state` continue to work; they do not also claim the primary state.

## Boundaries

* Does **not** add in-place duplicate API calls on a single dispatch run (envelope re-call — AST-340 parked design).
* Does **not** create, seed, or auto-insert new `dispatch_task` rows; Susan still configures rows in Scheduled Actions.
* Does **not** change `JOB_STATES` / company transition rules or invent new `*_RETRY` states (e.g. no new `PASSED_JD_RETRY` unless Susan adds it elsewhere first).
* Does **not** alter score-floor semantics: `*_RETRY` trigger rows remain non–score-gated at claim per current rules.
* Does **not** change which `task_key` runs on a row (AST-534 routing stays row-driven).
* Must not break triple-unique dispatch rows (`candidate_id`, `task_key`, `trigger_state`) or TO_WATCH multi-task-key routing (AST-535).

## Acceptance criteria

* A Scheduled Action with `trigger_state` `VALID_TITLE` and `task_key` `qualify_job_listings` shows an **Available** count equal to eligible jobs in `VALID_TITLE` plus eligible jobs in `VALID_TITLE_RETRY` (scoped to candidate and existing floor rules).
* Running that row claims and processes jobs from both states in one dispatch pass (subject to `batch_size` / chunk rules).
* After a failed second attempt, a job in `VALID_TITLE_RETRY` transitions to the qualify error outcome (not left in `VALID_TITLE_RETRY`).
* After a failed first attempt, a job in `VALID_TITLE` with recoverable batch failure still transitions to `VALID_TITLE_RETRY` when config provides that retry holding state.
* The same primary + `_RETRY` union behavior works for `JD_READY` / `JD_READY_RETRY` (`evaluate_jd`) and for company prefilter (`WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY` on `prefilter`).
* A row with `trigger_state` `VALID_TITLE_RETRY` claims only `VALID_TITLE_RETRY` jobs; failures on those jobs do not remain in `VALID_TITLE_RETRY`.
* Rows that intentionally target only a retry state (legacy seed or manual rows) behave as today — no regression in run or count.

## Dependencies and blockers

None — builds on shipped dispatch routing (AST-534), triple-unique rows (AST-535), and claim score-floor split (AST-586).

## Open questions

None.

---

## Original brief

Automatically search for the input trigger + input trigger & "_RETRY"

The "only retry once" logic should still recognize the input trigger state individually so that a RETRY goes to Error and does not stay in RETRY.

### Comments

#### chuckles — 2026-06-14T19:15:08.219Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-630 (parent) | ftr/ast-630-auto-retry |
| AST-641 | sub/AST-630/AST-641-union-claim-count |
| AST-642 | sub/AST-630/AST-642-per-entity-batch-retry |

**Epic worktree:** `astral-AST-630/` — one active sub checked out at a time.

**Parent:** AST-630

**Sequencing:** AST-642 blocked by AST-641 (Review Posted).

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
