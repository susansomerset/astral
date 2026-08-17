# AST-1420 — Job copy snapshot payload (Create a Copy button on the Job Modal)

- **Linear:** [AST-1420](https://linear.app/astralcareermatch/issue/AST-1420/job-copy-snapshot-payload-create-a-copy-button-on-the-job-modal)
- **Parent:** [AST-1419](https://linear.app/astralcareermatch/issue/AST-1419/create-a-copy-button-on-the-job-modal) — Create a Copy button on the Job Modal
- **Publish ref:** `sub/AST-1419/AST-1420-job-copy-snapshot-payload`

Assembles a diagnostic JSON snapshot for one job and serves it on an authenticated jobs route: the full **stored** job record (artifact pins stay ids) plus populated `agent_data` for every id on that record and every latest hop for that job, covering all `BLOCK_TYPES` from config, with pointer rows resolved to referenced content. Does not own the Copy button chrome (AST-1421).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Add public `assemble_job_copy_snapshot`; helpers after it; extend the module header in-scope list | core |
| `src/ui/api/api_jobs.py` | Add `GET /api/jobs/<astral_job_id>/copy` with `@require_auth`; thin wrap of the assembler | ui |

**Do not touch:** `src/data/database.py` (pointer follow on read is already done by `_resolve_agent_data_block_data` / `get_agent_data` / `get_agent_data_for_ids` / `get_agent_data_by_batch`); `hydrate_job_artifacts_for_display`; `get_entity_agent_story`; `GET /api/jobs/<astral_job_id>` detail; React / Copy button (AST-1421); timesheets; dispatch ledger; company record; `tests/**`; `docs/test-bible/**`.

**Betty note (not this ticket’s build):** new coverage for the copy route (401, 404, stored pins not hydrated, pointer content populated, `BLOCK_TYPES` from config) belongs on the test tree after Code Complete.

---

## Snapshot contract (binding)

HTTP: `GET /api/jobs/<astral_job_id>/copy`

- `@require_auth` — missing/invalid session → existing decorator 401 `{"error": "Missing or invalid session credentials"}`.
- Job missing → `404` `{"error": "Not found"}` (same as `detail`).
- Success → `200` `application/json` via `jsonify` of the dict below (compact JSON; AST-1421 pretty-prints with `JSON.stringify(body, null, 2)` for the clipboard). Do not return `text/plain`. Do not `json.dumps(..., indent=2)` in this ticket.

Response shape:

```json
{
  "job": { },
  "agent_data": {
    "<agent_data_id>": {
      "id": "<agent_data_id>",
      "block_type": "RESPONSE",
      "batch_id": "<hop batch_id>",
      "task_key": "<task_key or empty string>",
      "blocks": {
        "SYSTEM": { "id": "<id>", "content": "<resolved plain text>" },
        "CACHE_A": { "id": "<id>", "content": "<resolved plain text>" }
      }
    }
  }
}
```

Rules for that shape:

1. `"job"` is a **copy** of `tracker.get_job(astral_job_id)` as stored: every column the data layer already returns (`astral_job_id`, `company`, `company_job_id`, `job_title`, `job_link`, `job_data`, `state`, `state_history`, `batch_id`, timestamps, `latest_score`, and any other keys `_job_row_to_dict` already includes). Do **not** call `_flatten_grades`. Do **not** call `hydrate_job_artifacts_for_display`. Do **not** attach `agent_story`. Artifact pin strings under `job_data.artifacts` (`job_resume`, `cover_letter`, `proposed_answers`) stay strings (ids), not resolved bodies.
2. `"agent_data"` is keyed by every distinct `agent_data_id` collected in Stage 1 step 3. Each value describes **that id’s hop** (its `batch_id`): `blocks` contains one entry per `block_type` that exists on that batch, keyed with the exact strings in `BLOCK_TYPES` from `src/utils/config.py` (`SYSTEM`, `CACHE_A`, `CACHE_B`, `CACHE_C`, `CACHE_D`, `NO_CACHE`, `TASK`, `RESPONSE`, `FEEDBACK`). Omit a type key when that batch has no row of that type. Do not invent empty content. Do not hardcode the type list — iterate `BLOCK_TYPES`.
3. `content` is the resolved plain-text `block_data` from the existing data-layer readers (pointers already followed). Never leave pointer-row content as null/empty when `ref_agent_data_id` is set and the canonical row has content.
4. If several collected ids share a `batch_id`, each id still gets its own `agent_data` entry; `blocks` may repeat the same hop payload. That keeps “every id that appeared” addressable by id.
5. Do not add timesheets, dispatch ledger rows, or the company record.

⚠️ **Decision:** Wrapper `{job, agent_data}` rather than in-place replacement of pin strings inside `job`. Parent definition requires the stored job body to keep ids; expansion is additive. AST-1421 copies the whole JSON.

⚠️ **Decision:** Do not reuse `get_entity_agent_story`. That path is display hydration (scored RESPONSE filtering, grade/rubric attachment, counter labels). This snapshot is a diagnostic dump of stored job + resolved hop blocks.

---

## Stage 1: Core assembler

**Done when:** `assemble_job_copy_snapshot(astral_job_id, *, debug=False)` returns `None` when the job is missing, and otherwise returns the `{job, agent_data}` dict above: stored pins remain ids; every collected id has populated hop `blocks` with resolved content; debug contract lines emit only when `debug=True`.

1. In `src/core/tracker.py`, add `assemble_job_copy_snapshot` to the module docstring in-scope list (same sentence style as the existing public names). Place the public function after `get_job` (public-then-helpers). Signature:

```python
def assemble_job_copy_snapshot(
    astral_job_id: str,
    *,
    debug: bool = False,
) -> Optional[Dict[str, Any]]:
```

2. Load the job with existing `get_job(astral_job_id)`. If missing, return `None`. Shallow-copy the top-level dict (`dict(job)`) so later work cannot mutate the caller’s row; nested `job_data` / `state_history` stay the parsed objects `get_job` already returned (do not deep-copy unless a later step would mutate nested structures — it must not).

3. Collect distinct agent_data ids (preserve first-seen order; skip empty/whitespace strings) from **both** of these sources, then union:

   a. **Stored-record walk.** Recursively walk the job dict (dicts, lists, strings only; ignore other types). Every non-empty `str` value is a candidate. Batch-resolve with `database.get_agent_data_for_ids(candidates)`. A candidate is an agent_data id only when it is a key in that result map. This picks up artifact pins and any other id string stored on the job without a hardcoded path list.

   b. **Latest hops for this job.** Call `database.list_entity_latest_agent_refs("job", astral_job_id)`. For each ref’s `prompt_blocks`, take every `id`. This is how consult/build hops appear when their ids are not copied into `job_data`. Wrap this call in `try/except Exception`: on failure, log a warning via `logger.warning` (not debug-contract) with `astral_job_id` and the exception, and treat hops as empty — still return the stored job plus any ids from (a). Do not import or call `get_entity_agent_story`.

⚠️ **Decision:** Union of walk + `list_entity_latest_agent_refs` is required. Pins live on the stored job; processing hops live on `agent_data.entity_id`. Either source alone would miss the parent’s “stored job plus the hops that produced it.”

4. If the collected id list is empty, return `{"job": job_copy, "agent_data": {}}`.

5. Resolve hop payloads. For each collected id, in first-seen order:

   - Load the seed row with `database.get_agent_data(id)`. If missing, skip that id (do not put a stub in `agent_data`).
   - Read `batch_id` from the seed row. If `batch_id` is missing/empty, skip that id.
   - Load hop rows with `database.get_agent_data_by_batch(batch_id)` (no `block_type` filter). Cache by `batch_id` so a shared hop is queried once.
   - Build `blocks` as an empty dict, then for each `block_type` in `BLOCK_TYPES` (import from `src.utils.config` — add the import next to the existing config imports in this file): take the **last** row in the batch list whose `block_type` equals that type (batch list is already `ORDER BY created_at`, so last = newest). If none, omit the key. If present, set `blocks[block_type] = {"id": row["agent_data_id"], "content": row.get("block_data") or ""}`. Use `block_data` only (readers already resolve pointers into that field). Do not copy zlib bytes. Do not re-implement `ref_agent_data_id` following.
   - Set `agent_data[id] = {"id": id, "block_type": seed.get("block_type") or "", "batch_id": batch_id, "task_key": seed.get("task_key") or "", "blocks": blocks}`.

6. Per-id / per-batch data-layer exceptions (`ValueError` from a dangling/cyclic pointer, or any other `Exception` from `get_agent_data` / `get_agent_data_by_batch`): log `logger.warning` with `astral_job_id` and the id/batch, skip that id, continue. One corrupt hop must not 500 the snapshot. Do not catch around `get_job` besides the `None` check.

7. Debug (only when `debug=True`): `dbg = get_logger(__name__, debug_flag=True)` (the module already imports `get_logger`).

   - One job-level index header: `func="assemble_job_copy_snapshot"`, `index=1`, `total=1`, `identifier=astral_job_id`, `outcome` = `assembled` if `agent_data` is non-empty else `assembled_no_ids`. Then `debug_detail` with `found_ids=<count> recorded=<count of agent_data keys>`.
   - Then one index header **per collected id** in first-seen order: `func="assemble_job_copy_snapshot"`, `index=i`, `total=len(collected)`, `identifier=<id>`, `outcome` one of `recorded` (entry present), `missing_row` (get_agent_data returned None), `skipped_no_batch`, `skipped_error`. Working detail (`debug_detail`) for recorded ids: `block_type=... batch_id=... task_key=... hop_block_types=<comma-joined keys of blocks in BLOCK_TYPES order>`. For each hop block whose `content` is a string, emit that content with `debug_detail_block(content)` (truncation is inside that helper — do not log full blobs another way). No debug-contract lines when `debug=False`. No `logger.info("[DEBUG] …")`.

8. Helpers (private, after the public function): `_collect_job_string_values(obj) -> List[str]` for the recursive walk in step 3a; `_hop_blocks_for_batch(batch_rows) -> Dict[str, Dict[str, str]]` for the `BLOCK_TYPES` loop in step 5. Do not put these helpers above the public function.

9. Import `BLOCK_TYPES` from `src.utils.config` in this file. Do not add a new config block. Do not add a new core module.

---

## Stage 2: Authenticated jobs route

**Done when:** `GET /api/jobs/<astral_job_id>/copy` with a valid Bearer/session returns the assembler JSON; missing job is 404; unauthenticated is 401; `GET /api/jobs/<id>` detail is unchanged (still hydrates artifacts and attaches `agent_story`).

1. In `src/ui/api/api_jobs.py`, import `assemble_job_copy_snapshot` from `src.core.tracker` (add it to the existing tracker import list). Import `ui_llm_debug` from `src.utils.deploy_status`.

2. Register this route **with the other `/<astral_job_id>/...` routes** (next to `detail` is fine). Path and handler:

```python
@jobs_bp.route("/<astral_job_id>/copy")
@require_auth
def copy_snapshot(astral_job_id):
    """Diagnostic snapshot: stored job plus populated agent_data hops."""
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        snapshot = assemble_job_copy_snapshot(astral_job_id, debug=debug)
    except Exception as exc:
        logger.warning(
            "copy_snapshot failed astral_job_id=%s: %s",
            astral_job_id,
            exc,
        )
        return jsonify({"error": str(exc)}), 500
    if snapshot is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(snapshot)
```

3. Do not add `@require_auth` logic by hand — the decorator is the 401. Do not call `get_entity_agent_story`, `hydrate_job_artifacts_for_display`, or `_flatten_grades` on this route. Do not import `src.data` or `src.external` from this module. Do not add frontend files.

⚠️ **Decision:** `ui_llm_debug` so local deploy (`ASTRAL_DEPLOY_ENV=local`) turns assembler debug on without AST-1421 having to pass `?debug=1`. Explicit `?debug=1|true|yes` still forces it on non-local. Same helper other UI-initiated APIs already use.

---

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1420
**Overall:** APPROVED
**Publish-ref:** `f35edb19b8a9bb26f79920b3656a700590655787`

## Traceability

AC2 → N/A boundary (clipboard/pretty-print is AST-1421); payload JSON body → Stage 1 + Stage 2 · AC3 → Stage 1 (id union + `BLOCK_TYPES` hop blocks) · AC4 → Stage 1 (`block_data` from existing pointer-resolving readers) · AC5 → Stage 2 (`@require_auth` on `GET /api/jobs/<astral_job_id>/copy`)

## Findings

### discuss — Stage 1 step 3b (`list_entity_latest_agent_refs` try/except)

**Location:** Stage 1, step 3b  
**Finding:** On `list_entity_latest_agent_refs` failure, the plan logs a warning and returns stored-job ids only — consult/build hops may be absent from the snapshot.  
**Recommendation:** Acceptable as documented resilience; implement as written. If Susan later wants fail-hard on hop lookup, that is a product call for AST-1421+UAT, not a plan gap.

### discuss — No `## Self-assessment` section

**Location:** Plan doc tail  
**Finding:** Plan lacks the usual confidence/self-assessment block; only `## Estimate` confirm is present.  
**Recommendation:** Optional polish for plan-child template consistency; scope and estimate (3) match the staged work — not blocking.

### acceptable — `database.*` vs `agent.get_agent_data` naming

**Location:** Stage 1 steps 3a/5  
**Finding:** Plan calls `database.get_agent_data` / `database.get_agent_data_by_batch` directly from `tracker.py`, matching existing artifact-resolve usage (`database.get_agent_data(pin_id)` at line 297) and avoiding `agent.get_agent_data(batch_id, …)`’s different signature.  
**Recommendation:** No change.

context_tokens≈52000

## Review (build)

**Built:** `origin/sub/AST-1419/AST-1420-job-copy-snapshot-payload` @ `ffd638d71739050840b9278b8dadaa290100ff90`

Stages 1–2: `assemble_job_copy_snapshot` in tracker (stored job + hop blocks from walk ∪ latest refs, `BLOCK_TYPES`, existing pointer-resolving readers); `GET /api/jobs/<id>/copy` with `@require_auth`. Tests deferred to Betty.

