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
