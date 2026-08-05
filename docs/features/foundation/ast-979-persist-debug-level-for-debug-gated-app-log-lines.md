<!-- linear-archive: AST-979 archived 2026-08-05 -->

## Linear archive (AST-979)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-979/persist-debug-level-for-debug-gated-app-log-lines-add-level-debug-to  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-976 — Add level "DEBUG" to app_log table  
**Blocked by / blocks / related:** parent: AST-976; blocks: AST-980

### Description

## What this implements

Debug-gated backend emissions persist as **DEBUG** in `app_log` when **debug=True**; production INFO/WARNING/ERROR unchanged when **debug=False**; persistence path does not drop DEBUG. Does **not** own Execution History Level list UI.

## Acceptance criteria

1. On a backend run with **debug=True** that emits debug-contract lines, `app_log` contains rows with level **DEBUG** for those emissions (verifiable via Execution History **Level = DEBUG** and/or direct inspection of `app_log`).
2. On an otherwise comparable run with **debug=False**, those same debug-contract lines do **not** appear as DEBUG (or at all); ordinary production INFO/WARNING/ERROR rows still appear as today.
3. Ordinary INFO lines that are not debug-gated still persist as **INFO** on both debug=True and debug=False runs (debug mode does not re-label all INFO as DEBUG).
4. WARNING and ERROR persistence and display behavior are unchanged.

## Boundaries

Does **not** own Execution History Level list UI (sibling child). Does **not** backfill historical INFO rows. Does **not** redesign AST-538 debug contract content/shape — stored severity only. Must preserve late-import utils→data cycle guard for `app_log` writes.

## Notes for planning

Backend debug contract: AST-538 / Code Rules §1.5.1. Logging via utils logging module; DB handler writes app_log via late import. Sibling owns Level=DEBUG on Execution History.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-976-add-level-debug-to-app_log-table`, child `sub/AST-976/<this-id>-…`. Created at dispatch-parent. Publish to origin/<sub-ref> only.

### Comments

#### chuckles — 2026-07-25T19:04:25.204Z
[merge-child] blocked: validate-sub-log after restack — missing `plan(AST-979):` and `merge-tests(AST-979):` on `origin/sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines` (cherry-pick restack dropped merge-tests; plan was only `docs(…): plan`). @Ada Lovelace: on epic worktree, checkout publish ref, `git commit --allow-empty -m "plan(AST-979): — sequence label for merge-child gate"`, push `--force-with-lease` if needed. Stay User Testing. @Betty White: re-deliver `merge-tests(AST-979): origin/tests beae6c5b4eaa15dec0de359d4e085a4e2a31f978` onto that tip.

— Chuckles

#### chuckles — 2026-07-25T19:00:11.194Z
[merge-child] blocked: git pull merge on sub — subjects starting with `Merge remote-tracking branch` (e.g. b7766d6, 5a8b857). @Ada Lovelace: rebase onto `origin/ftr/AST-976-add-level-debug-to-app_log-table`, drop pull-merge commits, `git push --force-with-lease` to `origin/sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines`. Stay User Testing.

— Chuckles

#### radia — 2026-07-24T01:34:11.387Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-979
**Publish ref:** `origin/sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines` @ `a083770e8b3ca15eeafef7d0f883ab404dfa466e`
**Overall:** DISCUSS

Baseline: `origin/dev` three-dot vs publish-ref. Product delta: `src/utils/logging.py` only (+ plan/bible/tests from pipeline).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | not-applicable | paths miss (src/core/**, src/utils/config.py) |
| astral.agent.do-task-delegation | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.batch.batch-id-first | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.batch.batch-id-format | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.batch.claim-process-release | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.config.config-source-of-truth | scoped | conforms | no new behavior-driving config; stdlib levels only |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | paths miss (no config.py / core / data) |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets or env-specific values |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features plan doc is not a spike (C4 straggler vs Joan exclude) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single foundation plan file for AST-979 (C4 straggler vs Joan exclude) |
| astral.git.betty-no-src-or-features | scoped | conforms | src/features from engineer/plan; Betty only tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree via test(AST-979)/merge-tests (C4 straggler vs Joan exclude) |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.layers.import-direction | scoped | conforms | utils-only product edit; late-import exception preserved |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | paths miss src/ui/** / config.py |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.standards.debug-contract-gated | scoped | conforms | gates/shape/prefix/truncation unchanged; severity DEBUG only |
| astral.standards.dry-and-focused-functions | scoped | conforms | emit-site + handler threshold; no handler remapping |
| astral.standards.in-scope-only | scoped | conforms | product = logging.py; UI/schema/backfill excluded |
| astral.standards.logging-via-utils | scoped | conforms | change stays in utils logging facade |
| astral.standards.no-cross-contamination | scoped | conforms | no new cross-layer deps |
| astral.standards.no-hardcoded-sets | scoped | conforms | logging.DEBUG/INFO only; no new enums |
| astral.standards.public-then-helpers | scoped | conforms | existing method layout retained |
| astral.standards.utils-data-late-import-only | scoped | conforms | add_log_entry late import in _flush_buffer untouched |
| astral.state.core-decides-transitions | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.state.job-prior-states-enforced | scoped | not-applicable | paths miss |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ∩ {utils,docs} empty |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | paths miss |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-979) one-sha from origin/tests |
| orch.git.commit-vocabulary | universal | conforms | code/test/docs/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | publish on child sub/* only |
| orch.git.ftr-sub-topology | universal | conforms | sub/AST-976/AST-979-… under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | no checkout anti-pattern in delivery |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rewrite/force on publish path |
| orch.git.no-dev-agent-branches | universal | conforms | ignored Linear gitBranchName; used publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | reviewed in astral-AST-976 |
| orch.git.three-permanent-branches | universal | conforms | no fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | severity correction already in definition |
| orch.pipeline.plan-is-bible | universal | conforms | docs/features/foundation/ast-979-….md |
| orch.pipeline.project-scoped-queues | universal | conforms | Foundation child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | bible/tests via Betty test() commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Chuckles not assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | review-child leaves assignee unchanged |
| orch.roles.pre-commit-path-bans | universal | conforms | docs() only on features plan path |

## Pattern conformance

none cited

## Plan adherence

Stage 1 delivered exactly: helpers → `Logger.debug`; `set_debug_flag` raises/restores named logger; `__init__` routes through `set_debug_flag`; handler `setLevel(DEBUG)`; late-import flush preserved; no UI/schema/call-site backfill. Self-Assessment Scope `Single-Component` matches footprint. Sibling AST-980 boundary held.

## Findings

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` against plan Files Changed (`logging.py` only). Net three-dot diff vs `origin/dev` includes `docs/features/**`, `docs/test-bible/**`, and `tests/**`, so those statutes score in-scope. Content still **conforms** — no product fix.

