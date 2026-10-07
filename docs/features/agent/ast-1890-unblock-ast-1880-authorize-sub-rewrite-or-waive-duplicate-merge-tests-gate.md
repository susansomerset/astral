# AST-1890 — Unblock AST-1880: authorize sub rewrite or waive duplicate merge-tests gate

<!-- linear-archive: AST-1890 archived 2026-10-07 -->

## Linear archive (AST-1890)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1890/unblock-ast-1880-authorize-sub-rewrite-or-waive-duplicate-merge-tests  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1851; blocks: AST-1880

### Description

**Needed:** your call on one of two ways to clear AST-1880's sub-log gate. Neither AST-1880 nor AST-1851 is assigned to you. This ticket is the only thing waiting on you.

**Why it's stuck:** `origin/sub/AST-1851/AST-1880-admin-model-pickers-platform-keys` has two `merge-tests(AST-1880)` commits from Betty:

* `e74930781`: the first QA delivery.
* `eb81cfe3a`: the AC 7 test-tree fix after Radia's review. The two test files still contained the literal `send_to_deepseek`, so AC 7's grep failed.

`validate-sub-log.sh` hard-fails on more than one `merge-tests` per child. `resolve-child` §9a and `merge-child` both run it, so AST-1880 can't reach User Testing or merge to ftr. The validator's own fix ("amend on tests, one merge-tests only") means rewriting published history on the sub. Git law forbids that: no force-push, no rebase of origin branches. No agent can clear it legally. This happened because Chuckles sent Betty back for the review return with "commit per qa-child"; she flagged the rule break when she pushed.

Everything else is done. Ada's resolve fix (`be239f09a`) is pushed, the dry-run merges into dev and ftr are clean, and the issue doc has Radia's review and Ada's resolution.

**Pick one (reply here):**

1. **Authorize a one-time rewrite:** Betty squashes her two tests commits into one on `tests`, then rebuilds the sub with a single `merge-tests` and Ada's and Chuckles' commits on top, force-pushed once.
2. **Waive the validator for this child:** accept two `merge-tests` on AST-1880. Either merge by hand, or have the validator allow a second `merge-tests` after a `docs(AST-1880): Radia review` commit (a review return pass).

Move this to **Done** once you've answered. The agents do the git work; you don't need to push.

### Comments

#### susan — 2026-09-29T23:00:44.962Z
One time rewrite approved.

---

_Implementation detail may live in git history on `origin/dev`._
