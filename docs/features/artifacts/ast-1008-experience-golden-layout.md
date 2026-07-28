# Experience golden layout — lead vs bullets, compact phrasing (Resume Render Format discrepancies)

**Linear:** [AST-1008](https://linear.app/astralcareermatch/issue/AST-1008/experience-golden-layout-lead-vs-bullets-compact-phrasing-resume)
**Parent:** [AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) — Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-993/AST-1008-experience-golden-layout`
**Blocked by (landed):** [AST-1007](https://linear.app/astralcareermatch/issue/AST-1007/nested-typography-markers-on-render-resume-render-format-discrepancies) — nested markers deep-walk is on `origin/ftr/ast-993-resume-render-format-discrepancies` / this sub after merge.

Rewrite shared experience job-array HTML emit so each AST-994/996 job renders as a golden-style role **article**: compact `Title • Company`, compact dates/location phrasing (`dates: place (arrangement)`), optional non-bullet lead paragraph when a source line carries the configured lead marker, then a bullet list for remaining achievement lines. Lands on all three resume surfaces via the existing shared `_emit_experience_jobs_html` path. Does **not** own education/skills/prior chrome (AST-1009), header/meta/stylesheet expansion (AST-1010), nested marker vocabulary (AST-1007), or the job-array parse contract (AST-994/996).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["experience_role_layout"]` with lead-prefix and location-arrangement separator literals | utils |
| `src/core/builder.py` | Rewrite `_emit_experience_jobs_html` to golden article/header/lead/`ul` markup; replace AST-998 role CSS with selectors for the new classes; keep markers-before-escape; leave legacy string experience path alone | core |

**Out of scope (do not touch):** `candidate.py` / job-array schema / craft prompts; education/skills/prior emit (AST-1009); header `Name • Title`, meta description, full stylesheet expansion (AST-1010); `_apply_resume_text_markers` / `_resume_site_markers` vocabulary (AST-1007); cover-letter emit; `tests/`, bible (Betty).

## Golden contract (emit only — do not redefine wire shape)

Each experience job object remains AST-996 fields: `company`, `title`, `dates`, `location`, `accomplishments` (one string block). This ticket only changes how those fields are **emitted** to HTML.

Target markup per non-empty job (match parent desired fixture structure/classes for Experience):

```html
<article class="role">
  <div class="role-header">
    <p class="compact-title"><strong>{Title} • {Company}</strong></p>
    <p class="compact-location"><em>{dates}: {place} ({arrangement})</em></p>
  </div>
  <p class="role-description">{lead text without marker}</p>   <!-- only when a lead line exists -->
  <ul>
    <li>{achievement line}</li>
    …
  </ul>
</article>
```

Parent AC coverage for this ticket: AC1 experience portion + AC3 (Somerset lead paragraph vs list items). Markers inside title/company/dates/location/lead/bullets remain AST-1007’s responsibility (already applied deep + emit-time idempotent calls stay).

## Stage 1: Config — experience role layout literals

**Done when:** `BUILD_CONFIG["experience_role_layout"]` exists with the keys below; no other `BUILD_CONFIG` / `TASK_CONFIG` / artifact shape edits.

1. In `src/utils/config.py`, inside `BUILD_CONFIG` (after `supported_sections` is fine), add:
   ```python
   "experience_role_layout": {
       # Paste/source prefix on an accomplishments line → role-description, not <li>.
       "lead_line_prefix": "<no bullet>",
       # Splits freeform `location` into place + arrangement for compact-location phrasing.
       "location_arrangement_sep": " / ",
   },
   ```
2. Do **not** add title/company joiner to config — emit uses the existing two-character-space bullet joiner `" • "` (same token `_resume_site_markers` already rewrites for NBSP spacing).
3. Do **not** change `supported_sections["experience"]["body_kind"]` (stays `"experience_jobs"`).
   ⚠️ **Decision:** Lead detection is the literal prefix from the parent paste fixture (`<no bullet>`), config-driven per §2.1 — not “first line is always lead” and not a new job-array field. Wire shape stays AST-996.

## Stage 2: Rewrite `_emit_experience_jobs_html` to golden role articles

**Done when:** Calling `build_session_base_resume`, `build_base_resume`, or `build_resume_from_job` with an AST-996 experience job array produces `#experience` HTML where each role is an `<article class="role">` with `div.role-header` / `p.compact-title` / `p.compact-location` (when data present), optional `p.role-description` for lines prefixed with the config lead marker (marker stripped from visible text), and a `<ul>` of `<li>` for remaining non-empty accomplishment lines; a job whose accomplishments include a Somerset-style `<no bullet>…` lead plus following lines shows the lead as a paragraph and the rest as list items; roles with no lead marker emit only header + `<ul>` (no empty `role-description`); empty roles still omitted; legacy string `experience` still uses the existing single `prose-block` section path; cover-letter HTML unchanged.

1. In `src/core/builder.py`, keep the `_emit_body_sections_html` branch that calls `_emit_experience_jobs_html` for job arrays — do **not** change section wrapping (`<section aria-labelledby="experience">` / `<h2>`).
2. Replace the body of `_emit_experience_jobs_html(jobs: list) -> str` as follows (helpers named below may be private functions immediately under it):
   - For each item: skip non-dicts; read `title` / `company` / `dates` / `location` / `accomplishments` with `str(... or "").strip()`; skip when all five empty.
   - Read layout config once per call: `layout = BUILD_CONFIG["experience_role_layout"]`, `lead_prefix = layout["lead_line_prefix"]`, `loc_sep = layout["location_arrangement_sep"]`.
   - **Compact title text** (before escape):
     - If both title and company non-empty: `f"{title} • {company}"`.
     - Elif title only: `title`.
     - Elif company only: `company`.
     - Else: omit compact-title element.
     - Run `_resume_site_markers` on the joined title string when non-empty.
   - **Compact location text** (before escape) via a private helper `_format_compact_location(dates: str, location: str, sep: str) -> str`:
     - If `location` contains `sep`, split **once** on first `sep` into `place` / `arrangement` (both strip); if `dates` and both parts non-empty → `f"{dates}: {place} ({arrangement})"`; if dates empty but both parts → `f"{place} ({arrangement})"`; if arrangement empty after split, fall through to dates+place only.
     - Else (no sep): if dates and location → `f"{dates}: {location}"`; elif dates only → `dates`; elif location only → `location`; else `""`.
     - Apply `_resume_site_markers` to the resulting string when non-empty.
     ⚠️ **Decision:** Arrangement phrasing is emit-only rewrite of the freeform `location` field’s `" / "` (config) into `place (arrangement)` under `dates:` — does **not** change stored job JSON or AST-994 parse.
   - **Accomplishments split** via private helper `_split_role_accomplishments(accomplishments: str, lead_prefix: str) -> tuple[list[str], list[str]]` returning `(lead_paras, bullet_lines)`:
     - Split on `\n`; for each line, `line.strip()`; skip empties.
     - If a stripped line **starts with** `lead_prefix`, append the remainder after the prefix (`.removeprefix(lead_prefix).strip()`) to `lead_paras` when that remainder is non-empty.
     - Else append the full stripped line to `bullet_lines`.
     - Preserve relative order within each list. Emit order is: all lead paragraphs (in encounter order), then one `<ul>` of all bullets (in encounter order) — matches golden (lead then list).
     - Apply `_resume_site_markers` to each lead and bullet string **after** prefix strip, **before** `html.escape`.
   - **Emit structure** for each role:
     ```html
     <article class="role">
       <div class="role-header">
         …optional compact-title…
         …optional compact-location…
       </div>
       …optional role-description paras…
       …optional <ul>…</ul>…
     </article>
     ```
     - `compact-title`: `<p class="compact-title"><strong>{escaped}</strong></p>` when title text non-empty.
     - `compact-location`: `<p class="compact-location"><em>{escaped}</em></p>` when location text non-empty.
     - If both title and location texts are empty, still emit empty `<div class="role-header"></div>` only when there is lead or bullet body; if header and body all empty, skip the role (same as today’s all-empty skip — should not happen after the five-field check unless accomplishments were only whitespace/prefix).
     - Each lead: `<p class="role-description">{escaped}</p>`.
     - If any bullets: wrap in `<ul>` with one `<li>{escaped}</li>` per line (no `role-accomplishments` div; no `prose-block` on the list).
     - If accomplishments empty: omit description and `ul` (header-only role still allowed when title/company/dates/location present).
   - Update the function docstring to describe golden article layout (lead vs bullets + compact phrasing), not AST-998 subheader/meta/prose-block.
3. Keep emit-time `_resume_site_markers` on title/company/dates/location/accomplishments paths as above (idempotent with AST-1007 deep-walk). Do **not** remove deep-walk.
4. Do **not** change `_emit_body_sections_html` education/skills/prior branches, header/contact join, or cover helpers.
5. Do **not** invent a sixth experience field or change `is_experience_job_array`.

## Stage 3: Embedded CSS — swap AST-998 role selectors for golden classes

**Done when:** `_emit_html_document` screen CSS no longer depends on `.role-subheader` / `.role-meta` / `.role-accomplishments` for experience chrome; new selectors keep role text left-aligned (not centered by the global `h1,h2,h3` rule) and list/description readable; print `.role { page-break-inside: avoid; }` remains; fuller font/structure polish stays AST-1010.

1. In the CSS string inside `_emit_html_document`, **replace** the AST-998 block:
   ```css
   .role { … }
   .role-subheader { … }
   .role-meta { … }
   .role-accomplishments { margin: 0; }
   ```
   with:
   ```css
   .role { margin: 10px 0 14px; }
   .role-header { margin: 0 0 6px; }
   .compact-title {
     text-align: left;
     font-family: var(--header-font-family);
     font-size: 16px;
     font-weight: 700;
     line-height: 1.25;
     margin: 8px 0 2px;
     color: var(--text-primary);
   }
   .compact-location {
     text-align: left;
     font-family: var(--list-font-family);
     font-size: 13px;
     line-height: 1.35;
     margin: 0 0 6px;
     color: var(--text-secondary);
   }
   .role-description {
     text-align: left;
     margin: 0 0 6px;
     line-height: 1.25;
   }
   .role ul { margin: 0 0 0 1.2em; padding: 0; }
   .role li { margin: 0 0 4px; }
   ```
2. Keep existing print rule `.role { page-break-inside: avoid; }`.
3. Do **not** add external stylesheet links, meta description, or header/contact CSS changes (AST-1010).
   ⚠️ **Decision:** Minimal class CSS lives with emit (same pattern as AST-998) so golden structure is usable before AST-1010’s stylesheet pass; AST-1010 may refine tokens/fonts without redoing article structure.

## Stage 4: Three-surface fixture proof (manual / build verification)

**Done when:** With an in-memory experience job array shaped like the parent fixture’s Somerset Consulting role (`company` with `__` markers allowed, `title`, `dates`, `location` using `" / "` arrangement, `accomplishments` whose first line starts with `<no bullet>…` and following lines are plain achievements) plus at least one sibling role with no lead marker, each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` produces HTML where (a) Somerset’s lead is a `p.role-description` (no `<no bullet>` visible, not inside `<li>`), (b) following Somerset lines are `<li>` items, (c) compact-title shows `Title • Company` (markers applied), (d) compact-location shows `dates: place (arrangement)` italics line, (e) non-lead roles have `<ul>` only. Do not assert education/skills/meta (siblings).

1. During **build-child**, verify with REPL / `debug/spikes/AST-1008/` ad-hoc calls — **do not** commit spike output; **do not** add repo-root `artifacts/`.
2. Prefer parent AST-993 paste substrings for company/title/location/accomplishments rather than inventing a new fixture dialect.
3. If accomplishments from real session parse lack the lead prefix after LLM craft (marker dropped upstream), **stop** and comment on **parent** AST-993 — do **not** invent a second heuristic (e.g. “first line is always lead”) or edit craft prompts in this ticket.

## Self-Assessment

**Scope:** `Single-Component` — `BUILD_CONFIG` layout literals + `builder.py` experience emit/CSS only; shared path covers session/base/job surfaces without per-surface forks.

**Conf:** `high` — AST-998 already centralized role emit; AST-1007 markers are landed; golden HTML in the parent ticket is explicit for classes and lead-vs-`<li>` behavior.

**Risk:** `Medium` — wrong lead/bullet split or location rewrite would regress Experience HTML on all three resume surfaces; legacy string experience and non-experience sections must stay untouched.

## Code rules check

- §1.3 DRY: one `_emit_experience_jobs_html` + small private helpers; all three builders already share it.
- §1.1 / scope: no education/skills/header/meta/parse ownership.
- §2.1: lead prefix and location arrangement separator live in `BUILD_CONFIG["experience_role_layout"]`; `" • "` joiner reuses existing marker token.
- §2.4 / §2.6: N/A.
- §3.3: core + utils only; no new cross-layer imports.
- §3.5: private helpers `_format_compact_location`, `_split_role_accomplishments` beside `_emit_experience_jobs_html`.
- §3.6: spikes under `debug/spikes/AST-1008/` only if used; never commit dumps.
- Engineer test-tree ban: no `tests/` or bible edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-993/AST-1008-experience-golden-layout`
**Plan path:** `docs/features/artifacts/ast-1008-experience-golden-layout.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `252f640d` | `experience_role_layout` + golden `_emit_experience_jobs_html` + role CSS |
| 4 | `456a3749` / `113a6521` | Betty golden layout proof + merge-tests |

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1008
**Publish ref tip (pre-docs):** post–`origin/ftr` merge on `sub/AST-993/AST-1008-experience-golden-layout`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3 match plan: `BUILD_CONFIG["experience_role_layout"]`, `_format_compact_location` / `_split_role_accomplishments`, golden `<article class="role">` emit, CSS swap off AST-998 selectors; markers-before-escape retained; legacy string experience path untouched.
- Betty `TestAst1008ExperienceGoldenLayout` covers lead vs bullets + compact title/location + config keys.
- Self-Assessment Single-Component holds; AST-1009/1010/1007 boundaries respected (siblings arrive via ftr merge-clean only).

### Issues

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — excluded at plan time; in-scope on diff via `docs/features/**`. Substance **conforms**.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — excluded at plan time; in-scope on diff. Substance **conforms** (one features file per ticket).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — excluded at plan time; in-scope via Betty bible/tests. Substance **conforms** (`test(AST-1008)` + one `merge-tests(AST-1008)`).

No **fix-now** product findings.

### Recommended actions

Engineer (`resolve-child`): acknowledge C4 stragglers — no product code change required for those three.

## Resolution

**Date:** 2026-07-28  
**Radia tip:** `e87afd13` · Overall DISCUSS · no fix-now

| Finding | Action |
|---------|--------|
| discuss C4 `astral.debug.spikes-under-debug-dir` | Acknowledged — substance conforms; no product change |
| discuss C4 `astral.docs.features-single-file-per-ticket` | Acknowledged — substance conforms; no product change |
| discuss C4 `astral.git.engineer-test-tree-ban` | Acknowledged — substance conforms; no product change |

No product or test-tree edits in resolve. Proceeding to User Testing after §9a dry-run.
