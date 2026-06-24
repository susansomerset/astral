# AST-593 — Need to pick up and parse daisy chained prompts from the middle using agent_data content

<!-- linear-archive: AST-593 archived 2026-06-23 -->

## Linear archive (AST-593)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-593/need-to-pick-up-and-parse-daisy-chained-prompts-from-the-middle-using  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-300

### Description

## Purpose

During [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) UAT, a late resume-chain hop can fail after several successful upstream LLM hops whose prompts and responses are already stored in **agent_data** (per [AST-528](https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks) / [AST-531](https://linear.app/astralcareermatch/issue/AST-531/per-hop-dispatch-ledger-rows-for-run-next-chains-per-hop-execution)). Today the job stays in **BUILD_ARTIFACTS** for the whole synchronous chain run; on failure it lands in **BUILD_FAILED** and the next dispatch restarts from the configured entry task — re-running expensive upstream hops even when their outputs are still on disk. Susan needs incremental chain progress so a downstream validation or prompt issue (e.g. [AST-592](https://linear.app/astralcareermatch/issue/AST-592/draft-job-resume-dispatch-job-failed)) can be fixed and retried from the failed hop without replaying the entire artifact pipeline.

## Functional scope

* **Per-hop progress on the job:** When a daisy-chain hop completes successfully, the job records that progress before the next hop runs — so the product knows which hop finished and which hop is next. Susan's working hypothesis is encoding progress as **state plus next entry task** (e.g. awaiting `draft_job_resume` after `advise_job_resume` completes); the exact encoding is an open product decision (see Open questions).
* **Mid-chain dispatch entry:** The dispatcher can claim a job for a **Scheduled Action** row whose `task_key` names a mid-chain hop (not only `contemplate_job` / chain entry). That run starts `do_task` at that key and continues via existing `run_next` links for any hops still remaining in the same batch.
* **Reuse stored hop output:** When resuming from a mid-chain entry, chain tokens (`{$CALLER_*}`) for already-completed upstream hops are populated from persisted **agent_data** for that job and hop — not by re-invoking the LLM for hops whose successful responses are already stored.
* **Failure release:** If a hop fails, the job is released from the in-flight batch claim promptly so the next scheduler tick can dispatch it again at the appropriate entry task without double-processing the same job in one tick.
* **Terminal behavior unchanged:** When the terminal resume-craft hop succeeds and structure-keyed content persists per [AST-552](https://linear.app/astralcareermatch/issue/AST-552/build-artifacts-gate-and-structure-keyed-persistence-build-resume) / [AST-551](https://linear.app/astralcareermatch/issue/AST-551/structure-aligned-resume-chain-after-ast-477-build-resume-artifact), the job still transitions to **CANDIDATE_REVIEW** with populated `resume_content`. Mid-chain progress must not publish a candidate-ready draft before that terminal gate.
* **Debug traceability (backend):** When debug is enabled on a mid-chain or resumed dispatch run, each hop logs per [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) Style D (index header with `index N/M`, task key, outcome; substantive lines prefixed `|`; long payloads truncated 15 + omit + 15). Logs must show whether caller tokens were loaded from **agent_data** vs fresh LLM output for that hop.

## Boundaries

* **Phase E artifact chains first** — resume (and optionally cover-letter) `run_next` pipelines under **BUILD_ARTIFACTS** / [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact). Consult-path and roster `run_next` chains are out of scope for v1 unless Susan expands scope in Open questions.
* **Does not fix validation/schema bugs** on individual task keys ([AST-592](https://linear.app/astralcareermatch/issue/AST-592/draft-job-resume-dispatch-job-failed) and siblings remain separate fixes).
* **Does not author or reorder prompts** — hop order stays in Manage Tasks `run_next` ([AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) / [AST-450](https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry) dumb-chain rule); no ordered step arrays in config.
* **Does not replace per-hop Execution History** ([AST-528](https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks) family) — this feature consumes stored hop rows, not redesigns the UI.
* **Must not break** single-hop dispatch, ad-hoc workbench tests, consult batch grading, or the **RECOMMENDED → BUILD_ARTIFACTS** approval gate ([AST-552](https://linear.app/astralcareermatch/issue/AST-552/build-artifacts-gate-and-structure-keyed-persistence-build-resume)).
* **Must not auto-enter BUILD_ARTIFACTS** from consult pass states.

## Acceptance criteria

1. After hop *N* succeeds in a resume artifact chain, the job's recorded progress reflects that *N* completed and identifies the next hop entry task — observable without re-running hop *N*.
2. Susan can dispatch a mid-chain Scheduled Action (e.g. `draft_job_resume` at **BUILD_ARTIFACTS**) for a job whose upstream hops already succeeded; the run completes hop *N* onward using stored upstream **agent_data** for caller tokens — upstream LLM calls from that dispatch run are zero for hops already completed in a prior successful run.
3. When hop *N* fails, the job is not left claimed in a batch that blocks redispatch on the next tick; a subsequent manual or auto dispatch at the correct entry task processes the job once.
4. A full successful chain still lands the job in **CANDIDATE_REVIEW** with non-empty structure-keyed `resume_content`; mid-chain progress alone never shows a candidate-ready draft in the Job Analysis Report.
5. With debug enabled, logs for a resumed mid-chain run include Style D index lines per hop and indicate reuse of stored caller content vs new LLM calls.
6. Component or integration coverage demonstrates: per-hop progress after success, mid-chain entry with caller tokens from **agent_data**, failure release without duplicate batch claim, and unchanged terminal **CANDIDATE_REVIEW** transition.

## Dependencies and blockers

* [AST-531](https://linear.app/astralcareermatch/issue/AST-531/per-hop-dispatch-ledger-rows-for-run-next-chains-per-hop-execution) (per-hop **agent_data** / dispatch_ledger rows) — Done; prerequisite storage model.
* [AST-534](https://linear.app/astralcareermatch/issue/AST-534/honor-dispatch-task-key-in-dispatcher-consult-and-artifact-entry-bug) (honor dispatch row `task_key` at chain entry) — Done.
* [AST-552](https://linear.app/astralcareermatch/issue/AST-552/build-artifacts-gate-and-structure-keyed-persistence-build-resume) / [AST-551](https://linear.app/astralcareermatch/issue/AST-551/structure-aligned-resume-chain-after-ast-477-build-resume-artifact) (BUILD_ARTIFACTS gate, structure-keyed terminal persist) — in [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) UAT; terminal transition rules must stay aligned.
* [AST-592](https://linear.app/astralcareermatch/issue/AST-592/draft-job-resume-dispatch-job-failed) (immediate validation failure on `draft_job_resume`) — separate bug; mid-chain resume is most valuable after that hop can succeed, but architecture need not wait on the fix.
* Parent epic [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) (User Testing) — this capability closes open question #3 on partial chain failure / restart cost.

## Open questions

1. **Progress encoding:** Susan's brief suggests `<state>.<next_chain_key>`. Should progress be literal compound entries in **JOB_STATES**, a dedicated field on the job record (e.g. last completed hop + next entry `task_key`), or dispatch-only bookkeeping with **BUILD_ARTIFACTS** unchanged until terminal?
   1. I think there's an argument here to not bother with an elegant solution and instead just extend the BUILD_ARTIFACTS state into the suite of states "BUILD_ARTIFACTS.anticipate_scan" etc., and let the initial job transition state go to "BUILD_ARTIFACTS.anticipate_scan".  Put it in the config file to specify that the Generate Artifacts button causes a transition to that first position state for build artifacts. 
      
       I think we've talked about putting the actual task_config element in sequential order, so that could be a lookup in the future, but for now, just put it in the config explicitly.
2. **Recovery from BUILD_FAILED:** After a mid-chain failure, may Susan redispatch from the failed/next hop without candidate re-approval from **RECOMMENDED**, or must recovery still flow through **BUILD_FAILED → re-approve**?
   1. For daisy-chains, job doesn't reach a fail state.  It just stays in the last happy state it was in
3. **Scope for v1:** Resume artifact chain only, or the same mid-chain resume behavior for cover-letter and non-artifact `run_next` chains in one delivery?
   1. It's all the same chain, so yees, just the artifact chain.

---

## Original brief

Every job should transition when a step in the daisy chain is completed, so that a downstream issue with agent content does not require a complete restart for the job analysis.  This might just be updating the job state to <state>.<next_chain_key> and then setting up the dispatcher to run from each mid-stage link, which, in the event of a failure, would be released from its batch and be available to run separately without possibly catching the same record twice on the tick.

### Comments

#### betty — 2026-06-12T18:33:55.896Z
**Betty land preflight: CLEAN** @ `9cf9e2e4`

`merge-tree origin/dev vs origin/ftr/AST-593-mid-chain-artifact-resume` — no conflicts (tips identical; merge-base `9cf9e2e4`). Result tree `30b3987d`.

**Bible/tests:** no `changed in both` on `docs/ASTRAL_TEST_BIBLE.md` or `tests/`. §7.13zz on `origin/dev` includes **AST-595** · **AST-596** · **AST-597** rows + narrowed runs. `docs/ASTRAL_TEST_BIBLE.md` shasum `5d11ee6a65eaa1b8722d9266945492c85fb4642f`.

Joan **`push-dev`** may proceed for finish-up.

— Betty

#### susan — 2026-06-12T18:06:09.295Z
I'm moving this to PR Ready before completely testing it, because I need to prioritize other work, so I will need to come back to test this functionality soon.

#### chuckles — 2026-06-12T17:16:44.660Z
## Manual test steps

1. **Compound states (AST-595):** Approve **Generate Artifacts** on a RECOMMENDED job → job state becomes `BUILD_ARTIFACTS.anticipate_scan` (first hop in config), not flat `BUILD_ARTIFACTS`.
2. **Per-hop progress:** Run resume artifact chain; after each successful hop confirm job state advances to next `BUILD_ARTIFACTS.<task_key>` before the next hop runs (DB/state history or admin job view).
3. **Mid-chain dispatch (AST-596):** Create/use a Scheduled Action row targeting a mid-chain hop (e.g. `draft_job_resume`) at compound `BUILD_ARTIFACTS.*` state; dispatch claims and runs from that hop, not only `contemplate_job`.
4. **Hop failure release:** Force a hop failure mid-chain → job stays at last successful compound state (no `BUILD_FAILED`); job is released from batch claim and redispatches on next tick without double-claim.
5. **agent_data reuse (AST-597):** With upstream hops already succeeded and stored in agent_data, dispatch mid-chain → upstream LLM calls are not replayed; caller tokens come from stored data.
6. **Debug (optional):** Enable debug on a resumed run → Style D lines per hop show `caller_source=agent_data` vs `live_llm` appropriately.
7. **Terminal gate:** Full successful chain still lands **CANDIDATE_REVIEW** with populated `resume_content`; mid-chain progress alone does not show candidate-ready draft in Job Analysis Report.

`origin/ftr/AST-593-mid-chain-artifact-resume` @ `12471b5c` · local `dev` merged (§8). Restart app if running.

— Chuckles

#### chuckles — 2026-06-06T09:36:49.232Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-593 (parent) | ftr/AST-593-mid-chain-artifact-resume |
| AST-595 | sub/AST-593/AST-595-compound-build-artifacts-hop-states |
| AST-596 | sub/AST-593/AST-596-mid-chain-dispatch-claim-release |
| AST-597 | sub/AST-593/AST-597-agent-data-mid-chain-resume |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `e2b3809b-86a3-4e4d-8faa-b9fbb45d4353` | AST-593 (parent) | git |
| Hedy | `b49d0e21-21bc-47e1-8f3b-ddee10f9df66` | AST-595 | engineer |
| Betty | `615561c5-48c6-4558-92a0-7b9b7b3899c3` | AST-595 | qa |
| Radia | `195f36e3-b98e-42e4-9c62-5549831ed3f0` | AST-595 | review |
| Hedy | `20d7ce03-6a22-4c02-845c-389ed5a8254c` | AST-596 | engineer |
| Betty | `e093acc9-4806-43a9-819f-470910c1661f` | AST-596 | qa |
| Radia | `1caaaf6b-25b1-455e-a02d-7aa5e9444db0` | AST-596 | review |
| Ada | `c954ee99-f75d-4a48-8ca7-49eb3538f2b6` | AST-597 | engineer |
| Betty | `af270112-695c-4a68-814e-d54fe2f705ec` | AST-597 | qa |
| Radia | `4e21cd00-b4d7-4c7e-853c-afc088a7fda2` | AST-597 | review |

**Parent:** AST-593

**blockedBy:** AST-596 and AST-597 blocked by AST-595 (compound states first).

— Chuckles

#### chuckles — 2026-06-06T05:18:01.987Z
@susan Open questions on the definition (please answer in thread or inline in Description):

1. **Progress encoding:** compound `JOB_STATES` entries (e.g. `BUILD_ARTIFACTS.draft_job_resume`), a metadata field on the job row, or dispatch-only progress with state unchanged until terminal?
2. **Recovery from failure:** retry the failed/next hop without re-approval from **RECOMMENDED**, or keep **BUILD_FAILED → re-approve**?
3. **Scope for v1:** resume artifact chain only, or all **run_next** chains (cover letter, consult, roster) in the same delivery?

---

_Implementation detail may live in git history on `origin/dev`._
