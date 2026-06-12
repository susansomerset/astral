<!-- linear-archive: AST-303 archived 2026-06-03 -->

## Linear archive (AST-303)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-306; related: AST-304; blocks: AST-300

### Description

Extend do_task() in src/external/anthropic.py to support self-chaining. After a successful task completes and saves its agent_response, do_task() checks the agent_task row for a run_next task key. If present, calls itself recursively passing the prior response as {$CALLER_RESPONSE} token and the accumulated cache blocks as {$CACHE_BLOCK_A} through {$CACHE_BLOCK_D}. Each step saves independently to agent_responses. Chain terminates when run_next is empty. Callers ([consult.py](<http://consult.py>), [roster.py](<http://roster.py>)) require zero changes — they call do_task() as today and receive the final chained result.

Cycle policy decision (2026-05-05): prevent repeat chains via run_next configuration/UI (dropdown should only allow task keys not already present in chain). No default numeric depth limit unless explicitly added in a separate decision.

### Comments

#### susan — 2026-05-06T21:05:14.963Z
Review feedback resolved. Branch `chuckles/ast-303-daisy-chain-task-execution-in-do_task` is ready for testing. Commit: `c85ad158`

#### susan — 2026-05-06T20:16:45.834Z
**Code review (Radia)** — `origin/dev`…`chuckles/ast-303-daisy-chain-task-execution-in-do_task`

**Counts:** fix-now **0** · discuss **2** · advisory **1**

**What’s solid:** Chaining in `src/core/agent.py` (not `anthropic.py`); invalid `run_next` / unknown `TASK_CONFIG` key → log + return current hop; inner failure returned unchanged; `chain_context` + `_chain_tokens_for_next_hop` wired for AST-304 tokens; same outer kwargs on recursive call (batch context preserved per §2.4 intent).

**Discuss:** (1) `CACHE_BLOCK_*` string shape vs what **AST-304** / prompts expect — avoid double-wrapping. (2) No runtime cycle cap (plan 7a) — infinite recursion still possible if `run_next` misconfigured.

**Advisory:** `CALLER_RESPONSE` via `json.dumps` can bloat child prompts on huge parsed payloads.

**Combined doc** (review appended, local commit `0c3a8940` on feature branch):
https://github.com/susansomerset/astral/blob/0c3a8940/docs/features/artifacts/ast-303-daisy-chain-task-execution-in-do-task.md

— Radia

#### susan — 2026-05-06T19:59:14.421Z
Built by Ada (b-build-linear complete).

**Branch:** `chuckles/ast-303-daisy-chain-task-execution-in-do_task`
**Commits:** `2a5b57ff` (feat: daisy-chain `do_task` on `run_next` + `chain_context`), `454e82a6` (docs: review stub on plan artifact).

**Handoff:** Radia — please run **c-review-linear** on this branch. Label review comment posted (agree conf/risk/scope).

#### susan — 2026-05-06T19:58:55.184Z
Label review (build agent):

Conf: agree — **conf-Medium** still matches (recursion + `chain_context` merge + failure return paths need careful review, but the plan anticipated this).
Risk: agree — **risk-HIGH** still matches (wrong chain can duplicate spend / mis-attribute audit / loop if misconfigured).
Scope: agree — **scope-MAJOR-CHANGE** still matches (`do_task` success-path behavior changes for every chain-capable task).

(This is the **b-build-linear** step-4 second opinion, posted after the implementation commit because the build started mid-thread — the substance still matches the plan’s self-assessment.)

#### susan — 2026-05-06T19:46:12.509Z
**AST-303 build progress (Ada)**

`do_task` now chains after a **successful** hop when the current `agent_task.run_next` is set:

- Reads **`run_next`** from the loaded `agent_task` row; unknown / invalid keys → **warning + return current hop result** (no recurse).
- **`await do_task(next_key, …)`** with the **same** `live_content`, `index`, `candidate_data` / `ctx`, `debug`, `store_agent_data` as the outer call.
- New optional kwarg **`chain_context`** (merged into `resolve_tokens` with **`SELECTED_AGENT`** for the current hop’s agent): parent hop supplies **`CALLER_RESPONSE`** plus **`CACHE_BLOCK_A`–`D`** materialized from that hop’s resolved **system / cache / nocache / live** strings (AST-304 chain tokens).
- **Return semantics:** inner failure → return inner dict; inner success → return inner dict (**final hop wins**).
- **Cycle / depth:** no new runtime hop cap or visited-set guard (**plan step 7 (a)** — acyclic **`run_next`** graph enforced administratively + UI/DB validation from earlier work).

**Commit:** `feat(AST-303): daisy-chain do_task on run_next with chain_context` on `chuckles/ast-303-daisy-chain-task-execution-in-do_task` (local; not pushed yet).

— Ada

#### susan — 2026-05-06T19:42:27.612Z
[check-linear] (Ada · Astral Artifacts)

**Pass — inbox:** Zero actionable thread items (nothing needing a reply after each issue’s latest `[check-linear]` / plan-ready comment).

**Board delta vs last run:** **AST-365** is now **Plan Approved** (still only the older plan-ready thread comment; no new discussion text).

**Scan (Ada + Astral Artifacts, `hasNextPage` false everywhere):**
- **Todo:** none
- **Plan Ready:** **AST-361**, **AST-305**, **AST-368**, **AST-370**
- **Plan Approved:** **AST-303**, **AST-365**
- **In Progress / Code Complete / Review Posted / Testing / PR Ready:** none

**Step 6 — post-inbox chain (Ada)**
- **a-plan-linear:** no **Todo** — skipped
- **e-push-linear:** no **PR Ready** — skipped
- **d-resolve-linear:** no **Review Posted** — skipped
- **b-build-linear:** **two** tickets at **Plan Approved** (**AST-365**, **AST-303**) — **not started in this check-linear pass** (needs a dedicated build session on the respective `chuckles/...` branches; this agent context is **`workspace/ada-idle`**).

#### susan — 2026-05-06T19:30:24.826Z
[check-linear] (Ada · **Astral Artifacts** only)

**Pass 1 — inbox:** No actionable thread items across Ada-labelled rows in this project (nothing needing a reply after the latest `[check-linear]` / plan-ready post on each scanned issue).

**Scanned (Ada + Astral Artifacts):** `Todo` (empty), `Plan Ready` (**AST-361**, **AST-305**, **AST-365**, **AST-368**, **AST-370**), `Plan Approved` (**AST-303**), `In Progress` / `Code Complete` / `Review Posted` / `Testing` / `PR Ready` (all empty). Pagination: `hasNextPage` false on each query.

**Step 6 — post-inbox chain (Ada)**
- **a-plan-linear:** No **Todo** + Ada + Astral Artifacts — skipped.
- **e-push-linear:** No Ada + Astral Artifacts at **PR Ready** — skipped.
- **d-resolve-linear:** No Ada + Astral Artifacts at **Review Posted** — skipped.
- **b-build-linear:** **AST-303** is **Plan Approved** — **not started in this check-linear pass** (full `do_task` daisy-chain implementation is its own build session; repo here is on **`workspace/ada-idle`**, not the feature branch). Say the word to run **`b-build-linear` AST-303** next.

#### susan — 2026-05-05T17:51:39.553Z
Per Susan: the **Manage Tasks `run_next` anti-repeat** behavior is **explicitly in-scope for AST-303** (not deferred), and short directives without “in the future…” should be treated as **this-ticket scope**.

Implemented:
- **UI:** `ui/frontend/src/pages/AdminTaskPrompts.tsx` — `run_next` `<select>` only lists next hops that keep the global `run_next` graph **acyclic** (matches the server rule), while still showing an invalid current value if one already exists in DB.
- **Server:** `src/data/database.py` — `save_agent_task` now rejects any `run_next` update that would introduce a **directed cycle** in current `agent_task.run_next` edges.

Compiled: `python3 -m py_compile src/data/database.py`, `cd ui/frontend && npx tsc -b --noEmit`.

#### susan — 2026-05-05T17:37:56.414Z
[check-linear]

Saw your new direction:

> "run_next dropdown should only include tasks not already in the daisy chain, so the chain cannot repeat."

I’m treating that as the cycle-policy decision for this chain effort: **no numeric depth cap**; enforce acyclic chains by configuration/UI and keep runtime behavior non-heuristic.

One scope check before I proceed with `b-build-linear` on AST-303:
- The dropdown behavior lives in Manage Tasks UI / task-save validation (historically AST-306 area), while AST-303 is `do_task` execution.
- AST-306 is already merged to `dev`, so changing dropdown filtering now is either:
  1) a follow-up ticket against the Manage Tasks surfaces, or
  2) added directly into AST-303 implementation scope by explicit instruction.

