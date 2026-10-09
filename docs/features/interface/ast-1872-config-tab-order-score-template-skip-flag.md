<!-- linear-archive: AST-1872 archived 2026-10-08 -->

## Linear archive (AST-1872)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1872/config-tab-order-score-template-and-server-side-skip-flag-recommended  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1862 — Recommended Job Modal Changes  
**Blocked by / blocks / related:** parent: AST-1862; blocks: AST-1874

### Description

## What this implements

Backend and config only: the report top tabs are reordered so Analysis is first, the header title template gains the score placeholder, and the job detail response carries a flag saying whether Skip is legal, decided by core's prior-state rule. No UI changes. #3 consumes the flag and template.

## Citations

`astral.config.config-source-of-truth`, `astral.state.core-decides-transitions`, `astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`.

## Scope

* `src/utils/config.py`: modified constant. The Recommended report top-tab list is reordered so `analysis` comes first and `summary` second, with the rest unchanged. Modified constant: the phase score header title template gains a score placeholder between the phase label and the breakdown, rendering as `{phase_label} - {score} - score: {earned} out of {possible} possible ({max} max total)`. Both already flow to React through the state-UI manifest.
* `src/core/tracker.py`: new public function. Given a current job state and a target state, it returns whether the target's configured prior states admit the current one, reusing the existing private prior-state matcher (so `BUILD_ARTIFACTS` hop sub-states behave exactly as `transition_job_state` treats them). No change to `transition_job_state`.
* `src/ui/api/api_jobs.py`: modified function (job detail route). It attaches a boolean field saying whether the job can move to `CANDIDATE_SKIPPED`, computed through the new tracker function. The field name is `plan-child`'s call. No new route, and the skip route is unchanged.

## Acceptance criteria

1. **Analysis is first and default.** `JOBS_RECOMMENDED_REPORT_TOP_TABS` in `src/utils/config.py` lists `analysis` at index 0 and `summary` at index 1. In `test_JobAnalysisReportModal.test.tsx`, opening the modal with the manifest renders the Analysis pane (phase sections visible) and the tab bar order is Analysis, Summary, Artifacts, Discussion. Switching to a different `jobId` after selecting Summary returns to Analysis. Fail = Summary pane shown on open, or wrong order.
2. **Skip legality is server-resolved.** `GET /api/jobs/<id>` for a job in `RECOMMENDED`, `CANDIDATE_REVIEW`, or a `BUILD_ARTIFACTS` hop sub-state returns the skip-legal flag `true`. For `CANDIDATE_SKIPPED` or `CANDIDATE_APPLIED` it returns `false`. Fail = any of those inverted, or the flag missing.
3. **No new routes or schema.** `git diff origin/dev...<ftr> -- src/data/ src/ui/frontend/src/components/Modal.tsx` is empty, and `grep -n "@jobs_bp.route" src/ui/api/api_jobs.py | wc -l` is unchanged from `origin/dev`. Fail = any change there.

## Boundaries

No UI changes — header layout/labels/Skip button render are #2; modal wiring, default tab, score in headers, skip action are #3.

## Notes for planning

Blocks #3. Citations above are this child's Canon Scope subset of the parent's Architectural definition.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1862-recommended-job-modal-changes`, child `sub/AST-1862/<child-id>-config-tab-order-score-template-skip-flag`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-29T18:35:00.277Z
[code-rubric] PROCEED (Commit: 938dc37) Core-owned can_skip, config tabs

#### betty — 2026-09-29T18:31:36.859Z
`origin/sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag` @ `938dc37d` · manifest in tracker bible

#### joan — 2026-09-29T18:23:03.739Z
[plan-rubric] PROCEED (Commit: be770690) Backend config plan sound

#### katherine — 2026-09-29T18:19:39.709Z
`origin/sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag` @ `be770690` · plan ready, two stages

---

# AST-1872 — Config tab order, score template, and server-side skip flag (Recommended Job Modal Changes)

