# gaze_email

**Test module:** `tests/component/core/test_gaze_email.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/gaze_email.py` | `tests/component/core/test_gaze_email.py` | no |

---

### AST-1090 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox`.

Null-candidate mailbox runner: From-bind → unbound age→Trash → bound shapes (ignore / subject URL / html_links / subject_body) → Ruth parse + Playwright scrape → **per-candidate** `job_link_exists_for_candidate` dedupe → `create_meteorite_job` → archive on create or all-duplicate skip; Style D when `debug=True`. Wiring: **`docs/test-bible/core/dispatcher.md`** · config/data/gmail: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`** · **`docs/test-bible/data/database.md`** / jobs cluster · **`docs/test-bible/external/gmail.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Subject URL + unbound stale helpers | `src/core/gaze_email.py` | **`TestAst1090SubjectIsUrl`**, **`TestAst1090UnboundStale`** |
| Runner outcomes (trash/ignore/create/archive/Style D) | `src/core/gaze_email.py` | **`TestAst1090RunGazeEmail`** |

**Broken / obsolete:** none for this new module.

**Integration:** no existing scenarios assert `gaze_email` runner — none revised (do not invent new integration coverage).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py \
  -q
```


### AST-1136 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner`.

Candidate-bound `run_gaze_email`: requires row `candidate_id`; filters From→A; unbound leave/Trash hygiene; stamps `update_candidate_last_email_check` after completed run (incl. zero matches); Style D `run-start` / per-message / `run-complete`. Public `process_gaze_email_messages` for AST-1129 (bound ingest only — no list/Trash/stamp). Config comment-only. Provision/Avail: siblings **AST-1134** / **AST-1135**.

| Area | Source | Component tests |
| --- | --- | --- |
| Bound filter + stamp + process_ helper | `src/core/gaze_email.py` | **`TestAst1136CandidateBoundGazeEmail`**; revised **`TestAst1090RunGazeEmail`** |

**Broken / obsolete (Betty revision):** null-shell `run_gaze_email({})` calls (now require `candidate_id`); stamp stub required on runner tests. **AST-1140 return:** `_handle_bound` mock returns must be 5-tuple when tip includes selected-ids outcome string.

**Integration:** none — no existing scenario asserts candidate-bound gaze runner; do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail \
  tests/component/core/test_gaze_email.py::TestAst1136CandidateBoundGazeEmail \
  -q
```

### AST-1140 · AST-1129

**Parent:** [AST-1129 — Manage Email — select inbox messages and Land Meteorite](https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite). **Publish:** `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint`.

`run_gaze_email_selected_ids` ingests only explicit Astral inbox ids through shared `_handle_bound` (bind / route / scrape / dedupe / METEORITE_NEW / archive); skip outcomes for missing / unbound / unmatched; no `last_email_check` stamp, no Create strip/extract, no unbound Trash. Style D via `debug_func_selected` when `debug=True`. Config: **`docs/test-bible/utils/config.md`**. Admin HTTP / React = siblings **AST-1141** / **AST-1142**.

| Area | Source | Component tests |
| --- | --- | --- |
| Selected-ids skips + bound ingest + forbidden call sites + debug gate | `src/core/gaze_email.py` | **`TestAst1140RunGazeEmailSelectedIds`** |
| Selected-ids config vocabulary | `src/utils/config.py` | **`TestAst1140GazeEmailSelectedConfig`** |
| Candidate-bound runner + process_ helper (AST-1136 on tip) | `src/core/gaze_email.py` | **`TestAst1136CandidateBoundGazeEmail`**; revised **`TestAst1090RunGazeEmail`** |

**Broken / obsolete (Betty return pass — resolve `origin/dev` merge):** AST-1136 `_handle_bound` mocks must return 5-tuple `(processed, passed, failed, errors, outcome)` after AST-1140 helper change; sub tip must carry AST-1136 + AST-1140 test/bible surface from `origin/tests` / `origin/dev`.

**Integration:** none — no existing scenario asserts Land Meteorite selected-ids; do not invent new coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py::TestAst1140RunGazeEmailSelectedIds \
  tests/component/utils/test_config.py::TestAst1140GazeEmailSelectedConfig \
  tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail \
  tests/component/core/test_gaze_email.py::TestAst1136CandidateBoundGazeEmail \
  -q
```
