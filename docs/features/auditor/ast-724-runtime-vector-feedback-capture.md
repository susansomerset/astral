<!-- linear-archive: AST-724 archived 2026-07-29 -->

## Linear archive (AST-724)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-724/runtime-vector-feedback-capture-and-lenient-parse-runtime-rubric  
**Status at archive:** Archive  
**Project:** Astral Auditor  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-378 — Runtime Rubric Validation  
**Blocked by / blocks / related:** parent: AST-378

### Description

## What this implements

Extend the agent performance envelope so every rubric-backed task requests per-vector feedback (Relevance, Clarity, Verdict codes). When `agent_performance.status=success`, always process **agent_payload** — feedback parse failures do not fail the run. Unparseable feedback → raw text in **agent_data** **FEEDBACK** block, no **vector_feedback** rows. Clean parse → one **vector_feedback** row per feedback type per vector per run, linked to **rubric_vector** UUID. Parsing stays dumb; validate codes against config. Debug logs per AST-538 when debug=True.

## Acceptance criteria

1. Every rubric-backed agent task returns per-vector feedback when the model complies, using config-allowed value codes.
2. When `agent_performance.status = success` but vector feedback is missing or unparseable, the run **still succeeds** for task payload purposes; raw feedback is stored in **agent_data** **FEEDBACK**; **no** **vector_feedback** rows are created for that run.
3. When vector feedback parses cleanly, **vector_feedback** rows are persisted with correct **rubric_vector** UUID, candidate, task run identifier, and one row per feedback type per vector.
4. With debug enabled, rubric-backed runs log each vector feedback found and recorded, or log that raw FEEDBACK was stored due to parse failure.

## Boundaries

Does not build Admin UI (sibling Katherine ticket). Does not mutate rubrics from Edit/Drop verdicts. Does not change task letter-grade validation.

## Notes for planning

