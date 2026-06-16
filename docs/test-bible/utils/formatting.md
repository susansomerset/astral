# Formatting

**Test module:** `tests/component/utils/test_formatting.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/formatting.py` | `tests/component/utils/test_formatting.py` | yes |

---

### AST-713 · AST-710

**`collapse_consecutive_blank_lines`** in `formatting.py` — collapses runs of two or more consecutive blank (whitespace-only) lines to a single blank line; preserves non-empty line content unchanged. Parent **AST-710** removes redundant empty rows from persisted visible text.

| Area | Source | Component tests |
| --- | --- | --- |
| Blank-line normalizer | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines` |

**AST-713** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.
