# AST-1051 — UAT: Create button on Manage Email list rows (not modal)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1051/uat-create-button-on-manage-email-list-rows-not-modal  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate  

**Publish ref (origin):** `sub/AST-1044/AST-1051-uat-create-button-on-manage-email-list-rows`  
**Parent integration ref:** `ftr/AST-1044-bind-email-to-candidate`

Move Manage Email **Create** from the HTML-preview modal onto each **matched** inbox list row so the operator can create a meteorite job without fighting the body panel. Reuse the existing AST-1049 `POST …/create-job` path and match gating; do not change strip/extract, match rules, or backend contracts.

Boundaries (do **not** implement): From→candidate match rules; strip/extract semantics; meteorite create API / `create_meteorite_job_from_inbox_message`; enabling Create on unmatched rows; z-index-only modal patches; removing HTML preview; Gmail / mailbox mutation.

**Depends on:** AST-1048 + AST-1049 already on `origin/ftr/AST-1044-bind-email-to-candidate` (merge that tip before build — `candidate_match` list payloads + create-job POST exist).

---

## UAT fitness

- **AC restored:** Parent AC 3 — “On Manage Email, a matched message exposes an active **Create** control; an unmatched or ambiguous message does not.” Parent AC 4 — “Pressing **Create** on a matched message strip/extracts the message content (including the **subject** in the content), creates a meteorite job for that candidate via the AST-1034 create capability with that result as the JD HTML, and the operator can observe success (or a clear failure) without leaving the pane flow.”
- **Correct outcome:** Each matched list row shows an active **Create** button; pressing it runs strip/extract + meteorite create for that message id; unmatched rows have no Create control; Create is not required inside the HTML preview modal.
- **Sibling check:** AST-1048 match chrome (`candidate_match` column + modal match line) stays; AST-1049 create-job endpoint and toast success/failure contract stay — only the UI affordance location moves. Verified by reading current `AdminManageEmail.tsx` + `POST /api/admin/inbox/messages/<id>/create-job` on ftr tip.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Pure z-index/CSS so Create stays only in the modal; removing HTML preview; enabling Create on unmatched rows; changing match/create backend contracts.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Per-row Create on matched list items; remove Create from modal; reuse create-job POST; stopPropagation so Create does not open the modal | ui |
| `src/ui/frontend/src/App.css` | Adjust Manage Email Create styles for list-row placement (drop modal-only action footer if unused) | ui |

No backend, config, core, or API changes.

---

## Stage 1: List-row Create + remove modal Create

**Done when:** On Manage Email, every list row with `candidate_match.matched === true` and a non-empty `astral_candidate_id` shows an enabled **Create** button in an **Actions** column; unmatched/ambiguous/missing-match rows show an empty Actions cell (no Create); clicking Create POSTs the existing create-job route for that row’s `id` and shows the same success/error toast as today; Create disables while that request is in flight; clicking Create does **not** open the message modal; the modal still shows match + HTML body but has **no** Create button.

1. In `src/ui/frontend/src/pages/AdminManageEmail.tsx`, update the React import to include `type MouseEvent`. Replace the boolean `createBusy` state with `createBusyId: string | null` (null = idle).

2. Replace `onCreateClick` (selected-message only) with a row-scoped handler:

```ts
async function onCreateClick(row: InboxMessage, e: MouseEvent) {
  e.stopPropagation()
  const matched =
    row.candidate_match?.matched === true &&
    Boolean((row.candidate_match.astral_candidate_id || "").trim())
  if (!matched || createBusyId !== null) return
  setCreateBusyId(row.id)
  setToast(null)
  try {
    const r = await api(
      `/api/admin/inbox/messages/${encodeURIComponent(row.id)}/create-job`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      },
    )
    const data = await r.json().catch(() => ({} as Record<string, unknown>))
    if (!r.ok) {
      const msg =
        (typeof data.error === "string" && data.error) || `HTTP ${r.status}`
      setToast({ text: msg, variant: "error" })
      return
    }
    const jobId =
      typeof data.astral_job_id === "string" ? data.astral_job_id : ""
    setToast({
      text: jobId ? `Created job ${jobId}` : "Created job",
      variant: "success",
    })
  } catch (err) {
    setToast({
      text: err instanceof Error ? err.message : "Create failed",
      variant: "error",
    })
  } finally {
    setCreateBusyId(null)
  }
}
```

