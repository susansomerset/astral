# AST-1466 — Retire gaze_email stack (Clean up agent_task so that only the right meteorite email intake task is run)

<!-- linear-archive: AST-1466 archived 2026-09-09 -->

## Linear archive (AST-1466)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1466/retire-gaze-email-stack-clean-up-agent-task-so-that-only-the-right  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / 5  
**Parent:** AST-1363 — Clean up agent_task so that only the right meteorite email intake task is run  
**Blocked by / blocks / related:** parent: AST-1363

### Description

## What this implements

Retire the AST-1128 `gaze_email` stack and orphan `dispatch_task` cleanup per parent AST-1363: remove `gaze_email` agent_task/dispatch/config/module, rehome candidate-bound mailbox intake and Land Meteorite selected-ids under `meteorite_email` only.

## Scope

### Component scope

* `src/core/gaze_email.py` — delete after AST-1136 runner and AST-1140 selected-ids paths are rehomed under `meteorite_email`.
* `src/core/dispatcher.py` — remove AST-1134/1135 `gaze_email` provision, due merge, and dispatch branch; wire `meteorite_email` candidate-bound provision and runner call instead.
* `src/utils/config.py` — delete `GAZE_EMAIL_CONFIG` and `TASK_CONFIG["gaze_email"]`; consolidate mailbox literals into meteorite-email config; keep `INBOX_BIND_CONFIG` and admin enrichment coherent on `meteorite_email` only.
* `src/data/database.py` — migration to delete `gaze_email` dispatch rows, purge orphan `dispatch_task` rows, and (if needed) retarget AST-1135 bind-filtered Avail count queries from `gaze_email` to `meteorite_email`.
* `src/ui/api/api_inbox.py` — replace `run_gaze_email_selected_ids` with rehomed Land Meteorite selected-ids entrypoint on `meteorite_email`.
* `src/ui/api/api_admin.py` — remove `GAZE_EMAIL_CONFIG` Scheduled Actions special cases; rely on existing `is_meteorite_email_mailbox_task_key` enrichment only.
* `data/admin/agent_task.json` — remove `gaze_email` catalog row; `meteorite_email` remains the sole intake identity.
* `docs/uat-fixtures/AST-756/expected-agent_task.json` — byte-identical lockstep after gaze row removal.
* `tests/component/core/test_gaze_email.py` — delete; retarget `test_dispatcher.py`, `test_api_inbox.py`, `test_api_admin.py`, `test_config.py`, and frontend Scheduled Actions tests.
* `docs/test-bible/core/gaze_email.md` — retire or fold into meteorite-mailbox bible (Betty at Code Complete).

### Technical scope

* `src/core/gaze_email.py` — module deletion once `run_gaze_email`, `_handle_bound`, `run_gaze_email_selected_ids`, and helpers move to the `meteorite_email` home.
* `src/core/dispatcher.py` — delete `ensure_gaze_email_dispatch_task`, `provision_gaze_email_dispatch_tasks`, `_gaze_email_due_tasks`; add/rename equivalent provision+due for `meteorite_email`; modify `_dispatch_one` mailbox branch to import/call the rehomed runner.
* `src/utils/config.py` — delete `GAZE_EMAIL_CONFIG` block and asserts; extend `METEORITE_EMAIL_PARSE_CONFIG` (or sibling block) with mailbox runner literals formerly on gaze; modify `INBOX_BIND_CONFIG` and `_admin_dispatch_row_enrichment` to drop gaze branches.
* `src/data/database.py` — new idempotent migration(s): DELETE `dispatch_task` WHERE `task_key='gaze_email'`; DELETE orphan `dispatch_task` WHERE `task_key` NOT IN current `agent_task`; retarget any count/claim SQL still filtering on `gaze_email`.
* `src/ui/api/api_inbox.py` — modified land-meteorite handler calling the rehomed selected-ids async entrypoint.
* `src/ui/api/api_admin.py` — modified enrichment/filter helpers with gaze branches removed.
* Seed JSON + fixture — remove `gaze_email` object from array; no second intake row added.
* Tests / bible — delete or retarget gaze-specific coverage to `meteorite_email` dispatch runner behavior.

## Acceptance criteria

- [X] No live `gaze_email` product identity (agent_task, dispatch_task, config, module, imports).
- [X] Candidate-bound mailbox intake and Land Meteorite selected-ids work under `meteorite_email` only.
- [X] Orphan `dispatch_task` rows whose `task_key` is absent from current `agent_task` are removed.

## Boundaries

* Does not change Ruth `meteorite_email` parse prompts or qualify/GDL paths.
* Does not redesign Manage Email UI beyond rehomed ingest entrypoints.
* Betty owns test-tree / bible edits at Code Complete.

## Notes for planning

Approved ancestor: AST-1128 (archived). Patch `docs/features/meteorite/ast-1128-gaze-email-candidate-bound-dispatch-redesign.md` per plan-fix — inverse of 1134/1135/1136 shipped stack.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1363-clean-up-agent-task-so-that-only-the-right-meteorite-email-intake-task-is-run`, child `sub/AST-1363/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-24T22:40:04.000Z
[code-rubric] PROCEED (Commit: 770ba86f) Retire gaze_email rehome clean

#### katherine — 2026-08-24T22:36:09.855Z
`origin/sub/AST-1363/AST-1466-retire-gaze-email-stack` @ `770ba86f4d8b3768959c330a914ebb69b21b440b`

[bug-repro] `TestAst1467GazeEmailRetired` red→green (6 fail @ pre-fix `3cb55289` → 6 pass @ tip). Orphan-sweep guard + mailbox poller row seed landed in `test(AST-1466)`.

#### katherine — 2026-08-24T22:24:29.520Z
`origin/sub/AST-1363/AST-1466-retire-gaze-email-stack` @ `aba53d4ff977eb4b575869becb4a541b34de4c09` · inventory gate green

#### betty — 2026-08-24T22:02:34.025Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/gaze_email.md — broken test retarget — test_gaze_email.py delete + dispatcher/inbox/admin/config/repo_admin_json gaze_email asserts break on meteorite_email rehome

#### katherine — 2026-08-24T22:00:07.460Z
`origin/sub/AST-1363/AST-1466-retire-gaze-email-stack` @ `5997896f1b4649f1b705c7b745b094b7c54733bd` · Retire gaze_email stack

---

_Implementation detail may live in git history on `origin/dev`._
