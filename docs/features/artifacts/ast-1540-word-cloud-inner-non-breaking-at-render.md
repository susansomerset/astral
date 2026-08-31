# AST-1540 — Word-cloud inner non-breaking at render

**Linear:** [AST-1540](https://linear.app/astralcareermatch/issue/AST-1540/word-cloud-inner-non-breaking-at-render-word-cloud-items-with-inner)  
**Parent:** [AST-1539](https://linear.app/astralcareermatch/issue/AST-1539/word-cloud-items-with-inner-characters-must-be-non-breaking)  
**Publish ref:** `sub/AST-1539/AST-1540-word-cloud-inner-non-breaking-at-render` (origin only)

AST-1528/AST-1536 glued word-cloud **bullet separators** with NBSP at render (`\u00a0•\u00a0`), but multi-word and hyphenated **items** still soft-wrap on ordinary spaces and ASCII hyphens inside the item. Extend the existing render-only glue helper so remaining breakable spaces and ASCII hyphens in the cloud emit string become non-breaking before HTML — without putting that encoding on generation, `_resume_site_markers`, or non-`word_cloud` formats.

## Explicit scope gate

Ticket **Scope** names `src/core/builder.py` only — **modified** render helper used by the `word_cloud` arm of body-section emit (today `_glue_word_cloud_bullet_separators`): after existing bullet-separator glue, convert remaining ordinary spaces to NBSP and remaining ASCII hyphens to non-breaking hyphens in that emit-only string. Do not put this conversion on `_resume_site_markers` / generation. Shared marker path stays left-only for non-cloud formats. All Files Changed / Stage steps stay inside that file (Betty owns any `tests/**` follow-up). Cover from-block, new digraphs, typography redesign, and non-`word_cloud` formats stay out.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/core/builder.py` | Extend `_glue_word_cloud_bullet_separators` (keep call site on `word_cloud` arm): after `\u00a0•\u00a0` glue, replace remaining ordinary `" "` → `\u00a0` and remaining ASCII `"-"` → `\u2011` | core | engineer (Stage 1) |
| `tests/component/core/test_builder.py` | Lock inner NBSP / non-breaking-hyphen on `word_cloud` emit; keep format-switch / left-only marker asserts green | tests | Betty (qa-child) |

## Stage 1: Inner non-breaking on cloud render glue

**Done when:** A `word_cloud` section whose items contain ordinary spaces and/or ASCII hyphens (no `__` / `~~` digraphs required) emits those characters as `\u00a0` and `\u2011` inside `p.competencies-list` on base Print / session Open HTML / job Print (shared `_emit_body_sections_html` path). Existing `\u00a0•\u00a0` bullet glue still holds. `_resume_site_markers` output is unchanged by this ticket (left-only / digraph contracts from AST-1536). Switching the same content to `free_prose` does not show cloud inner NBSP / `\u2011` encoding. Engineer `code()` commit contains **only** `src/core/builder.py`.

1. In `src/core/builder.py`, locate `_glue_word_cloud_bullet_separators` (immediately after `_resume_site_markers`; docstring today cites AST-1536). **Keep the function name and its single call site** in `_emit_body_sections_html` (`elif fmt == "word_cloud":` → `cloud_text = _glue_word_cloud_bullet_separators(str(text))` then `_emit_inline_emphasis_html(cloud_text)`). Do **not** add a parallel helper or a second call from `_apply_resume_text_markers`, `_mark_resume_value`, or any non-`word_cloud` format arm.

2. Extend the helper body so order of operations is exactly:

   a. Early return if `not text` (unchanged).  
   b. Load `emit_sep = COVER_FROM_BLOCK_CONFIG["emit_separator"]` and set `glued = "\u00a0•\u00a0"` (unchanged).  
   c. Apply existing bullet glue: `t = text.replace(emit_sep, glued).replace("\u00a0• ", glued)`.  
   d. **Then** convert remaining ordinary spaces: `t = t.replace(" ", "\u00a0")`.  
   e. **Then** convert remaining ASCII hyphens: `t = t.replace("-", "\u2011")`.  
   f. `return t`.

   Update the docstring to state: NBSP both sides of `•`, then remaining spaces → NBSP and ASCII hyphens → non-breaking hyphen, for `word_cloud` HTML emit only (AST-1536 / AST-1540).

   ⚠️ **Decision:** Extend `_glue_word_cloud_bullet_separators` in place (ticket Notes / DRY) rather than a second helper or a CSS `white-space` rule on `.competencies-list`. Character-level emit matches digraph history (`__` / `~~`) and keeps format-switch safe. Do **not** edit `_resume_site_markers`, `COVER_FROM_BLOCK_CONFIG`, cover from-block, header/contact joins, or non-cloud format arms. Do **not** convert en-dash / em-dash / soft hyphen — only ASCII `"-"` and ordinary `" "`.

3. Optional local sanity (no test-tree commit): after the edit, in a Python REPL or one-off, assert roughly:

   - `_glue_word_cloud_bullet_separators("Delivery | Alignment")` (or post-marker `"Delivery\u00a0• Alignment"` / `"Delivery • Alignment"`) yields full `\u00a0•\u00a0` between items **and** no ordinary `" "` left in the result.  
   - `_glue_word_cloud_bullet_separators("AI-Assisted Delivery • Cloud")` (after glue path) contains `AI\u2011Assisted\u00a0Delivery` and `\u00a0•\u00a0` (or equivalent glued bullet).  
   - `_resume_site_markers("A | B | C")` still returns left-only `"A\u00a0• B\u00a0• C"` (no change).  
   - `_resume_site_markers("AI~~Assisted__Delivery")` still expands digraphs only (`AI\u2011Assisted\u00a0Delivery`) — this ticket does not re-encode on the marker path.

   Existing component tests that only lock separator glue stay green; new inner-space / hyphen asserts are Betty’s qa-child — engineer does not patch `tests/**`.

## Betty qa-child (inner non-breaking lock — not engineer Stage 1)

After engineer Stage 1 lands, Betty’s **qa-child** manifest should extend `tests/component/core/test_builder.py` (and bible § as needed) to assert, on a `word_cloud` session/base emit path:

- Multi-word items without digraphs appear with `\u00a0` between words inside `p.competencies-list` (e.g. `Project\u00a0Management`).  
- ASCII-hyphenated items appear with `\u2011` (e.g. `AI\u2011Assisted`).  
- Existing AST-1528/AST-1536 separator glue and format-switch (`TestAst1536BugReproWordCloudFormatSwitch`) remain green — free_prose must **not** inherit inner cloud NBSP / `\u2011` from this helper.  
- `_resume_site_markers` left-only and digraph asserts unchanged.

Engineer never commits under `tests/**` (`astral.git.engineer-test-tree-ban`).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Traceability

1→Stage 1 (inner `" "` → `\u00a0`, `"-"` → `\u2011` after bullet glue in `_glue_word_cloud_bullet_separators`).  
2→Stage 1 (existing emit_sep / left-only → `\u00a0•\u00a0` steps unchanged).  
3→Stage 1 (helper remains word_cloud-arm-only; markers / generation untouched → format switch safe).  
4→Stage 1 (shared `_emit_body_sections_html` word_cloud arm → base / session / job).  
5→Stage 1 (no cover / non-cloud / digraph / config edits).

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1540
**Overall:** APPROVED
**Publish ref:** `sub/AST-1539/AST-1540-word-cloud-inner-non-breaking-at-render` @ `3b6622318208540c86fac5a9d7342c8e9c843959`

## Traceability

1→Stage 1 (`" "` → `\u00a0`, `"-"` → `\u2011` after bullet glue in `_glue_word_cloud_bullet_separators`). 2→Stage 1 (existing `emit_sep` / `\u00a0• ` → `\u00a0•\u00a0` unchanged). 3→Stage 1 (helper word_cloud-arm-only; `_resume_site_markers` / generation untouched). 4→Stage 1 (shared `_emit_body_sections_html` `word_cloud` arm). 5→Stage 1 (no cover / non-cloud / config / digraph edits).

## Findings

### acceptable — Procedure / assignee at fetch
- **Location:** Linear AST-1540
- **Finding:** Status `Plan Ready` but assignee was Katherine Johnson (not Joan) at `get-issue` time.
- **Recommendation:** Chuckles spawn is authoritative for this stdout-only pass; restore implementer after posting upshot per validate-plan §8.

### acceptable — Files Changed `tests/**` row
- **Location:** Files Changed table
- **Finding:** Row names `tests/component/core/test_builder.py` while ticket `## Scope` is `builder.py` only.
- **Recommendation:** Explicit scope gate + Betty qa-child section correctly partition engineer vs Betty ownership; Stage 1 commit boundary (`code()` only `src/core/builder.py`) is clear.

### acceptable — Parent cites `astral.layers.import-direction`; child citations omit it
- **Location:** Citations vs parent Architectural definition
- **Finding:** Child lists `pattern.layers.import-discipline` instead of repeating the statute id.
- **Recommendation:** No action — single-file core change still satisfies import-direction; pattern citation is sufficient for R6.

No `fix-now` or `discuss` findings on plan substance.

context_tokens≈42000

## Review (build)

**Built:** `origin/sub/AST-1539/AST-1540-word-cloud-inner-non-breaking-at-render` @ `bc5ad81a` — `_glue_word_cloud_bullet_separators` after `\u00a0•\u00a0` glue replaces remaining `" "` → `\u00a0` and `"-"` → `\u2011`; call site still `word_cloud` arm only.

**Out of build scope (Betty / qa-child):** inner NBSP / non-breaking-hyphen asserts on `word_cloud` emit; format-switch / left-only marker locks stay hers.