Keep the request shape identical to the current AST-1049 wire (same path, method, empty JSON body, toast copy).

3. Add an **Actions** column to the list table (header after **Status** is fine):

- In `<thead>`, add `<th>Actions</th>`.
- In each data `<tr>`, after the Status `<td>`, add:

```tsx
<td onClick={e => e.stopPropagation()}>
  {row.candidate_match?.matched === true &&
  (row.candidate_match.astral_candidate_id || "").trim() ? (
    <button
      type="button"
      className="manage-email-create"
      disabled={createBusyId !== null}
      onClick={e => onCreateClick(row, e)}
    >
      Create
    </button>
  ) : null}
</td>
```

- Update the empty-state `colSpan` from `5` to `6`.

⚠️ **Decision — omit Create on unmatched (not disabled):** Bug Diagnosis: “unmatched rows still have no Create.” An empty Actions cell is clearer than a permanently disabled button and matches “does not” expose Create.

⚠️ **Decision — disable all Create buttons while any create is in flight:** Single `createBusyId` prevents double-submit across rows without inventing a queue.

4. Remove Create from the modal:

- Delete the entire `<div className="manage-email-actions">…</div>` block (and the modal Create button).
- Keep the modal match line (`Matched: {selectedMatchId}`) and HTML body / loading / error behavior unchanged.
- Remove now-unused `selectedMatched` if it is only used for Create (keep `selectedMatchId` for the match line).

5. In `src/ui/frontend/src/App.css`:

- Keep `.manage-email-create` / `:disabled` styles.
- Remove `.manage-email-actions` if nothing else uses it (modal footer padding/border no longer needed).
- Optionally add a small list-row rule if the button needs tighter padding in the Actions cell (e.g. `.list-page-table .manage-email-create { … }`) — only if the existing button looks oversized in the table; do not invent a new design system.

⚠️ **Decision — remove modal Create entirely:** Ticket title and Expected require list-row Create and reject leaving Create only in the modal. Dual Create (row + modal) would leave the occluded control in place; remove it.

---

## Self-Assessment

**Scope:** `minor` — UI-only move of an existing Create control and CSS tweak in Manage Email; no API/core/config.

**Conf:** `high` — create-job endpoint and match gating already shipped; change is placement + stopPropagation on the known page.

**Risk:** `low` — worst case is Create still hard to click or row click racing Create; backend create path unchanged.

---

## Code-rules self-review

- §1.3 DRY — reuse existing create-job POST + toast; no second create path.
- §2.1 / §2.4 / §2.6 — N/A (no config/batch/state-machine changes).
- §3.3 imports — React mouse event only; no new layer imports.
- §3.5 naming — keep `manage-email-create` class and create-job route names.

---

## Review

**Publish ref:** `sub/AST-1044/AST-1051-uat-create-button-on-manage-email-list-rows`

**Product tip (pre-docs):** `026732cf` (`merge-tests(AST-1051)`; product `code(AST-1051)` @ `d5b42c84`)

**Overall:** CLEAN — no fix-now / discuss

**1051 product delta (`d5b42c84`):** Move Create onto matched list-row Actions; remove modal Create + `.manage-email-actions`; `createBusyId` + `stopPropagation`; reuse AST-1049 create-job POST/toast. CSS: drop unused modal footer rule.

### Notes
- No Joan plan-rubric verdict attachment on the ticket (C4 straggler check N/A).
- Three-dot vs `origin/dev` is 1051-only (siblings already on integration line).

### Statutes checked

