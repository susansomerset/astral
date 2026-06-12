# AST-421 — Design data flow for Astral Boards: plan company resolution and consult parity

**Parent:** [AST-379](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards)

**Publish ref (origin):** `sub/AST-379/AST-421-design-data-flow-for-astral-boards` (child of AST-379; not `main` integration line).

**Summary:** Board-sourced jobs enter Astral with saved-search provenance and no real hiring employer attached. Qualify/evaluate can use the JD alone, but Consult, culture work, and the company-centric pipeline require a resolved employer (`company_id`) with website and eventual job-list page data. This plan binds how board jobs graduate from a **sentinel placeholder company (`BOARD-SOURCE`)** through a **standalone dispatcher batch** that extracts/links the hiring employer (with agency rules), introduces job state **`SEEK_COMPANY`** when identity is actionable (name + homepage URL), runs **mandatory Roster prefilter** for newly resolved board-origin employers, joins the existing company state machine (**WEBSITE_FOUND** → roster spine), and finally reaches **Consult parity** with manually ingested jobs while preserving **`board_search_id`** provenance. **No product code in AST-421** — this file is the execution partition for follow-on build tickets.

---

## Files changed (planned — follow-on implementation)

Spike or one-off investigation output stays under **`debug/spikes/<topic>/…`** only (gitignored). No repo-root **`artifacts/`**.

| File | Change | Layer |
|------|--------|-------|
| `docs/features/boards/ast-421-design-data-flow-for-astral-boards-plan-company-resolution-and-consult-parity.md` | Architecture + execution slices (this document) | docs |
| `src/utils/config.py` | Sentinel company id/key (literal), new `JOB_STATES` entry **`SEEK_COMPANY`** (+ `prior_states` / UI lists), new `TASK_CONFIG` + optional `TRACKER_CONFIG` keys for employer-extraction schema, metrics key names documented in tracker/dispatcher | utils |
| `src/data/database.py` | Claim/clear/get batch helpers for the resolution task (jobs by state + provenance predicates); extend header inventory only as designed in child ticket; optional narrow columns on `jobs` for resolution counters if not derived from ledger | data |
| `src/core/dispatcher.py` | New batch runner wired like existing claim→process→clear tasks; **`dispatch_tasks` row** (DB) for entity_type `job`, trigger state per §Stage 2 | core |
| `src/core/tracker.py` | `transition_job_state` callers for board resolution outcomes; guardrails so non-board jobs are untouched | core |
| `src/core/consult.py` | Ensure consult batch **claim SQL** excludes board jobs still in **`SEEK_COMPANY`** until company prep gates pass (or equivalent single gate in dispatcher) | core |
| `src/core/roster.py` | No alternate prefilter for board employers — use existing **`prefilter_company`** / **`WEBSITE_FOUND`** path; company create/link sets state per rules below | core |
| `tests/component/...` | Resolution batch, state transitions, consult gating (owned by follow-on QA manifest — not this ticket) | tests |

---

## Stage 1: Sentinel placeholder — `BOARD-SOURCE`

**Done when:** The data model and config name a single canonical **placeholder company** used for all board-sourced jobs that have **not** completed hiring-employer resolution. Ingest and board pipelines reference it by **`config.py` literal** (e.g. stable ` BOARD_SOURCE_COMPANY_ID` keyed to a row created at bootstrap or migration). No production job that has a resolved hiring employer retains `company_id == BOARD_SOURCE`.

1. Define **`BOARD-SOURCE`** (display name negotiable in implementation; canonical **company id / slug** stable) as the sentinel row in **`companies`**. Document in config a single authoritative id integer (or slug lookup at startup once — prefer **literal id** in config after bootstrap migration to satisfy **ASTRAL_CODE_RULES §2.1** “no fallback” ethos for sentinel identity).

2. **Board ingest** (already owned by **AST-415–419** slice) attaches new board jobs to this sentinel **until** resolution succeeds per Stage 3–4. This plan does **not** re-specify ingest; it only requires **`jobs.company_id = BOARD_SOURCE`** for the unresolved board path.

3. ⚠️ **Decision:** Sentinel is a **real `companies` row**, not a null `company_id`. Foreign keys and Consult prep stay consistent with existing “job has a company” assumptions; “no real employer” is expressed as **sentinel id**, not SQL NULL.

---

## Stage 2: Standalone dispatcher task — employer resolution (decoupled from qualify / evaluate / Consult order)

