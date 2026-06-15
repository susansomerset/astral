# AST-484 — Strengthen the relationships between lookup lists in the UI and live values in config

<!-- linear-archive: AST-484 archived 2026-06-15 -->

## Linear archive (AST-484)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-484/strengthen-the-relationships-between-lookup-lists-in-the-ui-and-live  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-346; related: AST-538; related: AST-470

### Description

## Purpose

Astral already treats `config.py` as the single source of truth for state machines, task keys, board registry, and UI manifests (Code Rules §2.1). In several places the product still maintains **parallel lookup lists**—hand-written TypeScript unions, duplicate “seed” templates, or UI-only option arrays—that can drift from the live config keys the backend validates against. When that happens, admins and candidates see choices the runtime will reject, or miss choices config already allows.

This feature closes that gap: **UI and admin lookup vocabulary should be derived from config keys** (or from small API payloads built from those keys at request time), not from separately curated seed lists. The outcome Susan should see is fewer “mystery” form options, and config edits that automatically flow to the surfaces that depend on them.

This is a **product-wide hygiene parent epic** under **Astral Foundation** (Boards work is iceboxed; config alignment applies across admin, candidate, roster, consult, and dispatch surfaces).

## Functional scope

* **Inventory and classify drift:** Produce a documented inventory of UI/admin surfaces that populate dropdowns, filters, toggles, or validation hints from lists that are not tied to config keys. Classify each as: already correct (API reads config), fixable by extending an existing manifest endpoint, or needs a new thin read API. Inventory lives on this parent (Description or linked doc Susan approves).
* **Config-key-driven lookups:** For each in-scope surface, options shown to the user must come from the authoritative config structure for that domain—e.g. state tuples (`BOARD_SEARCH_STATES`, `JOB_STATES`, `COMPANY_STATES`, `CANDIDATE_STATES`), dict keys (`TASK_CONFIG`, `BOARD_CONFIG` adopted keys), or manifests already built in config (`build_state_ui_manifest`, dispatch state options pattern).
* **No seeds, defaults, or fallbacks for allowed values:** Retire duplicate seed vocabulary entirely. UI/admin allowed-value sets come **only** from config keys or config-built manifests. No `_DISPATCH_TASK_SEED`-style parallel lists, no default field templates that introduce a second valid-key vocabulary, no silent fallbacks when config is missing — missing config is a **crash-worthy bug** (fail loud during dev/UAT).
* **Parent + one child per culprit:** After inventory, Chuckles creates **separate Backlog Enhancement child tickets** under this parent — **one ticket per identified culprit surface** — managed and dispatched one at a time. This parent holds the inventory, cross-cutting rules, and acceptance for the epic; children implement individual surfaces.
* **Frontend contract:** React must not hardcode parallel enums for values that config owns. Either consume an API manifest or treat server responses as the allowed set (with graceful handling when a stored row has a legacy value not in the current config).
* **Admin channel (in-scope examples):** Scheduled Actions and similar admin forms must not offer trigger states or entity states outside `JOB_STATES` / `COMPANY_STATES` (today partially correct via `/dispatch_tasks/state_options`; extend the same discipline anywhere still seed-driven).

## Lookup drift inventory (dispatch 2026-06-02)

| Surface | Authoritative config source | Disposition |
| -- | -- | -- |
| `GET /api/state_ui_manifest` | `build_state_ui_manifest()` | Already correct |
| `GET /api/admin/dispatch_tasks/state_options` | `JOB_STATES`, `COMPANY_STATES` keys | Already correct |
| `GET /api/nav_config` | `NAV_CONFIG` + candidate state resolution | Already correct |
| `database._DISPATCH_TASK_SEED` + `config._DISPATCH_TASK_TRIGGER_SEED` mirror | Should derive from `TASK_CONFIG` + state tuples only | **Fix v1** — child 1 |
| `GET /api/admin/dispatch_tasks/task_keys` form defaults | Currently merges TASK_CONFIG with dispatch seed (seed wins) | **Fix v1** — child 1 |
| Admin adhoc dispatch preview (`get_dispatch_row_or_seed_preview_meta`) | Dispatch seed templates | **Fix v1** — child 1 |
| `StateUiContext.tsx` `EMPTY` constant | Duplicates full manifest shape in TypeScript | **Fix v1** — child 2 |
| Board search UI option lists | `BOARD_CONFIG` / board states | **Defer** (Boards iceboxed) |

## Boundaries

