# AST-380 — Astral Testing

<!-- linear-archive: AST-380 archived 2026-06-15 -->

## Linear archive (AST-380)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-380/astral-testing  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

For Live projects, we need test coverage.

Specifically, we need:

* **Component tests** — unit-style tests with **100% branch coverage** per source file (see `docs/ASTRAL_TEST_BIBLE.md`).
* **Integration tests** — **out of scope** for this epic until a separate project is opened. `tests/integration/` stays a placeholder only.

Before we create component tests, we should review each component by a set of criteria to determine if the component should be refactored before tests are generated for it ("Don't test the mess"). [AST-382](https://linear.app/astralcareermatch/issue/AST-382/component-review) covers that review pass.

---

## Harness status (done)

* `tests/component/` mirror tree, pytest + Vitest config, layer `conftest.py` fixtures, `scripts/testing/run_component_tests.sh`, `scripts/testing/check_per_file_coverage.py`, and the **Test Bible** runbook.
* Worked example: `src/core/tracker.py` → `tests/component/core/test_tracker.py` (100% branch coverage).

## Already at 100% branch coverage (Python)

* `src/core/tracker.py`
* `src/utils/cost_calculator.py`, `logging.py`, `network.py`, `rubric_text.py`

## Close the gap

* `src/utils/formatting.py` — finish remaining branches (or justified `pragma: no cover`).

---

## Betty sequence guide (build subissues in this order)

Read `docs/ASTRAL_TEST_BIBLE.md` before each ticket. One test file per source file unless the Bible carve-out applies (`database.py`). Each ticket ends with: full branch coverage on its files, §7.13 map updated, and paths appended to `LOCKED_AT_100` in `scripts/testing/check_per_file_coverage.py`.

0. [AST-382](https://linear.app/astralcareermatch/issue/AST-382/component-review) — component review (refactor gate; complete before locking coverage on messy files).
1. [AST-390](https://linear.app/astralcareermatch/issue/AST-390/component-branch-coverage-utils-layer) — utils layer (`config.py`, finish `formatting.py`).
2. [AST-391](https://linear.app/astralcareermatch/issue/AST-391/component-branch-coverage-external-layer) — external layer (`anthropic.py`, `gmail.py`, `playwright.py`).
3. [AST-392](https://linear.app/astralcareermatch/issue/AST-392/component-branch-coverage-data-layer-databasepy) — data layer (`database.py`; optional `tests/component/data/database/` split).
4. [AST-393](https://linear.app/astralcareermatch/issue/AST-393/component-branch-coverage-core-layer) — core layer (eight modules; `tracker.py` already done).
5. [AST-394](https://linear.app/astralcareermatch/issue/AST-394/component-branch-coverage-ui-flask-layer) — UI Flask layer (`auth.py`, `server.py`, `api/*.py`).
6. [AST-395](https://linear.app/astralcareermatch/issue/AST-395/component-branch-coverage-react-frontend) — React frontend (`lib/`, `contexts/`, `components/`, `pages/`, `App.tsx`, `routes.tsx`).

**Not in this epic:** integration tests, `src/main.tsx`, `src/**/__init__.py`.

### Comments

#### chuckles — 2026-05-17T22:30:30.748Z
## Landed on origin/dev — Chuckles

**finish-up AST-380** — no `ftr/` or `sub/` branches on origin (work merged earlier via Betty integration branches).

- Verified **AST-390–395** and **AST-382** commits reachable from **`origin/dev`**
- No merge required; **`dev`** already matches **`origin/dev`**
- Children already **PR Ready** (assignee unchanged): AST-390, AST-391, AST-392, AST-393, AST-394, AST-395

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
