# AST-952 — Candidate Profile Preamble to Intake

<!-- linear-archive: AST-952 archived 2026-08-07 -->

## Linear archive (AST-952)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-953

### Description

## Purpose

Give intake a durable **preamble** before Topic Menu work: the candidate supplies contact identity and source documents through a short mechanical front door; those inputs land in a clean **contact / context / artifacts** library (plus high-frequency name/pronoun columns) so Estelle and Topic Menu ([AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation)) always know where to read from. **This epic is a technical blocker for Topic Menu** — populated context (and contact) is required input to Topic Menu generation. Estelle’s “Anything here you would change?” confirm pass is **not** in this epic — it is step 1 of Topic Menu on [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation).

## Functional scope

* **Candidate data homes.** Move from two blobs to **three** JSON blobs on the candidate — **contact**, **context**, **artifacts** — plus **first name, last name, full name, and pronouns as individual candidate-table text columns** (not nested in a blob) because they are high-frequency tokens (`FIRST_NAME` / `LAST_NAME` / `FULL_NAME` / pronouns).
  * **Contact blob** — emails (Astral-message vs resume if different), phone, LinkedIn (URL or username → URL), GitHub username (URL or username → URL), websites / profile URL list, and related contact handles — not mixed with prose context.
  * **Context blob** — natural prose and raw sources, passable whole-cloth into AI prompts: bio, hopes, interests, concerns, strengths, priorities, dealbreakers, backstory, writing_preferences, raw_resume, raw_profile, raw_sample (and remap today’s equivalent keys). **New** hopes / interests / concerns are Topic Menu inputs.
  * **Artifacts blob** — structured processable JSON (structured resume, rubrics, etc.); candidate-mutable but UI-shaped for runtime company/job analysis — not freeform preamble prose.
* **Reusable preamble validation loop.** One low-cost validation prompt: “Does this response look like a valid answer to this question?” Returns **Valid**, **Try Again**, or **Escalate**. Implemented as a **new agent_task record using Ruth (Little Brain) only** — no new agent personas, no new agent patterns.
* **PREAMBLE_CONFIG (config).** Config-driven preamble script: step sequence, which blob/field each step writes, **Intro** text shown every time a candidate starts a new intake, and Archie-provided **1st Try** / **2nd Try** prompt text (2nd Try used on Try Again). Intro/step copy appears in the same presentation style as Estelle intake responses so the handoff feels seamless.
* **Mechanical front door (UI).** Non-chat prompts in order driven by PREAMBLE_CONFIG (resume → LinkedIn → sample cover letter at minimum). Writes the correct library fields; calls the Ruth validation task; does not re-implement validation or own config.
* **Handoff readiness for Topic Menu.** When mechanical sources are Valid and stored, contact + context are ready for [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). Estelle confirmable summary (“Anything here you would change?”) stays on [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation).
* **Surfaces stay coherent.** Profile / admin edit paths read/write the same columns and blobs — no shadow copies.
* **Debug traceability (backend).** On touched backend `debug=True` paths for validation or library writes: per-step found/recorded lines (universal `index N/M`, primary id, outcome; detail under `|`; long blobs truncated per Code Rules / AST-538). UI has no debug-logging requirement.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — PREAMBLE_CONFIG lives as an explicit product config block (source of truth for sequence, fields, Intro, try-copy).
* **New patterns proposed**
  * Three-blob candidate library + high-frequency name/pronoun columns (contact / context / artifacts split) — introduced by child #1; Topic Menu and Profile read the same homes.
  * Ruth Valid / Try Again / Escalate `agent_task` for mechanical preamble answers — introduced by child #2; reusable for other low-context “is this a valid answer?” checks if Archie later wants it cataloged.
  * PREAMBLE_CONFIG-driven intake script (Intro + ordered mechanical steps) — introduced by child #3; UI (#4) only executes it.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — PREAMBLE_CONFIG and field vocabulary are config, not UI hardcodes.
  * `astral.layers.ui-config-driven-business-logic` — mechanical UI reads config; does not own the script.
  * `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` — library/validation/UI stay in the correct layers.
  * `astral.agent.do-task-delegation` — validation is an agent_task on Ruth, not a new persona.
  * `astral.standards.debug-contract-gated` — backend `debug=True` found/recorded contract on touched paths.
  * `astral.docs.features-single-file-per-ticket` — one plan doc per child when planning.

