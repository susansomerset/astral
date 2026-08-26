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
