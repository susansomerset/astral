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

## Radia review

# Radia review — AST-1619

**Publish ref:** `origin/sub/AST-1616/AST-1619-editable-entity-type-modal` @ `bfc19678`  
**Diff baseline:** `origin/dev...origin/sub/AST-1616/AST-1619-editable-entity-type-modal` (11 paths; layers: `ui`, `data`, `docs`)  
**AST-1619 product footprint:** `655144b9` + `2c554f69` — 1 product file (`AdminScheduledActions.tsx`) + frontend component tests + bible  
**Internal grade:** CLEAN

---

```
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1619
**Publish ref:** origin/sub/AST-1616/AST-1619-editable-entity-type-modal @ bfc19678
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent grading paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no do_task changes |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grade-vector paths |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch claim paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch-id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/process helpers |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity_agent_responses |
| `astral.config.config-source-of-truth` | scoped | conforms | entity keys/options from `/state_options` + task-key catalog meta |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no seed paths |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run-next changes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | `docs/features/dispatcher/ast-1619-editable-entity-type-modal.md` |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Radia read-only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | tests + Betty bible manifest aligned |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no core/external edits |
| `astral.layers.import-direction` | scoped | conforms | frontend page only; no layer violations |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | entity options from `stateOptions` API keys; no hardcoded entity enum |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no render/verdict |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no new API routes (sibling AST-1618 in branch diff) |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed overrides |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed hot-path |
| `astral.seed.define-approved` | scoped | not-applicable | no define/seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no AST-1619 data edits (sibling in branch diff only) |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no AST-1619 DB edits |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug emission |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | small `inputStatesForEntity` helper; localized modal change |
| `astral.standards.in-scope-only` | scoped | conforms | AST-1619 commits touch only planned `AdminScheduledActions.tsx` (+ tests/docs) |
| `astral.standards.logging-via-utils` | scoped | conforms | no new logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | ticket id in test comments only |
| `astral.standards.no-cross-contamination` | scoped | conforms | no unrelated module rewrites in AST-1619 commits |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | `Object.keys(stateOptions)` for entity `<option>` values; plan anti-pattern avoided |
| `astral.standards.public-then-helpers` | scoped | conforms | helper placed above component; modal logic unchanged structure |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no data/utils changes in AST-1619 commits |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job prior-state enforcement |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no daisy-chain runtime |
| `astral.ui.frontend-file-placement` | scoped | conforms | change in existing routed page under `src/ui/frontend/src/pages/` |
| `astral.ui.naming-conventions` | scoped | conforms | no new misnamed modules |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1619)` at tip |
| `orch.git.commit-vocabulary` | universal | conforms | `code`/`test`/`docs` prefixes on AST-1619 commits |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub branch under parent |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1616/AST-1619-...` |
| `orch.git.merge-on-checkout` | universal | conforms | no merge-gate evidence in AST-1619 commits |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear stage commits |
| `orch.git.no-dev-agent-branches` | universal | conforms | engineer sub branch |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in `astral-AST-1616` |
| `orch.git.three-permanent-branches` | universal | conforms | no main/master/dev writes |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no unresolved product forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 Done-when satisfied |
| `orch.pipeline.project-scoped-queues` | universal | conforms | UI-only sibling to AST-1618 |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | `pages.md` manifest + combobox-index regression notes |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | n/a to diff |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine assignee; review recommend-only |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path commits |

**Sweep count:** 65 active statutes scored in-session (0 `violates`, 0 `needs-discussion` on statutes).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | plan cites no `canon/patterns/**` ids |

## Plan adherence

Stage 1 lands per plan and UAT fitness:

| Plan step | Status |
|-----------|--------|
| `inputStatesForEntity` helper indexing `stateOptions` | Done — matches plan signature + `hasOwnProperty` guard |
| `inputStateOptions` useMemo delegates to helper | Done |
| Entity Type `<select>` replaces readOnly `<input>` | Done — no `readOnly`/opacity lock |
| onChange clears invalid `trigger_state` | Done — `nextStates.includes(...) ? keep : ""` |
| POST + PUT include `entity_type: form.entity_type` | Done — both `handleSave` branches |
| Candidate on Add stays readOnly | Done — unchanged row; test asserts |
| Task prefill keeps entity editable | Done — Add `onChange` still sets `cfg?.entity_type`; Edit uses `taskKeyChangePatch` |
| No API/data edits | Done in AST-1619 commits (sibling AST-1618 present in branch diff vs `dev`, not in AST-1619 commits) |
| Estimate 2 | Fits — single TSX file + targeted Vitest |

**Traceability:** AC1→select control; AC2→entity change swaps Input State + clears invalid trigger; AC3→Candidate readOnly; Save payloads→POST/PUT `entity_type` tests.

## Findings

### advisory — Empty Entity Type on Save

**Location:** `AdminScheduledActions.tsx` — Entity Type `<option value="">Select…</option>` + unconditional `entity_type: form.entity_type` in POST/PUT  
**Finding:** Admin can choose empty entity and Save; body sends `entity_type: ""` → AST-1618 returns 400 (`entity_type must be non-empty when provided`). Toast surfaces via existing `readApiError` path. Plan explicitly allows both the empty option and always sending `entity_type`.  
**Recommendation:** UAT note only; optional follow-up: omit key when `""`, disable Save, or inline validation — not blocking if normal flow is Task-select prefill.

### advisory — Stacked sibling in three-dot diff

**Location:** branch diff vs `origin/dev`  
**Finding:** Three-dot diff includes AST-1618 product/tests/docs (not yet on `origin/dev`) alongside AST-1619. AST-1619's own commits are scope-clean (4 files). Expected mid-epic stacking until `merge-child` / ftr rollup.  
**Recommendation:** Chuckles/`merge-child` hygiene only; not an AST-1619 scope violation.

### advisory — Edit + Task-key change stale Input State (Joan discuss, pre-existing)

**Location:** `taskKeyChangePatch` Edit branch  
**Finding:** Edit Task change updates catalog `entity_type` but may leave `trigger_state` invalid for new entity until admin changes Entity Type or Input State. Joan flagged as out-of-AC / optional follow-up.  
**Recommendation:** Defer unless UAT hits Edit+Task-change path; not introduced by this ticket.

## What's solid

- Config-driven entity list via `Object.keys(stateOptions)` — avoids parallel `ENTITY_TYPES` hardcoding (plan UAT fitness “wrong fix rejected”).
- `inputStatesForEntity` replaces brittle inline ternary; empty entity → `[]` options per plan decision.
- Betty manifest covers AC1–AC3 + POST/PUT payload asserts; combobox-index regressions revised for inserted Entity Type select (Task=0, Entity=1, Input State=2).
- Sibling boundary respected: no API/data edits in AST-1619 commits; persistence delegated to AST-1618.

## Frame diff

(none) — AST-1619 description frame, scope gate, and UAT fitness match the implementation; parent AC1/AC2/AC7 restored without scope creep in product commits.

## Notes

- Joan plan-rubric APPROVED; no Excluded-statute list → no stragglers.
- Tip `bfc19678` is merge-tests; product `655144b9`, tests `2c554f69`.
- C7 artifact complete; recommend Chuckles append + **Review Posted**.

context_tokens≈38000
