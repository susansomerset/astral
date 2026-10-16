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

⚠️ **Decision — DSN stricter than live Telescope client:** `telescope.py` uses `.get` then an empty check. This client uses `os.environ[KEY]` (no `.get`) on purpose, matching `astral.config.secrets-and-env-specific-from-environ`. Do not loosen it to match Telescope.

**Stage 2 commit message:** `code(AST-2238): astral_agent enqueue/await client`

## Execution contract

- Stages in order; one commit per stage on the epic worktree; push to `origin/sub/AST-2235/AST-2238-platform-astral-agent-client-enqueue-await` after each.
- Do not add files outside **Files Changed**.
- Do not import `service.*` or edit AST-2237 trees.
- Ambiguity → stop and comment on **AST-2238** (parent only if the question is epic-wide design).

## Traceability

| AC | Check | Satisfied by |
|----|--------|----------------|
| 1 | `ASTRAL_AGENT_CONFIG` keys; no DSN/secret literals | Stage 1 |
| 2 | Enqueue/await surface + dedicated error on failure/cancel/connectivity | Stage 2 (`submit`, `AstralAgentError`) |
| 3 | `ASTRAL_DATABASE_URL` via required `os.environ[...]`; missing/blank fails before insert | Stage 2 `_dsn()` |
| 4 | No `service.*` import; constants duplicated locally | Stage 2 imports + Execution contract |
| 5 | `_JOB_TABLE` / channels / terminal statuses match AST-2237 | Contract mirror table |
| 6 | Platform slice of parent AC 9: env-only DSN, no hardcoded secrets | Stage 1 + Stage 2 `_dsn()`. Service provider keys and Stytch on wake/health → **N/A** (AST-2237 / AST-2239) |

Parent AC **1–2, 4–8, 10–12** → **N/A** (service tree, fence, cutover, local reads, `database.py`, daisy-chain, console logs, Ad Hoc — other children). Parent AC **3** (claim/lease lifecycle) → **N/A** here; this ticket only inserts and awaits. No orphan stages.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Revisions

### Revision 1 — 2026-10-16

Driven by: Joan `[plan-discuss] round=1 concern` / fix-now R5 — Linear child ACs are now the six platform-client checks; plan had no AC map.

Changes: Added **## Traceability** keyed to child AC 1–6 (AC 6 service half and parent AC 1–8, 10–12 marked N/A). Noted intentional DSN divergence from Telescope `.get`.

## Joan validate

[plan-discuss] round=1 concern  
[plan-rubric]  
**Ticket:** AST-2238  
**Overall:** REVISE  
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066  
**Publish ref:** `494eb53d79301eef5cb5b454922cb12b406f2b4d` (`origin/sub/AST-2235/AST-2238-platform-astral-agent-client-enqueue-await`)

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.layers.core-vs-external-bright-line | A | | |
| astral.config.secrets-and-env-specific-from-environ | A | | |
| stat.logging.error | A | | |
| stat.logging.warning | A | | |
| stat.logging.info | A | | |
| stat.logging.debug | A | | |
| patt.agent.provider-io-via-queue | X | | pending Archie / not in `canon_clerk` active corpus; plan id-only |

(Worst grade **A** on roll-up ids. `astral.config.*` resolved from `canon/statutes/astral/config/` at corpus tip.)

### Traceability

Linear child lists **only AC 9** (parent/service wording: service env secrets + no Stytch on wake/health). Plan has **no** `## Traceability` / AC mapping. Intended child outcomes (enqueue/await client, `ASTRAL_AGENT_CONFIG`, contract mirror, strict platform DSN) live in Purpose/Stages only — **not** keyed to ticket AC checkboxes. Parent epic AC **3** (job lifecycle) / **6** (cutover) / **9** (service secrets) are not partitioned in the ticket body; platform slice of **9** (DSN via env) → **S1–S2** if amended; service halves → **N/A** (AST-2237/2239). **R5 fail** until plan maps child-appropriate ACs or documents explicit N/A quotes.

