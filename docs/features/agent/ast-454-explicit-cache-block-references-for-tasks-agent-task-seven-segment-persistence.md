# AST-454 — Explicit cache block references for tasks: agent_task seven-segment persistence

**Linear:** [AST-454](https://linear.app/astralcareermatch/issue/AST-454/explicit-cache-block-references-for-tasks-agent-task-seven-segment)  
**Parent:** [AST-453 — Explicit cache block references for tasks](https://linear.app/astralcareermatch/issue/AST-453/explicit-cache-block-references-for-tasks)  
**Feature ref (origin only):** `sub/AST-453/AST-454-explicit-cache-block-references-for-tasks-agent-task-seven-segment-persistence`

## Summary

Persist all seven Manage Tasks prompt segments in `agent_task`: system prompt (existing `system_prompt`), four independent cache segments (legacy `cache_prompt` is **semantic slot A** plus new columns for slots B–D), no-cache (`nocache_prompt`), and user (`user_prompt`). Ship schema migration (`ALTER ADD` for cache B/C/D only), versioning rules that treat **any** segment edit as prompt content versioning, expanded admin read/write APIs, and list-row metadata lengths so Manage Tasks / admin list stay consistent. Legacy rows keep working: historical `cache_prompt` text stays in **cache block A**. Runtime Anthropic assembly and caller tokens belong to **AST-455**; React panels belong to **AST-456**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Extend `agent_task` header inventory; `_ensure_agent_task_schema` ADD `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` (TEXT NOT NULL DEFAULT ''); widen `save_agent_task`/`sync_agent_tasks`/`list_candidate_tasks` INSERT/UPDATE/SELECT; versioning compares all seven segments + existing metadata rules | data |
| `src/ui/api/api_admin.py` | `update_task`: accept/pass `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` into `save_agent_task`; `_enrich_tasks`: include lengths / token estimates aggregating all cache slots (sum of raw lengths; for `parsed_cache_tokens` and `task_ready`, check unresolved `{$...}` across **concatenated** cache A–D resolved strings with explicit separator `\n---\n` between blocks only for the regex probe, not stored); `cache_write` threshold `total_cache ≈ system_tokens + summed parsed cache segments` when model present | ui |
| Other `agent_task` call sites found by grep for `save_agent_task`, `cache_prompt=` | Align tuple length / kwargs with new columns (if any besides `api_admin`; fix same commit) | — |

Spike scripts default `--out-dir` → `debug/spikes/<issue>/` only; nothing under repo-root `artifacts/`.

---

## Stage 1: Schema and migration

**Done when:** Fresh DB creates full column set; upgraded DB picks up three new TEXT columns default `''`; `PRAGMA table_info(agent_task)` shows `cache_prompt` + `_b/_c/_d`.

1. Update the **bullet** for `agent_task` in **`src/data/database.py`** header (first ~40 lines inventory) documenting seven semantic segments: `system_prompt`, `cache_prompt` (block A), `cache_prompt_b/c/d` (blocks B–D), `nocache_prompt`, `user_prompt`, plus existing `run_next`, `agent_id`, versioning columns.
2. In `_ensure_agent_task_schema`, after existing `system_prompt` migration block, for each of `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` missing from `PRAGMA table_info`, execute `ALTER TABLE agent_task ADD COLUMN <name> TEXT NOT NULL DEFAULT ''` then `conn.commit()`.
3. **No destructive table rebuild** unless an existing SQLite file contains an unmigrated anomaly—reuse the same ALTER pattern as `run_next`/`system_prompt`.
4. `python3 -m py_compile src/data/database.py`

⚠️ **Decision:** Database column naming uses `cache_prompt` as slot A instead of renaming to `cache_prompt_a` to avoid rewriting every INSERT in migration history and all foreign tooling; semantics are spelled in the inventory comment only.

---

## Stage 2: `save_agent_task` semantics and versioning

**Done when:** Any change among the seven segments OR among `user_prompt`/`cache_prompt`/`*_b`/`*_c`/`*_d`/`nocache_prompt`/`system_prompt` bumps a new row version (current=1) like today’s **content versioning** branch; purely `agent_id` / `run_next` metadata updates behave like today.

1. Extend `save_agent_task` kwargs with optional `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` (same typing style as existing cache fields—`Optional[str]` coerced via `existing` pattern).
2. Widen SELECT of current row to read all seven segments plus `task_key_uuid`, `agent_id`, `run_next`.
3. On insert for new tasks, set new columns to `(x or "").strip()` or `''` consistent with sibling fields.
4. Compute `content_changed` as inequality on **pairwise** normalized strings for: `user_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, `system_prompt` (match existing strip rules: `system_prompt` uses `.strip()` when comparing like current code).
5. Copy `run_next` / `agent_id` behavior unchanged from current implementation.
6. Metadata-only branch: allow updating new cache columns via `UPDATE` when `content_changed` is false ONLY if introducing new kwargs `None`-means-no-op matches today—that is, unchanged.
7. `python3 -m py_compile src/data/database.py`

---

## Stage 3: `list_candidate_tasks` and sync

**Done when:** List rows expose char lengths useful to admin `_enrich_tasks`; `sync_agent_tasks` inserts include new columns defaulted empty.

1. Extend `SELECT` in `list_candidate_tasks` with `LENGTH(cache_prompt_b|c|d)` as `cache_prompt_b_len`, `cache_prompt_c_len`, `cache_prompt_d_len`.
2. In `sync_agent_tasks` INSERT tuple, extend column list matching fresh CREATE semantics (seven empty prompt fields plus system/run_next defaults).
3. `python3 -m py_compile src/data/database.py`

---

## Stage 4: Admin API payload

**Done when:** `GET /api/admin/tasks/<task_key>` JSON includes keys `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` from `get_agent_task`; `PUT` accepts same keys (`body.get(...)`) forwarded to `save_agent_task`; miss keys → pass `None` so **no unintended wipe** consistent with PUT today.

1. Extend `database.save_agent_task(...)` invocation in **`update_task`** with `cache_prompt_b=body.get("cache_prompt_b"), ...`.
2. Grep codebase for **`save_agent_task(`** beyond this file—update any callers in the **same Astral codebase** touched by this ticket (typically none else); if spike scripts cite old signature, defer—spikes exempt but must compile if touched.
3. `python3 -m py_compile src/ui/api/api_admin.py`

---

## Stage 5: `_enrich_tasks` cache metrics alignment

**Done when:** List API remains backward-compatible keys; admins see realistic cache mass when multiple cache slots populated.

1. Compute `cache_raw_total = sum(LENGTH(...))`-equivalent server-side via `database.list_candidate_tasks` new len fields (`cache_prompt_len` + `_b/_c/_d`).
2. For `$`-token cleanliness, build `combined_cache_probe = concatenate(resolve_tokens(blockA), …, resolve_tokens(blockD))` using real `resolve_tokens` per block with same `cd`, `task_key`, `_cc` as today’s single-block path; `task_ready` false if **any** block still has unresolved `{$TOKEN}` pattern (reuse same regex as line ~180).
3. `parsed_cache_tokens = len(combined_cache_probe) // CHARS_PER_TOKEN` when `task_ready`.
4. `total_cache = system_tokens + parsed_cache_tokens` when `task_ready` else fall back to `system_tokens + base_cache_tokens` using **raw** sum of four cache lengths (document in code comment **two-line** why approx is acceptable when unresolved tokens).
5. `python3 -m py_compile src/ui/api/api_admin.py`

---

## Stage 6: Runtime build handoff note (no `agent.py` edits here)

**Done when:** Plan doc states explicitly: **AST-455** must read `cache_prompt_b/c/d` from `agent_task_row`; until then production only uses block A in `do_task`—acceptable intermediate because **this ticket** only promises persistence + admin API per child scope.

1. Add a short **Handoff to AST-455** bullet in a Linear comment at Code Complete (builder), not in this plan body.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches authoritative `database.py` schema + admin task API contract; multiple integration points but one vertical slice (persistence).

**Conf:** `Medium` — Follows existing `save_agent_task` versioning and ALTER patterns; multi-column versioning is detailed but not novel.

**Risk:** `Medium` — Migration mis-ordered ALTER or missed INSERT column tuple causes runtime DB errors for admin saves; mitigated by compile check + Betty tests on affected paths later.

---

## Plan vs `ASTRAL_CODE_RULES.md`

| Section | Compliance |
|---------|-------------|
| §1.3 DRY | Reuse `_ensure_agent_task_schema` ALTER cascade; extend `save_agent_task` branches instead of duplicate upsert helpers. |
| §2.1 config | Do **not** add prompt text to `config.py`; segmentation is DB-backed per parent spec. |
| §2.4 batch processing | Not applicable—no dispatcher changes. |
| §2.6 state machine | Not applicable—no transitions. |
| §3.3 imports | Database changes only touch data + thin API (allowed). |
| §3.5 naming | Column names lowercase snake per existing `agent_task` fields. |

No conflicts forcing `conf-!!-NONE`.

---

## Review (implementation stub)

Built by Ada (`dev-ada`). Product commits on `origin/sub/AST-453/AST-454-explicit-cache-block-references-for-tasks-agent-task-seven-segment-persistence` via cherry-pick; update the commit hash(es) below after publish.

**Branch:** `sub/AST-453/AST-454-explicit-cache-block-references-for-tasks-agent-task-seven-segment-persistence`  

**Commits:** `f8b263d10e5bce455269ed9c173a2ca175957f7a` (product `feat(AST-454)` cherry-picked to this sub ref)

## Review

**Diff:** `git diff origin/dev...origin/ftr/AST-454` · **Baseline tip (pre-this-doc):** `69f69c17f455fcbf0bffe53c79457e8d805765b7`

### What’s solid

- `agent_task` inventory + `_ensure_agent_task_schema` ALTERs for `cache_prompt_b|c|d`; v1 → v2 INSERT column list aligns with bindings.
- Versioning expands to all seven segments; stripping rules for cache B/C/D via `_strip_seg` match plan; dropping ad-hoc `system_prompt` updates on non-versioning UPDATE path matches “system changes version” semantics.
- `list_candidate_tasks` length aggregates feed `_enrich_tasks` joined probe (`\n---\n`) and `task_ready` / approximate `total_cache` behavior documented in-admin.
- `update_task` passes through optional B/C/D with `None` → leave-untouched parity with PUT semantics.

### Issues

None **fix-now**. No rubric-aligned blockers (**ASTRAL_CODE_RULES** §1 / database bind review).

### Recommended actions

| Priority | Audience | Action |
|----------|-----------|--------|
| Advisory | UAT / operators | Smoke one migrated legacy task (single `cache_prompt` only) round-trip GET/PUT/admin list enrichment per AC2. |

---

## Resolution

**Date:** 2026-05-23  

**Versus Radia (`review-astral`, Linear comment thread):**

- **Fix-now:** none (counts 0). No product deltas required for acceptance of that review bucket.
- **Discuss / Advisory:** Acknowledged — UAT/operators should smoke one migrated legacy-only-cache-A task GET/PUT + list enrichment (AC2 advisory); deferred to Susan’s batch UAT, not gated on further code here.
- **Plan doc:** Radia’s **`docs(AST-454): Radia review — seven-segment persistence`** landed from `origin/ftr/AST-454` (**`b8c89791`**) onto `dev-ada`; this section records closure from **resolve-astral** before **User Testing**. **Publish ref:** **`origin/ftr/AST-454`** (Cherry picks for prep-uat vs parent **AST-453**).


