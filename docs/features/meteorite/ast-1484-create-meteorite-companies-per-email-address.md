# AST-1484 — Create meteorite companies per email address

<!-- linear-archive: AST-1484 archived 2026-09-09 -->

## Linear archive (AST-1484)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Meteorite jobs today all hang under one placeholder company per candidate (`meteorite-{candidate_id}` in IGNORE), so operators cannot tell which mailbox sender or job-link source produced a landing. This epic creates (or reuses) companies in a new **METEORITE** company state, keyed by Ruth-discerned sender (`{email}-{candidate}` or `meteorite-self-{candidate}`) or by a job-link slug (`{slug}-{candidate}`) when one is available, and lands the job under that company — provenance is visible from the company short_name. Email-bound lands leave the monolithic placeholder; Slack/Contact without email sender keep `meteorite-{candidate_id}` but move that placeholder onto **METEORITE** (not IGNORE) for a single track.

## Functional scope

1. **METEORITE company state** — Register company state `METEORITE` (roster-inert like IGNORE: no gaze/prefilter batch criteria). New and legacy meteorite placeholder companies use this state instead of IGNORE.
2. **Ruth discerns company stem** — On email-bound land/qualify enrichment, Ruth chooses the company short_name stem: original sender email, literal `meteorite-self` when the message is from the candidate and not a forward, or a job-link **slug** when a usable link/slug is present. Core does not hard-code forward/autoforward header logic — Ruth decides from CONTENT.
3. **Ensure METEORITE company** — Idempotently ensure `{stem}-{candidate_id}` in state **METEORITE**, owned by that candidate; reuse on repeat stems.
4. **Land under that company** — Email-bound meteorite create/land attaches the job to the ensured company, not to a generic undifferentiated bucket when a stem is known.
5. **Track recognition** — Meteorite-track carve-outs (consult/GDL/title-pattern skip) recognize companies in state **METEORITE** and/or jobs already on `METEORITE_*` job states; keep a legacy short_name fallback for any remaining `meteorite-{candidate}` rows not yet re-stated.
6. **Non-email ingress** — Slack/Contact/`land_meteorite` without an email sender still use `meteorite-{candidate_id}`, ensured in **METEORITE**.
7. **Debug observability** — When `debug=True` on touched ensure/land paths, Style D shows stem, company short_name, and create-vs-reuse; no new contract lines when `debug=False`.

## Component scope

* `src/utils/config.py` — **modified** — `COMPANY_STATES["METEORITE"]`; METEORITE_CONFIG company_state → METEORITE; short_name templates for sender/self/slug stems; any Ruth field / land outcome literals.
* `src/core/meteorite.py` — **modified** — ensure by stem + candidate into METEORITE; track predicate via company state (+ legacy prefix); create/`land_meteorite` attach under ensured company when stem present.
* `src/core/consult.py` / `src/core/agent.py` — **modified** — land/qualify enrichment: Ruth returns company stem (sender / meteorite-self / slug); prompts + schema as plan chooses within this epic.
* `src/core/inbox.py` — **modified** — email land paths supply CONTENT so Ruth can discern; pass resulting stem into meteorite ensure/create (no Gmail inside meteorite).
* `src/core/gaze_email.py` — **modified** — same for gaze_email / Land Meteorite selected-id paths.
* `src/core/gazer.py` — **modified** — only if email HTML ingest still creates here; shared sender/slug-aware ensure path.
* `src/ui/api/api_companies.py` / `src/ui/api/api_system.py` — **modified** — only if operators need a METEORITE company list/count sibling to Ignored (thin state filter; no new business rules in UI).
* `src/utils/config.py` NAV / frontend routes — **modified** only if a Companies → Meteorite nav item is required for UAT visibility (same carve-out as api_companies).

## Technical scope

