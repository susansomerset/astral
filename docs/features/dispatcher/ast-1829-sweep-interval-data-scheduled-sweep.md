# AST-1829 — Sweep interval data + scheduled sweep

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1829
- **Parent:** [AST-1824](https://linear.app/astralcareermatch/issue/AST-1824) — Add a sweep interval to dispatch_task
- **Publish ref:** `sub/AST-1824/AST-1829-sweep-interval-data-scheduled-sweep`

Each `dispatch_task` row gains a nullable `sweep_hrs` (hours; NULL/0 = off). On every scheduler tick, an AUTO-on row whose Avail is above 0 but below `min_count` becomes due **as a sweep** when at least `sweep_hrs` have passed since `last_run_at`. A tick-spawned sweep runs exactly one batch with an effective minimum of 1 — the same behavior today's manual Sweep (UI-initiated run on an AUTO row) already has in `_run_dispatch_loop` — but without the local-env debug forcing that `ui_initiated` triggers. Both AUTO due paths (claim-queue `get_due_tasks`, mailbox `_meteorite_email_due_tasks`) get the rule. The sweep is decided inside the existing due selection and spawned by the existing tick loop — no new thread, timer, or scheduler. Ships parent AC 1–10, 12, 15 (this ticket's AC 1–12). Admin API + UI are sibling AST-1830.

## Explicit scope gate

This ticket's **## Scope** names exactly two files:

- `src/data/database.py` — schema column (CREATE TABLE + missing-column migration map, no backfill), insert accepts optional sweep interval, update whitelist + AST-875 template-copy column set, new sweep-due helper reusing `_parse_dispatch_last_run_at`, `get_due_tasks` OR's in the sweep branch and marks sweep rows.
- `src/core/dispatcher.py` — mailbox due gets the same OR rule + mark (trigger / `freq_allows` gates kept), tick loop passes the mark into the spawn, `run_task` accepts a scheduled-sweep flag alongside `ui_initiated`, `_run_dispatch_loop` caps at one batch / min 1 for the flag on an AUTO row, no debug forcing for a non-UI sweep.

No other files. Do **not** edit `src/ui/api/api_admin.py` or `src/ui/frontend/src/pages/AdminScheduledActions.tsx` (AST-1830). Do not touch `tests/`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `sweep_hrs REAL` in fresh `CREATE TABLE` + `_migrate_cols`; `save_dispatch_task(sweep_hrs=)`; `sweep_hrs` in `_DISPATCH_TASK_UPDATE_COLS` + `_DISPATCH_TASK_TEMPLATE_COPY_COLS` + `_dispatch_task_schedule_assign`; new `dispatch_task_sweep_due`; sweep branch + `_scheduled_sweep` mark in `get_due_tasks` | data |
| `src/core/dispatcher.py` | Sweep branch + mark in `_meteorite_email_due_tasks`; `_tick_loop` passes mark to `run_task`; `run_task(scheduled_sweep=)`; `_run_dispatch_loop` one batch / min 1 when flagged on AUTO | core |

## Frozen names (contract with AST-1830)

- **Column:** `dispatch_task.sweep_hrs` — `REAL`, nullable, no default. NULL or `0` = no scheduled sweep. Mirrors `freq_hrs` naming. AST-1830's API/UI must use this exact key.
- **Due-dict mark / task-dict flag:** `_scheduled_sweep` (bool), same underscore convention as the existing `_ui_initiated`. Runtime only — never a column, never persisted.
- **Helper:** `database.dispatch_task_sweep_due(task) -> bool`, placed directly after `dispatch_task_freq_allows`.
- **Spawn kwarg:** `run_task(task_id, *, ui_initiated=False, scheduled_sweep=False)`.

## Stage 1: Data layer — column, insert/update/template, sweep-due helper, claim-queue due

