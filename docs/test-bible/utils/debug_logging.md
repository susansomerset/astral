# Debug Logging

**Test module:** `tests/component/utils/test_debug_logging.py`

### AST-554 (parent AST-538)

**AST-538 (parent):** Mandatory backend debug contract in **`docs/ASTRAL_CODE_RULES.md`** §1.5.1, shared emission API on **`_PrefixedLogger`** (`debug_index`, `debug_detail`, `debug_detail_block`), pure **`truncate_debug_content`** / **`format_debug_index_header`**. Parent AC **7** — Betty tests **gating + truncation math only** (no log-string golden files). Operational backfill (**inflow_discovery** per-index traces, AC 2/4 spot-check) is **AST-557**; nav rename **AST-555**; **review-astral** rubric **AST-556**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-554** | Constants, truncation helper, index header formatter, debug-gated INFO emission | `src/utils/logging.py`, `docs/ASTRAL_CODE_RULES.md` §1.5.1 | **`TestTruncateDebugContent`**, **`TestFormatDebugIndexHeader`**, **`TestPrefixedLoggerDebugGating`** in **`test_debug_logging.py`**; regression **`test_logging_batch.py`** |

**AST-554** narrowed run (pytest-only — python-only child; avoids Vitest tail / **AST-511** cross-ticket noise on engineer worktrees):

```bash
.venv/bin/python -m pytest tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

**`[qa-handoff]` return (2026-06-03):** Ada **`test-astral`** — `run_component_tests.sh` with trailing paths still invoked full Vitest on **`dev-ada`**; manifest uses direct **`pytest`** gate (13 tests). Harness on **`dev-betty`** skips Vitest when trailing paths are set (**Appendix A** in [README](../README.md)).
