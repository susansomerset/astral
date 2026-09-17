# AST-1703 — Email breadcrumb on meteorite.link (forward peel + timezone clock)

**Linear:** [AST-1703](https://linear.app/astralcareermatch/issue/AST-1703/email-breadcrumb-on-meteoritelink-forward-peel-timezone-clock)  
**Parent:** [AST-1640](https://linear.app/astralcareermatch/issue/AST-1640/job-source-entity-parent-meteoritecompany-candidate-facing-link) — Job source_entity parent (meteorite|company) + candidate-facing link  
**Publish ref:** `sub/AST-1640/AST-1703-email-breadcrumb-on-meteorite-link-forward-peel-timezone-clock`

Authors the candidate-facing no-URL email breadcrumb onto `meteorite.link` for `single_jd_no_link` / `multi_jd_inline` email ingress: Ruth peels inner From/To on forwards and returns from/to/sent-at; Python formats the clock in `contact.timezone` via AST-1701 helpers and writes the non-http string. Sibling #2 inherits that link onto `job.job_link`; this ticket does not re-own parent columns, bot-block append, or Job Detail.

## UAT fitness

- **AC restored:** Parent AC6 / child AC6 — After land, `job.job_link` equals `meteorite.link` for that row’s linked job (breadcrumb authored here, inherited by #2). Fail: non-http breadcrumb missing on `meteorite.link` for no-URL email outcomes. Parent Functional scope item 6 format: `From:<email> M/D H:MM <timezone> To:<email>` (peel inner headers on forward; Python formats clock in `contact.timezone`).
- **Correct outcome:** For email text outcomes, each inserted meteorite row has a non-http `link` breadcrumb in that shape before land; after #2 land inherit, `job.job_link` matches that same string so the candidate can find the listing again.
- **Sibling check:** #1 helpers (`JOB_LINK_BREADCRUMB_FORMAT`, `format_contact_timezone_clock`, `format_job_link_breadcrumb`) remain the only format SSOT — this ticket only calls them. #2 still owns inherit / bot-block / append and must not be rewritten. #4 Job Detail http(s)-only href still applies to inherited breadcrumbs. Verified by: no second format string in `meteorite.py`; `grep` shows no `ensure`/parent/inherit edits beyond setting `meteorite.link` on text email rows; `consult.py` untouched.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Writing envelope From/To without Ruth peel “fixes” direct-send mail but fails forwarded listings (envelope From is the candidate). Synthesizing `email-<mid>` / `source_ref` as the link reopens the retired source-ref path and contradicts parent locked decisions. Filtering inherit to http(s)-only in this ticket would steal #2’s AC and hide breadcrumbs from `job.job_link`.

## Scope gate

Ticket **## Scope** (amended after `[scope-gate]`):

- `src/core/meteorite.py` — classify/land path that authors non-http `meteorite.link` breadcrumbs (forward peel + timezone clock); does not re-own parent/inherit/append writes from #2
- `data/admin/agent_task.json` (`task_key=stage_meteorite`) — instruct peel of inner From/To on forwards; require returning `from_email` / `to_email` / `sent_at` for text outcomes (`source_ref` stays unused; breadcrumb lands on `meteorite.link`)
- `src/utils/config.py` — call AST-1701 breadcrumb format / timezone helpers (no second SSOT); extend `TASK_CONFIG["stage_meteorite"]["response_schema"]` so those fields are accepted (prefer on `jobs` `items_schema` so `invoke_stage_meteorite` returns them without touching `consult.py`)

Technical: breadcrumb writer for text outcomes — agent returns from / to / sent-at; Python formats clock in `contact.timezone`; forwarded mail uses inner headers; `source_ref` stays unused.

All Files Changed / Stages below stay inside that set. Out of scope: `tracker.py` / land inherit / bot-block (#2), `consult.py`, Job Detail / jobs API (#4), Slack/paste breadcrumb authorship.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `from_email` / `to_email` / `sent_at` to `TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]` (required False at schema level; runtime require for email text outcomes in meteorite) | utils |
| `data/admin/agent_task.json` | Update `stage_meteorite` cache + user prompts: peel inner headers on forwards; return from/to/sent_at on text outcomes; stop promising source-ref synthesis for `job_link`/`company_job_id` | data/admin |
| `src/core/meteorite.py` | Author breadcrumb onto `meteorite.link` for email + `text_source_ref_outcomes` via AST-1701 helpers + candidate `contact.timezone`; leave non-email text rows with `link=None` | core |

## Stage 1: Schema + Ruth prompt (agent returns from / to / sent-at)

**Done when:** `TASK_CONFIG["stage_meteorite"]` accepts `from_email`, `to_email`, `sent_at` on each jobs item; `data/admin/agent_task.json` for `task_key=stage_meteorite` instructs forward peel and requires those fields on text outcomes; no second breadcrumb format string added in config. `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, inside `TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]`, add three optional string fields (same shape as existing `job_title` / `jd_text` entries):

```python
"from_email": {"type": "str", "required": False},
"to_email": {"type": "str", "required": False},
"sent_at": {"type": "str", "required": False},
```

Do **not** add a second `JOB_LINK_BREADCRUMB_FORMAT` / clock-label map. Do **not** change `STAGE_METEORITE_CONFIG` outcome partitions.

2. In `data/admin/agent_task.json`, find the object with `"task_key": "stage_meteorite"` and edit prompts as follows:

   a. **`cache_prompt` — outcome 1 (`single_jd_no_link`):** Replace the sentence that says `job_link` / `company_job_id` will be source-refs (caller synthesizes) with: leave `job_link` / `company_job_id` empty/omitted; put visible JD text in `jd_text`; set `from_email`, `to_email`, and `sent_at` (see HEADER FIELDS below).

   b. **`cache_prompt` — outcome 3 (`multi_jd_inline`):** Replace “source-ref identity” wording with: one jobs item per JD with `jd_text` per item; leave `job_link` / `company_job_id` empty/omitted; set the **same** `from_email` / `to_email` / `sent_at` on every jobs item (one email → one breadcrumb identity).

   c. **`cache_prompt` — SOURCE-REF RULES section:** Retitle/repurpose to **HEADER / BREADCRUMB FIELDS** (keep a short “do not invent UUIDs / do not use company homepages as job_link for text outcomes” line). Add explicit rules:

   - For `single_jd_no_link` and `multi_jd_inline`: always return bare email addresses in `from_email` and `to_email` (no `From:` / `To:` prefixes), and `sent_at` as the original send time string (prefer ISO-8601; RFC 2822 Date-header text is OK).
   - **Direct send** to the platform: use the envelope From / To / Date shown in the blob headers.
   - **Forward:** when the candidate forwarded the listing, envelope From is the candidate — peel the **inner** original From / To / Date from the forwarded block in CONTENT; do not use the candidate’s address as `from_email`.
   - URL outcomes (`single_jd_with_more`, `link_list`): keep returning http(s) `job_link` as today; `from_email` / `to_email` / `sent_at` optional (Python ignores them for URL rows).
   - Skip outcomes: still `jobs: []`.

   d. **`user_prompt`:** Extend to mention returning `from_email`, `to_email`, `sent_at` on text-outcome jobs items in addition to `outcome` + `jobs`.

⚠️ **Decision:** Fields live on each **jobs** item (not top-level response) so existing `invoke_stage_meteorite` in `consult.py` already surfaces them via `jobs` — no consult edit (matches Scope). Same values duplicated on every `multi_jd_inline` item is intentional.

## Stage 2: Author breadcrumb on email text meteorite rows

**Done when:** For `source_kind == "email"` and outcome in `STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]`, every dict passed to `insert_meteorite_rows` has non-empty `link` equal to `format_job_link_breadcrumb(from_email, to_email, clock)` where `clock = format_contact_timezone_clock(parsed_sent_at, contact.timezone)`; shape matches `From:<email> M/D H:MM <label> To:<email>`; `source_ref` is never written. Non-email text outcomes still insert with `link=None`. URL scrape outcomes unchanged. `run_stage_meteorite` / `run_land_meteorite` / tracker inherit paths are **not** rewritten. `python3 -m py_compile src/core/meteorite.py` succeeds. Manual check: after map, `link` does not start with `http://` or `https://` and does not start with `email-`.

1. In `src/core/meteorite.py` imports from `src.utils.config`, add `format_contact_timezone_clock` and `format_job_link_breadcrumb` (helpers already shipped by AST-1701).

2. Add a private helper near `_map_classify_jobs_to_meteorite_rows` (name is free; e.g. `_email_breadcrumb_link`):

```python
def _email_breadcrumb_link(
    *,
    from_email: str,
    to_email: str,
    sent_at: str,
    timezone_key: str,
) -> str:
```

   Behavior (literal):

   - Strip `from_email` / `to_email` / `sent_at`; if any blank → raise `ValueError` with a short reason (caller turns into map error).
   - Parse `sent_at` to aware UTC `datetime`:
     - Try `datetime.fromisoformat(sent_at.replace("Z", "+00:00"))`.
     - Else try `email.utils.parsedate_to_datetime(sent_at)` (import `parsedate_to_datetime` from `email.utils` at module top).
     - If both fail → raise `ValueError("unparseable sent_at")`.
     - If naive after parse → treat as UTC (`replace(tzinfo=timezone.utc)`).
   - `clock = format_contact_timezone_clock(dt, timezone_key)` — pass stripped timezone key (empty OK → helper’s UTC path).
   - Return `format_job_link_breadcrumb(from_email, to_email, clock)`.
   - `logger.debug` callee in/out around the two format helpers per `stat.logging.debug` (param keys/values in; full breadcrumb string out). No `print`. No `logger.info("[DEBUG] …")`.

3. Add a tiny timezone reader used only here (keep in `meteorite.py` — do not open `candidate.py`):

```python
def _candidate_contact_timezone(candidate_id: str) -> str:
```

   - `cand = get_candidate(candidate_id)` (already imported).
   - Resolve contact dict the same way `_estelle…` / existing meteorite code does: `cd = cand.get("candidate_data") if isinstance(cand.get("candidate_data"), dict) else {}` then `contact = cd.get("contact") if isinstance(cd.get("contact"), dict) else {}`; if that contact is empty, also try top-level `cand.get("contact")` when it is a dict.
   - Return `(contact.get("timezone") or "").strip()` — never invent a zone.

4. Change `_map_classify_jobs_to_meteorite_rows` signature to accept `timezone_key: str = ""` (keyword-only after the existing `*` kwargs is fine — add as `timezone_key: str = ""` next to `source_id`).

   In the `text_source_ref_outcomes` branch, **replace** `"link": None` with:

   - If `source_kind == "email"`: for each job dict, read `from_email` / `to_email` / `sent_at` as stripped strings (non-str → `""`). Call `_email_breadcrumb_link(...)`. On `ValueError`, return `[], str(exc)` (same fail shape as missing `jd_text`). Set `"link": breadcrumb` on the row dict.
   - Else (slack/paste): keep `"link": None` (parent: Slack/paste breadcrumbs out of this ticket).

   Do **not** write `source_ref`. Do **not** synthesize `email-<mid>`.

5. In `ingest_candidate_email_message`, where `_map_classify_jobs_to_meteorite_rows` is called, pass `timezone_key=_candidate_contact_timezone(cid)`. Candidate is already loaded earlier as `cand` — you may pass timezone from that raft instead of a second `get_candidate` inside the helper when `cand` is in hand; either way is fine as long as the key is `contact.timezone`.

6. **Logging (canon):** When a breadcrumb is successfully authored for an inserted row, after `insert_meteorite_rows` (or once per authored row before insert — prefer once per row id after insert when ids exist), emit one `stat.logging.info.entity` line using the existing `_meteorite_state_info` / `_entity_info` style already in this file — entity id = meteorite row id, type `meteorite`, event naming the breadcrumb write (e.g. detail `link breadcrumb` or reuse state info only if a state change already covers it). Do **not** put the full breadcrumb string on an always-on info line if that would dump PII-heavy content beyond id-pipe norms; prefer info that the link was authored, and `logger.debug` the full breadcrumb string. Follow existing `_meteorite_state_info` patterns for NEW inserts (already logged) — if NEW state info already fires, add only `logger.debug` for the breadcrumb body and skip a second info line.

7. Do **not** edit `run_stage_meteorite` text branch beyond what is required if a row somehow reaches stage with email text outcome and empty `link`: optional safety — if `outcome in text_source_ref_outcomes` and `source_kind == "email"` and `link` blank, ERROR with `missing breadcrumb link` rather than READY. Prefer authorship at map/insert so this branch rarely trips; include the safety check only if it is ≤10 lines and uses data already on the row (no second Ruth call). If the row has no from/to/sent_at stored (they are not columns), **skip** stage backfill — authorship at insert is the SoT; stage safety then is: email + text outcome + blank link → ERROR `missing breadcrumb link`.

⚠️ **Decision:** Authorship at `_map_classify_jobs_to_meteorite_rows` (insert time) so #2 land inherit sees `meteorite.link` already set — matches sibling #2 plan (“#3 authors them”). No consult changes. Slack/paste text outcomes stay `link=None`.

## Estimate

Confirm Chuckles estimate: 3 — agree

One core authorship path + schema/prompt wiring; helpers already from #1; no schema migration. Fits a 3.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1640/AST-1703-email-breadcrumb-on-meteorite-link-forward-peel-timezone-clock`.
- Do not edit `consult.py`, `tracker.py`, land inherit/bot-block append, or Job Detail.
- Do not invent a second breadcrumb format SSOT.
- When a step is ambiguous or the codebase drifted — stop, comment on the **parent** issue with the Stage blocked template, wait.

## AC traceability

- Child AC6 / Parent AC6 (breadcrumb on `meteorite.link` for no-URL email; inherit by #2) → Stage 2.
- Parent Functional scope item 6 format + forward peel + `contact.timezone` clock → Stage 1 (agent peel) + Stage 2 (Python format).
- `source_ref` unused → Stage 1 prompt + Stage 2 map (no synthesis).

## Joan validate

[plan-rubric]
**Ticket:** AST-1703
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1640/AST-1703-email-breadcrumb-on-meteorite-link-forward-peel-timezone-clock` @ `76def5139ed280f45a51005b4960c8c36ba51c5e`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.entity | A | | Step 6 keeps id-pipe info; full breadcrumb on `logger.debug` only — no PII dump on always-on info |
| stat.logging.debug | A | | `_email_breadcrumb_link` requires ungated callee in/out around AST-1701 format helpers |

## Traceability

AC6 → Stage 2 (`_map_classify_jobs_to_meteorite_rows` authors non-http `meteorite.link` for email + `text_source_ref_outcomes`; #2 inherit out of scope). Parent Functional scope item 6 (format, forward peel, `contact.timezone` clock) → Stage 1 (Ruth peel + schema fields) + Stage 2 (Python format via #1 helpers). `source_ref` unused → Stage 1 prompt + Stage 2 map (no synthesis). Parent AC1–5, 7–9 N/A — siblings #1–2 / #4.

## Findings

### discuss

- **Location:** Linear Description `## Scope` vs plan `## Scope gate`
- **Finding:** Ticket body still lists only `meteorite.py` + narrow `config.py` call; plan (post `[scope-gate]`) correctly adds `data/admin/agent_task.json` and `TASK_CONFIG` schema wiring. Plan is self-consistent; Linear partition text is stale.
- **Recommendation:** Chuckles syncs Linear `## Scope` to match amended plan; implementer follows plan Scope gate.

- **Location:** Stage 2 step 7 — optional `run_stage_meteorite` safety
- **Finding:** Authorship at insert is the SoT; optional stage backfill for blank email `link` is defensive only. Omitting it does not block AC6 if map-time authorship is correct.
- **Recommendation:** Include the ≤10-line safety if cheap; not required for plan approval.

- **Location:** Child AC6 wording / UAT fitness
- **Finding:** End-to-end `job.job_link == meteorite.link` after land requires #2 inherit; this ticket’s concrete fail test is breadcrumb present on `meteorite.link` at insert — honestly scoped.
- **Recommendation:** None; coordinate UAT with #2 on epic line.

### acceptable

- **Location:** `[scope-gate]` thread
- **Finding:** Prior gate correctly identified missing `agent_task.json` + schema fields; republished plan at `76def513` addresses envelope-only From/To and source-ref contradiction.
- **Recommendation:** None.

- **Location:** Stage 1 — jobs `items_schema` placement
- **Finding:** Fields on each jobs item flow through `invoke_stage_meteorite` without `consult.py` edits — matches Technical scope and current `consult.py` passthrough.
- **Recommendation:** None.

- **Location:** Stage 2 — `source_kind == "email"` branch only
- **Finding:** `_map_classify_jobs_to_meteorite_rows` has a single caller (`ingest_candidate_email_message`); slack/paste stay `link=None` per parent boundary.
- **Recommendation:** None.

### fix-now

(none)

context_tokens≈65000

---

## Build

**Code Complete** @ `f264e868d19fae2f56e45011cd97a6bbeada929b` on `sub/AST-1640/AST-1703-email-breadcrumb-on-meteorite-link-forward-peel-timezone-clock`

- Stage 1: `stage_meteorite` schema + Ruth peel prompt (`from_email` / `to_email` / `sent_at`)
- Stage 2: email text map authors non-http `meteorite.link` via AST-1701 helpers; stage safety for blank email breadcrumb
