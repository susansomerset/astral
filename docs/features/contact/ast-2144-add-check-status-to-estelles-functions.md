# AST-2144 — Add /check-status to Estelle's functions

<!-- linear-archive: AST-2144 archived 2026-10-16 -->

## Linear archive (AST-2144)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2144/add-check-status-to-estelles-functions  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Candidates want to ask Estelle "where is this job at?" without opening Astral and hunting for it. `@Estelle /check-status <search string>` answers that in one terse Slack reply. Contact finds the job among the sender's own jobs from a link, title, company, or any text the candidate types. Estelle replies in a thread under the candidate's message, also shared to the channel, with the title, the date we got the job, its current state and when it reached that state, and the same deeplink the Recommended Job Report's Copy Link produces. The candidate clicks through to read the rest. There's no conversation to manage: it's one question and one answer. This is the second command on the registry that `/add-job` introduced ([AST-2035](https://linear.app/astralcareermatch/issue/AST-2035)), and the first one that reads.

## Functional scope

1. `/check-status` **command.** A bound candidate types `@Estelle /check-status <search string>` in a DM or private channel, where Estelle already listens. The search string can be a job link, title, company, job id, or any substring. A bare `/check-status` gets a fixed usage reply, the same as a bare `/add-job`.
2. **Candidate-scoped lookup.** The search string is matched against **only** the sender's own jobs, using the same rules as the existing `get_job_by_pattern` contact task (title / company / link / id, case-insensitive substring). Another candidate's job is never shown.
3. **One match, terse reply.** A fixed template (no LLM turn) gives the job title, the date we got it, its current state as the raw state key (for example `PASSED_LIKE`), the timestamp it entered that state, and the job's deeplink. Times show in the candidate's contact timezone, in the clock format meteorite breadcrumbs use.
4. **The deeplink is the Copy Link URL.** It has the same shape as the Recommended Job Report's Copy Link: `<origin>/jobs/detail/<job id>`. The backend has no browser origin, so the origin is `https://` plus Railway's `RAILWAY_PUBLIC_DOMAIN`. Where that variable is unset (local dev), the reply goes out without links.
5. **Several matches.** One line per match (title, company, raw state, deeplink), so the candidate clicks the right one. There's no follow-up question.
6. **No match.** A terse "nothing matched" with a hint to try a link, title, or company.
7. **Placement.** Every `/check-status` reply (usage, match, list, no match) posts as a thread reply under the candidate's message (or in their thread) with Slack's "Also send to channel" on, whatever the global `thread_response` setting is. Other Estelle replies keep following `thread_response`.
8. **Read-only.** `/check-status` never writes a job, meteorite, company, or candidate row.

**Out of scope:** passing the job record into an Estelle LLM turn; thread-scoped context or follow-up memory (deferred per Susan); a friendly label map for job states (raw is fine per Susan); Slack's own registered slash-command API; changes to `/add-job`; AST-1637's two-tier turn rework.

## Component scope

* `src/utils/config.py`: **modified**. Adds the `check-status` command entry with its reply templates and placement, relaxes the registry asserts so `ack_reply_template` is no longer required on every entry, adds the handler's pinhole row, and adds the env-name contract for the deeplink origin.
* `src/core/tracker.py`: **modified**. Adds the `/check-status` handler next to the AST-1518 contact-task job reads.
* `src/core/contact.py`: **modified**. `code`-mode commands can post a reply the handler composed, on a hit or a miss, and a command entry can override reply placement.

## Technical scope

* `src/utils/config.py`, `CONTACT_CONFIG["commands"]`. **New entry** `check-status`:
  * `mode: "code"`
  * a handler dotted path into `src.core.tracker`
  * `description` and `usage_reply_text`
  * **new fields**: the reply templates the handler formats. These are a single-match template (title, date received, state, state timestamp, deeplink), a several-match header plus a per-match line template (title, company, state, deeplink), and a no-match text.
  * **new field**: an optional per-command reply placement, using the existing `thread_response` vocabulary. It's set to `always_with_share` for `check-status`.

  Reply wording lives in config, not code.
