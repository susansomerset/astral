# AST-1128 — gaze_email — candidate-bound dispatch (redesign)

<!-- linear-archive: AST-1128 archived 2026-08-11 -->

## Linear archive (AST-1128)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

AST-1087 proved mailbox ingest can land, but a **shared null-**`candidate_id` `gaze_email` **row** plus an Avail carve-out was the wrong shape for dispatcher UAT. This epic redesigns `gaze_email` so each candidate has a **candidate-bound** dispatch path: Scheduled Actions shows real per-candidate availability, a run only processes inbox messages that bind to **that** candidate, and the product records when that candidate’s mailbox was last checked. Keep the reusable Ruth parse / scrape / per-candidate dedupe / archive+trash pieces from AST-1087; do **not** carry the null-candidate shell forward as the primary design.

## Functional scope

1. **Candidate-bound** `gaze_email` **dispatch rows** — Replace the shared null-`candidate_id` `gaze_email` shell with normal per-candidate `dispatch_task` rows for `gaze_email`. **Every** `candidate` **gets a** `gaze_email` **row** (same coverage model as other candidate-scoped dispatch tasks). Retire the null-candidate row and any special “mailbox shell with fake/zero Avail” carve-out so `gaze_email` behaves like other candidate-scoped tasks in Scheduled Actions.
2. **Selected-candidate inbox filter** — On each `gaze_email` run for a candidate, list current Astral inbox (non-archived) messages and process **only** those whose From binds to **that** selected candidate. Reuse the established bind / shape-route / Ruth parse / scrape / per-candidate dedupe / **METEORITE_NEW** create / archive outcomes from the AST-1087 runner where they still fit; do not invent a second ingest pipeline.
3. `last_email_check` **on candidate** — Add `last_email_check` on `candidate` (default null). When `gaze_email` runs for a candidate, update that candidate’s `last_email_check` to the run time (whether or not any messages were processed).
4. **Real Avail count** — Avail for a candidate’s `gaze_email` row is the live count of current inbox messages that bind to that candidate (API/count path — not a hardcoded zero and not an always-visible-under-Avail-gt0 carve-out).
5. **Unbound inbox retention** — Messages whose From binds to no candidate stay in the inbox so a candidate can later add the unrecognized address and bind them (as designed). After the configured retention window (`unbound_retention_days`, already designed under AST-1087), move those unbound messages to Gmail **Trash**. This hygiene must run without restoring a null-candidate **primary** Avail/dispatch shell (shared mailbox hygiene invoked from the candidate-bound `gaze_email` path, or equivalent under normal dispatch).
6. **Debug observability (backend)** — When `debug=True` on touched paths, log what was found and what was recorded per candidate run, per message, and per job/mailbox outcome (Style D index headers with `index N/M`, primary id, outcome; working detail lines prefixed with two spaces, pipe, two spaces; long payloads truncated per AST-538 / Code Rules). No React debug requirements.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — `gaze_email` / `GAZE_EMAIL_CONFIG` / TASK_CONFIG shell moves to candidate-bound expectations; `unbound_retention_days` stays config-owned; secrets stay environ.
  * `pattern.layers.import-discipline` — Gmail list/get/archive/trash stays external; core owns bind filter, route, unbound hygiene, and orchestration; admin Avail surfaces stay thin.
  * `pattern.state.entity-state-transitions` — ingest still stops at **METEORITE_NEW**; no daisy-chain into qualify/GDL in this run.
  * `pattern.ui.admin-endpoint` — Scheduled Actions / dispatch Avail continues to read API-provided counts; remove special-case visibility flags for this task once Avail is real.
* **New patterns proposed**
  * none — per-candidate `dispatch_task` rows and external mailbox I/O already exist; this epic changes ownership from null-candidate shell to candidate-bound rows + real Avail, not a new catalog pattern.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — task key, account expectation, unbound retention days, runner literals remain config-owned.
  * `astral.config.secrets-and-env-specific-from-environ` — Gmail OAuth / mailbox user remain environ.
  * `astral.seed.other-via-coverage-join` — provision `gaze_email` for every row in `candidate` (not hardcoded candidate ids); null-candidate exception no longer applies as the primary design.
  * `astral.seed.define-approved` / `astral.seed.archie-catalog-wins` — any seed/catalog rename of the shell must stay Archie-named and catalog-aligned.
  * `astral.layers.core-vs-external-bright-line` / `astral.layers.import-direction` — Gmail I/O vs core policy.
  * `astral.standards.no-hardcoded-sets` / `astral.standards.in-scope-only` — no inline task-key / carve-out sets; Manage Email Land Meteorite is AST-1129.
  * `astral.standards.debug-contract-gated` — Style D only when `debug=True`.
  * `astral.state.no-daisy-chain-in-run` / `astral.state.core-decides-transitions` — land **METEORITE_NEW** only.
  * `universal` product-code set implied for any `src/` change.

