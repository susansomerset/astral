# AST-1243 — Candidate Artifacts now daisy chain

<!-- linear-archive: AST-1243 archived 2026-08-17 -->

## Linear archive (AST-1243)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Candidate artifact rubrics are no longer meant to be built one Generate click at a time in the Artifacts UI. Prompts now daisy-chain from `craft_get_rubric` via `agent_task.run_next` (seed on `origin/dev`). This epic makes dispatch the build path: enter `REQUESTED_ARTIFACTS`, run the craft rubric chain with per-hop persistence into candidate artifact data, and watch hops in execution history the same way job `BUILD_ARTIFACTS` already does. Regenerate becomes an expensive, explicit reset of the whole rubric set—not a silent single-artifact rewrite. Resume daisy-chaining stays out of scope.

## Functional scope

* **Retire wrapper task keys.** Remove product references to `candidate_requested_resume` and `candidate_requested_artifacts` (config, seeds, dispatch provisioning, workers, tests). Those names must not remain as live dispatch `task_key`s.
* **States stay choosable without trigger-state validation.** `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS` remain viable candidate states. Operators can select either when creating a candidate-entity dispatch task whose opening hop is `craft_get_rubric`. Do not add input validation that restricts which of those triggers may bind to that task (resume state is included now so it does not have to be undone and redone later). Resume *daisy-chain generation* remains out of scope.
* **Artifacts chain via dispatch + persistence.** For `REQUESTED_ARTIFACTS`, dispatch claims the candidate and runs the craft rubric daisy chain starting at `craft_get_rubric`, following live `agent_task.run_next` succession. Each successful hop persists its rubric/content into the correct candidate artifact fields the same way `BUILD_ARTIFACTS` already persists job resume / cover letter (and siblings)—not via a new hop-order list in `config.py`. Terminal success graduates to `ARTIFACTS_READY`; failures use existing retry/error companions.
* **No hop sequencing in config.** Do not hard-code or list-sequence the craft rubric chain in `config.py`. Chain membership and order come only from live `agent_task.run_next`.
* **Execution history parity.** Operators watch the chain unfold hop-by-hop in execution history with the same operational feel as `BUILD_ARTIFACTS` (intermediate hops visible; not a black-box single UI generate).
* **Generate and Regenerate both kick the chain.** Empty-state **Generate** and **Regenerate** both move the candidate to `REQUESTED_ARTIFACTS` and start the dispatch build path. **Regenerate** alone shows the full-reset warning (explicitly naming Job Description, Get, Do, Like, and the other hops in the live chain); default control is **NO** / cancel. **Generate** does the same handoff **without** that scary warning.
* **Post-chain editability.** When the chain completes, new rubric contents appear under Artifacts navigation and remain editable as today.
* **Debug traceability (backend).** Touched `debug=True` dispatch/craft paths log what was found and what was recorded per hop (index headers, `|` detail, long-content truncation) per AST-538 / Code Rules—not pass/fail summaries alone.

## Architectural definition

* **Patterns to reuse**
  * `pattern.state.entity-state-transitions` — candidate enters `REQUESTED_ARTIFACTS` / graduates `ARTIFACTS_READY` (and retry/error) via core transitions against `CANDIDATE_STATES`; data layer does not choose next state.
  * `pattern.dispatch.run-next-chain-authority` (proposed; statute binds) — chain membership and succession come from live `agent_task.run_next`, not a parallel hop-order frozenset; entry hop is `craft_get_rubric` for this epic.
  * `pattern.batch.entity-claim-process-release` — dispatch claim → process → release for the candidate stage, same batch posture as other entity stages.
* **New patterns proposed**
  * none — prefer extending existing §2.6.0 / `BUILD_ARTIFACTS` persistence + hop-visible chain behavior to the candidate `REQUESTED_ARTIFACTS` / `craft_get_rubric` path over inventing a second chain model or config hop lists.
* **Applicable statutes**
  * `astral.dispatch.run-next-is-chain-authority` — `run_next` is succession authority; do not restate hop sets in config.
  * `astral.state.no-daisy-chain-in-run` — one transition step per cycle except the documented `run_next` carve-out (§2.6.0); no ad-hoc in-run pipeline outside that carve-out.
  * `astral.state.core-decides-transitions` — core picks targets from registries.
  * `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — states and task wiring live in config/seeds; do not invent parallel craft-hop sequencing lists in `config.py`.
  * `astral.dispatch.seed-auto-false` — new/changed stage dispatch rows stay click/auto-mode consistent with seed law.
  * `astral.standards.debug-contract-gated` — backend debug contract on touched `debug=` paths.
  * `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` / `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` / `astral.standards.logging-via-utils` / `astral.standards.data-raises-caller-logs` — universal product-code set.
  * `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — Generate/Regenerate confirm UI stays in the established frontend layout.

## Boundaries

* Does **not** daisy-chain resume generation (`craft_resume_base` / future resume chain)—explicitly out of scope; `REQUESTED_RESUME` may still be selected as a trigger state for `craft_get_rubric` without new trigger-state validation.
* Does **not** add hop-order or sequencing lists in `config.py`; persistence + `run_next` only.
* Does **not** redesign Artifacts navigation, rubric editing UX (beyond Generate/Regenerate handoff + Regenerate confirm), or rubric prompt copy (prompts already updated in `agent_task` seed).
* Does **not** change job `BUILD_ARTIFACTS` behavior; it is the reference model for persistence and execution-history feel.
* Does **not** reopen the AST-871 state vocabulary epic; it consumes `REQUESTED_*` / `*_READY` / retry / error states already shipped.
* Must not break existing edit-and-save of rubric artifacts after generation, or candidate transition history.

## Acceptance criteria

1. No remaining product references to `candidate_requested_resume` or `candidate_requested_artifacts` as live dispatch/task keys.
2. `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS` remain selectable candidate states when creating a candidate-entity dispatch task for `craft_get_rubric` (opening hop), with no new validation that blocks either pairing.
3. **Regenerate** shows a warning that **all** chain rubrics will be reset (explicitly includes Job Description, Get, Do, Like, and the other hops in the live chain); default control is **NO** / cancel; **YES** moves the candidate to `REQUESTED_ARTIFACTS`.
4. Empty-state **Generate** also moves the candidate to `REQUESTED_ARTIFACTS` / starts the same dispatch build path, without the full-reset scary warning.
5. With the candidate in `REQUESTED_ARTIFACTS` and dispatch running, execution history shows the daisy chain progressing hop-by-hop comparably to `BUILD_ARTIFACTS`.
6. On successful completion, candidate is in `ARTIFACTS_READY` (or the configured success state) and each chain rubric’s new content is visible and editable under Artifacts nav.
7. Failure paths still land on the configured retry/error companions for the artifacts stage without silent stuck mid-chain.
8. No craft-rubric hop sequencing list is introduced in `config.py`; succession remains `agent_task.run_next`, and per-hop persistence matches the `BUILD_ARTIFACTS` job-artifact persist posture.
9. Backend `debug=True` on touched craft/dispatch paths emits per-hop found/recorded detail under the debug contract (index headers + `|` lines; long payloads truncated).

## Dependencies and blockers

* Depends on shipped AST-871 candidate state machine (`REQUESTED_ARTIFACTS` / `ARTIFACTS_READY` / retry / error vocabulary and claim eligibility scaffolding).
* Depends on `origin/dev` `agent_task` seed where `craft_get_rubric` is the chain head (`run_next` succession already authored).
* Soft adjacency: job `BUILD_ARTIFACTS` chain (reference persistence + execution-history UX only).
* none otherwise blocking start.

## Open questions

none.

## Proposed child tickets

#### 1!!!: **Artifacts dispatch chain, persistence, and retire wrappers - Ada**

