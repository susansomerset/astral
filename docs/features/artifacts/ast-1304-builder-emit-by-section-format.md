# AST-1304 — Builder emit by section format

**Linear:** https://linear.app/astralcareermatch/issue/AST-1304/builder-emit-by-section-format  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections  
**Publish ref:** `sub/AST-1299/AST-1304-builder-emit-by-section-format`

After AST-1303: render enabled resume sections in structure order by each section’s `format`, reusing the existing Somerset HTML treatments. Highlights and Publications print as `bullet_list`. Required `experience` emits only as an `experience_detail` job array (leftover prose is not rendered). Html-style italic/bold tags in body text render; other tags are escaped. When `debug=True`, each enabled section logs id / title / format / emit outcome under Style D headers and `|` detail. Does **not** own hop schemas (**AST-1305**) or the structure editor (**AST-1306**). Does **not** change cover-letter emit.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Dispatch body emit by `format`; add `bullet_list` treatment; skip leftover prose Experience; restore allowlisted italic/bold in body text; Style D per-section trail when `debug=True`. | core |
| `src/core/candidate.py` | Widen `filter_content_to_resume_structure` so extra `experience_detail` job arrays and extra list-of-scalars bodies reach the builder. Do **not** drop leftover Experience prose here (builder emit skips it). | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `RESUME_STRUCTURE_*` catalog, `normalize_resume_structure`, emphasis tag **names** | AST-1303 (already on `origin/ftr/AST-1299-support-alternative-resume-sections`) |
| Craft/draft hop schemas, `_flatten_craft_resume_section_strings` KNOWN gate, `draft_job_resume_allowed_section_keys`, legacy label→extra slug, `filter_base_resume_to_structure` / token serialize | AST-1305 |
| Structure editor UI, format picker API, PUT overlay that can remove optionals | AST-1306 |
| `BUILD_CONFIG["supported_sections"]`, cover-letter HTML (`_emit_somerset_cover_html_document`, `_emit_cover_sections_html`) | out of this child |
| `tests/`, `docs/test-bible/**` | Betty |

## Traceability (this child's AC only)

Parent ACs 5–8 are AST-1305. Parent AC 3 (printed heading follows title) is already true: `_emit_body_sections_html` uses `resume_section_titles`; AST-1306 owns the editor that changes the title. Parent AC 1 (seven-only structure renders) is verified in Stage 1 — emit already walks enabled ids only.

| Child AC | Stage |
|----------|--------|
| 2 — Highlights + Publications as `bullet_list` print heading + bullets in structure order | 1 |
| 3 — changing an optional section’s format changes HTML treatment; id unchanged | 1 |
| 4 — italic/bold tags render; other tags are not a raw HTML hole | 1 |
| 5 — leftover prose Experience is not rendered as the required Experience section | 1 |
| 6 — `debug=True`: each enabled section logs id, title, format, emit outcome (Style D + `\|`) | 2 |

## Stage 1: Emit by format, bullet_list, emphasis, skip leftover prose

**Done when:** Calling `build_session_base_resume` (or `build_base_resume` / `build_resume_from_job`) with a normalized structure that is only the seven required ids plus enabled `highlights` / `publications` (`format` `bullet_list`) and a content blob whose `highlights` / `publications` values are newline-separated strings (or lists of scalar lines) produces HTML that contains those two `<h2>` titles in structure order, each followed by a `<ul>` of `<li>` lines. Changing `education_certifications` `format` from `indented_bold_single` to `bullet_list` on the same id emits `<ul><li>…` instead of `div.education-list`, and the section DOM id stays `education` (`_KEY_TO_SECTION_ID`). A `professional_summary` (or `bullet_list`) body containing `<i>…</i>` / `<em>…</em>` / `<b>…</b>` / `<strong>…</strong>` renders those tags; a body containing `<script>alert(1)</script>` or `<i onclick="x">` does not put a raw tag in the HTML (escaped). Required `experience` whose content is a non-empty prose string produces **no** Experience `<section>` (no `div.prose-block` fallback). Required `experience` that is a job array still emits `_emit_experience_jobs_html` as today. A seven-only structure (no optional keys) still emits header + the enabled body sections that have content. Cover-letter functions are unchanged. No new Style D per-section indexes yet.

