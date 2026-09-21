# AST-1545 — Fix false popup-blocked toast on Print / Open HTML (Erroneous error occurs for print buttons)

<!-- linear-archive: AST-1545 archived 2026-09-09 -->

## Linear archive (AST-1545)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1545/fix-false-popup-blocked-toast-on-print-open-html-erroneous-error  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1542 — Erroneous error occurs for print buttons  
**Blocked by / blocks / related:** parent: AST-1542

### Description

## What this implements

Fix false "Popup blocked — allow popups to open the HTML tab." toast when validate-then-blob Print / Open HTML successfully opens the HTML tab. With `noopener`, `window.open` returns `null` even on success; stop treating that null as blocked. Applies at all four call sites that share the toast.

## Scope

### Component scope

* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — modified: Recommended JAR Print Resume is the reported surface (`/jobs/recommended`); same `noopener` + `!win` toast path.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — modified: Base Resume Print uses the identical blocked-toast pattern.
* `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` — modified: Session Open HTML uses the identical pattern (origin of the toast copy).
* `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` — modified: Session Cover Open HTML uses the identical pattern.

### Technical scope

- [X] `JobAnalysisReportModal.tsx` — modified function (`handlePrintResume`): change how success vs blocked is decided after `window.open` of the blob URL so a successful tab does not toast.
- [X] `ArtifactsBaseResumeContent.tsx` — modified Print handler: same success-vs-blocked decision after blob `window.open`.
- [X] `AdminSessionResumePaste.tsx` — modified Open HTML handler: same success-vs-blocked decision after blob `window.open`.
- [X] `AdminSessionCoverLetter.tsx` — modified Open HTML handler: same success-vs-blocked decision after blob `window.open`.

## Acceptance criteria

- [X] On Recommended, clicking Print Resume opens the HTML tab and does **not** show `Popup blocked — allow popups to open the HTML tab.` when the tab actually opened.
- [X] Base Resume Print, Session Open HTML, and Session Cover Open HTML have the same success-path behavior (no false blocked toast).
- [X] A truly blocked popup still surfaces the existing blocked toast (or equivalent clear failure) when the tab did not open.

## Boundaries

Does **not** change print HTML emit, fetch/validate flow, or cover Print's non-blob `window.open` path beyond the false-positive blocked toast on validate-then-blob opens.

## Notes for planning

Approved ancestor: AST-1350 (feature doc `docs/features/artifacts/ast-1350-unsupported-experience-shape-toast-no-emit.md`). Parent mini-epic AST-1542.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-31T20:29:26.690Z
[code-rubric] PROCEED (Commit: fdc47334) Clean four-site blob-open fix

#### joan — 2026-08-31T20:05:05.852Z
[board-joan] CANON: OK

No statute or pattern requires `window.open(..., "noopener,noreferrer")` for blob opens; clearing `opener` manually after open is fine. UI-only; AST-1350 unsupported-shape gate untouched.

#### betty — 2026-08-31T20:03:34.233Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md + pages.md — broken tests assert window.open(..., "noopener,noreferrer") on four blob sites; no repro that success omits Popup-blocked toast

#### hedy — 2026-08-31T20:02:01.171Z
`origin/sub/AST-1542/AST-1545-fix-false-popup-blocked-toast-on-print-open-html` @ `3e6b50d21cef6bc0acbe16da6159a62dc6ab2603` · noopener null false toast

---

_Implementation detail may live in git history on `origin/dev`._
