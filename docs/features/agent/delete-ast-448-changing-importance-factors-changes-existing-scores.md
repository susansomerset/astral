# AST-448 — Changing importance factors changes existing scores?

<!-- linear-archive: AST-448 archived 2026-07-22 -->

## Linear archive (AST-448)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-448/changing-importance-factors-changes-existing-scores  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-447

### Description

when I changed the importance values for job list criteria vectors, the importance did not resequence.  Not sure what the right solution is here, but we should not resequence the headers if the importance was not weighted at the time of the run, when the score was calculated and stored.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
