<!-- linear-archive: AST-532 archived 2026-06-23 -->

## Linear archive (AST-532)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-532/execution-history-ui-per-hop-rows-and-inspection-per-hop-execution  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-528 — Per-hop Execution History for daisy-chained tasks  
**Blocked by / blocks / related:** parent: AST-528

### Description

## What this implements

Execution History UI correctly lists and inspects per-hop rows for daisy-chained runs: correct task key per row, hop-scoped prompt/response inspection, hop-scoped app logs, and no regression for single-hop dispatch or ad-hoc workbench test rows. Rows display individually (no chain grouping UI).

## Acceptance criteria

5. Rows from one chained run are discoverable as a group (filterable or visually grouped) without collapsing back into a single row.
   * Parent resolution: show tasks as if called individually — natural list order; no special group chrome required.
6. Single-hop dispatch runs and ad-hoc workbench test rows behave as before — no duplicate or missing history rows.

Also verify AC #1–#4 end-to-end in the UI after **AST-531** lands (task column, per-hop inspect, per-hop app logs, per-hop status/cost).

## Boundaries

* Does **not** implement ledger creation — **AST-531**.
* Does **not** change console debug logging — **AST-527**.
* Does not fix caller tokens — **AST-529**.

## Notes for planning

* Primary: `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` and related components.
* API contract comes from **AST-531** — plan against publish ref after blocker merges.
* Vitest §6c for routed page tests per **ASTRAL_TEST_BIBLE**.

## Git branch (authoritative)

Parent `ftr/AST-528-per-hop-execution-history`, child `sub/AST-528/AST-532-execution-history-ui-per-hop`. `blockedBy` **AST-531**.

### Comments

#### radia — 2026-05-30T00:47:18.025Z
## Review (Radia) — `origin/dev...origin/sub/AST-528/AST-532-execution-history-ui-per-hop` @ `1f166417`

