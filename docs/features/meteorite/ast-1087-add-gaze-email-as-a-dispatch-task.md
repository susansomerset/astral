# AST-1087 — Add gaze_email as a dispatch task

<!-- linear-archive: AST-1087 archived 2026-08-11 -->

## Linear archive (AST-1087)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-1128

### Description

## Purpose

Meteorite jobs currently enter the funnel when someone uses Manage Email Create by hand. Candidates already forward or auto-send job mail into the shared Astral Gmail inbox; leaving that mail parked until a human clicks Create delays GDL and burns attention. This epic adds a `gaze_email` dispatch task that reads that inbox, binds each message to a known candidate when possible, ingests actionable mail into **METEORITE_NEW** (with scrape / Ruth parse / per-candidate dedupe as the message shape requires), and cleans up the mailbox (archive processed mail; age-gated trash for unbound stale mail) so the product can keep pace with inbound meteorites without a human sitting on Manage Email.

## Functional scope

1. `gaze_email` **dispatch task** — Register `gaze_email` like any other task and provision one `dispatch_task` row for the shared Astral inbox with `candidate_id` null allowed (table must not require a candidate on every row) and `auto_mode` true on that row — normal dispatch machinery, not a special AUTO subtype. On each run it lists inbox (non-archived) messages for the configured Astral mail account and processes them per the rules below. Account identity and unbound-retention window are config-driven (default account `astral.career.match@gmail.com`; default unbound keep window 7 days).
2. **Unbound message handling** — If a message cannot be bound to a known candidate (existing From→candidate bind): if received within the configured retention window, leave it untouched (candidate email may be added later); if older than that window, move it to Gmail **Trash** (not permanent delete).
3. **Bound message shape routing** — For messages bound to a candidate, classify and act:
   * **No subject + body is pure HTML** — Ruth (little-brain) parses the HTML for meteorite job links and metadata **using that bound candidate’s API key**; each link is scraped as its own job description; each job is deduped **for that candidate** (same job may exist for another candidate); survivors save as **METEORITE_NEW**; then archive the message.
   * **Subject is a URL + no body text** — Scrape that URL as the job description; per-candidate dedupe; save **METEORITE_NEW**; archive.
   * **Subject and body text present** — Ruth parses the HTML (bound candidate’s API key) for content and any likely job-description link. If a job link exists: scrape it, append the email subject + body to the scraped JD text (so later analysts see how the job arrived), per-candidate dedupe, save **METEORITE_NEW**, archive. If no job link: use subject + body as the JD text, per-candidate dedupe, save **METEORITE_NEW**, archive.
   * **Subject that is not a URL + no body text** — Ignore (leave in inbox). Attachments are out of scope.
4. **All-duplicate archive** — If a bound message yields only per-candidate duplicate skips (no new **METEORITE_NEW** rows), still **archive** the message.
5. **Reuse existing meteorite landing** — Created jobs land in **METEORITE_NEW** via the established meteorite create / gazer ingest surfaces where they already fit; this epic does not run `qualify_meteorite` or GDL in the same hop.
6. **Debug observability (backend)** — When `debug=True` on the touched paths, log what was found and what was recorded per message and per job outcome (Style D index headers with `index N/M`, primary id, outcome; working detail lines prefixed with two spaces, pipe, two spaces; long payloads truncated per AST-538 / Code Rules). No React debug requirements.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — `gaze_email` task registration, Astral inbox account expectation, unbound retention days, and Ruth email-parse task literals live in named config blocks; secrets/tokens stay in environ.
  * `pattern.state.entity-state-transitions` — ingest stops at **METEORITE_NEW**; no daisy-chain into qualify/GDL in this run.
  * `pattern.layers.import-discipline` — Gmail mutate (list/get/archive/trash) stays external; core owns bind/classify/orchestrate; existing dispatcher admin covers the row like any other task.
* **New patterns proposed**
  * none — null `candidate_id` on a normal `dispatch_task` row plus mailbox I/O is a schema/allowance + runner body, not a new catalog pattern.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — retention days, task key, parse task key in config.
  * `astral.config.secrets-and-env-specific-from-environ` — Gmail OAuth / refresh token / mailbox user remain environ; candidate API keys resolved per bound candidate at Ruth call time.
  * `astral.layers.core-vs-external-bright-line` — Gmail API I/O in external; policy in core.
  * `astral.layers.import-direction` — layer import direction.
  * `astral.standards.no-hardcoded-sets` — no inline retention windows / task keys / shape enums outside config.
  * `astral.standards.debug-contract-gated` — Style D only when `debug=True`.
  * `astral.standards.in-scope-only` — attachments, Manage Email redesign, qualify/GDL out; no special-case AUTO subtype for this task.
  * `astral.state.no-daisy-chain-in-run` — create to **METEORITE_NEW** only; qualify remains a later dispatch hop.
  * `astral.state.core-decides-transitions` — core chooses job landing state from config.
  * `universal` product-code set as implied by the above for any `src/` change.

