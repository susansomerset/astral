# AST-1513 — Reject duplicate Do rubric codes (meteorite_grade_do is failing)

<!-- linear-archive: AST-1513 archived 2026-09-09 -->

## Linear archive (AST-1513)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1513/reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1510 — meteorite_grade_do is failing  
**Blocked by / blocks / related:** parent: AST-1510

### Description

## What this implements

Fix the somerset Do rubric **duplicate **`TP` **code collision** so `meteorite_grade_do` / `grade_do` decode a complete grade set (Hands-On Technical Partnership With Engineers present once; Speaking Truth to Power With Diplomacy not duplicated). Parent bug AST-1510; ancestor context AST-723 (rubric_vector authority).

## Scope

## Component scope

* `src/core/candidate.py` — modified if adding duplicate-code validation on rubric save/sync — reject or warn when two current `rubric_vector` rows for the same owner share a code.
* `src/core/consult.py` — modified only if hardening `_vector_labels_map` to detect/log duplicate codes instead of silent last-wins (diagnostic).
* `src/core/agent.py` — modified only if decode should fail fast on duplicate codes in one line (optional; data fix may be sufficient).
* **Somerset rubric data** (via Artifacts UI / `rubric_vector` rows) — modified — reassign duplicate `TP` so HT and TP are distinct codes (primary fix if collision is data-only).

## Technical scope

* `src/core/candidate.py`: optional new validation in rubric sync/save path — when building criteria from `rubric_vector` rows, raise or surface duplicate `code` values for one `(candidate_id, task_key)` owner before persist. — **done** (`_assert_unique_rubric_codes` in `normalize_rubric_artifacts_on_save`)
* `src/core/consult.py`: optional `_vector_labels_map` change — detect duplicate codes in input list and log/raise Style D detail under `debug=True` instead of silent last-wins overwrite. — **done** (warning + first-wins map; `debug_detail` when `debug=True`)
* `src/core/agent.py`: optional decode guard — if the same two-char code appears twice in one encoded line, treat as incomplete/retry with explicit duplicate-code detail (AST-1155 retry path). — **done** (`_decode_payload` duplicate segment check)
* **Rubric data**: reassign the colliding vector's code (likely HT vs TP) so `_vector_labels_map` and the model prompt agree on eleven unique codes. — **staging ops** (Artifacts save on somerset; not product code)

## Acceptance criteria

1. Somerset Do rubric has unique two-letter codes for every vector (HT and TP distinct). — **pending staging data fix**
2. A somerset `meteorite_grade_do` batch decodes and applies scored pass/fail without incomplete-grade error for missing HT. — **pending staging data fix + re-run**
3. Duplicate code assignment is rejected or surfaced at save/sync (product guard), not silent last-wins only. — **done**

## Boundaries

Does not reopen AST-1150 retry-routing policy. Does not change `_render_score` math for complete grade sets. vector_reviews wire-format parse failures are secondary unless they block scoring.

### Comments

#### radia — 2026-08-27T00:04:34.871Z
[code-rubric] PROCEED (Commit: 3d8eae67) duplicate rubric code guards clean

#### betty — 2026-08-26T23:59:44.545Z
[bug-repro]
origin/sub/AST-1510/AST-1513-reject-duplicate-do-rubric-codes @ ca88ef5e · repro lands red, awaits fix

#### joan — 2026-08-26T23:56:43.692Z
[board-joan] CANON: OK

Scoped statutes and patterns: no canon update required. Save-time duplicate-code guard and `_vector_labels_map` collision diagnostics extend existing grade-vector-validation and data-raises-caller idioms without conflicting with embedded-wins-on-code (preserved in What must still hold).

#### betty — 2026-08-26T23:46:50.859Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/candidate.md — no duplicate rubric-code save guard — repro-first test for do_rubric duplicate TP → ValueError/400 before sync; docs/test-bible/core/consult.md — _vector_labels_map duplicate-code collision (HT/TP last-wins → incomplete grade set) untested; optional docs/test-bible/core/agent.md — _decode_payload duplicate segment guard if Step 4 lands

#### hedy — 2026-08-26T23:45:36.894Z
`origin/sub/AST-1510/AST-1513-reject-duplicate-do-rubric-codes` @ `946f8031` · duplicate TP guard + HT fix

