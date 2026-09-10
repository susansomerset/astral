# AST-569 — Timesheets for deepseek are inaccurate

**Component:** agent  
**Children:** AST-570, AST-571, AST-580  
**Linear archived:** AST-569 2026-06-15; AST-570 2026-06-15; AST-571 2026-06-15; AST-580 2026-06-15

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-06-15 11:19 | AST-569 | docs | `688dddfa1` | archive Linear issue content |

## Epic — AST-569

_Archived: 2026-06-15 · Linear URL: https://linear.app/astralcareermatch/issue/AST-569/timesheets-for-deepseek-are-inaccurate · Status at archive: Done · Project: Astral Agent · Assignee: chuckles · Priority / estimate: High / —_

### Purpose

Susan needs trustworthy spend numbers for DeepSeek-backed agent calls. Agent Timesheets and Execution History must reconcile with DeepSeek's usage export: token counts and daily dollar totals must match exactly; per-request costs must use enough precision that row-level sums are trustworthy (minor per-row rounding is acceptable). Astral already stores granular token buckets and calc_cost components (AST-324 / AST-494) and records DeepSeek completions in the same shape as Anthropic (AST-493). The gap is DeepSeek cost fidelity — wrong rate buckets, Anthropic-shaped usage mapping, or stale pricing — not missing rows for the UTC 2026-06-03 pro sample (the fifth pro request in the export is explained by Pacific-evening vs UTC-day grouping).

### Functional scope

* Align DEEPSEEK_MODEL_PRICING with DeepSeek published rates for deepseek-v4-pro and deepseek-v4-flash, using cache hit, cache miss, and output billing categories as DeepSeek reports them (not only Anthropic cache read / fresh input / output).
* Map each DeepSeek API usage response into agent_timesheets token columns and calc_cost components so per agent_req_id row totals reflect vendor charges at stored precision.
* Reconcile at two grains: per agent_req_id (tokens exact; cost components as granular as storage allows) and per UTC calendar day per model (token totals and dollar totals exact vs DeepSeek export for the astral-somerset key).
* Backfill: recompute token columns and calc_cost\_\* for all existing DeepSeek provider rows, not forward-only.
* Downstream parity: Admin Agent Timesheets (UI + CSV) and Execution History batch cost use the same corrected stored components.
* Anthropic provider rows and cost math unchanged; regression coverage on anthropic paths.

### Boundaries