1. In `src/core/builder.py`, extend the existing `from src.utils.config import` list (do not add a second config import) with:

   - `RESUME_STRUCTURE_BODY_FORMATS`
   - `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`
   - `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES`

   Keep `BUILD_CONFIG` and `RESUME_STRUCTURE_CONTACT_SECTION_IDS`.

2. Next to `_KEY_TO_HEADING`, add a module-level regex built from config (do not hardcode `i\|em\|b\|strong` in the pattern):

   ```python
   _EMPHASIS_TAG_RE = re.compile(
       r"</?(?:" + "|".join(re.escape(n) for n in RESUME_STRUCTURE_EMPHASIS_TAG_NAMES) + r")>",
       re.IGNORECASE,
   )
   ```

   Add helper `_emit_inline_emphasis_html(text: str) -> str` in the helpers section (with the other `_emit_*` functions, after `_resume_site_markers`):

   - If `text` is empty, return `""`.
   - Walk `_EMPHASIS_TAG_RE.finditer(text)`. For each match, `html.escape` the slice before the match; then emit a **lowercase** tag with no attributes: `</name>` if the match starts with `</`, else `<name>`, where `name` is `match.group(0).strip("</>").lower()`.
   - Escape the tail after the last match.
   - Tags with attributes, whitespace inside the brackets, or names not in `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES` do **not** match the regex and stay in the escaped text.

   ⚠️ **Decision:** Escape-then-restore via exact no-attribute tags (not a general HTML sanitizer). That is the closed italic/bold surface AST-1303 declared. `<I>` becomes `<i>`; `<i class="x">` stays escaped.

3. In `src/core/candidate.py`, rewrite **only** the value-keep loop inside `filter_content_to_resume_structure` (keep the `allowed` / `allow_contact` preamble). For each `key` in `allowed`:

   | `val` | Action |
   |-------|--------|
   | `is_experience_job_array(val)` and `val` nonempty | `out[key] = val` — **any** enabled id, not only `"experience"` |
   | `key == "experience"` and `val` is a nonempty stripped string | `out[key] = val` — leftover prose stays in the filtered dict so tracker persist (`_prepare_job_resume_content` / `persist_job_artifact_from_parsed`) does not silently drop it; **builder emit** skips it in step 7 |
   | any other key | if `val` is a nonempty stripped string → keep it; elif `val` is a nonempty list and **every** item is not a `dict` → set `out[key]` to `_coerce_resume_section_string(val)` when that returns a string; else drop |

   Do **not** change `filter_base_resume_to_structure`, `_flatten_craft_resume_section_strings`, `split_craft_resume_base_payload`, hop validators, or token serialize.

   ⚠️ **Decision:** Extra `experience_detail` job arrays must survive the filter or Stage 1 cannot emit them. Extra `bullet_list` list-of-scalars must coerce to a newline string or Highlights stored as a list never prints. Dropping Experience prose in this shared filter would change tracker persist — that regenerate is AST-1305.

4. In `src/core/builder.py`, add `_html_section_dom_id(sid: str) -> str` that returns `_KEY_TO_SECTION_ID[sid]` when present, else `sid.replace("_", "-")`. Use this everywhere `_emit_body_sections_html` currently does `_KEY_TO_SECTION_ID.get(key, key)`.

