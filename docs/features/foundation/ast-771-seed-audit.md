# AST-771 — '_SEED' audit

<!-- linear-archive: AST-771 archived 2026-07-22 -->

## Linear archive (AST-771)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-771/seed-audit  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-883

### Description

## Purpose

Susan asked for a catalog of every place Astral **writes default or bootstrap content** into the database (or imports legacy content on startup) — not runtime business writes from dispatch, consult, or admin saves. Hidden auto-seeding causes deleted rows to reappear, drifts staging from Susan's intent, and duplicates config that AST-484/AST-549 already moved to `config.py`. This epic delivers that inventory in Discussion, records a keep / remove / relocate decision per case, then dispatches child action tickets only for approved changes. Devs do **not** re-run the audit.

## Functional scope

* **Discussion-phase audit (this ticket):** Chuckles surveys product code (excluding test fixtures) for automatic content seeding, `_SEED`-named constants, startup upserts, and schema-ensure migrations that mutate `agent`, `agent_task`, `dispatch_task`, or other tables without an explicit operator action.
* **Per-case disposition:** Each finding gets a Chuckles recommendation (justify, remove, or relocate) and a blank **Susan decision** field for Discussion review.
* **Post-approval action items:** After Susan moves this parent to Todo, `dispatch-parent` creates one child ticket per approved removal or relocation — not a monolithic "fix all seeding" child.
* **Inventory (product code — March 2026 survey):**

