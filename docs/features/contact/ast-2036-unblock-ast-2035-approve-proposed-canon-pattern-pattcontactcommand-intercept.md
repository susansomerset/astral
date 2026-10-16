# AST-2036 — Unblock AST-2035: approve proposed canon pattern patt.contact.command-intercept

<!-- linear-archive: AST-2036 archived 2026-10-16 -->

## Linear archive (AST-2036)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2036/unblock-ast-2035-approve-proposed-canon-pattern-pattcontactcommand  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2032; blocks: AST-2035

### Description

**Needed:** approve (or reject/rename) the proposed canon pattern `patt.contact.command-intercept` so it can land in `canon/directives/`.

**Why:** [AST-2035](https://linear.app/astralcareermatch/issue/AST-2035) implements it exactly as the AST-2032 definition describes: a `CONTACT_CONFIG["commands"]` registry keyed by command id (handler + mode `code`/`agent`), a `/<command>` match on the first token after mentions, an intercept ahead of paste recovery and the LLM turn, and a per-mode reply. Joan approved the plan, Betty's 22 tests pass, and Radia found no fix-now items. Radia's only ESCALATE is that this id is on the ticket's Canon Scope but is not in the canon corpus yet, so it can't be scored. Details are in `## Radia review` of `docs/features/contact/ast-2035-contact-add-job-intercept.md` on `sub/AST-2032/AST-2035-contact-add-job-intercept`.

**How to answer:** reply here with "approved as-is", or with the changes you want to the pattern's wording. The agents will write the directive into the repo, so you don't need to push anything. Move this ticket to **Done** when you've answered.

Neither AST-2035 nor the parent AST-2032 is assigned to you. This gate is what holds them, and prep-uat won't run until it's Done.

### Comments

#### susan — 2026-10-08T09:51:45.211Z
Approved as is

---

_Implementation detail may live in git history on `origin/dev`._
