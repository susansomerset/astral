# AST-1693 — Persist meteorite http onto job.job_link (+ land when text without scrape)

**Linear:** [AST-1693](https://linear.app/astralcareermatch/issue/AST-1693)  
**Parent:** [AST-1686](https://linear.app/astralcareermatch/issue/AST-1686) — Hyperlink to job with meteorite http link  
**Publish ref:** `sub/AST-1686/AST-1693-persist-meteorite-http-job-link`

Land/create and qualify bot-blocked paths always copy http(s) `meteorite.link` / resolved listing URL onto `job.job_link`. Pre-land `BOT_BLOCKED` meteorite rows that already carry non-scrape JD `content` create/land a job on the existing land claim→process→release path; link-only empty-content `BOT_BLOCKED` stays for AST-1561 Estelle paste. Does not own API listing-href (#2) or React (#3).

## Scope gate

Ticket **## Scope** (verbatim):

`src/core/meteorite.py` (land/create + BOT_BLOCKED-with-content create); `src/core/consult.py` (qualify bot-blocked preserves/writes job_link); `src/core/tracker.py` (only save/initialize touch points required). Technical: http(s) copy onto `job.job_link`; create/land when content present on bot-blocked row; no force-land of empty-content BOT_BLOCKED.

All Files Changed / Stages stay inside that set. **Do not** edit `src/utils/config.py`, `src/data/database.py`, API, or frontend (siblings AST-1694 / AST-1695). **Do not** rewrite AST-1561 notify/paste beyond the minimal contentful-row handoff below.

**Citations (Canon Scope):** `patt.entity.batch-processing`, `stat.logging.info.entity`, `stat.logging.debug`, `stat.logging.error`, `stat.logging.warning`.

**AC partition (this ticket):** Parent AC1–AC3 only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | On `save_meteorite_job` meteorite duplicate-skip, backfill empty `job_link` when caller passes http(s); thin http(s) `job_link` persist helper for qualify bot branch | core |
| `src/core/consult.py` | `qualify_meteorite` bot-blocked branch: persist http(s) `job_link` before/with state → `BOT_BLOCKED` | core |
| `src/core/meteorite.py` | `run_land_meteorite` claims READY + BOT_BLOCKED; land contentful BOT_BLOCKED with http `job_link`; empty BOT_BLOCKED left for AST-1561; notify skips contentful BOT_BLOCKED | core |

## Stage 1: Tracker — http `job_link` persist touch points

**Done when:** `save_meteorite_job` backfills an empty/null `job.job_link` on meteorite-source duplicate-skip when the caller supplies http(s); a small tracker helper writes http(s)-only `job_link` for an existing job without requiring `initialize_job` title/JD; `python3 -m py_compile src/core/tracker.py` succeeds.

1. In `src/core/tracker.py`, add a module-level helper near `initialize_job` (name is the implementer’s call; e.g. `persist_http_job_link`):

   - Args: `astral_job_id: str`, `job_link: str` (and optional `debug: bool = False` only if peers take it — prefer no new debug flag; debug stays ContextVar-gated).
   - Strip `job_link`. If it does **not** start with `http://` or `https://`, return without writing (no-op; non-http breadcrumbs stay out of `job.job_link`).
   - Otherwise call existing `save_job(astral_job_id, job_link=link)` (merge/column update only — do **not** call `initialize_job`, do **not** require `job_title`).
   - No new logging at info for the no-op; callee in/out stays `logger.debug` per `stat.logging.debug` if this helper is called from consult.

2. In `save_meteorite_job` Branch A (existing meteorite-source match → `land_outcome_duplicate_skip`):

   - After resolving `match` / `match_id`, if caller `link` is http(s) **and** `(match.get("job_link") or "").strip()` is empty: `database.save_job(match_id, job_link=link)` (or `save_job` wrapper), then re-`get_job` for the return payload.
   - If match already has a non-empty `job_link`, leave it (never clobber a populated link on duplicate-skip).
   - Do **not** change Branch B (supersede) or Branch C (create) — they already pass `job_link=link` when set.

⚠️ **Decision:** Qualify bot-blocked cannot call full `initialize_job` — that requires `job_title` + `job_link` keys and would overwrite/empty title when Ruth has nothing useful. A link-only persist helper matches parent Technical scope (“initialize_job or equivalent column update”).

## Stage 2: Consult — qualify bot-blocked preserves/writes http `job_link`

**Done when:** In `qualify_meteorite`’s `_classify_jd` → bot branch, before `_transition_job_state_for_task` to `bot_blocked_state`, http(s) resolved `job_link` is written onto the job row; non-http resolved links do not write; content-fail / pass paths unchanged; `python3 -m py_compile src/core/consult.py` succeeds.

1. In `src/core/consult.py` `qualify_meteorite` → inner `process`, locate the bot block:

   ```python
   if _classify_jd(input_jd) == "bot" or (jd_text and _classify_jd(jd_text) == "bot"):
       to_state = cfg["bot_blocked_state"]
       ...
       _transition_job_state_for_task(task_key, [aid], to_state)
       return to_state
   ```

2. Immediately **before** `_transition_job_state_for_task` (after `job_link` / `link_source` are already resolved by the Ruth-vs-input http preference block above):

   - Call `tracker.persist_http_job_link(aid, job_link)` (or whatever Stage 1 named the helper) with the already-resolved `job_link`.
   - Keep the existing debug line and `_warn_job(aid, to_state, "bot_classification")`.
   - Do **not** call `initialize_job` on this branch.
   - Do **not** change the content-fail early return or the success `initialize_job` path.

3. Logging: no new always-on info line for the link write (entity info stays on land/create outcomes). Soft misses stay `_warn_job`. Exceptions stay handler `logger.exception` — do not add a second error log.

## Stage 3: Meteorite — land BOT_BLOCKED-with-content; leave empty for AST-1561

**Done when:** `run_land_meteorite` claims both `READY` and `BOT_BLOCKED` under the same `entity_batch_id`, lands rows with non-empty `content` (including prior BOT_BLOCKED) via `tracker.save_meteorite_job` with http(s) `job_link` from `row.link`, leaves empty-content `BOT_BLOCKED` unchanged for Estelle notify, and `run_notify_meteorite_bot_blocked` skips contentful rows so land owns them; empty-content BOT_BLOCKED still notified; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. In `run_land_meteorite` (`src/core/meteorite.py`):

   - Keep mint/`entity_batch_id` / `finally: clear_meteorite_batch` claim→process→release shape (`patt.entity.batch-processing`).
   - Change the claim call to use the existing multi-state API:

     ```python
     claim_meteorite_batch(
         batch_id,
         cfg["land_trigger_state"],  # still "READY" for the positional/default arg
         limit=batch_size,
         states=["READY", "BOT_BLOCKED"],
     )
     ```

     Do **not** add config keys (config out of scope). Debug log both states in the claim line.

2. Per-row loop body (replace the current “missing content → ERROR” for all rows):

   - `content = (row.get("content") or "").strip()`
   - `from_state = (row.get("state") or "").strip()`
   - **If not content:**
     - If `from_state == "BOT_BLOCKED"`: leave the row unchanged (no `update_meteorite`, no ERROR). `_row_miss` is optional; prefer a single debug line that land skipped empty BOT_BLOCKED for AST-1561. Do **not** increment `total_failed` / `total_errors`. `continue`.
     - If `from_state == "READY"` (or anything else claimed): keep today’s behavior — `update_meteorite(..., state="ERROR", error="missing content")`, `_row_miss`, fail counts.
   - **If content:** unchanged ensure → `job_link = existing_link if _is_http_url(existing_link) else None` → `tracker.save_meteorite_job(..., job_link=job_link, job_data={jd_key: content}, ...)`.
     - On ok outcomes: `update_meteorite(row_id, state="LANDED", astral_job_id=job_id)` even when `from_state == "BOT_BLOCKED"`. (`update_meteorite` does not enforce `METEORITE_STATES` priors — data layer allows the write; config prior list stays READY-only this ticket because `config.py` is out of scope.)
     - Keep `_meteorite_state_info` / `_entity_info` entity info lines.
     - On save miss: ERROR path unchanged.

⚠️ **Decision:** Land BOT_BLOCKED→LANDED in one `update_meteorite` rather than hop BOT_BLOCKED→READY→LANDED. Data does not check priors; avoiding a fake READY hop keeps Estelle notify from racing a transient READY row. Registry `LANDED.prior_states` honesty is a follow-up if Archie widens Scope to `config.py`.

3. In `run_notify_meteorite_bot_blocked`, at the top of the per-row try (before nag-limit / Slack):

   - If `(row.get("content") or "").strip()` is non-empty: do **not** DM, do **not** abandon, do **not** stamp notify fields. Leave state `BOT_BLOCKED`. Debug that notify skipped contentful row for land. `continue` (no fail count — land owns AC2).
   - Empty-content BOT_BLOCKED keeps today’s notify/nag/abandon behavior (AC3 / AST-1561).

4. Do **not** change `run_scrape_meteorite` blocked path (it already does not write challenge text into `content`). Do **not** change public `land_meteorite` / `create_meteorite_job` signatures — they already accept/pass `job_link`; table land is the BOT_BLOCKED gap.

5. Confirm create path still passes http link: `run_land_meteorite` already sets `job_link` from `_is_http_url(row.link)`; Stage 1 duplicate-skip backfill covers re-land. No further create edits unless a literal call site drops `job_link` when `row.link` is http — if found during build, pass it; do not invent new create helpers.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

**Ticket:** AST-1693
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1686/AST-1693-persist-meteorite-http-job-link` @ `041ec97845380d67226737fd0d7d8f6352765756`

## Canon scores

patt.entity.batch-processing | A | | Stage 3 keeps mint/`entity_batch_id`/`finally: clear_meteorite_batch`; multi-state `claim_meteorite_batch` stays on existing land runner
stat.logging.info.entity | B | | Entity info preserved on land outcomes; plan should pass captured `from_state` into `_meteorite_state_info` for BOT_BLOCKED→LANDED (not hardcoded READY)
stat.logging.debug | A | | ContextVar-gated callee in/out; no new always-on info disguised as debug
stat.logging.error | A | | Per-row `logger.exception` at handler; no duplicate error logs on link write
stat.logging.warning | A | | `_warn_job` / `_row_miss` on soft misses; empty BOT_BLOCKED skip does not inflate fail counts

## Traceability

AC1 → Stages 1–3 (tracker duplicate-skip backfill, qualify bot `persist_http_job_link`, land `job_link` from http `row.link`); AC2 → Stage 3 (`claim_meteorite_batch` READY+BOT_BLOCKED, contentful `save_meteorite_job` → LANDED); AC3 → Stage 3 (empty BOT_BLOCKED `continue`; notify skips contentful rows). Parent AC4–AC7 N/A — out of child Scope.

## Findings

### acceptable
- **Location:** Stage 3 — `_meteorite_state_info` call site
- **Finding:** Plan introduces `from_state` per row but says only “keep” entity info lines; current code hardcodes `from_state="READY"`.
- **Recommendation:** One-line plan tweak: pass the captured `from_state` into `_meteorite_state_info` on BOT_BLOCKED land. Implementer can infer; not blocking.

### acceptable
- **Location:** Stage 3 — Decision on `LANDED.prior_states`
- **Finding:** BOT_BLOCKED→LANDED without `config.py` prior update is explicitly scoped out with documented rationale.
- **Recommendation:** None for this child; registry honesty is a follow-up if Scope widens.

## R6 checklist (summary)

- Definition fidelity: plan matches parent child-1 slice; Files Changed ⊆ ticket Scope; no sibling API/React/config creep.
- DRY / scope: thin `persist_http_job_link` helper avoids `initialize_job` misuse on bot branch; no parallel ingress runner.
- Self-assessment: Estimate 5 — agree; stages are concrete with done-when gates.

context_tokens≈42000
