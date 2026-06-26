# AST-527 — Daisy-chain hop debug logging

<!-- linear-archive: AST-527 archived 2026-06-15 -->

## Linear archive (AST-527)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-313; related: AST-528

### Description

## Purpose

Susan is exercising the Phase E artifact daisy chain via manual dispatch while prompt authoring continues under [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring). During multi-hop `run_next` runs, the console shows generic token warnings (`Token {$CALLER_SYSTEM} resolved to empty`) with no hop-boundary context — parent task, child task, which caller keys were supplied, or whether the hop is chain entry vs mid-chain. She cannot diagnose chains without reading database rows. This ticket adds structured daisy-chain observability only; caller-token propagation correctness is [AST-529](https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops).

## Functional scope

* **Chain-hop debug visibility:** When `do_task` executes a `run_next` hop, emit structured debug output at the hop boundary: parent `task_key`, child `task_key`, `batch_id`, and for each caller chain key (`CALLER_SYSTEM`, `CALLER_CACHE_A`–`D`, `CALLER_RESPONSE`) whether it is populated and its character length (not full prompt text).
* **Chain-entry vs mid-chain:** Distinguish chain entry (first hop in a run, no incoming caller context) from mid-chain hops where caller keys may be expected. Empty caller tokens at chain entry must not use the same warning shape as unexpected mid-chain empties.
* **Empty-token diagnostics:** When a chain-source token resolves empty, the log line must identify the immediate parent `task_key` (when applicable) and which caller keys the parent supplied — not only the callee `task_key`.
* **Manual-run parity:** Manual dispatch runs from Scheduled Actions (admin **Run**) must surface the same chain-hop debug detail as other debug-enabled batch paths.

## Boundaries

* Does **not** fix caller-token propagation logic — that is [AST-529](https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops).
* Does not author or change Manage Tasks prompt text, agent assignment, or `run_next` wiring ([AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)).
* Does not add dispatch seed rows or change `BUILD_ARTIFACTS` entry task.
* Does not implement new chain tokens or change `TOKEN_SOURCES` registry semantics.
* Does not change LLM provider behavior, grading, or artifact persistence.
* Per **ASTRAL_CODE_RULES** §1.5, logging stays in utils/core (`do_task`, `resolve_tokens`); data layer does not log.
* Must not break existing daisy-chain behavior for consult, roster, or non-artifact paths ([AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task), **AST-455**, **AST-469**).

## Acceptance criteria

1. Every `run_next` transition logs parent `task_key` → child `task_key`, `batch_id`, and populated/empty status plus character length for each `CALLER_*` key passed to the child.
2. The first hop in a dispatch run logs that it is chain entry; empty caller tokens on that hop do not emit mid-chain "unexpected empty" warnings.
3. When a `{$CALLER_*}` token resolves empty on a mid-chain hop, the warning includes parent `task_key` and a summary of which caller keys the parent supplied (populated vs empty).
4. Triggering **Run** on a Scheduled Actions row for a multi-hop artifact task produces hop-boundary debug lines in the server console for the full chain through terminal hop.
5. Existing component tests for daisy-chain merge ([AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task), **AST-370**, **AST-455**) remain green; new or extended tests cover chain-entry vs mid-chain log distinction.

## Dependencies and blockers

* [AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task) (daisy-chain `run_next`) — Done.
* **AST-455** (`CALLER_*` token model) — Done.
* [AST-529](https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops) (caller propagation fix) — related sibling; can land before or after this ticket.
* [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) (prompt authoring) — In Progress; legitimately empty resolved segments must remain distinguishable in logs.

## Open questions

1. Should enhanced chain debug logging be gated behind the existing per-run `debug` flag only, or always emit at INFO for every production `run_next` hop?
   1. if debug is set for one, it is set for all hops.  
2. When the parent hop's resolved system content is genuinely empty (blank agent / blank system tab), should mid-chain empty `{$CALLER_SYSTEM}` remain a warning, or downgrade to debug once hop-boundary logs expose the cause?
   1. There will never be a case when the caller's token is expected to be blank.  Do not execute the call with an empty token.

---

## Original brief

Split from combined [AST-527](https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging) report (2026-05-29): console log from manual `anticipate_scan` dispatch showing sparse hop detail and generic `Token {$CALLER_SYSTEM} resolved to empty (chain_context, task=contemplate_job)` warnings. Full log preserved on [AST-529](https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops).

### Comments

#### chuckles — 2026-05-29T23:47:37.520Z
## Manual test steps

**Prerequisites:** Local `dev` @ `d9eb3784` (AST-530 merged). Restart Flask if already running. Job in `BUILD_ARTIFACTS` with candidate key configured; Phase E chain wired in Admin → Manage Tasks (`anticipate_scan` → `contemplate_job` or your test chain).

