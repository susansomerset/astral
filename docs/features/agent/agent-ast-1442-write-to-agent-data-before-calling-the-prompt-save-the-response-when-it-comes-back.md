# AST-1442 — write to agent_data BEFORE calling the prompt, save the response when it comes back.

**Component:** agent  
**Children:** AST-1448  
**Linear archived:** AST-1442 2026-09-09; AST-1448 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-19 09:31 | AST-1448 | docs | `ecf7bbbe2` | plan — persist prompt before provider |
| 2026-08-19 09:37 | AST-1448 | docs | `a5bcf0b9a` | Joan validate — persist-before-provider plan approved |
| 2026-08-19 09:40 | AST-1448 | code | `6b2fafc9f` | persist workbench prompt before provider |
| 2026-08-19 09:40 | AST-1448 | code | `cb2196fef` | persist do_task prompt before provider |
| 2026-08-19 09:40 | AST-1448 | code | `f94263a3c` | propose persist-before-provider pattern |
| 2026-08-19 09:41 | AST-1448 | docs | `d5f4bc7a9` | build review stub |
| 2026-08-19 09:51 | AST-1448 | merge-tests | `3688da45f` | origin/tests 6784989aa10c1618c94f139e169311b535fff0fa |
| 2026-08-19 09:51 | AST-1448 | test | `6784989aa` | persist prompt before provider |
| 2026-08-19 09:53 | AST-1442 | sync | `992e295d4` | origin/sub/AST-1442/AST-1448-persist-prompt-before-provider |
| 2026-08-19 09:53 | AST-1448 | sync | `992e295d4` | origin/sub/AST-1442/AST-1448-persist-prompt-before-provider |
| 2026-08-19 13:04 | AST-1448 | docs | `c84cec246` | Radia review — clean |
| 2026-08-19 13:05 | AST-1448 | docs | `bacb1a9b9` | dedupe Radia review section |
| 2026-08-19 13:06 | AST-1442 | merge | `e35807476` | Merge remote-tracking branch 'origin/dev' into tmp-refresh-AST-1 |
| 2026-08-25 21:40 | AST-1442 | docs | `98c4ba2a3` | mirror epic registry Threads |
| 2026-09-09 17:54 | AST-1448 | docs | `a06c89f36` | archive Linear issue content |
| 2026-09-09 18:05 | AST-1442 | docs | `84f2f383f` | archive Linear issue content |

## Epic — AST-1442

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1442/write-to-agent-data-before-calling-the-prompt-save-the-response-when · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: Medium / 3_

### Purpose

When a job is killed or the server restarts during a provider call, Astral has no durable record of the prompt that was actually sent. Prompt segments are written to agent_data only after the call returns, so an interrupted run leaves a hole. This epic makes the sent prompt recoverable: commit assembled prompt segments before the provider is called, then save the response when it comes back.

### Functional scope

* For every stored LLM call (production task runs and Ad Hoc workbench Test), assembled prompt segments are committed to agent_data before the provider is invoked.
* The RESPONSE block is written only after the provider returns — success payload or failure-audit body, same outcomes as today.
* After a kill or process restart during the call, those prompt rows remain queryable by batch even when no RESPONSE row exists.
* Storage-off paths stay storage-off: a call that is not supposed to write agent_data still does not.
* When debug is on, the pre-call persist logs what was found and what was recorded per stored prompt block (index N/M, identifier, outcome) before the provider call; RESPONSE persist still logs after return. Long payloads follow the backend debug contract (first 15 / omitted / last 15). Quiet when debug is off.

### Architectural definition

**Patterns to reuse**

* `pattern.batch.entity-agent-responses` — latest-per-task refs stay RESPONSE-gated; prompt-only interrupted rows are audit state, not a new latest index.
* `pattern.layers.import-discipline` — persist stays in core orchestration; external still owns provider I/O; data still owns the write.
* `pattern.batch.entity-claim-process-release` — `batch_id` remains the golden ticket tying prompt rows, RESPONSE, ledger, and timesheets.

**New patterns proposed**

