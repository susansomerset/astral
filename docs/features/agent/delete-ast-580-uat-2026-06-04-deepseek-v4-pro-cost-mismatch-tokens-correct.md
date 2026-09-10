# AST-580 — UAT: 2026-06-04 deepseek-v4-pro cost mismatch (tokens correct)

<!-- linear-archive: AST-580 archived 2026-06-15 -->

## Linear archive (AST-580)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-580/uat-2026-06-04-deepseek-v4-pro-cost-mismatch-tokens-correct  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-569 — Timesheets for deepseek are inaccurate  
**Blocked by / blocks / related:** parent: AST-569

### Description

## Bug (parent UAT AST-569)

Susan **2026-06-05**: UTC **2026-06-04** `deepseek-v4-pro` — daily token totals match DeepSeek export (miss **22431**, output **9778**) but **cost still wrong**.

**Rows:** `a811f41e-617c-406d-876f-20e501852217`, `b2904570-f064-4a14-b16b-ef06c2159a99`

**Triage:** stored `calc_cost_*` reconciles to export per-token rates on `total_no_cache_input` + `total_output` (see parent `[check-linear]`). Open: which dollar surface disagrees (DeepSeek dashboard total, Admin **$ Total**, manual calc using `no_cache_live`+`no_cache_prompt`).

**Code:** `src/utils/cost_calculator.py`, `src/utils/config.py` (`DEEPSEEK_MODEL_PRICING`), `src/external/deepseek.py`, `src/ui/api/api_admin.py`, `src/ui/frontend/src/lib/timesheetCost.ts`

**Parent ftr:** `origin/ftr/ast-569-timesheets-deepseek-cost` @ `d9656be9` · local `dev` @ `5b96f9db`

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
