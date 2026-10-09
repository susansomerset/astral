# AST-1921 — Unblock AST-1851 prep-uat: foreign AST-1908/1916/1917 test commits on ftr — reseed, sub-only PR, or land as-is

<!-- linear-archive: AST-1921 archived 2026-10-08 -->

## Linear archive (AST-1921)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1921/unblock-ast-1851-prep-uat-foreign-ast-190819161917-test-commits-on-ftr  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1851

### Description

**Needed:** your call before prep-uat opens the next `ftr/AST-1851-support-openrouter-api-models → dev` PR. All AST-1851 children are User Testing and merged on ftr. This ticket is the only thing waiting on you.

**Problem:** ftr is 10 commits ahead of `origin/dev`. Six are AST-1920 (legit). Four are foreign test-only commits that came in through `merge-tests(AST-1920)` (`74087971d`) from the shared `origin/tests`, the same shared-tests problem as AST-1914:

* `849ec23bf test(AST-1908)`: AST-1899 epic (Session Resume Paste Vitest cases + pages.md)
* `1c4380b6c test(AST-1916)` and `36e35014b test(AST-1917)`: AST-1875 epic (runtime AUTO-thread cap tests + bible)
* `a3ce35871 resync(tests)`

None of their product code is on dev. On the ftr tip, `TestAst1916AutoThreadCap` errors 16 times in `tests/component/core/test_dispatcher.py`. Separately, `test_dispatcher.py` already has 45 failures on plain `origin/dev`, and `test_api_admin.py` can't collect locally (`asyncpg` missing). Those exist with or without this ftr.

**Options:**

1. **Reseed (recommended, same as AST-1914):** rebuild ftr from `origin/dev` plus only the AST-1920 commits. This needs a one-time history exception on ftr.
2. **PR only the AST-1920 sub:** like #200, merge `sub/AST-1851/AST-1920-manage-candidate-key-fields` after the same reseed, skipping the ftr.
3. **Land as-is:** the AST-1908/1916/1917 tests ride along and stay red on dev until their epics land.

Pick one and move this ticket to Done. Chuckles then runs prep-uat.

### Comments

#### chuckles — 2026-10-02T05:01:36.923Z
Option 1 (reseed) turned out to be a no-op: the four foreign commits (849ec23bf, 1c4380b6c, 36e35014b, a3ce35871) had already reached origin/dev when their epics landed. So origin/dev..ftr contained only AST-1920 work, and no history rewrite was needed.

prep-uat is done. The PR is https://github.com/susansomerset/astral/pull/205 and it touches 2 files: the plan doc and AdminManageCandidates.tsx. AST-1851 is now in User Testing.

#### susan — 2026-10-02T04:59:35.581Z
1

---

_Implementation detail may live in git history on `origin/dev`._
