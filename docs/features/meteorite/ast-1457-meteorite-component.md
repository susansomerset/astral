# AST-1457 — Meteorite component

<!-- linear-archive: AST-1457 archived 2026-09-09 -->

## Linear archive (AST-1457)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1457/meteorite-component  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** None / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Meteorite jobs arrive with wildly uneven context — a Slack scrap, a recruiter email with nothing but a link, or a full JD with company already named — while Tracker today assumes the gazer roster path for create, dedupe, and lifecycle. This epic establishes a **Meteorite component** whose public entry is `land_meteorite`: Contact (Estelle/Slack) or inbox (Gmail) hand it scraps of content; meteorite works with agent and gazer to flesh the job out, then saves through Tracker with dedupe **before** create. Jobs gain a durable **source** designation (`gazed` | `meteorite`, one-way gazed→meteorite only). A known gazed job may be superseded as a meteorite regardless of prior state; existing meteorite rows are never clobbered (re-sends land as dedupe skips). Enrichment reuses/repurposes `qualify_meteorite`. Email I/O stays in inbox; meteorite never calls Gmail. AST-1320 (`meteorite_email` parse quality) stays out of scope.

## Functional scope

 1. `land_meteorite` **public entry** — One core function accepts candidate-bound scraps (partial or full text, links, optional company hints, provenance) from Contact or inbox, orchestrates agent + gazer to flesh out a job object, and returns structured create/skip/error outcomes — not raw HTML insert alone.
 2. **Tracker-backed dedupe before create** — Meteorite delegates identity/dedupe and first write to Tracker; skip create when a matching job already exists; outcomes are explicit (created / duplicate-skip / error).
 3. **Job source designation** — Every job carries `gazed` or `meteorite`. Transition **gazed → meteorite** is allowed; **meteorite → gazed** is forbidden.
 4. **Supersede gazed, never clobber meteorites** — When a matching gazed job is found, meteorite may supersede it (source → `meteorite`, treat as a new meteorite landing — do **not** gate on the gazed job’s prior state). When a matching **meteorite** already exists, do not overwrite it — dedupe skip (candidates often re-send/forward the same job).
 5. **Known company, placeholder attach** — Intake may learn a real employer name; the job still attaches under `meteorite-{candidate_id}`, with the known name preserved in job metadata — no automatic roster company create in this epic.
 6. **No email I/O inside meteorite** — Meteorite exposes `land_meteorite` and save only; Gmail list/get/archive stays in inbox/external.
 7. **Job-listing intake API** — Authenticated endpoint receives a listing packet for a bound candidate and calls `land_meteorite` (thin HTTP wrapper for adapters that prefer HTTP over core import).
 8. **Thin inbox +** `fetch_email` **task** — Inbox hosts `fetch_email`: list/fetch, bind to candidate, scrape/normalize, call `land_meteorite` — replacing direct `create_meteorite_job` / duplicated Ruth+scrape decisions on the retargeted paths.
 9. **Repurpose** `qualify_meteorite` — Packet→job-object enrichment uses the existing `qualify_meteorite` task (repurposed), not a brand-new Grace task_key and not expanding AST-1320 `meteorite_email` parse work in this epic.
10. **Debug observability** — When `debug=True` on touched meteorite and inbox handoff paths, Style D index headers (`index N/M`, primary id, outcome) plus `|` working detail show found vs recorded; no new contract lines when `debug=False`.

## Component scope

