# Plan: AST-381 — Pushing database content to GitHub

**Linear:** https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github  
**Feature branch:** `betty/ast-381-pushing-database-content-to-github`

## Summary

Ship a **repo-tracked JSON snapshot** of allowlisted admin-related DB tables so code reviews and deploys can verify coupling with in-DB prompt/task content. Add **explicit** Administrator flows: generate export from current DB, preview read-only in UI, and import into a target DB with safeguards. **None** of this runs on server bootstrap; keep full independence from [AST-383](https://linear.app/astralcareermatch/issue/AST-383/corebootstrap-runtime-startup-orchestration-from-uiserverpy).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/administrator/admin-snapshot.schema.json` | Versioned JSON Schema for snapshot envelope + table payloads | docs |
| `docs/features/administrator/ast-381-pushing-database-content-to-github.md` | This plan (updated only if scope shifts) | docs |
| `src/utils/config.py` | `ADMIN_SNAPSHOT_CONFIG` block: `schema_version`, `allowed_tables` list (string keys only), optional `max_rows_per_table`, paths relative to repo root | utils |
| `src/core/admin_snapshot.py` | New: `build_snapshot_dict()`, `validate_snapshot_dict()`, `diff_snapshot_vs_db()` (dry-run), `apply_snapshot()` — all orchestration; call data layer for reads/writes | core |
| `src/data/database.py` | Header inventory if new helper tables none; add **read** helpers that return serializable rows for allowlisted tables and **write** helpers used only from `apply_snapshot` (parameterized table name from allowlist only) | data |
| `src/ui/api/api_admin.py` | New routes: `POST .../admin/snapshot/export`, `GET .../admin/snapshot/latest` (or file path param), `POST .../admin/snapshot/import` with `dry_run` body flag | ui |
| `src/ui/frontend/...` (new page or section under existing Admin) | Buttons: Export, Preview (render JSON tree or formatted table summary), Import with confirm + dry-run result panel | ui |

⚠️ **Decision:** Snapshot format is **one JSON file** with top-level keys `{ "schema_version", "exported_at", "tables": { "<table>": [ rows... ] } }`. Idempotency is row-level upsert by natural keys defined per table in config (e.g. `agent_task.task_key`); tables without a stable key are export-only until Susan defines merge rules.

## Stage 1: Config contract and schema

**Done when:** `ADMIN_SNAPSHOT_CONFIG` exists with allowlist and schema version constant; JSON Schema file validates the envelope shape in a unit test (no DB).

1. In `src/utils/config.py`, add `ADMIN_SNAPSHOT_CONFIG` after existing admin-related blocks (or after `ASTRAL_CONFIG` if no better anchor), with keys: `schema_version: 1`, `allowed_tables: [...]` starting with tables Susan names in ticket follow-up (minimum placeholder: `agent_task` only until expanded), `repo_relative_path: "data/admin_snapshot.json"` (or under `docs/` per final agreement — pick **one** path in config literal).
2. Add `docs/.../admin-snapshot.schema.json` describing required top-level keys and `tables` as object of string → array of objects.
3. Add `scripts/validate_admin_snapshot_schema.py` that loads the schema + a golden minimal JSON fixture under `docs/features/administrator/fixtures/` and validates (exit 0 on pass, nonzero on failure); wire no CI unless Susan already has a pattern for script checks.

## Stage 2: Core export / validate / dry-run / apply

**Done when:** Core functions exist; export reads only allowlisted tables; import refuses unknown tables and wrong `schema_version`; dry-run returns a structured diff without writing.

1. Create `src/core/admin_snapshot.py` with `get_logger(__name__)`.
2. Implement `build_snapshot_dict()` — for each key in `ADMIN_SNAPSHOT_CONFIG["allowed_tables"]`, call a new data helper `database.fetch_admin_snapshot_rows(table_key)` that maps key to a concrete SQL query **only** for known mappings (if/elif or dict of callables in data layer); unknown key raises `ValueError`.
3. Implement `validate_snapshot_dict(data: dict)` — checks schema version, allowed keys under `tables`, row shapes minimal (dict only).
4. Implement `diff_snapshot_vs_db(snapshot, dry_run=True)` — compares snapshot to current DB for listed tables; returns `{ "inserts": n, "updates": n, "deletes": n, "warnings": [...] }` without mutating when `dry_run`.
5. Implement `apply_snapshot(snapshot, ...)` — only after `validate_snapshot_dict` passes; uses transactions; logs batch_id if available via `log_batch_id` context where applicable.

## Stage 3: Data layer helpers

**Done when:** All SQL for snapshot lives in `database.py` (or existing pattern modules); no raw SQL from UI or core beyond calling these helpers.

1. In `src/data/database.py`, add `fetch_admin_snapshot_rows(table_key: str) -> list[dict]` and `apply_admin_snapshot_rows(table_key: str, rows: list[dict], mode: str)` with `mode in ("upsert", "replace")` per table policy in config.
2. Update `database.py` header table inventory if any new tables are introduced (prefer **no** new tables; reuse existing).

## Stage 4: Admin API

**Done when:** Authenticated admin routes return JSON; import requires `dry_run` first pass boolean; errors return JSON `{"error": "..."}` with appropriate HTTP status per `ASTRAL_CODE_RULES.md` §1.5 UI pattern.

1. In `src/ui/api/api_admin.py`, register routes under existing blueprint pattern. Use `@require_auth` on all three.
2. `POST /api/admin/snapshot/export` — calls core `build_snapshot_dict`, writes file to configured repo path (server cwd is repo root in dev), returns `{ "path", "sha256", "byte_size" }`.
3. `GET /api/admin/snapshot/preview` — reads file from configured path (or optional query `path=` restricted to under repo root — **reject** `..` segments); returns parsed JSON or 404.
4. `POST /api/admin/snapshot/import` — body `{ "dry_run": bool, "confirm_token": str | null }`. If `dry_run: true`, return diff only. If `dry_run: false`, require `confirm_token` matching server-generated value from a prior dry-run response (simple nonce stored in memory or signed JWT — document choice in code comment).

## Stage 5: Admin UI

**Done when:** Administrator can export, see preview panel, run dry-run import, then confirm import from UI without touching unrelated screens.

1. Add Admin UI section (exact page per existing navigation: extend `NAV_CONFIG` if a new route is added).
2. Wire `api()` client calls to the three endpoints; show errors in existing Toast pattern.
3. Preview: read-only `JSON.stringify(snapshot, null, 2)` in scrollable `<pre>` or use existing tabbed panel component.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches config, new core module, data helpers, admin API, and React admin UI across layers.

**Conf:** `Medium` — Pattern is established (admin API, config blocks) but table allowlist and merge semantics need Susan sign-off per environment.

**Risk:** `HIGH` — Wrong import could corrupt `agent_task` or related admin tables; mitigated by allowlist, dry-run, explicit confirm, and no auto-bootstrap.

## Plan vs ASTRAL_CODE_RULES

- §1.2: UI must not import `data`; core orchestrates snapshot; data holds SQL.  
- §2.1: All allowlists and paths from `ADMIN_SNAPSHOT_CONFIG`.  
- §1.5: UI API returns JSON errors; data raises; core catches and maps for API where appropriate.