**advisory:** Handler `setLevel(DEBUG)` is process-wide once attached; root stays INFO (Joan plan-time note). Acceptable per plan.

**fix-now:** none

### What’s solid

- AC 1–4 covered at emit + handler threshold without remapping in `_DatabaseLogHandler`.
- AST-538 contract shape unchanged; §5f gates intact.
- Betty asserts DEBUG persistence / silence / INFO stays INFO / WARN+ERROR / level restore.

### Notes

Joan plan-rubric verdict attached (APPROVED). Stragglers above are plan-time exclude vs post-Betty net diff only.

context_tokens≈28000

#### betty — 2026-07-24T01:15:26.951Z
## QA test manifest

`origin/sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines` @ `41ce3ed` (`merge-tests(AST-979): origin/tests beae6c5`)

### Broken / revised
1. `TestPrefixedLoggerDebugGating` emit paths — `caplog.set_level(DEBUG)` (was INFO; would miss DEBUG records) + assert `levelname == DEBUG`

### Gaps (new)
2. `TestAst979DebugLevelPersistence::test_debug_gated_helpers_buffer_debug_when_flag_true` — `debug_index` / `debug_detail` / `test` → buffer `level=DEBUG`
3. `…::test_debug_gated_helpers_silent_when_flag_false` — no buffer entries
4. `…::test_ordinary_info_stays_info_with_debug_flag_true` — plain `info` stays `INFO`
5. `…::test_warning_and_error_levels_unchanged`
6. `…::test_set_debug_flag_false_restores_named_logger_level`

### Existing regression
7. `tests/component/utils/test_logging_batch.py` (full file)

### Narrowed run
```bash
.venv/bin/python -m pytest tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

### Bible
`docs/test-bible/utils/debug_logging.md` — `### AST-979 · AST-976` — shasum `7648e668721a3b536bcab477303d9e2c3ebf3e43`

No UI Level-list coverage (AST-980).