If you want me to proceed immediately under AST-303, I can implement execution-side chaining now using **acyclic-config assumption** (no hard hop limit, no visited-set guard) and leave UI-chain filtering for a follow-up ticket.

Reply with **(1)** follow-up ticket or **(2)** include UI filtering in AST-303, and I’ll continue build the same pass.

#### susan — 2026-05-05T17:36:06.758Z
I want the "run_next" drop down list to only include tasks that are not already in the daisy chain, so that the chain cannot repeat.

#### susan — 2026-05-05T17:29:54.488Z
[check-linear]

**Inbox pass:** Zero actionable thread items (nothing needing a reply after each issue’s latest `[check-linear]` / plan-ready comment).

**Step 6 — post-inbox chain (Ada)**
- **a-plan-linear:** No **Todo** + **Ada** + **Astral Artifacts** — skipped.
- **e-push-linear (AST-306):** `origin/dev` already includes merge **`618848e6`** (`Merge branch 'chuckles/ast-306-add-run-next-field-to-manage-tasks' into dev`). Linear was **PR Ready** while git had landed the work — synced: **Done**, feature-branch GitHub attachment removed, **`dev`** plan link added. I could not use GitHub MCP / `gh` here to confirm PR number, squash-merge UI, or delete the remote feature branch; if you still want the branch deleted on GitHub, do that from the merged PR or locally.
- **d-resolve-linear:** No **Ada** + **Review Posted** — skipped.
- **b-build-linear (AST-303):** **Plan Approved**; **AST-304** is **Done** and **AST-306** is now **Done** — plan §1 dependency gate is satisfied on **`dev`**. **Build paused** at **plan step 7 (cycle / depth guard)** until you pick explicitly:
  1. **(a)** Rely on acyclic admin configuration only.
  2. **(b)** Hard max hop count constant in `config.py` (needs your OK per limits rule).
  3. **(c)** Visited set of `task_key` per invocation (needs your OK per limits rule).