* `src/utils/config.py` — **modified** — job source allowed values, meteorite intake/`land_meteorite` literals, `fetch_email` dispatch seed, METEORITE_CONFIG extensions; `qualify_meteorite` TASK_CONFIG adjustments for packet enrichment.
* `src/data/database.py` — **modified** — persist job source on the job row (header inventory update); dedupe helpers for meteorite vs gazed supersede rules.
* `src/core/tracker.py` — **modified** — meteorite-aware save/dedupe: create new, supersede gazed→meteorite, never clobber existing meteorite.
* `src/core/meteorite.py` — **modified** — public `land_meteorite`; orchestration with agent + gazer; no Gmail imports.
* `src/core/agent.py` / `src/core/consult.py` — **modified** — wire/repurpose `qualify_meteorite` for land enrichment.
* `src/core/inbox.py` — **modified** — thin fetch/bind/scrape; call `land_meteorite`.
* `src/core/gaze_email.py` — **modified** — retarget bound email ingest to `land_meteorite`.
* `src/core/gazer.py` — **modified** — retarget email HTML ingest helpers still on this path to `land_meteorite` / land-owned flesh-out.
* `src/core/dispatcher.py` — **modified** — seed `fetch_email` dispatch rows; keep meteorite dispatch rows consistent with repurposed qualify.
* `src/core/contact.py` — **modified** — Estelle/Slack path hands scraps to `land_meteorite` (no parallel create).
* `src/ui/api/api_meteorite.py` — **modified** — listing intake endpoint wrapping `land_meteorite`.
* `src/ui/api/api_inbox.py` — **modified** — admin inbox surfaces call thin inbox helpers only.
* `tests/component/core/test_meteorite.py` — **modified** — `land_meteorite` + source + dedupe/supersede contracts.
* `tests/component/core/test_inbox.py` — **modified** — fetch_email → `land_meteorite` handoff.
* `tests/component/ui/api/test_api_meteorite.py` — **modified** — intake API surface.

## Technical scope

