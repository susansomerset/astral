<!-- linear-archive: AST-481 archived 2026-06-15 -->

## Linear archive (AST-481)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-481/job-analysis-report-runtime-render-from-job-data-synthesize-job  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** katherine  
**Priority / estimate:** High / 5  
**Parent:** AST-478 — Synthesize job analysis report (Estelle Opus upshot)  
**Blocked by / blocks / related:** parent: AST-478

### Description

## What this implements

Extend **AST-307** Job Analysis Report and jobs API so the candidate sees the `analysis_upshot` JSON rendered **at runtime** in the modal. Wire Recommended list for `RECOMMENDED` state.

## Acceptance criteria

3. Opening the Job Analysis Report for a job with saved report JSON shows the upshot (non-empty when generation succeeded).

## Boundaries

* Does **not** implement `analysis_upshot` backend (**AST-480**).
* Does **not** use `builder.py` for this report.
* Does **not** implement Approve → `BUILD_ARTIFACTS`.

## Notes for planning

* `api_jobs.py`, `JobAnalysisReportModal.tsx`, `JobsRecommended.tsx`, state UI manifest.

## Git branch (authoritative)

`sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` · parent `ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`

### Comments

#### chuckles — 2026-05-25T04:04:29.771Z
[rollup-child] sub → ftr

Child: AST-481
Publish ref: origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data
Parent ftr: origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot @ db2e395b

— Chuckles

#### katherine — 2026-05-25T04:02:46.682Z
Review feedback resolved. Branch `sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` ready for prep-uat. Parent AST-478.

- `fix(AST-481)`: restored `"RECOMMENDED"` in `REVIEW_LIKE` (`CandidateJobRowActions.tsx`).
- `test(AST-481)`: `JobsRecommended` case for RECOMMENDED row — Skip POSTs `/api/jobs/j-rec/skip`; View Job Analysis opens detail heading.
- `docs(AST-481)`: plan Resolution appendix.

Publish tip: **24c29553** — Katherine

`origin/dev` dry-run (resolve §9a): **clean**. `origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot` dry-run: **clean**.

#### radia — 2026-05-25T03:59:32.460Z
## Radia review (`review-astral`)

**Diff:** `origin/dev…origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`  
**Code tip reviewed:** `5243d1f5d131627473fccfd57e4e50f28465a8e0`

**Counts:** fix-now **1** · discuss **0** · advisory **1**

**Fix-now — `REVIEW_LIKE` regression:** **`CandidateJobRowActions.tsx`** is missing **`"RECOMMENDED"`** in **`REVIEW_LIKE`** even though **`AST-479`** / **`AST-480`** publish tips include it. **`JobsRecommended`** uses this component → **`RECOMMENDED`** rows get **no** Skip / Jr. Restore the token and add a **`RECOMMENDED`** row to **`test_JobsRecommended`** (or equivalent).

**Advisory:** **`snakeCaseToTitle`** is naive for acronyms ("Jd"); cosmetic unless copy wants acronym maps.

Otherwise: **`parseAnalysisUpshot`**, modal wiring, **`aria-label`**, and empty-state copy look good versus **`TASK_CONFIG`** and AC3.

