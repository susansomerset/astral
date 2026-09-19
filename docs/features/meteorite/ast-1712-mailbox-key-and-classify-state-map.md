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

All Files Changed / Stages stay inside that set.

**Out of scope (siblings):**

- `src/core/meteorite.py` writes, Ruth save, consult removal — **AST-1713**. Do not add `"SCRAPE_ERROR"` / `"NEW_EMAIL_ERROR"` / `"NOT_A_JOB"` there. AC2's `rg` of `config.py` and `meteorite.py` prints matches once `config.py` has the strings.
- `src/core/inbox.py` `check_email`, dispatcher mailbox branch, admin task-key checks — **AST-1714**. Those three files already contain no quoted `meteorite_email`. Do not edit them. Pointing `debug_func` at `inbox.check_email` is a config string only; do not create the function.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename scrape-failure `ERROR` to `SCRAPE_ERROR`; add `NOT_A_JOB` and `NEW_EMAIL_ERROR`; mailbox task key + debug runner | utils |
| `data/admin/agent_task.json` | Mailbox shell row `task_key` and `task_name` | data |
| `src/core/agent.py` | Legacy mailbox fold comment follows the renamed parse-config task key | core |

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

## Execution contract

Execute stages in order, steps in order. One commit per stage on this epic worktree, then `git push origin <sha>:sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map`. Do not add files. Do not edit `tests/` or `src/core/meteorite.py`. If a named symbol has moved, stop and comment on AST-1711. Do not adapt silently.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Review

- **Build tip:** `origin/sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map` @ `8827531f39ee9f94503ebffe52608eb8a7d37f01`
- **Stages:** meteorite classify state registry → mailbox key `stage_email_meteorite`

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
