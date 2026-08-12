<!-- linear-archive: AST-980 archived 2026-08-05 -->

## Linear archive (AST-980)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-980/add-debug-to-execution-history-level-list-add-level-debug-to-app-log  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-976 — Add level "DEBUG" to app_log table  
**Blocked by / blocks / related:** parent: AST-976

### Description

## What this implements

Execution History Level control includes **DEBUG** so Susan can filter expanded logs to DEBUG-only (filter/Copy/empty-state consistent with other levels). Does **not** own app_log persistence or other Execution History redesign. If DEBUG is already present from prior Level-filter work, confirm it and close the gap only if missing.

## Acceptance criteria

4. Execution History Level control lists **DEBUG** as a selectable option; with **Level = DEBUG** on a debug=True batch that produced DEBUG rows, the expanded log shows those DEBUG lines; with **Level = INFO**, those DEBUG lines are hidden and INFO lines remain visible.

## Boundaries

Does **not** own app_log persistence (sibling AST-979). Does **not** redesign ledger columns, Skip Checks, Agent Data, or other Execution History filters. Prior Level-filter work (AST-838 / AST-840) may already list DEBUG — confirm or add only if missing.

## Notes for planning

Blocked by AST-979 (DEBUG rows must exist for UAT). UI page: Execution History / performance_monitor Level filter.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-976-add-level-debug-to-app_log-table`, child `sub/AST-976/<this-id>-…`. Created at dispatch-parent. Publish to origin/<sub-ref> only.

### Comments

#### chuckles — 2026-07-25T19:07:13.571Z
[merge-child] blocked: after AST-979 rollup, sub not stacked on ftr — @Katherine Johnson: rebase onto `origin/ftr/AST-976-add-level-debug-to-app_log-table`, keep sequence labels + single merge-tests, `git push --force-with-lease`. Stay User Testing.

— Chuckles

#### chuckles — 2026-07-25T19:04:26.158Z
[merge-child] blocked: validate-sub-log after restack — missing `plan(AST-980):`, `code(AST-980):`, `merge-tests(AST-980):`, `test(AST-980):` on `origin/sub/AST-976/AST-980-add-debug-to-execution-history-level-list` (confirm-only; restack dropped merge-tests). @Katherine Johnson: empty sequence labels `plan`/`code`/`test` for merge-child gate, push. Stay User Testing. @Betty White: re-deliver `merge-tests(AST-980): origin/tests 6abdf66a78d2fd5ddadf3e6a0cc7d4b547a479b4`.

— Chuckles

#### chuckles — 2026-07-25T19:00:11.415Z
[merge-child] blocked: git pull merge on sub — subjects starting with `Merge remote-tracking branch`. @Katherine Johnson: rebase onto `origin/ftr/AST-976-add-level-debug-to-app_log-table`, drop pull-merge commits, `git push --force-with-lease` to `origin/sub/AST-976/AST-980-add-debug-to-execution-history-level-list`. Stay User Testing.

— Chuckles

#### radia — 2026-07-25T18:58:50.241Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-980
**Publish ref:** `origin/sub/AST-976/AST-980-add-debug-to-execution-history-level-list` @ `09a1e3482ca8cb32f1e3ca6d6c0c120f585a202e`
**Overall:** DISCUSS

Baseline: `origin/dev` three-dot vs publish-ref. **No `src/` delta** (confirm-only / Stage 2 no-op). Net diff: plan + Betty bible/tests.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | not-applicable | layers ∩ {docs} empty |
| astral.agent.do-task-delegation | scoped | not-applicable | layers ∩ {docs} empty |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers ∩ {docs} empty |
| astral.batch.batch-id-first | scoped | not-applicable | layers ∩ {docs} empty |
| astral.batch.batch-id-format | scoped | not-applicable | layers ∩ {docs} empty |
| astral.batch.claim-process-release | scoped | not-applicable | layers ∩ {docs} empty |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers ∩ {docs} empty |
| astral.config.config-source-of-truth | scoped | not-applicable | layers ∩ {docs} empty |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | layers ∩ {docs} empty |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | layers ∩ {docs} empty |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan doc under docs/features is not a spike (C4 straggler vs Joan exclude) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single foundation plan file (C4 straggler vs Joan exclude) |
| astral.git.betty-no-src-or-features | scoped | conforms | features=engineer plan; Betty only bible/tests |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree via Betty docs(AST-980)/merge-tests (C4 straggler) |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers ∩ {docs} empty |
| astral.layers.import-direction | scoped | not-applicable | layers ∩ {docs} empty |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ∩ {docs} empty |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers ∩ {docs} empty (no src/ui in net diff) |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers ∩ {docs} empty |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers ∩ {docs} empty |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.debug-contract-gated | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.dry-and-focused-functions | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.in-scope-only | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.logging-via-utils | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.no-cross-contamination | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.public-then-helpers | scoped | not-applicable | layers ∩ {docs} empty |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers ∩ {docs} empty |
| astral.state.core-decides-transitions | scoped | not-applicable | layers ∩ {docs} empty |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers ∩ {docs} empty |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers ∩ {docs} empty |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ∩ {docs} empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ∩ {docs} empty |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers ∩ {docs} empty |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-980) one-sha from origin/tests |
| orch.git.commit-vocabulary | universal | conforms | docs/merge-tests vocabulary; no spurious code() |
| orch.git.flow-direction-inviolable | universal | conforms | publish on child sub/* only |
| orch.git.ftr-sub-topology | universal | conforms | sub/AST-976/AST-980-… under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | no checkout anti-pattern |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite/force on publish path |
| orch.git.no-dev-agent-branches | universal | conforms | used publish-ref, not Linear gitBranchName |
| orch.git.one-epic-worktree-per-parent | universal | conforms | reviewed in astral-AST-976 |
| orch.git.three-permanent-branches | universal | conforms | no fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | confirm-if-present already in definition |
| orch.pipeline.plan-is-bible | universal | conforms | docs/features/foundation/ast-980-….md |
| orch.pipeline.project-scoped-queues | universal | conforms | Foundation child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | bible/tests via Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Chuckles not assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | review-child leaves assignee unchanged |
| orch.roles.pre-commit-path-bans | universal | conforms | docs() only on features plan path |

## Pattern conformance

none cited

## Plan adherence

Stages 1–3 delivered as planned confirm-only path: Stage 1 Linear checklist with file:line citations; Stage 2 no-op (no AdminPerformanceMonitor / App.css edits in three-dot); Stage 3 AC4 Level-list lock notes AST-979 for real DEBUG rows. Self-Assessment `minor` matches zero product footprint. Independently re-verified on `origin/dev`: LOG_LEVELS DEBUG, URL select, visibleLogs equality, empty-state order, Copy, `.dispatch-log-level-debug`.

## Findings

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` against plan UI Files Changed. Net three-dot includes `docs/features/**`, `docs/test-bible/**`, `tests/**` — those statutes score in-scope and still **conform**. No product fix.

