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
