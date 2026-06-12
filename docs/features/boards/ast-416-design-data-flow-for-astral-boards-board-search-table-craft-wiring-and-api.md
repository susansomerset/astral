# Design data flow for Astral Boards: board_search table, craft wiring, and API

- **Linear:** [AST-416](https://linear.app/astralcareermatch/issue/AST-416/design-data-flow-for-astral-boards-board-search-table-craft-wiring-and-api)
- **Parent:** [AST-379](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards)
- **Feature ref:** `ftr/AST-416`
- **Blocked by:** [AST-415](https://linear.app/astralcareermatch/issue/AST-415) for real `BOARD_CONFIG` rows — plan uses config validation hook that no-ops or stubs until **AST-415** lands.

## Summary

Persist **candidate-owned saved board searches** in a `board_search` table (`board_search_id`, `candidate_id`, `board_key`, `criteria` JSON). Expose CRUD API and **`craft_board_search_*`** generation endpoints so the UI can build `criteria` from `TASK_CONFIG` shapes. Multiple rows per `(candidate_id, board_key)`; **no credential fields**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TASK_CONFIG` keys `craft_board_search_label`, `craft_board_search_criteria`; `BOARDS_CONFIG["board_search"]` | utils |
| `src/data/database.py` | Table `board_search`; CRUD | data |
| `src/core/boards.py` | `save_board_search`, `get_board_search`, `list_board_searches`, `delete_board_search`, `validate_board_key_adopted` | core |
| `src/ui/api/api_boards.py` | Blueprint: CRUD + craft generate routes | ui |
| `src/ui/server.py` | Register `api_boards` | ui |
| `tests/component/ui/api/test_api_boards.py` | CRUD + craft contract tests | tests |

## Stage 1: Config + schema

**Done when:** Two `board_search` rows for same `(candidate_id, board_key)` insert and list independently.

1. In `config.py`, add `BOARDS_CONFIG["board_search"]` with `criteria_version: 1` and document that `criteria` JSON keys must match fields returned by craft (step 3).

2. Add `TASK_CONFIG` entries:
   - `craft_board_search_label` — short human label for the saved search (string).
   - `craft_board_search_criteria` — structured criteria object; `response_schema` lists allowed keys aligned with future `search_keys` / `BOARD_CONFIG` (v1: `title_query`, `work_mode`, `max_listing_age` as optional strings until spike profiles promote page labels).

3. In `database.py` header inventory, add `board_search`:
   - `board_search_id TEXT PRIMARY KEY`
   - `candidate_id TEXT NOT NULL`
   - `board_key TEXT NOT NULL`
   - `label TEXT NOT NULL`
   - `criteria TEXT NOT NULL` (JSON)
   - `created_at`, `updated_at` TIMESTAMP

4. Implement `_ensure_board_search_table`, `save_board_search(...)`, `get_board_search(board_search_id)`, `list_board_searches(candidate_id, board_key=None)`, `delete_board_search(board_search_id)`.

## Stage 2: Core validation

**Done when:** `save_board_search` rejects unknown `board_key` when `BOARD_CONFIG` has no entry; accepts when key exists.

5. In `src/core/boards.py`, add `validate_board_key_adopted(board_key: str) -> None`:
   - Read `BOARD_CONFIG.get(board_key)` from `config.py` (empty dict until **AST-415**).
   - If missing, raise `ValueError(f"board_key not in BOARD_CONFIG: {board_key!r}")`.

6. Implement `save_board_search`, `get_board_search`, `list_board_searches`, `delete_board_search` calling database layer; `save`/`update` call `validate_board_key_adopted` and `json.loads` criteria with `ValueError` on invalid JSON.

⚠️ **Decision:** `candidate_id` column stores Astral **`astral_candidate_id`** string (same as `api_candidate` routes), not numeric PK.

## Stage 3: API + craft wiring

**Done when:** Authenticated tests create two searches, run craft criteria endpoint, PATCH criteria.

7. Create `src/ui/api/api_boards.py` blueprint `boards_bp`:

| Method | Path | Behavior |
|--------|------|----------|
| GET | `/api/boards/searches` | Query `candidate_id`, optional `board_key` |
| POST | `/api/boards/searches` | Body: `candidate_id`, `board_key`, `label`, `criteria` (object); server UUID `board_search_id` |
| GET | `/api/boards/searches/<board_search_id>` | Single row |
| PATCH | `/api/boards/searches/<board_search_id>` | Update `label` and/or `criteria` |
| DELETE | `/api/boards/searches/<board_search_id>` | Delete |
| POST | `/api/boards/searches/<board_search_id>/generate/<task_key>` | `task_key` ∈ `{craft_board_search_label, craft_board_search_criteria}`; `@require_auth`; delegate to `run_candidate_artifact_generation` pattern with `board_search` row as context |

8. Reject bodies containing keys matching `(?i)(password|username|cookie|token|credential)` with **400** `{"error": "board credentials not supported"}`.

9. Register blueprint in `server.py` under `/api/boards`.

## Stage 4: Tests

**Done when:** `pytest tests/component/ui/api/test_api_boards.py` green.

10. Fixture: test candidate + stub `BOARD_CONFIG["a16z"] = {"status": "adopted"}` in test setup (monkeypatch `config.BOARD_CONFIG`).

11. Assert two POST searches same board → distinct `board_search_id`; list length 2; craft generate returns 200 JSON shape per `TASK_CONFIG`.

## Execution contract

- No `gaze_board`, no job ingest, no Playwright in this ticket.
- No React UI (**Katherine** sibling).

## Self-Assessment

### Scope

**Single-Component** — `board_search` table, `boards.py` core, one API blueprint, tests.

### Conf

**Medium** — `BOARD_CONFIG` may be empty until **AST-415**; craft schema may evolve when spike `search_keys` promote.

### Risk

**Medium** — New table and API surface; must not break existing candidate routes.

## Self-review vs ASTRAL_CODE_RULES

- §2.1: criteria shape from `TASK_CONFIG`; board keys from `BOARD_CONFIG`.
- §3.3: core → data; ui → core only.
- §2.4: no batch claim in this ticket.

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-379/AST-416-design-data-flow-for-astral-boards`

### What's solid
| Area | Notes |
|------|--------|
| Schema/API | `board_search` table + CRUD; parameterized SQL; `api_boards` blueprint; craft task keys; component tests for POST/credential reject. |
| B2 | UI routes through `src.core.boards` only. |
| Boundaries | No gazer/ingest in this diff slice. |

### Issues
| Severity | Item |
|----------|------|
| **fix-now** | 1 — **`save_board_search`**: `return row or {}` after insert can yield **201 with `{}`** if re-read fails (**D3**). Raise or 500. |
| **fix-now** | 2 — **`POST .../generate`**: whitelist should match core (`craft_board_search_label` / `craft_board_search_criteria` only), not any `TASK_CONFIG` key. |
| **discuss** | 1 — **`BOARD_CONFIG` empty** until **AST-415** — all `board_key` creates fail until adopted keys land. |
| **discuss** | 2 — AuthZ: `candidate_id` from query without ownership check (product confirm). |
| **advisory** | 1 — Tests mock-heavy; no PATCH/DELETE or DB-path coverage yet. |

### Recommended actions
| Action | Owner |
|--------|--------|
| Fix fix-now on `dev-hedy`, re-publish sub branch | Hedy |

## Resolution (resolve-astral 2026-05-18)

| Radia fix-now | Action |
|---------------|--------|
| D3 empty body after insert | `save_board_search` raises `RuntimeError` if row missing after insert |
| Generate API task whitelist | `api_boards` `/generate/<task_key>` accepts only `craft_board_search_label` / `craft_board_search_criteria` |

Discuss items (BOARD_CONFIG empty until AST-415, candidate_id authZ) unchanged — documented in plan.