* `src/utils/config.py`, registry asserts. **Modified.** `ack_reply_template` becomes optional. When it's present it must still carry `{meteorite_id}`. The new template fields get shape asserts on entries that declare them. The placement field, when present, must be one of the `thread_response` values.
* `src/utils/config.py`, `_CONTACT_PINHOLE_HANDLERS`. **New row** for the `/check-status` handler, kind `read job`.
* `src/utils/config.py`, deeplink origin. **New** env-name contract, holding the name `RAILWAY_PUBLIC_DOMAIN`, placed alongside the existing `JOBS_DETAIL_ROUTE_PREFIX`. The deeplink is `https://` + that env value + `JOBS_DETAIL_ROUTE_PREFIX` + `/` + the URL-encoded job id. That's the same path the Copy Link builds in `JobAnalysisReportModal.tsx`, with no second path string. Read it with `os.environ.get` on the config-held name. Unset or empty means no links.
* `src/core/tracker.py`. **New function**: the `/check-status` command handler, using the command-handler signature `(candidate_id, payload, *, source_id, thread_ts, debug)`. It reuses the existing candidate-scoped matcher and ownership check behind `contact_task_get_job_by_pattern`, with no new query and no hydration (no agent story, no blob). It formats the entry's templates from `job_title`, `company`, `created_at`, `state`, and `state_changed_at`. Times go through the existing `format_contact_timezone_clock` with the candidate's contact timezone.
  * One match returns `ok` and the composed reply text.
  * Several matches return `ok` and the composed list.
  * No match returns not-`ok` with the existing `unmatched_pattern` error plus the no-match reply text.
  * If the origin env is unset, it composes the reply without links and logs one warning that the deeplink is missing (stat.logging.warning). It still replies.

  No writes.
* `src/core/contact.py`, `_contact_reply_placement`. **Modified.** It accepts an optional placement mode that overrides `CONTACT_CONFIG["thread_response"]` for that call. It stays the single placement rule, so call sites never write their own `thread_ts or …`.
* `src/core/contact.py`, `_run_contact_command`. **Modified.** It resolves placement with the entry's override when one is present, for the usage reply and every `code`-mode post. In `code` mode, when the handler returns reply text, that text is posted (via `format_contact_reply_text` / `contact_post_message`) whether the result is `ok` or not. When it returns none, today's behavior holds: `ack_reply_template` on `ok`, nothing on a miss (hear-ack fallback). `add-job` declares no override and returns no reply text, so it's unchanged. `agent` mode is untouched. The handler anchor (`anchor_ts`) is unchanged.

## Architectural definition

**Patterns to reuse**

