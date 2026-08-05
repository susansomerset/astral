# AST-1193 — ANALYSIS token vector↔rubric match parity

**Linear:** https://linear.app/astralcareermatch/issue/AST-1193/analysis-token-vectorrubric-match-parity-issues-while-running  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan  
**Publish ref:** `sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`

Make `{$ANALYSIS_JD}` / `{$ANALYSIS_DO}` / `{$ANALYSIS_GET}` / `{$ANALYSIS_LIKE}` format every persisted consult grade vector into a non-empty CONSIDER / rubric blob / ANALYSIS RESULT block for artifact hops (starting with `anticipate_scan`). Prefer the live rubric via the **same** label-or-code match scoring already uses; when live misses a full-label vector that still appears on the job-carried analysis-time `*_rubric` snapshot (AST-1063), resolve identity from that snapshot and pull `content` from live by code so grades that already passed scoring are not silently skipped. Add debug-gated found/recorded counts per ANALYSIS phase. Does **not** own candidate name token view (**AST-1192**), provider timeout hardening (**AST-1164**), or rubric regeneration.

## Diagnosis (why `'Compensation'` misses today)

Verified in code against the parent log (~35 full human labels across all four ANALYSIS phases — not 2-char codes):

1. **`_format_analysis_phase_text`** (`consult.py`) loads criteria only from live `rubric_criteria_for_task(cid, owner)`. It never reads the job-carried `jd_rubric` / `do_rubric` / `get_rubric` / `like_rubric` snapshots that `render_verdict` / evaluate batch already persist via `_rubric_snapshot_for_job_data` (AST-1063).
2. Match today is **label-only** (stripped). Scoring helpers `_lookup_rubric_reason_for_grade` / `_importance_for_label` already accept stripped label **or** uppercased code (AST-707). That drift is real and worth fixing for code-shaped vectors, but **every** unmatched vector in the parent log is a full label (`'Compensation'`, `'Program Scope'`, …). The code disjunct cannot fire for those strings (`_CODE_SUFFIX` / `_vector_labels_map` treat codes as two letters). **Stage 1 alone is a no-op for the observed run.**
3. Grades that persisted through AST-1155 `_require_complete_grade_set` had vectors equal to the **then-live** rubric labels. A 100% miss against **now-live** criteria (with non-empty criteria — otherwise the formatter returns `""` before per-vector warnings) fits **post-grade rubric label change** (or a different current criteria set for that owner), not code-vs-label formatting.
4. Snapshots intentionally **omit `content`** (list-header shape). So snapshot-only formatting cannot supply the rubric blob; content must still come from live (by code) when possible.

Local `data/astral.db` in this worktree has zero jobs/candidates — diagnosis is from code + parent log shapes, not a live row dump.

⚠️ **Decision (AC4 delivery):** Prefer live label-or-code first. On miss, match the grade vector to the job-carried phase `*_rubric` snapshot by the same label-or-code helper; use snapshot `label`/`code` for identity; resolve `content` from live by code (or label). If live has no content for that code, still emit `CONSIDER: {title}\n\nANALYSIS RESULT: …` so the token is non-empty. Do **not** regenerate rubrics. Do **not** invent fuzzy label matching. (Escalate path rejected for this plan: parent AC4 requires the reproduce case to stop logging empty ANALYSIS from these unmatchable vectors; snapshot identity + live content is the mismatch class that closes it without rewriting `rubric_vector`.)

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add shared `_find_rubric_criterion`; refactor scoring helpers; ANALYSIS formatter: live label-or-code + snapshot fallback + live content-by-code; phase iteration from `JOB_TOKEN_CONFIG["analysis_phases"]`; Style D found/recorded via local debug logger handle | core |
| `src/core/agent.py` | Pass `debug` from `do_task` into `_job_context_for_call` → `build_job_token_context(..., debug=debug)` | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Candidate name / `build_candidate_token_view` / `{$FIRST_NAME}` / `{$LAST_NAME}` | AST-1192 |
| Provider timeout / blank `error=` / zero-token classification | AST-1164 |
| `JOB_TOKEN_CONFIG` phase key declarations / grades_key / owner task keys | unchanged (read-only) |
| Rubric regeneration / `rubric_vector` writes / widening `_rubric_snapshot_for_job_data` to store `content` | out of epic |
| `_grade_set_vector_diff` / IncompleteGradeSetError / pass thresholds | out of scope |
| Manage Tasks prompt prose | out of epic |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Shared label-or-code criterion lookup (DRY — not the AC4 fix alone)

**Done when:** Scoring helpers and the ANALYSIS formatter share one `_find_rubric_criterion` with the AST-707 predicate. A grade whose `vector` is a 2-char code that scoring would accept matches via this helper. **This stage does not by itself close AC4 for the parent log** (full-label vectors); Stage 3 does.

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

   Match rules must be **byte-for-byte** the same predicate as today's loops in `_lookup_rubric_reason_for_grade` and `_importance_for_label`. Do **not** add fuzzy / casefold label matching or substring match.