5. Add `_emit_bullet_list_html(text: str) -> str`:

   - Split `str(text)` on lines; skip blank/whitespace lines.
   - Each remaining line → `        <li>{_emit_inline_emphasis_html(line)}</li>`.
   - If no items, return `""`.
   - Else return `      <ul>\n` + joined items + `\n      </ul>`.

   Do **not** add a new CSS class. In the golden stylesheet inside `_emit_html_document`, change the existing selectors:

   - `.role ul` → `section ul, .role ul` (same declarations)
   - `.role li` → `section li, .role li` (same declarations)
   - `.role li:last-child` → `section li:last-child, .role li:last-child` (same declarations)

   ⚠️ **Decision:** Highlights bullets share Experience list chrome. That is reuse of the Somerset treatment, not a new visual language. Do not add `bullet-list` classes or new type-scale tokens.

6. Change `_emit_html_document` to take `resume_structure: Optional[dict] = None` (after `body_section_titles`). Pass it through to `_emit_body_sections_html`. Update the three resume callers (`build_resume_from_job`, `build_base_resume`, `build_session_base_resume`) to pass `resume_structure=structure`. Do **not** change cover-letter callers (they do not use `_emit_html_document`).

7. Rewrite `_emit_body_sections_html` to take `resume_structure: Optional[dict] = None` and dispatch **by format**, not by section id. Keep the `for key in ordered_ids` loop and the empty-skip behavior.

   Resolve format for each `key`:

   ```python
   spec = ((resume_structure or {}).get("sections") or {}).get(key) or {}
   fmt = spec.get("format") or RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID.get(key)
   ```

   If `fmt` is not in `RESUME_STRUCTURE_BODY_FORMATS`, skip the section (do not emit JSON / `prose-block`).

   Heading: `html.escape(titles.get(key, _KEY_TO_HEADING.get(key, key.replace("_", " ").title())))` — unchanged title source. DOM id: `_html_section_dom_id(key)`.

   Coerce non-array body content to a string the same way as today (`str(raw)` / `_format_experience_value` only when `raw` is `dict`/`list` **and** format is not `experience_detail` / not a job array). Prefer: if `raw` is a string, use it; if `raw` is a list of non-dicts, join with `"\n"` (filter step 3 already does this; keep the join here as defense if a caller skips the filter).

   | `fmt` | Emit (reuse existing helpers; do not fork a second visual language) |
   |-------|---------------------------------------------------------------------|
   | `free_prose` | Today’s `professional_summary` path: `_session_cover_letter_paragraphs` → `<p class="summary-intro">{_emit_inline_emphasis_html(p)}</p>` |
   | `bullet_list` | `_emit_bullet_list_html`; skip section if it returns `""` |
   | `word_cloud` | Today’s `core_competencies` / `prior_experience` path: `<p class="competencies-list">{_emit_inline_emphasis_html(text)}</p>` |
   | `dual_column` | `_emit_skills_grid_html` after switching that helper’s `html.escape` calls to `_emit_inline_emphasis_html`; skip if empty |
   | `indented_bold_single` | `_emit_education_list_html` after the same escape→emphasis swap; skip if empty |
   | `experience_detail` | If `candidate_mod.is_experience_job_array(raw)` and `_emit_experience_jobs_html(raw)` is nonempty → today’s role `<article>` block. **If `key == "experience"` and `raw` is not a job array → skip (no `div.prose-block`).** If `key != "experience"` and `raw` is not a job array → skip (do not `json.dumps`). |

   Delete the id-keyed `if key == "professional_summary"` / `education_certifications` / `technical_skills` / `core_competencies` / `experience` / `prior_experience` branches. Historical slugs keep today’s look because AST-1303 default formats match those treatments.

   In `_emit_experience_jobs_html`, replace `html.escape` on `title_text`, `loc_text`, `lead`, and `bullet` with `_emit_inline_emphasis_html`. Leave attribute/id escaping as `html.escape`.

   ⚠️ **Decision:** Required Experience has no prose render fallback (parent). Extra sections may use `experience_detail` and then must be a job array to print. Format, not id, chooses the treatment so AST-1306 format edits change HTML without minting a new id.

