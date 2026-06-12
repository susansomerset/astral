# Job Analysis Report — runtime render from `job_data` (analysis upshot)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-481/job-analysis-report-runtime-render-from-job-data-synthesize-job  
**Parent:** https://linear.app/astralcareermatch/issue/AST-478/synthesize-job-analysis-report-estelle-opus-upshot  

**Publish ref (origin):** `sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`  
**Parent integration ref:** `ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`  

Extend the existing **Job Analysis Report** modal and the **Recommended** jobs surface so the candidate sees structured **`analysis_upshot`** JSON from **`job.job_data`** rendered at runtime (no `builder.py`, no server-stored HTML). Align the Recommended list and row actions with job state **`RECOMMENDED`** once that state exists in config.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Append `RECOMMENDED` to `RECOMMENDED_JOB_STATES` once `JOB_STATES` defines that key (dependency **AST-479**). | utils |
| `src/ui/frontend/src/components/CandidateJobRowActions.tsx` | Include `RECOMMENDED` in `REVIEW_LIKE` so Skip + **Jr** (View Job Analysis) match other review-like states. | ui |
| `src/ui/frontend/src/lib/analysisUpshot.ts` | New module: TypeScript types + `parseAnalysisUpshot(raw: unknown)` derived from **`TASK_CONFIG["analysis_upshot"]["response_schema"]`** (dependency **AST-480** / **AST-313**). | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | After job load, parse `job_data.analysis_upshot` and render sections; keep existing summary, JD preview, Applied footer. | ui |
| `src/ui/frontend/src/App.css` | Styles for upshot sections (spacing, headings, lists) under the existing stylesheet TOC. | ui |

**Not in scope (per ticket):** persisting `analysis_upshot` (**AST-480**), dispatch / `PASSED_LIKE` → `RECOMMENDED` mechanics (**AST-479**), Approve → `BUILD_ARTIFACTS`.

**API:** `GET /api/jobs/<id>` already returns the full job dict from `get_job`; `job_data` is included. No change to `api_jobs.py` unless discovery shows `job_data` is stripped or transformed — if so, stop and comment on **AST-481** (do not guess API shape).

---

## Stage 1: Recommended list + row actions for `RECOMMENDED`

**Done when:** Jobs in state `RECOMMENDED` appear in `/api/jobs?view=recommended` (same candidate scope as today) and show Skip + **Jr** in the actions column; `python3 -m py_compile` on any touched `.py` passes.

1. **`git fetch origin && git merge origin/dev`** on `dev-kath`, then **`git merge origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`** so the publish tip is attached.
2. Open `src/utils/config.py` and verify `JOB_STATES` contains an entry **`"RECOMMENDED"`**. If it does not, **stop** — post on **AST-481** (and reference **AST-479**): build cannot complete this stage without that registry entry. Do not add a new `JOB_STATES` row in **AST-481**; that belongs to the state-machine ticket.
3. If **`RECOMMENDED`** exists in `JOB_STATES` but is missing from **`RECOMMENDED_JOB_STATES`**, append **`"RECOMMENDED"`** to that list (keep a single ordered list; place it with the other post-LIKE review-like states — immediately after **`"PASSED_LIKE"`** is acceptable).
4. In `src/ui/frontend/src/components/CandidateJobRowActions.tsx`, add **`"RECOMMENDED"`** to the **`REVIEW_LIKE`** `Set` alongside `CANDIDATE_REVIEW`, `BUILD_ARTIFACTS`, `PASSED_LIKE`.
5. **`python3 -m py_compile src/utils/config.py`**

⚠️ **Decision:** Nav counts and list queries use **`RECOMMENDED_JOB_STATES`** (`api_system.py` + `api_jobs.py`). Extending that one list keeps list, counts, and config DRY per **ASTRAL_CODE_RULES §2.1 / §1.4** — no duplicate state sets in TS.

---

## Stage 2: Type contract from `TASK_CONFIG`

