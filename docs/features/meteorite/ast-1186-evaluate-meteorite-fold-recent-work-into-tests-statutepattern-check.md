# AST-1186 — evaluate_meteorite: fold recent work into tests + statute/pattern check

<!-- linear-archive: AST-1186 archived 2026-08-17 -->

## Linear archive (AST-1186)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

`evaluate_meteorite` recently became a **standalone twin** of classic JD evaluate (own `TASK_CONFIG` pass/fail/error, own `meteorite_jobdesc_rubric`, own dispatch claim at **METEORITE_QUALIFIED**, own batch entry, Analysis-JD token override) instead of a shared-`evaluate_jd` + meteorite overlay. Product code and a thin component lock already exist, but the test bible and several adjacent docs still describe the obsolete `evaluate_jd`@meteorite / overlay story. This epic reviews that shipped contract against approved patterns and statutes, closes any real conformance gaps (including evaluate_meteorite-related UI), and folds the current twin into bible + component tests so future meteorite GDL work (aliases, groupings) cannot reintroduce the old shape by accident.

## Functional scope

* **Contract inventory:** Review the live `evaluate_meteorite` surface — config orchestration states, dispatch claim at **METEORITE_QUALIFIED**, consult batch twin entry, Analysis-JD meteorite rubric override, craft-rubric / artifact ownership, incomplete-grade retry holding, and **evaluate_meteorite-related UI** (Artifacts Meteorite Criteria / craft-rubric editor wiring and any other operator surfaces that bind to this twin) — and write down what is already true on `origin/dev` vs what tests and bible still claim.
* **Pattern and statute validation:** Check that surface against the Architectural definition citations below. Record each finding as pass, bible/test drift only, or product defect.
* **Conformance fixes (narrow):** When the audit finds a product defect against those citations (wrong overlay still wired for the JD hop, missing twin ownership, illegal not_ready / score-floor coupling, UI still pointed at classic evaluate_jd ownership for meteorite criteria, etc.), fix it in this epic (config, consult, dispatch, and evaluate_meteorite-related UI). Do not redesign meteorite GDL or invent aliases.
* **Bible honesty:** Update `docs/test-bible/**` (especially consult + config + dispatcher notes that still say meteorite GDL entry is `evaluate_jd` overlay / `evaluate_jd`@**METEORITE_QUALIFIED**) so the documented contract matches the standalone twin.
* **Component coverage fold-in:** Extend component tests so the twin contract is locked beyond the existing orchestration/render smoke — dispatch claim key+trigger, rubric/artifact ownership maps, Analysis-JD override for meteorite-sourced jobs, incomplete-grade → **METEORITE_QUALIFIED_RETRY** (not technical fail), and Style D found/recorded on any touched `debug=` evaluate path.
* **Seed/fixture honesty:** Bring the AST-756 expected `agent_task` fixture into lockstep for missing `evaluate_meteorite` / `craft_evaluate_meteorite_rubric` catalog rows (labeled re-baseline), without blind whole-file overwrite of unrelated prompt drift.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — twin orchestration, dispatch specs, rubric ownership, and Analysis-JD override stay config-owned.
  * `pattern.batch.entity-claim-process-release` — evaluate hop keeps claim → process → release; twin key does not invent a new claim shape.
  * `pattern.state.entity-state-transitions` — **METEORITE_PASSED_JD** / **METEORITE_FAILED_JD** / **METEORITE_ERROR_EVALUATE_JD** / **METEORITE_QUALIFIED_RETRY** priors stay registry-true.
  * `pattern.layers.import-discipline` — config/consult/dispatcher/UI changes honor layer bounds.
