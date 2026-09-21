<!-- linear-archive: AST-1351 archived 2026-08-31 -->

## Linear archive (AST-1351)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1351/experience-array-ui-renderprint-parity-clarify-candidate  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / 5  
**Parent:** AST-1345 — Clarify candidate_data.artifacts.base_resume.experience node  
**Blocked by / blocks / related:** parent: AST-1345

### Description

## What this implements

Owns Base Resume Content presenting/persisting the experience array as the base template, job artifact surfaces using the same structure by default, plus render/print emitting each role from the array. Does **not** own prompt/schema wording or the unsupported toast / no-emit path (siblings). After contract sibling; may land in parallel with toast sibling once the contract is fixed.

## Citations

`pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.debug-contract-gated`

## Acceptance criteria

- [X] 5. In the Base Resume Content UI, Susan can view and save experience as the job-array template (not as one undifferentiated prose field that round-trips as a string).
- [X] 6. Render and Print of a base (and job, where applicable) resume show each experience job with role metadata and accomplishments from the array — not one merged experience string.

## Boundaries

- [X] Does **not** own prompt/schema wording or the unsupported toast / no-emit path (siblings).

## Notes for planning

After contract; parallel with toast sibling when unblocked.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

## QA test manifest

1. ExperienceJobsEditor add/remove/reorder: `tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx`
2. ArtifactEditor array Save + legacy abort: `test_ArtifactEditor.test.tsx` AST-996/AST-1351 + AST-1351 legacy
3. Config field spine: `TestAst1351ExperienceJobUiFields`
4. ui_config exposure: `TestAst1351ExperienceJobUiConfig`
5. Builder Style D debug jobs: `TestAst1351ExperienceDebugJobs`

**Bible shasums** (`origin/sub/AST-1345/AST-1351-experience-array-ui-render-print-parity`):

* `docs/test-bible/frontend/components.md` `21be7d7295630c7f71f661082a60426b6c6d7455`
* `docs/test-bible/utils/config.md` `6e6bd060716789cefebf741f42d2814ce360b7c8`
* `docs/test-bible/ui/api/api_system.md` `fb07e384e225ab9a95fa83fba23d28d577a512f5`
* `docs/test-bible/core/builder.md` `7fc963135154cc3ccec0d8801b04069406186325`

### Comments

#### radia — 2026-08-13T00:42:13.470Z
[code-rubric] PROCEED (Commit: 863871fb) experience job UI emit parity

#### betty — 2026-08-13T00:39:42.159Z
`origin/sub/AST-1345/AST-1351-experience-array-ui-render-print-parity` @ `863871fb4e29b12d0522d396d57ab69eeb950a68` · experience UI tests landed

#### joan — 2026-08-13T00:33:45.456Z
[plan-rubric] PROCEED (Commit: a6e36b19) array UI + emit parity

#### katherine — 2026-08-13T00:32:25.042Z
`origin/sub/AST-1345/AST-1351-experience-array-ui-render-print-parity` @ `a6e36b1908841ddb5640bf572f30e12784ef5618` · plan ready

---

# Experience array UI + render/print parity (Clarify candidate_data.artifacts.base_resume.experience node)

