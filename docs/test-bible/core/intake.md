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


---

### AST-1075 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`.

`build_preamble_packet_snapshot` (name columns + packet context/contact; requires `raw_resume`); `run_topic_menu_preamble_confirm` (Estelle confirm via `do_task` / `_run_intake_task`; whitelist patches; stamp on `accepted`); `generate_topic_menu_from_preamble` (gate on confirm; soft-drop invalid informs; recompute `informs_covered` from survivors; `save_topic_menu(..., revise=True)`). Style D when `debug=True`. API: **`docs/test-bible/ui/api/api_intake.md`**. UI: **`docs/test-bible/frontend/pages.md`** / **`docs/test-bible/frontend/components.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Packet / confirm / generate | `src/core/intake.py` | **`TestAst1075TopicMenuConfirmGenerate`** |

**Broken / obsolete:** none for core — UI handoff revise lives under frontend pages (AST-559 chat-after-preamble → Topic Menu phase).

**Integration:** no existing scenario — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_intake.py::TestAst1075TopicMenuConfirmGenerate \
  tests/component/ui/api/test_api_intake.py::TestAst1075TopicMenuRoutes \
  -q
```
