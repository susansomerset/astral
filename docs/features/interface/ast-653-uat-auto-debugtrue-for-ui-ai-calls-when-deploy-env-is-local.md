# AST-653 — UAT: auto debug=true for UI AI calls when deploy env is local

**Linear:** [AST-653 — UAT: auto debug=true for UI AI calls when deploy env is local](https://linear.app/astralcareermatch/issue/AST-653/uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local)  
**Parent:** [AST-640 — Show environment and up time as read-only at the bottom of nav for admin view only](https://linear.app/astralcareermatch/issue/AST-640/show-environment-and-up-time-as-read-only-at-the-bottom-of-nav-for) (AC reference only)  
**Publish ref:** `origin/sub/AST-640/AST-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local` (origin only)

## Summary

On local deploy (`ASTRAL_DEPLOY_ENV=local`), UI-triggered LLM paths (Ad Hoc **Test**, intake turns/build, dispatch **Run**, candidate **Generate**, board search **Generate**) do not pass `debug=True`, so backend debug-contract lines (AST-538) never emit. This UAT bug adds a single server-side helper that treats deploy env `local` as implicit debug for **UI-initiated** routes only; non-local behavior unchanged (explicit query param / dispatch-row debug flag only). Scheduler AUTO tick and CLI paths are untouched.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/deploy_status.py` | Add `is_local_deploy_env()` and `ui_llm_debug(*, explicit_debug=False)` | utils |
| `src/ui/api/api_intake.py` | `_debug_flag()` → OR explicit query param with `ui_llm_debug(explicit_debug=…)` | ui |
| `src/ui/api/api_admin.py` | `adhoc_test`: pass `debug=ui_llm_debug()` to `run_adhoc_workbench_test`; `run_dtask`: call `run_task(task_id, ui_initiated=True)` | ui |
| `src/core/dispatcher.py` | `run_task(..., ui_initiated=False)`; `_dispatch_one`: `debug = row_flag or (ui_initiated and is_local_deploy_env())` | core |
| `src/core/candidate.py` | `run_candidate_artifact_generation(..., debug=False)` → pass `debug` into `do_task` | core |
| `src/core/boards.py` | `run_board_search_generation(..., debug=False)` → pass `debug` into `do_task` | core |
| `src/ui/api/api_candidate.py` | Pass `debug=ui_llm_debug()` into `run_candidate_artifact_generation` | ui |
| `src/ui/api/api_boards.py` | Pass `debug=ui_llm_debug()` into `run_board_search_generation` | ui |
| `tests/component/utils/test_deploy_status.py` | Tests for `is_local_deploy_env` / `ui_llm_debug` (Betty manifest — engineer runs in test-child) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/core/agent.py` | `run_adhoc_workbench_test`, `run_adhoc`, `do_task` already accept `debug` |
| `src/external/anthropic.py`, `src/external/deepseek.py` | Debug contract already gated on `debug=True` |
| `src/ui/frontend/**` | No UI toggles; local env is the signal per ticket |
| `src/ui/api/api_jobs.py` | `generate_artifacts` only transitions job state — no direct LLM call |

**Out of scope:** deploy footer display, commit/uptime, non-local debug behavior, new UI toggles, scheduler AUTO tick debug, CLI/batch paths, `adhoc/preview` (no LLM call).

---

## Stage 1: Deploy-env debug helpers

**Done when:** `is_local_deploy_env()` returns True only when stripped `ASTRAL_DEPLOY_ENV` equals `local` (case-insensitive); `ui_llm_debug(explicit_debug=True)` is True regardless of env; `ui_llm_debug()` is True on local and False otherwise; `python3 -m py_compile src/utils/deploy_status.py` passes.

1. In `src/utils/deploy_status.py`, after `_resolve_environment()`, add:

   ```python
   def is_local_deploy_env() -> bool:
       raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip()
       return raw.lower() == "local"


   def ui_llm_debug(*, explicit_debug: bool = False) -> bool:
       """True when caller explicitly requested debug or server deploy env is local."""
       return explicit_debug or is_local_deploy_env()
   ```

   ⚠️ **Decision:** Case-insensitive match on `"local"` only — Susan's UAT repro uses `ASTRAL_DEPLOY_ENV=local`; other labels (`staging`, `eu-west`, etc.) must not auto-enable debug. Whitespace-only env (AST-651) → not local.

2. `python3 -m py_compile src/utils/deploy_status.py`

**Ritual:** `code(AST-653): deploy_status local-env debug helpers`

---

## Stage 2: UI API routes — intake, ad hoc, generate delegates

**Done when:** Intake session/turn/build honor local auto-debug; Ad Hoc **Test** passes `debug=True` on local; candidate and board generate POSTs pass debug into core runners.

1. In `src/ui/api/api_intake.py`:
   - Add import: `from src.utils.deploy_status import ui_llm_debug`
   - Replace `_debug_flag()` body with:
     ```python
     def _debug_flag() -> bool:
         explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
         return ui_llm_debug(explicit_debug=explicit)
     ```
   - No route signature changes; existing `debug=_debug_flag()` call sites unchanged.

2. In `src/ui/api/api_admin.py`:
   - Add import: `from src.utils.deploy_status import ui_llm_debug`
   - In `adhoc_test()`, add `debug=ui_llm_debug()` to the `run_adhoc_workbench_test(...)` kwargs (after `task_key_uuid=…`).

3. In `src/ui/api/api_candidate.py`:
   - Add import: `from src.utils.deploy_status import ui_llm_debug`
   - In `generate_artifact()`, change call to:
     `run_candidate_artifact_generation(candidate_id, task_key, live, debug=ui_llm_debug())`

4. In `src/ui/api/api_boards.py`:
   - Add import: `from src.utils.deploy_status import ui_llm_debug`
   - In `generate_search()`, change call to:
     `run_board_search_generation(board_search_id, task_key, None, debug=ui_llm_debug())`

5. `python3 -m py_compile src/ui/api/api_intake.py src/ui/api/api_admin.py src/ui/api/api_candidate.py src/ui/api/api_boards.py`

**Ritual:** `code(AST-653): wire ui_llm_debug on intake adhoc and generate APIs`

---

## Stage 3: Core runners — do_task debug param and UI-only dispatch Run

**Done when:** Candidate/board generate pass `debug` through to `do_task`; admin dispatch **Run** (not scheduler tick) ORs local env into dispatch debug; scheduler AUTO tick unchanged.

1. In `src/core/candidate.py`, update `run_candidate_artifact_generation` signature to add `debug: bool = False` as the fourth parameter (after `live_content`).

2. In the `do_task(...)` call inside that function (~line 731), add `debug=debug`.

3. In `src/core/boards.py`, update `run_board_search_generation` signature to add `debug: bool = False` as the fourth parameter (after `live_content`).

4. In the `do_task(...)` call inside that function (~line 523), add `debug=debug`.

5. In `src/core/dispatcher.py`:
   - Add import: `from src.utils.deploy_status import is_local_deploy_env`
   - Change `run_task` signature to `def run_task(task_id: int, *, ui_initiated: bool = False) -> bool:`
   - After `task = database.get_dispatch_task(task_id)` and before thread spawn, set `task["_ui_initiated"] = ui_initiated` on the task dict (ephemeral key, not persisted to DB).
   - In `_dispatch_one`, replace `debug = bool(task.get("debug"))` with:
     ```python
     ui_initiated = bool(task.get("_ui_initiated"))
     debug = bool(task.get("debug")) or (ui_initiated and is_local_deploy_env())
     ```
   - Leave `_tick_loop` calling `run_task(tid)` with default `ui_initiated=False`.

6. In `src/ui/api/api_admin.py` `run_dtask()`, change `run_task(task_id)` to `run_task(task_id, ui_initiated=True)`.

7. `python3 -m py_compile src/core/candidate.py src/core/boards.py src/core/dispatcher.py`

**Ritual:** `code(AST-653): pass debug through generate runners and UI dispatch Run`

---

## Stage 4: Component tests (Betty manifest / test-child)

**Done when:** `tests/component/utils/test_deploy_status.py` covers local detection and `ui_llm_debug` OR semantics; existing candidate/board/dispatcher tests still pass (default `debug=False` preserved).

Betty adds to **Tests Ready** manifest. If omitted, engineer adds only:

1. In `tests/component/utils/test_deploy_status.py`, add class `TestLocalDeployDebug`:
   - `test_is_local_deploy_env_true`: `monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")` → `assert ds.is_local_deploy_env() is True`
   - `test_is_local_deploy_env_case_insensitive`: `monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "LOCAL")` → True
   - `test_is_local_deploy_env_false_for_staging`: `monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")` → False
   - `test_is_local_deploy_env_false_when_unset`: delete env → False
   - `test_ui_llm_debug_explicit_overrides_non_local`: unset env, `assert ds.ui_llm_debug(explicit_debug=True) is True`
   - `test_ui_llm_debug_local_without_explicit`: `monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")`, `assert ds.ui_llm_debug() is True`
   - `test_ui_llm_debug_false_non_local_no_explicit`: `monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")`, `assert ds.ui_llm_debug() is False`

2. Optional smoke (if Betty includes): monkeypatch `is_local_deploy_env` in `test_api_admin` adhoc test or `test_candidate` generate to assert `do_task`/`run_adhoc_workbench_test` receives `debug=True` — not required if utils tests cover helper.

3. Re-run affected component tests from manifest.

**Ritual:** `test(AST-653): local deploy auto-debug helpers`

---

## Execution contract reminders

- Do **not** edit frontend files or add debug toggles.
- Do **not** enable local auto-debug for scheduler `_tick_loop` / AUTO spawn (`ui_initiated` stays False).
- Do **not** edit `tests/` or `docs/ASTRAL_TEST_BIBLE.md` in **build-child** — Betty owns manifest; engineer runs tests in **test-child**.
- Blocking ambiguity → `🛑` comment on **AST-640** parent.

---

## Self-Assessment

**Scope:** `Single-Component` — One new helper pair in `deploy_status.py` plus thin wiring across known UI-initiated LLM entry points (eight files, no new modules).

**Conf:** `high` — UAT repro maps to missing `debug=True` on existing call sites; AST-538 contract and `do_task`/`run_adhoc` debug params already exist; dispatch UI vs tick split uses explicit `ui_initiated` flag.

**Risk:** `low` — Wrong gating only affects log verbosity on local dev or staging; no state transitions, persistence, or auth changes; non-local production behavior unchanged when env ≠ local.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `ui_llm_debug` / `is_local_deploy_env` in `deploy_status.py`; UI routes call helper instead of duplicating env reads |
| §1.5.1 debug | Honors AST-538 — only sets `debug=True` on UI paths when local or explicit; no new contract emission when False |
| §2.1 config | Reuses existing `ASTRAL_DEPLOY_ENV`; no new config block |
| §2.4 batch | N/A — debug flag only |
| §2.6 state machine | N/A |
| §3.3 imports | UI → utils OK; core dispatcher imports utils for env read (same pattern as deploy footer) |
| §3.5 naming | `is_local_deploy_env`, `ui_llm_debug` match deploy_status module role |

No conflicts requiring `conf-!!-NONE`.
