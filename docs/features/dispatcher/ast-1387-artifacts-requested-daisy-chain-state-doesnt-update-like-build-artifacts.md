# AST-1387 — ARTIFACTS_REQUESTED daisy chain state doesn't update like BUILD_ARTIFACTS

<!-- linear-archive: AST-1387 archived 2026-08-31 -->

## Linear archive (AST-1387)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1387/artifacts-requested-daisy-chain-state-doesnt-update-like-build  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

When a candidate is in `REQUESTED_ARTIFACTS` (Susan’s note: ARTIFACTS_REQUESTED) and dispatch runs the craft daisy chain from `craft_get_rubric` onward, hop success does not leave the candidate on a compound progress label the way jobs do on `BUILD_ARTIFACTS`. Progress is not recorded as `<TRIGGER_STATE>.<last_completed_task_in_chain>` on the entity state, so mid-chain position is not visible the same way as the job artifact chain.

## To-be

Whenever a daisy chain is indicated via `run_next`, after each successful hop the entity state is `<TRIGGER_STATE>.<last_completed_task_in_chain>` — including the `REQUESTED_ARTIFACTS` / craft chain from `craft_get_rubric` onward — matching the behavior already working for `BUILD_ARTIFACTS`.

## Proposed steps

1. Confirm where `_write_dispatch_hop_label_on_success` / `_should_write_dispatch_hop_label` gates on `entity_type == "job"` and what candidate-path equivalent (if any) exists after AST-1252.
2. Extend hop-label writes so `REQUESTED_ARTIFACTS` + craft `run_next` hops stamp `REQUESTED_ARTIFACTS.<completed_task_key>` (or the live trigger) after each success, without breaking terminal graduation to `ARTIFACTS_READY`.
3. Verify mid-chain failure leaves the last successful compound label; redispatch / UI can see progress without reading execution history alone.
4. Regression-check job `BUILD_ARTIFACTS` hop labels and AST-1264 succession still green.

## Original brief

When a daisy chain is indicated with a run next, the state of the job should be <TRIGGER_STATE>.<last_completed_task_in_chain>.

This works great for BUILD_ARTIFACTS, but it does not work with ARTIFACTS_REQUESTED (from craft_get_rubric onward).

### Comments

#### susan — 2026-08-15T02:18:01.018Z
1252

#### chuckles — 2026-08-15T02:15:10.175Z
Ancestor candidates (ranked — pick one, ask about one, or reject all):

1. **AST-1252** (`docs/features/candidate/ast-1252-artifacts-dispatch-chain-persistence-and-retire-wrappers.md`) — owns `REQUESTED_ARTIFACTS` dispatch chain + craft hop persist; plan explicitly keeps `_should_write_dispatch_hop_label` job-only (no candidate hop labels). Strongest gap match.
2. **AST-1243** — parent epic “Candidate Artifacts now daisy chain”; AC expects hop-by-hop progress comparable to `BUILD_ARTIFACTS`.
3. **AST-847** (`docs/features/consult/ast-847-unify-build-artifacts-chain-in-do-task-per-hop-state-terminal-graduation.md`) — established the generic `<trigger_state>.<completed_task_key>` DB hop-label pattern (canonical UAT was `BUILD_ARTIFACTS`).
4. **AST-1264** (`docs/features/candidate/ast-1264-uat-craft-get-run-next.md`) — UAT succession fix for `craft_get_rubric` → rest of chain under `REQUESTED_ARTIFACTS`; adjacent but focused on run_next continuing, not compound state labels.
5. **AST-597** / **AST-595** — original compound `BUILD_ARTIFACTS.<task_key>` hop-state work (later superseded by AST-847 runtime labels); weaker fit for the candidate/REQUESTED path.

---

_Implementation detail may live in git history on `origin/dev`._
