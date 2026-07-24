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