#### joan — 2026-07-24T00:19:33.975Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-979
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages

| Parent AC (AST-976) | Plan coverage |
| -- | -- |
| 1. debug=True debug-contract lines persist as DEBUG in app_log | Stage 1 (helpers → Logger.debug; handler setLevel DEBUG; flush path unchanged) |
| 2. debug=False: those lines absent; ordinary INFO/WARNING/ERROR unchanged | Stage 1 (gates kept; named-logger level restored to INFO when flag False; info/warning/error paths untouched) |
| 3. Ordinary non-gated INFO stays INFO on both modes | Stage 1 (plain logger.info still INFO; no remapping in handler) |
| 4. Execution History Level lists DEBUG; Level=DEBUG filters work | N/A — boundary: child Description “Does not own Execution History Level list UI (sibling child)” / plan Files Changed excludes AdminPerformanceMonitor (AST-980) |
| 5. WARNING and ERROR persistence/display unchanged | Stage 1 (WARNING/ERROR emit paths unchanged; display owned by sibling) |

### Plan stages → definition

| Plan stage | Maps to |
| -- | -- |
| Stage 1: Persist debug-gated lines as DEBUG | Purpose (stored severity correction); Functional scope bullets DEBUG for gated emissions / INFO remains INFO / persistence accepts DEBUG; child AC 1–4; Boundaries (no UI, no backfill, no contract redesign, late-import preserved) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| astral.config.config-source-of-truth | conforms | No new behavior-driving config; uses stdlib logging levels only |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets or env-specific values introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer (Ada) owns src edit; plan is not Betty test-tree work |
| astral.layers.import-direction | conforms | Single utils file; preserves late-import exception only |
| astral.standards.debug-contract-gated | conforms | Gates, header shape, detail prefix, truncation unchanged; severity only |
| astral.standards.dry-and-focused-functions | conforms | Emit-site severity fix; no duplicate handler remapping |
| astral.standards.in-scope-only | conforms | Only logging.py; explicitly excludes UI, schema, call-site backfill |
| astral.standards.logging-via-utils | conforms | Change stays inside utils logging facade |
| astral.standards.no-cross-contamination | conforms | No new cross-layer deps |
| astral.standards.no-hardcoded-sets | conforms | No new enums/sets; logging.DEBUG/INFO only |
| astral.standards.public-then-helpers | conforms | Existing method layout retained |
| astral.standards.utils-data-late-import-only | conforms | Plan forbids moving/removing add_log_entry late import in _flush_buffer |
| orch.git.betty-merge-tests-one-sha | conforms | Plan does not invent Betty merge mechanics |
| orch.git.commit-vocabulary | conforms | No commit steps that violate vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child sub/* under parent ftr |
| orch.git.ftr-sub-topology | conforms | Uses authoritative sub/AST-976/AST-979-… ref |
| orch.git.merge-on-checkout | conforms | N/A to plan content; no checkout anti-pattern prescribed |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite/force operations in plan |
| orch.git.no-dev-agent-branches | conforms | No Linear gitBranchName as publish ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-976 only |
| orch.git.three-permanent-branches | conforms | Does not invent fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | No product ambiguity; severity correction is in definition |
| orch.pipeline.plan-is-bible | conforms | Single plan doc under docs/features/foundation/ |
| orch.pipeline.project-scoped-queues | conforms | Foundation child only; no cross-project queue claim |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready → validate-plan path respected |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits in Files Changed |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer is Ada per parent Team table |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign to Ada on Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Planned paths are allowed engineer src |

## Considered and excluded

**Considered:** astral.config.config-source-of-truth; astral.config.secrets-and-env-specific-from-environ; astral.git.betty-no-src-or-features; astral.layers.import-direction; astral.standards.debug-contract-gated; astral.standards.dry-and-focused-functions; astral.standards.in-scope-only; astral.standards.logging-via-utils; astral.standards.no-cross-contamination; astral.standards.no-hardcoded-sets; astral.standards.public-then-helpers; astral.standards.utils-data-late-import-only; orch.git.betty-merge-tests-one-sha; orch.git.commit-vocabulary; orch.git.flow-direction-inviolable; orch.git.ftr-sub-topology; orch.git.merge-on-checkout; orch.git.no-cherry-pick-rebase-force; orch.git.no-dev-agent-branches; orch.git.one-epic-worktree-per-parent; orch.git.three-permanent-branches; orch.pipeline.call-susan-for-product-decisions; orch.pipeline.plan-is-bible; orch.pipeline.project-scoped-queues; orch.pipeline.status-gates-skill-entry; orch.roles.archie-approves-statutes; orch.roles.betty-owns-test-tree; orch.roles.chuckles-never-ticket-assignee; orch.roles.engineer-assignee-through-resolve; orch.roles.pre-commit-path-bans

**Excluded:**
- astral.agent.confidence-bounds — paths miss src/utils/logging.py
- astral.agent.do-task-delegation — layers ∩ utils empty
- astral.agent.grade-vector-validation — layers ∩ utils empty
- astral.batch.batch-id-first — layers ∩ utils empty
- astral.batch.batch-id-format — layers ∩ utils empty
- astral.batch.claim-process-release — layers ∩ utils empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ utils empty
- astral.config.pass-threshold-vs-score-floor — paths miss src/utils/logging.py
- astral.debug.no-repo-root-artifacts-dir — paths miss src/utils/logging.py
- astral.debug.spikes-under-debug-dir — paths miss src/utils/logging.py
- astral.docs.features-single-file-per-ticket — layers ∩ utils empty
- astral.git.engineer-test-tree-ban — paths miss src/utils/logging.py
- astral.layers.core-vs-external-bright-line — layers ∩ utils empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ utils empty
- astral.layers.ui-config-driven-business-logic — paths miss src/utils/logging.py
- astral.patterns.coat-check-never-store-empty — layers ∩ utils empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ utils empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ utils empty
- astral.standards.data-raises-caller-logs — layers ∩ utils empty
- astral.standards.database-header-inventory — layers ∩ utils empty
- astral.state.core-decides-transitions — layers ∩ utils empty
- astral.state.job-prior-states-enforced — paths miss src/utils/logging.py
- astral.state.no-daisy-chain-in-run — layers ∩ utils empty
- astral.ui.frontend-file-placement — layers ∩ utils empty
- astral.ui.naming-conventions — layers ∩ utils empty
- astral.ui.single-gunicorn-worker — paths miss src/utils/logging.py

## Findings

None fix-now.

- **discuss** (acceptable for build): `_DatabaseLogHandler.setLevel(DEBUG)` is process-wide once attached, not toggled with `debug_flag`. Plan correctly keeps root at INFO so third-party DEBUG stays filtered at source; Ada should not raise root if debugging the flood risk during build.

Self-assessment (Single-Component / high / Medium) matches the plan.

— Joan
context_tokens≈42000

#### ada — 2026-07-24T00:10:43.685Z
Plan: [ast-979-persist-debug-level-for-debug-gated-app-log-lines.md](https://github.com/susansomerset/astral/blob/sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines/docs/features/foundation/ast-979-persist-debug-level-for-debug-gated-app-log-lines.md) @ d6eb73a

**Scope:** Single-Component — one utils module (src/utils/logging.py); no data schema, no UI, no call-site backfill.

**Conf:** high — root cause is local (helpers call info; handler setLevel INFO); add_log_entry already accepts free-text level; AST-538 gating and late-import flush path stay intact.

**Risk:** Medium — logging is process-wide; wrong root-level change would flood third-party DEBUG, and failing to lower the handler would drop DEBUG entirely. Mitigated by named-logger-only level raise + explicit handler setLevel(DEBUG).

---

# AST-979 — Persist DEBUG level for debug-gated app_log lines

**Linear:** [AST-979 — Persist DEBUG level for debug-gated app_log lines](https://linear.app/astralcareermatch/issue/AST-979/persist-debug-level-for-debug-gated-app-log-lines-add-level-debug-to)  
**Parent:** [AST-976 — Add level "DEBUG" to app_log table](https://linear.app/astralcareermatch/issue/AST-976/add-level-debug-to-app_log-table)  
**Publish ref:** `origin/sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines`

Debug-gated backend emissions (`debug_index` / `debug_detail` / `debug_detail_block` / `test`) currently call `Logger.info`, so `_DatabaseLogHandler` stores them as `level=INFO` in `app_log` and they are indistinguishable from ordinary production INFO. This ticket corrects **stored severity only**: when `debug_flag=True`, those helpers emit at Python `DEBUG` and the DB handler persists `level=DEBUG`; when `debug_flag=False` they still emit nothing; ordinary `info` / `warning` / `error` paths and the late-import `add_log_entry` flush stay unchanged. Execution History Level-list UI is **AST-980** (out of scope).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/logging.py` | Emit debug-gated helpers at DEBUG; raise named-logger level when `debug_flag=True`; set `_DatabaseLogHandler` level to DEBUG so records are not dropped; update docstrings that still say INFO | utils |

No other files. Do **not** edit `src/data/database.py` (`add_log_entry` already accepts free-text `level`; `app_log.level` is `TEXT`). Do **not** edit Execution History UI (`AdminPerformanceMonitor.tsx` — AST-980). Do **not** mass-migrate grandfathered `logger.info("[DEBUG] …")` call sites. Do **not** change AST-538 message shape (`format_debug_index_header`, `DEBUG_DETAIL_PREFIX`, truncation).

## Stage 1: Persist debug-gated lines as DEBUG

**Done when:** With a `_PrefixedLogger` that has `debug_flag=True`, calling `debug_index` / `debug_detail` / `debug_detail_block` / `test` produces buffered handler entries whose `level` is the string `DEBUG` (and after `flush_log_buffer`, matching `app_log` rows). The same calls with `debug_flag=False` produce no entries. A plain `logger.info("…")` still buffers/persists as `INFO`. WARNING/ERROR unchanged. Late import of `add_log_entry` inside `_flush_buffer` is preserved.

1. In `src/utils/logging.py`, in `_PrefixedLogger.set_debug_flag`, after assigning `self._debug_flag = flag`:
   - When `flag` is `True`, call `self._logger.setLevel(logging.DEBUG)` so `Logger.debug` / `isEnabledFor(DEBUG)` succeed on that named logger (root stays at INFO via existing `basicConfig` — do **not** raise the root logger to DEBUG; that would flood third-party `httpcore` / similar DEBUG).
   - When `flag` is `False`, if `self._logger.level == logging.DEBUG`, call `self._logger.setLevel(logging.INFO)` so a later non-debug use of the same named logger does not leak bare `.debug()` emissions into `app_log`.
2. In `_PrefixedLogger.__init__`, after storing `self._logger`, call `self.set_debug_flag(debug_flag)` (instead of only assigning `self._debug_flag`) so `get_logger(..., debug_flag=True)` applies the same level rule as an explicit `set_debug_flag(True)`.
3. In `_PrefixedLogger.test`, replace `self._logger.info(f"[ ~ ] {message}")` with `self._logger.debug(f"[ ~ ] {message}")` (keep the `[ ~ ]` prefix and the `if self._debug_flag:` gate).
4. In `_PrefixedLogger.debug_index`, replace `self._logger.info(format_debug_index_header(...))` with `self._logger.debug(format_debug_index_header(...))`. Keep the `if not self._debug_flag: return` gate and the keyword-only header args. Update the method docstring from “at INFO” to “at DEBUG”.
5. In `_PrefixedLogger.debug_detail`, replace `self._logger.info(f"{DEBUG_DETAIL_PREFIX}{message}")` with `self._logger.debug(f"{DEBUG_DETAIL_PREFIX}{message}")`. Keep the gate and `DEBUG_DETAIL_PREFIX`. Update the docstring if it implies INFO.
6. Leave `debug_detail_block` as a loop over `debug_detail` (no separate emit). Leave `_PrefixedLogger.debug` as-is (already uses `Logger.debug` with `[ ~ ]`).
7. In `get_logger`, change `_db_handler_instance.setLevel(logging.INFO)` to `_db_handler_instance.setLevel(logging.DEBUG)` so DEBUG records reach `emit` → buffer → `add_log_entry`. Do **not** move or remove the late import of `add_log_entry` inside `_flush_buffer`. Do **not** change `_FLUSH_THRESHOLD`, buffer shape (`level` / `logger_name` / `message` / `batch_id`), stderr failure paths, or `flush_log_buffer`.
8. Update any adjacent comments/docstrings in this file that claim debug-contract helpers log at INFO (module docstring usage block may stay as call-shape examples; method docs must match DEBUG).

⚠️ **Decision:** Fix severity at the `_PrefixedLogger` emit site + handler threshold only — not by remapping message text in `_DatabaseLogHandler`, not by sniffing `DEBUG_DETAIL_PREFIX` / `[ ~ ]`, and not by changing `add_log_entry`. Handler already stores `record.levelname`; once helpers use `Logger.debug`, persisted level is `DEBUG` with no schema change.

⚠️ **Decision:** Include `.test()` in the INFO→DEBUG switch. It is the same `debug_flag` gate as the AST-538 contract helpers and today also pollutes INFO in `app_log`; leaving it on INFO would leave a second debug-gated path mis-labeled. Grandfathered `logger.info("[DEBUG] …")` call sites outside this file stay untouched per parent boundaries.

⚠️ **Decision:** Raise **only** the named module logger when `debug_flag=True`; keep root `basicConfig(level=logging.INFO)`. Propagation still delivers DEBUG records to the root-attached `_DatabaseLogHandler` and stdout handler without enabling third-party DEBUG.

## Self-Assessment

**Scope:** `Single-Component` — one utils module (`src/utils/logging.py`); no data schema, no UI, no call-site backfill.

**Conf:** `high` — root cause is local (helpers call `info`; handler `setLevel(INFO)`); `add_log_entry` already accepts `level` as free text; AST-538 gating and late-import flush path stay intact.

**Risk:** `Medium` — logging is process-wide; wrong root-level change would flood logs, and failing to lower the handler would drop DEBUG entirely (silent AC miss). Mitigated by explicit “do not raise root” and handler `setLevel(DEBUG)` steps.

## Code rules self-review

- **§1.3 DRY:** Single emit-site change on existing helpers; no duplicated severity mapping in the handler.
- **§1.5 / late import:** `_flush_buffer` late import of `add_log_entry` unchanged; still the only utils→data path.
- **§1.5.1 debug contract:** Gating, header shape, `|` detail prefix, and truncation unchanged; only Python/storage severity corrected.
- **§2.1 config:** No new config keys (severity is logging stdlib, not TASK_CONFIG).
- **§2.4 / §2.6:** N/A (no batch claim / state machine).
- **§3.3 imports:** No new cross-layer imports.
- **§3.5 naming:** Existing method names retained.

## Review (build stub)

**Built:** `origin/sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines` @ `ccb2d98`.

**Stages delivered:**
- Stage 1: `src/utils/logging.py` — debug-gated helpers emit via `Logger.debug`; named logger raised to DEBUG when `debug_flag=True` (root stays INFO); `_DatabaseLogHandler.setLevel(DEBUG)`; late-import flush path unchanged — `ccb2d98`.

**Betty:** at **Code Complete** — cover DEBUG vs INFO persistence for `debug_index` / `debug_detail` / `test` under `debug_flag` True/False; confirm ordinary `info` stays INFO; do not require UI Level-list coverage (AST-980).

## Radia review (code-rubric.v1)

`[code-rubric] revision=1`

**Overall:** DISCUSS (no fix-now)

**Publish ref tip (pre-docs):** `41ce3edd4898335fb16e1a2a1a7c0c6c24854df7`

### What’s solid

- Stage 1 matches plan: debug-gated helpers use `Logger.debug`; `set_debug_flag` raises/restores named-logger level; root stays INFO; `_DatabaseLogHandler.setLevel(DEBUG)`; late-import `add_log_entry` in `_flush_buffer` unchanged.
- AC boundaries held: no Execution History UI (AST-980), no schema/`add_log_entry` rewrite, no grandfathered `info("[DEBUG]")` mass migrate.
- Betty coverage asserts DEBUG persistence / silence / INFO stays INFO / WARN+ERROR unchanged / level restore.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` against plan Files Changed (`logging.py` only). Net three-dot diff vs `origin/dev` also includes `docs/features/**`, `docs/test-bible/**`, and `tests/**`, so those statutes score in-scope here. Content still **conforms** (real plan doc, single features file, Betty-owned test-tree commits). No product fix required — note only.

**advisory:** Joan’s plan-time note stands — handler `setLevel(DEBUG)` is process-wide once attached; root stays INFO so third-party DEBUG remains filtered at source.

### Recommended actions

- Resolve-child: accept discuss stragglers / no product delta; move to User Testing when ready.
- Sibling AST-980 owns Level-list UI.

## Resolution

**Date:** 2026-07-24  
**Ref:** Radia `[code-rubric] revision=1` Overall DISCUSS @ `a083770` (intake via merge `origin/<publish-ref>`).

- **fix-now:** none — no product changes.
- **discuss (C4 straggler):** Accepted as noted — statutes score in-scope on net three-dot diff but content **conforms**; no code or plan delta.
- **advisory:** Handler `setLevel(DEBUG)` remains process-wide once attached; root stays INFO per plan — no change.
