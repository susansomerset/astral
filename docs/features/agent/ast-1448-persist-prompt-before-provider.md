<!-- linear-archive: AST-1448 archived 2026-09-09 -->

## Linear archive (AST-1448)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1448/persist-prompt-before-provider-write-to-agent-data-before-calling-the  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1442 — write to agent_data BEFORE calling the prompt, save the response when it comes back.  
**Blocked by / blocks / related:** parent: AST-1442

### Description

## What this implements

Every stored LLM call (production task run and Ad Hoc workbench Test) commits assembled prompt segments to agent_data before the provider is called, and writes RESPONSE only after return. Kill or restart mid-call leaves those prompt rows queryable by batch. Does not own UI, timesheets, state transitions, storage-off Ad Hoc, or a new table.

## Citations

`pattern.agent.prompt-persist-before-provider` (proposed), `pattern.batch.entity-agent-responses`, `astral.agent.do-task-delegation`, `astral.batch.entity-agent-responses-latest-only`, `astral.standards.debug-contract-gated`, `astral.layers.core-vs-external-bright-line`.

## Acceptance criteria

- [X] On a stored production task run, agent_data contains the prompt segments for that batch before the provider call is issued — verifiable by reading the batch while a call is in flight, or by killing mid-call and reading afterward.
- [X] On a stored Ad Hoc workbench Test, the same: prompt segments are present even if the call is interrupted and no RESPONSE exists.
- [X] When the provider returns successfully, a RESPONSE row is written with the same success body rules as today.
- [X] When the provider returns a failure, a RESPONSE failure-audit row is written as today.
- [X] After kill or restart mid-call: prompt rows for that batch are present; RESPONSE may be absent; a later successful run writes its own prompt and RESPONSE without corrupting the interrupted batch's prompt rows.
- [X] A storage-off call writes no agent_data rows.
- [X] When debug is on, prompt persist emits per-block found/recorded (index N/M) before the provider call; RESPONSE persist still emits after return. When debug is off, no new debug-contract lines.
- [X] Latest-per-task and agent story still require a RESPONSE — a prompt-only interrupted batch does not become the latest story entry.

## Boundaries

- [X] Does not own UI for prompt-only batches, timesheets, entity state on kill, storage-off Ad Hoc, import agent data (AST-1439), or Ad Hoc seven-segment editors (AST-1403). Does not change block types, compression, content-dedup refs, or entity_id stamping.

## Notes for planning

This child introduces `pattern.agent.prompt-persist-before-provider` once Archie approves the catalog id. One inseparable sequencing invariant across the two stored call sites.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1442-write-to-agent-data-before-calling-the-prompt`,
child `sub/AST-1442/<this-id>-persist-prompt-before-provider`. Created at dispatch-parent.

## QA test manifest

Narrowed `test-child` run (pytest green — not zero-arg harness / branch-lock):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired::test_list_latest_per_task_key \
  -q
```

1. Existing coverage: `TestDoTask` API-failure store; `TestDoTaskStorageFailures` swallow; `TestAst515AdhocWorkbenchLedger` (prompt still stored once); `TestAst984EntityColumnRetired::test_list_latest_per_task_key` (latest-per-task is RESPONSE-gated).
2. Broken/obsolete: none — `_store_prompt_blocks` still once; order moved before the provider await.
3. New: `tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider` — `do_task` prompt-before-`send_to_anthropic` and RESPONSE after; provider raise leaves prompt only; `store_agent_data=False` writes nothing; persist exception still calls provider; later success uses a new `batch_id`; workbench Test same vs `run_adhoc`; bare `run_adhoc` stores nothing; debug found/recorded before await and silent when `debug=False`; prompt-only rows are not `list_entity_latest_agent_refs`.

Bible: `docs/test-bible/core/agent.md` shasum `1d11d592de93c507caa2e29973fd39801472190c` (`git show origin/sub/AST-1442/AST-1448-persist-prompt-before-provider:docs/test-bible/core/agent.md | shasum`).

### Comments

#### radia — 2026-08-19T20:04:50.102Z
[code-rubric] PROCEED (Commit: 3688da45fdc5a2abf4bc097e37e1e022ac51c597) persist-before-provider clean

#### betty — 2026-08-19T16:52:22.042Z
`origin/sub/AST-1442/AST-1448-persist-prompt-before-provider` @ `3688da45` · persist-before-provider tests

