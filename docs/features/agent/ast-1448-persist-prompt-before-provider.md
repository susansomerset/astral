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

## Bug: AST-1842 — Build stub (Ada / make-fix)

**Publish ref:** `origin/sub/AST-1825/AST-1842-agent-data-writes-off-event-loop`

| Step | Commit | Summary |
|------|--------|---------|
| 1 | `49a6eaed` | `ASTRAL_CONFIG["db_connection"]` — `busy_timeout_seconds: 10.0`, `journal_mode: "WAL"` |
| 2 | `48b1ae31` | `_get_connection` — `sqlite3.connect(..., timeout=...)` + `PRAGMA journal_mode` from config |
| 3 | `259ed6be` | `do_task` — 1 prompt + 12 RESPONSE stores via `await asyncio.to_thread(...)`; `import asyncio` |
| 4 | — | Verified: `rg -nP "(?<![\w.])_store_(response_block\|prompt_blocks)\(" src/core/agent.py` → only `run_adhoc_workbench_test` (out of scope); no bare store call left in `do_task`. `_run_with_retry` unchanged |
| 5 | `b198975c` | `_find_job_page_from_assembled` — `provider_call_timeout` joins balance-refusal hold (`PJL_READY`, `state_held`) |
| 6 | — | Host 30+ company re-run not performed here (operator / test-fix / UAT) |

**Sanity (temp DB):** `_get_connection` → `journal_mode=wal`, `busy_timeout=10000`; a write commits in ~0s while another connection holds an open read transaction.

**Touched-area suites (Python 3.14 venv):** `tests/component/core/test_agent.py` + `test_agent_ast1448.py` + `TestAst984…test_list_latest_per_task_key`, `tests/component/core/test_roster.py`, `tests/component/data/**` — failure sets identical before vs after this fix (41 / 50 / 51 failed + 2 collection errors, zero new). Pre-existing reds include `TestAst1448PersistPromptBeforeProvider::test_do_task_debug_emits_prompt_found_recorded_before_provider` (expects a `prompt-found` event), `no such table: company`, and `SURFER_BATCH_CONFIG` import errors — for Betty/test-fix, not product changes here.

## Bug: AST-1842 — Radia review-fix

[code-rubric]

**Ticket:** AST-1842  
**Publish ref:** `b43b7bf9832357371c678f474289ece5b12d50c0` (`origin/sub/AST-1825/AST-1842-agent-data-writes-off-event-loop`)  
**Diff base:** `origin/ftr/AST-1825-select-job-page-db-lock-loop-stall...origin/sub/AST-1825/AST-1842-agent-data-writes-off-event-loop` (5 paths: `src/core/agent.py`, `src/core/roster.py`, `src/data/database.py`, `src/utils/config.py`, plan-fix doc append)  
**Corpus:** `a0bc2f0e5b5810448cf465ebeff84ffb6f1d60b6`  
**Overall:** CLEAN

## Canon scores

Frozen canon list on AST-1842 is **empty** (no `Canon Scope` / directive ids locked at Plan Approved; fix-board Joan: overlap triage only, `CANON: OK`, no `validate-plan` fix-mode rubric). Per `review-child` §5, **no directive rows to score** — roll-up from canon grades is vacuously clean. `docs/canon-index.md` remains absent on publish ref (same resolution path as fix-board: harvested statutes + patterns via `canon_clerk`).

## Column diff vs plan stage

`no plan-stage scores attached` (no Joan `validate-plan` column on this bug; fix-board narrative only).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** N/A — routed to sibling **AST-1843** (Betty `[board-betty] TESTS: REVISE`; repro coverage not in this diff; not a miss on AST-1842).

**## What must still hold** — OK

