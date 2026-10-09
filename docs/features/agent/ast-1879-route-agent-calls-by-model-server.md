<!-- linear-archive: AST-1879 archived 2026-10-08 -->

## Linear archive (AST-1879)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1879/route-agent-calls-by-model-server-support-openrouter-api-models-for  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** katherine  
**Priority / estimate:** None / 5  
**Parent:** AST-1851 — Support OpenRouter API models for agent work  
**Blocked by / blocks / related:** parent: AST-1851; blocks: AST-1880

### Description

## What this implements

After #2. `do_task` and the ad-hoc runner pick server + tier from agent model + brain size, use only that server's candidate key (no fallback), and call the Anthropic client or the shared compat client; dispatcher skip gate, meteorite hand-off, and Estelle's Slack turn read the key map. Does **not** own admin routes or UI (#4).

## Citations

new pattern *Model → server catalog routing*; `stat.logging.warning`, `stat.logging.error`.

## Scope

`src/core/agent.py` — `do_task` server/tier/key resolution, conversational brain override removed, client dispatch; `run_adhoc` / workbench wrapper route by server. `src/core/dispatcher.py` — skip gate on the task agent's server key. `src/core/meteorite.py` — ctx hand-off carries key map. `src/core/contact.py` — Estelle turn passes resolved candidate ctx; no candidate → fail with reason.

## Acceptance criteria

 7. **Right key, no fallback.** A candidate-key task for an agent on server X, for a candidate with keys for X and Y, sends X's key (component test intercepting the outbound client). With no X key, the task fails with an error naming X and no request goes out — not with Y's key, not with an env key. Any outbound request in the no-key case = fail.
 8. **Ledger per server.** An Estelle (analysis) task run writes an `agent_timesheets` row whose provider is the Kimi direct server id, model is the K2.6 SKU, token columns hold the call's fresh-input / cache-read / cache-write / output volumes, and cost equals the per-type sum from catalog pricing (component test recomputes it). Provider `deepseek`, zero tokens, or a cost mismatch = fail.
 9. **Contact Estelle is a discrete agent.** `data/admin/agent_task.json`'s `contact_estelle_turn` row names the new contact-Estelle agent (not `principal_recruiter_estelle`); `rg -n "default_brain_setting" src/` returns nothing; an Estelle Slack turn goes out at the contact row's model + brain size (component test). Any of these not holding = fail.
10. **No system-key tasks.** `python -c` over `TASK_CONFIG` finds no entry without `requires_candidate_key: True`; an Estelle Slack turn for a candidate with a key for her model's server goes out with that key (component test), and one for an unresolved Slack user sends no request. Any flag missing or any outbound request in the no-candidate case = fail.

## Boundaries

Stays inside the Scope above. Sibling slices: #1 catalog/client, #2 storage, #4 admin UI.

## Notes for planning

New pattern *Model → server catalog routing* is defined on parent AST-1851 (Architectural definition). Each child must stay green on its own `sub/*`. Additive only: legacy provider symbols stay importable until #4. AC 11's `default_brain_setting` grep clears when #4 deletes that key; this child removes every use of it in `agent.py`.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-29T21:34:34.751Z
[code-rubric] PROCEED (Commit: ea18268dd) core routing by catalog

#### betty — 2026-09-29T21:32:14.134Z
@susan AC 8 heads-up: `agent_timesheets` has no `provider` column, so no row can literally store "kimi". The server id is only `_add_timesheet_entry`'s `provider` arg (SKU-on-server check + anthropic mirror switch). The test asserts insert provider=`kimi`, SKU `kimi-k2.6` (priced only on kimi), token columns, catalog cost sum, and no anthropic mirror. If you want a stored provider, that's a `database.py` change outside AST-1879's scope. Your call where it lands; not blocking this ticket.

#### betty — 2026-09-29T21:32:13.098Z
`origin/sub/AST-1851/AST-1879-route-calls-by-model-server` @ `ea18268dd` · manifest in core/agent.md

#### joan — 2026-09-29T21:13:57.871Z
[plan-rubric] PROCEED (Commit: 5c361de46) Core routing plan clean — context_tokens≈135000

#### katherine — 2026-09-29T21:12:31.340Z
`origin/sub/AST-1851/AST-1879-route-calls-by-model-server` @ `5c361de46` · catalog routing, no-fallback keys

---

# AST-1879 — Route agent calls by model → server

