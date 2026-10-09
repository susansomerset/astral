<!-- linear-archive: AST-1956 archived 2026-10-08 -->

## Linear archive (AST-1956)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1956/send-the-agents-settings-on-the-wire-refactor-agent-settings-and  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1953 — Refactor agent settings and ingest per-endpoint model options  
**Blocked by / blocks / related:** parent: AST-1953

### Description

## What this implements

Agent calls send temperature, effort and the provider object straight from the agent's settings, on both clients, with no gating. A rejected setting is an ordinary failure. The debug line shows what was sent. After #1. Does **not** touch admin routes or UI (#3).

## Citations

`patt.task.dispatch-retry` (rejections take the normal retry path); `stat.logging.debug`.

## Scope

* `src/core/agent.py` (**modified**):
  * **Modified route helper:** calls the new resolver with the agent row.
  * **Modified call path (**`do_task`**,** `run_adhoc`**):** passes the resolved temperature/effort/provider object through. The craft-rubric guard still forces thinking off, and the floors still apply.
  * **Modified debug line:** logs the temperature and effort sent.
* `src/external/llm_compat.py` (**modified**): **modified request assembly**.
  * Sends `temperature` when given.
  * Sends the effort in `output_config.effort`, or `thinking: {type: "disabled"}` for `none`.
  * Merges the provider object into the body.
  * The thinking-on/off-from-tier branch goes. The failure path is unchanged.
* `src/external/anthropic.py` (**modified**): **modified** `send_to_anthropic`. Takes an optional effort and sends it the same way when given. The failure path is unchanged.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/core/test_agent.py`
  * `tests/component/external/test_llm_compat.py`
  * `tests/component/external/test_anthropic.py`
  * `docs/test-bible/core/agent.md`
  * `docs/test-bible/external/llm_compat.md`
  * `docs/test-bible/external/anthropic.md`

## Acceptance criteria

"Stubbed client" means the component-test stubs of the Anthropic SDK client used by `test_llm_compat.py`, `test_anthropic.py` and `test_agent.py`.

1. **Provider object from the agent row.**
   * **Check (stubbed client):** an agent on `openai/gpt-oss-120b` with `quantization: "bf16"`, fallbacks true and nothing else sends `provider == {"quantizations": ["bf16"], "allow_fallbacks": true}` exactly. With `provider_only: ["crusoe"]`, `provider_sort: "price"` added, it also carries `only` and `sort`.
   * **Fails if:** any other key appears, or there is an `order` pin, or the body differs.
2. **Empty settings send nothing.**
   * **Check (stubbed client):** an OpenRouter agent with every setting empty except fallbacks sends no `temperature`, no `output_config`, no `thinking`, and `provider == {"allow_fallbacks": true}`.
   * **Fails if:** any of those keys appears with a value the agent didn't set.
3. **Temperature and effort exactly as set, no gating.**
   * **Check (stubbed client):**
     * `temperature: 0.3` → `temperature == 0.3`;
     * `reasoning_effort: "high"` → `output_config.effort == "high"`;
     * `reasoning_effort: "none"` → `thinking == {"type": "disabled"}`.
   * **Check:** a model whose old config said it couldn't think still sends `"high"` when set.
   * **Check:** the same on `claude-sonnet-4-6` via the Anthropic client.
   * **Fails if:** any value is dropped, changed or blocked in code.
4. **A rejected setting is an ordinary failure.**
   * **Check (stubbed 400 "Reasoning is mandatory for this endpoint and cannot be disabled"):** `do_task` returns the normal failure result. No new failure class is introduced: `rg -n "config_error|configuration_error" src/` returns nothing.
   * **Fails if:** a special class or hold path appears.
5. **Truthful debug line.**
   * **Check (component test):** for an agent with empty temperature, the `Calling _send_to_server` debug line shows `temp=None`.
   * **Fails if:** a number is logged.

## Boundaries

Does not touch [config.py](<http://config.py>) / [database.py](<http://database.py>) / seed (#1) or admin routes/UI (#3). Uses #1's settings resolver.

## Notes for planning

Parent AST-1953 Description is the authority (Functional scope, Technical scope, Susan's 2026-10-03 answers). Code it loosely — no vocabulary lists, no pre-send gating (Susan).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1953-agent-settings`, child `sub/AST-1953/AST-1956-send-settings-on-wire`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-03T23:42:22.075Z
[code-rubric] PROCEED (Commit: 7aa622ec7) Settings on wire clean

