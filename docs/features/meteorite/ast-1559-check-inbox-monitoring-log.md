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

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1559
**Overall:** APPROVED
**Publish ref:** `sub/AST-1555/AST-1559-check-inbox-monitoring-log` @ `f55dab146b11fd5a084240d6f1de58a4853c75e1`

## Traceability
AC1 → Stages 3–4 (`check_inbox` inline classify via `invoke_stage_meteorite` → `insert_meteorite_rows` N-row fan-out → `archive_candidate_email`; classify/map failure leaves mid unarchived with zero rows); AC2 → Stage 3 skip branch (`STAGE_METEORITE_CONFIG["skip_outcomes"]` → zero rows + `log_meteorite_inbox_classify` always-on info, then archive).

## Findings

### acceptable
- **Location:** Linear ticket — `## Citations` / `## Scope` empty
- **Finding:** Dispatch template fields blank; plan Scope gate correctly mirrors parent proposed child #3 and **What this implements**.
- **Recommendation:** Chuckles backfill Linear `## Citations` / `## Scope` from parent #3 when appending (same hygiene as AST-1557); plan content itself is scoped.

### acceptable
- **Location:** Stage 3 — `classify_failed` / `map_failed` monitoring literals
- **Finding:** Hardcoded outcome strings while `already_ingested` lives in `METEORITE_MONITORING_CONFIG`.
- **Recommendation:** Optional follow-up to fold error-path literals into config; not blocking — they are monitoring labels, not state sets.

### acceptable
- **Location:** Stage 3 — `_map_classify_jobs_to_meteorite_rows` vs `_map_stage_jobs_to_scraps`
- **Finding:** Parallel partition logic; plan explicitly avoids calling land/scrap mapper from `check_inbox`.
- **Recommendation:** Keep as staged; AST-1560 owns `NEW`→transition path.

**In-session statute pass:** `invoke_stage_meteorite` delegates to `do_task` with `STAGE_METEORITE_CONFIG["task_key"]` — **astral.agent.do-task-delegation** conforms. Inline classify + fan-out only (no scrape/land in same run) — **astral.state.no-daisy-chain-in-run** conforms with parent carve-out. `meteorite` → `inbox` → Gmail, no `external/gmail` in `meteorite.py` — **astral.layers.import-direction** / **astral.layers.core-vs-external-bright-line** conform. Monitoring via `get_logger(...).info` always-on — **astral.standards.logging-via-utils** / **astral.standards.debug-contract-gated** conform. Format SSOT in config — **astral.config.config-source-of-truth** conforms. Universal orch.* — N/A/conforms.

## Radia review

# Radia review — AST-1559

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1559  
**Publish ref:** `sub/AST-1555/AST-1559-check-inbox-monitoring-log` @ `c8e5506a387c05f353d9bf2e995b8c54ebf121c5`  
**Overall:** DISCUSS  
**Internal grade:** DISCUSS (product faithful; eligibility-count gap + branch stack)

**Baseline:** `git diff origin/dev...origin/sub/AST-1555/AST-1559-check-inbox-monitoring-log`  
**Status gate:** Tests Passed (spawn prompt — trusted)

