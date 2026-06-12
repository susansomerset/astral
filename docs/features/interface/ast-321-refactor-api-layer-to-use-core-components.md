<!-- linear-archive: AST-321 archived 2026-06-03 -->

## Linear archive (AST-321)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-321/refactor-api-layer-to-use-core-components  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

The UI API layer (ui/api/) currently imports and calls src/data/database directly in most endpoint modules, violating our layer rules (ASTRAL_CODE_RULES SS 3.2, 3.3: "ui: core + utils. Never external. Never data.").

api_admin.py is exempt — admin endpoints are inherently cross-cutting and already acknowledged as a direct-access layer.

All other API modules need to route through their corresponding core module:

**api_candidate.py** — route through src/core/candidate.py

* database.save_candidate() — needs core wrapper
* database.clear_candidate_api_key() — needs core wrapper
* database.get_candidate() — already exists as candidate.get_candidate()
* do_task imported from src/external/anthropic — needs core wrapper (candidate artifact generation should be orchestrated by core)

**api_companies.py** — route through src/core/roster.py

* count_companies, get_active_trigger_states, get_company, list_companies, list_company_job_scans, save_company, update_company — need thin core wrappers in roster.py

**api_jobs.py** — route through src/core/tracker.py

* get_job, list_jobs, save_job — need thin core wrappers in tracker.py

**api_system.py** — route through appropriate core modules

* get_active_trigger_states, list_companies, list_company_job_scans — through roster.py
* count_jobs — through tracker.py
* These are inline imports inside functions (for nav badge counts); same rule applies.

### Comments

#### betty — 2026-05-11T01:25:41.319Z
**Review feedback resolved** (`f-resolve-linear`, Betty).

Radia’s thread had **fix-now 0**; no product changes required. Added **`## Resolution`** to the combined plan on **`dev-betty`** and published:

- **Branch:** `betty/ast-321-refactor-api-layer-to-use-core-components`
- **Doc commit:** `0e42dcdd` — `fix(AST-321): review feedback — resolution (0 fix-now)`

**Linear:** **Testing** (this workspace’s column for post-review acceptance per `list_issue_statuses` — maps to **User Testing** in `docs/ASTRAL_TEAM_WORKFLOW.md`). **Assignee:** Susan.

— Betty

#### betty — 2026-05-11T01:21:04.476Z
**Betty — `e-review-linear`-style pass** (Susan: Review Posted queue; formal skill §2 is Radia on **Tests Passed**, so this is a follow-up verification, not a state transition.)

**Diff:** `origin/dev...origin/betty/ast-321-refactor-api-layer-to-use-core-components` (tip `20a7c163`)

**Counts:** fix-now **0** · discuss **0** · advisory **1**

**Rubric / rules**
- **B2 (layer):** `rg` on `src/ui/api/*.py` shows **`src.data` only in `api_admin.py`** (documented exemption). `api_candidate` / companies / jobs / system routes go through core facades — matches plan + **ASTRAL_CODE_RULES** §3.3.
- **B1:** No new nested imports in the touched API slice beyond existing lazy patterns where applicable.
- **Plan fidelity:** Plan scope (roster/tracker/candidate + API thin wrappers) matches the diff footprint.

**Advisory**
- **H / testing:** Large surface in `api_candidate` + new core helpers — **`d-test-linear`** should exercise candidate save, artifact generation path, and at least one list endpoint per module touched.

— Betty

#### radia — 2026-05-11T01:15:55.534Z
## Radia code review (local git)

**Branch / baseline:** `refs/heads/radia/ast-321-refactor-api-layer-to-use-core-components` from Linear **does not exist** locally. Review used **`betty/ast-321-refactor-api-layer-to-use-core-components`** vs **`origin/dev`** (three-dot diff).

**Diff summary:** Adds **`docs/features/interface/ast-321-refactor-api-layer-to-use-core-components.md`** only — **no** `src/` or `ui/` changes vs `origin/dev`.

**Counts:** fix-now **0** · discuss **1** · advisory **1**

### Plan fidelity (doc-only)
- Staged rollout (companies → jobs → system → candidate) matches the ticket’s layering goal and calls out **`api_admin` exemption** consistently.
- Verification stage (`rg` on `src/ui/api` excluding admin) is a concrete acceptance check.