| Item | Verdict |
|------|---------|
| AST-1448 AC1–AC8 (prompt before provider; RESPONSE after; swallow does not skip provider; `store_agent_data` gate; sequencing) | `await asyncio.to_thread(_store_prompt_blocks, …)` completes before `send_to_*` (agent.py ~2155–2218); RESPONSE stores remain after provider return with same `_should_store` / swallow pattern; no change to `store_agent_data=False` logic. |
| AST-1189 (`PROVIDER_CALL_BUDGET`, budget machinery) | Config block untouched; roster compares `failure_class` to `PROVIDER_CALL_BUDGET["failure_class"]` only. |
| AST-897 balance-refusal hold | Same return dict shape; timeout shares the branch. |
| Healthy `select_job_page` / non-timeout failures → `NO_JOBLIST` | Success path and fall-through `_save_company(… NO_JOBLIST …)` unchanged after the widened hold branch. |
| Data layer contract | `_run_with_retry` unchanged; `save_agent_data` path unchanged aside from caller thread; no new tables/migrations/logging in `src/data/`. |
| Boundaries | No edits to `PROVIDER_CALL_BUDGET` values, `dispatch_timeout_seconds`, dispatcher gather, or prompts. |

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Plan fidelity:** Diff matches plan-fix steps 1–5 (config `db_connection`, `_get_connection` WAL + busy timeout, all `do_task` store sites via `asyncio.to_thread`, roster timeout hold). Step 6 (30+ company host re-run) explicitly operator/UAT — still open per build stub; not a code defect on this tip.
- **Sibling test carry / coverage gap:** Betty flagged missing repro coverage at fix-board; ownership on **AST-1843**, not this publish ref (product-only diff).
- **Blast radius (WAL):** `download_db` / unchecked WAL pages — already documented in plan-fix; no new regression introduced by this diff beyond the accepted WAL flip.
- **Stale ticket Technical scope** mentioned a possible async `_run_with_retry` variant; **plan-fix Step 4** chose verify-only — implementation follows the patch, not the looser intake bullet.

## What's solid

- Surgical footprint: four production modules, aligned with declared scope; no sibling product smuggle.
- Ordering invariant preserved: prompt persist still gates provider await; failure-class hold mirrors AST-897 instead of inventing new roster states.
- Config-driven sqlite settings (`db_connection`) rather than hard-coded PRAGMA/timeouts in `database.py`.

## Notes for Chuckles (post-review branching)

| Gate | Parent shape | Next action |
|------|----------------|-------------|
| **PROCEED** (C7 complete) | Normal mini-parent **AST-1825** (live `ftr`, not orphaned-to-dev) | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** (`resolve-child` skipped). |

Do **not** treat AST-1842 as orphaned merge-to-dev despite plan doc wording “orphaned bug” in the INTERRUPTED sense — spawn prompt confirms live `ftr/AST-1825-select-job-page-db-lock-loop-stall`.

## Recommended actions (downstream only — not performed here)

- Append this artifact to `docs/features/agent/ast-1448-persist-prompt-before-provider.md` § Bug: AST-1842 and `docs()` push on sub branch.
- Post slim upshot via `linear_proxy.py --as radia save-comment`.
- Move **Review Posted** then §3h → **User Testing** if Susan/Chuckles accept CLEAN.
- Track **AST-1843** for Betty repro tests; **AST-1842** does not block on `[bug-repro]` presence.

`context_tokens≈28000`

---

```
[code-rubric] PROCEED (Commit: b43b7bf9832357371c678f474289ece5b12d50c0) Off-loop writes WAL hold
```

## Docs-acceptance (AST-1842)

Repro coverage for the select_job_page timeout hold, the do_task loop-not-blocked store, and the WAL/busy-timeout connection is owned by sibling gap **AST-1843** (orphaned fix-board TESTS: REVISE path). No test() on this tip; lighter test-fix compile/sanity **Tests Passed** @ `b43b7bf9`.

## Bug: AST-1843 — repro coverage for AST-1842 (timeout hold, loop-not-blocked store, WAL connection)

