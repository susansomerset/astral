# AST-813 — Get inflow_discovery to work

<!-- linear-archive: AST-813 archived 2026-07-22 -->

## Linear archive (AST-813)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-813/get-inflow-discovery-to-work  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

**inflow_discovery** is broken for **somerset** (**LIVE_PROMPTS**, fourteen saved search terms): Scheduled Actions can show **Available = 1**, but a manual **Run** skips with `available_count=0` and logs `eligibility: 14 table row(s) but 0 stale (scan_interval_hours=168.0)` while the dispatch row's `freq_hrs` **is 0**. Eligibility and batch selection still read the hardcoded **168**-hour interval from product config instead of the dispatch row — and the admin **Available** count can disagree with the count at run time. Susan needs a **minimal hotfix** (not the deferred [AST-801](https://linear.app/astralcareermatch/issue/AST-801/inflow-discovery-is-not-recognizing-candidate-ready-for-scanning) `search_term` entity rework) that wires `dispatch_task.freq_hrs` through the full path and removes **INFLOW_CONFIG** `scan_interval_hours` as the staleness source for **inflow_discovery**.

## Functional scope

* **Single eligibility source:** **Available** on the Scheduled Actions list, `count_eligible_for_dispatch_task`, and `run_inflow_discovery_batch` stale-term selection all use the same interval derived from the candidate's **inflow_discovery** dispatch row `freq_hrs` — no hardcoded **168** and no silent ignore of the row value.
* `freq_hrs` **semantics:** when `freq_hrs > 0`, a term is stale when `last_scan_at` is null or older than `freq_hrs` hours. When `freq_hrs` **is 0 or unset**, no staleness interval applies — **every** table row counts as stale (Susan's current **somerset** row with `freq_hrs = 0` must show eligible and run).
* **Candidate gate unchanged:** owning candidate must still be in **LIVE_PROMPTS** (today's trigger state).
* **Table read path:** eligibility and batch execution load terms from `company_search_terms` without error; legacy artifact-only blobs reconcile into the table when that blocks reads.
* **Discovery execution:** when eligible, **inflow_discovery** runs CSE for each stale term (per semantics above), bumps `last_scan_at` after a successful search, dedupes hits, and records **NEW** companies through the existing Phase 1 path.
* **Debug traceability (AST-538):** skip logs with `debug=True` name the `freq_hrs` interval actually applied (including `0` **= no interval**), not `scan_interval_hours=168`.

## Boundaries

* **Out of scope:** [AST-801](https://linear.app/astralcareermatch/issue/AST-801/inflow-discovery-is-not-recognizing-candidate-ready-for-scanning) — no `search_term` dispatch entity type or admin entity-type migration.
* **Out of scope:** **vet_inflow_discovery**, **inflow_resolve_website**, and downstream vet/resolve unless this fix regresses them ([AST-754](https://linear.app/astralcareermatch/issue/AST-754/vet-inflow-seems-to-have-been-skipped) / [AST-775](https://linear.app/astralcareermatch/issue/AST-775/split-inflow-discovery-to-record-new-only-vet-inflow-seems-to-have) stay separate).
* **Out of scope:** Artifacts UI redesign, intake/craft authoring, CSE tuning, deferred Astral project work.
* **Must not break:** Artifacts save/sync into `company_search_terms`, other dispatch tasks on the same candidate, and per-term `last_scan_at` bump semantics after a successful CSE.

## Acceptance criteria

1. **somerset** / **LIVE_PROMPTS** / `freq_hrs = 0` / fourteen `company_search_terms` rows: Scheduled Actions **Available ≥ 1** and manual **Run** does **not** skip for `available=0` or `0 stale (scan_interval_hours=168)`.
2. **Available** on the list and `available_count` at dispatch start match for the same dispatch row (no **1** in admin → **0** at run drift).
3. With `freq_hrs > 0`, a term scanned within that interval is not eligible; lowering `freq_hrs` re-opens terms without redeploy.
4. Auto-mode and manual **Run** share the same eligibility rule (**min_count** unchanged).
5. With `debug=True` and skip, logs emit an `eligibility:` reason citing the applied `freq_hrs` (not config **168**).
6. Component tests cover `freq_hrs = 0` (all terms stale) and `freq_hrs > 0` cadence (Betty manifest).
7. A manual search of the codebase will NOT return a hit for `168` pertaining to discovery inflow, the value is database-driven, not config-driven.

## Dependencies and blockers

* **AST-524** / **AST-525** — `company_search_terms` table and per-term `last_scan_at` (shipped on **dev**).
* **AST-538** — backend debug contract (shipped).
* None blocking start.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-813 (parent) | ftr/AST-813-inflow-discovery-freq-hrs |
| AST-814 | sub/AST-813/AST-814-inflow-discovery-freq-hrs |

**Epic worktree:** `astral-AST-813/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |

---

## Original brief

Right now, there's a fat bug between dispatcher and candidate trying to fetch company search terms from the table.

This has birthed a plan for a whole new Astral project, but for now, I just need the search terms to get searched and the results processed, so just do the minimum needed for dispatch to use the dispatch_task freq_hrs value to determine company_search_term eligibility to run inflow_discovery.

### Comments

#### chuckles — 2026-06-26T02:15:51.176Z
[check-linear] Discussion — AC 7 incorporated (@susan)

#### susan — 2026-06-26T02:14:52.658Z
@chuckles See my updated acceptance criteria.

#### chuckles — 2026-06-26T02:13:11.031Z
[check-linear] Discussion — definition updated (@susan)

#### susan — 2026-06-26T02:10:46.511Z
@chuckles when I checked just now, it said 1 available, so I ran it, but I forgot to set the debug flag.  So, I killed the run.  Console showed this:

```
dispatcher._dispatch_one index 1/1 inflow_discovery -> task start
 | candidate_id=somerset available_count=0 entity_batch_id=inflow_discovery-cc4c35ef-cc73-42eb-9990-55e678ec8b46 mode=CLICK run_next_chain=False entity_type='candidate' trigger_state='LIVE_PROMPTS'
Dispatching inflow_discovery — 0 available, batch inflow_discovery-cc4c35ef-cc73-42eb-9990-55e678ec8b46
dispatcher._run_dispatch_loop index 1/1 inflow_discovery -> skipped — below min_count
 | available=0 effective_min=1 is_auto=False
 | eligibility: 14 table row(s) but 0 stale (scan_interval_hours=168.0)
Skipping inflow_discovery: 0 available (min_count=1)
[inflow_discovery] thread exited and cleared from registry
```

Now it says avail = 0, but the freq_hrs for the dispatch_task record is set to 0, so at the very least, remove the hard coded value of 168.

#### chuckles — 2026-06-26T02:03:52.337Z
@susan

1. Confirm UAT repro: which candidate (still **somerset**?) and whether the live failure is **Available = 0**, a runtime error on run, or both — so acceptance testing matches your experience.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