8. Update `_render_content_keys` so **any** nonempty job-array value (not only `markers["experience"]`) is included alongside nonempty strings.

9. Do **not** in this stage: add per-section `debug_index` calls; edit cover-letter emit; edit `BUILD_CONFIG["supported_sections"]`; remove the unused `emit_prior_experience` parameter; add `debug=` to `normalize_resume_structure`.

## Stage 2: Style D per-section emit trail

**Done when:** With `debug=True` on `build_session_base_resume` / `build_base_resume` / `build_resume_from_job`, after the existing document-level success `debug_index` (`index 1/1`), the log also has one Style D header per **enabled** section (`enabled_resume_section_ids` order) with universal `index N/M` (`M` = enabled count), `identifier` = section id, and `outcome` one of `emitted`, `skipped — empty`, `skipped — leftover prose`, `skipped — not job array`, `skipped — missing format`. Each header is followed by `|` detail `title=<repr> format=<repr>` (`format=None` for contact/header ids). With `debug=False`, none of these new lines appear. Existing document-level details (`resume_source`, `html_preview`, …) stay.

1. Add optional kwargs to `_emit_html_document` and `_emit_body_sections_html`: `debug: bool = False`, `debug_func: str = ""`. The three resume callers pass `debug=debug` and `debug_func` equal to that public function’s current `func=` string (`builder.build_resume_from_job`, `builder.build_base_resume`, `builder.build_session_base_resume`).

2. Inside `_emit_body_sections_html`, record per-id emit result while looping (`emitted` vs skip reason). After the loop, **only if** `debug` is True:

   - `_log.set_debug_flag(True)` is already set by the public caller; do not emit when `debug` is False.
   - `enabled = candidate_mod.enabled_resume_section_ids(resume_structure or {})`
   - `total = len(enabled)` (use `1` if empty so you never pass `total=0`)
   - For `i, sid` in `enumerate(enabled, start=1)`:
     - `spec` / `title` from structure; `fmt = spec.get("format")` (absent on contact ids → `None`)
     - Contact/header (`sid in RESUME_STRUCTURE_CONTACT_SECTION_IDS`): `outcome = "emitted"` if `str(render.get(sid) or "").strip()` else `"skipped — empty"`
     - Body id that appended a chunk: `"emitted"`
     - Body id skipped because leftover Experience prose: `"skipped — leftover prose"`
     - Body id skipped because `experience_detail` and not a job array (extras): `"skipped — not job array"`
     - Body id skipped because `fmt` not in `RESUME_STRUCTURE_BODY_FORMATS`: `"skipped — missing format"`
     - Else: `"skipped — empty"`
     - `_log.debug_index(func=debug_func or "builder._emit_body_sections_html", index=i, total=total, identifier=sid, outcome=outcome)`
     - `_log.debug_detail(f"title={title!r} format={fmt!r}")`

   Do **not** `debug_detail_block` the per-section HTML (the document-level `html_preview` already truncates the full document via `truncate_debug_content`).

3. Keep the existing document-level success/failure `debug_index` + details on the three public resume builders. Per-section indexes are **additional**. Do not add this trail to `build_cover_letter` / `build_cover_letter_from_job` / `build_session_cover_letter`.

