# AST-856 — check_cover_letter not recognized as a valid task_key
**Component:** artifacts  
**Children:** AST-955, AST-962  
**Linear archived:** AST-856 2026-08-02; AST-955 2026-08-02; AST-962 2026-08-02

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-07-22 16:42 | AST-955 | docs | `5bef45065` | docs(AST-955): plan — align Scheduled Actions Save with task_key picker |
| 2026-07-22 16:44 | AST-955 | code | `15248c1a6` | code(AST-955): save_dispatch_task passes trigger into defaults |
| 2026-07-22 16:44 | AST-955 | code | `9ee7d6ee4` | code(AST-955): registered-key dispatch_task_admin_defaults |
| 2026-07-22 16:45 | AST-955 | code | `0efa2bba3` | code(AST-955): Save accepts registered TASK_CONFIG task keys |
| 2026-07-22 16:45 | AST-955 | code | `e332ec652` | code(AST-955): append build review stub |
| 2026-07-22 16:49 | AST-955 | test | `a4b8fbbc5` | test(AST-955): Save accepts registered TASK_CONFIG keys (check_cover_letter) |
| 2026-07-22 16:50 | AST-955 | merge-tests | `5f87d190a` | merge-tests(AST-955): origin/tests a4b8fbbc5 |
| 2026-07-22 16:55 | AST-955 | docs | `264652777` | docs(AST-955): Radia review — clean |
| 2026-07-22 16:56 | AST-955 | resolve | `ae30f3969` | resolve(AST-955): — clean |
| 2026-07-22 16:57 | AST-955 | plan | `04619b168` | plan(AST-955): align Scheduled Actions Save with task_key picker |
| 2026-07-22 16:58 | AST-856 | prep-uat | `6ab3b7274` | prep-uat(AST-856): rebuild merge ticket log |
| 2026-07-22 20:32 | AST-955 | test | `8bfe40fe1` | test(AST-960): drop frozenset inventory coverage; TASK_CONFIG catalog only |
| 2026-07-23 11:15 | AST-962 | plan | `646345336` | plan(AST-962): UAT check_cover_letter Save still 400 (karfo) |
| 2026-07-23 11:16 | AST-962 | code | `b3b016a33` | code(AST-962): default cover-letter mid-hop trigger CANDIDATE_REVIEW |
| 2026-07-23 11:16 | AST-962 | code | `c3bf81602` | code(AST-962): append build review stub |
| 2026-07-23 11:19 | AST-962 | test | `d32e2a631` | test(AST-962): cover-letter mid-hop defaults to CANDIDATE_REVIEW |
| 2026-07-23 11:19 | AST-962 | merge-tests | `db8cfcdcb` | merge-tests(AST-962): origin/tests d32e2a631 |
| 2026-07-23 11:21 | AST-962 | docs | `028d7e96f` | docs(AST-962): Radia review — clean |
| 2026-07-23 11:22 | AST-962 | resolve | `7893cb11c` | resolve(AST-962): — clean |
| 2026-07-23 11:34 | AST-856 | prep-uat | `62cf9aba4` | prep-uat(AST-856): rebuild merge ticket log |
| 2026-08-02 09:37 | AST-856 | docs | `b07fa5a97` | docs(AST-856): archive Linear issue content |
| 2026-08-02 09:37 | AST-955 | docs | `91403b331` | docs(AST-955): archive Linear issue content |
| 2026-08-02 09:37 | AST-962 | docs | `575ae17b7` | docs(AST-962): archive Linear issue content |

_The `test(AST-960)` row above is reachable from the `AST-955` grep (its body names AST-955); AST-960 itself belongs to the AST-957 family._

## Epic — AST-856
_Archived: 2026-08-02 · Linear URL: https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Low / — · Blocked by / blocks / related: —_

### Purpose

Susan administers dispatch through Scheduled Actions as the sole admin user. Saving a row for `check_cover_letter` fails with HTTP 400 even though that key appears in the task_key picker — a second, narrower allowlist blocks save while the dropdown lists every registered task key. Misapplied dispatch config should surface on the first run of the task, not as a UI barrier at save time. This ticket removes that save-time gate so picker and Save accept the same registered task keys.

### Functional scope

