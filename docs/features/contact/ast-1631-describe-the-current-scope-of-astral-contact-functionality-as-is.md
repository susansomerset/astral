# AST-1631 — Describe the current scope of Astral contact functionality, as is

<!-- linear-archive: AST-1631 archived 2026-10-02 -->

## Linear archive (AST-1631)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1631/describe-the-current-scope-of-astral-contact-functionality-as-is  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is scope: Astral Contact

**What it is (today):** Astral Contact is the Slack ↔ Estelle runtime for inbound conversation, candidate identity resolve, allowlisted entity-save skills, Contact-task markup dispatch, optional meteorite land/paste recovery, and admin Manage Slack controls. Primary code: `src/core/contact.py` on `origin/dev`.

**What it is not:** Candidate/profile “contact fields” UI and uniqueness contracts (Candidate / Interface projects) are adjacent product surfaces — not this runtime — except where Contact skills explicitly write allowlisted `contact.*` / `profile.*` paths via ACL.

### Purpose

* Accept Slack Events (`app_mention`, DM `message`) when Manage Slack **Listen** is on.
* Resolve Slack user → Astral candidate by in-process lookup (no create-on-miss; AST-1668).
* Run one Estelle conversational turn with Slack-sourced context.
* Execute allowlisted **skills** (entity saves) and **Contact tasks** (markup `~~/task_key … ~~`).
* Optionally land meteorite scraps / recover BOT_BLOCKED paste via meteorite APIs.
* Persist listen/debug/activity durable state; expose admin HTTP + Manage Slack UI.

### Inbound channels

| Path | Module | Notes |
| -- | -- | -- |
| Production Events API | `POST /api/slack/events` → `receive_slack_events_http` → background `handle_slack_event` | Signature verify in Contact; path from `CONTACT_CONFIG["events_http_path"]` (`/slack/events`) under `api_slack` blueprint prefix `/api`. |
| Local/dev Socket Mode | `scripts/slack_socket_mode_dev.py` + `src/external/slack.py` | Feeds Events-shaped payloads into the same `handle_slack_event`. Not production. |

**Accepted event shapes:** `app_mention` (channel @Estelle); human DM `message` only (no bot/subtype; non-DM messages skipped). Listen-off, missing/duplicate `event_id`, and type skips return `accepted=False`.

### Config (load-bearing)

* `CONTACT_CONFIG` — listen/debug/activity filenames, Slack env name contracts (`SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SLACK_APP_TOKEN`), Events path, bot event types, event-id dedupe ring, prospect id template `slack-{slack_user_id}`, conversation context cache limits, hear-ack text, non-prod reply prefix, **skills ACL**.
* `CONTACT_ESTELLE_CONFIG` — Estelle turn defaults (brain Medium, task key `contact_estelle_turn`, context message/char limits).
* `CONTACT_TASK_CONFIG` — allowlisted Contact-task keys → handler dotted paths (distinct from skills ACL and global `TASK_CONFIG`).

### Core modules (owners)

| Area | Location |
| -- | -- |
| Runtime | `src/core/contact.py` |
| Durable listen / debug / activity | `src/data/contact_listen.py`, `contact_debug.py`, `contact_estelle_activity.py` → `data/contact_slack_listen.json`, `contact_slack_debug.json`, `contact_estelle_activity.json` |
| Admin HTTP | `src/ui/api/api_contact.py` — `/api/admin/contact/{listen,debug,estelle_activity,skills,skills/<key>}` (`@require_admin`) |
| Slack webhook transport | `src/ui/api/api_slack.py` |
| Admin UI | `AdminManageSlack` at route `admin/manage_slack` — listen toggle, debug toggle, Estelle activity list |
| Slack external I/O | `src/external/slack.py` (post, history, profile, signature, Socket Mode helper) |
| Contact-task handlers (built) | `src.core.gazer.contact_task_gazer_scrape`, `src.core.meteorite.create_contact_meteorite`, `src.core.tracker.contact_task_get_{job_by_pattern,job_data,company_data,candidate_data}` |

### Identity resolve (candidate pairing)

