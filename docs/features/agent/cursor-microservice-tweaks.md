# cursor-microservice-tweaks — working plan

- **Branch:** `cursor-microservice-tweaks` (local, from `origin/dev` @ `00b95efc9`; no upstream, not pushed)
- **Owner:** Cursor pairing with Susan — hand-crafted fixes, one step at a time, commit only when Susan says so.
- **Trigger:** staging `prefilter_company-e4c5f915…` (2026-10-17 15:00 UTC) — 11 pass / 1 fail / 28 error out of 40.

## Why

Staging astral-agent runs one replica with `WORKER_CONCURRENCY = 4`. Every queued provider call across every
candidate shares those 4 slots, and astral-core's 900s job deadline counts queue wait. Of the 28 errors:
17 jobs were never claimed, 8 were claimed ~30s before their deadline and cancelled, 2 were real 600s provider
timeouts, 1 was an OpenRouter connection drop. Queue waits grew 0s → 775s across the run.

## Direction (agreed)

- **The service decides when it is full; astral-core does not guess capacity.** No app-side throttles on either side.
- **Option 1 fleet:** the astral-agent worker claims what is queued; Railway scales the replica vertically; replica
  count stays manual (availability, not capacity).
- **Rate limits are learned from provider pushback**, not configured: honor `Retry-After`, no growing (2^n) delays.
- **astral-core claims everything, astral-agent runs the batch.** At the tick astral-core claims every eligible
  entity (avail ≥ `min_count`, sweeps for low traffic) and enqueues all calls at once (one `agent_job` per call,
  shared `batch_id`). astral-agent owns warm → fan-out → learned in-flight limit for that batch.

## Universal methods (astral-agent + Telescope)

Both services are copies of one skeleton (`jobqueue.py` identical but for table names; `worker.py` same
claim / heartbeat / maintenance / drain loops). Where they do the same job, they do it the same way:

- **U1. Holding area + gate (the parking lot).** The worker claims every claimable job (no count cap) into an
  in-memory waiting line; DB leases are heartbeated for everything held, so a crash still re-queues it. A gate
  admits a waiting job when there is room; every finish wakes the gate. Only the gate differs:
  astral-agent = per batch/host, size learned from 429/529 (step 6); Telescope = memory headroom (container
  memory in use vs. its limit, read live from cgroup). Replaces `WORKER_CONCURRENCY` in both.
- **U2. One failure table, retried in the waiting line** (not via DB `run_after` re-delivery; DB `attempts`
  stays for crash re-delivery only):
  - *Pushback* (429/529) → back of line, not counted, shrinks the lot.
  - *Timeout* → back of line, counted; the second timeout is final.
  - *Transient* (connection error, 5xx, `scrape_failed`, Firefox crash) → back of line after a fixed delay,
    counted, up to the job's `max_attempts`.
  - *Permanent* (bad request, click target missing, balance refusal, auth) → fail now.
- **U3. Per-call timeout comes in the request** (`timeout_seconds`), service default when absent.
  astral-agent: from the agent row (step 4). Telescope: default stays `REQUEST_TIMEOUT_SECONDS` 120.
- **U4. Caller waits on a 24h backstop only** (`job_deadline_seconds` in both `ASTRAL_AGENT_CONFIG` and
  `TELESCOPE_CONFIG`), never as a work timer (step 4).
- **U5. Queue failures never become verdicts** in either client's callers (step 1).
- **U6. [approved] One shared copy of the skeleton.** `service/common/` (jobqueue + worker loops +
  gate interface) copied into both images; each service keeps only its executor and its gate. Touches both
  Dockerfiles, both `watchPatterns`, and the import-fence test.

## Telescope todo

- [ ] **T1.** `TELESCOPE_CONFIG["job_deadline_seconds"]` 600 → 24h backstop (U4, with step 4).
- [ ] **T2.** Verdict audit (U5, with step 1): `telescope_timeout` from the caller's wait, cancellation, and
  worker loss hold state instead of `_save_parse_dispatch_failure` (`src/core/roster.py` ~1328); also check
  `fetch_jd`, `gazer`, homepage fetch. A real scrape timeout after its retry stays a real outcome.
- [ ] **T3.** Holding area + memory gate (U1): claim everything; start a Firefox context only while memory use is
  below the cutoff; remove `WORKER_CONCURRENCY = 20` and the 2 GiB `limitOverride`. Verify Railway exposes the
  container limit in cgroup `memory.max` before relying on it. Cutoff is a config setting, default **70%**
  (Susan: 80% also acceptable).
- [ ] **T4.** Retries move into the waiting line (U2): `_retry_delay` 2/4/8s doubling → fixed delay (config
  setting, default **2s**, same value and setting for astral-agent transient retries);
  `TIMEOUT_MAX_ATTEMPTS = 2` keeps its meaning; permanent classes unchanged.
- [ ] **T5.** Optional `timeout_seconds` on the scrape request (U3); default unchanged.
- [ ] **T6.** `telescope_worker.concurrency` (NOT NULL) reports held count instead of a cap; astral-core never
  reads it (checked). `wait_s` / stats split *held* vs. *running*.
