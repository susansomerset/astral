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

**Built:** `origin/sub/AST-1419/AST-1421-job-modal-copy-control` @ `cbd2837fa7ef6a7435f2688043043ddcb6e1a67a`

Stages 1–3: `copyJobSnapshotToClipboard` helper; Copy on Job Detail Info tab; Copy on Recommended Job Report header. Tests deferred to Betty.

## Radia review

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1421  
**Publish ref:** `cbd2837fa7ef6a7435f2688043043ddcb6e1a67a` (`origin/sub/AST-1419/AST-1421-job-modal-copy-control`)  
**Overall:** CLEAN  

**Diff baseline:** `origin/dev...origin/sub/AST-1419/AST-1421-job-modal-copy-control`  
**Diff paths (19):** `src/ui/frontend/**` (5 product files), stacked AST-1420 backend (`src/core/tracker.py`, `src/ui/api/api_jobs.py`), Betty test-bible/tests for AST-1420 + AST-1421, plan docs for AST-1420 + AST-1421  
**Diff layers:** `core`, `ui`, `docs`  
**AST-1421 engineer commits (`68a90e83`…`94207bdd`):** only the 5 planned frontend files — no `api_jobs.py`, `tracker.py`, or list-page mounts touched  

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent/LLM confidence paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task / dispatch delegation |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector validation |
| astral.batch.batch-id-first | scoped | not-applicable | 1420 stack reads batch_id only; 1421 does not touch batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch_id minting |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/release lifecycle |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no write semantics on stacked backend |
| astral.config.config-source-of-truth | scoped | conforms | 1421 consumes existing copy route; no parallel config literals |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env wiring in 1421 chrome |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact dirs |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next / chain changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | dedicated `ast-1421-*.md` plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty touched test-bible/tests only |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests via Betty `test(AST-1421)` + merge-tests, not build commits |
| astral.layers.core-vs-external-bright-line | scoped | conforms | 1421 is frontend lib/components only |
| astral.layers.import-direction | scoped | conforms | frontend imports lib `api` + new helper; no UI→data/external |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/** changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no hardcoded job-state lists; uses existing modal/manifest patterns |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | read-only clipboard fetch |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render-verdict paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | copy route (stacked 1420) is `@require_auth`; client uses authenticated `api()` |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog edits |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | user-initiated click handler |
| astral.seed.define-approved | scoped | not-applicable | no define/seed work |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed operator rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed coverage |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | 1421 chrome has no data-layer calls |
| astral.standards.database-header-inventory | scoped | not-applicable | `database.py` untouched by 1421 |
| astral.standards.debug-contract-gated | scoped | conforms | 1421 does not pass `?debug=`; stacked 1420 debug remains server-gated |
| astral.standards.dry-and-focused-functions | scoped | conforms | single `copyJobSnapshotToClipboard` helper; modal handlers are thin |
| astral.standards.in-scope-only | scoped | conforms | 1421 build footprint = plan Stages 1–3; stacked 1420 backend is sibling prerequisite on branch, not 1421 scope creep |
| astral.standards.logging-via-utils | scoped | conforms | no `print()` / ad-hoc logging in 1421 frontend |
| astral.standards.names-not-ticket-ids | scoped | conforms | public names describe behavior |
| astral.standards.no-cross-contamination | scoped | conforms | no assembler reimplementation; AST-1420 route consumed as prerequisite |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | no enum/set literals added |
| astral.standards.public-then-helpers | scoped | conforms | exported helper at module top |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data changes |
| astral.state.core-decides-transitions | scoped | not-applicable | Skip handler unchanged; no new transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no transition enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no daisy-chain config/run changes |
| astral.ui.frontend-file-placement | scoped | conforms | helper under `src/lib/`; components under `components/` |
| astral.ui.naming-conventions | scoped | conforms | camelCase TS, kebab route via `api()` |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker/config surface |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1421)` at tip |
| orch.git.commit-vocabulary | universal | conforms | commit messages follow vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub branch under epic topology |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1419/AST-1421-...` |
| orch.git.merge-on-checkout | universal | conforms | review uses fetched origin refs |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops |
| orch.git.no-dev-agent-branches | universal | conforms | publish ref is sub/* |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1419 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs origin/dev only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Info-tab placement tradeoff Joan-preaccepted |
| orch.pipeline.plan-is-bible | universal | conforms | helper + both modals match binding plan text |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a to code shape |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns added tests/manifest |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine build commits frontend-only |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path violations observed |

**Sweep count:** 65 active statutes scored in-session (C1–C3 satisfied).  
**Straggler (C4):** Joan `[plan-rubric]` APPROVED with no Excluded list — no stragglers.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan has no “Patterns to reuse” section |

**Uncited shape notes (advisory):** `btn secondary` on diagnostic Copy aligns with `pattern.ui.shared-button-roles`; thin lib helper + modal wiring aligns with existing UI composition — no catalog citation required.

## Plan adherence

**Stages 1–3 (1421 build commits):**

| Stage | Plan | Actual |
|-------|------|--------|
| 1 | `copyJobSnapshotToClipboard` — GET `/copy`, pretty-print, clipboard, boolean, silent failures | Matches plan snippet byte-for-byte (+ file comment) |
| 2 | Info-tab Copy above Skip; `entity-summary-actions` CSS; 2000ms Copied; Skip byte-for-byte | ✓ Skip wrapper/labels/handlers unchanged; Copy uses `btn secondary`, `disabled={copying}`, labels `Copy`/`Copied` |
| 3 | Header Copy always available; guard widened; separate from `copyFeedback`; JobAnalysisReportModal handler | ✓ snapshot props wired; email/linkedin handlers and feedback span untouched |

**Do-not-touch respected (1421 commits):** no backend, Modal.tsx, list pages, toasts, detail GET changes.

**Estimate (2):** matches confirmed footprint.

**Cross-ticket (AST-1420):** consumes existing copy route; does not reimplement assembler. Branch tip stacks full AST-1420 payload (already PROCEED) — expected pre–ftr rollup, not 1421 scope violation.

## Frame diff

| Frame | Notes |
|-------|-------|
| Planned 1421 product | 5 frontend files only — matches engineer commits |
| vs `origin/dev` three-dot | Also includes stacked AST-1420 backend + tests + Radia-reviewed payload — epic branch composition, not 1421 smuggling |
| Issue doc build SHA | Doc cites `94207bdd`; tip is `cbd2837f` (Betty tests + merge-tests) — Chuckles housekeeping when appending |

## Findings

No **fix-now** items.

### advisory — issue doc build SHA stale

**Location:** `docs/features/interface/ast-1421-job-modal-copy-control.md` → `## Review (build)`  
**Finding:** Build line references `94207bdd`; publish tip is `cbd2837f`.  
**Recommendation:** Chuckles doc refresh when appending — not a product fix.

### advisory — duplicate modal handlers (plan-mandated)

**Location:** `JobDetailModal.tsx`, `JobAnalysisReportModal.tsx` — identical `handleCopySnapshot` bodies  
**Finding:** Plan explicitly requires the same handler shape in both modals rather than a shared hook.  
**Recommendation:** Accept per plan-is-bible; optional future DRY is out of scope.

### advisory — Info-tab-only visibility (pre-accepted)

**Location:** Stage 2 placement  
**Finding:** Copy visible on Info tab only, not JD/Agent Story tabs — Joan discuss item already accepted.  
**Recommendation:** No resolve-child action unless UAT requests broader placement.

## What’s solid

- Helper contract is exact: encoded path, no query params, `JSON.stringify(body, null, 2)`, silent `false` on all failure modes.
- Recommended header shows Copy when email/LinkedIn absent (guard widened correctly).
- Snapshot Copied state is on the button label; gold `copyFeedback` span remains email/linkedin-only.
- Betty coverage: lib unit tests (OK/non-OK/json/clipboard reject), header isolation, modal Copy→Copied→Copy timing, silent failure, adjacent controls preserved.

## Notes

- §5a: no layer/import/logging violations on 1421 product files; silent `catch` is plan-approved resilience, not D2 swallow in runtime logging paths.
- §5f/§5g: not triggered by 1421 frontend diff (stacked 1420 backend already reviewed CLEAN).
- Stacked AST-1420 backend in branch diff: do not re-review as 1421 findings; already `[code-rubric] PROCEED` on AST-1420 @ `65884db6`.

## Frame diff

(none beyond table — 1421 product matches plan frame; extra diff paths are stacked sibling + Betty pipeline)

context_tokens≈95000