**fix-now:** none

### What’s solid

- AST-840 already ships DEBUG Level list; this child correctly closed as confirmation.
- Betty reuses existing AST-840 Vitest describe; no engineer test-tree edits.
- Persistence boundary with AST-979 held.

### Notes

Joan plan-rubric verdict attached (APPROVED). Stragglers are plan-time exclude vs post-Betty net diff only.

context_tokens≈22000

#### betty — 2026-07-25T18:56:38.325Z
## QA test manifest

`origin/sub/AST-976/AST-980-add-debug-to-execution-history-level-list` @ `7775aa2` (`merge-tests(AST-980): origin/tests 6abdf66`)

Confirm-only / no-op product delta (Katherine Stage 1–2). Coverage already on **AST-840**.

### Existing coverage (bible-backed)
1. `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — describe **`AST-840 log level filter`**
   - Level options include **DEBUG**
   - URL `log_level` seed / client filter / filtered-empty / filtered Copy (generic path covers DEBUG)

### Broken / gaps
None — no product files changed this ticket; no new Vitest required.

### Narrowed run
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "AST-840 log level filter"
```

### Bible
`docs/test-bible/frontend/pages.md` — `### AST-980 · AST-976` — shasum `e7a623b4d0989caee46581b50b2ab8e3e4a54ea6`

