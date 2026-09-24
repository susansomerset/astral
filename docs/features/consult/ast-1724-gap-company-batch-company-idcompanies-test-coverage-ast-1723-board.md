# AST-1724 — Gap: company batch company_id/companies test coverage (AST-1723 board)

<!-- linear-archive: AST-1724 archived 2026-09-24 -->

## Linear archive (AST-1724)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1724/gap-company-batch-company-idcompanies-test-coverage-ast-1723-board  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1720 — company-entity tasks are returning job references  
**Blocked by / blocks / related:** parent: AST-1720

### Description

## What this implements

Test/bible gap opened by fix-board on AST-1723: company prefilter/vet fixtures still assert `batch_entities.astral_job_id` + `parsed_response.jobs`; no coverage for the to-be `company_id` / `companies` contract. Land a \[bug-repro\] that fails against pre-fix product and passes after AST-1723, plus bible note.

## Scope

### Component scope

* `tests/component/core/test_roster.py` — **modified** — revise AST-702 / AST-880 (and any sibling) fixtures that assert company batch `astral_job_id` / `jobs`; add coverage for `company_id` / `companies` (or the exact keys plan-fix freezes).
* `docs/test-bible/core/roster.md` — **modified** — record AST-1723/AST-1720 company-batch identity coverage under the AST-702 / prefilter-company entry.

### Technical scope

* `test_roster.py` — **modified / new test case(s)** under existing AST-702 / AST-880 suites: company batch encode/decode must not require job vocabulary; assert `company_id` on batch_entities and company-labeled parsed payload (exact names per plan-fix).
* `docs/test-bible/core/roster.md` — **modified bible entry** naming the new node id / pattern for Betty/qa-fix successors.

## Proposed change

- [X] Sync/merge AST-1723 product (`company_id` / `companies`) onto gap tip via ftr
- [X] Betty `[bug-repro]` `TestAst1724CompanyBatchCompanyIdContract` green on tip
- [X] No product rewrite beyond ftr merge (test-tree remains Betty's)

## Notes for planning

Sibling of AST-1723 (product company_id/companies contract). Board: `[board-betty] TESTS: REVISE` — docs/test-bible/core/roster.md (AST-702 / AST-880) — broken fixtures assert batch_entities.astral_job_id + parsed_response.jobs.

### Comments

#### radia — 2026-09-20T05:12:57.980Z
[code-rubric] PROCEED (Commit: d971f9ad) company_id repro coverage clean

[bug-repro] OK for encode + reconcile. What must still hold OK. No fix-now. Advisory: stale AST-507 docstring only.

#### betty — 2026-09-20T05:08:49.625Z
[bug-repro]
`origin/sub/AST-1720/AST-1724-company-batch-company-id-test-coverage` @ `ba1e3c76` · repro lands red, awaits fix

#### betty — 2026-09-20T05:03:26.631Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md (AST-702 / AST-880) — missing [bug-repro] for company_id/companies; revise obsolete jobs/astral_job_id fixtures in test_roster.py — land per Proposed change

#### joan — 2026-09-20T05:03:06.699Z
[board-joan]  CANON: OK

context_tokens≈12000

#### hedy — 2026-09-20T05:01:43.207Z
`origin/sub/AST-1720/AST-1724-company-batch-company-id-test-coverage` @ `4062328f10cc3a6f0ff474cab6700b00ba7d50a5` · company_id test coverage plan

---

_Implementation detail may live in git history on `origin/dev`._
