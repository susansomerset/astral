# AST-279 — Establish Agent Tokens
**Component:** administrator  
**Children:** — (single ticket)  
**Linear archived:** AST-279 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-02 11:02 | AST-279 | — | `07782ece4` | AST-279: Establish agent tokens and restructure candidate_data |
| 2026-03-02 11:16 | AST-279 | merge | `0b2548c37` | Merge pull request #29 from susansomerset/chuckles/ast-279-establish-agent-tokens |
| 2026-03-02 11:37 | AST-279 | merge | `ba4bc9152` | Merge pull request #30 from susansomerset/chuckles/ast-279-establish-agent-tokens |

_Pre-`verb(AST-NNN)` era. Path convention was `ui/…`._

## Epic — AST-279
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-279/establish-agent-tokens · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: None / —_

### Original brief

create the list of replacement tokens that can be used in the prompt builds.

#### Comments

_No comments._

### Files changed (plan vs actual)

_No written plan or files list on the ticket; actual from `07782ece4` ("Establish agent tokens and restructure candidate_data")._

| | file | planned | actual |
|---|---|---|---|
| + | `src/utils/config.py` | — | `07782ece4` (125 lines — token list / candidate_data restructure) |
| + | `src/data/database.py` | — | `07782ece4` |
| + | `src/core/candidate.py` | — | `07782ece4` |
| + | `scripts/migrations/bootstrap_candidate.py` | — | `07782ece4` |
| + | `src/ui/frontend/src/components/{DetailsEditPage,FormFields}.tsx` | — | `07782ece4` (`ui/frontend/…`) |
| + | `src/ui/frontend/src/pages/Admin/ManageCandidates.tsx` | — | `07782ece4` |
| + | `src/ui/frontend/src/pages/Candidate/{Goals,Priorities}.tsx` | — | `07782ece4` |
| + | `src/ui/frontend/src/routes.tsx` | — | `07782ece4` |

_Implementation detail may live in git history on `origin/dev`._
