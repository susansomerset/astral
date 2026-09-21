# AST-1184 — Task config aliases via master_task_key

<!-- linear-archive: AST-1184 archived 2026-08-17 -->

## Linear archive (AST-1184)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1185; related: AST-1186

### Description

## Purpose

Meteorite GDL already reuses classic Do/Get execution (`grade_do` / `grade_get`) under different trigger states so prompts stay single-sourced. Because Admin grouping is keyed by one `agent_task` identity per task key, those shared hops cannot sit under **Meteorite Review** beside twin meteorite tasks without either duplicating prompt bodies or leaving meteorite Do/Get rows stuck under Gaze Review. This epic adds a first-class **task alias** contract in config — any alias identity for UI/dispatch/grouping declares `master_task_key` and resolves to that master for prompts and shared execution content — so operators can organize aliases into the right sections and trigger states without cloning task content, and without one-off hard-coded alias maps.

## Functional scope

* Introduce a general config-level task-alias contract: any TASK_CONFIG entry may be an alias by declaring `master_task_key` pointing at another live catalog key that owns prompts and shared execution content. Resolution is field-driven (alias → master) — not a one-off explicit link table for meteorite (or any other pair).
* Resolve aliases at runtime so invoking or scheduling an alias loads the master's prompts/content (clean alias: no prompt override on the alias), while the alias remains the identity operators see for that row.
* Alias entries carry their own pass/fail/error (and related orchestration) in config so different trigger tracks can share prompts without a meteorite outcome overlay. First consumers retire `METEORITE_GDL_OUTCOME_BY_TASK` for Do/Get.
* Allow aliases to participate in dispatch with their own trigger states (and related admin defaults) so the same master prompts can be claimed from different input states without inventing a parallel duplicate task body.
* Allow each alias to have its own Admin grouping/section membership (via its own `agent_task` identity) so aliases can sit under Meteorite Review (or any section) while the master stays under Gaze Review — without replicating prompts.
* Ship the first concrete consumers: `meteorite_grade_do` → `grade_do`, `meteorite_grade_get` → `grade_get`; retarget meteorite dispatch rows to those alias keys; place alias catalog rows under the meteorite review grouping once **AST-1183** exists (or under the live Job Review / Meteorite Review name at land time).
* Keep Admin/task-key catalogs honest: aliases appear as selectable task keys wherever task keys are listed; resolution to master is backend/config behavior, not a hidden UI-only rename.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — alias/`master_task_key` literals and resolve helpers live in config; callers read config, do not hardcode alias maps in UI or core.
  * `pattern.layers.import-discipline` — resolve in utils/config; core/UI consume the resolver; no reverse imports.
* **New patterns proposed**
  * `pattern.config.task-alias` (proposed) — any TASK_CONFIG identity may declare `master_task_key`; runtime and Admin resolve prompts/shared content to the master while preserving the alias as the dispatch/UI key; alias may own distinct orchestration outcomes. **Archie approval required before implementation depends on this shape.**
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — alias pointers and alias-owned orchestration live as config literals.
  * `astral.standards.no-hardcoded-sets` — no parallel one-off alias tables in React or core outside the `master_task_key` contract.
  * `astral.seed.agent-tables-in-repo-json` — alias `agent_task` rows (grouping identity) ship in repo seed JSON; prompts come from the master's row (no override).
  * `astral.agent.do-task-delegation` — alias invocation still goes through `do_task` / consult using resolved master content.
  * `astral.standards.names-not-ticket-ids` — alias keys are domain names (`meteorite_grade_do` / `meteorite_grade_get`), not ticket-scoped strings.
  * `astral.standards.in-scope-only` — do not take Gaze/Meteorite section rename (**AST-1183**), UI hardcode audit (**AST-1185**), or `meteorite_email` rename (**AST-1182**).
  * `astral.standards.debug-contract-gated` — if touched `debug=` consult/agent paths change for alias resolution, keep Style D found/recorded detail.
  * `astral.standards.no-cross-contamination` / `astral.layers.import-direction` — honor layer bounds on resolve call sites.

## Boundaries

