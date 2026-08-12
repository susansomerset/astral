<!-- linear-archive: AST-1106 archived 2026-08-11 -->

## Linear archive (AST-1106)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1106/uat-gaze-email-missing-from-scheduled-actions-default-view  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1087 — Add gaze_email as a dispatch task  
**Blocked by / blocks / related:** parent: AST-1087

### Description

## What failed

On staging Task Dispatcher / Scheduled Actions after AST-1087 landed, Susan cannot find the `gaze_email` task at all (“I still don't see the gaze email task”).

## Expected

The shared null-`candidate_id` `gaze_email` `dispatch_task` row is visible and operable in Scheduled Actions / Task Dispatcher without hunting past filters that permanently hide mailbox tasks.

## Repro

1. Open Admin → Scheduled Actions (Task Dispatcher) on staging after deploy of AST-1087.
2. Leave default filters (notably Avail **> 0**).
3. Look for `gaze_email` (shared inbox / null candidate row).
4. Observe: row is missing from the default view (or not present at all).

## Parent AC (quoted inline)

> 1. With a `gaze_email` `dispatch_task` row (`candidate_id` null, `auto_mode` true) running under normal dispatch, a bound inbox message matching each in-scope shape produces the corresponding **METEORITE_NEW** job(s) for that candidate (including subject+body appended when a job link was scraped), and the message is archived afterward.
> 2. The `dispatch_task` schema/provision path allows `candidate_id` null for `gaze_email` (no table-level requirement that every dispatch row have a candidate).

## Diagnosis

* **Hypothesis:** Default Scheduled Actions filter `availGtZeroFilter="gt0"` hides rows with `available_count === 0`. For `gaze_email`, list enrichment sets `available_count=0` whenever `entity_type` / `trigger_state` / `candidate_id` are missing — which is intentional for this mailbox task — so the row is invisible under the default filter even when provisioned. Secondary: `gaze_email` has no `agent_task.json` catalog row (unlike `parse_meteorite_email`), so Task Prompts / section meta also omit it.
* **Correct outcome:** Susan can see and run/flip AUTO on the shared `gaze_email` row in the admin dispatcher without clearing obscure filters; catalog meta exists so it groups sanely.
* **Wrong fix to avoid:** Fake a non-zero `available_count` for mailbox tasks; delete the Avail filter entirely without a mailbox carve-out; require a fake candidate_id just to show in UI.
* **Related siblings / contracts:** AST-1088 provision/ensure null-candidate row; AST-1090 runner; do not change Ruth parse (AST-1089) contracts.

## Boundaries

* This bug does **not** change: Gmail scopes, Ruth parse prompts, meteorite create/dedupe rules, or Manage Email UI.
* "No more missing row" alone is **not** done — Parent AC + Correct outcome must hold (row visible + operable under normal admin use).

## In scope

- [X] `astral.config.config-source-of-truth` — Avail-gt0 always-visible task keys in `ADMIN_CONFIG`, seeded from `GAZE_EMAIL_CONFIG["task_key"]`
- [X] `astral.standards.no-hardcoded-sets` — no React `gaze_email` visibility set; API boolean only
- [X] `astral.layers.ui-config-driven-business-logic` — carve-out resolved in `list_dtasks` from config; frontend honors the flag
- [X] `astral.ui.frontend-file-placement` — Scheduled Actions page filter only
- [X] `astral.standards.in-scope-only` — visibility + catalog meta only; no Gmail/Ruth/runner changes

## Considered but excluded

- [X] Fake non-zero `available_count` for mailbox shells — Diagnosis wrong fix
- [X] Delete default Avail gt0 without carve-out — Diagnosis wrong fix; preserves AST-894 default
- [X] Fake `candidate_id` to pass enrichment — Diagnosis wrong fix
- [X] AST-1089 Ruth `parse_meteorite_email` prompts / TASK_CONFIG — sibling contract
- [X] AST-1090 runner / due wiring — sibling contract
- [X] AST-1107 bulk `task_name := task_key` for all catalog rows — sibling UAT bug (new `gaze_email` row already uses `task_name=gaze_email`)
- [X] `astral.layers.core-vs-external-bright-line` — no Gmail I/O on this ticket
- [X] `pattern.state.entity-state-transitions` — no job state hops

### Comments

#### betty — 2026-07-31T18:12:27.539Z
Hygiene fix for Chuckles merge-child block — **User Testing / Ada unchanged**.

**Done:**
- Squashed Betty deliveries on `origin/tests` → single `714eec8a` (`test(AST-1106): SA Avail gt0 always-visible carve-out + gaze_email catalog`).
- Rebuilt `origin/sub/AST-1087/AST-1106-…` from product tip `ace6c669` with **exactly one** `merge-tests(AST-1106): origin/tests 714eec8a…` (`deec7fcd`), then replayed Radia `docs` + Ada `resolve`.
- Tip tree == pre-rewrite tip (`6a9274a7…`); plan/code/test/docs/resolve subjects intact.

**validate-sub-log:** `merge-tests(AST-1106)` count in `--not ftr` range = **1** (duplicate check passes).

Note: full script still hits a **pre-existing** `Merge remote-tracking branch 'origin/dev' into tmp-refresh-…` ancestor in the `--not ftr` range (unrelated to AST-1106; was masked when duplicate failed first). Not introduced by this rewrite.

Tip: `dd597e30`

— Betty

#### chuckles — 2026-07-31T18:08:43.327Z
[merge-child] blocked: duplicate merge-tests(AST-1106) on sub — count=2 (amend on tests, one merge-tests only)

@Betty — squash/hygiene so origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view has a single merge-tests(AST-1106): tip, then Chuckles re-runs merge-child.

— Chuckles

#### ada — 2026-07-31T18:08:20.980Z
Resolve clean — no product fix-now.

Radia **discuss** on dual `merge-tests(AST-1106)` (`6c612416` + `625b2f08` after conflict recovery) is **process-only**; product tip accepted. @Chuckles Cursor / @Betty White — confirm whether that recovery second merge-tests is OK under `orch.git.betty-merge-tests-one-sha`.

`origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view` @ `f4b43e82` · §9a clean vs dev + ftr.

#### radia — 2026-07-31T18:06:59.002Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1106
**Publish ref:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view` tip `6c546ee0fe9d456f4d44db6384868994005d9e81` (product tip reviewed `a08eb40d`; docs() `6c546ee0`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | needs-discussion | Two `merge-tests(AST-1106)` on tip after conflict recovery |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/docs/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Published to origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1087/AST-1106-…` under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | ftr already up to date |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in history |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named epic branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1087 |
| orch.git.three-permanent-branches | universal | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis + wrong-fix list documented |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–4(+4b) match Files Changed |
| orch.pipeline.project-scoped-queues | universal | conforms | Meteorite child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected |
| astral.agent.confidence-bounds | scoped | conforms | No graded path |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths {core} no match |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths {core} no match |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths no match |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths no match |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths no match |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths no match |
| astral.config.config-source-of-truth | scoped | conforms | Always-visible keys in ADMIN_CONFIG from GAZE_EMAIL_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scored consult path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets added |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan docs, not spikes |
| astral.dispatch.seed-auto-false | scoped | conforms | Tip keeps GAZE_EMAIL_CONFIG auto_mode False; ticket does not seed AUTO-true |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One AST-1106 plan file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths no match |
| astral.layers.import-direction | scoped | conforms | ui←utils only for helper |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Carve-out resolved in API; React honors boolean |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths no match |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths no match |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | list_dtasks remains @require_admin |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new swallow in API path |
| astral.standards.database-header-inventory | scoped | not-applicable | layers {data} no match |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug paths |
| astral.standards.dry-and-focused-functions | scoped | conforms | Small helper + stamp + filter predicate |
| astral.standards.in-scope-only | scoped | conforms | Visibility + catalog only; no Gmail/Ruth/runner |
| astral.standards.logging-via-utils | scoped | conforms | No new logging surface |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in utils/ui/admin seed |
| astral.standards.no-hardcoded-sets | scoped | conforms | No React gaze_email visibility set |
| astral.standards.public-then-helpers | scoped | conforms | Public frozenset accessor |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data import |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths no match |
| astral.state.job-prior-states-enforced | scoped | conforms | No job transitions |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths no match |
| astral.ui.frontend-file-placement | scoped | conforms | Change in AdminScheduledActions page only |
| astral.ui.naming-conventions | scoped | conforms | API snake_case flag; TS mirrors |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker changes |

## Pattern conformance

- none cited beyond description statute ids (covered in table)

## Plan adherence

Self-Assessment Scope `MAJOR-CHANGE` matches utils/API/React/catalog footprint. Stages 1–4(+4b null-safe Candidate) delivered. Wrong fixes avoided (no fake avail, no deleting Avail default, no fake candidate_id).

## Findings

**discuss:** Two `merge-tests(AST-1106)` commits on the sub (`6c612416` then `625b2f08`) after conflict-marker recovery tests. Statute wants exactly one merge-tests SHA per child. Product tip is coherent; ask Betty/Chuckles whether recovery merge is acceptable or needs process follow-up. No product rewrite required from Ada for this item.

**advisory:** no plan-rubric verdict attached.

### What’s solid

Config-driven always-visible carve-out; API boolean; SA filter honors flag; gaze_email catalog groups under Job Review; null Candidate cell safe.

### Recommended actions

1. Process discuss on dual merge-tests (Betty/Chuckles).
2. No product fix-now.

context_tokens≈42000

#### betty — 2026-07-31T18:02:54.624Z
## QA test manifest — AST-1106

**Publish tip:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view` @ `a08eb40d`
**Delivery:** `957437a8` (coverage) + follow-up marker strip @ tip (merge conflict cleanup on sub)
**Null-safe Candidate cell:** verified `row.candidate_id || "—"` on tip (`64431acd`)

### Run (epic worktree on publish tip)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1106AlwaysVisibleUnderAvailGt0 \
  tests/component/ui/api/test_api_admin.py::TestAst1106ListDtasksAlwaysVisibleFlag \
  tests/component/core/test_repo_admin_json.py::TestAst1106GazeEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  -q

cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions_AST1106.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-1106|AST-887|AST-894"
```

### Manifest

1. **Config always-visible keys** — `TestAst1106AlwaysVisibleUnderAvailGt0` (frozenset seeded from `GAZE_EMAIL_CONFIG["task_key"]`).
2. **API stamp** — `TestAst1106ListDtasksAlwaysVisibleFlag` (`always_visible_under_avail_gt0` true for gaze_email; avail stays 0; others false).
3. **SA Avail gt0 carve-out + null-safe Candidate (§6c)** — `test_AdminScheduledActions_AST1106.test.tsx` (flag keeps mailbox row under default gt0; non-flag zero-avail still hidden; Candidate cell `—` for null id).
4. **Catalog** — `TestAst1106GazeEmailCatalogRow` (Job Review empty-prompt shell, seq 2.3); revised **`TestAst786AgentTaskRepoJsonSeed`** 47→48 + `gaze_email` in frozenset.
5. **Regression** — re-run AST-887 / AST-894 Avail default predicates in `test_AdminScheduledActions.test.tsx`.

### Broken / obsolete (revised this pass)

- AST-786 **47**-row catalog asserts → **48**.

### Integration

none

### Bible shasums (on publish tip)

- `docs/test-bible/utils/config.md` — `32cdd9f22ffaf515e6e5d1ec7e02213f5dff70e2fe168d9ad70d4ee5e761db67`
- `docs/test-bible/ui/api/api_admin.md` — `6a346b6b419ce8b7b1bd3d9d381f083268550fb05ebfd1800dc09ae280701d77`
- `docs/test-bible/frontend/pages.md` — `8cac5fefde0d85c63bb420faec0ae48cfaea58ab4e538d55d6f31508541803b4`
- `docs/test-bible/core/repo_admin_json.md` — `9f581e1ead6e4f205af48d40c7aba90eef991225bb63db269196ded06e3d0e9d`

#### ada — 2026-07-31T17:58:00.218Z
Product return fixed — staying **Code Complete** for your re-run, @Betty White.

**Publish:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view` @ `ace6c669` (fix `64431acd`)

**Fix:** `DispatchTask.candidate_id` is now typed `string | null` (matches the API — AST-1088 shared mailbox rows), the Candidate cell renders `row.candidate_id || "—"` like its sibling cells, and `openEdit` coerces to `""` (the edit PUT never sends `candidate_id`, so the form value is display-only).

**Unchanged:** Avail gt0 carve-out, `always_visible_under_avail_gt0` stamping, and `available_count` computation. No invented candidate id.

`npx tsc -b --noEmit` clean under `src/ui/frontend`.

#### betty — 2026-07-31T17:54:17.026Z
Product bug on publish tip `1d5b5c7e` — holding **Code Complete** (not advancing Tests Ready).

**What broke:** Stage 3 Avail gt0 carve-out correctly keeps a `gaze_email` row with `available_count === 0` and `always_visible_under_avail_gt0 === true`. Under Candidate **All**, expanding **Job Review** throws:

`TypeError: Cannot read properties of null (reading 'length')` in `truncateForDisplay` ← `ListTableTruncatedCell text={row.candidate_id}` in `AdminScheduledActions.tsx` (~line 247).

Shared mailbox rows have `candidate_id: null` (AST-1088). The row was previously filtered out by Avail gt0, so this path never painted. Visibility carve-out now surfaces it; Correct outcome (“visible and operable”) fails.

**Expected fix (still in AST-1106 scope):** null-safe Candidate cell (e.g. `row.candidate_id || "—"` / coerce before truncate) — do **not** invent a fake candidate_id; do **not** weaken the Avail carve-out.

**Betty status:** config / API / catalog tests drafted and green against the tip; SA §6c vitest blocked on this crash. Re-run qa-child after the display fix lands on the publish ref.

— Betty

#### ada — 2026-07-31T17:45:25.379Z
**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view/docs/features/meteorite/ast-1106-uat-gaze-email-missing-from-scheduled-actions-default-view.md

**Tip:** `8a2191c0` on `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`

**Self-assessment**
- **Scope:** `MAJOR-CHANGE` — utils admin config, list_dtasks flag, Scheduled Actions Avail filter, repo `agent_task` + AST-756 fixture.
- **Conf:** `high` — matches `et and ts and cid else 0` + default Avail gt0; API boolean from config (no React hardcode); catalog seed mirrors AST-1089 / empty-prompt shells.
- **Risk:** `Medium` — Avail predicate regression if carve-out is wrong; fixture drift fails AST-786; scoped only to `GAZE_EMAIL_CONFIG["task_key"]`.

---

# UAT: gaze_email missing from Scheduled Actions default view

**Linear:** [AST-1106](https://linear.app/astralcareermatch/issue/AST-1106/uat-gaze-email-missing-from-scheduled-actions-default-view)

**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task)

**Publish ref:** `sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`

After AST-1087 UAT, the shared null-`candidate_id` `gaze_email` dispatch row is invisible under Scheduled Actions’ default Avail **> 0** filter because list enrichment correctly sets `available_count=0` when `entity_type` / `trigger_state` / `candidate_id` are absent. This ticket adds a config-driven, API-resolved “always visible under Avail gt0” carve-out for that mailbox shell (without faking a positive avail count) and ships a repo `agent_task` catalog row so the task groups under Job Review like its meteorite siblings.

## UAT fitness

- **AC restored:** Parent AC1 — “With a `gaze_email` `dispatch_task` row (`candidate_id` null, `auto_mode` true) running under normal dispatch…” — and Parent AC9 — “The `dispatch_task` schema/provision path allows `candidate_id` null for `gaze_email`…” — require Susan to find and operate that shared row in Task Dispatcher / Scheduled Actions during UAT.
- **Correct outcome:** Susan can see and run/flip AUTO on the shared `gaze_email` row under default Scheduled Actions filters (Avail **> 0**, Candidate All) without clearing obscure filters; catalog meta exists so it groups under Job Review.
- **Sibling check:** AST-1088 provision/ensure null-candidate row unchanged; AST-1090 runner / due wiring unchanged; AST-1089 Ruth `parse_meteorite_email` prompts/contracts unchanged. AST-1107 (`task_name := task_key`) is a separate display pass — this plan sets `task_name` to `gaze_email` on the new catalog row so it already matches that temporary clarity rule.
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done. Row must be visible + operable under normal admin use.
- **Wrong fix rejected:** Do **not** fake a non-zero `available_count` for mailbox tasks; do **not** delete the Avail gt0 default without a mailbox carve-out; do **not** invent a fake `candidate_id` just to pass enrichment; do **not** hardcode `gaze_email` visibility sets in React (UI business rules resolve in API from config).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `ADMIN_CONFIG` always-visible-under-avail-gt0 task-key tuple (seeded from `GAZE_EMAIL_CONFIG["task_key"]`) + helper frozenset accessor | utils |
| `src/ui/api/api_admin.py` | Stamp `always_visible_under_avail_gt0` on each `list_dtasks` row from that helper | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Avail gt0 filter keeps rows where the API flag is true; extend `DispatchTask` type | ui |
| `data/admin/agent_task.json` | Add current `gaze_email` catalog row (empty prompts, Job Review grouping) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy after the new row (AST-786 seed gate) | docs |

## Stage 1: Config — always-visible under Avail gt0 keys

**Done when:** `admin_always_visible_under_avail_gt0_dispatch_task_keys()` returns a frozenset containing `GAZE_EMAIL_CONFIG["task_key"]` (`"gaze_email"`) and no other product literals are invented in React for this rule.

1. In `src/utils/config.py`, on `ADMIN_CONFIG` (near `hidden_dispatch_task_keys` usage / the existing `ADMIN_CONFIG` dict), add:

   ```python
   "always_visible_under_avail_gt0_dispatch_task_keys": (
       GAZE_EMAIL_CONFIG["task_key"],
   ),
   ```

   `GAZE_EMAIL_CONFIG` is already defined above `ADMIN_CONFIG` on this tip — do **not** duplicate the string `"gaze_email"` as a bare literal in this tuple.

2. Immediately after `admin_hidden_dispatch_task_keys()`, add:

   ```python
   def admin_always_visible_under_avail_gt0_dispatch_task_keys() -> frozenset:
       """task_key values kept visible under Scheduled Actions Avail > 0 (mailbox shells)."""
       raw = ADMIN_CONFIG.get("always_visible_under_avail_gt0_dispatch_task_keys") or ()
       return frozenset(raw)
   ```

3. Mirror the module header inventory comment style if `ADMIN_CONFIG` / helpers are listed there — one line noting the Avail-gt0 always-visible set (AST-1106).

⚠️ **Decision — config frozenset, not fake avail:** Visibility exception is an admin-UI policy for mailbox shells with intentional zero entity eligibility. Keep `available_count` computation unchanged (`0` when entity/trigger/candidate missing).

**Ritual:** `code(AST-1106): admin always-visible under avail gt0 config`

## Stage 2: API stamps the visibility flag on dispatch_task rows

**Done when:** `GET /api/admin/dispatch_tasks` JSON rows include boolean `always_visible_under_avail_gt0` true iff `task_key` is in the Stage 1 frozenset; other rows false. Enrichment still sets `available_count` via the existing `et and ts and cid` gate (gaze_email stays `0`).

1. In `src/ui/api/api_admin.py`, import `admin_always_visible_under_avail_gt0_dispatch_task_keys` from `src.utils.config` (same import cluster as `admin_hidden_dispatch_task_keys`).

2. In `list_dtasks()`, after computing `available_count` for each row (and before/alongside the hidden-key filter is fine), set:

   ```python
   row["always_visible_under_avail_gt0"] = (
       row.get("task_key") in admin_always_visible_under_avail_gt0_dispatch_task_keys()
   )
   ```

3. Do **not** change `count_eligible_for_dispatch_task` / the `et and ts and cid else 0` gate. Do **not** add this flag by inventing a positive `available_count`.

⚠️ **Decision — resolve in API:** Code Rules §3 UI — frontend must not own the business set; it only honors the boolean the API already resolved from config.

**Ritual:** `code(AST-1106): stamp always_visible_under_avail_gt0 on list_dtasks`

## Stage 3: Scheduled Actions Avail gt0 carve-out (flag only)

**Done when:** With default `availGtZeroFilter === "gt0"`, a row with `available_count === 0` and `always_visible_under_avail_gt0 === true` remains in `filteredRows`; other zero-avail rows stay omitted. Default Avail remains `"gt0"` (AST-894). No React literal `"gaze_email"` for this filter.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, extend the `DispatchTask` interface with:

   ```typescript
   always_visible_under_avail_gt0?: boolean
   ```

2. Replace the Avail gt0 predicate only — keep Candidate / section / AUTO / other filters unchanged:

   ```typescript
   if (availGtZeroFilter === "gt0") {
     filtered = filtered.filter(
       r => (r.available_count ?? 0) > 0 || !!r.always_visible_under_avail_gt0,
     )
   }
   ```

3. Do **not** change `formatAvailableCount` (gaze_email continues to show Avail as `—` when count is 0). Do **not** change default `useState("gt0")`. Do **not** widen Candidate All semantics (null `candidate_id` still only appears when Candidate filter is empty / All).

**Ritual:** `code(AST-1106): SA Avail gt0 keeps API always-visible rows`

## Stage 4: Repo `agent_task` catalog row + AST-756 fixture

**Done when:** `data/admin/agent_task.json` has a `current: 1` row for `task_key == "gaze_email"` with Job Review grouping; `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical; JSON remains a flat-row array. Startup `apply_repo_admin_json` will ship the row (same path as AST-1089).

1. Append one object to `data/admin/agent_task.json` (flat scalars only), modeled on the existing non-Ruth dispatch shells (`gaze`, `fetch_jd`) — **not** on Ruth prompt rows:

   | Field | Value |
   |-------|--------|
   | `task_key_uuid` | `519eba14-091c-45d2-9fa7-ff94b42bf9cf` |
   | `task_key` | `gaze_email` |
   | `current` | `1` |
   | `agent_id` | `n/a` |
   | `user_prompt` / `cache_prompt` / `cache_prompt_b`–`d` / `nocache_prompt` / `system_prompt` / `run_next` | `""` |
   | `task_group_order` | `"4000"` |
   | `task_group_name` | `Job Review` |
   | `task_seq` | `2.3` (before `parse_meteorite_email` ~`2.4`, before `qualify_meteorite` `2.5`) |
   | `task_name` | `gaze_email` (equals `task_key` — temporary clarity; aligns with AST-1107) |
   | `updated_at` | ISO-ish UTC timestamp string consistent with neighboring rows |

2. Sync the AST-786 gate fixture:

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
   ```

3. Verify parse + presence:

   ```bash
   python3 -c "import json; rows=json.load(open('data/admin/agent_task.json')); assert any(r.get('task_key')=='gaze_email' and r.get('task_group_name')=='Job Review' for r in rows)"
   ```

⚠️ **Decision — repo JSON is source of truth for grouping:** Same as AST-1089; do **not** hand-edit live DB. Empty prompts because `gaze_email` is a mailbox dispatch shell (Ruth parse stays on `parse_meteorite_email`).

⚠️ **Decision — out of scope for this ticket:** Do **not** rewrite every existing friendly `task_name` to equal `task_key` (that is AST-1107). Do **not** change Gmail scopes, runner, or Ruth prompts.

**Ritual:** `code(AST-1106): gaze_email agent_task catalog + AST-756 fixture`

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1087 with the Stage N blocked template.
- Leave AST-1088/1089/1090 product contracts and AST-1107 bulk rename untouched except the new `gaze_email` catalog row named above.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — utils admin config, admin API enrichment, Scheduled Actions React filter, and repo `agent_task` + AST-756 fixture.

**Conf:** `high` — diagnosis matches `list_dtasks` (`et and ts and cid else 0`) + default `availGtZeroFilter="gt0"`; carve-out pattern is a boolean flag from config; catalog seed mirrors AST-1089 / empty-prompt shells like `gaze`.

**Risk:** `Medium` — wrong Avail predicate could re-hide mailbox shells or accidentally show unrelated zero-avail rows if the config set is widened carelessly; fixture drift fails AST-786 gate. Scoped to `GAZE_EMAIL_CONFIG["task_key"]` only.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth:** Always-visible task keys live in `ADMIN_CONFIG`, seeded from `GAZE_EMAIL_CONFIG["task_key"]`.
- **§1.4 / no-hardcoded-sets:** No React `"gaze_email"` visibility set; API boolean only.
- **§3 UI business logic:** Visibility exception resolved in `api_admin.list_dtasks` from config; frontend renders the flag.
- **§3.3 imports:** ui←utils only for the helper; no new data/external imports in UI.
- **in-scope-only:** No Gmail / Ruth / runner / fake candidate_id / removing Avail default.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`
**Tip:** `64431acd`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ea8c8665` | ADMIN_CONFIG always-visible under Avail gt0 |
| 2 | `31f34265` | list_dtasks stamps `always_visible_under_avail_gt0` |
| 3 | `7c32fd19` | SA Avail gt0 keeps API always-visible rows |
| 4 | `ee05c771` | gaze_email agent_task catalog + AST-756 fixture |
| 4b | `64431acd` | null-safe Candidate cell (Betty product return) |

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1106
**Publish ref tip (at review):** `a08eb40d0c6fb326c57f39c4bfe8495080bc9351`
**Overall:** DISCUSS

### What’s solid

- Stages 1–4(+4b) match plan: `ADMIN_CONFIG` always-visible keys seeded from `GAZE_EMAIL_CONFIG["task_key"]`; API stamps boolean; SA Avail gt0 honors flag without faking avail; `gaze_email` catalog + AST-756 sync; null-safe Candidate cell.
- No React `"gaze_email"` visibility set; `available_count` gate unchanged.

### Issues

**discuss:** Tip has **two** `merge-tests(AST-1106)` commits (`6c612416`, `625b2f08`) after conflict-marker recovery. `orch.git.betty-merge-tests-one-sha` letter wants one SHA — product tip intact; clarify with Betty/Chuckles whether recovery merge is acceptable.

**advisory:** No Joan plan-rubric verdict attachment on the ticket.

### Recommended actions

None for product fix-now. Process discuss only.

### Statutes checked (summary)

57 active statutes swept vs `origin/dev...origin/sub/AST-1087/AST-1106-…`. One **needs-discussion** (merge-tests one-sha). Full table in Linear review comment.

**Betty product return (`64431acd`):** the Stage 3 carve-out surfaced the shared mailbox row, and `ListTableTruncatedCell text={row.candidate_id}` crashed `truncateForDisplay` on the null `candidate_id` (AST-1088). `DispatchTask.candidate_id` is now typed `string | null` to match the API, the Candidate cell renders `"—"` like its sibling cells, and `openEdit` coerces to `""` (the edit PUT never sends `candidate_id`). Avail carve-out and `available_count` computation unchanged; no invented candidate id.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1106
**Publish ref tip (at review):** `a08eb40d0c6fb326c57f39c4bfe8495080bc9351`
**Overall:** DISCUSS

### What’s solid

- Stages 1–4(+4b) match plan: `ADMIN_CONFIG` always-visible keys seeded from `GAZE_EMAIL_CONFIG["task_key"]`; API stamps boolean; SA Avail gt0 honors flag without faking avail; `gaze_email` catalog + AST-756 sync; null-safe Candidate cell.
- No React `"gaze_email"` visibility set; `available_count` gate unchanged.

### Issues

**discuss:** Tip has **two** `merge-tests(AST-1106)` commits (`6c612416`, `625b2f08`) after conflict-marker recovery. `orch.git.betty-merge-tests-one-sha` letter wants one SHA — product tip intact; clarify with Betty/Chuckles whether recovery merge is acceptable.

**advisory:** No Joan plan-rubric verdict attachment on the ticket.

### Recommended actions

None for product fix-now. Process discuss only.

### Statutes checked (summary)

57 active statutes swept vs `origin/dev...origin/sub/AST-1087/AST-1106-…`. One **needs-discussion** (merge-tests one-sha). Full table in Linear review comment.
