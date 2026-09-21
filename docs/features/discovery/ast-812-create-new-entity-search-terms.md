# AST-812 — Create new entity: search_terms

<!-- linear-archive: AST-812 archived 2026-08-19 -->

## Linear archive (AST-812)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-812/create-new-entity-search-terms  
**Status at archive:** Archive  
**Project:** Astral Discovery  
**Assignee:** susan  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## inflow_discovery — specialized **candidate** entity code (inventory)

 1. `src/utils/config.py` — `_dispatch_entity_type_for_task_key` maps `inflow_discovery` → `"candidate"`; `_dispatch_trigger_state_for_task_key` → `LIVE_PROMPTS`; `_dispatch_sort_by_for` candidate branch; `INFLOW_CONFIG["discovery"]`; `dispatch_task_admin_defaults`; `DISPATCH_SCHEDULABLE_TASK_KEYS`; `COMPANY_SEARCH_TERMS` token registry (candidate-sourced, table overlay at runtime).
    1. We would effectively replace "candidate" for "search_terms", right?
 2. `src/data/database.py` — `describe_candidate_inflow_discovery_eligibility`, `count_candidate_inflow_discovery_eligible`; `count_eligible_for_dispatch_task` candidate/`inflow_discovery` branch; `company_search_terms` table DDL/CRUD; stale-term queries; `last_scan_at` updates; artifact reconcile/migrate.
    1. This seems absolutely out of pattern, can we cleanly remove this logic specific for inflow_discovery?
 3. `src/core/dispatcher.py` — `_dispatch_entity_identifier` candidate branch; `_run_unified` candidate path (`entities = [ctx]`, no DB batch claim); no company/job batch clear for candidate; `_run_dispatch_loop` `inflow_discovery` eligibility debug; available count via `count_eligible_for_dispatch_task`.
    1. As far as I know, we don't have any "scheduled" candidate entity work, but do we need candidate entity in place for ui-driven tasks?
 4. `src/core/consult.py` — `entity_type == "candidate"` → `run_inflow_discovery_batch`; `vet_inflow_discovery` resolves candidate from ctx.
    1. does consult have run_<taskname>_batch for other tasks?  Is there a reason that's needed?
 5. `src/core/roster.py` — `run_inflow_discovery_batch` (CSE over stale terms, dedupe, record hits); `record_inflow_discovery_hit`; `vet_inflow_discovery_company`.
    1. Hmm, this looks duplicated from consult, which doesn't make sense.  If anything, gazer should have "inflow_discovery(<search term>)" that then calls roster to ingest the findings.
 6. `src/core/candidate.py` — `company_search_terms_*` read/write/sync; artifact reconcile on read; `apply_company_search_terms_save`.
    1. I actually think that company_search_terms should be owned by roster.py, not candidate. The shape of the candidate foreign key on search_terms matches that on company, and one feeds the other.  In fact, we *should* add a nullable foreign key from company to the search_terms table to identify the origin.
 7. `src/core/agent.py` — `COMPANY_SEARCH_TERMS` token overlay from table via `company_search_terms_joined_text`.
    1. Wait, why is agent worrying about company search terms?  I thought agent was just taking prompts and passing back to the calling core component? This makes me wonder about the handful of core components we have that sort of straddle between "owning business logic" and "glorified util/external component" and how well we are differentiating them in the architecture.
 8. `src/ui/api/api_admin.py` — `_dispatch_task_key_trigger_error` validates `inflow_discovery` against `CANDIDATE_STATES`; available counts; `state_options` candidate array.
    1. I think this can just come straight out, right?  why on earth is api_admin doing validation?  It should just be getting it's content from core components…
 9. `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — Input State options when `entity_type === "candidate"`.
    1. Let's take this out for now.
10. `src/ui/api/api_candidate.py` — table-backed GET/PUT/sync (feeds term table discovery reads).
    1. This is okay as is, I think.
11. `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` — Artifacts editor for term text.
    1. As is is fine, I think
12. `src/core/intake.py` — build path `sync_company_search_terms_from_text`.
    1. I don't think this is part of intake, exactly.  It should probably be in roster.py because roster can just harvest the updated content from candidate_data to sync the table contents in company_search_terms.

## Components to update for `search_terms` entity (bound to `candidate_search_terms` / current `company_search_terms` table)

 1. `src/utils/config.py` — add `search_terms` to `ENTITY_TYPES`; state/eligibility registry; remap `_dispatch_entity_type_for_task_key("inflow_discovery")`; `INFLOW_CONFIG`; admin defaults; token resolution if entity grain changes.
    1. What would be the details of the state/eligibility registry?
    2. Why is INFLOW_CONFIG a thing?  What do we have in there?
 2. `src/data/database.py` — entity identity on term table (rename/migrate TBD); batch claim/release for search-term rows; eligibility by term entity; `count_eligible_for_dispatch_task` / ledger / `agent_data` `entity_type`.
    1. Nope, just use company_search_terms, per above.  We do not have to add entity_type for agent_data, but if it's more complex to omit it, then let it be included in the validation.
 3. `src/core/dispatcher.py` — claim search-term entities from DB (replace candidate `entities = [ctx]`); per-term debug identifiers; batch clear lifecycle; loop available-count per term.
    1. Yes
 4. `src/core/consult.py` — `entity_type == "search_terms"` path (likely one CSE per claimed term).
    1. Move to roster, not consult.  search_terms are gazer/roster-only, none of them get sent to an agent after initial list generation.
 5. `src/core/roster.py` — refactor `run_inflow_discovery_batch` to term-scoped execution; keep hit record / company vet paths coherent.
    1. I just remembered that gazer uses playwright, and this is using google cse, so I think roster IS the right home for inflow, but yes, not by batch, only by search term.  A single search term results might return 100 URLs, all of which would be potentially added to the company table.  I wish we had a pattern for this….  WAIT, Don't we?  OMG.
    2. a single search term is like a job site url.  Gazer runs and gets the jobs from the playwright content, then calls tracker with the whole batch to dedupe and filter by regex for ingest. Let's use THAT pattern here.  Let's set up a config-driven global list of regex filter AGAINST (e.g. "wikipedia" or "news" or whatever), then send those we can't auto-filter to company to be vetted by AI in the next task.  Roster can own both tasks, but the dedupe/autofilter pattern should serve us here.  The key difference is that the auto-filter pattern for discovery is NOT candidate-specific, but config-driven for all links returned.
 6. `src/core/candidate.py` — parent CRUD/sync decoupled from dispatch eligibility; boundary with search_terms helpers if extracted.
 7. `src/core/agent.py` — token/build context for single term vs whole-candidate list.
 8. `src/ui/api/api_admin.py` — validation, `state_options`, available count for `search_terms` rows.
 9. `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — `search_terms` entity branch in edit modal.
