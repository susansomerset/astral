# AST-1280 — Connection error on dispatch task did not clear the batch_id

<!-- linear-archive: AST-1280 archived 2026-08-19 -->

## Linear archive (AST-1280)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1280/connection-error-on-dispatch-task-did-not-clear-the-batch-id  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

A job-artifacts **dispatch** run of `draft_job_resume` hit a DeepSeek **Connection error** and logged `do_task(...) provider call failed` with live `batch_id=draft_job_resume-2d304338-…`. Archie found that job row still carrying the populated `batch_id` after the failure and had to null it by hand. That violates claim → process → release: the job stays unclaimable until someone intervenes. This epic restores durable automatic release + error/hold so Connection-style provider failures cannot orphan a lock on the job-artifacts dispatch path.

## Functional scope

1. **Release after provider Connection error on job-artifacts dispatch.** When a dispatch-claimed job-artifacts task (repro: `draft_job_resume`) returns provider `success=False` with a non-empty Connection-style error, the job’s `batch_id` lock is cleared once that failure is handled — the row is not left claimed under that dispatch `batch_id` after the run finishes (no manual SQL/null required).
2. **Configured error/hold outcome.** On that same failure path, the job lands on the task’s configured artifact error/hold outcome (`ERROR_BUILD_ARTIFACTS` for this hop), except already-defined hold exceptions such as provider balance refusal (state held, claim still released).
3. **Failure remains auditable.** Existing ERROR lines that name `task_key`, `batch_id`, and the non-empty provider error stay visible in app_log / Execution History; release must not erase the failure trail.
4. **Debug release trail.** When `debug=True` on the touched failure path, Style D found/recorded detail includes `batch_released=true|false` with the non-empty error / error-or-hold outcome. No new debug-contract lines when `debug=False`.

## Architectural definition

* **Patterns to reuse**
  * `pattern.batch.entity-claim-process-release` — claimed jobs must clear locks on early failure as well as happy-path `finally`; orphaned `batch_id` after provider failure is a pattern violation.
