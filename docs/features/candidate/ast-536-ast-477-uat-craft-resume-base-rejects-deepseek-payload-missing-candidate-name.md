# AST-536 — AST-477 UAT: craft_resume_base rejects DeepSeek payload (missing candidate_name)

<!-- linear-archive: AST-536 archived 2026-06-15 -->

## Linear archive (AST-536)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-536/ast-477-uat-craft-resume-base-rejects-deepseek-payload-missing  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-477 — Candidate Resume Structure  
**Blocked by / blocks / related:** parent: AST-477

### Description

## Found by

Susan UAT on parent **AST-477** (2026-05-31): Generate **craft_resume_base** via Base Resume Content fails validation.

```
do_task validation failed. task_key='craft_resume_base' error=Missing required field 'candidate_name'
```

DeepSeek run (\~220s, 12k+ out tokens) — model likely returned `resume_structure` without flat top-level contact keys in `agent_payload`.

## Fix (shipped d38b2b28)

Before `_validate_response_schema` for `craft_resume_base`, `normalize_craft_resume_base_agent_payload` flattens enabled section strings from `resume_structure.sections` (`content`/`text`/`value`/`body`), `resume_structure.content`, and sibling content dicts onto top-level keys required by `TASK_CONFIG["craft_resume_base"]["response_schema"]`. Same flatten in `split_craft_resume_base_payload` for persistence.

## Acceptance

* Generate on Base Resume Content succeeds when model returns structure-heavy JSON without duplicate flat contact keys.
* `TestAst517ResumeStructure` green (29 tests).

## Git

Published on `origin/ftr/AST-477-candidate-resume-structure` (`d38b2b28`).

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
