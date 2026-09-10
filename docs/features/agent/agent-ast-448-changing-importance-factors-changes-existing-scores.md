# AST-448 — Changing importance factors changes existing scores?

**Component:** agent  
**Children:** — (single ticket)  
**Linear archived:** AST-448 2026-07-22

## Ledger

_No AST-tagged commits — this ticket predates the `verb(AST-NNN):` convention._

## Epic — AST-448

_Archived: 2026-07-22 · Linear URL: https://linear.app/astralcareermatch/issue/AST-448/changing-importance-factors-changes-existing-scores · Status at archive: Archive · Project: Astral Agent · Assignee: susan · Priority / estimate: High / — · Blocked by / blocks / related: duplicate: AST-447_

#### Description

when I changed the importance values for job list criteria vectors, the importance did not resequence.  Not sure what the right solution is here, but we should not resequence the headers if the importance was not weighted at the time of the run, when the score was calculated and stored.

#### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