* Does not change brain-tier to model routing (AST-492 / AST-493) or add multi-vendor UI beyond cost accuracy.
* Does not redesign agent_timesheets schema (AST-494).
* Does not re-open AST-324 Anthropic console reconciliation except to avoid regressions.
* No React debug logging requirements (AST-538 backend only).
* Pricing stays [config.py](<http://config.py>) literals for non-secret rates.

### Acceptance criteria

1. For UTC 2026-06-03 and deepseek-v4-pro: summed cache-hit, cache-miss, and output token counts across all Astral agent_timesheets rows for that model and date equal the DeepSeek export line amounts exactly.
2. For the same scope: sum of calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output equals the DeepSeek export dollar total for that model and date exactly.
3. For UTC 2026-06-03 and deepseek-v4-flash: same exact token and dollar reconciliation against the export.
4. Every agent_req_id row in the Original brief CSV (and full UTC-day export scope): stored token columns match the vendor usage attributable to that request exactly; per-row cost components use maximum practical precision with only acceptable minor rounding on the four calc_cost fields.
5. Backfill completes for all historical agent_timesheets rows where provider is deepseek; recomputed values persist in place.
6. DEEPSEEK_MODEL_PRICING matches DeepSeek published pricing at ship (snapshot date noted in plan).
7. Admin Agent Timesheets and CSV row totals equal the sum of stored calc_cost\_\* for sampled DeepSeek rows after backfill.
8. Timesheet and cost-calculator tests pass; DeepSeek reconciliation tests added without weakening Anthropic cases.

### Dependencies and blockers

* AST-493 (DeepSeek client + timesheet recording) — Done.
* AST-494 (unified agent_timesheets + admin API) — Done.
* None blocking start.

### Open questions

None.

---

### Original brief

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

#### Comments


##### susan — 2026-06-05T19:54:21.111Z

@chuckles Oh geez, I saw the cost on the usage spreadsheet and misunderstood it as a subtotal.  We're good.  Setting to PR-ready.

##### chuckles — 2026-06-05T19:15:04.260Z

@susan — **datt paused** (not a merge/git block). Your 06/04 UAT thread is answered in the comment above: stored `calc_cost_*` for those two rows sums to **$0.018264345**, matching DeepSeek export rates × your token totals (22431 miss + 9778 output). **AST-580** is filed if we still need a code fix.

**Need one reply** so we know whether to run bug pipeline or close as triage:
- Paste the **DeepSeek dashboard daily $** for 2026-06-04 pro if it ≠ $0.018264345, **or**
- Paste **Admin → $ Total** for `a811f41e…` / `b2904570…` if UI ≠ stored sum, **or**
- Say **"math OK, close AST-580"** if the JSON you pasted was the full check.

Feature children **570/571** stay **User Testing**; no regression.

##### chuckles — 2026-06-05T19:13:26.987Z

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

##### susan — 2026-06-05T19:11:24.528Z

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

### Manual test steps

**Prereq:** Restart app if running; use DB with DeepSeek timesheet rows (shared `data/`).

#### AST-570 — backend cost fidelity

1. Run documented backfill / reconciliation from `agent-ast-569-timesheets-for-deepseek-are-inaccurate.md#ast-570--deepseek-cost-math-mapping-and-backfill` (UTC-day reconcile vs DeepSeek export).
2. For **UTC 2026-06-03** **deepseek-v4-pro**: summed cache-hit, cache-miss, output tokens across all `agent_timesheets` rows = DeepSeek export line amounts exactly.
3. Same date/model: sum of four `calc_cost_*` fields = export dollar total exactly.
4. Repeat 2–3 for **deepseek-v4-flash**.
5. Spot-check parent brief rows (e.g. `840f7662-a5de-44cd-ac2e-09fade0aca81`): per-row tokens and four cost components match vendor usage.

#### AST-571 — Admin display parity

6. **Admin → Agent Timesheets:** **$ Total** column on DeepSeek rows equals sum of four `calc_cost_*` (compare to CSV components for same `agent_req_id`).
7. **Export CSV:** `total_cost` column present; row values match UI **$ Total**.
8. **Execution History:** batch cost rollups match summed timesheet costs for a sampled DeepSeek batch.

`origin/ftr/ast-569-timesheets-deepseek-cost` @ `d9656be9` · local `dev` merged @ `408ca97f`. Restart app if running.

Reset: `git reset --hard origin/dev`

##### chuckles — 2026-06-03T19:04:44.257Z

@susan — Read all comments on AST-569 / AST-570 / AST-571. Your **OQ's answered!** matches the parent Description (**Open questions: None**; both grains, exact tokens/dollars, full backfill, fifth pro request = UTC vs Pacific). No open product questions on the parent.

Active thread is **AST-570** `[qa-handoff]` (regression manifest pins Anthropic path while `active_provider` is deepseek) — Betty clearing per check-linear §5b, then orchestration resumes (test-astral → review → resolve → rollup → prep-uat). Not treating that as a parent blocker.

### Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

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

##### susan — 2026-06-03T18:47:24.136Z

OQ's answered!

##### chuckles — 2026-06-03T18:28:52.168Z

@susan — open questions on AST-569 (numbered in Description):

1. Reconciliation target: per `agent_req_id` row, daily aggregate per model, or both? (Your brief: four rows vs full-day export with five pro requests + flash.)
2. Acceptable delta vs DeepSeek export ($ or %)?
3. Backfill existing DeepSeek timesheet rows or forward-only fix?
4. In scope to find the missing fifth `deepseek-v4-pro` request on 2026-06-03, or math on stored rows only?

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-570 — DeepSeek cost math, mapping, and backfill

_Archived: 2026-06-15 · Linear URL: https://linear.app/astralcareermatch/issue/AST-570/deepseek-cost-math-mapping-and-backfill-timesheets-for-deepseek-are · Status at archive: Done · Project: Astral Agent · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-569; blocks: AST-571_

#### What this implements

Correct DeepSeek timesheet cost fidelity end-to-end in the backend: vendor-aligned DEEPSEEK_MODEL_PRICING (cache hit, cache miss, output), map DeepSeek API usage into agent_timesheets token columns and calc_cost\_\* components, recompute all historical rows where provider is deepseek, and provide a repeatable UTC-day reconciliation check against DeepSeek usage export. Anthropic provider math and rows must not change.

#### Acceptance criteria

1. For UTC 2026-06-03 and deepseek-v4-pro: summed cache-hit, cache-miss, and output token counts across all Astral agent_timesheets rows for that model and date equal the DeepSeek export line amounts exactly.
2. For the same scope: sum of calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output equals the DeepSeek export dollar total for that model and date exactly.
3. For UTC 2026-06-03 and deepseek-v4-flash: same exact token and dollar reconciliation against the export.
4. Every agent_req_id row in the parent Original brief CSV (and full UTC-day export scope): stored token columns match the vendor usage attributable to that request exactly; per-row cost components use maximum practical precision with only acceptable minor rounding on the four calc_cost fields.
5. Backfill completes for all historical agent_timesheets rows where provider is deepseek; recomputed values persist in place.
6. DEEPSEEK_MODEL_PRICING matches DeepSeek published pricing at ship (snapshot date noted in plan).
7. Timesheet and cost-calculator tests pass; DeepSeek reconciliation tests added without weakening Anthropic cases.

#### Boundaries

* Does not change Admin Agent Timesheets React page or CSV column wiring (sibling Katherine ticket).
* Does not change brain-tier routing (AST-492/493).
* Does not redesign agent_timesheets schema (AST-494).

#### Notes for planning

Primary surfaces: src/utils/config.py, src/utils/cost_calculator.py, src/external/deepseek.py, src/core/timesheets.py, src/data/database.py backfill path. Document DeepSeek cache-hit/miss/output mapping in plan. Reconciliation script or documented procedure for Susan UAT.

##### Comments


###### radia — 2026-06-03T19:09:05.860Z

**Diff:** `origin/dev...origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` (tip `96aebe5e`). **Review doc:** `agent-ast-569-timesheets-for-deepseek-are-inaccurate.md#ast-570--deepseek-cost-math-mapping-and-backfill` (Radia § Review).

**fix-now:** none — product matches approved plan Stages 1–3; Betty tests green on publish ref.

**discuss**
- **UAT ops:** Stage 4 `debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py` not on publish ref (gitignored). Parent AC **1–3** still need Susan to run `backfill_deepseek_agent_timesheet_costs()` then UTC-day reconcile; post exact commands on this ticket when green.
- **Tests vs plan:** `test_cost_calculator_deepseek.py` uses UTC-day aggregate export totals, not per-row `840f7662…` / `f778a6ce…` anchors from plan Stage 5 — math is sound, per-`agent_req_id` proof weaker.
- **Backfill scope:** pass 1 updates `calc_cost_*` only from stored token ints. If reconcile FAILs on miss/output **integers**, need documented pass 2 within **AST-570** (plan Stage 4).

**advisory**
- `src/external/deepseek.py` — pre-existing `[DEBUG]` `logger.info` when `debug=True` (grandfather §1.5.1).
- `docs/ASTRAL_TEST_BIBLE.md` — **§7.13zz** correct; extra §7.13* rollup lines are sibling Betty publish noise.

**Recommended:** `resolve-astral` only if reconcile fails or Susan wants optional per-row golden tests; otherwise proceed to UAT after backfill + reconcile.

###### betty — 2026-06-03T19:06:24.775Z

[check-linear] Tests Ready — [qa-handoff] cleared: pinned `get_active_llm_provider` → anthropic + `send_to_deepseek` stub on `test_send_to_anthropic_receives_resolved_key_for_big_tier`; bible §7.13zz narrowed §7.13ze regression nodes. Manifest items 1+2 green on `dev-betty`. Publish `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` @ `96aebe5e`. Assignee Ada for `test-astral`.

###### ada — 2026-06-03T19:03:05.846Z

[qa-handoff]

**Regression item 2** (§7.13ze narrowed scope per bible): manifest command
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/data/database/test_timesheets.py \
  tests/component/core/test_timesheets.py
```

**Item 1 (AST-570 manifest):** 7/7 passed on `dev-ada` after merge `origin/dev` → `origin/ftr/ast-569-timesheets-deepseek-cost` → `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` (publish @ `34c9c54f`).

**Item 2 failure (test/manifest, not product):**

`tests/component/core/test_agent.py::TestAst492BrainSettingDoTask::test_send_to_anthropic_receives_resolved_key_for_big_tier`

- Mocks `send_to_anthropic` only; does **not** pin `get_active_llm_provider` (sibling `test_send_to_deepseek_receives_vendor_model_and_tier_meta` **does** pin `deepseek`).
- `LLM_PROVIDER_CONFIG["active_provider"]` is `"deepseek"` on publish ref → `do_task` calls real `send_to_deepseek`, which fails on Anthropic-shaped `_api_response()` mock: `API response content block missing text attribute`.
- **Not** an AST-570 product regression; DeepSeek cost/backfill tests are green.

**Ask @Betty White:** Either add `monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "anthropic")` (and stub `send_to_deepseek`) to the anthropic-path test, or narrow regression manifest to exclude that case / run only `test_send_to_deepseek_*` + pricing tests. Reassign Ada when manifest is green.

**Note:** Running full `tests/component/utils/test_config.py` (per comment shorthand “brain tiers”) also fails unrelated `TestAst510MiddleNameConfig` — not on integration line; bible narrowed class is `TestAst492LlmBrainTierConfig`.

###### betty — 2026-06-03T19:00:20.211Z

**QA test manifest (AST-570)**

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_cost_calculator_deepseek.py tests/component/data/database/test_timesheets.py::TestBackfillDeepseekAgentTimesheetCosts tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping`
2. **Regression:** §7.13ze — `tests/component/utils/test_config.py` (brain tiers), `tests/component/core/test_agent.py::TestAst492BrainSettingDoTask`, `tests/component/data/database/test_timesheets.py`, `tests/component/core/test_timesheets.py`
3. **Susan UAT (post test-astral green):** `python3 debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py --export-csv <path> --utc-date 2026-06-03` (gitignored spike; not in manifest run)

