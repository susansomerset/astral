# AST-1986 — Tokens are unexpectedly empty.

<!-- linear-archive: AST-1986 archived 2026-10-13 -->

## Linear archive (AST-1986)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1986/tokens-are-unexpectedly-empty  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1987

### Description

## As-is

The five `Token {$…} resolved to empty (job_context, task=anticipate_scan)` warnings are not coming from a real `anticipate_scan` run. They come from the **Manage Tasks list probe**. `GET /api/admin/tasks` → `_enrich_tasks` (`src/ui/api/api_admin.py`) resolves every task's system prompt and cache blocks to estimate token counts. It does that with a candidate but **no job**, so `job_context` is `None`, and with `warn_on_empty` left at its default `True`. Every `source: job` token in the prompt therefore logs a warning on every screen load or refetch.

Evidence:

* The job-source tokens in `anticipate_scan`'s `system_prompt` (`data/admin/agent_task.json`) are exactly `VISIBLE_JD`, `ANALYSIS_JD`, `ANALYSIS_DO`, `ANALYSIS_GET`, `ANALYSIS_LIKE`, which are the five that warned. Its cache blocks carry none, and `RESUME_SECTION_CATALOG` isn't in that prompt, so it doesn't warn.
* The same five-line burst was captured in AST-1406's brief, sandwiched between `GET /api/admin/tasks?candidate_id=somerset` requests.
* The real dispatch path (`consult._run_dispatch_chain_job_batch` → `do_task`) always builds a single-job `ctx`, so `_job_context_for_call` returns a populated `build_job_token_context`. A job can't reach BUILD_ARTIFACTS with no description and no consult grades, so all five empty at once in a real run isn't plausible.

Result: noisy WARN lines in Railway and local logs, which read as a broken artifact hop when nothing is wrong.

**Runtime side:** when a token genuinely does resolve empty inside `do_task`, `resolve_tokens` only logs a WARNING per token and the prompt is **sent to the model anyway** with the blank in place. The only runtime guard is AST-530's mid-chain `{$CALLER_*}` check; the [AST-1780](https://linear.app/astralcareermatch/issue/AST-1780/list-enrich-autorun-gates-force-auto-off-dispatch-validation) empty-render gate runs before dispatch in the admin API and never scores job tokens.

## To-be

**Susan:** "An empty token at runtime should be an error, not a warning."

* **Runtime** (`do_task`, i.e. a real model call): if **any** token the prompt references resolves empty, the prompt is **not sent**. That covers candidate, job, rubric and config tokens, and `{$CALLER_*}` on any hop, entry included. Candidate content fields (Deal Breakers, Ideal Day, …) are never optional.
* **The entity goes to an error state, not "failed".** The hop's entity, mid-chain hops included, goes **straight** to the task's configured `error_state`: no `_RETRY` detour, and it never stays in state. It counts as an error, never as a failed judgment. **Susan:** "Do not retry. Just go straight to error state (even for midhops). … a retry will not resolve the problem. The problem is with our data, not the agent's response." That carve-out from `patt.task.dispatch-retry` is recorded in canon.
* One `ERROR` line names the task, entity and every empty token. No per-token `WARNING`s on this path.
* **Not runtime** (Manage Tasks token-count probe): silent. **Admin preview** stays as it is today.

## Answer to Susan's question

> Why are these tokens resolving as empty to begin with? Are we sending incomplete context to the agent???

**No. Nothing is sent to an agent when these warnings fire.** The Manage Tasks screen isn't an agent call: for each task row it renders the prompt locally only to estimate a token count. That screen has a candidate selected but no job, so every job-scoped token (`VISIBLE_JD`, `ANALYSIS_*`) is blank by definition, and the renderer warns about it as if it were a real call.

Checked this round:

* **Reproduced:** running the Manage Tasks list code (`_enrich_tasks('somerset')`) with nothing else emits exactly these five `anticipate_scan` warnings and no others.
* **Provenance:** all 50 `resolved to empty (job_context, …)` rows in the local `app_log` (5 for `anticipate_scan`, 45 for `contemplate_job`) have **no** `batch_id`. Every dispatch or agent run stamps a `batch_id`, so none of them came from an agent call.
* **Real runs:** the dispatch path (`consult._run_dispatch_chain_job_batch` → `do_task`) always passes the one job in scope, and `build_job_token_context` fills `VISIBLE_JD` from the job description and `ANALYSIS_*` from the consult grades. `TestAst513JobTokenContext` covers that path. The local database has no jobs, so I couldn't also show a populated live prompt here.
* **Production proof later:** Railway lines don't carry `batch_id` yet. [AST-1987](https://linear.app/astralcareermatch/issue/AST-1987) adds it, after which any empty-token warning from a real run will show its `batch_id`, and probe noise won't have one.

## Proposed steps

1. **Collect empties at render time** (`src/utils/config.py`): give `resolve_tokens` an optional collector (e.g. a list). When it's passed, each token that resolves empty, from any source including chain/`CALLER_*`, is appended instead of logged. Every other caller keeps today's behaviour.
2. **Runtime guard in** `do_task` (`src/core/agent.py`): pass one collector through `resolved_task_system` and the seven segment resolves (user, cache A–D, nocache). If it's non-empty after resolving, log one ERROR and return the existing failure shape (`success: False`, `error`) plus a marker such as `empty_tokens: [...]`, before any provider call. The existing `_mid_chain_empty_caller_tokens` guard either folds into this or stays as is; that's plan-fix's call.
3. **Route the entity to error, not retry or failed:** where a dispatcher maps `success: False` to a destination, an `empty_tokens` result goes straight to the task's `error_state` (never `_RETRY`, never stays in state) and counts under errors. The shared hook is `consult._consult_batch_fail_dest`, which today prefers the retry holding state, plus the claim-release-only branch in `_run_dispatch_chain_job_batch`. plan-fix audits the other `do_task` callers (roster, meteorite, candidate, contact, intake) for retry or "failed" routing on `success: False`.
4. **Quiet the probe:** `_enrich_tasks` (`src/ui/api/api_admin.py`) passes `warn_on_empty=False` on its three resolves.
5. **Tests:** a `do_task` whose prompt has an empty `{$VISIBLE_JD}` (or a blank candidate field, or an empty `{$CALLER_*}`) never reaches the provider, returns `empty_tokens`, and logs one ERROR. A job-dispatch run lands that job in the task's `error_state` (not its retry state) and counts it as an error rather than failed. A fully populated prompt proceeds. Loading Manage Tasks logs nothing.

## Component scope

* `src/utils/config.py` — modified: `resolve_tokens` can collect empty tokens for the caller instead of only warning.
* `src/core/agent.py` — modified: `do_task` runs the runtime empty-token guard before the provider call; `resolved_task_system` passes the collector through.
* `src/core/consult.py` — modified: job dispatch / batch failure routing sends an empty-token failure to `error_state` instead of retry holding, and counts it as an error.
* `canon/directives/active/patt.task.dispatch-retry.md` — modified: "When this doesn't apply" records the empty-token (data failure) carve-out, so the fix stops contradicting "always applies".
* `src/ui/api/api_admin.py` — modified: `_enrich_tasks` stops emitting empty-token warnings from its token-count probe.
* `src/core/roster.py`, `src/core/meteorite.py`, `src/core/candidate.py`, `src/core/contact.py`, `src/core/intake.py` — audited; changed only where `success: False` currently routes to a retry holding state or a "failed" outcome.

## Technical scope

* `src/utils/config.py` — modified function `resolve_tokens`: new optional keyword-only collector argument, appended per empty token across all sources; default behaviour unchanged.
* `src/core/agent.py` — modified functions `do_task` (collect, check, return failure with `empty_tokens` before the provider call) and `resolved_task_system` (keyword-only pass-through).
* `src/core/consult.py` — modified functions `_consult_batch_fail_dest` (or a sibling helper) and `_run_dispatch_chain_job_batch`: an empty-token result goes straight to `error_state`, with no retry holding and counted as an error.
* `src/ui/api/api_admin.py` — modified function `_enrich_tasks`: `warn_on_empty=False` on its probe resolves.
* Other `do_task` callers — modified only if their `success: False` branch sends the entity to retry holding or "failed".

## Decisions (answered by Susan)

1. **"Error" means fail the call.** I read it as don't send the prompt and fail the task, not "log at ERROR and send anyway". Default: fail the call.
   1. Error means do not send the prompt and mark the relevant entities to error state (or the previous hop state), rather than considering the entities as "failed" the task.
