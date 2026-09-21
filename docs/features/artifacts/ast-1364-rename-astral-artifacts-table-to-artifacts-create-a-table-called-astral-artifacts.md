# AST-1364 — Rename astral_artifacts table to artifacts (Create a table called astral_artifacts)

<!-- linear-archive: AST-1364 archived 2026-08-31 -->

## Linear archive (AST-1364)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1364/rename-astral-artifacts-table-to-artifacts-create-a-table-called  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1340 — Create a table called astral_artifacts  
**Blocked by / blocks / related:** parent: AST-1340

### Description

## Susan comment (verbatim)

[bug] So sorry, Chuckles!  I meant for the table to be named "artifacts", not "astral_artifacts" because we don't have that prefix for job or company, etc.

## As-is / to-be

* **As-is:** The versioned artifact store table is named `astral_artifacts`.
* **To-be:** The table is named `artifacts` (no `astral_` prefix), consistent with `job` / `company` and other entity tables.

## Suggested engineer

Ada Lovelace (owned AST-1352 table + current-flag writers; AST-1353 Save wire may need call-site updates after rename).

## Proposed change (checklist)

- [X] Header inventory lists `artifacts` with `artifact_uuid` PK
- [X] `_ensure_artifacts_table` creates/renames from `astral_artifacts`; index `idx_artifacts_entity_type_current`
- [X] Public API `save_artifact` / `get_current_artifact` / `list_artifacts` (no `*_astral_artifact*` aliases)
- [X] Core `snapshot_saved_base_resume_artifact` + API Save wire updated
- [X] Product `src/**` clear of legacy table/API names (migration strings only in ensure)

### Comments

#### radia — 2026-08-14T20:01:32.371Z
[code-rubric] PROCEED (Commit: bba0a29b) rename artifacts; clean sub on ftr

#### betty — 2026-08-14T19:56:34.745Z
[bug-repro]
`origin/sub/AST-1340/AST-1364-rename-astral-artifacts-to-artifacts` @ `59544b84` · repro lands red, awaits fix

#### betty — 2026-08-14T19:54:41.476Z
[board-betty] TESTS: REVISE
What: docs/test-bible/data/database/astral_artifacts.md (+ core/candidate.md, ui/api/api_candidate.md) — broken tests — TestAst1352AstralArtifacts / TestAst1353* / confest `_astral_artifacts_schema_ensured` still call save_astral_artifact / astral_artifact_uuid / snapshot_saved_base_resume_astral_artifact; rename product symbols will AttributeError until Betty retargets.

#### joan — 2026-08-14T19:54:29.157Z
[board-joan]  CANON: OK

No active statute or approved pattern codifies the `astral_artifacts` table/API names. The patch updates `database.py` header inventory per `astral.standards.database-header-inventory` (conforming — no statute text change). `astral.debug.no-repo-root-artifacts-dir` governs repo-root filesystem paths, not the SQLite table name `artifacts`. Proposed `pattern.data.versioned-current-row` was never cataloged; nothing to amend in `canon/patterns/**`.

context_tokens≈12000

#### ada — 2026-08-14T19:53:30.131Z
`origin/sub/AST-1340/AST-1364-rename-astral-artifacts-to-artifacts` @ `bedaacb5` · rename plan patched

---

_Implementation detail may live in git history on `origin/dev`._