**Done when:** `analysisUpshot.ts` exists and `tsc` passes; parser returns `null` for non-objects and for payloads missing the minimal bar for “has upshot content” (see step 3).

1. Open `src/utils/config.py` and locate **`TASK_CONFIG["analysis_upshot"]`**. If missing, **stop** — comment on **AST-481** referencing **AST-480** / task authoring (**AST-313**); do not invent field names.
2. From **`response_schema`** (and any nested structure the task uses for the report), define a **`AnalysisUpshot`** type in `src/ui/frontend/src/lib/analysisUpshot.ts` that mirrors every **top-level** property the UI will render. For nested objects/arrays, type them explicitly to match the schema (no `any` on leaves; `unknown` only at the parser boundary).
3. Implement **`parseAnalysisUpshot(raw: unknown): AnalysisUpshot | null`**: return `null` if `raw` is not a non-null object; validate required keys the UI needs for “non-empty when generation succeeded” (per acceptance: at least one substantive field present — use the same fields **`analysis_upshot`** success writes per **AST-480**, e.g. the whole-JD upshot or Estelle take string if those are the required schema fields). Do **not** add a new npm dependency for JSON Schema validation unless one is already in `package.json` (use `typeof` / `Array.isArray` checks).

---

## Stage 3: `JobAnalysisReportModal` runtime render

**Done when:** Opening the report for a job whose `job_data` contains a valid `analysis_upshot` shows readable section content above or below the header block (order: **summary rows → upshot → JD preview → footer**). If `analysis_upshot` is absent or invalid, show a single neutral line in the upshot area: **“No analysis upshot on file.”** Do not crash the modal.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, derive **`const upshot = parseAnalysisUpshot(job?.job_data && (job.job_data as Record<string, unknown>).analysis_upshot)`** (adjust cast to match existing `job_data` access style).
2. If **`upshot` is non-null**, render each top-level field with a heading (derive label from config key: split snake_case → Title Case) and body: plain text in `<p>` / `<div>` for strings; `<ul>` for string arrays; nested objects — render subheadings recursively one level deep if the schema has a single level of nesting; if deeper, render JSON pretty-print inside a `<pre>` for that subtree only (edge case — prefer matching **AST-313** schema depth exactly in **Stage 2** types so this rarely triggers).
3. Preserve the existing **Job Description** block and **Applied** / notes flow unchanged.
4. Do **not** call `builder.py` or add HTML-from-server paths.

---

## Stage 4: Styles

**Done when:** New classes are referenced from **Stage 3** and the modal remains readable in wide layout.

1. In `src/ui/frontend/src/App.css`, add a numbered subsection (update TOC at top of file per house style) for **Job Analysis Report — analysis upshot**: e.g. `.job-analysis-upshot`, `.job-analysis-upshot-section`, list indent, heading size. Use existing CSS variables (`--text-secondary`, etc.) — **ASTRAL_CODE_RULES §3.5**.
2. Do **not** introduce fixed **max-height** / truncation on upshot text unless **Susan** has approved a cap (see project rule: no display limits without confirmation). `overflow: auto` on an existing modal body pattern is only allowed if it matches other entity panels without capping content height arbitrarily.

---

## Stage 5: Verify

**Done when:** Typecheck passes; no new test files (**build-astral** test-tree ban).

1. **`cd src/ui/frontend && npx tsc -b --noEmit`**
2. **`python3 -m py_compile`** on every changed `.py` file (if any).

---

## Execution contract (developer agent)

Per **plan-astral**: execute stages in order; one commit per stage on `dev-kath` with subject containing **`AST-481`**, then cherry-pick to **`origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`** per **build-astral** / **orientation-astral**. If **`JOB_STATES`** / **`TASK_CONFIG["analysis_upshot"]`** / prior_states for Applied transitions are missing, **stop** and comment on **AST-481** with **🛑** format — do not invent backend or schema.

---

## Self-Assessment

