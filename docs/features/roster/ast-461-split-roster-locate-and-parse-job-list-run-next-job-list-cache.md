# AST-461 — Split roster locate and parse_job_list (run_next, job list cache)

<!-- linear-archive: AST-461 archived 2026-06-15 -->

## Linear archive (AST-461)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-461/split-roster-locate-and-parse-job-list-run-next-job-list-cache  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Roster today runs job-page **selection** and **parse** as a hard-coded one-two punch in a single code path: after `select_job_page` confirms the list page, parse runs immediately using in-memory DOM only—no `run_next`, no durable job-list visible text, and no clean handoff for companies reopened from **NO_OPENINGS**. This refactor splits **locate** (through job-list confirmation) from **parse**, uses platform caching (`run_next`, caller cache tokens), and handles **JOBS_FOUND** with a verify-then-parse path—not parse alone.

Supersedes the **locate/parse refactor** portion of [AST-375](https://linear.app/astralcareermatch/issue/AST-375) (canceled). Sibling: **recheck_no_openings** ticket (introduces **JOBS_FOUND** and routes recheck there).

**Historical note:** Older specs referred to `vet_job_site` / `vet_job_list`. The live pipeline uses `select_job_page`, which returns `response_type`, `job_titles`, and `no_jobs_message`—that confirmation step (not parse alone) is where job titles are recognized for DOM culling before `parse_job_list`.

## Functional scope

### Locate phase (discovery → confirm job list page)

* `locate_job_page` (or equivalent) ends after the product is confident which URL is the job list page—via existing multi-page discovery for **TO_WATCH**, without invoking parse in the same batch.
* **Outcomes unchanged in intent:** Including **NO_OPENINGS** when visible text already shows a no-jobs message on the confirmed page; **WATCH** / **HARD_PARSE** / **CANNOT_PARSE_JOB_SITE** / **NO_JOBLIST** / **BOT_BLOCK** etc. when applicable after the full chain completes.
* On successful job-list confirmation (**titles present**, not no-jobs): persist job-list **visible text** for the confirmed page in `company_data` (new key; exposed as a `{$JOB_LIST_VISIBLE}` token). **Do not** save job-list visible text when the outcome is **NO_OPENINGS** (no list content to cache).
* Configure `run_next` from locate’s terminal AI step to the parse task so the chain is data-driven, not hard-coded in roster core.

### Parse phase (`parse_job_list` via `run_next`)

* **Parse** runs as a separate hop: consume `{$CALLER_CACHE_A}` (or equivalent) for job-list visible text from the locate hop, plus **live** DOM content for the same page load where required.
* Validate parse output and transition to post-locate states per existing roster rules. Do not land in **WATCH** without successful parse when listings are expected.

### **JOBS_FOUND** path (from sibling recheck ticket)

* Companies in **JOBS_FOUND** have a known `job_site` but no trustworthy cached job-list content (recheck did not store visible text).
* Processing starts from **job-list confirmation onward** on that URL—functionally the post-discovery slice that today lives in `select_job_page` and below (legacy “vet” role): fresh Playwright scrape, confirm the page is still valid (covers **404** / dead page), obtain `job_titles` when the list is present, then chain parse via `run_next`.
* **Not** parse-only: a dead or wrong page must fail into appropriate existing error states, not **WATCH** with bad instructions.
* **No stale cache:** Do not reuse old job-list visible text; scrape at verify time, then pass through caller cache for the parse hop only within that execution chain.

### Platform alignment

* Task keys remain the configured source of truth; `run_next` and caller cache tokens follow established agent patterns.
* Optional **run_next** to **gaze** after **WATCH** remains optional (existing behavior).

## Boundaries

* Does **not** implement the **NO_OPENINGS** Playwright-only recheck (sibling ticket).
* Does **not** reconfigure dispatch table rows (follow-up).
* Does **not** address unrelated per-site parse errors (**AST-179**) or **NO_JOB_SITE** search fallback (**AST-180**).
* State machine changes (**JOBS_FOUND**, transitions) coordinated with sibling; any new transitions live in config.

## Acceptance criteria

1. **Split batches:** Locate/confirm batch does not call `parse_job_list` inline; parse runs via `run_next` (or equivalent documented chain) on the success path.
2. **Visible text token:** On job-list confirmation with titles, `{$JOB_LIST_VISIBLE}` resolves from persisted or caller-cached content; **not** saved on **NO_OPENINGS** outcomes.
3. **Parse input:** Parse hop receives caller-cached visible text plus DOM as designed; outcomes match today’s post-locate state set for equivalent page content.
4. **JOBS_FOUND:** A company routed from recheck is processed from single-page confirm onward (fresh scrape, titles/404 handling), then parse; reaches **WATCH** only with valid parse instructions when listings exist.
5. **Regression:** **TO_WATCH** discovery still finds job sites; **NO_OPENINGS** recheck sibling still does not use AI.
6. **No stale job-list cache:** Reopened companies do not parse from job-list content stored while they were **NO_OPENINGS**.

## Dependencies and blockers

* **Sibling ticket (recheck_no_openings):** Introduces **JOBS_FOUND** and recheck routing; this ticket implements verify+parse for that state.
* **AST-323** (Done) — prior consolidated discovery context.
* None blocking start on the **TO_WATCH** split; **JOBS_FOUND** path should ship after or with sibling state definition.

## Open questions

None.

### Comments

#### chuckles — 2026-05-26T01:34:58.909Z
`origin/dev` @ `9b5fd04c` — roster locate/parse split landed. Merge conflicts in `docs/ASTRAL_TEST_BIBLE.md` + `src/data/database.py` (boards + roster integration) resolved at finish-up.

Engineers: merge into `dev-<agent>`:

```bash
git fetch origin && git checkout dev-<agent> && git merge origin/dev
```

(not rebase unless Susan directs)

— Chuckles

#### chuckles — 2026-05-25T04:28:50.577Z
## AST-485 pipeline complete — rollup landed; UAT prep partial

**Child [AST-485](https://linear.app/astralcareermatch/issue/AST-485)** → **User Testing** (Hedy). Full lane: plan → validate → build → qa → test → review → resolve.

**Rollup:** `origin/sub/AST-461/AST-485-roster-dispatch-admin-task-keys` merged into **`origin/ftr/AST-461-split-roster-locate-and-parse-job-list-run-next-job-list-cache`** @ **`0e0f0c50`**.

**Dispatch UAT check (your blocker):** On that ref, Admin create-task picker should expose **`find_job_page`**, **`select_job_page`**, **`parse_job_list`** (legacy **`locate_job_page`** migrated in DB ensure). Smoke **Scheduled Actions → Dispatch Task → Create**.

**Integration sanity:** `run_component_tests.sh` on **`ftr/`** after rollup → **6 failed**, **923 passed** (roster parse branches + AST-471 dispatch config helpers). Per prep-uat §6, not merging into **local `dev`** until resolved.

**Local `dev`:** merge **`origin/ftr/…`** into **`dev`** hit conflicts in **`docs/ASTRAL_TEST_BIBLE.md`**, **`src/data/database.py`** — merge aborted. @susan resolve on `dev` or test from a worktree at **`origin/ftr/AST-461-…`** @ **`0e0f0c50`**.

**Sub branch:** kept on origin until conflicts green and you want **`prep-uat`** cleanup delete.

— Chuckles

#### chuckles — 2026-05-25T04:09:32.728Z
## Dispatch follow-up — Chuckles

| Ticket | Title | Assigned to | Branch |
|--------|-------|-------------|--------|
| AST-485 | Dispatch admin task_keys (find/select/parse) | Hedy | `sub/AST-461/AST-485-roster-dispatch-admin-task-keys` |

Parent **User Testing** unchanged; UAT sign-off waits on AST-485 + rollup.

— Chuckles

#### chuckles — 2026-05-25T04:09:27.728Z
## UAT blocked — dispatch seed follow-up

Susan: UAT on **AST-461** stays **blocked** until **AST-485** (Hedy) ships and rolls into the parent **`ftr/`** branch.

**Symptom:** Dispatch Task create modal still lists **`locate_job_page`**; **`select_job_page`** and **`parse_job_list`** missing from task_keys seed.

**Child:** [AST-485](https://linear.app/astralcareermatch/issue/AST-485) — Hedy, pipeline started.

**Publish ref:** `origin/sub/AST-461/AST-485-roster-dispatch-admin-task-keys`

— Chuckles

#### chuckles — 2026-05-25T04:06:04.502Z
[check-linear]

**§0a:** `astral` / `dev` — `git merge origin/dev` already up to date.

**§0b–§2 (AST-461 + child AST-469):** Scanned full threads. **No `@chuckles`** and no open assignee thread for Chuckles after the latest `[check-linear]` / prep-uat comments.

**Actionable — Susan UAT note (2026-05-25):**

> `locate_job_page` still in Dispatch Task modal task-key list; `select_job_page` and `parse_job_list` missing from create options.

**Diagnosis (read-only on `origin/ftr/AST-461-…` + local `dev`):**

- Admin picker seeds from `database.dispatch_task_seed_templates()` → `_DISPATCH_TASK_SEED` in `src/data/database.py`.
- That dict still includes **`locate_job_page`** (legacy label) and does **not** list **`select_job_page`** or **`parse_job_list`**.
- AST-469 roster work uses **`find_job_page`** / **`select_job_page`** / **`parse_job_list`** (`agent_task` + `ROSTER_CONFIG`); **`_apply_ast469_select_job_page_run_next_migration`** wires agent `run_next`, not dispatch table seeds.
- Parent definition **AST-461** explicitly deferred **dispatch table row reconfiguration** (follow-up per plan validation **discuss**).

**Not a check-linear code fix** (Chuckles does not land product). **UAT on roster chain** can still pass without new dispatch rows; this is **admin discoverability / scheduling** gap.

**Suggested next step (pick one):**
1. **Accept for UAT** — treat as known follow-up; file a small **Roster** or **Admin** ticket to refresh `_DISPATCH_TASK_SEED` (`find_job_page` vs `locate_job_page`, optional `select_job_page` / `parse_job_list` rows).
2. **Block UAT** — if you need those keys in the modal before sign-off, assign **Hedy** (or whoever owns admin seed) with explicit scope off AST-469.

**Pipeline status (unchanged):** Parent **User Testing** @ `origin/ftr/AST-461-split-roster-locate-and-parse-job-list-run-next-job-list-cache` (`ea3227ab`). Child **AST-469** **User Testing**. **finish-up** after **PR Ready**.

— Chuckles

#### susan — 2026-05-25T04:04:24.600Z
"locate_job_page" still appears in the selection list on the Dispatch Task modal, and select_job_page and parse_job_list do not appear as options to create for dispatch.

#### chuckles — 2026-05-24T02:04:17.971Z
## UAT Ready — Chuckles

All **1** child branch merged into parent branch and child branch deleted.

**Parent branch:** `origin/ftr/AST-461-split-roster-locate-and-parse-job-list-run-next-job-list-cache` @ **`ea3227ab`**

**Merged in order:**
1. **AST-469** — Roster locate/parse split: run_next, JOB_LIST_VISIBLE, JOBS_FOUND path (`sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path` — **deleted**)

**Local `dev`** merged (prep-uat §8) @ **`c5faa1f8`** — resolved conflicts with your in-flight board commits (**AST-457/458** on `dev`). **Not** pushed to `origin/dev`.

**Engineers — after Susan runs finish-up and pushes `origin/dev`:** merge `origin/dev` into `dev-<agent>` per orientation § Merge integration line.

## Manual test steps

**Prereq:** Restart API/workers if running; use local **`dev`** @ **`c5faa1f8`**.

1. **TO_WATCH locate → parse chain:** Run a **TO_WATCH** company through roster locate (`find_job_page` / `select_job_page`). On **JOBLIST_TITLES**, confirm **`parse_job_list`** runs as a **second hop** (agent batch / logs show chained task), not inline in the same roster call stack.
2. **`JOB_LIST_VISIBLE`:** On successful title confirmation, inspect resolved prompt for **`parse_job_list`** — visible job-list text should come from caller cache token **`{$JOB_LIST_VISIBLE}`**, not empty/stale DOM-only.
3. **NO_OPENINGS — no list cache:** Company ending **NO_OPENINGS** on locate must **not** persist job-list visible text for later parse (reopen or **JOBS_FOUND** must not read old list text).
4. **JOBS_FOUND path:** From **NO_OPENINGS** recheck (**AST-460**), transition a fixture company to **JOBS_FOUND**; run roster processing — expect **fresh Playwright** on stored **`job_site`**, confirm page, then chained parse; **WATCH** only when parse succeeds with listings.
5. **Regression — recheck:** **NO_OPENINGS** **`recheck_no_openings`** batch still Playwright-only (no AI) per **AST-460**.
6. **Admin (optional):** Manage Tasks — **`select_job_page`** has **`run_next`** → **`parse_job_list`** where migration applied (`database.py` seed).

If testing fails on `dev`:
```bash
git reset --hard origin/dev
```

— Chuckles

#### chuckles — 2026-05-24T01:35:01.489Z
## do-all-the-things — run complete (partial)

**Parent:** [AST-461](https://linear.app/astralcareermatch/issue/AST-461/split-roster-locate-and-parse-job-list-run-next-job-list-cache)

**Children:**
| Ticket | Title | Status | Assignee |
|--------|-------|--------|----------|
| AST-469 | Roster locate/parse split: run_next, JOB_LIST_VISIBLE, JOBS_FOUND path | **Tests Ready** | Hedy |

### Completed path
- **Dispatch:** 1 child (Hedy); `ftr/AST-461-split-roster-locate-and-parse-job-list-run-next-job-list-cache` + `sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path`
- **plan-astral** → **Plan Ready** (Hedy)
- **validate-plan** → **Plan Approved**
- **build-astral** → **Code Complete** (sub tip through Hedy feat + Betty QA commits)
- **qa-astral** → **Tests Ready** + manifest

### Stalled / needs Susan or integration hygiene
- **test-astral:** Betty/Hedy targeted manifest **3/3 pass** (`TestAst469ResolveRunNextLive`, `TestAst469LocateParseResolver`, `test_jobs_found_dispatch_pass_fail_ast469`).
- **Full** `./scripts/testing/run_component_tests.sh` on **`dev-hedy`** after merge sub **`8cf428a7`**: **893 passed, 19 failed** — failures cluster in **consult/gazer/board/cover-letter** tests ( **`dev-hedy` vs `origin/dev` integration drift**, not roster AST-469 asserts). Chuckles fixed two test-layer bugs on sub (`resolve_tokens` NameError + monkeypatch recursion); published **`8cf428a7`**.
- **review-astral / resolve-astral / prep-uat:** **not run** (blocked on **Tests Passed**).

### Engineer worktrees
- **Ada/Katherine:** `git merge origin/dev` conflicts on **`dev-ada` / `dev-kath`** — reported via **check-linear**; reconcile before next ticket.

### prep-uat
- **Skipped** — child not **User Testing**.

### Sub publish tip
`origin/sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path` @ **8cf428a7**

**Next:** Hedy **`test-astral`** after **`dev-hedy`** merges **`origin/dev`** cleanly (or Betty widens manifest / fixes consult shims if failures are test-layer). Then Radia → Hedy resolve → Chuckles **prep-uat**.

— Chuckles

#### ada — 2026-05-24T01:14:11.381Z
[check-linear]

- **§0a — blocked:** On `astral-ada`, `git fetch origin` → `git checkout dev-ada` → `git merge origin/dev` hit **content conflicts** (branch was **ahead 30 / behind 50** vs `origin/dev`). **`git merge --abort`** — `dev-ada` back to pre-merge HEAD. **Conflict paths:** `docs/ASTRAL_TEST_BIBLE.md`, `src/ui/api/api_boards.py`, `src/utils/config.py`, `tests/component/core/test_agent.py`, `tests/component/core/test_candidate.py`, `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`, `tests/component/ui/api/test_api_boards.py`, `tests/component/utils/test_config.py`. Needs Susan/Chuckles or a dedicated integration pass before `dev-ada` can carry **merge integration line** cleanly (per **check-linear** / **orientation-astral** — **merge**, not rebase, unless Susan directs).

- **§0b (`@ada`):** `list_issues` **`query: "@ada"`**, **Team Astral**, **`includeArchived: true`**, paginated to **`hasNextPage: false`** → **34** issue ids in the union. Repeated with **`project: "Astral Roster"`** added **AST-460** (overlap with team query). **Session context:** also read threads on **AST-461** (this parent) and **AST-469** (child; **Plan Approved**, assignee **Hedy**).

- **§1 (assignee add-on):** Session note **“assigned issue ids: (none)”** + **Astral Roster** — no Ada assignee backlog there (**AST-469** → Hedy; **AST-461** → Chuckles). **`list_issues` with `assignee: "me"`** still errors from this MCP client (JSON); no surrogate assignee rows required Ada thread work this pass.

- **§2–§4:** **`list_comments`** on the full **34-id** union **plus** **AST-461** / **AST-469**. **No** comment that is (1) not by **Ada**, (2) **after** the latest **`[check-linear]`** / Ada baseline **on that issue** where that pattern exists, and (3) **`@ada`** or clearly requiring **Ada**’s reply **still open**. Latest **AST-461** / **AST-469** traffic is **Chuckles** dispatch + plan validation + **Hedy** plan handoff — **no `@ada`**.

- **Happy path / publish ref (info only):** **AST-469** → `origin/sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path` (per Chuckles dispatch). **Ada** is **not** on this build; no **`plan-astral` / `build-astral` / `test-astral` / `resolve-astral`** from this pass.

- **§6:** On **`dev-ada`**, **not** merged with **`origin/dev`** until §0a blocker is resolved.

#### chuckles — 2026-05-24T01:07:09.863Z
## Dispatch — Chuckles

Dispatched **1** child ticket from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-469 | Roster locate/parse split: run_next, JOB_LIST_VISIBLE, JOBS_FOUND path | Hedy | `sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path` | — |

**Parent branch:** `ftr/AST-461-split-roster-locate-and-parse-job-list-run-next-job-list-cache`

**Publish refs (for agent prompts):**
- AST-461 → `origin/ftr/AST-461-split-roster-locate-and-parse-job-list-run-next-job-list-cache`
- AST-469 → `origin/sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path`

**Assignment rationale:**
- **Hedy:** Roster core (`roster.py`), `find_job_page` / `select_job_page` / `parse_job_list`, batch dispatch, `run_company_task` — single coherent slice.

Parent **In Progress**, assignee Chuckles. — Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
