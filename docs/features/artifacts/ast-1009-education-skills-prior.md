# Education lines + skills category grid + prior list (Resume Render Format discrepancies)

**Linear:** [AST-1009](https://linear.app/astralcareermatch/issue/AST-1009/education-lines-skills-category-grid-prior-list-resume-render-format)
**Parent:** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-993/AST-1009-education-skills-prior`

Shared resume HTML builders still emit `education_certifications` and `technical_skills` as a single escaped dump inside one wrapper (`education-list` / `skills-grid`), and parent AC1/AC4 require golden-fixture structure instead: education as per-line paragraphs with the credential name in `<strong>` and the issuer/dates after a bullet separator; technical skills as a category grid (`Category: items` → `skill-category` with `h4` + items `<p>`); prior experience as the competencies-list style with markers already applied by AST-1007. This plan changes emit markup for those three body keys only — it does **not** rework experience role chrome (AST-1008), header/contact/meta/stylesheet expansion (AST-1010), or the markers vocabulary (AST-1007, already on `origin/ftr`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Replace education / technical-skills dumps in `_emit_body_sections_html` with per-line education list + category skills grid helpers; keep prior as `competencies-list` (markers via existing deep-walk); no CSS expansion, no experience/header/meta changes | core |

**Out of scope (do not touch):** `_emit_experience_jobs_html` / lead-vs-bullets / compact title-location (AST-1008); header `Name • Title`, contact join, meta description, embedded stylesheet expansion for `.education-list` / `.skills-grid` layout polish (AST-1010); `_resume_site_markers` / `_apply_resume_text_markers` / `_mark_resume_value` (AST-1007); cover-letter emit; `candidate.py` parse / schemas; `config.py` section catalog; `tests/`, bible (Betty).

## Emit contracts (this ticket)

Markers run **before** emit via `_apply_resume_text_markers` on all three resume surfaces. After that pass, `" • "` has already become `"\u00a0• "` (`NBSP` + `•` + space). Education / skills helpers must split on the **post-marker** separator, not re-apply markers.

### Prior experience

Keep the existing emit shape:

```html
<section aria-labelledby="prior-experience">
  <h2 id="prior-experience">…</h2>
  <p class="competencies-list">{escaped marked text}</p>
</section>
```

Do **not** change this branch except to leave it intact when editing neighboring `elif` arms. Markers are already applied on the string leaf.

### Education & certifications

Source is a **string** (schema `str`) with one credential per line (newlines), as in the parent fixture. Emit:

```html
<div class="education-list">
  <p><strong>{credential}</strong>\u00a0• {rest}</p>
  …
</div>
```

Rules:

1. Split on `str.splitlines()`, keep non-empty stripped lines only.
2. For each line, split on the **first** `"\u00a0• "` (post-marker bullet). Left = credential (wrapped in `<strong>` after `html.escape`); right = issuer/dates (escaped, no strong).
3. If a line has no `"\u00a0• "`, emit `<p><strong>{escaped whole line}</strong></p>` (credential-only line — do not invent an issuer).
4. Do **not** wrap the whole section in a single `<p class="prose-block">`.

### Technical skills

Source is a **string** with one `Category: items` line per newline. Emit:

```html
<div class="skills-grid">
  <div class="skill-category">
    <h4>{category}</h4>
    <p>{items}</p>
  </div>
  …
</div>
```

Rules:

1. Split on `str.splitlines()`, keep non-empty stripped lines only.
2. For each line, split on the **first** `": "` (colon + space). Left = category → `<h4>` (escaped); right = items → `<p>` (escaped; markers already applied).
3. If a line has no `": "`, emit one `skill-category` with **no** `<h4>` and a single `<p>{escaped whole line}</p>` so content is not dropped.
4. Do **not** emit one outer `skill-category` wrapping the entire multi-line dump.

⚠️ **Decision:** Separator and category-split literals stay in `builder.py` next to the existing marker helpers (same grandfather as AST-1007 / AST-998). Do **not** add a `BUILD_CONFIG` block for `"\u00a0• "` or `": "` — these are emit conventions tied to the marker pass and the golden fixture, not environment-tunable behavior. Stylesheet rules for grid/education polish remain AST-1010; this ticket only emits the golden class/structure names already referenced in the fixture (`.education-list`, `.skills-grid`, `.skill-category`).

## Stage 1: Education + skills emit helpers; keep prior competencies-list

**Done when:** Given marked string values shaped like the parent fixture’s Prior Experience / Education & Certifications / Technical Skills sections, `_emit_body_sections_html` (via the three public builders) produces: prior as one `p.competencies-list`; education as `div.education-list` with one `<p><strong>…</strong>\u00a0• …</p>` per non-empty line; skills as `div.skills-grid` with one `div.skill-category` per non-empty `Category: items` line (`h4` + `p`). No single escaped dump remains for education or skills. Experience / header / CSS / markers helpers are unchanged.

1. In `src/core/builder.py`, add a private helper `_emit_education_list_html(text: str) -> str` immediately above `_emit_body_sections_html` (or directly below it in the helpers section — same neighborhood as `_emit_experience_jobs_html`):
   - Implement the education contract above (splitlines → per-line strong + post-marker bullet rest).
   - Return the inner HTML for the education section body only (the `div.education-list` … block, indented consistently with neighboring section bodies — leading spaces matching current `      <div class="education-list">…` style).
   - Use `html.escape` on credential and rest separately; do not escape the `<strong>` tags.
2. In `src/core/builder.py`, add a private helper `_emit_skills_grid_html(text: str) -> str` beside the education helper:
   - Implement the skills contract above (splitlines → per-line category / items).
   - Return the inner `div.skills-grid` … block with the same indentation conventions.
3. In `_emit_body_sections_html`, replace the `education_certifications` arm so that after the existing empty-text skip, it builds the section with `_emit_education_list_html(str(text))` instead of `<div class="education-list"><p class="prose-block">{inner}</p></div>`. Keep the same `<section aria-labelledby=…>` / `<h2>` wrapper pattern used by neighboring arms.
4. Replace the `technical_skills` arm to use `_emit_skills_grid_html(str(text))` instead of the single-category dump.
5. Leave the `prior_experience` arm as `p.competencies-list` with the already-escaped `inner` (or equivalent: escape once after confirming markers already ran — same as today). Do not convert prior into a list or grid.
6. Do **not** change how `dict`/`list` non-string values are coerced via `_format_experience_value` before these arms — schemas keep these keys as `str`; structured dumps stay the existing JSON visibility path if somehow present.
7. Do **not** edit `_emit_html_document` CSS, `_emit_experience_jobs_html`, header/contact join, cover letter, or marker helpers.
8. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.

## Stage 2: Three-surface fixture proof (manual / build verification)

**Done when:** With in-memory / session content whose `prior_experience`, `education_certifications`, and `technical_skills` strings match the parent AST-993 fixture lines (including `__` / `~~` on skills and prior), each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` yields HTML where: Prior Experience is one `p.competencies-list` with no leftover literal `__`/`~~`; Education has ≥3 `div.education-list > p > strong` lines (CSM, CSPO, UW Milwaukee) and is not one `prose-block` dump; Technical Skills has ≥8 `div.skill-category` nodes with `h4` category titles (e.g. `Program & Delivery`, `AI Development & Orchestration`) and item `<p>` text without literal `__`/`~~`. Experience role chrome, header composition, and meta description are **not** asserted here.

1. During **build-child**, exercise the three public builders with fixture-shaped section strings (REPL, or ad-hoc under `debug/spikes/AST-1009/` — **do not** commit spike output; **do not** add repo-root `artifacts/`).
2. Confirm HTML source structure for the three sections matches the contracts in this plan.
3. If a fixture line fails the split rules in a way this plan did not anticipate (e.g. education using a different bullet glyph), **stop**, comment on the **parent** AST-993 with the Stage blocked template, and wait — do not improvise alternate separators.

## Self-Assessment

**Scope:** `Single-Component` — emit helpers and `_emit_body_sections_html` arms in `src/core/builder.py` only; no UI, config, parse, or CSS expansion.

**Conf:** `high` — golden HTML in the parent description is explicit; prior already matches; education/skills are localized string-split emits beside the existing summary paragraph and experience job-array patterns; markers already deep-walked by AST-1007.

**Risk:** `Medium` — wrong split (pre- vs post-marker bullet, or splitting on every colon) would garble education/skills HTML across session/base/job surfaces; impact is resume body typography/structure, not dispatch or DB state.

## Code rules check

- §1.3 DRY: two focused helpers for education/skills; prior reuses existing competencies-list arm; no duplicated marker vocabulary.
- §1.1 / scope isolation: only `builder.py` emit for these three keys; siblings own experience and header/styles.
- §2.1: no new config keys; emit separators stay next to existing marker literals (grandfathered).
- §2.4 / §2.6: N/A (no batch/state-machine work).
- §3.3: core-only change; no new cross-layer imports.
- §3.5 naming: `_emit_education_list_html` / `_emit_skills_grid_html` beside existing `_emit_*` helpers.
- §3.6: spike/debug under `debug/spikes/AST-1009/` only if used; never commit spike dumps.

## Review (build stub)

**Publish ref:** `origin/sub/AST-993/AST-1009-education-skills-prior`
**Plan path:** `docs/features/artifacts/ast-1009-education-skills-prior.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `8c4539e3` / `d2765707` | Education per-line + skills category grid emit; prior competencies-list kept |
| 2 | `35f7f9b1` | Betty three-surface fixture proof |

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1009
**Publish ref tip (pre-docs):** `210fc16b` — `origin/sub/AST-993/AST-1009-education-skills-prior`
**Overall:** DISCUSS

### What’s solid

- Stage 1 matches plan: `_emit_education_list_html` / `_emit_skills_grid_html` beside `_emit_body_sections_html`; post-marker `"\u00a0• "` education split; first `": "` skills split; prior stays `p.competencies-list`; no CSS / experience / markers changes.
- Betty `TestAst1009EducationSkillsPrior` covers education-list / skills-grid / prior structure.
- Self-Assessment Single-Component holds; AST-1008/1010/1007 boundaries respected (1007 present via blockedBy merge only).

### Issues

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — excluded at plan time; in-scope on diff via `docs/features/**`. Substance **conforms**.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — excluded at plan time; in-scope on diff. Substance **conforms** (one features file per ticket; AST-1007 plan is dependency ancestry).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — excluded at plan time; in-scope via Betty bible/tests. Substance **conforms** (`test(AST-1009)` + one `merge-tests(AST-1009)`).

No **fix-now** product findings.

### Recommended actions

Engineer (`resolve-child`): acknowledge C4 stragglers — no product code change required for those three.

## Resolution

**Date:** 2026-07-28  
**Outcome:** clean — no product code changes.

Acknowledged Radia’s three **discuss (C4 straggler)** items (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`). Each was Joan-excluded at plan time, in-scope on the three-dot diff, and marked **conforms** in substance. No **fix-now** items. Publish tip after resolve remains product+Betty+Radia stack on `origin/sub/AST-993/AST-1009-education-skills-prior`.

