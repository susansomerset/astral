# AST-1804 — fetch type avail counts appear not to include _RETRY records

<!-- linear-archive: AST-1804 archived 2026-10-07 -->

## Linear archive (AST-1804)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1804/fetch-type-avail-counts-appear-not-to-include-retry-records  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

# fetch type avail counts appear not to include \_RETRY records

**Original brief:** This shouldnt be this hard, Its not complicated. include retry records with their base states.

**Susan (2026-09-26, binding):** There should be NO explicit `_RETRY` state in config. It is an implicit substate for exactly this purpose. Always query for `_RETRY` when claiming a batch with the base state, but don't validate the full RETRY string.

## As-is

`_RETRY` states are modelled as explicit registry entries: 13 keys in `JOB_STATES` (`VALID_TITLE_RETRY`, `NEW_RETRY`, `JD_READY_RETRY`, `PASSED_JD_RETRY`, `PASSED_DO_RETRY`, `CULTURE_READY_RETRY`, `PASSED_LIKE_RETRY`, and the six `METEORITE_*_RETRY`), 3 in `COMPANY_STATES` (`WEBSITE_FOUND_RETRY`, `JOBLIST_IDENTIFIED_RETRY`, `PREFILTER_PASSED_RETRY`), and 2 in `CANDIDATE_STATES` (`REQUESTED_RESUME_RETRY`, `REQUESTED_ARTIFACTS_RETRY`). Many registry entries also carry `retry_state` fields and `prior_states` lists naming them. Transition validators (`transition_job_state`, `transition_company_state`, `transition_candidate_state`) reject any `to_state` not in the registry. So a base state only gets a retry substate if someone hand-registered one, and fetch-family bases such as `PASSED_JOBLIST` and `PASSED_GET` have none. Claim/count pairing is already suffix-always ([AST-1798](https://linear.app/astralcareermatch/issue/AST-1798/fix-strict-retry-suffix-claim-pairing-no-retry-state-companion)), and claim helpers skip registry validation for `states=` ([AST-1800](https://linear.app/astralcareermatch/issue/AST-1800/dispatcher-performing-data-validation)).

## To-be

`_RETRY` is an implicit substate of every registered base state. No `*_RETRY` key or `*_RETRY` `retry_state` value appears in any entity-state registry. Anywhere a state string is validated (job/company/candidate transitions, claim helpers, admin dispatch-row trigger validation), `{base}_RETRY` is accepted whenever `{base}` is a registered state, without checking the full `_RETRY` string. Moving between a base and its own `_RETRY` substate is always allowed. A `_RETRY` substate can go wherever its base can go. Claim and Available for a primary trigger keep querying `[base, base_RETRY]`, as they already do. Routing a failure to a retry holding state is spelled `{base}_RETRY` (derived, not configured).

## Proposed steps

1. Add one implicit-retry helper in config (for example, "is this state `{registered base}_RETRY`" and "base of a retry state") as the single place that knows the suffix rule.
2. Make every state validator accept `{base}_RETRY` via that helper: `transition_job_state` / `_job_state_matches_prior`, `transition_company_state`, `transition_candidate_state` / `_candidate_state_allowed`, claim helpers, and admin dispatch-row trigger validation. Priors for a `_RETRY` target are the base plus the base's own priors. A `_RETRY` source matches any `prior_states` entry that names its base.
3. Delete the 18 explicit `*_RETRY` registry keys. Rewrite `retry_state` fields that name them as derived (`{base}_RETRY`, or drop the field where a helper derives it). Strip `*_RETRY` names out of `prior_states` lists, where the implicit rule now covers them. Fix module-level asserts that required registered retry keys.
4. Replace hard-coded `*_RETRY` literals outside config (the consult legacy input-state→task map, roster/gazer branches) with the base-derived form, so behaviour is unchanged for the states that exist today.
5. Leave AST-892 second-strike ownership of `WEBSITE_FOUND_RETRY` rows that have homepage text as-is: it is ownership, not registry.

## Component scope

* `src/utils/config.py` — modified — remove explicit `*_RETRY` keys from `JOB_STATES` / `COMPANY_STATES` / `CANDIDATE_STATES`; rewrite `retry_state` fields and `prior_states` entries that name them; add the implicit-retry helper; update module-level asserts; `dispatch_claim_states` stays suffix-always.
* `src/core/tracker.py` — modified — `transition_job_state` / `_job_state_matches_prior` / job-state validation accept `{base}_RETRY` via the helper.
* `src/core/roster.py` — modified — `transition_company_state` validation accepts `{base}_RETRY`; literal `WEBSITE_FOUND_RETRY` / `JOBLIST_IDENTIFIED_RETRY` branches keep working off the derived name.
* `src/core/candidate.py` — modified — `transition_candidate_state`, `_candidate_state_allowed`, and the candidate claim/trigger checks accept `{base}_RETRY`.
* `src/core/consult.py` — modified — legacy `_INPUT_STATE_TO_TASK` `*_RETRY` entries and other `*_RETRY` literals resolve through the base.
* `src/core/gazer.py` — modified only if it transitions to a literal `*_RETRY` that must now be derived. **AST-1810:** modified — `fetch_website_batch` drops its AST-892 second-strike skip (the `skipped` count stays, always 0).
* `src/ui/api/api_admin.py` — modified — dispatch-row create/update trigger validation accepts `{base}_RETRY` for a registered base; `state_options` lists bases only.
* `src/data/database.py` — verify only — claim/count already uses `_state_in_sql` with no registry validation; change only if a path still rejects an unregistered `_RETRY`. **AST-1810:** modified — drop the AST-892 `homepage_text` exclusion from `count_companies_eligible_for_fetch_website` and the company batch claim (`exclude_prefilter_second_strike`), so fetch_website counts and claims every `WEBSITE_FOUND_RETRY` row.
* `src/core/dispatcher.py` — verify only — claim resolution already uses `dispatch_claim_states`. **AST-1810:** modified — stop passing `exclude_prefilter_second_strike` for fetch_website (and `src/core/roster.py` claim passthrough to match).
* `src/ui/api/api_system.py` — modified — `_progress_rank` resolves a `{base}_RETRY` candidate state through its base, so purging the candidate retry keys doesn't drop nav rank to −1 ([AST-1806](https://linear.app/astralcareermatch/issue/AST-1806/fix-purge-explicit-retry-states-from-entity-state-registries) scope-gate).

## Technical scope

* `src/utils/config.py` — new function(s): the implicit-retry helper (retry-of-base check plus base resolver). Modified data: the three entity-state registries lose their `*_RETRY` keys, and `retry_state` / `prior_states` stop naming them. Modified asserts, so config still loads.
* `src/core/tracker.py` — modified functions: `transition_job_state`, `_job_state_matches_prior`, and any `validate_value(_JOB_STATE_LIST, …)` call on a transition target, so they accept implicit retries.
* `src/core/roster.py` — modified function: `transition_company_state` (and the claim-helper registry check, if it is still single-state-bound), for the same reason.
* `src/core/candidate.py` — modified functions: `transition_candidate_state`, `_candidate_state_allowed`, and the bare-trigger registry check, for the same reason.
* `src/core/consult.py` — modified map/branches: the legacy input-state→task map and literal `*_RETRY` checks derive from the base, so removing the registry keys doesn't change routing.
* `src/ui/api/api_admin.py` — modified function(s): dispatch-task trigger validation plus `state_options`, so admin never needs an explicit `_RETRY` key.
* `src/ui/api/api_system.py` — modified function: `_progress_rank` looks up rank via the registered base, because the explicit retry keys that carried rank are deleted.
* `src/data/database.py` / `src/core/dispatcher.py` / `src/core/roster.py` / `src/utils/config.py` / `src/core/gazer.py` (AST-1810) — modified functions: remove the AST-892 second-strike exclusion from the fetch_website count and claim (and the now-unused filter helper/flag), because Susan ruled `_RETRY` rows are included whatever `homepage_text` holds.
* Exact helper names, and whether priors are resolved inside the helper or at each call site, are plan-fix's call under statute.

## Ancestor candidates

- [ ] AST-641 — Union claim and count for primary + `_RETRY` trigger states (Auto retry) — shipped home of Available/claim primary+companion union via `dispatch_claim_states` / `count_eligible_for_dispatch_task`
- [ ] [AST-1798](https://linear.app/astralcareermatch/issue/AST-1798/fix-strict-retry-suffix-claim-pairing-no-retry-state-companion) (mini-parent [AST-1797](https://linear.app/astralcareermatch/issue/AST-1797/retry-suffix-issues)) — strict `_RETRY` suffix claim pairing on the AST-641 feature doc — recent rewrite of `dispatch_claim_states`; plausible if pairing/count regressed for fetch-\* after that land
- [ ] AST-849 — Retire consult chain dispatch claim — introduced `dispatch_chain_claim_states_for_row` as the Available/claim resolver for chain job triggers, which can replace the AST-641 two-state list and drop `{ts}_RETRY`

### Comments

#### chuckles — 2026-09-27T04:12:53.929Z
[fix-intake] finish-up blocked on a GitHub CLI bug, so AST-1804 is parked at User Testing with PR [#162](https://github.com/susansomerset/astral/pull/162) open (@susan)

AST-1810 is merged into the ftr, all five children are at User Testing or Done, and #162 (ftr → dev) merges cleanly. The land never started. `finish-up-land.sh` first refreshes the open PR with `gh pr edit`, and gh 2.46 fails that call on GitHub's retired "Projects (classic)" API. Nothing landed and no refs were deleted.

Pick one:
1. Merge #162 on GitHub yourself, then set PR Ready and assign Chuckles so finish-up does the cleanup.
2. OK a one-call fix in `create-dev-pr.py`: update the PR with `gh api -X PATCH …/pulls/N` instead of `gh pr edit`. Then set PR Ready and assign Chuckles.
3. Upgrade `gh` on this host (newer versions don't query classic projects). Then set PR Ready and assign Chuckles.

#### chuckles — 2026-09-27T00:54:32.359Z
[fix-intake] filed AST-1810 at Discussion (assigned to you): drop the AST-892 homepage_text exclusion so fetch_website counts and claims every WEBSITE_FOUND_RETRY row. To release it, check the diagnosis and assign it to Chuckles.

#### susan — 2026-09-27T00:52:42.570Z
@chuckles The deliberate exception is a bug.  Please remove the exception and include the RETRY rows regardless of homepage text.

#### chuckles — 2026-09-27T00:28:07.086Z
[check-linear] answered — yes, the fix is on `main`. It went in with the dev→main merge at 00:22 UTC (#156), five minutes before your comment, so production may not have been redeployed yet when you looked.

On the current code, every Avail count uses the same states as the claim: the base state plus `{base}_RETRY`.

One deliberate exception: for **fetch_website**, `WEBSITE_FOUND_RETRY` rows that already have `homepage_text` are left out of both the count and the claim. Those rows belong to the prefilter second-strike retry (AST-892), not to fetch_website.

If the count is still short after the deploy is live, tell me which fetch task (its trigger state) and what number you expected. That tells me whether it's this exception or a new bug. @susan

#### susan — 2026-09-27T00:27:19.938Z
@chuckles confirm that this fix has been merged into main, please?  It's still an issue from what I can see.

#### chuckles — 2026-09-26T22:07:37.447Z
AST-1805 estimate 5→3 — plan-fix confirmed 8 pts; split: AST-1805 validators accept implicit {base}_RETRY, AST-1806 purges explicit _RETRY registry keys (blocked by AST-1805).

#### susan — 2026-09-26T20:56:16.522Z
There should be NO explicit \_RETRY state in config.  It is an implicit substate for exactly this purpose.  Always query for \_RETRY when claiming a batch with the base state, but don't validate the full RETRY string.

#### chuckles — 2026-09-26T20:54:20.746Z
@susan — AST-1805 plan-fix stopped before planning because the bug as written doesn't reproduce on current code. Ada's findings are on [AST-1805](https://linear.app/astralcareermatch/issue/AST-1805).

**What current code does** (`origin/dev` = `origin/main` tip): for a primary row, Available and claim both use `[trigger, trigger_RETRY]`. With one entity in each state, each fetch-* primary counts 2 and each retry-only row counts 1.

**Why "the fix predates your observation" doesn't hold:** AST-1798 (suffix-always pairing) reached `main` Sep 25 at 18:04 UTC, and you filed this Sep 26 at 19:44 UTC. If prod redeployed from main after that, what you saw was already on fixed code, so something else is going on.

**What could still look like missing retries:**
- `fetch_jd` (`PASSED_JOBLIST`) and `fetch_culture_pages` (`PASSED_GET`) have no retry state in config. `PASSED_JOBLIST_RETRY` and `PASSED_GET_RETRY` aren't registered and nothing routes jobs into them. Their failures go to `JD_SCRAPE_FAIL*` / `BOT_BLOCKED` / `NEED_CULTURE_CONTENT` / `NO_CULTURE_LINKS`, which are separate states rather than `_RETRY` records.
- `fetch_website` counts `WEBSITE_FOUND_RETRY` but skips rows that have homepage text, because the prefilter second strike owns those (AST-892).
- The `PASSED_*` and `PREFILTER_PASSED` primaries are score-gated, and the floor also applies to their `_RETRY` records. A retry record with a missing or low score drops out.

Neither of us can reach the prod DB from this box.

**Need from you (reply here, then reassign AST-1804 to Chuckles):**
1. Which fetch row(s), and which states the missing records are actually sitting in.
2. Or: the counts look right in prod now, and I cancel AST-1804.
3. Or: re-scope to a specific change, for example counting the fetch failure states (`JD_SCRAPE_FAIL*`, `NEED_CULTURE_CONTENT`, …) as that fetch row's retries, or not applying the score floor to `_RETRY` records.

AST-1805 stays Todo with Ada; nothing is committed on the branches.

---

_Implementation detail may live in git history on `origin/dev`._
