# AST-1575 — Rename ARTIFACT_CATALOG→ARTIFACT_CONFIG and hierarchical catalog keys

<!-- linear-archive: AST-1575 archived 2026-09-09 -->

## Linear archive (AST-1575)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1575/rename-artifact-catalogartifact-config-and-hierarchical-catalog-keys  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1568 — Implement patt.artifact.manage-catalog  
**Blocked by / blocks / related:** parent: AST-1568

### Description

## Susan UAT comment (verbatim)

[bug]

Please update the [config.py](<http://config.py>) and any current wiring to reflect the requested changes above.

## Referenced UAT asks (same thread)

1. Catalog keys use hierarchy from the existing `_data` path, e.g. `candidate.artifacts.base_resume`, `job.artifacts.cover_letter`, `candidate.context.strengths`.
2. Config block name is `ARTIFACT_CONFIG` (standard `_CONFIG` suffix), not `ARTIFACT_CATALOG` / `ARTIFACTS_CATALOG`.

## As-is

Landed pilot registers flat key `base_resume` under config block `ARTIFACT_CATALOG`, and current helpers/tests/wiring use that name and key.

## To-be

Config block is `ARTIFACT_CONFIG`; pilot catalog key is the hierarchical path form (at least `candidate.artifacts.base_resume`); `config.py` and current catalog helpers/tests/wiring match that naming.

## Proposed change (checklist)

- [X] Rename `ARTIFACT_CATALOG` → `ARTIFACT_CONFIG` in `src/utils/config.py` (docstring + block + asserts)
- [X] Pilot key `candidate.artifacts.base_resume`; remove flat `base_resume` catalog key (no alias)
- [X] `artifact_catalog.py` imports `ARTIFACT_CONFIG`; error prefix `unknown catalog key:`
- [X] Betty-owned tests/bible retarget (qa-fix / bug-repro) — engineer did not edit test tree

## Suggested engineer

Ada Lovelace (sibling AST-1573)

## Parent

AST-1568 — publish ref context: `origin/ftr/AST-1568-artifact-catalog`

### Comments

#### chuckles — 2026-09-02T20:07:06.359Z
[check-linear] User Testing — not on `origin/dev` yet; landed on `origin/ftr/AST-1568-artifact-catalog` only — parent prep-uat pushes `dev` when the epic rolls up (@susan)

#### susan — 2026-09-02T20:06:12.437Z
@chuckles Has this been pushed to origin dev?  I don't see the changes yet.

#### radia — 2026-09-02T19:48:09.511Z
[code-rubric] PROCEED (Commit: 7b96d9f8) hierarchical keys clean

#### betty — 2026-09-02T19:43:34.811Z
[bug-repro]
`origin/sub/AST-1568/AST-1575-artifact-config-hierarchical-keys` @ `a31a997c` · repro lands red, awaits fix

#### betty — 2026-09-02T19:40:40.612Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/artifact_catalog.md + tests/component/utils/test_artifact_catalog.py — broken test — AST-1573 scaffold asserts ARTIFACT_CATALOG / flat base_resume / unknown artifact type; must retarget ARTIFACT_CONFIG + candidate.artifacts.base_resume + unknown catalog key (and flat-key non-resolve) per plan-fix.

#### joan — 2026-09-02T19:40:38.259Z
[board-joan]  CANON: OK

Product-only rename (`ARTIFACT_CATALOG`→`ARTIFACT_CONFIG`) and hierarchical pilot key (`candidate.artifacts.base_resume`); no active statute names the old block or flat lookup shape. `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` still satisfied via `config.py` registry. Draft `patt.artifact.manage-catalog` Implementation §1 leaves key shape unspecified; OPEN QUESTIONS §1 already lists `ARTIFACT_CONFIG` as valid placement — UAT resolution belongs in product code, not a canon patch.

context_tokens≈12000

#### ada — 2026-09-02T19:39:27.020Z
`origin/sub/AST-1568/AST-1575-artifact-config-hierarchical-keys` @ `27f3f29ae827f276a04becd3ab12c8a6ed9b4f3f` · plan-fix ready

---

_Implementation detail may live in git history on `origin/dev`._
