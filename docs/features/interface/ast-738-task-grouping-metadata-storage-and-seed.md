<!-- linear-archive: AST-738 archived 2026-06-23 -->

## Linear archive (AST-738)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-738/task-grouping-metadata-storage-and-seed-organizing-tasks  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-734 — Organizing Tasks  
**Blocked by / blocks / related:** parent: AST-734; blocks: AST-740; blocks: AST-739

### Description

## What this implements

Persist four global-per-`task_key` grouping fields on agent task records: `task_group_order`, `task_group_name`, `task_seq`, and `task_name`. Run a one-time deploy migration that copies organized config `phase` / `seq` into the new columns wherever they exist today, derives initial `task_group_name` from `phase`, maps `task_group_order` from existing group ordering, and uses `task_key` as initial `task_name` where no separate name exists. Admin APIs read and write these fields on Manage Tasks save/load paths; list/enrich endpoints return them for UI consumers.

## Acceptance criteria

1. Deploy seed copies existing config `phase` / `seq` into the new DB fields for all catalog tasks that had them; initial `task_name` populated where appropriate.
2. Every catalog task key appears on Manage Tasks with stored `task_group_order`, `task_group_name`, `task_seq`, and `task_name`.
3. Manage Tasks edit modal exposes all four fields; saving persists them; reopening the modal shows saved values.
4. Invalid or inconsistent group data can be saved without server-side rejection (Susan verifies manually).

## Boundaries

* Does not build Manage Tasks or Scheduled Actions React layout — sibling Katherine ticket.
* Does not remove `phase` / `seq` from TASK_CONFIG — sibling Ada ticket after UI migration.
* Does not add validation beyond basic type/presence needed to save.
* Does not change dispatch execution, scheduler, or prompt content.

## Notes for planning

* Values are global per `task_key`, never candidate-specific.
* Seed must run before config keys are removed; migration reads config `phase`/`seq` once at deploy.
* `save_agent_task` / `get_agent_task` / list paths in data layer; `api_admin.py` task GET/PUT and `_enrich_tasks` must surface all four fields from DB only (not config) after this ticket lands.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-734-organizing-tasks`, child `sub/AST-734/<child-id>-task-grouping-metadata-storage-and-seed`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-18T22:36:34.255Z
**Review correction (§5d boundaries)**

Re-checked `origin/dev...origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` @ `273e906`.

The prior review comment stated no frontend / no `_dispatch_task_key_form_meta` changes. That was inaccurate for the three-dot diff: this branch also carries **`code(AST-739)`** commits (`d9dbdb6`, `487e0a2`, `736c306`) — `AdminTaskPrompts.tsx`, `AdminScheduledActions.tsx`, and `_catalog_task_grouping_meta` / `dispatch_task_keys` DB reads.

**AST-738 scope itself** (database seed/save, Manage Tasks GET/PUT/`_enrich_tasks`) still matches plan and has no fix-now blockers.

**discuss:** Epic-worktree branch contamination — AST-739 UI/dispatch work landed on the AST-738 publish ref. `@Chuckles` / `@Susan`: OK to leave for merge-child rollup, or should Hedy revert AST-739 commits from `sub/AST-734/AST-738-*` before `resolve-child`? Separate publish ref `origin/sub/AST-734/AST-739-*` exists with its own test manifest.

No status change; correction only.

#### radia — 2026-06-18T22:34:46.089Z
**Review** — `origin/dev...origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` @ `273e9066` (includes doc commit)

### Plan fidelity
Stages 1–3 delivered: four `agent_task` columns, idempotent seed (`backfill_task_grouping_metadata` + `_apply_ast738_*`), data-layer read/write with metadata-only in-place updates, admin GET/PUT/`_enrich_tasks` sourcing grouping from DB with backward-compat `phase`/`seq`. Boundaries respected — no frontend, no config key removal, no dispatch form meta changes.

### Rubric (ASTRAL_CODE_RULES)
- **§1.3 DRY:** `seed_values_for_task_key` shared by migration, `sync_agent_tasks`, and insert path — matches plan.
- **§2.1 / §3.3:** Runtime API reads DB; lazy `_task_grouping_seed_helpers()` import documented in plan (acceptable exception chain).
- **§2.6 / versioning:** `content_changed` excludes grouping-only edits; prompt versioning copies grouping forward — critical plan Risk item handled correctly (`test_grouping_only_edit_keeps_version_uuid`, `test_segment_edit_copies_grouping_forward`).
- **Layer (B2):** `api_admin` changes stay on `database` facade — no new UI→data violations.

### fix-now
None.

### discuss
- **Seed guard edge case:** Guard skips when *any* `current=1` row has non-empty `task_group_name`. If an operator cleared **every** row’s name to `''`, the next `_ensure_agent_task_schema` would re-seed from `TASK_CONFIG`. AC allows invalid saves — @susan OK with that reset behavior, or tighten guard in a follow-up?

### advisory
- Sibling plan doc `ast-740-remove-phase-and-seq-from-task-config.md` on this branch — doc-only, no code smuggle.
- Stray `# placeholder removed = "qualify_job_listings"` in `test_agent_tasks.py` — optional cosmetic cleanup in resolve.

