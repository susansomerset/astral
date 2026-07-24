# AST-977 — agent_data self-ref + dedupe write/read

- **Linear:** [AST-977](https://linear.app/astralcareermatch/issue/AST-977/agent-data-self-ref-dedupe-writeread-add-a-self-reference-key-to-agent)
- **Parent:** [AST-974 — Add a self-reference key to agent_data](https://linear.app/astralcareermatch/issue/AST-974/add-a-self-reference-key-to-agent-data)
- **Publish ref:** `origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read`
- **Summary:** Add nullable `ref_agent_data_id` on `agent_data`, ensure it via the existing lazy/bootstrap schema path, and change write/read so every content write still creates an audit row while identical `block_data` reuses the earliest canonical row (omit duplicate payload on the audit row). Reads resolve refs to plain text transparently. Canonical rows keep `ref_agent_data_id` null; self-refs/cycles raise. Debug found/recorded trails on touched `agent.py` write/read paths when `debug=True`. Historical backfill is **AST-978** (out of scope).

## UAT fitness

- **AC restored:** Parent AST-974 AC 1–6, 8–9 (runtime; not backfill AC 7): schema nullable `ref_agent_data_id` via normal schema-ensure; every content write creates an audit row; match → `ref_agent_data_id` → earliest and no second full content copy; no-match → content row with ref null; canonical earliest always ref null; reject self-ref/cycle; match on exact `block_data` only (block_type may differ); reads by id and by batch return the same plain-text payload whether direct or referenced; debug found/recorded when `debug=True` / quiet when `debug=False`; existing store-then-retrieve system/task/response flows still succeed.
- **Correct outcome:** After a write of content that already exists, SQL shows a new audit row whose `ref_agent_data_id` points at the earliest identical content row and whose `block_data` is empty/absent; callers that load by id or batch still receive the full plain-text payload; first/canonical content row never points at itself.
- **Sibling check:** AST-978 owns one-time backfill of refs on existing duplicates and must not clear `block_data`. This plan does not implement backfill, does not null/delete historical payloads, and leaves AST-978 free to set refs on legacy duplicate content rows. Verified by scope Boundaries below and by not adding any backfill script/stage.
- **Not sufficient:** Removing an exception or making INSERT succeed without the audit-row + ref + transparent-read contract is **not** done.
- **Wrong fix rejected:** Skipping the new row when a match exists (no audit trail), matching on `(block_type, block_data)`, hashing without storing refs, or clearing historical `block_data` on write — all violate parent AC / Boundaries. Correct path is always-insert audit row + ref-to-earliest + omit payload + resolve on read.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory; `_ensure_agent_data_schema` column; match helper; `save_agent_data` dedupe write; resolve on `get_agent_data` / `get_agent_data_by_batch` / `get_agent_data_for_ids` | data |
| `src/core/agent.py` | Thread `debug` into store helpers; emit debug-contract found/recorded on write; emit resolve trail on touched read/hydration paths when `debug=True` | core |
| `docs/ASTRAL_CODE_RULES.md` | Extend the existing Data-layer `agent_data` compression sentence to state that `ref_agent_data_id` is resolved transparently on read (callers still see plain text) | docs |

**Out of scope (explicit):**

| Item | Owner |
|------|--------|
| Backfill `ref_agent_data_id` on existing duplicates | **AST-978** |
| Clear / null / delete / vacuum historical `block_data` | Susan SQL outside epic |
| BLOCK_TYPES, prompt assembly, Anthropic call behavior | unchanged |
| `tests/` / bible | Betty |

---

## Stage 1: Schema + inventory

**Done when:** Fresh and legacy DBs expose nullable `ref_agent_data_id` on `agent_data` after `_ensure_agent_data_schema` (including bootstrap registry path); header inventory mentions the column; `python3 -m py_compile src/data/database.py` passes. No write/read behavior change yet beyond schema.

1. In `src/data/database.py` module docstring inventory, update the `agent_data` bullet to note nullable self-ref `ref_agent_data_id` (points at earliest identical content row; audit rows may omit `block_data`).

2. In `_ensure_agent_data_schema` (~line 5251):
   - Add `ref_agent_data_id TEXT` (nullable, no DEFAULT required) to the `CREATE TABLE agent_data` column list.
   - When the table **already exists**, run `PRAGMA table_info(agent_data)` and, if `ref_agent_data_id` is missing, `ALTER TABLE agent_data ADD COLUMN ref_agent_data_id TEXT` (swallow only the existing “duplicate column name” pattern used elsewhere — do not swallow other errors).
   - Keep `CREATE INDEX idx_agent_data_batch` on fresh create only (unchanged).
   - Do **not** add a foreign-key constraint (SQLite FK not used elsewhere for this table; reject bad refs in write logic).
   - Do **not** reset or clear any existing `block_data`.

3. Confirm `agent_data` remains registered in `_UPSERT_LAZY_SCHEMA_HANDLERS` so `ensure_all_upsert_registry_schemas_at_startup()` / `ensure_table_schema_for_upsert` pick up the migration (no bootstrap.py edit).

⚠️ **Decision:** Column name is exactly `ref_agent_data_id` (parent + child AC). No parallel hash column — identity is exact logical `block_data` via existing compress/decompress helpers.

---

## Stage 2: Dedupe write path (`save_agent_data`)

**Done when:** Every successful content insert creates an `agent_data` row; identical logical content sets `ref_agent_data_id` to the earliest canonical match and stores `block_data` NULL; no-match stores compressed content with `ref_agent_data_id` NULL; self-ref and non-canonical/cycle targets raise `ValueError`; `INSERT OR IGNORE` duplicate primary key still means “no new row”; compile passes.

1. Add a private helper in `src/data/database.py` next to `save_agent_data` (name: `_find_earliest_agent_data_content_match`):

   ```python
   def _find_earliest_agent_data_content_match(
       conn: sqlite3.Connection,
       plain_text: str,
   ) -> Optional[str]:
       """Return agent_data_id of earliest canonical row with identical logical block_data, or None."""
   ```

   Behavior (literal):
   - Consider only rows where `ref_agent_data_id IS NULL` and `block_data IS NOT NULL`.
   - Order by `created_at ASC`, then `agent_data_id ASC`.
   - Identity: `_decompress_payload(row.block_data) == plain_text` (plain text the caller passed in — same contract as today’s save input). Do **not** filter by `block_type`.
   - Return the first matching `agent_data_id`, or `None`.
   - Do **not** log. Do **not** truncate the candidate set for performance.

⚠️ **Decision:** Match on decompressed logical content (Code Rules: compression invisible above data; parent: identity on exact `block_data` as callers treat plain text). Blob-only SQL equality is insufficient for legacy TEXT rows `_decompress_payload` already supports.

⚠️ **Decision:** No depth/row caps on the scan — Susan forbids unauthorized limits; correctness over premature optimization.

2. Rewrite `save_agent_data` body (same signature args; **change return type** from `bool` to `Dict[str, Any]`):

   Return shape (always a dict):

   | key | meaning |
   |-----|---------|
   | `inserted` | `True` if a new row was written |
   | `outcome` | `"new_content"` \| `"ref_existing"` \| `"duplicate_id"` |
   | `agent_data_id` | the id passed in |
   | `ref_agent_data_id` | set when `outcome == "ref_existing"`, else `None` |

   Algorithm inside `_with_conn` after `_ensure_agent_data_schema(conn)`:
   1. Let `plain = block_data` (must be `str`; keep existing `BLOCK_TYPES` validation).
   2. `match_id = _find_earliest_agent_data_content_match(conn, plain)`.
   3. If `match_id == agent_data_id`: raise `ValueError("agent_data self-ref rejected: …")`.
   4. If `match_id` is not None:
      - Load that row; if its `ref_agent_data_id` is not null/empty, raise `ValueError` (non-canonical target / would create a multi-hop write).
      - Insert with `ref_agent_data_id=match_id`, `block_data=NULL`, keep `token_size` from the caller, other columns as today.
      - On successful insert: return `{inserted: True, outcome: "ref_existing", agent_data_id, ref_agent_data_id: match_id}`.
   5. Else (no match): compress via `_compress_payload(plain)`, insert with `ref_agent_data_id=NULL` and compressed blob (same as today). Return `{inserted: True, outcome: "new_content", agent_data_id, ref_agent_data_id: None}`.
   6. Preserve `INSERT OR IGNORE` semantics for primary-key collision: if no row inserted (`total_changes == 0`), return `{inserted: False, outcome: "duplicate_id", agent_data_id, ref_agent_data_id: None}` — do not update the existing row.
   7. Update the docstring to describe dedupe + return dict. Do not log.

3. Call sites that currently ignore the return value stay valid (`_store_prompt_blocks`, `_store_response_block`, feedback helper in `database.py`). Do **not** adapt call sites to treat the return as `bool`.

⚠️ **Decision:** Return a dict (not bool) so Stage 4 can log found/recorded without a second SELECT. No production caller currently depends on the bool.

---

## Stage 3: Transparent read resolution

**Done when:** `get_agent_data`, `get_agent_data_by_batch`, and `get_agent_data_for_ids` return rows whose `block_data` is the resolved plain-text content (canonical payload) whether the row stores content directly or via `ref_agent_data_id`; broken/missing refs and cycles raise `ValueError` (data raises; callers log); compile passes.

1. Add private helper `_resolve_agent_data_block_data(conn, row_dict) -> Optional[str]`:
   - If `ref_agent_data_id` is null/empty: return `_decompress_payload(row_dict["block_data"])`.
   - Else follow the ref chain: load target by `agent_data_id`, track visited ids, raise `ValueError` on cycle or missing target.
   - Terminal row must be canonical (`ref_agent_data_id` null) with content; return its decompressed `block_data`.
   - Do not log.

2. In `get_agent_data`, `get_agent_data_by_batch`, and `get_agent_data_for_ids`, after `_row_to_dict`, set `d["block_data"] = _resolve_agent_data_block_data(conn, d)` instead of bare `_decompress_payload`. Keep `ref_agent_data_id` on the returned dict so debug callers can see it.

3. Do **not** change UI routes; `api_system.get_agent_data` already goes through core → `get_agent_data_by_batch`.

⚠️ **Decision:** Resolve inside the data layer so every read path (batch, id, ids map, feedback, hydration) stays transparent without teaching core about refs.

---

## Stage 4: Debug found/recorded on touched agent paths

**Done when:** With `debug=True`, `_store_prompt_blocks` / `_store_response_block` and the `do_task` hydration read that uses `get_agent_data_for_ids` emit §1.5.1 index/detail lines showing match-vs-new and ids recorded/resolved; with `debug=False`, no new debug-contract lines from these edits; data layer still has zero logging; compile passes.

1. Extend `_store_prompt_blocks` and `_store_response_block` with `debug: bool = False`.
2. From `do_task`, pass `debug=debug` into those store helpers wherever they are invoked for persistence.
3. After each `save_agent_data(...)` call in those helpers, when `debug=True`:
   - `dbg = get_logger(__name__, debug_flag=True)`
   - One `debug_index` (or `debug_detail` under an existing index if already inside a `do_task` index header) with outcome from the return dict: `new_content` vs `ref_existing` vs `duplicate_id`, plus `agent_data_id` and `ref_agent_data_id`.
   - Use `truncate_debug_content` if any payload excerpt is logged (prefer ids/outcome only — no full prompt dump required).
4. On the mid-chain hydration path that calls `get_agent_data_for_ids` (~line 644), when `debug=True`, for each requested id emit a detail line: resolved vs direct (`ref_agent_data_id` present/absent) and the id used. Do not add debug requirements to UI.
5. Do **not** add logging inside `src/data/database.py`.

⚠️ **Decision:** Debug lives in `agent.py` (caller logs) using the Stage 2 return dict + resolved row fields — satisfies “data raises; callers log” and AC debug trail without contaminating the data layer.

---

## Stage 5: Code Rules mention

**Done when:** The Data-layer bullet in `docs/ASTRAL_CODE_RULES.md` that documents `agent_data` compression also states that nullable `ref_agent_data_id` is followed on read so callers still receive plain text; no other rules churn.

1. Locate the sentence: *`agent_data.block_data` is zlib-compressed on write and decompressed on read — this is handled transparently by `save_agent_data` / `get_agent_data_by_batch`…*
2. Extend it (same paragraph) to say writes may store `ref_agent_data_id` to the earliest identical content row and omit duplicate payload; reads resolve the ref before returning plain text (`get_agent_data`, `get_agent_data_by_batch`, `get_agent_data_for_ids`).

---

## Self-Assessment

**Scope:** `Single-Component` — primarily `database.py` agent_data schema/write/read plus thin `agent.py` debug/passthrough; one Code Rules sentence.

**Conf:** `high` — pattern is specified by parent AC; compression helpers and `_ensure_*` migration patterns already exist; call sites already ignore `save_agent_data`’s return.

**Risk:** `Medium` — wrong match/resolve would corrupt what callers treat as prompt/response text across roster/consult/intake hydration; mitigated by exact plain-text match, canonical-only refs, and cycle checks.

## Rules self-review

- **§1.3 DRY:** Single match helper + single resolve helper; all three getters use resolve.
- **§1.5 / data-raises-caller-logs:** No logging in `database.py`; `ValueError` on self-ref/cycle/missing ref; debug only in `agent.py` behind `debug=True`.
- **§1.5.1:** Index/detail helpers only; no new `[DEBUG]` INFO; quiet when `debug=False`.
- **§2.1:** No new config keys (none required).
- **§3.3:** No new cross-layer imports; UI still does not touch data.
- **§3.5:** Column/helper names match parent vocabulary (`ref_agent_data_id`).
- **Compression contract preserved:** Callers still pass/receive plain text; omit payload only on audit rows with refs.
)

## Review (build stub)

**Built:** `origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read` @ `6dcfc6a`

**Stages delivered:**
- Stage 1: `ref_agent_data_id` schema + inventory — `baa8f4a`
- Stage 2: `save_agent_data` dedupe write (return dict) — `3194770`
- Stage 3: transparent read resolve on getters — `30e16c0`
- Stage 2 follow-up: exclude write id from match (PK retry) — `b51b137`
- Stage 4: `agent.py` debug found/recorded on write/hydration read — `a2d70db`
- Stage 5: Code Rules data-layer sentence — this commit

**Betty:** manifest at **Code Complete** — schema ensure column; write match/ref/omit; read resolve by id/batch/ids; self-ref/cycle raise; debug quiet when `debug=False`.
