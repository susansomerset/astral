# AST-1088 — gaze_email config + null-candidate dispatch shell + Gmail archive/trash

**Linear:** [AST-1088](https://linear.app/astralcareermatch/issue/AST-1088/gaze-email-config-null-candidate-dispatch-shell-gmail-archivetrash-add)
**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task) — Add gaze_email as a dispatch task
**Publish ref:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`

Owns Astral inbox expectation + unbound retention config, registers `gaze_email` as a normal dispatch task key, allows/provisions **one** `dispatch_task` row with **null** `candidate_id` and `auto_mode` true (schema must not require a candidate on every row; no AUTO subtype), and extends Gmail external with archive + Trash under a modify-capable OAuth scope contract. Does **not** own Ruth parse prompts (AST-1089) or the per-message bind/route/scrape/create decision tree (AST-1090). Does **not** invent a special AUTO dispatch path.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `GAZE_EMAIL_CONFIG`; `TASK_CONFIG["gaze_email"]` shell entry; special-case admin defaults + trigger/entity helpers for null claim queue | utils |
| `src/data/database.py` | Nullable `dispatch_task.candidate_id`; partial unique index for null-candidate rows; `save_dispatch_task` accepts `Optional` candidate_id | data |
| `src/core/dispatcher.py` | `ensure_gaze_email_dispatch_task` / `provision_gaze_email_dispatch_task`; call from `start_scheduler` | core |
| `src/external/gmail.py` | Expand scopes to modify-capable; add `archive_message` + `trash_message` | external |

No `tests/` / bible / React / Ruth agent_task / gaze_email runner body on this ticket.

## Stage 1: `GAZE_EMAIL_CONFIG` + `TASK_CONFIG` shell

**Done when:** Config exposes account address + unbound retention days + task/row seed literals; `TASK_CONFIG["gaze_email"]` exists so `dispatch_task_admin_defaults("gaze_email")` succeeds and returns null entity/trigger (no claim queue); Gmail secrets stay environ-only.

1. In `src/utils/config.py` module docstring config inventory, add one line:
   `GAZE_EMAIL_CONFIG — Astral inbox gaze_email task key, account expectation, unbound retention, dispatch row seed (AST-1088)`.

2. Immediately **after** `METEORITE_EMAIL_INGEST_CONFIG` (before `METEORITE_DISPATCH_TASKS`), add:

```python
# AST-1088: shared Astral inbox gaze_email dispatch shell (null candidate_id row).
# Live mailbox identity remains GMAIL_USER environ; account_address is the product expectation.
# Runner bind/route/create is AST-1090; Ruth parse task is AST-1089.
GAZE_EMAIL_CONFIG = {
    "task_key": "gaze_email",
    "account_address": "astral.career.match@gmail.com",
    "unbound_retention_days": 7,
    "auto_mode": True,
    "min_count": 1,
    "batch_size": 1,
    "freq_hrs": 0,
    # Mailbox poller — no entity claim queue on the dispatch_task row.
    "entity_type": None,
    "trigger_state": None,
}

assert isinstance(GAZE_EMAIL_CONFIG["unbound_retention_days"], int)
assert GAZE_EMAIL_CONFIG["unbound_retention_days"] > 0
assert GAZE_EMAIL_CONFIG["task_key"] == "gaze_email"
```

⚠️ **Decision — config owns the expected address; environ owns the live mailbox:** Parent AC requires account address from config with default `astral.career.match@gmail.com`. Existing Gmail I/O already binds to `GMAIL_USER` environ (`userId="me"`). Do **not** move `GMAIL_USER` / OAuth secrets into config. AST-1090 may compare `GAZE_EMAIL_CONFIG["account_address"]` to `GMAIL_USER` for ops diagnostics if needed — out of scope here.

3. In `TASK_CONFIG`, add a **shell** entry (no response schema / agent_task / Ruth prompts — AST-1089 owns parse):

```python
"gaze_email": {
    "entity_type": None,
    "requires_candidate_key": False,
    "trigger_state": None,
},
```

Place it near other non-consult dispatch keys if a natural neighbor exists; otherwise immediately before the closing `}` of `TASK_CONFIG` is fine.

4. In `dispatch_task_admin_defaults`, **before** the generic entity/trigger derivation, special-case:

```python
if tk == GAZE_EMAIL_CONFIG["task_key"]:
    return {
        "entity_type": None,
        "trigger_state": None,
        "sort_by": None,
        "batch_call_mode": 0,
    }
