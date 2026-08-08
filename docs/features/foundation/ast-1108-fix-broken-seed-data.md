# AST-1108 — Fix broken seed data

<!-- linear-archive: AST-1108 archived 2026-08-07 -->

## Linear archive (AST-1108)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1108/fix-broken-seed-data  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** cursorapp  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Next steps (for Chuckles → Betty)

**Publish ref:** `origin/ftr/AST-1108-fix-broken-seed-data` @ `547d26d6` (pushed; includes merge of `origin/dev`).

### 1. Betty — update tests for Track 3 product change `[qa-handoff]`

Cover-letter / artifact-chain dispatch defaults are now `BUILD_ARTIFACTS` (graduation *output* is `CANDIDATE_REVIEW`). Four tests still assert the old default — Betty owns the tree:

* `tests/component/utils/test_config.py`
  * `TestAst955RegisteredKeyDispatchAdminDefaults::test_check_cover_letter_without_override_defaults_candidate_review`
  * `TestAst962CoverLetterMidHopDefaultTrigger::test_dispatch_trigger_state_defaults`
  * `TestAst962CoverLetterMidHopDefaultTrigger::test_admin_defaults_without_override`
  * `TestAst962CoverLetterMidHopDefaultTrigger::test_draft_cover_letter_and_grade_do_unchanged` (flip cover-letter half only; `grade_do` → `PASSED_JD` still correct)

Expected: `_dispatch_trigger_state_for_task_key` / `dispatch_task_admin_defaults` → `BUILD_ARTIFACTS` for `draft_cover_letter`, `check_cover_letter`, `finalize_cover_letter`, `propose_application_responses`. Override-based tests may stay. Update bible rows under `docs/test-bible/utils/config.md` if they document the old AST-962 default.

Also worth a quick pass: this branch already had ~10 unrelated failures in `test_config.py` / `test_api_admin.py` before Track 3 (gaze_email `freq_hrs`, seed-statute registration, prefilter grouping, resolve-tokens) — do not misattribute those to the cover-letter change.

### 2. After Betty green — land on `origin/dev`

Merge `origin/ftr/AST-1108-fix-broken-seed-data` → `origin/dev` (prep-uat / Chuckles ship path). Then on staging/prod run once:

```bash
python scripts/migrations/retarget_artifact_chain_trigger_state.py --apply
```

(dry-run default; local already applied). Restart app so retired vet migrations + SA grouping fix are live.

### 3. Still deferred (not required for this merge)

* **Track 1 compliance:** all-candidate meteorite provision; audit remaining ensure-time data writers (AST-561 / 723 / 738); wire `SEED_CONFIG` beyond scaffolding.
* Topic Menu still shares `task_group_order` `2000` with Candidate Artifacts.
* `task_type: CHAIN` as trigger-default proxy — later `config.py` analysis.
* Full removal of `bootstrap_candidate_context` TASK_CONFIG stub (catalog row already omitted).

---

## Seed needs (Archie / define)

* `agent` / `agent_task`: keep non-empty repo JSON under `data/admin/` (repo-wins at bootstrap).
* Non-JSON seeds (`dispatch_task`, etc.): SQL-first `SEED_CONFIG` / coverage joins — no template-only candidate hardcodes.
* No hot-path prompt or catalog writes inside `_ensure_*_schema` (see Track 4).

## Work tracks

1. **Compliance** — statute machinery: provision meteorite (+ other) catalogs for all `candidate` rows; audit leftover hot-path seed/migrations in `database.py`; keep agent JSON non-empty.
2. **Grouping (Scheduled Actions)** — unique / normalized `task_group_order` in `agent_task.json` (Preamble was unquoted `1`; quoted to `"1"` as first slice).
3. **Wrong data** — four live `dispatch_task` rows with `trigger_state=CANDIDATE_REVIEW` (not a dispatch-ready job state); delete or retarget (original repro below).
4. **Hot-path agent_task thrash (fixed)** — AST-776/822/880 `vet_inflow_discovery` prompt migrations in `_ensure_agent_task_schema` overwrote each other once per process (880 seed omitted prior markers) → new `task_key_uuid`/`updated_at` forever → permanent Manage Tasks "Revert to file" banner. Retired those migrations; authoritative prose stays in `data/admin/agent_task.json`. Sibling data migrations still on ensure (e.g. AST-561, AST-723, AST-738) need the same audit under Track 1.

**Ops note:** local `DB_PATH` is shared across worktrees (`…/astral/data/astral.db`); multiple `server.py` processes amplify any remaining hot-path writers.

---

