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
| Roster debug flush of **`pace_detail`** lines | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst837CsePaceDebug::test_discovery_debug_streams_pace_detail_during_search` |
| **`GOOGLE_CSE_CONFIG`** literals | `src/utils/config.py` | Imported by pacing tests (no separate config cluster) |

**Regression (required):** full **`tests/component/external/test_google_cse.py`** (AST-489 + AST-837).

**AST-837** narrowed run (**`test-child`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_google_cse.py \
  tests/component/core/test_roster.py::TestAst837CsePaceDebug
```

**Pass criterion:** pytest green on narrowed args — not zero-arg harness / branch-lock gate.

---

### AST-839 · AST-835 (UAT bug)

**AST-837** buffered **`pace_lines`** then flushed after **`debug_index`** — UAT could not see per-HTTP pacing/outcome in real time. Fix streams **`log.debug_detail`** as **`pace_detail`** (pre-search **`debug_index`** outcome **`CSE search`**) and adds per-request **`CSE HTTP start=… status=… items=…`** / **`rate_limited=…`** lines from **`_http_get_with_pacing_and_retry`**. Pacing/retry semantics unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Per-HTTP **`pace_detail`** outcome lines | `src/external/google_cse.py` | `tests/component/external/test_google_cse.py::TestGoogleCseAst839HttpOutcomeLines` |
| Discovery streaming callback + index order | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst837CsePaceDebug::test_discovery_debug_streams_pace_detail_during_search` |
| Resolve streaming pre-index + complete detail | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst839CseDebugStreaming::test_resolve_debug_streams_pre_search_index_and_complete_detail` |

**Regression (required):** full **`tests/component/external/test_google_cse.py`** (AST-489 + AST-837 + AST-839).

**AST-839** narrowed run (**`test-child`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_google_cse.py \
  tests/component/core/test_roster.py::TestAst837CsePaceDebug \
  tests/component/core/test_roster.py::TestAst839CseDebugStreaming
```

**Pass criterion:** pytest green on narrowed args — not zero-arg harness / branch-lock gate.

### AST-2219 · AST-2215 (zero-stub `get_receipt` + `GoogleCseSearchResult`)

Parent AC **5** search half + Stage 1 return shape. `get_receipt(ids, key)` → shared `TIMESHEET_RECEIPT_FIELDS`, `platform_cost=None`, `completion_status="stub"`, no HTTP. `search_google_cse` returns `{hits, call_start, call_stop, hit_count}` (not a bare list).

| Area | Source | Component tests |
| --- | --- | --- |
| New — stub shape / no HTTP / timing keys | `get_receipt` / `search_google_cse` | `TestAst2219GetReceiptAndSearchResult` |
| Revised — all former list assertions use `["hits"]` | `search_google_cse` | `TestGoogleCseSearchGoogleCse` / `TestGoogleCseAst837*` / AST-839 HTTP lines |

**Primary manifest:** [`../core/roster.md`](../core/roster.md) § AST-2219 (AC10) + this file for stub.


### AST-2253 · AST-2246 (search credentials from the candidate)

**Parent:** [AST-2246](https://linear.app/astralcareermatch/issue/AST-2246). **Publish:** `origin/sub/AST-2246/AST-2253-search-candidate-secrets`. Plan: `docs/features/foundation/ast-2253-search-candidate-secrets.md`.

`search_google_cse` takes `api_key` and `cx` from the caller. A blank value raises `ValueError` before HTTP. Roster resolve and discovery pass the hydrated `google_cse_api_key` and `google_cse_id`, and warn with the candidate id and secret id when one is missing. Timesheet fetch looks up `google_cse_api_key` and skips when it is absent. The AST-489 spike requires `--api-key` and `--cx`.

| Area | Component tests |
| --- | --- |
| Caller key and cx are the HTTP params; blank raises before HTTP | revised **`TestGoogleCseSearchGoogleCse`** (`test_blank_api_key_raises_before_http`, `test_blank_cx_raises_before_http`, `test_caller_key_and_cx_are_the_http_params`); other search calls go through `_search` |
| Resolve and discovery pass or skip on the candidate secrets | **`TestAst2253SearchCredentials`** in `tests/component/core/test_roster.py` |
| Timesheet skip and pass | **`TestAst2219GoogleCseReceiptRoute`** in `tests/component/core/test_timesheets.py` |
| Spike flags | `tests/component/scripts/test_ast489_cse_spike.py` |

**Broken / obsolete:** `GOOGLE_CSE_API_KEY` / `GOOGLE_CSE_ID` `RuntimeError` cases, and the timesheet empty-key stub. Revised in place. Roster suites that mock `search_google_cse` get both secrets from `_candidate_search_secrets` unless they restore `_REAL_SEARCH_CREDENTIALS`. **Integration:** none.

## QA test manifest — AST-2253

1. `tests/component/external/test_google_cse.py`
2. `tests/component/scripts/test_ast489_cse_spike.py`
3. `tests/component/core/test_timesheets.py::TestAst2219GoogleCseReceiptRoute`
4. `tests/component/core/test_roster.py::TestAst2253SearchCredentials`
5. `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path`
6. `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues`
7. `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_searches_only_stale_terms`
8. `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_freq_hrs_zero_searches_fresh_terms`
9. `tests/component/core/test_roster.py::TestAst2219SearchTimesheetRecording`
10. `tests/component/core/test_roster.py::TestAst837CsePaceDebug`
11. `tests/component/core/test_roster.py::TestAst839CseDebugStreaming`
12. `tests/component/core/test_roster.py::TestAst506InflowResolve`
13. `tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm::test_run_batch_stamps_term_from_cse_loop`
14. `tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm::test_run_batch_debug_emits_originating_search_term`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_google_cse.py \
  tests/component/scripts/test_ast489_cse_spike.py \
  tests/component/core/test_timesheets.py::TestAst2219GoogleCseReceiptRoute \
  tests/component/core/test_roster.py::TestAst2253SearchCredentials \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_searches_only_stale_terms \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_freq_hrs_zero_searches_fresh_terms \
  tests/component/core/test_roster.py::TestAst2219SearchTimesheetRecording \
  tests/component/core/test_roster.py::TestAst837CsePaceDebug \
  tests/component/core/test_roster.py::TestAst839CseDebugStreaming \
  tests/component/core/test_roster.py::TestAst506InflowResolve \
  tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm::test_run_batch_stamps_term_from_cse_loop \
  tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm::test_run_batch_debug_emits_originating_search_term
```

**Pass criterion:** pytest green on those nodes. Not the zero-arg harness.

**Bible shasum (after publish):**

```text
git show origin/sub/AST-2246/AST-2253-search-candidate-secrets:docs/test-bible/external/google_cse.md | shasum
git show origin/sub/AST-2246/AST-2253-search-candidate-secrets:docs/test-bible/core/roster.md | shasum
git show origin/sub/AST-2246/AST-2253-search-candidate-secrets:docs/test-bible/core/timesheets.md | shasum
```
