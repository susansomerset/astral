# AST-1099 — Pin agent_data_id on job artifact slots after chain hops

**Linear:** [AST-1099](https://linear.app/astralcareermatch/issue/AST-1099/pin-agent-data-id-on-job-artifact-slots-after-chain-hops-job-resume)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved) (AC reference only)

**Publish ref:** `origin/sub/AST-1091/AST-1099-pin-agent-data-id`

After a successful `finalize_job_resume` / `finalize_cover_letter` / `propose_application_responses` hop, core writes that hop's RESPONSE `agent_data_id` into `job_data.artifacts.job_resume` / `cover_letter` / `proposed_answers` — including mid-chain when `run_next` continues. Bodies stay in `agent_data`; this ticket pins pointers only. JAR/UI resolve is AST-1100.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add task_key → artifact slot map; extend `JOB_BUILD_ARTIFACT_CLEAR_KEYS` with pin slots | utils |
| `src/core/tracker.py` | Add `pin_job_artifact_agent_data_id` (non-empty id only; Style D found/recorded when `debug=True`) | core |
| `src/core/agent.py` | After successful RESPONSE store for the three task keys, call pin regardless of `run_next`; stop terminal body-copy via `persist_job_artifact_from_parsed` for `finalize_job_resume` / `finalize_cover_letter` | core |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| JAR / Materials Preview / API readers resolve pinned ids to bodies | AST-1100 |
| `JOBS_RECOMMENDED_ARTIFACT_TABS` `artifact_key` remaps | AST-1100 |
| TASK_CONFIG `persist_in` (or any new destination dialect) | excluded by parent |
| `save_prefix` grade / craft / `analysis_upshot` persists | excluded by parent |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: Config — pin map + cancel clear keys

**Done when:** `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` (exact name below) maps the three task keys to the three slot names; `JOB_BUILD_ARTIFACT_CLEAR_KEYS` includes the three pin slots so cancel does not leave stale pointers; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, immediately after `JOB_BUILD_ARTIFACT_CLEAR_KEYS`, add:

```python
# AST-1099: do_task pins RESPONSE agent_data_id under job_data.artifacts[<slot>] (pointer only).
JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK = {
    "finalize_job_resume": "job_resume",
    "finalize_cover_letter": "cover_letter",
    "propose_application_responses": "proposed_answers",
}
```

2. Change `JOB_BUILD_ARTIFACT_CLEAR_KEYS` to include the pin slots while keeping the legacy body keys (manual PUT / older rows still clear on cancel):

```python
JOB_BUILD_ARTIFACT_CLEAR_KEYS = (
    "resume_content",
    "cover_letter",
    "application_responses",
    "job_resume",
    "proposed_answers",
)
```

⚠️ **Decision:** Slot names are exactly `job_resume` / `cover_letter` / `proposed_answers` per parent AC (not `resume_content` / `application_responses`). `cover_letter` becomes a pointer string under this epic; AST-1100 updates readers. Legacy body keys stay in the clear tuple so cancel still wipes old blobs.

## Stage 2: Tracker — pin helper (never store empty)

**Done when:** `pin_job_artifact_agent_data_id` merges a non-empty string id into `job_data.artifacts[slot]`; blank/None/whitespace id skips the write and does not clear a prior value; when `debug=True`, Style D detail logs recorded key+id or skip reason; when `debug=False`, no new debug-contract lines; `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py`, import `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` only if needed for validation — prefer validating the slot as a non-empty `str` at the call site; the helper accepts `(astral_job_id, artifact_key, agent_data_id, *, debug=False) -> bool` and returns `True` only when a write happened.
2. Implement `pin_job_artifact_agent_data_id` next to the other artifact save helpers (`save_job_artifact_cover_letter` / `persist_job_artifact_from_parsed`):
   - If `astral_job_id` is missing/blank → return `False` (optional debug skip reason `missing_job_id`).
   - If `artifact_key` is missing/blank → return `False` (skip reason `missing_artifact_key`).
   - Coerce `agent_data_id` with `str(...).strip()`; if empty → return `False` without calling `save_job_data` (skip reason `empty_agent_data_id`) — coat-check never-store-empty.
   - On success: `save_job_data(astral_job_id, {"artifacts": {artifact_key: agent_data_id}})` (deep merge; other artifact keys untouched).
   - When `debug=True`: `get_logger(__name__, debug_flag=True)` then `debug_detail` — recorded line `artifact_pin key=<artifact_key> agent_data_id=<id> recorded` or skip line `artifact_pin key=<artifact_key> skipped reason=<reason>`. No ungated `[DEBUG]` spam; no `logger.info("[DEBUG] …")`.
3. Do **not** rewrite `persist_job_artifact_from_parsed` body-merge helpers here — Stage 3 stops calling them for the pin task keys from `do_task`.

⚠️ **Decision:** Pointer value is the bare RESPONSE `agent_data_id` string (same id returned by `_store_response_block`), not a nested `{agent_data_id: …}` object — matches parent AC “equals that hop's RESPONSE `agent_data_id`”.

## Stage 3: Agent — pin after successful RESPONSE store (mid-chain and terminal)

**Done when:** On a successful hop for each of the three task keys, after a RESPONSE row is stored and its id is known, `job_data.artifacts[<slot>]` equals that id whether or not `run_next` continues; failed/empty id paths leave a prior good pointer untouched; terminal `persist_job_artifact_from_parsed` no longer body-copies for `finalize_job_resume` / `finalize_cover_letter`; `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py`, import `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` from `src.utils.config` (same import area as other config constants already used in this module).
2. Locate the success RESPONSE store block (~`if _should_store and raw_text:` that assigns `resp_id = _store_response_block(...)`). Immediately after a successful `resp_id` assignment (still inside the success path where `result` is the successful hop — not failure-audit stores earlier in `do_task`):
   - Resolve `slot = JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK.get(task_key)`.
   - If `slot` is set and `index` is truthy and `resp_id` is a non-empty string: lazy-import `pin_job_artifact_agent_data_id` from `src.core.tracker` (same cycle-break style as the existing `persist_job_artifact_from_parsed` lazy import) and call `pin_job_artifact_agent_data_id(index, slot, resp_id, debug=debug)`.
   - If `slot` is set but pin cannot run (no `index`, no `resp_id`, store exception left `resp_id` unset): when `debug=True`, log skip via the pin helper or a single `debug_detail` with reason (`missing_index` / `missing_resp_id` / `store_failed`) — do **not** call `save_job_data` with a blank id.
3. Placement must be **before** the `if not effective_next:` / `run_next` recurse branch so mid-chain pins fire. Repo `data/admin/agent_task.json` has `finalize_job_resume.run_next = draft_cover_letter` and `finalize_cover_letter.run_next = propose_application_responses` — those hops never enter the current terminal-only body persist.
4. In the terminal block that calls `persist_job_artifact_from_parsed` when `not effective_next`, **remove** the `finalize_job_resume` / `finalize_cover_letter` body-copy path (delete or hard-disable `allow_resume` / `allow_cover` for those keys). Pointer pin from step 2 is the sole write for those hops. Leave `persist_job_artifact_from_parsed` and the PUT helpers intact for manual API / other callers.
5. Do not pin on failure RESPONSE stores (schema/API failure paths that call `_store_response_block` then return `success=False`).
6. Do not add TASK_CONFIG fields. Do not edit UI/API files.

⚠️ **Decision:** Stop `do_task` body-copy for the two finalize hops so `artifacts.cover_letter` is not overwritten by a dict after a pointer string pin (same key). `resume_content` body writes from that terminal path are also stopped for `finalize_job_resume`; the authoritative resume pointer is `job_resume`. Manual `PUT …/artifacts/resume_content` remains for editors until AST-1100 remaps surfaces.

## Self-Assessment

**Scope — `Single-Component`**  
Touches config map + tracker pin helper + `do_task` post-RESPONSE persist; no UI, no schema, no TASK_CONFIG dialect.

**Conf — `high`**  
Reuses existing `_store_response_block` id + `save_job_data` deep-merge artifacts pattern; mid-chain gap is explicit in `agent_task.json` `run_next` and the terminal-only `persist_job_artifact_from_parsed` guard.

**Risk — `Medium`**  
`artifacts.cover_letter` type changes from object to `agent_data_id` string for chain-written jobs — JAR/readers stay broken until AST-1100, which is intentional and blockedBy this ticket. A bad pin (wrong id / skipped mid-chain) leaves UAT surfaces empty.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Status |
|------|--------|
| §1.3 DRY | One pin helper; one config map; no parallel persist framework |
| §1.5.1 debug-contract-gated | Style D only when `debug=True`; no new ungated `[DEBUG]` |
| §2.1 config | Slot/task map in `config.py`; no TASK_CONFIG `persist_in` |
| §2.4.1 entity-agent-responses-latest-only | Pin by RESPONSE `agent_data_id`; body stays in `agent_data`; no entity JSON `agent_responses` revival |
| §2.8 coat-check-never-store-empty | Blank id skips write; prior pointer preserved |
| §3.3 imports | Core → tracker/config; lazy import breaks agent↔tracker cycle |

No conflicts requiring `conf-!!-NONE`.
