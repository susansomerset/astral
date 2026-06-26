<!-- linear-archive: AST-653 archived 2026-06-23 -->

## Linear archive (AST-653)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-653/uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-640 — Show environment and up time as read-only at the bottom of nav for admin view only.  
**Blocked by / blocks / related:** parent: AST-640

### Description

## What failed

On a **local** deploy (`ASTRAL_DEPLOY_ENV=local`), UI-triggered AI work (e.g. Anthropic Ad Hoc **Test**, intake LLM turns, dispatch **Run**) does not emit backend debug-contract logging. Susan cannot see enough trace output for what happens to generated content during local dev UAT.

## Expected

When the running server's deploy environment is `local`, every **UI-initiated** AI/LLM call path treats `debug=True` automatically (same backend debug-contract lines as when debug is explicitly enabled). Non-local deploys unchanged — debug only when explicitly requested (query param / dispatch row flag).

## Repro

1. Run Astral locally with `ASTRAL_DEPLOY_ENV=local`; sign in as admin.
2. Confirm nav footer shows environment `local`.
3. Open **Admin → Anthropic Ad Hoc** (or intake chat); run **Test** without any debug toggle.
4. Observe server logs / debug output — insufficient detail on LLM request/response handling vs explicit `debug=true`.

## Parent AC (quoted inline)

> **Server-sourced truth** — Environment, commit, and uptime values come from an authenticated API response; the frontend renders what the API returns and does not infer environment from the URL or build metadata alone.

> **Environment label** — Display exactly one of: `local`, `test`, `staging`, or `production`. The label reflects the running server's deployment context, not the browser hostname alone.

> Sign in as an admin on local dev → bottom of left nav shows `local`, a commit identifier, and an uptime string in the compact format above.

(Susan UAT 2026-06-14: *"if the deploy environment is local, then all the UI generated AI calls are considered as Debug = true. We are not getting enough output on what happens to the results of the content."*)

## Boundaries

* Does **not** change deploy footer display, commit/uptime, or non-local debug behavior.
* Does **not** enable debug for CLI/batch/dispatcher paths that are not UI-initiated unless they already honor dispatch-row debug.
* Does **not** add new UI toggles — local env is the signal.

### Comments

#### radia — 2026-06-15T00:07:51.254Z
**Diff:** `origin/dev`…`origin/sub/AST-640/AST-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local` @ `38a64deb`

## Solid

- **Plan fidelity:** Stages 1–3 match the combined plan — `is_local_deploy_env` / `ui_llm_debug` in `deploy_status.py`; intake `_debug_flag()` ORs explicit query with helper; `adhoc_test` passes `debug=ui_llm_debug()`; candidate/board generate pass `debug` through to `do_task`; dispatch **Run** uses `run_task(..., ui_initiated=True)` and `_dispatch_one` ORs `row.debug` with `(ui_initiated && local)`.
- **Boundaries:** Scheduler tick still calls `run_task(tid)` with default `ui_initiated=False` (`dispatcher.py` ~828). `adhoc/preview` untouched (no LLM). No frontend changes.
- **§1.5.1:** No new ungated contract emission — change only flips `debug=True` on listed UI paths when `ASTRAL_DEPLOY_ENV=local` (or explicit intake query). Existing AST-538 gating in `do_task` / providers unchanged.
- **§3 layer:** UI → `utils.deploy_status` only; `core.dispatcher` → `is_local_deploy_env` matches existing core→utils config/logging pattern. Imports at module top.
- **Tests:** `TestLocalDeployDebug` covers local/staging/unset and explicit OR semantics per manifest.

## Advisory

- **`docs/ASTRAL_TEST_BIBLE.md` §7.13zzt:** Diff also documents **AST-652** list-table autosize (sibling **AST-633** child) — likely `merge-tests` carryover, not AST-653 product scope. Harmless for this ticket; no action unless you want bible rows split by child at merge time.

## fix-now

None.

## discuss

None.

**Katherine:** `resolve-child` — no code changes expected from this review.

#### betty — 2026-06-15T00:02:56.043Z
## QA test manifest (AST-653)

