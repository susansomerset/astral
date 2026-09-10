# AST-1503 — Carve-out agent-tables boot apply statute (gap for AST-1497)

<!-- linear-archive: AST-1503 archived 2026-09-09 -->

## Linear archive (AST-1503)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1503/carve-out-agent-tables-boot-apply-statute-gap-for-ast-1497  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1492 — updates to candidate are happening when we deploy  
**Blocked by / blocks / related:** parent: AST-1492

### Description

## What this implements

Land the canon carve-out fix-board named on AST-1497: update `astral.seed.agent-tables-in-repo-json` (and any tightly coupled seed statute wording) so boot repo-wins apply being disabled is an explicit kill-switch exception until a later ops/seed design — without weakening export / Revert-to-file / future explicit apply.

## Citations

Sibling AST-1497 plan-fix patch. `[board-joan] CANON: REVISE` on AST-1497. Statutes: `astral.seed.agent-tables-in-repo-json`, `astral.seed.operator-rows-stay-deleted`, `astral.seed.define-approved`.

## Scope

## Component scope

* Statute / canon file(s) for `astral.seed.agent-tables-in-repo-json` (under `docs/` / `canon/` as currently laid out) — modified: one-line boot-apply kill-switch carve-out.
* `docs/features/foundation/ast-842-database-updates-are-not-running-on-production-deployments.md` — modified only if the Bug: AST-1497 What must still hold / Proposed change must cite the carve-out after it lands.

## Technical scope

* Modified statute Statement/Guidance: boot `apply_repo_admin_json_at_startup` may be a no-op under the deploy kill-switch; export / Revert-to-file / future explicit apply remain; fail-loud apply elsewhere unchanged unless the statute already requires boot-only.

## Proposed change (make-fix)

- [X] `astral.seed.agent-tables-in-repo-json` records boot-apply kill-switch carve-out (Joan LANDED @ `cc2d4ef5`)
- [X] Export / Revert-to-file / future explicit apply remain intact in statute
- [X] Feature doc edit not required — statute Notes already cite § Bug: AST-1497
- [X] No product kill-switch work (AST-1497 owns that)

## Acceptance criteria

- [X] Active canon no longer requires unconditional startup repo-wins apply while the kill-switch is in force.
- [X] Export / Revert-to-file paths remain documented as intact.

## Boundaries

Does not implement product kill-switch code (AST-1497). Does not redesign seed/ops. Orphaned-bug fix-board REVISE → sibling gap.

## Notes for planning

Board What: astral.seed.agent-tables-in-repo-json — boot repo-wins apply disabled — record kill-switch carve-out until explicit ops/seed design.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1492-updates-to-candidate-are-happening-when-we-deploy`, child `sub/AST-1492/<child-segment>`.

### Comments

#### radia — 2026-08-26T16:27:04.970Z
[code-rubric] PROCEED (Commit: cc2d4ef5) canon carve-out clean

#### joan — 2026-08-26T16:03:51.498Z
[validate-plan fix] LANDED — astral.seed.agent-tables-in-repo-json boot-apply kill-switch carve-out recorded on origin/sub/AST-1492/AST-1503-carve-out-agent-tables-boot-apply-statute.

#### joan — 2026-08-26T15:56:49.052Z
[board-joan]  CANON: REVISE
What: astral.seed.agent-tables-in-repo-json — boot repo-wins apply disabled — record kill-switch carve-out until explicit ops/seed design
Copied from sibling AST-1497 board; this gap child is the canon carve-out slice.

---

_Implementation detail may live in git history on `origin/dev`._