## Boundaries

* Does **not** keep the shared null-`candidate_id` `gaze_email` row as the **primary** dispatch/Avail design (retire/supersede it).
* Does **not** keep the AST-1106-style always-visible-under-Avail-gt0 carve-out once Avail is a real bind-filtered count.
* Does **not** redesign Manage Email UI or own **Land Meteorite** multi-select (AST-1129) — but must leave a core path AST-1129 can call for the same ingest outcomes (coordinate; do not fork pipelines).
* Does **not** own `qualify_meteorite`, GDL, Recommended, LIKE/upshot, or attachments.
* Does **not** change From→candidate bind rules (reuses existing bind).
* Does **not** force AST-1061 global `job_link` skip across candidates — per-candidate dedupe remains intentional on this path.
* Does **not** permanently delete unbound mail — Trash only after retention.
* Does **not** send outbound mail.
* Does **not** invent a special AUTO subtype — `auto_mode` on normal `dispatch_task` rows is enough.
* AST-1087 is marked Duplicate of this epic; do not extend the null-candidate shell further under AST-1087 children.

## Acceptance criteria

1. There is no primary shared null-`candidate_id` `gaze_email` dispatch row in active use; **every** `candidate` has a `gaze_email` `dispatch_task` row bound to that `candidate_id`.
2. Running `gaze_email` for candidate A processes only current inbox messages whose From binds to A; messages that bind only to other candidates are left for those candidates’ rows.
3. After a `gaze_email` run for candidate A, `candidate.last_email_check` for A is non-null and reflects that run (including runs that found zero matching messages).
4. Scheduled Actions Avail for a candidate’s `gaze_email` row equals the live count of current inbox messages that bind to that candidate; zero-Avail rows are not kept visible by a `gaze_email`-specific carve-out.
5. An unbound message newer than `unbound_retention_days` remains in the inbox unchanged (so a later profile/email update can bind it).
6. An unbound message older than `unbound_retention_days` is moved to Gmail **Trash** without restoring a null-candidate primary Avail/dispatch shell.
7. Bound in-scope message shapes still produce the AST-1087 ingest outcomes for that candidate (**METEORITE_NEW** / archive / ignore rules as already established for bound mail); a single run does not advance jobs into qualify/GDL.
8. With `debug=True`, each candidate run, each considered message, and each create/skip/archive/trash/ignore outcome is visible in Style D (found + recorded); with `debug=False`, no new debug noise from this path.
9. Gmail secrets remain environ-only; Ruth invocations for a bound message continue to use **that candidate’s** API key; retention days remain config-owned.

## Dependencies and blockers

* Reuse foundations already shipped / landed under AST-1087 children (config including `unbound_retention_days`, Gmail archive/trash, Ruth `parse_meteorite_email`, runner helpers) — redesign in place; do not re-litigate bind or METEORITE_NEW create.
* Related sibling **AST-1129** (Manage Email Land Meteorite) should call the same core ingest path; not a hard blocker to start this epic, but coordinate so Land Meteorite does not fork a second pipeline.
* Prior Done foundations: AST-1032 inbox read, AST-1044/AST-1047 bind, AST-1049/AST-1061 meteorite ingest.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Retire null shell — candidate-bound config, schema, provision, last_email_check - Ada**

