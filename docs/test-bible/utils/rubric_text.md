# Rubric Text

**Test module:** `tests/component/utils/test_rubric_text.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/rubric_text.py` | `tests/component/utils/test_rubric_text.py` | no |

---

### AST-906 · AST-900 (UAT fix)

**`coerce_embedded_newline_escapes`** expands literal `\n` / `\r\n` escapes when content has fewer than two real newlines (craft Get prompt shape). **`ensure_criterion_grade_table`** writes expanded content back onto the criterion before grade-table parse. Empty / single-grade content still raises. API PUT Save path: **`docs/test-bible/ui/api/api_candidate.md`** § AST-906.

| Area | Source | Component tests |
| --- | --- | --- |
| Literal `\n` coerce + ensure mutate | `src/utils/rubric_text.py` | **`TestCoerceEmbeddedNewlineEscapes`**, **`TestEnsureCriterionGradeTableAst906`** |
| Empty / single-grade still reject | `src/utils/rubric_text.py` | **`TestEnsureCriterionGradeTableAst906::test_empty_still_raises`**, **`test_single_grade_*`** |

**AST-906** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_rubric_text.py \
  tests/component/ui/api/test_api_candidate.py::TestAst906GetRubricLiteralNewlineSave \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.