Reply with **a**, **b**, or **c** (and any numeric cap if **b**) and I’ll resume **b-build-linear** on **`chuckles/ast-303-daisy-chain-task-execution-in-do_task`**.

**Relations:** Cleared **blockedBy** **AST-306** and **AST-304** on this issue now that both are **Done** (MCP `removeBlockedBy`).

#### susan — 2026-05-04T20:48:36.714Z
[check-linear]

- **Thread / plan:** Merged `origin/dev` into `chuckles/ast-303-daisy-chain-task-execution-in-do_task`, added **Revision 1** to the execution doc (step 4: same outer `ctx` / kwargs; no gratuitous `get_*`; parameter-object pass-through / `build_resume({ job })` framing).
- **Commits:** merge prep then `d1279991` (plan-only revision — see branch log).
- **Linear:** **Plan Ready**; Conf/Risk/Scope/Feature/**Ada** unchanged. Separate Linear comment posted with revision summary.

**check-linear step 6 tail:** `e-push-linear` — no Ada **Astral Artifacts** ticket at **PR Ready** (skipped). `d-resolve-linear` — no **Review Posted** Ada work left after **AST-306** → **Testing** (skipped). `b-build-linear` — **AST-303** is **Plan Ready**, not **Plan Approved** (skipped until you approve).

#### susan — 2026-05-04T20:48:26.255Z
**Plan revision (a-plan-linear, queue: Ada)**

Doc: `docs/features/artifacts/ast-303-daisy-chain-task-execution-in-do-task.md` on `chuckles/ast-303-daisy-chain-task-execution-in-do_task`.

**Revision 1** folds Susan’s **AST-306** thread direction into step 4: same outer `ctx` / kwargs across hops unless this plan or **AST-304** documents otherwise; **no** new `get_*` helpers just to re-fetch caller-owned data; pass structured parameter objects through the chain (`build_resume({ job })` framing).

**Self-assessment (unchanged):** Scope **MAJOR-CHANGE**, Conf **Medium**, Risk **HIGH** — same justifications as prior plan; revision tightens execution contract only.

#### susan — 2026-05-04T19:48:28.918Z
**From Susan (via AST-306 thread) — chain context & API shape**

1. **Chained `do_task` hops** should receive the **same `ctx`** (and the same outer-call parameters: `live_content`, `index`, `candidate_data` / `ctx`, `debug`, `store_agent_data`) as the root invocation unless this ticket’s plan explicitly documents a narrower or extended shape for a specific hop.

2. **No gratuitous getters:** Prefer **orchestrating data the caller already has** into **parameter objects** passed down the chain, instead of adding new `get_*` helpers whose only job is to re-fetch what the caller could pass in.

3. **API framing example:** treat **`build_resume(job_id)`**-style entry points as **`build_resume({ job })`** (or equivalent dict/object) — **how the `{job}` is obtained is the caller’s concern**; the chain executor passes through structured inputs rather than re-resolving by id inside every hop.

When this ticket is (re)planned or built, the execution doc should spell out how `run_next` recursion composes with that rule so **AST-304** chain tokens and **AST-306** `run_next` land without a parallel “fetch everything again” pattern.

— Ada (posted per Susan’s request)

#### susan — 2026-04-29T20:28:30.958Z
**Plan ready (a-plan-linear, queue: Ada)**

**Doc:** `docs/features/artifacts/ast-303-daisy-chain-task-execution-in-do-task.md` on branch `chuckles/ast-303-daisy-chain-task-execution-in-do_task`.

**Self-assessment**
- **Scope — MAJOR-CHANGE:** Core `do_task` success path changes for every chain-capable task; depends on **AST-304** / **AST-306** for tokens and `run_next`.
- **Conf — Medium:** Tail `await do_task` pattern is clear; recursion, failure propagation, and cycle policy need alignment with sibling tickets + Susan on hop limits.
- **Risk — HIGH:** Bugs could duplicate API spend, corrupt audit trails, or loop; consult + artifacts depend on correct chaining.

**Note:** Linear text says `anthropic.py`; plan corrects to **`src/core/agent.py`** per §2.2 / §2.5 (orchestration stays in core; `anthropic.py` stays a thin API client).

**ASTRAL_CODE_RULES self-review:** §1.3 DRY (one loop/helper), §2.1 config for any confirmed hop guard, §2.4 same `batch_id` across hops, §2.6 disambiguated from entity state machine, §3.3 layer imports, §3.5 naming — no blocking conflicts if **AST-304**/**AST-306** land first.

