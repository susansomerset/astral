# AST-1336 — Candidate Profile dirty-leave wiring

**Linear:** [AST-1336](https://linear.app/astralcareermatch/issue/AST-1336)
**Parent:** [AST-1315](https://linear.app/astralcareermatch/issue/AST-1315) — Do not navigate away from dirty content
**Publish ref:** `sub/AST-1315/AST-1336-candidate-profile-dirty-leave-wiring`

Wire Candidate Profile to the shared dirty-leave helper from AST-1335 so unsaved Profile edits cannot be silently discarded by in-app navigation: track dirty against the last loaded/saved snapshot, prompt with Save as primary, persist via the existing Profile PUT path, then continue to the requested destination. Profile only — does not implement the helper, does not expand to other Save pages, and does not treat in-page text-tab switches as leave.

**Prerequisite (already on this worktree via `origin/ftr/AST-1315-do-not-navigate-away-from-dirty-content`):** `useDirtyLeaveSaveThenNavigate` in `src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate.ts` and `createBrowserRouter` in `App.tsx`. Do not re-implement or fork that contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Dirty vs last loaded/saved snapshot; Promise-based save shared by header Save and dirty-leave `onSave`; call `useDirtyLeaveSaveThenNavigate` | ui |

**Do not touch:** `useDirtyLeaveSaveThenNavigate.ts`, `App.tsx`, `routes.tsx`, `NavigationShell.tsx`, `TabbedTextArea.tsx`, `Modal.tsx`, ArtifactEditor / other Save pages, API/shapes/config, `tests/**`, `docs/test-bible/**`, canon pattern files (owned by AST-1335).

## Stage 1: Dirty snapshot + Promise save + dirty-leave wiring

**Done when:** On Candidate Profile with unsaved edits, choosing another in-app left-nav / SPA destination shows the themed Save confirm (primary Save). Affirm persists via the existing `PUT /api/candidates/:id/data` path (reload Profile shows the same values) and then lands on the requested destination. Cancel on the prompt stays on Profile with the draft intact. Save failure stays on Profile with the same visible error/toast as header Save and does not navigate. Clean Profile leaves without a prompt. Switching only among Profile’s in-page text tabs does not show the leave prompt and keeps draft text. Header Cancel and header Save still work as today when the operator is not mid-navigation.

1. In `src/ui/frontend/src/pages/CandidateProfile.tsx`, add:

   ```ts
   import { useDirtyLeaveSaveThenNavigate } from "../hooks/useDirtyLeaveSaveThenNavigate"
   ```

   Place it with the other relative imports (after `api` / toast helpers is fine).

2. **Dirty detection** — after `const data = fetched?.id === selectedId ? fetched.data : null`, compute:

   ```ts
   const isDirty =
     data !== null && JSON.stringify(values) !== JSON.stringify(data)
   ```

   `data` is already the last successfully loaded or saved edit tree (`fetched` updated on load and on successful save). Do **not** introduce a separate `touched` flag, a new lib helper, or shapes-driven field walking. Do **not** compare against a second snapshot object.

   ⚠️ **Decision:** `JSON.stringify` equality against the existing `fetched` snapshot. Both trees are produced by `editValuesFromCandidate` / `setByPath` on the same shape, so structural stringify is enough for Profile. Rejected: Modal-style `touched` (parent AC is value-vs-snapshot, not “user typed”). Rejected: new `deepEqual` module (one-page use; out of scope).

3. **Promise save shared by header Save and dirty-leave** — replace the fire-and-forget `handleSave` body with a `useCallback` that returns `Promise<void>`:

   ```ts
   const persistProfile = useCallback((): Promise<void> => {
     if (!selectedId) {
       return Promise.reject(new Error("No candidate selected"))
     }
     setError(null)
     return api(`/api/candidates/${selectedId}/data`, {
       method: "PUT",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify(values),
     })
       .then(async r => {
         if (!r.ok) await readApiError(r, `/api/candidates/${selectedId}/data`, "PUT")
         return r.json()
       })
       .then(candidate => {
         const vals = editValuesFromCandidate(candidate)
         setFetched({ id: selectedId, data: vals })
         setValues({ ...vals })
         refreshCandidate()
         setToast({ text: "Profile saved", variant: "success" })
       })
       .catch(e => {
         setError(e.message)
         setToast(
           e instanceof ApiError
             ? errorToastFromApiError(e)
             : { text: "Save failed", variant: "error" },
         )
         throw e
       })
   }, [selectedId, values, refreshCandidate])
   ```

   Requirements literal to this contract:

   - Same URL, method, headers, and `JSON.stringify(values)` body as today’s `handleSave`.
   - On success: update `fetched` + `values` from `editValuesFromCandidate(candidate)`, call `refreshCandidate()`, success toast — **before** the promise resolves (clears `isDirty` so `blocker.proceed()` is not re-blocked).
   - On failure: set `error` + error toast **and rethrow** (`throw e`) so `useDirtyLeaveSaveThenNavigate` calls `blocker.reset()` and does not navigate.
   - Header Save becomes: `function handleSave() { void persistProfile() }` (or `onClick={() => { void persistProfile() }}`). Do not change button labels, classes (`btn primary` / `btn secondary`), or placement.

4. **Header Cancel unchanged** — keep `handleCancel` as today: `if (data) setValues({ ...data }); setError(null)`. Do not call the dirty-leave helper, do not navigate, do not discard via a confirm.

5. **Wire the helper** — call (hooks must run unconditionally before any early `return`; place with other hooks, not after the Loading / No candidate early returns):

   ```ts
   useDirtyLeaveSaveThenNavigate({
     isDirty,
     onSave: persistProfile,
   })
   ```

   Do **not** pass custom `message` / `title` / `confirmLabel` / `cancelLabel` unless a later Plan Discuss requires it — use the helper defaults (Save primary / Cancel secondary). Do **not** wrap `TabbedTextArea` or invent a leave handler for tab index changes: `TabbedTextArea` keeps active tab in local state and does not change `location.pathname`; the helper already blocks only on pathname change.

6. Do **not** add `beforeunload`, autosave, debounce save, or Modal discard semantics. Do **not** edit other pages.

7. From `src/ui/frontend`, run `npm run build` (or at least `tsc -b`) and `npm run lint`. Fix only type/lint breaks caused by this file’s changes.

⚠️ **Decision:** One `persistProfile` Promise for both header Save and dirty-leave `onSave` (DRY; same error surface). Rejected: duplicating the PUT in an inline `onSave` that diverges from header Save.

⚠️ **Decision:** Rely on AST-1335’s pathname-only `useBlocker` for AC6 (in-page text tabs). Do not add Profile-local tab guards or route search/hash logic.

## Execution contract

- Stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1315/AST-1336-candidate-profile-dirty-leave-wiring`.
- If `useDirtyLeaveSaveThenNavigate` is missing from the tree after `sync-child.sh` with `--ftr AST-1315-do-not-navigate-away-from-dirty-content` — stop and comment on **parent** AST-1315; do not re-implement the helper.
- If `persistProfile` success updates snapshot after `proceed` would run (dirty still true) — stop and fix ordering so snapshot clear happens before the promise resolves (helper contract).
- Do not expand to other Save pages or change API/shapes contracts.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1336
**Overall:** APPROVED
**Publish ref:** `sub/AST-1315/AST-1336-candidate-profile-dirty-leave-wiring` @ `fd57bab1f9ad0eadd90ee101d5eb24f4cfb936bf`

## Traceability
AC1→S1 (`isDirty` + `useDirtyLeaveSaveThenNavigate`); AC2→S1 (`persistProfile` success clears snapshot then helper `proceed`); AC3→S1 (helper cancel/`blocker.reset` + header Cancel unchanged); AC4→S1 (`persistProfile` rethrow + error/toast, no `proceed`); AC5→S1 (`isDirty` false when `values` matches `fetched.data`); AC6→S1 (AST-1335 pathname-only blocker; no tab guards); AC7→S1 (header Save/Cancel labels, classes, and Cancel revert behavior preserved).

## Findings

### acceptable — `JSON.stringify` dirty check
**Location:** Stage 1 step 2
**Finding:** Stringify equality is a blunt instrument, but both trees share `editValuesFromCandidate` / `setByPath` origin; plan documents the rejected alternatives explicitly.
**Recommendation:** Proceed as written; revisit only if Profile field shapes introduce ordering instability (unlikely on this page).

### acceptable — no explicit self-assessment block
**Location:** plan doc overall
**Finding:** Plan omits formal self-assessment/conf prose, but single-stage scope, prerequisite gate, hook-order rule, and `persistProfile` contract are specific and match estimate 2.
**Recommendation:** None required before build.

context_tokens≈52000

[plan-rubric] PROCEED (Commit: fd57bab1f9ad0eadd90ee101d5eb24f4cfb936bf) Profile wiring faithful
