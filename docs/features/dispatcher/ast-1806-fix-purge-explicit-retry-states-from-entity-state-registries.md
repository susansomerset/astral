# AST-1806 — fix: purge explicit _RETRY states from entity-state registries

<!-- linear-archive: AST-1806 archived 2026-10-07 -->

## Linear archive (AST-1806)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1806/fix-purge-explicit-retry-states-from-entity-state-registries  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 5  
**Parent:** AST-1804 — fetch type avail counts appear not to include _RETRY records  
**Blocked by / blocks / related:** parent: AST-1804; blocks: AST-1808

### Description

## What this implements

Second half of the AST-1804 split: remove every explicit `*_RETRY` state from the entity-state registries, now that AST-1805 has made all validators accept `{base}_RETRY` implicitly. This follows Susan's binding rule on AST-1804: no explicit `_RETRY` state in config.

## Scope

## Component scope

* `src/utils/config.py` — modified — remove explicit `*_RETRY` keys from `JOB_STATES` / `COMPANY_STATES` / `CANDIDATE_STATES`; rewrite `retry_state` fields and `prior_states` entries that name them; add the implicit-retry helper; update module-level asserts; `dispatch_claim_states` stays suffix-always.
* `src/core/tracker.py` — modified — `transition_job_state` / `_job_state_matches_prior` / job-state validation accept `{base}_RETRY` via the helper.
* `src/core/roster.py` — modified — `transition_company_state` validation accepts `{base}_RETRY`; literal `WEBSITE_FOUND_RETRY` / `JOBLIST_IDENTIFIED_RETRY` branches keep working off the derived name.
* `src/core/candidate.py` — modified — `transition_candidate_state`, `_candidate_state_allowed`, and the candidate claim/trigger checks accept `{base}_RETRY`.
* `src/core/consult.py` — modified — legacy `_INPUT_STATE_TO_TASK` `*_RETRY` entries and other `*_RETRY` literals resolve through the base.
* `src/core/gazer.py` — modified only if it transitions to a literal `*_RETRY` that must now be derived.
* `src/ui/api/api_admin.py` — modified — dispatch-row create/update trigger validation accepts `{base}_RETRY` for a registered base; `state_options` lists bases only.
* `src/data/database.py` — verify only — claim/count already uses `_state_in_sql` with no registry validation; change only if a path still rejects an unregistered `_RETRY`.
* `src/core/dispatcher.py` — verify only — claim resolution already uses `dispatch_claim_states`.
* `src/ui/api/api_system.py` — modified — `_progress_rank` resolves a `{base}_RETRY` candidate state through its base, so purging the candidate retry keys doesn't drop nav rank to −1 (AST-1806 scope-gate).

## Technical scope

* `src/utils/config.py` — new function(s): the implicit-retry helper (retry-of-base check plus base resolver). Modified data: the three entity-state registries lose their `*_RETRY` keys, and `retry_state` / `prior_states` stop naming them. Modified asserts, so config still loads.
* `src/core/tracker.py` — modified functions: `transition_job_state`, `_job_state_matches_prior`, and any `validate_value(_JOB_STATE_LIST, …)` call on a transition target, so they accept implicit retries.
* `src/core/roster.py` — modified function: `transition_company_state` (and the claim-helper registry check, if it is still single-state-bound), for the same reason.
* `src/core/candidate.py` — modified functions: `transition_candidate_state`, `_candidate_state_allowed`, and the bare-trigger registry check, for the same reason.
* `src/core/consult.py` — modified map/branches: the legacy input-state→task map and literal `*_RETRY` checks derive from the base, so removing the registry keys doesn't change routing.
* `src/ui/api/api_admin.py` — modified function(s): dispatch-task trigger validation plus `state_options`, so admin never needs an explicit `_RETRY` key.
* `src/ui/api/api_system.py` — modified function: `_progress_rank` looks up rank via the registered base, because the explicit retry keys that carried rank are deleted.
* Exact helper names, and whether priors are resolved inside the helper or at each call site, are plan-fix's call under statute.

## Split (plan-fix AST-1805, 8 pts confirmed)

* **AST-1805 (3):** implicit-retry helpers in config (for example `retry_of(base)` and derived prior rules); every validator (job/company/candidate transitions, claim checks, sort-by, admin trigger validation) accepts `{base}_RETRY`. No deletions yet, so behaviour is unchanged.
* **AST-1806 (5, blocked by AST-1805):** delete the 18 explicit `*_RETRY` registry keys, strip `*_RETRY` from `prior_states`, and rewrite remaining `"X_RETRY"` literals in config/consult/roster/gazer as `retry_of("X")`. The plan section lives in the same feature doc.