⚠️ **Decision:** Per-section `debug_index` (Style D headers) rather than only `|` lines under the document header — parent AC names Style D headers with id / title / format / emit outcome. Contact ids are enabled sections and must appear in the `N/M` walk even though they are not body formats.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that does not exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits `code(AST-1304): …`, publishes to `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — resume HTML emit in `builder.py` plus the existing `filter_content_to_resume_structure` keep-loop so extra bodies reach that emit; no hops, no editor, no cover letter, no new config catalog.

**Conf:** `high` — AST-1303 already persisted `format` and `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES`; every treatment except `bullet_list` already exists as an id-keyed branch; this ticket rekeys those branches and adds one list helper.

**Risk:** `Medium` — a wrong format map would regress every printed resume; a loose emphasis restore would open an HTML hole; dropping Experience prose in the shared filter would change tracker persist (explicitly not done).

## Code Rules check

- §1.1 / `astral.standards.in-scope-only`: only builder emit + the filter keep-loop the emit needs. Hops, editor, cover letter, `BUILD_CONFIG["supported_sections"]` left to siblings / out of scope.
- §1.3 / `dry-and-focused-functions` / `public-then-helpers`: one format dispatch; reuse `_emit_education_list_html` / `_emit_skills_grid_html` / `_emit_experience_jobs_html` / `_session_cover_letter_paragraphs`; new helpers are `_emit_inline_emphasis_html`, `_emit_bullet_list_html`, `_html_section_dom_id`.
- §1.4 / `no-hardcoded-sets`: formats and emphasis tag names read from `RESUME_STRUCTURE_BODY_FORMATS` / `RESUME_STRUCTURE_EMPHASIS_TAG_NAMES` / `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`; do not retype `("i", "em", "b", "strong")` or the six format strings in builder.
- §1.5.1 / `astral.standards.debug-contract-gated`: Stage 2 lines only when `debug=True`; Style D `index N/M`; `|` detail; no new lines when `debug=False`.
- §2.1 / `config-source-of-truth` / `pattern.config.config-block`: consume AST-1303 catalog; do not invent a parallel format table in builder.
- §2.4 / §2.6: not applicable (no batch / state machine).
- §3.3 / `import-direction`: builder already imports core + utils + data; new names are utils config only. `candidate.py` filter change stays in core.
- §3.5 naming: snake_case helpers; no new files; no `AST_1304_*` symbols.
- `astral.standards.names-not-ticket-ids`: helper names are domain (`_emit_inline_emphasis_html`), not ticket-prefixed.
- `astral.git.engineer-test-tree-ban`: no `tests/` or bible edits. Existing filter tests that assume extra lists / extra job arrays are dropped may fail — Betty owns that revision.

## Contract for siblings (non-goals)

- **AST-1305** accepts extra keys on craft/draft hops and regenerates leftover Experience prose in persisted blobs. This ticket only refuses to **print** leftover Experience prose.
- **AST-1306** lets operators change `format` / title. This ticket is why that change reprints with a different treatment and the same id.

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1304
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format` @ `f51e905d7cbb6176b09918ddc5b82b4af223e16e`

## Traceability
Child AC1→S1; AC2→S1; AC3→S1; AC4→S1; AC5→S2; parent AC1→S1; parent AC3→(titles unchanged); parent AC2/4/5/11→child AC1–5/S1–2; parent AC5–8→AST-1305

## Findings

### discuss — Traceability table uses parent AC numbers (2–6), not child checkbox order (1–5)
**Location:** Traceability (this child's AC only)
**Finding:** Child ticket lists five AC bullets without parent indices; plan maps parent AC2–6 / 11. Content aligns; numbering differs.
**Recommendation:** Non-blocking. Engineer may cross-reference child Description when implementing.

### discuss — `filter_content_to_resume_structure` widens persist path before AST-1305 hop ingest
**Location:** Stage 1 step 3; Contract for siblings
**Finding:** Filter keeps leftover Experience prose and extra list/job-array bodies so emit can run; hop acceptance of extra keys remains AST-1305. End-to-end Highlights/Publications from craft hops needs 1305 on the rollup line.
**Recommendation:** Non-blocking for this child — plan correctly scopes emit vs persist and names AST-1305 for regenerate.

— Joan
context_tokens≈95000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1299/AST-1304-builder-emit-by-section-format`
**Tip:** `757f2cda6f7555191fa83a899a6ad9660f251ef9`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `6c6e7dd5` | emit by format, bullet_list, emphasis, skip leftover prose Experience |
| 2 | `757f2cda` | Style D per-section emit trail |