**Doc:** [combined plan + review table](docs/features/interface/ast-738-task-grouping-metadata-storage-and-seed.md#review-radia)

**Handoff:** Proceed to `resolve-child` — no blockers.

#### betty — 2026-06-18T22:27:16.104Z
## QA test manifest (AST-738)

**Publish:** `origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` @ `e07e751` (`merge-tests(AST-738): origin/tests aa7a342`)

### 1. New coverage
1. **Data layer — grouping columns + seed** (`TestAst738TaskGroupingMetadata`): `seed_values_for_task_key` from `TASK_CONFIG`; new-row defaults; metadata-only grouping edit keeps version UUID; segment edit copies grouping forward; `list_candidate_tasks` columns; backfill global guard when `task_group_name` already set.
2. **Admin API — Manage Tasks paths** (`TestAst738TaskGroupingApi`): `_grouping_from_agent_task_row` backward-compat `phase`/`seq`; GET surfaces DB grouping; PUT forwards four fields; invalid `task_seq` → 400.

### 2. Broken / revised tests
1. **`TestTaskRoutes::test_preview_task_and_get_update`** — `phase`/`seq` now come from DB grouping fields on the mocked `get_agent_task` row, not `TASK_CONFIG` overlay.

### 3. Existing coverage (unchanged)
- **`TestAst454SevenSegmentPersistence`** / **`TestSaveAgentTask`** — segment versioning baseline still applies; AST-738 extends metadata-only path to grouping kwargs.
- **`/dispatch_tasks/task_keys`** — still config-derived (**AST-739** scope); not in this manifest.

### Run (test-child)
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_tasks.py::TestAst738TaskGroupingMetadata \
  tests/component/ui/api/test_api_admin.py::TestAst738TaskGroupingApi \
  tests/component/ui/api/test_api_admin.py::TestTaskRoutes::test_preview_task_and_get_update \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### Bible shasum (`origin/sub/...`)
- `docs/test-bible/data/database/agent_tasks.md` `fe5a4bd526b9b3bdd06daa4d8c550c897bd92fe55f01e1cb7972c1b81741e8bd`
- `docs/test-bible/ui/api/api_admin.md` `8faa64011b69801e486de1ef1400e94f546dba1b0d065a49b36e65ef5e62cb9b`

#### hedy — 2026-06-18T22:16:12.215Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed/docs/features/interface/ast-738-task-grouping-metadata-storage-and-seed.md

**Scope:** `Single-Component` — `agent_task` storage, one migration script, Manage Tasks admin API only; no frontend or config cleanup.

**Conf:** `high` — reuses existing column migration, metadata-only save (run_next pattern), and admin enrichment; seed mapping from config is fully specified.

**Risk:** `Medium` — incorrect prompt versioning could drop grouping metadata on prompt edits; global seed guard must not clobber operator edits after first deploy.

#### hedy — 2026-06-18T22:15:49.796Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed/docs/features/interface/ast-738-task-grouping-metadata-storage-and-seed.md

**Scope:** `Single-Component` — `database.py` + `api_admin.py` only; four `agent_task` columns, one-time TASK_CONFIG seed, metadata save without prompt versioning, Manage Tasks API read/write with backward-compat `phase`/`seq` from DB.

**Conf:** `high` — mirrors existing `_apply_ast*` migrations and agent_task metadata-only update pattern; AST-568 documents the UI paths being swapped in AST-739.

**Risk:** `Medium` — wrong versioning on metadata-only save would drop operator grouping data; admin-only blast radius, no dispatch execution change.

React modal/list (AC #3–#5 UI) and `/dispatch_tasks/task_keys` DB reads are **AST-739**; config `phase`/`seq` removal is **AST-740**.

---

# Task grouping metadata storage and seed (Organizing Tasks)

**Linear:** [AST-738](https://linear.app/astralcareermatch/issue/AST-738/task-grouping-metadata-storage-and-seed-organizing-tasks)  
**Parent:** [AST-734](https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks)  
**Publish ref:** `sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed`

Susan wants task grouping and ordering editable in admin without redeploying config. This ticket adds four global-per-`task_key` fields on `agent_task` rows (`task_group_order`, `task_group_name`, `task_seq`, `task_name`), seeds them once from today's `TASK_CONFIG` `phase` / `seq`, and wires Manage Tasks API save/load paths to read and write DB values only. React list layout and Scheduled Actions grouping are **AST-739**; removing `phase` / `seq` from config is **AST-740**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add four columns; extend save/get/list/sync/copy-upsert; idempotent seed hook | data |
| `scripts/migrations/backfill_task_grouping_metadata.py` | Seed logic (callable + CLI); reads `TASK_CONFIG` `phase`/`seq` | scripts |
| `src/ui/api/api_admin.py` | PUT/GET `/tasks/<task_key>` and `_enrich_tasks` surface DB grouping fields; backward-compat `phase`/`seq` from DB | ui |

**Out of scope (this ticket):** `src/ui/frontend/**` (AST-739), `src/utils/config.py` phase/seq removal (AST-740), `_dispatch_task_key_form_meta` / `/dispatch_tasks/task_keys` (AST-739), `tests/**` (Betty after Code Complete).

## Stage 1: Schema columns and seed migration

**Done when:** Fresh and migrated databases have four new columns on `agent_task`; every `current=1` catalog row is seeded after first bootstrap; re-running seed does not overwrite operator edits.

1. In `scripts/migrations/backfill_task_grouping_metadata.py`, create a module with:
   - Docstring listing CLI usage: `python scripts/migrations/backfill_task_grouping_metadata.py [--dry-run]`
   - `def seed_values_for_task_key(task_key: str) -> dict`: read `cfg = TASK_CONFIG.get(task_key, {})`; `phase = (cfg.get("phase") or "").strip()`; `seq_raw = cfg.get("seq")`; return:
     - `task_group_name`: `phase if phase else "(unassigned)"`
     - `task_group_order`: `phase if phase else "ZZZ"`
     - `task_seq`: `float(seq_raw) if seq_raw is not None else 999.0`
     - `task_name`: `task_key`
   - `def backfill_task_grouping_metadata(conn, *, dry_run: bool = False) -> dict[str, int]`: assume caller ran `_ensure_agent_task_schema(conn)`. **Global guard:** `SELECT COUNT(*) FROM agent_task WHERE current = 1 AND task_group_name != ''` — if count > 0, return immediately (already seeded or operator-edited). Loop `get_task_keys()`; for each key SELECT `current=1` row; if none, count `skipped_no_row`. UPDATE with `seed_values_for_task_key` values. For orphan `current=1` rows whose `task_key` ∉ `get_task_keys()`, set unassigned defaults. Count `updated` / `skipped`. If `dry_run`, do not commit.
   - `if __name__ == "__main__"`: argparse `--dry-run`; connect with `ASTRAL_CONFIG["db_dir"] / "astral.db"`; print counts.

2. In `src/data/database.py` header inventory, extend the `agent_task` bullet: `task_group_order TEXT NOT NULL DEFAULT ''`, `task_group_name TEXT NOT NULL DEFAULT ''`, `task_seq REAL NOT NULL DEFAULT 999.0`, `task_name TEXT NOT NULL DEFAULT ''`.

3. In `_ensure_agent_task_schema(conn)`, after existing column migrations and **before** `_apply_ast469_select_job_page_run_next_migration(conn)`, add idempotent ALTERs for the four columns if missing (refresh `cols` after each add). Add columns to both CREATE TABLE DDL branches (empty table + v1 migration).

4. Add `def _apply_ast738_task_grouping_metadata_seed(conn)` that lazy-imports and calls `backfill_task_grouping_metadata(conn, dry_run=False)`. Call from `_ensure_agent_task_schema` after column adds and existing `_apply_ast*` migrations.

5. In `sync_agent_tasks`, extend INSERT for missing keys to include four columns from `seed_values_for_task_key(key)`.

6. At **end** of `sync_agent_tasks` (after insert loop, before `conn.commit()`), call `_apply_ast738_task_grouping_metadata_seed(conn)` so fresh DBs seed after catalog rows exist.

⚠️ **Decision:** Initial `task_group_order` equals config `phase` string (labels already sort lexicographically). Susan can rename/reorder groups in admin later.

⚠️ **Decision:** `task_seq` default `999.0` matches today's UI `(seq ?? 999)` fallback for unseeded rows.

⚠️ **Decision:** Global seed guard (any non-empty `task_group_name`) prevents deploy re-runs from clobbering operator edits.

## Stage 2: Data layer read/write

**Done when:** `save_agent_task`, `get_agent_task`, `list_candidate_tasks`, and `sync_agent_tasks` round-trip all four fields; metadata-only saves do not retire prompt versions; prompt-version inserts copy metadata forward.

1. Extend `_save_agent_task_on_connection` with optional kwargs: `task_group_order`, `task_group_name`, `task_seq`, `task_name` (`None` = leave existing).

2. Extend existing-row SELECT to include the four grouping columns.

3. **Insert path** (no existing row): use kwargs when provided, else `seed_values_for_task_key(task_key)` (import from migration module or re-export thin wrapper in `database.py`).

4. **Content-changed versioning path**: copy forward grouping fields from retired row unless kwargs override.

5. **In-place update path** (no prompt segment change): apply grouping updates alongside `agent_id` / `run_next`; coerce `task_seq` with `float(...)` when provided; strip strings; allow empty strings; do **not** set `content_changed`.

6. Extend public `save_agent_task(...)` to accept and forward the four kwargs.

7. In `list_candidate_tasks`, add the four columns to SELECT.

8. `apply_agent_task_copy_upsert`: new columns flow automatically via `table_columns(conn, "agent_task")` once schema exists.

## Stage 3: Admin API — Manage Tasks save/load paths

**Done when:** `GET/PUT /api/admin/tasks/<task_key>` and `GET /api/admin/tasks` expose grouping metadata from DB; backward-compat `phase`/`seq` keys come from DB (not config) until AST-739 switches the frontend.

1. In `src/ui/api/api_admin.py`, add helper `_grouping_from_agent_task_row(task: dict | None, task_key: str) -> dict`:
   ```python
   {
       "task_group_order": ...,
       "task_group_name": ...,
       "task_seq": ...,  # float
       "task_name": ...,
       "phase": task_group_name if task_group_name and task_group_name != "(unassigned)" else None,
       "seq": task_seq if task_seq != 999.0 else None,
   }
   ```
   When `task` is None: empty strings, `task_seq=999.0`, `task_name=task_key`, `phase=None`, `seq=None`.

2. **`get_task`:** Remove `cfg.get("phase")` / `cfg.get("seq")` overlay. Merge `_grouping_from_agent_task_row(task, task_key)`. Keep `entity_type` from `TASK_CONFIG`.

3. **`update_task`:** Read optional body keys `task_group_order`, `task_group_name`, `task_seq`, `task_name` using `if "field" in body` pattern. Pass to `save_agent_task`. Coerce `task_seq` with `float(...)` when present (400 only on non-numeric). No business-rule validation.

4. Return merged `get_agent_task` + `_grouping_from_agent_task_row` after PUT.

5. **`_enrich_tasks`:** Remove `cfg.get("phase")` and `cfg.get("seq")`. Spread `_grouping_from_agent_task_row(t, task_key)` into each row (columns from `list_candidate_tasks` after Stage 2).

6. Do **not** change `_dispatch_task_key_form_meta` or `/dispatch_tasks/task_keys` (AST-739).

⚠️ **Decision:** AC #3 (edit modal exposes four fields) is API-ready here; React inputs land in **AST-739**. Verify with PUT then GET before closing.

## Stage 4: Manual verification (build-child)

**Done when:** Local admin API returns seeded grouping metadata and accepts edits.

1. Bootstrap or touch DB to trigger schema ensure + seed.
2. `GET /api/admin/tasks?candidate_id=<any>` — known key has `task_group_name` matching former config phase.
3. `PUT /api/admin/tasks/<key>` with altered grouping fields; `GET` confirms persistence.
4. Confirm `_enrich_tasks` / `get_task` no longer read `phase`/`seq` from `TASK_CONFIG`.

## Self-Assessment

**Scope:** `Single-Component` — `database.py`, one migration script, and `api_admin.py` Manage Tasks paths only.

**Conf:** `high` — Follows established `agent_task` column migration, metadata-only update, and admin enrichment patterns.

**Risk:** `Medium` — Wrong versioning (retire on metadata-only save or drop metadata on prompt edit) would lose operator grouping work; blast radius is admin task management only.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | `seed_values_for_task_key` shared by CLI seed, `sync_agent_tasks`, and new-row insert. |
| §2.1 config | Seed reads `TASK_CONFIG` once; runtime API reads DB for grouping. Config untouched (AST-740). |
| §3.3 imports | Lazy import in `_apply_ast738` avoids load-time cycle. |
| §3.5 naming | Snake_case fields match ticket spec. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Built:** `origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` @ `1e6ab76` (`5b62160` data layer + seed, `1e6ab76` admin API).

**Out of build scope (Betty / qa-child):** component/API tests per build-child test-tree ban; React modal/list (AST-739).

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` @ `e07e751`

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | Stages 1–3 match plan: four columns, idempotent seed, `save`/`list`/`sync` paths, admin GET/PUT/`_enrich_tasks` from DB with backward-compat `phase`/`seq`. |
| Versioning (§2.6 / plan Risk) | `content_changed` excludes grouping-only edits; segment versioning copies grouping via `_resolved_grouping_fields`; tests lock both behaviors. |
| Boundaries (§5d) | No frontend, no `TASK_CONFIG` removal, no `_dispatch_task_key_form_meta` — sibling tickets untouched. |
| Layer / imports (§3.3) | Lazy `_task_grouping_seed_helpers()` documented in plan; `api_admin` uses `database` only. |
| Seed guard | Global `task_group_name != ''` skip matches plan; `sync_agent_tasks` pre-seeds inserts so fresh DBs need no second pass. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| advisory | `docs/features/interface/ast-740-remove-phase-and-seq-from-task-config.md` on this branch | Sibling AST-740 plan doc shipped with AST-738 commits — harmless doc-only; no code boundary leak. |
| advisory | `tests/component/data/database/test_agent_tasks.py` | Stray `# placeholder removed = "qualify_job_listings"` comment — cosmetic cleanup optional in resolve. |
| discuss | `backfill_task_grouping_metadata` guard | If an operator cleared **every** `current=1` row’s `task_group_name` to `''`, the next schema ensure would re-seed from config. AC allows invalid saves; confirm Susan is OK with that reset edge case or tighten guard later. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Proceed to `resolve-child` — no fix-now blockers | Hedy |
| Optional: drop placeholder comment in test file | Hedy (resolve) |
| AST-739: wire React modal to four DB fields | Katherine |

---

## Resolution (2026-06-18)

**Review:** Radia @ `273e906` — no fix-now items; proceed per handoff.

**Product changes:** None. AST-738 scope (data layer seed/save, Manage Tasks GET/PUT/`_enrich_tasks`) shipped as reviewed.

**Discuss (logged, no code change this pass):**
- **Seed guard reset:** If every `current=1` row has empty `task_group_name`, deploy re-seeds from `TASK_CONFIG`. Matches plan guard; AC allows invalid operator data — left as-is pending Susan follow-up if she wants a tighter guard.
- **Branch contamination:** AST-739 commits also appear on this publish ref (Radia correction @ `273e906`). AST-738 product scope unaffected; rollup via `merge-child` / sibling `sub/AST-734/AST-739-*` is Chuckles/Susan orchestration.

**§9a dry-run:** `origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` merges cleanly into `origin/dev` and `origin/ftr/AST-734-organizing-tasks`.

**Publish tip:** `origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` @ resolve commit.
