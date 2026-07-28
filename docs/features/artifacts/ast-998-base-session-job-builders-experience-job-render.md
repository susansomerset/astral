# Base + session + job builders: experience job render (Parse resume json output is incomplete)

**Linear:** [AST-998](https://linear.app/astralcareermatch/issue/AST-998/base-session-job-builders-experience-job-render-parse-resume-json)
**Parent:** [AST-994](https://linear.app/astralcareermatch/issue/AST-994/parse-resume-json-output-is-incomplete) — Parse resume json output is incomplete
**Publish ref:** `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render`
**Blocked by:** [AST-996](https://linear.app/astralcareermatch/issue/AST-996/judith-craft-base-experience-job-array-parse-resume-json-output-is) — Plan Approved job-array contract (`_EXPERIENCE_JOB_*`, filter/split preserve). Plan HTML recognition of that shape; do **not** own Judith prompts or tailor hops.

Resume HTML builders (candidate base, session/Admin paste, and job-tailored) recognize Experience as the AST-996 ordered job array and render each role with consistent subheaders/metadata (company, title, dates, location) plus one accomplishments block — not a JSON dump or a single merged prose blob. Shared emit path keeps the three surfaces aligned. Does **not** own craft-base/job-tailored prompts (AST-996 / AST-997) or AST-993 lead/bullet / Title•Company chrome.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Set `BUILD_CONFIG["supported_sections"]["experience"]["body_kind"]` to `"experience_jobs"` (render kind docs; emit still keys off value shape) | utils |
| `src/core/builder.py` | Recognize experience job arrays in `_emit_body_sections_html`; emit per-role HTML + CSS; apply resume-site markers to job string fields; keep legacy string path; tighten debug `render_keys` for job arrays | core |

**Out of scope (do not touch):** `data/admin/agent_task.json` / Judith prompts; `craft_resume_base` / `draft_job_resume` / `finalize_job_resume` schemas (AST-996 / AST-997); `ArtifactEditor.tsx`; cover-letter emit; `prior_experience` (stays prose string); AST-993 education/skills/header chrome or lead-vs-bullets role layout; `tests/`, bible.

**Build precondition:** Before Stage 1 product commits, merge `origin/sub/AST-994/AST-996-judith-craft-base-experience-job-array` (or rolled-up `origin/ftr/ast-994-parse-resume-json-output-is-incomplete` once Chuckles merges 996) so `filter_content_to_resume_structure` / session+base content preserve the job array and `candidate._is_experience_job_array` exists. If those landings are missing after merge, **stop** and comment on the parent — do not re-implement craft-base preserve logic here. AST-997 is **not** required to emit job-array HTML from base/session content; job-tailored HTML uses the same emit once job `resume_content.experience` is a job array (997’s responsibility to produce it).

## Contract reference (AST-996 — do not redefine)

Each experience job object (wire keys fixed):

| Field | Type | Render |
|-------|------|--------|
| `company` | str | Meta (or subheader fallback when title empty) |
| `title` | str | Role subheader when non-empty |
| `dates` | str (freeform) | Meta |
| `location` | str (`""` if absent) | Meta when non-empty; omit empty |
| `accomplishments` | str (one block) | Role body (`prose-block`) |

## Stage 1: Config — experience body_kind

**Done when:** `BUILD_CONFIG["supported_sections"]["experience"]["body_kind"]` is `"experience_jobs"`; no TASK_CONFIG / artifact_shapes / craft-base edits.

1. In `src/utils/config.py`, change only:
   ```python
   "experience": {
       "heading_level": "section_heading",
       "body_kind": "experience_jobs",
       "page_break_policy": "avoid_split",
   },
   ```
2. Do **not** change `prior_experience` or other sections’ `body_kind`.
3. Do **not** duplicate `_EXPERIENCE_JOB_*` here — those stay owned by AST-996.

## Stage 2: Shared HTML emit — recognize job array + consistent role chrome

**Done when:** Calling `build_session_base_resume`, `build_base_resume`, or `build_resume_from_job` with `experience` as a non-empty AST-996 job array produces HTML where `#experience` contains one `.role` per job (not a JSON dump and not one undifferentiated prose blob); each role shows title (or company fallback) as subheader, a meta line with the non-empty subset of company/dates/location, and the accomplishments body; legacy string `experience` still renders as today’s single `prose-block`; cover-letter HTML unchanged.

1. In `src/core/builder.py`, replace the generic “any dict/list → `_format_experience_value`” path inside `_emit_body_sections_html` so **`experience` is handled first**:
   - If `key == "experience"` and `candidate_mod._is_experience_job_array(raw)`:
     - Build inner HTML via new helper `_emit_experience_jobs_html(raw)`.
     - If that helper returns empty/whitespace, `continue` (omit the Experience section).
     - Else append the Experience `<section>` with `<h2>` + the roles HTML (no wrapping JSON/`prose-block` for the whole section).
     - `continue` (do not fall through to string coercion).
   - Else keep today’s behavior for other keys and for legacy string `experience` (string → escape → section-specific wrappers).
   - For unexpected non-job-array `list`/`dict` on **non-experience** keys, keep `_format_experience_value` (JSON visibility) as today.
   ⚠️ **Decision:** Branch on **value shape** via AST-996’s `_is_experience_job_array`, not on `body_kind`. Legacy stored string experience must keep working after Stage 1’s `body_kind` flip; reading `body_kind` for emit would break that.
2. Add `_emit_experience_jobs_html(jobs: list) -> str`:
   - For each item in order: skip if not a `dict`.
   - Read fields with `str(... or "").strip()` for `title`, `company`, `dates`, `location`, `accomplishments`.
   - Skip the role entirely when all five stripped values are empty.
   - Apply `_resume_site_markers` to each non-empty field **before** `html.escape`.
   - **Subheader (`h3.role-subheader`):** prefer `title`; if title empty and company non-empty, use `company` as the subheader text; if both empty, omit the `h3`.
   - **Meta (`p.role-meta`):** build an ordered list of non-empty parts:
     - If subheader used `title`, include `company` in meta when non-empty.
     - If subheader used `company` (title was empty), **do not** repeat company in meta.
     - Then append `dates` and `location` when non-empty.
     - Join with `" • "` (existing `_resume_site_markers` will turn `" • "` into NBSP•).
     - If no meta parts, omit the `<p>`.
   - **Body:** if `accomplishments` non-empty, emit `<div class="role-accomplishments prose-block">{escaped}</div>` (same `white-space: pre-wrap` as other prose — preserves paste newlines/bullets without inventing `<ul>` lead/bullet chrome).
   - Wrap each role in `<div class="role">…</div>`.
   - Return the concatenated role HTML (no outer section — caller owns `<section>` / `<h2>`).
   ⚠️ **Decision:** Subheader = title (company fallback); meta = company (when not already in the subheader) + dates + location. This is **consistent metadata**, not AST-993’s `Title • Company` / dates:place phrasing chrome or lead-vs-bullets split. Accomplishments stay **one** text block.
3. In `_emit_html_document` CSS (screen rules, not only `@media print`), add left-aligned role styles so role `h3` is not centered by the existing `h1, h2, h3 { text-align: center }` rule:
   ```css
   .role { margin: 10px 0 14px; }
   .role-subheader {
     text-align: left;
     font-family: var(--header-font-family);
     font-size: 16px;
     font-weight: 700;
     line-height: 1.25;
     margin: 8px 0 2px;
     color: var(--text-primary);
     text-transform: none;
     letter-spacing: normal;
   }
   .role-meta {
     text-align: left;
     font-family: var(--list-font-family);
     font-size: 13px;
     line-height: 1.35;
     margin: 0 0 6px;
     color: var(--text-secondary);
   }
   .role-accomplishments { margin: 0; }
   ```
   Keep the existing print rule `.role { page-break-inside: avoid; }` (already present).
4. Keep `_format_experience_value` for unexpected structured values on other paths; update its docstring to note experience job arrays are handled by `_emit_experience_jobs_html`, not this helper.
5. In `build_resume_from_job` / `build_base_resume` / `build_session_base_resume` debug blocks that compute `content_keys` as “string values with strip”, also treat a non-empty experience job array as present (e.g. include `"experience"` when `_is_experience_job_array(markers.get("experience"))` and the list is non-empty) so Style D `render_keys` is not falsely missing Experience after the array lands. Do **not** add new parse-hop debug (AST-996 / AST-997 own AC9).
6. Confirm all three public entry points already share `_emit_html_document` → `_emit_body_sections_html` (`build_base_resume`, `build_session_base_resume`, `build_resume` / `build_resume_from_job`) — no per-surface duplicate emit. Do **not** add a fourth builder.
7. Do **not** change cover-letter helpers (`_emit_cover_sections_html`, etc.).
8. Do **not** edit `candidate.filter_content_to_resume_structure` here — if arrays are dropped before emit, that is an AST-996 merge/precondition failure (stop + parent comment).

## Self-Assessment

**Scope:** `Single-Component` — builder HTML emit + one `BUILD_CONFIG` `body_kind` literal; no prompt/schema/UI ownership.

**Conf:** `high` — all three surfaces already share `_emit_body_sections_html`; AST-996 defines the wire shape and preserve helpers; current code already JSON-dumps lists, so the recognition gap is localized.

**Risk:** `Medium` — wrong subheader/meta join or accidental stringification would regress Session Paste / base / job-tailored Experience HTML; legacy string path must remain for pre-996 blobs.

## Code rules check

- §1.3 DRY: one `_emit_experience_jobs_html` used by the single body-emit path (session + base + job).
- §2.1: only `body_kind` literal in config; field names come from AST-996 contract (not re-hardcoded as a second schema).
- §2.4 / §2.6: no batch or state-machine changes.
- §3.3: builder stays core; continues to import `candidate` / `config` / `formatting` / `logging` only — no ui/external.
- §3.5: helpers `_emit_experience_jobs_html`; public builders unchanged in signature.
- §1.5.1: no new ungated debug; only extend existing `debug=True` `render_keys` honesty.
- §3.6: no repo-root `artifacts/` directory.

## Review (build stub)

**Publish ref:** `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render`
**Plan path:** `docs/features/artifacts/ast-998-base-session-job-builders-experience-job-render.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `631db63d` | `BUILD_CONFIG` experience `body_kind` → `experience_jobs` |
| 2 | `cfa1c7cf` | shared `_emit_experience_jobs_html` + role CSS + legacy string path + `render_keys` honesty |

**Tip:** see `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render` HEAD after this commit.

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1`

**Publish ref tip:** (see Linear / post-push SHA) on `origin/sub/AST-994/AST-998-base-session-job-builders-experience-job-render`
**Baseline:** `origin/dev`
**Overall:** DISCUSS

### What’s solid
- `body_kind` → `experience_jobs`; emit branches on `is_experience_job_array` (legacy string preserved).
- Shared `_emit_experience_jobs_html` + role CSS for base/session/job; markers before escape; empty roles omitted.
- Style D `render_keys` honesty via `_render_content_keys`; Betty `test`/`merge-tests` on builder tests only.

### Issues
**discuss (C4 stragglers):** Joan excluded debug/docs/engineer-test-tree/UI statutes that the tip brings in-scope via 996/997 merge + features/tests — all scored **conforms**.

### Recommended actions
No fix-now. Stragglers are process notes — resolve-child may proceed without product edits.

## Resolution

**Date:** 2026-07-28
**Review:** Radia `[code-rubric] revision=1` — Overall **DISCUSS**; **fix-now** none; discuss items are Joan C4 statute-exclusion stragglers (all scored **conforms** on tip) — no product changes.
**Outcome:** Clean resolve — no code delta vs `d5b0383b` (Radia docs tip). Proceed to User Testing per resolve-child / spawn direction.