---

_Implementation detail may live in git history on `origin/dev`._

## Bug: AST-2008 — Rubric code uptick, consult timeout retry, ledger call timing, gen-stats off

Parent: AST-2007 (orphaned mini-parent, `ftr/AST-2007-meteorite-grade-do-timeout`). Publish: `sub/AST-2007/AST-2008-rubric-codes-timeout-ledger`. Reverses AST-1513's **Technical scope** first bullet (the `_assert_unique_rubric_codes` raise); AST-1513's consult and agent guards are unchanged.

### As-is

1. **Rubric codes.** `normalize_rubric_artifacts_on_save` calls `_assert_unique_rubric_codes`, which raises `ValueError` on a duplicate code. The UI save (`src/ui/api/api_candidate.py`, around line 407) returns HTTP 400 and the craft persist (`src/core/candidate.py`, around line 3619) fails. The check runs before `apply_rubric_vectors_save` merges the embedded QC/GC/RC vectors. Separately, `database.sync_rubric_vectors_from_criteria` keys current rows by code in a dict, so when two current rows share a code only the last one is tracked. The older row is never matched and never retired. Somerset's Do rubric has two current `TP` rows. Every dispatch logs `duplicate rubric codes: TP→[…]`.
2. **Timeout routing.** In `consult.render_verdict`, a `do_task` failure that isn't a balance refusal or `empty_tokens` falls through to `_fail`. `_fail` transitions straight to `error_state` (`METEORITE_FAILED_TECHNICAL_DO`), so a `provider_call_timeout` (AST-1189, 600s) gets no retry. The live failure took this path: its log line `db358880-… -> METEORITE_FAILED_TECHNICAL_DO [Provider call exceeded per-call time budget (600s)]` is a WARNING, which is `_fail`'s `_warn_job`. `_log_fail_dest` would have logged ERROR for a terminal destination. The batch envelope path (`_run_batch_consult` → `_transition_batch_consult_failures`) and the per-entity loop (around `consult.py` line 1278) already route through `_consult_batch_fail_dest`.
3. **Ledger.** `dispatch_ledger` has no call duration or failure class. `agent.do_task` writes only `host`, and only on successful calls (AST-1960).
4. **Generation stats.** `timesheets.record_timesheet_entry` spawns a `reconcile_timesheet_platform` daemon thread for every non-`direct` routed call. That thread logs `no platform cost after 5 tries` when OpenRouter 404s. There is no switch to turn it off.

### To-be

1. One pure helper runs in front of every rubric save, UI and craft alike. It re-letters the last character of any later duplicate code (X, Y, Z, A, B, …, W) until the code is unique. Saves never raise on duplicates. Sync retires extra current rows that share a code, so stored duplicates clear on the next save.
2. A `provider_call_timeout` in `render_verdict` goes to the job's retry holding (`METEORITE_PASSED_JD` → `METEORITE_PASSED_JD_RETRY`). A timeout while already on `_RETRY` goes to `error_state`. That is one hop, per AST-642.
3. Every `do_task` call writes `llm_call_seconds` and `llm_failure_class` to the active ledger row, on success and on failure.
4. `TIMESHEET_RECONCILE_ENABLED = False` stops the reconcile thread from spawning. Timesheet rows keep their catalog cost. The reconcile code, `get_generation_stats`, and `get_batch_host` (AST-1960) are untouched.

### Repro

The fixtures are Python literals. Persistence is SQLite through `src/data/database.py`.

