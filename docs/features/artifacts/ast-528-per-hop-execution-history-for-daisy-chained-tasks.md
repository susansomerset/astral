# AST-528 — Per-hop Execution History for daisy-chained tasks

<!-- linear-archive: AST-528 archived 2026-06-23 -->

## Linear archive (AST-528)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When Susan runs a multi-hop artifact pipeline via Scheduled Actions (e.g. `anticipate_scan` chaining through `contemplate_job` and beyond), Execution History today shows a single dispatch row for the entry task. All `run_next` hops share that one batch identifier, so she cannot open each hop's prompt, response, app logs, cost, and status the way she can for a standalone dispatch or ad-hoc workbench test. That blocks UAT of [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) prompt authoring and [AST-516](https://linear.app/astralcareermatch/issue/AST-516/insert-task-anticipate-scan-in-the-daisy-chain) chain wiring — she needs one inspectable history record per agent task in the chain, not one lumped record for the whole run.

## Functional scope

* **Per-hop Execution History rows:** Each task that executes as part of a daisy chain (`run_next`) appears as its own row in Execution History, labeled with that hop's task key (e.g. `anticipate_scan`, then `contemplate_job`), with its own start/end timestamps, status, processed counts, and cost.
* **Per-hop prompt and response inspection:** For each hop row, Susan can expand app logs and open agent prompt/response inspection showing only that hop's call content and model response — the same capabilities Execution History already provides for a single-task dispatch or ad-hoc workbench test.
* **Per-hop logging:** App log lines emitted during a hop are associated with that hop's history record, not commingled under the entry task's batch only.
* **Chain run discoverability:** Rows from the same chained run remain identifiable as belonging together (e.g. shared grouping metadata or sequential ordering Susan can follow) so she can review the full pipeline without losing hop-level granularity.

## Boundaries

