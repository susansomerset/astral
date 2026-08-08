<!-- linear-archive: AST-1104 archived 2026-08-07 -->

## Linear archive (AST-1104)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1104/fix-scheduled-actions-blank-page-on-candidate-all-avail-all-bug-when  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1102 — Bug when select All candidates and All avail count  
**Blocked by / blocks / related:** parent: AST-1102

### Description

## What this implements

Reproduce the blank-page failure when Candidate and Avail are both All, fix the render/runtime fault so chrome and list (or empty-filter status) stay up, and verify defaults plus other filter combos still behave. Does **not** own Avail calculation, dispatch, or filter-bar redesign.

## Acceptance criteria

- [X] On Admin → Scheduled Actions, set **Candidate** to All and **Avail** to All: header, nav, and Scheduled Actions content remain visible (not a blank black page).
- [X] With that combination and no other narrowing filters, rows with zero/empty Avail that exist in the loaded data remain visible (Avail All semantics).
- [X] After reproducing the former failure path, the document is not left as an empty `#root` shell with no app UI.
- [X] Fresh load still defaults Avail to > 0 and remains usable; selecting a specific candidate remains usable.
- [X] Changing Candidate and Avail among All / specific / > 0 does not blank the page for any of those combinations.

## Boundaries

* Does not change how Available is calculated, claimed, or dispatched.
* Does not change Avail column formatting, add new Avail modes, or redesign the filter bar.
* Does not change Run / Stop / AUTO / edit-modal / Manage Tasks behavior.
* Does not change Recommended Jobs or other sectioned screens.
* Does not open a separate global React error-boundary epic.

## In scope

- [X] `astral.standards.in-scope-only` — touch only the pinned throw site on Scheduled Actions / shared Last Run time formatting
- [X] `astral.standards.dry-and-focused-functions` — absorb invalid timezone once in `fmtTime` when Branch A; no duplicated catch sprawl
- [X] `astral.ui.frontend-file-placement` — stay in `pages/` / `lib/` / `components/`
- [X] `astral.ui.naming-conventions` — existing SA / Time naming unchanged
- [X] `astral.layers.ui-config-driven-business-logic` — no new Avail/Candidate business rules in React; formatting/stability only

## Considered but excluded

- [X] `pattern.ui.admin-endpoint` — no new admin HTTP surface unless Stage 1 proves API root cause (then stop)
- [X] Global React ErrorBoundary epic — parent boundary; recovery UI only as needed to stop this blank page
- [X] Available count calculation / claim / dispatch (`src/core/dispatcher.py`, data claim paths)
- [X] Avail filter redesign or new Avail modes beyond existing All / `> 0`
- [X] Other sectioned list screens (Recommended Jobs, etc.)

## Notes for planning

Frontend bug fix on Admin → Scheduled Actions (AST-751 / AST-887 / AST-888 filter surface). Empty `#root` ⇒ uncaught exception (no ErrorBoundary in `main.tsx`). Stage 1 pinned Branch A: invalid `timeZone` in `fmtTime`; Stage 2 absorbs in `fmt.ts`.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

| Ticket | `origin/…` |
| -- | -- |
| AST-1102 (parent) | ftr/AST-1102-bug-when-select-all-candidates-and-all-avail-count |
| AST-1104 | sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all |

### Comments

#### radia — 2026-07-31T06:08:10.093Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1104
**Publish ref:** `origin/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all` @ `b425f08135bb8b16e81de2be018ca9d2cea54ed6`
**Overall:** DISCUSS

