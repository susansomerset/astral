<!-- linear-archive: AST-1964 archived 2026-10-08 -->

## Linear archive (AST-1964)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1964/model-routing-type-and-openrouter-generation-stats-lookup-query-llm  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1963 — Query LLM Platform for Timesheet Data to Finish Batch  
**Blocked by / blocks / related:** parent: AST-1963; blocks: AST-1966

### Description

## What this implements

Adds the `direct` / `openrouter` routing type to every model (and switches the provider-object check to it), the retry constants, and the external function that fetches one call's billed cost, native tokens and host. Does **not** touch the database, `llm_compat` or `core/timesheets.py` (#2, #3). Hedy built `openrouter.py` in AST-1959.

## Citations

`stat.logging.debug`.

## Scope

* `src/utils/config.py` — **modified**. Routing type on every model; `resolve_agent_settings` reads it; a helper to get a timesheet row's routing; reconcile retry count and wait constants.
  * **New model field** — a routing type on every `LLM_MODEL_CONFIG` entry, `openrouter` for entries built by `_build_openrouter_models`, `direct` for every hand-written entry; allowed values in one config tuple.
  * **Modified validator** `validate_llm_provider_environment` — rejects a model whose routing type is missing or not an allowed value.
  * **Modified function** `resolve_agent_settings` — builds the OpenRouter provider object when the model's routing type is `openrouter`, instead of comparing `server` to the string `"openrouter"`.
  * **New helper** — routing type for a (server id, SKU) pair, the two values a timesheet row carries; raises on unknown.
  * **New constants** — reconcile retry count (default 5) and the backoff base wait (default 2 seconds, doubled after each try).
* `src/external/openrouter.py` — **modified**. Fetch one call's generation stats by generation id and key.
  * **New function** — takes a generation id and an API key, calls OpenRouter's generation-stats endpoint, returns billed total cost, native prompt / completion / cached / reasoning token counts and serving host, or an error result when the call fails or the record isn't ready. No database or candidate access; the caller passes the key.
* `tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md`, `tests/component/external/test_openrouter.py`, `docs/test-bible/external/openrouter.md` — **modified**.

## Acceptance criteria

"Stubbed lookup" = the component-test stub of the OpenRouter generation-stats HTTP call.

1. **Routing type is the source of truth.**
   * **Check (**`test_config.py`**):** every `LLM_MODEL_CONFIG` entry built from `OPENROUTER_MODEL_TABLE` has routing `openrouter`; `kimi-k2.6`, every `claude-*` and both `deepseek-*` entries have `direct`; a model with a missing or unknown routing makes `validate_llm_provider_environment` raise.
   * **Check:** `rg -n '"openrouter"' src/external/ src/core/timesheets.py src/data/database.py` returns nothing, and `rg -n 'server"\] == "openrouter"' src/utils/config.py` returns nothing.
   * **Fails if:** any value differs, the validator accepts a bad value, or either grep hits.
2. **Lookup returns billed numbers or an error.**
   * **Check (**`test_openrouter.py`**, stubbed lookup):** a stubbed 200 with `total_cost: 0.0123`, `native_tokens_cached: 400`, `provider_name: "DeepInfra"` returns those values; a stubbed 404 and a stubbed timeout each return an error result and raise nothing.
   * **Fails if:** a value differs from the stub, or a failure raises or returns a cost.
