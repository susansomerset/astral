# AST-878 — UAT: fetch_culture_pages missing from codebase JSON content

**Linear:** [AST-878](https://linear.app/astralcareermatch/issue/AST-878/uat-fetch-culture-pages-missing-from-codebase-json-content)  
**Parent:** [AST-872](https://linear.app/astralcareermatch/issue/AST-872/fetch-culture-pages-task-is-missing)  
**Publish ref:** `origin/sub/AST-872/AST-878-uat-fetch-culture-pages-missing-json`

**FIX-UAT:** After AST-872 / AST-874 shipped, **`fetch_culture_pages`** is schedulable in config and runtime, but Susan’s codebase JSON (`data/admin/agent_task.json`) has no row for it — so the key is absent from the repo-owned catalog she reviews for dispatchable tasks. Add the mechanical gazer hop row (mirror **`fetch_jd`**) and keep the AST-756 UAT fixture byte-identical.

Does **not** change LIKE rubric/scoring, coat-check scrape code, `NEED_WEBSITE_CONTENT`, or `GAZER_CONFIG` / dispatch registry (already on ftr from AST-874).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Insert current **`fetch_culture_pages`** row (Job Review, between GET and LIKE); bump **`grade_like`** / **`analysis_upshot`** `task_seq` | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Same bytes as updated `agent_task.json` (AST-786 identity contract) | docs |

**Out of scope:** `src/**` (config already registers the key); `tests/` / `docs/test-bible/**` (Betty revises AST-786 count/frozenset assertions at qa-child — catalog grows 37 → 38); LIKE prompts; coat-check; `dispatch_task` DB migration (AST-874 already seeds rows).

---

## Stage 1: Add `fetch_culture_pages` to repo agent_task JSON + fixture

**Done when:** Both JSON files are byte-identical; exactly one current row has `"task_key": "fetch_culture_pages"`; Job Review sequence is qualify → fetch_jd → evaluate_jd → grade_do → grade_get → **fetch_culture_pages** → grade_like → analysis_upshot; `cmp -s` of the two paths exits 0.

1. In `data/admin/agent_task.json`, locate the current (`"current": 1`) objects with:
   - `"task_key": "grade_get"` → `"task_seq": 6`
   - `"task_key": "grade_like"` → `"task_seq": 7`
   - `"task_key": "analysis_upshot"` → `"task_seq": 8`

2. Update sequences (integers only):
   - `grade_like` → `"task_seq": 8`
   - `analysis_upshot` → `"task_seq": 9`

3. Insert a new object into the JSON array (same key order as the existing `fetch_jd` row — PRAGMA / export shape). Values:

   ```json
   {
     "task_key_uuid": "a8c3e1f2-4b5d-4e6a-9c0d-1f2a3b4c5d6e",
     "task_key": "fetch_culture_pages",
     "current": 1,
     "agent_id": "n/a",
     "user_prompt": "",
     "cache_prompt": "",
     "cache_prompt_b": "",
     "cache_prompt_c": "",
     "cache_prompt_d": "",
     "nocache_prompt": "",
     "system_prompt": "",
     "run_next": "",
     "updated_at": "2026-07-12 22:00:00",
     "task_group_order": "4000",
     "task_group_name": "Job Review",
     "task_seq": 7,
     "task_name": "Fetch Culture Pages"
   }
   ```

   ⚠️ **Decision:** Place at **`task_seq` 7** between **`grade_get`** (6) and **`grade_like`** (8) so Manage Tasks / JSON ordering matches **PASSED_GET → CULTURE_READY → LIKE**. Mechanical hop like **`fetch_jd`**: `agent_id` `"n/a"`, empty prompts, empty `run_next`. Use the literal UUID above (stable across fixture + repo file) — do not regenerate per build.

4. Keep JSON formatting consistent with the file: `indent=2`, UTF-8, trailing newline. Prefer editing via a small Python rewrite that:
   - loads the list
   - applies seq bumps + insert
   - writes `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"`
   so key order on the new row matches the template dict order above (same 17 keys as siblings).

5. Copy bytes to the UAT fixture (mandatory — AST-786 / AST-834):

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
   ```

6. Hand-verify (build comment / local check — not a test edit):

   ```python
   import json
   from pathlib import Path
   rows = json.loads(Path("data/admin/agent_task.json").read_text())
   assert len(rows) == 38
   by = {r["task_key"]: r for r in rows if r.get("current") == 1}
   assert "fetch_culture_pages" in by
   assert by["fetch_culture_pages"]["task_seq"] == 7
   assert by["grade_like"]["task_seq"] == 8
   assert by["analysis_upshot"]["task_seq"] == 9
   assert by["fetch_culture_pages"]["task_group_name"] == "Job Review"
   assert by["fetch_culture_pages"]["agent_id"] == "n/a"
   ```

**Commit message:** `code(AST-878): add fetch_culture_pages to agent_task repo JSON`

**Betty note (qa-child, not this stage):** `TestAst786AgentTaskRepoJsonSeed` still asserts **37** keys / `AST786_EXPECTED_TASK_KEYS` — expect **`[qa-handoff]`** or Betty’s Code Complete pass to bump to **38** and include **`fetch_culture_pages`**. Engineer must **not** edit `tests/`.

---

## Execution contract

The plan is binding. One stage, one product commit on the epic worktree sub checkout; publish to `origin/sub/AST-872/AST-878-uat-fetch-culture-pages-missing-json`. No `src/**` changes. If `agent_task.json` shape drifted (missing columns, non-list root), stop and comment on **AST-872** with the `🛑 Stage N blocked` template.

---

## Self-Assessment

**Scope:** `minor` — two JSON files only; inserts one catalog row and renumbers two siblings’ `task_seq`.

**Conf:** `high` — same mechanical pattern as existing `fetch_jd` / `fetch_website` repo JSON rows; AST-786 fixture identity contract is established.

**Risk:** `low` — catalog metadata only; runtime dispatch already has the key from AST-874. Residual: Betty’s 37-key tests go red until she updates (expected).

---

## Self-review vs ASTRAL_CODE_RULES

- **§2.1:** No new config literals — key already in `DISPATCH_SCHEDULABLE_TASK_KEYS` / `GAZER_CONFIG` from AST-874.
- **AST-782 repo JSON:** Flat scalars only; `current: 1`; startup upsert will import the new row on next boot.
- **§1.3 / layers:** No core/UI code; data/docs fixture only.
- **Test ownership:** Engineer does not patch `tests/` when count assertions fail — Betty owns that delta.

## Review (build stub)

**Built:** `astral-AST-872` @ d90362a on `origin/sub/AST-872/AST-878-uat-fetch-culture-pages-missing-json`

| Stage | Summary |
|-------|---------|
| 1 | Added `fetch_culture_pages` to `data/admin/agent_task.json` (Job Review seq 7); bumped `grade_like`→8, `analysis_upshot`→9; synced AST-756 fixture byte-identical |

**Verify:** 38 rows; `cmp -s` repo JSON vs fixture — pass. Hand-check seq/agent_id — pass.

**Betty note:** `TestAst786AgentTaskRepoJsonSeed` still expects 37 keys — revise to 38 + `fetch_culture_pages` at qa-child.
