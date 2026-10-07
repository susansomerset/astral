# AST-1805 — fix: _RETRY as implicit substate — no explicit _RETRY registry states, validators accept {base}_RETRY

<!-- linear-archive: AST-1805 archived 2026-10-07 -->

## Linear archive (AST-1805)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1805/fix-retry-as-implicit-substate-no-explicit-retry-registry-states  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1804 — fetch type avail counts appear not to include _RETRY records  
**Blocked by / blocks / related:** parent: AST-1804; blocks: AST-1806

### Description

## What this implements

Make `_RETRY` an implicit substate of every registered base state, per Susan's binding rule on AST-1804: no explicit `*_RETRY` states in config, claim keeps querying `[base, base_RETRY]`, and no validator checks the full `_RETRY` string. `{base}_RETRY` is accepted wherever `{base}` is registered.

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

## Technical scope

* `src/utils/config.py` — new function(s): the implicit-retry helper (retry-of-base check plus base resolver). Modified data: the three entity-state registries lose their `*_RETRY` keys, and `retry_state` / `prior_states` stop naming them. Modified asserts, so config still loads.
* `src/core/tracker.py` — modified functions: `transition_job_state`, `_job_state_matches_prior`, and any `validate_value(_JOB_STATE_LIST, …)` call on a transition target, so they accept implicit retries.
* `src/core/roster.py` — modified function: `transition_company_state` (and the claim-helper registry check, if it is still single-state-bound), for the same reason.
* `src/core/candidate.py` — modified functions: `transition_candidate_state`, `_candidate_state_allowed`, and the bare-trigger registry check, for the same reason.
* `src/core/consult.py` — modified map/branches: the legacy input-state→task map and literal `*_RETRY` checks derive from the base, so removing the registry keys doesn't change routing.
* `src/ui/api/api_admin.py` — modified function(s): dispatch-task trigger validation plus `state_options`, so admin never needs an explicit `_RETRY` key.
* Exact helper names, and whether priors are resolved inside the helper or at each call site, are plan-fix's call under statute.

## Split (plan-fix AST-1805, 8 pts confirmed)

* **AST-1805 (3):** implicit-retry helpers in config (for example `retry_of(base)` and derived prior rules); every validator (job/company/candidate transitions, claim checks, sort-by, admin trigger validation) accepts `{base}_RETRY`. No deletions yet, so behaviour is unchanged.
* **AST-1806 (5, blocked by AST-1805):** delete the 18 explicit `*_RETRY` registry keys, strip `*_RETRY` from `prior_states`, and rewrite remaining `"X_RETRY"` literals in config/consult/roster/gazer as `retry_of("X")`. The plan section lives in the same feature doc.

## Boundaries

Do not change `dispatch_claim_states` suffix-always pairing (AST-1798) or the `states=` claim relaxation (AST-1800). Keep the AST-892 `WEBSITE_FOUND_RETRY` second-strike ownership filter. Do not add new routing into retry substates beyond what exists today; this ticket changes how retries are modelled, not which failures retry. Tests and the test bible are Betty's (a fix-board REVISE files a gap sibling).

## Notes for planning

