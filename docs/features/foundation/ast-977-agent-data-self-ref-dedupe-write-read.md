<!-- linear-archive: AST-977 archived 2026-08-05 -->

## Linear archive (AST-977)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-977/agent-data-self-ref-dedupe-writeread-add-a-self-reference-key-to-agent  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-974 — Add a self-reference key to agent_data  
**Blocked by / blocks / related:** parent: AST-974; blocks: AST-978

### Description

## What this implements

Schema for `ref_agent_data_id` on `agent_data`; write always creates an audit row; on identical `block_data` sets ref → earliest match and omits duplicate payload; read resolves refs transparently; canonical rows keep `ref_agent_data_id` null; debug found/recorded on touched backend paths. Does **not** own historical backfill.

## Acceptance criteria

1. Schema includes nullable `ref_agent_data_id` on `agent_data`, applied via the project’s normal schema-ensure path so existing and new databases gain the column.
2. On every content write, an `agent_data` audit row is created; when identical `block_data` already exists, that row’s `ref_agent_data_id` points at the earliest match and the row does not store a second full content copy.
3. Writing content with no identical match creates a normal content row with `ref_agent_data_id` null.
4. The earliest/canonical content row always has `ref_agent_data_id` null; writes that would create a self-ref or cycle are rejected.
5. Matching for reuse uses exact `block_data` only (block_type may differ between audit row and ref).
6. Reading agent content (by id and by batch) returns the same plain-text payload whether the row holds content directly or references the earliest identical row.
7. With `debug=True` on touched backend write/read paths, a scannable per-index trail shows match-vs-new and the ids recorded/resolved; with `debug=False`, no new debug-contract noise.
8. Existing flows that store and later retrieve system/task/response blocks for a batch still succeed end-to-end after the change.

## Boundaries

Does not own the one-time backfill of existing duplicates (sibling). Does not clear, null, or delete historical `block_data` (Susan-owned SQL + vacuum). Does not change BLOCK_TYPES, prompt assembly, or Anthropic call behavior.

## Notes for planning

Content-addressed self-reference pattern: `ref_agent_data_id` → earliest identical block; audit rows may omit payload. Data layer raises; callers log.

## Git branch (authoritative)

Per orientation § Branch law. Created at dispatch-parent. Publish to origin/<sub-ref> only.

### Comments

#### radia — 2026-07-24T01:06:59.641Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-977
**Publish ref:** `origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read` @ `6a2812c33bdeed652ac0e961f5f9ce51a7851e9b`
**Overall:** FIX-NOW

## Statutes checked

