# AST-1398 — Update agent.json and agent_task.json

<!-- linear-archive: AST-1398 archived 2026-08-31 -->

## Linear archive (AST-1398)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1398/update-agentjson-and-agent-taskjson  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Repo seed `data/admin/agent.json` still has the six checked-in personas (Atlas, Ruth, Judith, Grace, Estelle, Laslo) from the AST-756 / AST-787 contract. Repo seed `data/admin/agent_task.json` still has the in-repo Do/Like prompt rows (`craft_do_rubric`, `craft_like_rubric`, plus `grade_do` / `grade_like`). Those files do not include the agent-model and Do/Like prompt updates already made live (this ticket's attached `agents.txt` / `agent_task.txt`). A fresh clone or server restart upserts the stale repo JSON and clobbers the updated copy.

## To-be

Checked-in `data/admin/agent.json` and `data/admin/agent_task.json` match the attached updated agent model and Do/Like prompts, so startup upsert loads that content. AST-756 fixture twins (`docs/uat-fixtures/AST-756/expected-agent.json` and `expected-agent_task.json`) stay honest with whatever parity rule the last seed ticket used.

## Proposed steps

1. Pull `agents.txt` and `agent_task.txt` from this ticket's attachments and map them onto the repo JSON shape (`data/admin/agent.json` / `data/admin/agent_task.json` columns — no `model_code`; `brain_setting` authoritative).
2. Replace persona rows in `agent.json` with the attached agent-model export; do not invent extra personas or drop the six-id set unless the attachment actually does.
3. Update the Do/Like task rows in `agent_task.json` from the attachment (`craft_do_rubric` / `craft_like_rubric` at minimum; `grade_do` / `grade_like` / meteorite twins only if those files changed them). Leave unrelated task rows alone unless the attachment is a full current-row export.
4. Sync the AST-756 expected fixtures to the same bytes, or surgical row updates if a wholesale `cp` would absorb unrelated drift — plan-fix picks.
5. No `src/` unless the export/upsert contract is broken; no new task keys.

## Original brief

We have updated the agent model and the do and like prompts.  Make the seed data in the repo reflect these changes.

[agent_task.txt](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/58be1b84-33e8-48a0-8602-e21f8f18654a/1be7252a-5ed3-4816-9c39-507e78914f64)

[agents.txt](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/40b4b5ce-12be-487c-8a05-7b6b52274c25/f5ab795b-b5a6-4aa6-9d78-50e8065cd8c5)

### Comments

#### susan — 2026-08-16T07:15:04.892Z
756

#### chuckles — 2026-08-16T07:14:14.975Z
Ancestor candidates (ranked — pick one, ask about one, or reject the set):

1. AST-756 (archived, Foundation) — create repo JSON for `agent` and `agent_task`. Best parent: this bug is "those seed files are stale vs a new export."
2. AST-787 (archived, child of AST-756) — populated `data/admin/agent.json` with the six persona rows. Closest child for the agent-model half.
3. AST-786 (archived, child of AST-756) — populated `data/admin/agent_task.json` prompts/metadata, including `craft_do_rubric` / `craft_like_rubric`. Closest child for the Do/Like prompt half.
4. AST-1103 (archived, Astral Agent) — last wholesale rewrite of both seed files (persona + prompt corpus). Plausible if this is another content pass on the same two files rather than Foundation seed-infra.
5. AST-1368 (Candidate, parent AST-1360) — most recent Do/Like *craft* seed edit (`craft_do_rubric.cache_prompt` Ideal Day). Weaker: does not touch `agent.json`, and the ask here looks like a full model+prompt dump, not Ideal Day wiring.

---

_Implementation detail may live in git history on `origin/dev`._
