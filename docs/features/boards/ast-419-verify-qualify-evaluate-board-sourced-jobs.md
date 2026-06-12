# AST-419 — Verify qualify and evaluate for board-sourced jobs

Parent: **AST-379**. Verification ticket (manifest + tests): board-sourced jobs reach normal dispatch (`validate_title` → `qualify_job_listings` → `scrape_jd` → `evaluate_jd`).

## Review

**Reviewer:** Radia  
**Refs reviewed:** `git diff origin/dev...origin/ftr/AST-419` @ `fba9ac5775318b30b8e2b3616480621c21e0e229`  
**Orientation publish-ref note:** `origin/sub/AST-379/AST-419-design-data-flow-for-astral-boards` resolves to `13dfe346`, an ancestor of current `origin/dev` (three-dot diff vs `origin/dev` is empty). Actionable implementation tip matches Betty’s comment: **`origin/ftr/AST-419`** @ **`fba9ac57`**.

### What’s solid (intent)

- **Plan fidelity:** Diff adds §**7.13v** in `docs/ASTRAL_TEST_BIBLE.md` and two component tests scoped to AST-419: ingest→`NEW` with `board_search_id`, then full qualify/evaluate chain via **`get_new_job_batch`** / **`clear_job_batch`** with consult/scrape I/O mocked — aligned with acceptance criteria **7** and ticket boundaries (no consult product fixes claimed).
- **Rubric / architecture (diff-only):** Test module uses top-level imports; no layer violations in **`src/`** (no production files changed). Fixture pattern targets real SQLite with explicit schema flags reset.

### Issues

| Severity | Bucket | Finding |
|----------|--------|---------|
| **fix-now** | Tests / integration | **`pytest` does not collect** on published tip: `ImportError: cannot import name 'BOARDS_CONFIG' from src.utils.config`. On the same tree, **`ingest_board_listings`** is not defined in `src/core/tracker.py`, and board-related symbols are absent from `src/data/database.py` / `src/utils/config.py` (grep). The new tests and bible row assume APIs and config that are **not present** on `origin/dev` or on **`fba9ac57`**. Verification cannot run until sibling ingest/schema work (per ticket: **AST-417** / **AST-418**) is merged and this branch is **rebased** (or equivalent integration line), then manifest re-run. |
| advisory | Tests | `test_board_job_reaches_qualify_and_evaluate_dispatch` uses literal **`"JD_READY"`** when claiming the evaluate batch; prefer `CONSULT_CONFIG["scrape_jd"]["pass_state"]` for consistency with other assertions once tests are runnable. |
| advisory | Tests | **`_SCHEMA_FLAGS`** in `tests/component/core/conftest.py` may drift if `database.py` adds new `_…_schema_ensured` guards; a short comment or alignment check reduces silent skew. |

### Recommended actions

1. **Engineer:** Integrate **board ingest + config + schema** from dependency tickets, rebase **`ftr/AST-419`**, confirm `./scripts/testing/run_component_tests.sh tests/component/core/test_board_sourced_qualify_evaluate.py` is green, re-publish tip.  
2. Optional: Replace hardcoded `JD_READY` with config-driven pass state after integration.

**Git:** Doc commit **`bae25679`** — **`docs(AST-419): Radia review — qualify/evaluate verification blocked on missing board deps`**. Cherry-pick onto **`dev-<agent>`** from **`origin/ftr/AST-419`**.

## Resolution

**Engineer:** Betty (verification / resolve on **`dev-betty`**)  
**Dates:** review **2026-05-23** Radia (`review-astral`); integration + this appendix **2026-05-24**

### Vs Radia `review-astral`

| Item | Outcome |
|------|---------|
| **fix-now** (collection failed on isolated **`fba9ac57`** — missing **`BOARDS_CONFIG`**, **`ingest_board_listings`**, board schema vs **`origin/dev`**) | **Resolved on integration line.** Merged **`origin/ftr/AST-419`** into **`dev-betty`** at **`a63a4635`** (first parent **`3cf46062`** already carried board ingest / schema / config from sibling board work). Merged **`docs/ASTRAL_TEST_BIBLE.md`** keeping §§**7.13o–7.13u** plus §**7.13v**. `./scripts/testing/run_component_tests.sh tests/component/core/test_board_sourced_qualify_evaluate.py` — **918 passed**, **1 skipped** across full harness invocation; **`TestBoardSourcedQualifyEvaluateAst419`** **passed**. |
| **advisory** — literal **`JD_READY`** vs **`CONSULT_CONFIG["scrape_jd"]["pass_state"]`** | **Unchanged** in this pass per **`resolve-astral` §9** (single engineer commit excludes test-tree‑only tweaks). Equivalent today; Betty may tighten later. |
| **advisory** — **`_SCHEMA_FLAGS`** vs **`database.py`** ensured-flag drift | Noted — watch **`tests/component/core/conftest.py`** when DDL gates move. |

### Publish

Publication: integration merge **`a63a4635`**, plus this resolution doc (**commit in Linear comment**), pushed to **`origin/ftr/AST-419`** and **`origin/sub/AST-379/AST-419-design-data-flow-for-astral-boards`**.

Parent epic **AST-379** — child ready for **`prep-uat`** when Chuckles merges per workflow.