| id | tier | verdict | one-line |
|---|---|---|---|
| `astral.agent.confidence-bounds` | scoped | conforms | no grade/confidence changes in agent.py |
| `astral.agent.do-task-delegation` | scoped | conforms | store/hydration stay in agent; no Anthropic assembly elsewhere |
| `astral.agent.grade-vector-validation` | scoped | conforms | untouched grade-vector paths |
| `astral.batch.batch-id-first` | scoped | conforms | no new batch claim APIs |
| `astral.batch.batch-id-format` | scoped | conforms | batch_id usage unchanged |
| `astral.batch.claim-process-release` | scoped | conforms | untouched |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | still stores agent_data ids; no entity-array rewrite |
| `astral.config.config-source-of-truth` | scoped | conforms | no new config keys |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | untouched |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env literals |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | docs/features plan file; not spike notes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single docs/features/foundation/ast-977-….md |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test commit touched tests/bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer code commits exclude tests/; Betty owns test SHA |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | no external I/O; data+core only |
| `astral.layers.import-direction` | scoped | conforms | data helpers in database; debug in agent; no UI→data |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers miss (no scripts) |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | layers miss (no ui/utils) |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | untouched |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | untouched |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers miss (no ui) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | ValueError in data; zero data logging; debug in agent |
| `astral.standards.database-header-inventory` | scoped | conforms | agent_data inventory notes ref_agent_data_id |
| `astral.standards.debug-contract-gated` | scoped | violates | hydrate agent_data_read debug_detail before any do_task debug_index |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | single match + resolve helpers shared by getters |
| `astral.standards.in-scope-only` | scoped | conforms | no backfill/vacuum/BLOCK_TYPES/Anthropic |
| `astral.standards.logging-via-utils` | scoped | conforms | get_logger debug helpers in agent only |
| `astral.standards.no-cross-contamination` | scoped | conforms | layered files only |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | BLOCK_TYPES unchanged; no new enums |
| `astral.standards.public-then-helpers` | scoped | conforms | private _find/_resolve beside agent_data CRUD cluster |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | layers miss (no utils) |
| `astral.state.core-decides-transitions` | scoped | conforms | untouched |
| `astral.state.job-prior-states-enforced` | scoped | conforms | untouched |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | untouched |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers miss (no ui) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers miss (no ui) |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | layers miss (no ui/scripts/utils) |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single merge-tests SHA 12cfcb0 from origin/tests 8c562e6 |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary only |
| `orch.git.flow-direction-inviolable` | universal | conforms | published on child sub under AST-974 |
| `orch.git.ftr-sub-topology` | universal | conforms | origin/sub/AST-974/AST-977-… |
| `orch.git.merge-on-checkout` | universal | conforms | merge origin/dev into sub; no rebase of dev onto worktree |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no rewrite ops in tip history |
| `orch.git.no-dev-agent-branches` | universal | conforms | work on epic sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-974 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | contract fixed by parent AC; no product fork |
| `orch.pipeline.plan-is-bible` | universal | conforms | stages 1–5 match tip; Stage 4 read-trail gap scored under debug-contract |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Foundation child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test()+bible via Betty merge-tests path |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | implementer Ada; Chuckles not assignee |
| `orch.roles.engineer-assignee-through-resolve` | universal | needs-discussion | Linear assignee is Radia at Tests Passed; Joan named Ada |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer commits stayed off tests/; Betty owns test tree |

## Pattern conformance

none cited (ticket “content-addressed self-reference” is prose, not a canon pattern id)

## Plan adherence

Stages 1–3 and 5 match the tip (schema, dedupe write + exclude-id, transparent resolve, Code Rules). Stage 4 write trail nests under `_do_task_debug_entry`; hydration read trail does not — see fix-now. Self-Assessment Scope (Single-Component) matches the diff footprint. AST-978 backfill boundary held. Joan plan-rubric APPROVED attached.

## Findings

**fix-now** — `astral.standards.debug-contract-gated` / Plan Stage 4 / §1.5.1: `_block_text_by_type` emits `agent_data_read` via `debug_detail` during `_hydrate_caller_chain_context`, which runs before `_do_task_debug_entry` / `_resume_hop_debug_index`. Plan requires `debug_index` when not already under a do_task index. Write-path `agent_data_write` details after task-start index are OK.

**Recommended:** When `debug=True` and ids are non-empty, emit one local `debug_index` (e.g. func=`_block_text_by_type` / `agent_data_read`, index 1/1 or per-id) then details; or collect and emit the read trail after `_do_task_debug_entry`.

**discuss** — `orch.roles.engineer-assignee-through-resolve`: ticket assignee is Radia; Joan named Ada. review-child does not reassign — restore Ada through resolve.

