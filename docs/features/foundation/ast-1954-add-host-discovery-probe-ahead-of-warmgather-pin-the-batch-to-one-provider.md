# AST-1954 — Add host-discovery probe ahead of warm/gather; pin the batch to one provider

<!-- linear-archive: AST-1954 archived 2026-10-08 -->

## Linear archive (AST-1954)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1954/add-host-discovery-probe-ahead-of-warmgather-pin-the-batch-to-one  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

[AST-1953](https://linear.app/astralcareermatch/issue/AST-1953) removes today's hard-coded single-host pin. After that, every OpenRouter call routes on its own, and prompt caches belong to a single host. If the warm call lands on one host and the parallel (gather) calls land on others, the warm call bought nothing. On `anticipate_scan` that costs roughly 4x on input per call, about 20x more than any price difference between hosts. Susan wants each dispatch batch to send one cheap **probe** first, letting OpenRouter pick the host. The batch is then **locked** to that host for the warm call and the gather calls, and the host is recorded on the batch's `dispatch_ledger` row. This only matters for OpenRouter, so the probe and the batch→host map live in the OpenRouter external.

**Decisions (Susan, 2026-10-03):**

* **Pin shape.** The probe routes freely: it carries the agent's provider object from [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953/refactor-agent-settings-and-ingest-per-endpoint-model-options) unchanged, so OpenRouter chooses the host and fallbacks are allowed. Warm and gather send `only: [<host>]`. There is no fallback mid-batch, so a host failure fails the call. Susan wrote "order for the probe". There is no host list to put in an `order` field before the probe runs, so the probe sends none and lets the router decide.
* **Probe, then warm, then gather.** The probe doesn't warm the cache, so the warm call stays.
* **No slug mapping.** `openrouter.py` keeps a simple batch→host map and uses the host exactly as OpenRouter returns it in the response's `provider` field.
* **No fallback when the probe fails.** The batch's calls fail and the entities take the ordinary [`patt.task.dispatch-retry`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.dispatch-retry.md>) path: retry, then error.
* **The host is recorded in** `dispatch_ledger`**.** For direct servers it is always that server's host.

**As-built facts (**`origin/dev` **@** `5d4d8e2f2`**;** [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953/refactor-agent-settings-and-ingest-per-endpoint-model-options) **children in flight):**

* **The warm call is the batch's first real call.** `dispatcher._warm_then_gather` (per-row path) and the consult chunk loop (chunk 0, then the rest) both run it on its own, wait `cache_warm_delay_seconds`, then fire the rest in parallel. The probe goes in front of that first call. The dispatcher's sequencing does not change.
* [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953/refactor-agent-settings-and-ingest-per-endpoint-model-options) **as shipped** does not create `src/external/openrouter.py`, has no endpoint catalog, and leaves served-host logging to this ticket. It does build the OpenRouter provider object from the agent row (`quantizations`, `allow_fallbacks`, `only`, `ignore`, `sort`) and merges it in `llm_compat`. **This epic builds on** [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953/refactor-agent-settings-and-ingest-per-endpoint-model-options) **being on** `dev`**.**
* **The host goes back through** `agent.py` **to the ledger, not through the dispatcher.** `ctx` is copied on the way down (`task_ctx`, `hop_ctx`, `merged_ctx`), and dispatch results are summed into counters, so a host set inside the call would not reliably reach the dispatcher. `agent.py` already writes ledger rows for chained hops (`_open_run_next_hop_ledger` / `_finalize_run_next_hop_ledger`). So `do_task` records the host returned with the response on the ledger row of the active batch (`log_batch_id`). That covers dispatcher batches and hop rows alike. `dispatcher.py` does not change.
* **Host naming risk, accepted.** OpenRouter's docs describe `only` in terms of provider **slugs** (`deepinfra`), while the response names the provider (`DeepInfra`). An `only` list matching no provider fails with a 404. Per Susan, the response value is used as-is. UAT AC 7 is the tripwire. If the warm call 404s, a return trip adds the mapping.

## Functional scope

1. **One probe per batch.** In a dispatch batch, the first OpenRouter call for a given request-parameter block is preceded by **one** probe request:
   * its content is trivial (the index plus "respond with 1");
   * it has no system block and no `cache_control`;
   * every other field is identical to the real call: `max_tokens`, temperature/effort and AST-1953's provider object.

   Calls that arrive at the same time wait for that one probe and do not send their own.
2. **Lock the batch to the probe's host.** Every real call in that batch for that parameter block, including the warm call, sends `only: [<probe host>]` in place of the agent's `only`. The rest of the agent's provider object (for example `quantizations`) is kept.
3. **A failed probe fails the batch's calls.** If the probe errors or returns no `provider`, no real request is sent for that batch key. Each call returns an ordinary failure, and the entity takes `patt.task.dispatch-retry`. The failure is remembered for the batch key, so the batch sends no second probe.
4. **The host comes back with every response.** Every `llm_compat` result carries the host that served it:
   * OpenRouter: the response's `provider`;
   * other compat servers: the server's own label.

   For Anthropic-direct calls, `agent.py` uses the server's label. The per-call INFO line names the served host.
5. **The host is recorded on the batch ledger row.** `do_task` writes the host on the `dispatch_ledger` row of the active batch id. This covers both dispatcher batch rows and chained-hop rows.
6. **Scope boundary.** Only servers whose `LLM_SERVER_CONFIG` probe flag is on (OpenRouter) probe or lock. Calls with no batch id (adhoc/workbench) send no probe and no lock. `dispatcher.py` does not change.

## Component scope

* `src/utils/config.py`: **modified**. Per-server probe flag on `LLM_SERVER_CONFIG` (on for `openrouter`) and the probe message text.
* `src/external/openrouter.py`: **new**. The probe request and the per-batch host map.
* `src/external/llm_compat.py`: **modified**. Calls the host map before sending when the server is flagged and a batch id is set, merges the `only` lock, fails without sending when the probe failed, and returns the served host.
* `src/utils/logging.py`: **modified**. `log_llm_batch_summary`'s INFO line names the served host.
* `src/core/agent.py`: **modified**. Records the returned host (or the server label for Anthropic-direct) on the active batch's `dispatch_ledger` row.
* `src/data/database.py`: **modified**. `dispatch_ledger` gains a host column, which is writable through `update_dispatch_ledger` and returned by the ledger readers.
* Tests and bibles (**modified** or **new**, Betty in `qa-child`):
  * `tests/component/utils/test_config.py`
  * `tests/component/external/test_openrouter.py` (**new**)
  * `tests/component/external/test_llm_compat.py`
  * `tests/component/utils/test_logging_batch.py`
  * `tests/component/core/test_agent.py`
  * `tests/component/data/database/test_dispatch_ledger.py`
  * `docs/test-bible/utils/config.md`
  * `docs/test-bible/external/openrouter.md` (**new**)
  * `docs/test-bible/external/llm_compat.md`
  * `docs/test-bible/utils/logging_batch.md`
  * `docs/test-bible/core/agent.md`
  * `docs/test-bible/data/database/dispatch_ledger.md`

## Technical scope

* `src/utils/config.py`:
  * **New server field:** a boolean probe flag on every `LLM_SERVER_CONFIG` entry, true on `openrouter` only, checked by the server validator. No server name is hard-coded outside config.
  * **New constant:** the probe message text.
* `src/external/openrouter.py`:
  * **New probe function:** takes the real call's fully assembled request arguments, swaps the content for the probe message, drops the system block, sends it through the same client and returns the response's `provider`. It records the probe on the timesheet through the caller's `record_timesheet` callback, so its cost shows in the ledger.
  * **New host-map function:** keyed on (batch id, the request arguments minus content and system), it returns the batch's host or the remembered probe failure. Exactly one probe runs per key, even when first calls arrive at the same time. Entries are never evicted; a restart clears them, and no cap or TTL is added.
* `src/external/llm_compat.py`:
  * **Modified request assembly in** `send_to_llm_compat`: when the server's probe flag is on and a batch id is set, gets the host from the map. On success it sets `provider.only = [host]`. On a remembered failure it returns a failure result with no request sent. Otherwise the request is exactly as today.
  * **Modified result:** carries `host`, which is the response's `provider` or, when that is absent, the server's label. The served host goes into the per-call summary.
* `src/utils/logging.py`: **modified** `log_llm_batch_summary`. The INFO line adds the served host and stays one line per call.
* `src/core/agent.py`: **modified call path** (`do_task` via `_send_to_server`). After each call it writes the result's host, or the server label for the Anthropic-direct client, to the `dispatch_ledger` row for `log_batch_id` when one is set.
* `src/data/database.py`:
  * **Modified** `dispatch_ledger` schema-ensure: adds the host column (DDL only, per AST-1497).
  * **Modified** `_LEDGER_UPDATE_COLS`: includes it.
  * **Modified readers:** return it.

## Architectural definition

* **Patterns to reuse:**
  * [`patt.entity.batch-processing`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>): the host map is keyed on the batch id the claim minted, and the host is recorded on that batch's ledger row. No new batch identity is invented.
  * [`patt.task.dispatch-retry`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.dispatch-retry.md>): a failed probe, or a warm/gather call that fails on the locked host, is an ordinary failed call, so the entity goes to `_RETRY` and then the configured error state (Susan: "retry and error out").
* **New patterns proposed:** `none`.
* **Applicable statutes:**
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>): the probe request/response and the host-map decisions log generous ungated `logger.debug`.
  * [`stat.logging.info`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>): the served host extends the existing per-call INFO line. There is no second per-call line.
  * [`stat.logging.warning`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>): a failed probe leaves each affected entity on the retry path with the existing per-item warning (who and why). There is no extra per-call warning tally.

