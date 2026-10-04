# AST-1974 — Jobs list partition, views, skip, and nav config

- **Ticket:** [AST-1974](https://linear.app/astralcareermatch/issue/AST-1974)
- **Parent:** [AST-1970 — Jobs Navigation changes](https://linear.app/astralcareermatch/issue/AST-1970)
- **Publish ref:** `sub/AST-1970/AST-1974-jobs-nav` (origin only)
- **Canon Scope:** `stat.logging.info.api`, `stat.logging.error`

Backend half of the Jobs nav re-cut. The Jobs sidebar becomes six lists — Ready, Review, Applied,
Processing, Skipped, Meteorites — that between them show every job exactly once. This ticket
adds the Ready / Review state lists, moves `ERROR_BUILD_ARTIFACTS` and `BUILD_FAILED` into
Skipped, guards the four explicit lists against overlap, makes Processing the complement of
those four (never a typed-out list), derives `CANDIDATE_SKIPPED`'s prior states from the
Applied / Skipped lists, adds a core skip that releases a held batch claim, swaps the
`view=` branches, deletes the Applied repair-on-read loop that crashes for real candidates,
emits all six nav counts, reshapes the state-UI manifest jobs block, and carries each
meteorite's landed-job state on the Meteorites list API. No React file is touched —
[AST-1975](https://linear.app/astralcareermatch/issue/AST-1975) and
[AST-1976](https://linear.app/astralcareermatch/issue/AST-1976) own the frontend.

## Scope gate

Every row below is in this ticket's `## Scope` Component list, and every change is the kind
its Technical scope describes for that file. No file outside the six is touched.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `list_jobs` / `count_jobs` gain `exclude_states`; `list_meteorites_for_candidate` returns `job_state` via `astral_job_id` | data |
| `src/core/tracker.py` | `list_jobs` / `count_jobs` facades forward `exclude_states`; new `candidate_skip_job` | core |
| `src/utils/config.py` | Ready / Review lists replace `RECOMMENDED_JOB_STATES`; Skipped + section order / labels / bulk-retry gain two build-failure states; disjointness guard + derived exclusion list; derived skip priors; Processing sections replace In Review sections; manifest jobs block reshaped; meteorite sub-section constant removed; Meteorites column added; Jobs `NAV_CONFIG` replaced | utils |
| `src/ui/api/api_jobs.py` | `view=ready|review|processing` replace `in_review|recommended|responded`; Applied helper + repair loop deleted; skip route delegates to core + one completion info line | ui |
| `src/ui/api/api_system.py` | `_get_job_counts` emits six counts | ui |
| `src/ui/api/api_meteorite.py` | `_LIST_KEYS` gains `job_state` | ui |

## Contract for AST-1975 / AST-1976 (frontend consumers)

These names are decided here so the sibling plans can bind to them:

- **Manifest `jobs` block** (`GET /api/state_ui_manifest`):
  - `jobs.in_review_sections` is **renamed** `jobs.processing_sections` — same row shape
    `{state, label}`; today's In Review rows plus `{"state": "BUILD_ARTIFACTS", "label": "Building Artifacts"}` appended last.
  - `jobs.recommended.sections` is now exactly
    `[{"state": "RECOMMENDED", "label": "Review"}, {"state": "CANDIDATE_REVIEW", "label": "Ready"}]`
    (the `BUILD_ARTIFACTS` "In Progress" row moves to Processing).
  - `jobs.recommended.meteorite_section` is **removed**.
  - `jobs.recommended.primary_actions_by_state` is unchanged (keeps the `BUILD_ARTIFACTS` Cancel entry — the report modal uses it).
  - Everything else in `jobs.*` (`skipped`, `detail`, `grade_*`, `recommended.report_*`, `recommended.phase_score_*`) keeps its key; `skipped.section_order` / `section_labels` / `bulk_retry_to_state_by_from_state` gain the two build-failure states.
- **List API:** `GET /api/jobs?view=ready|review|applied|processing|skipped&candidate_id=X`. The default when `view` is omitted is `ready`.
- **Meteorites list API:** each `meteorites[]` row gains `job_state` (the landed job's current `job.state`, or `null` when `astral_job_id` is null or the job row is gone). `columns` gains `{"key": "job_state", "label": "Job State", "sortable": True}` right after the `astral_job_id` ("Job") column.

## Stage 1: Data and core — exclusion filter, landed-job state, core skip

**Done when:** `tracker.list_jobs(exclude_states=[...], candidate_id=X)` returns only rows whose state is outside the list, `count_jobs` with the same args matches its length, `list_meteorites_for_candidate(X)` rows carry `job_state`, and `tracker.candidate_skip_job` exists. Nothing calls the new pieces yet; the app still imports.

1. In `src/data/database.py`, `list_jobs` (currently line ~2321): add a final parameter `exclude_states: Optional[List[str]] = None`. Inside `_with_conn`, immediately after the existing `if states:` block, add the same shape `list_companies` uses:
   ```python
   if exclude_states:
       clauses.append(f"state NOT IN ({','.join('?' for _ in exclude_states)})")
       params.extend(exclude_states)
   ```
   Update the docstring first line to `"""List jobs with optional state IN / NOT IN filters and required candidate_id scope (AST-1598)."""` (keep the remaining docstring lines).
2. In `src/data/database.py`, `count_jobs` (currently line ~2357): add the same final parameter `exclude_states: Optional[List[str]] = None` and the same `NOT IN` block right after its `if states:` block. Docstring unchanged.
3. In `src/data/database.py`, `list_meteorites_for_candidate` (currently line ~4171): inside `_with_conn`, call `_ensure_job_schema(conn)` right after `_ensure_meteorite_schema(conn)`, and replace the query with:
   ```python
   rows = conn.execute(
       """SELECT m.*, j.state AS job_state FROM meteorite m
          LEFT JOIN job j ON j.astral_job_id = m.astral_job_id
          WHERE m.candidate_id = ?
          ORDER BY m.state_changed_at DESC""",
       (cid,),
   ).fetchall()
   ```
   Update the docstring to `"""Return all meteorite rows for candidate_id, newest state_changed_at first; job_state = landed job's current state (None when unlanded)."""`. In the module docstring (line ~12) change `candidate-scoped listing via \`list_meteorites_for_candidate(candidate_id)\`` to `candidate-scoped listing via \`list_meteorites_for_candidate(candidate_id)\` (+ landed \`job_state\`, AST-1974)`.

   ⚠️ **Decision:** Key name `job_state` (not `state`) — `meteorite.state` already exists on the row and must not be shadowed. A `LEFT JOIN` keeps unlanded rows. The other caller (`src/core/meteorite.py` `_landed_peers_for_candidate`) reads only `id` / `state`, so the extra key is inert there.
4. In `src/core/tracker.py`, the `list_jobs` facade (currently line ~1578): add final parameter `exclude_states: Optional[List[str]] = None` and forward it: `return database.list_jobs(states=states, candidate_id=candidate_id, order_by=order_by, exclude_states=exclude_states)`.
5. In `src/core/tracker.py`, the `count_jobs` facade (currently line ~1586): add final parameter `exclude_states: Optional[List[str]] = None` and forward it: `return database.count_jobs(states=states, candidate_id=candidate_id, exclude_states=exclude_states)`.
6. In `src/core/tracker.py`, directly after `cancel_artifact_build` (currently ends line ~1039), add:
   ```python
   def candidate_skip_job(astral_job_id: str) -> str:
       """Candidate Skip: any state CANDIDATE_SKIPPED admits → CANDIDATE_SKIPPED; release a held batch claim first (AST-1974)."""
       job = get_job(astral_job_id)
       if not job:
           raise ValueError(f"Job not found: {astral_job_id}")
       state = job.get("state") or ""
       # Legality first so an illegal skip (e.g. CANDIDATE_APPLIED) never drops a live claim.
       if not job_state_admits_transition(state, "CANDIDATE_SKIPPED"):
           raise ValueError(f"Invalid transition: {state} -> CANDIDATE_SKIPPED")
       # Same lock release cancel_artifact_build does; a running chain hop can't land on a skipped job.
       if job.get("batch_id"):
           database.clear_job_batch_lock(astral_job_id)
       transition_job_state([astral_job_id], "CANDIDATE_SKIPPED")
       return "CANDIDATE_SKIPPED"
   ```
   `job_state_admits_transition` and `transition_job_state` are defined later in the same module; that is fine (resolved at call time). **No** `logger.info` in this function (`stat.logging.info.api` — core adds none).

   ⚠️ **Decision:** Name `candidate_skip_job`, not `skip_job` — `api_jobs.py` already has a route function named `skip_job`, and importing a same-named core function into that module would shadow it.

   ⚠️ **Decision:** Skip does **not** call `clear_job_build_artifacts`. The Technical scope says the core skip clears the batch lock and transitions — nothing more. Partial artifacts on a skipped build stay on the row; `cancel_artifact_build` (→ RECOMMENDED) is unchanged and still clears them.
7. Verify: `python3 -m py_compile src/data/database.py src/core/tracker.py` and `PYTHONPATH=src:. ~/astral/.venv/bin/python -c "import src.core.tracker"` both exit 0.

## Stage 2: Config — state model (additive; nothing removed yet)

**Done when:** `python -c "import src.utils.config"` exits 0; `READY_JOB_STATES`, `REVIEW_JOB_STATES`, `JOBS_PROCESSING_EXCLUDED_STATES` exist; `SKIPPED_STATES` contains `ERROR_BUILD_ARTIFACTS` and `BUILD_FAILED`; `JOB_STATES["CANDIDATE_SKIPPED"]["prior_states"]` is computed. Old constants (`IN_REVIEW_STATES`, `RECOMMENDED_JOB_STATES`, `JOBS_RECOMMENDED_METEORITE_SECTION`) still exist so the API modules keep importing.

1. In `src/utils/config.py`, directly **above** `RECOMMENDED_JOB_STATES` (currently line ~3389), add:
   ```python
   # AST-1974: Jobs → Ready / Review lists (two of the four explicit lists; Processing is their complement).
   READY_JOB_STATES = ["CANDIDATE_REVIEW"]
   REVIEW_JOB_STATES = ["RECOMMENDED"]
   ```
2. In `src/utils/config.py`, `SKIPPED_STATES` (currently line ~3949): insert a line `"ERROR_BUILD_ARTIFACTS", "BUILD_FAILED",` immediately before `"CANDIDATE_SKIPPED",`.
3. Directly after the closing `]` of `SKIPPED_STATES`, add:
   ```python
   # AST-1974: Ready + Review + Applied + Skipped — Processing = every job state NOT IN this list.
   # Derived, never typed out; the assert keeps the four lists pairwise disjoint (each job on exactly one list).
   JOBS_PROCESSING_EXCLUDED_STATES = [*READY_JOB_STATES, *REVIEW_JOB_STATES, *APPLIED_JOB_STATES, *SKIPPED_STATES]
   assert len(JOBS_PROCESSING_EXCLUDED_STATES) == len(set(JOBS_PROCESSING_EXCLUDED_STATES)), "Jobs lists overlap"

   # AST-1974: Skip is legal from every job state not already Applied or Skipped (hop labels / _RETRY
   # resolve through their base in _job_state_matches_prior / state_prior_states).
   JOB_STATES["CANDIDATE_SKIPPED"]["prior_states"] = [
       s for s in JOB_STATES if s not in APPLIED_JOB_STATES and s not in SKIPPED_STATES
   ]
   ```
4. In the `JOB_STATES` literal (currently line ~2615), replace
   `"CANDIDATE_SKIPPED":      {"prior_states": ["CANDIDATE_REVIEW", BUILD_ARTIFACTS_BASE_STATE, "RECOMMENDED"]},`
   with
   `"CANDIDATE_SKIPPED":      {"prior_states": []},  # AST-1974: derived after SKIPPED_STATES (Applied/Skipped complement)`.

   ⚠️ **Decision:** Post-assignment after `SKIPPED_STATES` rather than moving `APPLIED_JOB_STATES` / `SKIPPED_STATES` above `JOB_STATES` — a derivation has to run after the registry literal anyway, and nothing between the literal and `SKIPPED_STATES` reads `CANDIDATE_SKIPPED`'s priors at import (checked: the only import-time `prior_states` read there is the `BOT_BLOCKED` assert). Resulting set = today's three (`CANDIDATE_REVIEW`, `BUILD_ARTIFACTS`, `RECOMMENDED`) plus every pipeline state.
5. `JOBS_SKIPPED_SECTION_ORDER` (currently line ~4036): insert `"ERROR_BUILD_ARTIFACTS",` and `"BUILD_FAILED",` as the **first two** entries (before `"FAILED_LIKE"`). The list runs latest pipeline stage first; build is later than LIKE.
6. `JOBS_SKIPPED_SECTION_LABELS` (currently line ~4070): add `"ERROR_BUILD_ARTIFACTS": "Error Build Artifacts",` and `"BUILD_FAILED": "Build Failed",` as the first two entries.
7. `JOBS_SKIPPED_BULK_RETRY_TO_STATE` (currently line ~4165): add a group at the top:
   ```python
   # AST-1974: artifact build failures — each state's only legal successor.
   "ERROR_BUILD_ARTIFACTS": "RECOMMENDED",
   "BUILD_FAILED": "CANDIDATE_REVIEW",
   ```
   The existing asserts below the dict (keys ⊆ section order; key set == section order minus `CANDIDATE_SKIPPED`; keys / values in `JOB_STATES`) must still pass unchanged.
8. Verify: `python3 -m py_compile src/utils/config.py`; `~/astral/.venv/bin/python -c "import src.utils.config as c; assert 'CANDIDATE_REVIEW' in c.JOB_STATES['CANDIDATE_SKIPPED']['prior_states']; assert 'CANDIDATE_APPLIED' not in c.JOB_STATES['CANDIDATE_SKIPPED']['prior_states']; assert 'ERROR_BUILD_ARTIFACTS' not in c.JOB_STATES['CANDIDATE_SKIPPED']['prior_states']"` exits 0; `PYTHONPATH=src:. ~/astral/.venv/bin/python -c "import src.ui.api.api_jobs, src.ui.api.api_system, src.ui.api.api_meteorite"` exits 0.

## Stage 3: Views, nav, manifest, and Meteorites column — swap and remove old

**Done when:** the backend AC (1–10, and AC 11/12 for `config.py` + `src/ui/api`) hold: `GET /api/nav_config` shows the six Jobs items with counts; `view=ready|review|applied|processing|skipped` partition the candidate's jobs; skip works from Processing states and logs one line; `rg -n "jobs/in_review|jobs/recommended|jobs/responded" src/utils/config.py src/ui/api` and `rg -n "candidate_id=None" src/ui/api/api_jobs.py` and `rg -n "meteorite_section|JOBS_RECOMMENDED_METEORITE_SECTION|IN_REVIEW_STATES|RECOMMENDED_JOB_STATES" src --glob '!src/ui/frontend/**'` return nothing.

### config.py

1. Delete `RECOMMENDED_JOB_STATES` and its comment line (currently line ~3388–3389).
2. Change the assert under `JOBS_RECOMMENDED_PRIMARY_ACTIONS` (currently line ~3459) to:
   ```python
   # BUILD_ARTIFACTS Cancel stays — the report modal still offers it on a running build.
   assert all(
       state in (*READY_JOB_STATES, *REVIEW_JOB_STATES, BUILD_ARTIFACTS_BASE_STATE)
       for state in JOBS_RECOMMENDED_PRIMARY_ACTIONS
   )
   ```
   `READY_JOB_STATES` / `REVIEW_JOB_STATES` are defined above this point (Stage 2 step 1).
3. Delete `IN_REVIEW_STATES` and its comment line `# Ordered state lists for Jobs UI views ...` (currently line ~3556–3565). In the comment block below it (line ~3568) change `(see api_jobs skipped / in_review)` to `(see api_jobs skipped / processing)`.
4. Rename `JOBS_IN_REVIEW_UI_SECTIONS` → `JOBS_PROCESSING_UI_SECTIONS` (only defined at line ~3975 and read in `build_state_ui_manifest`). Append one row at the end of the list: `{"state": BUILD_ARTIFACTS_BASE_STATE, "label": "Building Artifacts"},`. Directly after the list add:
   ```python
   # Processing rows must never name a state that lives on one of the four explicit lists.
   assert not any(row["state"] in JOBS_PROCESSING_EXCLUDED_STATES for row in JOBS_PROCESSING_UI_SECTIONS)
   ```
   (Mid-chain `BUILD_ARTIFACTS.<task>` rows have no section of their own; the frontend's existing legacy-state fallback labels them — AST-1975.)
5. `JOBS_RECOMMENDED_UI_SECTIONS` (currently line ~4009): replace the three rows with
   ```python
   {"state": "RECOMMENDED", "label": "Review"},
   {"state": "CANDIDATE_REVIEW", "label": "Ready"},
   ```
   and change its assert (currently line ~4034) to `assert all(row["state"] in (*READY_JOB_STATES, *REVIEW_JOB_STATES) for row in JOBS_RECOMMENDED_UI_SECTIONS)`.
6. Delete `JOBS_RECOMMENDED_METEORITE_SECTION`, its three asserts, and its two-line `# AST-1052 / AST-1057 ...` comment (currently lines ~4012–4026).
7. In `build_state_ui_manifest` (currently line ~4208):
   - delete the two lines building `in_review_allowed` / `in_review_sections`;
   - delete the `recommended_sections = [...]` comprehension;
   - in the returned dict, replace `"in_review_sections": in_review_sections,` with `"processing_sections": list(JOBS_PROCESSING_UI_SECTIONS),`;
   - replace `"sections": recommended_sections,` with `"sections": list(JOBS_RECOMMENDED_UI_SECTIONS),`;
   - delete the whole `"meteorite_section": {...},` entry.
8. `JOBS_METEORITES_LIST_COLUMNS` (currently line ~3491): insert `{"key": "job_state", "label": "Job State", "sortable": True},` immediately after the `astral_job_id` ("Job") entry.
9. `NAV_CONFIG` Jobs group (currently line ~5617): replace the `items` list with exactly
   ```python
   {"label": "Ready", "path": "/jobs/ready"},
   {"label": "Review", "path": "/jobs/review"},
   {"label": "Applied", "path": "/jobs/applied"},
   {"label": "Processing", "path": "/jobs/processing"},
   {"label": "Skipped", "path": "/jobs/skipped"},
   {"label": "Meteorites", "path": "/jobs/meteorites"},
   ```
   (The `SYNC` comment above stays — AST-1975 adds the matching routes.)

### api_jobs.py

10. Imports: remove `IN_REVIEW_STATES`, `RECOMMENDED_JOB_STATES`, and `METEORITE_CONFIG` from the `src.utils.config` import; add `JOBS_PROCESSING_EXCLUDED_STATES`, `READY_JOB_STATES`, `REVIEW_JOB_STATES`. In the `src.core.tracker` import add `candidate_skip_job`. Keep `get_company` / `update_company` (still used by `candidate_action`). Remove `transition_job_state` from the tracker import **only if** `rg -n "transition_job_state" src/ui/api/api_jobs.py` shows no remaining use after step 13 (today `bulk_state` still uses it — so it stays).
11. Delete `_list_applied_jobs_for_candidate` entirely (currently lines ~111–146).
12. Replace the body of `list_view` (currently line ~151) with:
    ```python
    """List jobs filtered by view.

    Query params:
      view: ready | review | applied | processing | skipped
      candidate_id: scope to one candidate
    """
    view = request.args.get("view", "ready")
    candidate_id = request.args.get("candidate_id")

    if view == "ready":
        rows = list_jobs(states=list(READY_JOB_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "review":
        rows = list_jobs(states=list(REVIEW_JOB_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "applied":
        # job.candidate_id scoping (AST-1598) covers every Applied row; no company-linkage repair.
        rows = list_jobs(states=list(APPLIED_JOB_STATES), candidate_id=candidate_id, order_by="state_changed_at")
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "processing":
        # Complement of the four explicit lists — never an include-list (AST-1974).
        rows = list_jobs(
            exclude_states=list(JOBS_PROCESSING_EXCLUDED_STATES),
            candidate_id=candidate_id,
            order_by="state_changed_at",
        )
        if candidate_id:
            # Below-floor rows are virtual skips — they show on Skipped only.
            floors = score_floor_by_trigger_for_candidate(candidate_id)
            if floors:
                rows = [r for r in rows if not job_misses_dispatch_score_floor(r, floors)]
        return jsonify([_flatten_grades(r) for r in rows])
    elif view == "skipped":
        ...  # existing skipped branch body, unchanged
    else:
        return jsonify([])
    ```
    The `skipped` branch body is copied verbatim from today's code. No `logger.info` anywhere in `list_view`.

    ⚠️ **Decision:** Default `view` is `ready` (first nav list), replacing the removed `in_review` default.
13. Replace the body of `skip_job` (route `/<astral_job_id>/skip`, currently line ~445) with:
    ```python
    """Candidate Skip from any non-Applied, non-Skipped state → CANDIDATE_SKIPPED; core releases a held batch claim."""
    job = get_job(astral_job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    try:
        candidate_skip_job(astral_job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    logger.info(
        "%s | api %s completed: POST %s",
        job.get("candidate_id") or "-",
        f"/api/jobs/{astral_job_id}/skip",
        200,
    )
    return jsonify({"ok": True})
    ```
    This is the only `logger.info` added under `src/ui/api` (`stat.logging.info.api`: one line at the completing POST route; 404 / 409 are not completions and log nothing).

### api_system.py

14. Imports from `src.utils.config`: remove `IN_REVIEW_STATES` and `RECOMMENDED_JOB_STATES`; add `APPLIED_JOB_STATES`, `JOBS_PROCESSING_EXCLUDED_STATES`, `READY_JOB_STATES`, `REVIEW_JOB_STATES` (keep `SKIPPED_STATES`).
15. Replace the `try:` body of `_get_job_counts` (currently line ~85) with:
    ```python
    from src.core.tracker import count_jobs, count_jobs_below_dispatch_score_floor
    from src.data.database import list_meteorites_for_candidate

    below = count_jobs_below_dispatch_score_floor(candidate_id)
    return {
        "/jobs/ready": count_jobs(states=list(READY_JOB_STATES), candidate_id=candidate_id),
        "/jobs/review": count_jobs(states=list(REVIEW_JOB_STATES), candidate_id=candidate_id),
        "/jobs/applied": count_jobs(states=list(APPLIED_JOB_STATES), candidate_id=candidate_id),
        # Below-floor rows render on Skipped, not Processing (mirrors api_jobs list_view).
        "/jobs/processing": count_jobs(
            exclude_states=list(JOBS_PROCESSING_EXCLUDED_STATES), candidate_id=candidate_id
        ) - below,
        "/jobs/skipped": count_jobs(states=list(SKIPPED_STATES), candidate_id=candidate_id) + below,
        # Same read the Meteorites list uses, so the badge equals the list length.
        "/jobs/meteorites": len(list_meteorites_for_candidate(candidate_id)),
    }
    ```
    The `except` block is unchanged.

    ⚠️ **Decision:** Meteorites count = `len(list_meteorites_for_candidate(...))`, not a new `COUNT(*)` helper — the Technical scope gives `database.py` no meteorite count function, and reusing the list read guarantees AC 10 (badge == list length). `src/ui/api` already imports this function directly from `src.data.database` (`api_meteorite.py`).

    ⚠️ **Decision:** Processing/Skipped below-floor arithmetic is today's In Review/Skipped rule, unchanged. It is exact as long as every dispatch trigger state with a score floor is a Processing state — true for every trigger the pipeline uses (generation from `RECOMMENDED` is UI-only, `start_artifact_build`). A hand-made dispatch row triggering on a Review / Skipped state would already double-show today; not widened here.

### api_meteorite.py

16. `_LIST_KEYS` (currently line ~30): add `"job_state"` after `"astral_job_id"`. The route body and its single `logger.exception` handler are unchanged — the new read happens inside `list_meteorites_for_candidate`, already inside the handler's `try` (`stat.logging.error`: one `logger.exception` with live facts, no re-raise).

### Verify

17. `python3 -m py_compile src/utils/config.py src/data/database.py src/core/tracker.py src/ui/api/api_jobs.py src/ui/api/api_system.py src/ui/api/api_meteorite.py` exits 0.
18. `PYTHONPATH=src:. ~/astral/.venv/bin/python -c "import src.utils.config, src.ui.api.api_jobs, src.ui.api.api_system, src.ui.api.api_meteorite"` exits 0.
19. The three `rg` checks in this stage's **Done when** return nothing, and `git diff origin/dev -- src/ui/api | rg "^\+.*logger\.info"` shows exactly one line (the skip route).

## Notes for QA (Betty — not edited by this ticket)

Existing tests that reference removed / renamed backend symbols and will need Betty's attention:
`tests/component/utils/test_config.py`, `tests/component/ui/api/test_api_system.py`,
`tests/component/ui/api/test_api_jobs.py` (`IN_REVIEW_STATES`, `RECOMMENDED_JOB_STATES`,
`JOBS_RECOMMENDED_METEORITE_SECTION`, `view=in_review` / `view=recommended`,
`_list_applied_jobs_for_candidate`, manifest `in_review_sections` / `meteorite_section`).
Frontend fixtures (`stateUiManifestFixture.ts`, `test_StateUiContext`, `test_JobsRecommended`,
`test_JobsInReview`) follow AST-1975.

## Estimate

Confirm Chuckles estimate: 5 — agree