**discuss (straggler)** — Joan Excluded but in-scope on diff (all conforms): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`.

**advisory** — `save_agent_data` uses `conn.total_changes == 0` for `duplicate_id`; fragile if `_ensure_agent_data_schema` mutates on the same connection. Common path after ensure-flag is OK; prefer statement `rowcount` if touching this again.

### What’s solid
Schema/ALTER/inventory; exact plain-text match without block_type; always-insert audit + omit payload; resolve on get/by_batch/for_ids; self-ref/cycle/missing raise; data raises / agent logs; Betty test tree ownership; AST-978 out of scope.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Docs append on plan file @ this tip.

context_tokens≈48000

#### betty — 2026-07-24T00:27:46.116Z
## QA test manifest

`origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read` @ `12cfcb0` (`merge-tests(AST-977): origin/tests 8c562e6`)

### Broken / revised
1. `TestSaveAgentData::test_saves_and_reads_batch_blocks` — assert bool → outcome dict (`new_content`)
2. `TestFeedbackBlockType::test_save_agent_data_accepts_feedback_block` — same bool→dict revision

### Gaps (new)
3. Schema ensure fresh + ALTER adds `ref_agent_data_id`
4. Identical write → `ref_existing`, earliest canonical, omit payload; block_type may differ
5. Reads resolve plain text via `get_agent_data` / `get_agent_data_by_batch` / `get_agent_data_for_ids`
6. PK retry → `duplicate_id`
7. Missing ref / cycle → `ValueError`
8. Agent debug: `agent_data_write` / `agent_data_read` when `debug=True`; quiet when `debug=False`

### Existing coverage (bible-backed)
- Baseline invalid `block_type` still in `TestSaveAgentData`

### Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_data.py \
  tests/component/data/database/test_rubric_vectors.py::TestFeedbackBlockType \
  tests/component/core/test_agent.py::TestAst977AgentDataDedupeDebug \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### Bible shasums (publish-ref)
- `docs/test-bible/data/database/agent_data.md` `sha256:36f1102cbb3a3a43d1ff13994e654edcdf8825f3ee484154803d5cab58beaf08`
- `docs/test-bible/core/agent.md` `sha256:d3acf264affc71d4d2996cecbacb919e4b5c6c184547432f177dcbc9fe1b54e2`

Out of scope: AST-978 backfill.

#### joan — 2026-07-24T00:14:12.113Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-977
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read`
**Engineer:** Ada

## Traceability

### Parent AC → plan stages

| Parent AST-974 AC | Plan coverage |
|---|---|
| 1 Schema nullable `ref_agent_data_id` via schema-ensure | Stage 1 |
| 2 Every write creates audit row; match → ref earliest + omit payload | Stage 2 |
| 3 No-match → content row, ref null | Stage 2 |
| 4 Canonical earliest ref null; reject self-ref/cycle | Stages 2–3 |
| 5 Match on exact `block_data` only (block_type may differ) | Stage 2 (`_find_earliest…`, no block_type filter; logical decompress equality) |
| 6 Reads by id/batch return same plain text direct or via ref | Stage 3 |
| 7 Backfill dry-run + live | N/A — boundary; child + plan assign to AST-978 |
| 8 Debug found/recorded when `debug=True`; quiet when false | Stage 4 |
| 9 Existing store-then-retrieve flows still succeed | Stages 2–3 (transparent resolve; signatures preserved aside from save return dict ignored by callers) |

### Plan stages → definition

| Stage | Maps to |
|---|---|
| 1 Schema + inventory | Purpose / Functional scope §1; AC1; Boundaries (no clear/delete) |
| 2 Dedupe write | Functional scope §2–3; AC2–5 |
| 3 Transparent read | Functional scope §4; AC6, AC9 |
| 4 Debug on touched agent paths | Functional scope §6; AC8 |
| 5 Code Rules mention | Compression/ref contract documentation (data-layer bullet) |

## Statute verdicts

