# AST-847 — Unify BUILD_ARTIFACTS chain in do_task (per-hop state + terminal graduation)

<!-- linear-archive: AST-847 archived 2026-07-29 -->

## Linear archive (AST-847)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-847/unify-build-artifacts-chain-in-do-task-per-hop-state-terminal  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

UAT on [AST-803](https://linear.app/astralcareermatch/issue/AST-803), [AST-832](https://linear.app/astralcareermatch/issue/AST-832), and [AST-844](https://linear.app/astralcareermatch/issue/AST-844) shows jobs can complete every hop in a `run_next` daisy chain and still never reach the successor state Susan expects (e.g. **Ready** / `CANDIDATE_REVIEW` after artifact build). The [AST-803](https://linear.app/astralcareermatch/issue/AST-803/build-artifacts-chain-dispatch-and-state-flattening-build-artifacts) split — flat holding state plus a consult-only chain wrapper that graduates after the outer call returns — is the wrong architecture.

Susan's product model is a **generic, database-driven dispatch-chain pattern**. Hop order and linkage come from `dispatch_tasks` and `agent_task.run_next` in the DB — not from enumerating compound states in `JOB_STATES`. When dispatch claims a job at a **trigger state** and the claimed hop has a non-empty `run_next` graph, `do_task` owns the full synchronous chain as self-referencing recursion. `BUILD_ARTIFACTS` → `CANDIDATE_REVIEW` is the canonical UAT instance; implementation must not hardcode that state name in core chain logic.

This ticket supersedes [AST-788](https://linear.app/astralcareermatch/issue/AST-788/build-artifacts-substates-do-not-graduate) and rolls in [AST-803](https://linear.app/astralcareermatch/issue/AST-803), [AST-832](https://linear.app/astralcareermatch/issue/AST-832), and [AST-844](https://linear.app/astralcareermatch/issue/AST-844).

## Functional scope

* `do_task` **owns the chain:** Dispatch invokes `do_task` for the claimed hop at the job's current state. If that hop's agent row has non-empty `run_next`, `do_task` executes the hop, advances the job record, and recurses into the next hop — same entry point, no consult-only chain orchestrator. Example: `do_task("anticipate_scan")` at `BUILD_ARTIFACTS` succeeds → job state becomes `BUILD_ARTIFACTS.anticipate_scan` → `do_task("consider_job")` at that state → repeat until the last executed hop has empty `run_next`.
* **DB hop labels on the job record:** After each successful hop, write `<trigger_state>.<completed_task_key>` to `job.state` in the database (e.g. `BUILD_ARTIFACTS.anticipate_scan`). These are **runtime labels on the job row** — not pre-registered compound keys in `JOB_STATES` or config. Mid-chain failure leaves the job on the last successful label so redispatch can resume from that hop via `run_next` and caller hydration.
* **Terminal graduation:** When the executed hop's `run_next` is empty, transition the job from its current compound label to the **next job state** already defined in the config-driven state machine (UAT: `BUILD_ARTIFACTS.*` → `CANDIDATE_REVIEW`). Graduation happens in the same `do_task` invocation as the terminal hop. **No domain persist gates** and no business logic in the chain runner beyond state writes and task execution.
* **Mid-chain resume:** A job at `<trigger_state>.<hop>` can be claimed by dispatch on the hop whose `run_next` continues the chain (or chain-entry row per dispatch-key honesty rules). Upstream `{$CALLER_*}` tokens hydrate from persisted `agent_data` ([AST-769](https://linear.app/astralcareermatch/issue/AST-769) — Done) — no LLM re-run for completed hops.
* **Single-hop dispatch rows:** When a dispatch row's `run_next` is intentionally empty, `do_task` runs exactly that hop, writes the matching `<trigger>.<hop>` label, and does **not** graduate to the chain's successor state.
* **Failure behavior:** Retryable hop failure leaves the job on the last successful DB hop label (or bare `trigger_state` if no hop completed) and releases the dispatch claim. Hard failures transition to the hop's configured `TASK_CONFIG` `error_state` without false promotion to the success state.
* **Unified chain:** All hops reachable via `run_next` at the same `trigger_state` — including `draft_cover_letter` when wired in the graph — run inside the same `do_task` recursion. Retire consult exclusions that route cover-letter hops through a separate batch wrapper.
* **Retire AST-803 split:** Remove consult-layer chain wrappers (`do_chain_for_job` pattern), flat-only holding during hops, persist-gate graduation, and graduation logic that runs only after the outer task call returns.
* **Observability:** When `debug=True`, each chain hop logs index header (N/M), hop task key, job id, outcome, and state before/after write ([AST-538](https://linear.app/astralcareermatch/issue/AST-538) Style D). Terminal graduation logs an info-level line visible without debug.

## Boundaries

* **Database-driven, not registry-driven:** Chain topology from `dispatch_tasks` + `agent_task.run_next`. Hop progress from `job.state` DB writes (`<trigger>.<hop>`). Do **not** add compound hop keys to `JOB_STATES`. Do **not** hardcode `BUILD_ARTIFACTS` branches in core chain logic — it remains a valid config state name only.
* **Agent layer, not consult:** Chain recursion, per-hop state writes, and terminal graduation live in `do_task`. Consult and dispatcher claim batches and invoke `do_task` only.
* **Supersedes** [AST-788](https://linear.app/astralcareermatch/issue/AST-788) architecture. Do not patch the old split further.
* **No prompt / graph edits:** Hop prompts and Susan's `run_next` wiring in Manage Tasks stay as-is — execution and state wiring only.
* **Caller hydration (dependency, not build):** Mid-chain caller retrieval from `agent_data` is shipped ([AST-769](https://linear.app/astralcareermatch/issue/AST-769)). Must not regress. Post-run harvest of artifact bodies into `job_data` remains out of scope (deferred in [AST-803](https://linear.app/astralcareermatch/issue/AST-803)).
* **Generate Artifacts / Cancel** on Recommended Jobs: behavior unchanged except DB hop labels align with the per-hop model.
* Must not break non-chain consult dispatch, per-hop execution history rows, or caller-token propagation across hops.
* **Code Rules note:** `ASTRAL_CODE_RULES` §2.6 should document the daisy-chain carve-out — within one `do_task` invocation, jobs **do** auto-advance through `run_next` hops via DB state writes until terminal machine graduation.

## Acceptance criteria

1. **Canonical UAT chain** — Scheduled Actions **Run** on `anticipate_scan` @ `BUILD_ARTIFACTS` with full `run_next` graph: all hops execute in order; job graduates to `CANDIDATE_REVIEW`; job appears **Ready** in Recommended Jobs UI.
2. After each successful hop, `job.state` reflects the completed hop (`<trigger_state>.<task_key>`); Susan can see progress without reading execution history.
3. Mid-chain resume: job on `<trigger>.<hop>` completes remaining hops using `agent_data` caller hydration and graduates without manual state repair.
4. Single-hop run (`anticipate_scan` with `run_next` cleared): exactly one LLM hop runs; job advances to matching DB hop label; does **not** reach `CANDIDATE_REVIEW`.
5. Retryable hop failure: job stays on last successful DB hop label; redispatch can resume. Hard failure: hop `error_state`; no false **Ready**.
6. Terminal hop dispatch row (e.g. `propose_application_responses`) succeeds and graduates in the same run — no silent skip / zero-work batch.
7. Consult-layer chain wrapper, persist-gate graduation, and AST-803-only paths removed; no state-name-specific chain branches replace them.
8. Component coverage: full chain from chain-entry dispatch, per-hop DB state writes, mid-chain resume with caller hydration, single-hop dispatch, retry hold, error state, terminal graduation, non-job-chain `run_next` regression.

## Dependencies and blockers

* [AST-788](https://linear.app/astralcareermatch/issue/AST-788) — superseded by this ticket; cancel parent and shipped children when Susan approves dispatch.
* Per-hop execution history ([AST-531](https://linear.app/astralcareermatch/issue/AST-531)) and dispatch-key honesty ([AST-534](https://linear.app/astralcareermatch/issue/AST-534)) — Done; must remain green.
* Mid-chain caller hydration ([AST-769](https://linear.app/astralcareermatch/issue/AST-769)) — Done; must remain green.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-847 (parent) | ftr/AST-847-unify-build-artifacts-chain-do-task |
| AST-848 | sub/AST-847/AST-848-do-task-run-next-chain |
| AST-849 | sub/AST-847/AST-849-retire-consult-chain-dispatch-claim |

**Epic worktree:** `astral-AST-847/` — seeded from `origin/ftr/AST-788-build-artifacts-chain-dispatch` (supersedes AST-788).

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 2cc40ce2-c13c-4612-8172-b4b09a32d736 |
| Hedy | engineer | fe466967-af2f-47bd-b13b-5c4afb99f00f |
| Betty | qa | 35ddcf6f-06ad-4d36-9365-e539904f85d2 |
| Radia | review | b2eaf0d6-b087-41bf-bc7d-7958f6f2402d |
|  |  |  |

---

## Original brief

Susan UAT: BUILD_ARTIFACTS daisy-chains complete every LLM hop but jobs do not reliably graduate to **Ready** (`CANDIDATE_REVIEW`). The [AST-803](https://linear.app/astralcareermatch/issue/AST-803/build-artifacts-chain-dispatch-and-state-flattening-build-artifacts) approach (flat `BUILD_ARTIFACTS` + consult wrapper graduation) is the wrong architecture.

**Target model (Susan, 2026-07-08):** Call the task runner for any dispatch hop. If `run_next` is set, the runner recurses to the next hop. After each successful hop, transition job state (e.g. `BUILD_ARTIFACTS` → `BUILD_ARTIFACTS.anticipate_scan`). Loop until `run_next` is empty, then graduate `BUILD_ARTIFACTS*` → `CANDIDATE_REVIEW`. No separate consult chain flow. Supersedes [AST-788](https://linear.app/astralcareermatch/issue/AST-788); resolve from the same `ftr/AST-788` branch.

### Comments

#### chuckles — 2026-07-09T01:52:48.734Z
[check-linear] Discussion — definition updated per thread; assignee Susan for final review.

— Chuckles

#### susan — 2026-07-09T01:50:33.249Z
Go ahead and update the description and I'll do a final review.

#### chuckles — 2026-07-09T01:04:59.934Z
[check-linear] @susan — confirmed before I touch the Description:

1. **DB hop labels on the job record** — runtime `job.state` values like `BUILD_ARTIFACTS.anticipate_scan` are written to the job row as the chain advances; they are **not** pre-registered in `JOB_STATES`. Mid-chain failure leaves the job on the last successful `<trigger>.<hop>` so redispatch can resume from that hop via `run_next`.

2. **Terminal transition** — when the dispatched hop's `run_next` is empty, graduate from the current compound label to the **next config job state** in the machine (`BUILD_ARTIFACTS.*` → `CANDIDATE_REVIEW` in UAT).

3. **`do_task` self-recursion** — dispatch invokes `do_task` for the claimed hop at the current job state; on success, advance `job.state` to `<trigger>.<completed_hop>`, then recurse into the `run_next` hop at that state until `run_next` is blank, then final machine transition. No consult chain wrapper.

I'll revise the definition to match — stripping registry/compound-config language and the per-hop `pass_state` model.

— Chuckles

#### susan — 2026-07-09T01:03:14.282Z
1. Yes.
2. No. The job record supports <trigger_state>.<hop_task> in the database on the job record itself.  The chain-run can grab <trigger_state>.<task_a> to run task_b where task_a has ask_b in the run_next field.  This means that if the job fails mid-chain, the job record remembers the state it last left successfully.
3. When the run_next is exhausted, the state transitions to the next job state in the config-driven machine.  So <config_job_state_g>.<db_hop_task> goes to <config_job_state_h>.  You see?
4. do_task owns recursion based on whether or not the dispatch_task key has a run_next on it or not.  If it does, run the chain as self-referencing subroutines (e.g. (do_task("anticipate_scan" for "BUILD_ARTIFACTS") runs, and when it's done, if anticipate_scan has a run next, then the state on the job record goes to BUILD_ARTIFACTS.anticipate_scan, then do_task("consider_job", "BUILD_ARTIFACTS.anticipate_scan"), and so on until run_next is blank, then it does the final job transition to "CANDIDATE_REVIEW".

Again, respond in the comments here before you edit the description.

#### chuckles — 2026-07-09T00:54:57.298Z
[check-linear] @susan — my read before revising the definition:

1. **Database-driven chain, not JOB_STATES registry:** Hop order and linkage come from `dispatch_tasks` + `agent_task.run_next` in the DB. We do **not** enumerate `<trigger_state>.<hop>` compound keys in `JOB_STATES` / config — that was wrong in the last draft.

2. **Job stays on the trigger state during the chain:** The entity remains at the dispatch row's `trigger_state` (e.g. `BUILD_ARTIFACTS`) while `do_task` walks the `run_next` graph synchronously. Mid-chain progress is persisted via execution history / `agent_data` (caller hydration per AST-769) — not via registering every hop as a named machine state.

3. **One machine transition at the end:** When `run_next` is exhausted, the **trigger state** graduates to the next job state already defined in the state machine (UAT: `BUILD_ARTIFACTS` → `CANDIDATE_REVIEW`) — same successor relationship as today, not a per-hop config `pass_state` on each hop.

4. **`do_task` owns recursion;** consult/dispatcher claim and invoke — no consult chain wrapper.

If that's right I'll strip all "compound holding state in registry" language from the definition. If mid-chain **job.state** should still show a runtime `<trigger>.<hop>` label (DB-written, not config-registered), say so — I had conflated runtime labels with registry entries.

— Chuckles

#### susan — 2026-07-09T00:53:10.387Z
NO. <input_state>.<hop> is NOT explicit in the job state registry. The whole POINT of the daisy chain is to be database-driven, not config-driven, but the originating trigger state still needs to graduate to the next job state in the machine.

Respond in a comment before revising the scope of the ticket to make sure you understand the whole picture.

#### chuckles — 2026-07-09T00:37:25.094Z
@susan Rewrote definition per your 2026-07-09 comment — generic `run_next` chain pattern (`<input_state>.<task_key>` → next job state), not `BUILD_ARTIFACTS`-hardcoded core logic. Removed premature Git/Team tables (dispatch adds those).

Remaining open questions:

1. **Next job state resolution:** dispatch_task metadata, TASK_CONFIG field, or JOB_STATES lookup?
2. **Terminal graduation gate:** domain persist gates vs empty `run_next` alone?
3. **`draft_cover_letter`:** separate dispatch path or inside unified chain loop?

— Chuckles

#### susan — 2026-07-09T00:35:14.320Z
Okay, this whole ticket needs a rewrite, because I do NOT want "BUILD_ARTIFACTS" to be hard coded in the codebase.  It's just a pattern.

Input state to run a dispatch_task that has a run_next daisy chain, the full chain runs before the input state graduates to the next state.  So, the job state machine has "BUILD_ARTIFACTS" > "CANDIDATE_REVIEW" but because BUILD_ARTIFACTS HAPPENS to be used in a dispatch task for a candidate to run anticipate_scan, which is a task that has a run-next.

So it's really <INPUT_STATE>.<task_key> is the internal state progression until the chain is exhausted, and then it's <INPUT_STATE>.<last_chain_task> → <NEXT_JOB_STATE>. Make sense?

#### chuckles — 2026-07-09T00:29:23.682Z
@susan Open questions before dispatch:

1. **Generate Artifacts entry state:** base `BUILD_ARTIFACTS` until first hop completes, or directly `BUILD_ARTIFACTS.<first_hop>`?
2. **Terminal graduation gate:** keep persist gate (resume body in job data) before `CANDIDATE_REVIEW`, or graduate on empty `run_next` alone?
3. **`draft_cover_letter`:** separate `CANDIDATE_REVIEW` batch dispatch, or fold into unified CHAIN runner?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