## Boundaries

Validator/helper work is AST-1805's (land it first). Do not change claim pairing (AST-1798) or the AST-892 ownership filter. No new failure routing into retry substates. Tests and the test bible are Betty's (fix-board REVISE files a gap sibling).

## Notes for planning

Plan section: `docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md`, under `## Bug: AST-1805` (the purge half). Add a `## Bug: <this id>` section there; do not create a new doc. Ada's prior-rule derivation was script-checked against the explicit job/candidate retry transitions that exist today; keep that check as the gate before deleting keys.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1804-fetch-avail-retry`, child `sub/AST-1804/AST-1806-retry-registry-purge`. Created at bug-fix.

### Comments

#### radia — 2026-09-26T22:36:21.514Z
[code-rubric] PROCEED (Commit: cfcf3c27) Registry purge clean

B1–B5 delivered; 0 explicit *_RETRY keys; boundaries held. Non-blocking: AST-1808 should pin the consult fail-dest path for retry states.

#### ada — 2026-09-26T22:32:02.721Z
test-fix (lighter path — qa-fix did not run; Betty's REVISE routed to AST-1808). origin/sub/AST-1804/AST-1806-retry-registry-purge @ cfcf3c27, no new commits.

Suites: test_candidate, test_consult, test_roster, test_tracker, tests/component/data/database/, test_database, test_api_admin(+_telescope), test_api_system, test_config — run sequentially on origin/ftr @ 65e3ca6f (171 failed baseline) vs tip (181 failed). Pre-existing collection errors on both: test_meteorites, test_surfer_batches.

**New failures — all `tests/component/utils/test_config.py`, all raw-registry `_RETRY` asserts the purge intentionally breaks. Zero product-side new failures.**

Expected, in AST-1808 Scope (7):
- 1439 AST-874 `test_job_states_and_like_priors`
- 2267 AST-898 `test_registry_retry_pointers_and_drain`
- 2308 AST-1339 `test_registry_retry_pointer_no_nested`
- 2605 AST-1253 `test_requested_artifacts_priors_include_regenerate_states`
- 3061 AST-1053 `test_job_states_priors`
- 3169 AST-1053 `test_non_meteorite_gdl_and_recommended_untouched`
- 3448 AST-1195 `test_bot_blocked_registry_and_skipped_ui`

Same class, **missing from AST-1808 Scope** (7) — flagged on AST-1808 for Betty:
- 1306 AST-721 `test_parse_states_and_transitions` (`JOBLIST_IDENTIFIED_RETRY` in COMPANY_STATES)
- 1340 AST-720 `test_selection_states_and_transitions` (`PREFILTER_PASSED_RETRY` in COMPANY_STATES)
- 1524 AST-507 `test_company_states_and_transitions` (`WEBSITE_FOUND_RETRY` in COMPANY_STATES)
- 2643 AST-1375 `test_inflight_hide_states_exact_membership` (hide states all `in CANDIDATE_STATES`)
- 3475 AST-1197 `test_task_config_email_and_bot_knobs` (`METEORITE_NEW_RETRY` in priors)
- 3661 AST-1055 `test_recommended_priors_include_meteorite_like_states` (`METEORITE_PASSED_LIKE_RETRY` in priors)
- 4763 AST-1155 `test_retry_state_and_dispatch_claim_companions` (`PASSED_JD_RETRY` in JOB_STATES)

Restoring these keys would violate the AST-1804 no-explicit-_RETRY rule, so no product change. Newly passing on tip (4): test_candidate AST-901 ×2, test_consult AST-972 routing, test_api_admin AST-825.

#### ada — 2026-09-26T22:27:43.507Z
make-fix done @ cfcf3c27 on `sub/AST-1804/AST-1806-retry-registry-purge`: 18 explicit `_RETRY` keys purged; literals → `retry_of()`; roster/database/candidate/consult/api_system resolve via base. py_compile OK; purge gate (`state_prior_states` snapshot) identical before/after. No linter installed (ruff/pyflakes absent) — manual unused-import check only. `tests/` untouched (AST-1808 owns the test_config asserts).

#### joan — 2026-09-26T22:25:19.449Z
[board-joan]  CANON: OK

Purge conforms to patt.task.dispatch-retry, entity-state-bound, config-source-of-truth; improves derive-dont-restate. No statute edit required. F3 not triggered.

#### betty — 2026-09-26T22:24:35.206Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md (+ core/roster.md, core/candidate.md, data/database.md, ui/api/api_system.md) — broken tests + missing coverage — B1/B2 break raw-registry asserts in tests/component/utils/test_config.py, and B4 retry-resolution + the carried _requested_stage_failure_target fix have no test.

**Breaks (all tests/component/utils/test_config.py, ftr 65e3ca6f), rewrite via state_prior_states / key-absence:**
- ~1450–1452 PASSED_LIKE / FAILED_LIKE / FAILED_TECHNICAL_LIKE prior_states == [CULTURE_READY, CULTURE_READY_RETRY]
- ~2268–2275 AST-898 test_registry_retry_pointers_and_drain: JOB_STATES["NEW_RETRY"] / ["VALID_TITLE_RETRY"] indexing, "VALID_TITLE_RETRY" in JOB_STATES, NEW_RETRY priors, NEW_RETRY in PASSED_JOBLIST / FAILED_JOBLIST priors (retry_state == "NEW_RETRY" lines stay green)
- ~2310–2311 AST-1339 JOB_STATES["METEORITE_NEW_RETRY"] indexing + priors
- ~2606–2616 REQUESTED_ARTIFACTS priors loop includes REQUESTED_ARTIFACTS_RETRY
- ~3067–3112 AST-1053 test_job_states_priors: every meteorite *_RETRY prior-list equality + JOB_STATES["METEORITE_PASSED_LIKE_RETRY"] + PASSED_LIKE priors
- ~3184–3190 RECOMMENDED priors contain PASSED_LIKE_RETRY; PASSED_JD priors == [JD_READY, JD_READY_RETRY, …]
- ~3454–3458 BOT_BLOCKED priors == [PASSED_JOBLIST, METEORITE_NEW, METEORITE_NEW_RETRY]

**Needs new coverage:** repro (0 *_RETRY keys across the three registries; _requested_stage_failure_target retry-only candidate row → error_state, not KeyError); roster.claim_company_batch single-state retry (no test today); candidate.check_context_complete and api_system._progress_rank retry rank == base (4 / 6); gate-snapshot identity as a pinned test.

**Stays green (anchors, no edit):** test_dispatch_tasks.py save_company(state="WEBSITE_FOUND_RETRY") ×4 (via B4 is_registered_state); test_tracker.py:350; test_consult _INPUT_STATE_TO_TASK; IN_REVIEW / UI section / grade-field string asserts (same strings via retry_of); AST-1807 helper tests.

**Bible stale:** config.md prior-list rows naming explicit retry priors (~789 AST-1053/1195, ~2611 BOT_BLOCKED/AST-1339) → mark Broken/obsolete, point at derived rule.

#### ada — 2026-09-26T22:22:33.306Z
`origin/sub/AST-1804/AST-1806-retry-registry-purge` @ `9e5bc738` · scope-gate cleared

#### chuckles — 2026-09-26T22:21:54.610Z
Scope amended on AST-1804 + AST-1806: added `src/ui/api/api_system.py` (`_progress_rank` via registered base) — answers AST-1806 [scope-gate].

#### ada — 2026-09-26T22:20:04.901Z
[scope-gate] AST-1806 plan is published but held at Plan Discuss: one file is outside `## Scope`.

`origin/sub/AST-1804/AST-1806-retry-registry-purge` @ `811ae7f4` (full plan in § Bug: AST-1806).

**File needed:** `src/ui/api/api_system.py`, `_progress_rank` (~46). The change is one expression: `CANDIDATE_STATES.get(registered_base(CANDIDATE_STATES, state) or "")`.

**Why:** today `REQUESTED_RESUME_RETRY` / `REQUESTED_ARTIFACTS_RETRY` are registry keys with `progress_rank` 4 / 6, equal to their bases. Once they're purged, `_progress_rank` returns −1 for a candidate in retry, and `_is_at_or_past` closes nav items (`api_system.py` ~111). That's a user-visible regression the purge can't avoid without touching this file.

**Scope lines that don't cover it:** Component scope lists `config.py`, `tracker.py`, `roster.py`, `candidate.py`, `consult.py`, `gazer.py`, `api_admin.py`, `database.py` (verify), `dispatcher.py` (verify). `api_system.py` isn't listed.

This is the same kind of change as the listed files (resolve a runtime state through `registered_base`), so it's a small omission for Chuckles to amend, not a new approach. After amending, assign this bug to Chuckles.

Everything else is in scope and ready. Estimate is 5, and the gate (derived priors reproduce today's legal edges) passes in the dry run with 0 diffs.

---

_Implementation detail may live in git history on `origin/dev`._
