# AST-1528 — Word-cloud NBSP bullet glue

**Linear:** [AST-1528](https://linear.app/astralcareermatch/issue/AST-1528/word-cloud-nbsp-bullet-glue-resume-word-clouds-need-non-breaking)  
**Parent:** [AST-1526](https://linear.app/astralcareermatch/issue/AST-1526/resume-word-clouds-need-non-breaking-spaces)  
**Publish ref:** `sub/AST-1526/AST-1528-word-cloud-nbsp-bullet-glue` (origin only)

Resume `word_cloud` sections (Core Competencies, Prior Experience on that format, and any other body section with `format: word_cloud`) currently emit pipe-authored and space-bullet-space text as `\u00a0• ` — NBSP only on the left of `•`. Print/Open HTML can still wrap onto a leading bullet because the space after `•` is ordinary. Restore the historical `__•__` equivalence: NBSP-bullet-NBSP on the shared resume site-marker expand path so base Print, session Open HTML, and job resume Print all glue separators the same way. Cover-letter from-block stays on `candidate.expand_cover_from_block_text` and is not retargeted.

## Explicit scope gate

Ticket **Scope** names `src/core/builder.py` only — modified `_resume_site_markers` and/or `word_cloud` body emit so space-bullet-space becomes NBSP-bullet-NBSP for cloud (and any text already on that expand path); no new files. All Files Changed / Stage steps stay inside that file. Cover from-block, `COVER_FROM_BLOCK_CONFIG` values, new digraphs, and experience-array work stay out.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/core/builder.py` | Tighten `_resume_site_markers` space-bullet-space → NBSP-bullet-NBSP; keep `_emit_education_list_html` partition/join on the same glued shape | core | engineer (Stage 1) |
| `tests/component/core/test_builder.py` | Flip asymmetric `\u00a0• ` expectations (markers, compact titles, education, competencies HTML) to `\u00a0•\u00a0` where they assert separator glue | tests | Betty (qa-child) |

## Stage 1: Shared marker glue + education partition

**Done when:** Calling `_resume_site_markers` on a pipe-authored cloud line (e.g. `A | B | C`) and on a line that already contains `" • "` both yield `\u00a0•\u00a0` between items; `A__•__B` still yields `\u00a0•\u00a0` (AST-1027). Base / session / job resume HTML that emit `word_cloud` after `_apply_resume_text_markers` show that glued shape in the competencies text node. Education list rows that use the post-marker bullet still split credential vs rest. Cover from-block emit path and `COVER_FROM_BLOCK_CONFIG["emit_separator"]` are untouched. Engineer `code()` commit contains **only** `src/core/builder.py`.

1. In `src/core/builder.py`, locate `_resume_site_markers` (today ends with `t.replace(" • ", "\u00a0• ")` after the `|` → `emit_separator` join). Change that final tighten so every occurrence of the cover/resume authoring emit separator (`COVER_FROM_BLOCK_CONFIG["emit_separator"]`, currently `" • "`) becomes the glued form `"\u00a0•\u00a0"` (NBSP + `•` + NBSP) — not `"\u00a0• "` (left-only). Prefer replacing via the already-loaded `emit_sep` variable (or the same config key) rather than a second hard-coded `" • "` literal, so the search string stays tied to config; the replacement string is the historical `__•__` → NBSP-bullet-NBSP shape.

   Keep order of operations unchanged: `__` → `\u00a0`, `~~` → `\u2011`, then `|` join with `emit_sep`, then the glue replace. Do **not** add a cloud-only fork helper. Do **not** edit `COVER_FROM_BLOCK_CONFIG` in `src/utils/config.py` (cover `expand_cover_from_block_text` shares `emit_separator`; leaving the config value as `" • "` keeps cover alone).

2. In the same file, update `_emit_education_list_html` so its local `bullet` partition/join string matches the new post-marker shape `"\u00a0•\u00a0"` (today it is `"\u00a0• "`). Education body text already runs through `_apply_resume_text_markers` before emit; without this companion edit, credential/rest split breaks after Stage 1 step 1.

   ⚠️ **Decision:** Prefer one expand path in `_resume_site_markers` (ticket Notes / DRY) over a `word_cloud`-arm-only post-pass. The education partition update is inseparable blast inside `builder.py` from that shared tighten — same separator shape, not a new digraph or format. Do **not** change header `h1_inner` (`name\u00a0• title`) or `"\u00a0• ".join(parts)` contact join; those are not on the space-bullet-space → glue replace and are outside cloud separator intent.

3. Optional local sanity (no test-tree commit): after the edit, in a Python REPL or one-off, assert:

   - `_resume_site_markers("A | B | C")` contains `A\u00a0•\u00a0B\u00a0•\u00a0C`
   - `_resume_site_markers("A__•__B")` contains `A\u00a0•\u00a0B`
   - `_resume_site_markers("A • B")` contains `A\u00a0•\u00a0B`

   Existing component tests that still expect `\u00a0• ` (asymmetric) will fail until Betty’s qa-child — that is expected; engineer does not patch `tests/**`.

## Betty qa-child (separator glue lock — not engineer Stage 1)

After engineer Stage 1 lands, Betty’s **qa-child** manifest must update `tests/component/core/test_builder.py` assertions that lock the old left-only shape, including at least:

- `TestAst1027UatMarkerExpand` (keep `__•__` → `\u00a0•\u00a0`; add or extend a pipe-authored / `" • "` case that expects `\u00a0•\u00a0` both sides).
- Compact-title / education / competencies HTML asserts that currently expect `\u00a0• ` (regular space after `•`) where those strings came from `_resume_site_markers` — flip to `\u00a0•\u00a0`.
- Cover from-block / `COVER_FROM_BLOCK_CONFIG["emit_separator"] == " • "` tests must **remain** green (no config change).

Do **not** weaken AST-1027 digraph fidelity. Engineer never commits under `tests/**` (`astral.git.engineer-test-tree-ban`).

## Estimate

Confirm Chuckles estimate: 2 — agree
