# AST-1193 — ANALYSIS token vector↔rubric match parity

**Linear:** https://linear.app/astralcareermatch/issue/AST-1193/analysis-token-vectorrubric-match-parity-issues-while-running  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan  
**Publish ref:** `sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`

Make `{$ANALYSIS_JD}` / `{$ANALYSIS_DO}` / `{$ANALYSIS_GET}` / `{$ANALYSIS_LIKE}` format every persisted consult grade vector against the candidate's live rubric using the **same** label-or-code match rules consult scoring already uses (`_lookup_rubric_reason_for_grade` / `_importance_for_label`), so artifact hops (starting with `anticipate_scan`) get non-empty ANALYSIS tokens when grades exist. Add debug-gated found/recorded counts per ANALYSIS phase on that path. Does **not** own candidate name token view (**AST-1192**), provider timeout hardening (**AST-1164**), or rubric regeneration.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add shared `_find_rubric_criterion`; refactor scoring helpers to call it; fix `_format_analysis_phase_text` to use it (label-or-code); thread `debug=` through `build_job_token_context` / `_format_analysis_phase_text` and emit Style D found/recorded per ANALYSIS phase | core |
| `src/core/agent.py` | Pass `debug` from `do_task` into `_job_context_for_call` → `build_job_token_context(..., debug=debug)` so hop debug runs reach the formatter | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Candidate name / `build_candidate_token_view` / `{$FIRST_NAME}` / `{$LAST_NAME}` | AST-1192 |
| Provider timeout / blank `error=` / zero-token classification | AST-1164 |
| `JOB_TOKEN_CONFIG` phase keys / grades_key / owner task keys | unchanged (AST-513 already correct) |
| Rubric regeneration / `rubric_vector` writes | out of epic |
| `_grade_set_vector_diff` / IncompleteGradeSetError / pass thresholds | out of scope |
| Manage Tasks prompt prose | out of epic |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Shared label-or-code criterion lookup + ANALYSIS formatter parity

**Done when:** `_format_analysis_phase_text` resolves a grade vector when either stripped label **or** uppercased code matches (identical to scoring helpers). A grade whose `vector` is a 2-char code that scoring would accept produces a CONSIDER / rubric blob / ANALYSIS RESULT block instead of the "no rubric criterion" skip. Scoring helpers still behave the same (refactored to the shared finder only).

1. In `src/core/consult.py`, immediately after `_strip_code`, add:

   ```python
   def _find_rubric_criterion(rubric_criteria: list, vector_label: str):
       """Return the criterion dict matching vector by stripped label or code (AST-707 / AST-1193)."""
       target = _strip_code((vector_label or "").strip())
       t_upper = target.upper()
       for item in rubric_criteria or []:
           if not isinstance(item, dict):
               continue
           lab = _strip_code(str(item.get("label") or "").strip())
           code = str(item.get("code") or "").strip().upper()
           if lab != target and code != t_upper:
               continue
           return item
       return None
   ```

   Match rules must be **byte-for-byte** the same predicate as today's loops in `_lookup_rubric_reason_for_grade` and `_importance_for_label` (stripped label equality **or** uppercased code equality). Do **not** add fuzzy / casefold label matching, substring match, or importance defaults inside this helper.

2. In `_lookup_rubric_reason_for_grade`, replace the open `for item in rubric_criteria:` match loop with a call to `_find_rubric_criterion(rubric_criteria, vector_label)`. Keep the existing grade-description resolution (`grade_descriptions` list, then `parse_trailing_grade_table_lines` on `content`) unchanged once a criterion is found. Keep the same `ValueError` messages when criterion or grade description is missing.

3. In `_importance_for_label`, replace the open match loop with `_find_rubric_criterion(rubric_criteria, vector_label)`. Keep the existing importance / default / `ValueError` behavior when found or missing.

4. In `_format_analysis_phase_text`, replace the label-only match block:

   ```python
   criterion = None
   target = _strip_code(vector_label)
   for item in rubric_criteria:
       ...
       if _strip_code(str(item.get("label") or "").strip()) == target:
           criterion = item
           break
   ```

   with:

   ```python
   criterion = _find_rubric_criterion(rubric_criteria, vector_label)
   ```

   Keep all other behavior unchanged:
   - Meteorite override merge via `JOB_TOKEN_CONFIG["analysis_phases_meteorite_override"]` when `_entity_state_is_meteorite`
   - Grades from `phase_cfg["grades_key"]`; empty / non-list → `""`
   - Rubric via `rubric_criteria_for_task(cid, owner)` when owner + candidate id present; empty criteria → `""`
   - On `criterion is None`: keep the existing `logger.warning("_format_analysis_phase_text: no rubric criterion for vector %r (phase=%s)", …)` and `continue` (skip that vector; do not fail the whole token)
   - On match: same CONSIDER / `{content}` / ANALYSIS RESULT block shape and `\n\n` join

   ⚠️ **Decision:** Extract one shared finder and reuse it in scoring + ANALYSIS rather than only patching the formatter loop. AST-707 already taught scoring label-or-code; ANALYSIS was left on label-only (AST-513). One helper prevents the three sites from drifting again (§1.3 DRY).

