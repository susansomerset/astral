# AST-1448 — Persist prompt before provider

- **Linear:** [AST-1448](https://linear.app/astralcareermatch/issue/AST-1448)
- **Parent:** [AST-1442](https://linear.app/astralcareermatch/issue/AST-1442)
- **Publish ref:** `sub/AST-1442/AST-1448-persist-prompt-before-provider`

Stored LLM calls (production `do_task` and Ad Hoc workbench Test) currently assemble prompt segments, await the provider, then write those segments to `agent_data`. A kill or restart during the await leaves no durable prompt. This ticket commits the same `_store_prompt_blocks` writes **before** `send_to_anthropic` / `send_to_deepseek` / `run_adhoc`, then writes RESPONSE only after return. `save_agent_data` already `conn.commit()`s per row, so those prompt rows are queryable by `batch_id` while the call is in flight. Storage-off paths stay storage-off. Latest-per-task / agent story stay RESPONSE-gated (`list_entity_latest_agent_refs` filters `block_type = 'RESPONSE'`). Catalog lands `pattern.agent.prompt-persist-before-provider` as **`status: proposed`** (`proposed_in: AST-1442`); product code does not look up that id.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/patterns/agent/pattern.agent.prompt-persist-before-provider.md` | New proposed catalog entry | docs |
| `canon/patterns/README.md` | Add the new row; bump proposed count | docs |
| `canon/patterns/HARVEST.md` | Add supporting-package + crosswalk rows | docs |
| `src/core/agent.py` | Persist prompt segments before provider at both stored call sites; RESPONSE stay after return | core |

Do **not** edit: `src/data/database.py` (`save_agent_data` already commits), `src/external/anthropic.py`, `src/external/deepseek.py`, `src/core/timesheets.py`, `src/utils/config.py` (`BLOCK_TYPES` / `ENTITY_TYPES` unchanged), `src/ui/**`, `run_adhoc` (storage-off), hop ledger / entity state transitions, `tests/`, bible.

## Stage 1: Propose the persist-before-provider catalog entry

**Done when:** `canon/patterns/agent/pattern.agent.prompt-persist-before-provider.md` exists with SCHEMA frontmatter `status: proposed`, `proposed_in: AST-1442`, `approved_by: null`, `approved_at: null`. README and HARVEST list it. No `src/` changes in this stage.

1. Create directory `canon/patterns/agent/` if missing. Add `canon/patterns/agent/pattern.agent.prompt-persist-before-provider.md` with this frontmatter and body (no extra frontmatter keys):

```yaml
---
id: pattern.agent.prompt-persist-before-provider
name: Persist assembled prompt before provider call
status: proposed
proposed_in: AST-1442
approved_by: null
approved_at: null
canonical_refs:
  - path: src/core/agent.py
    symbol: do_task
  - path: src/core/agent.py
    symbol: run_adhoc_workbench_test
  - path: src/core/agent.py
    symbol: _store_prompt_blocks
related_statutes:
  - astral.agent.do-task-delegation
  - astral.batch.entity-agent-responses-latest-only
  - astral.layers.core-vs-external-bright-line
  - astral.standards.debug-contract-gated
  - astral.batch.batch-id-first
supersedes: null
superseded_by: null
---
```

Body sections in SCHEMA order:

- `# Problem` — Prompt segments are only written after the provider returns, so a kill or process restart during the await leaves no durable record of what was sent.
- `# Solution shape` — When `agent_data` storage is on, commit assembled prompt segments via existing `_store_prompt_blocks` / `save_agent_data` **before** the external provider await; write RESPONSE after return (success body or failure-audit, same as today). Prompt writes are best-effort: a failed prompt write must not abort the provider call. Persist stays in core; provider I/O stays in external. Latest-per-task and agent story remain RESPONSE-gated. Point at `canonical_refs` — do not paste large code.
- `## When not to use` — bullets: storage-off calls (`store_agent_data=False`, bare `run_adhoc`); writing timesheets before the provider returns; treating a prompt-only interrupted batch as latest story / latest-per-task; aborting the provider call because prompt persist failed; adding a new table or block type; UI for prompt-only batches.
- `## Notes` — Implementation must not depend on this catalog id until `status: approved` (AUTHORING). This child lands the file as proposed and implements the sequencing invariant; Archie sets approved later.

2. In `canon/patterns/README.md`, update the harvested-corpus sentence that currently says three entries are `status: proposed` to **four**. Add this table row after the last proposed row (`pattern.ui.in-place-live-refresh`):

   `| \`pattern.agent.prompt-persist-before-provider\` | proposed | \`agent/pattern.agent.prompt-persist-before-provider.md\` |`

3. In `canon/patterns/HARVEST.md`, add a supporting-package row:

   `| persist prompt before provider | \`pattern.agent.prompt-persist-before-provider\` |`

   and a Crosswalk row:

   `| create (AST-1442) | \`pattern.agent.prompt-persist-before-provider\` | agent | \`agent/pattern.agent.prompt-persist-before-provider.md\` | AST-1442 | proposed — commit prompt segments before provider await; RESPONSE after return |`

⚠️ **Decision:** Land the catalog id as **proposed**, not approved. AUTHORING forbids implementation *depending on* an unapproved id; the product change is a call-order move that does not import or look up the id. Do not edit `docs/ASTRAL_CODE_RULES.md` in this ticket.

## Stage 2: `do_task` — prompt persist before provider await

**Done when:** In `do_task`, `_store_prompt_blocks` runs after `_assemble_blocks_seven_segment` and **before** `await send_to_anthropic` / `await send_to_deepseek`. `_store_response_block` (success and failure-audit) still runs only after those awaits return. `_should_store` is still `store_agent_data and batch_id and entity_type`. Persist failure still does not skip the provider call. `store_agent_data=False` still writes no prompt or RESPONSE rows. Prompt-block kwargs (`entity_id=index if index else None`, `caches_resolved_four=(rca or "", rcb or "", rcc or "", rcd or "")`, etc.) are unchanged. When `debug=True`, `_store_prompt_blocks` Style D found/recorded (index N/M) emits before the await; `_store_response_block` still emits after return. When `debug=False`, this path adds no new debug-contract lines. `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py` `do_task`, immediately **after** the post-assemble `if debug:` block that logs `llm_params` / `blocks system=...` (the block that ends with `runtime_prompt_segments={len(runtime_prompt)}`) and **before** `if provider == "anthropic":`, insert the existing persist setup **verbatim** (same kwargs, same `try`/`except Exception` + `logger.debug("_store_prompt_blocks failed", exc_info=True)`):

```python
    prompt_blocks: List[Dict[str, str]] = []
    _should_store = store_agent_data and batch_id and entity_type
    if _should_store:
        try:
            prompt_blocks = _store_prompt_blocks(
                entity_type=entity_type,
                task_key=task_key,
                batch_id=batch_id,
                system_content=system_content,
                caches_resolved_four=(rca or "", rcb or "", rcc or "", rcd or ""),
                nocache_content=nocache_content,
                user_content=user_content,
                live_content=live_content,
                debug=debug,
                entity_id=index if index else None,
            )
        except Exception:
            logger.debug("_store_prompt_blocks failed", exc_info=True)
```

2. **Delete** the duplicate persist block that currently sits after `result["runtime_prompt"] = runtime_prompt` (the comment `# Store prompt blocks in agent_data (non-blocking; best-effort)` through the `_store_prompt_blocks` `except`). Leave `result["runtime_prompt"] = runtime_prompt` and the following provider-failure `logger.error` / `if not result.get("success"):` RESPONSE audit store unchanged.

3. Do **not** call `_store_prompt_blocks` a second time after the await. Do **not** move `_store_response_block`, timesheet recording (`record_timesheet` on the external send), hop ledger close, or validation/decode. Do **not** add a new persist helper — relocate this call only. Do **not** treat persist failure as fatal: keep the `except Exception` swallow.

⚠️ **Decision:** Relocate the existing call rather than wrap persist+await in a new function. One sequencing change, same helper, same best-effort contract. Durability is the existing `save_agent_data` `conn.commit()` per row — do not add a data-layer flush.

## Stage 3: Workbench Test — prompt persist before `run_adhoc`

**Done when:** `run_adhoc_workbench_test` writes prompt segments after ledger `RUNNING` and **before** `await run_adhoc(...)`. RESPONSE (success stringify / failure-audit) still runs only after `run_adhoc` returns a result dict. Bare `run_adhoc` still writes no `agent_data`. If `run_adhoc` raises, the existing inner `except` still marks the ledger FAILED and re-raises; prompt rows already committed for that `batch_id` remain. Persist failure still does not skip `run_adhoc`. `python3 -m py_compile src/core/agent.py` passes.

1. In `run_adhoc_workbench_test`, **move** the existing `_store_prompt_blocks` `try`/`except` (the block that uses `caches_resolved_four=(cache_content or "", cache_content_b or "", ...)` and `entity_id=entity_id if entity_id else None`) to immediately **before** `result = await run_adhoc(`, still **inside** the outer `try` and **outside** the inner `except Exception` that marks ledger FAILED (persist must not be treated as a workbench crash). Keep the swallow:

```python
        try:
            _store_prompt_blocks(
                entity_type=entity_type,
                task_key=workbench_task_key,
                batch_id=batch_id,
                system_content=system_content,
                caches_resolved_four=(
                    cache_content or "",
                    cache_content_b or "",
                    cache_content_c or "",
                    cache_content_d or "",
                ),
                nocache_content=nocache_content,
                user_content=user_content,
                live_content=live_content,
                debug=debug,
                entity_id=entity_id if entity_id else None,
            )
        except Exception:
            logger.debug("_store_prompt_blocks failed", exc_info=True)

        try:
            result = await run_adhoc(
```

2. **Delete** the post-`run_adhoc` `_store_prompt_blocks` block (the one currently after the inner `except` / `raise` and before `if not result.get("success"):`). Leave ledger updates, `_store_response_block` success/failure, `compute_batch_cost`, `result["batch_id"] = batch_id`, and the `finally` log flush unchanged.

3. Do **not** add `store_agent_data` or `_store_prompt_blocks` inside `run_adhoc`. Do **not** change Preview (`adhoc_preview` / `_resolve_adhoc`). Do **not** change `BLOCK_TYPES`, compression, content-dedup, or entity_id stamping kwargs.

⚠️ **Decision:** Workbench persist stays in `run_adhoc_workbench_test`, not inside storage-off `run_adhoc`. That keeps the two stored call sites (`do_task` and workbench Test) as the only persist-before-provider surfaces.

## Execution contract

- Execute stages in order. One commit per stage on this epic worktree, then `git push origin HEAD:sub/AST-1442/AST-1448-persist-prompt-before-provider`.
- Do not add files, config blocks, tables, routes, or UI not listed above.
- Do not edit `tests/` or the bible. Existing component tests that assert `_store_prompt_blocks` was called once after a mocked provider **returns** still hold (call still happens once). Betty owns any new in-flight / kill-mid-call order assertion.
- If a referenced helper signature has drifted, stop and comment on **AST-1442** with the Stage N blocked template — do not improvise.

## Pattern / statute map (this ticket)

| Id | Role |
|----|------|
| `pattern.agent.prompt-persist-before-provider` | Introduced as proposed (Stage 1); sequencing in Stages 2–3 |
| `pattern.batch.entity-agent-responses` | Reuse — latest-per-task stays RESPONSE-gated; do not change `list_entity_latest_agent_refs` |
| `astral.agent.do-task-delegation` | Core still delegates I/O through `send_to_*`; reorder persist vs await inside `do_task` |
| `astral.batch.entity-agent-responses-latest-only` | Prompt-only interrupted batches must not become latest story |
| `astral.layers.core-vs-external-bright-line` | Persist stays in core; provider I/O stays in external |
| `astral.standards.debug-contract-gated` | Prompt found/recorded before await; RESPONSE after return; quiet when `debug=False` |
| `astral.standards.database-header-inventory` | No new tables |
| `astral.standards.dry-and-focused-functions` | Reuse `_store_prompt_blocks`; do not fork a second store path |
| `astral.standards.in-scope-only` | Sequencing + durability of existing writes only |
| `astral.standards.data-raises-caller-logs` | No data-layer logging; persist failure remains `logger.debug` in core |
| `astral.batch.batch-id-first` | Prompt and RESPONSE rows keep the existing `batch_id` |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1448
**Overall:** APPROVED
**Commit:** `ecf7bbbe2640a391a61e49ab7a9834f131ea0952` (`origin/sub/AST-1442/AST-1448-persist-prompt-before-provider`)

## Traceability
AC1 production persist-before-call → S2; AC2 workbench Test same → S3; AC3–4 RESPONSE success/failure after return → S2–S3 (do not move `_store_response_block`); AC5 kill/restart prompt-only + later run on a new `batch_id` → S2–S3 relocate-only; AC6 storage-off → S2 `_should_store` / S3 no persist in `run_adhoc`; AC7 debug found/recorded before await, RESPONSE after, quiet when off → S2; AC8 latest-per-task stays RESPONSE-gated → S2–S3 (no `list_entity_latest_agent_refs` edit); S1 → parent New patterns proposed (`pattern.agent.prompt-persist-before-provider` as `status: proposed`, no runtime id lookup).

**Findings**

- **acceptable** — Stage 1 README: insert-after `pattern.ui.in-place-live-refresh` is stale; current last `proposed` row is `pattern.dispatch.run-next-chain-authority`. Engineer should bump the harvested-corpus proposed count to four and add the new row with the other proposed entries; not a definition miss.
- No `fix-now`. No R3 `violates`. R5 maps. R6: files stay `core` + `canon/patterns`; no new tables/config/`ui`; reuse `_store_prompt_blocks`; `save_agent_data` already `conn.commit()`s per row; AUTHORING “must not depend on unapproved id” is honored (catalog file only). Cited reuse patterns resolve `status: approved`. Parent AC and this child’s AC match.

R1–R4 executed in-session (universal set scored; scoped exclusions are layer/path misses: `data`/`ui`/`utils`/`scripts`/`tests`/`docs/features/**`/seed-admin paths). Slim R7: statute table not appended.

context_tokens≈48000
