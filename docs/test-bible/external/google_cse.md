# Google Cse

**Test module:** `tests/component/external/test_google_cse.py`

**AST-489:** `src/external/google_cse.py` — `tests/component/external/test_google_cse.py` (HTTP mocked; no branch lock). Spike `scripts/spikes/ast489_google_cse_company_search_spike.py` is console-only / live credentials — not a component-test target.

---

### AST-837 · AST-835

**`GOOGLE_CSE_CONFIG`** literals (`inter_query_delay_sec`, `rate_limit_pause_sec`, `rate_limit_max_retries`) drive shared inter-query pacing and pause-and-retry inside **`search_google_cse`**; roster discovery/resolve pass optional **`pace_detail`** when **`debug=True`** (AST-538 Style D detail lines — no new log strings in external layer).

| Area | Source | Component tests |
| --- | --- | --- |
| Inter-query delay + 429 / JSON envelope retry + exhausted raise | `src/external/google_cse.py` | `tests/component/external/test_google_cse.py::TestGoogleCseAst837PacingAndRateLimit` |
| Rate-limit detection helpers | `src/external/google_cse.py` | `tests/component/external/test_google_cse.py::TestGoogleCseHelpers::test_is_rate_limit_response_*` |
| Roster debug flush of **`pace_detail`** lines | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst837CsePaceDebug::test_discovery_debug_flushes_pace_detail` |
| **`GOOGLE_CSE_CONFIG`** literals | `src/utils/config.py` | Imported by pacing tests (no separate config cluster) |

**Regression (required):** full **`tests/component/external/test_google_cse.py`** (AST-489 + AST-837).

**AST-837** narrowed run (**`test-child`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_google_cse.py \
  tests/component/core/test_roster.py::TestAst837CsePaceDebug
```

**Pass criterion:** pytest green on narrowed args — not zero-arg harness / branch-lock gate.