---

# AST-303 — Daisy-Chain Task Execution in do_task()

**Linear:** [AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task) — Daisy-Chain Task Execution in do_task()  
**Project:** Astral Artifacts  
**Priority / estimate:** Urgent / 8 points  
**Parent / blocked-by:** Blocked by **AST-306** (Run Next column on `agent_task`) and **AST-304** (chain tokens in `resolve_tokens()`). Blocks resume/cover artifact chains (**AST-300**, **AST-301**, children).

## Goal

After a **successful** `do_task` run (schema/grades/decode all pass, response stored, `_store_agent_response` completed for that step), if the **current** `agent_task` row carries a non-empty **`run_next`** task key, invoke **`do_task` again** for that key so callers still issue **one** top-level `await do_task(...)` and receive the **final** step’s result dict. Each hop persists its own `agent_data` / `agent_responses` trail as today. Chain ends when `run_next` is empty/NULL or missing.

**Linear description** names `src/external/anthropic.py`; **implementation belongs in `src/core/agent.py`** — `do_task` orchestrates prompts, validation, storage, and already calls `send_to_anthropic` per **ASTRAL_CODE_RULES §2.2 / §2.5**. Do **not** add orchestration or recursion inside **`anthropic.py`**.

## Numbered steps

1. **Dependency gate (ordering)** — Land **AST-306** (`run_next` on `agent_task` + UI/API persistence) and **AST-304** (`{$CALLER_RESPONSE}`, `{$CACHE_BLOCK_A}`–`{$CACHE_BLOCK_D}` and any companion tokens `resolve_tokens` needs) **before** or **in the same integration branch as** this work so `get_agent_task()` exposes `run_next` and token resolution accepts chain context. If building on a branch that already includes those migrations, call that out in the PR description.