**Linear:** [AST-1351](https://linear.app/astralcareermatch/issue/AST-1351/experience-array-ui-render-print-parity-clarify)
**Parent:** [AST-1345](https://linear.app/astralcareermatch/issue/AST-1345/clarify-candidate-data-artifacts-base-resume-experience-node) — Clarify candidate_data.artifacts.base_resume.experience node
**Publish ref:** `origin/sub/AST-1345/AST-1351-experience-array-ui-render-print-parity`

Owns Base Resume Content (and job resume artifact surfaces that share `ArtifactEditor` + resume structure) presenting and persisting `experience` as the ordered job-array template, plus happy-path render/print emitting each role from that array. Does **not** own craft/parse/finalize schema or prompt wording (AST-1349) or the unsupported-shape toast / no-emit gate (AST-1350). Contract sibling is already User Testing on `ftr`; this plan assumes the shared five-key array and `is_experience_job_array` / `_emit_experience_jobs_html` already exist on tip after `sync-child` merges `origin/ftr/AST-1345-clarify-candidate-data-artifacts-base-resume-experience-node`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["experience_job_ui_fields"]` — ordered `{key, label}` list whose keys are exactly `_EXPERIENCE_JOB_ITEM_SCHEMA` (company, title, dates, location, accomplishments) | utils |
| `src/ui/api/api_system.py` | Expose `experience_job_ui_fields` (+ reuse existing `unsupported_resume_structure_message` string) on `GET /api/system/ui_config` | ui |
| `src/ui/frontend/src/components/ExperienceJobsEditor.tsx` | New: per-role editor for the five config fields; add/remove/reorder roles; emits `unknown[]` job objects (not a prose string) | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | For experience (`type === "experience_jobs"` or `key === "experience"`): render `ExperienceJobsEditor` instead of raw JSON/`LabeledTextArea`; Save payload remains a parsed job array; structureMode shapeFields mark experience as `experience_jobs`; non-array legacy values stay read-only with the unsupported message (no Print chrome) | ui |
| `src/ui/frontend/src/App.css` | Minimal styles for role cards / field rows under `.experience-jobs-editor` (reuse existing `dep-field` / `dep-input` tokens where possible) | ui |
| `src/core/builder.py` | Happy-path parity audit: base / session / job emit already use `_emit_experience_jobs_html` for `experience_detail`; add Style D found/recorded experience shape + per-job detail when `debug=True` on those emit entrypoints (reuse `candidate.debug_experience_jobs`); do **not** change AST-1350 refuse gate or role HTML layout chrome | core |

**Out of scope (do not touch):** `data/admin/agent_task.json` / TASK_CONFIG experience schemas (AST-1349); Print / Open HTML / JAR toast + no-tab gate (AST-1350); cover letter; education/skills golden chrome beyond existing `_emit_experience_jobs_html`; migration/backfill; `tests/` / bible; inventing a second job-only experience schema.

**As-is (why this ticket exists):** AST-996 taught ArtifactEditor to round-trip experience as pretty-printed JSON text so Save does not `str()`-corrupt the array. Base Resume Content and job resume still edit experience as one undifferentiated textarea (JSON blob). Operators cannot view/edit the job-array **template** (company / title / dates / location / accomplishments per role). Render/print already emit roles via `_emit_experience_jobs_html` (AST-998/1008) and refuse non-arrays (AST-1350), but Style D on emit paths still mostly logs `render_keys` without per-job found/recorded detail.

## Contract (reuse — do not redefine)

Each experience job object (config `_EXPERIENCE_JOB_ITEM_SCHEMA` / AST-1349):

| Field | Type | Notes |
|-------|------|-------|
| `company` | str | required on wire |
| `title` | str | required on wire |
| `dates` | str | required; freeform |
| `location` | str | required; `""` when none |
| `accomplishments` | str | required; one text block per role |

UI editor fields must use these keys only (labels from `BUILD_CONFIG["experience_job_ui_fields"]`). Empty experience → `[]`. Save must persist a JSON array of objects, never a single prose string.

⚠️ **Decision:** Replace the experience JSON textarea with a structured `ExperienceJobsEditor` for valid arrays. Do **not** keep dual JSON + form editing in happy path — one template presentation for Base and job structureMode surfaces.

⚠️ **Decision:** Job resume artifact already uses the same `ArtifactEditor` + `useCandidateResumeStructure` path (`JobAnalysisReportModal`). Fixing ArtifactEditor once covers Base and job; do not fork a second job-only editor.

⚠️ **Decision:** Legacy string / non-array experience in the editor: show the value read-only and surface the exact `BUILD_CONFIG["unsupported_resume_structure_message"]` text inline (via `ui_config`). Do **not** implement Print/Open-HTML toast or tab withholding here (AST-1350). Block Save of that experience tab until regenerate replaces it with an array (other sections may still save if product already allows partial payload — if current Save is all-or-nothing for the artifact dict, keep that behavior and abort whole Save with that message when experience is non-array).

## Stage 1: Config + ui_config — experience job UI field spine

**Done when:** `BUILD_CONFIG["experience_job_ui_fields"]` lists the five keys in schema order with operator labels; `GET /api/system/ui_config` returns that list and the existing unsupported message string; keys match `_EXPERIENCE_JOB_ITEM_SCHEMA` exactly (no sixth field).

1. In `src/utils/config.py`, inside `BUILD_CONFIG` (near `experience_role_layout` / `_EXPERIENCE_JOB_*` consumers), add:

```python
"experience_job_ui_fields": [
    {"key": "company", "label": "Company"},
    {"key": "title", "label": "Title"},
    {"key": "dates", "label": "Dates"},
    {"key": "location", "label": "Location"},
    {"key": "accomplishments", "label": "Accomplishments"},
],
```

2. Confirm each `"key"` is a member of `_EXPERIENCE_JOB_ITEM_SCHEMA` and that the list length is 5. Do not duplicate the schema types here — labels only.
3. In `src/ui/api/api_system.py` `ui_config()`, add to the JSON payload:
   - `"experience_job_ui_fields": BUILD_CONFIG["experience_job_ui_fields"]`
   - `"unsupported_resume_structure_message": BUILD_CONFIG["unsupported_resume_structure_message"]` (already defined by AST-1350 — expose for the editor notice; do not rewrite the string).
4. Do not change `_EXPERIENCE_JOB_*` schemas, prompts, or DATA_SHAPES `type: "experience_jobs"` (already correct).

## Stage 2: ExperienceJobsEditor component

**Done when:** A new flat component under `src/ui/frontend/src/components/` edits an array of job objects using only `experience_job_ui_fields` from props; Add role / Remove / Move up / Move down work; `onChange` receives a new array reference; empty list is valid.

1. Create `src/ui/frontend/src/components/ExperienceJobsEditor.tsx`.
2. Props (exact shape):
   - `fields: { key: string; label: string }[]` — from ui_config
   - `value: Record<string, string>[]` — current jobs (caller normalizes)
   - `onChange: (next: Record<string, string>[]) => void`
   - `disabled?: boolean`
3. Render one card/row per job. For each field in `fields`:
   - `accomplishments` → multiline textarea (`dep-input` / existing textarea class)
   - other keys → single-line text input
4. Controls per job: Move up, Move down, Remove (allow removing the last job → `[]`).
5. Footer: **Add role** appends `{ company: "", title: "", dates: "", location: "", accomplishments: "" }` (all five keys present as empty strings).
6. Do not import core/data. Do not hardcode field keys beyond reading `fields` props (Add-role empty object may initialize from `fields.map(f => [f.key, ""])`).
7. In `App.css`, add a short `.experience-jobs-editor` block (spacing, role border using existing CSS variables). No new design system, no purple/glow chrome.

## Stage 3: ArtifactEditor — present/persist experience as job array

**Done when:** On Base Resume Content and job resume structureMode tabs, the Experience section shows `ExperienceJobsEditor` for array values; Save writes `experience: [...]` (array of objects); Generate/load maps arrays into the editor; non-array legacy values are read-only with the unsupported message; other sections still use `LabeledTextArea`.

1. In `ArtifactEditor.tsx`, when building `shapeFields` from `structureSections` (structureMode), set `type: "experience_jobs"` on the field whose `key === "experience"` (other sections omit type or keep unset). Keep the existing `key === "experience"` Save fallback.
2. Load `experience_job_ui_fields` and `unsupported_resume_structure_message` once via `api("/api/system/ui_config")` (module-level state or effect in ArtifactEditor — same pattern as Base Resume accent palette). If the request fails, fall back to the five keys with Title-Case labels derived from the key string only for that session (still the five contract keys).
3. Helpers (keep near existing `sectionValueToTabContent` / `tabContentToSectionValue`):
   - `isExperienceTab(key, fieldType?)` → `fieldType === "experience_jobs" || key === "experience"`.
   - `parseExperienceJobs(content: string): { ok: true; jobs: Record<string, string>[] } | { ok: false; raw: string }` — empty trim → `{ ok: true, jobs: [] }`; valid JSON array of objects → normalize each job to the five ui field keys as strings; otherwise `{ ok: false, raw: content }`.
   - Keep Save path: for experience tabs, `tabContentToSectionValue` still returns `JSON.parse` / `[]` so the wire payload is an array. Prefer storing the editor’s jobs by serializing to the tab’s `content` string as `JSON.stringify(jobs)` on each editor `onChange` (same SideTab `content: string` model — no SideTab type change).
4. In the CollapsiblePanel body for an experience tab:
   - If `parseExperienceJobs(tab.content).ok`, render `<ExperienceJobsEditor … onChange={jobs => updateTab(tab.id, { content: JSON.stringify(jobs) })} />` instead of `LabeledTextArea`.
   - If not ok: render a short error line with `unsupported_resume_structure_message` and a read-only textarea of `raw` (no edit). `doSave` / `buildPayload`: if any experience tab fails parse, toast that exact unsupported message (variant error) and abort — do not persist a string experience.
5. Load / Generate mapping already uses `sectionValueToTabContent` (JSON.stringify for arrays). Leave that for experience arrays so the editor receives JSON text it can parse. Do **not** use `String(array)` / `[object Object]`.
6. Job persistence structureMode path must hit the same branch (no separate job editor). Confirm `JobAnalysisReportModal` needs **no** file change if it only mounts ArtifactEditor with `useCandidateResumeStructure`.
7. Do not change Print buttons on `ArtifactsBaseResumeContent` / JAR (AST-1350).

## Stage 4: Builder — emit parity + Style D on debug

**Done when:** Base, session, and job resume HTML builders still emit each experience job via `_emit_experience_jobs_html` (role metadata + accomplishments), never one merged experience string on the happy path; when `debug=True` on those build entrypoints, Style D records experience shape and per-job detail (reuse `candidate.debug_experience_jobs`); AST-1350 refuse gate remains unchanged.

1. In `src/core/builder.py`, confirm (read-only audit; edit only if drifted):
   - `_emit_body_sections_html` for `fmt == "experience_detail"` calls `_emit_experience_jobs_html` when `is_experience_job_array(raw)` (already true on tip).
   - `build_base_resume`, `build_resume`, and `build_session_base_resume` all reach that path for experience (no parallel prose-join helper for arrays).
2. At each of those three public build entrypoints, when `debug=True` and after content is resolved (before or after markers — prefer after resolve, before HTML assembly), call `candidate_mod.debug_experience_jobs(_log, content_dict)` so found/recorded shape + per-job company/title/dates/location/accomplishments appear under Style D. Do not invent a second debug format.
3. Do **not** soften `_reject_unsupported_experience_shape` or change `_emit_experience_jobs_html` layout (lead prefix / location sep stay AST-1008).
4. Do not touch cover-letter builders.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1351
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1345/AST-1351-experience-array-ui-render-print-parity` @ `a6e36b1908841ddb5640bf572f30e12784ef5618`

## Traceability

| AC | Plan stage(s) |
|----|----------------|
| 5 | S1 (`experience_job_ui_fields` + `ui_config` exposure), S2 (`ExperienceJobsEditor`), S3 (`ArtifactEditor` structured present/persist; legacy non-array read-only + Save abort) |
| 6 | S4 (audit happy-path `_emit_experience_jobs_html` on base/session/job builds; no prose-merge regression; Style D per-job detail when `debug=True`) |

Stages S1–S4 map to child scope (array UI template + emit parity); parent AC 7 and toast/no-emit correctly deferred to AST-1350; schema/prompt contract to AST-1349.

## Findings

**acceptable** — Assignee is Katherine (Linear: Joan Clarke display name); Chuckles-spawned pass; no review block.

**acceptable** — Plan assumes AST-1349 contract + AST-1350 gate on ftr tip (`unsupported_resume_structure_message`, `_reject_unsupported_experience_shape` already present on worktree); `sync-child` merge expectation is explicit.

**acceptable** — As-is verified: `ArtifactEditor` still round-trips experience via pretty-printed JSON `LabeledTextArea` (`sectionValueToTabContent` / `tabContentToSectionValue`); `structureMode` `shapeFields` currently omit `type: "experience_jobs"` (plan S3.1 fixes); builder emit already uses `_emit_experience_jobs_html` with AST-1350 refuse on non-array; no `debug_experience_jobs` on build entrypoints yet (plan S4 adds).

**acceptable** — `JobAnalysisReportModal` mounts `ArtifactEditor` with `useCandidateResumeStructure` + `structureSections` — plan’s “fix once in ArtifactEditor” covers job resume without a separate JAR file change.

No `fix-now` or `discuss` findings. In-session statute/pattern sweep: cited entries (`pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.debug-contract-gated`, `astral.config.config-source-of-truth`, `astral.layers.import-direction`, `astral.standards.in-scope-only`) all `conforms`; field keys sourced from config via `ui_config`; no UI→data/core shortcuts; sibling boundaries respected (no prompt/schema edits, no Print toast gate changes).

context_tokens≈62000

---

[plan-rubric] PROCEED (Commit: a6e36b19) array UI + emit parity

AST-1351 plan approved.

## Review (build stub)

- **Publish ref:** `sub/AST-1345/AST-1351-experience-array-ui-render-print-parity`
- **Tip:** `eac6612ab20f3854b4840e921727b470522d7b7d`
- **Stages:** S1 `experience_job_ui_fields` + ui_config; S2 `ExperienceJobsEditor`; S3 ArtifactEditor structured present/persist; S4 builder Style D `debug_experience_jobs` on base/session/job emit

## Radia review

# Radia review — AST-1351

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1351  
**Publish ref:** `origin/sub/AST-1345/AST-1351-experience-array-ui-render-print-parity` @ `863871fb4e29b12d0522d396d57ab69eeb950a68`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent confidence paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No `agent.py` edits |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector work |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/process/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No entity responses |
| `astral.config.config-source-of-truth` | scoped | conforms | `experience_job_ui_fields` + unsupported message in `BUILD_CONFIG`; API/UI consume via `ui_config` |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No chain edits |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single issue doc |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Engineer commit: `src/` only; tests/bible via Betty |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer commit excludes `tests/` and `docs/test-bible/` |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No render/verdict |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | `ui_config` route unchanged auth-wise |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Core debug reuse only; UI does not own emit gate |
| `astral.layers.import-direction` | scoped | conforms | UI → `api`/`utils`; `ExperienceJobsEditor` has no core/data imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/` |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Field keys/labels from `BUILD_CONFIG` via `ui_config`; no React shape business rules beyond parse/save |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No `agent_task.json` (AST-1349) |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No seed catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No boot seed |
| `astral.seed.define-approved` | scoped | not-applicable | Implementation ticket |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No operator rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No `src/data/` |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No DB/migrations |
| `astral.standards.debug-contract-gated` | scoped | conforms | `debug_experience_jobs` only when `debug=True` on build entrypoints |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Focused helpers in `ArtifactEditor`; dedicated `ExperienceJobsEditor` |
| `astral.standards.in-scope-only` | scoped | conforms | No AST-1349 schema/prompt or AST-1350 toast/gate edits |
| `astral.standards.logging-via-utils` | scoped | conforms | Reuses `candidate.debug_experience_jobs` / builder `_log` |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | No ticket-id symbols |
| `astral.standards.no-cross-contamination` | scoped | conforms | UI/render parity only; `_reject_unsupported_experience_shape` / `_emit_experience_jobs_html` layout untouched |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Five keys sourced from config; session fallback keys match contract (plan-allowed) |
| `astral.standards.public-then-helpers` | scoped | conforms | Private parse helpers in component module |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No utils→data |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state machine |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run chain |
| `astral.ui.frontend-file-placement` | scoped | conforms | New component under `components/` |
| `astral.ui.naming-conventions` | scoped | conforms | `ExperienceJobsEditor.tsx` naming |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `863871fb merge-tests(AST-1351)` |
| `orch.git.commit-vocabulary` | universal | conforms | `code(AST-1351)` / `test(AST-1351)` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | `sub/AST-1345/...` epic line |
| `orch.git.ftr-sub-topology` | universal | conforms | Child publish ref correct |
| `orch.git.merge-on-checkout` | universal | conforms | Branch includes expected ftr/sync ancestry |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history |
| `orch.git.no-dev-agent-branches` | universal | conforms | `sub/` publish ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | `astral-AST-1345` worktree |
| `orch.git.three-permanent-branches` | universal | conforms | Baseline `origin/dev` |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Implements Joan-approved plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | S1–S4 delivered |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Artifacts / AST-1345 child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed spawn |
| `orch.roles.archie-approves-statutes` | universal | conforms | Joan APPROVED @ `a6e36b19` |
| `orch.roles.betty-owns-test-tree` | universal | conforms | `test(AST-1351)` + merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Katherine assignee |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Engineer path set clean |

**Active-set count scored in-session:** 64 rows; no `violates` / `needs-discussion` statute rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | `BUILD_CONFIG["experience_job_ui_fields"]` is single source; `ui_config` exposes it |
| `pattern.layers.import-discipline` | conforms | UI editor is presentation-only; emit gate stays in core (AST-1350) |
| *(Joan informal)* `astral.layers.ui-config-driven-business-logic`, `astral.standards.debug-contract-gated` | conforms | Covered above |

## Plan adherence

**Engineer product commit** `eac6612a` — six planned files, no scope creep:

| Stage | Plan | Tip |
|-------|------|-----|
| **S1** | `experience_job_ui_fields` (5 keys) + `ui_config` exposure + unsupported message | Delivered in `config.py` / `api_system.py`; keys match `_EXPERIENCE_JOB_ITEM_SCHEMA` order |
| **S2** | `ExperienceJobsEditor` — add/remove/reorder, five fields, `dep-field`/`dep-input`, `App.css` | Delivered; Add role initializes all keys from `fields` |
| **S3** | `ArtifactEditor` structured editor; `type: "experience_jobs"` on experience; legacy non-array read-only + Save abort; no Print changes | Delivered — `parseExperienceJobs`, `ExperienceJobsEditor` branch, unsupported inline notice, `doSave` pre-check; `JobAnalysisReportModal` unchanged (plan §3.6) |
| **S4** | Audit emit path; add `debug_experience_jobs` on `build_base_resume` / `build_resume_from_job` / `build_session_base_resume` when `debug=True`; no gate/layout changes | Delivered — three `if debug:` calls after resolve/filter; `_reject_unsupported_experience_shape` and `_emit_experience_jobs_html` unchanged |

**Sibling boundaries:** No `agent_task.json`, no AST-1350 refuse/toast/JAR changes, no schema redefinition. Branch ancestry correctly includes AST-1349/1350 work via epic sync.

**Estimate 5:** Footprint matches (new component + ArtifactEditor integration + config/ui_config + builder debug).

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

1. **Three-dot diff vs `origin/dev` is epic-aggregate** — Includes AST-1349/1350 (and other ftr siblings) because publish ref sits on merged epic line. For AST-1351 product review, filter to `eac6612a` (6 files). No resolve-child action required on unrelated paths.
2. **Builder Style D test coverage is session-only** — `TestAst1351ExperienceDebugJobs::test_session_debug_lists_experience_jobs` exercises one of three entrypoints; `build_base_resume` / `build_resume_from_job` use the same `debug_experience_jobs(_log, render)` pattern. Optional manifest extension before broader UT.
3. **Unsupported-message fallback** — `ArtifactEditor` seeds `unsupportedExperienceMessage` with the literal before `ui_config` fetch; matches `BUILD_CONFIG` today and plan’s field-key fallback pattern. If the config string ever changes, fetch still wins after load.
4. **`ExperienceJobsEditor` uses `key={index}`** — Acceptable for MVP reorder list; downstream may prefer stable role ids if drag/reorder bugs appear in UT.

## What's solid

- Replaces JSON textarea happy path with structured per-role editing while preserving `SideTab` string model (`JSON.stringify` on change).
- Legacy string experience: read-only display + exact unsupported message + Save abort (no PUT) — component test proves.
- Config field spine validated against craft schema keys (`TestAst1351ExperienceJobUiFields`).
- Core emit parity preserved; AST-1350 refuse gate untouched; Style D reuses existing `debug_experience_jobs` helper.

## Frame diff

Since Joan APPROVED @ `a6e36b19` and build stub @ `eac6612a`:

| Commit | Delta |
|--------|-------|
| `eac6612a` | S1–S4 product: config, ui_config, `ExperienceJobsEditor`, `ArtifactEditor`, `App.css`, builder debug |
| `88ddcc5b` | Betty: `TestAst1351*` + bible rows |
| `863871fb` | `merge-tests(AST-1351)` |

Branch also carries resolved AST-1350 + synced AST-1349/1350 epic line (expected pre-UT rollup).

context_tokens≈50000

---

```
[code-rubric] PROCEED (Commit: 863871fb) experience job UI emit parity
```


## Bug: AST-1381 — Base Resume craft/UI/print issues

Parent mini-bug: [AST-1362](https://linear.app/astralcareermatch/issue/AST-1362/base-resume-issues) / child [AST-1381](https://linear.app/astralcareermatch/issue/AST-1381/fix-base-resume-issues-craftuiprint). Schema/prompt half of symptom 1 is also patched under `ast-1349-experience-array-contract-schema-prompts-agent.md` § Bug: AST-1381. Approved ancestor context: AST-1345 (Done).

### As-is

1. Craft/parse still treat job `accomplishments` as one bullet-bearing string; `_emit_experience_jobs_html` wraps every non-lead line in `<li>` → double bullets.
2. Authoring `|` is not converted to `•` on resume emit for Contact header (`candidate_contact_detail`) and Core Competencies (and any other resume string leaves that only run `_resume_site_markers`). Cover from-block already does `|`→`•`; general resume markers do not.
3. `ExperienceJobsEditor` roles are flat always-open cards labeled `Role N` — not collapsible, no `<company>, <title> / <from> - <to>` collapsed header.
4. Changing Prior Experience structure format from `word_cloud` → `free_prose` in Base Resume Content and using the content **Save** still prints as `word_cloud`, because format lives on `artifacts.resume_structure` and only persists via the separate **Save sections** path; Print reads `build_base_resume` → persisted structure (default `prior_experience` format remains `word_cloud`).

### To-be

1. After the ast-1349 schema/prompt flip, emit/UI treat `accomplishments` as `string[]` and bullet each element **once** (strip residual leading `•`/`-`/`*` if present). `<no bullet>`-prefixed elements stay role-description paragraphs.
2. Every authoring `|` in resume content strings converts to the print bullet separator on emit (including Contact header and Core Competencies), same operator rule as cover from-block.
3. Each experience role is a `CollapsiblePanel` (or equivalent existing chrome) whose collapsed header shows `{company}, {title} / {dates}` (dates field is the freeform from–to span; no new schema keys).
4. After the operator saves a Prior Experience format of `free_prose`, Print/HTML uses the `free_prose` arm (`summary-intro` paragraphs), not `word_cloud` (`competencies-list`).

### Repro

1. **Double bullets:** Craft/parse with accomplishments string lines that already include `•`; Print base resume → `<li>• …</li>`.
2. **Pipes:** In Base Resume Content, set `candidate_contact_detail` and/or `core_competencies` to `A | B | C`; Print → literal `|` remains (cover from-block with `|` would have become `•`).
3. **Collapsible:** Open Base Resume Content → Experience tab → roles are always expanded as `Role N` cards.
4. **Prior format:** On Base Resume Content, set Prior Experience format dropdown to `free_prose`, click the primary content **Save** (not Save sections), click **Print** → Prior Experience still emits as `p.competencies-list` (word_cloud). Then click **Save sections** and Print again — only then (today) does free_prose appear, proving the dual-save gap.

### Root cause

1. **Accomplishments type + emit:** Contract left `accomplishments: str` (ast-1349 as-is); `_split_role_accomplishments` / `_emit_experience_jobs_html` treat every non-lead line as a bullet body and do not strip existing markers. UI textarea round-trips a single string.
2. **`|`→`•` gap:** `_resume_site_markers` only rewrites `__`, `~~`, and ` • ` → NBSP-bullet; it never maps authoring `|` → emit `•`. `_apply_contact_to_render_dict` rebuilds contact from profile fields with bullets, but session/paste and stored `candidate_contact_detail` / `core_competencies` strings go through markers only — craft even teaches competencies as `" | "`-separated.
3. **Flat editor:** AST-1351 shipped always-visible role cards; collapsible chrome was out of that child’s scope.
4. **Split persist paths:** `ArtifactEditor.doSave` PUTs only `artifacts.base_resume`; format edits sit in `structureRows` until `onStructureSave` / `ArtifactsBaseResumeContent.saveStructure` PUTs `artifacts.resume_structure`. Print uses `GET /candidate/resume/base` → `build_base_resume` → `resolve_resume_structure` from disk, so unsaved (content-Save-only) format changes never reach emit.

### Proposed change

**A — Accomplishments emit + UI (depends on ast-1349 schema flip)**

1. `src/core/builder.py` `_emit_experience_jobs_html` / `_split_role_accomplishments`: accept `accomplishments` as `list[str]` (primary). For each element: if it starts with `BUILD_CONFIG["experience_role_layout"]["lead_line_prefix"]`, emit as `p.role-description`; else strip one leading bullet glyph/`-`/`*` + whitespace if present, then emit as a single `<li>`. **Do not** wrap an element that is already only a marker. Optional read-path: if a legacy `str` is still present, newline-split once into the same pipeline (do not require regenerate to Print).
2. `ExperienceJobsEditor`: treat `accomplishments` as `string[]` on the job object. Multiline textarea may edit as one-line-per-element for operators; `onChange` writes a `string[]` (drop empties). Other fields stay strings. Widen prop types as needed (`Record<string, string | string[]>` or equivalent). `ArtifactEditor` `parseExperienceJobs` / Save payload must persist `accomplishments` as a JSON array of strings inside each job, never `str()`.
3. Defense in depth: if emit receives a string that still contains embedded `•` lines, split+strip rather than double-wrap.

**B — Resume-wide `|`→`•`**

1. Extend `_resume_site_markers` in `src/core/builder.py` so authoring `|` becomes the print bullet separator for **all** resume string leaves that already deep-walk through `_apply_resume_text_markers` (Contact header text, Core Competencies, technical skills lines, etc.). Match cover-from-block intent: authoring separator `|` → emit ` • ` / ` • ` consistently with existing ` • ` NBSP tightening — prefer config constants over new literals when a shared separator already exists (`COVER_FROM_BLOCK_CONFIG` authoring/emit pair or a small BUILD_CONFIG resume-marker pair if cover config must stay cover-only).
2. Do **not** break intentional `|` inside URLs; if a naive replace is unsafe, split on ` | ` / bare `|` with the same empty-segment drop policy cover uses, or document the chosen rule in this section before coding.
3. Align craft prompts that still teach competencies / skills as `" | "` separators to authoring `|` **or** `•` with the understanding emit normalizes — optional prompt tweak in the same `agent_task.json` pass as ast-1349 (twin file required if prompts change).

**C — Collapsible experience roles**

1. In `ExperienceJobsEditor.tsx`, wrap each role in existing `CollapsiblePanel` (same component ArtifactEditor already uses).
2. Collapsed `label`: `{company}, {title} / {dates}` using the job’s `company`, `title`, and `dates` strings (trim; omit empty segments gracefully so a missing title does not leave a dangling comma). This is the operator header for Susan’s `<company>, <title> / <from> - <to>` — `dates` already holds the freeform range; **do not** add `from`/`to` schema fields.
3. Move up / down / remove stay in the panel `actions` slot (stop propagation so they do not toggle expand). Default: collapsed or first expanded — pick one and keep it consistent; prefer **collapsed by default** so long resumes scan by header.
4. Minimal CSS under `.experience-jobs-editor` if CollapsiblePanel spacing needs a tweak; reuse tokens.

**D — Prior Experience format Save → print**

1. On Base Resume Content structure authoring, **persist `resume_structure.sections` (including `format`) whenever the operator Saves in a way that they reasonably expect format to stick.** Concrete options (pick the smallest that closes the repro; do not leave dual-save as the only path):
   - **Preferred:** When `structureAuthoring` is on, `doSave` (content Save) also PUTs `artifacts.resume_structure.sections` from current `structureRows` (same payload shape as `saveStructure`), in one request or sequential awaits before toast success; **or**
   - Call `onStructureSave(structureRows)` as part of content Save when any structure row (format/title/enabled/order) is dirty.
2. Keep the explicit **Save sections** control working (idempotent).
3. Confirm `build_base_resume` → `_emit_body_sections_html` already branches `free_prose` vs `word_cloud` from `spec.format` — no emit change required once persistence is fixed. If after persistence Print still word_clouds, then fix format resolution in `_emit_body_sections_html` / `resolve_resume_structure` (verify `prior_experience` row retains `format: "free_prose"` through normalize).

### Blast radius

- Experience job wire shape (shared with job resume ArtifactEditor / draft/finalize).
- All resume HTML builders that deep-walk markers (`build_base_resume`, `build_session_base_resume`, `build_resume_from_job`).
- Operators who author `|` in competencies/skills/contact; golden fixtures that assert literal `|` in HTML (should become `•`).
- Base Resume Content Save UX; any test that assumes content Save never writes `resume_structure`.
- AST-1350 unsupported-shape gate: still refuse non-array `experience`; legacy string **accomplishments** inside a valid job array should coerce or render without blocking the whole resume (see Proposed A).

### What must still hold

- Experience happy path remains job-array template editing (AST-1351) — not a return to JSON textarea.
- Legacy non-array `experience` stays read-only + unsupported message; Print still refuses non-arrays (AST-1350).
- Five job keys only; `dates` stays freeform string; no dual JSON+form editing.
- `_resume_site_markers` still applies `__` / `~~` / NBSP-bullet tightening.
- Prior Experience default format in config may stay `word_cloud`; operator override to `free_prose` must survive Save → Print.
- Cover from-block `|`→`•` behavior unchanged except insofar as shared helpers are reused deliberately.

### Resolution (2026-08-15, resolve-child)

Product landed on `origin/sub/AST-1362/AST-1381-fix-base-resume-issues` (emit `|`→`•`, collapsible roles, content-Save + `resume_structure`, accomplishments list emit). Sibling AST-1382 landed bug-repro + UI/bible retarget. Radia fix-now cleared: Betty restored alien `tests/component/core/test_agent.py` + `docs/test-bible/core/agent.md` to match ftr (orphan AST-1383 coverage removed). No product revert of AST-1381/1382. Advancing to User Testing.


## Bug: AST-1382 — gap: bible + repro for emit / `|`→`•` / collapsible / format-Save (board-betty REVISE)

Parent mini-bug: [AST-1362](https://linear.app/astralcareermatch/issue/AST-1362/base-resume-issues) / gap child [AST-1382](https://linear.app/astralcareermatch/issue/AST-1382/gap-base-resume-issues-testsbible-board-betty-revise). Product already on sibling AST-1381. Schema/sample-job fixture half: `ast-1349-…` § Bug: AST-1382.

### As-is

1. Builder fixtures still feed `"accomplishments": "<prose str>"` into `_emit_experience_jobs_html` / Style D / golden-layout tests; they pass only because emit coerces legacy str — they do **not** prove `string[]` → one `<li>` without double bullets.
2. No focused assert that `_resume_site_markers` / session-or-base emit converts authoring `|` to `•` on `candidate_contact_detail` and `core_competencies`.
3. Frontend AST-1351 / AST-996 tests expect flat **`Role N`** labels and string accomplishments in `ExperienceJobsEditor` / `ArtifactEditor`; they fail on collapsible `{company}, {title} / {dates}` headers and `string[]` wire.
4. No coverage that Base Resume Content **content Save** persists `resume_structure.sections[].format` (e.g. `prior_experience: free_prose`) so Print uses free_prose, not default word_cloud.
5. `docs/test-bible/frontend/components.md` (+ builder.md rows for experience emit) still describe str accomplishments / Role N chrome.

### To-be

Bible + fixtures match AST-1381 product. At least one **[bug-repro]-style** coverage path each for: (a) `accomplishments: string[]` → single bullet emit (no `<li>• …`); (b) contact + competencies `|`→`•` on emit; (c) content-Save persists `prior_experience` format → free_prose print. UI tests expect collapsible headers and list accomplishments.

### Repro

Product tip includes AST-1381. Pre-gap:

```bash
cd src/ui/frontend && ./node_modules/.bin/vitest run \
  ../../../tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1351|AST-996"
```

→ fails on `getByText("Role 1")` (header is now `Acme, Eng / 2020`-style). Builder suites that only pass via str coerce do not fail, but also do not lock the string[] contract.

### Root cause

Same board REVISE as ast-1349 § AST-1382: product moved; UI/emit/print fixtures and bible did not. Gap sibling owns test/bible only.

### Proposed change

**A — Retarget existing fixtures (no product edits)**

1. **`tests/component/core/test_builder.py`:** Where experience jobs use string `accomplishments`, prefer `list[str]` (split lead/`<no bullet>` + bullets into array elements). Update `TestAst1008ExperienceGoldenLayout` sample that uses `f"{_LEAD}\n{_BULLET_A}\n{_BULLET_B}"` → `[f"{_LEAD}…", _BULLET_A, _BULLET_B]` (or equivalent). Keep one **legacy str coerce** case if useful (emit still newline-splits) — label it legacy, not the happy path.
2. **`tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx`:** Fixtures use `accomplishments: ["Did stuff"]` (or multi-line arrays). Assert collapsed header text via `getByText(/Acme, Eng \/ 2020/)` (or the job’s company/title/dates), **not** `Role N`. Expect `onChange` payloads with `accomplishments` as `string[]`. Add-role empty job includes `accomplishments: []`.
3. **`tests/component/frontend/components/test_ArtifactEditor.test.tsx`:** Same retarget for AST-1351 / AST-996 / AST-1375 experience fixtures; drop `Role 1` queries; Save payload expectations use accomplishments arrays.

**B — New repro coverage (board AC — tag `[bug-repro]` on handoff when landing)**

1. **string[] single-bullet emit:** New or extended test in `test_builder.py` (e.g. under `TestAst1008` / dedicated `TestAst1382…`): job with `accomplishments: ["• Shipped X", "Did Y"]` → HTML contains `<li>Shipped X</li>` and `<li>Did Y</li>`, and must **not** contain `<li>• Shipped X</li>`.
2. **Contact + competencies `|`→`•`:** Session or base emit with `candidate_contact_detail` / `core_competencies` text containing `A | B | C` → HTML shows bullet separators, no literal `|` in those nodes (markers path / competencies-list).
3. **prior_experience format Save → print:** Prefer an API or page-level component test that PUTs `artifacts.base_resume` **together with** `artifacts.resume_structure.sections.prior_experience.format = "free_prose"` (mirroring ArtifactEditor content-Save bundling), then `build_base_resume` / HTML route emits prior as free_prose (`summary-intro`), not `competencies-list`. If a pure builder unit is cleaner: structure with `format: "free_prose"` + prior text → assert free_prose markup; pair with an ArtifactEditor or api_candidate test that the Save payload includes `resume_structure` when structure authoring is on.

**C — Bible**

1. **`docs/test-bible/frontend/components.md` § AST-1351 / AST-996:** Accomplishments are `string[]`; collapsible header contract `{company}, {title} / {dates}`; update narrowed vitest patterns / obsolete “Role N” / JSON-textarea notes.
2. **`docs/test-bible/core/builder.md`:** Add or extend an AST-1381/1382 row for string[] emit, `|`→`•` markers, and format-driven prior emit; point commands at the new repro nodes.
3. Cross-link candidate/config bible updates from ast-1349 § AST-1382.

### Blast radius

- Broad builder experience fixtures (AST-998/1007/1008/1030/1350/1351 debug) — retarget carefully; keep AST-1350 non-array refuse tests unchanged.
- Frontend ArtifactEditor suites beyond AST-1351 that mount experience tabs.
- AST-1381 `[qa-handoff]` clears once these greens land on a publish ref Betty/Chuckles can merge for the handoff.

### What must still hold

- AST-1351 happy path remains ExperienceJobsEditor (not JSON textarea).
- AST-1350 unsupported non-array experience refuse + read-only notice unchanged.
- Five job keys; dates freeform string; markers still apply `__` / `~~` / NBSP-bullet.
- Prior default format may stay `word_cloud` in config; operator `free_prose` override must be what repro (3) proves.
- Cover from-block `|`→`•` stays cover’s path; resume markers reuse the same authoring/emit separators without changing cover tests’ intent.
