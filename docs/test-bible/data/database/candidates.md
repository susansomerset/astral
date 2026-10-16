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

### AST-1901 · AST-1851 (bug: candidate keys as a JSON array on the candidate)

> Supersedes the AST-1878 key storage above. `candidate_key`, `set/clear/list_candidate_server_key(s)` and `TestAst1878CandidateServerKeys` are gone. AST-1878 manifest lines that cite them are frozen records.

Per-server keys live in a `candidate.api_keys` column: a JSON array of `{"server", "key"}` with the key Fernet-encrypted, at most one entry per server, no fixed slots. `update_candidate_api_keys(cid, [{server, key}])` sets or replaces with a non-empty key and removes with `""`. Existing order is kept and new servers append. It raises on a duplicate or unknown server, a blank id, or a missing candidate, and writes nothing on error. `_parse_candidate_row` hydrates `candidate_api_keys {server: plaintext}` on every parsed row, list rows included. Undecryptable or malformed entries read as not set. Schema setup adds the column and drops `candidate_key` (DDL only, no copy). Hard delete no longer counts `candidate_key`. The routing contract (`candidate_api_keys`) is unchanged for AST-1879 readers.

| Area | Source | Component tests |
| --- | --- | --- |
| New (bug-repro): array storage, hydrate, edits, duplicate/bad input, undecryptable, malformed, schema add + drop, retired helpers, hard delete | `src/data/database.py` | `TestAst1901CandidateApiKeysArray` (replaces `TestAst1878CandidateServerKeys`) |
| Revised: facade `update_candidate_api_keys`; per-server set/clear wrappers retired | `src/core/candidate.py` | `test_candidate.py::TestCandidateAdminFacades` ([`../../core/candidate.md`](../../core/candidate.md)) |
| Revised: outbound `api_keys: [{server, label}]`, PUT `api_keys: [{server, key}]`, duplicate → 400 | `src/ui/api/api_candidate.py` | [`../../ui/api/api_candidate.md`](../../ui/api/api_candidate.md) § AST-1901 |
| Revised: stored entries + "Add API key for…" picker | `AdminManageCandidates.tsx` | [`../../frontend/pages.md`](../../frontend/pages.md) § AST-1901 |

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

## QA test manifest (AST-1901)

**Bug-repro (qa-fix):** every node below except the two pre-existing reds is red on the pre-fix tree (`origin/sub/AST-1851/AST-1901-candidate-keys-json-array` @ `f422a71d0`). Each fails for the root cause: no `update_candidate_api_keys`, no `api_keys` column, dict-shaped outbound `api_keys`, the old `{server_id: key}` PUT contract, or fixed per-server fields. test-fix must see all of them flip green.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1901CandidateApiKeysArray \
  tests/component/data/database/test_candidates.py::TestSaveCandidate \
  tests/component/core/test_candidate.py::TestCandidateAdminFacades \
  tests/component/ui/api/test_api_candidate.py::TestSanitizeCandidate \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes \
  tests/component/core/test_agent_ast1879.py

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

**Pass criterion:** all green except two pre-existing reds that also fail on the pre-fix tree for unrelated reasons: `TestCandidateRoutes::test_list_candidates_and_states` (stale `PROSPECT`) and `::test_update_merges_data_and_state` (`qualify_job_listings` agent_task 400).
