<!-- linear-archive: AST-1288 archived 2026-08-19 -->

## Linear archive (AST-1288)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1288/manage-candidates-are-you-sure-on-illegal-state-state-transition  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1285 — State transition validation for candidates is broken  
**Blocked by / blocks / related:** parent: AST-1285

### Description

## What this implements

When an admin selects an illegal target state on Manage Candidates, show the are-you-sure warning (current → target) and only proceed on confirm using the override path from AST-1287; on cancel, leave state unchanged and skip only the state change (non-state field edits may still apply — Archie Q3). Does **not** own core transition enforcement (AST-1287).

## In scope

- [X] `pattern.ui.admin-endpoint` — Manage Candidates edit save on existing admin-gated candidate data PUT
- [X] `astral.layers.ui-config-driven-business-logic` — legality from API `illegal_candidate_transition` code; React does not mirror `prior_states`
- [X] `astral.idioms.require-auth-on-protected-endpoints` — existing authed `api()` client on admin page (no new public mutator)
- [X] `astral.standards.no-hardcoded-sets` — no frontend allowlist for legal hops; state options stay from `/api/candidates/states`
- [X] `astral.standards.in-scope-only` — only `AdminManageCandidates.tsx` edit-save path

## Considered but excluded

- [X] `pattern.state.entity-state-transitions` / core `force` / `confirm_state_override` API — owned by AST-1287
- [X] `astral.config.config-source-of-truth` graph repair / loosening `prior_states` — out of epic (Archie Q1)
- [X] Company/job transition UI — out of boundaries
- [X] Preflight legality endpoint or React `prior_states` duplicate — rejected; detect via first-save 400
- [X] `tests/` / `docs/test-bible/**` — Betty after Code Complete

## Acceptance criteria

1. [X] From Manage Candidates, an admin who chooses a registered target state that the registry rejects from the current state sees an are-you-sure warning that identifies from → to before the state changes.
2. [X] Confirming the warning results in the candidate persisting in the chosen target state; canceling leaves the prior state unchanged.
3. [X] An admin choosing an allowed target state still saves without that warning (aside from unrelated existing confirms).

## Boundaries

* Does not own admin confirm-override core/API path (AST-1287).
* Does not redesign candidate lifecycle or prior_states graph.
* Does not change company/job transition UI.

## Notes for planning

After AST-1287. Use existing user-confirm patterns on Manage Candidates. Cancel = skip state only.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1285-state-transition-validation`, child `sub/AST-1285/AST-1288-manage-candidates-are-you-sure`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-08T21:08:14.089Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed on `origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure`: commit `17b67fd4` (`Merge remote-tracking branch 'origin/dev' into sub/…`). @Hedy Lamarr — rebuild/republish the sub tip as a linear history from `origin/ftr/AST-1285-state-transition-validation` without that pull-merge (keep the AST-1288 plan/code/test/merge-tests/docs/resolve sequence). Do not merge `origin/dev` into the sub.

— Chuckles

#### radia — 2026-08-08T21:06:33.827Z
[code-rubric] revision=2

**Rubric:** code-rubric.v2
**Ticket:** AST-1288
**Publish ref:** `origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure` @ `a2a274ac` (this ticket's own diff; doc-only `32037232` review append on top)
**Overall:** DISCUSS

## Plan adherence

- Diff matches the Files Changed table and the single stage exactly, including both `⚠️ Decision` notes (detect illegality via first-save 400, not a preflight endpoint; on cancel, reload + reset the state select but leave the modal open).
- Self-Assessment `Scope: Single-Component` / `Conf: high` matches the diff's real footprint.
- Joan's attached `[plan-rubric] revision=1` verdict is **APPROVED**; her two discuss items are carried forward below (shipped code matches what she reviewed, unchanged).
- `origin/dev...origin/<publish-ref>` also carries AST-1287's not-yet-landed diff. Confirmed byte-identical to AST-1287's own tip (post-`resolve-child`), so it is not re-scored here — this review covers only `AdminManageCandidates.tsx` + its test + this ticket's own plan/bible entries.

## Findings

- **discuss — carried from Joan's plan-rubric verdict:** on cancel, an `api_key` edit submitted in the same save as the illegal state is dropped (AST-1287's illegal-hop 400 returns before the key-write block), and the cancel toast doesn't surface that. Joan scored this non-blocking with two remediation paths (re-PUT minus `state` here, or reorder the key-write in AST-1287's file via the parent). No new finding — shipped code matches the approved plan.
- **discuss — carried from Joan's plan-rubric verdict:** leaving the edit modal open after cancel can produce a second "discard changes?" prompt from `Modal`'s dirty-tracking on close, even though non-state fields already saved. Same status — flagged by Joan, plan approved anyway, unchanged in the diff.

No fix-now findings. Full 64-statute active set (17 universal + 47 scoped) scored in-session against this ticket's own diff; no `violates`. No stragglers — this ticket's Considered-but-excluded list (core force path, `prior_states` graph repair, company/job UI, preflight endpoint, test-tree) stayed untouched.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.admin-endpoint` | conforms | Confirm UX added to the existing admin-gated page/`api()` client; no new route; legality stays server-resolved |

