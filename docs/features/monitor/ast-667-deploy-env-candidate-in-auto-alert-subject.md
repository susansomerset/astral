<!-- linear-archive: AST-667 archived 2026-06-23 -->

## Linear archive (AST-667)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-667/deploy-env-and-candidate-last-name-in-auto-alert-subject-include  
**Status at archive:** Done  
**Project:** Astral Monitor  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-660 — Include ASTRAL_DEPLOY_ENV in email alert header  
**Blocked by / blocks / related:** parent: AST-660

### Description

## Git branch (authoritative)

Per **orientation § Branch law**: child `sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject`. Created at **dispatch-parent**.

## What this implements

Replace the hardcoded `[Astral]` prefix on AUTO dispatch error alert email subjects with the deploy environment label from `ASTRAL_DEPLOY_ENV` and the owning candidate's profile last name, formatted as `[{deploy_label}/{last_name}]`. Wire the dispatcher to pass candidate context into `auto_run_error` so monitor can resolve the label. Reuse existing deploy-env resolution semantics (AST-646 / AST-651).

## Acceptance criteria

1. With `ASTRAL_DEPLOY_ENV=local`, an AUTO error alert subject begins with `[local/{LastName}]` for the owning candidate, followed by the existing `{task_key} {final_status}: …` summary and batch id suffix.
2. With `ASTRAL_DEPLOY_ENV=eu-west`, subject prefix is `[eu-west/{LastName}]` (raw deploy label, case preserved).
3. With `ASTRAL_DEPLOY_ENV` unset or whitespace-only, deploy label in the bracket is `Astral`; candidate last name suffix still applies when resolvable.
4. Candidate last name appears for AUTO errors across entity types (job, company, board_search, candidate) by resolving the owning candidate for the run.
5. Email body content and alert trigger conditions (AUTO mode, `total_errors > 0`) are unchanged from AST-344.
6. Monitor component tests cover deploy-label prefix, candidate last name suffix, and fallback when deploy env or last name is unavailable.

## Boundaries

* AUTO error alert subject line only — no body, recipient, or trigger changes.
* No UI or new alert types.
* Sibling scope: none (single child epic).

## Notes for planning

* Primary touch: monitor subject formatting; dispatcher call site passes `candidate_id` (and entity context if needed for last-name resolution).
* Reuse deploy env helper from `deploy_status.py` — do not duplicate allowlist logic.
* Last name from `candidate_data.profile.last` per candidate data model.

### Comments

#### radia — 2026-06-15T06:34:45.677Z
**Review** — `origin/dev...origin/sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject` @ `e528330e` (includes doc commit).

### fix-now
None.

### discuss
None.

### What's solid
- **Plan fidelity:** Stages 1–3 match diff — `get_deploy_label()`, monitor subject helpers + `candidate_id` param, dispatcher wires `candidate_id` in `_dispatch_one` finally block; gmail/body/trigger guards unchanged.
- **AC 1–6:** `TestAutoRunErrorSubjectPrefix` covers `local`/`eu-west`/unset/whitespace deploy labels, last-name suffix and omit paths; dispatcher test asserts `auto_run_error` arg[4]; legacy alert test isolates host env with `delenv`.
- **§1.3 DRY:** Single env read via `_resolve_environment()` wrapper.
- **§3.3 layers:** `core` → `utils.deploy_status` + existing `data.database`; no UI/external violations.

### advisory
- `_resolve_candidate_last_name` uses `or {}` on optional profile fields — bounded omission of `/LastName` when data missing; fine for non-raising alert formatting.

**Doc:** `docs/features/monitor/ast-667-deploy-env-candidate-in-auto-alert-subject.md` § Review updated on publish ref.

#### betty — 2026-06-15T06:25:08.889Z
[check-linear]

**[qa-handoff] cleared.** `TestAutoRunError::test_sends_alert_with_log_body` now `monkeypatch.delenv("ASTRAL_DEPLOY_ENV")` before the alert call so `[Astral]` fallback is isolated from host env (epic worktree `local` was the failure Hedy saw).

**Republish:** `origin/sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject` @ `b7784856` (`merge-tests(AST-667): origin/tests 5b657ff8`). Manifest unchanged; same narrowed run as prior QA comment.

**Assignee → Hedy** for `test-child`.

#### hedy — 2026-06-15T06:19:21.165Z
[qa-handoff]

**Command:** `./scripts/testing/run_component_tests.sh tests/component/core/test_monitor.py tests/component/core/test_dispatcher.py::TestDispatchOne::test_auto_run_error_on_auto_failures tests/component/utils/test_deploy_status.py::TestGetDeployLabel`

**Result:** 15 passed, 1 failed — `TestAutoRunError::test_sends_alert_with_log_body`

