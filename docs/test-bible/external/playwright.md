# Playwright

**Test module:** `tests/component/external/test_playwright.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/playwright.py` | `tests/component/external/test_playwright.py` | yes |

---

### AST-765 · AST-757

**Sunset boards channel:** `board_search_deeplink` removed; **`extract_raw_job_listings`** (roster) unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Roster job-list extraction | `src/external/playwright.py` | **`tests/component/external/test_playwright.py`** (minus `TestBoardSearchDeeplink`) |

**AST-765** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/external/test_playwright.py -q
```