* Does **not** implement [AST-470](https://linear.app/astralcareermatch/issue/AST-470/board-searches-pre-fill-criteria-json-from-board-config-examples) (criteria JSON pre-fill from board examples)—adjacent UX, separate ticket.
* Does **not** refactor `config.py` into a package ([AST-346](https://linear.app/astralcareermatch/issue/AST-346/refactor-configpy-into-a-config-package))—may benefit later but is out of scope here.
* Does **not** change business rules for dispatch, gaze, or ingest—only how allowed values are **surfaced** in UI/admin.
* Does **not** require debug-logging work ([AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)) unless a touched surface already has `debug=` paths and Susan adds that in a follow-on.
* **Boards channel:** Boards project is iceboxed; board-specific lookup fixes may be deferred to children if still needed later — epic scope is product-wide hygiene, not a boards-only slice.
* Must **not** break **G1** manifest pattern: `state_ui_manifest` remains the jobs/companies UI vocabulary; this work extends alignment, not a second parallel TS state machine.
* Code Rules §2.1 still applies: allowed value sets live in config; this feature enforces that relationship in the UI layer.

## Acceptance criteria

1. A written inventory (in the epic Description or a linked doc Susan approves) lists each in-scope lookup surface, its authoritative config source, and disposition (fix in v1 child / defer).
2. For every surface marked **fix in v1** (each child ticket), a user opening the relevant form or list sees only options that match the current config keys for that field (or sees a clear “legacy/unmapped” affordance for stored values no longer in config).
3. Adding a new key to an in-scope config tuple or dict (e.g. a new `JOB_STATES` value) does **not** require editing a separate frontend seed list for that surface to appear in the UI.
4. No regression: existing saved rows with valid states continue to display and save; API validation messages remain authoritative on submit.
5. Component tests for touched admin/candidate pages are updated so manifests/API mocks reflect config-driven options (Betty manifest pass as usual after implementation children exist).
6. One Enhancement child ticket exists per inventory culprit before dispatch of that surface’s fix.

## Dependencies and blockers

* [AST-379](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards) (boards epic) — **Done**; board search and `BOARD_CONFIG` primitives exist.
* [AST-471](https://linear.app/astralcareermatch/issue/AST-471/board-search-replace-enabledstatus-with-state-activeorinactiveorerror) (`board_search.state` workflow) — **Done**; canonical state column in place.
* [AST-522](https://linear.app/astralcareermatch/issue/AST-522/state-grouped-recommended-list-with-phase-scores-recommended-jobs-list) (recommended jobs manifest) — **Done**; precedent for config-built UI manifest.
* None blocking definition approval; implementation ordering follows inventory → child tickets → dispatch one at a time.

## Open questions

none.

## Decisions

* **Epic scope:** Product-wide hygiene epic under **Astral Foundation**; Boards iceboxed (Susan 2026-06-02).
* **Dispatch seed semantics:** No default values, no seeds, no fallbacks — drive allowed values from config only; missing config is crash-worthy (Susan 2026-06-02).
* **v1 delivery shape:** Inventory on this parent; **one Enhancement child ticket per identified culprit**; dispatch and UAT one surface at a time (Susan 2026-06-02).
* **Parent label:** This ticket is the **Parent** epic; children carry **Enhancement** (Susan 2026-06-02).

---

## Original brief

We are using "seed" lists for lookup values when it would be far better and cleaner to use the keys, themselves, from the config arrays, not from a separately maintained list.

### Comments

#### chuckles — 2026-06-03T00:28:37.982Z
## Manual test steps

1. **Restart** the app on local `dev` if it is already running.
2. **AST-549 — Dispatch admin:** Open **Scheduled Actions** (or admin dispatch task UI). Confirm **task_keys** / create-task defaults match live `TASK_CONFIG` + job/company states — no roster options that config does not allow. Create or preview an **adhoc** row for `select_job_page` (or roster trio) and confirm defaults match config, not a hidden seed template.
3. **AST-549 — API spot-check:** `GET /api/admin/dispatch_tasks/task_keys` — schedulable keys are config-derived; seed keys must not override config.
4. **AST-550 — State UI manifest:** Open **Jobs → Recommended**, **In Review**, and **Skipped**. Confirm sections/columns render after manifest load (brief loading OK); no crash on empty manifest error path. Confirm **Companies** watch/ignored/inactive lists and job/company modals still section rows correctly.
5. **AST-550 — Legacy row:** If you have a job in a state **not** in the current manifest, confirm it appears under a **legacy/unmapped** section (not silently dropped).
6. **Regression:** Saved rows with valid states still display and save; invalid submit still returns API validation errors.

`origin/ftr/ast-484-strengthen-lookup-config-ui` @ `1f967780` · local `dev` merged (§8). Restart app if running.

Reset: `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-06-03T00:20:25.892Z
@susan — **AST-550** **User Testing**; **`git.sh rollup AST-550`** failed: merge conflict **`docs/ASTRAL_TEST_BIBLE.md`** (sub @ `55695141` → **`origin/ftr/ast-484-strengthen-lookup-config-ui`**). **AST-549** already on ftr. Resolve on ftr, re-run rollup, then **prep-uat AST-484**.

— Chuckles

#### chuckles — 2026-06-03T00:13:42.173Z
@susan — **AST-484** orchestration paused (§6a). **AST-549** **User Testing**. **AST-550** **Code Complete** — Betty QA manifest on `origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback` @ `a67db974`; not **Tests Ready** yet (stage 7 headless runs interrupted). Resume: finish **qa-astral** on **AST-550**, then **test → review → resolve → rollup → prep-uat**. Reassign parent to Chuckles when ready.

— Chuckles

#### chuckles — 2026-06-02T23:30:24.142Z
[check-linear]

**Joan / rollup:** `git.sh` now resolves parent **`ftr/*`** from **`debug/epic-sessions/AST-484/manifest.json`** (`ftr/ast-484-strengthen-lookup-config-ui`) before `ls-remote ftr/AST-484*`. Re-ran **`git.sh rollup AST-549`** — already on **`origin/ftr/ast-484-strengthen-lookup-config-ui`** (idempotent). No `@susan` escalation; **AST-550** pipeline can continue on **`do-all-the-things`**.

— Chuckles

#### susan — 2026-06-02T23:07:18.296Z
@chuckles This should be an issue Joan is capable of understanding and resolving herself.  If she is looking too narrowly, update her skill and try again.  This is the entire reason Joan exists, so that I do not have to worry about this stuff.

#### chuckles — 2026-06-02T22:26:06.242Z
@susan — **AST-549** reached **User Testing**; **`git.sh rollup AST-549`** failed: `joan blocked: no ftr ref for parent AST-484`. Origin has **`ftr/ast-484-strengthen-lookup-config-ui`** but rollup resolves **`ftr/AST-484*`** (case/pattern mismatch). **AST-550** pipeline paused until rollup lands or git.sh/manifest lookup is fixed.

— Chuckles

#### chuckles — 2026-06-02T22:01:35.448Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-484 (parent) | ftr/ast-484-strengthen-lookup-config-ui |
| AST-549 | sub/AST-484/AST-549-retire-dispatch-task-seed |
| AST-550 | sub/AST-484/AST-550-remove-stateui-manifest-fallback |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `bc8dc9c9-e39f-40c6-82a4-af04978e55cd` | AST-484 (parent) | git |
| Ada | `1c4c2b41-e3a3-4cc0-b4c3-e25efd2558a8` | AST-549 | engineer |
| Betty | `207f9989-8bfc-4a6b-bafa-47a851bb38e7` | AST-549 | qa |
| Radia | `6cf4631e-ee90-4561-8310-92807447fd77` | AST-549 | review |
| Katherine | `79d3f118-f25d-479e-86e8-a8b0d6ed7078` | AST-550 | engineer |
| Betty | `0ed758a5-f9fd-4d4c-8147-e15c98acd55b` | AST-550 | qa |
| Radia | `9147e705-77be-4bf4-92c3-3f0b50353b5c` | AST-550 | review |

**Parent:** AST-484

**Sequencing:** AST-550 blocked by AST-549.

— Chuckles

#### chuckles — 2026-06-02T21:17:13.045Z
[check-linear]

Folded your inline Open-question answers into **Decisions** on the Description:

- **Product-wide** hygiene under **Astral Foundation** (Boards iceboxed)
- **No seeds / defaults / fallbacks** — config keys only; missing config = crash-worthy
- **Parent epic** — inventory here, then one **Enhancement** child per culprit; dispatch one surface at a time

**Open questions:** none. **Original brief** unchanged.

When you're happy, move **AST-484** to **Todo** (assign Chuckles) and I'll run inventory + child ticket backfill before dispatch.

— Chuckles

#### susan — 2026-06-02T20:45:55.137Z
@chuckles See my changes in the Description text, please.

#### chuckles — 2026-06-02T19:53:50.440Z
@susan — definition prepended on **AST-484** (Backlog). Please review the Description; Chuckles will not move this to Todo.

**Open questions (need your call):**

1. **Scope:** Product-wide epic vs **boards-first** slice under Astral Boards?
2. **Dispatch seed:** Retire seed as a lookup vocabulary, or keep for **defaults only** with trigger_state constrained to config state keys?
3. **Priority:** Which surfaces are must-fix in v1 after inventory (board searches, scheduled actions, other)?

When this looks right, move to **Todo** (and assign Chuckles if you want dispatch). No code in this pass.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
