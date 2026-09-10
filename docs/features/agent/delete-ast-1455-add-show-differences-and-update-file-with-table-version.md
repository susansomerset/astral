# AST-1455 — Add "Show Differences" and "Update file with table version"

<!-- linear-archive: AST-1455 archived 2026-09-09 -->

## Linear archive (AST-1455)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1455/add-show-differences-and-update-file-with-table-version  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Manage Agents and Manage Tasks already warn when live database personas or task prompts differ from the checked-in repo JSON, and they can restore the database from the file. Operators still cannot see what drifted, and making the table version durable still requires a separate CLI export of both tables. Worse, non-local server start still overwrites the live tables from those JSON files (repo wins), so carefully edited database rows vanish on the next restart or deploy unless someone exported first. This epic adds **Show Differences** and **Update file with table version** on both screens, and **stops automatic JSON→database apply at server start** so the live table is no longer clobbered on boot — Archie inspects drift and writes the current table back to its own repo JSON without leaving the page, then commits in git when ready.

## Functional scope

* When the live table for agent personas or task prompts diverges from its checked-in JSON, Manage Agents and Manage Tasks offer **Show Differences** and **Update file with table version** on the existing divergence warning, alongside **Revert to file**.
* **Show Differences** opens a readable comparison of that page's table versus its file: rows only in the table, rows only in the file, and for shared rows each field that differs (file value vs table value). The comparison uses the same normalization as the existing divergence check so the warning and the diff cannot disagree about whether something changed.
* **Update file with table version** overwrites that page's JSON file with the current database export for that table only — not the sibling table. After a successful write, that table is no longer diverged until the next edit. Committing the file in git remains a separate operator step.
* **Server start no longer auto-applies** either repo JSON file into the database on any deploy env (including the previous non-local repo-wins path). Local skip-of-apply becomes unnecessary for this path because apply-at-startup is gone. The only product path that writes JSON → database for these tables is explicit **Revert to file** (CLI export of both tables may remain for operators; it is not this epic's UI).
* Existing save-to-database and **Revert to file** behavior are unchanged except that banner copy must no longer claim a restart or deploy will overwrite the live table from the file.

## Component scope

* `src/core/repo_admin_json.py` — **modified** — structured row/field comparison for one table; write one table's current rows to that table's JSON only; stop automatic startup apply.
* `src/core/bootstrap.py` — **modified** — drop or no-op the boot-time call that applied repo admin JSON before serving traffic.
* `src/ui/api/api_admin.py` — **modified** — authenticated admin read of one table's comparison; authenticated admin write of one table's JSON file.
* `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — **modified** — **Show Differences** and **Update file with table version** on the shared warning; refresh after a successful file write; replace restart/deploy overwrite copy.
* `src/utils/config.py` — **modified** — only the `REPO_ADMIN_JSON_CONFIG` (and related helper comments) so config text no longer describes unconditional startup apply as the seed path.

## Technical scope

* `src/core/repo_admin_json.py` — new comparison helper for one table key that returns rows only in the database, rows only in the file, and per shared row the fields whose normalized file value differs from the normalized table value, reusing the existing normalize/sort path so status and diff cannot disagree.
* `src/core/repo_admin_json.py` — new or narrowed export helper that writes current database export rows for exactly one table key to that table's configured JSON path (sibling file untouched).
* `src/core/repo_admin_json.py` — change `apply_repo_admin_json_at_startup` so it never applies repo-wins rows (always no-op), or remove that entry point once bootstrap no longer calls it; keep `revert_repo_admin_json_table` as the explicit JSON→database path.
* `src/core/bootstrap.py` — stop invoking startup repo-JSON apply in the runtime bootstrap order (or leave a documented no-op call only if removal would confuse callers — prefer removal).
* `src/ui/api/api_admin.py` — new admin GET that returns the structured comparison for one `agent` / `agent_task` key; new admin POST that writes that one table's file via the core helper and returns success metadata.
* `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — add secondary **Show Differences** that presents the comparison payload; add primary **Update file with table version** with confirm; on success refetch status the same way save/revert already do; rewrite the warning sentence so it no longer says restart/deploy will overwrite from the file.
* `src/utils/config.py` — update the repo-admin JSON config block comments (and any operator-facing path description tied to startup apply) so they match “files are durable seed; apply is Revert-only,” without changing table keys or paths.

## Architectural definition

**Patterns to reuse**

* [`pattern.ui.admin-endpoint`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>) — authenticated admin read of the comparison and write of one table's JSON; business rules stay out of React.
* [`pattern.ui.shared-button-roles`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.shared-button-roles.md>) — labeled `btn` roles: **Show Differences** is secondary; **Update file with table version** is primary (commit-like); **Revert to file** stays the existing secondary + danger confirm.
* [`pattern.ui.in-place-live-refresh`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.in-place-live-refresh.md>) — after a successful file write, the warning refetches silently the same way it does after save/revert.

**New patterns proposed**

none.

**Applicable statutes**

* [`astral.seed.agent-tables-in-repo-json`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.agent-tables-in-repo-json.md>) — those JSON files remain the durable seed; **request change:** Statement currently requires Startup (and Revert) to apply repo-wins — this epic needs Startup removed from that requirement so only explicit Revert applies JSON→database; do not treat the statute as already amended until Archie approves.
* [`astral.idioms.require-auth-on-protected-endpoints`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>) — comparison and file write are admin-authenticated.
* [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — compare/write live in core; API stays thin.
* [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — only the two tables already on the divergence warning; only boot apply for those tables.
* [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>) — reuse the existing export-shape compare and per-table file writer; do not fork a second normalize.
* [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — table keys come from the existing repo-admin JSON registry.
* [`astral.standards.no-cross-contamination`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-cross-contamination.md>) — UI does not reach data; data does not log.
* [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — paths and table keys stay in config.
* [`astral.ui.frontend-file-placement`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>) / [`astral.ui.naming-conventions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.naming-conventions.md>) — banner/diff chrome live with the existing admin UI.
* [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>) — if a touched backend path already takes `debug=`, found/recorded compare-and-write outcomes follow the AST-538 contract; no debug-logging requirement on React.

## Boundaries

* Only agent personas and task prompts — the two tables already covered by the divergence warning. Not dispatch rows or any other admin table.
* Does not git add, commit, or push. Does not write the sibling table's JSON when updating one page.
* Does not auto-export on every save.
* Does not replace or change **Revert to file** (still the explicit JSON→database path).
* **Does** remove automatic JSON→database apply at server start on every deploy env (this overrides the earlier “do not change startup apply” draft).
* Does not invent a second seed channel (SQL dumps, alternate JSON roots, etc.).
* Writing the file on a host without a checkout you will commit (for example staging) is not a durable git update — the same limitation as today's CLI export on that host.
* The two new actions live on the existing divergence warning; they are not shown when that table is in sync.
* Statute text for `astral.seed.agent-tables-in-repo-json` is Archie's to approve; implementers must not silently keep startup apply after this epic ships.

## Acceptance criteria

* On Manage Agents, when personas diverge from the personas JSON, **Show Differences** lists the actual row and field differences (added rows, removed rows, changed fields with file vs table values). It does not include task-prompt drift.
* On Manage Tasks, when task prompts diverge from the task JSON, **Show Differences** lists the actual row and field differences. It does not include persona drift.
* After **Update file with table version** on Manage Agents, the personas JSON matches the live personas table, the agents warning clears, and the tasks warning is unchanged if tasks still diverge.
* After **Update file with table version** on Manage Tasks, the task JSON matches the live task table, the tasks warning clears, and the agents warning is unchanged if personas still diverge.
* Cancel on the Update confirm does not write the file; divergence stays.
* **Revert to file** still restores the database from the file after confirm, without requiring a restart.
* After a successful database edit that diverges from the file, restarting the server (any deploy env) leaves the live table as edited — it is **not** overwritten from the JSON file. **Revert to file** still can restore from the file when the operator chooses it.
* Divergence banner copy no longer tells the operator that the next restart or deploy will overwrite the live table from the file.

## Dependencies and blockers

none for sequencing against siblings. Adjacent Agent work (entity_id batch stamp [AST-1423](https://linear.app/astralcareermatch/issue/AST-1423/entity-id-is-not-populated-for-all-agent-data-rows-in-a-batch) / [AST-1431](https://linear.app/astralcareermatch/issue/AST-1431/gap-tests-for-prompt-row-entity-id-stamp-entity-id-is-not-populated), FEEDBACK entity_id [AST-1486](https://linear.app/astralcareermatch/issue/AST-1486/feedback-block-type-still-has-null-entity-id-in-agent-data-batch)) does not own this warning or these files. **Archie approval** of the `astral.seed.agent-tables-in-repo-json` startup-removal change is required before implementers treat startup apply as gone from canon.

## Open questions

none.

## Proposed child tickets

#### 1!: **Stop startup apply, structured diff, and per-table file write - Ada**

Owns removing automatic JSON→database apply at boot, computing the structured row/field comparison with the same normalization as divergence, and writing one table's current rows to that table's JSON only. Exposes admin-authenticated read of the comparison and write of the file. Does not own banner chrome. Does not write the sibling table. Does not amend the statute file itself — cites the Archie-requested change.

**Citations: **`pattern.ui.admin-endpoint`, `astral.seed.agent-tables-in-repo-json` (startup-removal request), `astral.standards.dry-and-focused-functions`, `astral.standards.no-hardcoded-sets`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.config.config-source-of-truth`

**Scope: **`src/core/repo_admin_json.py` — **modified** — structured row/field comparison for one table; write one table's current rows to that table's JSON only; stop automatic startup apply. `src/core/bootstrap.py` — **modified** — drop or no-op the boot-time call that applied repo admin JSON before serving traffic. `src/ui/api/api_admin.py` — **modified** — authenticated admin read of one table's comparison; authenticated admin write of one table's JSON file. `src/utils/config.py` — **modified** — only the `REPO_ADMIN_JSON_CONFIG` (and related helper comments) so config text no longer describes unconditional startup apply as the seed path. `src/core/repo_admin_json.py` — new comparison helper for one table key that returns rows only in the database, rows only in the file, and per shared row the fields whose normalized file value differs from the normalized table value, reusing the existing normalize/sort path so status and diff cannot disagree. `src/core/repo_admin_json.py` — new or narrowed export helper that writes current database export rows for exactly one table key to that table's configured JSON path (sibling file untouched). `src/core/repo_admin_json.py` — change `apply_repo_admin_json_at_startup` so it never applies repo-wins rows (always no-op), or remove that entry point once bootstrap no longer calls it; keep `revert_repo_admin_json_table` as the explicit JSON→database path. `src/core/bootstrap.py` — stop invoking startup repo-JSON apply in the runtime bootstrap order (or leave a documented no-op call only if removal would confuse callers — prefer removal). `src/ui/api/api_admin.py` — new admin GET that returns the structured comparison for one `agent` / `agent_task` key; new admin POST that writes that one table's file via the core helper and returns success metadata. `src/utils/config.py` — update the repo-admin JSON config block comments (and any operator-facing path description tied to startup apply) so they match “files are durable seed; apply is Revert-only,” without changing table keys or paths.

**Estimate: 5**

#### 2: **Show Differences and Update file on the divergence banner - Katherine**

After #1. Adds the two labeled actions to the shared warning used by Manage Agents and Manage Tasks. **Show Differences** presents Ada's comparison. **Update file with table version** confirms, then writes that page's table only and refreshes the warning. Rewrites banner copy so it no longer claims restart/deploy overwrite. Does not change **Revert to file** confirm behavior.

**Citations: **`pattern.ui.shared-button-roles`, `pattern.ui.in-place-live-refresh`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`

**Scope: **`src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — **modified** — **Show Differences** and **Update file with table version** on the shared warning; refresh after a successful file write; replace restart/deploy overwrite copy. `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — add secondary **Show Differences** that presents the comparison payload; add primary **Update file with table version** with confirm; on success refetch status the same way save/revert already do; rewrite the warning sentence so it no longer says restart/deploy will overwrite from the file.

**Estimate: 2**

Monolith check: four functional capabilities (show differences, update file, stop startup apply, both screens) with two children because both screens already share one warning and stop-apply + compare/write are one core module — splitting screens or splitting core would duplicate chrome or the same `repo_admin_json` surface.

Scope partition check: every Component/Technical item appears in exactly one child (#1 core/api/config/bootstrap; #2 banner only).

---

## Original brief

Add to Manage Tasks and Manage Agents.

### Comments

#### chuckles — 2026-08-27T03:13:36.805Z
@susan Parent stays In Progress until every child is User Testing — including Bug child AST-1511 (Show Differences modal scroll). Feature children AST-1505 / AST-1506 are already UT; AST-1511 is still Tests Passed in the fix lane (needs review-fix → User Testing → merge into ftr). Prep-uat cannot re-promote this parent until that bug lands. Fix-lane watcher owns AST-1511; datt will not drive a Bug-labeled child.

#### susan — 2026-08-27T02:29:40.456Z
@chuckles Why isn't this ticket closing?

#### susan — 2026-08-26T23:27:54.919Z
\[bug\]

The modal screen does not scroll, so I can only see the first three differences.

#### chuckles — 2026-08-26T19:02:32.761Z
[refresh-ftr] blocked: docs/test-bible/core/meteorite.md (@Betty White) — merge origin/dev into origin/ftr/AST-1455-show-differences-update-file.

#### chuckles — 2026-08-24T21:51:36.932Z
@susan Dispatch cannot proceed — definition shape gaps:

- Missing **`## Component scope`** section (file-level scope prose required by define-parent).
- Missing **`## Technical scope`** section (function/table-level change prose required by define-parent).
- Proposed child blocks lack explicit **`Scope:`** lines citing their slice of Component/Technical scope (each `####` block needs Citations + Scope per dispatch-parent §2c).

Functional scope, Architectural definition, and Proposed children look otherwise ready. Please run a define refresh (add Component scope + Technical scope, add Scope lines to each child block), then move back to **Todo** + assign **Chuckles**.

#### chuckles — 2026-08-24T21:50:34.112Z
[thread-missing] Cursor chat `0a23a9e1-b25c-4b2e-97d6-03e2b96d88a1` has no local `store.db` on **not-chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/0a23a9e1-b25c-4b2e-97d6-03e2b96d88a1/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `a148da3c-b8e4-4922-89a0-69aca2d932b9`.

Watcher rule `datt` on `AST-1455` (Thread owner `AST-1455`).

---

_Implementation detail may live in git history on `origin/dev`._
