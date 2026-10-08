# AST-2031 — Job run modal requests entity-scoped agent data

- **Parent:** [AST-2028 — Technical fail modals must filter by entity_id](https://linear.app/astralcareermatch/issue/AST-2028)
- **Ticket:** [AST-2031](https://linear.app/astralcareermatch/issue/AST-2031)
- **Publish ref:** `sub/AST-2028/AST-2031-job-run-modal-entity-scoped` (origin only)
- **Depends on:** AST-2030 (#2 — `GET /api/agent_data/<batch_id>?entity_id=` slices NO_CACHE / TASK / RESPONSE). This ticket only makes the job modal *ask* for the slice; it works against today's backend too (the endpoint already accepts `entity_id`).

When an admin opens a run from a job's State History (Job Detail modal, on Processing / Skipped pages), the run's agent-data panes currently fetch the whole batch. This ticket threads the open job's `astral_job_id` from `JobDetailModal` → `BatchExecutionModal` → `BatchAgentDataPanes`, which appends `?entity_id=<id>` to the `/api/agent_data/…` fetch only. Every other caller of `BatchAgentDataPanes` (Execution History, Vector Feedback, Ad Hoc, the standalone `BatchAgentDataModal`) passes no id and keeps fetching the full batch. Canon Scope: none (frontend prop plumbing only).

## Scope check

Ticket `## Scope` names exactly three files; every row below is one of them, and each change is the kind it describes. No backend, no test, no bible edits (tests/bible are Betty's).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | `BatchAgentDataPanes` gains optional `entityId` prop → `entity_id` query on the `/api/agent_data/…` fetch only | ui (frontend) |
| `src/ui/frontend/src/components/BatchExecutionModal.tsx` | Optional `entityId` prop, forwarded to `BatchAgentDataPanes` | ui (frontend) |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Passes `job?.astral_job_id` as `entityId` into `BatchExecutionModal` | ui (frontend) |

Not touched (must stay byte-identical): `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, `AdminVectorFeedback.tsx`, `AdminAnthropicAdHoc.tsx`, `JobAnalysisReportModal.tsx`, `JobDiscussionPane.tsx`, `AgentStoryTab.tsx`, everything under `src/ui/api/` and `src/data/`.

## Stage 1: Entity-scoped agent-data fetch from the job run modal

**Done when:** opening a run from a job's State History fetches `/api/agent_data/<runId>?entity_id=<astral_job_id>`; every other `BatchAgentDataPanes` caller still fetches `/api/agent_data/<batchId>` with no query string; `npm run lint` and `npx tsc -b` pass.

1. In `src/ui/frontend/src/components/BatchAgentDataModal.tsx`, add to `interface PanesProps` (after `candidateId?: string`):

   ```ts
   /** When set, agent data is requested sliced to this entity (`entity_id` query); timesheets / ledger stay batch-wide. */
   entityId?: string
   ```

   Do **not** add `entityId` to the modal-level `interface Props` or to the default-export `BatchAgentDataModal` — its callers are batch-wide.

2. Same file, change the `BatchAgentDataPanes` signature to destructure the new prop:

   ```ts
   export function BatchAgentDataPanes({ batchId, candidateId, entityId, className }: PanesProps) {
   ```

3. Same file, in the first `useEffect`, replace only the agent-data fetch line

   ```ts
   api(`/api/agent_data/${encodeURIComponent(batchId)}`).then(r => r.json()),
   ```

   with

   ```ts
   // Entity-scoped only when a caller names the entity; batch-wide views pass none
   api(`/api/agent_data/${encodeURIComponent(batchId)}${entityId ? `?entity_id=${encodeURIComponent(entityId)}` : ""}`).then(r => r.json()),
   ```

   Leave the `/api/admin/timesheets?batch_id=…` and `/api/admin/dispatch_ledger/…` fetches unchanged (Tokens & Cost stays batch-wide — parent Functional scope 7).

4. Same file, change that effect's dependency array from `[batchId, candidateId]` to `[batchId, candidateId, entityId]`.

   ⚠️ **Decision:** Empty-string `entityId` is treated as "no id" (truthiness check) so a blank id never produces `?entity_id=` — the backend would read that as a real (empty) filter.

5. In `src/ui/frontend/src/components/BatchExecutionModal.tsx`, add to `interface Props` (after `runId: string | null`):

   ```ts
   /** Entity whose slice of the run's agent data to show (job modal passes the open job). Omitted → whole batch. */
   entityId?: string
   ```

6. Same file, change the signature to `export default function BatchExecutionModal({ runId, entityId, onClose }: Props) {` and the panes line to:

   ```tsx
   <BatchAgentDataPanes batchId={runId} entityId={entityId} />
   ```

   The `/api/admin/dispatch_ledger/…/logs` fetch is unchanged.

7. In `src/ui/frontend/src/components/JobDetailModal.tsx`, change the sibling modal line (currently line 260) to:

   ```tsx
   <BatchExecutionModal runId={selectedRunId} entityId={job?.astral_job_id} onClose={() => setSelectedRunId(null)} />
   ```

   Keep the existing `{/* Sibling, not child: … */}` comment above it.

   ⚠️ **Decision:** `job?.astral_job_id` rather than the `jobId` prop. The ticket names `job.astral_job_id`, and a run can only be selected from `InfoTab`, which renders only once `job` is loaded — so the value is always present when the modal opens. `job` is `null` only while no run is selectable, in which case `undefined` is harmless.

8. Verify (from `src/ui/frontend/`):
   - `npm ci` (no `node_modules` in the epic worktree today).
   - `npm run lint` — zero errors.
   - `npx tsc -b` — zero errors.
   - `npm run test:component -- test_JobDetailModal test_BatchAgentDataModal test_AdminPerformanceMonitor` — existing tests stay green (Betty adds the AC 8 assertion at qa-child; do not edit `tests/`).
   - From repo root: `git diff origin/dev -- src/ui/frontend/src/pages/ src/ui/api/ src/data/` is empty.

9. Commit only the three files: `code(AST-2031): job run modal requests entity-scoped agent data`, then `git push origin HEAD:sub/AST-2028/AST-2031-job-run-modal-entity-scoped`.

## AC mapping

- **AC 8** (job modal sends the id): steps 3, 6, 7 — clicking State History row for job `J`, run `R` fetches `/api/agent_data/R?entity_id=J`. Test is Betty's (`test_JobDetailModal.test.tsx`).
- **AC 9** (batch-wide callers unchanged): no page file is touched; `AdminPerformanceMonitor` passes no `entityId`, so its fetch URL and `test_AdminPerformanceMonitor.test.tsx` are unchanged.

⚠️ **AC 9 grep defect (pre-existing, not introduced here):** `grep -n "entity_id" src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` already returns 8 lines on `origin/dev` (the Ad Hoc workbench's own run payload / table fields, unrelated to agent-data fetches). `AdminPerformanceMonitor.tsx` and `AdminVectorFeedback.tsx` return nothing. This plan does not touch `AdminAnthropicAdHoc.tsx`; the AC's intent (Ad Hoc's `BatchAgentDataPanes` call at line ~653 passes no entity id) holds. Flagged on Linear so the grep check can be narrowed (e.g. `git diff origin/dev -- <three pages>` empty) before review.

## Execution contract

Execute steps in order. No files beyond the three above. If a referenced line, prop, or fetch differs from what's quoted here, stop and comment on AST-2028 using the `🛑 Stage 1 blocked:` format.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2031
**Overall:** APPROVED
**Corpus:** 8fa9f84d0e775852bc529f67faadf7e6f12cd904 (canon/ tree at publish tip)
**Publish ref:** ff397285d

## Canon scores
(none — ticket and plan declare Canon Scope empty; frontend prop plumbing only)

## Traceability
8→Stage 1 steps 3, 6, 7 (`entityId` on `/api/agent_data/…` only; Betty owns `test_JobDetailModal` assertion); 9→Stage 1 step 8 (`git diff origin/dev -- src/ui/frontend/src/pages/ …` empty) + no edits to the three admin pages; batch-wide callers use `BatchAgentDataModal` / `BatchAgentDataPanes` without `entityId`.

## Findings
- **discuss** | Parent AC 9 / Katherine comment | Literal `grep -n "entity_id" …AdminAnthropicAdHoc.tsx` already matches 8 lines on `origin/dev` (workbench payload/table fields, not agent-data URL). Plan correctly does not touch that page and uses **page diff** in Stage 1 §8 instead of grep. Intent holds; parent AC 9 wording should be narrowed at definition level (e.g. diff-empty on those pages, or grep scoped to `BatchAgentDataPanes` / agent_data fetch) so UAT/review does not re-litigate a pre-existing false negative.
- **acceptable** | AC mapping § | Plan documents the grep defect and mirrors Katherine’s Linear finding — aligned with implementation path.

context_tokens≈32000

## Review

- **Branch:** `origin/sub/AST-2028/AST-2031-job-run-modal-entity-scoped`
- **Build tip:** `26e02c09e` (Stage 1: `entityId` prop on `BatchAgentDataPanes` → `entity_id` query on the agent-data fetch only; forwarded through `BatchExecutionModal`; `JobDetailModal` passes `job?.astral_job_id`. 3 files, 11 insertions, 6 deletions)
- **Build notes:** Built as planned, steps 1–9 in order, no code deviations. Built on top of `origin/ftr/AST-2028-technical-fail-modals-filter-by-entity-id` (siblings AST-2029 / AST-2030 merged by sync). `npm ci` run in `src/ui/frontend`. `npx tsc -b --noEmit` passes. Step 8's "`npm run lint` — zero errors" can't be met literally: repo-wide lint reports the same 31 pre-existing problems (26 errors, 5 warnings) with and without this change, none in the three touched files. `git diff origin/dev -- src/ui/frontend/src/pages/ src/ui/api/ src/data/` is empty.
- **For qa-child:** in `test_JobDetailModal.test.tsx`, two tests in the AST-1865 describe now fail as expected, because they assert the exact unscoped URL and the job modal now sends `?entity_id=j1` (AC 8): `AC4` (`/api/agent_data/hop-R`) and `AC6` (`/api/agent_data/legacy-B`). One more, `AST-1695 … null listing_href → no Link <a>`, already fails on the pre-change tree. `test_BatchAgentDataModal` and `test_AdminPerformanceMonitor` are green with no edits.

## Radia review

[code-rubric]
**Ticket:** AST-2031
**Publish ref:** caef65df488ee9ea735886bcdd56c223cc27a1c9
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Overall:** CLEAN

## Canon scores
(none — frozen Canon Scope empty; no directives to score)

## Column diff vs plan stage
no plan-stage canon scores attached (Joan likewise scored no canon rows)

## Frame diff
- [ ] **Acceptance criteria (parent AST-2028):** Replace AC9 literal `grep -n "entity_id"` over three admin pages with a check that matches intent (e.g. `git diff origin/dev -- <pages>` empty and no `entityId={` on `BatchAgentDataPanes` in those pages), since `AdminAnthropicAdHoc.tsx` already contains unrelated `entity_id` strings on `origin/dev`.

## Findings

### fix-now
(none)

### discuss
(none)

### advisory
- **advisory** | sibling product + test carry | Three-dot diff vs `origin/dev` still includes AST-2029 / AST-2030 backend (`src/core/agent.py`, `src/utils/formatting.py`, `test_agent_ast2029.py`, `test_agent_ast2030.py`, sibling plan docs). Expected on stacked epic publish ref (`blockedBy` AST-2030). AST-2031-owned UI delta is three components plus frontend tests/bible rows.
- **advisory** | Parent AC9 wording | Plan and bible document the pre-existing `grep entity_id` false positive on `AdminAnthropicAdHoc.tsx`; implementation correctly uses page diff + panes prop wiring instead. UAT should not treat literal grep as the gate.
- **advisory** | `BatchAgentDataModal.tsx` | Default-export modal still renders `<BatchAgentDataPanes … />` without `entityId` (Execution History / Vector Feedback / standalone modal stay batch-wide). Ad Hoc (`AdminAnthropicAdHoc.tsx` ~653) passes no `entityId`.
- **advisory** | Build hygiene | Issue doc build tip `26e02c09e` differs from current publish tip `caef65df` (likely doc lag); review used `origin/sub/AST-2028/AST-2031-job-run-modal-entity-scoped`.

## What's solid
- Plan Stage 1 steps 1–7 implemented exactly: optional `entityId` on `PanesProps` / `BatchExecutionModal` only; agent-data URL appends `?entity_id=${encodeURIComponent(entityId)}` when truthy; timesheets and dispatch ledger URLs unchanged; effect deps include `entityId`.
- `JobDetailModal` forwards `job?.astral_job_id` into `BatchExecutionModal` (AC8).
- AC9 intent: `git diff origin/dev...publish-ref -- src/ui/frontend/src/pages/ src/ui/api/ src/data/` is empty; no `entityId={` on panes from admin pages.
- Tests: `test_JobDetailModal` AC4/AC6 assert scoped URL and reject unscoped; `test_BatchAgentDataModal` covers encode, batch-wide default, refetch on `entityId` change; `test_AdminPerformanceMonitor` untouched per manifest.

## Recommended actions (downstream only — not executed in this session)
- Chuckles: append artifact, `docs(AST-2031): Radia review — clean`, post slim upshot `--as radia`, **Review Posted**.
- Archie / parent AST-2028: tick or amend Frame diff AC9 row so UAT does not re-litigate grep.
- Epic merge: land #1–#2 before or with #3 so `entity_id` query returns sliced rows in production.

context_tokens≈18000