2. **Read `run_next` after success** — On the success path of `do_task` (after the existing `_store_agent_response(...)` that runs for a fully validated success, immediately before the final `return result`), read `run_next` from the same `agent_task_row` dict already loaded for the current `task_key` (or re-fetch current row if versioning requires). Treat **NULL / empty / whitespace** as “no chain”.

3. **Validate next key** — If `run_next` is set: strip; confirm the string is a **`TASK_CONFIG`** key (same rule as unknown `task_key` today). If invalid, **log and return the current step’s success result** (do not recurse) so misconfiguration fails closed without inventing a new task.

4. **Chain invocation** — Call `do_task` recursively with the **same** `live_content`, `index`, `candidate_data` / `ctx`, `debug`, and `store_agent_data` as the outer call unless this plan or **AST-304** explicitly documents a narrower or extended shape for a specific hop. **Do not** add new `get_*` helpers whose only job is to re-fetch data the caller already holds — orchestrate that data into **parameter objects** passed down the chain (same idea as preferring `build_resume({ job })` over `build_resume(job_id)` at API boundaries: **how** `{ job }` is obtained is the caller’s concern; the chain executor passes structured inputs through rather than re-resolving by id on every hop). Pass **only** the extra chain context **AST-304** defines (e.g. serialized prior `parsed_response` / raw text for `{$CALLER_RESPONSE}`, and materialized cache block strings for `{$CACHE_BLOCK_A}`–`{$CACHE_BLOCK_D}` derived from the **completed** step’s assembled prompts or API blocks — exact construction is owned by **AST-304**; this step wires the handoff).

5. **Failure and return semantics** — If an inner `do_task` returns `success: False`, **return that dict unchanged**; do not attempt further hops. If inner succeeds, **return the inner dict** (final hop wins). Outer caller therefore always sees a single result shape identical to today’s `do_task` contract.

6. **`batch_id` / entity storage** — Keep **`log_batch_id`** (and `entity_type` / `index`) from the outer invocation for all hops in one chain so **§2.4** audit trails stay one batch where callers already set context. Do not allocate a new batch per hop unless Susan explicitly changes that (would split `agent_data` by batch).

7. **Cycle / depth guard (product)** — Recursive `run_next` graphs must not spin forever. **Flag:** confirm with Susan whether to (a) rely on **acyclic admin configuration** only, (b) add a **hard max hop count** constant in `config.py`, or (c) maintain a **visited set** of `task_key`s for this invocation. Do not pick (b) or (c) without confirmation per project rule on implicit limits.

8. **Callers** — **No changes** to `consult.py`, `roster.py`, or other `do_task` callers (per ticket). Verify with a quick grep after implementation.

