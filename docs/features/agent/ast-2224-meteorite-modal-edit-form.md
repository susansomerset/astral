# AST-2224 — Edit form on the meteorite modal

- **Linear:** [AST-2224](https://linear.app/astralcareermatch/issue/AST-2224)
- **Parent:** [AST-2216](https://linear.app/astralcareermatch/issue/AST-2216) — Make meteorite text editable (not versioned)
- **Publish ref:** `sub/AST-2216/AST-2224-meteorite-modal-edit-form`

React half of candidate meteorite edit: when the detail GET says the row is editable, the Jobs → Meteorites detail modal renders inputs for exactly the server-listed fields, a state `<select>` pre-selected to the server default, and one Save that PUTs those fields; on success it re-fetches detail and tells the list page to reload; on 4xx it shows the server's `error` text and does not fire the saved callback. Ships parent AC 1 (React half) and AC 12. Does **not** own config / core / API (sibling AST-2223).

## UAT fitness

- **AC restored:** Parent AC 1 (React half): *Negative check: `rg -n "LANDED|\"CHECK_UNIQUE\"|\"NEW\"" src/ui/frontend/src/components/MeteoriteDetailModal.tsx` returns nothing — React must not hard-code states.* Parent AC 12: *Frontend component test: editable detail → one input per server-listed field, a state select pre-selected to the server default, and a Save button; non-editable detail → read-only view and no Save button; Save success → detail re-fetched and the "saved" callback fires once; Save 409 → the server's error text is shown and the callback does not fire.*
- **Correct outcome:** On a non-landed meteorite, the candidate can edit JD text / link / title / employer / electronic contact / state from the modal, Save, see the modal refresh with the stored values, and see the Meteorites list refresh — without leaving the modal or inventing states client-side.
- **Sibling check:** AST-2223 (User Testing) owns `GET` edit envelope keys `editable`, `editable_fields`, `state_options`, `default_save_state` and `PUT /api/meteorites/<id>` requiring the full editable set (incl. `content` + `state`). This ticket only consumes that contract; verify by typing envelope fields from the GET response and sending PUT bodies whose keys are exactly `editable_fields` (no client-invented keys).
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Hard-coding `LANDED` / `CHECK_UNIQUE` / `NEW` (or any state/field list) in `MeteoriteDetailModal.tsx`, or treating editability as a client-side state check — that breaks AC 1 and diverges from AST-2223's config-sourced envelope.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` | Edit form from server envelope; PUT save; re-fetch; optional `onSaved` | ui |
| `src/ui/frontend/src/pages/JobsMeteorites.tsx` | Pass list `load` as modal `onSaved` | ui |

Do **not** edit: `src/utils/config.py`, `src/core/meteorite.py`, `src/ui/api/api_meteorite.py` (AST-2223), `src/data/database.py`, `tests/**`, bible, SearchResults (optional `onSaved` stays unset — out of this ticket's Scope).

**Prerequisite (not this ticket's Files Changed):** product tree for build must include AST-2223's detail envelope + PUT. Contract used below is frozen on `origin/sub/AST-2216/AST-2223-candidate-meteorite-edit` (`_detail_payload` + `meteorite_candidate_edit`).

## Stage 1: MeteoriteDetailModal edit form + save

**Done when:** With a mocked detail payload where `editable: true` and `editable_fields` / `state_options` / `default_save_state` are set, the modal shows one control per listed field (textarea for `content`, `<select>` for `state` pre-selected to `default_save_state`, text inputs otherwise) and a Save control; with `editable: false` or missing, today's read-only `ReportSectionList` path remains and there is no Save. Save success re-GETs detail, applies the new payload, and invokes `onSaved` once; Save 409 shows `body.error` and does not invoke `onSaved`. `rg -n 'LANDED\|"CHECK_UNIQUE"\|"NEW"' src/ui/frontend/src/components/MeteoriteDetailModal.tsx` returns nothing. `npx tsc -b` in `src/ui/frontend` passes for the touched component (or repo-equivalent frontend typecheck).

1. In `src/ui/frontend/src/components/MeteoriteDetailModal.tsx`, extend `Props`:

```ts
type Props = {
  meteoriteId: number | null
  onClose: () => void
  /** Optional: host refreshes its list after a successful candidate save (AST-2224). */
  onSaved?: () => void
}
```

Export signature becomes `function MeteoriteDetailModal({ meteoriteId, onClose, onSaved }: Props)`.

2. Extend detail load state to keep the AST-2223 envelope next to `meteorite` / `sections`:

   - After a successful GET JSON parse, set:
     - `sections` / `meteorite` as today
     - `editable` = `data.editable === true` (missing → false)
     - `editableFields` = `Array.isArray(data.editable_fields) ? data.editable_fields.map(String) : []`
     - `stateOptions` = `Array.isArray(data.state_options) ? data.state_options.map(String) : []`
     - `defaultSaveState` = `typeof data.default_save_state === "string" ? data.default_save_state : ""`
   - Clear those envelope fields on close / 404 / load failure (same branches that clear `meteorite`).

3. Add draft + save UI state: `draft: Record<string, string>`, `saving: boolean`, `saveError: string | null`.

4. When load succeeds and `editable` is true, initialize `draft` as follows (do this in the same success path as step 2, and again after a successful save re-fetch in step 8):

   - For each `key` in `editableFields` **in server order**:
     - If `key === "state"`: `draft[key] = defaultSaveState` (server default — **not** `meteorite.state`).
     - Else: `draft[key] = String(meteorite?.[key] ?? "")` — raw string, **no** `formatMeteoriteContent` pretty-print (that helper stays display-only on the read-only content path).
   - If not editable: `draft = {}` and `saveError = null`.

5. When `editable` is true, render an edit form **above** the existing `ReportSectionList` (keep sections for classify_outcome / timestamps / provenance id+sources / linked job — read-only context). Form rules:

   - Iterate `editableFields` in order. For each `key`:
     - Label text = `key` (no client-side rename table).
     - If `key === "content"`: `<textarea className="entity-story-content" value={draft[key] ?? ""} onChange=… />` (editable — not `readOnly`).
     - Else if `key === "state"`: `<select value={draft[key] ?? ""} onChange=…>` with one `<option value={opt}>{opt}</option>` per entry in `stateOptions` (again: options come only from the server array).
     - Else: `<input type="text" value={draft[key] ?? ""} onChange=… />`.
   - Show `saveError` when non-null (reuse an existing error class such as `list-page-status` or `entity-error` already used in this UI family).
   - ⚠️ **Decision:** Do **not** strip editable keys from `ReportSectionList` section bodies in this ticket — duplicate display of link/content/state is acceptable and keeps the read-only section code path unchanged for non-edit fields. Prefer a short form block + Save over rewriting `renderMeteoriteSection`.

6. Wire Modal Save exactly when editable:

   - Keep `showFooter={false}` when **not** editable (today's behavior).
   - When editable: `showFooter={true}` and `onSave={handleSave}` so Modal's primary footer button is the single Save (matches `CompanyDetailModal` / Modal contract). Do not add a second in-body Save button.

7. Implement `handleSave` (async):

   - No-op if `meteoriteId == null`, not `editable`, or `saving`.
   - `setSaving(true)`; `setSaveError(null)`.
   - Body = plain object: for each `key` in `editableFields`, `body[key] = draft[key] ?? ""` (exactly those keys — AST-2223 Stage 2h requires `content` + `state` present).
   - `api(\`/api/meteorites/${meteoriteId}\`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })`.
   - If `!res.ok`: parse JSON if possible; `setSaveError(String(body.error ?? "Save failed"))`; **do not** call `onSaved`; return.
   - If `res.ok`: parse JSON; apply the same envelope + meteorite + sections setters as the GET success path (step 2), re-init draft (step 4), then `onSaved?.()` **once**. Do **not** call `onClose` (modal stays open with refreshed detail — parent AC 7 / functional scope).

8. Extract a small internal helper (same file) `applyDetailPayload(data: …)` used by both the initial GET and the PUT 200 path so load and post-save refresh stay identical — no duplicated field mapping.

9. Hard rule for AC 1 React half: this file must contain **no** string literals `LANDED`, `CHECK_UNIQUE`, or `NEW` (quoted or bare identifiers used as state names). State options and defaults come only from the envelope variables.

## Stage 2: JobsMeteorites list refresh on save

**Done when:** `JobsMeteorites` passes its existing `load` callback as `onSaved` on `MeteoriteDetailModal`; a successful modal save triggers one list reload. `npx tsc -b` in `src/ui/frontend` still passes.

1. In `src/ui/frontend/src/pages/JobsMeteorites.tsx`, change the modal usage from:

```tsx
<MeteoriteDetailModal meteoriteId={viewingId} onClose={() => setViewingId(null)} />
```

to:

```tsx
<MeteoriteDetailModal
  meteoriteId={viewingId}
  onClose={() => setViewingId(null)}
  onSaved={load}
/>
```

2. Do not invent a second reload path; `load` is already the list's `useCallback` fetch.

## Execution contract

- Stages in order; one commit per stage on the epic worktree; push `origin/sub/AST-2216/AST-2224-meteorite-modal-edit-form` after each stage.
- Do not add files outside Files Changed; do not implement server logic; do not edit `tests/` (Betty owns AC 12 frontend component coverage under qa-child).
- If the worktree lacks AST-2223's GET envelope / PUT route when building, stop and comment on **parent** AST-2216 with the Stage-blocked template (need sibling product on the epic line) — do not stub those routes in React.
- Ambiguity / drift → comment on **parent** AST-2216 with the Stage-blocked template and stop.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Ticket:** AST-2224
**Overall:** REVISE
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-2216/AST-2224-meteorite-modal-edit-form` @ `e2622e005df06159ad9a672fc99d9c65218c3c77`

## Canon scores

(no directives — ticket **Citations:** `none`; frozen list empty by dispatch partition; nothing to score in R3)

## Traceability

1 → Stage 1 steps 2, 5, 9 + `rg` gate (React half; server envelope N/A AST-2223) · 12 → Stage 1 edit form / Save / re-GET / `onSaved` / 409 `saveError` + Stage 2 `onSaved={load}`

## Findings

**fix-now** — Post-save state draft vs parent “re-read”

- **Location:** Stage 1 step 4 (draft init) + step 7 (PUT 200 re-init “again” per step 4)
- **Finding:** Step 4 always sets `draft.state = defaultSaveState`, including after a successful save re-fetch. Non-`state` draft keys come from refreshed `meteorite`. Parent functional scope: form **opens** with default pre-select (`CHECK_UNIQUE`) — that matches first load — but after save the modal must **re-read** stored values (parent AC 12 success path + functional scope item 7). Resetting the select to `default_save_state` while `meteorite.state` reflects the saved choice misrepresents the row and invites an accidental second save with the default state.
- **Recommendation:** Split init: **first open** → `state` from `default_save_state` (per scope item 2); **after PUT 200** → `state` from refreshed `meteorite.state` (other fields unchanged rule). Document in step 4/7 or `applyDetailPayload` flag.

**discuss** — Canon Scope gap (not scored)

- **Location:** Citations `none`
- **Finding:** `astral.ui.frontend-file-placement` plainly governs the two touched frontend paths; not on this child’s frozen list (intentional per dispatch note). No R3 row unless Archie amends scope.

**acceptable** — AC 12 component tests not in plan stages (Betty / `qa-child`).

**acceptable** — Duplicate field display in `ReportSectionList` + form block (plan ⚠️ decision).

**acceptable** — Prerequisite on AST-2223 envelope; execution contract Stage-blocked if API missing on worktree.

No D/F on an empty directive list. R6 otherwise: Files Changed ⊆ Scope; no server edits; AST-2223 contract consumption documented in UAT fitness / prerequisite.

context_tokens≈45000

---

[plan-rubric] REVIEW (Commit: e2622e00) Fix post-save state draft