Not an HTTP API. On an accepted Slack event, `handle_slack_event` calls in-process `resolve_slack_user(event.user, estelle_in_play=True)`.

**In:** Slack user id (`event.user` only). `estelle_in_play` does not create a candidate; on a miss it only allows a Slack `users.info` fetch for display names.

**Lookup:** `get_candidate_id_for_query(slack_user_id)` walks non-deleted candidates and casefolds the id against `CANDIDATE_LOOKUP_CONFIG` homes: `contact.slack_user_id`, email paths (`contact.contact_email`, `contact.reply_email`, transitional `profile.contact_email` / `profile.reply_email`, `contact.extra_emails`), and name paths. Returns an Astral candidate id only on exactly one hit. Zero hits or two-or-more hits return nothing.

**Out, unique hit:** `{astral_candidate_id, state, created: false, slack_username, slack_display_name}`. State comes from `get_candidate`. Slack `users.info` fills username/display; if the row has no `slack_username`, Contact saves `contact.slack_user_id` + `contact.slack_username` (AST-1105). `created` is always false.

**Out, miss or ambiguous:** `{astral_candidate_id: null, state: null, created: false, slack_username, slack_display_name}`. No PROSPECT mint. `CONTACT_CONFIG["prospect_candidate_id_template"]` is unused by this path (AST-1668).

**Then:** activity row with `bind_ok` true only when an id came back. Known users get Slack text `I know who that is`, then paste recovery or the Estelle turn with that candidate id. Unknown users get `I don't recognize you` and the turn is skipped (`outcome: unrecognized`).

### Conversation context

Process-local LRU cache + Slack history fetch (`load_slack_conversation_context` / `append_slack_conversation_message`). Keyed by `(channel, thread_ts)`. Limits from `CONTACT_CONFIG` history/cache/TTL.

### Estelle turn loop

`run_contact_estelle_turn` (AST-1073 / envelope AST-1046 / AST-1072): listen re-check → context → agent turn → strip/post human reply → parse Contact-task markup → `run_contact_task_dispatch` → optional skill runs → optional `land_calls` / `apply_paste` → activity record. Non-production replies get environment prefix. Hear-ack text available from config for accept UX.

Inbound orchestration in `handle_slack_event`: resolve user → activity → Estelle turn (and BOT_BLOCKED paste recovery via `try_meteorite_apply_paste_from_slack` when applicable).

### Skills ACL (entity-save)

Configured under `CONTACT_CONFIG["skills"]`; runners via `run_contact_skill` / admin POST:

| Skill | Writes (allowlisted paths) |
| -- | -- |
| `save_candidate_profile` | `profile.first`, `profile.last`, `profile.pronoun_preference`, `profile.contact_email` |
| `save_candidate_contact` | `contact.contact_email`, `contact.reply_email` |

Admin: `GET/POST /api/admin/contact/skills…`.

### Contact tasks (markup dispatch) — built

Markup form: `~~/task_key param~~` (`parse_contact_task_markup` / `strip_contact_task_markup`).

| Task key | Handler | Role |
| -- | -- | -- |
| `gazer_scrape` | gazer | Fetch visible text/links/status for one job URL |
| `create_contact_meteorite` | meteorite | Land meteorite from link (scrape-first) or pasted page text |
| `get_job_by_pattern` | tracker | Hydrated job for Slack candidate from text pattern |
| `get_job_data` | tracker | Stored job data by id (candidate-owned) |
| `get_company_data` | tracker | Stored company data by short_name/id |
| `get_candidate_data` | tracker (+ pin path) | Stored candidate data; **artifact UUID** → `resolve_pinned_base_resume` / `get_operative_base_resume` (AST-1585); bare `artifacts.base_resume` refused (`pin_required`) |

These task keys are implemented in product code on `dev` (parents may still be User Testing for UAT — in scope per ticket decisions).

### Meteorite handoff (built — included)

