# AST-1878 — Agent model field + per-platform candidate keys

- **Parent:** [AST-1851 — Support OpenRouter API models for agent work](https://linear.app/astralcareermatch/issue/AST-1851)
- **Ticket:** [AST-1878](https://linear.app/astralcareermatch/issue/AST-1878)
- **Publish ref:** `origin/sub/AST-1851/AST-1878-agent-model-per-platform-keys`
- **Canon Scope:** new pattern *Model → server catalog routing* (defined on AST-1851 § Architectural definition). No statute ids are cited for this child.

This ticket is the data layer of *Model → server catalog routing*. Each `agent` row gets a `model_id` column that holds an `LLM_MODEL_CONFIG` key (from AST-1877), and every agent write checks the brain size against that model's own sizes. Candidates get a new `candidate_key` table with one Fernet-encrypted key per server. `get_candidate` returns those keys as a `candidate_api_keys` map (`{server_id: plaintext}`) and no longer returns the legacy single `candidate_api_key`. No save path writes that legacy column any more. The repo seed names a model for every agent and adds a separate contact-Estelle agent, and `contact_estelle_turn` now points at it. `run_session_resume_parse` requires a candidate id and puts that candidate's key map into its synthetic ctx, without binding or persisting anything. `database.py` also stops importing the legacy provider symbols that #4 (AST-1880) deletes from `config.py`, because #4 cannot edit `database.py`. Call routing is #3 (AST-1879). Admin routes and UI are #4 (AST-1880).

## Scope gate

Every row in **Files Changed** is named in this ticket's `## Scope`, and every stage is the kind of change that Scope describes for that file.

- `src/utils/config.py`: **only** the `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` edit (AST-1883 exception). No other `config.py` line changes.
- The backfill is Scope's "backfill switches to `calculate_cost_components_from_counts`". Stage 3's rename and generalization is how that switch is carried out (see the ⚠️ Decision there).
- The `hard_delete_candidate` / legacy-migration cascade rows for `candidate_key` are part of the new candidate key table's lifecycle in `database.py` (see the ⚠️ Decision in Stage 2).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `"model_id"` to `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` | utils |
| `src/data/database.py` | `agent.model_id` column, per-model brain validation on save/update/repo-JSON apply, catalog-backed `_expose_agent_public`. New `candidate_key` table with set/clear/list helpers. `get_candidate` key map, legacy key dark, `save_candidate` loses `candidate_api_key`. Cascade on hard delete. Timesheet SKU/server validation. Backfill on `calculate_cost_components_from_counts`. Legacy provider imports removed. Header inventory. | data |
| `src/core/candidate.py` | `set_candidate_api_key(candidate_id, server_id, api_key)` (new). `clear_candidate_api_key(candidate_id, server_id)` (modified). `run_session_resume_parse(..., candidate_id=...)` | core |
| `data/admin/agent.json` | `model_id` on every row. New `contact_recruiter_estelle` row | data |
| `data/admin/agent_task.json` | `contact_estelle_turn` → `agent_id: "contact_recruiter_estelle"` | data |

No other file is touched. No `tests/` or bible edits. Betty owns those; see **Tests expected to move** below.

---

## Stage 1: Agent model field, per-model brain validation, seed

**Done when:** `agent` has a `model_id` column. `save_agent` / `update_agent` / Revert-to-file reject a brain size the model lacks. `data/admin/agent.json` round-trips through the repo-JSON validator with a catalog model on every row. `contact_estelle_turn` names `contact_recruiter_estelle`. `database.py` no longer imports `get_active_llm_provider`, `resolve_brain_setting_to_anthropic_agent_key`, `resolve_brain_setting_to_deepseek_tier_meta`, or `validate_allowed_brain_setting`.

1. **`src/utils/config.py`**: in `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]`, insert `"model_id",` between `"content",` and `"brain_setting",`. The tuple becomes `("agent_id", "content", "model_id", "brain_setting", "temperature", "max_tokens", "updated_at")`. Change nothing else in `config.py`.

2. **`src/data/database.py` imports** (the `from src.utils.config import (...)` block):
   - Remove `get_active_llm_provider`, `resolve_brain_setting_to_anthropic_agent_key`, `resolve_brain_setting_to_deepseek_tier_meta`, and `validate_allowed_brain_setting`.
   - Add `BRAIN_SETTINGS`, `resolve_model_brain`, and `validate_brain_setting_for_model`.
   - Keep `infer_brain_setting_from_legacy_model_code` (still used by `_coerce_agent_brain_setting`) and `AGENT_CONFIG` (untouched).

3. **`_expose_agent_public`** (near line 138): replace the body after `out["brain_setting"] = bs` so that the public `model_code` / `resolved_model_key` come from the row's own model:

   ```python
   def _expose_agent_public(row_dict: Dict[str, Any]) -> Dict[str, Any]:
       """brain_setting authoritative; model_code JSON key mirrors the catalog SKU for admin UI (None without model_id)."""
       out = dict(row_dict)
       bs = _coerce_agent_brain_setting(out)
       out["brain_setting"] = bs
       mid = out.get("model_id")
       # Legacy rows written before Revert-to-file carry no model yet.
       rk = resolve_model_brain(mid, bs)["sku"] if mid else None
       out["resolved_model_key"] = rk
       out["model_code"] = rk
       return out
   ```

4. **New helper** directly below `_expose_agent_public`:

   ```python
   def _validate_agent_model_brain(model_id: Optional[str], brain_setting: str) -> None:
       """Per-model brain check; model-less writes (admin routes until AST-1880) use the global tiers."""
       if model_id:
           validate_brain_setting_for_model(model_id, brain_setting)
       elif brain_setting not in BRAIN_SETTINGS:
           raise ValueError(f"Invalid brain_setting {brain_setting!r}. Allowed: {list(BRAIN_SETTINGS)}")
   ```

   ⚠️ **Decision:** `model_id` stays optional on `save_agent` / `update_agent` on this branch. Today's `api_admin` create/update routes (#4's file) send no model. Requiring one would break Manage Agents create on `sub/*` and `ftr` until #4 lands. When a model is present, the check is strictly per-model. An unknown `model_id` raises through `get_llm_model`. Repo JSON (step 8) **requires** `model_id` on every row.

5. **`_ensure_agent_schema`**: add `model_id TEXT,` to the `CREATE TABLE agent` column list, directly after `content TEXT,`. Add `("model_id", "TEXT"),` as the first tuple in the `ALTER TABLE ... ADD COLUMN` migration list. Do not backfill content (AST-1497 DDL-only rule stays). Leave the `model_code` column as is: it stays legacy and unwritten, and `model_id` is the one column that holds the catalog model id.

6. **`save_agent`**: add keyword `model_id: Optional[str] = None` after `brain_setting`. Update the docstring to: `"""Upsert an agent row; new rows require brain_setting; model_id (catalog key) validated with it (model_code column is legacy, not written)."""`. At the top of `save_agent`, normalize it: `mid = model_id.strip() if model_id is not None else None`, and `if mid == "": raise ValueError("model_id must be non-empty when provided")`.
   - Change the existing-row lookup to `SELECT agent_id, model_id, brain_setting FROM agent WHERE agent_id = ?`.
   - **Insert branch:** keep the "requires brain_setting" error. Replace `validate_allowed_brain_setting(...)` with `_validate_agent_model_brain(mid, str(brain_setting).strip())`. Insert `model_id` as a column: `INSERT INTO agent (agent_id, content, model_id, brain_setting, temperature, max_tokens, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)` with `mid` in the third position.
   - **Update branch:** if `mid is not None or brain_setting is not None`, compute `eff_mid = mid if mid is not None else existing["model_id"]` and `eff_bs = str(brain_setting).strip() if brain_setting is not None else (existing["brain_setting"] or "")`, then call `_validate_agent_model_brain(eff_mid, eff_bs)`. Remove the old `validate_allowed_brain_setting` call. Append `"model_id = ?"` / `mid` to `sets` / `params` when `mid is not None`, before the existing `brain_setting` append.

7. **`update_agent`**: `_UPDATE_AGENT_ALLOWED = frozenset({"content", "model_id", "brain_setting", "temperature", "max_tokens"})`. Inside `_with_conn`, after `_ensure_agent_schema(conn)` and before the `UPDATE`, when `"model_id" in cols or "brain_setting" in cols`:
   - Read `SELECT model_id, brain_setting FROM agent WHERE agent_id = ?`. If there is no row, `return 0`.
   - Compute `eff_mid` = `kwargs["model_id"]` if passed, else the row's `model_id`. Compute `eff_bs` the same way from `brain_setting`.
   - A passed `model_id` that is `None` or blank after `.strip()` → `raise ValueError("model_id must be non-empty when provided")`.
   - Call `_validate_agent_model_brain(eff_mid, str(eff_bs or "").strip())`.

   Changing only the model therefore re-checks the stored brain size against the new model.

8. **Repo JSON**:
   - `_validate_agent_repo_json_rows`: after the `brain_setting required` check, add:

     ```python
     mid = row.get("model_id")
     if mid is None or not str(mid).strip():
         raise ValueError(f"agent repo JSON row {i}: model_id required")
     try:
         validate_brain_setting_for_model(str(mid).strip(), str(bs).strip())
     except ValueError as e:
         raise ValueError(f"agent repo JSON row {i}: {e}") from e
     ```

     This keeps validation before any write, as today.
   - `apply_agent_repo_json_startup`: delete the `validate_allowed_brain_setting(bs)` line, because the validator above already checked the pair. Add `mid = str(row["model_id"]).strip()`. The INSERT becomes `INSERT INTO agent (agent_id, content, model_id, brain_setting, temperature, max_tokens, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)` with `(aid, content, mid, bs, temp, max_t, updated)`. The UPDATE becomes `UPDATE agent SET content = ?, model_id = ?, brain_setting = ?, temperature = ?, max_tokens = ?, updated_at = ? WHERE agent_id = ?` with `(content, mid, bs, temp, max_t, updated, aid)`.
   - `fetch_agent_repo_json_export_rows` needs no edit because it reads the config columns.

9. **`list_agents`**: in the SELECT column list, change `model_code, brain_setting,` to `model_code, model_id, brain_setting,`. Update the docstring to `"""Return all agents including model_id / brain_setting / resolved_model_key plus UI-compat model_code."""`. `get_agent` uses `SELECT *` and needs no edit.

10. **Header inventory** (module docstring `agent` line): replace it with
    `- agent    — Agent: agent_id TEXT PK, content TEXT, model_id TEXT (LLM_MODEL_CONFIG key; brain_setting validated against that model's sizes — AST-1878), model_code TEXT (legacy/unwritten), brain_setting TEXT (Little|Medium|Big), temperature REAL, max_tokens INTEGER, updated_at TIMESTAMP.`

11. **`data/admin/agent.json`**: agent.json round-trips byte-identical through `json.dumps(..., indent=2, ensure_ascii=False) + "\n"` (verified at plan time). Edit it with this one-off from the worktree root. Do not commit the snippet.

    ```python
    import json
    p = "data/admin/agent.json"
    rows = json.load(open(p, encoding="utf-8"))
    model = {
        "ats_expert_atlas": "deepseek-v4", "college_intern_ruth": "deepseek-v4",
        "content_writer_judith": "kimi-k2.6", "job_analyst_grace": "deepseek-v4",
        "principal_recruiter_estelle": "kimi-k2.6", "web_scraper_laslo": "deepseek-v4",
    }
    def with_model(r, mid):
        # model_id sits between content and brain_setting (config column order).
        return {k: v for k, v in [("agent_id", r["agent_id"]), ("content", r["content"]), ("model_id", mid),
                                  ("brain_setting", r["brain_setting"]), ("temperature", r["temperature"]),
                                  ("max_tokens", r["max_tokens"]), ("updated_at", r["updated_at"])]}
    out = [with_model(r, model[r["agent_id"]]) for r in rows]
    est = next(r for r in rows if r["agent_id"] == "principal_recruiter_estelle")
    out.append({"agent_id": "contact_recruiter_estelle", "content": est["content"], "model_id": "kimi-k2.6",
                "brain_setting": "Little", "temperature": None, "max_tokens": None,
                "updated_at": "2026-09-29 00:00:00"})
    out.sort(key=lambda r: r["agent_id"])
    open(p, "w", encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    ```

    Brain sizes are unchanged from today: Atlas Big, Ruth Little, Grace Medium, Laslo Medium, Estelle Big, Judith Big. The new row sorts between `college_intern_ruth` and `content_writer_judith`, which matches export order (`ORDER BY agent_id`).

    ⚠️ **Decision (contact-Estelle id):** `contact_recruiter_estelle` follows the `<role>_<name>` convention of the other rows.
    ⚠️ **Decision (contact-Estelle temperature/max_tokens):** `null`, so the Kimi K2.6 Little catalog defaults apply (`default_temperature` 0.6, `default_max_tokens` 16000). Copying the analysis row's `max_tokens: 384000` would carry a DeepSeek-era AST-1391 floor onto a Kimi model. Scope only says to copy *content*.

12. **`data/admin/agent_task.json`**: this file does **not** round-trip through `json.dumps` (verified), so use a text edit. Line 763 is `"agent_id": "principal_recruiter_estelle",` inside the object whose `"task_key": "contact_estelle_turn"` (line 774, `task_key_uuid` `59eb6a1d-0988-414b-8a10-34375eba03e3`). Change that one line to `"agent_id": "contact_recruiter_estelle",`. No other field changes: `task_key_uuid` and `updated_at` stay, and `agent_id` is not a versioned prompt segment.

**Stage 1 check** (worktree root):

```bash
python3 -m py_compile src/utils/config.py src/data/database.py
python3 -c "
import json
from src.utils.config import LLM_MODEL_CONFIG as M
for r in json.load(open('data/admin/agent.json')):
    if r.get('model_id') not in M or r['brain_setting'] not in M[r['model_id']]['brain_sizes']: print(r['agent_id'])"
python3 -c "
import json, sqlite3; import src.data.database as db
c = sqlite3.connect(':memory:'); c.row_factory = sqlite3.Row
db._agent_schema_ensured = False
db.apply_agent_repo_json_startup(c, json.load(open('data/admin/agent.json')))
print(sorted(tuple(r) for r in c.execute('SELECT agent_id, model_id, brain_setting FROM agent')))"
rg -n "get_active_llm_provider|resolve_brain_setting_to_|validate_allowed_brain_setting" src/data/database.py
git diff --stat data/admin/
```

The second command prints nothing (parent AC 3). The third prints seven rows with the AC 4 values. The `rg` returns nothing. `git diff --stat` shows `agent_task.json` as 1 line changed.

---

## Stage 2: Per-server candidate keys; legacy key goes dark

**Done when:** `set_candidate_server_key` twice on one candidate (two servers) leaves two `candidate_key` rows, both ciphertext. `get_candidate` returns `candidate_api_keys` with both plaintexts and has **no** `candidate_api_key` key. `save_candidate` has no `candidate_api_key` parameter. Nothing in `database.py` writes `candidate.candidate_api_key`. `run_session_resume_parse` without a candidate id returns 400 before any ledger row or `do_task` call.

1. **`src/data/database.py` imports**: add `get_llm_server` to the config import block.

2. **New table + helpers**: place them directly **above** `def get_candidate(` (replacing `clear_candidate_api_key`, which step 5 deletes):

   ```python
   # -- candidate_key: one Fernet-encrypted API key per (candidate, LLM server) (AST-1878) --

   def _ensure_candidate_key_table(conn: sqlite3.Connection) -> None:
       # No module flag: test/DB swaps reuse the process, so re-check every call (CREATE IF NOT EXISTS is cheap).
       conn.execute("""
           CREATE TABLE IF NOT EXISTS candidate_key (
               candidate_id TEXT NOT NULL,
               server_id TEXT NOT NULL,
               api_key TEXT NOT NULL,
               created_at TIMESTAMP NOT NULL,
               updated_at TIMESTAMP NOT NULL,
               PRIMARY KEY (candidate_id, server_id)
           )
       """)


   def _candidate_key_map(conn: sqlite3.Connection, candidate_id: str) -> Dict[str, str]:
       """server_id → plaintext key; undecryptable rows are omitted (treated as not set)."""
       _ensure_candidate_key_table(conn)
       out: Dict[str, str] = {}
       for r in conn.execute(
           "SELECT server_id, api_key FROM candidate_key WHERE candidate_id = ? ORDER BY server_id",
           (candidate_id,),
       ).fetchall():
           try:
               out[r["server_id"]] = decrypt_value(r["api_key"])
           except (RuntimeError, ValueError):
               continue
       return out


   def set_candidate_server_key(candidate_id: str, server_id: str, api_key: str) -> None:
       """Upsert this candidate's key for one catalog server (Fernet-encrypted). Raises on unknown server / blank key."""
       cid = str(candidate_id or "").strip()
       if not cid:
           raise ValueError("candidate_id is required")
       get_llm_server(server_id)
       key = str(api_key or "").strip()
       if not key:
           raise ValueError("api_key is required (use clear_candidate_server_key to remove)")
       ciphertext = encrypt_value(key)
       now = _utc_now()

       def _with_conn() -> None:
           conn = _get_connection()
           try:
               _ensure_candidate_schema(conn)
               if conn.execute(
                   "SELECT 1 FROM candidate WHERE astral_candidate_id = ?", (cid,)
               ).fetchone() is None:
                   raise LookupError(f"Candidate not found: {cid}")
               _ensure_candidate_key_table(conn)
               conn.execute(
                   """INSERT INTO candidate_key (candidate_id, server_id, api_key, created_at, updated_at)
                      VALUES (?, ?, ?, ?, ?)
                      ON CONFLICT(candidate_id, server_id)
                      DO UPDATE SET api_key = excluded.api_key, updated_at = excluded.updated_at""",
                   (cid, server_id, ciphertext, now, now),
               )
               conn.commit()
           finally:
               conn.close()

       _run_with_retry(_with_conn)


   def clear_candidate_server_key(candidate_id: str, server_id: str) -> bool:
       """Delete this candidate's key for one catalog server. Returns True when a row was removed."""
       get_llm_server(server_id)

       def _with_conn() -> bool:
           conn = _get_connection()
           try:
               _ensure_candidate_key_table(conn)
               cur = conn.execute(
                   "DELETE FROM candidate_key WHERE candidate_id = ? AND server_id = ?",
                   (candidate_id, server_id),
               )
               conn.commit()
               return cur.rowcount > 0
           finally:
               conn.close()

       return _run_with_retry(_with_conn)


   def list_candidate_server_keys(candidate_id: str) -> Tuple[str, ...]:
       """Server ids this candidate holds a key for (no plaintext) — admin set/not-set."""
       def _with_conn() -> Tuple[str, ...]:
           conn = _get_connection()
           try:
               _ensure_candidate_key_table(conn)
               return tuple(r["server_id"] for r in conn.execute(
                   "SELECT server_id FROM candidate_key WHERE candidate_id = ? ORDER BY server_id",
                   (candidate_id,),
               ).fetchall())
           finally:
               conn.close()

       return _run_with_retry(_with_conn)
   ```

   ⚠️ **Decision (list returns ids, not plaintext):** the list helper is for set/not-set displays (#4). Plaintext only leaves the data layer through `get_candidate`'s `candidate_api_keys`, which is what #3's key selection reads.
   ⚠️ **Decision (no schema flag):** `tests/component/data/conftest.py` resets a fixed list of `_*_schema_ensured` flags. A new flag would leave the table missing after a test DB swap. `CREATE TABLE IF NOT EXISTS` on every call avoids that.
   ⚠️ **Decision (ON CONFLICT upsert):** SQLite here is 3.46.1. Upsert syntax needs ≥ 3.24.

3. **`_parse_candidate_row`**: delete the `if d.get("candidate_api_key"): ... decrypt ...` block (4 lines + `try/except`). In its place put `d.pop("candidate_api_key", None)` with the comment `# Legacy single key is never exposed (AST-1878); per-server keys hydrate in get_candidate.` This covers `list_candidates` as well.

4. **`get_candidate`**: in `_with_conn`, replace `return _parse_candidate_row(_row_to_dict(row)) if row else None` with:

   ```python
   if not row:
       return None
   d = _parse_candidate_row(_row_to_dict(row))
   d["candidate_api_keys"] = _candidate_key_map(conn, candidate_id)
   return d
   ```

   Update the docstring to `"""Select single candidate by astral_candidate_id. Returns parsed dict (with candidate_api_keys server → key map) or None."""`.

5. **Legacy writes removed**:
   - `save_candidate`: delete the `candidate_api_key: Optional[str] = None,` parameter, the `candidate_api_key: if provided, ...` docstring line, and the `encrypted_key = ...` line. In the INSERT, drop `candidate_api_key` from the column list and its `encrypted_key` value, which leaves 11 columns / 11 `?`. In the UPDATE branch, delete the `if encrypted_key is not None:` block.
   - Delete `def clear_candidate_api_key` entirely (database layer).
   - Leave the `candidate_api_key TEXT` column in `_ensure_candidate_schema`'s CREATE / ALTER lists as is.

   ⚠️ **Decision:** the legacy column stays in DDL (no destructive migration). It is no longer read or written, per parent functional scope 5 ("no migration of the old single key").

6. **Cascade on hard delete** (`hard_delete_candidate`): add `"candidate_key": 0,` to the `counts` dict (before `"candidate": 0`). Add `("candidate_key", "DELETE FROM candidate_key WHERE candidate_id = ?"),` to the `for table, sql in (...)` tuple after the `rubric_vector` row. In the phase-A inline cascade of `_legacy_candidate_migrate_conn` (the `for sql in (...)` tuple before `DELETE FROM candidate WHERE astral_candidate_id = ?`, ~line 3272), add `"DELETE FROM candidate_key WHERE candidate_id = ?",` after the `rubric_vector` line. Both loops already swallow `sqlite3.OperationalError` when the table is absent.

   ⚠️ **Decision:** candidate ids are lowercase last names, so a re-created candidate would otherwise inherit a deleted person's API keys.

7. **Header inventory**: replace the `candidate` line's `candidate_api_key TEXT (Fernet-encrypted Anthropic key)` with `candidate_api_key TEXT (legacy — not read or written since AST-1878)`. Add a new line directly after the `candidate` line:
   `- candidate_key — Per-server candidate API keys (AST-1878): candidate_id, server_id (LLM_SERVER_CONFIG key), api_key (Fernet ciphertext), created_at, updated_at; PRIMARY KEY (candidate_id, server_id). set/clear/list_candidate_server_key(s); get_candidate hydrates candidate_api_keys {server_id: plaintext}; cascade-deleted with the candidate.`

8. **`src/core/candidate.py` wrappers** (at `save_candidate_admin` / `clear_candidate_api_key`, ~line 3514):
   - `save_candidate_admin`: change only the docstring to `"""Direct candidate row updates from admin API (state override, etc.). API keys: set_candidate_api_key."""`.
   - Replace `clear_candidate_api_key` and add its setter:

     ```python
     def set_candidate_api_key(candidate_id: str, server_id: str, api_key: str) -> None:
         """Store this candidate's key for one catalog server (admin)."""
         database.set_candidate_server_key(candidate_id, server_id, api_key)


     def clear_candidate_api_key(candidate_id: str, server_id: str) -> bool:
         """Remove this candidate's key for one catalog server (admin). True when a key was removed."""
         return database.clear_candidate_server_key(candidate_id, server_id)
     ```

   ⚠️ **Decision:** `clear_candidate_api_key` keeps its name because `src/ui/api/api_candidate.py` (#4) imports it at module load. Renaming it would make the candidate blueprint fail to import. Its old one-argument call and `save_candidate_admin(..., candidate_api_key=...)` in that route fail at call time until #4 rewires the PATCH. See **Transitional gaps**.

9. **`run_session_resume_parse`**:
   - New signature: `def run_session_resume_parse(resume_text: str, *, candidate_id: Optional[str] = None, debug: bool = False) -> Tuple[Dict[str, Any], int]:`.
   - New docstring: `"""Parse pasted resume text via simple_resume_parse (Ruth / Little) on the selected candidate's API keys; no candidate bind/persist.\n\n    Returns (json_body, http_status) for Admin session-resume paste (AST-986 / AST-1038 / AST-1878).\n    """`
   - After the existing `resume_text is required` 400 check, insert:

     ```python
     cid = (candidate_id or "").strip()
     if not cid:
         return ({"success": False, "error": "candidate_id is required"}, 400)
     cand = database.get_candidate(cid)
     if not cand:
         return ({"success": False, "error": f"Candidate not found: {cid}"}, 404)
     ```

   - In the synthetic `ctx` literal, add `"candidate_api_keys": dict(cand.get("candidate_api_keys") or {}),` after the `candidate_data` entry. Change the comment above `ctx` to `# Synthetic token ctx + the selected candidate's key map only — no astral_candidate_id (no bind/persist).` Nothing else in the function changes: no write to the candidate row, and the `"session"` ledger sentinel stays.

   ⚠️ **Decision:** `candidate_id` is keyword-with-default rather than required, so today's `api_admin` route (#4 passes the id) gets a clean 400 instead of a `TypeError` 500 until #4 lands.

**Stage 2 check** (worktree root):

```bash
python3 -m py_compile src/data/database.py src/core/candidate.py
rg -n "candidate_api_key" src/data/database.py
python3 -c "import src.data.database, src.core.candidate; from src.core.candidate import clear_candidate_api_key, set_candidate_api_key, save_candidate_admin"
```

The `rg` hits only the header line, `_parse_candidate_row`'s `pop`, the comment, and `_ensure_candidate_schema`'s DDL/ALTER entries. None of them is an `UPDATE`/`INSERT` that writes it. The import line must succeed. It covers the three names `api_candidate.py` imports from core. The blueprints themselves can't be imported locally because `asyncpg` isn't installed, so the test suite covers them.

---

## Stage 3: Timesheet validation + backfill on catalog pricing

**Done when:** `_add_timesheet_entry` rejects a SKU that is not priced on the given server. The backfill recomputes one server's rows via `calculate_cost_components_from_counts`. `rg -n -i "deepseek" src/data/database.py` returns nothing.

1. **Imports**:
   - Config block: remove `DEEPSEEK_MODEL_PRICING`, add `LLM_MODEL_CONFIG` and `get_sku_pricing`.
   - Replace `from src.utils.cost_calculator import calculate_cost_components_deepseek_from_counts` with `from src.utils.cost_calculator import calculate_cost_components_from_counts`.

2. **`_add_timesheet_entry`**: directly after the existing `provider not in ALLOWED_TIMESHEET_PROVIDERS` raise, add:

   ```python
   if model_code:
       # Ledger row must name a SKU the catalog prices on this server (raises ValueError otherwise).
       get_sku_pricing(model_code, provider)
   ```

   Every current writer passes a catalog SKU with its server: `anthropic.py` passes alias keys under `anthropic`, `deepseek.py` passes `deepseek-v4-*` under `deepseek`, and `llm_compat.py` passes `sku` under `server_id`. All five existing `_add_timesheet_entry` test calls use catalog SKUs, checked at plan time.

3. **Backfill**: replace `backfill_deepseek_agent_timesheet_costs` with:

   ```python
   def backfill_agent_timesheet_costs(server_id: str) -> int:
       """Recompute calc_cost_* from stored token counts for agent_timesheets rows priced on one catalog server."""
       get_llm_server(server_id)
       model_codes = tuple(sorted({
           sku for m in LLM_MODEL_CONFIG.values() if m["server"] == server_id for sku in m["pricing"]
       }))
       if not model_codes:
           return 0
       placeholders = ",".join("?" for _ in model_codes)
   ```

   Keep the rest of the body unchanged except the cost call, which becomes:

   ```python
   parts = calculate_cost_components_from_counts(
       row["cache_read_tokens"],
       row["total_no_cache_input_tokens"],
       row["total_output_tokens"],
       row["cache_write_tokens"],
       sku=row["model_code"],
       server_id=server_id,
   )
   ```

   ⚠️ **Decision (rename + `server_id` argument):** #4 deletes `DEEPSEEK_MODEL_PRICING` and the DeepSeek cost wrappers from files it owns, and no later child owns `database.py`. The backfill therefore has to source SKUs from the catalog now, and parent AC 2 (`rg -i deepseek src/` outside `config.py`) needs the vendor name out of the function name. The only caller is `tests/component/data/database/test_timesheets.py`. `backfill_agent_timesheet_costs("deepseek")` gives the same result for that test's rows. Scoping by server keeps Anthropic history from being repriced.

**Stage 3 check** (worktree root):

```bash
python3 -m py_compile src/data/database.py
rg -n -i "kimi|moonshot|openrouter|deepseek" src/data/database.py src/core/candidate.py
python3 -c "import src.data.database, src.core.candidate"
```

The `rg` returns nothing. The imports succeed.

---

## Compile / lint (every stage)

`python3 -m py_compile` on every `.py` file changed in the stage (build-child §7; no linter is configured), then that stage's import check. Both must pass before each `code()` commit.

## Tests expected to move (Betty — qa-child; engineer does not edit `tests/`)

- `tests/component/core/test_candidate.py`: `test_save_candidate_admin_and_clear_api_key` (the clear wrapper takes `server_id` and the database function is renamed). `run_session_resume_parse(...)` cases need `candidate_id=` and a stubbed `database.get_candidate`.
- `tests/component/data/database/test_timesheets.py`: import and call `backfill_agent_timesheet_costs("deepseek")`.
- `tests/component/data/database/test_agents.py`, `tests/component/core/test_repo_admin_json.py`, `tests/component/ui/api/test_api_admin.py`: fixtures and assertions for agent repo-JSON rows (now need `model_id`) and for `resolved_model_key` / `model_code` (now the row's catalog SKU, or `None` without `model_id`).
- New coverage for ticket AC 3/4 (seed one-liner), AC 5 (`get_candidate` has `candidate_api_keys` and no `candidate_api_key`), and parent AC 6's storage half (two ciphertext rows).

## Transitional gaps (by design of the layer split; closed by #3 / #4)

Between this child and #3/#4, on `sub/*` and `ftr` only (UAT runs after all four land):

- `dispatcher.py` skip gate, `agent.py` key override, and `meteorite.py` ctx hand-off read `candidate_api_key`, which is now absent. Candidate-key tasks skip or run without a candidate key until #3 reads `candidate_api_keys`.
- `api_candidate.py`: `has_api_key` reads false, and PATCH `api_key` fails at call time. `api_admin.py`: the dispatch Run/Auto key gate reports the key missing, and session paste returns 400 without `candidate_id`. All of this until #4.

## Hand-off notes for #3 / #4

- Key map contract: `get_candidate(cid)["candidate_api_keys"]` is `{server_id: plaintext}`. It holds only servers with a decryptable key.
- Admin set/not-set: `database.list_candidate_server_keys(cid)` returns server ids. Core writes go through `set_candidate_api_key(cid, server_id, key)` / `clear_candidate_api_key(cid, server_id)`.
- Agent writes accept `model_id=` on `save_agent` and `update_agent`. Passing it makes the brain check per-model.
- Observation (not changed here): `principal_recruiter_estelle` keeps `max_tokens: 384000` from its DeepSeek era while moving to Kimi K2.6 Big. #3's call path should make sure the value the server receives is one Kimi accepts.

## Estimate

Confirm Chuckles estimate: 5 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-1878
**Overall:** APPROVED
**Corpus:** `e1f2699fad`
**Publish ref:** `0f6eee2f7`

## Canon scores

Model → server catalog routing | A | | Stages 1–3: model_id + per-model brain checks, server-scoped keys, catalog SKU timesheet validation, seed/task wiring

## Traceability

3→S1 (repo JSON + `agent.json` + in-memory apply check) | 4→S1 step 11–12 (seed models/sizes + `contact_recruiter_estelle` + task agent) | 5→S2 (`candidate_api_keys`, legacy column dark, `save_candidate` / `_parse_candidate_row`) + **Tests expected to move** (Betty AC 5) | parent 6-partial→S2 (two-server `candidate_key` storage; Betty lists coverage) | parent 11-partial→S1 step 12 (`contact_estelle_turn` agent) | parent 16-partial→S2 step 9 (`run_session_resume_parse` candidate_id + key map; HTTP/route #4) | parent 5,7–10,12–15→N/A (#3/#4 or epic-only)

## Findings

### acceptable

- **Severity:** acceptable
- **Location:** Linear assignee vs validate-plan §1
- **Finding:** Ticket assignee is still Hedy at Plan Ready; this pass was user-requested Joan validation only.
- **Recommendation:** Chuckles restores implementer after posting upshot (normal handoff).

- **Severity:** acceptable
- **Location:** Scope gate / AST-1883
- **Finding:** Repo-admin `model_id` column-only `config.py` edit and backfill switch to `calculate_cost_components_from_counts` (with rename/generalization in Stage 3) match approved Scope moves.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** **Transitional gaps** / **Hand-off notes**
- **Finding:** Layer split knowingly leaves `candidate_api_key` consumers red on `sub/*` until #3/#4; plan documents gaps and contracts for `candidate_api_keys`, server-scoped set/clear, and optional `model_id` on agent writes until admin routes land.
- **Recommendation:** None — faithful to parent partition.

- **Severity:** acceptable
- **Location:** Stage 1 step 4 / Hand-off note
- **Finding:** Analysis Estelle keeps `max_tokens: 384000` on Kimi K2.6 Big while contact row uses catalog null defaults; plan flags #3 call-path risk without changing seed beyond Scope.
- **Recommendation:** None at plan stage.

### discuss

- **Severity:** discuss
- **Location:** Child ticket **Acceptance criteria** vs plan Stage 2 + **Tests expected to move**
- **Finding:** Parent AC 6 (two platform keys on one candidate) is implemented in Stage 2 but not copied into the child ticket’s three AC bullets; verification is delegated to qa-child explicitly.
- **Recommendation:** Optional Linear AC addendum citing parent AC 6 storage half so UAT traceability matches the plan (not blocking build).

context_tokens≈115000

[plan-rubric] PROCEED (Commit: 0f6eee2f7) Data layer keys plan clean

## Review

- **Branch:** `origin/sub/AST-1851/AST-1878-agent-model-per-platform-keys`
- **Build tip:** `be5917353` (stages: `af2895717` agent `model_id` + per-model brain validation + seed · `31046806a` `candidate_key` + key map + legacy key dark + session paste candidate · `be5917353` timesheet SKU/server validation + backfill on catalog pricing)
- **Build notes:** Built as planned, no deviations. `agent_task.json` line 763 was changed with a line-scoped `sed`, because the editor tool can't read that file; the diff is exactly one line. Smoke-tested against temp SQLite DBs: repo-JSON apply of the seed (seven rows, AC 4 values); per-model brain rejects on save/update; two `candidate_key` ciphertext rows and upsert; `get_candidate` map with no `candidate_api_key`; hard-delete cascade count; `run_session_resume_parse` 400 without a candidate and 404 for an unknown one; timesheet SKU/server reject; backfill by server. `src/ui/api/*` can't be import-tested locally (`asyncpg` not installed).
- **For qa-child:** see **Tests expected to move** above; also Joan's optional note — parent AC 6 storage half (two ciphertext rows) is implemented in Stage 2.
