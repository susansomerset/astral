# AST-2032 — Let Estelle post a meteorite from Slack

<!-- linear-archive: AST-2032 archived 2026-10-16 -->

## Linear archive (AST-2032)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2032/let-estelle-post-a-meteorite-from-slack  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1637

### Description

## Purpose

Today a candidate who finds a job can only get it into Astral by email (inbox → `stage_meteorite`) or by chatting with Estelle and hoping her LLM turn emits the `create_contact_meteorite` contact task, which writes straight to the **job** table and skips the meteorite staging spine. Susan wants a deterministic Slack command, `@Estelle /add-job <link or pasted text>`, that saves the raw blob into the `meteorite` **table** at state `NEW`. The existing `stage_meteorite` hop then classifies it with Ruth and routes it down the same spine (stage → scrape → uniqueness → land) as every other posting. This realizes the original vision for `NEW`: any blob can be saved there and staged later. Which Contact commands exist, and whether each one runs code only or also an Estelle agent turn, becomes config-driven.

## Decisions (Susan's inline answers, folded in)

1. **Routing — option B.** `/add-job` saves the raw blob at `NEW` with no classifier outcome, and the `stage_meteorite` dispatch hop learns to Ruth-classify unclassified `NEW` rows. *Fact check on the original vision:* the AST-1530/1560 spine as built classifies inline at ingress (email rows are inserted already past `NEW`), and today's `NEW` hop only routes rows that already carry `classify_outcome` (an unclassified row goes to `SCRAPE_ERROR`). This epic closes that gap for the Slack path. Email ingest is unchanged and keeps classifying inline (moving email to the raw-`NEW` path is out of scope).
2. **Agent turn vs code action — config-driven.** Yes, `CONTACT_CONFIG` already exists. It holds the recognition replies (`known_recognition_reply_text` / `unknown_recognition_reply_text`), the skills ACL, and Slack env/listen settings. Contact tasks live in the sibling `CONTACT_TASK_CONFIG`. This epic adds a **commands** registry inside `CONTACT_CONFIG`, keyed by command id. Each entry declares its handler and a **mode**: `code` (fixed reply, no LLM turn) or `agent` (run the action, then one Estelle turn that sees the action's result). `add-job` ships as `code`.
3. **Syntax.** Mention-first everywhere (channel and DM): `@Estelle /add-job …`. Registering a real Slack slash command is out of scope for this phase.

## Functional scope

1. A bound (recognized) candidate can post `@Estelle /add-job <payload>` in their channel, or in a DM to Estelle, and Estelle saves exactly one new meteorite row at state `NEW` for that candidate, holding the raw payload.
2. The payload can be a job link (including Slack's auto-linked form of a bare host like `www.dice.com/jobs/13234abcd`) or pasted job-description text. Slack link markup is unwrapped to the plain `http(s)` URL before saving.
3. Contact commands are a config registry keyed by command id. A command is recognized only when it is the first token after any leading @mentions. Any other message, including one that mentions `/add-job` mid-sentence, goes through the normal Estelle path unchanged.
4. Each command declares a mode. In `code` mode, Estelle posts a short fixed confirmation naming the saved meteorite id and no LLM turn runs. In `agent` mode, the action runs first and then one Estelle turn runs with the action result in context and replies conversationally. `add-job` ships in `code` mode.
5. Guard rails: an unrecognized sender gets the existing "I don't recognize you" reply and no row. An empty payload gets a fixed usage reply and no row. A command message is never consumed by the BOT_BLOCKED paste-recovery path.
6. The `stage_meteorite` hop classifies unclassified `NEW` rows with Ruth (same classifier and prompt as email staging), then routes them the way it routes classified rows today: link → `SCRAPE_LINK`, text → `CHECK_UNIQUE`. Not-a-job content → `NOT_A_JOB`. A classify failure → `NEW_EMAIL_ERROR` (the existing human-reset stage-failure state). When a blob holds several postings, the original row takes the first and each additional posting becomes its own classified `NEW` row. Rows that are already classified route exactly as they do today.

## Pipeline flow

No new states and no new dispatch rows. A new **birth** enters the existing meteorite staging spine (`METEORITE_STATES`, AST-1557 / AST-1773), and the `NEW` hop gains a classify step for unclassified rows:

| State (or trigger) | Dispatch `task_key` / handler | Next state(s) |
| -- | -- | -- |
| Slack `@Estelle /add-job <payload>` (bound sender) | Contact command intercept in `handle_slack_event` → registry handler (meteorite Slack-command insert) | meteorite `NEW` (`source_kind = slack`, `classify_outcome` empty) |
| `NEW`, unclassified | `stage_meteorite` → `run_stage_meteorite` → Ruth classify (`stage_meteorite` agent task) | `NOT_A_JOB` / `NEW_EMAIL_ERROR`; otherwise the row is filled from job 1 and falls through to the classified branch below, and jobs 2..N are inserted as classified `NEW` rows (routed next run) |
| `NEW`, classified | `stage_meteorite` → `run_stage_meteorite` (unchanged) | `SCRAPE_LINK` (http link) / `CHECK_UNIQUE` (text) / `SCRAPE_ERROR` (miss) |
| `SCRAPE_LINK` | `scrape_meteorite` → `run_scrape_meteorite` | `CHECK_UNIQUE` / `BOT_BLOCKED` / `LINK_EXPIRED` / `SCRAPE_ERROR` |
| `CHECK_UNIQUE` | `check_unique_meteorite` → `run_check_unique_meteorite` | `READY` / `DUPLICATE` |
| `READY` | `land_meteorite` → `run_land_meteorite` | `LANDED`, which **creates the** `job` at `METEORITE_NEW` (Ruth `qualify_meteorite` takes over) |

The hops run on the candidate's existing per-candidate `dispatch_task` rows (seed `auto_mode = 0`, so they run on click or when the operator turns AUTO on). This epic does not change that.

## Component scope

* `src/core/meteorite.py` — **modified** — new public entry that inserts one Slack-sourced raw `NEW` row from a link or pasted text, plus a `run_stage_meteorite` branch that Ruth-classifies unclassified `NEW` rows and fans out multi-posting blobs.
* `src/utils/config.py` — **modified** — `CONTACT_CONFIG` commands registry (command id → handler, mode `code`/`agent`, usage/ack reply texts) with import-time asserts.
* `src/core/contact.py` — **modified** — command parse (strip leading mentions, unwrap Slack `<url|label>` link markup), intercept in `handle_slack_event` ahead of paste recovery and the Estelle turn, mode-driven reply (`code` → fixed ack/usage post; `agent` → one Estelle turn with the command result), activity/info logging.

## Technical scope

* `src/core/meteorite.py` (insert): new public function. It takes a candidate id, the payload (already unwrapped by Contact), a Slack source id (event-scoped, e.g. channel + message ts), and a thread anchor. It inserts one row via the existing `_insert_stage_rows` / `insert_meteorite_rows` path at `NEW` with `source_kind = "slack"`, `content` = the payload, `classify_outcome` empty, and `estelle_thread_ts` = thread anchor (so a later BOT_BLOCKED nag lands in the same thread). It returns an `{ok, meteorite_id}`-shaped dict. On bad input it soft-fails (`ok=False`) and never raises into Contact. Link-vs-text is **not** decided here; Ruth decides at the stage hop.
* `src/core/meteorite.py` (stage hop): modify `run_stage_meteorite` so a claimed row with empty `classify_outcome` is classified via the existing `_classify_stage_blob` (tied to the claim's entity batch id rather than a self-minted one) and mapped via `_map_classify_jobs_to_meteorite_rows`. Skip outcomes → row `NOT_A_JOB`. Classify or map failure → row `NEW_EMAIL_ERROR` with `error` set. Landable outcomes → write job 1's `classify_outcome` / `content` / `link` / `job_title` / `employer_name` / electronic contact onto the row, then fall through to the existing classified-row routing in the same pass. Jobs 2..N are inserted as classified `NEW` rows with the same `source_kind` / `source_id`. The existing classified-row branch is unchanged.
* `src/utils/config.py`: new `commands` block inside `CONTACT_CONFIG` (name is plan-child's), keyed by command id. Each entry has a handler dotted path (must resolve under `src.core.`), mode ∈ {`code`, `agent`}, description, usage reply text, and an ack reply template with a meteorite-id placeholder. `add-job` → meteorite Slack-command insert, mode `code`. Import-time asserts cover shape, mode vocabulary, and no id collision with `CONTACT_TASK_CONFIG` keys or `CONTACT_CONFIG["skills"]`.
* `src/core/contact.py`: new parse helper that returns `(command_id, payload)` or nothing. It strips leading `<@U…>` mentions, matches `/<command>` against the config registry only, and unwraps Slack `<url|label>` / `<url>` markup in the payload. New intercept step in `_handle_slack_event_body`, after known/unknown recognition and **before** `try_meteorite_apply_paste_from_slack` and `run_contact_estelle_turn`, for a bound sender with a matched command:
  * It resolves and calls the registry handler.
  * In `code` mode, it posts the ack (or the usage text on an empty payload) via `contact_post_message` in-thread, and sets `estelle_turn` to a result with `outcome` = the command id and its `slack_post`, so the existing `_emit_listen_info` / hear-ack bookkeeping sees a posted reply.
  * In `agent` mode, it calls `run_contact_estelle_turn` once with the command result added to the turn's live content. This is a small modification to that function: an optional extra-context parameter.
  * Paste recovery is skipped for that event either way.

## Architectural definition

* **Patterns to reuse:**
  * `patt.entity.batch-processing` — the stage hop's new classify step runs inside the dispatcher's claimed batch; the Ruth `agent_data` rows join on the claim's batch id. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>)
  * For the Contact intercept, `no established pattern applies`. The closest precedent is the AST-1561 pre-turn paste-recovery intercept, which is product code, not a catalog pattern.
* **New patterns proposed:** `patt.contact.command-intercept` *(proposed — needs Archie approval)*. A `CONTACT_CONFIG` commands registry keyed by command id declares handler + mode (`code` | `agent`). Contact intercepts `/<command>` (first token after mentions) before paste recovery and the LLM turn, dispatches to a `src.core.*` handler, and replies per mode. `/add-job` is the first consumer.
* **Applicable statutes:**
  * `astral.batch.claim-process-release` — `run_stage_meteorite` still claims, processes, and releases every claimed row, including rows that fan out or fail classify. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.batch.claim-process-release.md>)
  * `astral.entity.required-metadata` — inserted rows (the Slack row and fan-out siblings) carry the full meteorite batch/state metadata set; use the existing insert path, never a hand-rolled INSERT. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.entity.required-metadata.md>)
  * `stat.logging.info.contact` — the accepted command event and its action (command id, mode, meteorite id) is the Contact production record line. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.contact.md>)
  * `stat.logging.info.entity` — meteorite rows entering `NEW` and leaving it via the classify branch emit entity success lines (existing `_meteorite_state_info`). [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
  * `stat.logging.info.dispatcher` — the stage hop's rollup summary counts the classify-branch rows the same way as today's rows. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.dispatcher.md>)
  * `stat.logging.debug` — parse/insert/classify/post calls log in/out under the debug contract. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
  * `stat.logging.warning` / `stat.logging.error` — soft-fail (bad payload, insert miss, classify fail) and post failures log once with who/why/next step. [warning](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>) · [error](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)

## Acceptance criteria

 1. **Link payload lands raw at NEW.** A bound candidate posts `@Estelle /add-job www.dice.com/jobs/13234abcd`, and the event text arrives as `<@UBOT> /add-job <http://www.dice.com/jobs/13234abcd|www.dice.com/jobs/13234abcd>`. Then `SELECT candidate_id, state, source_kind, classify_outcome, content FROM meteorite ORDER BY id DESC LIMIT 1` returns that candidate, `NEW`, `slack`, NULL, and `http://www.dice.com/jobs/13234abcd`. **Fail:** no new row, any other state, a non-NULL `classify_outcome`, or `<`, `>` or `|` left in `content`.
 2. **Text payload lands raw at NEW.** `@Estelle /add-job <multi-line pasted JD>` inserts exactly one row with `state = NEW`, `classify_outcome` NULL, and `content` equal to the pasted text with the mention and command token removed. **Fail:** `content` still holds `/add-job` or `<@U…>`, or more than one row is inserted.
 3. `code` **mode: no LLM turn, one ack.** In a component test with `do_task` patched and `add-job` at its shipped `code` mode, handling an `/add-job` event calls `do_task` **zero** times. The result has `estelle_turn.outcome == "add-job"`, and there is exactly one `contact_post_message` call whose text contains the new meteorite id. **Fail:** any `do_task` call, no ack, or a second (hear-ack) post.
 4. `agent` **mode is honored from config.** With the `add-job` registry entry patched to `agent`, the same event inserts the row and then calls `run_contact_estelle_turn` exactly once, with live content that contains the new meteorite id. The Slack reply is that turn's reply. **Fail:** zero or two turns, or the id is absent from the turn's live content.
 5. **Paste recovery is not triggered.** With a `BOT_BLOCKED` meteorite row already present for the candidate, `/add-job <text>` inserts a new `NEW` row, and the `BOT_BLOCKED` row's `content` and `state` are unchanged. **Fail:** `apply_paste` called, or the BOT_BLOCKED row is modified.
 6. **Unknown sender and empty payload.** An unbound sender's `/add-job …` posts the existing unknown-recognition text and inserts no meteorite row (row count unchanged). A bound sender's bare `@Estelle /add-job` posts the config usage text and inserts no row. **Fail:** any row inserted in either case.
 7. **Only the leading command is recognized.** `@Estelle can you /add-job this later` takes the normal Estelle turn path (`do_task` called once, no meteorite insert). **Fail:** an insert, or the turn is skipped.
 8. **Stage hop classifies unclassified NEW rows.** With Ruth's `do_task` patched, `run_stage_meteorite` routes rows as follows:
    * The AC1 row (Ruth → `link_list`, one job) goes to `SCRAPE_LINK` with `link` = the URL.
    * The AC2 row (Ruth → `single_jd_no_link`) goes to `CHECK_UNIQUE`.
    * A row Ruth calls `not_job_content` goes to `NOT_A_JOB`.
    * A Ruth failure leaves the row at `NEW_EMAIL_ERROR` with `error` set.
    * A `multi_jd_inline` result with 3 jobs leaves the original row routed plus **2** new classified `NEW` rows sharing its `source_id`.

    **Fail:** any unclassified row ends at `SCRAPE_ERROR` with `error = "missing classify_outcome"`, or the fan-out count is wrong.
 9. **Classified rows unchanged.** An existing component test fixture of a `NEW` row that already carries `classify_outcome` routes exactly as on `origin/dev` today, and `do_task` is called zero times for it. **Fail:** a Ruth call or a different target state.
10. **Batch join.** `agent_data` rows written by the stage hop's classify step carry the dispatcher claim's `batch_id` (`SELECT DISTINCT batch_id FROM agent_data WHERE task_key = 'stage_meteorite' AND …` equals the claim id), and every claimed row is released (batch fields cleared) after the run. **Fail:** a self-minted `stage_meteorite-stage-…` batch id from the hop, or a row left claimed.
11. **Registry, not literals.** `rg -n "['\"]/?add-job['\"]" src/core/` returns no matches; the command id and its mode appear only in `src/utils/config.py`. **Fail:** a quoted command literal or a parallel command/mode map in `src/core/`.
12. **Production record.** Each successful command emits, at INFO without debug, one contact info line naming the sender, event, command id, mode, and meteorite id, plus one meteorite entity info line for the row entering `NEW`. **Fail:** either line absent with debug off.

## Open questions

none

## Proposed child tickets

#### 1!: **Raw NEW meteorite insert + stage-hop classify - Ada**

Owns the meteorite side. It adds the public entry that saves one Slack-sourced raw blob at `NEW`, and teaches `run_stage_meteorite` to Ruth-classify unclassified `NEW` rows (in-place first job, fan-out siblings, `NOT_A_JOB` / `NEW_EMAIL_ERROR` on skip/failure) without changing the classified-row path. Ships AC8, AC9, and AC10, plus the AC1/AC2 row shape when the entry is called directly. Does **not** own Slack parsing, the command registry, or replies (#2).
**Citations:** `patt.entity.batch-processing`, `astral.batch.claim-process-release`, `astral.entity.required-metadata`, `stat.logging.info.entity`, `stat.logging.info.dispatcher`, `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`.
**Scope:** `src/core/meteorite.py` (modified — new public entry that inserts one Slack-sourced raw `NEW` row from a link or pasted text, plus a `run_stage_meteorite` branch that Ruth-classifies unclassified `NEW` rows and fans out multi-posting blobs). Technical (insert): new public function taking candidate id, payload, Slack source id, and thread anchor. It inserts via `_insert_stage_rows` / `insert_meteorite_rows` at `NEW` with `source_kind = "slack"`, `content` = payload, `classify_outcome` empty, and `estelle_thread_ts` = thread anchor, and returns `{ok, meteorite_id}`. It soft-fails and never raises into Contact; link-vs-text is decided by Ruth at the stage hop. Technical (stage hop): `run_stage_meteorite` classifies empty-`classify_outcome` rows via `_classify_stage_blob` (tied to the claim's entity batch id) and maps via `_map_classify_jobs_to_meteorite_rows`. Skip outcomes → `NOT_A_JOB`. Classify/map failure → `NEW_EMAIL_ERROR` with `error`. Landable outcomes → job 1's fields are written onto the row and it falls through to the existing classified routing in the same pass, and jobs 2..N are inserted as classified `NEW` rows with the same `source_kind` / `source_id`. The classified-row branch is unchanged.
Estimate: 5

#### 2: **Contact command registry +** `/add-job` **intercept - Hedy**

After #1. Owns the `CONTACT_CONFIG` commands registry (handler + `code`/`agent` mode), recognizing `@Estelle /<command> …` in Slack events ahead of paste recovery and the Estelle turn, and the mode-driven reply. Ships AC1–AC7, AC11, and AC12 end to end. Does **not** own the row insert or the stage hop (#1).
**Citations:** `patt.contact.command-intercept` (proposed), `stat.logging.info.contact`, `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`.
**Scope:**

* `src/utils/config.py` (modified — `CONTACT_CONFIG` commands registry (command id → handler, mode `code`/`agent`, usage/ack reply texts) with import-time asserts). Technical: new `commands` block in `CONTACT_CONFIG` keyed by command id, with handler dotted path under `src.core.`, mode ∈ {`code`, `agent`}, description, usage text, and ack template with a meteorite-id placeholder. `add-job` ships in `code` mode. Asserts cover shape, mode vocabulary, and no collision with `CONTACT_TASK_CONFIG` / `CONTACT_CONFIG["skills"]`.
* `src/core/contact.py` (modified — command parse (strip leading mentions, unwrap Slack `<url|label>` link markup), intercept in `handle_slack_event` ahead of paste recovery and the Estelle turn, mode-driven reply (`code` → fixed ack/usage post; `agent` → one Estelle turn with the command result), activity/info logging). Technical:
  * Parse helper returns `(command_id, payload)` or nothing: strip leading `<@U…>`, match `/<command>` against the registry only, unwrap `<url|label>` / `<url>`.
  * Intercept in `_handle_slack_event_body` after known/unknown recognition and before `try_meteorite_apply_paste_from_slack` / `run_contact_estelle_turn` calls the registry handler.
  * `code` mode posts the ack (or usage on an empty payload) via `contact_post_message` in-thread and sets `estelle_turn` with `outcome` = command id and its `slack_post`.
  * `agent` mode calls `run_contact_estelle_turn` once with the command result added via a new optional extra-context parameter.
  * Paste recovery is skipped for command events.

Estimate: 3

**New patterns:** #2 introduces `patt.contact.command-intercept`. Future Slack commands reuse it by adding a `CONTACT_CONFIG` commands row (handler + mode) and a `src.core.*` handler.

**Monolith check:** Functional scope N = 6, children M = 2. The split follows layers: #1 is the core meteorite table and stage hop, and #2 is the Contact transport and its config registry.

**Scope partition check:** `src/core/meteorite.py` → #1; `src/utils/config.py` → #2; `src/core/contact.py` → #2. Every Component and Technical scope item is claimed exactly once.

**Adjacency:** [AST-1637](https://linear.app/astralcareermatch/issue/AST-1637) (Discussion) plans to rework `run_contact_estelle_turn` / the post-resolve hand-off in `src/core/contact.py`. This epic's intercept sits *before* that hand-off, and #2's `agent` mode adds one optional parameter to `run_contact_estelle_turn`. Whichever lands second rebases on the other.

---

## Original brief

Give Estelle (the bot) a skill like "/add-job <pasted text>" and save that as a NEW state meteorite in the table by the same name.  A candidate in their channel could post `@Estelle /add-job www.dice.com/jobs/13234abcd`.

### Comments

#### chuckles — 2026-10-08T09:55:44.323Z
@susan — merge order: merge [PR #258](https://github.com/susansomerset/astral/pull/258) (AST-2028) **before** [PR #259](https://github.com/susansomerset/astral/pull/259) (this epic).

Betty's tests-branch merge carried AST-2028's test commits (AST-2029/2030/2031) onto this `ftr`. Those tests cover AST-2028 product code that is only in #258 and isn't on `dev` yet, so merging #259 first would land failing tests on `dev`.

#### chuckles — 2026-10-08T05:58:39.549Z
AST-2035 ESCALATE — Radia clean on code (no fix-now) but `patt.contact.command-intercept` is not in canon; gated on [AST-2036](https://linear.app/astralcareermatch/issue/AST-2036) for Archie approval.

#### chuckles — 2026-10-08T05:26:30.878Z
AST-2034 estimate 5→3 — one file, reuses existing classify/map/insert helpers; no schema/config change.

#### chuckles — 2026-10-08T04:33:13.345Z
@susan

1. **How should the `NEW` row get routed forward?** Today the stage hop (`run_stage_meteorite`) fails any `NEW` row that has no classifier outcome, so it ends up at `SCRAPE_ERROR`. Email ingest avoids this because Ruth classifies inline and the rows skip `NEW`.
   * **(A) — recommended:** `/add-job` stamps the existing outcome for its payload type (link → scrape, text → uniqueness check). No LLM runs at this hop, and Ruth still qualifies the job after it lands. The downside is that the "not a job" filter and multi-job splitting are skipped.
   * **(B):** leave the outcome empty and teach the stage hop to Ruth-classify unclassified `NEW` rows. This means more scope plus an LLM call per command.
   * **(C):** classify inline like email does. The row skips `NEW`, which contradicts your brief.
2. **Should Estelle skip her LLM turn for `/add-job`** and just post a fixed "saved meteorite #N" confirmation? Or should she also chat after saving?
3. **Is `@Estelle /add-job …` OK as the form everywhere, including DMs?** Slack's client grabs any message that *starts* with `/` as a slash command, so a bare `/add-job` won't send in a DM. A real registered Slack slash command would need a Slack app manifest change and a new endpoint, which is out of scope as drafted.

---

_Implementation detail may live in git history on `origin/dev`._