* Does **not** change console/server debug logging — that is [AST-527](https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging).
* Does **not** fix caller-token propagation (`{$CALLER_SYSTEM}`, etc.) — that is [AST-529](https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops).
* Does not author Manage Tasks prompts, agent assignment, or `run_next` wiring ([AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)).
* Does not change whether hops execute or in what order — only how completed hops are recorded and surfaced in Execution History.
* Does not add Better Stack or external log shipping; stays on existing `dispatch_ledger` / `app_log` / agent audit storage.
* Must not break single-hop dispatch runs, ad-hoc workbench test history ([AST-515](https://linear.app/astralcareermatch/issue/AST-515/ad-hoc-workbench-test-runs-in-execution-history-include-ad-hoc-calls)), or non-chain batch processing.
* [AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task) originally kept one batch identifier across all hops for audit continuity; this ticket intentionally changes that product expectation for Execution History visibility. Downstream planning must not silently revert to one row per chain.

## Acceptance criteria

1. After a manual **Run** on a dispatch task whose chain includes at least two hops (e.g. `anticipate_scan` → `contemplate_job`), Execution History lists **separate rows** for each executed hop, each showing the correct task key in the Task column.
2. Opening prompt/response inspection on the `anticipate_scan` row shows that hop's prompt blocks and model response only; opening inspection on the `contemplate_job` row shows that hop's content only — no commingling of prior-hop blocks under one batch view.
3. Expanding app logs on each hop row shows log lines for that hop's execution window, not the entire chain under the entry task row only.
4. Each hop row reports its own status (RUNNING / COMPLETED / FAILED) and cost; a failure on a mid-chain hop does not appear as success on that hop's row.
5. Rows from one chained run are discoverable as a group (filterable or visually grouped) without collapsing back into a single row.
6. Single-hop dispatch runs and ad-hoc workbench test rows behave as before — no duplicate or missing history rows.

## Dependencies and blockers

* [AST-281](https://linear.app/astralcareermatch/issue/AST-281/view-execution-history) (Execution History foundation) — Done.
* [AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task) (daisy-chain `run_next` execution) — Done; this ticket revises the history/audit presentation decision documented there.
* [AST-515](https://linear.app/astralcareermatch/issue/AST-515/ad-hoc-workbench-test-runs-in-execution-history-include-ad-hoc-calls) (ad-hoc workbench test ledger pattern) — Done; reference behavior for one inspectable row per LLM call.
* [AST-527](https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging), [AST-529](https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops) — related siblings (console logging and caller tokens); not blockers.

## Open questions

1. Should per-hop history rows apply to **all** `run_next` chains (consult, roster, artifacts), or only dispatch-scheduled runs?
   1. Yes, we want the history for all chained tasks, because that way we can troubleshoot issues with agent responses, etc., mid-chain.
2. Should the entry dispatch row (the task Susan clicked **Run** on) remain as a parent/summary row in addition to per-hop rows, or should only individual hop rows appear?
   1. only individual hop rows should appear. We'll know it's a hop.
3. How should chained rows be grouped in the UI — shared parent batch identifier column, contiguous sort order, expandable group, or filter-by-chain-run?
   1. no, just show the tasks as if they were called individually.  That's how the daisy chain is supposed to work.
4. If a chain aborts mid-hop, should downstream hops that never ran appear in Execution History at all (expected: no)?
   1. No.  Just the ones that ran.

---

## Original brief

I should see the log for "anticipate_scan" with the distinct call and response to the agent for that task, then I should see a separate execution history log for "contemplate_job" with the same ability to see that separate call's content and response as well as the logging for its execution..

### Comments

#### chuckles — 2026-05-30T01:07:31.326Z
## Manual test steps

**Prerequisites:** Local `dev` @ `0b47d4f3` (AST-528 rollup + land-ftr). Restart Flask if already running. Phase E chain wired in Admin → Manage Tasks (`anticipate_scan` → `contemplate_job` or your test chain). Job in `BUILD_ARTIFACTS` with candidate key.

1. **Per-hop rows (AC #1):** Admin → Scheduled Actions → **Run** entry hop on a multi-hop chain. Admin → Execution History: confirm **separate rows** for each executed hop (`anticipate_scan`, then `contemplate_job`, …) with correct **Task** column — **no** single summary row for the entry dispatch alone.
2. **Hop-scoped inspect (AC #2):** On the first hop row → **View agent data** — prompt/response blocks for that hop only. Repeat on second hop — no commingling from hop 1.
3. **Hop-scoped app logs (AC #3):** Expand logs on each hop row — lines for that hop's window only.
4. **Per-hop status/cost (AC #4):** Each row shows its own status and cost. If you can force a mid-chain failure, that hop row shows **FAILED** (not success).
5. **Discoverability (AC #5):** Rows appear individually in natural `started_at DESC` order — no chain grouping UI required.
6. **Regression (AC #6):** Single-hop dispatch **Run** → one row as before. Ad-hoc workbench **Test** → `adhoc-*` row still works. Craft **Generate** → `user-*` row still works.

**Optional automated smoke:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst531RunNextHopLedger \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_run_next_chain_skips_dispatch_level_ledger
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "AST-532 per-hop"
```

**Out of scope:** console hop debug (**AST-527**), caller token propagation (**AST-529**).

`origin/ftr/AST-528-per-hop-execution-history` @ `0b47d4f3` · local `dev` merged (§8). Restart app if running.

Deleted: `sub/AST-528/AST-531-per-hop-dispatch-ledger`, `sub/AST-528/AST-532-execution-history-ui-per-hop`

— Chuckles

#### betty — 2026-05-30T00:37:05.310Z
[check-linear]

**Session scope:** Parent **AST-528** / **Astral Artifacts** — assigned **AST-531**, **AST-532**.

**§0a (`astral-betty` / `dev-betty`):** `git fetch origin`, `checkout dev-betty`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@betty` issue search (Team Astral + **Astral Artifacts** project). Full threads on **AST-528**, **AST-531**, **AST-532** — **0** actionable `@betty` comments.

**§1:** Assignee-me scan blocked by MCP (`assignee: me` JSON); scoped manually to assigned children + parent. No Betty-owned tickets in **AST-528** epic.

**§2:** **0** actionable comments — Katherine’s Stage 1 block note on **AST-532** is informational (pre-**AST-531** product); **AST-531** publish ref now has product @ `634707cc`.

**§5b:** Team-wide **Tests Ready** + latest comment **`[qa-handoff]`** — **0** issues. No handoffs to clear.

**QA (`qa-astral` happy path, assigned ids):**
- **AST-531** — **Tests Passed** (Ada manifest green @ `634707cc`). Betty manifest + bible §7.13zm already on `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` (`ca6306cd` test, `a432caf70569…` bible shasum). No further QA work.
- **AST-532** — **Plan Approved** (Katherine). Blocker **AST-531** product is landed; next gate **`build-astral`**, then Betty **`qa-astral`** on **Code Complete**. Publish ref: `origin/sub/AST-528/AST-532-execution-history-ui-per-hop` (plan only @ `444079d5` today).

**Pipeline:** Inbox quiet; no manifest/test/bible edits this pass.

#### hedy — 2026-05-30T00:25:37.680Z
[check-linear]

**Session scope:** Parent **AST-528** — orchestrator assigned issue ids **(none)** for Hedy. Children **AST-531** (Ada) / **AST-532** (Katherine) only.

**§0a (`astral-hedy` / `dev-hedy`):** `[check-linear] blocked:` — `git merge origin/dev` conflicts; branch diverged (**176** ahead / **10** behind `origin/dev`). Conflict files:
- `docs/ASTRAL_TEST_BIBLE.md`
- `src/core/candidate.py`
- `src/core/consult.py`
- `src/ui/api/api_candidate.py`
- `src/utils/config.py`
- `tests/component/core/test_candidate.py`

Did not resolve — needs Susan/Chuckles direction before integration line is merge-clean.

**§0b:** `@hedy` issue search (Team Astral + **Astral Artifacts** project). Threads on **AST-528**, **AST-531**, **AST-532**, and Hedy-assignee **AST-524** — **0** actionable `@hedy` comments since last `[check-linear]`.

**§1:** No tickets assignee = Hedy under **AST-528**. Exiting per orchestrator (no assigned children).

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral`.

#### chuckles — 2026-05-30T00:22:17.028Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-528 (parent) | ftr/AST-528-per-hop-execution-history |
| AST-531 | sub/AST-528/AST-531-per-hop-dispatch-ledger |
| AST-532 | sub/AST-528/AST-532-execution-history-ui-per-hop |

**Sequencing:** AST-532 `blockedBy` AST-531.

— Chuckles

#### chuckles — 2026-05-29T22:57:46.451Z
@Susan Somerset — open questions on **AST-528** definition:

1. Should per-hop history rows apply to **all** `run_next` chains (consult, roster, artifacts), or only dispatch-scheduled runs?
2. Should the entry dispatch row (the task you clicked **Run** on) remain as a parent/summary row in addition to per-hop rows, or should only individual hop rows appear?
3. How should chained rows be grouped in the UI — shared parent batch identifier column, contiguous sort order, expandable group, or filter-by-chain-run?
4. If a chain aborts mid-hop, should downstream hops that never ran appear in Execution History at all (expected: no)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
