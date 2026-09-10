# AST-1455 — Add "Show Differences" and "Update file with table version"

**Component:** agent  
**Children:** AST-1505, AST-1506, AST-1511  
**Linear archived:** AST-1455 2026-09-09; AST-1505 2026-09-09; AST-1506 2026-09-09; AST-1511 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-26 11:03 | AST-1505 | docs | `6040382d0` | plan — compare, per-table write, no boot apply |
| 2026-08-26 11:06 | AST-1505 | docs | `7e7f42d11` | Joan validate — APPROVED core compare write APIs |
| 2026-08-26 11:08 | AST-1505 | docs | `0f71251a5` | append build review stub |
| 2026-08-26 11:08 | AST-1505 | code | `18d58dbab` | admin compare and write repo JSON routes |
| 2026-08-26 11:08 | AST-1505 | code | `f201ae469` | per-table export, remove boot apply |
| 2026-08-26 11:08 | AST-1505 | code | `7750fb62f` | structured repo JSON table comparison |
| 2026-08-26 11:10 | AST-1505 | test | `73184142a` | compare/write manifest, retire boot apply tests |
| 2026-08-26 11:16 | AST-1505 | resolve | `5051a0199` | — clean |
| 2026-08-26 11:16 | AST-1505 | docs | `8fc78b30a` | Radia review — REVIEW statute corpus lag on parent |
| 2026-08-26 11:18 | AST-1505 | merge-tests | `756d9c068` | origin/tests 73184142 |
| 2026-08-26 11:33 | AST-1506 | docs | `f784a0446` | plan — divergence banner Show Differences and Update file |
| 2026-08-26 11:35 | AST-1506 | docs | `341ec0c54` | Joan validate — banner Show Update wired |
| 2026-08-26 11:36 | AST-1506 | code | `69f04f10e` | divergence banner Show Differences modal and copy |
| 2026-08-26 11:37 | AST-1506 | docs | `c899f1c44` | append build review stub |
| 2026-08-26 11:37 | AST-1506 | code | `a549ac4a9` | divergence banner Update file with table version |
| 2026-08-26 11:39 | AST-1506 | test | `c0422905d` | banner Show Differences and Update file manifest |
| 2026-08-26 11:39 | AST-1506 | test | `48c880784` | banner Show Differences and Update file manifest |
| 2026-08-26 11:42 | AST-1506 | docs | `04a007168` | Radia review — banner Show Update wired |
| 2026-08-26 11:44 | AST-1506 | merge-tests | `c3a5a8003` | origin/tests 48c88078 |
| 2026-08-26 12:03 | AST-1455 | merge | `39c179363` | Merge origin/dev into ftr/AST-1455-show-differences-update-file |
| 2026-08-26 17:25 | AST-1511 | docs | `daaef3d18` | plan-fix — Show Differences modal scroll |
| 2026-08-26 17:51 | AST-1511 | merge-tests | `dbc44800d` | origin/tests 1d1b236a |
| 2026-08-26 17:51 | AST-1511 | test | `1d1b236aa` | bug-repro — Show Differences modal scroll |
| 2026-08-26 17:54 | AST-1511 | code | `46870882c` | scroll wrapper for Show Differences modal body |
| 2026-08-27 05:50 | AST-1511 | docs | `e7b2d351e` | Radia review — clean modal scroll fix |
| 2026-08-27 05:53 | AST-1511 | resolve | `b612660d2` | — clean |
| 2026-08-28 22:28 | AST-1455 | docs | `6775d5cac` | mirror epic registry Threads |
| 2026-09-09 17:59 | AST-1505 | docs | `18850a0f0` | archive Linear issue content |
| 2026-09-09 17:59 | AST-1506 | docs | `a7864df1d` | archive Linear issue content |
| 2026-09-09 17:59 | AST-1511 | docs | `5330cbd21` | archive Linear issue content |
| 2026-09-09 18:05 | AST-1455 | docs | `78cc156c1` | archive Linear issue content |

## Epic — AST-1455

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1455/add-show-differences-and-update-file-with-table-version · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: High / 8_

### Purpose

Manage Agents and Manage Tasks already warn when live database personas or task prompts differ from the checked-in repo JSON, and they can restore the database from the file. Operators still cannot see what drifted, and making the table version durable still requires a separate CLI export of both tables. Worse, non-local server start still overwrites the live tables from those JSON files (repo wins), so carefully edited database rows vanish on the next restart or deploy unless someone exported first. This epic adds **Show Differences** and **Update file with table version** on both screens, and **stops automatic JSON→database apply at server start** so the live table is no longer clobbered on boot — Archie inspects drift and writes the current table back to its own repo JSON without leaving the page, then commits in git when ready.

### Functional scope

