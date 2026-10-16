# AST-2183 — Unblock AST-2176: OK Betty --no-verify bible commit (shared engineer pre-commit hook)

<!-- linear-archive: AST-2183 archived 2026-10-16 -->

## Linear archive (AST-2183)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2183/unblock-ast-2176-ok-betty-no-verify-bible-commit-shared-engineer-pre  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** unassigned  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2172; blocks: AST-2176

### Description

**Need:** one call so Betty can commit her QA pass for [AST-2176](https://linear.app/astralcareermatch/issue/AST-2176).

The epic worktree `astral-AST-2172` shares the main repo's hook directory (`/home/susan/astral/.git/hooks/pre-commit`), and the hook installed there is the **engineer** hook — it blocks `tests/**` and `docs/test-bible/**`. Betty's docs-acceptance bible block (new AST-2176 entry in `docs/test-bible/README.md`, already written and staged in the worktree) can't be committed. No tests break and none are needed; AC 10b already passes on the branch tip.

Pick one (reply here):

1. **OK** `--no-verify` for this one bible-only Betty commit (and for later Betty bible commits in this epic while the shared engineer hook stays installed).
2. **Swap the hook yourself** (or tell Chuckles to) — note this changes the hook for the main `astral/` tree too, since worktrees share it.

Neither the child nor the parent is assigned to you. Move this to **Done** once you've answered; the agents take it from there.

### Comments

#### susan — 2026-10-12T23:47:05.984Z
1.

---

_Implementation detail may live in git history on `origin/dev`._
