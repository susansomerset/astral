# AST-1323 — Structure editor: controls on collapsible header row with body between (Support alternative resume sections)

<!-- linear-archive: AST-1323 archived 2026-08-19 -->

## Linear archive (AST-1323)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1323/structure-editor-controls-on-collapsible-header-row-with-body-between  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1299 — Support alternative resume sections  
**Blocked by / blocks / related:** parent: AST-1299

### Description

## As-is

Section labels, type select, enabled, job-edit, and up/down controls are not on a single collapsible header row; section text sits at the bottom of the page instead of between headers.

## To-be

Those controls live on one collapsible header row per section, with that section's text body appearing between the headers.

## UAT report (verbatim)

[bug] Put the section labels, type select, enabled, job-edit (instead of job agent editable) and the up/down buttons on a single collapsible header row with the text for that section appearing between the headers (instead of the bottom of the page).

## Affected sibling

AST-1306 — Author extra sections (title and format)

## Proposed change

- [X] Structure authoring controls on `ArtifactEditor` `CollapsiblePanel` headers when catalog props are passed (title, format from `catalog.body_formats`, Enabled, Job edit, Up/Down, Remove if optional)
- [X] Section body text remains in the panel body between headers
- [X] Standalone flat `ResumeStructureEditor` UI removed from Base Resume Content; types-only module retained
- [X] Add section + Save sections stay separate from content Save; no GET/PUT/slug/normalize/config catalog changes
- [X] `JobAnalysisReportModal` unchanged (no catalog/authoring props)

### Comments

#### betty — 2026-08-12T00:08:51.959Z
`origin/sub/AST-1299/AST-1323-structure-editor-collapsible-header-row-body-between` @ `3663165657b024b913cf12171edc9b873c7a865d` · obsolete suite dropped

#### chuckles — 2026-08-12T00:07:58.810Z
[check-linear] Review Posted — Betty thread called on AST-1323

#### susan — 2026-08-12T00:06:24.131Z
@chuckles please call Betty's thread specifically about this issue to unblock her.

#### ada — 2026-08-11T23:53:57.612Z
[qa-handoff]
@Betty White

Radia fix-now (REVIEW @ `e8ffff6a` / product `21986a9e`): `tests/component/frontend/components/test_ResumeStructureEditor.test.tsx` still default-imports and renders the flat `ResumeStructureEditor` UI. That module is types-only after make-fix — no default export. Import/render will fail.

Not a product bug. Please delete or rewrite that test (type-only smoke or drop the file) and migrate any still-needed catalog assertions into `test_ArtifactsBaseResumeContent` (AST-1323 page case already covers header authoring). Bible already notes the file obsolete.

Stay Review Posted until tests land and Ada is reassigned.

#### radia — 2026-08-11T23:53:34.856Z
[code-rubric] REVIEW (Commit: 21986a9e) fix obsolete ResumeStructureEditor component test

#### betty — 2026-08-11T23:42:44.215Z
[bug-repro]
`origin/sub/AST-1299/AST-1323-structure-editor-collapsible-header-row-body-between` @ `6797d902` · repro lands red, awaits fix

#### betty — 2026-08-11T23:40:26.124Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md ### AST-1306 + test_ResumeStructureEditor / test_ArtifactsBaseResumeContent — assume standalone flat editor; missing header-row+body-between (Job edit / catalog on CollapsiblePanel) coverage Blast radius flags

#### joan — 2026-08-11T23:39:57.800Z
[board-joan]  CANON: OK

UI-only composition fix: structure controls move onto existing `ArtifactEditor` collapsible headers; GET/PUT, slug/prepare, normalize, and catalog HTTP unchanged. Plan explicitly preserves AST-1306 config-driven format options (`catalog.body_formats` only, no hardcoded TSX sets) — conforms to `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`, and `pattern.ui.admin-endpoint` thin-API shape. No statute or pattern carve-out required.

#### ada — 2026-08-11T23:37:20.575Z
`origin/sub/AST-1299/AST-1323-structure-editor-collapsible-header-row-body-between` @ `1d7ebcf8` · collapsible header plan

---

_Implementation detail may live in git history on `origin/dev`._
