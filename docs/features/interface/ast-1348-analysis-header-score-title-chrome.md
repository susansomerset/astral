# Analysis header score title chrome

**Linear:** [AST-1348](https://linear.app/astralcareermatch/issue/AST-1348/analysis-header-score-title-chrome-add-rubric-score-to-analysis)  
**Parent:** [AST-1346 — Add rubric score to analysis header](https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header)  
**Publish ref (origin):** `sub/AST-1346/AST-1348-analysis-header-score-title-chrome`  
**Parent integration ref:** `ftr/AST-1346-add-rubric-score-to-analysis-header`  
**Depends on:** [AST-1347](https://linear.app/astralcareermatch/issue/AST-1347/persist-phase-score-breakdown-with-grades-add-rubric-score-to-analysis) (persist + flatten of `{prefix}_score_breakdown`; already User Testing on parent ftr)

Render `{Phase label} - score: {earned} out of {possible} possible ({max} max total)` on Recommended Job Report **Analysis** tab section headers (JD / DO / GET / LIKE). Prefer the stored trio from AST-1347 when present; when absent, **derive at read time** in the jobs API from grades + job-carried `*_rubric` via the same `_phase_score_breakdown` helper (do not reimplement the formula in React). Omit the score suffix when the phase is unscored. Does **not** own score-save writes, Recommended list phase-score columns, Summary/Artifacts tabs, or grade-dot header chrome.

Parent brief example numbers (`137 out of 150 possible (320 max total)`) are **format-only**.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree `/home/susan/astral-AST-1346`: run  
   `~/.cursor/scripts/git/sync-child.sh sub/AST-1346/AST-1348-analysis-header-score-title-chrome --ftr AST-1346-add-rubric-score-to-analysis-header --worktree /home/susan/astral-AST-1346/`  
   and require exit 0. Use the **full** parent ftr segment (not bare `AST-1346`) so Ada’s AST-1347 tip is merged.
2. Confirm `PHASE_SCORE_BREAKDOWN_KEY_SUFFIX`, `PHASE_SCORE_BREAKDOWN_FIELDS`, `_phase_score_breakdown`, and `_flatten_grades` breakdown lift from AST-1347 are present on `HEAD` before coding chrome.
3. Do **not** change score-save paths, `{prefix}_score` semantics, or `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS`.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add Analysis header score-title template string; expose on `build_state_ui_manifest()` recommended block | utils |
| `src/ui/api/api_jobs.py` | After stored-trio lift, derive missing `{jd,do,get,like}_score_breakdown` at read time via `_phase_score_breakdown` (response only — never write `job_data`) | ui |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Type the new manifest template field | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Helpers: read breakdown for a grades field; format phase section title with score suffix | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Analysis section `nav_label` uses formatted score title when breakdown is available | ui |

**Out of scope:** consult score-save / persist (AST-1347); Recommended list Score columns / dispatch soft-fail; grade+confidence metadata row (AST-950 / AST-1327); Summary / Artifacts tabs; historical DB backfill; `tests/` / bible (Betty).

**Consume-only contract (AST-1347):**

| Phase | Grades | 0–10 score | Breakdown key | Rubric snapshot |
|-------|--------|------------|---------------|-----------------|
| JD | `jd_grades` | `jd_score` | `jd_score_breakdown` | `jd_rubric` |
| DO | `do_grades` | `do_score` | `do_score_breakdown` | `do_rubric` |
| GET | `get_grades` | `get_score` | `get_score_breakdown` | `get_rubric` |
| LIKE | `like_grades` | `like_score` | `like_score_breakdown` | `like_rubric` |

Breakdown dict keys are exactly `PHASE_SCORE_BREAKDOWN_FIELDS` = `("earned", "possible", "max")`.

---

## Stage 1: Config template for header title shape

**Done when:** `config.py` owns the AC title template and the state-UI manifest exposes it under `jobs.recommended`; no UI behavior change yet.

1. In `src/utils/config.py`, immediately after `PHASE_SCORE_BREAKDOWN_FIELDS`, add:

   ```python
   # AST-1348 — Analysis section header title when a phase breakdown is available
   PHASE_SCORE_HEADER_TITLE_TEMPLATE = (
       "{phase_label} - score: {earned} out of {possible} possible ({max} max total)"
   )
   ```

2. In `build_state_ui_manifest()`, inside the `"recommended"` dict (beside `report_phase_tabs`), add:

   ```python
   "phase_score_header_title_template": PHASE_SCORE_HEADER_TITLE_TEMPLATE,
   ```

3. Do **not** alter `JOBS_RECOMMENDED_REPORT_PHASE_TABS` `nav_label` strings (base labels stay `JD Analysis` / `DO Analysis` / …).

⚠️ **Decision:** Template lives in config + manifest (not a React string literal) so the AC shape is config-sourced under `astral.layers.ui-config-driven-business-logic` / `astral.standards.no-hardcoded-sets`. Placeholders are exactly `phase_label`, `earned`, `possible`, `max`.

---

## Stage 2: API read-time derive when stored trio is absent

**Done when:** Job list/detail JSON that already flattens grades/scores/rubrics also exposes `{prefix}_score_breakdown` for Analysis phases when (a) stored on `job_data`, or (b) derivable from grades + job-carried rubric with a present numeric `{prefix}_score`; dealbreaker / unscored / incomplete inputs leave the key absent; nothing is written back to the DB.

1. In `src/ui/api/api_jobs.py`, import `_phase_score_breakdown` from `src.core.consult` and keep using `PHASE_SCORE_BREAKDOWN_KEY_SUFFIX` / `PHASE_SCORE_BREAKDOWN_FIELDS` from config.

2. After the existing stored-key lift loop in `_flatten_grades`, for each prefix in `("jd", "do", "get", "like")`:

   - `bk = f"{prefix}_{PHASE_SCORE_BREAKDOWN_KEY_SUFFIX}"`
   - If `job` already has `bk` (from the lift loop), **skip**.
   - Resolve inputs preferring flattened top-level then `job_data`:
     - `grades = job.get(f"{prefix}_grades")` (already lifted when present)
     - `score = job.get(f"{prefix}_score")` if key on job else `jd.get(f"{prefix}_score")`
     - `rubric = job.get(f"{prefix}_rubric")`
   - **Derive gate (all required):**
     - `score is not None` (numeric 0–10 present — excludes F2 / unscored paths that omitted `{prefix}_score`)
     - `grades` is a non-empty `list`
     - `rubric` is a non-empty `list`
   - On gate pass, call `_phase_score_breakdown(rubric, grades)` inside `try/except (ValueError, TypeError, KeyError)`:
     - success → set `job[bk]` to the returned dict (response only)
     - exception → leave key absent (do not invent zeros)
   - Do **not** mutate `job["job_data"]` / do **not** call `save_job_data`.

3. Do **not** invent breakdown when grades exist but `{prefix}_score` is missing (dealbreaker / no scorable score — parent AC5 / Joan handoff).

4. Do **not** change `latest_score`, list phase-score column fields, or soft-fail annotations.

⚠️ **Decision:** Derive in `api_jobs` (UI → core), not in React — React must not duplicate contribution math (`pattern.layers.import-discipline` / import-direction). Reuse `_phase_score_breakdown` unchanged.

⚠️ **Decision:** Gate derive on `{prefix}_score is not None` so all-no-signal jobs that still persisted `0.0` + optional stored `{earned:0, possible:0, max:…}` keep a suffix when stored/derivable, while dealbreaker paths that never wrote a score stay label-only.

---

## Stage 3: Frontend title helpers

**Done when:** Pure helpers in `recommendedJobReport.tsx` can resolve a phase breakdown from a job payload and format a section title from the manifest template; no modal wiring yet.

1. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, on `jobs.recommended`, add optional:

   ```ts
   phase_score_header_title_template?: string
   ```

2. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, add:

   ```ts
   /** Top-level flatten or job_data — same lookup style as jobGradesForField. */
   export function jobScoreBreakdownForGradesField(
     job: Record<string, unknown>,
     gradesField: string,
   ): { earned: number; possible: number; max: number } | null
   ```

   Behavior:

   - Derive breakdown key from `gradesField` by replacing a trailing `_grades` with `_score_breakdown` (e.g. `jd_grades` → `jd_score_breakdown`). If `gradesField` does not end with `_grades`, return `null`.
   - Read from top-level `job[breakdownKey]`, else `job.job_data[breakdownKey]` when `job_data` is a plain object.
   - Accept only a plain object whose `earned` / `possible` / `max` are all finite numbers (use those exact key names). Otherwise `null`.

3. Add:

   ```ts
   export function formatPhaseSectionScoreTitle(
     phaseLabel: string,
     breakdown: { earned: number; possible: number; max: number },
     template: string,
   ): string
   ```

   Behavior:

   - Display numbers as **nearest integers** via `Math.round` for `{earned}`, `{possible}`, `{max}` (brief uses whole numbers; floats from contribution math must not leak long decimals into the header).
   - Replace `{phase_label}`, `{earned}`, `{possible}`, `{max}` in `template` (simple split/join or sequential `replaceAll` — no extra templating library).
   - If `template` is empty/missing, fall back to the exact AC shape:  
     `` `${phaseLabel} - score: ${e} out of ${p} possible (${m} max total)` ``  
     using the same rounded ints (defensive only — manifest should always supply the config string after Stage 1).

4. Do **not** call any scoring math in the frontend.

⚠️ **Decision:** Round for **display only** — payload floats stay exact; chrome matches the parent brief’s integer presentation.

⚠️ **Decision (all-no-signal `0/0`):** When a valid breakdown object is present (stored or API-derived), **show** the suffix even if earned/possible are `0` and max is non-zero. Omit only when the helper returns `null` (no grades path / unscored / derive failed). This is the explicit AST-1348 ownership Joan/Radia deferred from AST-1347.

---

## Stage 4: Wire Analysis section headers in the report modal

**Done when:** On the Analysis tab, each phase section header label is the formatted score title when breakdown is available, otherwise the plain manifest `nav_label`; grade+confidence metadata row and section bodies are unchanged; Summary/Artifacts labels unchanged.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, update the `analysisSections` `useMemo` so that for each `report_phase_tabs` entry:

   - Start from `base = p.nav_label`.
   - If `job` is loaded, `breakdown = jobScoreBreakdownForGradesField(jobRec, p.grades_field)`.
   - If `breakdown` is non-null, set  
     `nav_label = formatPhaseSectionScoreTitle(base, breakdown, manifest.jobs.recommended.phase_score_header_title_template ?? "")`.
   - Else keep `nav_label = base`.
   - Keep `section_id: p.tab_id` and `default_expanded: false`.

2. Dependency array must include `job` (and the template via `manifest`) so titles refresh when detail loads.

3. Pass the resulting `nav_label` into `ReportSectionList` as today (`label={section.nav_label}` via `CollapsiblePanel`) — **do not** put the score string in the metadata slot (metadata remains `buildPhaseSectionGradeConfidenceRow`).

4. Do **not** change Summary / Artifacts section label construction.

5. Do **not** alter `JobsRecommended` list columns or any score-floor UI.

---

## Stage 5: Manual smoke (builder)

**Done when:** Hand-check confirms stored trio, derived trio, and unscored omit paths for Analysis headers without touching list Score columns.

1. Optional gitignored notes under `debug/spikes/AST-1348/` only.
2. Verify mentally / against fixtures:
   - Job with `jd_score_breakdown` present → JD header shows formatted title; DO/GET/LIKE same when present.
   - Older job: grades + `*_rubric` + `*_score`, no breakdown key → API derive fills response key → header shows title.
   - Phase with no grades, or grades without `*_score` (dealbreaker) → plain `JD Analysis` (etc.) only.
   - Recommended list still shows 0–10 phase-score columns only.

---

## Self-Assessment

**Scope:** `Single-Component` — API derive-on-read + Analysis header title chrome; no scoring formula changes.

**Conf:** `High` — AST-1347 contract and `_phase_score_breakdown` are on parent ftr; header chrome is a thin format of fields already lifted; AST-950 section wiring is stable.

**Risk:** `Low–Medium` — wrong derive gate could show a score on dealbreaker phases or omit historical headers; mitigated by requiring `{prefix}_score is not None` and reusing the core helper. Display rounding is presentation-only.

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** One core helper for math; one frontend formatter; no second formula in TS.
- **§1.4 / §2.1 / ui-config-driven:** Title template + breakdown field names from config/manifest; phase labels stay on `report_phase_tabs`.
- **§3.2 / §3.3:** `api_jobs` imports core+utils; React consumes JSON + manifest only.
- **Job-carried rubric law (AST-1063):** Derive uses flattened `*_rubric` snapshot, never live candidate artifacts.
- **Boundaries:** No persist writes; no list column / soft-fail changes; grade-dot metadata untouched.

---

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1348
**Overall:** APPROVED
**Publish ref:** `sub/AST-1346/AST-1348-analysis-header-score-title-chrome` @ `c5864e220195da5e9a343a6f803606000ada9803`

## Traceability
AC1 → Stages 2–4 (API derive + `formatPhaseSectionScoreTitle` on JD Analysis header); AC2 → Stages 2–4 (same loop over jd/do/get/like prefixes); AC3 → Stage 2 (read-time `_phase_score_breakdown` when stored trio absent, grades + job-carried rubric + `{prefix}_score` present); AC4 → Stages 2–3–4 (derive gate on `{prefix}_score is not None` + null helper + plain `nav_label` fallback); AC5 → Stages 1–2–4 (no `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS` / `latest_score` / soft-fail / list UI changes).

## Findings

### discuss — derive without explicit completeness check
**Location:** Stage 2 derive gate  
**Finding:** Plan calls `_phase_score_breakdown` when grades/rubric/score are present but does not invoke `_require_complete_grade_set` before derive; mismatched historical payloads would fail into absent key (plain label) rather than AC3 numbers.  
**Recommendation:** Accept for build — jobs that earned a stored `{prefix}_score` should already have had a complete set at grade time; add completeness guard only if Betty surfaces a real fixture gap.

### acceptable — breakdown lookup precedence vs `jobGradesForField`
**Location:** Stage 3 `jobScoreBreakdownForGradesField`  
**Finding:** Helper reads top-level breakdown before `job_data`, opposite of `jobGradesForField` (job_data first).  
**Recommendation:** Intentional — API derive writes top-level only; follow plan as written.

### acceptable — derive runs on list flatten path
**Location:** Stage 2 in `_flatten_grades`  
**Finding:** Breakdown derive would run for list rows even though only the Analysis modal consumes it.  
**Recommendation:** Accept — extra JSON fields do not change list columns (AC5); optimize later only if perf matters.

**R6 checklist:** Definition fidelity ✓ (header chrome only; persist deferred to AST-1347). Layer imports ✓ (`ui/api` → `core.consult` + utils; React consumes JSON/manifest only — matches `pattern.layers.import-discipline`). Config/manifest ✓ (template in `config.py` + `build_state_ui_manifest`; base `nav_label` unchanged on `report_phase_tabs`). DRY ✓ (single core helper; no TS scoring math). Boundaries ✓ (no score-save, no grade-dot metadata row, no Summary/Artifacts label changes). Self-assessment ✓ (High conf justified; derive gate and AST-1347 contract cited). Joan AST-1347 handoff ✓ (explicit 0/0 suffix ownership in Stage 3).

**Statute pass (in-session):** Universal orch set — conforms. Scoped applies — `astral.layers.import-direction`, `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`, `astral.standards.dry-and-focused-functions`, `astral.docs.features-single-file-per-ticket` — all **conforms**. No R3 `violates`; no R5 gaps on child AC 1–5.

**Procedural:** Status `Plan Ready` ✓; assignee Joan ✓; no Plan Discuss rounds.

context_tokens≈48000

---

## Review

**Built:** `origin/sub/AST-1346/AST-1348-analysis-header-score-title-chrome` @ `1a899283958046206b2e24221e461d5016e3b4a5`

Stages 1–4: `PHASE_SCORE_HEADER_TITLE_TEMPLATE` + manifest; `_flatten_grades` read-time derive via `_phase_score_breakdown`; frontend breakdown lookup + title format; Analysis section headers wired in `JobAnalysisReportModal`. Stage 5 smoke: derive when score+grades+rubric present; stored trio wins; no-score omits key. Tests deferred to Betty.

## Radia review

# Radia review — AST-1348

**Publish ref:** `origin/sub/AST-1346/AST-1348-analysis-header-score-title-chrome` @ `cf6cbb5ad886c7959d38896183d379e17d90384e`  
**Diff baseline:** `origin/dev...origin/sub/AST-1346/AST-1348-analysis-header-score-title-chrome` (24 files; **AST-1348 product commit** `1a899283`: `config.py`, `api_jobs.py`, `JobAnalysisReportModal.tsx`, `StateUiContext.tsx`, `recommendedJobReport.tsx`)

```
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1348
**Publish ref:** `sub/AST-1346/AST-1348-analysis-header-score-title-chrome` @ `cf6cbb5a`
**Overall:** DISCUSS
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent/confidence validation changes on AST-1348 product commit. |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No `do_task` changes on AST-1348 product commit. |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | Derive reuses existing helper; no grade-set rule edits. |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch API signature changes on AST-1348 product commit. |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch_id format changes. |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/process/finally edits. |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No agent_response persistence changes. |
| `astral.config.config-source-of-truth` | scoped | conforms | `PHASE_SCORE_HEADER_TITLE_TEMPLATE` + manifest field in `config.py`. |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env handling. |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No repo-root artifact dirs. |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No committed spike files. |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch seed paths. |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No run-next / chain edits. |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Plan doc at `docs/features/interface/ast-1348-…`. |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Product `src/` from engineer; bible/tests from Betty merge. |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer product commit is `src/` only. |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | No external imports; core helper via allowed ui→core path. |
| `astral.layers.import-direction` | scoped | conforms | `api_jobs` imports `core.consult` + `utils.config` only; React consumes JSON/manifest. |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/` changes. |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Title template from manifest; base `nav_label`s unchanged on `report_phase_tabs`. |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No coat-check paths. |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No score-save / orchestration edits on AST-1348 product commit. |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | No route/auth changes. |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed table edits. |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No catalog conflicts. |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No seed boot paths. |
| `astral.seed.define-approved` | scoped | not-applicable | No define/seed work. |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No operator seed rows. |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage-join seed logic. |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No `src/data/` changes. |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No DB/migration changes. |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | No new debug emission on AST-1348 product paths. |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Single core helper for math; frontend format-only helpers. |
| `astral.standards.in-scope-only` | scoped | conforms | Product commit touches only plan files (config, api_jobs, frontend chrome). |
| `astral.standards.logging-via-utils` | scoped | conforms | No `print()` / raw `logging` imports added. |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Runtime keys/template placeholders are domain names; ticket id in comments only. |
| `astral.standards.no-cross-contamination` | scoped | conforms | Layer imports legal; no out-of-layer deps. |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Template from config/manifest; phase prefixes from existing tab config. |
| `astral.standards.public-then-helpers` | scoped | conforms | Frontend exports public helpers; core reuse is plan-mandated private import. |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No utils→data late-import edits. |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No transition changes on AST-1348 product commit. |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No prior-state enforcement edits. |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run/daisy-chain edits. |
| `astral.ui.frontend-file-placement` | scoped | conforms | Helpers in `lib/recommendedJobReport.tsx`; modal wiring in `components/`. |
| `astral.ui.naming-conventions` | scoped | conforms | camelCase TS helpers; snake_case API keys consistent with flatten. |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No server worker config. |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Tip is `merge-tests(AST-1348): origin/tests 2092f7bf`. |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `docs` / `merge-tests` / `resolve` vocabulary on branch. |
| `orch.git.flow-direction-inviolable` | universal | conforms | Sub off parent epic; no dev/main writes. |
| `orch.git.ftr-sub-topology` | universal | conforms | Child on `sub/AST-1346/AST-1348-…`. |
| `orch.git.merge-on-checkout` | universal | conforms | Branch includes `resolve(AST-1347)` + ftr sync prerequisite satisfied. |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | None observed. |
| `orch.git.no-dev-agent-branches` | universal | conforms | Publish ref is `sub/…`. |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Reviewed in `astral-AST-1346` worktree. |
| `orch.git.three-permanent-branches` | universal | conforms | Diff vs `origin/dev` only. |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | 0/0 suffix display ownership explicit in plan Stage 3. |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–4 match plan on product commit. |
| `orch.pipeline.project-scoped-queues` | universal | conforms | N/A to code diff. |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Review at Tests Passed per pipeline. |
| `orch.roles.archie-approves-statutes` | universal | conforms | N/A to implementation. |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Tests/bible from Betty + merge-tests. |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | N/A to code. |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine remains assignee. |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No hook-ban violations in product paths. |

**Active set count:** 65 scored in-session.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | `PHASE_SCORE_HEADER_TITLE_TEMPLATE` added beside scoring constants; exposed via manifest. |
| `pattern.layers.import-discipline` | conforms | Derive in `api_jobs` (ui→core); React has no scoring math (matches `api_admin` consult import precedent). |

## Plan adherence

Stages 1–4 land on product commit `1a899283`: config template + `build_state_ui_manifest()` field; `_flatten_grades` lifts stored trio then derives missing breakdown (response-only, gated on `{prefix}_score is not None` + non-empty grades + rubric); frontend helpers validate finite `earned|possible|max`, round for display, wire Analysis `nav_label` only. Boundaries held: no score-save edits on this commit, no list column / `latest_score` / soft-fail changes, grade-dot metadata row untouched, Summary/Artifacts labels unchanged. Estimate **2** fits. Betty manifest covers config/manifest, API derive/omit/stored, lib helpers (incl. 0/0 fallback), and modal chrome.

## Findings

### discuss — Sibling ticket test commit on AST-1348 sub-branch

**Location:** Branch history `c7bed34b test(AST-1343)` + `tests/component/frontend/pages/test_CandidateProfile.test.tsx`  
**Finding:** AST-1343 (Candidate Profile dirty-state bug, different parent) test landed on this sub ref alongside AST-1348 work. Same pattern as AST-1341/1342 on AST-1347.  
**Recommendation:** Not a product fix for Katherine. Chuckles should confirm sibling bug-lane tests stay bundled through `ftr` merge or get split before parent rollup.

### discuss — Derive failures swallowed without log

**Location:** `src/ui/api/api_jobs.py` `_flatten_grades` derive loop  
**Finding:** `try/except (ValueError, TypeError, KeyError): pass` leaves breakdown absent on bad historical payloads — plan-intended, but no stderr/debug signal when derive fails.  
**Recommendation:** Accept per plan; optional advisory log at `debug_detail` if operators need visibility — not required for merge.

### discuss — Derive without explicit completeness check

**Location:** `src/ui/api/api_jobs.py` derive gate  
**Finding:** Joan flagged: no `_require_complete_grade_set` before `_phase_score_breakdown`; mismatched historical grades+rubric+score → absent key → plain label.  
**Recommendation:** Accept as planned; jobs that earned `{prefix}_score` should have been complete at grade time.

### advisory — Breakdown lookup comment vs `jobGradesForField` precedence

**Location:** `src/ui/frontend/src/lib/recommendedJobReport.tsx` `jobScoreBreakdownForGradesField`  
**Finding:** Docstring says “same lookup style as `jobGradesForField`” but reads top-level before `job_data` (opposite of grades helper). Joan accepted as intentional for API-flattened payloads.  
**Recommendation:** Optional comment fix in resolve pass; behavior is correct.

### advisory — Modal test uses stored breakdown only

**Location:** `test_JobAnalysisReportModal.test.tsx` AST-1348 case  
**Finding:** Modal test asserts stored `jd_score_breakdown`; API derive path covered separately in `TestAst1348FlattenDeriveBreakdown`.  
**Recommendation:** Sufficient split coverage; end-to-end derive→modal path is implicit via flatten contract.

## What's solid

- Product commit is tightly scoped (5 files) and plan-faithful.
- Derive gate correctly requires `{prefix}_score is not None` — dealbreaker/unscored stay label-only.
- Stored trio wins (skip derive when key already lifted); `job_data` never mutated.
- `formatPhaseSectionScoreTitle` rounds for display; empty-template fallback matches AC shape; 0/0 suffix shown per Stage 3 decision.
- `analysisSections` deps include `job` + manifest template; metadata row and Summary/Artifacts paths untouched.
- Tests cover derive, stored-trio retention, unscored omit, helper validation, manifest constant, and modal chrome.

## Frame diff

`(none)` — first Radia pass on AST-1348.

Product frame under review (`1a899283`):
- `src/utils/config.py`: `PHASE_SCORE_HEADER_TITLE_TEMPLATE` + manifest exposure
- `src/ui/api/api_jobs.py`: read-time derive in `_flatten_grades`
- `src/ui/frontend/src/lib/recommendedJobReport.tsx`: breakdown lookup + title formatter
- `src/ui/frontend/src/contexts/StateUiContext.tsx`: manifest type
- `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`: Analysis header wiring

**Note:** Three-dot diff vs `origin/dev` also includes AST-1347 dependency stack (consult persist, breakdown constants, flatten lift) — expected prerequisite per plan gate; not AST-1348 scope creep.

## Notes

- Joan plan-rubric verdict attached (APPROVED); no Excluded-statute stragglers.
- AST-1347 Radia discuss items (0/0 suffix, sibling tests) addressed in AST-1348 plan Stage 3 — implementation matches.
- No fix-now product defects; engineer `resolve-child` not required for product code on this pass.

context_tokens≈58000
