# AST-2239 — Provider wrappers inside the worker

- **Linear:** [AST-2239](https://linear.app/astralcareermatch/issue/AST-2239) · parent [AST-2235](https://linear.app/astralcareermatch/issue/AST-2235) (Build astral-agent microservice)
- **Publish ref:** `origin/sub/AST-2235/AST-2239-provider-wrappers-inside-the-worker`
- **Assignee:** Hedy
- **Canon Scope:** `astral.layers.core-vs-external-bright-line`; `astral.config.secrets-and-env-specific-from-environ`; `stat.logging.error`; `patt.agent.provider-io-via-queue` (pending Archie)

Replace the AST-2237 stub executor with service-local OpenRouter / Anthropic / llm-compat (DeepSeek) HTTP wrappers that run from an assembled `request` jsonb (tools / schema / settings included), read no platform SQLite, and return usage + `failure_class` aligned with today's platform clients. Retire the in-process `send_to_*` call surfaces on `src/external/{anthropic,llm_compat}.py` that agent / Ad Hoc used (thin stubs). Does **not** cut `do_task` / Ad Hoc over to the queue (AST-2240), does **not** own the platform enqueue client (AST-2238), and does **not** own Railway / CI fence (AST-2241).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `service/astral_agent/` — **modified** — provider-wrapper executor modules.
- `src/external/anthropic.py` / `llm_compat.py` / `openrouter.py` — **modified** — retire in-process call surfaces agent/Ad Hoc used (plan-child picks thin stub vs delete).

Every **Files Changed** row is under those paths. Technical kinds covered: service-local provider HTTP from assembled request jsonb; env / request secrets (no hardcoded keys); usage + `failure_class` parity with today's clients where practical; thin-stub retirement of `send_to_*`. No `src/core/agent.py`, no `src/external/astral_agent.py`, no `src/utils/config.py`, no `database.py`, no `railway.toml`, no CI fence, no tests/bible (Betty).

**Prerequisite (AST-2237):** Builder works on a tip that already contains `service/astral_agent/{executor,worker,jobqueue,app,requirements}.py` from `origin/sub/AST-2235/AST-2237-astral-agent-queue-schema-and-worker-skeleton` (or `origin/ftr/AST-2235-astral-agent-microservice` once rollup lands). If `sync-child.sh … --ftr AST-2235` skips because the short ftr name is missing, re-run with `--ftr AST-2235-astral-agent-microservice` or merge `origin/sub/AST-2235/AST-2237-…` into this sub before Stage 1. Stop + parent comment if the stub tree is absent.

## Canon notes (planner)

- **`astral.layers.core-vs-external-bright-line` (read in full):** Provider HTTP is I/O. It lives in `service/astral_agent/` (service external boundary), not in `src/core`. Platform `src/external/*` keeps receipts / helpers that are not chat send; live chat HTTP leaves those modules.
- **`astral.config.secrets-and-env-specific-from-environ` (read in full):** `ASTRAL_DATABASE_URL` already required by AST-2237 settings. Provider API keys for agent work are **platform-assembled into `request["api_key"]`** (candidate key resolution stays on the platform — AST-2240). Service must not hardcode keys, must not read Stytch/candidate tables, and must not put secrets in `agent_config.py`. Optional env fallback keys are **not** used for the agent path (today `api_key` is always non-empty when `_send_to_server` runs).
- **`stat.logging.error`:** Service has no `src.utils.logging` — keep AST-2237 Railway JSON console logging. On unhandled executor crash: one `logger.exception` at the worker handler (already present). Soft provider failures (`success: False` result dict) are **not** exceptions — log **warning** once with `failure_class` + short error (no secret / no full request body).
- **`patt.agent.provider-io-via-queue`:** pending Archie — **id-only**, not scoring law this pass. Still implement the worker half of the queue contract AST-2237/2238 named.

## Request / result contract (owned by this ticket)

AST-2238 treats `request` as opaque jsonb. AST-2240 will build this shape; this ticket is the authority for field names.

### `request` (jsonb)

| Key | Required | Meaning |
|-----|----------|---------|
| `protocol` | yes | `"anthropic"` or `"anthropic_compat"` (same vocabulary as `LLM_SERVER_PROTOCOLS`) |
| `server_id` | yes | Label for logs / `host` echo (`anthropic` / `openrouter` / `deepseek` / `kimi` / …) — **not** looked up in config |
| `model` | yes | SKU / model_code string |
| `api_key` | yes | Non-empty string from the platform (candidate server key) |
| `messages` | yes | Anthropic Messages `messages` list (user content blocks already assembled) |
| `system` | no | System blocks (cache_control allowed) |
| `max_tokens` | yes | int |
| `temperature` | no | float; omit when unset (do not send null) |
| `extra_body` | no | dict merged into SDK `extra_body` (effort, `provider` object, `request_extras`, thinking-off) |
| `extra_headers` | no | dict (e.g. anthropic-beta for documents) |
| `tools` / `tool_choice` | no | Forced-tool / web_search wire already shaped by the platform |
| `base_url` | if `anthropic_compat` | Compat endpoint base |
| `auth` | if `anthropic_compat` | `"x-api-key"` or `"bearer"` |
| `concurrency` | no | dict: `rate_limit_retries`, `backoff_base_seconds`, `backoff_max_seconds`, `max_concurrent`, `exhausted_stops_batch` (mirror today's server concurrency) |
| `probe` | no | bool — when true and `server_id` routing is OpenRouter-shaped, run today's host-probe before the real call |
| `routing` | no | `"openrouter"` \| `"direct"` \| omit — gates probe / `require_parameters` behavior that today uses `get_model_routing` |
| `timeout_seconds` | no | default `600` (copy of `PROVIDER_CALL_BUDGET["timeout_seconds"]`) |
| `grace_seconds` | no | default `10` |
| `max_retries` | no | default `0` (SDK retries) |
| `batch_id` | no | string — OpenRouter host pin key when `probe` is true |

⚠️ **Decision — platform assembles wire + api_key; service never reads `LLM_SERVER_CONFIG`:** Import fence forbids `src/`. Catalog / candidate key / token resolve stay on the platform (parent locked). Service is dumb HTTP.

⚠️ **Decision — soft provider failures complete the job (`done`), not `failed`:** Today's `send_to_*` return `{success: False, failure_class, error}` without raising. Keep that: `executor.execute` returns that dict → `jobqueue.complete`. Use `jobqueue.fail(..., error_class=…)` only for malformed request / unhandled crash (no usable result dict). Ada's client pass-through `error_class` covers transport failures; AST-2240 reads `result["failure_class"]` on `done` rows for provider soft-fails.

### `result` (json dict → zlib in `agent_job.result`)

Success:

```python
{
  "success": True,
  "api_response": "<extracted text or forced-tool JSON string>",
  "stop_reason": "<str or null>",
  "response_id": "<provider id or null>",
  "usage": {
    "input_tokens": int,
    "output_tokens": int,
    "cache_read_input_tokens": int,
    "cache_creation_input_tokens": int,
  },
  "host": "<optional pinned host label>",
  # No parsed_response, no record_timesheet side effects — decode + timesheet stay on platform (parent).
}
```

Soft failure: same keys with `"success": False`, `"error": "<non-empty str>"`, `"failure_class": "<str>"`, zeroed `usage` when unknown.

`failure_class` strings to emit when practical (copy literals — do not import `src`):

| Class | When |
|-------|------|
| `provider_call_timeout` | wall-budget / SDK timeout |
| `provider_balance_refusal` | 402 / balance substrings |
| `provider_rate_limit` | 429 after retries when `exhausted_stops_batch` |
| `provider_probe_failure` | OpenRouter probe failed (non-429) |
| `provider_empty_response` | hollow response (missing stop, zero tokens, no content) |
| `max_tokens` | truncation / max_tokens stop path (same string as today) |
| `bad_request` | missing required request keys / wrong types (job `failed`) |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `service/astral_agent/requirements.txt` | Add `anthropic`, `httpx` pins matching platform ranges | service |
| `service/astral_agent/providers/__init__.py` | Package marker | service |
| `service/astral_agent/providers/errors.py` | Local failure_class literals + classify helpers + call-budget await | service |
| `service/astral_agent/providers/anthropic_provider.py` | Native Anthropic Messages HTTP | service |
| `service/astral_agent/providers/llm_compat_provider.py` | Anthropic-compat (DeepSeek / Kimi / OpenRouter protocol path) | service |
| `service/astral_agent/providers/openrouter_provider.py` | Host probe / batch host pin (today's `openrouter.get_batch_host` behavior) | service |
| `service/astral_agent/executor.py` | Replace stub: validate request → dispatch provider → return result dict | service |
| `service/astral_agent/worker.py` | Soft-fail logging; map raised `ProviderJobError` → `fail(error_class=…)`; drop stub-only log wording | service |
| `service/astral_agent/logging_util.py` | Add `providers` logger names to `_OWN_LOGGERS` | service |
| `src/external/anthropic.py` | Thin-stub `send_to_anthropic`; keep `getTimestampPrefix` / `get_receipt` / pure helpers still used elsewhere | external |
| `src/external/llm_compat.py` | Thin-stub `send_to_llm_compat`; keep `get_receipt` | external |
| `src/external/openrouter.py` | Module note + no chat-send surface (probe/receipt stay for platform timesheet / future platform-side use until AST-2240 moves probe into the assembled request path) | external |

**Out of this ticket:** `src/core/agent.py` cutover (AST-2240); `src/external/astral_agent.py` / `ASTRAL_AGENT_CONFIG` (AST-2238); `railway.toml` / CI fence (AST-2241); `src/data/database.py`; `tests/` / `docs/test-bible/**`.

## Stage 1: Requirements + local error/budget helpers

**Done when:** `service/astral_agent/requirements.txt` installs with anthropic+httpx; `providers/errors.py` exposes classify helpers and `await_provider_call_with_budget` without importing `src`; stub `executor.execute` still behaves as AST-2237 until Stage 2.

1. In `service/astral_agent/requirements.txt`, keep fastapi/uvicorn/asyncpg pins and append (match platform `requirements.txt` ranges):
   ```
   anthropic>=0.7.0,<1.0.0
   httpx>=0.27.0,<1
   ```
2. Create `service/astral_agent/providers/__init__.py` (empty or package docstring only).
3. Create `service/astral_agent/providers/errors.py`:
   - Copy the **literal** failure_class strings / status codes / substrings / budget numbers from today's `PROVIDER_*` / `PROVIDER_CALL_BUDGET` blocks in `src/utils/config.py` into module-level dicts (`BALANCE_REFUSAL`, `RATE_LIMIT`, `PROBE_FAILURE`, `EMPTY_RESPONSE`, `CALL_BUDGET`). Comment: mirror platform; change both sides together when classes change.
   - `class ProviderJobError(Exception)` with `.error_class: str` and `.detail: str` (for malformed request → worker `fail`).
   - Port `classify_provider_balance_refusal`, `classify_provider_rate_limit`, `classify_provider_call_timeout`, `non_empty_provider_error`, `is_unusable_provider_response`, `extract_api_response_text`, and `await_provider_call_with_budget` from `src/utils/llm_external.py` — stdlib/asyncio/`anthropic` response attribute access only; **no** `src` imports.
4. In `logging_util.py`, extend `_OWN_LOGGERS` with `"providers"`, `"providers.anthropic_provider"`, `"providers.llm_compat_provider"`, `"providers.openrouter_provider"`, `"providers.errors"`.

⚠️ **Decision — duplicate classify literals under `providers/errors.py`:** Fence forbids sharing `src/utils`. Small fixed tables beat inventing a third shared package.

**Stage 1 commit message:** `code(AST-2239): provider error helpers and requirements`

## Stage 2: Provider modules + live `executor.execute`

**Done when:** `await executor.execute(valid_anthropic_request)` performs a real Messages create (or returns a soft-fail dict); compat + OpenRouter probe paths exist; invalid request raises `ProviderJobError("bad_request", …)`; no `src` imports under `service/astral_agent/`; entity-ban / app_log greps still clean.

1. Create `service/astral_agent/providers/anthropic_provider.py`:
   - `async def send(request: dict) -> dict` implementing today's native Anthropic path from `src/external/anthropic.py` **minus** `record_timesheet`, `require_controlled_external_io`, debug logger flag, and `parsed_response` / schema parse branches.
   - Build `Anthropic(api_key=request["api_key"], timeout=httpx.Timeout(timeout_seconds), max_retries=max_retries)` — never `os.environ["ANTHROPIC_API_KEY"]` for this path.
   - `messages.create` kwargs from request: `model`, `max_tokens`, `messages`, optional `system`, `temperature`, `extra_body`, `extra_headers`, `tools`, `tool_choice`.
   - Success → result contract above (`extract_api_response_text`; forced-tool: if tool_use block present, JSON-dump `input` as `api_response` text — same idea as today's forced-tool parse, without platform schema validation).
   - Empty/unusable → soft-fail `provider_empty_response`.
   - `max_tokens` stop → soft-fail `max_tokens` when today's truncation condition matches (port the condition from `anthropic.py`, not a new heuristic).
   - Exceptions → soft-fail dict with `failure_class` from classify helpers (timeout / balance); else omit `failure_class` (platform defaults to `provider_failed`).
2. Create `service/astral_agent/providers/openrouter_provider.py`:
   - Port `get_batch_host` / probe request shaping from `src/external/openrouter.py` into service-local functions that take an async `_send(kwargs)` callback and `batch_id` + `api_kwargs` — **no** `LLM_SERVER_CONFIG` / `src` imports.
   - Keep behavior: probe when requested; pin host; surface probe errors as strings for the compat caller.
3. Create `service/astral_agent/providers/llm_compat_provider.py`:
   - `async def send(request: dict) -> dict` for `protocol == "anthropic_compat"`.
   - Client: `Anthropic(base_url=request["base_url"], api_key=request["api_key"], …)` with auth style from `request["auth"]` matching today's `_get_client` (bearer vs x-api-key).
   - Apply `extra_body` / tools as provided; when `probe` is true and `routing == "openrouter"`, call `openrouter_provider` host pin before the real create (pass `batch_id`).
   - Rate-limit retry loop from `concurrency` (same numeric behavior as today's `_create` retries) — copy the retry structure from `llm_compat.py`, not a new backoff invention.
   - Soft-fail classes: probe / rate_limit / balance / empty / max_tokens / timeout — same strings as Stage 1 tables.
4. Replace `service/astral_agent/executor.py`:
   ```python
   async def execute(request: dict) -> dict:
       # validate required keys → ProviderJobError("bad_request", ...)
       # protocol == "anthropic" → anthropic_provider.send
       # protocol == "anthropic_compat" → llm_compat_provider.send
       # else → ProviderJobError("bad_request", ...)
   ```
   - Docstring: AST-2239 live wrappers; signature stable for `worker.py`.
   - **No** network in the validator; **no** entity / `do_task` / `TASK_CONFIG` strings anywhere in the package.

⚠️ **Decision — thin port of wire behavior, drop timesheet + parse:** Parent: dumb provider I/O; timesheet/decode on platform. Result carries usage + raw text so AST-2240 can `_store_response_block` / `record_timesheet_entry` after await.

⚠️ **Decision — OpenRouter stays a helper under `providers/`, not a third `protocol` value:** Today OpenRouter is `anthropic_compat` + routing/probe. Keep one compat entrypoint; `openrouter_provider.py` is the probe/pin module the ticket Scope named.

**Stage 2 commit message:** `code(AST-2239): service provider wrappers and executor`

## Stage 3: Worker glue + platform `send_to_*` thin stubs

**Done when:** Worker logs provider soft-fails at warning, maps `ProviderJobError` → `jobqueue.fail` with that `error_class`, and no longer mentions stub success; `send_to_anthropic` / `send_to_llm_compat` raise a clear retired error; `get_receipt` / `getTimestampPrefix` / openrouter probe+receipt helpers still importable; AC greps for entity / app_log strings clean on `service/astral_agent/`.

1. In `service/astral_agent/worker.py` `_run_job`:
   - `from providers.errors import ProviderJobError` (or `providers.errors` depending on package layout — use the same import style as `import executor` today: flat modules on `sys.path=/app`).
   - On `ProviderJobError`: log **error** once with class+detail (no traceback required if detail is enough; use `logger.error` with facts), then `jobqueue.fail(..., error=detail[:2000], error_class=exc.error_class, retry_in_seconds=None)`.
   - On other exceptions: keep `logger.exception` + `fail(..., error_class="executor_error", …)` (rename from `stub_error`).
   - On success return: if `result.get("success") is False`, `_log.warning` once with `failure_class` + truncated error; still `jobqueue.complete`.
   - Info done line: replace `stub` with `server_id`/`model` from request when present (`request.get("server_id")`, `request.get("model")`) — never log `api_key` or full messages.
2. Platform thin stubs (⚠️ **Decision — thin stub, not delete:** other helpers and Betty fixtures still import these modules; AST-2240 removes call sites):
   - `src/external/anthropic.py`: `send_to_anthropic` body becomes raise:
     ```python
     raise RuntimeError(
         "send_to_anthropic retired (AST-2239); use src.external.astral_agent.submit with an assembled provider request"
     )
     ```
     Keep `getTimestampPrefix`, `get_receipt`, and any pure helpers still referenced outside agent send.
   - `src/external/llm_compat.py`: same raise pattern for `send_to_llm_compat`; keep `get_receipt`.
   - `src/external/openrouter.py`: add module docstring that chat HTTP lives in `service/astral_agent/providers/`; leave `probe_host` / `get_batch_host` / `get_receipt` implemented for any remaining platform callers until AST-2240 stops using them in-process (no chat `send_to` exists here today).
3. Sanity greps before stage done (stop + parent comment on hit):
   - `rg -n "from src\\.|import src|do_task|run_next|entity_id|TASK_CONFIG|dispatch_" service/astral_agent/` → no matches.
   - `rg -n "app_log|astral\\.db|save_agent_data|add_log_entry" service/astral_agent/` → no matches.
   - `rg -n "async def send_to_anthropic|async def send_to_llm_compat" src/external/` → stubs still defined (raise body).
   - Confirm stubs raise on call: `python -c` importing and awaiting is optional; reading the raise line is enough for this ticket.

⚠️ **Decision — stub now, cutover later:** Scope requires retiring agent/Ad Hoc call surfaces on this ticket. Production `do_task` stays on `send_to_*` until AST-2240 — that sibling must land before this sub is the sole provider path on `dev`. Do not partially rewrite `agent.py` here.

**Stage 3 commit message:** `code(AST-2239): worker error_class glue and send_to stubs`

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each with `git push origin HEAD:sub/AST-2235/AST-2239-provider-wrappers-inside-the-worker`.
- Do not add files outside **Files Changed**. Do not implement platform enqueue, `do_task` cutover, railway.toml, or CI fence.
- Ambiguity / drift → stop and comment on **parent** AST-2235 with the Stage-blocked template from plan-child.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2239
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `53e6d8da893faa6a7379e95cdb08a03dc347abff` (`origin/sub/AST-2235/AST-2239-provider-wrappers-inside-the-worker`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.layers.core-vs-external-bright-line | A | | |
| astral.config.secrets-and-env-specific-from-environ | B | | DSN via AST-2237; provider credential on assembled `request["api_key"]`, not service `os.environ` |
| stat.logging.error | B | | Console/Railway JSON: `exception` on crash; `error` on `ProviderJobError`; warning on soft `success: False` |
| patt.agent.provider-io-via-queue | X | | pending Archie / not in `canon_clerk` active corpus; plan id-only |

(Worst grade **B** → roll-up PROCEED.)

## Traceability

Child AC: **5→S2–S3** (entity-ban greps + executor/worker); **6→S1–S2** (no hardcoded keys; `ASTRAL_DATABASE_URL` on service via AST-2237; provider secret via `request["api_key"]` — ticket wording caveat below); **7→S1 `logging_util` + S3 greps**. Stages cover child **## Scope** and parent dumb-I/O slice; no orphan stages. Parent AC **1–4, 8–12** N/A (siblings/boundaries).

## Findings

**discuss** — **AC 6 vs assembled wire.** Linear still says service reads provider keys from **environ only**; plan follows parent locked “assembled wire in” with **`api_key` in jsonb** (Canon notes + Stage 2). Align ticket AC or add a one-line plan **## Traceability** note so Radia is not torn between grep-AC and plan.

**acceptable** — `send_to_*` stubs before AST-2240; merge-order warning in Stage 3.

**acceptable** — Scope gate (service providers + three `src/external` modules only); soft-fail → `complete` matches today’s provider clients.

## R6 (summary)

Faithful to child #3 definition; no scope creep into cutover/client/railway/tests. DRY: fenced ports from `src/external/*` + `llm_external` literals. No **D**/**F**; no `fix-now`.

context_tokens≈54000

[plan-rubric] PROCEED (Commit: 53e6d8da) Service provider wrappers plan

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-2235/AST-2239-provider-wrappers-inside-the-worker` @ `14d7c04fbece2d284913c2e15edc200adadb94ee`

**Product commits:** `1dfd50c43` (Stage 1 — error helpers + requirements), `106246155` (Stage 2 — provider modules + executor), `14d7c04fb` (Stage 3 — worker glue + send_to stubs)

**Implemented:**
- `service/astral_agent/providers/` — Anthropic, compat (DeepSeek/Kimi/OpenRouter), OpenRouter host pin; failure_class literals local to the service
- `executor.execute` validates the assembled request and dispatches by `protocol`
- Soft provider failures complete the job; `ProviderJobError` → `fail(error_class=bad_request)`; other crashes → `executor_error`
- `send_to_anthropic` / `send_to_llm_compat` raise retired; `get_receipt` / `getTimestampPrefix` / OpenRouter probe+receipt stay

**Tests:** Betty at Code Complete. Do not land `do_task` cutover here (AST-2240).

**Canon (self-check):** provider HTTP stays in the service; no hardcoded keys (`request["api_key"]`); crash path logs once via worker `logger.exception`. `patt.agent.provider-io-via-queue` still pending — not scored.

## Radia review

[code-rubric]
**Ticket:** AST-2239
**Publish ref:** `af06670dacb5363f7a1e1ba274d0a04e5d5f51ce` (`origin/sub/AST-2235/AST-2239-provider-wrappers-inside-the-worker`)
**Corpus:** `b7ab2203048ce0beb2869a12200ab7fa696c8066`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.layers.core-vs-external-bright-line | A | | |
| astral.config.secrets-and-env-specific-from-environ | B | | Provider credential on assembled `request["api_key"]`; DSN remains AST-2237 `ASTRAL_DATABASE_URL` |
| stat.logging.error | B | | Service Railway JSON: `exception` on crash; `error` on `ProviderJobError`; `warning` on soft `success: False` |
| patt.agent.provider-io-via-queue | X | | pending Archie / not in `canon_clerk` active corpus; plan id-only |

(Worst **B** → roll-up **CLEAN**. `astral.layers.*` / `astral.config.*` from `canon/statutes/astral/` on corpus tip; `stat.logging.error` via `canon_clerk expand`.)

## Column diff vs plan stage

(aligned) — Joan worst **B** on `astral.config.*` and `stat.logging.error`; code matches.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **AC 6 wording vs assembled wire** — Linear AC **6** says service reads provider keys from **environ only**; plan + implementation use platform-assembled **`request["api_key"]`** (no service env fallback for agent HTTP). **@susan:** amend child AC **6** to “no hardcoded secrets; keys only via assembled request / existing `ASTRAL_DATABASE_URL` for Postgres” or keep plan-only traceability? **Default:** score against plan + parent locked dumb-I/O; no `resolve-child` code change; optional Description tweak only.

- **Merge order before `dev`** — `send_to_anthropic` / `send_to_llm_compat` now **raise immediately**; `do_task` still calls them until **AST-2240**. **@susan:** confirm parent **finish-up** lands **2240** (or full **ftr**) with **2239**, not an isolated **2239** merge to `dev`. **Default:** treat as epic rollup constraint (plan Stage 3 already warns); block isolated child merge, not a rework of stubs.

### advisory

- **sibling carry on `origin/dev...` three-dot diff:** full **AST-2237** `service/astral_agent/` skeleton, **AST-2238** issue doc, and Betty harness ride this ref; **AST-2239 product commits** (`1dfd50c43`, `106246155`, `14d7c04fb`) touch only scoped paths (providers, executor, worker glue, three `src/external` modules).
- **Territory:** `stat.logging.error` `applies_when.paths` is `src/**`; service uses AST-2237 console logging — intentional **B**, not a fence breach.
- **`src/external/openrouter.py`:** docstring notes chat HTTP in service; probe/receipt helpers remain for platform until **2240** moves probe into assembled requests — matches plan.

## What's solid

- `service/astral_agent/providers/` — fenced copies of classify/budget helpers + Anthropic / compat / OpenRouter pin paths; **no `src` imports** under providers.
- `executor.execute` validates required keys and dispatches `anthropic` vs `anthropic_compat`; malformed input → `ProviderJobError("bad_request", …)`.
- Provider HTTP uses **`request["api_key"]`** (e.g. `anthropic_provider.send`); no hardcoded key literals; entity / `app_log` ban greps clean on `service/astral_agent/`.
- Soft provider failures return `success: False` dicts → **`jobqueue.complete`** with **warning** log; `ProviderJobError` → **`fail`** with `error_class`; unhandled → **`logger.exception`** + `executor_error`.
- `send_to_anthropic` / `send_to_llm_compat` bodies are immediate **retired** `RuntimeError`; **`get_receipt` / `getTimestampPrefix`** and OpenRouter probe/receipt remain importable.
- Plan fidelity for **2239-owned deltas**; estimate **5** still fits (provider port + stub retirement + harness, not cutover/client).

## Recommended actions (downstream only — not executed in this session)

- Chuckles: append artifact, `docs(AST-2239): Radia review — clean`, push publish ref, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED** toward **User Testing** (optional Susan AC **6** text alignment only).

context_tokens≈24000

---

```
[code-rubric] PROCEED (Commit: af06670da) Service provider wrappers landed
```

## Resolution

2026-10-16 — Radia **CLEAN**, no fix-now. Discuss defaults taken (no product change):

- **AC 6:** score against the plan and parent locked dumb I/O. Provider keys stay on assembled `request["api_key"]`. `ASTRAL_DATABASE_URL` stays the Postgres secret from AST-2237. Description text not rewritten here (no live checkboxes; AC wording is Chuckles/Susan).
- **Merge order:** stubs stay. Isolated AST-2239 must not land on `dev` ahead of AST-2240; epic rollup owns that.

Advisory left as written (sibling carry on the three-dot diff, logging statute path, OpenRouter helpers until AST-2240).
