<!-- linear-archive: AST-1041 archived 2026-08-05 -->

## Linear archive (AST-1041)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1041/meteorite-company-config-lazy-ensure-support-meteorite-jobs  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1034 — Support meteorite jobs  
**Blocked by / blocks / related:** parent: AST-1034; blocks: AST-1042

### Description

## What this implements

Owns the config seed template (including **IGNORE**), the core lazy-ensure helper (insert `meteorite-<candidate_id>` if missing for a given candidate), leave-in-place lifecycle, and hard exclusion of those rows from roster/gazer company claim paths. Does **not** own the job create API (child 2) or email ingest.

## Citations

`pattern.config.config-block`; `pattern.state.entity-state-transitions`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.debug-contract-gated`; `astral.standards.database-header-inventory`.

## Acceptance criteria

1. Config defines the meteorite placeholder template (display name, `meteorite-<candidate_id>` shape, **IGNORE**, unidentified-employer metadata).
2. Calling lazy-ensure for a candidate inserts `meteorite-<candidate_id>` once when missing and is a no-op when the row already exists; server start alone does **not** create meteorite rows for all ACTIVE_SEARCH candidates.
3. Meteorite placeholder companies in **IGNORE** are never claimed or processed by roster website-resolution / gazer company batch tasks.
4. Existing `meteorite-*` companies (and jobs) remain in the database after the candidate is no longer ACTIVE_SEARCH.
5. With `debug=True` on the lazy-ensure path, insert vs already-present outcomes use Style D index headers and `|` detail; with `debug=False`, no new debug-contract lines from that path.
6. Existing non-meteorite company and job flows still behave as before (smoke: a normal company is still claimable on its existing triggers).

## Boundaries

Does **not** own the job create API (sibling). Does **not** own email ingest. Does **not** bulk-seed at server start.

## Notes for planning

Citations above. Config-templated lazy per-candidate placeholder ensure (new pattern flag on parent).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1034-support-meteorite-jobs`, child `sub/AST-1034/<this-id>-meteorite-company-config-lazy-ensure`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T17:21:50.222Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1041
**Publish ref:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure` @ `fffc224e` (product tip `ae062c74` + docs review)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure` — `config.py` METEORITE_CONFIG, `src/core/meteorite.py`, `database.py` claim exclusion + Betty tests/bible.
**Notes:** Joan plan-rubric attached (APPROVED). Three C4 stragglers (substance conforms). No fix-now. §5f Style D applied on ensure `debug=` path.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence / agent scoring |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched |
| astral.batch.batch-id-first | scoped | conforms | Claim exclusion inside existing `set_company_batch` |
| astral.batch.batch-id-format | scoped | conforms | Untouched |
| astral.batch.claim-process-release | scoped | conforms | Hardens claim; does not bypass claim/process/release |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | `METEORITE_CONFIG` owns literals; claim reads prefix |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | `job_create_latest_score` parked for AST-1042 |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/` — not a misplaced spike |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file for AST-1041 |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer src/features; Betty tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | Betty owns `test()`/`merge-tests()` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O |
| astral.layers.import-direction | scoped | conforms | meteorite → data+utils; database → utils only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss (`scripts`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No UI; config block only |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers miss (`ui`) |
| astral.standards.data-raises-caller-logs | scoped | conforms | ensure raises; data does not log |
| astral.standards.database-header-inventory | scoped | conforms | Existing `company` APIs only; no new tables |
| astral.standards.debug-contract-gated | scoped | conforms | Style D index+detail only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single public ensure; claim filter localized |
| astral.standards.in-scope-only | scoped | conforms | No API/email/UI/bulk seed |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` Style D helpers |
| astral.standards.no-cross-contamination | scoped | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | scoped | conforms | No inline `meteorite-` in claim SQL |
| astral.standards.public-then-helpers | scoped | conforms | Public `ensure_meteorite_company` only |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data |
| astral.state.core-decides-transitions | scoped | conforms | Ensure writes registered `IGNORE` from config |
| astral.state.job-prior-states-enforced | scoped | conforms | No job writes |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers miss (`ui`) |
| astral.ui.naming-conventions | scoped | not-applicable | layers miss (`ui`) |
| astral.ui.single-gunicorn-worker | scoped | conforms | `config.py` touch; gunicorn untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1041)` @ `ae062c74` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure` |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/...` already ancestor |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1034` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Plan decisions already locked |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match shipped code |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit |

## Pattern conformance

