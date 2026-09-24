# AST-1716 — Unblock AST-1713: AC2 consult grep vs land enrich import

<!-- linear-archive: AST-1716 archived 2026-09-24 -->

## Linear archive (AST-1716)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1716/unblock-ast-1713-ac2-consult-grep-vs-land-enrich-import  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1711

### Description

AST-1713 is stopped at Plan Discuss. Acceptance criterion 2 requires `rg -n consult src/core/meteorite.py` to print nothing. After the stage invoke is deleted, `land_meteorite` still late-imports `enrich_meteorite_land_packet` from `src.core.consult`. That function's only caller is land, and the body uses consult-private helpers (`_resolve_company_job_id`, `_hold_log_batch`), so it cannot move into `meteorite.py` as a cut-paste.

Scope only deletes the stage-meteorite invoke and says not to retarget scrape or land `SCRAPE_ERROR` writes. Leaving the import fails AC2. Deleting it breaks land. Moving enrich plus those helpers is a different capability than saving the Ruth row.

The earlier gap (meteorite columns `job_title` and `employer_name` on insert) is already on AST-1713 Scope. Do not re-decide that.

Pick one, reply on this ticket, and move this ticket to **Done**:

A. Narrow AC2 so `land_meteorite` may keep `from src.core.consult import enrich_meteorite_land_packet`. Stage and inbox ingest must still not import consult.

B. Add to AST-1713 Scope: relocate `enrich_meteorite_land_packet` and the consult-private helpers it needs, so `meteorite.py` has no consult import. Do not retarget `SCRAPE_ERROR` writes.

Neither AST-1713 nor AST-1711 is assigned to you. Hedy stays on the child. Chuckles stays on the parent. Agents will amend the ticket from your answer. You do not need to push.

### Comments

#### chuckles — 2026-09-19T23:23:56.038Z
Option B. Added to AST-1713 Scope: relocate `enrich_meteorite_land_packet` and the consult-private helpers it needs (`_hold_log_batch`, `_resolve_company_job_id`) so `meteorite.py` has no consult import. `qualify_meteorite` still calls `_resolve_company_job_id`. `_land_scrap_body` is already in `meteorite.py`. Scrape and land `SCRAPE_ERROR` writes are not retargeted. Hedy stays on AST-1713.

#### chuckles — 2026-09-19T23:23:31.765Z
[check-linear] Done — Option B

#### susan — 2026-09-19T23:20:57.062Z
@chuckles Option B, please.

---

_Implementation detail may live in git history on `origin/dev`._
