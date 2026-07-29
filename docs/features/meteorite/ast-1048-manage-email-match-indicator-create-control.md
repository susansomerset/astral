# AST-1048 — Manage Email match indicator + Create control

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1048/manage-email-match-indicator-create-control-bind-email-to-candidate  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate  

**Publish ref (origin):** `sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`  
**Parent integration ref:** `ftr/AST-1044-bind-email-to-candidate`

Rename the admin **Read email** surface to **Manage Email**, render the AST-1047 `candidate_match` bind on list + selected message, and expose an **active Create** control only when `candidate_match.matched` is true — while unmatched messages stay fully browsable. Does **not** implement reusable lookup (AST-1047, already on `ftr`) or strip/extract + meteorite create (AST-1049).

Boundaries (do **not** implement): `get_candidate_id_for_query` / `CANDIDATE_LOOKUP_CONFIG` / inbox From enrichment (AST-1047); strip/extract, subject-in-content, `POST` meteorite create orchestration (AST-1049); multi-candidate picker; Gmail client changes; mailbox mutation; Profile/Admin contact editors.

**Depends on:** AST-1047 rolled on `origin/ftr/AST-1044-bind-email-to-candidate` (merge that tip before build — list payloads already include `candidate_match`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename Admin nav item label `Read email` → `Manage Email`; change path `/admin/read_email` → `/admin/manage_email` | utils |
| `src/ui/frontend/src/pages/AdminReadEmail.tsx` | Rename file → `AdminManageEmail.tsx`; heading, match column/indicator, Create enablement from `candidate_match` | ui |
| `src/ui/frontend/src/routes.tsx` | Import `AdminManageEmail`; route path `admin/manage_email` under `AdminRoute` | ui |
| `src/ui/frontend/src/App.css` | Minimal styles for match indicator + Create control on the Manage Email page (no new CSS framework) | ui |

No new API blueprints, no `src/core/**` changes, no `src/external/**` changes.

---

## Stage 1: Nav + route rename (Manage Email)

**Done when:** Admin sidebar shows **Manage Email** linking to `/admin/manage_email`; that route renders the (still-old-chrome) page under `AdminRoute`; `/admin/read_email` is no longer registered. No match/Create UI yet.

1. In `src/utils/config.py`, locate the Admin `NAV_CONFIG` item currently `{"label": "Read email", "path": "/admin/read_email"}` (after Session Cover Letter). Change it to:

```python
{"label": "Manage Email", "path": "/admin/manage_email"},
```

Keep relative order among Admin items unchanged (still immediately after Session Cover Letter).

2. Rename `src/ui/frontend/src/pages/AdminReadEmail.tsx` → `src/ui/frontend/src/pages/AdminManageEmail.tsx` (git `mv`). Rename the default export function `AdminReadEmail` → `AdminManageEmail`. Change the page `<h1>` text from `Read email` to `Manage Email`.

3. In `src/ui/frontend/src/routes.tsx`:
   - Update the import to `AdminManageEmail` from `./pages/AdminManageEmail`.
   - Change the route from `path: "admin/read_email"` to `path: "admin/manage_email"` with the same `<AdminRoute>` wrapper.
   - Do **not** leave a redirect/alias for `admin/read_email`.

⚠️ **Decision — path rename:** AC requires the screen/nav **label** Manage Email. Changing the path to `/admin/manage_email` keeps nav path and label aligned and avoids a permanent “Read email” URL. Deep links to `/admin/read_email` intentionally break (seed surface only; no public bookmarks required).

⚠️ **Decision — no backend rename:** Inbox APIs stay under `/api/admin/inbox/**` with `@require_admin` (AST-1033 / AST-1047). This ticket does not rename API prefixes.

---

## Stage 2: Match indicator from `candidate_match` (list + modal)

**Done when:** List rows that ship `candidate_match.matched === true` show a clear visual bind to `candidate_match.astral_candidate_id`; unmatched/ambiguous (`matched === false` or missing object) show a neutral empty/“—” cell; opening a row still loads HTML body as today; no Create button yet.

1. In `AdminManageEmail.tsx`, extend the `InboxMessage` type:

```ts
type CandidateMatch = {
  matched: boolean
  astral_candidate_id: string | null
}

type InboxMessage = {
  id: string
  thread_id: string
  subject: string
  from_address: string
  date: string
  unread: boolean
  candidate_match?: CandidateMatch
}
```

Treat missing `candidate_match` as unmatched (defensive — AST-1047 always attaches the object on list).

2. Add a table column **Candidate** (header after **From**, before **Date** is fine; keep one consistent order):

| Condition | Cell content |
|-----------|--------------|
| `row.candidate_match?.matched === true` and non-empty `astral_candidate_id` | Visible bind text: `Matched: {astral_candidate_id}` plus CSS class `manage-email-match` on the cell (or inner span) |
| otherwise | `—` (em dash), no match class |

3. In the message modal (after open), show the same bind under the modal title area (or as a one-line subtitle above the HTML body): when matched, render `Matched: {id}`; when not, omit the line (do not show “unmatched” noise — browse stays calm).

4. Do **not** re-call lookup from the browser. Do **not** invent match rules in React. Use only the server `candidate_match` payload from `GET /api/admin/inbox/messages`.

5. In `App.css`, add minimal rules for `.manage-email-match` (e.g. slightly emphasized text color using existing CSS variables such as `--text-primary` / accent already used on admin pages — no new purple/glow theme). Keep rules short; no layout rewrite of the table.

⚠️ **Decision — list is source of truth for bind:** AST-1047 enriches **list** only; get-message returns HTML. Selected-row match comes from the list row already in React state (`messages.find`). Do not change `get_message_html` / get API in this ticket.

---

## Stage 3: Create control enablement (no meteorite wire)

**Done when:** Matched selected message shows an enabled **Create** button; unmatched/ambiguous selected message shows **Create** disabled (or hidden — see Decision); unmatched browse (list + HTML modal) still works; clicking Create does **not** call meteorite create or strip/extract (AST-1049 owns that).

1. In the modal footer/actions area of `AdminManageEmail.tsx`, add:

```tsx
<button
  type="button"
  className="manage-email-create"
  disabled={!selected?.candidate_match?.matched}
  onClick={onCreateClick}
>
  Create
</button>
```

where `selected` is the current list row for `selectedId`.

2. Implement `onCreateClick` as a **no-op stub** for this ticket:

```ts
function onCreateClick() {
  // AST-1049 owns strip/extract + meteorite create wire from this control.
}
```

Do **not** `POST` `/api/candidates/.../meteorite/jobs`. Do **not** invent a new create inbox endpoint. Do **not** toast “not implemented” as product UX unless you need a temporary guard — prefer silent no-op so AST-1049 replaces the body without fighting a fake error path.

3. Enablement rule (literal):

- `disabled === false` only when `selected.candidate_match?.matched === true`.
- Otherwise `disabled === true` (button still visible so Susan sees the control exists but inactive).

4. Optional list-row Create is **out of scope** — Create lives on the open-message modal only (operator already inspecting the body).

5. Confirm `AdminRoute` remains on the route (Stage 1) so unauthenticated users cannot reach the screen; do not add a public route.

⚠️ **Decision — disabled vs hidden:** Parent AC3: matched exposes an **active** Create; unmatched does **not**. Showing a disabled Create on unmatched rows teaches the control without implying orphan jobs are creatable. Do not hide the button entirely on unmatched.

⚠️ **Decision — Create click owned by AST-1049:** This ticket’s AC stops at enablement chrome. Wiring Create to strip/extract + AST-1034 meteorite create is **AST-1049** only. Leaving a labeled stub `onCreateClick` avoids dual ownership of the same handler.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the Files Changed table.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`, then proceeds.

Blocking comment format (parent AST-1044):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — Admin Manage Email React page + `NAV_CONFIG` / route rename + light CSS; consumes AST-1047 `candidate_match` only; no core/API create path.

**Conf:** high — AST-1047 already ships list enrichment; existing `AdminReadEmail` + `AdminRoute` + nav config are the exact surfaces to rename/extend; Create stub boundary with AST-1049 is explicit.

**Risk:** Medium — nav/path rename breaks old `/admin/read_email` bookmarks and revises AST-1033 nav/path tests; wrong enablement would show Create on unmatched senders (orphan-job UX risk once AST-1049 wires click).

---

## Code Rules self-review

| Rule | Check |
|------|--------|
| §1.3 DRY | Reuse list `candidate_match`; no second lookup client-side |
| §2.1 / no-hardcoded-sets | Match eligibility from server payload; no inline email/name field lists in React |
| §3.3 import direction | UI → `api()` only; no Gmail/data imports in the page |
| `require-auth` / AdminRoute | Keep `AdminRoute`; inbox APIs stay `@require_admin` (unchanged) |
| ui-config-driven business logic | Create enablement = `candidate_match.matched` from API, not React heuristics |
| In-scope only | No strip/extract, no meteorite POST, no lookup config edits |

---

## Review (build stub)

**Publish ref:** `sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`
**Build tip:** `88df7b07ba5dce779485a6fd4fb93d681dcb1b5e`