## Boundaries

* Does **not** build Topic Menu generation, topic satisfaction, REQUIRED/ALL_TOPICS_READY automation, or Estelle’s confirmable summary pass — [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation).
* Does **not** change the candidate state machine vocabulary/transitions from [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine).
* Does **not** invent new AI agents or agent-framework patterns for validation — **Ruth + one new agent_task only**.
* Does **not** craft structured resume/rubric artifacts beyond the library boundary; hopes/interests/concerns stay **context** for Topic Menu.
* Does **not** replace the full Estelle topic interview after the preamble.
* Does **not** break existing Profile/Admin identity/pronoun editing — migrate into columns + contact blob without divergent copies.
* Code Rules: PREAMBLE_CONFIG and field vocabulary live in config as source of truth (§2.1); backend debug contract when `debug=` surfaces are touched (§1.5.1).

## Acceptance criteria

1. Candidate has three blobs (contact / context / artifacts) plus first, last, full, and pronouns as table columns; contact identity/comms are not stored as freeform context prose; raw resume / LinkedIn / sample live in context; structured resume/rubrics remain artifacts.
2. Ruth agent_task validation returns Valid / Try Again / Escalate; Try Again does not advance; Escalate ≠ Valid; no new agent persona shipped.
3. PREAMBLE_CONFIG defines sequence, target fields, Intro, and 1st/2nd Try copy; Intro appears at new-intake start in Estelle-consistent presentation.
4. Candidate can complete the mechanical preamble UI driven by PREAMBLE_CONFIG; Valid answers persist to the correct columns/blobs; UI calls Ruth validation rather than inlining a checker.
5. Hopes, interests, and concerns exist as context fields for Topic Menu; Estelle confirm UI is **not** required in this epic ([AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation)).
6. After Valid mechanical sources are stored, contact + context are complete enough to feed [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation).
7. Profile/Admin identity and pronoun editing still work against the new columns/contact home — no divergent copies.
8. Touched backend `debug=True` validation/write paths emit per-step found/recorded debug lines per the contract above.

## Dependencies and blockers

* **Blocks:** [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation) — needs this library + Valid preamble packet; [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation) owns Estelle confirm-as-step-1.
* Related (soft): [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine) — Done.
* Soft adjacency: intake chat (AST-539 family), pronoun selection (AST-573 family) — must not regress.
* none blocking start of this epic.

## Open questions

none.

## Proposed child tickets

#### 1!!: **Contact / context / artifacts library + name columns - Ada**

