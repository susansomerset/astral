# AST-1797 — _RETRY suffix issues

<!-- linear-archive: AST-1797 archived 2026-10-02 -->

## Linear archive (AST-1797)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1797/retry-suffix-issues  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

A `prefilter` (or any company) dispatch row with `trigger_state=HOMEPAGE_READY` claims and counts both `HOMEPAGE_READY` and `WEBSITE_FOUND_RETRY`, because `dispatch_claim_states` prefers `COMPANY_STATES["HOMEPAGE_READY"]["retry_state"]` (`WEBSITE_FOUND_RETRY`) over the `{trigger}_RETRY` name. Live tip returns `['HOMEPAGE_READY', 'WEBSITE_FOUND_RETRY']`. Companion pairing is gated on registry membership / `retry_state` config rather than a strict suffix of the trigger.

## To-be

Claim/count companions are **only** the trigger state plus `trigger_state + "_RETRY"` WHETHER OR NOT that companion key exists in the entity registry. The registry should NOT error when a state has a matching registry item that STARTS with the string, and do not validate suffix content. A `HOMEPAGE_READY` row therefore claims `HOMEPAGE_READY` and `HOMEPAGE_READY_RETRY` — never `WEBSITE_FOUND_RETRY` via an arbitrary `retry_state` config field. Registry `retry_state` may still describe failure *routing* destinations; it must not drive claim grouping. This is true for ALL `dispatch_task` records, no exceptions for entity type or task key.

## Proposed steps

1. Change `dispatch_claim_states` in `src/utils/config.py`: drop registry-`retry_state` preference (AST-882) and drop the “companion must be in registry” gate. Primary trigger → always `[ts, f"{ts}_RETRY"]`; trigger already ending `_RETRY` → `[ts]` only. Same rule for every `entity_type` / task key — no special cases.
2. Ensure callers that validate claim states against the entity registry do **not** error or strip the suffix companion when `{ts}_RETRY` is absent from the registry, and do not validate suffix content beyond the literal `"_RETRY"` append (no prefix/cross-name matching into another state’s `retry_state`).
3. Leave scrape ownership of `WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY` on `fetch_website` alone except insofar as claim pairing becomes suffix-only; do not reintroduce cross-named claim unions from `HOMEPAGE_READY`.
4. Update unit coverage that asserts `HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY` (or requires companion ∈ registry) to expect always `[HOMEPAGE_READY, HOMEPAGE_READY_RETRY]` and equivalent suffix pairs for other primaries.

## Component scope

* `src/utils/config.py` — modified: `dispatch_claim_states` companion rule (suffix-only, always; no `retry_state`, no registry membership gate); any helper it calls that still validates companion registry membership.
* `src/data/database.py` and/or claim callers — modified only if they reject or error when a claim-state list includes a `{ts}_RETRY` not present in the entity registry (must accept the paired suffix without validating suffix content).
* `tests/component/utils/test_config.py` — modified: claim-state assertions for suffix-always pairing (including `HOMEPAGE_READY` → `HOMEPAGE_READY_RETRY`, never `WEBSITE_FOUND_RETRY`).

## Technical scope

* `src/utils/config.py` — modified function `dispatch_claim_states`: remove the branch that returns `[ts, registry[ts].retry_state]`; remove `if companion in registry` gating; always append `f"{ts}_RETRY"` for non-`_RETRY` triggers across job/company/candidate/meteorite. Do not invent cross-name companions from config.
* Claim/count callers (`src/data/database.py` and thin dispatcher/roster/tracker plumbing only if they currently validate every claim state ∈ registry) — modified validation: allow the suffix companion without erroring or requiring a registry entry; do not treat “starts with primary” as license to pull a different state’s `retry_state`.
* `tests/component/utils/test_config.py` — modified tests: primary → always two-state suffix list; missing companion key in registry is fine (no error); `HOMEPAGE_READY` never unions `WEBSITE_FOUND_RETRY`.

## Ancestor candidates

- [ ] AST-882 — Prefilter one-retry / error (`docs/features/roster/ast-882-prefilter-one-retry-error.md`) — introduced preferring registry `retry_state` over `{ts}_RETRY` so `HOMEPAGE_READY` claims `WEBSITE_FOUND_RETRY` (direct cause of this bug)
- [ ] AST-641 — Union claim and count for primary + `_RETRY` (`docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md`) — original suffix `dispatch_claim_states` design (still gated on registry membership — this bug removes that gate)
- [ ] AST-702 — Batch prefilter evaluate phase (`docs/features/consult/ast-702-batch-prefilter-evaluate-phase.md`) — set `COMPANY_STATES["HOMEPAGE_READY"]["retry_state"] = "WEBSITE_FOUND_RETRY"` (the cross-name config AST-882 later read for claim)
- [ ] AST-630 — Auto retry parent (`docs/features/dispatcher/ast-630-auto-retry.md`) — epic that defined primary + `trigger+"_RETRY"` union claim behavior

## Original report

Dispatch is grouping "WEBSITE_FOUND_RETRY" states with "HOMEPAGE_READY", when it should only do "HOMEPAGE_READY" and "HOMEPAGE_READY_RETRY".  Revise the code so that the \_RETRY is a strict suffix to the trigger state, not an arbitrary config setting.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
