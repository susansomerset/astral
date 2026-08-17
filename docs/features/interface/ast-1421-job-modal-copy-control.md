# AST-1421 — Job modal Copy control (Create a Copy button on the Job Modal)

- **Linear:** [AST-1421](https://linear.app/astralcareermatch/issue/AST-1421/job-modal-copy-control-create-a-copy-button-on-the-job-modal)
- **Parent:** [AST-1419](https://linear.app/astralcareermatch/issue/AST-1419/create-a-copy-button-on-the-job-modal) — Create a Copy button on the Job Modal
- **Publish ref:** `sub/AST-1419/AST-1421-job-modal-copy-control`

Adds a labeled **Copy** control to the Job Detail modal (In Review and Skipped) and the Recommended Job Report. Clicking it fetches the AST-1420 snapshot from `GET /api/jobs/<astral_job_id>/copy`, writes pretty-printed JSON to the clipboard, and shows **Copied** on that control for 2 seconds. Does not assemble or expand agent_data. Does not replace Copy Application Email or Copy LinkedIn.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/copyJobSnapshot.ts` | New: `copyJobSnapshotToClipboard(astralJobId)` — GET copy route, `JSON.stringify(body, null, 2)`, clipboard write; returns `boolean` | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Copy button on Info tab; copied/busy state; call the helper | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Snapshot copy handler + `snapshotCopied` state; pass props into the header | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Always-available diagnostic Copy button (`btn secondary`) | ui |
| `src/ui/frontend/src/App.css` | `.entity-summary-actions` under the existing Summary layout block | ui |

**Do not touch:** `src/ui/api/api_jobs.py`; `src/core/tracker.py`; `src/ui/frontend/src/components/Modal.tsx`; `JobsInReview.tsx` / `JobsSkipped.tsx` / `JobsRecommended.tsx` (they already mount these modals); Skip This Job markup/handler/label; Copy Application Email / Copy LinkedIn handlers, labels, or `copyFeedback` span; tabs; job-detail GET payload; Company Modal; Data Management; Execution History; toasts; `tests/**`; `docs/test-bible/**`.

**Prerequisite on this worktree:** `GET /api/jobs/<astral_job_id>/copy` already exists (`copy_snapshot` in `src/ui/api/api_jobs.py`, `@require_auth`). If that route is missing when this plan is executed, stop and comment on parent AST-1419 — do not reimplement the assembler.

**Betty note (not this ticket’s build):** component coverage for the Copy control (label Copy → Copied after success, silent on non-OK / clipboard reject, email/linkedin/Skip unchanged) belongs on the test tree after Code Complete.

---

## Stage 1: Clipboard helper

**Done when:** `src/ui/frontend/src/lib/copyJobSnapshot.ts` exports `copyJobSnapshotToClipboard` that, given an `astral_job_id`, GETs the copy route through `api()`, pretty-prints the JSON body, writes it with `navigator.clipboard.writeText`, and returns `true` only when that write succeeds. Non-OK HTTP, JSON parse failure, and clipboard rejection all return `false` with no throw and no toast.

1. Create `src/ui/frontend/src/lib/copyJobSnapshot.ts` with exactly this public function (plus a one-line file comment that it is the diagnostic job snapshot clipboard write, not email/linkedin copy):

```typescript
import api from "./api"

export async function copyJobSnapshotToClipboard(astralJobId: string): Promise<boolean> {
  try {
    const res = await api(`/api/jobs/${encodeURIComponent(astralJobId)}/copy`)
    if (!res.ok) return false
    const body = await res.json()
    await navigator.clipboard.writeText(JSON.stringify(body, null, 2))
    return true
  } catch {
    return false
  }
}
```

2. Do not pass `?debug=` (or any other query). Assembler debug is server-side via `ui_llm_debug` on AST-1420. Do not log. Do not import Toast. Do not pretty-print on the server. Do not use `ClipboardItem`. Do not add a React hook.

⚠️ **Decision:** One lib helper, not duplicated fetch/stringify/clipboard in the two modals, and not a new React component. `api.ts` stays the HTTP client only — clipboard is not its job. Pretty-print is `JSON.stringify(body, null, 2)` as AST-1420’s snapshot contract already specified for this ticket. Failures are silent (parent: blocked clipboard write is silent; this ticket: no error toasts), including 404/500 from the route.

---

## Stage 2: Job Detail modal (In Review / Skipped)

**Done when:** Opening a job from In Review or Skipped shows a `btn secondary` control labeled **Copy** on the Job Detail Info tab, immediately above the existing Skip This Job control. After a successful helper return, that control’s label is **Copied** for 2000ms, then **Copy** again. Skip This Job’s existing wrapping `div`, `className`, `onClick`, `disabled`, and label expressions are byte-for-byte unchanged. Side tabs and the detail GET are unchanged.

1. In `src/ui/frontend/src/App.css`, immediately after the `.entity-summary-col` rule (the Summary layout block that already styles `JobDetailModal` Info), add:

```css
.entity-summary-actions {
  margin-top: 20px;
}
```

Do not add a TOC entry. Do not restyle `.btn`. Do not change `.modal-card--wide .modal-body` or `.side-tab-panel`.

2. In `src/ui/frontend/src/components/JobDetailModal.tsx`:

   - Import `copyJobSnapshotToClipboard` from `../lib/copyJobSnapshot`.
   - In `JobDetailModal`, add `const [snapshotCopied, setSnapshotCopied] = useState(false)` and `const [snapshotCopying, setSnapshotCopying] = useState(false)`.
   - Add `useEffect(() => { setSnapshotCopied(false) }, [jobId])`.
   - Add `async function handleCopySnapshot()`: if `!jobId` or `snapshotCopying`, return. `setSnapshotCopying(true)`. `const ok = await copyJobSnapshotToClipboard(jobId)`. `setSnapshotCopying(false)`. If `!ok`, return (label stays **Copy**). `setSnapshotCopied(true)` then `window.setTimeout(() => setSnapshotCopied(false), 2000)`. Same 2000ms as `handleCopyApplicationEmail` in `JobAnalysisReportModal.tsx`.
   - Pass `onCopy={handleCopySnapshot}`, `copied={snapshotCopied}`, `copying={snapshotCopying}` into `InfoTab`.

3. Extend the `InfoTab` props type with `onCopy: () => void`, `copied: boolean`, `copying: boolean`. Immediately **before** the existing Skip wrapper (`<div style={{ marginTop: 20 }}>` that contains Skip This Job), insert:

```tsx
<div className="entity-summary-actions">
  <button
    type="button"
    className="btn secondary"
    onClick={onCopy}
    disabled={copying}
  >
    {copied ? "Copied" : "Copy"}
  </button>
</div>
```

Do not add `in-flight` (that is primary-only). Do not add `in-row` (this is not a data-table row). Do not change Skip This Job. Do not put Copy in `Modal`’s header or footer. Do not wrap `SideTabPanel`.

⚠️ **Decision:** Info-tab placement, not chrome above `SideTabPanel`. Job Detail uses `size="wide"`, so `.modal-card--wide .modal-body` is `padding: 0` and `.side-tab-panel` is `height: 100%`. A sibling above the panel would need a new flex wrapper and would fight that fill. Copy on Info sits with the other job-level action (Skip), needs no Modal API change, and still satisfies AC1 (control on the Job Detail modal used from In Review and Skipped). Rejected: `headerActions` on `Modal.tsx` (shared shell, out of this ticket’s files).

⚠️ **Decision:** Labels are exactly `Copy` and `Copied` (not `✓ Copied`, not a separate feedback span). During the fetch the label stays `Copy` and the button is `disabled` — AC only names Copy ↔ Copied.

---

## Stage 3: Recommended Job Report header

**Done when:** Opening a Recommended job shows the same labeled Copy control on the Recommended Job Report header, visible even when application email and LinkedIn are both absent. Copy Application Email, Copy LinkedIn Profile, their `copyFeedback` span, and Print Resume / Print Cover Letter are unchanged. After a successful helper return, the diagnostic Copy control reads **Copied** for 2000ms, then **Copy** again.

1. In `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`, add optional props to `Props` and the destructuring list:

   - `onCopySnapshot?: () => void`
   - `snapshotCopied?: boolean`
   - `snapshotCopying?: boolean`

2. Change the links-row guard from `(applicationEmail || linkedInUrl)` to `(onCopySnapshot || applicationEmail || linkedInUrl)`.

3. Inside `.recommended-report-links`, **before** the existing `{applicationEmail && (` Copy Application Email button, insert:

```tsx
{onCopySnapshot && (
  <button
    type="button"
    className="btn secondary"
    onClick={() => onCopySnapshot()}
    disabled={snapshotCopying}
  >
    {snapshotCopied ? "Copied" : "Copy"}
  </button>
)}
```

Leave the Copy Application Email button, Copy LinkedIn Profile button, and `{copyFeedback && ( <span className="recommended-report-copy-feedback">{copyFeedback}</span> )}` exactly as they are. Do not drive `copyFeedback` from snapshot copy. Do not add CSS — `.recommended-report-links` already flex-wraps with `gap: 8px`.

4. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`:

   - Import `copyJobSnapshotToClipboard` from `../lib/copyJobSnapshot`.
   - Add `const [snapshotCopied, setSnapshotCopied] = useState(false)` and `const [snapshotCopying, setSnapshotCopying] = useState(false)` next to the existing `copyFeedback` state. Do not reuse `copyFeedback` for this control.
   - Add `useEffect(() => { setSnapshotCopied(false) }, [jobId])`.
   - Add `async function handleCopySnapshot()` identical in behavior to Stage 2 step 2 (guard `!jobId` / `snapshotCopying`; call helper; silent on `false`; 2000ms Copied).
   - On `<RecommendedJobReportHeader`, add `onCopySnapshot={handleCopySnapshot}`, `snapshotCopied={snapshotCopied}`, `snapshotCopying={snapshotCopying}`. Do not change `copyFeedback`, `onCopyApplicationEmail`, `onCopyLinkedIn`, or print props.

⚠️ **Decision:** Diagnostic Copy is always offered when the header is given `onCopySnapshot`, independent of email/linkedin presence. Gating it on `(applicationEmail || linkedInUrl)` would hide Copy on recommended jobs that lack those fields and fail AC1. It is an additional control — not a replacement. Its Copied state is the button label, not the existing gold `copyFeedback` span (that span stays email/linkedin-only so the two copy families do not share one word of feedback).

---

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1421
**Overall:** APPROVED
**Publish-ref:** `d77b117e0a1ead9a9cfe22e09260499a6204e44c`

## Traceability

AC1 → Stage 2 (Job Detail Info tab, default first tab) + Stage 3 (Recommended header, guard widened for snapshot-only jobs) · AC2 → Stage 1 (`JSON.stringify(body, null, 2)`) + Stage 2/3 (2000ms `Copied` label on the diagnostic button) · AC3 → Stage 2/3 boundaries (Skip/email/linkedin/tabs/detail GET untouched; `copyFeedback` span stays email/linkedin-only) · Parent AC2 (pretty-print clipboard JSON) → Stage 1 · Parent AC5 (Copied feedback) → Stage 2/3 · Parent AC6 (adjacent controls unchanged) → Stage 2/3 `Do not touch` list

## Findings

### discuss — Copy control lives on Info tab only (Job Detail)

**Location:** Stage 2, Info-tab placement decision  
**Finding:** Copy is not visible from JD or Agent Story side tabs; user must be on (or switch to) Info.  
**Recommendation:** Acceptable — Info is `SideTabPanel` default (`tabs[0]`), satisfies child AC1 (“on the Job Detail modal”), and the placement rationale (wide-modal layout, Skip adjacency) is sound.

### discuss — No `## Self-assessment` section

**Location:** Plan doc tail  
**Finding:** Only `## Estimate` confirm present; no confidence axes block.  
**Recommendation:** Optional template polish; estimate (2) matches staged scope — not blocking.

### acceptable — AST-1420 prerequisite documented

**Location:** Files Changed prerequisite note  
**Finding:** `GET /api/jobs/<astral_job_id>/copy` is already present on this worktree (`copy_snapshot` in `api_jobs.py`); plan correctly gates build on route existence without reimplementing the assembler.  
**Recommendation:** No change.

context_tokens≈38000

## Review (build)

**Built:** `origin/sub/AST-1419/AST-1421-job-modal-copy-control` @ `94207bdd36c80740d4438a9a6e6f58b6efeb1086`

Stages 1–3: `copyJobSnapshotToClipboard` helper; Copy on Job Detail Info tab; Copy on Recommended Job Report header. Tests deferred to Betty.