**Done when:** A **`dispatch_tasks` table** row exists whose **`entity_type`** is `job`, whose trigger state is **`PASSED_JD`** (see substeps), whose batch runner is **orthogonal** to `qualify_job_listings`, `evaluate_jd`, and `consult_*` — i.e. it is scheduled and claimed on its **own row**, not inlined inside those runners. Timing is indirectly coupled only because **PASSED_JD** implies JD text exists.

1. **Task key:** use a **new dispatcher batch function** registered alongside existing runners in **`src/core/dispatcher.py`** (name e.g. `resolve_board_hiring_employer` — final identifier set in **`dispatch_tasks`** + **`TASK_CONFIG`** in follow-on ticket). **`batch_id`** pattern follows **§2.4**: `f"{task_key}-{uuid4()}"`.

2. **Claim predicate (exact shape for implementer):** Claim jobs where **all** hold:
   - `job.board_search_id IS NOT NULL` (board provenance — column name per live schema from **AST-458** family if already present; if absent at build time, stop and escalate),
   - `job.company_id == BOARD_SOURCE_COMPANY_ID`,
   - `job.state == 'PASSED_JD'`,
   - Optional anti-retry flags as designed in child ticket (e.g. resolution attempt cap) — **do not add silent infinite loops**.

3. **Independence:** The runner **must not** call `render_verdict` or transition jobs into Consult states. It only performs employer identification, company link/create, and **job/company state transitions** defined in Stages 3–5.

4. ⚠️ **Decision:** **Trigger state `PASSED_JD`** is the gate (not `NEW` or `PASSED_JOBLIST`) so title/JD gates from the v1 board slice remain authoritative; resolution consumes **full JD** after evaluate.

---

## Stage 3: Extraction semantics — hiring employer vs board site, ATS, staffing agency

**Done when:** The resolution task extracts **exactly one hiring employer candidate** suitable for **`companies`** linkage: the **end client** employer, excluding the board marketplace domain, ATS vendor hostname noise, and **pure staffing-agency posters** unless the JD is employer-of-record only.

1. **`TASK_CONFIG`** entry defines a structured JSON schema ( **`response_schema`**) capturing at minimum: `employer_name`, `employer_homepage_url` (nullable), `agency_only` (bool), `agency_and_client_detected` (bool), optional `agency_name`, `confidence`/`notes`. Implementation uses **`do_task`** / **`tracker`** patterns per **§2.2**.

2. **Agency-only posting:** When the model classifies **`agency_only=true`** and there is **no** identifiable end client, the job **does not** receive a real hiring `company_id`. Transition: leave job on **`BOARD-SOURCE`** (or dedicated terminal job state per follow-on product policy) and emit metric **`agency_rejected`**. **Do not** create a stub “client” company from the agency brand.

3. **Client + agency:** When **`agency_and_client_detected`**, **only the client** populates `employer_name` / `employer_homepage_url`. Agency may be stored in **`job_data`** notes for application mechanics only — **not** as `companies.name` for the hiring employer.

4. **Board site / ATS:** URLs that point to the **saved-search board host** or generic ATS **apply** pages **must not** be treated as `employer_homepage_url` unless the schema explicitly encodes a **verified** employer domain (implementer encodes rejection of known board host patterns in core after model output — defense in depth).

---

## Stage 4: Job + company outcomes — `SEEK_COMPANY`, link/create, `WEBSITE_FOUND` vs `NO_WEBSITE`

**Done when:** Every resolution run ends in a **documented terminal class** for the job and (when applicable) company rows, matching metrics in Stage 7. **No permanent “stub company with job-site work only”** shortcut: unknown employers are either **real `NO_WEBSITE` rows awaiting web search** or remain on **`BOARD-SOURCE`** until extraction succeeds.

### 4.1 Job state — `SEEK_COMPANY`

1. Add **`SEEK_COMPANY`** to **`JOB_STATES`** with **`prior_states: ['PASSED_JD']`** initially (narrow if code review finds a second legal entry — escalate; do **not** guess extra priors).

2. **Enter `SEEK_COMPANY`** iff extraction yields **both** a non-empty **employer name** and a **valid employer homepage URL** resolving to **`WEBSITE_FOUND` path** for the hiring company **in the same resolution pass** as `company_id` is updated off **`BOARD-SOURCE`**. On transition: **`job.company_id`** points to the real company row (**linked or created**), never simultaneously **`BOARD-SOURCE`**.

3. **`BOARD-SOURCE` exit criterion:** Whenever **`job.company_id != BOARD_SOURCE_COMPANY_ID`**, the job has left the sentinel path. **`SEEK_COMPANY`** is the **sole metadata flag** indicating “resolution produced actionable employer identity (name + URL) and Consult prep may proceed pending company readiness” (consult gating in Stage 6).

