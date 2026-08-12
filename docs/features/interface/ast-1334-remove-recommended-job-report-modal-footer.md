# AST-1334 — Remove Recommended Job Report modal footer

- **Linear:** [AST-1334](https://linear.app/astralcareermatch/issue/AST-1334/remove-recommended-job-report-modal-footer-remove-the-cancel-button-and)
- **Parent:** [AST-1329](https://linear.app/astralcareermatch/issue/AST-1329/remove-the-cancel-button-and-footer-from-the-recommended-job-modal) — Remove the Cancel button and footer from the Recommended Job Modal
- **Publish ref:** `sub/AST-1329/AST-1334-remove-recommended-job-report-modal-footer`

Hide the shared `Modal` footer Cancel/chrome for the Recommended Job Report modal only so Summary / Analysis / Artifacts content is fully visible. Dismiss stays on the header × (`pattern.ui.icon-control`). Artifacts-tab in-flight Cancel (`cancel_build`) is unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/Modal.tsx` | Add optional `showFooter` prop (default `true`); omit `.modal-footer` when `false` | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Pass `showFooter={false}` on the shared `Modal` | ui |

**Do not touch:** other `Modal` call sites; `App.css` (flex body already fills remaining height when footer is absent); Artifacts Generate/Cancel strip in `JobAnalysisReportModal`; `JobsRecommended.tsx` entry wiring; dirty-discard / AST-1315; any Save+Cancel edit modals; `tests/**`; `docs/test-bible/**`.

**Betty note (not this ticket’s build):** existing `tests/component/frontend/components/test_Modal.test.tsx` and `test_JobAnalysisReportModal.test.tsx` will need coverage for footer omission + preserved Artifacts Cancel / header Close — engineer does not edit the test tree.

---

## Stage 1: Opt out of shared Modal footer for the report only

**Done when:** Opening a Recommended job report renders no `.modal-footer` and no footer Cancel button; header × still closes the modal; while `BUILD_ARTIFACTS` (or compound hop), Artifacts strip still shows Generating… + Cancel beside it. Other Modal consumers still render their Cancel/Save footer unchanged.

1. In `src/ui/frontend/src/components/Modal.tsx`, extend `ModalProps` with `showFooter?: boolean` (document in the interface that default is show footer). Destructure it with default `showFooter = true` in the component signature next to the existing props (`open`, `onClose`, `title`, `children`, `onSave`, `dirty`, `size`, `stacked`).
2. In the same file, wrap the existing footer block so it renders only when `showFooter` is true:

```tsx
{showFooter && (
  <div className="modal-footer">
    <button className="btn secondary" onClick={guardedClose}>Cancel</button>
    {onSave && (
      <button className="btn primary" onClick={onSave}>Save</button>
    )}
  </div>
)}
```

Do not change `guardedClose`, dirty discard, header × (`className="icon-control"`), overlay/card/body markup, or any other prop behavior.

3. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, on the `<Modal …>` that wraps the report shell (the call that already passes `open={!!jobId}`, `onClose={onClose}`, `title={…}`, `size="wide"`), add `showFooter={false}`. Do not alter header chrome, tabs, Artifacts primary-action strip (`renderArtifactsPane` Generating… / Cancel), or list `onClose` wiring.

⚠️ **Decision:** Opt-in hide via `showFooter={false}` on this call site only — do **not** change Modal’s default (footer remains for every other consumer) and do **not** hide the footer whenever `onSave` is absent (read-only modals like Rubric / Materials Preview / Batch agent data still need Cancel).

**Compile / lint (before stage commit):** from `src/ui/frontend`, run the project’s usual typecheck/lint (`npm run build` or the repo’s established `tsc` / eslint script if that is what sibling UI tickets use). Fix only errors introduced by this stage’s files.

---

## Estimate

Confirm Chuckles estimate: 1 — agree
