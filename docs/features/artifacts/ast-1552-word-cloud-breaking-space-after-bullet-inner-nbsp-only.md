# AST-1552 — Word-cloud: breaking space after bullet (inner NBSP only)

<!-- linear-archive: AST-1552 archived 2026-09-09 -->

## Linear archive (AST-1552)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1552/word-cloud-breaking-space-after-bullet-inner-nbsp-only  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1539 — Word cloud items with INNER characters must be non-breaking  
**Blocked by / blocks / related:** parent: AST-1539

### Description

## Susan comment (verbatim)

[bug]

Now there are zero breaking spaces.  the space between the bullet character and the first character of the cloud item should be a normal, breaking space.

## As-is

Word-cloud emit (AST-1540) converts every remaining ordinary space in the cloud string to NBSP, so the space between `•` and the first character of each cloud item is non-breaking — the cloud has no breaking spaces left.

## To-be

Keep inner item spaces and hyphens non-breaking, but leave a normal breaking space between the bullet and the first character of each cloud item.

## Suggested engineer

Katherine (AST-1540)

## Proposed change

- [X] 1. Keep existing glue + inner space/hyphen conversion in `_glue_word_cloud_bullet_separators`.
- [X] 2. After that, restore `\u00a0•\u00a0` → `\u00a0• ` (breaking space after bullet; NBSP before • unchanged).
- [X] 3. Docstring notes AST-1552 restore; helper remains `word_cloud`-arm-only.
- [X] 4. No `_resume_site_markers` / generation / cover / config changes.

### Comments

#### radia — 2026-08-31T21:25:55.887Z
[code-rubric] PROCEED (Commit: 23483405) Post-bullet space restored

#### betty — 2026-08-31T21:21:02.841Z
[bug-repro]
`origin/sub/AST-1539/AST-1552-word-cloud-breaking-space-after-bullet` @ `41ca076a` · repro lands red, awaits fix

#### joan — 2026-08-31T21:16:47.186Z
[board-joan]  CANON: OK

#### betty — 2026-08-31T21:16:02.868Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/builder.md (AST-1540) — TestAst1540WordCloudInnerNonBreaking (+ TestAst1528 session HTML, TestAst1029) lock `\u00a0•\u00a0` / no ordinary spaces in cloud; repro needs `\u00a0• ` post-bullet while keeping inner NBSP/`\u2011` — revise those asserts + add/adjust [bug-repro] for post-bullet breaking space

#### katherine — 2026-08-31T21:14:43.188Z
`origin/sub/AST-1539/AST-1552-word-cloud-breaking-space-after-bullet` @ `d169eace66fa2cd385498c4d8058df8e7b9ee97d` · plan-fix ready

---

_Implementation detail may live in git history on `origin/dev`._