- **Linear:** [AST-1872](https://linear.app/astralcareermatch/issue/AST-1872) · parent [AST-1862](https://linear.app/astralcareermatch/issue/AST-1862)
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

## Joan validate

[plan-rubric]
**Ticket:** AST-1872
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag` @ `be7706903168f8e1d2ef1b593115393f74aa1caf`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.config.config-source-of-truth | A | | |
| astral.state.core-decides-transitions | A | | |
| astral.layers.ui-config-driven-business-logic | A | | |
| astral.idioms.require-auth-on-protected-endpoints | A | | |

## Traceability

AC1→Stage1 (config tab order + template; modal default/tab-bar asserts N/A—#3); AC2→Stage2 (`can_skip` via `job_state_admits_transition`); AC3→Stages1–2 (no `src/data`/Modal; route count 15 unchanged).

### Findings

- **discuss** — Plan **Canon Scope (id-only)** · Finding: All four frozen ids exist as statute files under `canon/statutes/` but are absent from `canon_clerk.py` roster at this corpus sha (plan cites AST-1678 gap). · Recommendation: Track clerk migration so validate-plan / review-child expansion matches Discussion locks; does not block this plan’s substance.

- **discuss** — Child **AC1** vs **Boundaries** · Finding: AC1 names `test_JobAnalysisReportModal` default tab and tab-bar order; this child explicitly ships no UI (#3 consumes manifest). Stage 1 only satisfies the `config.py` slice. · Recommendation: Betty `qa-child` / #3 manifest should not gate AST-1872 on modal tests; config component tests (~566–573) are the in-scope AC1 proof.

- **acceptable** — Plan **Stage 1 integration note** · Finding: Merging config before #3 may show literal `{score}` in headers until formatter lands. · Recommendation: Accepted partition; documented in plan.

- **acceptable** — Plan **Stage 2** · Finding: `job_state_admits_transition` reuses `_job_state_matches_prior` + `state_prior_states(JOB_STATES, to_state)` aligned with `skip_job` → `transition_job_state(..., "CANDIDATE_SKIPPED")`; `CANDIDATE_SKIPPED.prior_states` is `RECOMMENDED`, `BUILD_ARTIFACTS`, `CANDIDATE_REVIEW` on current `origin/dev` config. · Recommendation: None.

context_tokens≈24000

## Review

| Field | Value |
|-------|-------|
| Branch | `sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag` |
| Build tip | `720a7a60dfbbcdf3131ffbe51c55385e62dfc1ac` |
| Status | Code Complete |

## Radia review

[code-rubric]
**Ticket:** AST-1872
**Publish ref:** 938dc37de79db55403526a988c3e8514cd895f90
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51 · `canon_clerk.py expand` still rejects all four frozen ids (statute files under `canon/statutes/` scored directly; same clerk gap Joan noted at validate-plan)
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.config.config-source-of-truth | A | | |
| astral.state.core-decides-transitions | A | | |
| astral.layers.ui-config-driven-business-logic | A | | |
| astral.idioms.require-auth-on-protected-endpoints | A | | |

## Column diff vs plan stage

(aligned) — Joan APPROVED all four at A; code on `f0cd0de5` / `720a7a60` matches plan Stages 1–2.

## Frame diff

- [x] **Acceptance criteria 1:** Proof for “Analysis first and default” is config manifest + `tests/component/utils/test_config.py` (`test_ast565_recommended_report_manifest_tabs`), not `test_JobAnalysisReportModal` (no UI on this child; #3 owns modal default/tab bar).

## Findings

### fix-now

(none)

### discuss

- **Branch tip vs `origin/dev` (integration)** · `git diff origin/dev origin/sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag` drops recent `origin/dev` work in `src/core/dispatcher.py`, `src/core/monitor.py`, and `src/core/roster.py` (e.g. AST-1867 provider balance-outage handling on dispatcher). AST-1872 commits did not touch those files; `5ee6d34b` resync + epic merge-base history left the sub tip behind dev on those paths. · **Default:** Before `merge-child` rolls this sub into `ftr/AST-1862`, merge `origin/dev` into the publish ref and re-run the AST-1872 test manifest so ftr does not regress shipped dev fixes.

- **Description AC1 vs boundaries** · Linear AC1 still names modal default/tab order in `test_JobAnalysisReportModal`; plan Boundaries and Stage 1 confine this ticket to `config.py` + server flag. Betty’s `46902d66` covers AC1 via config/manifest tests only (appropriate). · **Default:** `resolve-child` §10 ticks AC1 using config component proof; defer modal AC1 to blocked child #3.

### advisory

- **sibling test carry:** `938dc37d merge-tests(AST-1872)` / `46902d66` — `tests/component/core/test_tracker.py`, `tests/component/ui/api/test_api_jobs.py`, `tests/component/utils/test_config.py`, `docs/test-bible/{core/tracker,ui/api/api_jobs,utils/config}.md`; plus unrelated plan-doc bulk from resync/merge-tests in the three-dot stat (not AST-1872 product scope).

- **Three-dot diff noise:** `origin/dev...origin/sub/…` warns *multiple merge bases* and lists many `src/**` paths (e.g. `src/data/database.py` PRAGMA) that are **byte-identical** on `origin/dev` and sub tip; tip-vs-tip product delta for this child is `src/utils/config.py` (tab order + `{score}` template only in AST-1872 commits), `src/core/tracker.py` (`job_state_admits_transition`), `src/ui/api/api_jobs.py` (`can_skip` on `detail()`). Use two-dot or AST-1872 commit range when auditing scope, not three-dot alone.

- **Canon clerk:** Frozen ids remain off `canon_clerk.py` roster; reproducible expand still blocked until clerk migration (AST-1678 pattern).

- **Integration timing:** Literal `{score}` in headers until #3 updates `formatPhaseSectionScoreTitle` — accepted in plan; not a defect on this ticket.

## What's solid

- Stage 1 constants match plan verbatim (`JOBS_RECOMMENDED_REPORT_TOP_TABS` analysis-first; `PHASE_SCORE_HEADER_TITLE_TEMPLATE` with ` - {score} - ` segment).
- `job_state_admits_transition` is a thin public wrapper over `_job_state_matches_prior` + `state_prior_states(JOB_STATES, to_state)` — same gate as `transition_job_state` / `skip_job` → `"CANDIDATE_SKIPPED"`.
- `detail()` keeps `@require_auth`; route count remains 15; `src/data/**` and `Modal.tsx` unchanged tip-vs-tip (AC3 schema/no-UI boundary holds on publish tip).
- Betty tests parametrize admitted/refused states, hop vs non-hop suffix (`BUILD_ARTIFACTS.draft_job_resume` vs `.resume`), KeyError on bad target, and integration-style `can_skip` on the detail route without mocking the core rule.

## Recommended actions (downstream — not for Radia)

1. Chuckles: merge `origin/dev` into `origin/sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag` and re-verify green before ftr merge (dispatcher regression).
2. Chuckles: append this artifact to `docs/features/interface/ast-1872-config-tab-order-score-template-skip-flag.md`, commit `docs(AST-1872): Radia review — clean`, post slim upshot, move to Review Posted.
3. Optional: align Linear AC1 wording with config-test proof (frame diff above) so UAT does not expect modal tests on AST-1872.

```
[code-rubric] PROCEED (Commit: 938dc37) Core-owned can_skip, config tabs
```

context_tokens≈58000

## Resolution

2026-09-29 — resolve-child against Radia review `3737a06c` (Overall CLEAN, no fix-now).

- **discuss — dev drift (dispatcher/monitor/roster):** Default taken. `sync-child.sh` merged `origin/dev` into the sub (`6de3e3ca sync(dev)`); `git diff origin/dev HEAD -- src/core/dispatcher.py src/core/monitor.py src/core/roster.py` is now empty. Betty's manifest item 1 re-run on the merged tip: 35 passed. No AST-1872 product change.
- **discuss — AC1 proof:** Default taken. AC1 ticked on config component proof (`test_ast565_recommended_report_manifest_tabs`, `TestAst1550DiscussionHopKeys`); modal default-tab / tab-bar AC1 deferred to AST-1874. Frame diff row checked above. Linear description carries no checkboxes — nothing to tick there.
- **advisory:** clerk gap, three-dot noise, and `{score}` integration timing acknowledged; no action on this ticket.
