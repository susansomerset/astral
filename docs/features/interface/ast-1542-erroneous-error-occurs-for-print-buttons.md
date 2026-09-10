# AST-1542 — Erroneous error occurs for print buttons

<!-- linear-archive: AST-1542 archived 2026-09-09 -->

## Linear archive (AST-1542)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1542/erroneous-error-occurs-for-print-buttons  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

When I click "Print…" buttons on the UI, I get an error toast saying that a popup has been blocked, even though the page loaded fine on the new tab as designed.  This error should not occur.

```
Astral error diagnostic
timestamp: 2026-08-31T19:15:20.140Z
message: Popup blocked — allow popups to open the HTML tab.
route: /jobs/recommended
astral_candidate_id: somerset
```

## As-is

On Recommended (and the other validate-then-blob Print / Open HTML controls), clicking Print opens the HTML tab as designed, but the UI still shows an error toast: `Popup blocked — allow popups to open the HTML tab.`

## To-be

When the HTML tab actually opens, no popup-blocked toast. That toast only appears when the browser truly blocked the new tab.

## Proposed steps

1. Fix the false-positive blocked check on every validate-then-blob open that uses `window.open(blobUrl, "_blank", "noopener,noreferrer")` then `if (!win)` → error toast. With `noopener`, browsers return `null` even when the tab opened successfully — that is why the toast fires while the page loads fine.
2. Detect a real block only when the tab did not open (e.g. open without relying on a null return under `noopener`, or an equivalent approach that still keeps the tab isolated). Exact naming/shape is plan-fix's call.
3. Apply the same correction at all four call sites that share this toast string so Base Resume Print, Session Open HTML, Session Cover Open HTML, and JAR Print Resume stay consistent.

## Component scope

* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — modified: Recommended JAR Print Resume is the reported surface (`/jobs/recommended`); same `noopener` + `!win` toast path.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — modified: Base Resume Print uses the identical blocked-toast pattern.
* `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` — modified: Session Open HTML uses the identical pattern (origin of the toast copy).
* `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` — modified: Session Cover Open HTML uses the identical pattern.

## Technical scope

* `JobAnalysisReportModal.tsx` — modified function (`handlePrintResume`): change how success vs blocked is decided after `window.open` of the blob URL so a successful tab does not toast.
* `ArtifactsBaseResumeContent.tsx` — modified Print handler: same success-vs-blocked decision after blob `window.open`.
* `AdminSessionResumePaste.tsx` — modified Open HTML handler: same success-vs-blocked decision after blob `window.open`.
* `AdminSessionCoverLetter.tsx` — modified Open HTML handler: same success-vs-blocked decision after blob `window.open`.

## Ancestor candidates

- [X] [AST-1350](https://linear.app/astralcareermatch/issue/AST-1350/unsupported-experience-shape-toast-no-emit-clarify-candidate) — unsupported experience shape toast / no emit (wired JAR Print Resume to fetch-then-blob + this exact toast on Recommended)
- [ ] [AST-1345](https://linear.app/astralcareermatch/issue/AST-1345/clarify-candidate-dataartifactsbase-resumeexperience-node) — clarify candidate_data.artifacts.base_resume.experience node (parent of [AST-1350](https://linear.app/astralcareermatch/issue/AST-1350/unsupported-experience-shape-toast-no-emit-clarify-candidate))
- [ ] [AST-1337](https://linear.app/astralcareermatch/issue/AST-1337/print-control-on-base-resume-content-add-a-print-button-to-base-resume) — print control on Base Resume Content (same toast + `noopener` null-check pattern)
- [ ] [AST-1314](https://linear.app/astralcareermatch/issue/AST-1314/add-a-print-button-to-base-resume-content) — add a Print button to Base Resume Content (parent of [AST-1337](https://linear.app/astralcareermatch/issue/AST-1337/print-control-on-base-resume-content-add-a-print-button-to-base-resume))
- [ ] AST-987 — Admin Session Resume Paste page + HTML new tab (introduced the toast string / blob-open pattern)
- [ ] AST-1025 — Admin Session Cover Letter page + session retention (same toast + `noopener` null-check pattern)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