**AST-1559-only product footprint** (commits `9fde2953`…`9f150cf3`): `src/utils/config.py`, `src/core/candidate.py`, `src/core/meteorite.py`, `src/core/dispatcher.py` (+14 lines mailbox repoint).

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no confidence bounds |
| astral.agent.do-task-delegation | scoped | conforms | `invoke_stage_meteorite` → `do_task` with `STAGE_METEORITE_CONFIG["task_key"]` |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch claim |
| astral.batch.batch-id-format | scoped | not-applicable | no batch ids |
| astral.batch.claim-process-release | scoped | not-applicable | mailbox poller, not entity claim queue |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent_responses |
| astral.config.config-source-of-truth | scoped | conforms | `METEORITE_MONITORING_CONFIG` format SSOT; outcomes from `STAGE_METEORITE_CONFIG` / mailbox config |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | `GMAIL_USER` read only in `check_inbox` debug account-mismatch check (not config) |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no artifacts dir |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes |
| astral.dispatch.seed-auto-false | scoped | conforms | no new auto seeds; task_key stays `meteorite_email` |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `ast-1559-*.md` plan doc |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty test commits |
| astral.git.engineer-test-tree-ban | scoped | not-applicable | engineer `src/` per plan contract |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no `src.external.gmail` in `meteorite.py`; inbox owns Gmail I/O |
| astral.layers.import-direction | scoped | conforms | meteorite→inbox→external; candidate helpers in core |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI in AST-1559 footprint |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | direct `invoke_stage_meteorite`, not render verdict |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no route changes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | admin JSON untouched |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot seed |
| astral.seed.define-approved | scoped | not-applicable | implement ticket |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join |
| astral.standards.data-raises-caller-logs | scoped | conforms | data helpers called; exceptions propagate to runner |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py edits in AST-1559 commits |
| astral.standards.debug-contract-gated | scoped | conforms | Style D gated `debug=True`; monitoring is deliberate always-on `logger.info` per plan carve-out |
| astral.standards.dry-and-focused-functions | scoped | conforms | `_map_classify_jobs_to_meteorite_rows` parallels scrap mapper; `email_aliases_for_candidate` consolidates lookup |
| astral.standards.in-scope-only | scoped | conforms | AST-1559 commits touch only scoped files |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger(__name__).info` for monitoring |
| astral.standards.names-not-ticket-ids | scoped | conforms | `check_inbox`, `log_meteorite_inbox_classify` |
| astral.standards.no-cross-contamination | scoped | conforms | meteorite ingress path cohesive; no `meteorite_email.py` delete |
| astral.standards.no-hardcoded-sets | scoped | conforms | skip/landable partitions from `STAGE_METEORITE_CONFIG`; monitoring format in config |
| astral.standards.public-then-helpers | scoped | conforms | public `check_inbox` / `log_meteorite_inbox_classify` after helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | fan-out to `NEW` only; no scrape/land transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | staging rows, not job transitions |
| astral.state.no-daisy-chain-in-run | scoped | conforms | inline classify + insert rows; no scrape/land in same run |
| astral.ui.frontend-file-placement | scoped | not-applicable | no UI |
| astral.ui.naming-conventions | scoped | not-applicable | no UI |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1559)` on tip |
| orch.git.commit-vocabulary | universal | conforms | staged commits per plan |
| orch.git.flow-direction-inviolable | universal | conforms | sub under AST-1555 |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1555/AST-1559-…` |
| orch.git.merge-on-checkout | universal | conforms | sync merges from ftr/dev on branch |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | clean history |
| orch.git.no-dev-agent-branches | universal | conforms | engineer sub branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1555 worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-policy invention |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–4 implemented |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review |
| orch.roles.archie-approves-statutes | universal | conforms | no new statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest + tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Katherine assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | implementer still assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no hook bypass |

**Active set scored:** 64 rows (registry lists 65; all corpus ids covered).

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan **Citations** list `astral.*` statutes only; no `pattern.*` ids in plan body |

---

## Plan adherence

**Stages 1–4 (AST-1559 commits):** Matches plan.

| Stage | Verdict |
|-------|---------|
| **1 Config** | `METEORITE_MONITORING_CONFIG` + asserts; `debug_func` → `meteorite.check_inbox`; header bullet |
| **2 candidate.py** | `email_aliases_for_candidate` uses `_lookup_path_value` / `_iter_uniqueness_path_values`; order-stable dedupe |
| **3 meteorite.py** | `check_inbox` pipeline: aliases → fetch → dedup → classify → fan-out / skip / fail paths; monitoring always-on; archive rules; `update_candidate_last_email_check`; no Gmail import |
| **4 dispatcher** | Mailbox branch `await check_inbox(...)`; log strings updated; `meteorite_email.py` retained |

**AC1 / AC3 traceability:** Tests cover N-row fan-out + archive, classify-fail zero rows + no archive, skip zero rows + monitor + archive, dedup skip classify, empty aliases still stamp.

**Estimate 5:** Honest for ~350 LOC `check_inbox` + config + candidate helper + dispatcher repoint.

**Dependencies consumed:** `insert_meteorite_rows`, `list_meteorites_by_source`, `fetch_candidate_email`, `archive_candidate_email` present (AST-1557/1558 merged on branch).

---

## Findings

### discuss — mailbox `available_count` still zero (AST-1558 deferral not closed)

- **Location:** `src/core/inbox.py` `count_inbox_bound_by_candidate` / `count_inbox_messages_bound_to_candidate`; `src/core/dispatcher.py` `run_task` mailbox branch
- **Finding:** Stubs still return `{}` / `0` with docstring “until AST-1559 eligibility,” but AST-1559 plan forbids `inbox.py` edits and implementation did not repoint Avail to alias-filtered message counts. AUTO mailbox dispatch `available_count` remains 0.
- **Recommendation:** Not blocking CLICK/manual `check_inbox` UAT. **Susan/Archie:** confirm AUTO Avail is intentionally deferred (follow-up ticket) or accept CLICK-only until counts wired. **Do not** expand resolve-child scope without parent decision.

### discuss — stacked sibling product on publish ref vs `origin/dev`

- **Location:** Full three-dot diff includes AST-1557 (`database.py`, `METEORITE_STATES`), AST-1558 (`inbox.py`, `api_inbox`, `AdminManageEmail`, dispatcher fetch_email retirement) plus AST-1559 work
- **Finding:** Expected after `merge AST-1557/1558 dependency` + ftr sync; AST-1559-only commits are the four files above.
- **Recommendation:** **Chuckles/datt:** ensure ftr merge order matches blockedBy; no double-land of sibling commits.

### discuss — `total_failed` never incremented in `check_inbox` summary

- **Location:** `src/core/meteorite.py::check_inbox` return dict
- **Finding:** Counters use `processed` / `passed` / `errors`; `total_failed` stays 0 even on map/classify error paths (errors bucket used instead).
- **Recommendation:** Dispatcher ledger may still be correct via `total_errors`. Advisory unless downstream dashboards distinguish failed vs errors.

### advisory — per-message `invoke_stage_meteorite` late import lacks B1 comment

- **Location:** `check_inbox` inner loop, `from src.core.consult import invoke_stage_meteorite`
- **Finding:** Function-scoped import with no cycle-break comment (dispatcher mailbox branch has one).
- **Recommendation:** Optional one-line comment in resolve-child; not AC-blocking.

### advisory — monitoring line not asserted in Betty tests

- **Location:** `TestAst1559CheckInbox`
- **Finding:** Fan-out / archive / dedup / skip / classify-fail covered; no explicit `logger.info` / format-string assertion for `log_meteorite_inbox_classify`.
- **Recommendation:** Betty follow-up if log contract regression risk matters; not fix-now per rubric.

### advisory — `classify_failed` / `map_failed` literals hardcoded

- **Location:** `check_inbox` monitoring calls
- **Finding:** Joan acceptable finding in plan; only `already_ingested` in config.
- **Recommendation:** Optional config fold later.

### advisory — sibling test/bible bleed + off-manifest debt

- **Location:** AST-1556 tracker tests, `test_ast1467` `INBOX_BIND_CONFIG` assert (if still on branch)
- **Finding:** Same pattern as AST-1557/1558 Radia reviews; manifest-scoped green.
- **Recommendation:** Chuckles/Betty hygiene downstream; not AST-1559 product.

---

## What's solid

- `check_inbox` correctly implements parent ingress spine: inline classify, N-row fan-out at `NEW`, archive on success/skip/dedup, no archive on classify/map failure.
- No `stage_meteorite` / `land_meteorite` / Gmail imports in `meteorite.py`.
- Monitoring format SSOT in config; subject sanitization; always-on info separate from Style D.
- `email_aliases_for_candidate` in core (dedupes AST-1558 api_inbox helper for runner path).
- Dispatcher repointed; `meteorite_email.py` preserved per AST-1562 boundary.
- Betty manifest covers fan-out AC, classify-fail, skip, dedup, empty aliases, config literals, dispatcher routing.

---

## Frame diff

| Area | Paths | Verdict |
|------|-------|---------|
| AST-1559 product | `config.py` monitoring, `candidate.py` aliases, `meteorite.py` check_inbox, `dispatcher.py` repoint | In-scope; plan-faithful |
| AST-1559 tests/bible | `test_meteorite.py::TestAst1559CheckInbox`, `test_candidate.py`, `test_config.py`, `test_dispatcher.py`, meteorite/candidate/dispatcher bible | In-scope |
| Sibling stack | AST-1557 `database.py`; AST-1558 inbox/api/ui/dispatcher retirements | Discuss — merged dependencies |
| Out of scope respected | No `meteorite_email.py` delete; no scrape/land transitions; no UI edits in AST-1559 commits | Conforms |

---

## Notes

- Joan plan-rubric APPROVED @ `f55dab14`; no Excluded-statute attachment.
- C6 lenses (imports, layers, silent failure, fallbacks, logging, batch §5f, external §5g): no fix-now violations in AST-1559 `src/` footprint.
- `grep` confirms zero `src.external.gmail` imports in `meteorite.py` at tip.
- No fix-now product findings on AST-1559 scope.

---

## Recommended actions (downstream — not Radia)

1. **Chuckles:** Append verdict; post slim upshot; → Review Posted.
2. **Susan/Archie:** Decide AUTO `available_count` follow-up vs CLICK-only acceptance.
3. **resolve-child:** Optional B1 comment on consult lazy import; no mandatory product changes for AC1/AC3.
4. **Chuckles/datt:** Manage sibling-stack merge order on ftr.

## Resolution

**2026-08-31 — resolve-child (Katherine)**

Radia **DISCUSS** @ `c8e5506a` — no fix-now product findings on AST-1559 footprint.

| Finding | Action |
|---------|--------|
| Advisory — B1 lazy import in `check_inbox` | Added `# Late-import: consult loads is_meteorite_company at module top.` before inner-loop `invoke_stage_meteorite` import (matches `stage_meteorite`) |
| Discuss — mailbox `available_count` stubs | **Deferred** — AST-1558 docstring deferral; plan forbids `inbox.py` edits; CLICK/manual UAT acceptable per Radia |
| Discuss — sibling stack on publish ref | **No code change** — expected merge of AST-1557/1558 dependencies; Chuckles owns ftr merge order |
| Discuss — `total_failed` never incremented | **No code change** — dispatcher ledger uses `total_errors`; advisory only |
| Advisory — monitoring assert / config literals | **No code change** — Betty/Chuckles follow-up if needed |

**§9a:** `origin/sub/AST-1555/AST-1559-check-inbox-monitoring-log` merges cleanly into `origin/dev`. `origin/ftr/AST-1555` not on origin — ftr dry-run skipped.

**Manifest:** Betty §QA test manifest re-run green before User Testing.

