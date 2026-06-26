# Backfill Latest-Only Rubric Entity Data (migration script)

**Test module:** `tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/backfill_latest_only_rubric_entity_data.py` | `tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py` | no |

**Existing coverage (reuse):** runtime dedupe + backfill normalizer — `docs/test-bible/core/roster.md` (**AST-726**, **AST-727**); entity ref upsert — `docs/test-bible/data/database/agent_responses.md` (**AST-726**).

---

### AST-727 (parent AST-717)

One-time backfill: collapse duplicate `agent_responses` refs per `task_key` (latest `created_at` wins), drop empty-`task_key` legacy refs, **`agent_data` untouched**. CLI `--dry-run`, `--company`, `--job` filters; idempotent second run.

| Area | Source | Component tests |
| --- | --- | --- |
| `normalize_agent_responses_for_backfill` | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst727NormalizeAgentResponsesForBackfill` |
| Company dry-run / live / unchanged / not-found | `scripts/migrations/backfill_latest_only_rubric_entity_data.py` | `TestBackfillCompanies` |
| Job dry-run / live / unchanged / not-found | same | `TestBackfillJobs` |
| `--company` only / `--job` only / full scan routing | same | `TestRunBackfill` |

Runtime sibling (**AST-726**): `dedupe_agent_responses_latest` — `TestAst726LatestOnlyRosterStory::test_dedupe_agent_responses_latest_wins_per_task_key`.

**AST-727** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst727NormalizeAgentResponsesForBackfill \
  tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.
