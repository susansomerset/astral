# Search (data)

**Test module:** `tests/component/data/database/test_search.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/database.py` — `search_entity_rows` | `tests/component/data/database/test_search.py` | no (`database.py` not in `LOCKED_AT_100`) |

---

### AST-2173 · AST-2168

**Parent:** [AST-2168](https://linear.app/astralcareermatch/issue/AST-2168) (Add Universal Entity Search). **Publish:** `origin/sub/AST-2168/AST-2173-search-backend`.

`search_entity_rows(entity_type, candidate_id, needle)`: one generic read; table = `SEARCH_ENTITY_CONFIG` key, columns = its base + payload fields; `candidate_id = ?`; case-insensitive `LIKE … ESCAPE '\'` with `\` `%` `_` escaped; `matched_fields` per row (config order, `__hit_N` flags popped); `ORDER BY state_changed_at DESC NULLS LAST`; no `LIMIT`. Blank cid / needle → `ValueError`; unknown type → `KeyError`. All tests on real SQLite (`sqlite_in_memory`).

| Area | Component tests |
| --- | --- |
| Every configured field (+ `name_fields`, `candidate_id`, `state_changed_at`) is a real column, per type | **`TestAst2173RegistryMatchesSchema`** (3) |
| AC 1 candidate scope, all three tables | **`TestAst2173CandidateScope`** |
| AC 3 job full id / `company_job_id` / 6-char middle; meteorite numeric `id`; meteorite `astral_job_id` | **`TestAst2173IdsFindable`** (3) |
| `matched_fields` base + payload in config order; no `__hit_` leak; company / meteorite payload fields; meteorite contact column via `METEORITE_CONFIG["electronic_contact_column"]` | **`TestAst2173MatchedFields`** (3) |
| AC 5 case-insensitive; `%` `_` `\` literal | **`TestAst2173CaseAndLiteralWildcards`** (2) |
| AC 6 600 matches, no cap | **`TestAst2173NoCap`** |
| AC 7 drop `job_link` from config → link-only job gone | **`TestAst2173FieldsFromConfig`** |
| Newest `state_changed_at` first, NULL last | **`TestAst2173Order`** |
| Guards (blank cid ×3, blank needle ×3, unknown type), fresh-DB empty list ×3, header inventory line | **`TestAst2173Guards`** |

**Note:** `save_job`'s INSERT ignores `latest_score` (update path only) — seed scores with a second `save_job(jid, latest_score=…)` call (used in `core/test_search.py`).

**Broken / obsolete:** none. Cluster row added to `tests/component/data/database/_README.md`. Manifest: [`../../core/search.md`](../../core/search.md) § AST-2173.
