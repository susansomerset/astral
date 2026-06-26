# AST-816 — UAT: Compact vector_reviews still not hydrating on evaluate_jd

- **Linear:** [AST-816](https://linear.app/astralcareermatch/issue/AST-816/uat-compact-vector-reviews-still-not-hydrating-on-evaluate-jd)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation) — Runtime Rubric Validation
- **Publish ref:** `origin/sub/AST-378/AST-816-uat-compact-vector-reviews-hydrate-evaluate-jd`
- **Shipped baseline:** [AST-808](https://linear.app/astralcareermatch/issue/AST-808/uat-hydrate-rubric-vector-codes-on-admin-vector-feedback) display hydration; [AST-724](https://linear.app/astralcareermatch/issue/AST-724/runtime-vector-feedback-capture-and-lenient-parse-runtime-rubric) capture + lenient parse

## Summary

Susan UAT 2026-06-26: **`evaluate_jd`** SUCCESS runs return well-formed compact **`agent_performance.vector_reviews`** (e.g. `CLRAOCVK`, `DORAOCVK`, …) but inspection still shows **opaque codes** in debug logs, the **FEEDBACK** agent-data tab, and Admin Vector Feedback — and **`vector_feedback`** rows are **not** persisted (FEEDBACK fallback only). AST-808 added read-path hydration for persisted rows and the FEEDBACK modal, but left **capture parse**, **debug decode**, and **candidate_id wiring** unchanged. This UAT fix closes those gaps for **`evaluate_jd`** without changing lenient run success or AST-809 batch metadata.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Lenient run success when feedback is truly unparseable | AST-724 contract (unchanged) |
| `batch_size` / `completed_at` on `vector_feedback` | [AST-809](https://linear.app/astralcareermatch/issue/AST-809/uat-capture-batch-id-completion-timestamp-and-batch-size-with-vector) (shipped) |
| Letter grades / consult scoring math | — |
| Prefilter embedded-RC capture semantics | AST-724 resolve (unchanged) |

## Root cause (plan-time)

Three independent gaps explain Susan's repro:

1. **Capture parse still fails** for otherwise valid compact lines → **`insert_vector_feedback_rows` never runs** → Admin list has no enriched rows; only a raw JSON **FEEDBACK** block is stored. AST-808 explicitly did not change capture. Likely triggers on **`evaluate_jd`**: (a) **`vector_reviews` type coercion** (JSON string instead of list, or list elements needing strip), (b) **set mismatch** between parsed codes and **`expected_codes`** (model returns N vectors while rubric expects N±1), or (c) silent skip when **`agent_performance.status`** is not normalized to `"success"`. Stage 0 spike confirms which case applies on Susan's 2026-06-26 payload before code changes.

2. **FEEDBACK tab hydration gated on `candidate_id`** — `BatchAgentDataModal` skips **`POST /vector_feedback/hydrate_reviews`** when neither the **`candidateId` prop** nor **`dispatch_ledger.candidate_id`** is available. **Admin Performance Monitor** opens the modal **without** passing the ledger row's **`candidate_id`**, and Vector Feedback batch links do not pass the row's **`candidate_id`** when the page filter is unset → UI falls back to raw JSON textarea even though AST-808 hydration API exists.

3. **Debug logging (AC #7)** — On parse failure, capture logs only `"vector feedback unparseable — stored raw FEEDBACK block"`. Susan also sees compact codes in the **`raw_response`** debug block (full JSON dump). Neither path emits **decoded vector label + criterion + R/C/V labels** required by parent AC #7.

⚠️ **Decision:** Fix capture normalization + diagnostics, debug hydrated lines, and UI **`candidate_id` / `owner_task_key` wiring** — do **not** relax strict parse equality (`parsed_codes == expected_codes`) when persisting **`vector_feedback`**; partial lists remain display-only via **`hydrate_vector_review_strings`**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `debug/spikes/ast-816-evaluate-jd-vector-reviews/repro_parse.py` | Spike script — reproduce parse + rubric lookup for Susan's sample codes | spike (gitignored dir) |
| `src/utils/rubric_feedback.py` | `normalize_vector_reviews_raw`, `parse_vector_reviews_diagnostic`, `format_hydrated_review_debug_line` | utils |
| `src/core/agent.py` | Capture: normalize input, diagnostic debug, hydrated debug lines on success/failure | core |
| `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | Resolve `candidate_id` / `owner_task_key`; hydrate when partial rows return | ui |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Pass ledger row `candidate_id` into modal | ui |
| `src/ui/frontend/src/pages/AdminVectorFeedback.tsx` | Pass row `candidate_id` when opening batch modal from detail table | ui |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

---

## Stage 0: Spike — confirm parse failure mode (evaluate_jd)

**Done when:** Spike script prints `expected_codes`, parsed codes, diagnostic reason, and hydrated sample lines for Susan's seven compact strings against a candidate with active **`evaluate_jd`** rubric vectors; result recorded in Stage 1 commit message or Linear comment if spike contradicts plan-time hypothesis.

1. Create **`debug/spikes/ast-816-evaluate-jd-vector-reviews/repro_parse.py`** (gitignored parent per **ASTRAL_CODE_RULES §3.6**):
   - Args: `--candidate-id`, `--owner-task-key evaluate_jd`, optional `--reviews` comma-separated (default: Susan's seven codes from ticket).
   - Load **`list_rubric_vector_uuid_by_code`** and **`rubric_criteria_for_task`** (same as capture).
   - Call **`parse_vector_reviews_diagnostic`** (Stage 1) and print: `expected`, `parsed`, `reason`, `missing`, `extra`.
   - Call **`hydrate_vector_review_strings`** via **`list_rubric_vectors`** lookup; print first two formatted debug lines.

2. Run locally against a candidate known to have **`evaluate_jd`** rubric (Susan's staging candidate if available in dev DB). **Do not commit spike output files.**

3. If spike shows **`expected_codes` empty** → stop and comment on **AST-378** parent (data/backfill issue, not display). If spike shows **parse succeeds** → focus Stages 2–3 on UI/debug wiring only.

---

## Stage 1: Utils — normalize + diagnostic parse + debug line formatter

**Done when:** `normalize_vector_reviews_raw` and `parse_vector_reviews_diagnostic` are importable; existing **`parse_vector_reviews`** behavior unchanged for callers except it uses normalization internally; debug line formatter returns human-readable single-line summary.

1. In **`src/utils/rubric_feedback.py`**, add:

   ```python
   def normalize_vector_reviews_raw(raw: Any) -> Optional[List[str]]:
   ```

   - Return `None` when input cannot become a non-empty list of strings.
   - Accept: `list` of strings (strip each); JSON string that parses to such a list; reject dict/non-string elements.

2. Add:

   ```python
   def parse_vector_reviews_diagnostic(
       raw_reviews: Any,
       expected_codes: frozenset[str],
       code_to_uuid: Dict[str, str],
   ) -> tuple[Optional[List[Dict[str, str]]], Optional[str], frozenset[str], frozenset[str]]:
   ```

   - Returns `(rows, failure_reason, parsed_codes, missing_codes)`.
   - `failure_reason` one of: `"empty_expected"`, `"not_list"`, `"bad_line"`, `"duplicate_code"`, `"unknown_code"`, `"missing_codes"`, `"extra_codes"`, or `None` on success.
   - Reuse **`parse_vector_review_string`** per line; apply same strict equality as **`parse_vector_reviews`**.

3. Refactor **`parse_vector_reviews`** to call **`normalize_vector_reviews_raw`** then **`parse_vector_reviews_diagnostic`**, returning rows only (keep signature stable for AST-724 callers).

4. Add:

   ```python
   def format_hydrated_review_debug_line(row: Dict[str, str]) -> str:
   ```

   - Format: `{code} {label} — R/{relevance_label} C/{clarity_label} V/{verdict_label} — {content_first_80_chars}` using **`RUBRIC_FEEDBACK_CONFIG["value_labels"]`**; truncate content with `…` when longer than 80 chars.

5. Update **`rubric_feedback.py` module docstring** one-liner to mention AST-816 diagnostic helpers.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Single normalize + diagnostic path shared by capture |
| §2.1 config | Value labels from `RUBRIC_FEEDBACK_CONFIG` |
| §3.3 imports | utils → config only |

---

## Stage 2: Capture + debug — normalize, persist when strict match, hydrate debug lines

**Done when:** Susan's seven-code **`evaluate_jd`** SUCCESS payload (when rubric count matches) inserts **`vector_feedback`** rows; debug logs per-vector hydrated lines on success; on parse failure debug logs reason + hydrated lines for parseable subset without failing the run.

1. In **`src/core/agent.py`**, **`_capture_rubric_vector_feedback`**:
   - Replace **`expected_codes`** computation with **`frozenset(code_to_uuid.keys())`** when **`code_to_uuid`** is non-empty (equivalent to criteria ∩ UUID for table-backed rubrics; removes redundant criteria walk).
   - Before parse, set `raw_list = normalize_vector_reviews_raw(perf_dict.get("vector_reviews"))`; if `None`, treat as unparseable.
   - Call **`parse_vector_reviews_diagnostic(raw_list, expected_codes, code_to_uuid)`**.

2. On **success** (`rows` not `None`):
   - Keep **`insert_vector_feedback_rows`** unchanged (AST-809 metadata already wired).
   - Build **`rubric_by_code`** once via **`list_rubric_vectors(candidate_id, owner_task_key, current_only=True)`** mapped by uppercased code (same shape as admin lookup).
   - Debug loop: for each parsed row, **`hydrate_vector_review_strings([compact], rubric_by_code)`** or format from row + lookup; emit **`debug_index`** per vector (index i/N) + **`debug_detail(format_hydrated_review_debug_line(...))`** per AST-538 style D.

3. On **failure**:
   - Keep **`store_feedback_block`** + raw JSON via **`format_vector_reviews_raw`** (lenient — no run failure).
   - When **`debug=True`**: emit **`debug_index`** once with outcome `"vector feedback unparseable"`; **`debug_detail(f"reason={failure_reason} missing={sorted(missing)} expected={sorted(expected_codes)}")`**; for each line in **`raw_list`** that **`parse_vector_review_string`** accepts, emit **`debug_detail(format_hydrated_review_debug_line(...))`** using rubric lookup (partial hydrate OK per ticket AC #3).

4. Do **not** change **`envelope_snapshot`** timing or SUCCESS gate (`status == "success"` after lowercasing).

5. Update **`agent.py` inventory comment** near **`_capture_rubric_vector_feedback`** to reference AST-816 diagnostic debug.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §1.5.1 debug | Per-vector index headers; detail only when `debug=True` |
| §2.7 consult | Capture still after envelope snapshot, SUCCESS-only |
| §3.3 imports | core → data/utils only |

---

## Stage 3: React — reliable FEEDBACK hydration entry points

**Done when:** Opening batch agent data from Performance Monitor or Vector Feedback detail hydrates FEEDBACK compact JSON; partial hydrate table shown when at least one row decodes; raw textarea only when hydration unavailable.

1. In **`BatchAgentDataModal.tsx`**:
   - Add state `modalCandidateId` initialized from prop; update when ledger loads: `setModalCandidateId(prev => prev || candidateId || ledger?.candidate_id || "")`.
   - Set `hydrateOwnerTaskKey` from **`feedbackBlocks[0]?.task_key`** resolved to owner in POST body as **`owner_task_key`** (keep **`task_key`** for backward compat):

     ```typescript
     body: JSON.stringify({
       candidate_id: hydrateCandidateId,
       owner_task_key: hydrateOwnerTaskKey,
       task_key: hydrateTaskKey,
       vector_reviews: feedbackReviews,
     })
     ```

   - Change hydrate gate: require **`hydrateCandidateId && (hydrateOwnerTaskKey || hydrateTaskKey)`** only — not both candidate and task from ledger if prop supplies candidate.
   - **`showHydratedFeedback`**: true when **`hydratedRows?.length > 0`** (partial lists OK per ticket); show table even if some lines failed parse.

2. In **`AdminPerformanceMonitor.tsx`**, track `agentDataCandidateId` alongside `agentDataBatchId`. When opening modal from expanded row button, set both from **`row.batch_id`** and **`row.candidate_id`**. Pass **`candidateId={agentDataCandidateId || undefined}`** to **`BatchAgentDataModal`**.

3. In **`AdminVectorFeedback.tsx`**, track `agentDataCandidateId`. When batch link clicked, set **`agentDataBatchId`** and **`agentDataCandidateId`** from **`row.candidate_id`** (fallback **`filters.candidate_id`**). Pass **`candidateId={agentDataCandidateId || filters.candidate_id || undefined}`** to modal.

4. No change to **`AdminVectorFeedback`** list columns — persisted rows already join rubric content (AST-808); this stage fixes FEEDBACK-only inspection paths.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Reuse existing hydrate API + modal table |
| §3.2 ui config-driven | Labels from server hydrate response |
| Scope | Read-only UI; no capture changes in React |

---

## Execution contract (build-child)

- Stages **0 → 1 → 2 → 3** in order; one commit per stage on epic worktree; publish each to **`origin/sub/AST-378/AST-816-uat-compact-vector-reviews-hydrate-evaluate-jd`**.
- Do **not** edit **`tests/`** or **`docs/test-bible/**`**.
- On ambiguity — **`🛑 Stage N blocked`** on **AST-378** parent; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — Utils parse/diagnostic helpers, one capture hook in `agent.py`, and three frontend touchpoints for `candidate_id` wiring; no schema or API route additions beyond existing AST-808 hydrate endpoints.

**Conf:** `Medium` — Root causes are identified at plan-time (capture vs display vs debug), but Stage 0 spike must confirm which parse failure mode applies on Susan's exact payload before Stage 2 lands.

**Risk:** `Medium` — Incorrect relaxation of strict parse would persist wrong feedback rows; mitigation is spike-first, unchanged equality rule, and diagnostic-only logging on failure.

---

## Self-review vs ASTRAL_CODE_RULES

| Section | Result |
|---------|--------|
| §1.3 DRY | Extends AST-808 `hydrate_vector_review_strings`; no duplicate parse logic in React |
| §2.1 config | Value labels from `RUBRIC_FEEDBACK_CONFIG` |
| §3.3 imports | ui → api; core → utils/data |
| §3.6 spikes | Under `debug/spikes/ast-816-…/` only |
| §1.5.1 debug | Per-vector headers + hydrated detail lines |

No unresolved rule conflicts.
