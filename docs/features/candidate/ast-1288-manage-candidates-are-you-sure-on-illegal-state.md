# AST-1288 — Manage Candidates are-you-sure on illegal state

**Linear:** [AST-1288](https://linear.app/astralcareermatch/issue/AST-1288/manage-candidates-are-you-sure-on-illegal-state-state-transition)
**Parent:** [AST-1285](https://linear.app/astralcareermatch/issue/AST-1285/state-transition-validation-for-candidates-is-broken) — State transition validation for candidates is broken
**Publish ref:** `sub/AST-1285/AST-1288-manage-candidates-are-you-sure`

When an admin on Manage Candidates chooses a registered target state that the candidate registry rejects from the current state, show an are-you-sure warning naming current → target, and only apply the hop after confirm by retrying the admin PUT with `confirm_state_override: true` (AST-1287). Cancel leaves the candidate’s prior state unchanged and skips only the state change (non-state field edits from the first attempt may already be persisted — Archie Q3). Legal hops and same-state re-saves stay quiet. This ticket does **not** own core/API transition enforcement (AST-1287).

**Depends on:** AST-1287 (`confirm_state_override` + `code: "illegal_candidate_transition"` with `from_state` / `to_state` on `PUT /api/candidates/<id>/data`). AST-1287 is User Testing; contract is on the epic worktree.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | On edit save: detect illegal-hop 400; `useUserConfirm` are-you-sure (from → to); confirm retries with `confirm_state_override: true`; cancel skips state-only | ui (React) |

## Stages

### Stage 1: Illegal-hop confirm on Manage Candidates edit save

**Done when:** From the Manage Candidates edit modal, saving an illegal registered state shows an are-you-sure dialog that names `from_state → to_state`; confirming persists that target state via a second PUT with `confirm_state_override: true`; canceling does not send the confirm flag (state unchanged) and reloads the list so non-state edits already applied are visible; an allowed target (or same current state) still saves with a single PUT and no illegal-hop dialog.

1. In `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, change `handleEditSave` from a sync function to `async function handleEditSave()`. Keep the same payload construction (first/last/pronouns/contact/state plus optional `api_key` / clear). Wire the edit `Modal` as `onSave={() => { void handleEditSave() }}` so the async path matches `handleDelete` / `handleSetDispatchTasks`.

2. Replace the current PUT `.then` chain with an `async`/`await` flow that:

   a. `const r = await api(\`/api/candidates/${editTarget.astral_candidate_id}/data\`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })`

   b. `const body = await r.json().catch(() => ({} as Record<string, unknown>))`

   c. On `r.ok`: existing success path — close edit modal, clear `editTarget`, success toast `"Candidate updated"`, `loadAll()`, `loadDispatchTaskCounts()`, `refresh()`. Return.

   d. On failure where `(body as { code?: string }).code === "illegal_candidate_transition"`:

      - Read `from_state` and `to_state` from the body (strings; fall back to `editTarget.state` and `payload.state` only if a field is missing — do not invent other states).
      - `const ok = await confirm(\`This state change is not allowed by the transition rules: ${from_state} → ${to_state}. Proceed anyway?\`, { title: "Confirm illegal state change", confirmLabel: "Change state", variant: "danger" })`
      - If `!ok` (cancel): do **not** retry with confirm. Call `loadAll()` and `loadDispatchTaskCounts()` so any non-state fields already saved on the first PUT are reflected. Set `editForm` state field back to `from_state` (and `editTarget` state’s display source stays consistent). Toast info: `"State unchanged; other fields saved if they were."` Keep the edit modal open. Return.
      - If `ok`: build `confirmPayload = { ...payload, confirm_state_override: true }` and PUT again to the same URL. On 200: same success path as (c). On failure: error toast from `body.error` / `"Update failed"`; leave modal open.

   e. On any other non-OK response (including unknown-state 400 **without** that code): error toast from `body.error || "Update failed"`; no confirm dialog; leave modal open.

3. Do **not** add a React-side `prior_states` / allowlist check. Legality is decided only by the API response code from AST-1287 (`astral.layers.ui-config-driven-business-logic`). Do **not** call core or invent a preflight endpoint.

4. Do **not** change `UserPrompt.tsx`, delete confirm, set-dispatch-tasks confirm, Clear API key confirm, company/job UIs, or any backend file. Reuse the existing `useUserConfirm()` already imported in this page.

5. Do **not** edit `tests/` or `docs/test-bible/**` — Betty owns those after Code Complete.

   ⚠️ **Decision:** Detect illegality from the first save’s structured 400 rather than pre-checking transitions in the browser. Matches AST-1287’s documented consumer contract and keeps prior_states owned by config/core.

   ⚠️ **Decision:** On cancel after an illegal-hop 400, reload the list and reset the state select to `from_state`, but leave the modal open so the admin can keep editing. Non-state fields may already be on the server; do not discard them client-side or re-PUT without confirm.

## Self-Assessment

**Scope:** `Single-Component` — one React page (`AdminManageCandidates.tsx`); no backend, no config registry, no company/job UI.

**Conf:** `high` — AST-1287 already defines the exact error code and confirm retry flag; Manage Candidates already uses `useUserConfirm` for delete / set-tasks / clear-key.

**Risk:** `Medium` — a bug that auto-sends `confirm_state_override: true` on every save would force illegal hops without consent; a bug that treats all 400s as illegal hops would spam confirms on unknown-state / validation errors.

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | Reuses `useUserConfirm` and existing PUT payload; no second confirm component |
| §2.1 / no-hardcoded-sets | No frontend prior_states mirror; state options stay from `/api/candidates/states` |
| §2.6 / core-decides-transitions | UI never writes state outside `PUT …/data`; force only via AST-1287 flag |
| `astral.layers.ui-config-driven-business-logic` | Confirm UX only; legality from API `code` |
| `pattern.ui.admin-endpoint` / require-auth | Existing admin page + `api()` client; no new route |
| §3.3 imports | Frontend → HTTP API only; no new core/data imports |
| Boundaries | No core force path; no graph repair; no company/job transition UI; no test-tree edits |

## Review

**Publish ref:** `origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure`  
**Tip:** `b4770bcb`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `b4770bcb` | Illegal-hop confirm + `confirm_state_override` retry on Manage Candidates edit save |
