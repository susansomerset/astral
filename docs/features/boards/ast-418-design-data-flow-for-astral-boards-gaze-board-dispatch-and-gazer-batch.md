# Design data flow for Astral Boards: gaze_board dispatch and gazer batch

- **Linear:** [AST-418](https://linear.app/astralcareermatch/issue/AST-418/design-data-flow-for-astral-boards-gaze-board-dispatch-and-gazer-batch)
- **Parent:** [AST-379](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards)
- **Feature ref:** `ftr/AST-418`
- **Depends on:** [AST-417](ast-417-design-data-flow-for-astral-boards-board-job-ingest-fork-board-search-id-dedup-invalid-title.md) (ingest fork), [AST-416](ast-416-design-data-flow-for-astral-boards-board-search-table-craft-wiring-and-api.md) (`board_search` rows)

## Summary

Implement **`gaze_board`**: a `dispatch_tasks` row with `entity_type` that claims **`board_search`** rows (not companies), loads `BOARD_CONFIG[board_key]` + row `criteria`, runs **anonymous** Playwright pre-scrape (**`deep_link` first**, `interactive` later), extracts listing HTML, calls **`ingest_board_listings`** (**AST-417**). Same mechanical depth as company gazer batch — **no qualify/evaluate** in this batch.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `BOARDS_CONFIG["gaze_board"]`; seed `dispatch_tasks` doc in plan (Susan applies migration row) | utils |
| `src/data/database.py` | `claim_board_search_batch`, `clear_board_search_batch` | data |
| `src/core/gazer.py` | `process_gaze_board_batch`; deep_link scrape path | core |
| `src/core/boards.py` | `run_board_search_gaze(batch_id, board_search_row)` orchestration | core |
| `src/external/playwright.py` | `board_search_deeplink(page, entry_url, params) -> tuple[str, dict]` | external |
| `tests/unit/test_gaze_board_batch.py` | Claim + ingest called with mocks | tests |

## Stage 1: Dispatch + claim

**Done when:** `claim_board_search_batch(batch_id, limit)` returns rows; `clear_board_search_batch` releases.

1. Document SQL seed for `dispatch_tasks` (Susan or migration script, not committed in spike):

| Field | Value |
|-------|-------|
| `task_key` | `gaze_board` |
| `entity_type` | `board_search` |
| `trigger_state` | `READY` (or dedicated `board_search` state — see step 2) |
| `batch_call_mode` | `parallel` or match company gaze |
| `batch_size` | from config default 5 |

2. Add `board_search.status` column **or** use `criteria` + `updated_at` only — ⚠️ **Decision:** add `status TEXT DEFAULT 'active'` on `board_search` (`active` | `running` | `error`) for claim semantics; claim sets `running`, clear sets `active`.

3. In `database.py`: `claim_board_search_batch(batch_id, limit) -> List[dict]`, `clear_board_search_batch(batch_id)`.

4. In `dispatcher.py`, route `entity_type == "board_search"` to new handler (mirror `job` / company paths) calling `gazer.process_gaze_board_batch`.

## Stage 2: deep_link scrape (v1 ship)

**Done when:** Integration test with mocked Playwright returns HTML passed to ingest.

5. In `playwright.py`, add `async def board_search_deeplink(page, entry_url: str, query_params: dict) -> tuple[str, dict]`:
   - Build URL: `entry_url` + `?` + `urlencode(query_params)` when params non-empty.
   - `goto` + consent dismiss using `ASTRAL_CONFIG["cookie_dismiss_selectors"]`.
   - Return `(page.content(), meta)` with `meta["mode"] = "deep_link"`.

6. In `boards.py`, `async def run_board_search_gaze(batch_id: str, row: dict) -> dict`:
   - Load `profile = BOARD_CONFIG[row["board_key"]]`.
   - If `profile.get("scrape_mode") == "deep_link"` or `criteria` contains `params` URL keys, call deeplink.
   - If `scrape_mode == "interactive"`, raise `NotImplementedError("interactive gaze_board — follow-on")` in **this ticket** unless Susan waives in Linear comment.

⚠️ **Decision (ticket AC):** Ship **`deep_link` only** in build; `interactive` widget driving deferred to follow-on after spike profiles in `BOARD_CONFIG`.

7. Extract listing cards: reuse `gazer.extract_raw_job_listings` or add `extract_board_listings(html, parse_instructions)` in `boards.py` using profile `parse_instructions`.

8. Call `ingest_board_listings(...)` with `title_matchers` from `profile.get("title_patterns")` compiled via shared helper (same as company gazer).

## Stage 3: Gazer batch wrapper

**Done when:** `process_gaze_board_batch` logs per-row outcomes; records `board_search_run` when **AST-417** added table.

9. In `gazer.py`, `async def process_gaze_board_batch(batch_id, searches, debug=False, ctx=None)`:
   - For each row: try `run_board_search_gaze`; on success `clear_board_search_batch` slice; on failure set status `error` + log.

10. Return list of `{board_search_id, new, duplicates, invalid_title, error?}` per entity.

## Stage 4: Tests

**Done when:** Unit tests mock playwright + ingest; dispatcher routes `board_search`.

11. `test_gaze_board_batch.py`: patch `board_search_deeplink` to return fixture HTML; assert `ingest_board_listings` called with `board_search_id`.

## Execution contract

- **Anonymous only** — if `BOARD_CONFIG` has `login_required: true`, raise before browser starts.
- No `BOARD_CONFIG` authoring (**AST-415**).
- No UI.

## Self-Assessment

### Scope

**MAJOR-CHANGE** — dispatcher route, gazer batch, playwright helper, boards orchestration.

### Conf

**LOW** — deep_link path is narrow; interactive explicitly deferred.

### Risk

**HIGH** — dispatcher + gazer integration; must not break company gaze.

## Self-review vs ASTRAL_CODE_RULES

- §2.2: Playwright in external; core orchestrates.
- §1.4: timeouts named in playwright module.
- §2.4: claim/clear batch pattern matches company gaze.

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-379/AST-418-design-data-flow-for-astral-boards`

### What's solid
| Area | Notes |
|------|--------|
| Gaze path | `dispatch_tasks` entity `board_search`; `process_gaze_board_batch` → `run_board_search_gaze` → `ingest_board_listings`; `board_search_deeplink` v1. |
| H* | Dispatcher claim + `finally` clear pattern present (see fix-now on clear semantics). |
| Tests | `TestProcessGazeBoardBatch` for success/fail/skip. |

### Issues
| Severity | Item |
|----------|------|
| **fix-now** | 1 — **`clear_board_search_batch`** sets **`status='active'`** for all rows in batch, undoing **`error`** set in gazer — mirror **`clear_job_batch`** (null `batch_id` only). |
| **fix-now** | 2 — **`board_search_run` PK = `batch_id` only** — multi-search batches overwrite metrics; need composite PK or per-search run id. |
| **fix-now** | 3 — **`test_tracker.py`** `title_mismatch` vs **`invalid_title`** (same as **417**). |
| **discuss** | 1 — After (1), failed rows return to **`active`** — confirm retry vs persistent error UX. |
| **advisory** | 1 — Tip stacks **416+417+418** commits — UAT/prep-uat should treat as ordered set. |

### Recommended actions
| Action | Owner |
|--------|--------|
| Fix fix-now items on `dev-hedy`, re-publish **418** (and dependent sub branches) | Hedy |

## Resolution (resolve-astral 2026-05-18)

| Radia fix-now | Action |
|---------------|--------|
| `clear_board_search_batch` reset `error` → `active` | Clear `batch_id` only (mirror `clear_job_batch`); preserve `status` |
| `board_search_run` PK `batch_id` only | Composite PK `(batch_id, board_search_id)` + idempotent migration from old table |
| `test_tracker` `title_mismatch` | **[qa-handoff]** to Betty (engineer test-tree ban) — see AST-417 |

Discuss: failed rows stay `error` until manually cleared or retried — intentional for now.
