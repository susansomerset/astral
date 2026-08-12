<!-- linear-archive: AST-1042 archived 2026-08-05 -->

## Linear archive (AST-1042)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1042/api-create-job-under-meteorite-from-raw-html-support-meteorite-jobs  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1034 — Support meteorite jobs  
**Blocked by / blocks / related:** parent: AST-1034

### Description

## What this implements

Owns the API create path that lazy-ensures the candidate’s meteorite company, then creates a job from raw HTML as the JD, landing in **JD_READY** with **latest_score 10.0** (synthetic joblist-qualifier stand-in), with a legal prior_states entry path — no new job state, no admin UI, no email ingest. After AST-1041.

## Citations

`pattern.state.entity-state-transitions`; `astral.state.job-prior-states-enforced`; `astral.state.core-decides-transitions`; `astral.config.pass-threshold-vs-score-floor`; `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.patterns.require-auth-on-protected-endpoints`.

## Acceptance criteria

4. An authenticated API create call can create a job under `meteorite-<candidate_id>` from raw HTML job-description content; it lazy-ensures the company first; the job is in **JD_READY**, has **latest_score 10.0**, persists that HTML as the JD, and does not require a real employer website or a fetch_jd scrape.
5. No admin UI for meteorite job create ships in this epic.
6. Existing non-meteorite company and job flows still behave as before (smoke: a normal company is still claimable on its existing triggers).

## Boundaries

Does **not** own meteorite company config/ensure (AST-1041). Does **not** own email ingest or admin UI.

## Notes for planning

Citations above. Calls lazy-ensure from sibling. After #1.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1034-support-meteorite-jobs`, child `sub/AST-1034/<this-id>-api-create-job-under-meteorite-from-raw-html`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-29T18:04:24.476Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offending subject in `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html` (not on ftr): `baf34d2e Merge remote-tracking branch 'origin/ftr/AST-1034-support-meteorite-jobs' into sub/…`