| cited | verdict |
| -- | -- |
| `pattern.config.config-block` | conforms — `METEORITE_CONFIG` after `JOB_STATES` with asserts |
| `pattern.state.entity-state-transitions` | conforms — writes registered `IGNORE` only |
| `astral.config.config-source-of-truth` | conforms |
| `astral.standards.no-hardcoded-sets` | conforms |
| `astral.standards.debug-contract-gated` | conforms — §5f Style D gated |
| `astral.standards.database-header-inventory` | conforms |

## Plan adherence

Stages 1–2 match Self-Assessment **Single-Component**. Config template, insert-once ensure, claim-only `NOT LIKE` prefix, leave-in-place (no reaper), and Style D gating match the plan bible. AST-1042 job-create defaults parked unused as planned. No API/email/UI smuggling.

## Findings

### fix-now
(none)

### discuss
1. **straggler** — `astral.debug.spikes-under-debug-dir` (docs/features in three-dot). Substance: **conforms**.
2. **straggler** — `astral.docs.features-single-file-per-ticket`. Substance: **conforms**.
3. **straggler** — `astral.git.engineer-test-tree-ban` (Betty tests/bible). Substance: **conforms**.

### advisory
(none)

### What’s solid
- Config-owned prefix in claim SQL; insert-only-when-missing avoids `INSERT OR REPLACE` wipe; Style D index+detail on both outcomes.

### Recommended actions
- Ada: acknowledge stragglers (no product change expected) → resolve-child → User Testing.

context_tokens≈38000

#### betty — 2026-07-29T17:19:15.805Z
1. `tests/component/utils/test_config.py::TestAst1041MeteoriteConfig` — `METEORITE_CONFIG` keys, IGNORE/JD_READY registry, prefix/template shape
2. `tests/component/core/test_meteorite.py` — empty id; insert once / no-op; Style D debug on+off
3. `tests/component/data/database/test_companies.py::TestAst1041MeteoriteClaimExclusion` — claim skips `meteorite-*` (NEW + IGNORE); normal still claimed; clear still clears

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/core/test_meteorite.py \
  tests/component/data/database/test_companies.py::TestAst1041MeteoriteClaimExclusion \
  -q
```

**Pass:** pytest green on the three items above.

**Broken/revised:** none — new module + additive config/claim filter.
**Integration:** no existing `tests/integration/` scenarios assert meteorite placeholders / claim exclusion — none revised; no new scenarios.

**Publish:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure` @ `ae062c74` (`merge-tests(AST-1041): origin/tests 98b657378e67183cb2f76bfb8e74c621d767ece7`)

**Bible shasums on publish ref:**
- `docs/test-bible/core/meteorite.md` `ff93170bd0177ba8bbd0c4a054e5138363f5fe9a`
- `docs/test-bible/utils/config.md` `38c2cf35d847ac9156a0589cef1bb7132491b89a`
- `docs/test-bible/data/database/companies.md` `aef899f8560097bd6fcb63a3077906c32fb1a0a0`

— Betty

