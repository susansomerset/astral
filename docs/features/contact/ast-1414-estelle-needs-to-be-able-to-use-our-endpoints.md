# AST-1414 — Estelle needs to be able to use our endpoints.

<!-- linear-archive: AST-1414 archived 2026-10-02 -->

## Linear archive (AST-1414)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Estelle already talks on Slack. People paste job-description links (and sometimes page text), and she currently cannot look at a page, land it as a meteorite, or read jobs we have already recommended. This epic gives the **application** those abilities: Contact reads Estelle's replies for `~~/<contact_task_key> [parameters]~~`, runs thin config-listed wrappers around existing core (gazer scrape, meteorite create, job/company/candidate reads), and feeds results back so she can inspect a posting (or confirm it is blocked), file it for analysis, and talk about recommended jobs. The Slack bot stays stupid — it never calls ACLs, HTTP, or other services.

## Functional scope

**Application-side contact tasks.** A new config block lists contact tasks. Each task is a thin wrapper around an existing core function. Contact reads Estelle's response, finds instructions of the form `~~/<contact_task_key> [parameters]~~`, strips that markup from the Slack-visible reply, and runs only keys listed in that block. Estelle does not call skills, ACLs, or endpoints.

**Gazer scrape (contact task).** Estelle can emit a scrape instruction for a conversation URL. Contact fetches through gazer and obtains visible text, links on the page, and whether the page looks blocked / ok / closed / missing (existing classifier). This does not create a job. Contact then gives Estelle the payload on a follow-up turn in the same inbound event so she can describe the page or confirm a block — she still only emits text and markup.

**Create a meteorite from Slack (contact task** `create_contact_meteorite`**).** For the Slack-resolved candidate, a link instruction scrapes first then lands a meteorite (visible text + link); pasted page text lands as given with no fetch. The job enters the existing meteorite landing state. That landing queues meteorite analysis through existing dispatch. Estelle does not wait for analysis in the Slack turn.

**Read job / company / candidate (contact tasks).** Contact wrappers: `get_job_by_pattern` (resolve a job for the Slack-resolved candidate from a text pattern — title, company, link, or id — and return it fully hydrated, including agent responses and dates); `get_job_data`; `get_company_data`; `get_candidate_data`. These wrap extant getters; they do not run a new analysis. Estelle uses them so she can talk about recommended jobs (and other jobs that pattern-match for that candidate).

When Contact debug is on, each contact-task run logs what was found and what was recorded per item — Style D index headers with universal `index N/M`, identifier, and outcome; working detail prefixed `|`; payloads longer than 50 lines truncated to first 15 / omitted count / last 15. Backend only.

## Component scope

* `src/utils/config.py` — **modified** — new `CONTACT_TASK_CONFIG` block (allowlisted task keys + handler metadata; distinct from `CONTACT_CONFIG` skills ACL and `TASK_CONFIG`).
* `src/core/contact.py` — **modified** — parse `~~/<contact_task_key> [parameters]~~` from Estelle replies; strip markup from Slack-visible text; dispatch to config-listed handlers; optional same-event follow-up Estelle turn with task payloads in live content.
* `data/admin/agent_task.json` — **modified** — `contact_estelle_turn` prompt teaches markup format and lists available contact tasks (not ACL `skill_calls`).
* `src/core/gazer.py` — **modified** — contact-task scrape helper (visible text + links + blocked/ok/closed/missing via existing classifier).
* `src/core/meteorite.py` — **modified** — `create_contact_meteorite` wrapper (link path delegates scrape to gazer helper; page-text path lands as given).
* `src/core/tracker.py` — **modified** — `get_job_by_pattern` plus contact-task read wrappers that delegate to existing job/company/candidate getters and hydration.

## Technical scope

* `src/utils/config.py` — new config block registering all contact-task keys (`gazer_scrape`, `create_contact_meteorite`, `get_job_by_pattern`, `get_job_data`, `get_company_data`, `get_candidate_data`) with handler references and parameter shape metadata; import-time asserts; keys must not collide with `TASK_CONFIG` or `CONTACT_CONFIG["skills"]`.
* `src/core/contact.py` — new markup parser; dispatch router that resolves only allowlisted keys for the Slack-resolved candidate; strips markup before `contact_post_message`; runs configured handlers and collects return payloads; optional second `do_task(contact_estelle_turn)` in the same inbound event with payloads in live content; Style D when `debug=True`.
* `data/admin/agent_task.json` — extend `contact_estelle_turn` system/cache prompts: markup syntax, available task keys, parameter expectations; reinforce that user-visible reply stays conversational and payloads are not pasted raw to Slack.
* `src/core/gazer.py` — new async helper wrapping extant Playwright visible-text fetch + link extraction + `_classify_jd` outcome for a single URL (contact-task surface, not batch gazer).
* `src/core/meteorite.py` — new `create_contact_meteorite` entrypoint: candidate-scoped; link mode calls gazer scrape helper then `create_meteorite_job`; text mode calls `create_meteorite_job` directly; returns create result dict for contact dispatch.
* `src/core/tracker.py` — new `get_job_by_pattern` (candidate-scoped pattern match against title/company/link/id); new contact-task read helpers that call existing `get_job_data`, `roster.get_company_data`, `candidate.get_candidate`, and `agent.get_entity_agent_story` for hydration; refuse cross-candidate or unmatched patterns.