Persist three candidate blobs (**contact**, **context**, **artifacts**) and **first / last / full / pronouns** as individual candidate-table text columns (not in a blob). Contact blob holds emails, phone, LinkedIn/GitHub URL-or-username, websites; context holds prose + raw_resume / raw_profile / raw_sample (and remaps); artifacts stay structured resume/rubrics. Readable by Profile/Admin and intake. Does **not** own validation (#2), PREAMBLE_CONFIG (#3), or mechanical UI (#4). Does **not** own Estelle confirm (AST-953).
**Citations:** new three-blob + name/pronoun columns pattern (proposed); `astral.layers.import-direction`; `astral.layers.core-vs-external-bright-line`; `astral.standards.debug-contract-gated`.

#### 2!: **Preamble Valid / Try Again / Escalate via Ruth - Hedy**

New **agent_task** only, using **Ruth (Little Brain)**: Valid / Try Again / Escalate. After #1. Does **not** own the data library (#1), PREAMBLE_CONFIG (#3), or intake UI (#4). No new agents or agent patterns.
**Citations:** new Ruth Valid/Try Again/Escalate agent_task pattern (proposed); `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`.

#### 3!: **PREAMBLE_CONFIG preamble script - Ada**

Add **PREAMBLE_CONFIG** in product config: step sequence, target blob/field names, Archie-provided **1st Try** / **2nd Try** prompt text, and **Intro** text for every new intake. After #1. Does **not** own library persistence (#1), Ruth validation (#2), or the intake UI (#4).
**Citations:** `pattern.config.config-block`; new PREAMBLE_CONFIG intake-script pattern (proposed); `astral.config.config-source-of-truth`; `astral.layers.ui-config-driven-business-logic`.

#### 4: **Mechanical intake front door UI - Katherine**

Resume to LinkedIn to sample cover letter mechanical UI driven by PREAMBLE_CONFIG; calls Ruth validation. After #1, #2, and #3. Does **not** own library (#1), validation (#2), config (#3), or Topic Menu (AST-953).
**Citations:** `astral.layers.ui-config-driven-business-logic`; `astral.config.config-source-of-truth` (UI consumes config, does not hardcode the script).

**Monolith check:** Functional scope has 7 capabilities; 4 proposed children (already materialised as AST-1014…AST-1017).

**New patterns:** (1) Three-blob + name/pronoun columns — #1. (2) Ruth Valid/Try Again/Escalate agent_task — #2. (3) PREAMBLE_CONFIG intake script — #3.

## Git (authoritative — ignore Linear gitBranchName)

| Ticket | origin |
| -- | -- |
| AST-952 (parent) | ftr/AST-952-candidate-profile-preamble-to-intake |
| AST-1014 | sub/AST-952/AST-1014-contact-context-artifacts-library |
| AST-1015 | sub/AST-952/AST-1015-preamble-validation-ruth |
| AST-1016 | sub/AST-952/AST-1016-preamble-config |
| AST-1017 | sub/AST-952/AST-1017-mechanical-intake-ui |
| AST-1083 | sub/AST-952/AST-1083-uat-store-response-block-nameerror |

**Epic worktree:** astral-AST-952/ — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/09ce8830-4442-48ac-8a7b-d24d604be81a/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/dfb49f98-08ec-4552-a640-3c0c319edde8/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/76c6db7e-d67f-401a-a1a0-6f5096f9b9b9/store.db` |
| Radia | review | `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/643a4613-9f42-428e-bd24-61eebbf8c9a5/store.db` |

---

## Original brief

Name, contact data (email, phone, gituser, wevs), pronouns, profile urls list (personal website, github repo, portfolios, etc.), original resume text, linkedin profile content, sample cover letter, Interests (if any), Hopes (if any), Concerns (if any), and bio.

Where i'm getting a little blurry is the distinction between what the candidate actually enters as her information, and what Estelle can infer and propose.  I think the intake is going to start with the basics.  "Let's start with uploading your existing/latest resume", then "now let's get your linkedin profile", then "a sample cover letter from a past application to give us a sense of your writing style", as non-AI prompts but mechanical intake questions. Then send all that content up to Estelle, who can then parse all the metadata and a recipe for intake by topics. (see "Topic Menu" issue)

This would be experientially identical to the current intake flow, but the user responses would be basically populating the preamble fields.  We could send quick check calls to Estelle to say "Does this response look like resume text?", etc. without a bunch of context, to let AI validate the user's entries.

### Comments

#### chuckles — 2026-07-31T04:03:28.524Z
@susan Yes — in `src/utils/config.py`, block **`PREAMBLE_CONFIG`**. The ordered array is **`PREAMBLE_CONFIG["steps"]`** (plus **`intro`** and **`validation_task_key`**). Each step has `id`, `order`, `prompt_1st_try` / `prompt_2nd_try`, `target` `{blob, field}`, and `validation_question`. Today that’s resume → LinkedIn → sample cover letter into `context.raw_*`.

Your job-search feeling question would be another entry in that **`steps`** list (new `id` + target field, usually under **context**). There is no built-in **"skip"** verb yet — that would be product behavior on top of a step (optional step / accept skip as Valid), not a separate config key today.

Copy is still `[PLACEHOLDER — Archie]` on the three shipped steps — swap those strings (and add steps) in **`PREAMBLE_CONFIG`** for UAT wording.

— Chuckles

#### chuckles — 2026-07-31T04:03:12.399Z
@susan Yes — preamble script lives in **`PREAMBLE_CONFIG`** in `src/utils/config.py`.

- **`intro`** — shown at new-intake start
- **`steps`** — the array of preamble elements (today: `raw_resume`, `raw_profile`, `raw_sample`)
- Each step has: `id`, `order`, `prompt_1st_try` / `prompt_2nd_try`, `target` (`blob` + `field`), `validation_question`
- Ruth validates via `validation_task_key` → `preamble_validate_response`

Mechanical UI (AST-1017) just executes that array — it does not hardcode the questions.

**To add your job-search feeling prompt:** append another object to `steps` (and add the destination field under context in `CANDIDATE_LIBRARY_CONFIG` if it is not already a context key). Today step `target.blob` must be `context`, and `id` must match `target.field`. Copy is still `[PLACEHOLDER — Archie]` until you paste final wording.

**Skip:** there is no special “say skip” outcome in preamble validation yet (Valid / Try Again / Escalate only). If you want skip → store empty / advance without Valid, say so and I’ll file a UAT bug for that behavior + the new step.

Assigning you back for the browser pass.

— Chuckles

#### susan — 2026-07-31T04:01:21.506Z
@chuckles Where can I specify what else is asked for in the preamble?  For example, we may want to ask "How are you feeling about your job search at this point?  What's been your experience so far?  Just say "skip" if you don't want to answer."  I want an array of preamble elements.  Are they in config.py?

#### chuckles — 2026-07-30T18:55:45.758Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1083** | NameError in _store_response_block RESPONSE debug log |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1083** — _NameError in _store_response_block RESPONSE debug log_
- **Issue reported:** While UAT-testing Candidate Intake (candidate `mcevoy`), after Estelle `intake_initiate_candidate` returned a successful assistant message, backend logged:
- **Should now:** `_store_response_block` persists the RESPONSE block and (when `debug=True`) emits the found/recorded-style `agent_data_write` detail line without raising. Intake initiate continues without a stacktrace in the server log.
- **Quick check (this fix only):**
  1. Open Candidate Intake for candidate `mcevoy` on local/staging with debug logging on.
  2. Start a new intake so Estelle runs `intake_initiate_candidate` (after preamble / into chat as applicable).
  3. Observe server log: LLM success, then `_store_response_block failed` NameError on `result`.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-30T16:47:36.332Z
Got a stack trace while testing our intake:

```
127.0.0.1 - - [30/Jul/2026 09:46:22] "GET /api/candidates/mcevoy/intake/sessions/active HTTP/1.1" 200 -
LLM deepseek task=intake_initiate_candidate 17.3s stop=end_turn tokens in=3256 out=699
send_to_deepseek index 1/1 intake_initiate_candidate -> success
 | provider=deepseek model=deepseek-v4-pro task=intake_initiate_candidate duration=17.3s stop_reason=end_turn
 | vendor=deepseek-v4-pro tokens fresh=3256 cache_read=0 cache_write=0 output=699
 | response_preview:
 | {
 |   "ready_to_build": false,
 |   "assistant_message": "Hi Brian, I'm Estelle. I'm part of the Astral Career Match team, and I'll be helping build your profile so we can match you with roles that actually fit.\n\nFrom what I've read, you're the engineer they drop into the messy real-world gaps — designing the panel, wiring the system, writing the PLC code, and then showing up on site to make sure it all actually runs. There's a throughline of making hardware behave, whether that's in a wastewater plant, a Tesla factory, or a particle accelerator. I'm excited to dig into the real stories behind the bullet points.\n\nSound okay if we start by walking through your work history, most recent first?"
 | }
 | agent_data_write block_type=SYSTEM outcome=ref_existing agent_data_id=intake-intake_initiate_candidate-d1cc801b-f3db-430d-9535-dc91c593e8e0-system-7895fbb453b82a85 ref_agent_data_id='analysis_upshot-2010da6c-0c18-4b41-84e9-e482c3829596-system-0bd91b5b85af494b'
 | agent_data_write block_type=NO_CACHE outcome=new_content agent_data_id=intake-intake_initiate_candidate-d1cc801b-f3db-430d-9535-dc91c593e8e0-no_cache-ba8b5cf99ce39c10 ref_agent_data_id=None
 | agent_data_write block_type=TASK outcome=ref_existing agent_data_id=intake-intake_initiate_candidate-d1cc801b-f3db-430d-9535-dc91c593e8e0-task-09a309a6d3b8b5e7 ref_agent_data_id='intake-intake_initiate_candidate-77a4947f-bf99-4a3b-b62f-4f02cc61590c-task-5147327097249f23'
 | raw_response task_key=intake_initiate_candidate lines=4 chars=702
 | {
 |   "ready_to_build": false,
 |   "assistant_message": "Hi Brian, I'm Estelle. I'm part of the Astral Career Match team, and I'll be helping build your profile so we can match you with roles that actually fit.\n\nFrom what I've read, you're the engineer they drop into the messy real-world gaps — designing the panel, wiring the system, writing the PLC code, and then showing up on site to make sure it all actually runs. There's a throughline of making hardware behave, whether that's in a wastewater plant, a Tesla factory, or a particle accelerator. I'm excited to dig into the real stories behind the bullet points.\n\nSound okay if we start by walking through your work history, most recent first?"
 | }
[ ~ ] _store_response_block failed
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 2593, in do_task
    resp_id = _store_response_block(entity_type, task_key, batch_id, store_content, index=index, debug=debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 1549, in _store_response_block
    f"agent_data_write block_type=RESPONSE outcome={result.get('outcome')} "
                                                    ^^^^^^
NameError: name 'result' is not defined
do_task(intake_initiate_candidate) completed successfully batch_id=intake-intake_initiate_candidate-d1cc801b-f3db-430d-9535-dc91c593e8e0 index=mcevoy
do_task index 1/1 mcevoy -> completed
 | task_key=intake_initiate_candidate batch_id=intake-intake_initiate_candidate-d1cc801b-f3db-430d-9535-dc91c593e8e0 success=True
127.0.0.1 - - [30/Jul/2026 09:46:25] "GET /api/candidates/mcevoy/intake/sessions/active HTTP/1.1" 200 -
127.0.0.1 - - [30/Jul/2026 09:46:29] "GET /api/deploy_status HTTP/1.1" 200 -
127.0.0.1 - - [30/Jul/2026 09:46:33] "GET /api/nav_config?candidate_id=mcevoy HTTP/1.1" 200 -
```

#### chuckles — 2026-07-30T16:37:03.435Z
@susan Yes — for UT, start a **new intake** on the web **Candidate Intake** screen for a candidate.

What happens: with no active intake session (or after you start new), the page enters the **preamble** phase (`IntakePreamblePanel`) driven by `PREAMBLE_CONFIG`, then hands off to Estelle chat. Validation goes through `/api/candidates/<id>/preamble/validate` (Ruth Valid / Try Again / Escalate). That is the same intake function path the Slack bot will eventually drive; for this epic’s UAT the browser Candidate Intake UI is the wired front door.

If an intake session is already active, the UI skips preamble and goes straight to chat — archive/start new if you need to re-run the mechanical steps.

No UAT bug children from this comment — assigning you back for the browser pass.

— Chuckles

#### susan — 2026-07-30T16:34:44.037Z
@chuckles Please confirm I can test this by starting a new intake for a candidate?  The intake screen on our UI will be used by the the slack bot in production, but for UT I need it wired to the intake function.

#### chuckles — 2026-07-30T16:07:41.850Z
@susan AST-1017 is merged onto `ftr` now (Katherine republished + merge-child ok).

[refresh-ftr] blocked: merge origin/dev into ftr — conflict files:
- docs/test-bible/utils/config.md; docs/uat-fixtures/AST-756/expected-agent_task.json — @Betty White
- src/core/candidate.py; src/ui/api/api_admin.py — @Ada Lovelace
- data/admin/agent_task.json; src/utils/config.py — @Hedy Lamarr

Spawning Betty/Ada/Hedy (+ Katherine per your ping) to resolve, then retry refresh-ftr (attempt 1/3).

— Chuckles

#### susan — 2026-07-30T05:09:53.641Z
@chuckles you need to call Katherine to fix the issue with the merge. She won't wake up on her own.

#### chuckles — 2026-07-30T03:43:10.630Z
[merge-child] blocked: cannot roll up to ftr before prep-uat.

- AST-1014: validate-sub-log missing plan/code/merge-tests/test/docs/resolve — @Ada Lovelace refresh/republish sub from origin/ftr/AST-952-candidate-profile-preamble-to-intake
- AST-1015: git pull merges on sub — @Hedy Lamarr merge origin/ftr (no pull) and republish
- AST-1016: already on ftr
- AST-1017: git pull merges on sub — @Katherine Johnson merge origin/ftr (no pull) and republish

Chuckles stays assignee until merge-child + refresh-ftr are clean.
— Chuckles

#### chuckles — 2026-07-29T23:10:30.546Z
@susan Yes. Updated Description to current formatting expectations: bang-tier child headers (`#### 1!!:` …), per-child Citations, and **Architectural definition**. Four-child scope unchanged. — Chuckles

#### susan — 2026-07-29T23:05:05.032Z
@chuckles Do we need any revisions to teh description with our latest formatting expectations?

#### chuckles — 2026-07-28T18:55:33.850Z
[publish-ref-stale] AST-1014 STALE(dev+1092) on_ftr — @Ada Lovelace please refresh `sub/AST-952/AST-1014-contact-context-artifacts-library`: `git fetch origin && git checkout` that sub, `git merge origin/dev`, `git merge origin/ftr/AST-952-candidate-profile-preamble-to-intake`, resolve, push origin/sub. Holding AST-1016 build until refresh lands.

— Chuckles

#### susan — 2026-07-28T16:57:31.969Z
@chuckles Add a fourth child ticket to handle the update to config.py.

#### susan — 2026-07-28T16:46:27.031Z
@chuckles this should be three child tickets, don't mush together the UI and the validation loop.

#### susan — 2026-07-28T16:42:04.666Z
See my comments to the child tickets proposed.

#### chuckles — 2026-07-28T16:21:41.102Z
[check-linear] Discussion — Proposed child tickets → header format (@susan)

#### susan — 2026-07-28T16:19:45.918Z
@chuckles Please revise the child issues in the description text with the new formatting rules (headers, not tables)

#### chuckles — 2026-07-28T04:30:04.380Z
[check-linear] Discussion — definition updated from answers; waiting Todo (@susan)

#### susan — 2026-07-28T04:12:15.476Z
1. Nah, I've decided it's not really worth making the distinction.  We have a reasonably bright line between context and artifacts for the candidate.  The AI can parse the context from provided input from the user, it's still context.  Hopes/etc should actually be AI summarized, like "So, you would say you are hoping to blah blah blah" and the user would confirm during intake, and the blah blah blah string would get saved as the hopes.
2. I think the Github URL and the LinkedIn URL are the same as the users for GH and LI, so we can have them provide the URL or the username and we can extrapolate the url, because we fancy.
3. New fields, for sure.  They will inform the Topic Menu, not the downstream artifacts.
4. Bio Estelle proposed.  I hate writing bios for myself.
5. This is a technical blocker for the topic menu prompt because this content is the input to the topic menu generation prompt (see #3)

#### chuckles — 2026-07-28T03:44:37.027Z
@susan

1. Entered vs proposed — confirm the split in the Description (mechanical sources + typed identity/contact = entered; Estelle proposes parsed contact/name, Interests/Hopes/Concerns, bio for accept/edit). Or should Interests/Hopes/Concerns always be candidate-typed only?
2. Contact “gituser, wevs” — what do these mean vs existing GitHub URL / LinkedIn URL?
3. Interests / Hopes / Concerns vs strengths / priorities / deal breakers / backstory — new fields, renames, or early seeds that map later?
4. Bio — Estelle-proposed-then-confirmed, always candidate-written, or either?
5. Sequencing with AST-953 — Todo/dispatch this epic before Topic Menu is defined, or approve both definitions together?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
