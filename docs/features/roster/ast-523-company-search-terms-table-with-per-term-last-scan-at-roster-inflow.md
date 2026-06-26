# AST-523 — Company search terms table with per-term last_scan_at (Roster inflow)

<!-- linear-archive: AST-523 archived 2026-06-15 -->

## Linear archive (AST-523)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-523/company-search-terms-table-with-per-term-last-scan-at-roster-inflow  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-490 — Roster inflow  
**Blocked by / blocks / related:** parent: AST-490

### Description

## Purpose

Roster inflow Phase 0 stores company discovery search terms as a single newline-delimited string on the candidate artifact. Phase 1 discovery runs all terms whenever the candidate-level dispatch task is due. That cannot record when each individual term was last searched, so the product cannot skip recently scanned terms or resume fairly across a long term list. This ticket replaces the blob with a per-candidate table of search terms, each row carrying its own **last_scan_at**, and wires Phase 1 discovery to scan only terms that are due — independent of dispatch-task run timestamps.

## Functional scope

* **Persistent term table:** A **company_search_terms** store holds one row per search term per candidate (trimmed non-empty term text). Each row includes **last_scan_at** (nullable until first successful search).
* **Textarea UX unchanged:** The Artifacts **Company Search Terms** page keeps a single textarea with **one term per line** — same interaction model as today. Save and Generate still feel like editing plain text.
* **Save sync:** When the user saves (or autosaves) the textarea, the system **upserts** rows for every line in the text and **deletes** rows for terms that are no longer present. Unchanged terms keep their existing **last_scan_at**.
* **Generate sync:** When **craft_company_search_terms** returns a new term list, apply the same upsert-and-delete rules before the user confirms Save (or on Save after review — same contract as other craft artifacts).
* **One-time migration:** Existing **artifacts.company_search_terms** strings for live candidates are imported into the table on upgrade (split on newlines, trim, drop blanks). After migration, the table is the source of truth for discovery.
* **Token for prompts:** **COMPANY_SEARCH_TERMS** (and any craft/discovery prompts that need the list) resolve from the table — rendered as newline-delimited text for the model — not from the artifact blob.
* **Per-term discovery cadence:** **inflow_discovery** considers a term eligible when **last_scan_at** is null or older than the configured scan interval (weekly intent, same as today's 7-day discovery window — sourced from product config, not from **dispatch_task.last_run_at** or **freq_hrs** on the dispatch row).
* **Discovery batch behavior:** When discovery runs for a candidate, Google CSE executes **only for eligible (stale) terms**. After a term's search completes successfully, that row's **last_scan_at** is updated. Failed terms do not advance **last_scan_at**.
* **Dispatch eligibility:** The **inflow_discovery** dispatch task is available when the candidate has at least one stale term (and other existing candidate/state preconditions still hold). It is **not** gated on **dispatch_task.last_run_at** for cadence.

## Boundaries

* **No cron / calendar schedules** (e.g. "every Monday at 6am") — out of scope; per-term **last_scan_at** + config interval only.
* **No change** to Phase 1 vetting, ingest, or Phases 2–5 beyond reading terms from the table and per-term timestamps.
* **No new Artifacts UI paradigm** — no per-row table editor in v1; textarea only.
* **Does not** remove the **inflow_discovery** dispatch task row; it changes what "eligible" means and what runs inside the batch.
* **Does not** change **IMPORTED** ingest or company URL dedupe rules.
* **Artifact blob:** Stop writing **artifacts.company_search_terms** after migration; optional read-through during transition is acceptable if needed for rollback, but discovery and tokens must use the table.

## Acceptance criteria

1. Saving the Company Search Terms textarea creates/updates/deletes **company_search_terms** rows for that candidate; terms removed from the text are deleted from the table.
2. Regenerating terms and saving applies upsert-and-delete; terms unchanged in text retain their prior **last_scan_at**.
3. Migrating an existing candidate with an artifact string produces equivalent table rows without data loss.
4. **COMPANY_SEARCH_TERMS** in prompts matches the table content (newline-joined), not a stale artifact field.
5. **inflow_discovery** runs CSE only for terms whose **last_scan_at** is null or past the configured scan interval; terms searched recently are skipped.
6. After a successful CSE for a term, that term's **last_scan_at** is set; dispatch-task **last_run_at** is not used to decide term staleness.
7. Dispatch shows **inflow_discovery** as available when at least one term is stale (and candidate preconditions pass), even if the dispatch row was run recently for other reasons.
8. Artifacts page still presents one textarea, one term per line; Generate/Regenerate/Save behavior matches other craft artifacts from the user's perspective.

## Dependencies and blockers

* [AST-504](https://linear.app/astralcareermatch/issue/AST-504/company-search-terms-artifact-and-craft-task-roster-inflow) — shipped Phase 0 artifact/craft task (superseded for storage by this ticket).
* [AST-505](https://linear.app/astralcareermatch/issue/AST-505/discovery-search-vet-slugs-and-ingest-new-companies-roster-inflow) — Phase 1 discovery pipeline to retarget at the table and per-term cadence.
* Parent epic [AST-490](https://linear.app/astralcareermatch/issue/AST-490/roster-inflow) — coordination only; may finish UAT before this lands.

## Open questions

None.

---

## Original brief

Susan (UAT on AST-490): We have a single text block of search terms but need to track each term's **last_scan_at** per candidate. Proposed table name **company_search_terms**.

Decisions:

1. Upsert with delete for missing terms on save/generate.
2. Per-term search cadence via **last_scan_at** — not timed from dispatch-task dates (**freq_hrs** / **last_run_at**). Future calendar schedules (e.g. "every Monday 6am") are out of scope.
3. UI: keep one term per line in a textarea for consistency with other artifacts.
4. New ticket under roster inflow, not folded into current UAT finish-up.

### Comments

#### chuckles — 2026-05-29T03:51:54.788Z
## Manual test steps

**Prereqs:** Local `dev` merged (§8). Restart app if already running. Candidate with roster inflow preconditions (profile/context, rubric if discovery needs it). `INFLOW_CONFIG["discovery"]["scan_interval_hours"]` = 168 (weekly).

### AST-524 — table + migration
1. Pick a candidate that still has legacy `artifacts.company_search_terms` string (or seed one), restart app / open DB fresh so migration runs.
2. Inspect `company_search_terms` table — rows match trimmed newline terms; `last_scan_at` null for new imports.
3. Save textarea with terms removed — corresponding rows deleted; unchanged terms keep prior `last_scan_at`.

### AST-526 — Artifacts UI/API
4. **Artifacts → Company Search Terms** — one textarea, one term per line; loads from table (not artifact blob).
5. Edit lines, Save — table upsert/delete; `artifacts.company_search_terms` not persisted on save.
6. Generate / Regenerate — craft flow unchanged from user POV; save after generate syncs table.

### AST-525 — per-term discovery cadence
7. Confirm **COMPANY_SEARCH_TERMS** token in a craft/discovery prompt preview matches table (newline-joined).
8. Set one term's `last_scan_at` recent, leave another stale/null — run **inflow_discovery** dispatch; only stale term gets CSE.
9. After successful search, stale term's `last_scan_at` updates; recently scanned term skipped on next run.
10. Dispatch shows **inflow_discovery** available when ≥1 stale term exists even if dispatch row `last_run_at` is recent.

### Regression
11. Company dispatch / consult path — no `consult ↔ roster` import crash on startup or dispatch.

---

`origin/ftr/AST-523-company-search-terms-table-with-per-term-last-scan-at-roster-inflow` @ `c22a8d20` · local `dev` @ `8c835d8f` merged (§8). Sub branches deleted (524, 525, 526).

**§6 note:** Full `run_component_tests.sh` still reports 48 failures — same count as `origin/dev` baseline (pre-existing agent/admin mocks). AST-523 scoped tests (12) green; collection 1122 tests, no import errors.

**Radia audit §6.5:** Parent acceptance criteria PASS on composite code review; child subs rolled up. No fix-now sub-issues filed.

— Chuckles

#### chuckles — 2026-05-29T03:25:55.875Z
prep-uat blocked — §6 component test smoke failed on `origin/ftr/AST-523-company-search-terms-table-with-per-term-last-scan-at-roster-inflow` @ `259b3a4e`.

**Gates §1–§2:** Parent In Progress; children AST-524/525/526 all User Testing; sibling merge gate satisfied.

**§5:** All three `sub/*` tips already ancestors of `ftr` (rollup-child complete) — no additional merges.

**§6 `run_component_tests.sh` (throwaway worktree at ftr tip):** Collection interrupted — **4 errors** before tests run:

1. **Circular import** `src.core.consult` ↔ `src.core.roster` — `roster.py` imports `_render_pass_fail` from `consult`; `consult.py` imports `roster` (uses `roster.get_company_data`, `roster.run_company_task`). Affects `test_agent.py`, `test_board_sourced_qualify_evaluate.py`, `test_consult.py`, and anything importing consult at collection time.

2. **Bible vs product mismatch (AST-526 publish ref):** `tests/component/core/test_candidate.py` and `tests/component/utils/test_config.py` import `RESUME_STRUCTURE_CONTACT_SECTION_IDS` from `src.utils.config`, but that symbol is **not** in `config.py` on this ref (AST-526 plan §5d documents intentional removal of AST-517 resume_structure surface from this branch).

**Baseline note:** `origin/dev` runs the same harness with collection succeeding (53 failed / 1004 passed on a dev worktree) — failures are pre-existing on dev; the **ftr rollup adds collection-blocking import/symbol errors** that must be fixed before UAT prep can continue.

**Not done:** §6.5 audit-linear, §7 sub branch deletion, §8 local `dev` merge, §9 User Testing.

@susan — please fix on `origin/ftr/AST-523-company-search-terms-table-with-per-term-last-scan-at-roster-inflow` (break consult↔roster cycle and align tests with AST-526 config scope, or restore symbols if removal was premature), then re-run prep-uat AST-523.

— Chuckles

#### ada — 2026-05-29T02:59:18.470Z
[check-linear]

**Session scope:** Parent **AST-523** / **Astral Roster** — orchestrator assigned issue ids **(none)** (no pipeline on parent or siblings **AST-524**–**526**).

**§0a (`astral-ada` / `dev-ada`):** `git fetch origin`, `checkout dev-ada`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). No publish-ref merges (check-linear only).

**§0b:** `@ada` issue search (Team Astral + **Astral Roster** project); roster **14d** fallback. Full threads on **AST-523**, children **AST-524** / **AST-525** / **AST-526**, and assignee-me / @ada hits (**AST-521**, **AST-515**, **AST-520**, **AST-517**, **AST-518**, **AST-507**, **AST-513**). **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix.

**§1:** Assigned ids **(none)** — assignee-me add-on scanned for comments only; no ticket work in scope.

**Epic status (informational):** Children **Tests Passed** (Hedy **524**/**525**, Katherine **526**); Betty manifests on publish refs; Chuckles git table on parent unchanged. Next gates: engineer **`test-astral`** / Radia **`review-astral`** on children — not invoked from this pass.

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral`.

#### ada — 2026-05-29T02:16:06.054Z
[check-linear]

**Session scope:** Parent **AST-523** / **Astral Roster** — orchestrator assigned issue ids **(none)** (skip sibling **AST-524**–**526** and parent pipeline work).

**§0a (`astral-ada` / `dev-ada`):** `git fetch origin`, `checkout dev-ada`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). No publish-ref merges (check-linear only; no `test-astral` / `resolve-astral`).

**§0b:** `@ada` issue search (Team Astral + **Astral Roster** project); **14d** fallback on roster project (`updatedAt -P14D`). Full threads on **AST-523**, children **AST-524** / **AST-525** / **AST-526**, and recent @ada hits in session project (**AST-513**, **AST-520**, **AST-521**, **AST-517**, **AST-498** / **AST-522**). **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix.

**§1:** Assigned ids **(none)** — no assignee-me add-on tickets in scope.

**Thread notes (not Ada inbox):** Children **Plan Approved** (Hedy **524**/**525**, Katherine **526**); Chuckles plan-validation + git table on parent; no new `@ada` since prior roster/interface check-linear passes.

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass (happy path).

#### chuckles — 2026-05-29T02:10:14.454Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-523 (parent) | ftr/AST-523-company-search-terms-table-with-per-term-last-scan-at-roster-inflow |
| AST-524 | sub/AST-523/AST-524-company-search-terms-table-and-sync |
| AST-525 | sub/AST-523/AST-525-per-term-inflow-discovery-cadence |
| AST-526 | sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table |

**blockedBy:** AST-525, AST-526 → AST-524

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
