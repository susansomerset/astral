# AST-1948 — Agent mode persisted and applied; temperature and model_code retired from the agent row

- **Parent:** [AST-1946 — Support "Big" brain OpenRouter models](https://linear.app/astralcareermatch/issue/AST-1946)
- **Ticket:** [AST-1948](https://linear.app/astralcareermatch/issue/AST-1948)
- **Publish ref:** `origin/sub/AST-1946/AST-1948-agent-mode-row`
- **Canon Scope:** `stat.logging.debug`, `stat.logging.info.api`. No pattern applies (parent § Architectural definition: `no established pattern applies`).
- **Blocked by / paired with:** [AST-1947](https://linear.app/astralcareermatch/issue/AST-1947) (option A, [AST-1951](https://linear.app/astralcareermatch/issue/AST-1951)). AST-1947 is already on this sub via `origin/ftr/AST-1946-big-brain-openrouter`. It gives `resolve_model_brain(model_id, brain_setting, mode)`, `validate_agent_mode`, `AGENT_MODE_CONFIG`, the repo-JSON `mode` column and the seed rows with `mode`. It also removes `infer_brain_setting_from_legacy_model_code` and every tier's `default_temperature`.

The agent row gets a `mode` column (Deterministic | Creative) and loses `temperature` and the duplicate `model_code`. Every agent write, update and repo-JSON apply needs a valid mode. Agent calls (`do_task`) and the admin workbench (`_resolve_adhoc`) pass the agent's mode to AST-1947's resolver, and they take thinking and temperature only from the tier it returns. The agent public view returns `mode` and stops emitting `model_code`; `resolved_model_key` stays. `GET /agents/models` drops per-size `default_temperature`. This ticket also repairs the callers AST-1947 broke (the Chuckles comment on this ticket), so `ftr` imports and boots again. The UI (AST-1949) and the live-row migration (AST-1950) are not touched here.

## Scope gate

Every row in **Files Changed** is named in this ticket's `## Scope`, and every stage is the kind of change Scope describes for that file.

- `src/data/database.py`: config imports for the new mode validation and SKU read; the table docstring; schema-ensure (`mode` in, `temperature` / `model_code` dropped); brain-size coercion without the legacy fallback; the public view (`mode` in, `model_code` out, `resolved_model_key` kept); `save_agent`, the `update_agent` allow-list, repo-JSON validation and repo-JSON apply. `list_agents` is the public view's list read, and its SELECT swaps `model_code, temperature` for `mode`.
- `src/core/agent.py`: `_agent_llm_route` (the LLM route helper) passes mode. The `do_task` call path takes temperature from the resolved tier. The craft-rubric thinking-off guard and the `max_tokens_floor` block are unchanged.
- `src/ui/api/api_admin.py`: create/update routes, `_resolve_adhoc` (adhoc/workbench resolver) and `GET /agents/models`. The task-manager list's `resolve_model_brain` call (`_enrich_tasks`, line 389) also gets the mode argument. That is the same kind of change as the adhoc pass-through, and the Chuckles comment on this ticket names it ("passing the new `mode` argument to `resolve_model_brain`"; AST-1947 § Sequencing gap row 2 lists `api_admin.py:389`).
- `stat.logging.debug`: no `debug=` parameter is added anywhere. `do_task`'s existing ungated `logger.debug("Calling _send_to_server: [… temp=%s …]")` line keeps logging the temperature, which is now the mode's. `src/data/` gets no logging.
- `stat.logging.info.api`: `create_agent` / `update_agent` keep their existing `_api_completed(...)` lines unchanged. Neither line ever carried `temperature`, so there is nothing to swap for `mode`, and no new info line is added.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Docstring `agent` line. Config import: `infer_brain_setting_from_legacy_model_code` → `get_llm_model`, plus `validate_agent_mode`. `_coerce_agent_brain_setting` loses the legacy fallback. `_expose_agent_public`: mode-independent SKU, no `model_code`. `_validate_agent_repo_json_rows` validates mode. `apply_agent_repo_json_startup` writes `mode`. `_ensure_agent_schema`: `mode` added, `temperature` / `model_code` dropped. `save_agent` takes a required `mode`. `list_agents` SELECT. `_UPDATE_AGENT_ALLOWED` / `update_agent` validate mode. | data |
| `src/core/agent.py` | `_agent_llm_route` requires and passes `mode`. `do_task` temperature line → `tier["temperature"]`. | core |
| `src/ui/api/api_admin.py` | `list_models` drops `default_temperature`. `create_agent` / `update_agent` require `mode` and drop `temperature`. Task-manager list + `_resolve_adhoc` pass `mode`. `_resolve_adhoc` temperature → `tier["temperature"]`. | ui |

No other file is touched. No `tests/` or bible edits; Betty owns those (see **Tests expected to move**).

---

## Stage 1: Agent table — mode in, temperature and model_code out (`database.py`)

**Done when:** `python3 -c "import src.data.database"` succeeds. On an in-memory DB with the old agent shape, `_ensure_agent_schema` leaves `mode` and neither `temperature` nor `model_code`. `apply_agent_repo_json_startup` loads `data/admin/agent.json` with its seven modes. A repo row with `mode: "Wild"` is rejected. (Exact script in **Verification**.)

All line numbers are as of sub tip `17e0a8004`. Match on the quoted text; if the text is not there, stop and comment (execution contract).

1. **Header docstring, line 14.** Replace the whole `- agent    — Agent: …` line with:

   ```
   - agent    — Agent: agent_id TEXT PK, content TEXT, model_id TEXT (LLM_MODEL_CONFIG key; brain_setting validated against that model's sizes — AST-1878), brain_setting TEXT (Little|Medium|Big), mode TEXT (AGENT_MODES: Deterministic|Creative — decides thinking + temperature; AST-1948), max_tokens INTEGER, updated_at TIMESTAMP.
   ```

2. **Config import block (lines 103–106).** Replace the line `    infer_brain_setting_from_legacy_model_code,` with `    get_llm_model,`. Directly after the line `    validate_brain_setting_for_model,`, insert `    validate_agent_mode,`. No other import changes.

3. **Replace `_coerce_agent_brain_setting` and `_expose_agent_public`** (lines 132–149, both whole functions) with:

   ```python
   def _coerce_agent_brain_setting(row: Dict[str, Any]) -> str:
       raw = row.get("brain_setting")
       return raw.strip() if isinstance(raw, str) else ""


   def _expose_agent_public(row_dict: Dict[str, Any]) -> Dict[str, Any]:
       """brain_setting authoritative; resolved_model_key = the catalog SKU (None without model_id).
       The SKU does not depend on mode, so rows still awaiting a mode (AST-1950 migration) keep listing."""
       out = dict(row_dict)
       bs = _coerce_agent_brain_setting(out)
       out["brain_setting"] = bs
       mid = out.get("model_id")
       rk = None
       # Legacy rows written before Revert-to-file carry no model yet.
       if mid:
           validate_brain_setting_for_model(mid, bs)
           rk = get_llm_model(mid)["brain_sizes"][bs]["sku"]
       out["resolved_model_key"] = rk
       return out
   ```

   ⚠️ **Decision:** the public view reads the SKU straight from the catalog instead of calling `resolve_model_brain`. The SKU is the same in every mode. `mode` is nullable, and live rows stay NULL until AST-1950 runs, so going through the resolver would make `list_agents` / `get_agent` (and so Manage Agents and every PUT re-GET) fail on any row without a mode. The behavior is otherwise unchanged: an unknown model or size still raises `ValueError` from `validate_brain_setting_for_model`, as `resolve_model_brain` did. `mode` comes through untouched in `out` because both reads SELECT it.

   ⚠️ **Decision:** a blank `brain_setting` now coerces to `""` instead of being guessed from `model_code`. Rows with a `model_id` always have a validated size (every write path checks it), so this only affects model-less legacy rows, which skip the SKU read anyway.

4. **`_validate_agent_repo_json_rows` (lines 669–688).** In the closing `try:` block, directly after `            validate_brain_setting_for_model(str(mid).strip(), str(bs).strip())`, insert:

   ```python
               validate_agent_mode(row["mode"])
   ```

   The existing `except ValueError as e: raise ValueError(f"agent repo JSON row {i}: {e}") from e` wraps it. The key-set check above already requires `mode` (AST-1947 put it in `REPO_ADMIN_JSON_CONFIG`), so `row["mode"]` cannot `KeyError`. A null, empty or unknown mode is rejected by `validate_agent_mode`.

5. **`apply_agent_repo_json_startup` (lines 726–762).**
   - Replace `        temp = row.get("temperature")` with `        mode = row["mode"]`.
   - In the INSERT: column list `temperature` → `mode`, and the tuple `(aid, content, mid, bs, temp, max_t, updated)` → `(aid, content, mid, bs, mode, max_t, updated)`.
   - In the UPDATE: `temperature = ?` → `mode = ?`, and the tuple `(content, mid, bs, temp, max_t, updated, aid)` → `(content, mid, bs, mode, max_t, updated, aid)`.

6. **`_ensure_agent_schema` (lines 5924–5961).**
   - In `CREATE TABLE agent (…)`, delete the `model_code TEXT,` and `temperature REAL,` lines, and insert `mode TEXT,` directly after `brain_setting TEXT,`. The column order is then `agent_id, content, model_id, brain_setting, mode, max_tokens, updated_at`.
   - In the `else:` branch's add-missing list, delete `("model_code", "TEXT"),` and `("temperature", "REAL"),`, and insert `("mode", "TEXT"),` directly after `("brain_setting", "TEXT"),`.
   - Replace the comment line `        # AST-1497: DDL-only — no model_code / brain_setting content backfills on ensure` with:

     ```python
             # AST-1948: mode supersedes the row temperature; model_id is the one model indicator.
             for col_name in ("temperature", "model_code"):
                 if col_name in cols:
                     try:
                         conn.execute(f"ALTER TABLE agent DROP COLUMN {col_name}")
                         conn.commit()
                     except sqlite3.OperationalError as e:
                         if "no such column" not in str(e).lower():
                             raise
             # AST-1497: DDL-only — no mode / brain_setting content backfills on ensure (AST-1950 sets starting modes)
     ```

   ⚠️ **Decision:** use SQLite's native `ALTER TABLE … DROP COLUMN` (SQLite ≥ 3.35; the host has 3.46.1), not the table-rebuild used by `_drop_entity_agent_responses_column` (AST-984). The agent table has no index, foreign key or constraint on either column, so a native drop works and takes 8 lines instead of ~30. The `no such column` catch matches the add loop's `duplicate column name` catch: if two processes ensure at once, the second one's drop is a no-op.

7. **`save_agent` (lines 5964–6020).**
   - Signature: insert `    mode: str,` as the first keyword-only parameter (directly after `    *,`), and delete `    temperature: Optional[float] = None,`.
   - Replace the docstring with `    """Upsert an agent row; mode always required (AST-1948); new rows require brain_setting; model_id (catalog key) validated with it."""`
   - Directly after the docstring, insert `    validate_agent_mode(mode)` (before `mid = …`).
   - INSERT: column list `temperature` → `mode`; tuple `(agent_id, content, mid, str(brain_setting).strip(), temperature, max_tokens, now)` → `(agent_id, content, mid, str(brain_setting).strip(), mode, max_tokens, now)`.
   - UPDATE branch: `sets = ["content = ?", "updated_at = ?"]` → `sets = ["content = ?", "mode = ?", "updated_at = ?"]`, and `params: List[Any] = [content, now]` → `params: List[Any] = [content, mode, now]`.
   - Replace the loop

     ```python
                 for col, val in [("temperature", temperature), ("max_tokens", max_tokens)]:
                     if val is not None:
                         sets.append(f"{col} = ?")
                         params.append(val)
     ```

     with

     ```python
                 if max_tokens is not None:
                     sets.append("max_tokens = ?")
                     params.append(max_tokens)
     ```

8. **`list_agents` (lines 6041–6058).**
   - Docstring → `    """Return all agents including model_id / brain_setting / mode / resolved_model_key."""`
   - In the SELECT, replace `model_code, model_id, brain_setting, temperature, max_tokens, updated_at,` with `model_id, brain_setting, mode, max_tokens, updated_at,`.

9. **`_UPDATE_AGENT_ALLOWED` / `update_agent` (lines 6061–6100).**
   - `_UPDATE_AGENT_ALLOWED = frozenset({"content", "model_id", "brain_setting", "mode", "max_tokens"})`. `temperature` is gone.
   - In `update_agent`, directly after the `if not cols: return 0` block, insert:

     ```python
         if "mode" in cols:
             validate_agent_mode(kwargs["mode"])
     ```

   ⚠️ **Decision:** `update_agent` stays partial at the data layer (it rejects an unknown mode when one is passed). The route makes `mode` required on PUT (Stage 2 step 3, AC 7). Nothing else calls `update_agent` (`rg "update_agent\(" src/ scripts/` → only `api_admin.py`).

**Stage commit:** `code(AST-1948): agent table — mode column + validation, temperature and model_code dropped`

---

## Stage 2: Mode on the call path and admin routes (`agent.py`, `api_admin.py`)

**Done when:** `python3 -c "import src.core.agent, src.ui.api.api_admin"` succeeds. `_agent_llm_route` on `z-ai/glm-4.6` / Little / Creative returns a tier with `thinking is True`, and on a row with no mode it raises `ValueError`. `GET /agents/models` (unwrapped) returns 98 ids and no `default_temperature`. The AC 6 / AC 8 greps are clean on all three files. (Exact checks in **Verification**.)

### `src/core/agent.py`

1. **Replace `_agent_llm_route`** (lines 1822–1831, the whole function) with:

   ```python
   def _agent_llm_route(agent_row: Dict[str, Any]) -> Dict[str, Any]:
       """Agent model_id + brain_setting + mode → resolve_model_brain route (server, SKU, tier). Raises on missing/invalid config."""
       aid = agent_row.get("agent_id")
       model_id = (agent_row.get("model_id") or "").strip()
       if not model_id:
           raise ValueError(f"Agent '{aid}' has no model_id configured.")
       brain_setting = (agent_row.get("brain_setting") or "").strip()
       if not brain_setting:
           raise ValueError(f"Agent '{aid}' has no brain_setting configured.")
       mode = (agent_row.get("mode") or "").strip()
       if not mode:
           raise ValueError(f"Agent '{aid}' has no mode configured.")
       return resolve_model_brain(model_id, brain_setting, mode)
   ```

   ⚠️ **Decision:** no fallback mode. A row without a mode fails loudly, the same way a row with no `brain_setting` does today. `task_llm_server_id_or_none` keeps re-raising for real agents, so the dispatcher stays loud too. Between deploy and the AST-1950 run ("once per environment, right after deploy"), calls on mode-less rows fail with this message instead of quietly picking a mode. A default would be exactly the hidden setting Susan asked to clear out, and it matches AST-1947's no-default `mode` argument.

2. **`do_task` temperature (line 2080).** Replace

   ```python
       agent_temperature = agent_row.get("temperature") if agent_row.get("temperature") is not None else tier["default_temperature"]
   ```

   with

   ```python
       # AST-1948: the agent's mode decides temperature (resolve_model_brain); the agent row has none.
       agent_temperature = tier["temperature"]
   ```

   The `agent_max_tokens` line, the `CRAFT_RUBRIC_UI_TASK_KEYS` block (max-tokens floor + `tier = {**tier, "thinking": False}`), the `max_tokens_floor` block and the `logger.debug("Calling _send_to_server: …")` line stay exactly as they are. `run_adhoc` / `run_adhoc_workbench_test` already take `temperature` from their caller and are unchanged.

### `src/ui/api/api_admin.py`

3. **`list_models` (line 206).** Delete the line `                    "default_temperature": t["default_temperature"],`. Each size then carries `order` and `default_max_tokens`.

4. **`create_agent` (lines 226–249).**
   - Directly after `    brain_setting = (body.get("brain_setting") or "").strip()`, insert:

     ```python
         mode = body.get("mode")
         mode = mode.strip() if isinstance(mode, str) else ""
     ```

   - Replace the required check and its error with:

     ```python
         if not agent_id or not model_id or not brain_setting or not mode:
             return jsonify({"error": "agent_id, model_id, brain_setting and mode are required"}), 400
     ```

   - In the `database.save_agent(...)` call, replace `            temperature=body.get("temperature"),` with `            mode=mode,`. An unknown mode (`"Wild"`) raises `ValueError` from `save_agent`, and the existing `except ValueError` turns it into a 400.

5. **`update_agent` (lines 252–273).**
   - Directly after the 404 block (`return jsonify({"error": f"Agent not found: {agent_id}"}), 404`), insert:

     ```python

         mode = body.get("mode")
         if not isinstance(mode, str) or not mode.strip():
             return jsonify({"error": "mode is required"}), 400
     ```

   - In the `kwargs` comprehension, change the strip tuple `("model_id", "brain_setting")` → `("model_id", "brain_setting", "mode")`, and the key tuple `("content", "model_id", "brain_setting", "temperature", "max_tokens")` → `("content", "model_id", "brain_setting", "mode", "max_tokens")`. An unknown mode raises `ValueError` from `database.update_agent`, and the existing `except ValueError` turns it into a 400.

   ⚠️ **Decision:** PUT requires `mode` on every call, as AC 7 says ("Omitting `mode` … → 400"). The only PUT caller is `AdminAgentPrompts.tsx` `handleEditSave`, which does not send `mode` until AST-1949 lands. So on `ftr`, between this ticket's merge and AST-1949's, editing an agent in the UI returns `400 mode is required`. Creating one returns the create error. That window is part of how the ticket was defined (UI is #3), not a bug in this one.

6. **Task-manager list — `_enrich_tasks` (line 389).** Replace

   ```python
                       route = resolve_model_brain((agent.get("model_id") or "").strip(), brain_setting_eff)
   ```

   with

   ```python
                       route = resolve_model_brain(
                           (agent.get("model_id") or "").strip(), brain_setting_eff, (agent.get("mode") or "").strip()
                       )
   ```

   A mode-less agent lands in the existing `except ValueError` warning branch (a display row with no SKU or cache threshold) instead of failing the screen. That is the branch's documented purpose. The row's `"model_code": resolved_model_key` key (line 460) belongs to the task-manager payload, not the agent public view, and is unchanged.

7. **`_resolve_adhoc` (lines 1542–1548).**
   - Replace the call

     ```python
             route = resolve_model_brain(
                 (agent.get("model_id") or "").strip(), (agent.get("brain_setting") or "").strip()
             )
     ```

     with

     ```python
             route = resolve_model_brain(
                 (agent.get("model_id") or "").strip(),
                 (agent.get("brain_setting") or "").strip(),
                 (agent.get("mode") or "").strip(),
             )
     ```

   - Replace `    temperature = agent["temperature"] if agent.get("temperature") is not None else tier["default_temperature"]` with `    temperature = tier["temperature"]`.

   A mode-less agent returns 400 with the resolver's `Invalid mode '' …` message through the existing `except ValueError`. The returned dict still carries `"temperature": temperature` and `"tier": tier`, so `adhoc_test` → `run_adhoc_workbench_test` is unchanged.

**Stage commit:** `code(AST-1948): agent mode on the call path and admin routes — resolver gets mode, temperature from the tier`

---

## Verification (build-child §7, before each commit)

- **Compile:** `python3 -m py_compile src/data/database.py src/core/agent.py src/ui/api/api_admin.py`
- **Lint:** `ruff check --select F,E9 <touched files>`. ruff is **not installed** on this host (checked at planning). Do what AST-1947 did: `pip install --target /tmp/ruffenv ruff`, then `PYTHONPATH=/tmp/ruffenv python3 -m ruff check --select F,E9 <files>`, with no repo or system change. If that install fails, stop and comment on the parent. Do not commit unlinted (Susan's rule).
- **After Stage 1** (from the repo root):

  ```bash
  python3 - <<'EOF'
  import json, sqlite3
  from src.data import database as d
  c = sqlite3.connect(":memory:"); c.row_factory = sqlite3.Row
  c.execute("CREATE TABLE agent (agent_id TEXT PRIMARY KEY, content TEXT, model_id TEXT, model_code TEXT, "
            "brain_setting TEXT, temperature REAL, max_tokens INTEGER, updated_at TIMESTAMP)")
  d._agent_schema_ensured = False
  d._ensure_agent_schema(c)
  cols = [r[1] for r in c.execute("PRAGMA table_info(agent)")]
  assert "mode" in cols and "temperature" not in cols and "model_code" not in cols, cols
  rows = json.load(open("data/admin/agent.json"))
  d.apply_agent_repo_json_startup(c, rows)
  got = {r["agent_id"]: r["mode"] for r in c.execute("SELECT agent_id, mode FROM agent")}
  assert got == {r["agent_id"]: r["mode"] for r in rows}, got
  for bad in ("Wild", None, ""):
      try:
          d._validate_agent_repo_json_rows([dict(rows[0], mode=bad)])
          raise SystemExit(f"mode {bad!r} accepted")
      except ValueError:
          pass
  pub = d._expose_agent_public({"agent_id": "x", "model_id": "claude", "brain_setting": "Medium", "mode": None})
  assert pub["resolved_model_key"] == "claude-sonnet-4-6" and "model_code" not in pub, pub
  print("stage 1 ok", got)
  EOF
  ```

- **After Stage 2:**

  ```bash
  python3 - <<'EOF'
  import inspect
  from flask import Flask
  from src.core.agent import _agent_llm_route
  import src.ui.api.api_admin as a
  t = _agent_llm_route({"agent_id": "x", "model_id": "z-ai/glm-4.6", "brain_setting": "Little", "mode": "Creative"})["tier"]
  assert t["thinking"] is True and t["thinking_params"] == {"thinking": {"type": "adaptive"}}, t
  t = _agent_llm_route({"agent_id": "x", "model_id": "claude", "brain_setting": "Medium", "mode": "Deterministic"})
  assert t["sku"] == "claude-sonnet-4-6" and t["tier"]["temperature"] == 0.2, t
  try:
      _agent_llm_route({"agent_id": "x", "model_id": "claude", "brain_setting": "Medium", "mode": None})
      raise SystemExit("mode-less row routed")
  except ValueError:
      pass
  with Flask(__name__).app_context():
      models = inspect.unwrap(a.list_models)().get_json()
  assert len(models) == 98, len(models)
  assert not any("default_temperature" in s for m in models.values() for s in m["brain_sizes"].values())
  print("stage 2 ok", len(models))
  EOF
  ```

- **Greps (after Stage 2):**
  - AC 6: `rg -n "default_temperature|brain_setting_for_anthropic_agent_key|admin_brain_setting_catalog|infer_brain_setting_from_legacy_model_code" src/ --glob '!src/ui/frontend/**'` returns nothing. The only remaining `src/` hits should be in `AdminAgentPrompts.tsx`, which is AST-1949's file. Its `temperature` grep is AST-1949's too.
  - AC 8: `rg -n "0\.6\b|0\.2\b" src/core/agent.py src/ui/api/api_admin.py src/data/database.py` returns nothing. The slug grep (`rg -n "apodex/|bytedance/ui-tars|ibm-granite/|inclusionai/|meta/muse|microsoft/|minimax/|sao10k/l3|thedrummer/|z-ai/glm-4|moonshotai/kimi-k2\.[57]" src/ --glob '!src/utils/config.py'`) returns nothing.
  - Leftovers: `rg -n "temperature|model_code" src/data/database.py | rg -v "timesheet|ledger|model_codes|sku=row"` shows no agent-table hit. `rg -n "\"temperature\"\]|get\(\"temperature\"\)" src/core/agent.py src/ui/api/api_admin.py` returns nothing.

## AC traceability

| AC (ticket numbering) | Where |
|---|---|
| **5** Mode drives every call on the wire | Stage 2 step 1 (`_agent_llm_route` → `resolve_model_brain(…, mode)`) + step 2 (`tier["temperature"]`). Thinking flag/payload, SKU and floors come from AST-1947's tier; craft guard + floors unchanged. Wire assertions = Betty's stubbed-client tests in `test_agent.py`. |
| **6** No stray thinking/temperature settings | Stage 1 step 2 (legacy helper import gone), Stage 2 steps 2, 3, 7 (`default_temperature` reads gone). `AdminAgentPrompts.tsx` grep is AST-1949's half. |
| **7** Agent row: mode in, temperature/model_code out | Stage 1 steps 3, 5–9; Stage 2 steps 4–5. Revert = `apply_agent_repo_json_startup` (Stage 1 step 5) via `POST /api/admin/repo_json/revert/agent`. |
| **8** No slug or mode literal outside config | Only `tier["temperature"]` reads; Verification greps. |

## Tests expected to move (Betty, `qa-child`)

These are not edited here, since the test tree is off-limits to engineers. They're listed so the manifest can account for them:

- `tests/component/core/test_agent.py`: any agent-row fixture with `temperature` or without `mode`; any `_agent_llm_route` / `do_task` stub that expects `tier["default_temperature"]` or a two-arg `resolve_model_brain`. New coverage: AC 5's seven wire cases through `do_task` with stubbed clients (OpenRouter glm-4.6 Creative/Deterministic, phi-4 Creative, kimi-k2.6 Little Creative / Big Deterministic, deepseek-v4 Big Creative ≥ 384000, claude Medium Deterministic → Anthropic `claude-sonnet-4-6` at 0.2), plus a mode-less agent → `ValueError`.
- `tests/component/ui/api/test_api_admin.py`: create/update bodies with `temperature`; `list_models` `default_temperature` assertions; agent GET `model_code` assertions; `_resolve_adhoc` temperature. New coverage: AC 7 PUT `mode: "Creative"` round-trip with no `temperature` / `model_code` key; PUT/POST without `mode` or with `"Wild"` → 400; `GET /agents/models` = 98 ids (AST-1947 AC 8 / parent AC 11, now on this sub).
- `tests/component/core/test_repo_admin_json.py`: agent columns / `temperature` assertions and the AST-787 fixture comparison. New coverage: AC 7 schema-ensure on a DB with both old columns (`PRAGMA table_info`), revert from `data/admin/agent.json`, and a repo row with a bad mode rejected.
- These three files have been red on `ftr` since AST-1947 merged (AST-1947 § Sequencing gap). This ticket is what turns them green.

## Estimate

Confirm Chuckles estimate: 5 — agree
