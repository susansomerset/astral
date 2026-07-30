# Intake

**Test module:** `tests/component/core/test_intake.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/intake.py` | `tests/component/core/test_intake.py` | yes |

### AST-1014 · AST-952

Persist remapped context `raw_resume` / `raw_profile` / `raw_sample`. Primary: **`docs/test-bible/core/candidate.md`** § AST-1014 — revised **`TestIntakeSessionFlow`**.


### AST-1015 · AST-952

**AST-1015:** `validate_preamble_answer` — Ruth `do_task(preamble_validate_response)` → Valid / Try Again / Escalate; empty answer allowed; unrecognized outcome never Valid; no `save_candidate_data`; Style-D `debug=` found|outcome. Config: **`docs/test-bible/utils/config.md`**. API: **`docs/test-bible/ui/api/api_intake.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Core callable + outcomes + no writes + debug | `src/core/intake.py` | **`TestAst1015ValidatePreambleAnswer`** |
