# AST-1142 — Manage Email multi-select + Land Meteorite + retire Create

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1142/manage-email-multi-select-land-meteorite-retire-create-manage-email  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite  

**Publish ref (origin):** `sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create`  
**Parent integration ref:** `ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`

After AST-1141: add multi-select + **Land Meteorite** on Manage Email, wire it to `POST /api/admin/inbox/land-meteorite`, show per-selected-message outcomes (including skips) without leaving the page, and **retire** the per-row **Create** control. Does **not** redesign the rest of Manage Email. Does **not** own core ingest (AST-1140) or the admin API (AST-1141). Does **not** call `/create-job` / strip-extract create.

**Depends on:** AST-1141 on `origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite` (merge that tip before build — `POST /api/admin/inbox/land-meteorite` + pass-through `results` / totals must exist).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Multi-select; Land Meteorite; batch outcome panel; remove Create | ui |
| `src/ui/frontend/src/App.css` | Toolbar / outcome / checkbox styles; drop `.manage-email-create` | ui |

No `src/core/**`, no `src/ui/api/**`, no `src/utils/config.py`, no `tests/` / bible, no route/nav changes.

---

## Stage 1: Multi-select chrome + Land Meteorite enablement (no POST yet)

**Done when:** On Manage Email, Archie can select/deselect individual inbox rows, select all visible rows, and clear selection without leaving the page. A **Land Meteorite** control is visible; it is disabled (not actionable) when the selection is empty and enabled when one or more message ids are selected. Per-row **Create** is still present in this stage (retired in Stage 2). No Land Meteorite network call yet.

1. In `src/ui/frontend/src/pages/AdminManageEmail.tsx`, add selection state:

   ```ts
   const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
   ```

   Helpers (inline functions or `useCallback` — match existing page style; this file already uses `useCallback` for toast clear):

   - `toggleSelect(id: string)` — add/remove id in a new `Set` copy.
   - `selectAllVisible()` — `setSelectedIds(new Set(messages.map(m => m.id)))`.
   - `clearSelection()` — `setSelectedIds(new Set())`.
   - `selectionCount = selectedIds.size`.
   - `landEnabled = selectionCount > 0 && !landBusy` (introduce `landBusy` boolean state now, default `false`; Stage 2 sets it during POST).

2. Above the table (inside the `!loading && !error` block), add a toolbar row with:

   - Button **Select all** → `selectAllVisible()` (disabled when `messages.length === 0`).
   - Button **Clear selection** → `clearSelection()` (disabled when `selectionCount === 0`).
   - Button **Land Meteorite** → Stage 1: `type="button"` with `disabled={!landEnabled}`; `onClick` may be a no-op stub `() => {}` or omitted until Stage 2 — must not call `/create-job`. Label text exactly `Land Meteorite`.
   - Short status text: `{selectionCount} selected` (plain text).

3. Add a leading checkbox column:

   - Header: checkbox that is checked when `messages.length > 0 && selectedIds.size === messages.length`; `onChange` → if all selected then `clearSelection()`, else `selectAllVisible()`. Stop row-open behavior is N/A on `<th>`.
   - Each body row: `<td onClick={e => e.stopPropagation()}>` wrapping `<input type="checkbox" checked={selectedIds.has(row.id)} onChange={() => toggleSelect(row.id)} />`.
   - Keep existing row `onClick={() => openMessage(row)}` for subject/body open; checkbox cell must not open the modal.

4. Update empty-state `colSpan` from `6` to `7` (new checkbox column).

5. In `src/ui/frontend/src/App.css`, add minimal classes next to the existing `.manage-email-*` block (after `.manage-email-create` is fine):

   - `.manage-email-toolbar` — flex row, gap, margin under the h1 / above the table.
   - `.manage-email-toolbar button` — reuse button look consistent with `.manage-email-create` (padding/font), including `:disabled` opacity.
   - Do **not** delete `.manage-email-create` yet (Stage 2).

⚠️ **Decision — stay on custom `AdminManageEmail` page, do not migrate to `ListPage`:** Parent AC is selection + Land Meteorite + Create retirement only. Rewiring the page through `ListPage` would expand scope into shared list chrome without buying AC fidelity.

⚠️ **Decision — selection is client-only `Set<string>` of message ids:** Server already owns ingest eligibility (AST-1140/1141). React must not invent bind/match filters for which rows may be selected — any current inbox row is selectable; skips come back in the API `results`.

**Done when (recheck):** With ≥2 loaded messages, select two → toolbar shows `2 selected` and Land Meteorite enabled; Clear → `0 selected` and Land Meteorite disabled; Select all → all checkboxes on; clicking a checkbox does not open the message modal; Create still visible on matched rows.

