# AST-1532 — Put the list of loadable previous tasks to a 5 line scrollable selection box, filtered on the selected candidate and selected task_key in the dropdown.

<!-- linear-archive: AST-1532 archived 2026-09-09 -->

## Linear archive (AST-1532)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1532/put-the-list-of-loadable-previous-tasks-to-a-5-line-scrollable  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Agent Ad Hoc import list from [AST-1439](https://linear.app/astralcareermatch/issue/AST-1439/add-import-agent-data-to-agent-ad-hoc) / AST-1451–1452 returns every `agent_data` batch with no filter or cap, so the table dominates the page and buries the prompt editors. Operators need a short, scrollable picker of recent runs for the **selected candidate** and **selected task key**, newest first, so Load stays one click away without scrolling through the whole history.

## Functional scope

* **Scoped recent runs:** The import picker shows only runs that match the currently selected candidate and (when a catalog task key is chosen) the selected task key, ordered by `created_at` descending, capped at the last 10 matches.
* **Compact scrollable picker:** The picker is a roughly five-row-tall scrollable selection surface (not an unbounded full-page table), so the prompt editors stay reachable without paging through a long list.
* **Load behavior unchanged:** Selecting a row and Load still fills the seven editors from the existing batch payload, with the same dirty-confirm and entity restore behavior already shipped.
* When no candidate is selected, the picker is empty. When a candidate is selected but Task Key is “No Task,” the picker shows the last 10 runs for that candidate across task keys. Task-key match treats a stored `adhoc-<key>` as the same catalog key (one leading `adhoc-` stripped for comparison).

## Component scope

* `src/utils/config.py` — **modified** — named literals for import-list cap (10) and visible row count / picker height (5); no magic numbers in UI or SQL.
* `src/data/database.py` — **modified** — scoped batch list query (candidate + optional task_key, newest first, limit).
* `src/core/agent.py` — **modified** — pass filters/limit through `list_agent_data_runs`; keep debug found→recorded on the returned set.
* `src/ui/api/api_admin.py` — **modified** — `GET /api/admin/adhoc/runs` accepts candidate/task filters and returns the capped list.
* `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` — **modified** — refetch on candidate/task change; replace unbounded table with five-line scrollable selection chrome; keep Load wiring.

## Technical scope

* `src/utils/config.py` — new named keys (UI_CONFIG or adjacent config block) for max import runs (10) and visible picker rows (5); served or imported so API and React share the same caps.
* `src/data/database.py` — extend or replace the unfiltered `list_agent_data_batches` path with a filtered list: join `dispatch_ledger` on `batch_id` for `candidate_id`, optional `task_key` match including `adhoc-` prefix equivalence, `ORDER BY created_at DESC`, `LIMIT` from config; still one row per `batch_id` with the same metadata fields.
* `src/core/agent.py` — `list_agent_data_runs` accepts the same filter/limit kwargs, delegates to data, and when `debug=True` emits Style D found→recorded only for rows actually returned.
* `src/ui/api/api_admin.py` — `adhoc_runs` reads `candidate_id` / `task_key` query params (and uses config limit), still `@require_admin`, still JSON array of `{batch_id, created_at, entity_id, task_key}`.
* `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` — refetch `/api/admin/adhoc/runs` when `selectedId` or `taskKey` changes (pass those query params); constrain the picker container to ~five visible rows with overflow scroll; preserve row select + Load / confirmLoad behavior.

## Architectural definition

**Patterns to reuse**

* [`pattern.ui.admin-endpoint`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>) — extend existing admin `GET /adhoc/runs`; keep auth and thin API shape.
* [`pattern.ui.shared-button-roles`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.shared-button-roles.md>) — Load / confirm controls stay on existing `.btn` roles (no new button family).

**New patterns proposed:** none

**Applicable statutes**