Touches [agent.py](<http://agent.py>), external providers, config prompts/envelope instructions. All rubric-backed task keys systematically — not a phased subset.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-378-runtime-rubric-validation`, child `sub/AST-378/<identifier>-runtime-vector-feedback-capture`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-18T04:20:15.079Z
**Diff:** `origin/dev...origin/sub/AST-378/AST-724-runtime-vector-feedback-capture` (code `a609a04`, doc `b18ba06`)
**Doc:** `docs/features/auditor/ast-724-runtime-vector-feedback-capture.md` § Review (Radia)

*Note: three-dot diff includes sibling AST-722/723 not yet on origin/dev.*

### What's solid
- Stages 1–3: `prompt_suffix`, `rubric_feedback.py` parse, data insert/FEEDBACK store, `do_task` suffix + pre-unwrap `envelope_snapshot` + SUCCESS-only capture.
- Lenient contract honored — parse failures → FEEDBACK only; task grading unaffected.
- `_ensure_vector_feedback_table` on first insert (AST-722 discuss closed).
- Betty manifest aligns.

### discuss
1. **Prefilter embedded RC:** `expected_codes` from `rubric_criteria_for_task` includes embedded RC; `list_rubric_vector_uuid_by_code` is DB-only → RC has no UUID → prefilter reviews likely always unparseable (raw FEEDBACK). Confirm: exclude embedded-only codes from expected set, or require RC in table.
2. **Debug contract (§1.5.1):** clean parse uses one `debug_index` for N vectors; unparseable emits `debug_detail` without index header — optional polish in resolve.

### advisory
- Capture store/insert failures log at `logger.debug` only (lenient by design).
- Diff baseline includes AST-722/723 stack until ftr → dev.

**Verdict:** Approve for `resolve-child`. Resolve prefilter RC discuss before UAT sign-off on prefilter feedback.

#### betty — 2026-06-18T04:18:04.516Z
## QA test manifest (AST-724)

**Publish ref:** `origin/sub/AST-378/AST-724-runtime-vector-feedback-capture` @ `a609a04` (`merge-tests(AST-724): origin/tests e24f5b6`)

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_rubric_feedback.py \
  tests/component/utils/test_config.py::TestAst724RubricBackedTask \
  tests/component/data/database/test_rubric_vectors.py::TestAst724VectorFeedbackRows \
  tests/component/core/test_agent.py::TestAst724VectorFeedbackCapture \
  -q
```

**Manifest:**

1. `tests/component/utils/test_rubric_feedback.py` — `TestParseVectorReviewString`, `TestParseVectorReviews`, `TestFormatVectorReviewsRaw` (lenient `vector_reviews` parse; format `CODE` + `R` + rel + `C` + cla + `V` + ver, e.g. `G1RACOVK`)
2. `tests/component/utils/test_config.py::TestAst724RubricBackedTask` — `is_rubric_backed_task`, `prompt_suffix` in `RUBRIC_FEEDBACK_CONFIG`
3. `tests/component/data/database/test_rubric_vectors.py::TestAst724VectorFeedbackRows` — `list_rubric_vector_uuid_by_code`, `insert_vector_feedback_rows`, `store_feedback_block`
4. `tests/component/core/test_agent.py::TestAst724VectorFeedbackCapture` — `_agent_performance_status`, owner/candidate resolution, clean parse → rows, unparseable → FEEDBACK block, non-success skip

**Bible shasums (`origin/sub/AST-378/AST-724-runtime-vector-feedback-capture`):**

- `docs/test-bible/utils/rubric_feedback.md`: `a69e25462bb74b5c9ae31e1d0f3efe21f2aaa23a`
- `docs/test-bible/data/database/rubric_vectors.md`: `c1cb7ac40075be24251d281b90f220fdf3c6d83a`
- `docs/test-bible/core/agent.md`: `a591b238b1e8b872fc3e099476b3eca5d8c790ec`
- `docs/test-bible/utils/config.md`: `b3a4dfe112bfa2291eb8584a2960c979add78f2e`

— Betty

#### ada — 2026-06-18T04:11:25.794Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-378/AST-724-runtime-vector-feedback-capture/docs/features/auditor/ast-724-runtime-vector-feedback-capture.md

Publish ref: `origin/sub/AST-378/AST-724-runtime-vector-feedback-capture` @ `7392b8a`

**Self-assessment**
- **Scope:** MAJOR-CHANGE — new `rubric_feedback.py` parse module, `vector_feedback` insert path, and `do_task` envelope capture across all twelve rubric-backed task keys (consumer + craft).
- **Conf:** Medium — envelope + lenient parse contract is specified in parent/AST-722; hook placement (snapshot before unwrap) is the main execution risk, mitigated in-plan.
- **Risk:** Medium — wrong SUCCESS-hook timing could drop reviews or store FEEDBACK when rows should persist; plan pins snapshot before `_normalize_rubric_task_response` / unwrap.

---

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

**Diff:** `origin/dev...origin/sub/AST-378/AST-724-runtime-vector-feedback-capture` (code tip `a609a04`)  
**Reviewed:** 2026-06-18  
**Note:** Three-dot diff includes sibling **AST-722/723** commits not yet on `origin/dev`; review scoped to AST-724 Stages 1–3.

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | `prompt_suffix` + `is_rubric_backed_task`; pure `rubric_feedback.py` parse module; `store_feedback_block` + `insert_vector_feedback_rows` + `list_rubric_vector_uuid_by_code`; `do_task` suffix injection, pre-unwrap `envelope_snapshot`, SUCCESS-only capture hook. |
| Lenient contract | Parse failures store FEEDBACK block only; task grading unaffected; no schema validation on `vector_reviews`; non-`success` agent_performance skips capture. |
| §3.3 layers | `rubric_feedback.py` → utils/config only; data persists; core orchestrates; no external provider changes. |
| Hook placement | `envelope_snapshot` deep-copied before `agent_payload` unwrap and `_normalize_rubric_task_response` / `_decode_payload`. |
| AST-722 follow-up | `_ensure_vector_feedback_table` invoked on first insert path. |
| Tests / bible | Betty manifest covers parse helpers, capture clean/unparseable/skip paths, config gate (`test_rubric_feedback.py`, `TestAst724VectorFeedbackCapture`). |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| discuss | `_capture_rubric_vector_feedback` + `prefilter_company` | `expected_codes` from `rubric_criteria_for_task` includes embedded **RC**; `list_rubric_vector_uuid_by_code` is DB-only (per plan). RC has no UUID unless also in `rubric_vector` → prefilter reviews always unparseable → raw FEEDBACK only. Confirm: exclude embedded-only codes from expected set, or require RC row in table. |
| discuss | `_capture_rubric_vector_feedback` debug path | Clean parse uses one `debug_index(1, total=N)` then multiple `debug_detail` lines — §1.5.1 prefers per-vector index headers when `N > 1`. Unparseable path emits `debug_detail` without a preceding index header. |
| advisory | `_capture_rubric_vector_feedback` | `except Exception` on store/insert logs at `logger.debug` only — lenient by design; operators won't see capture DB failures unless debug/log level raised. |
| advisory | `store_feedback_block` | No `_run_with_retry` wrapper (relies on `save_agent_data` internals) — minor vs plan prose. |
| advisory | Diff baseline | Full AST-722/723 stack in `origin/dev...` until ftr → dev. |

### Recommended actions

| Priority | Action |
|----------|--------|
| resolve | Decide prefilter embedded-RC vs `expected_codes` / UUID map; adjust capture or document FEEDBACK-only expectation for prefilter. |
| resolve | Optional: per-vector `debug_index` loop when `len(parsed_rows) > 1`; index header before unparseable detail. |
| AST-725 | Admin UI reads `vector_feedback` rows + FEEDBACK fallback. |

**Verdict:** Approve for `resolve-child`. No functional fix-now blockers; prefilter embedded-RC discuss should be resolved before UAT sign-off on prefilter feedback.

---

## Resolution (Ada)

**Date:** 2026-06-18  
**Driven by:** Radia review discuss items #1–2.

**Changes:**

1. **Prefilter embedded RC:** `expected_codes` is now the intersection of `rubric_criteria_for_task` codes and `list_rubric_vector_uuid_by_code` keys. Embedded-only vectors without a `rubric_vector` row (e.g. RC before backfill) are excluded from the required parse set; capture skips when no DB-backed codes exist.
2. **Debug contract (§1.5.1):** Clean parse emits per-vector `debug_index` headers (`index` 1..N); unparseable path adds an index header before the `debug_detail` line.

**Publish:** `resolve(AST-724)` on `origin/sub/AST-378/AST-724-runtime-vector-feedback-capture`.

## Bug: AST-1384 — craft_* must not emit vector_reviews feedback

### As-is

On a `craft_*` rubric run (e.g. `craft_get_rubric` for candidate `abrams`), the model returns authored `agent_payload.criteria` **and** feedback-style `agent_performance.vector_reviews` (compact codes like `TRRACAVK`). Craft is taught to emit those reviews because AST-724 gated the feedback `prompt_suffix` (and SUCCESS capture) on `is_rubric_backed_task`, which is true for all twelve keys — six consumer graders **plus** six craft authors via `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` / `rubric_owner_task_key`.

### To-be

`craft_*` rubric responses deliver complete `agent_payload.criteria` without emitting rubric-feedback `vector_reviews`. Grade/evaluate consumers still request and capture per-vector feedback as today. Craft SUCCESS does not persist `vector_feedback` rows for the craft run.

### Repro

1. Run UI/API generate for `craft_get_rubric` on candidate `abrams` (or any live candidate with Get craft).
2. Inspect the SUCCESS envelope / pending craft generation payload.
3. Observe: `agent_payload.criteria` present **and** `agent_performance.vector_reviews` populated with compact `CODE`+`R`+rel+`C`+cla+`V`+ver strings.
4. After fix: same run yields complete criteria; `vector_reviews` absent (or not taught/captured); no new `vector_feedback` rows keyed to that craft `task_key` / batch.

Explicitly **not** a `max_tokens` / truncation failure (Susan).

### Root cause

AST-724's single gate **`is_rubric_backed_task(task_key) := rubric_owner_task_key(task_key) is not None`** intentionally treated craft and consumer as the same envelope+capture surface (plan Decision under "Rubric-backed task set"). That was wrong for craft's job: craft **authors** criteria; feedback compact codes belong only on **grade/evaluate** consumers that score against an existing rubric.

Two coupled effects in `do_task` (`src/core/agent.py`):

1. **Teach:** when `is_rubric_backed_task`, append `RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]` → model emits `vector_reviews`.
2. **Capture:** same gate takes `envelope_snapshot` and, on SUCCESS, calls `_capture_rubric_vector_feedback` → may insert `vector_feedback` / FEEDBACK blocks for craft runs.

`rubric_owner_task_key` itself must stay dual-purpose (craft still resolves which owner rubric it authors). Only the **vector-feedback request + capture** path must exclude craft.

### Proposed change

Concrete enough for `make-fix` — no judgment calls:

1. **`src/utils/config.py`** — add helper next to `is_rubric_backed_task`:

   ```python
   def is_vector_feedback_task(task_key: str) -> bool:
       """True when task should request/capture vector_reviews (consumers only; not craft)."""
       if task_key in CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY:
           return False
       return rubric_owner_task_key(task_key) is not None
   ```

   - Leave **`is_rubric_backed_task`** unchanged (still True for craft — owner/rubric identity).
   - Leave **`rubric_owner_task_key`** / **`task_keys_for_rubric_owner`** unchanged (Admin historical filter may still see old craft `task_key` rows; craft simply stops writing new ones).
   - Do **not** change `RUBRIC_FEEDBACK_CONFIG` value codes or `prompt_suffix` text; only who receives the suffix.

2. **`src/core/agent.py`** — switch the three feedback-path gates from `is_rubric_backed_task` to `is_vector_feedback_task`:

   | Site | Current | Change |
   |------|---------|--------|
   | Prompt suffix injection (~after `resolve_tokens`) | `if is_rubric_backed_task(task_key):` append suffix | `if is_vector_feedback_task(task_key):` |
   | `_normalize_rubric_envelope_for_capture` before snapshot | `if is_rubric_backed_task(...)` | `if is_vector_feedback_task(...)` |
   | `envelope_snapshot = copy.deepcopy(parsed)` | `if is_rubric_backed_task(...) and "agent_performance" in parsed` | `if is_vector_feedback_task(...)` same condition |

   With snapshot absent for craft, the existing SUCCESS `_capture_rubric_vector_feedback` block no-ops automatically — no separate early-return required inside the capture helper (optional defense-in-depth `if not is_vector_feedback_task: return` is fine but not required if the three gates above are complete).

3. **Import:** add `is_vector_feedback_task` to the existing config import list in `agent.py`; keep `is_rubric_backed_task` only if still referenced elsewhere in that file after the swap (else drop unused import).

4. **Out of scope (do not touch):** `CRAFT_RUBRIC_MAX_TOKENS` / truncation budget; Admin Vector Feedback UI; letter-grade / confidence validation; `rubric_feedback.py` parse rules; consumer grader prompt/capture behavior.

### Blast radius

| Area | Impact |
|------|--------|
| `grade_*` / `evaluate_*` / `prefilter_company` / `qualify_job_listings` | Unchanged — still `is_vector_feedback_task` True → suffix + capture. |
| All keys in `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` (incl. `craft_evaluate_meteorite_rubric`) | Stop suffix + snapshot + capture. |
| `is_rubric_backed_task` callers / bible | Semantics unchanged; Betty may add coverage for the new helper and craft exclusion. |
| `task_keys_for_rubric_owner` / Admin AST-725 | Unchanged expansion; historical craft-run feedback rows remain queryable; no new craft rows after fix. |
| Tests that assumed craft receives `prompt_suffix` or capture | Likely need Betty revise (`fix-board` TESTS) — engineer does not patch `tests/`. |

### What must still hold

From AST-724 / parent AST-1378 AC (do not regress):

1. Consumer rubric-backed SUCCESS still requests `vector_reviews` via `prompt_suffix` and captures clean parses into `vector_feedback` (lenient: unparseable → FEEDBACK block only; never fails the task).
2. Non-`success` `agent_performance` still skips capture.
3. Craft SUCCESS still returns complete `agent_payload.criteria` under existing craft schema; craft `max_tokens` floor unchanged.
4. `rubric_owner_task_key(craft_*)` still resolves the consumer owner for artifact authorship / pending craft paths.
5. No Admin UI redesign; no letter-grade scoring math changes.

## Review (Radia) — AST-1384

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | No confidence validation paths touched |
| `astral.agent.do-task-delegation` | scoped | conforms | Three `do_task` gates swapped; capture still via existing helper |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector validation logic changed |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch-id handling changed |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch-id format logic |
| `astral.batch.claim-process-release` | scoped | not-applicable | No dispatcher/claim paths |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No entity-agent-response queries |
| `astral.config.config-source-of-truth` | scoped | conforms | New `is_vector_feedback_task` colocated with existing rubric gates in `config.py` |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env usage |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch/seed paths |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No run_next changes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Bug patch appended to existing AST-724 feature doc |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Engineer diff only (Betty lane separate) |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | No `tests/` changes — correct fix-lane discipline |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | `agent.py` changes stay in core; no external/data imports added |
| `astral.layers.import-direction` | scoped | conforms | Standard `src.utils.config` import in `agent.py` |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No scripts changes |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | No UI changes |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No consult/render paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | No API auth changes |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No catalog/seed edits |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | Hot-path change is intentional narrow gate swap |
| `astral.seed.define-approved` | scoped | not-applicable | No define/seed work |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No operator rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No data-layer changes |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No DB/migrations |
| `astral.standards.debug-contract-gated` | scoped | conforms | Existing capture debug paths unchanged; craft simply skips snapshot |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Single-purpose 7-line helper |
| `astral.standards.in-scope-only` | scoped | conforms | Touches only `config.py`, `agent.py`, plan doc — matches `## Proposed change` |
| `astral.standards.logging-via-utils` | scoped | conforms | No new logging patterns introduced |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Symbol names are domain terms, not ticket ids |
| `astral.standards.no-cross-contamination` | scoped | conforms | No utils→data or ui→data leakage |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Craft exclusion uses existing `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`, not a new ad-hoc set |
| `astral.standards.public-then-helpers` | scoped | conforms | Public helper placed adjacent to `is_rubric_backed_task` |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No utils→data imports added |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job state logic |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No daisy-chain paths |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | No frontend files |
| `astral.ui.naming-conventions` | scoped | not-applicable | No UI naming |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No gunicorn config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Diff is product-only; Betty merge discipline unaffected |
| `orch.git.commit-vocabulary` | universal | conforms | N/A to diff content |
| `orch.git.flow-direction-inviolable` | universal | conforms | Sub stacked on parent `ftr` as expected |
| `orch.git.ftr-sub-topology` | universal | conforms | Branch topology matches fix-lane convention |
| `orch.git.merge-on-checkout` | universal | conforms | N/A to diff content |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | N/A to diff content |
| `orch.git.no-dev-agent-branches` | universal | conforms | N/A to diff content |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | N/A to diff content |
| `orch.git.three-permanent-branches` | universal | conforms | N/A to diff content |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Plan already encodes Susan's truncation exclusion |
| `orch.pipeline.plan-is-bible` | universal | conforms | Implementation matches `## Proposed change` verbatim |
| `orch.pipeline.project-scoped-queues` | universal | conforms | N/A to diff content |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | N/A to diff content |
| `orch.roles.archie-approves-statutes` | universal | conforms | N/A to diff content |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Engineer did not patch tests (Betty REVISE → AST-1385) |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | N/A to diff content |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | N/A to diff content |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Diff paths are allowed (`src/`, `docs/features/`) |

