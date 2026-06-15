# Astral test bible — index and standards



This is the reference to existing tests, including unit/component and integration testing.

**Owner:** **Betty** — maintained via **`qa-astral`**: use it to decide which **existing** tests apply to an issue (manifest-only is OK when coverage already matches), which tests a change **breaks** and must be revised, and when to **append or correct** `docs/test-bible/` so the map stays true. **Engineers do not commit** `docs/test-bible/` or other **test-tree** paths — see **`docs/ASTRAL_TEAM_WORKFLOW.md`** § Test ownership.



## Tree layout



`docs/test-bible/` mirrors `tests/component/` (Python layer folders; React under `frontend/` with folder-level bible files).

Component files hold coverage maps and `### AST-NNN` manifest blocks for that module or folder.

The monolith `docs/ASTRAL_TEST_BIBLE.md` remains until Radia **review-child** confirms this tree (**AST-598**).



### Layer index



| Layer | Bible path | Test tree |

| --- | --- | --- |

| Core | [`core/`](core/) | `tests/component/core/` |

| Data | [`data/`](data/) | `tests/component/data/` |

| External | [`external/`](external/) | `tests/component/external/` |

| Utils | [`utils/`](utils/) | `tests/component/utils/` |

| UI | [`ui/`](ui/) | `tests/component/ui/` |

| Frontend | [`frontend/`](frontend/) | `tests/component/frontend/` |

| Dev | [`dev/`](dev/) | `tests/component/dev/` |



### Retired monolith section map



| Former § | New home |

| --- | --- |

| §2, §4a, §6, §6c, §7.12, Appendix A | this README |

| §7.7, §7.7b, §7.8 | this README |

| §7.13 utils table | `utils/*.md` |

| §7.13b external | `external/*.md` |

| §7.13c data | `data/database.md` + `data/database/*.md` |

| §7.13d core | `core/*.md` |

| §7.13e UI | `ui/*.md`, `ui/api/*.md` |

| §7.13f frontend | `frontend/*.md` |

| §7.13* ticket blocks | `### AST-NNN` in routed component files |



## 2. Where tests live

- **Component tests:** `tests/component/` mirrors `src/` (Python under layer folders; React under `tests/component/frontend/`).
- **Integration tests:** `tests/integration/` is a placeholder only until a separate program opens integration work.
- **Data layer carve-out (§4a):** `tests/component/data/database/` holds cluster files for `src/data/database.py`; see `tests/component/data/database/_README.md`.

## 4a. `database.py` cluster tests

- Keep `src/data/database.py` as one module; split the **test tree** under `tests/component/data/database/` (`test_<cluster>.py`, not `test_database_<cluster>.py`).
- Shared real SQLite fixtures live in `tests/component/data/conftest.py` (`sqlite_in_memory`, `seeded_db`, `db_factory`).
- Thin import smoke stays in `tests/component/data/test_database.py`.

## 6. Branch coverage standard

### 6a. Python (backend + Flask UI/API modules under component test)

- Target **100% branch coverage** for each file committed to **`LOCKED_AT_100`** (`scripts/testing/check_per_file_coverage.py`).
- List intended branches in comment blocks above each `class Test…` (see `tests/component/core/test_tracker.py` when present).
- When such a file reaches 100%, update **§7.12**, the **§7.13** tables (branch lock column), and **`LOCKED_AT_100`** in the same commit.
- **`pragma: no cover`** is allowed only with a short in-file note and bible mention when a branch is impractical to hit in component tests (AST-390: `formatting.py` DOM sibling union + JSON heal edge paths; AST-391: `playwright.py` browser session/crawl paths and `anthropic.py` SDK/heal edge paths; AST-394: `api_admin.py` `update_dtask` `score_floor` elif false exit arc; **AST-471**: `roster.py` unreachable `job_ids` index guard after length parity — **AST-622** retired gazer board-batch legacy `_log.debug` stanza in favor of §1.5.1 contract lines).

### 6b. Frontend (Vitest + RTL under `tests/component/frontend/`)

- **Risk-based**, not branch-count completeness: Prefer tests that anchor real regressions and user-visible flows over enforcing a percentage per source file (**AST-395**).
- **No** mandated per-file 100% branch targets for `src/ui/frontend/src/**`. **`LOCKED_AT_100` in `scripts/testing/check_frontend_coverage.py` stays intentionally empty** unless Product adopts explicit frontend locks later.
- `./scripts/testing/run_component_tests.sh` still runs Vitest with coverage and invokes `check_frontend_coverage.py`; the gate is **tests passing** plus the checker succeeding with **zero** locked files—not full branch saturation.
- Detailed map: §7.13f.
- **QA manifest rules (Betty — all UI tickets):** §6c.

