<!-- linear-archive: AST-300 archived 2026-06-23 -->

## Linear archive (AST-300)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When a candidate approves a recommended job for artifact work, Astral must produce a **job-tailored resume draft** — structured JSON keyed to that candidate's section catalog — without Susan hand-copying base resume content for every application. This parent epic closes the loop from **BUILD_ARTIFACTS** (explicit UI approval after the job analysis report at RECOMMENDED) through the multi-agent resume chain, persistence on the job record, and a candidate-editable draft in the Job Analysis Report before apply/skip actions.

Much of the plumbing already landed (daisy-chain execution, dispatch entry at `contemplate_job`, tracker save helpers, prompt authoring, per-candidate structure). This definition re-scopes AST-300 after **AST-477** so remaining work is **end-to-end integration and UAT**, not re-deciding architecture.

## Functional scope

* **Lifecycle gate:** Resume artifact generation runs only for jobs in **BUILD_ARTIFACTS** — set by the candidate's explicit approval action on a **RECOMMENDED** job (see **AST-478**). No dispatch task may enter BUILD_ARTIFACTS automatically.
* **Dumb chain execution:** Batch runner claims BUILD_ARTIFACTS jobs and starts the resume chain at the configured entry task (`contemplate_job`). Hop order, agents, and prompts are wired via **Manage Tasks** `run_next` links (**AST-313** / **AST-450**) — product code does not encode an ordered step list.
* **Job-scoped resume content:** The terminal resume-craft hop produces JSON stored in `job_data.artifacts.resume_content`. Keys are the candidate's **enabled section ids** from `artifacts.resume_structure` (**AST-477**); no orphan keys outside that catalog.
* **Contact snapshot:** Contact/header section values are copied into `resume_content` at persist time as a point-in-time snapshot (**AST-477** Q4). Job-tailoring agents do not invent or rewrite contact fields; snapshot reflects base resume / structure at craft time.
* **Base resume in chain context:** Early chain hops may read the candidate's base resume via cache/chain tokens so agents start from current base content; revised resume text flows to later hops through `run_next` token pass-through — not a separate code-orchestrated "promotion" step.
* **Success and failure states:** On successful chain completion, the job lands in **CANDIDATE_REVIEW** with a populated draft. On failure, the job lands in **BUILD_FAILED** (or the configured error holding state) with no partial publish unless Susan's prompt chain explicitly defines otherwise.
* **Candidate draft editing:** The Job Analysis Report exposes the resume draft for review and edit; saves round-trip to `job_data.artifacts.resume_content` before the candidate marks Applied or Skip.
* **Print/render handoff:** Saved `resume_content` is consumable by the resume HTML builder and print route using the candidate's structure for section order and titles (**AST-518**).
* **Debug traceability (backend):** When a BUILD_ARTIFACTS dispatch run has debug enabled, each chain hop logs per **AST-538** / Code Rules Style D: index header (`index N/M`, task key, outcome) and substantive detail lines prefixed `|`; payloads over 50 lines truncate (first 15, omission count, last 15). Per-hop execution history rows remain inspectable (**AST-528** family).

## Boundaries

* **Resume only** — cover letter artifact pipeline (**AST-301**, canceled) is out of scope; cover letter chain hops may still exist in Manage Tasks but are not part of this parent.
* **Does not define candidate structure** — section catalog, Base Resume Content tabs, and `craft_resume_base` belong to **AST-477** / **AST-517–519** (Done). This epic consumes structure, does not redefine it.
* **Does not author prompts** — Manage Tasks prompt prose and `run_next` wiring remain Susan's work under **AST-313** (Done). Code registers task keys only (**AST-450** pattern).
* **Does not build the job analysis report from scratch** — synthesis at RECOMMENDED is **AST-478** (Done); modal shell is **AST-307** (Done). Structure-driven resume **draft tabs** in the report may require a sibling UI ticket if **AST-307** panels still assume global section keys.
* **Does not inject contact at render-only time** — superseded by structure snapshot model (**AST-477**); builder may still overlay live profile on render, but job artifact stores the snapshot used for that application.
* **No ordered pipeline arrays in config** — forbidden by **AST-450** / Code Rules config-as-truth; chain choreography stays in `agent_task.run_next`.
* **Must not break** existing consult path (DO→GET→LIKE→analysis_upshot→RECOMMENDED), candidate action states (**AST-302** / **AST-311**), or base resume editing (**AST-519**).

## Acceptance criteria

1. A job at **RECOMMENDED** does **not** start the resume chain until the candidate's explicit approval sets **BUILD_ARTIFACTS**.
2. A BUILD_ARTIFACTS job claimed by the artifact dispatch produces a complete resume chain run (all configured hops through the terminal resume-craft task) and persists `job_data.artifacts.resume_content`.
3. Persisted `resume_content` keys are a subset of the candidate's enabled structure section ids; contact sections present match the snapshot rules from **AST-477**.
4. On chain success, the job is **CANDIDATE_REVIEW** and the Job Analysis Report shows editable resume draft content loaded from `resume_content`.
5. Candidate edits in the report save back to `job_data.artifacts.resume_content` and appear in the resume print/preview output for that job.
6. On chain failure, the job is **BUILD_FAILED** (or configured error state) and no false CANDIDATE_REVIEW draft is shown.
7. With debug enabled on the dispatch run, app logs show per-hop Style D index lines for the resume chain; Execution History lists inspectable per-hop rows (**AST-528**).
8. A second candidate with a different section catalog receives job `resume_content` keyed only to their catalog — no cross-candidate section leakage.

## Dependencies and blockers