**Sweep:** 65 active statutes scored in-session. 0 `violates`. 0 `needs-discussion`.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Bug patch cites no catalog patterns |

## Plan adherence

Diff implements `## Proposed change` exactly:

1. **`is_vector_feedback_task`** added in `config.py` — craft keys excluded via `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY`, consumers still gated by `rubric_owner_task_key`.
2. **`is_rubric_backed_task`** left unchanged (craft still rubric-backed for owner identity).
3. **`agent.py`** — all three feedback-path gates swapped; unused `is_rubric_backed_task` import dropped.
4. Out-of-scope areas untouched (Admin UI, `rubric_feedback.py`, `CRAFT_RUBRIC_MAX_TOKENS`, consumer behavior).

Gate completeness verified: with `envelope_snapshot` absent for craft, the SUCCESS block at `agent.py:2886–2938` no-ops without needing a defense-in-depth guard inside `_capture_rubric_vector_feedback` — matches plan's optional note.

## Fix-specific checks

**`[bug-repro]`:** not applicable — clean board opt-out. `fix-board` Betty REVISE deferred test coverage to sibling **AST-1385**; no `[bug-repro]` test in diff or qa-fix thread. Documented gap, not a fix-now on this ticket.

**`## What must still hold`:** OK

| # | Item | Verdict |
|---|------|---------|
| 1 | Consumer SUCCESS still gets `prompt_suffix` + capture | OK — non-craft rubric consumers remain `is_vector_feedback_task` True; three gates unchanged for them |
| 2 | Non-`success` `agent_performance` skips capture | OK — `_capture_rubric_vector_feedback` status gate untouched (`agent.py:1466`) |
| 3 | Craft SUCCESS criteria + `max_tokens` unchanged | OK — no craft schema or token-floor edits |
| 4 | `rubric_owner_task_key(craft_*)` unchanged | OK — helper and `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` mapping untouched |
| 5 | No Admin UI / letter-grade math changes | OK — no UI or scoring edits |

## Findings

*(none)*

### Advisory

- **`task_keys_for_rubric_owner` docstring** (`config.py:2240`) still says craft writes `vector_feedback` — pre-existing, slightly stale post-fix. Betty's AST-1385 bible/test work is the right home; not blocking.
- **`docs/test-bible/utils/config.md`** still documents `is_rubric_backed_task` as the capture gate — same AST-1385 follow-up.

## What's solid

- Minimal, surgical diff — one helper, three gate swaps, no behavior change for consumers.
- Uses the canonical craft key map already maintained for rubric ownership; no parallel hardcoded craft list.
- Capture path remains envelope-snapshot-driven, so craft runs cannot accidentally persist feedback even if a model emits stray `vector_reviews`.

## Frame diff

```
docs/features/auditor/ast-724-runtime-vector-feedback-capture.md  (+82 plan-fix patch)
src/utils/config.py                                               (+is_vector_feedback_task)
src/core/agent.py                                                 (3 gates + import swap)
```

## Chuckles branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal (`ftr/AST-1378-*` exists) | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped) |

**Notes:** `no plan-rubric verdict attached` (fix-lane; Joan validate-plan not re-litigated). Betty test gap tracked on AST-1385.

context_tokens≈N