## Frame diff

(none — ticket description AC/scope table already accurate)

**What's solid:** No frontend `prior_states` mirror or preflight endpoint — legality decided purely by the API's `code` field. `useUserConfirm()` reused, no new confirm component. Retry re-sends the full payload (self-heals an API-key edit on confirm). Unknown-state 400s correctly skip the confirm dialog (dedicated test). `npx eslint` and `npx tsc -b --noEmit` both clean on the touched file. Engineer/Betty test-tree boundary holds (single `merge-tests(AST-1288)` SHA carries test-tree changes; `code(AST-1288)` touches only the page file). Test coverage matches all 4 plan branches.

**Recommended actions:** None blocking. The two carried-forward discuss items are Joan's to resolve at the parent/AST-1287 level if Susan wants them addressed; not required for this child.

Full review also appended as `docs(AST-1288): Radia review — discuss` on `origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure` @ `32037232`.

context_tokens≈58000

— Radia

#### betty — 2026-08-08T21:01:12.279Z
## QA test manifest

`origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure` @ `a2a274ac` (`merge-tests(AST-1288): origin/tests 3fd2dd328d1a4e7e33928cce187b0a35e128c7a7`)

### 1. Existing coverage (bible-backed)
1. `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` — full file (routed page §6c; edit/save/delete/confirm paths still green with async `handleEditSave`)

### 2. Broken / obsolete
None — existing PUT mocks still 200; no prior_states mirror in React to revise.

### 3. Gaps (new this pass)
1. `AST-1288: illegal hop shows from→to confirm; confirm retries with override`
2. `AST-1288: cancel illegal confirm leaves state unchanged and does not send override`
3. `AST-1288: legal hop saves without illegal-state confirm`
4. `AST-1288: unknown-state 400 does not open illegal confirm`

**Integration:** none.

### Run
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx \
  -t "AST-1288"
```

Full-file regression also fine:
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

### Bible (on publish ref)
- `docs/test-bible/frontend/pages.md` shasum `a7bf01122a8f7760e3c49b44c93d9025cda48676`

#### joan — 2026-08-08T20:57:17.346Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1288
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure` @ `5debe43c`

## Traceability

AC1→S1.2d; AC2→S1.2d (confirm retry / cancel branch); AC3→S1.2c plus the same-state skip already in the AST-1287 API. No unmapped AC, no orphan stage. Parent AC4–AC7 sit with AST-1287 and the plan quotes that boundary rather than reaching for them.

