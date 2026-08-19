# AST-1453 — Persist skipped-job field and state edits

**Linear:** [AST-1453](https://linear.app/astralcareermatch/issue/AST-1453/persist-skipped-job-field-and-state-edits-when-a-job-is-in-a-skipped)  
**Parent:** [AST-1446](https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable)  
**Publish ref:** `sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits`

Authenticated persist for title, link, and job description on jobs whose current `job.state` is in `SKIPPED_STATES`. State changes go through `tracker.transition_job_state` (prior-state enforcement and `state_history`). GET job detail tells the client whether fields are editable and which registered states are legal next. This ticket does not change Job Detail form chrome (sibling AST-1454 / child #2).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Add `legal_job_successor_states` and `persist_skipped_job_edits`; skipped-state gate; title/link/`job_description` writes; optional `transition_job_state` | core |
| `src/ui/api/api_jobs.py` | Attach `fields_editable` + `legal_next_states` on GET detail; add `PUT /api/jobs/<astral_job_id>` | ui |

Do not edit `JobDetailModal.tsx`, `JobsSkipped.tsx`, `src/utils/config.py`, `bulk_state`, `/skip`, `/copy`, candidate_action, artifact PUTs, or `tests/` / `docs/test-bible/**` (Betty).

## Stage 1: Core persist and successor list

**Done when:** `persist_skipped_job_edits` writes title/link/`job_description` only when current `job.state` is in `SKIPPED_STATES`, calls `transition_job_state` for a different requested `state`, and `legal_job_successor_states(from_state)` is exactly the set of `JOB_STATES` keys `transition_job_state` would accept from that `from_state` excluding `from_state` itself. No Flask routes yet.

1. In `src/core/tracker.py`, add this import next to the existing `JOB_STATES` import from `src.utils.config`: `SKIPPED_STATES`. Do not add any other config names.

2. Immediately after `_job_state_matches_prior` (before `write_job_dispatch_hop_label`), add:

```python
def legal_job_successor_states(from_state: str) -> List[str]:
    """JOB_STATES keys that transition_job_state would accept from from_state, excluding from_state."""
    current = (from_state or "").strip()
    out: List[str] = []
    for name, cfg in JOB_STATES.items():
        if name == current:
            continue
        if _job_state_matches_prior(current, cfg.get("prior_states")):
            out.append(name)
    return out
```

⚠️ **Decision:** Include unrestricted-entry states (`prior_states is None`: `NEW`, `FAILED_TECHNICAL`, `METEORITE_NEW`, `ERROR_QUALIFY_JOB_LISTINGS`, `ERROR_EVALUATE_JD`). Those hops are legal under existing `transition_job_state` / `_job_state_matches_prior`. Do not invent a narrower operator allowlist. Do not put a parallel successor list in config or TypeScript.

3. Immediately after `legal_job_successor_states`, add `persist_skipped_job_edits` with this contract:

- Signature: `persist_skipped_job_edits(astral_job_id: str, fields: Dict[str, Any]) -> Dict[str, Any]`
- Load the job via `get_job`. If missing, raise `ValueError(f"Job not found: {astral_job_id}")`.
- If `(job.get("state") or "")` is not in `SKIPPED_STATES`, raise `ValueError("Job is not in a skipped state")`. Below-dispatch-floor jobs whose state is not in `SKIPPED_STATES` fail this check (parent: not unlocked).
- Allowed keys in `fields`: `job_title`, `job_link`, `job_description`, `state`. Ignore any other key.
- If `job_title` is in `fields`: `title = (fields["job_title"] if fields["job_title"] is not None else "")` then `title = str(title).strip()`. If `title` is empty, raise `ValueError("job_title required")`.
- If `job_link` is in `fields`: same strip; empty → `ValueError("job_link required")`.
- If `job_description` is in `fields`: coerce with `"" if fields["job_description"] is None else str(fields["job_description"])` (do **not** strip the whole blob; persist the operator string, including empty). Write via `save_job_data(astral_job_id, {jd_key: text})` where `jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]`. Do **not** call `get_job_data` (that coat-check scrapes).
- If `job_title` and/or `job_link` were provided, call `save_job(astral_job_id, **col)` with only the provided column kwargs. If `save_job` returns `False`, raise `ValueError("job identity collision")`. If `sqlite3.IntegrityError` is raised and `_is_job_identity_unique_violation(exc)` is true, raise `ValueError("job identity collision")`; otherwise re-raise.
- If `state` is in `fields`: `to_state = str(fields["state"] or "").strip()`. If `to_state` is empty, raise `ValueError("state required")`. If `to_state != (job.get("state") or "")`, call `transition_job_state([astral_job_id], to_state)` (do not catch `ValueError` here — caller maps HTTP). Same-state is a no-op (do not append `state_history`).
- Apply column/JD writes **before** the transition so a later illegal hop still keeps field edits.
- Return `get_job(astral_job_id)` after writes (must not be `None`; if it is, raise `ValueError(f"Job not found: {astral_job_id}")`).
- Do not log. Do not dispatch, scrape, or consult.

4. Do not change `transition_job_state`, `bulk_state` callers, or `JOB_STATES` / `SKIPPED_STATES` contents.

## Stage 2: GET meta + PUT persist

**Done when:** `GET /api/jobs/<id>` includes `fields_editable` (bool) and `legal_next_states` (list of strings) on every found job; `PUT /api/jobs/<id>` with `@require_auth` persists skipped-job edits through `persist_skipped_job_edits` and returns the same detail shape as GET (including agent_story flatten). Non-skipped PUT is 409. Illegal `state` is 409. Missing job is 404. Unauthenticated is 401 via existing decorator. No React files changed.

1. In `src/ui/api/api_jobs.py`, import `legal_job_successor_states` and `persist_skipped_job_edits` from `src.core.tracker` (same import block as `transition_job_state`). `SKIPPED_STATES` is already imported.

2. Add this helper above `list_view` (after `_flatten_grades`):

```python
def _attach_skipped_edit_meta(job: dict) -> dict:
    state = job.get("state") or ""
    editable = state in SKIPPED_STATES
    job["fields_editable"] = editable
    job["legal_next_states"] = legal_job_successor_states(state) if editable else []
    return job
```

3. In `detail`, after `_flatten_grades(job)` and before the artifacts hydrate, call `_attach_skipped_edit_meta(job)`. Keep agent_story try/except unchanged. Do **not** attach these keys on list_view rows.

4. Register `PUT` on the same path as GET, after `detail` and before `/copy`:

```python
@jobs_bp.route("/<astral_job_id>", methods=["PUT"])
@require_auth
def persist_skipped_edits(astral_job_id):
```

Body: `request.get_json(force=True) or {}`. Allowed keys: `job_title`, `job_link`, `job_description`, `state`. Build `fields = {k: data[k] for k in ("job_title", "job_link", "job_description", "state") if k in data}`. If `fields` is empty, return `jsonify({"error": "No valid fields to update"}), 400`.

Call `get_job(astral_job_id)` first; if missing, `jsonify({"error": "Not found"}), 404` (do not call persist). Then:

```python
    try:
        persist_skipped_job_edits(astral_job_id, fields)
    except ValueError as exc:
        msg = str(exc)
        if msg == "Job is not in a skipped state" or msg.startswith("Invalid transition") or msg == "job identity collision":
            return jsonify({"error": msg}), 409
        if "not in allowed list" in msg:
            return jsonify({"error": msg}), 409
        return jsonify({"error": msg}), 400
```

After success, reuse the GET `detail` body: call `detail(astral_job_id)` **or** duplicate the GET assembly (flatten, `_attach_skipped_edit_meta`, artifact hydrate, agent_story try/except, `jsonify(job)`). Prefer calling the existing `detail` function so the response shape cannot drift.

⚠️ **Decision:** Put persist on `jobs_bp` `PUT /api/jobs/<id>` with `@require_auth`, not `api_admin.py`. Job Detail is already an authenticated jobs surface (`skip`, `copy`, GET). `pattern.ui.admin-endpoint` here means auth + thin API + eligibility in the API, not the admin blueprint.

⚠️ **Decision:** 409 for not-skipped and illegal/unknown target state (same family as `POST .../skip`); 400 for empty title/link/state string and empty body.

5. Do not change `/bulk_state`, `/skip`, `/copy`, artifact PUTs, or `candidate_action`. Do not auto-re-run consult, scrape, or dispatch after save.

## Estimate

Confirm Chuckles estimate: 3 — agree