* `config.py` — Add `METEORITE` to COMPANY_STATES; point METEORITE_CONFIG `company_state` at it; templates for `{stem}-{candidate_id}` and `meteorite-self` literal; optional nav path literals.
* `meteorite.py` — Ensure get-or-insert by stem; `is_meteorite_company` (or successor) true when company state is METEORITE (legacy `meteorite-` prefix fallback); create/`land_meteorite` use ensured short_name when stem known.
* `consult.py` / `agent.py` — Extend land/`qualify_meteorite` enrichment so Ruth returns a company stem (email, `meteorite-self`, or link slug) from CONTENT; no core header-parser for forwards.
* `inbox.py` / `gaze_email.py` / `gazer.py` — Pass message CONTENT into enrichment; apply returned stem to ensure+attach; single shared company-create path.
* `api_companies.py` / `api_system.py` / NAV — Optional list/count for state METEORITE if Archie needs a sidebar sibling to Ignored for tracing UAT.

## Architectural definition

* **Patterns to reuse**
  * [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>) — METEORITE company state + stem templates in config.
  * [`pattern.state.entity-state-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/state/pattern.state.entity-state-transitions.md>) — companies enter METEORITE; jobs stay on METEORITE_* land/GDL states; core decides.
  * [`pattern.layers.import-discipline`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>) — Gmail external; inbox/gaze supply CONTENT; meteorite ensures + lands.
  * [`pattern.agent.prompt-persist-before-provider`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/agent/pattern.agent.prompt-persist-before-provider.md>) — Ruth stem discernment persists before provider.
  * [`pattern.batch.entity-agent-responses`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/batch/pattern.batch.entity-agent-responses.md>) — enrichment RESPONSE via existing entity refs.
  * [`pattern.ui.admin-endpoint`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>) — only if METEORITE company list endpoint/nav is in scope.
* **New patterns proposed**
  * **METEORITE company state + stem-keyed placeholders** — companies in METEORITE keyed by Ruth stem (sender / self / slug) + candidate for provenance. Flag for Archie approval before catalog law.
* **Applicable statutes**
  * [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
  * [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
  * [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>)
  * [`astral.layers.core-vs-external-bright-line`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.core-vs-external-bright-line.md>) / [`astral.layers.import-direction`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
  * [`astral.state.core-decides-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/state/astral.state.core-decides-transitions.md>)
  * [`astral.agent.do-task-delegation`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/agent/astral.agent.do-task-delegation.md>) — Ruth stem via do_task, not ad-hoc LLM in core.
  * [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
  * Universal set for product code (in-scope-only, data-raises-caller-logs, logging-via-utils, public-then-helpers, names-not-ticket-ids, no-cross-contamination, database-header-inventory if company_data changes).

## Acceptance criteria

1. `METEORITE` exists in COMPANY_STATES; new meteorite placeholder companies are created in **METEORITE**, not IGNORE.
2. Ruth-discerned stem `alice@example.com` for candidate `somerset` ensures company `alice@example.com-somerset` (or the config-normalized form of that template) in METEORITE; idempotent on repeat.
3. When Ruth returns `meteorite-self`, the company short_name is `meteorite-self-{candidate_id}` in METEORITE.
4. When Ruth returns a job-link slug stem, the company short_name is `{slug}-{candidate_id}` in METEORITE.
5. Email-bound create/land attaches the job’s `company` to that ensured short_name.
6. Meteorite-track carve-outs treat METEORITE-state companies (and METEORITE_* jobs) as meteorite track; legacy `meteorite-{candidate}` rows still work until restated.
7. Slack/Contact lands without email sender still use `meteorite-{candidate_id}` in METEORITE.
8. Existing jobs under old IGNORE placeholders are not bulk-migrated in this epic (optional leave-in-place); new ensures use METEORITE.
9. With `debug=True`, ensure/land emit Style D for stem and company; with `debug=False`, no new debug-contract noise.

## Open questions

none

## Proposed child tickets

#### 1!!: **METEORITE company state + stem ensure + track detection - Ada**

Register `COMPANY_STATES["METEORITE"]`; flip METEORITE_CONFIG company_state; ensure `{stem}-{candidate}` idempotently; track predicate via company state (+ legacy prefix); Style D on ensure. Does **not** own Ruth prompts or inbox wiring.

**Citations: **`pattern.config.config-block`, `pattern.state.entity-state-transitions`; `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.debug-contract-gated`, `astral.state.core-decides-transitions`, `astral.standards.dry-and-focused-functions`.

**Scope: **`src/utils/config.py` — modified — COMPANY_STATES METEORITE; METEORITE_CONFIG company_state + stem templates + meteorite-self literal. `src/core/meteorite.py` — modified — ensure by stem+candidate into METEORITE; broaden track detection via company state (+ legacy prefix); Style D on ensure.

**Estimate: 5**

#### 2!: **Ruth company-stem discernment (sender / self / slug) - Hedy**

Land/`qualify_meteorite` enrichment: Ruth returns company stem from CONTENT (original sender email, `meteorite-self`, or job-link slug). After #1. Does **not** own ensure API or inbox path wiring (#1 / #3).

**Citations: **`pattern.agent.prompt-persist-before-provider`, `pattern.batch.entity-agent-responses`; `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.standards.no-hardcoded-sets`.

**Scope: **`src/core/consult.py` / `src/core/agent.py` — modified — enrichment invoke + RESPONSE mapping for company stem. `src/utils/config.py` — modified — TASK_CONFIG / schema / prompt literals for the stem field only (shared file; units not owned by #1). Catalog/`agent_task` row updates as plan chooses within this child.

**Estimate: 3**

#### 3: **Email land paths apply stem → company attach - Katherine**

Inbox + gaze_email (+ gazer if needed) supply CONTENT, take Ruth stem, call #1 ensure, attach job under that company in create/`land_meteorite`. Optional thin METEORITE company list/nav if needed for UAT. After #1 and #2.

**Citations: **`pattern.layers.import-discipline`, `pattern.ui.admin-endpoint`; `astral.layers.core-vs-external-bright-line`, `astral.layers.import-direction`, `astral.standards.debug-contract-gated`, `astral.standards.dry-and-focused-functions`.

**Scope: **`src/core/inbox.py` — modified — CONTENT + stem → ensure/attach. `src/core/gaze_email.py` — modified — same. `src/core/gazer.py` — modified — only if still creating on this path. `src/core/meteorite.py` — modified — create/`land_meteorite` attach when stem present (shared file; units not owned by #1). `src/ui/api/api_companies.py` / `src/ui/api/api_system.py` / NAV+routes — modified — only if METEORITE company list/count sibling ships in this epic.

**Estimate: 5**

**New patterns:** #1 introduces METEORITE company state + stem-keyed placeholders — flagged for Archie approval.

**Monolith check:** Seven functional capabilities → three children (state/ensure, Ruth stem, email wire).

**Scope partition check:** COMPANY_STATES + ensure/track in #1; Ruth enrichment units in #2; inbox/gaze/gazer/optional UI + land attach in #3 — no double-claimed units.

**Out of scope:** Bulk migration of historical IGNORE `meteorite-{candidate}` jobs; inventing core forward-header parsers; AST-1320 `meteorite_email` parse quality.

---

## Original brief

When an email is bound to a candidate, identify the sender email, if possible (use "meteorite-self" if it was just from the candidate and wasn't a forwarded message, etc.

With the parsed sender email, create "[sender@emailaddress](<mailto:sender@emailaddress>)-<candidate>" company in state IGNORE, and create the job for that company.

It's too hard right now to trace back where a meteorite came from.

### Comments

#### chuckles — 2026-08-26T17:53:48.503Z
AST-1495 REVIEW — merge-child blocked; recalling Katherine for git-pull merges on sub (need merge-resume republish).

#### chuckles — 2026-08-26T17:10:01.217Z
AST-1495 REVIEW — merge-child blocked; recalling @Katherine Johnson to republish sub without git-pull merge commits.

#### chuckles — 2026-08-26T03:51:45.711Z
@susan
1. Short_name shape vs track prefix — Prefer (A) exact `{sender@email}-{candidate}` and broaden detection, (B) `meteorite-{sender_token}-{candidate}` keeping the `meteorite-` prefix, or (C) other? Must `@` appear literally, or may we normalize if storage/UI rejects it?
2. Forward vs self — When From is the candidate’s address, how do we decide it wasn’t a forwarded message?
3. Autoforwards (candidate on To, recruiter on From) — is From always the sender token, or sometimes a body original-from?

---

_Implementation detail may live in git history on `origin/dev`._
