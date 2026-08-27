# AST-1506 — Show Differences and Update file on the divergence banner

**Linear (this ticket):** [AST-1506](https://linear.app/astralcareermatch/issue/AST-1506/show-differences-and-update-file-on-the-divergence-banner)  
**Parent:** [AST-1455](https://linear.app/astralcareermatch/issue/AST-1455/add-show-differences-and-update-file-with-table-version)  
**Publish ref:** `origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner`

Child #2 of AST-1455. Wires **Show Differences** and **Update file with table version** into the shared `RepoJsonDivergenceBanner` used by Manage Agents and Manage Tasks. Consumes Ada's sibling AST-1505 admin routes (`GET /api/admin/repo_json/compare/<table_key>`, `POST /api/admin/repo_json/write/<table_key>`). Rewrites warning copy so it no longer claims restart/deploy will overwrite the live table from the file. Does **not** change **Revert to file** confirm text or behavior.

## UAT fitness

- **AC restored:** Parent AC — *"On Manage Agents, when personas diverge from the personas JSON, **Show Differences** lists the actual row and field differences (added rows, removed rows, changed fields with file vs table values). It does not include task-prompt drift."* and *"After **Update file with table version** on Manage Agents, the agents warning clears, and the tasks warning is unchanged if tasks still diverge."* (symmetric for Manage Tasks / `agent_task`.)
- **Correct outcome:** Operator opens the divergence warning on the page they are on, inspects a readable diff for **that table only**, and can persist the live table to that table's repo JSON without leaving the page; banner clears for that table after a successful write; sibling-table warning unchanged.
- **Sibling check:** AST-1505 owns compare/write API + core helpers; this ticket only calls them from React. Existing `GET /status`, `POST /revert/<table_key>`, page `refreshToken` / `onReverted` wiring unchanged except write success also calls `fetchStatus()` and `onReverted?.()` like revert. Per-table isolation verified by sibling tests — UI must pass `tableKey` from props only, never hardcode both tables.
- **Not sufficient:** Rewriting banner copy without working Show/Update actions, or calling CLI export instead of `POST /write/<table_key>`.
- **Wrong fix rejected:** Fetching compare for both tables on one page, writing both JSON files from one button, or re-adding restart-overwrite messaging — all violate parent boundaries and AST-1505 per-table contract.

## Scope gate

All files and change kinds below are taken from this ticket's **## Scope** only. Out of scope: `src/core/**`, `src/ui/api/**`, `src/utils/config.py`, `src/data/**`, `data/admin/**`, `tests/**`, `docs/test-bible/**`, statute files, git commit/push from the product.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | Add **Show Differences** modal + **Update file with table version** confirm/write; rewrite warning copy; refetch status after successful write | ui |

**Out of scope (explicit):** `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`, `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` (already mount banner with `tableKey` / `refreshToken` / `onReverted` — no edits unless a compile error forces an import path fix, which should not happen), `src/ui/api/api_admin.py`, `src/core/repo_admin_json.py`, `tests/**`, `docs/test-bible/**`.

**Pre-flight (build-child):** After `sync-child.sh sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner --ftr AST-1455 --worktree …`, confirm sibling AST-1505 is reachable on the epic line: `grep -q 'repo_json/compare' src/ui/api/api_admin.py && grep -q 'get_repo_admin_json_table_comparison' src/ui/api/api_admin.py`. If either is missing, stop and comment on **AST-1506** — do not re-implement Ada's API in this ticket.

## Stage 1: Warning copy and Show Differences modal

**Done when:** When `status.diverged` is true, the banner shows rewritten copy (no restart/deploy overwrite claim), a secondary **Show Differences** button, and the existing **Revert to file** button unchanged. Clicking **Show Differences** opens `Modal` with three readable sections populated from `GET /api/admin/repo_json/compare/<tableKey>`. Manage Agents uses `tableKey="agent"`; Manage Tasks uses `tableKey="agent_task"` — each sees only its table's diff. `cd src/ui/frontend && npx tsc -b --noEmit` passes. No **Update file** button yet.

1. In `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx`, add:

   ```ts
   import Modal from "./Modal"
   ```

2. Add file-local types matching AST-1505 compare JSON (do not import from backend):

   ```ts
   type CompareFieldChange = {
     field: string
     file_value: unknown
     database_value: unknown
   }

   type CompareChangedRow = {
     row_key: string
     fields: CompareFieldChange[]
   }

   type ComparePayload = {
     table_key: string
     diverged: boolean
     repo_relative_path: string
     only_in_database: Record<string, unknown>[]
     only_in_file: Record<string, unknown>[]
     changed_rows: CompareChangedRow[]
   }
   ```

   Add row-key helper:

   ```ts
   const ROW_KEY_FIELD: Record<TableKey, string> = {
     agent: "agent_id",
     agent_task: "task_key",
   }

   function rowLabel(row: Record<string, unknown>, tableKey: TableKey): string {
     const col = ROW_KEY_FIELD[tableKey]
     const v = row[col]
     return typeof v === "string" && v ? v : String(v ?? "(missing key)")
   }

   function formatCellValue(value: unknown): string {
     if (value === null || value === undefined) return "—"
     if (typeof value === "string") return value
     return JSON.stringify(value)
   }
   ```

3. Add state next to existing `reverting` / `error`:

   ```ts
   const [diffOpen, setDiffOpen] = useState(false)
   const [diffLoading, setDiffLoading] = useState(false)
   const [diffError, setDiffError] = useState<string | null>(null)
   const [diffData, setDiffData] = useState<ComparePayload | null>(null)
   ```

4. Replace the warning `<span>` body (lines ~99–103) with copy that **does not** mention restart, deploy, or `export_repo_admin_json.py`. Use exactly:

   ```tsx
   Local <strong>{meta.label}</strong> in the database differ from <code>{path}</code>.
   {" "}Use <strong>Show Differences</strong> to inspect drift,{" "}
   <strong>Update file with table version</strong> to write the live table to the repo JSON file, or{" "}
   <strong>Revert to file</strong> to restore the database from the checked-in file.
   ```

5. Add `async function openDiff()`:
   - `setDiffOpen(true)`; `setDiffLoading(true)`; `setDiffError(null)`; `setDiffData(null)`
   - `const r = await api(\`/api/admin/repo_json/compare/${tableKey}\`)`
   - Parse JSON; if `!r.ok`, throw using `data.error` string when present
   - `setDiffData(data as ComparePayload)`; clear error
   - `catch` → `setDiffError(message)`; `finally` → `setDiffLoading(false)`

6. In the button row (`div` with **Revert to file**), insert **before** the revert button:

   ```tsx
   <button
     type="button"
     className="btn secondary"
     disabled={reverting}
     onClick={() => void openDiff()}
   >
     Show Differences
   </button>
   ```

   Keep **Revert to file** button markup and `handleRevert` **unchanged** (same confirm title, labels, variant `"danger"`, POST path).

7. Render diff modal at the bottom of the component (sibling to the warning `div`, still inside the fragment returned when diverged):

   ```tsx
   <Modal
     open={diffOpen}
     onClose={() => setDiffOpen(false)}
     title={`Differences — ${meta.label}`}
     showFooter={false}
     size="wide"
   >
   ```

   Body content:
   - If `diffLoading`: `<p style={{ fontSize: 13 }}>Loading comparison…</p>`
   - Else if `diffError`: error text in `var(--error, #f87171)`
   - Else if `diffData`:
     - **Rows only in database** — if `only_in_database.length === 0`, show `(none)`; else `<ul>` of `rowLabel(row, tableKey)` for each row
     - **Rows only in file** — same for `only_in_file`
     - **Changed fields** — if `changed_rows.length === 0`, show `(none)`; else for each `changed_rows` entry, a subsection titled `Row: {row_key}` with a `<table className="list-page-table">` (or plain `<table>` with `width: 100%`, `fontSize: 13`) columns **Field**, **File**, **Database**. Cell text from `formatCellValue`. For any cell where formatted length &gt; 120, wrap in `<pre style={{ maxHeight: "8em", overflow: "auto", margin: 0, whiteSpace: "pre-wrap" }}>` instead of bare text.
   - If modal opens with empty payload and not loading/error, show `(no differences reported)`

   ⚠️ **Decision:** Diff presentation stays in this file — no new component module; `Modal` + inline lists/tables match existing admin read-only patterns.

## Stage 2: Update file with table version and post-write refresh

**Done when:** Diverged banner shows primary **Update file with table version** between **Show Differences** and **Revert to file**. Confirm cancel leaves DB/file unchanged (no POST). Confirm OK calls `POST /api/admin/repo_json/write/<tableKey>`, then `fetchStatus()` and `onReverted?.()` on success — same refresh pattern as revert. Button shows `in-flight` class while the POST is in flight. Failed write surfaces inline error without clearing the warning. `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. Add `const [updating, setUpdating] = useState(false)` next to `reverting`.

2. Add `async function handleUpdateFile()`:
   - `const ok = await confirm(`Write the current live ${meta.label} to ${path}? This overwrites the checked-in repo JSON file on this host. Committing in git is a separate step.`, { title: "Update file with table version", confirmLabel: "Update file with table version", cancelLabel: "Cancel", variant: "default" })`
   - If `!ok`, return (no API call)
   - `setUpdating(true)`; clear banner `error`
   - `POST` to `/api/admin/repo_json/write/${tableKey}`
   - On success: `fetchStatus()` then `onReverted?.()` (same order as `handleRevert`)
   - On failure: set `error` message
   - `finally`: `setUpdating(false)`

3. Insert button between **Show Differences** and **Revert to file**:

   ```tsx
   <button
     type="button"
     className={updating ? "btn primary in-flight" : "btn primary"}
     disabled={updating || reverting}
     onClick={() => void handleUpdateFile()}
   >
     {updating ? "Updating…" : "Update file with table version"}
   </button>
   ```

4. Update **Show Differences** and **Revert to file** buttons: add `disabled={updating || reverting}` (revert already had `disabled={reverting}` — extend both).

5. Do **not** change `handleRevert` confirm strings, variant, or POST handler.

⚠️ **Decision:** `onReverted?.()` after write keeps page-level `refreshToken` / list reload behavior aligned with revert and save paths (`pattern.ui.in-place-live-refresh` — silent status refetch, no full-page remount).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner`  
**Product commits:** `3c43c353` (sync ftr — AST-1505 compare/write API), `02f3aca7` (Stage 1 — Show Differences modal + copy), `01a2f5b3` (Stage 2 — Update file with table version)

**Implemented:**
- `RepoJsonDivergenceBanner.tsx` — rewritten warning copy; **Show Differences** opens wide `Modal` with `GET /compare/<tableKey>` payload; **Update file with table version** confirm + `POST /write/<tableKey>` + `fetchStatus()` / `onReverted?.()`; **Revert to file** unchanged

**Tests:** Betty at Code Complete (`qa-child`) — engineers do not land test-tree changes.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1506
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner` @ `744bf4a51fae6cac5031de432a60dc446469fd82`

### Traceability

AC1–2 → Stage 1 `openDiff()` + `GET /compare/${tableKey}` modal (props `tableKey` isolates agent vs agent_task); AC3–4 → Stage 2 `handleUpdateFile()` + `POST /write/${tableKey}` then `fetchStatus()`; AC5 → Stage 2 confirm early-return (no POST on cancel); AC6 → Stage 1 rewritten warning span (no restart/deploy/CLI export copy); parent Revert AC → unchanged `handleRevert` per Boundaries.

### Findings

#### discuss

- **Location:** Stage 2 decision note / `pattern.ui.in-place-live-refresh`
- **Finding:** Ticket cites `pattern.ui.in-place-live-refresh`, which remains `status: proposed` in canon — not approved catalog law. Plan does not import `useInPlaceLiveRefresh`; it mirrors the existing revert path (`fetchStatus` + `onReverted?.()`).
- **Recommendation:** Fine to build as written. Optionally soften the pattern citation to "same refresh contract as revert" so Joan/Radia do not treat a proposed id as mandatory hook adoption.

- **Location:** Stage 1 `ROW_KEY_FIELD` / `astral.standards.no-hardcoded-sets`
- **Finding:** Row-key column names (`agent_id`, `task_key`) are duplicated in React for `rowLabel`, parallel to core `_REPO_JSON_ROW_KEY`.
- **Recommendation:** Acceptable for this two-table banner with a `TableKey` union and per-page `tableKey` prop. Optional future: expose key column from compare payload if a third admin table joins the warning.

- **Location:** Plan structure / R6 self-assessment
- **Finding:** No `## Self-Assessment` section (Estimate confirm line present).
- **Recommendation:** Optional add before build; stages and hand-verify pre-flight are otherwise explicit.

#### acceptable

- **Location:** Stage 2 button order / `pattern.ui.shared-button-roles`
- **Finding:** **Revert to file** stays `btn secondary` (not `danger`) per "do not change Revert" boundary; confirm dialog still uses `variant: "danger"`.
- **Recommendation:** Matches ticket Boundaries; destructive styling on the labeled button itself is out of scope.

- **Location:** Pre-flight / sibling AST-1505
- **Finding:** Plan requires Ada compare/write routes on the epic line before build; ticket Notes say "after #1."
- **Recommendation:** `build-child` pre-flight grep is the right gate; Katherine should not re-implement API in this ticket.

## Radia review

**Rubric:** code-rubric.v2  
**Ticket:** AST-1506  
**Publish ref:** `origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner` @ `0bc099bf5c3f9d4ac4264b125eec58d321a087b5`  
**Overall:** CLEAN  
**Diff:** `origin/dev...origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner` — AST-1506 product commits (`02f3aca7`, `01a2f5b3`): `RepoJsonDivergenceBanner.tsx` only (+212/−23).

### Plan adherence

Stages 1–2 delivered: warning copy rewritten; Show Differences modal via GET compare; Update file with confirm + POST write + fetchStatus/onReverted; Revert unchanged; per-table isolation via props `tableKey`.

### Findings (advisory only)

- `ROW_KEY_FIELD` duplicates core row-key columns — acceptable for two-table banner (Joan acceptable).
- Betty tests omit explicit only_in_database/only_in_file modal rendering — optional addition, not blocking.
- Modal list keys could collide in edge cases — optional index suffix if UAT surfaces.
- Statute `astral.seed.agent-tables-in-repo-json` lag on sibling AST-1505 — parent close-out, not AST-1506 blocking.

**No fix-now or discuss findings on Katherine's banner implementation.**

## Bug: AST-1511 — Show Differences modal does not scroll

### As-is

On Manage Agents or Manage Tasks, when the divergence warning is shown and the operator clicks **Show Differences**, the wide modal opens but the body does not scroll. Content below the first viewport (Susan saw only the first three differences) is clipped and unreachable.

### To-be

The **Show Differences** modal scrolls inside the dialog so the operator can review every section — rows only in database, rows only in file, and all changed-field tables — without closing the modal.

### Repro

1. Sign in as admin; open **Manage Tasks** (or **Manage Agents**) with live table diverged from repo JSON (multiple `changed_rows` and/or long field values — e.g. several task keys with `content` drift).
2. Click **Show Differences** on the gold divergence banner.
3. Observe the modal title **Differences — …** and the first diff sections render.
4. Attempt to scroll (wheel, trackpad, or scrollbar) to rows/fields below the fold.
5. **Actual:** no scroll; content below ~first three differences is not visible. **Expected:** modal body scrolls to reveal all diff sections.

Component-test shape (Betty): mock `GET /api/admin/repo_json/compare/<tableKey>` with `changed_rows` length ≥ 4 (or tall `content` strings); after opening modal, assert a later row label (e.g. 4th `row_key`) is reachable via `scrollIntoView` / container `scrollTop` / `within(modal-body).getByText(...)` after scroll helper — no browser UAT required for make-fix.

### Root cause

AST-1506 Stage 1 renders the compare payload inside shared `Modal` with `size="wide"`. In `App.css`, `.modal-card--wide .modal-body` sets `overflow: hidden` and `padding: 0` so wide modals can host nested SideTabPanel layouts with their own scroll regions. The diff modal places content **directly** in `modal-body` with no inner scroll wrapper (unlike `.email-html-source`, which wraps content in `height: 100%; overflow: auto`). Tall diff output is clipped by the fixed `90vh` card.

### Proposed change

**File:** `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` only.

1. Inside the **Show Differences** `<Modal … size="wide" showFooter={false}>`, wrap **all** body branches (loading, error, `diffData`, empty fallback) in one scroll container:

   ```tsx
   <div
     style={{
       padding: "20px",
       height: "100%",
       overflowY: "auto",
       boxSizing: "border-box",
     }}
   >
     {/* existing loading / error / diffData / empty content unchanged */}
   </div>
   ```

2. Do **not** change `Modal.tsx`, `App.css`, compare API, button labels, Update/Revert handlers, or `size="wide"` (table needs horizontal room).

3. **Done when:** With a compare payload taller than the viewport, the inner wrapper scrolls; header (title + ×) stays fixed; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

⚠️ **Decision:** Fix locally in the banner component (same pattern as `.email-html-source` inner scroll) rather than changing global `.modal-card--wide .modal-body` — avoids regressing SideTabPanel wide modals site-wide.

### Blast radius

- **Show Differences modal only** on Manage Agents / Manage Tasks — no other `Modal` call sites.
- **AST-1506** Show/Update/Revert behavior and API wiring unchanged.
- Betty may extend `test_RepoJsonDivergenceBanner.test.tsx` (AST-1511) for multi-row scroll reachability; engineer does not edit `tests/` or `docs/test-bible/**`.

### What must still hold

- Parent AST-1455 AC: **Show Differences** lists actual row and field differences for **that page's table only** (`tableKey` prop); must include rows beyond the first viewport when drift is large.
- **Update file with table version** and **Revert to file** confirm/POST behavior unchanged (AST-1506 Boundaries).
- Wide modal layout preserved for three-column Field / File / Database tables.
- Per-cell `<pre>` scroll for long values (AST-1506 Stage 1) remains; this fix is modal-level scroll for many rows/sections.

## Radia review (AST-1511)

# Radia review-fix — AST-1511

**Rubric:** code-rubric.v2  
**Ticket:** AST-1511  
**Parent:** AST-1455 (normal — `origin/ftr/AST-1455-show-differences-update-file` exists; not orphaned)  
**Publish ref:** `origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` @ `46870882ca8f19ff85869a2a195f0c8bbb916c49`  
**Overall:** CLEAN  
**Diff base:** `origin/ftr/AST-1455-show-differences-update-file...origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` (mandated fix-lane base)

**Diff-base note:** Three-dot diff spans 25 files (+931/−63) — sibling fixes (AST-1512, AST-1513, AST-1515, etc.) merged on `sub/AST-1455/AST-1511` ahead of `ftr`. **AST-1511 footprint:** product commit `46870882` (`RepoJsonDivergenceBanner.tsx` only, +67/−57); Betty `test(AST-1511): bug-repro` @ `1d1b236a` merged @ `dbc44800`. Statute sweep and findings below target AST-1511 footprint; sibling paths on the sub tip are not re-audited in this pass.

---

## Fix-specific checks

### `[bug-repro]` — OK

**Test:** `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` — `RepoJsonDivergenceBanner — AST-1511` → `[bug-repro] Show Differences modal scrolls to later changed rows`

**Assertions (concrete, tied to To-be):**
- Mocks `GET /compare/agent_task` with `tallComparePayload(4)` — four `changed_rows`, each with 200-char `content` values (tall enough to exceed viewport).
- After opening modal, locates `.modal-card--wide .modal-body` → `firstElementChild` scroll wrapper.
- **Pins fix contract:** `scrollWrap.style.overflowY === "auto"` and `scrollWrap.style.height === "100%"` — matches plan-fix `## Proposed change` inline styles exactly.
- Asserts 4th row label `Row: drift_row_4` reachable after `scrollWrap.scrollTop = scrollWrap.scrollHeight`.

**Pre-fix plausibility:** Pre-AST-1511, modal body content sat directly under `.modal-body` (no inner wrapper). `firstElementChild` would be a `<p>` or content `<div>` without `overflowY: auto` — style assertions **fail**. Correct repro-first shape.

**Caveat (advisory, not fix-now):** `toBeVisible()` after manual `scrollTop` is weak in jsdom (no real layout clip). Primary guard is structural wrapper + overflow styles; acceptable for component tier.

### `## What must still hold` — OK

| Item | Verdict |
|------|---------|
| Show Differences lists row/field diffs for **that page's `tableKey` only** | OK — `openDiff()` still calls `/compare/${tableKey}`; modal sections unchanged |
| **Update file** and **Revert to file** confirm/POST behavior unchanged | OK — `handleUpdateFile` / `handleRevert` untouched in `46870882` |
| Wide modal layout for Field/File/Database tables | OK — `size="wide"` retained; tables unchanged |
| Per-cell `<pre>` scroll for long values (`diffCellContent`) | OK — helper untouched; modal-level scroll is additive |

---

## Statutes checked

Scored against AST-1511 footprint (`RepoJsonDivergenceBanner.tsx` + Betty bug-repro test).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no dispatch |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade vector |
| astral.batch.batch-id-first | scoped | not-applicable | no batch |
| astral.batch.batch-id-format | scoped | not-applicable | no batch |
| astral.batch.claim-process-release | scoped | not-applicable | no batch |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch |
| astral.config.config-source-of-truth | scoped | not-applicable | no config |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next |
| astral.docs.features-single-file-per-ticket | scoped | conforms | plan-fix patch in parent AST-1506 feature doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test-tree only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer product commit: one TSX file only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | frontend only |
| astral.layers.import-direction | scoped | conforms | no new imports; Modal import pre-existing |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | `tableKey` prop still drives compare URL |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | still calls authenticated admin routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed/boot paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no bootstrap |
| astral.seed.define-approved | scoped | not-applicable | no seed catalog |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no boot apply |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug logging |
| astral.standards.dry-and-focused-functions | scoped | conforms | minimal wrapper; comment explains why |
| astral.standards.in-scope-only | scoped | conforms | single file per plan-fix blast radius |
| astral.standards.logging-via-utils | scoped | conforms | no logging added |
| astral.standards.names-not-ticket-ids | scoped | conforms | N/A |
| astral.standards.no-cross-contamination | scoped | conforms | Show Differences modal only |
| astral.standards.no-hardcoded-sets | scoped | conforms | no new hardcoded table sets |
| astral.standards.public-then-helpers | scoped | conforms | N/A |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils |
| astral.state.core-decides-transitions | scoped | not-applicable | no state machine |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job states |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run chain |
| astral.ui.frontend-file-placement | scoped | conforms | component path unchanged |
| astral.ui.naming-conventions | scoped | conforms | N/A |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1511)` at tip ancestry |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1511)` / `test(AST-1511)` |
| orch.git.flow-direction-inviolable | universal | conforms | fix sub on ftr line |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1455/AST-1511-*` |
| orch.git.merge-on-checkout | universal | conforms | N/A |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | N/A |
| orch.git.no-dev-agent-branches | universal | conforms | N/A |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1455 worktree |
| orch.git.three-permanent-branches | universal | conforms | ftr base used |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | localized CSS workaround per plan decision |
| orch.pipeline.plan-is-bible | universal | conforms | matches `## Proposed change` exactly |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped fix |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | N/A |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty bug-repro |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | single TSX product file |

Registry: 63 active rows scored.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan-fix cites `.email-html-source` pattern by analogy, not a catalog id |

---

## Plan adherence

**`## Proposed change` delivered** in `46870882`:
- Inner scroll wrapper wraps **all** modal body branches (loading, error, `diffData`, empty).
- Styles: `padding: 20px`, `height: 100%`, `overflowY: auto`, `boxSizing: border-box` — match plan.
- `Modal.tsx`, `App.css`, compare API, button labels, Update/Revert handlers, `size="wide"` — untouched.
- In-code comment documents root cause (`.modal-card--wide .modal-body` `overflow: hidden`).

**Root cause / To-be:** Addresses clipped tall compare output; operator can scroll all sections inside dialog while header stays fixed (wrapper inside `modal-body`, not global CSS change — correct blast-radius decision).

**Blast radius:** Show Differences modal only — confirmed.

---

## Findings

**No fix-now or discuss findings.**

### advisory

- **Location:** `[bug-repro]` test — `toBeVisible()` after `scrollTop`  
- **Finding:** jsdom does not model overflow clipping; structural style assertions are the real gate.  
- **Recommendation:** Susan hand-verify on staging if desired; not blocking.

- **Location:** Diff base `ftr...sub`  
- **Finding:** Sub tip carries sibling fix commits not yet on `ftr`; unrelated to AST-1511 product quality.  
- **Recommendation:** `merge-child` / ftr rollup handles separately; do not attribute sibling diffs to this fix review.

---

## What's solid

- Localized fix mirrors existing `.email-html-source` inner-scroll pattern — avoids site-wide `.modal-card--wide` regression.
- All modal states (loading/error/empty/data) scroll consistently.
- AST-1506 Show/Update/Revert wiring preserved.
- Betty bug-repro pins wrapper contract and 4-row payload; fails pre-fix.

---

## Frame diff

AST-1511 frame = inner scroll `<div>` in Show Differences `Modal` + Betty `[bug-repro]` test + plan-fix patch in AST-1506 feature doc. No API, CSS global, or sibling behavior changes in AST-1511 product commit.

---

## Notes for Chuckles

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal AST-1455 | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` **skipped**) |

No `[board-betty]` / `[board-joan]` comments on issue doc — qa-fix ran with `[bug-repro]` test (valid; not clean-board opt-out absence issue).

C7 artifact complete.

`context_tokens≈72000`

---

```
[code-rubric] PROCEED (Commit: 46870882) modal scroll wrapper fixed
