# AST-992 — Betty skills: integration drift duty

- **Linear:** [AST-992](https://linear.app/astralcareermatch/issue/AST-992/betty-skills-integration-drift-duty-betty-monitors-integration-tests)
- **Parent:** [AST-989](https://linear.app/astralcareermatch/issue/AST-989/betty-monitors-integration-tests-agent-skills)
- **Publish ref:** `origin/sub/AST-989/AST-992-betty-skills-integration-drift-duty`
- **Blocked by:** [AST-991](https://linear.app/astralcareermatch/issue/AST-991/betty-agent-integration-harness-ownership-betty-monitors-integration) (agent identity first — do not edit `betty-AGENTS.md` here)
- **Summary:** Update Betty’s QA skill procedure (`qa-child`, plus intake wording in `check-linear` and a one-line engineer pointer in `test-child`) so reading those docs alone teaches when and how she **revises existing** integration scenarios / harness-related test-tree work when product invalidates them, when she returns a product bug to the engineer, and that Chuckles-routed harness failures fit her existing queue — **not** inventing new integration coverage or a second QA persona.

## UAT fitness

- **AC restored:** Parent AC2 — “Reading Betty’s QA skill(s) alone teaches when and how she **revises existing** integration scenarios / harness-related test-tree work when product invalidates them (not when to invent new coverage), and when she returns a product bug to the engineer.” Parent AC4 (skills half) — “After host install of the updated agent/skills, a Betty session following those docs would treat a drifted **existing** integration scenario as her authority the same way she treats a broken component test.” (Agent-content half is AST-991.)
- **Correct outcome:** A Betty session that follows installed `qa-child` (+ intake note) treats a product-invalidated **existing** `tests/integration/` scenario as her revise-and-publish duty (bible map honesty for the integration tier included), and routes real product defects back to the engineer via comment — without adding new scenarios as this epic’s deliverable.
- **Sibling check:** AST-991 owns `betty-AGENTS.md` identity/standards only. This plan must not rewrite agent identity. Engineer skills stay untouched except the one-line `test-child` pointer. Verified by Files Changed = Betty skills + one engineer line + this plan.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done. (N/A as symptom — shipping a vague “Betty looks at CI” sentence without revise-vs-product-bug procedure and update-existing-only rule is also not done.)
- **Wrong fix rejected:** Inventing new integration scenarios / fixing AST-988 harness red / expanding AST-915–927 coverage / rewriting `betty-AGENTS.md` / editing Joan `integration-operator` are out of scope. Correct fix is procedure prose in Betty skills (+ one engineer handoff pointer).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/qa-child/SKILL.md` | Add integration drift duty procedure; align Who-runs-this bible-edit “only” list to include `docs/test-bible/integration/**` | skills (Betty) |
| `~/team-chuckles/skills/check-linear/SKILL.md` | One Betty intake note: Chuckles-routed integration harness failure uses existing inbox / §5b — no parallel queue | skills (Betty intake) |
| `~/team-chuckles/skills/test-child/SKILL.md` | One-line cross-ref: drifted `tests/integration/` scenarios → `[qa-handoff]`, not engineer edits | skills (engineer pointer) |
| `docs/features/team-chuckles/ast-992-betty-skills-integration-drift-duty.md` | This plan | docs |

**Commit homes:** skill edits in **`team-chuckles`**. Plan doc only on this astral **`origin/sub/AST-989/AST-992-betty-skills-integration-drift-duty`**.

**Out of scope (do not touch):**

- `~/team-chuckles/agents/betty-AGENTS.md` (AST-991)
- `build-child` / `resolve-child` (test-tree ban already covers `tests/`; only `test-child` gets the explicit integration pointer)
- Joan `integration-operator`, GHA workflow YAML, Astral `src/**`, `tests/**`, `docs/test-bible/**` content (procedure only — no scenario edits in this ticket)
- AST-988 harness repair; AST-915 / AST-927 coverage expansion

---

## Stage 1: `qa-child` — integration drift procedure

**Done when:** Reading `~/team-chuckles/skills/qa-child/SKILL.md` alone teaches (1) when product work invalidates an **existing** integration scenario / harness wiring, Betty revises it the same way she revises a broken component test; (2) she keeps `docs/test-bible/integration/` honest when that map applies; (3) she returns real product bugs to the engineer instead of papering over them in tests; (4) inventing new integration coverage is **not** the default deliverable of a Betty pass under this epic’s rules.

1. Open `~/team-chuckles/skills/qa-child/SKILL.md` (source of truth; symlink at `~/.cursor/skills/qa-child/SKILL.md`).
2. Extend the YAML `description` so it still lists bible / manifest / `[qa-handoff]`, and also names **integration drift of existing scenarios** (update-existing only). Exact replacement for the YAML description block:

```yaml
description: >-
  Betty: from Code Complete, use docs/test-bible/** to pick existing tests vs new
  work, flag tests broken by the change (component and existing integration
  scenarios), keep the bible honest including docs/test-bible/integration/ when
  that tier applies; revise existing integration scenarios when product
  invalidates them — do not invent new integration coverage as the default;
  return real product bugs to the engineer; manifest for test-child; commit on
  astral-tests; publish bible/tests to origin/sub/* only (Betty push); merge
  origin/ftr parent on astral-tests before bible edit; queue Code Complete by
  status; Tests Ready [qa-handoff] with assignee Betty (check-linear);
```

3. In the **Who runs this** opening paragraph, after the sentence that ends with “dying quietly in `test-child`.”, insert this exact sentence (keep the rest of the paragraph; do not replace the whole paragraph):

```markdown
 She also owns **integration-test drift** for **existing** scenarios under `tests/integration/` and related harness wiring (`scripts/testing/run_integration_tests.sh`, fixtures in `tests/integration/conftest.py`): when a product change invalidates an existing scenario, revise it in the same pass class as a broken component test; keep `docs/test-bible/integration/` honest when the map applies; **do not** invent new integration scenarios as the default deliverable of this skill (coverage expansion stays other epics — AST-915 / AST-927). Real product defects → comment back to the engineer; do not paper over product bugs in tests.
```

4. In the same **Who runs this** opening paragraph, **replace** (do not leave both) these two phrases so bible-edit authority matches the integration-map duty — no improvisation:

   a. Replace:

```markdown
She is the **sole authority** on **`docs/test-bible/**`** — the per-component tree mirroring **`tests/component/`**:
```

   with:

```markdown
She is the **sole authority** on **`docs/test-bible/**`** — the per-component tree mirroring **`tests/component/`**, plus the integration-tier map under **`docs/test-bible/integration/`** (existing **`tests/integration/`** scenarios):
```

   b. Replace:

```markdown
Betty edits **only** the component file(s) for modules this ticket touches plus **`docs/test-bible/README.md`** when cross-cutting standards change.
```

   with:

```markdown
Betty edits **only** the component file(s) for modules this ticket touches, **`docs/test-bible/integration/**`** when that tier applies (map honesty for **existing** scenarios), plus **`docs/test-bible/README.md`** when cross-cutting standards change.
```

5. Immediately after the **Who runs this** / publish paragraph block (before **Branch law:**), insert this new subsection with exact text:

```markdown
### Integration drift duty (update-existing only)

**When it applies:** During **§3–§7** for any ticket whose plan/product diff can invalidate an **existing** scenario under `tests/integration/` (or its fixtures / `run_integration_tests.sh` harness wiring), treat that drift as Betty authority parallel to a broken component test.

**Do:**
1. Read `docs/test-bible/integration/README.md` (and any `### AST-NNN` blocks there that name scenarios) when the ticket touches layers those scenarios exercise.
2. List invalidated **existing** paths under **§6 Broken / obsolete tests** (same list as component); revise them in **§7–§9**.
3. Update the integration bible map in the same pass when mapping is wrong or stale for those existing scenarios.
4. If the failure is a **product** contract break (scenario correctly asserts shipped behavior; product is wrong) → **`save_comment`** naming the product bug, leave or return the ticket to the implementing engineer — **do not** weaken the scenario to hide the bug.

**Do not:**
- Add new `tests/integration/scenarios/test_*.py` files (or expand the suite as a program) unless the **ticket plan** and bible already require that named scenario as acceptance for **this** child — default for AST-989 monitoring ownership is **revise existing only**.
- Fix AST-988 harness redness as a drive-by; do not redesign AST-915 / AST-927 coverage.
- Invent a parallel QA queue or persona for “integration Betty.”
```

6. In **§3 Read context**, after the bullet that reads the combined plan via `git show`, add this exact bullet:

```markdown
- **Integration tier:** When the plan/product diff can affect multi-layer API/nav/wiring covered by existing integration scenarios, also read `docs/test-bible/integration/README.md` and skim matching files under `tests/integration/scenarios/` / `tests/integration/conftest.py`. Spot assertions, fixtures, or harness assumptions the change will break — same keeper duty as component tests. Prefer **revision** of those existing paths; do **not** treat “add a new integration scenario” as the default fix for drift.
```

7. In **§6 Design the manifest**, after classification item **2. Broken / obsolete tests**, add this exact clarifying sentence as a new paragraph (still under §6, before item **3. Gaps**):

```markdown
**Integration scenarios:** Put drifted **existing** `tests/integration/**` paths in classification **2** (revise in this pass). Do **not** use classification **3 Gaps** to invent new integration coverage for monitoring ownership — Gaps remain for bible+plan holes the ticket already accepts; new integration-suite expansion is out of scope for this skill’s default path.
```

8. In **§7**, replace the bullet that currently ends with “Implement **tests / fixtures / harness only**…” with this exact bullet (same placement in the list):

```markdown
- Implement **tests / fixtures / harness only** (including **revisions** to component tests **and** to **existing** `tests/integration/**` scenarios / fixtures / `scripts/testing/run_integration_tests.sh` wiring marked obsolete in **§6**) in the working tree before **§8**. **Do not** land product fixes here — real bugs go back to the engineer with a comment; unmaintainable tests → comment and hold **`Code Complete`** or ask Archie. **Do not** add new integration scenarios unless the ticket plan explicitly requires that named file.
```

9. Do **not** change intake gates A/B/C status lists, bible sole-authority publish rules, Land preflight, or §9 merge-tests ceremony — only the drift/procedure additions above (including Stage 1 step 4 bible-edit scope alignment).

⚠️ **Decision:** Procedure lives in `qa-child` (Betty’s execution skill). Agent identity stays AST-991. Engineer pointer is a single `test-child` line (Stage 3), not a rewrite of engineer skills. Who-runs-this bible-edit “only” list is rewritten (step 4) so it includes `docs/test-bible/integration/**` — same authority as the new drift subsection, no conflicting “component files only” leftover.

---

## Stage 2: `check-linear` — Chuckles-routed harness fits existing intake

**Done when:** Reading Betty’s `check-linear` path alone states that a Chuckles-routed integration harness failure is handled via the existing Betty inbox / §5b → `qa-child` path — no new queue letter or parallel persona.

1. Open `~/team-chuckles/skills/check-linear/SKILL.md`.
2. Immediately after the **§5b** heading line and the “**Betty only.** …” intro paragraph (before the numbered list starting with `list_issues`), insert this exact paragraph:

```markdown
**Integration harness (no parallel queue):** If Chuckles (or a Chuckles-routed thread) surfaces a red / drifted **existing** GHA integration harness or `tests/integration/` scenario to Betty — including `@Betty` on a Discussion opened from Joan’s operator triage — treat it as ordinary Betty inbox / **`[qa-handoff]`** / **§5b** work that runs **`qa-child`** (revise existing scenarios or return a product bug). Do **not** invent a fourth queue letter or a second QA persona for “integration only.”
```

3. Do **not** change §5b numbered steps, engineer gates, or Chuckles §5c.

---

## Stage 3: `test-child` — one-line engineer pointer

**Done when:** Engineers reading `test-child` see an explicit one-line that drifted integration scenarios are Betty’s via `[qa-handoff]`, not something to patch under `tests/integration/` themselves.

1. Open `~/team-chuckles/skills/test-child/SKILL.md`.
2. Immediately after the existing **Test-tree ban (engineers):** paragraph, append this exact one-line paragraph:

```markdown
**Integration scenarios:** `tests/integration/` (and integration harness scripts under `scripts/testing/`) are inside that ban — if a product fix invalidates an **existing** integration scenario, **`[qa-handoff]`** Betty; do not edit integration tests yourself.
```

3. Do **not** edit `build-child` or `resolve-child` in this ticket.

---

## Stage 4: Install verify + team-chuckles commit

**Done when:** Host install surfaces the new wording under `~/.cursor/skills/{qa-child,check-linear,test-child}/SKILL.md`, and the three skill files are committed on `team-chuckles`.

1. From `~/team-chuckles`, run `./install.sh` (or confirm skill links refresh `~/.cursor/skills/`).
2. Confirm by grep that `~/.cursor/skills/qa-child/SKILL.md` contains both `Integration drift duty` and `update-existing only`, and also contains ``docs/test-bible/integration/**`` in the Who-runs-this “Betty edits **only**” sentence.
3. Confirm by grep that `~/.cursor/skills/check-linear/SKILL.md` contains `Integration harness (no parallel queue)`.
4. Confirm by grep that `~/.cursor/skills/test-child/SKILL.md` contains `Integration scenarios:` and `[qa-handoff]`.
5. Confirm by grep that `~/team-chuckles/agents/betty-AGENTS.md` was **not** modified in this ticket’s working tree.
6. Commit in **`team-chuckles`** only the three skill files:

   `code(AST-992): Betty skills own integration drift revise-existing`

7. Code Complete note for Chuckles/hosts: re-run `./install.sh` so Betty/engineer sessions see the update.

---

## Execution contract

- This ticket only — AST-992 skills procedure (+ one engineer pointer).
- Literal Stage 1–3 text; if a named insertion anchor has drifted (missing paragraph / heading), stop and comment on **AST-992** (not parent).
- Do not start Stage 1 product/skills commits until Linear **blockedBy AST-991** is cleared enough for this child to build (identity first); planning/publish of this plan doc does not require AST-991 Code Complete.
- No Astral product behavior change; no GHA YAML; no test-tree scenario edits in this ticket.
- Plan doc stays on astral publish ref; skill files commit on `team-chuckles`.

## Self-Assessment

**Scope:** `minor` — three Team Chuckles skill markdown files (Betty procedure + intake note + one engineer line) plus this plan doc.

**Conf:** `high` — sibling AST-991 already scoped identity vs skills; insertion anchors in `qa-child` / `check-linear` / `test-child` are stable; Stage 1 step 4 removes the Who-runs-this vs integration-bible authority contradiction Joan flagged.

**Risk:** `low` — docs-only skill wording; worst case Betty under-revises integration drift until wording is tightened, with no product runtime impact.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — satisfied (skills + plan; no `src/` / no scenario files).
- §3.6 / §4.2 — plan under `docs/features/team-chuckles/` — satisfied.
- No config / batch / state-machine / import / naming statutes apply to skill markdown.
- Boundaries match parent: no AST-988 fix, no new coverage program, no second QA persona, no agent-identity rewrite.
- `orch.pipeline.plan-is-bible` — Stage 1 step 4 aligns Who-runs-this edit scope with integration-map duty so build does not improvise.

## Revisions

### Revision 1 — 2026-07-27
Driven by: Joan `[plan-discuss] round=1 concern` — fix-now: Stage 1 inserts required `docs/test-bible/integration/` map updates while leaving “Betty edits **only** the component file(s)… plus README” unchanged, so a literal build would contradict itself on bible-edit scope.
Changes: Added Stage 1 step 4 with literal replacements for the sole-authority mirroring clause and the “Betty edits **only**…” sentence so authority explicitly includes `docs/test-bible/integration/**` when that tier applies; renumbered later Stage 1 steps; Stage 4 grep + Decision note updated.

## Review (build stub)

**Publish ref:** `origin/sub/AST-989/AST-992-betty-skills-integration-drift-duty`
**Plan path:** `docs/features/team-chuckles/ast-992-betty-skills-integration-drift-duty.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–4 | `team-chuckles@4549329` | `qa-child` drift duty + bible-edit scope; `check-linear` no-parallel-queue; `test-child` integration `[qa-handoff]` pointer |

**Tip:** astral plan stub (this commit); skills on `team-chuckles` `main` @ `4549329`. Hosts: re-run `~/team-chuckles/install.sh`.

## Radia review (code-rubric.v1)

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-992
**Reviewed tip:** `d35bdfc` (`origin/sub/AST-989/AST-992-betty-skills-integration-drift-duty` before this docs append)
**Overall:** DISCUSS

### Diff change set

- **Paths:** `docs/features/team-chuckles/ast-992-betty-skills-integration-drift-duty.md` (add), `docs/test-bible/README.md` (modify)
- **Layers:** `docs`
- **Change types:** `add`, `modify`
- **Off-repo deliverable verified:** `team-chuckles@4549329` — `qa-child` Integration drift duty + bible-edit scope for `docs/test-bible/integration/**`; `check-linear` no-parallel-queue note; `test-child` one-line integration `[qa-handoff]`; `betty-AGENTS.md` untouched.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | layers+paths miss (no src/core\|utils) |
| astral.agent.do-task-delegation | scoped | not-applicable | layers+paths miss (no src/core) |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers+paths miss (no src/core) |
| astral.batch.batch-id-first | scoped | not-applicable | layers+paths miss (no src data/core) |
| astral.batch.batch-id-format | scoped | not-applicable | layers+paths miss (no src data/core) |
| astral.batch.claim-process-release | scoped | not-applicable | layers+paths miss (no src data/core) |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers+paths miss (no src data/core) |
| astral.config.config-source-of-truth | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | layers+paths miss (no src core/data/config) |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | layers+paths miss (no src/scripts) |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (no artifacts/** / scripts/spikes) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | production plan under docs/features; not spike notes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single plan file docs/features/team-chuckles/ast-992-….md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty merge-tests only touched test-bible; features by engineer |
| astral.git.engineer-test-tree-ban | scoped | conforms | docs/test-bible/README.md via Betty merge-tests, not engineer |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers+paths miss (no src core/external) |
| astral.layers.import-direction | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers+paths miss (no scripts/**) |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers+paths miss (no src/ui) |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers+paths miss (no src/core) |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers+paths miss (no src/core) |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers+paths miss (no src/ui) |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.standards.database-header-inventory | scoped | not-applicable | layers+paths miss (no src/data) |
| astral.standards.debug-contract-gated | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.standards.dry-and-focused-functions | scoped | not-applicable | layers+paths miss (no src/scripts) |
| astral.standards.in-scope-only | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.standards.logging-via-utils | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.standards.no-cross-contamination | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.standards.public-then-helpers | scoped | not-applicable | layers+paths miss (no src/**) |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers+paths miss (no src/utils) |
| astral.state.core-decides-transitions | scoped | not-applicable | layers+paths miss (no src core/data) |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers+paths miss (no src core/data/config) |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers+paths miss (no src/core) |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers+paths miss (no src/ui/frontend) |
| astral.ui.naming-conventions | scoped | not-applicable | layers+paths miss (no src/ui) |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers+paths miss (no ui/scripts/config) |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one merge-tests(AST-992) on sub tip |
| orch.git.commit-vocabulary | universal | conforms | plan/docs/code/merge-tests vocabulary only |
| orch.git.flow-direction-inviolable | universal | conforms | tests→sub via merge-tests; no reverse flow |
| orch.git.ftr-sub-topology | universal | conforms | publish ref sub/AST-989/AST-992-… |
| orch.git.merge-on-checkout | universal | conforms | no evidence of coding on unmerged stale sub |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force in commit history |
| orch.git.no-dev-agent-branches | universal | conforms | work on ticket sub + team-chuckles; no dev-\<agent\> |
| orch.git.one-epic-worktree-per-parent | universal | conforms | astral-AST-989 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | literal Stage 1–3 text; no product improvisation |
| orch.pipeline.plan-is-bible | universal | conforms | skills match Stage 1–3 literal inserts; R1 bible-edit scope applied |
| orch.pipeline.project-scoped-queues | universal | conforms | Team Chuckles ticket-scoped work |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child entry |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statutes/** edits |
| orch.roles.betty-owns-test-tree | universal | conforms | bible README by Betty; skills reinforce Betty revise + engineer handoff |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays implementer assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | role path bans respected across homes |

### Pattern conformance

none cited

### Plan adherence

Scope `minor` matches: three team-chuckles skills + astral plan (+ Betty bible README). Stages 1–3 text present at `4549329`; Stage 1 step 4 Who-runs-this includes `docs/test-bible/integration/**`; `betty-AGENTS.md` not touched (AST-991). No AST-988 / new coverage / AST-915–927 smuggle.

### Findings

**discuss:** straggler — Joan excluded `astral.git.engineer-test-tree-ban` (plan said no bible), but the three-dot diff includes `docs/test-bible/README.md` (Betty `docs(AST-992)` via merge-tests). Statute still **conforms** (Betty-owned path). No product fix required — acknowledge plan-time exclusion did not anticipate Betty’s bible note.

### What’s solid

- `qa-child` alone teaches revise-existing integration drift + product-bug return.
- Intake note + engineer one-liner close the queue/handoff loop without a second QA persona.

### Recommended actions

- Hedy: no code change for the straggler; acknowledge in resolve if desired, then User Testing when ready.
- Hosts: re-run `~/team-chuckles/install.sh` so sessions see skills @ `4549329`.

## Resolution

**Date:** 2026-07-27
**Review tip:** `4dbeed6` (`docs(AST-992): Radia review — findings`)
**Outcome:** clean — no product / skill / test-tree changes.

**discuss (straggler) — acknowledged:** Joan’s plan-time exclusion of `astral.git.engineer-test-tree-ban` assumed no bible path in the ticket deliverable. Betty later added `docs/test-bible/README.md` via `docs(AST-992)` + `merge-tests(AST-992)` (expected Betty sole-authority). Statute verdict remains **conforms**. No code change.

**fix-now:** none.