**Diff:** 3 files (+342): plan doc, `test_AdminPerformanceMonitor.test.tsx` (`AST-532 per-hop execution history UI` ×6), `docs/ASTRAL_TEST_BIBLE.md` §7.13zn. **No** `AdminPerformanceMonitor.tsx`, **no** `BatchAgentDataModal.tsx`, **no** backend — matches plan Stages 2–3 and sibling boundaries (**AST-531** ledger, **AST-527**/**AST-529** out of scope).

### Plan fidelity
- Self-assessment **`scope-Single-Component`** matches footprint (Vitest + bible manifest only).
- All seven planned Stage 2 cases present: separate hop rows, hop-scoped logs, hop-scoped agent_data modal, `task_key` query param on ledger fetch, adhoc/user prefix regression, FAILED badge (`dispatch-status-fail`).
- No chain-grouping UI — correct per parent AST-528 decision.
- Existing page already keys expand/inspect off `row.batch_id` (**AST-515**); tests lock that contract without redundant page edits.

### ASTRAL_CODE_RULES (§3.3 / §3.5)
- Test-only diff under `tests/component/frontend/pages/` — no layer violations, no new runtime modules, no hardcoded state lists in React.

### Advisory
- **`ASTRAL_TEST_BIBLE.md` §7.13zn** landed in engineer commit; Betty corrected shasum in thread — content aligns with manifest. No action for resolve.
- **`chainHopRowsForToday()`** pins fixture `started_at` to candidate TZ (`America/Los_Angeles`) so rows survive the page’s default `date_from=todayInTz` filter — same intent as existing tests; acceptable.

### Recommended actions
| Severity | Item | Action |
|----------|------|--------|
| — | None | **resolve-astral** may proceed (no fix-now / discuss). |

**UAT note:** Component tests prove batch_id scoping with mocks; parent **AST-528** manual checklist (AC #1–#6 against live chained dispatch after **AST-531** on parent ftr) remains Susan’s UAT pass.

#### betty — 2026-05-30T00:42:46.151Z
**Bible shasum correction:** on `origin/sub/AST-528/AST-532-execution-history-ui-per-hop` after fetch: `800b3ba857b4c4355f3be2365309eae6f1033a2c` (§7.13zn — disambiguated from §7.13zm **AST-522** on this branch).

#### katherine — 2026-05-30T00:37:31.019Z
[check-linear]

**Session scope:** Parent **AST-528** / **Astral Artifacts** — assigned **AST-532**.

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).

**§0b:** `@katherine` issue search (Team Astral). Full threads on **AST-532**, **AST-528**, sibling **AST-531**. **0** actionable @-mention comments.

**§1:** **AST-532** assignee-me — **Plan Approved**. Thread after prior `[check-linear]` (`2026-05-30T00:25`): only Katherine **Stage 1 blocked** note (`00:26`) — no external replies. Sibling **AST-531** now **Tests Passed** with product on `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` @ `634707cc` (Ada) — supersedes plan-only @ `3287b80e`; **AST-532 Stage 1 gate is clear**.

**Pipeline:** Inbox quiet; no `build-astral` from this pass (happy path).

#### katherine — 2026-05-30T00:26:22.322Z
🛑 Stage 1 blocked: AST-531 publish ref has no per-hop ledger commits yet.

Checked `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` @ `3287b80e` — tip is `docs(AST-531): plan` only; diff vs `origin/dev` is the plan doc (+190 lines), no changes under `src/core/`, `src/data/`, or `src/ui/api/`.

Build paused on **dev-kath** per plan Stage 1 step 3. **Ada** needs to land AST-531 product commits on that publish ref before Katherine can merge and proceed with AST-532.

#### katherine — 2026-05-30T00:25:43.743Z
[check-linear]

**Session scope:** Parent **AST-528** / **Astral Artifacts** — assigned **AST-532**. Publish ref `origin/sub/AST-528/AST-532-execution-history-ui-per-hop`.

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). No publish-ref merge (check-linear only; no `build-astral` / `test-astral`).

**§0b:** `@katherine` issue search (Team Astral + **Astral Artifacts** project). Full threads on **AST-532**, parent **AST-528**, sibling **AST-531**. **0** actionable @-mention comments.

**§1:** Assignee-me in **Astral Artifacts**: **AST-532** (active). **Plan Approved**; latest thread is Katherine plan doc @ `2026-05-30T00:23` — no external replies or nags yet. Sibling **AST-531** assignee Ada (Plan Approved); parent git table comment is informational only.

**Pipeline:** Inbox quiet; no `build-astral` from this pass (happy path).

#### katherine — 2026-05-30T00:23:52.976Z
Plan doc: [ast-532-execution-history-ui-per-hop-rows-and-inspection.md](https://github.com/susansomerset/astral/blob/sub/AST-528/AST-532-execution-history-ui-per-hop/docs/features/artifacts/ast-532-execution-history-ui-per-hop-rows-and-inspection.md)

**Self-assessment**

- **Scope:** `scope-Single-Component` — Vitest in `test_AdminPerformanceMonitor.test.tsx` plus at-most-minor Execution History page tweaks; no backend/ledger work (AST-531).
- **Conf:** `conf-Medium` — UI follows AST-515 batch_id-scoped patterns, but build gates on AST-531 publish ref containing product commits; contract documented from parent/sibling definitions until then.
- **Risk:** `risk-Medium` — Execution History is operator-critical for artifact pipeline UAT; regressions on adhoc/user/dispatch rows or wrong batch scoping would block mid-chain prompt debugging.

**Approach:** Stage 1 merges `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` and stops if empty. Stages 2–3 add per-hop Vitest coverage (separate rows, hop-scoped logs + agent_data, task filter, FAILED badge, adhoc/user/dispatch regression) and touch page source only if tests expose a scoping bug — no chain-grouping UI per parent open Q #3.

---

# AST-532 — Execution History UI per-hop rows and inspection

**Linear:** https://linear.app/astralcareermatch/issue/AST-532/execution-history-ui-per-hop-rows-and-inspection-per-hop-execution  
**Parent:** https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks  
**Feature ref:** `sub/AST-528/AST-532-execution-history-ui-per-hop` (origin only)

After **AST-531** creates one `dispatch_ledger` row per daisy-chain hop (distinct `batch_id`, hop-scoped `agent_data` and app logs), this ticket verifies and locks in Execution History UI behavior: each hop appears as its own row with the correct **Task** label, expand shows only that hop’s logs, prompt/response inspection loads only that hop’s blocks, and single-hop dispatch plus **AST-515** / **AST-521** prefixed rows still behave as today. No chain-grouping chrome — rows appear in natural list order like individually dispatched tasks.

---

## AST-531 API contract (build against this — do not implement)

**Blocked by AST-531.** Before **build-astral** Stage 1, merge **`origin/sub/AST-528/AST-531-per-hop-dispatch-ledger`**. If that ref’s tip has no AST-531 product commits (still equals pre-work `origin/dev`), **stop** and comment on AST-532 — do not guess ledger shape.

When AST-531 lands, each executed hop exposes:

| Surface | Contract |
|---------|----------|
| `GET /api/admin/dispatch_ledger` | **One row per executed hop** (no parent/summary row for the entry dispatch Susan clicked). **`task_key`** = plain hop key (e.g. `anticipate_scan`, `contemplate_job`) — same as single-hop dispatch, **not** `adhoc-` / `user-` unless that hop is actually an ad-hoc/craft path. **`batch_id`** unique per hop. **`status`**, **`total_cost`**, count columns reflect **that hop only**. Rows **`ORDER BY started_at DESC`** (existing `list_dispatch_ledger`). |
| `GET /api/admin/dispatch_ledger/<batch_id>/logs` | App log lines where **`app_log.batch_id`** = that hop’s `batch_id` only. |
| `GET /api/agent_data/<batch_id>` | Prompt/response blocks stored under **that hop’s** `batch_id` only (same modal path as **AST-515**). |
| Not in scope | Console debug (**AST-527**), caller tokens (**AST-529**), ledger creation logic (**AST-531**). |

**UI implication (from AST-515):** `AdminPerformanceMonitor.tsx` and `BatchAgentDataModal.tsx` already key list expand, log fetch, and inspection off **`row.batch_id`**. AST-532 adds **tests + regression proof**; page source changes only if tests expose a real scoping bug.

⚠️ **Decision:** No chain-grouping UI (parent AST-528 open Q #3). Do **not** add parent batch column, expandable group, or “chain run” filter — contiguous **`started_at DESC`** order is sufficient discoverability (AC #5).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` | New Vitest cases: multi-hop rows, per-batch logs, per-batch agent_data, task filter, adhoc/user/dispatch regression | tests |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | **Only if** Stage 2 tests fail — minimal fix to row expand / list rendering (expected: **no edit**) | ui |
| `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | **Only if** Stage 2 tests fail — expected: **no edit** | ui |

No changes to `src/ui/api/api_admin.py`, `src/core/*`, or `src/data/database.py` — those belong to **AST-531**.

---

## Stage 1: Dependency gate + contract read

**Done when:** `dev-kath` includes merged **AST-531** publish tip; builder has read AST-531 diff and confirmed list/logs/agent_data endpoints match the table above.

1. On **`dev-kath`**: `git fetch origin && git merge origin/dev` (resolve conflicts; re-check **`BEHIND=0`** vs **`origin/dev`**).
2. `git merge origin/sub/AST-528/AST-531-per-hop-dispatch-ledger`. Resolve conflicts on **`dev-kath`** only; commit merge if needed.
3. If merged tip contains **no** AST-531 implementation (only empty publish seed / parent composite merges), **stop** with Linear comment on AST-532: `🛑 Stage 1 blocked: AST-531 publish ref has no per-hop ledger commits yet`.
4. Read AST-531 changed files (expected hot: `src/core/agent.py`, `src/core/dispatcher.py`, `src/data/database.py`, possibly `src/ui/api/api_admin.py`). Confirm:
   - Each hop calls `save_dispatch_ledger` / `update_dispatch_ledger` with a **new** `batch_id` and hop `task_key`.
   - `log_batch_id.set(batch_id)` scopes logs per hop.
   - `_store_prompt_blocks` / `_store_response_block` use that hop’s `batch_id`.
   - No extra “entry task” ledger row when Susan runs a chain from Scheduled Actions.
5. Re-read `AdminPerformanceMonitor.tsx` expand path: `toggleExpand(row.batch_id)` → `/api/admin/dispatch_ledger/${batchId}/logs`; modal `setAgentDataBatchId(row.batch_id)` → `/api/agent_data/${batchId}`. Note line numbers for Stage 2 test anchors.

---

## Stage 2: Vitest — per-hop rows, scoped inspect, regressions

**Done when:** New tests in `test_AdminPerformanceMonitor.test.tsx` pass via `./scripts/testing/run_component_tests.sh tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`; existing cases in that file still pass.

Extend **`installBaseApiMocks`** pattern already in the file. Mock **`/api/candidates`**, **`/api/agent_data/<batch>`**, **`/api/admin/timesheets?batch_id=`**, ledger list, and per-batch logs.

1. Add shared fixture **`chainHopRows`** (array of three ledger dicts, same `candidate_id`, distinct `batch_id`, `started_at` descending):
   - `{ batch_id: "anticipate_scan-uuid-1", task_key: "anticipate_scan", status: "COMPLETED", total_processed: 1, total_passed: 1, total_cost: 0.01, … }`
   - `{ batch_id: "contemplate_job-uuid-2", task_key: "contemplate_job", status: "COMPLETED", … }`
   - `{ batch_id: "consult_get-uuid-3", task_key: "consult_get", status: "COMPLETED", … }` (single-hop dispatch regression row)

2. **Test `lists separate per-hop rows with correct task keys`:** Mock list endpoint to return `chainHopRows`. Render page. Assert table body contains **`anticipate_scan`**, **`contemplate_job`**, and **`consult_get`** as separate cells (three Task values). Assert no duplicate `batch_id` keys in DOM (one expand control per row).

3. **Test `expands hop-scoped logs per batch_id`:** Mock `/api/admin/dispatch_ledger/anticipate_scan-uuid-1/logs` → `[{ id: "l1", message: "hop-one-log", … }]`. Mock `/api/admin/dispatch_ledger/contemplate_job-uuid-2/logs` → `[{ id: "l2", message: "hop-two-log", … }]`. Expand first hop row (click **`anticipate_scan`** row). Assert **`hop-one-log`** visible, **`hop-two-log`** not. Collapse; expand **`contemplate_job`** row. Assert **`hop-two-log`** visible, **`hop-one-log`** not.

4. **Test `opens hop-scoped agent_data per batch_id`:** Mock `/api/agent_data/anticipate_scan-uuid-1` → `[{ block_type: "RESPONSE", block_data: "\"hop-one-response\"", … }]`. Mock `/api/agent_data/contemplate_job-uuid-2` → `[{ block_type: "RESPONSE", block_data: "\"hop-two-response\"", … }]`. Click “View agent data” on hop 1 → modal shows **`hop-one-response`**. Close; open hop 2 → **`hop-two-response`**.

5. **Test `task filter shows one hop when task_key query set`:** Render with `router: { initialEntries: ["/admin/performance?task_key=anticipate_scan"] }`. Mock list to return full `chainHopRows` (API would filter server-side; for UI test, return only matching row from mock when URL contains `task_key=anticipate_scan`, **or** return all rows and assert client still displays filtered fetch — match existing test pattern at line ~64 that passes query params). Assert **`contemplate_job`** not in document when filter active.

6. **Test `regression adhoc and user prefixed task keys still render`:** Add rows `{ task_key: "adhoc-evaluate_jd", batch_id: "adhoc-b1", … }` and `{ task_key: "user-craft_resume_base", batch_id: "user-b1", … }` to list mock. Assert both Task strings visible alongside chain hops (AST-515 / AST-521 labels unchanged).

7. **Test `failed mid-chain hop shows FAILED badge`:** Add row `{ task_key: "contemplate_job", batch_id: "fail-b", status: "FAILED", total_failed: 1, … }`. Assert element with class **`dispatch-status-fail`** and text **`FAILED`** for that row (AC #4 UI slice).

8. Run:

```bash
cd /Users/susan/chuckles/astral-kath
./scripts/testing/run_component_tests.sh tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx
```

**Betty manifest note (for `qa-astral`, not run in build):** Extend **§7.13k** / parent **AST-528** UAT table with AST-532 Vitest class names above; manual UAT Stage 3 remains Susan’s chain run on parent **AST-528**.

---

## Stage 3: UI source — fix only if Stage 2 exposed a bug

**Done when:** Stage 2 tests pass. If they pass **without** editing page components, post Linear comment: “No `AdminPerformanceMonitor` / `BatchAgentDataModal` source changes — batch_id-scoped UI sufficient after AST-531.”

1. If Stage 2 fails due to UI assuming one row per run (e.g. shared expand state keyed wrong, list dedupe, wrong `batch_id` in log URL): fix **`AdminPerformanceMonitor.tsx`** at the failing path only — do **not** add grouping UI.
2. If **`BatchAgentDataModal`** fails to isolate blocks (unlikely — loads by `batchId` prop): fix modal fetch URL only.
3. Optional polish **only if** Task column truncates hop keys in RTL (unlikely at 120px): in `COLUMNS`, change `task_key` `width` from `120` to `160`. Skip if full task names already visible in tests.
4. Re-run Stage 2 test command until green.

---

## Stage 4: Manual verification (Susan / parent AST-528 UAT)

**Done when:** Parent acceptance criteria **1–6** observable after AST-531 + this ticket on integration branch.

1. Select candidate with timezone; open **Execution History** (today filter).
2. **Scheduled Actions → Run** on a dispatch task whose chain runs ≥2 hops (e.g. `anticipate_scan` → `contemplate_job`). Confirm **separate rows**, correct **Task** column per hop, distinct **`batch_id`** in expand header.
3. Inspect **`anticipate_scan`** row → prompt/response blocks are hop 1 only; inspect **`contemplate_job`** row → hop 2 only (AC #2).
4. Expand app logs on each hop → hop-scoped lines only (AC #3).
5. Confirm per-hop **status** and **Cost**; force or find a mid-chain failure → **FAILED** on that hop’s row only (AC #4).
6. Confirm hops from one run appear in sensible time order without group chrome (AC #5).
7. Run single-hop dispatch and ad-hoc workbench **Test** → one row each, no duplicates/missing rows (AC #6); **`adhoc-`** / **`user-`** prefixes still present where applicable.

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Vitest coverage in `test_AdminPerformanceMonitor.test.tsx` plus at-most-minor Execution History page tweaks; no backend or ledger work.

**Conf:** `conf-Medium` — UI patterns match **AST-515** (batch_id-scoped list/expand/inspect), but implementation depends on **AST-531** landing first; contract is specified from parent/ sibling definitions until publish ref contains product commits.

**Risk:** `risk-Medium` — Execution History is operator-critical for artifact pipeline UAT; missed regression on adhoc/user/dispatch rows or wrong batch scoping would block prompt debugging mid-chain.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.3 DRY | Reuses existing page + modal + API routes; no duplicate ledger or fetch helpers. |
| §2.1 config | No new config blocks. |
| §2.4 batch | UI consumes `batch_id` per row; does not merge hops. |
| §2.6 state machine | No entity state changes. |
| §3.3 imports | Test-only stage touches frontend test tree; page edits stay in `pages/` flat layout. |
| §3.5 naming | No new components; optional width tweak in existing `AdminPerformanceMonitor.tsx`. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

| Field | Value |
|-------|-------|
| Branch | `origin/sub/AST-528/AST-532-execution-history-ui-per-hop` |
| Commit | `1af38309` |
| Stage 1 | Merged `origin/sub/AST-528/AST-531-per-hop-dispatch-ledger` on `dev-kath`; verified `_open_run_next_hop_ledger` / `_finalize_run_next_hop_ledger` per-hop `batch_id` + `log_batch_id` in `agent.py`. |
| Stage 2–3 | No `AdminPerformanceMonitor.tsx` or `BatchAgentDataModal.tsx` edits — list expand (`toggleExpand(row.batch_id)` → `/api/admin/dispatch_ledger/${batchId}/logs`), agent data modal (`batchId` prop → `/api/agent_data/${batchId}`) already hop-scoped per **AST-515**. |
| Betty | Plan Stage 2 Vitest cases (`chainHopRows`, per-hop logs/agent_data, task filter, adhoc/user regression, FAILED badge) — **qa-astral** per build-astral test-tree ban. |

---

## Resolution (2026-05-29, resolve-astral)

| Radia item | Action |
|------------|--------|
| **fix-now** | None — review @ `1f166417` on `origin/sub/AST-528/AST-532-execution-history-ui-per-hop`; resolve proceeds without product edits. |
| **discuss** | None. |
| **advisory — bible §7.13zn shasum** | Betty corrected shasum in thread (`800b3ba8`); content aligns with manifest — no engineer action. |
| **advisory — `chainHopRowsForToday()` TZ pin** | Accepted; same intent as existing Execution History date-filter tests. |

**Outcome:** Vitest-only diff locks per-hop row list, hop-scoped logs/agent_data, task filter, adhoc/user regression, and FAILED badge. No `AdminPerformanceMonitor.tsx` or `BatchAgentDataModal.tsx` source changes — **AST-515** `batch_id`-scoped expand/inspect sufficient after **AST-531**. Parent **AST-528** manual AC #1–#6 remains Susan UAT on integration branch.

**Publish:** `origin/sub/AST-528/AST-532-execution-history-ui-per-hop` @ resolve commit. **§9a:** clean vs `origin/dev` and `origin/ftr/AST-528-per-hop-execution-history`.