### ASTRAL_CODE_RULES (application code)
- **Not applicable** to this diff — there is no Python/TS delta here to grade §1–§3 against.

### Discuss
- Ticket is **Code Complete** in Linear, but the reachable delta on the local feature branch vs `origin/dev` is **plan-only**. If implementation already landed on `dev` under another branch name, consider updating **`gitBranchName`** / a ticket comment so the next reviewer does not hunt a ghost branch; if implementation is **not** merged yet, **Code Complete** may be premature for a code-review gate.

### Advisory
- Stage 4 mentions moving `do_task` usage out of UI — good — keep artifact/dispatch sequencing in **one** core entrypoint as the plan suggests to avoid split-brain ledger updates.

#### betty — 2026-05-11T00:30:59.793Z
**Built by Betty.** (`b-build-linear`)

- **Branch:** `betty/ast-321-refactor-api-layer-to-use-core-components`
- **Commit:** `20a7c163` — `feat(AST-321): route UI API through core facades (roster/tracker/candidate)`

Non-admin API modules no longer import `src.data`; `api_candidate` artifact generation lives in `core.candidate.run_candidate_artifact_generation`.

— Betty

#### betty — 2026-05-11T00:27:14.932Z
**Label review (build agent):** agree on all three — **conf-high**, **risk-HIGH**, **scope-MAJOR-CHANGE** match the plan (multi-blueprint + core facades + dispatch ledger moves).

— Betty (`b-build-linear`)

#### betty — 2026-05-08T22:08:22.879Z
**Plan posted** — `docs/features/interface/ast-321-refactor-api-layer-to-use-core-components.md`

GitHub: https://github.com/susansomerset/astral/blob/betty/ast-321-refactor-api-layer-to-use-core-components/docs/features/interface/ast-321-refactor-api-layer-to-use-core-components.md

**Self-assessment**
- **Scope:** `MAJOR-CHANGE` — All non-admin API blueprints plus new core facades on candidate/roster/tracker.
- **Conf:** `high` — Ticket lists concrete symbol routing per module.
- **Risk:** `HIGH` — Missed callsite or wrong ledger/task wiring breaks authenticated UI and dispatch records.

— Betty

---

# Plan: AST-321 — Refactor API layer to use core components

**Linear:** https://linear.app/astralcareermatch/issue/AST-321/refactor-api-layer-to-use-core-components  
**Feature branch:** `betty/ast-321-refactor-api-layer-to-use-core-components`

## Summary

Remove **all** direct `src.data` imports from Flask blueprints except `api_admin.py` (explicitly exempt). Each endpoint’s persistence and orchestration goes through **`src/core/`** facades (`candidate`, `roster`, `tracker`, and split helpers for system counts) so `ASTRAL_CODE_RULES.md` §3.3 holds: **ui → core + utils only**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add thin wrappers: `save_candidate_admin(...)`, `clear_candidate_api_key(...)`, artifact/dispatch path that owns `do_task` + ledger updates currently inlined in `api_candidate.py` | core |
| `src/core/roster.py` | Add wrappers re-exporting or wrapping: `count_companies`, `get_active_trigger_states`, `get_company`, `list_companies`, `list_company_job_scans`, `save_company`, `update_company` if not already present as roster-facing APIs | core |
| `src/core/tracker.py` | Add wrappers: `count_jobs`, `count_jobs_below_dispatch_score_floor`, `get_job`, `list_jobs`, `save_job`, `job_misses_dispatch_score_floor`, `list_jobs_below_dispatch_score_floor`, `score_floor_by_trigger_for_candidate` — only signatures the UI needs | core |
| `src/ui/api/api_candidate.py` | Delete `from src.data import database` and `from src.core.agent import do_task`; call core-only APIs | ui |
| `src/ui/api/api_companies.py` | Replace `from src.data.database import (...)` with `from src.core.roster import (...)` (or dedicated `core.companies` if you split — **pick one module** to avoid scatter) | ui |
| `src/ui/api/api_jobs.py` | Replace data imports with `src.core.tracker` (or roster where already mixed — keep **jobs** in `tracker` per ticket) | ui |
| `src/ui/api/api_system.py` | Replace inline `from src.data.database import ...` with core calls for nav badge counts; fix nested `src.core.agent` imports per **AST-384** after this lands if still lazy | ui |
| `src/ui/api/api_admin.py` | **No change** to layering rule (may still import `data`) | ui |

