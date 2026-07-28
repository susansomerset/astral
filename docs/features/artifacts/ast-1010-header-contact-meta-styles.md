# Header/contact + ATS meta description + embedded styles (Resume Render Format discrepancies)

**Linear:** [AST-1010](https://linear.app/astralcareermatch/issue/AST-1010/headercontact-ats-meta-description-embedded-styles-resume-render)
**Parent:** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-993/AST-1010-header-contact-meta-styles`

Shared resume HTML builders already emit a header (`Name` + optional ` • Title`) and a single contact span, with an embedded `<style>` block driven by `BUILD_CONFIG["default_style"]`. Parent AC1 / AC5 / AC7 still fail: the name–title separator is not the legacy NBSP bullet spacing; there is no `<meta name="description">` from a paste tagline; the tagline has no render-key home so it cannot feed meta without appearing as body content; and the embedded stylesheet lacks rules for the golden-layout classes siblings will emit (`.role-header`, `.compact-title`, `.compact-location`, `.role-description`, richer `.education-list` / `.skills-grid` / `.skill-category`). This plan owns header/contact composition, optional `candidate_tagline` plumbing for ATS meta only, and stylesheet expansion — it does **not** own experience/education/skills emit markup (AST-1008 / AST-1009), nested markers (AST-1007, already on `ftr`), Manage Tasks prompt text, cover-letter HTML, or an external `styles07.css` link.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Optional `candidate_tagline` on craft schema + `BUILD_CONFIG` artifact_shapes / supported_sections; add id to `RESUME_STRUCTURE_CONTACT_SECTION_IDS`, `RESUME_STRUCTURE_KNOWN_SECTION_IDS`, and `RESUME_STRUCTURE_DEFAULT` (contact-adjacent, not a body section) | utils |
| `src/core/builder.py` | Header join with legacy `\u00a0• `; emit `<meta name="description">` from name/title/tagline; never emit tagline in header/body; expand embedded CSS for golden header/role/education/skills classes; tighten `.contact` to one centered line | core |

**Out of scope (do not touch):** `_emit_experience_jobs_html` lead-vs-bullets / compact title–location emit (AST-1008); education per-line / skills category / prior-list emit structure (AST-1009); `_apply_resume_text_markers` / `_resume_site_markers` (AST-1007); Manage Tasks / `agent_task` prompt bodies; cover-letter emit; `<title>` string shape (parent: no legacy document-title chrome chase); external CSS file; `tests/`, bible (Betty).

## Stage 1: Optional `candidate_tagline` in config + resume structure

**Done when:** `candidate_tagline` is an optional string on the craft_resume_base / resume_content contracts; it is a known contact-adjacent section id (enabled in the default structure, excluded from body emission via `RESUME_STRUCTURE_CONTACT_SECTION_IDS`); `filter_content_to_resume_structure` keeps a non-empty tagline string when present in content; no Manage Tasks prompt files are edited.

1. In `src/utils/config.py`, add `"candidate_tagline": {"type": "str", "required": False}` to:
   - `TASK_CONFIG["craft_resume_base"]["response_schema"]` (after `candidate_contact_detail`)
   - `BUILD_CONFIG["artifact_shapes"]["resume_content"]` (after `candidate_contact_detail`)
2. In `BUILD_CONFIG["supported_sections"]`, add a `candidate_tagline` entry with `"heading_level": "none"`, `"body_kind": "prose"`, `"page_break_policy": "keep_with_next"` (peer to `candidate_title` — meta/header identity, not a section heading).
3. Extend `RESUME_STRUCTURE_CONTACT_SECTION_IDS` to include `"candidate_tagline"` (tuple order: name, title, tagline, contact — tagline before contact so body exclusion still covers it).
4. Extend `RESUME_STRUCTURE_KNOWN_SECTION_IDS` to include `"candidate_tagline"` in the same relative position among the contact trio.
5. In `RESUME_STRUCTURE_DEFAULT["sections"]`, add:
   ```python
   "candidate_tagline": {
       "id": "candidate_tagline",
       "title": "Candidate Tagline",
       "enabled": True,
       "order": 2,  # after title (1); bump candidate_contact_detail order to 3; shift later sections by +1
       "job_agent_editable": False,
   },
   ```
   Re-number existing `order` values for `candidate_contact_detail` and all later default sections so orders stay unique and ascending (contact was 2 → 3; professional_summary 3 → 4; … through technical_skills).
   ⚠️ **Decision:** Key name is `candidate_tagline` (same `candidate_*` spine as name/title/contact). It is contact-adjacent identity for ATS meta, not a new body section catalog entry with its own `<section>`. Parent forbids Manage Tasks prompt redesign — do **not** edit `agent_task` prompt content; optional schema + structure only so parse may return the field and filter will keep it. If UAT shows the model never returns `candidate_tagline`, escalate on parent AST-993 — do not invent tagline text from summary/title/contact in the builder.
6. Do **not** add admin UI field rows unless an existing admin field list for base_resume already enumerates the contact trio in the same config neighborhood and omitting tagline would leave a broken parallel — if such a list exists next to the trio (e.g. artifact field catalog around `candidate_contact_detail`), add one optional `{key: "candidate_tagline", label: "Candidate Tagline", type: "str"}` entry; otherwise leave admin lists alone.

## Stage 2: Header composition + ATS meta description in `_emit_html_document`

**Done when:** For a markers dict with non-empty `candidate_name`, `candidate_title`, and `candidate_tagline`, `_emit_html_document` (via all three public resume builders) produces (a) `<h1>` text `Name\u00a0• Title` (after escape; markers already applied on name/title strings), (b) one `.contact` span with the contact string (unchanged field source), (c) `<meta name="description" content="Resume of {name}, {title}, specializing in {tagline}">` with HTML-escaped attribute values from the marker-applied strings, and (d) **no** visible tagline under the header or in `<main>`. When any of name/title/tagline is empty/missing, omit the meta description tag entirely (do not emit a partial or placeholder meta).

1. In `src/core/builder.py` `_emit_html_document`, after reading `name` / `title` / `contact` escapes, also read:
   ```python
   tagline_raw = str(render.get("candidate_tagline") or "").strip()
   tagline = html.escape(tagline_raw) if tagline_raw else ""
   ```
   (Markers already ran on the render dict before this helper; do not call `_resume_site_markers` again here.)
2. Build the `<h1>` inner HTML as:
   - both name and title non-empty: `f"{name}\u00a0• {title}"`
   - name only: `name`
   - title only (no name): `title`
   - neither: empty string
   ⚠️ **Decision:** Use `\u00a0• ` (NBSP before the bullet, regular space after) to match `_resume_site_markers` / contact separator convention — not a plain `" • "` join.
3. Keep contact markup as:
   ```html
   <div class="contact"><span>{contact}</span></div>
   ```
   Do not split contact into multiple spans/chips.
4. Build meta description only when `name`, `title`, and `tagline` are all non-empty after the escapes above (empty escape means missing input). Content string **before** attribute escape assembly:
   `Resume of {unescaped_name}, {unescaped_title}, specializing in {unescaped_tagline}`
   where the three pieces are the marker-applied raw strings (`str(render.get(...)).strip()`), then `html.escape` the **entire** content value for the attribute. Exact template (comma after name, comma after title, literal ` specializing in `):
   `Resume of {name}, {title}, specializing in {tagline}`.
5. Insert the meta tag in `<head>` after `<title>…</title>` and before `<style>`:
   ```html
   <meta name="description" content="{meta_esc}" />
   ```
   When the three fields are not all present, insert nothing (no empty meta).
6. Confirm `_structure_ordered_body_ids` / `_RESUME_BODY_KEYS` never include `candidate_tagline` (contact-set exclusion + body-keys tuple already omit it — do not add it to `_RESUME_BODY_KEYS` or `_KEY_TO_SECTION_ID`).
7. Do **not** change `_apply_profile_to_render_dict` to invent a tagline from profile (no profile tagline field). Session paste continues to supply header fields from parse section strings (`build_session_base_resume` already skips profile overwrite).
8. Do **not** change the document `<title>` text construction (leave `{name} — Resume` / `Resume` fallback).

## Stage 3: Expand embedded stylesheet for golden layout classes

**Done when:** The CSS string inside `_emit_html_document` includes rules that style the golden-fixture class names for header/contact and for the role / education / skills structures siblings will emit, without linking an external stylesheet; existing rules used by current emit (`.role-subheader`, `.role-meta`, `.competencies-list`, `.summary-intro`, etc.) remain so AST-994 emit still paints until AST-1008/1009 land.

1. In the embedded `css` f-string in `_emit_html_document`, **keep** existing rules for `:root`, `body`, `h1`/`h2`/`h3`, `.header`, `.contact` (modify `.contact` only as in step 2), `.content`, `.summary-intro`, `.competencies-list`, `.role`, `.role-subheader`, `.role-meta`, `.role-accomplishments`, cover/ATS/print blocks.
2. Change `.contact` so it is one centered line (not flex chips): remove `display: flex; flex-wrap: wrap; gap: 8px 16px; justify-content: center;` and use block centering consistent with `.competencies-list` / list stack (keep `margin`, `font-size`, `color`, and the shared `font-family` / `text-align: center` rule that already targets `.contact`).
3. **Add** the following rules (use existing CSS variables `--header-font-family`, `--body-font-family`, `--list-font-family`, `--text-primary`, `--text-secondary`, `--header-color`, `--accent-color`, `--max-width` — do not invent new `:root` tokens or new `BUILD_CONFIG` keys in this ticket):
   - `.role-header` — left-aligned block wrapping title + location; margin matching current `.role` header spacing.
   - `.compact-title` — left-aligned; header font; ~16px; weight 700; margin `8px 0 2px`; color `var(--text-primary)`; no uppercase / no letter-spacing stretch.
   - `.compact-location` — left-aligned; list font; ~13px; margin `0 0 6px`; color `var(--text-secondary)`.
   - `.role-description` — body font; left-aligned; margin `6px 0`; line-height ~1.25 (lead paragraph under role header).
   - `article.role` — same vertical margin as `.role` (siblings may emit `<article class="role">`).
   - `.role ul` — left-aligned body list; margin `6px 0 0`; padding-left standard list indent (~1.25em).
   - `.role li` — body font; line-height ~1.25; margin `0 0 4px`.
   - `.education-list` — block container; margin `6px 0 0`.
   - `.education-list p` — body font; left-aligned; margin `4px 0`; line-height ~1.25.
   - `.skills-grid` — block/grid container; margin `6px 0 0`; gap between categories ~8px (CSS grid with `1fr` columns or stacked block — pick **stacked block** with each `.skill-category { margin: 0 0 8px; }` so print stays simple).
   - `.skill-category h4` — header font; left-aligned; ~14px; weight 700; margin `0 0 2px`; color `var(--text-primary)`; no flanking rules (those stay on `h2` only).
   - `.skill-category p` — keep/extend the existing shared rule that already includes `.skill-category p` for list font + center; **override inside `.skills-grid .skill-category p`** to `text-align: left` and secondary color so category items match the golden left-aligned items line (do not change `.competencies-list` centering).
4. Do **not** add `<link rel="stylesheet" href="styles07.css">`. Do **not** emit role/education/skills HTML structure changes — only CSS readiness for sibling class names.
5. Do **not** edit `tests/` or bible — Betty owns fixture assertions after Code Complete.

## Stage 4: Three-surface verification (manual / build verification)

**Done when:** With an in-memory render (or session content) that supplies `candidate_name`, `candidate_title`, `candidate_tagline`, and `candidate_contact_detail` (markers optional), each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` produces HTML whose `<head>` contains the exact meta description form above, whose `<header>` has `Name\u00a0• Title` and one contact span with **no** tagline text in the header/main, and whose `<style>` contains the new class selectors from Stage 3. Spike output only under `debug/spikes/AST-1010/` if used — never commit spike dumps; never repo-root `artifacts/`.

1. During **build-child**, exercise the three public builders with a minimal content dict including `candidate_tagline` (string shaped like the parent fixture line: `Program Delivery • Cross-Functional Alignment • Cloud SaaS • AI-Assisted Engineering`).
2. Assert by inspection: meta content matches `Resume of …, …, specializing in …`; h1 uses NBSP-bullet join; tagline absent from body text; CSS source includes `.compact-title`, `.role-description`, `.skills-grid`, `.education-list`.
3. Repeat once with `candidate_tagline` omitted — confirm **no** `<meta name="description"` in the HTML.
4. If Stage 1–3 assumptions fail against current helpers (e.g. filter drops unknown keys despite CONTACT inclusion), **stop**, comment on **parent** AST-993 with the Stage blocked template, and wait — do not improvise.

## Self-Assessment

**Scope:** `Single-Component` — `config.py` optional tagline contract + contact-adjacent structure ids; `builder.py` header join, meta emit, and embedded CSS expansion only.

**Conf:** `high` — header/contact emit and embedded CSS already live in `_emit_html_document`; AST-294 already anticipated optional tagline; contact-section exclusion pattern is established; sibling emit chrome is explicitly out of scope.

**Risk:** `Medium` — wrong meta escaping or tagline leaking into body would break ATS/PDF metadata and golden header composition across session/base/job surfaces; CSS mistakes are visual-only until siblings emit new classes, but a bad `.contact` change is immediately user-visible.

## Code rules check

- §1.3 DRY: one meta builder path inside `_emit_html_document`; reuse existing escape + style merge; no second HTML document template.
- §1.1 / scope isolation: no experience/education/skills emit changes; no Manage Tasks prompts; no cover letter.
- §2.1: tagline contract and structure ids live in `config.py`; CSS continues to consume style tokens already merged from `BUILD_CONFIG["default_style"]`; no new magic marker pairs.
- §1.4: no new hardcoded state sets; CSS sizing follows existing embedded-px pattern rather than inventing unused type_scale wiring in this ticket.
- §2.4 / §2.6: N/A.
- §3.3: core + utils only; no new cross-layer imports.
- §3.5 naming: `candidate_tagline` matches `candidate_*` spine.
- §3.6: spikes under `debug/spikes/AST-1010/` only if used; never commit.

## Review (build stub)

**Publish ref:** `origin/sub/AST-993/AST-1010-header-contact-meta-styles`
**Plan path:** `docs/features/artifacts/ast-1010-header-contact-meta-styles.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `8a00e5eb` | Optional `candidate_tagline` + header/meta emit + embedded golden CSS |
| 4 | `87c99e5f` | Betty three-surface meta/header/CSS + config coverage |

**Tip:** `8a00e5eb` on `origin/sub/AST-993/AST-1010-header-contact-meta-styles`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1010
**Publish ref tip (pre-docs):** `d446ab31` — `origin/sub/AST-993/AST-1010-header-contact-meta-styles`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3 match plan: optional `candidate_tagline` in craft/BUILD/DATA_SHAPES + CONTACT/KNOWN/DEFAULT structure; `<h1>` uses `\u00a0• `; meta `Resume of {name}, {title}, specializing in {tagline}` only when all three present; tagline not in body keys; embedded CSS adds golden class rules without `styles07.css`; `.contact` no longer flex chips.
- Experience emit on this tip still AST-994 `role-subheader` — sibling emit not smuggled into `code(AST-1010)`.
- Betty `TestAst1010HeaderContactMetaStyles` covers meta present/omit + CSS selectors.

### Issues

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; in-scope via `docs/features/**`. Substance conforms.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on diff. Substance conforms (one features file per ticket; sibling plans are ancestry).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope via bible/tests. Substance conforms (`test(AST-1010)` + one `merge-tests(AST-1010)`).

No **fix-now** product findings.

### Recommended actions

Engineer (`resolve-child`): acknowledge C4 stragglers — no product code change required for those three.