| id | applies | verdict | note |
|---|---|---|---|
| astral.agent.confidence-bounds | no | n/a | layers miss |
| astral.agent.do-task-delegation | no | n/a | layers miss |
| astral.agent.grade-vector-validation | no | n/a | layers miss |
| astral.batch.batch-id-first | no | n/a | layers miss |
| astral.batch.batch-id-format | no | n/a | layers miss |
| astral.batch.claim-process-release | no | n/a | layers miss |
| astral.batch.entity-agent-responses-latest-only | no | n/a | layers miss |
| astral.config.config-source-of-truth | yes | conforms | No new config; UI affordance only |
| astral.config.pass-threshold-vs-score-floor | no | n/a | layers miss |
| astral.config.secrets-and-env-specific-from-environ | yes | conforms | No secrets |
| astral.debug.no-repo-root-artifacts-dir | no | n/a | paths miss |
| astral.debug.spikes-under-debug-dir | yes | conforms | Feature plan only |
| astral.docs.features-single-file-per-ticket | yes | conforms | One plan file |
| astral.git.betty-no-src-or-features | yes | conforms | Betty owns test/bible tip |
| astral.git.engineer-test-tree-ban | yes | conforms | Engineer commit is UI-only |
| astral.layers.core-vs-external-bright-line | no | n/a | layers miss |
| astral.layers.import-direction | yes | conforms | React/api only; no new layer imports |
| astral.layers.scripts-exempt-from-layer-rules | no | n/a | layers miss |
| astral.layers.ui-config-driven-business-logic | yes | conforms | Match gate still from server `candidate_match` |
| astral.patterns.coat-check-never-store-empty | no | n/a | layers miss |
| astral.patterns.render-verdict-orchestrates-consult | no | n/a | layers miss |
| astral.patterns.require-auth-on-protected-endpoints | yes | conforms | No new route; create-job unchanged |
| astral.standards.data-raises-caller-logs | yes | conforms | Untouched backend |
| astral.standards.database-header-inventory | no | n/a | layers miss |
| astral.standards.debug-contract-gated | yes | conforms | No new debug paths |
| astral.standards.dry-and-focused-functions | yes | conforms | Reuses create-job POST/toast |
| astral.standards.in-scope-only | yes | conforms | Affordance move only |
| astral.standards.logging-via-utils | yes | conforms | No new logging |
| astral.standards.no-cross-contamination | yes | conforms | UI only |
| astral.standards.no-hardcoded-sets | yes | conforms | No new sets |
| astral.standards.public-then-helpers | yes | conforms | N/A shape; page handlers clear |
| astral.standards.utils-data-late-import-only | no | n/a | layers miss |
| astral.state.core-decides-transitions | no | n/a | layers miss |
| astral.state.job-prior-states-enforced | no | n/a | layers miss |
| astral.state.no-daisy-chain-in-run | no | n/a | layers miss |
| astral.ui.frontend-file-placement | yes | conforms | Existing AdminManageEmail page |
| astral.ui.naming-conventions | yes | conforms | keep manage-email-create / create-job |
| astral.ui.single-gunicorn-worker | yes | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | yes | conforms | One merge-tests tip |
| orch.git.commit-vocabulary | yes | conforms | code/test/docs/merge-tests |
| orch.git.flow-direction-inviolable | yes | conforms | sub under ftr |
| orch.git.ftr-sub-topology | yes | conforms | `sub/AST-1044/AST-1051-…` |
| orch.git.merge-on-checkout | yes | conforms | Review merged ftr + publish tip |
| orch.git.no-cherry-pick-rebase-force | yes | conforms | No forbidden ops |
| orch.git.no-dev-agent-branches | yes | conforms | On sub/* |
| orch.git.one-epic-worktree-per-parent | yes | conforms | astral-AST-1044 |
| orch.git.three-permanent-branches | yes | conforms | Untouched |
| orch.pipeline.call-susan-for-product-decisions | yes | conforms | UAT expected outcome followed |
| orch.pipeline.plan-is-bible | yes | conforms | `d5b42c84` matches Stage 1 |
| orch.pipeline.project-scoped-queues | yes | conforms | Meteorite |
| orch.pipeline.status-gates-skill-entry | yes | conforms | Tests Passed → review |
| orch.roles.archie-approves-statutes | yes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | yes | conforms | Betty owned test commit |
| orch.roles.chuckles-never-ticket-assignee | yes | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | yes | conforms | Assignee left Hedy |
| orch.roles.pre-commit-path-bans | yes | conforms | No banned paths in product commit |

**Active statutes:** 56 · **Applicable (yes):** 38 · **n/a:** 18 · **fix-now:** 0 · **discuss:** 0

— Radia