9. **Tests** — If the repo has an existing async test harness for `do_task` / agent, add a minimal test: stub DB rows with `run_next` unset → single call; with `run_next` pointing to a second stub task → two API paths mocked, two `append_agent_response`-level side effects or mocks as the harness allows. If no harness exists, document manual verification steps in the PR instead of inventing a large test layout.

## Files Changed (summary)

| File | Change |
|------|--------|
| `src/core/agent.py` | Tail of success path: read `run_next`, validate, build chain context per AST-304, `await do_task(next_key, ...)`, return inner result or current on skip/failure. |
| `src/utils/config.py` | **Only if** step 7 chooses a max-hop or similar literal — otherwise unchanged (tokens live under AST-304). |
| `src/data/database.py` | **Only if** not already landed via AST-306 — `run_next` column + `save_agent_task` / `get_agent_task` plumbing. Prefer **not** duplicating 306 in this ticket. |

## Decisions flagged for implementation

- **Cycle / depth policy** — Step 7; needs Susan’s call before coding guards.
- **Exact shape of chain `ctx` / `resolve_tokens` kwargs** — Owned by **AST-304**; this ticket passes through whatever 304 standardizes.
- **§2.6 wording** — State-machine “no daisy-chaining” refers to **entity job/company state**, not agent task prompt chains; avoid conflating in comments/review.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | One chain loop in `do_task` (or one private helper called from there); no second copy in `anthropic.py`. |
| §2.1 config | Any hop limit / token registry additions go through `config.py` / existing token patterns per AST-304. |
| §2.4 batch | Same `batch_id` across hops when present; each hop still writes `agent_data` / refs consistent with existing pattern. |
| §2.6 state machine | Agent task chain does not imply automatic **job** state transitions. |
| §3.3 imports | Core → data, external, utils only; no UI imports. |
| §3.5 naming | `run_next` matches DB/UI naming from AST-306. |

**Conflicts:** None blocking the plan if **AST-304** / **AST-306** land first. If 303 ships before 304/306, implementation would be incomplete — treat as ordering violation.

## Self-Assessment

**Scope — `scope-MAJOR-CHANGE`**  
Primary touch is `do_task`’s success path in **`src/core/agent.py`**, but behavior changes every successful task invocation chain-wide and depends on **`agent_task.run_next`** and **`resolve_tokens`** extensions delivered in sibling tickets.

**Conf — `conf-Medium`**  
Pattern (tail-call `await do_task`) is clear, but recursion with token plumbing, failure propagation, and cycle policy need alignment with **AST-304** / **AST-306** and Susan’s guard preference.

**Risk — `risk-HIGH`**  
A bug could duplicate API spend, drop responses, mis-attribute costs, or loop indefinitely; consult and artifact pipelines depend on correct chaining.

---

**Artifact doc path (repo):** `docs/features/artifacts/ast-303-daisy-chain-task-execution-in-do-task.md`

---

## Revisions

**Revision 1 — 2026-05-04**  
**Driven by:** Susan (via **AST-306** thread), consolidated on **AST-303** — same `ctx` / outer kwargs for chained hops; avoid gratuitous getters; prefer parameter objects (`build_resume({ job })` framing: caller supplies structured inputs, chain passes them through).  
**Changes:** Step 4 expanded to lock those rules into the execution doc so **AST-304** token work and **AST-306** `run_next` land without a parallel “fetch everything again” pattern.

## Review (stub — b-build-linear)

**Branch:** `<agent>/ast-303-daisy-chain-task-execution-in-do_task`  
**Implementation commit:** `2a5b57ff` — `feat(AST-303): daisy-chain do_task on run_next with chain_context`

**What shipped (code)**  
- `do_task` tail: after successful hop + `_store_agent_response`, read `run_next` from current `agent_task` row; validate `TASK_CONFIG` key; `await do_task(next_key, …)` with same outer kwargs; inner failure/success dict returned as final result.  
- Optional kwarg `chain_context` merged into `resolve_tokens` with per-hop `SELECTED_AGENT`; parent builds `CALLER_RESPONSE` + `CACHE_BLOCK_A`–`D` for child hop (AST-304 chain tokens).  
- Cycle/depth: **no** new runtime hop cap or visited-set guard (**plan step 7 (a)** — acyclic `run_next` graph via admin + Manage Tasks / DB validation).

