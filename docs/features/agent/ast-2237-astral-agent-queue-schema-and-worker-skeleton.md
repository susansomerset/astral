# AST-2237 — astral-agent queue schema and worker skeleton

- **Linear:** [AST-2237](https://linear.app/astralcareermatch/issue/AST-2237) · parent [AST-2235](https://linear.app/astralcareermatch/issue/AST-2235) (Build astral-agent microservice)
- **Publish ref:** `origin/sub/AST-2235/AST-2237-astral-agent-queue-schema-and-worker-skeleton`
- **Assignee:** Katherine
- **Canon Scope:** `patt.entity.batch-processing` (contrast); `stat.logging.error`; `stat.logging.warning`; `stat.logging.info`; `stat.logging.debug`; `patt.agent.provider-io-via-queue` (pending Archie); `astral.config.secrets-and-env-specific-from-environ`

Stand up `service/astral_agent/` as a Telescope-shaped Postgres queue consumer: `agent_job` DDL, claim/lease/NOTIFY/heartbeat/maintenance, FastAPI `/healthz` + `/wake`, Dockerfile + requirements, and a **stub** executor that writes a terminal result with no live provider HTTP. Does not own the platform client (AST-2238), provider wrappers (AST-2239), `do_task`/Ad Hoc cutover (AST-2240), or Railway/CI fence (AST-2241).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `service/astral_agent/` — **new** — worker package: schema ensure, claim/lease/heartbeat loop, stub executor, result write, `/healthz`, `/wake`, console logging only.
- `service/astral_agent/jobqueue.py` — **new** — Postgres DDL + SQL.
- `service/astral_agent/Dockerfile` — **new**.
- `service/astral_agent/requirements.txt` — **new**.

Every row in **Files Changed** is under those paths. Technical kinds covered: `agent_job` / worker registry / NOTIFY channels; `FOR UPDATE SKIP LOCKED` claim; lease heartbeat + requeue on expiry; stub execute → terminal `done`/`failed`; env `ASTRAL_DATABASE_URL`; console-only logs; Dockerfile + requirements. No `railway.toml`, no `src/**`, no provider HTTP modules, no platform enqueue client, no CI fence scripts (those are siblings).

## Canon notes (planner)

- **`patt.entity.batch-processing` (contrast, read in full):** Entity claim uses `batch_id` lock + audit on product rows; release in `finally`. Astral-agent jobs are **not** entity claims — no `batch_id`, no `entity_id`, no `TASK_CONFIG`, no `do_task` / `run_next` / `dispatch_*`. Leasing is Postgres `lease_until` + `FOR UPDATE SKIP LOCKED` on `agent_job` only (same isolation idea as Telescope's `telescope_job`, not the entity batch pattern).
- **`patt.agent.provider-io-via-queue`:** flagged pending Archie — **not** scoring law this pass. Id-only. This ticket still implements the service half of the queue so siblings can land against a real tree.
- **`astral.config.secrets-and-env-specific-from-environ`:** `ASTRAL_DATABASE_URL` from environ only; no hardcoded DSN. Provider API keys are **not** read in this ticket (stub executor) — AST-2239 adds them.
- **Logging statutes** (`stat.logging.*`): directive paths are `src/**` / `app_log`. Service has **no** SQLite / `app_log` / `save_agent_data`. Apply the **semantic** (error once at handler with facts + traceback; warning for soft fails; succinct info; debug at joints) via **stdlib console logging** — do not import `src.utils.logging`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `service/astral_agent/__init__.py` | Empty package marker | service |
| `service/astral_agent/agent_config.py` | Service-local tunables (concurrency, lease, poll, retention, idle sleep, port, log level defaults) — **no** `src` imports | service |
| `service/astral_agent/settings.py` | Load `ASTRAL_DATABASE_URL` from environ + tunables from `agent_config` | service |
| `service/astral_agent/logging_util.py` | Railway-JSON console handler (mirror Telescope `logging_util.py` shape, own logger names) | service |
| `service/astral_agent/jobqueue.py` | `agent_job` / `agent_worker` DDL + claim/complete/fail/heartbeat/maintain/has_pending/release_all + NOTIFY channels | service |
| `service/astral_agent/executor.py` | Stub executor: assembled `request` jsonb in → result dict out (no HTTP) | service |
| `service/astral_agent/worker.py` | Queue consumer: LISTEN + poll claim loop, heartbeat, maintenance, run stub, write terminal | service |
| `service/astral_agent/app.py` | FastAPI lifespan, Runtime sleep/wake, `GET /healthz`, `GET /wake` | service |
| `service/astral_agent/requirements.txt` | `fastapi`, `uvicorn[standard]`, `asyncpg` only (no Playwright, no provider SDKs) | service |
| `service/astral_agent/Dockerfile` | Slim Python image; copy only this package; single uvicorn worker | service |

**Out of this ticket (do not touch):** `service/astral_agent/railway.toml` / CI fence (AST-2241); `src/external/astral_agent.py` / `src/utils/config.py` (AST-2238); provider wrapper modules / retiring `src/external/{openrouter,anthropic,llm_compat}.py` call surfaces (AST-2239); `src/core/agent.py` cutover (AST-2240); `src/data/database.py`; `tests/` / `docs/test-bible/**` (Betty at qa-child).

## Stage 1: Package skeleton, settings, console logging, jobqueue DDL+SQL

**Done when:** `service/astral_agent/` exists; `jobqueue.SCHEMA_SQL` creates `agent_job` + `agent_worker` with the columns below; `ensure_schema` / `claim` / `complete` / `fail` / `heartbeat` / `maintain` / `has_pending` / `release_all` are importable; settings refuse a missing `ASTRAL_DATABASE_URL` at load. No FastAPI app or worker loop yet.

1. Create `service/astral_agent/__init__.py` (empty).

2. Create `service/astral_agent/agent_config.py` with these module-level constants (integers/floats/strings as shown):

| Name | Value | Role |
|------|-------|------|
| `WORKER_CONCURRENCY` | `4` | Jobs in flight per replica |
| `QUEUE_POLL_SECONDS` | `2.0` | Claim-loop backstop poll |
| `LEASE_SECONDS` | `300` | Running-job lease (provider-ready; stub finishes instantly) |
| `HEARTBEAT_SECONDS` | `30` | Lease + worker registry refresh |
| `MAINTENANCE_SECONDS` | `30` | Reap / expire / prune cadence |
| `JOB_RETENTION_HOURS` | `24` | Delete terminal rows older than this |
| `WORKER_STALE_SECONDS` | `90` | Drop stale `agent_worker` rows |
| `SHUTDOWN_GRACE_SECONDS` | `25` | Drain in-flight on stop |
| `IDLE_SLEEP_SECONDS` | `300` | Drop PG pool when idle (serverless wake) |
| `DB_POOL_MAX_SIZE` | `5` | asyncpg pool max |
| `PORT` | `8080` | Documented bind; Dockerfile CMD uses 8080 |
| `LOG_LEVEL` | `"INFO"` | Default when env unset |

⚠️ **Decision (concurrency 4 / lease 300s):** Stub work is instant, but AST-2239 will run real provider HTTP in this same worker. Prefer provider-shaped defaults now so #3 does not retune the skeleton. Scale out is replicas, not gunicorn workers (same as Telescope).

3. Create `service/astral_agent/settings.py`:
   - Frozen dataclass `Settings` with fields: `database_url`, `worker_concurrency`, `queue_poll_seconds`, `lease_seconds`, `heartbeat_seconds`, `maintenance_seconds`, `job_retention_hours`, `worker_stale_seconds`, `shutdown_grace_seconds`, `idle_sleep_seconds`, `db_pool_max_size`, `port`, `log_level`.
   - `load_settings()`:
     - `database_url = os.environ["ASTRAL_DATABASE_URL"].strip()` — **no** `.get()`, **no** empty-string fallback. Missing key → `KeyError` at import/load (crash loud).
     - Tunables from `agent_config` constants.
     - `idle_sleep_seconds = float(os.environ["ASTRAL_AGENT_IDLE_SLEEP_SECONDS"])` if that env key is set, else `IDLE_SLEEP_SECONDS` from config. (Optional override only for idle; DSN stays required.)
     - `log_level = (os.environ.get("ASTRAL_AGENT_LOG_LEVEL") or LOG_LEVEL).strip() or LOG_LEVEL`.
   - Module-level `settings = load_settings()`.

⚠️ **Decision (DSN vs optional tunables):** Ticket cites `astral.config.secrets-and-env-specific-from-environ` and AC4. `ASTRAL_DATABASE_URL` is the secret/env-specific value — required, no fallback. Idle/log overrides are non-secrets and may use optional env like Telescope's `TELESCOPE_IDLE_SLEEP_SECONDS` / `TELESCOPE_LOG_LEVEL`.

4. Create `service/astral_agent/logging_util.py` by adapting `service/telescope/logging_util.py`:
   - Same Railway JSON-to-stdout handler pattern (`RailwayJsonHandler`, level map, worker label helpers).
   - `_OWN_LOGGERS = frozenset({"app", "worker", "jobqueue", "executor"})`.
   - `configure_logging()` / `get_logger(name)` / `set_worker_label` / `worker_label`.
   - No `joblog` debug-job filter complexity required for stub — keep `_LevelOrJobDebug` with `_job_debug` always `False` unless a later sibling adds job-context hooks. Level filter alone is enough.
   - Do **not** import anything from `src/` or `service/telescope/`.

5. Create `service/astral_agent/jobqueue.py` as a **structural copy** of `service/telescope/jobqueue.py` with these renames and constants:

| Telescope | astral-agent |
|-----------|--------------|
| `JOB_TABLE = "telescope_job"` | `JOB_TABLE = "agent_job"` |
| `WORKER_TABLE = "telescope_worker"` | `WORKER_TABLE = "agent_worker"` |
| `CHANNEL_NEW = "telescope_job_new"` | `CHANNEL_NEW = "agent_job_new"` |
| `CHANNEL_DONE = "telescope_job_done"` | `CHANNEL_DONE = "agent_job_done"` |
| `_SCHEMA_LOCK_KEY = 0x7E1E5C09E` | `_SCHEMA_LOCK_KEY = 0xA6E47A6E` (distinct advisory lock) |

   Keep the same column set and CHECKs as Telescope's `SCHEMA_SQL` (uuid id, status queued|running|done|failed|cancelled, priority, request jsonb, result bytea, error, error_class, attempts, max_attempts, run_after, expires_at, lease_until, worker_id, created_at, started_at, finished_at) plus the same three indexes and `agent_worker` registry table.

   Port these functions **verbatim in behavior** (only table/channel/lock names change): `encode_result`, `decode_result`, `create_pool`, `ensure_schema`, `claim`, `complete`, `fail`, `heartbeat`, `maintain`, `has_pending`, `release_all`, and the `ClaimedJob` dataclass.

   Module docstring must state: contract mirror for future `src/external/astral_agent.py` (AST-2238) — same table/column/channel names; import fence forbids sharing code; change both sides together when #2 lands. **Do not** add an insert/enqueue helper in this ticket (platform client owns insert; Betty may INSERT via SQL in component tests).

⚠️ **Decision (mirror Telescope SQL, not invent):** Parent Technical scope says mirror `telescope_job` shape. Copying the proven claim/lease/NOTIFY SQL avoids a second queue dialect for Ada's client to rediscover.

**Stage 1 commit message:** `code(AST-2237): agent jobqueue schema and settings`

## Stage 2: Stub executor + queue worker loops

**Done when:** A `QueueWorker` can claim a queued `agent_job`, run the stub executor, and write terminal `done` with zlib-compressed JSON result (or `failed` on stub crash); heartbeat and maintenance loops run; a second claim with a different `worker_id` cannot take a row already `running` with a live lease. No HTTP app yet (worker is constructible with a pool for harness use).

1. Create `service/astral_agent/executor.py`:
   - `async def execute(request: dict) -> dict`:
     - If `request` is not a dict → raise `ValueError("request must be a dict")`.
     - Return exactly:
       ```python
       {
           "stub": True,
           "echo": request,
           "usage": {"input_tokens": 0, "output_tokens": 0},
       }
       ```
     - No `httpx` / SDK / network. No reads of provider env keys.
   - Module docstring: replaced by AST-2239 provider wrappers; keep this signature (`request` dict → result dict) so `worker.py` stays stable.

⚠️ **Decision (stub returns `done` with echo, not auto-`failed`):** AC2 needs a terminal write path. Echoing the request proves claim→execute→complete without inventing provider error_class mapping (that is #3). A deliberate failure path is still exercised if `execute` raises — worker maps that to `fail(..., error_class="stub_error", retry_in_seconds=None)`.

2. Create `service/astral_agent/worker.py` adapting `service/telescope/worker.py`:
   - `make_worker_id()` — same shape (`RAILWAY_REPLICA_ID` or hostname + pid + short uuid).
   - `QueueWorker.__init__(self, db, *, worker_id=None, concurrency=None)` — **no** Firefox/browser dependency.
   - `start` / `stop` / `_connect_listener` (LISTEN `agent_job_new`) / `_claim_loop` / `_heartbeat_loop` / `_maintenance_loop` / `_job_done` — same control flow as Telescope.
   - `_run_job(self, job)`:
     1. Call `await executor.execute(job.request if isinstance(job.request, dict) else {})`.
     2. On success → `jobqueue.complete(..., result=result)`.
     3. On `CancelledError` → re-raise.
     4. On any other exception → log once with `logger.exception` (facts: job id, exc type/message), then `jobqueue.fail(..., error=str(exc)[:2000], error_class="stub_error", retry_in_seconds=None)` (terminal; stub does not retry).
   - Wrap DB writes like Telescope (`_db_write` helper with short retry) so a Postgres blip does not kill the process.
   - Log lines use label prefix; **info** for start/stop/stats; **warning** for claim/heartbeat/listener soft fails; **exception** only on unhandled job crash path above.
   - Ban strings in this package (enforced by AC greps later): do not reference `do_task`, `run_next`, `entity_id`, `TASK_CONFIG`, `dispatch_`, `app_log`, `save_agent_data`, `add_log_entry`, or `astral.db`.

**Stage 2 commit message:** `code(AST-2237): stub executor and queue worker`

## Stage 3: FastAPI app (`/healthz`, `/wake`) + Dockerfile + requirements

**Done when:** `test -d service/astral_agent && test -f service/astral_agent/Dockerfile && test -f service/astral_agent/jobqueue.py` exits 0; `uvicorn app:app` starts when `ASTRAL_DATABASE_URL` is set; `GET /healthz` reports ok/asleep/unhealthy; `GET /wake` resumes a sleeping runtime; image build context copies only `service/astral_agent/`; `rg` bans in AC3/AC5 would be clean on this tree.

1. Create `service/astral_agent/app.py` adapting `service/telescope/app.py` **without** Firefox:
   - `Runtime` holds `db` pool + `QueueWorker` only; `asleep` flag; same wake/sleep race guard using `jobqueue.has_pending`.
   - Lifespan: require `settings.database_url` (already loaded); `runtime.start()`; yield; `runtime.close()`.
   - `GET /wake` → `runtime.wake()`; on exception log exception once, return 503 `{"status": "wake_failed"}`; else `{"status": "awake", "woke": <bool>}`.
   - `GET /healthz`:
     - If asleep → `{"status": "asleep"}` with 200.
     - Else compute `loop_ok` from `worker.last_loop_at` vs `max(30.0, settings.queue_poll_seconds * 10)`; body includes `status`, `worker_id`, `in_flight`, `db_ok`, `claim_loop_age_s`. No `browser_ok` key.
     - Unhealthy → 503 + warning log with body.
   - **No** candidate/Stytch/bearer auth on these routes (AC4 fail condition is adding that auth — private networking owns exposure; match current Telescope wake/health openness).
   - Call `configure_logging()` at module import and again at lifespan start (same as Telescope).

2. Create `service/astral_agent/requirements.txt`:
   ```
   fastapi>=0.115.0,<1
   uvicorn[standard]>=0.30.0,<1
   asyncpg>=0.30.0,<1
   ```
   No Playwright, no Anthropic/OpenAI/httpx pins (those land with AST-2239).

3. Create `service/astral_agent/Dockerfile`:
   ```dockerfile
   # syntax=docker/dockerfile:1
   FROM python:3.12-slim-bookworm
   ENV PYTHONUNBUFFERED=1
   WORKDIR /app
   COPY service/astral_agent/requirements.txt /app/requirements.txt
   RUN pip install --no-cache-dir -r /app/requirements.txt
   COPY service/astral_agent/ /app/
   EXPOSE 8080
   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
   ```
   Comments: build from monorepo root (COPY paths are root-relative); single worker; scale with replicas; do **not** copy `src/`.

4. Sanity greps the builder must run before declaring the stage done (stop + comment if any hit):
   - `rg -n "from src\\.|import src|do_task|run_next|entity_id|TASK_CONFIG|dispatch_" service/astral_agent/` → no matches.
   - `rg -n "app_log|astral\\.db|save_agent_data|add_log_entry" service/astral_agent/` → no matches.
   - `test -f service/astral_agent/Dockerfile && test -f service/astral_agent/jobqueue.py`.

**Stage 3 commit message:** `code(AST-2237): astral-agent app health wake dockerfile`

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each with `git push origin HEAD:sub/AST-2235/AST-2237-astral-agent-queue-schema-and-worker-skeleton`.
- Do not add files outside **Files Changed**. Do not implement provider HTTP, platform client, railway.toml, or CI fence.
- Ambiguity / drift → stop and comment on **parent** AST-2235 with the Stage-blocked template from plan-child.

## Estimate

Confirm Chuckles estimate: 5 — agree