Persistence / real DEBUG `app_log` rows remain AST-979.

#### katherine — 2026-07-25T18:55:16.104Z
Stage 3 acceptance lock — parent AC4 Level-list portion:

- Level control lists **DEBUG** (`LOG_LEVELS` includes DEBUG; URL `log_level=DEBUG`).
- With Level=DEBUG, expanded log shows only `level === "DEBUG"` rows; with Level=INFO, DEBUG rows are hidden and INFO remains (`visibleLogs` strict equality).
- Copy / filtered-empty behave like other levels.

No product delta this ticket (AST-840 already shipped). Real DEBUG `app_log` rows for end-to-end UAT wait on AST-979. No engineer test edits — Betty owns AST-840 regression coverage.

`origin/sub/AST-976/AST-980-add-debug-to-execution-history-level-list` @ `3b00be5`

#### katherine — 2026-07-25T18:54:26.577Z
Stage 1 confirm — AST-840 DEBUG Level coverage (all present):

1. **LOG_LEVELS** — present: `AdminPerformanceMonitor.tsx:40` = `["DEBUG", "INFO", "WARNING", "ERROR"]`
2. **Level select + URL** — present: `log_level` via `searchParams` (`:146`); `<select>` + `LOG_LEVELS.map` under All (`:314–318`); `setFilter("log_level", …)`
3. **visibleLogs filter** — present: `entry.level === logLevelFilter` (`:445–448`)
4. **Empty-state order** — present: loading (`:450`) → zero-log (`:451–452`) → filtered-empty ``No '${logLevelFilter}' type…`` (`:454–458`)
5. **Copy** — present: `copyLogs` joins `visibleLogs` only (`:462–463`)
6. **CSS** — present: `.dispatch-log-level-debug` (`App.css:1938`)

Stage 2: no-op product delta.

#### joan — 2026-07-24T01:00:20.072Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-980
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC (AST-976) | Plan coverage |
| -- | -- |
| 1. debug=True → DEBUG rows in app_log | N/A — boundary: child Description “Does not own app_log persistence (sibling AST-979)” |
| 2. debug=False: no DEBUG flood; INFO/WARNING/ERROR unchanged | N/A — boundary: persistence sibling AST-979 |
| 3. Ordinary INFO stays INFO | N/A — boundary: persistence sibling AST-979 |
| 4. Execution History Level lists DEBUG; Level=DEBUG shows DEBUG rows; Level=INFO hides them | Stages 1–3 (confirm AST-840 coverage / conditional gap-close / AC4 Level-list acceptance lock) |
| 5. WARNING and ERROR persistence/display unchanged | N/A — boundary: no redesign of other levels; Stage 2 forbids DEBUG-only filter branches |

### Plan stages → definition