5. Do **not** change `JOB_TOKEN_CONFIG`, grade persistence keys, `_grade_set_vector_diff`, coat-check handlers, or candidate name resolution.

## Stage 2: Debug found/recorded per ANALYSIS phase + wire from `do_task`

**Done when:** A `do_task` hop with `debug=True` that builds job token context emits Style D per-index headers for each ANALYSIS phase with found grade counts vs recorded (formatted) vector counts. `debug=False` emits no new debug-contract lines from this path.

1. Change `build_job_token_context` signature to:

   ```python
   def build_job_token_context(
       job: Dict[str, Any], candidate_data: dict, *, candidate_id: str = "", debug: bool = False
   ) -> Dict[str, str]:
   ```

   At the start of the body: `logger.set_debug_flag(debug)`.

2. Change `_format_analysis_phase_text` signature to accept `*, debug: bool = False` (or rely on module logger flag already set by the builder — prefer an explicit `debug` kwarg and `logger.set_debug_flag(debug)` at the top of the formatter so preview/direct callers stay correct). Pass `debug=debug` from `build_job_token_context` into each `_format_analysis_phase_text` call.

3. After computing the joined blocks string for a phase (including early-return empty cases), when `debug=True`, emit:

   - `logger.debug_index(`
     - `func="_format_analysis_phase_text"`
     - `index` = 1-based position of this phase among `("ANALYSIS_JD", "ANALYSIS_DO", "ANALYSIS_GET", "ANALYSIS_LIKE")`
     - `total` = `4`
     - `identifier` = `f"{job_id}:{phase_token}"` where `job_id` is `str((job or {}).get("astral_job_id") or "")` threaded from the builder (add an optional `*, job_id: str = ""` kwarg on the formatter, or pass identifier pieces via kwargs — builder owns the job row)
     - `outcome` = `"formatted"` when the returned text is non-empty, else `"empty"`
     - `)`
   - `logger.debug_detail(`
     - `f"found_grades={found} recorded_vectors={recorded} rubric_criteria={len(rubric_criteria) if rubric_criteria else 0}"`
     - `)`

   Count definitions (literal):
   - **found_grades:** number of `grades` entries that are `dict` with non-empty stripped `vector`
   - **recorded_vectors:** number of CONSIDER blocks appended (successful criterion matches)
   - Early exits (missing phase cfg / empty grades / empty rubric): `found_grades` as above (0 if grades missing), `recorded_vectors=0`, still emit the index + detail when `debug=True`

   Do **not** log full rubric blobs or full token text in detail lines (counts only). Payloads are short; no `debug_detail_block` required.

4. In `src/core/agent.py`:
   - Add `debug: bool = False` to `_job_context_for_call`
   - Pass it through: `return builder(..., candidate_id=cid, debug=debug)` (builder already receives job row + `cd_copy`)
   - At the existing call site in `do_task` (`_jc = _job_context_for_call(ctx, index, cd)`), pass `debug=debug`

5. Preview / adhoc callers (`candidate.py` Manage Tasks preview, `api_admin.py` adhoc resolve) may keep the default `debug=False` — no required edits unless a touched call site already has a `debug` flag in scope; if it does, pass it through. Do **not** invent new UI debug toggles.

6. Coat-check statute (`astral.patterns.coat-check-never-store-empty`): this ticket does **not** add persistence of ANALYSIS strings. It only fixes formatting so prompt tokens are non-empty when grades match the live rubric. Do **not** write empty ANALYSIS text into job_data / artifacts as a "success" payload.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, publishes to `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — primary change is `consult.py` ANALYSIS formatting + a thin `debug` thread through `agent._job_context_for_call`; no new modules, config keys, or UI.

**Conf:** `high` — the formatter's label-only loop is a known drift from AST-707's label-or-code scoring helpers; the fix is a shared predicate plus Style D counts on an existing `debug=` path.

**Risk:** `Medium` — ANALYSIS tokens feed artifact LLM prompts; a wrong criterion match would attach the wrong rubric blob to a grade, but the match predicate is already trusted by scoring/hydration, so risk is parity restoration rather than a new algorithm.

## Code rules check

- §1.3 DRY: one `_find_rubric_criterion`; scoring + ANALYSIS call it — no third copy of the loop.
- §1.5.1 debug-contract-gated: new lines only when `debug=True` via `set_debug_flag` + `debug_index` / `debug_detail`; Style D index N/M; no `[DEBUG]` info spam.
- §2.1 config-source-of-truth: no new config; continue reading `JOB_TOKEN_CONFIG` phase maps.
- §2.3.1 grade-vector-validation: formatter consumes already-persisted grades; does not change decode/validation.
- §2.4 / §2.6: no batch lifecycle or state-machine changes.
- §3.3 imports: stay in core; keep lazy `rubric_criteria_for_task` import inside the formatter.
- Boundaries: no name-token work, no AST-1164 provider path, no test-tree edits.