1. **Uptick:** `normalize_rubric_artifacts_on_save({"do_rubric": [c("TP","Hands-On Technical Partnership With Engineers"), c("TP","Hands-On Technical Partnership With Engineers"), c("SD","Speaking Truth to Power With Diplomacy")]})`, where `c(code, label)` is a valid criterion dict with content, a grade table, and importance 5. Today it raises `ValueError: Rubric 'do_rubric': duplicate code 'TP' …`. Expected: no raise. `_uptick_duplicate_rubric_codes(list, "do_rubric")` then returns codes `["TP", "TX", "SD"]`.
2. **Reserved originals:** codes `["TP", "TP", "TX"]` → `["TP", "TY", "TX"]`. Every first occurrence keeps its code.
3. **Sync orphan:** seed two `current = 1` `rubric_vector` rows for (`somerset`, `grade_do`) both with code `TP`, inserted in order r1 then r2. Call `sync_rubric_vectors_from_criteria("somerset", "grade_do", [TP criterion matching r1, TX criterion])`. Today the current rows are `TP`, `TP`, `TX`. Expected: r2 retired, current rows `TP` (r1) and `TX`.
4. **Timeout routing:** call `render_verdict("meteorite_grade_do", aid)` for a job in `METEORITE_PASSED_JD`, with `do_task` stubbed to return `{"success": False, "error": "Provider call exceeded per-call time budget (600s)", "failure_class": "provider_call_timeout", "timesheet": {"duration": 613.9}}`. Today the job lands in `METEORITE_FAILED_TECHNICAL_DO`. Expected: `METEORITE_PASSED_JD_RETRY`. Run again from `METEORITE_PASSED_JD_RETRY` and expect `METEORITE_FAILED_TECHNICAL_DO`.
5. **Ledger:** use the same stubbed `_send_to_server` result with `log_batch_id` set. Expected: `update_dispatch_ledger(batch_id, llm_call_seconds=613.9, llm_failure_class="provider_call_timeout")`, with no `host` kwarg.
6. **Reconcile off:** call `record_timesheet_entry(agent_req_id="gen-x", provider="openrouter", model_code=<openrouter-routed SKU>, …)`. Expected: the row is inserted and no `threading.Thread` is started.

### Root cause

1. AST-1513 chose reject over repair. The check also sits before the embedded merge. The sync's dict keyed by code means a stored duplicate can never be retired by a save, which is why AST-1513's staging re-save left the duplicate in place.
2. `render_verdict` has no failure-class branch for the call budget. Everything that falls through goes to `_fail`.
3. The ledger has no columns for call outcome, and the agent write is gated on `success`.
4. The reconcile has no on/off switch.

### Proposed change

**Step 1 — `src/core/candidate.py`, rubric code uptick.**

- Add the module constant `_RUBRIC_CODE_UPTICK_LETTERS = "XYZABCDEFGHIJKLMNOPQRSTUVW"` (the full alphabet starting at X, wrapping).
- Add `_uptick_duplicate_rubric_codes(criteria: list, artifact_key: str) -> list`. It is pure and returns a new list:
  - `reserved` is the set of `code.strip().upper()` for every dict item with a non-blank code. Every first occurrence is pre-reserved, so a later original such as `TX` is never taken by a re-letter.
  - Walk the items in order and track `seen` codes. Pass non-dict and blank-code items through unchanged; sync still assigns `V{idx}`.
  - On the first occurrence of a code, add it to `seen` and keep the item.
  - On a later duplicate, try `code[:-1] + letter` for each letter in `_RUBRIC_CODE_UPTICK_LETTERS`. Take the first candidate whose upper-case form is not in `reserved`, then add it to `reserved` and `seen`. Append a shallow copy `{**item, "code": new_code}`. Never mutate the input dict, because merged lists hold references to the `EMBEDDED_*` constants. Log one `logger.warning("Rubric %r: duplicate code %s on %r -> %s", artifact_key, code, label, new_code)`.
  - If all 26 candidates are taken, keep the item unchanged and log a warning instead (see Decision C).
- In `apply_rubric_vectors_save`, right after the QC/GC/RC merge `if/elif` and immediately before `database.sync_rubric_vectors_from_criteria(...)`: `val = _uptick_duplicate_rubric_codes(val, key)`. The UI save and craft persist both call `apply_rubric_vectors_save`, so they share this one call site. Don't add calls at the two callers.
- In `normalize_rubric_artifacts_on_save`, delete the line `_assert_unique_rubric_codes(val, key)`. Delete the `_assert_unique_rubric_codes` function too, since it has no other callers. The remaining `ValueError`s (non-list artifact, non-dict criterion, grade table, importance) stay, as does the docstring's "raises" sentence.

**Step 2 — `src/data/database.py`, `sync_rubric_vectors_from_criteria`.**