2. In `_lookup_rubric_reason_for_grade`, replace the open match loop with `_find_rubric_criterion(rubric_criteria, vector_label)`. Keep grade-description resolution and `ValueError` messages unchanged.

3. In `_importance_for_label`, replace the open match loop with `_find_rubric_criterion(rubric_criteria, vector_label)`. Keep importance / default / `ValueError` behavior.

4. Do **not** yet change `_format_analysis_phase_text` beyond what Stage 3 specifies (Stage 3 owns the formatter body). Stage 1 may leave the formatter on the old loop until Stage 3 lands in the same build sequence — implement Stage 1 helpers first, then Stage 3 switches the formatter to the shared finder + snapshot path in one coherent edit if committing stages separately: **Stage 1 commit = helper + scoring refactors only; Stage 3 commit = formatter.**

## Stage 2: Debug found/recorded per ANALYSIS phase + wire from `do_task`

**Done when:** A `do_task` hop with `debug=True` that builds job token context emits Style D per-index headers for each ANALYSIS phase with found grade counts vs recorded vector counts. `debug=False` emits **no** new debug-contract lines and **does not** lower the shared `src.core.consult` module logger's debug state.

1. Change `build_job_token_context` signature to:

   ```python
   def build_job_token_context(
       job: Dict[str, Any], candidate_data: dict, *, candidate_id: str = "", debug: bool = False
   ) -> Dict[str, str]:
   ```

2. Debug handle rule (single instruction — no alternatives): obtain a **local** logger for contract lines with `log = get_logger(__name__, debug_flag=debug)` (same pattern as other gated helpers). Emit `log.debug_index` / `log.debug_detail` only through that handle. **Do not** call `logger.set_debug_flag(debug)` (or `False`) inside `build_job_token_context` or `_format_analysis_phase_text` — that setter lowers the shared module logger from DEBUG to INFO when `debug=False` and would clobber other consult debug runs in-process.

3. Change `_format_analysis_phase_text` to accept `*, debug: bool = False, job_id: str = ""`. Pass `debug=debug` and `job_id=str(job.get("astral_job_id") or "")` from the builder. Inside the formatter, use the same local-handle rule: `log = get_logger(__name__, debug_flag=debug)`.

4. Phase list authority: in `build_job_token_context`, replace the hardcoded `("ANALYSIS_JD", "ANALYSIS_DO", "ANALYSIS_GET", "ANALYSIS_LIKE")` iteration with:

   ```python
   phase_tokens = tuple((JOB_TOKEN_CONFIG.get("analysis_phases") or {}).keys())
   ```

   Use `phase_tokens` for both formatting and debug `index`/`total` (`total=len(phase_tokens)`). Meteorite override continues to mutate owner/artifact for `ANALYSIS_JD` only inside the formatter — it does not change the key set.

5. After computing the joined blocks string for a phase (including early-return empty cases), when `debug=True`, emit via the local handle:

   - `log.debug_index(func="_format_analysis_phase_text", index=<1-based among phase_tokens>, total=len(phase_tokens), identifier=f"{job_id}:{phase_token}", outcome="formatted" if text else "empty")`
   - `log.debug_detail(f"found_grades={found} recorded_vectors={recorded} live_criteria={n_live} snapshot_criteria={n_snap}")`

   Counts:
   - **found_grades:** grade dicts with non-empty stripped `vector`
   - **recorded_vectors:** CONSIDER blocks appended
   - **live_criteria** / **snapshot_criteria:** lengths of the lists used for that phase (0 when missing)
   - Early exits still emit index + detail when `debug=True`

   Counts only — no full blobs / token text.

6. In `src/core/agent.py`: add `debug: bool = False` to `_job_context_for_call`; pass `debug=debug` into the builder; at the `do_task` call site pass `debug=debug`.

7. Preview / adhoc callers may keep default `debug=False`. Do not invent UI debug toggles.

8. Coat-check: do **not** persist empty ANALYSIS strings into job_data / artifacts as success.

## Stage 3: ANALYSIS formatter — live first, snapshot identity fallback (AC4)

**Done when:** For a job with persisted `*_grades` and matching phase `*_rubric` snapshot labels (even when live criteria labels have drifted), each `{$ANALYSIS_*}` token is non-empty and includes CONSIDER / ANALYSIS RESULT for those vectors. Live label-or-code hits still use live `content`. Debug counts from Stage 2 show `recorded_vectors` tracking found grades on that path.