* When the live table for agent personas or task prompts diverges from its checked-in JSON, Manage Agents and Manage Tasks offer **Show Differences** and **Update file with table version** on the existing divergence warning, alongside **Revert to file**.
* **Show Differences** opens a readable comparison of that page's table versus its file: rows only in the table, rows only in the file, and for shared rows each field that differs (file value vs table value). The comparison uses the same normalization as the existing divergence check so the warning and the diff cannot disagree about whether something changed.
* **Update file with table version** overwrites that page's JSON file with the current database export for that table only — not the sibling table. After a successful write, that table is no longer diverged until the next edit. Committing the file in git remains a separate operator step.
* **Server start no longer auto-applies** either repo JSON file into the database on any deploy env (including the previous non-local repo-wins path). Local skip-of-apply becomes unnecessary for this path because apply-at-startup is gone. The only product path that writes JSON → database for these tables is explicit **Revert to file** (CLI export of both tables may remain for operators; it is not this epic's UI).
* Existing save-to-database and **Revert to file** behavior are unchanged except that banner copy must no longer claim a restart or deploy will overwrite the live table from the file.

### Component scope

* `src/core/repo_admin_json.py` — **modified** — structured row/field comparison for one table; write one table's current rows to that table's JSON only; stop automatic startup apply.
* `src/core/bootstrap.py` — **modified** — drop or no-op the boot-time call that applied repo admin JSON before serving traffic.
* `src/ui/api/api_admin.py` — **modified** — authenticated admin read of one table's comparison; authenticated admin write of one table's JSON file.
* `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — **modified** — **Show Differences** and **Update file with table version** on the shared warning; refresh after a successful file write; replace restart/deploy overwrite copy.
* `src/utils/config.py` — **modified** — only the `REPO_ADMIN_JSON_CONFIG` (and related helper comments) so config text no longer describes unconditional startup apply as the seed path.

### Technical scope

* `src/core/repo_admin_json.py` — new comparison helper for one table key that returns rows only in the database, rows only in the file, and per shared row the fields whose normalized file value differs from the normalized table value, reusing the existing normalize/sort path so status and diff cannot disagree.
* `src/core/repo_admin_json.py` — new or narrowed export helper that writes current database export rows for exactly one table key to that table's configured JSON path (sibling file untouched).
* `src/core/repo_admin_json.py` — change `apply_repo_admin_json_at_startup` so it never applies repo-wins rows (always no-op), or remove that entry point once bootstrap no longer calls it; keep `revert_repo_admin_json_table` as the explicit JSON→database path.
* `src/core/bootstrap.py` — stop invoking startup repo-JSON apply in the runtime bootstrap order (or leave a documented no-op call only if removal would confuse callers — prefer removal).
* `src/ui/api/api_admin.py` — new admin GET that returns the structured comparison for one `agent` / `agent_task` key; new admin POST that writes that one table's file via the core helper and returns success metadata.
* `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — add secondary **Show Differences** that presents the comparison payload; add primary **Update file with table version** with confirm; on success refetch status the same way save/revert already do; rewrite the warning sentence so it no longer says restart/deploy will overwrite from the file.
* `src/utils/config.py` — update the repo-admin JSON config block comments (and any operator-facing path description tied to startup apply) so they match “files are durable seed; apply is Revert-only,” without changing table keys or paths.

### Architectural definition

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

### Boundaries

* Only agent personas and task prompts — the two tables already covered by the divergence warning. Not dispatch rows or any other admin table.
* Does not git add, commit, or push. Does not write the sibling table's JSON when updating one page.
* Does not auto-export on every save.
* Does not replace or change **Revert to file** (still the explicit JSON→database path).
* **Does** remove automatic JSON→database apply at server start on every deploy env (this overrides the earlier “do not change startup apply” draft).
* Does not invent a second seed channel (SQL dumps, alternate JSON roots, etc.).
* Writing the file on a host without a checkout you will commit (for example staging) is not a durable git update — the same limitation as today's CLI export on that host.
* The two new actions live on the existing divergence warning; they are not shown when that table is in sync.
* Statute text for `astral.seed.agent-tables-in-repo-json` is Archie's to approve; implementers must not silently keep startup apply after this epic ships.

### Acceptance criteria

* On Manage Agents, when personas diverge from the personas JSON, **Show Differences** lists the actual row and field differences (added rows, removed rows, changed fields with file vs table values). It does not include task-prompt drift.
* On Manage Tasks, when task prompts diverge from the task JSON, **Show Differences** lists the actual row and field differences. It does not include persona drift.
* After **Update file with table version** on Manage Agents, the personas JSON matches the live personas table, the agents warning clears, and the tasks warning is unchanged if tasks still diverge.
* After **Update file with table version** on Manage Tasks, the task JSON matches the live task table, the tasks warning clears, and the agents warning is unchanged if personas still diverge.
* Cancel on the Update confirm does not write the file; divergence stays.
* **Revert to file** still restores the database from the file after confirm, without requiring a restart.
* After a successful database edit that diverges from the file, restarting the server (any deploy env) leaves the live table as edited — it is **not** overwritten from the JSON file. **Revert to file** still can restore from the file when the operator chooses it.
* Divergence banner copy no longer tells the operator that the next restart or deploy will overwrite the live table from the file.

### Dependencies and blockers

none for sequencing against siblings. Adjacent Agent work (entity_id batch stamp [AST-1423](https://linear.app/astralcareermatch/issue/AST-1423/entity-id-is-not-populated-for-all-agent-data-rows-in-a-batch) / [AST-1431](https://linear.app/astralcareermatch/issue/AST-1431/gap-tests-for-prompt-row-entity-id-stamp-entity-id-is-not-populated), FEEDBACK entity_id [AST-1486](https://linear.app/astralcareermatch/issue/AST-1486/feedback-block-type-still-has-null-entity-id-in-agent-data-batch)) does not own this warning or these files. **Archie approval** of the `astral.seed.agent-tables-in-repo-json` startup-removal change is required before implementers treat startup apply as gone from canon.

### Open questions

none.

### Proposed child tickets


##### 1!: **Stop startup apply, structured diff, and per-table file write - Ada**

Owns removing automatic JSON→database apply at boot, computing the structured row/field comparison with the same normalization as divergence, and writing one table's current rows to that table's JSON only. Exposes admin-authenticated read of the comparison and write of the file. Does not own banner chrome. Does not write the sibling table. Does not amend the statute file itself — cites the Archie-requested change.

**Citations: **`pattern.ui.admin-endpoint`, `astral.seed.agent-tables-in-repo-json` (startup-removal request), `astral.standards.dry-and-focused-functions`, `astral.standards.no-hardcoded-sets`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.config.config-source-of-truth`

**Scope: **`src/core/repo_admin_json.py` — **modified** — structured row/field comparison for one table; write one table's current rows to that table's JSON only; stop automatic startup apply. `src/core/bootstrap.py` — **modified** — drop or no-op the boot-time call that applied repo admin JSON before serving traffic. `src/ui/api/api_admin.py` — **modified** — authenticated admin read of one table's comparison; authenticated admin write of one table's JSON file. `src/utils/config.py` — **modified** — only the `REPO_ADMIN_JSON_CONFIG` (and related helper comments) so config text no longer describes unconditional startup apply as the seed path. `src/core/repo_admin_json.py` — new comparison helper for one table key that returns rows only in the database, rows only in the file, and per shared row the fields whose normalized file value differs from the normalized table value, reusing the existing normalize/sort path so status and diff cannot disagree. `src/core/repo_admin_json.py` — new or narrowed export helper that writes current database export rows for exactly one table key to that table's configured JSON path (sibling file untouched). `src/core/repo_admin_json.py` — change `apply_repo_admin_json_at_startup` so it never applies repo-wins rows (always no-op), or remove that entry point once bootstrap no longer calls it; keep `revert_repo_admin_json_table` as the explicit JSON→database path. `src/core/bootstrap.py` — stop invoking startup repo-JSON apply in the runtime bootstrap order (or leave a documented no-op call only if removal would confuse callers — prefer removal). `src/ui/api/api_admin.py` — new admin GET that returns the structured comparison for one `agent` / `agent_task` key; new admin POST that writes that one table's file via the core helper and returns success metadata. `src/utils/config.py` — update the repo-admin JSON config block comments (and any operator-facing path description tied to startup apply) so they match “files are durable seed; apply is Revert-only,” without changing table keys or paths.

**Estimate: 5**

##### 2: **Show Differences and Update file on the divergence banner - Katherine**

After #1. Adds the two labeled actions to the shared warning used by Manage Agents and Manage Tasks. **Show Differences** presents Ada's comparison. **Update file with table version** confirms, then writes that page's table only and refreshes the warning. Rewrites banner copy so it no longer claims restart/deploy overwrite. Does not change **Revert to file** confirm behavior.

**Citations: **`pattern.ui.shared-button-roles`, `pattern.ui.in-place-live-refresh`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`

**Scope: **`src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — **modified** — **Show Differences** and **Update file with table version** on the shared warning; refresh after a successful file write; replace restart/deploy overwrite copy. `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — add secondary **Show Differences** that presents the comparison payload; add primary **Update file with table version** with confirm; on success refetch status the same way save/revert already do; rewrite the warning sentence so it no longer says restart/deploy will overwrite from the file.

**Estimate: 2**

Monolith check: four functional capabilities (show differences, update file, stop startup apply, both screens) with two children because both screens already share one warning and stop-apply + compare/write are one core module — splitting screens or splitting core would duplicate chrome or the same `repo_admin_json` surface.

Scope partition check: every Component/Technical item appears in exactly one child (#1 core/api/config/bootstrap; #2 banner only).

---

### Original brief

Add to Manage Tasks and Manage Agents.

#### Comments


##### chuckles — 2026-08-27T03:13:36.805Z

@susan Parent stays In Progress until every child is User Testing — including Bug child AST-1511 (Show Differences modal scroll). Feature children AST-1505 / AST-1506 are already UT; AST-1511 is still Tests Passed in the fix lane (needs review-fix → User Testing → merge into ftr). Prep-uat cannot re-promote this parent until that bug lands. Fix-lane watcher owns AST-1511; datt will not drive a Bug-labeled child.

##### susan — 2026-08-27T02:29:40.456Z

@chuckles Why isn't this ticket closing?

##### susan — 2026-08-26T23:27:54.919Z

\[bug\]

The modal screen does not scroll, so I can only see the first three differences.

##### chuckles — 2026-08-26T19:02:32.761Z

[refresh-ftr] blocked: docs/test-bible/core/meteorite.md (@Betty White) — merge origin/dev into origin/ftr/AST-1455-show-differences-update-file.

##### chuckles — 2026-08-24T21:51:36.932Z

@susan Dispatch cannot proceed — definition shape gaps:

- Missing **`## Component scope`** section (file-level scope prose required by define-parent).
- Missing **`## Technical scope`** section (function/table-level change prose required by define-parent).
- Proposed child blocks lack explicit **`Scope:`** lines citing their slice of Component/Technical scope (each `####` block needs Citations + Scope per dispatch-parent §2c).

Functional scope, Architectural definition, and Proposed children look otherwise ready. Please run a define refresh (add Component scope + Technical scope, add Scope lines to each child block), then move back to **Todo** + assign **Chuckles**.

##### chuckles — 2026-08-24T21:50:34.112Z

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `a148da3c-b8e4-4922-89a0-69aca2d932b9`.

Watcher rule `datt` on `AST-1455` (Thread owner `AST-1455`).

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1505 — Stop startup apply, structured diff, and per-table file write

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1505/stop-startup-apply-structured-diff-and-per-table-file-write-add-show · Status at archive: Archive · Project: Astral Agent · Assignee: ada · Priority / estimate: None / 5 · Blocked by / blocks / related: parent: AST-1455; blocks: AST-1506_

#### What this implements

Owns removing automatic JSON→database apply at boot, computing the structured row/field comparison with the same normalization as divergence, and writing one table's current rows to that table's JSON only. Exposes admin-authenticated read of the comparison and write of the file. Does not own banner chrome. Does not write the sibling table. Does not amend the statute file itself — cites the Archie-requested change.

#### Citations

`pattern.ui.admin-endpoint`, `astral.seed.agent-tables-in-repo-json` (startup-removal request), `astral.standards.dry-and-focused-functions`, `astral.standards.no-hardcoded-sets`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.config.config-source-of-truth`

#### Scope

`src/core/repo_admin_json.py` — **modified** — structured row/field comparison for one table; write one table's current rows to that table's JSON only; stop automatic startup apply. `src/core/bootstrap.py` — **modified** — drop or no-op the boot-time call that applied repo admin JSON before serving traffic. `src/ui/api/api_admin.py` — **modified** — authenticated admin read of one table's comparison; authenticated admin write of one table's JSON file. `src/utils/config.py` — **modified** — only the `REPO_ADMIN_JSON_CONFIG` (and related helper comments) so config text no longer describes unconditional startup apply as the seed path. `src/core/repo_admin_json.py` — new comparison helper for one table key that returns rows only in the database, rows only in the file, and per shared row the fields whose normalized file value differs from the normalized table value, reusing the existing normalize/sort path so status and diff cannot disagree. `src/core/repo_admin_json.py` — new or narrowed export helper that writes current database export rows for exactly one table key to that table's configured JSON path (sibling file untouched). `src/core/repo_admin_json.py` — change `apply_repo_admin_json_at_startup` so it never applies repo-wins rows (always no-op), or remove that entry point once bootstrap no longer calls it; keep `revert_repo_admin_json_table` as the explicit JSON→database path. `src/core/bootstrap.py` — stop invoking startup repo-JSON apply in the runtime bootstrap order (or leave a documented no-op call only if removal would confuse callers — prefer removal). `src/ui/api/api_admin.py` — new admin GET that returns the structured comparison for one `agent` / `agent_task` key; new admin POST that writes that one table's file via the core helper and returns success metadata. `src/utils/config.py` — update the repo-admin JSON config block comments (and any operator-facing path description tied to startup apply) so they match "files are durable seed; apply is Revert-only," without changing table keys or paths.

#### Acceptance criteria

- [X] After **Update file with table version** on Manage Agents (via API), the personas JSON matches the live personas table; sibling task JSON unchanged when tasks still diverge.
- [X] After **Update file with table version** on Manage Tasks (via API), the task JSON matches the live task table; sibling personas JSON unchanged when personas still diverge.
- [ ] Cancel on the Update confirm does not write the file; divergence stays. (AST-1506 UI confirm — API is POST-only on explicit call.)
- [X] **Revert to file** still restores the database from the file after confirm, without requiring a restart.
- [X] After a successful database edit that diverges from the file, restarting the server (any deploy env) leaves the live table as edited — it is **not** overwritten from the JSON file.

#### Boundaries

- [X] Does not own banner chrome (sibling #2 Katherine). Does not write the sibling table's JSON when updating one page. Does not amend `astral.seed.agent-tables-in-repo-json` statute file — cites Archie-requested change only.

#### Notes for planning

Parent AST-1455 definition is authoritative. Statute startup-removal needs Archie approval before implementers treat canon as amended.

##### Comments


###### ada — 2026-08-26T18:18:47.781Z

[check-linear] republished sub @ `5051a019` — ftr-base linear history, no sync(dev)/Merge remote-tracking; validate-sub-log ok

###### radia — 2026-08-26T18:16:18.019Z

[code-rubric] REVIEW (Commit: c4936837) statute corpus lag on parent

###### betty — 2026-08-26T18:12:31.049Z

`origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `c4936837` · compare write manifest

###### joan — 2026-08-26T18:06:09.879Z

[plan-rubric] PROCEED (Commit: b14c091c) core compare write APIs

###### ada — 2026-08-26T18:03:32.667Z

origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write @ `b14c091c45a50a4969c535660728f817cccd3c48` · three-stage core+API plan

---

#### Summary

Child #1 of AST-1455. Adds core comparison and per-table repo JSON export for `agent` and `agent_task`, exposes them through authenticated admin API routes, and finalizes removal of automatic JSON→database apply at boot. Katherine's sibling AST-1506 wires **Show Differences** and **Update file with table version** in `RepoJsonDivergenceBanner.tsx` against these endpoints. AST-1497/AST-1502 already removed the bootstrap wire and made `apply_repo_admin_json_at_startup` a no-op; this ticket makes that permanent product behavior, adds the missing compare/write surface, and updates operator-facing config text.

#### UAT fitness

- **AC restored:** Parent AC — *"After **Update file with table version** on Manage Agents … the personas JSON matches the live personas table; sibling task JSON unchanged when tasks still diverge"* and *"After a successful database edit that diverges from the file, restarting the server (any deploy env) leaves the live table as edited — it is **not** overwritten from the JSON file."*
- **Correct outcome:** Admin can GET a structured row/field diff for one table and POST to overwrite only that table's checked-in JSON from the live DB; server restart never re-applies repo JSON into SQLite; **Revert to file** still restores DB from file on demand.
- **Sibling check:** AST-1506 consumes `GET /api/admin/repo_json/compare/<table_key>` and `POST /api/admin/repo_json/write/<table_key>`; existing `GET /status` and `POST /revert/<table_key>` unchanged; cancel-on-confirm is UI-only (Katherine).
- **Not sufficient:** Leaving `apply_repo_admin_json_at_startup` as a silent no-op without compare/write APIs, or only updating banner copy without per-table file write — operators still cannot see drift or persist one table's version from the product.
- **Wrong fix rejected:** Re-enabling boot-time repo-wins apply, writing both JSON files when updating one table, or forking a second normalization path that could disagree with `get_repo_admin_json_divergence_status`.

#### Scope gate

All files and change kinds below are taken from this ticket's **## Scope** only. Out of scope: `RepoJsonDivergenceBanner.tsx`, React pages, statute file edits, git commit/push, sibling-table writes, `tests/**`, `docs/test-bible/**`.

#### Stage 1: Core structured comparison

**Done when:** `get_repo_admin_json_table_comparison(table_key)` returns the structured diff payload; when `_repo_admin_json_table_diverged` is false for a table, all three diff lists are empty; when true, at least one list is non-empty; `python3 -m py_compile src/core/repo_admin_json.py` passes. No API routes yet.

1. In `src/core/repo_admin_json.py`, add private helper **`_normalized_row_maps(table_key: str, file_rows: list[dict], db_rows: list[dict]) -> tuple[dict[str, dict], dict[str, dict], dict[str, dict], dict[str, dict]]`** returning `(file_by_key, db_by_key, file_norm_by_key, db_norm_by_key)` where:
   - `key_col = _REPO_JSON_ROW_KEY[table_key]`
   - Keys are `str(row.get(key_col) or "")` for each row in file and db lists
   - `*_norm_by_key` values come from `_normalize_repo_json_row(table_key, row)` on the **raw** row
   - `file_by_key` / `db_by_key` hold the **export-shaped raw rows** (same objects as input lists) for display in the API

2. Add public function **`get_repo_admin_json_table_comparison(table_key: str) -> dict[str, Any]`**:
   - Validate `table_key in get_repo_admin_json_table_keys()` else `ValueError`
   - Open one connection via `database._get_connection()`; `try/finally` close
   - `file_rows = load_repo_admin_json_file(table_key)` (propagate `RuntimeError` / `ValueError`)
   - `db_rows = _fetch_db_repo_json_rows(conn, table_key)`
   - Build maps via `_normalized_row_maps`
   - `file_keys = set(file_by_key)`; `db_keys = set(db_by_key)`
   - **`only_in_database`:** list of `db_by_key[k]` for each `k in sorted(db_keys - file_keys)`
   - **`only_in_file`:** list of `file_by_key[k]` for each `k in sorted(file_keys - db_keys)`
   - **`changed_rows`:** for each `k in sorted(file_keys & db_keys)`, compare `file_norm_by_key[k]` vs `db_norm_by_key[k]` field-by-field (union of keys in both normalized dicts). For each field where normalized values differ, append `{"field": name, "file_value": file_by_key[k].get(name), "database_value": db_by_key[k].get(name)}`. If the fields list is non-empty, append `{"row_key": k, "fields": [...]}` to `changed_rows`
   - Return:
```python
     {
         "table_key": table_key,
         "diverged": _repo_admin_json_table_diverged(conn, table_key),
         "repo_relative_path": REPO_ADMIN_JSON_CONFIG["tables"][table_key]["repo_relative_path"],
         "only_in_database": [...],
         "only_in_file": [...],
         "changed_rows": [...],
     }
```

3. Add **`get_repo_admin_json_table_comparison`** to **`__all__`**.

⚠️ **Decision:** Reuse existing `_normalize_repo_json_row`, `_sorted_normalized_rows`, and `_repo_admin_json_table_diverged` — do not duplicate scalar rules. Invariant: when `diverged` is false, `only_in_database`, `only_in_file`, and `changed_rows` must all be empty.

#### Stage 2: Core per-table export and startup apply removal

**Done when:** `export_repo_admin_json_table_to_file(table_key)` writes exactly one JSON file and returns metadata; `apply_repo_admin_json_at_startup` is removed from the module; `export_repo_admin_json_to_files()` still writes both tables (CLI unchanged); `REPO_ADMIN_JSON_CONFIG` comment reflects Revert-only apply; `python3 -m py_compile src/core/repo_admin_json.py src/core/bootstrap.py src/utils/config.py` passes.

1. In `src/core/repo_admin_json.py`, add **`export_repo_admin_json_table_to_file(table_key: str) -> dict[str, Any]`**:
   - Validate `table_key in get_repo_admin_json_table_keys()` else `ValueError`
   - Open connection; fetch rows via `_fetch_db_repo_json_rows(conn, table_key)`; close connection
   - `path = get_repo_admin_json_path(table_key)`; `path.parent.mkdir(parents=True, exist_ok=True)`
   - Write `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"` with UTF-8 (same as `export_repo_admin_json_to_files`)
   - Return `{"table_key": table_key, "row_count": len(rows), "repo_relative_path": REPO_ADMIN_JSON_CONFIG["tables"][table_key]["repo_relative_path"]}`
   - **Do not** read or write the sibling table's path

2. Add **`export_repo_admin_json_table_to_file`** to **`__all__`**. Leave **`export_repo_admin_json_to_files`** unchanged (both-table CLI path).

3. **Remove** function **`apply_repo_admin_json_at_startup`** entirely:
   - Delete the function body and its **`__all__`** entry
   - Update module docstring (lines 1–7): boot-time apply is **removed** (AST-1455), not merely kill-switched; export, load, compare, revert, and per-table write remain

4. In `src/core/bootstrap.py`, read the module docstring. If it still references AST-1497 kill-switch only, update to cite AST-1455 permanent removal. **Do not** re-add any call to repo JSON apply. `bootstrap_runtime()` stays: validate → schema ensure → scheduler.

5. In `src/utils/config.py`, change the comment above **`REPO_ADMIN_JSON_CONFIG`** (~line 3866) from *"checked-in JSON applied at startup (AST-782)"* to state that checked-in JSON under `data/admin/` is the durable seed, **explicit Revert to file** (and future scripted apply) loads repo-wins into the DB, and **server start does not apply** these files (AST-1455). Do not change table keys, paths, or column definitions.

⚠️ **Decision:** Remove `apply_repo_admin_json_at_startup` rather than keep a no-op stub — `bootstrap_runtime` already does not call it (AST-1502). `revert_repo_admin_json_table` remains the product JSON→DB path. Betty may revise `TestApplyRepoAdminJsonAtStartup` in qa-child; Ada does not edit `tests/`.

#### Stage 3: Admin API compare and write routes

**Done when:** Authenticated admin GET returns comparison JSON; POST writes one table's file and returns success metadata; invalid `table_key` returns 400; core errors return 500; routes follow the same thin-wrapper pattern as existing `/repo_json/status` and `/repo_json/revert/<table_key>`; `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, extend imports from `src.core.repo_admin_json`:
```python
   from src.core.repo_admin_json import (
       export_repo_admin_json_table_to_file,
       get_repo_admin_json_divergence_status,
       get_repo_admin_json_table_comparison,
       revert_repo_admin_json_table,
   )
```

2. Add route **`GET /api/admin/repo_json/compare/<table_key>`** with `@require_admin`:
   - If `table_key not in get_repo_admin_json_table_keys()` (import from `src.utils.config`), return `jsonify({"error": "unknown repo admin JSON table"})`, **400**
   - Try `get_repo_admin_json_table_comparison(table_key)`; on `RuntimeError` / `ValueError`, return `jsonify({"error": str(exc)})`, **500**
   - Else return `jsonify(comparison)`, **200**

3. Add route **`POST /api/admin/repo_json/write/<table_key>`** with `@require_admin`:
   - Same `table_key` validation → **400**
   - Try `export_repo_admin_json_table_to_file(table_key)`; on `RuntimeError` / `ValueError`, return `jsonify({"error": str(exc)})`, **500**
   - Else return `jsonify({"ok": True, **result})`, **200** where `result` is the core helper's return dict

4. Place both routes in the existing **Repo admin JSON divergence (AST-783)** section, immediately after `repo_json_revert`.

⚠️ **Decision:** Validate `table_key` against `get_repo_admin_json_table_keys()` from config — not a hardcoded `("agent", "agent_task")` tuple — per `astral.standards.no-hardcoded-sets`. Optionally align `repo_json_revert` to the same guard in this stage only if the one-line change is adjacent; do not otherwise refactor revert.

#### Hand-verify (build completion, before Betty)

Run on epic worktree with local server or Flask test client:

1. Edit one persona in Manage Agents (or insert a test row), confirm `GET /api/admin/repo_json/compare/agent` shows the field in `changed_rows` and `diverged: true`.
2. `POST /api/admin/repo_json/write/agent` — confirm `data/admin/agent.json` on disk matches DB export shape; `GET /api/admin/repo_json/status` shows `agent.diverged: false`; `agent_task` status unchanged if tasks were not edited.
3. Restart server (or re-run `bootstrap_runtime()` in a shell) — edited DB row still present; not overwritten from JSON.
4. `POST /api/admin/repo_json/revert/agent` — DB restores from file; divergence clears.

Document pass/fail in the Stage 3 Linear completion comment only (no prompt bodies in comments).

#### Estimate

Confirm Chuckles estimate: 5 — agree. Startup wire is already gone; remaining work is comparison logic, per-table export, API surface, and config/doc cleanup — fits 5 points with Betty manifest on compare/write/revert invariants.

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1505
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `b14c091c45a50a4969c535660728f817cccd3c48`

#### Traceability

AC1–2 → Stage 2 `export_repo_admin_json_table_to_file` + Stage 3 `POST /repo_json/write/<table_key>` (sibling AST-1506 wires UI); AC3 → N/A this child (cancel is Katherine confirm-only); AC4 → Stage 2 preserves `revert_repo_admin_json_table` + existing revert route; AC5 → Stage 2 removes `apply_repo_admin_json_at_startup` + bootstrap docstring; parent Show Differences → Stage 1 `GET /repo_json/compare/<table_key>` for AST-1506.

#### Findings


##### discuss

- **Location:** Stage 1 `get_repo_admin_json_table_comparison` / `astral.standards.dry-and-focused-functions`
- **Finding:** After building `file_rows`/`db_rows` and normalized maps, the stage calls `_repo_admin_json_table_diverged(conn, table_key)`, which reloads file and DB rows again.
- **Recommendation:** Optional implement-time tweak: derive `diverged` from the maps already built (or pass pre-fetched rows into a narrowed helper) to avoid duplicate I/O. Not blocking — correctness is sound.

- **Location:** Stage 2 / `astral.seed.agent-tables-in-repo-json`
- **Finding:** Canon statute still documents kill-switch no-op as the conforming boot path; this plan permanently removes `apply_repo_admin_json_at_startup`. Parent AST-1455 and child Boundaries correctly defer statute amendment to Archie.
- **Recommendation:** Track Archie canon update on parent; do not block build on statute file edit in this child.

- **Location:** Plan structure / R6 self-assessment checklist
- **Finding:** No `## Self-Assessment` section (Estimate confirm line is present).
- **Recommendation:** Optional add before build if Ada wants explicit conf/risk flags; not required for approval given detailed stages and hand-verify checklist.

##### acceptable

- **Location:** Stage 3 optional `repo_json_revert` guard alignment
- **Finding:** Plan leaves existing hardcoded `("agent", "agent_task")` tuple on revert unless adjacent one-line change is convenient; new routes correctly use `get_repo_admin_json_table_keys()`.
- **Recommendation:** Aligning revert in Stage 3 is nice consistency; skipping is fine within child scope.

- **Location:** Betty / `orch.roles.betty-owns-test-tree`
- **Finding:** Removing `apply_repo_admin_json_at_startup` will break `tests/component/core/test_repo_admin_json.py` until Betty revises manifest in qa-child (plan acknowledges this).
- **Recommendation:** Expected pipeline — no Ada test edits.

#### Build

**Publish ref:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `f131f7d45ecbff3b946d58916d004f1cc6e8e5f8`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `e8a037b2` | `get_repo_admin_json_table_comparison` + `_normalized_row_maps` |
| 2 | `7ecb2895` | `export_repo_admin_json_table_to_file`; remove `apply_repo_admin_json_at_startup`; config/bootstrap docstrings |
| 3 | `f131f7d4` | `GET/POST /api/admin/repo_json/compare|write/<table_key>`; revert guard via `get_repo_admin_json_table_keys()` |

Hand-verify: `py_compile` on all touched `.py` files; compare `diverged` invariant checked at import time when env available. Full Flask smoke deferred to Betty manifest.

#### Radia review — AST-1505

**Rubric:** code-rubric.v2
**Ticket:** AST-1505
**Publish ref:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `c49368370d433a775de41f2bd266b69c10723744`
**Overall:** DISCUSS
**Diff:** `origin/dev...origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` — 10 files, +532/−45 (core compare/write + boot-apply removal, admin routes, Betty test manifest merge, plan doc)

---

#### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent dispatch / confidence paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade vector changes |
| astral.batch.batch-id-first | scoped | not-applicable | no batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | no batch paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths |
| astral.config.config-source-of-truth | scoped | conforms | `REPO_ADMIN_JSON_CONFIG` comment only; table defs unchanged |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env reads |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single child plan doc in diff |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty paths only in tests/test-bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree edits via Betty `merge-tests` SHA, not engineer product commits |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no external layer |
| astral.layers.import-direction | scoped | conforms | core→data/utils; ui→core/utils; no layer violations |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no frontend; API uses config table keys |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | compare/write routes use `@require_admin` (existing admin pattern) |
| astral.seed.agent-tables-in-repo-json | scoped | needs-discussion | product removes boot apply entry point; statute still documents kill-switch no-op as conforming |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog changes |
| astral.seed.boot-only-not-hot-path | scoped | conforms | bootstrap docstring: schema ensure only, no boot JSON apply |
| astral.seed.define-approved | scoped | not-applicable | no new seed catalog |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | boot does not re-apply repo JSON; operator DB edits survive restart |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer changes |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py / migration changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug logging added |
| astral.standards.dry-and-focused-functions | scoped | conforms | `_normalized_row_maps` shared; removed dead logger with apply removal |
| astral.standards.in-scope-only | scoped | conforms | no frontend, no statute files, no sibling-table smuggling |
| astral.standards.logging-via-utils | scoped | conforms | removed unused `get_logger` import with apply removal |
| astral.standards.names-not-ticket-ids | scoped | conforms | public helpers named by behavior |
| astral.standards.no-cross-contamination | scoped | conforms | repo JSON surface only |
| astral.standards.no-hardcoded-sets | scoped | conforms | routes/revert use `get_repo_admin_json_table_keys()` |
| astral.standards.public-then-helpers | scoped | conforms | new public helpers precede private maps in module |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | utils change is comment-only |
| astral.state.core-decides-transitions | scoped | not-applicable | no job/state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state paths |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend |
| astral.ui.naming-conventions | scoped | conforms | route names match existing `repo_json_*` pattern |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1505)` lands Betty manifest at publish tip |
| orch.git.commit-vocabulary | universal | conforms | stage commits follow vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub-branch topology respected |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/AST-1455/...` |
| orch.git.merge-on-checkout | universal | conforms | no checkout violations in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review on AST-1455 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs origin/dev baseline |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no unresolved product forks |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 delivered per plan |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped child ticket |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | statute amendment deferred to parent per Joan/plan |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns merged test manifest |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path engineer commits in product stages |

Registry table: 63 active rows scored (README cites 65 corpus; 2 not in harvested table).

---

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan / parent cite no catalog patterns |

---

#### Plan adherence

Stages 1–3 are implemented on the publish tip:

- **`get_repo_admin_json_table_comparison`** + **`_normalized_row_maps`** — structured diff with empty lists when aligned; field-level `changed_rows` on DB edit (tested).
- **`export_repo_admin_json_table_to_file`** — writes one table’s JSON only (tested); sibling file untouched.
- **`apply_repo_admin_json_at_startup`** removed from module and `__all__` (tested).
- Bootstrap + `REPO_ADMIN_JSON_CONFIG` comments updated to AST-1455 permanent semantics.
- Admin **`GET /repo_json/compare/<table_key>`** and **`POST /repo_json/write/<table_key>`** — thin wrappers, `@require_admin`, config-driven `table_key` guard, 400/500 handling matching revert pattern.
- **`repo_json_revert`** guard aligned to `get_repo_admin_json_table_keys()` (plan optional item — done).
- No `RepoJsonDivergenceBanner.tsx` / frontend scope (AST-1506).
- Hand-verify Flask smoke deferred to Betty manifest per plan; Betty manifest merged at tip.

**Estimate (5):** footprint matches — core helpers, two routes, doc cleanup, Betty tests; no scope creep.

**Joan:** plan-rubric APPROVED attached; no Excluded statute list in artifact → no straggler callouts.

---

#### Findings


##### discuss

- **Location:** `astral.seed.agent-tables-in-repo-json` / parent AST-1455 canon track
- **Finding:** Statute still lists `apply_repo_admin_json_at_startup` no-op as a conforming kill-switch path. This diff permanently deletes that entry point — correct product behavior per plan, but statute corpus is stale.
- **Recommendation:** Track Archie statute amendment on parent AST-1455 (already noted in Joan plan review); do not block this child on canon file edits.

- **Location:** `src/core/repo_admin_json.py` — `get_repo_admin_json_table_comparison` `diverged` field (~line 138)
- **Finding:** Plan text specified returning `diverged` from `_repo_admin_json_table_diverged(conn, table_key)`; implementation derives `diverged` from `only_in_*` / `changed_rows`. Joan flagged duplicate I/O as optional optimization — implementation avoids re-read. For normal single-key-per-row data this matches status endpoint logic. Edge case: duplicate row keys in file/DB collapse in `_normalized_row_maps` but still appear in `_sorted_normalized_rows` — `compare.diverged` could disagree with `GET /status` `diverged`.
- **Recommendation:** Optional resolve-child tweak: call `_repo_admin_json_table_diverged` with already-fetched rows (narrowed helper) for guaranteed parity with status, or document duplicate-key as invalid input. Not blocking for current two-table catalog.

##### advisory

- **Location:** `docs/test-bible/core/bootstrap.md`
- **Finding:** Historical § still references AST-1502 kill-switch narrative; AST-1505 section notes supersession but full bootstrap bible sweep not done.
- **Recommendation:** Betty or parent close-out can tighten bootstrap bible prose.

- **Location:** `tests/component/core/test_repo_admin_json.py`
- **Finding:** Compare tests cover aligned + `changed_rows` paths; no explicit `only_in_file` / `only_in_database` cases.
- **Recommendation:** Betty may add if she wants fuller diff-list coverage.

- **Location:** `tests/component/ui/api/test_api_admin.py`
- **Finding:** Write route success + 400 covered; no 500 surfacing test for write (compare has 500 test).
- **Recommendation:** Optional Betty addition.

---

#### What’s solid

- Thin admin API layer: validate table key from config → delegate to core → consistent error JSON.
- Per-table file write isolation tested (`task_path` stays `["unchanged"]` when exporting `agent`).
- Dead boot-apply stub and unused logger removed cleanly.
- Revert route hardcoded tuple replaced — consistent with new routes.
- Betty manifest at tip exercises compare invariant, export isolation, route wiring, and apply removal.

---

#### Frame diff

`(none)` — diff matches planned scope: core compare/write + boot-apply removal, admin routes, config/bootstrap comments, Betty test manifest, plan doc. No frontend (AST-1506), no `data/admin/**` edits, no `database.py` changes.

---

#### Notes

- Joan plan-rubric verdict attached (APPROVED @ `b14c091c`).
- No plan Excluded statutes → no straggler rows.
- C7 artifact complete for Chuckles writeback.

`context_tokens≈95000`

---

#### Resolution

**2026-08-26 — resolve-child (Ada)**

Radia **DISCUSS** @ `c4936837` — **no fix-now** items. Product tip unchanged.

| Finding | Action |
|---------|--------|
| Statute `astral.seed.agent-tables-in-repo-json` stale vs removed boot apply | Deferred to parent AST-1455 / Archie per plan Boundaries — no child canon edit |
| `diverged` derived from diff lists vs `_repo_admin_json_table_diverged` | Kept implementation — avoids duplicate I/O (Joan discuss); duplicate row keys not valid for current catalog |
| Bootstrap bible / Betty test coverage gaps | Advisory only — no engineer test-tree edits |

§9a dry-run: publish ref merges cleanly into `origin/dev` and `origin/ftr/AST-1455-show-differences-update-file`.

**Publish ref @ resolve:** `origin/sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write` @ `dde9a333`

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/repo_admin_json.py` | Structured per-table comparison; per-table DB→file export; r | `f201ae469` `7750fb62f` |
| ✓ | `src/core/bootstrap.py` | Confirm module docstring matches permanent no boot-apply (no | `f201ae469` |
| ✓ | `src/ui/api/api_admin.py` | `GET /api/admin/repo_json/compare/<table_key>`; `POST /api/a | `18d58dbab` |
| ✓ | `src/utils/config.py` | Update `REPO_ADMIN_JSON_CONFIG` header comment only — Revert | `f201ae469` |
| | _tests_ | — | 2 file(s) |

### AST-1506 — Show Differences and Update file on the divergence banner

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1506/show-differences-and-update-file-on-the-divergence-banner-add-show · Status at archive: Archive · Project: Astral Agent · Assignee: katherine · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1455_

#### What this implements

After #1. Adds the two labeled actions to the shared warning used by Manage Agents and Manage Tasks. **Show Differences** presents Ada's comparison. **Update file with table version** confirms, then writes that page's table only and refreshes the warning. Rewrites banner copy so it no longer claims restart/deploy overwrite. Does not change **Revert to file** confirm behavior.

#### Citations

`pattern.ui.shared-button-roles`, `pattern.ui.in-place-live-refresh`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`

#### Scope

- [X] `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — **modified** — **Show Differences** and **Update file with table version** on the shared warning; refresh after a successful file write; replace restart/deploy overwrite copy. `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — add secondary **Show Differences** that presents the comparison payload; add primary **Update file with table version** with confirm; on success refetch status the same way save/revert already do; rewrite the warning sentence so it no longer says restart/deploy will overwrite from the file.

#### Acceptance criteria

- [X] On Manage Agents, when personas diverge from the personas JSON, **Show Differences** lists the actual row and field differences (added rows, removed rows, changed fields with file vs table values). It does not include task-prompt drift.
- [X] On Manage Tasks, when task prompts diverge from the task JSON, **Show Differences** lists the actual row and field differences. It does not include persona drift.
- [X] After **Update file with table version** on Manage Agents, the agents warning clears, and the tasks warning is unchanged if tasks still diverge.
- [X] After **Update file with table version** on Manage Tasks, the tasks warning clears, and the agents warning is unchanged if personas still diverge.
- [X] Cancel on the Update confirm does not write the file; divergence stays.
- [X] Divergence banner copy no longer tells the operator that the next restart or deploy will overwrite the live table from the file.

#### Boundaries

- [X] Does not own core compare/write or startup-apply removal (sibling #1 Ada). Does not change **Revert to file** confirm behavior.

#### Notes for planning

Parent AST-1455 definition is authoritative. After sibling #1 (Ada API must exist first).

##### Comments


###### radia — 2026-08-26T18:42:17.558Z

[code-rubric] PROCEED (Commit: 0bc099bf) banner Show Update wired

###### betty — 2026-08-26T18:39:20.815Z

`origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner` @ `0bc099bf` · banner Show Update manifest

###### joan — 2026-08-26T18:35:28.852Z

[plan-rubric] PROCEED (Commit: 744bf4a) banner Show Update wired

###### katherine — 2026-08-26T18:33:40.089Z

origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner @ `744bf4a51fae6cac5031de432a60dc446469fd82` · banner Show/Update wired

---

#### UAT fitness

- **AC restored:** Parent AC — *"On Manage Agents, when personas diverge from the personas JSON, **Show Differences** lists the actual row and field differences (added rows, removed rows, changed fields with file vs table values). It does not include task-prompt drift."* and *"After **Update file with table version** on Manage Agents, the agents warning clears, and the tasks warning is unchanged if tasks still diverge."* (symmetric for Manage Tasks / `agent_task`.)
- **Correct outcome:** Operator opens the divergence warning on the page they are on, inspects a readable diff for **that table only**, and can persist the live table to that table's repo JSON without leaving the page; banner clears for that table after a successful write; sibling-table warning unchanged.
- **Sibling check:** AST-1505 owns compare/write API + core helpers; this ticket only calls them from React. Existing `GET /status`, `POST /revert/<table_key>`, page `refreshToken` / `onReverted` wiring unchanged except write success also calls `fetchStatus()` and `onReverted?.()` like revert. Per-table isolation verified by sibling tests — UI must pass `tableKey` from props only, never hardcode both tables.
- **Not sufficient:** Rewriting banner copy without working Show/Update actions, or calling CLI export instead of `POST /write/<table_key>`.
- **Wrong fix rejected:** Fetching compare for both tables on one page, writing both JSON files from one button, or re-adding restart-overwrite messaging — all violate parent boundaries and AST-1505 per-table contract.

#### Scope gate

All files and change kinds below are taken from this ticket's **## Scope** only. Out of scope: `src/core/**`, `src/ui/api/**`, `src/utils/config.py`, `src/data/**`, `data/admin/**`, `tests/**`, `docs/test-bible/**`, statute files, git commit/push from the product.

#### Stage 1: Warning copy and Show Differences modal

**Done when:** When `status.diverged` is true, the banner shows rewritten copy (no restart/deploy overwrite claim), a secondary **Show Differences** button, and the existing **Revert to file** button unchanged. Clicking **Show Differences** opens `Modal` with three readable sections populated from `GET /api/admin/repo_json/compare/<tableKey>`. Manage Agents uses `tableKey="agent"`; Manage Tasks uses `tableKey="agent_task"` — each sees only its table's diff. `cd src/ui/frontend && npx tsc -b --noEmit` passes. No **Update file** button yet.

1. In `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx`, add:
```ts
   import Modal from "./Modal"
```

2. Add file-local types matching AST-1505 compare JSON (do not import from backend):
```ts
   type CompareFieldChange = {
     field: string
     file_value: unknown
     database_value: unknown
   }

   type CompareChangedRow = {
     row_key: string
     fields: CompareFieldChange[]
   }

   type ComparePayload = {
     table_key: string
     diverged: boolean
     repo_relative_path: string
     only_in_database: Record<string, unknown>[]
     only_in_file: Record<string, unknown>[]
     changed_rows: CompareChangedRow[]
   }
```

   Add row-key helper:
```ts
   const ROW_KEY_FIELD: Record<TableKey, string> = {
     agent: "agent_id",
     agent_task: "task_key",
   }

   function rowLabel(row: Record<string, unknown>, tableKey: TableKey): string {
     const col = ROW_KEY_FIELD[tableKey]
     const v = row[col]
     return typeof v === "string" && v ? v : String(v ?? "(missing key)")
   }

   function formatCellValue(value: unknown): string {
     if (value === null || value === undefined) return "—"
     if (typeof value === "string") return value
     return JSON.stringify(value)
   }
```

3. Add state next to existing `reverting` / `error`:
```ts
   const [diffOpen, setDiffOpen] = useState(false)
   const [diffLoading, setDiffLoading] = useState(false)
   const [diffError, setDiffError] = useState<string | null>(null)
   const [diffData, setDiffData] = useState<ComparePayload | null>(null)
```

4. Replace the warning `<span>` body (lines ~99–103) with copy that **does not** mention restart, deploy, or `export_repo_admin_json.py`. Use exactly:
```tsx
   Local <strong>{meta.label}</strong> in the database differ from <code>{path}</code>.
   {" "}Use <strong>Show Differences</strong> to inspect drift,{" "}
   <strong>Update file with table version</strong> to write the live table to the repo JSON file, or{" "}
   <strong>Revert to file</strong> to restore the database from the checked-in file.
```

5. Add `async function openDiff()`:
   - `setDiffOpen(true)`; `setDiffLoading(true)`; `setDiffError(null)`; `setDiffData(null)`
   - `const r = await api(\`/api/admin/repo_json/compare/${tableKey}\`)`
   - Parse JSON; if `!r.ok`, throw using `data.error` string when present
   - `setDiffData(data as ComparePayload)`; clear error
   - `catch` → `setDiffError(message)`; `finally` → `setDiffLoading(false)`

6. In the button row (`div` with **Revert to file**), insert **before** the revert button:
```tsx
   <button
     type="button"
     className="btn secondary"
     disabled={reverting}
     onClick={() => void openDiff()}
   >
     Show Differences
   </button>
```

   Keep **Revert to file** button markup and `handleRevert` **unchanged** (same confirm title, labels, variant `"danger"`, POST path).

7. Render diff modal at the bottom of the component (sibling to the warning `div`, still inside the fragment returned when diverged):
```tsx
   <Modal
     open={diffOpen}
     onClose={() => setDiffOpen(false)}
     title={`Differences — ${meta.label}`}
     showFooter={false}
     size="wide"
   >
```

   Body content:
   - If `diffLoading`: `<p style={{ fontSize: 13 }}>Loading comparison…</p>`
   - Else if `diffError`: error text in `var(--error, #f87171)`
   - Else if `diffData`:
     - **Rows only in database** — if `only_in_database.length === 0`, show `(none)`; else `<ul>` of `rowLabel(row, tableKey)` for each row
     - **Rows only in file** — same for `only_in_file`
     - **Changed fields** — if `changed_rows.length === 0`, show `(none)`; else for each `changed_rows` entry, a subsection titled `Row: {row_key}` with a `<table className="list-page-table">` (or plain `<table>` with `width: 100%`, `fontSize: 13`) columns **Field**, **File**, **Database**. Cell text from `formatCellValue`. For any cell where formatted length &gt; 120, wrap in `<pre style={{ maxHeight: "8em", overflow: "auto", margin: 0, whiteSpace: "pre-wrap" }}>` instead of bare text.
   - If modal opens with empty payload and not loading/error, show `(no differences reported)`

   ⚠️ **Decision:** Diff presentation stays in this file — no new component module; `Modal` + inline lists/tables match existing admin read-only patterns.

#### Stage 2: Update file with table version and post-write refresh

**Done when:** Diverged banner shows primary **Update file with table version** between **Show Differences** and **Revert to file**. Confirm cancel leaves DB/file unchanged (no POST). Confirm OK calls `POST /api/admin/repo_json/write/<tableKey>`, then `fetchStatus()` and `onReverted?.()` on success — same refresh pattern as revert. Button shows `in-flight` class while the POST is in flight. Failed write surfaces inline error without clearing the warning. `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. Add `const [updating, setUpdating] = useState(false)` next to `reverting`.

2. Add `async function handleUpdateFile()`:
   - `const ok = await confirm(`Write the current live ${meta.label} to ${path}? This overwrites the checked-in repo JSON file on this host. Committing in git is a separate step.`, { title: "Update file with table version", confirmLabel: "Update file with table version", cancelLabel: "Cancel", variant: "default" })`
   - If `!ok`, return (no API call)
   - `setUpdating(true)`; clear banner `error`
   - `POST` to `/api/admin/repo_json/write/${tableKey}`
   - On success: `fetchStatus()` then `onReverted?.()` (same order as `handleRevert`)
   - On failure: set `error` message
   - `finally`: `setUpdating(false)`

3. Insert button between **Show Differences** and **Revert to file**:
```tsx
   <button
     type="button"
     className={updating ? "btn primary in-flight" : "btn primary"}
     disabled={updating || reverting}
     onClick={() => void handleUpdateFile()}
   >
     {updating ? "Updating…" : "Update file with table version"}
   </button>
```

4. Update **Show Differences** and **Revert to file** buttons: add `disabled={updating || reverting}` (revert already had `disabled={reverting}` — extend both).

5. Do **not** change `handleRevert` confirm strings, variant, or POST handler.

⚠️ **Decision:** `onReverted?.()` after write keeps page-level `refreshToken` / list reload behavior aligned with revert and save paths (`pattern.ui.in-place-live-refresh` — silent status refetch, no full-page remount).

#### Estimate

Confirm Chuckles estimate: 2 — agree

#### Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner`
**Product commits:** `3c43c353` (sync ftr — AST-1505 compare/write API), `02f3aca7` (Stage 1 — Show Differences modal + copy), `01a2f5b3` (Stage 2 — Update file with table version)

**Implemented:**
- `RepoJsonDivergenceBanner.tsx` — rewritten warning copy; **Show Differences** opens wide `Modal` with `GET /compare/<tableKey>` payload; **Update file with table version** confirm + `POST /write/<tableKey>` + `fetchStatus()` / `onReverted?.()`; **Revert to file** unchanged

**Tests:** Betty at Code Complete (`qa-child`) — engineers do not land test-tree changes.

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1506
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner` @ `744bf4a51fae6cac5031de432a60dc446469fd82`

##### Traceability

AC1–2 → Stage 1 `openDiff()` + `GET /compare/${tableKey}` modal (props `tableKey` isolates agent vs agent_task); AC3–4 → Stage 2 `handleUpdateFile()` + `POST /write/${tableKey}` then `fetchStatus()`; AC5 → Stage 2 confirm early-return (no POST on cancel); AC6 → Stage 1 rewritten warning span (no restart/deploy/CLI export copy); parent Revert AC → unchanged `handleRevert` per Boundaries.

##### Findings


###### discuss

- **Location:** Stage 2 decision note / `pattern.ui.in-place-live-refresh`
- **Finding:** Ticket cites `pattern.ui.in-place-live-refresh`, which remains `status: proposed` in canon — not approved catalog law. Plan does not import `useInPlaceLiveRefresh`; it mirrors the existing revert path (`fetchStatus` + `onReverted?.()`).
- **Recommendation:** Fine to build as written. Optionally soften the pattern citation to "same refresh contract as revert" so Joan/Radia do not treat a proposed id as mandatory hook adoption.

- **Location:** Stage 1 `ROW_KEY_FIELD` / `astral.standards.no-hardcoded-sets`
- **Finding:** Row-key column names (`agent_id`, `task_key`) are duplicated in React for `rowLabel`, parallel to core `_REPO_JSON_ROW_KEY`.
- **Recommendation:** Acceptable for this two-table banner with a `TableKey` union and per-page `tableKey` prop. Optional future: expose key column from compare payload if a third admin table joins the warning.

- **Location:** Plan structure / R6 self-assessment
- **Finding:** No `## Self-Assessment` section (Estimate confirm line present).
- **Recommendation:** Optional add before build; stages and hand-verify pre-flight are otherwise explicit.

###### acceptable

- **Location:** Stage 2 button order / `pattern.ui.shared-button-roles`
- **Finding:** **Revert to file** stays `btn secondary` (not `danger`) per "do not change Revert" boundary; confirm dialog still uses `variant: "danger"`.
- **Recommendation:** Matches ticket Boundaries; destructive styling on the labeled button itself is out of scope.

- **Location:** Pre-flight / sibling AST-1505
- **Finding:** Plan requires Ada compare/write routes on the epic line before build; ticket Notes say "after #1."
- **Recommendation:** `build-child` pre-flight grep is the right gate; Katherine should not re-implement API in this ticket.

#### Radia review

**Rubric:** code-rubric.v2
**Ticket:** AST-1506
**Publish ref:** `origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner` @ `0bc099bf5c3f9d4ac4264b125eec58d321a087b5`
**Overall:** CLEAN
**Diff:** `origin/dev...origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner` — AST-1506 product commits (`02f3aca7`, `01a2f5b3`): `RepoJsonDivergenceBanner.tsx` only (+212/−23).

##### Plan adherence

Stages 1–2 delivered: warning copy rewritten; Show Differences modal via GET compare; Update file with confirm + POST write + fetchStatus/onReverted; Revert unchanged; per-table isolation via props `tableKey`.

##### Findings (advisory only)

- `ROW_KEY_FIELD` duplicates core row-key columns — acceptable for two-table banner (Joan acceptable).
- Betty tests omit explicit only_in_database/only_in_file modal rendering — optional addition, not blocking.
- Modal list keys could collide in edge cases — optional index suffix if UAT surfaces.
- Statute `astral.seed.agent-tables-in-repo-json` lag on sibling AST-1505 — parent close-out, not AST-1506 blocking.

**No fix-now or discuss findings on Katherine's banner implementation.**

#### Bug: AST-1511 — Show Differences modal does not scroll


##### As-is

On Manage Agents or Manage Tasks, when the divergence warning is shown and the operator clicks **Show Differences**, the wide modal opens but the body does not scroll. Content below the first viewport (Susan saw only the first three differences) is clipped and unreachable.

##### To-be

The **Show Differences** modal scrolls inside the dialog so the operator can review every section — rows only in database, rows only in file, and all changed-field tables — without closing the modal.

##### Repro

1. Sign in as admin; open **Manage Tasks** (or **Manage Agents**) with live table diverged from repo JSON (multiple `changed_rows` and/or long field values — e.g. several task keys with `content` drift).
2. Click **Show Differences** on the gold divergence banner.
3. Observe the modal title **Differences — …** and the first diff sections render.
4. Attempt to scroll (wheel, trackpad, or scrollbar) to rows/fields below the fold.
5. **Actual:** no scroll; content below ~first three differences is not visible. **Expected:** modal body scrolls to reveal all diff sections.

Component-test shape (Betty): mock `GET /api/admin/repo_json/compare/<tableKey>` with `changed_rows` length ≥ 4 (or tall `content` strings); after opening modal, assert a later row label (e.g. 4th `row_key`) is reachable via `scrollIntoView` / container `scrollTop` / `within(modal-body).getByText(...)` after scroll helper — no browser UAT required for make-fix.

##### Root cause

AST-1506 Stage 1 renders the compare payload inside shared `Modal` with `size="wide"`. In `App.css`, `.modal-card--wide .modal-body` sets `overflow: hidden` and `padding: 0` so wide modals can host nested SideTabPanel layouts with their own scroll regions. The diff modal places content **directly** in `modal-body` with no inner scroll wrapper (unlike `.email-html-source`, which wraps content in `height: 100%; overflow: auto`). Tall diff output is clipped by the fixed `90vh` card.

##### Proposed change

**File:** `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` only.

1. Inside the **Show Differences** `<Modal … size="wide" showFooter={false}>`, wrap **all** body branches (loading, error, `diffData`, empty fallback) in one scroll container:
```tsx
   <div
     style={{
       padding: "20px",
       height: "100%",
       overflowY: "auto",
       boxSizing: "border-box",
     }}
   >
     {/* existing loading / error / diffData / empty content unchanged */}
   </div>
```

2. Do **not** change `Modal.tsx`, `App.css`, compare API, button labels, Update/Revert handlers, or `size="wide"` (table needs horizontal room).

3. **Done when:** With a compare payload taller than the viewport, the inner wrapper scrolls; header (title + ×) stays fixed; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

⚠️ **Decision:** Fix locally in the banner component (same pattern as `.email-html-source` inner scroll) rather than changing global `.modal-card--wide .modal-body` — avoids regressing SideTabPanel wide modals site-wide.

##### Blast radius

- **Show Differences modal only** on Manage Agents / Manage Tasks — no other `Modal` call sites.
- **AST-1506** Show/Update/Revert behavior and API wiring unchanged.
- Betty may extend `test_RepoJsonDivergenceBanner.test.tsx` (AST-1511) for multi-row scroll reachability; engineer does not edit `tests/` or `docs/test-bible/**`.

##### What must still hold

- Parent AST-1455 AC: **Show Differences** lists actual row and field differences for **that page's table only** (`tableKey` prop); must include rows beyond the first viewport when drift is large.
- **Update file with table version** and **Revert to file** confirm/POST behavior unchanged (AST-1506 Boundaries).
- Wide modal layout preserved for three-column Field / File / Database tables.
- Per-cell `<pre>` scroll for long values (AST-1506 Stage 1) remains; this fix is modal-level scroll for many rows/sections.

#### Radia review-fix — AST-1511

**Rubric:** code-rubric.v2
**Ticket:** AST-1511
**Parent:** AST-1455 (normal — `origin/ftr/AST-1455-show-differences-update-file` exists; not orphaned)
**Publish ref:** `origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` @ `46870882ca8f19ff85869a2a195f0c8bbb916c49`
**Overall:** CLEAN
**Diff base:** `origin/ftr/AST-1455-show-differences-update-file...origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` (mandated fix-lane base)

**Diff-base note:** Three-dot diff spans 25 files (+931/−63) — sibling fixes (AST-1512, AST-1513, AST-1515, etc.) merged on `sub/AST-1455/AST-1511` ahead of `ftr`. **AST-1511 footprint:** product commit `46870882` (`RepoJsonDivergenceBanner.tsx` only, +67/−57); Betty `test(AST-1511): bug-repro` @ `1d1b236a` merged @ `dbc44800`. Statute sweep and findings below target AST-1511 footprint; sibling paths on the sub tip are not re-audited in this pass.

---

#### Fix-specific checks


##### `[bug-repro]` — OK

**Test:** `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` — `RepoJsonDivergenceBanner — AST-1511` → `[bug-repro] Show Differences modal scrolls to later changed rows`

**Assertions (concrete, tied to To-be):**
- Mocks `GET /compare/agent_task` with `tallComparePayload(4)` — four `changed_rows`, each with 200-char `content` values (tall enough to exceed viewport).
- After opening modal, locates `.modal-card--wide .modal-body` → `firstElementChild` scroll wrapper.
- **Pins fix contract:** `scrollWrap.style.overflowY === "auto"` and `scrollWrap.style.height === "100%"` — matches plan-fix `## Proposed change` inline styles exactly.
- Asserts 4th row label `Row: drift_row_4` reachable after `scrollWrap.scrollTop = scrollWrap.scrollHeight`.

**Pre-fix plausibility:** Pre-AST-1511, modal body content sat directly under `.modal-body` (no inner wrapper). `firstElementChild` would be a `<p>` or content `<div>` without `overflowY: auto` — style assertions **fail**. Correct repro-first shape.

**Caveat (advisory, not fix-now):** `toBeVisible()` after manual `scrollTop` is weak in jsdom (no real layout clip). Primary guard is structural wrapper + overflow styles; acceptable for component tier.

##### `## What must still hold` — OK

| Item | Verdict |
|------|---------|
| Show Differences lists row/field diffs for **that page's `tableKey` only** | OK — `openDiff()` still calls `/compare/${tableKey}`; modal sections unchanged |
| **Update file** and **Revert to file** confirm/POST behavior unchanged | OK — `handleUpdateFile` / `handleRevert` untouched in `46870882` |
| Wide modal layout for Field/File/Database tables | OK — `size="wide"` retained; tables unchanged |
| Per-cell `<pre>` scroll for long values (`diffCellContent`) | OK — helper untouched; modal-level scroll is additive |

---

#### Statutes checked

Scored against AST-1511 footprint (`RepoJsonDivergenceBanner.tsx` + Betty bug-repro test).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no dispatch |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade vector |
| astral.batch.batch-id-first | scoped | not-applicable | no batch |
| astral.batch.batch-id-format | scoped | not-applicable | no batch |
| astral.batch.claim-process-release | scoped | not-applicable | no batch |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch |
| astral.config.config-source-of-truth | scoped | not-applicable | no config |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next |
| astral.docs.features-single-file-per-ticket | scoped | conforms | plan-fix patch in parent AST-1506 feature doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty test-tree only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer product commit: one TSX file only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | frontend only |
| astral.layers.import-direction | scoped | conforms | no new imports; Modal import pre-existing |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | `tableKey` prop still drives compare URL |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | still calls authenticated admin routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed/boot paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no bootstrap |
| astral.seed.define-approved | scoped | not-applicable | no seed catalog |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no boot apply |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug logging |
| astral.standards.dry-and-focused-functions | scoped | conforms | minimal wrapper; comment explains why |
| astral.standards.in-scope-only | scoped | conforms | single file per plan-fix blast radius |
| astral.standards.logging-via-utils | scoped | conforms | no logging added |
| astral.standards.names-not-ticket-ids | scoped | conforms | N/A |
| astral.standards.no-cross-contamination | scoped | conforms | Show Differences modal only |
| astral.standards.no-hardcoded-sets | scoped | conforms | no new hardcoded table sets |
| astral.standards.public-then-helpers | scoped | conforms | N/A |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils |
| astral.state.core-decides-transitions | scoped | not-applicable | no state machine |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job states |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run chain |
| astral.ui.frontend-file-placement | scoped | conforms | component path unchanged |
| astral.ui.naming-conventions | scoped | conforms | N/A |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1511)` at tip ancestry |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1511)` / `test(AST-1511)` |
| orch.git.flow-direction-inviolable | universal | conforms | fix sub on ftr line |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1455/AST-1511-*` |
| orch.git.merge-on-checkout | universal | conforms | N/A |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | N/A |
| orch.git.no-dev-agent-branches | universal | conforms | N/A |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1455 worktree |
| orch.git.three-permanent-branches | universal | conforms | ftr base used |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | localized CSS workaround per plan decision |
| orch.pipeline.plan-is-bible | universal | conforms | matches `## Proposed change` exactly |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped fix |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | N/A |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty bug-repro |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | single TSX product file |

Registry: 63 active rows scored.

---

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan-fix cites `.email-html-source` pattern by analogy, not a catalog id |

---

#### Plan adherence

**`## Proposed change` delivered** in `46870882`:
- Inner scroll wrapper wraps **all** modal body branches (loading, error, `diffData`, empty).
- Styles: `padding: 20px`, `height: 100%`, `overflowY: auto`, `boxSizing: border-box` — match plan.
- `Modal.tsx`, `App.css`, compare API, button labels, Update/Revert handlers, `size="wide"` — untouched.
- In-code comment documents root cause (`.modal-card--wide .modal-body` `overflow: hidden`).

**Root cause / To-be:** Addresses clipped tall compare output; operator can scroll all sections inside dialog while header stays fixed (wrapper inside `modal-body`, not global CSS change — correct blast-radius decision).

**Blast radius:** Show Differences modal only — confirmed.

---

#### Findings

**No fix-now or discuss findings.**

##### advisory

- **Location:** `[bug-repro]` test — `toBeVisible()` after `scrollTop`
- **Finding:** jsdom does not model overflow clipping; structural style assertions are the real gate.
- **Recommendation:** Susan hand-verify on staging if desired; not blocking.

- **Location:** Diff base `ftr...sub`
- **Finding:** Sub tip carries sibling fix commits not yet on `ftr`; unrelated to AST-1511 product quality.
- **Recommendation:** `merge-child` / ftr rollup handles separately; do not attribute sibling diffs to this fix review.

---

#### What's solid

- Localized fix mirrors existing `.email-html-source` inner-scroll pattern — avoids site-wide `.modal-card--wide` regression.
- All modal states (loading/error/empty/data) scroll consistently.
- AST-1506 Show/Update/Revert wiring preserved.
- Betty bug-repro pins wrapper contract and 4-row payload; fails pre-fix.

---

#### Frame diff

AST-1511 frame = inner scroll `<div>` in Show Differences `Modal` + Betty `[bug-repro]` test + plan-fix patch in AST-1506 feature doc. No API, CSS global, or sibling behavior changes in AST-1511 product commit.

---

#### Notes for Chuckles

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal AST-1455 | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` **skipped**) |

No `[board-betty]` / `[board-joan]` comments on issue doc — qa-fix ran with `[bug-repro]` test (valid; not clean-board opt-out absence issue).

C7 artifact complete.

`context_tokens≈72000`

---
```
[code-rubric] PROCEED (Commit: 46870882) modal scroll wrapper fixed
```

#### Resolution

**2026-08-27 — resolve-child (Katherine)**

Radia **PROCEED / CLEAN** @ `46870882` — **no fix-now** items. Product tip unchanged.

| Finding | Action |
|---------|--------|
| Advisory: jsdom `toBeVisible` after `scrollTop` weak | Deferred — structural `overflowY`/`height` assertions remain the gate |
| Advisory: sub tip carries sibling commits not on ftr | Deferred to `merge-child` / ftr rollup |

**§9a:** `origin/sub/AST-1455/AST-1511-…` @ pre-resolve tip conflicted with `origin/dev` (changed-in-both on plan doc, banner TSX, agent/candidate/config, test-bible). Merged `origin/dev` on the sub (`sync(dev)` @ `b065dcc8`); scroll wrapper retained. Dry-run clean into `origin/dev` and `origin/ftr/AST-1455-show-differences-update-file`.

#### Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

##### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1455 (parent) | ftr/AST-1455-show-differences-update-file |
| AST-1505 | sub/AST-1455/AST-1505-stop-startup-apply-structured-diff-per-table-file-write |
| AST-1506 | sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner |
| AST-1511 | sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll |

**Epic worktree:** `astral-AST-1455/` — one active sub checked out at a time.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | Add **Show Differences** modal + **Update file with table ve | `a549ac4a9` `69f04f10e` |
| | _tests_ | — | 1 file(s) |

### AST-1511 — Show Differences modal does not scroll

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1511/show-differences-modal-does-not-scroll · Status at archive: Archive · Project: Astral Agent · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1455_

##### Description

[bug]

The modal screen does not scroll, so I can only see the first three differences.

#### As-is

- [X] The Show Differences modal on Manage Agents / Manage Tasks does not scroll, so only the first few row/field differences are visible (Susan saw three).

#### To-be

- [X] The Show Differences modal scrolls (or otherwise shows all differences) so the operator can review every added/removed/changed row and field.

#### Suggested engineer

Katherine Johnson (AST-1506 — Show Differences banner/modal UI)

##### Comments


###### katherine — 2026-08-27T12:53:15.377Z

origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `b612660d` · §9a clean · ftr dry-run clean

###### radia — 2026-08-27T12:50:41.760Z

[code-rubric] PROCEED (Commit: 46870882) modal scroll wrapper fixed

###### chuckles — 2026-08-27T03:58:29.922Z

[check-linear] Tests Passed — not UAT yet; fix lane still needs review-fix, then User Testing, then merge into parent ftr. Parent prep-uat waits until AST-1511 is UT with AST-1505/AST-1506.

###### susan — 2026-08-27T03:57:28.404Z

@chuckles What's next? Is this ready for uat?

###### katherine — 2026-08-27T00:55:02.251Z

origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `46870882` · modal scrolls

###### betty — 2026-08-27T00:52:00.453Z

[bug-repro]
`origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` @ `dbc44800` · repro lands red, awaits fix

###### betty — 2026-08-27T00:51:49.593Z

[bug-repro]
`origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` @ `PENDING` · repro lands red, awaits fix

###### joan — 2026-08-27T00:50:38.295Z

[board-joan]  CANON: OK

###### betty — 2026-08-27T00:42:08.608Z

[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § AST-1506 — missing modal scroll reachability — extend test_RepoJsonDivergenceBanner.test.tsx with ≥4 changed_rows and assert 4th row_key reachable after scroll (plan-fix § Repro)

###### katherine — 2026-08-27T00:25:52.403Z

origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `daaef3d1829adc9f1c19a076f69a94eafa8728b8` · modal scroll wrapper

---

_Implementation detail may live in git history on `origin/dev`._

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| + unplanned | `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | — | `46870882c` |
| | _tests_ | — | 1 file(s) |
