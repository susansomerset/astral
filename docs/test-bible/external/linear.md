# Linear

**Test module:** `tests/component/external/test_linear.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/linear.py` | `tests/component/external/test_linear.py` | no |

---

### AST-792

Batch GraphQL lookup of parent issue state names for deploy-status UAT filter (`fetch_parent_issue_states`). HTTP mocked via `urllib.request.urlopen`; requires `LINEAR_API_KEY` at runtime only.

| Behavior | Tests |
| --- | --- |
| Maps identifiers → state names | `TestFetchParentIssueStates::test_fetch_parent_issue_states_maps_identifiers` |
| Empty input → `{}` | `TestFetchParentIssueStates::test_fetch_parent_issue_states_empty_input` |
| Invalid ticket id → `ValueError` | `TestFetchParentIssueStates::test_invalid_ticket_id_raises` |
| GraphQL errors → `LinearApiError` | `TestFetchParentIssueStates::test_graphql_errors_raise_linear_api_error` |

**Manifest pytest gate (AST-792 — partial; see core + utils bible files):**

```bash
.venv/bin/python -m pytest tests/component/external/test_linear.py -q
```