* `contact_land_meteorite` — Contact/Estelle sync entry to `stage_meteorite` (AST-1471 / AST-1531); used from turn `land_calls`.
* `try_meteorite_apply_paste_from_slack` **/** `apply_paste` — BOT_BLOCKED paste recovery without re-classify (AST-1561).
* `create_contact_meteorite` — Contact-task create path (AST-1517).

### Admin listen / debug / activity

* Listen SoT: durable file via `set_slack_listen_enabled` / `slack_listen_enabled` (default config `listen_enabled: false` until file/env says otherwise).
* Debug SoT: durable file via `set_slack_debug_enabled` / `slack_debug_enabled` — **sole** SoT for Contact Slack Events debug depth (AST-1207); separate from UI LLM debug.
* Estelle activity: durable JSON rows listed for Manage Slack (AST-1094 / AST-1105 username display).

### Test-bible cross-check (claimed behaviors still asserted)

| Bible | Covers |
| -- | -- |
| `docs/test-bible/core/contact.md` | Core scaffold, Events, resolve, context, skills, Estelle turn, tasks, land/paste, debug |
| `docs/test-bible/ui/api/api_contact.md` | Admin contact HTTP |
| `docs/test-bible/data/contact_debug.md` | Debug durable file |
| `docs/test-bible/data/contact_estelle_activity.md` | Activity durable file |
| `docs/test-bible/utils/config.md` | CONTACT\_\* config contracts |

Component tests: `tests/component/core/test_contact.py`, `tests/component/ui/api/test_api_contact.py`, `tests/component/data/test_contact_*.py`.

### Explicit out of scope / adjacency (not Astral Contact runtime)

* Candidate contact-field uniqueness / shapes / profile Manage Contact nav (Candidate + Interface feature docs AST-1045/1079/1080/1014, AST-1065/1081/1082) — product data/UI contracts, not Slack Estelle runtime.
* Global `TASK_CONFIG` dispatcher catalog (Contact tasks are a separate allowlist).
* Production Socket Mode (local script only).
* Canceled Contact work (excluded by decision).

### Feature-doc inventory (built trail under `docs/features/contact/`)

Slack foundation: AST-1043, 1046, 1066–1073; UAT follow-ups AST-1094, 1101, 1105; debug AST-1203/1206–1208; Contact-task wave AST-1515–1518. Cross-project built hooks referenced above: meteorite land/cutover, operative pin resolve (AST-1585).

## Decisions (locked)

* Deliverable home: this Description only — no separate docs file.
* Depth: everything built/implemented, including User Testing / UAT; exclude Canceled only.
* Meteorite Contact land + candidate contact-field contracts: include land (built); treat candidate field UI/uniqueness as adjacency only.

## Risks / open questions

* none

## Further exploration

1. Candidate pairing — answered above under Identity resolve. Estelle does not call an HTTP pairing API from the Slackbot. Pairing is `resolve_slack_user` → `get_candidate_id_for_query` on `event.user`.

---

## Original brief

Describe the current scope of Astral contact functionality, as is

### Comments

#### chuckles — 2026-09-14T21:35:37.684Z
[check-linear] User Testing — attached origin/dev blobs for `src/core/contact.py` and `src/ui/api/api_contact.py` on this ticket (@susan)

#### chuckles — 2026-09-14T21:34:54.727Z
[check-linear] User Testing — noted; Description holds the as-is scope (@susan)

#### fable — 2026-09-14T21:33:21.166Z
@Chuckles Cursor — please attach the full contents of `src/core/contact.py` and `src/ui/api/api_contact.py` to this ticket, so we can review the actual code directly for the candidate pairing / architecture question in Further exploration item 1.

#### chuckles — 2026-09-14T21:09:34.140Z
[check-linear] Discussion — decisions locked in Description; flip to Todo when ready to write the as-is (@susan)

#### fable — 2026-09-14T21:07:31.649Z
@Chuckles Cursor — answers to your open questions:

1. Deliverable home: post the as-is content directly in this ticket's Description. No separate docs file needed.

2. Depth: include everything built and implemented, including work sitting in User Testing / UAT status — that's built and working, just not yet verified and merged to main. Only exclude Canceled work; there isn't really an "archived" category we care about here otherwise.

3. Meteorite Contact land handoff and candidate contact-field contracts: only include these if they've actually been built already. If they're still planned/future work, leave them out.

---

_Implementation detail may live in git history on `origin/dev`._
