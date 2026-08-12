# AST-777 — Refactor database.py

<!-- linear-archive: AST-777 archived 2026-08-02 -->

## Linear archive (AST-777)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-777/refactor-databasepy  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** unassigned  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

`database.py` has grown to roughly six thousand lines and mixes runtime persistence, schema bootstrap, admin import plumbing, ticket-scoped migrations, and orphaned one-off utilities in one module. That blurs the "dumb persistence" contract Foundation expects and makes the data layer hard to navigate. This epic restores a single slimmed `database.py` tightly coupled to data tables (not core domain logic), clarifies layer bright lines in Code Rules, relocates non-runtime work to scripts, rewires callers that today depend on domain logic living in data, and sets acceptance criteria for the refactor without breaking deploy, bootstrap, or existing callers.

## Functional scope

* **Data-layer contract in Code Rules.** Extend `ASTRAL_CODE_RULES` with an explicit, durable definition of the data layer: runtime persistence and schema bootstrap only; no outcome branching, no domain decisions, no logging; header table inventory remains authoritative; migrations/backfills policy documented below.
* **Layer bright lines (Susan — for future dev work).**
  * `database.py` **(data):** SQLite access, CRUD, batch claim/get/clear by caller-supplied criteria or explicit entity IDs, compression/encryption on write/read, schema bootstrap. Reads and writes what callers specify — does not interpret score floors, pass/fail, or agent-response semantics.
  * `src/core/*` **(domain):** Orchestration and business rules — who qualifies for a batch, what the next state is, how to derive agent-response status, dispatch eligibility. Core decides; data persists.
  * `src/ui/api/*` **(HTTP):** Thin routes — auth, request parsing, call core, return JSON. No direct data imports; no duplicated domain rules (config-driven response shaping only, per Code Rules §3.2).
* **Explicit bootstrap (not lazy ensure).** Greenfield `CREATE TABLE` and additive column setup run via an explicit one-shot bootstrap invoked at server startup and from `setup_dev.sh` — not scattered lazy `_ensure_*_schema` on first connection per query path.
* **Runtime vs non-runtime separation.** Classify everything currently in `database.py` as runtime persistence versus non-runtime maintenance. Non-runtime moves out; runtime keeps the same outward semantics.
* **Migration and backfill home.** Bootstrap schema in data bootstrap module(s); completed ticket migrations archived under `scripts/migrations/`; operator maintenance scripts-only.
* **Single slimmed** `database.py`**.** One primary module organized by data table/entity family; shared internals factored; no multi-file package re-export.
* **Score-floor and status derivation (Option B — confirmed).** Core/dispatcher cherry-picks eligible entities; data assigns `batch_id` / locks explicit rows only. Core derives agent-response status before data insert.
* **Admin Copy Output preserved.** Orchestration in core (`table_copy_upsert.py`); persistence primitives in data.
* **Caller rewiring.** Every component in **Impact summary** updated per its mapped child below.

## Impact summary (research — components touched)