**Considered:** 18 universal + 14 scoped active statutes on layer `ui`, path `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, change_type `modify`; the rest of the scoped corpus excluded on layer or path (no core, data, external, utils, scripts, or docs paths in the Files Changed table). All considered statutes score `conforms`. `pattern.ui.admin-endpoint` resolves as `status: approved` and the plan matches its shape — no new route, existing admin-gated PUT, existing authed `api()` client.

## Findings

**discuss — an API-key edit in the same save is dropped on the illegal-hop attempt, and the cancel toast implies otherwise.** In the landed AST-1287 code, the illegal-hop response returns at `src/ui/api/api_candidate.py:250`, which is before the `api_key` block at `:258`. So a save that carries both a key change (or the clear-key tick) and an illegal state persists the `candidate_data` fields but never applies the key. On confirm this self-heals, because the retry re-sends the whole payload. On cancel it does not: the plan's toast says "State unchanged; other fields saved if they were", the list reloads, and the key edit is gone with nothing on screen to say so — keys are not rendered in the list, so it is invisible.

The drop itself is pre-existing (any 400 from that block has always returned before the key write), which is why this is not a blocker on your plan. What is new is the message telling the operator their other fields made it. Cheapest honest fix inside your file: on cancel, when the payload carried `api_key`, re-PUT the same payload minus `state` so the key lands, then toast; or at minimum name the field that did not apply. If you would rather reorder `update_candidate_data` so the key write precedes the state block, that is AST-1287's file — take it to the parent for Chuckles instead of pulling it into this child.

**discuss — leaving the edit modal open after cancel leaves the dirty flag set.** `Modal` auto-detects dirty from any input event (`touchedRef`) and this page passes no `dirty` prop, so after the cancel branch the operator gets a second "You have unsaved changes. Discard them?" prompt when they eventually close the modal — even though everything except the state was already saved. Not an AC break, and keeping the modal open is a defensible choice, but two confirms stacked on one save is a rough moment. Worth deciding deliberately rather than discovering in UAT.

**discuss — the epic's proposed override pattern is still undrafted in canon.** Carried from the AST-1287 review and unchanged: "admin confirmed prior-states override" has no file under `canon/patterns/**`. Your plan correctly cites only `pattern.ui.admin-endpoint` and treats the rest as AST-1287's, so nothing is required of you here.

**acceptable — the dependency claim checks out against the tree, not just the sibling's plan.** `src/ui/api/api_candidate.py:240–257` has the same-state skip, the `IllegalCandidateTransition` catch returning `code: "illegal_candidate_transition"` with `from_state` / `to_state`, and a separate plain-`ValueError` 400 without that code. So every branch your Stage 1 keys off exists as described, including the unknown-state case that must not offer confirm-to-invent.

**acceptable — confirm-over-modal is already proven on this page.** The Clear API key confirm at line 449 fires from inside the open edit modal today, so raising the are-you-sure over the same modal is an established shape here rather than a new stacking risk.

**acceptable — the component APIs match what the plan calls.** `useUserConfirm` is imported and bound at line 116 and accepts exactly the `title` / `confirmLabel` / `variant: "danger"` options you pass; the toast `info` variant exists and is already used on this page; and `Modal.onSave` is typed `() => void`, so the `void handleEditSave()` wrapper is safe (and matches the async style of `handleDelete` and `handleSetDispatchTasks`).

**acceptable — detecting illegality from the 400 is the right call.** Rejecting a preflight endpoint and refusing to mirror `prior_states` in React keeps legality where `astral.layers.ui-config-driven-business-logic` and `astral.standards.no-hardcoded-sets` want it, and the state options still come from `/api/candidates/states`.

**acceptable — self-assessment is honest.** `Single-Component` matches one React file, and the `Medium` risk line names the two failure modes that actually matter: an always-on confirm flag forcing hops without consent, and treating every 400 as an illegal hop.

context_tokens≈145000

— Joan

#### hedy — 2026-08-08T20:53:24.628Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1285/AST-1288-manage-candidates-are-you-sure/docs/features/candidate/ast-1288-manage-candidates-are-you-sure-on-illegal-state.md

`origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure` @ `5debe43c`

**Scope:** Single-Component — only `AdminManageCandidates.tsx` edit-save; no backend.

**Conf:** high — consumes AST-1287’s `illegal_candidate_transition` / `confirm_state_override` contract; reuses existing `useUserConfirm`.

**Risk:** Medium — accidental always-on confirm flag would force hops without consent; mistaking every 400 for illegal-hop would spam confirms.

---

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

## Radia review

[code-rubric] revision=2

**Rubric:** code-rubric.v2
**Publish ref tip:** `a2a274ac`
**Overall:** DISCUSS

**Full-set sweep:** all 64 active statutes scored in-session (17 universal + 47 scoped) against this ticket's own contribution. `origin/dev...origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure` also carries AST-1287's not-yet-landed diff (`src/core/candidate.py`, `src/ui/api/api_candidate.py`, their tests/bible) — confirmed byte-identical between `origin/sub/AST-1285/AST-1287-admin-confirm-override` (current tip, post-`resolve-child`) and this branch, so that content is not re-scored here; only `AdminManageCandidates.tsx` + its test + this ticket's plan/bible entries are this ticket's diff. No `violates`.

**What's solid:** No frontend `prior_states` mirror or preflight endpoint — legality is decided purely by the API's `code: "illegal_candidate_transition"` (matches `astral.layers.ui-config-driven-business-logic` / `astral.standards.no-hardcoded-sets`, both cited "In scope"). `useUserConfirm()` is the same hook already wired for delete / set-tasks / clear-key on this page — no new confirm component. `from_state`/`to_state` read from the response body with a narrow fallback only when a field is missing (no state invention). The retry path re-sends the full payload with `confirm_state_override: true` rather than a partial PUT, so an API-key edit in the same save self-heals on confirm. Unknown-state 400s (no `code` field) correctly fall through to the plain error toast with no confirm dialog — verified by the dedicated `NOT_A_STATE` test. `Modal.onSave={() => { void handleEditSave() }}` matches the existing async wrapper style used by `handleDelete` / `handleSetDispatchTasks`. `npx eslint` and `npx tsc -b --noEmit` both clean on the touched file. Engineer/Betty test-tree boundary holds — `code(AST-1288)` touches only `AdminManageCandidates.tsx`; `test(AST-1288)` (merged via the single `merge-tests(AST-1288)` SHA) touches only the test file + bible. Test coverage matches all 4 plan branches (confirm-retry, cancel, legal-quiet, unknown-state-quiet).

**Findings**

- **discuss — carried from Joan's plan-rubric verdict, unresolved by design:** on cancel, an `api_key` edit submitted in the same save as the illegal state is dropped (the AST-1287 illegal-hop 400 returns before the key-write block in `update_candidate_data`) and the cancel toast ("other fields saved if they were") doesn't surface that. Joan scored this `discuss`/non-blocking and gave two remediation paths (re-PUT minus `state` on cancel here, or reorder the key-write in AST-1287's file — the latter needs Chuckles/parent). Shipped code matches the approved plan exactly; flagging forward per C6 §5c rather than re-litigating — no new finding beyond Joan's.
- **discuss — carried from Joan's plan-rubric verdict:** leaving the edit modal open after cancel means `Modal`'s dirty-tracking can produce a second "discard changes?" prompt on close even though the non-state fields already saved. Same status as above — Joan flagged, plan approved anyway, shipped code unchanged from what she reviewed.

No fix-now findings; no new stragglers (this ticket's Considered-but-excluded list — `pattern.state.entity-state-transitions` / core force path, `prior_states` graph repair, company/job UI, preflight endpoint, test-tree — all correctly stayed untouched in the diff).

**Pattern conformance:**

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.admin-endpoint` | conforms | Confirm UX added to the existing admin-gated page/`api()` client; no new route; legality stays server-resolved |

**Plan adherence:** Diff matches the Files Changed table and the single stage exactly, including both `⚠️ Decision` notes (detect via first-save 400, not preflight; reload + reset state select on cancel but leave modal open). Self-Assessment `Scope: Single-Component` / `Conf: high` matches the diff's real footprint. Joan's attached `[plan-rubric] revision=1` verdict is **APPROVED** with the two discuss items carried forward above; no round 2 was required and none is introduced by this review.

**Cross-ticket boundary:** No core/API changes (AST-1287's file untouched by this ticket, confirmed identical to its own tip); no company/job transition UI; no `tests/`/`docs/test-bible/**` edits by the engineer commit.

## Frame diff

(none — ticket description AC/scope table already accurate)

context_tokens≈54000

— Radia

## Resolution

**Date:** 2026-08-08  
**Review tip:** `32037232` (`docs(AST-1288): Radia review — discuss`)

- **fix-now:** none — no product changes.
- **discuss (api_key drop on cancel + toast):** deferred per Radia recommended actions — Joan/Radia scored non-blocking; remediation is parent/AST-1287 key-write order or a future UI follow-up, not required for this child. Plan toast and cancel path left as approved.
- **discuss (modal dirty after cancel):** deferred same way — plan deliberately keeps the modal open; second discard prompt accepted for UAT awareness, not changed here.
