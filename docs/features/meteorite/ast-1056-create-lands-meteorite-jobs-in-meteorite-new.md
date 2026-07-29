# AST-1056 — Create lands meteorite jobs in METEORITE_NEW

**Linear:** [AST-1056](https://linear.app/astralcareermatch/issue/AST-1056/create-lands-meteorite-jobs-in-meteorite-new-processing-meteorites)
**Parent:** [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — Processing meteorites
**Publish ref:** `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`

Retarget meteorite job create so Manage Email **Create** / `POST …/meteorite/jobs` / `create_meteorite_job` inserts new jobs in **METEORITE_NEW** (meteorite GDL entry) instead of the AST-1042 default **JD_READY**. Config owns the landing state; core already reads `METEORITE_CONFIG["job_create_state"]`. Does **not** own GDL state registration, dispatch rows, agent prompts, or Recommended Meteorites.

**Depends on:** AST-1053 (`METEORITE_NEW` in `JOB_STATES` with `prior_states: None`) — already on `origin/ftr/AST-1052-processing-meteorites` / this sub after merge.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Set `METEORITE_CONFIG["job_create_state"]` → `"METEORITE_NEW"`; refresh adjacent comments | utils |
| `src/core/meteorite.py` | Update module + `create_meteorite_job` docstrings to name **METEORITE_NEW** / config key (no call-path logic change) | core |

No API, inbox, UI, dispatcher, or Recommended edits. Do **not** edit `tests/` or `docs/test-bible/**` (Betty).

## Stage 1: Config create landing → METEORITE_NEW

**Done when:** `METEORITE_CONFIG["job_create_state"] == "METEORITE_NEW"`, the existing `assert … in JOB_STATES` still passes at import, and comments no longer claim JD_READY as the create default. No dispatcher / Recommended / GDL-state edits.

1. In `src/utils/config.py`, in the `METEORITE_CONFIG` block (after AST-1041 company template keys), change:

```python
    # AST-1042 / AST-1056 job-create defaults (consumed by create_meteorite_job)
    "job_create_state": "METEORITE_NEW",
    "job_create_latest_score": 10.0,
```

Keep `"job_create_latest_score": 10.0` unchanged (synthetic score stand-in; meteorite dispatch `score_floor` 0 is sibling AST-1054 — out of scope).

2. Update the block comment immediately above `METEORITE_CONFIG` so it no longer says create defaults are **JD_READY**. Replace the JD_READY phrase with **METEORITE_NEW** (meteorite GDL entry / AST-1056). Leave company-ensure commentary intact.

3. Do **not** change `JOB_STATES`, `IN_REVIEW_STATES`, `SKIPPED_STATES`, `PASSED_SCORE_GATED_STATES`, `RECOMMENDED` priors, `TASK_CONFIG`, or any `DISPATCH_*` tables.

⚠️ **Decision — config-only landing retarget:** `create_meteorite_job` already assigns `state = METEORITE_CONFIG["job_create_state"]` and inserts via `save_job` (AST-1042 create carve-out). Hardcoding `"METEORITE_NEW"` in core would violate `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets`. Do not invent a second create path.

⚠️ **Decision — keep direct insert (no `transition_job_state`):** `METEORITE_NEW` has `prior_states: None` (AST-1053), so first-write insert is a lawful unrestricted entry (same shape as `ingest_jobs` → `NEW`). Do not route create through `transition_job_state`.

⚠️ **Decision — leave `job_create_latest_score` at 10.0:** Parent AC6 is landing state only. Score-floor behavior for meteorite GDL is AST-1054.

## Stage 2: Docstring honesty in `meteorite.py`

**Done when:** Module and `create_meteorite_job` docs describe landing via `METEORITE_CONFIG["job_create_state"]` (**METEORITE_NEW** after Stage 1); create still inserts without `transition_job_state`; runtime body unchanged except docs.

1. In `src/core/meteorite.py`, rewrite the module docstring so it no longer claims jobs land in **JD_READY**. State that API-facing create inserts into `METEORITE_CONFIG["job_create_state"]` (meteorite GDL entry **METEORITE_NEW** after AST-1056), with synthetic `latest_score` from `job_create_latest_score`. Keep: lazy-ensure company, no email ingest / admin UI ownership in this module’s ensure path, leave-in-place rows.

2. Rewrite `create_meteorite_job`’s docstring:

- Summary line: insert a job from raw HTML into `METEORITE_CONFIG["job_create_state"]` (not a hardcoded **JD_READY** name).
- Carve-out paragraph: first write inserts directly into that config state via `save_job` (same pattern as ingest → `NEW`); do **not** call `transition_job_state`. Note that **METEORITE_NEW** is unrestricted (`prior_states: None`); do **not** expand normal `JD_READY` priors and do **not** invent a new job state on this ticket.
- Returns block: keep the same keys (`astral_job_id`, `company`, `state`, `latest_score`, `company_inserted`, `job`).

3. Do **not** change the function body: still read `state` / `score` from `METEORITE_CONFIG`, still two-step `save_job` + `latest_score` update, still postcondition checks against the config-derived `state` / `score`.

4. Do **not** edit `src/ui/api/api_meteorite.py`, `src/core/inbox.py`, `src/ui/api/api_inbox.py`, or frontend Manage Email — they already propagate `payload["state"]` from core.

**Done when (recheck):** `python3 -m py_compile src/utils/config.py src/core/meteorite.py` succeeds; `from src.utils.config import METEORITE_CONFIG, JOB_STATES` shows `METEORITE_CONFIG["job_create_state"] == "METEORITE_NEW"` and that key is in `JOB_STATES`; a manual mental trace of Manage Email Create → `create_meteorite_job_from_inbox_message` → `create_meteorite_job` yields insert state **METEORITE_NEW**.

## Out of scope (do not implement)

- Parallel meteorite `JOB_STATES` / In Review manifests (AST-1053 — already landed on ftr).
- Meteorite dispatch rows / `score_floor` 0 (AST-1054).
- `meteorite_like` / meteorite upshot agent_task prompts (AST-1055).
- Recommended **Meteorites** section (AST-1057).
- Normal (non-meteorite) GDL create / `JD_READY` scrape path.
- Test-tree or bible edits (Betty updates AST-1041/1042/1053 asserts that still expect `JD_READY`).

## Self-Assessment

**Scope:** `minor` — one config key retarget plus docstring updates in the existing meteorite create module; no new files or layers.

**Conf:** `high` — create already consumes `job_create_state`; AST-1053 already registered unrestricted `METEORITE_NEW`; API/inbox need no wiring changes.

**Risk:** `Medium` — wrong landing state would put meteorite jobs on the vetted-company GDL trail (or an illegal state); confining the change to the config key plus docs keeps the blast radius to the meteorite create path only.

## Rules self-review

- §1.4 / `astral.standards.no-hardcoded-sets` — landing state stays in `METEORITE_CONFIG`, not hardcoded in core.
- §2.1 / `astral.config.config-source-of-truth` — single key owns create default; assert `in JOB_STATES` unchanged.
- §2.6 / `astral.state.job-prior-states-enforced` — insert into `METEORITE_NEW` (`prior_states: None`) is lawful unrestricted entry; no illegal hop via `transition_job_state`.
- §3.3 imports — no new imports.
- §2.4 batch — untouched (create is not a claim batch).
- Engineer must not edit `tests/` / bible; Betty owns assert flips from `JD_READY` → `METEORITE_NEW`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`
**Plan path:** `docs/features/meteorite/ast-1056-create-lands-meteorite-jobs-in-meteorite-new.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `b8850e8e` | `job_create_state` → METEORITE_NEW + meteorite.py docstring honesty |

**Tip:** `b8850e8e83f185083250b42be865dc613651b434` on `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`
