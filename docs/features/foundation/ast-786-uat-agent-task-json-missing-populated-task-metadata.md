<!-- linear-archive: AST-786 archived 2026-07-22 -->

## Linear archive (AST-786)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-786/uat-agent-taskjson-missing-populated-task-metadata-37-keys  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-756 — create repo json files for agent and agent_task.  
**Blocked by / blocks / related:** parent: AST-756

### Description

## What failed

Susan UAT on fresh deploy: `data/admin/agent_task.json` rows exist but critical fields are empty (`agent_id`, `user_prompt`, `system_prompt`, cache/nocache prompts, `task_name`, `task_group_name`, `run_next`, etc.). Only skeleton keys present — not usable as authoritative repo contract.

## Expected

`data/admin/agent_task.json` contains **37** `current = 1` rows (one per task key below) with full metadata populated (prompts, grouping, run-next wiring, UUIDs, timestamps). After server start, DB `agent_task` current rows match this file.

**Task keys (37):** advise_job_resume, analysis_upshot, anticipate_scan, check_cover_letter, check_job_resume, contemplate_job, craft_company_search_terms, craft_do_rubric, craft_get_rubric, craft_jobdesc_rubric, craft_joblist_rubric, craft_like_rubric, craft_prefilter_rubric, craft_resume_base, draft_cover_letter, draft_job_resume, evaluate_jd, fetch_jd, fetch_job_pages, fetch_website, finalize_cover_letter, finalize_job_resume, gaze, grade_do, grade_get, grade_like, inflow_discovery, intake_build_request, intake_candidate_response, intake_initiate_candidate, parse_job_list, prefilter_company, propose_application_responses, qualify_job_listings, recheck_no_openings, select_job_page, vet_inflow_discovery

**Fixture (authoritative expected export):** `docs/uat-fixtures/AST-756/expected-agent_task.json` on this ticket's publish sub (seeded at dispatch).

## Repro

1. Fresh clone; checkout epic `ftr/AST-756-repo-json-agent-agent-task` or sub for this bug.
2. Open `data/admin/agent_task.json`.
3. Observe empty/minimal fields on current rows vs fixture in `docs/uat-fixtures/AST-756/expected-agent_task.json`.
4. Start server; confirm DB current rows still lack populated prompt metadata.

## Parent AC (quoted inline)

> After a fresh clone and server start, current (`current = 1`) rows in `agent` and `agent_task` match the checked-in `data/admin/` JSON files (field values for every row present in JSON).

## Boundaries

* This bug does **not** change: divergence warning UI, revert-to-file flow, export endpoint shape, or `agent.json` content (separate bug).
* Copy fixture into `data/admin/agent_task.json`; do not invent alternate task keys.

### Comments

#### radia — 2026-06-24T21:58:10.494Z
### Plan fidelity (AST-786) — FIX-UAT

Diff `origin/dev...origin/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata` @ `0721ae2` (+ doc `3818646`).

UAT bug fix verified: `code(AST-786)` @ `54ceac3` replaces skeleton **33-row** repo JSON with normalized **37-row** catalog from `docs/uat-fixtures/AST-756/expected-agent_task.json` only (scope gate PASS — no `src/**`). All rows `current = 1`; fixture and `data/admin/agent_task.json` byte-identical (129643 bytes); Betty manifest `TestAst786AgentTaskRepoJsonSeed` locks 37-key set, spot-checks (`prefilter_company`, `grade_get`, `anticipate_scan`), and startup apply smoke.

**fix-now:** none.

**discuss:** `data/admin/agent.json` still `[]` — explicit out of scope here; persona startup gap tracked separately (**AST-787**). This ticket closes the **task metadata** UAT item only.

**advisory:** `expected-agent.json` reference fixture on branch (with legacy `model_code`) not wired to repo `agent.json`; OK as staging artifact outside `code(AST-786)`.

Combined review: `docs/features/foundation/ast-786-uat-agent-task-json-missing-populated-task-metadata.md` (Radia review section).

#### betty — 2026-06-24T21:53:28.068Z
## QA test manifest (AST-786)

**Publish:** `origin/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata` @ `0721ae2` (`merge-tests(AST-786): origin/tests a5a53d7`)

