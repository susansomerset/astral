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

