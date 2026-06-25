# AST-808 — UAT: Hydrate rubric vector codes on Admin Vector Feedback

- **Linear:** [AST-808](https://linear.app/astralcareermatch/issue/AST-808/uat-hydrate-rubric-vector-codes-on-admin-vector-feedback)
- **Parent (context only):** [AST-378](https://linear.app/astralcareermatch/issue/AST-378/runtime-rubric-validation) — Runtime Rubric Validation
- **Publish ref:** `origin/sub/AST-378/AST-808-uat-hydrate-vector-codes-admin`
- **Shipped baseline:** [AST-725](https://linear.app/astralcareermatch/issue/AST-725/admin-vector-feedback-screen-runtime-rubric-validation) admin list/summary; [AST-724](https://linear.app/astralcareermatch/issue/AST-724/runtime-vector-feedback-capture-and-lenient-parse-runtime-rubric) capture + `rubric_vector` authority

## Summary

Susan UAT 2026-06-25: Admin **Vector Feedback** shows opaque compact review strings (e.g. `ACRAOCVK`, `CFRAOCVK`) instead of the human-readable rubric assessment — vector **label** plus criterion **content** from active **`rubric_vector`** rows. This bug adds **`vector_content`** to the list API, enriches rows with a formatted assessment header, updates the detail table to show label + expandable criterion text, and hydrates raw **`vector_reviews`** JSON in the **FEEDBACK** agent-data tab so unparseable runs are inspectable without raw compact codes.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| `batch_size` / `completed_at` on `vector_feedback` rows | [AST-809](https://linear.app/astralcareermatch/issue/AST-809/uat-capture-batch-id-completion-timestamp-and-batch-size-with-vector) |
| Runtime capture, lenient parse rules, rubric_vector write cutover | AST-724 / AST-723 |
| Rubric health badges on Artifacts pages | — |
| Grouping three feedback-type rows into one row per vector | — (v1 keeps grain; assessment column carries rubric text) |

## Root cause (plan-time)

AST-725 joins **`rubric_vector`** for **`code`** + **`label`** only — **`content`** (criterion assessment text) is never selected or shown. Susan's quoted JSON list is the model's compact **`vector_reviews`** envelope; when parse fails, **FEEDBACK** blocks store that JSON verbatim and the modal shows raw strings with no decode. Parsed **`vector_feedback`** rows expose short **codes** in the Vector column without adjacent criterion body, so inspection feels like opaque codes rather than assessments.

⚠️ **Decision:** Fix display + FEEDBACK hydration only — no capture or parse rule changes. Filter/sort continues to use **`vector_code`** (short code from join); human-readable text is display-only enrichment.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `list_vector_feedback` SELECT adds `rv.content`, `rv.importance` | data |
| `src/utils/rubric_feedback.py` | `hydrate_vector_review_strings(...)` for compact-line + rubric lookup display | utils |
| `src/ui/api/api_admin.py` | Enrich list rows; `GET /vector_feedback/rubric_lookup` | ui |
| `src/ui/frontend/src/pages/AdminVectorFeedback.tsx` | Assessment column (header + expandable content) | ui |
| `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | FEEDBACK tab: hydrated table when body is `vector_reviews` JSON | ui |

**Tests:** Betty owns **`tests/`** at Code Complete — engineer does **not** add test files in **build-child**.

---

## Stage 1: Data layer — return rubric content on list rows

**Done when:** `list_vector_feedback` returns `vector_content` and `vector_importance` from the joined `rubric_vector` row; no API/React changes yet.

1. In **`src/data/database.py`**, extend **`list_vector_feedback`** SELECT (AST-725 query ~line 3305):

   ```sql
   rv.code AS vector_code,
   rv.label AS vector_label,
   rv.content AS vector_content,
   rv.importance AS vector_importance,
   rv.current AS rubric_current
   ```

2. Do **not** add columns to **`vector_feedback`** table — join-only change.

3. Update **`database.py` header inventory** one-liner for `list_vector_feedback` to mention content hydration (AST-808).

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §1.1 inventory | Header note updated |
| §3.3 imports | data → utils only |

---

## Stage 2: Utils hydrate helper + admin API enrichment

**Done when:** List API returns `vector_assessment_header` and `vector_content`; rubric lookup endpoint returns code → label/content/importance for FEEDBACK modal; `@require_admin` on new route.

1. In **`src/utils/rubric_feedback.py`**, add:

   ```python
   def hydrate_vector_review_strings(
       raw_reviews: Any,
       rubric_by_code: Dict[str, Dict[str, Any]],
   ) -> List[Dict[str, str]]:
   ```

   - Input: JSON list of compact strings (e.g. `["ACRAOCVK", ...]`) or return `[]` when not a list.
   - For each string: **`parse_vector_review_string(line)`** → `(code, {relevance, clarity, verdict})` or skip line on parse failure.
   - Lookup **`rubric_by_code[code]`** (uppercased); build row:

     ```python
     {
         "compact": line,
         "code": code,
         "label": rubric.get("label") or code,
         "content": rubric.get("content") or "",
         "importance": str(rubric.get("importance") or ""),
         "relevance": vals["relevance"],
         "clarity": vals["clarity"],
         "verdict": vals["verdict"],
         "relevance_label": RUBRIC_FEEDBACK_CONFIG["value_labels"].get(vals["relevance"], vals["relevance"]),
         # ... clarity_label, verdict_label similarly
     }
     ```

   - Do **not** require full expected-code set (unlike capture parse) — partial lists OK for display.

2. In **`src/ui/api/api_admin.py`**, import **`list_rubric_vectors`** from **`database`** (same pattern as AST-725 list imports).

3. Extend **`_enrich_vector_feedback_row(row)`**:

   ```python
   imp = row.get("vector_importance")
   label = row.get("vector_label") or ""
   code = row.get("vector_code") or ""
   out["vector_assessment_header"] = format_rubric_vector_header_for_api(imp, label, code)
   ```

   Add module helper mirroring artifact header shape (no React import):

   ```python
   def _vector_assessment_header(importance, label, code) -> str:
       imp = importance if isinstance(importance, int) and 1 <= importance <= 10 else 5
       lab = (label or "").strip() or "??"
       cd = (code or "").strip()
       return f"{imp} - {lab} ({cd})" if cd else f"{imp} - {lab}"
   ```

4. Add **`_VECTOR_FEEDBACK_COLUMNS`** entries after **`vector_label`**:

   | key | label | type |
   |-----|-------|------|
   | `vector_assessment_header` | Assessment | str |
   | `vector_content` | Criterion | str |

   Keep existing **`vector_code`** column for sort/filter.

5. Add route **`GET /vector_feedback/rubric_lookup`** + **`@require_admin`**:
   - Query args: **`candidate_id`**, **`owner_task_key`** (required); 400 if either missing.
   - Call **`list_rubric_vectors(candidate_id, owner_task_key, current_only=True)`**.
   - Return JSON object keyed by uppercased **`code`**:

     ```json
     { "AC": { "label": "...", "content": "...", "importance": 8 }, ... }
     ```

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §2.1 config | Value labels from `RUBRIC_FEEDBACK_CONFIG` in hydrate helper |
| §3.2 ui config-driven | Rubric lookup served from API, not hardcoded in React |
| §2.9 auth | `@require_admin` on `/rubric_lookup` |

---

## Stage 3: React — assessment column + FEEDBACK tab hydration

**Done when:** Detail table shows assessment header + expandable criterion content; FEEDBACK tab renders hydrated table for `vector_reviews` JSON; vector code filter unchanged.

1. In **`AdminVectorFeedback.tsx`**, update **`FeedbackRow`** interface with `vector_content`, `vector_importance`, `vector_assessment_header`.

2. Replace separate sparse Vector/Label columns with:

   | key | label | render |
   |-----|-------|--------|
   | `vector_code` | Code | plain (sort/filter grain) |
   | `vector_assessment_header` | Assessment | plain header string |
   | `vector_content` | Criterion | **`ListPage` expandable** pattern — use column `expandable: true` or custom `render` with truncated text + expand if content length > 100 |

   ⚠️ **Decision:** Keep **`vector_code`** column for AC #6 filter on code; assessment header matches Artifacts **`formatRubricVectorHeader`** shape (`{importance} - {label} ({code})`).

3. In **`BatchAgentDataModal.tsx`**:
   - When active tab is **`FEEDBACK`** and **`block_data`** parses as JSON **array of strings**:
     - Extract **`candidate_id`** from first block's context if available, else skip hydration and show raw (modal has no candidate today — use batch-level fetch).
   - On FEEDBACK tab load, call **`GET /api/admin/vector_feedback/rubric_lookup?candidate_id=…&owner_task_key=…`** where **`owner_task_key`** comes from first block's **`task_key`** passed through **`rubric_owner_task_key`** — **API-only**: add optional query arg normalization in **`rubric_lookup`** route: when **`task_key`** is a craft/consumer run key, map to owner via **`rubric_owner_task_key`** in **`api_admin`** before **`list_rubric_vectors`**.
   - Call **`hydrate_vector_review_strings`** result shape from new endpoint **`POST /vector_feedback/hydrate_reviews`** OR compute client-side from lookup + **`parse_vector_review_string`** exposed via static FEEDBACK value labels — **prefer server:**

   Add **`POST /vector_feedback/hydrate_reviews`** + **`@require_admin`**:

   ```json
   { "candidate_id": "...", "owner_task_key": "...", "vector_reviews": ["ACRAOCVK", ...] }
   ```

   Returns **`{"rows": [...]}`** from **`hydrate_vector_review_strings`**.

4. FEEDBACK tab UI: when hydrate returns rows, show read-only HTML table (code, label, relevance/clarity/verdict labels, content preview); else fall back to existing raw textarea.

5. Extend **`BLOCK_TYPE_ORDER`** — already includes **`FEEDBACK`** from AST-725; no change if present.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Reuse `parse_vector_review_string`, ListPage expandable, existing modal |
| Scope | Read-only display; no capture changes |

---

## Execution contract (build-child)

- Stages **1 → 2 → 3** in order; one commit per stage on epic worktree; publish each to **`origin/sub/AST-378/AST-808-uat-hydrate-vector-codes-admin`**.
- Do **not** edit **`tests/`** or **`docs/test-bible/**`**.
- On ambiguity — **`🛑 Stage N blocked`** on **AST-378** parent; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — One UAT display fix across data list SELECT, utils hydrate helper, two admin API routes, Admin Vector Feedback columns, and FEEDBACK modal hydration; no capture or schema migration beyond join fields.

**Conf:** `high` — Root cause is missing `content` + FEEDBACK JSON display; AST-725 join and `parse_vector_review_string` already exist; sibling AST-809 metadata is explicitly out of scope.

**Risk:** `low` — Read-only admin enrichment; wrong label lookup only affects inspection UI.

---

## Self-review vs ASTRAL_CODE_RULES

| Section | Result |
|---------|--------|
| §1.3 DRY | Reuses `list_rubric_vectors`, `parse_vector_review_string`, `RUBRIC_FEEDBACK_CONFIG` labels |
| §2.1 config | Value labels from config in hydrate helper |
| §3.3 imports | ui → data/utils; utils pure except config import |
| §3.5 naming | `hydrate_vector_review_strings`, `rubric_lookup`, `hydrate_reviews` |

No conflicts requiring `conf-!!-NONE`.

## Review (build)

- **commit:** `3503af3`
- **branch:** `origin/sub/AST-378/AST-808-uat-hydrate-vector-codes-admin`
- **stages:** data SELECT content/importance; hydrate helper + rubric_lookup/hydrate_reviews routes; AdminVectorFeedback assessment columns; BatchAgentDataModal FEEDBACK hydration table