### Findings

**fix-now** — **R5 / ticket AC hygiene.** Child **Acceptance criteria** is a single pasted parent AC 9 (service provider keys + wake/health auth). That does not describe this child’s deliverables and cannot be traced stage-by-stage without fiction. **Recommendation:** Chuckles amend Linear child ACs to platform-client checks (config block, `submit`/`AstralAgentError` surface, strict `ASTRAL_DATABASE_URL`, no `service.*` import, contract constants); plan adds a one-line **## Traceability** table keyed to those numbers (and explicit N/A for any service-only parent bullets).

**discuss** — **DSN strictness vs Telescope.** Plan requires `os.environ[KEY]` for DSN; live `telescope.py` uses `.get` then empty check. Astral-agent plan is **stricter** and aligns with `astral.config.secrets-and-env-specific-from-environ` — no plan change required; optional note in plan that this is intentional divergence from Telescope client.

**acceptable** — Assignee Ada (not Joan) at fetch; stdout handoff only.

**acceptable** — Telescope-shaped structural copy, AST-2237 contract mirror without `service` imports, scope gate (two files only), `require_controlled_external_io`, wake optional via documented Decision.

### R6 (summary)

Definition fidelity: matches AST-2235 child #2 scope and boundaries; no `agent.py`/provider/cutover creep. DRY: explicit mirror of telescope queue half. Self-assessment: Estimate confirm only; stage **Done when** and Decision callouts are specific. Canon list has no **D**/**F**.

context_tokens≈48000

## Joan validate