**Publish:** `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` @ `34c9c54f`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (origin/sub tip):** `be5c164f` — verify with `git show origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill:docs/ASTRAL_TEST_BIBLE.md | shasum -a 256`

###### ada — 2026-06-03T18:52:11.376Z

Plan: `agent-ast-569-timesheets-for-deepseek-are-inaccurate.md#ast-570--deepseek-cost-math-mapping-and-backfill`

https://github.com/susansomerset/astral/blob/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill/docs/features/agent/ast-570-deepseek-cost-math-mapping-backfill.md

Publish: `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` @ `6720c897`

**Self-assessment**
- **Scope:** MAJOR-CHANGE — config pricing, cost_calculator, deepseek recording, database backfill, reconciliation spike.
- **Conf:** high — DeepSeek pricing page + parent export define CPMs and UTC 2026-06-03 reconciliation targets; spike only if `usage.input_tokens` ≠ cache-miss.
- **Risk:** HIGH — Wrong pro rates or miss/hit mapping breaks spend trust; Anthropic path isolated by separate helpers and SQL filter on DeepSeek `model_code` only.

---

#### DeepSeek → ledger mapping (authoritative for this ticket)

DeepSeek bills three input/output categories. Astral keeps the **existing** `agent_timesheets` columns (AST-494); only **semantics** for `provider=deepseek` rows change.

| DeepSeek export `type` | Stored column | Source on API usage (Anthropic-compat Messages API) | `calc_cost_*` key |
|------------------------|---------------|-----------------------------------------------------|-------------------|
| `input_cache_hit_tokens` | `cache_read_tokens` | `usage.cache_read_input_tokens` (0 if missing) | `calc_cost_cache_read` ← `cpm_cache_read` |
| `input_cache_miss_tokens` | `total_no_cache_input_tokens` | `usage.input_tokens` (must equal vendor **cache miss** count, not “fresh after breakpoint” unless docs prove identical) | `calc_cost_no_cache_input` ← `cpm_input` |
| `output_tokens` | `total_output_tokens` | `usage.output_tokens` | `calc_cost_output` ← `cpm_output` |
| *(not billed)* | `cache_write_tokens` | always **0** | `calc_cost_cache_write` always **0.0** |

**Unchanged diagnostic columns (not used in dollar reconciliation):** `no_cache_prompt_tokens`, `no_cache_live_tokens` — keep populating from char estimates in `agent.py` / `send_to_deepseek` kwargs; do **not** add them to export reconciliation sums.

⚠️ **Decision:** Reuse Anthropic-shaped column names so **AST-571** can sum `calc_cost_*` without schema work; map DeepSeek **miss** into `total_no_cache_input_tokens` and **hit** into `cache_read_tokens`, not into `cache_write_tokens`.

##### UTC 2026-06-03 acceptance anchors (parent Original brief + export)

| Model | Export cache-hit tokens | Export cache-miss tokens | Export output tokens | Export $ total (price × amount sum) |
|-------|-------------------------|--------------------------|----------------------|-------------------------------------|
| `deepseek-v4-pro` | 54,400 | 39,339 | 23,547 | hit `0.1972` + miss `0.017112465` + out `0.02048589` ≈ **$0.2348** |
| `deepseek-v4-flash` | 6,656 | 3,874 | 3,102 | hit `0.0186368` + miss `0.00054236` + out `0.00086856` ≈ **$0.0200** |

Pro row sample: summed `cache_read_tokens` across the four pro rows in the parent CSV equals **54,400** — hit mapping is already correct on stored data. Dollar drift is driven mainly by **wrong `DEEPSEEK_MODEL_PRICING` for `deepseek-v4-pro`** today (`cpm_cache_read` / `cpm_input` / `cpm_output` do not match the export unit prices). After pricing fix, backfill must still prove **miss** and **output** column sums match export for the **full UTC day** (all `agent_req_id` rows in scope, not only the four-row CSV excerpt).

#### Stage 1: Pricing literals and shared cost math

**Done when:** `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]` matches the pricing table (per-1M: hit `3.625`, miss `0.435`, output `0.87`); flash row unchanged; unit tests prove one pro and one flash row match export `price × amount` within `1e-9` per component.

1. In `src/utils/config.py`, inside `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]`, set `cpm_cache_read` to `3.625`, `cpm_input` to `0.435`, `cpm_output` to `0.87`, `cpm_cache_write` to `0.0`. Update the block comment snapshot date to `2026-06-03`.
2. In `src/utils/cost_calculator.py`, add:
```python
def deepseek_usage_to_token_counts(usage) -> dict:
    """Return cache_read, cache_miss, output, cache_write ints for DeepSeek billing."""
```

   - `cache_read` = `getattr(usage, "cache_read_input_tokens", 0) or 0`
   - `cache_miss` = `usage.input_tokens` (document in docstring: DeepSeek compat reports miss here; if Stage 2 spike disproves, stop and comment on **AST-570**)
   - `output` = `usage.output_tokens`
   - `cache_write` = `0`

3. Add `calculate_cost_components_deepseek_from_counts(cache_read, cache_miss, output, cache_write, vendor_model)` returning the same four `calc_cost_*` keys using `DEEPSEEK_MODEL_PRICING`.
4. Change `calculate_cost_components_deepseek(usage, vendor_model)` to call steps 2–3 only (no duplicate formulas).

#### Stage 2: Live recording path (`send_to_deepseek`)

**Done when:** A mocked `messages.create` with usage `{input_tokens: 100, cache_read_input_tokens: 50, output_tokens: 25}` produces `_timesheet_kwargs` with `cache_read_tokens=50`, `total_no_cache_input_tokens=100`, `total_output_tokens=25`, `cache_write_tokens=0`, and `calc_cost_*` matching `calculate_cost_components_deepseek_from_counts`.

1. In `src/external/deepseek.py`, after `usage = response.usage`, call `counts = deepseek_usage_to_token_counts(usage)` and `cost_parts = calculate_cost_components_deepseek_from_counts(...)` (or the usage wrapper).
2. Set `_timesheet_kwargs` fields: `cache_write_tokens=counts["cache_write"]`, `cache_read_tokens=counts["cache_read"]`, `total_no_cache_input_tokens=counts["cache_miss"]`, `total_output_tokens=counts["output"]`; keep `no_cache_prompt_tokens` / `no_cache_live_tokens` from existing kwargs unchanged.
3. Extend `tests/component/external/test_deepseek.py` (or add beside existing mocks) to assert the kwargs passed to `record_timesheet` match the table above.