* [`patt.contact.command-intercept`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.contact.command-intercept.md>): `/check-status` is one registry row plus a `src.core.*` handler, intercepted before paste recovery and the turn, in `code` mode. **Change requested (Archie):** the pattern fixes the handler result to `{ok, meteorite_id, error}`, requires `ack_reply_template` with `{meteorite_id}` on every entry, says a `code`-mode miss posts nothing, and has no per-command placement. This epic needs:
  * an optional handler-composed reply text that `code` mode posts on a hit or a miss
  * the ack template made optional
  * an optional per-entry placement override

  Arc steps 3–4 and Data coupling also still lag [AST-2072](https://linear.app/astralcareermatch/issue/AST-2072) (recognition post removed, placement via `thread_response`).

**New patterns proposed**

* none

**Applicable statutes**

* [`stat.logging.info.contact`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.contact.md>): one listen line per inbound event naming `check-status:code`.
* [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>): Calling/Response pairs on the handler call, not gated by a debug flag.
* [`stat.logging.warning`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>): a missing origin env, or an unavailable handler, is a warning naming what isn't happening.
* [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>): a handler that raises is logged once by the existing intercept with who / why / next step.

## Acceptance criteria

 1. **Registry.** `python3 -c "from src.utils.config import CONTACT_CONFIG as C; e=C['commands']['check-status']; print(e['mode'])"` prints `code`, and the entry's placement field equals `always_with_share`. **Fails if:** a KeyError, or any other value.
 2. **Pinhole.** `python3 -c "from src.utils.config import CONTACT_CONFIG as C, _CONTACT_PINHOLE_HANDLERS as P; print(P[C['commands']['check-status']['handler']])"` prints a value starting with `read`. **Fails if:** a KeyError, or a `write…` value.
 3. **Parse.** `parse_contact_command("<@UBOT> /check-status Senior Engineer")` returns `("check-status", "Senior Engineer")`, and `parse_contact_command("<@UBOT> /check-status <https://x.com/j/1|x.com/j/1>")` returns `("check-status", "https://x.com/j/1")`. **Fails if:** `None`, or a payload that differs.
 4. **One match.** The candidate owns exactly one job whose title contains the pattern, and `RAILWAY_PUBLIC_DOMAIN=astral.example`. `handle_slack_event` on a bound `app_mention` `/check-status <pattern>` makes exactly one `post_message` call. Its text contains the job title, the raw state key, `format_contact_timezone_clock` output for both `created_at` and `state_changed_at` in the candidate's timezone, and `https://astral.example/jobs/detail/<url-encoded job id>`. **Fails if:** any of these is missing, or there are 0 or 2+ posts.
 5. **Thread + share.** For AC 4 with `CONTACT_CONFIG["thread_response"] == "threads_only"` and a top-level inbound message, that `post_message` call has `thread_ts` equal to the inbound `ts` and `reply_broadcast=True`. If the inbound message was already in thread `T`, `thread_ts == T`. **Fails if:** `thread_ts` is missing or wrong, or `reply_broadcast` isn't `True`.
 6. **No LLM, no paste, no write.** For AC 4, `do_task`, `try_meteorite_apply_paste_from_slack`, and `insert_slack_meteorite` are each called zero times, and the job row is byte-identical before and after. **Fails if:** any call happens, or the row changes.
 7. **Several matches.** Two owned jobs match. One post contains both titles and both `/jobs/detail/<id>` links. **Fails if:** either id or link is missing.
 8. **Candidate scope.** A job owned by another candidate whose title matches exactly is absent from the post: its id and title do not appear. **Fails if:** either appears.
 9. **No match.** The post text equals the entry's no-match text (after `format_contact_reply_text`), threaded and shared as in AC 5, and the hear-ack text is **not** posted. **Fails if:** there's no post, the hear-ack posts, or the text or placement differs.
10. **No origin.** With `RAILWAY_PUBLIC_DOMAIN` unset, AC 4 still posts the title, state, and times, with no `/jobs/detail/` text, and `caplog` shows exactly one WARNING naming the missing deeplink. **Fails if:** there's no post, a link appears, or there are 0 or 2+ warnings.
11. **Bare command.** `/check-status` with no payload posts the entry's `usage_reply_text`, threaded and shared as in AC 5, and the handler is called zero times. **Fails if:** the handler runs, or the text or placement differs.
12. **Placement unchanged elsewhere.** With `threads_only`, a top-level non-command `@Estelle hi` reply and a top-level `/add-job <link>` ack each post with no `thread_ts` and no `reply_broadcast`. **Fails if:** either is threaded or broadcast.
13. **Listen line.** With debug off, `caplog` at INFO for AC 4 shows exactly one `contact listen` line whose `action:` list contains `check-status:code`. **Fails if:** zero or several such lines, or the key is missing.
14. **No literals in core.** `rg -n "check-status|jobs/detail|RAILWAY_PUBLIC_DOMAIN|always_with_share" src/core` returns only the pre-existing `always_with_share` line(s) inside `_contact_reply_placement`, and none of the other strings. **Fails if:** any other hit. The command id, route prefix, env name, and per-command placement live only in config.
15. `/add-job` **unchanged.** `tests/component/core/test_contact.py::TestAst2035ContactCommandIntercept` passes unmodified, including the `code`-mode miss path that falls to the hear-ack. **Fails if:** any test in that class fails or needed editing.

## Open questions

none

## Proposed child tickets

#### 1!: **Check-status registry entry, deeplink origin, and job handler - Ada**

Adds the `check-status` entry with its reply templates and `always_with_share` placement, relaxes the registry asserts (optional ack template, placement vocabulary), adds the pinhole row and the `RAILWAY_PUBLIC_DOMAIN` origin contract, and adds the tracker handler that finds the sender's job(s) and composes the terse summary-plus-deeplink reply (one / several / none / no origin). Ships AC 1–2 and the handler side of AC 4 and AC 7–10. It does **not** touch `src/core/contact.py`. Until #2 lands, the composed text and placement aren't used.
**Citations:** `patt.contact.command-intercept`; `stat.logging.debug`; `stat.logging.warning`.
**Scope:**

* `src/utils/config.py`: **modified**.
  * `CONTACT_CONFIG["commands"]`, **new entry** `check-status` with:
    * `mode: "code"`
    * a handler dotted path into `src.core.tracker`
    * `description` and `usage_reply_text`
    * **new fields** for the reply templates the handler formats: a single-match template (title, date received, state, state timestamp, deeplink), a several-match header plus a per-match line template (title, company, state, deeplink), and a no-match text
    * **new field** for an optional per-command reply placement using the existing `thread_response` vocabulary, set to `always_with_share` for `check-status`
  * Registry asserts, **modified**: `ack_reply_template` is optional and still carries `{meteorite_id}` when present. The new template fields get shape asserts on entries that declare them. The placement field, when present, must be a `thread_response` value.
  * `_CONTACT_PINHOLE_HANDLERS`, **new row** for the `/check-status` handler, kind `read job`.
  * Deeplink origin, **new** env-name contract holding `RAILWAY_PUBLIC_DOMAIN`, alongside `JOBS_DETAIL_ROUTE_PREFIX`. The deeplink is `https://` + env value + prefix + `/` + URL-encoded job id. Read with `os.environ.get`; unset or empty means no links.
* `src/core/tracker.py`: **modified**. **New function**, the `/check-status` command handler with the command-handler signature `(candidate_id, payload, *, source_id, thread_ts, debug)`. It reuses the existing candidate-scoped matcher and ownership check behind `contact_task_get_job_by_pattern`, with no new query and no hydration. It formats the entry's templates from `job_title`, `company`, `created_at`, `state`, and `state_changed_at`, with times through `format_contact_timezone_clock` in the candidate's contact timezone.
  * One match: `ok` plus the reply text.
  * Several matches: `ok` plus the list.
  * No match: not-`ok`, `unmatched_pattern`, plus the no-match text.
  * Origin env unset: no links, one warning, still replies.
  * No writes.

Estimate: 2

#### 2: **Code-mode handler reply + per-command placement - Hedy**

After #1. `_contact_reply_placement` takes an optional override. `_run_contact_command` uses the entry's placement for the usage reply and every `code`-mode post, and posts a handler-composed reply on a hit or a miss. It keeps the ack-template / hear-ack path for handlers that return no reply text (`add-job`). Ships AC 3, AC 5–6, AC 11–15, and the end-to-end posting of AC 4 and AC 7–10. It does **not** own config or the handler (#1).
**Citations:** `patt.contact.command-intercept`; `stat.logging.info.contact`; `stat.logging.error`.
**Scope:**

* `src/core/contact.py`: **modified**.
  * `_contact_reply_placement`, **modified**: it accepts an optional placement mode that overrides `CONTACT_CONFIG["thread_response"]` for that call, and stays the single placement rule.
  * `_run_contact_command`, **modified**: it resolves placement with the entry's override when present, for the usage reply and every `code`-mode post. In `code` mode, when the handler returns reply text, that text is posted (via `format_contact_reply_text` / `contact_post_message`) whether the result is `ok` or not. When it returns none, today's behavior holds: `ack_reply_template` on `ok`, nothing on a miss. `add-job` is unchanged, `agent` mode is untouched, and `anchor_ts` is unchanged.

Estimate: 2

**New patterns:** none. #1 and #2 widen `patt.contact.command-intercept` (handler-composed `code`-mode reply, optional ack, per-command placement), which is flagged above as a change request.

**Monolith check:** Functional scope has 8 items and there are 2 children. #1 is config plus the data read, and #2 is the Contact posting and placement rule. Each can be checked on its own.

**Scope partition check:** `src/utils/config.py` and `src/core/tracker.py` are in #1 only, and `src/core/contact.py` is in #2 only. Every Technical scope item appears in exactly one child.

---

## Original brief

Create a task for Estelle to get a command like `@Estelle /check-status <search string>` where the search string might be the job link or a job title or other string to pattern match.

Let Estelle get the full blob of job data for that job and read it, then give a quick summary of the title, the date we got it and its current state as of what timestamp, then ask the user what they would like to know, and begin the context for that thread, so that responses in the thread have the context of the whole thread history.

**Susan's revision (2026-10-12, inline on the first define pass):**

Rethinking this…. Let's just have her give the summary of title, dates, current state, and deeplink to the job page (wherever it is in Astral) so the candidate can just click on it to read.  No need to manage context just yet.

**Susan's answers (2026-10-12, inline on the second define pass), in question order — deeplink origin / voice vs template / state wording / Linear project:**

1. Yes it does.  There's a feature to copy the job link on the recommended job modal.  Use that, otherwise use the railway_public_domain.
2. For now, just have a terse response, and post as a thread reply with a "share with channel" set to true.
3. Raw is fine.
4. Done

### Comments

#### chuckles — 2026-10-12T18:01:11.925Z
@susan Rescoped to summary + deeplink only: no job record in a turn, no thread context. Estimate drops 5 → 3.

1. **Deeplink origin.** The backend doesn't know Astral's public URL today; the UI's Copy Link uses the browser's origin. I scoped a new env var, `ASTRAL_APP_URL`, set per Railway environment. The alternatives are Railway's `RAILWAY_PUBLIC_DOMAIN` (wrong with a custom domain) or a hardcoded prod URL (wrong for test). OK with `ASTRAL_APP_URL`? If so, what are the prod and test values?
2. **Estelle's voice or a fixed template?** I scoped `code` mode: a fixed config template, with no LLM call, the same every time, and free. The alternative is `agent` mode, where Estelle words the summary herself (more natural, costs a turn). Which one?
3. **State wording.** There's no single friendly-label map for job states, so the reply shows the raw key (for example `PASSED_LIKE`). Is that OK, or do you want a label map added (bigger scope)?
4. **Linear project.** The ticket still has no Linear project. I've assumed **Contact**. Can you set it?

#### chuckles — 2026-10-12T17:51:37.497Z
@susan

1. **How does the thread keep the job context?** I scoped option (a); say if you want another.
   - (a) **Re-run from the thread root.** Every Estelle turn in a thread whose first message is `/check-status …` re-runs the lookup and hands her the fresh job record. There is no new storage, and Slack is the only memory.
   - (b) **Job id in Estelle's reply.** Her reply includes the job id, and on follow-ups she can choose to fetch it with the existing `get_job_data` task. She might not fetch.
   - (c) **Hidden Slack message metadata.** The job id rides as hidden metadata on her reply. This touches `src/external/slack.py`.
   - (d) **In-memory thread→job map.** It's lost on restart.
2. **Several jobs match.** I scoped this: Estelle lists them (title, company, state, id) in the thread and asks which one. The alternative is that she asks the candidate to re-run `/check-status` with the job id or link. Which one?
3. **"The date we got it".** I scoped it as the job row's `created_at`. If you mean when it first arrived as a meteorite (earlier, for Slack/email intake), say so.
4. **Linear project.** The ticket has no Linear project. I've assumed **Contact** (`docs/features/contact/`). Can you set it?

---

_Implementation detail may live in git history on `origin/dev`._