Owns retiring the shared null-`candidate_id` `gaze_email` provision/shell as the primary design; moves TASK_CONFIG / `GAZE_EMAIL_CONFIG` expectations to candidate-bound rows (keep `unbound_retention_days`); adds `candidate.last_email_check` (default null); provisions a `gaze_email` row for **every** `candidate` via coverage join; removes always-visible-under-Avail-gt0 special-casing for this task once Avail is real. Does **not** own the per-message runner decision tree (sibling #3) or the live bind-filtered Avail count implementation detail beyond making the shell honest (sibling #2).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.seed.other-via-coverage-join`; `astral.standards.in-scope-only`.

#### 2!: **Candidate-bound Avail count + dispatch eligibility - Hedy**

After #1 (or tightly with it): Avail / eligible count for a candidate’s `gaze_email` row is the live API count of current inbox messages that bind to that candidate; wire due/dispatch selection so candidate-bound rows fire under normal dispatch without the null-candidate mailbox carve-out. Does **not** own ingest shape routing or unbound Trash hygiene (sibling #3).
**Citations:** `pattern.layers.import-discipline`; `pattern.ui.admin-endpoint`; `astral.layers.core-vs-external-bright-line`; `astral.standards.no-hardcoded-sets`.

#### 3: **Candidate-bound gaze_email runner + last_email_check + unbound hygiene - Katherine**

After #1/#2: redesign the core runner so a run for candidate A filters inbox to From→A only, reuses Ruth/scrape/dedupe/create/archive outcomes for those messages, stamps `last_email_check`, and applies unbound leave-then-Trash after `unbound_retention_days` as shared mailbox hygiene **without** restoring a null-candidate primary Avail shell; Style D debug. Leaves a callable core path AST-1129 can reuse for selected message ids.
**Citations:** `pattern.state.entity-state-transitions`; `astral.state.no-daisy-chain-in-run`; `astral.standards.debug-contract-gated`; `astral.layers.core-vs-external-bright-line`; `astral.standards.in-scope-only`.

**New patterns:** none.

**Monolith check:** Functional scope has 6 capabilities; 3 children — shell/schema/provision, Avail/dispatch wiring, runner+unbound hygiene — split across layers intentionally.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1128 (parent) | ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign |
| AST-1134 | sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config |
| AST-1135 | sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility |
| AST-1136 | sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner |

* **AST-1144**: `sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`

**Epic worktree:** `astral-AST-1128/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/1c0e795437f6ce7d14a00499faa7508f/fafeec3f-315c-45eb-b656-77d7f0c5ed60/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/1c0e795437f6ce7d14a00499faa7508f/589b8517-425f-4878-8fad-3e0878bf108d/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/1c0e795437f6ce7d14a00499faa7508f/762aaa56-f27a-48c1-ad40-b19bc9b45d1a/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/854e300e-989c-4387-aebc-0cf6e206750f/store.db` |
| Radia | review | `/home/susan/.cursor/chats/1c0e795437f6ce7d14a00499faa7508f/e1279aa0-eaf0-43ad-8147-4e3312d9c66e/store.db` |

---

## Original brief

## Brief

Replace the shared null-`candidate_id` `gaze_email` design (shipped under AST-1087) with **candidate-bound** `gaze_email`:

* One `gaze_email` dispatch path per candidate (binding found for that candidate).
* On run: list inbox messages whose From binds to the **selected candidate** only.
* Add `last_email_check` on `candidate` (default null); update when `gaze_email` runs for that candidate.
* Avail count = API count of current inbox messages that bind to that candidate (not a fake/zero mailbox carve-out).

## Lessons from AST-1087

AST-1087 proved mailbox ingest / Ruth parse / scrape / per-candidate dedupe / archive+trash can land, but the **system-wide null-candidate row + Avail carve-out** model was the wrong product shape for dispatcher UAT. Keep reusable runner/parse/Gmail pieces where they still fit; do **not** carry forward the null-candidate shell as the primary design.

## Next

Chuckles runs **define-parent** here (Discussion), then datt when Archie moves to Todo. Reference AST-1087 for implementation lessons.

### Comments

#### chuckles — 2026-08-02T22:30:19.876Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1144** | parse_meteorite_email rejects jobs[].metadata dict (expects str) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1144** — _parse_meteorite_email rejects jobs[].metadata dict (expects str)_
- **Issue reported:** Running candidate-bound `gaze_email` for somerset on a bound html_links inbox message, Ruth `parse_meteorite_email` returned jobs with `metadata` as objects (`{"company":…,"location":…}`). Validation failed:
- **Should now:** Bound html_links mail whose Ruth parse yields job links (with optional company/location metadata) validates, scrapes/creates **METEORITE_NEW** (or per-candidate dedupe skip), and archives — same AST-1087 ingest outcomes under the candidate-bound runner.
- **Quick check (this fix only):**
  1. Ensure somerset has a `gaze_email` dispatch row and an inbox message From-bound to somerset whose body is HTML with Dice (or similar) job links.
  2. Run that somerset `gaze_email` row with debug on.
  3. Observe `parse_meteorite_email` validation error on `jobs[].metadata` dict vs str, and message left unprocessed / error outcome.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-08-02T21:50:12.725Z
```
[2026-08-02 21:49:20] DEBUG src.core.agent:  |           "company": "Vaco by Highspring"
[2026-08-02 21:49:20] DEBUG src.core.agent:  |         }
[2026-08-02 21:49:20] DEBUG src.core.agent:  |       }
[2026-08-02 21:49:20] DEBUG src.core.agent:  |     ],
[2026-08-02 21:49:20] DEBUG src.core.agent:  |     "jd_link": "",
[2026-08-02 21:49:20] DEBUG src.core.agent:  |     "content_text": ""
[2026-08-02 21:49:20] DEBUG src.core.agent:  |   }
[2026-08-02 21:49:20] DEBUG src.core.agent:  | }
[2026-08-02 21:49:20] ERROR src.core.agent: do_task validation failed. task_key='parse_meteorite_email' error=jobs[0]: Field 'metadata' must be str, got dict
[2026-08-02 21:49:20] DEBUG src.core.agent:  | agent_data_write block_type=RESPONSE outcome=new_content agent_data_id=gaze_email-16b25827-ab72-4245-b0b8-fd851a4d2c36-response-f7edac16e64e2b09 ref_agent_data_id=None
[2026-08-02 21:49:20] DEBUG src.core.gaze_email:  | ruth_fail=jobs[0]: Field 'metadata' must be str, got dict
[2026-08-02 21:49:20] DEBUG src.core.gaze_email: gaze_email.run index 1/1 19fc35a17d487cc9 -> error
[2026-08-02 21:49:20] DEBUG src.core.gaze_email: gaze_email.run index 1/1 somerset -> run-complete
[2026-08-02 21:49:20] DEBUG src.core.gaze_email:  | last_email_check=stamped
[2026-08-02 21:49:20] DEBUG src.core.gaze_email:  | summary={total_processed=1, total_passed=0, total_failed=0, total_errors=1}
[2026-08-02 21:49:19] DEBUG src.core.gaze_email: gaze_email.run index 1/1 somerset -> run-start
[2026-08-02 21:49:19] INFO googleapiclient.discovery_cache: file_cache is only supported with oauth2client<4.0.0
[2026-08-02 21:49:19] DEBUG src.core.candidate: get_candidate_id_for_query index 1/1 susan@susansomerset.com -> found|matched
[2026-08-02 21:49:19] DEBUG src.core.candidate:  | query=Susan Somerset <susan@susansomerset.com>
[2026-08-02 21:49:19] DEBUG src.core.candidate:  | needle=susan@susansomerset.com
[2026-08-02 21:49:19] DEBUG src.core.candidate:  | candidate_id=somerset
[2026-08-02 21:49:19] DEBUG src.core.inbox: inbox_from_bind index 1/1 19fc35a17d487cc9 -> found|matched
[2026-08-02 21:49:19] DEBUG src.core.inbox:  | from_address=Susan Somerset <susan@susansomerset.com>
[2026-08-02 21:49:19] DEBUG src.core.inbox:  | astral_candidate_id=somerset
[2026-08-02 21:49:19] DEBUG src.core.gaze_email: gaze_email.run index 1/1 19fc35a17d487cc9 -> found
[2026-08-02 21:49:19] DEBUG src.core.gaze_email:  | from_address=Susan Somerset <susan@susansomerset.com>
[2026-08-02 21:49:19] DEBUG src.core.gaze_email:  | astral_candidate_id=somerset
[2026-08-02 21:49:19] INFO googleapiclient.discovery_cache: file_cache is only supported with oauth2client<4.0.0
[2026-08-02 21:49:19] DEBUG src.core.gaze_email:  | shape=html_links
[2026-08-02 21:49:19] INFO src.core.agent: run_next chain entry: task=parse_meteorite_email batch_id=gaze_email-16b25827-ab72-4245-b0b8-fd851a4d2c36
[2026-08-02 21:49:19] DEBUG src.core.agent: do_task index 1/1 19fc35a17d487cc9 -> task start
[2026-08-02 21:49:19] DEBUG src.core.agent:  | task_key=parse_meteorite_email batch_id=gaze_email-16b25827-ab72-4245-b0b8-fd851a4d2c36 index=19fc35a17d487cc9 in_run_next_chain=False
[2026-08-02 21:49:19] INFO src.core.agent: [DEBUG] do_task('parse_meteorite_email'): brain_setting=Little provider=deepseek model=deepseek-v4-flash max_tokens=8192 temp=0.3 skip_cache=False candidate=somerset
[2026-08-02 21:49:19] DEBUG src.core.agent:  | llm_params provider=deepseek brain_setting=Little model=deepseek-v4-flash max_tokens=8192 temp=0.3 skip_cache=False candidate_id=somerset
[2026-08-02 21:49:19] DEBUG src.core.agent:  | blocks system=2 user=2 runtime_prompt_segments=4
[2026-08-02 21:49:19] INFO src.external.deepseek: LLM deepseek task=parse_meteorite_email 2.3s stop=end_turn tokens in=325 out=287
[2026-08-02 21:49:19] DEBUG src.external.deepseek: send_to_deepseek index 1/1 parse_meteorite_email -> success
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  | provider=deepseek model=deepseek-v4-flash task=parse_meteorite_email duration=2.3s stop_reason=end_turn
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  | vendor=deepseek-v4-flash tokens fresh=325 cache_read=4992 cache_write=0 output=287
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  | response_preview:
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  | {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |   "agent_performance": {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |     "status": "success"
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |   },
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |   "agent_payload": {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |     "parse_mode": "html_links",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |     "jobs": [
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |       {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "job_link": "https://www.dice.com/job-detail/3628bf85-8915-4525-93ff-2f05e09f9e39",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "job_title": "Health Data Services Operations & Strategy Director",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "metadata": {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |           "company": "Triune Infomatics Inc",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |           "location": "San Francisco, CA"
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         }
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |       },
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |       {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "job_link": "https://www.dice.com/job-detail/add50803-2af1-4f26-aba5-3997c9db8905",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "job_title": "Lead Systems Analyst",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "metadata": {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |           "company": "System One"
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         }
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |       },
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |       {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "job_link": "https://www.dice.com/job-detail/eaba0d1b-5258-4843-9ddc-5487b7985338",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "job_title": "Data Strategy / Business Analyst Consultant",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         "metadata": {
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |           "company": "Vaco by Highspring"
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |         }
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |       }
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |     ],
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |     "jd_link": "",
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |     "content_text": ""
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  |   }
[2026-08-02 21:49:19] DEBUG src.external.deepseek:  | }
[2026-08-02 21:49:19] DEBUG src.core.agent:  | agent_data_write block_type=SYSTEM outcome=ref_existing agent_data_id=gaze_email-16b25827-ab72-4245-b0b8-fd851a4d2c36-system-aaf5ce79148dd726 ref_agent_data_id='qualify_job_listings-b19b0d3b-c73b-4e4b-99d8-c282a16eb4e6-system-cbfb0bb55a6614f7'
[2026-08-02 21:49:19] DEBUG src.core.agent:  | agent_data_write block_type=CACHE_A outcome=ref_existing agent_data_id=gaze_email-16b25827-ab72-4245-b0b8-fd851a4d2c36-cache_a-37688c4f2cc636d1 ref_agent_data_id='gaze_email-6d9cb2c5-82d1-4887-83d9-05c4cc2b3c78-cache_a-daf76ea50b0bc0ef'
[2026-08-02 21:49:19] DEBUG src.core.agent:  | agent_data_write block_type=NO_CACHE outcome=ref_existing agent_data_id=gaze_email-16b25827-ab72-4245-b0b8-fd851a4d2c36-no_cache-4404ef8776802eed ref_agent_data_id='gaze_email-6d9cb2c5-82d1-4887-83d9-05c4cc2b3c78-no_cache-1245ebd7132089db'
[2026-08-02 21:49:19] DEBUG src.core.agent:  | agent_data_write block_type=TASK outcome=ref_existing agent_data_id=gaze_email-16b25827-ab72-4245-b0b8-fd851a4d2c36-task-d99d1fec71f24e91 ref_agent_data_id='gaze_email-6d9cb2c5-82d1-4887-83d9-05c4cc2b3c78-task-1d901c61b8aa2b25'
[2026-08-02 21:49:19] DEBUG src.core.agent:  | raw_response task_key=parse_meteorite_email lines=34 chars=952
[2026-08-02 21:49:19] DEBUG src.core.agent:  | {
[2026-08-02 21:49:19] DEBUG src.core.agent:  |   "agent_performance": {
[2026-08-02 21:49:19] DEBUG src.core.agent:  |     "status": "success"
[2026-08-02 21:49:19] DEBUG src.core.agent:  |   },
[2026-08-02 21:49:19] DEBUG src.core.agent:  |   "agent_payload": {
[2026-08-02 21:49:19] DEBUG src.core.agent:  |     "parse_mode": "html_links",
[2026-08-02 21:49:19] DEBUG src.core.agent:  |     "jobs": [
[2026-08-02 21:49:19] DEBUG src.core.agent:  |       {
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "job_link": "https://www.dice.com/job-detail/3628bf85-8915-4525-93ff-2f05e09f9e39",
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "job_title": "Health Data Services Operations & Strategy Director",
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "metadata": {
[2026-08-02 21:49:19] DEBUG src.core.agent:  |           "company": "Triune Infomatics Inc",
[2026-08-02 21:49:19] DEBUG src.core.agent:  |           "location": "San Francisco, CA"
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         }
[2026-08-02 21:49:19] DEBUG src.core.agent:  |       },
[2026-08-02 21:49:19] DEBUG src.core.agent:  |       {
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "job_link": "https://www.dice.com/job-detail/add50803-2af1-4f26-aba5-3997c9db8905",
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "job_title": "Lead Systems Analyst",
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "metadata": {
[2026-08-02 21:49:19] DEBUG src.core.agent:  |           "company": "System One"
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         }
[2026-08-02 21:49:19] DEBUG src.core.agent:  |       },
[2026-08-02 21:49:19] DEBUG src.core.agent:  |       {
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "job_link": "https://www.dice.com/job-detail/eaba0d1b-5258-4843-9ddc-5487b7985338",
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "job_title": "Data Strategy / Business Analyst Consultant",
[2026-08-02 21:49:19] DEBUG src.core.agent:  |         "metadata": {
```

Why wasn't this caught by test coverage?

#### chuckles — 2026-08-02T21:01:11.607Z
[refresh-ftr] blocked: merge origin/dev into ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign

* `src/utils/config.py` — inventory docstring (METEORITE_EMAIL_INGEST_CONFIG / GAZE_EMAIL_CONFIG lines) — @Ada Lovelace

— Chuckles

#### chuckles — 2026-08-02T19:00:34.500Z
@susan

1. Unbound inbox mail (From binds to no candidate): leave untouched for Manage Email / AST-1129, or keep age→Trash retention without a null-candidate shell?
2. Row coverage: provision `gaze_email` for every `candidate`, or only candidates that already have a bindable email address?

— Chuckles

#### chuckles — 2026-08-02T19:00:25.408Z
@susan

1. Unbound inbox mail (From binds to no candidate): leave untouched for Manage Email / AST-1129, or keep age→Trash retention without a null-candidate shell?
2. Row coverage: provision `gaze_email` for every `candidate`, or only candidates that already have a bindable email address?

— Chuckles

---

## Bug: AST-1466 — Retire gaze_email stack

### As-is

AST-1128’s candidate-bound mailbox architecture still runs under the legacy `gaze_email` product identity: `data/admin/agent_task.json` carries a `gaze_email` catalog row (empty prompts; dispatch-only shell), `GAZE_EMAIL_CONFIG` + `TASK_CONFIG["gaze_email"]` drive per-candidate `dispatch_task` rows, `src/core/gaze_email.py` owns the runner (`run_gaze_email`, `_handle_bound`, `run_gaze_email_selected_ids`, `process_gaze_email_messages`), `dispatcher.py` provisions/dispatches via `ensure_gaze_email_dispatch_task` / `provision_gaze_email_dispatch_tasks` / `_gaze_email_due_tasks` and calls `run_gaze_email` from `_dispatch_one`, `api_inbox.py` Land Meteorite POST calls `run_gaze_email_selected_ids`, `api_admin.py` still branches on `GAZE_EMAIL_CONFIG["task_key"]` alongside `is_meteorite_email_mailbox_task_key`, and `SEED_CONFIG["dispatch_task-gaze-email"]` can still insert a null-candidate shell. That duplicates the consolidated `meteorite_email` mailbox fold (Ruth parse already on `meteorite_email`; AST-1282 dispatcher fold). Orphan `dispatch_task` rows whose `task_key` is absent from current `agent_task` may also remain.

### To-be

No live `gaze_email` identity anywhere (agent_task seed, dispatch_task rows, config blocks, module, imports). Candidate-bound mailbox intake — bind-filtered Avail, AUTO due merge, unbound Trash hygiene, `last_email_check` stamping, and Land Meteorite selected-ids — runs exclusively under `meteorite_email` dispatch/config, preserving AST-1128 behavioral contracts on the surviving key. Orphan `dispatch_task` rows whose `task_key` is not in current `agent_task` are removed idempotently.

### Repro

1. On a dev tree at pre-fix tip, confirm `data/admin/agent_task.json` contains a `task_key: "gaze_email"` object and `rg 'gaze_email' src/core/dispatcher.py` hits provision/dispatch branches.
2. Start backend against a DB that has per-candidate `dispatch_task` rows with `task_key='gaze_email'` (normal post–AST-1134 state).
3. Open Admin → Scheduled Actions: rows show `task_key=gaze_email` with live bind-filtered Avail.
4. Run one candidate’s `gaze_email` row (CLICK or AUTO): `src/core/gaze_email.py` executes; `candidate.last_email_check` stamps for that candidate.
5. POST Manage Email Land Meteorite with selected message ids: handler imports `run_gaze_email_selected_ids` from `src.core.gaze_email`.
6. After fix lands, repeat steps 1–5: every step must fail the old identity (no `gaze_email` seed/config/module) and succeed on `meteorite_email` equivalents only.

Fixture anchor: any candidate with a bound inbox message (e.g. somerset + From-bound html_links mail from AST-1144 UAT logs) on a DB carrying `gaze_email` dispatch rows pre-migration.

### Root cause

AST-1128 shipped the candidate-bound redesign under a separate `gaze_email` dispatch identity before later epics (AST-1182 / AST-1212 / AST-1282) consolidated Ruth parse and dispatcher mailbox handling onto `meteorite_email`. Both keys stayed live, leaving duplicate provision, Avail enrichment, runner, and Land Meteorite entrypoints.

### Proposed change

**1. Rehome runner module (`src/core/meteorite_email.py`)**

- Move the full contents of `src/core/gaze_email.py` into new `src/core/meteorite_email.py` (same module boundary — not `gazer.py`; gazer stays create-job strip/extract).
- Rename public entrypoints:
  - `run_gaze_email` → `run_meteorite_email`
  - `run_gaze_email_selected_ids` → `run_meteorite_email_selected_ids`
  - `process_gaze_email_messages` → `process_meteorite_email_messages` (AST-1129 reuse path)
- Replace every `GAZE_EMAIL_CONFIG[...]` read with `METEORITE_EMAIL_MAILBOX_CONFIG[...]`.
- Update Style D `debug_func` strings to `meteorite_email.run` / `meteorite_email.selected_ids`.
- Delete `src/core/gaze_email.py`.

**2. Config consolidation (`src/utils/config.py`)**

- Add `METEORITE_EMAIL_MAILBOX_CONFIG` (sibling to `METEORITE_EMAIL_PARSE_CONFIG`) carrying the former `GAZE_EMAIL_CONFIG` literals keyed to `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` (`"meteorite_email"`): `account_address`, `unbound_retention_days`, `auto_mode`, `min_count`, `batch_size`, `freq_hrs`, `entity_type`, `trigger_state`, `subject_url_schemes`, `debug_func`, `debug_func_selected`, selected-id outcome strings.
- Delete `GAZE_EMAIL_CONFIG` and its asserts.
- Delete `TASK_CONFIG["gaze_email"]` entry; keep existing `TASK_CONFIG["meteorite_email"]` Ruth parse block unchanged.
- Point `INBOX_BIND_CONFIG["inbox_address"]` at `METEORITE_EMAIL_MAILBOX_CONFIG["account_address"]` (stop aliasing deleted block).
- In `dispatch_task_admin_defaults`, remove the `tk == GAZE_EMAIL_CONFIG["task_key"]` branch; `is_meteorite_email_mailbox_task_key(tk)` is the sole mailbox path.
- Delete `SEED_CONFIG["dispatch_task-gaze-email"]` null-shell INSERT tuple.
- Update module inventory docstring lines that name `GAZE_EMAIL_CONFIG`.

**3. Dispatcher (`src/core/dispatcher.py`)**

- Remove `GAZE_EMAIL_CONFIG` import.
- Rename and retarget:
  - `ensure_gaze_email_dispatch_task` → `ensure_meteorite_email_dispatch_task` (uses `METEORITE_EMAIL_MAILBOX_CONFIG` + `METEORITE_EMAIL_PARSE_CONFIG["task_key"]`; same idempotent insert semantics as AST-1134).
  - `provision_gaze_email_dispatch_tasks` → `provision_meteorite_email_dispatch_tasks` (retire any remaining null-candidate `gaze_email` rows during migration window; ensure per-candidate `meteorite_email` rows via coverage join over `database.list_candidates()`).
  - `_gaze_email_due_tasks` → `_meteorite_email_due_tasks` (filter `_is_inbox_mailbox_task_key` rows — after step 2 that helper is equivalent to `is_meteorite_email_mailbox_task_key` + non-empty `candidate_id`).
- Simplify `_is_inbox_mailbox_task_key` to delegate to `is_meteorite_email_mailbox_task_key` only (drop `gaze_email` literal).
- In `_dispatch_one` mailbox branch: `from src.core.meteorite_email import run_meteorite_email`; call `run_meteorite_email`; update log strings (`gaze_email` → `meteorite_email`).
- Startup tick: call `provision_meteorite_email_dispatch_tasks()` instead of gaze provision.

**4. Database migration (`src/data/database.py`)**

- Add idempotent migration function (next sequential migration id) that:
  1. `DELETE FROM dispatch_task WHERE task_key = 'gaze_email'`.
  2. `DELETE FROM dispatch_task WHERE task_key NOT IN (SELECT task_key FROM agent_task)` (orphan sweep — same pattern as existing `gaze_board`/`validate_title` purge at ~7047).
- Update module docstring/comments referencing gaze_email live Avail to `meteorite_email`.
- No Ruth parse or qualify SQL changes.

**5. API layers**

- `src/ui/api/api_inbox.py`: import `run_meteorite_email_selected_ids` from `src.core.meteorite_email`; Land Meteorite handler calls renamed function.
- `src/ui/api/api_admin.py`: remove `GAZE_EMAIL_CONFIG` import and `gaze_tk` local; `_inbox_avail_task_key(tk)` becomes `is_meteorite_email_mailbox_task_key(tk)` only; update warning log text; keep bind-count enrichment path unchanged.

**6. Seed / fixture**

- `data/admin/agent_task.json`: delete the `task_key: "gaze_email"` object (empty dispatch shell at task_seq 2.3); leave `meteorite_email` and legacy `parse_meteorite_email` rows untouched.
- `docs/uat-fixtures/AST-756/expected-agent_task.json`: same removal, byte-identical lockstep with catalog.

**7. Tests / bible (Betty at Code Complete — make-fix may stub imports only)**

- Delete `tests/component/core/test_gaze_email.py`.
- Retarget `tests/component/core/test_dispatcher.py`, `tests/component/ui/api/test_api_inbox.py`, `tests/component/ui/api/test_api_admin.py`, `tests/component/data/database/test_dispatch_tasks.py`, and any `test_config.py` gaze branches to `meteorite_email` / `METEORITE_EMAIL_MAILBOX_CONFIG` names.
- Retire or fold `docs/test-bible/core/gaze_email.md` into meteorite-mailbox bible (Betty).

### Blast radius

- **AST-1129 / Manage Email:** any caller of `process_gaze_email_messages` must switch to `process_meteorite_email_messages` (grep before delete).
- **AST-1282 fold:** `_is_inbox_mailbox_task_key` simplification — ensure legacy `parse_meteorite_email` dispatch rows (if any) still match `is_meteorite_email_mailbox_task_key`.
- **AST-756 seed integrity:** removing `gaze_email` agent_task row triggers fixture lockstep + orphan sweep may delete other stale dispatch rows beyond gaze.
- **Frontend Scheduled Actions tests:** any hardcoded `gaze_email` task_key strings.
- **Existing DBs:** migration deletes live `gaze_email` dispatch rows before `provision_meteorite_email_dispatch_tasks` re-creates under new key — brief window where no mailbox dispatch row exists until startup provision runs.

### What must still hold

- AST-1128 AC 1–9 behavior unchanged on the `meteorite_email` key: per-candidate dispatch rows (coverage join), From→selected-candidate inbox filter on run, real bind-filtered Avail (no carve-out), `last_email_check` stamped every dispatch run (not on selected-ids path), unbound retention→Trash hygiene without null-candidate shell, bound ingest stops at **METEORITE_NEW** (no qualify/GDL daisy-chain), Style D debug contract when `debug=True`, Gmail secrets environ-only, Ruth uses bound candidate API key.
- `meteorite_email` remains the sole mailbox intake agent_task identity; Ruth parse prompts/schema on `TASK_CONFIG["meteorite_email"]` are not redesigned.
- Land Meteorite selected-ids outcomes (`skipped-unbound`, `skipped-not-in-inbox`, `skipped-unmatched`) and per-id Style D logging preserved under renamed config keys.
- `INBOX_BIND_CONFIG` header order and bind rules unchanged; only `inbox_address` source moves to mailbox config block.

---

## Resolution: AST-1467 (2026-08-24)

Radia FIX-NOW on Review Posted (bible + frontend gap — Betty `[qa-handoff]`):

1. **`docs/test-bible/core/meteorite_email.md`** — all `run_component_tests` blocks retargeted from deleted `test_gaze_email.py` to `test_meteorite_email.py` (+ matching node ids). Tip `0fa5bc81` / merge-tests `31bffc80`.
2. **`test_AdminScheduledActions_AST1106.test.tsx`** — retired (gaze Avail-gt0 carve-out obsolete post–AST-1134/1466); `docs/test-bible/frontend/pages.md` § AST-1106 + `repo_admin_json.md` AST-1219 Vitest pointer retargeted.

Inventory gate `TestAst1467GazeEmailRetired` green (6 passed) on tip. No product code change this resolve pass.

---

_Implementation detail may live in git history on `origin/dev`._