#### joan — 2026-08-19T16:37:27.861Z
[plan-rubric] PROCEED (Commit: ecf7bbbe2640a391a61e49ab7a9834f131ea0952) Persist-before-provider plan

#### ada — 2026-08-19T16:32:17.637Z
`origin/sub/AST-1442/AST-1448-persist-prompt-before-provider` @ `ecf7bbbe` · persist-before-provider plan

---

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

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1442/AST-1448-persist-prompt-before-provider`  
**Product commits:** `f94263a3` (Stage 1 — proposed `pattern.agent.prompt-persist-before-provider`), `cb2196fe` (Stage 2 — `do_task` persist before provider), `6b2fafc9` (Stage 3 — workbench persist before `run_adhoc`)

`_store_response_block`, timesheets, `run_adhoc` storage-off, `database.py`, UI, and `BLOCK_TYPES` left untouched.

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

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1448
**Publish ref:** `3688da45fdc5a2abf4bc097e37e1e022ac51c597` (`origin/sub/AST-1442/AST-1448-persist-prompt-before-provider`)
**Overall:** CLEAN

**Diff change set** (`origin/dev...3688da45`): layers `core` + `docs`; change_types `add` + `modify`. AST-1448 product: `src/core/agent.py`, proposed catalog + patterns README/HARVEST, issue doc. Betty: `tests/component/core/test_agent_ast1448.py`, `docs/test-bible/core/agent.md`. Also on three-dot via `test(AST-1450)` + `merge-tests`: `docs/test-bible/frontend/components.md`, `tests/component/frontend/components/test_NavigationShell.test.tsx` — not this child's Files Changed.

**Statutes checked:** Full harvested active set (64 ids). Universal never `not-applicable`. All scoped statutes conform or not-applicable per layer/path miss.

**Pattern conformance:** `pattern.batch.entity-agent-responses` conforms; `pattern.agent.prompt-persist-before-provider` conforms (introduced as `status: proposed`).

**Plan adherence:** Stages 1–3 match issue doc; estimate 3 matches relocate + proposed catalog.

**Findings:** *(none — no fix-now / discuss)*

**advisory:** Three-dot also contains AST-1450 NavigationShell / frontend bible via `test(AST-1450)` + `merge-tests`. Out of AST-1448 Files Changed.

**advisory:** Pre-await persist dropped the old "non-blocking; best-effort" comment — matches plan "verbatim" snippet.

**What's solid:** Call-order only, same kwargs, RESPONSE/timesheets/external untouched, catalog proposed with no runtime id lookup.

## Bug: AST-1842 — agent_data writes off event loop + sqlite lock hardening

- **Linear:** [AST-1842](https://linear.app/astralcareermatch/issue/AST-1842) · mini-parent [AST-1825](https://linear.app/astralcareermatch/issue/AST-1825) (orphaned bug, `select_job_page INTERRUPTED`)
- **Publish ref:** `sub/AST-1825/AST-1842-agent-data-writes-off-event-loop` · parent `ftr/AST-1825-select-job-page-db-lock-loop-stall`
- **Explicit scope:** AST-1842 `## Scope` — `src/core/agent.py` (`do_task`), `src/data/database.py` (`_get_connection`, `_run_with_retry`), `src/utils/config.py` (`db_retry` sibling block), `src/core/roster.py` (`select_job_page` outcome mapping). No Canon Scope listed on AST-1842 or AST-1825 — nothing resolved here; fix-board (Joan) owns the canon verdict.
- **Boundaries (from ticket):** no change to `PROVIDER_CALL_BUDGET` (600s/10s) or `dispatch_timeout_seconds` (3600); no new tables / `agent_data` migration; no dispatcher gather / concurrency rework beyond moving these writes off the loop.

### As-is

AST-1448 (Stage 2 above) moved `_store_prompt_blocks` ahead of the provider await in `do_task`, but every `agent_data` write in `do_task` is still a **synchronous** call on the event loop: one `_store_prompt_blocks(...)` (before `send_to_anthropic` / `send_to_deepseek`) and twelve `_store_response_block(...)` sites (provider-failure audit, envelope / schema / catalog / confidence / grade / rubric-normalize / decode / post-decode failure audits, and the success RESPONSE). Each ends in `save_agent_data` → `_run_with_retry(_with_conn)` → `conn.commit()`. `_get_connection` opens `sqlite3.connect(str(DB_PATH))` with the implicit 5s busy timeout and the default rollback journal. Under a concurrent writer (a parallel batch, a long reader), each failed commit freezes the whole loop for up to 3 × 5s busy wait + `time.sleep` backoff (0.5s, 1s) ≈ 16.5s, then the row is dropped (`_log_swallowed_agent_data` → "Continuing without that agent_data row"). With ~30 companies × several prompt blocks, the loop stalls for minutes, so every in-flight `await_provider_call_with_budget` timer (`asyncio.wait(..., timeout=610)`) fires late and together — Somerset batch `select_job_page-903ff01b-…` logged `Provider call exceeded per-call time budget (600s)` at 999–1565s, ~20 within one second, and the batch hit the 3600s dispatch wall (`INTERRUPTED: 1 error(s) / 30 processed`).