* `pattern.agent.prompt-persist-before-provider` — when agent_data storage is on, commit assembled prompt segments before the external provider call; commit RESPONSE after the call returns. Prompt writes must be durable before the await. A failed prompt write does not abort the provider call (best-effort, same as today). Archie approval required before implementation depends on the catalog id.

**Applicable statutes**

* `astral.agent.do-task-delegation` — core still delegates AI through the existing task entry; this epic reorders persist vs I/O inside that orchestration and does not let callers talk to the provider.
* `astral.batch.entity-agent-responses-latest-only` — RESPONSE still tagged with entity_id when known; list API still RESPONSE-only.
* `astral.layers.core-vs-external-bright-line` — provider I/O stays in external; persist stays in core.
* `astral.layers.import-direction` — no new cross-layer imports.
* `astral.standards.debug-contract-gated` — found/recorded only when debug is on; no data-layer debug noise.
* `astral.standards.data-raises-caller-logs` — data raises; core decides what to log.
* `astral.standards.in-scope-only` — sequencing + durability of existing agent_data writes only.
* `astral.standards.database-header-inventory` — no new tables; existing agent_data only.
* `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — reuse existing persist helpers; do not fork a second store path.
* `astral.standards.no-hardcoded-sets` — `BLOCK_TYPES` unchanged.
* `astral.standards.logging-via-utils` — debug via the shared logger helpers.
* `astral.standards.no-cross-contamination`
* `astral.batch.batch-id-first` — prompt and RESPONSE rows still keyed by the existing batch id.
* `astral.config.config-source-of-truth` — block types and entity types stay in config.

### Boundaries

* Does not add UI for prompt-only (in-flight or killed) batches. Agent story and latest-per-task stay RESPONSE-gated.
* Does not change block types, compression, content-dedup refs, or entity_id stamping on prompt and RESPONSE rows (AST-1423 / AST-1429 / AST-1431).
* Does not persist on bare Ad Hoc runs that are defined as storage-off.
* Does not write timesheets before the provider returns.
* Does not make prompt persist a hard gate: a failed prompt write still does not abort the provider call.
* Does not change entity state-machine behavior on kill (existing claim/release and balance-refusal hold rules stay as they are).
* Does not import agent data (AST-1439) or change Ad Hoc seven-segment editors (AST-1403).

### Acceptance criteria

* On a stored production task run, agent_data contains the prompt segments for that batch before the provider call is issued — verifiable by reading the batch while a call is in flight, or by killing mid-call and reading afterward.
* On a stored Ad Hoc workbench Test, the same: prompt segments are present even if the call is interrupted and no RESPONSE exists.
* When the provider returns successfully, a RESPONSE row is written with the same success body rules as today.
* When the provider returns a failure, a RESPONSE failure-audit row is written as today.
* After kill or restart mid-call: prompt rows for that batch are present; RESPONSE may be absent; a later successful run writes its own prompt and RESPONSE without corrupting the interrupted batch's prompt rows.
* A storage-off call writes no agent_data rows.
* When debug is on, prompt persist emits per-block found/recorded (index N/M) before the provider call; RESPONSE persist still emits after return. When debug is off, no new debug-contract lines.
* Latest-per-task and agent story still require a RESPONSE — a prompt-only interrupted batch does not become the latest story entry.

### Dependencies and blockers

none.

Adjacent in flight on the same persist surface: AST-1423 / AST-1429 / AST-1431 (entity_id on prompt rows, User Testing) and AST-1403 (Ad Hoc seven-segment, User Testing). This epic must preserve prompt-row entity_id stamps and seven-segment persist; it is not blocked by them.

### Open questions

none

### Proposed child tickets


##### 1: **Persist prompt before provider - Ada**

Every stored LLM call (production task run and Ad Hoc workbench Test) commits assembled prompt segments to agent_data before the provider is called, and writes RESPONSE only after return. Kill or restart mid-call leaves those prompt rows queryable by batch. Does not own UI, timesheets, state transitions, storage-off Ad Hoc, or a new table.
**Citations:** `pattern.agent.prompt-persist-before-provider` (proposed), `pattern.batch.entity-agent-responses`, `astral.agent.do-task-delegation`, `astral.batch.entity-agent-responses-latest-only`, `astral.standards.debug-contract-gated`, `astral.layers.core-vs-external-bright-line`.
**Estimate: 3**

**Monolith check:** Functional scope has five capabilities; one child is intentional — one inseparable sequencing invariant across the two stored call sites, which share persist helpers in one orchestration module. Splitting would collide on the same surface and leave kill-during-call UAT incomplete.

**New patterns:** this child introduces `pattern.agent.prompt-persist-before-provider` once Archie approves the catalog id.

---

### Original brief

Prompt data is only saved to agent data when the prompt returns, no way to know what was actually sent if we kill a job or the server restarts.

#### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1448 — Persist prompt before provider

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1448/persist-prompt-before-provider-write-to-agent-data-before-calling-the · Status at archive: Archive · Project: Astral Agent · Assignee: ada · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1442_

#### What this implements

Every stored LLM call (production task run and Ad Hoc workbench Test) commits assembled prompt segments to agent_data before the provider is called, and writes RESPONSE only after return. Kill or restart mid-call leaves those prompt rows queryable by batch. Does not own UI, timesheets, state transitions, storage-off Ad Hoc, or a new table.

#### Citations

`pattern.agent.prompt-persist-before-provider` (proposed), `pattern.batch.entity-agent-responses`, `astral.agent.do-task-delegation`, `astral.batch.entity-agent-responses-latest-only`, `astral.standards.debug-contract-gated`, `astral.layers.core-vs-external-bright-line`.

#### Acceptance criteria

- [X] On a stored production task run, agent_data contains the prompt segments for that batch before the provider call is issued — verifiable by reading the batch while a call is in flight, or by killing mid-call and reading afterward.
- [X] On a stored Ad Hoc workbench Test, the same: prompt segments are present even if the call is interrupted and no RESPONSE exists.
- [X] When the provider returns successfully, a RESPONSE row is written with the same success body rules as today.
- [X] When the provider returns a failure, a RESPONSE failure-audit row is written as today.
- [X] After kill or restart mid-call: prompt rows for that batch are present; RESPONSE may be absent; a later successful run writes its own prompt and RESPONSE without corrupting the interrupted batch's prompt rows.
- [X] A storage-off call writes no agent_data rows.
- [X] When debug is on, prompt persist emits per-block found/recorded (index N/M) before the provider call; RESPONSE persist still emits after return. When debug is off, no new debug-contract lines.
- [X] Latest-per-task and agent story still require a RESPONSE — a prompt-only interrupted batch does not become the latest story entry.

#### Boundaries

- [X] Does not own UI for prompt-only batches, timesheets, entity state on kill, storage-off Ad Hoc, import agent data (AST-1439), or Ad Hoc seven-segment editors (AST-1403). Does not change block types, compression, content-dedup refs, or entity_id stamping.

#### Notes for planning

This child introduces `pattern.agent.prompt-persist-before-provider` once Archie approves the catalog id. One inseparable sequencing invariant across the two stored call sites.

#### QA test manifest

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

##### Comments


###### radia — 2026-08-19T20:04:50.102Z

[code-rubric] PROCEED (Commit: 3688da45fdc5a2abf4bc097e37e1e022ac51c597) persist-before-provider clean

###### betty — 2026-08-19T16:52:22.042Z

`origin/sub/AST-1442/AST-1448-persist-prompt-before-provider` @ `3688da45` · persist-before-provider tests

###### joan — 2026-08-19T16:37:27.861Z

[plan-rubric] PROCEED (Commit: ecf7bbbe2640a391a61e49ab7a9834f131ea0952) Persist-before-provider plan

###### ada — 2026-08-19T16:32:17.637Z

`origin/sub/AST-1442/AST-1448-persist-prompt-before-provider` @ `ecf7bbbe` · persist-before-provider plan

---

#### Stage 1: Propose the persist-before-provider catalog entry

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

#### Stage 2: `do_task` — prompt persist before provider await

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

#### Stage 3: Workbench Test — prompt persist before `run_adhoc`

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

#### Execution contract

- Execute stages in order. One commit per stage on this epic worktree, then `git push origin HEAD:sub/AST-1442/AST-1448-persist-prompt-before-provider`.
- Do not add files, config blocks, tables, routes, or UI not listed above.
- Do not edit `tests/` or the bible. Existing component tests that assert `_store_prompt_blocks` was called once after a mocked provider **returns** still hold (call still happens once). Betty owns any new in-flight / kill-mid-call order assertion.
- If a referenced helper signature has drifted, stop and comment on **AST-1442** with the Stage N blocked template — do not improvise.

#### Pattern / statute map (this ticket)

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

#### Estimate

Confirm Chuckles estimate: 3 — agree

#### Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1442/AST-1448-persist-prompt-before-provider`
**Product commits:** `f94263a3` (Stage 1 — proposed `pattern.agent.prompt-persist-before-provider`), `cb2196fe` (Stage 2 — `do_task` persist before provider), `6b2fafc9` (Stage 3 — workbench persist before `run_adhoc`)