[plan-rubric]
**Ticket:** AST-2238
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `00930a45f6ac5900e35580fcecafa420cd2e2779` (`origin/sub/AST-2235/AST-2238-platform-astral-agent-client-enqueue-await`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.layers.core-vs-external-bright-line | A | | |
| astral.config.secrets-and-env-specific-from-environ | A | | |
| stat.logging.error | A | | |
| stat.logging.warning | A | | |
| stat.logging.info | A | | |
| stat.logging.debug | A | | |
| patt.agent.provider-io-via-queue | X | | pending Archie / not in `canon_clerk` active corpus; plan id-only |

(Worst grade **A** on roll-up ids.)

## Traceability

Child AC **1→S1**; **2→S2** (`submit`, `AstralAgentError`, `close_loop_resources`, `run_one_shot`); **3→S2** `_dsn()`; **4→S2** + execution contract; **5→contract mirror** + S2 SQL/notify; **6→S1+S2** (platform DSN; service keys/Stytch **N/A** per table). Parent AC outliers marked N/A in plan **## Traceability**; no orphan stages. Round-1 R5 gap closed (Linear AC 1–6 + plan table @ `00930a45`).

## Findings

**acceptable** — Plan Discuss **round=1** concern/reply complete; revision note documents traceability add.

**acceptable** — DSN stricter than Telescope documented as intentional Decision.

## R6 (summary)

Matches AST-2235 child #2 scope; two-file gate; Telescope queue-half mirror; no cutover/provider/service edits. Self-assessment and stage **Done when** clauses are specific. No **D**/**F**; no `fix-now` / blocking `discuss`.

context_tokens≈56000

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-2235/AST-2238-platform-astral-agent-client-enqueue-await`
**Product commits:** `04ae0ce79` (Stage 1 — `ASTRAL_AGENT_CONFIG`), `39e000a14` (Stage 2 — enqueue/await client)

**Implemented:**
- `src/utils/config.py` — `ASTRAL_AGENT_CONFIG` after `TELESCOPE_CONFIG` (deadline 900, stale 90, wake timeout 30). Env key name only; no DSN literal.
- `src/external/astral_agent.py` — `_AstralAgentQueue` (insert `agent_job`, LISTEN `agent_job_done`, poll, throttled `/wake`), public `submit` / `close_loop_resources` / `run_one_shot`, `AstralAgentError`. DSN via `os.environ[ASTRAL_DATABASE_URL]`. No `service.*` or `src.core` imports.

**Canon (self-check):** External owns queue I/O (`astral.layers.core-vs-external-bright-line`). Secrets stay in environ (`astral.config.secrets-and-env-specific-from-environ`); wake base URL `.get` is the documented optional exception. Soft fails use `warning`/`debug`; terminal `done` is one `info` line without the request body. `patt.agent.provider-io-via-queue` still pending — id-only.

**Tests:** Betty at Code Complete (`qa-child`). No test-tree edits in this build.

## Radia review

[code-rubric]
**Ticket:** AST-2238
**Publish ref:** `c4a8b3f8119f907efdd37a7b6554f867b8b76bb5` (`origin/sub/AST-2235/AST-2238-platform-astral-agent-client-enqueue-await`)
**Corpus:** `b7ab2203048ce0beb2869a12200ab7fa696c8066`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.layers.core-vs-external-bright-line | A | | |
| astral.config.secrets-and-env-specific-from-environ | A | | |
| stat.logging.error | A | | |
| stat.logging.warning | A | | |
| stat.logging.info | A | | |
| stat.logging.debug | A | | |
| patt.agent.provider-io-via-queue | X | | pending Archie / skeleton queue client only; id-only per plan |

(Worst grade **A** on roll-up ids. `astral.layers.core-vs-external-bright-line` and `astral.config.*` from `canon/statutes/astral/` at corpus tip; logging ids via `canon_clerk expand`.)

## Column diff vs plan stage

(aligned) — Joan post-revision column is all **A** / **X**; code review matches.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **sibling product + test carry on `origin/dev...` three-dot diff:** full **AST-2237** `service/astral_agent/**`, **AST-2237** issue doc, service component harness, and `docs/features/agent/ast-2239-*.md` ride this publish ref after **ftr** sync — expected epic stacking; **AST-2238 product commits** `04ae0ce79` + `39e000a14` touch only `src/utils/config.py` and `src/external/astral_agent.py`.
- **Dependency:** spawn `Relations: blockedBy AST-2237 (User Testing)`; branch carries merged **2237** worker tree so client contract tests can run against real table names — not **2238** scope creep in product commits.
- **DSN strictness vs Telescope client:** `_dsn()` uses `os.environ[KEY]` + empty-strip fail; Telescope still uses `.get` — intentional per plan Decision; aligns with `astral.config.secrets-and-env-specific-from-environ` on this module.

## What's solid

- **`ASTRAL_AGENT_CONFIG`** matches plan: `database_url_env` only (no DSN literal), deadline **900**, `worker_stale_seconds` **90**, wake throttle/timeout, optional `base_url_envs`; `TELESCOPE_CONFIG` untouched.
- **`src/external/astral_agent.py`:** contract constants match **AST-2237** (`agent_job`, channels, terminal statuses); insert + `pg_notify`, LISTEN/poll await, throttled multi-replica `/wake`, `AstralAgentError` vocabulary, public `submit` / `close_loop_resources` / `run_one_shot`; `require_controlled_external_io("astral_agent.submit")`; no `service.*` / `src.core` imports.
- **Logging:** `get_logger(__name__)` throughout; succinct `info` on terminal `done` (provider/model/task_key only, not full request); `warning` for listener/poll/cancel/deadline/wake-skipped; `debug` at enqueue/wake joints (Telescope-shaped, including wake `resp.text[:200]` mirror).
- **Plan fidelity:** two-file scope gate; no `agent.py` cutover, no provider wrappers, no `database.py`; estimate **3** fits; Linear AC **1–6** traceable to stages (Joan round-1 gap closed in plan @ `00930a45`).

## Recommended actions (downstream only — not executed in this session)

- Chuckles: append artifact, `docs(AST-2238): Radia review — clean`, push publish ref, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED** toward **User Testing**.

context_tokens≈24000
