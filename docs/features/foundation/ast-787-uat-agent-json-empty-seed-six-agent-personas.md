<!-- linear-archive: AST-787 archived 2026-07-22 -->

## Linear archive (AST-787)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-787/uat-agentjson-empty-seed-six-agent-personas  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-756 — create repo json files for agent and agent_task.  
**Blocked by / blocks / related:** parent: AST-756

### Description

## What failed

Susan UAT: `data/admin/agent.json` is `[]` (empty array). No agent persona rows checked in — startup upsert has nothing to load for `agent` table.

## Expected

`data/admin/agent.json` contains **6** agent rows with full persona metadata (`agent_id`, `content`, `model_code`, `brain_setting`, `temperature`, `max_tokens`, `updated_at`).

**Agent ids (6):** job_analyst_grace, ats_expert_atlas, content_writer_judith, web_scraper_laslo, principal_recruiter_estelle, college_intern_ruth

**Fixture (authoritative expected export):** `docs/uat-fixtures/AST-756/expected-agent.json` on this ticket's publish sub (seeded at dispatch).

## Repro

1. Fresh clone; open `data/admin/agent.json`.
2. Observe `[]` or missing rows.
3. Compare to `docs/uat-fixtures/AST-756/expected-agent.json` on publish sub.
4. Start server; `agent` current rows do not match Susan's UAT personas.

## Parent AC (quoted inline)

> After a fresh clone and server start, current (`current = 1`) rows in `agent` and `agent_task` match the checked-in `data/admin/` JSON files (field values for every row present in JSON).

## Boundaries

* This bug does **not** change: `agent_task.json` seed data (separate bug), divergence UI, or export API semantics.
* Populate repo JSON only; no new admin UI.

### Comments

#### radia — 2026-06-24T21:58:47.148Z
### Plan fidelity (AST-787) — FIX-UAT

Diff `origin/dev...origin/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas` @ `16e2dc1` (+ doc `7e0a4f0`).

UAT bug fix verified: `code(AST-787)` @ `1c8364e` replaces empty `data/admin/agent.json` with **six** persona rows mapped from `docs/uat-fixtures/AST-756/expected-agent.json` — AST-782 repo columns only (`model_code` stripped), sorted by `agent_id`, fixture `brain_setting` verbatim. Betty manifest `TestAst787AgentRepoJsonSeed` locks id set, fixture mapping, column contract, and startup apply smoke. No `src/**` changes; `agent_task.json` untouched.

**fix-now:** none.

**advisory:** Branch diff vs `origin/dev` includes AST-786 rollup; AST-787 product delta is `agent.json` only. `code(AST-787)` also touched plan build stub in same commit — doc-only, not scope leak.

Closes empty-`agent.json` discuss from AST-782/786 reviews.

Combined review: `docs/features/foundation/ast-787-uat-agent-json-empty-seed-six-agent-personas.md` (Radia review section).

#### betty — 2026-06-24T21:55:00.694Z
## QA test manifest (AST-787)

**Publish:** `origin/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas` @ `16e2dc1` (`merge-tests(AST-787): origin/tests 33b821e`)

**Scope:** Data-only UAT fix — six persona rows in `data/admin/agent.json` mapped from `docs/uat-fixtures/AST-756/expected-agent.json` (repo columns; `model_code` stripped). No `src/**` changes.

### Manifest (test-child)

1. **Fixture mapping + 6-id catalog + startup smoke** — `tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed` (full class)

2. **Scope gate (required):** `git show 1c8364e --name-only` — expect **only** `data/admin/agent.json` and `docs/features/foundation/ast-787-uat-agent-json-empty-seed-six-agent-personas.md` (no `src/`).

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed \
  -q
```

**Pass criterion:** pytest green on item 1 + scope gate item 2 — not zero-arg harness / branch-lock gate.

**Bible shasum (`origin/sub/...`):**
- `docs/test-bible/data/database/agents.md` `7528077762e2ce3b7265498310e8e423d556d2d60ddaf4c335852b29b738224e`
- `docs/test-bible/core/repo_admin_json.md` `212909019cc084659dbc2a545ee77ce186a08ac9094558fda9cbcb5552588572`

#### chuckles — 2026-06-24T21:50:20.851Z
## validate-plan — APPROVED

Data-only UAT fix; scope matches bug boundaries. Normalization decisions documented (`current=1`, drop `model_code`). No layer violations.

— Chuckles

#### katherine — 2026-06-24T21:49:27.433Z
Plan: `https://github.com/susansomerset/astral/blob/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas/docs/features/foundation/ast-787-uat-agent-json-empty-seed-six-agent-personas.md`

