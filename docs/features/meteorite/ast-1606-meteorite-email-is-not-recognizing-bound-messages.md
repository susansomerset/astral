# AST-1606 — meteorite_email is not recognizing bound messages

<!-- linear-archive: AST-1606 archived 2026-09-22 -->

## Linear archive (AST-1606)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1606/meteorite-email-is-not-recognizing-bound-messages  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1558; related: AST-1560; related: AST-1555; related: AST-1559

### Description

## As-is

`meteorite_email` reports no available messages for a candidate who should have bound inbox mail. On Manage Email, Land Meteorite surfaces an error, but nothing appears in Execution History to inspect what failed.

## To-be

Candidate-bound inbox mail is visible to the `meteorite_email` / `check_inbox` path (Avail and/or a Click run actually sees the messages). Manage Email Land either succeeds into staging ingress, or on failure leaves a reviewable execution/error trail so the failure is diagnosable without guessing.

## Proposed steps

1. Confirm whether "no available messages" is the Scheduled Actions Avail count for `meteorite_email` ([AST-1559](https://linear.app/astralcareermatch/issue/AST-1559/check-inbox-monitoring-log-meteorite-ingress-staging-table) noted AUTO Avail may still be deferred) versus `check_inbox` / `fetch_candidate_email` returning an empty list for that candidate's aliases.
2. Trace alias resolution (`email_aliases_for_candidate`) and `fetch_candidate_email` against the live Gmail row that Manage Email can still list — fix the miss if aliases/filter exclude a message that should bind.
3. Reproduce Manage Email Land with a candidate filter selected; capture the API error body from `POST` land (`api_inbox` → `stage_meteorite`) and whether the UI drops it.
4. If Land correctly fails but never writes Execution History because it bypasses the dispatcher, either wire a durable error surface (toast/detail + ledger row) or document that Manage Email Land is not a dispatch run and fix the user-visible error path instead.
5. Re-test: Avail/Click sees the bound message; Land either lands staging rows or shows a concrete, reviewable failure.

## Component scope

* `src/core/inbox.py` — modified: `fetch_candidate_email` (and related list/filter) is what both mailbox and Manage Email use to decide which messages exist for a candidate.
* `src/core/candidate.py` — modified if alias lookup is wrong: `email_aliases_for_candidate` feeds the fetch.
* `src/core/meteorite.py` — modified: `check_inbox` (mailbox runner behind task_key `meteorite_email`) and/or `stage_meteorite` (Manage Email Land entry).
* `src/core/dispatcher.py` — modified only if Avail / `available_count` for the `meteorite_email` mailbox shell is wrong or never computed for this task shape.
* `src/ui/api/api_inbox.py` — modified: Manage Email list + Land endpoints; error payload and any missing failure recording.
* `src/ui/frontend/src/pages/AdminManageEmail.tsx` — modified: how Land errors are shown when the API returns failure without an execution-history row.

## Technical scope

* `src/core/inbox.py` — modified function(s) on the candidate-scoped fetch/filter path so bound messages are not dropped before mailbox or Manage Email can act on them.
* `src/core/candidate.py` — modified function for alias resolution if the candidate's From/To addresses are incomplete or mismatched against the live message.
* `src/core/meteorite.py` — modified `check_inbox` and/or `stage_meteorite` so empty-fetch vs classify/land failure is distinguishable and Land failures carry a usable error string.
* `src/core/dispatcher.py` — modified Avail/eligibility path for `meteorite_email` only if the shell still reports zero when fetch would return messages (or if Click is blocked by a stale count).
* `src/ui/api/api_inbox.py` — modified Land handler to return and optionally persist a clear error when `stage_meteorite` fails, instead of a bare UI "error" with no ledger trail.
* `src/ui/frontend/src/pages/AdminManageEmail.tsx` — modified Land error handling to surface the API error (and/or deep-link to whatever log row exists).

## Ancestor candidates

- [X] [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) — Meteorite ingress: staging table + inbox/meteorite consolidation (parent epic for both mailbox and Manage Email land paths)
- [ ] [AST-1559](https://linear.app/astralcareermatch/issue/AST-1559/check-inbox-monitoring-log-meteorite-ingress-staging-table) — check_inbox + monitoring; dispatcher `meteorite_email` → `check_inbox` (Avail / "no available messages" on the mailbox task)
- [ ] [AST-1558](https://linear.app/astralcareermatch/issue/AST-1558/inbox-candidate-verbs-manage-email-filter-meteorite-ingress-staging) — inbox candidate verbs + Manage Email filter; Land requires `candidate_id` → `stage_meteorite` (Manage Email land error surface)
- [ ] [AST-1560](https://linear.app/astralcareermatch/issue/AST-1560/stage-scrape-land-transitions-meteorite-ingress-staging-table) — stage/scrape/land table transitions (if Land is expected to drive row transitions beyond classify-only `stage_meteorite`)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
