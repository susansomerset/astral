# AST-788 — BUILD_ARTIFACTS substates do not graduate

<!-- linear-archive: AST-788 archived 2026-07-22 -->

## Linear archive (AST-788)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-788/build-artifacts-substates-do-not-graduate  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan UAT: jobs still stuck after the BUILD_ARTIFACTS resume-artifact chain; [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) was the wrong approach. Revert that work, cancel [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts), and replace compound-state plus per-hop graduation machinery with a **CHAIN** dispatch model: one base job state (`BUILD_ARTIFACTS`), hop order from `dispatch_tasks` rows and `run_next`, execution via a single `do_chain()` wrapper around `do_task()`, and terminal transition through the normal `JOB_STATES` machine to `CANDIDATE_REVIEW` (UI **Ready**).

## Functional scope

* **Revert and retire:** Roll back [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) product commits on `origin/dev`; cancel [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) with an expunged-from-codebase comment; retire epic `ftr/` / `sub/` refs at re-dispatch.
* **Remove graduation / compound hop states:** Drop `BUILD_ARTIFACTS.<task_key>` compound states, per-hop graduation helpers, and task-specific artifact runners. Jobs stay on base `BUILD_ARTIFACTS` for the duration of the chain (legacy in-flight rows matching `BUILD_ARTIFACTS*` are handled by mid-chain resume until flattened).
* **Task type enum:** Add optional task type on `TASK_CONFIG`: `CRAFT`, `RUBRIC`, `CHAT`, `CHAIN`. Only `CHAIN` is wired in consult for this epic; other values are schema-only.
* `do_chain()` **in consult:** One function wraps `do_task()` for `CHAIN` tasks whose `trigger_state` is a base state (e.g. `BUILD_ARTIFACTS`):
  * **Chain entry:** Among dispatch rows for the base trigger, pick the `task_key` that does not appear as any other row's `run_next` target.
  * **Execute:** Walk hops via `run_next`, reusing the inbound `batch_id`; state advances follow the **dispatch row sequence**, not compound entries in `JOB_STATES`.
  * **Retry vs error:** Retryable hop failure leaves the job on the **last completed** state for redispatch. Hard failures transition to `ERROR_BUILD_ARTIFACTS` (new holding state in `JOB_STATES`).
  * **Terminal:** When `run_next` is exhausted, transition `BUILD_ARTIFACTS` **→** `CANDIDATE_REVIEW` via standard `transition_job_state`.
  * **Mid-chain resume:** Same `do_chain()` for jobs whose state matches `BUILD_ARTIFACTS*` — resume from the dispatch row aligned with current progress; no separate code path per hop task.
* **Out of scope — coat-check:** Post-run harvest of artifact content from `agent_data` into `job_data` is a follow-on ticket.

## Design considerations (answered)

1. **Why compound** `BUILD_ARTIFACTS.<task_key>` **states?** Historical (AST-595/597) — duplicates what `dispatch_tasks` **+** `run_next` already express. Remove them; one base state, dispatch table defines hop order.
2. **What special BUILD_ARTIFACTS code exists today?** `run_resume_artifact_chain_for_job`, `_maybe_transition_resume_hop_progress`, compound `JOB_STATES`, `_resume_artifact_dispatch_row_ok`, batch-exit graduation ([AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts)), mid-chain caller hydration, cover-letter side effect on `contemplate_job` entry. With `do_chain()`, no task-specific consult functions are required. Mid-chain peeling into `job_data` is not required for graduation — coat-check deferred.
3. **What must change for normal flow?** Flatten to `BUILD_ARTIFACTS` **+** `CHAIN` **+** `do_chain()`; delete compound registry and graduation paths; terminal state via normal machine after chain end.

## Boundaries

* Revert [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) before new work; no graduation-helper pattern.
* `CRAFT` **/** `RUBRIC` **/** `CHAT`: config schema only — no consult wiring beyond `CHAIN`.
* No tracker coat-check / post-run `agent_data` slurp (follow-on).
* **Generate Artifacts** / **Cancel** on `RECOMMENDED`: enter base `BUILD_ARTIFACTS` only — behavior unchanged except flat state.
* Do not change hop prompts or `run_next` graph content — only execution and transition wiring.
* Must not break non-artifact consult dispatch paths.

## Acceptance criteria

