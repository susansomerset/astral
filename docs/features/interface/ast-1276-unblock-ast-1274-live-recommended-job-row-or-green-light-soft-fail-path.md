# AST-1276 — Unblock AST-1274: live Recommended job row or green-light soft-fail path

<!-- linear-archive: AST-1276 archived 2026-08-17 -->

## Linear archive (AST-1276)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1276/unblock-ast-1274-live-recommended-job-row-or-green-light-soft-fail  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1274; blocks: AST-1273

### Description

## What is needed

[AST-1274](https://linear.app/astralcareermatch/issue/AST-1274/restore-recommended-job-detail-open-job-isnt-loading-on-recommended) Stage 1 cannot reproduce the detail HTTP 500: job `4a7dbb0c-a1cb-4c1d-ab9d-0c098c8313fc` is absent from the shared epic worktree DB (0 RECOMMENDED rows; 0 `agent_data` for that entity_id). Plan forbids sliding into Stage 2 without a confirmed cause (or an accepted waiver).

Pick **one**:

1. Restore the live `job` + `agent_data` rows onto the shared DB the epic worktree uses (or point it at the DB where the 500 was observed), **or**
2. Provide another RECOMMENDED job id that currently 500s on `GET /api/jobs/<id>` while listing, **or**
3. Green-light implementing the soft-fail path with Stage 4 forced-raise proof only (no live 500) — acceptance-risk call per `orch.pipeline.call-susan-for-product-decisions`.

Reply here or attach the file/rows; the agents will place it in the repo — you do not need to push. Move this ticket to **Done** when provided.

Neither [AST-1274](https://linear.app/astralcareermatch/issue/AST-1274/restore-recommended-job-detail-open-job-isnt-loading-on-recommended) nor parent [AST-1273](https://linear.app/astralcareermatch/issue/AST-1273/job-isnt-loading-on-recommended-page) is assigned to you. Child stays with Ada; parent stays In Progress with Chuckles.

— Chuckles

### Comments

#### susan — 2026-08-08T01:26:10.735Z
This is almost 100% the issue that we did not fully implement the ref_agent_data_id logic from the fetch side.  When the content is fetched from agent_data for the agent_data_id, the block_content is null, and it does not yet support recognizing if the block_content is null and the ref_agent_data_id is populated, then return that ref's block_content.

---

_Implementation detail may live in git history on `origin/dev`._