1. In `_format_analysis_phase_text`, keep meteorite phase-cfg merge and grades load. Derive snapshot key from `grades_key`: if `grades_key` ends with `"_grades"`, snapshot key is `grades_key[:-7] + "_rubric"` (e.g. `do_grades` → `do_rubric`, `jd_grades` → `jd_rubric`). Read `snapshot = job_data.get(snapshot_key)`; treat non-list as `[]`.

2. Load live `rubric_criteria` via `rubric_criteria_for_task(cid, owner)` when owner + cid present; else `[]`. **Remove** the early `if not rubric_criteria: return ""` — empty live must not abort formatting when grades + snapshot can still produce blocks. Keep early `return ""` only for missing phase cfg or empty/non-list grades.

3. For each grade dict with non-empty `vector_label`:

   a. `criterion = _find_rubric_criterion(live_criteria, vector_label)`  
   b. If `criterion is None` and snapshot is a non-empty list: `snap_row = _find_rubric_criterion(snapshot, vector_label)`  
      - If `snap_row` is not None: set `title = str(snap_row.get("label") or vector_label).strip()` and `code = str(snap_row.get("code") or "").strip()`; then `criterion = _find_rubric_criterion(live_criteria, code) if code else None` to obtain live `content` (and prefer live label for title when that live hit exists). If live content lookup misses, keep `criterion = None` but still treat as a **snapshot identity hit** (see c).  
   c. Emit rules:
      - **Live hit (a):** `title = str(criterion.get("label") or vector_label).strip()`; `rubric_blob = str(criterion.get("content") or "").strip()`; append CONSIDER / blob / ANALYSIS RESULT as today.
      - **Snapshot identity hit with live content (b with live criterion):** same block shape using live content; title from live label if present else snapshot label.
      - **Snapshot identity hit without live content:** append  
        `CONSIDER: {title}\n\nANALYSIS RESULT: {letter} ({conf_s} confidence)`  
        (blank line where blob would be — token still non-empty; title from snapshot).
      - **Neither live nor snapshot:** keep existing warning  
        `"_format_analysis_phase_text: no rubric criterion for vector %r (phase=%s)"`  
        and `continue`.

4. Letter / confidence formatting and `\n\n` join unchanged.

5. Pass `job_data` snapshot path only — do **not** widen `_rubric_snapshot_for_job_data` to persist `content` in this ticket.

6. `build_job_token_context` iterates `phase_tokens` from Stage 2 and passes `debug` / `job_id` into the formatter.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, publishes to `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — `consult.py` ANALYSIS formatting + shared criterion finder + snapshot fallback; thin `debug` thread through `agent._job_context_for_call`.

**Conf:** `Medium` — Stage 1 DRY is certain; AC4 delivery rests on job-carried `*_rubric` snapshots existing for the failing jobs (AST-1063 write path) and on snapshot labels still matching persisted grade vectors after live drift. If a job lacks `*_rubric`, fallback cannot help and that case needs a separate escalate.

**Risk:** `Medium` — snapshot fallback can attach a live content blob by code after label drift (intended); wrong-code collisions would mis-attach content, same class of risk as scoring's code match. Emitting CONSIDER without blob when live content is gone is weaker context but still non-empty (AC4).

## Code rules check

- §1.3 DRY: one `_find_rubric_criterion` for scoring, live ANALYSIS, and snapshot lists.
- §1.5.1 debug-contract-gated: local `get_logger(..., debug_flag=debug)` only; never lower shared module debug via `set_debug_flag(False)`.
- §1.4 / §2.1: phase iteration from `JOB_TOKEN_CONFIG["analysis_phases"]` keys; no second hardcoded phase tuple / magic `total=4`.
- §2.3.1: formatter consumes persisted grades; no decode/validation change.
- Coat-check: no new empty ANALYSIS persistence.
- Boundaries: no name-token work, no AST-1164, no rubric regeneration, no test-tree edits.

## Revisions

Revision 1 — 2026-08-05  
Driven by: Joan `[plan-discuss] round=1 concern` (fix-now: label-or-code alone is a no-op for full-label parent-log vectors / AC4; discuss: `set_debug_flag(False)` clobber; discuss: hardcoded phase tuple + `total=4`).  
Changes: Added Diagnosis + AC4 Decision (live first, job-carried `*_rubric` snapshot identity fallback, live content-by-code). Stage 1 scoped as DRY only. Stage 2 uses local debug logger handle (never lower shared flag) and phase keys from `JOB_TOKEN_CONFIG`. New Stage 3 implements snapshot fallback. Conf `high` → `Medium`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`
**Tip:** `29c1af56`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `5a7b1f39` | Shared `_find_rubric_criterion`; scoring helpers refactored |
| 2–3 | `29c1af56` | ANALYSIS live-first + `*_rubric` snapshot fallback; Style D found/recorded; `do_task` debug thread |