We seem to have wandered off the path with our seed data scenario.  Work with me to figure out how we can make sure the data that is seeded is accurate and not creating ghost issues on its own.

Specifically, 'CANDIDATE_REVIEW' is NOT a dispatch-ready job state, and should not be the input state.

```
[
  {
    "auto_mode": 0,
    "batch_call_mode": 0,
    "batch_id": null,
    "batch_size": 1,
    "candidate_id": "somerset",
    "debug": 0,
    "entity_type": "job",
    "freq_hrs": 0,
    "id": 11177,
    "last_run_at": "2026-07-10 16:07:53",
    "max_runs": 1,
    "min_count": 1,
    "score_floor": null,
    "skip_cache": 0,
    "sort_by": "state_changed_at",
    "task_key": "draft_cover_letter",
    "trigger_state": "CANDIDATE_REVIEW",
    "updated_at": "2026-07-10 16:07:53"
  },
  {
    "auto_mode": 0,
    "batch_call_mode": 0,
    "batch_id": null,
    "batch_size": 1,
    "candidate_id": "johnson",
    "debug": 0,
    "entity_type": "job",
    "freq_hrs": 0,
    "id": 11201,
    "last_run_at": null,
    "max_runs": 1,
    "min_count": 1,
    "score_floor": null,
    "skip_cache": 0,
    "sort_by": "state_changed_at",
    "task_key": "draft_cover_letter",
    "trigger_state": "CANDIDATE_REVIEW",
    "updated_at": "2026-07-12 22:47:48"
  },
  {
    "auto_mode": 0,
    "batch_call_mode": 0,
    "batch_id": null,
    "batch_size": null,
    "candidate_id": "somerset",
    "debug": 0,
    "entity_type": "job",
    "freq_hrs": 0,
    "id": 11203,
    "last_run_at": "2026-07-23 18:36:10",
    "max_runs": 1,
    "min_count": 1,
    "score_floor": null,
    "skip_cache": 0,
    "sort_by": "state_changed_at",
    "task_key": "check_cover_letter",
    "trigger_state": "CANDIDATE_REVIEW",
    "updated_at": "2026-07-23 18:36:10"
  },
  {
    "auto_mode": 0,
    "batch_call_mode": 0,
    "batch_id": null,
    "batch_size": null,
    "candidate_id": "karfo",
    "debug": 0,
    "entity_type": "job",
    "freq_hrs": 0,
    "id": 11204,
    "last_run_at": "2026-07-23 19:45:22",
    "max_runs": 1,
    "min_count": 1,
    "score_floor": null,
    "skip_cache": 0,
    "sort_by": "state_changed_at",
    "task_key": "check_cover_letter",
    "trigger_state": "CANDIDATE_REVIEW",
    "updated_at": "2026-07-23 19:45:22"
  }
]
```

### Comments

#### chuckles — 2026-07-31T23:39:30.244Z
## Landed on `origin/dev`

Fast-forwarded `origin/dev` to **`0d45ec8f`** (ftr tip including Betty merge-tests). Deleted **`origin/ftr/AST-1108-fix-broken-seed-data`**.

**Still for ops after Railway picks up `dev`:**
```bash
python scripts/migrations/retarget_artifact_chain_trigger_state.py --apply
```
Restart so retired vet migrations + SA grouping are live. Track 1 / deferred items unchanged.

#### betty — 2026-07-31T23:30:49.592Z
[qa-handoff]

## QA test manifest — AST-1108 (Track 3 cover-letter defaults)

**Publish:** `origin/ftr/AST-1108-fix-broken-seed-data` @ `0d45ec8f` (`merge-tests(AST-1108): origin/tests 10faa22d`)
**Product tip included:** `547d26d6` +
**Betty SHA:** `10faa22d` (`test(AST-1108): cover-letter defaults expect BUILD_ARTIFACTS`)

### Classification
1. **Existing coverage (revised):** AST-962 / AST-955 cover-letter admin-default suites — still the right homes; expected Input State is now **`BUILD_ARTIFACTS`** (`CANDIDATE_REVIEW` = graduation *output*).
2. **Broken / obsolete (revised this pass):**
   - `tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults::test_check_cover_letter_without_override_defaults_build_artifacts` (renamed)
   - `tests/component/utils/test_config.py::TestAst962CoverLetterMidHopDefaultTrigger` (3 methods; `grade_do` → `PASSED_JD` unchanged)
   - `tests/component/data/database/test_dispatch_tasks.py::TestAst962SaveDispatchTaskCoverLetterDefaults` (omit-trigger insert → `BUILD_ARTIFACTS`)
3. **Gaps:** none. **No new integration scenarios.**