`_store_response_block`, timesheets, `run_adhoc` storage-off, `database.py`, UI, and `BLOCK_TYPES` left untouched.

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1448
**Overall:** APPROVED
**Commit:** `ecf7bbbe2640a391a61e49ab7a9834f131ea0952` (`origin/sub/AST-1442/AST-1448-persist-prompt-before-provider`)

#### Traceability

AC1 production persist-before-call → S2; AC2 workbench Test same → S3; AC3–4 RESPONSE success/failure after return → S2–S3 (do not move `_store_response_block`); AC5 kill/restart prompt-only + later run on a new `batch_id` → S2–S3 relocate-only; AC6 storage-off → S2 `_should_store` / S3 no persist in `run_adhoc`; AC7 debug found/recorded before await, RESPONSE after, quiet when off → S2; AC8 latest-per-task stays RESPONSE-gated → S2–S3 (no `list_entity_latest_agent_refs` edit); S1 → parent New patterns proposed (`pattern.agent.prompt-persist-before-provider` as `status: proposed`, no runtime id lookup).

**Findings**

- **acceptable** — Stage 1 README: insert-after `pattern.ui.in-place-live-refresh` is stale; current last `proposed` row is `pattern.dispatch.run-next-chain-authority`. Engineer should bump the harvested-corpus proposed count to four and add the new row with the other proposed entries; not a definition miss.
- No `fix-now`. No R3 `violates`. R5 maps. R6: files stay `core` + `canon/patterns`; no new tables/config/`ui`; reuse `_store_prompt_blocks`; `save_agent_data` already `conn.commit()`s per row; AUTHORING “must not depend on unapproved id” is honored (catalog file only). Cited reuse patterns resolve `status: approved`. Parent AC and this child’s AC match.

R1–R4 executed in-session (universal set scored; scoped exclusions are layer/path misses: `data`/`ui`/`utils`/`scripts`/`tests`/`docs/features/**`/seed-admin paths). Slim R7: statute table not appended.

context_tokens≈48000

#### Radia review

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

#### Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

##### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1442 (parent) | ftr/AST-1442-write-to-agent-data-before-calling-the-prompt |
| AST-1448 | sub/AST-1442/AST-1448-persist-prompt-before-provider |

**Epic worktree:** `astral-AST-1442/` — one active sub checked out at a time.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `canon/patterns/agent/pattern.agent.prompt-persist-before-provider.md` | New proposed catalog entry | `f94263a3c` |
| ✓ | `canon/patterns/README.md` | Add the new row; bump proposed count | `f94263a3c` |
| ✓ | `canon/patterns/HARVEST.md` | Add supporting-package + crosswalk rows | `f94263a3c` |
| ✓ | `src/core/agent.py` | Persist prompt segments before provider at both stored call  | `6b2fafc9f` `cb2196fef` |
| | _tests_ | — | 1 file(s) |