#### betty — 2026-10-03T23:36:55.469Z
`origin/sub/AST-1953/AST-1956-send-settings-on-wire` @ `7aa622ec7` · manifest in agent bible

#### joan — 2026-10-03T23:10:35.338Z
[plan-rubric] PROCEED (Commit: 5851456ca) Wire path traceable

#### hedy — 2026-10-03T23:08:54.222Z
`origin/sub/AST-1953/AST-1956-send-settings-on-wire` @ `5851456ca` · settings sent as stored

---

# AST-1956 — Send the agent's settings on the wire

- **Ticket:** [AST-1956](https://linear.app/astralcareermatch/issue/AST-1956) · **Parent:** [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953) Refactor agent settings and ingest per-endpoint model options
- **Publish ref:** `sub/AST-1953/AST-1956-send-settings-on-wire` (origin only)
- **Canon Scope:** `patt.task.dispatch-retry`, `stat.logging.debug`
- **Depends on:** [AST-1955](https://linear.app/astralcareermatch/issue/AST-1955) (`resolve_agent_settings`, already on `origin/ftr/AST-1953-agent-settings` and merged into this sub)

Agent calls stop deriving anything from a mode or brain size. `do_task` routes through AST-1955's `resolve_agent_settings`, and both LLM clients send the agent's `temperature`, `reasoning_effort` and (OpenRouter) provider object exactly as stored: an empty setting is not sent, and nothing is gated by model. An endpoint that rejects a setting fails like any other provider call and takes the existing `patt.task.dispatch-retry` path — no new failure class. The `Calling _send_to_server` debug line logs the temperature and effort actually sent. This ticket does **not** touch `config.py` / `database.py` / seed (AST-1955), `api_admin.py` / `AdminAgentPrompts.tsx` (AST-1957), or live rows (AST-1958).

## Scope gate

Every product file below is named in this ticket's `## Scope`. The tests and bibles listed there are Betty's (`qa-child`) — no test-tree edits here.

## AC map

| AC | Closed by | Notes |
|----|-----------|-------|
| 1 Provider object from the agent row | Stage 1 step 3 (merge `tier["provider"]` into `extra_body`) | Object itself is built by AST-1955's resolver; this ticket puts it on the wire unchanged. No `order` key exists anywhere in the new path. |
| 2 Empty settings send nothing | Stage 1 steps 2–3 | `temperature` only when not `None`; effort fields only when set. |
| 3 Temperature/effort as set, no gating | Stage 1 steps 1–3 (compat), Stage 1 step 2 (Anthropic) | `"none"` → `thinking: {"type": "disabled"}`; any other value → `output_config.effort`. No model lookup. |
| 4 Rejected setting = ordinary failure | No code change — failure paths untouched (Stage 1 "Failure path" note) | `PROVIDER_BALANCE_REFUSAL` matches HTTP 402 and billing substrings only; a 400 "Reasoning is mandatory…" is not classified, so it is a plain `success: False` → `provider_failed` → `_RETRY` then error state. Done-when runs the `rg` check. |
| 5 Truthful debug line | Stage 2 step 4 | Logs `temp=None` when the agent's temperature is empty. |
| Parent AC 5 (proxies gone from `src/`) | Stage 2 steps 1–3 + Stage 1 step 3 for this ticket's three files | `api_admin.py` still imports `resolve_model_brain` until AST-1957. |
| Parent AC 6 wire half (`deepseek-v4-pro`, `max_tokens: 384000` → `max_tokens == 384000`) | Stage 2 — `do_task`'s `max_tokens` logic is unchanged and `deepseek-v4-pro` has `max_tokens_floor None` (AST-1955) | AST-1955's plan deferred this stubbed-client assertion to this ticket's call-path tests (Betty). |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/anthropic.py` | New `_effort_body` helper; `send_to_anthropic` takes `reasoning_effort`, sends temperature only when set | external |
| `src/external/llm_compat.py` | Request assembly: temperature when set, effort via `_effort_body`, provider object merged into `extra_body`; thinking-from-tier branch removed | external |
| `src/core/agent.py` | Import `resolve_agent_settings`; `_agent_llm_route` rewritten; craft guard sets effort `"none"`; `_send_to_server` passes effort to the Anthropic client; truthful debug lines in `do_task` and `run_adhoc` | core |

## Wire contract (used by every stage)

| Setting (from `route["tier"]`) | Empty | Set |
|---|---|---|
| `temperature` (passed as the `temperature` argument) | not sent | `temperature: <value>` (0.0 is a value) |
| `reasoning_effort` | not sent | `"none"` → `thinking: {"type": "disabled"}`; anything else → `output_config: {"effort": <value>}` |
| `provider` (OpenRouter only; `None` elsewhere) | not sent | `provider: <object as resolved>` |

⚠️ **Decision (body fields via `extra_body`):** effort and provider go in the SDK's `extra_body`, on both clients, not the typed `output_config=` / `thinking=` kwargs. The installed SDK (anthropic 0.125.0) types `output_config.effort` as `Literal['low','medium','high','xhigh','max']`; Susan wants no vocabulary, and `extra_body` is the existing home for vendor body fields in `llm_compat` (and what its tests already record). On the wire both forms produce the same JSON keys.

⚠️ **Decision (one effort rule for both clients):** a single helper `_effort_body` in `anthropic.py`, imported by `llm_compat.py` (which already imports private parsers from `anthropic.py`). `llm_compat` no longer reads `server["thinking_off_params"]`; that config key becomes unread. It lives in `config.py` (AST-1955's file, out of this ticket's Scope), so it is left as is — noted here for Chuckles, not acted on. Using `thinking_off_params` instead was rejected: the `anthropic` server's value is `{}`, which would fail AC 3's Claude check.

## Stage 1: Clients — send settings as stored

**Done when:** `python3 -m py_compile src/external/anthropic.py src/external/llm_compat.py` passes, and the stub script below prints `OK`.

1. **`src/external/anthropic.py` — add `_effort_body`** immediately above `async def send_to_anthropic(` (after the last parser helper, keep two blank lines either side):
   ```python
   def _effort_body(reasoning_effort: Optional[str]) -> Dict[str, Any]:
       """The agent's reasoning_effort as Messages-protocol body fields, sent as stored (AST-1956).
       "none" turns thinking off; any other value goes in output_config.effort; empty sends nothing.
       No vocabulary and no per-model check — an endpoint that rejects it fails the call."""
       if not reasoning_effort:
           return {}
       if reasoning_effort == "none":
           return {"thinking": {"type": "disabled"}}
       return {"output_config": {"effort": reasoning_effort}}
   ```

2. **`src/external/anthropic.py` — `send_to_anthropic`.**
   - Signature: add `reasoning_effort: Optional[str] = None,` on the line after `temperature: Optional[float] = None,`.
   - Docstring: after the `content_blocks → messages[user].` line add `temperature / reasoning_effort → sent only when set (AST-1956).`
   - In the `api_kwargs` dict literal, delete the line `"temperature": temperature,`.
   - Immediately after the `if system_blocks: api_kwargs["system"] = system_blocks` block, add:
     ```python
             # Agent settings as stored (AST-1956): an empty one is not sent — the SDK would send null.
             if temperature is not None:
                 api_kwargs["temperature"] = temperature
             effort_body = _effort_body(reasoning_effort)
             if effort_body:
                 api_kwargs["extra_body"] = effort_body
     ```
   ⚠️ **Decision:** today `send_to_anthropic` always puts `temperature` in the kwargs; with an empty agent temperature the SDK serializes `"temperature": null` (verified against the installed SDK). Parent Functional scope 2 says an empty setting is not sent, and the debug line must be truthful, so the temperature line moves under `is not None`. This is the same request-assembly change in `send_to_anthropic` the Scope names, not a new capability.

3. **`src/external/llm_compat.py` — request assembly.**
   - Change the import `from src.external.anthropic import _parse_api_response, _parse_json_response, _parse_python_code_response` to `from src.external.anthropic import _effort_body, _parse_api_response, _parse_json_response, _parse_python_code_response`.
   - Replace these six lines (the comment through the temperature `if`):
     ```python
             # Thinking + server extras + brain-size extras (OpenRouter provider pin) are vendor body fields
             # taken verbatim from config; later wins on key collision, so the size's extras beat the server's.
             thinking_on = bool(tier.get("thinking"))
             thinking_body = (tier.get("thinking_params") or {}) if thinking_on else server["thinking_off_params"]
             api_kwargs["extra_body"] = {**thinking_body, **server["request_extras"], **tier.get("request_extras", {})}
             if temperature is not None and not thinking_on:
                 api_kwargs["temperature"] = temperature
     ```
     with:
     ```python
             # Agent settings go on the wire as stored (AST-1956): temperature when set, effort as body
             # fields, and the OpenRouter provider object — nothing gated by model. Later wins on key
             # collision, so the agent's provider object beats a server extra of the same name.
             if temperature is not None:
                 api_kwargs["temperature"] = temperature
             provider = {"provider": tier["provider"]} if tier.get("provider") else {}
             api_kwargs["extra_body"] = {**_effort_body(tier.get("reasoning_effort")), **server["request_extras"], **provider}
     ```
   - No other line in `llm_compat.py` changes.

   **Failure path:** both clients' `try/except` blocks, `classify_provider_balance_refusal`, `classify_provider_call_timeout` and the returned failure envelope are **not** edited. No logger calls are added in either client: the existing `Calling messages.create` debug line in `llm_compat` already prints the full kwargs (including `extra_body`), per `stat.logging.debug`.

4. Run the Done-when stub script (no network; patches the client seams):
   ```bash
   python3 - <<'EOF'
   import asyncio
   from src.external import llm_compat as lc, anthropic as an
   cap = {}
   def fake_create(client, api_kwargs, server_id, concurrency):
       cap.clear(); cap.update(api_kwargs)
       raise RuntimeError("Error code: 400 - Reasoning is mandatory for this endpoint and cannot be disabled")
   lc._create = fake_create
   blk = [{"type": "text", "text": "hi"}]
   def compat(tier, temperature=None):
       r = asyncio.run(lc.send_to_llm_compat(blk, server_id="openrouter", sku="openai/gpt-oss-120b",
                                             tier=tier, api_key="k", temperature=temperature, max_tokens=10))
       assert r["success"] is False and not r.get("failure_class"), r
       return dict(cap)
   c = compat({"provider": {"quantizations": ["bf16"], "allow_fallbacks": True}})
   assert c["extra_body"] == {"provider": {"quantizations": ["bf16"], "allow_fallbacks": True}} and "temperature" not in c, c
   c = compat({"provider": {"allow_fallbacks": True}, "reasoning_effort": "high"}, temperature=0.3)
   assert c["temperature"] == 0.3 and c["extra_body"]["output_config"] == {"effort": "high"} and "thinking" not in c["extra_body"], c
   c = compat({"provider": None, "reasoning_effort": "none"})
   assert c["extra_body"] == {"thinking": {"type": "disabled"}}, c
   class Msgs:
       def create(self, **kw):
           cap.clear(); cap.update(kw); raise RuntimeError("stub")
   class Client: messages = Msgs()
   an.Anthropic = lambda **kw: Client()
   def claude(**kw):
       asyncio.run(an.send_to_anthropic(blk, model_code="claude-sonnet-4-6", api_key_override="k", max_tokens=10, **kw))
       return dict(cap)
   c = claude()
   assert "temperature" not in c and "extra_body" not in c, c
   c = claude(temperature=0.3, reasoning_effort="high")
   assert c["temperature"] == 0.3 and c["extra_body"] == {"output_config": {"effort": "high"}}, c
   assert claude(reasoning_effort="none")["extra_body"] == {"thinking": {"type": "disabled"}}
   print("OK")
   EOF
   ```

## Stage 2: Core — route through the settings resolver, truthful debug lines

**Done when:** `python3 -m py_compile src/core/agent.py` passes; `python3 -c "import src.core.agent"` succeeds; `rg -n "_openrouter_pin|AGENT_MODE|OPENROUTER_QUANT_BRAIN_SIZE|resolve_model_brain|validate_agent_mode|brain_setting|brain_sizes|can_think|thinking_params" src/core/agent.py src/external/llm_compat.py src/external/anthropic.py` returns nothing; `rg -n "config_error|configuration_error" src/` returns nothing; and the stub script in step 6 prints `OK`.

All edits in `src/core/agent.py`.

1. **Config import (line ~60).** In the `from src.utils.config import (` block, replace `resolve_model_brain,` with `resolve_agent_settings,`.

2. **`_agent_llm_route` (~1822–1834).** Replace the whole function with:
   ```python
   def _agent_llm_route(agent_row: Dict[str, Any]) -> Dict[str, Any]:
       """Agent model_id + plain settings → resolve_agent_settings route (server, SKU, tier) (AST-1956).
       Raises ValueError on a missing or unknown model_id; settings are passed through unchecked."""
       aid = agent_row.get("agent_id")
       model_id = (agent_row.get("model_id") or "").strip()
       if not model_id:
           raise ValueError(f"Agent '{aid}' has no model_id configured.")
       return resolve_agent_settings(model_id, agent_row)
   ```
   `agent_row` comes from `database.get_agent` (public view), so list settings are already `list[str]` and fallbacks a `bool` (AST-1955 Stage 2). `task_llm_server_id` / `task_llm_server_id_or_none` are unchanged; `get_llm_model` still raises `ValueError`, which `task_llm_server_id_or_none` already catches.

3. **`_send_to_server` (~1918–1921).** Change the Anthropic return line to:
   ```python
           return await send_to_anthropic(
               user_blocks, model_code=sku, api_key_override=api_key, debug=debug,
               reasoning_effort=tier.get("reasoning_effort"), **common,
           )
   ```
   Keep the comment above it. The compat line is unchanged (it already passes `tier`, which carries `reasoning_effort` and `provider`).

4. **`do_task` call path (~2068–2094 and ~2258–2261).**
   - Replace the comment
     `# AST-1879: the agent row's model + brain size pick the server, SKU, and tier. Contact Estelle`
     `# is her own agent row (AST-1878), so there is no conversational brain override.`
     with
     `# AST-1879 / AST-1956: the agent row's model + plain settings pick the server, SKU, and tier.`
     `# Contact Estelle is her own agent row (AST-1878), so there is no conversational override.`
   - Replace `# AST-1948: the agent's mode decides temperature (resolve_model_brain); the agent row has none.` with `# AST-1956: temperature is the agent row's own setting, sent as stored (None → not sent).` The line `agent_temperature = tier["temperature"]` stays.
   - In the craft-rubric block, replace
     ```python
             # AST-1380 Decision A: thinking shares max_tokens with the JSON answer —
             # disable thinking so craft criteria are not starved mid-string.
             tier = {**tier, "thinking": False}
     ```
     with
     ```python
             # AST-1380 Decision A: thinking shares max_tokens with the JSON answer —
             # force thinking off (effort "none") so craft criteria are not starved mid-string.
             tier = {**tier, "reasoning_effort": "none"}
     ```
     The `CRAFT_RUBRIC_MAX_TOKENS` floor and the `max_tokens_floor` block are unchanged.
   - Replace the `Calling _send_to_server` debug call with:
     ```python
         logger.debug(
             "Calling _send_to_server: [task_key=%s, server=%s, model=%s, max_tokens=%s, temp=%s, effort=%s, skip_cache=%s, candidate=%s]",
             task_key, server_id, sku, agent_max_tokens, agent_temperature, tier.get("reasoning_effort"), skip_cache, candidate_id or "",
         )
     ```
     The `_send_to_server(...)` call and the `Response from _send_to_server` line are unchanged.

   ⚠️ **Decision (craft guard):** "forces thinking off" now means `reasoning_effort = "none"`, which the clients send as `thinking: {"type": "disabled"}` — the same body the old guard produced on every compat server. On an endpoint that mandates reasoning this 400s, exactly as it would have before; per Susan that is an ordinary failure. On Claude direct the guard now sends `thinking: disabled` explicitly (previously nothing), which is Anthropic's default anyway.

5. **`run_adhoc` (~3334–3392).**
   - Change the error string `"run_adhoc requires server_id and tier (resolve_model_brain route)"` to `"run_adhoc requires server_id and tier (resolve_agent_settings route)"`.
   - Immediately before `result = await _send_to_server(`, add:
     ```python
         logger.debug(
             "Calling _send_to_server: [task_key=adhoc, server=%s, model=%s, max_tokens=%s, temp=%s, effort=%s, candidate=%s]",
             server_id, model_code, max_tokens, temperature, tier.get("reasoning_effort"), candidate_id or "",
         )
     ```
   - Nothing else in `run_adhoc` or `run_adhoc_workbench_test` changes: the caller (`api_admin._resolve_adhoc`, AST-1957) supplies `tier` from `resolve_agent_settings` and `temperature=tier["temperature"]`; `_send_to_server` forwards effort/provider from that `tier`.

   ⚠️ **Decision:** the parent's Component scope says of the debug line "`run_adhoc` gets the same". `run_adhoc` had no `Calling _send_to_server` line, so it gets one in the same shape (`stat.logging.debug` callee-in). The wrapper's existing `Response from run_adhoc` line covers callee-out; no response line is added inside `run_adhoc`.

6. Run the Done-when stub script (no DB, no network; patches `_send_to_server`'s clients):
   ```bash
   python3 - <<'EOF'
   import asyncio
   from src.core import agent as ag
   route = ag._agent_llm_route({"agent_id": "a", "model_id": "openai/gpt-oss-120b", "quantization": "bf16",
                                "provider_allow_fallbacks": True, "temperature": None, "reasoning_effort": None})
   assert route["server_id"] == "openrouter" and route["tier"]["provider"] == {"quantizations": ["bf16"], "allow_fallbacks": True}
   assert route["tier"]["temperature"] is None and route["tier"]["reasoning_effort"] is None
   seen = {}
   async def fake_anthropic(blocks, **kw):
       seen.update(kw); return {"success": False, "error": "stub"}
   ag.send_to_anthropic = fake_anthropic
   asyncio.run(ag._send_to_server([], server_id="anthropic", sku="claude-sonnet-4-6",
       tier={"reasoning_effort": "high"}, api_key="k", system_blocks=[], response_format=None, prompt_label="t",
       candidate_id=None, temperature=None, max_tokens=10, debug=False, task_key_uuid=None,
       no_cache_prompt_tokens=0, no_cache_live_tokens=0))
   assert seen["reasoning_effort"] == "high" and seen["temperature"] is None, seen
   print("OK")
   EOF
   ```
   The `temp=None` debug assertion (AC 5) and the full `do_task` stubbed-client checks need DB fixtures and are Betty's (`tests/component/core/test_agent.py`).

## Sequencing note (for Betty / Chuckles — not a step)

After this ticket, `import src.core.agent` works again, so `tests/component/core/` collects (AST-1955's Sequencing risk clears for that tree). `src/ui/api/api_admin.py` still imports `resolve_model_brain` until AST-1957 lands, so anything importing `api_admin` (e.g. `tests/component/ui/api/`) still fails at collection on this sub alone. Existing `test_llm_compat.py` cases that assert the AST-1947 thinking/pin bodies (`KIMI_OR_PIN`, `thinking_off_params`, `tier["thinking"]`) are invalidated by design and are Betty's to rewrite.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate


**Ticket:** AST-1956  
**Overall:** APPROVED  
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51  
**Publish ref:** `sub/AST-1953/AST-1956-send-settings-on-wire` @ `5851456ca13c86d823bd762c8f0a9925e2989a1a`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.dispatch-retry | A | | |
| stat.logging.debug | A | | |

## Traceability

1 → Stage 1 step 3 (`extra_body` provider merge) · 2 → Stage 1 steps 2–3 · 3 → Stage 1 (`_effort_body`, no tier thinking branch) · 4 → Stage 1 failure-path note + Stage 2 done-when `rg` · 5 → Stage 2 step 4 (`do_task` / `run_adhoc` debug) · parent AC 5 (`src/` proxies in these three files) → Stage 2 steps 1–3 + Stage 1 step 3 · parent AC 6 wire (`deepseek-v4-pro` / `max_tokens`) → **AC map** + unchanged `do_task` `max_tokens` (Betty stubbed-client)

## Findings

### acceptable

- **Location:** Plan structure — no `## Self-assessment`
- **Finding:** **AC map**, wire contract, and inline done-when stubs carry complexity; estimate confirm present.
- **Recommendation:** None blocking.

- **Location:** **Sequencing note**
- **Finding:** `api_admin` / `resolve_model_brain` and legacy `test_llm_compat` thinking-pin cases called out for AST-1957 and Betty.
- **Recommendation:** None.

- **Location:** Wire contract — `thinking_off_params` unread
- **Finding:** Documented as AST-1955 config leftover; no edit in this Scope.
- **Recommendation:** Optional Chuckles cleanup on a later config pass; not blocking build.

context_tokens≈65000

## Review

- **Branch:** `sub/AST-1953/AST-1956-send-settings-on-wire`
- **Build commits:** `fbcf088ae` (Stage 1 clients) · `04533705b` (Stage 2 core)
- **Build notes:** both stages executed as written; each stage's Done-when stub script printed `OK`, `import src.core.agent` succeeds, and both `rg` checks return nothing. Ruff `F` counts on the three files are unchanged from baseline (pre-existing only). No deviations.

## Radia review

[code-rubric]

**Ticket:** AST-1956  
**Publish ref:** `7aa622ec786afd3883d030719f7bdd1ab471e302` (`origin/sub/AST-1953/AST-1956-send-settings-on-wire`)  
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51  
**Overall:** CLEAN  

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.dispatch-retry | A | | |
| stat.logging.debug | A | | |

## Column diff vs plan stage

(aligned) — Joan validate: `patt.task.dispatch-retry` A, `stat.logging.debug` A.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `git diff origin/dev...origin/sub/AST-1953/AST-1956-send-settings-on-wire`
- **Finding:** Three-dot diff vs `origin/dev` includes stacked AST-1955 / AST-1957 / AST-1958 product, seed, UI, migration script, and sibling tests/bible. AST-1956 engineer commits touch only `src/external/anthropic.py`, `src/external/llm_compat.py`, and `src/core/agent.py` (`fbcf088ae`, `04533705b`).
- **Recommendation:** Score wire/routing work on those three files; treat the rest as sibling publish carry.

- **Location:** Wire contract — `thinking_off_params` in `LLM_SERVER_CONFIG`
- **Finding:** `llm_compat` no longer reads `server["thinking_off_params"]`; config key remains unused (plan defers to AST-1955 / optional later cleanup).
- **Recommendation:** Optional Chuckles/config hygiene later; not blocking this sub.

- **Location:** **Sequencing note** / stacked tip
- **Finding:** This publish ref also carries AST-1957 (`api_admin` already on `resolve_agent_settings`), so `import src.core.agent` and much of `tests/component/core/` can collect here; parent AC 5’s full-`src/` `rg` still closes on ftr rollup.
- **Recommendation:** None on AST-1956 tip.

- **Location:** Estimate confirm **3**
- **Finding:** Two client stages + core routing/debug align with confirmed points.
- **Recommendation:** None.

## What's solid

- **Stage 1:** `_effort_body` matches plan; `send_to_anthropic` omits `temperature` when `None` and merges effort via `extra_body`; `llm_compat` drops tier thinking/pin assembly and sends temperature, `_effort_body(reasoning_effort)`, and `provider` with correct merge order. `llm_compat` diff does not alter `classify_provider_*` / failure envelopes (AC 4 / `patt.task.dispatch-retry`).
- **Stage 2:** `_agent_llm_route` → `resolve_agent_settings`; craft rubric guard uses `reasoning_effort: "none"`; `_send_to_server` forwards `reasoning_effort` to Anthropic; `do_task` debug line includes `temp=%s, effort=%s`; `run_adhoc` gains matching callee-in debug. Done-when legacy-symbol `rg` clean on the three product files.
- **AC map:** Betty’s `TestAst1956SettingsOnTheWire` covers debug `temp=None`, route/settings passthrough, craft guard, and parent AC 6 wire (`deepseek-v4-pro` + `max_tokens: 384000` unchanged on send).
- **`stat.logging.debug`:** New/updated `logger.debug` callee-in lines are not gated with `if debug`; existing `Response from _send_to_server` retained.

## Recommended actions (downstream — not for Radia)

- Chuckles: append artifact, `docs(AST-1956): Radia review — clean`, push publish ref, post slim upshot `--as radia`, **Review Posted** → **User Testing** per datt.
