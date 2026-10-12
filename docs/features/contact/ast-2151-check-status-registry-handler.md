# AST-2151 — Check-status registry entry, deeplink origin, and job handler

**Linear:** [AST-2151](https://linear.app/astralcareermatch/issue/AST-2151)
**Parent:** [AST-2144](https://linear.app/astralcareermatch/issue/AST-2144) — Add /check-status to Estelle's functions
**Publish ref:** `origin/sub/AST-2144/AST-2151-check-status-registry-handler`

This ticket adds the config and data half of `@Estelle /check-status <search string>`. In `src/utils/config.py` it adds a second row to the `CONTACT_CONFIG["commands"]` registry (the first one is `/add-job`, from AST-2035). That row is `check-status`, in `code` mode, with its reply templates and a per-command `reply_placement` of `always_with_share`. The registry asserts are relaxed so `ack_reply_template` is optional, and new asserts check the shape of the new template fields and the placement vocabulary. The ticket also adds the handler's pinhole row and an env-name contract (`RAILWAY_PUBLIC_DOMAIN`) placed next to `JOBS_DETAIL_ROUTE_PREFIX`. In `src/core/tracker.py` it adds the handler. The handler finds the sender's own job(s) using the same matcher and ownership check as `contact_task_get_job_by_pattern`, with no new query and no hydration. It then composes a terse reply: one match, several matches, no match, or no links when the origin env is unset. It returns that reply as `reply_text` on the handler result. This ticket ships parent AC 1–2 and the handler side of AC 4 and AC 7–10. It does **not** touch `src/core/contact.py`. Posting `reply_text` and applying `reply_placement` belong to sibling **#2 (Hedy)**.

## Scope gate

The ticket's `## Scope` names two files, `src/utils/config.py` and `src/core/tracker.py`. Every row below is one of those two files, and every change is a kind the Scope names:

- `src/utils/config.py`: the new `check-status` command entry (handler, mode, description, usage text, reply-template fields, placement field), the modified registry asserts, the new pinhole row, and the new deeplink-origin env-name contract next to `JOBS_DETAIL_ROUTE_PREFIX`.
- `src/core/tracker.py`: the new command handler, plus one private formatting helper for the timestamps it uses. The Scope's "times through `format_contact_timezone_clock`" needs a string-to-datetime step, because job `created_at` and `state_changed_at` are `TEXT` columns. That step is part of the handler, so the private helper is in scope.

Reused as-is (no change): `_match_jobs_by_pattern`, `_job_owned_by_candidate` (both in `tracker.py`), `format_contact_timezone_clock`, `JOBS_DETAIL_ROUTE_PREFIX` (both in `config.py`), and `src.core.meteorite._candidate_contact_timezone` (the existing reader for `contact.timezone`; imported inside the function, because `meteorite` already imports `tracker` at module level).

**Interim behavior until #2 lands (on ftr only, never dev):** today's `_run_contact_command` reads `meta["ack_reply_template"]` on an `ok` result, and `check-status` declares no such field. A `/check-status` hit would raise a `KeyError`. The existing intercept `try/except` in `_handle_slack_event_body` logs it once, and the hear-ack posts. A miss posts the hear-ack, as it does today. #2 replaces this path. That is the ticket's "Until #2 lands, the composed text and placement aren't used."

## Contract with sibling #2 (Hedy)

These two names are new here, and #2's `contact.py` change reads them. #2's plan must use the same spelling.

⚠️ **Decision:** The handler result carries the composed text under the key **`reply_text`** (a `str`, or `None` when there is nothing to post). The full shape is `{ok, meteorite_id, error, reply_text}`. `meteorite_id` is always `None` for this handler. It stays in the shape because `_run_contact_command` and `_emit_listen_info` read it (`meteorite:-`).

⚠️ **Decision:** The per-command placement field on a registry entry is named **`reply_placement`**. Its values are the `thread_response` vocabulary: `threads_only`, `always_no_share`, `always_with_share`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Updated `commands` comment. New `check-status` entry. Private `_CONTACT_THREAD_RESPONSE_MODES` tuple, used by the existing `thread_response` assert and the new `reply_placement` assert. Private `_CONTACT_COMMAND_TEXT_FIELDS` / `_CONTACT_COMMAND_JOB_LOOKUP_FIELDS` maps that drive the optional-field asserts. Modified command-registry assert loop. New `_CONTACT_PINHOLE_HANDLERS` row. New `JOBS_DETAIL_ORIGIN_DOMAIN_ENV` constant plus its assert, after `JOBS_DETAIL_ROUTE_PREFIX`. | utils |
| `src/core/tracker.py` | Imports (`os`, `urllib.parse.quote`, four config names). New private `_contact_job_clock`. New public `contact_command_check_status`, placed directly after `contact_task_get_job_by_pattern`. | core |

No other file is touched. `tests/` and `docs/test-bible/**` are Betty's.

## Stage 1: Config: registry entry, asserts, pinhole, origin env contract

**Done when:** parent AC 1 and AC 2 pass as written. `python3 -c "from src.utils.config import CONTACT_CONFIG as C; e=C['commands']['check-status']; print(e['mode'], e['reply_placement'])"` prints `code always_with_share`. AC 2's command prints `read job`. If you temporarily delete `{deeplink}` from `match_reply_template`, the import fails on an `AssertionError`. Revert that edit before committing. `/add-job` still imports, with its ack template unchanged.

1. In `src/utils/config.py`, replace the four-line comment directly above `"commands": {` (it starts `# AST-2035: Slack commands —`) with:

   ```python
       # AST-2035: Slack commands — `@Estelle /<command id> <payload>`, recognized only as the
       # first token after leading @mentions. handler: sync src.core.* callable
       # (candidate_id, payload, *, source_id, thread_ts, debug) -> {ok, meteorite_id, error[, reply_text]}.
       # mode "code": fixed usage post, no LLM turn; the handler's reply_text when it returns one, else
       # ack_reply_template on ok (AST-2144). mode "agent": one Estelle turn sees the result.
       # Optional reply_placement overrides thread_response for this command's replies (AST-2144).
   ```

2. In `src/utils/config.py`, inside `CONTACT_CONFIG["commands"]`, add this entry immediately **after** the closing `},` of the `"add-job": { … }` entry and **before** the closing `},` of `"commands"`:

   ```python
           # AST-2151: read-only status lookup over the sender's own jobs (no LLM turn, no writes).
           "check-status": {
               "handler": "src.core.tracker.contact_command_check_status",
               "mode": "code",
               "description": "Look up your own job by link, title, company, or job id: its state, dates, and a link to the job page.",
               "usage_reply_text": "Usage: @Estelle /check-status <job link, title, company, or job id>",
               # Every reply to this command threads under the sender's message and shares to channel.
               "reply_placement": "always_with_share",
               # One match. Format with job_title=, created_at=, state=, state_changed_at= (contact clock), deeplink=.
               "match_reply_template": "{job_title}\nReceived {created_at}\nState {state} since {state_changed_at}{deeplink}",
               # Several matches: header (count=) then one line per job (job_title=, company=, state=, deeplink=).
               "matches_header_template": "{count} jobs matched:",
               "matches_line_template": "• {job_title} — {company} — {state}{deeplink}",
               # Appended as {deeplink} only when the origin env is set; "" otherwise. Format with url=.
               "deeplink_template": "\n{url}",
               "no_match_reply_text": "Nothing matched that. Try a job link, title, or company.",
           },
   ```

   ⚠️ **Decision:** A single `deeplink_template` (`"\n{url}"`) serves both the one-match reply and each list line, so the link sits on its own line under the item it belongs to. When there is no origin, `{deeplink}` is `""`, so nothing about the link is left in the text (AC 10: "no `/jobs/detail/` text"). The link is a bare URL, not a Slack `<url|label>`, so the text contains the exact URL string AC 4 checks for.

3. In `src/utils/config.py`, replace the existing line

   ```python
   assert CONTACT_CONFIG["thread_response"] in ("threads_only", "always_no_share", "always_with_share"), CONTACT_CONFIG["thread_response"]
   ```

   with:

   ```python
   # AST-2072 / AST-2144: reply-placement vocabulary — global thread_response and per-command reply_placement.
   _CONTACT_THREAD_RESPONSE_MODES = ("threads_only", "always_no_share", "always_with_share")
   assert CONTACT_CONFIG["thread_response"] in _CONTACT_THREAD_RESPONSE_MODES, CONTACT_CONFIG["thread_response"]
   ```

4. In `src/utils/config.py`, replace the whole AST-2035 command-registry assert block. It starts at `# AST-2035: command registry shape;` and ends at `assert _cmd_id not in CONTACT_CONFIG["skills"], _cmd_id`. Replace it with:

   ```python
   # AST-2144: optional reply-text fields → placeholders each must carry when an entry declares it.
   _CONTACT_COMMAND_TEXT_FIELDS = {
       "ack_reply_template": ("{meteorite_id}",),
       "match_reply_template": ("{job_title}", "{created_at}", "{state}", "{state_changed_at}", "{deeplink}"),
       "matches_header_template": ("{count}",),
       "matches_line_template": ("{job_title}", "{company}", "{state}", "{deeplink}"),
       "deeplink_template": ("{url}",),
       "no_match_reply_text": (),
   }
   # Job-lookup reply fields travel together: a handler that formats one formats them all.
   _CONTACT_COMMAND_JOB_LOOKUP_FIELDS = frozenset(_CONTACT_COMMAND_TEXT_FIELDS) - {"ack_reply_template"}
   # AST-2035: command registry shape; ids are the bare token after "/" (no whitespace).
   assert isinstance(CONTACT_CONFIG["commands"], dict)
   for _cmd_id, _cmd_meta in CONTACT_CONFIG["commands"].items():
       assert isinstance(_cmd_id, str) and _cmd_id.split() == [_cmd_id] and not _cmd_id.startswith("/"), _cmd_id
       assert isinstance(_cmd_meta, dict), _cmd_id
       assert _cmd_meta.get("mode") in ("code", "agent"), _cmd_id
       for _field in ("handler", "description", "usage_reply_text"):
           assert isinstance(_cmd_meta.get(_field), str) and _cmd_meta[_field].strip(), (_cmd_id, _field)
       assert _cmd_meta["handler"].startswith("src.core.") and _cmd_meta["handler"].count(".") >= 3, _cmd_id
       # AST-2144: ack_reply_template is optional; any declared text field is non-empty and carries its placeholders.
       for _field, _needs in _CONTACT_COMMAND_TEXT_FIELDS.items():
           if _field in _cmd_meta:
               assert isinstance(_cmd_meta[_field], str) and _cmd_meta[_field].strip(), (_cmd_id, _field)
               assert all(_ph in _cmd_meta[_field] for _ph in _needs), (_cmd_id, _field)
       _lookup = _CONTACT_COMMAND_JOB_LOOKUP_FIELDS & _cmd_meta.keys()
       assert not _lookup or _lookup == _CONTACT_COMMAND_JOB_LOOKUP_FIELDS, (_cmd_id, sorted(_lookup))
       if "reply_placement" in _cmd_meta:
           assert _cmd_meta["reply_placement"] in _CONTACT_THREAD_RESPONSE_MODES, _cmd_id
       assert _cmd_id not in CONTACT_CONFIG["skills"], _cmd_id
   ```

   ⚠️ **Decision:** The "all-or-none" group assert on the five job-lookup fields exists so the handler can index `meta[...]` directly, with no `.get` fallbacks. The ticket asks for "shape asserts on entries that declare them", and this is the cheapest assert that makes a half-declared entry fail at import instead of at reply time.

5. In `src/utils/config.py`, in `_CONTACT_PINHOLE_HANDLERS`, add this row directly **after** the `"src.core.tracker.contact_task_get_job_by_pattern": "read job",` row:

   ```python
       "src.core.tracker.contact_command_check_status": "read job",
   ```

6. In `src/utils/config.py`, directly **after** the line `JOBS_DETAIL_ROUTE_PREFIX = "/jobs/detail"`, add:

   ```python
   # AST-2144: backend deeplink origin — https:// + os.environ.get(<this name>) + JOBS_DETAIL_ROUTE_PREFIX
   # + "/" + URL-encoded job id (same path as the job report modal's Copy Link). Unset/empty → no links.
   JOBS_DETAIL_ORIGIN_DOMAIN_ENV = "RAILWAY_PUBLIC_DOMAIN"
   assert isinstance(JOBS_DETAIL_ORIGIN_DOMAIN_ENV, str) and JOBS_DETAIL_ORIGIN_DOMAIN_ENV.strip()
   ```

   ⚠️ **Decision:** This is a module-level constant, not a `CONTACT_CONFIG` key. `CONTACT_CONFIG` is defined about 4,000 lines above `JOBS_DETAIL_ROUTE_PREFIX`, and the Scope places the contract "alongside `JOBS_DETAIL_ROUTE_PREFIX`". It is read with `os.environ.get`, not `os.environ[...]` (the `CONTACT_CONFIG["…_env"]` convention), because unset is a valid state (local dev).

7. Compile and lint: `python3 -m py_compile src/utils/config.py && ruff check src/utils/config.py`. Then run the Done-when checks, and run `pytest tests/component/core/test_contact.py -k TestAst2035ContactCommandIntercept -q` (read-only; it must stay green). Commit `code(AST-2151): stage 1 — check-status registry entry, asserts, pinhole, origin env`, then publish per build-child.

## Stage 2: Tracker handler `contact_command_check_status`

**Done when:** with a candidate in the local DB that owns at least one job, `python3 -c` calling `contact_command_check_status(<cid>, <a substring of one owned job's title>, source_id="x:1", thread_ts=None)` returns `ok=True` and a `reply_text`. That text has the title, the raw state, two `M/D HH:MM <label>` clocks, and (with `RAILWAY_PUBLIC_DOMAIN=astral.example` exported) `https://astral.example/jobs/detail/<id>`. A nonsense pattern returns `ok=False`, `error="unmatched_pattern"`, and `reply_text` equal to `no_match_reply_text`. With the env unset, the text has no link and one WARNING is logged. `rg -n "check-status|jobs/detail|RAILWAY_PUBLIC_DOMAIN|always_with_share" src/core/tracker.py` returns nothing.

1. In `src/core/tracker.py`, imports:
   - Add `import os` between `import json` and `import sqlite3`.
   - Add `from urllib.parse import quote` directly after `from typing import Any, Dict, List, Optional, Sequence, Tuple`.
   - In the `from src.utils.config import ( … )` list, add `CONTACT_CONFIG,` directly before `JOB_BUILD_ARTIFACT_CLEAR_KEYS,`. Add `JOBS_DETAIL_ORIGIN_DOMAIN_ENV,` and `JOBS_DETAIL_ROUTE_PREFIX,` directly after `JOB_STATES,`. Add `format_contact_timezone_clock,` directly after `dispatch_hop_label,`. Do not reorder the existing names.

2. In `src/core/tracker.py`, directly **after** the end of `contact_task_get_job_by_pattern` (its final `return row`) and **before** `def contact_task_get_job_data(`, add:

   ```python
   def _contact_job_clock(raw: Any, timezone_key: str) -> str:
       """Job TEXT timestamp (UTC ``YYYY-MM-DD HH:MM:SS`` or ISO) → contact clock; ``-`` when absent/unparseable."""
       log = get_logger(__name__)
       try:
           dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
       except ValueError:
           return "-"
       log.debug("Calling format_contact_timezone_clock: [dt=%s, timezone_key=%s]", dt.isoformat(), timezone_key)
       clock = format_contact_timezone_clock(dt, timezone_key)
       log.debug("Response from format_contact_timezone_clock: %s", clock)
       return clock


   def contact_command_check_status(
       candidate_id: str,
       payload: str,
       *,
       source_id: str,
       thread_ts: Optional[str] = None,
       debug: bool = False,
   ) -> dict:
       """CONTACT_CONFIG["commands"] code handler: terse status + deeplink for the sender's matching job(s) (AST-2144).

       Read-only. Returns {ok, meteorite_id (always None), error, reply_text}; Contact posts reply_text.
       """
       log = get_logger(__name__)
       # Own registry row, found by handler path: no command-id literal in src/core (AST-2144 AC 14).
       cmd_id, meta = next(
           (k, m) for k, m in CONTACT_CONFIG["commands"].items()
           if m["handler"] == f"{__name__}.contact_command_check_status"
       )
       cid = (candidate_id or "").strip()
       pat = (payload or "").strip()
       if not cid:
           # Contact only runs commands for bound senders; no reply_text → Contact's hear-ack path.
           return {"ok": False, "meteorite_id": None, "error": "no_candidate", "reply_text": None}

       # Same candidate-scoped matcher + ownership check as contact_task_get_job_by_pattern; no hydration.
       log.debug("Calling _match_jobs_by_pattern: [candidate_id=%s, pattern=%s]", cid, pat)
       jobs = [j for j in _match_jobs_by_pattern(cid, pat) if _job_owned_by_candidate(j, cid)]
       log.debug("Response from _match_jobs_by_pattern: %s", [j.get("astral_job_id") for j in jobs])
       if not jobs:
           return {
               "ok": False, "meteorite_id": None, "error": "unmatched_pattern",
               "reply_text": meta["no_match_reply_text"],
           }

       # Unset/empty origin → reply still goes out, just without links (one warning per reply).
       domain = (os.environ.get(JOBS_DETAIL_ORIGIN_DOMAIN_ENV) or "").strip()
       if not domain:
           log.warning(
               "%s | /%s deeplink missing — %s is unset\n  This reply goes out without job links",
               cid, cmd_id, JOBS_DETAIL_ORIGIN_DOMAIN_ENV,
           )
       # Local import: meteorite imports tracker at module level.
       from src.core.meteorite import _candidate_contact_timezone

       log.debug("Calling _candidate_contact_timezone: [candidate_id=%s]", cid)
       tz_key = _candidate_contact_timezone(cid)
       log.debug("Response from _candidate_contact_timezone: %s", tz_key)

       def _fields(job: Dict[str, Any]) -> Dict[str, str]:
           # Same path as the job report modal's Copy Link: origin + route prefix + "/" + encoded id.
           url = f"https://{domain}{JOBS_DETAIL_ROUTE_PREFIX}/{quote(str(job['astral_job_id']), safe='')}"
           return {
               "job_title": job.get("job_title") or "-",
               "company": job.get("company") or "-",
               "state": job.get("state") or "-",
               "created_at": _contact_job_clock(job.get("created_at"), tz_key),
               "state_changed_at": _contact_job_clock(job.get("state_changed_at"), tz_key),
               "deeplink": meta["deeplink_template"].format(url=url) if domain else "",
           }

       if len(jobs) == 1:
           reply = meta["match_reply_template"].format(**_fields(jobs[0]))
       else:
           log.debug("Beginning job status line loop on %s items", len(jobs))
           lines = [meta["matches_line_template"].format(**_fields(j)) for j in jobs]
           log.debug("End job status line loop after %s items", len(lines))
           reply = "\n".join([meta["matches_header_template"].format(count=len(jobs)), *lines])
       return {"ok": True, "meteorite_id": None, "error": None, "reply_text": reply}
   ```

   ⚠️ **Decision:** The ownership check runs as a filter over every match (`_job_owned_by_candidate`), not as a gate on a single match the way `contact_task_get_job_by_pattern` uses it. That is how one call can serve one, several, and none. **Inherited consequence:** `_job_owned_by_candidate` is `False` for a job whose `company` is empty. Some meteorite-landed jobs have `company_id = NULL` (AST-1701), so those jobs are filtered out and the reply is the no-match text. That is today's `get_job_by_pattern` behavior, and the ticket says to reuse that check unchanged. Changing it is out of scope here.

   ⚠️ **Decision:** A no-match logs **no** warning. Unlike `/add-job`'s soft-fail, this handler composes a reply for the miss, so the miss is the answer and not a failed item. The listen line already records `error`. The only warning this handler emits is the missing-origin one (AC 10: exactly one).

   ⚠️ **Decision:** `quote(id, safe="")` is the Python equivalent of the modal's `encodeURIComponent(jobId)`. They differ only on `!'()*`, which never appear in `astral_job_id` values.

   ⚠️ **Decision:** A missing or unparseable `created_at` / `state_changed_at` renders as `-` instead of raising. `format_contact_timezone_clock` raises on `None`, and a bad timestamp on one row should not cost the candidate the whole reply.

   Unused-by-design signature params: `source_id`, `thread_ts`, `debug`. These are the fixed command-handler signature from `patt.contact.command-intercept`. A read handler has no anchor to store, and debug goes through the `log_debug` ContextVar (`stat.logging.debug`), not the flag.

3. Compile and lint: `python3 -m py_compile src/core/tracker.py && ruff check src/core/tracker.py`. Then run the Done-when checks and the `rg` literal check. Commit `code(AST-2151): stage 2 — contact_command_check_status handler`, then publish per build-child.

## Test impact (for Betty)

- Parent AC 1–2 are config one-liners.
- The handler side of AC 4, 7, 8, 9, and 10 can be checked by calling `contact_command_check_status` directly and asserting on `reply_text` / `ok` / `error` and on `caplog` WARNING count. End-to-end `post_message` assertions need #2.
- `TestAst2035ContactCommandIntercept` must pass unmodified. Its registry shape is now enforced by the relaxed assert loop.

## Estimate

Confirm Chuckles estimate: 2 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2151
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2144/AST-2151-check-status-registry-handler` @ `5bda36039d471ab68d4ac667540206379cba1abc`

## Canon scores

patt.contact.command-intercept | B | | Registry row + `src.core.tracker` handler, handler-path registry lookup (no command-id literals in core), templates/placement in config; `reply_text` / optional ack / placement defer `_run_contact_command` to sibling #2 per parent change request
stat.logging.debug | A | |
stat.logging.warning | A | | Stage 2: one WARNING when origin env unset, names candidate + command + env and product consequence (no warning on composed no-match)

## Traceability

AC1 → Stage 1; AC2 → Stage 1 step 5; AC3 → N/A E2E until #2 — Stage 2 direct handler calls + Test impact; AC4 → Stage 2 several-match branch; AC5 → Stage 2 ownership filter on matcher results; AC6 → N/A posting/hear-ack until #2 — Stage 2 `unmatched_pattern` + `reply_text`; AC7 → Stage 2 unset-origin path + caplog in Done-when.

### discuss — Ticket AC 3–6 vs handler-only verification

- **Location:** Child Description AC 3–6 (`handle_slack_event` / `post_message`); plan Boundaries + Test impact.
- **Finding:** Linear AC text still reads end-to-end; the plan correctly limits this child to composed `reply_text` and points Betty at direct handler + caplog until Hedy (#2).
- **Recommendation:** Keep build/tests on the plan; optional ticket-description tidy is Chuckles/Susan, not a plan rewrite.

### discuss — In-force pattern vs epic widening

- **Location:** Parent Architectural definition (Archie change request on `patt.contact.command-intercept`); plan Contract with sibling #2 and Stage 1 commands comment.
- **Finding:** Corpus arc still describes mandatory `ack_reply_template` and code-mode miss → no post; this child implements the widened contract on the handler/config side only.
- **Recommendation:** Proceed on plan; pattern amendment stays Archie/epic scope (#2 completes runner side).

### discuss — Canon Scope gap (not scored)

- **Location:** Plan Stage 1 (`JOBS_DETAIL_ORIGIN_DOMAIN_ENV`, registry asserts) and `astral.layers.import-direction` territory.
- **Finding:** `astral.config.config-source-of-truth` and `astral.layers.import-direction` plainly touch this footprint but are absent from the child Citations list.
- **Recommendation:** Archie may amend parent Canon Scope at Discussion if those ids should ride on #1; Joan did not grade them.

### acceptable — Interim `KeyError` until #2

- **Location:** Scope gate “Interim behavior until #2 lands”.
- **Finding:** `/check-status` without `ack_reply_template` can raise under today’s `_run_contact_command`; documented, ftr-only, replaced by sibling.
- **Recommendation:** None for plan approval.

### acceptable — No formal `## Self-assessment`

- **Location:** Plan ends at Estimate confirm.
- **Finding:** R6 honesty checklist has no dedicated block; staged literals, `rg` gate, and inherited-ownership note are specific enough.
- **Recommendation:** Optional; not blocking.

**R6 (summary):** Definition fidelity for child #1: only `config.py` and `tracker.py`; no `contact.py`. Reuses matcher/ownership without new query. Stages cover registry, pinhole, origin contract, and handler branches (one / several / none / no origin). No scope creep into sibling posting. No `fix-now` findings.

context_tokens≈42000


## Review

- **Branch:** `origin/sub/AST-2144/AST-2151-check-status-registry-handler`
- **Stage 1:** `f01360949` — `check-status` registry entry, optional-text/placement asserts, pinhole row, `JOBS_DETAIL_ORIGIN_DOMAIN_ENV`
- **Stage 2:** `3c80c683d` — `contact_command_check_status` handler + `_contact_job_clock`
- **Build notes:** Two files (`src/utils/config.py`, `src/core/tracker.py`), as planned. `py_compile` is clean on both. Ruff on `config.py` is unchanged (102 before and after). On `tracker.py` there are 3 new UP006/UP045 hits (`Dict[...]` ×2, `Optional[str]`). They match the module's annotation style and the plan's exact code, so they were left as written. There are no F-class (real error) hits. Parent AC 1 prints `code always_with_share` and AC 2 prints `read job`. Removing `{deeplink}` from `match_reply_template` fails the import with `AssertionError: ('check-status', 'match_reply_template')`. `TestAst2035ContactCommandIntercept` passes (22 tests; run from the `astral/.venv` interpreter, because system python lacks `asyncpg`). The AC 14 `rg` over `src/core` returns only the existing `always_with_share` lines in `_contact_reply_placement`. Smoke run with the matcher, ownership, and timezone stubbed (`America/Los_Angeles`), job id `acme_com:j 1`:
  - One match gives title, `Received 10/1 08:04 Pacific`, `State PASSED_LIKE since 10/10 02:30 Pacific`, and `https://astral.example/jobs/detail/acme_com%3Aj%201`.
  - Two matches give `2 jobs matched:` plus two lines, each with its own link. The other candidate's same-title job is absent.
  - No match gives `ok=False`, `unmatched_pattern`, and the no-match text, with 0 warnings.
  - Origin unset gives the same one-match text without the link, plus exactly 1 WARNING (`cand1 | /check-status deeplink missing — RAILWAY_PUBLIC_DOMAIN is unset`).
  - Empty candidate gives `no_candidate` with `reply_text=None`.
  - A `None` or garbage timestamp renders `-`.
- **Spawn-prompt note:** the prompt's `--ftr AST-2144` doesn't exist on origin. The registry's `parent_ftr` is `ftr/AST-2144-check-status` (at `c4f0d3a59`, already this sub's base). The sync and `validate-sub-log` were re-run with that segment and both returned ok.


## Radia review

[code-rubric]
**Ticket:** AST-2151
**Publish ref:** `cac60b36ebcb0d5b32734335df0a76cf5de9f21e` (`origin/sub/AST-2144/AST-2151-check-status-registry-handler`)
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.contact.command-intercept | B | | |
| stat.logging.debug | A | | |
| stat.logging.warning | A | | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Location:** Linear Description AC 3–6 (`handle_slack_event` / `post_message`) vs child Boundaries and `TestAst2151ContactCommandCheckStatus`.
- **Finding:** Ticket AC text still describes end-to-end Slack posting; the diff correctly implements registry + handler `reply_text` only and tests the handler directly (plus config import asserts). E2E posting remains sibling #2.
- **Decision @susan:** Whether to tighten Linear AC wording on AST-2151 for handler-only verification.
- **Default:** Leave AC text as-is; keep verification on handler tests and config one-liners until #2 lands.

- **Location:** In-force `patt.contact.command-intercept` corpus (mandatory `ack_reply_template`, `{ok, meteorite_id, error}` only, `code` posts ack on `ok`) vs `check-status` entry (no ack, `reply_text`, `reply_placement`) and unchanged `src/core/contact.py`.
- **Finding:** Product matches the epic/plan widening and parent change-request note; corpus arc is not yet amended. Interim `KeyError` on successful `/check-status` under today’s `_run_contact_command` is documented on the issue doc.
- **Decision @susan:** Whether interim ftr behavior needs a user-visible note before #2 merges.
- **Default:** Proceed; resolve-child does not expand scope into `contact.py`.

### advisory

- **Canon Scope (off-list, not scored):** `JOBS_DETAIL_ORIGIN_DOMAIN_ENV`, extended `CONTACT_CONFIG["commands"]` asserts, and the in-handler `from src.core.meteorite import _candidate_contact_timezone` sit in territory Joan flagged for `astral.config.config-source-of-truth` / `astral.layers.import-direction`. They are absent from this child’s frozen Citations list; parent Canon Scope amendment is Archie’s lane if those ids should ride on #1.
- **Interim runner:** Until sibling #2, a successful handler result without `ack_reply_template` can raise under current `_run_contact_command`; plan documents ftr-only behavior.
- **Tests/bible:** `tests/component/core/test_tracker.py`, `tests/component/utils/test_config.py`, and bible § AST-2151 entries belong to this ticket (Betty), not sibling product carry.

## What’s solid

- Registry row, relaxed optional-ack asserts, job-lookup all-or-none group, pinhole `read job`, and origin env contract match Stage 1 and parent AC 1–2.
- Handler resolves its registry row by handler path (no `/check-status` or placement literals in `src/core/tracker.py`); reuses `_match_jobs_by_pattern` + `_job_owned_by_candidate` read-only; branches for one / several / none / missing origin match plan and parent handler ACs.
- Debug loop begin/end and Calling/Response pairs on matcher, timezone, and `format_contact_timezone_clock`; single WARNING on missing origin with candidate, command id, env name, and product consequence; no warning on composed no-match.
- Component tests cover AC-shaped handler behavior and spliced import-time assert probes.

## Recommended actions (for issue doc only — not executed by Radia)

- Chuckles: append this artifact, `docs(AST-2151): Radia review — clean`, push publish ref, post slim upshot `--as radia`, move to **Review Posted**.
- If Susan wants Linear AC 3–6 clarified, Chuckles can edit Description in a separate pass (optional).
- Archie/parent: consider Canon Scope ids for config SSOT / import-direction if those should be explicit on child tickets like this.

context_tokens≈28000


## Resolution

2026-10-12, against Radia review `30d0dd808` (CLEAN, no fix-now). No product change.

- **Discuss: AC 3–6 wording.** Took Radia's default: the Linear AC text is left as-is. Verification stays on the handler tests and the config one-liners until sibling #2 lands. Susan can reverse this by having Chuckles tighten the Description.
- **Discuss: interim ftr behavior / pattern corpus.** Took Radia's default: proceed. `src/core/contact.py` is not in this ticket's scope. The interim `KeyError` on a successful `/check-status` stays documented under the Scope gate and is replaced by #2. The `patt.contact.command-intercept` amendment stays with Archie.
- **Advisory: off-list Canon Scope ids** (`astral.config.config-source-of-truth`, `astral.layers.import-direction`). These are the parent Canon Scope's lane (Archie). No change here.
- **Advisory: interim runner, tests/bible ownership.** Already documented; nothing to do.
- **Re-verified on the resolve tip** (after `sync(dev)` brought in AST-2149's one-line `gather_stagger_seconds` config add): `py_compile` is clean, and Betty's manifest item 1 gives 54 passed.

## Bug: AST-2169 — Estelle job reads own meteorite jobs by candidate_id, not null company

**Linear:** [AST-2169](https://linear.app/astralcareermatch/issue/AST-2169) (fix child of orphaned bug [AST-2167](https://linear.app/astralcareermatch/issue/AST-2167))
**Publish ref:** `origin/sub/AST-2167/AST-2169-check-status-ownership-candidate-id`
**Reverses:** the **Inherited consequence** under this doc's Stage 2 ⚠️ Decision (null-`company_id` jobs filtered to the no-match text). Nothing else in Stages 1–2 changes.

### As-is

`@Estelle /check-status <job link>` returns `no_match_reply_text` for a job that exists and belongs to the sender when that job has no company. `_match_jobs_by_pattern` finds it (`list_jobs(candidate_id=cid)` returns it, and the link matches `job_link`), and then `_job_owned_by_candidate` drops it. The same helper makes `get_job_by_pattern` return `refused_cross_candidate` and `get_job_data` return `refused_cross_candidate` for the same job.

### To-be

All three Estelle job reads (`contact_command_check_status`, `contact_task_get_job_by_pattern`, `contact_task_get_job_data`) treat a job as the sender's when the job row's own `candidate_id` equals the sender's candidate id. `company` / `company_id` can be NULL or set, and neither affects the result. A job whose `candidate_id` is another candidate stays invisible on all three paths.

### Repro

Live: Somerset sends `@Estelle /check-status https://www.dice.com/job-detail/6889a7c5-d9c5-49e8-9598-ddaf1142df0a`. The target is job `6775db61-…`, state `CANDIDATE_SKIPPED`, meteorite-sourced, `company_id` NULL. Today Somerset gets the no-match reply. After the fix, Somerset gets the single-match reply with state `CANDIDATE_SKIPPED`.

Fixture (component, same stubbing style as `TestAst2151ContactCommandCheckStatus._stub`): `list_jobs` returns

```python
{"astral_job_id": "m1", "candidate_id": "c1", "company": None,
 "job_title": "Platform Engineer", "job_link": "https://www.dice.com/job-detail/x1",
 "state": "CANDIDATE_SKIPPED", "created_at": "2026-10-01 15:04:00",
 "state_changed_at": "2026-10-10T09:30:00Z"}
```

`contact_command_check_status("c1", "https://www.dice.com/job-detail/x1", source_id="C1:1.0")` → today `error == "unmatched_pattern"`; to-be `ok is True` with the single-match reply. Do the same with `get_job` returning that row: `contact_task_get_job_data("c1", "m1")` → today `refused_cross_candidate`; to-be `ok is True`. With `"candidate_id": "c2"` on the row, `get_job_data` still refuses.

### Root cause

`_job_owned_by_candidate` (`src/core/tracker.py`, from AST-1518) resolves ownership as `job["company"]` → `get_company(short_name)` → `company.candidate_id`, and returns `False` when `company` is blank. AST-1518 did this deliberately because job rows had no `candidate_id` at the time ("job rows do **not** carry `candidate_id`" in its Stage 1 step 3). Two later changes made that wrong:

- **AST-1598** added `job.candidate_id`. It is backfilled from `company.candidate_id`, required on every `save_job` insert, returned on every row dict (`SELECT *`), and it is the only scope key for `list_jobs` / `count_jobs` / `claim_job_batch`. `_candidate_id_for_job` in the same module already prefers it.
- **AST-1701** made the job's company link nullable. Meteorite-landed jobs have `company_id = NULL` and set `source_entity_id` instead, so the `company` compat alias on the row is `None`.

The combination means a meteorite job is in the sender's `list_jobs` scope, but the ownership check filters it out because the job has no company.

### Proposed change

**`src/core/tracker.py` only. Function `_job_owned_by_candidate(job, cid)`.** Signature, name, and position stay the same, and no new function is added. Replace the body so ownership comes from the job row alone:

```python
def _job_owned_by_candidate(job: Dict[str, Any], cid: str) -> bool:
    """True when the job row's own candidate_id matches cid (AST-1598 scope key; company may be NULL — AST-1701)."""
    owner = job.get("candidate_id")
    return isinstance(owner, str) and bool(owner.strip()) and owner.strip() == cid
```

- Remove the `company` → `get_company` lookup from this helper. `get_company` itself stays, because other callers use it.
- Do not edit any of the three callers. `contact_command_check_status` keeps it as a filter over every match, and `contact_task_get_job_by_pattern` / `contact_task_get_job_data` keep it as a `refused_cross_candidate` gate. Error keys and reply templates stay the same.
- Do not edit the AST-2151 handler comment "Same candidate-scoped matcher + ownership check as contact_task_get_job_by_pattern". It stays true.

⚠️ **Decision: no company fallback for a blank `job.candidate_id`.** AST-2167 left this to plan-fix ("if any exist"). It is dropped for three reasons:

1. A row's `candidate_id` can only be blank if the row predates AST-1598 *and* its company had no owner at backfill time. For that row the old company lookup also returns no owner, so a fallback would almost never flip a result.
2. On the two pattern paths, every row already comes from `list_jobs(candidate_id=cid)`, which filters on `job.candidate_id = cid`. A blank row can never reach them.
3. A single source of truth is less to reason about than a two-tier one.

**Alternative, if fix-board or Susan prefers it:** mirror `_candidate_id_for_job` inline. Check `candidate_id` first, and fall back to `company` → `get_company` only when `candidate_id` is blank. That is about 6 more lines, and it keeps today's company-only test fixtures green (see Blast radius). Do not *call* `_candidate_id_for_job`: it takes an id and re-reads the row through `database.get_job`, which would add one DB read per match to `/check-status`, and AST-2151 promised "no new query".

### Blast radius

- **Callers (behavior change, no code change):** `contact_command_check_status`, `contact_task_get_job_by_pattern`, `contact_task_get_job_data`. No other caller exists (grep on `_job_owned_by_candidate` finds these three in `src/`).
- **Security:** `get_job_data` is the only path where the gate is not redundant, because it loads by arbitrary id through `get_job`. A foreign id is still refused, since its row's `candidate_id` is the foreign candidate. AST-1518's warning ("a foreign `astral_job_id` would otherwise succeed") was about the column being *absent*, and comparing it to `cid` does not reopen that hole.
- **Tests (Betty's call at fix-board; noted here, not touched):** `tests/component/core/test_tracker.py`. The AST-1518 job-read tests in `TestAst1518ContactTaskReads` (`_job()` fixture, about line 2271, used by `test_contact_task_get_job_by_pattern_happy_and_errors` and `test_contact_task_get_job_data_ownership`) and the AST-2151 `/check-status` tests in `TestAst2151ContactCommandCheckStatus` (`_job()` / `_stub(..., owners)`, about line 2405) build job rows **without** `candidate_id` and drive ownership by stubbing `get_company`. Under the Proposed change, their happy paths turn red, and the cross-candidate case needs to vary `job["candidate_id"]` instead of the company owner. `docs/test-bible/core/tracker.md` (about line 898) describes the handler as using `_job_owned_by_candidate`, and the name stays the same. Expect **TESTS: REVISE** with fixture updates plus a null-company repro case.
- **Docs:** AST-1518 (`docs/features/contact/ast-1518-…md` Stage 1 step 3) and AST-1563 (`docs/features/tracker/ast-1563-audit-of-get-job-data.md`) describe the old company-based rule. They are historical plan docs and are not patched. This block records the change.
- **Not touched:** `_match_jobs_by_pattern`, `list_jobs` scoping, `_candidate_id_for_job`, reply templates, `CONTACT_CONFIG`, `src/core/contact.py`, schema, backfill.

### What must still hold

- AST-2151 handler ACs: one / several / none / no-origin branches. Registry row found by handler path. Read-only (no `save_job` / `delete_job` / `save_artifact`). Single WARNING on a missing origin. `reply_text` contract with sibling #2.
- AST-1518 contracts: `get_job_by_pattern` refuses ambiguous and unmatched patterns. `get_job_data` refuses `refused_cross_candidate` for a job owned by another candidate and returns `not_found` for a missing id. Hydration (`agent_story`) is unchanged.
- An employer-sourced job (company set) owned by the sender behaves exactly as today. Its `candidate_id` was backfilled from that company's owner and set on insert, so both rules agree.
- No new DB reads per match. The helper stays a pure function of the row it is given.


## Joan fix-board — AST-2169

[board-joan]  CANON: OK

AST-2169 board-joan done — CANON: OK.

**Rationale:** The plan-fix change is a one-helper body swap in `src/core/tracker.py` (`_job_owned_by_candidate`): ownership follows `job.candidate_id`, matching how `list_jobs` / `count_jobs` already scope jobs (AST-1598) and how nullable `company_id` meteorite rows behave (AST-1701). No in-force statute or active pattern (`patt.contact.command-intercept`, artifact scope patterns, layer/import rules) encodes the old company→`get_company` gate; that rule lived only in historical plan docs (AST-1518), which the patch explicitly leaves unpatched. Security intent (`refused_cross_candidate` on foreign ids via `get_job`) is preserved. No new carve-out, precedent, or corpus amendment is required for this fix—only product code (and Betty’s tests).

**Chuckles routing (orphaned bug-fix):** Betty TESTS: REVISE → sibling test gap child; Joan CANON: OK. AST-2169 proceeds to make-fix on product only.