* **Done — foundations:** **AST-296** (BUILD_CONFIG), **AST-303** (daisy-chain `do_task`), **AST-304** (chain tokens), **AST-302** (artifact job states), **AST-450** (task key registry), **AST-513** (job analysis tokens).
* **Done — structure pivot:** **AST-477**, **AST-517**, **AST-518**, **AST-519** (candidate structure storage, builder/tracker filtering, base resume UI).
* **Done — upstream gate:** **AST-478** (RECOMMENDED analysis report; BUILD_ARTIFACTS UI-only entry).
* **Done — prompt chain:** **AST-313** (+ **AST-516** / **AST-520** anticipate_scan hop).
* **Done — prior children (pre-rescope):** **AST-370** (chain wiring), **AST-371** (persistence + dispatch trigger) — may need gap-fill tickets if UAT finds structure misalignment.
* **Related (consume, do not redo):** **AST-307** (report modal), **AST-294** / **AST-298** (builder + print routes), **AST-528** (per-hop execution history).

## Open questions

1. **Done-child gap-fill vs UAT-only:** **AST-370** and **AST-371** completed before **AST-477**. Should this parent dispatch **new child tickets** only for verified gaps (e.g. finalize schema, report UI tabs), or treat existing Done children as sufficient and limit scope to Susan UAT sign-off?
2. **Report resume panel:** Should structure-driven draft tabs (mirroring **AST-519** Base Resume Content) be **in scope under AST-300** or a separate enhancement under **AST-307**?
3. **Partial chain failure:** If a mid-chain hop fails after an earlier hop wrote advisory JSON but before `finalize_job_resume`, should the job remain BUILD_FAILED with no `resume_content`, or is any intermediate persistence acceptable?

---

## Original brief

