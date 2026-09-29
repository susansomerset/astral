# Candidates

**Test module:** `tests/component/data/database/test_candidates.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-971 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-971. Column coverage: **`TestAst971CandidateStateHistoryColumn`**.

### AST-973 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-973. **`hard_delete_candidate`**, **`migrate_legacy_candidate_states`** (ensure = phases BC only).

### AST-1134 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`.

Adds nullable `candidate.last_email_check` (fresh CREATE + ALTER migrate) and `update_candidate_last_email_check` stamp helper. Call site after `gaze_email` run is **AST-1136**.

| Area | Source | Component tests |
| --- | --- | --- |
| Column + stamp helper | `src/data/database.py` | **`TestAst1134LastEmailCheck`** |

**Broken / obsolete:** none — additive column/helper.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1134LastEmailCheck \
  -q
```

### AST-1258 · AST-1257

**Parent:** [AST-1257 — candidate table does not have batch_id](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id). **Publish:** `origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis`.

Candidate row `batch_id` / `batch_created_at` (null/empty = unclaimed) plus data-layer pool claim → get → clear peers of job/company (`claim_candidate_batch` batch_id-first, cross-candidate pool, no single-ctx gate). Eligibility / Avail for non-inflow candidate stage tasks: **`docs/test-bible/data/database/dispatch_tasks.md`** § AST-1258. Dispatcher/core wrappers: sibling **AST-1259**. Canon/docs: **AST-1260**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema columns + unclaimed save | `src/data/database.py` | **`TestAst1258CandidateBatchClaim::test_schema_has_nullable_batch_columns`**, **`::test_save_leaves_batch_unclaimed`** |
| Claim → get → clear multi-row; concurrent refuse; release all | `src/data/database.py` | **`TestAst1258CandidateBatchClaim::test_claim_get_clear_multi_row_pool`** |
| Claim unions primary + retry states | `src/data/database.py` | **`TestAst1258CandidateBatchClaim::test_claim_unions_retry_states`** |

**Broken / obsolete (Betty revision):** none in this module — claim APIs are additive. Stage Avail assertion revision lives in **`test_dispatch_tasks.py`**.

**Integration:** none (no existing integration scenario asserts unlocked candidate claim / inflow-only stage Avail).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1258CandidateBatchClaim \
  -q
```

### AST-1417 · AST-1415 (gap — save_candidate hop-label persist)