**Done when:** On a fresh DB and on an existing DB without the column, `PRAGMA table_info(dispatch_task)` lists `sweep_hrs` as `REAL`, `notnull=0`, `dflt_value=None`, and pre-existing rows read `NULL`. `save_dispatch_task(..., sweep_hrs=2.5)` persists 2.5; `update_dispatch_task(id, sweep_hrs=4)` persists 4; a template copy from a row with `sweep_hrs=6` yields 6 on the target. `get_due_tasks()` returns an AUTO row with `min_count=10`, `sweep_hrs=1`, Avail 3, `last_run_at` 2h ago, with `_scheduled_sweep=True`; with `last_run_at` 10 min ago, NULL/0 `sweep_hrs`, or Avail 0 it is not returned; a row with Avail ≥ `min_count` is returned without `_scheduled_sweep`.

1. In `src/data/database.py`, `_ensure_dispatch_task_schema`, fresh-table branch (`CREATE TABLE dispatch_task (` inside `if cursor.fetchone()[0] == 0:`), add one line directly after `score_floor REAL,`:

   ```sql
                sweep_hrs REAL,
   ```

   Do **not** add it to any of the legacy rebuild `CREATE TABLE dispatch_task_new` blocks (enabled→auto_mode rename, AST-535 triple unique, AST-1088 null candidate) or their `INSERT … SELECT` column lists.

   ⚠️ **Decision:** Legacy rebuild blocks stay untouched. They only fire on ancient schema shapes, Scope names only the fresh `CREATE TABLE` + migration map, and they already omit `skip_daisy_chain` by the same precedent; `_migrate_cols` restores the column on the next ensure.

2. Same function, `_migrate_cols` dict (the "Add any other columns that may be missing from older schemas" block), add as the last entry after `"score_floor":    "REAL",`:

   ```python
            "sweep_hrs":      "REAL",  # AST-1829: scheduled sweep interval (hours); NULL/0 = off, no backfill
   ```

   No `UPDATE` / backfill anywhere — existing rows stay NULL.

