# AST-1619 — Editable Entity Type control on Scheduled Actions modal

**Linear:** [AST-1619](https://linear.app/astralcareermatch/issue/AST-1619)
**Parent:** [AST-1616](https://linear.app/astralcareermatch/issue/AST-1616) — Make all fields on Add Dispatch Task modal editable
**Publish ref:** `sub/AST-1616/AST-1619-editable-entity-type-modal`

Own the Add/Edit modal UX on Scheduled Actions: replace the read-only Entity Type text input with an editable `<select>` bound to the entity keys already returned by state options, keep task-key catalog prefill, clear an invalid Input State when Entity Type changes, and include `entity_type` in create and update Save payloads. Does not own API validation or persistence (AST-1618). Candidate on Add stays context-bound / read-only.

## UAT fitness

- **AC restored:** Parent AC1 — “In Scheduled Actions → Add Task, after choosing a Task, the Entity Type control is not `readOnly` / not opacity-locked text — … shows an editable control (e.g. `<select>`) rather than `readOnly`.” Parent AC2 — “Changing Entity Type in the modal changes the Input State option list to that entity's states (company vs candidate vs job).” Parent AC7 — “Candidate on Add remains read-only / context-bound to the selected candidate.”
- **Correct outcome:** Admin can change Entity Type in Add and Edit Task modals; Input State options follow the entity currently shown; Save sends the chosen `entity_type` so the row can persist it (via AST-1618); Candidate on Add stays locked to the page-selected candidate.
- **Sibling check:** AST-1618 already accepts/persists `entity_type` on POST/PUT and validates trigger against the submitted entity. This ticket only sends the field from the modal — verified by including `entity_type` in both JSON bodies; no API/data edits. Parent AC3–AC6 remain AST-1618’s contract.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done. (N/A as failure mode — this is a read-only control unlock, not an error path.)
- **Wrong fix rejected:** Stripping `readOnly` / opacity from the existing text `<input>` without a select bound to state-options entity keys, without clearing invalid `trigger_state` on entity change, or without sending `entity_type` on Save would leave Input State / persistence misaligned with the form. Hardcoding `["candidate","company","job"]` in the page (parallel to `ENTITY_TYPES` / state-options keys) violates `astral.standards.no-hardcoded-sets`.

## Explicit scope gate

Ticket **## Scope** covers only:

- `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — modified — editable Entity Type control; include `entity_type` in create/update payloads; clear invalid `trigger_state` when `entity_type` changes.

No other files. No API/data changes. Does not make Candidate editable on Add. Does not own trigger validation or `sort_by` (AST-1618).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Editable Entity Type `<select>` from `stateOptions` keys; clear invalid Input State on entity change; send `entity_type` on POST and PUT Save | ui |

## Stage 1: Editable Entity Type + Save payload

**Done when:** `grep -n 'Entity Type' -A8 src/ui/frontend/src/pages/AdminScheduledActions.tsx` shows a `<select>` (not `readOnly` text input). Changing Entity Type in the open modal updates the Input State option list to that entity’s states from `stateOptions`, and clears `trigger_state` when the current value is not in the new list. Both Add (POST) and Edit (PUT) Save bodies include `entity_type: form.entity_type`. Candidate on Add remains the existing read-only / opacity-locked input bound to `form.candidate_id` / selected candidate. Task change still prefills `entity_type` from `allTaskKeys[key]` catalog meta and leaves the Entity Type control editable afterward.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, near `taskKeyChangePatch`, add a small helper that returns the Input State list for an entity key from the loaded options object (same shape already stored in `stateOptions`):

   ```ts
   function inputStatesForEntity(
     entityType: string,
     options: { job: string[]; company: string[]; candidate: string[] },
   ): string[] {
     if (Object.prototype.hasOwnProperty.call(options, entityType)) {
       return options[entityType as keyof typeof options]
     }
     return []
   }
   ```

   ⚠️ **Decision:** Index `stateOptions` by the selected key (same object returned by `/api/admin/dispatch_tasks/state_options` — config-backed state registries). Do **not** introduce a separate `["candidate","company","job"]` constant in this file. Entity Type `<option>` values come from `Object.keys(stateOptions)` (the API payload keys), not a parallel enum.

2. Replace the `inputStateOptions` `useMemo` body so it calls `inputStatesForEntity(form.entity_type, stateOptions)` instead of the inline ternary. Dependencies stay `[form.entity_type, stateOptions]`.

3. Replace the Entity Type row (currently `<input type="text" value={form.entity_type} readOnly style={{ opacity: 0.7 }} />`) with:

   ```tsx
   <select
     value={form.entity_type}
     onChange={e => {
       const next = e.target.value
       const nextStates = inputStatesForEntity(next, stateOptions)
       setForm({
         ...form,
         entity_type: next,
         trigger_state: nextStates.includes(form.trigger_state) ? form.trigger_state : "",
       })
     }}
   >
     <option value="">Select…</option>
     {Object.keys(stateOptions).map(k => (
       <option key={k} value={k}>{k}</option>
     ))}
   </select>
   ```

   Do not add `readOnly` or opacity lock on this control. Keep the surrounding `modal-detail-row` / `modal-detail-label` markup and label text `Entity Type`.

4. In `handleSave`, add `entity_type: form.entity_type` to **both** JSON bodies:

   - Edit `PUT` body (alongside existing `trigger_state`, `task_key`, etc.).
   - Add `POST` body (alongside existing `candidate_id`, `task_key`, `trigger_state`, etc.).

   Do not omit `entity_type` on either path. Do not change Candidate read-only behavior, Save/Cancel `btn` roles, or the modal × `icon-control`.

5. Leave Task `onChange` prefill behavior as-is for catalog defaults (`entity_type: cfg?.entity_type || ""` on Add; `taskKeyChangePatch` on Edit). Do not re-lock Entity Type after Task change.

⚠️ **Decision:** Empty Entity Type (`""`) yields no Input State options (`inputStatesForEntity` → `[]`) rather than defaulting to `job` — avoids showing the wrong entity’s states when no entity is chosen. Catalog prefill on Task select still sets a concrete entity before the admin saves.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; push each to `origin/sub/AST-1616/AST-1619-editable-entity-type-modal`.
- Do not touch `src/ui/api/**`, `src/data/**`, scheduler/claim paths, or files outside the Files Changed table.
- If `state_options` response shape or `handleSave` signatures have drifted, stop and comment on **AST-1616** with the Stage blocked template — do not invent a parallel entity-type list or call non-admin endpoints.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1619
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1616/AST-1619-editable-entity-type-modal` @ `95601ca6f6a1d1248ebb6e7b000927da89aa112c`

## Traceability

Child AC1→Stage 1 step 3 (`<select>` replaces readOnly Entity Type input); AC2→Stage 1 steps 1–3 (`inputStatesForEntity` + onChange clears invalid `trigger_state`); AC3→Stage 1 step 4 (Candidate row untouched). Save payloads add `entity_type` (parent Functional/Technical scope). Parent AC3–AC6 N/A — AST-1618 API/data sibling.

## Findings

### acceptable — Procedure — Assignee at fetch

**Location:** Linear AST-1619
**Finding:** Status `Plan Ready` but assignee was Katherine Johnson, not Joan, at `get-issue` time.
**Recommendation:** Chuckles restores implementer after posting; no plan defect.

### discuss — Plan structure — Missing Self-Assessment block

**Location:** plan doc
**Finding:** No `## Self-Assessment` / confidence section (same gap as AST-1618).
**Recommendation:** Optional add; stages + explicit scope gate + UAT fitness are otherwise complete.

### discuss — Edit task-key change — Stale Input State (pre-existing)

**Location:** `taskKeyChangePatch` / Task `onChange` Edit branch
**Finding:** Add path resets `trigger_state` on Task change; Edit path only patches `entity_type` via `taskKeyChangePatch` and may leave a `trigger_state` invalid for the new catalog entity until the admin changes Entity Type or Input State manually.
**Recommendation:** Out of child AC (entity-change clearing is covered). Optional follow-up if UAT hits Edit+Task-change; not blocking this ticket.

**Considered:** (in-session — corpus present; cited ui patterns/statutes + universal orch.* conform; no `violates`)

context_tokens≈45000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1616/AST-1619-editable-entity-type-modal`
**Tip:** `655144b9`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `655144b9` | Editable Entity Type `<select>` from `stateOptions`; clear invalid Input State; POST/PUT send `entity_type` |
