# AST-867 — Data table primary key data type inconsistencies

<!-- linear-archive: AST-867 archived 2026-07-29 -->

## Linear archive (AST-867)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-867/data-table-primary-key-data-type-inconsistencies  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-883

### Description

We have an integer index set for ONE table (dispatch_task), where other tables have UUIDs for their primary keys.  We must require consistency across our tables.

Separately, we are using UUIDs for most primary keys, but for company, candidate, etc., we are using names. We need to update the database to be consistent throughout.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
