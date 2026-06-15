# AST-538 — Improve Quality of Debug Logging

<!-- linear-archive: AST-538 archived 2026-06-15 -->

## Linear archive (AST-538)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-546; blocks: AST-545; blocks: AST-544; blocks: AST-543; blocks: AST-542; blocks: AST-541; blocks: AST-540; related: AST-531; related: AST-528

### Description

## Purpose

Susan runs dispatch, roster inflow, consult batches, and ad-hoc agent work with **debug** enabled while authoring prompts and tuning pipelines. When **debug** is on, she means **deep operational visibility** — not a single summary line. She needs to see what each step actually found and stored (e.g. Google CSE hits for a search term, vet outcomes, ingest results) because that data is not yet reproducible in unit tests and must appear during user testing. Today the console mixes ad-hoc `[DEBUG]` INFO lines, hop-boundary lines from [AST-527](https://linear.app/astralcareermatch/issue/AST-527)/[AST-530](https://linear.app/astralcareermatch/issue/AST-530), truncated batch summaries, and sparse warnings without the surrounding discovery context. This epic standardizes **step-by-step, human-readable debug logging** on **backend** paths, documents the contract in **ASTRAL_CODE_RULES**, renames **Anthropic Ad Hoc** to **Agent Ad Hoc** in navigation, and makes **insufficient debug instrumentation a Radia fix-now** on review — without Betty asserting log text in tests.

## Functional scope

* **Code Rules contract:** Add a precise, mandatory section to `docs/ASTRAL_CODE_RULES.md` (§1.5 or adjacent) for **backend** functions in debuggable runs: emit only when `debug=True` is passed through the call chain (including runs started from **Agent Ad Hoc** — backend only; **no** debug-logging requirement on React/UI). Use `src/utils/logging.py` (extend `get_logger` / `logger.test()` and/or a small helper). Document the **two line kinds** below and the **long-content truncation** rule.
* **When debug is on, log what happened — not only counts:** For each meaningful step, log **inputs discovered and outputs recorded** (e.g. search term + Google result URLs/snippets summary, vet pass/fail + what was written to roster, ingest slug + ownership outcome). Aggregate `summary={...}` at batch end remains, but must not replace per-step/per-index detail.
* **Per-index lines (visually distinct):** Each item in a batch loop gets a **header line** using universal `index N/M` (not domain-specific “term” in the format). Style: **D** — module/function context, `index N/M`, primary identifier, arrow outcome. Header lines must be easy to scan (distinct from detail lines).
* **Working-log detail lines:** All substantive debug detail (search hits, recorded fields, branch reasons, payload excerpts) uses prefix ` | ` (two spaces, pipe, two spaces) so working log content is visually grouped under its index header.
* **Long text truncation:** When logging string/blob content longer than **50 lines**, emit **first 15 lines**, then a single line `<{n} lines omitted>` (exact count), then **last 15 lines**. Shorter content logs in full.
* **Unified debug emission:** Retire hand-rolled `logger.info("[DEBUG] …")` **when a file is otherwise touched** for this epic; grandfather untouched files until then.
* **Debug flag propagation:** Any backend path that accepts `debug=` passes it through; align with [AST-530](https://linear.app/astralcareermatch/issue/AST-530) `run_next` passthrough.
* **Agent Ad Hoc navigation:** Rename sidebar **Anthropic Ad Hoc** → **Agent Ad Hoc** in `NAV_CONFIG` (route path may stay `/admin/anthropic_ad_hoc` unless Susan wants a URL change).
* **Review enforcement:** Update `review-astral` — missing/inadequate debug instrumentation on touched `debug=` surfaces is **fix-now**. Betty does **not** add manifest tests for log strings.
* **Dispatch structure:** Parent delivers rules + helper + review rubric + nav rename + representative backfill entry points. **One child ticket per backfill component** (dispatcher, agent, roster, consult, gazer, builder, external LLM wrappers, etc.).

## Boundaries

* **No** debug-logging requirements on UI/React components — backend only.
* Does **not** change default production log volume when `debug=False`.
* Does **not** add Betty / Test Bible log-string assertions.
* Does **not** redo [AST-527](https://linear.app/astralcareermatch/issue/AST-527)/[AST-530](https://linear.app/astralcareermatch/issue/AST-530) hop semantics.
* Does **not** change Execution History UI or `app_log` schema.
* Data layer remains **no log** per §1.5.
* Does **not** log full prompts/responses without the 50-line / 15+omit+15 truncation rule.

## Acceptance criteria

1. `docs/ASTRAL_CODE_RULES.md` documents: debug trigger, helper, index header format, ` | ` detail lines, long-content truncation, and anti-patterns.
2. Debug `inflow_discovery` / `vet_inflow_discovery` run: for each **index N/M**, logs show **search/discovery results** and **what was recorded** (not only pass/fail), then batch summary.
3. A payload or scrape dump **>50 lines** in debug shows first 15 / `<n lines omitted>` / last 15 only.
4. No new debug-only lines when `debug=False` (spot-check dispatcher + one roster path).
5. Sidebar shows **Agent Ad Hoc**.
6. `review-astral` documents insufficient debug logging as **fix-now**.
7. Component tests stay green; new tests cover helper **gating** and truncation helper behavior, not log string content.

## Dependencies and blockers

* [AST-527](https://linear.app/astralcareermatch/issue/AST-527) / [AST-530](https://linear.app/astralcareermatch/issue/AST-530) — **Done**.
* [AST-388](https://linear.app/astralcareermatch/issue/AST-388) — **Done**.
* None blocking definition approval.

## Open questions

none.

## Decisions

* **Backfill:** one sub-issue per backfill component (Susan 2026-06-02).
* **Agent Ad Hoc / UI:** backend functions only; UI components do not need debug logging (Susan 2026-06-02).
* **Mechanism migration:** grandfather existing `logger.info("[DEBUG] …")` until the file is otherwise touched (Susan 2026-06-02).
* **Per-index format:** **Style D** with `index N/M` on visually distinct header lines; working detail prefixed with ` | ` (Susan 2026-06-02).
* **Debug depth:** when debug is on, log **results found** (e.g. Google CSE) and **results recorded** — UAT-grade traceability, not itemized pass/fail alone (Susan 2026-06-02).
* **Long content:** >50 lines → first 15, `<n lines omitted>`, last 15 (Susan 2026-06-02).

---

## Original brief

When I am running a task with "debug" mode on, I really want to see each step of the process in the log.  I don't care if it's verbose, it will not be set for runtime, but we do a lot of new prompts and such, and debugging is very important.

I need for the Code Rules document to reflect exactly how to handle debug logging for every function, to use header content thoughtfully to make it human-readable (e.g. include the function name issuing the log) and for that to only appear when the debug flag is set to true, or run from Anthropic Ad Hoc (Which should also be renamed to "Agent Ad Hoc" in the navigation).

I want Radia to consider insufficient debug logging in submitted code to be a FIX NOW.

I do NOT need Betty to test for log output, let's make this Radia's concern.

Here is an example of 95 search terms run in debug mode, with 3 failures:

\[2026-06-02 16:53:02\] INFO dispatch.scheduler: Dispatching inflow_discovery — 1 available, batch inflow_discovery-e2f1247c-a9c0-4fd3-b06b-f7120c1711cc

\[2026-06-02 16:53:02\] INFO src.core.dispatcher: \[DEBUG\] \_run_task: running 'inflow_discovery' batch_size=1 batch_id=inflow_discovery-e2f1247c-a9c0-4fd3-b06b-f7120c1711cc...

\[2026-06-02 16:53:02\] INFO src.core.dispatcher: \[DEBUG\] \_run_unified\[candidate/LIVE_PROMPTS\]: claimed 1 entities (batch=inflow_discovery-e2f1247c-a9c0-4fd3-b06b-f7120c1711cc) batch_call_mode=False dispatch batch_size=1

\[2026-06-02 16:53:02\] INFO src.core.agent: run_next chain entry: task=vet_inflow_discovery batch_id=inflow_discovery-e2f1247c-a9c0-4fd3-b06b-f7120c1711cc

\[2026-06-02 16:53:02\] INFO src.external.deepseek: LLM deepseek task=vet_inflow_discovery 74.1s stop=end_turn tokens in=15345 out=11507

\[2026-06-02 16:53:02\] INFO src.core.agent: do_task(vet_inflow_discovery) completed successfully batch_id=inflow_discovery-e2f1247c-a9c0-4fd3-b06b-f7120c1711cc index=somerset

\[2026-06-02 16:53:02\] WARNING src.core.roster: ingest_new_companies: slug 'conduktor' owned by another candidate

\[2026-06-02 16:53:02\] WARNING src.core.roster: ingest_new_companies: slug 'aidoc' owned by another candidate

\[2026-06-02 16:53:02\] INFO src.core.dispatcher: \[DEBUG\] \_run_task: runner returned summary={'total_processed': 1, 'total_passed': 92, 'total_failed': 3, 'total_errors': 0}

### Comments

#### chuckles — 2026-06-05T18:09:09.615Z
@susan — **finish-up blocked** (retry): `git.sh push-dev AST-538` merge failed again. Conflicts:

- `docs/ASTRAL_TEST_BIBLE.md`
- `docs/features/foundation/ast-554-debug-logging-contract-and-shared-helper.md` (add/add)
- `docs/features/foundation/ast-555-agent-ad-hoc-navigation-rename-improve-quality-of-debug-logging.md`

`origin/ftr/ast-538-improve-quality-of-debug-logging` @ `11b515e5` still exists. Resolve on `dev` (take ftr versions for bible + AST-538 plan docs per prep-uat pattern), commit merge, then re-run **finish-up AST-538**.

— Chuckles

#### chuckles — 2026-06-03T22:58:11.000Z
@susan — **finish-up blocked:** `git.sh push-dev AST-538` merge failed (Joan). Conflicts in:

- `docs/ASTRAL_TEST_BIBLE.md`
- `docs/features/foundation/ast-554-debug-logging-contract-and-shared-helper.md` (add/add)
- `docs/features/foundation/ast-555-agent-ad-hoc-navigation-rename-improve-quality-of-debug-logging.md`

Local `dev` also has unstaged WIP: `src/core/intake.py`, `src/ui/frontend/src/components/IntakeChatModal.tsx` — resolve or stash before re-run push-dev.

— Chuckles

#### chuckles — 2026-06-03T19:12:11.924Z
[check-linear]

Susan — full answer to your **2026-06-03** question (why `anticipate_scan` still looks legacy, what this epic actually shipped, and what to run next).

## Why `anticipate_scan` still shows `[DEBUG]` lines

Your sample is the **expected** console today for that task key. **`anticipate_scan` was never instrumented in AST-538.**

That run path is:

1. **Dispatcher** — `src/core/dispatcher.py` (`_run_unified`, `_run_task`) still uses grandfathered `logger.info("[DEBUG] …")` for **every task except** `inflow_discovery`.
2. **Agent** — `src/core/agent.py` (`do_task`, `run_next`) — still hand-rolled `[DEBUG]` (brain_setting, block counts, etc.).
3. **DeepSeek wrapper** — `src/external/deepseek.py` — still `[DEBUG] send_to_deepseek(…)` plus token lines at INFO.

AST-557 only switched **dispatcher + roster** to the new helper on the **`inflow_discovery`** task key. For `anticipate_scan`, the dispatcher `elif debug:` branches still emit the old strings — same shape you pasted.

**Nothing is wrong with your UAT run** if you were watching `anticipate_scan`; you were watching a path this epic deliberately left for the **backfill parents** in Backlog.

## Git (authoritative — fetch first)

```bash
git fetch origin
```

| Ref | SHA | Notes |
|-----|-----|--------|
| `origin/ftr/ast-538-improve-quality-of-debug-logging` | `11b515e5` | Parent integration branch (all four children rolled up) |
| `origin/dev` | (your baseline) | Does **not** include AST-538 product work until you merge or land ftr |

Recent rollup commits on ftr: `81057fa5` (AST-555), `50716857` (AST-556), `11b515e5` (AST-557). Sub branches `origin/sub/AST-538/*` were deleted after rollup per prep-uat.

**To UAT the epic as built:** run the app from a tree that contains ftr @ `11b515e5` (local `dev` after land-ftr merge, or temporary checkout of that ref). Restart backend after merge.

## What AST-538 + children 554–557 actually shipped

**Parent AST-538** delivered the **contract + plumbing + one representative path**, not full-repo backfill.

| Child | What landed on ftr | Key paths |
|-------|-------------------|-----------|
| **AST-554** | Code Rules **§1.5.1**, shared helpers in `src/utils/logging.py` (`debug_index`, `debug_detail`, `debug_detail_block`, `truncate_debug_content`, `format_debug_index_header`), component tests `tests/component/utils/test_debug_logging.py` | `docs/ASTRAL_CODE_RULES.md`, `src/utils/logging.py` |
| **AST-555** | Sidebar label **Agent Ad Hoc** (route unchanged) | `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, `src/utils/config.py` (`NAV_CONFIG`) |
| **AST-556** | `review-astral` skill: insufficient debug on touched `debug=` surfaces = **fix-now** | `~/.cursor/skills/review-astral/SKILL.md` (docs-only child) |
| **AST-557** | **Representative** inflow instrumentation only — not all roster/dispatcher tasks | `src/core/roster.py` (`run_inflow_discovery_batch`), `src/core/dispatcher.py` (only when `dispatch_task_key == inflow_discovery`) |

**Log shape on ftr (actual implementation):**

- **Index header** (style D, INFO when `debug=True`): `roster.run_inflow_discovery_batch index 12/95 <term> -> <outcome>` (function context + `index N/M` + identifier + ` -> ` outcome). The earlier thread sample used `>> [N/M]` as illustration; shipped headers do **not** include `>>`.
- **Working detail** (INFO when `debug=True`): lines prefixed with **` | `** (two spaces, pipe, two spaces) via `DEBUG_DETAIL_PREFIX` in `src/utils/logging.py`.
- **Long blobs:** `debug_detail_block` + `truncate_debug_content` (first 15 / `<n lines omitted>` / last 15 when >50 lines).

**AST-557 does *not* replace** legacy `[DEBUG]` elsewhere in `roster.py` (e.g. other batch functions) or in `agent.py` / `external/*.py`.

## Backlog parents AST-540–546 (what to dispatch for the rest)

Each is **Backlog**, **blockedBy AST-538** (helper now exists on ftr). None of these need to run for you to **prove** the epic — only to extend the new style to other modules.

| Ticket | Module / scope | Primary files | Covers your `anticipate_scan` pain? |
|--------|----------------|---------------|--------------------------------------|
| **AST-540** | **Dispatcher** — claim, loop drain, skip guards, batch end; retire `[DEBUG]` on touched dispatcher paths | `src/core/dispatcher.py` | **Partially** — dispatch shell around any task, including `anticipate_scan` |
| **AST-541** | **Agent** — `do_task`, `run_next`, token/prompt assembly, chain hops | `src/core/agent.py` | **Yes** — your `do_task('anticipate_scan')` `[DEBUG]` lines |
| **AST-542** | **Roster** — full inflow/vet/ingest/locate backfill (broader than AST-557 slice) | `src/core/roster.py` (+ related) | No (different tasks) |
| **AST-543** | **Consult** — batch grading, rubric paths | `src/core/consult.py` | No |
| **AST-544** | **Gazer** — company gaze / watch | gazer modules | No |
| **AST-545** | **Builder** — artifact HTML generation | builder paths | No |
| **AST-546** | **External LLM wrappers** — DeepSeek, Anthropic timing/detail | `src/external/deepseek.py`, `src/external/anthropic.py` | **Yes** — your `send_to_deepseek('anticipate_scan')` `[DEBUG]` lines |

**For `anticipate_scan` to match the new contract end-to-end**, you need at least **AST-540 + AST-541 + AST-546** implemented and on your running branch (542 is inflow-focused; 557 already did the inflow representative slice).

## What you should run *now* to see the new logging (no new tickets)

1. **Confirm code:** `git rev-parse HEAD` or merged ftr should reach `11b515e5` (or descendant).
2. **Restart** app/backend.
3. **Dispatch `inflow_discovery`** (not `anticipate_scan`) with **debug enabled** on the dispatch task row for a candidate with **stale company search terms**.
4. In console, look for:
   - `roster.run_inflow_discovery_batch index …/…` headers
   - ` | ` detail lines (CSE hits, vet outcomes, ingest recorded / not recorded)
   - Dispatcher lines only for **inflow_discovery**: `dispatcher._run_unified index 1/1 …` (AST-557 scoped claim logging)
5. **pytest spot-check:** `pytest tests/component/utils/test_debug_logging.py -q`

If that path looks good, **AST-538 UAT for the delivered scope is satisfied** even while `anticipate_scan` stays legacy until 540/541/546.

## What you must dispatch/run for `anticipate_scan` + full backfill

1. Move **AST-540**, **AST-541**, **AST-546** (and optionally 542–545) from **Backlog → Todo** when you want Chuckles to dispatch — or say **dispatch AST-540** (etc.) explicitly.
2. After those land and roll up to ftr (or `dev`), run **`anticipate_scan`** again with **debug=True** on the dispatch task.
3. Expect **541** to replace `do_task`/`run_next` `[DEBUG]` blocks; **546** to replace DeepSeek `[DEBUG]` vendor lines with ` | ` detail + truncation; **540** to structure dispatcher claim/summary around the batch.

**AST-542** overlaps AST-557 on inflow — dispatch 542 only if you want *full* roster coverage beyond the 557 representative path.

---

**Bottom line:** Epic success on ftr = contract + helper + Agent Ad Hoc rename + review rubric + **`inflow_discovery` proof path**. `anticipate_scan` is still on grandfathered logging until backlog **540 / 541 / 546** ship.

— Chuckles

#### chuckles — 2026-06-03T19:06:36.484Z
[check-linear] User Testing — verify **inflow_discovery** debug on merged ftr/dev; **anticipate_scan** still legacy until **AST-540–546** (@susan)

#### susan — 2026-06-03T19:04:02.887Z
I can't be sure if this is working or not, since the dispatch logging still looks like this:

\[2026-06-03 14:04:33\] INFO src.external.deepseek: LLM deepseek task=anticipate_scan 131.2s stop=end_turn tokens in=21753 out=5466

\[2026-06-03 14:04:33\] INFO src.external.deepseek: \[DEBUG\] send_to_deepseek('anticipate_scan'): 131.2s | stop_reason=end_turn
\[2026-06-03 14:04:33\] INFO src.external.deepseek: \[DEBUG\]   vendor=deepseek-v4-pro tokens: fresh=21753 cache_read=0 cache_write=0 output=5466

\[2026-06-03 14:01:27\] INFO src.core.agent: run_next chain entry: task=anticipate_scan batch_id=anticipate_scan-5b4c3f8d-e2a2-4d39-abfc-d5223cd3133c

\[2026-06-03 14:01:27\] INFO src.core.agent: \[DEBUG\] do_task('anticipate_scan'): brain_setting=Big provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset

\[2026-06-03 14:01:27\] INFO src.core.agent: \[DEBUG\] do_task('anticipate_scan'): 2 system block(s) + 1 user block(s)

Which other tickets would need to be executed from the backlog that would employ the changes of this ticket?

#### chuckles — 2026-06-03T05:26:31.864Z
## Manual test steps

**Prerequisites:** Local `dev` includes land-ftr merge (commit `7ef2b148`). Restart app/backend if already running. Use a candidate with inflow discovery work queued or runnable.

### AST-554 — contract + helper
1. Open `docs/ASTRAL_CODE_RULES.md` §1.5.1 — confirm debug trigger, `debug_index` / `debug_detail`, truncation rule, anti-patterns.
2. Run `pytest tests/component/utils/test_debug_logging.py -q` — all green.
3. With `debug=False`, run one dispatcher path (e.g. small batch) — confirm no new `[ ~ ]` / `>> [N/M]` lines beyond existing hop logging.

### AST-555 — navigation
4. Open admin UI sidebar — label reads **Agent Ad Hoc** (route may still be `/admin/anthropic_ad_hoc`).

### AST-556 — review rubric
5. Skim `~/.cursor/skills/review-astral/SKILL.md` — insufficient debug on touched `debug=` surfaces is **fix-now** (docs-only; no runtime test).

### AST-557 — inflow representative instrumentation
6. Run **inflow_discovery** (or equivalent) with **debug=True** on a small batch (1–3 terms).
7. For each **index N/M**: confirm header line (module/function, identifier, outcome) and **`  |  `** detail lines showing **search/discovery results** and **what was recorded** (not only pass/fail).
8. Trigger or simulate a payload **>50 lines** in debug — confirm **first 15**, `<n lines omitted>`, **last 15** only.
9. End-of-batch **summary** line still present; per-index detail must not be replaced by summary alone.

**Note:** Full `run_component_tests.sh` on composite `dev` reported 4 failures in `test_agent` resume-artifact tests (likely unrelated to this epic); epic logging tests and 1281 other tests passed.

`origin/ftr/ast-538-improve-quality-of-debug-logging` @ `11b515e5` · local `dev` merged (§8). Sub branches deleted.

**Rollup guidance:** See [check-linear] comment above (who: Chuckles + Joan; bible/sub ordering).

Reset after UAT: `git reset --hard origin/dev` (when ready to drop local UAT merge).

— Chuckles

#### chuckles — 2026-06-03T04:30:18.054Z
[check-linear]

**Who does rollup:** Chuckles runs **`rollup-child`** after each child hits **User Testing**; **Joan** executes the git merge via **`~/.cursor/skills/git-astral/git.sh rollup <child-id>`** (worktree at `origin/ftr/…`, merge `origin/sub/…`, push). Engineers do not merge sibling subs into the parent ftr.

**Joan (AST-538) — how this happened**

1. **AST-555** — Betty published **§7.13zt** on the child sub before **§7.13zs** (AST-554) was on **ftr**. Joan’s merge saw overlapping edits in **`docs/ASTRAL_TEST_BIBLE.md`** (not a fast-forward). Fix: Betty re-based bible on **ftr** (keep **§7.13zs**, append **§7.13zt**); rollup then FF @ `81057fa5`.

2. **AST-557** — Child **sub** was integrated from **dev-hedy** without **ftr** after siblings rolled up, so the sub tip **removed** AST-554/555/556 product and bible sections Joan had already merged to **ftr**. Fix: Hedy rebuilt publish ref = **ftr @ `50716857` + roster/dispatcher + bible §7.13zu only**; rollup FF @ `11b515e5`.

3. **Stale `git-rollup-work` worktrees** (other epics, e.g. AST-562) blocked Joan until Chuckles removed **`/private/tmp/git-rollup-*`** orphans.

4. **prep-uat `land-ftr`** — Separate step: merge **`origin/ftr/ast-538`** into **local `dev`**. Failed because **local `dev` is ~81 commits ahead of `origin/dev`** with overlapping plan/bible files — not a Joan rollup failure; needs your call on how to reconcile **dev** before UAT landing.

**Joan — recommendations (avoid repeat)**

| Practice | Why |
|----------|-----|
| Roll up in **`blockedBy` order** (554 → 555 → 556 → 557) | Parent ftr always has blockers first |
| Before Betty edits bible on a child, **`git merge origin/ftr/<parent>`** on **dev-betty** | Sub bible = ftr sections + one new §7.13z* block only — no cumulative stray §7.13zr/zw from other epics |
| Before engineer **store-code-commit**, merge **ftr** on **dev-&lt;agent&gt;** | Sub must not drop sibling commits already on ftr |
| After each **User Testing**, Chuckles runs **`rollup-child`** immediately | Siblings merge **ftr** for integration, not each other’s stale **sub** |
| **`land-ftr` only when `dev` is merge-clean with `origin/dev`** | Prevents UAT landing conflicts |

**Current git:** All four children **User Testing**; **`origin/ftr/ast-538-improve-quality-of-debug-logging` @ `11b515e5`** has full rollup. **Blocked:** your **`dev` ↔ ftr** merge for prep-uat (see prior comment).

— Chuckles

#### susan — 2026-06-03T04:28:34.200Z
@chuckles please answer the question I posted 2 hours ago.  I know you're stuck, but the team needs to know how to avoid/manage these issues.  That's the whole point of this orchestration.

#### chuckles — 2026-06-03T03:31:02.823Z
@susan — prep-uat blocked: `land-ftr` merge `origin/ftr/ast-538-improve-quality-of-debug-logging` into local `dev` conflicts (bible + plan docs; dev 81 commits ahead of origin/dev). All four children User Testing; ftr @ 11b515e5 has full rollup. Resolve dev↔ftr then re-run prep-uat AST-538.

— Chuckles

#### susan — 2026-06-03T02:44:35.848Z
Who is doing the roll up work?  I want you to directly ask Joan how this happened for this feature and what she recommends to avoid it in the future.  Print her response as a comment here.

#### chuckles — 2026-06-03T00:40:40.819Z
@susan — **rollup-child** blocked merging **AST-555** `sub/*` → `ftr/ast-538` (**`docs/ASTRAL_TEST_BIBLE.md`** conflict). **AST-554** rolled to `ftr` @ `262fec33`. **AST-554**/**AST-555** User Testing; **AST-556**/**AST-557** Plan Ready. Betty bible fix on **AST-555**, then Chuckles resume rollup + validate/build for **556**/**557**.

— Chuckles

#### chuckles — 2026-06-03T00:06:54.638Z
@susan — Orchestration interrupted during Betty qa (stage 7); resume from **AST-555** qa → test → review path, then **AST-556**/**AST-557** after **AST-554** Review Posted. **AST-554** Tests Ready; **AST-555** Code Complete; **AST-556**/**AST-557** Todo.

— Chuckles

#### chuckles — 2026-06-02T22:29:45.031Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-538 (parent) | ftr/ast-538-improve-quality-of-debug-logging |
| AST-554 | sub/AST-538/AST-554-debug-logging-contract-and-helper |
| AST-555 | sub/AST-538/AST-555-agent-ad-hoc-nav-rename |
| AST-556 | sub/AST-538/AST-556-review-astral-debug-fix-now |
| AST-557 | sub/AST-538/AST-557-inflow-discovery-representative-debug |

## Epic sessions (headless — Chuckles injects in every spawn)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `de2831b2-4e47-463f-88eb-f09f0c63a494` | AST-538 (parent) | git |
| Ada | `08cdb463-00e5-41c2-8aea-b29511717924` | AST-554 | engineer |
| Betty | `b9f73e77-11e4-4bd6-a8a6-3dde6b8cfef5` | AST-554 | qa |
| Radia | `af97691b-7a8a-4fe8-b3c2-c67cac140384` | AST-554 | review |
| Katherine | `88ca8f3a-57d3-408d-9b6b-c8db7e727d7c` | AST-555 | engineer |
| Betty | `641e5b69-c033-4450-bf5a-a5a4b6f433d6` | AST-555 | qa |
| Radia | `dba10942-643f-41cd-98bc-dab992eb0888` | AST-555 | review |
| Radia | `a48371a4-da3e-478a-8085-87aa6f59da5e` | AST-556 | engineer |
| Betty | `f89c83aa-b883-4dd3-b8cf-6013de7c6f08` | AST-556 | qa |
| Radia | `3584a127-c512-438e-a586-e63ed1882165` | AST-556 | review |
| Hedy | `d1dff490-97b6-413e-8fd5-544591d93fa4` | AST-557 | engineer |
| Betty | `46d20596-888f-474a-9aff-c35c2afb7d9c` | AST-557 | qa |
| Radia | `2600234a-27ff-4ca0-bad0-c99cb7f9993f` | AST-557 | review |

**blockedBy:** AST-556, AST-557 → AST-554.

**Parent:** AST-538

— Chuckles

#### chuckles — 2026-06-02T19:35:28.703Z
[check-linear]

**Your 2026-06-02 thread — done:**

- **`define-linear` skill** — added **Define debug logging** section (`~/.cursor/skills/define-linear/SKILL.md`): depth (found + recorded), index N/M headers, ` | ` detail lines, 50-line truncation, backend-only, Radia fix-now, split backfill into separate Backlog parents.
- **Description** — updated **Functional scope** / **Decisions** with define-linear cross-ref and backfill parent list.
- **Backlog parent tickets** (each **blockedBy AST-538**): **AST-540** dispatcher · **AST-541** agent · **AST-542** roster · **AST-543** consult · **AST-544** gazer · **AST-545** builder · **AST-546** external LLM wrappers.

Open questions: none. Move **AST-538** to **Todo** (assign Chuckles) when you want dispatch on the core epic.

— Chuckles

#### susan — 2026-06-02T19:03:10.647Z
This looks good.  I want you to include "define debug logging" where appropriate as part of your /define-linear skill file so that I can see how you would want to create log content and the agents don't just guess.

Otherwise, I think we're ready to go!  Please update the description to incorporate that, and also, let us create SEPARATE parent issues for debug refactor of existing high-traffic components, and keep them in the backlog.

#### chuckles — 2026-06-02T18:57:59.632Z
@susan — **AST-538** definition updated (Backlog): your clarifications are in **Decisions** — deep debug (found + recorded), **index N/M** headers (style D), **`  |  `** working lines, **50-line** truncation rule. **Open questions:** none.

**Confirmed sample log shape** (debug on, `vet_inflow_discovery` batch; `[ ~ ]` = `logger.test()` prefix from `logging.py`):

```
[ ~ ] dispatcher._run_task: inflow_discovery batch_id=inflow_discovery-e2f1247c… batch_size=1
[ ~ ] dispatcher._run_unified: claimed entities=1 batch_call_mode=False

>> [12/95] roster.vet_inflow_discovery | slug=acme-corp
  |  google_cse: query="acme corp careers" hits=6 top_urls=[https://…, https://…]
  |  vet: pass → recorded candidate_slug=acme-corp company_id=…

>> [13/95] roster.vet_inflow_discovery | slug=conduktor
  |  google_cse: query="conduktor jobs" hits=4 top_urls=[…]
  |  vet: fail → not recorded (slug owned by another candidate)

>> [14/95] roster.vet_inflow_discovery | slug=aidoc
  |  google_cse: …
  |  vet: fail → not recorded (slug owned by another candidate)

[ ~ ] agent.do_task: vet_inflow_discovery completed batch_id=… index=somerset
[ ~ ] external.deepseek: task=vet_inflow_discovery 74.1s tokens in=15345 out=11507
  |  llm_response (87 lines):
  |  <line 1>
  |  …
  |  <line 15>
  |  <57 lines omitted>
  |  <line 73>
  |  …
  |  <line 87>

[ ~ ] dispatcher._run_task: summary total_processed=1 total_passed=92 total_failed=3 total_errors=0
```

**Notes:** `>> [N/M]` header lines are the visually distinct index rows; everything underneath for that index uses **`  |  `**. Exact `>>` prefix is implementer choice as long as headers scan separately from detail lines. Helper should centralize truncation so roster/agent/dispatcher stay consistent.

If this matches what you want, move **AST-538** to **Todo** (assign Chuckles) for dispatch.

— Chuckles

#### susan — 2026-06-02T18:41:34.017Z
I see.  I was confused by your use of the word "term".  The issue is not only the itemized log, but that when I want a Debug log, I REALLY MEAN IT.  Log the results of what was found for the search term from the google search, log the results of what was recorded.  These are data that we cannot yet reproduce in unit testing, so we need to see it when I'm user testing.  for long inputs outputs, I want the first 15 lines, then a <n lines between> and then the last 15 lines of the content, if the content is more than 50 lines long.

I think using "index 12/95" is fine, and more universal.  I like style D for this, but please add an additional "  |  " string to prefix the "working log" content, and let the "index" lines be more visually distinct.

Can you confirm what the logs will look like with this clarification, please?

#### chuckles — 2026-06-02T18:34:13.303Z
[check-linear]

**AST-538** — Incorporated your inline answers on the description (backfill = one child per component; backend-only debug; grandfather `[DEBUG]` INFO until touch). One item left: **per-item log line shape** for batch loops.

**What “per-item line shape” means:** For each search term / slug / job in a batch, we emit one debug line *before* the final `summary={...}` — so you can see *which* 3 of 95 failed, not only `total_failed=3`.

Pick **A**, **B**, **C**, or **D** (or say “B + progress” etc.):

**A — Minimal (index + id + outcome)**
```
[ ~ ] vet_inflow_discovery: term i=12 slug=acme-corp outcome=pass
[ ~ ] vet_inflow_discovery: term i=13 slug=beta-io outcome=fail reason=vet_reject
```

**B — With batch progress (N of M)**
```
[ ~ ] vet_inflow_discovery: [12/95] slug=acme-corp outcome=pass
[ ~ ] vet_inflow_discovery: [13/95] slug=beta-io outcome=fail reason=vet_reject
```

**C — Step header + key=value (matches proposed Code Rules style)**
```
[ ~ ] ingest_new_companies: process_term term=12/95 slug=acme-corp outcome=pass
[ ~ ] ingest_new_companies: process_term term=13/95 slug=beta-io outcome=fail reason=slug_owned_by_other_candidate
```

**D — Function prefix in message (like today's `[DEBUG] _run_task:` but gated)**
```
[ ~ ] roster.ingest_new_companies: term 12/95 acme-corp → pass
[ ~ ] roster.ingest_new_companies: term 13/95 beta-io → fail (owned by another candidate)
```

After you pick, I'll fold it into the definition and you can move **AST-538** to **Todo** for dispatch.

— Chuckles

#### chuckles — 2026-06-02T17:26:02.210Z
@susan — **AST-538** definition is on the ticket (Backlog). Four open questions need your call before dispatch:

1. **Backfill breadth** — one epic for all `debug=` modules vs rules/helper/review first, backfill in children?
2. **Agent Ad Hoc** — always verbose on that page, or only when `debug=True` is passed today?
3. **Mechanism** — migrate off `logger.info("[DEBUG] …")` in the same delivery, or grandfather until files are touched?
4. **Per-item lines** — `(index, id/slug, status)` enough, or require explicit `term N/M` (or similar) on every batch loop line?

Move to **Todo** when you're happy with the definition (or comment edits).

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