Parent AST-1804 Description is authoritative, including Susan's quoted rule. This is a registry/validator refactor: 18 explicit keys (13 job, 3 company, 2 candidate), plus `retry_state` / `prior_states` references, plus three transition validators. If the plan confirms more than 5 points, propose a split into sibling children in the plan doc (for example, validators accept implicit retry first, then registry purge) instead of trimming Susan's rule. Historical feature-doc home: `docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md` (AST-641 / AST-1798 / AST-1800 sections). plan-fix patches an existing feature doc, never creates a new one.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1804-fetch-avail-retry`, child `sub/AST-1804/AST-1805-fetch-avail-retry`. Created at bug-fix.

### Comments

#### radia — 2026-09-26T22:17:23.530Z
[code-rubric] PROCEED (Commit: d088edfd) Stage A validators clean

#### ada — 2026-09-26T22:14:40.463Z
`origin/sub/AST-1804/AST-1805-fetch-avail-retry` @ `d088edfd` · lighter check (no qa-fix, no [bug-repro]); nothing new pushed.

- `py_compile`: all 5 touched files pass.
- Suites run with `/home/susan/astral-tests/.venv/bin/python -m pytest`: `tests/component/utils/test_config.py`, `core/test_{tracker,roster,candidate,dispatcher,consult}.py`, `ui/api/test_api_admin{,_telescope}.py`.
- **No regressions:** 123 FAILED post-fix; the pre-fix tree (`9f6536ce`, same suites) fails the **identical 123 node ids** (0 new, 0 fixed). These are baseline test debt, not AST-1805 product bugs.
- @Betty, for AST-1807 / test debt, examples in the touched area:
  - `test_dispatcher.py::TestRunUnified::test_ast641_company_prefilter_passes_union_claim_states` still expects the pre-AST-1798 `WEBSITE_FOUND_RETRY` companion.
  - `test_candidate.py::TestAst1259CandidateBatchApi::test_claims_and_returns_rows` does not expect the `candidate_id=None` kwarg.
  - `test_tracker.py::TestAst562ArtifactBuildTransitions::*` hit "candidate_id required".
  - `test_config.py::TestResolveTokens::test_resolves_candidate_config_output_and_chain_tokens`: `{$FIRST_NAME}` resolves to empty.

Full failing node list:
```
tests/component/core/test_candidate.py::TestAst1030CraftResumeBaseNoBulletPreserve::test_cache_prompt_preserves_no_bullet_lead_prefix
tests/component/core/test_candidate.py::TestAst1259CandidateBatchApi::test_claims_and_returns_rows
tests/component/core/test_candidate.py::TestAst1333CraftParseHighlightsPrompts::test_craft_resume_base_prompt_requires_highlights_above_experience
tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_validate_accepts_five_key_job_array
tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_validate_rejects_string_experience_contract_message
tests/component/core/test_candidate.py::TestAst1514AdviseResumeBriefJsonPayload::test_parse_returns_items_from_dict
tests/component/core/test_candidate.py::TestAst1514AdviseResumeBriefJsonPayload::test_parse_returns_items_from_json_string
tests/component/core/test_candidate.py::TestAst1514AdviseResumeBriefJsonPayload::test_validate_accepts_dict_resume_brief
tests/component/core/test_candidate.py::TestAst1514AdviseResumeBriefJsonPayload::test_validate_accepts_json_string_resume_brief
tests/component/core/test_candidate.py::TestAst1576SaveCandidateDataOperative::test_craft_generation_calls_save_artifact
tests/component/core/test_candidate.py::TestAst1584GetOperativeBaseResume::test_miss_wrong_entity_wrong_type_return_none
tests/component/core/test_candidate.py::TestAst517ResumeStructure::test_parse_persists_custom_structure_per_candidate
tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_persist_craft_resume_base_keeps_job_array
tests/component/core/test_candidate.py::TestParseCandidateResume::test_persists_parsed_resume
tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration::test_persists_artifacts_on_craft_resume_base_success
tests/component/core/test_consult.py::TestAst1062QualifyMeteorite::test_content_gates_fail_state
tests/component/core/test_consult.py::TestAst1120CompanyJobIdFallback::test_empty_ai_no_uuid_still_empty_id_fail
tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource::test_debug_fail_ai_source_omits_fallback_link
tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource::test_debug_fail_neither_includes_fallback_link
tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource::test_debug_pass_ai_source_no_fallback_link
tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource::test_debug_pass_uuid_source_includes_fallback_link
tests/component/core/test_consult.py::TestAst1133QualifyMeteoriteListCreated::test_debug_detail_includes_link_source_input
tests/component/core/test_consult.py::TestAst1193AnalysisMatchParity::test_build_job_token_context_debug_emits_found_recorded
tests/component/core/test_consult.py::TestAst1197QualifyMeteoriteApply::test_style_d_email_link_and_subject_title_source
tests/component/core/test_consult.py::TestAst1494EnrichMeteoriteCompanyStem::test_dispatch_debug_logs_company_stem_when_present
tests/component/core/test_consult.py::TestAst369CoverLetterDispatch::test_cover_letter_for_job_calls_chain_when_resume_present
tests/component/core/test_consult.py::TestAst513JobTokenContext::test_build_job_token_context_visible_jd_plain_text_only
tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty::test_compound_trigger_state_not_chain_routed_returns_zero
tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes::test_qualify_job_listings_persists_joblist_score_on_fail
tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes::test_qualify_job_listings_persists_joblist_score_on_pass
tests/component/core/test_consult.py::TestRemainingConsultBranches::test_batch_leaves_missing_ids_without_retry_or_error
tests/component/core/test_consult.py::TestRemainingConsultBranches::test_batch_retries_missing_ids
tests/component/core/test_consult.py::TestRemainingConsultBranches::test_batch_skips_bad_grade_transition_without_dest
tests/component/core/test_consult.py::TestRemainingConsultBranches::test_qualify_ignores_score_errors
tests/component/core/test_consult.py::TestRunBatchConsult::test_counts_passed_and_failed_rows
tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch::test_debug_log_auto_off_stage_skips_style_d
tests/component/core/test_dispatcher.py::TestAst1259CandidatePoolClaim::test_claim_honors_batch_size_and_claim_states
tests/component/core/test_dispatcher.py::TestAst802InflowDiscoveryDebug::test_skip_emits_eligibility_reason_when_debug_true
tests/component/core/test_dispatcher.py::TestAst814InflowDiscoveryDebug::test_skip_cites_freq_hrs_when_all_terms_fresh
tests/component/core/test_dispatcher.py::TestAst841DispatchTerminalLogging::test_completed_with_errors_emits_terminal_warning_log
tests/component/core/test_dispatcher.py::TestAst841DispatchTerminalLogging::test_interrupted_dispatch_emits_terminal_error_log
tests/component/core/test_dispatcher.py::TestCircuitBreaker::test_disables_task_after_zero_progress_runs
tests/component/core/test_dispatcher.py::TestCircuitBreaker::test_ignores_short_history
tests/component/core/test_dispatcher.py::TestCircuitBreaker::test_keeps_enabled_when_recent_runs_show_progress
tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_company_prefilter_passes_union_claim_states
tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_consult_routes_candidate_entity
tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_ingest_creates_new_without_website
tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues
tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path
tests/component/core/test_roster.py::TestAst507EncodedPrefilter::test_inflow_dealbreaker_f2_prefilter_failed
tests/component/core/test_roster.py::TestAst507EncodedPrefilter::test_inflow_f1_no_dealbreaker_prefilter_passed
tests/component/core/test_roster.py::TestAst603ConsultParityHydration::test_inflow_pass_persists_prefilter_score
tests/component/core/test_roster.py::TestAst603ConsultParityHydration::test_karbon_dict_envelope_hydrates_notes_and_links
tests/component/core/test_roster.py::TestAst698PrefilterDebugPassthrough::test_prefilter_company_forwards_debug_to_do_task
tests/component/core/test_roster.py::TestAst707EmbeddedRcBatchHydration::test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact
tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting::test_batch_homepage_ready_pass_requires_hydrated_pjl
tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting::test_inflow_empty_links_routes_no_prefilter_joblists
tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting::test_inflow_pass_hydrates_possible_joblist_links
tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting::test_inflow_unhydratable_indices_route_no_prefilter_joblists
tests/component/core/test_roster.py::TestAst837CsePaceDebug::test_discovery_debug_streams_pace_detail_during_search
tests/component/core/test_roster.py::TestAst839CseDebugStreaming::test_resolve_debug_streams_pre_search_index_and_complete_detail
tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm::test_ingest_new_companies_kwarg_and_source_hit
tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm::test_run_batch_debug_emits_originating_search_term
tests/component/core/test_roster.py::TestAst891ParseJobListBatch::test_debug_emits_per_company_index
tests/component/core/test_roster.py::TestAst891ParseJobListBatch::test_scrape_timeout_labeled_infra_and_counts_passed
tests/component/core/test_roster.py::TestCoatCheckHandlers::test_prefilter_notes_paths
tests/component/core/test_roster.py::TestFetchJobLinksContent::test_skips_missing_urls_and_records_scrape_failures
tests/component/core/test_roster.py::TestFetchJobLinksContentBranches::test_records_visible_text_without_dom_or_new_links
tests/component/core/test_roster.py::TestFetchPrefilterNotesBranches::test_persists_optional_fields_and_handles_failures
tests/component/core/test_roster.py::TestFinalize469BranchCoverage::test_after_chain_empty_containers_debug_true_logs
tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct[-https://example.com-False]
tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct[https://careers.example/jobs-https://example.com-True]
tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct[https://example.com-https://example.com-False]
tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct[https://example.com/-https://example.com-False]
tests/component/core/test_roster.py::TestPrefilterCompany::test_exception_sets_error_state
tests/component/core/test_roster.py::TestPrefilterCompany::test_pass_and_fail_grades_persist_data
tests/component/core/test_roster.py::TestPrefilterCompany::test_redirect_and_empty_text_paths
tests/component/core/test_roster.py::TestPrefilterCompanyEdgeCases::test_exception_without_error_state
tests/component/core/test_roster.py::TestRosterCoverageGaps::test_find_job_page_try_links_empty_retry_keeps_failure
tests/component/core/test_roster.py::TestRosterCoverageGaps::test_find_job_page_try_links_retry_failure_without_debug
tests/component/core/test_roster.py::TestRosterCoverageGaps::test_prefilter_notes_returns_saved_notes_with_nav_links
tests/component/core/test_roster.py::TestRunCompanyTaskEdgeCases::test_locate_error_without_configured_error_state
tests/component/core/test_tracker.py::TestAst1523NotesMetadataRetention::test_persist_job_artifact_writes_notes_not_resume_content
tests/component/core/test_tracker.py::TestAst1693SaveMeteoriteDuplicateLinkBackfill::test_backfills_empty_job_link_on_duplicate_skip
tests/component/core/test_tracker.py::TestAst1693SaveMeteoriteDuplicateLinkBackfill::test_does_not_clobber_existing_job_link
tests/component/core/test_tracker.py::TestAst551StructureAlignedResumeChain::test_parsed_matches_resume_content_false_when_no_enabled_body
tests/component/core/test_tracker.py::TestAst551StructureAlignedResumeChain::test_parsed_matches_resume_content_subset_of_enabled_catalog
tests/component/core/test_tracker.py::TestAst551StructureAlignedResumeChain::test_persist_resume_content_without_global_required_keys
tests/component/core/test_tracker.py::TestAst552BuildArtifactsGate::test_parsed_matches_job_resume_content_requires_non_contact_body
tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_from_mid_hop_compound_state
tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_persists_cleared_build_artifact_keys
tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_rejects_wrong_state
tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_transitions_and_releases_batch_lock
tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_start_artifact_build_from_recommended
tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_start_artifact_build_rejects_wrong_state
tests/component/core/test_tracker.py::TestAst733InitializeJobCollision::test_deletes_current_row_when_canonical_exists
tests/component/core/test_tracker.py::TestAst733InitializeJobCollision::test_incomplete_identity_skips_collision_lookup
tests/component/core/test_tracker.py::TestAst733InitializeJobCollision::test_saves_when_no_collision
tests/component/core/test_tracker.py::TestAst997ExperienceJobArrayPersist::test_persist_stores_experience_job_array
tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_db_row_adds_orphan_key
tests/component/ui/api/test_api_admin.py::TestAst1214AdminCatalogAlphabeticalWritable::test_mailbox_trigger_null_only_and_unsupported_craft_wording
tests/component/ui/api/test_api_admin.py::TestAst781ListDtasksRetiredEntityType::test_list_dtasks_legacy_board_search_row_returns_zero_available_count
tests/component/ui/api/test_api_admin.py::TestAst783RepoJsonApi::test_repo_json_revert_invalid_table_key
tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_list_dispatch_tasks_and_keys
tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig::test_qualify_task_config_and_dispatch_row
tests/component/utils/test_config.py::TestAst1071ContactSkillsConfig::test_allowlisted_paths_no_slack_user_id
tests/component/utils/test_config.py::TestAst1098GazeEmailSeedClick::test_seed_auto_false_statute_registered
tests/component/utils/test_config.py::TestAst1127QualifyMeteoriteCompanyJobIdOptional::test_schema_required_false
tests/component/utils/test_config.py::TestAst1195SchemaNullsAndBotBlocked::test_job_link_title_schema_optional
tests/component/utils/test_config.py::TestAst1195SchemaNullsAndBotBlocked::test_validate_allows_omit_and_null_link_title
tests/component/utils/test_config.py::TestAst1214DispatchAdminDefaultsWidened::test_helper_resolvable_and_mailbox_defaults
tests/component/utils/test_config.py::TestAst1229SurferBatchConfig::test_surfer_batch_config_vocab_and_flags
tests/component/utils/test_config.py::TestAst1386ThreeSegmentAdminNav::test_three_admin_only_groups_order_membership_and_paste_labels
tests/component/utils/test_config.py::TestAst1529StageMeteoriteConfig::test_not_a_meteorite_dispatch_claim
tests/component/utils/test_config.py::TestAst1557MeteoriteStates::test_retention_partitions
tests/component/utils/test_config.py::TestAst1562RetentionConfig::test_retention_config_literals
tests/component/utils/test_config.py::TestAst1562RetentionConfig::test_seed_catalog_has_retention_dispatch_row
tests/component/utils/test_config.py::TestAst1621MeteoriteEntityTypeRegistry::test_retention_seed_stays_null_entity_type
tests/component/utils/test_config.py::TestAst721ParseJobListConfig::test_parse_job_list_roster_config
tests/component/utils/test_config.py::TestAst853PlaywrightConfig::test_playwright_config_keys
tests/component/utils/test_config.py::TestAst901CraftRubricUiTaskKeys::test_ui_task_keys_match_artifact_map
tests/component/utils/test_config.py::TestResolveTokens::test_resolves_candidate_config_output_and_chain_tokens
tests/component/utils/test_config.py::TestResolveTokens::test_resolves_cover_letter_signature_from_profile
```

#### ada — 2026-09-26T22:11:51.545Z
`origin/sub/AST-1804/AST-1805-fetch-avail-retry` @ `d088edfd` · Stage A only (no registry deletions).
- Checks: `py_compile` passes on all 5 files. No linter (ruff/flake8/pyflakes) is installed or configured in the repo. The derived-prior script shows **0 lost edges** across job/company/candidate, `{base}_RETRY` validates for any registered base, and `dispatch_claim_states` is unchanged.
- Env note: none of the local venvs have `asyncpg` (it's in requirements.txt), so importing `roster` needs a stub or install before test-fix.
- For AST-1806: `candidate.run_requested_artifacts_dispatch` passes `bare_trigger` to `_requested_stage_failure_target`, which indexes `CANDIDATE_STATES[primary]["retry_state"]`. A retry-only candidate dispatch row already raises `KeyError` there today (the legacy retry keys have no `retry_state`/`error_state`). After the purge, resolve the primary with `registered_base(...)`.

#### joan — 2026-09-26T22:08:46.377Z
[board-joan]  CANON: OK

Stage A implements `patt.task.dispatch-retry` (suffixed states need not be registry keys; validate via base). No directive amendment; F3 not triggered.

context_tokens≈18500

#### betty — 2026-09-26T22:08:31.354Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md + core/tracker.md (also core/roster.md, core/candidate.md, ui/api/api_admin.md) — missing coverage — no test exercises the repro (PASSED_DO → PASSED_GET_RETRY via transition_job_state) or the new LOCKED_AT_100 helpers retry_of/retry_base/registered_base/is_registered_state/state_prior_states (derived-prior rule incl. cross-base feeders NEW_RETRY/WEBSITE_FOUND_RETRY, retry self-drain, KeyError on unregistered) and the per-validator {base}_RETRY acceptance branches (roster/candidate/is_valid_*_batch_claim_state/_dispatch_sort_by_for/api_admin both sites). Stage A breaks no existing test (registry keys + raw prior_states asserts in test_config.py ~3106 untouched until AST-1806); must-not-resolve fail-dest paths already covered in test_consult/test_roster.

#### ada — 2026-09-26T22:07:06.654Z
`origin/sub/AST-1804/AST-1805-fetch-avail-retry` @ `8bd1441e` · 8 pts — split A/B

#### ada — 2026-09-26T20:53:13.676Z
[plan-fix blocked] @susan — as-is does not reproduce on current code; need your call before planning.

**Live DB:** not reachable from here. Local `data/astral.db` (→ `~/astral/data/astral.db`, mtime Sep 25 14:50) has 0 jobs, 0 companies, 1 `dispatch_task` row (`gaze_email`); `data/admin/dispatch_task.json` has no fetch-family rows; no Railway CLI on this box.

**Fixture repro on a scratch copy** (one entity in `{ts}` + one in `{ts}_RETRY`, real `count_eligible_for_dispatch_task`, tip `51d4f793` = origin/dev):

| row | primary Available | retry-only Available |
|---|---|---|
| fetch_website / WEBSITE_FOUND | 2 | 1 |
| fetch_job_pages / PREFILTER_PASSED | 2 | 1 |
| fetch_jd / PASSED_JOBLIST | 2 | 1 |
| fetch_culture_pages / PASSED_GET | 2 | 1 |

Claim (`_run_unified`) uses the same `dispatch_claim_states` list. `dispatch_chain_claim_states_for_row` is not in play — the only chain trigger is `BUILD_ARTIFACTS`.

**Named resolver (historical):** pre-AST-1798 `dispatch_claim_states` paired the companion only if registered; `PASSED_JOBLIST_RETRY` and `PASSED_GET_RETRY` are not in `JOB_STATES`, so **fetch_jd** and **fetch_culture_pages** primaries dropped `_RETRY`. AST-1798 (`8721f208`, suffix-always pairing, on origin/dev Sep 25) already fixed that — your observation likely predates the deploy.

**Only remaining gap seen:** job primaries (PASSED_* are score-gated) apply the score floor to the `_RETRY` companion too, so a `_RETRY` job with NULL/low `latest_score` is excluded from the primary's Available and claim. Speculative — not confirmed on live data.

Options: (a) confirm on prod post-AST-1798 deploy and cancel AST-1804 if Available now includes retries; (b) send me the live fetch-* row + counts showing the omission; (c) scope the fix to "score floor must not filter `_RETRY` companions" (would need your approval — not what the bug describes).

---

_Implementation detail may live in git history on `origin/dev`._