#### Stage 3: Historical backfill (database)

**Done when:** Running `backfill_deepseek_agent_timesheet_costs()` in a test DB updates every row with `model_code IN ('deepseek-v4-flash','deepseek-v4-pro')` and leaves rows with `model_code` like `claude-sonnet-4-6` unchanged; function is idempotent (second run identical).

1. In `src/data/database.py`, add `backfill_deepseek_agent_timesheet_costs() -> int` (returns rows updated).
2. SQL scope: `SELECT agent_req_id, model_code, cache_write_tokens, cache_read_tokens, total_no_cache_input_tokens, total_output_tokens FROM agent_timesheets WHERE model_code IN (...)` — keys from `DEEPSEEK_MODEL_PRICING`.
3. For each row, compute costs via `calculate_cost_components_deepseek_from_counts` using **stored** token integers (do not alter token columns in this stage unless Stage 4 proves miss integers wrong).
4. `UPDATE agent_timesheets SET calc_cost_cache_write=?, calc_cost_cache_read=?, calc_cost_no_cache_input=?, calc_cost_output=? WHERE agent_req_id=?`.
5. Do **not** write to `anthropic_timesheets` (DeepSeek rows are agent ledger only per AST-494).
6. Export `backfill_deepseek_agent_timesheet_costs` through `src/core/timesheets.py` as `backfill_deepseek_timesheet_costs` only if admin/script entry is needed; otherwise keep DB-only and invoke from reconciliation script step below.

⚠️ **Decision:** Backfill pass 1 recomputes **costs only** from existing token columns. If reconcile script (Stage 4) shows miss token drift, add pass 2 in a follow-up commit within this ticket — do not improvise token rewrites without a documented rule.

#### Stage 4: Reconciliation script (Susan UAT)

**Done when:** Susan can run one command against a copied DeepSeek export CSV and see PASS/FAIL for UTC 2026-06-03 pro and flash token and dollar totals vs `agent_timesheets`.

1. Create `debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py` (gitignored parent per **orientation-astral**).
2. CLI args: `--export-csv PATH`, `--utc-date YYYY-MM-DD`, optional `--db` (default prod path from env if present else test fixture).
3. Parse export rows: group by `model` + `type` (`input_cache_hit_tokens`, `input_cache_miss_tokens`, `output_tokens`).
4. Query SQL: `SELECT model_code, SUM(cache_read_tokens), SUM(total_no_cache_input_tokens), SUM(total_output_tokens), SUM(calc_cost_cache_write+calc_cost_cache_read+calc_cost_no_cache_input+calc_cost_output) FROM agent_timesheets WHERE date(created_at)=? AND model_code IN (...) GROUP BY model_code`.
5. Print side-by-side table; exit code `1` on any token or dollar mismatch (tolerance: costs `1e-6` per component sum, tokens exact integer match).
6. Document in plan comment on **AST-570** after first green run: exact command Susan used.

7. After backfill implementation, add a one-line admin or shell entry in script docstring only — **no** new Flask route unless Susan asks.

#### Stage 5: Tests and bible handoff

**Done when:** `pytest tests/component/utils/test_cost_calculator_deepseek.py tests/component/data/database/test_timesheets.py -q` passes; existing Anthropic cost tests unchanged.

1. Add `tests/component/utils/test_cost_calculator_deepseek.py` with:
   - Pro row `840f7662-a5de-44cd-ac2e-09fade0aca81` token counts from parent CSV → costs matching stored export math at new CPMs.
   - Flash single-row sample `f778a6ce-b336-4e62-878d-7d1f82b347fa`.
   - Assert `calculate_cost_components` (Anthropic) still passes existing tests in `test_cost_calculator.py` if present, or run full utils component folder.
2. Extend `tests/component/data/database/test_timesheets.py`: insert deepseek + anthropic rows, run `backfill_deepseek_agent_timesheet_costs()`, assert deepseek costs changed and anthropic identical.
3. Do **not** weaken `TestAst492BrainSettingDoTask` or Anthropic timesheet tests.

#### Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches config pricing, pure cost math, external client recording, and data-layer backfill across the DeepSeek ledger path.

**Conf:** `high` — Official pricing page and parent export supply exact CPMs and reconciliation targets; remaining risk is confirming `usage.input_tokens` equals cache-miss on live API (Stage 2 test + optional manual smoke).

**Risk:** `HIGH` — Incorrect mapping or pro CPMs regress spend reporting and parent UAT; Anthropic path must stay isolated via separate functions and backfill SQL filter on `model_code`.

#### Self-review vs ASTRAL_CODE_RULES

- **§2.1:** Pricing literals only in `config.py`; snapshot date in comment.
- **§1.3 DRY:** Single `calculate_cost_components_deepseek_from_counts`; no duplicated `/ 1_000_000` math in `deepseek.py` or `database.py`.
- **§3.3:** `cost_calculator` imports only `config`; `deepseek.py` imports `cost_calculator`, not `database`; backfill in `database.py` imports cost helper from utils (allowed: data → utils).
- **§3.6:** Reconciliation script under `debug/spikes/ast-570-deepseek-export-reconcile/`, not repo-root `artifacts/`.
- **§2.4 / state machine:** No dispatch changes.

No `conf-!!-NONE`.

#### Execution contract

- Execute stages in order; one commit per stage on `dev-ada`; Joan `store-code-commit` after each stage commit (build-astral §6).
- If `usage.input_tokens` does not equal export miss for a live `agent_req_id`, stop and post on **AST-570**:
```
🛑 Stage 2 blocked: DeepSeek usage.input_tokens ≠ export cache-miss
Step: Stage 2 — map usage to total_no_cache_input_tokens
Issue: <paste usage dict and export row>
Proposed resolutions: (1) use alternate usage field <name> (2) derive miss as input_total - cache_read (3) need Susan/vendor doc
```

- Do not edit **AST-571** UI files.

#### Review (build)

**Branch:** `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill`
**Tip:** `48321b2ed23c2b2f91772eae9d7e3a71226d94ea` (Joan store-code-commit after stage 3)

**Stages shipped (product):**
1. `DEEPSEEK_MODEL_PRICING` pro CPMs + `deepseek_usage_to_token_counts` / `calculate_cost_components_deepseek_from_counts`
2. `send_to_deepseek` timesheet kwargs via shared mapping (`cache_write_tokens=0`)
3. `backfill_deepseek_agent_timesheet_costs()` in `database.py`

**Susan UAT reconcile (local, gitignored):**
`python3 debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py --export-csv <path> --utc-date 2026-06-03`

**Tests:** Betty at Code Complete (`qa-astral`) per plan Stage 5.

#### Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` (tip `96aebe5e` after tests). **Baseline:** `origin/dev`.

##### What's solid

- **§2.1 / plan Stage 1:** `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]` CPMs (`3.625` / `0.435` / `0.87`) and snapshot comment `2026-06-03`; flash row unchanged.
- **§1.3 DRY:** `deepseek_usage_to_token_counts` + `calculate_cost_components_deepseek_from_counts` shared by `calculate_cost_components_deepseek`, `send_to_deepseek`, and `backfill_deepseek_agent_timesheet_costs`.
- **§3.3:** `cost_calculator` → `config` only; `deepseek.py` → `cost_calculator` only; `database.py` → utils helper (allowed data → utils).
- **Plan Stage 2:** `TestSendToDeepseekTimesheetMapping` pins `cache_read_tokens` / `total_no_cache_input_tokens` / `total_output_tokens` / `cache_write_tokens=0` and matching `calc_cost_*`.
- **Plan Stage 3:** Backfill updates DeepSeek SKU rows by `model_code IN DEEPSEEK_MODEL_PRICING`; anthropic row untouched in `test_recomputes_deepseek_costs_leaves_anthropic_unchanged`.
- **Anthropic isolation:** `TestAnthropicCostComponentsRegression` + `TestAst492BrainSettingDoTask` monkeypatch `get_active_llm_provider` → `anthropic` on the Big-tier regression.
- **Golden math:** `test_pro_utc_day_export_totals_match_pricing_snapshot` / flash counterpart match parent export dollar components at new CPMs.

##### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | Plan Stage 4 / UAT | `debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py` is **not** on the publish ref (gitignored per orientation). Parent AC **1–3** UTC-day token + dollar checks still need Susan to run backfill + reconcile locally; document the exact `backfill_deepseek_agent_timesheet_costs()` invocation (Python one-liner or script) when reconcile is first green. |
| **discuss** | `tests/component/utils/test_cost_calculator_deepseek.py` | Plan Stage 5 asked per-row anchors (`840f7662…`, `f778a6ce…`); shipped tests use **UTC-day aggregate** token totals instead. Math is still anchored to export; weaker per-`agent_req_id` proof before UAT. |
| **discuss** | `backfill_deepseek_agent_timesheet_costs` | Pass 1 recomputes **calc_cost_* only** (per plan). If Stage 4 reconcile shows **miss/output** column drift vs export, need pass 2 within **AST-570** — do not improvise token rewrites without a documented rule. |
| **advisory** | `src/external/deepseek.py` `if debug:` block | Pre-existing `logger.info("[DEBUG] …")` left unchanged — grandfather per **§1.5.1** / **§5f** (file touched but not migrated to contract helpers). |
| **advisory** | `docs/ASTRAL_TEST_BIBLE.md` | **§7.13zz** manifest is correct for **AST-570**; large bible diff includes rollup notes for sibling tickets — expected Betty publish shape for `rollup-child`. |

##### Recommended actions

| Item | Owner | Action |
|------|-------|--------|
| UAT reconcile + backfill command | Ada / Susan | After merge to UAT DB: run `backfill_deepseek_agent_timesheet_costs()`, then gitignored `reconcile.py` (or equivalent SQL) for UTC `2026-06-03` pro + flash; post exact command on **AST-570** when green. |
| Per-row golden tests (optional) | Ada via `resolve-astral` | If Susan wants stronger pre-UAT proof, add tests using parent CSV row token integers for `840f7662…` and `f778a6ce…`. |
| Token pass 2 (conditional) | Ada via `resolve-astral` | Only if reconcile FAIL on miss/output **integers** — follow plan Stage 4 escalation, not cost-only backfill. |

**Verdict:** No **fix-now** on published product code vs approved plan Stages 1–3 and Betty tests. **Review Posted** — engineer may proceed to `resolve-astral` for **discuss** UAT ops only; no code changes required for sign-off unless reconcile fails.

#### Resolution (2026-06-03)

**Review tip:** `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` @ `7fc6b78d` (Radia doc + Betty tests @ `96aebe5e` product).

**Fix-now:** None — no product commits in resolve pass.

**Discuss (closed for sign-off):**

| Item | Resolution |
|------|------------|
| UAT ops | Backfill + reconcile are Susan UAT steps (gitignored spike). Commands below. |
| Per-row golden tests | Deferred — UTC-day aggregate tests in `test_cost_calculator_deepseek.py` match export dollar math; optional per-`agent_req_id` tests only if Susan requests before UAT. |
| Backfill pass 2 | Conditional — run only if reconcile FAIL on miss/output **integers**; pass 1 (cost-only from stored tokens) is shipped. |

**Susan UAT (parent AC 1–3):**
```bash
# 1. Recompute calc_cost_* for all DeepSeek rows (prod DB path from env or --db)
python3 -c "from src.data.database import backfill_deepseek_agent_timesheet_costs; print(backfill_deepseek_agent_timesheet_costs(), 'rows updated')"

# 2. UTC-day reconcile vs DeepSeek export (gitignored spike; copy export CSV locally)
python3 debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py \
  --export-csv /path/to/deepseek_usage.csv \
  --utc-date 2026-06-03
```

If step 2 FAIL on token integers (not dollars only), stop and escalate per plan Stage 4 — do not rewrite token columns without a documented rule.

**§9a:** publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-569-timesheets-deepseek-cost`.

#### Files changed (plan vs actual)  _(no commit trail — plan only)_

| | file | planned | actual |
|---|---|---|---|
| · | `src/utils/config.py` | Correct `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]` to offic | — |
| · | `src/utils/cost_calculator.py` | Add `deepseek_usage_to_token_counts(usage) -> dict`; add `ca | — |
| · | `src/external/deepseek.py` | Build `_timesheet_kwargs` from `deepseek_usage_to_token_coun | — |
| · | `src/data/database.py` | Add `backfill_deepseek_agent_timesheet_costs()` — `UPDATE` a | — |
| · | `debug/spikes/ast-570-deepseek-export-reconcile/reconcile.py` | CLI: load DeepSeek export CSV + query `agent_timesheets` for | — |
| · | `tests/component/utils/test_cost_calculator_deepseek.py` | Golden token→cost cases for both SKUs; pro pricing matches e | — |
| · | `tests/component/data/database/test_timesheets.py` | Backfill updates `calc_cost_*` for seeded deepseek row; anth | — |
| · | `docs/ASTRAL_TEST_BIBLE.md` | §7 entry for AST-570 manifest paths (Betty adds in qa-astral | — |

### AST-571 — Admin timesheet cost display parity

_Archived: 2026-06-15 · Linear URL: https://linear.app/astralcareermatch/issue/AST-571/admin-timesheet-cost-display-parity-timesheets-for-deepseek-are · Status at archive: Done · Project: Astral Agent · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-569_

#### What this implements

After backend DeepSeek cost fix lands on the parent ftr branch, ensure Admin Agent Timesheets (UI + CSV export) and Execution History batch cost rollups display totals that match the sum of stored calc_cost\_\* fields for DeepSeek rows.

#### Acceptance criteria

7. Admin Agent Timesheets and CSV row totals equal the sum of stored calc_cost\_\* for sampled DeepSeek rows after backfill.

#### Boundaries

* Does not change pricing math or backfill (sibling Ada ticket).
* Does not change Anthropic display paths except regression-safe shared helpers.

#### Notes for planning

Likely src/ui/api/api_admin.py, src/ui/frontend/src/pages/AdminAgentTimesheets.tsx, Execution History cost aggregation if separate from timesheet list.

##### Comments


###### radia — 2026-06-03T19:24:19.435Z

**Doc publish:** `agent-ast-569-timesheets-for-deepseek-are-inaccurate.md#ast-571--admin-timesheet-cost-display-parity` § Review (Radia) on `origin/sub/AST-569/AST-571-admin-timesheet-cost-display` @ `656db863` (cherry-pick of `66a778f2` on dev-radia).