* **New patterns proposed**
  * none — twin-task shape already matches `meteorite_like` / `meteorite_upshot`; this epic validates and locks it, does not invent a new catalog pattern.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — twin states, artifact keys, dispatch specs, Analysis override live in config.
  * `astral.config.pass-threshold-vs-score-floor` — GDL entry remains ungated (`score_floor` None); do not couple scored not_ready into score-floor claim gating.
  * `astral.patterns.render-verdict-orchestrates-consult` — incomplete vectors → retry holding, not technical fail (AST-1155 family).
  * `astral.batch.claim-process-release` — batch_id-first claim/clear unchanged for the twin batch.
  * `astral.state.job-prior-states-enforced` / `astral.state.core-decides-transitions` — transitions via registry + core, not ad-hoc.
  * `astral.agent.do-task-delegation` — twin still goes through normal agent/consult path.
  * `astral.standards.debug-contract-gated` — Style D on touched `debug=` evaluate surfaces.
  * `astral.standards.no-hardcoded-sets` — no parallel twin maps outside config.
  * `astral.layers.ui-config-driven-business-logic` — evaluate_meteorite-related UI must stay config/DB-driven (no hard-coded classic evaluate_jd ownership for meteorite criteria).
  * `astral.standards.in-scope-only` — do not take qualify_meteorite, gaze_email, aliases (AST-1184), Gaze/Meteorite Review grouping (AST-1183), general UI hardcode audit (AST-1185), or `meteorite_email` rename (AST-1182).
  * `astral.seed.agent-tables-in-repo-json` — fixture/catalog re-baseline for evaluate/craft rows is in scope.

## Boundaries

* Does **not** change `qualify_meteorite`, gaze_email ingest, or Manage Email Create/Land paths.
* Does **not** invent task aliases or retire `METEORITE_GDL_OUTCOME_BY_TASK` for Do/Get (AST-1184).
* Does **not** rename Job Review / add Meteorite Review (AST-1183) or run the general UI hardcode audit (AST-1185) — only evaluate_meteorite-related UI ownership for this twin.
* Does **not** rename `parse_meteorite_email` → `meteorite_email` or change AI email payloads (AST-1182).
* Does **not** rewrite meteorite Do/Get/Like/upshot prompts or convert `evaluate_meteorite` into an alias of `evaluate_jd`.
* Does **not** widen into a full agent_task catalog↔fixture byte-identity campaign beyond the evaluate_meteorite / craft rows.
* Must **not** break classic `evaluate_jd` @ **JD_READY** or vetted-company GDL.

## Acceptance criteria

* A written audit (Linear comment or plan attachment on the child) lists the evaluate_meteorite contract points checked against the Architectural definition, each marked pass / bible-drift / product-defect.
* After the epic, `evaluate_jd` is **not** the meteorite GDL entry key in config or live provisioned meteorite dispatch rows; `evaluate_meteorite` claims **METEORITE_QUALIFIED** (ungated).
* `TASK_CONFIG["evaluate_meteorite"]` owns meteorite JD pass/fail/error directly; `evaluate_jd` is absent from `METEORITE_GDL_OUTCOME_BY_TASK`.
* Analysis-JD for meteorite-sourced jobs resolves to `meteorite_jobdesc_rubric` / owner `evaluate_meteorite`, not classic `jobdesc_rubric` / `evaluate_jd`.
* Incomplete/extra grade vectors on the meteorite evaluate hop land on **METEORITE_QUALIFIED_RETRY** (or the live retry holding for that trigger), never **METEORITE_ERROR_EVALUATE_JD** as a completeness misclassify.
* Evaluate_meteorite-related UI (Meteorite Criteria / craft path) binds to the twin artifact/owner, not classic evaluate_jd ownership.
* Test bible sections that still document meteorite entry as `evaluate_jd` overlay / `evaluate_jd`@**METEORITE_QUALIFIED** are corrected or marked obsolete with the twin truth.
* Component tests fail if the twin contract regresses (orchestration states, dispatch key+trigger, rubric ownership, Analysis override, incomplete→retry).
* Classic `evaluate_jd` @ **JD_READY** behavior and non-meteorite Analysis-JD ownership remain unchanged.
* AST-756 expected fixture includes current `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` rows in lockstep with catalog for those keys (no blind whole-file absorb of unrelated drift).
* If backend `debug=` evaluate paths are touched: Style D index headers show found/recorded detail; no new ungated debug noise.

## Dependencies and blockers

* Soft awareness (not Linear blockedBy): prior Done work that created the twin — AST-1052 / AST-1054 / AST-1060 family, plus incomplete-grade retry AST-1155.
* Soft awareness: AST-756 fixture drift for missing evaluate/craft rows was deferred from AST-1196 (parent AST-1188 Done) — **in scope** here (Archie answered yes).
* Sibling Discussion tickets AST-1182–AST-1185 are adjacent only; none block this definition.
* Intake source AST-1181 remains Backlog — out of scope for this epic (never touch Backlog).

