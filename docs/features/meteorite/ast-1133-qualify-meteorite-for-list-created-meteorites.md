# AST-1133 — qualify_meteorite for list-created meteorites

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1133/qualify-meteorite-for-list-created-meteorites-manage-email-create  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working  

**Publish ref (origin):** `sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites`  
**Parent integration ref:** `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`

After AST-1131 / AST-1132 produce clean **METEORITE_NEW** rows from Manage Email list Create (Dice Saved-jobs HTML or newline-delimited ATS links), owns restoring end-to-end `qualify_meteorite` so usable extracts reach **METEORITE_QUALIFIED** with non-empty `job_title` and non-empty `company_job_id`. Investigates remaining **METEORITE_ERROR_QUALIFY** (technical / missing-id) vs content **METEORITE_FAILED_QUALIFY**. Does **not** widen `gaze_email` Ruth parse (AST-1089), change GDL, or re-own paste normalize / link hygiene.

**Diagnosis (code tip after AST-1131+1132 merge — no runtime spike required):**

Create already lands `job_link` + Playwright JD with null title / null `company_job_id` (`create_meteorite_job`). Shipped qualify path already has: Pattern-A batch apply (AST-1062), placeholder `"000"` / `\d{1,3}` bind (AST-1076), optional schema `company_job_id` + UUID-from-`job_link` resolve (AST-1120 / AST-1127). Two remaining gaps still push **usable** list-created rows off the QUALIFIED path:

1. **Multi-job claim-id bind gap → ERROR:** `_bind_response_jobs_to_claimed` only remaps empty/`\d{1,3}` when `len(response) == len(claimed)`. When Ruth echoes a non-digit wrong id (e.g. external UUID, or job URL) into `astral_job_id` on a multi-job batch, every row is treated as FABRICATED and every claim becomes MISSING → **METEORITE_ERROR_QUALIFY**. List Create commonly qualifies 2–N jobs in one batch; single-job bind does not cover that shape.
2. **Create-time `job_link` ignored by http content gate → FAILED:** `qualify_meteorite` process already uses `input_job["job_link"]` for `_resolve_company_job_id` fallback, but the `job_link.startswith("http")` gate and `initialize_job` persist only Ruth’s `job_link`. Empty / non-http Ruth link fails content gate even when Create stored a clean ATS URL — wrong outcome for usable extracts (should QUALIFY with create link, not FAILED/ERROR).

True content failures (short title, short `jd_text`, no AI id and no UUID in any usable link) stay **METEORITE_FAILED_QUALIFY**. Whole-batch `do_task` envelope/schema failures stay **METEORITE_ERROR_QUALIFY** (not reinvented here).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Job-link claim-id bind for `qualify_meteorite` multi-job batches; input `job_link` fallback in `qualify_meteorite` process + Style D source label | core |

No config / gazer / inbox / dispatcher / agent_task / UI / `tests/` / bible changes (Betty after Code Complete). Do **not** edit `_bind_response_jobs_to_claimed` digit rules (AST-1076 stays as-is). Do **not** invent a parallel batch shape or force `batch_size=1`.

---

## Stage 1: Bind multi-job qualify responses by `job_link` when claim ids mismatch

**Done when:** A multi-job `qualify_meteorite` batch whose Ruth rows carry usable title / link / jd / id fields but non-claimed non-digit `astral_job_id` values still bind 1:1 to claimed rows via normalized `job_link`, reach `process_fn`, and can land **METEORITE_QUALIFIED**; equal-count digit/`000` bind (AST-1076) still works first; unmatched / ambiguous links are left for existing MISSING/FABRICATED accounting; `qualify_job_listings` path unchanged; `python3 -m py_compile src/core/consult.py` succeeds.

1. In `src/core/consult.py`, immediately after `_bind_response_jobs_to_claimed`, add:

```python
def _bind_response_jobs_by_job_link(response_jobs: list, claimed_jobs: list) -> None:
    """Bind unmatched response rows to claimed jobs by normalized job_link (AST-1133).

    Used when Ruth puts a non-digit wrong value in astral_job_id on multi-job
    qualify_meteorite batches. Does not overwrite ids already in the claim set.
    """
```

2. Implement literally:

- Import `normalize_link` from `src.utils.formatting` at module top if not already imported (consult already imports `uuid_path_segment_from_url` from the same module — add `normalize_link` to that import).
- Skip if `response_jobs` empty or `claimed_jobs` empty.
- `claimed_ids = [j["astral_job_id"] for j in claimed_jobs if j.get("astral_job_id")]`
- `claimed_set = set(claimed_ids)`
- `claimed_by_link: dict[str, str] = {}` — for each claimed job with both `astral_job_id` and a non-empty `normalize_link(job_link)`, map `norm → astral_job_id`. If two claims normalize to the same key, **drop that key** from the map (ambiguous — do not bind either via link).
- `assigned = { (rj.get("astral_job_id") or "").strip() for rj in response_jobs if isinstance(rj, dict) and (rj.get("astral_job_id") or "").strip() in claimed_set }`
- For each `rj` in `response_jobs` where `isinstance(rj, dict)`:
  - `aid = (rj.get("astral_job_id") or "").strip()`
  - If `aid in claimed_set`: continue
  - `norm = normalize_link(rj.get("job_link") or "")`
  - If not `norm`: continue
  - `target = claimed_by_link.get(norm)`
  - If not `target` or `target in assigned`: continue
  - Set `rj["astral_job_id"] = target`; add `target` to `assigned`

⚠️ **Decision — second helper, do not widen AST-1076 digit remap:** AST-1076 explicitly refuses to overwrite non-digit fabricated UUIDs on multi-job batches (correct for listing grades). List-created meteorites have authoritative Create `job_link`s that Ruth is also asked to echo — link match is a safe second key without promoting arbitrary UUID remaps.

⚠️ **Decision — qualify_meteorite only:** Call this helper only for `task_key == "qualify_meteorite"` so roster `qualify_job_listings` keeps today’s bind surface.

3. In `_run_batch_consult`, immediately after `_bind_response_jobs_to_claimed(response_jobs, jobs)`, add:

```python
    if task_key == "qualify_meteorite":
        _bind_response_jobs_by_job_link(response_jobs, jobs)
```

4. When `debug` and `task_key == "qualify_meteorite"`, after both binds, emit one `debug_detail` listing final `astral_job_id` values on `response_jobs` (compact list). Do **not** emit when `debug=False`.

**Done when (recheck):** Claimed links `L0,L1,L2` with ids `C0,C1,C2`; Ruth returns three jobs with `astral_job_id` = Dice UUIDs (not C*) but `job_link` matching `L0..L2` and usable title/jd/company_job_id → after bind, `received_ids == {C0,C1,C2}`, no MISSING, process runs, states can reach **METEORITE_QUALIFIED**. Ambiguous duplicate normalized links → no link-bind for that key; digit bind still applies when lengths match.

---

## Stage 2: Prefer Create-time `job_link` when Ruth’s link is unusable

**Done when:** `qualify_meteorite` process uses a http(s) `job_link` from the claimed input row when Ruth’s `job_link` is empty or does not start with `"http"`; UUID resolve + `initialize_job` persist that link; content fail for short title / short jd / empty resolved `company_job_id` still → **METEORITE_FAILED_QUALIFY**; Style D records whether link came from AI or input; single-job happy path with good Ruth link unchanged; `python3 -m py_compile src/core/consult.py` succeeds.

1. In `qualify_meteorite`’s `process` closure, replace the current strip + resolve preamble so that after reading Ruth fields:

```python
        ai_company_job_id = (response_job.get("company_job_id") or "").strip()
        job_title = (response_job.get("job_title") or "").strip()
        ruth_link = (response_job.get("job_link") or "").strip()
        input_link = (input_job.get("job_link") or "").strip()
        jd_text = (response_job.get("jd_text") or "").strip()
        if ruth_link.startswith("http"):
            job_link = ruth_link
            link_source = "AI"
        elif input_link.startswith("http"):
            job_link = input_link
            link_source = "input"
        else:
            job_link = ruth_link
            link_source = "neither"
        company_job_id = _resolve_company_job_id(ai_company_job_id, job_link)
```

2. Keep the existing `id_source` labels for `company_job_id` (`AI` / `UUID-from-job_link` / `neither`) based on `ai_company_job_id` vs resolved id — unchanged logic, but pass `job_link` (post-fallback) into `_resolve_company_job_id` (no separate `link_for_id`).

3. Keep content gates in this order: empty `company_job_id` → title too short → `not job_link.startswith("http")` → `jd_text` too short. On fail / pass Style D detail lines, append `link_source={link_source}` next to the existing `found source={id_source}` bits (debug only).

4. Pass path: `parsed_job["job_link"]` must be the post-fallback `job_link` (so Create ATS URL is recorded when Ruth omitted it).

⚠️ **Decision — no jd_text / title fallback from input:** Title is null at Create; Playwright body may be chrome-heavy. Ruth still owns title + authoritative `jd_text`. Only `job_link` is Create-authoritative for list ingest.

⚠️ **Decision — Ruth http link wins when present:** Prefer AI enrich URL when it is a real http(s) link; fall back only when Ruth’s value cannot satisfy the http gate.

**Done when (recheck):** Claimed job with `job_link=https://www.dice.com/job-detail/<uuid>`, Ruth returns title + jd + omit/`null` `company_job_id` + empty `job_link` → resolve UUID from input link, pass http gate, → **METEORITE_QUALIFIED** with non-empty title + `company_job_id` + recorded Dice link. Short title still → **METEORITE_FAILED_QUALIFY**. Envelope `do_task` failure still → **METEORITE_ERROR_QUALIFY** for the batch (unchanged).

---

## Self-Assessment

**Scope:** `Single-Component` — one core file (`consult.py`); bind helper + qualify process link fallback only.

**Conf:** `high` — tip after 1131/1132 already has apply + digit bind + UUID resolve; remaining ERROR/FAILED paths for usable list rows are the two concrete gaps above.

**Risk:** `Medium` — over-eager link bind could mis-pair if Ruth returns wrong links; mitigated by unique normalized-link map + never overwriting claimed ids + qualify_meteorite-only call site. Wrong input-link fallback would persist Create URL when Ruth intended a different http link — mitigated by preferring Ruth whenever it starts with `http`.

---

## Self-review vs ASTRAL_CODE_RULES

- **§2.4 claim-process-release / `pattern.batch.entity-claim-process-release`:** Batch shape unchanged; only id reconciliation + process field selection harden.
- **§2.6 / `astral.state.core-decides-transitions`:** Core still maps pass → QUALIFIED, content → FAILED_QUALIFY, technical → ERROR_QUALIFY; no new states.
- **§2.2 / `astral.agent.do-task-delegation`:** Still one `do_task` via `_run_batch_consult`; no UI LLM.
- **§1.5.1 / `astral.standards.debug-contract-gated`:** New detail only under existing `debug` gates.
- **§1.3 DRY:** Second bind helper; digit rules left in AST-1076 helper.
- **§1.1 in-scope-only:** No gazer / gaze_email / GDL / config knobs.
- **§3.3 import-direction:** `normalize_link` from utils into core — already allowed.

No plan conflicts requiring `conf-!!-NONE`.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites`  
**Plan path:** `docs/features/meteorite/ast-1133-qualify-meteorite-for-list-created-meteorites.md`

**Built tip:**  ()

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 |  | job-link claim bind + Create-time job_link fallback in qualify_meteorite |