### 4.2 Name-only employer (no URL in JD)

1. Create or match a **`companies`** row with state **`NO_WEBSITE`** — **explicit**, not silently stubbed as **`WEBSITE_FOUND`**.

2. **Leave `jobs.company_id` on `BOARD_SOURCE`** until a **separate future web-search dispatch** (explicitly **out of AST-421 v1 build scope** unless Susan approves widening) attaches a canonical URL and promotes the company.

3. **Job state:** remains **`PASSED_JD`** (still on sentinel) OR follow-on **`EMPLOYER_NAME_PENDING`** — **implementer chooses one** in the child ticket; default recommendation: **stay `PASSED_JD` + exclude from duplicate resolution claims via `job_data.resolution_attempt` flag** to avoid starvation. ⚠️ **Decision:** Prefer **stay `PASSED_JD`** with idempotent **`job_data` flags** over proliferating micro-states unless Susan mandates otherwise.

### 4.3 Company lookup — create vs link

1. **Lookup first:** Normalize **hostname** / canonical domain from **`employer_homepage_url`**; query existing **`companies`** by website / domain keys already used elsewhere (reuse existing helpers in **`tracker`** / **`database`** — **DRY §1.3**).

2. **Link:** If match found, attach `job.company_id` to that row; **update** missing fields only where safe (no destructive overwrite of human-curated fields without an explicit rule in the child ticket).

3. **Create:** If no match, insert company with initial state:
   - **`WEBSITE_FOUND`** when URL present from JD,
   - **`NO_WEBSITE`** when name-only path (Stage 4.2).

4. **No stub-only GET/DO pattern:** Do **not** create a throwaway company that only exists to scrape a job listing without a validated employer domain linkage to that company record.

---

## Stage 5: Mandatory prefilter and Roster handoff (`WEBSITE_FOUND` spine)

**Done when:** Every board-origin employer that enters **`WEBSITE_FOUND`** completes **`prefilter_company`** (**`ROSTER_CONFIG['prefilter']`**) **before** any Consult prep consumes company metadata that prefilter normally supplies. Routing matches **manually imported** companies: **`WEBSITE_FOUND`** → (**prefilter**) → **`TO_WATCH` / `IGNORE` / `PREFILTER_UNKNOWN` / errors** → existing **`locate_job_page`** / **`parse_job_list`** flows through **`WATCH`** per **ASTRAL_CODE_RULES §3.2 dispatch table**.

1. **Dispatch:** Prefilter continues to trigger on **`trigger_state='WEBSITE_FOUND'`** — ensure board-created companies land in **`WEBSITE_FOUND`**, not a parallel hidden state.

