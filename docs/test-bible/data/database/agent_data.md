# Agent Data

**Test module:** `tests/component/data/database/test_agent_data.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/database.py` (`agent_data` schema / save / get / resolve / backfill) | `tests/component/data/database/test_agent_data.py` | no |

---

### AST-392

Baseline `save_agent_data` / `get_agent_data_by_batch` smoke (invalid `block_type`; save+read).

| Area | Source | Component tests |
| --- | --- | --- |
| Invalid block_type | `src/data/database.py` | `TestSaveAgentData::test_rejects_invalid_block_type` |
| Save + batch read | `src/data/database.py` | `TestSaveAgentData::test_saves_and_reads_batch_blocks` |

### AST-977 · AST-974

Nullable `ref_agent_data_id` on `agent_data`: every content write creates an audit row; identical logical `block_data` sets ref → earliest canonical and omits payload; reads resolve refs to plain text; cycle/missing ref raise. Historical backfill is **AST-978** (out of scope). Agent found/recorded debug: **`docs/test-bible/core/agent.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema ensure (fresh + ALTER) | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_ensure_schema_adds_ref_column_on_fresh_and_legacy` |
| Match → ref earliest + omit payload; block_type may differ | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_identical_write_refs_earliest_and_omits_payload` |
| Resolve by id / batch / ids | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_reads_resolve_ref_to_plain_text` |
| PK retry → `duplicate_id` | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_duplicate_primary_key_returns_duplicate_id` |
| Missing ref / cycle raise | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_resolve_raises_on_missing_ref_and_cycle` |
| Obsolete bool return assert | `tests/component/data/database/test_agent_data.py`, `test_rubric_vectors.py` | revised — `save_agent_data` returns outcome dict |

**AST-977** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_data.py \
  tests/component/data/database/test_rubric_vectors.py::TestFeedbackBlockType \
  tests/component/core/test_agent.py::TestAst977AgentDataDedupeDebug \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-978 · AST-974

One-time `backfill_agent_data_refs` — dry-run + live UPDATE of `ref_agent_data_id` on legacy duplicate content rows to earliest twin; never clears `block_data`; match without `exclude_agent_data_id` so canonical stays ref-null. Operator CLI: **`docs/test-bible/dev/backfill_agent_data_refs.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Dry-run would_set_ref / no write | `src/data/database.py` | `TestAst978BackfillAgentDataRefs::test_dry_run_would_set_ref_without_writing` |
| Live set_ref + payload intact + idempotent | `src/data/database.py` | `TestAst978BackfillAgentDataRefs::test_live_sets_ref_leaves_block_data_and_is_idempotent` |
| already_ref skip + decompress error | `src/data/database.py` | `TestAst978BackfillAgentDataRefs::test_skips_already_ref_and_records_decompress_error` |

**AST-978** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_data.py::TestAst978BackfillAgentDataRefs \
  tests/component/scripts/test_backfill_agent_data_refs.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1274 · AST-1273

**Parent:** [AST-1273](https://linear.app/astralcareermatch/issue/AST-1273/job-isnt-loading-on-recommended-page). **Publish:** `origin/sub/AST-1273/AST-1274-restore-recommended-job-detail-open`.

Complete fetch-side `ref_agent_data_id` resolve when local `block_data` is null/empty; secondary soft-fail in `get_entity_agent_story` / `GET /api/jobs/<id>` so corrupt graphs do not HTTP 500; `JobAnalysisReportModal` maps 404 → "Job not found" and other non-OK to honest copy.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty local + ref → canonical plain text; populated ref always follows chain | `src/data/database.py` (`_resolve_agent_data_block_data`) | **`TestAst1274ResolveNullBlockDataRef`**; existing **`TestAst977AgentDataSelfRefDedupe::{test_reads_resolve_ref_to_plain_text,test_resolve_raises_on_missing_ref_and_cycle}`** |
| Story soft-fail (list / get_agent_data_for_ids) | `src/core/roster.py` | **`TestAst1274AgentStorySoftFail`** |
| Detail soft-fail → 200 + `agent_story: []` | `src/ui/api/api_jobs.py` | **`TestJobsRoutes::test_detail_soft_fails_agent_story`**; regression **`test_detail_not_found`**, **`test_detail_returns_agent_story`** |
| Modal 404 vs non-404 load copy | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-1274 load error honesty`** |

**Broken / obsolete:** JAR fixture drift revised on first pass (`contact` / `job_resume`). **Return pass:** dropped `test_local_body_preferred_over_ref` — product follows populated `ref_agent_data_id` (no `has_local`); assert ref-target content when both body and ref set.

**Integration:** none — existing integration map has no job-detail scenario to revise (`docs/test-bible/integration/README.md` job-entity gap). Do not invent new integration coverage.

**AST-1274** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_data.py::TestAst1274ResolveNullBlockDataRef \
  tests/component/data/database/test_agent_data.py::TestAst977AgentDataSelfRefDedupe::test_reads_resolve_ref_to_plain_text \
  tests/component/data/database/test_agent_data.py::TestAst977AgentDataSelfRefDedupe::test_resolve_raises_on_missing_ref_and_cycle \
  tests/component/core/test_roster.py::TestAst1274AgentStorySoftFail \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_soft_fails_agent_story \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_not_found \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_returns_agent_story \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.
