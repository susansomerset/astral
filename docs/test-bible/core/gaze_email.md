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
