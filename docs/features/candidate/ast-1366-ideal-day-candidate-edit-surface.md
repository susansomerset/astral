<!-- linear-archive: AST-1366 archived 2026-08-31 -->

## Linear archive (AST-1366)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1366/ideal-day-candidate-edit-surface-add-ideal-day-to-the-set-of-candidate  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1360 — Add "ideal_day" to the set of candidate context (strengths, priorities, etc.)  
**Blocked by / blocks / related:** parent: AST-1360

### Description

## What this implements

Ship Candidate nav + Ideal Day edit page (peer of Strengths/Priorities) wired to the library key from the Ideal Day library + token sibling.

## Citations

`pattern.config.config-block`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`.

## Acceptance criteria

- [X] 2. Ideal Day is reachable from Candidate navigation (label/path peer of Strengths) and editable with the same save semantics as the other context list pages.

## Boundaries

Does **not** own Topic Menu informs or craft prompts. After Ideal Day library + token.

## Notes for planning

Parent AST-1360. Estimate: 2. After #1.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1360-ideal-day-candidate-context`,
child `sub/AST-1360/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-14T19:07:36.432Z
[code-rubric] PROCEED (Commit: 4cdd9cb7) nav page route peer

#### betty — 2026-08-14T19:05:00.306Z
`origin/sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface` @ `4cdd9cb7` · Ideal Day page tests

#### joan — 2026-08-14T18:57:16.352Z
[plan-rubric] PROCEED (Commit: 329b52c9618915d62126f486c8cf5d2995a668ab) nav page route peer

#### hedy — 2026-08-14T18:55:35.801Z
`origin/sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface` @ `329b52c9618915d62126f486c8cf5d2995a668ab` · Ideal Day edit plan

---

# AST-1366 — Ideal Day Candidate edit surface

**Linear:** [AST-1366](https://linear.app/astralcareermatch/issue/AST-1366/ideal-day-candidate-edit-surface-add-ideal-day-to-the-set-of-candidate)
**Parent:** [AST-1360](https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc) — Add `ideal_day` to the set of candidate context (strengths, priorities, etc.)
**Publish ref:** `sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface`

Ship Candidate nav + Ideal Day edit page as a peer of Strengths / Priorities / Deal Breakers / Backstory, wired to the `ideal_day` library key from AST-1365. Reuse `ContextTextPage` and the existing `PUT /api/candidates/<id>/data` merge path — no new save API. This ticket does **not** own Topic Menu informs / Estelle allowlists (AST-1367) or JD/DO/LIKE craft prompt text (AST-1368). Library vocabulary, `{$IDEAL_DAY}` token, and completeness gate already land via AST-1365 on `origin/ftr/AST-1360-ideal-day-candidate-context` (merge that ftr before coding).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add Ideal Day item to Candidate group in `NAV_CONFIG` | utils |
| `src/ui/frontend/src/pages/CandidateIdealDay.tsx` | New thin `ContextTextPage` wrapper (`contextKey="ideal_day"`) | ui |
| `src/ui/frontend/src/routes.tsx` | Import Ideal Day page; add `candidate/ideal_day` route (keep SYNC comment with `NAV_CONFIG`) | ui |

**Out of scope (do not touch):**

| File / area | Owner |
|-------------|--------|
| `CANDIDATE_LIBRARY_CONFIG`, `TOKEN_SOURCES["IDEAL_DAY"]`, `check_context_complete` / `context_completeness_keys` | AST-1365 (already on parent ftr) |
| `TOPIC_MENU_CONFIG["informs"]`, `TOPIC_MENU_GEN_CONFIG` packet/patch allowlists | AST-1367 |
| `data/admin/agent_task.json` / craft rubric prompt bodies for JD/DO/LIKE | AST-1368 |
| `DATA_SHAPES` Profile detail | N/A — peer context pages are not Profile shape fields (same as Strengths today) |
| `ContextTextPage.tsx` itself | unchanged — Ideal Day is another caller |
| Candidate state machine / survey unlock gates | Parent: no new state transitions for Ideal Day |
| Migrations / backfill | Parent: empty until edited or Topic Menu writes |

## Stages

### Stage 1: Nav + Ideal Day page + route

**Done when:** Candidate sidebar shows **Ideal Day** (path `/candidate/ideal_day`) between Backstory and Writing Preferences; navigating there loads a textarea page titled Ideal Day; Save persists `candidate_data.context.ideal_day` via the same `PUT .../data` merge as Strengths and reload shows the prose.

1. In `src/utils/config.py`, inside `NAV_CONFIG`, in the Candidate group `items` list, insert Ideal Day **immediately after** the Backstory item and **before** Writing Preferences:

```python
{"label": "Backstory", "path": "/candidate/backstory"},
{"label": "Ideal Day", "path": "/candidate/ideal_day"},
{"label": "Writing Preferences", "path": "/candidate/writing_preferences"},
```

   No `enabled` / `visible` on the item — Strengths / Priorities / Deal Breakers / Backstory have none; Ideal Day matches.

   ⚠️ **Decision:** Nav placement after Backstory keeps the five gated completeness-context pages contiguous (Strengths → … → Backstory → Ideal Day) before ungated Writing Preferences. Path segment `ideal_day` matches the library key (same snake_case pattern as `deal_breakers`).

2. Create `src/ui/frontend/src/pages/CandidateIdealDay.tsx` as a one-liner peer of `CandidateStrengths.tsx`:

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function IdealDay() { return <ContextTextPage title="Ideal Day" contextKey="ideal_day" /> }
```

   Do **not** edit `ContextTextPage.tsx`. Save/load already deep-merges `context.<key>` through `PUT /api/candidates/<id>/data`.

