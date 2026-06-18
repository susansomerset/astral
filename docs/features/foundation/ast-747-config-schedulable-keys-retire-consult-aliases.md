# Config schedulable keys retire consult aliases (Task keys vs. dispatch task keys)

**Linear:** [AST-747](https://linear.app/astralcareermatch/issue/AST-747/config-schedulable-keys-retire-consult-aliases-task-keys-vs-dispatch-task-keys)  
**Parent:** [AST-736](https://linear.app/astralcareermatch/issue/AST-736/task-keys-vs-dispatch-task-keys)  
**Publish ref:** `origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases`

## Summary

Retire `consult_do`, `consult_get`, and `consult_like` from the schedulable dispatch vocabulary in `src/utils/config.py`. Collapse the consult→grade alias map so schedulable defaults, batch-call-mode grouping, scored-trigger helpers, and admin validation use `grade_do`, `grade_get`, and `grade_like` — the same strings as `TASK_CONFIG` and Manage Tasks. Hard cutover in config paths: no read-time alias acceptance for retired keys. Admin API rejects new `consult_*` dispatch rows with an explicit error. Product rules doc updated; test-bible consult/dispatch wording is a Betty handoff for epic AC #6.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `consult_*` with `grade_*` in schedulable/batch-mode frozensets; add `DISPATCH_RETIRED_TASK_KEYS`; remove `_CONSULT_TASK_TO_AGENT_TASK`; identity `resolve_dispatch_task_config_key`; update trigger/entity helpers | utils |
| `src/ui/api/api_admin.py` | Reject retired `consult_*` on `POST /api/admin/dispatch_tasks`; verify `task_keys` payload for `grade_*` defaults | ui |
| `docs/ASTRAL_CODE_RULES.md` | Dispatch pipeline table + §2.7 wording: operator-facing schedulable names are `grade_*` | docs |

**Out of scope (sibling tickets — do not touch):**

| Ticket | Owner | Scope |
|--------|-------|-------|
| AST-748 | Hedy | DB row rename migration; `consult.py` / `dispatcher.py` runtime cutover; `_CHUNK_EXHAUST_CONSULT_JOB_KEYS`; `_INPUT_STATE_TO_TASK` legacy map values |
| AST-749 | Katherine | Scheduled Actions React UI; dispatch modals |

**QA manifest (Betty — not engineer commits):** Update `tests/component/utils/test_config.py` schedulable-key assertions; `tests/component/ui/api/test_api_admin.py` task_keys derivation tests; `docs/test-bible/utils/config.md`, `docs/test-bible/ui/server.md`, `docs/test-bible/core/consult.md`, `docs/test-bible/core/dispatcher.md`, and `docs/ASTRAL_TEST_BIBLE.md` consult/dispatch sections — replace operator-facing `consult_*` schedulable names with `grade_*` per parent AC #6.

## Prerequisite (build gate — not a commit stage)

**Done when:** Epic worktree is on `sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases` with `origin/dev` and `origin/ftr/ast-736-task-keys-vs-dispatch-task-keys` merged (already satisfied at plan time).

⚠️ **Decision:** **test-child** green on the full component manifest requires **AST-748** runtime changes on `origin/ftr/ast-736-task-keys-vs-dispatch-task-keys` — removing the config alias breaks `consult.run_consult_task` paths that still pass `consult_*` until Hedy lands. Ada completes **code()** for config + admin + rules only; do not patch `src/core/consult.py` or `src/core/dispatcher.py` in this ticket.

---

## Stage 1: Config — schedulable keys, retired keys, collapse alias map

**Done when:** `grep consult_do src/utils/config.py` returns no schedulable/alias references (JOB_STATES comments may still mention consult outcomes); `dispatch_task_admin_defaults("grade_do")` returns `entity_type=job`, `trigger_state=PASSED_JD`, `batch_call_mode=1`; `dispatch_task_admin_defaults("consult_do")` raises with a retired-key message; `resolve_dispatch_task_config_key("grade_do")` returns `"grade_do"`.

1. In `src/utils/config.py`, add module-level frozenset immediately above `DISPATCH_SCHEDULABLE_TASK_KEYS`:

   ```python
   DISPATCH_RETIRED_TASK_KEYS = frozenset({
       "consult_do", "consult_get", "consult_like",
   })
   ```

2. Add public helper (same file, near `dispatch_task_admin_defaults`):

   ```python
   _RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS = {
       "consult_do": "grade_do",
       "consult_get": "grade_get",
       "consult_like": "grade_like",
   }

   def dispatch_task_key_retired_message(task_key: str) -> str | None:
       """Return operator-facing error text when task_key is retired, else None."""
   ```

   When `task_key.strip()` is in `DISPATCH_RETIRED_TASK_KEYS`, return exactly:
   `f"task_key {tk!r} is retired; use {_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS[tk]!r}"`.

3. In `DISPATCH_SCHEDULABLE_TASK_KEYS`, remove `"consult_do"`, `"consult_get"`, `"consult_like"`. Add `"grade_do"`, `"grade_get"`, `"grade_like"` (keep `"analysis_upshot"` and all other existing keys unchanged).

4. In `_DISPATCH_BATCH_CALL_MODE_ONE`, replace `"consult_do"`, `"consult_get"`, `"consult_like"` with `"grade_do"`, `"grade_get"`, `"grade_like"`.

5. Delete dict `_CONSULT_TASK_TO_AGENT_TASK` entirely.

6. Replace `resolve_dispatch_task_config_key` body with identity only:

   ```python
   def resolve_dispatch_task_config_key(task_key: str) -> str:
       """Return task_key unchanged — dispatch and TASK_CONFIG share one string (AST-736)."""
       return (task_key or "").strip()
   ```

   Do **not** map retired keys to replacements in this function.

7. In `_dispatch_trigger_state_for_task_key`, replace the three branches:

   | Remove | Add |
   |--------|-----|
   | `if task_key == "consult_do": return "PASSED_JD"` | `if task_key == "grade_do": return "PASSED_JD"` |
   | `if task_key == "consult_get": return "PASSED_DO"` | `if task_key == "grade_get": return "PASSED_DO"` |
   | `if task_key == "consult_like": return "PASSED_GET"` | `if task_key == "grade_like": return "PASSED_GET"` |

8. In `_dispatch_entity_type_for_task_key`, replace the hardcoded tuple entry list `"consult_do", "consult_get", "consult_like"` with `"grade_do", "grade_get", "grade_like"`.

9. In `dispatch_task_admin_defaults`, as the **first** statement after normalizing `tk`:

   ```python
   retired = dispatch_task_key_retired_message(tk)
   if retired:
       raise KeyError(retired)
   ```

   Keep existing `DISPATCH_SCHEDULABLE_TASK_KEYS` membership check unchanged after the retired guard.

10. Simplify `dispatch_task_key_is_scored` to read `TASK_CONFIG` directly (no alias resolution required):

    ```python
    def dispatch_task_key_is_scored(task_key: str) -> bool:
        tk = (task_key or "").strip()
        return bool((TASK_CONFIG.get(tk) or {}).get("scored"))
    ```

11. Grep `src/utils/config.py` for remaining `consult_do`, `consult_get`, `consult_like` — only JOB_STATES / comment references to consult **outcomes** (e.g. `FAILED_TECHNICAL_GET`) may remain; no schedulable, alias, or trigger-rule references.

⚠️ **Decision:** Keep `resolve_dispatch_task_config_key` as a named function (identity) rather than deleting call sites in `api_admin.py` / `bootstrap.py` — AST-748 and AST-749 still import it; identity preserves the catalog-resolution hook without aliasing.

---

## Stage 2: Admin API — reject retired keys; confirm task_keys catalog

**Done when:** `POST /api/admin/dispatch_tasks` with `task_key: "consult_do"` returns HTTP 400 with body containing `retired` and `grade_do`; `GET /api/admin/dispatch_tasks/task_keys` JSON includes `grade_do` with `entity_type=job`, `trigger_state=PASSED_JD`, `is_scored=true`, and DB grouping fields from `_catalog_task_grouping_meta("grade_do")`; `consult_do` is absent unless an legacy DB row still exists (list loop only — no schedulable merge).

1. In `src/ui/api/api_admin.py`, add import: `dispatch_task_key_retired_message` from `src.utils.config`.

2. In `create_dtask()`, immediately after the required-field check and **before** `save_dispatch_task`:

   ```python
   retired = dispatch_task_key_retired_message(data.get("task_key", ""))
   if retired:
       return jsonify({"error": retired}), 400
   ```

3. In `_dispatch_task_key_form_meta`, no structural change required — with identity `resolve_dispatch_task_config_key`, schedulable `grade_*` keys merge `dispatch_task_admin_defaults` and `_catalog_task_grouping_meta(catalog_key)` where `catalog_key == task_key`.

4. Update the adhoc live-content comment near line 973 from `consult_do/get/like` to `grade_do/get/like`.

5. Grep `src/ui/api/api_admin.py` for `consult_do`, `consult_get`, `consult_like` — zero remaining references except none expected.

⚠️ **Decision:** Do **not** add retired-key validation to `PUT /api/admin/dispatch_tasks/<id>` — updates cannot change `task_key`; migration of existing rows is AST-748. Create path is the AC #5 gate.

---

## Stage 3: Product rules — ASTRAL_CODE_RULES dispatch vocabulary

**Done when:** `grep consult_do docs/ASTRAL_CODE_RULES.md` returns zero matches; dispatch pipeline table lists `grade_do`, `grade_get`, `grade_like`.

1. In `docs/ASTRAL_CODE_RULES.md` §3.3 dispatch pipeline table (~lines 373–375), rename rows:

   | Task | PW | AI | DB |
   |------|----|----|-----|
   | grade_do | | X | X |
   | grade_get | | X | X |
   | grade_like | / | X | X |

2. In §2.6.2 Jobs example (~line 195), fix the incorrect example: a job in `PASSED_JD` is claimed by the **`grade_do`** dispatch task; `render_verdict` grades it and transitions to `PASSED_DO`, `FAILED_DO`, or `FAILED_TECHNICAL_DO`.

3. In §2.7 step 1 (~line 209), replace alias wording with: resolve orchestration via **`TASK_CONFIG[task_type]`** — dispatch `task_key` and catalog key are the same string for graded consult steps (`grade_do`, `grade_get`, `grade_like`).

4. Grep `docs/ASTRAL_CODE_RULES.md` for `consult_do`, `consult_get`, `consult_like` — zero matches when Stage 3 completes.

---

## Execution contract

Binding per **plan-child**: stages **1 → 2 → 3** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases`**. Do not edit `tests/` or `docs/test-bible/**`. Do not edit `src/core/consult.py`, `src/core/dispatcher.py`, or `src/data/database.py`. On ambiguity — **`🛑 Stage N blocked`** on **AST-736** parent; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — primarily `src/utils/config.py` schedulable vocabulary and alias removal, with a narrow admin validation pass in `api_admin.py` and rules-doc table updates.

**Conf:** `high` — AST-549 established the `dispatch_task_admin_defaults` pattern; this ticket renames three frozenset members and removes a three-entry alias dict using the same explicit trigger branches already present for `consult_*`.

**Risk:** `Medium` — config-only cutover breaks runtime consult routing until AST-748 merges; incorrect schedulable/trigger pairing would mis-label admin defaults for the three graded consult hops without affecting unrelated roster/gazer keys.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Retiring alias map removes duplicate vocabulary; identity `resolve_dispatch_task_config_key` avoids scattered string replacements in this ticket's scope. |
| §2.1 config | Schedulable keys remain explicit frozenset; retired keys fail loudly; no env fallbacks. |
| §2.4 batch | `batch_call_mode` frozenset updated in same edit as schedulable keys — no drift. |
| §2.6 state machine | Trigger states unchanged (`PASSED_JD` / `PASSED_DO` / `PASSED_GET`); only task_key strings change. |
| §3.3 imports | Utils-only changes in Stage 1; ui imports one new config helper in Stage 2 — layer rules preserved. |
| §3.5 naming | `grade_*` matches existing `TASK_CONFIG` index and Manage Tasks keys. |

No conflicts requiring `!!-NONE`.
