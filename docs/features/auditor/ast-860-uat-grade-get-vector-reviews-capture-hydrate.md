# AST-860 — UAT: grade_get RACOVK vector_reviews still not captured or hydrated

- **Linear:** [AST-860](https://linear.app/astralcareermatch/issue/AST-860/uat-grade-get-racovk-vector-reviews-still-not-captured-or-hydrated)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation) — Runtime Rubric Validation
- **Publish ref:** `origin/sub/AST-378/AST-860-uat-grade-get-vector-reviews-capture-hydrate`
- **Shipped baseline:** [AST-859](https://linear.app/astralcareermatch/issue/AST-859/uat-fix-vector-reviews-prompt-example-racovk) RACOVK prompt example; [AST-820](https://linear.app/astralcareermatch/issue/AST-820/uat-add-debug-logging-to-vector-feedback-hydration-path) pipeline trace; [AST-816](https://linear.app/astralcareermatch/issue/AST-816/uat-compact-vector-reviews-still-not-hydrating-on-evaluate-jd) normalize/diagnostic capture

## Summary

Susan UAT 2026-07-10 23:12 (post AST-859): **`grade_get`** batch SUCCESS now returns **RACOVK-shaped** compact `vector_reviews` (e.g. `ATRACOVK`, `DORACOVK`, …) in the raw response preview, but **vector feedback is still not captured, persisted, or hydrated** — no AST-820 capture start/skip/hydrate lines, no Admin rows, no FEEDBACK decode. This UAT fix closes the **`grade_get` Pattern-A batch** gap: ensure envelope snapshot + capture preconditions match what the model returns, align **`expected_codes`** with the rubric the prompt actually uses, and guarantee **`astral_candidate_id`** reaches **`do_task`** from **`_run_batch_consult`**.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Revert AST-859 `prompt_suffix` RACOVK example | — |
| `grade_get` provider `max_tokens` / truncated responses | separate issue |
| Admin UI column changes (AST-808 / AST-809 shipped) | — unless capture still empty after product fix |
| Retroactive rewrite of stored FEEDBACK blocks | — |

## Root cause (plan-time)

| # | Failure mode | Evidence |
|---|--------------|----------|
| 1 | **Silent capture omission** | `do_task` SUCCESS hook only enters capture when `envelope_snapshot.get("agent_performance") is not None` (~line 2403). If `agent_performance` is missing from the snapshot dict (or never normalized before snapshot), **no** capture and **no** AST-820 skip line — only raw `response_preview` shows `vector_reviews`. |
| 2 | **`agent_performance.status` absent** | `_capture_rubric_vector_feedback` returns early when `_agent_performance_status(perf) != "success"` (~line 1253). Encoded **`grade_get`** envelopes may include `vector_reviews` without `status`; capture skips with a skip line — Susan may not see full pipeline trace. |
| 3 | **`empty_expected_codes` / code-set mismatch** | Capture uses `expected_codes = frozenset(code_to_uuid.keys())` from **`list_rubric_vector_uuid_by_code` only** (~line 1275–1276). Consult prompt vectors come from **`rubric_criteria_for_task`** in **`_run_batch_consult`** (~line 1029). If DB-backed UUID map is empty or code set ≠ model's 11 codes (`AT`, `CR`, `DO`, …), capture skips (`empty_expected_codes`) or lenient-fails parse (`missing_codes` / `extra_codes`) without persisting **`vector_feedback`** rows. Ticket repro step 4 asks to compare **`rubric_vector`** codes for owner **`grade_get`** vs parsed codes. |
| 4 | **Batch ctx candidate wiring** | Capture needs **`_owner and _cid`** (~line 2423). Dispatcher **`ctx`** from **`get_candidate`** should carry **`astral_candidate_id`**, but **`_run_batch_consult`** does not explicitly inject it into **`task_ctx`** (~line 1032–1033). Defensive wiring prevents batch regressions when **`ctx`** shape drifts. |

⚠️ **Decision:** Fix product capture path only — do **not** relax strict `parsed_codes == expected_codes` equality (AST-724 lenient contract). When rubric count mismatches, store raw **FEEDBACK** + full debug trace; Susan's case expects **clean parse** when DB codes match the 11 GET vectors.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Envelope normalize before snapshot; status default; expected_codes ∩ criteria; silent-skip debug | core |
| `src/core/consult.py` | Inject `astral_candidate_id` (+ `candidate_data` when present) into `task_ctx` in `_run_batch_consult` | core |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

---

## Stage 1: Envelope normalization and capture preconditions (`agent.py`)

**Done when:** For a synthetic `grade_get` envelope dict with `agent_performance: {"vector_reviews": ["ATRACOVK"]}` (no `status`), manual `do_task` SUCCESS path calls `_capture_rubric_vector_feedback` and debug shows capture start or explicit skip (never silent); `expected_codes` uses criteria ∩ UUID map per AST-724 Resolution.

1. In **`src/core/agent.py`**, add **`_normalize_rubric_envelope_for_capture(parsed: dict) -> dict`** (module-level, near `_agent_performance_status`):

   - Input: top-level parsed envelope **before** `agent_payload` unwrap (~line 2130).
   - If not a `dict`, return unchanged.
   - Ensure **`agent_performance`** is a `dict` (replace `None` with `{}`).
   - If **`vector_reviews`** present at **top level** and missing under **`agent_performance`**, copy into **`agent_performance["vector_reviews"]`** (do not delete top-level key — harmless).
   - If **`agent_performance`** has non-empty **`vector_reviews`** (after normalize) and **`status`** is missing/blank, set **`agent_performance["status"] = "success"`** (lenient — only when reviews present; do not override explicit `"failure"`).
   - Return the mutated dict (mutate in place is OK).

2. In **`do_task`**, immediately **before** the existing **`envelope_snapshot`** assignment (~line 2130):

   ```python
   if is_rubric_backed_task(task_key) and isinstance(parsed, dict):
       parsed = _normalize_rubric_envelope_for_capture(parsed)
       result["parsed_response"] = parsed
   ```

   Run **after** `coerce_grades_encoded_json_parse` and strict envelope re-check (~lines 2124–2128) so normalized shape still passes **`_strict_encoded_batch_consult_envelope_err`**.

3. In **`_capture_rubric_vector_feedback`**, replace **`expected_codes`** computation (~lines 1275–1276):

   ```python
   from src.core.candidate import rubric_criteria_for_task

   code_to_uuid = list_rubric_vector_uuid_by_code(candidate_id, owner_task_key)
   criteria_codes = frozenset(
       str(c.get("code")).strip().upper()
       for c in rubric_criteria_for_task(candidate_id, owner_task_key)
       if isinstance(c, dict) and c.get("code")
   )
   uuid_codes = frozenset(code_to_uuid.keys())
   expected_codes = criteria_codes & uuid_codes
   ```

   Keep **`empty_expected_codes`** skip when **`not expected_codes`**. Extend debug skip detail to include `criteria_codes={sorted(criteria_codes)} uuid_codes={sorted(uuid_codes)}` so Susan can see rubric/DB drift on staging.

4. In **`do_task` SUCCESS hook** (~lines 2401–2422), when **`envelope_snapshot`** is not `None` but **`_perf is None`**:

   - If **`debug`** and **`isinstance(envelope_snapshot, dict)`** and **`envelope_snapshot.get("vector_reviews") is not None`**, emit **`do_task`** debug_index outcome **`vector feedback capture skipped`** + detail **`skip reason=agent_performance missing after normalize`**.
   - (Covers residual silent path after Stage 1 normalize.)

5. Do **not** change **`parse_vector_review_string`** regex or lenient run-success semantics.

6. Manual verify on epic worktree (no commit script):

   ```python
   from src.core.agent import _normalize_rubric_envelope_for_capture, _capture_rubric_vector_feedback
   env = {"agent_payload": "0|ATX3", "agent_performance": {"vector_reviews": ["ATRACOVK"]}}
   out = _normalize_rubric_envelope_for_capture(env)
   assert out["agent_performance"]["status"] == "success"
   assert out["agent_performance"]["vector_reviews"] == ["ATRACOVK"]
   ```

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.7 consult | Normalize before snapshot; capture still lenient |
| §1.5.1 debug | All new lines behind `debug=True` |
| §3.3 imports | `agent.py` may import `rubric_criteria_for_task` from `candidate` (existing lazy-import pattern) |

---

## Stage 2: `grade_get` batch ctx hardening (`consult.py`)

**Done when:** `_run_batch_consult` always passes `astral_candidate_id` on `task_ctx` when dispatcher `ctx` has it; `do_task` debug line `candidate=` is non-empty for `grade_get` batch runs.

1. In **`src/core/consult.py`**, inside **`_run_batch_consult`** after **`vector_labels`** build (~line 1030), before **`do_task`**:

   ```python
   cid = _candidate_id_from_ctx(ctx)
   task_ctx = {**(ctx or {}), "batch_size": len(jobs), "batch_entities": jobs, "vector_labels": vector_labels}
   if cid:
       task_ctx["astral_candidate_id"] = cid
   if ctx and ctx.get("candidate_data") is not None:
       task_ctx["candidate_data"] = ctx["candidate_data"]
   ```

   Replace the existing one-liner `task_ctx = {**ctx, ...} if ctx else {...}` with the block above.

2. Do **not** change **`assemble_fn`**, **`process_fn`**, or decode paths.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §2.7 consult | Single choke-point for Pattern-A batch consult |
| Scope | `consult.py` only — no dispatcher edits |

---

## Execution contract (build-child)

- **Two stages**, two commits on epic worktree; publish each to **`origin/sub/AST-378/AST-860-uat-grade-get-vector-reviews-capture-hydrate`**.
- Do **not** edit **`tests/`** or **`docs/test-bible/**`**.
- On ambiguity — **`🛑 Stage N blocked`** on **AST-378** parent; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — `agent.py` capture hook + `consult.py` batch ctx wiring.

**Conf:** `Medium` — Susan's repro isolates `grade_get` after RACOVK prompt fix; code review shows multiple skip/silent paths; exact staging failure mode (empty DB vs status vs silent snapshot) confirmed at build via debug strings.

**Risk:** `Medium` — Touches shared capture hook for all rubric-backed tasks; changes are guarded (normalize only when rubric-backed; expected_codes intersection already specified in AST-724 Resolution).

---

## Self-review vs ASTRAL_CODE_RULES

| Section | Result |
|---------|--------|
| §2.7 consult | Batch ctx + envelope normalize align consult prompt with capture |
| §1.5.1 debug | Explicit skip reasons for prior silent paths |
| §3.3 imports | core → candidate/data/utils only |

No unresolved rule conflicts.

---

## Review (Radia)

**Branch:** `origin/sub/AST-378/AST-860-uat-grade-get-vector-reviews-capture-hydrate`  
**Built tip:** `4e73031` — `agent.py` envelope normalize + criteria ∩ UUID `expected_codes` + silent-skip debug; `consult.py` batch `astral_candidate_id` wiring.

*Awaiting Radia review after Tests Passed.*
