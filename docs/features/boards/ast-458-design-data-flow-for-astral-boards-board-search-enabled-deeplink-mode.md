# Design data flow for Astral Boards: board_search enabled, deeplink mode, duplicate validation

- **Linear:** [AST-458](https://linear.app/astralcareermatch/issue/AST-458/design-data-flow-for-astral-boards-board_search-enabled-deeplink-mode)
- **Parent:** [AST-379](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards)
- **Feature ref (origin):** `sub/AST-379/AST-458-design-data-flow-for-astral-boards-board-search-enabled-deeplink-mode`
- **Depends on shipped:** AST-416 `board_search` table, Craft wiring, REST in `src/core/boards.py` + `src/ui/api/api_boards.py`; batch columns `status` / `batch_id` remain operational only (ship path as in current `database.py`)

## Summary

This ticket extends **`board_search`** so each row has a separate user **`enabled`** flag (default on), persists either **criteria-driven** search (**JSON**) or a full **deeplink URL** (**mutually exclusive** shapes switchable via PATCH), enforces **board entry-domain** parity on deeplinks at save time, and rejects **duplicate** saved searches per `(candidate_id, board_key)` using **normalized** URL equality or **normalized** criteria JSON equality. Responses align with the **AST-457** UI contract (`label`, `board_key`, `enabled`, explicit **mode**, timestamps, identifiers). Scope is backend + SQLite only — no React, no BOARD_CONFIG authoring, no `gaze_board` behavior (**AST-459** consumes this contract).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Under `BOARDS_CONFIG["board_search"]`, add `save_modes`: `("criteria", "deeplink")` (tuple or list — single source for allowed modes; validator reads via `boards` layer). Optionally add `"dedup_trailing_slash_rule": "strip_non_root"` literal if you prefer a named constant alongside URL normalization (optional — see Stage 2). | utils |
| `src/data/database.py` | Extend header inventory comments for **`board_search`**: document `enabled`, `search_mode`, `deeplink_url`, meaning of `criteria` vs `deeplink`; idempotent **`ALTER`** in `_ensure_board_search_table` + default values; extend `_parse_board_search_row`, `save_board_search_row` insert columns, **`update_board_search_row`**/`list`/`get` unchanged SQL shape except selected columns (`SELECT *` already). Add **no duplicate logic in data layer** — core passes normalized fingerprint / calls list helper. If new columns need explicit arguments on `save_board_search_row`, extend signatures and every caller in same change-set. | data |
| `src/core/boards.py` | Add `_normalize_board_deeplink_url`, `_normalize_criteria_blob`, `_board_entry_domain(board_key)`, `_duplicate_board_search_conflict(...)` helpers; extend `save_board_search`, `update_board_search` arguments for `enabled`, `search_mode`, `deeplink_url`, coercions, mutual exclusivity, domain + dup checks **before** calling `database`. Preserve existing craft / listing helpers untouched except imports. | core |
| `src/ui/api/api_boards.py` | POST/PATCH acceptance for `enabled`, `mode` (wire name `mode` ↔ DB `search_mode`), `criteria`, `deeplink_url`; deterministic JSON responses with boolean `enabled`, string `mode` (`criteria` \| `deeplink`), nullable `deeplink_url`, `criteria` object. Map credential rejection pattern unchanged. | ui |

Spike/playwright artifacts: none in-repo — use `debug/spikes/AST-458/…` if needed (**gitignored**).

## Stage 1: Config + SQLite schema (+ data-layer row shape)

**Done when:** Fresh DB migrations create/amend **`board_search`** with new columns with safe defaults for existing rows; `SELECT *` round-trips parse; **`save_board_search_row`**/`update_board_search_row` read/write those columns without breaking claim SQL (below).

1. **Config:** In `BOARDS_CONFIG["board_search"]`, add key **`save_modes`** with value **`("criteria", "deeplink")`**. Builders validate `search_mode`/API `mode` only against values in this tuple (read from config inline in `boards.save_*`).
2. **Schema (SQLite):** In `_ensure_board_search_table`:
   - Add column **`enabled`**: `INTEGER NOT NULL DEFAULT 1` (truthy → user enabled).
   - Add column **`search_mode`**: `TEXT NOT NULL DEFAULT 'criteria'` constrained in core (not SQLite CHECK unless you prefer — ⚠️ **Decision:** enforce in **`boards`** only via config tuple; DB stays permissive `TEXT`).
   - Add column **`deeplink_url`**: `TEXT` nullable (null when criteria mode).
   - Use existing **idempotent ALTER** loop pattern already used for `status`/`batch_id`.
3. **`_parse_board_search_row`:** Return `criteria` decoded as today; add raw **`enabled`** as `bool(row["enabled"])` style for consumers; **`search_mode`** string; **`deeplink_url`** `str | None`.
4. **`save_board_search_row`:** Extend INSERT column list with `enabled`, `search_mode`, `deeplink_url` (defaults wired from caller — never omit if NOT NULL semantics require explicit binds).
5. **`update_board_search_row`:** Extend allowed kwargs tuple `enabled`, `search_mode`, `deeplink_url`, `criteria_json`, `label` consistently with PATCH contract.
6. **Header inventory comments** atop `database.py` table list: mirror new columns verbatim for **§1.1**.

## Stage 2: Normalization + domain + duplicate policy (pure `boards`)

**Done when:** Two helper-level unit behaviors are defined in prose here and exercised in **`build-astral`** by existing test patterns Betty adds later — planner does **not** add **`tests/`** (`build-astral` test-tree ban).

7. **`_normalize_board_deeplink_url(url: str) -> str`:** Implement in `boards.py`:
   - `strip()` inputs; **`urllib.parse.urlparse` / `urlunparse`**.
   - Normalization: **`scheme`** and **`netloc`** lowercased (hostname lowercased). Empty scheme after normalization → treat as validation error (**400**) at save boundary.
   - **Path:** If path is empty, treat as `"/"`; otherwise apply ⚠️ **Decision:** **`path.rstrip("/")`** — if result is empty string, use **`"/"`** so root collapses cleanly.
   - **Query:** Rebuild sorted by **parameter name ascending** ASCII; duplicate names — preserve order of first occurrence stable sort by `(key, original_index)`. Use `urllib.parse.parse_qsl`/`urlencode(..., doseq=True)` semantics that match Flask's typical `requests`/`urlencode` behavior.
   - **Fragment (`#`):** Stripped/not included in normalization — ⚠️ **Decision:** Fragments never reach server-stored uniqueness; drop fragment before fingerprint.
8. **`_criteria_fingerprint_json(criteria: Any) -> str`:** Canonical form: **`json.dumps`** recursively built **sorted keys** (`sort_keys=True`) with **separator `(",", ":")`** on outer + inner dumps if you build intermediate dict manually; rejects non-JSON-serializable with **400**.
9. **Duplicate fingerprint:**
   - If `search_mode == "criteria"`: fingerprint = **`_criteria_fingerprint_json(criteria_dict)`**.
   - If `search_mode == "deeplink"`: fingerprint = **`_normalize_board_deeplink_url(stored_or_incoming_url)`**.
10. **Duplicate scan:** Implement **`_candidate_board_duplicate(board_search_id: Optional[str], candidate_id: str, board_key: str, fingerprint: str, fingerprint_kind: Literal["criteria","deeplink"])`** returning **matching `board_search_id` or None**:
    - **`database.list_board_search_rows(candidate_id, board_key=board_key)`** then for each sibling:
      - SKIP same primary key when **`board_search_id` matches PATCH target**.
      - For each sibling row derive fingerprint using **its** saved `search_mode`/criteria/deeplink.
      - **Collision** if fingerprints **string-equal** (`==`).
11. **`_validate_deeplink_domain(board_key: str, deeplink_url: str)`:** Resolve board profile via **`BOARD_CONFIG[board_key]`** (reuse `validate_board_key_adopted`). Take **`entry_url` if non-empty else `jobs_url`**; both must yield a parseable **`netloc`**. Normalize hostnames (**lowercase**). Deeplink **`netloc` must equal** board entry **`netloc`** (**strict hostname match**, no subdomain wildcard unless explicitly added — ⚠️ **Decision:** substring / parent-domain matches are **not** accepted; Katherine may request relax in AST-457 only if Susan comments). Port differences: ⚠️ **Decision:** Normalize by comparing **`netloc`** from `urlparse` as-is (includes `:port`). If **`entry_url` omits scheme**, reject with explicit **400** saying board profile misconfigured (`board_key` in message).

## Stage 3: Core CRUD coherence

**Done when:** `save_board_search` / `update_board_search` orchestrate validations; mutual exclusivity and defaults match AC.

12. **`save_board_search`** signature extension: **`enabled: Optional[bool]`** default **`True`**; **`search_mode`** default **`"criteria"`**; **`deeplink_url`** optional **`str | None`**.
    - Preconditions: **`validate_board_key_adopted`** unchanged.
    - If **`search_mode == "criteria"`**: require **`criteria`** presents per existing `_criteria_to_json` path (non-empty dict after parse **or allow `{}` if craft allows empties** — ⚠️ **Decision:** `{}` acceptable for criteria mode baseline; disallow only when BOTH empty criteria and deeplink absent on create).
    - If **`search_mode == "criteria"`**: **force `deeplink_url` stored SQL `NULL`**.
    - If **`search_mode == "deeplink"`**: require **`deeplink_url` non-empty** after strip; coerce **`criteria_json`** to **`'{}'`** constant string for SQLite column (**NOT NULL** column still satisfied).
13. **`update_board_search`**: accept optional switches; when **`mode` toggles**, explicitly **clear opposing storage** (**NULL** vs `'{}`). If PATCH sets only `criteria` without `mode`, remain in prior mode unless conflicting fields appear — ⚠️ **Decision:** PATCH that sends **`criteria` + explicit `deeplink_url` non-null** simultaneously without `mode` → **400** `mutually_exclusive`.
14. **Duplicate enforcement:** Invoke duplicate scan immediately before **`database.save`** / **`update`** with assembled target fingerprint.
15. **Domain enforcement:** Deeplink saves / updates **`_validate_deeplink_domain`** first (after adoptee board validation).

## Stage 4: REST surface (`api_boards.py`)

**Done when:** Postman-level JSON contract stable; statuses match semantics.

16. **`POST /api/boards/searches`**: Body JSON accepts **`candidate_id`, `board_key`, `label`**, **`mode`** (**optional**, default **`criteria`**), **`enabled`** (**optional**, default **true**), **`criteria`** (object — required unless mode `deeplink`), **`deeplink_url`** (string — required iff mode **`deeplink`**). Maintain credential scanner.
17. **`PATCH /searches/<id>`**: Allow partial **`label`, enabled, mode, criteria, deeplink_url`** respecting mutual exclusivity and duplicate/domain rules.
18. **Wire JSON outward:** Responses map **`search_mode`** → **`mode`** property; coerce **`enabled`** to JSON boolean (`True`/`False`). Include **`deeplink_url`**: `null` when criteria mode. Include **`criteria`** object unchanged from `_parse_board_search_row` shape. Preserve **`created_at` / `updated_at` / board_search_id** keys already returned from DB dict (ensure serializers leave ISO/str as stored).
19. Errors: duplicate → **409** `{"error": "duplicate board search"}`; domain mismatch → **400** `{"error": "deeplink domain does not match board entry domain"}`; mutual exclusivity → **400**.

## Execution contract

- Executes stages in order during **`build-astral`**; stage boundaries = commits per **`build-astral`** conventions.
- **No** edits to **`gazer.py`** claim path here — **AST-459** adjusts claim filter for `enabled` + deeplink gaze path.
- **No** repurposing **`status`** for user enable/disable.

## Self-Assessment

### Scope

**Single-Component** — Touches **`config`** block for enumerated modes, **`database`** DDL/persistence for **`board_search`**, **`boards`** orchestration helpers, **`api_boards`** request/response contract only.

### Conf

**high** — Extends AST-416 patterns (`board_search_*` primitives, Flask blueprint shapes) without inventing parallel tables; duplication + URL rules are spelled out precisely.

### Risk

**Medium** — Incorrect duplicate/domain logic blocks legitimate Katherine flows or admits unsafe cross-board URLs; reversible via PATCH + clarified rules.

---

## Rules cross-check

- **§1.3 DRY:** Normalization centralized in **`boards`** helpers (`_normalize_*`).
- **§2.1 config:** Allowed save modes enumerated under **`BOARDS_CONFIG["board_search"]`** tuple.
- **§2.4 batch:** **`status`** / `batch_id` unchanged — still claim lifecycle only (**AST-418**).
- **§2.6 state machine:** Candidate/job company states unaffected.
- **§3.3 imports:** API unchanged — still **`core.boards`** + Flask only.
- **§3.5 naming:** snake_case Python; REST JSON keys **`mode`** for UI alignment.

---

## Review

**Reviewer:** Radia (`linear-radia`) · **Linear:** [AST-458](https://linear.app/astralcareermatch/issue/AST-458/design-data-flow-for-astral-boards-board_search-enabled-deeplink-mode)

**Git:** Three-dot review vs **`origin/dev`** on publish branch **`origin/ftr/AST-458`** at tip **`372b877e`** (integration + tests). *`origin/sub/AST-379/AST-458-design-data-flow-for-astral-boards-board-search-enabled-deeplink-mode` matches plan-only **`c01e203d`**; it is not the integration tip Betty exercised.*

### What’s solid

- **AC alignment (persistence + API):** `enabled`, `search_mode` / wire `mode`, nullable `deeplink_url`, criteria JSON, normalized **duplicate** rejection, and **entry-domain** checks on save/update are implemented in **`src/core/boards.py`**, **`src/data/database.py`**, and **`src/ui/api/api_boards.py`** in line with the staged plan.
- **Layering:** `api_boards` stays **core + Flask** only; duplicate logic is not pushed into **`database`** helpers.
- **REST contract:** 409 on duplicate, explicit domain-mismatch error string via `DeeplinkDomainMismatchError`, mutual-exclusivity errors on POST/PATCH, and response serialization exposing `mode` + boolean `enabled` are coherent.

### Issues

**(fix-now)** **`run_board_search_gaze`** always builds navigation off **`BOARD_CONFIG` `entry_url`/`jobs_url` + criteria query keys** and never branches on **`row["search_mode"]` / `row["deeplink_url"]`**. Deeplink-mode rows therefore do not gaze the **stored user URL** the API accepted — the URL is validated and persisted but not consumed on the scrape path. This breaks the end-to-end meaning of deeplink mode for any `gaze_board` run that uses this helper.

**(discuss)** **Ticket boundary vs branch reality:** AST-458 description says **no `gaze_board`**, but the publish branch includes **`dispatcher` `entity_type == "board_search"`**, **`consult.run_consult_task` routing** to **`process_gaze_board_batch`**, and **`gazer.process_gaze_board_batch`**. Likely intentional **AST-379 / AST-418** stack integration — worth confirming in tracking so scope text and actual merge stay aligned.

**(discuss)** **`claim_board_search_batch`** does not filter **`enabled`**, so **user-disabled** rows remain batch-claimable until **AST-459** (or claim SQL) narrows the set.

**(discuss — rubric B1)** Several function-scoped imports (**`boards.extract_board_listings`**, **`run_board_search_gaze`**, **`dispatcher` board_search branch**, **`consult` board_search branch**) lack the short **lazy-load / cycle-break** comment **`ASTRAL_CODE_RULES`** expects when imports are not at module top.

**(advisory)** **`_parse_board_search_row`** tolerates invalid criteria JSON by leaving a raw string — consider surfacing corruption as a hard error on read paths if UI should never see opaque strings.

**(advisory)** Broad **`except Exception`** in **`run_board_search_generation`** / **`process_gaze_board_batch`** returns structured failure — acceptable mitigated pattern, but narrowing types would reduce accidental masking.

### Recommended actions

| Severity | Action |
|----------|--------|
| fix-now | Teach **`run_board_search_gaze`** a **`search_mode == "deeplink"`** path that loads **`row["deeplink_url"]`** (post-normalization / domain checks already implied by storage) instead of always using criteria-derived query params against **`entry_url`**. |
| discuss | Record whether **gaze_board wiring** is credited to **AST-418** (plan) vs **AST-458** for traceability. |
| discuss | Coordinate **`enabled` filtering** in claim SQL with **AST-459** so disabled rows do not run unless explicitly desired. |
| discuss | Add **B1** one-liners (or refactor imports) for lazy imports called out above. |
| advisory | Tighten criteria JSON parse failure behavior if corrupt rows should not propagate to clients. |

---

## Resolution

**2026-05-23 — Hedy (`resolve-astral`, Review Posted → User Testing)**

- **fix-now — deeplink gaze:** `run_board_search_gaze` branches on `search_mode`: **`deeplink`** navigates with `board_search_deeplink(page, stored_deeplink_url, None)`; **criteria** keeps `entry_url` + synthesized query keys. Aligns with Radia’s finding and **AST-459** plan text (implemented here on **`ftr/AST-458`** so the publish branch matches the reviewed stack).
- **advisory / discuss — criteria JSON:** `_parse_board_search_row` now **raises** `ValueError` on invalid criteria JSON instead of leaving an opaque string.
- **discuss — B1 lazy imports:** One-line rationales on function-local imports in `boards.extract_board_listings`, `boards.run_board_search_gaze`, `gazer.process_gaze_board_batch`, `consult.run_consult_task` (`board_search`), and `dispatcher._run_unified` (`board_search` claim/clear).
- **discuss — gaze_board wiring:** Batch wiring lives under **AST-418** / parent **AST-379** integration; **AST-458** ticket “no gaze_board” refers to **not expanding** new gaze behavior beyond what this branch already carries for **board_search** CRUD + validation.
- **discuss — `enabled` in claim:** Left to **AST-459** per review table; **no** `claim_board_search_batch` change in this **458** publish commit.
