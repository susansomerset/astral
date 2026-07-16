# UAT: Get criteria Save failed and content lost on return

**Parent:** [AST-900 — craft get rubric did not populate the rubric content for candidate](https://linear.app/astralcareermatch/issue/AST-900/craft-get-rubric-did-not-populate-the-rubric-content-for-candidate)

**Linear:** [AST-904](https://linear.app/astralcareermatch/issue/AST-904/uat-get-criteria-save-failed-and-content-lost-on-return)

**Publish ref:** `origin/sub/AST-900/AST-904-uat-get-criteria-save-lost`

**Summary (FIX-UAT):** On `/artifacts/get_job_criteria` for `karfo`, criteria were visible for review but **Save** toasted `Save failed`; after navigate-away/return the criteria were gone (not in the editor, not recovered). Sibling AST-903 owns truncated Generate JSON; this ticket owns the **Save + recovery** gap so a failed Save cannot erase recoverability, and the user sees the real server error. Review-then-Save and base-resume auto-persist stay unchanged.

---

## Root cause (code, UAT)

| Observation | Implication |
|-------------|-------------|
| Toast text is exactly `"Save failed"` | `ArtifactEditor.doSave` catch **discards** `Error.message` (server `error` from 400) and always shows the hardcoded string — UAT cannot see `normalize_rubric_artifacts_on_save` / `sync_rubric_vectors_from_criteria` reasons. |
| Save path: `normalize` → `apply_rubric_vectors_save` → clear pending → `save_candidate_data` | `apply_rubric_vectors_save` **`del artifacts[key]`** for each rubric key before the clear loop. Production clear uses `if artifact_key in arts` → **never clears** craft pending after a real rubric Save. API test mocks `apply_*` so it does not delete — false green. |
| Failed Save (normalize/sync `ValueError` → HTTP 400) | Exception path returns before clear (good), but frontend hides the reason. Navigate away: AST-902 skips unmount auto-save while in review (correct). Return depends on pending stash / ledger fallback. |
| Content gone on return | Hydrate shows empty `get_rubric` (nothing in `rubric_vector`); recovery 404 when pending missing **and** ledger/`agent_data` unusable (e.g. prior truncated COMPLETED from AST-903 era). Failed Save must **re-stash** submitted criteria so return always recovers the review payload. |

**Conclusion:** Two product defects compose the UAT report: (1) Save errors are opaque; (2) a failed Save does not guarantee the submitted criteria remain in `pending_craft_generations`, so page-return recovery can 404 even though the user just saw the criteria. Pending clear-after-`del` is a third defect (successful Save never clears pending) — fix in the same Save path so clear runs only **after** successful persist, using keys captured **before** `apply` mutates `arts`.

**Out of scope:** craft rubric prompts/schemas; AST-903 token/truncation; dispatcher `grade_get` batches; base resume auto-persist.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_candidate.py` | Capture rubric keys before apply; clear pending only after successful persist; on Save failure re-stash submitted criteria | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Toast real Save error; keep review mode on failure (verify) | ui (React) |

**Not in scope:** `rubric_text.py` grade grammar (unless build proves generated `A ==` content cannot pass — stop and comment); page wrappers; prompts; AST-903 provider hard-fail.

---

## Stage 1: Save path — clear pending only after success; re-stash on failure

**Done when:** A failed `PUT /api/candidates/<id>/data` with `artifacts.get_rubric` leaves that payload in `pending_craft_generations[craft_get_rubric]` for `GET …/pending`. A successful Save clears that pending key even though `apply_rubric_vectors_save` deletes the artifact key from `arts`.

1. In `src/ui/api/api_candidate.py` `update_candidate_data`, inside the `isinstance(arts, dict)` branch, **before** `normalize_rubric_artifacts_on_save(arts)`:
   - `rubric_keys_to_clear = [k for k in arts if k in RUBRIC_CRITERIA_ARTIFACT_KEYS]` (import `RUBRIC_CRITERIA_ARTIFACT_KEYS` from config if not already imported — same set used by normalize).
   - `submitted_rubric = {k: arts[k] for k in rubric_keys_to_clear}` — shallow copy of lists/dicts as submitted (before normalize mutates criterion dicts in place is OK if we copy list of dicts with `copy.deepcopy` **or** build re-stash payload from pre-normalize snapshot). Prefer `import copy` + `submitted_rubric = copy.deepcopy({k: arts[k] for k in rubric_keys_to_clear})` before normalize.
2. Keep call order: `normalize_rubric_artifacts_on_save(arts)` then `apply_rubric_vectors_save(candidate_id, arts)`.
3. **Remove** the clear-pending loop from its current position (between apply and `save_candidate_data`).
4. After `save_candidate_data(candidate_id, body, replace=False)` succeeds (still inside the `if body:` path that performed the artifact save), clear pending:
   ```python
   for craft_task_key, artifact_key in CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.items():
       if artifact_key in rubric_keys_to_clear:
           _clear_pending_craft_generation(candidate_id, craft_task_key)
   ```
5. In the existing `except Exception as e:` that returns 400:
   - Before return, if `submitted_rubric` was defined and non-empty: for each `(craft_task_key, artifact_key)` in `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.items()` where `artifact_key in submitted_rubric` and the value is a non-empty list of criterion dicts, call `_stash_pending_craft_generation(candidate_id, craft_task_key, batch_id=None, parsed_response={"criteria": submitted_rubric[artifact_key]})`.
   - Initialize `submitted_rubric = {}` / `rubric_keys_to_clear = []` before the `try` so the except path is safe.
6. Do **not** change normalize/sync validation rules in this stage.

⚠️ **Decision:** Re-stash on failure uses the **submitted** criteria (what the user tried to Save), not a new Generate — restores page-return recovery even when prior pending/ledger is missing or truncated.

⚠️ **Decision:** Clear only after `save_candidate_data` returns — vectors already written by `apply_rubric_vectors_save`; if `save_candidate_data` itself raises, except re-stash still runs (pending holds review payload). Acceptable: table may already have vectors from apply; hydrate would show them on return — re-stash is belt-and-suspenders for the empty-table failure case.

---

## Stage 2: ArtifactEditor — surface Save errors; stay in review on failure

**Done when:** A 400 Save shows the server `error` string in the toast (not generic `"Save failed"`). Failed Save does not clear `snapshot` / review mode.

1. In `ArtifactEditor.tsx` `doSave` (candidate path and jobPersistence path):
   - Change `catch { setToast({ text: "Save failed", … }) }` to `catch (e) { setToast({ text: (e as Error).message || "Save failed", variant: "error" }) }`.
2. Confirm failure path does **not** call `setSnapshot(null)` (today only success clears snapshot) — leave that behavior.
3. No new props; no page-wrapper edits.

⚠️ **Decision:** Same toast fix for jobPersistence for consistency (one catch pattern); rubric UAT is the candidate path.

---

## Execution contract (for build-child)

- Stages in order; one `code(AST-904):` commit per stage; publish to `origin/sub/AST-900/AST-904-uat-get-criteria-save-lost`.
- Merge `origin/ftr/AST-900-craft-get-rubric-populate` before coding (AST-903 tip may already be on ftr).
- If a real Save of valid generated `A ==` / `B ==` criteria still fails for a reason not covered (e.g. missing `agent_task` for `grade_get`) — stop, comment on **parent AST-900** with the exact `error` string and proposed fix; do not invent prompt changes.
- Do **not** edit `tests/` or `docs/test-bible/**` — note for Betty: `test_put_artifact_clears_matching_pending` must use a real `apply_rubric_vectors_save` (or a mock that `del`s keys) so clear-after-success is actually asserted.

---

## Self-Assessment

**Scope:** `Single-Component` — candidate Save API ordering + `ArtifactEditor` toast; no prompt/schema/generate changes.

**Conf:** `high` — failure modes are visible in `api_candidate.update_candidate_data` / `doSave`; re-stash + clear-after-success are direct fixes for the UAT symptoms.

**Risk:** `Medium` — Save path is shared by all rubric artifacts; wrong clear/re-stash ordering could leave stale pending after a good Save or drop recovery on failure. Mitigated by capturing keys/payload before mutate and clearing only after successful `save_candidate_data`.

---

## Review

**Radia** · `origin/dev`…`origin/sub/AST-900/AST-904-uat-get-criteria-save-lost` @ `f3a8945` · AST-904 product delta = `api_candidate.py` (`2838dad`) + `ArtifactEditor.tsx` (`621cf7d`); AST-903 files in the vs-`dev` diff were already reviewed clean.

### What's solid

- **Plan fidelity:** Stages 1–2 match. Captures `rubric_keys_to_clear` + `copy.deepcopy(submitted_rubric)` **before** normalize/apply; removes the broken clear-after-`apply` loop; clears pending only after `save_candidate_data`; except path re-stashes non-empty submitted criteria with `batch_id=None`. Frontend toasts `(e as Error).message || "Save failed"` on both candidate and jobPersistence paths; failure does not clear `snapshot` (review retained).
- **Root-cause fix:** Clear uses keys captured before `apply_rubric_vectors_save` deletes artifact keys — closes the AST-901 false-green (`if artifact_key in arts` after `del`). Betty test updated to mock apply with `arts.pop("get_rubric")`.
- **§3.2 / §3.3:** API stays thin; reuses core `_stash` / `_clear` + config maps; no data-layer import from UI; no prompt/schema/AST-903 scope creep.
- **Self-Assessment:** Diff footprint matches **Single-Component** / high conf; Medium risk mitigated by pre-mutate capture + clear-after-persist.

### Issues

None (no fix-now / discuss).

### Advisory (not fix-now)

- Except-path re-stash runs for any exception after capture — including a rare combined PUT where artifact persist+clear already succeeded and a later `state`/`api_key` write fails. ArtifactEditor Saves only `{ artifacts: { [key]: … } }`, so the UAT path is fine; would leave stale pending after a mostly-successful admin combined PUT.
- Re-stash ignores `_stash_pending_craft_generation`’s bool return (AST-901 resolve). If the candidate row is gone mid-request, user still gets the 400 toast but page-return recovery cannot help — same class of edge case as generate-path stash failure.

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| _(none)_ | — | Clean — ready for resolve-child / merge-child rollup |

## Resolution

_(resolve-child fills after Review Posted)_

---

## Rules review (ASTRAL_CODE_RULES)

| Rule | Compliance |
|------|------------|
| §1.3 DRY | Reuses `_stash_pending_craft_generation` / `_clear_pending_craft_generation` / `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`. |
| §3.2 UI | API stays thin; validation errors still raised from core normalize/sync. |
| §3.3 imports | UI → core/utils only; no new data imports in API. |
| Boundaries | No prompt/schema/AST-903 token work. |
