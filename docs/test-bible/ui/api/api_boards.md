# Api Boards

**Test module:** `tests/component/ui/api/test_api_boards.py`

### AST-457 · AST-471 · AST-379 · AST-649 · AST-648

**Retired (AST-649):** **`CandidateBoardSearches.tsx`** deleted; nav/route removed — backend **`/api/boards`** and core board modules remain (**§7.13q**). Manifest for removal: **§7.13zzu** (**AST-649**).

**Historical (pre-649):** **`CandidateBoardSearches`** — Active / Paused toggles PATCH **`state`** **`ACTIVE`** ↔ **`INACTIVE`**; **`ERROR`** row shows **Resume ACTIVE**. CRUD via **`/api/boards/searches`**, **`GET /api/boards`** picker.

| Area | Source | Component tests |
| --- | --- | --- |
| REST + DDL (backend unchanged) | `src/ui/api/api_boards.py`, `src/data/database.py` | `tests/component/data/database/test_board_search_integration.py` (**`TestBoardSearchRestAst458`**) |