- Append `ORDER BY rowid` to the current-rows `SELECT`. `rubric_vector` has a `TEXT PRIMARY KEY` and is a rowid table.
- In the loop that builds `current_by_code`, if `code` is already a key, call `_retire_rubric_vector_row_on_connection(conn, r[0], now=now)` and skip the row. Otherwise store it as today. `now` is already assigned before the `SELECT`.
- The rest of the upsert, fingerprint, and retire logic is unchanged.

**Step 3 — `src/core/consult.py`, `render_verdict` timeout branch.**

- Add `PROVIDER_CALL_BUDGET` to the existing `from src.utils.config import (...)` block.
- In the `if not result.get("success"):` block, after the `empty_tokens` branch and before `return _fail(...)`:

```python
if result.get("failure_class") == PROVIDER_CALL_BUDGET["failure_class"]:
    # AST-642 routing: primary → retry holding, *_RETRY → error_state (one hop).
    dest = _consult_batch_fail_dest(job.get("state"), error_state)
    _log_fail_dest(astral_job_id, dest, result.get("error") or "provider call timeout")
    if dest:
        _transition_job_state_for_task(agent_task, [astral_job_id], dest)
    return {"success": False, "to_state": dest, "error": result.get("error"),
            "failure_class": result.get("failure_class")}
```

- Leave `_run_batch_consult` and the per-entity loop alone. They already route a timeout through `_consult_batch_fail_dest`.

**Step 4 — `src/data/database.py`, ledger columns.**

- In `_ensure_dispatch_ledger_schema`, add `llm_call_seconds REAL` and `llm_failure_class TEXT` after `host` in the `CREATE TABLE`. Append `("llm_call_seconds", "REAL")` and `("llm_failure_class", "TEXT")` to `migrations` with an `# AST-2008: …` comment, AST-1960 style. No backfill; old rows stay NULL.
- Add both names to `_LEDGER_UPDATE_COLS`.

**Step 5 — `src/core/agent.py`, `do_task` post-call ledger write.**

- Replace the `if ledger_batch_id and result.get("success"):` host block with `if ledger_batch_id:`, building
  `cols = {"llm_call_seconds": (result.get("timesheet") or {}).get("duration"), "llm_failure_class": None if result.get("success") else (str(result.get("failure_class") or "").strip() or "provider_failed")}`.
- Add `cols["host"] = …` only when `result.get("success")`. Keep the existing host expression and the AST-1960 reason why a failed call never writes the host.
- Make one `await asyncio.to_thread(database.update_dispatch_ledger, ledger_batch_id, **cols)` call in the existing `try/except` with `logger.exception`. Generalize the exception message from "host" to "call outcome". It stays off the event loop and never fails the call.
- `provider_failed` reuses `_close_hop_ledger`'s existing token for an unclassified provider failure. Early `_send_to_server` returns carry `"timesheet": {}`, so they write `llm_call_seconds = NULL`.

**Step 6 — `src/utils/config.py` and `src/core/timesheets.py`, reconcile switch.**

- `config.py`: directly above `TIMESHEET_RECONCILE_RETRIES`, add `TIMESHEET_RECONCILE_ENABLED = False` with a comment: the AST-1963 platform-cost reconcile is off pending a new epic (AST-2007), and timesheet rows keep their catalog cost.
- `timesheets.py`: import `TIMESHEET_RECONCILE_ENABLED`. In `record_timesheet_entry`, right after `_add_timesheet_entry(**kwargs)`, add `if not TIMESHEET_RECONCILE_ENABLED: return`. `reconcile_timesheet_platform` is unchanged. Add one line to the module docstring saying the reconcile is gated by the flag.

**Explicit decisions (Susan approved, AST-2008 resume):**

- **A — Shared ledger row: last call wins.** Several `do_task` calls can share one `dispatch_ledger` row, for example the per-entity consult loop or a `run_next` hop row. Each call overwrites both `llm_call_seconds` and `llm_failure_class`, so the pair always describes the same call (success writes `llm_failure_class = NULL`). The rows are not summed, and a failure class doesn't stick across calls.
- **B — Performance Monitor columns left out.** `AdminPerformanceMonitor.tsx` is not touched. The new fields are DB-only, for analysis.
- **C — Uptick exhaustion.** If all 26 last-letter candidates are taken, the duplicate is kept and a warning is logged. This follows Susan's "never error" direction. It only happens if 26 or more codes in one rubric share a first letter.
- **D — Always uptick (AST-2007 default).** Identical-label pairs are re-lettered, never collapsed. Today's somerset `TP`/`TP` becomes `TP`/`TX`.

