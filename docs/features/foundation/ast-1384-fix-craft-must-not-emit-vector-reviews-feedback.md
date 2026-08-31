# AST-1384 — fix: craft_* must not emit vector_reviews feedback

<!-- linear-archive: AST-1384 archived 2026-08-31 -->

## Linear archive (AST-1384)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1384/fix-craft-must-not-emit-vector-reviews-feedback  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** betty  
**Priority / estimate:** None / 3  
**Parent:** AST-1378 — feedback rubric returned on a craft prompt  
**Blocked by / blocks / related:** parent: AST-1378

### Description

## What this implements

Stop `craft_*` rubric tasks from emitting (and capturing) feedback-style `agent_performance.vector_reviews` on the rubric they just authored. Craft returns criteria only; compact feedback codes stay on grade/evaluate consumers.

## Citations

From parent AST-1378 / ancestor AST-724 contract split: craft vs grade envelope for `vector_reviews`.

## Acceptance criteria

- [X] A successful `craft_get_rubric` (and peer `craft_*_rubric`) response has complete `agent_payload.criteria` and does **not** include rubric-feedback `vector_reviews` compact codes.
- [X] Grade/evaluate rubric-backed tasks still request and capture per-vector feedback as today.
- [X] Craft SUCCESS does not persist craft-run rows as vector feedback for the newly authored rubric (capture no-ops or is excluded for `craft_*`).
- [ ] Re-run on candidate `abrams` Get craft confirms criteria without feedback reviews.

## Proposed change (make-fix)

- [X] `is_vector_feedback_task` in `config.py` — consumers only; craft keys in `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` return False.
- [X] `do_task` prompt suffix / envelope normalize / snapshot gated on `is_vector_feedback_task` (not `is_rubric_backed_task`).
- [X] `is_rubric_backed_task` / `rubric_owner_task_key` / `task_keys_for_rubric_owner` left unchanged.

## Boundaries

* Does **not** raise craft `max_tokens` / truncation budget (explicitly out — Susan).
* Does **not** redesign Admin Vector Feedback UI.
* Does **not** change letter-grade scoring math.

## Notes for planning

Ancestor context: archived AST-724 (`docs/features/auditor/ast-724-runtime-vector-feedback-capture.md`) intentionally included craft in the twelve rubric-backed keys. This fix reverses that for craft only. Parent Description has As-is / To-be / Proposed steps + evidence. Sibling gap AST-1385 owns Betty TESTS REVISE (no qa-fix / no [bug-repro] on this child).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1378-no-feedback-reviews-on-craft`, child `sub/AST-1378/AST-1384-fix-craft-no-vector-reviews`.

### Comments

#### radia — 2026-08-15T01:01:12.215Z
[code-rubric] PROCEED (Commit: b9048765) craft feedback gates split

Clean review — 0 violates. `is_vector_feedback_task` + three agent.py gates match plan. `[bug-repro]` N/A (gap AST-1385). ## What must still hold OK. → Review Posted → User Testing (§3h shortcut).

#### betty — 2026-08-15T00:57:32.170Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md § AST-724 — missing coverage — no is_vector_feedback_task / craft exclusion (repro craft_* still taught/captured under is_rubric_backed_task)

#### joan — 2026-08-15T00:57:30.453Z
[board-joan]  CANON: OK

context_tokens≈8500

#### ada — 2026-08-15T00:56:34.013Z
`origin/sub/AST-1378/AST-1384-fix-craft-no-vector-reviews` @ `0a2d7b06731cca9e3e0f66749bf42ce48ee1ed6d` · craft/grade feedback split

---

_Implementation detail may live in git history on `origin/dev`._
