# AST-1324 — base_resume_content must load/render existing artifact sections (default prose) (Support alternative resume sections)

<!-- linear-archive: AST-1324 archived 2026-08-19 -->

## Linear archive (AST-1324)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1324/base-resume-content-must-loadrender-existing-artifact-sections-default  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1299 — Support alternative resume sections  
**Blocked by / blocks / related:** parent: AST-1299

### Description

## As-is

The base_resume_content page does not freely render from the existing `candidate_data.artifacts.base_resume` payload — sections already present in candidate_data (artificially applied, including Highlights and the intended section set) do not drive the page load/render.

## To-be

Load from what is already in `candidate_data.artifacts.base_resume` and render freely from that artifact; if style/format is missing, default to prose.

## Susan comment (verbatim)

[bug] Sorry, Chuckles, I think I wasn't clear enough about this.  It's not the SAVE that is the issue.  It's the RENDER of the existing base_resume artifact.  The base_resume_content page should render FREELY based on the information in the base_resume artifact, setting the style to "prose" by default if it's missing.  I'm asking you to LOAD from what is already in candidate_data, which I artificially applied and correctly has all the sections I want.  Does that clear things up?

## Proposed change

- [X] `hydrate_resume_structure_from_base_resume` in `src/core/candidate.py` (read-only; missing format → `free_prose`)
- [X] `GET /resume_structure` hydrates from `artifacts.base_resume` after resolve
- [X] Frontend unchanged — panels follow hydrated enabled sections
- [X] Extra/new-extra `bullet_list` defaults unchanged

### Comments

#### radia — 2026-08-12T01:53:18.981Z
[code-rubric] PROCEED (Commit: e0825092) GET hydrates base_resume extras as free_prose

#### betty — 2026-08-12T01:16:09.831Z
[bug-repro]
`origin/sub/AST-1299/AST-1324-base-resume-content-must-load-render-existing-artifact-secti` @ `5cb301e889774e39b75d3bb9e83049602acf2869` · repro lands red, awaits fix

#### betty — 2026-08-12T01:11:20.168Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/candidate.md + ui/api AST-519/1306 GET / frontend/pages.md — no GET hydrate-from-base_resume coverage (extra panel + free_prose); orphan-hide page case may break

#### joan — 2026-08-12T01:10:59.017Z
[board-joan]  CANON: OK

Read-time `hydrate_resume_structure_from_base_resume` in core, wired through GET `/resume_structure` — thin API + config-driven formats (`RESUME_STRUCTURE_*`, `_is_resume_content_section_id`), no React format allowlist. Load default `free_prose` for missing format is an explicit in-helper decision (Susan prose), not a new config catalog or statute exception; ingest/add-section `bullet_list` defaults unchanged. Conforms to `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, and `pattern.ui.admin-endpoint`. No canon edit required.

#### ada — 2026-08-12T01:09:05.681Z
`origin/sub/AST-1299/AST-1324-base-resume-content-must-load-render-existing-artifact-secti` @ `f431b3c394de0e49880464ae41e279cee7cf24c7` · hydrate GET from base_resume

---

_Implementation detail may live in git history on `origin/dev`._