* Does **not** own Gaze Review / Meteorite Review section rename or meteorite membership reshuffle (**AST-1183**) — only supplies alias identities that can be grouped; section names come from that sibling or current seed.
* Does **not** own the UI hardcode / alphabetical dropdown verification pass (**AST-1185**) — this epic makes aliases real in config/runtime; that sibling confirms dropdowns and grouping surfaces stay data-driven.
* Does **not** rename `parse_meteorite_email` → `meteorite_email` or change AI payloads (**AST-1182**).
* Does **not** fold evaluate_meteorite tests/statutes (**AST-1186**).
* Does **not** invent full twin TASK_CONFIG clones (prompts + schemas copied) for Do/Get — that is the anti-goal; aliases share master prompts via `master_task_key` with no override.
* Does **not** keep `METEORITE_GDL_OUTCOME_BY_TASK` for Do/Get once aliases own meteorite pass/fail/error (overlay retirement is in scope for those hops).
* Does **not** retire `meteorite_like` / `meteorite_upshot` / `evaluate_meteorite` twins unless Susan explicitly expands scope (those already have distinct keys and can group under Meteorite Review without aliases).
* Does **not** change classic Gaze Review dispatch keys for vetted-company Do/Get (`grade_do` @ `PASSED_JD`, `grade_get` @ `PASSED_DO`).

## Acceptance criteria

* Config declares a general alias contract: any entry may set `master_task_key` to a live non-alias master; a resolve helper returns the master for prompt/content lookup and returns the key unchanged when not an alias — without a one-off meteorite-only link map.
* Alias entries for first consumers carry their own pass/fail/error (and related orchestration); `METEORITE_GDL_OUTCOME_BY_TASK` no longer supplies Do/Get meteorite outcomes.
* Invoking or dispatching `meteorite_grade_do` / `meteorite_grade_get` executes the master's prompts/content (no alias prompt override); operators do not maintain a second prompt body for that hop.
* Meteorite dispatch rows for Do/Get use the alias task keys with meteorite trigger states; classic Gaze rows continue to use `grade_do` / `grade_get`.
* Alias identities have `agent_task` grouping metadata that can place them under Meteorite Review (or the live meteorite section name) independently of the master's Gaze Review grouping.
* Admin task-key listings that are config/DB-driven include the new alias keys (alphabetical / catalog behavior refinements remain **AST-1185**).
* Editing the master's prompts changes what the alias runs; the alias has no divergent prompt row.
* If backend `debug=True` paths for these hops are touched: Style D index headers show found/recorded detail for the alias identity (and resolution to master is visible in detail when useful); no new ungated debug noise.

## Dependencies and blockers

* Related intake: **AST-1181** (Backlog; out of scope for this define — sibling bullets live on **AST-1182**–**AST-1186**).
* Soft awareness (not Linear blockedBy): **AST-1183** owns Meteorite Review section naming — alias seed grouping should use whichever section name is live when this lands (Job Review today; Gaze/Meteorite Review after 1183).
* Soft awareness: **AST-1054** / **AST-1055** established shared Do/Get + meteorite twins and `METEORITE_GDL_OUTCOME_BY_TASK`; this epic replaces shared-key meteorite Do/Get dispatch with aliases and retires the Do/Get overlay entries.
* Sibling Discussion tickets **AST-1182**, **AST-1183**, **AST-1185**, **AST-1186** are adjacent scope only; none block this definition.

none as Linear blockedBy.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Task alias config contract + resolve helpers - Ada**