* Scheduled Actions task_key picker continues to list every registered task key; no additional allowlist filtering on what appears in the dropdown.
* Creating or updating a Scheduled Action accepts any task_key that is a registered task key — Save must not reject keys solely because they sit outside a separate "schedulable" allowlist (Susan's repro: `check_cover_letter`).
* Form defaults (entity type, trigger state, grouping metadata) may still be derived from the task registry and existing agent-task rows; Save must not require membership in that separate allowlist.
* First-run / dispatch execution remains the correctness check: a bad trigger state or entity pairing fails when the row runs, not when Susan clicks Save.
* Susan's repro (`check_cover_letter` selected, Save returns *Unknown or non-schedulable task_key*) is fixed without manually curating a second allowlist for each new artifact hop.

### Boundaries

* Admin-only Scheduled Actions surface — no change to Manage Tasks Run Next authoring.
* Does not remove the task registry itself or change prompt / run-next content.
* Does not add ordered pipeline step lists or new chain choreography.
* May retain blocking of explicitly **retired** dispatch keys (dead runtime paths) — not the artifact-hop allowlist gap Susan hit.
* Does not change dispatcher claim logic, Execution History, or debug logging beyond what is required to honor saved rows.
* Code Rules §2.1 (config as single source of truth): Save acceptance for this admin surface must align with the same registered task catalog the picker already uses — dual catalogs for the same decision are out of scope to retain.

### Acceptance criteria

1. Susan can create a Scheduled Action dispatch row with `task_key=check_cover_letter` for candidate `somerset` without HTTP 400 — the error from the original brief no longer occurs.
2. Any other registered task key visible in the picker can be saved the same way (no *Unknown or non-schedulable task_key* for registered task keys).
3. Saving `check_job_resume` and `finalize_job_resume` continues to work unchanged.
4. A deliberately misconfigured row (wrong trigger state for the chosen task_key) is rejected or fails at **run** time, not at Save time — observable on first Run, not blocked at Save for merely being outside a separate schedulable allowlist.
5. Automated coverage asserts admin create acceptance for `check_cover_letter` and at least one regression case for an already-schedulable key.

### Dependencies and blockers

none.

### Open questions

none.

### Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Align Scheduled Actions Save with task_key picker | Admin create/update accepts every registered task key the picker already offers (except explicitly retired keys). Fixes Susan's `check_cover_letter` 400; leaves run-time validation as the place misconfigured trigger/entity pairings fail. Does not own Manage Tasks, chain choreography, or dispatcher claim changes. | Ada | — |

**Monolith check:** Functional scope has 5 capabilities; one child is intentional — one inseparable vertical slice (Save validation + admin create acceptance + regression coverage) must ship atomically for UAT.

_(An earlier decomposition comment proposed a single child titled "Remove Scheduled Actions save-time schedulable allowlist"; the approved table above is the one that shipped.)_

### Original brief

```
Astral error diagnostic
timestamp: 2026-07-10T16:08:04.219Z
message: Unknown or non-schedulable task_key: 'check_cover_letter'
route: /admin/scheduled_actions
astral_candidate_id: somerset
api_path: /api/admin/dispatch_tasks
http_method: POST
http_status: 400
response_body:
{
  "error": "Unknown or non-schedulable task_key: 'check_cover_letter'"
}
```

It was in the dropdown list.

#### Comments

##### susan — 2026-07-10T16:12:18.773Z
@chuckles Please let me know what determines the contents of the dropdown list on the UI, and whether it is definitively sourced by the TASK_CONFIG content, or if it is a one-off in config.py or otherwise.

Then confirm the source of truth used by the validation rules and confirm whether or not they are the same, and if not, where that source is determined. Do that in the discussion phase of this bug so that the devs can simply fix it.

##### chuckles — 2026-07-10T16:14:16.258Z
[check-linear]

**Scheduled Actions task_key dropdown** (`/admin/scheduled_actions` → Add/Edit form):

The picker is populated from **`GET /api/admin/dispatch_tasks/task_keys`**, which builds its key set in this order:

1. **Every key in `TASK_CONFIG`** via `get_task_keys()` (all entries in `config.py` `TASK_CONFIG` dict).
2. Plus any key in **`DISPATCH_SCHEDULABLE_TASK_KEYS`** not already in `TASK_CONFIG` (e.g. roster keys like `prefilter` that are not TASK_CONFIG entries).
3. Plus any **`task_key` already on an existing `dispatch_task` row** in the DB.
4. Minus **`admin_hidden_dispatch_task_keys()`** and **`DISPATCH_RETIRED_TASK_KEYS`**.

So the dropdown is **TASK_CONFIG-broad**, not limited to schedulable keys.

**Save validation is narrower:** **`POST /api/admin/dispatch_tasks`** accepts only keys in **`DISPATCH_SCHEDULABLE_TASK_KEYS`** (via `dispatch_task_admin_defaults`). That is why `check_cover_letter` appears in the picker (it is in `TASK_CONFIG`) but save returns *Unknown or non-schedulable task_key* (it is not yet in `DISPATCH_SCHEDULABLE_TASK_KEYS`).

**Not the same control as Manage Tasks → Run Next**, which uses a different admin surface (agent_task / save_agent_task validation).

**AST-856 fix scope:** add the missing BUILD_ARTIFACTS chain hops (`check_cover_letter`, `finalize_cover_letter`, `propose_application_responses`) to the schedulable set so picker and save align for those keys — not a one-off UI list.

##### susan — 2026-07-10T16:33:30.944Z
Why does `DISPATCH_SCHEDULABLE_TASK_KEYS` exist independently from TASK_CONFIG? @chuckles

##### chuckles — 2026-07-10T16:47:09.638Z
[check-linear]

**Why `DISPATCH_SCHEDULABLE_TASK_KEYS` is separate from `TASK_CONFIG`**

They serve different jobs:

- **`TASK_CONFIG`** — runtime task registry: every `task_key` `do_task` may run, with `response_schema`, entity metadata, graded/scored flags, etc. Includes hops that exist only for **Manage Tasks / `run_next` chaining** (registry-only artifact hops), candidate-prep tasks (`craft_resume_base`), and other keys Susan authors but never schedules as a standalone dispatch row.

- **`DISPATCH_SCHEDULABLE_TASK_KEYS`** — **Scheduled Actions allowlist only**: keys that may appear on a `dispatch_task` DB row. Membership means config can supply **`dispatch_task_admin_defaults`** for that key — `entity_type`, `trigger_state`, `sort_by`, `batch_call_mode` — so the dispatcher knows **what queue to claim** and **which task_key to run first**.

**Not every `TASK_CONFIG` key belongs on that allowlist.** Example: `anticipate_scan` is in `TASK_CONFIG` (chain hop) but deliberately **not** in `DISPATCH_SCHEDULABLE_TASK_KEYS` (AST-520) — Susan wires it via `run_next`, not as a default schedulable row. Conversely, **`prefilter`** is schedulable but its dispatch metadata comes from **`ROSTER_CONFIG`**, not a `TASK_CONFIG` entry — so it can be in the allowlist without being in `TASK_CONFIG`.

**This bug:** `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses` were registered in `TASK_CONFIG` (AST-450) and should be schedulable mid-chain hops like `check_job_resume`, but were **never added** to `DISPATCH_SCHEDULABLE_TASK_KEYS`. The dropdown lists all `TASK_CONFIG` keys; save checks the allowlist — hence the mismatch.

**Fix for devs (unchanged):** add those three keys to `DISPATCH_SCHEDULABLE_TASK_KEYS` with the same BUILD_ARTIFACTS dispatch defaults as sibling resume hops — not collapse the two registries into one.

##### susan — 2026-07-10T17:35:36.164Z
If that's the case, this is still wrong, because "finalize_job_resume" and "check_job_resume" were deemed "schedulable tasks". Please remove this excessive data validation to avoid stupid UI barriers where if the config is misapplied, it will be instantly seen in the first run of the task. THAT should be the scope of this ticket. Populate the dropdown with all the tasks in TASK_CONFIG, no precious filtering. The admin is the only user using this screen, and we don't need full belt-and-suspenders validation.

_(This reverses the "add the three keys to `DISPATCH_SCHEDULABLE_TASK_KEYS`" fix chuckles proposed above: the ticket now drops the save-time allowlist gate entirely rather than curating a second allowlist.)_

##### chuckles — 2026-07-12T00:07:26.425Z
[check-linear] Discussion — scope aligned (@susan)

You're right — save-time rejection via **`dispatch_task_admin_defaults`** / **`DISPATCH_SCHEDULABLE_TASK_KEYS`** is what this ticket removes. **`finalize_job_resume`** and **`check_job_resume`** are already allowlisted; keys like **`check_cover_letter`** should save without that gate.

**Agreed scope:** picker = all **`TASK_CONFIG`** keys; **POST/PUT** accept any **`TASK_CONFIG`** key; drop allowlist membership and excessive save-time validation; misconfig surfaces on first dispatch run.

Definition already matches — approve/move to **Todo** when ready and I'll dispatch.

##### susan — 2026-07-23T18:11:17.811Z
@chuckles This issue is still occuring.

```
Astral error diagnostic
timestamp: 2026-07-23T18:10:33.974Z
message: Unknown or non-schedulable task_key: 'check_cover_letter'
route: /admin/scheduled_actions
astral_candidate_id: karfo
api_path: /api/admin/dispatch_tasks
http_method: POST
http_status: 400
response_body:
{
  "error": "Unknown or non-schedulable task_key: 'check_cover_letter'"
}
```

_(UAT re-report on candidate `karfo` after the first ship — spawns child AST-962.)_

##### chuckles — 2026-07-23T18:34:20.125Z
[fix-uat] UAT fixes landed — ready for re-test

**AST-962** — _check_cover_letter Save still 400 (karfo)_
- **Issue reported:** On staging after the first ship, saving a Scheduled Action with `task_key=check_cover_letter` still returns HTTP 400.
- **Should now:** `POST /api/admin/dispatch_tasks` accepts `check_cover_letter` for any candidate (including `karfo`) without *Unknown or non-schedulable task_key* — same as any other registered task key visible in the picker. Misapplied trigger/entity should fail at first Run, not at Save.
- **Quick check (this fix only):**
  1. Open `/admin/scheduled_actions` for candidate `karfo` (or any candidate).
  2. Add/Save a dispatch row with `task_key=check_cover_letter` and a valid job trigger state from the form.
  3. Confirm HTTP 400 with `Unknown or non-schedulable task_key: 'check_cover_letter'` no longer occurs.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

_(Linear-state process pings — parent in Discussion not Todo, Description missing the `## Proposed child tickets` table, and a "regression still open" status ping — omitted.)_

### Files changed (plan vs actual)

_No product commit trail on the parent — the two `prep-uat(AST-856)` commits only rebuild the merge ticket log; implementation landed via the sub-issues below._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-955 — Align Scheduled Actions Save with task_key picker
_Archived: 2026-08-02 · Linear URL: https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-856_

#### What this implements

Admin create/update on Scheduled Actions accepts every registered task key the picker already offers (except explicitly retired keys). Fixes Susan's `check_cover_letter` 400; leaves run-time validation as the place misconfigured trigger/entity pairings fail. Does not own Manage Tasks, chain choreography, or dispatcher claim changes.

#### Acceptance criteria

1. Susan can create a Scheduled Action dispatch row with `task_key=check_cover_letter` for candidate `somerset` without HTTP 400 — the error from the original brief no longer occurs.
2. Any other registered task key visible in the picker can be saved the same way (no *Unknown or non-schedulable task_key* for registered task keys).
3. Saving `check_job_resume` and `finalize_job_resume` continues to work unchanged.
4. A deliberately misconfigured row (wrong trigger state for the chosen task_key) is rejected or fails at **run** time, not at Save time — observable on first Run, not blocked at Save for merely being outside a separate schedulable allowlist.
5. Automated coverage asserts admin create acceptance for `check_cover_letter` and at least one regression case for an already-schedulable key.

#### Boundaries

* Does not change Manage Tasks Run Next authoring.
* Does not remove the task registry or change prompt / run-next content.
* Does not add pipeline step lists or chain choreography.
* May still block explicitly retired dispatch keys.
* Does not change dispatcher claim logic or Execution History beyond honoring saved rows.

#### Notes for planning

* Align Save acceptance with the same registered task catalog the Scheduled Actions picker already uses (Code Rules §2.1 — single source of truth). Drop the separate save-time "schedulable" allowlist gate that rejected `check_cover_letter`.
* Form defaults may still derive from the task registry / existing agent-task rows.

#### Root cause (verified on this branch)

1. `GET /api/admin/dispatch_tasks/task_keys` builds the picker from `get_task_keys()` / `TASK_CONFIG` (`dispatch_task_keys` in `api_admin.py`).
2. `POST`/`PUT` Save calls `_dispatch_task_key_trigger_error`, which calls `dispatch_task_admin_defaults(tk)` and maps `KeyError` → `Unknown or non-schedulable task_key`.
3. `dispatch_task_admin_defaults` raises when `tk not in DISPATCH_SCHEDULABLE_TASK_KEYS`.
4. `check_cover_letter` is in `TASK_CONFIG` and `JOB_ARTIFACT_ENTRY_TASK_KEYS`, but **not** in `_RESUME_ARTIFACT_HOP_TASK_KEYS` / `DISPATCH_SCHEDULABLE_TASK_KEYS` (unlike `check_job_resume` / `finalize_job_resume`).
5. Even if the API helper were bypassed, `save_dispatch_task` also calls `dispatch_task_admin_defaults` and would raise `ValueError: … not schedulable`.

#### Stage 1: Config — registered-key admin defaults

**Done when:** `dispatch_task_admin_defaults("check_cover_letter", trigger_state="CANDIDATE_REVIEW")` returns `entity_type="job"`, that `trigger_state`, a non-empty `sort_by`, and `batch_call_mode` (0). `dispatch_task_admin_defaults("grade_do")` (no override) is unchanged vs today. `dispatch_task_admin_defaults("consult_do")` still raises via retired messaging. Calling `dispatch_task_admin_defaults("check_cover_letter")` with no override still raises `KeyError` (no invented default trigger — see Decision).

1. In `src/utils/config.py`, change `dispatch_task_admin_defaults` signature to:

```python
def dispatch_task_admin_defaults(
    task_key: str,
    trigger_state: Optional[str] = None,
) -> Dict[str, Any]:
```

2. Replace the body membership gate as follows (keep retired check first, order matters):
   - `tk = (task_key or "").strip()`
   - `retired = dispatch_task_key_retired_message(tk)`; if set → `raise KeyError(retired)` (unchanged)
   - If `tk not in TASK_CONFIG` → `raise KeyError(f"dispatch_task_admin_defaults: unknown task_key {tk!r}")`
   - **Delete** the `if tk not in DISPATCH_SCHEDULABLE_TASK_KEYS: raise KeyError(... not schedulable)` branch
   - `entity_type = _dispatch_entity_type_for_task_key(tk)` (already resolves `check_cover_letter` via `TASK_CONFIG["entity_type"]`)
   - Resolve effective trigger:
     - `override = (trigger_state or "").strip()`
     - If `override`: use it as `effective_ts`
     - Else: `effective_ts = _dispatch_trigger_state_for_task_key(tk)` (may KeyError — do not catch)
   - Return dict with `entity_type`, `trigger_state=effective_ts`, `sort_by=_dispatch_sort_by_for(entity_type, effective_ts)`, `batch_call_mode=_dispatch_batch_call_mode_for(tk)`
   - Update the docstring: defaults for any registered non-retired `TASK_CONFIG` key; optional `trigger_state` required when the key has no derived default trigger rule.

3. In `_dispatch_trigger_state_for_task_key`, **delete** only this gate (leave all explicit branches and the final `TASK_CONFIG` / `not_ready_state` fallthrough unchanged):

```python
if task_key not in DISPATCH_SCHEDULABLE_TASK_KEYS:
    raise KeyError(f"dispatch trigger_state: unknown task_key {task_key!r}")
```

After deletion, keys with `TASK_CONFIG[task_key]["trigger_state"] is None` and no explicit branch (e.g. `check_cover_letter`) still hit the final `raise KeyError(f"dispatch trigger_state: no rule for task_key {task_key!r}")` when called without an override — that is intentional.

⚠️ **Decision:** Do **not** add `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses` to `DISPATCH_SCHEDULABLE_TASK_KEYS`, and do **not** hardcode new per-key trigger branches for them. Parent + child forbid retaining a second curated allowlist for Save acceptance. Form / POST already supply Input State; defaults take that override for column derivation (`sort_by`).

⚠️ **Decision:** Leave `DISPATCH_SCHEDULABLE_TASK_KEYS` itself intact for bootstrap inventory and `_dispatch_task_key_form_meta` enrichment of schedulable keys. This ticket only stops using that frozenset as the Save membership gate.

#### Stage 2: Data layer — insert uses request trigger for defaults

**Done when:** `save_dispatch_task(..., task_key="check_cover_letter", trigger_state="CANDIDATE_REVIEW", ...)` no longer raises `ValueError: … not schedulable` solely because the key is outside `DISPATCH_SCHEDULABLE_TASK_KEYS`. Existing schedulable inserts (`grade_do`, `check_job_resume`, `finalize_job_resume`) still derive columns when `trigger_state` is omitted.

1. In `src/data/database.py` `save_dispatch_task`, replace the defaults call:

```python
try:
    defaults = dispatch_task_admin_defaults(task_key, trigger_state=trigger_state)
except KeyError as e:
    raise ValueError(f"dispatch_task task_key rejected: {task_key!r}") from e
```

(Keep the subsequent "fill entity_type / trigger_state from defaults when omitted" logic unchanged; with override passed, `defaults["trigger_state"]` matches the request when provided.)

2. Do **not** change `get_dispatch_row_or_seed_preview_meta` beyond what falls out of Stage 1 (still `dispatch_task_admin_defaults(task_key)` with no override; returns `None` on KeyError for keys without a derived trigger — acceptable for adhoc preview). Do **not** change schema backfill's `try/except KeyError: continue`.

#### Stage 3: Admin API — Save membership = registered catalog

**Done when:** `POST /api/admin/dispatch_tasks` with `task_key=check_cover_letter`, a valid job `trigger_state` (e.g. `CANDIDATE_REVIEW`), and required fields for candidate `somerset` returns **201** (not 400 with `Unknown or non-schedulable`). Same for `PUT` changing `task_key` to `check_cover_letter`. `check_job_resume` / `finalize_job_resume` still save. Retired keys still 400. Completely unknown strings still 400 with `Unknown task_key: …` (no "non-schedulable" wording).

1. In `src/ui/api/api_admin.py` `_dispatch_task_key_trigger_error`, replace the `try/except KeyError` around `dispatch_task_admin_defaults` with an explicit registered-key check. Concrete body:

```python
def _dispatch_task_key_trigger_error(task_key: str, trigger_state: str | None) -> str | None:
    tk = (task_key or "").strip()
    if not tk:
        return "task_key is required"
    retired = dispatch_task_key_retired_message(tk)
    if retired:
        return retired
    if tk not in TASK_CONFIG:
        return f"Unknown task_key: {tk!r}"
    ts = (trigger_state or "").strip()
    if not ts:
        return "trigger_state is required"
    try:
        et = _dispatch_entity_type_for_task_key(tk)
    except KeyError:
        return f"task_key {tk!r} has unsupported entity_type"
    if et not in ENTITY_TYPES:
        return f"task_key {tk!r} has unsupported entity_type {et!r}"
    try:
        registry = dispatch_entity_state_registry(et)
    except KeyError:
        return f"task_key {tk!r} has unsupported entity_type {et!r}"
    registry_ts = ts
    parsed_registry = parse_dispatch_hop_label(ts)
    if parsed_registry:
        registry_ts = parsed_registry[0]
    if registry_ts not in registry:
        return f"task_key {tk!r} ({et}) is not valid for trigger_state {ts!r}"
    if is_dispatch_chain_trigger(registry_ts):
        parsed = parse_dispatch_hop_label(ts)
        if parsed and parsed[1] != tk:
            return f"task_key {tk!r} does not match hop in trigger_state {ts!r}"
    return None
```

2. Import `_dispatch_entity_type_for_task_key` from `src.utils.config` in `api_admin.py` (add to the existing config import block). `TASK_CONFIG` is already imported.

3. In `update_dtask`, when `"task_key" in data`, change the defaults line to pass the effective trigger already computed for validation:

```python
defaults = dispatch_task_admin_defaults(
    (data["task_key"] or "").strip(),
    trigger_state=effective_trigger_state,
)
```

(`effective_trigger_state` is already `data.get("trigger_state", row.get("trigger_state"))` immediately above.)

4. Do **not** change `create_dtask` field list, retired pre-check, or UNIQUE 409 handling. Do **not** change `dispatch_task_keys` / `_dispatch_task_key_form_meta` (picker already lists registered keys).

⚠️ **Decision:** Keep trigger_state **registry** + hop-label matching at Save (existing behavior for `grade_do` + compound hops). Parent AC4's "not blocked at Save for merely being outside a separate schedulable allowlist" is satisfied by dropping the schedulable membership gate. Completely invalid state strings still 400; a valid registry state that claim/eligibility will not run for still surfaces on first Run — matching "misconfigured pairing fails at run." Do **not** remove registry checks in this ticket (would expand scope and churn Betty's existing helper tests without fixing Susan's repro).

#### Stage 4: Manual verification (engineer, before Code Complete)

**Done when:** Local or staging admin can Save `check_cover_letter` for `somerset` without the original 400 string; regression Saves for `check_job_resume` and `finalize_job_resume` still work.

1. After Stages 1–3 compile clean, exercise (or document for UAT) `POST /api/admin/dispatch_tasks` JSON shaped like:

```json
{
  "candidate_id": "somerset",
  "task_key": "check_cover_letter",
  "trigger_state": "CANDIDATE_REVIEW",
  "min_count": 1
}
```

Expect **201** and a new `dispatch_task` row. Confirm response body is not `{"error": "Unknown or non-schedulable task_key: 'check_cover_letter'"}`.

2. Confirm `POST` with `task_key=check_job_resume` and `task_key=finalize_job_resume` still **201** with their usual triggers.

3. Confirm `POST` with `task_key=consult_do` still **400** retired messaging.

**Betty note:** AC5 automated coverage lands via `qa-child` / `tests/` — do not edit `tests/` or `docs/test-bible/**` on this ticket.

#### Execution contract

- Execute stages in order; one commit per stage on the epic worktree sub-branch; publish to `origin/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker` after each stage per `build-child`.
- Do not add files outside the Files Changed table.
- If `dispatch_task_admin_defaults` call sites elsewhere break because of the new optional arg, only keyword-optional use is allowed — positional callers of `(task_key,)` must keep working.
- On ambiguity or codebase drift → stop, comment on parent AST-856 with the blocking template, wait.

#### Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.3 DRY | One membership notion for Save (`TASK_CONFIG`) shared with the picker source (`get_task_keys` / `TASK_CONFIG`); no new parallel allowlist |
| §2.1 config | Defaults and entity/trigger derivation stay in `config.py`; Save stops using a second frozenset as acceptance |
| §2.4 batch | Untouched |
| §2.6 state machine | No new states; registry validation on trigger_state retained |
| §3.3 imports | `api_admin` already imports config; add `_dispatch_entity_type_for_task_key` only |
| §3.5 naming | Keep `dispatch_task_admin_defaults` name; optional `trigger_state` is additive |

**Self-Assessment:** Single-Component — utils defaults + data insert + admin Save validation for one admin surface; no dispatcher/core/frontend. Conf high — root cause is a single membership gate (`DISPATCH_SCHEDULABLE_TASK_KEYS`) duplicated on API + `save_dispatch_task`; picker path already shows the correct catalog. Risk Medium — admin create/update is critical for Susan's ops; wrong defaults could write bad `sort_by`/`entity_type` for newly accepted keys, but existing schedulable keys keep the same derivation path when no override is needed.

##### Comments

###### ada — 2026-07-22T23:42:51.585Z
Plan: `origin/sub/AST-856/AST-955-…`. **Scope:** Single-Component — utils `dispatch_task_admin_defaults` + `save_dispatch_task` + admin `_dispatch_task_key_trigger_error` so Save accepts the same registered `TASK_CONFIG` catalog the picker already lists; retired keys still blocked; no dispatcher/frontend changes. **Conf:** high — verified `check_cover_letter` is in `TASK_CONFIG` / picker but outside `DISPATCH_SCHEDULABLE_TASK_KEYS`; Save maps that KeyError to the exact 400 Susan hit. **Risk:** Medium — admin create/update path.

###### betty — 2026-07-22T23:51:05.244Z
Coverage: `check_cover_letter` + `CANDIDATE_REVIEW` create 201; `check_job_resume` regression; unknown wording (`Unknown task_key`, not non-schedulable); DB insert + rejected wording; config defaults with optional trigger.

**Broken / obsolete revised this pass:**
- `TestAst549DispatchAdminDefaults::test_unknown_task_key_raises` — `anticipate_scan` is registered (hop-derived `BUILD_ARTIFACTS`); now asserts junk key + `unknown task_key`.
- `TestDispatchTasks::test_create_dispatch_task_paths` — fake `custom`/`WATCH` 400 before save; uses `grade_do`/`PASSED_JD`.

Publish: `origin/sub/AST-856/AST-955-…` @ `5f87d19` (`merge-tests(AST-955): origin/tests a4b8fbb`).

Bible shasum (publish tip):
- `docs/test-bible/ui/api/api_admin.md` `eafb1d5799becdbfb3fa48830b9f8916cfcc0804`
- `docs/test-bible/utils/config.md` `0f1253696e20dadbabc0f1a1b1c13e629026dd6e`
- `docs/test-bible/data/database/dispatch_tasks.md` `0337a6e35ab994d442182050bbc5682291947440`

###### radia — 2026-07-22T23:55:22.452Z
**Radia review — clean.** Diff: `origin/dev...origin/sub/AST-856/AST-955-…` @ `2646527`.

**Plan fidelity:** Stages 1–3 match. Save membership is registered `TASK_CONFIG` (not `DISPATCH_SCHEDULABLE_TASK_KEYS`); optional `trigger_state` flows through defaults on insert/update; schedulable frozenset left for bootstrap / form enrichment; dispatcher claim untouched.

**Rules:** §1.3 / §2.1 — one Save catalog shared with picker source. §3.3 — utils import only for this change. §2.4 / §2.6 / §5f / §5g N/A.

**fix-now / discuss:** none. **Verdict:** Clean — `resolve-child` may proceed.

#### Resolution (2026-07-22, resolve-child)

**Radia:** clean — fix-now / discuss none (`docs(AST-955): Radia review — clean` @ `2646527`). **Product:** no code changes this pass. Stages 1–3 from build remain the ship; Betty `merge-tests` @ `5f87d19` unchanged. **Outcome:** `resolve(AST-955): — clean` → **User Testing** (assignee Ada).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Extend `dispatch_task_admin_defaults` to registered `TASK_CONFIG` keys (optional `trigger_state`); drop schedulable-only gate in `_dispatch_trigger_state_for_task_key` | `9ee7d6ee4` |
| ✓ | `src/data/database.py` | `save_dispatch_task` passes request `trigger_state` into defaults; clarify KeyError → ValueError wording | `15248c1a6` |
| ✓ | `src/ui/api/api_admin.py` | `_dispatch_task_key_trigger_error` accepts any non-retired `TASK_CONFIG` key; `update_dtask` passes effective trigger into defaults | `0efa2bba3` |
| | _tests_ | AC5 create acceptance + already-schedulable regression | `a4b8fbbc5` — 3 test file(s) + test-bible (Betty) |

### AST-962 — UAT: check_cover_letter Save still 400 (karfo)
_Archived: 2026-08-02 · Linear URL: https://linear.app/astralcareermatch/issue/AST-962/uat-check-cover-letter-save-still-400-karfo · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-856 · UAT bug of AST-856 / first-ship child AST-955_

#### What failed

On staging after AST-955, saving a Scheduled Action with `task_key=check_cover_letter` still returned HTTP 400 `Unknown or non-schedulable task_key: 'check_cover_letter'` (candidate `karfo`, `2026-07-23T18:10:33Z`). Susan reported the original issue still occurring.

#### Expected

`POST /api/admin/dispatch_tasks` accepts `check_cover_letter` for any candidate (including `karfo`) without *Unknown or non-schedulable task_key* — same as any other registered task key visible in the picker. Misapplied trigger/entity should fail at first Run, not at Save for allowlist membership.

#### Repro

1. Open `/admin/scheduled_actions` for candidate `karfo` (or any candidate).
2. Add/Save a dispatch row with `task_key=check_cover_letter` and a valid job trigger state from the form.
3. Observe HTTP 400 with `Unknown or non-schedulable task_key: 'check_cover_letter'`.

#### Parent AC (quoted inline)

> 1. Susan can create a Scheduled Action dispatch row with `task_key=check_cover_letter` for candidate `somerset` without HTTP 400.
> 2. Any other registered task key visible in the picker can be saved the same way.
> 3. A deliberately misconfigured row is rejected or fails at **run** time, not at Save time.

#### Boundaries

* Does **not** change: Manage Tasks / run_next authoring, dispatcher claim logic, Execution History UX, or chain choreography.
* May still block explicitly retired dispatch keys.

#### Diagnosis (this branch tip)

1. `_dispatch_task_key_trigger_error` on tip returns `Unknown task_key` for unregistered keys — **not** `Unknown or non-schedulable` (AST-955). Grep of `origin/dev` `src/` finds **no** `non-schedulable` string.
2. `check_cover_letter` ∈ `TASK_CONFIG` with `entity_type=job`, `trigger_state=None`. `_dispatch_trigger_state_for_task_key("check_cover_letter")` raises `no rule for task_key`.
3. `_dispatch_task_key_form_meta` tries `dispatch_task_admin_defaults(task_key)` then `except KeyError: pass` — picker entry keeps empty `trigger_state`. Frontend Save POSTs `form.trigger_state` (often `""`) → API `trigger_state is required` **or** staging still running pre-AST-955 if deploy lagged (matches quoted diagnostic wording).
4. With explicit `trigger_state="CANDIDATE_REVIEW"`, tip defaults + membership already accept `check_cover_letter`.

⚠️ **Decision:** Do **not** treat this as "re-implement AST-955 membership." Membership is already fixed on tip. Close the UAT gap by giving cover-letter mid-chain keys the same default Input State as `draft_cover_letter` (`CANDIDATE_REVIEW`) so form meta + `save_dispatch_task` without override succeed. If staging still served the old **non-schedulable** string, Chuckles **prep-uat** after this child reaches User Testing refreshes Railway from `origin/dev`.

#### Stage 1: Default trigger for cover-letter mid-chain keys

**Done when:** `_dispatch_trigger_state_for_task_key("check_cover_letter") == "CANDIDATE_REVIEW"`; same for `finalize_cover_letter` and `propose_application_responses`. `dispatch_task_admin_defaults("check_cover_letter")` (no override) returns `entity_type=job`, `trigger_state=CANDIDATE_REVIEW`, non-empty `sort_by`, `batch_call_mode=0`. `draft_cover_letter` and `grade_do` defaults unchanged. `_dispatch_task_key_form_meta` / `GET …/task_keys` entry for `check_cover_letter` exposes non-empty `trigger_state` (via existing prefer-defaults path).

1. In `src/utils/config.py` `_dispatch_trigger_state_for_task_key`, immediately after the existing `draft_cover_letter` → `CANDIDATE_REVIEW` branch, add:

```python
if task_key in ("check_cover_letter", "finalize_cover_letter", "propose_application_responses"):
    return "CANDIDATE_REVIEW"
```

⚠️ **Decision:** Reuse `CANDIDATE_REVIEW` (same as `draft_cover_letter`) rather than `BUILD_ARTIFACTS` — cover-letter chain entry already schedules at candidate-review; mid-chain Save from Scheduled Actions should share that Input State. Do **not** add these keys to any schedulable frozenset (AST-960 deleted that inventory; AST-955 forbade dual allowlists).

2. Do **not** change `_dispatch_task_key_trigger_error`, `save_dispatch_task`, or frontend — form meta already prefers `dispatch_task_admin_defaults` when it resolves.

#### Stage 2: Tip smoke (engineer, before Code Complete)

**Done when:** Against this worktree tip, Save acceptance for `check_cover_letter` no longer depends on a hand-picked Input State, and the old diagnostic string cannot be produced by the API helper.

1. Confirm `rg -n 'non-schedulable' src/` is empty on the tip after Stage 1.
2. In a Python REPL with the project venv:

```python
from src.utils.config import dispatch_task_admin_defaults, _dispatch_trigger_state_for_task_key
assert _dispatch_trigger_state_for_task_key("check_cover_letter") == "CANDIDATE_REVIEW"
d = dispatch_task_admin_defaults("check_cover_letter")
assert d["entity_type"] == "job" and d["trigger_state"] == "CANDIDATE_REVIEW"
```

3. Optional Flask/admin smoke: `POST /api/admin/dispatch_tasks` with `candidate_id=karfo`, `task_key=check_cover_letter`, `trigger_state=CANDIDATE_REVIEW`, `min_count=1` → **201** (or 409 if row already exists — not 400 with non-schedulable / unknown).

**Betty note:** Extend AST-955 coverage for default-trigger-without-override on `check_cover_letter`; do not edit `tests/` here.

#### Execution contract

- Stages in order; one `code(AST-962):` commit per product stage on the epic sub-branch; push to `origin/sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo`.
- Plan commit subject must start with **`plan(AST-962):`** (validate-sub-log vocabulary).
- No files outside the Files Changed table.
- Ambiguity / drift → stop, comment on parent AST-856 with blocking template.

#### Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.3 DRY | Single helper branch next to existing `draft_cover_letter` rule — no parallel allowlist |
| §2.1 config | Trigger default lives in `config.py` |
| §2.4 / §2.6 | Untouched |
| §3.3 | Utils only |

**Self-Assessment:** Single-Component — one `_dispatch_trigger_state_for_task_key` branch in `config.py`. Conf Medium — tip already lacks the quoted error string (AST-955); UAT may partly be stale staging, but empty default trigger is a verified tip gap that blocks one-click Save. Risk low — only default Input State for three registered job keys; claim/run behavior unchanged; retired-key and unknown-key Save paths untouched.

##### Comments

###### ada — 2026-07-23T18:15:45.271Z
Plan. **Scope:** Single-Component — default `_dispatch_trigger_state_for_task_key` for `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses` → `CANDIDATE_REVIEW` so form meta + defaults resolve without override. AST-955 membership already on tip; quoted `non-schedulable` string absent from `origin/dev` `src/`. **Conf:** Medium. **Risk:** low.

###### betty — 2026-07-23T18:19:43.395Z
Coverage: mid-hop keys (`check_cover_letter` / `finalize_cover_letter` / `propose_application_responses`) default trigger + admin defaults without override; DB insert for `karfo` omits trigger and fills `CANDIDATE_REVIEW`; draft/grade_do regressions.

**Broken / obsolete revised this pass:** `TestAst955RegisteredKeyDispatchAdminDefaults::test_check_cover_letter_without_override_raises_no_rule` → now defaults to `CANDIDATE_REVIEW` (no KeyError).

Publish: `origin/sub/AST-856/AST-962-…` @ `db8cfcd` (`merge-tests(AST-962): origin/tests d32e2a6`).

Bible shasum (publish tip):
- `docs/test-bible/utils/config.md` `d2d70543b3b815a8eef4241ce75c55dde3bbf87d`
- `docs/test-bible/ui/api/api_admin.md` `c84ae63751efffe4551ec8ed77b4e2f74ee45aa9`
- `docs/test-bible/data/database/dispatch_tasks.md` `40b9c1f8e7cd36d0eeec2771113c94bc70b5d11d`

###### radia — 2026-07-23T18:21:21.613Z
**Radia review — clean.** Diff: `origin/dev...origin/sub/AST-856/AST-962-…` @ `028d7e9`.

**Plan fidelity:** Stage 1 exact — mid-chain cover-letter hops default to `CANDIDATE_REVIEW` beside `draft_cover_letter`. No Save membership rework; `non-schedulable` still absent from `src/`.

**Rules:** §1.3 / §2.1 — one config helper branch. §2.4 / §2.6 / §5f / §5g N/A.

**fix-now / discuss:** none. **Verdict:** Clean — `resolve-child` may proceed.

#### Resolution (2026-07-23, resolve-child)

**Radia:** clean — fix-now / discuss none (`docs(AST-962): Radia review — clean` @ `028d7e9`). **Product:** no code changes this pass. Stage 1 mid-hop `CANDIDATE_REVIEW` defaults from build remain the ship; Betty `merge-tests` @ `db8cfcd` unchanged. **Outcome:** `resolve(AST-962): — clean` → **User Testing** (assignee Ada).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Default trigger for cover-letter mid-chain keys in `_dispatch_trigger_state_for_task_key` | `b3b016a33` |
| | _tests_ | default-trigger-without-override on `check_cover_letter` + regressions | `d32e2a631` — 2 test file(s) + test-bible (Betty) |
