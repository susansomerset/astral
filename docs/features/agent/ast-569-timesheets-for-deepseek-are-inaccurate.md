# AST-569 — Timesheets for deepseek are inaccurate

<!-- linear-archive: AST-569 archived 2026-06-15 -->

## Linear archive (AST-569)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-569/timesheets-for-deepseek-are-inaccurate  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan needs trustworthy spend numbers for DeepSeek-backed agent calls. Agent Timesheets and Execution History must reconcile with DeepSeek's usage export: token counts and daily dollar totals must match exactly; per-request costs must use enough precision that row-level sums are trustworthy (minor per-row rounding is acceptable). Astral already stores granular token buckets and calc_cost components (AST-324 / AST-494) and records DeepSeek completions in the same shape as Anthropic (AST-493). The gap is DeepSeek cost fidelity — wrong rate buckets, Anthropic-shaped usage mapping, or stale pricing — not missing rows for the UTC 2026-06-03 pro sample (the fifth pro request in the export is explained by Pacific-evening vs UTC-day grouping).

## Functional scope

* Align DEEPSEEK_MODEL_PRICING with DeepSeek published rates for deepseek-v4-pro and deepseek-v4-flash, using cache hit, cache miss, and output billing categories as DeepSeek reports them (not only Anthropic cache read / fresh input / output).
* Map each DeepSeek API usage response into agent_timesheets token columns and calc_cost components so per agent_req_id row totals reflect vendor charges at stored precision.
* Reconcile at two grains: per agent_req_id (tokens exact; cost components as granular as storage allows) and per UTC calendar day per model (token totals and dollar totals exact vs DeepSeek export for the astral-somerset key).
* Backfill: recompute token columns and calc_cost\_\* for all existing DeepSeek provider rows, not forward-only.
* Downstream parity: Admin Agent Timesheets (UI + CSV) and Execution History batch cost use the same corrected stored components.
* Anthropic provider rows and cost math unchanged; regression coverage on anthropic paths.

## Boundaries

