<!-- linear-archive: AST-1107 archived 2026-08-11 -->

## Linear archive (AST-1107)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1107/uat-admin-task-name-should-equal-task-key-for-now  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1087 — Add gaze_email as a dispatch task  
**Blocked by / blocks / related:** parent: AST-1087

### Description

## What failed

Admin switched from showing `task_key` to showing `task_name`. Susan cannot tell what is what, and she believes this broke task sections in Scheduled Actions. She wants task names to be their `task_key` for now.

## Expected

In Admin Task Prompts / Scheduled Actions catalog meta, each task’s displayed `task_name` equals its `task_key` (temporary clarity), and section grouping still works so she can find tasks including meteorite/gaze_email-related ones during UAT.

## Repro

1. Open Admin → Task Prompts (and Scheduled Actions section headers).
2. Observe displayed names are friendly labels (or blank) rather than `task_key`.
3. Try to locate tasks by key name / navigate sections — clarity is lost; sections feel broken.

## Parent AC (quoted inline)

> 1. With a `gaze_email` `dispatch_task` row (`candidate_id` null, `auto_mode` true) running under normal dispatch, a bound inbox message matching each in-scope shape produces the corresponding **METEORITE_NEW** job(s) for that candidate (including subject+body appended when a job link was scraped), and the message is archived afterward.

(Parent UAT requires Susan to identify and operate dispatcher tasks for this epic; Admin display now keys off `task_name` / section meta from `agent_task`.)

## Diagnosis

* **Hypothesis:** UI reads `task_name` (fallback `task_key` only when empty) and sections read `task_group_name` from `agent_task`. Friendly / inconsistent `task_name` values (and missing catalog rows for new keys like `gaze_email`) make keys unrecognizable and scramble section navigation during UAT of this epic.
* **Correct outcome:** For now, every in-catalog `agent_task.task_name` equals that row’s `task_key` so Admin labels match keys; sections remain usable. New keys used by this epic (`gaze_email`, and any sibling parse key already present) are included.
* **Wrong fix to avoid:** Hardcode display strings in React; invent a second naming system; rename `task_key` values themselves.
* **Related siblings / contracts:** AST-1088/1089/1090 catalog keys; do not change TASK_CONFIG prompts or dispatch claim semantics.

## Boundaries

* This bug does **not** change: dispatch runner behavior, Gmail I/O, or long-term product naming strategy beyond temporary `task_name := task_key`.
* "Labels look different" alone is **not** done — Parent AC operability + Correct outcome must hold.

## In scope

- [X] `astral.config.config-source-of-truth` — Manage Tasks labels live in repo-owned `agent_task` JSON (AST-782); rewrite `task_name` there
- [X] `astral.standards.no-hardcoded-sets` — no React display-name map
- [X] `astral.layers.ui-config-driven-business-logic` — UI already renders catalog `task_name`; no new React business rule
- [X] `astral.standards.in-scope-only` — temporary `task_name := task_key` only; no runner/Gmail/`task_key` renames
- [X] `astral.docs.features-single-file-per-ticket` — this child’s plan doc only

## Considered but excluded

- [X] Hardcode display strings in React — Diagnosis wrong fix
- [X] Invent a second naming system — Diagnosis wrong fix
- [X] Rename `task_key` values — Diagnosis wrong fix
- [X] Change TASK_CONFIG prompts / Ruth parse / gaze_email runner — sibling contracts AST-1088/1089/1090
- [X] Change `task_group_*` section grouping — sections must stay usable; only `task_name` rewrites
- [X] `astral.layers.core-vs-external-bright-line` — no Gmail I/O
- [X] Long-term product naming strategy beyond temporary clarity — Boundaries

### Comments

#### radia — 2026-07-31T18:24:18.651Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1107
**Publish ref:** `origin/sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now` tip `1f035425e84bd4a788cb305c78a4789bf352eacb` (product tip reviewed `9b93389d`; docs() `1f035425`)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1107): origin/tests f7dd8db9…` |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/docs/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Published to origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1087/AST-1107-…` under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | ftr already up to date |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in history |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named epic branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1087 |
| orch.git.three-permanent-branches | universal | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Temporary UAT clarity decision documented |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match Files Changed |
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
| astral.config.config-source-of-truth | scoped | conforms | Labels live in repo agent_task JSON |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scored consult |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan docs, not spikes |
| astral.dispatch.seed-auto-false | scoped | conforms | No AUTO-true seed in this ticket’s commits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-1107 plan file present (sibling 1106 separate) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths no match |
| astral.layers.import-direction | scoped | conforms | No new cross-layer imports in 1107 code |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No React name map; catalog drives labels |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths no match |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths no match |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No auth surface change in 1107 code |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new swallow |
| astral.standards.database-header-inventory | scoped | not-applicable | layers {data} no match |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug paths |
| astral.standards.dry-and-focused-functions | scoped | conforms | Mechanical catalog rewrite |
| astral.standards.in-scope-only | scoped | conforms | task_name only; grouping/prompts/keys untouched |
| astral.standards.logging-via-utils | scoped | conforms | No new logging |
| astral.standards.no-cross-contamination | scoped | conforms | Catalog + fixture only for 1107 |
| astral.standards.no-hardcoded-sets | scoped | conforms | No React display-name map |
| astral.standards.public-then-helpers | scoped | conforms | No new public API surface |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths no match |
| astral.state.job-prior-states-enforced | scoped | conforms | No job transitions |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths no match |
| astral.ui.frontend-file-placement | scoped | conforms | No 1107 frontend edit |
| astral.ui.naming-conventions | scoped | conforms | No 1107 frontend rename |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker changes |

