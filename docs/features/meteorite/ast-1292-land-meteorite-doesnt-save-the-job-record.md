# AST-1292 — Land Meteorite doesn't save the job record

<!-- linear-archive: AST-1292 archived 2026-08-19 -->

## Linear archive (AST-1292)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1292/land-meteorite-doesnt-save-the-job-record  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

On staging, **Land Meteorite** can return a green toast that reads as passed with zero errors while **no new job row** appears. After AST-1129 shipped selected-ids ingest, Archie needs Land Meteorite to either persist a **METEORITE_NEW** job when a selected message is successfully landable, or make it obvious that nothing was written — never a success-shaped pass when the job table did not gain a row for that land.

## Functional scope

1. **Job persist on successful land** — When Land Meteorite processes a selected, candidate-bound inbox message through the shared `gaze_email` selected-ids ingest path and that path produces a creatable job (scrape/parse yields landable JD content that is not a per-candidate duplicate skip), a new job record is saved in **METEORITE_NEW** and is visible in the job table for that candidate.
2. **Honest per-message outcomes** — Each selected message’s returned `outcome` distinguishes cases where a job was created from cases where the message was skipped, ignored, archived without create, failed, or errored. Operators and debug traces can tell whether a job row was recorded.
3. **Honest operator feedback on Manage Email** — After Land Meteorite, the on-page results and toast do **not** present a green / “passed without errors” success when zero jobs were created for the selection. Success-shaped feedback is reserved for runs that actually recorded at least one new job (or an explicitly approved product equivalent Susan confirms in Open questions).
4. **Debug observability (backend)** — When `debug=True` on touched Land Meteorite / selected-ids ingest paths, log what was found and what was recorded per selected message (create vs skip vs ignore vs archive-without-create vs fail/error), Style D index headers with `index N/M`, primary message id, outcome; working detail lines prefixed with two spaces, pipe, two spaces; long payloads truncated per AST-538 / Code Rules. No React debug requirements.

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — keep Land Meteorite on the thin authenticated admin surface; React stays presentational; create/skip/fail decisions stay server-side.
  * `pattern.layers.import-discipline` — mailbox I/O stays external; core owns selected-ids ingest and job create; UI calls core via API only.
  * `pattern.state.entity-state-transitions` — land still stops at **METEORITE_NEW**; no daisy-chain into qualify/GDL.
  * `pattern.config.config-block` — reuse `GAZE_EMAIL_CONFIG` / meteorite ingest literals; do not invent a parallel Land-Meteorite config block for the same path.
* **New patterns proposed**
  * none — bugfix on the shipped AST-1129 Land Meteorite stack (selected-ids core + admin API + Manage Email feedback).
* **Applicable statutes**
  * `astral.layers.core-vs-external-bright-line` / `astral.layers.import-direction` — mailbox vs core policy.
  * `astral.layers.ui-config-driven-business-logic` / `astral.patterns.require-auth-on-protected-endpoints` — admin mutator auth + thin UI.
  * `astral.config.config-source-of-truth` — outcome / state literals from config.
  * `astral.state.no-daisy-chain-in-run` / `astral.state.core-decides-transitions` / `astral.state.job-prior-states-enforced` — **METEORITE_NEW** only; core decides create/transition.
  * `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` / `astral.standards.no-hardcoded-sets` — Land Meteorite persist + honesty only; no unrelated Manage Email / dispatcher redesign.
  * `astral.standards.debug-contract-gated` — Style D only when `debug=True`.
  * `astral.standards.data-raises-caller-logs` — data raises; callers log; create failures must not look like silent success.
  * `universal` product-code set for any `src/` change.

## Boundaries

* Does **not** redesign Manage Email beyond Land Meteorite outcome/toast honesty (no multi-select rewrite, no revive of retired Create, no nav/Topic Menu work).
* Does **not** redesign dispatcher `gaze_email` / Scheduled Actions Avail (adjacent **AST-1282** `parse_meteorite_email` avail mismatch stays its own ticket).
* Does **not** change From→candidate bind rules, qualify/GDL, Recommended, LIKE/upshot, or attachments.
* Does **not** stamp `candidate.last_email_check` on Land Meteorite (stamp stays dispatcher-only).
* Does **not** invent a second ingest pipeline or call the retired Create strip/extract create-job path.
* Does **not** force whole-inbox processing when nothing is selected.
* Does **not** own AST-1087/AST-1128 feature expansion beyond what is required to fix Land Meteorite job persist + operator honesty on staging.