#### joan — 2026-07-29T17:11:58.667Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1041
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `b8a8df3d`. Project Astral Meteorite. New-pattern flag on parent is “implement under epic citations until catalog” — plan stays in that lane (no statute/corpus invent).
**Implementer:** Ada (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Config meteorite template (name, shape, IGNORE, metadata) | Stage 1 |
| 2 Lazy-ensure insert-once / no-op; no server-start bulk seed | Stage 2 ensure + Stage 1 “do not bulk seed” |
| 3 IGNORE meteorite never claimed by roster/gazer company batches | Stage 2 `set_company_batch` claim `NOT LIKE` prefix |
| 4 API create job under meteorite from HTML | N/A — boundary: AST-1042 |
| 5 No admin UI for meteorite create | N/A — out of scope (no UI files) |
| 6 Leave-in-place after candidate leaves ACTIVE_SEARCH | Stage 2: no reaper/delete hooks |
| 7 Style D on lazy-ensure when `debug=True` | Stage 2 ensure debug |
| 8 Non-meteorite flows still claimable | Stage 2 filter scoped to `short_name_prefix` only |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Config template | 1 |
| 2 Lazy-ensure idempotent; no bulk start seed | 2 (+1) |
| 3 Hard exclusion from roster/gazer claims | 2 |
| 4 Leave-in-place | 2 |
| 5 Style D gated debug | 2 |
| 6 Non-meteorite smoke | 2 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 `METEORITE_CONFIG` | Purpose / Functional scope template; Architectural config-block; AC1; job-create defaults parked for AST-1042 |
| 2 `ensure_meteorite_company` + claim exclusion | Lazy-ensure; IGNORE exclusion; leave-in-place; debug AC; Boundaries (no API/email/UI/bulk) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1041):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No rewrite flow |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1034` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Parent open questions none; pattern flagged for implement-under-citations |
| orch.pipeline.plan-is-bible | conforms | Stages binding; AST-1042 excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | No AI/do_task |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Claim exclusion stays inside existing `set_company_batch` |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Hardens claim; does not bypass claim/process/release |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | `METEORITE_CONFIG` owns literals; claim reads prefix from config |
| astral.config.pass-threshold-vs-score-floor | conforms | `job_create_latest_score` parked for AST-1042; unused here |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src/features |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O |
| astral.layers.import-direction | conforms | meteorite → data+utils; database → utils only |
| astral.layers.ui-config-driven-business-logic | conforms | No UI |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | ensure raises; data does not log |
| astral.standards.database-header-inventory | conforms | Existing `company` APIs only; no new tables |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | Single public ensure; no roster stuffing |
| astral.standards.in-scope-only | conforms | Explicitly excludes API/email/UI/bulk/tests |
| astral.standards.logging-via-utils | conforms | `get_logger` Style D helpers |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | No inline `meteorite-` in database claim |
| astral.standards.public-then-helpers | conforms | Public `ensure_meteorite_company` first |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | Ensure writes registered `IGNORE` from config |
| astral.state.job-prior-states-enforced | conforms | No job writes in this child |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. `job_create_state` / `job_create_latest_score` in `METEORITE_CONFIG` unused by AST-1041 — matches parent Architectural “create defaults in config”; AST-1042 consumes.
2. Claim hard-exclusion in `database.py` is defense-in-depth beyond empty IGNORE `batch_criteria` — aligns with child AC3; single claim path (`set_company_batch` / wrapper).
3. Insert-only-when-missing avoids `INSERT OR REPLACE` wipe — called out in Risk.
4. Self-assessment Single-Component / high / Medium — honest.
5. New `src/core/meteorite.py` vs stuffing roster — good for AST-1042/ingest reuse.

— Joan
context_tokens≈48000

#### chuckles — 2026-07-29T17:09:49.831Z
[thread-orphan] Joan session relocated:
found: `/home/susan/.cursor/chats/0ab2adc851c7f84d4ce4bb00f485d83d/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db`
expected: `/home/susan/.cursor/chats/7b0e833423ebc6a5ec29067f1fb11ea3/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db`
UUID unchanged — resume.

— Chuckles

#### ada — 2026-07-29T17:09:23.153Z
Plan published on `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure` @ `b8a8df3d`.

**Plan:** [docs/features/meteorite/ast-1041-meteorite-company-config-lazy-ensure.md](https://github.com/susansomerset/astral/blob/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure/docs/features/meteorite/ast-1041-meteorite-company-config-lazy-ensure.md)

**Self-assessment**
- **Scope:** Single-Component — `METEORITE_CONFIG`, new `src/core/meteorite.py` lazy-ensure, and `set_company_batch` claim exclusion for the meteorite prefix; no UI/job-create/email.
- **Conf:** high — reuses `save_company`/`get_company`, Style D debug, and existing claim `where_base` filter pattern; IGNORE already has no batch_criteria, hard exclusion is defense in depth.
- **Risk:** Medium — a wrong `NOT LIKE` prefix could hide real companies or miss placeholders; ensure only inserts when missing to avoid `INSERT OR REPLACE` field wipe.

---

# AST-1041 — Meteorite company config + lazy ensure

**Linear:** [AST-1041](https://linear.app/astralcareermatch/issue/AST-1041/meteorite-company-config-lazy-ensure-support-meteorite-jobs)
**Parent:** [AST-1034](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs) — Support meteorite jobs
**Publish ref:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`