Separately, `_find_job_page_from_assembled` (`src/core/roster.py`) treats any `do_task` failure that is not `provider_balance_refusal` as a verdict: `_save_company(state="NO_JOBLIST", raw_response={"response_type": "SELECT_FAILED", ...})`. A provider-call-budget timeout (`failure_class="provider_call_timeout"`, AST-1189) therefore moves the company `PJL_READY -> NO_JOBLIST` as if the model had answered.

### To-be

- No `agent_data` prompt/RESPONSE write in `do_task` runs on the event loop. A locked or slow commit blocks one worker thread; other companies' provider calls keep running, and a budget timeout reports ≈ 610s (budget + grace), not 1000s+.
- `_get_connection` opens every connection with a config-driven busy timeout and ensures WAL journal mode, so readers no longer lock out writers and concurrent batches wait briefly instead of raising `database is locked`. Prompt/RESPONSE rows stop being dropped in normal operation.
- A `select_job_page` provider-call-budget timeout holds the company at `PJL_READY` (loop-eligible — the next `select_job_page` dispatch retries it) and returns `failure_class="provider_call_timeout"` plus the error, instead of saving `NO_JOBLIST`.
- A healthy `select_job_page` run stores the same prompt + RESPONSE rows and reaches `JOBLIST_IDENTIFIED` / `NO_JOBLIST` / `NO_PJL_SELECTED` exactly as before.

### Repro

Astral persists to sqlite via `src/data/database.py`; all three repros are fixture-level (no production data needed).

1. **Loop freeze (agent.py).** Patch `src.core.agent.save_agent_data` with `lambda **kw: time.sleep(2.0)` and `src.core.agent.send_to_deepseek` with an `AsyncMock` returning a minimal success dict. Run `asyncio.gather(do_task("select_job_page", live_content="x", index="acme_com", ctx={...}, debug=False), heartbeat())` where `heartbeat()` records `loop.time()` every 0.05s for 3s. **As-is:** the largest heartbeat gap ≥ 2.0s (per stored block). **To-be:** largest gap < 0.2s; `save_agent_data` still called with the same kwargs and the same number of times.
2. **Reader locks writer (database.py).** Temp DB file. `conn_r = sqlite3.connect(path)`; `conn_r.execute("BEGIN"); conn_r.execute("SELECT * FROM agent_data").fetchall()` (hold the read transaction open). From a second connection obtained via `_get_connection()`, insert one `agent_data` row and `commit()`. **As-is (rollback journal):** `sqlite3.OperationalError: database is locked` after the 5s busy wait. **To-be (WAL):** commit succeeds immediately; `PRAGMA journal_mode` on the file returns `wal`.
3. **Timeout recorded as verdict (roster.py).** Patch `src.core.roster.do_task` with an `AsyncMock` returning `{"success": False, "error": "Provider call exceeded per-call time budget (600s)", "failure_class": "provider_call_timeout"}`; company fixture `{"short_name": "acme_com", "state": "PJL_READY", "company_data": {<assembled PJL maps>}}`; call `run_select_job_page_dispatch(entity, "b1")`. **As-is:** `_save_company(..., state="NO_JOBLIST")` and return `state == "NO_JOBLIST"`, `response_type == "SELECT_FAILED"`. **To-be:** no `_save_company` call; return `{"state": "PJL_READY", "response_type": "SELECT_FAILED", "error": <message>, "failure_class": "provider_call_timeout", "state_held": True}`; `run_company_task` counts it as `total_errors: 1` and `_warn_company` logs the company name with the error.

### Root cause