Override-based tests that pass `trigger_state="CANDIDATE_REVIEW"` stay.

### Narrowed run (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst962CoverLetterMidHopDefaultTrigger \
  tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults \
  tests/component/data/database/test_dispatch_tasks.py::TestAst962SaveDispatchTaskCoverLetterDefaults \
  -q
```

**Pass criterion:** pytest green on those lines — not zero-arg harness / branch-lock gate.

### Bible shasums on publish tip
- `docs/test-bible/utils/config.md` — `e4cd5d7653e2431560b76ce7b898efa19157052b`
- `docs/test-bible/data/database/dispatch_tasks.md` — `9e17cabfaa15a4b42e15c50f93ac8b57040a29f1`

### Note
Pre-existing unrelated reds in `test_config.py` / `test_api_admin.py` (gaze_email `freq_hrs`, seed-statute registration, prefilter grouping, resolve-tokens) are **not** Track 3 — do not misattribute.

— Betty

#### chuckles — 2026-07-31T23:28:05.066Z
[check-linear] Code Complete — Betty qa-child on origin/ftr/AST-1108-fix-broken-seed-data

#### susan — 2026-07-31T23:26:01.755Z
@chuckles Please read the content of this issue and summon betty as a one-off to prepare tests as usual for the ftr branch on origin (everything is committed and pushed to that branch and recently refreshed from dev origin).

#### chuckles — 2026-07-31T23:23:54.977Z
## Ready for Betty (prodesk)

**Branch:** `origin/ftr/AST-1108-fix-broken-seed-data` @ **`547d26d6`** — already on origin; includes `origin/dev` merge.

### Product already shipped on this ftr tip

| Track | What landed |
|---|---|
| Statutes | Six `astral.seed.*` + `astral.standards.names-not-ticket-ids` |
| SEED_CONFIG | SQL-first scaffolding in `config.py` (not fully wired) |
| Track 4 | Retired AST-776/822/880 hot-path vet prompt migrations |
| Track 3 | Artifact-chain / cover-letter defaults → `BUILD_ARTIFACTS`; migration script retargets `CANDIDATE_REVIEW` rows |
| Track 2 (slice) | SA grouping: API fallback uses catalog meta; three missing `agent_task.json` shells restored; bootstrap left out |

### Betty action `[qa-handoff]`

Update assertions (and bible if needed) so cover-letter mid-hop / draft defaults expect **`BUILD_ARTIFACTS`**, not `CANDIDATE_REVIEW`. Files/tests listed in the issue **Next steps** section.

Engineer did **not** touch `tests/**` or `docs/test-bible/**` per `astral.git.engineer-test-tree-ban`.

### After Betty

Chuckles: merge ftr → `origin/dev`, run retarget migration `--apply` on staging/prod, restart. Track 1 + remaining grouping polish stay deferred.

@susan — hand Betty from here when ready.

#### chuckles — 2026-07-31T23:07:45.083Z
## Track 2 slice — Scheduled Actions “(unassigned)” grouping

**Root cause (two defects):**
1. `GET /dispatch_tasks/task_keys` fallback for keys outside `get_task_keys()` hard-coded empty `task_group_*` — ignored live `agent_task` metadata for `gaze`, `recheck_no_openings`, fetch_*, `inflow_discovery`, `prefilter`.
2. `candidate_requested_resume` / `candidate_requested_artifacts` / `find_company_website` were missing from `data/admin/agent_task.json`, so repo-wins boot retired their current rows.

**Fix:** Fallback now uses `_dispatch_task_key_form_meta` (same catalog path as registry keys). Added the three shell rows (Intake `1000` seq 4–5; Roster `3000` seq 3). `bootstrap_candidate_context` stays out of the JSON (decommissioned; TASK_CONFIG key retained with comment for legacy test reference).

After restart / Revert to file: no `(unassigned)` sections; fetch tasks land under Company Roster / Job Review; candidate_requested_* under Candidate Intake.

#### chuckles — 2026-07-31T22:00:42.326Z
## Track 3 landed — CANDIDATE_REVIEW is an output state

Archie's call: `CANDIDATE_REVIEW` is the **output** of the artifact chain, not the input. Confirmed in code — `DISPATCH_CHAIN_TERMINAL_GRADUATION` maps `BUILD_ARTIFACTS -> CANDIDATE_REVIEW`, i.e. the chain graduates *into* it. AST-962 had wired that graduation target in as the trigger, so those rows claimed jobs that had already finished (the "ghost issues" on this ticket).

**Fix:** `_dispatch_trigger_state_for_task_key` now returns `BUILD_ARTIFACTS` for the whole artifact chain — reusing `JOB_ARTIFACT_ENTRY_TASK_KEYS` plus `draft_cover_letter` (excluded from that set because it runs a separate batch). Three branches collapse to one, so resume and cover-letter hops can no longer drift apart. Explicit operator overrides still honored; `CANDIDATE_REVIEW` remains a valid state to pick by hand.

**Data:** `scripts/migrations/retarget_artifact_chain_trigger_state.py` (dry-run by default, `--apply` to commit). Retargeted the four rows from the ticket — 11177/11201 `draft_cover_letter`, 11203/11204 `check_cover_letter`. All were `auto_mode=0` (CLICK), so no autonomous behavior changed. Zero `CANDIDATE_REVIEW` dispatch rows remain; re-run is a no-op. **Staging/prod still need `--apply`.**

## [qa-handoff] Betty — 4 tests encode the old semantics

Not touched per `astral.git.engineer-test-tree-ban`. All in `tests/component/utils/test_config.py`:

- `TestAst955RegisteredKeyDispatchAdminDefaults::test_check_cover_letter_without_override_defaults_candidate_review`
- `TestAst962CoverLetterMidHopDefaultTrigger::test_dispatch_trigger_state_defaults`
- `TestAst962CoverLetterMidHopDefaultTrigger::test_admin_defaults_without_override`
- `TestAst962CoverLetterMidHopDefaultTrigger::test_draft_cover_letter_and_grade_do_unchanged`

Each asserts the artifact-chain default is `CANDIDATE_REVIEW`; expected value is now `BUILD_ARTIFACTS`. The `grade_do` half of the last one is still correct. Override-based tests in `test_api_admin.py` pass unchanged.

**Separately:** this branch already had **10** pre-existing failures in `test_config.py` / `test_api_admin.py` before my change (gaze_email `freq_hrs`, seed-statute registration, prefilter grouping, resolve-tokens). Not from Track 3/4 — flagging so they aren't misattributed.

## Remaining

Track 2 grouping renumber (Topic Menu shares `2000` with Candidate Artifacts; Preamble still `"1"` on a 1000 scale; four `ZZZ`/(unassigned) rows) and Track 1 compliance.

#### chuckles — 2026-07-31T21:56:21.029Z
## Statute add: `astral.standards.names-not-ticket-ids`

Identifiers (functions/vars/constants/modules) use stable domain language — no Linear issue ids in the name. Carve-outs: comments, commits, feature docs, branches, Linear prose. `astral.seed.boot-only-not-hot-path` now points here instead of restating the rule.

## Track 3 needs a product call

AST-962 deliberately set cover-letter dispatch defaults (`draft_cover_letter` / `check_cover_letter` / …) to trigger `CANDIDATE_REVIEW`. This ticket says that is **not** a dispatch-ready input state. Resume hops already default to `BUILD_ARTIFACTS`.

Waiting on Archie: retarget defaults + the four live rows to `BUILD_ARTIFACTS`, or delete the four rows only?

#### chuckles — 2026-07-31T21:52:48.347Z
## Track 4 landed (hot-path vet prompt migrations)

**Symptom:** Manage Tasks showed permanent "Revert to file" on `agent_task` even when prompts matched the repo file.

**Root cause:** `_ensure_agent_task_schema` ran three sequential prompt seeds for `vet_inflow_discovery` (AST-776 → AST-822 → AST-880). Each is "idempotent" only if its marker appears in the current `user_prompt`. AST-880's seed did **not** include the 776/822 markers, so every new process re-ran all three, each call going through `_save_agent_task_on_connection` (new `task_key_uuid` + `updated_at`). Bootstrap order made it worse: `apply_repo_admin_json_at_startup()` then `ensure_all_upsert_registry_schemas_at_startup()` — file applied, then migrations immediately rewrote the row.

**Fix (this branch):**
- Retired the three migrations to no-ops; removed their calls from `_ensure_agent_task_schema`.
- Deleted the in-code seed string constants — authoritative prompt remains in `data/admin/agent_task.json`.
- Quoted Preamble `task_group_order` `1` → `"1"` in `agent_task.json` (+ AST-756 UAT fixture) so TEXT affinity no longer false-diverges (`1` vs `'1'`).

**After deploy / server restart:** one Revert to file (or clean bootstrap with repo-wins) clears leftover UUID drift from the thrash. Old running servers still load the old code until restarted.

**Still open on this ticket:** Track 1 compliance (incl. other `_apply_ast*` data writers on ensure), Track 2 full grouping renumber, Track 3 `CANDIDATE_REVIEW` dispatch rows.

---

_Implementation detail may live in git history on `origin/dev`._
