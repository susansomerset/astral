# AST-1396 — Gate empty-token warnings on Agent Ad Hoc load (loading ad hoc agent screen spills log warnings to the console)

<!-- linear-archive: AST-1396 archived 2026-08-31 -->

## Linear archive (AST-1396)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1396/gate-empty-token-warnings-on-agent-ad-hoc-load-loading-ad-hoc-agent  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1395 — loading ad hoc agent screen spills log warnings to the console  
**Blocked by / blocks / related:** parent: AST-1395

### Description

## What this implements

Silence `Token {$…} resolved to empty` WARNINGs when Agent Ad Hoc loads with no candidate selected. Keep the warning for real `do_task` / Test runs that have a candidate but missing name fields.

## Citations

Ancestor **AST-513** (archived — related-issue skipped). Feature doc: `docs/features/artifacts/ast-513-token-gap-correction.md` — owns the empty-token WARNING in `resolve_tokens`.

## Acceptance criteria

- [X] Opening Agent Ad Hoc with no candidate selected does not emit empty-token WARNINGs for `topic_menu_preamble_confirm` / `vet_inflow_discovery` (or any other task resolved on that load).
- [X] A `do_task` / Test run with a candidate still warns when `{$FIRST_NAME}` / `{$FULL_NAME}` is unexpectedly empty.

## Proposed change

- [X] Gate `resolve_tokens` candidate-source empty WARNINGs on truthy `candidate_data` (keep substituting `""`).

## Boundaries

Does not re-author prompts. Does not change the token registry. Does not silence empty-token warnings on production runs that have a `candidate_id`. Does not own Manage Tasks preview beyond a spot-check that real missing-name bugs still surface there.

## Notes for planning

Patch the existing AST-513 feature doc (`docs/features/artifacts/ast-513-token-gap-correction.md`) — do not create a new plan doc. Parent AST-1395 Description has As-is / To-be / Proposed steps. Engineer: Ada (AST-513 implementer).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1395-loading-ad-hoc-agent-screen-spills-log-warnings-to-the-console`, child `sub/AST-1395/<this-id>-<slug>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-16T02:56:50.351Z
[code-rubric] PROCEED (Commit: 1f8da029) gate empty-token warnings

#### joan — 2026-08-16T02:32:34.623Z
[board-joan]  CANON: OK

#### betty — 2026-08-16T02:28:29.388Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md — missing coverage — TestResolveTokens has no FIRST_NAME-only empty-cd silence assert (mixed any() still passes)

#### ada — 2026-08-16T02:23:35.118Z
`origin/sub/AST-1395/AST-1396-gate-empty-token-warnings-on-agent-ad-hoc-load` @ `65a463a5` · silence Ad Hoc list warnings

---

_Implementation detail may live in git history on `origin/dev`._