@Hedy Lamarr — rewrite that merge off the publish tip (custom `-m` merge message, or rebase onto `origin/ftr/AST-1034-support-meteorite-jobs` so no `Merge remote-tracking branch` subject remains in the sub-only range), force-push publish ref only, stay User Testing. Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-07-29T18:03:01.530Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1042
**Publish ref:** `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html` @ `56b46d43` (product tip `e057271a` + docs review)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html` — 1042 create API + core carve-out; three-dot also carries AST-1041 (blocked-by, already reviewed).
**Notes:** Joan plan-rubric attached (APPROVED). Five C4 stragglers (substance conforms). No fix-now.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence / agent scoring |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched |
| astral.batch.batch-id-first | scoped | conforms | No batch claim changes in 1042 |
| astral.batch.batch-id-format | scoped | conforms | Untouched |
| astral.batch.claim-process-release | scoped | conforms | Claim exclusion remains AST-1041 |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | State/score from `METEORITE_CONFIG`; JD key from `TRACKER_CONFIG` |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Synthetic 10.0 eligibility stand-in, not grading |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plans under `docs/features/` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file per ticket (1041 + 1042) |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer src/features; Betty tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | Betty owns `test()`/`merge-tests()` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No scrape/external I/O |
| astral.layers.import-direction | scoped | conforms | ui→core+utils+auth; core→data+utils+candidate |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss (`scripts`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Thin API; create policy in core |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check / fetch_jd |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_auth` on POST |
| astral.standards.data-raises-caller-logs | scoped | conforms | Core raises; API maps 400/404/502 |
| astral.standards.database-header-inventory | scoped | conforms | Existing company/job APIs; no new tables |
| astral.standards.debug-contract-gated | scoped | conforms | Passes `debug` through to ensure only |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses ensure; one create helper |
| astral.standards.in-scope-only | scoped | conforms | No UI/email/JOB_STATES expansion |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` on API failure path |
| astral.standards.no-cross-contamination | scoped | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | scoped | conforms | No inline JD_READY/10.0/`job_description` literals |
| astral.standards.public-then-helpers | scoped | conforms | Public `create_meteorite_job` |
| astral.standards.utils-data-late-import-only | scoped | conforms | Config-only utils touch; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | Core chooses state+score from config |
| astral.state.job-prior-states-enforced | scoped | conforms | Documented create carve-out; JD_READY priors unchanged |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss (`frontend/**`) |
| astral.ui.naming-conventions | scoped | conforms | `api_meteorite.py` + snake_case route |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1042)` @ `e057271a` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html` |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/...` already ancestor |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1034` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Carve-out already decided in plan/parent |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match shipped code |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit |

## Pattern conformance

| cited | verdict |
| -- | -- |
| `pattern.state.entity-state-transitions` | conforms — create carve-out documented; priors unchanged |
| `astral.state.job-prior-states-enforced` | conforms |
| `astral.state.core-decides-transitions` | conforms |
| `astral.config.pass-threshold-vs-score-floor` | conforms — synthetic score stand-in |
| `pattern.layers.import-discipline` | conforms — ui→core only |
| `astral.layers.import-direction` | conforms |
| `astral.patterns.require-auth-on-protected-endpoints` | conforms — `@require_auth` |

## Plan adherence

Stages 1–2 match Self-Assessment **Single-Component**. Ensure → insert JD_READY + two-step `latest_score`, auth-gated candidate-scoped POST, 400/404/502 mapping, and no UI/email/JOB_STATES expansion match the plan bible. Three-dot carries AST-1041 (blocked-by).

## Findings

### fix-now
(none)

### discuss
**straggler (Joan excluded → in-scope on three-dot; substance conforms):**
1. `astral.debug.spikes-under-debug-dir`
2. `astral.docs.features-single-file-per-ticket`
3. `astral.git.engineer-test-tree-ban`
4. `astral.standards.database-header-inventory` (AST-1041 `database.py` in three-dot)
5. `astral.standards.utils-data-late-import-only` (`config.py` in three-dot)

### advisory
(none)

### What’s solid
- Create carve-out avoids expanding JD_READY priors; postcondition checks after score update; thin HTTP response omits full job blob.

### Recommended actions
- Hedy: acknowledge stragglers (no product change expected) → resolve-child → User Testing.

context_tokens≈42000

#### betty — 2026-07-29T17:58:10.329Z
1. `tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob` — validation; missing candidate; JD_READY + score 10.0 + HTML JD; second create company no-op + new job
2. `tests/component/ui/api/test_api_meteorite.py` — POST create 201/400/404/502; 401 unauth; non-admin allowed (`@require_auth`)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  -q
```

**Pass:** pytest green on the two items above.

**Broken/revised:** none — additive `create_meteorite_job` + new `api_meteorite` blueprint. Keep AST-1041 ensure coverage in `test_meteorite.py`.
**Integration:** no existing `tests/integration/` scenarios assert meteorite job create — none revised; no new scenarios.

**Publish:** `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html` @ `e057271a` (`merge-tests(AST-1042): origin/tests 25762e62b7e2240ba72684926c73735ee2805e9f`)

**Bible shasums on publish ref:**
- `docs/test-bible/core/meteorite.md` `889c8e560a139ff85aad363d10ce9724c393565b`
- `docs/test-bible/ui/api/api_meteorite.md` `97a8bbe76de384cd2777e2119b5ab3c13f845673`

— Betty

#### joan — 2026-07-29T17:52:32.907Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1042
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `617746d7`. Blocked-by AST-1041 present on publish tip (`METEORITE_CONFIG` + `ensure_meteorite_company`). Create carve-out into JD_READY matches parent Architectural “documented create carve-out” option without expanding `prior_states`.
**Implementer:** Hedy (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1–3 meteorite config / ensure / claim exclusion | N/A — boundary: AST-1041 (dependency) |
| 4 Authenticated API create under meteorite from raw HTML → JD_READY + score 10.0 | Stages 1–2 |
| 5 No admin UI | Explicit out of scope; no React/NAV |
| 6 Leave-in-place lifecycle | N/A — AST-1041 |
| 7 Style D on lazy-ensure | Ensure call with `debug=`; no new create-only contract required |
| 8 Non-meteorite flows unchanged | No claim/roster edits in this child |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 4 API create + ensure + JD_READY + score + HTML JD | 1–2 |
| 5 No admin UI | Out of scope / Stage 2 |
| 6 Non-meteorite smoke | No claim-path edits |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 `create_meteorite_job` carve-out | Functional scope API create; Architectural prior_states carve-out; AC4 |
| 2 Auth-gated blueprint + register | AC4 authenticated; require_auth; Boundaries (no UI/email) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1042):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | 1041 already ancestor on tip |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1034` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Carve-out vs expand-priors decided per parent Architectural |
| orch.pipeline.plan-is-bible | conforms | Stages binding; 1041/email/UI excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Hedy on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | No AI/do_task |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | State/score from `METEORITE_CONFIG`; JD key from `TRACKER_CONFIG` |
| astral.config.pass-threshold-vs-score-floor | conforms | Synthetic 10.0 is eligibility stand-in, not grading |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | No scrape/external I/O |
| astral.layers.import-direction | conforms | ui → core+utils+auth; core → data+utils |
| astral.layers.ui-config-driven-business-logic | conforms | Thin API; create policy in core |
| astral.patterns.coat-check-never-store-empty | conforms | Explicitly avoids coat-check fetch |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_auth` on POST |
| astral.standards.data-raises-caller-logs | conforms | Core/API map errors; data raises |
| astral.standards.debug-contract-gated | conforms | Passes `debug` through to ensure only |
| astral.standards.dry-and-focused-functions | conforms | Reuses ensure; one create helper |
| astral.standards.in-scope-only | conforms | No UI/email/JOB_STATES expansion/tests |
| astral.standards.logging-via-utils | conforms | `get_logger` on API failure path |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | No inline JD_READY/10.0/job_description literals |
| astral.standards.public-then-helpers | conforms | Public `create_meteorite_job` |
| astral.state.core-decides-transitions | conforms | Core chooses state+score from config; data persists |
| astral.state.job-prior-states-enforced | conforms | Documented create carve-out; `transition_job_state` / JD_READY priors unchanged |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.naming-conventions | conforms | `api_meteorite.py` + snake_case route |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.ui.frontend-file-placement — paths miss (no frontend files)

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Two-step `save_job` insert + `latest_score` update — INSERT SQL omits `latest_score` today; update path writes it; postcondition checks are right.
2. Create carve-out vs expanding JD_READY `prior_states` — avoids legalizing scrape hops into JD_READY from empty; mirrors ingest→NEW insert pattern; parent-allowed.
3. `@require_auth` (not admin) + candidate-scoped route — matches authenticated API AC, not admin UI.
4. Self-assessment Single-Component / high / Medium — honest about score-floor risk.
5. Response omits full `job` blob — fine for thin API.

— Joan
context_tokens≈52000

#### hedy — 2026-07-29T17:29:06.325Z
Plan published on `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html` @ `617746d7`.

**Plan:** [docs/features/meteorite/ast-1042-api-create-job-under-meteorite-from-raw-html.md](https://github.com/susansomerset/astral/blob/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html/docs/features/meteorite/ast-1042-api-create-job-under-meteorite-from-raw-html.md)

**Self-assessment**
- **Scope:** Single-Component — extends `meteorite.py` with create carve-out; thin `@require_auth` blueprint + server register; no UI/email/JOB_STATES expansion.
- **Conf:** high — AST-1041 ensure + `METEORITE_CONFIG` job-create defaults already on ftr; insert mirrors `ingest_jobs` → NEW.
- **Risk:** Medium — missing `latest_score` update would leave NULL and score-floor would drop the job; mitigated by two-step write + postcondition checks.

---

# AST-1042 — API create job under meteorite from raw HTML

**Linear:** [AST-1042](https://linear.app/astralcareermatch/issue/AST-1042/api-create-job-under-meteorite-from-raw-html-support-meteorite-jobs)
**Parent:** [AST-1034](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs) — Support meteorite jobs
**Publish ref:** `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html`

Authenticated API that lazy-ensures the candidate’s meteorite company (AST-1041 `ensure_meteorite_company`), then creates a job under `meteorite-<candidate_id>` from raw HTML as the JD. The job lands in **JD_READY** with **latest_score 10.0** from `METEORITE_CONFIG` (synthetic joblist-qualifier stand-in) via a documented create carve-out — no new job state, no admin UI, no email ingest, no fetch_jd scrape.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | Add `create_meteorite_job` (ensure → insert JD_READY + score + HTML JD) | core |
| `src/ui/api/api_meteorite.py` | New blueprint: `POST …/meteorite/jobs` under `@require_auth` | ui |
| `src/ui/server.py` | Register `meteorite_bp` | ui |

## Stage 1: Core create carve-out (ensure + JD_READY insert)

**Done when:** Callers can `create_meteorite_job(candidate_id, html_body)` and get a persisted job under the meteorite short_name in `METEORITE_CONFIG["job_create_state"]` with `latest_score == METEORITE_CONFIG["job_create_latest_score"]` and HTML in `job_data` under the tracker JD key — without calling `transition_job_state`, without inventing a new `JOB_STATES` key, and without scraping.

1. In `src/core/meteorite.py`, update the module docstring to state that this module owns meteorite company ensure **and** API-facing job create from raw HTML (AST-1042). Still no email ingest and no admin UI.

2. Add imports needed for create (keep ensure imports; add only what create uses):

```python
import uuid
from datetime import datetime, timezone

from src.core.candidate import get_candidate
from src.data.database import get_company, get_job, save_company, save_job
from src.utils.config import METEORITE_CONFIG, TRACKER_CONFIG
```

(`get_logger` already present for ensure.)

3. Add public `create_meteorite_job` **above** any new helpers (public-first). Signature and contract:

```python
def create_meteorite_job(
    candidate_id: str,
    html_body: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Lazy-ensure meteorite company, then insert a JD_READY job from raw HTML.

    Create carve-out (not transition_job_state): first write inserts directly into
    METEORITE_CONFIG["job_create_state"] the same way ingest_jobs inserts into NEW
    (JOB_STATES prior_states=None unrestricted entry). JD_READY's registered
    prior_states remain ["PASSED_JOBLIST"] for scrape/qualify hops — this path does
    not expand those priors and does not invent a new job state.

    Returns:
      {
        "astral_job_id": str,
        "company": str,           # meteorite-<candidate_id>
        "state": str,             # job_create_state
        "latest_score": float,    # job_create_latest_score
        "company_inserted": bool, # from ensure
        "job": dict,              # get_job row after writes
      }
    """
```

4. Concrete steps inside `create_meteorite_job`:

- Strip `candidate_id`; if empty → `ValueError("candidate_id is required")`.
- Require `html_body` to be a `str`; strip for emptiness check only — **persist the original `html_body` string as provided** (do not `parse_text` / cull / convert). If `not isinstance(html_body, str) or not html_body.strip()` → `ValueError("html_body is required")`.
- Load candidate: `cand = get_candidate(candidate_id)`; if missing → `ValueError(f"candidate not found: {candidate_id}")` (API maps to 404).
- `ensured = ensure_meteorite_company(candidate_id, debug=debug)`.
- `short_name = ensured["short_name"]` (must equal `METEORITE_CONFIG["short_name_template"].format(candidate_id=candidate_id)`).
- Resolve JD key: `jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]` (today `"job_description"` — do not hardcode the string in meteorite.py).
- `state = METEORITE_CONFIG["job_create_state"]`  # JD_READY
- `score = float(METEORITE_CONFIG["job_create_latest_score"])`  # 10.0
- `astral_job_id = str(uuid.uuid4())`
- `now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")`
- **Insert** via `save_job` (create carve-out — do **not** call `transition_job_state`):

```python
inserted = save_job(
    astral_job_id,
    company=short_name,
    state=state,
    job_title=None,
    job_link=None,
    company_job_id=None,
    job_data={jd_key: html_body},
    state_history=[{"to_state": state, "timestamp": now, "score": score}],
    state_changed_at=now,
    merge=False,
)
if not inserted:
    raise RuntimeError(f"meteorite job insert failed: {astral_job_id}")
```

- **Score column:** `database.save_job` INSERT path does not write `latest_score` today. Immediately follow with an update-only call:

```python
save_job(astral_job_id, latest_score=score)
```

⚠️ **Decision:** Two-step insert + `latest_score` update rather than changing `save_job` INSERT SQL for all callers. Same end state as a single insert that included the column; keeps AST-1042 scoped to meteorite create.

- `row = get_job(astral_job_id)`; if None → `RuntimeError`.
- Verify `row["state"] == state` and `row.get("latest_score") == score` (float compare OK); if not → `RuntimeError` with detail.
- Return the dict shape above (`company_inserted=ensured["inserted"]`, `job=row`).

5. Do **not** call `initialize_job`, `transition_job_state`, playwright / `get_job_data` coat-check, or invent `job_title` / `job_link` / `company_job_id`. Do **not** expand `JOB_STATES["JD_READY"]["prior_states"]`. Do **not** add a new job state.

⚠️ **Decision:** Create carve-out (direct insert into JD_READY) instead of expanding `prior_states` to `None` or adding a predecessor state — parent forbids a new job state; unrestricted JD_READY would legalize illegal scrape hops; insert-on-create mirrors `ingest_jobs` → NEW.

**Done when (recheck):** Calling create twice for the same candidate yields two jobs (no dedup by HTML); each has company `meteorite-<id>`, state JD_READY, latest_score 10.0, and `job_data[jd_key]` equal to the supplied HTML; ensure is idempotent across calls.

## Stage 2: Auth-gated HTTP create API

**Done when:** Authenticated clients can `POST` raw HTML + candidate id and receive the create payload; missing/invalid session → 401; validation / missing candidate / upstream failures map to 400 / 404 / 502; no React/admin UI files.

1. Create `src/ui/api/api_meteorite.py` with module docstring:

```
Meteorite job-create API (AST-1042 / Support meteorite jobs).

Thin Flask wrapper over src.core.meteorite.create_meteorite_job.
No admin UI; no email ingest; no Gmail I/O.
```

2. Blueprint + route:

```python
from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.meteorite import create_meteorite_job
from src.utils.logging import get_logger

logger = get_logger(__name__)

meteorite_bp = Blueprint("meteorite", __name__, url_prefix="/api")


@meteorite_bp.route("/candidates/<candidate_id>/meteorite/jobs", methods=["POST"])
@require_auth
def meteorite_create_job(candidate_id: str):
    ...
```

⚠️ **Decision:** Path under `/api/candidates/<candidate_id>/meteorite/jobs` (not `/api/admin/…`) — parent AC is authenticated API capability, not an admin tool; matches intake-style candidate-scoped routes. `@require_auth` (not `@require_admin`) matches “authenticated API create call.”

3. Handler body:

- Parse JSON: `data = request.get_json(silent=True) or {}`.
- `html_body = data.get("html_body")` — require key present as string (see core validation).
- Optional `debug = bool(data.get("debug", False))`.
- `try: payload = create_meteorite_job(candidate_id, html_body, debug=debug)`
- Map exceptions:
  - `ValueError` whose message starts with `"candidate not found"` → `404` `{"error": str(e)}`
  - Other `ValueError` → `400` `{"error": str(e)}`
  - Any other `Exception` → log `logger.warning("[api_meteorite] create failed candidate_id=%s: %s", candidate_id, e)` → `502` `{"error": str(e)}`
- Success → `201` with JSON:

```json
{
  "astral_job_id": "...",
  "company": "meteorite-<candidate_id>",
  "state": "JD_READY",
  "latest_score": 10.0,
  "company_inserted": true|false
}
```

Do **not** return the full `job` blob unless needed — keep the response small; omit nested `job` from the HTTP body (core still returns it for callers/tests).

4. In `src/ui/server.py`, after the existing `jobs_bp` registration block, register:

```python
from ui.api.api_meteorite import meteorite_bp  # noqa: E402
app.register_blueprint(meteorite_bp)
```

Follow neighboring `# noqa: E402` style.

5. Do **not** add React pages, `NAV_CONFIG` items, `DATA_SHAPES`, or Gmail/email ingest callers. Do **not** edit `tests/` / bible.

**Done when (recheck):** Bearer-authenticated POST creates the job; unauthenticated → 401; empty `html_body` → 400; unknown candidate → 404; no UI routes added.

## Out of scope (do not implement here)

- Meteorite company config / ensure / claim exclusion (AST-1041 — already on ftr).
- Email ingest calling create/ensure (later ingest epic / AST-1031 sibling).
- Admin UI to paste HTML or create meteorite jobs.
- Expanding `JOB_STATES["JD_READY"]["prior_states"]` or adding a new job state.
- fetch_jd / playwright scrape for these jobs.
- Deleting or transitioning `meteorite-*` when candidate leaves ACTIVE_SEARCH.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — extends `src/core/meteorite.py` with one create helper; adds one thin auth-gated blueprint + server registration; no config literals beyond existing `METEORITE_CONFIG` / `TRACKER_CONFIG` keys; no UI/external.

**Conf:** `high` — ensure + `METEORITE_CONFIG` job-create defaults already shipped on AST-1041; insert carve-out mirrors `ingest_jobs` → NEW; auth pattern matches other `/api/candidates/…` routes.

**Risk:** `Medium` — wrong carve-out (calling `transition_job_state` into JD_READY from empty state) would raise; forgetting `latest_score` update would leave NULL and score-floor claim would drop the job; mitigated by explicit two-step write + postcondition checks in core.

## Rules self-review

- **§2.1 / no-hardcoded-sets:** State + score from `METEORITE_CONFIG`; JD key from `TRACKER_CONFIG["job_data_keys"]`.
- **§2.6 / job-prior-states-enforced:** Create carve-out documented; `transition_job_state` priors for JD_READY unchanged; no new `JOB_STATES` key.
- **§2.6 / core-decides-transitions:** Core chooses JD_READY + score from config; data only persists.
- **pass-threshold-vs-score-floor:** Synthetic `10.0` is dispatch eligibility stand-in only — not grading `pass_threshold`.
- **§3.3 import-direction:** `api_meteorite` → core + utils + `ui.auth`; `meteorite.py` → data + utils + `get_candidate`; no ui→external/data.
- **require-auth-on-protected-endpoints:** `@require_auth` on the create route.
- **§1.3 public-then-helpers:** Public `create_meteorite_job` after ensure; no private helpers required unless DRY appears during build.
- **In-scope only:** No UI, no email, no JOB_STATES expansion, no tests/bible.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html`
**Plan path:** `docs/features/meteorite/ast-1042-api-create-job-under-meteorite-from-raw-html.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `ec61e37f` | create_meteorite_job carve-out + POST /api/candidates/<id>/meteorite/jobs + register blueprint |

**Tip:** `e3f029ce0786fe7bf6c6c16c70bf6a9404144613` on `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1042
**Publish ref tip (pre-docs):** `e057271af4f79039e468e202bbc33138b163f3c8`
**Overall:** DISCUSS

### What’s solid
- `create_meteorite_job` carve-out → JD_READY + score from `METEORITE_CONFIG`; JD key from `TRACKER_CONFIG`; two-step insert + `latest_score` update with postconditions.
- Thin `@require_auth` POST; 400/404/502 mapping; no UI/email; ui→core only.

### Issues
- **discuss (straggler ×5):** Joan excluded spikes/docs/engineer-test-ban/database-header/utils-data-late at plan time; three-dot includes AST-1041 + Betty tests/docs — all **conforms** on substance.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `56b46d43` — **Overall:** DISCUSS; **fix-now:** none; **discuss:** statute straggler ×5 (all substance **conforms**); no advisory.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (AST-1041 + Betty tests/docs) — no code delta. Advanced to **User Testing**.