| Plan stage | Maps to |
| -- | -- |
| Stage 1: Confirm AST-840 DEBUG Level coverage | Functional scope “DEBUG on Execution History Level list”; Boundaries (confirm-or-add if missing); child AC4 |
| Stage 2: Gap-close (conditional) or no-op | Same; explicit no persistence / no ledger redesign |
| Stage 3: Acceptance lock | Parent AC4 Level-list portion; notes AST-979 for real DEBUG row UAT |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| astral.config.config-source-of-truth | conforms | No new behavior config; keeps AST-840 inline LOG_LEVELS display filter |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.git.betty-no-src-or-features | conforms | Engineer (Katherine) owns any UI gap-close; not Betty |
| astral.layers.import-direction | conforms | UI-only Files Changed; no new cross-layer imports |
| astral.layers.ui-config-driven-business-logic | conforms | Confirm/reuse existing Level filter; no new React business rules |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Does not open/alter API auth surface |
| astral.standards.data-raises-caller-logs | conforms | No data/core logging changes |
| astral.standards.debug-contract-gated | conforms | No UI debug-contract emissions; persistence stays AST-979 |
| astral.standards.dry-and-focused-functions | conforms | Reuses generic logLevelFilter path; no parallel DEBUG filter |
| astral.standards.in-scope-only | conforms | Only AdminPerformanceMonitor (+ optional App.css); excludes persistence/tests |
| astral.standards.logging-via-utils | conforms | Frontend Level filter only; no backend logging facade change |
| astral.standards.no-cross-contamination | conforms | Stays in ui frontend pages/styles |
| astral.standards.no-hardcoded-sets | conforms | Gap-close only if missing; does not invent new sets or relocate prior AST-840 pattern |
| astral.standards.public-then-helpers | conforms | No restructure of page helpers |
| astral.ui.frontend-file-placement | conforms | Existing page + App.css; no new dirs/modules |
| astral.ui.naming-conventions | conforms | Keeps log_level / LOG_LEVELS / LogViewer names |
| astral.ui.single-gunicorn-worker | conforms | No worker/deploy config edits |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge steps invented |
| orch.git.commit-vocabulary | conforms | Conditional code(AST-980) message matches vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publishes to child sub/* under parent ftr |
| orch.git.ftr-sub-topology | conforms | origin/sub/AST-976/AST-980-… |
| orch.git.merge-on-checkout | conforms | No checkout anti-pattern |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite/force |
| orch.git.no-dev-agent-branches | conforms | Uses authoritative publish ref, not Linear gitBranchName |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-976 |
| orch.git.three-permanent-branches | conforms | No fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Ticket already anticipates confirm-if-present; no product fork |
| orch.pipeline.plan-is-bible | conforms | Single docs/features/foundation plan |
| orch.pipeline.project-scoped-queues | conforms | Foundation child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready → validate-plan |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly bans engineer test/bible edits; leaves qa-child to Betty |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Katherine per parent Team table |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign to Katherine on Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Planned UI paths are engineer-allowed |

## Considered and excluded

**Considered:** astral.config.config-source-of-truth; astral.config.secrets-and-env-specific-from-environ; astral.git.betty-no-src-or-features; astral.layers.import-direction; astral.layers.ui-config-driven-business-logic; astral.patterns.require-auth-on-protected-endpoints; astral.standards.data-raises-caller-logs; astral.standards.debug-contract-gated; astral.standards.dry-and-focused-functions; astral.standards.in-scope-only; astral.standards.logging-via-utils; astral.standards.no-cross-contamination; astral.standards.no-hardcoded-sets; astral.standards.public-then-helpers; astral.ui.frontend-file-placement; astral.ui.naming-conventions; astral.ui.single-gunicorn-worker; orch.git.betty-merge-tests-one-sha; orch.git.commit-vocabulary; orch.git.flow-direction-inviolable; orch.git.ftr-sub-topology; orch.git.merge-on-checkout; orch.git.no-cherry-pick-rebase-force; orch.git.no-dev-agent-branches; orch.git.one-epic-worktree-per-parent; orch.git.three-permanent-branches; orch.pipeline.call-susan-for-product-decisions; orch.pipeline.plan-is-bible; orch.pipeline.project-scoped-queues; orch.pipeline.status-gates-skill-entry; orch.roles.archie-approves-statutes; orch.roles.betty-owns-test-tree; orch.roles.chuckles-never-ticket-assignee; orch.roles.engineer-assignee-through-resolve; orch.roles.pre-commit-path-bans

**Excluded:**
- astral.agent.confidence-bounds — layers ∩ ui empty
- astral.agent.do-task-delegation — layers ∩ ui empty
- astral.agent.grade-vector-validation — layers ∩ ui empty
- astral.batch.batch-id-first — layers ∩ ui empty
- astral.batch.batch-id-format — layers ∩ ui empty
- astral.batch.claim-process-release — layers ∩ ui empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ ui empty
- astral.config.pass-threshold-vs-score-floor — layers ∩ ui empty
- astral.debug.no-repo-root-artifacts-dir — paths miss plan UI files
- astral.debug.spikes-under-debug-dir — paths miss plan UI files
- astral.docs.features-single-file-per-ticket — layers ∩ ui empty
- astral.git.engineer-test-tree-ban — paths miss plan UI files
- astral.layers.core-vs-external-bright-line — layers ∩ ui empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ ui empty
- astral.patterns.coat-check-never-store-empty — layers ∩ ui empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ ui empty
- astral.standards.database-header-inventory — layers ∩ ui empty
- astral.standards.utils-data-late-import-only — layers ∩ ui empty
- astral.state.core-decides-transitions — layers ∩ ui empty
- astral.state.job-prior-states-enforced — layers ∩ ui empty
- astral.state.no-daisy-chain-in-run — layers ∩ ui empty

## Findings

None fix-now.

- **acceptable:** Current tree already has `LOG_LEVELS` including DEBUG, generic `visibleLogs` filter/Copy/empty-state, and `.dispatch-log-level-debug` — Stage 2 no-op is the expected happy path; Stage 1 citation comment remains required before build-child closes.

Self-assessment (minor / high / low) is honest.

— Joan
context_tokens≈48000

#### katherine — 2026-07-24T00:13:10.282Z
Plan: [ast-980-add-debug-to-execution-history-level-list.md](https://github.com/susansomerset/astral/blob/sub/AST-976/AST-980-add-debug-to-execution-history-level-list/docs/features/foundation/ast-980-add-debug-to-execution-history-level-list.md) @ `8bfb558`

**Scope:** `minor` — confirm-or-gap-close on Execution History Level list (`AdminPerformanceMonitor.tsx` + optional CSS); no persistence (AST-979).

**Conf:** `high` — AST-840 already ships `LOG_LEVELS` including DEBUG with generic filter/Copy/empty-state; ticket text anticipates confirm-if-present.

**Risk:** `low` — display-only Level option; wrong filter affects triage UX only.

---

# AST-980 — Add DEBUG to Execution History Level list

**Linear:** [AST-980](https://linear.app/astralcareermatch/issue/AST-980/add-debug-to-execution-history-level-list-add-level-debug-to-app-log)  
**Parent:** [AST-976 — Add level "DEBUG" to app_log table](https://linear.app/astralcareermatch/issue/AST-976/add-level-debug-to-app_log-table)  
**Publish ref:** `origin/sub/AST-976/AST-980-add-debug-to-execution-history-level-list`

Execution History’s Level control must list **DEBUG** so Susan can filter expanded batch logs to DEBUG-only (filter, Copy, and empty-state consistent with other levels). This ticket does **not** own `app_log` persistence (sibling **AST-979**). Prior Level-filter work (**AST-838** / **AST-840**) already shipped DEBUG in the dropdown — this plan **confirms** that coverage and closes a gap **only if** something is missing.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | **Only if Stage 1 finds a gap:** ensure `LOG_LEVELS` includes `"DEBUG"` (first option after All), and that `LogViewer` strict-equality filter / empty-state / Copy treat DEBUG like INFO/WARNING/ERROR. **If Stage 1 confirms present:** do **not** edit this file. | ui |
| `src/ui/frontend/src/App.css` | **Only if** `.dispatch-log-level-debug` is missing when Stage 1 runs: restore the muted DEBUG level color rule. **If present:** do not edit. | ui |

No backend, config, dispatcher, or ledger-column changes. No edits under `tests/` or `docs/test-bible/` (Betty owns those).

## Dependency note (not this ticket’s code)

- **AST-979** owns persisting debug-gated emissions as `app_log.level = DEBUG`. End-to-end UAT of parent AC4 against **real** DEBUG rows requires AST-979 on the integration line. This ticket only owns the Execution History Level list + client filter behavior for the string `"DEBUG"`.
- Build may complete on confirmation alone; do not implement persistence or invent fixture DB rows here.

## Stage 1: Confirm AST-840 DEBUG Level coverage

**Done when:** A Linear comment on **AST-980** cites the exact current lines proving (or disproving) DEBUG presence and filter behavior. No product commit yet.

1. In `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, open the module-level `LOG_LEVELS` constant. Record whether it is exactly `["DEBUG", "INFO", "WARNING", "ERROR"]` (order may match AST-840; DEBUG must be present as a selectable option).
2. Confirm the Level `<select>` maps `LOG_LEVELS` into `<option>` elements under the existing empty-value **All** option, and that selection is stored via `setFilter("log_level", …)` / `searchParams.get("log_level")` (URL-backed).
3. In `LogViewer`, confirm `visibleLogs` filters with `entry.level === logLevelFilter` when `logLevelFilter` is non-empty (so `log_level=DEBUG` shows only rows whose `level` field is the string `"DEBUG"`).
4. Confirm empty-state order: (a) loading; (b) `logs.length === 0` → `No log entries for this batch.`; (c) `visibleLogs.length === 0` → ``No '${logLevelFilter}' type log entries for this batch.`` — so Level=DEBUG with a batch that has only INFO yields the filtered-empty message, not the zero-log message.
5. Confirm `copyLogs` joins `visibleLogs` only (filtered Copy).
6. In `src/ui/frontend/src/App.css`, confirm `.dispatch-log-level-debug` exists (muted color for Level column).
7. Post a Linear comment on **AST-980** with the six findings as a checklist (present / missing per item), including file:line citations for `LOG_LEVELS`, `visibleLogs`, filtered-empty string, and CSS rule.

⚠️ **Decision:** Prefer confirm-over-rewrite. AST-840 already intended DEBUG in the Level list; do not refactor filter architecture, move `LOG_LEVELS` to config, or change ledger fetch. Client-side filter on `/api/admin/dispatch_ledger/<batch_id>/logs` remains the contract.

## Stage 2: Gap-close (conditional) or no-op product delta

**Done when:** Either (A) DEBUG is confirmed complete and **no** product files were changed, or (B) any missing pieces from Stage 1 are fixed in a single product commit on this publish ref.

1. If Stage 1 found **DEBUG missing** from `LOG_LEVELS`: add `"DEBUG"` to `LOG_LEVELS` so the Level dropdown options are `All`, `DEBUG`, `INFO`, `WARNING`, `ERROR` (same order as AST-840 / existing Betty assertion in `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`).
2. If Stage 1 found filter / empty-state / Copy broken for DEBUG specifically (e.g. special-casing that excludes DEBUG): restore the generic `logLevelFilter` strict-equality path so DEBUG behaves identically to INFO/WARNING/ERROR. Do not add DEBUG-only branches.
3. If Stage 1 found `.dispatch-log-level-debug` missing: add `.dispatch-log-level-debug { color: var(--text-muted); }` next to the other `.dispatch-log-level-*` rules in `App.css`.
4. If Stage 1 found **all six items present**: make **no** product file edits. Proceed to Stage 3 with a no-op product delta.
5. If any of steps 1–3 applied: commit on the epic worktree with message `code(AST-980): ensure DEBUG on Execution History Level list` and push to `origin/sub/AST-976/AST-980-add-debug-to-execution-history-level-list`.

## Stage 3: Acceptance lock for build-child / UAT handoff

**Done when:** Linear comment on **AST-980** states how parent AC4 Level-list portion is satisfied, and ticket is ready for Code Complete handoff to Betty (no engineer-owned test edits).

1. Re-state AC4 Level-list portion: Level control lists DEBUG; with `log_level=DEBUG`, expanded log shows only `level === "DEBUG"` rows; with `log_level=INFO`, DEBUG rows are hidden and INFO rows remain.
2. Explicitly note: proving AC4 against a **debug=True** batch with real DEBUG `app_log` rows is blocked on **AST-979** merge/UAT data; UI Level-list readiness does not wait on inventing persistence in this ticket.
3. Do **not** edit Betty’s AST-840 tests. If Stage 2 changed product code, leave regression coverage to Betty’s `qa-child` (existing AST-840 describe already asserts dropdown options include DEBUG).
4. Move Linear status to **Code Complete** only after Stage 1 comment exists and Stage 2 is either no-op or published — follow **build-child** status rules (this stage documents the acceptance lock for that skill; plan-child itself stops at Plan Ready).

## Self-Assessment

**Scope:** `minor` — confirm-or-gap-close on one React page (+ optional one CSS rule); no backend or persistence.

**Conf:** `high` — current tree already has `LOG_LEVELS` including DEBUG, generic `LogViewer` filter/Copy/empty-state, and `.dispatch-log-level-debug`; ticket text anticipates confirm-if-present.

**Risk:** `low` — display-only Level option; wrong filter would affect triage UX only; persistence and WARNING/ERROR paths are out of scope / unchanged.

## Rules check (ASTRAL_CODE_RULES)

- §1.5 / §1.5.1: not touched — persistence remains AST-979; UI has no debug-logging requirement.
- §1.3 DRY: reuse existing Level filter path; no parallel DEBUG filter.
- §2.1: `LOG_LEVELS` stays inline next to `STATUSES` (same AST-840 pattern; display filter, not entity state machine).
- §2.4 / §2.6: N/A (no batch claim / state machine).
- §3.3: UI-only; no new cross-layer imports.
- §3.5: no new modules; keep existing names (`log_level`, `LOG_LEVELS`, `LogViewer`).
- §3.6: no spike artifacts committed.

## Review (build)

**Built:** `origin/sub/AST-976/AST-980-add-debug-to-execution-history-level-list` @ `cb48b91959142f58de35e7e551199f1e69e7699c`

Stage 1: Confirmed AST-840 DEBUG Level coverage (all six checklist items present).  
Stage 2: No-op product delta — no edits to `AdminPerformanceMonitor.tsx` or `App.css`.  
Stage 3: AC4 Level-list portion satisfied by existing UI; real DEBUG row UAT waits on AST-979.

## Radia review (code-rubric.v1)

`[code-rubric] revision=1`

**Overall:** DISCUSS (no fix-now)

**Publish ref tip (pre-docs):** `7775aa225d190babb1f8188c40bd1debb903cb5d`

### What’s solid

- Confirm-only delivery matches plan Stages 1–3: Katherine Stage 1 checklist + Stage 3 lock on Linear; Stage 2 no-op product delta.
- Independent re-check vs `origin/dev`: `LOG_LEVELS` includes DEBUG (`AdminPerformanceMonitor.tsx:40`); URL `log_level` + select (`:146`, `:314–318`); `visibleLogs` strict equality (`:445–448`); filtered-empty / Copy on `visibleLogs`; `.dispatch-log-level-debug` (`App.css:1938`).
- Three-dot vs `origin/dev` has **no** `src/` edits — persistence stays AST-979; Betty reuses AST-840 Level-filter coverage.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` against plan UI Files Changed. Net three-dot diff is docs/bible/tests only, so those statutes score in-scope here. Content still **conforms**. No product fix.

### Recommended actions

- Resolve-child: accept discuss stragglers / no product delta; move to User Testing when ready.
- End-to-end DEBUG row UAT still depends on AST-979 persistence on the integration line.

## Resolution

**Date:** 2026-07-25  
**Commit:** `resolve(AST-980): — clean`

- **fix-now:** none — no product changes.
- **discuss (C4 straggler):** Accepted as process note only (Joan exclude vs post-Betty net diff). Statutes still conform; no product or plan-doc rewrite required.
- **Outcome:** Confirm-only child remains as shipped; User Testing for Level-list AC4 UI portion. Real DEBUG `app_log` rows still wait on AST-979.
