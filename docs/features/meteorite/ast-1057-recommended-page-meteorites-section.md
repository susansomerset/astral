# AST-1057 — Recommended page Meteorites section

**Linear:** [AST-1057](https://linear.app/astralcareermatch/issue/AST-1057/recommended-page-meteorites-section-processing-meteorites)
**Parent:** [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — Processing meteorites
**Publish ref:** `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`

Show a distinct **Meteorites** section on the Recommended page for post-upshot meteorite-track jobs (company short_name under `METEORITE_CONFIG["short_name_prefix"]`), while non-meteorite jobs stay in the existing Recommended / In Progress / Ready state sections. Does **not** own GDL states, dispatch, agent prompts, or Create landing.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add meteorite Recommended section block; expose on `build_state_ui_manifest()` | utils |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Type the new `meteorite_section` manifest field | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Partition rows: Meteorites section vs normal state sections | ui |

## Stage 1: Config + state UI manifest — Meteorites section contract

**Done when:** Manifest `jobs.recommended.meteorite_section` exposes `section_id`, `label`, and `company_prefix` from `METEORITE_CONFIG`; no GDL / dispatch / Create / agent_task changes.

1. In `src/utils/config.py`, immediately after `JOBS_RECOMMENDED_UI_SECTIONS` (and before `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS` is fine), add:

```python
# AST-1052 / AST-1057: Recommended page — distinct Meteorites section membership.
# Jobs already land in RECOMMENDED / BUILD_ARTIFACTS / CANDIDATE_REVIEW after meteorite_upshot
# (AST-1055); partition by company short_name prefix, not by a new job state.
JOBS_RECOMMENDED_METEORITE_SECTION = {
    "section_id": "meteorites",
    "label": "Meteorites",
    "company_prefix": METEORITE_CONFIG["short_name_prefix"],  # "meteorite-"
}
```

Assert: `JOBS_RECOMMENDED_METEORITE_SECTION["company_prefix"]` equals `METEORITE_CONFIG["short_name_prefix"]` and is a non-empty `str`. Do **not** invent a parallel `METEORITE_RECOMMENDED` job state.

⚠️ **Decision — membership by company short_name prefix, not state:** After AST-1055, meteorite upshot lands on shared `RECOMMENDED` (priors already allow `METEORITE_PASSED_LIKE` / `METEORITE_PASSED_LIKE_RETRY`). A new Recommended state would duplicate the surface and break Generate Artifacts / Ready flows. Prefix membership reuses `METEORITE_CONFIG` as the single source of truth for placeholder employers.

2. In `build_state_ui_manifest()`, under the existing `"recommended"` dict, add:

```python
"meteorite_section": {
    "section_id": JOBS_RECOMMENDED_METEORITE_SECTION["section_id"],
    "label": JOBS_RECOMMENDED_METEORITE_SECTION["label"],
    "company_prefix": JOBS_RECOMMENDED_METEORITE_SECTION["company_prefix"],
},
```

Do **not** add extra rows to `JOBS_RECOMMENDED_UI_SECTIONS` / `RECOMMENDED_JOB_STATES` (those stay state-driven for non-meteorite sections). Do **not** edit `TASK_CONFIG`, `METEORITE_DISPATCH_TASKS`, Create defaults, or agent_task JSON.

**Done when (recheck):** `build_state_ui_manifest()["jobs"]["recommended"]["meteorite_section"]["company_prefix"] == "meteorite-"`; `python3 -m py_compile src/utils/config.py` succeeds.

## Stage 2: Recommended page — Meteorites section UI

**Done when:** On `/jobs/recommended`, meteorite-company jobs appear under a **Meteorites** heading (when any exist); the existing Recommended / In Progress / Ready sections list only non-meteorite jobs for those states; empty-state and report modal behavior for remaining jobs unchanged.

1. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, extend `StateUiManifest.jobs.recommended` with optional:

```ts
meteorite_section?: {
  section_id: string
  label: string
  company_prefix: string
}
```

2. In `src/ui/frontend/src/pages/JobsRecommended.tsx`, update the `sections` `useMemo` (currently groups solely by `job.state` against `manifest.jobs.recommended.sections`):

- Read `prefix = manifest.jobs.recommended.meteorite_section?.company_prefix ?? ""`.
- Define `isMeteoriteJob(job) => Boolean(prefix) && job.company.startsWith(prefix)`.
- Split `rows` into `meteoriteRows` and `normalRows` using that predicate.
- Build **normal** state sections exactly as today, but iterate **`normalRows` only** (so meteorite jobs never appear under Recommended / In Progress / Ready).
- If `meteoriteRows.length > 0` and `meteorite_section` is present, **prepend** one section object:

```ts
{
  state: meteorite_section.section_id,  // sort-key / React key — "meteorites", not a JOB_STATES value
  label: meteorite_section.label,
  jobs: meteoriteRows,
}
```

  before the normal state sections. Keep legacy unmapped handling on **`normalRows` only**.

- Reuse the existing table markup for the Meteorites section (same columns, sort, row click → Job Analysis Report, `CandidateJobRowActions`). Do **not** invent a second table design.

⚠️ **Decision — one Meteorites section spanning all recommended-surface states:** Meteorite jobs in `RECOMMENDED`, `BUILD_ARTIFACTS`, and `CANDIDATE_REVIEW` all list under **Meteorites**. Splitting Meteorites × state would clutter the page; primary actions still key off `job.state` via existing `CandidateJobRowActions` / `primary_actions_by_state`.

⚠️ **Decision — prepend Meteorites when non-empty:** Makes the parallel track visible above the vetted Recommended stack. Do not render an empty Meteorites heading when there are zero matching rows.

3. Do **not** change `/api/jobs?view=recommended` payload shape (company field is already present). Do **not** change report modal / summary “Company Upshot” copy on this ticket. Do **not** edit `tests/` or bible.

**Done when (recheck):** `cd src/ui/frontend && npx tsc -b --noEmit` succeeds; reading `JobsRecommended.tsx` shows partition by `company_prefix` and a prepended Meteorites section; non-meteorite path still groups by `manifest.jobs.recommended.sections` states only.

## Out of scope (do not implement here)

- Parallel GDL `JOB_STATES` (AST-1053 — landed).
- Dispatch rows / `score_floor` 0 (AST-1054).
- `meteorite_like` / `meteorite_upshot` prompts (AST-1055).
- Create landing / `METEORITE_CONFIG["job_create_state"]` (AST-1056).
- Changing non-meteorite Recommended section labels, report tabs, or artifact generate API.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — Recommended list UI + config/manifest contract for one section; no core GDL / dispatch.

**Conf:** `high` — company short_name prefix already owned by `METEORITE_CONFIG`; page already manifests sections from config; partition is a localized `useMemo` change.

**Risk:** `Medium` — wrong prefix predicate could hide vetted Recommended jobs or leak meteorites into normal sections; mitigated by literal reuse of `METEORITE_CONFIG["short_name_prefix"]` and excluding meteorite rows from state sections.

## Rules self-review

- **§2.1 / config-source-of-truth / no-hardcoded-sets:** Section label + prefix live in config; UI reads via manifest only (no inline `"meteorite-"` string in the page).
- **§3.3 / import-direction:** UI → manifest JSON from API; no UI importing core/data.
- **Boundaries:** No states / dispatch / prompts / Create edits.
- **AC6 smoke (non-meteorite Recommended unchanged):** Normal sections still driven by `JOBS_RECOMMENDED_UI_SECTIONS` + `RECOMMENDED_JOB_STATES`; only membership filter changes.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`
**Plan path:** `docs/features/meteorite/ast-1057-recommended-page-meteorites-section.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `60f68589` | `JOBS_RECOMMENDED_METEORITE_SECTION` + manifest `meteorite_section` |
| 2 | `f1c1808b` | JobsRecommended partition + StateUi `meteorite_section` type |

**Tip:** `fec43afc1fc9aaf94d4578ee63f6cced1494e686` on `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1057
**Publish ref:** `37796488b181d764bf4308f7ae1a5334043d1a96` (`origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`)
**Overall:** DISCUSS

### What’s solid
- `JOBS_RECOMMENDED_METEORITE_SECTION` + manifest `meteorite_section`; prefix from `METEORITE_CONFIG`.
- JobsRecommended partitions by manifest prefix; meteorites prepended; normal sections use normalRows only.
- No hardcoded `meteorite-` in the page; no new Recommended job state.

### Issues
- **discuss (straggler ×14):** Joan excluded core/batch/docs/tests statutes at plan time (Files Changed utils+ui); three-dot vs `origin/dev` includes stacked sibling product + Betty tests/docs — all **conforms** on substance.

### Recommended actions
- Katherine: acknowledge stragglers → resolve-child → User Testing.