---

## Stage 2: Wire Land Meteorite POST + outcome panel + retire Create

**Done when:** Clicking **Land Meteorite** with a non-empty selection `POST`s `{ "message_ids": [...] }` to `/api/admin/inbox/land-meteorite`, shows each selected id’s `outcome` (and subject when known) on the page, surfaces HTTP errors without navigating away, retires per-row Create (button + handler + busy state + CSS), and does not call `/create-job`.

1. Add types for the AST-1141 response (local to the page file):

   ```ts
   type LandMeteoriteResultRow = {
     message_id: string
     outcome: string
     astral_candidate_id: string | null
   }

   type LandMeteoriteResponse = {
     results?: LandMeteoriteResultRow[]
     total_processed?: number
     total_passed?: number
     total_failed?: number
     total_errors?: number
     total_skipped?: number
     error?: string
   }
   ```

2. Add state:

   ```ts
   const [landBusy, setLandBusy] = useState(false)
   const [landResults, setLandResults] = useState<LandMeteoriteResultRow[] | null>(null)
   const [landError, setLandError] = useState<string | null>(null)
   ```

3. Implement `async function onLandMeteorite()`:

   - If `selectedIds.size === 0` or `landBusy`: return.
   - `const ids = messages.filter(m => selectedIds.has(m.id)).map(m => m.id)` — preserve **current list order** (stable display); if a selected id is missing from `messages` (stale), append leftovers from `[...selectedIds]` after the ordered ones so the POST still includes every selected id.
   - `setLandBusy(true)`; `setLandError(null)`; `setLandResults(null)`; clear toast optional.
   - `POST` via existing `api()` helper:

     ```ts
     const r = await api("/api/admin/inbox/land-meteorite", {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ message_ids: ids }),
     })
     ```

   - Parse JSON as `LandMeteoriteResponse`.
   - If `!r.ok`: set `landError` from `data.error` or `HTTP ${r.status}`; optional error toast; do **not** clear selection.
   - If `r.ok`: `setLandResults(Array.isArray(data.results) ? data.results : [])`; `clearSelection()`; optional success toast with totals (`total_passed` / `total_skipped` / `total_failed` / `total_errors` when present) — toast is summary only; the results panel is the AC6 surface.
   - After `r.ok`, reload the inbox list with the same fetch pattern as the mount `useEffect` (extract a `loadMessages` async function used by mount + post-land) so archived rows disappear.
   - `finally`: `setLandBusy(false)`.

4. Wire toolbar **Land Meteorite** `onClick={onLandMeteorite}` and `disabled={!landEnabled}` where `landEnabled = selectedIds.size > 0 && !landBusy`. While busy, button label may stay `Land Meteorite` (disabled) — do not invent a spinner requirement.

5. Below the toolbar (still above the table), render batch feedback when `landError` or `landResults`:

   - If `landError`: a paragraph with `color: var(--danger)` showing the error string.
   - If `landResults`: a compact results block titled `Land Meteorite results` listing one line/row per result:

     - Resolve subject: `messages.find(m => m.id === row.message_id)?.subject` **or** keep a snapshot map built just before POST from the then-current `messages` if the reload clears subjects — **Decision below** requires a pre-POST snapshot.
     - Show: subject (or message_id fallback), `outcome` string exactly as returned, and `astral_candidate_id` when non-null.
     - Presentation class helper (local function, not config):

       ```ts
       function outcomeKind(outcome: string): "skip" | "fail" | "ok" {
         const o = (outcome || "").trim()
         if (o.startsWith("skipped-") || o === "skipped-other-candidate") return "skip"
         if (o === "error" || o === "failed") return "fail"
         return "ok"
       }
       ```

       Map kind → CSS class (`manage-email-outcome--skip` / `--fail` / `--ok`). Do **not** invent ingest eligibility; this is display-only bucketing of server outcome strings.

⚠️ **Decision — snapshot subjects at POST time:** After a successful land, inbox reload may drop archived messages. Build `const subjectById = Object.fromEntries(messages.map(m => [m.id, m.subject]))` (or a `Map`) immediately before `fetch`/`api` and use it when rendering `landResults` so Archie still sees which selected subjects landed/skipped/failed.

⚠️ **Decision — show raw `outcome` strings from AST-1141/1140:** Skip vocabulary (`skipped-unbound`, `skipped-not-in-inbox`, `skipped-unmatched`) and bound outcomes (`archived`, `ignored`, `ignored-empty`, `error`, …) stay server-authored. React must not remap them to Create-era “Created job …” copy.

