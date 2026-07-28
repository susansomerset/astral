# Embedded stylesheet golden parity (Take 2: Resume Render Format discrepancies)

**Linear:** [AST-1020](https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity`

Align the shared resume embedded `<style>` block with the AST-1019 Take 2 golden CSS: contact flex, role/education/skills spacing and type, skills CSS grid, all-caps competencies/skills treatment, unused-but-present `.title` / `.specialties` / `.job-title` / `.dates` rules, mobile and print blocks, and config-driven font/color token updates where the builder already interpolates style. Does **not** own document title / meta emit (AST-1021), DOM structure beyond what CSS alone can fix, AST-993 structural contracts, or cover-letter HTML.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add golden text/border color tokens under `BUILD_CONFIG["default_style"]["colors"]` | utils |
| `src/core/builder.py` | Replace the resume-body CSS string inside `_emit_html_document` with the golden stylesheet (interpolating config tokens); keep Astral-only cover + ATS CSS appendages; always emit golden print `#prior-experience` rule | core |

**Out of scope (do not touch):** `<title>` / `<meta name="description">` emit (AST-1021); header `Name • Title` / contact string join / marker vocabulary; `_emit_experience_jobs_html` / education / skills / prior **markup**; cover-letter HTML structure; external `styles07.css`; `tests/`, bible (Betty).

## Golden CSS contract (stylesheet only)

Authoritative source: parent AST-1019 Original-brief desired HTML `<style>` block (laundry-list items **3–12**). After this ticket, the embedded `<style>` in HTML from `build_session_base_resume` / `build_base_resume` / `build_resume_from_job` must carry these rules (token values may be interpolated from `style` / `BUILD_CONFIG["default_style"]`, but selectors and declarations must match):

| Area | Required golden behavior |
|------|--------------------------|
| `:root` | `--max-width: 800px`; `--accent-color` / `--header-color` from style; `--text-primary` / `--text-secondary` / `--text-tertiary`; `--border-light` / `--border-medium`; three font stacks |
| Typography alignment | `h1,h2,h3,.title,.specialties` header font + center; `.contact,.competencies-list,.skill-category p` list font + center; `.skill-category h4` header font + center; `p,.role-description,ul,li` body font + left + `line-height: 1.25`; `p { margin-bottom: 12px }`; `.job-title` / `.dates` unused-but-present rules |
| All-caps | `.competencies-list` and `.skill-category p`: uppercase, `letter-spacing: 0.2px`, `font-size: 13.5px` |
| Contact | `.contact`: flex, wrap, `gap: 8px 16px`, `justify-content: center`; `.contact span { white-space: nowrap }` |
| Decorative `h2` | flex + `::before`/`::after` hairlines (already present — keep exact golden sizes/margins) |
| Experience | `.role` `margin-bottom: 12px` + `page-break-inside: avoid`; `.role-header` `margin-top: 20px; margin-bottom: 8px`; `.compact-title` / `.compact-location` (14.5px tertiary body font; `em` italic 14.5px); `.role ul` `padding-left: 20px`; bullet `margin-bottom: 6px` |
| Education | `.education-list` `margin-left: 0.5in`; tight `line-height: 1.1`; `strong` on header font |
| Skills | `.skills-grid` CSS grid `repeat(auto-fit, minmax(280px, 1fr))` + gap; category `h4` centered uppercase accent-colored |
| Mobile | Full `@media (max-width: 600px)` block from golden |
| Print | Full `@media print` from golden **including** `#prior-experience { page-break-before: always }` always (not gated on `emit_prior_experience`) |

Astral-only appendages that must **remain** after the golden resume rules (not in the desired HTML fixture, but required by existing builder surfaces):

- `.cover-block` / `.cover-signoff` rules (unchanged)
- `.ats-keywords` rules from `ats_keyword_block` config (unchanged)
- `.prose-block { white-space: pre-wrap; }` so the legacy string-`experience` emit path does not collapse newlines when golden general `p` rules drop `white-space: pre-wrap`

Do **not** emit `<link rel="stylesheet" …>`.

## Stage 1: Config — golden text/border color tokens

**Done when:** `BUILD_CONFIG["default_style"]["colors"]` exposes the golden text and border literals below; fonts / accent / header / page_background remain as today (`#3c2c6e`, `#f5f5f5`, Helvetica Neue / Palatino stacks). No other `BUILD_CONFIG` keys change.

1. In `src/utils/config.py`, inside `BUILD_CONFIG["default_style"]["colors"]`, **add** (do not rename existing `ink` / `muted` / `rule` / `surface` — leave them for other consumers):
   ```python
   "text_primary": "#1a1a1a",
   "text_secondary": "#444",
   "text_tertiary": "#666",
   "border_light": "#e0e0e0",
   "border_medium": "#ccc",
   ```
2. Confirm `default_accent`, `default_header`, `page_background`, and the three font stacks already match the golden `:root` values — if any drift exists vs `#3c2c6e` / `#f5f5f5` / Helvetica Neue / Palatino / list stack, correct those literals in the same edit so Stage 2 interpolation has no judgment call.
   ⚠️ **Decision:** Promote only the CSS custom-property colors that the golden `:root` defines and that Stage 2 interpolates. Do **not** move spacing/type-scale px values into config for this ticket — those stay as literal declarations in the CSS string copied from the golden block (same pattern as AST-1010 / current `_emit_html_document`).

## Stage 2: Replace resume embedded CSS with golden parity

**Done when:** The `css` f-string inside `_emit_html_document` produces a `<style>` body whose resume rules match the golden contract table above (selectors + declarations), interpolating `accent` / `header_c` / `page_bg` / font stacks / the five new color tokens from Stage 1; contact is flex-centered; skills use CSS grid; education has `0.5in` indent; mobile and print blocks are present; `#prior-experience { page-break-before: always }` is always in the print block; cover + ATS + `.prose-block` appendages remain; no external stylesheet link; title/meta/header/contact **emit** code paths are unchanged.

1. In `src/core/builder.py` `_emit_html_document`, after reading `fonts` / `colors` / `ak` as today, also read:
   ```python
   text_primary = colors.get("text_primary", "#1a1a1a")
   text_secondary = colors.get("text_secondary", "#444")
   text_tertiary = colors.get("text_tertiary", "#666")
   border_light = colors.get("border_light", "#e0e0e0")
   border_medium = colors.get("border_medium", "#ccc")
   ```
2. **Delete** the conditional `prior_rule` construction (`if emit_prior_experience: prior_rule = …`). Keep the `emit_prior_experience` parameter on the function signature (callers still pass it for body-section inclusion) — it must no longer affect CSS.
3. **Replace** the resume portion of the `css = f"""…"""` string (everything currently from `:root` through the skills / competencies rules, **before** cover/ATS) with the golden stylesheet translated to an f-string:
   - Interpolate `{accent}`, `{header_c}`, `{page_bg}`, `{hstack}`, `{bstack}`, `{lstack}`, `{text_primary}`, `{text_secondary}`, `{text_tertiary}`, `{border_light}`, `{border_medium}` into the matching `:root` / `body` declarations.
   - Copy every golden rule listed in the contract table **verbatim** (including unused `.title` / `.specialties` / `.job-title` / `.dates`).
   - Use `.role-description` (not `.prose-block`) in the body typography group, matching golden.
   - Do **not** put `white-space: pre-wrap` on the general `p, .role-description, ul, li` rule (golden does not).
4. **Immediately after** the golden skills rules and **before** the mobile block, append Astral-only:
   ```css
   .prose-block { white-space: pre-wrap; }
   .cover-block { … existing unchanged … }
   .cover-block p { white-space: pre-wrap; }
   .cover-signoff img { … }
   .cover-signoff p { … }
   .ats-keywords { … existing ak interpolations unchanged … }
   ```
5. Append the golden **Mobile** `@media (max-width: 600px)` block exactly.
6. Append the golden **Print** `@media print` block exactly, including `#prior-experience { page-break-before: always }` and `#competencies { page-break-after: avoid }` — no `{prior_rule}` splice.
7. Remove obsolete/divergent current declarations that conflict with golden (examples that must not survive): `.contact` without flex; `.compact-location` on list font / 13px / secondary; `.role ul { padding-left: 1.25em }`; `.skills-grid` without `display: grid`; `.skill-category h4` left-aligned primary color; `.education-list` without `margin-left: 0.5in`; duplicate `article.role` margin rule if golden only uses `.role`.
8. Do **not** change the HTML template below the CSS (`<!doctype…>`, `<title>`, meta, header `h1` / `.contact` span, body sections). Title/meta remain AST-1021.
9. Do **not** change `_emit_experience_jobs_html`, `_emit_education_list_html`, `_emit_skills_grid_html`, or section wrappers — markup already emits golden class names from AST-1008/1009; this stage only paints them.
   ⚠️ **Decision:** One wholesale CSS replacement against the parent golden `<style>` block, plus the three Astral appendages (cover / ATS / `.prose-block`), rather than piecemeal patches — avoids leaving half-updated AST-1010/1008 spacing values that fail UAT “no close enough.”

## Stage 3: Three-surface stylesheet proof (manual / build verification)

**Done when:** For fixture-shaped content matching the AST-1019 paste (or equivalent in-memory markers dict), each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` yields HTML whose embedded `<style>` contains the golden selectors/declarations from Stage 2 (spot-check at minimum: `.contact{` flex + gap; `.skills-grid` `minmax(280px`; `.education-list` `0.5in`; `.compact-location` `14.5px`; `@media (max-width: 600px)`; `#prior-experience { page-break-before: always }`); no `<link rel="stylesheet"`; header still `Name • Title` with markers; cover HTML path untouched when not requested. Spike dumps only under `debug/spikes/AST-1020/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, exercise the three public builders (REPL or ad-hoc under `debug/spikes/AST-1020/`).
2. Confirm the `<style>` source carries the Stage 2 contract (string search is enough for “Done when”; eye-check in browser print/preview is UAT, not a build gate inventing Betty tests).
3. If a golden rule cannot be applied because emit markup lacks a class this ticket was told already exists (e.g. missing `.skills-grid`), **stop**, comment on **parent** AST-1019 with the Stage blocked template, and wait — do not invent DOM changes (that is AST-1021 or a re-scope).

## Self-Assessment

**Scope:** `Single-Component` — `BUILD_CONFIG["default_style"]["colors"]` tokens plus the embedded CSS string inside `src/core/builder.py` `_emit_html_document`; no emit markup or UI layer changes.

**Conf:** `high` — golden `<style>` is pasted in the parent Original brief; builder already interpolates fonts/accent into one CSS f-string; AST-1008/1009 already emit the class names this CSS paints.

**Risk:** `Medium` — wrong stylesheet would visually regress all three resume surfaces (session / base / job-tailored) that share `_emit_html_document`, including print pagination for Prior Experience.

## Code Rules self-review

- §1.3 DRY: one CSS construction path inside `_emit_html_document`; no second document template.
- §1.4 / §2.1: fonts and colors stay in `BUILD_CONFIG["default_style"]`; Stage 1 adds the missing text/border tokens; spacing literals stay in the CSS string copied from golden (explicit Decision).
- §2.5 / §3.2: stylesheet emit remains core (`builder.py`); no UI/React duplication of resume cosmetics.
- §3.3: no new imports; utils config only + core builder.
- §3.5 naming: unchanged.
- §3.6: spikes under `debug/spikes/AST-1020/` only if used; never commit; never repo-root `artifacts/`.
- Engineer test-tree ban: no `tests/` or bible edits — Betty owns assertions after Code Complete.
- Sibling scope: title/meta emit left to AST-1021; no cover-letter HTML rewrite.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity`
**Plan path:** `docs/features/artifacts/ast-1020-embedded-stylesheet-golden-parity.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | 6104b15b | `BUILD_CONFIG` text/border color tokens |
| 2 | 89c3f44c | Golden embedded CSS in `_emit_html_document` + cover/ATS/prose-block |

**Tip:** `89c3f44c` on `origin/sub/AST-1019/AST-1020-embedded-stylesheet-golden-parity`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1020
**Publish ref:** `24a466ce420fa770b816603c01d4ce83f34d877a`
**Overall:** DISCUSS

### What’s solid

- Stage 1 tokens land in `BUILD_CONFIG["default_style"]["colors"]`; Stage 2 wholesale CSS replace matches the golden contract (contact flex, skills grid, education `0.5in`, mobile + always-on `#prior-experience` print break).
- Astral appendages (cover / ATS / `.prose-block`) retained; no `<link rel="stylesheet">`; title/meta/markup left for AST-1021.
- Engineer commits touch only `src/utils/config.py` + `src/core/builder.py` + plan; Betty owns one `merge-tests(AST-1020)` SHA.

### Issues / findings

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` against plan Files Changed; three-dot diff vs `origin/dev` brings them in-scope (plan file + Betty test/bible trees). Diff conforms on each — no product fix.

### Recommended actions

- Engineer: acknowledge stragglers (no code change). Proceed resolve-child → User Testing when clear.