**Scope:** Data-only UAT fix — populated **37-row** `data/admin/agent_task.json` from `docs/uat-fixtures/AST-756/expected-agent_task.json`. No `src/**` changes.

### Manifest (test-child)

1. **Fixture/repo parity + 37-key catalog** — `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed` (full class)

2. **Scope gate (required):** `git show 54ceac3 --name-only` — expect **only** `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` (no `src/`).

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  -q
```

**Pass criterion:** pytest green on item 1 + scope gate item 2 — not zero-arg harness / branch-lock gate.

**Bible shasum (`origin/sub/...`):**
- `docs/test-bible/data/database/agent_tasks.md` `5eddc0c9bb0229710f922f87d9a2e61276043039123216a5c6c458e6af32f130`
- `docs/test-bible/core/repo_admin_json.md` `91951d4fd79db3ae8800470cde24ece6e7b94fb3379dcd60871f536281d06bbe`

#### chuckles — 2026-06-24T21:50:19.804Z
## validate-plan — APPROVED

Data-only UAT fix; scope matches bug boundaries. Normalization decisions documented (`current=1`, drop `model_code`). No layer violations.

— Chuckles

#### ada — 2026-06-24T21:49:26.204Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata/docs/features/foundation/ast-786-uat-agent-task-json-missing-populated-task-metadata.md

**Self-assessment**
- **Scope:** minor — normalize and install `data/admin/agent_task.json` from `docs/uat-fixtures/AST-756/expected-agent_task.json` (37 keys); update fixture `current` → 1 and PRAGMA key order; no `src/**` changes.
- **Conf:** high — task-key set and authoritative fixture are in the ticket; AST-782 startup validation is the apply guardrail.
- **Risk:** Medium — repo JSON drives every restart; mitigated by exact key-set check, fixture/repo parity, and startup apply smoke in build.

---

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

## Radia review (2026-06-24) — FIX-UAT

**Ref:** `origin/dev...origin/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata` @ `0721ae2`

### What's solid

- **UAT fix verified:** `code(AST-786)` @ `54ceac3` touches **only** `data/admin/agent_task.json` + `docs/uat-fixtures/AST-756/expected-agent_task.json` (scope gate PASS — no `src/**`).
- **37-key catalog:** normalized rows match ticket task-key set; all `current = 1`; PRAGMA column keys validated in `test_startup_apply_loads_all_37_current_rows`.
- **Fixture parity:** repo JSON byte-identical to authoritative fixture (129643 bytes); Betty manifest `TestAst786AgentTaskRepoJsonSeed` locks parity + spot-checks + startup smoke.
- **Plan decisions honored:** `current` promoted to `1`; did not regenerate from local DB export; six tasks with empty `user_prompt` documented in plan (scraper/dispatch keys).

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **discuss** | `data/admin/agent.json` (unchanged `[]`) | Out of scope for AST-786 per plan — startup still wipes personas until sibling fix lands (**AST-787** on epic). UAT for **task** metadata is addressed here; agent personas remain a separate gap. |
| **advisory** | `docs/uat-fixtures/AST-756/expected-agent.json` | Reference fixture added on branch (includes legacy `model_code`); not applied to repo `agent.json` — OK as staging artifact, not part of `code(AST-786)` commit. |

No **fix-now** items.

### Recommended actions

| Priority | Action |
| --- | --- |
| resolve-child | None for AST-786 — merge when parent UAT lane clears. |
| Follow-on | Track **AST-787** (or sibling) for populated `agent.json` if persona UAT still open. |

## Resolution (2026-06-24)

**Radia review:** clean — no **fix-now** items.

**Discuss (`data/admin/agent.json` = `[]`):** Acknowledged. Out of scope for AST-786 per plan — task metadata UAT is closed here; empty persona seed tracked separately (**AST-787**).

**Product changes:** none — resolve pass is doc-only.

**§9a dry-run:** `origin/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata` merges cleanly into `origin/dev` and `origin/ftr/AST-756-repo-json-agent-agent-task` (no conflict markers in `git merge-tree`).

**Publish tip at resolve:** `origin/sub/AST-756/AST-786-agent-task-json-missing-populated-task-metadata` @ Radia doc `3818646`.
