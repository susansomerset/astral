# AST-1357 — Unlock Profile Original Resume Text

**Linear:** [AST-1357](https://linear.app/astralcareermatch/issue/AST-1357)
**Parent:** [AST-1356](https://linear.app/astralcareermatch/issue/AST-1356) — Make profile original resume text read/write
**Publish ref:** `sub/AST-1356/AST-1357-unlock-profile-original-resume-text`

Remove the Candidate Profile ad-hoc lock that disables Original Resume Text when `artifacts.base_resume` is present (including the lock placeholder). The field stays on the existing Profile `values` / PUT save path and dirty-leave wiring from AST-1336; no Artifacts regenerate redesign, no new warning/config lock.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Delete `hasBaseResume` and stop setting `disabled` / lock placeholder on the Original Resume Text tab | ui |

**Do not touch:** `TabbedTextArea.tsx`, `useDirtyLeaveSaveThenNavigate.ts`, `App.tsx`, shapes/`config.py` Profile sections, Artifacts generate/regenerate UI or craft-resume paths, Contact fields, other Profile text tabs, Intake preamble, Admin session resume paste, `tests/**`, `docs/test-bible/**`, canon.

## Stage 1: Remove Original Resume Text lock

**Done when:** On Candidate Profile for a candidate that already has `artifacts.base_resume`, the Original Resume Text tab textarea is enabled, accepts typed/pasted edits, participates in dirty detection the same as Bio Summary / other text tabs, Save persists `context.raw_resume` via the existing `PUT /api/candidates/:id/data` body, Cancel restores the last loaded/saved value, and candidates without a base resume behave as today. No lock placeholder copy remains.

1. In `src/ui/frontend/src/pages/CandidateProfile.tsx`, delete the line:

   ```ts
   const hasBaseResume = Boolean(getByPath(values, "artifacts.base_resume"))
   ```

   It exists only to drive the resume lock (around the signature-image helpers). After deletion, `getByPath` remains used elsewhere in this file — do not remove the import.

2. In the same file, inside the `textTabs` map that builds `TextTab[]` from `tabSections`, replace the resume-special-case block with ordinary tab props — no `isResume`, no `disabled`, no lock placeholder:

   **As-is (remove):**

   ```ts
   const textTabs: TextTab[] = tabSections.map(sec => {
     const f = sec.fields[0]
     const isResume = f.key === "context.raw_resume"
     return {
       label: sec.label,
       key: f.key,
       disabled: isResume && hasBaseResume,
       // Prefer shapes placeholder; resume-lock override when base resume exists.
       placeholder: f.placeholder ?? (isResume && hasBaseResume
         ? "Locked — base resume has been generated from this text"
         : undefined),
       help: typeof f.help === "string" && f.help.trim() ? f.help : undefined,
     }
   })
   ```

   **To-be (exact):**

   ```ts
   const textTabs: TextTab[] = tabSections.map(sec => {
     const f = sec.fields[0]
     return {
       label: sec.label,
       key: f.key,
       placeholder: f.placeholder,
       help: typeof f.help === "string" && f.help.trim() ? f.help : undefined,
     }
   })
   ```

   ⚠️ **Decision:** Drop `disabled` entirely from these tabs rather than pass `disabled: false`. `TextTab.disabled` is optional; omitting it matches other unlocked tabs and avoids keeping dead lock wiring. Rejected: shapes/config flag for editability (`astral.layers.ui-config-driven-business-logic` — remove the React lock, do not invent a parallel rule). Rejected: clearing or invalidating `artifacts.base_resume` on edit (parent Boundaries).

3. Do **not** change `persistProfile`, `handleCancel`, `isDirty`, or `useDirtyLeaveSaveThenNavigate` wiring. Once the textarea is enabled, edits to `context.raw_resume` already flow through `onChange={set}` → `values` → the same dirty stringify compare and PUT body as other Profile fields (AST-1336). AC4 (Artifacts regenerate consumes saved text) is already product-owned via `context.raw_resume` / existing craft path — verify only that Save still writes that key; do not open Artifacts UI.

4. Frontend compile/lint only for this page change: from `src/ui/frontend`, `npx tsc -b --pretty false` and eslint on the touched file (same bar as adjacent Profile work). No product commits in `tests/**`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1357
**Overall:** APPROVED
**Publish ref:** `sub/AST-1356/AST-1357-unlock-profile-original-resume-text` @ `58dd9eccca6aebbb7be87d0f4668691acaf5dea3`

## Traceability
AC 1–6 → Stage 1 (remove `hasBaseResume` lock in `CandidateProfile.tsx`; existing `values` / PUT persist / `handleCancel` / `isDirty` / `useDirtyLeaveSaveThenNavigate` unchanged; AC4 verify-only via `context.raw_resume` save path).

## Findings

### acceptable
- **Location:** Parent Architectural definition — `pattern.ui.dirty-leave-save-then-navigate`
- **Finding:** Pattern catalog entry is `status: proposed` (not `approved`).
- **Recommendation:** Acceptable here — citation inherited from parent AST-1356; plan does not invent new dirty-leave wiring and matches the pattern’s solution shape (hook unchanged; enabling the textarea lets `context.raw_resume` participate in existing dirty/save flow).

No `fix-now` or `discuss` findings. R1–R6 pass: single-file `ui` scope; lock removal aligns with `astral.layers.ui-config-driven-business-logic`; placement and in-scope boundaries honored; DRY via deletion not parallel paths; layer/import surface untouched.

context_tokens≈15000

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1356/AST-1357-unlock-profile-original-resume-text`
**Product commits:** `8e58e420` (remove hasBaseResume lock + placeholder on Original Resume Text tab)