## Acceptance criteria

"Stubbed client" means the component-test stub of the Anthropic SDK client used by `test_llm_compat.py` / `test_agent.py`. All checks run on the shipped tree, after [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953/refactor-agent-settings-and-ingest-per-endpoint-model-options).

1. **One probe per batch key, before the first real call.**
   * **Check (component test, stubbed client, batch id set, server** `openrouter`**):** one awaited `send_to_llm_compat` call, then three concurrent calls for the same model and settings. The stub records exactly **5** requests, and the first has the probe message as its only content.
   * **Fails if:** there are 0 or more than 1 probes, or the probe is not first.
2. **The probe matches the real call and carries no cache.**
   * **Check (same test):** the probe's request arguments equal the first real call's, except the content and the missing `system`. `max_tokens`, temperature/effort and `provider` are identical. No `cache_control` appears in the probe, and the probe has no `provider.only` beyond what the agent set.
   * **Fails if:** any of those fields differs, a `cache_control` block is present, or the probe carries a host lock.
3. **Warm and gather are locked to the probe's host.**
   * **Check (component test):** the stubbed probe response has `provider: "DeepInfra"`. Every later request in the batch carries `provider.only == ["DeepInfra"]`, and AST-1953's other provider keys (for example `quantizations: ["bf16"]`) are unchanged.
   * **Fails if:** `only` is missing or different, or another provider key is dropped or altered.
