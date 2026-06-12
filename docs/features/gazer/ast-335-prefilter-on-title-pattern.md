# AST-335 — Prefilter on Title Pattern

<!-- linear-archive: AST-335 archived 2026-06-03 -->

## Linear archive (AST-335)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-335/prefilter-on-title-pattern  
**Status at archive:** Done  
**Project:** Astral Gazer  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

We will have title_patterns added to candidate_data.context and use it to do a pattern match on each job list item that gazer finds after dedupe.  We will save them as NEW as usual, and gazer will have a separate function that will take up NEW records and pattern match them against the candidate data, and if they pattern match, their state becomes "VALID", and THAT becomes the input state for qualify job listing.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