Configure and run a daisy-chain multi-agent pipeline via do_task() to produce structured JSON resume content tailored to a specific job. Stored in job_data.artifacts.resume_content (shape defined in BUILD_CONFIG.artifact_shapes). Base resume content is cached for early agent passes then promoted (replaced in its cache slot) with the revised version so later agents never evaluate stale content. Pipeline triggered by batch runner when job reaches RECOMMENDED state. Agents produce a draft — candidate reviews and edits in the Job Analysis Report UI tabbed editor before generating final output. Agents never write contact details; [builder.py](<http://builder.py>) injects those from candidate_data.profile at render time.

### Comments

#### chuckles — 2026-06-06T04:33:02.197Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-591** | UAT hit **405** because `POST /api/jobs/<id>/generate_artifacts` was never registered on the `origin/ftr/AST-300-build-resume-artifact` integration line (Flask only exposed GET on `/<job_id>`). Added AST-562 `generate_artifacts` and `cancel |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-06T04:33:01.756Z
## Manual test steps

Re-prep after fix-uat; no re-audit.

**Prereq:** Local `dev` @ `7e3824fd` (land-ftr AST-591). Restart app if running.

### AST-591 — Generate Artifacts → BUILD_ARTIFACTS
1. Jobs → **Recommended**; click a **RECOMMENDED** job row → Job Analysis Report opens.
2. Click **Generate Artifacts**.
3. **Expected:** `POST /api/jobs/<id>/generate_artifacts` returns **200** (not 405); modal **closes**; job appears under **In Progress** / **BUILD_ARTIFACTS** on Recommended.
4. Run artifact batch (or wait for dispatch); job reaches **CANDIDATE_REVIEW**.
5. Open job from ready section → JAR shows editable resume/cover text tabs (not empty pre-build shell).

### Regression (prior fix-uat)
6. **AST-587:** Row click opens Job Analysis Report, not Job Detail.
7. **AST-581:** Preview Materials → resume + cover HTML tabs.

`origin/ftr/AST-300-build-resume-artifact` @ `55c6687a` · local `dev` @ `7e3824fd`.

— Chuckles

#### chuckles — 2026-06-06T04:28:18.560Z
## Git (UAT bugs — authoritative)

| Ticket | `origin/…` | Assignee | Status |
|--------|------------|----------|--------|
| AST-591 | sub/AST-300/AST-591-uat-generate-artifacts-must-transition-job-to-build-artifacts-405-wrong-ux | Katherine | Todo |

— Chuckles

#### susan — 2026-06-06T04:25:53.106Z
No, the flow should be:

Recommended List -> Click a job -> view the job analysis report -> Click "Generate Artifacts" -> Job transition to "BUILD_ARTIFACTS", modal closes with job in "In Progress" -> Dispatch catches and builds artifacts, sets the job state to ready (I can't remember the exact state name), and when the user clicks the job from the READY section of the Recommended page, it includes the resume and cover letter TEXT for the candidate to EDIT.

#### chuckles — 2026-06-06T04:19:30.249Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-587** | Recommended list row opens Job Detail instead of Job Analysis Report |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### susan — 2026-06-06T04:18:00.099Z
@chuckles I think "Generate Artifacts" button is supposed to do a job state transition to "BUILD_ARTIFACTS", not open the artifacts that haven't been built yet.

#### chuckles — 2026-06-06T04:16:02.741Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-581** | Preview Materials button + resume/cover HTML preview tabs in JAR |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### susan — 2026-06-06T03:56:40.740Z
@chuckles Bummer!  Please figure out why the generate_artifacts api call threw a 405 error.

127.0.0.1 - - \[05/Jun/2026 20:49:34\] "**POST /api/jobs/9eed9a79-cd09-47bf-8f05-a500acb01088/generate_artifacts HTTP/1.1**" 405 -

127.0.0.1 - - \[05/Jun/2026 20:49:44\] "GET /api/admin/dispatch_ledger?date_from=2026-06-05 HTTP/1.1" 200 -

127.0.0.1 - - \[05/Jun/2026 20:49:44\] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -

127.0.0.1 - - \[05/Jun/2026 20:49:48\] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -

#### chuckles — 2026-06-06T01:42:28.363Z
## Manual test steps

Re-prep after fix-uat; no re-audit.

**Prerequisites:** Candidate with resume structure (AST-477), at least one RECOMMENDED job with analysis report; restart app if already running.

### AST-587 (regression fix)
1. Open **Jobs → Recommended**.
2. Click a job **row** (not only the action buttons). **Expected:** `JobAnalysisReportModal` opens (report view), **not** `JobDetailModal`.

### AST-581 (Preview Materials)
3. From the Job Analysis Report, use **Preview Materials** (or equivalent).
4. **Expected:** Dual preview — resume HTML tab and cover letter HTML tab.

### AST-553 (JAR resume draft tabs)
5. Open a job in **CANDIDATE_REVIEW** with populated `resume_content`.
6. **Expected:** Structure-driven resume draft tabs in JAR; edit a section and save; reload and confirm persistence.

### AST-552 / AST-551 (pipeline)
7. On a RECOMMENDED job, explicit approval → **BUILD_ARTIFACTS** only (no auto-dispatch).
8. Run artifact batch; **Expected:** chain completes → **CANDIDATE_REVIEW** with structure-keyed `resume_content`; on failure → **BUILD_FAILED**.

`origin/ftr/AST-300-build-resume-artifact` @ `2c20732a` · local `dev` @ `f61ffdaa` (§8 land-ftr). Five child `sub/*` branches deleted.

Reset after UAT: `git reset --hard origin/dev` (after finish-up push).

— Chuckles

#### chuckles — 2026-06-06T01:39:00.919Z
[fix-uat] blocked: rollup AST-587 — merge conflict on `origin/ftr/AST-300-build-resume-artifact` (JobsRecommended.tsx, test_JobsRecommended.test.tsx, docs/ASTRAL_TEST_BIBLE.md).

@Katherine Johnson — product + Vitest hunks (restore row → JobAnalysisReportModal).
@Betty White — bible hunk.

Chuckles will re-run rollup-child then prep-uat after fixes land.

— Chuckles

#### chuckles — 2026-06-05T23:20:44.312Z
## Git (UAT bugs — authoritative)

| Ticket | `origin/…` | Assignee | Status |
|--------|------------|----------|--------|
| AST-587 | sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report | Katherine | Todo |

— Chuckles

#### susan — 2026-06-05T20:31:08.656Z
Whatever we just pushed to local dev blew away the "pretty" job report modal as the link from the Recommended list.  FIX THIS.

#### chuckles — 2026-06-05T20:18:17.052Z
## Manual test steps

**Prereq:** Local `dev` @ `bee17675` (land-ftr AST-300 + AST-581 UAT fix). Restart app if running.

### AST-551 / AST-552 — resume chain + persistence
1. Candidate with structure-enabled sections → job at **RECOMMENDED** → open Job Analysis Report → **Generate Artifacts** (not automatic).
2. Confirm job moves **BUILD_ARTIFACTS** then completes to **CANDIDATE_REVIEW** with `job_data.artifacts.resume_content` keys matching enabled structure ids only.
3. Force chain failure (if test env allows) → job lands **BUILD_FAILED**, no false draft in JAR.

### AST-553 — structure-driven draft tabs
4. At **CANDIDATE_REVIEW**, JAR shows resume draft tabs mirroring candidate structure; edit a section → save → reload modal → edits persist in `resume_content`.

### AST-581 — Preview Materials (UAT fix)
5. At **CANDIDATE_REVIEW** (or when resume/cover artifacts exist), JAR header shows **Preview Materials**.
6. Click → modal with **Resume** and **Cover Letter** tabs; each loads separate server HTML in iframe (`/candidate/resume/<job_id>` resume-only; `/candidate/cover/<job_id>` cover-only).
7. Cover tab hidden/disabled when no cover letter content.

### Print / regression
8. Resume print/preview reflects saved draft content and candidate structure order (**AST-518**).
9. Second candidate with different structure catalog → no cross-candidate section leakage in generated `resume_content`.

`origin/ftr/AST-300-build-resume-artifact` @ `2fa0b18e` · local `dev` merged (§8). Reset: `git reset --hard origin/dev` after UAT sign-off path via finish-up.

— Chuckles

#### hedy — 2026-06-05T20:10:44.454Z
**[fix-uat]** ftr config repair for `JOB_BUILD_ARTIFACT_CLEAR_KEYS`.

`origin/ftr/AST-300-build-resume-artifact` @ `2fa0b18e` — restored AST-562 symbols from `origin/dev` into `src/utils/config.py` (`JOB_BUILD_ARTIFACT_CLEAR_KEYS`, `JOBS_RECOMMENDED_*` manifest keys, `take_jd`, `RECOMMENDED` ← `BUILD_ARTIFACTS` prior_state). Component subset `test_tracker` + `test_builder`: 73 passed, collection clean.

#### chuckles — 2026-06-05T20:05:28.531Z
[fix-uat] blocked: rollup merge conflict rolling AST-581 into `origin/ftr/AST-300-build-resume-artifact`.

Conflict in:
- `docs/ASTRAL_TEST_BIBLE.md`
- `tests/component/ui/api/test_api_jobs.py`

@Betty White — bible + test tree paths above.
@Katherine Johnson — product overlap in `test_api_jobs.py` if any.

Chuckles will re-run `rollup-child AST-581` after fixes land on publish ref.

— Chuckles

#### chuckles — 2026-06-05T19:52:19.745Z
## Git (UAT bugs — authoritative)

| Ticket | `origin/…` | Assignee | Status |
|--------|------------|----------|--------|
| AST-581 | `sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar` @ `ff778766` | Katherine | Todo |

— Chuckles

#### susan — 2026-06-05T19:50:04.876Z
Thanks, Chuckles.  Please run fix-uat on 581 and reassign 300 when it's ready for me to test again.

#### chuckles — 2026-06-05T19:20:16.101Z
Bug filed: **[AST-581](https://linear.app/astralcareermatch/issue/AST-581)** — Preview Materials + dual HTML preview tabs.

#### chuckles — 2026-06-05T19:20:02.884Z
[check-linear]

@susan — **Delta vs your expected Recommended-job artifact UX** (code read on local **`dev`** @ **`ff778766`**; prep-uat baseline was **`origin/ftr/AST-300-build-resume-artifact`** @ **`859446c1`**). **5 subissues** under this parent (551/552/553 User Testing; 370/371 Done).

## Test tree first

**Use current local `dev`**, not ftr-only AST-300 rollup. Since prep-uat (**`5ec761ef`**), **`origin/dev`** lineage merged **AST-499** (**565/562/561**): tabbed JAR, **Generate Artifacts**, **Cancel**, **Apply**, manifest-driven artifact tabs. Manual steps @ **`859446c1`** describe the **older** collapsible modal (resume draft block only at **`CANDIDATE_REVIEW`**, no generate button).

| Ref | SHA | What you get |
|-----|-----|----------------|
| AST-300 ftr (prep-uat) | `859446c1` | Backend gate + resume chain + `PUT …/resume_content`; **stub UI** |
| Local `dev` now | `ff778766` | **AST-499** report shell + generate/cancel API |

## Your flow — delivered vs gap

| Step | Expected | On `dev` @ `ff778766` | Gap? |
|------|----------|------------------------|------|
| **Generate from RECOMMENDED in JAR** | Button → **`BUILD_ARTIFACTS`** | **Yes** — header **Generate Artifacts** → `POST /api/jobs/<id>/generate_artifacts` (`api_jobs.py`, `tracker.start_artifact_build`); manifest `JOBS_RECOMMENDED_PRIMARY_ACTIONS` (`config.py`) | No (not on ftr-only) |
| **Batch builds artifacts** | Dispatch runs chain | **Yes** — `contemplate_job` at **`BUILD_ARTIFACTS`**; resume chain (`run_resume_artifact_chain_for_job`); on success → **`CANDIDATE_REVIEW`** + cover letter chain in same batch (`consult.py` `_run_cover_letter_for_job`) | No |
| **1–3 editable tabs below analysis** | Resume / cover / application | **Partial** — `report_artifact_tabs` defines 3 types (`JobAnalysisReportModal.tsx`); tabs appear **only when** `artifactHasContent` (empty until chain finishes). Resume: structure editor + `PUT …/artifacts/resume_content`. Cover + application: `PUT …/cover_letter`, `PUT …/application_responses` (**AST-565**). **Application** tab has **no** generator in `src/core` today — tab is shell-only unless content pre-exists | **Application** pipeline if you expect a 3rd generated artifact |
| **Preview Materials → two render tabs** | Button opens resume HTML + cover letter HTML | **No** — routes exist (`/candidate/resume/<job_id>` bundles cover into **one** HTML doc via `builder.build_resume`); **no** JAR button, **no** dual-tab preview UX | **Yes → Bug child filed** |

## Bug child

**Backlog Bug** under this parent: **Preview Materials** — JAR button + resume/cover HTML preview tabs (separate surfaces; wire `api_resume_html.py` / `builder.py`).

## Joan / merge conflicts (your 2026-06-03 threads)

**Yes — Joan owns merge conflict resolution**, not Chuckles. All git mutations go through **`~/.cursor/skills/git-astral/git.sh`** with **`JOAN_SESSION`**; Chuckles orchestrates, Joan executes.

**Why conflicts still happen (not a Betty “impossible” failure):**

1. **Parallel epics** land overlapping files on **`dev`** / **`ftr`** (`docs/ASTRAL_TEST_BIBLE.md`, `ArtifactEditor.tsx`, `tracker.py`, etc.).
2. **Betty** publishes bible/tests to **`origin/sub/<child>`**; **rollup** merges sub→**ftr**; **land-ftr** merges ftr→**dev**. Each step can conflict if another epic already touched the same hunks on the target ref.
3. **Polluted sub tips** (sub HEAD = post–other-epic `land-ftr` slice, not ftr+child only) make blind **`git.sh rollup`** unsafe — Joan escalates; integrate via **ftr-only cherry-pick** or engineer **refresh publish ref** first.

**Process lock:** Chuckles must **not** hand-resolve hunks. On conflict → **`[check-linear] blocked:`** with paths + **`@Betty`** (bible/tests) / **`@engineer`** (product) per **`orientation-astral`** merge routing; invoke **Joan agent** on **`astral`** with session UUID. AST-300 land-ftr succeeded at **`5ec761ef`** after Joan merged from clean **`origin/dev`** ancestry.

**Pipeline:** Not resuming **`do-all-the-things`** / rollup / prep-uat from this inbox pass (per your “DO NOT RESUME PIPELINE” note on Joan thread). Parent stays **User Testing** for your pass on **`ff778766`**.

— Chuckles

#### susan — 2026-06-05T19:16:48.202Z
@chuckles I *think* the expected behavior is that for Recommended jobs, the candidate can prompt to generate artifacts for the job from the job report modal, and that ultimately generates ONE TO THREE new job artifacts, which will appear on the job report modal below the analysis tabs, and those tabs will be editable by the candidate.  Then the candidate can Preview Materials or whatever, from a button, that will open two new tabs that will render the job resume content and the cover letter.

Can you do a quick summary to see if there's a delta in what was delivered, before I try testing this on local dev?  Treat any gaps as "bugs found" and add subissues to this ticket to resolve them.

#### chuckles — 2026-06-03T02:51:36.350Z
## Manual test steps

**Prereqs:** App running from local `dev` (merged §8). Candidate with `artifacts.resume_structure` + base resume (**AST-477/519**). Manage Tasks resume chain wired through `finalize_job_resume` with `{$BASE_RESUME}` / `{$CALLER_RESPONSE}` tokens.

### Gate & chain (AST-552 / AST-551)
1. Job at **RECOMMENDED** — resume chain does **not** start until candidate approves artifacts (`POST /api/jobs/<id>/approve_artifacts` or UI when **AST-553** button exists).
2. After approval → **BUILD_ARTIFACTS**; batch/dispatch runs chain; on success job → **CANDIDATE_REVIEW** with `job_data.artifacts.resume_content` keys ⊆ enabled structure ids; contact sections are snapshot at persist.
3. On chain failure → **BUILD_FAILED**; no false draft in report.
4. Second candidate with different structure — no cross-candidate key leakage in `resume_content`.

### JAR draft UI (AST-553)
5. Open Job Analysis Report at **CANDIDATE_REVIEW** — structure-driven resume draft tabs visible; load from `resume_content`.
6. Edit sections; save persists via `PUT /api/jobs/<id>/artifacts/resume_content`; reload shows edits.
7. Print/preview route uses saved content + structure order (**AST-518**).

### Debug (optional)
8. Dispatch with debug on — per-hop Style D log lines + Execution History rows for resume chain.

`origin/ftr/AST-300-build-resume-artifact` @ `859446c1` · local `dev` @ `5ec761ef` (land-ftr). Sub branches deleted. Restart app if already running.

— Chuckles

#### susan — 2026-06-03T01:29:36.793Z
I don't resolve those issues.  That is supposed to be Joan's exclusive domain.  Something is wrong with her skills.  What do you recommend?

DO NOT RESUME THE PIPELINE UNTIL THIS IS ANSWERED.

#### chuckles — 2026-06-03T01:28:18.267Z
@susan **prep-uat land-ftr blocked:** `origin/ftr/AST-300-build-resume-artifact` @ `859446c1` has AST-551/552/553 rolled up (rollup-child done). `git.sh land-ftr AST-300` conflicts on local `dev` (17 commits ahead — AST-484/549/550 rollup): `docs/ASTRAL_TEST_BIBLE.md`, `docs/features/foundation/ast-550-remove-parallel-stateui-manifest-fallback-in-frontend.md`, `src/ui/frontend/src/components/ArtifactEditor.tsx`. Clean merge from `origin/dev` alone succeeds — resolve local `dev` vs ftr or test from ftr worktree, then reassign Chuckles for sub/* delete + parent User Testing.

— Chuckles

#### susan — 2026-06-03T01:17:31.123Z
before we address this specific ticket, would you please confirm whether or not Joanne is supposed to be able to resolve these conflicts independently either by calling the developers that are causing the conflicts like Betty or otherwise resolving it with her best judgment so that you and I do not have to face merge conflict issues? I'm also curious why we're still having merge conflict issues about test content when Betty is supposed to give Joanne her tests and then Joanne is supposed to propagate that around so that merge conflicts are impossible. Can you explain what's going on?

#### chuckles — 2026-06-03T00:47:04.155Z
@susan **rollup-child AST-552 blocked:** `git.sh rollup` merge conflict merging `origin/sub/AST-300/AST-552-build-artifacts-gate-persistence` into `origin/ftr/AST-300-build-resume-artifact` — `docs/ASTRAL_TEST_BIBLE.md`, `docs/features/artifacts/ast-551-structure-aligned-resume-chain.md`, `src/core/agent.py`, `src/core/tracker.py`, `tests/component/core/test_tracker.py`. AST-551 rolled up @ `37a853d5`; AST-553 not rolled yet. Resolve ftr merge (Betty for bible; engineers for product overlap), then reassign Chuckles to resume prep-uat.

— Chuckles

#### chuckles — 2026-06-03T00:06:56.592Z
@susan Pipeline blocked at Betty qa stage 7 — **AST-551** Tests Ready; **AST-552** / **AST-553** still Code Complete (orchestration interrupted before Betty finished). Also confirm Manage Tasks resume `run_next` chain ends at **`finalize_job_resume`**. Reassign parent to Chuckles when ready to resume.

— Chuckles

#### chuckles — 2026-06-02T22:28:56.758Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-300 (parent) | ftr/AST-300-build-resume-artifact |
| AST-551 | sub/AST-300/AST-551-structure-aligned-resume-chain |
| AST-552 | sub/AST-300/AST-552-build-artifacts-gate-persistence |
| AST-553 | sub/AST-300/AST-553-jar-resume-draft-tabs |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `0ca056cb-ffe4-4797-b7fa-a80108f0895c` | AST-300 (parent) | git |
| Ada | `66e70e9c-f93d-40f1-94b3-b8da9acbfe3c` | AST-551 | engineer |
| Betty | `a81857c7-23da-41bb-afa0-df3266662259` | AST-551 | qa |
| Radia | `d90e1774-b87c-4055-9fda-8cea06f3c0bc` | AST-551 | review |
| Hedy | `ffe6c2f9-b0a6-4fdb-a4fc-7906c5decac7` | AST-552 | engineer |
| Betty | `b7ebc398-90ab-43f2-88ac-2a22e6df38c8` | AST-552 | qa |
| Radia | `b84c25d8-d3ff-4734-9c6c-24117686385f` | AST-552 | review |
| Katherine | `cdf692b9-f778-4c86-adf8-120aaed44d41` | AST-553 | engineer |
| Betty | `921972fd-1ee8-46ce-825c-9240000f6b51` | AST-553 | qa |
| Radia | `804245f6-d2f1-41b1-83f4-56dac89f653b` | AST-553 | review |

**blockedBy:** AST-552 ← AST-551; AST-553 ← AST-552

**Parent:** AST-300

— Chuckles

#### chuckles — 2026-06-02T21:06:53.174Z
@susan Yes — the prepended definition is in the Description (your original brief preserved below the `---`). Three **Open questions** there still need your call unless you want to waive them and decide at dispatch/UAT.

**Approval signal for dispatch:** move AST-300 to **Todo** and assign **Chuckles**. I won't dispatch children until that.

— Chuckles

#### susan — 2026-06-02T21:05:52.688Z
I think this one is ready for you, now, yes?

#### chuckles — 2026-06-02T20:03:57.414Z
@susan — three open questions on the Description need your call before dispatch:

1. **Done-child gap-fill vs UAT-only:** AST-370 and AST-371 landed before AST-477. New child tickets for verified gaps only, or UAT sign-off on existing Done work?
2. **Report resume panel:** Structure-driven draft tabs — in scope under AST-300 or a separate AST-307 enhancement?
3. **Partial chain failure:** Mid-chain failure before `finalize_job_resume` — BUILD_FAILED with no `resume_content`, or allow intermediate persistence?

When you're happy with the definition, move to **Todo** and assign Chuckles for dispatch.

— Chuckles

#### chuckles — 2026-05-25T01:24:01.570Z
Moved from **User Testing** → **Backlog**, blocked by **AST-477** (Candidate Resume Structure).

Resume pipeline work resumes after structure definition is approved and dispatched. **AST-370** remains **Done**. **AST-371** also backlogged and blocked by **AST-477**.

— Chuckles

#### chuckles — 2026-05-22T17:27:11.749Z
## UAT Ready — Chuckles (prep-uat — Astral Artifacts)

Child **AST-371** work already on `origin/ftr/AST-300-build-resume-artifact` (sub branch previously deleted). Refreshed **local `dev`** from ftr.

**Parent branch:** `origin/ftr/AST-300-build-resume-artifact`

**Children:** **AST-370** Done (on ftr); **AST-371** User Testing (merged to ftr earlier)

Local `dev` merged (prep-uat §8). Restart the app if running, then test.

`ftr` tip: `7b962ab3` · local `dev` merge: `209357db` (in rollup `ed879a6b`)

## Manual test steps

**Prerequisites:** Candidate with a job that can reach **BUILD_ARTIFACTS** / **RECOMMENDED**; `craft_job_resume` prompts configured (AST-313 may still be Todo — smoke with existing prompts).

1. **Dispatch trigger** — From Scheduled Actions or batch path, confirm a job at **BUILD_ARTIFACTS** runs the resume pipeline (`craft_job_resume` / `run_resume_artifact_chain_for_job`).
2. **Persistence** — After successful run, inspect job data (UI Job Analysis Report or DB): `job_data.artifacts.resume_content` populated with structured JSON (no contact fields in artifact body).
3. **Job Analysis Report** — Open a recommended job → Resume Draft panel shows content; edit/save round-trip works.
4. **Print/HTML** — Open resume render route (`/candidate/resume/<job_id>`) in new tab; contact fields from profile injected; print preview reasonable.
5. **Base resume** — `/candidate/resume/base` still renders candidate base resume artifact.
6. **Regression** — Cover letter dispatch is **AST-301** (separate ticket); resume batch on this rollup also invokes cover letter when resume succeeds (integrated on `dev`).

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-05-19T21:05:23.146Z
## Manual test steps — UAT (AST-300)

**Scope:** Resume artifact daisy-chain (`craft_job_resume` + `run_next` hops) → `job_data.artifacts.resume_content`. Children: **AST-370** (chain/tokens), **AST-371** (persistence + `BUILD_ARTIFACTS` dispatch).

**Prerequisites**
1. App running on local **`dev`** (restart after pull).
2. Test **candidate** with: populated **base resume** (`candidate_data.artifacts.base_resume`), profile contact fields, and **Manage Tasks** prompts wired for the resume chain (**AST-313** — `craft_job_resume` and its `run_next` chain must exist and be authored).
3. At least one **job** that has completed **consult_like** (state **`BUILD_ARTIFACTS`**) with JD + company website content, or run the consult pipeline through **PASSED_GET** so LIKE pass lands the job in **`BUILD_ARTIFACTS`**.

---

### A. Dispatch + pipeline (AST-371)

1. Open **Scheduled Actions** (admin dispatch). Confirm a row exists for **`craft_job_resume`** with trigger **`BUILD_ARTIFACTS`** and **Avail > 0** for your test candidate.
2. **Run** that dispatch row (manual batch). Watch **Execution History** — batch should complete without technical error.
3. In DB or job API (`GET /api/jobs/<id>`), confirm **`job_data.artifacts.resume_content`** is populated as a JSON object matching **`BUILD_CONFIG.artifact_shapes.resume_content`** keys (`professional_summary`, `experience`, etc.).
4. Confirm job state moved appropriately (typically toward **`CANDIDATE_REVIEW`** when the chain completes successfully — not stuck in **`BUILD_FAILED`** unless the run genuinely failed).
5. **Idempotency / retry:** Re-run **`craft_job_resume`** on the same job only if product allows; note whether content is replaced cleanly (no corrupt merge / empty overwrite).

### B. Daisy-chain behavior (AST-370)

6. In **agent_responses** (or debug output if enabled), confirm **multiple hops** ran for the job (`craft_job_resume` first hop, then `run_next` steps per Manage Tasks config) — not a single orphaned response.
7. Confirm **cache promotion:** later hops should not re-use stale base-resume text from early cache slots (spot-check agent logs or intermediate responses if you have them).
8. On a forced failure (e.g. temporarily break one hop prompt), confirm the job lands in **`BUILD_FAILED`** (or configured error path) and **does not** publish a half-shaped `resume_content` unless spec says otherwise.

### C. Render / print (builder — AST-294 / AST-298)

9. With `resume_content` present, open **`/candidate/resume/<astral_job_id>`** (authenticated). HTML should render; **contact block** comes from **profile**, not from agent-invented fields in the artifact JSON.
10. Open **`/candidate/resume/base?candidate_id=<id>`** — base resume HTML still works.
11. Use browser **Print to PDF** — layout readable; accent color from base resume prefs (**AST-297**) if set.

### D. Recommended list + JAR (integration)

12. **Recommended Jobs** — job appears while in **`BUILD_ARTIFACTS`** / **`CANDIDATE_REVIEW`** (per **`RECOMMENDED_JOB_STATES`**).
13. Open **Job Analysis Report** from a recommended row — modal loads job summary; if resume editor panels are not yet in JAR UI, verify artifact via API/DB in step 3 (UI polish may be **AST-307** follow-on).

### E. Boundaries (should **not** happen)

14. Resume dispatch at **`BUILD_ARTIFACTS`** does **not** require cover letter to exist first.
15. Dispatcher/batch does **not** set **`CANDIDATE_APPLIED`** / other candidate-only states automatically.

---

**Pass:** Steps 1–4 and 9–11 succeed on a real job; chain evidence in 6–7; failures behave per 8.

**If testing fails on `dev`:** `git reset --hard origin/dev` then re-merge the feature branch Susan gave you for UAT.

— Chuckles

#### chuckles — 2026-05-18T23:48:34.303Z
## UAT Ready — Chuckles

Rebuilt **`ftr/AST-300-build-resume-artifact`** on **`origin/dev`** (was on stale `main`). Cherry-picked product commits only — **did not** merge stale `sub/*` branches.

**`tracker.py`:** kept **AST-309/311** helpers from `dev` + added **`persist_job_artifact_from_parsed`** (shared with 301).

**Cherry-picks:** `acc1050c` (feat 371), `0ee62f82` (test), `fe785922` (resume-only test scope)

**Deleted:** `sub/AST-300/AST-370-…`, `sub/AST-300/AST-371-…`

Local `dev` merged (`9a864821`). Restart app, then test.

— Chuckles

#### chuckles — 2026-05-18T23:35:56.718Z
## prep-uat merge conflict — Chuckles (batch)

Child branch **AST-371** conflicts with the parent branch after merging siblings.

**Conflict in:** `src/core/tracker.py`

**Already merged:** AST-370 (already up to date on `ftr`)

@susan — resolve on `origin/ftr/AST-300-build-resume-artifact` or re-run prep-uat after push.

— Chuckles

#### katherine — 2026-05-18T18:42:57.028Z
[check-linear]

- Susan split comment (AST-370 Ada / AST-371 Hedy): acknowledged — resume chain integration is not Katherine scope.

— Katherine

#### chuckles — 2026-05-16T15:44:30.841Z
## Parent status — Chuckles

Moved parent to **In Progress**: child tickets are in mixed pipeline states. Susan/Chuckles board cleanup 2026-05-16.

— Chuckles

#### susan — 2026-05-04T21:35:07.976Z
**Plan doc:** `docs/features/artifacts/ast-300-build-resume-artifact.md`

**Self-assessment:**
- **Scope — MAJOR-CHANGE:** Config + core pipeline + tracker/dispatcher + UI handoff to AST-307.
- **Conf — LOW:** Many blockers (296/302/303/304/370/371) must merge before late stages.
- **Risk — HIGH:** `job_data` / dispatch correctness is load-bearing.

GitHub: https://github.com/susansomerset/astral/blob/chuckles/ast-300-build-resume-artifact/docs/features/artifacts/ast-300-build-resume-artifact.md

— Katherine (a-plan-linear)

#### susan — 2026-05-04T21:30:27.317Z
[check-linear]

Acknowledged 2026-04-29 split / ownership comment (AST-370, AST-371; Katherine parent label). No Katherine code or doc action taken on this thread — ticket stays **Todo** until you queue it for planning/build.

— Katherine

#### susan — 2026-04-29T18:27:43.356Z
Split for ownership + closure sequencing:
- **AST-370** — Ada: do_task chain/token integration
- **AST-371** — Hedy: tracker persistence + batch trigger integration
- **Parent AST-300 label is Katherine** because UI is final integration/validation touchpoint.

Dependency links were synced to local graph model (hard blockers in `blockedBy`; process links in `relatedTo`).

— Chuckles

---

# Build Resume Artifact

**Linear:** https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact  
**Feature branch:** `<agent>/ast-300-build-resume-artifact`

Daisy-chain **`do_task()`** pipeline that produces **job-scoped** structured JSON resume content in **`job_data.artifacts.resume_content`**, shape from **`BUILD_CONFIG.artifact_shapes`** (see **AST-296**). Early passes cache base resume text in agent cache slots; a **promotion** step replaces that slot with revised content so later agents never read stale text. Trigger when job reaches **`RECOMMENDED`** (exact trigger wiring in **AST-371** with tracker). **AST-370** owns do_task/token chain plumbing; **AST-371** owns persistence + dispatch trigger. This parent plan is the **integration contract** Katherine uses to validate end-to-end behavior and UI surfaces (**AST-307** tabbed editor consumes `resume_content`).

**Blocks:** **AST-301** (cover letter). **Blocked by:** **AST-296**, **AST-302**, **AST-303**, **AST-304**, **AST-371** (and **AST-370** for chain). **Related:** **AST-313**, **AST-308**.

---

## Files Changed (planned) — integration touchpoints

| File | Change | Layer |
|------|--------|-------|
| `docs/features/artifacts/ast-300-build-resume-artifact.md` | This plan (updated as children land). | docs |
| `src/utils/config.py` | `BUILD_CONFIG.artifact_shapes.resume_content` keys; `TASK_CONFIG` / `CONSULT_CONFIG` entries for each chain step (names per **AST-313** authoring). | utils |
| `src/core/agent.py` | Daisy-chain steps per **AST-303**; cache promotion per ticket spec. | core |
| `src/core/dispatcher.py` | Dispatch row for RECOMMENDED → resume pipeline batch (pattern with **AST-371**). | core |
| `src/core/tracker.py` | Read/write `job_data.artifacts.resume_content`; transition guardrails with **AST-302** states. | core |
| `src/data/database.py` | Only if **AST-371** requires schema for `job_data` blob shape — follow child plan, not duplicate here. | data |
| `ui/frontend` (Job Analysis path) | Read-only display + edit save path for draft vs final per **AST-307** plan. | ui |

Exact modules per **AST-370** / **AST-371** child plans — if a path is owned solely by a child, **do not** edit it from this branch without coordinating; this parent ticket may close after children merge and Katherine runs acceptance.

---

## Stage 1: Config and shapes (post–AST-296)

**Done when:** `artifact_shapes.resume_content` exists and matches JSON schema agreed with builder; task keys registered.

1. After **AST-296** on `dev`, add **`BUILD_CONFIG.artifact_shapes["resume_content"]`** structure per product spec (fields, required keys — no contact fields; builder injects profile contact per ticket).
2. Register pipeline **`TASK_CONFIG`** tasks (Susan-authored prompts in **AST-313**); each step lists `response_schema` / `vectors` as needed.

⚠️ **Decision:** Chain task keys and order are **single ordered list** in config (e.g. `RESUME_PIPELINE_STEPS` constant next to shapes) so dispatcher and `do_task` loop share one source of truth.

---

## Stage 2: do_task daisy-chain (post–AST-303/304)

**Done when:** One batch run walks all steps; each step reads prior step output from agent_data / structured parse; promotion replaces cache slot after designated step index.

1. Implement chain driver in **`agent.py`** (or module called from it) following **AST-303** pattern with **AST-304** tokens for cross-step references.
2. Implement **cache promotion** at the index specified in config after “base resume draft” step completes successfully.
3. On any step failure, land job in **`error_state`** from `CONSULT_CONFIG` / `TASK_CONFIG` for that step — no partial `resume_content` publish unless spec says otherwise.

---

## Stage 3: Persistence + trigger (AST-371)

**Done when:** Job in `RECOMMENDED` is claimed by resume pipeline dispatch; `resume_content` JSON written atomically with `batch_id`.

1. Merge **AST-371** implementation first when ready; this stage is **verification only** on parent branch: run one integration test path in dev/staging.
2. Confirm **`job_data.artifacts.resume_content`** matches shape; confirm idempotency if dispatch retries.

---

## Stage 4: Child AST-370 merge + token QA

**Done when:** `do_task` chain matches **AST-370** acceptance checklist (link in Linear).

1. Rebase/merge **AST-370** branch; resolve conflicts in `agent.py` / token resolver only with Ada’s intent preserved.
2. Run targeted **`py_compile`** and one dry-run batch in dev environment if available.

---

## Stage 5: UI handoff (AST-307)

**Done when:** Job Analysis Report shows resume draft tab populated from `job_data.artifacts.resume_content`; candidate edits round-trip per **AST-307** plan.

1. Coordinate field names with **AST-307** plan doc — no duplicate JSON paths.
2. Katherine validates UI + save flows after backend merged.

---

## Stage 6: Verify

**Done when:** End-to-end: job hits `RECOMMENDED` → pipeline runs → draft appears in report → candidate edit → final state written per **AST-302**.

1. `python3 -m py_compile` on all changed `.py`.
2. Manual or scripted integration checklist in Linear comment.

---

## Execution contract (for the developer agent)

Execute in order; if **AST-303**/`304`/`371`/`370` not on `dev`, **stop at the stage boundary** and comment on **AST-300** with blocking issue id — do not half-merge.

---

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
Config, core agent/dispatcher/tracker, database possibly, and UI integration across multiple tickets.

**Conf — `LOW`**  
Many upstream tickets must land first; sequencing and merge conflict risk are the main unknowns until dependencies are green.

**Risk — `HIGH`**  
Bad pipeline logic corrupts `job_data` or fires wrong dispatch waves; high blast radius on hiring data.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §2.1 | All literals in `config.py`; no env fallbacks for non-secrets. |
| §2.4 | Dispatch uses `batch_id` pattern from **AST-371** / dispatcher norms. |
| §3.3 | Core → data/external only through allowed imports. |

**Conflicts:** None once dependency tickets’ plans agree on `job_data` path names.
