# AST-1389 — gap: REQUESTED_ARTIFACTS hop-label test coverage

<!-- linear-archive: AST-1389 archived 2026-08-31 -->

## Linear archive (AST-1389)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1389/gap-requested-artifacts-hop-label-test-coverage  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1387 — ARTIFACTS_REQUESTED daisy chain state doesn't update like BUILD_ARTIFACTS  
**Blocked by / blocks / related:** parent: AST-1387

### Description

## Purpose

Test/bible gap sibling for AST-1388 — Betty [board-betty] TESTS: REVISE.

## What

docs/test-bible/core/candidate.md — missing coverage — no bible-backed node asserts REQUESTED_ARTIFACTS.<hop> after craft hop success or mid-chain leave-label (AST-1252 persist/job hop tests only).

## Sibling

AST-1388 owns the product hop-label fix. This gap owns the repro/coverage bar Betty flagged.

## QA test manifest

1. Hop success write (bug-repro): `tests/component/core/test_agent.py::TestAst1389RequestedArtifactsHopLabels::test_craft_hop_success_writes_requested_artifacts_hop_label`
2. Mid-chain leave-label (bug-repro): `tests/component/core/test_candidate.py::TestAst1389RequestedArtifactsHopLabels::test_mid_chain_failure_leaves_hop_label`

Narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1389RequestedArtifactsHopLabels \
  tests/component/core/test_candidate.py::TestAst1389RequestedArtifactsHopLabels \
  -q
```

Bible: `docs/test-bible/core/candidate.md` @ `c4ad98b8195dab291b4a688ce3f36d8ce0c56f70` (on `origin/sub/AST-1387/AST-1389-requested-artifacts-hop-label-tests`).

Pre-fix: both nodes red (job-only hop-label gate; failure wipes to REQUESTED_ARTIFACTS_ERROR). Green awaits AST-1388 make-fix.

### Comments

#### radia — 2026-08-15T02:34:18.037Z
[code-rubric] PROCEED (Commit: 42b61351) hop repro tests clean

#### betty — 2026-08-15T02:28:29.632Z
[bug-repro]
`origin/sub/AST-1387/AST-1389-requested-artifacts-hop-label-tests` @ `668d2dcb` · repro lands red, awaits fix

---

_Implementation detail may live in git history on `origin/dev`._
