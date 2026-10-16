# AST-2137 — Prefilter fails

<!-- linear-archive: AST-2137 archived 2026-10-16 -->

## Linear archive (AST-2137)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2137/prefilter-fails  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Prior occurrences

* none found (not labeled `production`, §0b skipped).
* Narrowed per Susan (option 2): the `JOB:<n>` → `JO` decode failures in this log are fixed by [AST-2136](https://linear.app/astralcareermatch/issue/AST-2136) (related), not here. This ticket covers only the empty 429 warning detail.

## As-is

When a batch stops on an exhausted OpenRouter 429 (AST-2010), the dispatcher's one-line warning prints an empty detail:

```
WARNING src.core.dispatcher: somerset | dispatch company prefilter_company
  LLM provider rate limit: still 429 after retries ()
  The batch is stopping
```

`_note_provider_rate_limit_outage` (`src/core/dispatcher.py`) logs `result.get("error")`. But the result it receives is a consult/roster **summary**, not the raw LLM result. Both `_outage_tag` helpers, in `src/core/roster.py` and `src/core/consult.py`, forward only `failure_class` and `total_held` to the dispatcher, and they drop `error`. So the real provider text (`qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream…`, host Parasail) never reaches the warning. The same gap applies to the failed-probe warning (`_note_provider_probe_outage`, AST-2098), which reads `error` from the same tagged summary.

## To-be

The 429 batch-stop warning (and the failed-probe warning) shows the provider's error text inside the parentheses, the same text the `llm_compat` WARNING already logged for that call. Routing, retry counts and stop behavior are unchanged.

## Proposed steps

1. Have both `_outage_tag` helpers also carry the result's `error` string when they tag a rate-limit or probe outage, so the dispatcher's existing `result.get("error")` gets a value.
2. Leave `_note_provider_rate_limit_outage` / `_note_provider_probe_outage` as they are. They already print `error`; they were just handed an empty one.
3. Check the summary-merge sites (`_consult_chunk` sums only the summary's own counter keys; consult's `{**_fail(...), **_outage_tag(...)}`) so the extra string key doesn't break counter arithmetic or overwrite a different error.

## Component scope

* `src/core/roster.py` (modified): `_outage_tag` drops `error` when it lifts a rate-limit/probe outage to the dispatcher. This is the path the prefilter_company batches in this log took.
* `src/core/consult.py` (modified): `_outage_tag` (same helper, consult side) drops `error` the same way for consult/grade batches.

## Technical scope

* `src/core/roster.py`: modify function `_outage_tag` so a tagged outage also carries the result's error text. No new tables or fields.
* `src/core/consult.py`: modify function `_outage_tag`, same change, so consult-side outages report their detail too. No new tables or fields.

## Ancestor candidates

- [ ] AST-2010: OpenRouter 429 retry and batch error on exhausted rate limit (`docs/features/agent/ast-1877-model-server-catalog-compat-client.md` § Bug: AST-2010). Added `_note_provider_rate_limit_outage` and the `failure_class` lift that loses `error`.
- [ ] AST-2098: hold the batch on a failed host probe (`docs/features/foundation/ast-1959-per-batch-probe-and-host-lock-on-the-openrouter-path.md` § Bug: AST-2098). Extended `_outage_tag` to probe failures (`total_held`); same empty-detail gap.

## Original report

Debug flag was false

```
[2026-10-12 05:57:32] INFO src.core.dispatcher: somerset | dispatch company starting prefilter_company — 78 available (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.1s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.5s
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.4s stop=end_turn tokens in=9626 out=114
[2026-10-12 05:57:32] INFO src.core.roster: intersystems_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.2s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.2s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.7s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.7s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.9s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.5s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.1s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.1s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.5s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.6s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.7s
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.2s stop=end_turn tokens in=2972 out=143
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.0s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.0s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.2s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.5s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.3s
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.1s stop=end_turn tokens in=2880 out=146
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.0s
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.1s stop=end_turn tokens in=1147 out=140
[2026-10-12 05:57:32] INFO src.core.roster: pdhi_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.2s
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.5s stop=end_turn tokens in=3140 out=152
[2026-10-12 05:57:32] INFO src.core.roster: hsc_unm_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.7s
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 7.3s
[2026-10-12 05:57:32] INFO src.core.roster: trustplatform_sg | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.1s stop=end_turn tokens in=1834 out=147
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.7s stop=end_turn tokens in=3541 out=149
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.7s stop=end_turn tokens in=2454 out=152
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.2s stop=end_turn tokens in=4150 out=140
[2026-10-12 05:57:32] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.5s stop=end_turn tokens in=2260 out=144
[2026-10-12 05:57:32] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 11.1s
[2026-10-12 05:57:32] INFO src.core.roster: womenscollegehospital_ca | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:57:32] INFO src.core.roster: chartspan_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:57:32] INFO src.core.roster: bestpracticesoftware_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:57:32] INFO src.core.roster: hhccareers_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 14.2s
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 13.1s stop=end_turn tokens in=2066 out=120
[2026-10-12 05:58:15] INFO src.core.roster: ntracts_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] INFO src.core.roster: careers_bixal_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 17.3s stop=end_turn tokens in=5106 out=120
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.3s stop=end_turn tokens in=5134 out=58
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.9s stop=end_turn tokens in=4643 out=126
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 15.0s stop=end_turn tokens in=5825 out=143
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.8s stop=end_turn tokens in=3392 out=141
[2026-10-12 05:58:15] INFO src.core.roster: careers_microsoft_com_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] INFO src.core.roster: xurrent_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] INFO src.core.roster: d300_org | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 26.4s
[2026-10-12 05:58:15] INFO src.core.roster: clickhouse_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 21.5s stop=end_turn tokens in=2884 out=146
[2026-10-12 05:58:15] INFO src.core.roster: precisionformedicine_com | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] WARNING src.core.roster: precisionformedicine_com -> HOMEPAGE_READY_RETRY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 05:58:15] INFO src.core.roster: faspsych_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 25.0s stop=end_turn tokens in=4756 out=150
[2026-10-12 05:58:15] INFO src.core.roster: paubox_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] INFO src.core.roster: advancedmd_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 31.7s stop=end_turn tokens in=3789 out=149
[2026-10-12 05:58:15] INFO src.core.roster: legendbiotech_com_2 | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:58:15] WARNING src.core.roster: legendbiotech_com_2 -> HOMEPAGE_READY_RETRY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 05:58:15] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 52.9s stop=end_turn tokens in=5706 out=116
[2026-10-12 05:58:15] INFO src.core.roster: fidelity_com_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:02] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 5.1s stop=end_turn tokens in=4450 out=137
[2026-10-12 05:59:02] INFO src.core.roster: 3m_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.2s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 4.0s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 2.0s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.9s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 2.0s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.2s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.7s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.2s
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.0s stop=end_turn tokens in=4753 out=146
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.8s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.9s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.6s
[2026-10-12 05:59:24] INFO src.core.roster: enlightlab_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.3s stop=end_turn tokens in=3647 out=146
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.7s stop=end_turn tokens in=9054 out=162
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.5s stop=end_turn tokens in=4254 out=146
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.3s stop=end_turn tokens in=2991 out=153
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.7s stop=end_turn tokens in=4363 out=117
[2026-10-12 05:59:24] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.7s
[2026-10-12 05:59:24] INFO src.core.roster: element34_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:24] INFO src.core.roster: iqvia_com_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:24] INFO src.core.roster: gomohealth_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:24] INFO src.core.roster: blog_bluebin_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:24] INFO src.core.roster: blackduck_com | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.9s stop=end_turn tokens in=2478 out=145
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.3s stop=end_turn tokens in=1668 out=148
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.3s stop=end_turn tokens in=2644 out=163
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 10.8s stop=end_turn tokens in=7058 out=141
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 16.0s stop=end_turn tokens in=2317 out=155
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.0s stop=end_turn tokens in=6280 out=114
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 10.9s stop=end_turn tokens in=3543 out=148
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 10.9s stop=end_turn tokens in=5328 out=154
[2026-10-12 05:59:24] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 13.7s stop=end_turn tokens in=4501 out=152
[2026-10-12 05:59:30] INFO src.core.roster: codespaceinfotech_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:30] INFO src.core.roster: jobs_bd_com_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:30] INFO src.core.roster: nsightcare_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:30] INFO src.core.roster: fortunesoftit_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:30] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 19.5s stop=end_turn tokens in=654 out=150
[2026-10-12 05:59:30] INFO src.core.roster: alterahealth_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 05:59:30] INFO src.core.roster: events_mountsinaihealth_org | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 21.6s stop=end_turn tokens in=1905 out=149
[2026-10-12 06:00:33] INFO src.core.roster: ats_rippling_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] INFO src.core.roster: kent_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] INFO src.core.roster: nethealth_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 24.1s stop=end_turn tokens in=4822 out=143
[2026-10-12 06:00:33] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 24.6s stop=end_turn tokens in=8453 out=124
[2026-10-12 06:00:33] INFO src.core.roster: jobsjhpiego_icims_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] INFO src.core.roster: marybridge_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] INFO src.core.roster: familiestogetheroc_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] INFO src.core.roster: emorahealth_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 3.4s stop=end_turn tokens in=851 out=71
[2026-10-12 06:00:33] INFO src.core.roster: reliasource_net | company state: HOMEPAGE_READY_RETRY -> ERROR_PREFILTER_COMPANY (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:33] ERROR src.core.roster: reliasource_net -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.9s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.2s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.9s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.9s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.0s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.5s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.0s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.3s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.2s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.6s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.6s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.5s
[2026-10-12 06:00:33] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.7s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.9s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.8s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.6s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.9s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 7.8s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.4s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.0s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.7s
[2026-10-12 06:00:49] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 4.0s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.9s
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.7s stop=end_turn tokens in=517 out=125
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.0s
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 9.0s stop=end_turn tokens in=5821 out=151
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.1s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 7.9s
[2026-10-12 06:00:50] INFO src.core.roster: civilservicejobs_service_gov_uk | company state: HOMEPAGE_READY_RETRY -> PREFILTER_FAILED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.8s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 10.1s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.2s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 6.5s
[2026-10-12 06:00:50] INFO src.core.roster: business_att_com | company state: HOMEPAGE_READY_RETRY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.2s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.4s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.7s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.9s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.9s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 13.1s
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.4s stop=end_turn tokens in=4134 out=157
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 9.9s
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 10.5s stop=end_turn tokens in=1860 out=152
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 10.7s
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 13.0s
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.1s stop=end_turn tokens in=3182 out=149
[2026-10-12 06:00:50] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 14.8s
[2026-10-12 06:00:50] INFO src.core.roster: lacare_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:50] INFO src.core.roster: topconhealthcare_eu | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.9s stop=end_turn tokens in=486 out=70
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 13.8s stop=end_turn tokens in=17513 out=129
[2026-10-12 06:00:50] INFO src.core.roster: gethealthy_uams_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:50] WARNING src.core.agent: prefilter_company skipped — Agent failure: Unable to access the homepage content for index 000 (alvarezandmarsal_com) due to 'Access Denied' error. Cannot evaluate any rubric vectors based on unavailable content.
  This hop is not persisting a success RESPONSE
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 16.6s stop=end_turn tokens in=3528 out=140
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.6s stop=end_turn tokens in=4079 out=157
[2026-10-12 06:00:50] INFO src.core.roster: alvarezandmarsal_com | company state: HOMEPAGE_READY -> ERROR_PREFILTER_COMPANY (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:50] ERROR src.core.roster: alvarezandmarsal_com -> ERROR_PREFILTER_COMPANY [do_task: Agent failure: Unable to access the homepage content for index 000 (alvarezandmarsal_com) due to 'Access Denied' error. Cannot evaluate any rubric vectors based on unavailable content.]
[2026-10-12 06:00:50] INFO src.core.roster: hospitalsmagazine_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.1s stop=end_turn tokens in=2289 out=146
[2026-10-12 06:00:50] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.5s stop=end_turn tokens in=2083 out=147
[2026-10-12 06:00:50] INFO src.core.roster: uhs_com | company state: HOMEPAGE_READY_RETRY -> ERROR_PREFILTER_COMPANY (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:00:50] ERROR src.core.roster: uhs_com -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 06:00:50] INFO src.core.roster: smmcnj_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.8s stop=end_turn tokens in=3277 out=146
[2026-10-12 06:01:04] INFO src.core.roster: publichealth_pitt_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 22.0s stop=end_turn tokens in=2977 out=141
[2026-10-12 06:01:04] INFO src.core.roster: pmcky_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] INFO src.core.roster: mercy_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 28.7s stop=end_turn tokens in=510 out=134
[2026-10-12 06:01:04] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 18.4s
[2026-10-12 06:01:04] INFO src.core.roster: healthmeasures_net | company state: HOMEPAGE_READY_RETRY -> ERROR_PREFILTER_COMPANY (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] ERROR src.core.roster: healthmeasures_net -> ERROR_PREFILTER_COMPANY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 06:01:04] INFO src.core.roster: joinrs_com | company state: HOMEPAGE_READY_RETRY -> PREFILTER_FAILED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 31.8s
[2026-10-12 06:01:04] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 27.9s stop=end_turn tokens in=8913 out=146
[2026-10-12 06:01:04] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 30.7s stop=end_turn tokens in=4100 out=113
[2026-10-12 06:01:04] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 29.4s stop=end_turn tokens in=2348 out=156
[2026-10-12 06:01:04] INFO src.core.roster: ideagen_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] INFO src.core.roster: clinii_com | company state: HOMEPAGE_READY_RETRY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] INFO src.core.roster: adventisthealthcare_com | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:04] WARNING src.core.roster: adventisthealthcare_com -> HOMEPAGE_READY_RETRY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 06:01:31] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 46.1s stop=end_turn tokens in=1335 out=73
[2026-10-12 06:01:31] INFO src.core.roster: idndirectory_com | company state: HOMEPAGE_READY_RETRY -> PREFILTER_PASSED (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:31] WARNING src.external.llm_compat: LLM openrouter task=prefilter_company 58.5s error=Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'Provider returned error', 'error_type': 'rate_limit_exceeded'}, 'request_id': 'gen-1791784890-Dh5gPPderjtGCMdoRHvU', 'metadata': {'raw': 'qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Parasail', 'is_byok': False, 'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider routing: https://openrouter.ai/docs/features/provider-routing'}}
[2026-10-12 06:01:31] INFO src.core.roster: eclinicalworks_com | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-8b73b41b-2557-481a-9d8d-e725156e984c)
[2026-10-12 06:01:31] WARNING src.core.roster: eclinicalworks_com -> HOMEPAGE_READY_RETRY [do_task: Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'Provider returned error', 'error_type': 'rate_limit_exceeded'}, 'request_id': 'gen-1791784890-Dh5gPPderjtGCMdoRHvU', 'metadata': {'raw': 'qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Parasail', 'is_byok': False, 'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider routing: https://openrouter.ai/docs/features/provider-routing'}}]
[2026-10-12 06:01:31] WARNING src.core.dispatcher: somerset | dispatch company prefilter_company
  LLM provider rate limit: still 429 after retries ()
  The batch is stopping
```

```
[2026-10-12 05:36:55] INFO src.core.dispatcher: somerset | dispatch company starting prefilter_company — 132 available (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.5s stop=end_turn tokens in=7964 out=151
[2026-10-12 05:36:55] INFO src.core.roster: careers_zurich_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.6s
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.5s
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.7s
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 4.0s
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.1s stop=end_turn tokens in=8113 out=139
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.1s
[2026-10-12 05:36:55] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.1s
[2026-10-12 05:36:55] INFO src.core.roster: desmoinesregister_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 9.4s stop=end_turn tokens in=4369 out=143
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 5.2s stop=end_turn tokens in=1484 out=116
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 4.7s stop=end_turn tokens in=461 out=58
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.7s stop=end_turn tokens in=6235 out=140
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.1s stop=end_turn tokens in=3882 out=109
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.6s stop=end_turn tokens in=1326 out=141
[2026-10-12 05:36:55] INFO src.core.roster: jobs_siemens_com_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: va_gov | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: moffitt_org | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: bmc_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: tn_gov_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: hshs_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.0s stop=end_turn tokens in=2349 out=139
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 13.1s stop=end_turn tokens in=2961 out=146
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 13.8s stop=end_turn tokens in=7120 out=141
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.6s stop=end_turn tokens in=1003 out=133
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.7s stop=end_turn tokens in=2951 out=144
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.5s stop=end_turn tokens in=4691 out=141
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.9s stop=end_turn tokens in=4655 out=142
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 12.8s stop=end_turn tokens in=1610 out=145
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.0s stop=end_turn tokens in=2340 out=143
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.2s stop=end_turn tokens in=3467 out=145
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.6s stop=end_turn tokens in=9507 out=158
[2026-10-12 05:36:55] INFO src.core.roster: frontiersin_org_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: healthcareittoday_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: nestle_com_2 | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: mrocorp_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: sknhealth_online | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.core.roster: crosscountry_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:36:55] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 25.7s stop=end_turn tokens in=7223 out=159
[2026-10-12 05:36:55] INFO src.core.roster: 24x7mag_com | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:37:42] INFO src.core.roster: softangeles_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:37:42] INFO src.core.roster: chartis_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:37:42] INFO src.core.roster: pronixhealth_com | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:37:42] WARNING src.core.roster: pronixhealth_com -> HOMEPAGE_READY_RETRY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 05:37:42] INFO src.core.roster: intellivon_com_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:37:42] INFO src.core.roster: jobs_boeing_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:37:42] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.5s stop=end_turn tokens in=4220 out=148
[2026-10-12 05:37:42] INFO src.core.roster: amentum_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.2s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.0s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.9s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.4s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.1s
[2026-10-12 05:38:02] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 2.4s stop=end_turn tokens in=468 out=58
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.8s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.6s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.0s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 2.0s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.3s
[2026-10-12 05:38:02] INFO src.core.roster: browse_welch_jhmi_edu | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.4s
[2026-10-12 05:38:02] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 4.6s stop=end_turn tokens in=2001 out=105
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.9s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.4s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.8s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 6.9s
[2026-10-12 05:38:02] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.7s stop=end_turn tokens in=3279 out=152
[2026-10-12 05:38:02] INFO src.core.roster: remotejobs_org_2 | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:02] WARNING src.core.roster: remotejobs_org_2 -> HOMEPAGE_READY_RETRY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 05:38:02] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.2s stop=end_turn tokens in=2253 out=144
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 6.0s
[2026-10-12 05:38:02] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.1s stop=end_turn tokens in=4809 out=145
[2026-10-12 05:38:02] INFO src.core.roster: samsara_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.9s
[2026-10-12 05:38:02] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 7.2s
[2026-10-12 05:38:18] INFO src.core.roster: copehealthsolutions_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.2s
[2026-10-12 05:38:18] INFO src.core.roster: aspph_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.0s stop=end_turn tokens in=4022 out=145
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 7.5s stop=end_turn tokens in=3637 out=148
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.2s stop=end_turn tokens in=4288 out=146
[2026-10-12 05:38:18] INFO src.core.roster: linear_health | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] INFO src.core.roster: slack_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] INFO src.core.roster: jobs_insightpartners_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 10.9s
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.3s stop=end_turn tokens in=1317 out=142
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.3s stop=end_turn tokens in=3981 out=147
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 13.9s stop=end_turn tokens in=473 out=134
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.4s stop=end_turn tokens in=6565 out=149
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 11.4s stop=end_turn tokens in=5501 out=142
[2026-10-12 05:38:18] INFO src.core.roster: careers_redpoint_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] INFO src.core.roster: careers_quantumscape_com | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] INFO src.core.roster: jobs_ashbyhq_com_3 | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 20.8s stop=end_turn tokens in=400 out=128
[2026-10-12 05:38:18] INFO src.core.roster: aha_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] INFO src.core.roster: pasadena_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 22.6s stop=end_turn tokens in=6338 out=124
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 21.4s stop=end_turn tokens in=4313 out=150
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 20.1s stop=end_turn tokens in=3185 out=154
[2026-10-12 05:38:18] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 20.8s stop=end_turn tokens in=2463 out=149
[2026-10-12 05:38:53] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 22.5s
[2026-10-12 05:38:53] INFO src.core.roster: simple_health | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:53] INFO src.core.roster: relias_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:53] INFO src.core.roster: nchimss_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:53] INFO src.core.roster: jobs_firstcitizens_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:53] INFO src.core.roster: ouva_co | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:53] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 51.0s stop=end_turn tokens in=3092 out=149
[2026-10-12 05:38:53] INFO src.core.roster: python_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:38:53] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 05:39:02] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 2.4s
[2026-10-12 05:39:02] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 8.0s
[2026-10-12 05:39:38] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 16.3s stop=end_turn tokens in=1121 out=70
[2026-10-12 05:39:39] WARNING src.core.roster: logicplanet_com -> HOMEPAGE_READY_RETRY [decode: IncompleteGradeSetError: _render_score: missing vectors ['Staffing Agency or Outsourcing Shop']]
[2026-10-12 05:39:39] INFO src.core.roster: logicplanet_com | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:03] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 4.0s stop=end_turn tokens in=3540 out=72
[2026-10-12 05:40:03] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 6.3s stop=end_turn tokens in=4563 out=114
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.3s
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.8s
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.7s
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.0s
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.2s
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.0s
[2026-10-12 05:40:03] INFO src.core.roster: journals_plos_org | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.7s
[2026-10-12 05:40:03] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.9s
[2026-10-12 05:40:03] INFO src.core.roster: cigna_wd5_myworkdayjobs_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:07] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.7s
[2026-10-12 05:40:07] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.1s
[2026-10-12 05:40:07] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.2s
[2026-10-12 05:40:07] WARNING src.external.llm_compat: openrouter 429; retry 1/5 in 1.4s
[2026-10-12 05:40:07] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.4s
[2026-10-12 05:40:07] WARNING src.external.llm_compat: openrouter 429; retry 2/5 in 3.3s
[2026-10-12 05:40:07] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 4.0s stop=end_turn tokens in=653 out=76
[2026-10-12 05:40:07] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 9.1s stop=end_turn tokens in=3110 out=141
[2026-10-12 05:40:07] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.6s stop=end_turn tokens in=10762 out=138
[2026-10-12 05:40:07] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 4.9s
[2026-10-12 05:40:07] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 6.6s
[2026-10-12 05:40:14] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 5.5s
[2026-10-12 05:40:14] INFO src.core.roster: spinwheelio_applytojob_com | company state: HOMEPAGE_READY -> ERROR_PREFILTER_COMPANY_NO_JOBLIST_LINKS (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:14] INFO src.core.roster: medinsight_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:14] WARNING src.external.llm_compat: openrouter 429; retry 3/5 in 6.6s
[2026-10-12 05:40:14] INFO src.core.roster: play_google_com_3 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:14] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.2s stop=end_turn tokens in=616 out=138
[2026-10-12 05:40:14] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.2s stop=end_turn tokens in=4279 out=119
[2026-10-12 05:40:14] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.2s stop=end_turn tokens in=2691 out=146
[2026-10-12 05:40:14] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 8.2s stop=end_turn tokens in=3874 out=142
[2026-10-12 05:40:14] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 9.5s stop=end_turn tokens in=1248 out=152
[2026-10-12 05:40:14] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 12.1s
[2026-10-12 05:40:14] INFO src.core.roster: ca_indeed_com_3 | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:14] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 14.8s
[2026-10-12 05:40:14] INFO src.core.roster: netsafesolutions_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:21] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.0s stop=end_turn tokens in=1652 out=124
[2026-10-12 05:40:21] WARNING src.external.llm_compat: openrouter 429; retry 4/5 in 10.6s
[2026-10-12 05:40:21] INFO src.core.roster: jobs_massdigitalhealth_org | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:21] WARNING src.core.roster: jobs_massdigitalhealth_org -> HOMEPAGE_READY_RETRY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 05:40:21] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.0s stop=end_turn tokens in=1420 out=156
[2026-10-12 05:40:21] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 14.0s stop=end_turn tokens in=2757 out=151
[2026-10-12 05:40:21] INFO src.core.roster: uchealth_org | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:21] WARNING src.core.roster: uchealth_org -> HOMEPAGE_READY_RETRY [hydrate: No rubric criterion matching vector 'JO']
[2026-10-12 05:40:21] INFO src.core.roster: careers_amtrak_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:21] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 15.4s stop=end_turn tokens in=2181 out=146
[2026-10-12 05:40:21] INFO src.core.roster: careers_onpay_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:21] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 18.8s stop=end_turn tokens in=4614 out=154
[2026-10-12 05:40:21] INFO src.core.roster: careers_agfa_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:21] INFO src.core.roster: careers_ford_com_2 | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:43] INFO src.core.roster: cloudflare_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:43] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 21.0s stop=end_turn tokens in=402 out=134
[2026-10-12 05:40:43] INFO src.core.roster: accesstelecare_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:43] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 18.8s
[2026-10-12 05:40:43] INFO src.core.roster: formula5_com | company state: HOMEPAGE_READY -> PREFILTER_FAILED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:43] WARNING src.external.llm_compat: openrouter 429; retry 5/5 in 30.5s
[2026-10-12 05:40:43] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 32.0s stop=end_turn tokens in=3040 out=146
[2026-10-12 05:40:43] INFO src.core.roster: ttuhscep_edu | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:40:52] INFO src.external.llm_compat: LLM openrouter host=Parasail task=prefilter_company 45.9s stop=end_turn tokens in=1975 out=114
[2026-10-12 05:40:52] INFO src.core.roster: tildavps_com | company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:41:00] WARNING src.external.llm_compat: LLM openrouter task=prefilter_company 57.9s error=Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'Provider returned error', 'error_type': 'rate_limit_exceeded'}, 'request_id': 'gen-1791783659-whYmJzsRVHnlrT6u9g0q', 'metadata': {'raw': 'qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Parasail', 'is_byok': False, 'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider routing: https://openrouter.ai/docs/features/provider-routing'}}
[2026-10-12 05:41:00] INFO src.core.roster: remote_com_3 | company state: HOMEPAGE_READY -> HOMEPAGE_READY_RETRY (batch: prefilter_company-94a8a1f3-6386-4c49-b260-46c1579a8e5f)
[2026-10-12 05:41:00] WARNING src.core.roster: remote_com_3 -> HOMEPAGE_READY_RETRY [do_task: Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'Provider returned error', 'error_type': 'rate_limit_exceeded'}, 'request_id': 'gen-1791783659-whYmJzsRVHnlrT6u9g0q', 'metadata': {'raw': 'qwen/qwen3-235b-a22b-2507 is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations', 'provider_name': 'Parasail', 'is_byok': False, 'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider routing: https://openrouter.ai/docs/features/provider-routing'}}]
[2026-10-12 05:41:00] WARNING src.core.dispatcher: somerset | dispatch company prefilter_company
  LLM provider rate limit: still 429 after retries ()
  The batch is stopping
```

### Comments

#### chuckles — 2026-10-12T14:42:50.426Z
Project was unset; assigned **Astral Dispatcher** (same project as AST-2136 and the AST-2010 429 work).

Narrowed per option 2, with one scope correction. The empty `()` isn't a `dispatcher.py` bug: the warning already prints `result["error"]`. Both `_outage_tag` helpers (`src/core/roster.py`, `src/core/consult.py`) drop `error` when they hand the outage to the dispatcher. Component and Technical scope now name those two helpers instead of `dispatcher.py`.

#### susan — 2026-10-12T14:40:56.168Z
2 please.

#### chuckles — 2026-10-12T14:39:56.386Z
@susan I stopped before dispatching anything. [AST-2136](https://linear.app/astralcareermatch/issue/AST-2136) is this same bug: `JOB:<n>` gets decoded as vector `JO` in `_decode_payload`, the deferred item from AST-1828. It was filed a few minutes earlier and is already In Progress as its own mini-epic. Its fix child [AST-2138](https://linear.app/astralcareermatch/issue/AST-2138) is with Hedy on `ftr/AST-2136-job-link-prefix-decode`. If I start a second ftr and fix child on the same function, we pay for the same fix twice and get a merge conflict in `src/core/agent.py`.

AST-2136's scope already covers everything this ticket asks for on the decode side, and it adds the matching guard in `_should_decode_as_encoded_line`. The only thing here that it doesn't cover is optional step 3: the empty `()` in the AST-2010 429 warning in `src/core/dispatcher.py`.

How do you want it handled? Reply and reassign to me:
1. Mark this a Duplicate of AST-2136 and drop the `()` log nit.
2. Keep this ticket, but narrow it to the `()` 429 log fix in `src/core/dispatcher.py` only, link it as related to AST-2136, and run it as a small separate fix.
3. Something else.

No git refs, child tickets, or spawns were created.

---

_Implementation detail may live in git history on `origin/dev`._