| id | verdict | one-line |
|---|---|---|
| orch.git.betty-merge-tests-one-sha | conforms | Plan leaves tests to Betty; no merge-tests improvisation |
| orch.git.commit-vocabulary | conforms | Plan/docs vocabulary only; no banned commit types prescribed |
| orch.git.flow-direction-inviolable | conforms | Publish ref is child `sub/…` under parent ftr topology |
| orch.git.ftr-sub-topology | conforms | Uses authoritative `sub/AST-974/AST-977-…` |
| orch.git.merge-on-checkout | conforms | No contrary checkout guidance |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite operations in plan |
| orch.git.no-dev-agent-branches | conforms | Work stays on epic sub publish-ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree `astral-AST-974/` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Column/match/read contract fixed by parent AC; no product fork |
| orch.pipeline.plan-is-bible | conforms | Binding staged plan with Done-when gates |
| orch.pipeline.project-scoped-queues | conforms | Single-child Foundation ticket; no queue expansion |
| orch.pipeline.status-gates-skill-entry | conforms | Validation at Plan Ready only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | `tests/` / bible explicitly Betty / out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer is Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign to Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | Engineer paths `src/` + Code Rules docs; no test-tree |
| astral.agent.confidence-bounds | conforms | No grade/confidence changes |
| astral.agent.do-task-delegation | conforms | Keeps `do_task` store/hydration; no Anthropic assembly in other core |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | No new batch claim APIs |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Continues storing agent_data ids; no entity-array rewrite |
| astral.config.config-source-of-truth | conforms | Explicitly no new config keys |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env literals introduced |
| astral.git.betty-no-src-or-features | conforms | Engineer owns `src/` + plan; Betty excluded from those paths |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O; data persistence + core debug only |
| astral.layers.import-direction | conforms | data helpers in database; debug/logging in agent; UI stays off data |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | Data raises `ValueError`; zero data logging; debug in agent behind flag |
| astral.standards.database-header-inventory | conforms | Stage 1 updates `agent_data` inventory for `ref_agent_data_id` |
| astral.standards.debug-contract-gated | conforms | Stage 4 uses §1.5.1 helpers; quiet when `debug=False` |
| astral.standards.dry-and-focused-functions | conforms | Single match + single resolve helpers shared by getters |
| astral.standards.in-scope-only | conforms | Boundaries exclude backfill / vacuum / BLOCK_TYPES / Anthropic |
| astral.standards.logging-via-utils | conforms | `get_logger` / debug helpers in agent only |
| astral.standards.no-cross-contamination | conforms | Layered files only; no out-of-structure deps |
| astral.standards.no-hardcoded-sets | conforms | No new state/enum sets; BLOCK_TYPES unchanged |
| astral.standards.public-then-helpers | conforms | Private `_find_*` / `_resolve_*` beside public CRUD |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss plan paths
- astral.debug.spikes-under-debug-dir — paths miss plan paths
- astral.docs.features-single-file-per-ticket — paths `docs/features/**` miss (Code Rules path only)
- astral.git.engineer-test-tree-ban — paths miss plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss (no scripts)
- astral.layers.ui-config-driven-business-logic — layers/paths miss (no ui)
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss (no ui)
- astral.standards.utils-data-late-import-only — layers/paths miss (no utils)
- astral.ui.frontend-file-placement — layers/paths miss (no ui)
- astral.ui.naming-conventions — layers/paths miss (no ui)
- astral.ui.single-gunicorn-worker — layers/paths miss (no ui)

## Findings

None fix-now.

**acceptable** — Stage 2 full-table decompress scan on every write matches Susan’s no-unauthorized-limits rule and is already called Medium risk in self-assessment; build should keep the no-cap contract unless Susan authorizes a limit later.

**acceptable** — `save_agent_data` return flips bool→dict; production call sites ignore the return today (`agent.py` stores + database feedback helper). Betty may need mock return shapes later — correctly out of this plan.

Definition fidelity, layer/config/placement/pattern/DRY checks: pass. Self-assessment (Single-Component / high / Medium) is honest for a data-primary change with thin core debug.

— Joan
context_tokens≈42000

#### ada — 2026-07-24T00:07:07.113Z
Plan published on `origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read` @ `3f81b45`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read/docs/features/foundation/ast-977-agent-data-self-ref-dedupe-write-read.md

**Self-assessment**
- **Scope:** Single-Component — `database.py` agent_data schema/write/read + thin `agent.py` debug/passthrough; one Code Rules sentence.
- **Conf:** high — parent AC specifies the contract; compress/decompress and `_ensure_*` migration patterns already exist; current callers ignore `save_agent_data`’s return.
- **Risk:** Medium — bad match/resolve would corrupt prompt/response text for hydration callers; mitigated by exact plain-text match, canonical-only refs, and cycle checks.

**Approach (binding):** nullable `ref_agent_data_id` via `_ensure_agent_data_schema`; every write inserts an audit row; identical logical `block_data` → ref earliest + `block_data` NULL; reads resolve in data layer; debug found/recorded only in `agent.py` when `debug=True`. Backfill stays AST-978.

---

# AST-977 — agent_data self-ref + dedupe write/read

