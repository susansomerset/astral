# AST-1905 — Cover saved contact line vs sparse contact blob on resume render (test gap for AST-1904)

<!-- linear-archive: AST-1905 archived 2026-10-08 -->

## Linear archive (AST-1905)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1905/cover-saved-contact-line-vs-sparse-contact-blob-on-resume-render-test  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1902 — Candidate Contact Detail is truncated after email  
**Blocked by / blocks / related:** parent: AST-1902

### Description

## What this implements

Test gap from fix-board on AST-1904 (`[board-betty] TESTS: REVISE`). Two existing builder tests assume the contact blob always overwrites the saved line and will break under AST-1904's fix (option (a): the saved `candidate_contact_detail` wins). Nothing covers the bug itself.

## Scope

### Component scope

* `tests/component/core/test_builder.py` (modified): repoint `TestBuilderHelpers::test_applies_profile_contact_and_markers` and `::test_profile_uses_reply_email_and_skips_empty_name` at an empty saved contact line so they keep covering the blob fallback, and add the AST-1904 regression to `TestAst1014BuilderContact`.
* `docs/test-bible/core/builder.md` (modified): bible entry for the new coverage under § AST-1014, plus a cross-reference in `docs/test-bible/core/candidate.md` § AST-1014 if Betty keeps that as the primary home.

### Technical scope

* `tests/component/core/test_builder.py`: modified test functions. The two `TestBuilderHelpers` tests build their input with `_resume_blob(candidate_contact_detail="")` or an equivalent. New test function(s) in `TestAst1014BuilderContact`: a multi-part saved line survives an email-only blob; a whitespace-only saved line falls back to the blob-built line; `candidate_name` is still overwritten from the name columns.
* `docs/test-bible/core/builder.md`: a new bible row pointing at those tests.

## Acceptance criteria

1. The bug-repro test fails on `origin/dev` (pre-fix `src/core/builder.py`) and passes once AST-1904's product fix is on the tip.
2. The two repointed `TestBuilderHelpers` tests pass on the post-fix tip and still exercise the blob-built line.
3. No product code changes on this ticket.

## Boundaries

Tests and bible only. The product fix (early return in `_apply_contact_to_render_dict`, `src/core/builder.py`) belongs to sibling AST-1904. It lands on the mini-parent ftr first and reaches this sub via sync-child.

## Notes for planning