- [ ] **T7.** Shared skeleton (U6, approved) — last, after both services behave the same.
- [ ] **T8.** One owner per setting (decision F): drop the `TELESCOPE_CONFIG` mirror note / copies and the
  duplicated cookie selectors (astral-core sends them, or Telescope owns them alone).
- Deferred: websites throttling us (e.g. 152 JDs on one job board). Telescope never reads HTTP status today;
  measure before building a per-site lot.

## Steps (in order)

Each step: one small change, compile + lint + touched tests green before Susan reviews. Status in brackets.

1. **[todo] Queue failures must not become verdicts.** `select_job_page` holds `PJL_READY` for balance refusal,
   probe failure, and `provider_call_timeout`, but `astral_agent_timeout` / `astral_agent_cancelled` /
   `connectivity_failure` fall through to `ERROR_SELECT_JOB_PAGE_NO_JOBLIST`. Audit every `do_task` caller
   (prefilter, grade_*, evaluate_jd, parse_job_list, upshot, …) for the same gap, then fix in one place if the
   callers allow it (`is_provider_state_hold` in `src/utils/llm_external.py` is the likely seam).
2. **[todo] astral-agent: async provider client.** Replace `Anthropic` + `asyncio.to_thread` with `AsyncAnthropic`
   in `service/astral_agent/providers/` (compat, anthropic, OpenRouter probe). Cancelling a job then really aborts
   the HTTP call (no orphaned billed calls, no 429 bursts after cancel waves) and the default thread pool stops
   being a hidden concurrency cap. 429 retry sleeps become `await asyncio.sleep`.
3. **[todo] astral-agent: remove the worker cap (U1).** Drop `WORKER_CONCURRENCY` (claim everything claimable into
   the holding area) and the
   1 GiB `limitOverride` in `service/astral_agent/railway.toml`. Keep the `agent_worker.concurrency` column
   contract sane (it is NOT NULL). Depends on step 2.
4. **[todo] Timeouts live on the call, not the batch.**
   - astral-core's job wait (`job_deadline_seconds` 900 → `expires_at`) becomes a **24h backstop** only — it
     exists so a permanently dead worker can't strand a dispatch thread, not to time work.
   - The real timeout is **per provider call, per agent**: new timeout-window field on the **agent row**
     (heavy-thinking agents get longer). astral-core sends it as `timeout_seconds` on every request (today one
     global `PROVIDER_CALL_BUDGET` 600s, `src/core/agent.py` ~1890); astral-agent already honors it.
   - A timed-out call goes **back into the batch's waiting line once**; a second timeout is the real
     `provider_call_timeout`. Unlike a 429, a timeout does **not** shrink the lot (one stalled car ≠ full lot);
     the async client (step 2) actually aborts it so the slot frees.
   - Touches `src/external/astral_agent.py`, `service/astral_agent/jobqueue.py`, agent schema + admin agent form.
5. **[todo] astral-agent: warm call replaces the probe (every provider, not only OpenRouter).** First job seen for
   a `batch_id` sends one warm call: the batch's real `system` (shared prefix + cache A–D), the same model /
   reasoning / thinking settings, and the **real `max_tokens`**, with the user message replaced by
   "We are warming the cache here, just reply with 1 with no additional thinking so we can send you the whole
   batch." No output cap and no changed reasoning settings — both break host selection (a small `max_tokens` can
   pick a host the real calls can't use) or the cache match (thinking settings render into the prefix).
   Streamed: read the host from `message_start.message.provider` (OpenRouter pin), release the rest of the batch
   at the **first content event** (prompt processed = prefix cached), then hang up. Today's probe strips `system`
   (`openrouter_provider.probe_request_kwargs`), so it warms nothing. Depends on step 2.
   - Verified 2026-10-17 (staging, `gpt-oss-120b`, raw HTTP): OpenRouter `/api/v1/messages` stream sends
     `provider` in `message_start` (host `Venice`, 1.2s). Still to confirm: the Anthropic SDK exposes it on the
     streamed message.
   - **To test in the build:** hanging up after the first content event still leaves a usable cache. Pin one
     host (cache-read-reporting model, e.g. `deepseek/deepseek-v3.2`), shared prefix > 1,024 tokens: warm + hang
     up → follow-up `cache_read_input_tokens`, vs. warm to completion → follow-up. Same reads = hang-up is free.
   - **Confirm on the Task Performance admin screen** (`/admin/task_performance`) after rollout: Cache-read
     tokens / Cache hit % per task should rise to cover the shared prefix on every call after the warm. (The
     warm call itself is astral-agent-side and may not appear there.)
