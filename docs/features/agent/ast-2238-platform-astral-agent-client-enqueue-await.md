# AST-2238 — Platform astral_agent client (enqueue/await)

- **Linear:** [AST-2238](https://linear.app/astralcareermatch/issue/AST-2238) · parent [AST-2235](https://linear.app/astralcareermatch/issue/AST-2235) (Build astral-agent microservice)
- **Publish ref:** `origin/sub/AST-2235/AST-2238-platform-astral-agent-client-enqueue-await`
- **Assignee:** Ada
- **Canon Scope:** `astral.layers.core-vs-external-bright-line`; `astral.config.secrets-and-env-specific-from-environ`; `stat.logging.error`; `stat.logging.warning`; `stat.logging.info`; `stat.logging.debug`; `patt.agent.provider-io-via-queue` (pending Archie)

Add `src/external/astral_agent.py` as the platform half of the astral-agent Postgres queue (Telescope-shaped enqueue + await + wake throttle), plus `ASTRAL_AGENT_CONFIG` keys in `src/utils/config.py`. Returns the terminal decoded result to callers. Does **not** cut `do_task` / Ad Hoc (AST-2240), does **not** implement provider HTTP (AST-2239), and does **not** touch `service/astral_agent/` (AST-2237).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/external/astral_agent.py` — **new** — platform queue client.
- `src/utils/config.py` — **modified** — agent service wake/DB/deadline/concurrency keys.

Every **Files Changed** row is one of those two paths. Technical kinds covered: insert into `agent_job`, LISTEN/poll await on `agent_job_done`, wake throttling, config keys for DSN env name / wake / deadline / pool / attempts. No `service/**`, no `src/core/agent.py`, no provider modules, no `database.py`, no CI fence, no tests/bible (Betty).

## Canon notes (planner)

- **`astral.layers.core-vs-external-bright-line` (read in full):** External owns I/O; core orchestrates. This client is the external boundary for provider-queue I/O — Postgres insert/await + optional HTTP `/wake`. Core (`agent.py`) must not open asyncpg/httpx for this path (AST-2240 will call this module only).
- **`astral.config.secrets-and-env-specific-from-environ` (read in full):** `ASTRAL_DATABASE_URL` is required at enqueue time via `os.environ[…]` (no `.get()` empty fallback, no DSN string in `config.py`). Config holds only the **env key name** (`database_url_env`), same pattern as `TELESCOPE_CONFIG`. Wake base URL envs are optional-by-design (unset → skip wake ping, jobs wait) — mirror Telescope; document as Decision.
- **`stat.logging.*`:** Use `src.utils.logging.get_logger` — error once with facts; warning for soft fails (listener down, cancel best-effort, wake skipped); succinct info on terminal `done`; debug at enqueue/wake joints. No secrets in log lines.
- **`patt.agent.provider-io-via-queue`:** pending Archie — **id-only**, not scoring law this pass. Still implement the platform half of the queue contract AST-2237 already named.

## Contract mirror (AST-2237 — do not import service code)

Copy these **names** from `service/astral_agent/jobqueue.py` on `origin/sub/AST-2235/AST-2237-…` (import fence forbids sharing modules — duplicate string constants in the platform client):

| Constant | Value |
|----------|-------|
| `_JOB_TABLE` | `"agent_job"` |
| `_WORKER_TABLE` | `"agent_worker"` |
| `_CHANNEL_NEW` | `"agent_job_new"` |
| `_CHANNEL_DONE` | `"agent_job_done"` |
| `_TERMINAL` | `("done", "failed", "cancelled")` |

Insert columns match AST-2237 SCHEMA: `(id, request, priority, max_attempts, expires_at)` with `request` as `json.dumps(...)` + `$n::jsonb` (same as Telescope client). Result decode: zlib decompress → UTF-8 → `json.loads` (mirror `decode_result` behavior; local helper, do not import service).

⚠️ **Decision — build against named contract, not a live merge of AST-2237 into this sub:** This ticket's scope is platform-only. Schema ownership stays on the worker. If `agent_job` is missing at runtime, raise connectivity with a message that the astral-agent worker has never started (same UndefinedTableError path as Telescope).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `ASTRAL_AGENT_CONFIG` block after `TELESCOPE_CONFIG` | utils |
| `src/external/astral_agent.py` | New platform queue client (enqueue/await/wake/error mapping) | external |

**Out of this ticket:** `service/astral_agent/**` (AST-2237); provider wrappers / retiring `send_to_*` surfaces (AST-2239); `src/core/agent.py` cutover (AST-2240); `railway.toml` / CI fence (AST-2241); `src/data/database.py`; `tests/` / `docs/test-bible/**`.

## Stage 1: `ASTRAL_AGENT_CONFIG` in `config.py`

**Done when:** `from src.utils.config import ASTRAL_AGENT_CONFIG` works; keys below are present; no DSN/API-key string literals added; `TELESCOPE_CONFIG` untouched.

1. In `src/utils/config.py`, immediately after the `TELESCOPE_CONFIG = {…}` block, add:

```python
# ---------------------------------------------------------------------------
# ASTRAL_AGENT_CONFIG: platform side of the astral-agent Postgres job queue.
# Provider calls are rows in agent_job (schema owned by service/astral_agent/jobqueue.py);
# the platform inserts a job and waits for the worker to write the result.
# database_url is env-only (ASTRAL_DATABASE_URL — never a code default).
# ---------------------------------------------------------------------------
ASTRAL_AGENT_CONFIG = {
    "database_url_env": "ASTRAL_DATABASE_URL",
    "job_deadline_seconds": 900,
    "max_attempts": 4,
    "poll_interval_seconds": 1.0,
    "db_pool_max_size": 10,
    "default_priority": 0,
    "worker_stale_seconds": 90,
    # Serverless astral-agent: when no worker is live, GET <base url>/wake to wake it.
    # Base url is the private address (…railway.internal:8080) from
    # ASTRAL_AGENT_BASE_URL, else the first of ASTRAL_AGENT_BASE_URLS. Unset → no wake.
    "base_url_envs": ("ASTRAL_AGENT_BASE_URL", "ASTRAL_AGENT_BASE_URLS"),
    "wake_path": "/wake",
    "wake_throttle_seconds": 30,
    "wake_timeout_seconds": 30,  # HTTP-only cold start (no Firefox)
}
```

⚠️ **Decision — `job_deadline_seconds: 900`:** Platform provider HTTP budget is 600s (`PROVIDER_CALL` / anthropic path) plus queue/wake headroom. Telescope scrape uses 600; agent jobs need more wall clock for one long provider attempt before client cancel.

⚠️ **Decision — `worker_stale_seconds: 90`:** Match AST-2237 `WORKER_STALE_SECONDS` so the platform live-worker check and the service registry agree (Telescope platform uses 60 against its own service — do not copy that number).

⚠️ **Decision — no `admin_priority` / scrape-only keys:** This client has no Surfer/admin scrape surface; keep the config block to queue + wake only.

**Stage 1 commit message:** `code(AST-2238): ASTRAL_AGENT_CONFIG queue/wake keys`

## Stage 2: `src/external/astral_agent.py` client

**Done when:** Module exposes `submit` (enqueue+await), `close_loop_resources`, and `run_one_shot`; a successful `done` row returns the decoded result dict; failed/cancelled/deadline paths raise `AstralAgentError` with a stable `failure_class`; missing `ASTRAL_DATABASE_URL` raises connectivity; wake is throttled and skipped when unset or workers are live. No imports from `service.` or `src.core`. No calls into anthropic/openrouter/llm_compat.

1. Create `src/external/astral_agent.py` structured as a **trimmed structural copy** of the Postgres-queue half of `src/external/telescope.py` (`_LoopState`, `_TelescopeQueue` → `_AstralAgentQueue`, poller, listener, wake helpers). **Do not** copy BrowserSession / PageHandle / scrape_page / HTML helpers.

2. Module docstring (required points):
   - Platform astral-agent client (AST-2238).
   - Contract mirror: `service/astral_agent/jobqueue.py` owns schema; same table/channel names; import fence forbids sharing code — change both sides together.
   - Callers (future AST-2240): enqueue assembled provider request jsonb, await terminal result; decode/grade/daisy-chain stay on the platform.

3. Imports allowed: `asyncio`, `json`, `os`, `socket`, `threading`, `time`, `uuid`, `zlib`, `typing`, `urllib.parse` (`urlsplit`/`urlunsplit`), `asyncpg`, `httpx`, `src.utils.config.ASTRAL_AGENT_CONFIG`, `src.utils.integration_io.require_controlled_external_io`, `src.utils.logging.get_logger` (and `log_debug` only if a debug joint needs the gate — prefer `get_logger().debug`).

4. Define:
   ```python
   class AstralAgentError(Exception):
       def __init__(self, failure_class: str, detail: str) -> None:
           self.failure_class = failure_class
           self.detail = detail
           super().__init__(f"[{failure_class}] {detail}")
   ```
   Queue-level `failure_class` vocabulary used by this module:
   - `connectivity_failure` — missing DSN, pool/enqueue/SQL errors, missing `agent_job` table
   - `astral_agent_timeout` — client deadline / worker `timeout` / `expired`
   - `astral_agent_cancelled` — caller cancel / row `cancelled`
   - `astral_agent_job_failed` — terminal `failed` with unknown/other `error_class`
   - Pass-through: when terminal row `error_class` is a non-empty string **not** in `{timeout, expired, cancelled}`, use that string as `failure_class` (provider classes from AST-2239 land here without a second map).

5. Helpers (mirror Telescope naming/behavior, rename logs to `astral_agent`):
   - `_decode_result(blob)` — zlib + json (same as telescope `_decode_result`).
   - `_astral_agent_wake_url()` — first non-empty of `ASTRAL_AGENT_CONFIG["base_url_envs"]` (comma-split take `[0]`), append `wake_path`; else `""`.
   - `_wake_targets(url)` — copy Telescope's getaddrinfo multi-replica expansion.

6. `_AstralAgentQueue` (per-loop pool/listener/waiters/poller; process-wide wake throttle lock):
   - `_dsn()`: `os.environ[ASTRAL_AGENT_CONFIG["database_url_env"]].strip()` inside `try`/`KeyError` → `AstralAgentError("connectivity_failure", "<env> not set")`. Empty strip after read → same error. **No** `os.environ.get` fallback to `""` for the DSN.
   - `_get_db` / `_ensure_listener` / `_poll_loop` / `aclose_current_loop` — same structure as Telescope; LISTEN on `_CHANNEL_DONE`; poll selects `id, status, result, error, error_class` for waiter ids in `_TERMINAL`.
   - `async def submit(self, request: Dict[str, Any], *, priority: Optional[int] = None) -> dict`:
     1. `require_controlled_external_io("astral_agent.submit")`
     2. Insert job (`uuid4` id, `json.dumps(request)`, priority default from config, `max_attempts`, `expires_at = now() + job_deadline_seconds`); `pg_notify(_CHANNEL_NEW, '')`.
     3. `await self._maybe_wake(db, st)` after commit.
     4. `asyncio.wait_for(shield(fut), timeout=deadline)` — on `TimeoutError`: `_cancel`, log warning, raise `AstralAgentError("astral_agent_timeout", …)`; on `CancelledError`: shield `_cancel`, re-raise.
     5. If `status == "done"`: decode result, `_log.info` short done line (job id prefix + keys present in request if any of `provider`/`model`/`task_key` exist — never log full request body or secrets), return decoded dict.
     6. Else map to `AstralAgentError` per vocabulary above (detail includes job id, status, error_class, error text).
   - `_cancel`, `_live_workers`, `_maybe_wake`, `_ping_wake`, `_ping_one` — Telescope equivalents with astral-agent table/config/log strings. Wake timeout from `wake_timeout_seconds` (30).
   - `async def healthy(self) -> bool`: `_get_db()` then `True` (does not wake).

7. Module-level `_pool = _AstralAgentQueue()`.

8. Public surface (exact names — AST-2240 will import these):
   ```python
   async def submit(request: Dict[str, Any], *, priority: Optional[int] = None) -> dict:
       """Enqueue one provider job and await its result dict (or raise AstralAgentError)."""
       return await _pool.submit(request, priority=priority)

   async def close_loop_resources() -> None:
       await _pool.aclose_current_loop()

   def run_one_shot(coro: Awaitable[Any]) -> Any:
       # same asyncio.run + finally close_loop_resources pattern as telescope.run_one_shot
       ...
   ```

⚠️ **Decision — raise `AstralAgentError`, do not return failure dicts:** Telescope-shaped client; AST-2240 maps `AstralAgentError.failure_class` into the existing provider-failure audit branch. Keeps this module free of agent success-envelope shaping.

⚠️ **Decision — `request` is opaque jsonb:** This ticket does not define provider wire fields (AST-2239 owns that). Client inserts whatever dict the caller passes. Stub executor on AST-2237 will echo it; live wrappers replace the stub later.

⚠️ **Decision — optional wake base URL via `.get` on env:** Same operational exception as Telescope: wake is best-effort serverless ping; unset means "jobs wait until a worker starts." DSN remains strict `os.environ[KEY]`.

**Stage 2 commit message:** `code(AST-2238): astral_agent enqueue/await client`

## Execution contract

- Stages in order; one commit per stage on the epic worktree; push to `origin/sub/AST-2235/AST-2238-platform-astral-agent-client-enqueue-await` after each.
- Do not add files outside **Files Changed**.
- Do not import `service.*` or edit AST-2237 trees.
- Ambiguity → stop and comment on **AST-2238** (parent only if the question is epic-wide design).

## Estimate

Confirm Chuckles estimate: 3 — agree