- **Parent:** [AST-1851 — Support OpenRouter API models for agent work](https://linear.app/astralcareermatch/issue/AST-1851)
- **Ticket:** [AST-1879](https://linear.app/astralcareermatch/issue/AST-1879)
- **Publish ref:** `origin/sub/AST-1851/AST-1879-route-calls-by-model-server`
- **Canon Scope:** new pattern *Model → server catalog routing* (defined on AST-1851 § Architectural definition); `stat.logging.warning`, `stat.logging.error`.

This ticket is the runtime layer of *Model → server catalog routing*. `do_task` stops reading the global `active_provider`. It resolves the agent row's `model_id` + `brain_setting` through `resolve_model_brain` (AST-1877) into a server id, a SKU, and a tier row. It sends **only** the candidate's key for that server (`candidate_api_keys`, AST-1878): no env key and no other platform's key. It then calls `send_to_anthropic` or `send_to_llm_compat`, depending on the server's `protocol`. If the candidate has no key for the server, the task fails with an error that names the server, and no request goes out. The conversational brain override is removed, so Contact Estelle runs at her own agent row's model + brain size. `run_adhoc` and the workbench wrapper route by server id instead of `tier_meta is not None`. The dispatcher skip gate checks the key for the task agent's server. The meteorite classify hand-off carries the key map. Estelle's Slack turn passes the resolved candidate's ctx (key map included), and when no candidate resolves it fails with a reason before any call goes out. After this ticket `agent.py` no longer imports `send_to_deepseek` or any legacy provider symbol, so #4 (AST-1880) can delete them. Admin routes and UI are #4.

## Scope gate

Every row in **Files Changed** is named in this ticket's `## Scope`, and every stage is the kind of change that Scope describes for that file:

- `src/core/agent.py`: `do_task` server/tier/key resolution, override removed, client dispatch (Stage 1). `run_adhoc` / workbench wrapper route by server (Stage 2).
- `src/core/dispatcher.py`: skip gate on the task agent's server key (Stage 3).
- `src/core/meteorite.py`: ctx hand-off carries the key map (Stage 3).
- `src/core/contact.py`: Estelle turn passes the resolved candidate ctx; no candidate → fail with a reason (Stage 3).

`src/ui/api/api_admin.py` (ad-hoc resolve, dispatch Run/Auto gate) is **not** touched. It belongs to #4. See **Transitional gaps**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Imports: drop legacy provider symbols + `send_to_deepseek`, add catalog resolvers + `send_to_llm_compat`. New helpers `_agent_llm_route`, `task_llm_server_id`, `_candidate_server_key`, `_missing_server_key_result`, `_send_to_server`. `do_task` routing block + key gate + dispatch. `run_adhoc` / `run_adhoc_workbench_test` take `server_id` / `tier` / `candidate_api_keys`. | core |
| `src/core/dispatcher.py` | Skip gate reads `candidate_api_keys[task_llm_server_id(task_key)]` | core |
| `src/core/meteorite.py` | `_classify_stage_blob` hand-off copies `candidate_api_keys` | core |
| `src/core/contact.py` | `run_contact_estelle_turn`: no candidate → `no_candidate` fail before any call; both `do_task` calls get `ctx` with id + key map | core |

No other file is touched. No `tests/`, bible, `config.py`, `data/admin/`, or UI edits.

---

## Stage 1: `do_task` routes by model → server with the candidate's server key

**Done when:** `python3 -c "import src.core.agent"` succeeds. `rg -n -i "kimi|moonshot|openrouter|deepseek|get_active_llm_provider|resolve_brain_setting_to_|default_brain_setting|CONTACT_ESTELLE_CONFIG" src/core/agent.py` returns only the `send_to_deepseek` import (line 54) and the `run_adhoc` lines Stage 2 replaces (currently 3295 and 3309), and after Stage 2 it returns nothing. A `do_task` whose agent is on server X, for a candidate whose `candidate_api_keys` lacks X, returns `success: False` with an error naming X, and neither client is called.

1. **Imports** in `src/core/agent.py`:
   - Directly below line 54 `from src.external.deepseek import send_to_deepseek`, add `from src.external.llm_compat import send_to_llm_compat`. Line 54 stays until Stage 2, because `run_adhoc` still calls `send_to_deepseek` until then.
   - In the `from src.utils.config import (...)` block: remove `get_model`, `DEEPSEEK_MODEL_PRICING` (line 58), `get_active_llm_provider`, `resolve_brain_setting_to_anthropic_agent_key`, `resolve_brain_setting_to_deepseek_tier_meta`, `deepseek_brain_max_tokens_floor` (lines 60–63), and `CONTACT_ESTELLE_CONFIG` (line 76). Add `get_llm_server,` and `resolve_model_brain,` on the line where `get_active_llm_provider,` was.
   - Verified at plan time: each name removed here is used only inside the blocks Stage 1 replaces (`get_model` 1987, `DEEPSEEK_MODEL_PRICING` 1992, `CONTACT_ESTELLE_CONFIG` 1975/1977, the provider resolvers 1983–2007).

2. **New helpers**: insert them directly **above** `async def do_task(` (currently line 1828), after the end of `run_cover_letter_artifact_chain_for_job`:

   ```python
   def _agent_llm_route(agent_row: Dict[str, Any]) -> Dict[str, Any]:
       """Agent model_id + brain_setting → resolve_model_brain route (server, SKU, tier). Raises on missing/invalid config."""
       aid = agent_row.get("agent_id")
       model_id = (agent_row.get("model_id") or "").strip()
       if not model_id:
           raise ValueError(f"Agent '{aid}' has no model_id configured.")
       brain_setting = (agent_row.get("brain_setting") or "").strip()
       if not brain_setting:
           raise ValueError(f"Agent '{aid}' has no brain_setting configured.")
       return resolve_model_brain(model_id, brain_setting)


   def task_llm_server_id(task_key: str) -> str:
       """Catalog server behind task_key's agent model — dispatcher key gate (AST-1879)."""
       agent_row, _ = _resolve_task_prompts(task_key)
       return _agent_llm_route(agent_row)["server_id"]


   def _candidate_server_key(
       ctx: Optional[Dict[str, Any]], candidate_id: Optional[str], server_id: str
   ) -> Optional[str]:
       """The candidate's key for server_id only — never env, never another platform's key (AST-1879).

       ctx["candidate_api_keys"] wins (session paste carries a map but no candidate id);
       otherwise load the map by candidate id (callers that pass only astral_candidate_id).
       """
       keys = (ctx or {}).get("candidate_api_keys")
       if keys is None and candidate_id:
           keys = (database.get_candidate(candidate_id) or {}).get("candidate_api_keys")
       return (keys or {}).get(server_id) or None


   def _missing_server_key_result(candidate_id: Optional[str], server_id: str) -> Dict[str, Any]:
       """Failure envelope when the candidate holds no key for the route's server — no request was sent."""
       return {
           "success": False,
           "error": f"Candidate {candidate_id or '-'} has no API key for server {server_id!r}",
           "api_response": None,
           "parsed_response": None,
           "timesheet": {},
       }


   async def _send_to_server(
       user_blocks: List[Dict[str, Any]],
       *,
       server_id: str,
       sku: str,
       tier: Dict[str, Any],
       api_key: str,
       system_blocks: List[Dict[str, Any]],
       response_format: Optional[str],
       prompt_label: str,
       candidate_id: Optional[str],
       temperature: Optional[float],
       max_tokens: Optional[int],
       debug: bool,
       task_key_uuid: Optional[str],
       no_cache_prompt_tokens: int,
       no_cache_live_tokens: int,
       batch_size: int = 1,
   ) -> Dict[str, Any]:
       """One outbound call on the server's protocol client: Anthropic SDK or the shared compat client."""
       common = dict(
           system_blocks=system_blocks,
           response_format=response_format,
           prompt_label=prompt_label,
           candidate_id=candidate_id,
           temperature=temperature,
           max_tokens=max_tokens,
           task_key_uuid=task_key_uuid,
           no_cache_prompt_tokens=no_cache_prompt_tokens,
           no_cache_live_tokens=no_cache_live_tokens,
           batch_size=batch_size,
           record_timesheet=record_timesheet_entry,
       )
       if get_llm_server(server_id)["protocol"] == "anthropic":
           # api_key is always non-empty here, so send_to_anthropic never takes its env-key client.
           return await send_to_anthropic(user_blocks, model_code=sku, api_key_override=api_key, debug=debug, **common)
       return await send_to_llm_compat(user_blocks, server_id=server_id, sku=sku, tier=tier, api_key=api_key, **common)
   ```

   ⚠️ **Decision (load keys by candidate id when ctx has no map):** most callers pass the full `get_candidate` row (or spread it) as ctx, so `candidate_api_keys` rides along. `meteorite.py:1995` (`{"astral_candidate_id": cid}`) passes only the id and no map, and that file's Scope here is limited to the classify hand-off. Loading by id is still the candidate's own key for the same server. It is not a fallback. Checking `keys is None` (and not falsy) means an explicit empty map (a candidate with no keys) is honoured and never re-read.

   ⚠️ **Decision (protocol, not server name, picks the client):** routing branches on `LLM_SERVER_CONFIG[...]["protocol"]` (`"anthropic"` vs anything else, which #1's startup validation limits to `"anthropic_compat"`). No server or model name appears in `agent.py` (parent AC 2).

   ⚠️ **Decision (Anthropic SKU = pricing alias):** for the `claude` model the catalog SKU is the `AGENT_CONFIG` alias key (`claude-haiku-4-5` / `claude-sonnet-4-6` / `claude-opus-4-6`, AST-1877 Stage 1), which is what `send_to_anthropic(model_code=…)` sends and prices by today.

3. **`do_task`: remove the legacy key override.** Delete line 1880 `api_key_override = None` and lines 1891–1892:

   ```python
       if ctx and task_config.get("requires_candidate_key"):
           api_key_override = ctx.get("candidate_api_key")
   ```

   Change the `ctx` line in the docstring (line 1852) to `ctx: Full candidate raft dict. Extracts candidate_data + candidate_api_keys (server → key map).`

4. **`do_task`: replace the brain/provider block.** Replace lines 1974–2009 (from `brain_setting = (agent_row.get("brain_setting") or "").strip()` through the `_ds_floor` block ending `agent_max_tokens = max(int(agent_max_tokens), _ds_floor)`) with:

   ```python
       # AST-1879: the agent row's model + brain size pick the server, SKU, and tier. Contact Estelle
       # is her own agent row (AST-1878), so there is no conversational brain override.
       route = _agent_llm_route(agent_row)
       server_id = route["server_id"]
       sku = route["sku"]
       tier = route["tier"]
       api_key = _candidate_server_key(ctx, candidate_id, server_id)
       if not api_key:
           logger.warning(
               "%s | %s skipped — no %s API key on the candidate\n  This call is not going out",
               candidate_id or "-",
               task_key,
               server_id,
           )
           return _with_harvest(_missing_server_key_result(candidate_id, server_id))
       agent_temperature = agent_row.get("temperature") if agent_row.get("temperature") is not None else tier["default_temperature"]
       agent_max_tokens = agent_row.get("max_tokens") if agent_row.get("max_tokens") is not None else tier["default_max_tokens"]
       # Craft rubrics emit long per-criterion content — floor so Get cannot truncate mid-JSON (AST-903).
       if task_key in CRAFT_RUBRIC_UI_TASK_KEYS:
           agent_max_tokens = max(int(agent_max_tokens), int(CRAFT_RUBRIC_MAX_TOKENS))
           # AST-1380 Decision A: thinking shares max_tokens with the JSON answer —
           # disable thinking so craft criteria are not starved mid-string.
           tier = {**tier, "thinking": False}
       # AST-1391: catalog per-tier output floor (None = no floor).
       if tier.get("max_tokens_floor") is not None:
           agent_max_tokens = max(int(agent_max_tokens), int(tier["max_tokens_floor"]))
   ```

   ⚠️ **Decision (missing key = warning + failure envelope, not a raise):** "no key for this server" is a configured miss with no exception, so under `stat.logging.warning` it gets one per-item who/why/consequence line (candidate, task, server, "This call is not going out"). It returns the same envelope shape as the existing `guard_err` early return, so every caller's `success: False` handling applies unchanged. A missing or invalid `model_id` / `brain_setting` still **raises** `ValueError`, like today's `has no brain_setting configured`, because that is broken agent config and not a candidate miss. The caller's handler logs it once (`stat.logging.error`).

   ⚠️ **Decision (placement):** the key check runs before token resolution, `_store_prompt_blocks`, and the run_next hop-ledger open, so no agent_data prompt rows or hop ledgers are written for a call that never goes out. This matches the `hydr_err` early return just above it.

   ⚠️ **Decision (defaults and floor from the tier row):** `default_temperature` / `default_max_tokens` / `max_tokens_floor` now come from the catalog tier. For Claude and DeepSeek V4 these values are copied verbatim from `AGENT_CONFIG` / the legacy DeepSeek blocks (AST-1877 parity asserts), so today's agents behave the same. The craft-rubric thinking-off now applies to any tier. It is a no-op where the tier's thinking is already off (all Claude and DeepSeek V4 tiers).

5. **`do_task`: assembly model tag.** Delete line 2140 `assemble_model_tag = resolved_anthropic_key if provider == "anthropic" else tier_meta["vendor_model"]`. In the `_assemble_blocks_seven_segment(...)` call directly below it, change `model_code=assemble_model_tag,` to `model_code=sku,`.

6. **`do_task`: dispatch.** Replace lines 2175–2219 (from `send_fn_name = ...` through `logger.debug("Response from %s: %s", send_fn_name, result)`) with:

   ```python
       logger.debug(
           "Calling _send_to_server: [task_key=%s, server=%s, model=%s, max_tokens=%s, temp=%s, skip_cache=%s, candidate=%s]",
           task_key, server_id, sku, agent_max_tokens, agent_temperature, skip_cache, candidate_id or "",
       )
       result = await _send_to_server(
           user_blocks,
           server_id=server_id,
           sku=sku,
           tier=tier,
           api_key=api_key,
           system_blocks=system_blocks,
           response_format=response_format,
           prompt_label=task_key,
           candidate_id=candidate_id,
           temperature=agent_temperature,
           max_tokens=agent_max_tokens,
           debug=debug,
           task_key_uuid=agent_task_row.get("task_key_uuid"),
           no_cache_prompt_tokens=no_cache_prompt_tokens,
           no_cache_live_tokens=no_cache_live_tokens,
           batch_size=batch_size,
       )
       logger.debug("Response from _send_to_server: %s", result)
   ```

   Nothing after this point in `do_task` changes. The provider-failure branch (`normalize_provider_error`, audit body, hop failure) reads the same result keys from both clients (AST-1877: `send_to_llm_compat` keeps `send_to_deepseek`'s result contract).

7. **Stage 1 check** (worktree root):

   ```bash
   python3 -m py_compile src/core/agent.py
   python3 -c "import src.core.agent, src.core.dispatcher, src.core.contact, src.core.meteorite"
   rg -n "tier_meta|resolved_anthropic_key|provider ==|api_key_override = |send_fn_name|assemble_model_tag" src/core/agent.py
   ```

   The `rg` hits only the `run_adhoc_workbench_test` / `run_adhoc` lines Stage 2 replaces, plus `_send_to_server`'s `api_key_override=api_key` keyword. (`send_to_deepseek` is still imported and used only by `run_adhoc`.)

**Stage 1 commit:** `code(AST-1879): do_task routes by model → server with candidate server key`

---

## Stage 2: `run_adhoc` / workbench wrapper route by server

**Done when:** `rg -n -i "kimi|moonshot|openrouter|deepseek|tier_meta|api_key_override" src/core/agent.py` returns only `_send_to_server`'s `api_key_override=api_key` keyword (the `send_to_anthropic` parameter name). `run_adhoc` with `candidate_api_keys` missing the server returns `success: False` naming the server and sends nothing.

0. **Import:** delete line 54 `from src.external.deepseek import send_to_deepseek` (its last use is the `run_adhoc` body replaced below).

1. **`run_adhoc`** (currently line 3271). Signature: in the keyword-only section, replace `tier_meta: Optional[Dict[str, Any]] = None,` with two lines, `server_id: Optional[str] = None,` and `tier: Optional[Dict[str, Any]] = None,`. Replace `api_key_override: Optional[str] = None,` with `candidate_api_keys: Optional[Dict[str, str]] = None,`. All other parameters and their order stay the same.

   Replace the docstring and the whole body up to (not including) `result["runtime_prompt"] = runtime_prompt` with:

   ```python
       """Run an ad-hoc prompt without DB prompt resolution or agent_data storage.
       Routes by catalog server; sends only the candidate's key for that server (no fallback — AST-1879)."""
       if not model_code:
           raise ValueError("run_adhoc requires model_code (catalog SKU)")
       if not server_id or tier is None:
           raise ValueError("run_adhoc requires server_id and tier (resolve_model_brain route)")
       api_key = (candidate_api_keys or {}).get(server_id)
       if not api_key:
           return _missing_server_key_result(candidate_id, server_id)

       system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens = _assemble_blocks_seven_segment(
           system_content=system_content,
           user_content=user_content,
           caches_resolved_four=(cache_content, cache_content_b, cache_content_c, cache_content_d),
           nocache_content=nocache_content,
           live_content=live_content,
           model_code=model_code,
           skip_cache=False,
           candidate_id=candidate_id,
       )
       result = await _send_to_server(
           user_blocks,
           server_id=server_id,
           sku=model_code,
           tier=tier,
           api_key=api_key,
           system_blocks=system_blocks,
           response_format=response_format,
           prompt_label="adhoc",
           candidate_id=candidate_id,
           temperature=temperature,
           max_tokens=max_tokens,
           debug=debug,
           task_key_uuid=task_key_uuid,
           no_cache_prompt_tokens=no_cache_prompt_tokens,
           no_cache_live_tokens=no_cache_live_tokens,
       )
   ```

   ⚠️ **Decision (run_adhoc picks the key, not the route):** the caller (#4's `_resolve_adhoc`) passes `resolve_model_brain(...)`'s `server_id` / `sku` (as `model_code`) / `tier` plus `candidate.get("candidate_api_keys")`. Key selection lives in core, so no-fallback is enforced in one place for both `do_task` and ad-hoc. `run_adhoc` does not log the miss, because `run_adhoc_workbench_test` already emits the per-item `adhoc failed` warning on any `success: False` (one line per failure, `stat.logging.warning`).

   ⚠️ **Decision (rename, not alias):** `tier_meta` → `tier` and `api_key_override` → `candidate_api_keys` are renamed outright. The old names describe the removed behaviour (a DeepSeek-only tier and an optional override with an env fallback). The only production caller (`api_admin.adhoc_test`) has to change in #4 anyway, because it has no server id to pass. See **Transitional gaps**.

2. **`run_adhoc_workbench_test`** (currently line 3063). Signature: replace `tier_meta: Optional[Dict[str, Any]] = None,` with `server_id: Optional[str] = None,` and `tier: Optional[Dict[str, Any]] = None,`. Replace `api_key_override: Optional[str] = None,` with `candidate_api_keys: Optional[Dict[str, str]] = None,`.
   - Debug line (currently 3137–3140): change it to `"Calling run_adhoc: [task_key=%s, candidate=%s, server=%s, model=%s]", workbench_task_key, candidate_id, server_id, model_code,`.
   - In the `await run_adhoc(...)` call: replace `tier_meta=tier_meta,` with `server_id=server_id,` and `tier=tier,`. Replace `api_key_override=api_key_override,` with `candidate_api_keys=candidate_api_keys,`.
   - Nothing else in the wrapper changes (ledger, agent_data, warnings).

3. **Stage 2 check** (worktree root):

   ```bash
   python3 -m py_compile src/core/agent.py
   python3 -c "import src.core.agent"
   rg -n -i "kimi|moonshot|openrouter|deepseek|tier_meta|api_key_override|default_brain_setting" src/core/agent.py
   ```

   The `rg` returns only `_send_to_server`'s `api_key_override=api_key`.

**Stage 2 commit:** `code(AST-1879): run_adhoc and workbench route by server`

---

## Stage 3: Dispatcher key gate, meteorite hand-off, Estelle turn ctx

**Done when:** the dispatcher skips (warning, no ledger) a candidate that lacks a key for the task agent's server. `_classify_stage_blob` forwards `candidate_api_keys`. `run_contact_estelle_turn` with no resolvable candidate returns `error: "no_candidate"` without calling `do_task`, and with a candidate it calls `do_task` with `ctx` carrying `astral_candidate_id` and `candidate_api_keys`. `rg -n "candidate_api_key\b" src/core/` returns nothing.

1. **`src/core/dispatcher.py` import** (line 30): `from src.core.agent import _current_agent_task_run_next, compute_batch_cost, task_llm_server_id`.

2. **`src/core/dispatcher.py` skip gate** in `_dispatch_one_body`: replace lines 1335–1346 (from `ctx = database.get_candidate(candidate_id)` through the `return` after the warning) with:

   ```python
       ctx = database.get_candidate(candidate_id)
       # AST-1879: the key for the task agent's server only — another platform's key does not count.
       server_id = task_llm_server_id(task_key)
       if not ctx or not (ctx.get("candidate_api_keys") or {}).get(server_id):
           logger.debug(
               "skipped — no candidate or %s API key task_key=%s candidate_id=%s",
               server_id, task_key, candidate_id,
           )
           logger.warning(
               "%s | dispatch %s skipped — no candidate or %s API key\n  This task is not starting",
               candidate_id or "-",
               task_key,
               server_id,
           )
           return
   ```

   ⚠️ **Decision (gate reach):** only tasks that fall through the meteorite-ingress, bot-blocked-notify, and inbox-mailbox branches reach this gate. At plan time every `TASK_CONFIG` key with a seeded `agent_task` row resolves an agent. `bootstrap_candidate_context`, `propose_application_responses`, and `resolve_website` have no row, and `do_task` already raises on them today via `_resolve_task_prompts`. If `task_llm_server_id` raises (broken agent config), the exception propagates through `_dispatch_one` to `_task_thread_target`'s existing `except Exception` → `logger.exception("… dispatch task %s crashed")`, which logs it once (`stat.logging.error`). No new catch is added.

   ⚠️ **Decision (warning text):** the skip line keeps today's shape and adds the server id, so the operator sees which platform key is missing (`stat.logging.warning`: who, why, "This task is not starting").

3. **`src/core/meteorite.py` `_classify_stage_blob`**: replace lines 759–760 with:

   ```python
       if ctx and ctx.get("candidate_api_keys") is not None:
           task_ctx["candidate_api_keys"] = ctx["candidate_api_keys"]
   ```

4. **`src/core/contact.py` `run_contact_estelle_turn`**:
   a. Directly after the listen re-check block (after the `return out` that follows `out["error"] = "listen_off"`, line 1047) and before `logger.debug("Calling run_contact_estelle_turn: ...")`, insert:

      ```python
          # a2. Every LLM task runs on the candidate's platform key (AST-1879) — no candidate, no call.
          cid = astral_candidate_id.strip() if isinstance(astral_candidate_id, str) else ""
          row = get_candidate(cid) if cid else None
          if not isinstance(row, dict):
              logger.warning(
                  "%s | contact estelle turn skipped — no candidate for this Slack user\n  Estelle is not replying",
                  channel,
              )
              out = dict(empty)
              out["error"] = "no_candidate"
              return out
      ```

   b. In step `c.` (lines 1127–1146), replace the block

      ```python
          candidate_data: dict = {}
          if isinstance(astral_candidate_id, str) and astral_candidate_id.strip():
              row = get_candidate(astral_candidate_id)
              if isinstance(row, dict):
                  cd = row.get("candidate_data")
                  ...
                      if body is not None:
                          candidate_data.setdefault("artifacts", {})["base_resume"] = body
      ```

      with the same body using the `row` from step a2. Delete the `if isinstance(astral_candidate_id, str) ...`, `row = get_candidate(astral_candidate_id)`, and `if isinstance(row, dict):` lines, dedent the remaining lines by 8 spaces, and change `resolve_pinned_base_resume(astral_candidate_id, pin, debug=debug)` to `resolve_pinned_base_resume(cid, pin, debug=debug)`. Directly after the block (before `# d. do_task + envelope helper`), add:

      ```python
          # Resolved candidate ctx: do_task picks this candidate's key for the agent's server
          # and stamps the [astral-<id>] system prefix (AST-1639).
          turn_ctx = {
              "astral_candidate_id": cid,
              "candidate_data": candidate_data,
              "candidate_api_keys": dict(row.get("candidate_api_keys") or {}),
          }
      ```

   c. In **both** `do_task(...)` calls (lines 1155–1162 and 1204–1211), replace `candidate_data=candidate_data,` with `ctx=turn_ctx,`. Every other argument stays the same.

   ⚠️ **Decision (token view unchanged):** today `index=astral_candidate_id` already makes `_token_view_for_do_task` build the view from the candidate row (AST-1682). Adding `astral_candidate_id` to ctx takes the earlier branch of the same function with the same row, so the resolved tokens are identical. The new effects are intended: `do_task` finds the key map, and the `[astral-<id>]` prefix that `_assemble_blocks_seven_segment` requires (AST-1639) has a candidate id to use.

   ⚠️ **Decision (`no_candidate` code + warning):** the error uses the same `no_candidate` token as the turn's skill/land results and follows the `listen_off` early-return shape. The skip is a configured miss with no exception, so it gets one `stat.logging.warning` line (who = channel, why, consequence). A candidate with no key for Estelle's server is handled inside `do_task` (Stage 1): it gets the server-naming warning, `result["error"]` carries it, and the turn returns it as `error`.

5. **Stage 3 check** (worktree root):

   ```bash
   python3 -m py_compile src/core/dispatcher.py src/core/meteorite.py src/core/contact.py src/core/agent.py
   python3 -c "import src.core.dispatcher, src.core.meteorite, src.core.contact, src.core.agent"
   rg -n "candidate_api_key\b" src/core/
   rg -n -i "kimi|moonshot|openrouter|deepseek" src/core/agent.py src/core/dispatcher.py src/core/meteorite.py src/core/contact.py
   ```

   Both `rg` commands return nothing.

**Stage 3 commit:** `code(AST-1879): dispatcher server-key gate, meteorite key map, Estelle turn ctx`

---

## Compile / lint (every stage)

`python3 -m py_compile` on every `.py` file changed in the stage (build-child §7; no linter is configured), then that stage's import check. Both must pass before each `code()` commit.

## Acceptance mapping (this ticket)

- **AC 7 (right key, no fallback):** Stage 1 steps 2–4 and 6. The key comes from `candidate_api_keys[server_id]` only. A missing key returns before either client is called. `send_to_llm_compat` never reads env (AST-1877), and `send_to_anthropic` receives a non-empty `api_key_override`, so it never builds its env client.
- **AC 8 (ledger per server):** Stage 1. An agent on `kimi-k2.6` routes to `send_to_llm_compat`, which records `provider=server_id`, `model_code=sku`, and four-bucket costs from catalog pricing (AST-1877 Stage 4 f). `insert` validates the SKU/server pair (AST-1878 Stage 3).
- **AC 9 (Contact Estelle is a discrete agent):** Stage 1 step 4 removes the override, so the turn uses `contact_recruiter_estelle`'s model + brain (seeded by AST-1878). This ticket removes every `default_brain_setting` use in `agent.py`. The `config.py` key and the epic-wide grep clear in #4.
- **AC 10 (no system-key tasks):** Stage 3 step 4 (unresolved Slack user → `no_candidate`, no `do_task`) plus Stage 1 (candidate with the key → goes out with that key). The `TASK_CONFIG` flag half landed in AST-1877.

## Tests expected to move (Betty — qa-child; engineer does not edit `tests/`)

- `tests/component/core/test_agent*.py`: any test that patches `get_active_llm_provider`, `send_to_deepseek`, or `resolve_brain_setting_to_*` on `agent`, or that passes `tier_meta=` / `api_key_override=` to `run_adhoc` / `run_adhoc_workbench_test`. Agent-row fixtures need `model_id`, and ctx fixtures need `candidate_api_keys` for the agent's server (or a stubbed `database.get_candidate`).
- `tests/component/core/test_dispatcher*.py`: skip-gate tests that set `candidate_api_key` on the candidate need `candidate_api_keys` plus a stubbed `task_llm_server_id`.
- `tests/component/core/test_meteorite*.py`: classify ctx hand-off asserts `candidate_api_keys`.
- `tests/component/core/test_contact.py` (`run_contact_estelle_turn` class, ~line 665): the stubbed `get_candidate` must return a row for the do_task path. The fake `do_task` now receives `ctx=` (with `astral_candidate_id` / `candidate_api_keys`) instead of `candidate_data=`. A new case covers `astral_candidate_id=None` → `error == "no_candidate"` with `do_task` not awaited.
- New coverage: AC 7 (key X sent / no-X → error naming X, no client call), AC 8 (Kimi timesheet row), AC 9 (Estelle turn at the contact row's model + brain), AC 10 (turn with key / unresolved user → no request).

## Transitional gaps (closed by #4)

On `sub/*` and `ftr` only, until AST-1880 lands (UAT runs after all four children):

- `api_admin.adhoc_test` still passes `tier_meta=` / `api_key_override=` to `run_adhoc_workbench_test`. That raises `TypeError`, which the route's existing `except` turns into a 500 JSON error. #4 rewires `_resolve_adhoc` to `resolve_model_brain` + `candidate_api_keys`.
- `api_admin` dispatch Run/Auto gate (line ~2079) still reads the legacy `candidate_api_key` (#4).

## Deploy / UAT notes for Susan

- **Agent rows need `model_id` in the live DB.** `apply_agent_repo_json_startup` runs only on **Revert-to-file** (`revert_repo_admin_json_table`); there is no startup auto-apply. Until the `agent` table (and `agent_task`, for `contact_estelle_turn` → `contact_recruiter_estelle`) is reverted from repo JSON, `do_task` raises `Agent '<id>' has no model_id configured.` for every task.
- **Estelle (analysis) `max_tokens: 384000`** (flagged by AST-1878) is sent as-is on Kimi K2.6 Big. The agent row is authoritative, and this plan adds no cap (no limits without your approval). If Kimi rejects it, set that row's `max_tokens` to null in Manage Agents (the catalog default is 32000) or to a value you choose.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1879
**Overall:** APPROVED
**Corpus:** `e1f2699fad`
**Publish ref:** `5c361de46`

## Canon scores

Model → server catalog routing | A | | Stages 1–3: `resolve_model_brain` route, protocol dispatch, server-scoped keys, no legacy provider path in core
stat.logging.warning | A | | Missing-key skips (do_task, dispatcher, contact `no_candidate`); per-item who/why/consequence lines
stat.logging.error | A | | Broken agent config raises; dispatcher crash path unchanged; provider failures stay on client/handler contract

## Traceability

7→S1 steps 2–4,6 + S2 (`candidate_api_keys[server_id]` only; Betty AC 7 intercept tests) | 8→S1 dispatch via `_send_to_server` / compat timesheet fields (Betty AC 8; needs #1 client + #2 SKU validation + Kimi-seeded agent) | 9→S1 step 4 override removed + agent.py `default_brain_setting` purge (S2 rg); `agent_task.json` row→#2; config grep remainder→#4 (Betty AC 9 turn test) | 10→S3 contact `no_candidate` + S1 keyed turn path; `requires_candidate_key` assert→#1 (Betty AC 10) | parent 1–6,12–13,15–16→N/A (#4 or prior children)

## Findings

### acceptable

- **Severity:** acceptable
- **Location:** **Transitional gaps** / **Deploy / UAT notes**
- **Finding:** `api_admin` ad-hoc and dispatch Run/Auto stay on legacy signatures until #4; live DB needs repo revert for `model_id` / `contact_estelle_turn` before routed tasks run in production.
- **Recommendation:** None — documented layer split and operator steps.

- **Severity:** acceptable
- **Location:** Stage 1 `_candidate_server_key` decision
- **Finding:** Reloading `candidate_api_keys` by `candidate_id` when ctx omits the map (meteorite classify path) is scoped to the same server id, not env or cross-platform fallback.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** **Tests expected to move**
- **Finding:** AC 7–10 component coverage is named for Betty; engineer test-tree ban respected.
- **Recommendation:** None.

### discuss

- **Severity:** discuss
- **Location:** Child **Acceptance criteria** AC 9 vs **Acceptance mapping**
- **Finding:** Ticket AC 9 quotes the full parent AC 11 bar (`agent_task.json`, repo-wide `default_brain_setting` grep, component turn); this plan correctly assigns the seed row to #2, config key deletion to #4, and owns override removal + `agent.py` grep here — so the child ticket AC text overstates what #3 alone can pass before sibling merges.
- **Recommendation:** Optional ticket AC footnote mirroring **Notes for planning** (already on Linear description) so UAT does not treat AC 9 as failing on `sub/*` before #2/#4 are on the integration branch.

- **Severity:** discuss
- **Location:** Deploy note / AST-1878 hand-off
- **Finding:** Analysis Estelle may send `max_tokens: 384000` on Kimi K2.6 Big; plan defers cap to operator/config without inventing limits.
- **Recommendation:** Susan awareness only; no plan change required.

context_tokens≈135000

[plan-rubric] PROCEED (Commit: 5c361de46) Core routing plan clean

## Review

- **Branch:** `origin/sub/AST-1851/AST-1879-route-calls-by-model-server`
- **Build tip:** `85d426b0f` (stages: `026e1e74b` do_task catalog route + server key gate + protocol dispatch · `bf6d6887c` run_adhoc / workbench route by server · `85d426b0f` dispatcher server-key gate + meteorite key map + Estelle turn ctx)
- **Build notes:** Built as planned, no deviations. The Stage 3 check `rg -n "candidate_api_key\b" src/core/` also matches AST-1878's `set_candidate_api_key(` / `clear_candidate_api_key(` wrapper names in `candidate.py` (the `\b` fires before `(`). Those are per-server wrappers, not the legacy single-key field; no legacy-key reads remain in `src/core/`. `contact.py` / `meteorite.py` cannot be imported locally (`asyncpg` not installed); smoke under `debug/spikes/ast-1879/` (asyncpg stubbed) confirmed: kimi agent → `send_to_llm_compat` with only the kimi key from a two-key map; claude agent → `send_to_anthropic` with the anthropic key; no-key `do_task` / `run_adhoc` → `success: False` naming the server, zero client calls; Estelle turn with no candidate → `no_candidate`, zero calls.
- **For qa-child:** see **Tests expected to move** above (agent / dispatcher / meteorite / contact fixtures and the AC 7–10 coverage).

## Radia review

[code-rubric]
**Ticket:** AST-1879
**Publish ref:** ea18268dd
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

Model → server catalog routing | A | |
stat.logging.warning | A | |
stat.logging.error | A | |

## Column diff vs plan stage

(aligned)

## Frame diff

- [ ] **Acceptance criteria — AC 9 (`default_brain_setting` grep):** Optional ticket footnote that repo-wide grep clears when AST-1880 deletes `CONTACT_ESTELLE_CONFIG["default_brain_setting"]`; this child removed all `agent.py` / conversational override uses only. Engineer to confirm at UT against merged ftr, not `sub/*` alone.
- [ ] **Deploy / UAT — agent `model_id` in live DB:** Checkbox that production/UAT `agent` (+ `agent_task` for `contact_estelle_turn`) rows were reverted from repo JSON before routed dispatch is exercised (plan **Deploy / UAT notes**).

## Findings

### fix-now

(none)

### discuss

- **Severity:** discuss  
- **Location:** Linear **Acceptance criteria** AC 9 vs plan **Acceptance mapping** / AST-1880  
- **Finding:** Ticket AC 9 quotes the full parent AC 11 bar (`agent_task.json` row, `rg default_brain_setting src/`, component turn). Seed row is #2; config key deletion is #4; #3 owns override removal and `agent.py` purge — `rg` still hits `CONTACT_ESTELLE_CONFIG` in `config.py` until #4.  
- **Recommendation:** Optional AC footnote (Linear description already has **Notes for planning**).  
- **Default:** Treat AC 9 grep + `agent_task` as epic/ftr pass criteria; do not reopen #3 for `config.py` deletion.

- **Severity:** discuss  
- **Location:** Plan **Transitional gaps** — `api_admin` ad-hoc / dispatch Run·Auto  
- **Finding:** `run_adhoc_workbench_test` now requires `server_id` + `tier` + `candidate_api_keys`; legacy `api_admin` paths still pass old kwargs until #4 → `TypeError` / 500 on ad-hoc test and legacy single-key dispatch gate.  
- **Recommendation:** None in #3; #4 rewires admin.  
- **Default:** Document in UT checklist for ftr; no #1879 code change.

- **Severity:** discuss  
- **Location:** AST-1878 hand-off — `principal_recruiter_estelle` `max_tokens: 384000` on Kimi K2.6 Big  
- **Finding:** #3 sends agent row `max_tokens` as-is; Kimi may reject oversized values.  
- **Recommendation:** Operator awareness (plan deploy note).  
- **Default:** No cap in code without @susan; adjust row via admin after #4 or DB if provider rejects.

### advisory

- **Severity:** advisory  
- **Location:** Three-dot diff `origin/dev`…`sub/AST-1879`  
- **Finding:** Includes merged #1877/#1878 product (catalog, `database`, seed) — prerequisite stack, not #1879 scope smuggling. **#1879 product-only commits** (`026e1e74b`…`85d426b0f`): `agent.py`, `dispatcher.py`, `contact.py`, `meteorite.py` only.  
- **Recommendation:** Score routing against those four files.

- **Severity:** advisory  
- **Location:** `tests/component/**` in tip `ea18268dd` (merge-tests + Betty AC 7–10)  
- **Finding:** sibling test carry; engineer test-tree ban respected on code commits.  
- **Recommendation:** Note once.

## What's solid

- **Pattern:** `_agent_llm_route` → `resolve_model_brain`; `_candidate_server_key` uses `candidate_api_keys[server_id]` only (ctx map or `get_candidate` reload); `_missing_server_key_result` names server, no client call; `_send_to_server` branches `anthropic` vs `anthropic_compat` with explicit `api_key` (no env / cross-platform fallback).
- **Scope files:** Conversational `CONTACT_ESTELLE_CONFIG` brain override removed; `send_to_deepseek` and legacy provider imports gone from `agent.py`; no vendor/server name literals in `agent.py`.
- **`stat.logging.warning`:** Missing-key skips in `do_task`, dispatcher (`task_llm_server_id` gate), and contact `no_candidate` use per-item who / why / consequence lines.
- **`stat.logging.error`:** No new provider `logger.error` in routing path; client `log_llm_batch_summary` contract unchanged; existing dispatcher/agent exception sites untouched by this diff.
- **Stage 3:** Meteorite hand-off copies `candidate_api_keys`; Estelle turn builds `turn_ctx` with id + key map; both `do_task` calls use `ctx=turn_ctx`; no candidate → `no_candidate` before any LLM call.

## Recommended actions

- Chuckles: append artifact, `docs(AST-1879): Radia review — clean`, post slim upshot, **Review Posted** → datt **PROCEED** to User Testing.
- #4: wire `api_admin` ad-hoc + dispatch gate to `resolve_model_brain` + per-server keys; delete `CONTACT_ESTELLE_CONFIG["default_brain_setting"]`.
- Susan/UAT: repo revert `agent` / `agent_task` on target DB before exercising routed tasks in production.

context_tokens≈42000

[code-rubric] PROCEED (Commit: ea18268dd) core routing by catalog

## Resolution

2026-09-29, resolved against Radia review `ac37748b3` (CLEAN / PROCEED). No product changes.

- **fix-now:** none.
- **discuss — AC 9 quotes the full parent AC 11 bar:** took the `Default:`. The AC 9 `rg default_brain_setting src/` grep and the `agent_task.json` row are epic/ftr pass criteria. The seed row is #2's (already on ftr) and the `config.py` key deletion is #4's (AST-1880). This child removed every use in `agent.py` (the conversational override). #3 is not reopened for `config.py`.
- **discuss — `api_admin` ad-hoc / dispatch Run·Auto on legacy kwargs:** took the `Default:`. Already recorded under **Transitional gaps**; #4 rewires `_resolve_adhoc` and the dispatch gate. No AST-1879 code change.
- **discuss — Estelle (analysis) `max_tokens: 384000` on Kimi K2.6 Big:** took the `Default:`. No cap in code without Susan's approval; operator adjusts the row if Kimi rejects it (see **Deploy / UAT notes**).
- **Frame diff rows (AC 9 footnote, live-DB revert):** not ticked here. Both are checks against merged ftr / the target DB (after #4, and after Susan's Revert-to-file), which cannot be validated on this `sub/*` tip. They are left for UT, the same way AST-1878's frame-diff row was left for Susan. The ticket's Linear description has no checkbox rows to tick.
- **Advisories:** no action (sibling product stack and sibling test carry, as Radia noted).
