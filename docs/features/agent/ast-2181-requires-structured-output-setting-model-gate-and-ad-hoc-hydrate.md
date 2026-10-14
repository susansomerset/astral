# AST-2181 — "Requires structured output" setting and model gate

- **Linear:** [AST-2181](https://linear.app/astralcareermatch/issue/AST-2181) · parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172) (Enforced structured output for rubric graders)
- **Publish ref:** `origin/sub/AST-2172/AST-2181-structured-output-setting-model-gate`
- **Assignee:** Hedy
- **Canon Scope:** `stat.logging.error`

This is the agent-setting slice of AST-2172. It adds a stored boolean agent setting, `requires_structured_output`, to the `agent` table, the repo seed column tuple and `data/admin/agent.json`. The seed has it `true` for exactly Grace, Lucy and Kent. `GET /api/admin/agents/models` reports each model's structured-output capability. Agent create and update refuse, with a 400 and no write, a save that would leave the setting on with a model whose capability is `None`. Manage Agents gets a "Requires structured output" checkbox, and while it's checked the model picker offers only `enforced` / `advisory` models. Per Chuckles' `[scope-gate]` comment, the ad-hoc test hydrate moved to AST-2180 (already built there). This ticket doesn't touch `adhoc_test`, core grading, or any other part of config. No provider calls.

## Findings that shape this plan

1. **AST-2177 (#2) and AST-2180 (#5) are on `origin/ftr/AST-2172-structured-output-graders`** and this branch carries them. `get_structured_output_capability(model_id)` exists in `src/utils/config.py`. It returns `"advisory"` for `qwen/qwen3-235b-a22b-2507` and `openai/gpt-oss-120b`, and `None` for every other model; it raises `ValueError` on an unknown id.
2. **`provider_allow_fallbacks` is the template.** It's in `_AGENT_SETTING_TYPES` (`database.py`), which feeds `AGENT_SETTING_COLUMNS`. That tuple already drives the public columns, seed validation, `update_agent`'s allowlist and `api_admin._agent_settings_from_body` / the PUT kwargs. So adding the setting to the typed map carries it through every path except four hard-coded spots: `CREATE TABLE`, the migration list, `save_agent`'s parameters, and the `list_agents` SQL. The read-back-as-bool and seed-export bool conversions name `provider_allow_fallbacks` literally; both become a two-name `_AGENT_BOOL_SETTINGS` set.
3. **The setting never reaches a provider call.** `resolve_agent_settings` (`config.py`) builds the request tier from named keys only, so a new entry in `AGENT_SETTING_COLUMNS` can't leak onto the wire.
4. **Revert to file for agents already fails on dev, before this change.** `data/admin/agent.json` (Susan's exports of Oct 6 and Oct 8; identical on `origin/dev`) has two problems. Every row carries keys `brain_setting` (`Big` / `Medium`) and `mode` (`Deterministic` / `Creative`), which are not in the seed column tuple. And every row has `provider_allow_fallbacks: 1` (int), which `_check_agent_setting` rejects as not bool. `_validate_agent_repo_json_rows` therefore raises on row 1. Export only writes tuple columns, so those two keys exist only as hand edits in the repo file. See the decision under Stage 1.
5. **Verified at plan time.** I drafted the full change, ran it and then restored the tree. The tree was clean before both patches were checked with `git apply --check`. Results:
   - `py_compile` passes on all three Python files.
   - `ruff` total on them is unchanged (858 before, 858 after).
   - `npx tsc -b --noEmit` passes, using the main checkout's `node_modules` through a temporary symlink.
   - A scratch smoke test passed 4/4 (deleted, never committed). It covered `/agents/models` capability, the create gate, the update gate, unknown model → 400, data-layer round-trip, seed export as bool, and the seed apply landing Lucy `true` / Ruth `false` once Finding 4's defects are normalized in memory.
6. **Expected test churn (Betty):** run on the draft, the agent-related component files show exactly 3 new failures versus the pre-change tree. All three are contract updates rather than regressions:
   - `test_api_admin.py::TestAdminConfigAndAgents::test_list_models_is_flat_catalog_with_default_output_budget`: an exact dict without the new key.
   - `test_agents.py::TestAst782AgentRepoJsonStartup::test_apply_upserts_updates_and_deletes_absent_agents` and `test_agents.py::TestAst1878AgentModelField::test_repo_json_requires_known_model`: seed fixtures without the new key.

   The other 195 failures in those files fail identically on the pre-change tree.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `requires_structured_output` added to `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` (after `provider_sort`) | utils |
| `src/data/database.py` | Header line; `_AGENT_SETTING_TYPES` entry; `_AGENT_BOOL_SETTINGS`; bool read-back; `CREATE TABLE` + migration column; `save_agent` param, settings entry, new-row default `False`; `list_agents` SQL; seed-export bool loop | data |
| `data/admin/agent.json` | `requires_structured_output` on every row: `true` for `job_analyst_grace`, `job_filter_lucy`, `antagonist_kent`, `false` for the other 7 | data |
| `src/ui/api/api_admin.py` | Import `get_structured_output_capability`; new `_structured_output_gate`; `list_models` adds `structured_output_capability`; gate in `create_agent` and `update_agent` | ui |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | `ModelRow` / `Agent` / `SettingsForm` fields; empty / from-agent / body mapping; checkbox under the Model select; picker filtered while checked | ui |

## Stage 1: Setting, seed, API gate

**Done when:**
- `git apply` of Appendix A succeeds, and `py_compile` passes on the three Python files.
- `ruff check src/data/database.py src/ui/api/api_admin.py src/utils/config.py` reports the same total as before the stage (858 at plan time).
- The step 4 check prints `stage1 ok`.

1. Record the ruff baseline: `ruff check --no-cache src/data/database.py src/ui/api/api_admin.py src/utils/config.py 2>&1 | sed -E 's/\x1b\[[0-9;]*m//g' | grep '^Found'`.
2. Save **Appendix A** verbatim (everything between its fences, plus a trailing newline) to `debug/spikes/AST-2181/stage1.patch` and run `git apply debug/spikes/AST-2181/stage1.patch` from the repo root. If `git apply --check` fails, the code has drifted from the plan: **stop** and post the blocked comment (Execution contract). Don't hand-merge.
3. `python3 -m py_compile src/data/database.py src/ui/api/api_admin.py src/utils/config.py`, then re-run step 1's ruff command; the total must equal the baseline.
4. Run from the repo root, using the main checkout's venv (`/home/susan/astral/.venv/bin/python`) with `PYTHONPATH=.`:
   ```bash
   PYTHONPATH=. /home/susan/astral/.venv/bin/python - <<'EOF'
   import json, tempfile, pathlib
   from src.data import database
   from src.utils.config import REPO_ADMIN_JSON_CONFIG as R
   assert "requires_structured_output" in R["tables"]["agent"]["columns"]
   assert "requires_structured_output" in database.AGENT_SETTING_COLUMNS
   rows = json.load(open("data/admin/agent.json"))
   assert all(isinstance(r["requires_structured_output"], bool) for r in rows)
   assert sorted(r["agent_id"] for r in rows if r["requires_structured_output"]) == ["antagonist_kent", "job_analyst_grace", "job_filter_lucy"]
   database.DB_PATH = pathlib.Path(tempfile.mkdtemp()) / "t.db"
   database._agent_schema_ensured = False
   database.save_agent("a1", "c", model_id="qwen/qwen3-235b-a22b-2507")
   assert database.get_agent("a1")["requires_structured_output"] is False
   database.update_agent("a1", requires_structured_output=True)
   assert database.get_agent("a1")["requires_structured_output"] is True
   assert database.list_agents()[0]["requires_structured_output"] is True
   print("stage1 ok")
   EOF
   ```
5. Commit `code(AST-2181): requires_structured_output setting — column, seed, models capability, save gate`. Add only the four Stage 1 files, then push (Execution contract).

What Appendix A does, so a reviewer can read it without the patch:
- **`database.py`:**
  - `"requires_structured_output": (bool,)` goes into `_AGENT_SETTING_TYPES`, with the comment that it gates model choice and `resolve_agent_settings` never reads it.
  - `_AGENT_BOOL_SETTINGS = frozenset({"provider_allow_fallbacks", "requires_structured_output"})` replaces the literal name in `_agent_setting_from_db` and in `fetch_agent_repo_json_export_rows`.
  - `requires_structured_output INTEGER` is added to `CREATE TABLE agent` and to the `_ensure_agent_schema` ALTER list.
  - `save_agent` gets `requires_structured_output: bool | None = None` and the matching settings-dict entry; a new row defaults it to `False` next to the existing fallbacks-`True` default.
  - The column is added to the `list_agents` SELECT, and the module header line names the new column.
- **`api_admin.py`:**
  - `_structured_output_gate(requires, model_id) -> str | None` returns the 400 text when `requires` is truthy, `model_id` is set, and `get_structured_output_capability(model_id) is None`.
  - `list_models` adds `"structured_output_capability": get_structured_output_capability(mid)`.
  - `create_agent` gates on the body's flag and model before `save_agent`.
  - `update_agent` keeps the row it already fetches for the 404 (`current`) and gates on the post-PUT values: body keys win, absent keys keep the stored ones. It runs before `database.update_agent`, inside the existing `try`, so an unknown `model_id` still comes back 400.

⚠️ **Decision (stored setting in the typed map):** the parent Technical scope says "typed settings map … read back as bool like `provider_allow_fallbacks`". The map is also where "plain call settings" live, but Finding 3 shows nothing derives the provider request from that tuple, so the setting is stored and exposed without being sent. A separate non-call-setting list would touch the same paths twice.

⚠️ **Decision (new rows default `False`):** a new agent created without the key gets `False`, not NULL, mirroring how fallbacks default to `True` at insert. That keeps the setting two-valued for the UI and the gate. Live rows that exist when the migration adds the column stay NULL until Revert to file or a save (no content backfill on ensure, AST-1497). NULL reads as "off" everywhere: the gate tests truthiness, and the UI uses `?? false`.

⚠️ **Decision (gate lives in the API, not the data layer):** Scope puts the gate on "agent create/update" in `api_admin.py` and gives `database.py` only the column. So `save_agent` / `update_agent` and Revert to file don't gate. Seed values are reviewed in the repo, and the three seeded `true` rows use `advisory` models.

⚠️ **Decision (only `None` is refused):** per the parent's "Advisory hosts are allowed … only `none` is excluded". The 400 names the model and says to pick an enforced or advisory model or turn the setting off. It's a JSON error returned by the handler with no exception thrown and nothing logged, the same as the existing `ValueError` → 400 paths (`stat.logging.error` Notes: "UI APIs return JSON errors").

⚠️ **Decision (pre-existing seed defects, Finding 4) — Susan, please confirm or flip:** this plan **leaves `brain_setting`, `mode` and `provider_allow_fallbacks: 1` exactly as they are**. It only adds the new key, so Susan's `Big` / `Deterministic` notes aren't deleted on an assumption. Consequence: **Revert to file for agents keeps failing, as it does on dev today**, so the seeded `true` values don't reach the database that way. At UAT, AC 10's `GET /api/admin/agents/job_filter_lucy` → `true` comes from ticking the new checkbox on Grace, Lucy and Kent in Manage Agents. I asked Susan in chat at plan time (2026-10-14) and she skipped the question.
- **To flip it:** say "drop them". Stage 1 then gains a step 2a that rewrites `data/admin/agent.json` as `[dict(sorted({k: (bool(v) if k == "provider_allow_fallbacks" else v) for k, v in r.items() if k not in ("brain_setting", "mode")}.items())) for r in rows]`, written as `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"`.
- **What that does:** Revert to file then passes validation. The plan-time smoke test proved the apply lands Lucy `true` / Ruth `false` with exactly that normalization.

## Stage 2: Manage Agents checkbox and filtered picker

**Done when:** `git apply` of Appendix B succeeds, and `cd src/ui/frontend && npx tsc -b --noEmit` exits 0. In the browser, ticking the checkbox on an agent removes every model whose capability is null from the Model select, unticking restores them, and saving Lucy with an incapable model while ticked shows the API's 400 text in the error toast.

1. Save **Appendix B** verbatim to `debug/spikes/AST-2181/stage2.patch` and `git apply` it (drift → stop, as in Stage 1).
2. `cd src/ui/frontend && npx tsc -b --noEmit`. If this worktree has no `node_modules`, run `npm ci` there first. `node_modules` is gitignored.
3. Commit `code(AST-2181): Manage Agents — requires structured output checkbox, capable-only model picker` and push.

What Appendix B does:
- `ModelRow.structured_output_capability: "enforced" | "advisory" | null`, `Agent.requires_structured_output?: boolean | null` and `SettingsForm.requires_structured_output: boolean` are added.
- `EMPTY_SETTINGS` sets it `false`, `settingsFromAgent` reads `?? false`, and `settingsBody` always sends it. So every save carries the flag, and the API gate sees the edited value.
- In `AgentSettingsFields`:
  - `capable(id)` is true unless the box is ticked and that model's capability is null, and the option list is `byOrder(models).filter(capable)`.
  - When the agent's **current** model is incapable and the box is ticked, it stays in the select as one flagged option, `<label> — no structured output`. That way the select never silently displays a different model than the one that would be saved.
  - The checkbox renders directly under the Model select.

⚠️ **Decision (flagged current model):** AC 10's "picker does not offer that model" is met for choice: no incapable model appears in the list of alternatives. The one exception is the agent's current value, shown flagged, so the form stays truthful and the save surfaces the server's 400 instead of quietly switching models. Without it, a `<select>` whose value has no matching option renders the first option while state still holds the old id.

⚠️ **Decision (no list column):** Scope asks for the checkbox on the editor and the filtered picker. A "Structured" column in the agents grid isn't in it, so none is added.

## Canon check (`stat.logging.error`)

No new exception paths. `_structured_output_gate` returns text and the handlers return a 400 JSON body. `get_structured_output_capability`'s `ValueError` on an unknown model is caught by the handlers' existing `except ValueError` → 400, the same as the data layer's own model check. No `print`, no log-and-re-raise. The data layer adds a column and raises (via `_check_agent_setting`) without logging, as before.

## Execution contract

The plan is binding. Steps run in order and stages run in order. No added files, modules or dependencies; nothing committed from `debug/`. If a step is ambiguous, a patch doesn't apply, or a check fails, stop and comment on the parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage ends in one `code(AST-2181): …` commit on the epic worktree, published with `git push origin HEAD:sub/AST-2172/AST-2181-structured-output-setting-model-gate`. Compile and lint before every commit. Run `sync-child.sh` with `--ftr AST-2172-structured-output-graders`; the bare `--ftr AST-2172` doesn't match the parent ref on origin, so it skips the ftr merge.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Appendix A — Stage 1 patch

```diff
diff --git a/data/admin/agent.json b/data/admin/agent.json
index bca681a2e..cb22ecba6 100644
--- a/data/admin/agent.json
+++ b/data/admin/agent.json
@@ -12,6 +12,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": "high",
+    "requires_structured_output": true,
     "temperature": 0.1,
     "updated_at": "2026-10-08 00:08:28"
   },
@@ -28,6 +29,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": "high",
+    "requires_structured_output": false,
     "temperature": 0.7,
     "updated_at": "2026-10-04 03:56:24"
   },
@@ -44,6 +46,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": null,
+    "requires_structured_output": false,
     "temperature": 0.7,
     "updated_at": "2026-10-04 03:56:24"
   },
@@ -60,6 +63,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": "low",
+    "requires_structured_output": false,
     "temperature": 0.1,
     "updated_at": "2026-10-04 03:56:24"
   },
@@ -76,6 +80,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": null,
+    "requires_structured_output": false,
     "temperature": 0.7,
     "updated_at": "2026-10-04 03:56:24"
   },
@@ -92,6 +97,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": null,
+    "requires_structured_output": false,
     "temperature": 0,
     "updated_at": "2026-10-04 03:56:24"
   },
@@ -108,6 +114,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": null,
+    "requires_structured_output": false,
     "temperature": 0.6,
     "updated_at": "2026-10-04 04:41:38"
   },
@@ -124,6 +131,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": "low",
+    "requires_structured_output": true,
     "temperature": 0,
     "updated_at": "2026-10-04 03:56:24"
   },
@@ -140,6 +148,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": "high",
+    "requires_structured_output": false,
     "temperature": 0,
     "updated_at": "2026-10-06 04:00:23"
   },
@@ -156,6 +165,7 @@
     "provider_sort": null,
     "quantization": null,
     "reasoning_effort": "low",
+    "requires_structured_output": true,
     "temperature": 0.1,
     "updated_at": "2026-10-08 00:21:12"
   }
diff --git a/src/data/database.py b/src/data/database.py
index ae4f1731e..2cb670d7f 100644
--- a/src/data/database.py
+++ b/src/data/database.py
@@ -11,7 +11,7 @@ Tables used (inventory):
 - job       — Tracker: astral_job_id, company_id (nullable real employer; AST-1701), candidate_id (required owning candidate; AST-1598 / AST-1594), company_job_id, job_title, job_link, job_data, state, state_history, batch_id, source (company|meteorite parent/track; AST-1701 repurpose of AST-1469) + source_entity_id (company short_name or meteorite id text), etc.
 - meteorite — Ingress staging spine (AST-1557): one row per prospective job after classify fan-out; `state` from `METEORITE_STATES`; claim via `batch_id` / `batch_created_at`; eligibility count via `count_meteorites_unclaimed_in_states`; reverse lookup via `get_meteorite_by_astral_job_id(astral_job_id)`; candidate-scoped listing via `list_meteorites_for_candidate(candidate_id)` (+ landed `job_state`, AST-1974); listing-href fallback reverse lookup via `get_meteorite_link_by_astral_job_id(astral_job_id)` (AST-1694 — link column only; not AST-1685 provenance); columns id, candidate_id, source_kind, source_id, source_ref, state, content, classify_outcome, link, electronic_contact (AST-1689; config literal from AST-1688), job_title, employer_name (AST-1713; Ruth stage_meteorite response keys), astral_job_id, estelle_thread_ts, estelle_notified_at, nag_count, error, batch_id, batch_created_at, created_at, updated_at, state_changed_at.
 - candidate — Candidate: state, state_history JSON array, candidate_data JSON (contact/context/artifacts + meta), first/last/full/pronouns TEXT columns, candidate_api_key TEXT (legacy — not read or written since AST-1878), api_keys TEXT JSON array [{"server": LLM_SERVER_CONFIG id, "key": Fernet ciphertext}] — at most one entry per server; hydrated as candidate_api_keys {server: plaintext} (AST-1901), batch_id, batch_created_at (null/empty = unclaimed; AST-1258).
-- agent    — Agent: agent_id TEXT PK, content TEXT, model_id TEXT (LLM_MODEL_CONFIG key), max_tokens INTEGER, plain call settings sent as stored — quantization TEXT, temperature REAL, reasoning_effort TEXT, provider_allow_fallbacks INTEGER (bool), provider_only / provider_ignore TEXT (JSON array of provider slugs), provider_sort TEXT (AST-1955) — updated_at TIMESTAMP.
+- agent    — Agent: agent_id TEXT PK, content TEXT, model_id TEXT (LLM_MODEL_CONFIG key), max_tokens INTEGER, plain call settings sent as stored — quantization TEXT, temperature REAL, reasoning_effort TEXT, provider_allow_fallbacks INTEGER (bool), provider_only / provider_ignore TEXT (JSON array of provider slugs), provider_sort TEXT (AST-1955), requires_structured_output INTEGER (bool; gates model choice, never sent — AST-2172) — updated_at TIMESTAMP.
 - agent_task — Task prompt config with versioning: task_key_uuid TEXT PK, task_key TEXT, current INTEGER (1=active), agent_id TEXT, seven prompt segments (`user_prompt`; `cache_prompt` = Anthropic cache block A; `cache_prompt_b|c|d` = blocks B–D; `nocache_prompt`; `system_prompt` per-task override, empty = use agent content at runtime), `run_next`, `task_group_order TEXT`, `task_group_name TEXT`, `task_seq REAL`, `task_name TEXT` (UI grouping metadata, global per task_key), `updated_at`. Any segment edit (all seven) retires prior row + inserts new `current=1`.
 - anthropic_timesheets — Anthropic-only token/cost ledger mirror: anthropic_req_id TEXT UNIQUE, same metric columns as agent_timesheets (batch_id, token counts, calc_cost_*, agent_performance, failure_note, created_at).
 - agent_timesheets — Unified token/cost ledger for all LLM providers: agent_req_id TEXT UNIQUE (vendor request id), same metric columns as anthropic_timesheets, plus nullable platform columns (AST-1965: platform_cost — NULL = not reconciled, native_tokens_prompt/_completion/_cached/_reasoning, host, platform_reconciled_at) set by update_timesheet_platform; sum_cost_by_batch prefers platform_cost per row.
@@ -144,10 +144,14 @@ _AGENT_SETTING_TYPES: Dict[str, tuple] = {
     "provider_only": (list,),
     "provider_ignore": (list,),
     "provider_sort": (str,),
+    # Not a call setting: gates which models the agent may use (AST-2172); resolve_agent_settings never reads it.
+    "requires_structured_output": (bool,),
 }
 AGENT_SETTING_COLUMNS: Tuple[str, ...] = tuple(_AGENT_SETTING_TYPES)
 # List settings live in SQLite (and the repo seed) as JSON-array text.
 _AGENT_LIST_SETTINGS = frozenset({"provider_only", "provider_ignore"})
+# Bool settings live in SQLite as INTEGER and read back as bool.
+_AGENT_BOOL_SETTINGS = frozenset({"provider_allow_fallbacks", "requires_structured_output"})
 _AGENT_PUBLIC_COLUMNS = ("agent_id", "content", "model_id", "max_tokens", *AGENT_SETTING_COLUMNS, "updated_at")
 
 
@@ -172,7 +176,7 @@ def _agent_setting_from_db(name: str, value: Any) -> Any:
         return None
     if name in _AGENT_LIST_SETTINGS:
         return json.loads(value)
-    return bool(value) if name == "provider_allow_fallbacks" else value
+    return bool(value) if name in _AGENT_BOOL_SETTINGS else value
 
 
 def _check_agent_model_id(model_id: Any) -> None:
@@ -752,8 +756,9 @@ def fetch_agent_repo_json_export_rows(conn: sqlite3.Connection) -> List[Dict[str
         f"SELECT {cols_sql} FROM agent ORDER BY agent_id",
     ).fetchall()]
     for row in rows:
-        if row["provider_allow_fallbacks"] is not None:
-            row["provider_allow_fallbacks"] = bool(row["provider_allow_fallbacks"])
+        for name in _AGENT_BOOL_SETTINGS:
+            if row[name] is not None:
+                row[name] = bool(row[name])
     return rows
 
 
@@ -6460,6 +6465,7 @@ def _ensure_agent_schema(conn: sqlite3.Connection) -> None:
                 provider_only TEXT,
                 provider_ignore TEXT,
                 provider_sort TEXT,
+                requires_structured_output INTEGER,
                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
             )
         """)
@@ -6476,6 +6482,7 @@ def _ensure_agent_schema(conn: sqlite3.Connection) -> None:
             ("provider_only", "TEXT"),
             ("provider_ignore", "TEXT"),
             ("provider_sort", "TEXT"),
+            ("requires_structured_output", "INTEGER"),
         ]:
             if col_name not in cols:
                 try:
@@ -6510,9 +6517,10 @@ def save_agent(
     provider_only: Optional[List[str]] = None,
     provider_ignore: Optional[List[str]] = None,
     provider_sort: Optional[str] = None,
+    requires_structured_output: bool | None = None,
 ) -> None:
     """Upsert an agent row (AST-1955). Settings are type-checked only; on an existing row None leaves a column as is.
-    New rows default provider_allow_fallbacks to True."""
+    New rows default provider_allow_fallbacks to True and requires_structured_output to False."""
     settings: Dict[str, Any] = {
         "quantization": quantization,
         "temperature": temperature,
@@ -6521,6 +6529,7 @@ def save_agent(
         "provider_only": provider_only,
         "provider_ignore": provider_ignore,
         "provider_sort": provider_sort,
+        "requires_structured_output": requires_structured_output,
     }
     for name, value in settings.items():
         _check_agent_setting(name, value)
@@ -6540,6 +6549,8 @@ def save_agent(
                 # Default true is applied here, not as a SQL DEFAULT (no backfill of live rows on ensure).
                 if settings["provider_allow_fallbacks"] is None:
                     settings["provider_allow_fallbacks"] = True
+                if settings["requires_structured_output"] is None:
+                    settings["requires_structured_output"] = False
                 cols = ["agent_id", "content", "model_id", "max_tokens", *settings, "updated_at"]
                 vals = [agent_id, content, mid, max_tokens,
                         *(_agent_setting_to_db(n, v) for n, v in settings.items()), now]
@@ -6592,7 +6603,8 @@ def list_agents() -> List[Dict[str, Any]]:
             rows = conn.execute("""
                 SELECT agent_id, LENGTH(content) AS content_length,
                        model_id, max_tokens, quantization, temperature, reasoning_effort,
-                       provider_allow_fallbacks, provider_only, provider_ignore, provider_sort, updated_at,
+                       provider_allow_fallbacks, provider_only, provider_ignore, provider_sort,
+                       requires_structured_output, updated_at,
                        (SELECT COUNT(*) FROM agent_task WHERE agent_task.agent_id = agent.agent_id) AS task_count
                 FROM agent ORDER BY agent_id
             """).fetchall()
diff --git a/src/ui/api/api_admin.py b/src/ui/api/api_admin.py
index fa8cb57b1..bc179f756 100644
--- a/src/ui/api/api_admin.py
+++ b/src/ui/api/api_admin.py
@@ -57,6 +57,7 @@ from src.utils.config import (
     BUILD_CONFIG,
     LLM_MODEL_CONFIG,
     get_llm_server,
+    get_structured_output_capability,
     resolve_agent_settings,
     get_manage_agents_tokens,
     get_manage_tasks_chain_tokens,
@@ -146,6 +147,18 @@ def _agent_settings_from_body(body: Dict[str, Any]) -> Dict[str, Any]:
     return {k: body[k] for k in AGENT_SETTING_COLUMNS if k in body}
 
 
+def _structured_output_gate(requires: Any, model_id: Any) -> str | None:
+    """400 text when the agent requires structured output and its model can't take a forced tool (AST-2172).
+    Only None capability is refused — "advisory" hosts are allowed, the grade_schema light check covers them.
+    Raises ValueError on an unknown model id (callers turn it into a 400, same as the data layer)."""
+    if requires and model_id and get_structured_output_capability(model_id) is None:
+        return (
+            f"model {model_id!r} does not support structured output — "
+            "pick an enforced or advisory model, or turn off requires_structured_output"
+        )
+    return None
+
+
 @admin_bp.route("/agents")
 @require_admin
 def list_agents():
@@ -212,6 +225,8 @@ def list_models():
             "server_id": m["server"],
             "server_label": get_llm_server(m["server"])["label"],
             "default_max_tokens": m["default_max_tokens"],
+            # "enforced" | "advisory" | None — the Manage Agents picker hides None while the agent requires it (AST-2172).
+            "structured_output_capability": get_structured_output_capability(mid),
         }
         for i, (mid, m) in enumerate(LLM_MODEL_CONFIG.items())
     })
@@ -237,6 +252,9 @@ def create_agent():
     if database.get_agent(agent_id):
         return jsonify({"error": f"Agent '{agent_id}' already exists"}), 409
     try:
+        gate = _structured_output_gate(body.get("requires_structured_output"), model_id)
+        if gate:
+            return jsonify({"error": gate}), 400
         # Data layer checks model_id against the catalog and type-checks the settings (AST-1955).
         database.save_agent(
             agent_id,
@@ -255,7 +273,8 @@ def create_agent():
 @require_admin
 def update_agent(agent_id):
     body = request.get_json(silent=True) or {}
-    if not database.get_agent(agent_id):
+    current = database.get_agent(agent_id)
+    if not current:
         return jsonify({"error": f"Agent not found: {agent_id}"}), 404
 
     kwargs = {
@@ -266,6 +285,13 @@ def update_agent(agent_id):
     if not kwargs:
         return jsonify({"error": "No updatable fields provided"}), 400
     try:
+        # Gate on the row as it would be after this PUT: body values win, absent keys keep the stored ones.
+        gate = _structured_output_gate(
+            kwargs.get("requires_structured_output", current.get("requires_structured_output")),
+            kwargs.get("model_id", current.get("model_id")),
+        )
+        if gate:
+            return jsonify({"error": gate}), 400
         # update_agent checks model_id and type-checks the settings before its UPDATE (AST-1955).
         database.update_agent(agent_id, **kwargs)
     except ValueError as e:
diff --git a/src/utils/config.py b/src/utils/config.py
index 5eee1e598..609326c4e 100644
--- a/src/utils/config.py
+++ b/src/utils/config.py
@@ -4917,6 +4917,7 @@ REPO_ADMIN_JSON_CONFIG = {
                 "provider_only",
                 "provider_ignore",
                 "provider_sort",
+                "requires_structured_output",
                 "updated_at",
             ),
         },
```

## Appendix B — Stage 2 patch

```diff
diff --git a/src/ui/frontend/src/pages/AdminAgentPrompts.tsx b/src/ui/frontend/src/pages/AdminAgentPrompts.tsx
index 2f6115fb8..f9cf36b68 100644
--- a/src/ui/frontend/src/pages/AdminAgentPrompts.tsx
+++ b/src/ui/frontend/src/pages/AdminAgentPrompts.tsx
@@ -18,6 +18,8 @@ interface ModelRow {
   server_id: string
   server_label: string
   default_max_tokens: number
+  /** Forced-tool schema support (AST-2172); null = can't take one, hidden while the agent requires structured output. */
+  structured_output_capability: "enforced" | "advisory" | null
 }
 type ModelCatalog = Record<string, ModelRow>
 
@@ -38,6 +40,7 @@ interface Agent {
   provider_only?: string[] | null
   provider_ignore?: string[] | null
   provider_sort?: string | null
+  requires_structured_output?: boolean | null
   max_tokens?: number
   task_count?: number
   updated_at?: string
@@ -53,12 +56,13 @@ interface SettingsForm {
   provider_only: string
   provider_ignore: string
   provider_sort: string
+  requires_structured_output: boolean
 }
 
 // New agents start with fallbacks on (the data layer's new-row default) and everything else empty.
 const EMPTY_SETTINGS: SettingsForm = {
   quantization: "", temperature: "", reasoning_effort: "", provider_allow_fallbacks: true,
-  provider_only: "", provider_ignore: "", provider_sort: "",
+  provider_only: "", provider_ignore: "", provider_sort: "", requires_structured_output: false,
 }
 
 function settingsFromAgent(a: Agent): SettingsForm {
@@ -71,6 +75,7 @@ function settingsFromAgent(a: Agent): SettingsForm {
     provider_only:            (a.provider_only ?? []).join(", "),
     provider_ignore:          (a.provider_ignore ?? []).join(", "),
     provider_sort:            a.provider_sort ?? "",
+    requires_structured_output: a.requires_structured_output ?? false,
   }
 }
 
@@ -90,6 +95,7 @@ function settingsBody(f: SettingsForm): Record<string, unknown> {
     provider_only:            slugList(f.provider_only),
     provider_ignore:          slugList(f.provider_ignore),
     provider_sort:            f.provider_sort.trim() || null,
+    requires_structured_output: f.requires_structured_output,
   }
 }
 
@@ -486,6 +492,10 @@ function AgentSettingsFields({
 }) {
   const noModelMatch = !!modelId && !models[modelId]
   const defaultMax = models[modelId]?.default_max_tokens
+  // While the agent requires structured output, only models that can take a forced tool are offered (AST-2172).
+  const capable = (id: string) => !settings.requires_structured_output || models[id].structured_output_capability != null
+  // The current model stays visible (flagged) when it falls out of the list, so the select never silently shows another.
+  const incapableCurrent = !noModelMatch && !!modelId && !capable(modelId)
   // One text input per string setting; key is the SettingsForm field it edits.
   const text = (key: keyof SettingsForm, label: string, placeholder: string) => (
     <div className="dep-field" style={{ flex: 1 }}>
@@ -506,10 +516,19 @@ function AgentSettingsFields({
         <select className="dep-input" value={modelId} onChange={e => onModelChange(e.target.value)}>
           {noModelMatch ? <option value={modelId}>— (unknown model) —</option> : null}
           {modelId === "" ? <option value="">— choose model —</option> : null}
-          {byOrder(models).map(id => (
+          {incapableCurrent ? <option value={modelId}>{models[modelId].label} — no structured output</option> : null}
+          {byOrder(models).filter(capable).map(id => (
             <option key={id} value={id}>{models[id].label}</option>
           ))}
         </select>
+        <label className="dep-field-label">
+          <input
+            type="checkbox"
+            checked={settings.requires_structured_output}
+            onChange={e => onSettingsChange({ ...settings, requires_structured_output: e.target.checked })}
+          />{" "}
+          Requires structured output
+        </label>
       </div>
       <div style={{ display: "flex", gap: 12 }}>
         <div className="dep-field" style={{ flex: 1 }}>
```

## Joan validate

**Ticket:** AST-2181
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `origin/sub/AST-2172/AST-2181-structured-output-setting-model-gate` @ `70018bafb`

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| `stat.logging.error` | A | | |

## Traceability

**10** → Stage 1 (`list_models` + `structured_output_capability`, `_structured_output_gate` on create/update) + Stage 2 (checkbox, `capable` filter, flagged current model). **10a** → Appendix A `agent.json` keys + Stage 1 step 4 assert on three `true` agents. Parent AC 1–9, 11 / 10b N/A. Scope-gate: no `adhoc_test` (AST-2180); `REPO_ADMIN_JSON_CONFIG` agent column lands here with DB + seed (moved from AST-2177).

## Findings

### discuss

- **Location:** Stage 1 — Finding 4 / pre-existing seed defects  
  **Finding:** `brain_setting`, `mode`, and `provider_allow_fallbacks: 1` keep Revert to file failing (same as dev today). Plan only adds `requires_structured_output` to the repo file; **DB rows are not seeded `true` via Revert** until Susan normalizes or toggles in Manage Agents.  
  **Recommendation:** **Susan must choose** before UAT closes AC **10**: (a) “drop them” + step 2a normalization so Revert lands 10a in DB, or (b) accept manual checkbox on Grace/Lucy/Kent for `GET …/job_filter_lucy` → `true`. Plan documents both; neither is a plan defect.

- **Location:** Stage 2 — flagged incapable current model  
  **Finding:** AC **10** “picker does not offer that model” is met for **alternatives**; current incapable model stays visible with “— no structured output” so save hits API 400 instead of silent model swap.  
  **Recommendation:** Proceed; matches AC intent and the decision block.

- **Location:** Capability registry (AST-2177)  
  **Finding:** Only spiked OpenRouter slugs are `advisory`; most catalog entries are `null`, so a checked box narrows the picker sharply until more slugs are spiked.  
  **Recommendation:** Expected epic behavior; not AST-2181 scope creep.

### acceptable

- **Location:** Scope / Boundaries  
  **Finding:** Matches amended Description: `config.py` column tuple only; `database.py`, `agent.json`, `api_admin` (models + create/update gate), `AdminAgentPrompts.tsx`; no core grading, no `adhoc_test`.  
  **Recommendation:** None.

- **Location:** `stat.logging.error`  
  **Finding:** Gate returns JSON 400 without throw; unknown model stays existing `ValueError` → 400; data layer unchanged on logging; no `print` / log-and-re-raise.  
  **Recommendation:** None.

- **Location:** Setting plumbing  
  **Finding:** Mirrors `provider_allow_fallbacks` pattern (`_AGENT_SETTING_TYPES`, `_AGENT_BOOL_SETTINGS`, migration, `list_agents`, export bool loop); `resolve_agent_settings` does not read the new key (Finding 3). Gate only rejects `None` capability; `advisory` allowed per parent Discussion.

- **Location:** Verification  
  **Finding:** Appendix patches + stage checks; Betty churn enumerated (3 contract updates); sync `--ftr AST-2172-structured-output-graders`.

### fix-now

(none)

## R6 (condensed)

- Parent FS §3 (stored setting), §10 model gate, Discussion (stored not derived; only `none` excluded) reflected in API + UI.  
- Gate in API layer (not DB) is consistent with Scope and seed review.  
- Plan Discuss: **0** rounds; **Plan Ready**, assignee Joan.

context_tokens≈115000

---

## Review

Build on `origin/sub/AST-2172/AST-2181-structured-output-setting-model-gate`:

- `267cc83e2` Stage 1: Appendix A applied verbatim to `config.py`, `database.py`, `agent.json` and `api_admin.py`.
- `caafda77c` Stage 2: Appendix B applied verbatim to `AdminAgentPrompts.tsx`.

Checks:
- `py_compile` passes on the three Python files.
- `ruff` total is unchanged (858 before, 858 after).
- The Stage 1 step 4 check prints `stage1 ok`.
- `npx tsc -b --noEmit` exits 0.
- `validate-sub-log.sh --stage=build` is ok.
- No provider calls.

Schema audit (build-child §8): every `agent` INSERT/UPDATE builds its column list dynamically — seed apply, `save_agent`, `update_agent` — so the new column needs no fixed-count edit. The Stage 1 check exercised `save_agent`, `update_agent` and `list_agents`.

Not run here: the Stage 2 in-browser check (picker filter, 400 toast). There's no browser session on this host, so that's for Susan at UAT.

Seed decision (Finding 4): Susan hasn't said "drop them", so the default is built. `brain_setting`, `mode` and `provider_allow_fallbacks: 1` are untouched, and Revert to file for agents still fails as it does on dev. AC 10's Lucy `true` comes from the checkbox at UAT.

For qa-child: expect the 3 contract updates from Finding 6: the exact `list_models` dict, and two seed fixtures missing `requires_structured_output`. Coverage for AC 10 / 10a can follow the plan's scratch smoke test: models capability, create and update gate (400, row unchanged), unknown model → 400, bool round-trip, and the seed keys.

## Radia review


**Ticket:** AST-2181  
**Publish ref:** `8a35a745f606b427b52738051835460bafcc34a4` (`origin/sub/AST-2172/AST-2181-structured-output-setting-model-gate`)  
**Corpus:** `b7ab2203048ce0beb2869a12200ab7fa696c8066` (not DIRTY)  
**Overall:** CLEAN  

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| stat.logging.error | A | | |

Gate failures return JSON **400** without throw; unknown model stays `ValueError` → **400**. No new `logger.exception` / log-and-re-raise on the happy-path gate; data layer unchanged for logging posture.

## Column diff vs plan stage

(aligned) — Joan: `stat.logging.error` **A**; built API gate + UI filter match plan Canon check and Stage 1–2.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Location:** AC **10** / seed vs Revert (Joan Finding 4; build **Review**)  
  **Finding:** `data/admin/agent.json` carries **10a** (`requires_structured_output` on all rows; `true` only for `job_analyst_grace`, `job_filter_lucy`, `antagonist_kent` — verified on tip). Pre-existing `brain_setting` / `mode` / `provider_allow_fallbacks: 1` defects can still block **Revert to file** from loading DB seeds; Lucy **`GET …/job_filter_lucy` → `true`** may require UAT checkbox unless Susan normalizes seeds.  
  **Recommendation:** @susan — (a) normalize legacy seed fields so Revert lands **10a** in DB, or (b) accept manual toggle for the three graders at UAT.  
  **Default:** **(b)** — repo file and API/UI gate are correct; DB truth follows Manage Agents save.

### advisory

- **Location:** `origin/dev...8a35a745f` three-dot diff  
  **Finding:** Full epic stack (2176–2180 + transport/schema) appears in the branch diff; **2181** product footprint is `config.py` (`REPO_ADMIN_JSON_CONFIG` agent column), `database.py`, `agent.json`, `api_admin.py` (models + create/update gate), `AdminAgentPrompts.tsx`, plus tests/bible.  
  **Recommendation:** Rollup treats **2181** as admin slice only; `api_admin` ad-hoc forced-tool/hydrate lines on the composite diff are **AST-2180**, not this ticket’s scope.

- **Location:** Stage 2 in-browser check (build **Review**)  
  **Finding:** Picker filter + 400 toast not re-run in build environment (no browser session).  
  **Recommendation:** Susan UAT spot-check; component tests cover checkbox → PUT body and `capable()` filter logic.

- **Location:** AST-2177 capability registry  
  **Finding:** Picker hides only `structured_output_capability == null`; most catalog slugs stay `null` until spiked — narrow list when checkbox on is expected epic behavior.  
  **Recommendation:** Staging verification of provisional `advisory` slugs (Susan 2026-10-13 directive) — not a **2181** defect; no live provider calls on this host (sanctioned).

- **Location:** Radia pytest  
  **Finding:** `TestAst2181RequiresStructuredOutputSeed` **3 passed**; `test_agents.py` structured-setting tests **6 passed**; full `test_api_admin.py` collection failed on review host (`asyncpg` import) — not exercised here.  
  **Recommendation:** Trust Betty **Tests Passed** on publish ref for `TestAst2181StructuredOutputModelGate`.

## What's solid

- **API AC 10:** `list_models` exposes `structured_output_capability` per model; `_structured_output_gate` rejects `requires_structured_output` + `get_structured_output_capability(model) is None` on create/update with row unchanged; `advisory` allowed.
- **UI:** Checkbox + `capable()` filter; incapable current model shown as “— no structured output” but excluded from selectable alternatives (Joan decision).
- **10a:** Seed keys on all 10 agents; three grader agents `true` on models with non-`None` capability (`qwen/…`, `gpt-oss-…` advisory).
- **Plumbing:** `REPO_ADMIN_JSON_CONFIG` / `AGENT_SETTING_COLUMNS` / migration pattern mirrors `provider_allow_fallbacks`; `resolve_agent_settings` does not read the flag (gate-only — per plan).
- **Build checks:** `stage1 ok`, `tsc -b`, no provider calls; estimate **3** fits.

## Recommended actions (downstream only — not executed here)

- Chuckles: append artifact, `docs(AST-2181): Radia review — clean`, push sub, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED** toward **User Testing**.
- Susan: UAT **10** picker + toast; choose seed/Revert path for **10a** DB if needed (discuss **Default**).

context_tokens≈32000
