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

## Bug: AST-2075 — Skipped job's run panels show only the RESPONSE tab

The backend Each-mode read (`get_agent_data` with `entity_id`) is unchanged. See `docs/features/agent/ast-2030-slice-agent-data-reads-and-agent-story-by-entity.md` § Bug: AST-2052. This fix lives in the modal panes (`BatchAgentDataPanes`) that this ticket wired.

### As-is

On staging, a run opened from a **Skipped** job's State History (`JobDetailModal` → `BatchExecutionModal` → `BatchAgentDataPanes` with `entityId`) shows only the RESPONSE tab. SYSTEM, CACHE, NO_CACHE and TASK do not appear at all.

### To-be

When `entityId` is set, the panes always read like one Each-mode call:
- **Always-present tabs:** SYSTEM, NO_CACHE, TASK and RESPONSE always get a tab.
- **CACHE_A–D:** each shows when it has a row. When the call's prompt rows are missing altogether, a single **CACHE** tab stands in for them.
- **Missing rows:** any of those tabs with no `agent_data` row shows `No agent_data found for this part of the call — it has aged out or was never stored.` instead of disappearing (Susan's To-be: "indicate as much in the various tabs that are missing the content").
- **Batch-wide views** (no `entityId`: Execution History, Vector Feedback, Ad Hoc) are unchanged.

### Repro

`BatchAgentDataPanes batchId="R" entityId="J"`, with `/api/agent_data/R?entity_id=J` returning one row only:

```json
[{"agent_data_id": "R-response-x", "block_type": "RESPONSE", "block_data": "Provider failed: …", "token_size": 1, "task_key": "consult_do", "created_at": "2026-10-08 12:00:00"}]
```

| | Tabs today | Tabs expected |
|---|---|---|
| Entity view | `RESPONSE` | `SYSTEM`, `CACHE`, `NO_CACHE`, `TASK`, `RESPONSE` |
| SYSTEM tab text | (no tab) | `No agent_data found for this part of the call — it has aged out or was never stored.` |

### Root cause

There are two parts.

1. **The prompt rows are not in the run's `batch_id`.** I found no `agent_data` retention or pruning anywhere:
   - `rg -i "delete from agent_data|prune|retention|purge"` over `src/` and `scripts/` turns up no `agent_data` delete.
   - `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` explicitly leaves `agent_data` untouched.

   So nothing in code ages prompt rows out ahead of RESPONSE rows. The one in-code path that produces a RESPONSE row with no prompt rows is in `do_task` (`src/core/agent.py`):
   - `asyncio.to_thread(_store_prompt_blocks, …)` runs inside `try / except Exception as exc: _log_swallowed_agent_data(index, task_key, exc)`. A failed prompt write logs `Continuing without that agent_data row` and goes on.
   - The RESPONSE (failure or success) is written afterwards by a separate `_store_response_block` call.

   Failed calls are what put jobs on Skipped. Staging data to confirm which call failed is not available (Susan, 2026-10-09). The storage-side cause is therefore **not** fixed here.
2. **The panes hide what's missing.** `BatchAgentDataPanes` builds its tabs only from the row types it receives (`byType` → `orderedTypes`). So every type with no row simply vanishes, and nothing tells the admin that content is missing.

### Proposed change

All in `src/ui/frontend/src/components/BatchAgentDataModal.tsx`. No backend, API or schema change.

1. Below `BLOCK_TYPE_ORDER`, add:
   ```ts
   // AST-2075: entity-scoped run always shows one Each-mode call's tabs; CACHE stands in for CACHE_A–D when the prompt rows are gone
   const ENTITY_CALL_TYPES = ["SYSTEM", "CACHE", "NO_CACHE", "TASK", "RESPONSE"]
   const TAB_ORDER = [...BLOCK_TYPE_ORDER.slice(0, 5), "CACHE", ...BLOCK_TYPE_ORDER.slice(5)]
   const MISSING_AGENT_DATA = "No agent_data found for this part of the call — it has aged out or was never stored."
   ```
2. In the fetch effect, replace `setActiveType(present[0] ?? b[0]?.block_type ?? "")` with
   `setActiveType(entityId ? "SYSTEM" : (present[0] ?? b[0]?.block_type ?? ""))`. In entity mode SYSTEM is always a tab, either real or a placeholder.
3. Replace the `orderedTypes` declaration (`const orderedTypes = [ ...BLOCK_TYPE_ORDER.filter(t => byType[t]), ...Object.keys(byType).filter(t => !BLOCK_TYPE_ORDER.includes(t)), ]`) with:
   ```ts
   // CACHE placeholder only when SYSTEM is gone too — present SYSTEM + no CACHE_* means the caches were empty (AST-2052 skips those)
   const missingTypes = entityId
     ? ENTITY_CALL_TYPES.filter(t => t === "CACHE"
         ? !byType.SYSTEM && !Object.keys(byType).some(k => k.startsWith("CACHE_"))
         : !byType[t])
     : []
   const tabTypes = [...Object.keys(byType), ...missingTypes]
   const orderedTypes = [
     ...TAB_ORDER.filter(t => tabTypes.includes(t)),
     ...tabTypes.filter(t => !TAB_ORDER.includes(t)),
   ]
   ```
4. In `tabBarTabs`, change `label: byType[t].length > 1 ? \`${t} ×${byType[t].length}\` : t` to
   `label: (byType[t]?.length ?? 0) > 1 ? \`${t} ×${byType[t].length}\` : t`.
5. In the `<textarea>` `value`, change
   `activeType && byType[activeType] ? blockContent(byType[activeType]) : ""` to
   `activeType && byType[activeType] ? blockContent(byType[activeType]) : missingTypes.includes(activeType) ? MISSING_AGENT_DATA : ""`.
6. Change the empty-state guard `{!loading && blocks.length === 0 && (` to `{!loading && orderedTypes.length === 0 && (`. In entity mode the placeholder tabs replace "No agent data blocks recorded for this batch." Without `entityId`, `orderedTypes` is empty exactly when `blocks` is empty, so the batch-wide behaviour stays the same.
7. `cd src/ui/frontend && npx tsc -b --noEmit` must be clean. `git diff origin/dev...HEAD -- src/core/ src/data/ src/ui/api/` must show no AST-2075 change.

⚠️ **Decision D1-2075 — which missing tabs get a placeholder.** SYSTEM, NO_CACHE, TASK and RESPONSE always do. In normal operation `do_task` always stores a non-empty system prompt, the job's live NO_CACHE, the user prompt and a response. CACHE_A–D get **one** `CACHE` placeholder, and only when SYSTEM is also missing. AST-2052 deliberately drops empty caches, so with SYSTEM present and no cache rows, "the caches were empty" is the only honest reading. Showing "aged out" there would be false.
⚠️ **Decision D2-2075 — the storage-side cause is out of scope.** Why the prompt write failed (logged by `_log_swallowed_agent_data`) can't be diagnosed without staging logs. This fix makes the gap visible rather than guessing at a storage change.
⚠️ **Decision D3-2075 — scope.** `BatchAgentDataModal.tsx` / `BatchAgentDataPanes` is in the parent's Component and Technical scope as a modified function. The placeholder tabs are a new display behaviour for the entity-scoped mode that this epic introduced. Susan requested them directly in the bug's To-be.

### Blast radius

- **`BatchAgentDataPanes` callers:** `BatchExecutionModal` (passes `entityId` only from `JobDetailModal`) gets the new tabs. `BatchAgentDataModal` (Execution History, Vector Feedback) and `AdminAnthropicAdHoc` pass no `entityId`: `missingTypes` is `[]`, so their tabs are byte-identical.
- **Tests:** `tests/component/frontend/components/test_BatchAgentDataModal.test.tsx` entity-id cases that assert the exact tab list or the `No agent data blocks recorded…` text when `entityId` is set. `test_JobDetailModal.test.tsx` if it asserts the run modal's tabs. `test_AdminPerformanceMonitor.test.tsx` must pass unchanged (parent AC9). Betty's call (`fix-board`).
- **Backend:** none. `get_agent_data` / AST-2052 Each-mode read is untouched.

### What must still hold

- **AST-2031:** the entity fetch still sends `?entity_id=`, and timesheets / ledger fetches stay batch-wide.
- **Parent AC9 / §7:** the batch-wide views (no `entityId`) show exactly the tabs and empty state they show today.
- **AST-2052:** a present SYSTEM with empty caches shows no CACHE tab. Real rows render exactly as before.
- **Parent AC10:** no change under `src/ui/api/` or `src/data/`.

## Joan fix-board (AST-2075)

[board-joan]  CANON: OK

The patch is frontend-only in `BatchAgentDataModal.tsx` (`ENTITY_CALL_TYPES`, placeholder copy when `entityId` is set, unchanged `?entity_id=` fetch). **patt.entity.batch-processing** is unaffected: `batch_id` / entity-scoped read semantics stay on the backend; this only changes how missing rows are shown in the job run modal, not claim, storage, or join keys. **stat.logging.debug** does not apply to new React UI behavior (backend statute; no new `logger.debug` in `src/core` or elsewhere). Susan’s To-be and D3-2075 explicitly own the placeholder tabs; that is product/display scope within the parent’s already-scoped `BatchAgentDataPanes` work, not a new pattern or statute carve-out. D2’s note that “aged out” may overstate swallowed prompt-storage failures is honest copy/scope for the engineer and Betty, not a canon amendment.

## Radia review-fix (AST-2075)

[code-rubric]
**Ticket:** AST-2075
**Publish ref:** 2e80369af80edf16418ef875afc48e123c964115
**Ftr base:** 29333729925ac857384f33e930875234c9a0a757 (ancestor of publish ref — confirmed)
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Overall:** CLEAN
**Parent shape:** Normal (not orphaned)

## Canon scores
patt.entity.batch-processing | A |
stat.logging.debug | X |

## Column diff vs plan stage
no plan-stage canon scores attached (Joan fix-board **CANON: OK**)

## Frame diff
(none)

## [bug-repro]
**OK** — `[bug-repro]` lives in `tests/component/frontend/components/test_BatchAgentDataModal.test.tsx` (`BatchAgentDataPanes — AST-2075 missing-row placeholder tabs`), landed on `dev` at `d8eb8c5bd` and **absent from the ftr…sub diff by design** (qa-fix repro-first on dev). Assertion pins plan § Repro: RESPONSE-only entity fetch → tabs `SYSTEM`, `CACHE`, `NO_CACHE`, `TASK`, `RESPONSE`; opens on SYSTEM with `MISSING_AGENT_DATA` copy; RESPONSE shows real body; TASK placeholder on click. Would fail pre-fix tab list (`RESPONSE` only).

## ## What must still hold
**OK**
- **AST-2031:** `?entity_id=` fetch and batch-wide timesheets/ledger URLs unchanged in diff (only tab/placeholder logic added).
- **Parent AC9 / §7:** `missingTypes` is `[]` without `entityId`; `orderedTypes` / empty-state guard preserve batch-wide behavior — covered by `test_batch-wide (no entityId) unchanged`.
- **AST-2052 / D1-2075:** CACHE placeholder only when SYSTEM missing and no `CACHE_*` rows — `test_present SYSTEM with no CACHE_* rows → no CACHE tab`.
- **Parent AC10:** no `src/ui/api/` or `src/data/` files in ftr…sub diff.

## Findings

### fix-now
(none)

### discuss
(none)

### advisory
- **advisory** | `[bug-repro]` location | Repro test not on bug publish ref; regression depends on `dev` (or merged ftr) carrying `d8eb8c5bd`. Manifest must keep running the AST-2075 describe block on fix-lane **test-fix**.
- **advisory** | `stat.logging.debug` | **X** — React-only change; statute Notes exclude React debug-contract duty; no new backend `logger.debug`.

## What's solid
- Isolated diff: `BatchAgentDataModal.tsx` + plan patch in `ast-2031` doc only (119 insertions / 6 deletions).
- Plan steps 1–6 implemented: `ENTITY_CALL_TYPES`, `TAB_ORDER`, `MISSING_AGENT_DATA`, entity default active tab `SYSTEM`, CACHE placeholder rule, safe `byType[t]?.` labels, placeholder textarea text, `orderedTypes.length === 0` empty state.
- Vitest describe adds D1 guards (real `CACHE_*`, all-empty entity run) beyond `[bug-repro]`.

## Chuckles branching (read-only)
**PROCEED** + normal parent → **Review Posted** → fix-lane clean-review shortcut → **User Testing** (`resolve-child` skipped).


[code-rubric] PROCEED (Commit: 2e80369af) entity placeholder tabs OK
