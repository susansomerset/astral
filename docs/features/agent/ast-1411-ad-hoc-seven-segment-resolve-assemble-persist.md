# AST-1411 — Ad Hoc seven-segment resolve, assemble, persist

- **Linear:** [AST-1411](https://linear.app/astralcareermatch/issue/AST-1411)
- **Parent:** [AST-1403](https://linear.app/astralcareermatch/issue/AST-1403)
- **Publish ref:** `sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist`

Workbench Preview and Test still resolve, assemble, and store the old three-slot layout (one cache blob → slot A). Production `do_task` already token-resolves seven segments, sends Cache A–D as separate cached API blocks (empty omitted), and writes `CACHE_A`–`CACHE_D` `agent_data` rows via `_assemble_blocks_seven_segment` / `_store_prompt_blocks(..., caches_resolved_four=...)`. This ticket wires the Ad Hoc backend onto those same helpers so a Test with System + Cache A + Cache C + User persists those blocks (no empty B/D rows), Preview/Test empty System still sends the selected agent’s content, and the Test JSON carries `batch_id` so sibling #3 can load `GET /api/agent_data/<batch_id>`. Save As PUT already has the seven columns — do not add agent-content fallback there.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | `_resolve_adhoc` token-resolves all seven body segments; Preview JSON adds `cache_a`–`cache_d`; Test passes four caches into the workbench wrapper and returns `batch_id` | ui |
| `src/core/agent.py` | `run_adhoc` / `run_adhoc_workbench_test` assemble and store four cache slots; workbench result includes `batch_id`; `_store_prompt_blocks` Style D found→recorded per stored prompt block when `debug=True` | core |

Do **not** edit: `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` (sibling #2 / #3), preview modal / agent_data pane chrome (sibling #3), `PUT /api/admin/tasks/<task_key>` / `save_agent_task` (Save As columns already exist), `do_task` assembly / `run_next` / Manage Tasks preview (`preview_prompt`), `_caller_response_blob` / the AST-1393 stringify block inside `run_adhoc_workbench_test`, `src/utils/config.py` (`BLOCK_TYPES` already lists `CACHE_A`–`D`), `src/data/database.py`, `tests/`, bible.

## Stage 1: Resolve seven segments and Preview payload

**Done when:** `POST /api/admin/adhoc/preview` with `system_prompt`, `cache_prompt`, `cache_prompt_c`, and `user_prompt` populated (B and D omitted or `""`) returns JSON whose `system` is the token-resolved system (agent `content` when `system_prompt` is empty/whitespace), `cache` / `cache_a` equal the resolved Cache A text, `cache_c` equals the resolved Cache C text, `cache_b` and `cache_d` are `""`, `user` / `nocache` / `live_content` unchanged in meaning. Preview still does not write `agent_data` or a ledger row. `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, in `_resolve_adhoc`, keep agent/model/candidate/task_key_uuid/`_chain_context` / `resolved_task_system` as they are. Change **only** the prompt-resolution block that currently reads:

   ```python
       _cc = _chain_context(agent, cd, task_key, jc)
       agent_task_for_system = (
           {"system_prompt": ""} if agent_task_row is None and task_key == "adhoc" else (agent_task_row or {})
       )
       return {
           "system": resolved_task_system(agent, agent_task_for_system, cd, task_key, _cc, jc),
           "user": resolve_tokens(body.get("user_prompt", ""), cd, task_key, _cc, jc),
           "cache": resolve_tokens(body.get("cache_prompt", ""), cd, task_key, _cc, jc),
           "nocache": resolve_tokens(body.get("nocache_prompt", ""), cd, task_key, _cc, jc),
           ...
       }, None
   ```

   to:

   ```python
       _cc = _chain_context(agent, cd, task_key, jc)
       if "system_prompt" in body:
           # Editor sent the field (sibling #2): empty → agent content via resolved_task_system.
           agent_task_for_system = {"system_prompt": body.get("system_prompt") or ""}
       else:
           # Key omitted (today’s three-slot UI): keep DB task system, then agent content.
           agent_task_for_system = (
               {"system_prompt": ""} if agent_task_row is None and task_key == "adhoc" else (agent_task_row or {})
           )
       cache_a = resolve_tokens(body.get("cache_prompt", "") or "", cd, task_key, _cc, jc)
       cache_b = resolve_tokens(body.get("cache_prompt_b", "") or "", cd, task_key, _cc, jc)
       cache_c = resolve_tokens(body.get("cache_prompt_c", "") or "", cd, task_key, _cc, jc)
       cache_d = resolve_tokens(body.get("cache_prompt_d", "") or "", cd, task_key, _cc, jc)
       return {
           "system": resolved_task_system(agent, agent_task_for_system, cd, task_key, _cc, jc),
           "user": resolve_tokens(body.get("user_prompt", ""), cd, task_key, _cc, jc),
           "cache": cache_a,
           "cache_a": cache_a,
           "cache_b": cache_b,
           "cache_c": cache_c,
           "cache_d": cache_d,
           "nocache": resolve_tokens(body.get("nocache_prompt", ""), cd, task_key, _cc, jc),
           "model_code": model_code,
           "tier_meta": tier_meta,
           "temperature": temperature,
           "max_tokens": max_tokens,
           "candidate_id": candidate_id or None,
           "task_key_uuid": task_key_uuid,
           "api_key_override": api_key_override,
       }, None
   ```

   Request field names are the Manage Tasks / `PUT /tasks/<task_key>` names: `system_prompt`, `user_prompt`, `cache_prompt` (A), `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`. Do **not** invent `cache_a` on the request body.

2. In `adhoc_preview`, replace the `jsonify({...})` keys so the payload is:

   ```python
       return jsonify({
           "system": resolved["system"],
           "user": resolved["user"],
           "cache": resolved["cache"],
           "cache_a": resolved["cache_a"],
           "cache_b": resolved["cache_b"],
           "cache_c": resolved["cache_c"],
           "cache_d": resolved["cache_d"],
           "nocache": resolved["nocache"],
           "live_content": live_content,
       })
   ```

   Always include `cache_a`–`cache_d` (empty string when that slot resolved empty) so sibling #3 can show empty tabs. Keep `cache` as the Cache A alias so today’s Preview tab (`PreviewKey = "cache"`) still reads A. Do **not** call `save_agent_data` / ledger helpers from Preview.

3. Do **not** change `PUT /api/admin/tasks/<task_key>` (`update_task`). `save_agent_task(..., system_prompt=None)` means leave the column; `system_prompt=""` writes empty. Empty System on Save As must **not** copy agent `content` into `system_prompt`. That path is already correct if the key is present with `""`.

⚠️ **Decision:** `"system_prompt" in body` vs omitted. Production fallback is empty **segment** → agent `content` (`resolved_task_system`). Sibling #2 will send the key (including `""`). Until then the current page omits the key; treating omit as today’s DB-row system avoids Preview/Test dropping a loaded task’s saved system during the #1-only window. Empty string in the body never falls back to the DB task row — only to agent `content`.

⚠️ **Decision:** Reuse `resolved_task_system` for the system slot rather than a second fallback. Token resolve for A–D is the same `resolve_tokens(..., _cc, jc)` already used for Cache A.

## Stage 2: Assemble Cache A–D, persist, Test identity, store debug

**Done when:** A workbench Test whose resolved segments are System + Cache A + Cache C + User (B and D empty, no nocache, no live) calls `_assemble_blocks_seven_segment` with four cache slots (B and D empty/omitted by that helper) and `_store_prompt_blocks(..., caches_resolved_four=(A, "", C, ""))`, so `agent_data` for that `batch_id` contains `SYSTEM`, `CACHE_A`, `CACHE_C`, `TASK`, and `RESPONSE` and does **not** contain `CACHE_B` or `CACHE_D` rows. `POST /api/admin/adhoc/test` HTTP 200 includes `batch_id` equal to the ledger id (`adhoc-<task_key>-<uuid>`). HTTP 500 `success: false` (soft provider failure that still returns a result dict) also includes that `batch_id`. The AST-1393 stringify + `_caller_response_blob` success store is unchanged. When `debug=True`, each stored **prompt** block emits one Style D index header plus found → recorded detail (payload truncated via `debug_detail_block`); when `debug=False`, this store path adds no new debug-contract lines. `python3 -m py_compile src/core/agent.py src/ui/api/api_admin.py` passes.

1. In `src/core/agent.py`, extend `run_adhoc` with three optional kwargs immediately after `cache_content` (defaults `None`): `cache_content_b`, `cache_content_c`, `cache_content_d`. Replace the `_assemble_blocks(...)` call with `_assemble_blocks_seven_segment`:

   ```python
       system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens = _assemble_blocks_seven_segment(
           system_content=system_content,
           user_content=user_content,
           caches_resolved_four=(cache_content, cache_content_b, cache_content_c, cache_content_d),
           nocache_content=nocache_content,
           live_content=live_content,
           model_code=model_code,
           skip_cache=False,
       )
   ```

   Leave `send_to_anthropic` / `send_to_deepseek` arguments unchanged. Do **not** delete `_assemble_blocks` (legacy wrapper still used elsewhere / tests). Existing `run_adhoc(..., cache_content="...")` callers stay valid: B/C/D default `None` and the seven-segment helper skips empty slots.

2. In `run_adhoc_workbench_test`, add the same three optional kwargs (`cache_content_b`, `cache_content_c`, `cache_content_d`, default `None`) after `cache_content`. Pass them through to `run_adhoc`. Replace the `_store_prompt_blocks` call that currently uses `cache_content=cache_content or None` with the production four-slot interface (**do not** also pass `cache_content=` — that raises `TypeError`):

   ```python
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
           )
   ```

   Empty/whitespace cache slots are omitted inside `_store_prompt_blocks` (`if blob and blob.strip()`). Live content, when present, still stores a `NO_CACHE` row — same as production. Do **not** skip the `SYSTEM` row.

3. Still in `run_adhoc_workbench_test`, immediately before `return result` (the single successful-return at the end of the `try`, after ledger COMPLETED/FAILED update), set `result["batch_id"] = batch_id`. Do **not** add `batch_id` on the exception path that `raise`s after marking FAILED. Do **not** edit the AST-1393 success stringify block (`_caller_response_blob` / `debug_index` `outcome="serialized store"` / `_store_response_block`).

4. In `src/ui/api/api_admin.py` `adhoc_test`, pass the four resolved caches into `run_adhoc_workbench_test`. Use `.get` so existing tests that monkeypatch `_resolve_adhoc` with only `cache` / `nocache` do not KeyError:

   ```python
           result = asyncio.run(run_adhoc_workbench_test(
               workbench_task_key=task_key,
               candidate_id=resolved["candidate_id"],
               entity_id=entity_id or None,
               system_content=resolved["system"],
               user_content=resolved["user"],
               cache_content=resolved.get("cache") or None,
               cache_content_b=resolved.get("cache_b") or None,
               cache_content_c=resolved.get("cache_c") or None,
               cache_content_d=resolved.get("cache_d") or None,
               nocache_content=resolved.get("nocache") or None,
               live_content=live_content,
               response_format=task_response_format,
               model_code=resolved["model_code"],
               tier_meta=resolved.get("tier_meta"),
               temperature=resolved["temperature"],
               max_tokens=resolved["max_tokens"],
               api_key_override=resolved["api_key_override"],
               task_key_uuid=resolved["task_key_uuid"],
               debug=ui_llm_debug(),
           ))
   ```

5. In the same `adhoc_test`, after `if not result.get("success"):` keep HTTP 500, but include `batch_id` when present:

   ```python
       if not result.get("success"):
           err_body = {"success": False, "error": result.get("error", "Unknown error")}
           if result.get("batch_id"):
               err_body["batch_id"] = result["batch_id"]
           return jsonify(err_body), 500
   ```

   On the success `jsonify`, add `batch_id`:

   ```python
       return jsonify({
           "success": True,
           "response_text": response_text,
           "hydrated": hydrated,
           "timesheet": timesheet,
           "batch_id": result.get("batch_id"),
       })
   ```

   Leave `_caller_response_blob` extraction, encoded `_decode_payload`, `@require_admin`, and the exception→500 branch unchanged. Do **not** add schema/grade validation. Sibling #3 loads panes via existing `GET /api/agent_data/<batch_id>` (`api_system.py`) — do not add a new route.

6. In `_store_prompt_blocks`, keep the dual `caches_resolved_four` / `cache_content` contract and the skip-empty rules. Change the save loop so both paths collect `(block_type, content)` first, then save. Replace the inner `if debug: dbg.debug_detail("agent_data_write ...")` with Style D **per stored prompt block**:

   After building the list of segments to write (SYSTEM always; then A-only **or** A–D; then optional NO_CACHE / live NO_CACHE / TASK — same membership as today), loop `enumerate(segments, start=1)` with `total = len(segments)`. Inside `_save` after `save_agent_data`, when `debug` is True:

   ```python
           dbg = get_logger(__name__, debug_flag=True)
           outcome = result.get("outcome")
           dbg.debug_index(
               func="_store_prompt_blocks",
               index=index,
               total=total,
               identifier=f"{block_type}:{result.get('agent_data_id') or agent_data_id}",
               outcome=str(outcome) if outcome is not None else "saved",
           )
           dbg.debug_detail(f"found block_type={block_type} chars={len(content)}")
           dbg.debug_detail_block(content)
           dbg.debug_detail(
               f"recorded outcome={outcome} agent_data_id={result.get('agent_data_id')} "
               f"ref_agent_data_id={result.get('ref_agent_data_id')!r}"
           )
   ```

   Pass `index` and `total` into `_save`. When `debug=False`, emit none of those lines (no `debug_index` / `debug_detail` / `debug_detail_block`). Do **not** change `_store_response_block` (AST-977 `agent_data_write` + AST-1393 serialize found→recorded stay as-is). Do **not** add `logger.info("[DEBUG] …")`. `debug_detail_block` already truncates long payloads (15 / omitted / 15).

⚠️ **Decision:** Workbench store always uses `caches_resolved_four=`, never the legacy `cache_content=` branch, so Cache B–D cannot be dropped on the way through Test. `run_adhoc` still accepts `cache_content` as slot A for existing callers.

⚠️ **Decision:** Style D lives in the shared `_store_prompt_blocks` helper (the store production already uses) rather than a workbench-only logger. `do_task` assembly is untouched; `do_task` already calls this helper with `caches_resolved_four`. Debug lines remain gated on the existing `debug` flag.

⚠️ **Decision:** Test identity is `batch_id` only. That is the key `GET /api/agent_data/<batch_id>` already uses. Do not add a second Ad Hoc agent_data endpoint.

## Execution contract

- Execute stages in order. One commit per stage on this epic worktree, then `git push origin HEAD:sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist`.
- Do not add files, config blocks, routes, or React editors not listed above.
- Do not fold Ad Hoc Test into `do_task` (schema/grade validation stays off the workbench).
- If a referenced helper signature has drifted, stop and comment on **AST-1403** with the Stage N blocked template — do not improvise.

## Estimate

Confirm Chuckles estimate: 5 — revise to 3 because this is wiring Ad Hoc onto existing `_assemble_blocks_seven_segment` / `_store_prompt_blocks(caches_resolved_four=)` / `resolved_task_system`; no schema, no React, no new tables.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1411
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` @ `acf80f98461d696f7a421a177df9198945357780`

## Traceability

AC5→Stage 2 (four-slot `caches_resolved_four` assemble/store; omit empty CACHE_B/D); AC6→Stage 1 (`system_prompt` in body → agent fallback; omit key → DB task system) + Stage 2 (Preview/Test send resolved system); AC7→Stage 2 step 6 (Style D `debug_index`/`debug_detail` per stored prompt block, gated on `debug`).

## Findings

**acceptable** — Stage 2 step 6 refactors shared `_store_prompt_blocks` debug emission (not workbench-only). Intentional: parent functional scope requires found→recorded per block on the store path; reuses the production helper rather than forking.

**acceptable** — No explicit Self-Assessment conf block; stages + Done-when criteria are specific enough for this wiring-only scope.

context_tokens≈32000

[plan-rubric] PROCEED (Commit: acf80f98) seven-segment backend wiring

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist`  
**Product commits:** `a576dea8` (Stage 1 — seven-segment `_resolve_adhoc` + Preview keys), `e2795bec` (Stage 2 — `_assemble_blocks_seven_segment` / `caches_resolved_four` store, Test `batch_id`, Style D on `_store_prompt_blocks`)

React editors, preview modal, panes, Save As PUT, `do_task` assembly, and AST-1393 stringify left untouched.

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1411
**Publish ref:** `origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` @ `11477b6c6664e3f60c9fe23519e86e40d6b0f5c7`
**Overall:** CLEAN

**Diff baseline:** `origin/dev...origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist` (14 files; product: `src/core/agent.py`, `src/ui/api/api_admin.py`; plus Betty `merge-tests` / test-bible / `tests/**`)

**Status gate:** Spawn prompt `Tests Passed` — trusted.

**Joan:** plan-rubric APPROVED attached; no Excluded statute list — no straggler callouts.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No confidence/scoring paths touched |
| astral.agent.do-task-delegation | scoped | conforms | Ad Hoc still delegates I/O to externals; no new inline provider calls |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade/vector validation touched |
| astral.batch.batch-id-first | scoped | conforms | Workbench still sets `log_batch_id` before store; `batch_id` returned on soft-fail |
| astral.batch.batch-id-format | scoped | conforms | Existing `adhoc-{task_key}-{uuid}` ledger id unchanged |
| astral.batch.claim-process-release | scoped | not-applicable | No batch claim/clear helpers changed |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No latest-response selection logic changed |
| astral.config.config-source-of-truth | scoped | not-applicable | No config surface changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug/artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike/debug-dir paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | `dispatcher.py` / seed paths untouched |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No `run_next` / chain authority changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `ast-1411-*.md` plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Product `src/**` commits are engineer (`code(AST-1411)`); test/bible via Betty |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits limited to `src/`; test tree is Betty lane |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No new core→external assembly or I/O |
| astral.layers.import-direction | scoped | conforms | No new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | API resolves tokens/server-side; no hardcoded UI state |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | Empty CACHE_B/D omitted via `strip()`; intentional per plan |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render/consult orchestration |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` unchanged on preview/test |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | Seed/admin-json paths untouched |
| astral.seed.archie-catalog-wins | scoped | not-applicable | Dispatcher/catalog paths untouched |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No seed hot-path changes |
| astral.seed.define-approved | scoped | not-applicable | No define/seed approval flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row seed logic |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed logic |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer logging added |
| astral.standards.database-header-inventory | scoped | not-applicable | No `src/data/**` changes |
| astral.standards.debug-contract-gated | scoped | conforms | Style D index/found/recorded gated on `debug=True`; no `[DEBUG]` info spam |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses production helpers; segment-collect refactor is bounded |
| astral.standards.in-scope-only | scoped | conforms | Product diff limited to planned `agent.py` / `api_admin.py` wiring |
| astral.standards.logging-via-utils | scoped | conforms | Debug via `get_logger(..., debug_flag=True)` |
| astral.standards.names-not-ticket-ids | scoped | conforms | No ticket-id symbol names in product code |
| astral.standards.no-cross-contamination | scoped | conforms | Ad Hoc wiring only; `do_task` assembly untouched |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new hardcoded business sets |
| astral.standards.public-then-helpers | scoped | conforms | Changes stay in existing public entrypoints/helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No `src/utils/**` changes |
| astral.state.core-decides-transitions | scoped | not-applicable | No job/roster transition logic |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job prior-state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No daisy-chain run logic |
| astral.ui.frontend-file-placement | scoped | not-applicable | No `src/ui/frontend/**` product changes |
| astral.ui.naming-conventions | scoped | conforms | Preview keys follow existing `cache_prompt_*` naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No worker/config deployment changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip `merge-tests(AST-1411): origin/tests 0cf26ca1` present |
| orch.git.commit-vocabulary | universal | conforms | `code`/`test`/`docs`/`merge-tests` vocabulary on branch |
| orch.git.flow-direction-inviolable | universal | conforms | Sub publish ref; diff vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | Child `sub/AST-1403/AST-1411-...` topology |
| orch.git.merge-on-checkout | universal | conforms | No merge/rebase violations in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No forbidden git ops in artifact |
| orch.git.no-dev-agent-branches | universal | conforms | Publish on `sub/*`, not agent-named dev branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1403` worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch classes introduced |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Plan decisions documented; no new product forks |
| orch.pipeline.plan-is-bible | universal | conforms | Implementation matches staged plan Done-when |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code diff |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed per pipeline |
| orch.roles.archie-approves-statutes | universal | conforms | No canon statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible changes on Betty commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee; review recommend-only |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-ban evidence in diff |

**Active set scored:** 65 / 65

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan/parent cite no catalog patterns |

## Plan adherence

Stage 1 and Stage 2 match the issue doc Done-when criteria:

- **`_resolve_adhoc`:** token-resolves A–D; `system_prompt in body` vs omitted behavior matches the documented decision; Preview returns `cache` alias plus `cache_a`–`cache_d`.
- **`run_adhoc` / `run_adhoc_workbench_test`:** `_assemble_blocks_seven_segment` with four slots; workbench store uses `caches_resolved_four=` only (no legacy `cache_content=`).
- **`adhoc_test`:** forwards four caches via `.get`; returns `batch_id` on HTTP 200 and soft-fail 500; exception path that re-raises still omits `batch_id` (plan step 3).
- **`_store_prompt_blocks`:** segment collect → per-block Style D (`debug_index` N/M, found, `debug_detail_block`, recorded) when `debug=True`; quiet when `debug=False`.
- **Out of scope respected:** no React, no Save As PUT, no `do_task` / AST-1393 stringify edits, no new routes.

**Estimate (3):** footprint fits — two product files, wiring onto existing helpers.

Betty coverage (`TestAst1411*`, revised `TestAst515*`, `test_api_admin.py`) aligns with manifest intent in `docs/test-bible/core/agent.md` and `docs/test-bible/ui/api/api_admin.md`.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Publish-ref cargo:** branch tip includes Betty `test(AST-1408)` frontend cases via `merge-tests` — not AST-1411 product scope; expected for Tests Passed. Downstream `merge-child` should treat as tests-line alignment, not #1411 feature scope.
- **Shared helper blast radius:** `_store_prompt_blocks` Style D applies to production `do_task` store path too — Joan/plan marked acceptable; operators will see new per-block debug on production store when `debug=True`.

## What's solid

- Clean wiring onto existing `_assemble_blocks_seven_segment` / `_store_prompt_blocks(caches_resolved_four=)` / `resolved_task_system` — no parallel Ad Hoc store fork.
- Empty cache omission and SYSTEM-always-store semantics preserved.
- `batch_id` identity for sibling #3 (`GET /api/agent_data/<batch_id>`) is correct on success and provider soft-fail.
- Style D test (`test_store_prompt_blocks_style_d_debug_gated`) asserts both `debug=True` emission and `debug=False` quiet.

## Frame diff

| Planned | Landed |
|---------|--------|
| `api_admin.py` — seven-segment resolve + Preview keys + Test forward/`batch_id` | Matches (`a576dea8`) |
| `agent.py` — assemble/store/batch_id/Style D | Matches (`e2795bec`) |
| No frontend / Save As / `do_task` / AST-1393 block | Confirmed absent from product diff |
| Tests (Betty) | Present via `0cf26ca1` + `merge-tests` (includes AST-1408 frontend tests on tests line) |

## Recommended actions (downstream — not executed here)

- Chuckles: append this artifact to issue doc, `docs()` commit on sub-branch, post slim upshot `--as radia`, move to **Review Posted**.
- datt: **PROCEED** → User Testing (no `resolve-child` needed).

context_tokens≈38000

---

[code-rubric] PROCEED (Commit: 11477b6c) seven-segment adhoc wired
