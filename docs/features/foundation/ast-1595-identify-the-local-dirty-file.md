# AST-1595 — Identify the local dirty file

<!-- linear-archive: AST-1595 archived 2026-09-22 -->

## Linear archive (AST-1595)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1595/identify-the-local-dirty-file  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

There is a file dirty on the chuckles server so that pulls are blocked from team-chuckles origin main. Can you identify which file is dirty?

### Comments

#### chuckles — 2026-09-06T00:17:21.544Z
Dirty file blocking `git pull` on team-chuckles (`$TEAM_CHUCKLES_ROOT`, branch `main`, behind origin/main by 1):

`scripts/git/validate-tests-branch.sh` (modified, not staged)

No other dirty/untracked files in that working tree.

---

_Implementation detail may live in git history on `origin/dev`._