10. `src/ui/api/api_candidate.py` + `ArtifactsCompanySearchTerms.tsx` — table edits consistent with dispatch claims / staleness.
11. `src/core/intake.py` — intake build seeds terms without dispatch regression.
12. **Tests** — dispatcher, roster, consult, database company_search_terms, dispatch_tasks, api_admin, config, AdminScheduledActions + Artifacts tests (AST-504/524/525/526/802 areas).

---

## Original brief

Begin in this Discussion phase by making in the description of this issue an enumerated list of components where inflow_discovery has specialized code written to handle it as a "candidate" entity.

Then, SEPARATELY in the description, make an enumerated list of components we would need to update to regard "search_terms" as an entity (bound to "candidate_search_terms" in astral.db).

This will be an iterative discussion flow, but I will add on more content to the original brief section as we get closer to the complete solution definition.

Relatedly:
Search terms are a more significant cornerstone of the data than I originally expected.

We need that relationship established and monitored. Search terms that consistently result in duds need metrics.

For now, I think we can just pass the search string used as a new text column in company. We can refactor later.

### Comments

#### chuckles — 2026-06-26T01:03:18.644Z
[check-linear] Discussion — two inventory lists only; structured define removed (@susan)

#### susan — 2026-06-26T00:59:09.625Z
@chuckles This is Discussion phase.  You are prematurely defining the ticket.  Just create the two requested lists as described in the brief.'

#### chuckles — 2026-06-26T00:56:57.430Z
@susan

1. **Table name:** Brief says **`candidate_search_terms`**; shipped schema is **`company_search_terms`**. Rename/migrate, keep internal name with external alias, or new table?
2. **Entity identity:** Is one dispatch entity = one `(candidate_id, search_term)` row, or a surrogate PK with `search_term` as display id?
3. **State model:** Per-term **`last_scan_at`** staleness only (no row state column), or a new state registry (e.g. STALE / IN_FLIGHT / SCANNED)?
4. **Parent candidate gate:** Does `inflow_discovery` still require the parent candidate at **`LIVE_PROMPTS`**, or does eligibility move entirely to the term entity?
5. **`vet_inflow_discovery`:** Confirm unchanged as **company**-entity dispatch on NEW with blurb — out of scope for term-entity claim?
6. **`craft_company_search_terms`:** Stays candidate-scoped craft task, or split per-term / per-entity?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
