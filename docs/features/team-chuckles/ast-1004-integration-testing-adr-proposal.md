# AST-1004 — Integration testing ADR proposal

- **Linear (this ticket):** [AST-1004](https://linear.app/astralcareermatch/issue/AST-1004/integration-testing-adr-proposal-test-coverage-integration-testing)
- **Parent:** [AST-915](https://linear.app/astralcareermatch/issue/AST-915/test-coverage-integration-testing-discovery-first) — Test Coverage — integration testing, discovery first
- **Publish ref:** `origin/sub/AST-915/AST-1004-integration-testing-adr-proposal`
- **Blocked by (satisfied for build):** [AST-1003](https://linear.app/astralcareermatch/issue/AST-1003/function-forward-integration-readme-test-coverage-integration-testing) — function-forward map at `docs/test-bible/integration/README.md` (User Testing; on `origin/ftr/AST-915-…`)
- **Summary:** Land an Archie-interrogable ADR that takes program positions on taxonomy/boundary, ownership of **new** integration coverage, layer-seam contracts, prep-uat smoke (advisory→blocking), execution environment + CI story, and maintenance/cost — citing the AST-1003 README and keeping prep-uat smoke distinct from Joan’s Railway post-deploy gate. Docs/Linear only; no new scenarios; no CI vendor commitment; no implementation children filed in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/team-chuckles/ast-915-integration-testing-adr.md` | New — full ADR body (literal from Stage 1 Target) | docs |
| `docs/features/team-chuckles/ast-1004-integration-testing-adr-proposal.md` | This plan | docs |

**Linear (not a git path — build Stage 2):**

| Artifact | Change |
|----------|--------|
| Linear Document on **AST-1004** | Create via `save_document` with `issue: "AST-1004"`; title + content = ADR Target body (same markdown as the repo file, without wrapping the Target fence) |
| Linear comment on **AST-1004** | Link repo blob + Linear Document; note Archie review (assign stays Katherine through resolve; do **not** reassign Susan in this ticket) |
| Linear comment on **AST-915** (parent) | One substantive pointer: ADR landed for interrogation; no implementation children until Archie approves |

**Explicitly unchanged (do not edit):**

| File / area | Why |
|-------------|-----|
| `docs/test-bible/integration/README.md` | Sibling AST-1003 deliverable — cite only |
| `tests/integration/**`, `scripts/testing/**` | No new scenarios; no harness invent |
| `.github/workflows/**` | No CI vendor/tooling commitment this wave |
| `docs/integration-operator/**`, Joan `integration-operator` skill | Reference coexistence; do not redesign |
| Betty unit/component ownership, `[qa-handoff]`, existing-only drift duty | ADR proposes how **new** work relates; does not rewrite those rules |
| Any new Linear children under AST-915 for coverage/contracts/smoke | Filed only after Archie ADR approval (Chuckles/Archie) |

---

## Stage 1: Land ADR markdown on publish ref

**Done when:** `docs/features/team-chuckles/ast-915-integration-testing-adr.md` exists on `origin/sub/AST-915/AST-1004-integration-testing-adr-proposal` with content equal to the **Target ADR body** below (byte-for-byte aside from a single trailing newline). Grep checks:

- `rg -n '^## [0-9]+\.' docs/features/team-chuckles/ast-915-integration-testing-adr.md` → matches sections **1–8** exactly once each (headings `## 1.` … `## 8.`)
- File contains the citation path `docs/test-bible/integration/README.md` and the strings `advisory` and `Joan` / `post-deploy`
- File does **not** invent scenario filenames under `tests/integration/scenarios/` beyond citing the existing README map
- No edits under `tests/`, `docs/test-bible/`, `.github/workflows/`, or `docs/integration-operator/`

1. On `sub/AST-915/AST-1004-integration-testing-adr-proposal` after merge-clean (`origin/dev` ancestor, `BEHIND=0`, parent `origin/ftr/AST-915-test-coverage-integration-testing-discovery-first` merged), confirm read-only that `docs/test-bible/integration/README.md` still has `## Coverage by function area` (AST-1003 map present for citation).
2. Create `docs/features/team-chuckles/ast-915-integration-testing-adr.md` with the **entire** Target ADR body in the next section (overwrite if a stub exists; do not append).
3. Run the Done-when greps; all must pass.
4. Commit on epic worktree: `docs(AST-1004): ADR — integration testing program positions`. Push `git push origin HEAD:sub/AST-915/AST-1004-integration-testing-adr-proposal`. Do **not** push `origin/dev`. Do **not** file Linear children.

### Target ADR body (`docs/features/team-chuckles/ast-915-integration-testing-adr.md`)

````markdown
# ADR — Integration testing program (AST-915)

**Status:** Proposed — awaiting Archie approval in Linear  
**Ticket:** [AST-1004](https://linear.app/astralcareermatch/issue/AST-1004/integration-testing-adr-proposal-test-coverage-integration-testing)  
**Parent:** [AST-915](https://linear.app/astralcareermatch/issue/AST-915/test-coverage-integration-testing-discovery-first)  
**Map cited:** [`docs/test-bible/integration/README.md`](../../test-bible/integration/README.md) (AST-1003 function-forward coverage map)  
**Date:** 2026-07-28

## Decision summary (Archie one-screen)

1. **Taxonomy:** `tests/component/` = unit/component (Betty). `tests/integration/` = multi-layer in-process UI→core→data (not UAT, not live deploy smoke). Joan Railway post-deploy = separate operator gate on deployed `origin/dev`.
2. **New coverage ownership:** Inventing **new** integration scenarios is **independent Linear work** (separate issue type / child tickets), not Betty’s default invent duty. Once merged, those scenarios **fold into the GHA roster Betty maintains**. Betty’s shipped duty on **existing** scenarios (revise when product invalidates; `[qa-handoff]`) is unchanged.
3. **Layer-seam contracts:** Future work may add contract suites at data↔core and core↔ui seams per `ASTRAL_CODE_RULES` import direction — filed only after this ADR is approved; shape sketched in §3, not built here.
4. **Prep-uat smoke:** At the ftr→dev staging choke point (`prep-uat`), run a **smoke** of the integration harness **advisory first**; become **blocking** only after the suite earns trust (Archie signal). Distinct from Joan’s Railway post-deploy gate (§5).
5. **CI / env:** Keep documenting the **existing** GitHub Actions integration workflow as the current CI surface; do **not** commit a new CI vendor in this wave. ProDesk remains the candidate host for heavier/isolated runs later.
6. **Rot tax:** Creators pay invent cost (separate tickets). Betty pays maintain cost once scenarios are on the roster. Gate **policy** (advisory vs blocking) is Archie; Chuckles **runs** prep-uat; Joan **runs** post-deploy — do not merge those roles.

**Out of this ADR’s build wave:** no new `tests/integration/scenarios/*`, no workflow YAML changes, no prep-uat skill rewrite, no Joan skill redesign, no implementation children filed before approval.

---

## 1. Taxonomy and boundary

### Position

| Tier | Location | Proves | Owner (steady state) |
|------|----------|--------|----------------------|
| Unit / component | `tests/component/` | Single module / layer with fakes as today | Betty (invent + maintain for product tickets) |
| Integration (in-process) | `tests/integration/` | Multi-layer wiring Flask blueprints → core → data; stub external I/O by default | **Existing:** Betty revise/maintain. **New:** invent via independent tickets → then Betty roster |
| Deploy / operator | Railway test host + Joan scripts | Deployed `origin/dev` pin still green after push | Joan operator (`integration-operator`); failure → Linear Discussion for Chuckles |
| Human UAT | Browser on staging after prep-uat | Product acceptance | Archie / Susan |

**Bright lines:**

- Integration scenarios are **not** UAT and **not** live external I/O (default stub; product guard `ASTRAL_INTEGRATION_MODE=1` — see map README).
- Integration scenarios are **not** Joan’s post-deploy gate (that runs against Railway after deploy).
- Component suite stays independent: `run_component_tests.sh` does not pull integration unless paths are passed explicitly.

**Citation:** function-area has/should-have map — `docs/test-bible/integration/README.md` (AST-1003). Should-have rows are discovery gaps for prioritization after approval, not a commitment to build them in this wave.

---

## 2. Ownership for **new** integration work

### Position (answers parent open question)

**Creation of new integration tests is a separate issue type** (independent Linear child / issue under Archie or this parent as directed). Engineers (or a named implementation child) **invent** coverage when that ticket is dispatched.

**Betty does not invent new integration coverage as the default** deliverable of `qa-child`. Her duty on integration remains:

- Revise **existing** scenarios / harness wiring when product invalidates them (same class as broken component tests).
- Keep `docs/test-bible/integration/` honest for existing map entries.
- Return real product defects to the engineer — do not weaken scenarios to hide bugs.
- Maintain the **GHA roster** of integration tests once new scenarios land (harness green + drift), parallel to component ownership (AST-989 / AST-991 / AST-992).

**Fold-in rule:** When an implementation child merges a new scenario into `tests/integration/`, Betty’s ongoing ownership includes that path on the roster. The inventing ticket cites **this ADR §2** (and the function-area row it fills from the README map).

**Unchanged:** Betty unit/component ownership; engineer `[qa-handoff]` when the test layer is wrong; engineer ban on editing `tests/` / `docs/test-bible/**`.

---

## 3. Layer-seam contract tests (proposed shape — not built here)

### Position

After ADR approval, implementation children may add **contract** suites that pin seams required by `docs/ASTRAL_CODE_RULES.md` §3.2–§3.3:

| Seam | Intent | Non-goals |
|------|--------|-----------|
| **data ↔ core** | Core calls data with agreed signatures/state params; data raises, core decides | No business rules in data; no UI imports |
| **core ↔ ui (API)** | Blueprints call core only; auth + config-resolved responses; no data/external imports from UI | No React-as-integration tier; no full-server bootstrap required for v1 contracts |
| **external boundary** | Already covered by stub policy + `integration_io` guard in the in-process tier | Do not turn live network on in CI |

**Shape for later children (normative sketch):**

- Prefer extending `tests/integration/` (or a clearly named `tests/integration/contracts/` subfolder if a later child introduces it) over a third top-level suite.
- Keep the AST-711 harness pattern: real SQLite temp DB, mock token auth, **no** API↔core mocks at blueprint boundaries.
- Each contract child cites **this ADR §3** and a specific README function-area (has or should-have).

**This wave:** document only. No contract files, no new scenarios.

---

## 4. Prep-uat smoke posture (advisory → blocking)

### Position (answers parent open question)

**Choke point:** Chuckles `prep-uat` when landing `ftr` → `origin/dev` for Railway staging / Archie UAT.

**Behavior:**

1. **Advisory first:** After (or as a named step of) prep-uat land, run `./scripts/testing/run_integration_tests.sh` (or a later explicitly named smoke subset) and **report** result (Linear comment / log). A red advisory **does not** mechanically block finish-up / PR to `dev` until Archie promotes the gate.
2. **Blocking later:** Only after the suite earns trust (low flake, clear failure routing), Archie directs that prep-uat **fail closed** on smoke red. Until that signal, advise-only.

**Rationale:** A flaky blocking gate teaches the team to route around it. Trust before teeth.

**Implementation children (after approval only)** must cite **this ADR §4** if they wire smoke into `prep-uat` / `prep-uat-land.sh`. They must not silently make it blocking without Archie’s promote signal recorded on the parent.

---

## 5. Separation from Joan’s Railway post-deploy gate

### Position (parent AC3)

| | Prep-uat smoke (§4) | Joan post-deploy gate (AST-712 / AST-818) |
|--|---------------------|------------------------------------------|
| **When** | Before / at ftr→dev staging handoff | After `origin/dev` is deployed to Railway **test** |
| **Where** | Operator/local or CI against the **landed ref** being prepped | Railway test host against **deployed** pin |
| **Who** | Chuckles prep-uat path (future wiring) | Joan `integration-operator` |
| **Signal** | Advisory → later blocking on prep-uat | GitHub commit status `integration/tests` + Linear Discussion on failure |
| **Skill / docs** | `prep-uat` (future); not Joan | `docs/integration-operator/POST_DEPLOY_GATE.md`, `~/.cursor/skills/integration-operator/SKILL.md` |

**Coexistence:** Both may run the same underlying harness script. They answer different questions (“is this feature ref ready to stage?” vs “did the test host deploy stay green?”). **Do not** redesign or replace Joan’s operator skill as a drive-by of this program. **Do not** treat Joan Discussion failures as prep-uat smoke results or vice versa.

---

## 6. Execution environment and CI story

### Current state (fact — not a new vendor commit)

- In-process harness: `./scripts/testing/run_integration_tests.sh`.
- GitHub Actions workflow `.github/workflows/integration-tests.yml` already runs that harness on pushes to `dev` / `ftr/**` and PRs to `dev`.
- Railway post-deploy path is Joan’s (see §5).

### Position

1. **No new CI vendor** in this discovery wave. Do not introduce Circle, Buildkite, etc., or rewrite the workflow “for completeness.”
2. **GHA remains the default roster runner** for the in-process suite Betty maintains after fold-in (§2).
3. **ProDesk candidacy:** Prefer ProDesk (or an equivalent isolated operator machine) for any future **heavy** or **watchers-isolated** runs that must not share a laptop with live dispatch — decision deferred to an implementation child that cites **this ADR §6**. Isolation from live watchers is a requirement for that child to specify, not invent here.
4. **Live external I/O** stays opt-in / spike-only (`ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1`); never default in GHA or Joan operator.

---

## 7. Maintenance and cost ownership (rot tax)

### Position

| Cost | Who pays |
|------|----------|
| Inventing a new scenario / contract / smoke wire | The dispatched implementation ticket (engineer build + Betty qa for test-tree paths) |
| Keeping existing + folded scenarios green; revising on product drift; bible map honesty | Betty |
| Deciding advisory vs blocking for prep-uat smoke | Archie |
| Running prep-uat / merge-child / finish-up | Chuckles |
| Running Railway post-deploy gate; opening failure Discussions | Joan |
| Prioritizing which README should-have rows become tickets | Archie after ADR approval (Chuckles files children citing ADR sections) |

**Rot reality:** Integration suites rot faster than unit suites because they span layers. The fold-in rule (§2) exists so invent does not orphan maintain.

---

## 8. Approval and spawn path

### Position (parent AC4)

1. Archie interrogates this ADR in Linear (document on AST-1004 + repo path above).
2. **Until Archie approves:** no implementation children for coverage expansion, new contract suites, or prep-uat smoke wiring.
3. **After approval:** Chuckles/Archie file implementation children under AST-915 (or as Archie directs). **Each child Description must cite the ADR section it implements** (`§2` / `§3` / `§4` / `§6`, etc.) and the README function-area row when filling a should-have gap.
4. AST-1003 map remains the human-readable coverage outline; this ADR remains the program-position source.

### Explicit non-decisions (leave for post-approval children)

- Exact smoke command subset vs full harness.
- Whether contracts live in `tests/integration/contracts/` vs flat scenarios.
- ProDesk provisioning details.
- Promoting prep-uat smoke from advisory to blocking (Archie signal later).

---

## References

- Parent definition: AST-915
- Function-forward map: AST-1003 → `docs/test-bible/integration/README.md`
- Betty existing-only drift / GHA roster: AST-989, AST-991, AST-992
- Joan post-deploy: AST-712, AST-818 → `docs/integration-operator/`
- Layer law: `docs/ASTRAL_CODE_RULES.md` §3.2–§3.3
````

⚠️ **Decision:** Dual publish — repo markdown at `docs/features/team-chuckles/ast-915-integration-testing-adr.md` (stable cite path for future children) **and** Linear Document on AST-1004 (satisfies AC “ADR exists in Linear”). Same body; no third location under `docs/test-bible/` (engineer/Betty ownership walls).

⚠️ **Decision:** ADR file named `ast-915-…` (parent program id) not `ast-1004-…` so post-approval children cite the program ADR, not the planning ticket. Plan stays `ast-1004-…`.

---

## Stage 2: Publish ADR to Linear Document + comments

**Done when:**

1. A Linear Document exists with parent **issue AST-1004**, title exactly `ADR — Integration testing program (AST-915)`, content matching the Target ADR body (the markdown inside the Stage 1 fence — not the fence markers).
2. AST-1004 has a comment with: GitHub blob URL on publish ref for `docs/features/team-chuckles/ast-915-integration-testing-adr.md`, and the Linear Document link/id from `save_document`.
3. AST-915 (parent) has one comment pointing at AST-1004’s ADR for Archie interrogation; states explicitly that **no implementation children** should be filed until Archie approves.
4. No new Linear issues created under AST-915 (or elsewhere) for coverage/contracts/smoke.
5. Assignee on AST-1004 remains Katherine; status moves only via normal pipeline (this stage ends at Code Complete readiness — status change per build-child).

1. Using `linear-kath` MCP `save_document`: create document with `issue: "AST-1004"`, `title: "ADR — Integration testing program (AST-915)"`, `content:` = exact text of the committed ADR file (read from disk after Stage 1).
2. `save_comment` on AST-1004 with blob URL:
   `https://github.com/susansomerset/astral/blob/sub/AST-915/AST-1004-integration-testing-adr-proposal/docs/features/team-chuckles/ast-915-integration-testing-adr.md`
   plus Document id/URL from step 1.
3. `save_comment` on AST-915: ADR ready for interrogation on AST-1004; cite § Decision summary; remind no implementation children until approval.
4. Do **not** call `save_issue` to create children. Do **not** edit Joan/Betty skills or GHA.

---

## Stage 3: Code Complete handoff (docs-only)

**Done when:** Linear AST-1004 is **Code Complete**, Katherine still assignee; comment states Stages 1–2 landed (repo ADR + Linear Document); Betty’s qa-child for this ticket is docs-acceptance only (no `tests/` invent) — point her at verifying ADR file + Linear Document existence, not writing scenarios.

1. Per build-child: move status → **Code Complete**.
2. Comment: docs-only ADR; Betty verify presence/sections; no product/src; no new integration scenarios.

---

## Self-Assessment

**Scope:** `Single-Component` — docs + Linear Document only; cites existing README/operator docs; no `src/`, tests, or CI workflow edits.

**Conf:** `high` — parent AC and answered open questions already fix ownership (separate invent / Betty maintain) and advisory-first smoke; AST-1003 map is on ftr for citation; dual-publish pattern mirrors AST-1003’s literal-body plan.

**Risk:** `low` — wrong ADR wording could mis-file later children, but cannot regress runtime; mitigated by explicit non-decisions and “no children until approval.” Residual process risk if Stage 2 skips Linear Document — AC2 requires ADR **in Linear**.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope-only: only named ADR path + Linear Document + this plan; no scenario/CI invent.
- §3.2–§3.3: ADR §3 cites layer seams as **future** contract shape; does not add imports or modules now.
- §3.6: no spike/debug paths committed.
- No §2.4 / §2.6 batch or state-machine changes.
- Engineer test-tree ban honored — no `tests/` or `docs/test-bible/**` edits.
- Conflicts: none requiring `conf-!!-NONE`.