### 6c. QA manifest rules — routed pages and filter UX (**AST-436** UAT lesson)

Betty applies these when writing the **Tests Ready** manifest (**`qa-astral`** §6). **`test-astral`** must run every manifest line, not only the narrowest path.

**Routed page (required when the ticket changes a top-level React route / page file under `src/ui/frontend/src/pages/`):**

- Manifest **must** include at least one Vitest that **renders that page** via `renderWithProviders` (same pattern as existing `test_*Profile*.tsx`, `test_Admin*.tsx`).
- Mock **every** API the page hits on first paint (typical: `/api/candidates`, `/api/shapes/…`, `/api/ui_config` or `/api/system/ui_config`, route-specific GETs). **Component-only** tests (e.g. `TabbedTextArea.customPanels` alone) **do not** satisfy this rule when the product change is wired on the page.
- **Hooks:** page tests catch Rules-of-Hooks violations that child-only tests miss (conditional `return` before `useMemo` / `useCallback`).

**Filter / date / search-param UX (required when the ticket changes controlled filters bound to URL or immediate refetch):**

- Manifest **must** include interaction coverage, not only “default query string” or “API called with today”:
  - Type a **full** date (multi-digit day/month) without the input resetting mid-keystroke.
  - **Blur** or explicit Apply to commit (when product uses draft-then-commit).
  - **Clear** the default filter and confirm behavior (wide fetch, empty param, or explicit reset — per AC).
- Prefer RTL in `tests/component/frontend/pages/test_<Page>.test.tsx`; manual UAT steps are optional add-ons, not substitutes.

## 7.7 External fixtures

- Shared mocks live in `tests/component/external/conftest.py` (Gmail service, Anthropic client shapes). Core-layer tests should reuse these patterns when external I/O is stubbed.

## 7.7b Core fixtures

- `tests/component/core/conftest.py` sets Gmail env defaults for import-time `gmail.py` checks and provides shared `log_entries` for monitor tests.

## 7.8 Data fixtures

- Real in-memory SQLite files via `tests/component/data/conftest.py` (no sqlite mocks). Set `ASTRAL_DB_DIR` per test and patch `database.DB_PATH` to the temp `astral.db`.
- Component tests run on **Python 3.10+** (see Appendix A).

## 7.12 Per-file branch locks

Python/component modules locked at **100%** branches (enforced by `scripts/testing/check_per_file_coverage.py`). Frontend is out of scope here (**§6b**).

- `src/utils/config.py`
- `src/utils/formatting.py`
- `src/external/anthropic.py`
- `src/external/gmail.py`
- `src/external/playwright.py`
- `src/core/monitor.py`
- `src/core/timesheets.py`
- `src/core/tracker.py`
- `src/core/candidate.py`
- `src/core/gazer.py`
- `src/core/dispatcher.py`
- `src/core/consult.py`
- `src/core/builder.py`
- `src/core/agent.py`
- `src/core/roster.py`
- `src/ui/auth.py`
- `src/ui/server.py`
- `src/ui/api/api_system.py`
- `src/ui/api/api_candidate.py`
- `src/ui/api/api_companies.py`
- `src/ui/api/api_jobs.py`
- `src/ui/api/api_admin.py`

### 7.12b **`LOCKED_AT_100` substrate parity** (**AST-471** handoff)

The full harness **`./scripts/testing/run_component_tests.sh`** (zero args) runs **`check_per_file_coverage.py`** across **`LOCKED_AT_100`**. False reds on hotspots such as **`src/core/agent.py`**, **`src/core/roster.py`**, **`src/utils/config.py`** often mean the engineer’s **`dev-<agent>`** tree holds **different Python substrate** than the **ticket publish replay** (**`orientation-astral` § Integration line discipline**) — e.g. **`origin/dev`** lacks symbols added only on **`dev-<agent>`**, or a **`fix(<Linear-id>):`** commit (**`build-astral`** / **`test-astral`** **§9** replay) was applied only locally and never cherry-picked to **`origin/<publish-ref>`**, while **`qa-astral`** on **`dev-betty`** calibrated branch locks against **`merge origin/sub/…`** plus **`merge origin/dev`**.