## Pattern conformance

none cited beyond description statute ids (covered in table)

## Plan adherence

Self-Assessment Scope `Single-Component` matches catalog + fixture only. Stages 1–2 delivered: 0 current-row mismatches; `gaze_email` / `parse_meteorite_email` included; group fields unchanged vs origin/dev for shared UUIDs.

## Findings

None fix-now / discuss.

**advisory:** Three-dot also includes sibling AST-1106 visibility work via ftr. no plan-rubric verdict attached.

### What’s solid

Mechanical `task_name := task_key` across catalog; AST-756 sync; sections still use `task_group_*`.

### Recommended actions

None.

context_tokens≈38000

#### betty — 2026-07-31T18:21:35.132Z
## QA test manifest — AST-1107

**Publish tip:** `origin/sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now` @ `9b93389d`
**Delivery:** `merge-tests(AST-1107): origin/tests f7dd8db92863d7ff9e7c3697a2b13efb4b5dc8aa` (**one** merge-tests)

### Run (epic worktree on publish tip)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1107TaskNameEqualsTaskKey \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1106GazeEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst878FetchCulturePagesCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1072ContactEstelleTurnCatalogRow \
  -q
```

### Manifest

1. **Catalog `task_name := task_key`** — `TestAst1107TaskNameEqualsTaskKey` (every `current==1` row; fixture byte-locked to AST-756).
2. **Revised row asserts** — friendly labels → `task_name == task_key` for qualify_meteorite, fetch_culture_pages, preamble_validate_response, simple_resume_parse, craft_resume_base, contact_estelle_turn, topic_menu_*, parse_meteorite_email, gaze_email.
3. **Regression** — `TestAst786AgentTaskRepoJsonSeed` (48 + fixture lock).

### Broken / obsolete (revised this pass)

- Friendly `task_name` string asserts in `test_repo_admin_json.py` catalog row classes.

### Integration

none

### Note

`TestAst793AgentTaskRevertDivergence` fails on this product tip **without** these test edits (pre-existing revert/divergence). Not in this manifest.

### Bible shasum (on publish tip)

- `docs/test-bible/core/repo_admin_json.md` — `e76501d0ad42049a3b11ae9c7c7e9606740fad12dc7c93368fe5876526aa9a4c`

#### ada — 2026-07-31T18:17:15.708Z
**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now/docs/features/meteorite/ast-1107-uat-admin-task-name-should-equal-task-key-for-now.md

**Tip:** `3bfcfdae` on `origin/sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`

**Self-assessment**
- **Scope:** `Single-Component` — rewrite every `agent_task.task_name` to equal `task_key` + AST-756 fixture sync; no `src/` logic.
- **Conf:** `high` — mechanical catalog rewrite; Task Prompts already shows `task_name || task_key`; grouping columns untouched; `gaze_email` already matches from AST-1106.
- **Risk:** `low` — site-wide Admin label change to keys is intentional temporary clarity; fixture drift fails AST-786 if Stage 2 skipped.

---

# UAT: Admin task_name should equal task_key for now

**Linear:** [AST-1107](https://linear.app/astralcareermatch/issue/AST-1107/uat-admin-task-name-should-equal-task-key-for-now)

**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task)

**Publish ref:** `sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`

Admin Task Prompts now displays `task_name` (falling back to `task_key` only when empty). Friendly labels in `data/admin/agent_task.json` make meteorite / gaze_email UAT unreadable. This ticket rewrites every current catalog row so `task_name == task_key` (temporary clarity), keeps section grouping (`task_group_*`) unchanged, and syncs the AST-756 seed fixture. Does **not** hardcode display strings in React or rename any `task_key`.

## UAT fitness

- **AC restored:** Parent AC1 — “With a `gaze_email` `dispatch_task` row (`candidate_id` null, `auto_mode` true) running under normal dispatch…” — Parent UAT requires Susan to identify and operate dispatcher / Task Prompts catalog entries for this epic; labels currently come from `agent_task.task_name`.
- **Correct outcome:** Every in-catalog `agent_task.task_name` equals that row’s `task_key` so Admin labels match keys; section grouping (`task_group_order` / `task_group_name` / `task_seq`) remains usable. Keys used by this epic (`gaze_email`, `parse_meteorite_email`) are included.
- **Sibling check:** AST-1088/1089/1090 product contracts unchanged (no TASK_CONFIG prompt edits, no dispatch claim/runner/Gmail changes). AST-1106 already set `gaze_email`’s `task_name` to `gaze_email` — this pass normalizes the rest of the catalog the same way.
- **Not sufficient:** Changing one React label string alone is **not** done. Catalog data must make every Task Prompts row show its key.
- **Wrong fix rejected:** Do **not** hardcode display strings in React; do **not** invent a second naming system; do **not** rename `task_key` values; do **not** change long-term product naming strategy beyond temporary `task_name := task_key`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Set every current row’s `task_name` to equal that row’s `task_key` (leave grouping/prompts/agent_id untouched) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy after the rewrite (AST-786 seed gate) | docs |

## Stage 1: Rewrite catalog `task_name` := `task_key`

**Done when:** For every object in `data/admin/agent_task.json` with `current == 1`, `task_name == task_key` (string equality). No other fields change. JSON remains a flat-row array of scalars.

1. In the epic worktree on `sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`, load `data/admin/agent_task.json`.
2. For each row, set `task_name` to the exact string value of `task_key` (including rows that already match, e.g. `gaze_email`).
3. Do **not** edit `task_group_order`, `task_group_name`, `task_seq`, prompts, `agent_id`, or UUIDs.
4. Write the file back with the same pretty-print style as the repo (2-space indent + trailing newline). Prefer a small mechanical Python rewrite over hand-editing 47 rows.

⚠️ **Decision — data source, not React:** Task Prompts already renders `{row.task_name || row.task_key}` (`AdminTaskPrompts.tsx`). Scheduled Actions Task column already shows `task_key`. Fixing the catalog makes labels match keys without hardcoding display strings in the frontend (Code Rules UI business-logic / Diagnosis wrong fix).

⚠️ **Decision — temporary UAT clarity only:** Do not invent a permanent naming framework or change `task_key` identifiers. Sibling AST-1106 already aligned `gaze_email`; this ticket finishes the catalog.

**Verify:**

```bash
python3 -c "
import json
rows=json.load(open('data/admin/agent_task.json'))
bad=[(r.get('task_key'), r.get('task_name')) for r in rows if (r.get('task_name') or '') != (r.get('task_key') or '')]
assert not bad, bad
assert any(r.get('task_key')=='gaze_email' and r.get('task_name')=='gaze_email' for r in rows)
assert any(r.get('task_key')=='parse_meteorite_email' and r.get('task_name')=='parse_meteorite_email' for r in rows)
print('OK', len(rows))
"
```

**Ritual:** `code(AST-1107): agent_task task_name equals task_key`

## Stage 2: AST-756 fixture sync

**Done when:** `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to `data/admin/agent_task.json`.

