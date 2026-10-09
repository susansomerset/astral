# AST-1963 — Query LLM Platform for Timesheet Data to Finish Batch

<!-- linear-archive: AST-1963 archived 2026-10-08 -->

## Linear archive (AST-1963)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1963/query-llm-platform-for-timesheet-data-to-finish-batch  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Today every `agent_timesheets` row is priced locally: token counts × the catalog price for the SKU (`calculate_cost_components_from_counts`). On OpenRouter that number is a guess. OpenRouter routes each batch to whatever host the probe lands on (AST-1959), hosts charge different prices, and cache discounts vary by host, so the catalog price is only right when the batch happens to land on the catalog's provider. When the local cost can't be computed, no row is written at all and the batch looks cheaper than it was (known bug, rolled in here). OpenRouter keeps the billed cost of each call, keyed by the generation id we already store as `agent_req_id`. Susan wants each call's **platform-billed cost, native token counts and serving host** pulled from the platform and used for the timesheet and the batch's ledger cost, so execution history shows true batch totals and per-item cost can be derived from them. The lookup runs **asynchronously**: it never delays an LLM call or a batch closing, and the ledger picks up the cost whenever it lands.

**Decisions (Susan, 2026-10-04):**

* **Platform cost wins** whenever it is available; the calculated (catalog) cost is the fallback only.
* **Store native token counts and serving host** on the row too.
* **Retry** a not-ready lookup a config-driven number of times (default **5**) rather than falling back at once, with **exponential backoff** between tries; no later sweep is required. Base wait is config-driven; Chuckles' proposed default is **2 seconds, doubling** (2, 4, 8, 16 s between the five tries), the same base the DeepSeek concurrency backoff already uses (`backoff_base_seconds: 2.0`). No cap — the retry count bounds it. Edit the default here if you want a different one.
* **Direct servers are tabled.** Anthropic, DeepSeek and Kimi keep today's calculated cost exactly as it works now. No daily-delta, pricing-refresh or other infrastructure for them in this ticket; they can be trued up later.
* **Decoupled from batch close.** Nothing waits on cost data; the ledger is updated when the cost arrives.
* **A model attribute decides eligibility.** Each model carries a routing type (`direct` / `openrouter`); that model setting is the single source of truth for "this call went through OpenRouter".
* **Unpriced rows get written** (with platform cost filled in where the platform has it).
* **Platform lookup wherever it actually exists.** Research below: today that is OpenRouter only.

**Platform research (2026-10-04):**