Before **`[qa-handoff]`** on missing-test theory alone:

1. **`git fetch origin`**
2. **`git merge origin/dev`**
3. **`git merge origin/<publish-ref>`** for **this** ticket (child **`sub/<parent>/<segment>`**, not **`ftr/<ticket-id>`** unless the authoritative **Git branch** block says standalone **`ftr/`**)
4. Re-run **`./scripts/testing/run_component_tests.sh`**

Cherry-pick any ticket-local **`fix(<same ticket id>):`** product SHAs still missing from **`origin/<publish-ref>`**, then rerun the replay. **`ImportError`** on **`config`** / **`database`** when fast-forwarding **`origin/dev`** toward the **`sub/`** tip means **Susan has not landed prior rollup on `origin/dev`** — unblock integration before treating the harness as flaky.

### 7.12c Prep-uat **`origin/ftr/*`** composite (**AST-539**)

**`prep-uat` §6** runs the **full** harness on a throwaway worktree at **`origin/ftr/<parent-segment>`**. That tip often **trails `origin/dev`** on product APIs while **`tests/component`** on **`dev-betty`** already asserts merged children.

| Symptom on ftr tip | Test-tree response (Betty) |
| --- | --- |
| **`DISPATCH_SCHEDULABLE_TASK_KEYS`**, **`RESUME_SECTION_CATALOG`**, AST-551/552/562 tracker helpers, etc. missing | **`pytest.mark.skipif`** on the asserting class or method (`tests/component/conftest.py` **`_SKIP_UNLESS_DISPATCH_SCHEDULABLE`**, local skips beside the test module) |
| Default **`active_provider`** is **deepseek**; mocks target **`send_to_anthropic`** only | **`tests/component/conftest.py`** env keys; **`tests/component/core/conftest.py`** + **`tests/component/ui/conftest.py`** autouse **`anthropic`** provider |
| Strict **AST-501** envelope on **`evaluate_jd`** / encoded consult mocks | **`_strict_batch_llm_ok`** / **`_llm_failure_envelope`** in **`tests/component/core/test_agent.py`** |
| **`LOCKED_AT_100`** files below 100% branch % on composite product | **`run_component_tests.sh`** sets **`ASTRAL_FTR_COVERAGE_INTEGRATION=1`** when **`HEAD`** is contained in **`origin/ftr/*`**; **`check_per_file_coverage.py`** logs and **does not gate** sub-100 locks (pytest + Vitest still must pass) |

Do **not** weaken **`LOCKED_AT_100`** on **`dev-betty`** / child **`sub/*`** publishes — integration skip is for **parent ftr sanity** only.

## Appendix A — Run component tests

From repo root:

```bash
./scripts/testing/run_component_tests.sh
```

Requires **Python 3.10+** (creates `.venv` on first run). `ASTRAL_DB_DIR` defaults to `data/` in the harness. Install deps via `requirements.txt` when using `ASTRAL_PYTHON` instead of the default venv.

With zero arguments the harness selects **`tests/component`** wholesale. Passing paths, node IDs, or **`pytest`** flags after the script name forwards them verbatim as the **`pytest`** target list (narrow manifest runs without silently expanding to the full tree). Only the default full selection runs **`check_per_file_coverage.py`**.

When `src/ui/frontend/package.json` is present, the script also runs Vitest component tests under `tests/component/frontend/` — **only** when invoked with **zero** trailing arguments (narrowed pytest paths skip Vitest).

### AST-664 (parent AST-598)

**Scope:** Global Cursor skills (`qa-child`, `test-child`, `build-child`, `review-child`, `resolve-child`, `dispatch-parent`, `check-linear`, `do-all-the-things`), Betty/engineer **`AGENTS.md`** handoffs, and **`~/.cursor/hooks/pre-commit/engineer.sh`** — manifest contract, engineer ban paths, rollup/shasum, and read-only review pointers use **`docs/test-bible/**`** instead of the monolith. Repo commit on **`origin/sub/AST-598/AST-664-agent-skill-updates-test-bible`**: plan doc + **Implementation record** only (no `src/**`, `tests/**`, or bible content migration — sibling **AST-663**).

**Broken / obsolete tests (AST-664 return pass):** `TestDispatchTasks::test_scheduler_and_run_controls` — `run_task` mock must accept **`ui_initiated`** (**AST-653** on `origin/dev`).