1. **Chain-entry log (AC #2):** Admin → Scheduled Actions → **Run** on the entry hop task with **debug** enabled. In server console, confirm `run_next chain entry: task=<entry_key> batch_id=...` on the first hop. Empty `CALLER_*` on that hop must **not** emit mid-chain "unexpected empty" warnings.
2. **Hop-boundary INFO (AC #1):** On each `run_next`, confirm a line like `run_next hop: parent=<parent_task_key> child=<child_task_key> batch_id=... caller=CALLER_SYSTEM=populated(len=N),...` listing each `CALLER_*` key as populated or empty with length.
3. **Mid-chain empty warning (AC #3):** Force or reproduce a mid-chain hop where a referenced `{$CALLER_*}` is empty (e.g. blank parent system tab). Warning must include `parent=<parent_task_key>` and `parent_caller=` summary — not the generic `(chain_context, task=...)` only.
4. **Fail-fast guard (open Q #2):** Same empty mid-chain case — task must return failure **without** an LLM API call (no anthropic/deepseek request logged for that hop).
5. **Debug propagation (open Q #1):** Entry hop with debug on → confirm recursive hops inherit debug (child hop logs visible at same verbosity).
6. **Regression (AC #5):** Optional quick check — `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst530ChainHopResolveTokens tests/component/core/test_agent.py::TestDoTask::test_chain_entry_log tests/component/core/test_agent.py::TestDoTask::test_hop_boundary_log_on_run_next tests/component/core/test_agent.py::TestDoTask::test_mid_chain_empty_caller_skips_api`

**Out of scope this epic:** caller token propagation fix (**AST-529**), Execution History per-hop rows (**AST-528**).

`origin/ftr/AST-527-daisy-chain-hop-debug-logging` @ `a31703d2` · local `dev` merged (§8) @ `d9eb3784`. Restart app if running.

Deleted: `sub/AST-527/AST-530-chain-hop-debug-logging`

— Chuckles

#### hedy — 2026-05-29T23:36:21.969Z
[check-linear]

**Session scope:** Parent **AST-527** / **Astral Artifacts** — assigned issue ids **(none)**.

**§0a (`astral-hedy` / `dev-hedy`):** `git fetch origin`, `checkout dev-hedy`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD** (`c7327332`).

**§0b:** `@hedy` issue search (Team Astral + **Astral Artifacts** project); **14d** team fallback — hits are mostly historical `hedy/…` branch names, not comment `@hedy` mentions. Full threads on **AST-527**, child **AST-530**, siblings **AST-528** / **AST-529**, and related **AST-513**.

**§1:** Session assigned ids empty. Hedy-assignee in **Astral Artifacts** (**AST-294**, **AST-310**) are **Done** — no new thread activity.

**§2:** **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after prior agent `[check-linear]` posts. **AST-530** thread moved on since last pass (Betty cleared `[qa-handoff]` test harness; **Tests Passed**, assignee **Ada**) — not Hedy inbox work.

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` (happy path). Child **AST-530** @ `origin/sub/AST-527/AST-530-chain-hop-debug-logging` — next gate **Radia `review-astral`**, not engineer queue here.

#### katherine — 2026-05-29T23:36:14.214Z
[check-linear]

**Session scope:** Parent **AST-527** / **Astral Artifacts** — assigned issue ids **(none)**; publish ref `origin/sub/AST-527/AST-530-chain-hop-debug-logging`.

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of **HEAD**). Merged publish ref — **HEAD** `721750a4` (includes Betty test harness + Ada envelope fixes on sub tip).

**§0b:** `@katherine` issue search (Team Astral + **Astral Artifacts** project); team-wide `@katherine` paginated. Full threads on **AST-527**, child **AST-530**, and mention hits in project (**AST-513**, **AST-516**, **AST-308**, etc.). **0** actionable `@katherine` or directed-at-Katherine comments after Katherine `[check-linear]` @ `2026-05-29T23:19` on this parent.

**§1:** Orchestrator assigned ids **(none)**; no assignee-me add-on in session scope.

**Child AST-530:** **Tests Passed** (Ada). Katherine `[qa-handoff]` @ `23:29` cleared by Betty `[check-linear]` @ `23:35` (manifest green @ `783ba141`). No Katherine pipeline action.

**Out of session (not acted):** **AST-526** Chuckles prep-uat blocker (`9923b030`) — **Astral Roster** / `origin/sub/AST-523/AST-526-…`, not **AST-527** subtree.

**Pipeline:** Inbox quiet for **AST-527** / **Astral Artifacts** scope; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass (happy path).

#### katherine — 2026-05-29T23:19:12.391Z
[check-linear]

**Session scope:** Parent **AST-527** / **Astral Artifacts** — assigned issue ids **(none)**; publish ref `origin/sub/AST-527/AST-530-chain-hop-debug-logging` (not merged — blocked below).

**§0a blocked — `dev-kath` merge with `origin/dev`:**
- `docs/ASTRAL_TEST_BIBLE.md` (content)
- `src/core/candidate.py` (content)
- `src/ui/api/api_candidate.py` (content)
- `src/utils/config.py` (content)
- `tests/component/core/test_candidate.py` (content)
- `tests/component/ui/api/test_api_candidate.py` (content)
- `tests/component/utils/test_config.py` (content)

Merge aborted; `dev-kath` @ `e0daa84d` (`BEHIND=113`, `merge-clean: NO`). Did not merge publish ref. Need Susan/Chuckles direction before resolving integration conflicts — not attempting resolution from this inbox pass.

**§0b:** `@katherine` issue search (Team Astral + **Astral Artifacts** project); team-wide `@katherine` paginated; **14d** fallback on session project. Full threads on **AST-527**, child **AST-530**, and mention hits (**AST-513**, **AST-516**, **AST-522**, **AST-526**, **AST-308**). **0** actionable `@katherine` comments in session scope after prior Katherine `[check-linear]` posts.

**Out of session assigned ids (not acted here):** **AST-526** Chuckles prep-uat thread (`9923b030`) directed at Katherine — RESUME_STRUCTURE test import cleanup on `origin/sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table`.

**Pipeline:** Inbox quiet for **AST-527** subtree; **AST-530** **Plan Approved**, assignee **Ada** — no Katherine pipeline action from this pass.

#### hedy — 2026-05-29T23:19:02.988Z
[check-linear]

**Session scope:** Parent **AST-527** / **Astral Artifacts** — assigned issue ids **(none)** for Hedy.

**§0a (`astral-hedy` / `dev-hedy`):** `git fetch origin`, `checkout dev-hedy`, `merge origin/dev` (already up to date), `merge origin/sub/AST-527/AST-530-chain-hop-debug-logging` — merge-clean (**BEHIND=0**, `origin/dev` ancestor of **HEAD**). **HEAD** `deb90ab1` (plan doc from AST-530 publish ref).

**§0b:** `@hedy` issue search (Team Astral + **Astral Artifacts** project); **14d** team fallback — union is mostly historical branch-name hits, not comment `@hedy` mentions. Full threads on **AST-527**, child **AST-530**, sibling **AST-529** / **AST-528**, and parent-context tickets (**AST-313**, **AST-513**).

**§1:** Session assigned ids empty — no assignee-me add-on in scope. (MCP `assignee=me` query errored; manual review of Astral Artifacts Hedy-assignee tickets **AST-294** / **AST-310** are **Done**.)

**§2:** **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after prior agent `[check-linear]` posts.

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` (happy path).

#### chuckles — 2026-05-29T23:11:54.640Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-527 (parent) | ftr/ast-527 |
| AST-530 | sub/AST-527/AST-530-chain-hop-debug-logging |

— Chuckles

#### chuckles — 2026-05-29T23:00:43.945Z
@Susan Somerset — **do-all-the-things** for **AST-527** did not start:

1. **Status** is **Backlog** (need **Todo** as dispatch approval signal).
2. **Assignee** is you (need **Chuckles** for dispatch).
3. **Open questions** still open in the definition (debug-flag gating; warning vs debug for legitimately empty `{$CALLER_SYSTEM}`).

After you answer those two questions (update Description or comment), move to **Todo** and assign **Chuckles** — then re-run **do-all-the-things AST-527**.

— Chuckles

#### chuckles — 2026-05-29T22:53:30.865Z
Split **AST-527** into two tickets (2026-05-29):

- **[AST-527](https://linear.app/astralcareermatch/issue/AST-527)** — daisy-chain hop **debug logging** only
- **[AST-529](https://linear.app/astralcareermatch/issue/AST-529)** — **CALLER_SYSTEM** / caller-token **propagation** fix

Open questions remain on each ticket. Prior open-questions comment on the combined scope is superseded.

— Chuckles

#### chuckles — 2026-05-29T22:46:25.998Z
@Susan Somerset — open questions on **AST-527** definition:

1. Your repro dispatches `anticipate_scan` directly; the log shows `contemplate_job` → `advise_job_resume` downstream, which differs from the documented order `contemplate_job` → `anticipate_scan` → `advise_job_resume`. Is the bug on that ad-hoc wiring, on the intended chain after **AST-313** wiring, or both?

2. Should enhanced chain debug logging be gated behind the existing per-run `debug` flag only, or always emit at INFO for every production `run_next` hop?

3. When the parent hop's resolved system content is genuinely empty (blank agent / blank system tab), should mid-chain empty `{$CALLER_SYSTEM}` stay a warning, or downgrade to debug once hop-boundary logs expose the cause?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
