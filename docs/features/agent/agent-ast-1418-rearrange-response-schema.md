# AST-1418 — Rearrange response schema

**Component:** agent  
**Children:** — (single ticket)  
**Linear archived:** AST-1418 2026-08-31

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-17 06:57 | AST-1418 | code | `6113c749c` | put importance above content in craft rubric schema |
| 2026-08-31 14:17 | AST-1418 | docs | `5657a54ee` | archive Linear issue content |

## Epic — AST-1418

_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1418/rearrange-response-schema · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: Urgent / —_

#### Description

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

#### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| + unplanned | `src/utils/config.py` | — | `6113c749c` |
