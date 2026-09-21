# AST-1380 — Fix craft_get_rubric RESPONSE truncation (289-token cut)

<!-- linear-archive: AST-1380 archived 2026-08-31 -->

## Linear archive (AST-1380)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1380/fix-craft-get-rubric-response-truncation-289-token-cut  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1379 — Response truncated after 289 tokens?  
**Blocked by / blocks / related:** parent: AST-1379

### Description

## What this implements

Restore complete `craft_get_rubric` JSON output (or hard-fail on truncation) so a RESPONSE cannot land as success with a mid-criteria cut after ~289 tokens. Confirm whether AST-903's `CRAFT_RUBRIC_MAX_TOKENS` floor / provider `max_tokens` hard-fail still applies on this entry path; fix the hole if the floor is skipped or undercut.

## Acceptance criteria

- [X] A `craft_get_rubric` hop that would otherwise truncate mid-`criteria[].content` either completes with full parseable JSON or fails under the existing `max_tokens` / unusable-response failure class — never `agent_performance.status=success` with partial payload.
- [X] The path that produced batch `craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948` for candidate `abrams` (RESPONSE `token_size: 289`) applies the craft-rubric token floor (or equivalent budget) so a full criteria array can be written.
- [X] Re-run (or equivalent fixture) shows a complete criteria array persisted, not a mid-grade-row cut.

## Proposed change (make-fix)

- [X] Confirm hop / hole: AST-903 floor + max_tokens hard-fail still present; abrams signature matches thinking-budget starvation (Atlas Big) + success-shaped failure RESPONSE.
- [X] Decision A: force DeepSeek `thinking=False` for `CRAFT_RUBRIC_UI_TASK_KEYS` in `do_task` (shared max_tokens with JSON answer).
- [X] Prefix provider-failure RESPONSE audit bodies (`Provider failed …`) so raw `agent_performance.status=success` envelopes are not mistaken for finished hops.
- [X] AST-903 floor + provider JSON max_tokens hard-fail left intact; generate/REQUESTED_ARTIFACTS still fail closed on `success=False`.

## Boundaries

* Does not redesign GET rubric grading semantics or craft prompt prose except as required for token/budget correctness.
* Does not own unrelated hollow/empty provider classification (AST-1190) or hop-release debug trail (AST-1191) beyond consuming existing failure classes.
* Does not revive archived AST-903 as a parent — this is a fresh mini-epic off `origin/dev`.
* Betty TESTS:REVISE → sibling gap AST-1383 (tests not landed here).

## Notes for planning

* Bug parent: AST-1379 (orphaned mini-parent). Approved ancestor context: AST-903 (`docs/features/consult/ast-903-uat-craft-get-json-parse.md`) — prior craft_get truncate + `CRAFT_RUBRIC_MAX_TOKENS=32000` + JSON max_tokens hard-fail. Ticket archived; no related-issue link.
* Neighbor AST-1377 explicitly parked `craft_do_rubric max_tokens / truncated JSON` as out of epic.
* As-is/to-be/proposed steps live on AST-1379 Description.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1379-response-truncated-after-289-tokens`, child `sub/AST-1379/AST-1380-fix-craft-get-rubric-truncation`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-15T00:55:22.804Z
[review-fix] DISCUSS (no fix-now)

Decision A (craft-rubric DeepSeek thinking off) + provider-failure RESPONSE banner look solid; AST-903 max_tokens floor/gates untouched.

Process discuss: hop-confirm paper trail missing; TESTS:REVISE lives on sibling gap AST-1383 (not this sub). Chuckles taking clean-review → User Testing; gap must ship before parent finish-up.

#### joan — 2026-08-15T00:50:26.164Z
[board-joan]  CANON: OK

context_tokens≈12000

#### betty — 2026-08-15T00:50:24.169Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — Decision A thinking-off / truncated success RESPONSE for craft rubrics (AST-903 floor+max_tokens gate present; abrams path uncovered)

#### ada — 2026-08-15T00:49:13.093Z
`origin/sub/AST-1379/AST-1380-fix-craft-get-rubric-truncation` @ `45bb9982d062149a5a9ed5bd218d60524f7e149c` · truncation hole planned

---

_Implementation detail may live in git history on `origin/dev`._
