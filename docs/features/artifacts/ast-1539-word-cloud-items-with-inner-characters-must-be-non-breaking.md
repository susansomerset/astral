# AST-1539 — Word cloud items with INNER characters must be non-breaking

<!-- linear-archive: AST-1539 archived 2026-09-09 -->

## Linear archive (AST-1539)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1539/word-cloud-items-with-inner-characters-must-be-non-breaking  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** High / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

AST-1528/AST-1536 glued word-cloud **bullet separators** with NBSP at render, but multi-word cloud *items* still soft-wrap on ordinary spaces and ASCII hyphens inside the item (e.g. mid-phrase breaks in Print / Open HTML). Operators expect each cloud item—and the cloud string as a whole for breakable whitespace and hyphenation—to stay non-breaking the same way historical `__` / `~~` digraphs did, without re-encoding content at generation time (format switch must stay safe).

## Functional scope

* **Inner non-breaking cloud text.** On Open HTML / Print for base, session, and job resumes, every `word_cloud` body treats ordinary spaces and ASCII hyphens inside cloud items as non-breaking (no soft wrap mid-item), in addition to the existing NBSP glue around `•` separators.
* **Render-only encoding.** Apply that treatment only when emitting `word_cloud` HTML—not when generating or saving section text—so switching a section to `free_prose` (or another format) does not inherit cloud non-breaking characters (same contract as AST-1536).
* **Out of scope.** Cover-letter from-block; inventing new authoring digraphs; changing word-cloud typography (uppercase / letter-spacing) beyond break behavior; reopening experience-array work; UI authoring chrome; non-`word_cloud` formats.

## Component scope

* `src/core/builder.py` — **modified** — extend the existing `word_cloud` render glue path so remaining breakable spaces and hyphens in cloud text become non-breaking before HTML emit. No other files unless plan-child proves a shared CSS rule for `.competencies-list` must move with DRY (prefer character-level on the render helper, matching digraph history).

## Technical scope

* `src/core/builder.py` — **modified** render helper used by the `word_cloud` arm of body-section emit (today `_glue_word_cloud_bullet_separators`): after existing bullet-separator glue, convert remaining ordinary spaces to NBSP and remaining ASCII hyphens to non-breaking hyphens in that emit-only string. Do not put this conversion on `_resume_site_markers` / generation. Shared marker path stays left-only for non-cloud formats.
* No new tables, schema fields, agent_task prompts, or config separator keys expected.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>)): keep using existing `COVER_FROM_BLOCK_CONFIG` authoring/emit separators for bullet joins; do not invent a second separator vocabulary. `pattern.layers.import-discipline` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>)): non-breaking treatment stays in core builder emit; UI does not own spacer logic.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)) — touch only word-cloud render glue needed for inner non-breaking; `astral.standards.dry-and-focused-functions` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)) — extend the existing render glue helper rather than a parallel path; `astral.config.config-source-of-truth` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)) / `astral.standards.no-hardcoded-sets` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)) — separator literals stay on existing config keys; Unicode glue chars stay with the helper as today; `astral.layers.import-direction` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)); `astral.git.engineer-test-tree-ban` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)) — Betty owns tests/bible. Adjacent shipped intent: AST-1526 / AST-1528 (bullet glue) and AST-1536 (render-only, not generation).

## Acceptance criteria

1. A `word_cloud` section whose items contain ordinary spaces and/or ASCII hyphens (e.g. multi-word or hyphenated phrases) prints/Open-HTMLs with those inner spaces as `\u00a0` and those hyphens as `\u2011` in the cloud text node—Print/Open HTML does not soft-wrap mid-item on those characters.
2. Existing bullet glue remains: `\u00a0` immediately before each `•` and `\u00a0` between items (no regression vs AST-1528/AST-1536).
3. Saved / generated section text is unchanged by this treatment; switching the same content to `free_prose` (or another non-cloud format) does not show cloud inner NBSP / non-breaking-hyphen encoding.
4. Base resume Print, session Open HTML, and job resume Print that emit `word_cloud` all show the inner non-breaking treatment (shared builder render path).
5. Non-`word_cloud` formats and cover-letter from-block are unchanged in intent.

## Open questions

none

## Proposed child tickets

#### 1: **Word-cloud inner non-breaking at render - Katherine**

Extend the `word_cloud` render-only glue so ordinary spaces and ASCII hyphens inside cloud items become non-breaking in Print / Open HTML, without putting that encoding on generation or non-cloud formats. Does **not** own cover from-block, new digraphs, or typography redesign.
**Citations: **`pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.git.engineer-test-tree-ban`.
**Scope: **`src/core/builder.py` — **modified** render helper used by the `word_cloud` arm of body-section emit (today `_glue_word_cloud_bullet_separators`): after existing bullet-separator glue, convert remaining ordinary spaces to NBSP and remaining ASCII hyphens to non-breaking hyphens in that emit-only string. Do not put this conversion on `_resume_site_markers` / generation. Shared marker path stays left-only for non-cloud formats.
**Estimate: 2**

Monolith check: Functional scope has 2 in-scope capabilities on one inseparable render path — single child intentional.

---

## Original brief

The scope of [AST-1528](https://linear.app/astralcareermatch/issue/AST-1528/word-cloud-nbsp-bullet-glue-resume-word-clouds-need-non-breaking) was too narrow.  I want all characters in the word cloud string to be non-breaking.  That includes spaces, hyphens, or anything else that might think about soft-wrapping the string.

### Comments

#### chuckles — 2026-08-31T22:03:04.342Z
@susan AST-1552 (the UAT bug) finished the fix lane and merged into ftr; this parent was waiting on datt resume for prep-uat. Running that now.

#### susan — 2026-08-31T22:01:52.127Z
@chuckles Why is this stuck?

#### susan — 2026-08-31T20:52:51.926Z
\[bug\]

Now there are zero breaking spaces.  the space between the bullet character and the first character of the cloud item should be a normal, breaking space.

---

_Implementation detail may live in git history on `origin/dev`._