| # | Location | What it seeds | Chuckles recommendation | Susan decision |
| -- | -- | -- | -- | -- |
| 1 | `database._ensure_agent_schema` | `UPDATE agent` — fills NULL `model_code` / `temperature` / `max_tokens` from `AGENT_CONFIG`; renames `claude-sonnet-4-5` → `4-6`; fills NULL `brain_setting` from model | **Relocate** — one-time migration script; stop mutating agent rows on every schema ensure | Yes, let's create migration scripts for any ticket necessitating it, so that it can be run discretely at the time of the server restart, and not again during runtime. |
| 2 | `database.sync_agent_tasks` (called from `bootstrap_runtime` on every server start) | `INSERT` blank `agent_task` rows for any `TASK_CONFIG` key missing a current row; grouping columns from `seed_values_for_task_key` | **Discuss** — convenient for new task keys vs. admin-only row creation (overlaps [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) repo JSON upsert) | I think this is appropriate, as long as it only runs at server boot. |
| 3 | `database._apply_ast738_task_grouping_metadata_seed` | Backfills `task_group_*` columns from `TASK_CONFIG` when all current rows have empty `task_group_name` | **Justify** for first boot; **remove** from hot path once repo JSON ([AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task)) owns grouping | AAAAAAAAAACK!!!  NEVER CREATE FUNCTIONS REFERENCING THE AST ISSUE IDS IN THE SRC CODE OMG!!!  (See 772)&#10;&#10;Also, this should get replaced by  |
| 4 | `database._resolved_grouping_fields` / `seed_values_for_task_key` | Default grouping metadata when saving agent_task without explicit values | **Justify** — config-derived defaults match AST-484; not duplicate seed dicts |  |
| 5 | `database._AST561_ANALYSIS_UPSHOT_USER_PROMPT_SEED` + `_apply_ast561_analysis_upshot_take_jd_migration` | Full Estelle prompt text when `analysis_upshot` row exists but prompts empty; patches `take_jd` into non-empty prompts | **Remove** auto prompt body — require Admin → Task Prompts (same rule as `craft_company_search_terms`) |  |
| 6 | `database._apply_ast723_rubric_vectors_token_migration` | Replaces legacy rubric tokens with `{$RUBRIC_VECTORS}` on current `agent_task` rows (once per process) | **Relocate** — one-time migration script; drop from `_ensure_agent_task_schema` after fleet migrated |  |
| 7 | `database._apply_ast469_select_job_page_run_next_migration` | Sets `run_next = parse_job_list` on `select_job_page` when blank | **Relocate** — one-time script or repo JSON default ([AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task)); guarded but still hot-path |  |
| 8 | `database._ensure_dispatch_task_schema` | `UPDATE` NULL `entity_type` / `trigger_state` / `sort_by` / `batch_call_mode` from `dispatch_task_admin_defaults`; NULL `score_floor` → 1.0 for scored triggers | **Justify** — repairs incomplete operator-created rows; does not insert rows ([AST-745](https://linear.app/astralcareermatch/issue/AST-745/stop-dispatch-retry-auto-seed-and-startup-db-inventory-stop-rebuilding) removed `_RETRY_TASK_SEED` / `gaze_board` auto-insert) |  |
| 9 | `database._ensure_dispatch_task_schema` (legacy UPDATE block) | One-time retargets: `gaze*` sort_by, `locate_job_page` → `find_job_page`, NO_OPENINGS → `recheck_no_openings`, `consult_*` → `grade_*`, prefilter retry cleanup | **Relocate** — fold into checked-in migration scripts; stop re-running on every schema ensure |  |
| 10 | `database._migrate_company_search_terms_from_artifacts` | `INSERT` into `company_search_terms` from legacy `candidate_data.artifacts.company_search_terms` when table empty for candidate | **Remove** after one-time fleet sweep — data now lives in `company_search_terms` table / artifacts pipeline |  |
| 11 | `database.get_dispatch_row_or_seed_preview_meta` | **No DB write** — returns config defaults when no sample `dispatch_task` row (admin adhoc preview) | **Justify** behavior; optional **rename** to drop "seed" vocabulary (AST-549 already removed seed dicts) |  |
| 12 | `scripts/migrations/bootstrap_candidate.py` | Manual operator script — seeds first candidate via `do_task` | **Justify** — explicit script, not automatic; keep under `scripts/migrations/` |  |
| 13 | `scripts/migrations/backfill_task_grouping_metadata.py` | CLI backfill for [AST-738](https://linear.app/astralcareermatch/issue/AST-738/task-grouping-metadata-storage-and-seed-organizing-tasks) grouping columns | **Justify** as operator/CI tool; runtime hook (#3) is the concern |  |
| 14 | Core `seed_chain` / test `seeded_db` helpers | In-memory chain context or test fixtures only | **Out of scope** — naming collision, not DB seeding |  |

* **Explicitly out of inventory:** Normal dispatch/consult/admin save paths; `INSERT OR IGNORE` on timesheets/ledger dedupe; AST-745-retired `_DISPATCH_TASK_SEED` / `_RETRY_TASK_SEED` / `_ensure_gaze_board_dispatch_tasks` (confirmed absent on current `dev`).

## Boundaries

* Does **not** ask a dev agent to re-audit the codebase — inventory above is the Discussion artifact.
* Does **not** change runtime behavior until Susan approves per-row dispositions and children ship.
* Does **not** cover test-tree fixtures, in-memory variable names (`seed_chain`), or config literals in `config.py` (those are source-of-truth, not seeding).
* Must **not** break AST-484 rule: allowed dispatch defaults come from config helpers, not parallel seed dicts (already satisfied post-AST-549).
* [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) (repo JSON upsert for `agent` / `agent_task`) is a **sibling** — coordinate so startup seeding strategy is single-path after both land.

## Acceptance criteria

* Every product seeding site in the inventory table has a filled **Susan decision** (keep / remove / relocate / defer) before dispatch.
* Susan has reviewed Chuckles recommendations and confirmed or overridden each row.
* Approved removals/relocations become scoped child tickets at dispatch — no child titled "run the seed audit."
* After children ship, no removed auto-seed path re-inserts content Susan deleted without an explicit operator or repo-json action.
* [AST-745](https://linear.app/astralcareermatch/issue/AST-745/stop-dispatch-retry-auto-seed-and-startup-db-inventory-stop-rebuilding) guarantee preserved: deleting `dispatch_task` rows (including `*_RETRY`) stays deleted across server restart.

## Dependencies and blockers

* [AST-745](https://linear.app/astralcareermatch/issue/AST-745/stop-dispatch-retry-auto-seed-and-startup-db-inventory-stop-rebuilding) (Done) — removed recurring `dispatch_task` auto-insert; baseline for rows 8–9.
* **AST-549** (Done) — retired `_DISPATCH_TASK_SEED`; baseline for row 11.
* [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) (Discussion) — repo JSON startup upsert for `agent` / `agent_task` affects disposition of rows 2–3 and 5–7; decide sequencing before dispatch or block overlapping children.

## Open questions

1. Row 2 — keep `sync_agent_tasks` auto-insert of blank `agent_task` rows on every startup, or require admin/repo-json only?
2. Row 5 — confirm: no automatic full prompt body for `analysis_upshot` (admin must author, same as other tasks)?
3. Rows 6–7 and 9 — OK to consolidate all schema-ensure one-time migrations into `scripts/migrations/` and delete hot-path hooks once Susan's DB is migrated?
4. Row 1 — stop auto-setting `model_code` / `brain_setting` on existing agents, or keep as safety net for legacy NULL rows?
5. [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) vs this epic — dispatch [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) first (repo JSON becomes startup truth), then seed-cleanup children, or parallel?

---

## Original brief

I want a full audit of the entire codebase where we are "seeding" any content in the database or elsewhere.

For each case found, justify its existence or suggest a removal or relocation.

DO NOT have the dev run this audit, I want to see the audit in our discussion phase and make a set of action items for devs based on our determinations for each case.

### Comments

#### chuckles — 2026-06-23T20:39:11.187Z
@susan

1. Row 2 — keep `sync_agent_tasks` auto-insert of blank `agent_task` rows on every startup, or admin/repo-json only?
2. Row 5 — confirm no automatic full prompt body for `analysis_upshot`?
3. Rows 6–7 and 9 — consolidate schema-ensure one-time migrations into scripts and drop hot-path hooks?
4. Row 1 — stop auto-setting `model_code` / `brain_setting` on NULL agent rows?
5. AST-756 vs this epic — dispatch AST-756 first, then seed cleanup, or parallel?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
