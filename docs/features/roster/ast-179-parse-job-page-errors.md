# AST-179 — Parse Job Page Errors

<!-- linear-archive: AST-179 archived 2026-07-22 -->

## Linear archive (AST-179)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-179/parse-job-page-errors  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** unassigned  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

We're getting a few errors:

\[molecule\] ERROR: 'NoneType' object has no attribute 'get'
\[tagnos\] ERROR: 'NoneType' object has no attribute 'get'
\[braid\] ERROR: 'NoneType' object has no attribute 'get'

\[mediktor\] ERROR: No URLs found when crawling [https://www.mediktor.com/](<https://www.mediktor.com/>)

\[vitestro\] ERROR: ':gap-y-2' was detected as a pseudo-class and is either unsupported or invalid. If the syntax was not intended to be recognized as a pseudo-class, please escape the colon.

line 1:

div.container div.flex.flex-col.gap-y-5.lg\\:gap-y-2.border-t-2.border-blue-light.py-5.text-base\\/6

\[oxforddrugdesign\] ERROR: Page.goto: NS_ERROR_ABORT

Call log:

\- navigating to "[https://oxforddrugdesign.com/index.php/careers](<https://oxforddrugdesign.com/index.php/careers>)", waiting until "load"

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
