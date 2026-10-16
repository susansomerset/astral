# AST-1886 — Unblock AST-1874: approve AST-1873 merge past validate-sub-log plan() check

<!-- linear-archive: AST-1886 archived 2026-10-07 -->

## Linear archive (AST-1886)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1886/unblock-ast-1874-approve-ast-1873-merge-past-validate-sub-log-plan  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1873; blocks: AST-1862; blocks: AST-1874

### Description

**Need:** one decision so `merge-child` can land [AST-1873](https://linear.app/astralcareermatch/issue/AST-1873/report-header-layout-labels-job-link-line-skip-button-recommended-job) on `ftr/AST-1862-recommended-job-modal-changes`. [AST-1874](https://linear.app/astralcareermatch/issue/AST-1874/modal-wiring-analysis-default-list-score-in-headers-skip-action) can't start until AST-1873's header code is on the ftr.

**Why it's stuck:** `validate-sub-log` reports `plan(AST-1873)` missing. The plan commit `d818add5` is already an ancestor of the ftr. It rode in on AST-1872's branch when the wave-1 drones shared the epic worktree. Everything else is on the sub: code ×3, test, merge-tests, Joan, Radia, and resolve. The ftr is already refreshed from dev.

**Pick one (reply here):**

1. Approve a one-time merge of `origin/sub/AST-1862/AST-1873-report-header-layout-labels-skip-button` into the ftr without the validator.
   1. approved
2. Fix `validate-sub-log` (Team Chuckles) so it accepts a `plan()` / `docs(): plan` commit already reachable from the ftr. I re-run merge-child after.

Move this ticket to **Done** once you've answered. Neither [AST-1874](https://linear.app/astralcareermatch/issue/AST-1874/modal-wiring-analysis-default-list-score-in-headers-skip-action) nor [AST-1862](https://linear.app/astralcareermatch/issue/AST-1862/recommended-job-modal-changes) is assigned to you, and the pipeline resumes on its own.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
