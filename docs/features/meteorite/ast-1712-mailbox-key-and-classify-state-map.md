<!-- linear-archive: AST-1712 archived 2026-09-24 -->

## Linear archive (AST-1712)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1711 — Rework meteorite_email  
**Blocked by / blocks / related:** parent: AST-1711; blocks: AST-1713

### Description

## What this implements

The mailbox task key and the meteorite state registry: `SCRAPE_LINK`, `READY`, `NOT_A_JOB`, `NEW_EMAIL_ERROR`, and scrape-failure `SCRAPE_ERROR` in place of `ERROR`. Existing `src/core/meteorite.py` failure writes of `ERROR` become `SCRAPE_ERROR` so that rename is legal. Does not create `NEW_EMAIL_ERROR` or `NOT_A_JOB` rows, send blobs to Ruth, or walk the inbox.

## Citations

`patt.task.dispatch-retry` — scrape failure keeps the ordinary claim retry under `SCRAPE_ERROR`; `NOT_A_JOB` and `NEW_EMAIL_ERROR` are not that retry.

## Scope

* `src/utils/config.py` — modified — mailbox task key becomes `stage_email_meteorite`, and the meteorite state registry maps outcomes to `SCRAPE_LINK`, `READY`, `NOT_A_JOB`, and `NEW_EMAIL_ERROR`, and renames scrape-failure `ERROR` to `SCRAPE_ERROR`.
* `data/admin/agent_task.json` — modified — mailbox shell row's task key follows that rename.
* `src/core/agent.py` — modified — legacy mailbox prompt fold follows the renamed task key.
* `src/core/meteorite.py` — modified — existing failure writes `state="ERROR"` become `SCRAPE_ERROR`, including the scrape fallback default. Does not add `NEW_EMAIL_ERROR` or `NOT_A_JOB` writes.
* `src/utils/config.py`: modified mailbox config — the task key string `meteorite_email` becomes `stage_email_meteorite`, and the debug runner points at `inbox.check_email`; modified meteorite state registry — link outcomes save as `SCRAPE_LINK`, no-scrape outcomes save as `READY`, not-a-job saves as `NOT_A_JOB` (insert-legal, listed for scheduled cleanup, not a dispatch trigger, not on the stale list), and other stage failures save as `NEW_EMAIL_ERROR` (insert-legal, not a dispatch trigger, and `NEW` lists it as a prior so a human can reset), and the scrape-failure state `ERROR` is renamed to `SCRAPE_ERROR` in that registry, its prior states, the scrape page-status map, and the stale list.
* `data/admin/agent_task.json`: modified mailbox shell row — `task_key` and `task_name` become `stage_email_meteorite`; Ruth's `stage_meteorite` row stays.
* `src/core/agent.py`: modified prompt lookup — the legacy mailbox fold keys off `stage_email_meteorite` instead of `meteorite_email`.
* `src/core/meteorite.py`: modified stage, scrape, and land failure writes — the meteorite state literal `ERROR` becomes `SCRAPE_ERROR`; the scrape fallback `status_map.get(page_status, "ERROR")` default becomes `"SCRAPE_ERROR"`. Log lines that say `This row is ERROR` stay. Do not add `NEW_EMAIL_ERROR` or `NOT_A_JOB` writes.

## Acceptance criteria

1. `rg -n "['\"]meteorite_email['\"]" src/utils/config.py data/admin/agent_task.json src/core/agent.py src/core/dispatcher.py src/ui/api/api_admin.py src/core/inbox.py` prints nothing. Fail: any of those files still contains the quoted task key `meteorite_email`. `rg -n "stage_email_meteorite" src/utils/config.py` shows that string as the mailbox task key. Fail: the mailbox task key is not `stage_email_meteorite`.
2. `rg -n '"SCRAPE_ERROR"' src/utils/config.py src/core/meteorite.py`, `rg -n '"NEW_EMAIL_ERROR"' src/utils/config.py src/core/meteorite.py`, and `rg -n '"NOT_A_JOB"' src/utils/config.py src/core/meteorite.py` all print matches. `rg -n "trigger_state = 'NEW_EMAIL_ERROR'" src/utils/config.py` and `rg -n "trigger_state = 'NOT_A_JOB'" src/utils/config.py` print nothing. In `METEORITE_STATES`, `NEW`'s `prior_states` includes `NEW_EMAIL_ERROR`, `stale_list_states` includes `SCRAPE_ERROR` and does not include `NEW_EMAIL_ERROR` or `NOT_A_JOB`, and the scheduled-cleanup selection includes `NOT_A_JOB`. Fail: any of those states is missing, a dispatch task claims `NEW_EMAIL_ERROR` or `NOT_A_JOB`, `NEW` cannot follow `NEW_EMAIL_ERROR`, or `NOT_A_JOB` is on the stale list or missing from cleanup.
3. `rg -n 'state="ERROR"' src/core/meteorite.py` prints nothing, and `rg -n 'status_map.get(page_status, "ERROR")' src/core/meteorite.py` prints nothing. Fail: meteorite still writes state `ERROR`, or the scrape fallback default is still `"ERROR"`.