**Parent:** [AST-1415 — Candidate state validation bug](https://linear.app/astralcareermatch/issue/AST-1415). **Sibling product:** AST-1416. **Publish:** `origin/sub/AST-1415/AST-1417-save-candidate-hop-label-coverage`.

Board REVISE on AST-1416: `TestSaveCandidate` only rejects `NOT_A_STATE`; AST-1389 mocks the hop-label write. This gap owns the [bug-repro] bar for `save_candidate` persist of `REQUESTED_ARTIFACTS.<hop>`.

| Area | Source | Component tests |
| --- | --- | --- |
| Persist hop label via save_candidate UPDATE | `src/data/database.py` (`save_candidate`) | **`TestAst1417SaveCandidateHopLabelPersist::test_update_persists_requested_artifacts_hop_label`** (**[bug-repro]**) |

**Broken / obsolete this pass:** none — `TestSaveCandidate::test_rejects_invalid_state` still rejects non-hop unknowns (`NOT_A_STATE`, `NEW`).

**Integration:** none revised.

## QA test manifest

1. Hop-label persist (bug-repro): `tests/component/data/database/test_candidates.py::TestAst1417SaveCandidateHopLabelPersist::test_update_persists_requested_artifacts_hop_label`

**AST-1417** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1417SaveCandidateHopLabelPersist \
  -q
```

**Pass criterion:** node fails on pre-fix tree (`Invalid candidate state 'REQUESTED_ARTIFACTS.craft_get_rubric'`); flips green after AST-1416 `make-fix`.

### AST-1502 · AST-1492 (gap — ensure leaves live candidate content)

**Parent:** AST-1492. **Sibling product:** AST-1497. Primary bible: **`docs/test-bible/core/bootstrap.md`** § AST-1502.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure skips content migrates; ARTIFACTS_READY survives | `src/data/database.py` (`_ensure_candidate_schema`) | **`TestAst1502EnsureLeavesLiveCandidateContent::test_ensure_candidate_schema_leaves_artifacts_ready_without_content_migrates`** (**[bug-repro]**) |

**Broken / obsolete this pass:** none in this module beyond the new assertion bar (AST-575 ensure-driven backfill expectations may need a later revise when AST-1497 lands — out of this gap's board What).

**Integration:** none.

### AST-1878 · AST-1851 (agent model field + per-platform candidate keys)

New `candidate_key` table (one Fernet-encrypted key per candidate × `LLM_SERVER_CONFIG` server); `get_candidate` hydrates `candidate_api_keys` `{server_id: plaintext}` and never exposes the legacy single `candidate_api_key`; `save_candidate` loses the legacy parameter; hard delete cascades keys. Agent `model_id` + per-model brain validation ([`agents.md`](agents.md)), seed AC 3/4 ([`../../core/repo_admin_json.md`](../../core/repo_admin_json.md)), timesheet SKU/server check + per-server backfill ([`timesheets.md`](timesheets.md)), core wrappers + session paste ([`../../core/candidate.md`](../../core/candidate.md)).

| Area | Source | Component tests |
| --- | --- | --- |
| New — two-server ciphertext storage (parent AC 6 storage half), AC 5 key map / no legacy key, upsert, undecryptable omitted, set/clear/list, cascade | `src/data/database.py` | `TestAst1878CandidateServerKeys` |
| Revised — legacy key write retired | `save_candidate` | `TestSaveCandidate::test_save_candidate_no_longer_takes_legacy_api_key` (replaces `test_stores_encrypted_api_key`) |
| Retired — `database.clear_candidate_api_key` deleted | — | `TestClearCandidateApiKey` removed; superseded by `TestAst1878CandidateServerKeys::test_list_and_clear` |

**Not moved here (by design, #3 AST-1879):** `test_dispatcher.py` / `test_agent.py` / `test_meteorite_email.py` stubs still hand `candidate_api_key` dicts to consumers #3 rewires; they stay green on this tip because they stub their own dicts.

**Integration:** none.

## QA test manifest

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1878CandidateServerKeys \
  tests/component/data/database/test_candidates.py::TestSaveCandidate \
  tests/component/data/database/test_candidates.py::TestGetCandidate \
  tests/component/data/database/test_candidates.py::TestListCandidates \
  tests/component/data/database/test_agents.py \
  tests/component/data/database/test_timesheets.py \
  tests/component/core/test_candidate.py::TestCandidateAdminFacades \
  tests/component/core/test_candidate.py::TestAst986SessionResumeParse \
  tests/component/core/test_candidate.py::TestAst1038SessionResumeWire \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_session_parse_returns_job_array_in_base_resume \
  tests/component/core/test_repo_admin_json.py::TestAst1878AgentSeedModels \
  tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed::test_repo_json_has_seven_sorted_persona_ids \
  tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed::test_repo_rows_use_repo_columns_only \
  tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed::test_startup_apply_loads_all_seven_agents \
  tests/component/core/test_repo_admin_json.py::TestAst783RepoAdminJsonDivergence \
  tests/component/core/test_repo_admin_json.py::TestAst1072ContactEstelleTurnCatalogRow \
  tests/component/utils/test_config.py::TestAst1877LlmCatalogConfig
```

**Pass criterion:** narrowed run green — not the zero-arg harness. Full `tests/component` failure set on this tip is identical to the same tree with `origin/ftr/AST-1851-support-openrouter-api-models` product (baseline diff: zero new, all 20 moved items green). Pre-existing reds left out of the manifest: `TestAst787AgentRepoJsonSeed::test_repo_rows_match_fixture_repo_column_mapping`, `TestAst996ExperienceJobArray::test_persist_craft_resume_base_keeps_job_array`, `TestAst1258CandidateBatchClaim` (two nodes).