* **New patterns proposed** — none
* **Applicable statutes**
  * `astral.batch.claim-process-release` — claim → process → release; clear on every early-exit path where rows were claimed.
  * `astral.batch.batch-id-first` / `astral.batch.batch-id-format` — consume existing dispatch `task_key-uuid` locks; do not invent a second lock shape.
  * `astral.agent.do-task-delegation` — core consumes structured provider `success=False` / `error` / `failure_class`; no adapter redesign unless release is proven blocked by an empty/unclassified envelope.
  * `astral.standards.debug-contract-gated` — found/recorded release trail only when `debug=True`.
  * `astral.standards.logging-via-utils` — keep the existing `do_task(...) provider call failed …` ERROR line.
  * `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — fix the stuck-claim failure path; no hop-topology redesign.
  * `astral.state.core-decides-transitions` — error/hold state changes stay in core, not the data layer.
  * Adjacent shipped work: **AST-1191** already taught dispatch-chain hop failure to release + apply `error_state`; this epic closes the live gap (or regression) on the Connection-error repro — not a second parallel release design.

## Boundaries

* Does **not** fix DeepSeek/network reliability or retry/backoff policy for Connection errors.
* Does **not** redesign `run_next` / BUILD_ARTIFACTS hop topology or reopen AST-1109 daisy-chain work.
* Does **not** own provider call budget / timeout classification (AST-1189) or empty/unusable response classification (AST-1190), beyond consuming their structured failure fields if present.
* Does **not** change candidate or company claim APIs ([AST-1257](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id) family) unless the same orphaned-lock bug is proven on those paths with evidence.
* Does **not** invent UI chrome for stuck claims; clearing the row lock + correct error/hold state is the product fix.
* Must **not** break successful draft/finalize resume hops or intentional balance-refusal hold (claim released, state held).
* Confirmed out of scope for entry path: candidate-artifacts flows and Agent Ad Hoc — repro is **job-artifacts dispatch**.

## Acceptance criteria

1. Reproduce the logged shape on a **job-artifacts dispatch** run: `draft_job_resume` with provider `Connection error.` and `do_task(draft_job_resume) provider call failed batch_id=draft_job_resume-<uuid> error=Connection error.` After the run finishes, that job row’s `batch_id` is null/empty (not still that uuid) — without operator intervention.
2. That job is on `ERROR_BUILD_ARTIFACTS` (or the task’s configured error_state), not left mid-chain under a live claim — unless the failure is a documented balance-refusal hold, in which case state is held and `batch_id` is still cleared.
3. A later dispatch claim for the same eligible work can claim that job again (no permanent lock under the failed batch_id).
4. With `debug=True` on the failure path, found/recorded lines show a non-empty error and `batch_released=true`. With `debug=False`, no new debug-contract lines are added.
5. Healthy `draft_job_resume` success path still claims, processes, and clears normally (no double-clear breakage; no stuck locks on success).

## Dependencies and blockers

* Related prior ship: **AST-1191** (artifact hop failure release + debug trail) — adjacent contract; this ticket owns the live Connection-error orphan claim, not a rewrite of AST-1191 statute text.
* Related: [AST-1257](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id) (candidate batch_id parity) — relatedTo only; not a blocker for this job-artifacts path.
* Archie confirmation (folded): she found the job record with `batch_id` still populated after the Connection-error failure and cleared it to null by hand. An earlier state census that showed only null `batch_id` groups was after that manual clear (or did not surface the stuck row).

## Open questions

none

## Proposed child tickets

#### 1: **Release orphaned job claim after provider Connection error - Katherine**

One vertical slice on the **job-artifacts dispatch** path: find why the live `draft_job_resume` Connection-error path left `batch_id` set despite claim-process-release / AST-1191 hop-failure release, restore durable automatic clear + configured error/hold, and keep debug `batch_released` honest. Does not own provider retry policy or hop-topology redesign.
**Citations:** `pattern.batch.entity-claim-process-release`; `astral.batch.claim-process-release`; `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`.

Monolith check: Functional scope has 4 capabilities; single child is intentional — release, error/hold, audit line, and debug `batch_released` must ship on the same failure path for UAT.

---

## Original brief

```
[2026-08-08 01:28:48] ERROR src.external.deepseek: LLM deepseek task=draft_job_resume 60.7s error=Connection error.
[2026-08-08 01:28:48] ERROR src.core.agent: do_task(draft_job_resume) provider call failed batch_id=draft_job_resume-2d304338-1caf-48a4-9d2c-e96f92895ebe error=Connection error.
```

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| [AST-1280](https://linear.app/astralcareermatch/issue/AST-1280/connection-error-on-dispatch-task-did-not-clear-the-batch-id) (parent) | ftr/AST-1280-connection-error-on-dispatch-task-did-not-clear-the-batch-id |
| [AST-1298](https://linear.app/astralcareermatch/issue/AST-1298/release-orphaned-job-claim-after-provider-connection-error-connection) | sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error |

**Epic worktree:** `astral-AST-1280/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/8675e3708318a1930b78ec858d53d9c0/5af8be6e-5434-4a78-8569-610b4b259765/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/76fc0138-37b1-4b19-a7a4-330a6a5a4aea/store.db` |
| Radia | review | `/home/susan/.cursor/chats/8675e3708318a1930b78ec858d53d9c0/599ee163-c3a6-4ef7-bab8-37ca369b84a1/store.db` |

### Comments

#### chuckles — 2026-08-10T04:32:03.454Z
@susan

Dispatch blocked — missing answers:

* Open question 1 still open in the Description (and unanswered in comments): your census showed every group with `batch_id: null`, including the `ERROR_BUILD_ARTIFACTS` row at the Connection-error timestamp. Was the orphaned claim already gone when you measured, or is the live defect something else?
* Until that is answered or explicitly removed from `## Open questions`, show-stopper §2b fails and I cannot materialize children.

Reply here (or clear/resolve that Open questions bullet), then Todo + assign Chuckles again when ready.

— Chuckles

#### chuckles — 2026-08-08T01:38:42.294Z
@susan

1. Your census shows every group with `batch_id: null`, including the `ERROR_BUILD_ARTIFACTS` row timestamped to the Connection error. Was the orphaned claim already gone when you measured (so the defect was transient / already cleared), or is the live defect something else — e.g. wrong end state, the `BUILD_ARTIFACTS.draft_job_resume` hop-label row, or you observed a non-null `batch_id` earlier that this aggregate does not show?

— Chuckles

#### chuckles — 2026-08-08T01:34:46.902Z
@susan

1. After the two ERROR lines, once the dispatch run had **finished** (not mid-call), did the job row still show `batch_id=draft_job_resume-2d304338-1caf-48a4-9d2c-e96f92895ebe`, and what **job state** was it in (mid-chain / BUILD_ARTIFACTS hop label vs `ERROR_BUILD_ARTIFACTS`)?
2. Entry path for the repro: Scheduled Actions / dispatcher tick, or Generate Artifacts / Agent Ad Hoc?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
