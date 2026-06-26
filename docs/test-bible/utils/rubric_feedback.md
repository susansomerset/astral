# Rubric Feedback Parse

**Test module:** `tests/component/utils/test_rubric_feedback.py`

### AST-724 · AST-378

Pure lenient parse helpers for **`agent_performance.vector_reviews`** compact strings (`CODE` + `R` + relevance + `C` + clarity + `V` + verdict). Invalid input returns **`None`** — caller stores raw FEEDBACK (**AST-724** capture in **`agent.py`**).

| Area | Source | Component tests |
| --- | --- | --- |
| Single-line parse | `src/utils/rubric_feedback.py` | `TestParseVectorReviewString` |
| Full expected-code set validation | `src/utils/rubric_feedback.py` | `TestParseVectorReviews` |
| Raw FEEDBACK body serialization | `src/utils/rubric_feedback.py` | `TestFormatVectorReviewsRaw` |

**AST-724** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_rubric_feedback.py \
  -q
```

Config gate **`is_rubric_backed_task`** + **`prompt_suffix`**: **`docs/test-bible/utils/config.md`** (**AST-724**).

---

### AST-808 · AST-378 (UAT fix)

**`hydrate_vector_review_strings`** decodes compact review lines for Admin display (partial lists OK).

| Area | Source | Component tests |
| --- | --- | --- |
| Rubric lookup hydration | `src/utils/rubric_feedback.py` | `TestAst808HydrateVectorReviewStrings` |

Admin API + page: **`docs/test-bible/ui/api/api_admin.md`**, **`docs/test-bible/frontend/pages.md`**.

---

### AST-816 · AST-378 (UAT fix)

**`normalize_vector_reviews_raw`**, **`parse_vector_reviews_diagnostic`**, **`format_hydrated_review_debug_line`** — JSON-string envelopes, strict expected-code match, debug labels (Susan UAT compact codes on **`evaluate_jd`**).

| Area | Source | Component tests |
| --- | --- | --- |
| Raw envelope normalize | `src/utils/rubric_feedback.py` | `TestAst816NormalizeVectorReviews` |
| Diagnostic parse reasons | `src/utils/rubric_feedback.py` | `TestAst816ParseVectorReviewsDiagnostic` |
| Hydrated debug line format | `src/utils/rubric_feedback.py` | `TestAst816FormatHydratedReviewDebugLine` |

**AST-816** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_rubric_feedback.py::TestAst816NormalizeVectorReviews \
  tests/component/utils/test_rubric_feedback.py::TestAst816ParseVectorReviewsDiagnostic \
  tests/component/utils/test_rubric_feedback.py::TestAst816FormatHydratedReviewDebugLine \
  -q
```

Capture + Admin wiring: **`docs/test-bible/core/agent.md`**, **`docs/test-bible/frontend/pages.md`**.