- **Linear:** [AST-977](https://linear.app/astralcareermatch/issue/AST-977/agent-data-self-ref-dedupe-writeread-add-a-self-reference-key-to-agent)
- **Parent:** [AST-974 — Add a self-reference key to agent_data](https://linear.app/astralcareermatch/issue/AST-974/add-a-self-reference-key-to-agent-data)
- **Publish ref:** `origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read`
- **Summary:** Add nullable `ref_agent_data_id` on `agent_data`, ensure it via the existing lazy/bootstrap schema path, and change write/read so every content write still creates an audit row while identical `block_data` reuses the earliest canonical row (omit duplicate payload on the audit row). Reads resolve refs to plain text transparently. Canonical rows keep `ref_agent_data_id` null; self-refs/cycles raise. Debug found/recorded trails on touched `agent.py` write/read paths when `debug=True`. Historical backfill is **AST-978** (out of scope).

## UAT fitness

- **AC restored:** Parent AST-974 AC 1–6, 8–9 (runtime; not backfill AC 7): schema nullable `ref_agent_data_id` via normal schema-ensure; every content write creates an audit row; match → `ref_agent_data_id` → earliest and no second full content copy; no-match → content row with ref null; canonical earliest always ref null; reject self-ref/cycle; match on exact `block_data` only (block_type may differ); reads by id and by batch return the same plain-text payload whether direct or referenced; debug found/recorded when `debug=True` / quiet when `debug=False`; existing store-then-retrieve system/task/response flows still succeed.
- **Correct outcome:** After a write of content that already exists, SQL shows a new audit row whose `ref_agent_data_id` points at the earliest identical content row and whose `block_data` is empty/absent; callers that load by id or batch still receive the full plain-text payload; first/canonical content row never points at itself.
- **Sibling check:** AST-978 owns one-time backfill of refs on existing duplicates and must not clear `block_data`. This plan does not implement backfill, does not null/delete historical payloads, and leaves AST-978 free to set refs on legacy duplicate content rows. Verified by scope Boundaries below and by not adding any backfill script/stage.
- **Not sufficient:** Removing an exception or making INSERT succeed without the audit-row + ref + transparent-read contract is **not** done.
- **Wrong fix rejected:** Skipping the new row when a match exists (no audit trail), matching on `(block_type, block_data)`, hashing without storing refs, or clearing historical `block_data` on write — all violate parent AC / Boundaries. Correct path is always-insert audit row + ref-to-earliest + omit payload + resolve on read.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory; `_ensure_agent_data_schema` column; match helper; `save_agent_data` dedupe write; resolve on `get_agent_data` / `get_agent_data_by_batch` / `get_agent_data_for_ids` | data |
| `src/core/agent.py` | Thread `debug` into store helpers; emit debug-contract found/recorded on write; emit resolve trail on touched read/hydration paths when `debug=True` | core |
| `docs/ASTRAL_CODE_RULES.md` | Extend the existing Data-layer `agent_data` compression sentence to state that `ref_agent_data_id` is resolved transparently on read (callers still see plain text) | docs |

**Out of scope (explicit):**

| Item | Owner |
|------|--------|
| Backfill `ref_agent_data_id` on existing duplicates | **AST-978** |
| Clear / null / delete / vacuum historical `block_data` | Susan SQL outside epic |
| BLOCK_TYPES, prompt assembly, Anthropic call behavior | unchanged |
| `tests/` / bible | Betty |

---

## Stage 1: Schema + inventory

**Done when:** Fresh and legacy DBs expose nullable `ref_agent_data_id` on `agent_data` after `_ensure_agent_data_schema` (including bootstrap registry path); header inventory mentions the column; `python3 -m py_compile src/data/database.py` passes. No write/read behavior change yet beyond schema.

1. In `src/data/database.py` module docstring inventory, update the `agent_data` bullet to note nullable self-ref `ref_agent_data_id` (points at earliest identical content row; audit rows may omit `block_data`).

2. In `_ensure_agent_data_schema` (~line 5251):
   - Add `ref_agent_data_id TEXT` (nullable, no DEFAULT required) to the `CREATE TABLE agent_data` column list.
   - When the table **already exists**, run `PRAGMA table_info(agent_data)` and, if `ref_agent_data_id` is missing, `ALTER TABLE agent_data ADD COLUMN ref_agent_data_id TEXT` (swallow only the existing “duplicate column name” pattern used elsewhere — do not swallow other errors).
   - Keep `CREATE INDEX idx_agent_data_batch` on fresh create only (unchanged).
   - Do **not** add a foreign-key constraint (SQLite FK not used elsewhere for this table; reject bad refs in write logic).
   - Do **not** reset or clear any existing `block_data`.

3. Confirm `agent_data` remains registered in `_UPSERT_LAZY_SCHEMA_HANDLERS` so `ensure_all_upsert_registry_schemas_at_startup()` / `ensure_table_schema_for_upsert` pick up the migration (no bootstrap.py edit).

⚠️ **Decision:** Column name is exactly `ref_agent_data_id` (parent + child AC). No parallel hash column — identity is exact logical `block_data` via existing compress/decompress helpers.

---

## Stage 2: Dedupe write path (`save_agent_data`)

**Done when:** Every successful content insert creates an `agent_data` row; identical logical content sets `ref_agent_data_id` to the earliest canonical match and stores `block_data` NULL; no-match stores compressed content with `ref_agent_data_id` NULL; self-ref and non-canonical/cycle targets raise `ValueError`; `INSERT OR IGNORE` duplicate primary key still means “no new row”; compile passes.

1. Add a private helper in `src/data/database.py` next to `save_agent_data` (name: `_find_earliest_agent_data_content_match`):

   ```python
   def _find_earliest_agent_data_content_match(
       conn: sqlite3.Connection,
       plain_text: str,
   ) -> Optional[str]:
       """Return agent_data_id of earliest canonical row with identical logical block_data, or None."""
   ```

   Behavior (literal):
   - Consider only rows where `ref_agent_data_id IS NULL` and `block_data IS NOT NULL`.
   - Order by `created_at ASC`, then `agent_data_id ASC`.
   - Identity: `_decompress_payload(row.block_data) == plain_text` (plain text the caller passed in — same contract as today’s save input). Do **not** filter by `block_type`.
   - Return the first matching `agent_data_id`, or `None`.
   - Do **not** log. Do **not** truncate the candidate set for performance.

⚠️ **Decision:** Match on decompressed logical content (Code Rules: compression invisible above data; parent: identity on exact `block_data` as callers treat plain text). Blob-only SQL equality is insufficient for legacy TEXT rows `_decompress_payload` already supports.

⚠️ **Decision:** No depth/row caps on the scan — Susan forbids unauthorized limits; correctness over premature optimization.

2. Rewrite `save_agent_data` body (same signature args; **change return type** from `bool` to `Dict[str, Any]`):

   Return shape (always a dict):

   | key | meaning |
   |-----|---------|
   | `inserted` | `True` if a new row was written |
   | `outcome` | `"new_content"` \| `"ref_existing"` \| `"duplicate_id"` |
   | `agent_data_id` | the id passed in |
   | `ref_agent_data_id` | set when `outcome == "ref_existing"`, else `None` |

   Algorithm inside `_with_conn` after `_ensure_agent_data_schema(conn)`:
   1. Let `plain = block_data` (must be `str`; keep existing `BLOCK_TYPES` validation).
   2. `match_id = _find_earliest_agent_data_content_match(conn, plain)`.
   3. If `match_id == agent_data_id`: raise `ValueError("agent_data self-ref rejected: …")`.
   4. If `match_id` is not None:
      - Load that row; if its `ref_agent_data_id` is not null/empty, raise `ValueError` (non-canonical target / would create a multi-hop write).
      - Insert with `ref_agent_data_id=match_id`, `block_data=NULL`, keep `token_size` from the caller, other columns as today.
      - On successful insert: return `{inserted: True, outcome: "ref_existing", agent_data_id, ref_agent_data_id: match_id}`.
   5. Else (no match): compress via `_compress_payload(plain)`, insert with `ref_agent_data_id=NULL` and compressed blob (same as today). Return `{inserted: True, outcome: "new_content", agent_data_id, ref_agent_data_id: None}`.
   6. Preserve `INSERT OR IGNORE` semantics for primary-key collision: if no row inserted (`total_changes == 0`), return `{inserted: False, outcome: "duplicate_id", agent_data_id, ref_agent_data_id: None}` — do not update the existing row.
   7. Update the docstring to describe dedupe + return dict. Do not log.

3. Call sites that currently ignore the return value stay valid (`_store_prompt_blocks`, `_store_response_block`, feedback helper in `database.py`). Do **not** adapt call sites to treat the return as `bool`.

⚠️ **Decision:** Return a dict (not bool) so Stage 4 can log found/recorded without a second SELECT. No production caller currently depends on the bool.

---

## Stage 3: Transparent read resolution

**Done when:** `get_agent_data`, `get_agent_data_by_batch`, and `get_agent_data_for_ids` return rows whose `block_data` is the resolved plain-text content (canonical payload) whether the row stores content directly or via `ref_agent_data_id`; broken/missing refs and cycles raise `ValueError` (data raises; callers log); compile passes.

1. Add private helper `_resolve_agent_data_block_data(conn, row_dict) -> Optional[str]`:
   - If `ref_agent_data_id` is null/empty: return `_decompress_payload(row_dict["block_data"])`.
   - Else follow the ref chain: load target by `agent_data_id`, track visited ids, raise `ValueError` on cycle or missing target.
   - Terminal row must be canonical (`ref_agent_data_id` null) with content; return its decompressed `block_data`.
   - Do not log.

2. In `get_agent_data`, `get_agent_data_by_batch`, and `get_agent_data_for_ids`, after `_row_to_dict`, set `d["block_data"] = _resolve_agent_data_block_data(conn, d)` instead of bare `_decompress_payload`. Keep `ref_agent_data_id` on the returned dict so debug callers can see it.

3. Do **not** change UI routes; `api_system.get_agent_data` already goes through core → `get_agent_data_by_batch`.

⚠️ **Decision:** Resolve inside the data layer so every read path (batch, id, ids map, feedback, hydration) stays transparent without teaching core about refs.

---

## Stage 4: Debug found/recorded on touched agent paths

**Done when:** With `debug=True`, `_store_prompt_blocks` / `_store_response_block` and the `do_task` hydration read that uses `get_agent_data_for_ids` emit §1.5.1 index/detail lines showing match-vs-new and ids recorded/resolved; with `debug=False`, no new debug-contract lines from these edits; data layer still has zero logging; compile passes.

1. Extend `_store_prompt_blocks` and `_store_response_block` with `debug: bool = False`.
2. From `do_task`, pass `debug=debug` into those store helpers wherever they are invoked for persistence.
3. After each `save_agent_data(...)` call in those helpers, when `debug=True`:
   - `dbg = get_logger(__name__, debug_flag=True)`
   - One `debug_index` (or `debug_detail` under an existing index if already inside a `do_task` index header) with outcome from the return dict: `new_content` vs `ref_existing` vs `duplicate_id`, plus `agent_data_id` and `ref_agent_data_id`.
   - Use `truncate_debug_content` if any payload excerpt is logged (prefer ids/outcome only — no full prompt dump required).
4. On the mid-chain hydration path that calls `get_agent_data_for_ids` (~line 644), when `debug=True`, for each requested id emit a detail line: resolved vs direct (`ref_agent_data_id` present/absent) and the id used. Do not add debug requirements to UI.
5. Do **not** add logging inside `src/data/database.py`.

⚠️ **Decision:** Debug lives in `agent.py` (caller logs) using the Stage 2 return dict + resolved row fields — satisfies “data raises; callers log” and AC debug trail without contaminating the data layer.

---

## Stage 5: Code Rules mention

**Done when:** The Data-layer bullet in `docs/ASTRAL_CODE_RULES.md` that documents `agent_data` compression also states that nullable `ref_agent_data_id` is followed on read so callers still receive plain text; no other rules churn.

1. Locate the sentence: *`agent_data.block_data` is zlib-compressed on write and decompressed on read — this is handled transparently by `save_agent_data` / `get_agent_data_by_batch`…*
2. Extend it (same paragraph) to say writes may store `ref_agent_data_id` to the earliest identical content row and omit duplicate payload; reads resolve the ref before returning plain text (`get_agent_data`, `get_agent_data_by_batch`, `get_agent_data_for_ids`).

---

## Self-Assessment

**Scope:** `Single-Component` — primarily `database.py` agent_data schema/write/read plus thin `agent.py` debug/passthrough; one Code Rules sentence.

**Conf:** `high` — pattern is specified by parent AC; compression helpers and `_ensure_*` migration patterns already exist; call sites already ignore `save_agent_data`’s return.

**Risk:** `Medium` — wrong match/resolve would corrupt what callers treat as prompt/response text across roster/consult/intake hydration; mitigated by exact plain-text match, canonical-only refs, and cycle checks.

## Rules self-review

- **§1.3 DRY:** Single match helper + single resolve helper; all three getters use resolve.
- **§1.5 / data-raises-caller-logs:** No logging in `database.py`; `ValueError` on self-ref/cycle/missing ref; debug only in `agent.py` behind `debug=True`.
- **§1.5.1:** Index/detail helpers only; no new `[DEBUG]` INFO; quiet when `debug=False`.
- **§2.1:** No new config keys (none required).
- **§3.3:** No new cross-layer imports; UI still does not touch data.
- **§3.5:** Column/helper names match parent vocabulary (`ref_agent_data_id`).
- **Compression contract preserved:** Callers still pass/receive plain text; omit payload only on audit rows with refs.
)

## Review (build stub)

**Built:** `origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read` @ `6dcfc6a`

**Stages delivered:**
- Stage 1: `ref_agent_data_id` schema + inventory — `baa8f4a`
- Stage 2: `save_agent_data` dedupe write (return dict) — `3194770`
- Stage 3: transparent read resolve on getters — `30e16c0`
- Stage 2 follow-up: exclude write id from match (PK retry) — `b51b137`
- Stage 4: `agent.py` debug found/recorded on write/hydration read — `a2d70db`
- Stage 5: Code Rules data-layer sentence — this commit

**Betty:** manifest at **Code Complete** — schema ensure column; write match/ref/omit; read resolve by id/batch/ids; self-ref/cycle raise; debug quiet when `debug=False`.

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1` · **Overall:** FIX-NOW · tip `55c9dba65152df7d69ed01c45a15d9ba7b314aae`

### What’s solid
- Schema + inventory + ALTER path for `ref_agent_data_id`; match on logical plain text without `block_type`; audit row always inserted; omit payload on ref; resolve on all three getters; self-ref/cycle/missing raise in data; Code Rules sentence updated; AST-978 boundary held; Betty owns tests/bible.

### Issues
- **fix-now:** Hydration `agent_data_read` emits `debug_detail` in `_block_text_by_type` before any `do_task` `debug_index` (`_do_task_debug_entry` runs later). Plan Stage 4 / §1.5.1 want `debug_index` when not already under a task index. Write-path details under `_do_task_debug_entry` are fine.
- **discuss:** Linear assignee is Radia at Tests Passed; Joan named Ada — restore engineer assignee through resolve.
- **discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; diff brings them in-scope (all scored conforms).
- **advisory:** `conn.total_changes == 0` for `duplicate_id` is fragile if `_ensure_agent_data_schema` mutates on the same connection; common path OK after ensure-flag.

### Recommended actions
1. In `_block_text_by_type` (debug=True): emit a local `debug_index` for the read batch, then details — or defer read-trail until after `_do_task_debug_entry`.
2. Restore Ada as Linear assignee when resolving.

## Resolution (2026-07-24)

- **fix-now (debug-contract):** `_block_text_by_type` now emits per-id `debug_index` (`func=_block_text_by_type`, outcome `agent_data_read …`) before `debug_detail` lines when `debug=True`, so hydration read trails are not orphan detail without an index header.
- **discuss (assignee):** Linear assignee is already Ada Lovelace at resolve — no reassignment needed.
- **discuss (straggler):** Noted only; Joan excluded statutes scored conforms by Radia — no code change.
- **advisory:** Left `conn.total_changes` as-is (common path after ensure-flag); no product touch this pass.