1. **Sync I/O inside async `do_task`.** `_store_prompt_blocks` / `_store_response_block` are plain functions that do blocking sqlite commits (with blocking `time.sleep` retries in `_run_with_retry`); `do_task` calls them directly, so any DB wait is an event-loop wait. The per-call budget timer is a loop timer, so it cannot fire during the stall.
2. **Lock-prone connection defaults.** `sqlite3.connect(str(DB_PATH))` — rollback journal (a reader's SHARED lock blocks a writer's commit) and the implicit 5s busy timeout; nothing configures either.
3. **Failure mapping in `_find_job_page_from_assembled`.** The `if not res.get("success")` branch only carves out `is_provider_balance_refusal(res)`; every other failure, including `provider_call_timeout`, falls through to `_save_company(state="NO_JOBLIST")`.

### Proposed change

Execute in order; one `code()` commit per step on the epic worktree, each pushed to `origin/sub/AST-1825/AST-1842-agent-data-writes-off-event-loop`.

**Step 1 — `src/utils/config.py`: `db_connection` block.**
In `ASTRAL_CONFIG`, immediately after the existing `"db_retry": {...},` block, add a sibling block (do not change `db_retry`):

```python
    # sqlite connection settings (AST-1842): busy wait on locked writes + WAL so readers
    # never block a writer's commit. journal_mode is persistent in the db file once set.
    "db_connection": {
        "busy_timeout_seconds": 10.0,
        "journal_mode": "WAL",
    },
```

