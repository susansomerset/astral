# AST-2142 — Batch_mode "each" is throwing 429's

<!-- linear-archive: AST-2142 archived 2026-10-16 -->

## Linear archive (AST-2142)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2142/batch-mode-each-is-throwing-429s  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** unassigned  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

A `batch_mode "each"` dispatch (dispatch row `batch_call_mode = 0`) runs `_warm_then_gather` in `src/core/dispatcher.py`. It sends the first entity, waits `cache_warm_delay_seconds`, then fires **every** remaining claimed entity in the same instant with one `asyncio.gather`. In the `prefilter_company` run below, about 15–20 calls hit OpenRouter in the same second, a burst of them got 429s together, and they kept retrying in near-lockstep. One call was still refused after 5/5 retries ([AST-2010](https://linear.app/astralcareermatch/issue/AST-2010) retry policy, `exhausted_stops_batch: True`), so the dispatcher stopped the batch ("LLM provider rate limit: still 429 after retries … The batch is stopping"). `tbmc_fi` went to `HOMEPAGE_READY_RETRY`.

**What the limit actually is (round 1 findings):**

* **It is not an OpenRouter limit, and not workspace- or key-specific.** The 429 body says `limit_source: upstream_provider_shared_pool`, `provider_name: Parasail`, `is_byok: False`: "qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream." That is Parasail's capacity for that model, shared by **all** OpenRouter customers routed there without their own key.
* OpenRouter's [limits doc](<https://openrouter.ai/docs/api-reference/limits>) says paid (non-`:free`) models have **no platform-level request cap**, and "making additional accounts or API keys will not affect your rate limits, as we govern capacity globally."
* **There is no published number.** Any spacing we choose is empirical.
* The [AST-1959](https://linear.app/astralcareermatch/issue/AST-1959) per-batch host lock pins the batch to one host, which opts out of OpenRouter's automatic provider fallback. An upstream 429 therefore has nowhere else to go.

**Susan (round 2, verbatim):** "Question: What about doing a config-driven stagger instead of a cap? I think caps should be based on the dispatch_task record ONLY, because we've had issues with buried caps before. Let's do a config driven stagger that lets the gather function run asynch but with a stagger in between the calls. We can try it a 1 second to start, and see how that goes."

## To-be

`_warm_then_gather` still runs the remaining entities **concurrently**, but it **starts** them one stagger interval apart instead of all at once. Call *k* of the rest starts about *k* × stagger after the warm delay; calls still overlap and run in parallel once started. The interval is a single `config.py` setting, starting at **1.0 second**, with `0` meaning today's behavior (no stagger). **No new in-flight cap anywhere:** the only cap on how much a batch does stays on the `dispatch_task` record (`batch_size`), and OpenRouter's `concurrency` block keeps no `max_concurrent`.

## Proposed steps

1. Add a stagger setting (seconds, default `1.0`) to `ASTRAL_CONFIG` in `src/utils/config.py`, right beside `cache_warm_delay_seconds`, with an inline comment saying what it does and that `0` disables it.
2. In `_warm_then_gather`, after the existing warm delay, start each remaining entity with its own offset of index × stagger before calling `one_fn`, then gather them all as today. The calls stay async and overlapping, and exception handling and result order stay unchanged. Update the docstring.
3. Leave the AST-2010 retry/backoff block and `exhausted_stops_batch` as they are. The stagger reduces how many calls collide; retries still catch whatever gets through.
4. Out of scope unless Susan says otherwise: the `batch_call_mode = 1` chunked consult path (`dispatcher.py` around line 883) fires its chunks with its own `asyncio.gather`. This bug is about `each` mode, so that path is untouched.

**Two consequences to watch:**

* The stagger applies to **every** `each`-mode task, not just OpenRouter ones. That includes company tasks and `fetch_jd`, because `_warm_then_gather` doesn't know which server a task uses.
* At 1s, the last call in a batch starts about `batch_size` seconds after the first. For example, a 100-entity batch spends about 100s just launching calls.

## Component scope

* `src/utils/config.py` — modified — new stagger setting in `ASTRAL_CONFIG` next to `cache_warm_delay_seconds`; one source of truth for the interval.
* `src/core/dispatcher.py` — modified — `_warm_then_gather` spaces out when each concurrent call starts, using that setting.

## Technical scope

* `src/utils/config.py` — new field in `ASTRAL_CONFIG` (float seconds, default 1.0, 0 = off). It is config-driven per Susan, with no number hard-coded in the dispatcher.
* `src/core/dispatcher.py` — modified function `_warm_then_gather`. Each entity after the first waits its own index × stagger before calling `one_fn`, while everything stays inside the existing single `asyncio.gather`, so concurrency, `return_exceptions` handling, and result order are preserved.

## Ancestor candidates

- [ ] [AST-2010](https://linear.app/astralcareermatch/issue/AST-2010) — OpenRouter 429 retry (5x doubling) and batch error on exhausted rate limit (Done). It owns the retry policy that stopped this batch; the stagger works alongside it. No feature doc on disk yet.
- [ ] [AST-1875](https://linear.app/astralcareermatch/issue/AST-1875) — Scheduled Tasks concurrent-tasks dropdown (Archive; `docs/features/dispatcher/ast-1875-add-a-selection-box-on-scheduled-tasks-to-set-concurrent-tasks-limit.md`). Same "caps live on visible operator settings, not buried" principle; dispatcher-side precedent for a config-driven throughput knob.
- [ ] [AST-1959](https://linear.app/astralcareermatch/issue/AST-1959) — Per-batch probe and host lock on the OpenRouter path (Archive; `docs/features/foundation/ast-1959-per-batch-probe-and-host-lock-on-the-openrouter-path.md`). The host pin is why an upstream-pool 429 can't fall back to another provider.
- [ ] [AST-1877](https://linear.app/astralcareermatch/issue/AST-1877) — Model/server catalog + shared compat client (Archive; `docs/features/agent/ast-1877-model-server-catalog-compat-client.md`). Introduced the `concurrency` block; less relevant now that the fix stays out of it.

## Original report

I think OpenRouter has a cap of how many simultaneous calls it can support.  Investigate what that limit is, and propose a config-driven control method that can be set.  Look also if the rate-limit is workspace wide or api-token specific.

```
[2026-10-12 15:37:53] INFO src.core.dispatcher: abrams | dispatch company starting prefilter_company — 615 available (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.0s
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.0s stop=end_turn tokens in=6012 out=143
[2026-10-12 15:37:53] INFO src.core.roster: ki_se | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.6s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.9s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.1s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.5s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 2.0s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.3s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.2s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.1s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.4s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.6s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 4.0s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.1s
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.5s stop=end_turn tokens in=937 out=145
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 5.4s stop=end_turn tokens in=2491 out=146
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.9s
[2026-10-12 15:37:53] INFO src.core.roster: scientificwisdom_org | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.4s
[2026-10-12 15:37:53] INFO src.core.roster: merren_io | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 7.2s
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 6.2s
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.0s stop=end_turn tokens in=2197 out=149
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 5.1s stop=end_turn tokens in=4866 out=139
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.0s stop=end_turn tokens in=2254 out=145
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.1s stop=end_turn tokens in=1804 out=142
[2026-10-12 15:37:53] INFO src.core.roster: cattonline_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:53] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 9.1s
[2026-10-12 15:37:53] INFO src.core.roster: research_utexas_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:53] INFO src.core.roster: neurology_vcu_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:53] INFO src.core.roster: academicjournals_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.2s stop=end_turn tokens in=1537 out=149
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.7s stop=end_turn tokens in=2979 out=149
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 13.5s stop=end_turn tokens in=5430 out=143
[2026-10-12 15:37:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.0s stop=end_turn tokens in=4358 out=149
[2026-10-12 15:37:54] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 8.5s
[2026-10-12 15:37:54] INFO src.core.roster: source_washu_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:54] INFO src.core.roster: cen_acs_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:37:54] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 17.0s stop=end_turn tokens in=4400 out=139
[2026-10-12 15:40:07] INFO src.core.roster: headaches_org | company state: HOMEPAGE_READY -> ERROR_PREFILTER_COMPANY_NO_JOBLIST_LINKS (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:07] INFO src.core.roster: alphaxiv_org | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:07] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 19.1s stop=end_turn tokens in=2186 out=145
[2026-10-12 15:40:07] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 17.7s stop=end_turn tokens in=2325 out=145
[2026-10-12 15:40:07] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 20.3s
[2026-10-12 15:40:08] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.7s stop=end_turn tokens in=8101 out=162
[2026-10-12 15:40:08] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.4s stop=end_turn tokens in=6450 out=153
[2026-10-12 15:40:08] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.3s stop=end_turn tokens in=8934 out=161
[2026-10-12 15:40:08] INFO src.core.roster: mensbrainhealth_org | company state: HOMEPAGE_READY -> ERROR_PREFILTER_COMPANY_NO_JOBLIST_LINKS (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:08] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 24.3s stop=end_turn tokens in=1934 out=142
[2026-10-12 15:40:08] INFO src.core.roster: aotf_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:08] INFO src.core.roster: alum_mit_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:08] INFO src.core.roster: treatnow_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:08] INFO src.core.roster: encephalitis_info | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:08] INFO src.core.roster: blog_qualys_com | company state: HOMEPAGE_READY -> ERROR_PREFILTER_COMPANY_NO_JOBLIST_LINKS (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:08] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 28.4s stop=end_turn tokens in=5099 out=108
[2026-10-12 15:40:08] INFO src.core.roster: research_childrenshospital_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:08] INFO src.core.roster: hopeforminds_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:40:08] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 45.3s stop=end_turn tokens in=1957 out=131
[2026-10-12 15:40:08] INFO src.core.roster: ir_madrigalpharma_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:11] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 5.3s stop=end_turn tokens in=3524 out=145
[2026-10-12 15:42:11] INFO src.core.roster: astar_edu_sg | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.1s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.6s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.8s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.5s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.4s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.4s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 15:42:11] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 5.5s stop=end_turn tokens in=5486 out=144
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.7s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.6s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 2.0s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.5s
[2026-10-12 15:42:11] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.5s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.9s
[2026-10-12 15:42:36] INFO src.core.roster: fcc_gov_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 6.5s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 6.9s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.0s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.0s
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 5.8s stop=end_turn tokens in=3288 out=108
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.1s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.0s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 7.9s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.0s
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.3s stop=end_turn tokens in=1174 out=142
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 4.7s stop=end_turn tokens in=6959 out=137
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.3s
[2026-10-12 15:42:36] INFO src.core.roster: uclahealth_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.4s
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.5s stop=end_turn tokens in=1613 out=147
[2026-10-12 15:42:36] INFO src.core.roster: emotion_utu_fi | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: atsu_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 13.8s
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 9.8s stop=end_turn tokens in=4167 out=148
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.8s stop=end_turn tokens in=2969 out=145
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.6s stop=end_turn tokens in=3794 out=149
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 10.2s
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 9.5s stop=end_turn tokens in=2411 out=156
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 15.4s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 15.1s
[2026-10-12 15:42:36] INFO src.core.roster: pmc_ncbi_nlm_nih_gov_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: ucl_ac_uk | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: cedarssinai_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: legendbiotech_com_4 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: bristol_ac_uk | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 16.8s stop=end_turn tokens in=9173 out=161
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.3s stop=end_turn tokens in=2067 out=144
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.3s stop=end_turn tokens in=2368 out=140
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 15.4s stop=end_turn tokens in=1689 out=149
[2026-10-12 15:42:36] INFO src.core.roster: madonna_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: nmlabs_com | company state: HOMEPAGE_READY -> ERROR_PREFILTER_COMPANY_NO_JOBLIST_LINKS (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 22.3s stop=end_turn tokens in=2586 out=148
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 20.7s stop=end_turn tokens in=3993 out=139
[2026-10-12 15:42:36] INFO src.core.roster: mhir_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: ncat_edu | company state: HOMEPAGE_READY -> ERROR_PREFILTER_COMPANY_NO_JOBLIST_LINKS (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 31.6s
[2026-10-12 15:42:36] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 25.2s stop=end_turn tokens in=1384 out=71
[2026-10-12 15:42:36] INFO src.core.roster: mckinsey_com_4 | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: mcgill_ca | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] INFO src.core.roster: pa_gov_3 | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 16.4s
[2026-10-12 15:42:36] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 19.6s
[2026-10-12 15:43:34] WARNING src.external.llm_compat: LLM openrouter task=prefilter_company 41.0s error=Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'Provider returned error', 'error_type': 'rate_limit_exceeded'}, 'request_id': 'gen-1791819772-Q9qxXESn6BSJnqk2BGe0', 'metadata': {'raw': 'qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Parasail', 'is_byok': False, 'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider routing: https://openrouter.ai/docs/features/provider-routing'}}
[2026-10-12 15:43:34] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 48.7s stop=end_turn tokens in=3217 out=116
[2026-10-12 15:43:34] INFO src.core.roster: tbmc_fi | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:43:34] WARNING src.core.roster: tbmc_fi -> HOMEPAGE_READY_RETRY [do_task: Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'Provider returned error', 'error_type': 'rate_limit_exceeded'}, 'request_id': 'gen-1791819772-Q9qxXESn6BSJnqk2BGe0', 'metadata': {'raw': 'qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Parasail', 'is_byok': False, 'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider routing: https://openrouter.ai/docs/features/provider-routing'}}]
[2026-10-12 15:43:34] WARNING src.core.dispatcher: abrams | dispatch company prefilter_company
  LLM provider rate limit: still 429 after retries (Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'Provider returned error', 'error_type': 'rate_limit_exceeded'}, 'request_id': 'gen-1791819772-Q9qxXESn6BSJnqk2BGe0', 'metadata': {'raw': 'qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Parasail', 'is_byok': False, 'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider routing: https://openrouter.ai/docs/features/provider-routing'}})
  The batch is stopping
[2026-10-12 15:43:34] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 68.3s stop=end_turn tokens in=7206 out=124
[2026-10-12 15:43:34] INFO src.core.roster: fda_gov_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
[2026-10-12 15:43:34] INFO src.core.roster: broadinstitute_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-f06c2d02-9260-4a2d-8717-3233eaea9640)
```

### Comments

#### chuckles — 2026-10-12T18:30:36.723Z
Project was unset; assigned **Astral Dispatcher** (`_warm_then_gather` is dispatcher code; ancestors AST-2010 / AST-1875 live there).

---

_Implementation detail may live in git history on `origin/dev`._
