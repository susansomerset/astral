# AST-1555 — Meteorite ingress: staging table + inbox/meteorite consolidation

<!-- linear-archive: AST-1555 archived 2026-10-02 -->

## Linear archive (AST-1555)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Email→job ingress today has no durable spine between fetch, classify, scrape, and land: `meteorite_email.py` still duplicates inbox fetch, `stage_meteorite` stacks an invisible LLM in front of enrich/land with no retry bound, and a Playwright miss re-runs classify on the next poll. This epic adds a flat `meteorite` staging table as the pipeline checkpoint, shrinks `inbox.py` to candidate-scoped Gmail verbs, consolidates the runner into `meteorite.py` state transitions, and deletes `meteorite_email.py`. Downstream `qualify_meteorite` / `job` lifecycle from `METEORITE_NEW` stays untouched. Absorbs Archie’s Discussion draft and her answers to the define open questions (not re-derived under an Original brief).

## Functional scope

1. **Staging table spine** — One `meteorite` row per prospective job (classify fans an N-spec array into N flat rows). States `NEW → SCRAPE_LINK → READY → LANDED`, plus recoverable `BOT_BLOCKED`, retry-holding `ERROR`, and terminal `ABANDONED`. No `SKIPPED` row kept for not-job classify outcomes (audit is the monitoring log). `astral_job_id` is set 1:1 on `LANDED`.
2. **Candidate-scoped inbox verbs** — `inbox` exposes list/filter (`fetch_candidate_email(aliases)`), archive (`archive_candidate_email`), and keep `get_message_html` / `strip_extract`. Caller resolves candidate→aliases via `candidate`. No non-candidate email path; delete `run_fetch_email`, land-bound helpers that fold into meteorite, `FETCH_EMAIL_CONFIG`, and the `fetch_email` task key / seed / provision / due. Delete From-then-To bind machinery (`INBOX_BIND_CONFIG`, `_bind_inbox_message`, `_remaining_to_addresses`) — Manage Email no longer depends on it (see #8). Dependency: `meteorite → inbox → external/gmail` (meteorite never imports Gmail).
3. **Table-driven meteorite steps** — Single module `meteorite.py`: `check_inbox` (task entry: aliases → fetch → inline classify → fan-out N rows → archive mid only after successful classify → stamp last-check), plus dispatcher-driven `stage_meteorite` / `scrape_meteorite` / `land_meteorite` each claiming one state transition. Link outcomes → `SCRAPE_LINK` then Playwright `get_visible_text` / `page_status` → `READY` / `BOT_BLOCKED` / `ERROR`; text outcomes → `READY`; `READY` → create job `METEORITE_NEW` → set `astral_job_id` → `LANDED`. Classify stays **inline** in `check_inbox` (email durability until fan-out commits; N rows are the checkpoint) — not a separate pre-classify dispatch hop.
4. **BOT_BLOCKED recovery via Estelle** — Scheduled scan of `BOT_BLOCKED` with null notify stamp → Estelle DM (paste request + link) → stamp `estelle_notified_at` / `estelle_thread_ts`. Candidate paste in that thread (and unprompted `paste` source_kind) → `apply_paste` → content replaced, state `READY`, no re-classify. Nag limit exceeded → `ABANDONED`. Scrape never touches Slack.
5. **Archive + retention** — Archive Gmail mid after successful classify fan-out only; classify LLM failure leaves mail for next poll (source-ref dedup on re-fetch). Retention is a scheduled query (purge old `LANDED`, surface stale `ERROR` / `BOT_BLOCKED` / `ABANDONED`) — never pipeline code.
6. **Monitoring log contract** — Named helper, **info level, always on** (not Style D / `debug`-gated). Config format string is SSOT. One line per email post-classify (`from`, `mid`, `ts`, sanitized+truncated `subj`, `candidate`, outcome + N jobs). Row transitions at info (`BOT_BLOCKED` / `ERROR` / `LANDED job=`). Subject sanitize strips newlines and truncates.
7. **Simplifications** — Drop `_map_stage_jobs_to_scraps` source-ref synthesis (`email-<mid>`, `-2`, …); provenance is the meteorite row + `astral_job_id`. Jobs land with empty `job_link` / `company_job_id` until qualify extracts. Prefer dissolving the `meteorite ↔ consult` late-import cycle once stage/land live inside meteorite. Keep `ensure_meteorite_company`. Leave `create_meteorite_job` / `create_contact_meteorite` sync create for a separate converge/retire. **Remove unbound age→Trash hygiene** from the poller/`meteorite_email` path (Archie: future Manage Email ownership; out of scope here — okay to delete the logic now).
8. **Manage Email candidate filter** — Drop the “bound candidate” / Matched column. Add a candidate filter defaulting to **All** (list messages regardless of bind). When a candidate is selected, resolve aliases → `fetch_candidate_email` for that candidate only. Land selected-ids goes through meteorite ingress (not deleted bind/land-bound helpers).

**Out of scope: **`qualify_meteorite` dispatch and job lifecycle from `METEORITE_NEW` onward; removing `job.BOT_BLOCKED`; legacy sync create converge/retire; Astral-inbox unbound hygiene as a product feature (logic removed; future Manage Email); dispatch task-key plumbing beyond repointing runners / retiring `fetch_email`. Do **not** block this epic on [AST-1527](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point) children (AST-1529/1530/1531) — Archie treats those Duplicate-parent children as cancelled; consumable stage catalog/outcomes on `dev`/`ftr` may be reused but are not a gate.

## Component scope

* `src/data/database.py` — **modified** — add `meteorite` table + claim/process helpers + insert/update/transition + retention query helpers; header inventory for the new table.
* `src/utils/config.py` — **modified** — meteorite state registry / transition literals; monitoring log format SSOT; task keys for scrape/land/BOT_BLOCKED notify/retention; retire `FETCH_EMAIL_CONFIG` and `INBOX_BIND_CONFIG`; adjust mailbox / stage config for table-driven path; subject sanitize/truncate limits.
* `data/admin/` dispatch / agent_task seed JSON as needed — **modified** — repoint `meteorite_email` runner, remove `fetch_email` seed/provision, add scrape/land/notify/retention rows as required by config.
* `src/core/inbox.py` — **modified** — candidate-scoped fetch/archive verbs; keep HTML get + strip/extract; delete `run_fetch_email`, `_land_bound_inbox_message`, `land_inbox_message_ids`, and bind machinery (`_bind_inbox_message`, `_remaining_to_addresses`, bind enrichment on list).
* `src/core/meteorite.py` — **modified** — `check_inbox`, transition handlers (`stage`/`scrape`/`land`), `apply_paste`, monitoring log helper; stop inline enrich-in-front for this ingress path; drop source-ref scrap synthesis; keep `ensure_meteorite_company`; no unbound Trash hygiene.
* `src/core/meteorite_email.py` — **deleted** — runner shell rehomes to `meteorite.check_inbox`; unbound hygiene deleted with it.
* `src/core/dispatcher.py` — **modified** — drop `fetch_email` branch; wire new meteorite task keys / runner.
* `src/core/candidate.py` and/or `src/data/database.py` candidate helpers — **modified** — stamp last inbox/email check after successful `check_inbox` poll (existing `last_email_check` path or renamed equivalent).
* `src/core/contact.py` — **modified** — route Estelle paste replies for BOT_BLOCKED threads (and unprompted paste already on stage path) into `meteorite.apply_paste` where this epic owns that handoff.
* `src/core/consult.py` — **modified** — only as needed to dissolve stage/land late-import cycle once transitions live in meteorite (no new classify path).
* `src/ui/api/api_inbox.py` — **modified** — list supports All vs candidate-scoped fetch; Land calls meteorite ingress; drop bind/`land_inbox_message_ids` / `run_fetch_email` usage.
* `src/ui/frontend/src/pages/AdminManageEmail.tsx` — **modified** — candidate filter (default All); drop bound/Matched column; selected candidate uses aliases → fetch_candidate path.
* `src/external/gmail.py` / `src/external/playwright.py` — **unchanged** unless a one-line wrapper gap appears; scrape uses existing `get_visible_text` / `page_status`.

## Technical scope

* `database.py` — new `meteorite` table (columns: id, candidate_id, source_kind, source_id, source_ref, state, content, classify_outcome, link, astral_job_id, estelle_thread_ts, estelle_notified_at, nag_count, timestamps, error); new claim-batch / clear-batch / get-by-state helpers; insert N rows from classify fan-out; update state + fields per transition; scheduled retention select/delete helpers; header inventory update.
* `config.py` — new meteorite state / prior_states (or equivalent) registry; monitoring format string + sanitize limits; task_key literals for check/scrape/land/notify/retention; delete `FETCH_EMAIL_CONFIG` and `INBOX_BIND_CONFIG` and related asserts; mailbox config points at `meteorite.check_inbox`.
* admin seed JSON — remove `fetch_email` rows; ensure `meteorite_email` (or renamed) task row runs `check_inbox`; add dispatch rows for scrape/land/BOT_BLOCKED notify/retention with `auto_mode` false at seed.
* `inbox.py` — new public fetch/archive candidate verbs wrapping `external/gmail`; delete fetch_email runner, land-bound entrypoints, and bind helpers; list path no longer attaches `candidate_match` via From-then-To.
* `meteorite.py` — new `check_inbox` (inline `do_task(stage_meteorite)` classify → N inserts → archive → last-check); new/rewritten single-transition `stage`/`scrape`/`land` claim handlers; new `apply_paste`; new always-on info monitoring helper; remove `_map_stage_jobs_to_scraps` synthetic source-refs for this path; land creates job then sets `astral_job_id`; no unbound Trash loop.
* `meteorite_email.py` — delete module (including unbound hygiene).
* `dispatcher.py` — remove `FETCH_EMAIL_CONFIG` task branch; register new meteorite runners.
* `candidate` / DB — stamp helper after poll (reuse or rename `update_candidate_last_email_check`).
* `contact.py` — detect BOT_BLOCKED Estelle thread paste → `apply_paste`; no scrape-from-Slack.
* `consult.py` — trim stage invoke only if cycle removal needs it.
* `api_inbox.py` — All list vs candidate filter → `fetch_candidate_email`; Land → meteorite ingress.
* `AdminManageEmail.tsx` — candidate filter UI default All; remove Matched/bound column; wire filter + Land to new API shape.

## Architectural definition

**Patterns to reuse**

* [`pattern.state.entity-state-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/state/pattern.state.entity-state-transitions.md>) — meteorite row states are a core-decided registry, one transition per dispatch claim.
* [`pattern.batch.entity-claim-process-release`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/batch/pattern.batch.entity-claim-process-release.md>) — scrape/land/notify claim → process → clear with batch_id.
* [`pattern.layers.import-discipline`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>) — meteorite → inbox → gmail; meteorite never imports `external/gmail`; Playwright stays external.
* [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>) — states, log format, task keys, nag limits in config SSOT.
* [`pattern.dispatch.run-next-chain-authority`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/dispatch/pattern.dispatch.run-next-chain-authority.md>) — hop wiring via dispatch rows, not daisy-chained run stacks.
* [`pattern.ui.admin-endpoint`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>) — Manage Email API stays thin over core inbox/meteorite verbs.

**New patterns proposed**

* none (staging-table claim/transition is the existing entity-state + claim-process-release shape applied to a new entity, not a new catalog pattern).

**Applicable statutes**

* [`astral.state.core-decides-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.core-decides-transitions.md>) — core picks next meteorite state.
* [`astral.state.no-daisy-chain-in-run`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.no-daisy-chain-in-run.md>) — scrape/land/notify are separate claims; classify-inline in `check_inbox` is the documented fetch durability exception (email mid until fan-out).
* [`astral.batch.claim-process-release`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/batch/astral.batch.claim-process-release.md>) — transition handlers.
* [`astral.layers.import-direction`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>) / [`astral.layers.core-vs-external-bright-line`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.core-vs-external-bright-line.md>) — inbox/gmail and playwright boundaries.
* [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — Manage Email filter/list stays UI→API→core.
* [`astral.standards.database-header-inventory`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>) — new `meteorite` table.
* [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) / [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — states and log format in config.
* [`astral.standards.logging-via-utils`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>) — monitoring helper via utils logging; always-on info is intentional (not Style D).
* [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>) — Style D remains for `debug=True` paths; monitoring contract is separate always-on info.
* [`astral.agent.do-task-delegation`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/agent/astral.agent.do-task-delegation.md>) — classify still via `do_task(stage_meteorite)`.
* [`astral.dispatch.seed-auto-false`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/dispatch/astral.dispatch.seed-auto-false.md>) — new seed rows.
* [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>) / [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — single-purpose transitions; out-of-scope qualify/legacy create/hygiene-product untouched.

## Acceptance criteria

1. A successful classify of one email that yields N jobs creates exactly N `meteorite` rows and archives the Gmail mid once; a classify LLM failure leaves the mid in inbox and creates zero rows.
2. After fan-out, scrape and land each advance one row one state under their own claim/retry boundary; a Playwright failure on one row does not re-run classify for that email and does not block sibling rows.
3. `not_job_content` (and other no-job classify outcomes) produce no `meteorite` row and no job; the always-on info monitoring line records the email + outcome.
4. `BOT_BLOCKED` rows get an Estelle DM once; candidate paste in that thread moves the row to `READY` without re-classify; exceeding nag limit moves the row to `ABANDONED`.
5. `READY` → land creates a job in `METEORITE_NEW`, sets `astral_job_id`, state `LANDED`; `qualify_meteorite` behavior from that point is unchanged.
6. `inbox.py` has no `run_fetch_email` / `fetch_email` / From-then-To bind path; `meteorite_email.py` is gone; meteorite does not import `external/gmail`; unbound age→Trash hygiene is gone.
7. Retention scheduled path can purge old `LANDED` and list stale `ERROR` / `BOT_BLOCKED` / `ABANDONED` without those deletes living inside transition handlers.
8. Source-ref synthesis (`email-<mid>`, `-2`, …) is not used for provenance on this path; empty `job_link` / `company_job_id` until qualify is acceptable.
9. Manage Email shows a candidate filter defaulting to All (unfiltered list) and, when a candidate is selected, lists via aliases → `fetch_candidate_email`; the bound/Matched column is gone; Land uses meteorite ingress.

## Open questions

none

## Proposed child tickets

#### 1!!: **meteorite table + claim helpers - Ada**

Own the `meteorite` table, state registry in config, and DB claim/insert/update/retention helpers. No inbox verbs, no classify runner, no Estelle, no Manage Email. Does not own dispatch seed rows beyond config literals the later children wire.
**Citations: **`pattern.state.entity-state-transitions`, `pattern.batch.entity-claim-process-release`, `astral.standards.database-header-inventory`, `astral.standards.no-hardcoded-sets`, `astral.state.core-decides-transitions`
**Scope: **`src/data/database.py` (new table + claim/insert/update/retention helpers + header inventory); `src/utils/config.py` (meteorite state registry / transition literals only — not monitoring format or task-key retirements owned by later children)
**Estimate: 5**

#### 2!!: **inbox candidate verbs + Manage Email filter - Hedy**

Shrink `inbox.py` to candidate-scoped fetch/archive + keep HTML/strip helpers; delete `run_fetch_email` / land-bound helpers / bind machinery / `FETCH_EMAIL_CONFIG` / `INBOX_BIND_CONFIG` / dispatcher `fetch_email` branch and seeds. Rewrite Manage Email: candidate filter default All; drop Matched/bound column; selected candidate → aliases → `fetch_candidate_email`; Land → meteorite ingress. Does not implement `check_inbox` or staging transitions.
**Citations: **`pattern.layers.import-discipline`, `pattern.ui.admin-endpoint`, `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.layers.ui-config-driven-business-logic`, `astral.dispatch.seed-auto-false`
**Scope: **`src/core/inbox.py` (candidate verbs; delete fetch/land-bound/bind); `src/utils/config.py` (`FETCH_EMAIL_CONFIG` + `INBOX_BIND_CONFIG` retire); `src/core/dispatcher.py` (`fetch_email` branch remove); `data/admin/` seed JSON for `fetch_email` removal; `src/ui/api/api_inbox.py` (All vs candidate list; Land → meteorite); `src/ui/frontend/src/pages/AdminManageEmail.tsx` (filter + drop Matched column)
**Estimate: 5**

#### 3!: **check_inbox + monitoring log - Katherine**

After #1 and #2: `meteorite.check_inbox` — aliases → fetch → inline classify → fan-out N rows → archive on success → last-check stamp; always-on info monitoring helper + config format SSOT. Rehomes `meteorite_email` runner shell (file may still exist until #6). No unbound Trash hygiene. Does not own scrape/land transitions or Estelle.
**Citations: **`astral.agent.do-task-delegation`, `astral.standards.logging-via-utils`, `astral.standards.debug-contract-gated` (monitoring is explicit non-Style-D info), `astral.state.no-daisy-chain-in-run` (inline classify exception as defined)
**Scope: **`src/core/meteorite.py` (`check_inbox` + monitoring helper; no unbound hygiene); `src/utils/config.py` (monitoring format + mailbox task pointing at check_inbox); `src/core/candidate.py` and/or DB stamp helper; `src/core/dispatcher.py` / `data/admin/` seed for meteorite_email→check_inbox
**Estimate: 5**

#### 4!: **stage / scrape / land transitions - Ada**

After #1: dispatcher-driven single-transition handlers in `meteorite.py` (link→SCRAPE_LINK→Playwright→READY/BOT_BLOCKED/ERROR; text→READY; READY→job METEORITE_NEW→astral_job_id→LANDED). Retire inline enrich-in-front for this path; drop source-ref scrap synthesis. Does not own Estelle notify/paste or file delete.
**Citations: **`pattern.batch.entity-claim-process-release`, `pattern.state.entity-state-transitions`, `astral.batch.claim-process-release`, `astral.state.no-daisy-chain-in-run`, `pattern.layers.import-discipline`
**Scope: **`src/core/meteorite.py` (stage/scrape/land transitions; drop `_map_stage_jobs_to_scraps` synthesis; stop enrich-in-front on this path); `src/utils/config.py` + `data/admin/` + `src/core/dispatcher.py` for scrape/land task keys; `src/core/consult.py` only if cycle trim needed; Playwright via existing `src/external/playwright.py` (unchanged unless gap)
**Estimate: 5**

#### 5: **BOT_BLOCKED Estelle recovery + apply_paste - Hedy**

After #4: notify scan, Estelle DM + stamps, `apply_paste` → READY, nag→ABANDONED, contact paste routing for the thread. Does not own retention purge or `meteorite_email.py` delete.
**Citations: **`pattern.state.entity-state-transitions`, `astral.agent.do-task-delegation` (no re-classify), `astral.layers.core-vs-external-bright-line` (scrape never Slack)
**Scope: **`src/core/meteorite.py` (`apply_paste` + notify/abandon helpers); `src/core/contact.py` (paste → apply_paste); `src/utils/config.py` + dispatcher/seed for notify task / nag limits
**Estimate: 5**

#### 6: **Retention sweep + delete meteorite_email - Katherine**

After #3/#4/#5: scheduled retention query path; delete `meteorite_email.py` (and any leftover unbound hygiene); final seed/dispatcher cleanup; confirm source-ref synthesis, fetch_email, and bind paths are gone. Does not reopen qualify or legacy sync create.
**Citations: **`astral.standards.in-scope-only`, `astral.dispatch.seed-auto-false`, `pattern.config.config-block`
**Scope: **`src/data/database.py` / `src/core/meteorite.py` retention runner wiring; `src/core/meteorite_email.py` **deleted**; leftover config/dispatcher/seed cleanup; any final `consult.py` cycle cleanup left from #4
**Estimate: 3**

**Monolith check:** Functional scope has 8 capabilities; 6 children — not a monolith. Capability 7 (simplifications + hygiene removal) partitions into #4/#6; capability 8 (Manage Email) is #2.

**Scope partition check:** Every Component/Technical file appears in exactly one child’s Scope for its named slice (shared `config.py` / `dispatcher.py` / `data/admin/` / `meteorite.py` / `database.py` sliced by concern).

**Adjacencies: **[AST-1527](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point) Duplicate; Archie treats AST-1529/1530/1531 as cancelled — do not block [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) dispatch on them. Reuse stage catalog/outcomes already on tree if present. [AST-1320](https://linear.app/astralcareermatch/issue/AST-1320/something-looks-wrong-with-meteorite-email-task) (old parse quality) remains Discussion — cancel when this ships if still open. Out-of-scope qualify / `job.BOT_BLOCKED` / legacy sync create / future Manage Email hygiene stay separate.

### Comments

#### chuckles — 2026-09-09T23:49:12.180Z
[check-linear] answered

Ingress row transitions (dispatch `task_key` → claim state → next):

- `stage_meteorite` — claims `NEW` → `SCRAPE_LINK` (link) or `READY` (text)
- `scrape_meteorite` — claims `SCRAPE_LINK` → `READY` / `BOT_BLOCKED` / `ERROR`
- `land_meteorite` — claims `READY` → creates `job` (`METEORITE_NEW`) → `LANDED`

Related (not NEW→READY): `meteorite_email` runs `check_inbox` (classify fan-out into `NEW` rows); `meteorite_bot_blocked_notify`; `meteorite_retention`.

Config SSOT: `METEORITE_INGRESS_DISPATCH_CONFIG` (`stage_task_key` / `scrape_task_key` / `land_task_key`).

#### susan — 2026-09-09T23:47:46.481Z
@chuckles What is the dispatch task_key to evaluate meteorite records to transition them from NEW to READY, etc.?

#### chuckles — 2026-09-09T23:45:55.066Z
[check-linear] answered — not a gap

`READY` meteorite rows are claimed by the dispatcher `land_meteorite` hop (`run_land_meteorite`). That transition creates the `job` in `METEORITE_NEW`, writes `meteorite.astral_job_id`, and advances the row to `LANDED`. After that, existing `qualify_meteorite` owns the job lifecycle — unchanged by this epic.

If you are looking at rows stuck in `NEW` / `SCRAPE_LINK` / `BOT_BLOCKED` / `ERROR`, those have not reached land yet (scrape/notify/retry). Only `READY` → land creates the job.

#### susan — 2026-09-09T23:44:13.477Z
@chuckles I'm not sure how the records in meteorite are supposed to end up in job table at this point.  Is that a gap in this design, or am I just missing something?

#### chuckles — 2026-08-31T23:53:23.556Z
AST-1562 REVIEW — Radia discuss: Betty fix test_meteorite_email.py collection before broad component pytest.

#### chuckles — 2026-08-31T23:18:25.946Z
AST-1559 REVIEW — discuss: AUTO mailbox available_count still zero (AST-1558 deferral); Susan/Archie confirm CLICK-only vs follow-up ticket.

#### chuckles — 2026-08-31T23:03:14.837Z
AST-1560 REVIEW — Joan needs plan discuss on batch_id propagation + row-transition monitoring.

#### chuckles — 2026-08-31T22:56:22.617Z
AST-1558 REVIEW — merge-child blocked; recalling Hedy for missing plan() commit vocabulary on sub tip.

#### chuckles — 2026-08-31T22:54:38.042Z
AST-1558 REVIEW — Radia discuss on sibling bleed / off-manifest test; no product fix-now.

#### chuckles — 2026-08-31T22:44:03.081Z
AST-1557 REVIEW — Radia: product clean; discuss sibling AST-1556 test/bible bleed on sub tip (accept parallel-track carry from origin/tests; no product fix on this child).

#### chuckles — 2026-08-31T22:21:31.690Z
AST-1557 scope-gate cleared — copied Citations/Scope from parent proposed child #1; re-spawning plan-child.

#### chuckles — 2026-08-31T21:36:50.906Z
@susan

1. Unbound Astral-inbox hygiene (age→Trash for messages that do not match the polled candidate) today lives in `meteorite_email`. With only candidate-scoped fetch, where does that hygiene live — fold into `check_inbox` with a wider list pass, a sibling scheduled task, or drop until a follow-up?
2. Manage Email (`AdminManageEmail` + `api_inbox`) still uses From-then-To bind (`INBOX_BIND_CONFIG` / `_bind_inbox_message`) for match display and Land selected-ids. Keep bind for admin in this epic (poller uses candidate verbs; bind stays for Manage Email) and delete bind only in a follow-up, or rewrite Manage Email inside this epic before bind deletion?
3. AST-1527 is Duplicate while AST-1529/1530/1531 remain User Testing. Block AST-1555 dispatch until those land on `origin/dev`, seed this epic’s `ftr` from their tip, or treat stage catalog/outcomes as already consumable and cancel leftover 1527 children after handoff?

---

_Implementation detail may live in git history on `origin/dev`._
