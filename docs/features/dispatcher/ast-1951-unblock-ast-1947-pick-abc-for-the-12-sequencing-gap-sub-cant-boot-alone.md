# AST-1951 — Unblock AST-1947: pick A/B/C for the #1/#2 sequencing gap (sub can't boot alone)

<!-- linear-archive: AST-1951 archived 2026-10-08 -->

## Linear archive (AST-1951)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1951/unblock-ast-1947-pick-abc-for-the-12-sequencing-gap-sub-cant-boot  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1946

### Description

[AST-1947](https://linear.app/astralcareermatch/issue/AST-1947) (catalog / resolver / settings cleanup) can't stay importable and green on its own, which its Notes for planning ask for. Katherine's plan is written and pushed; it is held at Plan Discuss on this one call.

Why: Scope removes `infer_brain_setting_from_legacy_model_code` (imported by `src/data/database.py` at load), adds a required `mode` argument to `resolve_model_brain` (four two-argument callers in `agent.py`, `api_admin.py`, `database.py`), and drops `tier["default_temperature"]` (read in `agent.py` and `api_admin.py`, including `GET /agents/models`, which AC 8 counts). Every repair lives in [AST-1948](https://linear.app/astralcareermatch/issue/AST-1948)'s files and needs the agent `mode` column only AST-1948 adds.

Need one answer — pick A, B or C:

* **A (Katherine recommends, no scope change):** AST-1947 and AST-1948 land as a pair. AST-1947's QA stays on the config and compat tests; the AC 8 endpoint count (98 ids) is checked on ftr after AST-1948 merges. Cost: `ftr/AST-1946-big-brain-openrouter` won't boot between the two merges.
* **B:** widen AST-1947 into AST-1948's call sites, using a placeholder agent mode until AST-1948 adds the column.
* **C:** repartition so AST-1947 is additive only; the caller-breaking removals move to AST-1948, with interim stored thinking/temperature values.

A goes straight to Plan Ready as written. B or C means a re-plan of AST-1947 (and a scope edit on AST-1948).

Reply here with A, B or C. The agents will do the paperwork and re-plan; you do not need to push anything. Move this to **Done** when answered.

Neither AST-1947 nor AST-1946 is assigned to you. AST-1947 stays with Katherine; AST-1946 stays In Progress with Chuckles.

### Comments

#### susan — 2026-10-03T02:29:03.964Z
A please

---

_Implementation detail may live in git history on `origin/dev`._
