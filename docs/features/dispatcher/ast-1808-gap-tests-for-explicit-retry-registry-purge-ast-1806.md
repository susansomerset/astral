# AST-1808 — gap: tests for explicit _RETRY registry purge (AST-1806)

<!-- linear-archive: AST-1808 archived 2026-10-07 -->

## Linear archive (AST-1808)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1808/gap-tests-for-explicit-retry-registry-purge-ast-1806  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1804 — fetch type avail counts appear not to include _RETRY records  
**Blocked by / blocks / related:** parent: AST-1804

### Description

## What this implements

Test gap for AST-1806, from fix-board `[board-betty] TESTS: REVISE`. Rewrite the raw-registry asserts the purge breaks, and add coverage for the purge's retry-resolution sites, plus a repro that fails on the pre-purge tree and passes once AST-1806 lands.

## Scope

Test tree and bible only, as named in Betty's board verdict:

* Bible: `docs/test-bible/utils/config.md`, `docs/test-bible/core/roster.md`, `docs/test-bible/core/candidate.md`, `docs/test-bible/data/database.md`, `docs/test-bible/ui/api/api_system.md`.
* Breaks to rewrite (via `state_prior_states` / key-absence), all in `tests/component/utils/test_config.py` on ftr 65e3ca6f: \~1450–1452 LIKE priors; \~2268–2275 AST-898 `test_registry_retry_pointers_and_drain` (keep the `retry_state == "NEW_RETRY"` lines); \~2310–2311 AST-1339 METEORITE_NEW_RETRY; \~2606–2616 REQUESTED_ARTIFACTS priors loop; \~3067–3112 AST-1053 `test_job_states_priors`; \~3184–3190 RECOMMENDED / PASSED_JD priors; \~3454–3458 BOT_BLOCKED priors.
* Also in `test_config.py` (found at AST-1806 test-fix, same kind of rewrite): \~1306, \~1340, \~1524, \~2643, \~3475, \~3661, \~4763 — asserts on `*_RETRY` registry keys or priors the purge removes.
* Repro: zero `*_RETRY` keys across JOB_STATES / COMPANY_STATES / CANDIDATE_STATES (fails pre-purge, passes after AST-1806).
* New coverage: `_requested_stage_failure_target` on a retry-only candidate row resolves to `error_state` (no KeyError); `roster.claim_company_batch` single-state retry claim; `candidate.check_context_complete` and `api_system._progress_rank` retry rank equals base rank; the gate-snapshot identity as a pinned test.

## Boundaries

No product `src/` changes (AST-1806 owns them). AST-1807 owns the AST-1805 helper/validator-acceptance tests; don't duplicate them.

## Notes for planning

AST-1806's plan section: `docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md` `## Bug: AST-1806`. Add a `## Bug: AST-1808` section there. Betty lands the tests (qa-fix); engineers never edit `tests/`. Blocked by AST-1806: test-fix goes green only after AST-1806 is merged into ftr.

## Git branch (authoritative)

Parent `ftr/AST-1804-fetch-avail-retry`, child `sub/AST-1804/AST-1808-purge-retry-tests`. Created at bug-fix.

### Comments

#### radia — 2026-09-26T22:46:08.822Z
[code-rubric] PROCEED (Commit: 0435671d) Purge test gap clean

T1–T4 present; 14 purge rewrites + zero-key repro + pinned snapshot + consumer/fail-dest coverage. Closes the AST-1806 TESTS: REVISE bar.

#### ada — 2026-09-26T22:44:27.049Z
test-fix: `origin/sub/AST-1804/AST-1808-purge-retry-tests` @ `0435671d`, no new commits.

- [bug-repro] `TestAst1808RetryRegistryPurge::test_no_explicit_retry_keys_in_entity_registries`: **red** on pre-purge `65e3ca6f` `src/` (18 explicit keys) → **green** on tip.
- Touched suites (candidate/consult/roster/tracker/data database/api_admin(+telescope)/api_system/config), sequential: ftr `2a419fbf` 187 failed → tip 167 failed. **New failures: 0.** All 14 AST-1806 raw-registry `test_config` breaks now pass (+6 unrelated flips green in candidate/consult/roster/api_admin — also seen flipping in AST-1806 test-fix).
- `### AST-1808` manifest: 42 passed, 3 failed — all 3 pre-existing on ftr and `65e3ca6f` (`TestAst1195…::test_job_link_title_schema_optional`, `::test_validate_allows_omit_and_null_link_title`, `TestAst721…::test_parse_job_list_roster_config`); pulled in by whole-class manifest nodes.

#### ada — 2026-09-26T22:42:32.170Z
make-fix: no product change (AST-1806 on ftr). `origin/sub/AST-1804/AST-1808-purge-retry-tests` @ `0435671d`, ftr included, no `src/` diff vs ftr.

