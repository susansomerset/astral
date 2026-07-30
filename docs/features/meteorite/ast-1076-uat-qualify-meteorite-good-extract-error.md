# AST-1076 — UAT: qualify_meteorite good extract → ERROR (astral_job_id 000 + RESPONSE NameError)

**Linear:** [AST-1076](https://linear.app/astralcareermatch/issue/AST-1076/uat-qualify-meteorite-good-extract-error-astral-job-id-000-response)
**Parent:** [AST-1058](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite) — Qualify Meteorite
**Publish ref:** `origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error`

UAT fix on the shipped qualify path: Ruth returns usable meteorite enrich fields but echoes assemble line index (`"000"`) as `astral_job_id`, so `_run_batch_consult` treats the claim as MISSING / response as FABRICATED and lands **METEORITE_ERROR_QUALIFY**. Same debug run NameErrors in `_store_response_block` (`result` undefined after `save_agent_data`). Restore Parent AC4 success bind; keep content-fail → **METEORITE_FAILED_QUALIFY**. Does **not** change gazer ingest or post-qualify GDL.

## UAT fitness

- **AC restored:** Parent AC4 — “Batch task `qualify_meteorite` claims **METEORITE_NEW**, returns external job UUID, job title, `job_link`, and visible JD content; on success the job is on **METEORITE_QUALIFIED** with those fields as authoritative content.” (AC6 remains for truly unusable extracts → **METEORITE_FAILED_QUALIFY**, not for complete extracts that only mangled the echo id.)
- **Correct outcome:** Single-job (and ordered) `qualify_meteorite` batches bind the extract to the claimed job; success → **METEORITE_QUALIFIED** with title / link / jd / `company_job_id`. RESPONSE debug logging does not throw.
- **Sibling check:** AST-1062 apply + AST-1060 schema/states unchanged in role; content gates still send blank/short fields to **METEORITE_FAILED_QUALIFY**; roster `qualify_job_listings` behavior unchanged except shared helpers only if the bind is scoped so listing grades paths keep today’s ID rules.
- **Not sufficient:** Removing the stacktrace / exception / ERROR state alone without binding fields onto the claimed job and reaching **METEORITE_QUALIFIED**.
- **Wrong fix rejected:** Swallow NameError and mark success anyway; delete debug logging; accept any fabricated id without binding to claim; move ERROR jobs to QUALIFIED without applying fields; weaken AC so ERROR is OK when payload “looks fine.”

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Capture `save_agent_data` return as `result` in `_store_response_block` debug path | core |
| `src/core/consult.py` | Bind placeholder / single-job mismatched `astral_job_id` to claimed jobs before MISSING/FABRICATED accounting in `_run_batch_consult` (helper + call site) | core |

No gazer / config TASK_CONFIG / dispatcher / frontend / `tests/` / bible (Betty after Code Complete).

## Stage 1: RESPONSE debug NameError + claim-id bind for qualify fields

**Done when:** `_store_response_block(..., debug=True)` never raises `NameError` on `result`; a one-job `qualify_meteorite` batch whose Ruth JSON has usable fields but `astral_job_id` `"000"` (or other non-claimed placeholder) binds to the claimed UUID, runs `process_fn`, and can reach **METEORITE_QUALIFIED**; ordered multi-job batches with `\d{1,3}` / empty echo ids bind by index when lengths match; true content-gate fails still → **METEORITE_FAILED_QUALIFY**; `python3 -m py_compile src/core/agent.py src/core/consult.py` succeeds.

1. In `src/core/agent.py` `_store_response_block`, mirror `_store_prompt_blocks`’s `_save`: assign `result = save_agent_data(...)` then use `result.get("outcome")` / `agent_data_id` / `ref_agent_data_id` in the `debug` `debug_detail` line. Keep the existing `return agent_data_id` (local id string). Do **not** delete the debug block.

2. In `src/core/consult.py`, add a small helper near `_ensure_jobs_astral_ids` (same module, public-then-helpers: helper above call site):

```python
def _bind_response_jobs_to_claimed(response_jobs: list, claimed_jobs: list) -> None:
    """Rewrite placeholder / single-job mismatched astral_job_id to claimed ids (AST-1076).

    Assemble prefixes use 000/001…; fields-output Ruth often echoes that as astral_job_id.
    """
```

Rules (literal):

- Build `claimed_ids = [j["astral_job_id"] for j in claimed_jobs if j.get("astral_job_id")]` and `claimed_set = set(claimed_ids)`.
- Skip if `response_jobs` empty or `claimed_ids` empty.
- **Single-job bind:** if `len(response_jobs) == 1` and `len(claimed_ids) == 1`: if `(response_jobs[0].get("astral_job_id") or "").strip() not in claimed_set`, set `response_jobs[0]["astral_job_id"] = claimed_ids[0]`. Return.
- **Ordered placeholder bind:** if `len(response_jobs) == len(claimed_ids)`: for each index `i`, let `aid = (response_jobs[i].get("astral_job_id") or "").strip()`; if `not aid` or `re.fullmatch(r"\d{1,3}", aid)`, set `response_jobs[i]["astral_job_id"] = claimed_ids[i]`. Do **not** overwrite a response id that is already in `claimed_set`. Do **not** overwrite a non-digit fabricated UUID on multi-job batches (leave for existing FABRICATED drop).

⚠️ **Decision — bind in `_run_batch_consult` before MISSING/FABRICATED:** Fields tasks never hit `_ensure_jobs_astral_ids` (rubric-only). Fixing only `_ensure_jobs_astral_ids` would miss `qualify_meteorite`. Call the helper for every `_run_batch_consult` after `response_jobs = parsed["jobs"]` and after grade-reason hydration, **before** `sent_ids` / `received_ids` / missing transition — so listing qualify also recovers position-echo ids if they ever appear, without changing happy-path when ids already match.

3. In `_run_batch_consult`, immediately after successful hydration of `response_jobs` (and before the `sent_ids` / `received_ids` block), call `_bind_response_jobs_to_claimed(response_jobs, jobs)`.

4. Do **not** change `qualify_meteorite` content gates, `initialize_job` mapping, pass/fail/error states, gazer, or `qualify_job_listings` process_fn. Do **not** auto-promote ERROR rows without applying fields.

**Done when (recheck):** With claimed id `C` and Ruth `{"jobs":[{"astral_job_id":"000","company_job_id":"…","job_title":"…","job_link":"https://…","jd_text":"<≥min chars>"}]}`, after bind `received_ids` contains `C`, process runs, job → **METEORITE_QUALIFIED**. Short/blank fields still → **METEORITE_FAILED_QUALIFY**. `_store_response_block(..., debug=True)` logs outcome without NameError.

## Self-Assessment

**Scope:** `Single-Component` — two core files; claim-id bind + debug write fix only.

**Conf:** `high` — NameError is a clear missing assignment; `"000"` matches assemble `i:03d` echo; diagnosis spells bind rules.

**Risk:** `Medium` — over-eager multi-job remap could mis-bind; mitigated by digit/empty-only remap on multi and single-job-only bind for any non-claimed id.

## Self-review vs ASTRAL_CODE_RULES

- **§1.5.1 debug-contract-gated:** NameError fix restores gated debug lines; no new `debug=False` noise.
- **§2.2 do-task-delegation / §2.6 core-decides-transitions:** Bind happens in consult before process; core still decides QUALIFIED vs FAILED_QUALIFY.
- **§2.4 claim-process-release:** Claim surface unchanged; process receives correctly keyed response rows.
- **§1.3 DRY:** One helper; listing + meteorite share bind via `_run_batch_consult`.
