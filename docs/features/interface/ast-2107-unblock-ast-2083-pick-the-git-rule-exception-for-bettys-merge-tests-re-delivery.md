# AST-2107 — Unblock AST-2083: pick the git-rule exception for Betty's merge-tests re-delivery

<!-- linear-archive: AST-2107 archived 2026-10-16 -->

## Linear archive (AST-2107)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2107/unblock-ast-2083-pick-the-git-rule-exception-for-bettys-merge-tests-re  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** unassigned  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2046

### Description

[AST-2083](https://linear.app/astralcareermatch/issue/AST-2083) needs you to pick one git-rule exception so Betty can re-deliver her tests.

**What happened:** Betty's `merge-tests(AST-2083)` delivery (`6af214f93`) on `origin/sub/AST-2046/AST-2083-resume-editor` conflicts with `origin/dev` in exactly one file, `tests/component/utils/test_config.py`. Both sides add an identical `TestAst2096AllXFailStates` class, in different positions. Every way to re-deliver it breaks a written rule:

* **A (Betty's recommendation):** a one-time force-with-lease reset of the sub to `1c2a16f53`, then one fresh `merge-tests(AST-2083)` with the class at dev's position. This breaks `orch.git.no-cherry-pick-rebase-force`.
* **B:** add a second `merge-tests(AST-2083)`. `validate-sub-log.sh` then fails merge-child on the duplicate.
* **C:** Betty pushes a `sync(dev)` resolve merge onto the sub. That isn't a Betty commit type, and it carries dev's `src/`.
* **D:** the engineer finishes the dev merge with `--no-verify`, which bypasses the pre-commit hook.

Katherine's product fix (`7dbde0c02`) passes all 47 manifest tests locally. It stays unpushed until the re-delivery merges cleanly.

**What I need:** reply here with A, B, C, or D (or another option). The agents will carry it out, and you don't need to push anything. Move this ticket to **Done** when you've answered.

Neither AST-2083 nor the parent [AST-2046](https://linear.app/astralcareermatch/issue/AST-2046) is assigned to you. They stay with Betty/Katherine and Chuckles, and they resume automatically once this ticket is Done.

### Comments

#### fable — 2026-10-09T04:13:51.534Z
**D**, under the AST-2069 byte-identity rule. (Posted by Claude Code on Susan's behalf.) No force-push, no second `merge-tests`.

1. **Katherine:** in the epic worktree, merge `origin/dev` into `sub/AST-2046/AST-2083-resume-editor` (`sync-child.sh`). Resolve `tests/component/utils/test_config.py` by taking dev's side: `git checkout MERGE_HEAD -- tests/component/utils/test_config.py`. Dev's `TestAst2096AllXFailStates` is identical in content, so nothing of Betty's is lost. Before committing, run this check; it must exit 0:
   ```bash
   git diff --cached --name-only HEAD -- tests docs/test-bible docs/ASTRAL_TEST_BIBLE.md \
     | while read f; do git diff --cached --quiet MERGE_HEAD -- "$f" || git diff --cached --quiet HEAD -- "$f" || { echo "$f"; exit 1; }; done
   ```
   It confirms every staged test or bible path matches a merge parent byte-for-byte. Then commit the `sync(dev)` merge with `--no-verify`, for this merge commit only. Push it plus `7dbde0c02`, rerun the manifest, and set Tests Passed. The pending engineer-hook change makes this exact check automatic, so `--no-verify` won't be needed next time.
2. **Betty:** add one `test(AST-2083):` commit on `tests` that makes `tests/component/utils/test_config.py` byte-identical to `origin/dev`'s copy, so `git diff origin/dev -- tests/component/utils/test_config.py` prints nothing. Right now `origin/tests` itself conflicts with `origin/dev` in this file. Don't deliver it to the AST-2083 sub; the sub already has `merge-tests(AST-2083)`.
3. **Chuckles:** fast-forward `origin/tests-clean-base` to the current `origin/tests` tip so `9ead623ca` is grandfathered and `validate-tests-branch.sh` stops needing one-off skips.

Structural fixes are in progress in team-chuckles, so this kind of exception stops reaching me.

---

_Implementation detail may live in git history on `origin/dev`._
