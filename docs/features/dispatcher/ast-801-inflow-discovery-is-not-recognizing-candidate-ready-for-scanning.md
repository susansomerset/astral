# AST-801 — Inflow discovery is not recognizing candidate ready for scanning

<!-- linear-archive: AST-801 archived 2026-07-22 -->

## Linear archive (AST-801)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-801/inflow-discovery-is-not-recognizing-candidate-ready-for-scanning  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan's **inflow_discovery** repro (**somerset**, **LIVE_PROMPTS**, fourteen saved company search terms, **available_count=0**) exposed a deeper design mistake: we invented a **candidate-entity** dispatch path and duplicated cadence in both `dispatch_task.freq_hrs` and `INFLOW_CONFIG`, instead of running discovery through the same dispatcher pattern as **job** and **company** rows. The `company_search_terms` table already exists precisely so each saved term can be a first-class dispatch entity. This epic **reverts** the special-case inflow scheduling pattern (analogous to the **BUILD_ARTIFACTS** flattening revert), introduces `search_term` as a standard dispatch entity type, and wires **inflow_discovery** to claim stale search-term rows through the unified batch runner so Scheduled Actions **Available** and manual **Run** behave like every other dispatch task.

## Functional scope

* **Revert the candidate-entity inflow dispatch pattern** shipped under **AST-801/802/805**: remove dispatcher and admin paths that treat **inflow_discovery** as `entity_type=candidate`, including eligibility that counts the whole candidate instead of individual search-term rows.
* **Add** `search_term` **to the product's dispatch entity model** alongside **job**, **company**, and **candidate**. Each row in the existing `company_search_terms` table is the dispatch unit for inflow discovery (Susan: entity type is **search_term**, not candidate).
* **Unified batch claim, count, and run** for **inflow_discovery**: the dispatcher claims a batch of stale search-term rows using the same mechanics as company batch tasks (**freq_hrs** on the `dispatch_task` row, `trigger_state` from a search-term state registry, `sort_by`, `batch_size`, `score_floor` where applicable). No parallel INFLOW-specific dispatch scheduling block in config.
* **Parent candidate gate without candidate entity dispatch**: a search term is eligible only when its owning candidate is in **LIVE_PROMPTS** (or whatever trigger Susan confirms). That gate is a **filter on search_term claim/count**, not a separate candidate-entity dispatch branch.
* **Cadence single source of truth**: scan interval / dispatch frequency lives on the `dispatch_task` row (`freq_hrs`) and per-row `last_scan_at` staleness — not duplicated literals in an INFLOW scheduling config block. Remove INFLOW-specific **dispatch trigger**, **dispatch frequency**, and **record-fetch** configuration; keep only non-scheduling task behavior config (CSE limits, vet pass/fail states, task keys) if still needed outside dispatch rows.
* **Admin Scheduled Actions parity**: create/edit/validate **inflow_discovery** rows with `entity_type=search_term`; state options, trigger validation, and **Available** count use the search-term registry the same way job and company rows do today.
* **Roster inflow execution**: **inflow_discovery** batch processing consumes claimed search-term entities (one CSE query per term, bump `last_scan_at` on success) through the standard consult/dispatcher path — not a one-off candidate context shortcut.
* **Debug traceability**: when **inflow_discovery** skips or claims zero rows with `debug=True`, logs state the eligibility reason per the backend debug contract (**AST-538**): parent candidate state, zero table rows, zero stale terms, etc.

### New entity type rollout — components to touch (discussion checklist)

Susan asked for a step-by-step component list for adding `search_term`. Dispatch should treat this like prior entity additions (**company**, **job**). Expected touch surfaces:

 1. **Config registry** — extend `ENTITY_TYPES`; add `SEARCH_TERM_STATES` (or equivalent) with batch criteria (`sort_by`, staleness via `last_scan_at`, optional `scan_interval_hours` default); wire `dispatch_task_admin_defaults` / schedulable task key maps so **inflow_discovery** derives `entity_type=search_term` and a concrete `trigger_state`; remove INFLOW dispatch scheduling entries from config.
 2. **Data layer — schema inventory** — confirm `company_search_terms` (or renamed search-term table) is the entity store; document row identity (**candidate_id + search_term**), `last_scan_at`, and any state column if Susan chooses explicit states over staleness-only.
 3. **Data layer — claim / count / release** — implement `count_eligible_for_dispatch_task`, batch claim, and batch clear for `search_term` parallel to job/company helpers; apply parent-candidate **LIVE_PROMPTS** join filter; honor `freq_hrs` from the dispatch row for staleness.
 4. **Core — dispatcher unified runner** — add `search_term` branch in claim, entity identifier, batch clear, and consult handoff; delete `entity_type=candidate` shortcut used for inflow discovery.
 5. **Core — roster / inflow batch** — adapt **inflow_discovery** execution to accept search-term entity rows instead of candidate context; preserve CSE + vet handoff behavior.
 6. **Core — consult / agent** — ensure `run_consult_task` (or successor) accepts `search_term` entity type where inflow tasks need consult routing; token overlay for **COMPANY_SEARCH_TERMS** remains candidate-scoped.
 7. **UI API — admin dispatch** — extend `dispatch_entity_state_registry`, `_dispatch_task_key_trigger_error`, `GET …/state_options`, eligible-count enrichment, and PUT/POST validation for `search_term`.
 8. **UI — Scheduled Actions** — Input State options and form defaults when `entity_type === "search_term"`; remove candidate-state picker for **inflow_discovery**.
 9. **Bootstrap / seed rows** — migrate existing **inflow_discovery** `dispatch_task` rows to `entity_type=search_term` with correct `trigger_state` and `freq_hrs`; backfill `freq_hrs` from retired INFLOW dispatch literals where rows are null.
