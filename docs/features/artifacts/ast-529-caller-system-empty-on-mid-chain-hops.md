# AST-529 — CALLER_SYSTEM empty on mid-chain hops

<!-- linear-archive: AST-529 archived 2026-06-03 -->

## Linear archive (AST-529)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-529/caller-system-empty-on-mid-chain-hops  
**Status at archive:** Canceled  
**Project:** Astral Artifacts  
**Assignee:** Susan Somerset  
**Priority / estimate:** No priority / —  
**Parent:** —  
**Blocked by / blocks / related:** related to AST-303, AST-313, AST-527, AST-533, AST-528

### Description

## Purpose

During Phase E artifact daisy-chain runs, downstream hops receive empty `{$CALLER_SYSTEM}` and `{$CALLER_RESPONSE}` even when the parent hop completed successfully and sent non-empty resolved content to the LLM. Susan's repro (manual **Run** on `anticipate_scan`, May 29) shows `contemplate_job` and `advise_job_resume` hitting empty caller tokens mid-chain. That breaks prompts authored to consume prior-hop context via **AST-455** caller tokens. This ticket fixes propagation only; observability improvements are [AST-527](https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging).

## Functional scope

* **Caller token propagation:** After a successful parent hop, the resolved system text and cache segments that were actually sent to the LLM must populate `CALLER_SYSTEM` and `CALLER_CACHE_A`–`D` for the child hop, consistent with **AST-455** and admin preview `simulated_chain_context_for_preview` behavior.
* **CALLER_RESPONSE propagation:** The parent hop's parsed response must populate `CALLER_RESPONSE` for the child when the parent hop succeeded, using the same serialization rules as today's `_chain_tokens_for_next_hop`.
* **Mid-chain invariant:** If the parent hop's resolved system content was non-empty, the child must receive a non-empty `CALLER_SYSTEM` unless the parent explicitly resolved to empty (blank agent and blank system tab).

## Boundaries

* Does **not** add or change debug logging — that is [AST-527](https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging).
* Does not author or change Manage Tasks prompt text, agent assignment, or `run_next` wiring ([AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)).
* Does not add dispatch seed rows or change which task key owns `BUILD_ARTIFACTS` entry.
* Does not implement new chain tokens or change `TOKEN_SOURCES` registry beyond correct population of existing caller keys.
* Does not change LLM provider behavior, grading, or artifact persistence.
* Must not break consult, roster, or non-artifact `run_next` paths ([AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task), **AST-455**, **AST-469**).

## Acceptance criteria

1. Given a parent hop that completes successfully with non-empty resolved system content, the immediate child hop's `chain_context` includes a non-empty `CALLER_SYSTEM`.
2. Given a parent hop that completes successfully with a non-empty parsed response, the immediate child hop's `chain_context` includes a non-empty `CALLER_RESPONSE`.
3. Resolved cache segments sent to the LLM on the parent hop populate the matching `CALLER_CACHE_A`–`D` keys on the child hop.
4. Behavior matches admin preview chain simulation for the same parent task key and simulated parsed payload.
5. Existing component tests for daisy-chain token merge ([AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task), **AST-370**, **AST-455**) remain green; new or extended tests cover mid-chain `CALLER_SYSTEM` and `CALLER_RESPONSE` propagation.
6. Repro scenario from Original brief: manual multi-hop artifact chain run no longer passes empty caller tokens to child hops when parent hops produced content (verified by test or documented UAT steps).

## Dependencies and blockers

* [AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task) (daisy-chain `run_next`) — Done.
* **AST-455** (`CALLER_*` token model) — Done.
* [AST-527](https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging) (hop debug logging) — related sibling; recommended to land first for easier UAT, not a hard blocker.
* [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) (prompt authoring) — In Progress; empty caller tokens caused by blank parent prompts are out of scope (not a propagation bug).

## Open questions

1. Susan's repro dispatches `anticipate_scan` directly; the log shows `contemplate_job` then `advise_job_resume` downstream — which differs from the documented order `contemplate_job` → `anticipate_scan` → `advise_job_resume`. Is the bug on that ad-hoc wiring, on the intended three-hop chain after [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) wiring, or both?

---

## Original brief

127.0.0.1 - - \[29/May/2026 15:39:31\] "POST /api/admin/dispatch_tasks/5306/run HTTP/1.1" 200 -

Dispatching anticipate_scan — 1 available, batch anticipate_scan-05c78bfa-e28b-4768-927b-8ba3ebb08740

\[DEBUG\] \_run_task: running 'anticipate_scan' batch_size=1 batch_id=anticipate_scan-05c78bfa-e28b-4768-927b-8ba3ebb08740...

\[DEBUG\] \_run_unified\[job/BUILD_ARTIFACTS\]: claimed 1 entities (batch=anticipate_scan-05c78bfa-e28b-4768-927b-8ba3ebb08740) batch_call_mode=False dispatch batch_size=1

Token {$CALLER_SYSTEM} resolved to empty (chain_context, task=contemplate_job)

Token {$CALLER_RESPONSE} resolved to empty (chain_context, task=contemplate_job)

\[DEBUG\] do_task('contemplate_job'): brain_setting=Big provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset

\[DEBUG\] do_task('contemplate_job'): 2 system block(s) + 2 user block(s)

LLM deepseek task=contemplate_job 90.2s stop=end_turn tokens in=16400 out=3241

\[DEBUG\] send_to_deepseek('contemplate_job'): 90.2s | stop_reason=end_turn
\[DEBUG\]   vendor=deepseek-v4-pro tokens: fresh=16400 cache_read=0 cache_write=0 output=3241

Token {$CALLER_SYSTEM} resolved to empty (chain_context, task=advise_job_resume)

\[DEBUG\] do_task('advise_job_resume'): brain_setting=Big provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset

\[DEBUG\] do_task('advise_job_resume'): 3 system block(s) + 2 user block(s)

(Split from combined [AST-527](https://linear.app/astralcareermatch/issue/AST-527/daisy-chain-hop-debug-logging) report, 2026-05-29.)

### Comments

#### Susan Somerset — 2026-06-01T02:36:21.801Z

No code change necessary.  Resolving other issues (e.g. running them out of order) solved the problem.

---

**Canceled** 2026-06-01 — no code change; Susan confirmed empty caller tokens were caused by running hops out of order, not a propagation bug.