* [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — cap and visible-row counts live in config, not inline magic numbers.
* [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — same; 5 and 10 are named constants.
* [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>) — list debug remains `debug=True` only, found→recorded per returned row.
* [`astral.standards.database-header-inventory`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>) — any new/changed `agent_data` helper stays on the header inventory line.
* [`astral.standards.data-raises-caller-logs`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>) — data layer raises; no logging in the query helper.
* [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — only the listed files; no Save As / Preview / production `do_task` rewrites.
* [`astral.idioms.require-auth-on-protected-endpoints`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>) — keep `@require_admin` on `/adhoc/runs`.
* [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — filter/limit resolved in API/data; React renders the capped list.
* [`astral.ui.frontend-file-placement`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>) / [`astral.ui.naming-conventions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.naming-conventions.md>) — page stays under existing admin Ad Hoc placement/names.
* Universal active set (pipeline/git/roles) applies to how this epic is planned and merged — including [`orch.pipeline.plan-is-bible`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/orchestration/pipeline/orch.pipeline.plan-is-bible.md>), [`orch.git.flow-direction-inviolable`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/orchestration/git/orch.git.flow-direction-inviolable.md>), [`orch.git.ftr-sub-topology`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/orchestration/git/orch.git.ftr-sub-topology.md>), [`orch.git.one-epic-worktree-per-parent`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/orchestration/git/orch.git.one-epic-worktree-per-parent.md>), [`orch.roles.betty-owns-test-tree`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/orchestration/roles/orch.roles.betty-owns-test-tree.md>), and the other active `tier: universal` statutes in `canon/statutes/README.md`.

## Acceptance criteria

1. With a candidate selected and a task key selected, the Ad Hoc import picker shows at most 10 rows, all matching that candidate and that task key (including stored `adhoc-<task_key>`), newest `created_at` first.
2. The picker viewport shows about five rows at a time and scrolls within the capped set; the prompt editor tabs remain reachable without scrolling past a long unfiltered table.
3. Changing candidate or task key refreshes the picker to the new filter; empty candidate → empty picker; candidate + empty task key → last 10 runs for that candidate.
4. Load on a selected row still populates editors from `GET /api/agent_data/<batch_id>` with existing dirty-confirm and entity restore; Save As / Preview / Test contracts are unchanged.
5. When backend debug is on for the runs list, debug output covers only the filtered returned rows (found→recorded), not the full unfiltered history.

## Open questions

none

## Proposed child tickets

#### 1!: **Scoped adhoc runs list API - Ada**

Owns config literals for cap (10) and visible-row count (5), data/query filter via `dispatch_ledger.candidate_id` + task_key/`adhoc-` equivalence, core `list_agent_data_runs` kwargs + debug on the returned set, and `GET /api/admin/adhoc/runs` query params. Does not own React chrome (sibling #2).
**Citations: **`pattern.ui.admin-endpoint`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.debug-contract-gated`; `astral.standards.database-header-inventory`; `astral.idioms.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`
**Scope: **`src/utils/config.py` (named cap/visible-row keys); `src/data/database.py` (filtered limited batch list); `src/core/agent.py` (`list_agent_data_runs` filters + debug); `src/ui/api/api_admin.py` (`adhoc_runs` query params + config limit).
**Estimate: 2**

#### 2: **Compact filtered import picker UI - Hedy**

Owns Agent Ad Hoc picker chrome only: pass `candidate_id` / `task_key` into the runs GET on candidate/task change, render a ~five-row scrollable selection surface over the capped list, keep existing Load / confirmLoad / row selection. After #1. Does not change API contracts beyond consuming sibling #1’s query params.
**Citations: **`pattern.ui.shared-button-roles`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.standards.no-hardcoded-sets` (read visible-row / height from config)
**Scope: **`src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` (refetch with filters; five-line scrollable picker; preserve Load wiring).
**Estimate: 2**

---

## Original brief

The list of previous runs is loooooong.  Just give me a scrollable list with the last 10 runs in descending order by created_at so that I don't have to scroll 18 times to get to the prompt editing components.

### Comments

#### chuckles — 2026-08-29T22:08:41.340Z
AST-1535 REVIEW — Joan needs plan discuss on ui_config URL (/api/ui_config).

#### chuckles — 2026-08-29T21:28:46.815Z
AST-1534 REVIEW — Radia: AST-1537 tests/bible smuggled on publish ref; recalling Ada for resolve-child cleanup.

---

_Implementation detail may live in git history on `origin/dev`._
