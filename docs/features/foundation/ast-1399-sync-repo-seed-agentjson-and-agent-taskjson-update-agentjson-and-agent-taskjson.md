# AST-1399 — Sync repo seed agent.json and agent_task.json (Update agent.json and agent_task.json)

<!-- linear-archive: AST-1399 archived 2026-08-31 -->

## Linear archive (AST-1399)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1399/sync-repo-seed-agentjson-and-agent-taskjson-update-agentjson-and-agent  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1398 — Update agent.json and agent_task.json  
**Blocked by / blocks / related:** parent: AST-1398

### Description

## What this implements

Update checked-in `data/admin/agent.json` and `data/admin/agent_task.json` (and AST-756 fixture twins as required) so they match the live agent-model and Do/Like prompt export attached on AST-1398 (`agents.txt`, `agent_task.txt`). Startup upsert must load the updated personas and Do/Like prompts, not the stale seed.

## Acceptance criteria

- [X] `data/admin/agent.json` matches the attached agent-model export (repo column shape — no `model_code`; `brain_setting` authoritative).
- [X] `data/admin/agent_task.json` Do/Like rows (`craft_do_rubric` / `craft_like_rubric` at minimum; `grade_do` / `grade_like` / meteorite twins only if the attachment changed them) match the attached task export. Unrelated task rows stay untouched unless the attachment is a full current-row dump.
- [X] AST-756 expected fixtures (`docs/uat-fixtures/AST-756/expected-agent.json` and `expected-agent_task.json`) stay honest with the last seed ticket's parity rule (whole-file twin or surgical row update — plan-fix picks).
- [X] No `src/` unless the export/upsert contract is broken; no new task keys.

## Proposed change

- [X] Fetch AST-1398 `agents.txt` / `agent_task.txt` and map onto repo columns.
- [X] Replace catalog Estelle only (`temperature` 0, `max_tokens` 384000, §1 content, `updated_at` 2026-08-16 06:43:40); six-id set unchanged; no `model_code`.
- [X] Replace catalog `craft_do_rubric` / `craft_like_rubric` from the attachment; leave the other 50 rows; do not add the three ZZZ stubs (catalog stays 52).
- [X] `cp` catalog → `expected-agent_task.json` (byte twin); surgical Estelle repo columns on `expected-agent.json` (keep fixture `model_code`).
- [X] Tests stay on sibling AST-1400 — not landed here.

## Boundaries

* Does not redesign Manage Agents / Manage Tasks, startup upsert, or the export script (AST-782) except if the JSON shape itself is illegal under the existing contract.
* Does not invent personas or drop the six-id set unless the attachment actually does.
* Does not revive archived AST-756 as a parent — this is a fresh mini-epic off `origin/dev`.

## Notes for planning

* Bug parent: AST-1398 (orphaned mini-parent). Approved ancestor: AST-756 (`docs/features/foundation/ast-756-create-repo-json-files-for-agent-and-agent-task.md`) — repo-owned `agent` / `agent_task` JSON. Ticket archived; no related-issue link.
* As-is/to-be/proposed steps live on AST-1398 Description. Source of truth for the new text: Linear attachments `agents.txt` and `agent_task.txt` on AST-1398.
* Engineer: Ada (AST-756 team).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1398-update-agent-and-agent-task-json`, child `sub/AST-1398/AST-1399-sync-agent-agent-task-seed`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-16T07:38:16.253Z
[code-rubric] PROCEED (Commit: 10e71c80) seed sync matches plan

#### joan — 2026-08-16T07:30:57.319Z
[board-joan]  CANON: OK

#### betty — 2026-08-16T07:30:10.497Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/repo_admin_json.md — missing coverage — no test pins Estelle repo columns (temp 0, max_tokens 384000, §1 content) or craft_do/like attachment uuids and prompt lengths

#### ada — 2026-08-16T07:26:38.198Z
`origin/sub/AST-1398/AST-1399-sync-agent-agent-task-seed` @ `47262dfd` · surgical Estelle Do/Like seed

---

_Implementation detail may live in git history on `origin/dev`._
