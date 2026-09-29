# AST-1872 — Config tab order, score template, and server-side skip flag (Recommended Job Modal Changes)

- **Linear:** [AST-1872](https://linear.app/astral/issue/AST-1872) · parent [AST-1862](https://linear.app/astral/issue/AST-1862)
- **Publish ref:** `origin/sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag`
- **Assignee:** Katherine

Backend and config only, for the Recommended Job Report modal. Reorder the report top tabs so
Analysis comes first. Add a `{score}` placeholder to the Analysis phase header title template.
Also add a boolean to `GET /api/jobs/<id>` saying whether the job can legally move to
`CANDIDATE_SKIPPED`. Core decides that, reusing the same prior-state matcher
`transition_job_state` enforces. No UI changes: AST-1862 child #3 (Ada) consumes the flag and the
template, and #2 (Hedy) renders the Skip button.

## Scope check

Every file below is named in this ticket's `## Scope`, and every change is the kind Scope
describes:

- `src/utils/config.py`: two **modified constants** (`JOBS_RECOMMENDED_REPORT_TOP_TABS` order,
  `PHASE_SCORE_HEADER_TITLE_TEMPLATE` text).
- `src/core/tracker.py`: one **new public function** wrapping the existing private
  `_job_state_matches_prior`. `transition_job_state` is untouched.
- `src/ui/api/api_jobs.py`: **modified function** `detail()` (job detail route) attaches one
  boolean. No new route; `skip_job` is unchanged.

No scope gap.

## Canon Scope (id-only at plan)

`astral.config.config-source-of-truth`, `astral.state.core-decides-transitions`,
`astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`.

None of the four is a pattern, so per `canon-index` § Who reads what they stay id-only until
build-child §8. **Clerk note:** `python3 canon/canon_clerk.py expand <ids>` fails
`unknown directive id(s)` for all four at corpus `e1f2699fad` (the roster holds 21 directives, and
none of them use the `astral.config/state/layers/idioms` scopes). This is the same clerk-migration gap
recorded in `docs/features/foundation/ast-1678-catalog-resume-structure-body-shape.md`. Joan
curates the list at validate-plan.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Reorder `JOBS_RECOMMENDED_REPORT_TOP_TABS` (analysis, summary, …); add `{score}` segment to `PHASE_SCORE_HEADER_TITLE_TEMPLATE` | utils |
| `src/core/tracker.py` | New public `job_state_admits_transition(current_state, to_state) -> bool` | core |
| `src/ui/api/api_jobs.py` | Import the new function; `detail()` sets `job["can_skip"]` | ui |

No other files. `src/data/**`, `Modal.tsx`, and every frontend file stay untouched (AC 3).

## Stage 1: Config — tab order and score template

**Done when:** `JOBS_RECOMMENDED_REPORT_TOP_TABS[0]["tab_id"] == "analysis"` and `[1]["tab_id"] == "summary"`,
and `PHASE_SCORE_HEADER_TITLE_TEMPLATE` equals
`"{phase_label} - {score} - score: {earned} out of {possible} possible ({max} max total)"`. Both
reach the state-UI manifest unchanged through the existing lines at `config.py` ~4250–4252.

1. In `src/utils/config.py`, in `JOBS_RECOMMENDED_REPORT_TOP_TABS` (currently ~line 3439), swap the
   first two entries so the list reads, in order:
   ```python
   {"tab_id": "analysis", "nav_label": "Analysis"},
   {"tab_id": "summary", "nav_label": "Summary"},
   {"tab_id": "artifacts", "nav_label": "Artifacts"},
   {"tab_id": "discussion", "nav_label": "Discussion"},
   {"tab_id": "meteorite", "nav_label": "Meteorite"},
   ```
   Update the comment above it to:
   `# AST-948 / AST-1550 / AST-1691 / AST-1872: top-level Recommended report tabs — first entry is the default tab (Meteorite after Discussion).`
2. In `src/utils/config.py`, replace `PHASE_SCORE_HEADER_TITLE_TEMPLATE` (currently ~line 1180) with:
   ```python
   PHASE_SCORE_HEADER_TITLE_TEMPLATE = (
       "{phase_label} - {score} - score: {earned} out of {possible} possible ({max} max total)"
   )
   ```
   Update the comment above it to:
   `# AST-1348 / AST-1872 — Analysis section header title when a phase breakdown is available; {score} = list phase score (UI drops " - {score}" when absent)`
3. Do **not** touch the manifest wiring (`"report_top_tabs"` / `"phase_score_header_title_template"`
   keys, ~lines 4250–4252). They already pass both constants through.
4. `python3 -m py_compile src/utils/config.py`.
5. Commit: `code(AST-1872): config — Analysis-first report tabs, {score} header placeholder`. Publish per build-child §9.

⚠️ **Decision:** The literal ` - {score}` segment lives in the template, so the frontend (#3) can
drop it as one unit when a phase has no list score, per #3's Scope ("the ` - {score}` segment is
dropped, not rendered as an em dash"). The template carries no conditional logic.

⚠️ **Integration note (no action here):** Today's `formatPhaseSectionScoreTitle` in
`src/ui/frontend/src/lib/recommendedJobReport.tsx` fills only `{phase_label}/{earned}/{possible}/{max}`.
If this child merges to `ftr/AST-1862` before #3 does, Analysis headers render a literal `{score}`
until #3 lands. #3 owns that formatter (it's blocked by this ticket), so this is expected and is
**not** fixed here.

## Stage 2: Core skip-legality query and detail-route flag

**Done when:** `GET /api/jobs/<id>` returns `"can_skip": true` for jobs in `RECOMMENDED`,
`CANDIDATE_REVIEW`, `BUILD_ARTIFACTS`, or any `BUILD_ARTIFACTS.<hop>` sub-state whose `<hop>` is a
`TASK_CONFIG` key (e.g. `BUILD_ARTIFACTS.draft_job_resume`), and `"can_skip": false` for `CANDIDATE_SKIPPED` and
`CANDIDATE_APPLIED`. `transition_job_state` and `skip_job` are unchanged, and the
`@jobs_bp.route` count stays at 15.

1. In `src/core/tracker.py`, directly **after** `_job_state_matches_prior` (currently ends ~line 1354) and
   **before** `legal_job_successor_states`, add:
   ```python
   def job_state_admits_transition(current_state: str, to_state: str) -> bool:
       """True when to_state's configured prior_states admit current_state (AST-1872).

       Same rule transition_job_state enforces — hop sub-states resolve via their base.
       Raises KeyError when to_state is not a registered JOB_STATES key (config error, fail loud).
       """
       return _job_state_matches_prior(current_state, state_prior_states(JOB_STATES, to_state))
   ```
   Do not change any imports: `JOB_STATES` and `state_prior_states` are already imported from
   `src.utils.config`.
2. In `src/ui/api/api_jobs.py`, add `job_state_admits_transition,` to the `from src.core.tracker import (...)`
   block, in alphabetical position (between `hydrate_job_artifacts_for_display,` and
   `job_misses_dispatch_score_floor,`).
3. In `src/ui/api/api_jobs.py` `detail()`, immediately after the line `_attach_skipped_edit_meta(job)`, add:
   ```python
       # AST-1872: server-resolved Skip legality for the Recommended report (core owns the prior-state rule)
       job["can_skip"] = job_state_admits_transition(job.get("state") or "", "CANDIDATE_SKIPPED")
   ```
4. Leave `skip_job`, `transition_job_state`, `_attach_skipped_edit_meta`, and every route decorator
   unchanged. `detail()` keeps its existing `@require_auth`.
5. `python3 -m py_compile src/core/tracker.py src/ui/api/api_jobs.py`.
6. Sanity check by hand (not committed): in a Python shell with the repo env,
   `from src.core.tracker import job_state_admits_transition as f` must satisfy
   `f("RECOMMENDED","CANDIDATE_SKIPPED")`, `f("CANDIDATE_REVIEW","CANDIDATE_SKIPPED")`,
   `f("BUILD_ARTIFACTS","CANDIDATE_SKIPPED")`, `f("BUILD_ARTIFACTS.draft_job_resume","CANDIDATE_SKIPPED")`
   (hop suffix must be a `TASK_CONFIG` key — e.g. `BUILD_ARTIFACTS.resume` is **not** a hop and returns `False`),
   `not f("CANDIDATE_SKIPPED","CANDIDATE_SKIPPED")`, and `not f("CANDIDATE_APPLIED","CANDIDATE_SKIPPED")`.
   If any of these fails, stop and comment (see Execution contract).
7. Verify AC 3: `git diff origin/dev -- src/data/ src/ui/frontend/src/components/Modal.tsx` is empty;
   `grep -n "@jobs_bp.route" src/ui/api/api_jobs.py | wc -l` prints `15`.
8. Commit: `code(AST-1872): core job_state_admits_transition + detail can_skip flag`. Publish per build-child §9.

⚠️ **Decision (approach):** I considered three options. (a) A new public tracker wrapper around
`_job_state_matches_prior` + `state_prior_states`. **Chosen**: this is the approach Scope names,
it's one line of logic, and it can't drift from `transition_job_state`. (b) Having the API check
`JOB_STATES["CANDIDATE_SKIPPED"]["prior_states"]` directly. **Rejected**: the UI layer would
re-implement the core rule and miss hop sub-states. (c) A `dry_run` kwarg on
`transition_job_state`. **Rejected**: Scope says no change to `transition_job_state`.

⚠️ **Decision (field name):** The response field is **`can_skip`** (boolean, always present on
detail). Child #3 reads `job.can_skip`.

⚠️ **Decision (target literal):** `"CANDIDATE_SKIPPED"` is passed as a literal, the same one
`skip_job` already passes to `transition_job_state`, so the flag and the action always name the
same target. Adding a new config constant would widen `config.py` beyond the two constants Scope
names.

⚠️ **Decision (unregistered target):** `job_state_admits_transition` lets `state_prior_states`
raise `KeyError` for an unregistered `to_state` instead of returning `False`. A typo'd target is a
config error and should fail loud, not silently hide Skip. `CANDIDATE_SKIPPED` is registered, so
`detail()` never hits this.

## Test fallout (Betty — qa-child; engineer does not touch `tests/`)

- `tests/component/utils/test_config.py` (~566–573) asserts the old `report_top_tabs` order.
- Frontend tests asserting a Summary default belong to #3's scope and Betty's revisions there.
- New coverage for `job_state_admits_transition` and `can_skip` is Betty's manifest.

## Execution contract

Binding. Execute steps in order, stages in order. Do not add files, imports beyond Stage 2 step 2,
constants, or routes. If a referenced line, name, or signature has drifted from what's written
here, or step 6's sanity check fails, stop and comment on parent AST-1862:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage is one commit on the epic worktree, published to
`origin/sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag` before the next stage starts.

## Estimate

Confirm Chuckles estimate: 2 — agree
