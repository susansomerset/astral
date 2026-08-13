# Unsupported experience shape — toast, no emit (Clarify candidate_data.artifacts.base_resume.experience node)

**Linear:** [AST-1350](https://linear.app/astralcareermatch/issue/AST-1350/unsupported-experience-shape-toast-no-emit-clarify)
**Parent:** [AST-1345](https://linear.app/astralcareermatch/issue/AST-1345/clarify-candidate-data-artifacts-base-resume-experience-node) — Clarify candidate_data.artifacts.base_resume.experience node
**Publish ref:** `origin/sub/AST-1345/AST-1350-unsupported-experience-shape-toast-no-emit`

Owns the operator-visible failure path when `experience` is still a legacy string or any other non-array shape: toast exactly `unsupported resume structure, please regenerate`, open no HTML tab, and do not emit a printable resume with Experience omitted. Core refuses emit; UI surfaces the core error string. Does **not** migrate data, rewrite schemas/prompts (AST-1349), or own happy-path array UI/render layout (AST-1351).

## UAT fitness

- **AC restored:** Parent AC 7 — “Opening or printing a resume whose experience is still a string (or other non-array shape) shows toast text `unsupported resume structure, please regenerate`, opens no HTML tab, and does not emit a resume with Experience omitted.”
- **Correct outcome:** Operator clicks Print / Open HTML / Print Resume on a resume whose `experience` is a string (or other non-array); they see that exact toast, no new HTML tab (and no printable Experience-omitted document), and must regenerate to get a valid job-array experience before print works.
- **Sibling check:** AST-1349 locks the shared job-array contract (`is_experience_job_array` / five-key items) — this ticket uses that same predicate for “unsupported,” does not redefine schema text. AST-1351 owns array emit/UI parity — this ticket must not change happy-path role HTML layout; only turn the current leftover-prose skip into a hard fail when shape is wrong. Verified by: valid job-array experience still emits; string/non-array never reaches `_emit_body_sections_html` success.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** UI-only toast while `builder` still skips leftover prose and returns HTML without Experience — that still emits the forbidden Experience-omitted resume (and JAR `window.open` would show it). Client-side shape checks alone also fail layer rules and leave direct `/candidate/resume/…` hits uncoved.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add exact operator toast/error string under `BUILD_CONFIG` (single source) | utils |
| `src/core/builder.py` | Shared gate: if `experience` key is present and not `is_experience_job_array`, raise `ValueError` with that config string before any HTML emit; remove Experience leftover-prose skip-as-success path | core |
| `src/ui/api/api_resume_html.py` | Map the unsupported `ValueError` to HTTP 400 + `{"error": "<exact message>"}` (not 404 HTML-looking success) | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Keep fetch-then-blob Print; toast exact `error` string; do not open tab on failure (already mostly true — ensure message is not rewritten) | ui |
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | Same for Open HTML — toast exact message, no blob tab on unsupported | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Print Resume: fetch `/candidate/resume/<job_id>` first (like Base Resume); on non-OK toast exact `error` and do **not** `window.open`; on OK open blob/tab | ui |

**Out of scope (do not touch):** `data/admin/agent_task.json` / craft schemas (AST-1349); Base Resume Content experience editor chrome / happy-path `_emit_experience_jobs_html` layout (AST-1351); cover-letter routes; migration/backfill; `tests/` / bible; inventing a second experience schema.

**As-is:** `_emit_body_sections_html` skips non-array `experience` as `skipped — leftover prose` and still returns full HTML — Experience omitted. Base Resume / Session Open HTML toast whatever the API returns; JAR Print Resume `window.open`s the URL blindly (tab opens even on JSON error).

## Contract (reuse — do not redefine)

Unsupported when the resume content dict (base, job-resolved, or session) has key `"experience"` and `candidate_mod.is_experience_job_array(value)` is false.

| Shape | Gate |
|-------|------|
| key absent | allow emit (no experience section) |
| `[]` or list of dicts | allow (valid array; empty list may omit roles) |
| `str` (incl. non-empty legacy prose) | **refuse** — toast / no emit |
| `dict`, list of non-dicts, other | **refuse** — toast / no emit |

Exact operator text (literal, config-owned):

```text
unsupported resume structure, please regenerate
```

⚠️ **Decision:** Gate in **core builder** before HTML assembly (not React-only). UI only surfaces `error` and withholds the tab. That satisfies “no emit” for every route that calls `build_base_resume` / `build_resume` / `build_session_base_resume`.

⚠️ **Decision:** Check the content dict **before** filter/emit (e.g. raw `base_resume` / `_resolve_resume_sections` result / session `base_resume`), so a non-array value cannot be dropped then silently omitted.

## Stage 1: Config message + core no-emit gate

**Done when:** Calling `build_base_resume` / `build_resume_from_job` / `build_session_base_resume` with `experience` as a non-empty string (or other non-array) raises `ValueError` whose `str(exc)` equals the config literal; no HTML string is returned. Valid job-array `experience` still returns HTML. Leftover-prose skip for `experience` is no longer a success path.

1. In `src/utils/config.py`, under `BUILD_CONFIG`, add a small key for this operator message, e.g. `unsupported_resume_structure_message` (or nested under an existing resume-emit block if one already groups emit strings — prefer one new top-level string key next to other BUILD_CONFIG resume keys rather than inventing a new subsystem). Value must be exactly `unsupported resume structure, please regenerate`.
2. In `src/core/builder.py`, add a private helper (public-then-helpers: place after public `build_*` or with other private resume helpers) that:
   - Accepts a content `dict`.
   - If `"experience" not in content`: return.
   - If `candidate_mod.is_experience_job_array(content.get("experience"))`: return.
   - Else: raise `ValueError(BUILD_CONFIG["unsupported_resume_structure_message"])` (read the key you added; do not hardcode the toast string in builder).
3. Call that helper in:
   - `build_base_resume` — on the raw `br` dict **before** `filter_content_to_resume_structure` / `_emit_html_document`.
   - `build_resume_from_job` — on the dict returned by `_resolve_resume_sections` **before** filter/emit (after the existing resolve `ValueError` path).
   - `build_session_base_resume` — on the in-memory `base_resume` dict **before** filter/emit.
4. In `_emit_body_sections_html`, for `fmt == "experience_detail"` when `not candidate_mod.is_experience_job_array(raw)`: **do not** `continue` with `skipped — leftover prose` as a silent omit. Raise the same `ValueError` with the config message (defense in depth if a caller forgets the early gate). Do **not** change the happy-path `_emit_experience_jobs_html` branch.
5. Do **not** migrate or coerce string experience into an array. Do **not** touch cover-letter builders.

## Stage 2: API + UI toast, no HTML tab

**Done when:** Base Resume Print, Session Open HTML, and JAR Print Resume each show toast text exactly `unsupported resume structure, please regenerate` for a string-shaped experience, open no HTML tab, and never display an Experience-omitted resume document.

1. In `src/ui/api/api_resume_html.py`, for `resume_base` and `resume_for_job`: on `ValueError`, if `str(exc)` equals the BUILD_CONFIG unsupported message, return `jsonify({"error": str(exc)}), 400`. Keep existing 404 behavior for other `ValueError`s (missing candidate/job/etc.). Import the message from config (or compare to `BUILD_CONFIG[...]`) — do not duplicate the literal in the API module as a second source of truth beyond the comparison.
2. Confirm `session_resume_html` in `api_admin.py` already returns 400 + `error` for `ValueError` — leave status mapping alone if it already surfaces `str(exc)`; do not rewrite session cover routes.
3. In `ArtifactsBaseResumeContent.tsx` `handlePrint`: on `!r.ok`, toast `data.error` when present (already does); **do not** open a blob tab; **do not** rewrite the message to a generic “Print failed” when the API returned the unsupported string.
4. In `AdminSessionResumePaste.tsx` `handleOpenHtml`: same — toast exact API `error`, no blob tab on failure.
5. In `JobAnalysisReportModal.tsx` `onPrintResume`: replace bare `window.open(/candidate/resume/...)` with a fetch-first flow using the shared `api` helper (credentials), matching Base Resume:
   - GET `/candidate/resume/${jobId}` (or the same path the button used).
   - If not OK: parse JSON `error` when possible; toast that text (exact unsupported string when core gated); return without opening a window.
   - If OK: open a blob URL (or equivalent) in a new tab only after HTML text is received — same pattern as `ArtifactsBaseResumeContent.handlePrint`.
   - Wire toast state if the modal does not already have a Toast; reuse existing Toast / `setToast` patterns in the file tree (add minimal toast state on the modal if absent). Print Cover Letter stays unchanged.
6. Do **not** add React-side experience-shape business rules beyond reacting to the API error string. Do **not** change ArtifactEditor save/load chrome (AST-1351).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1350
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1345/AST-1350-unsupported-experience-shape-toast-no-emit` @ `8984d14e09ec7af614fd0973b3ad066d995dceef`

## Traceability

| AC | Plan stage(s) |
|----|----------------|
| 7 | S1 (core `BUILD_CONFIG` message + pre-emit gate in `build_base_resume` / `build_resume_from_job` / `build_session_base_resume`; defense-in-depth in `_emit_body_sections_html`), S2 (`api_resume_html` 400 mapping + Base Resume Print / Session Open HTML / JAR Print Resume fetch-then-blob with exact toast, no tab on failure) |

Stages S1–S2 map to parent AC 7 and functional-scope unsupported-shape operator path; parent AC 1–6 and array UI/render parity correctly deferred to AST-1349/AST-1351 per child Boundaries.

## Findings

**acceptable** — Assignee is Hedy (not Joan); Chuckles-spawned pass; no review block.

**acceptable** — `## UAT fitness` present and correctly frames AC 7 vs symptom-only fixes (wrong fix = UI toast while builder still omits Experience).

**acceptable** — As-is verified on tip: `_emit_body_sections_html` still `continue`s with `skipped — leftover prose` for non-array `experience` (lines 1511–1516); `api_resume_html` maps all `ValueError` to 404; JAR `onPrintResume` still blind `window.open`s `/candidate/resume/<job_id>`.

**acceptable** — `MaterialsPreviewModal.tsx` loads resume via iframe `src` without fetch-first but appears unused (no imports elsewhere); core gate still blocks Experience-omitted emit if wired later (iframe would show JSON/error body, not toast — out of this ticket’s three named surfaces).

No `fix-now` or `discuss` findings. In-session statute sweep: cited patterns/statutes (`pattern.layers.import-discipline`, `astral.layers.import-direction`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`) all `conforms`; plan correctly gates in core before `filter_content_to_resume_structure` so string experience cannot be dropped then silently omitted; reuses `is_experience_job_array` per AST-1349 contract without redefining schema.

context_tokens≈52000

## Review (build)

**Built:** `origin/sub/AST-1345/AST-1350-unsupported-experience-shape-toast-no-emit` @ `3b30b01bc7ff13ead7899a289d8b04c215436eb2`

Stage 1: `BUILD_CONFIG.unsupported_resume_structure_message` + `_reject_unsupported_experience_shape` in `build_base_resume` / `build_resume_from_job` / `build_session_base_resume`; leftover-prose skip → raise. Stage 2: `api_resume_html` 400 for unsupported; JAR Print Resume fetch-then-blob + toast (Base/Session already toast API `error`). Tests deferred to Betty.
