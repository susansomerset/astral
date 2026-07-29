# AST-752 — Use agent_data for the "caller" content

<!-- linear-archive: AST-752 archived 2026-07-29 -->

## Linear archive (AST-752)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-752/use-agent-data-for-the-caller-content  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Today, when `do_task` chains to a child hop via `run_next`, upstream `{$CALLER_*}` token values travel in memory through recursive calls. If the chain fails mid-stream, a retry must reconstruct caller context from scratch or rely on hop-specific resume logic. Susan wants caller tokens resolved from persisted `agent_data` for the parent hop on the same entity — keyed off the entity's stored hop history and the batch that advanced its state — so a failed daisy-chain can resume at the next hop without re-running upstream LLM calls and without bespoke reconstruction per chain type.

## Functional scope

* **Universal caller hydration:** Any task whose prompt references `{$CALLER_*}` tokens resolves those tokens from persisted `agent_data`, not from in-memory `chain_context` merge alone — roster, consult, resume-artifact, and other `run_next` chains in one epic.
* **Entity scope:** Applies to all entity-indexed chains — job, company, and candidate — wherever caller tokens appear in assembled prompts.
* **Traceability:** Caller content must come from the correct upstream hop for that entity. The batch id recorded when entity state last advanced anchors lookup; that batch traces back to the parent hop's stored blocks so the child receives exactly the right caller payload, not an arbitrary prior attempt.
* **Cross-dispatch resume:** When dispatch starts at a downstream hop after upstream hops already succeeded in a prior run, caller tokens load from stored upstream `agent_data` with zero upstream LLM calls in the new dispatch.
* **Same-run continuity:** When a parent hop completes and immediately chains to its child within one dispatch, the child hop resolves caller tokens from the parent hop's just-persisted `agent_data` blocks (storage must be visible before the child hop assembles prompts).
* **AST-597 consolidation:** Refactor (or directly expand) AST-597's resume-artifact hydration helpers into this general caller lookup — one code path, not a parallel resume-only branch.
* **Non-caller chain tokens unchanged:** Tokens such as `{$JOB_LIST_VISIBLE}` and `{$SELECTED_AGENT}` continue to pass through existing `chain_context` / `resolve_run_next_live` behavior (roster locate→parse and similar paths).
* **Debug traceability:** With `debug=True`, hop logs indicate whether caller content was loaded from stored `agent_data` vs chain entry, consistent with the AST-538 / AST-597 caller-source contract.

## Boundaries

* Does **not** change the `{$CALLER_*}` token registry, Manage Tasks prompt authoring, or which tasks are wired via `run_next`.
* Does **not** change per-hop `agent_data` storage shape or Execution History presentation (AST-531 / AST-528).
* Does **not** change roster `resolve_run_next_live` DOM/visible threading (AST-469) — only how `{$CALLER_*}` is sourced.
* Does **not** change consult/artifact compound state transitions already delivered in AST-597 — may refactor shared hydration helpers but must not regress per-hop progress or terminal transitions.
* Does **not** change admin preview chain simulation (`simulated_chain_context_for_preview`) — preview remains simulated, not a live dispatch path.
* Does **not** address empty caller tokens caused by blank parent prompts or out-of-order hop execution (AST-529 was canceled for that class of issue).
* Does **not** change dispatch_task / agent_task seeding (AST-741 / AST-745).
* Must not break non-chained single-hop `do_task` calls, grading, or artifact persistence.

## Acceptance criteria

1. Given a successful parent hop in a `run_next` chain that stored `agent_data` for an entity, the immediate child hop resolves non-empty `{$CALLER_*}` tokens referenced in its prompt from those stored blocks — observable via test or UAT without relying on in-memory-only propagation.
2. Live chain behavior matches today's successful outcomes: a full chain that succeeded before this change still succeeds with equivalent assembled prompts (parity on roster locate→parse, consult/cover-letter chains, and resume-artifact chains).
3. Given an entity whose upstream hop(s) already completed successfully in a prior dispatch, starting dispatch at the next downstream hop completes without re-running upstream LLM calls — caller tokens come from stored `agent_data`.
4. Given a chain that failed on hop *N* after hop *N−1* stored successfully, retrying from hop *N* (or re-dispatching at hop *N*) succeeds using stored caller content from hop *N−1* — no manual chain reconstruction.
5. Caller lookup uses the batch id tied to the entity's state advancement history — not a best-guess scan across unrelated prior attempts — so the child hop receives the caller content from the hop that actually completed upstream for this chain attempt.
6. Hydration works for job-, company-, and candidate-indexed chains that reference `{$CALLER_*}` in their prompts.
7. AST-597 resume-artifact mid-chain entry behavior is preserved through the refactored general hydration path (no parallel resume-only branch left behind).
8. With `debug=True`, logs for hops that load caller content from storage include Style D detail distinguishing `agent_data` reuse from chain-entry / live paths.
9. Existing daisy-chain component tests (AST-303, AST-455, AST-469, AST-597 coverage) remain green; new or extended tests cover at least one roster chain and one non-roster chain using stored caller hydration.