Owns the general config contract: any entry may declare `master_task_key`, validation that masters exist and are not aliases (no alias chains), resolve helpers for prompt/content lookup, and first-consumer alias entries `meteorite_grade_do` / `meteorite_grade_get` with their own pass/fail/error (no one-off link map). Does **not** rewire consult/agent call sites (sibling #2) or seed/retarget meteorite rows (sibling #3).
**Citations:** `pattern.config.config-block`; proposed `pattern.config.task-alias`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.names-not-ticket-ids`.

#### 2!: **Runtime alias resolution + retire Do/Get overlay - Hedy**

After #1: honor alias → master resolution wherever prompts/shared content are looked up; run alias dispatch keys with alias-owned orchestration; remove `METEORITE_GDL_OUTCOME_BY_TASK` use for Do/Get. Does **not** author the config contract (sibling #1) or seed/retarget meteorite rows (sibling #3).
**Citations:** `pattern.layers.import-discipline`; `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`; `astral.standards.no-hardcoded-sets`.

#### 3: **Meteorite Do/Get alias seed + retarget dispatch - Katherine**

After #2: add alias `agent_task` identities (grouping under Meteorite Review / live section; prompts from master — no override), retarget `METEORITE_DISPATCH_TASKS` Do/Get rows to `meteorite_grade_do` / `meteorite_grade_get`, and keep fixtures/seed consistent. Does **not** invent the resolve helpers (siblings #1–#2) or own the UI hardcode audit (**AST-1185**).
**Citations:** `astral.seed.agent-tables-in-repo-json`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`.

**New patterns:** Child #1 introduces proposed `pattern.config.task-alias`; children #2–#3 consume it once Archie approves.

**Monolith check:** Functional scope has 7 capabilities; 3 children span config contract, runtime resolve + overlay retirement, and first-consumer seed — intentional layer split.

---

## Original brief

From AST-1181:

* Support task aliases in task config, where we add a `master_task_key` to the real task in config, but the alias can be used in the UI for different trigger states (instead of duplicating and making prompt management insane) and most importantly, organized under different groupings/sections so they can all sit together without replicating task content or logic

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1184 (parent) | ftr/AST-1184-task-config-aliases-via-master-task-key |
| AST-1220 | sub/AST-1184/AST-1220-task-alias-config-contract-resolve-helpers |
| AST-1221 | sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay |
| AST-1222 | sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch |
| AST-1269 | sub/AST-1184/AST-1269-uat-alias-agent-task-rows-not-seeded-on-startup |

**Epic worktree:** `astral-AST-1184/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/a8481c836229f65f229e2b06ada96c47/a5a6f8e4-aa44-4290-9b9d-828c170ef0dd/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/a8481c836229f65f229e2b06ada96c47/0782dd7e-4f60-4369-9c52-cb438d5802da/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/a8481c836229f65f229e2b06ada96c47/6b51dcb4-404b-4b84-a259-29c4be10bb9b/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/268e59ce-8ece-4ad5-a454-2ab9edd5322b/store.db` |
| Radia | review | `/home/susan/.cursor/chats/a8481c836229f65f229e2b06ada96c47/14dea759-d62b-444b-933e-823d78b357e7/store.db` |

### Comments

#### chuckles — 2026-08-08T00:27:29.921Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1269** | Restored grouping-only `meteorite_grade_do` / `meteorite_grade_get` rows in `data/admin/agent_task.json` (Meteorite Review; empty prompts). Re-applied after `code(AST-1252)` wiped them from the admin seed; confirmed present on current `origin/dev`. |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1269** — _alias agent_task rows not seeded on startup_
- **Issue reported:** After server startup, `meteorite_grade_do` and `meteorite_grade_get` did not appear as seeded `agent_task` rows (config had the aliases; seed JSON did not).
- **Should now:** On boot (and Revert-to-file), current `agent_task` rows exist for both alias keys under Meteorite Review; prompts stay on the masters.
- **Quick check (this fix only):**
  1. Deploy / start from current `origin/dev` (Railway staging or local boot that applies `data/admin/agent_task.json`).
  2. Inspect current `agent_task` rows (Admin Task Prompts / Manage Tasks or DB) for `meteorite_grade_do` and `meteorite_grade_get`.
  3. Confirm both keys are present as current rows under Meteorite Review (empty prompts).

Local `dev` merged via prep-uat (`994915ff`). Staging should reflect the seed restore above.

— Chuckles

#### chuckles — 2026-08-08T00:09:54.490Z
Confirmed on `origin/dev`: `meteorite_grade_do` / `meteorite_grade_get` are in `TASK_CONFIG` (and `METEORITE_DISPATCH_TASKS`), but they are **absent** from `data/admin/agent_task.json`. AST-1222 did seed those grouping rows; later `code(AST-1252)` dropped them from the admin seed file. Startup only applies repo `agent_task.json` (repo-wins), so the server will not create those catalog rows. Needs a Bug / `[fix]` restore of the alias `agent_task` rows (not a config-only fix).

— Chuckles

#### susan — 2026-08-08T00:07:49.365Z
@chuckles The aliases need to be seeded to the agent_task table, but they are not seeding from the server startup.

#### chuckles — 2026-08-06T09:20:17.775Z
[refresh-ftr] blocked: merge origin/dev into ftr/AST-1184-task-config-aliases-via-master-task-key

**@Betty White** (bible / test-tree / fixtures):
- `docs/test-bible/core/repo_admin_json.md`
- `docs/uat-fixtures/AST-756/expected-agent_task.json`
- `tests/component/core/test_repo_admin_json.py`

**@Katherine Johnson** (product / seed):
- `data/admin/agent_task.json`

Resolve on epic worktree / astral-tests as appropriate, land fixes onto `origin/ftr/AST-1184-task-config-aliases-via-master-task-key`, then Chuckles will re-run refresh-ftr.

— Chuckles

#### chuckles — 2026-08-06T02:36:37.554Z
@susan — open questions before Todo:

1. Confirm first alias keys and masters: `meteorite_grade_do` → `grade_do`, `meteorite_grade_get` → `grade_get`?
2. Alias-owned pass/fail/error (retire `METEORITE_GDL_OUTCOME_BY_TASK` for Do/Get) vs keep overlay?
3. Alias `agent_task` grouping-only (prompts from master) for v1, or allow prompt overrides?
4. Confirm `master_task_key` on the **alias** pointing at the master (not the reverse).

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
