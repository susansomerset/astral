---
id: pattern.ui.dirty-leave-save-then-navigate
name: Dirty-leave save-then-navigate
status: proposed
proposed_in: AST-1315
approved_by: null
approved_at: null
canonical_refs:
  - path: src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate.ts
    symbol: useDirtyLeaveSaveThenNavigate
  - path: src/ui/frontend/src/App.tsx
    symbol: createBrowserRouter
related_statutes:
  - astral.ui.frontend-file-placement
  - astral.ui.naming-conventions
  - astral.standards.dry-and-focused-functions
supersedes: null
superseded_by: null
---

# Problem

Operators lose in-progress page drafts when they leave via in-app navigation. Pages reinvent leave prompts, or wipe silently. Modal discard-on-close and ArtifactEditor autosave/`beforeunload` solve different problems and must not be overloaded for route leave.

# Solution shape

Shared hook `useDirtyLeaveSaveThenNavigate` (pointer in `canonical_refs`):

- Caller owns dirty detection and the persist function (`onSave` → resolve success / reject failure).
- When dirty and the SPA pathname would change, block with React Router `useBlocker` (requires a data router — `createBrowserRouter` in `App.tsx`).
- Themed confirm via `useUserConfirm`: primary/default action is Save (`btn primary`); Cancel is `btn secondary`.
- Affirm → await `onSave` → `blocker.proceed()`. Cancel → `blocker.reset()` (stay; draft intact). Save rejection → `blocker.reset()` (stay; caller surfaces error the same way as ordinary Save).
- Do not treat same-pathname in-page chrome (e.g. Profile text tabs) as leave.
- Do not change Modal discard-on-close or add Profile autosave.

## When not to use

- Modal close with unsaved edits — keep Modal’s discard-oriented confirm.
- ArtifactEditor / criteria editors that already autosave or use `beforeunload`.
- Hard browser tab close/refresh — out of scope for this pattern (browser-native if addressed later).
- Citing this pattern id as catalog law until `status: approved` (AUTHORING).

## Notes

Proposed in parent AST-1315 Architectural definition. Helper lands with AST-1335; Candidate Profile wiring is AST-1336. Archie approves the id separately; remediations may use the hook before approval without treating the catalog id as approved.