**Plan step 9 (tests)** — No existing async harness for `do_task` in-repo; **manual verify:** two `agent_task` rows with `run_next` unset vs set to a second configured key; confirm one vs two Anthropic calls, same `batch_id` in traces, and `{$CALLER_RESPONSE}` resolves on hop 2 when prompts reference it.

## Review (Radia) — 2026-05-06

**Diff:** `origin/dev`…`<agent>/ast-303-daisy-chain-task-execution-in-do_task` (`src/core/agent.py` + this doc).

### What’s solid

- **Plan fidelity:** Chaining lives in **`src/core/agent.py`** (not `anthropic.py`), matches the plan and **§2.2 / §2.5** orchestration boundary.
- **`run_next` handling:** Empty/whitespace → no chain; key not in **`TASK_CONFIG`** → warning + return current hop (step 3).
- **Failure propagation:** Inner `do_task` failure dict returned as-is (step 5).
- **Chain tokens:** `_chain_tokens_for_next_hop` supplies `CALLER_RESPONSE` and `CACHE_BLOCK_*` for the child hop; **`chain_context`** merges into `_chain_context` for **AST-304** alignment.
- **Batch / context:** Same outer `live_content`, `index`, `ctx`, `store_agent_data`, `debug` on the recursive call — consistent with **§2.4** intent (one caller batch context).

### Issues

| Severity | Topic | Detail |
|----------|--------|--------|
| *Discuss* | Token shape vs prompts | `CACHE_BLOCK_B`/`C`/`D` wrap cache/nocache/live with fixed prefixes. Confirm with **AST-304** / prompt authors that templates will not double-wrap or diverge from `resolve_tokens` expectations. |
| *Discuss* | Cycle policy | Plan step **7 (a)** — no runtime hop cap; misconfigured cyclic `run_next` still risks infinite recursion. Acceptable only if admin/DB validation guarantees acyclic graphs. |
| *Advisory* | Prompt size | `CALLER_RESPONSE` uses `json.dumps` of parsed output — very large parsed payloads could inflate the child prompt; monitor in production. |

### Recommended actions

1. Manual / integration pass: two-step chain with a prompt that consumes `{$CALLER_RESPONSE}` on hop 2; confirm token substitution and single **`batch_id`** in ledger/agent_data traces.
2. Align with **AST-304** owners on whether `CACHE_BLOCK_*` string format should match any canonical delimiter already used in token resolution.

**Counts:** fix-now **0** · discuss **2** · advisory **1**

— Radia

## Resolution (f-resolve-linear) — 2026-05-06

**Radia review:** fix-now **0**; no code changes required for merge of review feedback.

**Discuss — `CACHE_BLOCK_*` shape**  
`_chain_tokens_for_next_hop` uses the same literal prefixes as `_assemble_blocks` (`--- CACHED CONTEXT ---`, `--- ADDITIONAL CONTEXT ---`, `--- CONTENT ---`); values are **post-`resolve_tokens`** strings from the parent hop. Child prompts should use `{$CACHE_BLOCK_B}` etc. **without** repeating those headers in the template (avoids double-wrapping). Documented here for prompt authors; no further AST-304 contract change in this pass.

**Discuss — runtime cycle cap**  
Per plan step **7 (a)** and product direction: no numeric hop limit in `do_task`. Acyclicity is enforced by **Manage Tasks** `run_next` dropdown + **`save_agent_task`** cycle rejection (see Linear thread 2026-05-05 on AST-303). Residual risk if bad data bypasses validation — accepted scope.

**Advisory — `CALLER_RESPONSE` size**  
Not implementing truncation or alternate serialization without explicit product approval (limits rule). Operational note only.

**Verify:** `python3 -m py_compile src/core/agent.py` (clean).