2. **Ordering:** Resolution task (Stage 2) **must not** skip prefilter by stuffing evaluate-only fields into downstream consult keys. **Evaluate** and **prefilter** remain distinct concerns (Susan resolved decision **#4**).

3. **`NO_WEBSITE` path:** **`prefilter` does not run** until web-search child promotes company to **`WEBSITE_FOUND`** (follow-on ticket).

---

## Stage 6: Consult parity and provenance (`board_search_id`)

**Done when:** After **employer resolution + prefilter + required company prep** (job page located / parsed far enough that existing **`consult_do`** prerequisites hold — match current company-ingested semantics), board jobs occupy **the identical `CONSULT_CONFIG` / `render_verdict` state sequence** (`PASSED_DO` → `PASSED_GET` → `BUILD_ARTIFACTS` …) **with `board_search_id` unchanged** on the job row.

1. Extend **`JOB_STATES['PASSED_DO']['prior_states']`** (and any other consult entry enforced in **`consult.py`** / **`transition_job_state`**) to include **`SEEK_COMPANY`** alongside **`PASSED_JD`** so transitions are config-valid.

2. **Gate consult batches:** **`consult_do` claim SQL** excludes jobs in **`SEEK_COMPANY`** until **company readiness** predicates pass (explicit list in follow-on ticket — e.g. company in **`WATCH`** with this job’s listing URL materialized, or whatever **`requires_company`** paths already assert). **Single source of truth:** implementer documents the exact SQL predicate in the child ticket; do not duplicate gate in three modules.

3. **`board_search_id`:** Never cleared on successful resolution; UI and reporting use it as saved-search provenance.

4. **Non-regression:** Manual-import jobs without `board_search_id` follow unchanged paths (**scope gate**: this plan touches board-provenance rows only unless config changes require neutral prior_lists).

---

## Stage 7: Per-run metrics and follow-on Linear tickets

**Done when:** Each resolution batch emits **counts** sufficient to compute the rates below ( **`dispatch_ledger` JSON**, structured **app_log**, or dedicated counter columns — child ticket picks one approach consistent with **`dispatcher`** observability patterns).

### 7.1 Per-run counters (minimum set)

| Metric key | Meaning |
|------------|---------|
| `resolved` | Job left **`BOARD-SOURCE`** with real `company_id` and entered **`SEEK_COMPANY`** in this run |
| `linked_existing` | Resolution attached to an existing **`companies`** row |
| `created_new` | Resolution inserted a new **`companies`** row |
| `agency_rejected` | Agency-only / no client — job stays on sentinel |
| `unresolved` | Parser/model could not identify a hiring employer to threshold — job stays **`PASSED_JD`** / sentinel (bounded retries) |
| `no_website_deferred` | Name-only employer → **`NO_WEBSITE`** company row / flags; sentinel retained per Stage 4.2 |
| `bad_url_rejected` | Model output failed URL/domain validation |

### 7.2 Proposed follow-on Linear tickets (boundaries explicit)

1. **`Board employer resolution`** — Implements Stages **1–4, 7** (`dispatch_tasks` row + runner + TASK_CONFIG extraction + sentinel bootstrap + JOB_STATES + DB claims + metrics). **Excludes** web search.

2. **`NO_WEBSITE web discovery`** — Separate Google-style search dispatcher to promote **`NO_WEBSITE` → `WEBSITE_FOUND`**; **not** part of v1 resolution slice unless Susan expands scope.

3. **`Consult gate + state wiring`** — Implements Stage **6** (`prior_states`, consult claim SQL, integration tests against board fixtures).

4. **`Roster / prefilter validation`** — Stage **5** hardening + regression tests ensuring board companies never bypass **`WEBSITE_FOUND` prefilter**.

5. **`Metrics dashboard / admin surfacing`** (optional) — surfaces counters; **not** required for architecture sign-off.

---

## Self-assessment

**Scope:** `MAJOR-CHANGE` — Follow-on builds touch **`config.py`**, **`dispatcher.py`**, **`database.py`**, **`tracker.py`**, **`consult.py`**, **`roster.py`**, and tests across job/company/roster/consult seams.

**Conf:** `Medium` — Reuses **`do_task`**, **`dispatch_tasks`**, and Roster **`WEBSITE_FOUND`** patterns (**§2.2 / §2.4 / §2.6**), but **`SEEK_COMPANY`** insertion and Consult gating need careful SQL to avoid starvation or double-claims.

**Risk:** `HIGH` — A wrong **`prior_states` matrix or consult claim** could deadlock board jobs or cause major consult/regression issues, or wedge company-ingested flows if predicates leak.

---

## Self-review vs `docs/ASTRAL_CODE_RULES.md`

- **§1.3 DRY:** Lookup/create company reuses existing domain matching; no second prefilter pathway.
- **§2.1 config:** Sentinel id, state names, and task keys live in **`config.py`** / **`dispatch_tasks`** — no magic inline state sets in SQL.
- **§2.4 batch processing:** Resolution uses **claim → process → clear** with **`batch_id` first**.
- **§2.6 state machine:** All **new transitions** enumerated; **`transition_job_state`** is the sole mutator — data layer performs updates from caller-supplied target state only.
- **§3.3 imports:** No layer violations introduced by this design; new code stays **core orchestrating data + external**.
- **§3.5 naming:** snake_case task keys / states; **`SEEK_COMPANY`** / **`BOARD-SOURCE`** documented here match config constants.

---

## Execution contract (for developer agents on **follow-on** build tickets)

The follow-on **`plan`** / **`build-astral`** tickets inherit this binding:

- Execute child ticket steps in order; do not skip or merge cross-ticket stages without a new **plan-astral** revision.
- Do not add files, tasks, or states not listed in the **follow-on** plan derived from this architecture.
- On ambiguity — **stop, comment on AST-421 or the child ticket with 🛑 format**, await Susan/Chuckles.

---

## References (code today — read-only context)

- **`JOB_STATES` / `COMPANY_STATES` / `ROSTER_CONFIG`** — `src/utils/config.py`
- **`dispatch_tasks` runners** — `src/core/dispatcher.py`
- **Board provenance tests** — `docs/ASTRAL_TEST_BIBLE.md` §7.13q (**AST-458** / **`board_search`**)