* Does not change brain-tier to model routing (AST-492 / AST-493) or add multi-vendor UI beyond cost accuracy.
* Does not redesign agent_timesheets schema (AST-494).
* Does not re-open AST-324 Anthropic console reconciliation except to avoid regressions.
* No React debug logging requirements (AST-538 backend only).
* Pricing stays [config.py](<http://config.py>) literals for non-secret rates.

## Acceptance criteria

1. For UTC 2026-06-03 and deepseek-v4-pro: summed cache-hit, cache-miss, and output token counts across all Astral agent_timesheets rows for that model and date equal the DeepSeek export line amounts exactly.
2. For the same scope: sum of calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output equals the DeepSeek export dollar total for that model and date exactly.
3. For UTC 2026-06-03 and deepseek-v4-flash: same exact token and dollar reconciliation against the export.
4. Every agent_req_id row in the Original brief CSV (and full UTC-day export scope): stored token columns match the vendor usage attributable to that request exactly; per-row cost components use maximum practical precision with only acceptable minor rounding on the four calc_cost fields.
5. Backfill completes for all historical agent_timesheets rows where provider is deepseek; recomputed values persist in place.
6. DEEPSEEK_MODEL_PRICING matches DeepSeek published pricing at ship (snapshot date noted in plan).
7. Admin Agent Timesheets and CSV row totals equal the sum of stored calc_cost\_\* for sampled DeepSeek rows after backfill.
8. Timesheet and cost-calculator tests pass; DeepSeek reconciliation tests added without weakening Anthropic cases.

## Dependencies and blockers

* AST-493 (DeepSeek client + timesheet recording) — Done.
* AST-494 (unified agent_timesheets + admin API) — Done.
* None blocking start.

## Open questions

None.

---

## Original brief

Timesheets for 4 transactions on '2026-06-03' were estimated to cost a total $0.15.

```
agent_req_id,created_at,candidate_id,batch_id,task_key_uuid,model_code,batch_size,cache_write_tokens,cache_read_tokens,no_cache_prompt_tokens,no_cache_live_tokens,total_no_cache_input_tokens,total_output_tokens,calc_cost_cache_write,calc_cost_cache_read,calc_cost_no_cache_input,calc_cost_output,agent_performance,failure_note
840f7662-a5de-44cd-ac2e-09fade0aca81,2026-06-03 14:09:41,somerset,draft_job_resume-f017d456-6ccb-4f90-82cc-364e1ec92c9f,48e5e443-26ba-416f-a8e0-d39b3e56797c,deepseek-v4-pro,1,0,21504,776,0,4090,10779,0.0,0.000311808,0.0071166,0.03751092,OK,
701e9c6c-63e3-4f68-967c-9163363e0e96,2026-06-03 14:06:43,somerset,advise_job_resume-f2e843e6-2993-41ff-a608-36398980fddf,77ac0379-1b69-4137-817e-7a2281f68b71,deepseek-v4-pro,1,0,20480,983,0,3070,4908,0.0,0.00029696000000000003,0.0053418,0.01707984,success,
e5c87f27-f2d9-4235-9c15-ca79c91da8c1,2026-06-03 14:04:33,somerset,contemplate_job-d59d2546-5305-427e-85aa-fe8595f9b375,bb6e0afa-0a6a-4b31-8dca-9b585d4c76ce,deepseek-v4-pro,1,0,12416,967,0,10152,2294,0.0,0.000180032,0.01766448,0.00798312,success,
702e0e09-f576-4923-8ddf-3a4eaba106f3,2026-06-03 14:03:28,somerset,anticipate_scan-5b4c3f8d-e2a2-4d39-abfc-d5223cd3133c,08d89fc1-d053-4476-b6da-7129d5ecbc24,deepseek-v4-pro,1,0,0,1185,0,21753,5466,0.0,0.0,0.037850220000000004,0.019021680000000003,success,
f778a6ce-b336-4e62-878d-7d1f82b347fa,2026-06-03 01:32:58,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,36,0.0,3.584e-07,9.380000000000002e-06,1.0080000000000002e-05,success,
941d2570-11f7-429a-b91d-f6b459066f80,2026-06-03 01:32:57,,,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,57,0.0,3.584e-07,9.380000000000002e-06,1.5960000000000003e-05,success,
6f6d120b-91fa-4f5f-8720-14dd0304285d,2026-06-03 01:32:56,,,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,93,0.0,3.584e-07,9.380000000000002e-06,2.604e-05,success,
def18a37-7287-42c9-b2f0-596ad9485288,2026-06-03 01:32:54,,,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,90,0.0,3.584e-07,9.380000000000002e-06,2.5200000000000003e-05,success,
179e54c9-a113-42e4-b942-7885b983bad4,2026-06-03 01:32:52,,,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,18,0.0,3.584e-07,9.380000000000002e-06,5.040000000000001e-06,success,
a14ad827-d1ec-4871-a4ea-c98a171c216d,2026-06-03 01:32:51,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,43,0.0,3.584e-07,9.380000000000002e-06,1.2040000000000002e-05,success,
9119cd1d-2506-47d4-a298-7334d8276b43,2026-06-03 01:32:50,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,43,0.0,3.584e-07,9.380000000000002e-06,1.2040000000000002e-05,success,
6a94a089-1077-4d21-87c9-397ebded67b9,2026-06-03 01:32:49,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,83,0.0,3.584e-07,9.380000000000002e-06,2.324e-05,success,
63f9278c-8421-43a9-bfd7-0a8cb0da6e58,2026-06-03 01:32:47,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,79,0.0,3.584e-07,9.380000000000002e-06,2.212e-05,success,
2eed0caa-b69d-4c2a-9a79-81970aa78307,2026-06-03 01:32:46,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,37,0.0,3.584e-07,9.380000000000002e-06,1.036e-05,success,
67861128-8ed5-45d3-9346-236f8180e841,2026-06-03 01:32:44,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,36,0.0,3.584e-07,9.380000000000002e-06,1.0080000000000002e-05,success,
64fc0bdd-467c-45ee-a0bb-5270229e571e,2026-06-03 01:32:43,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,43,0.0,3.584e-07,9.380000000000002e-06,1.2040000000000002e-05,success,
2c34e350-fe30-4c75-ad9f-548ebd6db81a,2026-06-03 01:32:42,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,70,0.0,3.584e-07,9.380000000000002e-06,1.96e-05,success,
91436f2e-f946-44c0-9d2b-d67ee462ca01,2026-06-03 01:32:40,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,67,0.0,3.584e-07,9.380000000000002e-06,1.8760000000000003e-05,success,
0965fc7e-01a7-4fe7-a246-ad1fac074326,2026-06-03 01:32:39,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,100,0.0,3.584e-07,9.380000000000002e-06,2.8000000000000003e-05,success,
9a03d4c9-87a7-4f66-ba03-1fea3a5a4a18,2026-06-03 01:32:37,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,72,0.0,3.584e-07,9.380000000000002e-06,2.0160000000000003e-05,success,
652c1fe9-76f7-4658-b6e9-dbb89e2b386c,2026-06-03 01:32:36,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,42,0.0,3.584e-07,9.380000000000002e-06,1.1760000000000001e-05,success,
75c7f18a-3f86-40c8-bf7e-1484aa6ad55e,2026-06-03 01:32:35,,,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,61,0.0,3.584e-07,9.380000000000002e-06,1.7080000000000002e-05,success,
6c22b00c-905d-47a9-922a-3e46ecf7f3e3,2026-06-03 01:32:33,,,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,18,0.0,3.584e-07,9.380000000000002e-06,5.040000000000001e-06,success,
4a747b65-8cc1-485a-b7ad-442da1878878,2026-06-03 01:32:32,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,61,0.0,3.584e-07,9.380000000000002e-06,1.7080000000000002e-05,success,
94e687aa-e556-49fc-b612-4a7a72b403e9,2026-06-03 01:32:31,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,55,0.0,3.584e-07,9.380000000000002e-06,1.54e-05,success,
1c6b180f-7b65-44e0-b917-16264c72021c,2026-06-03 01:32:30,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,36,0.0,3.584e-07,9.380000000000002e-06,1.0080000000000002e-05,success,
2cd7982e-5a4e-4310-8df1-9094255b030e,2026-06-03 01:32:29,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,18,0.0,3.584e-07,9.380000000000002e-06,5.040000000000001e-06,success,
2ae885bf-f3ba-49a9-a03f-bc074fea6b13,2026-06-03 01:32:28,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,79,0.0,3.584e-07,9.380000000000002e-06,2.212e-05,success,
613f49c8-78ff-4c14-bc3e-83c3a3e6c104,2026-06-03 01:32:26,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,36,0.0,3.584e-07,9.380000000000002e-06,1.0080000000000002e-05,success,
d7883bd9-7489-4f30-bb60-7d712df7f265,2026-06-03 01:32:25,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,41,0.0,3.584e-07,9.380000000000002e-06,1.1480000000000002e-05,success,
6624d9cd-7309-4721-866b-4a7cd4e5f94d,2026-06-03 01:32:24,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,38,0.0,3.584e-07,9.380000000000002e-06,1.0640000000000001e-05,success,
b317615f-a891-4bbb-9fad-c8e51f70263a,2026-06-03 01:32:22,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,43,0.0,3.584e-07,9.380000000000002e-06,1.2040000000000002e-05,success,
e9210119-72ab-4cc1-ba0c-39ee3dd56156,2026-06-03 01:32:21,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,81,0.0,3.584e-07,9.380000000000002e-06,2.2680000000000003e-05,success,
48b66edd-e31c-4422-837a-abcd2655b030,2026-06-03 01:32:20,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,69,0.0,3.584e-07,9.380000000000002e-06,1.932e-05,success,
d7d86c05-d6cf-4617-9f0f-7b6b4f21dfb3,2026-06-03 01:32:18,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,79,0.0,3.584e-07,9.380000000000002e-06,2.212e-05,success,
c2fca0ef-8821-49e2-8cd0-6ec4b0999600,2026-06-03 01:32:17,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,36,0.0,3.584e-07,9.380000000000002e-06,1.0080000000000002e-05,success,
06b283e2-dd49-4a88-89ca-d8a38f2ae0ff,2026-06-03 01:32:15,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,79,0.0,3.584e-07,9.380000000000002e-06,2.212e-05,success,
46d356e6-a7b7-4728-a704-2431de18b446,2026-06-03 01:32:14,,,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,36,0.0,3.584e-07,9.380000000000002e-06,1.0080000000000002e-05,success,
c258c1cc-424d-433e-ad67-3e8fe64bee8a,2026-06-03 01:32:13,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,86,0.0,3.584e-07,9.380000000000002e-06,2.4080000000000003e-05,success,
6b4fdda8-821f-4430-8e37-fbf03b672abe,2026-06-03 01:32:11,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,74,0.0,3.584e-07,9.380000000000002e-06,2.072e-05,success,
37322c21-8157-41d2-b1b8-c6cf3e548ba0,2026-06-03 01:32:10,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,79,0.0,3.584e-07,9.380000000000002e-06,2.212e-05,success,
0d267707-f0fd-4706-8ee3-d217276a70c4,2026-06-03 01:32:08,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,66,0.0,3.584e-07,9.380000000000002e-06,1.8480000000000003e-05,success,
5c553bde-8ab1-4987-8558-4bc51be52f43,2026-06-03 01:32:07,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,90,0.0,3.584e-07,9.380000000000002e-06,2.5200000000000003e-05,success,
e34c7cdc-449e-4956-8d23-ac127b52675d,2026-06-03 01:32:06,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,81,0.0,3.584e-07,9.380000000000002e-06,2.2680000000000003e-05,success,
48b64586-10fa-47e8-9d7e-465f5f053d86,2026-06-03 01:32:04,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,58,0.0,3.584e-07,9.380000000000002e-06,1.624e-05,success,
b7431930-59a1-4eda-b471-939a7c052c38,2026-06-03 01:32:03,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,100,0.0,3.584e-07,9.380000000000002e-06,2.8000000000000003e-05,success,
f3b729e4-15bb-41ac-a08e-1b6f180105d4,2026-06-03 01:32:02,,,uuid-1,deepseek-v4-flash,1,0,0,2,0,195,36,0.0,0.0,2.7300000000000003e-05,1.0080000000000002e-05,success,
72736a9a-6513-4899-bc4e-56690ba20e91,2026-06-03 01:32:00,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,66,0.0,3.584e-07,9.380000000000002e-06,1.8480000000000003e-05,success,
a5c99ee4-dad5-4782-9d8c-8b6660a60d79,2026-06-03 01:31:59,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,18,0.0,3.584e-07,9.380000000000002e-06,5.040000000000001e-06,success,
31820bab-222d-4e65-bb18-2803f87bcbfc,2026-06-03 01:31:58,,batch-1,uuid-1,deepseek-v4-pro,1,0,0,2,0,274,100,0.0,0.0,0.00047676,0.000348,failure,API response content block missing text attribute
b1f3c2f9-af44-4228-8e87-2170928392b4,2026-06-03 01:31:55,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,72,0.0,3.584e-07,9.380000000000002e-06,2.0160000000000003e-05,success,
e4e6380d-6433-4362-a5b6-759b409900b7,2026-06-03 01:31:54,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,62,0.0,3.584e-07,9.380000000000002e-06,1.7360000000000003e-05,success,
659d37c1-16c2-4202-803f-90acc8b0ee7a,2026-06-03 01:31:52,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,41,0.0,3.584e-07,9.380000000000002e-06,1.1480000000000002e-05,success,
fba2bc1e-15f0-4253-be0d-a2c19a9cdfb1,2026-06-03 01:31:50,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,66,0.0,3.584e-07,9.380000000000002e-06,1.8480000000000003e-05,success,
d8b7b22d-98c3-4586-bb9d-35004f986c10,2026-06-03 01:31:49,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,34,0.0,3.584e-07,9.380000000000002e-06,9.52e-06,success,
61ee7440-fae2-468f-99bd-1e661c817775,2026-06-03 01:31:47,,batch-1,uuid-1,deepseek-v4-flash,2,0,128,2,0,67,49,0.0,3.584e-07,9.380000000000002e-06,1.372e-05,success,
358965e2-9a61-4105-b38e-0b900e648446,2026-06-03 01:31:46,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,33,0.0,3.584e-07,9.380000000000002e-06,9.240000000000001e-06,success,
186ebc62-3412-4d36-a5d2-f841e1c5c7dc,2026-06-03 01:31:45,,batch-1,uuid-1,deepseek-v4-flash,1,0,128,2,0,67,50,0.0,3.584e-07,9.380000000000002e-06,1.4000000000000001e-05,success,
fcd4eda6-cfcb-467b-bc6a-89d76052f855,2026-06-03 01:31:44,,batch-1,uuid-1,deepseek-v4-flash,1,0,0,2,0,195,66,0.0,0.0,2.7300000000000003e-05,1.8480000000000003e-05,success,
```

Deepseek's usage platform says otherwise:

```
user_id,utc_date,model,api_key_name,api_key,type,price,amount
8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8,2026-06-03,deepseek-v4-pro,astral-somerset,sk-b6d90***********************52b1,output_tokens,0.00000087,23547
8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8,2026-06-03,deepseek-v4-pro,astral-somerset,sk-b6d90***********************52b1,request_count,,5
8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8,2026-06-03,deepseek-v4-pro,astral-somerset,sk-b6d90***********************52b1,input_cache_hit_tokens,0.000000003625,54400
8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8,2026-06-03,deepseek-v4-pro,astral-somerset,sk-b6d90***********************52b1,input_cache_miss_tokens,0.000000435,39339
8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8,2026-06-03,deepseek-v4-flash,astral-somerset,sk-b6d90***********************52b1,output_tokens,0.00000028,3102
8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8,2026-06-03,deepseek-v4-flash,astral-somerset,sk-b6d90***********************52b1,request_count,,54
8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8,2026-06-03,deepseek-v4-flash,astral-somerset,sk-b6d90***********************52b1,input_cache_hit_tokens,0.0000000028,6656
8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8,2026-06-03,deepseek-v4-flash,astral-somerset,sk-b6d90***********************52b1,input_cache_miss_tokens,0.00000014,3874
```

### Comments

#### susan — 2026-06-05T19:54:21.111Z
@chuckles Oh geez, I saw the cost on the usage spreadsheet and misunderstood it as a subtotal.  We're good.  Setting to PR-ready.

#### chuckles — 2026-06-05T19:15:04.260Z
@susan — **datt paused** (not a merge/git block). Your 06/04 UAT thread is answered in the comment above: stored `calc_cost_*` for those two rows sums to **$0.018264345**, matching DeepSeek export rates × your token totals (22431 miss + 9778 output). **AST-580** is filed if we still need a code fix.

**Need one reply** so we know whether to run bug pipeline or close as triage:
- Paste the **DeepSeek dashboard daily $** for 2026-06-04 pro if it ≠ $0.018264345, **or**
- Paste **Admin → $ Total** for `a811f41e…` / `b2904570…` if UI ≠ stored sum, **or**
- Say **"math OK, close AST-580"** if the JSON you pasted was the full check.

Feature children **570/571** stay **User Testing**; no regression.

— Chuckles

#### chuckles — 2026-06-05T19:13:26.987Z
[check-linear] @susan — UAT 2026-06-04 cost triage (parent **In Progress**; **AST-580** Bug filed; AST-570/571 stay **User Testing**).

**Your sample reconciles on stored math.** For the two `deepseek-v4-pro` rows you pasted:

| Check | Value |
|-------|-------|
| Σ `total_no_cache_input_tokens` | 22431 (= export `input_cache_miss_tokens`) |
| Σ `total_output_tokens` | 9778 (= export `output_tokens`) |
| Σ four `calc_cost_*` | **$0.018264345** |
| Export-priced (22431×$0.435/M + 9778×$0.87/M) | **$0.018264345** |

Per-row stored `calc_cost_no_cache_input` / `calc_cost_output` match `calculate_cost_components_deepseek_from_counts` in `src/utils/cost_calculator.py` using `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]` in `src/utils/config.py` (cpm_input **0.435**, cpm_output **0.87**).

**Likely confusion surface:** `no_cache_live_tokens` + `no_cache_prompt_tokens` (e.g. 13868+828=14696) ≠ `total_no_cache_input_tokens` (11356). Cost is billed on **vendor cache-miss** (`total_no_cache_input_tokens` / `usage.input_tokens` at record time in `src/external/deepseek.py`) — not on char-estimate live+prompt columns.

**Need from you:** which dollar total is wrong?
1. DeepSeek dashboard **daily $** for 2026-06-04 (paste the $ line if different from $0.018264345)
2. Admin **Agent Timesheets → $ Total** for those `agent_req_id`s
3. A manual calc you expected (formula + result)

**Refs:** `origin/ftr/ast-569-timesheets-deepseek-cost` @ `d9656be9` · local `dev` @ `5b96f9db` · Joan `bae3ad87-8192-493e-9129-cf664a9afad5` · children **2** (AST-570, AST-571) + bug **AST-580**.

#### susan — 2026-06-05T19:11:24.528Z
Still an issue.  The tokens are 100% correct, but the cost is incorrect:

From DeepSeek for transactions on 06/04:

| **8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8** | 2026-06-04 | deepseek-v4-pro | astral-somerset | sk-b6d90\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*52b1 | output_tokens | 0.00000087 | 9778 |
| -- | -- | -- | -- | -- | -- | -- | -- |
| **8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8** | 2026-06-04 | deepseek-v4-pro | astral-somerset | sk-b6d90\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*52b1 | request_count |  | 2 |
| **8ff3052b-a0a5-486b-ab3c-ac93fc98cbd8** | 2026-06-04 | deepseek-v4-pro | astral-somerset | sk-b6d90\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*52b1 | input_cache_miss_tokens | 0.000000435 | 22431 |

From our agent_timesheets table:

```
[
  {
    "agent_performance": "success",
    "agent_req_id": "a811f41e-617c-406d-876f-20e501852217",
    "batch_id": "analysis_upshot-17686698-b1f3-4d64-8915-801bac4af087",
    "batch_size": 1,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0,
    "calc_cost_cache_read": 0,
    "calc_cost_cache_write": 0,
    "calc_cost_no_cache_input": 0.00493986,
    "calc_cost_output": 0.00456228,
    "candidate_id": "somerset",
    "created_at": "2026-06-04 01:16:58",
    "failure_note": null,
    "model_code": "deepseek-v4-pro",
    "no_cache_live_tokens": 13868,
    "no_cache_prompt_tokens": 828,
    "task_key_uuid": "56d8eca2-6105-40e3-a391-f444d8134e46",
    "total_no_cache_input_tokens": 11356,
    "total_output_tokens": 5244
  },
  {
    "agent_performance": "success",
    "agent_req_id": "b2904570-f064-4a14-b16b-ef06c2159a99",
    "batch_id": "analysis_upshot-17686698-b1f3-4d64-8915-801bac4af087",
    "batch_size": 1,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0,
    "calc_cost_cache_read": 0,
    "calc_cost_cache_write": 0,
    "calc_cost_no_cache_input": 0.004817625,
    "calc_cost_output": 0.00394458,
    "candidate_id": "somerset",
    "created_at": "2026-06-04 01:18:47",
    "failure_note": null,
    "model_code": "deepseek-v4-pro",
    "no_cache_live_tokens": 11721,
    "no_cache_prompt_tokens": 828,
    "task_key_uuid": "56d8eca2-6105-40e3-a391-f444d8134e46",
    "total_no_cache_input_tokens": 11075,
    "total_output_tokens": 4534
  }
]
```

#### chuckles — 2026-06-03T19:27:19.484Z
## Manual test steps

**Prereq:** Restart app if running; use DB with DeepSeek timesheet rows (shared `data/`).

### AST-570 — backend cost fidelity
1. Run documented backfill / reconciliation from `docs/features/agent/ast-570-deepseek-cost-math-mapping-backfill.md` (UTC-day reconcile vs DeepSeek export).
2. For **UTC 2026-06-03** **deepseek-v4-pro**: summed cache-hit, cache-miss, output tokens across all `agent_timesheets` rows = DeepSeek export line amounts exactly.
3. Same date/model: sum of four `calc_cost_*` fields = export dollar total exactly.
4. Repeat 2–3 for **deepseek-v4-flash**.
5. Spot-check parent brief rows (e.g. `840f7662-a5de-44cd-ac2e-09fade0aca81`): per-row tokens and four cost components match vendor usage.

### AST-571 — Admin display parity
6. **Admin → Agent Timesheets:** **$ Total** column on DeepSeek rows equals sum of four `calc_cost_*` (compare to CSV components for same `agent_req_id`).
7. **Export CSV:** `total_cost` column present; row values match UI **$ Total**.
8. **Execution History:** batch cost rollups match summed timesheet costs for a sampled DeepSeek batch.

`origin/ftr/ast-569-timesheets-deepseek-cost` @ `d9656be9` · local `dev` merged @ `408ca97f`. Restart app if running.

Reset: `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-06-03T19:04:44.257Z
@susan — Read all comments on AST-569 / AST-570 / AST-571. Your **OQ's answered!** matches the parent Description (**Open questions: None**; both grains, exact tokens/dollars, full backfill, fifth pro request = UTC vs Pacific). No open product questions on the parent.

Active thread is **AST-570** `[qa-handoff]` (regression manifest pins Anthropic path while `active_provider` is deepseek) — Betty clearing per check-linear §5b, then orchestration resumes (test-astral → review → resolve → rollup → prep-uat). Not treating that as a parent blocker.

— Chuckles

#### chuckles — 2026-06-03T18:50:17.168Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-569 (parent) | ftr/ast-569-timesheets-deepseek-cost |
| AST-570 | sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill |
| AST-571 | sub/AST-569/AST-571-admin-timesheet-cost-display |

AST-571 blockedBy AST-570.

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | bae3ad87-8192-493e-9129-cf664a9afad5 | AST-569 (parent) | git |
| Ada | fa7ca645-c6ab-4c07-92b9-0e7e3b287a51 | AST-570 | engineer |
| Betty | 22747cf7-74a9-4628-9d96-7c7cbd93288b | AST-570 | qa |
| Radia | e3e917ea-3486-4a48-aa0e-76498a9e35cd | AST-570 | review |
| Katherine | 6d8b336b-2d1e-4bdc-8653-0af0f0040c6d | AST-571 | engineer |
| Betty | 74714d53-cc12-4cf1-aa78-f335c84933f3 | AST-571 | qa |
| Radia | 843845a3-404f-46f6-9909-6e144fac5c5c | AST-571 | review |

**Parent:** AST-569

— Chuckles

#### susan — 2026-06-03T18:47:24.136Z
OQ's answered!

#### chuckles — 2026-06-03T18:28:52.168Z
@susan — open questions on AST-569 (numbered in Description):

1. Reconciliation target: per `agent_req_id` row, daily aggregate per model, or both? (Your brief: four rows vs full-day export with five pro requests + flash.)
2. Acceptable delta vs DeepSeek export ($ or %)?
3. Backfill existing DeepSeek timesheet rows or forward-only fix?
4. In scope to find the missing fifth `deepseek-v4-pro` request on 2026-06-03, or math on stored rows only?

---

_Implementation detail may live in git history on `origin/dev`._
