<!-- linear-archive: AST-862 archived 2026-07-29 -->

## Linear archive (AST-862)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-862/uat-agent-performancefeedback-missing-from-agent-data-agent-response  
**Status at archive:** Archive  
**Project:** Astral Auditor  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-378 — Runtime Rubric Validation  
**Blocked by / blocks / related:** parent: AST-378

### Description

## What failed

Susan UAT 2026-07-11 00:08: Parsing/hydration now works (`grade_like` debug shows capture start, all 13 lines `parse=ok`), but **agent_performance / FEEDBACK does not appear in the stored** `agent_response` **on** `agent_data`.

Susan: "Looks like it's parsing correctly, now, but the agent performance envelope or feedback does not appear in the agent_response in agent_data table."

Log shows SUCCESS with RACOVK `vector_reviews`, full pipeline trace, then consult continues — but inspecting `agent_data.agent_response` for the job batch lacks `agent_performance` envelope and/or FEEDBACK block reference.

Example: `grade_like` batch `grade_like-c6c2e008-…`, job `532bf4b1-…`, candidate `somerset` — capture trace present in log.

## Expected

1. When vector feedback capture runs on SUCCESS, the persisted `agent_ref` **/** `agent_response` on the entity (and retrievable `agent_data` rows) includes:
   * **FEEDBACK** block in `prompt_blocks` when raw/unparseable fallback applies, OR
   * `agent_performance` (including `vector_reviews`) preserved in the stored response envelope Susan can inspect via agent_data / Performance Monitor / FEEDBACK tab.
2. Admin Vector Feedback rows from `vector_feedback` table remain queryable (capture may already persist DB rows — this bug is **agent_data visibility**).

## Repro

1. Staging: run `grade_like` (or `grade_get`) with debug enabled for candidate `somerset`.
2. Confirm debug log shows `vector feedback capture start` and `parse=ok` for all lines.
3. Query or UI-inspect `agent_data` for that batch/job — `agent_response` / prompt_blocks lack FEEDBACK and/or `agent_performance`.
4. Expected: stored agent_response reflects feedback envelope for Susan's inspection.

## Parent AC (quoted inline)

> 2. When `agent_performance.status = success` but vector feedback is missing or unparseable, the run **still succeeds** for task payload purposes; raw feedback is stored in **agent_data** **FEEDBACK**; **no** **vector_feedback** rows are created for that run.

> 7. With debug enabled, rubric-backed runs log each vector feedback found and recorded, or log that raw FEEDBACK was stored due to parse failure.

## Boundaries

* Does not change lenient run success or consult scoring.
* Does not revert AST-859/860 parse/capture fixes.

### Comments

#### radia — 2026-07-11T00:16:13.938Z
### AST-862 review (FIX-UAT)

**Diff:** `origin/dev...origin/sub/AST-378/AST-862-uat-agent-response-feedback-envelope` (code `265b552`, doc after push)
**Plan:** `docs/features/auditor/ast-862-uat-agent-response-feedback-envelope.md` § Review (Radia)

**What looks good**
- Clean-parse success path now mirrors unparseable branch: `store_feedback_block` + FEEDBACK ref in `prompt_blocks` after successful `insert_vector_feedback_rows`.
- Fixes Susan repro: `vector_feedback` rows persisted but no FEEDBACK in agent_data / Performance Monitor tab.
- RESPONSE / encoded consult decode unchanged; additive inspection only.
- Tests: FEEDBACK JSON content, AST-724 clean-parse expectation updated, store_feedback failure does not undo rows.

**advisory**
- If FEEDBACK store fails after row insert, Admin still has rows but agent_data lacks FEEDBACK (existing lenient swallow pattern).
- Pre-862 clean-parse batches need re-dispatch for FEEDBACK block — expected.

**Verdict:** Clean — approve for User Testing. No fix-now.

#### betty — 2026-07-11T00:15:15.915Z
## QA test manifest (AST-862)

**Publish ref:** `origin/sub/AST-378/AST-862-uat-agent-response-feedback-envelope` @ `265b552` (`merge-tests(AST-862): origin/tests 41db321`)

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

1. **Clean parse → FEEDBACK block (required):** `tests/component/core/test_agent.py::TestAst862CleanParseFeedbackBlock::test_clean_parse_feedback_block_has_vector_reviews_json` — after successful `insert_vector_feedback_rows`, `prompt_blocks` gains FEEDBACK ref and `agent_data` row holds `vector_reviews` JSON via `format_vector_reviews_raw`.

2. **FEEDBACK store failure non-fatal (required):** `tests/component/core/test_agent.py::TestAst862CleanParseFeedbackBlock::test_store_feedback_block_failure_still_inserts_vector_feedback_rows` — `vector_feedback` rows persist when `store_feedback_block` raises.

3. **AST-724 regression (required):** `tests/component/core/test_agent.py::TestAst724VectorFeedbackCapture::test_clean_parse_inserts_vector_feedback_rows` — revised assertion: clean parse now expects rows **and** FEEDBACK block (was empty `prompt_blocks` pre-862).

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst862CleanParseFeedbackBlock \
  tests/component/core/test_agent.py::TestAst724VectorFeedbackCapture::test_clean_parse_inserts_vector_feedback_rows \
  -q
```

**3 passed** on replay against publish ref.

**Test bible shasums** (`origin/sub/AST-378/AST-862-uat-agent-response-feedback-envelope` @ `265b552`):
- `docs/test-bible/core/agent.md`: 37d14ff67dcf6ed58372a16e8ee8c85fa2787275

— Betty

#### ada — 2026-07-11T00:12:43.826Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-378/AST-862-uat-agent-response-feedback-envelope/docs/features/auditor/ast-862-uat-agent-response-feedback-envelope.md

**Scope:** minor — single clean-parse branch in `_capture_rubric_vector_feedback`: append FEEDBACK block to `prompt_blocks` via existing `store_feedback_block` / `format_vector_reviews_raw` after successful `insert_vector_feedback_rows`.

**Conf:** high — Susan repro + code confirms clean-parse path omits FEEDBACK while unparseable path already stores it; FEEDBACK tab (AST-808) consumes this block shape.

**Risk:** low — intentional inspection duplicate alongside `vector_feedback` rows; no RESPONSE decode or consult scoring change.

---

# AST-862 — UAT: agent_performance/FEEDBACK missing from agent_data agent_response

- **Linear:** [AST-862](https://linear.app/astralcareermatch/issue/AST-862/uat-agent-performancefeedback-missing-from-agent-data-agent-response)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation) — Runtime Rubric Validation
- **Publish ref:** `origin/sub/AST-378/AST-862-uat-agent-response-feedback-envelope`
- **Shipped baseline:** [AST-860](https://linear.app/astralcareermatch/issue/AST-860/uat-grade-get-racovk-vector-reviews-still-not-captured-or-hydrated) capture normalize + expected_codes; [AST-859](https://linear.app/astralcareermatch/issue/AST-859/uat-fix-vector-reviews-prompt-example-racovk) RACOVK prompt; [AST-808](https://linear.app/astralcareermatch/issue/AST-808/uat-hydrate-rubric-vector-codes-on-admin-vector-feedback) FEEDBACK tab hydrate

## Summary

Susan UAT 2026-07-11 00:08 (post AST-860): **`grade_like`** / **`grade_get`** capture now runs — debug shows `vector feedback capture start`, all lines `parse=ok`, **`vector_feedback`** rows may persist — but **`agent_performance` / FEEDBACK is absent from the stored `agent_ref`** on job **`agent_responses`** and from inspectable **`agent_data`** (Performance Monitor / FEEDBACK tab). Root cause: clean-parse SUCCESS path calls **`insert_vector_feedback_rows`** only; **`store_feedback_block` + `prompt_blocks` FEEDBACK ref** run **only** on unparseable fallback (AST-724). Encoded-batch **RESPONSE** block stores decoded **`jobs[]`**, not the pre-unwrap envelope. This UAT fix adds an inspection **FEEDBACK** block on clean parse so Susan can see **`vector_reviews`** in **`agent_data`** without changing lenient run success or consult scoring.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Revert AST-859/860 capture or parse fixes | — |
| Change lenient run success / consult scoring | — |
| Admin Vector Feedback list API changes | — (DB rows already queryable) |
| Retroactive backfill of historical agent_responses | — |

## Root cause (plan-time)

| # | Gap | Evidence |
|---|-----|----------|
| 1 | **Clean parse skips FEEDBACK block** | `_capture_rubric_vector_feedback` (~lines 1381–1413): success path inserts **`vector_feedback`** rows and debug logs only; **`prompt_blocks.append({"type": "FEEDBACK", ...})`** is inside the **`parsed_rows is None`** branch (~line 1356) only. |
| 2 | **RESPONSE stores decoded payload, not envelope** | SUCCESS **`_store_response_block`** (~line 2491) stores **`json.dumps(parsed)`** after **`agent_payload` unwrap + decode** → **`jobs[]`** shape for encoded consult; **`agent_performance`** from **`envelope_snapshot`** is not copied into RESPONSE. |
| 3 | **`agent_ref` carries `prompt_blocks` refs only** | **`agent_ref`** (~lines 2502–2508) has no top-level **`agent_performance`**; inspection flows load **FEEDBACK** / **RESPONSE** blocks by id from **`prompt_blocks`**. Missing FEEDBACK ref ⇒ Susan sees no feedback envelope in UI. |

Susan repro: `grade_like` batch `grade_like-c6c2e008-…`, job `532bf4b1-…`, capture trace + `parse=ok` × 13, but **`agent_response`** lacks FEEDBACK / envelope.

⚠️ **Decision:** Add **FEEDBACK** block on **clean parse** (inspection duplicate of `vector_reviews` JSON) — same **`store_feedback_block` / `format_vector_reviews_raw`** as unparseable path. **`vector_feedback`** rows remain authoritative for Admin; FEEDBACK block satisfies parent AC #2 visibility + AST-808 FEEDBACK tab hydrate. Do **not** reshape encoded-batch RESPONSE body (would break job-grade consumers).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Append FEEDBACK block to `prompt_blocks` on clean vector_feedback capture | core |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

---

## Stage 1: FEEDBACK block on clean parse (`agent.py`)

**Done when:** After successful `insert_vector_feedback_rows`, `prompt_blocks` contains a **FEEDBACK** ref and `agent_data` has a **FEEDBACK** row with `vector_reviews` JSON for that batch; unparseable path unchanged; manual capture test shows FEEDBACK block on clean parse.

1. In **`src/core/agent.py`**, locate **`_capture_rubric_vector_feedback`** clean-parse success path after **`insert_vector_feedback_rows`** succeeds (~line 1389), **before** the debug hydrate loop (~line 1395).

2. Add FEEDBACK storage mirroring the unparseable branch (~lines 1348–1356):

   ```python
   try:
       fb_id = store_feedback_block(
           entity_type,
           task_key,
           batch_id,
           format_vector_reviews_raw(perf_dict),
           index=index,
       )
       prompt_blocks.append({"type": "FEEDBACK", "id": fb_id})
   except Exception:
       logger.debug("store_feedback_block failed", exc_info=True)
   ```

   Use existing **`perf_dict`** (set ~line 1321). **`format_vector_reviews_raw`** already returns JSON list of compact strings when **`vector_reviews`** present — compatible with AST-808 **`POST /vector_feedback/hydrate_reviews`** and FEEDBACK tab.

3. Do **not** change:
   - Unparseable branch (already stores FEEDBACK).
   - **`insert_vector_feedback_rows`** call or strict parse rules.
   - **`agent_ref`** / RESPONSE store shape for encoded consult.
   - **`consult.py`** batch **`append_agent_response`** — shared **`agent_ref`** from **`do_task`** already propagates updated **`prompt_blocks`** to each job.

4. Manual verify on epic worktree (requires seeded DB with rubric vectors):

   ```python
   from src.core.agent import _capture_rubric_vector_feedback
   # After call with perf={"status":"success","vector_reviews":["G1RACOVK"]} and matching rubric:
   # assert any(b["type"] == "FEEDBACK" for b in prompt_blocks)
   # assert vector_feedback rows count > 0
   ```

   Reuse pattern from **`TestAst724VectorFeedbackCapture.test_clean_parse_inserts_vector_feedback_rows`** — engineer verifies FEEDBACK ref present at build; Betty adds manifest at Code Complete.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.7 consult | Capture hook only; consult scoring unchanged |
| Lenient contract | FEEDBACK block is additive inspection; run still succeeds |
| §3.3 imports | Reuses existing `store_feedback_block`, `format_vector_reviews_raw` |

---

## Execution contract (build-child)

- **One stage**, one commit on epic worktree; publish to **`origin/sub/AST-378/AST-862-uat-agent-response-feedback-envelope`**.
- Do **not** edit **`tests/`** or **`docs/test-bible/**`**.
- On ambiguity — **`🛑 Stage 1 blocked`** on **AST-378** parent; stop.

---

## Self-Assessment

**Scope:** `minor` — Single branch in `_capture_rubric_vector_feedback` in `agent.py`.

**Conf:** `high` — Susan repro + code path confirms clean-parse omission; unparseable path is the template; FEEDBACK tab already consumes this block shape.

**Risk:** `low` — Duplicate storage (rows + FEEDBACK JSON) is intentional for inspection; no change to task payload or RESPONSE decode.

---

## Self-review vs ASTRAL_CODE_RULES

| Section | Result |
|---------|--------|
| §2.7 consult | Additive agent_data visibility only |
| §1.3 DRY | Reuses existing `store_feedback_block` / `format_vector_reviews_raw` |
| §3.3 imports | No new modules |

No unresolved rule conflicts.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-378/AST-862-uat-agent-response-feedback-envelope` (code tip `265b552`)  
**Reviewed:** 2026-07-11 (FIX-UAT / AST-378)

Minimal UAT fix diff (4 files) — single capture-hook branch; this review is AST-862 only.

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Clean-parse success path mirrors unparseable branch: `store_feedback_block` + `prompt_blocks` FEEDBACK ref after successful `insert_vector_feedback_rows`; RESPONSE / consult decode unchanged. |
| Root cause | Closes Susan gap: `vector_feedback` rows persisted but no FEEDBACK ref in `agent_ref.prompt_blocks` → FEEDBACK tab / Performance Monitor had nothing to hydrate. |
| §2.7 consult | Additive inspection only; lenient contract preserved; encoded-batch RESPONSE still stores decoded `jobs[]`. |
| Failure handling | `insert_vector_feedback_rows` failure still returns before FEEDBACK store; FEEDBACK store failure swallowed without undoing rows (tested). |
| Tests | `TestAst862CleanParseFeedbackBlock` asserts FEEDBACK JSON matches `vector_reviews`; AST-724 clean-parse test updated; store_feedback failure isolation test. |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| advisory | `_capture_rubric_vector_feedback` | If `insert_vector_feedback_rows` succeeds but `store_feedback_block` fails, Admin has rows but agent_data lacks FEEDBACK — same swallow pattern as unparseable path; acceptable lenient tradeoff. |
| advisory | Historical runs | Pre-862 batches with clean parse have `vector_feedback` rows but no FEEDBACK block until re-dispatch — expected per out-of-scope backfill. |

### Recommended actions

| Priority | Action |
|----------|--------|
| **resolve** | None required — approve for User Testing. |
| UAT | Re-run Susan `grade_like` / `grade_get` batch: Performance Monitor → agent data → FEEDBACK tab shows hydrated compact reviews; `prompt_blocks` includes FEEDBACK ref on `agent_response`. |

**Verdict:** Clean — approve for User Testing.

---

## Resolution

**Resolved:** 2026-07-11  
**Review:** Radia clean — no fix-now items.

| Item | Outcome |
|------|---------|
| Product | No additional changes — shipped at `0caf76b` as reviewed |
| Tests | Betty manifest green (3/3 on first pass) @ `265b552` |
| Docs | Radia review section at `c81cb55` |

**Publish ref:** `origin/sub/AST-378/AST-862-uat-agent-response-feedback-envelope` @ `c81cb55`  
**§9a:** Clean merge into `origin/dev` and `origin/ftr/AST-378-runtime-rubric-validation`.