**Data (staging ops, not code):** after Steps 1 and 2 land, re-save somerset's Do rubric once in Artifacts. Step 2 retires the orphan `TP` row and Step 1 assigns `TX`. Then re-run `meteorite_grade_do` and compare `llm_call_seconds`.

### Blast radius

- **Rubric saves:** `apply_rubric_vectors_save` is shared by the UI save (`api_candidate.py`) and craft persist (`candidate._persist_craft_dispatch_success`). Both get the uptick, and neither call site changes. `submitted_rubric` in `api_candidate.py` is captured before the save, so the pending-clear logic is unaffected.
- **Rubric sync:** `sync_rubric_vectors_from_criteria` has the same callers and also runs from `scripts/migrations/backfill_rubric_vectors.py`. For any owner with legacy duplicate current rows, the next sync retires the extras. That is the intended outcome.
- **Reads:** `rubric_criteria_for_task` → `consult._vector_labels_map` keeps AST-1513's first-wins warning. It still fires for stored duplicates until the rubric is re-saved. `agent._decode_payload`'s duplicate-segment guard is unchanged.
- **Consult:** only `render_verdict`'s fall-through changes. Balance refusal (state held) and `empty_tokens` (`_empty_token_fail_dest`) come first and are unchanged. Roster's AST-1842 timeout hold is a separate module and is not touched.
- **Ledger:** additive columns. The AST-1960 host write keeps its success-only rule. `update_dispatch_ledger` has other callers (agent around lines 3139–3364, the dispatcher), and they are unaffected by the larger allowlist.
- **Timesheets:** `record_timesheet_entry` is passed as `record_timesheet` to the external clients. With the flag off, nothing writes `agent_timesheets.platform_cost`, `native_tokens_*`, or `platform_reconciled_at`, and new rows stay NULL there. AST-1966's batch re-total on a late cost never fires.
- **Tests that assume the old behavior (Betty, `[qa-handoff]` territory, not engineer-edited):**
  - `tests/component/core/test_candidate.py::test_normalize_rejects_duplicate_do_rubric_codes` expects `ValueError` and must flip to expecting repair.
  - The `docs/test-bible/core/candidate.md` AST-1513 row for that test.
  - AST-1963/1966 timesheet tests that expect the reconcile thread to spawn must set `TIMESHEET_RECONCILE_ENABLED = True` or assert that it doesn't spawn.

### What must still hold

- **AST-1513:** `_vector_labels_map` is first-wins with a warning (and `debug_detail` under `debug=True`). The `_decode_payload` duplicate-segment guard still rejects a duplicated code on one encoded line (AST-1155 retry path).
- **AST-1085 / AST-1881:** embedded QC/GC/RC still win on a code collision during the merge. The uptick runs after the merge, and pre-reserved codes mean it never re-letters an embedded code or produces one.
- **AST-723:** sync's fingerprint-gated retire/insert and importance-only update behave the same for unique codes.
- **AST-642:** a primary state goes to retry holding, and `*_RETRY` goes to terminal. Retry states are implicit (`retry_of`), not registered in `JOB_STATES`, so `_consult_batch_fail_dest` on a `_RETRY` state returns `error_state`. There is no loop.
- **AST-1960:** a failed call never overwrites `host`. The ledger write is non-fatal and runs via `asyncio.to_thread`.
- **AST-1189:** `PROVIDER_CALL_BUDGET` (600s, `max_retries: 0`) is unchanged. The retry is a state hop, not a provider re-send.
- **AST-1963:** `reconcile_timesheet_platform`, the `TIMESHEET_RECONCILE_*` tunables, `get_generation_stats`, and `get_batch_host` stay in code, unchanged.


## Radia review — AST-2008 (review-fix)

[code-rubric]
**Ticket:** AST-2008
**Publish ref:** `9efa75aa35cc7ca08c2553b2f7d4995206cea4bb` (`origin/sub/AST-2007/AST-2008-rubric-codes-timeout-ledger`)
**Corpus:** n/a — `docs/canon-index.md` absent on publish ref; empty frozen list scored per fix-lane pattern
**Overall:** CLEAN

