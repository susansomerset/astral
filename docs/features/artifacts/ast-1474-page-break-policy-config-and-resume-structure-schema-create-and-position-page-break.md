# AST-1474 — Page-break policy config and resume_structure schema (Create and position page break)

<!-- linear-archive: AST-1474 archived 2026-09-09 -->

## Linear archive (AST-1474)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1474/page-break-policy-config-and-resume-structure-schema-create-and  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1462 — Create and position page break  
**Blocked by / blocks / related:** parent: AST-1462; blocks: AST-1475

### Description

## What this implements

Adds config-owned policy tokens with keep-together as the default for all known sections; extends `normalize_resume_structure` / defaults / GET catalog so structure sections persist a page-break policy. Does **not** emit print CSS or build React controls.

## Citations

`pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`.

## Scope

`src/utils/config.py` (allowed tokens, keep-together default map, catalog literals); `src/core/candidate.py` (validate/normalize/default new field); `src/ui/api/api_candidate.py` (catalog payload for policies).

## Acceptance criteria

1. **Defaults** — a candidate with no explicit page-break overrides gets keep-block-together for every section in print CSS; prior experience does **not** force a new page unless the operator set that policy.
2. **Persistence** — changing policies on Base Resume Content structure Save survives reload; JAR Job Resume shows the same structure policies (base as defaults) and print for that candidate/job reflects them without a separate job-only policy store.

## Boundaries

Does not emit print CSS or build React controls — those are sibling slices.

## Notes for planning

Estimate 2. Bang !!! — blocks later blockers.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1462-create-and-position-page-break`, child `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema`. Created at dispatch-parent.

## QA test manifest

1. Config tokens + keep-together defaults (incl. `prior_experience`): `tests/component/utils/test_config.py::TestAst1474PageBreakPolicyCatalog`
2. Normalize missing/blank → `avoid_split`; valid keep; unknown reject; hydrate soft-fill; ingest stamp: `tests/component/core/test_candidate.py::TestAst1474PageBreakPolicyNormalize`
3. GET catalog/`all_sections` page-break fields; soft-default invalid stored; PUT persist `page_break_before` / reject unknown: `tests/component/ui/api/test_api_candidate.py::TestAst1474PageBreakPolicyCatalogApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1474PageBreakPolicyCatalog \
  tests/component/core/test_candidate.py::TestAst1474PageBreakPolicyNormalize \
  tests/component/ui/api/test_api_candidate.py::TestAst1474PageBreakPolicyCatalogApi \
  -q
```

**Bible shasums** (`origin/sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema`):

* `docs/test-bible/core/candidate.md` `b81df1a8966686f2c0e43e046524d7ae6ed7f962`
* `docs/test-bible/utils/config.md` `b0d18955a55f03a407f45ca0d0b8830f2d974e85`
* `docs/test-bible/ui/api/api_candidate.md` `eb706279348f3de4ebb9279d0c811ae565b7fdc0`

### Comments

#### ada — 2026-08-25T00:16:30.713Z
`origin/sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema` @ `4aef54ff` · §9a clean

#### radia — 2026-08-25T00:08:58.022Z
[code-rubric] REVIEW (Commit: f150166d) wrong-parent sync on publish ref

#### betty — 2026-08-24T23:55:49.872Z
`origin/sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema` @ `f150166d` · schema tests ready

#### ada — 2026-08-24T23:06:03.748Z
`origin/sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema` @ `56eecd88` · plan published

---

_Implementation detail may live in git history on `origin/dev`._
