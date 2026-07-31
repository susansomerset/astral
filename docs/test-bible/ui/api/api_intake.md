# Api Intake

**Test module:** `tests/component/ui/api/test_api_intake.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_intake.py` | `tests/component/ui/api/test_api_intake.py` | yes |


### AST-1015 · AST-952

**AST-1015:** Authenticated `POST /api/candidates/<id>/preamble/validate` — thin wrapper over `validate_preamble_answer`; 200 with structured failure; 404 candidate missing; 400 validation. Primary core: **`docs/test-bible/core/intake.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Route auth / shape / errors | `src/ui/api/api_intake.py` | **`TestAst1015PreambleValidateRoute`** |


---

### AST-1075 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`.

Authenticated `POST /api/candidates/<id>/topic-menu/confirm` and `…/topic-menu/generate` — thin wrappers over intake callables. Confirm structured failure → **500** (unlike preamble validate 200). Generate without confirm stamp → **400**. Primary core: **`docs/test-bible/core/intake.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Route auth / shape / errors | `src/ui/api/api_intake.py` | **`TestAst1075TopicMenuRoutes`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_intake.py::TestAst1075TopicMenuRoutes \
  -q
```

---

### AST-1097 · AST-1096

**Parent:** [AST-1096 — Restart intake gets a 500 error](https://linear.app/astralcareermatch/issue/AST-1096/restart-intake-gets-a-500-error). **Publish:** `origin/sub/AST-1096/AST-1097-restore-archive-active-intake-api`.

Authenticated `POST /api/candidates/<id>/intake/sessions/active/archive` — thin wrapper over `archive_active_intake_session`; **200** with `archived_session_id` / `archived_at` / `intakes_old_count`; **404** when no active session (`LookupError`) or candidate missing / core `ValueError`; **401** without auth. After success, `GET …/sessions/active` is **404**. Core archive / `intakes_old`: **`TestIntakeArchive`**. Frontend Start Over (already POSTs archive): **`tests/component/frontend/pages/test_CandidateIntake.test.tsx`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Route auth / shape / errors + post-archive GET | `src/ui/api/api_intake.py` | **`TestAst1097ArchiveActiveRoute`** |
| Core archive + intakes_old (existing) | `src/core/intake.py` | **`TestIntakeArchive`** |

**Broken / obsolete:** none — route was missing; no prior API assertions to revise.

**Integration:** no existing scenario — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_intake.py::TestAst1097ArchiveActiveRoute \
  tests/component/core/test_intake.py::TestIntakeArchive \
  -q
```