3. In `src/ui/frontend/src/routes.tsx`:

   - Add import with the other Candidate page imports:
     `import IdealDay from "./pages/CandidateIdealDay"`
   - Add route next to the other context routes, immediately after Backstory and before Writing Preferences:
     `{ path: "candidate/ideal_day", element: <IdealDay /> },`

   Honor the file header SYNC comment: every route must have a matching `NAV_CONFIG` item (step 1).

4. Do **not** change Flask API modules — no new endpoint. Do **not** change `docs/features/candidate/CANDIDATE_DATA_MODEL.md` (AST-1365 already documents `context.ideal_day`).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1366
**Overall:** APPROVED
**Publish ref:** `sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface` @ `329b52c9618915d62126f486c8cf5d2995a668ab`

## Traceability
AC2→Stage 1 (`NAV_CONFIG` Ideal Day item + `CandidateIdealDay.tsx` `ContextTextPage` wrapper + `routes.tsx` `candidate/ideal_day` route); save/load via existing `PUT /api/candidates/<id>/data` merge (same as Strengths/Backstory).

### Findings

**acceptable** — Build depends on AST-1365 library key on `origin/ftr/AST-1360-ideal-day-candidate-context`; plan states merge-before-code (ftr tip already has `ideal_day` / `IDEAL_DAY`). Operational, not a plan gap.

**acceptable** — No frontend test touch in plan; `ContextTextPage` pattern is unchanged — Betty/`test-child` scope.

**acceptable** — Linear assignee is Hedy (not Joan); Chuckles spawn — no plan impact.

context_tokens≈48000

---

[plan-rubric] PROCEED (Commit: 329b52c9618915d62126f486c8cf5d2995a668ab) nav page route peer

## Review (build stub)

