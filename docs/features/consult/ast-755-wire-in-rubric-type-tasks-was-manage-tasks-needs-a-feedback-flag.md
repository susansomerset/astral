# AST-755 — Wire in RUBRIC type tasks (was ‘Manage Tasks needs a "Feedback" flag’)

<!-- linear-archive: AST-755 archived 2026-08-19 -->

## Linear archive (AST-755)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-755/wire-in-rubric-type-tasks-was-manage-tasks-needs-a-feedback-flag  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Some of our tasks are based on rubrics (e.g. the Artifact generating prompts), so we need a clean architecture of what to include in every prompt and what not to include and based on which criteria.

I'm tempted to suggest we have a specific function for prompt builder preferably, rather than stuffing everything into config.  It would be given a series of boolean flags to include or exclude content, set by the caller, and use content set in the PROMPT_CONFIG object in config.py

The issue is that right now, it is not cleanly coherent how prompts get "buffed" from config content, and when.  We need a small logical engine to determine if, say, the agent envelope should include rubric feedback or not.

Let's start with an audit of config.py to identify all the prompt padding that is happening and determine if there are task settings that would determine if that padding is appropriate or not.  It may be as simple as adding "padding" tokens to the prompts.  So, the system prompt would be {$DATE_TIME}\n\n{$NOTE_JSON_OUTPUT}\n\n{$NOTE_IMPORTANCE}, etc., so that it's easy to be consistent about the content.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
