# AST-1798 — fix: strict _RETRY suffix claim pairing (no retry_state companion)

<!-- linear-archive: AST-1798 archived 2026-10-02 -->

## Linear archive (AST-1798)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1798/fix-strict-retry-suffix-claim-pairing-no-retry-state-companion  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1797 — _RETRY suffix issues  
**Blocked by / blocks / related:** parent: AST-1797

### Description

## What this implements

Strict `_RETRY` suffix claim pairing for all dispatch_task rows: drop registry `retry_state` preference and registry-membership gate in `dispatch_claim_states` so `HOMEPAGE_READY` claims `HOMEPAGE_READY_RETRY` (always), never `WEBSITE_FOUND_RETRY`.

## Proposed change

- [X] `src/utils/config.py` — `dispatch_claim_states`: suffix-only pairing always; no `retry_state` preference; no registry membership gate
- [X] `src/data/database.py` / claim callers — confirmed no registry rejection of absent `{ts}_RETRY` (no change needed)
- [ ] `tests/component/utils/test_config.py` — owned by sibling gap (fix-board TESTS: REVISE); not this tip

## Scope

## Component scope

* `src/utils/config.py` — modified: `dispatch_claim_states` companion rule (suffix-only, always; no `retry_state`, no registry membership gate); any helper it calls that still validates companion registry membership.
* `src/data/database.py` and/or claim callers — modified only if they reject or error when a claim-state list includes a `{ts}_RETRY` not present in the entity registry (must accept the paired suffix without validating suffix content).
* `tests/component/utils/test_config.py` — modified: claim-state assertions for suffix-always pairing (including `HOMEPAGE_READY` → `HOMEPAGE_READY_RETRY`, never `WEBSITE_FOUND_RETRY`).

## Technical scope

* `src/utils/config.py` — modified function `dispatch_claim_states`: remove the branch that returns `[ts, registry[ts].retry_state]`; remove `if companion in registry` gating; always append `f"{ts}_RETRY"` for non-`_RETRY` triggers across job/company/candidate/meteorite. Do not invent cross-name companions from config.
* Claim/count callers (`src/data/database.py` and thin dispatcher/roster/tracker plumbing only if they currently validate every claim state ∈ registry) — modified validation: allow the suffix companion without erroring or requiring a registry entry; do not treat “starts with primary” as license to pull a different state’s `retry_state`.
* `tests/component/utils/test_config.py` — modified tests: primary → always two-state suffix list; missing companion key in registry is fine (no error); `HOMEPAGE_READY` never unions `WEBSITE_FOUND_RETRY`.

## Boundaries

Does not invent cross-name companions from config. Scrape ownership of `WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY` on `fetch_website` stays unless claim pairing alone requires a touch. Orphaned mini-parent is AST-1797 (no ancestor checked).

## Notes for planning

Parent AST-1797 Description (As-is / To-be / Proposed steps) is authoritative. Susan's To-be: always pair `trigger + "_RETRY"` whether or not companion exists in registry; do not error/validate suffix content against registry; all entity types / task keys.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1797-retry-suffix-claim`, child `sub/AST-1797/AST-1798-retry-suffix-claim`. Created at bug-fix.

### Comments

#### radia — 2026-09-25T17:15:35.836Z
[code-rubric] PROCEED (Commit: 8721f208) suffix-only claim pairing; TESTS:REVISE owned by gap AST-1799

#### joan — 2026-09-25T17:09:32.859Z
[board-joan]  CANON: OK

Suffix-only claim pairing restores `patt.task.dispatch-retry` Arc 1–3; registry `retry_state` stays for failure routing only. No canon edit / F3 validate-plan.

context_tokens≈12000

#### betty — 2026-09-25T17:08:39.200Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md — broken test — TestAst882/641/898 claim asserts encode cross-name companions; must flip to suffix-always

#### ada — 2026-09-25T17:07:50.288Z
`origin/sub/AST-1797/AST-1798-retry-suffix-claim` @ `c17228510738ea1483623a76b32f2336d87f5153` · suffix-only claim pairing

---

_Implementation detail may live in git history on `origin/dev`._
