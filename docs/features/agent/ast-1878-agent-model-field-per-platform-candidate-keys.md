<!-- linear-archive: AST-1878 archived 2026-10-08 -->

## Linear archive (AST-1878)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1878/agent-model-field-per-platform-candidate-keys-support-openrouter-api  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** hedy  
**Priority / estimate:** None / 5  
**Parent:** AST-1851 — Support OpenRouter API models for agent work  
**Blocked by / blocks / related:** parent: AST-1851; blocks: AST-1879

### Description

## What this implements

After #1. The `agent` table and seed carry a model; brain size is validated against it; candidates store one encrypted key per server and hydrate as a server → key map; the legacy single key goes dark. Does **not** change call routing (#3) or admin routes/UI (#4).

## Citations

new pattern *Model → server catalog routing*.

## Scope

`src/data/database.py` — agent model field (save/update allowlist, repo JSON), per-model brain-size validation on save, candidate key table + set/clear/list helpers, `get_candidate` key map without the legacy key, timesheet insert validation, header inventory; backfill switches to `calculate_cost_components_from_counts`. `src/utils/config.py` — **only** add the agent model field to `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` (AST-1883 approved exception). `src/core/candidate.py` — per-server save/clear wrappers; `run_session_resume_parse` requires a candidate id and adds its key map to the synthetic ctx (no bind/persist). `data/admin/agent.json` — model on every row; new contact-Estelle row (content copied from `principal_recruiter_estelle`, Kimi K2.6 direct, Little). `data/admin/agent_task.json` — `contact_estelle_turn` points at the contact-Estelle agent.

## Acceptance criteria

3. **Agent rows name catalog models with valid sizes.** Every row in `data/admin/agent.json` has a model id that is a config model-catalog key and a brain size in that model's list (a Python one-liner loading both prints nothing). Any missing/unknown model or size = fail.
4. **Seed values.** `principal_recruiter_estelle` and `content_writer_judith` carry the Kimi K2.6 (Kimi direct) model id with brain size Big; the new contact-Estelle row carries Kimi K2.6 (Kimi direct) with Little; the other four agents carry the DeepSeek V4 model id with their pre-epic brain sizes. Any other value = fail.
5. **Legacy key retired.** `get_candidate` no longer returns a single `candidate_api_key` string (component test), and no save path writes the legacy column. Either still present = fail.

## Boundaries

Stays inside the Scope above. Sibling slices: #1 catalog/client, #3 runtime routing, #4 admin UI.

## Notes for planning

New pattern *Model → server catalog routing* is defined on parent AST-1851 (Architectural definition). Each child must stay green on its own `sub/*`. Additive only: legacy provider symbols stay importable until #4.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-29T21:05:43.890Z
[code-rubric] PROCEED (Commit: f74ca3030) data layer keys clean — context_tokens≈38000

#### betty — 2026-09-29T21:02:49.820Z
`origin/sub/AST-1851/AST-1878-agent-model-per-platform-keys` @ `f74ca3030` · key/model tests landed

#### joan — 2026-09-29T20:50:27.285Z
[plan-rubric] PROCEED (Commit: 0f6eee2f7) Data layer keys plan clean — context_tokens≈115000

#### hedy — 2026-09-29T20:48:39.040Z
`origin/sub/AST-1851/AST-1878-agent-model-per-platform-keys` @ `0f6eee2f7` · plan ready, three stages

---

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


## Radia review

[code-rubric]
**Ticket:** AST-1878
**Publish ref:** f74ca3030
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

Model → server catalog routing | A | |

## Column diff vs plan stage

(aligned)

## Frame diff

- [ ] **Acceptance criteria — parent AC 6 (storage half):** Optional child-ticket bullet that two Fernet `candidate_key` rows per candidate are required (verification already in plan **Tests expected to move** / qa-child). Engineer to confirm at UT if Susan wants Linear traceability to match parent AC 6.

## Findings

### fix-now

(none)

### discuss