## Boundaries

Does not send blobs to Ruth or walk the inbox (siblings #2 and #3). Does not create `NEW_EMAIL_ERROR` or `NOT_A_JOB` rows.

## Notes for planning

Citations above are the canon scope for this slice. Exact function names are yours; the Scope lines are the files and the kind of change.

## Git branch (authoritative)

Parent `ftr/AST-1711-rework-meteorite-email`. Child ref is recorded in the epic registry at dispatch.

### Comments

#### radia — 2026-09-19T22:55:47.980Z
[code-rubric] PROCEED (Commit: b4d8f65a) registry key SCRAPE_ERROR clean

#### betty — 2026-09-19T22:51:59.679Z
`origin/sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map` @ `b4d8f65a79d7716adc0b6daf494baa10cd77d892` · mailbox key tests

#### chuckles — 2026-09-19T22:32:42.728Z
[check-linear] answered — see the thread. Not clearing Active from check.

#### chuckles — 2026-09-19T22:32:42.234Z
[check-linear] answered — yes. A Done gate is the release. The parent still wears Active/chuckles from the early exit, and the watcher will not spawn while that label is on. That hold is the hole. Nothing more is needed from you. Not clearing it from check.

#### susan — 2026-09-19T22:31:42.206Z
@chuckles That sounds like a bug in the mechanism to resolve and unblock tickets for Archie calls.  The ticket in this instance is in the Done state, so I don't know what more should be needed to re-engage Ada.

#### chuckles — 2026-09-19T22:27:09.526Z
[check-linear] answered — see the thread. Not clearing Active from check.

#### chuckles — 2026-09-19T22:27:09.024Z
[check-linear] answered — the parent wave exited on the gate before any child reached User Testing. That exit is not a completion, so Active/chuckles stayed on the parent. The watcher treats that label as a live session and will not start another wave, so Ada's spawn never starts. Not clearing it from check.

#### susan — 2026-09-19T22:24:57.065Z
@chuckles Yes, I know what it is.  I do not understand why it is not currently in-flight.  What is happening with this ticket, if Ada is not working on it?

#### chuckles — 2026-09-19T22:23:36.028Z
[check-linear] answered — Active/ada is the in-flight spawn marker, not the Plan Approved marker. It is set when Ada's spawn starts and cleared when that spawn returns. No Ada spawn is running, so the label is off. Assignee stays Ada. Not setting it from check.

#### susan — 2026-09-19T22:23:10.232Z
@chuckles Can you find out why this ticket doesn't have the ada Active label on it, if the plan has been approved?

#### chuckles — 2026-09-19T22:10:59.699Z
[check-linear] Plan Approved — that Done gate is off this ticket. Assignee stays Ada.

#### susan — 2026-09-19T22:09:40.604Z
@chuckles The call was made, the ticket is done.

#### chuckles — 2026-09-19T21:49:15.357Z
[check-linear] answered — held for the widen-this-slice call, which is in. Plan Approved stays with Ada; the parent wave has not resumed this child. Not driving it from check.

#### susan — 2026-09-19T21:47:40.019Z
@chuckles Why is this ticket not progressing?

#### betty — 2026-09-19T19:09:09.178Z
@susan — suspected scope issue: this slice renames scrape-failure `ERROR` to `SCRAPE_ERROR` in `METEORITE_STATES`, but `update_meteorite` only accepts states in that registry (`src/data/database.py`). `src/core/meteorite.py` still calls `update_meteorite(..., state="ERROR")` — the plan’s scope gate defers those writes to AST-1713. Those calls now raise `ValueError: unknown meteorite state: 'ERROR'` and the row stays `NEW`.

Repro: `tests/component/core/test_meteorite.py::TestAst1703EmailBreadcrumb::test_stage_email_text_blank_link_errors` asserts state `ERROR`, got `NEW`. Same break on the other `state="ERROR"` paths in stage / scrape / land.

Recommendation: revise the plan so this slice retargets those `meteorite.py` writes to `SCRAPE_ERROR` before Tests Ready. The registry rename is not shippable alone. Do not weaken the writer tests. Holding Code Complete; assignee stays Ada.

#### joan — 2026-09-19T19:00:41.062Z
[plan-rubric] PROCEED (Commit: fccf0171663f737c49825abe1651267c0c33b394) registry and key rename

#### ada — 2026-09-19T18:58:09.844Z
`origin/sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map` @ `fccf0171663f737c49825abe1651267c0c33b394` · mailbox key plan

#### chuckles — 2026-09-19T18:55:40.762Z
AC2 narrowed: the `meteorite.py` `state="ERROR"` clause is not this child's contract. It is on AST-1713. Scope unchanged. Status back to Todo so the plan can be written.

#### ada — 2026-09-19T18:54:16.570Z
[scope-gate] AC2 requires `src/core/meteorite.py` writes this ticket's Scope does not name.

Needed: stop `update_meteorite(..., state="ERROR", ...)` (today at meteorite.py ~1371, 1379, 1389, 1401, 1411, 1424, 1473, 1571, 1604). AC2: `rg -n 'state="ERROR"' src/core/meteorite.py` prints nothing. Fail line: "meteorite still writes state ERROR".

Scope that does not cover it:
- `src/utils/config.py` — mailbox task key + meteorite state registry (ERROR renamed to SCRAPE_ERROR in that registry, its prior states, the scrape page-status map, and the stale list).
- `data/admin/agent_task.json` — mailbox shell row task key.
- `src/core/agent.py` — legacy mailbox prompt fold.
- Boundaries: does not send blobs to Ruth or walk the inbox (siblings #2 and #3).

AST-1713 already owns "modified stage, scrape, and land failure writes — the meteorite state literal ERROR becomes SCRAPE_ERROR". Doing those writes here duplicates that child. The other AC2 greps (`"SCRAPE_ERROR"` / `"NEW_EMAIL_ERROR"` / `"NOT_A_JOB"`) can pass from `config.py` alone; the `state="ERROR"` grep cannot.

Please narrow this ticket's AC2 so the meteorite.py `state="ERROR"` clause is not this child's contract (leave it on AST-1713). Do not add `meteorite.py` to this Scope. AC1's dispatcher / api_admin / inbox quoted-key greps are already empty; no gap there.

---

# AST-1712 — Mailbox key and classify-state map

**Linear:** [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email)
**Parent:** [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email)
**Publish ref:** `sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map`

Rename the candidate mailbox task key from `meteorite_email` to `stage_email_meteorite`, and extend the meteorite staging-state registry so classify outcomes and scrape failure have legal states. Link outcomes stay `SCRAPE_LINK`. No-scrape outcomes stay `READY`. Not-a-job is `NOT_A_JOB` (insert-legal, scheduled cleanup, not a dispatch trigger, not stale). Other stage failures are `NEW_EMAIL_ERROR` (insert-legal, not a dispatch trigger, and `NEW` lists it as a prior so a human can reset). Scrape-failure `ERROR` is renamed to `SCRAPE_ERROR` in the registry, its prior lists, the scrape page-status map, and the stale list. `patt.task.dispatch-retry`: that rename keeps the ordinary scrape retry under `SCRAPE_ERROR`. `NOT_A_JOB` and `NEW_EMAIL_ERROR` are not that retry. This ticket does not send blobs to Ruth or walk the inbox.

## Scope gate

Ticket **## Scope** (the files and the kind of change):

- `src/utils/config.py` — mailbox task key string `meteorite_email` becomes `stage_email_meteorite`; debug runner points at `inbox.check_email`; meteorite state registry gains `NOT_A_JOB` and `NEW_EMAIL_ERROR` with the properties in the technical scope, and renames scrape-failure `ERROR` to `SCRAPE_ERROR` in that registry, its prior states, the scrape page-status map, and the stale list.
- `data/admin/agent_task.json` — mailbox shell row `task_key` and `task_name` become `stage_email_meteorite`. Ruth's `stage_meteorite` row stays.
- `src/core/agent.py` — legacy mailbox prompt fold keys off `stage_email_meteorite` instead of `meteorite_email`.
- `src/core/meteorite.py` — existing failure writes `state="ERROR"` become `SCRAPE_ERROR`, including the scrape page-status fallback default. Do not add `NEW_EMAIL_ERROR` or `NOT_A_JOB` writes.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings):**

- Ruth save, consult removal, insert-state, and `NEW_EMAIL_ERROR` / `NOT_A_JOB` row writes — **AST-1713**. Do not add those writes here. The `ERROR` → `SCRAPE_ERROR` literal retarget is Stage 3, not AST-1713.
- `src/core/inbox.py` `check_email`, dispatcher mailbox branch, admin task-key checks — **AST-1714**. Those three files already contain no quoted `meteorite_email`. Do not edit them. Pointing `debug_func` at `inbox.check_email` is a config string only; do not create the function.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename scrape-failure `ERROR` to `SCRAPE_ERROR`; add `NOT_A_JOB` and `NEW_EMAIL_ERROR`; mailbox task key + debug runner | utils |
| `data/admin/agent_task.json` | Mailbox shell row `task_key` and `task_name` | data |
| `src/core/agent.py` | Legacy mailbox fold comment follows the renamed parse-config task key | core |
| `src/core/meteorite.py` | Failure writes `state="ERROR"` become `SCRAPE_ERROR` | core |

## Stage 1: Meteorite state registry

**Done when:** Importing `src.utils.config` succeeds. `METEORITE_STATES` has keys `NEW`, `SCRAPE_LINK`, `READY`, `BOT_BLOCKED`, `SCRAPE_ERROR`, `NOT_A_JOB`, `NEW_EMAIL_ERROR`, `LANDED`, `ABANDONED` and does not have key `ERROR`. `NEW` `prior_states` is `["NEW_EMAIL_ERROR"]`. `NOT_A_JOB` and `NEW_EMAIL_ERROR` have `prior_states` `None`. `METEORITE_STATES_RETENTION["purge_states"]` is `("LANDED", "NOT_A_JOB")`. `stale_list_states` is `("SCRAPE_ERROR", "BOT_BLOCKED", "ABANDONED")`. `scrape_page_status_states` `closed` and `missing` are `SCRAPE_ERROR`. No `trigger_state` value in this file is `NEW_EMAIL_ERROR` or `NOT_A_JOB`. `python3 -m py_compile src/utils/config.py` succeeds, then `~/astral/.venv/bin/python -c "import src.utils.config"` from this worktree succeeds. `agent_task.json` and `agent.py` are unchanged.

1. In `src/utils/config.py`, replace the `METEORITE_STATES` dict (the block that starts at `METEORITE_STATES = {` and ends at the `ABANDONED` entry) with:

```python
METEORITE_STATES = {
    "NEW": {
        "prior_states": ["NEW_EMAIL_ERROR"],  # human reset from stage failure
    },
    "SCRAPE_LINK": {
        "prior_states": ["NEW", "SCRAPE_ERROR"],  # link outcomes; retry from SCRAPE_ERROR
    },
    "READY": {
        # text fan-out from NEW; scrape success; Estelle paste recovery
        "prior_states": ["NEW", "SCRAPE_LINK", "BOT_BLOCKED"],
    },
    "BOT_BLOCKED": {
        "prior_states": ["SCRAPE_LINK"],
    },
    "SCRAPE_ERROR": {
        "prior_states": ["SCRAPE_LINK"],  # retry-holding after Playwright / scrape miss
    },
    "NOT_A_JOB": {
        "prior_states": None,  # insert-legal; scheduled cleanup; not a dispatch trigger; not stale
    },
    "NEW_EMAIL_ERROR": {
        "prior_states": None,  # insert-legal; not a dispatch trigger; human resets via NEW
    },
    "LANDED": {
        "prior_states": ["READY"],
    },
    "ABANDONED": {
        "prior_states": ["BOT_BLOCKED", "SCRAPE_ERROR"],  # nag limit / terminal stale
    },
}
```

⚠️ **Decision:** `prior_states is None` is insert-legal (same meaning as the old `NEW` entry and as `JOB_STATES` "None for unrestricted entry"). Only `NOT_A_JOB` and `NEW_EMAIL_ERROR` get that. `NEW`'s list is exactly `["NEW_EMAIL_ERROR"]` so a human reset is legal and classify insert is not. Do not add a `_RETRY` suffix or a `retry_state` key. `patt.task.dispatch-retry` for scrape failure is the existing `ERROR` role, renamed `SCRAPE_ERROR` (still a prior of `SCRAPE_LINK`, still the page-status failure target). `NOT_A_JOB` and `NEW_EMAIL_ERROR` are not that retry.

2. Replace `METEORITE_STATES_RETENTION` with:

```python
METEORITE_STATES_RETENTION = {
    "purge_states": ("LANDED", "NOT_A_JOB"),
    "stale_list_states": ("SCRAPE_ERROR", "BOT_BLOCKED", "ABANDONED"),
}
```

Do not add a day-count key. `METEORITE_RETENTION_CONFIG["landed_purge_days"]` stays `90`. `stale_list_days` stays `14`.

3. Replace the assert `set(METEORITE_STATES) == { ... }` with:

```python
assert set(METEORITE_STATES) == {
    "NEW", "SCRAPE_LINK", "READY", "BOT_BLOCKED", "SCRAPE_ERROR",
    "NOT_A_JOB", "NEW_EMAIL_ERROR", "LANDED", "ABANDONED",
}
```

4. Replace `assert METEORITE_STATES["NEW"]["prior_states"] is None` with:

```python
assert METEORITE_STATES["NEW"]["prior_states"] == ["NEW_EMAIL_ERROR"]
assert METEORITE_STATES["NOT_A_JOB"]["prior_states"] is None
assert METEORITE_STATES["NEW_EMAIL_ERROR"]["prior_states"] is None
```

5. In `METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]`, set `"closed"` and `"missing"` to `"SCRAPE_ERROR"`. Leave `"blocked": "BOT_BLOCKED"` and `"ok": "READY"`. Leave `stage_trigger_state` `"NEW"`, `scrape_trigger_state` `"SCRAPE_LINK"`, `land_trigger_state` `"READY"`.

6. Replace the assert set under `scrape_page_status_states` so it is:

```python
assert set(_mid_ingress["scrape_page_status_states"].values()) <= {
    "READY", "BOT_BLOCKED", "SCRAPE_ERROR",
}
```

7. Replace `assert set(METEORITE_STATES_RETENTION["purge_states"]) == {"LANDED"}` with `== {"LANDED", "NOT_A_JOB"}`. Replace `assert set(METEORITE_STATES_RETENTION["stale_list_states"]) == { "ERROR", "BOT_BLOCKED", "ABANDONED" }` with `{ "SCRAPE_ERROR", "BOT_BLOCKED", "ABANDONED" }`. In the comment above `METEORITE_RETENTION_CONFIG`, change `ERROR` to `SCRAPE_ERROR` (the stale-list name only).

8. Do not add any `trigger_state` whose value is `NEW_EMAIL_ERROR` or `NOT_A_JOB`, in dict form or assignment form. Do not add rows to `METEORITE_DISPATCH_TASKS`. Do not edit `JOB_STATES` or `CANDIDATE_STATES`.

## Stage 2: Mailbox task key

**Done when:** `rg -n "['\"]meteorite_email['\"]" src/utils/config.py data/admin/agent_task.json src/core/agent.py src/core/dispatcher.py src/ui/api/api_admin.py src/core/inbox.py` prints nothing. `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]` and `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` are `stage_email_meteorite`. `debug_func` is `inbox.check_email`. The agent_task row with `task_key_uuid` `39b73c1e-b24f-45bc-bd03-085c72892fb3` has `task_key` and `task_name` `stage_email_meteorite`. The `stage_meteorite` row (`task_key_uuid` `3bbd54c2-60a7-494e-b79a-e68aca7c2d77`) is unchanged. `~/astral/.venv/bin/python -c "import src.utils.config"` and `python3 -m py_compile src/core/agent.py` succeed.

1. In the module header inventory bullet for `METEORITE_EMAIL_MAILBOX_CONFIG`, replace `meteorite_email` with `stage_email_meteorite` and replace `meteorite.check_inbox` with `inbox.check_email`.

2. In `METEORITE_EMAIL_MAILBOX_CONFIG`, set `"task_key"` to `"stage_email_meteorite"` and `"debug_func"` to `"inbox.check_email"`. Leave `entity_type` `None`, `trigger_state` `None`, `auto_mode` `False`, and every other key as they are. Update the two asserts that compare `task_key` and `debug_func` to those new strings. In the comment block immediately above the dict, replace the task-key words `meteorite_email` with `stage_email_meteorite` and the runner words `meteorite.check_inbox` with `inbox.check_email`. Do not quote `meteorite_email` in that comment.

3. In `METEORITE_EMAIL_PARSE_CONFIG`, set `"task_key"` to `"stage_email_meteorite"`. Leave `"legacy_agent_task_key": "parse_meteorite_email"` and `"admin_entity_type": "candidate"`. Update the assert that compares `task_key` to `"stage_email_meteorite"`. Leave the `legacy_agent_task_key` assert.

4. Replace `assert "meteorite_email" not in TASK_CONFIG` with `assert "stage_email_meteorite" not in TASK_CONFIG`. Do not add `stage_email_meteorite` to `TASK_CONFIG`. `TASK_CONFIG["stage_meteorite"]` stays.

5. In `is_meteorite_email_mailbox_task_key`, do not rename the function. Replace the docstring with `True for stage_email_meteorite or its legacy agent_task key parse_meteorite_email.` The body stays `tk == cfg["task_key"] or tk == cfg["legacy_agent_task_key"]`.

6. In `dispatch_task_admin_defaults`, replace the comment `Canonical meteorite_email:` with `Canonical stage_email_meteorite:`. Do not change the `if` body. It already reads `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]`.

7. In `data/admin/agent_task.json`, on the object whose `task_key_uuid` is `39b73c1e-b24f-45bc-bd03-085c72892fb3`, set `task_key` and `task_name` to `stage_email_meteorite`. Change no other field on that object. Do not edit the object whose `task_key` is `stage_meteorite`.

8. In `src/core/agent.py` `_resolve_task_prompts`, keep `cfg = METEORITE_EMAIL_PARSE_CONFIG` and keep `if content_key == cfg["task_key"]`. Do not hardcode the task-key string in this file. Replace the two-line comment above `cfg = METEORITE_EMAIL_PARSE_CONFIG` with:

```python
    # Mailbox fold: empty agent_id on stage_email_meteorite falls back to
    # legacy_agent_task_key parse_meteorite_email. Key lives on METEORITE_EMAIL_PARSE_CONFIG.
```

⚠️ **Decision:** The fold compares `content_key` to `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`, which Stage 2 step 3 sets to `stage_email_meteorite`. A second literal in `agent.py` would drift. `parse_meteorite_email` stays the legacy row name; AC1 forbids the quoted key `meteorite_email` only.

## Stage 3: Legalize failure writes as SCRAPE_ERROR

**Done when:** `rg -n 'state="ERROR"' src/core/meteorite.py` prints nothing. `rg -n 'status_map.get(page_status, "ERROR")' src/core/meteorite.py` prints nothing. `python3 -m py_compile src/core/meteorite.py` succeeds. No other file changes. `tests/` unchanged. Log strings such as `This row is ERROR` stay.

`update_meteorite` accepts any `METEORITE_STATES` key and does not check priors, so `SCRAPE_ERROR` written from `NEW` or `READY` is legal.

1. In `run_stage_meteorite`, change every `update_meteorite(..., state="ERROR"` to `state="SCRAPE_ERROR"`: `missing classify_outcome`, `skip outcome on row`, `missing link`, `missing content`, `missing breadcrumb link`, and `unhandled classify_outcome`.
2. In `run_scrape_meteorite`, same change for `missing link`, and change the fallback `status_map.get(page_status, "ERROR")` to `"SCRAPE_ERROR"`.
3. In `run_land_meteorite`, same change for empty-content `READY` (`missing content`) and land-failed. Empty `BOT_BLOCKED` still skips; do not write a state on that path.
4. Do not add `NEW_EMAIL_ERROR` or `NOT_A_JOB` writes. Do not call Ruth. Do not edit consult, database insert, inbox, or `tests/`. Do not change log lines that say `This row is ERROR`.

⚠️ **Decision:** Component tests that assert `state == "ERROR"` on these paths will go red (`TestAst1703EmailBreadcrumb::test_stage_email_text_blank_link_errors` and the other meteorite assertions that hardcode `ERROR`). Do not put `ERROR` back to satisfy them. Betty updates those assertions on qa. This stage does not edit `tests/`.

## Execution contract

Execute stages in order, steps in order. One commit per stage on this epic worktree, then `git push origin <sha>:sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map`. Do not add files. Do not edit `tests/`. Stage 3 is the only edit to `src/core/meteorite.py`, and only the state literals listed there. If a named symbol has moved, stop and comment on AST-1711. Do not adapt silently.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Review

- **Build tip:** `origin/sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map` @ `d04430a722da8f5797a9d4109a9763cc09ebbb72`
- **Stages:** meteorite classify state registry → mailbox key `stage_email_meteorite` → failure writes `SCRAPE_ERROR`

## Joan validate

[plan-rubric]
**Ticket:** AST-1712
**Overall:** APPROVED
**Corpus:** 751624d7ebdf9bc441fc3d08a51ae751ea8026af
**Publish ref:** fccf0171663f737c49825abe1651267c0c33b394

## Canon scores
patt.task.dispatch-retry | A

## Traceability
AC1 → Stage 2 (mailbox task key, `agent_task.json`, `agent.py` fold); AC2 → Stage 1 (registry, retention, ingress map, no dispatch triggers on `NOT_A_JOB`/`NEW_EMAIL_ERROR`; narrowed AC2 — `meteorite.py` `state="ERROR"` clause deferred to AST-1713)

## Findings
None.

context_tokens≈32000

[plan-rubric] PROCEED (Commit: fccf0171663f737c49825abe1651267c0c33b394) registry and key rename

## Radia review

[code-rubric]
**Ticket:** AST-1712
**Publish ref:** `b4d8f65a79d7716adc0b6daf494baa10cd77d892` (`origin/sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map`)
**Corpus:** `751624d7ebdf9bc441fc3d08a51ae751ea8026af`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.dispatch-retry | A | | |

## Column diff vs plan stage

(aligned) — Joan `patt.task.dispatch-retry | A`; code review `A`.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Joan traceability drift** — `## Joan validate` traceability still says `meteorite.py` `state="ERROR"` is deferred to AST-1713; publish tip lands Stage 3 / AC3 (`ERROR` → `SCRAPE_ERROR` in `src/core/meteorite.py`). Artifact-only; implementation is correct.
- **Interim stage-failure routing** — `run_stage_meteorite` still writes `SCRAPE_ERROR` for classify/shape misses (same paths as pre-rename `ERROR`). Registry now defines `NEW_EMAIL_ERROR` / `NOT_A_JOB` and excludes them from dispatch retry; proper outcome routing is AST-1713 per plan boundaries. Expected sibling sequencing, not a canon defect on this slice.

## What's solid

- **Registry** — `METEORITE_STATES` drops `ERROR`, adds `SCRAPE_ERROR`, `NOT_A_JOB`, `NEW_EMAIL_ERROR`; `SCRAPE_LINK` priors include `SCRAPE_ERROR`; retention partitions and `scrape_page_status_states` retargeted; asserts lock the shape.
- **Dispatch-retry slice** — No `trigger_state` (ingress, dispatch tasks, or notify config) targets `NEW_EMAIL_ERROR` or `NOT_A_JOB`; `TestAst1712MailboxKeyAndClassifyStates::test_classify_states_and_no_dispatch_triggers` encodes that.
- **Mailbox key** — `stage_email_meteorite` on mailbox + parse configs, `agent_task.json` shell row (`39b73c1e-…`), `debug_func` → `inbox.check_email`; `stage_meteorite` Ruth row untouched; AC1 quoted-key grep clean on scoped product files.
- **Failure writes** — All `state="ERROR"` and `status_map.get(page_status, "ERROR")` retargeted to `SCRAPE_ERROR`; log strings `This row is ERROR` preserved.
- **Tests** — Betty manifest classes (`TestAst1712MailboxKeyAndClassifyStates`, `TestAst1712MailboxCatalogKey`, `TestAst1712NotAJobPurge`) plus revised meteorite state asserts; AST-756 fixture lockstep.
- **Scope** — No product edits to `inbox.py`, `dispatcher.py`, or `api_admin.py`; no `NEW_EMAIL_ERROR` / `NOT_A_JOB` row writes; estimate footprint fits confirmed **3**.

## Recommended actions

Chuckles: append artifact, `docs(AST-1712): Radia review — clean`, push sub ref, post slim upshot `--as radia`, → **Review Posted**; datt **PROCEED** → User Testing (no `resolve-child` canon work).

context_tokens≈48000

[code-rubric] PROCEED (Commit: b4d8f65a) registry key SCRAPE_ERROR clean