## Architectural definition

* **Patterns to reuse**
  * [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>) — `CONTACT_TASK_CONFIG` allowlist + handler metadata; distinct from skills ACL and dispatch tasks.
  * [`pattern.layers.import-discipline`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>) — Contact orchestrates; gazer Playwright I/O stays external; core-to-core calls follow layer rules.
  * [`pattern.state.entity-state-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/state/pattern.state.entity-state-transitions.md>) — `create_contact_meteorite` uses existing meteorite landing state; no new job states.
* **New patterns proposed**
  * `pattern.core.contact-task-markup` — Estelle remains a text bot. Contact parses `~~/<contact_task_key> [parameters]~~`, executes only config-listed thin wrappers, strips markup from the user-visible Slack message, and may run one follow-up Estelle turn in the same event with task payloads in live content. Archie approval before implementation depends on it.
* **Applicable statutes**
  * [`astral.layers.core-vs-external-bright-line`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.core-vs-external-bright-line.md>) / [`astral.layers.import-direction`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>) — Contact orchestrates; Playwright I/O stays external.
  * [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) / [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — contact-task keys live only in the new config block.
  * [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>) / [`astral.standards.logging-via-utils`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) / [`astral.standards.no-cross-contamination`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-cross-contamination.md>) / [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>) / [`astral.standards.public-then-helpers`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.public-then-helpers.md>) / [`astral.standards.data-raises-caller-logs`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>)
  * [`astral.standards.database-header-inventory`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>) — no new tables.
  * [`astral.state.core-decides-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.core-decides-transitions.md>) / [`astral.state.job-prior-states-enforced`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.job-prior-states-enforced.md>) — existing meteorite create carve-out; no new transitions.
  * [`astral.agent.do-task-delegation`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/agent/astral.agent.do-task-delegation.md>) — Estelle still speaks via the existing Contact turn task.
  * [`astral.patterns.require-auth-on-protected-endpoints`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/patterns/astral.patterns.require-auth-on-protected-endpoints.md>) — no public scrape/create HTTP for the bot.

## Acceptance criteria

1. Estelle can emit `~~/<contact_task_key> [parameters]~~` in a turn. Contact executes only keys listed in the contact-task config. Unknown keys are not executed. Markup does not appear in the Slack-visible reply.
2. Given a job URL, Estelle can emit a scrape contact task and, in that same inbound Slack event (follow-up turn), tell the user whether the page looks blocked or ok (or closed/missing) and a gist of the visible content. No job is created.
3. Given a job URL, Estelle can emit `create_contact_meteorite` for the Slack-resolved candidate. The job exists in the meteorite landing state with stored visible text and the link. Meteorite analysis is queued via existing dispatch.
4. Given pasted page text and no usable link, `create_contact_meteorite` lands a meteorite from that text (no fetch) for the same candidate.
5. Estelle can emit `get_job_by_pattern` (and/or `get_job_data`) so Contact returns a fully hydrated job for that candidate (agent responses and dates included). She can then talk about a recommended job in Slack. A pattern that does not resolve to that candidate's job is refused.
6. `get_company_data` and `get_candidate_data` return extant stored data via wrappers; they do not invent new persistence.
7. User-visible Slack replies stay conversational (envelope reply). Task payloads are not pasted raw into Slack.
8. With Contact debug on, each contact-task run emits Style D found/recorded lines (`index N/M`, identifier, outcome, `|` detail; long payloads truncated per contract). Debug off is quiet on those surfaces.

## Open questions

none

## Proposed child tickets

#### 1!!: **Contact-task config, markup parse, and dispatch - Ada**