* [**config.py**](<http://config.py>) — Job source enum/list and defaults; METEORITE intake/`land_meteorite` keys; `fetch_email` dispatch_task seed; adjust `qualify_meteorite` TASK_CONFIG for packet enrichment (schema/prompts as plan chooses within this epic’s AC).
* [**database.py**](<http://database.py>) — Job source column on `job` + header inventory; `save_job` read/write source; helpers distinguishing gazed-match (supersede) vs meteorite-match (skip).
* [**tracker.py**](<http://tracker.py>) — Meteorite save entry: accept enriched job object + candidate context; dedupe; create or gazed-supersede; refuse clobber of existing meteorite; return structured outcomes.
* [**meteorite.py**](<http://meteorite.py>) — Public `land_meteorite`: validate candidate, ensure placeholder company, collaborate with gazer scrapers + `qualify_meteorite` enrichment, map to Tracker save, enforce source rules.
* **[consult.py](<http://consult.py>) / [agent.py](<http://agent.py>)** — Invoke repurposed `qualify_meteorite` for land enrichment; RESPONSE via existing agent_data patterns.
* [**inbox.py**](<http://inbox.py>) — `fetch_email` runner: Gmail via external, bind via INBOX_BIND_CONFIG, normalize/scrape into scraps, call `land_meteorite`.
* **gaze_email.py / [gazer.py](<http://gazer.py>)** — Replace direct `create_meteorite_job` with `land_meteorite`; archive/trash/stamp stay outside meteorite where already law.
* [**dispatcher.py**](<http://dispatcher.py>) — Seed `fetch_email`; align qualify/GDL claim rows with land outcomes.
* [**contact.py**](<http://contact.py>) — Slack/Estelle scrap path calls `land_meteorite`.
* **api_meteorite.py** — POST listing packet → `land_meteorite` → JSON outcomes.
* **api_inbox.py** — Route Land Meteorite / create through inbox → `land_meteorite`.

## Architectural definition

* **Patterns to reuse**
  * [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>) — job source, land literals, `fetch_email` seed, `qualify_meteorite` config in blocks.
  * [`pattern.state.entity-state-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/state/pattern.state.entity-state-transitions.md>) — land enters **METEORITE_NEW** (or existing meteorite landing states); gazed supersede flips source without inventing illegal transitions; core decides.
  * [`pattern.batch.entity-claim-process-release`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/batch/pattern.batch.entity-claim-process-release.md>) — `fetch_email` and qualify/GDL keep claim/process/release.
  * [`pattern.batch.entity-agent-responses`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/batch/pattern.batch.entity-agent-responses.md>) — qualify RESPONSE via entity_id latest-refs.
  * [`pattern.layers.import-discipline`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>) — Gmail/Playwright external; inbox/contact bind; meteorite orchestrates; UI thin.
  * [`pattern.ui.admin-endpoint`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>) — intake API + inbox admin authenticated thin wrappers.
  * [`pattern.agent.prompt-persist-before-provider`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/agent/pattern.agent.prompt-persist-before-provider.md>) — qualify enrichment persists before provider.
* **New patterns proposed**
  * `land_meteorite` **multi-ingress orchestration** — one public core entry for Contact + inbox scraps → agent/gazer flesh-out → Tracker dedupe save. Flag for Archie approval before catalog law.
  * **Job source one-way promotion with meteorite-non-clobber** — gazed→meteorite supersede allowed; existing meteorite never overwritten on re-send. Flag for Archie approval.
* **Applicable statutes**
  * [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) / [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
  * [`astral.standards.database-header-inventory`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>)
  * [`astral.layers.core-vs-external-bright-line`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.core-vs-external-bright-line.md>) / [`astral.layers.import-direction`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
  * [`astral.agent.do-task-delegation`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/agent/astral.agent.do-task-delegation.md>)
  * [`astral.state.core-decides-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.core-decides-transitions.md>) / [`astral.state.job-prior-states-enforced`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.job-prior-states-enforced.md>) / [`astral.state.no-daisy-chain-in-run`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.no-daisy-chain-in-run.md>)
  * [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>) / [`astral.standards.data-raises-caller-logs`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>)
  * [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) / [`astral.patterns.require-auth-on-protected-endpoints`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/patterns/astral.patterns.require-auth-on-protected-endpoints.md>)
  * Universal product-code set for all `src/` changes.

## Acceptance criteria

 1. Contact (Estelle/Slack) or inbox can call `land_meteorite` with scraps (link-only, text-only, or both) and get created / duplicate-skip / error — never a silent no-op.
 2. Tracker dedupe runs before insert; a matching **existing meteorite** is never overwritten (skip); a matching **gazed** job may be superseded to `meteorite` without checking the gazed job’s prior state.
 3. Every job row touched by this epic exposes `gazed` or `meteorite`; existing rows backfilled to `gazed` where source was unset.
 4. Attempting meteorite → gazed is rejected by core (config/test enforced).
 5. When intake learns an employer name, the job remains on `meteorite-{candidate_id}` with the name in job metadata, visible to operators.
 6. `src/core/meteorite.py` has no Gmail/mailbox imports; inbox `fetch_email` and Contact call `land_meteorite`.
 7. Authenticated listing intake API wraps `land_meteorite` and returns the same outcome shape.
 8. Production Land Meteorite / gaze_email create decisions go through `land_meteorite`, not direct `create_meteorite_job` HTML insert.
 9. Packet→job enrichment uses repurposed `qualify_meteorite`; AST-1320 `meteorite_email` empty-`jobs` quality is **not** required for this epic to pass UAT.
10. With `debug=True`, each packet/job shows Style D found→recorded; with `debug=False`, no new debug-contract noise on touched paths.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Job source + Tracker meteorite save - Ada**

Config-owned job source, job column + backfill, Tracker save/dedupe: create, gazed-supersede (any prior state), never clobber existing meteorite. Shared by all later slices.

**Citations:** `pattern.config.config-block`, `pattern.state.entity-state-transitions`; `astral.config.config-source-of-truth`, `astral.standards.database-header-inventory`, `astral.standards.no-hardcoded-sets`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced`.

**Scope:** `src/utils/config.py` (source enum, METEORITE_CONFIG extensions, `fetch_email` seed literals, `qualify_meteorite` TASK_CONFIG adjustments for packet enrichment); `src/data/database.py` (job source column, save_job, dedupe helpers); `src/core/tracker.py` (meteorite save, gazed supersede, meteorite non-clobber).

**Estimate: 5**

#### 2!!: **land_meteorite + qualify_meteorite enrichment - Hedy**

Public `land_meteorite`: scraps in → agent + gazer flesh-out via repurposed `qualify_meteorite` → Tracker save from #1; placeholder company; known-company metadata; Style D. After #1.

**Citations:** `pattern.agent.prompt-persist-before-provider`, `pattern.batch.entity-agent-responses`, `pattern.layers.import-discipline`; `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.standards.data-raises-caller-logs`, `astral.state.no-daisy-chain-in-run`.

**Scope:** `src/core/meteorite.py` (`land_meteorite`, no Gmail); `src/core/agent.py` / `src/core/consult.py` (invoke repurposed `qualify_meteorite`); `tests/component/core/test_meteorite.py`.

**Estimate: 5**

#### 3!: **Meteorite intake API + Contact land path - Katherine**

Authenticated listing API wrapping `land_meteorite`; Contact/Estelle scrap path calls `land_meteorite`. After #2.

**Citations:** `pattern.ui.admin-endpoint`; `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`.

**Scope:** `src/ui/api/api_meteorite.py` (listing intake); `src/core/contact.py` (call `land_meteorite`); `tests/component/ui/api/test_api_meteorite.py`.

**Estimate: 3**

#### 4: **Inbox fetch_email + gaze_email retarget - Katherine**

Inbox `fetch_email`: bind, fetch, scrape/normalize, call `land_meteorite`; retarget gaze_email / gazer email ingest and inbox admin create to `land_meteorite`. After #2.

**Citations:** `pattern.batch.entity-claim-process-release`, `pattern.layers.import-discipline`, `pattern.ui.admin-endpoint`; `astral.layers.core-vs-external-bright-line`, `astral.layers.import-direction`, `astral.dispatch.seed-auto-false`.

**Scope:** `src/core/inbox.py` (`fetch_email` → `land_meteorite`); `src/core/gaze_email.py`; `src/core/gazer.py` (email ingest retarget); `src/core/dispatcher.py` (`fetch_email` seed); `src/ui/api/api_inbox.py`; `tests/component/core/test_inbox.py`.

**Estimate: 5**

**New patterns:** #2 introduces `land_meteorite` multi-ingress orchestration; #1 introduces job source one-way promotion with meteorite non-clobber — both flagged for Archie approval.

**Monolith check:** Ten functional capabilities → four children; schema/save (#1) separate from orchestration (#2) and ingress (#3–#4).

**Scope partition check:** Every Component/Technical file appears in exactly one child Scope — `config.py` entirely in #1; orchestration invoke in #2; Contact+API in #3; inbox/gaze/gazer/dispatcher/api_inbox in #4.

**Out of scope:** AST-1320 `meteorite_email` parse-quality fix — separate ticket.

---

## Original brief

We have tracker for job creation and record management, but meteorites are special creatures.  They come in from email and from Slack.  The might have just a bit of text or a link or the full compliment of context including company.  We need to be able to flesh out the meteorite as a new job object and then save it using tracker to dedupe before creating.  If we know the job and it has failed before GDL, we run it again as a meteorite.  Job needs a source designation to indicate gazed or meteorite, which can go from gazed to meteorite but not the other direction.  Company can now be known from meteorites and still use meteorite-candidate as the placeholder.  The component does not call email, but has an endpoint that can receive a job listing from or for abound candidate.  We can extend task to fetch email, uses a tiny component for inbox to host the fetch_email task, which then calls the meteorite component to bind email to a candidate, scrape content, and send the packet of all available information to a Grace prompt that can return a job object that could be deduped when sent by meteorite to tracker for saving.

### Comments

#### chuckles — 2026-08-25T03:41:22.835Z
AST-1470 REVIEW — Joan needs plan discuss on land do_task batch_id + late-import.

#### chuckles — 2026-08-24T22:30:15.128Z
AST-1469 gated on AST-1473 — LINEAR_KEY_JOAN missing on chuckles host; Joan validate-plan §3i cannot post. @susan

#### chuckles — 2026-08-24T21:56:40.689Z
@susan

1. **Slack ingress** — Should Slack Contact/Estelle post the same JSON packet shape to the meteorite intake API, or does Slack need its own adapter child that normalizes DM/thread content first?
2. **Pre-GDL gazed retry states** — Which gazer-track job states count as “failed before GDL” for retry-as-meteorite (e.g. pre-qualify error states only, or any gazer job before **JD_READY** / before first successful qualify)?
3. **Grace enrichment task** — One new task_key for packet→job-object, or fold/replace the existing `meteorite_email` + `qualify_meteorite` chain inside meteorite orchestration?
4. **Phasing vs AST-1320** — Is fixing `meteorite_email` empty-`jobs` parse quality in scope of this epic, or does AST-1320 stay a separate fix-lane/discussion ticket?

---

_Implementation detail may live in git history on `origin/dev`._