## Boundaries

* Does **not** invent an “AUTO task” subtype or special dispatch path for `gaze_email` — `auto_mode` on the `dispatch_task` row is enough.
* Does **not** redesign Manage Email UI; manual Create may remain for exception handling.
* Does **not** own `qualify_meteorite`, GDL, Recommended, or LIKE/upshot hops.
* Does **not** process attachments or non-inbox labels beyond archive/trash outcomes named in scope.
* Does **not** permanently delete unbound mail — Trash only.
* Does **not** claim company boards or revive retired `gaze_board`.
* Does **not** change From→candidate bind rules (reuses existing bind); does not invent fuzzy candidate matching.
* Per-candidate dedupe is intentional for this path: the same external job may be saved again for a different candidate. Do not silently force AST-1061 global `job_link` skip across candidates for `gaze_email` outcomes.
* Does not send outbound mail from this task (monitor/send paths unchanged except shared credential use for archive/trash).
* Ruth calls for a bound message must use **that candidate’s** API key — not a shared/system key.

## Acceptance criteria

1. With a `gaze_email` `dispatch_task` row (`candidate_id` null, `auto_mode` true) running under normal dispatch, a bound inbox message matching each in-scope shape produces the corresponding **METEORITE_NEW** job(s) for that candidate (including subject+body appended when a job link was scraped), and the message is archived afterward.
2. A bound message with non-URL subject and empty body remains in the inbox (ignored); no job is created.
3. An unbound message newer than the configured retention window remains in the inbox unchanged.
4. An unbound message older than the configured retention window is moved to Gmail **Trash** and does not create a job.
5. When the same job link is ingested for two different candidates, both may receive a **METEORITE_NEW** row; when the same candidate receives a duplicate job already known for that candidate, create is skipped for that job; if a bound message produces only such skips, the message is still **archived**.
6. Account address and unbound retention days are read from config (defaults per Functional scope); Gmail secrets remain environ-only; Ruth invocations for bound mail use the bound candidate’s API key.
7. A single run does not advance jobs past **METEORITE_NEW** into qualify/GDL.
8. With `debug=True`, each processed message and each create/skip/trash/archive/ignore outcome is visible in Style D debug output (found + recorded); with `debug=False`, no new debug noise from this path.
9. The `dispatch_task` schema/provision path allows `candidate_id` null for `gaze_email` (no table-level requirement that every dispatch row have a candidate).

## Dependencies and blockers

* Prior shipped foundations (not blockers to start planning, required for live UAT): AST-1032 inbox read, AST-1044/AST-1047 bind, AST-1049/AST-1061 meteorite email ingest + **METEORITE_NEW** create, AST-1056/AST-1060 landing/qualify separation.
* **Ops/UAT verify:** Archie expects the existing `GOOGLE_REFRESH_TOKEN` already includes Gmail modify (or equivalent) for archive/trash — confirm at live UAT; remint only if verification fails.
* No open sibling Meteorite epics in flight that overlap this scope (board survey: Meteorite project otherwise Done).

## Open questions

none

## Proposed child tickets

#### 1!: **gaze_email config + null-candidate dispatch shell + Gmail archive/trash - Ada**