###### radia — 2026-06-03T19:23:45.816Z

**Review** — `origin/dev...origin/sub/AST-569/AST-571-admin-timesheet-cost-display` (tip `af32280b`). AST-571-only commits after `merge(AST-570)` @ `8e959c5c`.

**Solid**
- AC 7: `sum_calc_cost_components` + API `_enrich_timesheet_row` on list/export; `timesheetCost.ts` / `rowTotalCost`; `AdminAgentTimesheets` `$ Total` + footer; `BatchAgentDataModal` uses per-row `sumCalcCostComponents` on enriched rows.
- Execution History: `list_dispatch_ledger` + `sum_cost_by_batch` already sum four `calc_cost_*`; comment + `test_ast571_ledger_total_cost_matches_timesheet_sum` document AST-571 parity.
- §3.3: `api_admin` adds only `utils.cost_calculator`; no new UI→data/external.
- §5d: AST-571 slice does not add pricing/backfill beyond sibling merge base.

**discuss**
- `tests/component/core/test_dispatcher.py` — ledger test mocks `0.044939528` while `test_parent_brief_pro_row_840f7662` sums parent literals to `0.044939328` (~2e-7). Not a display bug; optional align in resolve.

**Doc:** `agent-ast-569-timesheets-for-deepseek-are-inaccurate.md#ast-571--admin-timesheet-cost-display-parity` § Review (Radia) — Joan publish pending from `66a778f2`.

###### betty — 2026-06-03T19:18:56.316Z

**Tests Ready** — `origin/sub/AST-569/AST-571-admin-timesheet-cost-display` @ `af32280b`

**Manifest**

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_cost_calculator.py::TestSumCalcCostComponents`
2. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestTimesheets::test_list_and_export_timesheets`
3. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestDispatchWrappers::test_ast571_ledger_total_cost_matches_timesheet_sum`
4. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` — routed page (§6c): **$ Total** column, footer **Cost: $0.1000**, date blur/clear in existing test

