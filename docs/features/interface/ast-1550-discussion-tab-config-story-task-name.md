# AST-1550 — Discussion tab config + story task_name

**Linear:** [AST-1550](https://linear.app/astralcareermatch/issue/AST-1550/discussion-tab-config-story-task-name-add-discussion-tab-to-recommended)  
**Parent:** [AST-1541 — Add "Discussion" tab to Recommended Job modal](https://linear.app/astralcareermatch/issue/AST-1541/add-discussion-tab-to-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-1541/AST-1550-discussion-tab-config-story-task-name`

Register **Discussion** on `JOBS_RECOMMENDED_REPORT_TOP_TABS` (immediately after Artifacts), expose an ordered nine-hop Discussion section list (keys + `task_name` labels, all `default_expanded: false`) on the recommended-report UI manifest, and enrich `get_entity_agent_story` entries with `task_name` from the live `agent_task` row. Does **not** own the React Discussion pane (sibling AST-1551 / child #2).

---

## Explicit scope gate

Ticket **## Scope** (only surfaces this plan may touch):

- `src/utils/config.py` — Discussion top tab + hop-order source
- `src/ui/api/api_system.py` — manifest Discussion sections
- `src/core/agent.py` — `task_name` on story entries

Every **Files Changed** row and every Stage step names only those files / that kind of change. No React, no `api_jobs.py`, no Job Detail Agent Story UI, no artifact generation.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Append Discussion to `JOBS_RECOMMENDED_REPORT_TOP_TABS`; add public hop-order walk from `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"]` via live `agent_task.run_next` | utils |
| `src/ui/api/api_system.py` | On `GET /api/state_ui_manifest`, attach `jobs.recommended.report_discussion_sections` (nine section defs from the walk + `task_name` / `task_key` labels, `default_expanded: false`) | ui |
| `src/core/agent.py` | In `get_entity_agent_story`, attach `task_name` from the current `agent_task` row when non-empty | core |

**Out of scope:** `JobAnalysisReportModal.tsx` / `JobDiscussionPane.tsx` / `App.css` / `AgentStoryTab.tsx` (sibling #2); Job Detail / Company Detail Agent Story behavior; artifact generation; Analysis / Summary bodies; `tests/` / bible (Betty).

**Sibling consume contract (AST-1551 — do not implement here):**

| Manifest / API field | Shape | UI use |
|----------------------|-------|--------|
| `jobs.recommended.report_top_tabs` | includes `{tab_id: "discussion", nav_label: "Discussion"}` after Artifacts | top-tab chrome (already driven by `report_top_tabs`) |
| `jobs.recommended.report_discussion_sections` | `[{section_id, nav_label, default_expanded}, …]` length 9 | Discussion pane section list |
| `agent_story[].task_name` | optional string | header label when present; else `task_key` |

---

## Stage 1: Config — Discussion top tab + hop-order walk

**Done when:** `JOBS_RECOMMENDED_REPORT_TOP_TABS` ends with Summary → Analysis → Artifacts → **Discussion**; a public config helper returns the live BUILD_ARTIFACTS daisy-chain task_keys starting at `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"]` (`contemplate_job`) and ending when `run_next` is empty (today: nine keys through `propose_application_responses`). No API or story behavior change yet.

1. In `src/utils/config.py`, immediately after the existing Artifacts entry in `JOBS_RECOMMENDED_REPORT_TOP_TABS`, append:

   ```python
   {"tab_id": "discussion", "nav_label": "Discussion"},
   ```

   Do **not** reorder Summary / Analysis / Artifacts. Comment the block as AST-1550 (Discussion after Artifacts).

2. In `src/utils/config.py`, near the other BUILD_ARTIFACTS / `resume_artifact_chain` helpers (after `is_build_artifacts_in_progress` / the `_rac` assert block is fine — same concern area), add a **public** function:

   ```python
   def build_artifacts_discussion_hop_task_keys() -> list[str]:
       """Live run_next walk for Recommended Job Report Discussion sections (AST-1550).

       Starts at BUILD_CONFIG['resume_artifact_chain']['first_task_key'] (contemplate_job).
       Follows current agent_task.run_next until empty. Cycle → RuntimeError.
       Does not include anticipate_scan (not on this chain).
       """
   ```

   Implementation rules (literal):

   - Late-import `get_agent_task` from `src.data.database` inside the function (same pattern as `_agent_task_parents_with_run_next` — utils must not import data at module load).
   - `start = (BUILD_CONFIG.get("resume_artifact_chain") or {}).get("first_task_key")` stripped; if empty, return `[]`.
   - Walk: append key → read `(get_agent_task(key) or {}).get("run_next")` stripped → next key; stop when next is empty.
   - If a key repeats, `raise RuntimeError(f"build_artifacts discussion run_next cycle at {key!r}")` (same discipline as `_walk_requested_artifacts_chain_task_keys` in `candidate.py`).
   - Do **not** hardcode the nine task_key strings in a list. Do **not** add a parallel `hop_task_keys` array under `BUILD_CONFIG["resume_artifact_chain"]` (that list was retired; membership is live `run_next`).

⚠️ **Decision:** Walk from `first_task_key` via live `run_next` rather than a static nine-key list — satisfies `astral.standards.no-hardcoded-sets` / parent Technical scope. Starting at `resume_artifact_chain.first_task_key` excludes `anticipate_scan` without naming it. Terminal is empty `run_next` (today `propose_application_responses`); do not special-case that key unless the walk would otherwise continue past it.

---

## Stage 2: api_system — attach Discussion section defs on the recommended manifest

**Done when:** `GET /api/state_ui_manifest` includes `jobs.recommended.report_discussion_sections` as an ordered list of nine `{section_id, nav_label, default_expanded: false}` objects where `section_id` is the hop `task_key` and `nav_label` is that hop’s `agent_task.task_name` when non-empty, else `task_key`. Walk/DB failure degrades to `[]` with a warning (rest of manifest still 200). Discussion already appears in `report_top_tabs` via Stage 1’s `list(JOBS_RECOMMENDED_REPORT_TOP_TABS)` inside `build_state_ui_manifest()` — do not duplicate the top-tab entry here.

1. In `src/ui/api/api_system.py`, import `build_artifacts_discussion_hop_task_keys` from `src.utils.config` (add to the existing config import block).

2. Import `get_agent_task` from `src.data.database` (UI → data is allowed; `api_admin` already uses it). Prefer a top-level import next to other data/core imports, or a late import inside the try block if that keeps the module header cleaner — either is fine; pick one and stay consistent with nearby code in this file.

3. In `state_ui_manifest()`, after `manifest = build_state_ui_manifest()` and **before** `return jsonify(manifest)`, attach Discussion sections. Mirror the AST-1253 soft-fail pattern used for `artifacts_chain_*` on the same endpoint:

   ```python
   try:
       sections = []
       for task_key in build_artifacts_discussion_hop_task_keys():
           row = get_agent_task(task_key) or {}
           name = (row.get("task_name") or "").strip()
           sections.append({
               "section_id": task_key,
               "nav_label": name or task_key,
               "default_expanded": False,
           })
       manifest.setdefault("jobs", {}).setdefault("recommended", {})[
           "report_discussion_sections"
       ] = sections
   except Exception as exc:
       _log.warning("discussion sections manifest walk failed: %s", exc)
       manifest.setdefault("jobs", {}).setdefault("recommended", {})[
           "report_discussion_sections"
       ] = []
   ```

4. Do **not** put `report_discussion_sections` inside `build_state_ui_manifest()` in config — ticket Scope assigns manifest Discussion sections to `api_system.py` (live `task_name` at request time, same reason AST-1253 enriches outside the pure config builder).

5. Do **not** change frontend TypeScript types in this ticket (sibling #2 / Katherine). Backend key name is exactly `report_discussion_sections`.

⚠️ **Decision:** Soft-fail to `[]` on walk failure so a broken `agent_task` chain cannot 500 the whole state-UI manifest (matches AST-1253). Healthy DB today yields exactly nine sections; Betty owns asserting that count.

---

## Stage 3: agent — `task_name` on `get_entity_agent_story` entries

**Done when:** Each enriched story entry from `get_entity_agent_story` includes `task_name` when the current `agent_task` row for that entry’s `task_key` has a non-empty `task_name`; when blank/missing, the key is **omitted** (UI falls back to `task_key`). Applies to job / company / candidate stories alike (additive field; Agent Story tabs unchanged). No change to block filtering, scored-task enrichment, or soft-fail behavior.

1. In `src/core/agent.py`, inside `get_entity_agent_story`, in the loop that builds each `entry` (after `task_key = e.get("task_key", "")` is known, and when assembling `entry = {**e, "blocks": blocks}` / before `enriched.append(entry)`):

   - Call `get_agent_task(task_key)` (already imported at module top from `src.data.database`).
   - `name = ((get_agent_task(task_key) or {}).get("task_name") or "").strip()`
   - If `name`: set `entry["task_name"] = name`.
   - If not `name`: do **not** set `task_name` to `""` — omit the key.

2. Prefer a single `get_agent_task` call per entry (reuse the row if you already fetch it for something else in the same iteration — today you do not). Do **not** batch-load all tasks unless an existing helper already does that; N is small (latest-per-task refs).

3. Do **not** change `_filter_response_block`, scored `vector_grades` / `rubric_artifact` attachment, or the soft-fail paths around `list_entity_latest_agent_refs` / `get_agent_data`.

⚠️ **Decision:** Omit empty `task_name` rather than sending `""` — matches parent Technical (“empty → omit / UI falls back to `task_key`”) and keeps payloads clean for siblings that check truthiness.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1541/AST-1550-discussion-tab-config-story-task-name`.
- Do not add files, modules, or frontend edits not listed above.
- Ambiguity / drift → comment on **parent** AST-1541 with the Stage blocked template; stop.

---

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1550
**Overall:** APPROVED
**Publish ref:** `sub/AST-1541/AST-1550-discussion-tab-config-story-task-name` @ `6a05e07e893fa93469e42cb0547da4b277711981`

## Traceability
AC1 → Stage 1 (`JOBS_RECOMMENDED_REPORT_TOP_TABS` → `build_state_ui_manifest` `report_top_tabs`); AC2 → Stages 2–3 (`report_discussion_sections` manifest labels + `get_entity_agent_story` `task_name` enrichment). Parent AC2/4–7 N/A — sibling AST-1551 (React pane / RESPONSE bodies).

## Findings

### acceptable — `astral.standards.utils-data-late-import-only` vs in-tree precedent
**Location:** Stage 1 (`build_artifacts_discussion_hop_task_keys` late-imports `get_agent_task` in `config.py`)
**Finding:** Statute text forbids utils→data late-import outside `logging.py`; the same file already uses that pattern in `_agent_task_parents_with_run_next` / `dispatch_chain_row_matches_job`. Parent Component/Technical scope assigns the hop walk to `config.py`; core’s `_current_agent_task_run_next` is not importable from utils.
**Recommendation:** Proceed as planned — matches parent definition and existing config chain helpers. Not a plan defect.

context_tokens≈52000
```

---

## Self-Assessment

**Scope:** `Single-Component` — config top tab + hop walk, api_system Discussion sections, agent story `task_name`; no React pane.

**Conf:** `High` — live `run_next` walk mirrors AST-1253; nine hops verified against DB; additive `task_name` field.

**Risk:** `Low` — soft-fail empty sections if walk fails; empty `task_name` omitted (UI falls back to `task_key`).

---

## Review

**Built:** `origin/sub/AST-1541/AST-1550-discussion-tab-config-story-task-name` @ `7b103e5a6be93581bff8a1d6f69d2df77281d497`

Stages 1–3: Discussion on `JOBS_RECOMMENDED_REPORT_TOP_TABS`; `build_artifacts_discussion_hop_task_keys`; `report_discussion_sections` on `state_ui_manifest`; `task_name` on `get_entity_agent_story`. Tests deferred to Betty.

## Radia review

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1550
**Publish ref:** `sub/AST-1541/AST-1550-discussion-tab-config-story-task-name` @ `814c237ca81681a24d2eea0153e19277bc074e84`
**Overall:** FIX-NOW

**Diff baseline:** `origin/dev...origin/sub/AST-1541/AST-1550-discussion-tab-config-story-task-name` (12 files; product: `src/utils/config.py`, `src/ui/api/api_system.py`, `src/core/agent.py`)

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match plan literally |
| orch.roles.archie-approves-statutes | universal | conforms | N/A to diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1550)` @ `814c237c` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` prefixes used |
| orch.git.flow-direction-inviolable | universal | conforms | Sub-branch publish ref |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1541/AST-1550-…` |
| orch.git.merge-on-checkout | universal | conforms | N/A to review |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No evidence in diff |
| orch.git.no-dev-agent-branches | universal | conforms | Sub publish ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree AST-1541 |
| orch.git.three-permanent-branches | universal | conforms | Sub topology correct |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-policy drift |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A |
| orch.pipeline.status-gates-skill-entry | universal | needs-discussion | Tests Passed but Toast cases appear red on tip (see fix-now) |
| orch.roles.archie-approves-statutes | universal | conforms | — |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible edits on Betty path |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook violations visible |
| astral.agent.confidence-bounds | scoped | not-applicable | No agent confidence paths touched |
| astral.agent.do-task-delegation | scoped | not-applicable | No do_task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | Story enrichment only; no grade logic change |
| astral.batch.batch-id-first | scoped | not-applicable | No batch paths |
| astral.batch.batch-id-format | scoped | not-applicable | No batch paths |
| astral.batch.claim-process-release | scoped | not-applicable | No dispatcher/claim changes |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No batch read path changes |
| astral.config.config-source-of-truth | scoped | conforms | Tabs/sections sourced from config + live agent_task |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env changes |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spikes |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | Hop walk follows live `run_next` |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No seed/dispatch rows |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan doc for AST-1550 |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Engineer src only; Betty test tree |
| astral.git.engineer-test-tree-ban | scoped | not-applicable | Engineer did not land tests |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `state_ui_manifest` remains `@require_auth` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | No external layer |
| astral.layers.import-direction | scoped | conforms | ui→data allowed; utils late-import matches file precedent |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Discussion chrome config-driven |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON edits |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No catalog conflict |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | Request-time manifest enrichment only |
| astral.seed.define-approved | scoped | not-applicable | Post-plan build |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No seed rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage join |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No data layer changes |
| astral.standards.database-header-inventory | scoped | not-applicable | No DB schema/SQL |
| astral.standards.debug-contract-gated | scoped | not-applicable | No debug= emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Focused helpers; walk parallels existing chain walkers |
| astral.standards.in-scope-only | scoped | conforms | Src touches limited to plan’s three files |
| astral.standards.logging-via-utils | scoped | conforms | `_log.warning` via `get_logger` |
| astral.standards.names-not-ticket-ids | scoped | conforms | Public names domain-shaped |
| astral.standards.no-cross-contamination | scoped | conforms | No out-of-layer src deps |
| astral.standards.no-hardcoded-sets | scoped | conforms | Nine-hop list from live `run_next`, not static array |
| astral.standards.public-then-helpers | scoped | conforms | `build_artifacts_discussion_hop_task_keys` public |
| astral.standards.utils-data-late-import-only | scoped | conforms | Late-import in `config.py` — Joan-approved + `_agent_task_parents_with_run_next` precedent |
| astral.state.core-decides-transitions | scoped | not-applicable | No state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job state enforcement |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | Manifest walk only; no run loop |
| astral.ui.frontend-file-placement | scoped | not-applicable | No frontend src in diff |
| astral.ui.naming-conventions | scoped | not-applicable | No frontend src |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server config |

**Active set scored:** 64 statute ids from registry (excludes namespace path rows). **0 violates** in product `src/`. **1 needs-discussion** (status gate vs Toast red tests).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan/parent cite no `canon/patterns/**` ids; AST-1253 soft-fail shape reused by convention |

## Plan adherence

Stages 1–3 land as specified:

- **Stage 1:** `JOBS_RECOMMENDED_REPORT_TOP_TABS` gains Discussion after Artifacts; `build_artifacts_discussion_hop_task_keys()` walks `resume_artifact_chain.first_task_key` via live `run_next` with cycle guard.
- **Stage 2:** `state_ui_manifest()` attaches `jobs.recommended.report_discussion_sections` outside `build_state_ui_manifest()`, soft-fails to `[]` on walk/DB error (AST-1253 mirror).
- **Stage 3:** `get_entity_agent_story` adds optional `task_name` when non-empty; omits key when blank.

Estimate **3** still fits the real footprint. Scope gate honored for **product** `src/`. **Test-tree scope bleed** from sibling AST-1549/AST-1553 (below) is outside the plan gate.

Joan plan-rubric **APPROVED** @ `6a05e07e`; `astral.standards.utils-data-late-import-only` flagged acceptable there — justification chain satisfied by existing `config.py` chain helpers. No straggler excluded statute scored in-scope.

## Findings

### fix-now — Sibling Toast tests on AST-1550 publish ref without product code

**Location:** `tests/component/frontend/components/test_Toast.test.tsx` (in diff; commit `72b918e3` `test(AST-1553)` on sub)

**Finding:** Three test cases assert AST-1549/AST-1553 Toast behavior (`\u26A0` error glyph, `.toast-copy-target`, `Dismiss` button / no-copy-on-dismiss). `src/ui/frontend/src/components/Toast.tsx` is **unchanged** on tip `814c237c` vs `origin/dev` — still uses `\u2717`, whole-toast click, no Dismiss. Static review: at least `shows success, error, and default info variants`, `error toast is clickable and copies diagnostic bundle`, and `AST-1553: dismiss closes error toast without copying` will fail if the frontend component suite runs on this ref.

**Why fix-now:** Publish ref is not self-consistent; `Tests Passed` is misleading for anyone running `test_Toast.test.tsx`. Not AST-1550 product scope — Betty/Chuckles should revert or relocate these deltas to the AST-1553/1549 sub (or land sibling product first), not route to Ada via `resolve-child`.

### discuss — Cross-ticket test commit on child sub

**Location:** Branch history: `72b918e3 test(AST-1553)` precedes `merge-tests(AST-1550)`

**Finding:** AST-1553 test work sits on the AST-1550 publish ref alongside Betty’s AST-1550 manifest. `orch.git.betty-merge-tests-one-sha` is satisfied (one merge-tests), but the direct `test(AST-1553)` commit blurs sibling boundaries under parent AST-1541.

**Question:** Was Tests Passed gated on a manifest that excluded `test_Toast.test.tsx`? If yes, document manifest scope on the issue; if no, status should not have advanced.

### advisory — Duplicate walk pattern

**Location:** `src/utils/config.py` `build_artifacts_discussion_hop_task_keys` vs `src/core/candidate.py` `_walk_requested_artifacts_chain_task_keys`

**Finding:** Same run_next-walk shape, different start keys/layers. Layer law prevents utils→core import; duplication is bounded and acceptable. Optional future consolidation if a shared utils walker emerges.

### advisory — Per-hop double `get_agent_task` in manifest path

**Location:** `src/ui/api/api_system.py` `state_ui_manifest` loop + internal walk in `build_artifacts_discussion_hop_task_keys`

**Finding:** ~2 DB reads per hop (N≤9). Within plan’s “N is small” allowance; optimize only if profiling warrants.

## What’s solid

- Product implementation is plan-faithful and ready for sibling AST-1551 consume contract.
- Cycle detection and empty-`first_task_key` → `[]` behavior tested.
- `task_name` omission-on-blank matches parent Technical and keeps payloads clean.
- AST-1550-scoped tests (`test_config`, `test_api_system`, `test_agent`) align with manifest intent.
- Soft-fail manifest enrichment preserves 200 on broken chains.

## Frame diff

- `JOBS_RECOMMENDED_REPORT_TOP_TABS`: +`discussion` tab after `artifacts`
- `GET /api/state_ui_manifest`: +`jobs.recommended.report_discussion_sections` `[{section_id, nav_label, default_expanded}]`
- `get_entity_agent_story` entries: +optional `task_name` string
- **Out of frame (on diff):** `test_Toast.test.tsx` AST-1549/1553 expectations — sibling tickets, no matching `Toast.tsx` change

## Recommended actions (downstream — not Radia)

1. **Betty/Chuckles:** Remove or relocate `test_Toast.test.tsx` AST-1549/1553 deltas from `sub/AST-1541/AST-1550-…`; keep AST-1550 tests only on this ref.
2. **Chuckles:** Confirm Tests Passed manifest excluded Toast; if not, regress status until test tree is green on tip.
3. **Ada / resolve-child:** No product `src/` fixes required for AST-1550 scope once test-tree fix-now is handled separately.

**Notes:** Joan validate artifact attached; no excluded statute straggler. Product `src/` alone would be **CLEAN / PROCEED**.

context_tokens≈72000

---

[code-rubric] REVIEW (Commit: 814c237c) Sibling Toast tests orphan
```

---

## Resolution

**Date:** 2026-08-31  
**Resolve tip (pre-push):** Betty Toast restore `9d57e822` on `origin/sub/AST-1541/AST-1550-discussion-tab-config-story-task-name`; product `src/` unchanged for review findings.

### fix-now — Sibling Toast tests

**Handled by Betty** (not Ada product): `9d57e822 test(AST-1550): restore Toast tests to origin/dev — drop sibling bleed`. `tests/component/frontend/components/test_Toast.test.tsx` matches `origin/dev` (empty diff). No `src/` fix-now required (spawn + Radia recommended action #3).

### discuss — Cross-ticket test commit / Tests Passed gate

**Answer:** Yes — Tests Passed was gated on Betty’s AST-1550 manifest only (bible `docs/test-bible/utils/config.md` § AST-1550 / Linear “Discussion QA ready”):

1. `tests/component/utils/test_config.py::TestAst1550DiscussionHopKeys`
2. `tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs`
3. `tests/component/ui/api/test_api_system.py::TestAst1550ReportDiscussionSections`
4. `tests/component/core/test_agent.py::TestAst1550AgentStoryTaskName`

`test_Toast.test.tsx` was **not** on that manifest. Toast bleed is now restored to `origin/dev` on this publish ref.

### advisory — Duplicate walk pattern

**Deferred:** Bounded utils vs core duplication; layer law blocks utils→core. No change this pass.

### advisory — Per-hop double `get_agent_task`

**Deferred:** N≤9; within plan allowance. No change this pass.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/81753492fa55c6a6a65968555e8f5c14/46b16373-da34-4f04-969b-131d1152b981/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/81753492fa55c6a6a65968555e8f5c14/c4f93f7e-ea37-43b5-a6fa-25c31c425e47/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/f9e04fce-94bf-4b71-92a7-cbbe544ee513/store.db` |
| Radia | review | `/home/susan/.cursor/chats/81753492fa55c6a6a65968555e8f5c14/f48c9428-ac74-4cbe-b103-23a94ed994d1/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1541 (parent) | ftr/AST-1541-discussion-tab-recommended-job-modal |
| AST-1550 | sub/AST-1541/AST-1550-discussion-tab-config-story-task-name |
| AST-1551 | sub/AST-1541/AST-1551-discussion-pane-recommended-job-report |

**Epic worktree:** `astral-AST-1541/` — one active sub checked out at a time.