**Publish ref:** `origin/sub/AST-640/AST-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local` @ `38a64deb` (`merge-tests(AST-653): origin/tests 94bbe18e`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `3354efe6684e4a273ea4860482377d7b84e199cb` (§7.13zzs — AST-653 row added)

### Coverage classification

1. **New tests (gap):** `is_local_deploy_env()` / `ui_llm_debug()` OR semantics — plan Stage 4; no log-string golden tests (AST-538 gating only).
2. **Existing coverage (unchanged):** `TestResolveEnvironment`, `TestGetDeployStatusPayload`, AST-646/651 deploy footer tests — product change does not break them.
3. **Broken / obsolete:** none.

### Manifest (run in order)

1. ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/utils/test_deploy_status.py::TestLocalDeployDebug
   ```

2. Regression spot-check (unchanged AST-651 env resolution):

   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/utils/test_deploy_status.py::TestResolveEnvironment
   ```

**Optional smoke (not in manifest):** API wiring for `debug=True` on local — covered indirectly by helper unit tests; manual UAT on local deploy for Ad Hoc **Test** / intake / dispatch **Run** per ticket repro.

— Betty

#### betty — 2026-06-15T00:02:51.418Z
## QA test manifest (AST-653)

**Classification:** Gap — new helper tests for `is_local_deploy_env()` / `ui_llm_debug()` (plan Stage 4). No log-string golden tests (AST-538 gating only). Existing candidate/board/dispatcher tests unchanged — default `debug=False` preserved on non-local paths.

**Publish:** `origin/sub/AST-640/AST-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local` @ `94bbe18e` (`test(AST-653): local deploy auto-debug helpers`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `3354efe6684e4a273ea4860482377d7b84e199cb` (§7.13zzs — AST-653 row added)

### Run (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_deploy_status.py::TestLocalDeployDebug
```

### Manifest

1. **`tests/component/utils/test_deploy_status.py::TestLocalDeployDebug`**
   - `test_is_local_deploy_env_true` — `ASTRAL_DEPLOY_ENV=local` → True
   - `test_is_local_deploy_env_case_insensitive` — `LOCAL` → True
   - `test_is_local_deploy_env_false_for_staging` — `staging` → False
   - `test_is_local_deploy_env_false_when_unset` — unset → False
   - `test_ui_llm_debug_explicit_overrides_non_local` — explicit True regardless of env
   - `test_ui_llm_debug_local_without_explicit` — local env → True without explicit flag
   - `test_ui_llm_debug_false_non_local_no_explicit` — staging, no explicit → False

2. **Regression (unchanged):** `TestResolveEnvironment`, `TestGetDeployStatusPayload`, `TestFormatUptimeSeconds` — no edits required; run if any deploy_status change surprises.

**Broken/obsolete:** None identified.

**Optional smoke (not in manifest):** API-level assert that `run_adhoc_workbench_test` / `do_task` receive `debug=True` on local — utils tests cover helper OR semantics; engineer may spot-check server logs on local UAT per plan Stage 4 note.

— Betty

#### katherine — 2026-06-14T23:58:41.402Z
Plan published for AST-653 (UAT bug — local deploy auto-debug for UI LLM paths).

**Plan doc:** [ast-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local.md](https://github.com/susansomerset/astral/blob/sub/AST-640/AST-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local/docs/features/interface/ast-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local.md) @ `c19ecc63`

**Approach:** Add `is_local_deploy_env()` + `ui_llm_debug()` in `deploy_status.py`; wire on intake, ad hoc Test, candidate/board Generate APIs; pass `debug` into `do_task`; dispatch **Run** only gets local OR via `run_task(..., ui_initiated=True)` — scheduler AUTO tick unchanged.

**Self-assessment**
- **Scope:** `Single-Component` — one helper pair plus thin wiring on eight known UI-initiated LLM entry points.
- **Conf:** `high` — repro is missing `debug=True` on existing call sites; AST-538 plumbing already exists.
- **Risk:** `low` — affects log verbosity only on local dev; non-local production behavior unchanged.

---

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

---

## Review

**Built:** `code(AST-653): deploy_status local-env debug helpers` → `code(AST-653): wire ui_llm_debug on intake adhoc and generate APIs` → `code(AST-653): pass debug through generate runners and UI dispatch Run`  
**Branch:** `origin/sub/AST-640/AST-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local` @ `22d41ce9`

---

## Resolution

**Date:** 2026-06-15  
**Radia review:** fix-now none; discuss none; advisory only (bible §7.13zzt AST-652 carryover from merge-tests — harmless, no action).

**Outcome:** No product changes from review. Shipped as built @ `38a64deb` (product `22d41ce9`, Betty tests `94bbe18e`, merge-tests `38a64deb`). §9a dry-run clean vs `origin/dev` and `origin/ftr/AST-640`.

**UAT verify:** `ASTRAL_DEPLOY_ENV=local`, restart server, sign in as admin — nav footer shows `local`. Run Ad Hoc **Test**, intake turn, or dispatch **Run** without debug toggle; server logs emit AST-538 debug-contract lines. On staging/production (env ≠ local), debug only when explicitly requested.