Baseline: `origin/dev`…`origin/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all`. Product code: `src/ui/frontend/src/lib/fmt.ts` only (Branch A). Plan doc + Betty test-tree / bible ride along in the three-dot.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | layers/paths miss (no core/utils config) |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths miss (no src/core) |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths miss (no src/core) |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths miss (no data/core) |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths miss (no data/core) |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths miss (no data/core) |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths miss (no data/core) |
| astral.config.config-source-of-truth | scoped | conforms | UTC fallback literal already plan-approved; no new config keys |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | layers/paths miss (no core/data/config.py) |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env touched in fmt.ts |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (no artifacts/** / scripts/spikes) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plan only; no misplaced spike |
| astral.dispatch.seed-auto-false | scoped | not-applicable | layers/paths miss (no dispatcher/config) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `ast-1104-…md` under docs/features/interface |
| astral.git.betty-no-src-or-features | scoped | conforms | src/features authored by engineer commits; Betty stay on tests |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree via Betty `test`/`merge-tests`; code() is fmt.ts only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths miss (no core/external) |
| astral.layers.import-direction | scoped | conforms | frontend lib only; no layer-crossing imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss (no scripts) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | formatting/error absorption only; no Avail/Candidate rules |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths miss (no src/core) |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths miss (no src/core) |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | no new HTTP routes/endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer work |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss (no src/data) |
| astral.standards.debug-contract-gated | scoped | conforms | UI fmt helper; no backend debug contract surface |
| astral.standards.dry-and-focused-functions | scoped | conforms | single absorption in fmtTime; no catch sprawl |
| astral.standards.in-scope-only | scoped | conforms | Branch A only; B/C untouched; matches Stage 1 pin |
| astral.standards.logging-via-utils | scoped | conforms | no print/logging in touched TS |
| astral.standards.no-cross-contamination | scoped | conforms | stays in frontend lib |
| astral.standards.no-hardcoded-sets | scoped | conforms | no new state/enum lists |
| astral.standards.public-then-helpers | scoped | conforms | public fmtTime absorbs; no new helper sprawl |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss (no src/utils) |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths miss (no core/data) |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers/paths miss (no core/data/config) |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths miss (no src/core) |
| astral.ui.frontend-file-placement | scoped | conforms | edit under `src/ui/frontend/src/lib/` |
| astral.ui.naming-conventions | scoped | conforms | fmtTime / existing SA naming unchanged |
| astral.ui.single-gunicorn-worker | scoped | conforms | no worker/server config changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip includes `merge-tests(AST-1104): origin/tests 3e1f81f1` |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on AST-1104 commits |
| orch.git.flow-direction-inviolable | universal | conforms | published to origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1102/AST-1104-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | origin/dev ancestor; merge before docs no-op clean |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force on review path |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named publish branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-1102 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Stage 1 pin recorded; no product-decision stop |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 2 Branch A matches Files Changed + pin comment |
| orch.pipeline.project-scoped-queues | universal | conforms | single-child Astral Interface review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty authored test/bible; engineer stayed off |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | assignee left on Katherine (implementer) |
| orch.roles.pre-commit-path-bans | universal | conforms | docs() review commit only on features plan |

## Pattern conformance

- `pattern.ui.admin-endpoint` — not-cited (Considered but excluded; Stage 1 pinned frontend `fmtTime`, no admin HTTP)
- no other pattern ids cited for implementation

## Plan adherence

Stage 1 Branch A pin (`RangeError` invalid TZ) → Stage 2 exactly `fmt.ts` try/UTC/raw-ISO. Self-Assessment Scope `Single-Component` matches product footprint. Boundaries honored (no Avail math, filter redesign, ErrorBoundary epic, B/C). Happy-path Intl options preserved.

## Findings

**discuss (C4 straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` (plan Files Changed was ui-only). Ship three-dot vs `origin/dev` scores them in-scope via plan doc + Betty test-tree. Content verdicts above are **conforms** — no product fix.

No fix-now.

### What’s solid

Invalid-TZ absorption with comment; exclusive Branch A; Betty harness for All+All survival + fmtTime UTC fallback.

### Recommended actions

Acknowledge C4 stragglers; no `fmt.ts` change expected. `resolve-child` → User Testing when clear.

Docs: `docs(AST-1104): Radia review` on publish-ref @ `b425f081`.

context_tokens≈52000

#### betty — 2026-07-31T06:01:26.917Z
1. `tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx` — **AST-1104 Candidate All + Avail All blank-page survival** (Candidate All + Avail All keeps chrome + zero-Avail Last Run; Avail gt0↔All stays mounted with invalid nav `contact.timezone`)
2. `tests/component/frontend/lib/test_fmt.test.ts` — `fmtTime` falls back to UTC on invalid IANA zone (Branch A pin)
3. `tests/component/frontend/components/test_Time.test.tsx` — invalid `contact.timezone` → UTC; fixtures revised from `profile.timezone`
4. Regression: `test_AdminScheduledActions.test.tsx` — `AST-894|AST-887|AST-893|AST-751|AST-768|AST-785`

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/lib/test_fmt.test.ts \
  ../../../tests/component/frontend/components/test_Time.test.tsx \
  --testNamePattern="AST-1104|AST-894|AST-887|AST-893|AST-751|AST-768|AST-785|fmtTime|Time"
```

`origin/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all` @ `9a59cbe6` (`merge-tests(AST-1104): origin/tests 3e1f81f1`)

Bible: `docs/test-bible/frontend/pages.md` shasum `3d67bb4fcb99b703ba2dad5bfae29e40d1aafe22`

#### katherine — 2026-07-31T05:49:46.224Z
**Stage 1 pin — Branch A**

**Repro path:** Harness A (lib). `fmtTime(iso, "Not/AZone")` with non-null ISO (same call path as Scheduled Actions Last Run → `<Time>` → `fmtTime`).

**Exception:** `RangeError: Invalid time zone specified: Not/AZone`

**Stack top:** `fmtTime` in `src/ui/frontend/src/lib/fmt.ts` (`toLocaleString` with `timeZone`). No root ErrorBoundary in `main.tsx` → uncaught throw empties `#root`.

**Why All+All:** Default Avail `gt0` can hide zero-avail rows that carry `last_run_at`; Candidate All + Avail All mounts those Last Run cells. Invalid nav-selected candidate `contact.timezone` then throws on first formatted timestamp.

**Stage 2 file:** `src/ui/frontend/src/lib/fmt.ts` (Branch A). Not B/C.

#### joan — 2026-07-31T05:48:34.995Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1104
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Candidate All + Avail All keeps chrome/content | Stages 1–3 (pin + fix + smoke) |
| AC2 zero/empty Avail rows remain visible under Avail All | Stage 2 shared constraints + Stage 3 smoke |
| AC3 not left as empty `#root` | Stage 1 Decision + Stage 2 stop the throw |
| AC4 fresh load Avail > 0; specific candidate usable | Stage 2 Done when + Stage 3 smoke |
| AC5 switching All/specific/> 0 does not blank | Stage 2 Done when + Stage 3 smoke |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 reproduce/pin | Purpose blank-page failure; Functional scope 1/4 |
| Stage 2 fix pinned throw (A/B/C) | Functional scope 1–4; Boundaries honored |
| Stage 3 verify filter survival | AC1–5; preserve AST-887/AST-888/AST-894 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | code(AST-1104) ritual named |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Merge ftr before build named |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1102/AST-1104-… only |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1102 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stop→parent/amend if pin unknown or off-table |
| orch.pipeline.plan-is-bible | conforms | Revision 1 Files Changed covers all Stage 2 branch paths |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Discuss re-validate only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/ left to Betty |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Katherine implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths proposed |
| astral.config.config-source-of-truth | conforms | No new config keys; UTC fallback already used |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.import-direction | conforms | Frontend-only |
| astral.layers.ui-config-driven-business-logic | conforms | Formatting/stability only; no new Avail/Candidate rules |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new routes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work |
| astral.standards.debug-contract-gated | conforms | UI; no backend debug requirement |
| astral.standards.dry-and-focused-functions | conforms | Prefer single absorption in fmt.ts |
| astral.standards.in-scope-only | conforms | Branch C limited to listed Files Changed rows; off-table → 🛑 |
| astral.standards.logging-via-utils | conforms | No Python logging path |
| astral.standards.no-cross-contamination | conforms | Stays in frontend UI |
| astral.standards.no-hardcoded-sets | conforms | No new enums/state lists |
| astral.standards.public-then-helpers | conforms | Focused helper absorption |
| astral.ui.frontend-file-placement | conforms | pages/lib/components + existing hooks/ file only (no new dirs) |
| astral.ui.naming-conventions | conforms | Existing SA/Time naming unchanged |
| astral.ui.single-gunicorn-worker | conforms | No worker/config changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers ∩ plan {ui} empty
- astral.agent.do-task-delegation — layers ∩ plan {ui} empty
- astral.agent.grade-vector-validation — layers ∩ plan {ui} empty
- astral.batch.batch-id-first — layers ∩ plan {ui} empty
- astral.batch.batch-id-format — layers ∩ plan {ui} empty
- astral.batch.claim-process-release — layers ∩ plan {ui} empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan {ui} empty
- astral.config.pass-threshold-vs-score-floor — layers ∩ plan {ui} empty
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.dispatch.seed-auto-false — layers ∩ plan {ui} empty
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {ui} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ∩ plan {ui} empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {ui} empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan {ui} empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan {ui} empty
- astral.standards.database-header-inventory — layers ∩ plan {ui} empty
- astral.standards.utils-data-late-import-only — layers ∩ plan {ui} empty
- astral.state.core-decides-transitions — layers ∩ plan {ui} empty
- astral.state.job-prior-states-enforced — layers ∩ plan {ui} empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan {ui} empty

## Findings

None fix-now.

**Round 1 closed:** Revision 1 added Files Changed rows for `useListTableColumnMeasure.ts` and `useSectionExpandPolicy.ts`; Branch C authorizes only table paths and 🛑+amends if the pin is elsewhere.

**acceptable:** Medium conf/risk remains honest; exclusive A/B/C + Stage 1 pin gate intact.

context_tokens≈42000

— Joan

#### katherine — 2026-07-31T05:46:41.283Z
[plan-discuss] round=1 reply

**Delta:** Closed fix-now Branch C vs Files Changed.

- Added conditional Files Changed rows for `src/ui/frontend/src/lib/useListTableColumnMeasure.ts` and `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts` (Branch C only, pin-gated).
- Rewrote Stage 2 Branch C to authorize **only** those table paths (+ `AdminScheduledActions.tsx` when the stack lands there); if the pin names anything else → 🛑 amend before coding.
- Revision 1 noted in the plan doc.

Plan: [ast-1104-fix-sa-blank-candidate-all-avail-all.md](https://github.com/susansomerset/astral/blob/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all/docs/features/interface/ast-1104-fix-sa-blank-candidate-all-avail-all.md)
`origin/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all` @ `4c41224b`

Status left **Plan Discuss** for Joan re-validate.

#### joan — 2026-07-31T05:42:03.750Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1104
**Overall:** REVISE

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Candidate All + Avail All keeps chrome/content | Stages 1–3 (pin + fix + smoke) |
| AC2 zero/empty Avail rows remain visible under Avail All | Stage 2 shared constraints (do not change Avail predicate) + Stage 3 smoke |
| AC3 not left as empty `#root` | Stage 1 Decision (uncaught exception) + Stage 2 stop the throw |
| AC4 fresh load Avail > 0; specific candidate usable | Stage 2 Done when + Stage 3 smoke |
| AC5 switching All/specific/> 0 does not blank | Stage 2 Done when + Stage 3 smoke |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 reproduce/pin | Purpose blank-page failure; Functional scope 1/4 |
| Stage 2 fix pinned throw (A/B/C) | Functional scope 1–4; Boundaries (no Avail math / filter redesign / ErrorBoundary epic) |
| Stage 3 verify filter survival | AC1–5 verification; preserve AST-887/AST-888/AST-894 semantics |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | code(AST-1104) ritual named |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Merge ftr before build named |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1102/AST-1104-… only |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1102 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stop→parent if pin unknown |
| orch.pipeline.plan-is-bible | violates | Stage 2 Branch C authorizes edits outside Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/ left to Betty |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Katherine implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths proposed |
| astral.config.config-source-of-truth | conforms | No new config keys; UTC fallback already used |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.import-direction | conforms | Frontend-only |
| astral.layers.ui-config-driven-business-logic | conforms | Formatting/stability only; no new Avail/Candidate rules |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new routes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work |
| astral.standards.debug-contract-gated | conforms | UI; no backend debug requirement |
| astral.standards.dry-and-focused-functions | conforms | Prefer single absorption in fmt.ts |
| astral.standards.in-scope-only | violates | Branch C can touch hooks not listed in Files Changed |
| astral.standards.logging-via-utils | conforms | No Python logging path |
| astral.standards.no-cross-contamination | conforms | Stays in frontend UI |
| astral.standards.no-hardcoded-sets | conforms | No new enums/state lists |
| astral.standards.public-then-helpers | conforms | Focused helper absorption |
| astral.ui.frontend-file-placement | conforms | pages/lib/components paths named for A/B |
| astral.ui.naming-conventions | conforms | Existing SA/Time naming unchanged |
| astral.ui.single-gunicorn-worker | conforms | No worker/config changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.config.config-source-of-truth, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers ∩ plan {ui} empty
- astral.agent.do-task-delegation — layers ∩ plan {ui} empty
- astral.agent.grade-vector-validation — layers ∩ plan {ui} empty
- astral.batch.batch-id-first — layers ∩ plan {ui} empty
- astral.batch.batch-id-format — layers ∩ plan {ui} empty
- astral.batch.claim-process-release — layers ∩ plan {ui} empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan {ui} empty
- astral.config.pass-threshold-vs-score-floor — layers ∩ plan {ui} empty
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.dispatch.seed-auto-false — layers ∩ plan {ui} empty
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {ui} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ∩ plan {ui} empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan {ui} empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan {ui} empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan {ui} empty
- astral.standards.database-header-inventory — layers ∩ plan {ui} empty
- astral.standards.utils-data-late-import-only — layers ∩ plan {ui} empty
- astral.state.core-decides-transitions — layers ∩ plan {ui} empty
- astral.state.job-prior-states-enforced — layers ∩ plan {ui} empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan {ui} empty

## Findings

**fix-now — Stage 2 Branch C vs Files Changed**
- **Location:** Stage 2 Branch C; Files Changed table
- **Finding:** Branch C says edit `AdminScheduledActions.tsx` and/or `useListTableColumnMeasure.ts` / `useSectionExpandPolicy.ts`, but Files Changed only lists `AdminScheduledActions.tsx`, `fmt.ts`, and `Time.tsx`. Real paths exist at `src/ui/frontend/src/lib/useListTableColumnMeasure.ts` and `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts`. Plan-is-bible cannot authorize those edits as written.
- **Recommendation:** Either (1) add conditional Files Changed rows for both hook files (ui / Only if Stage 1 pins expand-measure), or (2) constrain Branch C to `AdminScheduledActions.tsx` only and require 🛑 stop + plan amend if the pin stack is in the hooks, or (3) drop Branch C until Stage 1 proves it and amend then — but do not leave Stage 2 instructing out-of-table edits.

**discuss (non-blocking):** Primary Branch A hypothesis is well-evidenced; Medium conf/risk self-assessment is honest given Stage 1 pin gate.

**acceptable:** Boundaries vs Avail math / ErrorBoundary / Betty tests are clear; exclusive A/B/C “exactly one branch” is good discipline once Files Changed covers every branch.

context_tokens≈48000

— Joan

#### katherine — 2026-07-31T05:08:41.932Z
Plan: [docs/features/interface/ast-1104-fix-sa-blank-candidate-all-avail-all.md](https://github.com/susansomerset/astral/blob/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all/docs/features/interface/ast-1104-fix-sa-blank-candidate-all-avail-all.md)

`origin/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all` @ `b4ea4fc5`

**Scope:** Single-Component — Scheduled Actions blank-page survival; expected touch is `AdminScheduledActions.tsx` and/or shared `fmtTime`/`Time` for Last Run, not Avail math or dispatch.

**Conf:** Medium — empty `#root` + confirmed `fmtTime` RangeError on bad `timeZone` point to an uncaught render throw when Candidate All + Avail All mounts more Last Run cells; Stage 1 still pins the live stack (score_floor `.toFixed` / expand-measure loop remain alternate branches).

**Risk:** Medium — wrong branch could miss the real throw or soften timezone display; Avail/Candidate semantics regressions would break AST-887/AST-894 triage. Bounded to UI formatting/stability.

---

# Fix Scheduled Actions blank page on Candidate All + Avail All

**Linear:** [AST-1104](https://linear.app/astralcareermatch/issue/AST-1104/fix-scheduled-actions-blank-page-on-candidate-all-avail-all-bug-when)
**Parent:** [AST-1102](https://linear.app/astralcareermatch/issue/AST-1102/bug-when-select-all-candidates-and-all-avail-count)
**Publish ref:** `sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all`

On Admin → Scheduled Actions, setting **Candidate: All** together with **Avail: All** tears the SPA down to an empty `#root` (black page, no header/nav). View-source still shows the Vite shell with an empty root div — classic uncaught React render/effect exception with no ErrorBoundary. This ticket reproduces that path, pins the throw site, and fixes only what the crash requires so chrome + Scheduled Actions content (list or existing empty-filter status) stay mounted. Avail All / Candidate All semantics from AST-887 / AST-888 / AST-894 stay intact; defaults (Avail `> 0`) and other filter combos must keep working.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Only if Stage 1 pins the throw here (Branch B score_floor cell, and/or Branch C expand-prune / table-mount effect in this page): harden the offending render/effect path so Candidate All + Avail All cannot unmount the tree | ui |
| `src/ui/frontend/src/lib/fmt.ts` | Only if Stage 1 pins `fmtTime` / invalid `timeZone` (Branch A): catch `RangeError` (and equivalent) from `toLocaleString` and fall back to UTC formatting (or raw ISO when the date itself is unusable) so Last Run cells cannot blank the SPA | ui |
| `src/ui/frontend/src/components/Time.tsx` | Only if Stage 1 pins `<Time>` / candidate timezone (Branch A): coerce missing/invalid IANA timezone to `"UTC"` before calling `fmtTime` (same fallback rule as `fmt.ts`); prefer absorption in `fmt.ts` when that alone stops the throw | ui |
| `src/ui/frontend/src/lib/useListTableColumnMeasure.ts` | Only if Stage 1 pin stack is in this hook (Branch C): minimal stability fix (e.g. keep/strengthen `widthsEqual` so measure cannot loop) — do not change sticky math semantics beyond stopping the update-depth crash | ui |
| `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts` | Only if Stage 1 pin stack is in this hook (Branch C): minimal stability fix for expand-key updates — do not change Expand All / Expand One policy defaults or Avail predicates | ui |

**Out of scope (this ticket):** Available calculation / claim / dispatch; Avail column formatting semantics (zero/empty still em dash); new Avail modes or filter-bar redesign; Run / Stop / AUTO / edit-modal / Manage Tasks; Recommended Jobs or other sectioned screens; a new global React error-boundary epic; API / `api_admin.py` payload changes unless Stage 1 proves a server fault as root cause (then stop and comment — do not invent backend work); `tests/` and `docs/test-bible/**` (Betty at Code Complete).

**QA note (Betty — not engineer commits):** Extend `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` (and/or `test_Time.test.tsx` / `test_fmt.test.ts` if the pin is timezone) so Candidate All + Avail All keeps header/title and list-or-empty-status mounted; preserve AST-887/AST-894 Avail default + zero-row visibility; regression smoke `AST-1104|AST-894|AST-887|AST-893|AST-751|AST-768|AST-785`.

---

## Stage 1: Reproduce and pin the throw

**Done when:** The Candidate All + Avail All failure is reproduced (or a fixture-backed component/lib test that throws the same way), and a Linear comment on **AST-1104** records the exact exception name/message plus stack top (`file:line`). No product fix lands in this stage’s commit unless the pin is already known from an existing failing assertion written in this stage.

1. On the epic worktree (`astral-AST-1102/`), confirm checkout is `sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all`, `origin/dev` is an ancestor of `HEAD`, and `origin/ftr/AST-1102-bug-when-select-all-candidates-and-all-avail-count` has been merged (no-op if current).

2. Reproduce with the live admin UI when available:
   - Run Flask + Vite per `ASTRAL_CODE_RULES` §3.5.
   - Open Admin → Scheduled Actions (landing defaults: Avail `> 0`, Expand All).
   - Set **Candidate** to All, then **Avail** to All (or the reverse).
   - Confirm the viewport goes blank / `#root` empty and capture the **browser console** first error + stack.

3. If live data does not blank locally, pin with a focused failing harness instead (still Stage 1 — no silent guessing). Prefer the smallest of:
   - **A — invalid timezone + Last Run visible only under All+All:** mount Scheduled Actions (or `<Time>`) with nav-selected candidate `candidate_data.contact.timezone` set to a non-IANA string (e.g. `"Not/AZone"`), and at least one dispatch-task row with non-null `last_run_at` that is hidden under default Avail `gt0` (e.g. `available_count: 0`) but visible after `selectAvailAll()` + `selectAllCandidatesFilter()`. Expect uncaught `RangeError: Invalid time zone specified: …` from `fmtTime` / `<Time>` (confirmed: `fmtTime(iso, "Not/AZone")` throws today; there is no root ErrorBoundary in `main.tsx`).
   - **B — non-number `score_floor` on a newly visible scored row:** mount a scored row with `score_floor` as a string (e.g. `"1.00"`) that only appears under Candidate All + Avail All; expect `TypeError` from `(row.score_floor ?? 1).toFixed(2)` in `ScheduledPhaseTable`.
   - **C — expand / measure update-depth:** fixture with multiple sections + Expand All + All+All row growth; expect React “Maximum update depth exceeded” (or equivalent) from the expand-prune effect and/or `useListTableColumnMeasure` — only treat as the pin if the console stack points there.

4. Post a comment on **AST-1104** (not the parent) with:
   - Repro path (live UI vs harness A/B/C)
   - Exact exception + top of stack
   - Which Files Changed row will be edited in Stage 2

5. If none of A–C match the live stack and the page still blanks only in an environment you cannot capture, **stop** with the 🛑 Stage format on the **parent** AST-1102 and wait — do not invent a fourth root cause.

⚠️ **Decision:** Treat empty `#root` as an **uncaught exception**, not a CSS/black-background bug and not “missing data.” Do not add a global ErrorBoundary in this ticket (parent boundary). Stage 1 must name one throw site before Stage 2 edits product code.

**Ritual:** `docs(AST-1104):` only if this stage adds harness notes inside the plan; otherwise no commit — proceed to Stage 2 in the same build session after the Linear pin comment. (Plan-child publishes this plan doc separately; build-child owns product commits.)

---

## Stage 2: Fix only the pinned throw

**Done when:** Candidate All + Avail All keeps app chrome and Scheduled Actions content mounted; zero/empty Avail rows that exist in loaded data remain visible under Avail All with no other narrowing filters; fresh load still defaults Avail to `> 0`; switching Candidate/Avail among All / specific / `> 0` does not blank the page. `cd src/ui/frontend && npx tsc -b --noEmit` passes.

Execute **exactly one** branch matching the Stage 1 pin. Do not apply the other branches “just in case.”

### Branch A — `fmtTime` / `<Time>` invalid timezone

1. In `src/ui/frontend/src/lib/fmt.ts`, inside `fmtTime`, keep the existing null/empty → `"—"` and invalid-date → `String(iso)` behavior. Wrap the `toLocaleString(..., { timeZone })` call in `try/catch`. On failure (invalid time zone or other locale error), retry once with `timeZone: "UTC"`. If that also fails, return `String(iso)`. Do not change the happy-path format options (en-US, 2-digit year, etc.).

2. In `src/ui/frontend/src/components/Time.tsx`, when reading `contact?.timezone`, if the value is missing/blank use `"UTC"` (already true). Optionally pass through `fmt.ts` only — do **not** duplicate a second try/catch in `Time.tsx` if `fmtTime` already absorbs the RangeError. Prefer single absorption in `fmt.ts` (§1.3 DRY).

3. Do **not** change `CandidateContext` timezone sync unless Stage 1 stack shows the throw outside `fmtTime`/`Time` (unlikely). Do not validate timezone lists in config.

### Branch B — `score_floor.toFixed` TypeError in ScheduledPhaseTable

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx` `ScheduledPhaseTable` Floor cell, replace `(row.score_floor ?? 1).toFixed(2)` with a number-safe format: `const floor = Number(row.score_floor ?? 1);` then display `Number.isFinite(floor) ? floor.toFixed(2) : "—"` (still only when the row is scored). Do not change Floor filter math, score_floor persistence, or non-scored blank cells.

2. Do not widen `DispatchTask.score_floor` typing beyond what the fix needs; do not change the API.

### Branch C — expand / measure maximum update depth

1. Touch **only** the Files Changed row(s) named in the Stage 1 pin comment. Allowed paths for this branch:
   - `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — e.g. avoid `setExpandedKeys` when the pruned set equals current membership; do not re-expand on every filter change (AST-894 once-gate stays).
   - `src/ui/frontend/src/lib/useListTableColumnMeasure.ts` — e.g. keep/strengthen `widthsEqual` so measure cannot loop.
   - `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts` — e.g. stabilize expand-key updates if the stack lands here.
   Apply the **minimal** stability fix indicated by the stack. Do **not** edit any path outside the Files Changed table; if the stack names a different file, 🛑 stop and amend the plan before coding.

2. Do not change Expand All policy defaults or Avail filter predicates.

### Shared constraints (all branches)

1. Do **not** change `filteredRows` Avail predicate (`availGtZeroFilter === "gt0"` → `(r.available_count ?? 0) > 0`) or Candidate filter equality.
2. Do **not** change `formatAvailableCount` em-dash rules for null/0.
3. Do **not** redesign the filter bar or add recovery UI beyond stopping the throw.
4. If the pinned stack is in API/backend code, **stop** and comment — frontend-only unless root cause proves otherwise.

⚠️ **Decision:** Primary planning hypothesis is **Branch A** (invalid candidate timezone + first non-null `last_run_at` becoming visible when filters widen), because `fmtTime` throws today, `main.tsx` has no ErrorBoundary, and Last Run uses `<Time>` on every table row. Stage 1 still wins if the live stack says B or C.

**Ritual:** `code(AST-1104): stop SA blank page on Candidate All + Avail All`

---

## Stage 3: Verify filter survival (manual / existing tests)

**Done when:** Builder has smoke-checked the AC combinations on the fixed tip; existing component file still runs for the suites listed below (or failures are clearly pre-existing / test-only and handed to Betty via `[qa-handoff]` only after product AC is met).

1. Manual smoke on Admin → Scheduled Actions:
   - Landing: Avail defaults to `> 0`, page usable, chrome present.
   - Candidate All + Avail All: header, nav, Scheduled Actions title/filters remain; list shows zero/empty Avail rows when present in data (or existing empty-filter status if nothing matches other filters — not a blank `#root`).
   - Candidate specific + Avail All; Candidate All + Avail `> 0`; back to defaults — none blank the page.
2. Run (product sanity, not Betty ownership of new cases):
   ```bash
   cd src/ui/frontend && npm run test:component -- \
     ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
     --testNamePattern="AST-894|AST-887|AST-893|AST-751|AST-768|AST-785"
   ```
   If green, proceed. If red only because a new AST-1104 assertion is missing, leave test authorship to Betty. If red because the product fix broke Avail/expand semantics, fix product code (still this ticket) — do not “fix” tests in `tests/`.
3. `cd src/ui/frontend && npx tsc -b --noEmit`

**Ritual:** no separate commit unless Stage 2 needed a follow-up product fix; otherwise Stage 2 commit is sufficient before Code Complete.

---

## Self-Assessment

**Scope:** `Single-Component` — Scheduled Actions blank-page survival; Files Changed covers SA page, `fmtTime`/`Time`, and (Branch C only) the two expand/measure hooks — not Avail math or dispatch.

**Conf:** `Medium` — empty `#root` plus confirmed `fmtTime` RangeError on bad `timeZone` strongly suggest an uncaught render throw when wider filters mount more Last Run cells, but Stage 1 must pin the live stack before coding (B/C remain possible).

**Risk:** `Medium` — wrong fix could mask a different throw or soften timezone display; Avail/Candidate semantics regressions would break AST-887/AST-894 operator triage. Bounded to UI formatting/stability, not claim/dispatch.

## Code Rules Check

| Rule | Status |
|------|--------|
| §1.1 in-scope only | Pass — only the pinned throw site + listed files; no filter-bar redesign, no global ErrorBoundary epic |
| §1.3 DRY | Pass — timezone absorption prefers `fmt.ts` once; no duplicate catch in every page |
| §2.1 config | N/A — no new config keys; timezone fallback is UTC literal already used by `Time`/`fmtTime` |
| §2.4 batch | N/A — no batch/claim changes |
| §2.6 state machine | N/A |
| §3.3 imports | Pass — frontend-only; no new layer violations |
| §3.5 naming / file placement | Pass — stay in `pages/` / `lib/` / `components/` |
| `astral.layers.ui-config-driven-business-logic` | Pass — no new business rules in React; formatting/error absorption only |

## Revisions

Revision 1 — 2026-07-31  
Driven by: Joan `[plan-discuss] round=1 concern` — Stage 2 Branch C vs Files Changed (`orch.pipeline.plan-is-bible` / `astral.standards.in-scope-only`)  
Changes: Added conditional Files Changed rows for `useListTableColumnMeasure.ts` and `useSectionExpandPolicy.ts`; rewrote Branch C to authorize only those table paths (plus SA page when pinned there) and to 🛑 + amend if the stack names anything else.

## Review (build)

**Built:** `origin/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all` @ `2b9dc4085c8c675b472be0f1c86f7529b39b169c`

Stage 1 pinned Branch A (`fmtTime` RangeError on invalid `timeZone`). Stage 2: `fmt.ts` absorbs locale/timezone failures with UTC retry then raw ISO — Last Run cells cannot empty `#root`. Branches B/C not applied. SA regression smoke `AST-894|AST-887|AST-893|AST-751|AST-768|AST-785` green (24). Tests deferred to Betty.

## Review (Radia)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1104
**Publish ref tip (pre-docs):** `9a59cbe6206d5e330f0bdfc26952060f0cd8291a`
**Overall:** DISCUSS

### What’s solid

- Stage 1 pin → Branch A only; product diff is sole `fmt.ts` absorption matching plan.
- Happy-path format options unchanged; invalid TZ falls back UTC then raw ISO; in-code comment ties catch to missing root ErrorBoundary.
- Betty `merge-tests(AST-1104)` + AST-1104 frontend harness present; assignee remains Katherine.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time; ship three-dot vs `origin/dev` brings them in-scope via `docs/features/**` + Betty `tests/` / `docs/test-bible/**`. Scored **conforms** on content (single plan file; no spike misplacement; engineer did not author test-tree — Betty `test`/`merge-tests`). No product fix required.

### Recommended actions

- Engineer: acknowledge C4 stragglers; no `fmt.ts` change expected. Proceed `resolve-child` → User Testing when clear.

## Resolution

**2026-07-31** — Radia `[code-rubric] revision=1` Overall DISCUSS; **fix-now: none**.

- Acknowledged C4 stragglers (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`): Joan Excluded at plan time; three-dot scored **conforms**; no product change.
- No `fmt.ts` / Branch B/C edits on resolve.
- Merged `origin/dev` onto sub (mechanical keep-both in `tests/component/core/test_agent.py` for AST-1099 + AST-1083 classes).

