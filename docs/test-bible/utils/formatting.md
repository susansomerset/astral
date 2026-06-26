# Formatting

**Test module:** `tests/component/utils/test_formatting.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/formatting.py` | `tests/component/utils/test_formatting.py` | yes |

---

### AST-827 · AST-824

**AST-827 (child):** **`find_job_containers`** Phase 2b — sibling leaf tags each carrying one title (medicarerights-style flat `<a>` job rows) return one outerHTML per title-bearing leaf when the union covers all requested titles.

| Area | Source | Component tests |
| --- | --- | --- |
| Sibling anchor two-title cull | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestFindJobContainers::test_sibling_anchor_links_two_titles` |

Roster handoff + parse dispatch: **`docs/test-bible/core/roster.md`** (**AST-827**).

**AST-827** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestFindJobContainers::test_sibling_anchor_links_two_titles \
  tests/component/utils/test_formatting.py::TestFindJobContainers::test_phase_one_deepest_container \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-713 · AST-710

**`collapse_consecutive_blank_lines`** in `formatting.py` — collapses runs of two or more consecutive blank (whitespace-only) lines to a single blank line; preserves non-empty line content unchanged. Parent **AST-710** removes redundant empty rows from persisted visible text.

| Area | Source | Component tests |
| --- | --- | --- |
| Blank-line normalizer | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines` |

---

### AST-718 · AST-716

**`normalize_link()`** — pure PJL URL ledger key (scheme strip, fragment drop, slash collapse, index filename trim). Parent **AST-716** decomposed prefilter path.

| Area | Source | Component tests |
| --- | --- | --- |
| PJL URL normalizer | `src/utils/formatting.py` | `tests/component/utils/test_formatting.py::TestNormalizeLink` |

**AST-718** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_formatting.py::TestNormalizeLink -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

**AST-713** narrowed run:

```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_formatting.py::TestCollapseConsecutiveBlankLines -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.