10. **Artifacts / candidate save path** — keep table sync on save and Artifacts GET ( **AST-524/526** ); no return to artifact-only eligibility. Reconcile-at-count hacks from [AST-802](https://linear.app/astralcareermatch/issue/AST-802/inflow-discovery-eligibility-when-saved-search-terms-present-inflow) are superseded if search-term batch claim reads the table directly — revert those if redundant after the unified path lands.
11. **Tests (Betty)** — component coverage for search-term claim/count, admin validation, and Susan's **somerset** repro (**Available > 0**, manual **Run** proceeds).

## Boundaries

* Does **not** change CSE query parameters, discovery/vet task split (**AST-775/776**), or vet company-ingest semantics unless a separate ticket says so.
* Does **not** add new dispatch task keys beyond retargeting **inflow_discovery** (and existing inflow resolve/vet keys stay **company**-entity unless Susan directs otherwise in open questions).
* Does **not** remove the `company_search_terms` table or Artifacts save UX — only changes how dispatch sees those rows.
* Does **not** reintroduce `dispatch_task.last_run_at` as the per-term staleness signal (**AST-525** `last_scan_at` on each term row remains authoritative).
* Must not break job **BUILD_ARTIFACTS CHAIN**, company roster dispatch, or scored job consult batching.

## Acceptance criteria

1. Susan's repro (**somerset**, **LIVE_PROMPTS**, fourteen saved terms on local): **inflow_discovery** Scheduled Actions row shows **Available > 0** and manual **Run** executes discovery instead of **Skipping … 0 available (min_count=1)**.
2. The **inflow_discovery** `dispatch_task` row uses `entity_type=search_term` (not **candidate**); admin create/edit validates search-term trigger states and shows correct Input State options.
3. No INFLOW-specific **dispatch scheduling** config remains (no duplicate `dispatch_trigger_state` / `dispatch_freq_hrs` / dispatch record-fetch block for scheduling); `freq_hrs` on the dispatch row is the sole dispatch cadence knob alongside per-term `last_scan_at`.
4. Dispatcher claim/count for **inflow_discovery** follows the same batch pattern as company tasks (no `entities = [ctx]` candidate shortcut for this task).
5. With `debug=True` and zero available at dispatch time, logs include an explicit eligibility-reason line per **AST-538**.
6. Component tests cover search-term eligibility count and at least one happy-path batch claim for stale terms.

## Dependencies and blockers

* [AST-775](https://linear.app/astralcareermatch/issue/AST-775/split-inflow-discovery-to-record-new-only-vet-inflow-seems-to-have) and [AST-776](https://linear.app/astralcareermatch/issue/AST-776/vet-inflow-discovery-company-dispatch-and-mechanical-prompt-vet-inflow) (discovery/vet split) — shipped on **origin/dev**; inflow batch must remain compatible.
* **AST-524/525/526** (table, per-term `last_scan_at`, Artifacts sync) — foundation stays; dispatch wiring changes.
* Prior [AST-801](https://linear.app/astralcareermatch/issue/AST-801/inflow-discovery-is-not-recognizing-candidate-ready-for-scanning) child work ([AST-802](https://linear.app/astralcareermatch/issue/AST-802/inflow-discovery-eligibility-when-saved-search-terms-present-inflow), [AST-805](https://linear.app/astralcareermatch/issue/AST-805/uat-ast-801-missing-from-deploy-env-user-testing-tooltip-after-prep)) is **Canceled**; any code landed on **origin/dev** from that wave is reverted or superseded as part of this epic.

## Open questions

1. **Revert boundary on** `origin/dev`**:** revert only the [AST-802](https://linear.app/astralcareermatch/issue/AST-802/inflow-discovery-eligibility-when-saved-search-terms-present-inflow) eligibility/reconcile-at-count and **candidate-entity** dispatch wiring, or also strip other INFLOW dispatch hooks while keeping the table + Artifacts sync from **AST-524–526**?
2. **Search-term state model:** eligibility driven solely by `last_scan_at` staleness under one registry state (e.g. **READY**) vs. explicit per-row **state** column transitions like **company** — which model should `SEARCH_TERM_STATES` use?
3. **Sibling inflow tasks:** should **inflow_resolve_website** and **vet_inflow_discovery** stay **company**-entity dispatch unchanged, or move under **search_term** / another unified pattern in this same epic?

---

## Original brief

dispatcher._dispatch_one index 1/1 inflow_discovery -> task start

| candidate_id=somerset available_count=0 entity_batch_id=inflow_discovery-d9837feb-ea70-4675-b8e2-083a5658d853 mode=CLICK run_next_chain=False entity_type='candidate' trigger_state='LIVE_PROMPTS'
Dispatching inflow_discovery — 0 available, batch inflow_discovery-d9837feb-ea70-4675-b8e2-083a5658d853

Skipping inflow_discovery: 0 available (min_count=1)

(Full candidate JSON dump — ~270KB — was in the pre-define Description; truncated here because Linear caps Description size. Key facts preserved above: somerset, LIVE_PROMPTS, available_count=0, fourteen artifact search terms.)

### Comments

#### susan — 2026-06-26T00:47:04.175Z
I changed my mind.  Push the broken code, we will refactor in a fresh ticket.  This is insane.

#### chuckles — 2026-06-26T00:21:27.925Z
@susan

1. **Revert boundary on `origin/dev`:** revert only **AST-802** eligibility/reconcile-at-count and **candidate-entity** dispatch wiring, or also strip other INFLOW dispatch hooks while keeping table + Artifacts sync from **AST-524–526**?
2. **Search-term state model:** eligibility by **`last_scan_at`** staleness under one registry state vs. explicit per-row **state** column like **company** — which for **`SEARCH_TERM_STATES`**?
3. **Sibling inflow tasks:** **inflow_resolve_website** / **vet_inflow_discovery** stay **company**-entity unchanged, or move under **search_term** in this epic?

— Chuckles

#### susan — 2026-06-26T00:19:03.622Z
Oh right, I remember now:  we created a specific candidate_search_terms table for exactly this reason.  So in this case, the entity type is SEARCH_TERM, not job or company.  That should make things easier, right?

Let's design the pattern for creating a new entity type.  I want to see a comprehensive, step by step list of components that will need to be modified to support the new entity type of "search_term" in this discussion phase.

#### chuckles — 2026-06-25T17:44:59.529Z
[check-linear] Discussion — AST-802 and AST-805 Canceled; redefine on unified dispatcher pattern per your note (@susan)

#### susan — 2026-06-25T17:42:58.762Z
Okay, after some research, I have discovered that we INVENTED A NEW PATTERN for this dispatch task, and put frequency hours in BOTH the database (on dispatch_task) AND in config.py.

I am going to request that this ticket be reverted, as we have done recently on the BUILD_ARTIFACTS ticket.  I am resetting this ticket to discuss, and we are cancelling the subissues in User Testing.

Running tasks on ANY ENTITY (job|company|candidate) should share exactly the same pattern through the dispatcher.  There is NO reason for there to be special handling for the candidate entity type.

Remove ALL of the config.py content that is specific to the inflow discovery scheduling, record fetching, etc., and update the dispatch and other components to find entities with state for candidates as well as job and company.

#### chuckles — 2026-06-25T17:07:28.688Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-805** | AST-801 missing from deploy env User Testing tooltip after prep-uat |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-805** — _AST-801 missing from deploy env User Testing tooltip after prep-uat_
- **Issue reported:** After **AST-801** prep-uat landed on **origin/dev**, Susan restarted from **origin/dev** and hovered the deploy env label. The User Testing tooltip did **not** list **AST-801** among parents ready for UAT (other User Testing parents appear; **AST-801** is missing).
- **Should now:** When Chuckles runs **prep-uat** for a parent and lands **ftr** on **origin/dev**, that parent appears in **merge_tickets** (deploy env tooltip) once the parent is in Linear **User Testing** and Susan pulls **origin/dev** — without manual log surgery.
- **Quick check (this fix only):**
  1. Land **AST-801** via **prep-uat** (**ftr** merged to **origin/dev**; parent moved to **User Testing**).
  2. Pull **origin/dev** locally or on staging.
  3. Hover the deploy env label (AST-791 tooltip).
  4. Observe **AST-801** is absent from the User Testing parent list.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-25T16:56:04.691Z
@chuckles I don't see 801 in the list of User Testing issues in the tooltip when I restarted from origin/dev.  Can you confirm that this was fully prepped for UAT and that the log file was updated correctly?

#### chuckles — 2026-06-25T04:20:45.086Z
@susan

1. Was this repro on staging/Railway or local dev, and did you **Save** search terms in Artifacts after **Generate** (generate alone does not persist to the table)?
2. Is a one-time **artifacts → company_search_terms** backfill at eligibility time acceptable for legacy candidates like **somerset**, or should the fix be limited to forward paths only (save, generate finalize, startup migration)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