Owns config for Astral inbox expectations + unbound retention days; allows/provisions one `gaze_email` `dispatch_task` row with **null** `candidate_id` and `auto_mode` true (schema must not require candidate; no special AUTO subtype); extends Gmail external for archive + Trash (modify-capable credential contract). Does **not** own Ruth parse prompts or the per-message decision tree (siblings #2 / #3).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.config.secrets-and-env-specific-from-environ`; `astral.layers.core-vs-external-bright-line`; `astral.standards.in-scope-only`.

#### 2!: **Ruth little-brain meteorite email parse task - Katherine**

Owns the Ruth TASK_CONFIG / agent-task slice that accepts email HTML (and related shape inputs) and returns meteorite job links/metadata and/or a likely JD link + content hints for the subject+body path. **Must use the bound candidate’s API key** for the consult. Does **not** scrape URLs, create jobs, or mutate Gmail (sibling #3).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.config.secrets-and-env-specific-from-environ`; `astral.standards.in-scope-only`.

#### 3: **gaze_email runner — bind, route, scrape, dedupe, create, mailbox outcomes - Hedy**

After #1 and #2: core runner for the null-`candidate_id` `gaze_email` row that lists inbox, binds From→candidate, applies unbound age→Trash rules, routes bound shapes, calls Ruth with the bound candidate’s API key when required, scrapes links, per-candidate dedupes, creates **METEORITE_NEW**, archives on success **or** all-duplicate skip, Style D debug. Wire through normal dispatch like any other task body. Reuses meteorite create / gazer scrape helpers where they already match; does not own config shell or Ruth task definition.
**Citations:** `pattern.state.entity-state-transitions`; `astral.state.no-daisy-chain-in-run`; `astral.standards.debug-contract-gated`; `astral.layers.core-vs-external-bright-line`; `astral.standards.in-scope-only`.

**New patterns:** none.

**Monolith check:** Functional scope has 6 capabilities; 3 children — null-candidate shell + Gmail mutate, Ruth parse (candidate API key), and runner — split across layers intentionally.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1087 (parent) | ftr/AST-1087-add-gaze-email-as-a-dispatch-task |
| AST-1088 | sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash |
| AST-1089 | sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task |
| AST-1090 | sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox |

**Epic worktree:** `astral-AST-1087/` — one active sub checked out at a time.

* **AST-1106**: `sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`
* **AST-1107**: `sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/bd90604213fc3049015e64d030a28960/4371df31-c8e2-466c-a424-665fd6ec867d/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/bd90604213fc3049015e64d030a28960/4b78d50a-11c0-4c02-a2af-e4a793795bd6/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/bd90604213fc3049015e64d030a28960/1a68210c-fddf-49fe-91e9-fbe4cfeb0b8f/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/c2766d47-327b-42c4-95fe-7d5cf64ef7ad/store.db` |
| Radia | review | `/home/susan/.cursor/chats/bd90604213fc3049015e64d030a28960/73bf7e66-09e6-460e-96c1-5833b03d271a/store.db` |

---

## Original brief

Please create a new task that will do the following:

1. Check email at the astral email account (which should be config-driven as [astral.career.match@gmail.com](<mailto:astral.career.match@gmail.com>))
2. If email is found in the inbox (not archived) then open the email and assess it.
   1. If it cannot be bound to a known candidate
      1. If the email was received in the last 7 (config-driven) days, ignore it (candidate email may need to be added later so it can be bound).
      2. if the email was received before that, delete it.
   2. If it can be bound to a known candidate,
      1. If the email has no subject and the body is pure html,
         1. send the html to a little brain AI (Ruth) to parse the meteorite job links and metadata,
         2. scrape the links as separate job descriptions,
         3. dedupe each job for this candidate (job may be duplicate across candidates, that's fine)
         4. save each job as METEORITE_NEW.
         5. archive the email
      2. If the subject is a URL and there is no body text,
         1. scrape that link as the job description,
         2. dedupe the job,
         3. save the job as METEORITE_NEW.
         4. Archive the email message
      3. If there is a subject and body text,
         1. extract the html string of the email,
         2. send the html to Ruth to parse it for content and return any likely link to the job description, if the message included one.
            1. If the message had a joblink,
               1. scrape the job desc from the job link and append the email message subject and body to the job description text so the job analyst gets the full picture of how the job came to the candidate,
               2. dedupe job for the candidate
               3. save new job as METEORITE_NEW
               4. archive the email message.
            2. If the message has no job link,
               1. use the subject + body of the message to be the job description text
               2. dedupe job for the candidate
               3. save new job as METEORITE_NEW
               4. archive the email message.
      4. If there is a subject that is not a url and there is no body text, then ignore the message. (There may be an attachment, but that's out of scope for now)

### Comments

#### chuckles — 2026-08-02T18:58:38.019Z
[fix-uat] redesign supersede — no Bug children on this parent

Per Archie: null-candidate `gaze_email` design is wrong; replace rather than patch.

| New ticket | Status | Purpose |
| --- | --- | --- |
| **AST-1128** | Discussion @ Chuckles | Candidate-bound `gaze_email` redesign (`last_email_check`, bind-filtered inbox, Avail = bind count). Define-parent → later datt; lessons from AST-1087. |
| **AST-1129** | Discussion @ Chuckles | Manage Email multi-select + **Land Meteorite** (separate epic). |

AST-1087 → **Duplicate** of AST-1128. Prior UAT bugs AST-1106/AST-1107 stay historical under this parent.

— Chuckles

#### susan — 2026-08-02T18:53:59.024Z
Okay, we need to do a few things.  We need to do a candidate-specific gaze email where the binding is found for that candidate.  So, we say "Get the inbox email messages where the from binds to the selected candidate.  We need to add "last_email_check" as a field to candidate, default to null and update when gaze_email is run.  Gaze_email is candidate-bound, instead of candidate-free, and the Avail count comes from an api call to return the number of current messages in the inbox that bind to that candidate.

The above is all in the scope of this ticket, however we collectively did not design it correctly, so it needs to be replaced (marked as duplicate) to a new ticket for the same purpose, starting in Discussion and set to chuckles to revamp the design and we can run datt on the new ticket with a reference to this one for lessons learned.

Let's also create the manage email update ticket as a separate epic with a brief, accurate description of what we need (no fancy sections), and go ahead and set it to Discussion and assign it to chuckles.

#### chuckles — 2026-08-02T17:29:19.821Z
[fix-uat] blocked: open questions on parent

@susan — your latest note asks to refactor Manage Email so you can multi-select inbox messages and click **Land Meteorite** to run `gaze_email` only for those selections, and you want that in scope here.

I cannot file a Bug against an existing AC: none of the Acceptance criteria describe Manage Email selection / Land Meteorite, and **Boundaries** currently say this epic does **not** redesign Manage Email UI (manual Create may remain for exceptions).

Need a call before I open a UAT child:

1. Expand AST-1087 (amend AC + Boundaries to include inbox multi-select → Land Meteorite → `gaze_email` on selected ids only), **or**
2. Keep Manage Email out of this epic and file a follow-on Feature for that UI?

Also confirm: Land Meteorite should invoke the same bind/route/scrape/dedupe/archive path as the dispatcher `gaze_email` row, just filtered to the selected message ids — not a separate ingest pipeline?

— Chuckles

#### susan — 2026-08-02T17:27:35.818Z
I forgot to include that I would like to refactor the Manage Email a little bit, so that I can select emails from the inbox and click "Land Meteorite" button that will run the gaze_email job only for the selected emails, in scope with this ticket.

#### chuckles — 2026-07-31T18:28:43.105Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1106** | gaze_email missing from Scheduled Actions default view |
| **AST-1107** | Admin task_name should equal task_key for now |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1106** — _gaze_email missing from Scheduled Actions default view_
- **Issue reported:** On staging Task Dispatcher / Scheduled Actions after AST-1087 landed, Susan cannot find the `gaze_email` task at all (“I still don't see the gaze email task”).
- **Should now:** The shared null-`candidate_id` `gaze_email` `dispatch_task` row is visible and operable in Scheduled Actions / Task Dispatcher without hunting past filters that permanently hide mailbox tasks.
- **Quick check (this fix only):**
  1. Open Admin → Scheduled Actions (Task Dispatcher) on staging after deploy of AST-1087.
  2. Leave default filters (notably Avail **> 0**).
  3. Look for `gaze_email` (shared inbox / null candidate row).
  4. Observe: row is missing from the default view (or not present at all).

**AST-1107** — _Admin task_name should equal task_key for now_
- **Issue reported:** Admin switched from showing `task_key` to showing `task_name`. Susan cannot tell what is what, and she believes this broke task sections in Scheduled Actions. She wants task names to be their `task_key` for now.
- **Should now:** In Admin Task Prompts / Scheduled Actions catalog meta, each task’s displayed `task_name` equals its `task_key` (temporary clarity), and section grouping still works so she can find tasks including meteorite/gaze_email-related ones during UAT.
- **Quick check (this fix only):**
  1. Open Admin → Task Prompts (and Scheduled Actions section headers).
  2. Observe displayed names are friendly labels (or blank) rather than `task_key`.
  3. Try to locate tasks by key name / navigate sections — clarity is lost; sections feel broken.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### chuckles — 2026-07-31T18:26:47.527Z
[refresh-ftr] blocked: merge origin/dev into origin/ftr/AST-1087-add-gaze-email-as-a-dispatch-task

CONFLICT files:
- docs/test-bible/frontend/pages.md
- docs/test-bible/utils/config.md
- tests/component/utils/test_config.py

@Betty White — keep AST-1106/AST-1107 UAT blocks and origin/dev sibling content; push resolved tip to origin/ftr/AST-1087-add-gaze-email-as-a-dispatch-task. Chuckles will re-run refresh-ftr / prep-uat after.

— Chuckles

#### susan — 2026-07-31T17:35:49.872Z
First, we switched from using the task key in the Admin screen to using the task name, and for now, I would just like the task names to be their task_key, so I know what is what, and I believe it has caused issues with the task sections in scheduled actions.

Second, I still don't see the gaze email task

#### susan — 2026-07-31T01:42:41.933Z
Stop saying "AUTO gaze_email". it's just a task, and the dispatch_task record will have auto set to true.  Do not go crazy with special handling.

#### chuckles — 2026-07-31T00:40:02.287Z
@susan

1. For unbound-old mail, should “delete” mean Gmail **Trash** or **permanent delete**?
2. Confirm **one system-wide** AUTO `gaze_email` dispatch row (shared inbox) — not per-candidate dispatch rows.
3. Confirm ops will remint `GOOGLE_REFRESH_TOKEN` with a Gmail **modify** (or broader) scope so archive/delete can ship; readonly-only is insufficient.
4. If every job from a bound message is skipped as a per-candidate duplicate, should the message still be **archived**, or left in inbox?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