## Dependencies and blockers

* [AST-303](<https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task>) (daisy-chain `run_next` in `do_task`) — Done.
* [AST-455](<https://linear.app/astralcareermatch/issue/AST-455>) (`{$CALLER_*}` token model) — Done.
* [AST-531](https://linear.app/astralcareermatch/issue/AST-531) (per-hop `agent_data` / ledger `batch_id`) — Done.
* [AST-597](https://linear.app/astralcareermatch/issue/AST-597/per-hop-transitions-and-agent-data-mid-chain-resume-need-to-pick-up) (resume-artifact mid-chain entry hydration) — Done; refactor/expand into general path here.
* [AST-469](<https://linear.app/astralcareermatch/issue/AST-469/roster-locateparse-split-run-next-job-list-visible-jobs-found-path>) (roster `run_next` + `JOB_LIST_VISIBLE`) — Done.
* none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-752 (parent) | ftr/AST-752-agent-data-caller-content |
| AST-769 | sub/AST-752/AST-769-general-caller-hydration-agent-data |
| AST-828 | sub/AST-752/AST-828-draft-cover-letter-compound-state-claim |
| AST-863 | sub/AST-752/AST-863-contemplate-job-mid-chain-dispatch |

**Epic worktree:** `astral-AST-752/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 70a8b58d-a0cd-44e4-93e3-eba9e100c42f |
| Hedy | engineer | dc9b1c54-74da-4959-a446-9172e4bd442c |
| Betty | qa | 63e335a8-b033-4ed2-aab3-e9fd8845a321 |
| Radia | review | ee374970-3775-409d-b09e-b388a490ac1b |

---

## Original brief

Instead of using data in memory for calling a daisy-chained task, have the token for "{$CALLER…" and look up the last batch the job was in and pull up the blocks from agent_data.  That way, if it fails midstream, the process can pick up where it left off without having to reconstruct the chain from scratch.

### Comments

#### chuckles — 2026-07-11T00:28:30.334Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-863** | contemplate_job unhandled from BUILD_ARTIFACTS.anticipate_scan mid-chain dispatch |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-863** — _contemplate_job unhandled from BUILD_ARTIFACTS.anticipate_scan mid-chain dispatch_
- **Issue reported:** Manual Run on dispatch task `contemplate_job` with trigger state `BUILD_ARTIFACTS.anticipate_scan` shows Avail=1, but dispatch processes zero jobs. Console logs:
- **Should now:** Mid-chain resume-artifact dispatch from compound holding state `BUILD_ARTIFACTS.anticipate_scan` routes `contemplate_job` through the dispatch-chain consult path, runs `do_task` for the claimed job using stored upstream `agent_data` for caller tokens, and advances or fails with a
- **Quick check (this fix only):**
  1. Have a job in `BUILD_ARTIFACTS.anticipate_scan` with upstream artifact hops already completed (Susan: candidate `somerset`, Avail=1 on contemplate_job dispatch row for that trigger state).
  2. Admin → Scheduled Actions → Run on that dispatch task (POST `/api/admin/dispatch_tasks/11172/run`).
  3. Observe `run_consult_task: unhandled task_key=contemplate_job for input_state=BUILD_ARTIFACTS.anticipate_scan` and 0 processed.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-11T00:14:38.983Z
Trying to run `contemplate_job` from BUILD_ARTIFACTS.anticipate_scan, Avail = 1, but when I click run, I get this in the console:

```
127.0.0.1 - - [10/Jul/2026 17:12:32] "POST /api/admin/dispatch_tasks/11172/run HTTP/1.1" 200 -
dispatcher._dispatch_one index 1/1 contemplate_job -> task start
 | candidate_id=somerset available_count=1 entity_batch_id=contemplate_job-37a65399-5527-45b9-b437-8546b2985402 mode=CLICK run_next_chain=True entity_type='job' trigger_state='BUILD_ARTIFACTS.anticipate_scan'
Dispatching contemplate_job — 1 available, batch contemplate_job-37a65399-5527-45b9-b437-8546b2985402
run_consult_task: unhandled task_key=contemplate_job for input_state=BUILD_ARTIFACTS.anticipate_scan
Loop mode contemplate_job: 0 processed — stopping
[contemplate_job] thread exited and cleared from registry
127.0.0.1 - - [10/Jul/2026 17:12:32] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [10/Jul/2026 17:12:36] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
```

We need some working mechanism to pick up mid-chain threads, I thought that setting up explicit mid-chain trigger states would work, but apparently not.

#### chuckles — 2026-06-26T19:05:32.867Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-828** | draft_cover_letter dispatch crashes on BUILD_ARTIFACTS.finalize_job_resume trigger state |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-828** — _draft_cover_letter dispatch crashes on BUILD_ARTIFACTS.finalize_job_resume trigger state_
- **Issue reported:** Scheduled dispatch of `draft_cover_letter` crashes before any LLM hop runs. Log shows `[draft_cover_letter/...] crashed` with `ValueError: Value 'BUILD_ARTIFACTS.finalize_job_resume' not in allowed list` raised from `get_new_job_batch` → `validate_value(_JOB_STATE_LIST, s)`.
- **Should now:** Dispatch for cover-letter / resume-artifact chain tasks claims jobs in compound `BUILD_ARTIFACTS.<task_key>` holding states (here `BUILD_ARTIFACTS.finalize_job_resume`) without crashing, and the daisy-chain run proceeds or fails gracefully with a domain error — not a config valid
- **Quick check (this fix only):**
  1. Have a job in compound state `BUILD_ARTIFACTS.finalize_job_resume` with a dispatch row for `draft_cover_letter` on that trigger state (Susan's staging run: batch `draft_cover_letter-fbdbc4dc-c45c-4485-b498-479134903585`, candidate `somerset
  2. Run scheduled dispatch (or manual Run on that dispatch task).
  3. Observe dispatcher crash in `_run_unified` → `get_new_job_batch` before `do_task` starts.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-26T18:52:51.179Z
```
dispatcher._dispatch_one index 1/1 draft_cover_letter -> task start
 | candidate_id=somerset available_count=6 entity_batch_id=draft_cover_letter-fbdbc4dc-c45c-4485-b498-479134903585 mode=CLICK run_next_chain=True entity_type='job' trigger_state='BUILD_ARTIFACTS.finalize_job_resume'
Dispatching draft_cover_letter — 6 available, batch draft_cover_letter-fbdbc4dc-c45c-4485-b498-479134903585
[draft_cover_letter/draft_cover_letter-fbdbc4dc-c45c-4485-b498-479134903585] crashed
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 544, in _dispatch_one
    await _tracked()
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 534, in _tracked
    await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 663, in _run_dispatch_loop
    summary = await _run_task(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 434, in _run_task
    summary = await _run_unified(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 240, in _run_unified
    bid, entities = get_new_job_batch(
                    ^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/tracker.py", line 554, in get_new_job_batch
    validate_value(_JOB_STATE_LIST, s)
  File "/Users/susan/chuckles/astral/src/utils/config.py", line 3397, in validate_value
    raise ValueError(f"Value {value!r} not in allowed list: {allowed_list}")
ValueError: Value 'BUILD_ARTIFACTS.finalize_job_resume' not in allowed list: ['NEW', 'VALID_TITLE', 'INVALID_TITLE', 'VALID_TITLE_RETRY', 'PASSED_JOBLIST', 'FAILED_JOBLIST', 'FAILED_TECHNICAL', 'JD_READY', 'JD_SCRAPE_FAIL', 'JD_SCRAPE_FAIL_COOKIE', 'JD_SCRAPE_FAIL_BOT', 'JD_SCRAPE_FAIL_MISSING', 'JD_SCRAPE_FAIL_CLOSED', 'JD_READY_RETRY', 'PASSED_JD', 'FAILED_JD', 'PASSED_DO', 'FAILED_DO', 'FAILED_TECHNICAL_DO', 'PASSED_GET', 'FAILED_GET', 'FAILED_TECHNICAL_GET', 'NEED_WEBSITE_CONTENT', 'PASSED_LIKE', 'PASSED_LIKE_RETRY', 'RECOMMENDED', 'BUILD_ARTIFACTS', 'ERROR_BUILD_ARTIFACTS', 'BUILD_FAILED', 'CANDIDATE_REVIEW', 'CANDIDATE_APPLIED', 'CANDIDATE_INTERVIEW', 'CANDIDATE_REJECTED', 'CANDIDATE_GHOSTED', 'FAILED_LIKE', 'FAILED_TECHNICAL_LIKE', 'ERROR_QUALIFY_JOB_LISTINGS', 'ERROR_EVALUATE_JD', 'CANDIDATE_SKIPPED']
[draft_cover_letter] thread exited and cleared from registry
127.0.0.1 - - [26/Jun/2026 11:51:41] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [26/Jun/2026 11:51:42] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [26/Jun/2026 11:51:47] "GET /api/deploy_status HTTP/1.1" 200 -
127.0.0.1 - - [26/Jun/2026 11:51:47] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -
127.0.0.1 - - [26/Jun/2026 11:51:47] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [26/Jun/2026 11:51:52] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [26/Jun/2026 11:51:57] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [26/Jun/2026 11:52:02] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
```

Tried to run on a job in "BUILD_ARTIFACTS.finalize_job_resume" and it gave me this error in the console.

#### chuckles — 2026-06-23T17:56:23.980Z
@susan Open questions on the definition:

1. **Scope:** All `run_next` chains in one epic, or roster first?
2. **Entity types:** Job-indexed only, or company/candidate chains too?
3. **AST-597 consolidation:** Refactor resume hydration into one general path, or layer alongside?
4. **Ambiguous hop history:** Latest successful hop per `task_key`, latest in dispatch ledger chain, or other rule?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