**Failure:** Subject is `[local] qualify_job_listings failure: …` but the test still asserts `startswith("[Astral] …")`. Epic worktree has `ASTRAL_DEPLOY_ENV=local` in the process env; product behavior is correct per AC.

**Why test/manifest, not product:** Manifest item 1 claims `test_sends_alert_with_log_body` was updated for deploy-label brackets, but line 41 still hardcodes `[Astral]` with no `monkeypatch.delenv("ASTRAL_DEPLOY_ENV")`. The new `TestAutoRunErrorSubjectPrefix` cases pass; only this legacy assertion is stale.

**Ask:** Patch `test_sends_alert_with_log_body` to `delenv` deploy env (or assert `[{get_deploy_label()}]` / bracket prefix without hardcoding Astral) so it is isolated from host env. Republish manifest + reassign @Hedy.

@Betty White

#### betty — 2026-06-15T06:17:54.443Z
## QA test manifest (AST-667)

**Publish:** `origin/sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject` @ `d4f1c08f`  
**Tests commit:** `origin/tests` @ `d2f5acf9` (`merge-tests(AST-667): origin/tests d2f5acf9`)

### Existing coverage revised

1. **`tests/component/core/test_monitor.py::TestAutoRunError::test_sends_alert_with_log_body`** — subject prefix updated from hardcoded `[Astral]` to deploy-label bracket (default `Astral` when env unset).

### New / expanded tests

2. **`tests/component/core/test_monitor.py::TestAutoRunErrorSubjectPrefix`** — deploy label + candidate last name (AC 1–3, 6):
   - `test_local_env_with_candidate_last_name`
   - `test_eu_west_preserves_case`
   - `test_unset_env_falls_back_to_astral_without_last_name`
   - `test_unset_env_with_candidate_last_name`
   - `test_whitespace_env_falls_back_to_astral`
   - `test_missing_candidate_last_name_omits_suffix`
   - `test_missing_candidate_row_omits_suffix`

3. **`tests/component/utils/test_deploy_status.py::TestGetDeployLabel`** — `get_deploy_label()` wraps `_resolve_environment()` with `Astral` fallback.

4. **`tests/component/core/test_dispatcher.py::TestDispatchOne::test_auto_run_error_on_auto_failures`** — asserts `candidate_id` is passed as 5th positional arg to `auto_run_error` (AC 4).

### Run command (narrowed)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_monitor.py \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_auto_run_error_on_auto_failures \
  tests/component/utils/test_deploy_status.py::TestGetDeployLabel
