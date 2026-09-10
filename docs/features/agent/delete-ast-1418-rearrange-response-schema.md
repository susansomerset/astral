# AST-1418 — Rearrange response schema

<!-- linear-archive: AST-1418 archived 2026-08-31 -->

## Linear archive (AST-1418)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1418/rearrange-response-schema  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Move the importance rating above the description for every craft rubric response schema in config.py.

"agent_payload": {

```
"criteria": [
  {
    "label": "<label>",
    "code": "<code>",
    "content": "<content>",
    "importance": 0
  }
]
```

to

"agent_payload": {

```
"criteria": [
  {
    "label": "<label>",
    "code": "<code (unique to rubric)>",
    "importance": 0,
    "content": "<content>"
  }
]
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