3. `save_dispatch_task` — add a keyword parameter after `score_floor: Optional[float] = None,`:

   ```python
    sweep_hrs: Optional[float] = None,
   ```

   and extend the `INSERT INTO dispatch_task` statement inside `_with_conn` so `sweep_hrs` sits right after `score_floor` in both the column list and the values tuple (13 → 14 placeholders):

   ```python
                """INSERT INTO dispatch_task
                   (candidate_id, task_key, entity_type, trigger_state, sort_by, batch_call_mode,
                    freq_hrs, min_count, batch_size, auto_mode, score_floor, sweep_hrs, last_run_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (cid_val, tk, entity_type, trigger_state, sort_by, batch_call_mode,
                 freq_hrs, min_count, batch_size, int(auto_mode), score_floor, sweep_hrs, now, now),
   ```

   No parsing/validation in data (patt.entity.batch-criteria Arc 1: dispatch_task rows are not code-validated; AST-1830's API does the 400 on negatives). The `dispatcher.save_dispatch_task(*args, **kwargs)` passthrough needs no change.

4. `_DISPATCH_TASK_UPDATE_COLS` — add `"sweep_hrs"` to the set (append to the last line: `"task_key", "sort_by", "batch_call_mode", "sweep_hrs",`).

5. `_DISPATCH_TASK_TEMPLATE_COPY_COLS` — add `"sweep_hrs"` to the frozenset (append to the last line: `"max_runs", "score_floor", "sweep_hrs",`).

6. `_dispatch_task_schedule_assign` — change the existing `score_floor` branch so `sweep_hrs` is coerced the same way (NULL stays NULL, numbers become float):

   ```python
        elif col in ("score_floor", "sweep_hrs"):
            assign[col] = float(val) if val is not None else None
   ```

   `set_dispatch_tasks_from_template_rows` needs no change — it writes whatever `assign` holds.

7. Add the sweep-due helper directly **after** `dispatch_task_freq_allows` (reuse `_parse_dispatch_last_run_at`; do not write a second parser):

   ```python
   def dispatch_task_sweep_due(task: Dict[str, Any]) -> bool:
       """True when sweep_hrs > 0 and last_run_at is missing or at least sweep_hrs old (AST-1829).

       last_run_at is any run (AUTO batch, manual Run/Sweep, earlier scheduled sweep)."""
       sweep = float(task.get("sweep_hrs") or 0)
       if sweep <= 0:
           return False
       last = _parse_dispatch_last_run_at(task.get("last_run_at"))
       if last is None:
           return True
       return (datetime.now(timezone.utc) - last).total_seconds() >= sweep * 3600
   ```

8. `get_due_tasks` — replace the tail of the `for task in all_enabled:` loop (from `avail = count_eligible_for_dispatch_task(task)` through `due.append(task)`) with:

   ```python
        avail = count_eligible_for_dispatch_task(task)
        min_count = task.get("min_count") or 1  # match runner threshold (or 1) to avoid noisy zero-work runs
        if avail >= min_count:
            task["available_count"] = avail
            due.append(task)
        elif avail > 0 and dispatch_task_sweep_due(task):
            # AST-1829: partial remainder + sweep interval elapsed → one-batch sweep via the tick
            task["available_count"] = avail
            task["_scheduled_sweep"] = True
            due.append(task)
   ```

   Append one sentence to the docstring: `Rows with 0 < Avail < min_count are also due when dispatch_task_sweep_due is true (AST-1829); those carry _scheduled_sweep=True.` The `auto_mode = 1` SELECT is unchanged, so AUTO-off rows never reach either branch (AC 6).

   No logging of any level in this branch — `stat.logging.debug` bans debug in `src/data/`; the sweep-due debug line lives once in core (`_tick_loop`, Stage 2 step 2).

9. Compile: `python3 -m py_compile src/data/database.py`. Re-audit every literal `INSERT`/`UPDATE` on `dispatch_task` in this file (build-child §8): only `save_dispatch_task`'s INSERT changes shape; the legacy rebuild INSERTs keep their explicit 18-column lists (step 1 decision); `update_dispatch_task` and `set_dispatch_tasks_from_template_rows` build columns dynamically.

Commit: `code(AST-1829): sweep_hrs column, sweep-due helper, claim-queue sweep due`.

## Stage 2: Dispatcher — mailbox due, tick → spawn flag, one-batch sweep loop

**Done when:** A candidate-bound `stage_email_meteorite` AUTO row with bound Avail 2, `min_count` 5, `sweep_hrs` due, and `dispatch_task_freq_allows` true is in `_meteorite_email_due_tasks()` with `_scheduled_sweep=True`; with `freq_allows` false it is absent. A tick-spawned sweep row (Avail 3, `min_count` 10, `max_runs` 0) makes exactly one `_run_task` call, never logs "below min_count", and stamps `last_run_at`. With `is_local_deploy_env()` true and row `debug=0`, the sweep's `log_debug` stays false. `grep -n "Thread(" src/core/dispatcher.py` still returns exactly two matches.

1. In `src/core/dispatcher.py`, `_meteorite_email_due_tasks` — replace the per-task body after `if not meteorite_mailbox_trigger_allows(task): continue` (the `avail = …` line through `due.append(task)`) with:

   ```python
        avail = int(bound_counts.get(cid, 0))
        min_count = task.get("min_count") or 1
        sweep = avail < min_count
        # AST-1829: below min_count only proceeds as a sweep (Avail > 0 and sweep interval elapsed)
        if sweep and not (avail > 0 and database.dispatch_task_sweep_due(task)):
            continue
        # freq_hrs row cadence still gates both the normal and the sweep branch
        if not database.dispatch_task_freq_allows(task):
            continue
        if sweep:
            task["_scheduled_sweep"] = True  # sweep-due debug line is logged once in _tick_loop
        task["available_count"] = avail
        due.append(task)
   ```

   Change the docstring to: `"""AUTO candidate-bound inbox mailbox rows with live Avail ≥ min_count (or a due sweep, AST-1829) and freq allowing."""`

   ⚠️ **Decision:** For mailbox rows the flag only affects due selection. The mailbox run branch in `_dispatch_one_body` calls `check_email` directly (no `_run_dispatch_loop`, no `min_count` gate), so a mailbox sweep runs exactly as a normal mailbox AUTO run does today — the flag is carried but has nothing further to bypass.

2. `_tick_loop` — two edits, nothing else:

   a. Directly after the `due = list(database.get_due_tasks()) + _meteorite_email_due_tasks()` line (before the existing freq_hrs `# Note:` comment), add the single sweep-due debug site for both due paths:

   ```python
            # AST-1829: one sweep-due debug site for claim-queue and mailbox (no debug in src/data/)
            for t in due:
                if t.get("_scheduled_sweep"):
                    logger.debug(
                        "sweep due task_id=%s task_key=%s available=%s min_count=%s sweep_hrs=%s last_run_at=%s",
                        t.get("id"), t.get("task_key"), t.get("available_count"), t.get("min_count"),
                        t.get("sweep_hrs"), t.get("last_run_at"),
                    )
   ```

   The call is ungated (`stat.logging.debug`) — `log_debug` decides emission, not the caller.

   b. Change the spawn call inside `for task in due:` from `if run_task(tid):` to:

   ```python
                    if run_task(tid, scheduled_sweep=bool(task.get("_scheduled_sweep"))):
   ```

   `max_auto_threads` slots and the running-id skip apply to sweep rows unchanged.

3. `run_task` — change the signature to:

   ```python
   def run_task(task_id: int, *, ui_initiated: bool = False, scheduled_sweep: bool = False) -> bool:
   ```

   and directly after `task["_ui_initiated"] = ui_initiated` add:

   ```python
    task["_scheduled_sweep"] = scheduled_sweep  # AST-1829: tick-spawned sweep; row is re-read above so the due mark must be passed in
   ```

   `api_admin.py`'s `run_task(task_id, ui_initiated=True)` caller is untouched (defaults `scheduled_sweep=False`).

4. `_run_dispatch_loop` — after `ui_initiated = bool(task.get("_ui_initiated"))` add `scheduled_sweep = bool(task.get("_scheduled_sweep"))`, and replace the existing Sweep cap + comment:

   ```python
    # Sweep = UI click or tick-scheduled sweep (AST-1829) on an AUTO row: one batch, min 1.
    # Run (CLICK) and normal AUTO ticks honour row max_runs.
    if (ui_initiated or scheduled_sweep) and is_auto:
        max_runs = 1
   ```

   and replace the `effective_min` line + its comment:

   ```python
        # min_count gate only applies to normal unattended AUTO ticks — CLICK, manual Sweep
        # (UI-initiated on AUTO) and scheduled sweep (AST-1829) run whatever's available.
        effective_min = (task.get("min_count") or 1) if (is_auto and not ui_initiated and not scheduled_sweep) else 1
   ```

   `max_runs = 1` makes `max_runs=0` rows stop after one batch (the `if max_runs != 0` check sees 1). `last_run_at` is already stamped in `_dispatch_one_body`'s `finally` for every run — no change.

5. `_dispatch_one` — **no change.** Debug forcing stays `bool(task.get("debug")) or (ui_initiated and is_local_deploy_env())`; it reads only `_ui_initiated`, never `_scheduled_sweep` (AC 10).

   ⚠️ **Decision:** A separate `_scheduled_sweep` flag rather than reusing `_ui_initiated=True` for tick sweeps — reusing it would turn on local debug forcing (AC 10 fail) and mislabel an unattended run as UI-initiated.

6. Compile: `python3 -m py_compile src/core/dispatcher.py src/data/database.py`. Run `grep -n "Thread(" src/core/dispatcher.py` — must be exactly two lines (per-task thread in `run_task`, tick thread in `start_scheduler`).

Commit: `code(AST-1829): scheduled sweep in mailbox due, tick spawn, one-batch loop`.

## AC trace (this ticket)

| AC | Where |
|----|-------|
| 1 Column fresh + existing | S1 steps 1–2 |
| 2 Sweep due fires | S1 steps 7–8 |
| 3 Not due inside interval | S1 step 7 |
| 4 No interval, no sweep | S1 step 7 (`sweep <= 0 → False`) |
| 5 Zero Avail never sweeps | S1 step 8 / S2 step 1 (`avail > 0`) |
| 6 AUTO off never sweeps | existing `auto_mode = 1` SELECT / `auto_mode` filter in mailbox list — unchanged |
| 7 Full batches unaffected | S1 step 8 first branch unmarked; S2 step 4 flag false |
| 8 One batch, no min gate | S2 steps 2–4 |
| 9 Mailbox parity | S2 step 1 |
| 10 Debug forcing UI-only | S2 step 5 |
| 11 Template copy | S1 steps 5–6 |
| 12 No parallel scheduler | S2 step 6 grep |

## Canon

Scope list: `patt.entity.batch-criteria`, `patt.entity.batch-processing` (read in full), `astral.batch.claim-process-release`, `astral.dispatch.entity-state-bound`, `stat.logging.info.dispatcher`, `stat.logging.debug` (id-only until build-child §8).

- batch-criteria: `sweep_hrs` is eligibility/cadence row data alongside `freq_hrs` — read fresh each tick, no literal in the caller, no data-layer validation.
- batch-processing / claim-process-release: a sweep is one ordinary `_run_task` iteration — same claim, `batch_id`, release; nothing new in the claim path.
- entity-state-bound: sweep uses the row's own `entity_type` / `trigger_state` / `candidate_id` via the unchanged `count_eligible_for_dispatch_task` and `_run_task`.
- logging.info.dispatcher: sweep runs end in the existing `_log_dispatch_task_completed` line — no new info lines.
- logging.debug: sweep-due decisions log once, ungated, via `logger.debug` in `dispatcher._tick_loop`; no debug in `src/data/`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Revisions

Revision 1 — 2026-09-28
Driven by: Joan `[plan-discuss] round=1 concern` — fix-now: remove `_log.debug` from `get_due_tasks` (`stat.logging.debug` bans debug in `src/data/`), log sweep-due once in `src/core/dispatcher.py`; discuss: note `sweep_hrs` as eligibility/cadence row data alongside `freq_hrs`.
Changes: S1 step 8 drops the `_log.debug` block (plus a no-logging note). S2 step 1 drops the mailbox `logger.debug` block. S2 step 2 adds one ungated `logger.debug` loop over `due` in `_tick_loop` covering both due paths. Canon batch-criteria and logging.debug bullets updated.

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Ticket:** AST-1829
**Overall:** REVISE
**Corpus:** a0bc2f0e5b5810448cf465ebeff84ffb6f1d60b6
**Publish ref:** `origin/sub/AST-1824/AST-1829-sweep-interval-data-scheduled-sweep` @ `3e9a1c56567b65aa8eeae9e40549564e57187839`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |
| patt.entity.batch-processing | A | | |
| astral.batch.claim-process-release | A | | |
| astral.dispatch.entity-state-bound | A | | |
| stat.logging.info.dispatcher | A | | |
| stat.logging.debug | D | 2 | S1 step 8: `_log.debug` in `get_due_tasks` (`src/data/database.py`) |

## Traceability

AC 1 → S1 steps 1–2 · AC 2 → S1 steps 7–8 · AC 3 → S1 step 7 · AC 4 → S1 step 7 (`sweep <= 0`) · AC 5 → S1 step 8 / S2 step 1 (`avail > 0`) · AC 6 → S1 step 8 (`auto_mode = 1` SELECT unchanged) · AC 7 → S1 step 8 first branch / S2 step 4 · AC 8 → S2 steps 2–4 · AC 9 → S2 step 1 · AC 10 → S2 step 5 · AC 11 → S1 steps 5–6 · AC 12 → S2 step 6 (Thread grep) · Parent AC 11/13/14 → N/A (AST-1830)

## Findings

### fix-now

- **Location:** Stage 1 step 8 (`get_due_tasks` sweep branch)
- **Finding:** Plan commits to ungated `_log.debug(...)` inside `src/data/database.py` for sweep-due selection. `stat.logging.debug` explicitly lists debug in `src/data/` as a Don't (`logger.debug` / equivalent); data may use warning/error elsewhere, but sweep-due diagnostics belong in core (mailbox path already uses `logger.debug` in S2 step 1).
- **Recommendation:** Remove the `_log.debug` block from `get_due_tasks`. Log sweep-due once in `src/core/dispatcher.py` (e.g. in `_tick_loop` when iterating `due` and `task.get("_scheduled_sweep")`, or a small core helper called from both due paths) so claim-queue and mailbox stay consistent without data-layer debug.

### discuss

- **Location:** Plan `## Canon` (batch-criteria bullet)
- **Finding:** `patt.entity.batch-criteria` Arc 1 names `freq_hrs` / `score_floor` but not `sweep_hrs`; the plan’s reading (interval as row criteria, no caller literals, no data validation) matches the pattern’s intent and parent architectural definition.
- **Recommendation:** No canon amend required for this child; optional one-line plan note that `sweep_hrs` is eligibility/cadence row data alongside `freq_hrs`.

### acceptable

- **Location:** Explicit scope gate / Files Changed
- **Finding:** Two-file footprint matches ticket `## Scope`; AST-1830 API/UI explicitly excluded; frozen `sweep_hrs` / `_scheduled_sweep` / `dispatch_task_sweep_due` / `scheduled_sweep` kwarg contract is clear.
- **Recommendation:** None.

- **Location:** S2 step 1 (mailbox sweep flag)
- **Finding:** Mailbox sweep mark does not change `_run_dispatch_loop` behavior (documented decision); consistent with parent functional scope for mailbox path.
- **Recommendation:** None.

- **Location:** Identity / status
- **Finding:** AST-1829 is **Plan Ready**, assignee Joan; no prior `[plan-discuss]` rounds (0 completed). Parent AST-1824 definition and child AC 1–12 align with stages; sibling AC 11/13/14 correctly out of scope.

## R6 notes (non-canon checklist)

- Definition fidelity: matches AST-1829 slice of AST-1824; no scope creep into `api_admin` / frontend / tests.
- DRY: reuses `_parse_dispatch_last_run_at`, mirrors existing UI Sweep loop semantics via `scheduled_sweep` (AC 10 preserved).
- Missing self-assessment block in plan doc: not blocking; Estimate confirm line present.

context_tokens≈22000

## Joan validate — round 1 re-check

[plan-rubric]
**Ticket:** AST-1829
**Overall:** APPROVED
**Corpus:** a0bc2f0e5b5810448cf465ebeff84ffb6f1d60b6
**Publish ref:** `origin/sub/AST-1824/AST-1829-sweep-interval-data-scheduled-sweep` @ `c8314af01615f1d2adfb4bb326a27586c56c3869`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |
| patt.entity.batch-processing | A | | |
| astral.batch.claim-process-release | A | | |
| astral.dispatch.entity-state-bound | A | | |
| stat.logging.info.dispatcher | A | | |
| stat.logging.debug | A | | |

## Traceability

AC 1 → S1 steps 1–2 · AC 2 → S1 steps 7–8 · AC 3 → S1 step 7 · AC 4 → S1 step 7 (`sweep <= 0`) · AC 5 → S1 step 8 / S2 step 1 (`avail > 0`) · AC 6 → S1 step 8 (`auto_mode = 1` SELECT unchanged) · AC 7 → S1 step 8 first branch / S2 step 4 · AC 8 → S2 steps 2–4 · AC 9 → S2 step 1 · AC 10 → S2 step 5 · AC 11 → S1 steps 5–6 · AC 12 → S2 step 6 (Thread grep) · Parent AC 11/13/14 → N/A (AST-1830)

## Findings

### acceptable

- **Location:** `## Revisions` / S1 step 8 / S2 step 2a
- **Finding:** Round-1 fix-now closed: no debug in `src/data/`; single ungated `logger.debug` over merged `due` in `_tick_loop` covers claim-queue and mailbox marks.
- **Recommendation:** None.

- **Location:** Plan Discuss thread
- **Finding:** One completed round (`[plan-discuss] round=1 concern` via Joan upshot + Ada `round=1 reply` @ `c8314af0`); cap not hit.
- **Recommendation:** Chuckles may move to **Plan Approved** and restore implementer per skill §8.

context_tokens≈28000

## Review

- **Branch:** `origin/sub/AST-1824/AST-1829-sweep-interval-data-scheduled-sweep`
- **Stage 1:** `9f61f1ce` — `code(AST-1829): sweep_hrs column, sweep-due helper, claim-queue sweep due`
- **Stage 2:** `506c2d77` — `code(AST-1829): scheduled sweep in mailbox due, tick spawn, one-batch loop`
- **Build notes:** `py_compile` clean on both files; ruff `F,E9` shows no new findings vs pre-change. `grep -c "Thread(" src/core/dispatcher.py` = 2. Literal INSERT/UPDATE audit: `save_dispatch_task` is the only shape change; `apply_config_table_upsert` derives columns from live schema; `config.py` SEED_CONFIG inserts name columns explicitly (nullable `sweep_hrs` → NULL); legacy rebuild blocks unchanged per S1 step 1 decision.

## Radia review

[code-rubric]
**Ticket:** AST-1829
**Publish ref:** `4e623d46d0e92da370e0b290d3595823d78eff0b` (`origin/sub/AST-1824/AST-1829-sweep-interval-data-scheduled-sweep`)
**Corpus:** a0bc2f0e5b5810448cf465ebeff84ffb6f1d60b6
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |
| patt.entity.batch-processing | A | | |
| astral.batch.claim-process-release | A | | |
| astral.dispatch.entity-state-bound | A | | |
| stat.logging.info.dispatcher | A | | |
| stat.logging.debug | A | | |

## Column diff vs plan stage

(aligned) — Joan round-1 re-check scored all **A** on the same six ids; code matches the revised plan (no `logger.debug` in `src/data/`, single ungated sweep-due site in `_tick_loop`).

## Frame diff

(none) — Linear **Acceptance criteria** 1–12 in the issue description match what the tip implements and what Betty’s manifest maps; no new checklist rows required for `resolve-child` §10.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **sibling test carry:** `merge-tests` on the sub brings non–AST-1829 paths into the three-dot diff — e.g. `tests/component/frontend/**`, `tests/component/ui/api/test_api_candidate.py`, `docs/test-bible/frontend/lib.md`, `docs/test-bible/ui/api/api_candidate.md`. Product scope stays `src/data/database.py` + `src/core/dispatcher.py` only; do not treat those as AST-1829 scope violations.
- **Linear one-liner vs child AC 11:** Description “Ships AC 1–10, 12, and 15” omits **11** (template copy) while the child plan, tests (`TestAst1829SweepInterval::test_template_copy_carries_sweep_hrs`), and data diff include it. Plan doc is authoritative on this ticket; no code change implied.

## What's solid

- Two-file product footprint matches **## Scope** and explicit scope gate; AST-1830 API/UI untouched.
- `sweep_hrs` wired through fresh `CREATE TABLE`, `_migrate_cols`, `save_dispatch_task` (14-column INSERT / bind tuple aligned in diff), update whitelist, template-copy cols, and `dispatch_task_sweep_due` reusing `_parse_dispatch_last_run_at`.
- Claim-queue and mailbox due rules share the same sweep predicate; `_scheduled_sweep` is runtime-only; `run_task(..., scheduled_sweep=)` re-applies the due mark after re-read.
- `_run_dispatch_loop` mirrors UI Sweep: one batch + `effective_min` bypass for `scheduled_sweep`; `_dispatch_one` still gates `log_debug` on `debug` / `ui_initiated` only (AC 10 covered in `TestAst1829ScheduledSweep::test_sweep_one_batch_no_min_gate_and_debug`).
- `grep -n "Thread("` still exactly two sites in `dispatcher.py` (AC 12).
- Component coverage for AST-1829 is documented in `docs/test-bible/core/dispatcher.md` § AST-1829 and `docs/test-bible/data/database/dispatch_tasks.md`.

## Recommended actions (downstream only — not executed in this session)

- Chuckles: append this artifact to `docs/features/dispatcher/ast-1829-sweep-interval-data-scheduled-sweep.md`, `docs()` commit on the sub, post slim upshot `--as radia`, move **Review Posted**; **PROCEED** → datt may route toward **User Testing** per §3h.
- Optional: align Linear description “Ships …” line with child AC 11 if you want Description and plan byte-identical (cosmetic).

```
[code-rubric] PROCEED (Commit: 4e623d46) scheduled sweep clean
```

context_tokens≈38000