- **Linear:** [AST-1843](https://linear.app/astralcareermatch/issue/AST-1843) · mini-parent [AST-1825](https://linear.app/astralcareermatch/issue/AST-1825) · product fix sibling [AST-1842](https://linear.app/astralcareermatch/issue/AST-1842) (already merged into `ftr/AST-1825-select-job-page-db-lock-loop-stall`)
- **Publish ref:** `sub/AST-1825/AST-1843-repro-coverage`
- **Kind:** test/bible gap child opened by AST-1842 fix-board `[board-betty] TESTS: REVISE` (precedent: AST-1724 gap child of AST-1723). **Betty lands everything below at qa-fix** — test tree and bible are hers; this section is the spec, not code.
- **Explicit scope:** AST-1843 `## Scope` — `tests/component/core/test_roster.py`, `tests/component/core/test_agent.py`, `tests/component/data/test_database.py`, `docs/test-bible/core/roster.md`, `docs/test-bible/core/agent.md`, `docs/test-bible/data/database.md`. No product code (AST-1842 owns `agent.py` / `database.py` / `config.py` / `roster.py`). No coverage beyond the three repros. No Canon Scope on AST-1843 or AST-1825.

### As-is

None of AST-1842's three repros (§ Bug: AST-1842 → Repro 1–3) is covered on `origin/ftr/AST-1825-select-job-page-db-lock-loop-stall`:

- `tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal::test_find_job_page_holds_state` covers only the `provider_balance_refusal` hold in `_find_job_page_from_assembled`; nothing asserts the `provider_call_timeout` hold (`roster.py` is `LOCKED_AT_100` in `scripts/testing/check_per_file_coverage.py`).
- Nothing in `tests/component/core/test_agent.py` (or `test_agent_ast1448.py`) asserts the event loop keeps running while `save_agent_data` blocks inside `do_task`; existing AST-1448 tests stub `_store_*` with instant functions, so they pass whether the store runs on the loop or on a thread.
- `tests/component/data/test_database.py` opens connections via `db._get_connection()` for schema tests but never asserts `journal_mode` or `busy_timeout`.
- Bible pages `docs/test-bible/core/roster.md`, `core/agent.md` (§ AST-1448 · AST-1442), `data/database.md` name no AST-1842 node ids.

### To-be

Three `[bug-repro]` tests, each **red on pre-fix product** (`origin/dev`) and **green on the ftr tip** (AST-1842 merged), plus bible entries naming their node ids:

| # | Node id | Pre-fix (red) | Post-fix (green) |
|---|---------|---------------|------------------|
| 1 | `tests/component/core/test_roster.py::TestAst1842SelectJobPageTimeoutHold::test_find_job_page_provider_call_timeout_holds_pjl_ready` | `_save_company(state="NO_JOBLIST")` called; `out["state"] == "NO_JOBLIST"`, no `state_held` | no save; `PJL_READY`, `state_held`, `failure_class="provider_call_timeout"` |
| 2 | `tests/component/core/test_agent.py::TestAst1842DoTaskStoreOffLoop::test_slow_save_agent_data_does_not_block_loop` | heartbeat max gap ≥ one blocked store (~0.3s) | heartbeat max gap < 0.2s |
| 3 | `tests/component/data/test_database.py::TestAst1842ConnectionWalBusyTimeout::test_get_connection_wal_and_configured_busy_timeout` | `journal_mode == "delete"`, `busy_timeout == 5000` | `journal_mode == "wal"`, `busy_timeout == 10000` (from config) |

### Repro

Evidence this shape discriminates pre/post fix: during AST-1842 test-fix, a throwaway harness (outside `tests/`, not committed) using the same fixtures ran against both trees — roster: pre-fix saved `NO_JOBLIST`, post-fix held `PJL_READY`; agent (1.0s blocking stores): pre-fix max loop gap **1.046s**, post-fix **0.038s**; connection (temp DB): post-fix `journal_mode=wal`, `busy_timeout=10000`. Tests 1–3 below are that harness, tightened.

### Root cause

Coverage gap only: AST-1842 routed its `[bug-repro]` bar to this sibling (fix-board REVISE), so the product fix merged to ftr with lighter test-fix sanity and no committed repro.

### Proposed change

All three tests plus bible edits land in **one** Betty `test(AST-1843): …` commit (or one per file — her call) on `astral-tests`, published to `origin/sub/AST-1825/AST-1843-repro-coverage` only. Use existing module imports/helpers in each file; add no new fixture modules or conftest changes.

**Test 1 — `tests/component/core/test_roster.py`**

Add a new class `TestAst1842SelectJobPageTimeoutHold` **immediately after** `TestAst897HoldStateOnBalanceRefusal` (before `TestAst1155PrefilterIncompleteRetry`). Docstring: `"""AST-1842: provider_call_timeout on select_job_page holds loop-eligible state (no NO_JOBLIST)."""`. One async test, a copy of `TestAst897HoldStateOnBalanceRefusal::test_find_job_page_holds_state` with exactly these differences:

```python
    async def test_find_job_page_provider_call_timeout_holds_pjl_ready(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": False,
                    "error": "Provider call exceeded per-call time budget (600s)",
                    "failure_class": PROVIDER_CALL_BUDGET["failure_class"],
                }
            ),
        )
        saver = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", saver)
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=_company(state="PJL_READY")))
        out = await roster_mod._find_job_page_from_assembled(
            short_name="acme",
            company_website="https://cw",
            assembled_content="asm",
            page_url_map={1: "https://jobs"},
            page_dom_map={},
            visible_map={1: ""},
            nav_links="",
            browser_context=None,
            debug=False,
            ctx=None,
            chain_parse=False,   # select-only dispatch entry, as run_select_job_page_dispatch calls it
            decomposed=True,
        )
        assert out["response_type"] == "SELECT_FAILED"
        assert out["state"] == "PJL_READY"
        assert out["state_held"] is True
        assert out["failure_class"] == PROVIDER_CALL_BUDGET["failure_class"]
        assert out["error"]
        saver.assert_not_called()
```

`PROVIDER_CALL_BUDGET` comes from `src.utils.config` (add to the file's existing config import if absent — do not hard-code `"provider_call_timeout"`).

**Test 2 — `tests/component/core/test_agent.py`**

Append a new class `TestAst1842DoTaskStoreOffLoop` at the end of the file. Docstring: `"""AST-1842: a slow/locked save_agent_data blocks a worker thread, not the event loop."""`. Stub **`save_agent_data`** (the real `_store_prompt_blocks` / `_store_response_block` stay in play, so the test covers the actual call sites AST-1842 changed):

```python
    async def test_slow_save_agent_data_does_not_block_loop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        token = agent_mod.log_batch_id.set("batch-1")
        try:
            monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda _key: _agent_rows())
            block_types: List[str] = []

            def slow_save(**kw: Any) -> None:
                block_types.append(kw["block_type"])
                time.sleep(0.3)   # a locked-DB commit

            monkeypatch.setattr(agent_mod, "save_agent_data", slow_save)
            monkeypatch.setattr(agent_mod, "send_to_anthropic", AsyncMock(return_value={
                "success": True, "parsed_response": {"agent_payload": "0|CRA2"},
                "api_response": _api_response("ok"), "timesheet": {},
            }))
            ticks: List[float] = []
            done = asyncio.Event()

            async def heartbeat() -> None:
                while not done.is_set():
                    ticks.append(time.monotonic())
                    await asyncio.sleep(0.02)

            async def run() -> None:
                try:
                    await asyncio.sleep(0.1)   # heartbeat ticks first, so a freeze shows as a gap
                    await agent_mod.do_task("evaluate_jd", index="job-1", ctx=_draft_job_resume_ctx())
                finally:
                    done.set()

            await asyncio.gather(run(), heartbeat())
        finally:
            agent_mod.log_batch_id.reset(token)
        assert "SYSTEM" in block_types and "RESPONSE" in block_types   # prompt + RESPONSE stores both ran
        assert max(b - a for a, b in zip(ticks, ticks[1:])) < 0.2
```

- `_agent_rows`, `_api_response`, `_draft_job_resume_ctx` are this module's existing helpers (already imported by `test_agent_ast1448.py` from here). Add `asyncio` / `time` / `AsyncMock` imports only if the module lacks them.
- **Do not assert `out["success"]`.** In the AST-1842 harness this exact setup returned `success=False` from a downstream decode check (`agent_payload must be the newline-separated encoded string…`); that path still runs the prompt store and the failure-audit RESPONSE store, which is all the repro needs. The `block_types` assertion proves both store kinds ran.

⚠️ **Decision (timing values for Betty to confirm):** 0.3s per blocked save, 0.02s heartbeat, pass bar max gap < 0.2s. Pre-fix, every save is a ≥0.3s gap (red with margin); post-fix the harness measured ~0.04s (green with ~5× margin). Total runtime ≈ number of saves × 0.3s (~2–3s). If CI jitter bites, widen the per-save sleep, not the bar.

**Test 3 — `tests/component/data/test_database.py`**

Append a new class `TestAst1842ConnectionWalBusyTimeout`. Docstring: `"""AST-1842: _get_connection opens WAL with the configured busy timeout."""`. Point `DB_PATH` at a temp file so the shared `data/astral.db` is not the one flipped/asserted:

```python
    def test_get_connection_wal_and_configured_busy_timeout(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        from src.data import database as db
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setattr(db, "DB_PATH", tmp_path / "astral.db")
        cfg = ASTRAL_CONFIG["db_connection"]
        conn = db._get_connection()
        try:
            assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == cfg["journal_mode"].lower()
            assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == int(float(cfg["busy_timeout_seconds"]) * 1000)
        finally:
            conn.close()
```

- Pre-fix, `ASTRAL_CONFIG["db_connection"]` does not exist, so the test is red on `KeyError` before the PRAGMA asserts — acceptable as the pre-fix red (the fix is exactly "add this config + apply it"). If Betty prefers a pre-fix red on the PRAGMA values themselves, assert literals `"wal"` / `10000` instead; either reads config the product owns.
- Add `pytest` / `Path` imports only if absent (the module currently imports `sqlite3` only).

**Bible edits** (same commit(s)):

1. `docs/test-bible/core/roster.md` — new section `### AST-1842 · AST-1825 (select_job_page provider_call_timeout hold)`, with "Test/bible delivery on gap sibling **AST-1843**", a one-line behavior summary (timeout joins the AST-897 balance-refusal hold in `_find_job_page_from_assembled`; `PJL_READY` held, no `NO_JOBLIST`), a table row `| Timeout hold | src/core/roster.py (_find_job_page_from_assembled) | tests/component/core/test_roster.py::TestAst1842SelectJobPageTimeoutHold::test_find_job_page_provider_call_timeout_holds_pjl_ready |`, and a regression row pointing at `TestAst897HoldStateOnBalanceRefusal::test_find_job_page_holds_state`. roster.md has no existing AST-897 section to nest under (checked: no `897` / `balance` hits), so this is a new section.
2. `docs/test-bible/core/agent.md` — inside the existing `### AST-1448 · AST-1442 (persist prompt before provider)` section, add a table row `| Store off the event loop (AST-1842 / AST-1843) | src/core/agent.py (do_task → asyncio.to_thread) | tests/component/core/test_agent.py::TestAst1842DoTaskStoreOffLoop::test_slow_save_agent_data_does_not_block_loop |` and append that node id to the section's `run_component_tests.sh` block.
3. `docs/test-bible/data/database.md` — new section `### AST-1842 · AST-1825` (after `### AST-1821 · AST-1820`), "Test/bible delivery on gap sibling **AST-1843**", summary (`_get_connection` applies `ASTRAL_CONFIG["db_connection"]`: busy timeout + WAL), row `| Connection WAL + busy timeout | src/data/database.py (_get_connection), src/utils/config.py (db_connection) | tests/component/data/test_database.py::TestAst1842ConnectionWalBusyTimeout::test_get_connection_wal_and_configured_busy_timeout |`, plus a run block.

**Manifest for qa-fix / test-fix (narrowed):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst1842SelectJobPageTimeoutHold \
  tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_agent.py::TestAst1842DoTaskStoreOffLoop \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider \
  tests/component/data/test_database.py::TestAst1842ConnectionWalBusyTimeout \
  -q
```

Red check: the three `TestAst1842*` node ids against `origin/dev` product (pre-AST-1842) must fail; against the ftr tip they must pass.

### Blast radius

- **Test tree only** — three appended classes, three bible edits. No product file, no conftest, no fixture module.
- **Test 3 flips its temp DB to WAL** — isolated via `monkeypatch.setattr(db, "DB_PATH", tmp_path / …)`; the shared `data/astral.db` other tests use is untouched by this test (it already flips via ordinary `_get_connection` use on the ftr tip — expected, AST-1842 behavior).
- **Test 2 is timing-based** — ~2–3s added runtime; jitter margin per the Decision above.
- **Pre-existing reds on this suite** (unchanged by this ticket, recorded in § Bug: AST-1842 build stub): `test_agent.py` 41 / `test_roster.py` 50 / `tests/component/data/**` 51 + 2 collection errors in the local Python 3.14 venv, including `TestAst1448PersistPromptBeforeProvider::test_do_task_debug_emits_prompt_found_recorded_before_provider`. The manifest's AST-1448 class carries those 3 known reds; qa-fix should judge "green" on the new `TestAst1842*` nodes + no new reds, or fix those separately (out of this ticket's scope).
- **`LOCKED_AT_100`** (`agent.py`, `roster.py`, `config.py`): the new tests only add hits; nothing is removed.

### What must still hold

- AST-1843 AC: each repro red on `origin/dev`, green on ftr; bible names the node ids; no existing test weakened or deleted (`TestAst897HoldStateOnBalanceRefusal` and `TestAst1448PersistPromptBeforeProvider` unchanged).
- AST-1842's contract as merged: prompt persist completes before the provider await; timeout hold returns the AST-897 shape; `db_connection` config drives `_get_connection`. Tests assert that contract; they do not re-specify it.
- No product code on this publish ref (engineer and Betty hooks both enforce; plan-fix doc edit is the only engineer commit here).

## Bug: AST-1843 — Fix board (Joan)

## Fix-board Joan pass — AST-1843

**Ticket:** AST-1843 (test/bible gap sibling of AST-1842; mini-parent AST-1825)  
**Read:** `origin/sub/AST-1825/AST-1843-repro-coverage:docs/features/agent/ast-1448-persist-prompt-before-provider.md` § Bug: AST-1843 (As-is / To-be / Repro / Root cause / Proposed change / Blast radius / What must still hold)  
**Canon Scope:** None on AST-1843 or AST-1825 — roster overlap triage only (not R1–R7).  
**Roster:** No `docs/canon-index.md` on publish ref (same resolution as AST-1842 / prior fix-board passes: `canon/statutes/README.md`, `canon/docs/HARVEST-patterns.md`, active `canon/directives/active/*`).

### Plan-fix summary (canon lens)

| Deliverable | Paths | Product? |
|-------------|--------|----------|
| Three `[bug-repro]` tests | `test_roster.py`, `test_agent.py`, `test_database.py` | No |
| Bible nodes + manifest rows | `docs/test-bible/core/roster.md`, `core/agent.md`, `data/database.md` | No |

Root cause is **coverage gap only** (AST-1842 fix-board Betty `TESTS: REVISE` → gap child, same lane shape as AST-1822 / AST-1767 / AST-1743). Betty lands at `qa-fix` on `astral-tests`; explicit scope forbids product files.

**Behaviors under test** (already merged on ftr via AST-1842; Joan **CANON: OK** on product fix):

1. `provider_call_timeout` on `select_job_page` holds `PJL_READY` (AST-897-shaped hold, no `NO_JOBLIST`).
2. Slow `save_agent_data` during `do_task` does not freeze the event loop (`asyncio.to_thread` at store call sites).
3. `_get_connection` applies `ASTRAL_CONFIG["db_connection"]` (WAL + configured busy timeout).

Tests **pin** that contract; they do not redefine product law or edit `canon/**`.

---

### Overlap review

**`orch.roles.betty-owns-test-tree` / `astral.git.engineer-test-tree-ban` / `astral.git.betty-no-src-or-features`**  
- Proposed change is exactly Betty-owned paths; no `src/` or `docs/features/` product commits on this ref.  
- **Judgment:** Conforming workflow; no canon impact.

**`astral.standards.names-not-ticket-ids`**  
- `applies_when` is `src/**` and `scripts/**` only. `TestAst1842*` / bible headings citing AST-1842 are test-bible convention (parallel `TestAst897`, `TestAst1448`, bible `### AST-…` sections).  
- **Judgment:** Out of scope for this statute; no REVISE.

**`pattern.agent.prompt-persist-before-provider` (HARVEST proposed)**  
- Test 2 exercises prompt + RESPONSE stores with blocking I/O off the loop while preserving call order; does not weaken AST-1448 manifest tests in the narrowed manifest.  
- **Judgment:** Documents behavior Joan already treated as conforming on AST-1842; no catalog edit.

**`patt.task.dispatch-retry` (arc 5)**  
- Test 1 asserts timeout **hold**, not “failure stays in state” as a new dispatch-retry rule. Product precedent (AST-897 hold) was already accepted on AST-1842 board pass; tests mirror shipped ftr behavior.  
- **Judgment:** Pre-existing arc-5 tension vs holds is not **introduced** by this test-only ticket; no F3 trigger.

**`astral.config.config-source-of-truth`**  
- Test 1 imports `PROVIDER_CALL_BUDGET["failure_class"]` (plan forbids hard-coding `"provider_call_timeout"`). Test 3 reads `ASTRAL_CONFIG["db_connection"]` — asserts product config ownership, does not scatter literals in `src/`.  
- **Judgment:** Conforming test style; no statute change.

**`astral.standards.data-raises-caller-logs` / `astral.standards.debug-contract-gated`**  
- No `src/data` or debug-contract product edits; tests stub/measure only.  
- **Judgment:** No impact.

**`astral.standards.database-header-inventory`**  
- Test 3 uses temp `DB_PATH`; no new tables or header drift.  
- **Judgment:** No impact.

**`orch.roles.archie-approves-statutes`**  
- Plan does not touch `canon/statutes`, `canon/patterns`, or active directives.  
- **Judgment:** N/A.

**Blast radius (canon)**  
- Timing-based test (~2–3s), isolated WAL temp DB, pre-existing suite reds called out — operational/test-tree concerns for Betty, not corpus updates.  
- Bible prose describes **where** tests live; that is not directive authoring.

---

### ESCALATE check

- No new architectural precedent beyond AST-1842 (already board-cleared).  
- No ambiguous statute blocking Betty’s three repros + bible rows.  
- Bounded scope: three classes, three bible sections, no conftest/product.

---

### Verdict rationale

AST-1843 is a **test/bible gap** child. The proposed patch does not modify, contradict, or require carving exceptions in any active statute or pattern. It encodes the AST-1842 product contract Joan already rated **CANON: OK**. Precedent: gap siblings such as AST-1767 (`test/bible gap only; no product or active canon impact`).

F3 (`validate-plan` fix mode) is **not** triggered from this board pass.

```text
AST-1843 board-joan done — CANON: OK.
```

```
[board-joan]  CANON: OK
```

## Bug: AST-1843 — Build stub (Ada / make-fix)

**Publish ref:** `origin/sub/AST-1825/AST-1843-repro-coverage` · synced tip `870e2a0f` (`merge-tests(AST-1843): origin/tests 7c40f2c4`)

**Product absorbed from ftr, no product edits here.** AST-1842's four product commits reached this sub through `origin/ftr/AST-1825-select-job-page-db-lock-loop-stall`. `git diff --stat origin/ftr/AST-1825-select-job-page-db-lock-loop-stall HEAD -- src` is empty, so this sub carries no product delta of its own. Present on tip: `do_task` stores via `asyncio.to_thread` (12 RESPONSE + 1 prompt), `ASTRAL_CONFIG["db_connection"]` + `_get_connection` WAL/busy timeout, and the roster `PROVIDER_CALL_BUDGET["failure_class"]` hold.

**`[bug-repro]` gate (Betty `7c40f2c4`):**

| Node id | Tip `870e2a0f` | Pre-fix product (`31846c28` src swapped in) |
|---------|----------------|---------------------------------------------|
| `tests/component/core/test_roster.py::TestAst1842SelectJobPageTimeoutHold::test_find_job_page_provider_call_timeout_holds_pjl_ready` | PASSED | FAILED |
| `tests/component/core/test_agent.py::TestAst1842DoTaskStoreOffLoop::test_slow_save_agent_data_does_not_block_loop` | PASSED | FAILED |
| `tests/component/data/test_database.py::TestAst1842ConnectionWalBusyTimeout::test_get_connection_wal_and_configured_busy_timeout` | PASSED | FAILED |

**Regression classes from the manifest:** `TestAst897HoldStateOnBalanceRefusal` all green. `TestAst1448PersistPromptBeforeProvider` 14 passed / 3 failed, and all 3 failures are the known pre-existing reds recorded in § Bug: AST-1842 build stub (`…debug_emits_prompt_found…`, `…prompt_only_batch_is_not_latest_ref…`, `…bare_run_adhoc…`). Nothing new.

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
