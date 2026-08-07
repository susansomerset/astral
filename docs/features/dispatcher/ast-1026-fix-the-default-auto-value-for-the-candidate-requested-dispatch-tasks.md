# AST-1026 — Fix the default auto value for the candidate requested dispatch_tasks

<!-- linear-archive: AST-1026 archived 2026-08-05 -->

## Linear archive (AST-1026)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1026/fix-the-default-auto-value-for-the-candidate-requested-dispatch-tasks  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

### Research findings (confirmed on `$ASTRAL_MAIN` / `origin/dev`)

1. **Where AUTO-on was set:** commit `2ce7a744` (AST-972) — `ensure_candidate_stage_dispatch_tasks` called `save_dispatch_task(..., auto_mode=True, ...)` for every missing `(candidate_requested_resume|artifacts, REQUESTED_*)` pair.
2. **Boot still provisions those rows:** `start_scheduler()` → `provision_candidate_stage_dispatch_tasks()` → ensure on template `somerset` + every candidate that already has dispatch rows. Log line `AST-972 stage dispatch provision template=somerset touched=3 added=0 skipped=6` is that path (3 candidates × 2 keys already present → skip).
3. **Why the tick still fires them:** `get_due_tasks()` is `SELECT * FROM dispatch_task WHERE auto_mode = 1`. A row only reaches `Dispatching candidate_requested_artifacts…` if that row’s `auto_mode` is still **1**. Ensure **never updates** existing pairs — skip-only — so pre-1022 inserts stay AUTO on forever.
4. **Seed default already reversed in code:** commit `f0234c4c` (AST-1022, on `origin/dev`) set `CANDIDATE_STAGE_DISPATCH[*].auto_mode = False` and ensure now uses `entry.get("auto_mode", False)`. **New** missing pairs seed CLICK-only. AST-1022 plan explicitly left **out of scope** a one-time flip of already-seeded AUTO-on rows.
5. **Not** `repo_admin_json`**:** `data/admin/` only has `agent.json` / `agent_task.json` (no `dispatch_task`). Those log lines are unrelated.
6. **Local** `$ASTRAL_MAIN` **DB check:** `data/astral.db` currently has **0** `dispatch_task` rows (and 0 ledger hits for these keys), so the AUTO-on rows live on the host that produced Susan’s paste (Railway/prod). Prod admin data API returned 403 from this box (IP allowlist) — cannot dump live row values from here; the paste is sufficient proof those rows were AUTO on (`Dispatching…` only happens for due AUTO tasks).

### Plan to resolve

1. On the **live** DB that still auto-runs these keys (the environment in the brief): list `dispatch_task` where `task_key IN ('candidate_requested_resume','candidate_requested_artifacts')` and show `candidate_id, auto_mode` (include template `somerset`).
2. **One-time flip** those rows to `auto_mode=0` (admin AUTO toggle, or a narrow one-shot migration/script). Include template `somerset` so Apply Template cannot re-copy AUTO on.
3. **Do not** change the code seed again (already False). **Do not** make every boot rewrite `auto_mode` (would fight AST-1022 AC5 / operator toggles).
4. Restart or wait one tick: no `Dispatching candidate_requested_*` unless an operator turns AUTO on. CLICK Run still works.
5. Optional hardening only if needed after the flip: a checked-in one-shot migration under `scripts/migrations/` so the flip is repeatable/documented — not a standing provision rewrite.

## Done when

* Live `candidate_requested_resume` / `candidate_requested_artifacts` rows are AUTO **off** (including `somerset`), unless Susan deliberately left one on.
* Boot/tick no longer starts those tasks with AUTO off.
* CLICK Run still works; seed path for **new** rows remains AUTO off (AST-1022).

## Risks / open questions

* Confirm which env owns the paste DB before flipping (prod vs local Railway volume).
* Any candidate that should keep AUTO on for these keys — call out before blanket UPDATE.

---

## Original brief

```
Dispatching candidate_requested_artifacts — 1 available, batch candidate_requested_artifacts-4188c36d-e353-4fc5-9bb9-d8cc96be27af
Skipping candidate_requested_resume/karfo — no candidate or API key
[candidate_requested_resume] thread exited and cleared from registry
Stytch auth configured: env=test project_id=project-test-3c7ad997-81ae-4ca1-…
Loop mode candidate_requested_artifacts: 0 processed — stopping
Loop mode candidate_requested_resume: 0 processed — stopping
[candidate_requested_artifacts] thread exited and cleared from registry
[candidate_requested_resume] thread exited and cleared from registry
repo_admin_json applied table=agent rows=6
repo_admin_json applied table=agent_task rows=38
AST-972 stage dispatch provision template=somerset touched=3 added=0 skipped=6
Scheduler started — tick every 3min, max_auto_threads=3
 * Debugger is active!
```

Team chuckles set it up to auto-run, find where in the repo that happened and reverse it.

### Comments

#### chuckles — 2026-07-29T03:22:20.912Z
@susan Research pass done — confirmed, not guessed.

**Cause:** AST-972 (`2ce7a744`) seeded `candidate_requested_resume` / `candidate_requested_artifacts` with `auto_mode=True`. Boot still runs that provision (`start_scheduler` → ensure). Ensure **skips** existing pairs, so those rows stay AUTO on. Tick only wakes `auto_mode=1` (`get_due_tasks`) — that is why your paste shows `Dispatching candidate_requested_artifacts…` with `added=0 skipped=6`.

**Already fixed in code:** AST-1022 (`f0234c4c`, on `origin/dev`) seeds **new** rows AUTO **off**. It deliberately did **not** flip already-seeded rows.

**Not the culprit:** `repo_admin_json` (agent/agent_task only).

**Resolve plan:** one-time flip those live stage rows (incl. template `somerset`) to AUTO off on the env that produced the paste. Do not re-seed rewrite every boot. Details in Description.

— Chuckles

#### susan — 2026-07-29T03:19:41.356Z
@chuckles Thanks for this, but I want you, in this discussion, to DO THE RESEARCH TO CONFIRM, and then report here your plan to RESOLVE THE DISCOVERED ISSUE based on your findings.

---

_Implementation detail may live in git history on `origin/dev`._
