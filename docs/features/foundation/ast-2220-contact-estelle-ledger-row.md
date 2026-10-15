# AST-2220 — Contact Estelle turns open and close a ledger row

- **Linear:** [AST-2220](https://linear.app/astralcareermatch/issue/AST-2220)
- **Parent:** [AST-2215](https://linear.app/astralcareermatch/issue/AST-2215) — Add task `fetch_timesheet`
- **Publish ref:** `sub/AST-2215/AST-2220-contact-estelle-ledger-row`

Wrap every contact LLM turn that records a timesheet row in a `dispatch_ledger` open/close so the closed row gets timesheet state `NEW` and the recorded call carries that `batch_id` with request type `CONTACT_AGENT`. Covers `run_contact_estelle_turn` and the existing peer helper `_run_contact_ledgered_task`. Does **not** rename `dispatch_ledger`, own the `fetch_timesheet` runner (AST-2218), or Google search recording (AST-2219).

## UAT fitness

- **AC restored:** Parent AC **9** (“Contact turns mint a ledger row”): a stubbed Estelle turn creates one ledger row with `completed_at` set and timesheet state `NEW`, and the timesheet row for that turn carries that `batch_id` and request type `CONTACT_AGENT`.
- **Correct outcome:** After an Estelle (or peer contact) turn that hits the LLM, the candidate has a closed ledger batch whose `timesheet_state` is `NEW`, and every `service_timesheet` row written during that turn shares that `batch_id` with `request_type=CONTACT_AGENT`, so the turn enters the same receipt queue as dispatch batches.
- **Sibling check:** AST-2217 already owns `service_timesheet` attribution columns, `LEDGER_TIMESHEET_STATES`, and `do_task` defaulting to `DISPATCH_AGENT` (explicit deferral comment points here). AST-2218 owns runner / OpenRouter billed receipts / daemon retire / dispatcher close → `NEW`. AST-2219 owns Google `DISPATCH_SEARCH`. This plan only touches `contact.py` + the optional `request_type` kwarg on `do_task` in `agent.py`. Verified by Files Changed + Boundaries.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Opening a ledger without setting `timesheet_state=NEW` on close leaves contact batches out of the `NEW` queue. Leaving `do_task` hardcoding `DISPATCH_AGENT` would mint a ledger row but fail AC 9’s request-type check. Post-hoc rewriting of timesheet rows after the call is wrong — attribution is call-time (AST-2217).

## Explicit scope gate

Files and change kinds below are exactly this ticket’s **## Scope**. Test / bible paths are Betty (`qa-child`); engineer stages commit **product** files only (pre-commit bans `tests/` / `docs/test-bible/**`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Optional `request_type` on `do_task` (default `DISPATCH_AGENT`); pass through to `_send_to_server` | core |
| `src/core/contact.py` | Estelle turn + `_run_contact_ledgered_task`: open ledger, set `log_batch_id`, pass `CONTACT_AGENT`, close with `timesheet_state=NEW` | core |
| `tests/component/core/test_contact.py` | Betty — AC 9 stubbed Estelle turn | test |
| `docs/test-bible/core/contact.md` | Betty | bible |

**Out of this ticket (siblings):** `src/core/timesheets.py` runner, `src/core/dispatcher.py`, `src/external/openrouter.py`, `src/external/google_cse.py`, `src/core/roster.py`, `src/utils/config.py`, `src/data/database.py` (call existing `save_dispatch_ledger` / `update_dispatch_ledger` / `timesheet_state` only — no schema edits).

## Stage 1: Optional `request_type` on `do_task`

**Done when:** Callers can pass `request_type="CONTACT_AGENT"` into `do_task` and the recorded timesheet row gets that value; every existing caller that omits the kwarg still records `DISPATCH_AGENT` (byte-identical default to today’s behavior).

1. In `src/core/agent.py`, add keyword-only-compatible optional arg to `async def do_task(...)`:

```python
request_type: str = "DISPATCH_AGENT",
```

Place it after the existing kwargs (`store_agent_data`, `chain_context` — keep signature order stable by appending at the end before the closing paren). Document in the docstring: default `DISPATCH_AGENT`; contact turns pass `CONTACT_AGENT` (AST-2220).

2. Replace the hardcoded

```python
request_type="DISPATCH_AGENT",
```

on the `_send_to_server(...)` call inside `do_task` (the line immediately under the AST-2217 comment that says `contact = AST-2220`) with:

```python
request_type=request_type,
```

Keep the multi-entity `entity_id=None if _multi else …` logic unchanged.

3. Do **not** change the ad-hoc / other `_send_to_server` call sites in this file — they stay `DISPATCH_AGENT` literals (or omit via default if they go through `do_task`). Do **not** add a ContextVar for request type.

4. Assert by reading the call graph: `do_task(..., request_type="CONTACT_AGENT")` → `_send_to_server(..., request_type="CONTACT_AGENT")` → external `record_timesheet(..., request_type=...)`. Omitting the kwarg → `"DISPATCH_AGENT"`.

⚠️ **Decision:** Kwarg on `do_task`, not a ContextVar — contact already owns the call site and Scope names this shape explicitly. Default preserves every dispatch / hop caller.

## Stage 2: Contact ledger wrap + `CONTACT_AGENT`

**Done when:** A stubbed successful `run_contact_estelle_turn` (and a stubbed `_run_contact_ledgered_task` peer) leaves one `dispatch_ledger` row with `completed_at` set and `timesheet_state="NEW"`, and every timesheet row written under that turn carries the same `batch_id` with `request_type="CONTACT_AGENT"`. Failure / exception paths still close the ledger (status `FAILED` when the turn did not succeed) with `timesheet_state="NEW"` so the batch still enters the receipt queue. No rename of `dispatch_ledger`.

### 2a. Peer helper `_run_contact_ledgered_task`

1. In `src/core/contact.py`, import `CONTACT_AGENT` from the request-type registry already landed by AST-2217:

```python
from src.utils.config import (
    ...
    TIMESHEET_REQUEST_TYPES,  # only if needed for assert; prefer the literal via a local constant
)
```

Prefer a module-level constant next to other contact constants (or inline the string once at the call sites):

```python
_CONTACT_TIMESHEET_REQUEST_TYPE = "CONTACT_AGENT"  # TIMESHEET_REQUEST_TYPES; AST-2220
```

Do **not** invent a parallel registry. The string must be exactly `"CONTACT_AGENT"` (in `TIMESHEET_REQUEST_TYPES`).

2. Update `_run_contact_ledgered_task` so the `do_task(...)` call passes `request_type=_CONTACT_TIMESHEET_REQUEST_TYPE` (or `"CONTACT_AGENT"`).

3. On `update_dispatch_ledger` close (both success and failure paths that already set `status` / `completed_at` / totals / `total_cost`), also pass:

```python
timesheet_state="NEW",
```

Keep the existing `finally:` that resets `log_batch_id` and flushes the log buffer. Ledger open (`save_dispatch_ledger`) and `log_batch_id.set(batch_id)` stay as they are — that already passes `batch_id` into the recorded call via the contextvar AST-2217’s writers read.

4. `logger.debug` on the existing Calling / Response joints for `save_dispatch_ledger`, `do_task`, and `update_dispatch_ledger` — add `timesheet_state` / `request_type` to the Calling lines where those values are now passed (`stat.logging.debug`). Do not gate on `debug=`.

### 2b. `run_contact_estelle_turn`

1. After the candidate gate succeeds (`cid` / `row` valid) and **before** the first `do_task` (section **d**), mint a ledger batch and set the contextvar — same shape as `_run_contact_ledgered_task`:

```python
batch_id = f"contact-estelle-{uuid.uuid4()}"
started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
logger.debug("Calling save_dispatch_ledger: [batch_id=%s, candidate_id=%s]", batch_id, cid)
database.save_dispatch_ledger(
    batch_id, "contact-estelle", cid, started_at, entity_type="candidate", batch_size=1
)
_ledger_token = log_batch_id.set(batch_id)
```

Task key string on the ledger row is `"contact-estelle"` (audit label, not a `TASK_CONFIG` key). Do **not** open a second ledger for the follow-up `do_task` in the same turn — one turn, one batch.

2. Wrap the LLM work (primary `do_task`, optional follow-up `do_task`, and the close) in `try` / `finally`:

- Both `do_task(...)` calls (primary and follow-up) pass `request_type=_CONTACT_TIMESHEET_REQUEST_TYPE` (or `"CONTACT_AGENT"`).
- After both calls finish (success or not), before building the Slack outbound / return dict, close the ledger:

```python
ok = bool(turn.get("success")) and do_task_error is None
# Late import if not already imported at module/function scope for compute_batch_cost:
from src.core.agent import compute_batch_cost  # keep late-import discipline if needed
logger.debug(
    "Calling update_dispatch_ledger: [batch_id=%s, ok=%s, timesheet_state=NEW]",
    batch_id, ok,
)
database.update_dispatch_ledger(
    batch_id,
    status="COMPLETED" if ok else "FAILED",
    completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    total_processed=1,
    total_passed=int(ok),
    total_failed=int(not ok),
    total_cost=compute_batch_cost(batch_id),
    timesheet_state="NEW",
)
```

Place the close after `do_task_error` / `turn` / outcome are known (today that is just above the `out = {…}` block), still inside the `try`, so a turn that failed the LLM still gets `FAILED` + `NEW`.

- `finally:` always `flush_log_buffer()` and `log_batch_id.reset(_ledger_token)`.

3. Early returns **before** the ledger open (listen off, no candidate) stay unchanged — no ledger row.

4. If an exception escapes between open and close, the `finally` still clears `log_batch_id`. Add an `except` only if needed so the ledger is still closed with `status="FAILED"`, `completed_at` set, and `timesheet_state="NEW"` before re-raising — same audit trail as a failed turn. Prefer:

```python
try:
    ...
    # close ledger as above
except Exception:
    database.update_dispatch_ledger(
        batch_id,
        status="FAILED",
        completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        total_processed=1,
        total_passed=0,
        total_failed=1,
        total_cost=compute_batch_cost(batch_id),
        timesheet_state="NEW",
    )
    raise
finally:
    flush_log_buffer()
    log_batch_id.reset(_ledger_token)
```

Do not double-close on the happy path (structure so the success close and the except close are mutually exclusive).

5. Reuse existing imports already in `contact.py` (`uuid`, `datetime`, `timezone`, `database`, `log_batch_id`, `flush_log_buffer`, `logger`). Late-import `compute_batch_cost` / `do_task` the same way `_run_contact_ledgered_task` already does if that avoids a top-level cycle.

⚠️ **Decision:** One ledger row per Estelle turn (primary + optional follow-up share `batch_id`), matching parent AC 9’s “one ledger row” and parent Purpose (“each Estelle / contact turn opens and closes a ledger row”). Peer markup tasks keep their own per-call ledger via `_run_contact_ledgered_task`.

⚠️ **Decision:** Close always writes `timesheet_state="NEW"` including `FAILED` turns — parent Functional scope 2: every closed batch after deploy enters the queue; receipt runner decides readiness. Do not leave contact failures with null timesheet state.

## Estimate

Confirm Chuckles estimate: 2 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2220
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-2215/AST-2220-contact-estelle-ledger-row` @ `9187008ca81e727934a9e97a11d0f12f3192d730`

## Canon scores

patt.entity.batch-processing | A | | 
stat.logging.debug | A | | 

## Traceability

Parent AC: 9 → Stages 1–2 (ledger open/close `NEW`, `CONTACT_AGENT`, shared `batch_id`); 1–8,10–11 → N/A (siblings); Stages map to parent FS 8 + Purpose contact-queue bullet; child Linear AC empty — plan cites parent AC 9 in UAT fitness.

## Findings

### acceptable — Scope gate closure (`agent.py`)

- **Severity:** acceptable
- **Location:** `[scope-gate]` comment; ticket `## Scope` + plan Files Changed
- **Finding:** Prior gate correctly flagged `CONTACT_AGENT` wiring; Scope now includes optional `request_type` on `do_task`; plan Stage 1 matches.
- **Recommendation:** None.

### discuss — Build ordering vs AST-2217

- **Severity:** discuss
- **Location:** Boundaries / Stage 2 (`timesheet_state`, attribution registry)
- **Finding:** Plan assumes AST-2217 landed (`update_dispatch_ledger` accepts `timesheet_state`, `do_task`→`_send_to_server` attribution path, `TIMESHEET_REQUEST_TYPES`).
- **Recommendation:** Chuckles merge/build order: #1 UT before #4 build, or engineer confirms ftr carries #1 schema — not a plan rewrite.

### acceptable — Ledger close before post-LLM work (land / Slack)

- **Severity:** acceptable
- **Location:** Stage 2b try/close vs current `land_results` block after `do_task`
- **Finding:** Close sits after primary + follow-up `do_task`, before `out = {…}` (and thus before `contact_land_meteorite`); matches parent AC 9 focus on the Estelle LLM timesheet row, not ancillary land calls.
- **Recommendation:** Betty AC 9 stub should assert LLM-recorded row only; flag if land ever records billable rows without `batch_id`.

### discuss — Child `## Acceptance criteria` empty on Linear

- **Severity:** discuss
- **Location:** AST-2220 Description
- **Finding:** Parent AC 9 is the operative bar; plan `## UAT fitness` quotes it.
- **Recommendation:** Optional dispatch hygiene: paste child AC checkbox mirroring parent AC 9.

context_tokens≈32000

## Review (build)

**Built @ `050ce556a`** — `origin/sub/AST-2215/AST-2220-contact-estelle-ledger-row` (`050ce556a026063ac8fc9c4cda1376c4b04303bc`)

- Stage 1: `do_task` optional `request_type` (default `DISPATCH_AGENT`) passed to `_send_to_server`.
- Stage 2: `run_contact_estelle_turn` opens/closes one `contact-estelle` ledger with `timesheet_state=NEW`; primary + follow-up `do_task` pass `CONTACT_AGENT`; `_run_contact_ledgered_task` peer same attribution + NEW on close.
- Betty owns `tests/component/core/test_contact.py` + bible AC 9.



## Radia review

[code-rubric]
**Ticket:** AST-2220
**Publish ref:** `442105796baca3bf1981e08105bf8c74e9ccfe65` (`origin/sub/AST-2215/AST-2220-contact-estelle-ledger-row`)
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Overall:** FIX-NOW

## Canon scores

patt.entity.batch-processing | A | |
stat.logging.debug | A | |

## Column diff vs plan stage

(aligned) — Joan: both A @ plan tip `9187008ca81e727934a9e97a11d0f12f3192d730`; build adds `request_type` on `do_task` + contact ledger wrap through tip `442105796`.

## Frame diff

(none)

## Findings

### fix-now

- **`_run_contact_ledgered_task` exception path** — `src/core/contact.py`: `run_contact_estelle_turn` closes the ledger with `status=FAILED` and `timesheet_state="NEW"` in `except` before re-raise; `_run_contact_ledgered_task` only closes inside the happy `try` after `do_task` returns. If `asyncio.run(do_task(...))` raises, the ledger row stays open (no `completed_at`, no `timesheet_state=NEW`), breaking parent AC **9** for peer contact markup paths. Mirror the Estelle `except` + `_ledger_closed` guard (or equivalent) on the peer helper.

### discuss

- **Ledger close vs ancillary work** — `run_contact_estelle_turn` closes the ledger after `land_calls` and optional Slack post, still before `out = {…}`. Plan Stage 2b text allows “just above `out`”; Joan’s acceptable note imagined close before `contact_land_meteorite`. `log_batch_id` remains set through land/Slack.
  - **@susan:** Should contact ledger close immediately after the last `do_task`, excluding land/Slack from the open batch window?
  - **Default:** leave close where it is (land/Slack are not LLM timesheet writers today; Betty AC 9 asserts LLM rows only).

### advisory

- **Sibling product + test carry (AST-2217):** Three-dot diff vs `origin/dev` includes full AST-2217 stack (`database.py`, `config.py`, externals, attribution tests/bibles, `ast-2217` plan doc) because #1 is not on `dev` yet. AST-2220’s own product commits are only `src/core/agent.py` (+`request_type` kwarg) and `src/core/contact.py` (`a28f6e9c3`…`866018ee8`). Expected epic ordering; not scope smuggling on this child.
- **Build ordering:** Stage 2 assumes AST-2217 (`timesheet_state` on `update_dispatch_ledger`, `service_timesheet` attribution, `_send_to_server` path). Satisfied on this publish ref; Joan plan discuss unchanged.
- **Estimate footprint:** Confirmed **2** — 2220-owned product surface matches plan; large stat is stacked #1.

## What's solid

- Stage 1: `do_task(..., request_type=...)` defaults to `DISPATCH_AGENT`; wired through to `_send_to_server` without ContextVar.
- Stage 2b: Estelle turn opens one `contact-estelle-{uuid}` ledger, sets `log_batch_id`, passes `CONTACT_AGENT` on primary and follow-up `do_task`, closes with `timesheet_state="NEW"` on success/failure, `except` path for escape before close, `finally` resets contextvar + flushes log buffer.
- Peer helper: `CONTACT_AGENT` + `timesheet_state="NEW"` on normal success/failure close; debug joints name `request_type` / `timesheet_state` where passed.
- Betty: `test_contact.py` AC 9 coverage for Estelle + peer (`timesheet_state`, `batch_id`, `CONTACT_AGENT` on ledger and timesheet rows).
- Boundaries: no runner, dispatcher close path, OpenRouter, Google CSE, or new schema edits in 2220-owned commits.

## Recommended actions (Chuckles / downstream — not executed by Radia)

- Append artifact; `docs(AST-2220): Radia review — findings`; push; post slim upshot `--as radia`; **Review Posted** → `resolve-child` for peer `except` close.
- After AST-2217 lands on `dev`, future three-dot reviews of later siblings should shrink carry noise only; no action required for this verdict.

context_tokens≈42000

## Resolution

**Date:** 2026-10-15

- **fix-now — peer `_run_contact_ledgered_task` exception path:** Mirrored Estelle’s `except` + `_ledger_closed` guard. If `do_task` raises before the normal close, the ledger is updated `FAILED` + `timesheet_state="NEW"` then re-raised; `finally` still resets `log_batch_id` / flushes.
- **discuss — ledger close vs land/Slack:** No `Default:`; @susan unanswered. Kept tip behavior (close after land/Slack, just above `out`) per plan Stage 2b — no product move of the close window.
- **advisory:** No product action (sibling carry / estimate).