```

**Pass criterion:** all manifest lines green (pytest-only; no zero-arg `LOCKED_AT_100` gate on this narrowed run).

### Test bible (on publish ref)

| Path | sha256 |
| --- | --- |
| `docs/test-bible/core/monitor.md` | `2f3cf3cc472cf5b0f1ad9abe6f37a9dd1d6a1285fb24fb6a26572718d6a83f30` |
| `docs/test-bible/utils/deploy_status.md` | `ed55ab990e4ef50a7d24b1f71052e35df7bf46350bf1eea68e79d8ceae5ae58f` |

— Betty

#### hedy — 2026-06-15T06:08:25.775Z
Plan: [ast-667-deploy-env-candidate-in-auto-alert-subject.md](https://github.com/susansomerset/astral/blob/sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject/docs/features/monitor/ast-667-deploy-env-candidate-in-auto-alert-subject.md)

Three stages: (1) public `get_deploy_label()` in `deploy_status.py` reusing `_resolve_environment()` with `Astral` fallback; (2) monitor subject helpers + `candidate_id` on `auto_run_error`; (3) dispatcher passes task `candidate_id`. Betty manifests monitor/dispatcher component tests for deploy prefix, last-name suffix, and fallbacks.

**Self-Assessment**
- **Scope:** `scope-Single-Component` — `deploy_status.py`, `monitor.py`, `dispatcher.py` only; no trigger/body/UI changes.
- **Conf:** `conf-high` — existing deploy-env and `profile.last` paths; literal `[Astral]` swap at one call site.
- **Risk:** `risk-low` — subject-line triage only; monitor never-raises contract preserved.

---

# AST-667 — Deploy env and candidate last name in AUTO alert subject

**Linear:** [AST-667 — Deploy env and candidate last name in AUTO alert subject (Include ASTRAL_DEPLOY_ENV in email alert header)](https://linear.app/astralcareermatch/issue/AST-667/deploy-env-and-candidate-last-name-in-auto-alert-subject-include)

**Parent:** [AST-660 — Include ASTRAL_DEPLOY_ENV in email alert header](https://linear.app/astralcareermatch/issue/AST-660/include-astral-deploy-env-in-email-alert-header) (definition reference only)

**Publish ref:** `origin/sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject` (origin only)

## Summary

AUTO dispatch error alert emails (AST-344) still hardcode `[Astral]` in the subject. This child replaces that bracket with `[{deploy_label}/{last_name}]` when both are available, using the same stripped `ASTRAL_DEPLOY_ENV` semantics as the admin nav footer (AST-646 / AST-651) and the dispatch task's owning candidate profile last name (`candidate_data.profile.last`). Deploy label falls back to `Astral` when env is unset or whitespace-only; last-name segment is omitted when profile data has no non-empty `last`. Dispatcher passes `candidate_id` into `auto_run_error`; email body, recipient, and trigger conditions are unchanged.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/deploy_status.py` | Add public `get_deploy_label() -> str` wrapping `_resolve_environment()` with `"Astral"` fallback | utils |
| `src/core/monitor.py` | Subject prefix helpers; extend `auto_run_error` with `candidate_id`; import `get_deploy_label` | core |
| `src/core/dispatcher.py` | Pass `candidate_id` into `monitor.auto_run_error(...)` call site in `_dispatch_one` | core |
| `tests/component/core/test_monitor.py` | Cover deploy prefix, last-name suffix, fallbacks (Betty manifest — engineer runs in test-child) | test |
| `tests/component/core/test_dispatcher.py` | Assert `auto_run_error` receives `candidate_id` when AUTO errors fire (Betty manifest if needed) | test |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/external/gmail.py` | Unchanged — still receives formatted subject string |
| `src/utils/config.py` | `support_email` unchanged |
| `tests/component/utils/test_deploy_status.py` | `_resolve_environment()` behavior unchanged; optional Betty add for `get_deploy_label` |

**Out of scope:** email body, recipient, alert trigger (`total_errors > 0`, AUTO only), UI paths, new alert types, allowlist for deploy labels.

---

## Stage 1: Deploy label helper

**Done when:** `get_deploy_label()` returns stripped non-empty `ASTRAL_DEPLOY_ENV` verbatim (case preserved) or `"Astral"` when unset/whitespace-only; `python3 -m py_compile src/utils/deploy_status.py` passes.

1. In `src/utils/deploy_status.py`, after `_resolve_environment()`, add:

   ```python
   def get_deploy_label() -> str:
       """Display label for deploy env in alerts and UI; Astral when unset."""
       return _resolve_environment() or "Astral"
   ```

   ⚠️ **Decision:** Reuse `_resolve_environment()` — no second `os.environ` read path and no allowlist. Matches AST-646 nav footer: any non-empty stripped string is valid (`eu-west`, `staging`, etc.).

2. `python3 -m py_compile src/utils/deploy_status.py`

**Ritual:** `code(AST-667): deploy label helper for alert subject`

---

## Stage 2: Monitor subject prefix and candidate last name

**Done when:** `auto_run_error` builds subjects `[local/Somerset] {task_key} …` per AC; omits `/LastName` when profile `last` missing; uses `[Astral]` deploy fallback when env unset; never raises; `python3 -m py_compile src/core/monitor.py` passes.

1. In `src/core/monitor.py`, add import:

   ```python
   from src.utils.deploy_status import get_deploy_label
   ```

2. In the Helpers section (below `_format_log_body`), add:

   ```python
   def _resolve_candidate_last_name(candidate_id: str) -> str | None:
       """Profile last name for subject triage; None when missing or empty."""
       if not (candidate_id or "").strip():
           return None
       row = database.get_candidate(candidate_id.strip())
       if not row:
           return None
       profile = (row.get("candidate_data") or {}).get("profile") or {}
       last = (profile.get("last") or "").strip()
       return last or None


   def _format_alert_subject_prefix(deploy_label: str, last_name: str | None) -> str:
       """Bracket prefix: [deploy] or [deploy/LastName]."""
       if last_name:
           return f"[{deploy_label}/{last_name}]"
       return f"[{deploy_label}]"
   ```

3. Change `auto_run_error` signature to:

   ```python
   def auto_run_error(
       task_key: str,
       batch_id: str,
       accumulated: dict,
       final_status: str,
       candidate_id: str = "",
   ) -> None:
   ```

4. Replace the hardcoded subject block (lines building `f"[Astral] {task_key} …"`) with:

   ```python
   deploy_label = get_deploy_label()
   last_name = _resolve_candidate_last_name(candidate_id)
   prefix = _format_alert_subject_prefix(deploy_label, last_name)
   subject = (
       f"{prefix} {task_key} {final_status}: "
       f"{total_errors} error(s) / {total_processed} processed | {batch_id}"
   )
   ```

   ⚠️ **Decision:** Owning candidate is always the dispatch task's `candidate_id` (job, company, board_search, and candidate entity runs are all scoped to that candidate). No per-entity last-name lookup — matches parent AC #4 without extra DB hops on batch entities.

5. Update the `auto_run_error` docstring to document `candidate_id` and the new subject prefix shape.

6. `python3 -m py_compile src/core/monitor.py`

**Ritual:** `code(AST-667): AUTO alert subject deploy env and candidate last name`

---

## Stage 3: Dispatcher wires candidate_id

**Done when:** AUTO error path passes `candidate_id` from `_dispatch_one` into `auto_run_error`; existing CLICK / zero-error paths unchanged; `python3 -m py_compile src/core/dispatcher.py` passes.

1. In `src/core/dispatcher.py`, in `_dispatch_one` `finally` block, change the alert call from:

   ```python
   monitor.auto_run_error(task_key, dispatch_ledger_id, accumulated, final_status)
   ```

   to:

   ```python
   monitor.auto_run_error(
       task_key, dispatch_ledger_id, accumulated, final_status, candidate_id
   )
   ```

   `candidate_id` is already bound at line 479 from `task["candidate_id"]`.

2. `python3 -m py_compile src/core/dispatcher.py`

**Ritual:** `code(AST-667): pass candidate_id to auto_run_error`

---

## Acceptance criteria mapping (build + test-child)

| AC | Verification |
|----|----------------|
| 1. `ASTRAL_DEPLOY_ENV=local` → `[local/{LastName}]` prefix | `test_monitor.py` monkeypatch env + candidate profile |
| 2. `eu-west` → `[eu-west/{LastName}]`, case preserved | same |
| 3. unset env → `[Astral/…]` or `[Astral]` | same |
| 4. last name across entity types | dispatcher passes task `candidate_id` for all entity types — no entity-branch in monitor |
| 5. body + trigger unchanged | no edits to `_format_log_body`, gmail call, or dispatcher guard |
| 6. component tests | Betty manifest updates `test_monitor.py` (and dispatcher alert call if needed) |

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Three production files (`deploy_status.py`, `monitor.py`, `dispatcher.py`) plus monitor/dispatcher component tests; no UI, config blocks, or alert trigger changes.

**Conf:** `conf-high` — Deploy env resolution and `profile.last` paths already exist; subject format is a straight replacement of the `[Astral]` literal with two small helpers and one extra argument at the dispatcher call site.

**Risk:** `risk-low` — Wrong subject text affects inbox triage only; dispatch, ledger, and email delivery paths are untouched and monitor still never raises to the caller.

---

## Plan vs ASTRAL_CODE_RULES (§8 self-review)

- **§1.3 DRY:** `get_deploy_label()` centralizes env read; monitor does not duplicate `_resolve_environment` logic.
- **§2.1 config:** No new config keys; deploy label from env per established AST-646 pattern; `support_email` unchanged.
- **§2.4 batch processing:** No batch claim/release changes; `batch_id` in subject suffix unchanged.
- **§2.6 state machine:** No state transitions.
- **§3.3 imports:** `monitor` imports `utils.deploy_status` and `data.database` (already imports database); no UI or external layer violations.
- **§3.5 naming:** snake_case `get_deploy_label`, `_resolve_candidate_last_name`, `_format_alert_subject_prefix`.

No conflicts identified.

---

## Review

**Built:** `code(AST-667): deploy label helper for alert subject` → `code(AST-667): AUTO alert subject deploy env and candidate last name` → `code(AST-667): pass candidate_id to auto_run_error`  
**Branch:** `origin/sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject` @ `b7784856`  
**Diff baseline:** `origin/dev...origin/sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Three production files + tests match stages 1–3; dispatcher passes `candidate_id` from `_dispatch_one`; body/trigger/gmail path untouched. |
| AC 1–6 | `TestAutoRunErrorSubjectPrefix` covers env labels, case, Astral/whitespace fallbacks, last-name suffix/omit; dispatcher asserts arg[4]; existing AST-393 alert test isolated with `delenv`. |
| §1.3 DRY | `get_deploy_label()` wraps `_resolve_environment()` — single env read path. |
| §3.3 layers | `core` → `utils.deploy_status` + existing `data.database`; no UI/external violations. |
| §2.4 / §2.6 | No batch claim or state-machine changes. |

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

Proceed to **resolve-child** (no code changes required).

### Advisory

- `_resolve_candidate_last_name` uses `or {}` on optional profile fields — bounded: missing data omits `/LastName` rather than inventing a value; acceptable for non-raising alert formatting (§3.2 monitor never raises).

---

## Resolution

**Date:** 2026-06-15  
**Review:** Radia @ `e528330e` — **fix-now:** none; **discuss:** none.

No product changes required. Cherry-picked Radia review doc onto epic worktree; manifest re-run green (16 passed). §9a dry-run clean into `origin/dev` and `origin/ftr/AST-660-include-astral-deploy-env-in-email-alert-header`. Advanced to **User Testing**.

