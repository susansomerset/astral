# AST-1325 — Structure header row: name | style | Enabled | Job Edit | up/down (Support alternative resume sections)

<!-- linear-archive: AST-1325 archived 2026-08-19 -->

## Linear archive (AST-1325)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1325/structure-header-row-name-style-enabled-job-edit-updown-support  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1299 — Support alternative resume sections  
**Blocked by / blocks / related:** parent: AST-1299

### Description

## As-is

AST-1323 was a partial fix — the structure editor header row still does not lay out controls as a single row in the requested order/shape.

## To-be

Each section header row lays out like:
`[SECTION NAME           ] [STYLE    V] Enabled:[X] Job Edit:[ ]  [up][down]`
with section body between headers.

## Susan comment (verbatim)

[bug] Likewise 1323 was a partial fix, but I want the header row to lay out like this:

```
[SECTION NAME           ] [STYLE    V] Enabled:[X] Job Edit:[ ]  [up][down]
```

## Proposed change

- [X] `ArtifactEditor` structure-authoring header: name | style | `Enabled:` | `Job Edit:` | Up/Down | Remove-after
- [X] `App.css`: nowrap single row, name flex-grow, compact style, flag labels nowrap

### Comments

#### radia — 2026-08-12T01:54:46.157Z
[code-rubric] PROCEED (Commit: 33c11a9e) header row name|style|Enabled:|Job Edit:|up/down

#### betty — 2026-08-12T01:51:38.457Z
`origin/sub/AST-1299/AST-1325-structure-header-row-name-style-enabled-job-edit-up-down-sup` @ `33c11a9e60179df6c956e2c069e0e798b45b0dda` · handoff suite loads

#### ada — 2026-08-12T01:49:23.235Z
[qa-handoff]
@Betty White

Command:
  cd src/ui/frontend && npx vitest run --config vite.config.ts \
    ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx -t "AST-1325"

Failure: suite does not load — esbuild `The symbol "headers" has already been declared` at
`tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx:300` (duplicate `const headers`
in the AST-1323 case; also still asserts `Job edit` at ~L208/L291/L294 — product now uses `Job Edit:`).

Not a product bug — `code(AST-1325)` @ `da21f5ca` matches plan (name|style|Enabled:|Job Edit:|up/down).
Please fix the test file / bible and reassign Ada.

#### ada — 2026-08-12T01:48:14.037Z
`origin/sub/AST-1299/AST-1325-structure-header-row-name-style-enabled-job-edit-up-down-sup` @ `da21f5cac45708f8ea6c812b75cf3ca76b493228`

Product matches plan. Betty: `test_ArtifactsBaseResumeContent.test.tsx` cannot load — duplicate `const headers` in AST-1323 case (~L292/L300); also still asserts `Job edit` (needs `Job Edit:`).

#### betty — 2026-08-12T01:18:18.427Z
[bug-repro]
`origin/sub/AST-1299/AST-1325-structure-header-row-name-style-enabled-job-edit-up-down-sup` @ `f4083a9067a941a8639e594d6eece7a522f5320a` · repro lands red, awaits fix

#### betty — 2026-08-12T01:11:50.367Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md ### AST-1323 — no name|style|Enabled:|Job Edit:|up/down row contract; AST-1323/1306 asserts on "Job edit" / checkbox-before-label will break

#### joan — 2026-08-12T01:11:40.969Z
[board-joan]  CANON: OK

UI-only header layout/label polish in `ArtifactEditor` + `App.css` (flex order, `Enabled:` / `Job Edit:` copy, nowrap row). No GET/PUT, catalog, slug, normalize, or config changes; format `<select>` still driven by `catalog.body_formats` only. Display labels are not a business-rules allowlist — conforms to `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`, and `pattern.ui.admin-endpoint`. No statute or pattern update required.

#### ada — 2026-08-12T01:10:16.761Z
`origin/sub/AST-1299/AST-1325-structure-header-row-name-style-enabled-job-edit-up-down-sup` @ `a7c8e775dd4fb157e2eb941cda387412be295455` · header row layout polish

---

_Implementation detail may live in git history on `origin/dev`._
