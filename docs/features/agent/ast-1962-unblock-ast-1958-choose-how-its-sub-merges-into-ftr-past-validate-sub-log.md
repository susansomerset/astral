# AST-1962 — Unblock AST-1958: choose how its sub merges into ftr past validate-sub-log

<!-- linear-archive: AST-1962 archived 2026-10-08 -->

## Linear archive (AST-1962)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1962/unblock-ast-1958-choose-how-its-sub-merges-into-ftr-past-validate-sub  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1953

### Description

**Need:** your call on how AST-1958 gets merged into `ftr/AST-1953-agent-settings`. Neither AST-1958 nor AST-1953 is assigned to you; this ticket is the only thing waiting on you.

**Why it's stuck:** AST-1958 is User Testing (tests green, Radia clean). Its plan commit `eb7e78caa` reached ftr early, riding in on AST-1957's merge after the wave-2 engineers shared one epic worktree. `validate-sub-log.sh` only scans `ftr..sub`, can't see that plan commit, and fails with `missing plan(AST-1958)`. So merge-child refuses, and prep-uat can't open the PR without the migration on ftr.

**Pick one (reply here):**

1. Add a `plan()`-on-ftr exception to `validate-sub-log.sh`, mirroring the existing `test()` sibling-carry exception, plus a case in `test_validate_sub_log.sh`. Team-chuckles change.
2. One-off: Chuckles merges `origin/sub/AST-1953/AST-1958-migrate-agent-settings` into ftr by hand this time, with no tooling change.
3. Something else. Say what.

Reply here; the agents will make the change, so you don't need to push anything. Move this ticket to **Done** when you've answered, and AST-1953 resumes into prep-uat.

Side note, not part of this ask: the cause was parallel engineer builds sharing `astral-AST-1953`. AST-1956's build was run alone after the other two finished.

### Comments

#### susan — 2026-10-04T00:02:55.517Z
Option 1 — validator exception, merged in PR #26.

---

_Implementation detail may live in git history on `origin/dev`._