| Component | Current coupling to `database.py` | What must change |
| -- | -- | -- |
| `src/data/database.py` | Monolith: CRUD + lazy `_ensure_*` + inline ticket migrations + score-floor SQL + agent-status derivation + Copy Output upsert primitives | Slim and reorganize by table family; extract bootstrap; archive migrations; remove domain logic |
| `src/core/bootstrap.py` | First DB touch triggers lazy schema ensures | Explicit schema bootstrap before sync/scheduler |
| `src/ui/server.py` | Calls `bootstrap_runtime()` at startup | Bootstrap order gains explicit schema step |
| `scripts/setup_dev.sh` | Dev DB setup | Call explicit schema bootstrap (same path as server) |
| `src/core/dispatcher.py` | Passes `score_floor` into data claim; data filters | Option B: core pre-selects eligible IDs; data dumb claim |
| `src/core/tracker.py` | Score-floor delegates; `claim_job_batch(..., score_floor=…)` | Core-owned eligibility; dumb data claim |
| `src/core/roster.py` | `claim_company_batch(..., score_floor=…)` | Same Option B pattern |
| `src/core/agent.py` / `timesheets.py` | Data-side agent-response status derivation | Core derives status before persist |
| `src/core/table_copy_upsert.py` | Copy Output upsert helpers in data | Orchestration stays core; data helpers regrouped only |
| `src/core/*` (other) | Direct CRUD/batch — appropriate | Import surface may shift after child 7; no smuggled domain rules |
| `src/ui/api/api_admin.py` | Direct `database` imports — layer debt | Route through core wrappers; eligibility via core |
| `src/ui/api/api_jobs.py` | Score-floor filter via tracker → data | Core-owned filter; API calls tracker/core only |
| `src/ui/api/api_system.py` | `count_jobs_below_dispatch_score_floor` via tracker | Core-owned after relocation |
| `src/utils/logging.py` | Approved late-import only | **No change** |
| `scripts/migrations/` + prod sync | One-off imports | Receive archived blocks from `database.py` |
| `docs/ASTRAL_CODE_RULES.md` | Partial rules today | Child 1 |
| **Betty — test-bible + component tests** | Assert lazy ensure, inline migrations, data-layer score-floor | Child 8 — bible/manifest refresh after engineer children |

## Boundaries

* Does **not** change schema design, add tables, or alter product workflows — except relocating where rules execute.
* Does **not** replace SQLite, introduce an ORM, or split databases.
* Does **not** move batch-claim mechanism, zlib compression, Fernet encryption, or `logging.py` late-import.
* Does **not** split into multi-file `src/data/` package.
* Must **not** break Railway deploy, local dev bootstrap, or existing production DBs.

## Acceptance criteria

1. Code Rules documents data-layer scope, bright lines, bootstrap policy, migration archive location.
2. Inventory classifies every helper in current `database.py` — zero unclassified.
3. Ticket migrations archived; no orphaned runtime backfill entry points.
4. `database.py` table-centric; miscellany removed.
5. Explicit bootstrap at server startup / `setup_dev.sh` — no lazy per-query `_ensure_*`.
6. Score-floor and agent-response status in core (Option B).
7. Every impact-row component rewired per child mapping below.
8. Tests pass after child 8 Betty refresh.
9. Fresh and upgrading dev DBs open cleanly.

## Dependencies and blockers

none.

## Proposed subissues (dispatch order — `blockedBy` chain)

Eight children — one execution ticket per major impact cluster (Susan: table rows need matching subissues).

### Impact row → child

| Impact row(s) | Child |
| -- | -- |
| `docs/ASTRAL_CODE_RULES.md` + inventory appendix | **1** |
| `bootstrap.py`, `server.py`, `setup_dev.sh` | **2** |
| `scripts/migrations/` + inline `_apply_ast*` in `database.py` | **3** |
| `dispatcher.py`, `tracker.py`, `roster.py` (Option B claim) | **4** |
| `agent.py`, `timesheets.py` (status derivation) | **5** |
| `api_admin.py`, `api_jobs.py`, `api_system.py` | **6** |
| `database.py`, `table_copy_upsert.py` (slim + reorg) | **7** |
| Betty test-bible + `tests/component/data/**`, core/ui tests | **8** (Betty) |

### Child definitions

| # | Title (draft) | Assignee lane | Owns |
| -- | -- | -- | -- |
| **1** | Code Rules + `database.py` inventory | Dev (plan/doc) | `ASTRAL_CODE_RULES` bright lines; full helper inventory (**runtime** / **bootstrap** / **script-only** / **remove**). No runtime code moves. |
| **2** | Explicit schema bootstrap | Dev | Extract `_ensure_*` → explicit bootstrap module; wire `bootstrap_runtime()` + `setup_dev.sh`; remove lazy ensure from hot paths. |
| **3** | Archive ticket migrations | Dev | Move completed idempotent blocks to `scripts/migrations/`; bootstrap invokes greenfield-only remainder. |
| **4** | Score-floor Option B — dispatch claim rewiring | Dev | `dispatcher` / `tracker` / `roster`: core pre-selects eligible jobs/companies; data claim locks explicit set; remove score-floor interpretation from data. |
| **5** | Agent-response status derivation in core | Dev | Move `_derive_agent_status` logic to core (`agent`, `timesheets`); data insert stores caller-provided status fields. |
| **6** | Admin + jobs API — core wrappers | Dev (Katherine if UI-heavy) | `api_admin` routes through core (reduce direct `database` imports); `api_jobs` / `api_system` score-floor display via core after children 4–5. |
| **7** | Slim + reorganize `database.py` | Dev | Table-family reorg; shared internals; Copy Output primitive grouping; dead helper removal; stable import surface. **After** 2–6 land. |
| **8** | Test-bible + component test refresh | Betty | Rewrite obsolete `tests/component/data/**`, dispatcher/tracker/roster/admin bibles per landed behavior; QA manifest for regression pass. **After** child 7. |

