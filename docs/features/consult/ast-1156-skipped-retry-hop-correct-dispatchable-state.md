# AST-1156 — Skipped Retry → hop-correct dispatchable state (all rubric tasks)

**Linear:** [AST-1156](https://linear.app/astralcareermatch/issue/AST-1156/skipped-retry-hop-correct-dispatchable-state-all-rubric-tasks)  
**Parent:** [AST-1150](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt) — Technical fail for Do prompt  
**Project:** Astral Consult  
**Publish ref:** `sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`

Replace the Skipped page’s hard-coded `bulk_retry_to_state: NEW` with a config-owned **from-state → claimable trigger** map so Retry restores family- and hop-correct dispatchable states for every rubric fail/technical Skipped section (meteorite and regular). After Retry, Scheduled Actions Avail must be **> 0** on the matching dispatch task (e.g. meteorite Do fail → `METEORITE_PASSED_JD` for `grade_do`, not plain `NEW` with Avail 0).

**Non-goals:** Grade completeness contracts (AST-1154). Incomplete-grade → retry holding routing (AST-1155). Rubric content / `_render_score` math. Redesigning Skipped UI beyond Retry destination resolution. `CANDIDATE_SKIPPED` Resurrect (already separate). Betty test-tree / bible edits.

**Depends on:** AST-1154 + AST-1155 (Linear blockedBy). Parent ftr `origin/ftr/AST-1150-technical-fail-for-do-prompt` already carries both — merge it on checkout before build (authoritative segment, not bare `ftr/AST-1150`).

---

## Root cause (locked)

`build_state_ui_manifest()` exposes a single string `jobs.skipped.bulk_retry_to_state = "NEW"`. `JobsSkipped.handleRetry` posts every selected id to that one target via `POST /api/jobs/bulk_state`.

Meteorite (and regular mid-pipeline) jobs that landed on Skipped after a rubric hop are not claimable from `NEW`: meteorite `grade_do` claims `METEORITE_PASSED_JD`, regular `grade_do` claims `PASSED_JD`, etc. Retry → `NEW` leaves Avail at 0 on the hop that failed.

`bulk_state` today calls `tracker.save_job` (bypasses `prior_states` and does not append `state_history`). Hop-correct targets have restricted `prior_states` that do **not** yet list the fail/technical Skipped states, so switching to `transition_job_state` without expanding priors would silently no-op updates (`ValueError` swallowed).

---

## Decisions (locked for build)

1. **Config owns the Retry map.** Add `JOBS_SKIPPED_BULK_RETRY_TO_STATE: Dict[str, str]` (from Skipped section state → claimable **primary** trigger). Manifest exposes it as `bulk_retry_to_state_by_from_state`. Remove scalar `bulk_retry_to_state`.
2. **Land on the primary trigger, not `*_RETRY` holdings.** Parent AC example is `METEORITE_PASSED_JD`. AST-1155 holdings remain for incomplete-grade first-strike inside consult; operator Skipped Retry is a full hop re-entry on the dispatch claim state.
3. **Family stays family.** Meteorite fail/technical → meteorite triggers only; regular → regular only. No cross-family targets.
4. **Expand `prior_states` on every Retry target** so `transition_job_state` accepts from→to. Do not leave Retry on the `save_job` bypass.
5. **`bulk_state` uses `transition_job_state`.** Same endpoint body `{ astral_job_ids, to_state }`; frontend groups selected jobs by current `job.state` and issues one POST per destination.
6. **Map covers every `JOBS_SKIPPED_SECTION_ORDER` entry except `CANDIDATE_SKIPPED`.** Rubric rows are AC-critical; non-rubric rows get hop-correct targets too so NEW is not a silent default. `CANDIDATE_SKIPPED` stays Resurrect-only (omit from map; frontend skips unmapped ids).
7. **Below-dispatch floor section** is synthetic (`__BELOW_DISPATCH_FLOOR__`) — not in the map; those rows are still `PASSED_*` in DB and must not be bulk-retried via this map (checkboxes may exist — if selected with no map key, skip with toast that none were queued).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOBS_SKIPPED_BULK_RETRY_TO_STATE`; expand target `prior_states`; manifest key swap | utils |
| `src/ui/api/api_jobs.py` | `bulk_state` → `transition_job_state` | ui |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Manifest type: map replaces scalar | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Group Retry by `job.state`; look up map; one POST per `to_state` | ui |

**Out of scope:** `src/core/consult.py`, `src/core/agent.py`, grade/prompt paths, `tests/**`, `docs/test-bible/**`, `stateUiManifestFixture.ts` (Betty).

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | Assert map entries + `bulk_retry_to_state_by_from_state`; drop scalar `== "NEW"` |
| `tests/component/frontend/fixtures/stateUiManifestFixture.ts` | Mirror new manifest shape |
| `tests/component/frontend/pages/test_JobsSkipped.test.tsx` | Retry posts hop-correct `to_state` for a meteorite/regular fixture row |
| `tests/component/ui/api/test_api_jobs.py` | If present: bulk_state goes through transition / prior enforcement |
| `docs/test-bible/utils/config.md` (+ frontend pages if needed) | Skipped Retry map wording |

---

## Stage 1: Config map + prior_states + manifest

**Done when:** `JOBS_SKIPPED_BULK_RETRY_TO_STATE` is the SSOT; every listed from-state maps to a `JOB_STATES` key; each target’s `prior_states` includes its mapped from-states (or target has `prior_states is None`); manifest serves `bulk_retry_to_state_by_from_state` and no longer serves `bulk_retry_to_state`; a one-liner import check prints `ok`.

1. In `src/utils/config.py`, immediately above `build_state_ui_manifest` (near the other `JOBS_SKIPPED_*` maps), add:

   ```python
   # AST-1156: Skipped Retry — from Skipped section state → claimable primary trigger.
   # Keys ⊆ JOBS_SKIPPED_SECTION_ORDER except CANDIDATE_SKIPPED (Resurrect-only).
   JOBS_SKIPPED_BULK_RETRY_TO_STATE = {
       # Regular rubric / qualify / JD
       "FAILED_JOBLIST": "NEW",
       "ERROR_QUALIFY_JOB_LISTINGS": "NEW",
       "INVALID_TITLE": "NEW",
       "FAILED_JD": "JD_READY",
       "ERROR_EVALUATE_JD": "JD_READY",
       "FAILED_TECHNICAL": "NEW",
       "FAILED_DO": "PASSED_JD",
       "FAILED_TECHNICAL_DO": "PASSED_JD",
       "FAILED_GET": "PASSED_DO",
       "FAILED_TECHNICAL_GET": "PASSED_DO",
       "FAILED_LIKE": "CULTURE_READY",
       "FAILED_TECHNICAL_LIKE": "CULTURE_READY",
       # Meteorite rubric / qualify / JD
       "METEORITE_FAILED_QUALIFY": "METEORITE_NEW",
       "METEORITE_ERROR_QUALIFY": "METEORITE_NEW",
       "METEORITE_FAILED_JD": "METEORITE_QUALIFIED",
       "METEORITE_ERROR_EVALUATE_JD": "METEORITE_QUALIFIED",
       "METEORITE_FAILED_DO": "METEORITE_PASSED_JD",
       "METEORITE_FAILED_TECHNICAL_DO": "METEORITE_PASSED_JD",
       "METEORITE_FAILED_GET": "METEORITE_PASSED_DO",
       "METEORITE_FAILED_TECHNICAL_GET": "METEORITE_PASSED_DO",
       "METEORITE_FAILED_LIKE": "METEORITE_PASSED_GET",
       "METEORITE_FAILED_TECHNICAL_LIKE": "METEORITE_PASSED_GET",
       # Non-rubric hop re-entry (replace hard-coded NEW; not AC-critical but map-complete)
       "JD_SCRAPE_FAIL": "PASSED_JOBLIST",
       "JD_SCRAPE_FAIL_COOKIE": "PASSED_JOBLIST",
       "JD_SCRAPE_FAIL_BOT": "PASSED_JOBLIST",
       "JD_SCRAPE_FAIL_MISSING": "PASSED_JOBLIST",
       "JD_SCRAPE_FAIL_CLOSED": "PASSED_JOBLIST",
       "NEED_CULTURE_CONTENT": "PASSED_GET",
       "NO_CULTURE_LINKS": "PASSED_GET",
       "NEED_WEBSITE_CONTENT": "CULTURE_READY",
   }
   ```

2. Assert map integrity (module load):

   ```python
   assert "CANDIDATE_SKIPPED" not in JOBS_SKIPPED_BULK_RETRY_TO_STATE
   assert all(k in JOB_STATES and v in JOB_STATES for k, v in JOBS_SKIPPED_BULK_RETRY_TO_STATE.items())
   assert all(
       k in JOBS_SKIPPED_SECTION_ORDER
       for k in JOBS_SKIPPED_BULK_RETRY_TO_STATE
   )
   _skipped_retryable = [s for s in JOBS_SKIPPED_SECTION_ORDER if s != "CANDIDATE_SKIPPED"]
   assert set(JOBS_SKIPPED_BULK_RETRY_TO_STATE) == set(_skipped_retryable)
   ```

3. Expand `JOB_STATES[...]["prior_states"]` lists so each mapped transition is legal under `transition_job_state`. Append (do not remove existing priors) the from-states that Retry into each target:

   | Target | Append to `prior_states` |
   |--------|--------------------------|
   | `JD_READY` | `FAILED_JD`, `ERROR_EVALUATE_JD` |
   | `PASSED_JD` | `FAILED_DO`, `FAILED_TECHNICAL_DO` |
   | `PASSED_DO` | `FAILED_GET`, `FAILED_TECHNICAL_GET` |
   | `CULTURE_READY` | `FAILED_LIKE`, `FAILED_TECHNICAL_LIKE`, `NEED_WEBSITE_CONTENT` |
   | `PASSED_GET` | `NEED_CULTURE_CONTENT`, `NO_CULTURE_LINKS` |
   | `PASSED_JOBLIST` | all five `JD_SCRAPE_FAIL*` keys |
   | `METEORITE_QUALIFIED` | `METEORITE_FAILED_JD`, `METEORITE_ERROR_EVALUATE_JD` |
   | `METEORITE_PASSED_JD` | `METEORITE_FAILED_DO`, `METEORITE_FAILED_TECHNICAL_DO` |
   | `METEORITE_PASSED_DO` | `METEORITE_FAILED_GET`, `METEORITE_FAILED_TECHNICAL_GET` |
   | `METEORITE_PASSED_GET` | `METEORITE_FAILED_LIKE`, `METEORITE_FAILED_TECHNICAL_LIKE` |

   Targets with `prior_states is None` (`NEW`, `METEORITE_NEW`) need no change.

   ⚠️ **Decision:** Do **not** add fail states as priors on AST-1155 `*_RETRY` holdings — Retry lands on primaries only. Do **not** invent new JOB_STATES keys.

4. In `build_state_ui_manifest()`, under `jobs.skipped`, **replace**:

   ```python
   "bulk_retry_to_state": "NEW",
   ```

   with:

   ```python
   "bulk_retry_to_state_by_from_state": dict(JOBS_SKIPPED_BULK_RETRY_TO_STATE),
   ```

5. Verify:

   ```bash
   python3 -c "
   from src.utils.config import (
       JOBS_SKIPPED_BULK_RETRY_TO_STATE, JOB_STATES, build_state_ui_manifest, dispatch_claim_states,
   )
   m = build_state_ui_manifest()['jobs']['skipped']
   assert 'bulk_retry_to_state' not in m
   assert m['bulk_retry_to_state_by_from_state']['METEORITE_FAILED_DO'] == 'METEORITE_PASSED_JD'
   assert m['bulk_retry_to_state_by_from_state']['FAILED_DO'] == 'PASSED_JD'
   assert 'METEORITE_FAILED_DO' in JOB_STATES['METEORITE_PASSED_JD']['prior_states']
   assert 'FAILED_DO' in JOB_STATES['PASSED_JD']['prior_states']
   # claimable primary still companions with AST-1155 holding
   assert 'METEORITE_PASSED_JD' in dispatch_claim_states('METEORITE_PASSED_JD', 'job')
   print('ok')
   "
   ```

⚠️ **Decision:** Explicit dict (not “first prior of the fail state”) so multi-prior Skipped rows (`NEED_WEBSITE_CONTENT`) and `prior_states is None` error states stay unambiguous and reviewable.

---

## Stage 2: API transition + Skipped Retry UI

**Done when:** `POST /api/jobs/bulk_state` updates via `transition_job_state` (priors + `state_history`); Skipped Retry groups selection by each job’s current `state`, posts the mapped `to_state` per group, and reports how many jobs were queued; TypeScript manifest type matches Stage 1; `py_compile` + frontend typecheck of touched files succeed.

1. In `src/ui/api/api_jobs.py` `bulk_state`, replace the per-id `save_job(job_id, state=to_state)` loop with `transition_job_state`:

   ```python
   updated = 0
   for job_id in ids:
       try:
           transition_job_state([job_id], to_state)
           updated += 1
       except ValueError:
           pass
   return jsonify({"updated": updated})
   ```

   Keep the same request body contract (`astral_job_ids` + `to_state`). Do not add a second endpoint.

   ⚠️ **Decision:** Per-id try/except preserves today’s partial-success behavior when one id is illegal; do not fail the whole batch on the first `ValueError`.

2. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, change `jobs.skipped` typing:

   - Remove `bulk_retry_to_state: string`
   - Add `bulk_retry_to_state_by_from_state: Record<string, string>`

3. In `src/ui/frontend/src/pages/JobsSkipped.tsx` `handleRetry`:

   a. Build `id → state` from the loaded `rows` (each job already has `state`).
   b. Partition selected ids by `state`; for each partition look up `manifest.jobs.skipped.bulk_retry_to_state_by_from_state[state]`.
   c. Skip partitions with no map entry (e.g. accidental `CANDIDATE_SKIPPED` or floor synthetic key if ever selected).
   d. For each `(to_state, ids)` group, `POST /api/jobs/bulk_state` with that `to_state` and those ids (sequential `await` is fine — no new concurrency helper).
   e. Sum `updated` across responses; toast `` `${total} jobs queued for retry` `` on success; if `total === 0`, toast error `"Retry failed"` (or `"No retryable jobs in selection"` — pick the existing error toast style if `total === 0` after skips).
   f. Clear selection / `load()` as today after the loop.

4. Verify (engineer, no test-tree edits):

   ```bash
   python3 -m py_compile src/utils/config.py src/ui/api/api_jobs.py
   # From src/ui/frontend — typecheck only if the repo already has a script; otherwise:
   npx tsc --noEmit -p src/ui/frontend 2>/dev/null || true
   ```

   Manual UAT checklist (record in Linear stage comment, not in this plan as status):

   - Meteorite job in `METEORITE_FAILED_DO` → Retry → state `METEORITE_PASSED_JD`; Scheduled Actions Avail for `grade_do` @ `METEORITE_PASSED_JD` **> 0**.
   - Regular job in `FAILED_GET` → Retry → `PASSED_DO`; Avail for `grade_get` **> 0**.
   - Mixed selection (meteorite Do fail + regular Get fail) → two POSTs; each family lands correctly.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each tip to `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`.
- Do not edit files outside the Files Changed table.
- When a step is ambiguous, contradicts another step, or the codebase has drifted — stop, comment on the **parent** Linear issue with the Stage N blocked format, and wait.
- Do not edit `tests/**` or `docs/test-bible/**`.

---

## Self-Assessment

**Scope:** `Single-Component` — config state-UI map + job prior expansions, one API call-site swap, Skipped page Retry grouping; no consult/agent grade path changes.

**Conf:** `high` — parent AC names the meteorite Do → `METEORITE_PASSED_JD` example; fail-state priors already encode the hop trigger; manifest-driven bulk targets match existing company bulk_transitions pattern.

**Risk:** `Medium` — wrong map entry or missing prior would leave Avail at 0 or silently drop updates; mixed-selection Retry now multi-posts (regression surface on the Skipped page only).

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One config dict; UI does not hard-code destinations.
- **§1.4 / §2.1:** Retry targets live in `config.py`; manifest is the UI read path (`pattern.config.config-block`).
- **§2.6 / `astral.state.core-decides-transitions` / `astral.state.job-prior-states-enforced`:** Retry goes through `transition_job_state` with expanded `prior_states`; data layer still does not decide targets.
- **§2.4:** No new batch claim helpers — dispatch continues to claim primary (+ AST-1155 companion holdings).
- **§3.3 imports:** UI API already imports `transition_job_state`; no new layer violations.
- **No conflicts** requiring `conf-!!-NONE`.