1. Copy and verify:

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
```

2. Do **not** hand-edit the live DB — startup `apply_repo_admin_json` ships the repo file (same path as AST-1089 / AST-1106).

**Ritual:** `code(AST-1107): AST-756 fixture sync after task_name rewrite`

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1087 with the Stage N blocked template.
- Leave TASK_CONFIG prompts, dispatch runners, Gmail I/O, and React display logic untouched.

## Self-Assessment

**Scope:** `Single-Component` — repo `agent_task.json` catalog labels + AST-756 fixture sync; no `src/` product logic.

**Conf:** `high` — mechanical field rewrite; UI already prefers `task_name` with `task_key` fallback; grouping columns untouched; mirrors AST-1106’s `gaze_email` naming choice.

**Risk:** `low` — Admin Task Prompts labels change site-wide to keys (intentional temporary clarity); section headers still use `task_group_name`; fixture drift fails AST-786 gate if Stage 2 is skipped.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / config-source-of-truth:** Display labels for Manage Tasks live in repo-owned `agent_task` JSON (AST-782), not React literals.
- **§1.4 / no-hardcoded-sets:** No new React name maps.
- **§3 UI:** No frontend business-rule change; data already drives the label.
- **in-scope-only:** No runner / Gmail / TASK_CONFIG prompt / `task_key` renames.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1087/AST-1107-uat-admin-task-name-should-equal-task-key-for-now`
**Tip:** `adb30fc1`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `3356309c` | agent_task task_name equals task_key (47 rows rewritten) |
| 2 | `adb30fc1` | AST-756 fixture sync after task_name rewrite |

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1107
**Publish ref tip (at review):** `9b93389d7e290bb0651a8e02c8aeefb02734d390`
**Overall:** CLEAN

### What’s solid

- Stages 1–2 match plan: every catalog row `task_name == task_key` (48 rows / 0 mismatches); `task_group_*` untouched; AST-756 fixture byte-identical.
- No React name map; no `task_key` renames; single `merge-tests(AST-1107)`.

### Issues

**advisory:** Three-dot vs `origin/dev` also carries sibling AST-1106 visibility work via ftr. No Joan plan-rubric verdict attachment.

### Recommended actions

None.

### Statutes checked (summary)

57 active statutes swept vs `origin/dev...origin/sub/AST-1087/AST-1107-…`. No violates. Full table in Linear review comment.