2. **Which tokens count.** Default: candidate and job tokens only. Chain tokens stay with the existing mid-chain guard. Rubric, config and pronoun tokens aren't included in this pass. Caution: a candidate with a genuinely blank optional field (e.g. `{$DEAL_BREAKERS}`) would now fail every task that references it. That matches the [AST-1780](https://linear.app/astralcareermatch/issue/AST-1780/list-enrich-autorun-gates-force-auto-off-dispatch-validation) Run/AUTO gate, which already blocks dispatch on empty candidate tokens, but it's stricter at hop level.
   1. Yes, All candidate content fields are NOT OPTIONAL.  Deal Breakers, Ideal Day, etc.  This is already factored for the dispatch task in the UI, but in the event that a {$CALLER\_ token is empty or ANY token is empty, it needs to error out because the prompt is incomplete.
3. **Admin preview** (`/api/admin/tasks/<task>/preview`) stays as it is today: it still warns and doesn't error.
   1. Yes.

## Ancestor candidates

- [ ] [AST-530](<https://linear.app/astralcareermatch/issue/AST-530>) — Chain hop debug logging (`docs/features/artifacts/ast-530-chain-hop-debug-logging.md`): introduced `_mid_chain_empty_caller_tokens`, the "empty token → don't call the model" guard this generalizes
- [ ] [AST-1780](https://linear.app/astralcareermatch/issue/AST-1780) — List enrich + AUTO/Run gates (`docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`): pre-dispatch gate on empty candidate tokens; this moves the same rule to runtime
- [ ] [AST-1396](<https://linear.app/astralcareermatch/issue/AST-1396>) — Gate empty-token warnings on agent ad-hoc load (`docs/features/foundation/ast-1396-gate-empty-token-warnings-on-agent-ad-hoc-load-loading-ad-hoc-agent-screen-spills-log-warnings-to-the-console.md`): same class of bug on a different admin screen
- [X] [AST-1779](https://linear.app/astralcareermatch/issue/AST-1779) — Empty-token predicate helper (`docs/features/dispatcher/ast-1779-empty-token-predicate-helper.md`): introduced `warn_on_empty=False` for probe resolves
- [ ] [AST-1406](https://linear.app/astralcareermatch/issue/AST-1406) — Page refreshes and modals are closed/lost (`docs/features/foundation/ast-1406-page-refreshes-and-modals-are-closed-lost.md`): its brief captured this exact warning burst on `/api/admin/tasks` but didn't address it
- [ ] [AST-1978](https://linear.app/astralcareermatch/issue/AST-1978) — RSC column on Manage Tasks (`docs/features/interface/ast-1978-rsc-column-on-manage-tasks.md`): most recent change to `_enrich_tasks`
- [ ] [AST-1163](<https://linear.app/astralcareermatch/issue/AST-1163>) — Issues while running anticipate_scan (`docs/features/artifacts/ast-1163-issues-while-running-anticipate-scan.md`): earlier empty-token fix on the real run path (the run-path cause is ruled out here)

## Notes for bug-fix

The earlier logging fix children [AST-1989](https://linear.app/astralcareermatch/issue/AST-1989) and [AST-1993](https://linear.app/astralcareermatch/issue/AST-1993) are Canceled; [AST-1987](https://linear.app/astralcareermatch/issue/AST-1987) owns that work. `ftr/AST-1986-log-candidate-id` (plus the `sub/AST-1986/*` refs, the registry rows and the `astral-AST-1986` worktree) still carries AST-1989's cancelled code. Run `cancel-linear` for [AST-1989](https://linear.app/astralcareermatch/issue/AST-1989/stamp-candidate-id-on-dispatch-logs-job-context-for-anticipate-scan) and [AST-1993](https://linear.app/astralcareermatch/issue/AST-1993/candidate-id-log-stamp-tests-bible-test-gap-for-ast-1989), and seed this fix on a **new** `ftr` segment (e.g. `ftr/AST-1986-probe-token-warnings`) so it doesn't stack on that code.

---

## Original report

```
[2026-10-06T03:31:47.808320350Z] [warn] src.utils.config: Token {$VISIBLE_JD} resolved to empty (job_context, task=anticipate_scan)
[2026-10-06T03:31:47.808326105Z] [warn] src.utils.config: Token {$ANALYSIS_JD} resolved to empty (job_context, task=anticipate_scan)
[2026-10-06T03:31:47.808329593Z] [warn] src.utils.config: Token {$ANALYSIS_DO} resolved to empty (job_context, task=anticipate_scan)
[2026-10-06T03:31:47.808333050Z] [warn] src.utils.config: Token {$ANALYSIS_GET} resolved to empty (job_context, task=anticipate_scan)
[2026-10-06T03:31:47.808336182Z] [warn] src.utils.config: Token {$ANALYSIS_LIKE} resolved to empty (job_context, task=anticipate_scan)
```

Tokens resolving to empty unexpectedly.

### Comments

#### susan — 2026-10-06T05:25:02.267Z
Do not retry. Just go straight to error state (even for midhops). This is because we retry in the event that an agent goofed up, but in this case specifically a retry will not resolve the problem. The problem is with our data, not the agent's response.

#### chuckles — 2026-10-06T05:21:26.499Z
@susan — the AST-2000 fix is paused on one canon decision. Ada's plan is done, but fix-board came back REVISE from both Joan and Betty.

**The conflict:** the plan sends an empty-token entity straight to the task's `error_state`, skipping the `_RETRY` state, and leaves it at its input state when there's no error state. That routing came from my wording in the To-be ("no retry detour"), not yours: you wrote "error state (or the previous hop state)". `patt.task.dispatch-retry` says it **always applies** and that **a failure never stays in state**. Joan flagged the plan as contradicting both.

**Pick one:**
1. **Follow the pattern (my recommendation):** treat an empty token like any other failed attempt. First failure goes to the `_RETRY` state, second goes to the task's `error_state`, and the entity never stays put. No canon change. The retry never calls the model, so it only costs one extra dispatch tick.
2. **Carve-out:** amend `patt.task.dispatch-retry` so empty tokens skip the retry and go straight to `error_state` (or the previous hop state). That's a canon edit, filed as its own gap child.

Betty's test gap child (the repro tests, plus a rewrite of the AST-530 caller-guard test) gets filed once you pick, because the routing tests depend on the answer.

To resume: answer here and assign this bug to Chuckles. It stays In Progress, and AST-2000 resumes from Plan Discuss.

#### chuckles — 2026-10-06T04:43:54.299Z
Resume note: the ticket shows Discussion now. To resume the fix, set it to **In Progress** and assign it to Chuckles. At Discussion it would fire bug-find, and at Todo it would re-dispatch onto a fresh `ftr`.

#### chuckles — 2026-10-06T04:43:42.361Z
@susan — bug-fix paused: a duplicate fix is already in flight.

* [AST-1987](https://linear.app/astralcareermatch/issue/AST-1987) (Astral Foundation) has the same root cause as this bug's symptom 1. Its fix [AST-1988](https://linear.app/astralcareermatch/issue/AST-1988) is in **User Testing** on `ftr/AST-1987-railway-log-batch-candidate-ids` and touches the same six files as [AST-1989](https://linear.app/astralcareermatch/issue/AST-1989), which is merged into `ftr/AST-1986-log-candidate-id`. Neither branch contains the other. Whichever lands on dev second will conflict.
* The two Railway designs differ. AST-1988 adds top-level `batch_id` / `candidate_id` JSON fields. AST-1989 puts `name [cid]: message` into the message text, on both Railway and plain console.
* Betty held gap child [AST-1993](https://linear.app/astralcareermatch/issue/AST-1993) at Plan Discuss for the same reason. Its tests would go red against whichever design loses.

Decisions needed:
1. Which fix is the real one: AST-1987's, AST-1986's, or a merge of the two?
2. Railway console format: separate JSON fields or a `[cid]` tag in the message?
3. Symptom 2 (empty `anticipate_scan` job tokens) got no code change. Hedy found no evidence that `job_context` was `None`; an empty job description or grades gives the same log. Should it be split into its own bug? If so, the job id from the 03:31 run would let her trace it.

After you decide, assign this ticket to Chuckles and the wave will resume.

---

_Implementation detail may live in git history on `origin/dev`._
