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

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1334
**Overall:** APPROVED
**Publish ref:** `sub/AST-1329/AST-1334-remove-recommended-job-report-modal-footer` @ `5b69fa2fedd67e2aa0a1acf21cb0345d126018ff`

### Traceability

AC1–AC4 → Stage 1 (`showFooter` opt-out on `Modal.tsx`; `showFooter={false}` on `JobAnalysisReportModal.tsx`; header × / `guardedClose` and Artifacts `cancel_build` strip unchanged).

### Findings

**acceptable** — `Modal.tsx` / `JobAnalysisReportModal.tsx` — Plan correctly rejects auto-hiding the footer when `onSave` is absent; read-only consumers (`RubricModal`, `MaterialsPreviewModal`, `BatchAgentDataModal`) still need footer Cancel beside ×.

**acceptable** — Stage 1 — Betty test coverage (`test_Modal.test.tsx`, `test_JobAnalysisReportModal.test.tsx`) deferred to qa-child per engineer test-tree ban; plan names the gap explicitly.

No `fix-now` or `discuss` findings.

context_tokens≈42000

## Review (build)

**Built:** `origin/sub/AST-1329/AST-1334-remove-recommended-job-report-modal-footer` @ `fe131a0f6aac18f51214f7a0d984b132cc7d764e`

Stage 1: `Modal` `showFooter` opt-out (default true); `JobAnalysisReportModal` passes `showFooter={false}`. Header × and Artifacts Cancel unchanged. Tests deferred to Betty.

## Radia review

# Radia review — AST-1334

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1334
**Publish ref:** `sub/AST-1329/AST-1334-remove-recommended-job-report-modal-footer` @ `44fe3df2c76e822f069514f987f58bf32d3cb8c0`
**Overall:** CLEAN

**Diff baseline:** `origin/dev...origin/sub/AST-1329/AST-1334-remove-recommended-job-report-modal-footer` (6 commits: plan, Joan validate, product code, review stub, Betty `test(AST-1334)`, single `merge-tests(AST-1334)`)

**Change set:** `Modal.tsx` + `JobAnalysisReportModal.tsx` (ui); Betty-owned `tests/**` + `docs/test-bible/frontend/components.md`; issue doc.

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent/LLM paths in diff |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` / delegation changes |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grade-vector paths |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch/dispatcher changes |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/process/release helpers |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity-agent-response paths |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config module changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env wiring |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifact dirs |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed paths |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run-next / chain changes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | one new `docs/features/interface/ast-1334-*.md` for this ticket |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty commits touch tests/bible only (allowed) |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | product commit `fe131a0f` is test-tree-free; test paths arrived via Betty `09363cc3` + single `merge-tests` |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | ui-only diff |
| `astral.layers.import-direction` | scoped | conforms | no new cross-layer imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no `scripts/` changes |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no new hardcoded job/state strings; presentation prop only |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no render/verdict paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API/auth handlers |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no boot/seed hot path |
| `astral.seed.define-approved` | scoped | not-applicable | no define/seed flow |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator-row seed |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no data layer |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/migrations |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no backend `debug=` surfaces |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | minimal conditional wrapper; no refactor creep |
| `astral.standards.in-scope-only` | scoped | conforms | touches only planned Modal + JAR call site (+ Betty test merge) |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no logging added |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `showFooter` is semantic, not ticket-id naming |
| `astral.standards.no-cross-contamination` | scoped | conforms | no unrelated module edits |
| `astral.standards.no-hardcoded-sets` | scoped | not-applicable | no new hardcoded sets |
| `astral.standards.public-then-helpers` | scoped | conforms | prop on exported `ModalProps`; no helper reorder noise |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils/data imports |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job-state enforcement logic |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run/daisy-chain paths |
| `astral.ui.frontend-file-placement` | scoped | conforms | edits stay in flat `components/` |
| `astral.ui.naming-conventions` | scoped | conforms | `showFooter` camelCase boolean prop on interface |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server/worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | exactly one `merge-tests(AST-1334): origin/tests 09363cc3` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `merge-tests` / `docs` prefixes used correctly |
| `orch.git.flow-direction-inviolable` | universal | conforms | child on `sub/AST-1329/...`; tests via `origin/tests` merge |
| `orch.git.ftr-sub-topology` | universal | conforms | correct `sub/<parent>/<slug>` publish ref |
| `orch.git.merge-on-checkout` | universal | conforms | no rebase/cherry-pick signals in history |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear merge-tests only |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent-named publish branches |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1329 epic worktree pattern respected |
| `orch.git.three-permanent-branches` | universal | conforms | sub + tests merge; no fourth permanent branch |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | plan decision (explicit opt-out vs auto-hide) already documented |
| `orch.pipeline.plan-is-bible` | universal | conforms | implementation matches Stage 1 verbatim |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a to code; pipeline placement correct |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed as required |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a to diff content |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test + bible edits on Betty SHA, merged once |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Katherine (engineer) |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | engineer still assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no hook-evasion patterns observed |

**Sweep count:** 64 active statutes scored (per `canon/statutes/README.md` harvested corpus).

**Straggler (C4):** Joan plan-rubric APPROVED attached; no Excluded-statute list — no straggler callout.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.icon-control` | conforms | Header × still `className="icon-control"` with `title`/`aria-label="Close"`; diff does not restyle dismiss |

**none cited** beyond the above (issue doc references icon-control for dismiss; no other catalog ids in plan).

---

## Plan adherence

Stage 1 delivered exactly as specified:

- `ModalProps.showFooter?: boolean` with JSDoc, default `true`, conditional `.modal-footer` render.
- `JobAnalysisReportModal` passes `showFooter={false}` only on the report shell.
- `guardedClose`, dirty handling, header ×, overlay/card/body, and Artifacts `cancel_build` strip untouched in product diff.
- Correct rejection of auto-hiding footer when `onSave` is absent (read-only modals keep footer Cancel).
- Estimate **1** matches footprint.
- Betty test gap from plan is closed: `test_Modal.test.tsx` AST-1334 case + `test_JobAnalysisReportModal.test.tsx` footer opt-out describe block; bible section added; single `merge-tests` SHA.

**C6 lenses (§5a–§5g):** No import/layer/logging/debug/external/batch concerns on this ui-only presentation change.

---

## Findings

*(none)*

---

## What's solid

- Opt-in `showFooter` preserves every other `Modal` consumer (grep confirms no other call-site changes).
- Tests assert the right negatives: no `.modal-footer`, no stray footer Cancel on Summary, header Close still fires `onClose`, and BUILD_ARTIFACTS keeps exactly one Cancel in the Artifacts strip.
- Pipeline hygiene: engineer product commit test-free; Betty delivers one tests SHA merged once.

---

## Frame diff

(none) — implementation matches the approved plan frame; no architectural drift.

---

## Notes

- Joan verdict present; no plan exclusions to reconcile.
- Downstream: Chuckles may advance to **Review Posted** → **User Testing** (PROCEED path).

context_tokens≈28000

---
