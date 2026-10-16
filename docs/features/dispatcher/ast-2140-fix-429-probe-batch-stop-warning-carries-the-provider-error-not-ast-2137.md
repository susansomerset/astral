# AST-2140 — fix: 429 / probe batch-stop warning carries the provider error, not () (AST-2137)

<!-- linear-archive: AST-2140 archived 2026-10-16 -->

## Linear archive (AST-2140)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2140/fix-429-probe-batch-stop-warning-carries-the-provider-error-not-ast  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2137 — Prefilter fails  
**Blocked by / blocks / related:** parent: AST-2137; blocks: AST-2141; related: AST-2136

### Description

## What this implements

The fix for orphaned bug [AST-2137](https://linear.app/astralcareermatch/issue/AST-2137) (narrowed per Susan): the AST-2010 exhausted-429 batch-stop warning, and the AST-2098 failed-probe warning, print the provider's error text instead of an empty `()`.

## Citations

none. Bug fix inside existing AST-2010 / AST-2098 behavior; plan-fix / fix-board name any canon.

## Scope

### Component scope

* `src/core/roster.py` (modified): `_outage_tag` drops `error` when it lifts a rate-limit/probe outage to the dispatcher. This is the path the prefilter_company batches in this log took.
* `src/core/consult.py` (modified): `_outage_tag` (same helper, consult side) drops `error` the same way for consult/grade batches.

### Technical scope

* `src/core/roster.py`: modify function `_outage_tag` so a tagged outage also carries the result's error text. No new tables or fields.
* `src/core/consult.py`: modify function `_outage_tag`, same change, so consult-side outages report their detail too. No new tables or fields.

## Acceptance criteria

* An exhausted-429 batch stop logs `LLM provider rate limit: still 429 after retries (<provider error text>)`, never `()`.
* A failed-probe stop logs its probe error the same way.
* Routing, retry counts, held tallies and summary counters are unchanged.

## Boundaries

* Does not touch the `JOB:<n>` → `JO` decode bug. That's [AST-2136](https://linear.app/astralcareermatch/issue/AST-2136) / [AST-2138](https://linear.app/astralcareermatch/issue/AST-2138).
* Does not change `src/core/dispatcher.py` warning text or stop behavior, or 429 retry policy in `llm_compat`.
* Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one).

## Notes for planning

Ancestor context: AST-2010 section of `docs/features/agent/ast-1877-model-server-catalog-compat-client.md` (§ Bug: AST-2010), with AST-2098 in `docs/features/foundation/ast-1959-per-batch-probe-and-host-lock-on-the-openrouter-path.md`. Patch the AST-2010 doc per plan-fix; don't create a new plan doc.

## Git branch (authoritative)

Parent `ftr/AST-2137-outage-error-detail`, child `sub/AST-2137/AST-2140-outage-error-detail`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-12T14:52:40.060Z
[code-rubric] PROCEED (Commit: 9c28e9bdc) Option B outage_error lift

#### ada — 2026-10-12T14:50:04.904Z
`origin/sub/AST-2137/AST-2140-outage-error-detail` @ `9c28e9bdc` · test-fix (no qa-fix manifest; touched-suite check)

Command (both trees, `../astral/.venv`): `pytest -q tests/component/core/test_consult.py tests/component/core/test_roster.py tests/component/core/test_dispatcher.py`
- ftr baseline `origin/ftr/AST-2137-outage-error-detail` @ `a1af5cf6a`: 89 failed / 811 passed / 25 skipped
- tip `9c28e9bdc`: 87 failed / 813 passed / 25 skipped

**Expected-fail set (AST-2141 owns):**
- `test_consult.py::TestAst2098ProbeFailureHold::test_run_consult_task_single_entity_counts_held` — whole-dict assert at L4504 now sees the forwarded `error` key

**No other new failures.** Order-dependent flakes, red on the baseline full run only: `test_consult.py::TestAst371ResumeArtifactDispatch` (3 dispatch_chain_batch tests). They pass in isolation on both trees.

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

#### joan — 2026-10-12T14:47:50.959Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T14:47:09.352Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/consult.md + roster.md § AST-2010 / § AST-2098 — missing coverage + one broken test — no node asserts `error` on any `_outage_tag` summary (repro 1–3 are uncovered), and `test_consult.py::TestAst2098ProbeFailureHold::test_run_consult_task_single_entity_counts_held` (L4504) asserts the whole summary dict while its stubbed `rv` carries `error`, so `consult.py:3133` `**_outage_tag(rv)` adds `"error"` and the assert breaks.

Notes for qa-fix:
- The plan's Blast radius calls `TestAst2098ProbeFailureHold` key-by-key / unaffected. That's true in `test_roster.py` but not in `test_consult.py` L4504: expected dict needs `"error": self._ERR`.
- These whole-dict asserts were checked and still hold: `test_consult.py` L2104 (stub batch has no `error`), L4557 (balance → `_outage_tag` `{}`), and `test_dispatcher.py` L1952/L2110 (summary keys only).
- New coverage: plan § Repro 1–3 (prefilter 429, prefilter probe hold, single-entity grade probe), plus the `company_upshot_batch` probe-hold branch (roster change 3).
- Option A vs B: under B, add the select path. `_find_job_page_from_assembled`'s select failure must have no `error` and must have `outage_error`, and the `run_company_task` select summary should carry `error` with counts `(1, 1, 0)`. Under A, no select node is needed. A guard for the AST-2010 JOBS_FOUND error route stays green either way. Neither option changes the broken-test finding above.

#### ada — 2026-10-12T14:46:12.364Z
`origin/sub/AST-2137/AST-2140-outage-error-detail` @ `0bd88a6e3` · outage tags carry error text

---

_Implementation detail may live in git history on `origin/dev`._
