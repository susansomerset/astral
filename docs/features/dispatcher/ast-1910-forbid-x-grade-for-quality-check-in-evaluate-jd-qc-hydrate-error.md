# AST-1910 — Forbid X grade for Quality Check in evaluate_jd (QC hydrate error)

<!-- linear-archive: AST-1910 archived 2026-10-08 -->

## Linear archive (AST-1910)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1910/forbid-x-grade-for-quality-check-in-evaluate-jd-qc-hydrate-error  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1898 — [✅/Abrams] evaluate_jd COMPLETED: 9 error(s) / 9 processed | evaluate_jd-3aebf350-898a-44d8-abf0-43ea2996f7db  
**Blocked by / blocks / related:** parent: AST-1898; blocks: AST-1911

### Description

## What this implements

Fix child for orphaned bug AST-1898. The evaluate_jd model grades the embedded **QC / Quality Check** vector `X`, but QC has only A/B/C/F grade rows, so hydrate raises `No rubric description for vector 'Quality Check' grade X` and errors every job in the batch. Susan chose option (b) on AST-1898: forbid `X` for Quality Check, so the model grades F when a JD is too thin. QC stays A/B/C/F only, and hydrate stays strict (no silent X→F mapping in code).

## Scope

### Component scope

* `src/utils/config.py`: modified. QC's `content` in `EMBEDDED_EVALUATE_JD_CRITERIA` gains a "no X, use F" rule line.
* `data/admin/agent_task.json`: modified. The `evaluate_jd` row's prompt text gets a QC exception to the "use X0 when silent" rule.
* `docs/uat-fixtures/AST-756/expected-agent_task.json`: modified. Byte-twin of `data/admin/agent_task.json` (AST-756/AST-1773 lockstep); the `evaluate_jd` row's prompt edit is mirrored here so the twin does not drift further. Added at fix-board (Betty note on AST-1910).
* `tests/component/utils/test_config.py`: modified (Betty's tree). `TestAst1084EvaluateJdCriteria` QC assertions should cover the new rule line while still pinning grades to A/B/C/F.

### Technical scope

* `src/utils/config.py`: data change to a module-level constant. One added line in QC's `content` string; `grade_descriptions` unchanged. No function changes, and hydrate in `consult.py` stays strict by design.
* `data/admin/agent_task.json`: modified prompt string on one existing row (`task_key: evaluate_jd`). No schema change. plan-fix confirms how repo admin JSON is applied to the live `agent_task` table (`REPO_ADMIN_JSON_CONFIG`) so the prompt change actually reaches runtime.
* `docs/uat-fixtures/AST-756/expected-agent_task.json`: same one-row prompt-string edit as `data/admin/agent_task.json`, mirrored byte-for-byte. No other rows touched (four rows already drifted on dev; not this fix).
* `tests/component/utils/test_config.py`: modified test, adding one assertion that QC content forbids X.

## Acceptance criteria

1. QC's rubric content, as the model sees it, says `X` is not a valid grade for Quality Check and that a too-thin JD grades F.
2. The evaluate_jd task prompt keeps "use X0 when silent" for every other vector and names QC as the one exception.
3. QC `grade_descriptions` stay exactly A/B/C/F; `_lookup_rubric_reason_for_grade` is unchanged (still raises on an unknown grade).
4. The shared `_ENCODED_GRADE_SET_COMPLETENESS` block is unchanged unless plan-fix shows the per-vector rule can't win without it, and says so in the plan.

## Boundaries

Prompt/rubric text only. No change to hydrate or decode code paths, no X→F mapping, no change to GC or any other vector. If QC then comes back F on every job, that suggests the JD content is arriving empty, which is a separate bug and not this ticket.

## Notes for planning

Bug definition, Susan's (b) decision, and bug-find's read live in AST-1898's Description. No ancestor box was checked. bug-find's top candidate doc is `docs/features/interface/ast-1084-config-constant-jd-vectors.md` (defined QC A/B/C/F); AST-1085 wired QC into evaluate_jd.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1898-evaluate-jd-qc-forbid-x`, child `sub/AST-1898/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-01T00:24:10.824Z
[code-rubric] PROCEED (Commit: 2bc48e66) QC forbids X prompt fix

#### ada — 2026-10-01T00:22:22.439Z
`origin/sub/AST-1898/AST-1910-forbid-qc-x-grade` @ `2bc48e66` · Tests Passed (no new commits)

qa-fix did not run here (test work is on AST-1911), so this is the lighter touched-area check. Runner: `/home/susan/astral-AST-1851/.venv/bin/python -m pytest -q` on `tests/component/utils/test_config.py`, `tests/component/core/test_repo_admin_json.py`, `tests/component/core/test_candidate.py`, `tests/component/core/test_consult.py`.

- **This branch:** 77 failed, 1310 passed, 25 skipped
- **`origin/ftr/AST-1898-evaluate-jd-qc-forbid-x`** (same worktree, same runner): 77 failed, 1310 passed, 25 skipped
- **Failure sets are identical, with 0 new.** The `TestAst1084EvaluateJdCriteria` QC/GC tests pass.

**Pre-existing on ftr (not counted, not fixed):**
```
tests/component/core/test_candidate.py::TestAst1030CraftResumeBaseNoBulletPreserve::test_cache_prompt_preserves_no_bullet_lead_prefix
tests/component/core/test_candidate.py::TestAst1259CandidateBatchApi::test_claims_and_returns_rows
tests/component/core/test_candidate.py::TestAst1333CraftParseHighlightsPrompts::test_craft_resume_base_prompt_requires_highlights_above_experience
tests/component/core/test_candidate.py::TestAst1333CraftParseHighlightsPrompts::test_uat_fixture_agent_task_twin_matches_catalog
tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_uat_fixture_twin_matches_catalog_after_prompt_edits
tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_validate_accepts_five_key_job_array
tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_validate_rejects_string_experience_contract_message
tests/component/core/test_candidate.py::TestAst1514AdviseResumeBriefJsonPayload::test_parse_returns_items_from_dict
tests/component/core/test_candidate.py::TestAst1514AdviseResumeBriefJsonPayload::test_parse_returns_items_from_json_string
tests/component/core/test_candidate.py::TestAst1514AdviseResumeBriefJsonPayload::test_validate_accepts_dict_resume_brief
tests/component/core/test_candidate.py::TestAst1514AdviseResumeBriefJsonPayload::test_validate_accepts_json_string_resume_brief
tests/component/core/test_candidate.py::TestAst1576SaveCandidateDataOperative::test_craft_generation_calls_save_artifact
tests/component/core/test_candidate.py::TestAst1584GetOperativeBaseResume::test_miss_wrong_entity_wrong_type_return_none
tests/component/core/test_candidate.py::TestAst1881PrefilterRcDefaultVector::test_craft_prefilter_generate_merges_into_response_and_stash
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
tests/component/core/test_repo_admin_json.py::TestApplyRepoAdminJsonAtStartup::test_startup_apply_is_noop_on_all_deploy_envs[local]
tests/component/core/test_repo_admin_json.py::TestApplyRepoAdminJsonAtStartup::test_startup_apply_is_noop_on_all_deploy_envs[production]
tests/component/core/test_repo_admin_json.py::TestApplyRepoAdminJsonAtStartup::test_startup_apply_is_noop_on_all_deploy_envs[staging]
tests/component/core/test_repo_admin_json.py::TestAst1037SimpleResumeParseCatalogRow::test_judith_craft_resume_base_row_unchanged
tests/component/core/test_repo_admin_json.py::TestAst1037SimpleResumeParseCatalogRow::test_ruth_simple_resume_parse_row
tests/component/core/test_repo_admin_json.py::TestAst1055MeteoriteCatalogRows::test_meteorite_like_cache_prompt_and_seq
tests/component/core/test_repo_admin_json.py::TestAst1055MeteoriteCatalogRows::test_meteorite_upshot_user_prompt_context
tests/component/core/test_repo_admin_json.py::TestAst1222MeteoriteGradeAliasCatalogRows::test_alias_rows_grouping_only_and_fixture_lockstep
tests/component/core/test_repo_admin_json.py::TestAst1269AliasAgentTaskSeedRestore::test_catalog_has_aliases_under_meteorite_review
tests/component/core/test_repo_admin_json.py::TestAst1368IdealDayCraftDoCachePrompt::test_craft_do_cache_prompt_ideal_day_after_backstory_before_base_resume
tests/component/core/test_repo_admin_json.py::TestAst1400EstelleCraftSeedPins::test_estelle_and_craft_match_ast1399_export
tests/component/core/test_repo_admin_json.py::TestAst1494QualifyMeteoriteCompanyStemCatalog::test_fixture_byte_identical_to_catalog
tests/component/core/test_repo_admin_json.py::TestAst1529StageMeteoriteCatalogRow::test_fixture_stage_meteorite_lockstep
tests/component/core/test_repo_admin_json.py::TestAst1755StageMeteoriteJobTitlePrompts::test_fixture_stage_meteorite_job_title_lockstep
tests/component/core/test_repo_admin_json.py::TestAst1773StageEmployerNameAndReviewDuplicateCatalog::test_fixture_catalog_byte_lockstep
tests/component/core/test_repo_admin_json.py::TestAst1784StageMeteoriteLinkedTitlePrompts::test_fixture_stage_meteorite_title_as_href_lockstep
tests/component/core/test_repo_admin_json.py::TestAst1796StageMeteoriteComboPrompts::test_fixture_stage_meteorite_combo_lockstep
tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed::test_repo_rows_match_fixture_repo_column_mapping
tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig::test_qualify_task_config_and_dispatch_row
tests/component/utils/test_config.py::TestAst1061MeteoriteEmailIngestConfig::test_link_schemes_excludes_concurrency_min_jd
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
tests/component/utils/test_config.py::TestAst1726TelescopeConfig::test_telescope_config_keys
tests/component/utils/test_config.py::TestAst721ParseJobListConfig::test_parse_job_list_roster_config
tests/component/utils/test_config.py::TestAst853PlaywrightConfig::test_playwright_config_keys
tests/component/utils/test_config.py::TestAst901CraftRubricUiTaskKeys::test_ui_task_keys_match_artifact_map
tests/component/utils/test_config.py::TestResolveTokens::test_resolves_candidate_config_output_and_chain_tokens
tests/component/utils/test_config.py::TestResolveTokens::test_resolves_cover_letter_signature_from_profile
```

#### ada — 2026-10-01T00:20:28.420Z
`origin/sub/AST-1898/AST-1910-forbid-qc-x-grade` @ `2bc48e66` · Code Complete

- `src/utils/config.py`: QC `content` gains "Never grade Quality Check X …" before the A row. `grade_descriptions` stay A/B/C/F, and the trailing-table parse still yields A/B/C/F. `_lookup_rubric_reason_for_grade(…, 'Quality Check', 'X')` still raises.
- `data/admin/agent_task.json` + `docs/uat-fixtures/AST-756/expected-agent_task.json` (scope amendment): `evaluate_jd` `cache_prompt` gets a QC exception in STEP 3 and in GRADE SET COMPLETENESS. One changed line per file, other rows untouched. `_ENCODED_GRADE_SET_COMPLETENESS` is unchanged.
- Checks: py_compile OK, both JSON files load, ruff shows 92 findings before and 92 after (none new), existing `TestAst1084EvaluateJdCriteria` 3/3 pass. No `tests/` edits; test work is with AST-1911.
- **Deploy note:** the prompt change reaches the live DB only via admin **Revert to file** for `agent_task` (`POST /api/admin/repo_json/revert/agent_task`). Check the compare view first, because it rewrites every row. The QC rubric line needs no admin step.
- Lands via `ftr/AST-1898-evaluate-jd-qc-forbid-x` (normal stacked flow).

#### joan — 2026-10-01T00:18:42.933Z
[board-joan]  CANON: OK

#### betty — 2026-10-01T00:18:16.794Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md § AST-1084 (`TestAst1084EvaluateJdCriteria`) + docs/test-bible/ (AST-1154 `test_repo_admin_json` completeness class) — missing coverage — no test pins QC `content` forbidding X (with `parse_trailing_grade_table_lines` still A/B/C/F) or the `evaluate_jd` `cache_prompt` QC exception (catalog + per-key fixture lockstep); existing substring tests stay green after the append-only edits.

Note (not this fix's doing): `TestAst756…`/`AST-1773` byte-twin tests (`agent_task.json` == `docs/uat-fixtures/AST-756/expected-agent_task.json`) are already red on origin/dev (4 drifted rows). Plan item 2's "exactly one changed line" leaves the twin's `evaluate_jd` row stale too — make-fix should mirror the edit into the fixture.

#### ada — 2026-10-01T00:16:34.137Z
`origin/sub/AST-1898/AST-1910-forbid-qc-x-grade` @ `e2ac8ee6` · QC never X; grade F

---

_Implementation detail may live in git history on `origin/dev`._