4. **A failed probe fails the batch's calls with no fallback.**
   * **Check (component test):** the stubbed probe raises a 429. The stub records exactly **1** request (the probe) across one awaited call and three concurrent calls in that batch, and every call returns `success: False`.
   * **Fails if:** any real request is sent, a second probe is sent, or any call reports success.
5. **No probe outside scope.**
   * **Check (component test):** with server `kimi` or `deepseek`, or with `openrouter` and no batch id, the stub records zero probes and no request gets a host lock.
   * **Check:** `rg -n '"openrouter"' src/external/` returns nothing.
   * **Check:** `git diff origin/dev...HEAD --stat -- src/core/dispatcher.py` is empty.
   * **Fails if:** there is a probe or lock in those cases, a hit for `"openrouter"`, or a dispatcher change.
6. **The host comes back and is recorded.**
   * **Check (component test):** an `llm_compat` result for a stubbed response with `provider: "DeepInfra"` has `host == "DeepInfra"`, and the per-call INFO line contains `DeepInfra`.
   * **Check (component test, temp DB):** after `do_task` runs under a `log_batch_id` with a saved ledger row, `get_dispatch_ledger(<id>)` returns that host.
   * **Check:** for an Anthropic-direct agent, the ledger row's host is the `anthropic` server label.
   * **Fails if:** the host is missing from the result, the line or the ledger row, or it is wrong for direct.