`blockedBy`**:** 2→1, 3→2, 4→1, 5→1, 6→{4,5}, 7→{2,3,4,5,6}, 8→7.

## Open questions

none.

---

## Original brief

Propose a refactor of [database.py](<http://database.py>) to address the one-off helper scripts and other miscellany that have crept into this file.

Clarify the scope of this file in the ASTRAL_CODE_RULES, and specify where migration-type functions should live.

Begin by proposing in this definition what the scope and functionality ought to be for [database.py](<http://database.py>) so that it is not bogged down with functions not relevant to runtime processing.

Briefly describe the organization of the component's code, and how much, if any, explicit business logic must be present, vs. treating it as a fairly dumb component, as we do with externals.  Justify your recommendations, and prepare for debate before we move forward.

### Comments

#### chuckles — 2026-06-25T06:28:15.975Z
[check-linear] Discussion — eight children + **Impact row → child** mapping in Description (@susan)

— Chuckles

#### susan — 2026-06-25T06:26:00.925Z
Love the table, @chuckles , but it does seem like we are missing corresponding planned subissues to execute the work, right?

#### chuckles — 2026-06-25T06:21:39.063Z
[check-linear] Discussion — **Impact summary** table + Betty test note in Description (@susan)

— Chuckles

#### susan — 2026-06-25T06:19:06.271Z
@chuckles This is a huge ticket, I expect, because it isn't just database.py but rewiring the components that call it, sometimes rebalancing the owner of the business rules.

Please do the research and add a summary table to the description to itemize each component that will be impacted and a summary of what needs to be changed.

This is also going to make a lot of Betty tests obsolete.

#### chuckles — 2026-06-25T06:11:30.588Z
[check-linear] Discussion — five-child breakdown in Description **Proposed subissues** (@susan)

— Chuckles

#### susan — 2026-06-25T06:08:48.886Z
@chuckles What do propose for subissue breakdown? We have been getting into the habit of making overstuffed single-subissues lately.

#### chuckles — 2026-06-25T06:02:11.054Z
@susan

1. **Score-floor pattern:** Confirm Option B — core/dispatcher cherry-picks eligible jobs and data only assigns `batch_id` / locks explicit rows (no score-floor interpretation in `database.py`)?

— Chuckles

#### chuckles — 2026-06-24T02:52:58.062Z
@susan

1. **Lazy ensure vs explicit bootstrap:** Should greenfield `CREATE TABLE` / additive column migrations stay as lazy `_ensure_*_schema` on first connection, or move to an explicit one-shot bootstrap invoked from server startup / `setup_dev.sh` only?
2. **Monolith vs package:** Multi-file `src/data/` package with `database.py` as thin re-export, or single slimmed `database.py` with migrations extracted but CRUD still centralized?
3. **Completed ticket migrations:** After a ticket-scoped migration has run everywhere we care about, delete the idempotent block, archive under `scripts/migrations/`, or keep forever inside ensure for greenfield safety?
4. **Score-floor and status helpers:** Move dispatch score-floor eligibility and agent-response status derivation to core in this epic, or keep in data as documented exceptions?
5. **Line-count / split threshold:** Is ~1500 lines per file an acceptable planning default, or a different cap?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
