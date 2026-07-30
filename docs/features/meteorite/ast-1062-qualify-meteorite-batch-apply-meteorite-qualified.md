# AST-1062 — qualify_meteorite batch apply → METEORITE_QUALIFIED

**Linear:** [AST-1062](https://linear.app/astralcareermatch/issue/AST-1062/qualify-meteorite-batch-apply-meteorite-qualified-qualify-meteorite)
**Parent:** [AST-1058](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite) — Qualify Meteorite
**Publish ref:** `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`

Wires core/consult so Ruth task key `qualify_meteorite` (config/dispatch/agent_task already on tip from AST-1060) claims **METEORITE_NEW**, runs the same Pattern-A claim→`_run_batch_consult`→process→release shape as `qualify_job_listings`, persists external UUID / title / `job_link` / visible JD, and transitions **METEORITE_NEW → METEORITE_QUALIFIED** or **METEORITE_FAILED_QUALIFY** (technical batch failures → **METEORITE_ERROR_QUALIFY**). Style D on the apply path. Does **not** author gazer ingest (AST-1061) or invent a new Ruth batch pattern.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `min_job_title_length` + `min_jd_chars` on `TASK_CONFIG["qualify_meteorite"]` only | utils |
| `src/core/consult.py` | New `qualify_meteorite` batch wrapper + `run_consult_task` branch | core |
| `src/core/dispatcher.py` | Add `qualify_meteorite` to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` | core |
| `src/ui/api/api_admin.py` | Ad Hoc live-content assemble for `qualify_meteorite` (mirror listing qualify) | ui |

No gazer / meteorite create / `agent_task.json` prompt rewrite / frontend TS / `tests/` / bible (Betty after Code Complete). Do **not** edit `qualify_job_listings` behavior. Do **not** add `qualify_meteorite` to `agent._STRICT_ENCODED_BATCH_CONSULT_KEYS` (`output_type: "fields"`, not grades-encoded).

## Stage 1: Config thresholds for content fail gates

**Done when:** `TASK_CONFIG["qualify_meteorite"]` exposes the two mins below; other TASK_CONFIG / JOB_STATES / METEORITE_DISPATCH_TASKS rows unchanged; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, inside the existing `"qualify_meteorite"` TASK_CONFIG block (do **not** change `response_schema`, `pass_state` / `fail_state` / `error_state`, `output_type`, or `agent_task`), add after `fallback_batch_size`:

```python
        "min_job_title_length": 5,   # same role as qualify_job_listings title gate
        "min_jd_chars": 40,          # usable visible JD floor (align with METEORITE_EMAIL_INGEST_CONFIG)
```

⚠️ **Decision — content fail via apply gates, not grade vectors:** AST-1060 chose `scored: False` + `output_type: "fields"`. Schema allows empty strings (`required` checks `None` only). Ruth may return blank / placeholder fields for bogus/404/unusable extracts; `process_fn` maps those to `fail_state` (**METEORITE_FAILED_QUALIFY**). Envelope / schema / `do_task` failures stay on `error_state` via existing `_run_batch_consult` (AST-1060 three-outcome split).

## Stage 2: `qualify_meteorite` consult batch + dispatch wiring

**Done when:** Dispatcher can invoke `qualify_meteorite` through `run_consult_task`; a claimed **METEORITE_NEW** job that receives usable Ruth fields lands on **METEORITE_QUALIFIED** with `company_job_id` / `job_title` / `job_link` columns and `job_data["job_description"]` = returned `jd_text`; content-gate fails land on **METEORITE_FAILED_QUALIFY**; `qualify_job_listings` path unchanged; Style D emits only when `debug=True`; `python3 -m py_compile src/core/consult.py src/core/dispatcher.py src/ui/api/api_admin.py` succeeds.

1. In `src/core/consult.py`, immediately after `qualify_job_listings` (before `_jd_ready_for_evaluate`), add:

```python
async def qualify_meteorite(
    batch_id: str,
    jobs: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    batch_chunk_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Meteorite pre-AI enrich (Pattern A). Same claim/process shape as qualify_job_listings;
    fields output (no grades). AST-1062."""
```

Implementation rules (literal):

- `task_key = "qualify_meteorite"`; `cfg = _consult_orchestration(task_key)` (no meteorite GDL overlay needed — this key already has meteorite pass/fail/error).
- Do **not** call `validate_title_batch` / filter to VALID_TITLE* (roster-only).
- Claimed jobs are already **METEORITE_NEW**; process all `jobs` passed in (dispatcher claim surface).
- When `debug`: `logger.set_debug_flag(True)`; one `debug_detail` for `batch_id` + `job_count`; per-job `debug_index` (`func="consult.qualify_meteorite"`, identifier=`_consult_job_identifier(j)`, outcome=`"input job"`) + `debug_detail` with found `job_link` and `job_description` char length from `job_data` (Style D found→recorded later in process).
- `assemble(jobs)` — 0-based numbered lines, **exclude** `astral_job_id` from live content (same position contract as listing qualify; response still carries `astral_job_id` per schema). Use:

```python
    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    lines = [
        f"{i:03d}: job_link: {j.get('job_link') or ''}\n"
        f"job_description: {(j.get('job_data') or {}).get(jd_key, '') or ''}"
        for i, j in enumerate(jobs)
    ]
    return "METEORITE JOBS:\n" + "\n".join(lines)
```

  Import `TRACKER_CONFIG` from `src.utils.config` if not already imported in this module.

- `process(input_job, response_job, cfg)`:
  1. `aid = response_job["astral_job_id"]`.
  2. Strip fields: `company_job_id`, `job_title`, `job_link`, `jd_text` from `response_job`.
  3. **Content fail → `cfg["fail_state"]`** (no `initialize_job`) when any of:
     - `company_job_id` empty after strip
     - `len(job_title) < cfg["min_job_title_length"]`
     - `job_link` does not start with `"http"`
     - `len(jd_text) < cfg["min_jd_chars"]`
     Transition via `_transition_job_state_for_task(task_key, [aid], cfg["fail_state"])`. When `debug`, `debug_index` + `debug_detail` with which gate failed and found vs required. When not debug, `logger.info` title/aid → fail_state. Return fail_state.
  4. **Pass path:** build `parsed_job` for `tracker.initialize_job`:

```python
     parsed_job = {
         "company_job_id": company_job_id,
         "job_title": job_title,
         "job_link": job_link,
         jd_key: jd_text,   # authoritative visible JD → job_data job_description
     }
```

     Do **not** pass a `jd_text` key into `initialize_job` (would pollute job_data). Company = `input_job["company"]`.
  5. If `initialize_job` returns `False` (identity collision / deleted): treat as content fail → `cfg["fail_state"]` (same as listing qualify collision → fail_state); do **not** transition after delete (row gone). Return fail_state.
  6. Else `_transition_job_state_for_task(task_key, [aid], cfg["pass_state"])`. When `debug`: Style D index outcome=`METEORITE_QUALIFIED` + detail `found` (response fields) vs `recorded` (re-read via `tracker.get_job(aid)` columns + `job_data[jd_key]` lengths/values). When not debug: `logger.info` → pass_state. Return pass_state.
  7. Raise `ValueError` only for unexpected programming errors (caught by `_run_batch_consult` → missing from pass/fail counts / bad_grades path). Do **not** raise for content gates — those are fail_state.

- Return `await _run_batch_consult(task_key, batch_id, jobs, assemble, process, ctx, debug, batch_chunk_index=batch_chunk_index)`.

⚠️ **Decision — reuse `initialize_job` for column write:** Same identity-collision enforcement as `qualify_job_listings`. Remap schema `jd_text` → `TRACKER_CONFIG["job_data_keys"]["job_description"]` so coat-check / `evaluate_jd` see authoritative JD under the standard key.

⚠️ **Decision — no title-screen prefilter:** Meteorite jobs already carry visible JD from gazer/create; Ruth enriches metadata. Roster `validate_title_batch` must not run.

2. In `run_consult_task` (job branch), immediately after the `qualify_job_listings` arm, add:

```python
    elif task_key == "qualify_meteorite":
        r = await qualify_meteorite(
            batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
        )
```

3. In `src/core/dispatcher.py`, add `"qualify_meteorite"` to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` (next to `"qualify_job_listings"`) so `batch_call_mode=1` uses the same widen-claim + chunk parallel waves as listing qualify.

⚠️ **Decision — chunk exhaust membership:** AST-1060 already put `qualify_meteorite` in `_DISPATCH_BATCH_CALL_MODE_ONE`. Without chunk-exhaust membership, mode-1 would claim full backlog in one consult call; listing qualify uses chunk waves — parent says “exact same batch shape.”

4. In `src/ui/api/api_admin.py` `_adhoc_live_content` (or equivalent job assemble helper around the `qualify_job_listings` branch ~1179), add a sibling branch for `task_key == "qualify_meteorite"`:

- Resolve job ids the same way as listing qualify.
- For each job: read `job_link` and `job_data[TRACKER_CONFIG["job_data_keys"]["job_description"]]`.
- Emit the same `METEORITE JOBS:\n{i:03d}: …` shape as consult `assemble` (keep Ad Hoc / production assemble in lockstep).

5. Do **not** modify `agent.py` strict-encoded frozenset. Do **not** change `qualify_job_listings`, gazer, meteorite create, or GDL `evaluate_jd` (already claims **METEORITE_QUALIFIED** from AST-1060).

**Done when (recheck):**

- `run_consult_task(..., dispatch_task_key="qualify_meteorite", ...)` reaches `qualify_meteorite`.
- Content-gate fail → `JOB_STATES` prior allows **METEORITE_NEW → METEORITE_FAILED_QUALIFY**.
- Pass → columns + `job_description` set; state **METEORITE_QUALIFIED**.
- `debug=False` produces no new `debug_index` / `debug_detail` lines from this path; `debug=True` shows index + `|`-style detail for input and recorded outcomes.
- Non-meteorite `qualify_job_listings` smoke still routes only on its own branch.

## Self-Assessment

**Scope:** `Single-Component` — consult batch apply + thin dispatcher/Ad Hoc assemble + two TASK_CONFIG threshold keys; no gazer, no new batch pattern, no frontend.

**Conf:** `high` — AST-1060 already shipped states/schema/dispatch/agent_task; this ticket mirrors `qualify_job_listings` → `_run_batch_consult` with a fields `process_fn` and known fail/error split.

**Risk:** `Medium` — wrong persist/transition would stall meteorite GDL entry or pollute identity columns; roster `qualify_job_listings` is untouched by construction but shared `_run_batch_consult` / `initialize_job` must stay behavior-stable.

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One new wrapper; shared `_run_batch_consult` / `initialize_job` / `_transition_job_state_for_task` — no duplicated batch scaffolding.
- **§2.1 config:** Thresholds on `TASK_CONFIG["qualify_meteorite"]`; states/pass/fail/error already config-owned (AST-1060).
- **§2.2 / do-task-delegation:** Ruth I/O via `do_task` inside `_run_batch_consult`; core `process_fn` decides persist + transitions.
- **§2.4 claim-process-release / batch-id-first:** Dispatcher claim unchanged; consult processes claimed slice; chunk exhaust aligned with listing qualify.
- **§2.4.1 entity-agent-responses-latest-only:** Unchanged — `_run_batch_consult` already tags RESPONSE via `agent_ref`.
- **§2.6 core-decides-transitions:** Transitions only in consult `process_fn` / batch error paths — not in agent prompts.
- **§1.5.1 debug-contract-gated:** Style D only under `debug=True`.
- **§3.3 imports:** UI Ad Hoc may import `TRACKER_CONFIG` / database (existing pattern); no UI→core invent path for normalize.

No statute conflicts requiring `conf-!!-NONE`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`
**Plan path:** `docs/features/meteorite/ast-1062-qualify-meteorite-batch-apply-meteorite-qualified.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ffd116e7` | TASK_CONFIG min_job_title_length + min_jd_chars on qualify_meteorite |
| 2 | `03b0ab1f` | qualify_meteorite consult wrapper + run_consult_task + chunk-exhaust + Ad Hoc assemble |

**Tip:** `03b0ab1f2c8388ad32557e9254d85634a54c602d` on `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`
