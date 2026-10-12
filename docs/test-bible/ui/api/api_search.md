# API search

**Test module:** `tests/component/ui/api/test_api_search.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_search.py` | `tests/component/ui/api/test_api_search.py` | no (100% branch at AST-2173; not in `LOCKED_AT_100`) |

---

### AST-2173 · AST-2168

**Parent:** [AST-2168](https://linear.app/astralcareermatch/issue/AST-2168) (Add Universal Entity Search). **Publish:** `origin/sub/AST-2168/AST-2173-search-backend`.

`GET /api/search?q=…&candidate_id=…` under `@require_auth`. Blank `q` → 400 `{"error": "q required"}`; missing/blank `candidate_id` → 400 `{"error": "candidate_id required"}` (core never called). `q` goes to core exactly as sent; `candidate_id` stripped. Core exception → one `logger.exception` at the route + `server_error_from_exception` 500. No info line. Fixture: local `search_client` (bare Flask app + `search_bp`).

| Area | Component tests |
| --- | --- |
| 400s (4 shapes) + 401 without auth | **`TestAst2173SearchParams`** |
| 200 returns core dict; `q` verbatim, cid stripped | **`TestAst2173SearchOk`** |
| 500 + `logger.exception` once, no `logger.info` | **`TestAst2173SearchError`** |
| Route → core → real SQLite: keys exactly `job`/`company`/`meteorite`, other candidate absent; no match → three empty lists | **`TestAst2173SearchRealDb`** (ui `sqlite_in_memory`) |

**Broken / obsolete:** none — new blueprint. **Integration:** none. Manifest: [`../../core/search.md`](../../core/search.md) § AST-2173.