- **Severity:** discuss  
- **Location:** `src/ui/api/api_candidate.py` (unchanged on this branch) vs `src/core/candidate.py` `clear_candidate_api_key(candidate_id, server_id)`  
- **Finding:** Admin clear-key still calls `clear_candidate_api_key(candidate_id)` with one argument; the data-layer API is now per-server. That path will fail at runtime until #4 (AST-1880) updates candidate admin routes.  
- **Recommendation:** Treat as the documented layer split (#1878 data only); do not widen #1878 into `api_candidate.py`.  
- **Default:** #4 owns the PATCH/clear wiring to pass `server_id`; leave #1878 tip as-is.

### advisory

- **Severity:** advisory  
- **Location:** Three-dot diff vs `origin/dev`  
- **Finding:** Branch stacks AST-1877 catalog/client (`config.py`, `llm_compat.py`, `env.example`, ast-1877 plan doc) ahead of dev — expected for child 2 on the same epic, not AST-1878 scope smuggling. AST-1878 product footprint: `database.py`, `candidate.py`, `data/admin/agent.json`, `data/admin/agent_task.json`, plus the single `REPO_ADMIN_JSON_CONFIG` `model_id` column line in `config.py`.  
- **Recommendation:** None for resolve-child on #1878.

- **Severity:** advisory  
- **Location:** `tests/component/frontend/**` (AST-1874 modal/tab/score changes) in merge-tests commit `81dd0c445`  
- **Finding:** sibling test carry on the sub; not #1878 product scope.  
- **Recommendation:** Note once; no separate Linear comment.

- **Severity:** advisory  
- **Location:** `data/admin/agent.json` — `principal_recruiter_estelle`  
- **Finding:** Analysis Estelle keeps `max_tokens: 384000` on `kimi-k2.6` Big (plan hand-off to #3 for call-path sanity).  
- **Recommendation:** None at this review gate.

## What's solid

- **AC 3 / 4:** Seed has `model_id` on every agent; AC 4 mapping matches (`principal_recruiter_estelle` / `content_writer_judith` → `kimi-k2.6` Big; `contact_recruiter_estelle` → `kimi-k2.6` Little; four agents on `deepseek-v4` with prior brain sizes). `contact_estelle_turn` current row → `contact_recruiter_estelle`.
- **AC 5 (child slice):** `get_candidate` hydrates `candidate_api_keys` and strips legacy `candidate_api_key` from the returned dict; `save_candidate` does not write the legacy column; `candidate_key` table with Fernet upsert/clear/list and hard-delete cascade.
- **Pattern:** `model_id` + per-model brain validation on agent save/update/repo JSON; `_expose_agent_public` resolves SKU via `resolve_model_brain`; timesheet insert validates SKU with `get_sku_pricing(model_code, provider)`; backfill is `backfill_agent_timesheet_costs(server_id)` on `calculate_cost_components_from_counts`.
- **Scope gate (AST-1883):** `config.py` edit on this ticket is the repo-admin `model_id` column addition only (catalog block is #1877 carry).
- **Session paste (parent 16-partial):** `run_session_resume_parse` requires `candidate_id`, loads candidate, injects `candidate_api_keys` into synthetic ctx without bind/persist.

## Recommended actions

- Chuckles: append artifact, `docs(AST-1878): Radia review — clean`, post slim upshot, **Review Posted** → datt **PROCEED** to User Testing (no canon fix-now for #1878).
- #4 / #3: consume hand-off notes (`candidate_api_keys` map, server-scoped set/clear, optional `model_id` on agent writes, `api_candidate` arity).

context_tokens≈38000

`[code-rubric] PROCEED (Commit: f74ca3030) data layer keys clean`

## Resolution

2026-09-29, resolved against Radia review `ff3b5c2c4` (CLEAN / PROCEED). No product changes.

- **fix-now:** none.
- **discuss — `api_candidate.py` still calls `clear_candidate_api_key` with one argument:** took the review's `Default:`. #4 (AST-1880) owns the admin PATCH/clear wiring that passes `server_id`, and this tip stays as it is. That file is outside #1878's Scope, and the gap is already listed under **Transitional gaps**. Susan can reverse this by asking for it here.
- **Frame diff — parent AC 6 storage-half bullet:** not added to the Linear description. Engineers don't write AC. The storage half is implemented in Stage 2 and covered by `TestAst1878CandidateServerKeys`, and the row is left for Susan/Chuckles if she wants Linear to trace it.
- **Advisories:** no action. The AST-1877 carry, sibling test carry, and the Estelle `max_tokens` hand-off to #3 are already recorded.

## Bug: AST-1901 — Candidate keys: JSON array of {server, key} on the candidate

Design calls settled by Susan on AST-1901 ([plan-discuss] round=1, answer "1B, 2A"):
- Entries are keyed by **LLM server**: `{"server": "<LLM_SERVER_CONFIG id>", "key": "…"}`. Parent functional scope 5 and AC 6 (one key per platform) stay as they are.
- The array lives in a dedicated **`api_keys`** column on the `candidate` row. Each entry's `key` is Fernet-encrypted.
- The `candidate_key` table is removed. Duplicate server entries are rejected on save.

### As-is

Per-server keys live in a separate `candidate_key` table (AST-1878 Stage 2: one row per candidate × server, `set/clear/list_candidate_server_key(s)`, cascade-deleted with the candidate). `get_candidate` hydrates `candidate_api_keys` from that table. `list_candidates` rows carry no keys, so `api_candidate._sanitize_candidate` calls `get_candidate` once per list row. Outbound candidates carry `api_keys` as a **fixed dict with one slot per catalog server** (`{sid: {label, set}}` for every entry in `LLM_SERVER_CONFIG`). Manage Candidates renders one fixed key field per server (four today). The PUT body takes `api_keys` as a `{server_id: key}` object.

### To-be

The candidate row has an `api_keys` JSON array of `{"server", "key"}` entries: any number of entries, at most one per server, no fixed slots. `candidate_key` does not exist, and schema setup drops it on existing databases. Outbound candidates list only the servers that have a key (`[{server, label}]`, never the key). Manage Candidates shows those entries plus an "Add API key for…" server picker built from the catalog. The PUT body takes `api_keys` as an array of `{server, key}` edits. Routing and the Invalid / Run gates still read `get_candidate(...)["candidate_api_keys"]`, which is now hydrated from the array.

### Repro

On `origin/ftr/AST-1851-support-openrouter-api-models` @ `777c04a81`, with a candidate `smith` in state `NEW_CANDIDATE` and `ASTRAL_ENCRYPTION_KEY` set:
1. `database.set_candidate_server_key("smith", "kimi", "sk-kimi")`.
2. `sqlite3 astral.db "SELECT name FROM sqlite_master WHERE name='candidate_key'"` returns `candidate_key`, which should not exist.
3. `GET /api/candidates/smith` returns `"api_keys": {"anthropic": {"label": …, "set": false}, "deepseek": {…, "set": false}, "kimi": {…, "set": true}, "openrouter": {…, "set": false}}`, which is four fixed slots rather than an array holding only the kimi entry.
4. Manage Candidates → Edit `smith` shows four key fields.

### Root cause

AST-1878 Stage 2 modelled per-server keys as a separate relational table, as the parent Technical scope worded it ("new candidate key table"). AST-1880 then rendered one slot per `LLM_SERVER_CONFIG` entry. Susan's intent is a variable-length JSON array held on the candidate itself.

### Proposed change

⚠️ **Decision (scope):** this replaces the parent Technical scope's "new candidate key table" wording with Susan's UAT to-be. The files stay inside the parent Component scope (`database.py`, `core/candidate.py`, `api_candidate.py`, `AdminManageCandidates.tsx`), and each change is the same kind that scope already describes: key storage and hydration, per-server save wrappers, the PATCH plus the outbound set/not-set view, and a catalog-driven key form.

⚠️ **Decision (routing contract unchanged):** `candidate_api_keys` (`{server_id: plaintext}`) stays the in-memory hydrate. It is now derived from the `api_keys` array, which is the single stored copy. This leaves AST-1879's readers untouched: `dispatcher.py:1338`, `agent.py` (~1850, ~3343), `meteorite.py:759`, `contact.py:1161`, and `api_admin.py` (~1568, ~2061).

**1. `src/data/database.py`**

a. **Header inventory.**
   - In the `candidate` line, after `candidate_api_key TEXT (legacy — not read or written since AST-1878),`, insert `api_keys TEXT JSON array [{"server": LLM_SERVER_CONFIG id, "key": Fernet ciphertext}] — at most one entry per server; hydrated as candidate_api_keys {server: plaintext} (AST-1901),`.
   - Delete the whole `- candidate_key — …` line.

b. **`_ensure_candidate_schema`.**
   - In `CREATE TABLE candidate`, add `api_keys TEXT DEFAULT '[]',` directly after `candidate_api_key TEXT,`.
   - In the ALTER migration list, add `("api_keys", "TEXT DEFAULT '[]'"),` directly after `("candidate_api_key", "TEXT"),`.
   - After the `if/else` and before `_drop_entity_agent_responses_column(conn, "candidate")`, add:

     ```python
     # AST-1901: per-server keys live in candidate.api_keys; DDL-only drop, no content migration (AST-1497) — keys are re-entered in Manage Candidates.
     conn.execute("DROP TABLE IF EXISTS candidate_key")
     conn.commit()
     ```

   ⚠️ **Decision:** no copy of existing `candidate_key` rows into the array. Schema setup stays DDL-only (AST-1497), and the parent already says keys are entered manually with no migration. Any keys entered during UAT are re-entered once.

c. **Delete** the whole `# -- candidate_key: … (AST-1878) --` block: `_ensure_candidate_key_table`, `_candidate_key_map`, `set_candidate_server_key`, `clear_candidate_server_key`, `list_candidate_server_keys`.

d. **New helpers**, placed where that block was (directly above `def get_candidate(`):

   ```python
   def _candidate_api_key_entries(raw: Any) -> List[Dict[str, str]]:
       """candidate.api_keys column → [{server, key(ciphertext)}]; malformed JSON / entries dropped."""
       try:
           entries = json.loads(raw) if raw else []
       except (TypeError, ValueError):
           return []
       return [
           {"server": str(e["server"]), "key": str(e["key"])}
           for e in (entries if isinstance(entries, list) else [])
           if isinstance(e, dict) and e.get("server") and e.get("key")
       ]


   def _candidate_key_map_from_column(raw: Any) -> Dict[str, str]:
       """api_keys array → {server: plaintext} in array order; undecryptable entries omitted (treated as not set)."""
       out: Dict[str, str] = {}
       for e in _candidate_api_key_entries(raw):
           try:
               out[e["server"]] = decrypt_value(e["key"])
           except (RuntimeError, ValueError):
               continue
       return out


   def update_candidate_api_keys(candidate_id: str, entries: List[Dict[str, str]]) -> None:
       """Apply key edits to candidate.api_keys: non-empty key sets/replaces that server's entry, "" removes it.
       Raises ValueError on unknown server / duplicate server in entries, LookupError if the candidate is missing."""
       cid = str(candidate_id or "").strip()
       if not cid:
           raise ValueError("candidate_id is required")
       edits: Dict[str, Optional[str]] = {}
       for e in entries:
           sid = str((e or {}).get("server") or "")
           get_llm_server(sid)
           if sid in edits:
               raise ValueError(f"Duplicate api_keys entry for server {sid!r}")
           key = str((e or {}).get("key") or "").strip()
           # Encrypt before opening the connection; None marks a removal.
           edits[sid] = encrypt_value(key) if key else None
       now = _utc_now()

       def _with_conn() -> None:
           conn = _get_connection()
           try:
               _ensure_candidate_schema(conn)
               row = conn.execute(
                   "SELECT api_keys FROM candidate WHERE astral_candidate_id = ?", (cid,)
               ).fetchone()
               if row is None:
                   raise LookupError(f"Candidate not found: {cid}")
               # Existing order kept; new servers append — at most one entry per server by construction.
               merged = {e["server"]: e["key"] for e in _candidate_api_key_entries(row["api_keys"])}
               for sid, ciphertext in edits.items():
                   if ciphertext is None:
                       merged.pop(sid, None)
                   else:
                       merged[sid] = ciphertext
               conn.execute(
                   "UPDATE candidate SET api_keys = ?, updated_at = ? WHERE astral_candidate_id = ?",
                   (json.dumps([{"server": s, "key": k} for s, k in merged.items()]), now, cid),
               )
               conn.commit()
           finally:
               conn.close()

       _run_with_retry(_with_conn)
   ```

e. **`_parse_candidate_row`**: replace the two lines `# Legacy single key is never exposed (AST-1878); …` and `d.pop("candidate_api_key", None)` with:

   ```python
   # Legacy single key is never exposed (AST-1878); the api_keys array hydrates as a server → key map (AST-1901).
   d.pop("candidate_api_key", None)
   d["candidate_api_keys"] = _candidate_key_map_from_column(d.pop("api_keys", None))
   ```

   This hydrates every parsed row (`get_candidate`, `list_candidates`, the claim/list readers at ~3795), so list rows no longer need a follow-up `get_candidate` call.

f. **`get_candidate`**: restore the one-line body `return _parse_candidate_row(_row_to_dict(row)) if row else None`, which drops the `_candidate_key_map(conn, …)` call. Keep the docstring.

g. **Cascade removal.** The keys now die with the candidate row.
   - `hard_delete_candidate`: delete the `"candidate_key": 0,` counts entry and the `("candidate_key", "DELETE FROM candidate_key WHERE candidate_id = ?"),` tuple.
   - `_legacy_candidate_migrate_conn`: delete the `"DELETE FROM candidate_key WHERE candidate_id = ?",` line.

**2. `src/core/candidate.py`**

- `save_candidate_admin` docstring becomes `"""Direct candidate row updates from admin API (state override, etc.). API keys: update_candidate_api_keys."""`.
- Replace `set_candidate_api_key` and `clear_candidate_api_key` with:

  ```python
  def update_candidate_api_keys(candidate_id: str, entries: List[Dict[str, str]]) -> None:
      """Admin key edits on the candidate's api_keys array: key sets/replaces that server's entry, "" removes it."""
      database.update_candidate_api_keys(candidate_id, entries)
  ```

  (`List`, `Dict` are already imported.) `run_session_resume_parse` is unchanged, because it reads `candidate_api_keys` from `database.get_candidate`.

**3. `src/ui/api/api_candidate.py`**

a. Imports from core: remove `clear_candidate_api_key` and `set_candidate_api_key`, and add `update_candidate_api_keys`.

b. `_sanitize_candidate` becomes:

   ```python
   def _sanitize_candidate(c: dict) -> dict:
       """Strip every key (plaintext map + legacy ciphertext); expose the api_keys array as [{server, label}]. Applied to every outbound candidate."""
       keys = c.pop("candidate_api_keys", None) or {}
       c.pop("candidate_api_key", None)
       # One entry per stored key, in array order (AST-1901) — no fixed per-server slots, never the key itself.
       c["api_keys"] = [
           {"server": sid, "label": (LLM_SERVER_CONFIG.get(sid) or {}).get("label", sid)} for sid in keys
       ]
       return c
   ```

c. `update_candidate_data` changes:
   - Docstring's last line becomes `api_keys handling ([{server, key}]): non-empty key = set/replace that server's entry, "" = remove it; duplicate servers → 400.`
   - Replace the `if api_keys is not None:` validation block (dict check plus the per-server loop) with:

     ```python
     if api_keys is not None:
         if not isinstance(api_keys, list):
             return jsonify({"error": "api_keys must be an array of {server, key}"}), 400
         seen_servers: set = set()
         for e in api_keys:
             sid = e.get("server") if isinstance(e, dict) else None
             if sid not in LLM_SERVER_CONFIG or not isinstance(e.get("key"), str):
                 # Name the server only — never echo a submitted key.
                 return jsonify({"error": f"Invalid api_keys entry for server {sid!r}"}), 400
             if sid in seen_servers:
                 return jsonify({"error": f"Duplicate api_keys entry for server {sid!r}"}), 400
             seen_servers.add(sid)
     ```

   - Replace the apply loop (`# One candidate_key row per server; …` plus the `for sid, key in (api_keys or {}).items():` block) with:

     ```python
     # Edits land in the candidate's api_keys array; the data layer encrypts (AST-1901).
     if api_keys:
         update_candidate_api_keys(candidate_id, [{"server": e["server"], "key": e["key"].strip()} for e in api_keys])
     ```

   The trailing `if api_keys and not (…)` info-log check works unchanged on a list.

**4. `src/ui/frontend/src/pages/AdminManageCandidates.tsx`**

a. **`Candidate` type.** Replace the `api_keys?: Record<…>` field and its comment with:
   `/** Stored keys only, in array order (AST-1901): server id + catalog label — never the key itself. */`
   `api_keys?: { server: string; label: string }[]`

b. **Row mapping.** Change `api_key_status` to `(c.api_keys ?? []).map(k => k.label).join(", ") || "Not set"`. Update the `api_key_status` column comment (~line 595) to `// Value is the joined labels of servers with a stored key (AST-1901), or "Not set".`

c. **New state**, next to `keyInputs`:
   - `const [keyServers, setKeyServers] = useState<{ server: string; label: string }[]>([])` with the comment `// Server catalog for "Add API key for…", derived from /api/admin/agents/models (no literals).`
   - `const [addedServers, setAddedServers] = useState<string[]>([])`
   - Change the `keyInputs` comment to `// Key edits keyed by server id: typed value, show toggle, pending clear (stored entries) / added rows.`

d. **Mount effect** (the `useEffect` with `/api/shapes/candidates`): add

   ```ts
   api("/api/admin/agents/models").then(r => r.json()).then((m: Record<string, { order: number; server_id: string; server_label: string }>) => {
     const seen = new Set<string>()
     setKeyServers(Object.values(m).sort((a, b) => a.order - b.order).flatMap(x =>
       seen.has(x.server_id) ? [] : (seen.add(x.server_id), [{ server: x.server_id, label: x.server_label }])))
   })
   ```

e. **Opening Edit.** Next to `setKeyInputs({})` / `setShowKeys({})` / `setClearKeys({})` (~line 374), add `setAddedServers([])`.

f. **Save payload.** Replace the `apiKeys` block (~lines 425–431) with:

   ```ts
   // Only rows that changed: typed key = set/replace, "" = remove a stored entry; omit when nothing changed.
   const apiKeys: { server: string; key: string }[] = []
   for (const sid of [...(editTarget.api_keys ?? []).map(k => k.server), ...addedServers]) {
     if (clearKeys[sid]) apiKeys.push({ server: sid, key: "" })
     else if ((keyInputs[sid] ?? "").trim()) apiKeys.push({ server: sid, key: keyInputs[sid].trim() })
   }
   if (apiKeys.length) payload.api_keys = apiKeys
   ```

g. **Key fields.** Replace the `{/* One key field per catalog server (AST-1880); … */}` block with rows for stored entries followed by added rows, then the add picker:
   - `const keyRows = [...(editTarget?.api_keys ?? []).map(k => ({ ...k, stored: true })), ...addedServers.map(sid => ({ server: sid, label: keyServers.find(s => s.server === sid)?.label ?? sid, stored: false }))]`
   - Declare this inside the component body, just above `return (`.
   - Each row renders exactly as the current per-server field does, with `k.server` in place of `sid`, `key={k.server}`, and this label: `{k.label} API key {k.stored ? "(set — leave blank to keep current)" : "(new)"}`.
   - The existing **Clear** button (confirm dialog + `setClearKeys`) renders only when `k.stored && !keyInputs[k.server] && !clearKeys[k.server]`.
   - Unsaved rows (`!k.stored`) get a `btn secondary` **Remove** button that runs `setAddedServers(p => p.filter(s => s !== k.server))` and `setKeyInputs(p => { const n = { ...p }; delete n[k.server]; return n })`.
   - After the rows, when `keyServers.some(s => !keyRows.find(r => r.server === s.server))`, render:

     ```tsx
     <div className="dep-field">
       <select className="dep-input" value="" onChange={e => { const sid = e.target.value; if (sid) setAddedServers(p => [...p, sid]) }}>
         <option value="">Add API key for…</option>
         {keyServers.filter(s => !keyRows.find(r => r.server === s.server)).map(s => <option key={s.server} value={s.server}>{s.label}</option>)}
       </select>
     </div>
     ```

     This offers only servers without a row, so the UI can't produce a duplicate.

**Compile / lint:** `python3 -m py_compile` on the three `.py` files, then `cd src/ui/frontend && npx tsc -b --noEmit`.

### Blast radius

- **AST-1879 routing / gates** (`dispatcher.py`, `agent.py`, `meteorite.py`, `contact.py`, and `api_admin.py`'s Invalid + Run gate and ad-hoc resolve): no code change, because the `candidate_api_keys` contract is kept. `candidate_api_keys` now also appears on `list_candidates` / claim-batch rows, which is harmless for those readers.
- **AST-1880 admin surface:** the outbound `api_keys` shape changes from a dict to an array (only `AdminManageCandidates.tsx` reads it, per `rg api_keys src/ui/frontend/src`), and the PUT `api_keys` body changes from an object to an array.
- **Tests Betty will need to move:**
  - `test_candidates.py::TestAst1878CandidateServerKeys` (table helpers go away) and the hard-delete count assertions that mention `candidate_key`.
  - `test_candidate.py::TestCandidateAdminFacades` (set/clear wrappers become `update_candidate_api_keys`).
  - `test_api_candidate.py` `api_keys` sanitize / PUT cases (dict → array).
  - Any `tests/component/frontend/**` coverage of the Manage Candidates key fields.
  - Bible pages `data/database/candidates.md` and the api_candidate / frontend pages.
- **Data:** keys stored in `candidate_key` on existing databases are dropped with the table and have to be re-entered once.

### What must still hold

- **AST-1878 AC 5 / parent AC 13:** `get_candidate` has no single `candidate_api_key`, and no path writes the legacy column.
- **Parent AC 6, re-worded by Susan's to-be:** setting a Kimi key and an OpenRouter key leaves two entries in that candidate's `api_keys` array. Both hold ciphertext that differs from the plaintext, and a GET lists both servers. One key never overwrites another.
- **Parent AC 7 / 8 / 14 / 16:** right key and no fallback; Invalid on a missing server key; Slack and session-paste keys come from the candidate. These are unchanged because the map contract is unchanged.
- **Parent AC 2:** no server or model literals outside `config.py`. Labels come from `LLM_SERVER_CONFIG` or the models endpoint.
- **Parent AC 12, candidate half, superseded:** the "exactly one key field per server" wording is replaced by Susan's "no fixed slots". The form lists only stored entries plus an add picker drawn from the catalog.
- **No plaintext outbound:** API responses and error messages never include a key.


### Joan fix-board — AST-1901

**Verdict comment body (for Chuckles to post):**

```
[board-joan]  CANON: OK
```

**Rationale**

The `## Bug: AST-1901` patch keeps the runtime contract AST-1879 depends on: in-memory `candidate_api_keys` as `{server_id: plaintext}`, still derived from catalog server ids via `get_llm_server` / `LLM_SERVER_CONFIG`. That matches parent **Model → server catalog routing** (model → server for tasks; one key per platform on the candidate), even though persistence moves from `candidate_key` rows to a JSON `api_keys` column. Susan’s plan-discuss answer (1B, 2A) keys entries by **server**, not model, which aligns with parent functional scope 5 and AC 6’s “one key per platform” semantics; the patch explicitly supersedes the old “two rows in the candidate key table” / fixed four-slot UI wording without changing routing or gate behavior.

Against parent **Canon Scope** statutes, the touched surface (`database.py`, `api_candidate.py`, `AdminManageCandidates.tsx`) does not introduce a logging, API completion, or config-source-of-truth conflict: no new `debug=` logging paths; dispatch Invalid / skip warnings stay who/why on missing **server** keys; PUT completion info lines are unchanged; labels still come from config or `/api/admin/agents/models`; error responses still avoid echoing keys (“What must still hold”). Header-inventory edits are the kind **astral.standards.database-header-inventory** expects for schema changes, not a directive rewrite. Nothing in force mandates a separate `candidate_key` table or exactly four admin slots—those were epic plan text, corrected by Susan’s UAT to-be.

No **REVISE** (no statute/pattern carve-out to land in F3) and no **ESCALATE** (storage shape is a bounded product fix, not ambiguous statute intent).

```
AST-1901 board-joan done — CANON: OK.
```


### Radia review — AST-1901

[code-rubric]
**Ticket:** AST-1901
**Publish ref:** 5835782f1
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

(frozen list empty — ticket has no `## Citations` directive ids; Joan fix-board **CANON: OK** with no statute rows to score)

## Column diff vs plan stage

no plan-stage canon scores attached (fix-board only)

## Frame diff

(none)

## [bug-repro]

**Verdict:** OK — `TestAst1901CandidateApiKeysArray` (database) and `test_put_two_server_keys_stores_ciphertext_array_and_get_lists_servers_only` (api) pin **to-be**: `candidate.api_keys` JSON array, `candidate_key` table gone, outbound `[{server, label}]` only, two-platform ciphertext ≠ plaintext, map hydrate for routing. Would fail on AST-1878/1880 fixed-slot + `candidate_key` table.

**Advisory:** qa-fix commit names bug-repro but no test uses the first-line `[bug-repro]` tag the skill machinery expects; assertions are substantive anyway.

## What must still hold

**Verdict:** OK — legacy `candidate_api_key` not exposed; two-server storage + GET list semantics covered; `candidate_api_keys` map unchanged for #1879 readers; no vendor literals in touched UI/API; dynamic admin rows + catalog picker; errors do not echo submitted keys.

## Findings

### fix-now

(none)

### discuss

- **Severity:** discuss  
- **Location:** Susan UAT comment vs plan-discuss **1B, 2A**  
- **Finding:** Linear bug text says “array of JSON between **model** and key”; shipped design and patch use **`server`** (`LLM_SERVER_CONFIG` id) per Susan’s answered plan-discuss. Implementation matches patch and parent “one key per platform,” not a model-id array.  
- **Recommendation:** Optional ticket wording cleanup so UAT traceability matches storage shape.  
- **Default:** Treat plan-discuss + patch as authoritative; no code change.

### advisory

- **Severity:** advisory  
- **Location:** `database._ensure_candidate_schema` — `DROP TABLE IF EXISTS candidate_key`  
- **Finding:** DDL-only; no migration of existing `candidate_key` rows into `api_keys` (documented in patch). UAT DBs need keys re-entered once.  
- **Recommendation:** Note in parent UAT checklist.

- **Severity:** advisory  
- **Location:** AST-1879 deferrals (this brief)  
- **Finding:** **Not in AST-1901 scope:** `api_admin` ad-hoc/dispatch gate and `api_candidate` clear arity were **AST-1880** items (on `origin/dev` via PR #195). This fix replaces storage/UI shape only; it does not regress those paths and keeps `update_candidate_api_keys` + hydrated list rows.  
- **Recommendation:** Confirm parent UAT still exercises 1880 admin surfaces separately.

- **Severity:** advisory  
- **Location:** `stat.logging.info.api` (carry from AST-1880 Radia discuss)  
- **Finding:** `api_keys`-only `PUT …/data` still may omit a completion info line when no catalog leaf saves — unchanged by this diff (“must still hold: PUT completion info lines unchanged”).  
- **Recommendation:** Optional follow-up on AST-1880 / separate ticket if Susan wants that log.

## What's solid

- `candidate.api_keys` column + helpers; `candidate_key` table and server-key CRUD removed; `get_candidate` / `list_candidates` hydrate `candidate_api_keys` via `_parse_candidate_row` (no per-row `get_candidate` in `_sanitize_candidate`).
- `api_candidate`: array PUT validation, duplicate-server 400 without echoing keys, `_sanitize_candidate` → `[{server, label}]` in stored order.
- `AdminManageCandidates`: stored rows + “Add API key for…” from `/api/admin/agents/models`; no four fixed slots.
- Tests + bible updates on tip align with repro and AC 6 storage half.

## Recommended actions (Chuckles)

- Append artifact; `docs(AST-1901): Radia review — clean`; post slim upshot; **Review Posted** → fix-lane clean shortcut → **User Testing** (skip `resolve-child`).
- **Parent shape:** normal batch on AST-1851 (diff base `origin/dev...sub/AST-1901` per spawn override — not orphaned).
- Optional: clarify Linear bug text **model** → **server** if Susan wants ticket prose aligned.

## Bug: AST-1920 — Manage Candidate modal has no api_key access

UAT-batch bug on AST-1851. Susan's decision (AST-1920 Description, 2026-10-01) is **option 1, UI only**. It reverses the UI half of § Bug: AST-1901 step 4 (stored rows plus the "Add API key for…" picker). AST-1901's storage (`candidate.api_keys` array), the PUT contract and the `candidate_api_keys` hydrate are untouched.

### As-is

Manage Candidates → Edit renders one key field per **stored** `api_keys` entry, then an "Add API key for…" select. A candidate with no stored keys therefore shows no key text fields at all, only the select. On staging every candidate is in that state, because AST-1901's `DROP TABLE IF EXISTS candidate_key` deleted the UAT-entered keys by design.

### To-be

The Edit modal shows one API key field for **every** server in the model catalog (`GET /api/admin/agents/models`, deduped by server, catalog order), whether or not a key is set.
- A server with a stored entry shows "(set — leave blank to keep current)" with Show / Clear.
- A server without one shows "(not set)" with an empty field and Show.
- There is no picker and no Remove button.

Save still sends only the changed rows as `[{server, key}]` (`""` removes a stored entry) and omits `api_keys` when nothing changed.

Out of scope (Susan): recovering dropped `candidate_key` rows, and carrying legacy `candidate_api_key` values into `api_keys`. Keys are re-entered by hand.

### Repro

On `origin/sub/AST-1851/AST-1920-manage-candidate-key-fields` @ `dd4d03c0d`, Manage Candidates with a candidate whose GET carries `api_keys: []`, and `/api/admin/agents/models` serving the catalog (anthropic, kimi, deepseek, openrouter):
1. Click **Edit**.
2. No `… API key` field renders. Only the "Add API key for…" select is present.
3. With `api_keys: [{server: "kimi", label: "Kimi"}]`, only the Kimi field renders. Anthropic, DeepSeek and OpenRouter have no field.

### Root cause

AST-1901 step 4g derives `keyRows` from stored entries plus `addedServers`, so unset servers have no row until one is picked. Susan's AST-1901 "no fixed slots" was meant for the storage shape. In the UI it hid the key fields.

### Proposed change

**`src/ui/frontend/src/pages/AdminManageCandidates.tsx`** is the only product file. No API, data-layer or `Candidate.api_keys` type change.

1. **State.**
   - Delete `const [addedServers, setAddedServers] = useState<string[]>([])`.
   - Change the comment above `keyServers` to `// Server catalog for the key fields, derived from /api/admin/agents/models (no literals).`
   - Change the `keyInputs` comment to `// Key edits keyed by server id: typed value, show toggle, pending clear.`
   - The mount-effect fetch that fills `keyServers` (dedupe by `server_id`, sort by `order`) stays as it is.

2. **Opening Edit.** Delete the `setAddedServers([])` line next to `setKeyInputs({})` / `setShowKeys({})` / `setClearKeys({})`.

3. **`keyRows` derivation.** Replace the `keyRows` + `addableServers` block above `return (` with:

   ```ts
   // One row per catalog server (AST-1920), set or not; stored entries the catalog no longer lists stay visible so they can be cleared.
   const storedKeys = editTarget?.api_keys ?? []
   const keyRows = [
     ...keyServers.map(s => ({ ...s, stored: storedKeys.some(k => k.server === s.server) })),
     ...storedKeys.filter(k => !keyServers.some(s => s.server === k.server)).map(k => ({ ...k, stored: true })),
   ]
   ```

   ⚠️ **Decision:** a stored entry whose server isn't in the catalog (retired server) is appended after the catalog rows with its outbound label, which `_sanitize_candidate` falls back to the id for. This keeps the "no hidden key" to-be honest and lets an admin clear it. It also renders the stored rows during the moment before `/api/admin/agents/models` resolves.

4. **Save payload.** In the `apiKeys` loop, change the iterated list from `[...(editTarget.api_keys ?? []).map(k => k.server), ...addedServers]` to `keyRows.map(r => r.server)`. The body stays the same: `clearKeys[sid]` gives `{server, key: ""}`, and a trimmed non-empty `keyInputs[sid]` gives `{server, key}`. Change the comment to `// Only rows that changed: typed key = set/replace, "" = remove a stored entry; omit when nothing changed.`. Clear only renders on stored rows, so `""` is only ever sent for a stored server.

5. **Key fields.**
   - Change the `{/* … */}` comment above `keyRows.map` to `{/* One key field per catalog server (AST-1920); labels come from the server, not literals. */}`.
   - Label suffix: `{k.stored ? "(set — leave blank to keep current)" : "(not set)"}`, replacing `"(new)"`.
   - Delete the `{!k.stored && ( … Remove … )}` button block with its comment.
   - Delete the whole `{addableServers.length > 0 && ( … "Add API key for…" … )}` picker block with its comment.
   - The Show/Hide button and the stored-only Clear button (confirm dialog) stay as they are.

**Compile / lint:** `cd src/ui/frontend && npx tsc -b --noEmit && npx eslint src/pages/AdminManageCandidates.tsx`.

### Blast radius

- **AST-1901 frontend tests** (`tests/component/frontend/pages/test_AdminManageCandidates.test.tsx`) assert the picker, `(new)` rows and Remove: the main CRUD test, the "no keys … full picker" test, and "Remove drops an unsaved row …". Betty rewrites them, and updates `docs/test-bible/frontend/pages.md` § AST-1901 to say one field per catalog server.
- The API Key list column (`api_key_status`, stored labels), `api_candidate.py`, `database.py`, and the AST-1879 routing / gates are untouched.

### What must still hold

- **AST-1901 storage and API contract:** the PUT carries only changed rows as `[{server, key}]`, `""` removes, and `api_keys` is omitted when nothing changed. No duplicate server is possible, because each server has exactly one row.
- **Parent AC 2:** no server literals in the UI. Labels come from `/api/admin/agents/models` or the outbound `api_keys` label.
- **No plaintext outbound:** the form never shows a stored key, only "(set …)".
- **Parent AC 12, candidate half:** one key field per catalog server is restored (AST-1880's original shape), with stored state from the `api_keys` array.

### Joan fix-board (AST-1920)

#### Findings

The patch is **frontend-only** (`AdminManageCandidates.tsx`): `keyRows` becomes one row per catalog server (plus orphan stored servers for Clear), with the AST-1901 add-picker / `addedServers` / Remove path removed. **AST-1901** storage (`candidate.api_keys` JSON array), PUT `[{server, key}]`, and in-memory **`candidate_api_keys`** are unchanged, so **Model → server catalog routing** and AST-1879 gates/routing need no canon adjustment.

Susan’s **option 1 (UI only)** restores the parent **AC 12** candidate shape (one field per catalog server) without undoing the variable-length array on the row. That is product scope alignment, not a conflict with in-force directives. Labels still come from `/api/admin/agents/models` or outbound `{server, label}` (parent **AC 2**). No new API routes → no **stat.logging.info.api** impact. Betty’s bible/test updates are test-tree, not statute.

No statute or pattern text requires the “stored rows + Add API key for…” UI or forbids fixed catalog rows while keeping array storage.

---

```
[board-joan]  CANON: OK

```
[board-joan]  CANON: OK
```

### Radia review-fix (AST-1920)

[code-rubric]
**Ticket:** AST-1920
**Publish ref:** 711621d1b
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

#### Canon scores

(frozen list empty on AST-1920 — no `## Citations` directive ids; UAT-batch bound to parent **Model → server catalog routing** per Joan fix-board and AST-1878 parent scope)

Model → server catalog routing | A | |
stat.logging.debug | X | |
stat.logging.error | X | |
stat.logging.warning | X | |
stat.logging.info.api | X | |

#### Column diff vs plan stage

no plan-stage canon scores attached (fix-board only; Joan **CANON: OK**)

#### Frame diff

(none)

#### [bug-repro]

**Verdict:** OK — Betty’s thread points at `origin/sub/AST-1851/AST-1920-manage-candidate-key-fields` @ `74087971d` (merge-tests); product tip `711621d1b`. `test_AdminManageCandidates.test.tsx` pins **to-be**: four catalog-order fields (deduped DeepSeek), `(set …)` vs `(not set)`, no picker/Remove, Clear only on stored rows, `api_keys: []` → four `(not set)` fields and Save **omits** `api_keys`, orphan `retired_srv` row after catalog + clear-only PUT, whitespace-only Anthropic not sent, changed rows only `[{server, key}]`. Main CRUD test rewritten from picker flow. Would fail on pre-fix AST-1901 (stored-only rows + “Add API key for…”).

**Advisory:** qa-fix comment uses `[bug-repro]`; tests are named `AST-1920:` / file header comment — no first-line `[bug-repro]` tag in the test source (same pattern as AST-1909/1901).

#### What must still hold

**Verdict:** OK

- **AST-1901 storage/API:** Save loop iterates `keyRows.map(r => r.server)`; only `clearKeys` / trimmed `keyInputs` become PUT rows; tests assert omit-when-unchanged and partial updates. No `api_candidate` / `database` change on `711621d1b`.
- **Parent AC 2:** no vendor/server literals in `AdminManageCandidates.tsx`; labels from `keyServers` / outbound `api_keys` labels.
- **No plaintext outbound:** stored rows still use password inputs + “(set — leave blank to keep current)”; no echo of ciphertext.
- **Parent AC 12 (candidate half):** one field per catalog server restored; storage remains `api_keys` array (Susan option 1).

#### Findings

##### fix-now

(none)

##### discuss

(none)

##### advisory

- **Severity:** advisory  
- **Location:** `git diff origin/ftr/AST-1851-support-openrouter-api-models...origin/sub/AST-1851/AST-1920-manage-candidate-key-fields`  
- **Finding:** Range includes **sibling** epic/fix work (AST-1909 `AdminTaskPrompts`, AST-1916/1917 tests, AST-1904/1905 `builder.py`, ast-1014 doc, etc.). **AST-1920 product** is single-file `711621d1b` (+ Betty `7c9610031` / merge `74087971d`).  
- **Recommendation:** Merge/review AST-1920 on its commits; do not attribute sibling diffs to this bug.

- **Severity:** advisory  
- **Location:** UAT / data  
- **Finding:** Plan and ticket: legacy `candidate_key` drop and dark `candidate_api_key` are **out of scope**; staging keys still require manual re-entry — UI fix does not recover DB rows.  
- **Recommendation:** Parent UAT checklist only.

#### What's solid

- Plan patch followed: `addedServers` / picker / Remove removed; `keyRows` = full `keyServers` + orphan stored servers; suffix `(not set)`; save payload unchanged semantically.
- Restores discoverable key entry without undoing AST-1901 array PUT contract or routing hydrate.
- Bible § AST-1920 + manifest describe repro; picker-era AST-1901 tests retired as planned.

#### Recommended actions (Chuckles)

- Append artifact; `docs(AST-1920): Radia review — clean`; post slim upshot **`--as radia`**; **Review Posted** → fix-lane clean shortcut → **User Testing** (skip `resolve-child`).
- **Parent shape:** AST-1851 live epic, UAT-batch — **not orphaned**; normal `sub` merge path (not straight-to-dev).

context_tokens≈28000

---

`[code-rubric] PROCEED (Commit: 711621d1b) catalog key fields restored`