## Acceptance criteria

1. On staging, for a candidate-bound inbox message that is landable (produces creatable JD content and is not a per-candidate duplicate skip), running **Land Meteorite** on that selection results in a new **METEORITE_NEW** job row visible in the job table for that candidate.
2. When Land Meteorite creates zero jobs for a selection, Manage Email does **not** show a green success toast that reads as passed with zero errors.
3. After Land Meteorite, Archie can see per-selected-message outcomes that make create vs skip/ignore/archive-without-create vs fail/error distinguishable without leaving Manage Email.
4. A Land Meteorite run that records a new job does not advance that job into qualify/GDL and does not update `candidate.last_email_check`.
5. With `debug=True`, each selected message’s found → recorded path (including whether a job id was written) is visible in Style D; with `debug=False`, no new debug noise from this fix.
6. Unbound / unmatched selected messages remain explicit skips and do not block bound siblings in the same batch.

## Dependencies and blockers

* Built on Done **AST-1129** (AST-1140 selected-ids core, AST-1141 admin API, AST-1142 Manage Email Land Meteorite UI).
* Related (not a blocker): **AST-1282** — dispatcher `parse_meteorite_email` avail/skip on Scheduled Actions; different surface from Manage Email Land Meteorite.
* Adjacent in flight on Astral Meteorite (do not collide): AST-1088–1090 / AST-1106–1107 still User Testing on `gaze_email`.
* none otherwise.

## Open questions

1. When Land Meteorite archives a bound message after **all** link attempts were skips (duplicate / too-short) and creates **zero** jobs — should operator feedback be non-success with an explicit “no jobs created” signal (recommended from this UAT report), or is archive-without-create still allowed to look like a quiet success as long as the results panel lists skip/archive outcomes?
2. For the email you landed: what raw per-message `outcome` string did the **Land Meteorite results** panel show, and was the row **Matched** to a candidate beforehand?

## Proposed child tickets

#### 1!: **Land Meteorite selected-ids persist + outcome honesty - Ada**

Owns the shared selected-ids / bound ingest path so a landable selected message actually records a **METEORITE_NEW** job, and so per-message outcomes and totals distinguish created vs skip/ignore/archive-without-create vs fail/error (including Style D when `debug=True`). Does **not** own Manage Email toast/results chrome (sibling #2). Does **not** own AST-1282 dispatcher avail.
**Citations:** `pattern.layers.import-discipline`; `pattern.state.entity-state-transitions`; `pattern.config.config-block`; `astral.state.core-decides-transitions`; `astral.standards.debug-contract-gated`; `astral.standards.data-raises-caller-logs`; `astral.standards.in-scope-only`.

#### 2: **Manage Email Land Meteorite feedback honesty - Katherine**

After #1: Manage Email Land Meteorite results + toast must not present green / “passed without errors” success when zero jobs were created for the selection; surface the honest per-message outcomes from the admin API. Does **not** redesign selection chrome or revive Create. Does **not** own core ingest (sibling #1).
**Citations:** `pattern.ui.admin-endpoint`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`.

**New patterns:** none.

**Monolith check:** Functional scope has 4 capabilities; 2 children — core/API persist + outcome contract, then Manage Email feedback — split across layers intentionally.

---

## Original brief

I ran "Land Meteorite" for an email and got a green toast saying it had passed without errors, but no new data is in the job table.

### Comments

#### chuckles — 2026-08-09T17:44:48.370Z
@susan

1. When Land Meteorite archives a bound message after all link attempts were skips (duplicate / too-short) and creates zero jobs — should operator feedback be non-success with an explicit “no jobs created” signal (recommended from this UAT report), or is archive-without-create still allowed to look like a quiet success as long as the results panel lists skip/archive outcomes?
2. For the email you landed: what raw per-message `outcome` string did the Land Meteorite results panel show, and was the row Matched to a candidate beforehand?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
