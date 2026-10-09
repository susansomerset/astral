# AST-1952 — Unblock AST-1950: approve validator fix (A) or one-time merge override (B) for false 'missing test'

<!-- linear-archive: AST-1952 archived 2026-10-08 -->

## Linear archive (AST-1952)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1952/unblock-ast-1950-approve-validator-fix-a-or-one-time-merge-override-b  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1946

### Description

[AST-1950](https://linear.app/astralcareermatch/issue/AST-1950) (remap migration) is the last child of [AST-1946](https://linear.app/astralcareermatch/issue/AST-1946) not yet merged into `ftr/AST-1946-big-brain-openrouter`. Every child is at User Testing; prep-uat waits on this one merge.

Why: `merge-child.sh` stops with `BLOCKED: missing test(AST-1950)`. That is a false positive. Betty's shared `origin/tests` line has AST-1949's test commit on top of AST-1950's (`fe41777d9`), so AST-1949's `merge-tests` already carried AST-1950's test onto ftr. `validate-sub-log.sh` only scans commits on the sub that ftr doesn't have, so it can't see it. A dry-run merge into ftr is clean. A fake `test()` commit is forbidden, and no agent can change the validator's rule on its own.

Need one answer — pick A or B:

* **A (recommended):** change `validate-sub-log.sh` to accept a `test(<child>)` commit that is already reachable from ftr. Fixes this case for every future epic where sibling tests stack.
* **B:** one-time override — Chuckles merges `sub/AST-1946/AST-1950-remap-migration` into ftr without the validator, this epic only.

Reply here with A or B, then move this to **Done**. You do not need to push anything.

> A, please

Neither [AST-1950](https://linear.app/astralcareermatch/issue/AST-1950/run-once-agent-remap-starting-modes-new-sizes-kimi-fold-support-big) nor [AST-1946](https://linear.app/astralcareermatch/issue/AST-1946/support-big-brain-openrouter-models) is assigned to you. [AST-1950](https://linear.app/astralcareermatch/issue/AST-1950/run-once-agent-remap-starting-modes-new-sizes-kimi-fold-support-big) stays with Katherine; [AST-1946](https://linear.app/astralcareermatch/issue/AST-1946/support-big-brain-openrouter-models) stays In Progress with Chuckles.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
