# AST-1526 — Resume word clouds need non-breaking spaces

<!-- linear-archive: AST-1526 archived 2026-09-09 -->

## Linear archive (AST-1526)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1526/resume-word-clouds-need-non-breaking-spaces  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** None / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Resume **word cloud** sections (Core Competencies, Prior Experience when formatted as `word_cloud`, and any other body section on that format) must glue bullet separators with non-breaking spaces the same way the old `__` digraphs did — so print/HTML wrap never drops a bare `•` onto the start of a line, and the spaces between cloud items stay non-breaking. Pipe-authored content (`|` → emit bullet) currently lands as ordinary `" • "` and only tightens the left side, which is weaker than the historical `__•__` → NBSP-bullet-NBSP contract operators still expect.

## Functional scope

* **Word-cloud bullet glue.** On Open HTML / Print for base, session, and job resumes, every `word_cloud` body shows a non-breaking space immediately before each `•`, and non-breaking spaces as the separators between cloud items (the old `__` equivalent) — not ordinary spaces that let the line wrap onto a leading bullet.
* **Shared marker path, word-cloud outcome.** Restore that glue through the existing resume site-marker expand used before HTML emit (so pipe-authored and already-bulleted cloud strings both get the full NBSP treatment). Do not invent a second visual language, new digraphs, or a CSS-only wrap workaround.
* **Out of scope.** Cover-letter from-block layout; inventing new authoring digraphs; changing `word_cloud` typography (uppercase / letter-spacing) beyond separator whitespace; reopening [AST-1381](https://linear.app/astralcareermatch/issue/AST-1381/fix-base-resume-issues-craftuiprint) experience-array work; UI authoring chrome.

## Component scope

* `src/core/builder.py` — **modified** — resume site-marker expand and/or `word_cloud` emit so cloud bullet joins use NBSP before `•` and NBSP between items (old `__` equivalence). No other files unless plan-child proves a config token already owns the emit separator and must move with DRY.

## Technical scope

* `src/core/builder.py` — **modified **`_resume_site_markers` (and only if needed the `word_cloud` arm of body-section emit): after `|`→bullet join (or when text already contains space-bullet-space), produce the same NBSP-bullet-NBSP shape `__•__` historically expanded to, so cloud HTML text nodes no longer keep a regular space after `•`. Do not fork a parallel marker helper for clouds alone unless Joan/plan forces it; prefer one expand path (DRY).
* No new tables, schema fields, or agent_task prompt changes expected.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>)): authoring/emit separators already live on `COVER_FROM_BLOCK_CONFIG`; do not invent a second inline separator set in the builder. `pattern.layers.import-discipline` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>)): emit stays in core builder; UI does not own spacer logic.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)) — touch only marker/word-cloud glue needed for this outcome; `astral.standards.dry-and-focused-functions` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)) — keep one expand path; `astral.standards.no-hardcoded-sets` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)) / `astral.config.config-source-of-truth` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)) — if separator literals move, they move via existing config keys, not a new inline set; `astral.layers.import-direction` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)); `astral.git.engineer-test-tree-ban` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)) — Betty owns tests/bible. Adjacent history: AST-1027 (preserve `__`/`~~` so markers expand 1:1) and [AST-1381](https://linear.app/astralcareermatch/issue/AST-1381/fix-base-resume-issues-craftuiprint) (`|`→`•`); this epic closes the remaining space-side gap for word clouds.

## Acceptance criteria

1. A `word_cloud` section authored with `|` between items (e.g. Core Competencies) prints/Open-HTMLs with `\u00a0` immediately before each `•` and `\u00a0` between items — not a regular space after the bullet that allows wrap to start with `•`.
2. The same section authored with the old `__•__` digraphs still expands to the same NBSP-bullet-NBSP shape (no regression vs AST-1027).
3. Base resume Print, session Open HTML, and job resume Print that emit `word_cloud` all show the glued separators (shared builder path).
4. Non-`word_cloud` formats are unchanged in intent (no new digraphs, no cloud typography redesign); cover-letter from-block is untouched unless it already shared this exact helper call and the glue change is inseparable (prefer leave cover alone).

## Open questions

none

## Proposed child tickets

#### 1: **Word-cloud NBSP bullet glue - Katherine**

Restore non-breaking spaces before each cloud `•` and between cloud items (old `__` equivalence) on the shared resume marker / `word_cloud` emit path so Print and Open HTML never wrap onto a leading bullet. Does **not** own cover from-block, new digraphs, or experience-array work.
**Citations: **`pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.git.engineer-test-tree-ban`.
**Scope: **`src/core/builder.py` — **modified **`_resume_site_markers` and/or `word_cloud` body emit so space-bullet-space becomes NBSP-bullet-NBSP for cloud (and any text already on that expand path); no new files.
**Estimate: 2**

Monolith check: Functional scope has 2 capabilities on one inseparable emit path — single child intentional.

---

## Original brief

For word clouds, the string between the bullets should be non-breaking spaces, and one nonbreaking space before the bullet character (so that the new line never starts with a bullet).  The equivalent of the `__` characters in the old formatting method.

### Comments

#### chuckles — 2026-08-30T05:00:56.021Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1536** | Word-cloud NBSP glue must apply at render, not generation |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1536** — _Word-cloud NBSP glue must apply at render, not generation_
- **Quick check:** re-run the failure you reported for **AST-1536**.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-08-29T20:07:10.993Z
\[bug\]

The word-cloud nonbreaking spaces should be applied at the time of RENDER, not the time of GENERATION.  Resume content can be switched from word cloud to free prose, and the additional encoding would mess it up.

---

_Implementation detail may live in git history on `origin/dev`._
