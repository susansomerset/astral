# Backfill Collapse Blank Lines (migration script)

**Test module:** `tests/component/scripts/test_backfill_collapse_blank_lines.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/backfill_collapse_blank_lines.py` | `tests/component/scripts/test_backfill_collapse_blank_lines.py` | no |

**Existing coverage (reuse, no rerun required for AST-714 manifest):** **`collapse_consecutive_blank_lines`** helper — `docs/test-bible/utils/formatting.md` (**AST-713**); gazer save-path normalization — `docs/test-bible/core/gazer.md` (**AST-713**).

---

### AST-714 · AST-710

Local-only migration backfill for persisted **`company_data.homepage_text`** and **`job_data.job_description`** rows saved before **AST-713**. Applies shared **`collapse_consecutive_blank_lines`**; **`--dry-run`**, **`--company`**, **`--job`**, and full batch; idempotent skip when already normalized.

| Area | Source | Component tests |
| --- | --- | --- |
| `_normalize_if_changed` skip/changed | `scripts/migrations/backfill_collapse_blank_lines.py` | `TestNormalizeIfChanged` |
| Company dry-run / save / unchanged / not found / error | same | `TestBackfillCompanies` |
| Job dry-run / save / unchanged / not found | same | `TestBackfillJobs` |
| Section selection + dry-run summary | same | `TestRunBackfill` |

**AST-714** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/scripts/test_backfill_collapse_blank_lines.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.