6. **[todo] astral-agent: the parking lot — in-flight limit learned from pushback (per batch).** After the warm
   releases, send every remaining call at once. If K of N come back "lot full", the batch's limit = accepted count
   (e.g. 152 sent, 52 rejected → 100 in flight). Watch the exit: each finished call frees a slot immediately for
   a waiting one (fast finishers refill in seconds; slow calls don't hold the batch). A new "lot full" lowers
   the limit to the then-accepted count; the limit never grows within a batch — each batch learns fresh.
   - "Lot full" = HTTP **429 or 529** (Anthropic overloaded). Today `RATE_LIMIT` in
     `service/astral_agent/providers/errors.py` lists 429 only.
   - **Empty lot** (a whole wave rejected, nothing in flight to wait on): honor `Retry-After`; without it, send
     one call every **30s** (fixed, never growing) until one is accepted, then refill as normal.
   - Replaces the 10/20/40/80/160s doubling loop and `BoundedSemaphore` in `llm_compat_provider._create`, the
     `exhausted_stops_batch` stop, and all of `LLM_SERVER_CONFIG[…]["concurrency"]` (incl. DeepSeek
     `max_concurrent: 20`) — no configured throttles anywhere. Depends on steps 2 and 5.
7. **[todo] astral-core: share queue clients across threads.** One process-wide pool + LISTEN + result poller per
   service (astral-agent, Telescope) instead of one per event loop. Removes per-thread Postgres connections
   (staging `max_connections = 100`) and the missing astral-agent cleanup in `_task_thread_target`.
8. **[todo] astral-core: claim everything at the tick, enqueue at once.** Per-entity tasks claim every eligible
   entity in one run (no `batch_size` run chunking); the AST-1829 sweep stays for 0 < avail < `min_count`.
   Remove core-side warm-first and stagger (`_warm_then_gather` waits for the full warm response, then staggers
   1s per call; chunk 0 runs alone) — astral-agent owns that now. `batch_size` keeps one meaning: rows per prompt
   for `batch_call_mode = 1` rows (staging: only `qualify_job_listings`, 20 per prompt — keep). Mode-0 rows
   (every `grade_*`, `evaluate_jd`, meteorite row on staging) already send one entity per call. Depends on steps
   5 and 6.
9. **[todo] astral-core: remove the AUTO thread cap completely.** `max_auto_threads`, `get/set_auto_thread_cap`,
   tick slot check (`src/core/dispatcher.py`), runtime override API (AST-1916, `src/ui/api/api_admin.py`),
   Scheduled Actions dropdown (AST-1917, `AdminScheduledActions.tsx`), tests + test-bible. Depends on step 7.

## Ops (not code)

- Reset the 25 deadline-errored staging companies from `ERROR_PREFILTER_COMPANY` once steps 2–4 are live.
- After steps 5–6 ship: check cache hit % on `/admin/task_performance` (step 5).

## Deferred / noted

- **Probe host map is per-process** (`openrouter_provider._hosts`, never evicted). Only matters with >1 replica;
  would need a shared (Postgres) map keyed by batch.
- **Probe pin disables OpenRouter fallback** (`provider.only: [host]`) — kept on purpose: one host per batch
  means one quantization (consistent grades), one cache, and real 429s for the parking lot. OpenRouter
  `session_id` sticky routing was considered and dropped (overflow would land on other hosts silently).
- **Dead code:** `await_provider_call_with_budget` in `src/utils/llm_external.py`; `probe_host` / `get_batch_host`
  in `src/external/openrouter.py`; retired `src/external/llm_compat.py` call path.
- **`batch_call_mode = 1` on a `select_job_page` row** processes only `entities[0]` per run (others claimed, then
  released). Guard or document.
- **`fetch_jd` warm-first** sends one scrape alone before the rest; scrapes have no cache to warm.
- **Batch-log timestamps** in the monitor email cluster at flush time, not event time.

## Decisions (Susan, 2026-10-17)

- **A.** No batch timeout on astral-core beyond a 24h backstop. Timeout is per call, window on the agent row;
  timeout → back in line once → then a real timeout (step 4).
- **B.** Parking lot: limit = accepted count, refill on every exit, no growth within a batch; empty lot waits
  `Retry-After` or 30s fixed (step 6).
- **C.** Delete provider throttle config entirely — pushback (429/529) works for every host (step 6).
- **D.** Dropped `session_id`; keep the per-batch host pin.
- **E.** No change: grade tasks are mode 0 (one JD per call); `qualify_job_listings` keeps 20 rows per prompt.
- **Telescope:** memory cutoff and transient retry delay are config settings (70%, 2s); U6 shared skeleton approved.
- **F.** Service settings stay in service files (not Postgres, not Railway env): service-health tunables in each
  service's config file, shared ones in `service/common/` (U6). Per-job values (timeout, max attempts, deadline)
  travel in the request / job row from astral-core. Remove hand-copied mirrors (`TELESCOPE_CONFIG` mirror note
  in `telescope_config.py`, Telescope cookie selectors) — one owner each.

## Verify (every step)

- `python -m compileall -q src service`
- `ruff check` on touched files
- touched component tests (`pytest tests/component/...`)
- frontend steps only: `npm run lint` + `npm run build` in `src/ui/frontend`