**Regression:** §7.13zza regression block (`test_cost_calculator_deepseek.py`, database + core `test_timesheets.py`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `582e2210f1ff3d5b5cb869c1a18cc6af1567ec3bd4e4b5e79de1583983557f2a` — §7.13zza added

**Coverage:** `sum_calc_cost_components`, API `total_cost` enrichment + CSV column, ledger `sum_cost_by_batch` parity, page **$ Total** display.

###### katherine — 2026-06-03T19:12:44.761Z

**Plan:** [agent-ast-569-timesheets-for-deepseek-are-inaccurate.md#ast-571--admin-timesheet-cost-display-parity](https://github.com/susansomerset/astral/blob/sub/AST-569/AST-571-admin-timesheet-cost-display/docs/features/agent/ast-571-admin-timesheet-cost-display-parity.md) on `sub/AST-569/AST-571-admin-timesheet-cost-display` @ `16fb02a0`

**Summary:** Single row-total formula — sum of four stored `calc_cost_*` fields. Python `sum_calc_cost_components` + API enrichment (`total_cost` on list/CSV); frontend `$ Total` column and shared `lib/timesheetCost.ts`; Execution History parity test only (dispatcher already uses `sum_cost_by_batch`). **Pre-build:** merge `origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` on `dev-kath` before implementation (blockedBy).

**Self-assessment**
- **Scope:** Single-Component — admin timesheet/ledger display surfaces plus thin API enrichment; no pricing or schema.
- **Conf:** high — formula is parent AC 7; implementation is DRY wiring and regression tests once AST-570 backfill is on the integration line.
- **Risk:** Medium — spend display trust for admin users; Anthropic paths must stay regression-safe via shared helper tests.

**Git:** `dev-kath` merged `origin/ftr/ast-569-timesheets-deepseek-cost` (bible §7.13zz); merge-clean vs `origin/dev`.

---

#### Authoritative row total (single formula)

For any timesheet row dict (API JSON, CSV enrichment, or TS row):
```
total_cost = calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output
```

Treat missing/`None` as `0.0` before add. Do **not** sum token columns for dollars. Do **not** read `dispatch_ledger.total_cost` column in the DB for display — Execution History already overwrites with `sum_cost_by_batch` (same SQL sum as above).

⚠️ **Decision:** Python owns the canonical helper; API adds `total_cost` on every timesheet payload so CSV and JSON share one enrichment path; frontend uses API `total_cost` when present and falls back to the same four-key sum for tests/mocks.

##### Parent acceptance anchor (AC 7)

For sampled DeepSeek rows after backfill (parent Original brief pro rows, e.g. `840f7662-a5de-44cd-ac2e-09fade0aca81`), UI row total and CSV `total_cost` must equal:

`calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output`

from the API response (within display rounding: four decimal places in UI via existing `formatCell` / `fmtCost`).

#### Pre-build integration (mandatory)

**Done when:** `dev-kath` has merge-clean gate vs `origin/dev` and includes **AST-570** product commits needed for meaningful DeepSeek parity checks.

1. On `dev-kath`: `git fetch origin && git merge origin/dev` (re-check `BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. `git merge origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` (or `origin/ftr/ast-569-timesheets-deepseek-cost` if sibling already rolled up). Resolve conflicts only in files this ticket owns; commit merge on `dev-kath` if needed.
3. `git merge origin/sub/AST-569/AST-571-admin-timesheet-cost-display` before each publish commit (plan already on publish ref after plan-astral).

Do **not** change `src/external/deepseek.py`, `src/utils/config.py` pricing blocks, or `backfill_deepseek_agent_timesheet_costs` except merge conflict resolution that preserves **AST-570** behavior.

#### Stage 1: Shared sum helper (Python)

**Done when:** `sum_calc_cost_components` is importable; unit test proves parent brief row `840f7662-…` total matches sum of four CSV cost fields.

1. In `src/utils/cost_calculator.py`, after existing cost helpers, add:
```python
CALC_COST_KEYS = (
    "calc_cost_cache_write",
    "calc_cost_cache_read",
    "calc_cost_no_cache_input",
    "calc_cost_output",
)

def sum_calc_cost_components(row: dict) -> float:
    """Row total spend from stored calc_cost_* only."""
```

   Implementation: `return sum(float(row.get(k) or 0) for k in CALC_COST_KEYS)`.

2. In `tests/component/utils/test_cost_calculator.py`, add class `TestSumCalcCostComponents`:
   - `test_empty_keys_zero`
   - `test_parent_brief_pro_row_840f7662` using literals from AST-569 description: `0.0`, `0.000311808`, `0.0071166`, `0.03751092` → expect `≈ 0.044939528` (use `pytest.approx`).

#### Stage 2: Admin API enrichment + CSV column

**Done when:** `GET /api/admin/timesheets` and `GET /api/admin/timesheets/export` return each row with `total_cost` equal to `sum_calc_cost_components(row)`; CSV header includes `total_cost` after `calc_cost_output`.

1. In `src/ui/api/api_admin.py`, import `sum_calc_cost_components` from `src.utils.cost_calculator`.
2. Add:
```python
def _enrich_timesheet_row(row: dict) -> dict:
    out = dict(row)
    out["total_cost"] = sum_calc_cost_components(row)
    return out
```

3. In `list_timesheets_all`, after `rows = list_timesheets(...)`, set `rows = [_enrich_timesheet_row(r) for r in rows]` before `req_dict` branch and plain `jsonify`.
4. In `export_timesheets_csv`, same enrichment before `writer.writerows`.
5. Append `"total_cost"` to `_TIMESHEET_CSV_COLUMNS` immediately after `"calc_cost_output"`.
6. Append to `_TIMESHEET_COLUMNS`: `{"key": "total_cost", "label": "Total Cost", "type": "currency"}` after the four component cost columns.
7. In `tests/component/ui/api/test_api_admin.py`, class `TestTimesheets::test_list_and_export_timesheets`:
   - Change mock row to use `agent_req_id` (not `anthropic_req_id`) and non-zero `calc_cost_*`.
   - Assert `plain.get_json()[0]["total_cost"] == pytest.approx(0.1)` when components sum to `0.1`.
   - Assert exported CSV text contains header `total_cost` and data row includes formatted total.

#### Stage 3: Frontend timesheet page + shared TS helper

**Done when:** Agent Timesheets table shows **$ Total** column; footer **Cost:** matches sum of displayed row totals; export unchanged (server CSV already has `total_cost`).

1. Create `src/ui/frontend/src/lib/timesheetCost.ts`:
```typescript
export const CALC_COST_KEYS = [
  "calc_cost_cache_write",
  "calc_cost_cache_read",
  "calc_cost_no_cache_input",
  "calc_cost_output",
] as const

export function sumCalcCostComponents(row: Record<string, unknown>): number {
  return CALC_COST_KEYS.reduce((s, k) => s + (Number(row[k]) || 0), 0)
}

export function rowTotalCost(row: Record<string, unknown>): number {
  const t = row.total_cost
  return typeof t === "number" && !Number.isNaN(t) ? t : sumCalcCostComponents(row)
}
```

2. In `AdminAgentTimesheets.tsx`:
   - Import `rowTotalCost`, `sumCalcCostComponents`.
   - Add interface field `total_cost?: number`.
   - Replace `totalCost(r)` body with `return rowTotalCost(r)`.
   - Insert column after `calc_cost_output`: `{ key: "total_cost", label: "$ Total", type: "currency" }`.
   - In `sum()` reducer, use `rowTotalCost(r)` instead of `totalCost(r)`.
3. In `BatchAgentDataModal.tsx`, import `sumCalcCostComponents`; in `sumTimesheets`, keep per-component accumulators; set `totalCost` line to `rows.reduce((s, r) => s + sumCalcCostComponents(r), 0)` instead of summing four accumulator fields (equivalent but single formula).
4. In `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx`:
   - Add `total_cost: 0.1` to mock row (sum of `0.01+0.02+0.03+0.04`).
   - Assert `screen.getByText("$0.1000")` or matching formatted total in totals bar after load.
   - Assert table header **$ Total** present (`getByRole("columnheader", { name: "$ Total" })`).

#### Stage 4: Execution History parity test (no product change expected)

**Done when:** Component test documents that `list_dispatch_ledger` sets `total_cost` from `sum_cost_by_batch` (already implemented in `src/core/dispatcher.py`).

1. Do **not** edit `AdminPerformanceMonitor.tsx` unless test proves `total_cost` missing from API (it should not).
2. In `tests/component/ui/api/test_api_admin.py` (class `TestDispatchLedger`) or new class `TestAst571DispatchLedgerCostParity`:
   - Monkeypatch `admin_mod.list_dispatch_ledger` to return `[{"batch_id": "b-deep", "total_cost": 0.044939528}]`.
   - Monkeypatch is unnecessary if testing dispatcher: prefer `tests/component/core/test_dispatcher.py` with monkeypatch on `_db_list_dispatch_ledger` returning one row and `_db_sum_cost_by_batch` returning `{"b-deep": 0.044939528}`; call `dispatcher.list_dispatch_ledger()`; assert `rows[0]["total_cost"] == 0.044939528`.
3. Add one-line comment in `src/core/dispatcher.py` above `r["total_cost"] = costs.get(...)`:

   `# Display total matches sum of agent_timesheets calc_cost_* (AST-571).`

#### Stage 5: Manual UAT script (Susan)

**Done when:** Comment on **AST-571** with pass/fail after **AST-570** backfill on shared DB.

1. Open **Admin → Agent Timesheets**, filter `date_from=2026-06-03`, `date_to=2026-06-03`, `model_code=deepseek-v4-pro`.
2. For row `840f7662-a5de-44cd-ac2e-09fade0aca81`, confirm **$ Total** equals sum of four **$** component columns (four decimal places).
3. Export CSV; confirm `total_cost` column equals same value for that row.
4. Open **Execution History**, locate batch `draft_job_resume-f017d456-6ccb-4f90-82cc-364e1ec92c9f` (batch_id from parent CSV); confirm header total cost equals sum of timesheet rows for that batch (Batch Agent Data modal totals bar cross-check optional).

#### Self-Assessment

**Scope:** `Single-Component` — Touches one admin API surface, two frontend pages, one shared TS lib, and a small pure Python helper; no schema or pricing changes.

**Conf:** `high` — Formula is fixed in parent AC 7 and already used in SQL `sum_cost_by_batch`; work is wiring and regression tests, dependent on **AST-570** data being correct.

**Risk:** `Medium` — Wrong display erodes spend trust, but blast radius is admin read paths only; Anthropic rows use the same sum and must stay unchanged in tests.

#### Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.3 DRY | Single `sum_calc_cost_components` / `sumCalcCostComponents`; API enrichment once. |
| §2.1 config | No new config keys. |
| §3.3 imports | `api_admin` imports `utils.cost_calculator` only (allowed ui→utils). |
| §3.5 naming | Page stays `AdminAgentTimesheets.tsx` in `pages/`; new helper in `lib/timesheetCost.ts`. |
| §3.6 spikes | No spike output; UAT uses live admin UI. |

No `conf-!!-NONE` conflicts.

#### Execution contract

- Build **after** **AST-570** is on `dev-kath` (merge sibling sub ref in Pre-build).
- Stages 1→5 in order; one commit per stage on `dev-kath`; Joan `store-code-commit` to `origin/sub/AST-569/AST-571-admin-timesheet-cost-display` with `--session bae3ad87-8192-493e-9129-cf664a9afad5`.
- If API returns `total_cost` that disagrees with hand-sum of four components for a backfilled DeepSeek row, **stop** and comment on **AST-571** — do not patch pricing (**AST-570**).

#### Review (build)

**Branch:** `origin/sub/AST-569/AST-571-admin-timesheet-cost-display`
**Tip:** `4895fa848c59a0d4bc0e1cba23433037b616bc35` (Joan store-code-commit after stage 4)

**Stages shipped (product):**
1. `sum_calc_cost_components` + `CALC_COST_KEYS` in `src/utils/cost_calculator.py` (`a666d9fa` on publish ref `7953e0a8` ancestry)
2. `api_admin.py` — `_enrich_timesheet_row`, list/export `total_cost`, CSV/column metadata
3. `timesheetCost.ts`, `AdminAgentTimesheets.tsx`, `BatchAgentDataModal.tsx` — UI parity with API field
4. `dispatcher.py` — AST-571 comment on ledger `total_cost` assignment (behavior unchanged)

**Tests:** Betty at Code Complete (`qa-astral`) per plan Stages 2–4 component tests.

#### Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-569/AST-571-admin-timesheet-cost-display` (tip `af32280b`). AST-571-only commits after `merge(AST-570)` @ `8e959c5c` reviewed for plan fidelity.

##### What's solid

- **AC 7 formula:** `sum_calc_cost_components` / `CALC_COST_KEYS` in `src/utils/cost_calculator.py`; API `_enrich_timesheet_row` on list + CSV; `timesheetCost.ts` mirrors keys; `AdminAgentTimesheets` footer and `$ Total` column use `rowTotalCost`; `BatchAgentDataModal` batch bar sums per-row via `sumCalcCostComponents` on enriched API rows.
- **Execution History:** No product change; `list_dispatch_ledger` already uses `sum_cost_by_batch` (SQL sum of four `calc_cost_*`). AST-571 comment + `test_ast571_ledger_total_cost_matches_timesheet_sum` document parity.
- **Layers (§3.3):** `api_admin` adds only `utils.cost_calculator` import; no new `data`/`external` from UI.
- **Scope (§5d):** AST-571-only diff does not edit pricing, DeepSeek mapping, or backfill — sibling **AST-570** present only via documented merge base.

##### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| discuss | `tests/component/core/test_dispatcher.py` `test_ast571_ledger_total_cost_matches_timesheet_sum` | Mock total `0.044939528` vs `test_parent_brief_pro_row_840f7662` sum `0.044939328` from parent CSV literals (~2e-7). Display paths use the same four-key sum; align test constant in **resolve-astral** if you want one golden value. |

##### Recommended actions

| Action | Owner |
|--------|-------|
| Optional: set ledger test mock to `pytest.approx(0.044939328)` to match `TestSumCalcCostComponents::test_parent_brief_pro_row_840f7662` | Katherine / resolve-astral |
| Run plan Stage 5 manual UAT on backfilled DeepSeek rows after **AST-570** lands on shared DB | Susan |

#### Resolution (2026-06-03)

**Radia review:** No fix-now items. Discuss item (ledger test mock `0.044939528` vs cost-calculator golden `0.044939328`, ~2e-7) reviewed — display paths use the same four-key sum; delta is test-fixture only, not a product defect. Left unchanged per resolve-astral §9 (no test-tree commits on resolve pass).

**Publish:** Resolution doc commit via Joan `store-resolve-commit` to `origin/sub/AST-569/AST-571-admin-timesheet-cost-display`.

#### Files changed (plan vs actual)  _(no commit trail — plan only)_

| | file | planned | actual |
|---|---|---|---|
| · | `src/utils/cost_calculator.py` | Add `CALC_COST_KEYS` tuple and `sum_calc_cost_components(row | — |
| · | `src/ui/api/api_admin.py` | `_enrich_timesheet_row(row)`; apply in `list_timesheets_all` | — |
| · | `src/ui/frontend/src/lib/timesheetCost.ts` | `CALC_COST_KEYS`, `sumCalcCostComponents(row)` — mirror Pyth | — |
| · | `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Import lib; add `total_cost` column; totals use `row.total_c | — |
| · | `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | Replace inline cost sum with `sumCalcCostComponents`. | — |
| · | `tests/component/utils/test_cost_calculator.py` | `TestSumCalcCostComponents` — zeros, partial None, parent br | — |
| · | `tests/component/ui/api/test_api_admin.py` | `TestAst571LedgerCostUsesTimesheetSum` — ledger `total_cost` | — |
| · | `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` | Assert `$ Total` column and footer cost matches sum of four  | — |
| · | `docs/ASTRAL_TEST_BIBLE.md` | §7.13zza manifest (Betty adds in qa-astral). | — |

### AST-580 — UAT: 2026-06-04 deepseek-v4-pro cost mismatch (tokens correct)

_Archived: 2026-06-15 · Linear URL: https://linear.app/astralcareermatch/issue/AST-580/uat-2026-06-04-deepseek-v4-pro-cost-mismatch-tokens-correct · Status at archive: Done · Project: Astral Agent · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-569_

#### Bug (parent UAT AST-569)

Susan **2026-06-05**: UTC **2026-06-04** `deepseek-v4-pro` — daily token totals match DeepSeek export (miss **22431**, output **9778**) but **cost still wrong**.

**Rows:** `a811f41e-617c-406d-876f-20e501852217`, `b2904570-f064-4a14-b16b-ef06c2159a99`

**Triage:** stored `calc_cost_*` reconciles to export per-token rates on `total_no_cache_input` + `total_output` (see parent `[check-linear]`). Open: which dollar surface disagrees (DeepSeek dashboard total, Admin **$ Total**, manual calc using `no_cache_live`+`no_cache_prompt`).

**Code:** `src/utils/cost_calculator.py`, `src/utils/config.py` (`DEEPSEEK_MODEL_PRICING`), `src/external/deepseek.py`, `src/ui/api/api_admin.py`, `src/ui/frontend/src/lib/timesheetCost.ts`

**Parent ftr:** `origin/ftr/ast-569-timesheets-deepseek-cost` @ `d9656be9` · local `dev` @ `5b96f9db`

##### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
