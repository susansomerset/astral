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