```

Do **not** call `_dispatch_entity_type_for_task_key` / `_dispatch_trigger_state_for_task_key` / `_dispatch_sort_by_for` for this key (those helpers assume ENTITY_TYPES claim queues).

5. In `_dispatch_trigger_state_for_task_key` and `_dispatch_entity_type_for_task_key`, add early returns of `None` for `GAZE_EMAIL_CONFIG["task_key"]` **only if** other callers need them — otherwise the admin-defaults special-case alone is enough. Prefer the admin-defaults special-case only to minimize blast radius; if a helper is still reached and would `raise KeyError`, add the early `None` return.

6. Do **not** add `gaze_email` to `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`, `_DISPATCH_BATCH_CALL_MODE_ONE`, or `DISPATCH_RETIRED_TASK_KEYS`. Do **not** add Ruth/agent_task JSON (AST-1089). Do **not** wire due-task eligibility or a runner body (AST-1090).

**Done when (recheck):** `from src.utils.config import GAZE_EMAIL_CONFIG, TASK_CONFIG` exposes the keys above; `dispatch_task_admin_defaults("gaze_email")` returns null entity/trigger/sort_by and `batch_call_mode=0`.

## Stage 2: Nullable `candidate_id` + save path

**Done when:** `dispatch_task.candidate_id` may be NULL; at most one null-candidate row per `task_key`; `save_dispatch_task` can insert `candidate_id=None` for `gaze_email`; existing non-null rows keep `UNIQUE(candidate_id, task_key, trigger_state)` behavior.

1. In `src/data/database.py` `_ensure_dispatch_task_schema`, after existing column/unique migrations, add a migration that makes `candidate_id` nullable when the live `CREATE TABLE` SQL still has `candidate_id TEXT NOT NULL`:

   - Read `sqlite_master` SQL for `dispatch_task`.
   - If `candidate_id TEXT NOT NULL` (or equivalent NOT NULL on that column via `PRAGMA table_info` — `notnull=1` for `candidate_id`): rebuild the table with `candidate_id TEXT` (nullable), same other columns, and `UNIQUE(candidate_id, task_key, trigger_state)`.
   - Copy all rows; `DROP` old; `RENAME` new; `commit`.
   - Follow the same rebuild style already used in this function for `enabled`→`auto_mode` / unique-key migrations (do not invent a new migration framework).

⚠️ **Decision — rebuild rather than `ALTER`:** SQLite cannot drop `NOT NULL` with a simple `ALTER COLUMN`. Match existing `_ensure_dispatch_task_schema` rebuild pattern.

2. After the nullable migration (and on fresh create), ensure a **partial unique index** so SQLite’s NULL-distinct UNIQUE quirk cannot duplicate null-candidate shells:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_dispatch_task_null_candidate_task_key
ON dispatch_task(task_key)
WHERE candidate_id IS NULL
```

Also create this index on the fresh `CREATE TABLE` path (after create). Update the module header inventory comment for `dispatch_task` to note `candidate_id` is nullable (shared Astral inbox tasks).

3. Change `save_dispatch_task` signature to accept `candidate_id: Optional[str] = None`. Pass the value through to INSERT as SQL NULL when `candidate_id` is `None` or blank after strip **only when** `task_key == GAZE_EMAIL_CONFIG["task_key"]` (import `GAZE_EMAIL_CONFIG` from config — data may already import config). For every other task_key, blank/None `candidate_id` remains invalid: raise `ValueError("candidate_id is required")` before INSERT.

