# AST-1388 — fix: REQUESTED_ARTIFACTS daisy-chain hop state labels

<!-- linear-archive: AST-1388 archived 2026-08-31 -->

## Linear archive (AST-1388)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1388/fix-requested-artifacts-daisy-chain-hop-state-labels  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1387 — ARTIFACTS_REQUESTED daisy chain state doesn't update like BUILD_ARTIFACTS  
**Blocked by / blocks / related:** parent: AST-1387

### Description

## Purpose

Implement the hop-label parity fix for REQUESTED_ARTIFACTS (candidate craft daisy chain) so mid-chain state matches BUILD_ARTIFACTS.

## Context

Parent bug AST-1387 (approved ancestor AST-1252). See parent Description ## As-is / ## To-be / ## Proposed steps.

## Ancestor

docs/features/candidate/ast-1252-artifacts-dispatch-chain-persistence-and-retire-wrappers.md — plan kept `_should_write_dispatch_hop_label` job-only; this fix extends compound `<TRIGGER>.<hop>` progress to the candidate REQUESTED_ARTIFACTS chain.

## Proposed change

- [X] `run_requested_artifacts_dispatch` sets `dispatch_trigger_state` (no graduate_on_terminal)
- [X] `write_candidate_dispatch_hop_label` mirrors job hop writer (bypass CANDIDATE_STATES)
- [X] Parallel candidate-craft success gate in `agent.py` (job `_should_write_dispatch_hop_label` unchanged)
- [X] `_candidate_state_allowed` accepts hop labels whose trigger is in prior_states
- [X] Mid-chain failure leaves last compound hop label; bare-trigger failure still → retry/error
- [X] Claim carve-out + dispatcher expand for REQUESTED_ARTIFACTS hop labels; UI inflight hide includes live-chain hop labels
- [X] No `REQUESTED_ARTIFACTS` in `DISPATCH_CHAIN_TERMINAL_GRADUATION`

### Comments

#### radia — 2026-08-15T02:32:53.884Z
[code-rubric] PROCEED (Commit: 42b61351) hop labels clean

#### joan — 2026-08-15T02:24:38.154Z
[board-joan]  CANON: OK

context_tokens≈42000

#### betty — 2026-08-15T02:23:57.045Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/candidate.md — missing coverage — no bible-backed node asserts REQUESTED_ARTIFACTS.<hop> after craft hop success or mid-chain leave-label (AST-1252 persist/job hop tests only)

#### ada — 2026-08-15T02:22:49.917Z
`origin/sub/AST-1387/AST-1388-requested-artifacts-hop-labels` @ `cc078920` · hop-label plan patched

---

_Implementation detail may live in git history on `origin/dev`._
