# AST-1562 — Retention sweep + delete meteorite_email

**Linear:** [AST-1562](https://linear.app/astralcareermatch/issue/AST-1562/retention-sweep-delete-meteorite-email-meteorite-ingress-staging-table-inboxmeteorite-consolidation)  
**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) — Meteorite ingress: staging table + inbox/meteorite consolidation  
**Publish ref:** `sub/AST-1555/AST-1562-retention-sweep-delete-meteorite-email`

After AST-1559 (#3), AST-1560 (#4), and AST-1561 (#5): add a **scheduled dispatch** retention runner that purges old `LANDED` staging rows and **info-logs** stale `ERROR` / `BOT_BLOCKED` / `ABANDONED` rows (no deletes in transition handlers); delete `src/core/meteorite_email.py` and retire leftover unbound/selected-ids config; final grep confirms fetch/bind/source-ref synthesis paths are gone. Does not reopen qualify, legacy sync create, or Manage Email product hygiene.

## Scope gate

Linear child **## Scope** / **## Citations** headings are empty (dispatch template gap). Authoritative partition is parent **Proposed child tickets → #6**:

- `src/core/meteorite.py` — `run_meteorite_retention` scheduled runner (purge + stale list)
- `src/utils/config.py` + `src/core/dispatcher.py` + `data/admin/dispatch_task.json` — `METEORITE_RETENTION_CONFIG`, seed row, dispatcher branch
- `src/core/meteorite_email.py` — **deleted**
- Leftover config/dispatcher cleanup (unbound retention literals, `debug_func_selected`, selected-id outcome strings)
- Optional `src/core/consult.py` cycle trim if a concrete break remains from AST-1560 late imports

**Citations (parent #6):** `astral.standards.in-scope-only`, `astral.dispatch.seed-auto-false`, `pattern.config.config-block`

**Out of scope (siblings):** AST-1557 table/claim helpers (consume `list_meteorites_for_retention`, `delete_meteorites_by_ids`, `METEORITE_STATES_RETENTION` only — **no new SQL** unless symbols missing after merge); AST-1558 inbox/Manage Email; AST-1559 `check_inbox`; AST-1560 transitions; AST-1561 notify/`apply_paste`. Do **not** edit `tests/`, `docs/test-bible/**`, `src/ui/**`, or `src/core/inbox.py` (Betty owns test updates at Code Complete; inbox fetch/bind deletion is AST-1558).

**AC partition (this ticket):**

- Parent AC6 — `inbox.py` has no `run_fetch_email` / `fetch_email` / From-then-To bind path; `meteorite_email.py` is gone; meteorite does not import `external/gmail`; unbound age→Trash hygiene is gone.
- Parent AC7 — Retention scheduled path can purge old `LANDED` and list stale `ERROR` / `BOT_BLOCKED` / `ABANDONED` without those deletes living inside transition handlers.

**Depends on:** **AST-1557** (`list_meteorites_for_retention`, `delete_meteorites_by_ids`, `METEORITE_STATES_RETENTION`), **AST-1559** (`check_inbox` + mailbox `debug_func`), **AST-1560** (`METEORITE_INGRESS_DISPATCH_CONFIG`), **AST-1561** (`METEORITE_BOT_BLOCKED_NOTIFY_CONFIG` + notify dispatcher branch) merged onto the epic line before **build-child**. After `sync-child.sh`, if any of those symbols/branches are missing on HEAD, **stop** and comment on AST-1562 — do not re-implement sibling slices. Chuckles **merge-child** may land siblings onto `ftr`; builder may also merge `origin/sub/AST-1555/AST-1557-*` … `AST-1561-*` tips locally if `ftr` is absent on origin.

All Files Changed / Stages stay inside the Scope file set above.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_RETENTION_CONFIG` (day cutoffs, task key, batch size, stale log line, debug_func); retire `unbound_retention_days`, `debug_func_selected`, selected-id outcome keys from `METEORITE_EMAIL_MAILBOX_CONFIG`; header inventory + asserts | utils |
| `data/admin/dispatch_task.json` | Idempotent global dispatch row for retention runner (`auto_mode` false) | catalog |
| `src/core/dispatcher.py` | `_is_meteorite_retention_task_key` + custom branch → `run_meteorite_retention` (after notify, before mailbox `check_inbox`) | core |
| `src/core/meteorite.py` | `run_meteorite_retention` — purge old `LANDED`, info-log stale terminal/holding states | core |
| `src/core/meteorite_email.py` | **Delete module** | core |
| `src/core/consult.py` | Optional: trim import cycle only if a safe one-line break exists (else no edit) | core |

**Verified no touch:** `src/data/database.py` (retention SQL helpers ship AST-1557); `src/core/inbox.py` (AST-1558); `tests/**`; `docs/test-bible/**`. `meteorite_email` remains the dispatch **task_key** / agent_task fold name — only the **module file** and obsolete runner literals retire.

## Stage 1: Config + dispatch seed + dispatcher registration

**Done when:** `METEORITE_RETENTION_CONFIG` exposes task key, day cutoffs, batch size, stale list format string, and `debug_func`; one `SEED_CONFIG` entry + matching `data/admin/dispatch_task.json` row exist; `dispatcher._dispatch_one` recognizes the retention key and delegates to `run_meteorite_retention` with minted `entity_batch_id` (stub runner returning `_ZERO_SUMMARY` OK until Stage 2); `python3 -m py_compile src/utils/config.py src/core/dispatcher.py` succeeds.

1. In `src/utils/config.py` module header inventory, add bullet for `METEORITE_RETENTION_CONFIG` — scheduled LANDED purge + stale-row info list (AST-1562); day cutoffs live here (AST-1557 kept state literals only in `METEORITE_STATES_RETENTION`).

2. After `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG` block (AST-1561 — must exist on branch), insert:

```python
# AST-1562: scheduled retention — purge old LANDED; info-list stale ERROR/BOT_BLOCKED/ABANDONED.
METEORITE_RETENTION_CONFIG = {
    "task_key": "meteorite_retention",
    "landed_purge_days": 90,
    "stale_list_days": 14,
    "batch_size": 200,
    "debug_func": "meteorite.run_meteorite_retention",
    "stale_list_line": (
        "meteorite retention stale id={row_id} state={state} candidate={candidate_id} "
        "changed={state_changed_at}"
    ),
}
```

3. Asserts immediately after the block:

- `task_key`, `debug_func`, `stale_list_line` are non-empty str
- `landed_purge_days` and `stale_list_days` are int ≥ 1; `batch_size` is int ≥ 1
- `stale_list_line` contains `{row_id}`, `{state}`, `{candidate_id}`, `{state_changed_at}`
- `set(METEORITE_STATES_RETENTION["purge_states"]) == {"LANDED"}`
- `set(METEORITE_STATES_RETENTION["stale_list_states"]) == {"ERROR", "BOT_BLOCKED", "ABANDONED"}`

4. Add `SEED_CONFIG["dispatch_task-meteorite-retention"]` following peer global dispatch rows (NULL `candidate_id`, `task_key` from config, `entity_type` NULL, `trigger_state` NULL, `batch_size` from config, `auto_mode` 0, `freq_hrs` 24, conservative `min_count` 0 — daily hygiene, not a claim queue).

5. Add matching row to `data/admin/dispatch_task.json` (same literals as SEED_CONFIG).

6. In `src/core/dispatcher.py`, import `METEORITE_RETENTION_CONFIG`; add `_is_meteorite_retention_task_key(task_key) -> bool` comparing to config `task_key`.

7. In `_dispatch_one`, add branch **after** AST-1561 `meteorite_bot_blocked_notify` branch and **before** mailbox `check_inbox` branch:

   - Mint `entity_batch_id = f"{task_key}-{uuid.uuid4()}"`; `save_dispatch_ledger(...)`; `log_batch_id.set(entity_batch_id)`; set `task["entity_batch_id"] = entity_batch_id`.
   - Late-import `from src.core.meteorite import run_meteorite_retention`.
   - `summary = await run_meteorite_retention(task, debug=debug)` — mirror notify/ingress `await` branches (no nested `asyncio.run`).
   - Accumulate summary counts; ledger + `last_run_at` update in `finally` peer to notify branch.

8. Add minimal stub in `src/core/meteorite.py` if needed so Stage 1 compiles:

```python
async def run_meteorite_retention(task: dict, *, debug: bool = False) -> dict:
    """Dispatch runner: purge old LANDED + info-list stale rows (AST-1562)."""
    return dict(_ZERO_SUMMARY)  # replaced Stage 2
```

⚠️ **Decision:** Retention uses a **dispatch_task + core runner** (peer to AST-1561 notify), not AST-1122 `scheduled_query` raw SQL — parent technical scope names a retention **task_key**; DB helpers from AST-1557 are Python-callable from the runner. Purges/listing never run inside `run_stage_meteorite` / scrape / land / notify transition bodies (AC7).

⚠️ **Decision:** `landed_purge_days=90`, `stale_list_days=14` are config SSOT defaults — adjust only via config block, not inline in the runner.

## Stage 2: `meteorite.py` — retention runner

**Done when:** `run_meteorite_retention` deletes `LANDED` rows older than `landed_purge_days` (batched via `batch_size`); info-logs each stale `ERROR` / `BOT_BLOCKED` / `ABANDONED` row older than `stale_list_days` using `stale_list_line` at **info** level (always on, not Style D); **does not delete** stale-list states; returns summary dict with processed/passed/failed counts; no imports of `src.external.gmail`; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. Replace Stage 1 stub with full `async def run_meteorite_retention(task: dict, *, debug: bool = False) -> dict`:

   - `log = get_logger(__name__)`; `log.set_debug_flag(debug)` (Style D only when `debug=True`; stale lines are always info).
   - Load `cfg = METEORITE_RETENTION_CONFIG`; `batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])`.
   - `now = datetime.now(timezone.utc)`; compute ISO cutoffs:
     - `landed_cutoff = (now - timedelta(days=int(cfg["landed_purge_days"]))).isoformat()`
     - `stale_cutoff = (now - timedelta(days=int(cfg["stale_list_days"]))).isoformat()`
   - Initialize `summary = dict(_ZERO_SUMMARY)`.

2. **Purge path** (delete):

   - `purge_states = list(METEORITE_STATES_RETENTION["purge_states"])`
   - `rows = list_meteorites_for_retention(states=purge_states, older_than=landed_cutoff, limit=batch_size)`
   - If rows: `ids = [int(r["id"]) for r in rows]`; `n = delete_meteorites_by_ids(ids)`; `summary["total_processed"] += n`; `summary["total_passed"] += n`
   - Optional single info line: `log.info("meteorite retention purged landed count=%s", n)` when `n > 0` (not a second format SSOT — count-only).

3. **Stale list path** (log only — **no** `delete_meteorites_by_ids`):

   - `stale_states = list(METEORITE_STATES_RETENTION["stale_list_states"])`
   - `stale_rows = list_meteorites_for_retention(states=stale_states, older_than=stale_cutoff, limit=batch_size)`
   - For each row: `summary["total_processed"] += 1`; format `cfg["stale_list_line"].format(row_id=..., state=..., candidate_id=..., state_changed_at=...)` using `(row.get("state_changed_at") or row.get("updated_at") or "")`; `log.info(line)`; `summary["total_passed"] += 1`

4. Add imports at top of `src/core/meteorite.py` if missing:

   - `from datetime import datetime, timedelta, timezone`
   - `from src.data.database import delete_meteorites_by_ids, list_meteorites_for_retention`
   - `from src.utils.config import METEORITE_RETENTION_CONFIG, METEORITE_STATES_RETENTION`

5. Do **not** call `claim_meteorite_batch` / `clear_meteorite_batch` — retention is not an entity-state transition claim.

6. Do **not** invoke purge/delete from `run_stage_meteorite`, `run_scrape_meteorite`, `run_land_meteorite`, or `run_notify_meteorite_bot_blocked`.

## Stage 3: Delete `meteorite_email.py` + mailbox config cleanup

**Done when:** `src/core/meteorite_email.py` is removed; no product `.py` file imports `src.core.meteorite_email`; `METEORITE_EMAIL_MAILBOX_CONFIG` no longer carries unbound/selected-id runner literals; related asserts updated; `python3 -m py_compile src/utils/config.py src/core/dispatcher.py` succeeds.

1. `git rm src/core/meteorite_email.py`.

2. In `src/utils/config.py`, edit `METEORITE_EMAIL_MAILBOX_CONFIG`:

   - Remove keys: `unbound_retention_days`, `debug_func_selected`, `selected_outcome_skipped_unbound`, `selected_outcome_skipped_not_in_inbox`, `selected_outcome_skipped_unmatched`.
   - Update block comment: remove unbound Trash / selected-ids Land Meteorite references; state runner is `meteorite.check_inbox` only.
   - Update module header inventory bullet for `METEORITE_EMAIL_MAILBOX_CONFIG` — drop “unbound retention” and “selected-ids Land Meteorite”.

3. Remove asserts referencing deleted keys (`unbound_retention_days`, `debug_func_selected`, selected outcome strings). Keep asserts for `task_key == "meteorite_email"`, `debug_func == "meteorite.check_inbox"`, `auto_mode is False`.

4. Grep product tree (`src/**/*.py`, exclude `tests/`): if any `from src.core.meteorite_email` or `import meteorite_email` remains, repoint or delete the import:

   - Expected: **none** on post–AST-1559 dispatcher (mailbox uses `check_inbox`).
   - `api_inbox` Land path must not reference `run_meteorite_email_selected_ids` (AST-1558 uses `stage_meteorite` — verify only; do not edit `api_inbox` unless a stray import breaks compile after delete).

5. Do **not** rename `ensure_meteorite_email_dispatch_task`, `task_key`, or agent_task fold helpers — `meteorite_email` stays the scheduled mailbox **task name**.

## Stage 4: Final verification grep + optional consult trim

**Done when:** Manual grep checklist passes on epic worktree; optional `consult.py` edit only if step 6 applies; `python3 -m py_compile` on every touched `.py` file succeeds.

1. **AC6 / hygiene grep** (product `src/` only — record hits in Linear comment if unexpected):

   ```bash
   rg -n "run_fetch_email|FETCH_EMAIL_CONFIG|INBOX_BIND_CONFIG|_bind_inbox_message|fetch_email" src/core/inbox.py src/core/dispatcher.py src/utils/config.py
   rg -n "meteorite_email\\.py|from src\\.core import meteorite_email|from src\\.core\\.meteorite_email" src/
   rg -n "from src\\.external import gmail|from src\\.external\\.gmail" src/core/meteorite.py
   rg -n "unbound_retention|Trash|trash_message" src/core/meteorite.py src/core/dispatcher.py
   ```

   Expected: inbox/dispatcher/config have **no** live fetch/bind symbols (AST-1558); **no** `meteorite_email` module imports; `meteorite.py` has **no** gmail import; **no** unbound Trash hygiene in meteorite/dispatcher poller paths.

2. **AC7 / source-ref grep:**

   ```bash
   rg -n "_map_stage_jobs_to_scraps|email-<|source_ref.*mid" src/core/meteorite.py
   ```

   Expected: no `_map_stage_jobs_to_scraps`; fan-out uses real `source_id` / message id per AST-1559 mapper (no synthetic `-2` suffix chain).

3. **Retention isolation grep:**

   ```bash
   rg -n "delete_meteorites_by_ids|list_meteorites_for_retention" src/core/meteorite.py
   ```

   Expected: calls appear **only** inside `run_meteorite_retention`, not inside transition runners.

4. Confirm `data/admin/dispatch_task.json` includes `meteorite_retention` row and `meteorite_bot_blocked_notify` / ingress keys unchanged from AST-1560/1561.

5. Update `src/core/meteorite.py` module docstring: document `run_meteorite_retention`; note `meteorite_email.py` retired AST-1562.

6. **Optional `consult.py` trim:** Read top-level imports. If `from src.core.meteorite import is_meteorite_company` still forces a cycle with meteorite’s late `consult` imports and a **local** late import inside the one function that uses `is_meteorite_company` breaks the cycle without new public API, apply that single move. If no safe one-function late import exists, **leave consult.py unchanged** and note “no cycle break” in the stage commit message — do not refactor qualify/land consult paths.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1562
**Overall:** APPROVED
**Publish ref:** `sub/AST-1555/AST-1562-retention-sweep-delete-meteorite-email` @ `4fe81774e094081d1154d685a18ba9368cfb9a94`

### Traceability
AC6 → Stages 3–4 (delete `meteorite_email.py`, retire unbound/selected-id mailbox literals, grep confirms no fetch/bind/source-ref/gmail/hygiene); AC7 → Stages 1–2 (`run_meteorite_retention` scheduled dispatch purges old `LANDED`, info-lists stale `ERROR`/`BOT_BLOCKED`/`ABANDONED`, no delete/list inside transition runners).

### Findings

#### acceptable
- **Location:** AC6 partition vs Scope
- **Finding:** Parent AC6 includes `inbox.py` fetch/bind removal (AST-1558); this plan verifies via Stage 4 grep only — does not edit `inbox.py` or dispatcher `fetch_email` branch.
- **Recommendation:** Chuckles merge AST-1558/1559 before build-child; Stage 4 grep is the acceptance gate for those slices.

#### acceptable
- **Location:** Stage 3 — delete `meteorite_email.py`
- **Finding:** Plan assumes AST-1559 already repointed mailbox dispatcher to `check_inbox`; Depends names 1559 but does not spell “stop if dispatcher still imports `meteorite_email`.”
- **Recommendation:** Builder stops on missing `check_inbox` branch before `git rm`; add explicit gate in build if helpful, not blocking plan approval.

#### acceptable
- **Location:** Linear ticket — empty `## Citations` / `## Scope`
- **Finding:** Dispatch template gap; plan Scope gate mirrors parent proposed child #6.
- **Recommendation:** Chuckles backfill Linear fields when appending.

**In-session statute pass:** Retention config block + seed `auto_mode` 0 — **pattern.config.config-block** / **astral.dispatch.seed-auto-false** conform. Purge/list isolated to `run_meteorite_retention` — **astral.standards.in-scope-only** conform. `entity_batch_id` + `await` dispatcher branch — **astral.batch.batch-id-first** conforms (ledger id; no row claim). Day cutoffs in config, state partitions from AST-1557 — **astral.config.config-source-of-truth** conforms. Universal orch.* — N/A/conforms.

## Review

- **Publish ref:** `origin/sub/AST-1555/AST-1562-retention-sweep-delete-meteorite-email`
- **Tip:** `0eff452b8a2ff1f7760135964f1f5f395dc420ae`
- **Stages:** 1 retention config/seed/dispatcher · 2 `run_meteorite_retention` · 3 delete `meteorite_email.py` · 4 grep verify + consult late import
- **Build notes:** Merged sibling tips AST-1557–1561 locally (no origin/ftr). Minimal `api_inbox` literal for land skip outcome after mailbox config key removal.

## Radia review

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1562  
**Publish ref:** `sub/AST-1555/AST-1562-retention-sweep-delete-meteorite-email` @ `f2f9de2cefe72ecfe161f1347172caa3cc45d401`  
**Overall:** DISCUSS  
**Internal grade:** DISCUSS (product faithful; test-tree collection gap)

**Baseline:** `git diff origin/dev...origin/sub/AST-1555/AST-1562-retention-sweep-delete-meteorite-email`  
**Status gate:** Tests Passed (spawn prompt — trusted)

**AST-1562-only product footprint** (commits `7af96e96`…`0eff452b`): `src/utils/config.py`, `src/core/dispatcher.py`, `src/core/meteorite.py`, `src/core/meteorite_email.py` (deleted), `src/core/consult.py` (optional cycle trim), `data/admin/dispatch_task.json` (+1 row), `src/ui/api/api_inbox.py` (unused import removal only).

### Findings

#### discuss — `test_meteorite_email.py` breaks pytest collection after module delete
- **Location:** `tests/component/core/test_meteorite_email.py` (module-level `from src.core import meteorite_email as ge`)
- **Finding:** `pytestmark` skipif runs at test time, but module import fails at collection when `find_spec("src.core.meteorite_email")` is `None` (`ImportError` verified on tip). Bible claims the file "skips when module absent"; that is not true for collection.
- **Impact:** Manifest-scoped green (8 passed on `TestAst1562*`) masks failure on `pytest tests/component/core/test_meteorite_email.py` or any broad `tests/component/core/` collect.
- **Recommendation:** **Betty** (not resolve-child): delete `test_meteorite_email.py` or guard with `pytest.importorskip("src.core.meteorite_email")` before the import. Re-run component collect before prep-uat.

#### discuss — stacked sibling product on publish ref vs `origin/dev`
- **Location:** Full three-dot diff (~47 files, AST-1557–1561 stack)
- **Finding:** Expected epic merge; AST-1562-only engineer delta is 7 files / ~200 LOC net.
- **Recommendation:** **Chuckles/datt:** ftr merge order per blockedBy; not resolve-child scope.

#### advisory — retention `debug=True` has no per-row Style D index on stale loop
- **Location:** `run_meteorite_retention` stale_rows loop
- **Finding:** Plan explicitly makes stale lines always-on info (not Style D). When `debug=True`, multi-row stale loop has no `debug_index` per §5f batch guidance.
- **Recommendation:** Accept per plan; optional follow-up if operators need Style D on retention sweeps.

#### advisory — purge and stale paths each honor `batch_size` independently
- **Location:** `run_meteorite_retention`
- **Finding:** One run may process up to `2 × batch_size` rows (200 landed + 200 stale). Plan does not cap combined total.
- **Recommendation:** Accept at current scale; tune config if daily sweep needs a hard ceiling.

#### advisory — issue doc Review stub tip stale
- **Location:** `docs/features/meteorite/ast-1562-*.md` Review section cites `0eff452b`; tip is `f2f9de2c` (merge-tests)
- **Recommendation:** **Chuckles:** update stub when appending verdict.

### What's solid
- `run_meteorite_retention`: correct cutoffs, batched purge, stale info-only path, summary counts.
- Dispatcher retention branch: `entity_batch_id`, ledger, `await` runner, ordered after notify / before `check_inbox`.
- `meteorite_email.py` deleted; no `from src.core.meteorite_email` in `src/`.
- Mailbox config cleaned; Stage 4 greps clean; Betty manifest tests green.

**Notes:** No fix-now product violations. Recommended downstream: Betty fixes `test_meteorite_email.py` collection; no mandatory resolve-child product changes for AC6/AC7.
