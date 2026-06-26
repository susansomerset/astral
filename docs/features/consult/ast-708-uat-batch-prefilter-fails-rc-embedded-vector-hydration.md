# AST-708 — UAT: batch prefilter fails RC embedded vector hydration

<!-- linear-archive: AST-708 archived 2026-06-23 -->

## Linear archive (AST-708)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-708/uat-batch-prefilter-fails-rc-embedded-vector-hydration  
**Status at archive:** Duplicate  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-700 — prefilter as batch process  
**Blocked by / blocks / related:** parent: AST-700

### Description

## What failed

Batch **prefilter** dispatch on **HOMEPAGE_READY** companies: LLM returns valid encoded lines (e.g. `000|RCD3|MPB3|USA3|...`) with `agent_performance.status = success`, but every company lands **WEBSITE_FOUND_RETRY** because grade-reason hydration errors:

```
ERROR src.core.roster: [prefilter_company_batch] grade reason hydration failed: No rubric criterion matching vector 'RC'
```

Susan fixed candidate `company_prefilter` rubric vectors (MP, US, etc.) in admin config. **RC** (Reality Check) is an **embedded/global** rubric vector present on every prefilter call — not stored per-candidate — and hydration only searches candidate rubric criteria.

## Expected

After batch prefilter agent success, each company receives independent pass/fail outcome and correct state transition (**PREFILTER_PASSED** / **PREFILTER_FAILED** or inflow equivalents). Grade reasons hydrate for **RC** and other embedded vectors without retrying the whole batch.

## Repro

1. Run app on `origin/dev` with [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process) two-phase prefilter landed.
2. Ensure **HOMEPAGE_READY** companies exist (via **fetch_website**).
3. Dispatch **prefilter** batch (10 companies).
4. Observe LLM success in logs with encoded lines containing `RC` grades.
5. Observe `grade reason hydration failed: No rubric criterion matching vector 'RC'` and all companies → **WEBSITE_FOUND_RETRY**.

## Parent AC (quoted inline)

> 3. Multiple companies in **HOMEPAGE_READY** can be claimed in one dispatch batch and evaluated in a **single** agent call; each company receives an independent pass/fail outcome and state transition matching today's prefilter semantics.

> 5. Retryable prefilter failures still land in **WEBSITE_FOUND_RETRY** (or equivalent holding state Susan confirms) rather than silent loss.

## Boundaries

* This bug does **not** change: **prefilter_company** rubric prompt, encoded decode shape, or link persistence semantics.
* Does **not** change **fetch_website** scrape phase.
* Does **not** add UI beyond fixing hydration for embedded vectors.
* Susan's proposed direction: `config.py` holds embedded-vector definitions (importance, code, title, rubric options); hydration checks those global codes before erroring — implementer confirms exact shape in plan.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
