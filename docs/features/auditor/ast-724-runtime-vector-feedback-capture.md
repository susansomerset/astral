# AST-724 — Runtime vector feedback capture and lenient parse (Runtime Rubric Validation)

- **Linear:** [AST-724](https://linear.app/astralcareermatch/issue/AST-724/runtime-vector-feedback-capture-and-lenient-parse-runtime-rubric)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation)
- **Publish ref:** `origin/sub/AST-378/AST-724-runtime-vector-feedback-capture`
- **Depends on:** [AST-722](https://linear.app/astralcareermatch/issue/AST-722/rubric-storage-schema-backfill-and-feedback-config-runtime-rubric) schema + `RUBRIC_FEEDBACK_CONFIG`; [AST-723](https://linear.app/astralcareermatch/issue/AST-723/rubric-vector-read-write-cutover-and-rubric-vectors-token-runtime-rubric) table-backed rubric reads on `origin/ftr/AST-378-runtime-rubric-validation`

## Summary

Extend the **`agent_performance`** envelope on **every rubric-backed task** so the model may return **`vector_reviews`** (compact per-vector Relevance / Clarity / Verdict codes). When **`agent_performance.status` is `success`**, **`do_task` always completes normal task grading** — vector-feedback parse failures **do not** fail the run. Clean parse → **`vector_feedback`** rows (one per feedback type per vector per run, FK to **`rubric_vector`** UUID). Unparseable or missing feedback → raw text in **`agent_data`** block type **`FEEDBACK`**; **no** **`vector_feedback`** rows. Parsing validates codes against **`RUBRIC_FEEDBACK_CONFIG`** only. Debug runs log capture outcome per AST-538.

## Out of scope (explicit)

| Item | Owner ticket |
|------|----------------|
| Admin Vector Feedback UI | AST-725 |
| Mutating rubrics from Edit/Drop verdicts | — |
| Letter-grade / confidence validation changes | — |
| `TASK_CONFIG` `rubric_artifact` removal | AST-723+ |
| Prompt copy refresh in Manage Tasks DB rows (optional follow-up comment only) | — |

## Rubric-backed task set (systematic — not phased)

A task is **rubric-backed** when **`rubric_owner_task_key(task_key)`** returns non-`None` (**AST-723** helper in `config.py`). That covers all six **consumer** graders plus six **craft** rubric tasks:

| Consumer `task_key` | Craft `task_key` (same owner) |
|---------------------|-------------------------------|
| `prefilter_company` | `craft_prefilter_rubric` |
| `qualify_job_listings` | `craft_joblist_rubric` |
| `evaluate_jd` | `craft_jobdesc_rubric` |
| `grade_do` | `craft_do_rubric` |
| `grade_get` | `craft_get_rubric` |
| `grade_like` | `craft_like_rubric` |

⚠️ **Decision:** Use **`rubric_owner_task_key`** as the single gate — not `task_config["rubric_artifact"]` alone — so craft rubric tasks receive the same envelope instructions and capture path as consumer graders.

## Envelope contract (model output)

Inside **`agent_performance`** (sibling to **`status`** / **`failure_note`**), optional **`vector_reviews`**: a JSON **list of strings**, one per rubric vector **code** the model reviewed, compact form:

```
<CODE>R<relevance>C<clarity>V<verdict>
```

Example: `"RCROCRCVK"` → code `RC`, relevance `O`, clarity `C`, verdict `K`.

Allowed value letters come from **`RUBRIC_FEEDBACK_CONFIG`** (`A|O|S|R|N` for relevance/clarity; `K|E|D` for verdict). Codes are matched case-insensitively; stored values uppercase.

**Lenient rule:** Missing **`vector_reviews`**, wrong count, unknown code, malformed line, or invalid value letter → **unparseable** (not a task failure when **`status` is `success`**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `RUBRIC_FEEDBACK_PROMPT_SUFFIX` in `RUBRIC_FEEDBACK_CONFIG`; helper `is_rubric_backed_task(task_key)` | utils |
| `src/utils/rubric_feedback.py` | Pure parse/validate helpers for `vector_reviews` | utils |
| `src/data/database.py` | `insert_vector_feedback_rows`; `_store_feedback_block` helper pattern | data |
| `src/core/agent.py` | Prompt suffix injection; envelope snapshot; `_capture_rubric_vector_feedback`; SUCCESS-path hook; debug lines | core |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

## Stage 1: Config prompt suffix and pure parse helpers

**Done when:** `RUBRIC_FEEDBACK_PROMPT_SUFFIX` is importable; `parse_vector_reviews(...)` returns typed rows or `None` with safe error reason; unit-testable without DB.

1. In **`src/utils/config.py`**, extend **`RUBRIC_FEEDBACK_CONFIG`** with:

   ```python
   "prompt_suffix": (
       "Vector rubric review (agent_performance only — not agent_payload): include "
       "vector_reviews as a JSON list of strings. One string per rubric vector code "
       "you were given, format CODE + R + {A|O|S|R|N} + C + {A|O|S|R|N} + V + {K|E|D} "
       "(example: \"Q1RAOCVK\"). agent_performance.status reflects only whether you "
       "could perform the task — never \"failure\" because grades or verdicts were harsh."
   ),
   ```

2. Add **`is_rubric_backed_task(task_key: str) -> bool`** in the same file:

   ```python
   def is_rubric_backed_task(task_key: str) -> bool:
       return rubric_owner_task_key(task_key) is not None
   ```

3. Create **`src/utils/rubric_feedback.py`** with:

   - **`_VECTOR_REVIEW_RE`** — compiled once: `^([A-Za-z0-9]+)R([AOSRN])C([AOSRN])V([KED])$` (case-insensitive flags on input normalize to upper).
   - **`parse_vector_review_string(line: str) -> Optional[Tuple[str, Dict[str, str]]]`** — returns `(code_upper, {"relevance": "O", "clarity": "C", "verdict": "K"})` or `None`.
   - **`parse_vector_reviews(raw_reviews: Any, expected_codes: frozenset[str], code_to_uuid: Dict[str, str]) -> Optional[List[Dict[str, str]]]`**:
     - `raw_reviews` must be a non-empty `list` of strings.
     - Every **`expected_codes`** must appear exactly once in parsed output (no extras, no missing).
     - Each code must exist in **`code_to_uuid`**.
     - Each relevance/clarity/verdict value must be in **`RUBRIC_FEEDBACK_CONFIG`** type/value sets.
     - Return list of dicts: `{rubric_vector_uuid, code, relevance, clarity, verdict}` (flat per vector — expansion to DB rows happens in data layer).
     - On any failure: return **`None`** (caller treats as unparseable).

4. Add **`format_vector_reviews_raw(perf: dict) -> str`** — JSON-serialize the `vector_reviews` key if present, else serialize whole **`agent_performance`** dict (for FEEDBACK block body).

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.1 config | Prompt suffix + validation codes in `config.py` |
| §3.3 imports | `rubric_feedback.py` imports utils/config only |
| §1.3 DRY | Single parse module |

---

## Stage 2: Data layer — vector_feedback inserts and FEEDBACK block

**Done when:** `insert_vector_feedback_rows` writes N×3 rows per clean parse; `_store_feedback_block` persists FEEDBACK agent_data; `_ensure_vector_feedback_table` called on first insert.

1. In **`src/data/database.py`**, add **`_store_feedback_block(entity_type, task_key, batch_id, body: str, *, index: Optional[str]) -> str`** — mirror **`_store_response_block`** in `agent.py` but call **`save_agent_data(..., block_type="FEEDBACK", ...)`** with id prefix `{batch_id}-feedback-{hash}`.

   ⚠️ **Decision:** Keep FEEDBACK store helper in **data** layer as thin wrapper around **`save_agent_data`**; **`agent.py`** calls it to respect layer rules (core → data).

2. Add **`store_feedback_block(...) -> str`** public wrapper with **`_run_with_retry`**.

3. Add **`insert_vector_feedback_rows(rows: List[Dict[str, str]]) -> None`** where each input row has keys: `rubric_vector_uuid`, `candidate_id`, `batch_id`, `task_key`, `feedback_type`, `value`, optional `agent_data_id`.

   - Call **`_ensure_vector_feedback_table(conn)`** before insert loop.
   - One INSERT per row: `vector_feedback_id = str(uuid.uuid4())`, `created_at = _utc_now()`.
   - Expand each parsed vector dict into **three** rows (`relevance`, `clarity`, `verdict` feedback_types).

4. Add **`list_rubric_vector_uuid_by_code(candidate_id, owner_task_key) -> Dict[str, str]`** — `SELECT code, rubric_vector_uuid FROM rubric_vector WHERE candidate_id=? AND task_key=? AND current=1`; return uppercased code → uuid map (data-layer only; no embedded-vector merge).

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §1.1 inventory | Uses existing `vector_feedback` table |
| §2.4 batch | `batch_id` on each row |
| §3.3 imports | data → utils only |

---

## Stage 3: do_task capture hook, prompt injection, debug logging

**Done when:** Rubric-backed JSON tasks append prompt suffix; on SUCCESS with `agent_performance.status == success`, clean parse writes `vector_feedback` rows and debug logs per vector; unparseable writes FEEDBACK block + debug “raw FEEDBACK stored”; non-rubric tasks unchanged; encoded consult envelope path covered.

1. In **`src/core/agent.py`**, add **`_rubric_feedback_owner_and_candidate(task_key, cd, ctx) -> Tuple[Optional[str], Optional[str]]`** returning `(owner_task_key, candidate_id)` from `rubric_owner_task_key(task_key)` and `cd.get("_astral_candidate_id")` or `ctx` candidate id.

2. Add **`_capture_rubric_vector_feedback(*, task_key, owner_task_key, candidate_id, batch_id, entity_type, index, perf: dict, debug: bool, prompt_blocks: list) -> None`** in **`agent.py`**:
   - If **`_agent_performance_status(perf) != "success"`**: return immediately (no FEEDBACK, no rows).
   - Load **`expected_codes`** from **`rubric_criteria_for_task(candidate_id, owner_task_key)`** — use criterion `code` values uppercased; skip capture when expected set is empty (no rubric loaded).
   - Load **`code_to_uuid`** via **`database.list_rubric_vector_uuid_by_code(candidate_id, owner_task_key)`**.
   - Call **`parse_vector_reviews(perf.get("vector_reviews"), frozenset(expected_codes), code_to_uuid)`**.
   - **Clean parse:** call **`insert_vector_feedback_rows`**; append **`{"type": "FEEDBACK", "id": ...}`** only when storing raw — for clean parse, optional omit FEEDBACK block (rows are the grain). When debug: **`debug_index`** header + per-vector **`debug_detail`** lines (`code R/O C/O V/K recorded`).
   - **Unparseable:** **`store_feedback_block`** with **`format_vector_reviews_raw(perf)`**; append FEEDBACK ref to **`prompt_blocks`**; when debug: **`debug_detail`** `vector feedback unparseable — stored raw FEEDBACK block`.

3. Add **`_agent_performance_status(perf: Any) -> Optional[str]`** — normalize dict `perf["status"]`, legacy string `"success"`/`"failure"`, or `None`.

4. **Envelope snapshot (before unwrap):** Immediately after provider returns and **`result["parsed_response"]`** is set (~line 1684), when **`is_rubric_backed_task(task_key)`** and parsed is a `dict` with **`agent_performance`** key, set **`envelope_snapshot = copy.deepcopy(parsed)`** on the local stack (do not mutate after unwrap at ~1825).

5. **Prompt injection:** After **`user_content = resolve_tokens(...)`** (~1402), when rubric-backed:

   ```python
   suffix = RUBRIC_FEEDBACK_CONFIG.get("prompt_suffix") or ""
   if suffix:
       user_content = (user_content.rstrip() + "\n\n" + suffix).strip()
   ```

   Apply the same suffix to **`nocache_content`** when that segment carries the task instructions and `user_content` is empty (check assembled segments — at minimum **user_prompt** path must include suffix).

6. **SUCCESS hook:** At **`# SUCCESS: store decoded/validated response block`** (~1964), **before** RESPONSE store, when **`envelope_snapshot`** exists:

   ```python
   perf = envelope_snapshot.get("agent_performance") if isinstance(envelope_snapshot, dict) else None
   if perf is not None:
       _capture_rubric_vector_feedback(...)
   ```

7. **Encoded consult path:** **`envelope_snapshot`** must be captured **before** `_normalize_rubric_task_response` / `_decode_payload` replaces `parsed` with flat `jobs[]` shape — same snapshot point handles both JSON envelope and strict batch consult keys.

8. **Do not** add vector-feedback validation to **`_validate_response_schema`** — lenient contract forbids failing task on bad reviews.

9. **External providers (`anthropic.py`, `deepseek.py`):** **No changes** — full JSON envelope already returned in **`parsed_response`**.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §1.5.1 debug | `debug_index` / `debug_detail` only when `debug=True` |
| §2.7 consult | Capture runs after consult normalize on SUCCESS, not on normalize failure |
| §3.3 imports | core → data + utils; no ui |

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — New utils parse module, data insert path, and `do_task` envelope capture across all twelve rubric-backed task keys.

**Conf:** `Medium` — Envelope + lenient parse contract is specified in parent/AST-722 config; edge cases are encoded vs JSON paths and empty rubric sets (skip capture).

**Risk:** `Medium` — Incorrect hook placement could drop reviews or double-store; mitigation is envelope snapshot before unwrap/decode and explicit SUCCESS-only capture when `status == success`.

## Self-Review vs ASTRAL_CODE_RULES

| Section | Assessment |
|---------|------------|
| §1.1 Scope | Uses inventory tables/blocks only; no new tables |
| §1.3 DRY | Parse in `rubric_feedback.py`; owner gate via `rubric_owner_task_key` |
| §2.1 Config | Prompt suffix + value codes in `RUBRIC_FEEDBACK_CONFIG` |
| §2.4 Batch | `batch_id` on every `vector_feedback` row |
| §2.6 State machine | No job/company state transitions |
| §3.3 Imports | utils pure; data persists; core orchestrates |
| §3.5 Naming | snake_case; FEEDBACK block matches `BLOCK_TYPES` |

No unresolved rule conflicts.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-378/AST-724-runtime-vector-feedback-capture` (pending)  
**Built:** 2026-06-18

**Commits:** `9b22328` (config + parse helpers), `b37343e` (data layer inserts + FEEDBACK store), `a4c98e7` (do_task capture hook + prompt suffix)

**Publish ref:** `origin/sub/AST-378/AST-724-runtime-vector-feedback-capture`