⚠️ **Decision (value for fix-board / Susan):** `busy_timeout_seconds: 10.0`. Today's implicit value is sqlite3's 5.0. WAL removes the reader-blocks-writer lock (the likely source of today's multi-second locks); remaining contention is writer-vs-writer commits, which are short. 10s doubles headroom while bounding the worst case for DB callers that **stay on the loop** (roster state writes etc. — see Blast radius) at 3 × 10s + 1.5s backoff. Alternatives: 5.0 (no change in on-loop worst case, relies on WAL alone) or 30.0 (more headroom, but an on-loop caller could stall up to ~91s). Value is config-owned, so it is a one-line retune.

**Step 2 — `src/data/database.py`: `_get_connection`.**
Replace the body's connect line so every connection gets the configured busy timeout and ensures the journal mode (config already imported as `ASTRAL_CONFIG` — `_run_with_retry` reads `ASTRAL_CONFIG.get("db_retry", {})`):

```python
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    cfg = ASTRAL_CONFIG.get("db_connection", {}) or {}
    # busy timeout: locked writers wait instead of raising "database is locked" (AST-1842)
    conn = sqlite3.connect(str(DB_PATH), timeout=float(cfg.get("busy_timeout_seconds", 5.0)))
    # WAL is persistent per db file; re-issuing on an already-WAL db is a no-op read
    if cfg.get("journal_mode"):
        conn.execute(f"PRAGMA journal_mode={cfg['journal_mode']}")
    conn.row_factory = sqlite3.Row
    return conn
```

- Do not add a module-level "WAL already set" flag — the PRAGMA is idempotent and cheap on a WAL db; fewer moving parts.
- Do not touch `_run_with_retry` (see Step 4). Do not change any other `sqlite3.connect` in `scripts/**` (out of scope; they open the same file and inherit WAL from the db header).
- `python3 -m py_compile src/data/database.py src/utils/config.py` passes.

⚠️ **Decision:** Issue the PRAGMA on every connection rather than once at startup. The first connection after deploy flips the file to WAL (waiting up to the busy timeout if another connection is mid-write); every later call just reads back `wal`. There is no single startup hook shared by Flask, gunicorn workers, and the dispatcher, so per-connection is the simplest guarantee.

**Step 3 — `src/core/agent.py`: `do_task` writes via `asyncio.to_thread`.**

1. Add `import asyncio` to the stdlib import block at the top of `src/core/agent.py` (alphabetical with the existing `functools` / `inspect` / `sys` imports).
2. In `do_task`, the pre-provider prompt persist (the `if _should_store:` block right after `_assemble_blocks_seven_segment`, before `if provider == "anthropic":`): change **only** the call expression, keeping every kwarg and the `except Exception as exc: _log_swallowed_agent_data(index, task_key, exc)` swallow:

```python
            # Off the loop: a locked DB must not stall other companies' provider timers (AST-1842)
            prompt_blocks = await asyncio.to_thread(
                _store_prompt_blocks,
                entity_type=entity_type,
                task_key=task_key,
                batch_id=batch_id,
                # Same prefix as wire first system block (helper once on unresolved body).
                system_content=_system_text_with_candidate_prefix(system_content, candidate_id),
                caches_resolved_four=(rca or "", rcb or "", rcc or "", rcd or ""),
                nocache_content=nocache_content,
                user_content=user_content,
                live_content=live_content,
                debug=debug,
                entity_id=index if index else None,
            )
```

3. Every `_store_response_block(` call **inside `do_task`** (twelve sites: provider-failure audit; strict-envelope error; pre-decode schema error; pre-decode `resume_section_payload` catalog error; pre-decode confidence error; grade error; rubric-normalize exception; `_decode_payload` exception; post-decode schema error; post-decode catalog error; post-decode confidence error; success RESPONSE `resp_id = ...`) becomes `await asyncio.to_thread(_store_response_block, <same positional args>, <same kwargs>)`. Example (provider-failure audit):

```python
                await asyncio.to_thread(
                    _store_response_block,
                    entity_type, task_key, batch_id, _failure_response_block_data(index, audit_body), index=index,
                    debug=debug)
```

   and the success site:

```python
            resp_id = await asyncio.to_thread(
                _store_response_block, entity_type, task_key, batch_id, store_content, index=index, debug=debug)
```

   Argument expressions (`_failure_response_block_data(...)`, `_audit_response_body(...)`, `_validation_failure_audit_body(...)`, `store_content`) are evaluated on the loop exactly as today; only the `save_agent_data` I/O moves to the thread. Keep each surrounding `if _should_store:` / `try` / `except ...: _log_swallowed_agent_data(...)` unchanged — `asyncio.to_thread` re-raises the worker's exception at the `await`, so the existing swallow still catches it.

4. Do **not** add async wrapper helpers (`_store_*_async`) — `asyncio.to_thread(fn, ...)` at the call site is the whole change, and it resolves `_store_prompt_blocks` / `_store_response_block` from module globals at call time so existing `patch("src.core.agent._store_...")` mocks keep working.
5. Do **not** change `_store_prompt_blocks` / `_store_response_block` bodies, `run_adhoc_workbench_test`'s calls (lines ~3090/3178/3195 — Ad Hoc interactive path, not dispatch), `_capture_rubric_vector_feedback` (`store_feedback_block` / `insert_vector_feedback_rows`), hop ledger / timesheet calls, or the order established by AST-1448 (prompt persist still completes **before** the provider await; RESPONSE still after return).
6. `python3 -m py_compile src/core/agent.py` passes.

⚠️ **Decision:** Use the default executor (`asyncio.to_thread`), as the ticket's Technical scope names, not a dedicated DB `ThreadPoolExecutor`. Provider calls already run in the same default pool (`await_provider_call_with_budget` → `asyncio.to_thread`), so under heavy saturation a DB write can queue behind provider threads — that delays one company's hop but never freezes the loop. A dedicated pool would add a worker-count knob (a new limit) — not added without Susan's say-so; revisit only if the Step 6 re-run shows prompt writes queuing.

⚠️ **Decision:** `asyncio.to_thread` copies the caller's `contextvars` context, so `log_batch_id` and debug buffering seen inside `save_agent_data` / Style D found/recorded are unchanged; debug lines still emit before the provider await (AST-1448 AC7).

**Step 4 — `src/data/database.py`: `_run_with_retry` — verify, no code change.**
After Step 3 every `save_agent_data` reached from `do_task` runs inside the worker thread, so `_run_with_retry`'s `time.sleep` backoff for those writes sleeps the worker, not the loop. No async-aware variant is added: the remaining on-loop DB callers (roster `_save_company` / `transition_company_state` / `get_company`, hop ledger, timesheets) are outside this ticket's "agent_data writes" slice and the Boundary forbids broader rework. Record the check in the build stub (`rg -n "_store_prompt_blocks\(|_store_response_block\(" src/core/agent.py` shows no bare call inside `do_task`).

**Step 5 — `src/core/roster.py`: `_find_job_page_from_assembled` timeout → hold state.**

1. Add `PROVIDER_CALL_BUDGET` to the existing `from src.utils.config import (...)` block in `src/core/roster.py`.
2. In `_find_job_page_from_assembled`, `if not res.get("success"):` branch, widen the existing balance-refusal hold to also cover the AST-1189 timeout class (same return shape, so `run_company_task`'s `result.get("error")` → `_warn_company` + `total_errors: 1` path is reused unchanged):

```python
        if not res.get("success"):  # pragma: no branch
            # Balance refusal (AST-897) and provider-call-budget timeout (AST-1189) are not model
            # verdicts: hold the loop-eligible state so the next select_job_page dispatch retries (AST-1842).
            if is_provider_balance_refusal(res) or res.get("failure_class") == PROVIDER_CALL_BUDGET["failure_class"]:
                current_state = (get_company(short_name) or {}).get("state")
                logger.debug(
                    "Response from agent.do_task: state held failure_class=%r error=%r current_state=%r",
                    res.get("failure_class"), res.get("error"), current_state,
                )
                return {
                    ...  # unchanged dict: short_name, state=current_state, job_site, response_type="SELECT_FAILED",
                         # error, failure_class, state_held=True
                }
```

3. Leave the fall-through `_save_company(state="NO_JOBLIST", ... "SELECT_FAILED" ...)` for every other failure unchanged. Do not change the TRY_LINKS loop, `sel_cfg["retry_state"]`, `run_select_job_page_dispatch`, or `run_company_task`'s `terminal_ok` set.
4. `python3 -m py_compile src/core/roster.py` passes.

⚠️ **Decision:** "Retryable state" = hold `PJL_READY` (the `select_job_page` dispatch trigger), mirroring the AST-897 balance-refusal hold. Rejected: `sel_cfg["retry_state"]` (`PREFILTER_PASSED_RETRY`) — that state means "new try_links merged, re-scrape PJL pages", which would re-run scraping for a pure provider timeout; and a new `retry_of("PJL_READY")` company state — needs a `COMPANY_STATES` / `ROSTER_CONFIG` addition outside the declared config scope. Consequence to note: a company that times out on every attempt is retried on every dispatch (same as balance refusal today); no retry cap is added without Susan's approval.

⚠️ **Decision:** Compare against `PROVIDER_CALL_BUDGET["failure_class"]` inline in roster rather than add an `is_provider_call_timeout` helper to `src/utils/llm_external.py` — that file is not in AST-1842's scope.

**Step 6 — verification (no commit).**
Re-run a 30+ company `select_job_page` batch (parent Proposed step 5) on the test host once the fix lands: budget errors (if any) report ≈ 600–610s, no `database is locked` lines, batch completes under `dispatch_timeout_seconds`. Record the observed numbers in the build stub. This is operator verification for test-fix / UAT, not a make-fix gate.

### Blast radius

- **`do_task` callers** (every production LLM hop: roster, consult, tracker, candidate craft, artifacts). Behavior identical except the store I/O is awaited on a worker thread; call order (prompt → provider → RESPONSE) unchanged.
- **Tests that mock `_store_prompt_blocks` / `_store_response_block` / `save_agent_data`** (`tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider`, `test_agent.py::TestDoTask*`, `TestDoTaskStorageFailures`, `TestAst515AdhocWorkbenchLedger`): mocks are resolved at call time and exceptions re-raise at the `await`, so expectations should hold. Any test asserting the store runs on the *same thread* as the loop, or patching `asyncio.to_thread`, would need Betty.
- **Every `_get_connection` caller** (the whole data layer, incl. `api_admin.py` table browser): busy wait rises from 5s to the configured value; journal mode becomes WAL. On-loop DB callers not moved by this ticket (roster state writes, hop ledger, timesheets, `_capture_rubric_vector_feedback`) still block the loop while they wait — now bounded by the config value.
- **WAL side files.** After the flip, the db directory gains `astral.db-wal` / `astral.db-shm`. `src/ui/api/api_admin.py` `download_db` (`/data/download`) sends only `astral.db`; commits not yet checkpointed (sqlite auto-checkpoints every ~1000 pages) are absent from that download until the next checkpoint. Same for manual `cp data/astral.db` backups (`scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` docstring) and `scripts/sync_from_prod.py` default mode (`download_db()` pulls `/api/admin/data/download`), so a local prod sync can lag the last few un-checkpointed commits. Out of scope here (`src/ui/**`, `scripts/**`); flag for Susan whether to file a follow-up (e.g. `PRAGMA wal_checkpoint(TRUNCATE)` before `send_file`).
- **Railway volume.** WAL needs a local filesystem with shared-memory support (Railway volumes are block storage — fine); it is not safe on network filesystems.
- **`select_job_page` counters.** Timeout companies move from `total_passed` (via `NO_JOBLIST` ∈ `terminal_ok`) to `total_errors`, and the dispatch summary's error count rises accordingly; they stay `PJL_READY` for the next run.
- **AST-1448 / AST-1189 docs.** No change to their contracts: prompt-before-provider sequencing and the 600s + 10s budget / `provider_call_timeout` class are consumed, not modified.

### What must still hold

- **AST-1448 AC1–AC8:** prompt segments committed before the provider call is issued (the `await asyncio.to_thread(_store_prompt_blocks, ...)` completes before `send_to_*` is awaited); RESPONSE success/failure-audit rows written after return with the same bodies; prompt-persist failure never skips the provider call; `store_agent_data=False` writes nothing; debug found/recorded emits before the await and stays quiet with `debug=False`; latest-per-task stays RESPONSE-gated.
- **AST-1189:** `PROVIDER_CALL_BUDGET` values, `await_provider_call_with_budget`, and the `provider_call_timeout` failure class / never-empty error are untouched.
- **AST-897:** balance-refusal hold keeps its exact return shape and state-held behavior.
- **Healthy `select_job_page`:** stores prompt + RESPONSE rows and reaches `JOBLIST_IDENTIFIED` / `NO_JOBLIST` / `NO_PJL_SELECTED` exactly as before; non-timeout `do_task` failures still save `NO_JOBLIST` / `SELECT_FAILED`.
- **Data layer contract:** `save_agent_data` still commits per row and raises to the caller; no new logging in `src/data/`; no new tables, columns, or migrations.
- **Boundaries:** `PROVIDER_CALL_BUDGET`, `dispatch_timeout_seconds`, dispatcher gather/concurrency, and the `select_job_page` prompt unchanged.

## Bug: AST-1842 — Fix board (Joan)

## Fix-board Joan pass — AST-1842

**Ticket:** AST-1842 (orphaned bug under mini-parent AST-1825)  
**Read:** `origin/sub/AST-1825/AST-1842-agent-data-writes-off-event-loop:docs/features/agent/ast-1448-persist-prompt-before-provider.md` § Bug: AST-1842 (As-is / To-be / Repro / Root cause / Proposed change steps 1–6 / Blast radius / What must still hold)  
**Canon Scope:** None on AST-1842 or AST-1825 — overlap triage only (not R1–R7, no `validate-plan` rubric).  
**Roster:** `docs/canon-index.md` is absent on this publish ref, `origin/dev`, and `origin/main` (same resolution as prior fix-board passes: `canon/statutes/README.md` harvested table + `canon/docs/HARVEST-patterns.md` + `canon/docs/DIRECTIVES-DIRECTORY.md` for active `canon/directives/active/*`).

### Plan-fix summary (canon lens)

| Step | Layer | Canon-relevant shape |
|------|--------|----------------------|
| 1–2 | `config` + `data` | New `db_connection` block; `_get_connection` busy timeout + `PRAGMA journal_mode=WAL` |
| 3–4 | `core/agent` | All `do_task` `agent_data` writes via `await asyncio.to_thread(...)`; sequencing unchanged |
| 5 | `core/roster` | `provider_call_timeout` held like balance refusal — no `NO_JOBLIST` transition |
| 6 | ops | Host re-run; not a canon gate |

Boundaries explicitly preserve `PROVIDER_CALL_BUDGET`, `dispatch_timeout_seconds`, and AST-1448 prompt-before-provider ordering.

---

### Overlap review (roster rows that plausibly touch this diff)

**`pattern.agent.prompt-persist-before-provider` (HARVEST — proposed; no `canon/patterns/agent/…` file on this publish ref)**  
- Harvest text: commit prompt segments **before** provider await; RESPONSE after return.  
- Proposed change: `await asyncio.to_thread(_store_prompt_blocks, …)` **completes** before `send_to_*` is awaited; RESPONSE sites still after return.  
- **Judgment:** Conforming to the stated invariant; moving I/O to a worker thread is not a sequencing carve-out. No catalog edit required for F5.

**`astral.batch.entity-agent-responses-latest-only`**  
- RESPONSE tagging / `entity_id` / no entity-row mirrors — unchanged.  
- **Judgment:** No impact.

**`astral.agent.do-task-delegation` / `astral.layers.core-vs-external-bright-line`**  
- Bright line is external HTTP/DOM/API vs core orchestration. `do_task` already persists via `src/data`; this change threads blocking sqlite work, it does not push new external I/O into core.  
- **Judgment:** No conflict.

**`astral.standards.data-raises-caller-logs`**  
- Plan: no new logging in `src/data/`; `_run_with_retry` untouched; core still swallows via `_log_swallowed_agent_data` at the `await`.  
- **Judgment:** Conforming.

**`astral.standards.debug-contract-gated`**  
- Plan explicitly relies on `contextvars` + existing debug paths through `to_thread`; AC7 preserved in What must still hold.  
- **Judgment:** No new ungated debug; no edit.

**`astral.config.config-source-of-truth`**  
- `db_connection` as a sibling block in `ASTRAL_CONFIG` matches “behavior in organized config blocks.”  
- **Judgment:** Conforming.

**`astral.standards.database-header-inventory`**  
- Touches `_get_connection` only; no new tables or header inventory drift.  
- **Judgment:** Conforming.

**`patt.artifact.write-operative` (SQLite concurrency note)**  
- Acknowledges DB boundaries; fix strengthens shared-file behavior (WAL), does not change artifact write contract.  
- **Judgment:** No statute/pattern update required.

**`astral.dispatch.entity-state-bound`**  
- No change to `dispatch_task` registry pairs or claim keys; `select_job_page` still dispatches on real trigger states.  
- **Judgment:** No impact.

**`patt.task.dispatch-retry` (active directive — arc 5)**  
- Arc 5: failures must not “remain in the same state.”  
- **Pre-existing product tension:** AST-897 balance refusal already holds loop-eligible company state without a `_RETRY` transition — same return shape Step 5 copies for `provider_call_timeout`. AST-1842 does not invent hold-without-transition; it stops misclassifying a **timer/infrastructure** failure as a model verdict (`NO_JOBLIST`).  
- Parallels AST-1821 fix-board treatment: arc-5 vs stamp/hold behavior was already at odds with shipped code; this patch aligns timeout with an established hold class, not unbounded `_RETRY` bypass. Plan flags unbounded re-dispatch without a cap as a Susan product call, not a new canon shape.  
- **Judgment:** Worth noting in narrative; **does not require** a canon patch to proceed with F5 (not REVISE solely to record arc-5 exception retroactively for AST-897 + AST-1842).

**AST-896 feature archive (not harvested statute)**  
- Boundaries once said timeouts keep prior transition rules; this fix **changes** timeout routing for `select_job_page`. That is intentional product scope in the plan-fix (root cause #3), documented with ⚠️ decisions — not an in-force statute contradiction.  
- **Judgment:** Not ESCALATE — bounded roster branch, mirrors AST-897 precedent already on ftr lineage; not “new unbounded architectural precedent” at the canon layer.

**WAL / `download_db` / backup lag (Blast radius)**  
- Operational and admin-path honesty issue; no active statute mandates rollback journal or single-file backup completeness. Plan already flags follow-up for Susan.  
- **Judgment:** Out of fix-board canon scope.

**`PROVIDER_CALL_BUDGET` / AST-1189**  
- Explicitly untouched; inline `failure_class` compare only. No corpus entries for budget values on this branch.  
- **Judgment:** No impact.

---

### ESCALATE check

- No ambiguous statute intent that blocks implementation.  
- Blast radius is bounded in the plan (default executor sharing with provider `to_thread`, on-loop DB callers still blocking, WAL ops note).  
- No request for new `COMPANY_STATES`, retry caps, or dedicated DB pool without Susan — those are plan ⚠️ decisions, not missing canon.

---

### Verdict rationale

The proposed change does **not** contradict any active harvested statute or active directive in a way that **requires** landing a canon edit before `make-fix`. Closest pattern tension (`patt.task.dispatch-retry` arc 5) is **pre-existing** relative to AST-897-style holds; AST-1842 extends that hold to the correct failure class rather than introducing a new dispatch-retry story. Prompt-persist sequencing, data logging ownership, config sourcing, and database header inventory all remain aligned.

F3 (`validate-plan` fix mode) is **not** triggered from this board pass.

```text
AST-1842 board-joan done — CANON: OK.
```

```
[board-joan]  CANON: OK
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/28986dcb8aa0b05dd3cbc597098f0878/44f7e36b-5c91-4faf-809b-7693f77d7399/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/fd24db40-ab19-4f51-a863-46b00b2dd549/store.db` |
| Radia | review | `/home/susan/.cursor/chats/28986dcb8aa0b05dd3cbc597098f0878/a0e4c02e-db8d-49a1-8995-7cc0dc8205c1/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1442 (parent) | ftr/AST-1442-write-to-agent-data-before-calling-the-prompt |
| AST-1448 | sub/AST-1442/AST-1448-persist-prompt-before-provider |

**Epic worktree:** `astral-AST-1442/` — one active sub checked out at a time.
