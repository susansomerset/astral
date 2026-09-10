# AST-455 — Explicit cache block references for tasks: caller tokens and five-segment prompt assembly

**Linear:** [AST-455](https://linear.app/astralcareermatch/issue/AST-455/explicit-cache-block-references-for-tasks-caller-tokens-and-five-segment-prompt-assembly)  
**Parent:** [AST-453 — Explicit cache block references for tasks](https://linear.app/astralcareermatch/issue/AST-453/explicit-cache-block-references-for-tasks)  
**Feature ref (origin only):** `sub/AST-453/AST-455-explicit-cache-block-references-for-tasks-caller-tokens-and-five-segment-prompt-assembly`

## Summary

Upgrade `do_task` / `preview_prompt` / admin preview so **up to five** Anthropic `system` blocks carry `cache_control` ephemerally: resolved `system_prompt` plus each non-empty cache block A–D from `agent_task` (columns `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` per **AST-454**). No-cache and user segments stay **non-cached** user-message blocks. Replace AST-304’s implicit `CACHE_BLOCK_*` chain slot remapping with **caller-prefixed** tokens `CALLER_SYSTEM`, `CALLER_CACHE_A`–`CALLER_CACHE_D`, `CALLER_RESPONSE` in `TOKEN_SOURCES` / `chain_context`; remove `CACHE_BLOCK_A`–`CACHE_BLOCK_D` entries. Build `chain_context` for the next hop only from those caller-resolved strings plus response—**no** automatic promotion of callee no-cache/user into chain keys. Admin preview must match production for at least one multi-hop `run_next` chain when optional chain simulation query params are supplied.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TOKEN_SOURCES`: remove `CACHE_BLOCK_A`–`D`; add `CALLER_SYSTEM`, `CALLER_CACHE_A`, `CALLER_CACHE_B`, `CALLER_CACHE_C`, `CALLER_CACHE_D`, `CALLER_RESPONSE` (all `source: "chain"`). Add `get_manage_tasks_chain_tokens() -> list[str]` returning sorted allowed chain tokens for Manage Tasks (caller set + `CALLER_RESPONSE` + `SELECTED_AGENT`; **exclude** any hypothetical `NO_CACHE_BLOCK` / `USER_PROMPT` names they are not in registry). | utils |
| `src/core/agent.py` | Replace `_assemble_blocks` usage with a new helper (e.g. `_assemble_blocks_seven_segment`) that accepts **five** optional cached plaintext strings (`sys`, cache A–D) and builds `system_blocks[]` count 1..5 plus `user_blocks[]` from no-cache prefix pattern + live + stamped user identical ordering to today’s nocache/live/user sequencing; **`skip_cache` True** ⇒ strip all `cache_control` keys mirroring legacy. Resolve each segment via `resolve_tokens(..., chain_context)` before assembly. Extend `_store_prompt_blocks` to persist each non-empty cache block as its own row with `CACHE_A` … `CACHE_D` `block_type`s matching **`BLOCK_TYPES`**, SYSTEM unchanged, nocache/live/user unchanged. Rewrite `_chain_tokens_for_next_hop` to accept **resolved** strings: `caller_system`, `caller_cache_a`…`caller_cache_d`, plus `caller_response` serialized like today’s `caller` assembly—return dict keyed only `CALLER_*` + reuse `CALLER_RESPONSE` shaping. **`do_task`**: read four cache columns; pass into assembly; compute hop context from resolved segment strings **after** token resolution **on callee** surfaces; recurse `run_next` with `_merge_chain_context_for_next_hop` unchanged merging rules. **`preview_prompt`**: add optional `chain_context` argument forwarded to `_chain_context`; when absent behave as today for first hop. | core |
| `src/core/candidate.py` | `preview_task_prompt`: support optional query-driven chain simulation (see Stage 4) without breaking existing callers signature—add defaulted kwargs or sibling function re-export called from Flask only. | core |
| `src/ui/api/api_admin.py` | `task_tokens`: return `get_manage_tasks_chain_tokens()` instead of bare `get_tokens()` **or** add parallel endpoint `tasks/meta/chain_tokens` returning chain subset **and** wire frontend in AST-456—**this ticket** must expose chain token list REST-side (pick one endpoint, document slug). `preview_task` / related: pass synthesized `chain_context` when request args include simulated hop markers (Stage 4). | ui |

Spike output under `debug/spikes/` only.

---

## Stage 1: Config token registry

**Done when:** `resolve_tokens('{$CALLER_SYSTEM}', ..., chain={'CALLER_SYSTEM':'xy'})` yields `xy`; `{$CACHE_BLOCK_A}` untouched (not in TOKEN_SOURCES) remains literal `{...}` substring per forward-compat rule existing in `resolve_tokens` for unknown names—or confirm current behavior strips nothing.

1. Implement registry edits exactly as Files table; preserve alphabetical sort in `get_tokens()` consumer behavior—**new** `get_manage_tasks_chain_tokens()` **only** for Manage Tasks picker surface.
2. Ensure **no** `NO_CACHE_BLOCK` or `USER_PROMPT` keys exist in `TOKEN_SOURCES` (parent AC4).
3. `python3 -m py_compile src/utils/config.py`

---

## Stage 2: Assembly + storage

**Done when:** Non-empty cache B/C/D produce distinct API system blocks **and** distinct `agent_data` rows labeled `CACHE_B`/`CACHE_C`/`CACHE_D` when `store_agent_data` path exercised.

1. Factor assembly from `_assemble_blocks` into `_assemble_blocks_seven_segment(system_text, caches: tuple[str|None, …4], nocache_text, live_text, user_text, …)` returning same tuple shape `(system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens)` **with** runtime_prompt ledger entries labeled per block consistently (`cache_a`, etc.)—maintain cardinality rules for tests expecting list shape (extend labels in obvious pattern).
2. **Do not** inject hardcoded headings like `--- CACHED CONTEXT ---` into **cached** segments unless parent issue demands—parent says separate cached API blocks; operators own visible separators inside DB text.
3. For **no-cache** + **live** segments, reuse existing prefix strings (`--- ADDITIONAL CONTEXT ---`, `--- CONTENT ---`) verbatim to avoid churn.
4. Update `_store_prompt_blocks` signatures to accept optional `cache_b_text`, … or a list—store each with proper `BLOCK_TYPES` enum strings already defined.
5. `python3 -m py_compile src/core/agent.py`

---

## Stage 3: `do_task` resolution + chain pass-through

**Done when:** Two-hop chain with markers in each caller segment flows into callee `{$CALLER_*}` expansions; missing chain keys log-and-empty like today’s chain branch.

1. After loading `agent_task_row`, compute:
   - `raw_system`, `raw_ca`, `raw_cb`, `raw_cc`, `raw_cd`, `raw_nocache`, `raw_user` from DB keys `system_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, `user_prompt` (`.get` safe if column absent pre-454 merge—post 454 required).
2. Resolve in order: `system_content = resolve_tokens(raw_system, …)` using `_cc`; same for each cache block and nocache/user (chain_context available for callee tokens on **this** hop).
3. Feed **resolved** `system_content` + four cache resolved strings into assembly (None/empty → skip block).
4. Replace `_chain_tokens_for_next_hop` body: map **only** `CALLER_SYSTEM` = `system_content`, `CALLER_CACHE_A` = resolved cache A string, …, `CALLER_RESPONSE` from parsed output using existing JSON/string rules in current function.
5. Remove assignment to legacy `CACHE_BLOCK_*` keys entirely.
6. **Three-hop explicit test scenario (manual + unit if permitted without touching `tests/`):** builder proves hop2 cache A contains `{$CALLER_RESPONSE}` text so hop3 sees it via `CALLER_CACHE_A`—document replication steps in Code Complete comment (Betty may formalize).
7. `python3 -m py_compile src/core/agent.py`

⚠️ **Decision:** Non-chained runs pass `chain_context=None`; callee tokens empty → warnings only; **no** silent fallback to legacy slot mapping.

---

## Stage 4: Admin preview parity

**Done when:** `GET /api/admin/tasks/<task_key>/preview?candidate_id=…&chain_sim=1` (exact param names chooser in implementation) returns JSON including **per-segment** resolved strings matching `preview_prompt` / `do_task` ordering for at least: `system`, `cache_a`, `cache_b`, `cache_c`, `cache_d`, `nocache`, `user` keys (add keys only if non-empty to reduce payload bloat **or** always include—pick one in code and document here in Revisions if changed).

**Revisions:** Always include segment keys (`cache_a`…`cache_d`, legacy `cache` = A). Multi-hop simulation: **`chain_sim=1`** (`true`/`yes` accepted) plus optional **`simulate_parent=<task_key>`**, **`simulate_parsed=<payload>`**, and overlays **`chain_ctx_<TOKENNAME>=`** (example: `chain_ctx_CALLER_RESPONSE=...`).

1. Implement **optional** multi-hop simulation: when query includes parent task key + marker payload OR when `simulate_caller_*` args present, build `chain_context` dict without calling Anthropic (mirror `do_task` resolution for caller hop only).
2. Reuse `preview_prompt` core by lifting shared resolver into private helper if needed to avoid duplication >10 lines.
3. `python3 -m py_compile src/ui/api/api_admin.py src/core/candidate.py`

---

## Stage 5: Timesheet / token accounting sanity

**Done when:** `no_cache_prompt_tokens` / `no_cache_live_tokens` still computed from character lengths of **non-cached** segments only; cached segments continue contributing via Anthropic cache fields—**no** double counting after split.

1. Recompute `no_cache_prompt_tokens` using `len(nocache_content)+len(user_content)` chars // `CHARS_PER_TOKEN` matching old formula scope (live separate).
2. `python3 -m py_compile src/core/agent.py`

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Core `do_task` assembly + global token registry + admin preview contract.

**Conf:** `Medium` — Clear parent spec; careful ordering of resolve vs chain merge prevents subtle bugs.

**Risk:** `HIGH` — Regression on consult dispatch + artifact chains if assembly or chain_context wrong; requires strict compile + Betty integration tests post-build.

---

## Plan vs `ASTRAL_CODE_RULES.md`

| Section | Compliance |
|---------|------------|
| §1.3 DRY | Shared preview/resolution helper if duplication emerges; keep assembly in `agent.py`. |
| §2.1 config | Token registry lives in `config.py`; no secret env. |
| §2.4 batch | Unaffected. |
| §2.6 state machine | Unaffected. |
| §3.3 imports | UI → core only for preview helper usage. |

No `conf-!!-NONE`.

---

## Review (implementation stub)

Built by Ada (`dev-ada`). Cherry-picked to **`origin/sub/AST-453/AST-455-explicit-cache-block-references-for-tasks-caller-tokens-and-five-segment-prompt-assembly`**; update commit hash(es) below after publish.

**Branch:** `sub/AST-453/AST-455-explicit-cache-block-references-for-tasks-caller-tokens-and-five-segment-prompt-assembly`

**Commits:** `c62bff946fb0b1a6cbc392b5ec4434dffd959b6e` (product `feat(AST-455)` on `dev-ada`; cherry-pick to this sub ref)

## Review

**Diff:** `git diff origin/dev...origin/ftr/AST-455` · **Code tip reviewed (pre-this-doc):** `39a5ae4d489880fb9bf27f2f4771c3acf94e9653`

### What’s solid

- `TOKEN_SOURCES`: `CACHE_BLOCK_*` retired; caller keys + `tests/component/utils/test_config.py` prove legacy `{$CACHE_BLOCK_A}` stays literal (**D3**/forward-compat as planned).
- `get_manage_tasks_chain_tokens()` aggregates all `chain` entries; excludes nonexistent `NO_CACHE_BLOCK`/`USER_PROMPT` keys (**AC surface** aligned).
- `_assemble_blocks_seven_segment`, `_store_prompt_blocks`, and `do_task` read four DB cache columns consistently; `_chain_tokens_for_next_hop` maps **resolved** plaintext only (**AST-454** handoff satisfied).
- `preview_prompt` + `preview_task_prompt`/`simulated_chain_context_for_preview` + `/tasks/meta/chain_tokens` and query-driven chain simulation mirror plan Stage 4; UI layer stays thin Flask wiring.

### Issues

None **fix-now**. Accepted tolerances cite plan + comments: omission of injected `--- CACHED CONTEXT ---` on cached segments is **explicit Stage 2** (“operators own separators”).

### Recommended actions

| Sev | Audience | Finding |
| --- |----------|---------|
| **discuss** | Prompt authors | Cached Anthropic payloads no longer prepend `--- CACHED CONTEXT ---`; delimiter must live in segment text where operators still want it. |
| **discuss** | Operators | Migrate any lingering `{$CACHE_BLOCK_*}` references to `{$CALLER_*}`; literals otherwise stay unresolved (**ASTRAL_TEST_BIBLE §7.13o**). |
| Advisory | Historical docs | Feature docs under `docs/features/artifacts/` still describe AST-304 `CACHE_BLOCK_*` wiring—expected archival drift alongside AST-455. |

---

## Resolution

**Date:** 2026-05-23  

**Versus Radia (`review-astral`, Linear comment thread):**

- **Fix-now:** none (counts 0). No targeted product changes landed in this **`resolve-astral`** pass — reviewed tip (**`39a5ae4d`**) matched plan tolerances documented above.
- **Discuss (Radia buckets 2 × non-blocking):** Noted without code churn — prompts that relied on historically injected separators must fold delimiters into stored segment copy; callers must migrate `{$CACHE_BLOCK_*}` → `{$CALLER_*}` (`§7.13o`). UAT/playbook outreach is operator/Susan-facing, outside this cherry-pick.
- **Advisory (historical `docs/features/artifacts/` drift):** Logged — no doc sweep here (archival drift only per review).
- **Plan doc:** Radia’s **`docs(AST-455): Radia review …`** from `origin/ftr/AST-455` (**`77c1bfd8`**) merged to `dev-ada`; **`## Resolution`** closes **Review Posted**. **Publish ref:** **`origin/ftr/AST-455`**. Parent **AST-453**.

