# Anomaly — craft_task_keys shadow + boot run_next

**Linear:** [AST-1113](https://linear.app/astralcareermatch/issue/AST-1113/anomaly-craft-task-keys-shadow-boot-run-next-hard-coded-daisy-chain-in)  
**Parent:** [AST-1109](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy) — Hard-coded daisy chain in config.py  
**Publish ref:** `sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next`

Retire `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["craft_task_keys"]` as craft daisy-chain succession authority. Succession comes from live `agent_task.run_next`. At boot, a one-time SQL series confirm/corrects the craft chain (`craft_company_search_terms` → `craft_joblist_rubric` → … → `craft_prefilter_rubric` → empty). Keep per-hop persist in `run_requested_artifacts_dispatch`. Do not touch JOB_ARTIFACT_ENTRY / hop_task_keys / AST-1108 / statute files.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `requested_artifacts.craft_task_keys` list with singular `craft_task_key` entry; fix TASK_CONFIG assert | utils |
| `src/core/agent.py` | Honor `ctx["suppress_run_next"]` so a hop does not auto-recurse when the caller walks `run_next` itself | core |
| `src/core/candidate.py` | Walk craft hops via entry `craft_task_key` + `_current_agent_task_run_next`; pass `suppress_run_next` on dispatch + UI generate | core |
| `src/data/database.py` | Idempotent `_apply_ast1113_craft_run_next_chain_migration`; wire from `_ensure_agent_task_schema` | data |
| `data/admin/agent_task.json` | Set the same craft `run_next` links so repo admin JSON matches boot topology | data |

## Stage 1: Config — entry key only (no craft_task_keys list)

**Done when:** `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]` has `"craft_task_key": "craft_company_search_terms"` and **no** `"craft_task_keys"` key; the module-level `assert all(k in TASK_CONFIG …)` still passes; `rg 'craft_task_keys' src/` returns zero matches (except this plan doc is not under `src/`).

1. In `src/utils/config.py`, in `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]`, delete the comment `# Sequential fan-in — not run_next daisy-chain…` and the `"craft_task_keys": [ … ]` list.
2. Add `"craft_task_key": "craft_company_search_terms"` (singular — same shape as `requested_resume["craft_task_key"]`).
3. Update the assert immediately below `CANDIDATE_STAGE_DISPATCH` so it uses:
   - `CANDIDATE_STAGE_DISPATCH["requested_resume"]["craft_task_key"]`
   - `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["craft_task_key"]`
   - both stage `task_key` values  
   Do **not** reference `craft_task_keys`.
4. Do not edit hop_task_keys / `JOB_ARTIFACT_ENTRY` / other `CANDIDATE_STAGE_DISPATCH` fields (`task_key`, `trigger_state`, `pass_state`, `auto_mode`).

⚠️ **Decision:** Entry key only in config (true config-owned “where does REQUESTED_ARTIFACTS start”). Hop order is DB `run_next` after Stage 3 — not a replacement list in config.

## Stage 2: `suppress_run_next` in `do_task` + candidate walk / UI

**Done when:** `run_requested_artifacts_dispatch` no longer reads `craft_task_keys`; it walks `run_next` from the entry key with per-hop `_persist_craft_dispatch_success`; each `do_task` call passes `suppress_run_next=True` so `do_task` does not auto-recurse; `run_candidate_artifact_generation` also passes `suppress_run_next=True` so UI one-shot generate stays single-hop after boot wires `run_next`; `python3 -m py_compile` succeeds on touched `.py` files.

1. In `src/core/agent.py`, where `planned_next` / `effective_next` is taken from `agent_task_row.get("run_next")` (~line 2706), if `(ctx or {}).get("suppress_run_next")` is truthy, force `effective_next = ""` (do not recurse). Leave all other run_next behavior unchanged.
2. In `src/core/candidate.py`, rewrite `run_requested_artifacts_dispatch` succession:
   - `craft_key = stage["craft_task_key"]` (singular).
   - Loop while `craft_key` is non-empty:
     - Refresh candidate from DB (same as today).
     - `await do_task(..., ctx={**candidate, "suppress_run_next": True}, ...)` (candidate dict as ctx today — merge the flag onto a shallow copy: `task_ctx = {**(candidate or {}), "suppress_run_next": True}`).
     - On success, `_persist_craft_dispatch_success(...)` as today.
     - `craft_key = _current_agent_task_run_next(craft_key)` (already imported / available via existing import of `_current_agent_task_run_next` in this module — if not imported at top, add `from src.core.agent import _current_agent_task_run_next` next to existing agent imports).
   - Cycle guard: if a `craft_key` repeats in the walk, raise `RuntimeError` with the cycle key (do not infinite-loop).
   - Empty `run_next` on the entry key → one hop only then graduate to `pass_state` (same as a single-item chain).
   - Failure / transition behavior unchanged (`_requested_stage_failure_target`).
3. In `run_candidate_artifact_generation`, when calling `do_task`, pass ctx as a shallow copy of `candidate` plus `"suppress_run_next": True` so Manage UI generate remains one craft per click after Stage 3 sets `run_next` links.
4. Do not change `run_requested_resume_dispatch` (already singular `craft_task_key`; leave `craft_resume_base.run_next` alone).

⚠️ **Decision:** Walk + suppress, not a single unsuppressed `do_task` entry. Craft hops must persist per hop via `_persist_craft_dispatch_success`; unsuppressed `do_task` recursion would skip mid-hop persist and would also make UI entry-hop generate fan through the whole chain.

## Stage 3: Boot SQL confirm/correct + admin JSON alignment

**Done when:** After `_ensure_agent_task_schema`, current `agent_task` rows for the seven craft keys have the expected `run_next` values (queryable); migration is idempotent; `data/admin/agent_task.json` matches the same topology; `python3 -m py_compile src/data/database.py` passes.

Expected chain (former `craft_task_keys` order → terminal empty):

| task_key | run_next |
|----------|----------|
| `craft_company_search_terms` | `craft_joblist_rubric` |
| `craft_joblist_rubric` | `craft_jobdesc_rubric` |
| `craft_jobdesc_rubric` | `craft_do_rubric` |
| `craft_do_rubric` | `craft_get_rubric` |
| `craft_get_rubric` | `craft_like_rubric` |
| `craft_like_rubric` | `craft_prefilter_rubric` |
| `craft_prefilter_rubric` | `` (empty string) |

1. In `src/data/database.py`, add `_apply_ast1113_craft_run_next_chain_migration(conn)` modeled on `_apply_ast834_clear_select_job_page_run_next_migration`:
   - For each `(task_key, expected_run_next)` pair above: `SELECT task_key_uuid, run_next FROM agent_task WHERE task_key = ? AND current = 1 LIMIT 1`.
   - If no row, skip that key (do not insert ghost rows — AST-1108 out of scope).
   - If `(row.run_next or "").strip() == expected_run_next.strip()`, skip.
   - Else `UPDATE agent_task SET run_next = ?, updated_at = CURRENT_TIMESTAMP WHERE task_key_uuid = ?` with the expected value (empty string for terminal).
   - `conn.commit()` once after the series (or after each update — match neighboring migrations’ commit style; AST-834 commits per successful clear).
   - Swallow `sqlite3.Error` on the initial select the same way AST-834 does (early return).
2. Call it from `_ensure_agent_task_schema` immediately after `_apply_ast834_clear_select_job_page_run_next_migration(conn)` (before rubric prompt migrations).
3. In `data/admin/agent_task.json`, set the same seven `run_next` values on the matching `task_key` objects so repo-wins JSON does not disagree with the migration’s intended topology (schema ensure still runs after admin JSON at bootstrap and re-confirms).
4. Do **not** change `craft_resume_base` or non-craft `run_next` rows. Do **not** edit Manage Tasks UI.

⚠️ **Decision:** Confirm/correct = set `run_next` to the expected successor whenever the current row differs (including clearing a wrong non-empty value). Missing current rows are skipped (no seed invent). Observable = after boot, those seven current rows show the table above.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1109 with the Stage N blocked template.
- Leave hop_task_keys (AST-1112), JOB_ARTIFACT_ENTRY (AST-1111), statute/pattern files, AST-1108, and Betty’s test tree untouched.

## Self-Assessment

**Scope:** `Single-Component` — candidate-stage craft succession + `agent_task` boot migration; touches utils/core/data for one anomaly surface.

**Conf:** `high` — succession walk mirrors reading `_current_agent_task_run_next`; boot migration mirrors AST-834; entry-key config mirrors `requested_resume`; suppress flag is a one-line gate at the existing `planned_next` site.

**Risk:** `Medium` — wrong suppress placement would double-run hops or skip persist; wrong migration pairs would mis-order craft artifacts; UI generate without suppress would fan the whole chain after boot.

## Self-review vs ASTRAL_CODE_RULES

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Deletes config hop-order list; succession from live `run_next`; boot writes topology into `agent_task` only.
- **§1.4 / no-hardcoded-sets:** Expected chain pairs live in the migration (and matching admin JSON) as the one-time topology write — not a parallel membership frozenset consulted at dispatch time.
- **§1.1 / database-header-inventory:** Only `agent_task` (already inventoried).
- **§1.1 / in-scope-only:** No hop_task_keys, JOB_ARTIFACT_ENTRY, AST-1108, Manage Tasks UI.
- **§3.3 / layers:** `suppress_run_next` stays in agent; persist stays in candidate; SQL in data.
- **Betty test-tree ban:** Engineer does not edit `tests/` / bible.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next`
**Tip:** `978103de`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `56a9635d` | craft entry key only — drop craft_task_keys list |
| 2 | `b511d46b` | walk craft run_next with suppress_run_next |
| 3 | `978103de` | boot craft run_next chain + admin JSON |

### Radia — code-rubric.v1 (AST-1113)

`[code-rubric] revision=1` · tip reviewed `2e55bcd1` · **Overall: DISCUSS** (C4 stragglers only; deliverable conforms)

**What's solid**

- `craft_task_keys` gone under `src/`; singular `craft_task_key` entry only; walk via `_current_agent_task_run_next` + cycle guard.
- `suppress_run_next` keeps per-hop persist and UI single-hop generate.
- Boot migration + admin JSON match expected seven-hop craft topology; missing rows skipped (no AST-1108 invent).

**Discuss (C4 stragglers)** — Joan excluded; three-dot in-scope (scores `conforms`): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`.