Wire `REQUESTED_ARTIFACTS` to open at `craft_get_rubric`, follow live `agent_task.run_next` (no hop-order list in `config.py`), persist each hop into candidate artifact fields with `BUILD_ARTIFACTS`-style persistence, surface hop progress in execution history like `BUILD_ARTIFACTS`, graduate/fail via configured states, and remove all live `candidate_requested_artifacts` / `candidate_requested_resume` task-key wiring (seeds/config/workers/provisioning). Keep `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS` selectable for `craft_get_rubric` without new trigger-state validation. Does **not** own Generate/Regenerate UI (#2). Resume daisy-chain generation stays out of scope.
**Citations:** `pattern.dispatch.run-next-chain-authority`, `pattern.state.entity-state-transitions`, `astral.dispatch.run-next-is-chain-authority`, `astral.state.no-daisy-chain-in-run`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.debug-contract-gated`.

#### 2!: **Generate/Regenerate REQUESTED_ARTIFACTS handoff - Katherine**

**Regenerate:** full-rubric-reset warning (Job Description, Get, Do, Like, and other live chain hops named; default **NO**); on **YES**, transition to `REQUESTED_ARTIFACTS`. **Generate** (empty state): same handoff to `REQUESTED_ARTIFACTS` / dispatch build path **without** the scary warning. Retire per-artifact ad-hoc generate as the build path for these craft rubrics. Does **not** own dispatch chain internals (#1).
**Citations:** `pattern.state.entity-state-transitions`, `astral.state.core-decides-transitions`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`.

**Monolith check:** Functional scope has 7 capabilities; 2 proposed children (dispatch/persistence slice vs UI handoff). Intentional—not one mega-ticket.

**New patterns:** none.

---

## Original brief

We have refactored the Candidate artifact prompts to daisy-chain from craft_get_rubric.  See updated prompt content in data/admin/agent_task.json.

I believe this means that we need to wire in the persistence of those responses into different parts of the candidate_data, instead of having them generate one at a time in the UI as the only way to build them.

Let's also change the "Regenerate" button to prompt the user if they want to reset all their rubrics and start the process over, or cancel out.  Make it explicit that this includes Job Description, Get, Do, Like, etc., and make the default button NO.

We had the beginning of this idea with candidate_requested_artifacts, but I think that got a bit lost in the noise, so we should pull those elements out entirely.  At a future point, we will daisy chain the resume generation, but that is out of scope for this ticket.

When this ticket is finished and I pull the uat-ready tip from origin dev, I expect:

1. No more references to `candidate_requested_resume` or `candidate_requested_artifacts`
2. `REQUESTED_RESUME` and `REQUESTED_ARTIFACTS` are viable candidate states (was this part of the candidate state machine revamp we did recently?), that I can choose when I create a dispatch task for craft_get_rubric (the opening hop of the chain) for the candidate entity type.
3. When I click "Regenerate", I will get a warning message that I will be reseting all of the rubrics, and default to NO response. (we maintain history, so it's not lost forever, but still, it's expensive), and when I click YES, the candidate state becomes 'REQUESTED_ARTIFACTS' from whatever state it was originally.
4. I will watch the daisy chain unfold in the execution history just like BUILD_ARTIFACTS does.
5. When the process completes, I will see the candidate's new rubric contents correctly in the Artifacts navigation options, and I can edit them just as I do today.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1243 (parent) | ftr/AST-1243-candidate-artifacts-now-daisy-chain |
| AST-1252 | sub/AST-1243/AST-1252-artifacts-dispatch-chain |
| AST-1253 | sub/AST-1243/AST-1253-generate-regenerate-handoff |
| AST-1264 | sub/AST-1243/AST-1264-uat-craft-get-run-next |

**Epic worktree:** `astral-AST-1243/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/0fe0adeba785cd631583da63349b7fa7/63a1d5f9-a86c-40c7-81f0-178dcaec9ec1/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/0fe0adeba785cd631583da63349b7fa7/b878f30f-5140-40c1-9b5a-1ba639155d5a/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/5a225d39-43bc-4fbb-a0dd-6ecec5fa5175/store.db` |
| Radia | review | `/home/susan/.cursor/chats/0fe0adeba785cd631583da63349b7fa7/0b1b3bd1-d108-4a85-ba20-006ddfe33d89/store.db` |

### Comments

#### chuckles — 2026-08-07T21:13:23.502Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1264** | craft_get_rubric run_next does not continue to craft_do_rubric |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1264** — _craft_get_rubric run_next does not continue to craft_do_rubric_
- **Issue reported:** On UAT for candidate `somerset` in `REQUESTED_ARTIFACTS`, dispatch ran `craft_get_rubric` successfully (LLM success, criteria persisted to `get_rubric`), but the daisy chain stopped there. Susan’s observation: `run_next` **for** `craft_do_rubric` **did not run.**
- **Should now:** After `craft_get_rubric` succeeds, live `agent_task.run_next` continues the candidate artifacts chain (`craft_do_rubric` next, then the rest of the chain) with hop-visible execution history like `BUILD_ARTIFACTS`, persisting each hop until terminal graduation to `ARTIFACTS_READY`
- **Quick check (this fix only):**
  1. Put a candidate in `REQUESTED_ARTIFACTS` with a dispatch task whose opening hop is `craft_get_rubric` (candidate entity).
  2. Run the dispatch batch with debug on (or watch Railway/app logs).
  3. Confirm `craft_get_rubric` completes and persists.
  4. Observe whether `craft_do_rubric` (and later hops) appear in execution history / logs via `run_next`.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-08-07T20:36:23.887Z
```
[2026-08-07 20:24:05] INFO src.external.deepseek: LLM deepseek task=craft_get_rubric 203.0s stop=end_turn tokens in=7333 out=13730
[2026-08-07 20:24:05] DEBUG src.external.deepseek: send_to_deepseek index 1/1 craft_get_rubric -> success
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=craft_get_rubric duration=203.0s stop_reason=end_turn
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=7333 cache_read=0 cache_write=0 output=13730
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  | response_preview:
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  | {
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |   "agent_performance": {
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |     "status": "success",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |     "failure_note": "",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |     "vector_reviews": [
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "TIRACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "DCRACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "YERACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "ECRACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "TSRACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "CTRACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "LORACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "RRRACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "RLRACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       "ETRACAVK",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  | <59 lines omitted>
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       {
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |         "label": "Employment Type Framing",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |         "code": "ET",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |         "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD explicitly seeks a fractional, contract, or principal consultant. The candidate's 14-year freelance practice is a direct match and a strength.\nB == The JD is for a startup or small company that values autonomy and versatility; the candidate's consulting background is likely viewed as an asset, not a liability.\nC == The JD is for a traditional full-time role at an established company. The recruiter notes the candidate's long stretch of independent consulting and may question cultural fit or commitment, but will consider if the skills align.\nD == The JD is from a large, bureaucratic enterprise that signals a strong preference for career track records at similarly large companies (e.g., \"must have experience in Fortune 500 environments\"). The candidate's consultant-heavy resume will likely be filtered out.\nX == The JD gives no indication of employment type expectations.",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |         "importance": 6
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       },
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       {
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |         "label": "AI / Technology Specialty",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |         "code": "AS",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |         "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD explicitly asks for AI product management, AI tooling, or AI-assisted development experience. The candidate's resume details building AI recruiting pipelines, multi-agent workflows, and prompt engineering, providing a clear, recent match.\nB == The JD mentions AI/ML as a nice-to-have or part of the tech stack; the candidate's AI work is sufficient to check that box and may differentiate her.\nC == The JD does not mention AI, so the candidate's AI experience is neutral. Recruiter won't penalize or reward heavily.\nD == The JD requires deep technical AI/ML expertise (e.g., \"must have built and deployed machine learning models,\" \"PhD in ML\") that the candidate's resume does not evidence. Her AI experience reads as tool utilization and orchestration, not model development, and a recruiter would screen out.\nX == The JD does not reference AI at all.",
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |         "importance": 4
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |       }
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |     ]
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  |   }
[2026-08-07 20:24:05] DEBUG src.external.deepseek:  | }
[2026-08-07 20:24:05] DEBUG src.core.agent:  | agent_data_write block_type=SYSTEM outcome=new_content agent_data_id=craft_get_rubric-f43cf82e-5b49-4d0e-99ba-c86fc38e5e59-system-ca93184605354f61 ref_agent_data_id=None
[2026-08-07 20:24:05] DEBUG src.core.agent:  | agent_data_write block_type=CACHE_A outcome=new_content agent_data_id=craft_get_rubric-f43cf82e-5b49-4d0e-99ba-c86fc38e5e59-cache_a-b576e511d36174c2 ref_agent_data_id=None
[2026-08-07 20:24:05] DEBUG src.core.agent:  | agent_data_write block_type=NO_CACHE outcome=new_content agent_data_id=craft_get_rubric-f43cf82e-5b49-4d0e-99ba-c86fc38e5e59-no_cache-d66e6e820a134548 ref_agent_data_id=None
[2026-08-07 20:24:05] DEBUG src.core.agent:  | agent_data_write block_type=TASK outcome=new_content agent_data_id=craft_get_rubric-f43cf82e-5b49-4d0e-99ba-c86fc38e5e59-task-a848a17c2ab07fe2 ref_agent_data_id=None
[2026-08-07 20:24:05] DEBUG src.core.agent:  | raw_response task_key=craft_get_rubric lines=89 chars=13571
[2026-08-07 20:24:05] DEBUG src.core.agent:  | {
[2026-08-07 20:24:05] DEBUG src.core.agent:  |   "agent_performance": {
[2026-08-07 20:24:05] DEBUG src.core.agent:  |     "status": "success",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |     "failure_note": "",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |     "vector_reviews": [
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "TIRACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "DCRACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "YERACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "ECRACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "TSRACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "CTRACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "LORACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "RRRACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "RLRACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       "ETRACAVK",
[2026-08-07 20:24:05] DEBUG src.core.agent:  | <59 lines omitted>
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       {
[2026-08-07 20:24:05] DEBUG src.core.agent:  |         "label": "Employment Type Framing",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |         "code": "ET",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |         "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD explicitly seeks a fractional, contract, or principal consultant. The candidate's 14-year freelance practice is a direct match and a strength.\nB == The JD is for a startup or small company that values autonomy and versatility; the candidate's consulting background is likely viewed as an asset, not a liability.\nC == The JD is for a traditional full-time role at an established company. The recruiter notes the candidate's long stretch of independent consulting and may question cultural fit or commitment, but will consider if the skills align.\nD == The JD is from a large, bureaucratic enterprise that signals a strong preference for career track records at similarly large companies (e.g., \"must have experience in Fortune 500 environments\"). The candidate's consultant-heavy resume will likely be filtered out.\nX == The JD gives no indication of employment type expectations.",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |         "importance": 6
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       },
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       {
[2026-08-07 20:24:05] DEBUG src.core.agent:  |         "label": "AI / Technology Specialty",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |         "code": "AS",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |         "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD explicitly asks for AI product management, AI tooling, or AI-assisted development experience. The candidate's resume details building AI recruiting pipelines, multi-agent workflows, and prompt engineering, providing a clear, recent match.\nB == The JD mentions AI/ML as a nice-to-have or part of the tech stack; the candidate's AI work is sufficient to check that box and may differentiate her.\nC == The JD does not mention AI, so the candidate's AI experience is neutral. Recruiter won't penalize or reward heavily.\nD == The JD requires deep technical AI/ML expertise (e.g., \"must have built and deployed machine learning models,\" \"PhD in ML\") that the candidate's resume does not evidence. Her AI experience reads as tool utilization and orchestration, not model development, and a recruiter would screen out.\nX == The JD does not reference AI at all.",
[2026-08-07 20:24:05] DEBUG src.core.agent:  |         "importance": 4
[2026-08-07 20:24:05] DEBUG src.core.agent:  |       }
[2026-08-07 20:24:05] DEBUG src.core.agent:  |     ]
[2026-08-07 20:24:05] DEBUG src.core.agent:  |   }
[2026-08-07 20:24:05] DEBUG src.core.agent:  | }
[2026-08-07 20:24:05] DEBUG src.core.agent: _capture_rubric_vector_feedback index 1/1 craft_get_rubric -> vector feedback capture start
[2026-08-07 20:24:05] DEBUG src.core.agent:  | vector_reviews trace candidate=somerset owner=grade_get
[2026-08-07 20:24:05] DEBUG src.core.agent:  | raw type=list repr=['TIRACAVK', 'DCRACAVK', 'YERACAVK', 'ECRACAVK', 'TSRACAVK', 'CTRACAVK', 'LORACAVK', 'RRRACAVK', 'RLRACAVK', 'ETRACAVK',…
[2026-08-07 20:24:05] DEBUG src.core.agent:  | normalize -> 11 lines
[2026-08-07 20:24:05] DEBUG src.core.agent:  | expected_codes=['CR', 'GW', 'ID', 'KW', 'RE', 'SK', 'SS', 'TA', 'TD', 'YE'] count=10
[2026-08-07 20:24:05] DEBUG src.core.agent:  | rubric_lookup_keys=['CR', 'GW', 'ID', 'KW', 'RE', 'SK', 'SS', 'TA', 'TD', 'YE'] count=10
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[0] TIRACAVK parse=ok code=TI
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[1] DCRACAVK parse=ok code=DC
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[2] YERACAVK parse=ok code=YE
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[3] ECRACAVK parse=ok code=EC
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[4] TSRACAVK parse=ok code=TS
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[5] CTRACAVK parse=ok code=CT
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[6] LORACAVK parse=ok code=LO
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[7] RRRACAVK parse=ok code=RR
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[8] RLRACAVK parse=ok code=RL
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[9] ETRACAVK parse=ok code=ET
[2026-08-07 20:24:05] DEBUG src.core.agent:  | line[10] ASRACAVK parse=ok code=AS
[2026-08-07 20:24:05] DEBUG src.core.agent:  | diagnostic reason=unknown_code parsed=[] missing=[] extra=[]
[2026-08-07 20:24:05] DEBUG src.core.agent:  | hydrate rows=11
[2026-08-07 20:24:05] DEBUG src.core.agent:  | TI TI — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | DC DC — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | YE Years of Experience Match — R/Always C/Always V/Keep — A == The JD requires up to 10+ years of experience in technical product/program …
[2026-08-07 20:24:05] DEBUG src.core.agent:  | EC EC — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | TS TS — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | CT CT — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | LO LO — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent: _capture_rubric_vector_feedback index 1/1 craft_get_rubric -> vector feedback unparseable
[2026-08-07 20:24:05] DEBUG src.core.agent:  | reason=unknown_code missing=[] extra=[] expected=['CR', 'GW', 'ID', 'KW', 'RE', 'SK', 'SS', 'TA', 'TD', 'YE']
[2026-08-07 20:24:05] DEBUG src.core.agent:  | TI TI — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | DC DC — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | YE Years of Experience Match — R/Always C/Always V/Keep — A == The JD requires up to 10+ years of experience in technical product/program …
[2026-08-07 20:24:05] DEBUG src.core.agent:  | EC EC — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | TS TS — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | CT CT — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | LO LO — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | RR RR — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | RL RL — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | ET ET — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | AS AS — R/Always C/Always V/Keep — 
[2026-08-07 20:24:05] DEBUG src.core.agent:  | agent_data_write block_type=RESPONSE outcome=new_content agent_data_id=craft_get_rubric-f43cf82e-5b49-4d0e-99ba-c86fc38e5e59-response-10027aa0186ab59e ref_agent_data_id=None
[2026-08-07 20:24:05] DEBUG src.core.agent: do_task(craft_get_rubric).persist_candidate_craft index 1/1 somerset -> recorded
[2026-08-07 20:24:05] DEBUG src.core.agent:  | found task_key=craft_get_rubric artifact=get_rubric
[2026-08-07 20:24:05] DEBUG src.core.agent:  | {"criteria": [{"label": "Title Alignment", "code": "TI", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD's title contains \"Senior Technical PM,\" \"Principal TPM,\" \"Technical Product Manager,\" or \"Technical Product Owner\" \u2014 the exact wording the candidate uses as a headline or in recent roles. The recruiter reads it and nods.\nB == The JD's title is a close variant (e.g., \"Staff Technical Product Manager,\" \"Lead Product Manager,\" \"Technical Program Manager\") that clearly maps to the candidate's experience, even if the exact wording differs. Minimal translation needed.\nC == The JD's title is at a different level or function (e.g., \"Director of Product,\" \"Engineering Manager,\" \"Solutions Architect\") where the recruiter may question fit, but the candidate's background could still answer the mail if the rest of the resume hooks them.\nD == The JD's title represents a fundamentally different career track (e.g., \"Software Engineer,\" \"Data Scientist,\" \"Marketing Manager\") that the candidate's titles do not support. A recruiter will almost certainly pass.\nX == The JD does not specify a job title or level clearly enough to evaluate.", "importance": 9, "grade_descriptions": [{"grade": "A", "description": "The JD's title contains \"Senior Technical PM,\" \"Principal TPM,\" \"Technical Product Manager,\" or \"Technical Product Owner\" \u2014 the exact wording the candidate uses as a headline or in recent roles. The recruiter reads it and nods."}, {"grade": "B", "description": "The JD's title is a close variant (e.g., \"Staff Technical Product Manager,\" \"Lead Product Manager,\" \"Technical Program Manager\") that clearly maps to the candidate's experience, even if the exact wording differs. Minimal translation needed."}, {"grade": "C", "description": "The JD's title is at a different level or function (e.g., \"Director of Product,\" \"Engineering Manager,\" \"Solutions Architect\") where the recruiter may question fit, but the candidate's background could still answer the mail if the rest of the resume hooks them."}, {"grade": "D", "description": "The JD's title represents a fundamentally different career track (e.g., \"Software Engineer,\" \"Data Scientist,\" \"Marketing Manager\") that the candidate's titles do not support. A recruiter will almost certainly pass."}, {"grade": "X", "description": "The JD does not specify a job title or level clearly enough to evaluate."}]}, {"label": "Domain Credibility", "code": "DC", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD is for a healthcare, medical device, or healthtech company. The candidate's resume surfaces that domain repeatedly: HIPAA/FHIR compliance at EMIDS, FDA submissions at Green Mars, B2B2C wellness platform at PTown.tech. The recruiter immediately sees the fit.\nB == The JD is for a SaaS, cloud platform, or enterprise software company. Her resume mentions SaaS, cloud platforms, and enterprise clients (e.g., Microsoft, PTown.tech). The domain is not her deepest specialty but still credible.\nC == The JD is for a sector where she has no direct mention (e.g., fintech, e-commerce) but her transferable skills (platform delivery, stakeholder alignment) are strong. A recruiter might give her a look if the JD isn't rigid about industry.\nD == The JD is for a highly regulated or specialized industry outside healthcare (e.g., defense, aerospace, banking) where the JD explicitly requires that sector's compliance or domain expertise, and the resume has none.\nX == The JD does not indicate an industry or domain.", "importance": 7, "grade_descriptions": [{"grade": "A", "description": "The JD is for a healthcare, medical device, or healthtech company. The candidate's resume surfaces that domain repeatedly: HIPAA/FHIR compliance at EMIDS, FDA submissions at Green Mars, B2B2C wellness platform at PTown.tech. The recruiter immediately sees the fit."}, {"grade": "B", "description": "The JD is for a SaaS, cloud platform, or enterprise software company. Her resume mentions SaaS, cloud platforms, and enterprise clients (e.g., Microsoft, PTown.tech). The domain is not her deepest specialty but still credible."}, {"grade": "C", "description": "The JD is for a sector where she has no direct mention (e.g., fintech, e-commerce) but her transferable skills (platform delivery, stakeholder alignment) are strong. A recruiter might give her a look if the JD isn't rigid about industry."}, {"grade": "D", "description": "The JD is for a highly regulated or specialized industry outside healthcare (e.g., defense, aerospace, banking) where the JD explicitly requires that sector's compliance or domain expertise, and the resume has none."}, {"grade": "X", "description": "The JD does not indicate an industry or domain."}]}, {"label": "Years of Experience", "code": "YE", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD requires 8\u201315 years of relevant experience. The candidate's resume shows 20+ years of progressively responsible technical product/program roles, clearly exceeding the requirement.\nB == The JD requires 15\u201320 years, and the candidate meets that upper bound exactly; a recruiter sees adequate seniority.\nC == The JD requires fewer than 8 years (the candidate may appear overqualified) or exactly 20+ years with unspecified domains (the candidate hits the number but not necessarily in the exact field the JD wants). The recruiter may pause but could advance if other vectors look strong.\nD == The JD requires a specific number of years in a very narrow domain (e.g., \"5+ years in AI/ML product management\") that the candidate's timeline does not support; the recruiter reads it as a miss. Also a D if the JD is explicitly for a junior individual contributor role and the candidate's 20-year career screams \"too senior.\"\nX == The JD does not specify a years-of-experience requirement.", "importance": 5, "grade_descriptions": [{"grade": "A", "description": "The JD requires 8\u201315 years of relevant experience. The candidate's resume shows 20+ years of progressively responsible technical product/program roles, clearly exceeding the requirement."}, {"grade": "B", "description": "The JD requires 15\u201320 years, and the candidate meets that upper bound exactly; a recruiter sees adequate seniority."}, {"grade": "C", "description": "The JD requires fewer than 8 years (the candidate may appear overqualified) or exactly 20+ years with unspecified domains (the candidate hits the number but not necessarily in the exact field the JD wants). The recruiter may pause but could advance if other vectors look strong."}, {"grade": "D", "description": "The JD requires a specific number of years in a very narrow domain (e.g., \"5+ years in AI/ML product management\") that the candidate's timeline does not support; the recruiter reads it as a miss. Also a D if the JD is explicitly for a junior individual contributor role and the candidate's 20-year career screams \"too senior.\""}, {"grade": "X", "description": "The JD does not specify a years-of-experience requirement."}]}, {"label": "Education Credential", "code": "EC", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD does not list a degree requirement, or it says \"or equivalent experience.\" The candidate's education line (completed coursework, no degree) does not create a screen-out.\nB == The JD says \"Bachelor's degree preferred\" or lists a degree but adds \"or equivalent combination of education and experience.\" The recruiter may see the candidate's partial coursework and 20-year track record as compensating, creating minor friction.\nC == The JD requires a Bachelor's degree without an experience waiver clause. The candidate's education line lacks a completed degree, so the recruiter is likely to flag the application as not meeting the basic requirement and may reject unless other factors are exceptional.\nD == The JD explicitly requires a specific degree (e.g., \"BS in Computer Science\") and lists it as a hard requirement. The candidate's resume shows no degree, making an automatic rejection highly probable.\nX == The JD's education language is missing or so ambiguous that a recruiter cannot apply a standard filter.", "importance": 8, "grade_descriptions": [{"grade": "A", "description": "The JD does not list a degree requirement, or it says \"or equivalent experience.\" The candidate's education line (completed coursework, no degree) does not create a screen-out."}, {"grade": "B", "description": "The JD says \"Bachelor's degree preferred\" or lists a degree but adds \"or equivalent combination of education and experience.\" The recruiter may see the candidate's partial coursework and 20-year track record as compensating, creating minor friction."}, {"grade": "C", "description": "The JD requires a Bachelor's degree without an experience waiver clause. The candidate's education line lacks a completed degree, so the recruiter is likely to flag the application as not meeting the basic requirement and may reject unless other factors are exceptional."}, {"grade": "D", "description": "The JD explicitly requires a specific degree (e.g., \"BS in Computer Science\") and lists it as a hard requirement. The candidate's resume shows no degree, making an automatic rejection highly probable."}, {"grade": "X", "description": "The JD's education language is missing or so ambiguous that a recruiter cannot apply a standard filter."}]}, {"label": "Technical Skills Match", "code": "TS", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == Every must-have technical skill listed in the JD (e.g., Jira, AWS, Python, API design) appears verbatim in the candidate's Technical Skills section or is clearly demonstrated in experience bullets. Recruiter can check the box confidently.\nB == Most required skills are present; one or two are not exact matches but the candidate lists close analogues (e.g., JD asks for \"GitLab CI/CD\" and resume shows \"GitHub Actions\"). A recruiter would likely consider it a sufficient match.\nC == Several important skills are missing from the candidate's resume, but there is adjacent experience that could transfer. The recruiter is left with a \"maybe\" and must rely on other elements.\nD == The JD lists critical, non-negotiable technical skills (e.g., specific programming languages, cloud services, or frameworks) that are completely absent from the resume. A recruiter scanning for keywords would not find them and would reject the application.\nX == The JD does not enumerate any technical skills or the list is too vague to compare.", "importance": 9, "grade_descriptions": [{"grade": "A", "description": "Every must-have technical skill listed in the JD (e.g., Jira, AWS, Python, API design) appears verbatim in the candidate's Technical Skills section or is clearly demonstrated in experience bullets. Recruiter can check the box confidently."}, {"grade": "B", "description": "Most required skills are present; one or two are not exact matches but the candidate lists close analogues (e.g., JD asks for \"GitLab CI/CD\" and resume shows \"GitHub Actions\"). A recruiter would likely consider it a sufficient match."}, {"grade": "C", "description": "Several important skills are missing from the candidate's resume, but there is adjacent experience that could transfer. The recruiter is left with a \"maybe\" and must rely on other elements."}, {"grade": "D", "description": "The JD lists critical, non-negotiable technical skills (e.g., specific programming languages, cloud services, or frameworks) that are completely absent from the resume. A recruiter scanning for keywords would not find them and would reject the application."}, {"grade": "X", "description": "The JD does not enumerate any technical skills or the list is too vague to compare."}]}, {"label": "Certification Match", "code": "CT", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD requires or prefers Certified ScrumMaster (CSM) or Certified Scrum Product Owner (CSPO), both of which the candidate holds (valid 2024\u20132026). No gap.\nB == The JD mentions \"Agile certification preferred\" without specifying; CSM/CSPO satisfy it. Or the JD requires no certification. Minor friction, if any.\nC == The JD asks for a certification the candidate does not have (e.g., PMP, SAFe Agilist, AWS Solutions Architect) but the JD does not mark it as mandatory, or the candidate's experience suggests competency. Recruiter might still consider.\nD == The JD states that a specific certification (not held by the candidate) is a hard requirement (e.g., \"PMP certification is mandatory\"). The resume shows no evidence of that credential, and a recruiter will screen out.\nX == The JD does not mention certifications or requirements are unclear.", "importance": 4, "grade_descriptions": [{"grade": "A", "description": "The JD requires or prefers Certified ScrumMaster (CSM) or Certified Scrum Product Owner (CSPO), both of which the candidate holds (valid 2024\u20132026). No gap."}, {"grade": "B", "description": "The JD mentions \"Agile certification preferred\" without specifying; CSM/CSPO satisfy it. Or the JD requires no certification. Minor friction, if any."}, {"grade": "C", "description": "The JD asks for a certification the candidate does not have (e.g., PMP, SAFe Agilist, AWS Solutions Architect) but the JD does not mark it as mandatory, or the candidate's experience suggests competency. Recruiter might still consider."}, {"grade": "D", "description": "The JD states that a specific certification (not held by the candidate) is a hard requirement (e.g., \"PMP certification is mandatory\"). The resume shows no evidence of that credential, and a recruiter will screen out."}, {"grade": "X", "description": "The JD does not mention certifications or requirements are unclear."}]}, {"label": "Location / Work Model Objection", "code": "LO", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD is fully remote (US or global) or specifically lists the San Francisco Bay Area as the location. The candidate's \"Oakland, CA (PST)\" raises no red flags.\nB == The JD is remote but requires working hours aligned with a US timezone. PST falls within that range, so no significant objection.\nC == The JD is hybrid with an office in the Bay Area (commutable from Oakland), but the candidate's resume does not explicitly state willingness to commute. A recruiter might wonder but would likely proceed.\nD == The JD is fully on-site in a city far from Oakland (e.g., New York, Chicago, London) or requires relocation, and the candidate's resume contains no indication she is willing to move. A recruiter would typically discard the application.\nX == The JD does not specify a work location or arrangement.", "importance": 10, "grade_descriptions": [{"grade": "A", "description": "The JD is fully remote (US or global) or specifically lists the San Francisco Bay Area as the location. The candidate's \"Oakland, CA (PST)\" raises no red flags."}, {"grade": "B", "description": "The JD is remote but requires working hours aligned with a US timezone. PST falls within that range, so no significant objection."}, {"grade": "C", "description": "The JD is hybrid with an office in the Bay Area (commutable from Oakland), but the candidate's resume does not explicitly state willingness to commute. A recruiter might wonder but would likely proceed."}, {"grade": "D", "description": "The JD is fully on-site in a city far from Oakland (e.g., New York, Chicago, London) or requires relocation, and the candidate's resume contains no indication she is willing to move. A recruiter would typically discard the application."}, {"grade": "X", "description": "The JD does not specify a work location or arrangement."}]}, {"label": "Recency of Relevant Experience", "code": "RR", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD emphasizes a domain or skill that the candidate has exercised in her most recent role (2022\u2013present), such as SaaS delivery, AI product management, or healthcare platforms (e.g., PTown.tech, Somerset Consulting projects). Recency is unquestionable.\nB == The JD seeks experience that appears in roles from 2018\u20132022 (e.g., medical device work at Green Mars, HIPAA compliance at EMIDS). The gap is small; a recruiter would still see the skills as fresh.\nC == The JD requires experience that the candidate held only in earlier roles (pre-2018, e.g., operational BI at Tellme/Microsoft) and has not demonstrated since. The recruiter might question whether the candidate is still current.\nD == The JD demands a skill or domain with a strict recency requirement (e.g., \"3+ years in AI product management within the last 2 years\") that the candidate's timeline does not support, even if they have older experience. Recruiter will view it as insufficient.\nX == The JD does not provide enough timeline context to evaluate recency.", "importance": 7, "grade_descriptions": [{"grade": "A", "description": "The JD emphasizes a domain or skill that the candidate has exercised in her most recent role (2022\u2013present), such as SaaS delivery, AI product management, or healthcare platforms (e.g., PTown.tech, Somerset Consulting projects). Recency is unquestionable."}, {"grade": "B", "description": "The JD seeks experience that appears in roles from 2018\u20132022 (e.g., medical device work at Green Mars, HIPAA compliance at EMIDS). The gap is small; a recruiter would still see the skills as fresh."}, {"grade": "C", "description": "The JD requires experience that the candidate held only in earlier roles (pre-2018, e.g., operational BI at Tellme/Microsoft) and has not demonstrated since. The recruiter might question whether the candidate is still current."}, {"grade": "D", "description": "The JD demands a skill or domain with a strict recency requirement (e.g., \"3+ years in AI product management within the last 2 years\") that the candidate's timeline does not support, even if they have older experience. Recruiter will view it as insufficient."}, {"grade": "X", "description": "The JD does not provide enough timeline context to evaluate recency."}]}, {"label": "Role Level / Seniority", "code": "RL", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD targets a Senior, Lead, Principal, or Staff-level product/program manager. The candidate's headline \"Senior Technical PM,\" recent \"Principal TPM\" title, and scope of managing up to 40-person teams align perfectly.\nB == The JD is for a Manager or Lead role with hands-on expectations; the candidate's mix of strategy and execution is a good fit.\nC == The JD is for a Director or VP level role, and the candidate's titles (TPM, PO, Consultant) do not immediately convey strategic leadership on that scale. The recruiter would need to dig into the consulting engagements to see if the scope matches.\nD == The JD is for an entry-level or very junior role where 20+ years of experience would be seen as overqualified and a flight risk; a recruiter would likely screen out. Also a D if the JD is for a C-suite or SVP role that the candidate's career history does not approach.\nX == The JD does not specify the seniority level or the level is too ambiguous to judge.", "importance": 8, "grade_descriptions": [{"grade": "A", "description": "The JD targets a Senior, Lead, Principal, or Staff-level product/program manager. The candidate's headline \"Senior Technical PM,\" recent \"Principal TPM\" title, and scope of managing up to 40-person teams align perfectly."}, {"grade": "B", "description": "The JD is for a Manager or Lead role with hands-on expectations; the candidate's mix of strategy and execution is a good fit."}, {"grade": "C", "description": "The JD is for a Director or VP level role, and the candidate's titles (TPM, PO, Consultant) do not immediately convey strategic leadership on that scale. The recruiter would need to dig into the consulting engagements to see if the scope matches."}, {"grade": "D", "description": "The JD is for an entry-level or very junior role where 20+ years of experience would be seen as overqualified and a flight risk; a recruiter would likely screen out. Also a D if the JD is for a C-suite or SVP role that the candidate's career history does not approach."}, {"grade": "X", "description": "The JD does not specify the seniority level or the level is too ambiguous to judge."}]}, {"label": "Employment Type Framing", "code": "ET", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD explicitly seeks a fractional, contract, or principal consultant. The candidate's 14-year freelance practice is a direct match and a strength.\nB == The JD is for a startup or small company that values autonomy and versatility; the candidate's consulting background is likely viewed as an asset, not a liability.\nC == The JD is for a traditional full-time role at an established company. The recruiter notes the candidate's long stretch of independent consulting and may question cultural fit or commitment, but will consider if the skills align.\nD == The JD is from a large, bureaucratic enterprise that signals a strong preference for career track records at similarly large companies (e.g., \"must have experience in Fortune 500 environments\"). The candidate's consultant-heavy resume will likely be filtered out.\nX == The JD gives no indication of employment type expectations.", "importance": 6, "grade_descriptions": [{"grade": "A", "description": "The JD explicitly seeks a fractional, contract, or principal consultant. The candidate's 14-year freelance practice is a direct match and a strength."}, {"grade": "B", "description": "The JD is for a startup or small company that values autonomy and versatility; the candidate's consulting background is likely viewed as an asset, not a liability."}, {"grade": "C", "description": "The JD is for a traditional full-time role at an established company. The recruiter notes the candidate's long stretch of independent consulting and may question cultural fit or commitment, but will consider if the skills align."}, {"grade": "D", "description": "The JD is from a large, bureaucratic enterprise that signals a strong preference for career track records at similarly large companies (e.g., \"must have experience in Fortune 500 environments\"). The candidate's consultant-heavy resume will likely be filtered out."}, {"grade": "X", "description": "The JD gives no indication of employment type expectations."}]}, {"label": "AI / Technology Specialty", "code": "AS", "content": "POV: Recruiter holding only this JD and her resume, deciding whether the application stays in the pile.\nA == The JD explicitly asks for AI product management, AI tooling, or AI-assisted development experience. The candidate's resume details building AI recruiting pipelines, multi-agent workflows, and prompt engineering, providing a clear, recent match.\nB == The JD mentions AI/ML as a nice-to-have or part of the tech stack; the candidate's AI work is sufficient to check that box and may differentiate her.\nC == The JD does not mention AI, so the candidate's AI experience is neutral. Recruiter won't penalize or reward heavily.\nD == The JD requires deep technical AI/ML expertise (e.g., \"must have built and deployed machine learning models,\" \"PhD in ML\") that the candidate's resume does not evidence. Her AI experience reads as tool utilization and orchestration, not model development, and a recruiter would screen out.\nX == The JD does not reference AI at all.", "importance": 4, "grade_descriptions": [{"grade": "A", "description": "The JD explicitly asks for AI product management, AI tooling, or AI-assisted development experience. The candidate's resume details building AI recruiting pipelines, multi-agent workflows, and prompt engineering, providing a clear, recent match."}, {"grade": "B", "description": "The JD mentions AI/ML as a nice-to-have or part of the tech stack; the candidate's AI work is sufficient to check that box and may differentiate her."}, {"grade": "C", "description": "The JD does not mention AI, so the candidate's AI experience is neutral. Recruiter won't penalize or reward heavily."}, {"grade": "D", "description": "The JD requires deep technical AI/ML expertise (e.g., \"must have built and deployed machine learning models,\" \"PhD in ML\") that the candidate's resume does not evidence. Her AI experience reads as tool utilization and orchestration, not model development, and a recruiter would screen out."}, {"grade": "X", "description": "The JD does not reference AI at all."}]}]}
[2026-08-07 20:22:47] INFO src.core.agent: run_next chain entry: task=craft_get_rubric batch_id=craft_get_rubric-f43cf82e-5b49-4d0e-99ba-c86fc38e5e59
[2026-08-07 20:22:47] DEBUG src.core.agent: do_task index 1/1 somerset -> task start
[2026-08-07 20:22:47] DEBUG src.core.agent:  | task_key=craft_get_rubric batch_id=craft_get_rubric-f43cf82e-5b49-4d0e-99ba-c86fc38e5e59 index=somerset in_run_next_chain=True
[2026-08-07 20:22:47] DEBUG src.core.agent: do_task.candidate_token_view index 1/1 somerset -> success — name tokens
[2026-08-07 20:22:47] DEBUG src.core.agent:  | found first=nonempty last=nonempty full=nonempty branch=load_by_id
[2026-08-07 20:22:47] DEBUG src.core.agent:  | recorded FIRST_NAME='Susan' LAST_NAME='Somerset' FULL_NAME='Susan Somerset'
[2026-08-07 20:22:47] INFO src.core.agent: [DEBUG] do_task('craft_get_rubric'): brain_setting=Big provider=deepseek model=deepseek-v4-pro max_tokens=32000 temp=0.3 skip_cache=False candidate=somerset
[2026-08-07 20:22:47] DEBUG src.core.agent:  | llm_params provider=deepseek brain_setting=Big model=deepseek-v4-pro max_tokens=32000 temp=0.3 skip_cache=False candidate_id=somerset
[2026-08-07 20:22:47] DEBUG src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
```

run_next for craft_do_rubric did not run.

#### chuckles — 2026-08-07T04:11:27.801Z
@susan

1. **REQUESTED_RESUME + craft_get_rubric:** Both states choosable for a `craft_get_rubric` dispatch task, or only `REQUESTED_ARTIFACTS` binds now (resume craft deferred; state remains)?
2. **First-time Generate:** Also enter `REQUESTED_ARTIFACTS` / full chain (retire per-artifact ad-hoc generate), or only **Regenerate** kicks the chain?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._

---

## Bug: AST-1434 — REQUESTED_ARTIFACTS daisy chain

Delta only. Original AST-1243 Purpose / Functional scope / AC1–AC9 / Boundaries still stand; this section does not re-plan them. Mini-parent is AST-1426 (fresh `ftr` off `origin/dev`, not a resurrection of AST-1243).

### As-is

`REQUESTED_ARTIFACTS` is supposed to walk the live `agent_task.run_next` craft-rubric chain with per-hop persist. In the pasted 2026-08-18 run the hop that executed was `craft_joblist_rubric` (`in_run_next_chain=True`). The LLM returned a valid `joblist_rubric` payload, then `persist_candidate_craft_hops` rejected vector **Onsite Requirement** because grade letters were inline on one physical line (`A == … B == …`) instead of one `A =` / `B:` / `C ==` line each. Persist raised, `do_task` returned failure before `_write_dispatch_hop_label_on_success`, `chain_hop_failed`, so later hops — including `craft_jobdesc_rubric` — never run.

Chain participation is still not “`run_next` is set, period.” `src/core/consult.py` candidate branch only calls `run_requested_artifacts_dispatch` when `dispatch_task.task_key == CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]` (`craft_get_rubric`); any other candidate `task_key` with live `run_next` (including a mid-hop `craft_joblist_rubric` row) logs `unhandled candidate task_key` and returns zeros. Dispatcher mid-chain reclaim (`requested_artifacts_dispatch_claim_states`) is gated on that same entry-hop equality. `run_requested_artifacts_dispatch` always starts at the stage entry hop and hardcodes `dispatch_trigger_state` from `CANDIDATE_STAGE_DISPATCH`, not from the `dispatch_task` row.

A mid-hop one-off has no `dispatch_task` skip-daisy-chain toggle. UI generate already sets `ctx["suppress_run_next"]=True`; that flag is not wired from a dispatch row. Hop output is not `<dispatch_task.trigger_state>.<completed_task_key>` as a row-driven contract: candidate hop labels require `persist_candidate_craft_hops` plus `trigger_state == REQUESTED_ARTIFACTS`, and persist failure short-circuits the write.

### To-be

Daisy chain is entirely database-driven. If an `agent_task` has `run_next` set, that is the only participation signal — no leftover code/config membership list on this path. A regular `dispatch_task` that starts on a `task_key` with `run_next` uses the daisy-chain path (persist each hop, follow `run_next`, write hop labels). A `skip_daisy_chain` toggle on the `dispatch_task` itself covers a one-off mid-hop (do not walk the rest; do not graduate the stage). The output state of the daisy chain (current and future) is `<dispatch_task.trigger_state>.<completed_task_key>` (bare trigger prefix if the row’s `trigger_state` is already a hop label). `craft_joblist_rubric` / `craft_jobdesc_rubric` persist the pasted inline `A ==` form and the live `REQUESTED_ARTIFACTS` walk continues.

### Repro

Fixture is the pasted `craft_joblist_rubric` `agent_payload` (candidate `somerset`), not a SQL seed. One criterion is enough to fail persist today:

```json
{
  "agent_performance": {"status": "success", "failure_note": ""},
  "agent_payload": {
    "criteria": [
      {
        "label": "Onsite Requirement",
        "code": "OR",
        "importance": 10,
        "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == location field states Remote, Fully Remote, or Work From Home. B == location field states a Bay Area city (San Francisco, Oakland, Berkeley, Walnut Creek, Alameda) with no onsite requirement stated. C == location field states Hybrid with a Bay Area city. D == location field states Hybrid with a non-Bay Area city. F == location field states On-Site, Onsite, In-Office, or In-Person. X == location field is absent or blank."
      }
    ]
  }
}
```

Steps that must all pass after the fix:

1. `ensure_criterion_grade_table` / `normalize_rubric_artifacts_on_save` on that `joblist_rubric` criterion succeeds (inline `A ==` … `X ==` on one physical line). Newline form (`A == …\nB == …`) still succeeds.
2. Candidate in `REQUESTED_ARTIFACTS`; dispatch row `task_key=craft_get_rubric`, `trigger_state=REQUESTED_ARTIFACTS`, `skip_daisy_chain` unset/false. Chain walks live `run_next` through `craft_joblist_rubric` and `craft_jobdesc_rubric` (and the rest). Each successful hop persists via `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` and writes candidate.state `REQUESTED_ARTIFACTS.<completed_task_key>`. Terminal hop with empty `run_next` graduates to `ARTIFACTS_READY`.
3. Dispatch row whose `task_key` is a mid-chain hop with live `run_next` (e.g. `craft_joblist_rubric`) and `trigger_state=REQUESTED_ARTIFACTS`, `skip_daisy_chain` unset/false: consult uses the daisy-chain worker starting at that `task_key` (not `unhandled`); persist + succession continue from there.
4. Same mid-hop row with `skip_daisy_chain=true`: that hop persists (and hop-label writes); `run_next` is not followed; candidate is **not** force-graduated to `ARTIFACTS_READY`.

### Root cause

Three defects, one chain-stop:

1. **Persist parser is newline-only.** `src/utils/rubric_text.py` `parse_trailing_grade_table_lines` splits on `\n` and requires two trailing `_GRADE_LINE` matches. `coerce_embedded_newline_escapes` only expands literal `\n` when there are fewer than two real newlines — it does not split inline `A == … B == …` on one physical line. `_persist_craft_dispatch_success` → `normalize_rubric_artifacts_on_save` raises; `do_task` returns before hop-label write and before `run_next` recurse.
2. **Consult still membership-gates the daisy-chain worker** on `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]` (`craft_get_rubric`). Live `agent_task.run_next` is not the participation signal. Dispatcher reclaim of `REQUESTED_ARTIFACTS.<hop>` labels is gated the same way.
3. **No dispatch-row skip-daisy-chain; hop prefix is stage-hardcoded.** `suppress_run_next` exists only as a `do_task` ctx flag (UI generate). Candidate hop labels require `trigger_state == REQUESTED_ARTIFACTS` from `CANDIDATE_STAGE_DISPATCH`, not the dispatch row. `run_requested_artifacts_dispatch` always starts at the stage entry hop and, on `do_task` success, always `transition_candidate_state(..., pass_state)` — a one-off mid-hop would wrongly graduate if we only set `suppress_run_next` without changing that.

Not the root: `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` (persist routing, not hop order). `_walk_requested_artifacts_chain_task_keys` already walks live `run_next` (UI labels / claim expansion). Do not revive AST-1109 `config.py` hop-membership frozensets.

### Proposed change

**1. Accept inline grade letters in persist (unstick the pasted hop). Do not change `agent_task` prompt copy (AST-1243 Boundaries).**

In `src/utils/rubric_text.py` `parse_trailing_grade_table_lines` (used by `ensure_criterion_grade_table`): keep the existing trailing-newline parse. When that yields fewer than two grade lines, parse the last physical line (or whole content if it is one line) for inline grade tokens `[ABCDEFX]` + `==` / `=` / `:` and split into one row per token so `A == … B == …` on one line is accepted. Require at least two grades; same `ValueError` text if still short. After a successful inline split, rewrite `item["content"]` in `ensure_criterion_grade_table` to the canonical newline form (`A == desc\nB == desc`) so stored rubric_vector rows stay one-grade-letter-per-line for consult. Newline tables and `\\n` escapes keep working. This path is shared with Artifacts Save — intentional: the same payload must persist from dispatch and from UI save.

**2. Daisy-chain participation = live `run_next`, from the dispatch row’s `task_key`.**

In `src/core/consult.py` candidate branch: stop gating on `tk == CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]`. If `_current_agent_task_run_next(tk)` is non-empty (or this is already a chain child — not needed at consult entry) **and** `skip_daisy_chain` is false, call the candidate craft daisy-chain worker for **that** `tk`. If `skip_daisy_chain` is true and `tk` maps through `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` (or the existing `_persist_craft_dispatch_success` special cases), still run the worker for the single hop. Other candidate keys stay unhandled.

Generalize `run_requested_artifacts_dispatch` in `src/core/candidate.py` to take the dispatch row’s `task_key`, `trigger_state`, and `skip_daisy_chain` (consult passes them; existing entry-hop caller may keep defaults from `CANDIDATE_STAGE_DISPATCH`). Start `do_task` at that `task_key`, not always `craft_get_rubric`. Set `ctx["persist_candidate_craft_hops"]=True`, `ctx["dispatch_trigger_state"]` to the **bare** trigger (`parse_dispatch_hop_label(row.trigger_state)[0]` if the row trigger is already a hop label, else `row.trigger_state`), and `ctx["suppress_run_next"]=True` iff `skip_daisy_chain`.

On `do_task` success: if `skip_daisy_chain`, do **not** `transition_candidate_state` to `pass_state` (`ARTIFACTS_READY`); leave the hop label. If not skip and `dispatch_trigger_state` is the REQUESTED_ARTIFACTS stage trigger, graduate to `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["pass_state"]` as today. Failure paths keep `_requested_stage_failure_target` / AST-1388 leave-last-hop-label behavior.

Keep `CANDIDATE_STAGE_DISPATCH` as stage trigger / pass_state / entry-hop **for Generate/Regenerate and claim defaults**. It is not a hop-membership list. Do not add `craft_joblist_rubric` (or any hop) as a second consult `if tk ==` special case.

**3. `skip_daisy_chain` on `dispatch_task` (mirror `skip_cache`).**

- `src/data/database.py`: INTEGER NOT NULL DEFAULT 0 column; add to `_ensure_dispatch_task_schema` `_migrate_cols`, `_DISPATCH_TASK_UPDATE_COLS`, `_DISPATCH_TASK_TEMPLATE_COPY_COLS`, and the bool-int coercion branch next to `skip_cache`. Default 0 on insert (`save_dispatch_task` need not take it — update/PUT sets it, same as `skip_cache` today).
- `src/ui/api/api_admin.py`: add `skip_daisy_chain` to the PUT `allowed` set and the int-bool branch; POST may omit (default 0).
- `src/ui/frontend/src/pages/AdminScheduledActions.tsx`: checkbox on create/edit next to Debug; include in PUT/POST body; `DispatchTask` / form types.
- `src/core/dispatcher.py` `_dispatch_one`: if `task.get("skip_daisy_chain")`, set `ctx["suppress_run_next"]=True` (same pattern as `skip_cache` → `ctx["skip_cache"]`). Consult still passes the flag into the worker so graduation is skipped even if ctx were omitted.

UI generate (`run_candidate_artifact_generation`) keeps `suppress_run_next=True` independently. Do not replace that path with the dispatch column.

**4. Hop output = `<dispatch_task.trigger_state>.<completed_task_key>`.**

`dispatch_hop_label` already formats `{ts}.{tk}`. Changes:

- `run_requested_artifacts_dispatch` (generalized) sets `dispatch_trigger_state` from the dispatch row as in (2), not hardcoded `CANDIDATE_STAGE_DISPATCH["trigger_state"]`.
- `_should_write_candidate_craft_hop_label`: drop the `trigger_state == stage_trigger` equality. Keep `entity_type == "candidate"`, non-empty index/trigger, and `persist_candidate_craft_hops`. Any candidate daisy-chain with persist writes `write_candidate_dispatch_hop_label(index, trigger_state, task_key)`.
- Persist still runs **before** the hop-label write (today’s order). After (1), persist succeeds so the write is reached.
- Dispatcher candidate claim: when `input_state` is `REQUESTED_ARTIFACTS` (or a hop label whose trigger is that stage), expand claim states via `requested_artifacts_dispatch_claim_states()` **without** requiring `dispatch_task_key == craft_get_rubric`. Mid-hop rows can reclaim `REQUESTED_ARTIFACTS.<parent>` / bare trigger the same way job `dispatch_chain_claim_states_for_row` does.

Job `BUILD_ARTIFACTS` hop labels stay on the existing consult job path (`dispatch_trigger_state` already from the row). Do not change job graduation maps.

**5. Persist mapping unchanged.** `_persist_craft_dispatch_success` keeps `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` (and `craft_company_search_terms` / `craft_resume_base` special cases). That map routes hop → artifact field; it is not chain succession. `craft_jobdesc_rubric` QC/GC merge (`_merge_embedded_evaluate_jd_criteria`) stays.

### Blast radius

- `src/utils/rubric_text.py` — shared by dispatch persist, Artifacts Save, consult hydrate. Inline parse must not break existing newline tables or raise on legitimate two-line suffixes.
- `src/core/consult.py` candidate branch — every candidate `dispatch_task` with `run_next` now hits the daisy-chain worker; unhandled warning must remain for keys that are neither run_next-chain nor skip-one-off craft persist.
- `src/core/candidate.py` `run_requested_artifacts_dispatch` — start hop, trigger, skip, graduation. `requested_artifacts_dispatch_claim_states` / dispatcher reclaim. Generate/Regenerate still enter via `start_requested_artifacts` + entry hop `craft_get_rubric` (AST-1253).
- `src/core/agent.py` hop-label gate and persist-then-label order. `suppress_run_next` already used by UI generate and `select_job_page` special cases — skip-daisy-chain must not change those.
- `src/data/database.py` + Admin Scheduled Actions — new column; template copy; PUT whitelist.
- Tests (Betty owns `tests/`): `test_candidate.py` (requested-artifacts dispatch, `suppress_run_next` on UI generate), `test_agent.py` (hop labels, persist), `test_dispatcher.py` (claim states, skip_cache ctx copy), `test_api_admin.py` (PUT allowed), rubric_text component tests if present. Do not patch `tests/` on this ticket.
- Job `BUILD_ARTIFACTS` / `DISPATCH_CHAIN_TERMINAL_GRADUATION` — out of product scope except hop-label format already matches; do not retune job maps.
- Resume daisy-chain (`craft_resume_base` / `REQUESTED_RESUME` generation) stays out of scope (AST-1243 Boundaries).

### What must still hold

- AST-1243 AC5: execution history shows the daisy chain hop-by-hop comparably to `BUILD_ARTIFACTS`.
- AST-1243 AC6: on success, `ARTIFACTS_READY` and each chain rubric visible/editable under Artifacts nav.
- AST-1243 AC7: failure paths land on retry/error companions without silent stuck mid-chain (persist still raises on truly unparseable grade text; hop-label left in place per AST-1388 when already on a compound label).
- AST-1243 AC8: no craft-rubric hop sequencing list in `config.py`; succession remains `agent_task.run_next`; per-hop persist matches `BUILD_ARTIFACTS` posture. `CANDIDATE_STAGE_DISPATCH` stays stage wiring, not a hop set.
- `astral.dispatch.run-next-is-chain-authority` — `run_next` is succession authority; do not add a parallel membership frozenset or a second `if tk == "craft_joblist_rubric"` consult gate.
- `astral.state.no-daisy-chain-in-run` — only the documented `run_next` carve-out (§2.6.0); skip-daisy-chain is the one-off off-switch, not a second pipeline.
- `REQUESTED_RESUME` / `REQUESTED_ARTIFACTS` remain selectable for `craft_get_rubric` with no new trigger-state validation (AC2).
- Per-artifact UI generate for live chain keys stays 409 → `generate_artifacts` (AST-1253).
- Wrapper task keys `candidate_requested_artifacts` / `candidate_requested_resume` stay retired (AC1).
- Backend `debug=True` per-hop found/recorded (AC9) on touched persist/succession paths.

## Joan board (AST-1434)

[board-joan] CANON: OK — proposed change aligns with `astral.dispatch.run-next-is-chain-authority` / `astral.state.no-daisy-chain-in-run`; `skip_daisy_chain` is inside the §2.6.0 carve-out; inline `A ==` parsing is not a statute gap. No ESCALATE.

## Radia review (AST-1434)

[code-rubric] Overall CLEAN · PROCEED. Diff `origin/ftr/AST-1426-craft-jobdesc-rubric-requested-artifacts...origin/sub/AST-1426/AST-1434-fix-requested-artifacts-daisy-chain` @ `1fd85ad1`. No fix-now. Discuss: stale TestAst972 until AST-1437. Advisory: error text; terminal hop without skip unhandled.

