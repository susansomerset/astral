# AST-1501 — gap: seed statute carve-out for dispatch_task operator curation

Sibling gap of AST-1496 under mini-epic AST-1456. Stub for plan-fix.

## Bug: AST-1501 — gap seed statute carve-out

### As-is

`astral.seed.archie-catalog-wins` still states that Archie seed catalogs are ensured on boot and that deleting a meteorite/`dispatch_task` catalog row is temporary until the next ensure. Sibling statutes (`operator-rows-stay-deleted`, `other-via-coverage-join`, `astral.dispatch.seed-auto-false`) still draw a catalog-vs-operator bright line and use provision/`ensure_*` examples that assume those boot writers exist — contradicting the AST-1456 / AST-1496 product ban.

### To-be

Canon matches AST-1456: all live `dispatch_task` content is operator-curated (Manage Dispatch or Susan-run SQL from Linear comments). Boot/catalog ensure of `dispatch_task` rows is banned. Archie-named catalogs (`METEORITE_DISPATCH_TASKS`, `SEED_CONFIG` `dispatch_task-*`, mailbox/fetch catalogs) may remain as shape/docs / Linear paste material only — not an executable ensure authority. Sibling seed statutes’ prose and examples no longer require the provision paths AST-1496 removes.

### Repro

1. Read `canon/statutes/astral/seed/astral.seed.archie-catalog-wins.md` Conforming example: “Delete one meteorite pair in Scheduled Actions; next boot re-inserts it from `METEORITE_DISPATCH_TASKS`.”
2. Read AST-1496 plan `## To-be` / product ban: restart must not invent or recreate `dispatch_task` rows.
3. Conflict: following archie-catalog-wins as written requires the writers AST-1496 deletes; Joan `[board-joan] CANON: REVISE` on AST-1496 names this gap.

### Root cause

Seed statutes were written when catalog-wins + boot provision were policy for meteorite/`dispatch_task`. AST-1456 reversed that for `dispatch_task` only; statutes were not carved out when the product ban was planned.

### Proposed change

No product code in this gap (AST-1496 owns the ban). Canon only:

1. **`canon/statutes/astral/seed/astral.seed.archie-catalog-wins.md`**
   - **Statement:** Carve out `dispatch_task` explicitly. For all other Archie-named seed catalogs that remain in scope, existing “catalog wins / boot ensure” may stay. For `dispatch_task`: catalogs (`METEORITE_DISPATCH_TASKS`, `SEED_CONFIG` keys `dispatch_task-*`, and related mailbox/fetch catalog literals) are **not** authoritative for live row presence; boot and scheduler-start provision must **not** ensure or re-insert missing catalog rows. Lasting `dispatch_task` content changes are operator Manage Dispatch and/or SQL posted in Linear for Susan — not catalog ensure.
   - **Rationale:** Align with AST-1456 — curated schedule rows must survive restart; auto overwrite is forbidden.
   - **Examples — Conforming:** Operator deletes or edits a `dispatch_task` row; it stays as curated across restart (no catalog re-insert). Catalog SQL/shape text may be copied into a Linear comment for Susan to run when new rows are needed.
   - **Examples — Violating:** Boot or `start_scheduler` re-inserts deleted meteorite / `meteorite_email` / `fetch_email` (or any) `dispatch_task` rows from a Python/`SEED_CONFIG` catalog. Treat Scheduled Actions edits as temporary because “catalog will win on next boot.”
   - **Source docs:** add `docs/features/foundation/ast-1456-do-not-overwrite-dispatch-task.md` (and/or AST-1496 bug section) to `source_docs` frontmatter.

2. **`canon/statutes/astral/seed/astral.seed.operator-rows-stay-deleted.md`**
   - **Statement:** Expand to: **all** live `dispatch_task` rows are operator-owned for presence/content under AST-1456; product code must not re-insert **any** `dispatch_task` row on restart or schema ensure (not only “non-catalog” rows). Drop or rewrite the bright-line sentence that says catalog membership licenses resurrection.
   - **Examples:** Keep “hand-built row stays gone”; add/adjust so a deleted meteorite-catalog-shaped row also stays gone.
   - **Notes:** Point at the archie-catalog-wins `dispatch_task` carve-out; form defaults remain non-inserts.

3. **`canon/statutes/astral/seed/astral.seed.other-via-coverage-join.md`**
   - **Statement / Notes:** Clarify this statute does **not** authorize `dispatch_task` boot/provision (banned). Coverage-join remains the rule **if** Archie later approves a non-`dispatch_task` (or explicitly re-approved) seed path that inserts by scanning extant tables — it is not a standing requirement to run meteorite/`dispatch_task` provision loops.
   - **Examples:** Retire or reframe the conforming “Provision loops `SELECT candidate_id FROM candidate` then ensures catalog rows” so it is not read as required product behavior for `dispatch_task` after AST-1496. Violating hardcoded-id examples may remain as still-wrong **if** such a path existed.

4. **`canon/statutes/astral/dispatch/astral.dispatch.seed-auto-false.md`**
   - **Statement:** Keep CLICK-default for any seed/provision path that still inserts `dispatch_task` — and state that AST-1456/AST-1496 ban boot/`dispatch_task` provision; catalogs documenting shapes must still list `auto_mode` false.
   - **Examples:** Remove or reframe conforming examples that require `ensure_gaze_email_dispatch_task` / live provision reconcile as current product duty. Prefer: config catalog literals document `auto_mode` false; Admin may enable AUTO after create; no automatic path inserts AUTO-true (and no automatic `dispatch_task` insert at all under the ban).
   - **Violating:** Keep “insert with `auto_mode` true”; drop or reframe “Provision skips correcting shared bad-seed AUTO-on” if that provision path is gone.

5. **`canon/patterns/`** — only if an established pattern example still cites meteorite/gaze/`fetch_email` provision as **required** boot behavior; grep at make-fix time and edit **examples only**. No new pattern files. (plan-fix grep found none requiring edits; make-fix re-checks.)

### Blast radius

- Radia/Joan statute sweeps and future seed work will treat `dispatch_task` differently from other catalogs (e.g. `agent_task` JSON sync if still catalog-wins).
- Does not change AST-1496 product code; does not edit `tests/` or test-bible (AST-1500 owns test gap).
- Does not redesign Manage Dispatch UI or runtime bookkeeping policy.

### What must still hold

- Operator Manage Dispatch create/edit remains the supported in-app writer for `dispatch_task`.
- Schema DDL ensure for `dispatch_task` remains allowed (product); statutes must not forbid DDL-only ensure.
- Runtime bookkeeping (`last_run_at`, max_runs disable) remains allowed.
- `SEED_CONFIG` / `METEORITE_DISPATCH_TASKS` may remain in-repo as Linear paste / documentation shapes — statutes must not require deleting those literals, only ban treating them as boot ensure authority for live rows.
- Sibling product ban AST-1496 (and mini-epic AST-1456 purpose) stay the behavioral source of truth for code.