**Built:** `astral-AST-1360` @ `7251385e` on `origin/sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `329b52c9` | Plan doc |
| 1 | `7251385e` | `NAV_CONFIG` Ideal Day + `CandidateIdealDay.tsx` + `routes.tsx` |

**Verify:** `python3 -m py_compile` on `src/utils/config.py` — pass; `npx tsc -b --noEmit` in `src/ui/frontend` — pass.

**Note for Betty:** Thin `ContextTextPage` peer only — no API/save-path change; existing ContextTextPage coverage should still hold.

## Radia review

# Radia review — AST-1366

**Ticket:** AST-1366  
**Parent:** AST-1360  
**Publish ref:** `origin/sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface` @ `4cdd9cb748ecc7d24be76606c95966a555066fbc`  
**Diff baseline:** `origin/dev...origin/sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface` (16 files, +827/−8)  
**Status gate:** Tests Passed (spawn prompt; trusted)  
**Relation:** `blockedBy AST-1365` — prerequisite satisfied on branch tip (`ideal_day` library + `{$IDEAL_DAY}` present from AST-1365 ancestry)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1366  
**Publish ref:** `4cdd9cb748ecc7d24be76606c95966a555066fbc`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent grading changes |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` routing |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no rubric vectors |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch ids |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no agent-response persistence |
| `astral.config.config-source-of-truth` | scoped | conforms | nav item in `NAV_CONFIG`; 1366 does not duplicate library/token config |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run-next edits |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | `ast-1366-ideal-day-candidate-edit-surface.md` present |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty merge is test-tree only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | `code(AST-1366)` touches `src/` only; tests via `merge-tests` |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no external layer |
| `astral.layers.import-direction` | scoped | conforms | no new layer bends in 1366 commit |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | nav in `NAV_CONFIG`; page is thin `ContextTextPage` caller |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult render |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API/auth changes |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON in 1366 commit |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed hot-path |
| `astral.seed.define-approved` | scoped | not-applicable | no DEFINE seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no `src/data/` changes in 1366 commit |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no schema |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug logging |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | 3-file, 5-line product commit |
| `astral.standards.in-scope-only` | scoped | conforms | nav + page + route only; no Topic Menu / craft / API |
| `astral.standards.logging-via-utils` | scoped | conforms | no new logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | domain keys `ideal_day`, `Ideal Day`; ticket refs in docs/tests only |
| `astral.standards.no-cross-contamination` | scoped | conforms | no AST-1367/1368 surfaces touched in 1366 code commit |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | nav path/label in config, not inline React rules |
| `astral.standards.public-then-helpers` | scoped | conforms | thin page export matches peer pattern |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils→data imports |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run loop |
| `astral.ui.frontend-file-placement` | scoped | conforms | `CandidateIdealDay.tsx` in flat `pages/` |
| `astral.ui.naming-conventions` | scoped | conforms | peer naming matches `CandidateStrengths.tsx` pattern |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | tip is `merge-tests(AST-1366)` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `docs` / `test` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub-branch topology |
| `orch.git.ftr-sub-topology` | universal | conforms | child `sub/AST-1360/...` |
| `orch.git.merge-on-checkout` | universal | conforms | AST-1365 prerequisite on ancestry |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear stack |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/...` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1360 epic |
| `orch.git.three-permanent-branches` | universal | conforms | diff vs `origin/dev` |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | implementation matches staged plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | page + nav tests + bible via Betty |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | n/a |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path product commits |

**Active set count:** 64 rows (per `canon/statutes/README.md` harvested table). No `violates` or `needs-discussion` rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Plan cites `ContextTextPage` peer pattern in prose only; no `canon/patterns/**` id |

## Plan adherence

**AST-1366 product commit (`7251385e`):** exactly three files, five insertions — matches plan Stage 1.

| Plan item | Tip state |
|-----------|-----------|
| `NAV_CONFIG` Ideal Day after Backstory, before Writing Preferences | ✓ `{"label": "Ideal Day", "path": "/candidate/ideal_day"}` |
| `CandidateIdealDay.tsx` thin `ContextTextPage` wrapper | ✓ matches `CandidateStrengths.tsx` one-liner shape |
| `routes.tsx` import + `candidate/ideal_day` route after Backstory | ✓ SYNC comment honored |
| No `ContextTextPage.tsx` edit | ✓ unchanged in 1366 commit |
| No Flask/API changes | ✓ |
| No `CANDIDATE_DATA_MODEL.md` edit in 1366 commit | ✓ (1365 doc change on branch ancestry only) |
| No Topic Menu / craft / `DATA_SHAPES` | ✓ |

**Estimate (2):** Footprint matches — nav line + page + route.

**AST-1365 dependency:** Branch ancestry includes AST-1365 library/token/gate (`ideal_day` in `context_keys`, `TOKEN_SOURCES["IDEAL_DAY"]`). `blockedBy` satisfied for build/review on this tip.

**Test manifest:** Betty `test_CandidateIdealDay.test.tsx` (§6c render + PUT save), `TestAst1366IdealDayCandidateNav`, `ContextTextPage` regression (mock harness fix only). Bible entries aligned.

**Joan straggler (C4):** Plan-rubric APPROVED attached; no Excluded-statute list.

## Findings

### fix-now

*(none)*

### discuss

*(none)*

### advisory

- **Three-dot diff breadth:** Full diff vs `origin/dev` also carries AST-1365 product/docs/tests and (via `merge-tests` ancestry) AST-1368 seed tests in `test_repo_admin_json.py` — rollup on shared tests tip, not AST-1366 product scope. Epic merge/UAT should treat siblings independently.
- **UAT:** Ideal Day page is live once this lands with AST-1365 token/gate; operators can now fill `context.ideal_day` via UI (completeness gate from 1365 will start passing when prose is saved).

## What’s solid

- Textbook peer implementation: same `ContextTextPage` pattern as Strengths/Backstory with config-owned nav.
- `routes.tsx` / `NAV_CONFIG` kept in sync per file header contract.
- Betty page test proves PUT merge path for `context.ideal_day` without inventing new API surface.
- Surgical product commit — no scope creep into siblings.

## Frame diff

**AST-1366 frame:** Candidate nav + edit page + route — **matches**.

**Rollup note:** three-dot diff vs `origin/dev` includes AST-1365 prerequisite stack (required for `contextKey="ideal_day"` to resolve); not part of AST-1366’s planned Files Changed but expected on branch tip.

## Notes

- §5f / §5g not triggered.
- Build stub reports `py_compile` + `tsc -b --noEmit` pass.
- C7 artifact complete.

context_tokens≈38000

---

```
[code-rubric] PROCEED (Commit: 4cdd9cb7) nav page route peer

## Resolution

**Date:** 2026-08-14  
**Review tip:** `origin/sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface` @ `52d331b6` (Radia docs) / product+tests @ `4cdd9cb7`

Radia **CLEAN** / **PROCEED** — no fix-now or discuss items. Advisory notes (three-dot rollup breadth; UAT can fill Ideal Day via UI) acknowledged; no product or plan change required.

**Outcome:** resolve clean → User Testing.
```

