<!-- linear-archive: AST-502 archived 2026-06-15 -->

## Linear archive (AST-502)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-502/dispatcher-multi-chunk-cache-warm-exhaustion-high-volume-encoded-batch  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-500 — High-volume encoded batch consult: migrate all stages, cache-first exhaustion runs  
**Blocked by / blocks / related:** parent: AST-500; blocks: AST-503

### Description

## What this implements

When a consult step has more work than one **dispatch_task** batch allows, split into chunks of size **batch_size** (up to 500). Run **chunk 1** alone (cache warm), then run **chunks 2…K in parallel** (up to 500 concurrent assessments per wave). In one scheduler tick, **drain the full queue** for that step—no artificial cap on total jobs beyond chunking and concurrency limits.

## Acceptance criteria

3. A backlog of **2000** jobs with batch size **500** runs as **four** chunks: first chunk sequential, remaining three concurrent; all **2000** reach terminal or retry states in that run (not left in trigger state).
4. **Cache-first** behavior preserved: chunk 1 warms cache; later chunks benefit from warm cache.
5. **One scheduler tick** can exhaust the full queue for a step (no partial drain by design).
6. **Partial chunk failure:** per-job **RETRY** states when the envelope is valid but lines are missing; whole-chunk error only when the envelope/call fails.

## Boundaries

* Does not fix qualify/evaluate single-call batch path (blocked by AST-501).
* Does not migrate DO/GET/LIKE (sibling AST-503).
* Batch sizes come from **dispatch_task** only.

## Git branch (authoritative)

`sub/AST-500/AST-502-…` under parent `ftr/AST-500-…`.

### Comments

#### radia — 2026-05-27T03:47:46.643Z
**Diff:** `origin/dev...origin/sub/AST-500/AST-502-dispatcher-multi-chunk-cache-warm-exhaustion` @ `c18bbd1d`.

- **Plan / code — OK:** `claim_cap` + `claim_job_batch(..., claim_cap=)` implements “claim up to eligible count, chunk API by `batch_size`” without heuristic caps; raises if `dispatch_tasks.batch_size` missing for exhaustion keys; dispatcher runs chunk 0, `asyncio.sleep(cache_warm_delay_seconds)`, then `gather` on later chunks; `batch_chunk_index` suffix on `do_task` `index` avoids RESPONSE dedupe collisions; `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` narrowed to qualify/evaluate pending AST-503 aligns with stated boundary.
- **Discuss (resilience):** `asyncio.gather` on chunks fails the whole `_run_unified` path on first chunk exception, whereas `_warm_then_gather` absorbs per-entity exceptions into error-shaped dicts — confirm whether hard-fail-one-chunk is the intended failure mode for dispatcher ticks (vs `return_exceptions`/per-chunk summaries).

**Radia doc cherry-pick:** `4737e22f7545cb067dd0937004e3b962d24b5a44` — `git cherry-pick 4737e22f7545cb067dd0937004e3b962d24b5a44`. **`## Review`** appended on publish ref `docs/features/consult/ast-502-dispatcher-multi-chunk-cache-warm-exhaustion.md`.

#### chuckles — 2026-05-27T03:34:47.764Z
QA test manifest (**docs/ASTRAL_TEST_BIBLE.md** §7.13zf):

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestRunUnified::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_two_chunks_skips_sleep_when_delay_zero tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object`

Publish tip: `origin/sub/AST-500/AST-502-dispatcher-multi-chunk-cache-warm-exhaustion` @ `c18bbd1d`. Parent bible line: merge `origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs` before `sub` per integration line (§ Test Bible).

— Betty

#### betty — 2026-05-27T03:28:41.355Z
**Tests Ready — Betty [qa-handoff]** (AST-502 dispatcher chunk exhaustion)

Manifest (narrow):

1. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails` — chunk 0 completes → one `cache_warm_delay_seconds` sleep → tails only after sleep; `K=4` × 500-job slices; `claim_cap` from mocked eligible count.

2. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_two_chunks_skips_sleep_when_delay_zero` — `qualify_job_listings` path, two chunks; `asyncio.sleep` not awaited when delay is `0`; `batch_chunk_index` 0/1.

3. Regression with AST-501 row: `::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities` (dispatcher single-call baseline).

4. `tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_*` (envelope regressions unchanged).

**Publish / integration**

| ref | SHA |
| --- | --- |
| `origin/sub/AST-500/AST-502-dispatcher-multi-chunk-cache-warm-exhaustion` | `c18bbd1d` |
| `origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs` | `9f7c9973` |

`docs/ASTRAL_TEST_BIBLE.md` §7.13zf — SHA256 **`097d7d72e1d9d311be93458803532b94d164468f01c1c31721e0b60e1f81771d`** (identical blob on **sub** and **ftr** tips above).

`dev-betty`: merge **`705ea89a`** (integrate AST-502 product) then **`659d309d`** (tests + bible). Engineer handoff stays **Tests Ready** / assignee **Hedy** for **`test-astral`**.

— Betty

#### hedy — 2026-05-27T03:03:47.188Z
**Published plan:** [docs/features/consult/ast-502-dispatcher-multi-chunk-cache-warm-exhaustion.md](https://github.com/susansomerset/astral/blob/sub/AST-500/AST-502-dispatcher-multi-chunk-cache-warm-exhaustion/docs/features/consult/ast-502-dispatcher-multi-chunk-cache-warm-exhaustion.md)

**Self-assessment (with justifications)**

- **Scope — scope-MAJOR-CHANGE:** Alters dispatcher claiming, sequencing vs parallel gathers, chunk boundaries, and `do_task`/batch indexing coupling—foundation path for exhaustion.
- **Conf — conf-Medium:** Mirrors `_warm_then_gather` intent but introduces parallel gathers over multiple chunk calls; depends on aligning claim SQL predicates with dispatched counts (Stage 1 calls out STOP if mismatch).
- **Risk — risk-HIGH:** Bugs here duplicate work, stall the queue, or corrupt dedupe/clear-batch—dispatcher is prod-critical surface.

---

# AST-502 — Dispatcher multi-chunk cache-warm exhaustion

**Linear:** [AST-502](https://linear.app/astralcareermatch/issue/AST-502/dispatcher-multi-chunk-cache-warm-exhaustion-high-volume-encoded-batch)  
**Parent epic:** [AST-500](https://linear.app/astralcareermatch/issue/AST-500/high-volume-encoded-batch-consult-migrate-all-stages-cache-first)  
**Project:** Astral Consult  
**Publish ref:** `origin/sub/AST-500/AST-502-dispatcher-multi-chunk-cache-warm-exhaustion`

When eligible jobs exceed **`dispatch_tasks.batch_size`**, **`_run_unified`** (job + **`batch_call_mode=1`** consult paths) shall **claim the full backlog** for that **`batch_id`/dispatch ledger cycle** (**one `clear_job_batch` at exit** per code rules §2.4), **partition** claimed rows into contiguous chunks sized **`batch_size`**, **`await`** **chunk 0** (**cache warm**) through the existing **`consult`** batch runners, **`await asyncio.sleep`** for **`ASTRAL_CONFIG["cache_warm_delay_seconds"]`** (**same knob as `_warm_then_gather`**), then **`await asyncio.gather`** on **`chunks 1…K−1`** (each chunk = one **`consult.run_consult_task`**/`_run_batch_consult`/`do_task` round-trip sized to **`batch_size`**). **Depends on AST-501** for **`qualify`**/**`evaluate`** true single-call multi-line payloads — parallel chunks **amplify** regressions otherwise. **Leaves DO/GET/LIKE batch delegation to AST-503** except where **shared splitter** touches generic job batch runner only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/dispatcher.py` | Replace single **`consult.run_consult_task`** call for **`batch_call_mode`** job/consult slice with **`_run_chunked_batch_consult` (new private async helper)** partitioning **`entities`** and orchestrating **`await`/sleep/`gather`** as above; aggregate **`passed`/`failed`/`processed`** summaries into **`_SUMMARY_ZERO` shape**. | core |
| `src/core/consult.py` | Optional thin exports if split logic needs **`run_consult_task`** entry per chunk with explicit subset — **prefer no public API churn** (**dispatcher** passes slices identical to today's full list semantics). May add **`consult_batch_chunk(task, entities_slice, bid, ctx, debug, chunk_suffix)` only if unavoidable** (**document necessity** inline). | core |
| `src/core/agent.py` | **`do_task` index / RESPONSE dedupe**: today **`index=f"{task_key}_batch_{batch_id}"`** from **`_run_batch_consult`** must stay **collision-free** across **parallel chunks** (**two chunks same parent `bid` collide**); extend index with **stable suffix** per chunk (**e.g. `_c{chunk_index}`**) **only inside batch consult path**. | core |
| `src/data/database.py` | Extend **`claim_job_batch`** semantics **or add `claim_additional_job_rows_for_batch`** if single UPDATE cannot economically claim **`>batch_size`** in one txn — canonical approach per parent epic: **`count_eligible` then `LIMIT <eligible>` UPDATE** attaching **`batch_id`**. Prefer **minimal SQL** respecting existing sort/score-floor filters mirrored with **`count_eligible_for_dispatch_task`**. Parameter order **`batch_id` first**. | data |
| `src/core/tracker.py` | If **`database.claim_job_batch` signature** gains total limit / overload, **`get_new_job_batch`** plumbed-through kwargs **maintain backward compatibility**. | core |
| `tests/component/core/test_dispatcher.py` | Unit-test partition + ordering: mocked **`consult`** coroutine asserts **calls == K**, first chunk **serialized before** **`gather`** starts, **`sleep`** invoked exactly once **between** chunk0 completion and **`gather`** (use **`AsyncMock`** + **`unittest.mock`** `patch`** on **`asyncio.sleep`**). | tests |

---

## Stage 1: Expand claim semantics (data layer)

**Done when:** A single **`get_new_job_batch`** / **`database.claim_job_batch`** call can attach **all concurrent eligible rows** (**up to `available`**) for (**state**, **candidate_id**, filters) matching **`count_eligible_for_dispatch_task`** for that **`dispatch_task`** row (**no silent cap at `batch_size`** for claiming).

⚠️ **Decision:** Prefer **raising `effective_claim_limit = available_count` read before UPDATE** (**same predicates as count**) over repeated **`LIMIT batch_size`** rounds that **reuse `batch_id`**, because current SQL only targets **`batch_id IS NULL OR ''`** rows — **incremental accumulate with same bid is unsupported without schema change.**

1. Inspect **`database.count_eligible_for_dispatch_task`** SQL vs **`claim_job_batch` WHERE** clauses — enforce **equality** (**sort order**, **`score_floor`**, **`candidate_id` filter**) so **nothing is double-count mis-claimed**.
2. Implement **`claim_job_batch`** optional parameter **`effective_limit: Optional[int] = None`**: when **`None`**, preserve current behavior (**dispatcher passes `task["batch_size"]`** unchanged for non-exhaust callers). When **`dispatcher` chunked exhaust path passes `effective_limit=int(available_count)`**, **`UPDATE … LIMIT`** uses that integer (**exact eligible count**) — **never `min(..., heuristic_cap)`**.
3. Update **`dispatcher._run_unified`**: **`available = database.count_eligible_for_dispatch_task(task)`** (**already surfaced** indirectly through scheduler) — after successful claim path, **`get_new_job_batch(..., limit=available)` for batch_call_mode chunked mode** (**job + consult**) **instead of `limit=batch_size`**.

⚠️ **Decision:** Separate **claim limit** (large **`available_count`**) from **chunk size** (`task["batch_size"]` API assembly **only**) — avoids mutating **`get_new_job_batch`** default (**10**) for unrelated tasks (**add keyword at consult exhaustion callsite**; **company batches unchanged**).

---

## Stage 2: Chunk splitter + concurrency orchestration (`dispatcher`)

**Done when:** For **`entity_type=="job"`** with **`batch_call_mode==1`** and **`task_key` in configured consult-encoded set `{qualify_job_listings, evaluate_jd, consult_do, consult_get, consult_like}`** (**post-503** may grow set), splitter runs **exactly**:

1. **`K = ceil(len(jobs) / chunk_size)`** with **`chunk_size = int(task["batch_size"])`** from the **`dispatch_task` row**.

   ⚠️ **Decision:** **`chunk_size` source** = **`int(task["batch_size"])`** only — **crash if missing during dispatch** (**configuration error**) per **Susan no magic defaults**.
2. If **`K≤1`** → **`await consult.run_consult_task(..., entities=jobs,...)` once** (**legacy path**) — preserves today’s **`do_task`/batch_id** behavior (**no needless suffix**).

3. If **`K>1`** → build **`chunks`** list slicing **`jobs`** in stable order (**same **`sort_by` claim order** embodied in **`jobs` list`**).

   - **`r0 = await run_chunk(0, chunks[0])`**
   - **`await asyncio.sleep(ASTRAL_CONFIG.get("cache_warm_delay_seconds", 1.0))`**
   - **`gather(*[run_chunk(i, chunks[i]) for i in range(1, K)])`** collecting coroutine results (**tuple of dict summaries** compatible with aggregator).

4. **Aggregation:** **`run_consult_task`** returns **`_SUMMARY_ZERO` shape`; `_run_batch_consult` returns smaller dict (**passed/failed/total**) — unify **into `_SUMMARY_ZERO`** already near bottom of **`run_consult_task`** (**extend splitter to sum fields** analogous to **`_warm_then_gather`** loop).

5. **`run_chunk` responsibilities:** forward **`bid`/`ctx`/`debug`**, **`entity_type/input_state`** identical to today's **`run_consult_task`**.

---

## Stage 3: Uniqueness of **`do_task` index** across parallel chunks

**Done when:** Parallel chunks **never** collide on **`RESPONSE`** block hashing / **`agent_data` dedupe**.

1. Locate **`consult._run_batch_consult`** **`do_task` call** (**`index=f"{task_key}_batch_{batch_id}"`**).
2. Thread optional **`chunk_index: Optional[int] = None`** from **`dispatcher.run_chunk`** (or **`ctx["batch_chunk_suffix"]`** if fewer signature edits).
3. If **`chunk_index`** not **`None`** → **`index=f"{task_key}_batch_{batch_id}_c{chunk_index}"`**.
4. **Append_agent_response** uses **per-job references** unaffected — confirm **RESPONSE BLOCK** storage uses updated index (**dedupe HASH** uniqueness).

⚠️ **Decision:** Prefer **explicit kwarg through `consult` wrappers** vs stuffing **`ctx` magic string**.

---

## Stage 4: Blocked sibling guard + integration notes

**Done when:** Plan doc links **explicit ordering**: **implement after AST-501 merged** (**splitter testing uses multi-line payloads**).

- **Consult DO/GET/LIKE** chunked fan-out activates only after **`run_consult_task`** routes **`batch_slice`** (**AST-503**). Until then, **restrict consult set literal** (**qualify_job_listings**, **`evaluate_jd`**) behind runtime **feature-flagless** **`if`** on **`task_key`** — expands when **AST-503** lands (**single PR per ticket** prefers **narrow first diff** exposing helper only **for keys already batchable**).

**Per-chunk envelope partial failure**: inherited from **`AST-501`/ `_run_batch_consult`** (**retry/error** granularity) — **no new whole-chunk escalation** besides **`do_task` failure** (**entire envelope**).

---

## Stage 5: Tests

**Done when:**

1. Dispatcher test **mocks **`consult.run_consult_task`** → returns **`{total_processed: len(entities)}` mirrored into passed/failed** shape** verifies **ordering** (**sleep**/chunk call pattern).
2. Property check: **`K=4`/`batch_size=500`/`2000`** jobs → **`run_consult_task` awaited 4×** (**first awaited before gather others**).

---

## Self-Assessment

### Scope — **scope-MAJOR-CHANGE**

Cross-cuts **`database` claiming**, **`dispatcher` concurrency**, and **`consult`/`agent`** indexing — foundational dispatch behavior.

### Conf — **conf-Medium**

Depends on aligning **`claim` vs `count` SQL`; parallel **`asyncio.gather`** around shared **`bid`** is **novel** (**integration risk**) though patterns mirror **`_warm_then_gather`**.

### Risk — **HIGH**

Bug could **duplicate claims**, **starve concurrency**, **drop ledger summaries**, or **corrupt RESPONSE dedupe** — **dispatcher is production critical**.

---

## Plan vs ASTRAL_CODE_RULES cross-check

- **§2.4 Batch pattern:** Maintain **single `batch_id` claim/clear lifecycle** (**`clear_job_batch` in `finally` unchanged** — **aggregator processes all chunks prior** **`finally`**).
- **§1.4 No magic defaults:** **`batch_size` from DB**, **`sleep` duration from `ASTRAL_CONFIG` literal**.
- **§3.3:** **`dispatcher` imports `consult`; `database` untouched by `ui`**.
- **`!!-NONE`:** Claim/count predicate mismatch flagged during Stage1 — **STOP** Linear comment if divergence found.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-500/AST-502-dispatcher-multi-chunk-cache-warm-exhaustion` @ `c18bbd1d25cdfd49ed3b4a8611794060fe98dacb`

### What's solid
- **`claim_job_batch`** + **`get_new_job_batch`** plumbed **`claim_cap=`** (`effective_limit` in UPDATE) aligns with widening claims to **`count_eligible_for_dispatch_task`** for encoded batch consult exhaustion; raises if **`dispatch_tasks.batch_size`** missing — no heuristic cap (**plan Stage 1**).
- Dispatcher chunking: **`ceil(len/batch_size)`**, chunk 0 serial then **`sleep(cache_warm_delay_seconds)`**, tail **`asyncio.gather`** — mirrors intent; **`batch_chunk_index`** suffix on **`do_task` index** avoids RESPONSE dedupe collisions across chunks sharing one **`bid`**.
- Narrow **`_CHUNK_EXHAUST_CONSULT_JOB_KEYS`** to qualify + evaluate only on this slice matches AST-503 boundary (**plan Stage 4**).

### Issues / follow-ups

| Severity | Bucket | Topic | Notes |
| -------- | ------ | ----- | ----- |
| discuss | Operational resilience | **`asyncio.gather`** chunk fan-out vs **`_warm_then_gather`** behavior | **`_warm_then_gather`** catches per-slot exceptions into error-shaped summaries; **`gather`** here fails the whole **`_run_unified`** coroutine if a chunk raises — confirm this is acceptable for dispatcher ticks (versus chunk-isolated degraded summaries). |
| advisory | Config access style | **`ASTRAL_CONFIG.get("cache_warm_delay_seconds", 1.0)`** | Same pattern already in **`_warm_then_gather`**; literal exists under **`config.py`** — keyed read would satisfy the strictest reading of §1 binary config access, optional cleanup only if you want uniformity. |

### Recommended actions

No **fix-now** blocker for **`resolve-astral`**; resolve **`discuss`** if Hedy prefers **`gather(return_exceptions=True)`** parity.

---

## Resolution (`resolve-astral`)

**Date:** 2026-05-26  

**Against:** Radia `review-astral` § **Review** on `origin/sub/AST-500/AST-502-dispatcher-multi-chunk-cache-warm-exhaustion` @ **`c18bbd1d`**.

**Product / plan**

- **`fix-now`:** None — `claim_cap` / widen-claim exhaustion, **`batch_chunk_index`**, chunk-0 **`sleep`**, and parallel tail **`gather`** are as-reviewed; **`dev-hedy`** includes the **`docs(AST-502): Radia …`** tip before this appendix.
- **Discuss — `asyncio.gather` failing the whole **`_run_unified`**:** **Confirmed intentional** for catastrophic chunk/consult faults (explicit exception from a **`do_task`/batch invocation**). **`_warm_then_gather`-style** swallowed per-slot summaries are **not** replayed here: within a successful envelope, **`_run_batch_consult`** continues to honor **per-job RETRY** rules for omitted/garbled **positions**, matching parent **AST-500** partial-line expectations. Opting **`return_exceptions=True`** and digesting failures into degraded dicts stays **deferred** unless Susan requests softer tick-level masking.
- **Advisory — `ASTRAL_CONFIG.get(...)` literal default:** Mirrors existing **`_warm_then_gather`** style; left unchanged.
