# Builder

**Test module:** `tests/component/core/test_builder.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/builder.py` | `tests/component/core/test_builder.py` | yes |

---

### AST-623 · AST-545

**AST-545 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/builder.py`** — resume/cover letter/base-resume render entry points with Style D **`index 1/1`** headers, **`|`** detail for content-source resolution (job **`resume_content`** vs candidate **`base_resume`**, cover letter vs sample text), enabled structure keys, accent source, ATS keyword count, and truncated HTML preview via **`debug_detail_block`**; **`debug=False`** unchanged. **No Betty log-string tests** (parent + child explicit); plan Stage 4 is manual UAT spot-check only.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-623** | Contract debug on `build_resume`, `build_resume_from_job`, `build_cover_letter`, `build_cover_letter_from_job`, `build_base_resume`; read-only source label helpers; failure headers on `ValueError` paths | `src/core/builder.py` | **`tests/component/core/test_builder.py`** (full file — **`LOCKED_AT_100`**); **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-623** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/core/test_builder.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py
```

**Manifest focus (existing + branch-coverage extensions — no log-string asserts):**

| Touched path | Existing / extended tests |
| --- | --- |
| `build_resume_from_job` success + failure + `include_cover` + keyword shapes | **`TestBuildResumeFromJob`**, **`TestBuildResumeFromJobDebugPaths`**, **`TestAst581ResumeCoverSplit`** |
| `build_resume` load chain + failure headers | **`TestBuildResume`**, **`TestBuildResumeDebugPaths`** |
| `build_cover_letter` / `build_cover_letter_from_job` | **`TestAst581ResumeCoverSplit`**, **`TestBuildCoverLetterDebugPaths`**, **`TestBuildCoverLetterFromJobDebugPaths`** |
| `build_base_resume` | **`TestBuildBaseResume`**, **`TestBuildBaseResumeDebugPaths`** |
| Source label helpers | **`TestBuilderIdentifierHelpers`** |
| `debug=False` unchanged | All pre-AST-623 rows above; full-file branch lock |

**Betty test fix (AST-623):** Extended **`test_builder.py`** for **`LOCKED_AT_100`** on new **`debug=True`/`False`** branch pairs — not golden log-line asserts.