* **OpenRouter** — per-call lookup: `GET https://openrouter.ai/api/v1/generation?id=<gen-id>` with the same bearer key. Returns `total_cost` (USD), `native_tokens_prompt` / `_completion` / `_cached` / `_reasoning`, `provider_name` (serving host), `cache_discount`. Stats can lag the response by a few seconds. ([docs](<https://openrouter.ai/docs/api/api-reference/generations/get-request-&-usage-metadata-for-a-generation>))
* **Anthropic** — no per-call cost. The Admin API (`/v1/organizations/cost_report`, daily buckets only; `/v1/organizations/usage_report/messages`, token counts by model in 1m/1h/1d buckets) needs an organization **admin** key, not the candidate's key, and covers the whole org. ([docs](<https://platform.claude.com/docs/en/manage-claude/usage-cost-api>)) Catalog pricing for Anthropic is published and stable.
* **DeepSeek** — no per-call or usage endpoint for API keys; only `GET /user/balance`. Usage/cost endpoints exist only behind the web console's session login. ([docs](<https://api-docs.deepseek.com/api/get-user-balance>)) Side finding (tabled by Susan, no ticket): DeepSeek now bills **peak / off-peak** prices (peak = 2×), and our catalog rows (snapshot 2026-06-03) don't match the current published price.
* **Kimi (Moonshot)** — no per-call or usage endpoint; only `GET /v1/users/me/balance`. ([docs](<https://platform.kimi.ai/docs/api/balance>))

So this epic reconciles `openrouter`**-routed models only**. Direct models keep catalog cost.

## Functional scope

1. **Models carry a routing type.** Every model in the catalog is `direct` or `openrouter`. That attribute alone decides whether a call is reconciled from the platform, and it replaces the existing hard-coded "server is openrouter" check when building the agent's provider object.
2. **Every call gets a timesheet row.** When the local cost can't be computed, the row is still written (whatever token counts the response has, calculated cost 0) instead of being skipped.
3. **Look up one call's billed cost.** Given a generation id and the key that made the call, fetch the platform's billed total cost, native token counts and serving host. A failed or not-ready lookup returns an error, never a guess.
4. **Reconcile each call in the background.** When a timesheet row is written for an `openrouter`-routed model, a background lookup is started for that row. It never delays the call, the batch, or the batch closing, and it survives the batch finishing. A not-ready or failed lookup is retried up to the configured count (default 5) with exponential backoff between tries (configured base wait, doubling each try). On success the row gets the platform cost, native token counts, serving host and reconcile time. After the last failed try the row stays on its calculated cost and one warning names the row and why.
5. **Calculated cost is kept.** Reconciliation never changes a row's `calc_cost_*` or its existing token columns; platform values go in their own columns.
6. **Platform cost wins in every total.** Wherever a batch's cost is summed, a row with a platform cost counts that value, otherwise its calculated cost. When a row is reconciled after its batch's ledger row has closed, that ledger row's `total_cost` and `entity_cost` are recomputed, so execution history reflects the platform cost once it lands.

## Component scope

* `src/utils/config.py` — **modified**. Routing type on every model; `resolve_agent_settings` reads it; a helper to get a timesheet row's routing; reconcile retry count and wait constants.
* `src/external/openrouter.py` — **modified**. Fetch one call's generation stats by generation id and key.
* `src/external/llm_compat.py` — **modified**. A row whose local cost can't be computed is still recorded instead of skipped.
* `src/data/database.py` — **modified**. Platform columns on `agent_timesheets`, a writer for them, `_add_timesheet_entry` accepts an unpriced SKU, `sum_cost_by_batch` prefers platform cost.
* `src/core/timesheets.py` — **modified**. `record_timesheet_entry` starts the background reconcile for `openrouter`-routed rows; the reconcile (key lookup, retries, row write, ledger refresh) lives here.
* Tests and bibles (Betty in `qa-child`), all **modified**:
  * `tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md`
  * `tests/component/external/test_openrouter.py`, `docs/test-bible/external/openrouter.md`
  * `tests/component/external/test_llm_compat.py`, `docs/test-bible/external/llm_compat.md`
  * `tests/component/data/database/test_timesheets.py`, `docs/test-bible/data/database/timesheets.md`
  * `tests/component/core/test_timesheets.py`, `docs/test-bible/core/timesheets.md`

## Technical scope

* `src/utils/config.py`:
  * **New model field** — a routing type on every `LLM_MODEL_CONFIG` entry, `openrouter` for entries built by `_build_openrouter_models`, `direct` for every hand-written entry; allowed values in one config tuple.
  * **Modified validator** `validate_llm_provider_environment` — rejects a model whose routing type is missing or not an allowed value.
  * **Modified function** `resolve_agent_settings` — builds the OpenRouter provider object when the model's routing type is `openrouter`, instead of comparing `server` to the string `"openrouter"`.
  * **New helper** — routing type for a (server id, SKU) pair, the two values a timesheet row carries; raises on unknown.
  * **New constants** — reconcile retry count (default 5) and the backoff base wait (default 2 seconds, doubled after each try).
* `src/external/openrouter.py`: **new function** — takes a generation id and an API key, calls OpenRouter's generation-stats endpoint, returns billed total cost, native prompt / completion / cached / reasoning token counts and serving host, or an error result when the call fails or the record isn't ready. No database or candidate access; the caller passes the key.
* `src/external/llm_compat.py`: **modified function** `send_to_llm_compat` (its timesheet-kwargs helper) — when catalog pricing or token counting raises, returns row values with the available token counts and zero calculated cost instead of no row.
* `src/data/database.py`:
  * **New columns** on `agent_timesheets` — platform cost (nullable; null = not reconciled), native prompt / completion / cached / reasoning token counts, serving host, reconcile timestamp. Added by `_ensure_timesheets_schema` for existing databases and by `_create_agent_timesheets_table` for new ones.
  * **New writer** — sets one row's platform columns by `agent_req_id`.
  * **Modified function** `_add_timesheet_entry` — no longer refuses a SKU the catalog doesn't price (the server id check stays).
  * **Modified function** `sum_cost_by_batch` — per row, platform cost when present, else the sum of `calc_cost_*`.
* `src/core/timesheets.py`:
  * **Modified function** `record_timesheet_entry` — after the row is written, when the row's routing type (config helper, from its server id and SKU) is `openrouter` and it has a generation id, starts the background reconcile and returns at once.
  * **New function (background reconcile)** — resolves the key for the row's server from the row's candidate (same source as `agent._candidate_server_key`; no key → warn and stop), calls the OpenRouter lookup up to the configured count with exponential backoff (configured base wait, doubling each try), writes the platform columns on success, then, if the row's batch has a `dispatch_ledger` row with `completed_at` set, recomputes that row's `total_cost` (`sum_cost_by_batch`) and `entity_cost` (total ÷ `total_processed`, same rule as the dispatcher) via `update_dispatch_ledger`. Runs off the caller's event loop so it outlives the batch's loop and never blocks a call. The ledger refresh recomputes from the table every time, so it is safe to run more than once and safe against the batch-close write.

## Architectural definition

* **Patterns to reuse:**
  * [`patt.entity.batch-processing`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>) — `batch_id` is the join key from a timesheet row to its `dispatch_ledger` row; the ledger refresh finds the ledger row by that id and nothing else.
* **New patterns proposed:** `none`.
* **Applicable statutes:**
  * [`stat.logging.warning`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>) — one warning per row whose reconcile gave up (no key, or every try failed): which row, which batch, why.
  * [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — an exception in the background reconcile is logged once at its handler with traceback and never propagates to the call or the batch.
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — request and response of each generation-stats call, and each retry, logged at debug.

## Acceptance criteria

"Stubbed lookup" = the component-test stub of the OpenRouter generation-stats HTTP call.

1. **Routing type is the source of truth.**
   * **Check (**`test_config.py`**):** every `LLM_MODEL_CONFIG` entry built from `OPENROUTER_MODEL_TABLE` has routing `openrouter`; `kimi-k2.6`, every `claude-*` and both `deepseek-*` entries have `direct`; a model with a missing or unknown routing makes `validate_llm_provider_environment` raise.
   * **Check:** `rg -n '"openrouter"' src/external/ src/core/timesheets.py src/data/database.py` returns nothing, and `rg -n 'server"\] == "openrouter"' src/utils/config.py` returns nothing.
   * **Fails if:** any value differs, the validator accepts a bad value, or either grep hits.
2. **Lookup returns billed numbers or an error.**
   * **Check (**`test_openrouter.py`**, stubbed lookup):** a stubbed 200 with `total_cost: 0.0123`, `native_tokens_cached: 400`, `provider_name: "DeepInfra"` returns those values; a stubbed 404 and a stubbed timeout each return an error result and raise nothing.
   * **Fails if:** a value differs from the stub, or a failure raises or returns a cost.
3. **Unpriced calls still get a row.**
   * **Check (**`test_llm_compat.py`**):** with catalog pricing stubbed to raise, a successful call invokes `record_timesheet` once, with `calc_cost_*` all 0 and the response's token counts. (`test_timesheets.py`, database): `_add_timesheet_entry` with a SKU the catalog doesn't price returns `True` and the row exists.
   * **Fails if:** `record_timesheet` isn't called, or the insert is refused.
4. **Recording never waits on the platform.**
   * **Check (**`core/test_timesheets.py`**):** with the stubbed lookup blocked, `record_timesheet_entry` for an `openrouter`-routed row returns before the lookup completes and the row exists with null platform cost. For a `direct`-routed row, the stub is never called.
   * **Fails if:** it blocks, or a direct row is looked up.
5. **Retry then give up.**
   * **Check (same file, sleep stubbed and recorded):** stub returns not-ready 4 times then 200 → exactly 5 calls and the row's platform columns are set. Stub fails every time → exactly 5 calls (the configured count), platform cost stays null, `calc_cost_*` unchanged, one WARNING naming the row's `agent_req_id` and batch id. With base wait 2, the recorded waits between tries are `[2, 4, 8, 16]`.
   * **Check (**`test_config.py`**):** retry count constant is `5` and backoff base constant is `2`.
   * **Fails if:** call count ≠ 5 in either case, the row is wrong, warnings ≠ 1, or the waits are not doubling from the base (e.g. a fixed interval).
6. **Calculated cost is never overwritten.**
   * **Check (database test):** after the platform writer runs, the row's four `calc_cost_*` and existing token columns equal what was inserted, and the platform cost, native counts, host and timestamp equal what was written.
   * **Fails if:** any original column changed or a platform column is null.
7. **Platform cost wins in the total.**
   * **Check (database test):** a batch with two rows, one reconciled (calc 0.01, platform 0.03) and one not (calc 0.02): `sum_cost_by_batch([batch])` returns `0.05`.
   * **Fails if:** it returns 0.03 (calc only) or anything other than 0.05.
8. **Late cost refreshes a closed ledger row.**
   * **Check (**`core/test_timesheets.py`**):** a `dispatch_ledger` row with `completed_at` set, `total_processed = 2`, `total_cost = 0.02`; reconciling its one row to platform 0.06 leaves `total_cost = 0.06` and `entity_cost = 0.03`. Same with `completed_at` null → ledger row unchanged.
   * **Fails if:** the closed row isn't refreshed, the open row is touched, or `entity_cost` ≠ total ÷ processed.

## Open questions

none

## Proposed child tickets

#### 1!: **Model routing type and OpenRouter generation-stats lookup - Hedy**

Adds the `direct` / `openrouter` routing type to every model (and switches the provider-object check to it), the retry constants, and the external function that fetches one call's billed cost, native tokens and host. Does **not** touch the database, `llm_compat` or `core/timesheets.py` (#2, #3). Hedy built `openrouter.py` in AST-1959.

**Citations:** `stat.logging.debug`.

**Scope:**

* `src/utils/config.py` — **modified**. Routing type on every model; `resolve_agent_settings` reads it; a helper to get a timesheet row's routing; reconcile retry count and wait constants.
  * **New model field** — a routing type on every `LLM_MODEL_CONFIG` entry, `openrouter` for entries built by `_build_openrouter_models`, `direct` for every hand-written entry; allowed values in one config tuple.
  * **Modified validator** `validate_llm_provider_environment` — rejects a model whose routing type is missing or not an allowed value.
  * **Modified function** `resolve_agent_settings` — builds the OpenRouter provider object when the model's routing type is `openrouter`, instead of comparing `server` to the string `"openrouter"`.
  * **New helper** — routing type for a (server id, SKU) pair, the two values a timesheet row carries; raises on unknown.
  * **New constants** — reconcile retry count (default 5) and the backoff base wait (default 2 seconds, doubled after each try).
* `src/external/openrouter.py` — **modified**. Fetch one call's generation stats by generation id and key.
  * **New function** — takes a generation id and an API key, calls OpenRouter's generation-stats endpoint, returns billed total cost, native prompt / completion / cached / reasoning token counts and serving host, or an error result when the call fails or the record isn't ready. No database or candidate access; the caller passes the key.
* `tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md`, `tests/component/external/test_openrouter.py`, `docs/test-bible/external/openrouter.md` — **modified**.

Estimate: 3

#### 2!: **Platform columns and platform-first totals on the timesheet - Katherine**

Adds the platform columns to `agent_timesheets` and their writer, lets unpriced SKUs be recorded, and makes `sum_cost_by_batch` prefer platform cost. Does **not** call OpenRouter (#1) or start reconciles (#3).

**Citations:** `patt.entity.batch-processing`.

**Scope:**

* `src/data/database.py` — **modified**. Platform columns on `agent_timesheets`, a writer for them, `_add_timesheet_entry` accepts an unpriced SKU, `sum_cost_by_batch` prefers platform cost.
  * **New columns** on `agent_timesheets` — platform cost (nullable; null = not reconciled), native prompt / completion / cached / reasoning token counts, serving host, reconcile timestamp. Added by `_ensure_timesheets_schema` for existing databases and by `_create_agent_timesheets_table` for new ones.
  * **New writer** — sets one row's platform columns by `agent_req_id`.
  * **Modified function** `_add_timesheet_entry` — no longer refuses a SKU the catalog doesn't price (the server id check stays).
  * **Modified function** `sum_cost_by_batch` — per row, platform cost when present, else the sum of `calc_cost_*`.
* `tests/component/data/database/test_timesheets.py`, `docs/test-bible/data/database/timesheets.md` — **modified**.

Estimate: 2

#### 3: **Background reconcile per call, unpriced rows recorded - Ada**

After #1 and #2. `record_timesheet_entry` starts a background reconcile for each `openrouter`-routed row (retries, platform write, closed-ledger refresh), and `llm_compat` stops skipping rows it can't price.

**Citations:** `patt.entity.batch-processing`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.debug`.

**Scope:**

* `src/external/llm_compat.py` — **modified**. A row whose local cost can't be computed is still recorded instead of skipped.
  * **Modified function** `send_to_llm_compat` (its timesheet-kwargs helper) — when catalog pricing or token counting raises, returns row values with the available token counts and zero calculated cost instead of no row.
* `src/core/timesheets.py` — **modified**. `record_timesheet_entry` starts the background reconcile for `openrouter`-routed rows; the reconcile (key lookup, retries, row write, ledger refresh) lives here.
  * **Modified function** `record_timesheet_entry` — after the row is written, when the row's routing type (config helper, from its server id and SKU) is `openrouter` and it has a generation id, starts the background reconcile and returns at once.
  * **New function (background reconcile)** — resolves the key for the row's server from the row's candidate (same source as `agent._candidate_server_key`; no key → warn and stop), calls the OpenRouter lookup up to the configured count with exponential backoff (configured base wait, doubling each try), writes the platform columns on success, then, if the row's batch has a `dispatch_ledger` row with `completed_at` set, recomputes that row's `total_cost` (`sum_cost_by_batch`) and `entity_cost` (total ÷ `total_processed`, same rule as the dispatcher) via `update_dispatch_ledger`. Runs off the caller's event loop so it outlives the batch's loop and never blocks a call. The ledger refresh recomputes from the table every time, so it is safe to run more than once and safe against the batch-close write.
* `tests/component/external/test_llm_compat.py`, `docs/test-bible/external/llm_compat.md`, `tests/component/core/test_timesheets.py`, `docs/test-bible/core/timesheets.md` — **modified**.

Estimate: 3

**New patterns:** none.

**Monolith check:** Functional scope N = 6, children M = 3 — split by layer (config/external lookup, data, core reconcile).

**Scope partition check:** every Component scope file and Technical scope item appears in exactly one child's Scope.

### Comments

#### fable — 2026-10-04T01:58:22.906Z
## Susan's answers

1. **Retry wait.** Exponential backoff between retries (not a fixed interval).

2. **Direct servers follow-up (Anthropic/DeepSeek/Kimi).** No follow-up ticket for either right now — table direct-caller platform cost reconciliation entirely for this round. Keep the existing calculated/estimated cost (based on known token quantities and catalog pricing) exactly as it works today for these three servers — don't build the daily-delta or pricing-refresh work now. This leaves the door open to come back later and true up those costs properly once there's better data access, but no new infrastructure for them in this ticket.

#### chuckles — 2026-10-04T01:50:39.107Z
@susan Definition updated with your 8 answers. Research result: only OpenRouter has a per-call cost lookup, so this epic covers OpenRouter-routed models only (details in the Description under Platform research). Two questions left:

1. **Wait between retries.** Retry count is config, default 5. How long between tries — e.g. a fixed number of seconds per try, or doubling? I won't pick a number without you.
2. **Direct servers follow-up.** No per-call lookup exists for Anthropic, DeepSeek or Kimi. Do you want a follow-up ticket for either of these, or neither?
   * (a) **Anthropic daily delta** — compare the Admin API's daily cost per model against our timesheet sum for the same day. Needs an org **admin** key stored somewhere (not the candidate key).
   * (b) **DeepSeek pricing refresh** — our catalog rows (snapshot 2026-06-03) don't match DeepSeek's current published prices, and DeepSeek now charges 2× at peak hours. Our `deepseek-v4-pro` cache-read price (3.625/M) is higher than its input price (0.435/M), which looks wrong.

#### fable — 2026-10-04T01:47:57.221Z
## Susan's answers to Open questions

1. **Reading of the title.** Confirmed — after the batch, query the platform for what each call actually cost and use that for the timesheet/ledger, feeding true costs into execution history so per-item cost can be derived from the real batch total.

2. **Which platforms.** Don't settle for OpenRouter-only. Research what Anthropic, DeepSeek, and Kimi actually expose for cost reporting as part of this ticket's discussion — even a rough per-model delta/average is useful if true per-call billing isn't available. That said, direct-model (non-OpenRouter) support may end up deferred, since pricing for those is already known and stable — it's OpenRouter's variable host routing that makes this reconciliation necessary. Use the platform lookup wherever it's actually available.

3. **Keep or replace calculated cost.** The calculated/catalog cost is a fallback only, used when a direct platform API call isn't possible. Platform cost wins whenever available.

4. **Native token counts and host.** Store both on the row — tokens are definitely wanted, and serving host is in scope too.

5. **Not-ready lookups.** Retry a few times rather than falling back immediately or relying solely on a later sweep.
   - Retry count: config-driven, default **5**.

6. **Where it runs.** Decouple reconciliation from the synchronous batch-close path entirely — don't block batch processing/LLM turnaround waiting on cost data. Update the ledger with cost info asynchronously whenever it becomes available; execution history/UI should just reflect it once it lands.

7. **Opt-in flag.** Reconsider the design: rather than a boolean config flag (new or reusing `probe`), give models a type/routing attribute (e.g., "direct" vs "OpenRouter"). That model setting is the single source of truth for whether a call is routed through OpenRouter and therefore eligible for platform-cost reconciliation.

8. **Rows skipped today (no catalog price).** Yes — include these in scope. Rows that currently get skipped entirely when the catalog has no price should get a row written with platform-sourced cost. This is a known bug that should be rolled into this work.

#### chuckles — 2026-10-04T01:37:36.626Z
@susan

1. **Reading of the title.** Is this "after the batch, ask OpenRouter what each call actually cost and use that for the timesheet/ledger"? Or did you mean something else by "Finish Batch" (for example, a batch that today ends without a cost and should not close until the platform answers)?
2. **Which platforms.** OpenRouter only (the only server with a per-call billed-cost lookup)? Anthropic only offers org-level usage/cost reports, and DeepSeek/Kimi offer no per-call lookup that I know of. If you want those too, say which.
3. **Keep or replace the calculated cost.** Draft keeps `calc_cost_*` untouched and adds a platform-cost column that the batch total prefers (OpenRouter returns one total, not the four cache/input/output parts). Or should the platform cost overwrite the parts (needs a split rule), or replace the catalog pricing entirely for OpenRouter?
4. **Native token counts and host.** The lookup also returns OpenRouter's native token counts and the serving host. Store them on the row too (more columns), or cost only?
5. **Not-ready lookups.** OpenRouter's stats can lag a few seconds behind the response. When a lookup isn't ready at batch close: (a) leave the row on calculated cost, done (draft); (b) wait and retry — how many times and how long (I won't pick a number without you); or (c) a later sweep re-tries unreconciled rows?
6. **Where it runs.** Draft hooks `compute_batch_cost`, so every ledger close (dispatcher, chained hops, candidate, intake) reconciles. That function is synchronous and is called inside async paths, so the HTTP lookups would block the event loop while the batch closes. OK as-is, or limit it to the dispatcher's batch close, or make it async (touches ~20 call sites)?
7. **Opt-in flag.** New per-server config flag (draft), or reuse the existing `probe` flag (both mean "this is a routing platform")?
8. **Rows that are skipped today.** When the catalog has no price for a SKU, no timesheet row is written at all. Should this epic also write those rows (cost from the platform), or leave that alone?

---

_Implementation detail may live in git history on `origin/dev`._
