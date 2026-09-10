# AST-896 — In the event of insufficient balance, do not transition state

<!-- linear-archive: AST-896 archived 2026-08-02 -->

## Linear archive (AST-896)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-896/in-the-event-of-insufficient-balance-do-not-transition-state  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When an LLM provider refuses a call because the account is out of balance or credit (HTTP 402 / "Insufficient Balance" and the same class of billing refusal), the pipeline must not treat that as a content or task failure on the entity. Jobs and companies should stay in their current loop-eligible state so work resumes automatically once credit is restored — instead of being walked into error or retry states that look like the work itself failed.

## Functional scope

* Recognize provider **balance / credit refusal** responses from agent model calls (HTTP 402 and messages such as Insufficient Balance, plus clearly equivalent credit-exhausted refusals from any provider used by the agent path).
* When such a refusal occurs on a call that would otherwise drive an entity state change, **do not** transition the job or company away from its current state. The entity remains in the same dispatch / loop pool it was already in.
* Preserve normal failure recording for the attempt (ledger, timesheet/audit, error return to the caller) so the refusal is visible in history — only the **state transition** is withheld.
* Leave all other agent failure classes on their existing routing: content/schema/entity hard failures and ordinary API/validation failures continue to use current error/retry behavior.
* When `debug=True` on a touched backend path that applies this hold rule: emit an index-style outcome that the refusal was classified as balance/credit and that entity state was held, plus a working-detail line with the refusal signal (status and/or message class) — following the backend debug contract (AST-538).

## Boundaries

* Does **not** cover rate limits (e.g. 429), timeouts, malformed responses, schema/grade validation failures, missing entity data, or scrape/I/O failures — those keep today's transition rules.
* Does **not** add payment top-up, wallet UI, or automatic provider billing repair.
* Does **not** introduce a global dispatcher pause or drain; this is per-entity state hold only.
* Does **not** change pass/fail scoring outcomes for successful model responses.
* Does **not** redefine JOB_STATES / COMPANY_STATES inventories; it only refuses to leave the current state on balance refusal.
* Config remains the source of truth for state names and retry/error destinations (Code Rules §2.1); this feature only gates when those transitions fire after a balance refusal.

## Acceptance criteria

1. Given an agent/model call that returns HTTP 402 (or an equivalent Insufficient Balance / credit-exhausted refusal), the affected job or company **state string is unchanged** after the call completes.
2. The same entity remains eligible for the same dispatch/loop work it was eligible for before the refusal (it was not moved into an error or retry holding state solely because of the balance refusal).
3. Given a non-balance agent failure that already transitions to error or retry today, behavior is unchanged (entity still leaves the loop as before).
4. The refusal attempt is still observable in existing failure/history surfaces (not silently dropped).
5. With `debug=True` on a covered backend run, logs show that balance/credit refusal was recognized and that state was held (index outcome + working detail per AST-538).

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-896 (parent) | ftr/AST-896-insufficient-balance-hold-state |
| AST-897 | sub/AST-896/AST-897-hold-entity-state-balance-refusal |

**Epic worktree:** `astral-AST-896/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | a2d0da22-c8d0-499b-ae9e-7c8560dc9637 |
| Betty | qa | 4b563fe3-8399-4a74-8915-db94da7e263d |
| Radia | review | 90a43965-5b65-433e-85a0-9dcb84b96b75 |

---

## Original brief

If the agent response is 402 - {'error': {'message': 'Insufficient Balance', or similar, do not transition the entity state, just let it remain in the "loop"

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