Gap child filed by bug-fix from Betty's `[board-betty] TESTS: REVISE` on AST-1904 — read that comment. Plan section home: `docs/features/candidate/ast-1014-contact-context-artifacts-library.md` (same doc as AST-1904's `## Bug:` block).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1902-candidate-contact-detail-truncated`, child `sub/AST-1902/<child-segment>`. Created at bug-fix gap dispatch.

### Comments

#### radia — 2026-09-30T23:49:10.070Z
[code-rubric] PROCEED (Commit: 5246ff91f) bug-repro plus bible

#### ada — 2026-09-30T23:48:02.650Z
`origin/sub/AST-1902/AST-1905-cover-saved-contact-line-tests` @ `5246ff91f` · manifest green, bug-repro flips

**[bug-repro] gate:** `TestAst1014BuilderContact::test_saved_multi_part_contact_line_survives_email_only_blob`
- `origin/dev` `src/core/builder.py` (temp checkout, restored): **FAILED** (`hire@example.com` vs full saved line); full file 1 failed / 191 passed
- tip: **passed**

**AST-1905 manifest (`docs/test-bible/core/builder.md` § AST-1014 · AST-952), tip:**
1. bug-repro — passed
2. `TestAst1014BuilderContact` + `TestBuilderHelpers` — 12 passed
3. `tests/component/core/test_builder.py` — 192 passed

**AST-1901 carry — not ours** (run once, no product/test edits; AST-1901 product lives on `origin/ftr/AST-1851-support-openrouter-api-models` only):
- `tests/component/data/database/test_candidates.py` — 18 failed / 28 passed
- `tests/component/ui/api/test_api_candidate.py` — 16 failed / 125 passed
- `tests/component/core/test_candidate.py` — 20 failed / 447 passed
- `test_AdminManageCandidates.test.tsx` — not run (no `src/ui/frontend/node_modules`; install forbidden)
- Of the 54 Python failures, 33 are introduced by the AST-1901 test commit (`d3550e7ad`). 21 already fail on `origin/ftr/AST-1902-…` test files with the same `src/` (identical to ftr), and are unchanged with `origin/dev`'s `builder.py` swapped in, so they're pre-existing, not AST-1904/1905.

Runner: `ASTRAL_PYTHON=/home/susan/astral-AST-1851/.venv/bin/python` (ensure_component_venv.sh finds only 3.10–3.12). No commits this pass.

#### betty — 2026-09-30T23:44:01.865Z
[bug-repro]
`origin/sub/AST-1902/AST-1905-cover-saved-contact-line-tests` @ `5246ff91f` · repro lands red on pre-fix builder, green on tip

Stacked case: AST-1904 fix already on ftr, so the tip is post-fix. Red was proven against `origin/dev`'s `src/core/builder.py` (temporarily checked out, then restored): only `TestAst1014BuilderContact::test_saved_multi_part_contact_line_survives_email_only_blob` fails (`'hire@example.com' == <saved line>`, the Root-cause overwrite), 191 pass. Tip: `test_builder.py` 192/192. Manifest: `docs/test-bible/core/builder.md` § AST-1014 · AST-952. `validate-tests-branch.sh` skipped because `origin/tests-clean-base` is missing (AST-1894 precedent). Merge carries AST-1901 test/bible from origin/tests. @Ada

#### joan — 2026-09-30T23:41:27.093Z
[board-joan]  CANON: OK

Scope: **tests + `docs/test-bible/**` only** (AST-1905); no `src/**` on this publish ref. Product behavior is AST-1904 on ftr @ `7479f320a`. Frozen Canon Scope on AST-1902 / AST-1905: none cited.

Overlap skim (no `docs/canon-index.md` on ref; `canon/docs/DIRECTIVES-DIRECTORY.md` + in-force `canon/statutes/**`): `orch.roles.betty-owns-test-tree`, `astral.git.betty-no-src-or-features`, `astral.git.engineer-test-tree-ban` — delivery matches Betty/qa-fix; no engineer product landing. `astral.docs.features-single-file-per-ticket` applies to `docs/features/**`; bible rows in `docs/test-bible/core/{builder,candidate}.md` are test-tree documentation, not statute/pattern corpus.

No active directive requires amending canon to record AST-1904 precedence or test names; fixing fixture calls and adding `TestAst1014BuilderContact` regressions does not contradict `astral.config.config-source-of-truth` or any builder/contact statute (no product diff to score). Same fix-board pattern as other test-gap siblings (e.g. AST-1848): not F3 material.

context_tokens≈14000

#### betty — 2026-09-30T23:41:12.874Z
[board-betty] TESTS: REVISE
What: no bible entry for saved-line-over-sparse-blob — broken + missing coverage — this ticket is the test work itself, so it goes to qa-fix (make-fix cannot touch tests/). On the tip (AST-1904 fix at builder.py L1034–1035), `TestBuilderHelpers::test_applies_profile_contact_and_markers` (L350) and `::test_profile_uses_reply_email_and_skips_empty_name` (L380) fail until they pass `candidate_contact_detail=""`. The new `TestAst1014BuilderContact::test_saved_multi_part_contact_line_survives_email_only_blob` (exact-equality assert, red on origin/dev) is the [bug-repro] gate. `::test_whitespace_saved_contact_line_falls_back_to_blob` guards the fallback. The plan as written is sound: `_resume_blob()` stays unchanged, the bible adds lines only in builder.md § AST-1014 and a cross-ref in candidate.md § AST-1014, and no manifest edit is needed because the candidate.md manifest already runs both classes whole.

#### ada — 2026-09-30T23:40:31.276Z
`origin/sub/AST-1902/AST-1905-cover-saved-contact-line-tests` @ `b286ec308` · repoint two, add regression

---

_Implementation detail may live in git history on `origin/dev`._