⚠️ **Decision — null candidate_id is gaze_email-only at the save gate:** Parent requires null allowed for `gaze_email`, not a free-for-all null on every task. Application gate keeps accidental null rows out; schema nullity is the table-level allowance.

4. When inserting, allow `entity_type` / `trigger_state` / `sort_by` to remain SQL NULL when defaults return `None` (gaze_email). Do not coerce `None` to empty string for these columns.

5. Do **not** change `get_due_tasks` / `count_eligible_for_dispatch_task` / `_dispatch_one` in this stage. Today those paths skip rows missing `candidate_id` / `entity_type` / `trigger_state` — that keeps the provisioned `auto_mode=1` shell from firing until AST-1090 wires mailbox due + runner. Document that contract in the Stage 3 ensure docstring.

**Done when (recheck):** Fresh DB creates nullable `candidate_id`; existing DBs migrate; partial unique index exists; `save_dispatch_task(candidate_id=None, task_key="gaze_email", ...)` inserts one row; second insert of the same null shell raises UNIQUE; `save_dispatch_task(candidate_id=None, task_key="evaluate_jd", ...)` raises `ValueError`.

## Stage 3: Provision one null-candidate `gaze_email` row

**Done when:** Scheduler startup idempotently ensures exactly one `gaze_email` dispatch row with `candidate_id` NULL, `auto_mode` true (from config), null entity/trigger, and seed sizes from `GAZE_EMAIL_CONFIG`.

1. In `src/core/dispatcher.py`, add:

```python
def ensure_gaze_email_dispatch_task() -> Dict[str, Any]:
    """Idempotent insert of the shared Astral inbox gaze_email row (null candidate_id).

    Does not wire due-task eligibility or the mailbox runner (AST-1090).
    """
```

Concrete steps:

- `tk = GAZE_EMAIL_CONFIG["task_key"]`
- Scan `database.list_dispatch_tasks()` (or a focused query if adding one is clearly smaller) for an existing row where `(row.get("task_key") or "").strip() == tk` and `row.get("candidate_id")` is None or `""`.
- If found: return `{"task_key": tk, "added": 0, "skipped": 1, "id": row["id"]}`.
- If missing: `database.save_dispatch_task(candidate_id=None, task_key=tk, min_count=int(GAZE_EMAIL_CONFIG["min_count"]), auto_mode=bool(GAZE_EMAIL_CONFIG["auto_mode"]), entity_type=GAZE_EMAIL_CONFIG["entity_type"], trigger_state=GAZE_EMAIL_CONFIG["trigger_state"], batch_size=GAZE_EMAIL_CONFIG["batch_size"], freq_hrs=float(GAZE_EMAIL_CONFIG["freq_hrs"]))` and return `{"task_key": tk, "added": 1, "skipped": 0, "id": <new id>}`.
- If `tk not in TASK_CONFIG`, return/skip with `skipped_missing_config` (same spirit as meteorite ensure) — should not happen once Stage 1 lands.

2. Add thin wrapper:

```python
def provision_gaze_email_dispatch_task() -> Dict[str, Any]:
    """Startup provision for the shared gaze_email dispatch shell (AST-1088)."""
    return ensure_gaze_email_dispatch_task()
```

3. In `start_scheduler`, after the existing meteorite provision `try`/`except` block, add another `try`/`except` that calls `provision_gaze_email_dispatch_task()` and logs template-free stats (`added` / `skipped` / `id`) at info; on failure log exception (do not crash scheduler startup) — same pattern as AST-972 / AST-1054 provisions.

4. Do **not** copy this row via `set_dispatch_tasks_from_template_rows` / per-candidate meteorite ensure. Do **not** attach the row to `template_candidate_id`. Do **not** implement `_run_unified` / consult routing for `gaze_email` here.

**Done when (recheck):** Calling `ensure_gaze_email_dispatch_task` twice yields add then skip; `start_scheduler` invokes provision; no candidate-scoped duplicate shells.