7. **Live lock works (UAT).**
   * **Check:** run one live `anticipate_scan` batch of at least 3 entities on an OpenRouter agent. The batch log shows one probe. Every call's INFO line names the same host, and the batch's `dispatch_ledger` row shows it. Timesheet `inputcached` is greater than 0 on every call after the warm call.
   * **Fails if:** the warm call returns 404 (meaning `only` didn't accept the response's provider name), the hosts differ, the ledger host is empty, or `inputcached` is 0 after the warm call.

## Open questions

None.

## Proposed child tickets

#### 1!: **Per-batch probe and host lock on the OpenRouter path - Hedy**

The first OpenRouter call of each dispatch batch sends one probe first, and the batch's real calls are locked to the probe's host with `only`. A failed probe fails the batch's calls with no fallback. Every `llm_compat` result returns the host that served it, and the per-call INFO line names it. This child does **not** write the ledger (#2). Requires [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953/refactor-agent-settings-and-ingest-per-endpoint-model-options) on `dev`. Hedy built AST-1953's wire child in `llm_compat`.
**Citations:** `patt.entity.batch-processing` (host map keyed on the claim's batch id); `patt.task.dispatch-retry` (probe failure is an ordinary failed call); `stat.logging.debug`; `stat.logging.info`.
**Scope:**

* `src/utils/config.py` (**modified**):
  * **New server field:** a boolean probe flag on every `LLM_SERVER_CONFIG` entry, true on `openrouter` only, checked by the server validator. No server name is hard-coded outside config.
  * **New constant:** the probe message text.
* `src/external/openrouter.py` (**new**):
  * **New probe function:** takes the real call's fully assembled request arguments, swaps the content for the probe message, drops the system block, sends it through the same client and returns the response's `provider`. It records the probe on the timesheet through the caller's `record_timesheet` callback, so its cost shows in the ledger.
  * **New host-map function:** keyed on (batch id, the request arguments minus content and system), it returns the batch's host or the remembered probe failure. Exactly one probe runs per key, even when first calls arrive at the same time. Entries are never evicted; a restart clears them, and no cap or TTL is added.
* `src/external/llm_compat.py` (**modified**):
  * **Modified request assembly in** `send_to_llm_compat`: when the server's probe flag is on and a batch id is set, gets the host from the map. On success it sets `provider.only = [host]`. On a remembered failure it returns a failure result with no request sent. Otherwise the request is exactly as today.
  * **Modified result:** carries `host`, which is the response's `provider` or, when that is absent, the server's label. The served host goes into the per-call summary.
* `src/utils/logging.py` (**modified**): `log_llm_batch_summary`'s INFO line adds the served host and stays one line per call.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/utils/test_config.py`
  * `tests/component/external/test_openrouter.py` (**new**)
  * `tests/component/external/test_llm_compat.py`
  * `tests/component/utils/test_logging_batch.py`
  * `docs/test-bible/utils/config.md`
  * `docs/test-bible/external/openrouter.md` (**new**)
  * `docs/test-bible/external/llm_compat.md`
  * `docs/test-bible/utils/logging_batch.md`

Estimate: 3

#### 2: **Record the serving host on the dispatch ledger - Katherine**

`do_task` records the host returned with each response on the active batch's `dispatch_ledger` row, using the server label for Anthropic-direct calls. The ledger table gains the host column. This child comes after #1, whose `llm_compat` result supplies `host`. It does **not** touch the external layer (#1) or `dispatcher.py`.
**Citations:** `patt.entity.batch-processing` (host recorded on the claim's ledger row); `stat.logging.debug`.
**Scope:**

* `src/core/agent.py` (**modified**): **modified call path** (`do_task` via `_send_to_server`). After each call it writes the result's host, or the server label for the Anthropic-direct client, to the `dispatch_ledger` row for `log_batch_id` when one is set.
* `src/data/database.py` (**modified**):
  * **Modified** `dispatch_ledger` schema-ensure: adds the host column (DDL only, per AST-1497).
  * **Modified** `_LEDGER_UPDATE_COLS`: includes it.
  * **Modified readers:** return it.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/core/test_agent.py`
  * `tests/component/data/database/test_dispatch_ledger.py`
  * `docs/test-bible/core/agent.md`
  * `docs/test-bible/data/database/dispatch_ledger.md`

Estimate: 2

**New patterns:** none.

**Monolith check:** there are 6 functional items across 2 children. #1 owns items 1–4 and 6 (the external path). #2 owns item 5 (ledger).

**Scope partition check:**

* **#1:** `config.py`, `openrouter.py`, `llm_compat.py`, `logging.py`, plus their tests and bibles.
* **#2:** `agent.py`, `database.py`, plus their tests and bibles.
* No file is claimed twice and none is unclaimed.

---

## Original brief

NOTE: This needs to live in the openrouter external, NOT [agent.py](<http://agent.py>), because it is moot for other direct hosts, so it's in Foundation instead of Agent.

## Context

Batch dispatch currently runs **warm → gather**: a warming pass loads cache blocks, then the batch is sent. No `provider` object is set on any request, so each call routes independently on OpenRouter's price-weighted default. Two consequences:

**Cache affinity is lost.** Prompt caches are provider-local — the serving host's KV cache. If the warm pass lands on host A and gather calls land on B and C, the warming pass bought nothing and every gather call pays full input price. `anticipate_scan` carries \~25K input tokens; on `moonshotai/kimi-k2-thinking` (0.60 input / 0.15 cache read) that is **$0.015 cold versus $0.0038 warm**, a 4x difference per call. The price spread between hosts of the same model is roughly $0.0005 on the same token count, so **cache affinity is worth \~20x more than price shopping.**

**No failover and no precision floor.** `openai/gpt-oss-120b` is served at bf16 by DekaLLM, DeepInfra, AkashML and Crusoe, and at fp4 by CoreWeave, Nebius, Parasail and BaseTen. Unpinned, precision varies per call with nothing in the logs saying so. Separately, a 429 on 2026-10-03 (`limit_source: upstream_provider_shared_pool`, `provider_name: DekaLLM`) stalled `anticipate_scan` with no route around it.

## Problem

There is no mechanism to discover which host will serve a batch *before* committing expensive work to it, and no mechanism to hold a batch on one host once discovered.

Using the first real call as the discovery mechanism does not work: it serializes the batch behind a full inference (\~40s on a large prompt with reasoning) before the remaining calls can be pinned and dispatched in parallel.

## Scope

Insert a **probe** phase, making dispatch **probe → warm → gather**.

### Phase 1 — Probe

One call per batch, before warming.

* Trivial message body (e.g. the candidate UUID plus "respond with 1").
* **Carries the agent's full routing-relevant parameter block**, unchanged: `max_tokens`, `quantizations`, `response_format` / `structured_outputs`, `reasoning_effort`, `temperature`. This is load-bearing — OpenRouter filters eligible providers on `max_tokens` support, tool support and `structured_outputs` *before* selecting, so a probe with a smaller or simpler parameter set samples a **larger** eligibility set and can name a host the real calls cannot use.
* `allow_fallbacks: true`, no `only`. Let the router choose.
* Read `provider` from the response body. That is the host for this batch.
* Carries **no cache blocks.** Host discovery and cache loading are separate jobs: a probe carrying the payload would pay a full uncached input pass to a host that may then be unusable, and one probe cannot warm the differing cache block sets (A–D) that tasks within a batch require.

Cost note: with `max_tokens` matched to the agent's spec and reasoning on by default, the probe may emit a few hundred reasoning tokens. At gpt-oss-120b's 0.18/M that is under $0.0001. Acceptable; do not optimize it by lowering `max_tokens`, which would break eligibility matching.

### Phase 2 — Warm

Unchanged in purpose, now pinned:

```
"provider": {
  "only": ["<slug from probe>"],
  "quantizations": ["<agent quantization>"],
  "allow_fallbacks": true
}
```

### Phase 3 — Gather

Same `provider` block as warm. Calls may now be dispatched in parallel, since the host is known and the cache is loaded.

### Fallback accounting

`allow_fallbacks: true` is deliberate — correctness over cost. But a fallback means a cold-cache call, so it is a **cost** event, not just a latency event. Record the response `provider` on every call and count mismatches against the pinned host. A host that falls back often is quietly expensive.

## Acceptance criteria

**Given** a batch for an agent configured at bf16, **when** dispatch runs, **then** a probe call precedes the warm pass **and** the probe request contains the same `max_tokens`, `quantizations` and output-format parameters as the batch's real calls **and** the probe carries no cache blocks.

**Given** a probe that returns `provider: "DeepInfra"`, **when** the warm and gather phases run, **then** every request in those phases carries `provider.only: ["deepinfra"]` **and** the logged serving provider for each is DeepInfra.

**Given** a warmed batch pinned to one host, **when** gather calls execute, **then** `timesheet.inputcached` is greater than zero on calls after the warm pass.

**Given** a pinned host that returns 429 mid-batch, **when** `allow_fallbacks` is true, **then** the call succeeds on another host at the same quantization **and** the provider mismatch is logged as a fallback event with the cold-cache cost attributed.

**Given** a probe whose named host is subsequently unavailable, **when** the warm pass is assembled, **then** no cache payload has been spent on the unusable host.

## Out of scope

* Periodic or price-based host selection. The probe delegates selection to OpenRouter's router, which already prioritises price and skips providers with recent outages. A routing table is a separate decision.
* Cache TTL management and batch sizing against it. Current volume does not justify it; `timesheet.inputcached` already surfaces the signal if the assumption breaks.
* Agent settings plumbing (`quantization`, `temperature`, `reasoning_effort`, provider policy fields) — tracked separately. **This ticket depends on it:** without a per-agent `quantization` field there is nothing to put in `provider.quantizations`.

## Notes

* OpenRouter's default routing is inverse-square **weighted random** among the cheapest stable providers, not deterministic cheapest. The probe therefore returns *a* cheap host, sampled — two probes seconds apart may disagree. That is fine for affinity; do not model it as price-optimal. `sort: "price"` makes it deterministic if that is wanted later.
* `provider` in the response body is the ground truth for what served a call. The 429 error metadata carries `provider_name` as well, so fallback and failure attribution both work off the same field.

### Comments

#### chuckles — 2026-10-03T21:59:53.107Z
@susan Five questions before this can go to Todo (details and recommendations are in the Description's Open questions):

1. **Pin shape:** `order: [host]` + `allow_fallbacks: true` (recommended), or `only: [host]` as briefed? OpenRouter's `only` restricts routing to the listed hosts, so it can't fail over on a 429.
2. **Probe vs warm-call discovery:** on `dev` the warm pass already is the first real call, run on its own. Do you want to keep the probe (adds one short serial call), or pin to whatever host serves the warm call (no probe)?
3. **Provider name to slug:** where should the mapping come from?
   * (a) `openrouter.py` fetches the model's public endpoints list (recommended)
   * (b) `agent.py` passes the catalog map down
   * (c) lowercase/hyphenate the name

   And on a probe failure or no match: continue unpinned with one WARNING (recommended), or stop the batch?
4. **Fallback accounting:** the per-call INFO line only (recommended), or timesheet columns too? Separately, should the probe call be recorded in the timesheet (recommended: yes)?
5. **Pin registry lifetime:** never evict in process memory (recommended), or have `dispatcher.py` clear it when the batch is released?

---

_Implementation detail may live in git history on `origin/dev`._
