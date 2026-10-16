# AST-2141 — gap: tests for outage error forwarding (AST-2140)

<!-- linear-archive: AST-2141 archived 2026-10-16 -->

## Linear archive (AST-2141)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2141/gap-tests-for-outage-error-forwarding-ast-2140  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2137 — Prefilter fails  
**Blocked by / blocks / related:** parent: AST-2137; related: AST-2136

### Description

## What this implements

Test gap for [AST-2140](https://linear.app/astralcareermatch/issue/AST-2140), from fix-board `[board-betty] TESTS: REVISE`. Fix the existing whole-dict assert that AST-2140's `_outage_tag` change breaks, and add coverage proving the outage `error` text reaches the dispatcher summary. Include a repro that fails on the pre-fix tree and passes once AST-2140 lands.

## Scope

Test tree and bible only, as named in Betty's board verdict:

* Bible: `docs/test-bible/core/consult.md` and `docs/test-bible/core/roster.md` (§ AST-2010 / § AST-2098).
* Break to fix: `tests/component/core/test_consult.py::TestAst2098ProbeFailureHold::test_run_consult_task_single_entity_counts_held` (\~L4504). The expected summary dict gains `"error"`.
* Repro + new coverage: AST-2140 plan § Repro 1–3 (prefilter 429, prefilter probe hold, single-entity grade probe) and the `company_upshot_batch` probe-hold branch. Each asserts `error` on the `_outage_tag` summary.
* Option B select path (plan default): `_find_job_page_from_assembled`'s select failure has no `error` and has `outage_error`, and the `run_company_task` select summary carries `error` with counts unchanged. The AST-2010 JOBS_FOUND error-route guard stays green.
* Still-holding whole-dict asserts (no change): `test_consult.py` \~L2104, \~L4557; `test_dispatcher.py` \~L1952, \~L2110.

## Boundaries

No product `src/` changes; AST-2140 owns them. Not the `JOB:<n>` decode tests ([AST-2136](https://linear.app/astralcareermatch/issue/AST-2136) / [AST-2138](https://linear.app/astralcareermatch/issue/AST-2138)).

## Notes for planning

AST-2140's plan section: `docs/features/agent/ast-1877-model-server-catalog-compat-client.md` `## Bug: AST-2140`. Add a `## Bug: AST-2141` section there. Betty lands the tests (qa-fix); engineers never edit `tests/`. Blocked by AST-2140: test-fix goes green only after AST-2140 is merged into ftr.

## Git branch (authoritative)

Parent `ftr/AST-2137-outage-error-detail`, child `sub/AST-2137/AST-2141-outage-error-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-12T15:01:43.807Z
[code-rubric] PROCEED (Commit: 67745222d) Outage error tests locked

#### ada — 2026-10-12T15:00:13.818Z
`origin/sub/AST-2137/AST-2141-outage-error-tests` @ `67745222d` · test-fix green

**[bug-repro]** `test_roster.py::TestAst2010RateLimitForwarding::test_prefilter_429_error_reaches_dispatcher_warning`: red on pre-fix `a1af5cf6a` src + tip tests (`assert None == ERR`, no `error` on the prefilter result). Green on tip.

**Manifest** (`../astral/.venv`): the AST-2010 and AST-2098 classes in `test_consult.py` and `test_roster.py`, plus `TestAst1867BalanceHeldCounting`. **33 passed.**

**Touched suites** (`test_consult.py`, `test_roster.py`, `test_dispatcher.py`):
- ftr baseline `origin/ftr/AST-2137-outage-error-detail` @ `f0c1f167c`: 90 failed / 810 passed / 25 skipped
- tip `67745222d`: 86 failed / 821 passed / 25 skipped
- **New at tip: none.** Now passing: `test_consult.py::TestAst2098ProbeFailureHold::test_run_consult_task_single_entity_counts_held` (L4504).
- Order-dependent flakes, red in the baseline full run only: `test_consult.py::TestAst371ResumeArtifactDispatch` (3 dispatch_chain_batch tests). Same as the AST-2140 run, where they passed in isolation on both trees.

**Pre-existing (red on ftr baseline and tip; not touched):**
- `tests/component/core/test_consult.py::TestAst1062QualifyMeteorite::test_content_gates_fail_state`
- `tests/component/core/test_consult.py::TestAst1120CompanyJobIdFallback::test_empty_ai_no_uuid_still_empty_id_fail`
- `tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource::test_debug_fail_ai_source_omits_fallback_link`
- `tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource::test_debug_fail_neither_includes_fallback_link`
- `tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource::test_debug_pass_ai_source_no_fallback_link`
- `tests/component/core/test_consult.py::TestAst1121CompanyJobIdDebugSource::test_debug_pass_uuid_source_includes_fallback_link`
- `tests/component/core/test_consult.py::TestAst1133QualifyMeteoriteListCreated::test_debug_detail_includes_link_source_input`
- `tests/component/core/test_consult.py::TestAst1193AnalysisMatchParity::test_build_job_token_context_debug_emits_found_recorded`
- `tests/component/core/test_consult.py::TestAst1197QualifyMeteoriteApply::test_style_d_email_link_and_subject_title_source`
- `tests/component/core/test_consult.py::TestAst1494EnrichMeteoriteCompanyStem::test_dispatch_debug_logs_company_stem_when_present`
- `tests/component/core/test_consult.py::TestAst1704MeteoriteTrackSoT::test_qualify_company_source_new_still_title_screens`
- `tests/component/core/test_consult.py::TestAst369CoverLetterDispatch::test_cover_letter_for_job_calls_chain_when_resume_present`
- `tests/component/core/test_consult.py::TestAst513JobTokenContext::test_build_job_token_context_visible_jd_plain_text_only`
- `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty::test_compound_trigger_state_not_chain_routed_returns_zero`
- `tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes::test_qualify_job_listings_persists_joblist_score_on_fail`
- `tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes::test_qualify_job_listings_persists_joblist_score_on_pass`
- `tests/component/core/test_consult.py::TestAst797QualifyInlineValidateTitle::test_qualify_returns_early_when_inline_title_screen_fails_all`
- `tests/component/core/test_consult.py::TestAst797QualifyInlineValidateTitle::test_qualify_runs_inline_validate_for_new_jobs`
- `tests/component/core/test_consult.py::TestRemainingConsultBranches::test_batch_leaves_missing_ids_without_retry_or_error`
- `tests/component/core/test_consult.py::TestRemainingConsultBranches::test_batch_retries_missing_ids`
- `tests/component/core/test_consult.py::TestRemainingConsultBranches::test_batch_skips_bad_grade_transition_without_dest`
- `tests/component/core/test_consult.py::TestRemainingConsultBranches::test_qualify_ignores_score_errors`
- `tests/component/core/test_consult.py::TestRunBatchConsult::test_counts_passed_and_failed_rows`
- `tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch::test_debug_log_auto_off_stage_skips_style_d`
- `tests/component/core/test_dispatcher.py::TestAst1259CandidatePoolClaim::test_claim_honors_batch_size_and_claim_states`
- `tests/component/core/test_dispatcher.py::TestAst2098ProviderProbeOutage::test_run_unified_per_entity_skips_after_probe_failure`
- `tests/component/core/test_dispatcher.py::TestAst802InflowDiscoveryDebug::test_skip_emits_eligibility_reason_when_debug_true`
- `tests/component/core/test_dispatcher.py::TestAst814InflowDiscoveryDebug::test_skip_cites_freq_hrs_when_all_terms_fresh`
- `tests/component/core/test_dispatcher.py::TestAst841DispatchTerminalLogging::test_completed_with_errors_emits_terminal_warning_log`
- `tests/component/core/test_dispatcher.py::TestAst841DispatchTerminalLogging::test_interrupted_dispatch_emits_terminal_error_log`
- `tests/component/core/test_dispatcher.py::TestCircuitBreaker::test_disables_task_after_zero_progress_runs`
- `tests/component/core/test_dispatcher.py::TestCircuitBreaker::test_ignores_short_history`
- `tests/component/core/test_dispatcher.py::TestCircuitBreaker::test_keeps_enabled_when_recent_runs_show_progress`
- `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_company_prefilter_passes_union_claim_states`
- `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast891_parse_job_list_full_batch_despite_batch_call_mode_zero`
- `tests/component/core/test_dispatcher.py::TestTaskThreadTarget::test_cleans_registry_after_loop`
- `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_consult_routes_candidate_entity`
- `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_ingest_creates_new_without_website`
- `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues`
- `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path`
- `tests/component/core/test_roster.py::TestAst507EncodedPrefilter::test_inflow_dealbreaker_f2_prefilter_failed`
- `tests/component/core/test_roster.py::TestAst507EncodedPrefilter::test_inflow_f1_no_dealbreaker_prefilter_passed`
- `tests/component/core/test_roster.py::TestAst603ConsultParityHydration::test_inflow_pass_persists_prefilter_score`
- `tests/component/core/test_roster.py::TestAst603ConsultParityHydration::test_karbon_dict_envelope_hydrates_notes_and_links`
- `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_fetch_job_links_content_calls_readiness`
- `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_wait_for_careers_list_readiness_ready_on_listing_hits`
- `tests/component/core/test_roster.py::TestAst689ScrapeReadiness::test_wait_for_careers_list_readiness_timeout`
- `tests/component/core/test_roster.py::TestAst698PrefilterDebugPassthrough::test_prefilter_company_forwards_debug_to_do_task`
- `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_collapses_consecutive_blank_lines_at_scrape`
- `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_nav_failure_is_non_fatal`
- `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_playwright_infra_error_prefixes_failure_class`
- `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_redirect_and_empty_text_paths`
- `tests/component/core/test_roster.py::TestAst701ScrapeCompanyHomepageContent::test_scrape_exception_returns_error`
- `tests/component/core/test_roster.py::TestAst707EmbeddedRcBatchHydration::test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact`
- `tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting::test_batch_homepage_ready_pass_requires_hydrated_pjl`
- `tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting::test_inflow_empty_links_routes_no_prefilter_joblists`
- `tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting::test_inflow_pass_hydrates_possible_joblist_links`
- `tests/component/core/test_roster.py::TestAst718PrefilterPjlRouting::test_inflow_unhydratable_indices_route_no_prefilter_joblists`
- `tests/component/core/test_roster.py::TestAst837CsePaceDebug::test_discovery_debug_streams_pace_detail_during_search`
- `tests/component/core/test_roster.py::TestAst839CseDebugStreaming::test_resolve_debug_streams_pre_search_index_and_complete_detail`
- `tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm::test_ingest_new_companies_kwarg_and_source_hit`
- `tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm::test_run_batch_debug_emits_originating_search_term`
- `tests/component/core/test_roster.py::TestAst891ParseJobListBatch::test_debug_emits_per_company_index`
- `tests/component/core/test_roster.py::TestAst891ParseJobListBatch::test_scrape_timeout_labeled_infra_and_counts_passed`
- `tests/component/core/test_roster.py::TestAst891ScrapeListPageInfra::test_infra_error_raises_playwright_infra`
- `tests/component/core/test_roster.py::TestAst891ScrapeListPageInfra::test_non_infra_exception_rethrows_original`
- `tests/component/core/test_roster.py::TestCoatCheckHandlers::test_prefilter_notes_paths`
- `tests/component/core/test_roster.py::TestFetchJobLinksContent::test_skips_invalid_link_ids_without_debug`
- `tests/component/core/test_roster.py::TestFetchJobLinksContent::test_skips_missing_urls_and_records_scrape_failures`
- `tests/component/core/test_roster.py::TestFetchJobLinksContentBranches::test_records_scrape_failure_without_debug`
- `tests/component/core/test_roster.py::TestFetchJobLinksContentBranches::test_records_visible_text_without_dom_or_new_links`
- `tests/component/core/test_roster.py::TestFetchPrefilterNotesBranches::test_persists_optional_fields_and_handles_failures`
- `tests/component/core/test_roster.py::TestFinalize469BranchCoverage::test_after_chain_empty_containers_debug_true_logs`
- `tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct[-https://example.com-False]`
- `tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct[https://careers.example/jobs-https://example.com-True]`
- `tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct[https://example.com-https://example.com-False]`
- `tests/component/core/test_roster.py::TestJobSiteDistinct674::test_is_verified_job_site_distinct[https://example.com/-https://example.com-False]`
- `tests/component/core/test_roster.py::TestPrefilterCompany::test_exception_sets_error_state`
- `tests/component/core/test_roster.py::TestPrefilterCompany::test_pass_and_fail_grades_persist_data`
- `tests/component/core/test_roster.py::TestPrefilterCompany::test_redirect_and_empty_text_paths`
- `tests/component/core/test_roster.py::TestPrefilterCompanyEdgeCases::test_exception_without_error_state`
- `tests/component/core/test_roster.py::TestRosterCoverageGaps::test_fetch_job_links_content_dom_new_links_and_scrape_debug`
- `tests/component/core/test_roster.py::TestRosterCoverageGaps::test_find_job_page_try_links_empty_retry_keeps_failure`
- `tests/component/core/test_roster.py::TestRosterCoverageGaps::test_find_job_page_try_links_retry_failure_without_debug`
- `tests/component/core/test_roster.py::TestRosterCoverageGaps::test_prefilter_notes_returns_saved_notes_with_nav_links`
- `tests/component/core/test_roster.py::TestRunCompanyTaskEdgeCases::test_locate_error_without_configured_error_state`

#### betty — 2026-10-12T14:58:11.345Z
[bug-repro]
`origin/sub/AST-2137/AST-2141-outage-error-tests` @ `67745222d` · repro red pre-fix, green on tip

#### joan — 2026-10-12T14:53:55.518Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T14:53:42.161Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/consult.md + roster.md § AST-2010 / § AST-2098 — missing coverage + one broken test — this gap child is the test work itself. C1 fixes the L4504 whole-dict assert; C2–C3 and R1–R5 add coverage for the AST-2140 `error` / `outage_error` contract. The spec is sound as written, so qa-fix can land it.

Checked against ftr `f0c1f167c` (AST-2140 merged):
- R1 matches the dispatcher format `still 429 after retries (%s)`, with `ctx["provider_rate_limit_outage"] = {"error": ...}`. `caplog.at_level("WARNING", logger="src.core.dispatcher")` already works elsewhere in `test_dispatcher.py`. `test_roster.py` has no `import logging`, so use the string level (or add the import), and import `consult_mod` / `dispatcher_mod` locally the same way the AST-2098 nodes do.
- R2 and R3 mirror `test_prefilter_batch_probe_hold_counts_held` / `test_company_upshot_probe_hold_counts_held` (both use two companies, `total_held == 2`). That's correct.
- R4 and R5 match roster L2580 (`outage_error`, `error` stripped) and `_outage_tag` lifting it back up. The guard `test_run_company_task_jobs_found_error_forwards_tag` is unaffected.

Stale plan detail (not a blocker): § Repro says AST-2140 isn't on ftr yet and that the sub syncs from pre-fix `a1af5cf6a`. ftr now contains AST-2140 (`9c28e9bdc`), and the AST-2141 sub is behind ftr. After sync-child the sub is the green tree. Get the red proof by restoring `src/` from `a1af5cf6a` over these tests (AST-2098 precedent: `git restore --source a1af5cf6a -- src/`), not from the scratch-worktree merge.

#### ada — 2026-10-12T14:52:23.380Z
`origin/sub/AST-2137/AST-2141-outage-error-tests` @ `bda2ca88a` · L4504 fix, repro, coverage

---

_Implementation detail may live in git history on `origin/dev`._