## Fix-specific checks

**`[bug-repro]`:** OK — Betty F4 + manifest `docs/test-bible/core/candidate.md` § AST-2008 items 1–5 tie assertions to **To-be** / Repro steps:
| # | Area | Pin |
|---|------|-----|
| 1 | `TestAst2008RubricCodeUptick` | No raise (Repro 1); `TP,TX,SD`; `TP,TY,TX`; purity; Decision C |
| 2 | `TestAst2008SyncRetiresDuplicateCurrentRows` | Current `TP`/`TX`, r1 kept, r2 retired (Repro 3) |
| 3 | `TestAst2008RenderVerdictTimeoutRetry` | `METEORITE_PASSED_JD` → `_RETRY`; `_RETRY` → `METEORITE_FAILED_TECHNICAL_DO` (Repro 4) |
| 4 | `TestAst1960LedgerHost` + `TestAst2008LedgerCallOutcomeColumns` | `613.9` / `provider_call_timeout`; NULL class on success; no `host` on failure; last-call-wins / `provider_failed` (Repro 5) |
| 5 | `TestAst2008ReconcileSwitch` + `test_reconcile_ships_disabled` | Insert, no thread/routing (Repro 6) |

`test_normalize_accepts_duplicate_do_rubric_codes` is raise-only; uptick values are covered by siblings in the same class (plan: uptick on `apply_rubric_vectors_save`).

**`## What must still hold`:** OK — AST-1513 read guards unchanged; AST-1085 merge-then-uptick tested; AST-723/642/1960/1189/1963 constraints match diff (`render_verdict` hop only; host success-only; reconcile gated, body untouched; Decision B — no Performance Monitor).

## Canon scores

(no frozen canon list on Linear Description — fix-lane pattern; zero ids locked at Plan Approved; scored set empty)

## Column diff vs plan stage

no plan-stage scores attached (no F3 validate-plan artifact; Joan `[board-joan] CANON: OK` only)

## Frame diff

(none)

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon ids on AST-2008; Joan F2 OK without enumerated list.  
  **Recommendation:** No scope amendment unless Archie wants explicit ids on every fix bug.  
  **Default:** Proceed on empty scored set.

### advisory

- **Location:** Linear Description vs spawn  
  **Finding:** Description says “orphaned mini-parent”; spawn says **live** AST-2007, base `origin/ftr/AST-2007-meteorite-grade-do-timeout` — use **normal** merge path, not orphaned finish-up-to-dev.

- **Location:** `docs/test-bible/core/candidate.md` § AST-2008  
  **Finding:** Pre-existing reds outside manifest (e.g. `TestAst1966RetryThenGiveUp`) documented by Betty; not in this ftr…sub regression set.

## Plan fidelity (§5.4)

`git diff origin/ftr/AST-2007-meteorite-grade-do-timeout...origin/sub/AST-2007/AST-2008-rubric-codes-timeout-ledger`: 21 files, +587/−44 — Steps 1–6 + scope-gate `sync_rubric_vectors_from_criteria` duplicate retire; no cross-sibling product smuggle; Estimate **5** plausible.

## Chuckles — post-review branching

**PROCEED** + C7 complete + **normal parent** → **Review Posted** → clean-review shortcut → **User Testing**; **resolve-child** skipped.

---

```
[code-rubric] PROCEED (Commit: 9efa75aa) four-part meteorite fix clean
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Hedy | engineer | `/home/susan/.cursor/chats/257ed1c8ffb6f79f3e218ee5bced71d1/5f381b98-c56b-4496-a8d3-fa987a08c37a/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/31d79645-41ca-48d9-a0b4-a15d1e4b3397/store.db` |
| Radia | review | `/home/susan/.cursor/chats/257ed1c8ffb6f79f3e218ee5bced71d1/4b735e56-0439-4882-aaed-3bf394e4b55b/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2007 (parent) | ftr/AST-2007-meteorite-grade-do-timeout |
| AST-2008 | sub/AST-2007/AST-2008-rubric-codes-timeout-ledger |

**Epic worktree:** `astral-AST-2007/` — one active sub checked out at a time.