Config-owned meteorite placeholder company template plus a core **lazy-ensure** helper that inserts `meteorite-<candidate_id>` once when a known candidate needs it (no server-start bulk seed). Placeholders land in **IGNORE** and are hard-excluded from roster/gazer company claim SQL. Leave-in-place lifecycle (no delete when candidate leaves ACTIVE_SEARCH). Does **not** own the job-create API (AST-1042) or email ingest.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_CONFIG` seed template (+ job-create defaults for AST-1042 reuse) | utils |
| `src/core/meteorite.py` | New module: `ensure_meteorite_company(candidate_id, *, debug=False)` | core |
| `src/data/database.py` | On company **claim** (`set_company_batch` clear=False), exclude `short_name` matching meteorite prefix | data |

## Stage 1: `METEORITE_CONFIG` seed template

**Done when:** `METEORITE_CONFIG` is importable from `config.py` with every literal this epic’s ensure/create paths need; no callers yet.

1. In `src/utils/config.py`, add a new block **immediately after** `JOB_STATES` (so both `COMPANY_STATES` and `JOB_STATES` exist for the asserts):

```python
# ---------------------------------------------------------------------------
# METEORITE_CONFIG: per-candidate placeholder employer (AST-1034 / AST-1041).
# Lazy-ensure inserts meteorite-<candidate_id> on demand — never bulk at server start.
# Job-create defaults (JD_READY + score) are consumed by AST-1042; defined here so
# literals stay config-owned (parent Architectural definition).
# ---------------------------------------------------------------------------
METEORITE_CONFIG = {
    "short_name_prefix": "meteorite-",
    "short_name_template": "meteorite-{candidate_id}",  # format with candidate_id=
    "company_name": "meteorite",
    "company_state": "IGNORE",
    "company_data": {
        "note": (
            "The company for this job has not been identified, and cannot be "
            "vetted without a website url."
        ),
    },
    # AST-1042 job-create defaults (unused in AST-1041)
    "job_create_state": "JD_READY",
    "job_create_latest_score": 10.0,
}

assert METEORITE_CONFIG["company_state"] in COMPANY_STATES
assert METEORITE_CONFIG["job_create_state"] in JOB_STATES
```

⚠️ **Decision:** Place the block after `JOB_STATES` (currently ~line 1372+), not after `COMPANY_STATES`, so both registry asserts can run at import time without reordering large config sections.

2. Do **not** add server-start / bootstrap upsert loops. Do **not** seed rows for all ACTIVE_SEARCH candidates.

**Done when (recheck):** `from src.utils.config import METEORITE_CONFIG` works; keys above present; `company_state` is `"IGNORE"`.

## Stage 2: Core lazy-ensure + claim hard-exclusion

**Done when:** `ensure_meteorite_company` inserts once / no-ops when present with Style D debug; `set_company_batch` claim SQL never selects `meteorite-*` short names; no delete/reaper for leave-in-place.

1. Create `src/core/meteorite.py` with module docstring:

```
Meteorite placeholder company ensure (AST-1041).

Lazy-insert meteorite-<candidate_id> from METEORITE_CONFIG. No job create (AST-1042).
No email ingest. Leave-in-place — callers must not delete these rows on candidate exit.
```

2. Implement public API (public-first; helpers below if needed):

```python
def ensure_meteorite_company(candidate_id: str, *, debug: bool = False) -> dict:
    """Ensure meteorite-<candidate_id> exists in IGNORE. Idempotent.

    Returns:
      {"short_name": str, "inserted": bool, "company": dict}
    """