none as Linear blockedBy.

## Open questions

none — Archie answered in Discussion: (1) all evaluate_meteorite-related work including UI/config; (2) fix product defects in this epic; (3) include AST-756 fixture lockstep for evaluate/craft rows.

## Proposed child tickets

#### 1!: **evaluate_meteorite twin audit + conformance fixes - Ada**

Owns inventory of the live twin contract vs Architectural definition (config, consult, dispatch, and evaluate_meteorite-related UI), and any narrow product fixes required for pass. Posts the audit pass/drift/defect list. Does **not** own bible/component fold-in (sibling #2) or fixture re-baseline (sibling #3).
**Citations:** `pattern.config.config-block`; `pattern.batch.entity-claim-process-release`; `pattern.state.entity-state-transitions`; `astral.config.config-source-of-truth`; `astral.config.pass-threshold-vs-score-floor`; `astral.patterns.render-verdict-orchestrates-consult`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`.

#### 2: **Bible + component tests lock twin contract - Hedy**

After #1 (or in parallel once audit says no product blockers): retire obsolete bible claims that meteorite GDL entry is `evaluate_jd` overlay / `evaluate_jd`@**METEORITE_QUALIFIED**; extend component tests for dispatch key+trigger, rubric ownership, Analysis-JD override, incomplete→retry, and Style D on touched debug paths. Does **not** invent aliases or rewrite qualify paths.
**Citations:** `astral.standards.debug-contract-gated`; `astral.standards.no-hardcoded-sets`; `astral.batch.claim-process-release`; `astral.standards.in-scope-only`.

#### 3: **AST-756 fixture lockstep for evaluate/craft rows - Katherine**

After or with #2: surgical fixture update so expected `agent_task` includes current `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` catalog rows; no blind whole-file absorb of unrelated prompt drift.
**Citations:** `astral.seed.agent-tables-in-repo-json`; `astral.standards.in-scope-only`.

**New patterns:** none.

**Monolith check:** Functional scope has 6 capabilities; 3 children split audit/fix, test lock, and fixture — intentional.

---

## Original brief

From AST-1181:

* Review the changes recently made for evaluate_meteorite and incorporate the work in the test cases and validate against patterns and statutes

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1186 (parent) | ftr/AST-1186-evaluate-meteorite-fold-recent-work-into-tests |
| AST-1209 | sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes |
| AST-1210 | sub/AST-1186/AST-1210-bible-component-tests-lock-twin-contract |
| AST-1211 | sub/AST-1186/AST-1211-ast-756-fixture-lockstep-for-evaluate-craft-rows |

**Epic worktree:** `astral-AST-1186/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/e49a2bdbed5d3795886bd7895b100271/67a45e07-4ed3-4f9a-af60-b3e9c77eb88b/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/e49a2bdbed5d3795886bd7895b100271/8a5c3e14-8f69-4247-a7fa-c183cacc0a27/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/e49a2bdbed5d3795886bd7895b100271/be7babca-9438-446b-ab45-582720ca1dc2/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/01edba47-b824-45b4-a316-4cee2dbbf70c/store.db` |
| Radia | review | `/home/susan/.cursor/chats/e49a2bdbed5d3795886bd7895b100271/6561f5f6-c45c-4686-8c88-2339d5836b13/store.db` |

### Comments

#### chuckles — 2026-08-06T02:43:11.975Z
@susan

1. Confirm "recent work" boundary: standalone twin contract only (TASK_CONFIG + batch + dispatch @ METEORITE_QUALIFIED + meteorite_jobdesc_rubric/craft ownership + Analysis-JD override + incomplete→METEORITE_QUALIFIED_RETRY) — not qualify/gaze/aliases/groupings. Expand or shrink?
2. Product defects found in the audit: fix inside this epic (default), or file separate Discussion children and keep this epic test/bible-only?
3. Include labeled AST-756 fixture re-baseline for missing evaluate_meteorite / craft_evaluate_meteorite_rubric rows (surgical)? Or defer again?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