6. **Retire Create** in the same stage (same commit):

   - Delete `createBusyId` state, `onCreateClick`, and the entire Actions column cell that renders the Create button (matched-only Create).
   - Remove the **Actions** column header and body cells; drop Actions from the table entirely (checkbox + Subject + From + Candidate + Date + Status).
   - Update empty-state `colSpan` to `6` (checkbox + 5 data columns).
   - Delete unused `MouseEvent` import if nothing else needs it.
   - In `App.css`, **delete** `.manage-email-create` and `.manage-email-create:disabled`.
   - Add `.manage-email-results` / `.manage-email-outcome--ok|skip|fail` minimal styles (muted / warning / danger text colors using existing CSS variables where present).

7. Do **not**:

   - Call `/api/admin/inbox/messages/<id>/create-job` from this page.
   - Delete or edit `src/ui/api/api_inbox.py` create-job / land-meteorite routes (API leftover create-job is out of scope; Land Meteorite already exists from AST-1141).
   - Edit `src/core/**`, NAV_CONFIG, or routes.
   - Add React debug logging.
   - Filter selectable rows by `candidate_match` (unbound selected rows are valid; API returns skip outcomes).

**Done when (recheck):**

- Empty selection → Land Meteorite disabled; no POST.
- Non-empty selection → POST body `message_ids` matches selection; `200` shows a per-id results list with outcomes including at least one skip string when an unbound id was selected; page stays on Manage Email.
- Matched-row **Create** button is gone; no `manage-email-create` class in CSS; no `create-job` string in `AdminManageEmail.tsx`.
- `npm`/Vite typecheck path the repo already uses for frontend still accepts the page (or `tsc --noEmit` if that is the local habit — do not add a new toolchain).

---

## Self-Assessment

**Scope:** `Single-Component` — Manage Email React page + small CSS; consumes AST-1141 API only.

**Conf:** `high` — API contract is on `ftr`; page already lists inbox via `api()`; checkbox multi-select pattern exists on `JobsSkipped`; Create retirement is delete of known UI.

**Risk:** `Medium` — wrong POST wiring or leaving Create active would regress parent AC3/AC4/AC8; mitigated by literal endpoint path, enablement gate, and explicit Create deletion checklist.

---

## Code Rules check

- **§3.2 / `astral.layers.ui-config-driven-business-logic`:** Ingest/skip/create decisions stay server-side; React only selects ids, posts them, and renders returned `outcome` strings. No hardcoded candidate-state or bind rules in the page.
- **`pattern.ui.admin-endpoint`:** Calls existing authenticated admin mutator; no new Flask route on this ticket.
- **`astral.standards.in-scope-only`:** Selection chrome + Land Meteorite + Create retirement only; no Manage Email redesign, no core/API edits.
- **`astral.ui.frontend-file-placement` / naming:** Edit stays in `pages/AdminManageEmail.tsx`; route `admin/manage_email` unchanged.
- **§3.3:** Frontend → `api()` only; no direct core/data/external imports.
- **§1.5.1 debug:** No React debug requirements (parent AC9 is backend).

---

## Review

**Publish ref:** `origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create`
**Tip:** `2ee72f4b` (code); docs stub follows on publish-ref

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `1756919c` | multi-select chrome + Land Meteorite enablement |
| 2 | `2ee72f4b` | Land Meteorite POST + outcome panel; retire Create |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Overall:** DISCUSS (no fix-now on Manage Email UI; C4 dependency-merge stragglers)

**What’s solid**
- Multi-select + Select all / Clear / Land Meteorite enablement; checkbox cell stops row-open.
- POST `/api/admin/inbox/land-meteorite` with ordered ids + leftovers; subject snapshot; results panel with raw outcomes; Create retired (handler/column/CSS gone); no `create-job` on the page.
- AST-1142 `code()` = `AdminManageEmail.tsx` + `App.css` only.

**Issues / Recommended**
- **discuss (C4 stragglers):** Tip includes AST-1140/1141 + Betty tests/bible via dependency/`merge-tests`; Joan-excluded statutes in-scope on three-dot tip all scored **conforms** (see Linear). No product rewrite for this UI.
- **advisory (matches Joan):** `outcomeKind` display bucketing of server outcome strings is plan-documented; not eligibility logic.

Full `## Statutes checked` (65/65) lives in the Linear Review Posted comment.

---

## Resolution

**Date:** 2026-08-02  
**Review tip intake:** `e70e804e` (`docs(AST-1142): Radia review — findings`)

| Finding | Disposition |
|---------|-------------|
| fix-now | none — no product change |
| discuss (C4 stragglers) | accepted as scored **conforms**; no rewrite for this UI child |
| advisory (`outcomeKind` display bucketing) | leave as plan-documented display-only CSS; not eligibility |

**Commit:** `resolve(AST-1142): — clean`