3. **Retry then give up** (this child's part).
   * **Check (**`test_config.py`**):** retry count constant is `5` and backoff base constant is `2`.
   * **Fails if:** either constant differs.

## Boundaries

* Does **not** touch `src/data/database.py` (#2 Platform columns - Katherine) or `src/external/llm_compat.py` / `src/core/timesheets.py` (#3 Background reconcile - Ada).
* Does **not** change how direct models (Anthropic, DeepSeek, Kimi) are priced; they keep today's calculated cost.
* No sweep, no cap on backoff — the retry count bounds it.

## Notes for planning

* Cite `stat.logging.debug` — parent Architectural definition has the links.
* Platform facts (parent § Platform research): OpenRouter `GET /api/v1/generation?id=<gen-id>`, bearer key; `total_cost`, `native_tokens_prompt` / `_completion` / `_cached` / `_reasoning`, `provider_name`; stats can lag the response by a few seconds.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T02:15:29.708Z
[code-rubric] PROCEED (Commit: 3c645827b) routing and stats lookup

#### betty — 2026-10-04T02:13:12.561Z
`origin/sub/AST-1963/AST-1964-routing-and-generation-lookup` @ `3c645827b` · routing + lookup tests ready

#### joan — 2026-10-04T02:07:16.720Z
[plan-rubric] PROCEED (Commit: d51e4959f) routing and lookup plan

#### hedy — 2026-10-04T02:05:36.720Z
`origin/sub/AST-1963/AST-1964-routing-and-generation-lookup` @ `d51e4959f` · plan ready for Joan

---

# AST-1964 — Model routing type and OpenRouter generation-stats lookup

- **Ticket:** [AST-1964](https://linear.app/astralcareermatch/issue/AST-1964) · **Parent:** [AST-1963](https://linear.app/astralcareermatch/issue/AST-1963) Query LLM Platform for Timesheet Data to Finish Batch
- **Publish ref:** `sub/AST-1963/AST-1964-routing-and-generation-lookup` (origin only)
- **Canon Scope:** `stat.logging.debug`

Every `LLM_MODEL_CONFIG` entry gains a `routing` field (`direct` / `openrouter`) that becomes the single source of truth for "this call went through OpenRouter". `resolve_agent_settings` switches its provider-object check from `m["server"] == "openrouter"` to the routing field, the startup validator rejects a missing or unknown routing, a helper maps a timesheet row's (server id, SKU) to its routing, and two constants carry the reconcile retry count (5) and backoff base wait (2 s). `src/external/openrouter.py` gains `get_generation_stats(generation_id, api_key)`, which calls OpenRouter's `GET /api/v1/generation?id=…` and returns billed cost, native token counts and serving host, or an error result — never raises. This ticket does **not** touch `src/data/database.py` (AST-1963 #2, Katherine), `src/external/llm_compat.py` or `src/core/timesheets.py` (AST-1963 #3, Ada); it adds no retry loop (Ada's reconcile owns it).

## Scope gate

Every product file below is named in this ticket's `## Scope`; every function/constant below is one of the kinds its Technical scope lists (new model field + allowed-values tuple, modified validator, modified `resolve_agent_settings`, new routing helper, new retry constants; one new lookup function in `openrouter.py`). Tests and bibles listed in Scope are Betty's (`qa-child`) — no test-tree edits here.

## AC boundaries

| AC | Check | Closed here by | Closes on ftr after |
|----|-------|----------------|---------------------|
| 1 | Routing values per model; validator raises on missing / unknown | Stage 1 steps 2–4, 6 | — |
| 1 | `rg -n '"openrouter"' src/external/ src/core/timesheets.py src/data/database.py` empty; `rg -n 'server"\] == "openrouter"' src/utils/config.py` empty | Stage 1 step 5 (config grep); Stage 2 Done-when (no `"openrouter"` literal added to `src/external/`) | Siblings must not add the literal to `core/timesheets.py` / `database.py` (they look routing up via the Stage 1 helper) |
| 2 | Stubbed 200 / 404 / timeout | Stage 2 | — |
| 3 | Retry count `5`, backoff base `2` | Stage 1 step 7 | The retry loop itself is AST-1963 #3 |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `routing` on every model + `LLM_MODEL_ROUTING_TYPES`; validator check; `resolve_agent_settings` reads routing; `get_model_routing(server_id, sku)`; `TIMESHEET_RECONCILE_RETRIES` / `TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS` | utils |
| `src/external/openrouter.py` | `GENERATION_URL` constant; new `get_generation_stats(generation_id, api_key)` | external |

## Contract for AST-1963 #3 (Ada) — names used by the sibling

| Name | Where | Shape |
|------|-------|-------|
| `get_model_routing(server_id, sku)` | `src.utils.config` | `"direct"` \| `"openrouter"`; `ValueError` when no model has that server + SKU |
| `TIMESHEET_RECONCILE_RETRIES` | `src.utils.config` | `5` — total lookup attempts |
| `TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS` | `src.utils.config` | `2.0` — wait before the 2nd try; doubles each try (2, 4, 8, 16) |
| `get_generation_stats(generation_id, api_key)` | `src.external.openrouter` | success: `{"success": True, "total_cost": float, "native_tokens_prompt", "native_tokens_completion", "native_tokens_cached", "native_tokens_reasoning", "provider_name"}`; failure: `{"success": False, "error": str}` — no cost key on failure |

⚠️ **Decision (return keys):** success keys are OpenRouter's own field names verbatim (`total_cost`, `native_tokens_*`, `provider_name`). Rejected: renaming to our column names — Katherine's column names (#2) aren't fixed by this ticket, and a rename layer here would guess them. Token / host values pass through as the platform sends them (int or `None`); only `total_cost` is required.

## Stage 1: Config — routing type, validator, resolver, helper, reconcile constants

**Done when:** `python3 -c "import src.utils.config as c; c.validate_llm_provider_environment(); m=c.LLM_MODEL_CONFIG; assert all(m[s]['routing']=='openrouter' for s in c.OPENROUTER_MODEL_TABLE); assert [k for k,v in m.items() if v['routing']=='direct']==['kimi-k2.6','claude-haiku-4-5','claude-sonnet-4-6','claude-opus-4-6','deepseek-v4-flash','deepseek-v4-pro']; assert c.get_model_routing('openrouter','z-ai/glm-4.7')=='openrouter'; assert c.get_model_routing('deepseek','deepseek-v4-pro')=='direct'; assert (c.TIMESHEET_RECONCILE_RETRIES, c.TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS)==(5, 2)"` succeeds, and `rg -n 'server"\] == "openrouter"' src/utils/config.py` returns nothing.

All edits in `src/utils/config.py`.

1. **`LLM_MODEL_CONFIG` banner comment (~line 5211–5220).** After the `server              — LLM_SERVER_CONFIG id` line, add:
   ```
   #   routing             — LLM_MODEL_ROUTING_TYPES value: "openrouter" = billed cost is looked up on the
   #                         platform per call (AST-1963); "direct" = catalog price only
   ```
   Immediately **above** the banner (after `OPENROUTER_DEFAULT_MAX_TOKENS = 16000`, before the blank lines), add:
   ```python
   # Allowed LLM_MODEL_CONFIG `routing` values (AST-1963). The model's routing — not its server id — decides
   # whether a call goes through OpenRouter (provider object, platform cost lookup).
   LLM_MODEL_ROUTING_TYPES = ("direct", "openrouter")
   ```

2. **Hand-written models.** In each of the six literal entries — `kimi-k2.6`, `claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-6`, `deepseek-v4-flash`, `deepseek-v4-pro` — add `"routing": "direct",` on the line directly after that entry's `"server": …,` line.

3. **`_build_openrouter_models`.** In the dict it assigns to `LLM_MODEL_CONFIG[slug]`, add `"routing": "openrouter",` on the line directly after `"server": "openrouter",`.

4. **`validate_llm_provider_environment`.** In the `for mid, m in LLM_MODEL_CONFIG.items():` loop, directly after `get_llm_server(m["server"])`, add:
   ```python
           if m.get("routing") not in LLM_MODEL_ROUTING_TYPES:
               raise ValueError(f"LLM model {mid!r}: routing {m.get('routing')!r} not in {LLM_MODEL_ROUTING_TYPES}")
   ```
   (`m.get` so a missing key raises this `ValueError`, not `KeyError`.)

5. **`resolve_agent_settings`.** Replace `if m["server"] == "openrouter":` with `if m["routing"] == "openrouter":`. Nothing else in the function changes.

6. **New helper `get_model_routing`.** Insert directly after `get_llm_model` (before `get_sku_pricing`):
   ```python
   def get_model_routing(server_id: str, sku: str) -> str:
       """Routing type for a timesheet row's (server id, SKU) — the two values the row carries (AST-1963).
       Raises ValueError when no model has that server and SKU."""
       for m in LLM_MODEL_CONFIG.values():
           if m["server"] == server_id and m["sku"] == sku:
               return m["routing"]
       raise ValueError(f"No LLM model for server {server_id!r} and SKU {sku!r}")
   ```
   ⚠️ **Decision:** first match is returned without an ambiguity check. (server, SKU) is unique across all 101 entries today (one model id per vendor SKU, AST-1955), and two models on one server share a routing by construction, so a duplicate could not return a different answer.

7. **Reconcile constants.** Directly after `ALLOWED_TIMESHEET_PROVIDERS = tuple(LLM_SERVER_CONFIG)` (~line 5098), add:
   ```python
   # Platform cost reconcile for openrouter-routed timesheet rows (AST-1963). A not-ready / failed
   # generation-stats lookup is tried this many times in total; the wait before the 2nd try is the base,
   # doubled before each later try (2, 4, 8, 16 s). No cap — the retry count bounds it.
   TIMESHEET_RECONCILE_RETRIES = 5
   TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS = 2.0
   ```
   ⚠️ **Decision:** two flat constants beside the other timesheet config rather than a dict or a `LLM_SERVER_CONFIG["openrouter"]` sub-key. Routing type (not server) owns eligibility, so the reconcile settings don't belong on a server row; flat names give Betty's AC 3 check one obvious name each. `2.0` (float, `== 2`) matches the DeepSeek `backoff_base_seconds: 2.0` style.

8. **Header docstring (~line 21).** After the `LLM_MODEL_CONFIG  — …` line, change it to end `… → server + routing + SKU + output default/floor + pricing (AST-1851, AST-1955, AST-1963)`.

9. Run the Done-when command and grep; run `python3 -m py_compile src/utils/config.py` (build-child §7 compile/lint gate). Commit: `code(AST-1964): model routing type, routing helper, reconcile constants`.

## Stage 2: External — `get_generation_stats`

**Done when:** with `httpx.get` monkeypatched in a one-off `python3 -c` (not committed): a 200 with body `{"data": {"total_cost": 0.0123, "native_tokens_cached": 400, "provider_name": "DeepInfra"}}` returns `success True`, `total_cost == 0.0123`, `native_tokens_cached == 400`, `provider_name == "DeepInfra"`; a 404 returns `success False` with no `total_cost` key; a stub raising `httpx.ReadTimeout("t")` returns `success False` and nothing propagates. `rg -n '"openrouter"' src/external/ src/core/timesheets.py src/data/database.py` returns nothing.

All edits in `src/external/openrouter.py`.

1. **Module docstring.** Append one paragraph:
   ```
   get_generation_stats (AST-1963): one call's platform-billed cost, native token counts and serving host,
   by generation id (our agent_req_id) and the key that made the call. Never raises; retries are the caller's.
   ```

2. **Imports.** Add `import httpx` as its own third-party group: a blank line after `from typing import …`, then `import httpx`, then the existing blank line before the `src.` imports. Change `from src.utils.llm_external import normalize_provider_error` to `from src.utils.llm_external import normalize_provider_error, provider_call_http_timeout_seconds`. Add `from src.utils.integration_io import require_controlled_external_io` (alphabetical, before `src.utils.llm_external`).

3. **`__all__`** → `["probe_host", "get_batch_host", "get_generation_stats"]`.

4. **Constant.** After `_hosts_lock = threading.Lock()`, add:
   ```python
   # Generation-stats endpoint (bearer auth, ?id=<generation id>). Stats can lag the response by a few seconds.
   GENERATION_URL = "https://openrouter.ai/api/v1/generation"
   ```
   ⚠️ **Decision (URL placement):** module constant in the OpenRouter adapter. Rejected: (a) a new `config.py` constant or `LLM_SERVER_CONFIG` key — neither is a kind of change this ticket's Scope lists for `config.py`; (b) deriving from `get_llm_server("openrouter")["base_url"]` — puts the `"openrouter"` literal in `src/external/`, which AC 1's grep forbids; (c) finding the server via a model whose routing is `openrouter` — indirect for a single endpoint. This file is already OpenRouter-only, so its endpoint living here adds no server name elsewhere.

5. **New function** at the end of the file:
   ```python
   def get_generation_stats(generation_id: str, api_key: str) -> Dict[str, Any]:
       """One call's billed stats by generation id and key: {"success": True, "total_cost", "native_tokens_prompt",
       "native_tokens_completion", "native_tokens_cached", "native_tokens_reasoning", "provider_name"}, or
       {"success": False, "error"} when the call fails or the record isn't ready (404 / no total_cost). Never raises."""
       logger.debug("Calling GET generation: id=%s", generation_id)
       try:
           # Inside the try: the integration-mode guard's RuntimeError becomes an error result, not a raise.
           require_controlled_external_io("openrouter.get_generation_stats")
           resp = httpx.get(
               GENERATION_URL,
               params={"id": generation_id},
               headers={"Authorization": f"Bearer {api_key}"},
               timeout=provider_call_http_timeout_seconds(),
           )
           # Never log the key — status and body only.
           logger.debug("Response from GET generation: id=%s status=%s body=%s", generation_id, resp.status_code, resp.text)
           if resp.status_code != 200:
               return {"success": False, "error": f"Generation stats HTTP {resp.status_code}: {normalize_provider_error(resp.text, fallback='empty body')}"}
           data = (resp.json() or {}).get("data") or {}
           if data.get("total_cost") is None:
               return {"success": False, "error": "Generation stats not ready: no total_cost"}
           return {
               "success": True,
               "total_cost": float(data["total_cost"]),
               "native_tokens_prompt": data.get("native_tokens_prompt"),
               "native_tokens_completion": data.get("native_tokens_completion"),
               "native_tokens_cached": data.get("native_tokens_cached"),
               "native_tokens_reasoning": data.get("native_tokens_reasoning"),
               "provider_name": data.get("provider_name"),
           }
       except Exception as e:
           err = f"Generation stats lookup failed: {normalize_provider_error(e)}"
           logger.debug("Response from GET generation: id=%s error=%s", generation_id, err)
           return {"success": False, "error": err}
   ```
   ⚠️ **Decision (sync):** a plain synchronous `httpx.get`. AST-1963 #3 runs the reconcile off the caller's event loop so it outlives the batch; a blocking call with `time.sleep` backoff in that worker is the simplest fit and keeps this function free of loop ownership. Rejected: `async def` with `httpx.AsyncClient` — forces the caller to own a loop in its background worker.

   ⚠️ **Decision (timeout):** `provider_call_http_timeout_seconds()` (the existing `PROVIDER_CALL_BUDGET` 600 s) — no new limit invented. A tighter stats-specific timeout would be a new limit; raise it with Susan if wanted.

   ⚠️ **Decision (not-ready):** any non-200 (OpenRouter answers 404 while stats lag) and a 200 whose `data.total_cost` is missing/null are both error results; the caller decides whether to retry. No status-code classification here.

   ⚠️ **Decision (logging):** failures are logged at **debug** only (call-in / response-out per `stat.logging.debug`); the per-row WARNING after the last failed try belongs to the caller's reconcile (#3), so one failed attempt here does not emit a warning per try.

6. Run the Done-when one-off and grep; `python3 -m py_compile src/external/openrouter.py` (build-child §7 compile/lint gate). Commit: `code(AST-1964): OpenRouter generation-stats lookup`.

## Execution contract

The plan is binding. Steps in order, stages in order; no added files, modules, configs or dependencies (`httpx` is already a dependency — `src/external/llm_compat.py` imports it). Ambiguity, drift (e.g. a referenced line or function has moved or changed signature) or a literal step failing → stop and comment on the parent [AST-1963](https://linear.app/astralcareermatch/issue/AST-1963):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1964
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `sub/AST-1963/AST-1964-routing-and-generation-lookup` @ `d51e4959f`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | B | | Stage 2: `get_generation_stats` commits to ungated `logger.debug` call-in/response-out (no API key), failures at debug only; retry-loop debug deferred to AST-1963 #3 per boundaries |

## Traceability

AC1→Stage 1 (routing, validator, resolver, grep); AC2→Stage 2 (`get_generation_stats`); AC3→Stage 1 step 7 (reconcile constants). No orphan stages; parent AC 4–8 correctly out of child scope.

## Findings

### discuss — Canon Scope gap (not scored)

- **Location:** Stage 2 step 4 (`GENERATION_URL` module constant)
- **Finding:** `astral.config.config-source-of-truth` plainly governs a new HTTP endpoint URL but is not on this ticket’s frozen Canon Scope list.
- **Recommendation:** Archie may add it at Discussion if config-as-SoT should be enforced on this child; engineer’s documented rejection of `config.py` / `LLM_SERVER_CONFIG` is coherent for AC1 grep boundaries.

### acceptable — Definition fidelity

- **Location:** Boundaries / Files Changed
- **Finding:** Plan stays inside child `## Scope` (only `config.py`, `openrouter.py` for product code; no `database.py`, `llm_compat.py`, `core/timesheets.py`).
- **Recommendation:** None.

### acceptable — Sibling contract

- **Location:** `## Contract for AST-1963 #3`
- **Finding:** Names, shapes, and constant values match parent Technical scope and child AC; Ada-facing table is explicit.
- **Recommendation:** None.

### acceptable — Adversarial / DRY

- **Location:** Stages 1–2
- **Finding:** Reuses `normalize_provider_error`, `require_controlled_external_io`, `provider_call_http_timeout_seconds`; routing replaces `server == "openrouter"` per parent intent; no sibling scope creep.
- **Recommendation:** None.

### acceptable — Self-assessment

- **Location:** `## Estimate`
- **Finding:** No formal self-assessment block; estimate confirm (3) matches ticket and plan depth.
- **Recommendation:** Optional polish only.

context_tokens≈28000

## Review

- **Branch:** `sub/AST-1963/AST-1964-routing-and-generation-lookup`
- **Build commits:** `5070a23a7` (Stage 1 config) · `9780cf061` (Stage 2 OpenRouter lookup)
- **Build notes:** both stages executed as written; each stage's Done-when checks passed (Stage 2 via a stubbed `httpx.get` one-off: 200 / 404 / `ReadTimeout` / null `total_cost`), the validator raises on missing and unknown routing, and both AC 1 `rg` checks return nothing. `py_compile` clean on both files (no Python linter is installed on this host). Existing `test_config.py` / `test_openrouter.py` run: 21 failures, identical before and after this build (pre-existing — e.g. `TestAst1562RetentionConfig`). `validate-sub-log.sh --stage=build` run against `dev` because `origin/ftr/AST-1963` is not published yet: ok. No deviations.

## Radia review

[code-rubric]
**Ticket:** AST-1964
**Publish ref:** `d86e642ae39ffdb7c2da7f5a162e599bc733c710` (`origin/sub/AST-1963/AST-1964-routing-and-generation-lookup`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |

## Column diff vs plan stage

- `stat.logging.debug` — Joan **B** (plan text commitment) → Radia **A** (`get_generation_stats` delivers ungated `logger.debug` call-in / response-out on success, HTTP failure, and exception paths; API key never logged; full `resp.text` on HTTP response line)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Canon Scope (off-list, not scored):** `astral.config.config-source-of-truth` would judge `GENERATION_URL` in `src/external/openrouter.py`. Frozen list is only `stat.logging.debug`. Joan flagged this at plan; the issue doc documents the rejection of `config.py` / `LLM_SERVER_CONFIG` for AC1 grep boundaries. **Default (unchanged):** keep the module constant per plan; Archie amends Canon Scope at Discussion only if SoT should bind this child.
- **Plan fidelity:** `origin/dev...origin/sub/AST-1963/AST-1964-routing-and-generation-lookup` matches Stages 1–2 — routing on all models, validator, `resolve_agent_settings` / `get_model_routing`, reconcile constants (`5`, `2.0`), `get_generation_stats` contract, no `database.py` / `llm_compat.py` / `timesheets.py` product edits.
- **Estimate:** Confirm **3** — footprint (`config.py`, `openrouter.py`, Betty tests/bibles) fits.
- **Cross-ticket:** `Relations: (none)` — no sibling product scope in diff.
- **AC grep:** `server"] == "openrouter"` absent in `config.py`; `'"openrouter"'` absent under `src/external/`, `timesheets.py`, `database.py` on tip.

## What's solid

- Routing is the provider-object switch (`m["routing"] == "openrouter"`), with table-built models `openrouter` and six hand-written `direct` entries.
- `get_generation_stats` never raises; integration-mode guard, 404/500, not-ready `total_cost`, and `httpx` timeout map to `{"success": False, "error": ...}` without a cost key.
- Component tests cover AC 1–3 including debug lines with `log_debug` enabled and key absence from log records.

## Recommended actions (downstream — not for Radia)

- Chuckles: append this artifact, `docs(AST-1964): Radia review — clean`, post slim upshot `--as radia`, move to **Review Posted**; datt **PROCEED** → **User Testing** (no fix-now canon).
- Optional: if Susan wants every OpenRouter URL in `config.py`, that is a **parent / Canon Scope** change, not a resolve-child tweak on this frozen list.

context_tokens≈52000
