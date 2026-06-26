# AST-820 — UAT: Add debug logging to vector feedback hydration path

- **Linear:** [AST-820](https://linear.app/astralcareermatch/issue/AST-820/uat-add-debug-logging-to-vector-feedback-hydration-path)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation) — Runtime Rubric Validation
- **Publish ref:** `origin/sub/AST-378/AST-820-uat-vector-feedback-hydration-debug-logging`
- **Shipped baseline:** [AST-816](https://linear.app/astralcareermatch/issue/AST-816/uat-compact-vector-reviews-still-not-hydrating-on-evaluate-jd) capture normalize + diagnostic debug; [AST-808](https://linear.app/astralcareermatch/issue/AST-808/uat-hydrate-rubric-vector-codes-on-admin-vector-feedback) admin/FEEDBACK hydrate API

## Summary

Susan UAT 2026-06-26 (post AST-816): **`evaluate_jd`** with debug enabled still shows opaque compact **`vector_reviews`** in Admin / FEEDBACK UI, and the debug log does not prove the normalize → parse → hydrate pipeline ran or why it stopped. AST-816 added failure/success detail inside **`_capture_rubric_vector_feedback`** but left **silent early returns** and **utils helpers** without structured trace. This UAT fix adds **debug-only, step-by-step logging** through the vector feedback hydration/decode path so Susan can see raw input, normalized list, rubric lookup keys, per-line parse outcome, and hydrate rows emitted — without changing lenient run success or AST-809 metadata.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Lenient run success when feedback is truly unparseable | AST-724 contract |
| `batch_size` / `completed_at` on `vector_feedback` | AST-809 (shipped) |
| Production / non-debug logging noise | — |
| Regex or rubric code-length fixes (unless trace reveals bug and Susan opens follow-up) | separate ticket |
| React FEEDBACK tab changes | AST-816 unless trace shows missing `candidate_id` (log only here) |

## Root cause (plan-time)

Susan cannot tell whether AST-816 code paths execute on staging because:

1. **`_capture_rubric_vector_feedback` early returns are silent when `debug=True`:** non-`success` **`agent_performance.status`**, missing **`batch_id`**, and empty **`expected_codes`** (no DB rubric UUID rows) return with **no** **`debug_index` / `debug_detail`** lines. Any of these would leave FEEDBACK fallback or no rows while the **`raw_response`** block still shows compact codes.

2. **Utils helpers emit no trace:** **`normalize_vector_reviews_raw`**, **`parse_vector_reviews_diagnostic`**, and **`hydrate_vector_review_strings`** return results only — no record of input type (list vs JSON string), normalized line count, rubric lookup key set, or per-line skip reason.

3. **Capture hook may never run:** **`do_task`** calls capture only when **`_owner and _cid`**; missing **`astral_candidate_id`** in ctx skips capture with no debug line even when **`vector_reviews`** is present on the envelope snapshot.

4. **Admin hydrate API is opaque:** **`POST /vector_feedback/hydrate_reviews`** has no trace when Susan opens FEEDBACK tab (separate HTTP request, no dispatch debug flag today). Secondary for this ticket — primary repro is dispatch debug log.

⚠️ **Decision:** Add a **pure utils trace builder** (returns detail strings; no logging import in utils beyond existing config) and emit lines from **`_capture_rubric_vector_feedback`** + **`do_task`** pre-capture gate when **`debug=True`**. Do **not** change parse strictness or capture semantics.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/rubric_feedback.py` | `vector_reviews_pipeline_trace(...)` — structured step lines | utils |
| `src/core/agent.py` | Early-return debug; full pipeline trace in capture; skip debug when owner/cid missing | core |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

---

## Stage 1: Utils — pipeline trace builder (pure)

**Done when:** `vector_reviews_pipeline_trace` is importable and returns ordered detail strings for normalize, diagnostic parse, and hydrate steps; no logging side effects.

1. In **`src/utils/rubric_feedback.py`**, add:

   ```python
   def vector_reviews_pipeline_trace(
       *,
       raw_reviews: Any,
       expected_codes: frozenset[str],
       code_to_uuid: Dict[str, str],
       rubric_by_code: Dict[str, Dict[str, Any]],
       candidate_id: str = "",
       owner_task_key: str = "",
   ) -> List[str]:
   ```

   Emit lines in order (each a single **`debug_detail`-ready string**):

   | Step | Example line shape |
   |------|---------------------|
   | Context | `vector_reviews trace candidate={cid} owner={owner}` |
   | Raw input | `raw type={type} repr={truncated}` — truncate with **`…`** when longer than 120 chars |
   | Normalize | `normalize -> {n} lines` or `normalize -> None (reason=...)` |
   | Expected | `expected_codes={sorted} count={n}` |
   | Rubric keys | `rubric_lookup_keys={sorted(rubric_by_code.keys())} count={n}` |
   | Per line | `line[{i}] {compact} parse={ok\|fail code=...}` |
   | Diagnostic | `diagnostic reason={reason\|ok} parsed={...} missing={...} extra={...}` |
   | Hydrate | `hydrate rows={n}` then one **`format_hydrated_review_debug_line`** per row (max first 7 lines if more) |

2. Reuse existing **`normalize_vector_reviews_raw`**, **`parse_vector_reviews_diagnostic`**, **`parse_vector_review_string`**, **`hydrate_vector_review_strings`**, **`format_hydrated_review_debug_line`** — trace calls them; do not duplicate parse logic.

3. Update module docstring one-liner to mention AST-820 trace helper.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Single trace function wraps existing helpers |
| §3.3 imports | utils → config only; no data import |

---

## Stage 2: Capture + do_task — emit trace when debug=True

**Done when:** Debug **`evaluate_jd`** run logs pipeline trace on every capture outcome including early returns; Susan sees explicit skip reason when capture does not run.

1. In **`src/core/agent.py`**, **`_capture_rubric_vector_feedback`** — at function entry when **`debug=True`**:

   - Obtain **`dbg = _do_task_debug_logger(debug)`**.
   - Build **`rubric_by_code = _rubric_by_code_lookup(...)`** before early returns that need key counts (lazy: only when debug and about to log).
   - On **each early return**, emit **`debug_index`** once with outcome describing skip, then **`debug_detail`** with reason:
     - `status != success` → `skip reason=agent_performance.status={status}`
     - missing `batch_id` → `skip reason=empty batch_id`
     - empty `expected_codes` → `skip reason=empty_expected_codes candidate={candidate_id} owner={owner_task_key}`

2. After passing early gates, when **`debug=True`**:

   - **`debug_index(..., outcome="vector feedback capture start")`**
   - Call **`vector_reviews_pipeline_trace(...)`** with raw **`perf_dict.get("vector_reviews")`**, **`expected_codes`**, **`code_to_uuid`**, **`rubric_by_code`**, **`candidate_id`**, **`owner_task_key`**
   - For each trace line: **`dbg.debug_detail(line)`**

3. Keep existing AST-816 success/failure per-vector **`debug_index`** + **`format_hydrated_review_debug_line`** loops after trace (do not remove — trace is summary, loops are per-vector headers per §1.5.1 style D).

4. On **`insert_vector_feedback_rows`** exception when **`debug=True`**: add **`debug_detail(f"insert_vector_feedback_rows failed: {exc!r}")`** before existing **`logger.debug`**.

5. In **`do_task`** SUCCESS block (~line 2174), when **`envelope_snapshot`** has **`vector_reviews`** in **`agent_performance`**, **`debug=True`**, and **`not (_owner and _cid)`**:

   ```python
   dbg.debug_index(..., outcome="vector feedback capture skipped")
   dbg.debug_detail(f"skip reason=missing owner={_owner!r} candidate_id={_cid!r}")
   ```

6. Update **`_capture_rubric_vector_feedback` docstring** to reference AST-820 pipeline trace.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §1.5.1 debug | All new lines gated on `debug=True`; use `debug_index` + `debug_detail` only |
| §2.7 consult | Trace after envelope snapshot; no change to SUCCESS grading |
| §3.3 imports | core → utils only |

---

## Execution contract (build-child)

- Stages **1 → 2** in order; one commit per stage on epic worktree; publish each to **`origin/sub/AST-378/AST-820-uat-vector-feedback-hydration-debug-logging`**.
- Do **not** edit **`tests/`** or **`docs/test-bible/**`**.
- On ambiguity — **`🛑 Stage N blocked`** on **AST-378** parent; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — One utils trace helper and capture/do_task debug emission; no API or React changes.

**Conf:** `high` — Susan asked for observability only; AST-816 already has partial failure debug; gap is silent early returns and utils visibility.

**Risk:** `low` — Debug-only additions; no behavior change when `debug=False`.

---

## Self-review vs ASTRAL_CODE_RULES

| Section | Result |
|---------|--------|
| §1.3 DRY | Trace reuses AST-816 diagnostic/hydrate helpers |
| §1.5.1 debug | Gated on `debug=True`; no new production log paths |
| §3.3 imports | utils pure; core orchestrates emission |
| §3.5 naming | `vector_reviews_pipeline_trace` |

No unresolved rule conflicts.

---

## Build (Ada)

**Branch:** `origin/sub/AST-378/AST-820-uat-vector-feedback-hydration-debug-logging`  
**Code tip:** `b2713b2`  
**Stages:** 1 utils trace; 2 capture early-return + pipeline debug + do_task skip log.

| Stage | Summary |
|-------|---------|
| 1 | `vector_reviews_pipeline_trace`, `_normalize_failure_reason`, `_trace_repr_truncated` |
| 2 | Capture skip/start trace; `insert_vector_feedback_rows` debug; do_task missing owner/cid skip |

**Review stub:** Pending Radia (`review-child`).
