# AST-1240 — Discard job state and owner-scoped soft delete

**Linear:** [AST-1240](https://linear.app/astralcareermatch/issue/AST-1240/discard-job-state-and-owner-scoped-soft-delete-progress-cancellation)
**Parent:** [AST-1176](https://linear.app/astralcareermatch/issue/AST-1176/progress-cancellation-and-discarding-a-batch) — Progress, cancellation, and discarding a batch
**Publish ref:** `origin/sub/AST-1176/AST-1240-discard-job-state`

Owns the terminal job state for discarded Surfer jobs (absent from every Jobs view allow-list and every dispatch trigger), the authenticated owner-scoped core+HTTP path that moves a batch's jobs into that state without hard-deleting rows, and the pending-classification half of discard so a delivered-but-unresolved page never becomes a visible job after she chose discard. Introduces soft-delete-for-jobs (candidate `DELETED` shape applied to jobs). Does **not** hard-delete (parked **AST-1178**); does **not** own progress UI / copy (**AST-1241**) or the cancel control / keep-or-discard prompt (**AST-1242**); does **not** own batch membership persistence (**AST-1229** / **AST-1169** — consumes it).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `JOB_STATES["DISCARDED"]`; extend `SURFER_BATCH_CONFIG["url_outcomes"]` with `discarded`; assert `DISCARDED` absent from all three Jobs view lists + Skipped section order | utils |
| `src/core/surfer.py` | Add `discard_surfer_batch` + helpers; harden `add_surfer_batch_job` against post-discard association; Style D debug on discard | core |
| `src/ui/api/api_surfer.py` | Authenticated `POST /api/surfer/batches/<batch_id>/discard` (create blueprint file if absent — see Decision) | ui |
| `src/ui/server.py` | Register `surfer_bp` if this ticket creates `api_surfer.py` for the first time on the tip | ui |

**No changes expected:** `src/data/database.py` schema / header inventory (discard is a job `state` value + URL outcome string in existing JSON — confirm, do not invent columns); `claim_job_batch` / `clear_job_batch`; Jobs list/count filters (hiding is free); progress / cancel UI (**AST-1241** / **AST-1242**); `tests/` / bible (Betty after Code Complete); hard-delete / reap (**AST-1178**).

⚠️ **Decision — state name `DISCARDED` (not `DELETED`, not `SURFER_DISCARDED`):** Product language is discard. Candidate soft-delete already uses `DELETED`; reusing that string on jobs would collide in logs and mental model. Unprefixed `DISCARDED` is the tombstone AST-1178 will reap via `job.state_changed_at`.

⚠️ **Decision — `prior_states: None` (unrestricted entry):** Surfer-created jobs may sit in any meteorite / consult / candidate-facing state when she discards. Mirrors candidate `DELETED`. A finite allow-list would rot every time the ladder grows.

⚠️ **Decision — pending race: mark URL outcomes `discarded` + refuse new job association; do not invent a second batch status:** Parent settled both keep and discard end the batch **CANCELLED**. Discard intent is the new terminal URL outcome `discarded` (plus soft-deleted `job_ids`). Classification / batch-scoped intake (**AST-1228** / **AST-1231**) must call `surfer_batch_accepts_new_jobs` (this ticket) before creating or associating a job — consumer contract below. Do **not** add `DISCARDED` as a Surfer batch status.

⚠️ **Decision — hiding stays free:** Do **not** add `DISCARDED` to `IN_REVIEW_STATES`, `SKIPPED_STATES`, `RECOMMENDED_JOB_STATES`, or `JOBS_SKIPPED_SECTION_ORDER`. Parent note: adding filtering code or nav-count arithmetic for this state is a sign it was registered in the wrong list. Config asserts enforce absence.

⚠️ **Decision — `GET /api/jobs/<id>` stays ungated:** Parent flagged this. Nothing in the product links to a discarded job after discard; leave detail fetch as-is. Do not add a state gate on this ticket.

⚠️ **Decision — create `api_surfer.py` if absent:** Same placement rule as AST-1241. If `surfer_bp` already exists on the tip (progress GET from AST-1241), add only the discard route. If absent, create the blueprint + register in `server.py`. Do not invent a second Surfer blueprint.

## Pre-build dependency gate (before Stage 1 code)

**Done when:** Builder can name the live AST-1229 symbols below on the tip after `sync-child.sh` (or confirm they must wait — then STOP, do not invent).

1. `SURFER_BATCH_CONFIG` exists in `src/utils/config.py` with `statuses`, `url_outcomes`, `initial_status`, `initial_url_outcome`.
2. `src/core/surfer.py` exists with public: `transition_surfer_batch_status`, `set_surfer_batch_url_outcome`, `list_surfer_batch_jobs`, `add_surfer_batch_job`, and data access only via `database.get_surfer_batch` / `database.update_surfer_batch` (no core `get_surfer_batch` name).
3. If any of the above are missing after sync (AST-1229 / parent ftr not yet on this line) → **STOP**, comment on **AST-1240** naming the missing symbols and that AST-1169 product (at least AST-1229) must land on the epic line / `origin/dev` before build. Do **not** re-implement the Surfer batch entity and do **not** self-cherry-pick.

## Consumer contract (for AST-1228 / AST-1231 — not implemented here)

Before creating a meteorite/job for a batch-scoped page, or before `add_surfer_batch_job`:

1. Call `surfer_batch_accepts_new_jobs(batch_id, debug=...)` from `src/core/surfer.py`.
2. If it returns `False`: do **not** create a job; do **not** append to `job_ids`; leave/set the URL outcome as already `discarded` (or skip outcome write if already terminal `discarded`). Return the intake envelope without a new job.
3. Re-read immediately before create (discard may race mid-classification).

AST-1242 calls `discard_surfer_batch` (or the HTTP route) only when she chooses **discard**. Keep must **not** call discard.

## Stage 1: `DISCARDED` job state + `discarded` URL outcome

**Done when:** `JOB_STATES["DISCARDED"]` exists with `prior_states is None`; `SURFER_BATCH_CONFIG["url_outcomes"]["discarded"]` exists with `terminal: True`; asserts prove `DISCARDED` is absent from the three Jobs view lists and `JOBS_SKIPPED_SECTION_ORDER`; config import / `py_compile` succeed; no view-list membership and no new dispatch seed rows for `DISCARDED`.

1. In `src/utils/config.py`, in `JOB_STATES`, after the `CANDIDATE_SKIPPED` entry (or immediately after the last candidate-facing job state if that anchor moved), add:

```python
    # AST-1240: Surfer soft-delete tombstone. Not in any Jobs view allow-list.
    # Reap / hard-delete is AST-1178 (uses state_changed_at). prior_states None = discard from any state.
    "DISCARDED": {"prior_states": None},
```

2. Immediately after the existing Jobs view list definitions / skipped-section asserts neighborhood (near the `assert all(k in JOBS_SKIPPED_SECTION_ORDER …)` block is fine; keep with other JOB_STATES view asserts), add:

```python
assert "DISCARDED" in JOB_STATES
assert JOB_STATES["DISCARDED"].get("prior_states") is None
assert "DISCARDED" not in IN_REVIEW_STATES
assert "DISCARDED" not in SKIPPED_STATES
assert "DISCARDED" not in RECOMMENDED_JOB_STATES
assert "DISCARDED" not in JOBS_SKIPPED_SECTION_ORDER
```

3. In `SURFER_BATCH_CONFIG["url_outcomes"]` (AST-1229 block — must exist per pre-build gate), add:

```python
        "discarded": {"terminal": True},  # AST-1240: pending/delivered cancelled by discard; blocks new jobs
```

   Existing AST-1229 asserts over `url_outcomes` values already require a bool `terminal` — no assert rewrite needed beyond confirming `"discarded"` is present:

```python
assert "discarded" in SURFER_BATCH_CONFIG["url_outcomes"]
assert SURFER_BATCH_CONFIG["url_outcomes"]["discarded"]["terminal"] is True
assert SURFER_BATCH_CONFIG["initial_url_outcome"] != "discarded"
```

4. Do **not** add `DISCARDED` to any `data/admin/agent_task.json` (or other) `trigger_state`. Spot-check that no existing seed row already uses the string `DISCARDED` as `trigger_state`; if one does → **STOP** and comment (unexpected collision).

5. `~/astral/.venv/bin/python -m py_compile src/utils/config.py` (or repo venv equivalent).

⚠️ **Decision — do not add `DISCARDED` to Skipped sections:** Config import asserts every `JOBS_SKIPPED_SECTION_ORDER` state has a bulk-retry target. A tombstone must not enter that map.

## Stage 2: Core `discard_surfer_batch` + association gate

**Done when:** Given an owned RUNNING or CANCELLED Surfer batch with `job_ids` and a mix of pending/delivered/success URL outcomes, `discard_surfer_batch` (a) rejects foreign `candidate_id`, (b) marks every non-terminal URL outcome `discarded`, (c) transitions every associated job to `DISCARDED` via `tracker.transition_job_state` (idempotent if already `DISCARDED`), (d) moves the batch to the config cancel status when still non-terminal, (e) re-lists jobs once and transitions any race-created leftovers, (f) with `debug=True` emits Style D index headers + working detail for what was found and what changed; `add_surfer_batch_job` raises when the batch no longer accepts new jobs; `debug=False` emits no Style D; `py_compile` succeeds.

1. In `src/core/surfer.py`, add imports as needed (keep layer rules — core → data/utils/tracker/candidate only; **no** `src.ui`):

```python
from src.core.tracker import transition_job_state
from src.utils.config import SURFER_BATCH_CONFIG, JOB_STATES  # JOB_STATES only if needed for the literal target; prefer constant below
```

   Target state string: read from a module-level constant next to the new public API:

```python
_SURFER_DISCARD_JOB_STATE = "DISCARDED"  # must match JOB_STATES key from Stage 1
```

   At function entry, `assert _SURFER_DISCARD_JOB_STATE in JOB_STATES` is unnecessary if Stage 1 landed; still validate via `transition_job_state` (raises on unknown).

2. Add public helpers **above** helpers section (public-then-helpers):

```python
def surfer_batch_accepts_new_jobs(batch_id: str, *, debug: bool = False) -> bool:
    """False when discard has marked any URL outcome as discarded (AST-1240 gate)."""

def discard_surfer_batch(
    batch_id: str,
    candidate_id: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Owner-scoped soft-delete of Surfer batch jobs + pending URL outcomes.

    Returns:
      {
        "batch": <updated surfer_batch row>,
        "discarded_job_ids": list[str],  # ids successfully moved to DISCARDED this call (incl. already DISCARDED skipped from list or included — see step 6)
        "discarded_url_count": int,      # URLs whose outcome was set to discarded this call
      }

    Raises:
      ValueError: missing batch, blank ids, or candidate_id does not own the batch
                  (.error_code = "surfer_batch_not_owned" when ownership fails;
                   .error_code = "surfer_batch_not_found" when missing).
    """
```

3. `surfer_batch_accepts_new_jobs` behavior (literal):

   - `logger.set_debug_flag(debug)`.
   - `batch = database.get_surfer_batch(batch_id)`; if `None` → raise `ValueError(f"surfer_batch not found: {batch_id}")` with `.error_code = "surfer_batch_not_found"`.
   - Return `False` if any entry in `batch["urls"]` has `str(outcome) == "discarded"` (compare via config: outcome name must be the key present in `SURFER_BATCH_CONFIG["url_outcomes"]` whose purpose is discard — use the literal key `"discarded"` only as the config key name already added in Stage 1; do not invent synonyms).
   - Else return `True`.

4. Harden `add_surfer_batch_job` (existing AST-1229 function): after loading the batch and validating `astral_job_id`, if `not surfer_batch_accepts_new_jobs(batch_id, debug=debug)`:

```python
    err = ValueError(f"surfer_batch {batch_id} has discarded jobs; refusing new association")
    err.error_code = "surfer_batch_jobs_discarded"
    raise err
```

   Then proceed with the existing append logic. Do **not** change the idempotent append behavior when accepts is True.

5. Helper `_cancel_status() -> str` (below public API): return the unique status name in `SURFER_BATCH_CONFIG["statuses"]` where `terminal` is True **and** `requires_all_urls_terminal` is False. If not exactly one match → raise `RuntimeError` (config contract from AST-1229: CANCELLED is that status). Do **not** branch on the literal string `"CANCELLED"` in discard logic.

6. `discard_surfer_batch` behavior (literal order — race-safe):

   - Validate non-empty stripped `batch_id` and `candidate_id`; else `ValueError`.
   - `logger.set_debug_flag(debug)`.
   - Load `batch = database.get_surfer_batch(batch_id)`; missing → `ValueError` + `.error_code = "surfer_batch_not_found"`.
   - Ownership: if `str(batch.get("candidate_id") or "") != candidate_id.strip()` → `ValueError("surfer_batch not owned by candidate")` + `.error_code = "surfer_batch_not_owned"`.
   - **Debug found (batch header):** when `debug=True`, one index header for the batch (`func="surfer.discard_surfer_batch"`, `index=1`, `total=1`, `identifier=batch_id`, `outcome="found"`) and detail lines for `candidate_id`, current `status`, `len(urls)`, `len(job_ids)`, and each URL's current outcome.
   - **Mark pending URLs:** for each URL entry whose outcome is **not** terminal per `_is_terminal_url_outcome`, call `set_surfer_batch_url_outcome(batch_id, url, "discarded", debug=debug)`. Count how many were updated. (Already-terminal `success`/`failed` stay unchanged; their jobs are still soft-deleted via `job_ids`.)
     - Note: `set_surfer_batch_url_outcome` may auto-complete a fully-terminal worklist to COMPLETED while status is still non-terminal. That must **not** win over cancel: after URL marks, if status is still non-terminal, call `transition_surfer_batch_status(batch_id, _cancel_status(), debug=debug)`. If status is already terminal (CANCELLED or COMPLETED), leave status as-is (idempotent discard after AST-1242 cancel).
     - Prefer: mark URLs with a **direct** urls rewrite when auto-complete would fire incorrectly — **required behavior:** after all discard URL marks, batch status must be the cancel status (or already CANCELLED), never left RUNNING, and must not end as COMPLETED because discard filled the worklist with terminal outcomes. Implement by either (a) writing all `discarded` outcomes in one `database.update_surfer_batch(..., urls=...)` without going through `set_surfer_batch_url_outcome`'s auto-complete, then `transition_surfer_batch_status(..., _cancel_status())` if non-terminal, or (b) calling `set_surfer_batch_url_outcome` then forcing cancel if status became COMPLETED or is still RUNNING. **Choose (a)** — single urls write + explicit cancel transition. Do not call `set_surfer_batch_url_outcome` in a loop for discard marks.
   - Concrete (a) steps:
     1. Copy `urls` list; for each entry, if not `_is_terminal_url_outcome(outcome)`, set `outcome="discarded"` and `updated_at` to now (same timestamp format as `set_surfer_batch_url_outcome`).
     2. `database.update_surfer_batch(batch_id, urls=entries)` if any changed.
     3. Reload batch; if status is non-terminal → `transition_surfer_batch_status(batch_id, _cancel_status(), debug=debug)`.
   - **Soft-delete jobs:** `jobs = list_surfer_batch_jobs(batch_id, debug=debug)`. For each job, if `job.get("state") != _SURFER_DISCARD_JOB_STATE`, call `transition_job_state([job_id], _SURFER_DISCARD_JOB_STATE)`. Collect ids transitioned (and optionally ids already discarded — return all associated ids that are `DISCARDED` after the loop as `discarded_job_ids`).
   - **Race sweep:** call `list_surfer_batch_jobs` again; transition any still not `DISCARDED` the same way.
   - **Debug changed:** when `debug=True`, index header `outcome="discarded"` (or `"changed"`) with detail: discarded URL count, discarded job ids, final batch status.
   - Return the dict shape above. Final `batch` from `database.get_surfer_batch(batch_id)`.

7. Do **not** call `clear_job_batch` / touch `job.batch_id`. Do **not** remove ids from `job_ids` (association remains for audit; jobs are soft-deleted). Do **not** hard-delete rows.

8. `~/astral/.venv/bin/python -m py_compile src/core/surfer.py`.

⚠️ **Decision — ownership is `batch.candidate_id == candidate_id`, not Stytch user mapping:** Possession of a batch id alone is insufficient (parent / `astral.patterns.require-auth-on-protected-endpoints`). The route passes the candidate id from the request body; core enforces the match. Admin bypass is **out of scope** — foreign candidate always rejected.

⚠️ **Decision — discard cancels the batch if still running:** AST-1242 is expected to cancel before or when calling discard; this function still transitions to cancel status when non-terminal so a direct API call cannot leave a RUNNING discarded batch (resume safety).

## Stage 3: Authenticated discard route

**Done when:** `POST /api/surfer/batches/<batch_id>/discard` with auth + body `{ "candidate_id": "<owner>" }` returns 200 and the core result shape; missing/invalid session → 401; foreign candidate → 403; unknown batch → 404; missing `candidate_id` → 400; `debug` query/body threads into core; blueprint registered; `py_compile` succeeds.

1. If `src/ui/api/api_surfer.py` does **not** exist on the tip, create it:

```python
"""Surfer candidate-facing API (AST-1240 discard; siblings may add progress/cancel)."""

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.surfer import discard_surfer_batch
from src.utils.deploy_status import ui_llm_debug

surfer_bp = Blueprint("surfer", __name__, url_prefix="/api/surfer")


def _debug_flag() -> bool:
    body = request.get_json(silent=True) or {}
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    return ui_llm_debug(explicit_debug=explicit)
```

   If the file **already** exists (e.g. AST-1241 progress GET), reuse its blueprint, `_debug_flag` (or equivalent), and imports — add only the discard route + `discard_surfer_batch` import.

2. Add route:

```python
@surfer_bp.route("/batches/<batch_id>/discard", methods=["POST"])
@require_auth
def discard_batch(batch_id: str):
    """Owner-scoped soft-delete of jobs under a Surfer batch (AST-1240)."""
    body = request.get_json(silent=True) or {}
    candidate_id = (body.get("candidate_id") or "").strip()
    if not candidate_id:
        return jsonify({"error": "candidate_id required"}), 400
    try:
        result = discard_surfer_batch(
            batch_id, candidate_id, debug=_debug_flag()
        )
    except ValueError as e:
        code = getattr(e, "error_code", None)
        if code == "surfer_batch_not_found":
            return jsonify({"error": str(e), "error_code": code}), 404
        if code == "surfer_batch_not_owned":
            return jsonify({"error": str(e), "error_code": code}), 403
        return jsonify({"error": str(e), "error_code": code}), 400
    return jsonify(result), 200
```

3. If this ticket created `api_surfer.py`, register in `src/ui/server.py` next to the other blueprint imports:

```python
from ui.api.api_surfer import surfer_bp  # noqa: E402
app.register_blueprint(surfer_bp)
```

   If already registered, do not double-register.

4. `~/astral/.venv/bin/python -m py_compile src/ui/api/api_surfer.py src/ui/server.py`.

⚠️ **Decision — thin route, core owns rules:** `pattern.ui.admin-endpoint` (thin + auth; admin blueprint placement does **not** apply). No `ui` → `data` imports.

⚠️ **Decision — HTTP mapping for ownership is 403:** Distinguishes "not yours" from "not found" so AST-1242 / extension can act; do not collapse both to 404 on this ticket (parent AC requires rejection of another candidate's batch — 403 is the rejection).

## Self-Assessment

**Scope:** Single-Component — config tombstone + Surfer core discard/gate + one authenticated Surfer route; no schema migration; no Jobs view filter changes.

**Conf:** Medium — AST-1229 contracts are published and UT on their sub, but this tip may still lack `surfer.py` until 1169 rolls up (pre-build gate); pending-race approach is decided (URL `discarded` + association gate) rather than waiting on unbuilt AST-1228 classification internals.

**Risk:** Medium — a bug that skips the URL mark or the association gate would let classification create visible jobs after discard (parent AC10/13); wrong view-list membership would show tombstones in Jobs UI; ownership miss would allow cross-candidate discard.

## Rules check (plan-child §8)

- **§1.3 DRY:** Discard URL mark is one urls rewrite; job soft-delete loops call existing `transition_job_state`; cancel status from config flag, not a parallel string set.
- **§2.1 config:** `DISCARDED` in `JOB_STATES`; `discarded` in `SURFER_BATCH_CONFIG["url_outcomes"]`; view-list absence asserted; no env literals.
- **§2.4 batch:** Surfer `batch_id` first on core entrypoints; does not overload dispatcher `job.batch_id`; `clear_job_batch` untouched.
- **§2.6 state:** Core decides `DISCARDED` / cancel status; `transition_job_state` enforces priors (`None` = unrestricted); data does not choose the tombstone.
- **§3.3 imports:** UI → core only; core → tracker + database + utils; no ui→data.
- **§3.5 naming:** `discard_surfer_batch`, `surfer_batch_accepts_new_jobs`, route under `/api/surfer/batches/.../discard`.
- **§1.5.1 debug:** Style D only when `debug=True`; found + changed; no data-layer logging.
- **Header inventory:** No new table/column — confirmed soft-delete via existing `job.state` + URLs JSON.
