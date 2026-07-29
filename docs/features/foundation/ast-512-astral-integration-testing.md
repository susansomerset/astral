# AST-512 — Astral Integration Testing

<!-- linear-archive: AST-512 archived 2026-07-29 -->

## Linear archive (AST-512)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-512/astral-integration-testing  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-396

### Description

## Purpose

[AST-380](https://linear.app/astralcareermatch/issue/AST-380/astral-testing) delivered the component-test program (pytest/Vitest, branch-coverage locks, Test Bible, `run_component_tests.sh`) and explicitly left **integration tests** for a later effort — `tests/integration/` is still a placeholder. Susan wants that program opened with a **very small first slice**: automated tests that exercise **more than one real layer together** (not the per-file, heavily mocked component style) so regressions that only appear across layer boundaries are caught early. The outcome is a repeatable integration tier Susan can grow over time, with **Joan** as the long-term operator who runs the suite against a known deploy target and surfaces failures back to Chuckles for triage — not a one-off script.

## Functional scope

* **Integration tier definition** — Document what counts as an integration test in Astral versus a component test (multi-layer, real in-process wiring; still distinct from manual UAT or live production checks). Betty maintains the Test Bible when this lands.
* **Harness entry point** — A **standalone** `run_integration_tests.sh` (separate from the component suite) runnable locally and in CI so engineers and Joan know which gate applies.
* **First integration scenario (v1)** — **Seeded real SQLite + authenticated candidate API round-trip** (Susan's choice between options b/c; Chuckles recommends **b** over write-then-read-back alone because it proves routing, auth, and persistence together — the seams component tests mock away). Observable pass/fail assertions; no live external I/O.
* **External I/O policy** — Default integration runs **never** call live Anthropic, Playwright, Gmail, or Google CSE. Stubs or recorded fixtures at the **external layer boundary** only; core and data run for real against the test database. Opt-in live-I/O checks stay in spike scripts outside this tier.
* **Controlled vs live I/O contract** — Document and implement a single product rule: integration mode forces controlled externals (test env / harness flag); live credentials and network calls are rejected unless an explicit opt-in path (spikes, manual ops) is used. Component tests continue using the same external mock patterns; integration tests reuse those stubs but **do not** mock core↔data or API↔core seams.
* **Fixture and environment contract** — Shared rules for test database setup, required environment variables, scheduler/background-thread gating when startup is involved, and what must **not** run in the default integration pass.
* **Growth runway** — Structure under `tests/integration/` so additional scenarios can be added incrementally without redefining the tier.
* **Joan integration operator (v2 slice)** — Reframe Joan as the **integration-test agent**: after `origin/dev` lands, Joan runs the integration harness against a **dedicated Railway test host** pinned to that deploy (never production). On failure, Joan opens a **Discussion** ticket for Chuckles with repro output — Chuckles triages (bug child, definition fix, or infra). Joan does not own product fixes.

## Boundaries

* Does **not** replace or relax the component-test program ([AST-380](https://linear.app/astralcareermatch/issue/AST-380/astral-testing)): per-file branch locks and `tests/component/` stay as-is.
* Does **not** target 100% branch coverage on production modules for integration tests; pass/fail behavioral checks only.
* Does **not** include live Anthropic, Playwright, Gmail, or Google CSE calls in the default integration suite (no API spend, no browser farm in CI).
* Does **not** include full-browser E2E, production deployment smoke, or Susan's manual UAT flows.
* Does **not** close [AST-396](https://linear.app/astralcareermatch/issue/AST-396/component-branch-coverage-databasepy-migrations-and-batchscore-paths) deferred `database.py` migration/batch branch coverage — that remains component scope.
* Does **not** require [AST-383](https://linear.app/astralcareermatch/issue/AST-383/corebootstrap-runtime-startup-orchestration-from-uiserverpy) bootstrap refactor for v1 unless Susan later chooses a boot-centric scenario.
* **v1** does **not** require Railway or Joan automation to ship — those are the **second slice** after the in-process harness and first scenario are green locally and in CI.
* Must not break existing component or frontend test gates.

## Acceptance criteria

1. `docs/ASTRAL_TEST_BIBLE.md` (and/or `docs/test-bible/` tree) describes the integration tier (location, how it differs from component tests, external-I/O policy, controlled-vs-live rule, who maintains it).
2. `tests/integration/` contains at least one automated integration test (not merely `.gitkeep`) that runs green via `run_integration_tests.sh`.
3. The first scenario uses a real test database (same family of isolation as component data fixtures), exercises at least two layers (persistence + HTTP API with auth), and uses stubbed externals only.
4. A developer can run **only** integration tests with one documented command; the component suite does not require integration tests unless explicitly combined.
5. CI (or the project's standard test script invoked in CI) can execute the integration suite and fail the build on regression.
6. Adding a second scenario later does not require restructuring the first (clear module/file layout and shared fixtures documented in the Bible).
7. **(v2 — Joan + Railway)** Documented Joan workflow: test Railway service, trigger after dev land, failure → Discussion ticket for Chuckles; Joan run is reproducible against a known deploy ref.

## Dependencies and blockers

* [AST-380](https://linear.app/astralcareermatch/issue/AST-380/astral-testing) — **Done** (component harness and Bible exist; integration was deferred here).
* None blocking **v1** start; optional adjacency: [AST-383](https://linear.app/astralcareermatch/issue/AST-383/corebootstrap-runtime-startup-orchestration-from-uiserverpy) if a boot-centric scenario is chosen later.
* **v2** depends on **v1** harness existing and a Railway **test** environment (not production) Susan provisions.

## Open questions

none.

## Decisions

* **First scenario:** **(b) seeded DB + authenticated candidate/nav API round-trip** — recommended over (c) because it validates auth + routing + persistence together; boot-only **(a)** remains valid later if scheduler gating is solved ([Susan 2026-06-02](<https://linear.app/astralcareermatch/issue/AST-512>)).
* **External I/O:** Default integration runs use stubs/recorded fixtures at the external boundary only; no live APIs in the default harness ([Susan 2026-06-02]).
* **Harness shape:** Standalone `run_integration_tests.sh` — not pytest-marker-only ([Susan 2026-06-02]).
* **Joan operator:** Joan runs integration tests and opens **Discussion** tickets for Chuckles on failure; Chuckles triages, does not fix product in the Joan pass ([Susan 2026-06-12]).
* **Railway test host:** **Yes** — a dedicated Railway **test** service pinned to the landed `dev` deploy is the right Joan target (avoids "what version am I testing?" ambiguity). **v1** ships in-process pytest first; Joan + Railway is **v2** in this epic, not a blocker for the first green scenario ([Susan 2026-06-02]).
* **Controlled vs live code:** Integration mode = real core/data/API + **stubbed** `src/external/*` **only** via shared test fixtures and an explicit env/harness flag; live I/O = opt-in spikes/scripts only, documented as out-of-band in the Bible ([Susan 2026-06-02]).
* **Delivery order:** **Slice 1** — harness + first scenario + Bible + CI. **Slice 2** — Joan skill/workflow + Railway test host wiring + failure ticketing.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-512 (parent) | ftr/AST-512-astral-integration-testing |
| AST-711 | sub/AST-512/AST-711-integration-harness-first-api-scenario |
| AST-712 | sub/AST-512/AST-712-joan-operator-railway-test-host |

| AST-818 | sub/AST-512/AST-818-post-deploy-integration-github-status |

**Epic worktree:** `astral-AST-512/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | cb9c0c20-f8b9-401e-9c56-094f0be9d373 |
| Betty | qa | 529d383f-2b13-4d43-90ad-4a55967b24f4 |
| Radia | review | 798b0fd8-adf7-4a10-94d5-61f026aef658 |

---

## Original brief

We need to build automated integration testing for the solution, but we should start very small and build out from there.   What would be a simple, meaningful integration test we could perform, and how would we implement it?

### Comments

#### susan — 2026-07-12T00:08:39.416Z
I'm moving this to PR Ready without full UAT because I have other priorities and I don't want this hangnail to last forever.

#### chuckles — 2026-07-12T00:07:26.211Z
[check-linear] User Testing — both slices yes; UAT on you (@susan)

**AST-711** + **AST-712** are implemented on **origin/dev** (children **User Testing**). **AST-818** fix-uat also landed (**User Testing**): post-deploy gate + GitHub commit status per your 2026-06-26 decisions.

**Your next action:** UAT on local **dev** — integration harness/bible sanity; for **AST-818** push to **origin/dev** (or run **`post_deploy_integration_gate.sh`**) and confirm commit status on the deployed SHA. Operator-machine cron per **POST_DEPLOY_GATE.md** is optional until you want full automation.

— Chuckles

#### susan — 2026-07-12T00:05:30.291Z
@chuckles I'm confused about the status of this ticket.  Have we implemented both slices?  What is my next action?

#### chuckles — 2026-06-27T20:43:58.770Z
[check-linear] User Testing — commit status + Joan on deploy agreed (@susan)

Aligned: **no GitHub Actions workflow for now**. `origin/dev` push redeploys astral-test + staging; Joan **integration-operator** runs post-deploy on the test host and sets GitHub **commit status** on the deployed SHA (pass/fail). Failures → new Linear Discussion ticket with full context — not empty commits from Joan.

**Next:** after your `ASTRAL_DEPLOY_ENV=test` change, next `dev` push should show the status check on that commit.

Seed data: v1 integration tests use in-process seeded SQLite — richer test-host seeding is a follow-on if needed.

— Chuckles

#### chuckles — 2026-06-26T02:54:53.473Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-818** | Post-deploy integration run with GitHub commit status on origin/dev |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-818** — _Post-deploy integration run with GitHub commit status on origin/dev_
- **Issue reported:** After `origin/dev` push, **astral-test** Railway redeploys (`ASTRAL_DEPLOY_ENV=test`) but integration tests do **not** run automatically afterward, and GitHub shows **no commit status** on the landed dev SHA (e.g. `Integration Tests Passed`). Joan must be invoked manually; failur
- **Should now:** When the **test** Railway service finishes deploying a commit from **origin/dev**:
- **Quick check (this fix only):**
  1. Land a change on **origin/dev** (Susan: push already redeploys astral-test and astral-staging).
  2. Wait for **astral-test** deploy to complete (`RAILWAY_GIT_COMMIT_SHA` matches `origin/dev`).
  3. Observe: no automatic integration run; no GitHub status on the dev commit; manual Joan invoke only.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-26T02:46:48.279Z
@chuckles  pushing to origin dev already triggers a redeploy to astral-test on railway as well as astral-staging.  Same same.  I think the commit status check fits more cleanly, if any failures are routed into new Linear tickets with full context. For now, let's not worry about github workflows yet.  If we get to proper CI/CD one day, we'll add it. but i'm just trying to get everything working right now.

#### chuckles — 2026-06-26T02:40:00.116Z
[fix-uat] blocked: open questions — need your call before bug dispatch (@susan)

1. **Trigger:** Run integration tests on **Railway test deploy only** (`ASTRAL_DEPLOY_ENV=test`), on **every `origin/dev` push** (GitHub Actions calling test host), or **both**?
2. **Results on GitHub:** Prefer **commit status check** (`Integration Tests Passed` on the dev SHA) + workflow log artifact — **or** Joan **empty commit** to `origin/dev` with log file (heavier; mutates dev history)?
3. **Scope:** Record results for **test Railway** runs only, or also mirror **in-repo CI** (`.github/workflows/integration-tests.yml`) as the status source?

— Chuckles

#### susan — 2026-06-26T02:25:00.323Z
Okay, I have set the ASTRAL_DEPLOY_ENV to `test` on that environment.  Can you wire up integration tests to perform when deployed and then push an "empty" commit to github from Joan with the tests run and their output that she can push to origin dev, so that I can see the test results in teh commit history before we open a PR to main?  Or is there a better way to do this using github tools?  Can the origin branch be updated as "Integration Tests Passed" in addition to posting the details?

#### chuckles — 2026-06-26T02:19:28.619Z
[check-linear] User Testing — seed data on Railway test host (@susan)

**Correct:** integration scenarios **do not** rely on pre-populated rows in the service's `data/astral.db`. Each pytest run uses a **temp SQLite file** (`tests/integration/conftest.py` sets `ASTRAL_DB_DIR` to a per-run tmp dir and inserts `cand-1` in the fixture). The Railway app's persistent DB can stay empty for harness runs.

**astral-test.up.railway.app** linked to **origin/dev** is the right Joan target — next smoke: `./scripts/testing/verify_integration_deploy_ref.sh` then `./scripts/testing/run_railway_integration_tests.sh` (or Joan via `integration-operator` skill).

— Chuckles

#### susan — 2026-06-26T02:18:43.122Z
@chuckles astral-test.up.railway.app is live and linked with origin dev.

Seed data is added to the test env's astral.db tables, though, correct? it's just done as part of the test execution?

#### chuckles — 2026-06-26T02:09:03.547Z
[check-linear] User Testing — integration run recording + Joan next steps (@susan)

**Where runs are recorded today**

| Surface | Record | Owner |
|---------|--------|-------|
| **Local / CI** | pytest stdout + GitHub Actions **Integration tests** workflow (`.github/workflows/integration-tests.yml`) on `dev` / `ftr/**` pushes — pass/fail only, no DB artifact | engineer CI |
| **Railway test host (Slice 2)** | Joan runs `verify_integration_deploy_ref.sh` + `run_railway_integration_tests.sh`; stdout captured in Railway deploy logs; **failure → new Linear Discussion ticket for Chuckles** (not auto-filed on pass) | Joan per `~/.cursor/skills/integration-operator/SKILL.md` |
| **Product DB** | **No** persistent integration-run table in v1 — by design (behavioral gate, not audit ledger) |

**Next steps to stand up Joan on test host**

1. You provision a dedicated Railway **test** service (not staging UAT) — checklist in `docs/integration-operator/RAILWAY_TEST_HOST.md`.
2. Set operator env vars from `env.example` (harness + auth stubs; no live external I/O).
3. Wire deploy to track **`origin/dev`** SHA (`RAILWAY_GIT_COMMIT_SHA` pin via `verify_integration_deploy_ref.sh`).
4. Joan smoke: `./scripts/testing/run_railway_integration_tests.sh` after a dev land.
5. Optional follow-on epic: structured run log (JSON artifact or `app_log` row) if you want history beyond CI/Railway logs.

**Seed data**

- **In-process tests (Slice 1):** each scenario seeds its own temp SQLite in `tests/integration/conftest.py` — no shared production seed file; add scenarios = add fixture factories in `conftest.py` / `scenarios/`.
- **Railway test host:** same harness — ephemeral DB per run unless you later add a documented `scripts/testing/seed_integration_fixtures.sh` for multi-scenario hosts (out of v1 scope; open a child if you want persistent seed on Railway).

— Chuckles

#### susan — 2026-06-26T02:07:30.798Z
@chuckles Where are we/should we record integration test runs and their results?  I believe we planned for Joan to be able to run these on a designated test host.  What are the next steps to implement that? I assume we should have that separate environment pointing at origin dev, but what about seed data generation to perform future tests?

#### chuckles — 2026-06-16T20:54:58.435Z
[check-linear] User Testing — UAT tick-list posted below (@susan)

**Prereq:** `origin/dev` deployed to Railway staging (prep-uat landed **766511f**). Local optional: `cd astral && git checkout dev && git pull origin dev`.

### Slice 1 — in-process integration tier (ship bar)

- [ ] **Harness only:** `./scripts/testing/run_integration_tests.sh` → **3 passed**, finishes in ~1s. No Vitest, no component coverage gate.
- [ ] **Component gate unchanged:** `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py` (any narrow slice) still runs without requiring integration tests by default.
- [ ] **First scenario:** seeded SQLite + `GET /api/candidates` + `GET /api/nav_config` with Bearer auth; `401` without auth — see `tests/integration/scenarios/test_candidate_nav_api.py`.
- [ ] **External I/O blocked in integration mode:** with `ASTRAL_INTEGRATION_MODE=1`, live Anthropic/Playwright/Gmail/CSE/Stytch calls raise (guards in `src/utils/integration_io.py`).
- [ ] **Bible:** `docs/test-bible/integration/README.md` describes tier vs component tests, stub policy, harness command, maintainer.

### Slice 2 — Joan operator / Railway test host (optional until you provision)

- [ ] Read `docs/integration-operator/README.md` + `docs/integration-operator/RAILWAY_TEST_HOST.md`.
- [ ] Copy operator vars from `env.example` onto the **test** Railway service (not production).
- [ ] After staging reflects landed dev: `./scripts/testing/verify_integration_deploy_ref.sh` then `./scripts/testing/run_railway_integration_tests.sh` (requires Railway CLI + linked test service).
- [ ] Joan skill: `~/.cursor/skills/integration-operator/SKILL.md` — failure → **Discussion** ticket for Chuckles.

### Out of scope for this UAT pass

- Full-browser E2E, live LLM/browser spend, production Railway.
- AST-712 live Railway proof until test host is provisioned — Slice 1 green locally/staging is enough to approve Slice 1.

— Chuckles

#### susan — 2026-06-16T20:52:56.697Z
Okay, @chuckles, my friend, I'm going to need a little tick-list of setup and clear directions how to test for this work.

#### susan — 2026-06-12T23:06:25.882Z
We also need to reframe Joan as the integration test agent, where hopefully she can run integration tests and generate linear issues for chuckles to handle if the integration tests fail.

#### chuckles — 2026-06-02T20:14:01.213Z
[check-linear]

**Your question — integration testing vs boot, in plain terms**

Yes, testing the boot/startup path is a legitimate *integration* slice — not because "boot" is magic, but because startup is where **multiple real pieces have to agree at once**: config loads, SQLite opens/migrates, `sync_agent_tasks` runs, Flask registers blueprints, scheduler hooks attach. A **component** test on one function mocks the rest and proves that function's logic; an **integration** test lets several of those layers run together and asks "does the wired-up app actually come alive and respond?"

**How it manifests in Astral (concrete)**

| Tier | What you run | What it proves | Example |
|------|----------------|----------------|---------|
| **Component** (AST-380 today) | pytest on one module with mocks | Logic inside a file | `tracker.save_job_artifact` with fake DB |
| **Integration** (AST-512 goal) | pytest starts real test DB + in-process Flask (or core bootstrap) | Layers connect correctly | App boots → `GET /api/system/health` or seeded candidate → `GET /api/candidates/<id>` returns 200 + JSON |
| **Manual UAT** | You click in the browser | Whole product feel | Recommended list + Prepare button |

A **boot integration test** does *not* mean "spin up production" or call Anthropic. It means: create an isolated test database, run the same startup path `server.py` uses (or a thin `bootstrap_runtime()` if AST-383 lands later), issue **one real HTTP request** against the in-process app, assert status + shape. Failures you catch: missing migration, import cycle, blueprint not registered, scheduler double-start — bugs unit tests miss because nothing mocks the seam.

**Is boot the best *first* slice?** Optional. Open question **#1** on the ticket lists three starters; **(b) seeded DB + authenticated API round-trip** is often the sweetest first win (proves DB + auth + routing without fighting scheduler threads). **(a) boot + read-only health/config** is smaller but still valid if you want "does the app start?" as v1. Boot-heavy tests can be flakier if the scheduler starts background threads — we'd gate that in the fixture (start app with scheduler disabled for the test harness).

**Primer video (~5 min):** [Unit and Integration testing COMPARED](https://www.youtube.com/watch?v=pf6Zhm-PDfQ) — unit = one piece in isolation; integration = pieces wired together. Maps cleanly to our component suite vs `tests/integration/`.

**Still need from you** (unchanged from prior thread): pick **first scenario** (a/b/c or other), confirm **no live external I/O** in default runs, and **harness shape** (standalone script vs pytest marker vs both). No code this pass.

— Chuckles

#### susan — 2026-06-02T19:48:02.654Z
I need a little more context about this.  Is it appropriate to do integration testing for the boot process? How does that even manifest?  This is definitely a gap in my own technical knowledge, but can you either explain it in non-engineer-but-still-technical terms, or find a YouTube primer video I should watch to appreciate the context?

#### chuckles — 2026-05-28T18:45:36.636Z
@susan — definition is on the ticket; need your call before dispatch:

1. **First scenario** — (a) boot + read-only system/config API, (b) seeded DB + authenticated candidate/nav API round-trip, or (c) one entity write then read-back — or something else?
2. **External I/O** — OK if default integration runs never call live Anthropic / Playwright / Gmail (mocks/stubs only; live stays spikes)?
3. **Harness** — standalone `run_integration_tests.sh`, pytest marker only, or both?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
