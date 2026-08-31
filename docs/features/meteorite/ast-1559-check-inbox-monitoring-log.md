# AST-1559 — check_inbox + monitoring log

**Linear:** [AST-1559](https://linear.app/astralcareermatch/issue/AST-1559/check-inbox-monitoring-log-meteorite-ingress-staging-table-inboxmeteorite-consolidation)  
**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) — Meteorite ingress: staging table + inbox/meteorite consolidation  
**Publish ref:** `sub/AST-1555/AST-1559-check-inbox-monitoring-log`

After AST-1557 (#1) and AST-1558 (#2): add `meteorite.check_inbox` as the candidate-bound mailbox poller — resolve aliases → `fetch_candidate_email` → inline classify via `invoke_stage_meteorite` → fan-out N `meteorite` rows at `NEW` → archive Gmail on successful classify → stamp `last_email_check`; plus an always-on **info** monitoring helper whose format string lives in config. Repoint the dispatcher mailbox runner from `meteorite_email.run_meteorite_email` to `check_inbox`. Does **not** delete `meteorite_email.py`, run scrape/land transitions, Estelle recovery, retention sweep, or unbound Trash hygiene.

## UAT fitness

- **AC restored:** Parent AC1 — “A successful classify of one email that yields N jobs creates exactly N `meteorite` rows and archives the Gmail mid once; a classify LLM failure leaves the mid in inbox and creates zero rows.” Parent AC3 — “`not_job_content` (and other no-job classify outcomes) produce no `meteorite` row and no job; the always-on info monitoring line records the email + outcome.”
- **Correct outcome:** Dispatcher `meteorite_email` task runs `check_inbox`; one bound email with a landable classify outcome produces N staging rows (visible in `meteorite` table) and removes the message from Gmail INBOX; a classify LLM failure leaves the message in INBOX with zero new rows; skip outcomes emit one always-on monitoring line and zero rows.
- **Sibling check:** AST-1557 supplies `insert_meteorite_rows` / `list_meteorites_by_source`; AST-1558 supplies `fetch_candidate_email` / `archive_candidate_email` (no bind, no `meteorite`→Gmail import in `meteorite.py`). AST-1560 owns `NEW`→`SCRAPE_LINK`/`READY` transitions and row-level monitoring — this ticket only logs post-classify email lines. AST-1562 deletes `meteorite_email.py` — leave the module in place here.
- **Not sufficient:** Repointing dispatcher to `check_inbox` while still calling `stage_meteorite` (inline land) or skipping monitoring / archive / fan-out.
- **Wrong fix rejected:** Keeping `run_meteorite_email` bind+Trash+land path — violates parent table-driven ingress (#3) and leaves no staging checkpoint for AST-1560.

## Scope gate

Linear child **## Scope** / **## Citations** are empty (dispatch template). Authoritative partition is parent **Proposed child tickets → #3** (mirrored in this ticket’s **What this implements**):

- `src/core/meteorite.py` — `check_inbox` + monitoring helper; no unbound hygiene
- `src/utils/config.py` — monitoring format + mailbox runner literals pointing at `check_inbox`
- `src/core/candidate.py` and/or DB stamp helper — alias resolution + `last_email_check` stamp
- `src/core/dispatcher.py` / `data/admin/` seed — repoint `meteorite_email` poller to `check_inbox`

**Citations (parent #3):** `astral.agent.do-task-delegation`, `astral.standards.logging-via-utils`, `astral.standards.debug-contract-gated` (monitoring is explicit non–Style-D info), `astral.state.no-daisy-chain-in-run` (inline classify in `check_inbox`, no separate pre-classify dispatch hop)

**Out of scope (siblings):** AST-1557 table/helpers (consume only); AST-1558 inbox/Manage Email (consume only); AST-1560 stage/scrape/land; AST-1561 Estelle/`apply_paste`; AST-1562 retention + delete `meteorite_email.py`; row transition monitoring lines (`BOT_BLOCKED` / `ERROR` / `LANDED job=`).

**Depends on:** AST-1557 and AST-1558 merged onto the epic line before **build-child** (Chuckles merge-child order). If `insert_meteorite_rows`, `list_meteorites_by_source`, `fetch_candidate_email`, or `archive_candidate_email` are missing after sync, **stop** and comment on AST-1559 — do not invent stubs.

All Files Changed / Stages stay inside the Scope file set above.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_MONITORING_CONFIG` (format SSOT + subject sanitize limit + dedup outcome literal); repoint `METEORITE_EMAIL_MAILBOX_CONFIG["debug_func"]` to `meteorite.check_inbox`; update header inventory + asserts | utils |
| `src/core/candidate.py` | Add public `email_aliases_for_candidate(candidate_id)` using existing `_lookup_path_value` / `_iter_uniqueness_path_values` | core |
| `src/core/meteorite.py` | Add `_sanitize_meteorite_monitor_subject`, `log_meteorite_inbox_classify`, `_map_classify_jobs_to_meteorite_rows`, `check_inbox`; update module docstring | core |
| `src/core/dispatcher.py` | Mailbox branch: late-import and `await check_inbox(...)` instead of `run_meteorite_email`; log strings may say `check_inbox` | core |

**Verified no touch:** `data/admin/agent_task.json` — `meteorite_email` remains the agent_task / dispatch **task_key**; no runner path stored in JSON. Grep at build time; edit only if a seed row names `meteorite_email.run`.

## Stage 1: Config — monitoring format + mailbox runner literals

**Done when:** `METEORITE_MONITORING_CONFIG` is importable with a single inbox-classify format string and subject limit; `METEORITE_EMAIL_MAILBOX_CONFIG["debug_func"] == "meteorite.check_inbox"`; module header inventory documents the new block; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py` module header inventory, add a bullet for `METEORITE_MONITORING_CONFIG` — always-on info inbox classify line format + subject sanitize limit (AST-1559); distinct from Style D / `debug=True` paths.

2. Immediately **after** the `METEORITE_EMAIL_MAILBOX_CONFIG` assert block (~line 2710 today) and **before** `FETCH_EMAIL_CONFIG` / bind blocks (may already be deleted on post–AST-1558 tree), insert:

```python
# AST-1559: always-on info monitoring for meteorite ingress (not Style D).
METEORITE_MONITORING_CONFIG = {
    "subject_max_len": 120,
    "outcome_already_ingested": "already_ingested",
    "inbox_classify_line": (
        "meteorite inbox classify from={from_address} mid={message_id} ts={internal_date_ms} "
        "subj={subject} candidate={candidate_id} outcome={classify_outcome} jobs={job_count}"
    ),
}
```

3. Add asserts:

- `isinstance(METEORITE_MONITORING_CONFIG["subject_max_len"], int)` and `> 0`
- `METEORITE_MONITORING_CONFIG["outcome_already_ingested"]` is non-empty str
- `"inbox_classify_line"` contains `{from_address}`, `{message_id}`, `{candidate_id}`, `{classify_outcome}`, `{job_count}`

4. In `METEORITE_EMAIL_MAILBOX_CONFIG`, change `"debug_func": "meteorite_email.run"` → `"debug_func": "meteorite.check_inbox"`. Update the comment above the block to say runner is `meteorite.check_inbox` (candidate aliases → fetch → classify → fan-out); drop “unbound Trash hygiene” from the comment (removed in this runner).

5. Update the existing assert `METEORITE_EMAIL_MAILBOX_CONFIG["debug_func"] == "meteorite_email.run"` to expect `"meteorite.check_inbox"`.

6. Do **not** add scrape/land/notify/retention task keys, retire `unbound_retention_days` (AST-1562), or change `task_key` (stays `meteorite_email`).

⚠️ **Decision:** Row-level transition monitoring (`BOT_BLOCKED`, `ERROR`, `LANDED job=`) is AST-1560 Scope — only `inbox_classify_line` in this ticket.

## Stage 2: candidate.py — email aliases for check_inbox

**Done when:** `email_aliases_for_candidate(candidate_id)` returns order-stable unique bare addresses from `CANDIDATE_LOOKUP_CONFIG` email paths; empty string id → `[]`; missing candidate → `[]`; `python3 -m py_compile src/core/candidate.py` succeeds.

1. In `src/core/candidate.py`, after `_lookup_path_value` (~line 1561), add public:

```python
def email_aliases_for_candidate(candidate_id: str) -> list[str]:
    """Bare email addresses from CANDIDATE_LOOKUP_CONFIG paths (order-stable, unique)."""
```

2. Implementation (mirror AST-1558 `api_inbox._email_aliases_for_candidate` logic but use existing core helpers):

- `cid = (candidate_id or "").strip()`; if not `cid`: return `[]`
- `row = get_candidate(cid)`; if not row: return `[]`
- `seen: set[str] = set()`; `aliases: list[str] = []`
- For each `path` in `CANDIDATE_LOOKUP_CONFIG["email_paths"]`: `_lookup_path_value(row, path)` → `parseaddr` → token with `@`; dedupe by `casefold()`; append original token casing from parseaddr
- For each `path` in `CANDIDATE_LOOKUP_CONFIG["email_list_paths"]`: iterate `_iter_uniqueness_path_values(row, path)` same parse/dedupe
- Return `aliases`

3. Do **not** edit `src/ui/api/api_inbox.py` to call this helper (out of Scope — duplication acceptable until a follow-up).

4. `check_inbox` will call `update_candidate_last_email_check(cid)` from `src.data.database` at run end (same as today’s `run_meteorite_email`) — no new DB helper unless that symbol is missing after AST-1557 merge (then stop and comment).

## Stage 3: meteorite.py — monitoring helper, fan-out mapper, check_inbox

**Done when:** `check_inbox(task, debug=...)` returns the same summary dict shape as `run_meteorite_email` (`total_processed`, `total_passed`, `total_failed`, `total_errors`); successful landable classify inserts N rows via `insert_meteorite_rows`; classify LLM failure creates zero rows and leaves mail in inbox; skip outcomes create zero rows, emit monitoring line, and archive; dedup via `list_meteorites_by_source` skips re-classify; module never imports `src.external.gmail`; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. Update `src/core/meteorite.py` module docstring to document `check_inbox` (AST-1559) alongside existing public APIs; note no Gmail I/O in this module.

2. Add imports at top (keep existing; add as needed):

- `from src.core.candidate import email_aliases_for_candidate, get_candidate`
- `from src.core.inbox import archive_candidate_email, fetch_candidate_email, get_message_html, strip_extract_email_html`
- `from src.data.database import insert_meteorite_rows, list_meteorites_by_source, update_candidate_last_email_check`
- `from src.utils.config import METEORITE_MONITORING_CONFIG, METEORITE_EMAIL_MAILBOX_CONFIG, STAGE_METEORITE_CONFIG`

3. Add `_sanitize_meteorite_monitor_subject(raw: str) -> str`:

- Coerce to str; replace `\r`, `\n`, `\t` with single space; collapse repeated spaces; strip
- Truncate to `METEORITE_MONITORING_CONFIG["subject_max_len"]` characters (suffix `"…"` if truncated)

4. Add `log_meteorite_inbox_classify(*, from_address, message_id, internal_date_ms, subject, candidate_id, classify_outcome, job_count) -> None`:

- Build line with `METEORITE_MONITORING_CONFIG["inbox_classify_line"].format(...)` using sanitized subject
- Call `get_logger(__name__).info(line)` — **always**, regardless of `debug` (not `debug_index`)

5. Add `_map_classify_jobs_to_meteorite_rows(outcome, jobs, *, candidate_id, source_kind, source_id) -> tuple[list[dict], str | None]`:

- Same partition rules as `_map_stage_jobs_to_scraps` (`STAGE_METEORITE_CONFIG` text vs url outcomes; skip outcomes → `[], None`)
- Return list of dicts suitable for `insert_meteorite_rows`: required `candidate_id`, `source_kind`, `source_id`; optional `classify_outcome` (= outcome), `content` (= `jd_text`), `link` (= http(s) `job_link` for url outcomes, `None` for text outcomes)
- Do **not** set `source_ref` (parent: no `email-<mid>` synthesis on this path)
- On malformed jobs (missing jd_text / job_link per partition), return `[], "<reason>"`

⚠️ **Decision:** Reuse classify partition logic parallel to `_map_stage_jobs_to_scraps` but emit staging insert dicts — do not call `land_meteorite` or `_map_stage_jobs_to_scraps` from `check_inbox` (AST-1560 owns transitions from `NEW`).

6. Add `async def check_inbox(task: dict, *, debug: bool = False) -> dict[str, int]`:

**Setup**

- `cid = str((task or {}).get("candidate_id") or "").strip()`; if empty raise `ValueError("candidate_id is required")`
- If `debug`: `logger.set_debug_flag(True)`; optional Style D run-start line using `METEORITE_EMAIL_MAILBOX_CONFIG["debug_func"]` and `cid` as identifier (same pattern as `run_meteorite_email`)
- `aliases = email_aliases_for_candidate(cid)`; `messages = fetch_candidate_email(aliases, debug=debug)` — empty aliases → empty list, still stamp last check at end
- Initialize counters `processed = passed = failed = errors = 0`

**Per message loop** (enumerate with 1-based index for Style D when `debug=True`):

a. **Dedup:** If `list_meteorites_by_source("email", mid)` returns any rows: call `log_meteorite_inbox_classify(..., classify_outcome=METEORITE_MONITORING_CONFIG["outcome_already_ingested"], job_count=len(existing))`; try `archive_candidate_email(mid)` (ignore archive failure → count as error); increment processed/passed or errors; continue — do not re-classify.

b. **Fetch body:** `get_message_html(mid)` + `strip_extract_email_html(...)` with header fields from payload; on exception → Style D outcome `error`, increment errors, **no** monitoring line required (optional warning log OK), continue.

c. **Classify (inline):** Late-import `from src.core.consult import invoke_stage_meteorite`. Build `ctx` from `get_candidate(cid)` like `stage_meteorite` does. `invoke = await invoke_stage_meteorite(cid, blob, source_kind="email", source_id=mid, ctx=ctx, debug=debug)`.

d. **Classify failure** (`not invoke.get("success")`): log monitoring with `classify_outcome="classify_failed"` (literal string, not in STAGE_METEORITE_CONFIG) and `job_count=0`; **do not** archive; increment `errors`; Style D outcome `error`; continue.

e. **Skip outcome** (`invoke["outcome"] in STAGE_METEORITE_CONFIG["skip_outcomes"]`): `log_meteorite_inbox_classify(..., classify_outcome=invoke["outcome"], job_count=0)`; `archive_candidate_email(mid)`; increment processed/passed; Style D outcome str(outcome); continue.

f. **Landable outcome:** `_map_classify_jobs_to_meteorite_rows(...)` → if error string: treat like classify failure (no rows, no archive, monitoring with `classify_outcome="map_failed"`, job_count=0, errors++); else `ids = insert_meteorite_rows(row_dicts)` — must satisfy `len(ids) == len(row_dicts) == len(invoke.get("jobs") or [])` for valid map; `log_meteorite_inbox_classify(..., classify_outcome=invoke["outcome"], job_count=len(ids))`; `archive_candidate_email(mid)`; increment processed/passed; Style D outcome `archived` or outcome string.

**Run end**

- Always `update_candidate_last_email_check(cid)` after loop completes (including zero messages)
- If `debug`: run-complete Style D + summary dict line (mirror `run_meteorite_email`)
- Return `{"total_processed": processed, "total_passed": passed, "total_failed": failed, "total_errors": errors}`

7. **Forbidden in this function:** `trash_message`, `list_inbox_messages` without alias filter, `stage_meteorite`, `land_meteorite`, bind/unbound branches, any `src.external.gmail` import.

⚠️ **Decision — archive on successful classify:** Archive when classify completes successfully (`invoke.success`), including skip outcomes (0 rows) and landable fan-out (N rows). Do not archive on `invoke` failure or map failure — mail stays for retry (parent AC1).

⚠️ **Decision — Style D vs monitoring:** Style D remains `debug=True` only; monitoring helper is always-on info per parent functional scope #6.

## Stage 4: dispatcher — repoint mailbox runner to check_inbox

**Done when:** `_dispatch_one` mailbox branch calls `check_inbox` instead of `run_meteorite_email`; exception log text references `check_inbox`; grep `data/admin/*.json` for `meteorite_email.run` — if absent, no admin JSON edit; `python3 -m py_compile src/core/dispatcher.py` succeeds.

1. In `src/core/dispatcher.py`, mailbox branch (`_is_inbox_mailbox_task_key`):

- Change late import to `from src.core.meteorite import check_inbox`
- Replace `await run_meteorite_email(task, debug=debug)` with `await check_inbox(task, debug=debug)`
- Update debug_detail string `mailbox runner (meteorite_email path)` → `(check_inbox path)` (cosmetic)
- Update `CancelledError` / generic exception log messages from `meteorite_email` → `check_inbox` where they name the runner

2. Run `rg 'meteorite_email\.run' data/admin/` from repo root. If zero matches, **skip** admin JSON edits (task_key stays `meteorite_email`; provision rows unchanged).

3. Do **not** delete `src/core/meteorite_email.py` or change `process_meteorite_email_messages` / selected-ids helpers (AST-1562 / AST-1558 api paths).

4. Do **not** change `_meteorite_email_due_tasks` or `ensure_meteorite_email_dispatch_task` task_key.

## Execution contract

- Execute stages in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-1555/AST-1559-check-inbox-monitoring-log`.
- Do not edit `src/core/inbox.py`, `src/data/database.py` (except calling existing helpers), `src/ui/**`, `meteorite_email.py`, `tests/`, or bible.
- If AST-1557/1558 symbols or signatures differ after sync, stop and comment on **parent AST-1555** with the blocking format from plan-child.

## Estimate

Confirm Chuckles estimate: 5 — agree
