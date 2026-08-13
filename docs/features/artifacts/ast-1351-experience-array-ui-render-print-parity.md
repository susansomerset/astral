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