1. [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) reverted on `origin/dev`; [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) cancelled; epic git refs retired before new child work.
2. Compound `BUILD_ARTIFACTS.<task_key>` states and [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) graduation helper removed from touched product paths.
3. `CHAIN` type recognized; `do_chain()` runs BUILD_ARTIFACTS hops via dispatch sequence + `run_next`, same `batch_id` throughout.
4. Successful chain end: `BUILD_ARTIFACTS` **→** `CANDIDATE_REVIEW`; job under **Ready** in Recommended Jobs UI.
5. Mid-chain resume from `BUILD_ARTIFACTS*` completes remaining hops and graduates without manual repair.
6. Retryable failure: job remains on last completed state; hard failure: `ERROR_BUILD_ARTIFACTS`; neither false-promotes to `CANDIDATE_REVIEW`.
7. Component coverage: chain entry discovery, full chain, mid-chain resume, retry hold, error state, terminal graduation.

## Dependencies and blockers

* [AST-595](https://linear.app/astralcareermatch/issue/AST-595/compound-build-artifacts-hop-states-and-chain-order-config-need-to) / [AST-597](https://linear.app/astralcareermatch/issue/AST-597/per-hop-transitions-and-agent-data-mid-chain-resume-need-to-pick-up) compound-hop model — superseded (remove as part of this epic).
* [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) revert before implementation.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-788](https://linear.app/astralcareermatch/issue/AST-788/build-artifacts-substates-do-not-graduate) (parent) | ftr/AST-788-build-artifacts-chain-dispatch |
| [AST-803](https://linear.app/astralcareermatch/issue/AST-803/build-artifacts-chain-dispatch-and-state-flattening-build-artifacts) | sub/AST-788/AST-803-build-artifacts-chain-dispatch |

**Epic worktree:** `astral-AST-788/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | a527e68e-b004-4852-bc84-6a06d1fd3fb2 |
| Betty | qa | a0aba386-c743-4f3a-be23-a74d280aa1d1 |
| Radia | review | 4b5ac55a-a0f3-47bb-87a9-7b0e6a9ff965 |

---

## Original brief

The next job state after all the BUILD_ARTIFACTS daisy-chains are complete should be "READY" (I think? I'm sure it's in the job transitions table in config.). Anyway, when I run the BUILD_ARTIFACTS task, the job record gets "left" in BUILD_ARTIFACTS.finalize_job_resume

### Comments

#### chuckles — 2026-07-10T03:20:58.509Z
[check-linear] answered — on dev; threads queued (@susan)

**Merged:** `origin/dev` includes **prep-uat(AST-788)** (`9758877` / earlier lands) — AST-788 composite is on staging integration branch.

**Open @chuckles threads on this ticket (06-25 onward):** UAT instructions, BUILD_ARTIFACTS graduation, anticipate_scan/draft_cover_letter firing — say **which one first**; not mixing into AST-850 UAT pass.

— Chuckles

#### chuckles — 2026-07-03T00:10:36.673Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-844** | BUILD_ARTIFACTS chain completes but job does not graduate to CANDIDATE_REVIEW |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-844** — _BUILD_ARTIFACTS chain completes but job does not graduate to CANDIDATE_REVIEW_
- **Issue reported:** Susan UAT on **origin/dev** after [AST-832](https://linear.app/astralcareermatch/issue/AST-832/uat-anticipate-scan-chain-abort-at-build-artifactsfinalize-job-resume) (2026-07-02): job still does **not** graduate from **BUILD_ARTIFACTS** to **CANDIDATE_REVIEW** when the BUILD_ARTI
- **Should now:** * **AC 4:** Successful chain end → `BUILD_ARTIFACTS` **→** `CANDIDATE_REVIEW`; job shows **Ready** in Recommended Jobs UI.
- **Quick check (this fix only):**
  1. Pull **origin/dev** with [AST-832](https://linear.app/astralcareermatch/issue/AST-832/uat-anticipate-scan-chain-abort-at-build-artifactsfinalize-job-resume) landed.
  2. Run full BUILD_ARTIFACTS CHAIN for a job through to `propose_application_responses` (last hop).
  3. Confirm LLM task succeeds.
  4. Observe job state remains **BUILD_ARTIFACTS** instead of **CANDIDATE_REVIEW**.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-02T23:58:36.645Z
Still not graduating from BUILD_ARTIFACTS at the end of the daisy chain.  Here is the log from the last task in the chain:

```
[2026-07-02 23:03:48] INFO src.core.agent: do_task index 1/1 3bf41b64-1cc8-4d6c-99e8-b4df3a0c5d14 -> task start
[2026-07-02 23:03:48] INFO src.core.agent:  | task_key=propose_application_responses batch_id=propose_application_responses-2d5792ff-9e62-4206-bb27-325cb5f95c2e index=3bf41b64-1cc8-4d6c-99e8-b4df3a0c5d14 in_run_next_chain=True
[2026-07-02 23:03:48] INFO src.core.agent:  | token_overlay chain_entry=False caller_source=agent_data parent=finalize_cover_letter caller_keys=CALLER_CACHE_A=populated(len=7644),CALLER_CACHE_B=populated(len=1952),CALLER_CACHE_C=populated(len=3471),CALLER_CACHE_D=empty,CALLER_RESPONSE=populated(len=1850),CALLER_SYSTEM=populated(len=25873)
[2026-07-02 23:03:48] INFO src.core.agent:  | caller_hydration=agent_data upstream=finalize_cover_letter
[2026-07-02 23:03:48] INFO src.core.agent:  | job_context tokens=VISIBLE_JD,ANALYSIS_GET,ANALYSIS_LIKE,RESUME_SECTION_CATALOG
[2026-07-02 23:03:48] INFO src.core.agent: [DEBUG] do_task('propose_application_responses'): brain_setting=Big provider=deepseek model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset
[2026-07-02 23:03:48] INFO src.core.agent:  | llm_params provider=deepseek brain_setting=Big model=deepseek-v4-pro max_tokens=16000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-07-02 23:03:48] INFO src.core.agent:  | blocks system=3 user=1 runtime_prompt_segments=4
[2026-07-02 23:03:48] INFO src.external.deepseek: LLM deepseek task=propose_application_responses 16.8s stop=end_turn tokens in=754 out=1139
[2026-07-02 23:03:48] INFO src.external.deepseek: send_to_deepseek index 1/1 propose_application_responses -> success
[2026-07-02 23:03:48] INFO src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=propose_application_responses duration=16.8s stop_reason=end_turn
[2026-07-02 23:03:48] INFO src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=754 cache_read=6528 cache_write=0 output=1139
[2026-07-02 23:03:48] INFO src.external.deepseek:  | response_preview:
[2026-07-02 23:03:48] INFO src.external.deepseek:  | {
[2026-07-02 23:03:48] INFO src.external.deepseek:  |   "agent_performance": {
[2026-07-02 23:03:48] INFO src.external.deepseek:  |     "status": "success"
[2026-07-02 23:03:48] INFO src.external.deepseek:  |   },
[2026-07-02 23:03:48] INFO src.external.deepseek:  |   "agent_payload": {
[2026-07-02 23:03:48] INFO src.external.deepseek:  |     "application_questions_found": false,
[2026-07-02 23:03:48] INFO src.external.deepseek:  |     "message": "The provided job description contains no explicit application questions. It’s a standard listing, not an application form. If the platform later asks generic prompts like “Why Assured?” or “Describe your relevant experience,” I can draft concise, 255-character responses once you share the exact questions."
[2026-07-02 23:03:48] INFO src.external.deepseek:  |   }
[2026-07-02 23:03:48] INFO src.external.deepseek:  | }
[2026-07-02 23:03:48] INFO src.core.agent:  | raw_response task_key=propose_application_responses lines=9 chars=448
[2026-07-02 23:03:48] INFO src.core.agent:  | {
[2026-07-02 23:03:48] INFO src.core.agent:  |   "agent_performance": {
[2026-07-02 23:03:48] INFO src.core.agent:  |     "status": "success"
[2026-07-02 23:03:48] INFO src.core.agent:  |   },
[2026-07-02 23:03:48] INFO src.core.agent:  |   "agent_payload": {
[2026-07-02 23:03:48] INFO src.core.agent:  |     "application_questions_found": false,
[2026-07-02 23:03:48] INFO src.core.agent:  |     "message": "The provided job description contains no explicit application questions. It’s a standard listing, not an application form. If the platform later asks generic prompts like “Why Assured?” or “Describe your relevant experience,” I can draft concise, 255-character responses once you share the exact questions."
[2026-07-02 23:03:48] INFO src.core.agent:  |   }
[2026-07-02 23:03:48] INFO src.core.agent:  | }
[2026-07-02 23:03:48] INFO src.core.agent: do_task(propose_application_responses) completed successfully batch_id=propose_application_responses-2d5792ff-9e62-4206-bb27-325cb5f95c2e index=3bf41b64-1cc8-4d6c-99e8-b4df3a0c5d14
[2026-07-02 23:03:48] INFO src.core.agent: do_task index 1/1 3bf41b64-1cc8-4d6c-99e8-b4df3a0c5d14 -> completed
[2026-07-02 23:03:48] INFO src.core.agent:  | task_key=propose_application_responses batch_id=propose_application_responses-2d5792ff-9e62-4206-bb27-325cb5f95c2e success=True
```

I wonder if the issue is that the daisy-chain doesn't "step out" back to "run_chain" or whatever when there is no run_next.  Confirm the issue in the code, @chuckles, before you try to resolve it.

#### chuckles — 2026-07-02T23:09:58.837Z
[check-linear] answered (@susan)

Merge tooltip: AST-788 re-recorded in merge_ticket_log at prep-uat 2026-06-27 — should show when parent is User Testing on staging with LINEAR_API_KEY.

UAT instructions + code trace (6/26): see prior [fix-uat] blocked thread — walkthrough scope, not check-linear.

anticipate_scan / draft_cover_letter not firing (6/27): UAT gap — fix-uat when you want a bug child.

— Chuckles

#### chuckles — 2026-06-27T19:36:45.917Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-832** | anticipate_scan chain abort at BUILD_ARTIFACTS.finalize_job_resume (draft_cover_letter blocked) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-832** — _anticipate_scan chain abort at BUILD_ARTIFACTS.finalize_job_resume (draft_cover_letter blocked)_
- **Issue reported:** Susan UAT on **origin/dev** (2026-06-27): **anticipate_scan** and **draft_cover_letter** Scheduled Actions show **Available > 0** but **Run** does not execute work.
- **Should now:** * **AC 5:** Mid-chain resume from `BUILD_ARTIFACTS*` (including `BUILD_ARTIFACTS.finalize_job_resume`) runs remaining CHAIN hops via `do_chain_for_job` and graduates to **CANDIDATE_REVIEW** — not `dispatch row mismatch` abort.
- **Quick check (this fix only):**
  1. Pull **origin/dev**; use candidate **somerset** (or any job at `BUILD_ARTIFACTS.finalize_job_resume` with chain prerequisites).
  2. Admin → **Scheduled Actions** → **anticipate_scan** — confirm **Available > 0**.
  3. Click **Run**; watch server log.
  4. Observe `artifact chain: dispatch row mismatch task_key=anticipate_scan job_state=BUILD_ARTIFACTS.finalize_job_resume` and thread exit with no state change.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-27T19:28:59.759Z
Neither "anticipate_scan" nor "draft_cover_letter" tasks are firing, despite having >0 available records.

```
127.0.0.1 - - [27/Jun/2026 12:21:35] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [27/Jun/2026 12:21:35] "POST /api/admin/dispatch_tasks/5306/run HTTP/1.1" 200 -
dispatcher._dispatch_one index 1/1 anticipate_scan -> task start
 | candidate_id=somerset available_count=1 entity_batch_id=anticipate_scan-3d14a80a-2be4-433b-a234-3a73cbb5af30 mode=CLICK run_next_chain=True entity_type='job' trigger_state='BUILD_ARTIFACTS'
Dispatching anticipate_scan — 1 available, batch anticipate_scan-3d14a80a-2be4-433b-a234-3a73cbb5af30
artifact chain: dispatch row mismatch task_key=anticipate_scan job_state=BUILD_ARTIFACTS.finalize_job_resume
[anticipate_scan] thread exited and cleared from registry
127.0.0.1 - - [27/Jun/2026 12:21:36] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [27/Jun/2026 12:21:40] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
```

#### chuckles — 2026-06-26T00:39:46.279Z
[fix-uat] blocked: Susan requested UAT instructions + code trace — not a product bug; no fix wave this run.

@susan

## Deploy / visibility (AST-806 fix)
1. Pull **origin/dev** (latest includes **prep-uat(AST-788)** merge ticket log rebuild).
2. Hover deploy env label — **AST-788** should appear in User Testing tooltip (`data/merge_ticket_log.json` on dev lists AST-788).

## End-to-end UAT — BUILD_ARTIFACTS CHAIN (maps to parent AC)

**Setup:** Staging from **origin/dev**; pick a job stuck at or eligible for **BUILD_ARTIFACTS** (Recommended Jobs shows state before Ready).

### AC 4 — Full chain graduation (primary repro)
1. Admin → **Scheduled Actions** → row with **Input State = BUILD_ARTIFACTS** (or trigger full chain entry).
2. **Run** for a candidate/job that has artifact chain prerequisites met.
3. Watch job state through admin or Recommended Jobs.
4. **Pass:** after all CHAIN hops complete, job state = **CANDIDATE_REVIEW**; UI **Ready** (not stuck on `BUILD_ARTIFACTS.finalize_job_resume` or any compound hop).

### AC 5 — Mid-chain resume
1. Find or create a job at a legacy compound prefix (e.g. `BUILD_ARTIFACTS.advise_job_resume`) or mid-chain BUILD_ARTIFACTS* state.
2. **Run** the same BUILD_ARTIFACTS scheduled action (or chain batch entry).
3. **Pass:** remaining hops run; ends at **CANDIDATE_REVIEW** without manual DB repair.

### AC 6 — Failure paths
1. **Hard failure** (e.g. missing `candidate_data` pre-chain): job → **ERROR_BUILD_ARTIFACTS**, not CANDIDATE_REVIEW.
2. **Retryable failure:** job stays on last completed hop / BUILD_ARTIFACTS base; does not false-promote.

## Code trace (confirm logic matches steps)

| Step | Code |
| --- | --- |
| Scheduled Action Run → batch | `consult._run_build_artifacts_chain_batch` |
| Per-job chain driver | `consult.do_chain_for_job()` — walks dispatch rows via `run_next`, same `batch_id` |
| Chain entry discovery | `_resolve_build_artifacts_chain_entry_task_key` — first hop = not referenced in any `run_next` |
| Mid-chain / legacy compound | `do_chain_for_job` hydrates from job state prefix + caller |
| Terminal success | `do_chain_for_job` → `tracker.transition_job_state(..., CANDIDATE_REVIEW)` when no `run_next` |
| Hard error | `_handle_chain_failure` → **ERROR_BUILD_ARTIFACTS** |
| Flat states | `config.py` — `BUILD_ARTIFACTS`, `ERROR_BUILD_ARTIFACTS`; CHAIN `task_type` on dispatch rows |

**Tests on dev:** `tests/component/core/test_consult.py` (AST-803 manifest) — chain entry, full graduation, mid-chain resume, error state.

Reply with job id + which Scheduled Action row you **Run** if graduation still fails — that becomes the next bug.

— Chuckles

#### susan — 2026-06-26T00:38:34.622Z
@chuckles provide me end-to-end UAT instructions and trace the logic in the code to confirm all test steps are ready as expected.

#### chuckles — 2026-06-25T17:13:25.527Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-806** | AST-788 missing from deploy env User Testing tooltip after prep-uat |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-806** — _AST-788 missing from deploy env User Testing tooltip after prep-uat_
- **Issue reported:** After **AST-788** prep-uat landed **AST-803** on **origin/dev**, Susan restarted from **origin/dev** and hovered the deploy env label. The User Testing tooltip did **not** list **AST-788** among parents ready for UAT (other User Testing parents appear; **AST-788** is missing).
- **Should now:** When Chuckles runs **prep-uat** for a parent and lands **ftr** on **origin/dev**, that parent appears in **merge_tickets** (deploy env tooltip) once the parent is in Linear **User Testing** and Susan pulls **origin/dev** — without manual log surgery.
- **Quick check (this fix only):**
  1. Land **AST-788** via **prep-uat** (**ftr** merged to **origin/dev**; parent moved to **User Testing**).
  2. Pull **origin/dev** locally or on staging.
  3. Hover the deploy env label (AST-791 tooltip).
  4. Observe **AST-788** is absent from the User Testing parent list.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-25T16:57:21.784Z
@chuckles Similar to 801, I do not see 788 in the list of User Testing issues pushed to origin/dev.  Please confirm this was merged to origin/dev for uat?

#### chuckles — 2026-06-25T04:47:27.859Z
[check-linear] Discussion — CHAIN architecture + Design considerations answers in Description (@susan)

— Chuckles

#### susan — 2026-06-25T04:45:56.262Z
### Minimal fix direction (for dev plan — no new helper layer)

1. **Revert** [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts) product commits on `origin/dev`; cancel [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts); retire epic git refs at re-dispatch.
2. ~~**Restore** inline batch-exit graduation in ~~`~~\_run_job_artifact_entry_batch~~`~~ (pre-789 shape): on chain success, ~~`~~transition_job_state → CANDIDATE_REVIEW~~`~~ with existing persist gate — fix **why** gate or transition fails, do not wrap in a new helper.~~
3. ~~**Investigate during build** with ~~`~~debug=True~~`~~: confirm ~~`~~finalize_job_resume~~`~~ runs, resume body persists, and batch exit reaches the transition (Susan does not require a separate repro ticket).~~
4. ~~**Keep** compound ~~`~~JOB_STATES~~`~~ and AST-597 per-hop transitions — fix is batch exit / persist timing, not renaming states or peeling content mid-chain.~~
5. ~~**Tests:** regression that full chain graduation reaches ~~`~~CANDIDATE_REVIEW~~`~~, not ~~`~~BUILD_ARTIFACTS.finalize_job_resume~~`~~.~~

2\. Remove all logic for graduation and translate the "compound" task into the existing simple job state transition machine.

3. Establish an enumerated task type in task config, which will support CRAFT|RUBRIC|CHAT|CHAIN.
4. Refactor consult.py to explicitly recognize tasks with optionally set types for CHAIN type (and ignore any other types for now), the trigger_state as a "base" state (e.g. "BUILD_ARTIFACTS")
   1. LOGICALLY identify the first position prompt by finding all the dispatch tasks with "BUILD_ARTIFACTS%", and identifying the one that does not appear in the "run_next" field.
   2. call do_task() for each dispatch_task for the base state reusing the batch_id sent to the build_artifacts, transitioning according to the sequence of dispatch_task records, not explicitly set in the job state machine in config.py
   3. When the chain ends (no run_next task), then job state transitions to the next state in the machine that comes after BUILD_ARTIFACTS (CANDIDATE_REVIEW)
5. Also set consult.py in the same function to run chain from mid-chain, so search for any jobs with "BUILD_ARTIFACTS\*" and resume the do_task chain. From the function's perspective, it doesn't matter which state it's starting from, it just chains the tasks together using the job's state (which may be "BUILD_ARTIFACTS" or "BUILD_ARTIFACTS.advise_job_resume"

##

#### chuckles — 2026-06-25T04:13:59.060Z
[check-linear] Discussion — research findings and dev guidance posted in Description (@susan)

— Chuckles

#### susan — 2026-06-25T04:10:45.725Z
@chuckles You need to do the research described as functional work as part of the Discussion phase.  By the time I move this issue to "To Do", you should have all the answers and guidance for the devs to build according to our standards and patterns.  Do the work now to answer (and restore) those questions (the 3 that I asked in the previous versin of the description in Design Considerations).

#### chuckles — 2026-06-25T02:00:52.259Z
[check-linear] Discussion — revert + fresh define noted; waiting on your scope call (@susan)

#### chuckles — 2026-06-25T01:22:29.752Z
@susan

1. Confirm revert scope: roll back AST-789 on **origin/dev** (already landed via prep-uat) plus retire **ftr/** / **sub/** refs for this epic before re-dispatch?
2. After revert, please repro once with job id and which Scheduled Action row you **Run** (first compound hop vs mid-chain vs full chain entry).
3. **AST-789** is **User Testing** — cancel and replace with new child(ren) on re-dispatch, or reset that ticket in place?

— Chuckles

#### susan — 2026-06-25T01:21:28.218Z
@chuckles The issue is persisting.  I think you've overengineered the solution.  revert the changes made for this ticket and start fresh in Discussion mode.  I need to get to the bottom of this, and understand the real problem and the real solution that doesn't invent a new code pattern.

---

_Implementation detail may live in git history on `origin/dev`._
