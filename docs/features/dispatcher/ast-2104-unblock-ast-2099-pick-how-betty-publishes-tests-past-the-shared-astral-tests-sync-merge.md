# AST-2104 — Unblock AST-2099: pick how Betty publishes tests past the shared astral-tests sync merge

<!-- linear-archive: AST-2104 archived 2026-10-16 -->

## Linear archive (AST-2104)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2104/unblock-ast-2099-pick-how-betty-publishes-tests-past-the-shared-astral  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** unassigned  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2016

### Description

**Need:** pick how Betty publishes the AST-2099 tests, because the shared `astral-tests` worktree's local `tests` branch currently fails `validate-tests-branch.sh`.

**What happened:** Betty finished qa-fix for [AST-2099](https://linear.app/astralcareermatch/issue/AST-2099). Every planned test plus the extra prefilter row is written. The `[bug-repro]` is red on the pre-fix product (`assert 6 == 1`) and green with the AST-2098 fix. The work is safe at commit `c6d80345a` on local branch `betty/AST-2099-qa-fix`. Before she could publish, a concurrent Betty `qa-child` run for AST-2086 (epic AST-2073) merged `958d74cc8 sync(publish-ref): origin/sub/AST-2011/AST-2096-all-x-fail-state` into local `tests`. The validator forbids that commit (only `merge-tests(AST-NNN):` merges are allowed). That run has since exited and left the merge in place. Local `tests` is 85 commits ahead of `origin/tests`, so I'm not rewriting it without your say-so.

**Options:**

1. **Publish around it (skips the validator once):** Betty pushes `c6d80345a` to `origin/sub/AST-2016/AST-2099-probe-fail-hold-gaps` as `merge-tests(AST-2099)` without the tests-branch validator. The `tests` cleanup happens separately.
2. **AST-2073's side cleans up first:** the AST-2086 owner removes `958d74cc8` from local `tests`, then Betty re-runs the AST-2099 publish normally.
3. **I clean it up:** Chuckles/Betty rewrite local `tests` to drop `958d74cc8`. This changes the local state AST-2086's run left behind.

Reply here with 1, 2 or 3; the agents will act on it. You don't need to push anything. Move this ticket to **Done** when you've answered. Neither AST-2099 nor AST-2016 is assigned to you; this gate is the only thing blocking them.

Also worth a look later, not blocking: Betty and Ada both report about 85 tests in the six touched test files already failing on `dev` (for example the `_check_circuit_breaker` arity change and the removed `_is_verified_job_site_distinct`). AST-2098/2099 add none of them.

### Comments

#### susan — 2026-10-09T03:32:51.070Z
3

---

_Implementation detail may live in git history on `origin/dev`._
