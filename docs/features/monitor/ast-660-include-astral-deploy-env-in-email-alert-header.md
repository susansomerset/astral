# AST-660 — Include ASTRAL_DEPLOY_ENV in email alert header

<!-- linear-archive: AST-660 archived 2026-06-23 -->

## Linear archive (AST-660)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-660/include-astral-deploy-env-in-email-alert-header  
**Status at archive:** Done  
**Project:** Astral Monitor  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

AUTO dispatch error alert emails (AST-344) use a hardcoded `[Astral]` subject prefix, so Susan cannot tell which deployment sent the alert when multiple environments are running (local, staging, region labels, etc.). `ASTRAL_DEPLOY_ENV` already identifies the deployment elsewhere in the product. Susan also needs the owning candidate's last name in the subject so inbox triage can distinguish `[local/Somerset]` from `[staging/Jones]` at a glance.

## Functional scope

* **Deploy label in subject prefix:** AUTO error alert email subjects replace the literal `Astral` with the deploy environment label in square brackets — same stripped, non-empty `ASTRAL_DEPLOY_ENV` value used for the admin nav footer (AST-646 / AST-651), any non-empty string after trim, no allowlist.
* **Candidate last name in subject prefix:** AUTO error alert subjects use `[{deploy_label}/{last_name}]` — e.g. `[local/Somerset] evaluate_jd INTERRUPTED: 1 error(s) / 0 processed | {batch_id}`. Resolve the candidate for the failing run (dispatch task's candidate and/or the processed entity's owning candidate — job, company, board search, and candidate entity types all trace to a candidate).
* **Last name source:** Use the candidate profile last name for the resolved candidate.
* **Scope limited to AUTO error alerts:** Only the subject line built by `auto_run_error` when the dispatcher reports errors on an AUTO task run. Email body, recipient, send conditions, and Gmail delivery are unchanged. UI-initiated errors are out of scope for this ticket.

## Boundaries

* Does not add new alert types, change when alerts fire, or modify email body formatting.
* Does not change subjects on UI-initiated runs or any email path outside AUTO dispatch error alerts.
* Does not introduce a new environment allowlist or duplicate deploy-env resolution logic.
* When `ASTRAL_DEPLOY_ENV` is unset or whitespace-only, deploy label in the bracket falls back to `Astral` (current subject shape).
* When candidate last name cannot be resolved from profile data, omit the `/LastName` segment and use `[{deploy_label}]` only — do not invent a placeholder.
* Does not affect UI, React, or debug logging contracts.

## Acceptance criteria

1. With `ASTRAL_DEPLOY_ENV=local`, an AUTO error alert subject begins with `[local/{LastName}]` for the owning candidate, followed by the existing `{task_key} {final_status}: …` summary and batch id suffix.
2. With `ASTRAL_DEPLOY_ENV=eu-west`, subject prefix is `[eu-west/{LastName}]` (raw deploy label, case preserved).
3. With `ASTRAL_DEPLOY_ENV` unset or whitespace-only, deploy label in the bracket is `Astral`; candidate last name suffix still applies when resolvable.
4. Candidate last name appears for AUTO errors across entity types (job, company, board_search, candidate) by resolving the owning candidate for the run.
5. Email body content and alert trigger conditions (AUTO mode, `total_errors > 0`) are unchanged from AST-344.
6. Monitor component tests cover deploy-label prefix, candidate last name suffix, and fallback when deploy env or last name is unavailable.

## Dependencies and blockers

None. Builds on completed AST-344 (error alerts) and existing `ASTRAL_DEPLOY_ENV` resolution (AST-646 / AST-651).

## Open questions

None.

---

## Original brief

Please change: 
[Astral] evaluate_jd INTERRUPTED: 1 error(s) / 0 processed | evaluate_jd-c40f17ed-7d2c-4255-8949-599374636767

to 
[<ASTRAL_DEPLOY_ENV>] evaluate_jd INTERRUPTED: 1 error(s) / 0 processed | evaluate_jd-c40f17ed-7d2c-4255-8949-599374636767

### Comments

#### chuckles — 2026-06-15T06:06:06.695Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-660 (parent) | ftr/AST-660-include-astral-deploy-env-in-email-alert-header |
| AST-667 | sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject |

**Epic worktree:** `astral-AST-660/` — one active sub checked out at a time.

**Parent:** AST-660

— Chuckles

#### chuckles — 2026-06-15T02:07:38.391Z
@susan Open questions:

1. Which AUTO error runs count as "specific to a candidate" vs not? Every dispatch task row carries a `candidate_id`, but entity types differ (`job`, `company`, `board_search`, `candidate`). Should company-entity roster scan errors use `[env/LastName]` or `[env]` only?

— Chuckles

#### susan — 2026-06-15T02:05:49.590Z
Please also indicate the candidate if relevant \[<ASTRAL_DEPLOY_ENV>/<candidate_last_name>\] or just \[<ASTRAL_DEPLOYE_ENV>\] if the error is not specific to a candidate.

---

_Implementation detail may live in git history on `origin/dev`._
