# AST-313 — Artifact Pipeline Prompt Authoring

<!-- linear-archive: AST-313 archived 2026-06-23 -->

## Linear archive (AST-313)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Susan authors 8 agent task prompts for the resume and cover letter daisy-chain pipeline directly in the Manage Tasks UI (AdminTaskPrompts). No code changes — all input via the UI into the agent_task table. 

Chain sequence: 

(1) Judith free-think/coffee-date job analysis, 

(2) Estelle revision instructions for resume and cover letter, 

(3) Judith resume line edits using Estelle's instructions, 

(4) Grace resume fact-check, 

(5) Estelle final revised resume content, 

(6) Judith cover letter draft using Estelle's cached instructions, 

(7) Grace cover letter fact-check, 

(8) Estelle final cover letter. 

For each task: select agent, write system_prompt and task_prompt, set run_next to wire the chain, configure cache block assignments. Partially blocks Build Resume Artifact and Build Cover Letter Artifact — Chuckles can wire the chain structure and configure run_next scaffolding before prompts are written; Susan fills in prompt content after the chain skeleton is in place.

### Comments

#### susan — 2026-05-31T19:49:53.420Z
Setting this to PR ready so that child tickets get deployed.

#### chuckles — 2026-05-23T16:18:40.278Z
Blocked on [AST-450](https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry) — register the nine pipeline `task_key`s in `TASK_CONFIG` (dumb registry only; no step lists in code). After Ada lands that, you can wire `run_next` and author prompts here.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