**Scope:** minor — replace empty `data/admin/agent.json` with six persona rows from `docs/uat-fixtures/AST-756/expected-agent.json`, repo-shaped (strip `model_code` per AST-782 columns).

**Conf:** high — authoritative UAT fixture + mechanical column map; no product code.

**Risk:** low — loader validation fails loud on wrong keys/count; `agent_task.json` and divergence UI untouched.

---

# AST-787 — UAT: agent.json empty — seed six agent personas

**Linear (this ticket):** [AST-787](https://linear.app/astralcareermatch/issue/AST-787/uat-agent-json-empty-seed-six-agent-personas)  
**Parent:** [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) (User Testing)  
**Publish ref:** `origin/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas` (child of AST-756; ignore Linear `gitBranchName`)

## Summary

Susan UAT: `data/admin/agent.json` is `[]`, so startup repo-wins upsert (AST-782) loads zero personas and deletes any existing `agent` rows on boot. This UAT bug replaces the empty file with **six** checked-in persona rows copied from the authoritative fixture `docs/uat-fixtures/AST-756/expected-agent.json`, shaped for the AST-782 repo JSON contract (no `model_code` column — `brain_setting` is authoritative). **Data-only** — no product code, UI, or `agent_task.json` changes.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent.json` | Replace `[]` with six persona rows from UAT fixture (repo column shape) | data |

**Out of scope (explicit):** `data/admin/agent_task.json` (AST-786), divergence UI (AST-783), export CLI/API, `REPO_ADMIN_JSON_CONFIG`, startup apply logic, admin UI, `docs/uat-fixtures/**` edits, `tests/` / `docs/test-bible/**`.

## Stage 1: Seed `data/admin/agent.json` from UAT fixture

**Done when:** `data/admin/agent.json` is a UTF-8 JSON array of **exactly six** objects; each object’s keys equal `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]`; `load_repo_admin_json_file("agent")` succeeds; `agent_id` values match the fixture set; file is committed on publish ref.

1. Read **`docs/uat-fixtures/AST-756/expected-agent.json`** (already on publish sub at dispatch). Confirm **six** rows with these `agent_id` values (no extras, no omissions):

   - `job_analyst_grace`
   - `ats_expert_atlas`
   - `content_writer_judith`
   - `web_scraper_laslo`
   - `principal_recruiter_estelle`
   - `college_intern_ruth`

2. Build the repo JSON payload by mapping each fixture row to **only** these keys (in this order per row object):

   ```python
   AGENT_REPO_COLUMNS = (
       "agent_id",
       "content",
       "brain_setting",
       "temperature",
       "max_tokens",
       "updated_at",
   )
   ```

   For each fixture object `row`:

   ```python
   {
       "agent_id": row["agent_id"],
       "content": row["content"],
       "brain_setting": row["brain_setting"],
       "temperature": row["temperature"],
       "max_tokens": row["max_tokens"],
       "updated_at": row["updated_at"],
   }
   ```

   **Drop `model_code`** from every row — AST-782 startup validation requires `set(row.keys()) == set(AGENT_REPO_COLUMNS)` exactly; extra keys raise `ValueError`. `model_code` is legacy DB storage; persona tier is `brain_setting` only in repo JSON (AST-782 decision).

3. Sort the six row objects by `agent_id` ascending (matches `fetch_agent_repo_json_export_rows` `ORDER BY agent_id`).

4. Write **`data/admin/agent.json`**:

   - Top-level JSON **array** (Copy Output shape).
   - `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"` (UTF-8).
   - Do **not** modify `data/admin/agent_task.json`.

5. **Verify before commit** (epic worktree, from repo root):

   ```bash
   python3 -c "
   from src.core.repo_admin_json import load_repo_admin_json_file
   rows = load_repo_admin_json_file('agent')
   assert len(rows) == 6
   ids = {r['agent_id'] for r in rows}
   assert ids == {
       'job_analyst_grace', 'ats_expert_atlas', 'content_writer_judith',
       'web_scraper_laslo', 'principal_recruiter_estelle', 'college_intern_ruth',
   }
   for r in rows:
       assert set(r.keys()) == {
           'agent_id','content','brain_setting','temperature','max_tokens','updated_at'
       }
       assert str(r['brain_setting']).strip()
   print('ok', len(rows))
   "
   ```

6. **Hand-verify (document in build completion comment):** After a local server restart (or one call to `apply_repo_admin_json_at_startup()` against dev DB), Manage Agents lists six personas with prompt bodies matching fixture `content` (spot-check one `agent_id` length or hash — no need to log prompt text).

⚠️ **Decision:** Use fixture field values verbatim for the six repo columns — do not re-derive `brain_setting` from fixture `model_code` and do not add `model_code` to repo JSON. Fixture already includes correct `brain_setting` per row.

⚠️ **Decision:** Do not run `scripts/export_repo_admin_json.py` against a local DB to produce this file — Susan’s UAT fixture is authoritative; export might reflect empty or stale local DB and reintroduce `[]`.

## Execution contract (build-child)

- One **`code(AST-787)`** commit on epic worktree; publish to **`origin/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas`** before **Code Complete**.
- Do not add files beyond the table above without stopping and commenting on parent AST-756.
- If fixture rows fail `validate_allowed_brain_setting` at startup apply, stop — comment on AST-787 with the offending `brain_setting` value; do not change config validation in this bug.

## Self-Assessment

**Scope:** `minor` — Single tracked data file replacement; no `src/` changes.

**Conf:** `high` — Authoritative fixture and AST-782 column contract are explicit; transformation is mechanical strip-`model_code` + sort.

**Risk:** `low` — Wrong keys or row count fail loud at `load_repo_admin_json_file` / startup apply; mitigated by inline verify script before commit. Does not affect `agent_task` or divergence UI.

## Plan vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §2.1 config | Repo column list read from `REPO_ADMIN_JSON_CONFIG` — do not invent columns |
| §1.3 DRY | Reuse existing loader validation — no duplicate schema |
| §3.3 layers | Data file only — no layer violations |
| §3.6 | Fixture under `docs/uat-fixtures/` is reference only; product seed stays `data/admin/agent.json` |

No unresolved conflicts.

## Parent / sibling context (reference only)

- **AST-782** established repo JSON load/apply and excluded `model_code` from `agent` export columns.
- **AST-783** divergence UI warns when DB ≠ repo file; seeding `agent.json` clears false “empty repo” behavior on fresh clone.
- **AST-786** owns `agent_task.json` population separately — not this ticket.

## Build review stub

**Built:** `origin/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas` @ `1c8364e`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `1c8364e` | Seed `data/admin/agent.json` from UAT fixture (6 personas, repo columns) |

**Hand-verify:** `load_repo_admin_json_file('agent')` → 6 rows; fixture `model_code` stripped per AST-782 column contract.

## Radia review (2026-06-24) — FIX-UAT

**Ref:** `origin/dev...origin/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas` @ `16e2dc1`

### What's solid

- **UAT fix verified:** `code(AST-787)` @ `1c8364e` replaces `[]` with **six** persona rows mapped from `docs/uat-fixtures/AST-756/expected-agent.json` — repo columns only (`model_code` stripped), sorted by `agent_id`, `brain_setting` verbatim from fixture.
- **AST-782 contract:** row keys match `REPO_ADMIN_JSON_CONFIG` agent columns exactly; Betty manifest `TestAst787AgentRepoJsonSeed` locks id set, fixture mapping, column shape, spot-checks, and `apply_agent_repo_json_startup` smoke.
- **Scope gate:** no `src/**` changes; `data/admin/agent_task.json` untouched (AST-786 sibling).

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **advisory** | `code(AST-787)` commit | Same commit includes build-stub lines in plan doc (not just `data/admin/agent.json`) — harmless doc delta, not a product scope leak. |
| **advisory** | Branch diff vs `origin/dev` | Includes **AST-786** `agent_task.json` + fixture rollup from epic merge line — AST-787 product delta is `agent.json` only. |

No **fix-now** items. Closes empty-`agent.json` discuss from **AST-782/786** reviews.

### Recommended actions

| Priority | Action |
| --- | --- |
| resolve-child | None — merge with AST-786 when parent UAT lane clears. |
| Post-merge UAT | Fresh clone restart → Manage Agents shows six personas; divergence banner clears when DB matches repo file. |

## Resolution (2026-06-24)

**Radia review:** clean — no **fix-now** items.

**Advisory (AST-786 rollup on branch diff):** Expected on epic merge line; AST-787 product delta remains `data/admin/agent.json` only.

**Product changes:** none — resolve pass is doc-only. Persona seed shipped in `code(AST-787)` @ `1c8364e`; closes empty-`agent.json` discuss from AST-782/783 reviews.

**§9a dry-run:** `origin/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas` merges cleanly into `origin/dev` and `origin/ftr/AST-756-repo-json-agent-agent-task`.

**Publish tip at resolve:** `origin/sub/AST-756/AST-787-agent-json-empty-seed-six-agent-personas` @ `58208f7`.
