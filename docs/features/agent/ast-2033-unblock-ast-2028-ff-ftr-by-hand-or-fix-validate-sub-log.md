# AST-2033 — Unblock AST-2028: ff ftr by hand or fix validate-sub-log?

<!-- linear-archive: AST-2033 archived 2026-10-16 -->

## Linear archive (AST-2033)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2033/unblock-ast-2028-ff-ftr-by-hand-or-fix-validate-sub-log  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2028

### Description

Need one decision so AST-2028 can go to prep-uat.

Betty restored dev's `test_render_verdict_bad_confidence_first_strike_to_retry` (dropped from `origin/tests` by resync `84095c453`) onto `origin/sub/AST-2028/AST-2031-job-run-modal-entity-scoped` (`299e6fc0b`). `merge-child.sh` won't re-merge it: `validate-sub-log.sh` only looks at sub commits not yet on ftr and asks for `code()` / `docs()` / `resolve()(AST-2031)` again. Without it, the ftr → dev PR deletes that test from dev.

Pick one (reply here):

1. Fast-forward ftr to the AST-2031 sub tip by hand (same merge `merge-child.sh` does, skipping only the label check), then prep-uat.
2. Fix `validate-sub-log.sh` first so a test-only follow-up after a child's first merge passes, then re-run merge-child + prep-uat.

Reply here; the agents do the rest — you don't need to push. Move this to **Done** when answered. Neither the parent nor AST-2031 is assigned to you.

### Comments

#### susan — 2026-10-08T05:09:49.891Z
2, if it Will prevent this issue going forward

---

_Implementation detail may live in git history on `origin/dev`._