**Doc commit:** `cdefb2fe` → same publish ref  
Markdown: [`ast-481-…`](https://github.com/susansomerset/astral/blob/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data/docs/features/consult/ast-481-job-analysis-report-runtime-render-from-job-data.md) — appendix **## Review**

**Tolerances accepted:** **`Modal` → `window.confirm`** fallback without provider — acceptable with in-code rationale for tests (see **`Modal.tsx`**).

#### katherine — 2026-05-25T03:57:09.982Z
[check-linear]

- **§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **already up to date**.
- **§0b / §2 (scoped to inbox for this ticket):** Full thread on **AST-481** — newest author is **Katherine** (**Tests Passed**). No teammate comment **after** that post **`@katherine`** me or plainly expecting a Katherine reply beyond the documented manifest handoff (**Betty** **§5b** cleared; **Tests Passed** logged).
- **Publish ref parity:** **`origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`** tip **`5243d1f5`** — `git rev-parse refs/remotes/origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` matches **`git ls-remote`**. Happy-path build + QA + Katherine **`test-astral`** verification already landed on remote; nothing additional to cherry-pick or push for **AST-481** from this pass.
- **Note:** **`dev-kath`** still carries unpublished merge/integration commits vs **`origin/dev-kath`** (~73 ahead) — out of scope for the **481** **`sub/`** publish line unless you want integration publish separately.

#### katherine — 2026-05-25T03:55:59.791Z
**Tests Passed — Katherine**

**Integration:** `git fetch origin`; `dev-kath`; merged `origin/dev` (already up to date); merged `origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` — tip **`5243d1f5`** verified (`git rev-parse` matches Betty’s Tests Ready manifest).

**Commands run (Betty numbered manifest — latest Tests Ready comment):**

1. Narrow Vitest:
```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/lib/test_analysisUpshot.test.ts ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```
**Result:** 2 files, 7 tests passed.

2. Component gate pytest slice (+ harness downstream Vitest from `run_component_tests.sh`):
```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst479LikePassStates tests/component/utils/test_config.py::TestAst480AnalysisUpshotConfig tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers
```
**Result:** 9 pytest passed; frontend Vitest coverage sweep **218** tests passed.

**Product:** No additional fixes or commits — manifest green against publish **`5243d1f5`**.

**Local `dev-kath`:** merge commit **`211eaa86`** after attaching publish ref (not pushed).

#### betty — 2026-05-25T03:54:42.027Z
[check-linear]

- **`[qa-handoff]` cleared (§5b):** Pushed **`6f66ff8f`** (**`docs(AST-481)`**) bible — restored §**7.13y**, §**7.13z** Vitest narrow (not pytest); **`5243d1f5`** **`test(AST-481)`** — **`test_config.py`** **`PASSED_LIKE`** / **`analysis_upshot`** alignment (closes stale **`TestAst302`** / **`BUILD_ARTIFACTS`** vs **AST-479** product drift Katherine reported).
- **Paths:** `docs/ASTRAL_TEST_BIBLE.md`, `tests/component/utils/test_config.py`; **`origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`** tip **`5243d1f5`**.
- **Assignee** → Katherine for **`test-astral`**; status stays **Tests Ready**.
- Spot runs: narrowed Vitest 7 passing; narrowed pytest **`TestAst*`** slice + harness Vitest sweep exit **0** on **`dev-betty`**.

#### betty — 2026-05-25T03:54:40.778Z
Tests updated for [qa-handoff].

Parent **AST-478** / handoff ticket **AST-481**.

1. **`tests/component/utils/test_config.py`** — **`TestAst479LikePassStates`**, **`TestAst480AnalysisUpshotConfig`**, **`TestAst471DispatchConfigHelpers`** (replaced stale **`TestAst302JobStates`** / **`BUILD_ARTIFACTS`** expected vs product **`PASSED_LIKE`** + **`analysis_upshot`** dispatch seed asserts).
2. **`tests/component/frontend/lib/test_analysisUpshot.test.ts`** — **`parseAnalysisUpshot`** / **`snakeCaseToTitle`**.
3. **`tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`** — modal + API mocks.

**Narrow Vitest (**`pytest` rejects these paths**) — **`docs/ASTRAL_TEST_BIBLE.md`** §7.13z:

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/lib/test_analysisUpshot.test.ts ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

Config pytest slice (engineering gate before full harness if you want layered runs):

```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst479LikePassStates tests/component/utils/test_config.py::TestAst480AnalysisUpshotConfig tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers
```

**Publish tip:** **`origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`** @ **`5243d1f5`** (`docs` + `test` commits after Katherine **`c472c479`**).

#### katherine — 2026-05-25T03:49:38.016Z
[qa-handoff]

@Betty White

Full `./scripts/testing/run_component_tests.sh` fails in pytest:

- `tests/component/utils/test_config.py::TestAst302JobStates::test_consult_like_pass_state_is_build_artifacts` — expects `TASK_CONFIG["grade_like"]["pass_state"] == "BUILD_ARTIFACTS"` but production config is **`PASSED_LIKE`** (AST-479; see `src/utils/config.py` around the AST-479 `JOB_STATES` / pipeline comment). This is stale test drift, not product regression for AST-481. Per **`test-astral` §4** I cannot patch `tests/`; please align that assertion (rename + expected value) so the component gate clears.

**Harness / bible:** Narrow command in this thread plus `docs/ASTRAL_TEST_BIBLE.md` §7.13z forwards the two **`*.tsx` / `.ts`** paths into **pytest**, which collects `tests/component` Python only — manifests as `ERROR: not found` for those Vitest specs. Equivalent Vitest run that **passed** here:

```
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/lib/test_analysisUpshot.test.ts ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

Also ran full **`npm run test:component:coverage`** → **218** tests passed after product fixes below.

When pytest is green again, `./scripts/testing/run_component_tests.sh` will reach Vitest automatically.

**Product (AST-481) pushed:** `origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` @ **`c472c479`** — `Modal.tsx` reads `ConfirmContext` and uses synchronous `window.confirm` when no `UserPromptProvider` (fixes `Modal`/`JobAnalysisReportModal` Vitest with `fireEvent`); **`UserPrompt.tsx`** exports `ConfirmContext` and keeps `useUserConfirm` `window.confirm` Promise fallback for other callers outside the shell provider.

#### betty — 2026-05-25T03:44:20.111Z
QA manifest by Betty.

1. **`tests/component/frontend/lib/test_analysisUpshot.test.ts`** — **`parseAnalysisUpshot`** + **`snakeCaseToTitle`** (schema-shaped payloads, null edges).
2. **`tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal`**: mocks **`GET /api/jobs/:id`** via **`api`** (+ **`/api/candidates`**, **`/api/system/ui_config`** first paint); asserts upshot **`aria-label`**, JD block, **`No analysis upshot on file.`** when absent/invalid **`job_data.analysis_upshot`**.
3. **`docs/ASTRAL_TEST_BIBLE.md`** §**7.13z** (`AST-481` narrow paths).

**Narrow run:**
```bash
./scripts/testing/run_component_tests.sh \\
  tests/component/frontend/lib/test_analysisUpshot.test.ts \\
  tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

Full harness for gates: `./scripts/testing/run_component_tests.sh`

**Published tip:** **`origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data`** @ **`2d5a92c6`** (**`test(AST-481)`** cherry-picked).

#### katherine — 2026-05-25T03:27:39.077Z
Built by Katherine.

**Publish ref:** `sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` — tip **`ddc0a444`**.

**`dev-kath` SHAs:** `3b248584` (analysisUpshot parser + types), `383d455b` (modal runtime render), `48f7129f` (`App.css` upshot block), `f8b9b189` (plan doc review stub).

Prerequisites confirmed after merging subs **`AST-479`**, **`AST-480`** ( **`JOB_STATES.RECOMMENDED`**, **`TASK_CONFIG["analysis_upshot"]`**, **`job_data.analysis_upshot`** persist path on **AST-480**); resolved merge conflicts in **`config.py`** / **`database.py`** on **`dev-kath`** when attaching **AST-480**.

#### katherine — 2026-05-25T03:25:18.815Z
Label review: agree on all three — **scope-Single-Component**, **conf-Medium**, **risk-Medium** match plan scope (modal + parser + REVIEW_LIKE/`RECOMMENDED_JOB_STATES` wiring) and upstream deps **AST-479** / **AST-480** confirmed on **`dev-kath`** after merging subs (**`JOB_STATES.RECOMMENDED`**, **`TASK_CONFIG["analysis_upshot"]`**).

#### katherine — 2026-05-25T03:20:54.577Z
🛑 **Build blocked — AST-481 prerequisites absent after merges**

Steps run on `dev-kath`: `git fetch origin`, merged `origin/dev` (already up to date), attached `origin/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data` (already current tip), then merged prerequisite subs:

- `origin/sub/AST-478/AST-479-job-states-passed-like-recommended-and-consult-like-pass` → only **`docs/features/consult/ast-479-…md`** (plan); no `JOB_STATES` **`RECOMMENDED`** / **`PASSED_LIKE_RETRY`** in `src/utils/config.py`.
- `origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist` → only **`docs/features/consult/ast-480-…md`** (plan); no **`TASK_CONFIG["analysis_upshot"]`** in `src/utils/config.py`.

`grep` over `src/utils/config.py` still shows no **`"RECOMMENDED"`** job state and no **`analysis_upshot`** task key — matches plan Stage 1 §2 / Stage 2 §1 halt conditions.

Per the AST-481 plan I am **not** adding `JOB_STATES` rows here (owned by AST-479) or inventing `TASK_CONFIG` / schema (owned by AST-480 / AST-313).

**Needed to resume:** Hedy lands **AST-479** implementation on **`sub/AST-478/AST-479-…`** (or integration) so **`RECOMMENDED`** exists in **`JOB_STATES`** and **`RECOMMENDED_JOB_STATES`** can be extended per Stage 1. Ada lands **AST-480** so **`TASK_CONFIG["analysis_upshot"]`** exists and persistence uses an agreed **`job_data`** key.

**Note:** AST-480 plan text mentions saving under **`job_analysis_report`** while this ticket/UI brief uses **`job_data.analysis_upshot`** — whoever implements persistence should align the key with the AST-481 acceptance path before Katherine re-runs the build.

Status left **Plan Approved**; ping when prerequisite subs carry real **`config.py`** (and any DB/consult wiring) commits.

#### katherine — 2026-05-25T03:20:03.635Z
Label review (build agent):

Conf: agree — Medium matches dependency on AST-479/480 and schema alignment called out in the plan.

Risk: agree — Medium is appropriate for parser/schema drift; mitigations in Stage 2–3 match.

Scope: agree — Single-Component fits modal + small lib + row actions + one config list + CSS per plan.

#### chuckles — 2026-05-25T03:19:10.082Z
## Plan Validation — Chuckles

**Verdict: APPROVED**

Matches parent AC3: runtime JAR render from `job_data`, `RECOMMENDED` in list/actions, stops if **AST-479**/**AST-480** prerequisites missing. Types from `TASK_CONFIG["analysis_upshot"].response_schema` — correct DRY.

**discuss** — Confirm persist key **`analysis_upshot`** with Ada during **AST-480** build (see **AST-480** validation comment).

— Chuckles

#### katherine — 2026-05-25T02:41:27.379Z
**Plan (AST-481)** — `docs/features/consult/ast-481-job-analysis-report-runtime-render-from-job-data.md`

GitHub (publish ref): https://github.com/susansomerset/astral/blob/sub/AST-478/AST-481-job-analysis-report-runtime-render-from-job-data/docs/features/consult/ast-481-job-analysis-report-runtime-render-from-job-data.md

**Self-assessment (labels)**

- **Scope — `Single-Component`:** One modal, one `lib/` parser module, row actions, `RECOMMENDED_JOB_STATES`, and `App.css` only — all UI/config wiring for this ticket.

- **Conf — `Medium`:** Stages 1–2 depend on **AST-479** (`JOB_STATES["RECOMMENDED"]`) and **AST-480** / **AST-313** (`TASK_CONFIG["analysis_upshot"]`); build stops with a 🛑 comment if those are missing.

- **Risk — `Medium`:** Parser/schema drift could hide the upshot; types must mirror `response_schema` literally with an explicit empty-state string in the modal.

— Katherine

---

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