⚠️ **Decision:** Candidate artifact generation + `dispatch_ledger` / `do_task` sequence moves **verbatim logic** from `api_candidate.py` into `src/core/candidate.py` (or `src/core/candidate_artifacts.py` if file size triggers extract — **one** new file max unless Susan prefers single module).

## Stage 1: `api_companies.py` → roster

**Done when:** `api_companies.py` has zero `src.data` imports; all routes behave identically for list/detail/bulk/import flows in manual smoke.

1. In `src/core/roster.py`, for each function imported today in `api_companies.py` (`count_companies`, `get_active_trigger_states`, `get_company`, `list_companies`, `list_company_job_scans`, `save_company`, `update_company`), add a public function that calls the existing data-layer function internally (thin pass-through is OK in stage 1).
2. Update `api_companies.py` imports to pull those names from `roster` only.
3. Run Flask app import smoke: `python -c "from ui.server import app"`.

## Stage 2: `api_jobs.py` → tracker

**Done when:** `api_jobs.py` has zero `src.data` imports.

1. Mirror Stage 1 pattern in `src/core/tracker.py` for `get_job`, `list_jobs`, `save_job`, `job_misses_dispatch_score_floor`, `list_jobs_below_dispatch_score_floor`, `score_floor_by_trigger_for_candidate`.
2. Switch `api_jobs.py` imports to `tracker`.

## Stage 3: `api_system.py` counts → core

**Done when:** No `from src.data.database` inside `api_system.py` route bodies.

1. Add roster/tracker wrapper pair used by nav counts (`get_active_trigger_states`, `list_companies`, `list_company_job_scans`, `count_jobs`, `count_jobs_below_dispatch_score_floor`) behind **one** small function on `roster` or split per ticket text — follow Linear mapping: roster for company-side counts, tracker for job counts.
2. Replace inline imports with top-level `from src.core...` imports.

## Stage 4: `api_candidate.py` database + do_task

**Done when:** No `database.` references and no direct `do_task` import in `api_candidate.py`.

1. Move `save_candidate` / `clear_candidate_api_key` paths to `core.candidate` wrappers that call `database` internally.
2. Move the craft/artifact handler that uses `do_task`, `database.get_candidate`, `save_dispatch_ledger`, `update_dispatch_ledger` into core (single function e.g. `run_candidate_artifact_task(...)`) returning a dict the route can `jsonify`.
3. Route becomes: parse JSON → call core → return status codes unchanged.

## Stage 5: Verification

**Done when:** `rg "src\\.data|from src.data" src/ui/api --glob '!api_admin.py'` returns **zero** matches.

1. Repo-wide grep above.
2. Manual: create/update candidate, list companies watch list, list jobs in review, hit `/api/nav_config` or endpoints that used badge counts.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches all non-admin API blueprints plus new surface on `candidate`, `roster`, `tracker`.

**Conf:** `high` — Linear ticket lists concrete symbol routing per module.

**Risk:** `HIGH` — Wrong wrapper or missed callsite breaks authenticated UI flows and dispatch ledger integrity.

## Plan vs ASTRAL_CODE_RULES

§1.2 / §3.3: UI never imports `data` except exempt admin blueprint. Core may import `data` and `external`; move `do_task` usage out of UI into core.

## Review (stub — b-build-linear)

- **Branch:** `betty/ast-321-refactor-api-layer-to-use-core-components`
- **Implementation:** see Linear **Code Complete** comment for cherry-picked commit SHA on that branch.

## Resolution (2026-05-11 — f-resolve-linear, Betty)

**Radia `e-review-linear`:** fix-now **0** (see Linear thread). **Resolve pass:** no additional product changes required to clear review feedback.

Advanced to **User Testing** per `docs/ASTRAL_TEAM_WORKFLOW.md`. This section is doc-only; implementation SHAs remain on the feature branch from the **Code Complete** / **Built by Betty** comments.