**Scope — `Single-Component`**  
Touches one modal, one small lib module, row actions, one config list, and CSS — all UI/config wiring for this ticket.

**Conf — `Medium`**  
Depends on **AST-479** (`RECOMMENDED` in `JOB_STATES`) and **AST-480** / **AST-313** (`TASK_CONFIG` entry + schema); the build agent must confirm those before implementing Stages 1–2.

**Risk — `Medium`**  
A parser/schema mismatch would hide or mis-render the upshot; strict alignment with **`response_schema`** and an explicit empty state mitigates this.

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Single parser module; state list only in `RECOMMENDED_JOB_STATES`.
- **§2.1 config:** Job list states and nav counts stay driven from `config.py` — TS only gets `REVIEW_LIKE` extended for parity with server states.
- **§2.4 / §2.6:** No dispatcher or batch changes in this ticket.
- **§3.3 / §3.5:** No new imports across layers; components stay flat under `components/`, shared types under `lib/`, styles in `App.css`.

No conflicts identified.

---

## Review stub (build)

Built by Katherine.

- **Publish ref:** `sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`
- **Commits:** `3b248584` (parser), `383d455b` (modal), `48f7129f` (App.css)

## Review

**Radia** · 2026-05-24 · three-dot diff `origin/dev…origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`

| | |
|--|--|
| **Tip reviewed** | `5243d1f5d131627473fccfd57e4e50f28465a8e0` |

**What’s solid**

- **`parseAnalysisUpshot`** mirrors **`TASK_CONFIG["analysis_upshot"]["response_schema"]`**, rejects incomplete shapes, returns **`null`** without substantive content; **`JobAnalysisReportModal`** renders above JD preview with accessible region **`aria-label="Analysis upshot"`** and a clear empty line.
- Vitest coverage for parser + modal (**`tests/component/frontend/...`**) exercises happy path + missing/`{}` payloads.
- **`Modal`** guarded close: **`ConfirmContext`** with **`window.confirm`** fallback is documented as test-focused; aligns with **`UserPrompt`** provider expectations in prod.
- **§G1:** No duplicate hardcoded server state lists introduced beyond the existing **`REVIEW_LIKE`** set (candidate-actions pattern unchanged except see issues).

**Issues**

| Sev | Topic | Notes |
|-----|--------|--------|
| fix-now | **`REVIEW_LIKE` regression** | **`CandidateJobRowActions.tsx`** omits **`"RECOMMENDED"`** from **`REVIEW_LIKE`** while **`origin/sub/.../AST-479`** and **`.../AST-480`** include it. Jobs in **`RECOMMENDED`** on **`JobsRecommended.tsx`** therefore get **no** Skip / Jr actions — violates ticket AC (“Wire Recommended list for **`RECOMMENDED`** state”) and Stage 1 of this plan doc. Restore **`"RECOMMENDED"`** (and extend **`test_JobsRecommended`** with a **`RECOMMENDED`** row asserting both buttons). |
| advisory | **`snakeCaseToTitle`** | Naive capitalization yields e.g. “Whole Jd Upshot”; cosmetic unless product wants acronym handling. |

**Recommended actions**

- **`resolve-astral`**: one-line **`REVIEW_LIKE`** fix + targeted test assertion for **`RECOMMENDED`** rows.

**Radia doc commit:** see tip of `origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` after push.

---

## Resolution (2026-05-24)

**Review feedback (Radia fix-now)**

- Restored **`"RECOMMENDED"`** in **`REVIEW_LIKE`** in **`CandidateJobRowActions.tsx`** so Recommended-list rows in **`RECOMMENDED`** show Skip and View Job Analysis (Jr), matching other review-like states.
- Extended **`test_JobsRecommended.test.tsx`** with a **`RECOMMENDED`** row case: POST **`/api/jobs/…/skip`** on Skip; View Job Analysis opens the detail heading for that job title.

Refs: **`resolve-astral`** publish **`sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`**; see Linear comment for tip SHA after push.
