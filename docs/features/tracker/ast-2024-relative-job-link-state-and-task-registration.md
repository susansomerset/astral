# AST-2024 — RELATIVE_JOB_LINK state and task registration

- **Ticket:** [AST-2024](https://linear.app/astralcareermatch/issue/AST-2024)
- **Parent:** [AST-2022 — New Fetch task for RELATIVE_JOB_LINK](https://linear.app/astralcareermatch/issue/AST-2022)
- **Publish ref:** `sub/AST-2022/AST-2024-relative-job-link-state` (origin only)
- **Canon scope:** `astral.dispatch.entity-state-bound`, `patt.entity.batch-criteria`

Registry-only slice of AST-2022. Two new job states become legal: `RELATIVE_JOB_LINK` (where
qualify will park relative-link passes) and `RELATIVE_LINK_FAIL` (skipped, bulk-retryable back to
`RELATIVE_JOB_LINK`). `RELATIVE_JOB_LINK` becomes a legal prior of every state the click-through
runner can land a job in. The new fetch task key `fetch_relative_jd` gets its `GAZER_CONFIG`
block, its dispatch trigger-state / entity-type rules (`RELATIVE_JOB_LINK` / `job`), and an
`agent_task.json` catalog row so it shows in the Scheduled Actions picker. `qualify_job_listings`
gains a config key naming the relative-link destination. Jobs UI gets the processing and skipped
sections. **Nothing here routes qualify output, runs the fetch, or adds a dispatch router branch
— that is AST-2025.**

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `JOB_STATES` two new entries + six prior edits; `SKIPPED_STATES` / skipped order / labels / bulk-retry map; `JOBS_PROCESSING_UI_SECTIONS` row; `GAZER_CONFIG["fetch_relative_jd"]`; `TASK_CONFIG["qualify_job_listings"]["relative_link_state"]`; `_dispatch_trigger_state_for_task_key` + `_dispatch_entity_type_for_task_key` branches | utils |
| `data/admin/agent_task.json` | One new row (`fetch_relative_jd`, `telescope`, Job Review, `task_seq` 3.5) | data (seed) |

No other files. No tests, no bible, no `src/core/*`, no frontend (the Jobs UI reads
`build_state_ui_manifest()`; no TS state literals exist).

⚠️ **Decision — task key name `fetch_relative_jd`.** Neither the ticket nor the parent names the
key. `fetch_relative_jd` mirrors `fetch_jd` (same agent, same JD output, same Job Review group).
AST-2025's runner and dispatch-router branch must use this exact string. If Joan or Susan wants a
different name, it is a one-string change across both rows of this plan's Stage 2.

⚠️ **Decision — no score floor on `RELATIVE_JOB_LINK`.** The qualify key is named
`relative_link_state`, which `_task_config_transition_strings` (fixed keys `pass_state` /
`fail_state` / `error_state` / `not_ready_state` / `error_states`) does **not** read. So
`RELATIVE_JOB_LINK` is not in `_TRANSITION_STATES_USED_BY_SCORED_TASKS`,
`dispatch_claim_uses_score_floor("RELATIVE_JOB_LINK")` is `False`, and claim sort is
`updated_at`. Giving it a floor like `PASSED_JOBLIST` would mean editing
`_task_config_transition_strings`, a function-level change this ticket's Scope does not describe.

⚠️ **Decision — no `retry_state` on either new state.** The Scope doesn't ask for one.
`dispatch_claim_states("RELATIVE_JOB_LINK", "job")` already pairs the literal
`RELATIVE_JOB_LINK_RETRY` companion for claim purposes regardless of the registry.

## Notes for every stage

- **Compile + lint before every commit (Susan's rule).**
  - Compile: `python3 -m py_compile src/utils/config.py` — must exit 0.
  - Import (catches every module-level `assert` in config.py):
    `python3 -c "import src.utils.config"` — must exit 0.
  - Lint: `ruff check src/utils/config.py` — no new findings on lines this stage added.
    `ruff` is **not** installed in the epic worktree's environment today (nor `flake8` /
    `pyflakes`). If it still isn't available, **stop** and post the blocked comment on AST-2022
    naming the missing tool — do not skip lint and do not pick a different linter yourself.
  - JSON (Stage 2 only): `python3 -m json.tool data/admin/agent_task.json > /dev/null` — must
    exit 0.
- **`data/admin/agent_task.json` is in `.cursorignore`** — the editor tools can't open it. Edit it
  with a plain **text insertion** (e.g. a short `python3` script that splices lines, or `sed`
  line insert). **Never** `json.load` + `json.dump` the whole file — that rewrites every row's
  escaping/ordering and turns a one-row diff into a whole-file diff.
- **Do not touch** the `qualify_job_listings` row's prompts in `agent_task.json` (Susan edits
  that herself).
- Anchor every edit by the **content** quoted below, not by line number (line numbers drift).
- Tests are read-only for engineers. Relevant existing suites to run after Stage 2 (report
  results; don't edit): `python3 -m pytest tests/component -q -k "config or state_ui or dispatch"`.
  If collection fails on a missing third-party module (e.g. `asyncpg`), that is an environment
  gap — note it in the stage comment and continue.

---

## Stage 1: Job states, skipped wiring, UI sections

**Done when:** the ticket's AC 1 command exits 0, `python3 -c "import src.utils.config"` exits
0, and `build_state_ui_manifest()["jobs"]` lists `RELATIVE_JOB_LINK` in `processing_sections`
and `RELATIVE_LINK_FAIL` in `skipped.section_order` / `section_labels` /
`bulk_retry_to_state_by_from_state` (→ `RELATIVE_JOB_LINK`).

1. In `src/utils/config.py`, in the `JOB_STATES = {` dict, insert these two entries
   **immediately after** the `"INVALID_TITLE":` line and **before** the `"PASSED_JOBLIST":` line
   (aligned like their neighbours):

   ```python
       # AST-2022: relative-link qualify passes park here for the click-through fetch (fetch_relative_jd).
       "RELATIVE_JOB_LINK":      {"prior_states": ["NEW", "RELATIVE_LINK_FAIL"]},  # NEW_RETRY resolves through its base; RELATIVE_LINK_FAIL = Skipped bulk retry
       "RELATIVE_LINK_FAIL":     {"prior_states": ["RELATIVE_JOB_LINK"]},  # click target missing / Telescope error; job_link still relative
   ```

   Do **not** add `VALID_TITLE` to either list (AC 1 fails if you do).

2. In the same `JOB_STATES` dict, append `"RELATIVE_JOB_LINK"` as the **last** element of the
   `prior_states` list on each of these six lines (leave every other element and any trailing
   `retry_state` / comment untouched):
   - `"JD_READY":` → `["PASSED_JOBLIST", "FAILED_JD", "ERROR_EVALUATE_JD", "RELATIVE_JOB_LINK"]`
   - `"JD_SCRAPE_FAIL":` → `["PASSED_JOBLIST", "RELATIVE_JOB_LINK"]`
   - `"JD_SCRAPE_FAIL_COOKIE":` → `["PASSED_JOBLIST", "RELATIVE_JOB_LINK"]`
   - `"BOT_BLOCKED":` → `["PASSED_JOBLIST", "METEORITE_NEW", "RELATIVE_JOB_LINK"]`
   - `"JD_SCRAPE_FAIL_MISSING":` → `["PASSED_JOBLIST", "RELATIVE_JOB_LINK"]`
   - `"JD_SCRAPE_FAIL_CLOSED":` → `["PASSED_JOBLIST", "RELATIVE_JOB_LINK"]`

   ⚠️ **Decision:** `PASSED_JOBLIST`'s own prior list is **not** changed — the runner sends
   successful jobs straight to `JD_READY` (parent Pipeline flow), never to `PASSED_JOBLIST`.

3. In `SKIPPED_STATES = [`, change the line
   `"JD_SCRAPE_FAIL_COOKIE", "BOT_BLOCKED", "JD_SCRAPE_FAIL_MISSING", "JD_SCRAPE_FAIL_CLOSED",`
   to
   `"JD_SCRAPE_FAIL_COOKIE", "BOT_BLOCKED", "JD_SCRAPE_FAIL_MISSING", "JD_SCRAPE_FAIL_CLOSED", "RELATIVE_LINK_FAIL",`.

   (`JOB_STATES["CANDIDATE_SKIPPED"]["prior_states"]` is derived right after and will
   automatically include `RELATIVE_JOB_LINK` and exclude `RELATIVE_LINK_FAIL` — no edit.)

4. In `JOBS_PROCESSING_UI_SECTIONS = [`, insert immediately after
   `{"state": "PASSED_JOBLIST", "label": "Passed Job List"},`:

   ```python
       {"state": "RELATIVE_JOB_LINK", "label": "Relative Job Link"},
   ```

5. In `JOBS_SKIPPED_SECTION_ORDER = [`, insert `"RELATIVE_LINK_FAIL",` on its own line
   immediately after the `"JD_SCRAPE_FAIL_CLOSED",` line (before `"ERROR_QUALIFY_JOB_LISTINGS",`).

6. In `JOBS_SKIPPED_SECTION_LABELS = {`, add as the last entry (after
   `"METEORITE_FAILED_TECHNICAL_LIKE": "Meteorite Failed Technical LIKE",`):

   ```python
       "RELATIVE_LINK_FAIL": "Relative Link Fail",
   ```

7. In `JOBS_SKIPPED_BULK_RETRY_TO_STATE = {`, insert immediately after
   `"JD_SCRAPE_FAIL_CLOSED": "PASSED_JOBLIST",`:

   ```python
       "RELATIVE_LINK_FAIL": "RELATIVE_JOB_LINK",  # AST-2022: back to the click-through fetch
   ```

   The existing asserts below the map (`set(JOBS_SKIPPED_BULK_RETRY_TO_STATE) ==
   set(_skipped_retryable)`, keys/values in `JOB_STATES`) now cover the new pair — no new asserts.

8. Verify, in order (each must exit 0):
   - `python3 -m py_compile src/utils/config.py`
   - `python3 -c "import src.utils.config"`
   - The ticket's AC 1 command, verbatim:
     ```
     python -c "from src.utils.config import JOB_STATES as J, SKIPPED_STATES as S, JOBS_SKIPPED_BULK_RETRY_TO_STATE as R; assert set(J['RELATIVE_JOB_LINK']['prior_states'])=={'NEW','RELATIVE_LINK_FAIL'}; assert J['RELATIVE_LINK_FAIL']['prior_states']==['RELATIVE_JOB_LINK']; assert 'RELATIVE_LINK_FAIL' in S and R['RELATIVE_LINK_FAIL']=='RELATIVE_JOB_LINK'; assert all('RELATIVE_JOB_LINK' in J[s]['prior_states'] for s in ('JD_READY','BOT_BLOCKED','JD_SCRAPE_FAIL','JD_SCRAPE_FAIL_COOKIE','JD_SCRAPE_FAIL_MISSING','JD_SCRAPE_FAIL_CLOSED'))"
     ```
   - Manifest check:
     ```
     python3 -c "from src.utils.config import build_state_ui_manifest as B; j=B()['jobs']; assert {'state':'RELATIVE_JOB_LINK','label':'Relative Job Link'} in j['processing_sections']; s=j['skipped']; assert 'RELATIVE_LINK_FAIL' in s['section_order'] and s['section_labels']['RELATIVE_LINK_FAIL']=='Relative Link Fail' and s['bulk_retry_to_state_by_from_state']['RELATIVE_LINK_FAIL']=='RELATIVE_JOB_LINK'"
     ```
   - Lint per Notes.

9. Commit: `code(AST-2024): RELATIVE_JOB_LINK / RELATIVE_LINK_FAIL job states, skipped + processing UI`.
   Publish per build-child.

---

## Stage 2: Fetch task registration (config + dispatch rules + catalog row)

**Done when:** `_dispatch_trigger_state_for_task_key("fetch_relative_jd") == "RELATIVE_JOB_LINK"`,
`_dispatch_entity_type_for_task_key("fetch_relative_jd") == "job"`,
`TASK_CONFIG["qualify_job_listings"]["relative_link_state"] == "RELATIVE_JOB_LINK"`, and
`data/admin/agent_task.json` holds exactly one `fetch_relative_jd` row in Job Review at
`task_seq` 3.5 — so after bootstrap, `GET /api/admin/dispatch_tasks/task_keys` lists
`fetch_relative_jd` with `entity_type: "job"`, `trigger_state: "RELATIVE_JOB_LINK"`.

1. In `src/utils/config.py`, in `GAZER_CONFIG = {`, insert this block **immediately after** the
   closing `},` of the `"fetch_jd": {` block (before `"fetch_culture_pages": {`):

   ```python
       # AST-2022: click-through fetch for relative-link jobs (runner is AST-2025).
       # Click reached a page → same JD gates/outcomes as fetch_jd; click failed → fail_state.
       "fetch_relative_jd": {
           "fallback_batch_size": 10,   # config default only; dispatch_task.batch_size wins
           "trigger_state": "RELATIVE_JOB_LINK",
           "pass_state": "JD_READY",
           "fail_state": "RELATIVE_LINK_FAIL",
           "error_states": [
               "JD_SCRAPE_FAIL",
               "JD_SCRAPE_FAIL_COOKIE",
               "BOT_BLOCKED",
               "JD_SCRAPE_FAIL_MISSING",
               "JD_SCRAPE_FAIL_CLOSED",
           ],
       },
   ```

   ⚠️ **Decision:** `fail_state` is the click-target / Telescope-error destination
   (`RELATIVE_LINK_FAIL`). `JD_SCRAPE_FAIL` (empty / too-short text after a successful click)
   goes in `error_states` alongside the four classified states, because for this task every JD
   gate outcome happens **after** the link was resolved. That differs from `fetch_jd`, where
   `JD_SCRAPE_FAIL` is the `fail_state`. `patt.entity.batch-criteria`: `fallback_batch_size`
   is the only size here and is labelled as a fallback; no sort / floor / freq literals.

2. In `TASK_CONFIG["qualify_job_listings"]` (the block opening `"qualify_job_listings": {`
   under `# RUNTIME JOB VETTING PROMPTS - Ruth 1`), insert immediately after the line
   `"pass_state": "PASSED_JOBLIST",`:

   ```python
           # AST-2022: pass + non-empty, non-http(s) job_link → here instead of InvalidJobLinkError (routing is AST-2025).
           "relative_link_state": "RELATIVE_JOB_LINK",
   ```

   Do not rename it to any `*_state` key read by `_task_config_transition_strings` (see the
   no-score-floor Decision at the top).

3. In `_dispatch_trigger_state_for_task_key`, insert immediately after
   ```python
       if task_key == "fetch_jd":
           return "PASSED_JOBLIST"
   ```
   this branch:
   ```python
       if task_key == "fetch_relative_jd":
           return GAZER_CONFIG["fetch_relative_jd"]["trigger_state"]
   ```

4. In `_dispatch_entity_type_for_task_key`, change the tuple line
   `"fetch_jd", "fetch_culture_pages", "qualify_job_listings", "qualify_meteorite", "evaluate_jd",`
   to
   `"fetch_jd", "fetch_relative_jd", "fetch_culture_pages", "qualify_job_listings", "qualify_meteorite", "evaluate_jd",`.

   `astral.dispatch.entity-state-bound`: the pair is now `job` (a real `ENTITY_TYPES` member) /
   `RELATIVE_JOB_LINK` (a real `JOB_STATES` key from Stage 1), and AST-2025's runner must claim
   by exactly that pair. `fetch_relative_jd` is **not** added to `TASK_CONFIG` (same as
   `fetch_jd`), so the catalog defaults come only from these two helpers — no caller override path.

5. In `data/admin/agent_task.json`, insert the following text **immediately after** the `  },`
   line that closes the object whose `"task_key": "fetch_jd"` (i.e. between the `fetch_jd` row
   and the `fetch_culture_pages` row). Indentation is two spaces per level, keys in the same
   alphabetical order as every other row:

   ```json
     {
       "agent_id": "telescope",
       "cache_prompt": "",
       "cache_prompt_b": "",
       "cache_prompt_c": "",
       "cache_prompt_d": "",
       "current": 1,
       "nocache_prompt": "",
       "run_next": "",
       "system_prompt": "",
       "task_group_name": "Job Review",
       "task_group_order": "4000",
       "task_key": "fetch_relative_jd",
       "task_key_uuid": "f84f7468-ffb7-41b0-b28a-f21d4cf5e24e",
       "task_name": "fetch_relative_jd",
       "task_seq": 3.5,
       "updated_at": "2026-10-08 00:00:00",
       "user_prompt": ""
     },
   ```

   ⚠️ **Decision:** `task_seq` 3.5 — Job Review already uses every integer 1–9
   (`fetch_jd` = 3, `evaluate_jd` = 4); the DB column is `task_seq REAL` and the loader reads it
   with `float(...)`, so 3.5 sorts it right after `fetch_jd` without renumbering anyone else's
   row. The UUID above is fixed by this plan — use it verbatim.

6. Verify, in order (each must exit 0):
   - `python3 -m py_compile src/utils/config.py`
   - `python3 -c "import src.utils.config"`
   - `python3 -m json.tool data/admin/agent_task.json > /dev/null`
   - Registration check:
     ```
     python3 -c "from src.utils.config import _dispatch_trigger_state_for_task_key as T, _dispatch_entity_type_for_task_key as E, _dispatch_sort_by_for as SB, dispatch_claim_uses_score_floor as F, TASK_CONFIG as TC, GAZER_CONFIG as G, JOB_STATES as J; assert T('fetch_relative_jd')=='RELATIVE_JOB_LINK'; assert E('fetch_relative_jd')=='job'; assert SB('job','RELATIVE_JOB_LINK')=='updated_at'; assert F('RELATIVE_JOB_LINK') is False; assert TC['qualify_job_listings']['relative_link_state']=='RELATIVE_JOB_LINK'; c=G['fetch_relative_jd']; assert all(s in J for s in [c['trigger_state'],c['pass_state'],c['fail_state'],*c['error_states']])"
     ```
   - Catalog check:
     ```
     python3 -c "import json; r=[x for x in json.load(open('data/admin/agent_task.json')) if x['task_key']=='fetch_relative_jd']; assert len(r)==1 and r[0]['agent_id']=='telescope' and r[0]['task_group_name']=='Job Review' and r[0]['task_seq']==3.5 and r[0]['current']==1"
     ```
   - `git diff --stat data/admin/agent_task.json` shows **only** insertions (18 lines), zero
     deletions. If it shows deletions or a large diff, the file was re-serialized — revert it and
     redo step 5 as a text insertion.
   - Lint per Notes; run the component suites listed in Notes and record the result.

7. Commit: `code(AST-2024): fetch_relative_jd — GAZER_CONFIG, dispatch job/RELATIVE_JOB_LINK, qualify relative_link_state, agent_task row`.
   Publish per build-child.

---

## Acceptance trace

| Ticket AC | Covered by |
|-----------|-----------|
| 1. Registry command exits 0 | Stage 1 steps 1–3, 7; verified Stage 1 step 8 |
| 2. UI processing / skipped sections + bulk retry → `RELATIVE_JOB_LINK` | Stage 1 steps 4–7 (manifest-driven Jobs UI); manifest check Stage 1 step 8. Visible-with-jobs check is UAT once AST-2025 produces such jobs. |
| "New task key shows in Scheduled Actions as `job` / `RELATIVE_JOB_LINK`" | Stage 2 steps 3–5; picker meta = `_dispatch_*_for_task_key` helpers over agent_task membership |

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2024
**Overall:** APPROVED
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Publish ref:** `sub/AST-2022/AST-2024-relative-job-link-state` @ `201426ea0`

## Canon scores

astral.dispatch.entity-state-bound | A | | `fetch_relative_jd` → `job` / `RELATIVE_JOB_LINK` via `_dispatch_*` + real `JOB_STATES` keys; mirrors `fetch_jd`; no TASK_CONFIG override path
patt.entity.batch-criteria | A | | `fallback_batch_size` only in `GAZER_CONFIG`, labeled fallback; Stage 2 asserts `updated_at` sort and no score floor on `RELATIVE_JOB_LINK`

## Traceability

AC1 → Stage 1 (registry + skipped map + prior edits, AC1 command); AC2 → Stage 1 steps 4–7 + manifest check; “Scheduled Actions `job` / `RELATIVE_JOB_LINK`” → Stage 2 (`_dispatch_*`, `agent_task.json` row); parent AC3–8 N/A (AST-2024 Boundaries).

### discuss — Linear assignee at fetch time

- **Location:** `linear_proxy get-issue` (Plan Ready, assignee Ada Lovelace).
- **Finding:** validate-plan §1 expects Joan assigned for the gate; spawn still requested review.
- **Recommendation:** Chuckles assign Joan for the pass, then restore Ada after upshot (workflow only; plan substance unaffected).

### discuss — Task key `fetch_relative_jd`

- **Location:** Plan ⚠️ Decision — task key name.
- **Finding:** Parent/child Scope never literalizes the key; plan fixes `fetch_relative_jd` and binds AST-2025 to the same string.
- **Recommendation:** Susan/Archie confirm the name once; if changed, one-string sweep per plan note. Not a plan defect if name is accepted.

### acceptable — No `## Self-assessment` block

- **Location:** Plan structure (Estimate confirm only).
- **Finding:** R6 self-assessment checklist has nothing to grade; two-stage registry work is explicit in stages and verify commands.
- **Recommendation:** Optional self-assessment for build/review parity; not blocking.

### acceptable — Parent AC7 “manual run claims…” deferred

- **Location:** Boundaries vs parent epic AC7.
- **Finding:** Claim/process/release behavior is AST-2025 runner scope; this child only registers states, UI manifest inputs, dispatch defaults, and catalog row — consistent with child partition.
- **Recommendation:** None for AST-2024.

**R6 (summary):** Definition fidelity for parent child #2 (registry + task registration + UI labels + picker meta). Files/stages match Scope (`config.py`, `agent_task.json` only). `fail_state` / `error_states` split for click-through documented and aligned with pipeline. `agent_task.json` splice discipline matches seed-edit hazards. No `fix-now` findings.

context_tokens≈52000

`[plan-rubric] PROCEED (Commit: 201426ea0) registry and dispatch registration`

## Review

- **Branch:** `sub/AST-2022/AST-2024-relative-job-link-state`
- **Stage 1:** `bc027c9` — `RELATIVE_JOB_LINK` / `RELATIVE_LINK_FAIL` job states, six prior edits, skipped list / order / label / bulk retry, processing UI row
- **Stage 2:** `625c5a9` — `GAZER_CONFIG["fetch_relative_jd"]`, dispatch `job` / `RELATIVE_JOB_LINK` branches, `qualify_job_listings.relative_link_state`, `agent_task.json` row
- **Build notes:** lint unblocked by [AST-2027](https://linear.app/astralcareermatch/issue/AST-2027) (ruff approved); ruff reports no new findings vs. the pre-change file.
  `agent_task.json` diff is 19 insertions / 0 deletions (plan said 18 — miscount; the row is 17 keys + 2 braces).
  `pytest tests/component -k "config or state_ui or dispatch"`: 129 failures/collection errors also fail on the pre-AST-2024 tree (test tree ahead of / behind product imports). Two new failures, both tests pinning the old registry that this ticket's AC changes by design:
  `test_config.py::TestAst1195SchemaNullsAndBotBlocked::test_bot_blocked_registry_and_skipped_ui` (exact `BOT_BLOCKED` priors list) and
  `test_config.py::TestAst1808RetryRegistryPurge::test_prior_snapshot_pinned` (frozen `JOB_STATES` name snapshot). Left for Betty.

## Radia review

[code-rubric]
**Ticket:** AST-2024
**Publish ref:** `52c2d084c94049b92f1877ef1057543657acffd5` (`origin/sub/AST-2022/AST-2024-relative-job-link-state`)
**Corpus:** `2344ae3265b15125a8f4a655946fcfe66b3e1def`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.dispatch.entity-state-bound | A | | |
| patt.entity.batch-criteria | A | | |

## Column diff vs plan stage

(aligned) — Joan graded A/A; code matches her plan-stage rationale (`fetch_relative_jd` → `job` / `RELATIVE_JOB_LINK`, real `JOB_STATES` keys, `fallback_batch_size` only in `GAZER_CONFIG`, `updated_at` sort and no score floor on `RELATIVE_JOB_LINK`).

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Task key `fetch_relative_jd`**
  - **Location:** `data/admin/agent_task.json`, `GAZER_CONFIG`, `_dispatch_*_for_task_key` branches.
  - **Question (@susan):** Confirm the task key string is final for AST-2025 runner binding and Scheduled Actions labeling (parent/child Linear scope never literalized the name; plan fixed `fetch_relative_jd`).
  - **Default:** Keep `fetch_relative_jd` as landed; AST-2025 implements against that key without rename.

### advisory

- **Sibling stack on publish ref:** Three-dot diff vs `origin/dev` also includes AST-2023 product/docs/tests (`service/telescope/*`, `src/external/telescope.py`, `ast-2023` plan doc, telescope tests/bible). AST-2024 **product** commits on this ref are only `bc027c979` + `625c5a9c4` (`config.py`, `agent_task.json`). Expected epic sub stacking before `merge-child`; not AST-2024 scope creep in those commits.
- **Sibling test carry (non–AST-2024 nodes):** `tests/component/core/test_agent.py`, `test_consult.py`, `test_timesheets.py`, `test_openrouter.py`, `test_config.py` (`TestAst903CraftRubricMaxTokens`, `TestAst1955` resolver trim), plus core/agent OpenRouter paths — same merge-tests pattern as sibling subs.
- **AC2 visible UI:** Config/manifest wiring is covered by `TestAst2024RelativeJobLinkRegistry`; jobs actually appearing in processing/skipped UI with bulk retry is UAT once AST-2025 produces rows (per plan traceability).

## What’s solid

- **AC1 (verified on worktree):** Registry one-liner and plan registration check both exit 0 — priors, `SKIPPED_STATES`, bulk retry map, six JD-outcome priors, no `VALID_TITLE` on new states.
- **Registry + UI config:** `RELATIVE_JOB_LINK` / `RELATIVE_LINK_FAIL`; skipped order/label/bulk retry → `RELATIVE_JOB_LINK`; processing section between `PASSED_JOBLIST` and `JD_READY`.
- **Dispatch + gazer:** `GAZER_CONFIG["fetch_relative_jd"]` with `trigger_state` / pass / fail / `error_states` aligned to `fetch_jd` JD outcomes; `qualify_job_listings.relative_link_state`; `_dispatch_trigger_state_for_task_key` / `_dispatch_entity_type_for_task_key` mirror `fetch_jd` pattern.
- **Catalog:** `agent_task.json` splice — 19 insertions, 0 deletions; telescope / Job Review / `task_seq` 3.5 / fixed UUID; `TestAst2024FetchRelativeJdCatalogRow` + registry tests document AC intent.
- **Canon:** `RELATIVE_JOB_LINK` not score-gated (`dispatch_claim_uses_score_floor` false); job claim sort `updated_at` via existing `_dispatch_sort_by_for` branch for non–score-gated job states.

## Recommended actions (Chuckles / downstream — not Radia)

1. Append this artifact to `docs/features/tracker/ast-2024-relative-job-link-state-and-task-registration.md`, commit `docs(AST-2024): Radia review — clean`, push `sub/AST-2022/AST-2024-relative-job-link-state`, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED** → **User Testing** (no `resolve-child` canon work expected).
2. If Susan answers the task-key discuss before UT, note in the issue doc; otherwise `resolve-child` follows **Default** above.

Slim upshot: `[code-rubric] PROCEED (Commit: 52c2d08) registry and dispatch registration`

## Resolution

Resolved 2026-10-08 against Radia review `dcaf90af7` (CLEAN / PROCEED). No product changes.

- **fix-now:** none.
- **discuss — task key `fetch_relative_jd`:** Susan had not answered by resolve time, so Radia's **Default** applies: keep `fetch_relative_jd` as landed; AST-2025 binds its runner and dispatch-router branch to that exact string. To reverse: rename the key in `GAZER_CONFIG`, `_dispatch_trigger_state_for_task_key`, `_dispatch_entity_type_for_task_key`, and the `agent_task.json` row (`task_key` + `task_name`), plus Betty's `TestAst2024*` tests — before AST-2025 lands.
- **advisory:** sibling stacking on the publish ref and sibling test carry are expected before `merge-child`; AC2 visible-UI check is UAT once AST-2025 produces rows. No action.