```

Concrete steps inside `ensure_meteorite_company`:

- Strip `candidate_id`; if empty after strip, raise `ValueError("candidate_id is required")`.
- Build `short_name = METEORITE_CONFIG["short_name_template"].format(candidate_id=candidate_id)` (must equal `METEORITE_CONFIG["short_name_prefix"] + candidate_id` — do not invent a second shape).
- `log = get_logger(__name__); log.set_debug_flag(debug)`.
- `existing = get_company(short_name)` from `src.data.database`.
- If `existing` is not None:
  - If `debug`: `log.debug_index(func="meteorite.ensure_meteorite_company", index=1, total=1, identifier=short_name, outcome="already-present")` then `log.debug_detail(f"candidate_id={candidate_id}")`.
  - Return `{"short_name": short_name, "inserted": False, "company": existing}`.
- Else call `save_company(...)` with:
  - `short_name=short_name`
  - `state=METEORITE_CONFIG["company_state"]`  # IGNORE
  - `company_name=METEORITE_CONFIG["company_name"]`
  - `company_data=dict(METEORITE_CONFIG["company_data"])`  # shallow copy
  - `candidate_id=candidate_id`
  - leave `company_website` / `job_site` as default `None`
- Re-fetch with `get_company(short_name)` (must exist after save; if None raise `RuntimeError`).
- If `debug`: `log.debug_index(..., outcome="inserted")` + `log.debug_detail(f"candidate_id={candidate_id}")`.
- Return `{"short_name": short_name, "inserted": True, "company": row}`.

⚠️ **Decision:** New `src/core/meteorite.py` rather than stuffing into `roster.py` — AST-1042 and later ingest call ensure without pulling roster orchestration. Debug uses Style D only when `debug=True`; no `logger.info("[DEBUG]")` lines.

3. Do **not** add hooks that delete `meteorite-*` when a candidate leaves ACTIVE_SEARCH (leave-in-place = absence of reaper code).

4. In `src/data/database.py`:

- Import `METEORITE_CONFIG` alongside the existing `from src.utils.config import (...)` list.
- In `set_company_batch`, inside the **claim** branch (`clear=False`), after building `where_base` / `params` and **before** the `UPDATE ... WHERE short_name IN (SELECT ...)` / order/limit execute, append:

```python
meteorite_prefix = METEORITE_CONFIG["short_name_prefix"]
where_base += " AND short_name NOT LIKE ?"
params.append(meteorite_prefix + "%")
```

- Do **this only for claim** (`clear=False`), never for `clear=True`.
- Update the `set_company_batch` / `claim_company_batch` docstrings with one sentence: claim excludes short names matching `METEORITE_CONFIG["short_name_prefix"]`.

⚠️ **Decision:** Hard exclusion in data claim SQL (not only “IGNORE has no batch_criteria”) so a mistaken `state=IGNORE` claim or future trigger cannot pull meteorite placeholders into roster/gazer batches. Prefix comes from config — no inline `"meteorite-"` string in `database.py`.

5. Do **not** implement AST-1042 HTTP create, job inserts, or UI. Do **not** edit `tests/` / bible.

**Done when (recheck):** Calling ensure twice for the same candidate inserts once then no-ops; claim SQL cannot select `meteorite-*`; `debug=False` emits no new Style D lines from ensure; server start still does not seed meteorite rows.

## Out of scope (do not implement here)

- API create job under meteorite from raw HTML (AST-1042).
- Email ingest / calling ensure from Gmail path (later ingest epic / AST-1031 sibling).
- Admin UI for meteorite job create.
- Bulk seed at server start.
- Deleting or transitioning `meteorite-*` when candidate leaves ACTIVE_SEARCH.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — one config block, one new core module, one claim-SQL exclusion in `database.py`; no UI/external.

**Conf:** `high` — reuses `save_company` / `get_company` / Style D logging / existing IGNORE registry; claim exclusion mirrors other `where_base` filters in `set_company_batch`.

**Risk:** `Medium` — wrong claim filter could hide real companies (mitigated by config prefix + `NOT LIKE prefix%` only) or miss meteorite rows (prefix must match template); wrong ensure upsert could wipe company fields via `INSERT OR REPLACE` (mitigated by only inserting when missing).

## Rules self-review

- **§2.1 / no-hardcoded-sets:** All meteorite literals in `METEORITE_CONFIG`; claim uses `METEORITE_CONFIG["short_name_prefix"]`.
- **§1.5.1 debug-contract-gated:** Style D only when `debug=True` on ensure.
- **§2.6 / COMPANY_STATES:** Ensure writes registered `IGNORE` only.
- **§3.3 imports:** `meteorite.py` → data + utils; `database.py` → utils only (adds METEORITE_CONFIG import).
- **§1.3 public-then-helpers:** Single public `ensure_meteorite_company`.
- **database-header-inventory:** Uses existing `company` table only; no new tables.
- **In-scope only:** No job create / email / UI.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`
**Plan path:** `docs/features/meteorite/ast-1041-meteorite-company-config-lazy-ensure.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `b5d968b3` | METEORITE_CONFIG after JOB_STATES (IGNORE template + AST-1042 job-create defaults) |
| 2 | `047be5ff` | ensure_meteorite_company + set_company_batch claim NOT LIKE prefix |

**Tip:** `c49e1711a829850cc8b58c2b0b539ab622f682b9` on `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1041
**Publish ref tip (pre-docs):** `ae062c74123c6c862f676459dc82cfa339c5c5d4`
**Overall:** DISCUSS

### What’s solid
- `METEORITE_CONFIG` owns literals; `ensure_meteorite_company` insert-once / no-op; Style D only when `debug=True`.
- Claim `NOT LIKE` prefix from config in `set_company_batch` clear=False only; no bulk seed / no reaper / no AST-1042 API.

### Issues
- **discuss (straggler ×3):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot now includes `docs/features/**` + Betty tests/bible — all **conforms** on substance.

### Recommended actions
- Ada: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `fffc224e` — **Overall:** DISCUSS; **fix-now:** none; **discuss:** statute straggler ×3 (all substance **conforms**); no advisory.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (`docs/features/**` + Betty tests/bible) — no code delta. Advanced to **User Testing**.

