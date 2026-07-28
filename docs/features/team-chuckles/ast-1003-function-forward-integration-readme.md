# AST-1003 — Function-forward integration README

- **Linear (this ticket):** [AST-1003](https://linear.app/astralcareermatch/issue/AST-1003/function-forward-integration-readme-test-coverage-integration-testing)
- **Parent:** [AST-915](https://linear.app/astralcareermatch/issue/AST-915/test-coverage-integration-testing-discovery-first) — Test Coverage — integration testing, discovery first
- **Publish ref:** `origin/sub/AST-915/AST-1003-function-forward-integration-readme`
- **Blocks:** [AST-1004](https://linear.app/astralcareermatch/issue/AST-1004/integration-testing-adr-proposal-test-coverage-integration-testing) (ADR cites this map; do not draft ADR positions here)
- **Summary:** Rewrite `docs/test-bible/integration/README.md` so a reader validates coverage by **functionality area** (has / should-have). AST ticket ids are **citations only**, not section headings. Docs-only discovery map for Archie — no new scenarios, no CI vendor, no ADR program positions.

## Ownership split (mandatory)

Engineer pre-commit (`~/.cursor/hooks/pre-commit/engineer.sh`) blocks `docs/test-bible/*`. Ada cannot commit the target file.

| Role | Owns |
|------|------|
| Ada (`build-child`) | Verify inventory below still matches tip; Code Complete with **zero** Ada commits to `docs/test-bible/**` / `tests/**` / `src/**` |
| Betty (`qa-child`) | Replace `docs/test-bible/integration/README.md` with the **exact** Stage 2 body; publish on this publish ref |

⚠️ **Decision:** In-place rewrite of `docs/test-bible/integration/README.md` (parent AC names that README). Ada authors the full replacement in this plan; Betty lands it — same ownership pattern as AST-990 for test-tree paths. Do **not** invent a parallel map under `docs/features/` as the AC deliverable.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `docs/test-bible/integration/README.md` | Full rewrite: function-area sections (has / should-have); AST ids as citations; remove ticket-outline `### AST-711` / `### AST-712` / `### AST-818` headings | docs (bible) | Betty (qa-child) |
| `docs/features/team-chuckles/ast-1003-function-forward-integration-readme.md` | This plan | docs | Ada (plan-child) |

**Explicitly unchanged (do not edit):**

| File / area | Why |
|-------------|-----|
| `tests/integration/**` | No new scenarios; no harness fix-green |
| `docs/test-bible/README.md` | Index already points at `integration/`; no index rewrite in this ticket |
| `docs/integration-operator/**` | Joan operator contract stays there; README only links (adjacency) |
| `src/**`, CI workflows, ADR / AST-1004 content | Out of Boundaries |
| Betty unit/component ownership, `[qa-handoff]` rules | Do not modify |

## Inventory (planner read — build verifies only)

Current tip facts the rewrite must preserve as **has** coverage or adjacency:

1. **Scenarios on disk:** only `tests/integration/scenarios/test_candidate_nav_api.py` — three tests: list candidates, nav_config state gate (`ACTIVE_SEARCH` vs `NEW_CANDIDATE`), unauthenticated 401.
2. **Harness:** `./scripts/testing/run_integration_tests.sh`; fixtures in `tests/integration/conftest.py`; minimal Flask app = `system_bp` + `candidate_bp`.
3. **External I/O:** stub default + `src/utils/integration_io.py` product guard (AST-711).
4. **Joan adjacency (not in-process scenario outline):** AST-712 / AST-818 operator scripts + `docs/integration-operator/` — keep as a **Related** section, not as `### AST-712` / `### AST-818` outline headings.
5. **Today’s README defect:** primary outline is ticket sections (`### AST-711`, `### AST-712`, `### AST-818`) — violates parent AC1.

---

## Stage 1: Ada verify + Code Complete (build-child)

**Done when:** Epic worktree tip still matches the Inventory (one scenario file; no product edit required); Linear is **Code Complete** with Ada still assignee; Ada has posted a Code Complete comment pointing Betty at Stage 2 of this plan.

1. On `sub/AST-915/AST-1003-function-forward-integration-readme` after merge-clean (`origin/dev` ancestor, `BEHIND=0`, parent `origin/ftr/AST-915-test-coverage-integration-testing-discovery-first` merged), confirm read-only:
   - `tests/integration/scenarios/` still contains only `test_candidate_nav_api.py`.
   - `docs/test-bible/integration/README.md` still uses ticket-forward `### AST-711` / `### AST-712` / `### AST-818` headings (Betty’s target).
2. Do **not** edit `docs/test-bible/**`, `tests/**`, `src/**`, harness scripts, GHA, or `docs/integration-operator/**`.
3. Do **not** invent scenarios or ADR positions.
4. Move Linear → **Code Complete**. Comment: Betty applies Stage 2 literal replacement to `docs/test-bible/integration/README.md` on this publish ref; acceptance = function-forward outline (grep checks in Stage 2 Done when).

If Inventory drifted (new scenario files, renamed harness, removed operator docs), **stop** and comment on **AST-1003** (not parent) with the drift — do not improvise the Stage 2 body.

---

## Stage 2: Betty lands function-forward README (qa-child)

**Done when:**

1. `docs/test-bible/integration/README.md` on `origin/sub/AST-915/AST-1003-function-forward-integration-readme` equals the **Target file body** below (byte-for-byte aside from a single trailing newline if the editor adds one).
2. Outline is function-forward:
   - `rg -n '^### AST-[0-9]+' docs/test-bible/integration/README.md` → **no matches**
   - `rg -n '^## Coverage by function area' docs/test-bible/integration/README.md` → **one match**
   - File still contains citations `AST-711`, `AST-712`, `AST-818`, `AST-990` as prose/citation text (not as `### AST-NNN` headings).
3. No new files under `tests/integration/scenarios/`.
4. Betty publishes the bible commit to this publish ref (Betty’s normal test-tree publish — not Ada).

1. Replace the **entire** contents of `docs/test-bible/integration/README.md` with the Target file body in the next section (overwrite; do not append to the old ticket sections).
2. Run the three `rg` checks above; all must pass.
3. Commit/publish per Betty qa-child + merge-tests for this publish ref. Do **not** add new integration scenarios, CI vendor commits, or ADR prose.

### Target file body (`docs/test-bible/integration/README.md`)

````markdown
# Integration test tier

**Location:** `tests/integration/` — multi-layer in-process wiring (Flask blueprints → core → data). Not UAT; not live deploy smoke.

**Component suite:** `tests/component/` remains independent. `run_component_tests.sh` does **not** run integration tests unless paths are passed explicitly.

**Maintainer (existing scenarios):** Betty (`qa-child`) — revise when product invalidates an existing scenario; keep this map honest. Inventing new integration coverage is **not** the default deliverable of a Betty pass.

## How to run

```bash
./scripts/testing/run_integration_tests.sh
```

Default target: all of `tests/integration/`. Pass pytest paths or flags after the script name to narrow runs.

**Pass criterion:** pytest green — no branch-coverage gate, no Vitest tail.

## External I/O policy

- **Default:** stub only — env defaults in `tests/integration/conftest.py`; live network blocked in product when `ASTRAL_INTEGRATION_MODE=1` (`src/utils/integration_io.py`).
- **Spikes / manual only:** `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1` opts out of the guard.

## Fixtures

- Temp SQLite per test (`integration_db` / `seeded_candidate`) — same real-DB pattern as `tests/component/data/conftest.py`.
- Auth via mock token authenticator (`test-token` → admin Susan) — no API↔core mocks at blueprint boundaries.
- `integration_app` registers `system_bp` + `candidate_bp` only (minimal v1 harness).

## Coverage by function area

### Candidate list + nav config (API → core → data)

**Status:** has coverage

**What it proves:** Seeded SQLite + Bearer auth for `GET /api/candidates` and `GET /api/nav_config`; Jobs group visibility follows candidate state (`ACTIVE_SEARCH` shows Jobs; `NEW_CANDIDATE` hides the group); unauthenticated nav returns 401.

**Scenarios:**

- `tests/integration/scenarios/test_candidate_nav_api.py`

**Citations:** AST-711 (first scenario + harness); AST-990 (early-lifecycle seed aligned to `NEW_CANDIDATE`)

### Controlled external I/O (product guard)

**Status:** has coverage (infrastructure)

**What it proves:** Under default harness mode, live external network calls are blocked unless an explicit opt-out is set.

**Where:** `src/utils/integration_io.py` plus harness env defaults in `tests/integration/conftest.py` — exercised whenever the suite runs under stub policy.

**Citations:** AST-711

### Additional API blueprints beyond system + candidate

**Status:** should-have

**Gap:** The v1 harness registers only `system_bp` + `candidate_bp`. Other UI blueprints have no multi-layer in-process scenarios in this tier yet.

**Citations:** none (gap)

### Company / roster cultivation paths

**Status:** should-have

**Gap:** No integration scenario covers company roster multi-layer flows through API → core → data.

**Citations:** none (gap)

### Job pipeline (qualify / gaze / consult seams)

**Status:** should-have

**Gap:** No integration scenario covers job-entity multi-layer paths end-to-end in this tier.

**Citations:** none (gap)

### Artifact generation pipeline

**Status:** should-have

**Gap:** No integration scenario covers artifact generate/resume through UI → core → data (external stubs).

**Citations:** none (gap)

### Full-server / scheduler bootstrap

**Status:** should-have

**Gap:** v1 harness intentionally avoids full `ui.server` bootstrap and the in-process scheduler. Full-boot scenarios are not present yet.

**Citations:** AST-711 (minimal-app decision; full-server left open)

## Related: Joan Railway post-deploy operator

Adjacency only — **not** an in-process `tests/integration/` scenario area, and **not** a prep-uat smoke proposal.

**Trigger:** after `origin/dev` lands and Susan’s Railway **test** service deploy completes (Chuckles post-`push-dev` / `prep-uat`, or Susan manual invoke).

**Commands:**

```bash
./scripts/testing/verify_integration_deploy_ref.sh
./scripts/testing/run_railway_integration_tests.sh
```

**Skill:** `~/.cursor/skills/integration-operator/SKILL.md`

**Failure triage:** non-zero exit → Joan opens Linear **Discussion** for Chuckles with repro log under `debug/integration-operator/`; Joan does not patch product or enable live external I/O.

**Post-deploy gate (extends operator):** automatic Railway harness run after `origin/dev` deploy, GitHub commit status on the dev SHA (`integration/tests`), Linear **Discussion** auto-create on failure. Contract: [`docs/integration-operator/POST_DEPLOY_GATE.md`](../../integration-operator/POST_DEPLOY_GATE.md).

**Operator contract:** see [`docs/integration-operator/README.md`](../../integration-operator/README.md) (controlled-vs-live table — do not duplicate here).

**Citations:** AST-712 (operator + Railway test host); AST-818 (post-deploy GitHub status + failure Discussion)

## Growth

- Add scenarios under `tests/integration/scenarios/test_<name>.py`.
- Shared fixtures stay in `tests/integration/conftest.py`.
- Program positions for **new** coverage ownership, prep-uat smoke, and CI vendors are **out of scope for this README** — sibling ADR AST-1004 after Archie approval.
````

⚠️ **Decision:** Should-have areas named above are discovery gaps for Archie to validate — not a commitment to build them, not ADR ownership/CI positions. Do not expand or rename those headings during build/qa without a plan revision.

⚠️ **Decision:** Preserve Joan operator content as **Related** (citations AST-712 / AST-818) so the map stays honest about what exists adjacent to the harness, without using ticket ids as the document outline.

---

## Stage 3: Ada Tests Ready / test-child acceptance (after Betty publish)

**Done when:** Ada confirms Stage 2 Done-when checks on the publish-ref tip; Linear advances per normal engineer test-child path (manifest may be docs-acceptance only — Betty’s Tests Ready comment).

1. `git fetch origin` and inspect `origin/sub/AST-915/AST-1003-function-forward-integration-readme`.
2. Re-run the three `rg` checks from Stage 2 Done when against that tip’s `docs/test-bible/integration/README.md`.
3. Confirm `tests/integration/scenarios/` still has only `test_candidate_nav_api.py`.
4. If the README content diverges from Stage 2 Target or ticket-outline headings remain → **`[qa-handoff]`** comment, stay Tests Ready, assign Betty — do **not** patch `docs/test-bible/**` as Ada.

---

## Self-Assessment

**Scope:** `Single-Component` — one bible README rewrite plus this plan; no product or scenario tree.

**Conf:** `high` — target file and inventory are known; structure mirrors parent AC; ownership split matches AST-990 and the engineer hook.

**Risk:** `low` — docs-only map; wrong outline would confuse Archie/ADR but cannot regress runtime. Residual process risk if Betty skips Stage 2 literal paste — mitigated by rg Done-when checks.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope-only: only the named README + this plan; no ADR/CI/scenario expansion.
- §3.3 / layering: no `src/` imports or code.
- §3.6 spikes: N/A — no spike output.
- Test-tree ownership: engineer does not commit `docs/test-bible/**` (hook + AGENTS.md); Betty lands Stage 2.
- No conflict with §2.1 / §2.4 / §2.6 — no config, batch, or state-machine changes.
