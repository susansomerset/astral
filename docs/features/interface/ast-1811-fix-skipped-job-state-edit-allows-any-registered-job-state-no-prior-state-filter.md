# AST-1811 — fix: skipped-job state edit allows any registered job state (no prior-state filter)

<!-- linear-archive: AST-1811 archived 2026-10-07 -->

## Linear archive (AST-1811)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1811/fix-skipped-job-state-edit-allows-any-registered-job-state-no-prior  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1809 — Allow Skipped Job state change to ANY job state, do not filter/validate  
**Blocked by / blocks / related:** parent: AST-1809

### Description

## What this implements

Operator override on Skipped jobs: the Job Detail state control offers every registered job state (all `JOB_STATES` keys except the current state), and saving moves the job there with no prior-state validation — only the entity type (job) bounds the list. The transition still records `state_history` / `state_changed_at`. Prior-state enforcement stays unchanged for every other caller.

## Scope

## Component scope

* `src/core/tracker.py` — modified. It owns the successor list that feeds the dropdown, the skipped-edit persist, and the prior-state check in `transition_job_state`, so all three changes live here.
* `src/ui/api/api_jobs.py` — probably untouched. `_attach_skipped_edit_meta` and the PUT handler should pick up the wider list with no changes. Listed only in case the successor function is renamed or split and the import has to follow.

## Technical scope

* `src/core/tracker.py`:
  * **Modified function:** the successor-list function, `legal_job_successor_states` or a new sibling just for skipped editing. It should return every registered job state except the current one, so the dropdown stops filtering.
  * **Modified function:** `transition_job_state` gets a keyword-only flag that skips the `prior_states` check. The default keeps enforcement, so other callers are unaffected.
  * **Modified function:** `persist_skipped_job_edits` passes that flag, so the operator's chosen state is accepted as long as it is a registered job state.
* `src/ui/api/api_jobs.py`: no function-level change expected. At most, an import rename if the successor function is renamed.

## Boundaries

Does not relax prior-state checks for dispatcher, bulk Retry, Skip, chain graduation, or any non-skipped-edit caller. Does not unlock editing on non-skipped jobs (the current-state `SKIPPED_STATES` gate stays). Does not list runtime dispatch-hop labels or non-job entity states. Tests / bible are Betty's (fix-board decides whether a gap child is needed). Orphaned mini-parent is AST-1809; no ancestor box checked (AST-1453 / AST-1446 / AST-1454 are archived).

## Notes for planning

AST-1809 Description (As-is / To-be / Proposed steps) is authoritative. Susan's brief: "Should not be filtered beyond the entity type." This deliberately waives `astral.state.job-prior-states-enforced` for this one operator path — expect fix-board Joan to weigh in on canon. Likely plan-doc patch target (historical home, not an approved ancestor): `docs/features/interface/ast-1453-persist-skipped-job-field-and-state-edits.md`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1809-skipped-any-state`, child `sub/AST-1809/AST-1811-skipped-any-state`. Created at bug-fix.

### Comments

#### radia — 2026-09-27T01:25:42.322Z
[code-rubric] PROCEED (Commit: 59907eb9) skipped override conforms

#### ada — 2026-09-27T01:17:10.514Z
`origin/sub/AST-1809/AST-1811-skipped-any-state` @ `57b178d8` · lighter check green (no qa-fix; tests → AST-1812)

- Behavioral sanity (inline, fake DB): successor list = all 54 other `JOB_STATES` keys; default `transition_job_state` still raises `Invalid transition`; `enforce_prior_states=False` skips only the prior check (history written, unregistered still rejected); persist rejects `NEW_RETRY` / `BOGUS`, same-state no-op, skipped gate holds.
- `test_tracker.py` + `test_api_jobs.py` vs pre-fix baseline (`8938f271`): 22 failures pre-existing and unchanged; +2 new, both old-contract — for **AST-1812** (Betty):
  - `TestAst1453LegalJobSuccessorStates::test_excludes_self_includes_unrestricted_and_listed_priors` — asserts prior-filtered list.
  - `TestAst1453PersistSkippedJobEdits::test_writes_title_link_jd_then_transition` — `_transition(ids, to_state)` mock lacks the `enforce_prior_states` kwarg (TypeError).

#### joan — 2026-09-27T01:09:48.334Z
[board-joan]  CANON: REVISE
What: astral.state.job-prior-states-enforced — record skipped-job operator-edit carve-out (`enforce_prior_states=False` / unfiltered `JOB_STATES` targets) — Susan product call already in plan; statute text still universal

#### betty — 2026-09-27T01:09:04.200Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md AST-1453 (+ ui/api/api_jobs.md) — broken tests + missing repro coverage — `TestAst1453LegalJobSuccessorStates` asserts the prior-filtered list and will fail; `test_writes_title_link_jd_then_transition` mocks `_transition(ids, to_state)` with no kwargs, so it TypeErrors when persist passes `enforce_prior_states=False` (not in the plan's Blast radius); no test covers the `enforce_prior_states=False` bypass, the default still enforcing, or persist rejecting a non-`JOB_STATES` target (`*_RETRY` / hop label → "not in allowed list"). `src/core/tracker.py` is `LOCKED_AT_100`, so the new branches need tests anyway. The "illegal transition" premises in `test_field_writes_before_illegal_transition_propagates` and `test_api_jobs.py::test_put_illegal_transition_409` need rewriting as unregistered-target cases.

#### ada — 2026-09-27T01:07:49.198Z
`origin/sub/AST-1809/AST-1811-skipped-any-state` @ `c420b74c` · skipped any-state plan ready

---

_Implementation detail may live in git history on `origin/dev`._
