# AST-1354 — Fix agent story soft-fail + move to agent.py (Can't find agent data for proposed application responses)

<!-- linear-archive: AST-1354 archived 2026-08-31 -->

## Linear archive (AST-1354)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1354/fix-agent-story-soft-fail-move-to-agentpy-cant-find-agent-data-for  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1316 — Can't find agent data for proposed application responses  
**Blocked by / blocks / related:** parent: AST-1316

### Description

## What this implements

Fix agent-story load so a missing `propose_application_responses` TASK `agent_data` id (or missing artifact elements) does not dump a stacktrace / treat those pieces as required. Move `get_entity_agent_story` from `roster.py` → `agent.py` (roster is company data). Soften the residual AST-1274 soft-fail path (quieter than `logger.exception` stack dumps) and keep detail openable.

## Acceptance criteria

- [X] 1. Opening a job whose latest `propose_application_responses` refs a missing TASK `agent_data` id does **not** emit a full stacktrace for that expected missing piece; detail still returns usable payload (story empty or partial, not fatal).
- [X] 2. Missing optional artifact / agent_data elements for proposed application responses are not treated as required for story/detail load.
- [X] 3. `get_entity_agent_story` lives in `src/core/agent.py` (not `roster.py`); callers (`api_jobs` / `api_companies`) import from agent; roster no longer owns entity story.
- [X] 4. Ancestor context: AST-1274 soft-fail contract preserved (data still raises on corrupt refs; callers soft-fail).

## Proposed change (make-fix)

- [X] `list_entity_latest_agent_refs` metadata-only batch read (no sibling resolve)
- [X] Move `get_entity_agent_story` + `_filter_response_block` to `agent.py`; per-id soft content load; warning logs without traceback
- [X] Remove story from `roster.py` (no re-export)
- [X] `api_jobs` / `api_companies` import from agent; detail soft-fail uses `logger.warning`

## Boundaries

* Does not re-open AST-1274 primary data-layer ref resolve.
* Does not redesign artifact pin write (AST-1099) unless required for the “don’t require artifacts elements” read path.
* Does not change propose_application_responses LLM/task behavior.
* Betty TESTS:REVISE → sibling gap AST-1355 (tests not landed here).

## Notes for planning

* Approved ancestor doc: `docs/features/interface/ast-1274-restore-recommended-job-detail-open.md`
* Susan: move entity story to [agent.py](<http://agent.py>); roster = company data.
* Bug Description: no stacktrace; do not require elements in artifacts.
* Stack: `get_entity_agent_story` → `list_entity_latest_agent_refs` → missing TASK id.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1316-cant-find-agent-data-for-proposed-application-responses`, child `sub/AST-1316/AST-1354-fix-agent-story-no-require-artifacts`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-13T01:46:18.094Z
[code-rubric] PROCEED (Commit: 3bc5c8cf) metadata story soft-fail

#### ada — 2026-08-13T01:43:27.133Z
`origin/sub/AST-1316/AST-1354-fix-agent-story-no-require-artifacts` @ `3bc5c8cfbe29b57cadfb675cfe253af35ad9d034` · restored metadata-only list_refs; lighter check 11 passed

#### ada — 2026-08-13T01:42:49.131Z
`origin/sub/AST-1316/AST-1354-fix-agent-story-no-require-artifacts` @ `c5ca227b07deb195debb7a8c3c82f2eb161a7922` · lighter check green (no bug-repro; AST-1355 owns roster story tests)

#### joan — 2026-08-13T01:36:20.151Z
[board-joan]  CANON: OK

context_tokens≈14000

#### betty — 2026-08-13T01:35:26.776Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md + tests/component/core/test_roster.py (get_entity_agent_story / AST-1274 soft-fail) — imports + story ownership move to agent.py break existing rows; repro (dangling propose_application_responses TASK sibling → partial story, no exception stack) has no bible coverage yet

#### ada — 2026-08-13T01:34:20.088Z
`origin/sub/AST-1316/AST-1354-fix-agent-story-no-require-artifacts` @ `70c6d3a249ea0f29645881b8af437c6d0a62e0d4` · plan-fix story soft-fail

---

_Implementation detail may live in git history on `origin/dev`._