- [bug-repro] `TestAst1808RetryRegistryPurge::test_no_explicit_retry_keys_in_entity_registries`: green on tip.
- `### AST-1808` manifest: 42 passed, 3 failed — all 3 pre-existing (red on ftr `65e3ca6f` pre-purge), pulled in only because the manifest runs whole classes: `TestAst1195SchemaNullsAndBotBlocked::test_job_link_title_schema_optional`, `::test_validate_allows_omit_and_null_link_title`, `TestAst721ParseJobListConfig::test_parse_job_list_roster_config`. All 14 purge-break rewrites + new coverage green.

#### betty — 2026-09-26T22:41:35.187Z
[bug-repro]
`origin/sub/AST-1804/AST-1808-purge-retry-tests` @ `0435671d` · repro red pre-purge, green on ftr

Repro node: `tests/component/utils/test_config.py::TestAst1808RetryRegistryPurge::test_no_explicit_retry_keys_in_entity_registries`. Red→green already observed: red on `65e3ca6f` product files (18 keys; the `_requested_stage_failure_target` retry-only row raises `KeyError`), green on ftr `2a419fbf` (merged into this sub as `sync(AST-1808)`). The 14 purge-break rewrites flip red→green, and nothing new fails against baseline. The 20 remaining failures in the touched files are pre-existing (red on `65e3ca6f` too). Manifest: `### AST-1808` in `docs/test-bible/{utils/config,core/roster,core/candidate,ui/api/api_system}.md`.

Deviation: `tests/component/data/**` and `docs/test-bible/data/**` are blocked for agent edits by the `data/` rule in `.cursorignore`. So there's no new `test_companies.py` node; `save_company` retry coverage points to the existing real-DB `test_dispatch_tasks.py` anchors instead. The `sync(AST-1808)` merge resolved an append/append conflict in the shared plan doc (both sides kept verbatim).

#### joan — 2026-09-26T22:36:22.520Z
[board-joan]  CANON: OK

Test/bible-only gap; no statute/pattern text touched. F3 not triggered.

#### betty — 2026-09-26T22:35:58.625Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md (+ core/roster.md, core/candidate.md, data/database.md, ui/api/api_system.md) — broken tests + missing coverage — gap ticket is test-tree-only, so it routes to qa-fix (Betty lands T1–T4), not make-fix. T1 covers the 14 test_config rewrites (my 7 from AST-1806 plus Ada's 7 extra); T3 covers the B4 consumers; target files exist.

Two design notes qa-fix will apply (no plan round needed):
- **T2 snapshot must filter `*_RETRY_RETRY`.** Probed: pre-purge ftr 65e3ca6f gives 42 `*_RETRY_RETRY` derived priors (18 keys); AST-1806 cfcf3c27 gives 0. A fixture captured raw on the pre-purge tree would never match post-purge. Apply the same `_RETRY_RETRY` strip as the AST-1806 gate script, both when capturing and when comparing.
- **Fixture path:** `tests/fixtures/` doesn't exist (only `tests/component/frontend/fixtures/`). Place it at `tests/component/utils/fixtures/ast1806_prior_snapshot.json` next to test_config.py.

Red→green gets verified against AST-1806 product files (the ftr tip stays red until merge-child), same as AST-1807.

#### ada — 2026-09-26T22:34:34.731Z
`origin/sub/AST-1804/AST-1808-purge-retry-tests` @ `5a1becb6` · 14 rewrites, repro, coverage

#### ada — 2026-09-26T22:32:03.734Z
@Betty — scope gap from AST-1806 test-fix (tip cfcf3c27). Besides the 7 listed breaks, 7 more `tests/component/utils/test_config.py` raw-registry `_RETRY` asserts fail after the purge and need the same rewrite (via `state_prior_states` / `registered_base` / key-absence):

- 1306 AST-721 `test_parse_states_and_transitions` — `JOBLIST_IDENTIFIED_RETRY` in COMPANY_STATES
- 1340 AST-720 `test_selection_states_and_transitions` — `PREFILTER_PASSED_RETRY` in COMPANY_STATES
- 1524 AST-507 `test_company_states_and_transitions` — `WEBSITE_FOUND_RETRY` in COMPANY_STATES
- 2643 AST-1375 `test_inflight_hide_states_exact_membership` — `all(s in CANDIDATE_STATES for s in hide)`
- 3475 AST-1197 `test_task_config_email_and_bot_knobs` — `METEORITE_NEW_RETRY` in priors
- 3661 AST-1055 `test_recommended_priors_include_meteorite_like_states` — `METEORITE_PASSED_LIKE_RETRY` in priors
- 4763 AST-1155 `test_retry_state_and_dispatch_claim_companions` — `PASSED_JD_RETRY` in JOB_STATES

---

_Implementation detail may live in git history on `origin/dev`._
