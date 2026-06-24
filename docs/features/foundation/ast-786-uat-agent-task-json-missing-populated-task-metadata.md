# AST-786 — UAT: agent_task.json missing populated task metadata (37 keys)

**Linear (this ticket):** [AST-786](https://linear.app/astralcareermatch/issue/AST-786/uat-agent-taskjson-missing-populated-task-metadata-37-keys)  
**Parent:** [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task)  
**Publish ref:** `origin/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata` (UAT bug child; ignore Linear `gitBranchName`)

## Summary

Susan UAT on fresh deploy: `data/admin/agent_task.json` shipped from **AST-782** with **33 skeleton rows** (empty `agent_id`, prompts, grouping, `run_next`, etc.) — not a usable repo contract. **AST-786** replaces it with the **37-row authoritative fixture** already on this publish ref at `docs/uat-fixtures/AST-756/expected-agent_task.json`, normalized for startup import (`current = 1`, PRAGMA column key order). **No product code**, export API, divergence UI, or `agent.json` changes (separate bug).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Normalize `current` → `1` on all 37 rows; reorder object keys to SQLite `agent_task` PRAGMA order | docs (UAT fixture) |
| `data/admin/agent_task.json` | Replace with normalized fixture content (byte-identical to updated fixture) | data |

**Out of scope (explicit):** `src/**`, `scripts/export_repo_admin_json.py`, divergence / revert UI (**AST-783**), `data/admin/agent.json`, new task keys, inventing prompt text not in the fixture.

## Stage 1: Normalize fixture and install repo JSON

**Done when:** `data/admin/agent_task.json` contains exactly **37** rows with populated metadata matching the fixture; every row has `current = 1`; all task keys in the ticket Description are present; `load_repo_admin_json_file("agent_task")` + `apply_agent_task_repo_json_startup` succeed on a scratch DB (hand-verify in build completion comment). No `src/**` edits.

1. **Read** `docs/uat-fixtures/AST-756/expected-agent_task.json` (already on publish ref from dispatch).

2. **Validate fixture content** before writing (raise / stop if any check fails — do not patch product code):

   a. Parse as JSON array; length **must be 37**.

   b. Task keys (sorted) **must equal** this exact set (from ticket Description — do not add/remove keys):

   ```
   advise_job_resume, analysis_upshot, anticipate_scan, check_cover_letter, check_job_resume,
   contemplate_job, craft_company_search_terms, craft_do_rubric, craft_get_rubric,
   craft_jobdesc_rubric, craft_joblist_rubric, craft_like_rubric, craft_prefilter_rubric,
   craft_resume_base, draft_cover_letter, draft_job_resume, evaluate_jd, fetch_jd,
   fetch_job_pages, fetch_website, finalize_cover_letter, finalize_job_resume, gaze,
   grade_do, grade_get, grade_like, inflow_discovery, intake_build_request,
   intake_candidate_response, intake_initiate_candidate, parse_job_list, prefilter_company,
   propose_application_responses, qualify_job_listings, recheck_no_openings, select_job_page,
   vet_inflow_discovery
   ```

   c. Each row object keys **must equal** the set returned by `database.table_columns(conn, "agent_task")` on a live connection (17 columns today: `task_key_uuid`, `task_key`, `current`, `agent_id`, seven prompt segments, `run_next`, `updated_at`, four grouping fields).

   d. Spot-check **non-empty** on representative rows (not all prompts are non-empty by design — ticket lists 6 tasks with empty `user_prompt` in prod export): at minimum **`prefilter_company`**, **`grade_get`**, **`anticipate_scan`** must have non-empty `agent_id` and non-empty `user_prompt` after normalization.

3. **Normalize each row** (in memory — do not change prompt text):

   a. Set **`"current": 1`** on every row. ⚠️ **Decision:** Dispatch fixture was Copy Output with `current: 0` on all rows; startup path **`_validate_agent_task_repo_json_rows`** requires `current = 1` and **`apply_agent_task_copy_upsert`** only treats `current = 1` rows as the active catalog. Promoting to `1` preserves prompt bodies verbatim while satisfying AST-782 import contract.

   b. Reorder each row dict to **PRAGMA column order** (same order as `table_columns(conn, "agent_task")`) so repo JSON matches Copy Output / export round-trip shape.

4. **Write** normalized array to **both** paths with `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"` (UTF-8):

   - `docs/uat-fixtures/AST-756/expected-agent_task.json` (update authoritative fixture in place)
   - `data/admin/agent_task.json` (repo contract applied at startup)

   Use the **same normalized list** for both files so fixture and repo path stay identical.

5. **Hand-verify** (document in build completion — not automated in this ticket):

   ```python
   from src.core.repo_admin_json import load_repo_admin_json_file
   from src.data import database

   rows = load_repo_admin_json_file("agent_task")
   assert len(rows) == 37
   conn = database._get_connection()
   try:
       database.apply_agent_task_repo_json_startup(conn, rows)
       conn.commit()
       n = conn.execute("SELECT COUNT(*) FROM agent_task WHERE current = 1").fetchone()[0]
       assert n == 37
   finally:
       conn.close()
   ```

   Optional: open Manage Tasks locally after restart — grouped sections show names/prompts, not blank skeleton rows.

⚠️ **Decision:** Do **not** run `scripts/export_repo_admin_json.py` to regenerate repo JSON — local dev DB still has skeleton rows and would reintroduce the bug. Fixture is the sole source for this fix.

## Execution contract (build-child)

- **One** `code(AST-786)` commit for Stage 1 (both JSON files only).
- Publish to **`origin/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata`** before marking **Code Complete**.
- Betty owns tests/manifest; do not edit `tests/` or `docs/test-bible/**`.

## Self-Assessment

**Scope:** `minor` — Two tracked JSON files only; no layer changes.

**Conf:** `high` — Authoritative fixture and task-key list are in the ticket; normalization (`current = 1`, column order) is a documented one-time transform with existing AST-782 validation as guardrail.

**Risk:** `Medium` — Wrong row or truncated prompt in repo JSON affects every deploy restart; mitigated by exact 37-key set check, fixture parity, and startup apply smoke in build completion.

## Plan vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.2 scope | Data/docs only — no layer imports touched. |
| §2.1 config | Paths unchanged (`REPO_ADMIN_JSON_CONFIG` already points at `data/admin/agent_task.json`). |
| §3.6 | UAT fixture under `docs/uat-fixtures/AST-756/` per ticket; not spike output under `debug/spikes/`. |

No unresolved conflicts.

## Build review stub

**Built:** `origin/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata` @ `54ceac3`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `54ceac3` | Normalized 37-row fixture (`current=1`, PRAGMA key order) → `data/admin/agent_task.json` |

**Hand-verify:** 37 task keys match ticket set; `prefilter_company` / `grade_get` / `anticipate_scan` have non-empty `agent_id` + `user_prompt`; `load_repo_admin_json_file` + `apply_agent_task_repo_json_startup` → 37 `current=1` rows; fixture and repo JSON byte-identical (129643 bytes).
