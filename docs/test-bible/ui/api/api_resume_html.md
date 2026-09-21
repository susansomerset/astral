# Api Resume Html

**Test module:** `tests/component/ui/api/test_api_resume_html.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_resume_html.py` | `tests/component/ui/api/test_api_resume_html.py` | yes |

### AST-1350 · AST-1345

**AST-1350:** `resume_base` / `resume_for_job` map unsupported-experience `ValueError` to **400** + `{"error": <BUILD_CONFIG message>}`; other builder `ValueError`s stay **404**. Core gate: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| 400 vs 404 mapping | `src/ui/api/api_resume_html.py` | **`TestAst1350UnsupportedResumeHtml`**; reuse **`TestResumeHtmlRoutes`** other-404 rows |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_resume_html.py::TestAst1350UnsupportedResumeHtml \
  tests/component/ui/api/test_api_resume_html.py::TestResumeHtmlRoutes \
  -q
```

