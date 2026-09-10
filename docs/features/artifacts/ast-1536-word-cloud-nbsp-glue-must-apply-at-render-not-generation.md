# AST-1536 — Word-cloud NBSP glue must apply at render, not generation

<!-- linear-archive: AST-1536 archived 2026-09-09 -->

## Linear archive (AST-1536)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1536/word-cloud-nbsp-glue-must-apply-at-render-not-generation  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1526 — Resume word clouds need non-breaking spaces  
**Blocked by / blocks / related:** parent: AST-1526

### Description

[bug]

The word-cloud nonbreaking spaces should be applied at the time of RENDER, not the time of GENERATION. Resume content can be switched from word cloud to free prose, and the additional encoding would mess it up.

## Proposed change

- [X] `_resume_site_markers` — remove global full glue; restore left-only `emit_sep` → `\u00a0•` 
- [X] Add `_glue_word_cloud_bullet_separators` render-only helper
- [X] `_emit_body_sections_html` word_cloud arm calls glue before emphasis HTML
- [X] `_emit_education_list_html` partition bullet reverted to `\u00a0•` 
- [X] Cover from-block / header / contact paths untouched

## QA test manifest

1. **[bug-repro]** free_prose no cloud glue: `tests/component/core/test_builder.py::TestAst1536BugReproWordCloudFormatSwitch::test_free_prose_emit_has_no_cloud_glue`
2. word_cloud control still glued: `tests/component/core/test_builder.py::TestAst1536BugReproWordCloudFormatSwitch::test_word_cloud_emit_still_glued_after_format_switch_content`
3. Markers left-only + render cloud: `tests/component/core/test_builder.py::TestAst1528WordCloudNbspBulletGlue`
4. Digraph + compact-title/meta/edu regression: `TestAst1027UatMarkerExpand`, `TestAst998ExperienceJobRender`, `TestAst1008ExperienceGoldenLayout`, `TestAst1007NestedTypographyMarkers`, `TestAst1009EducationSkillsPrior`, `TestAst1010HeaderContactMetaStyles`, `TestAst1021DocumentTitleChrome`, `TestAst1382BugReproBaseResumeIssues::test_resume_site_markers_and_emit_convert_authoring_pipes`

**Repro gate:** item 1 green after make-fix @ `58aaece6`.

### Comments

#### radia — 2026-08-30T00:54:58.854Z
[code-rubric] PROCEED (Commit: 58aaece6) Render-only cloud glue clean

#### betty — 2026-08-30T00:51:51.584Z
[bug-repro]
`origin/sub/AST-1526/AST-1536-word-cloud-nbsp-glue-at-render` @ `15b28b28` · repro red, awaits fix

#### joan — 2026-08-30T00:49:32.412Z
[board-joan]  CANON: OK

Proposed change reverts AST-1528 global glue in `_resume_site_markers` and applies `\u00a0•\u00a0` only in the `word_cloud` emit arm via `_glue_word_cloud_bullet_separators` — still reads `emit_sep` from `COVER_FROM_BLOCK_CONFIG`; no config mutation; core-only; cover from-block untouched. Aligns with `astral.standards.in-scope-only`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, and cited patterns `pattern.config.config-block` / `pattern.layers.import-discipline`. Parent epic prose favoring one shared expand path is a plan/definition tension resolved by Susan’s render-time bug — not a canon gap requiring statute or pattern edits.

context_tokens≈22000

#### betty — 2026-08-30T00:49:21.824Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/builder.md § AST-1528 — no format-switch repro; TestAst1528WordCloudNbspBulletGlue locks generation-path glue that proposed change removes

#### katherine — 2026-08-30T00:48:39.801Z
`origin/sub/AST-1526/AST-1536-word-cloud-nbsp-glue-at-render` @ `5002e79e6965b203f886ff3e12175e0b861d98d0` · render-only glue

---

_Implementation detail may live in git history on `origin/dev`._