New `CONTACT_TASK_CONFIG` block (all task keys pre-registered with handler refs), markup parser, dispatch router, same-event follow-up Estelle turn, and `contact_estelle_turn` prompt markup contract. Does not implement gazer scrape, meteorite create, or read handlers — those are #2–#4. Does not extend Contact skills ACL.
**Citations: **`pattern.core.contact-task-markup` (proposed), [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>), [`astral.agent.do-task-delegation`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/agent/astral.agent.do-task-delegation.md>), [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
**Scope: **`src/utils/config.py` (modified — `CONTACT_TASK_CONFIG` block with all task keys + handler metadata); `src/core/contact.py` (modified — markup parser, dispatch router, follow-up turn, markup strip before Slack post); `data/admin/agent_task.json` (modified — `contact_estelle_turn` markup prompts). Technical: config block + asserts; contact markup parse/dispatch/follow-up + Style D; agent_task prompt contract.
**Estimate: 5**

#### 2!: **Gazer scrape contact task - Hedy**

Implement the gazer contact-task scrape handler registered in #1: visible text + links + blocked/ok/closed/missing. Same-event follow-up via #1 dispatch. Does not create a job. After #1. Blocks #3 (link-create reuses this scrape).
**Citations: **[`pattern.layers.import-discipline`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>), [`astral.layers.core-vs-external-bright-line`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.core-vs-external-bright-line.md>), [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>), [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
**Scope: **`src/core/gazer.py` (modified — contact-task scrape helper). Technical: async helper wrapping extant Playwright visible-text fetch + link extraction + `_classify_jd` outcome for a single URL.
**Estimate: 3**

#### 3: **create_contact_meteorite - Katherine**

Implement the `create_contact_meteorite` handler registered in #1. Link path uses #2 scrape helper; page-text path lands as given. Existing meteorite landing state; existing analysis dispatch. After #2.
**Citations: **[`pattern.state.entity-state-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/state/pattern.state.entity-state-transitions.md>), [`astral.state.job-prior-states-enforced`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.job-prior-states-enforced.md>), [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>), [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
**Scope: **`src/core/meteorite.py` (modified — `create_contact_meteorite` wrapper). Technical: candidate-scoped entrypoint; link mode calls gazer scrape helper then `create_meteorite_job`; text mode calls `create_meteorite_job` directly; returns create result dict for contact dispatch.
**Estimate: 3**

#### 4: **Job / company / candidate contact-task reads - Ada**

Implement read handlers registered in #1: `get_job_by_pattern`, `get_job_data`, `get_company_data`, `get_candidate_data`. Wrap extant getters; add pattern resolve + hydration where missing. After #1; parallel with #2/#3. Does not create jobs and does not run a new analysis.
**Citations: **[`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>), [`pattern.layers.import-discipline`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>), [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>), [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>)
**Scope: **`src/core/tracker.py` (modified — `get_job_by_pattern` + contact-task read wrappers). Technical: candidate-scoped pattern match; read helpers delegating to existing `get_job_data`, `roster.get_company_data`, `candidate.get_candidate`, and `agent.get_entity_agent_story`; refuse cross-candidate or unmatched patterns.
**Estimate: 3**

New pattern: child #1 introduces `pattern.core.contact-task-markup`; #2–#4 depend on it.

Monolith check: Functional scope has 4 capabilities; 4 children — markup/dispatch, scrape, create, reads.

Scope partition check: six Component scope files partitioned — #1 owns config/contact/agent_task; #2 gazer; #3 meteorite; #4 tracker.

---

## Original brief

Estelle (the slack bot) gets links to pages of job descriptions and she needs them scraped.

I want her to be able to request scraped visible text and links via our gazer component, so she can see things like that (or confirm that it is not blocked).

We need to be able to create jobs as meteorites that have been sent via slack, either as link or page text, and trigger the meteorite analysis for that job.

I also want her to be able to get job content for jobs that have been recommended for the candidate, so that she can talk intelligently about them.

This is important.  We are NOT opening ACL's for a slack bot to call.  Instead, we need the APPLICATION side to read Estelle's responses and look for instructions like ~~/<contact_task_key> [parameters]~~

Contact task would be a new config element in [config.py](<http://config.py>) that would be a thin wrapper around extant functions in other core components, so that [contact.py](<http://contact.py>) can call tracker to say "get_job_by_pattern" and get the fully hydrated job with agent responses and dates and "get_job_data" and "get_company_data", "get_candidate_data" as well as "create_contact_meteorite"

This way, the slack bot remains stupid, there's no concern about network security, and we are able to control the flow of data cleanly.

### Comments

#### chuckles — 2026-08-27T04:16:12.343Z
[merge-child] blocked: validate-sub-log missing plan(AST-1518) in sub-not-ftr range — need docs(AST-1518): plan — (or plan()) on publish tip then republish. @Ada Lovelace

#### chuckles — 2026-08-27T04:05:31.774Z
[refresh-ftr] blocked: merge origin/dev into ftr/AST-1414-estelle-endpoints — CONFLICT files: docs/test-bible/core/tracker.md, docs/test-bible/utils/config.md → @Betty White

#### chuckles — 2026-08-27T01:18:21.662Z
AST-1518 REVIEW — Radia ESCALATE: code(AST-1518) missing on publish tip; recalling Ada to land product + re-test.

#### chuckles — 2026-08-27T01:01:02.144Z
AST-1518 REVIEW — Joan needs plan discuss on job ownership check gap.

#### chuckles — 2026-08-27T00:42:46.335Z
AST-1515 REVIEW — Radia discuss items on pattern catalog and follow-up Slack path.

#### chuckles — 2026-08-27T00:33:12.276Z
AST-1515 REVIEW — Joan needs plan discuss on handler assert bullet.

#### chuckles — 2026-08-26T14:42:53.794Z
@susan dispatch cannot proceed — definition gaps:

- `## Component scope` — missing (required files this epic will touch)
- `## Technical scope` — missing (kind of change per Component scope file)
- Each `####` proposed child needs a **Scope** line (that child's slice of Component/Technical scope) — currently Citations only

Please run define-parent refresh (or paste those sections), then Todo + assignee Chuckles when ready.

---

_Implementation detail may live in git history on `origin/dev`._