## Stage 4: Gmail archive + Trash (modify-capable)

**Done when:** `src/external/gmail.py` can archive (remove `INBOX`) and move a message to Trash; credentials declare modify-capable scopes; every new live call gates through `require_controlled_external_io`; list/get/send keep working on the same credential helper.

1. Update the module docstring to state ownership of **send, inbox read, archive, and trash** via a **modify-capable** OAuth client. Keep required env vars unchanged (`GMAIL_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`; optional `GOOGLE_TOKEN_URI`). Note that live UAT must confirm the refresh token includes modify; remint is ops-only if verification fails (parent dependency — not a code branch).

2. Replace `_GMAIL_SCOPES` with:

```python
_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]
```

⚠️ **Decision — single `gmail.modify` scope:** Parent asks for a modify-capable credential contract for archive/trash. `gmail.modify` subsumes the prior send+readonly pair for send/list/get/label mutate/trash (non-permanent delete). Ops remint only if the existing refresh token was minted without modify.

3. Extend `__all__` with `"archive_message"` and `"trash_message"`.

4. Add public `archive_message(message_id: str) -> None`:

   - `require_controlled_external_io("gmail.archive_message")` first.
   - `users().messages().modify(userId="me", id=message_id, body={"removeLabelIds": ["INBOX"]})`.
   - On any exception after the gate, **raise** (same contract as list/get — callers map failures).

5. Add public `trash_message(message_id: str) -> None`:

   - `require_controlled_external_io("gmail.trash_message")` first.
   - `users().messages().trash(userId="me", id=message_id)`.
   - On any exception after the gate, **raise**.
   - Do **not** call `users().messages().delete` (permanent delete is out of parent scope).

6. Do **not** add core `inbox.py` wrappers on this ticket — AST-1090’s core runner may call external directly (core→external is allowed). Do **not** implement unbound age→trash policy here (runner owns the decision; this ticket only supplies the external capability named in AC 8).

**Done when (recheck):** Module docstring + scopes reflect modify; `archive_message` / `trash_message` are public, gated, and raise on failure; no permanent delete API.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1087 with the Stage N blocked template.
- Leave `get_due_tasks` / `_dispatch_one` / Ruth / bind-route-create untouched — AST-1090.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — touches utils config, data schema/migration + save gate, dispatcher provision, and Gmail external mutate APIs across four layers.

**Conf:** `high` — mirrors AST-1032 Gmail external + AST-1054/972 provision patterns; schema rebuild path already exists in `_ensure_dispatch_task_schema`; null-candidate due/runner explicitly deferred to AST-1090.

**Risk:** `Medium` — nullable `candidate_id` + unique/partial-index migration can break dispatch CRUD if wrong; expanding OAuth to `gmail.modify` requires ops token verification at UAT; leaving auto_mode shell non-due until AST-1090 is intentional (row visible, not self-firing).

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth:** Retention days, task key, account expectation, row seed literals in `GAZE_EMAIL_CONFIG`; secrets stay environ.
- **§2.1 / secrets-and-env-specific-from-environ:** `GMAIL_USER` + OAuth vars remain environ; no tokens in config.
- **§2.5 / core-vs-external:** Archive/trash I/O only in `gmail.py`; policy/age-gate stays out (AST-1090).
- **§1.4 / no-hardcoded-sets:** No inline `7` / task key / account string outside config.
- **§3.3 imports:** data←utils, core←data/utils, external←utils only.
- **in-scope-only:** No Ruth prompts, no runner decision tree, no AUTO subtype, no permanent delete, no Manage Email UI redesign.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`
**Tip:** `7dc42f3d` (`7dc42f3d`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `852d76cb` | GAZE_EMAIL_CONFIG + TASK_CONFIG shell |
| 2 | `d138f905` | nullable candidate_id + save gate |
| 3 | `090c0abc` | provision null-candidate gaze_email row |
| 4 | `7dc42f3d` | Gmail archive + trash under gmail.modify |
