# AST-1133 — qualify_meteorite for list-created meteorites

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1133/qualify-meteorite-for-list-created-meteorites-manage-email-create  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working  

**Publish ref (origin):** `sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites`  
**Parent integration ref:** `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`

After AST-1131 / AST-1132 produce clean **METEORITE_NEW** rows from Manage Email list Create (Dice Saved-jobs HTML or newline-delimited ATS links), owns restoring end-to-end `qualify_meteorite` so usable extracts reach **METEORITE_QUALIFIED** with non-empty `job_title` and non-empty `company_job_id`. Investigates remaining **METEORITE_ERROR_QUALIFY** (technical / missing-id) vs content **METEORITE_FAILED_QUALIFY**. Does **not** widen `gaze_email` Ruth parse (AST-1089), change GDL, or re-own paste normalize / link hygiene.

**Diagnosis (code tip after AST-1131+1132 merge — no runtime spike required):**

Create already lands `job_link` + Playwright JD with null title / null `company_job_id` (`create_meteorite_job`). Shipped qualify path already has: Pattern-A batch apply (AST-1062), placeholder `"000"` / `\d{1,3}` bind (AST-1076), optional schema `company_job_id` + UUID-from-`job_link` resolve (AST-1120 / AST-1127). Two remaining gaps still push **usable** list-created rows off the QUALIFIED path:

1. **Multi-job claim-id bind gap → ERROR:** `_bind_response_jobs_to_claimed` only remaps empty/`\d{1,3}` when `len(response) == len(claimed)`. When Ruth echoes a non-digit wrong id (e.g. external UUID, or job URL) into `astral_job_id` on a multi-job batch, every row is treated as FABRICATED and every claim becomes MISSING → **METEORITE_ERROR_QUALIFY**. List Create commonly qualifies 2–N jobs in one batch; single-job bind does not cover that shape.
2. **Create-time `job_link` ignored by http content gate → FAILED:** `qualify_meteorite` process already uses `input_job["job_link"]` for `_resolve_company_job_id` fallback, but the `job_link.startswith("http")` gate and `initialize_job` persist only Ruth’s `job_link`. Empty / non-http Ruth link fails content gate even when Create stored a clean ATS URL — wrong outcome for usable extracts (should QUALIFY with create link, not FAILED/ERROR).

True content failures (short title, short `jd_text`, no AI id and no UUID in any usable link) stay **METEORITE_FAILED_QUALIFY**. Whole-batch `do_task` envelope/schema failures stay **METEORITE_ERROR_QUALIFY** (not reinvented here).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Job-link claim-id bind for `qualify_meteorite` multi-job batches; input `job_link` fallback in `qualify_meteorite` process + Style D source label | core |

No config / gazer / inbox / dispatcher / agent_task / UI / `tests/` / bible changes (Betty after Code Complete). Do **not** edit `_bind_response_jobs_to_claimed` digit rules (AST-1076 stays as-is). Do **not** invent a parallel batch shape or force `batch_size=1`.

---

## Stage 1: Bind multi-job qualify responses by `job_link` when claim ids mismatch

**Done when:** A multi-job `qualify_meteorite` batch whose Ruth rows carry usable title / link / jd / id fields but non-claimed non-digit `astral_job_id` values still bind 1:1 to claimed rows via normalized `job_link`, reach `process_fn`, and can land **METEORITE_QUALIFIED**; equal-count digit/`000` bind (AST-1076) still works first; unmatched / ambiguous links are left for existing MISSING/FABRICATED accounting; `qualify_job_listings` path unchanged; `python3 -m py_compile src/core/consult.py` succeeds.

1. In `src/core/consult.py`, immediately after `_bind_response_jobs_to_claimed`, add:

```python
def _bind_response_jobs_by_job_link(response_jobs: list, claimed_jobs: list) -> None:
    """Bind unmatched response rows to claimed jobs by normalized job_link (AST-1133).

    Used when Ruth puts a non-digit wrong value in astral_job_id on multi-job
    qualify_meteorite batches. Does not overwrite ids already in the claim set.
    """
```

2. Implement literally:

- Import `normalize_link` from `src.utils.formatting` at module top if not already imported (consult already imports `uuid_path_segment_from_url` from the same module — add `normalize_link` to that import).
- Skip if `response_jobs` empty or `claimed_jobs` empty.
- `claimed_ids = [j["astral_job_id"] for j in claimed_jobs if j.get("astral_job_id")]`
- `claimed_set = set(claimed_ids)`
- `claimed_by_link: dict[str, str] = {}` — for each claimed job with both `astral_job_id` and a non-empty `normalize_link(job_link)`, map `norm → astral_job_id`. If two claims normalize to the same key, **drop that key** from the map (ambiguous — do not bind either via link).
- `assigned = { (rj.get("astral_job_id") or "").strip() for rj in response_jobs if isinstance(rj, dict) and (rj.get("astral_job_id") or "").strip() in claimed_set }`
- For each `rj` in `response_jobs` where `isinstance(rj, dict)`:
  - `aid = (rj.get("astral_job_id") or "").strip()`
  - If `aid in claimed_set`: continue
  - `norm = normalize_link(rj.get("job_link") or "")`
  - If not `norm`: continue
  - `target = claimed_by_link.get(norm)`
  - If not `target` or `target in assigned`: continue
  - Set `rj["astral_job_id"] = target`; add `target` to `assigned`

⚠️ **Decision — second helper, do not widen AST-1076 digit remap:** AST-1076 explicitly refuses to overwrite non-digit fabricated UUIDs on multi-job batches (correct for listing grades). List-created meteorites have authoritative Create `job_link`s that Ruth is also asked to echo — link match is a safe second key without promoting arbitrary UUID remaps.

⚠️ **Decision — qualify_meteorite only:** Call this helper only for `task_key == "qualify_meteorite"` so roster `qualify_job_listings` keeps today’s bind surface.

3. In `_run_batch_consult`, immediately after `_bind_response_jobs_to_claimed(response_jobs, jobs)`, add:

```python
    if task_key == "qualify_meteorite":
        _bind_response_jobs_by_job_link(response_jobs, jobs)
```

4. When `debug` and `task_key == "qualify_meteorite"`, after both binds, emit one `debug_detail` listing final `astral_job_id` values on `response_jobs` (compact list). Do **not** emit when `debug=False`.

**Done when (recheck):** Claimed links `L0,L1,L2` with ids `C0,C1,C2`; Ruth returns three jobs with `astral_job_id` = Dice UUIDs (not C*) but `job_link` matching `L0..L2` and usable title/jd/company_job_id → after bind, `received_ids == {C0,C1,C2}`, no MISSING, process runs, states can reach **METEORITE_QUALIFIED**. Ambiguous duplicate normalized links → no link-bind for that key; digit bind still applies when lengths match.

---

## Stage 2: Prefer Create-time `job_link` when Ruth’s link is unusable

**Done when:** `qualify_meteorite` process uses a http(s) `job_link` from the claimed input row when Ruth’s `job_link` is empty or does not start with `"http"`; UUID resolve + `initialize_job` persist that link; content fail for short title / short jd / empty resolved `company_job_id` still → **METEORITE_FAILED_QUALIFY**; Style D records whether link came from AI or input; single-job happy path with good Ruth link unchanged; `python3 -m py_compile src/core/consult.py` succeeds.

1. In `qualify_meteorite`’s `process` closure, replace the current strip + resolve preamble so that after reading Ruth fields:

```python
        ai_company_job_id = (response_job.get("company_job_id") or "").strip()
        job_title = (response_job.get("job_title") or "").strip()
        ruth_link = (response_job.get("job_link") or "").strip()
        input_link = (input_job.get("job_link") or "").strip()
        jd_text = (response_job.get("jd_text") or "").strip()
        if ruth_link.startswith("http"):
            job_link = ruth_link
            link_source = "AI"
        elif input_link.startswith("http"):
            job_link = input_link
            link_source = "input"
        else:
            job_link = ruth_link
            link_source = "neither"
        company_job_id = _resolve_company_job_id(ai_company_job_id, job_link)
```

2. Keep the existing `id_source` labels for `company_job_id` (`AI` / `UUID-from-job_link` / `neither`) based on `ai_company_job_id` vs resolved id — unchanged logic, but pass `job_link` (post-fallback) into `_resolve_company_job_id` (no separate `link_for_id`).

3. Keep content gates in this order: empty `company_job_id` → title too short → `not job_link.startswith("http")` → `jd_text` too short. On fail / pass Style D detail lines, append `link_source={link_source}` next to the existing `found source={id_source}` bits (debug only).

4. Pass path: `parsed_job["job_link"]` must be the post-fallback `job_link` (so Create ATS URL is recorded when Ruth omitted it).

⚠️ **Decision — no jd_text / title fallback from input:** Title is null at Create; Playwright body may be chrome-heavy. Ruth still owns title + authoritative `jd_text`. Only `job_link` is Create-authoritative for list ingest.

⚠️ **Decision — Ruth http link wins when present:** Prefer AI enrich URL when it is a real http(s) link; fall back only when Ruth’s value cannot satisfy the http gate.

**Done when (recheck):** Claimed job with `job_link=https://www.dice.com/job-detail/<uuid>`, Ruth returns title + jd + omit/`null` `company_job_id` + empty `job_link` → resolve UUID from input link, pass http gate, → **METEORITE_QUALIFIED** with non-empty title + `company_job_id` + recorded Dice link. Short title still → **METEORITE_FAILED_QUALIFY**. Envelope `do_task` failure still → **METEORITE_ERROR_QUALIFY** for the batch (unchanged).

---

## Self-Assessment

**Scope:** `Single-Component` — one core file (`consult.py`); bind helper + qualify process link fallback only.

**Conf:** `high` — tip after 1131/1132 already has apply + digit bind + UUID resolve; remaining ERROR/FAILED paths for usable list rows are the two concrete gaps above.

**Risk:** `Medium` — over-eager link bind could mis-pair if Ruth returns wrong links; mitigated by unique normalized-link map + never overwriting claimed ids + qualify_meteorite-only call site. Wrong input-link fallback would persist Create URL when Ruth intended a different http link — mitigated by preferring Ruth whenever it starts with `http`.

---

## Self-review vs ASTRAL_CODE_RULES

- **§2.4 claim-process-release / `pattern.batch.entity-claim-process-release`:** Batch shape unchanged; only id reconciliation + process field selection harden.
- **§2.6 / `astral.state.core-decides-transitions`:** Core still maps pass → QUALIFIED, content → FAILED_QUALIFY, technical → ERROR_QUALIFY; no new states.
- **§2.2 / `astral.agent.do-task-delegation`:** Still one `do_task` via `_run_batch_consult`; no UI LLM.
- **§1.5.1 / `astral.standards.debug-contract-gated`:** New detail only under existing `debug` gates.
- **§1.3 DRY:** Second bind helper; digit rules left in AST-1076 helper.
- **§1.1 in-scope-only:** No gazer / gaze_email / GDL / config knobs.
- **§3.3 import-direction:** `normalize_link` from utils into core — already allowed.

No plan conflicts requiring `conf-!!-NONE`.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites`  
**Plan path:** `docs/features/meteorite/ast-1133-qualify-meteorite-for-list-created-meteorites.md`

**Built tip:** `f172b5376185b2842c79f06fd506a0defc148a44` (`f172b537`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `f172b537` | job-link claim bind + Create-time job_link fallback in qualify_meteorite |

---

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1133
**Publish ref tip:** `3e01f3dc3bf0a7a30557c00fd5871de580995a8c`
**Overall:** DISCUSS

### What's solid

- Stages 1–2 match: `_bind_response_jobs_by_job_link` (unique normalize_link map, no overwrite of claimed ids, qualify_meteorite-only) + Create http(s) `job_link` fallback with `link_source` Style D.
- AST-1076 digit bind left intact; claim→process→release shape unchanged; QUALIFIED / FAILED_QUALIFY / ERROR_QUALIFY outcomes preserved.
- AST-1133 `code()` product touch is `consult.py` only; Betty `test()` + one `merge-tests`.

### Issues

**discuss:** `orch.git.commit-vocabulary` — `59ec6ce3` / `8d01c0c7` are docs-only plan tip fills committed as `code()`. Should have been `docs()`. No rewrite required; ack for future.

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.dispatch.seed-auto-false` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.layers.ui-config-driven-business-logic` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.seed.agent-tables-in-repo-json` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.seed.archie-catalog-wins` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.seed.operator-rows-stay-deleted` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.seed.other-via-coverage-join` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.standards.database-header-inventory` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.standards.utils-data-late-import-only` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.ui.single-gunicorn-worker` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.

### Recommended actions

- Engineer: ack vocabulary + C4 stragglers (no src change), then User Testing via `resolve-child`.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | No grade confidence path changes |
| `astral.agent.do-task-delegation` | scoped | conforms | Still one do_task via _run_batch_consult |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vector schema changes |
| `astral.batch.batch-id-first` | scoped | conforms | No claim helper signature changes |
| `astral.batch.batch-id-format` | scoped | conforms | No batch_id format changes |
| `astral.batch.claim-process-release` | scoped | conforms | Batch shape unchanged; bind + process field harden only |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data RESPONSE inventory changes |
| `astral.config.config-source-of-truth` | scoped | conforms | No new qualify knobs; rollup config from siblings only |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No scoring threshold changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss diff (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Combined plans under docs/features — not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | No dispatch/run_next changes |
| `astral.dispatch.seed-auto-false` | scoped | conforms | No seed/dispatch_task AUTO changes in this tip |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | One docs/features plan file for AST-1133 |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test/bible only; merge-tests exception ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Product code() is consult.py; tests from Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Core-only consult harden; no new I/O |
| `astral.layers.import-direction` | scoped | conforms | normalize_link from utils into core |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff empty (['scripts']); paths miss diff (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No UI rules; config rollup not UI business logic |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check keys |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | qualify_meteorite stays on _run_batch_consult path |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | No seed JSON work |
| `astral.seed.archie-catalog-wins` | scoped | conforms | No catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | No seed/boot path |
| `astral.seed.define-approved` | scoped | conforms | No seed define work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | No operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | No coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer edits in AST-1133 code() |
| `astral.standards.database-header-inventory` | scoped | conforms | Rollup uses existing job/company tables only |
| `astral.standards.debug-contract-gated` | scoped | conforms | Bind/link_source detail only when debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Second bind helper; AST-1076 digit rules intact |
| `astral.standards.in-scope-only` | scoped | conforms | AST-1133 code() is consult.py only |
| `astral.standards.logging-via-utils` | scoped | conforms | Style D via existing consult debug helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | _bind_response_jobs_by_job_link product-shaped |
| `astral.standards.no-cross-contamination` | scoped | conforms | qualify_meteorite-only call site; listings bind unchanged |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | No new host/state sets; existing http prefix gate |
| `astral.standards.public-then-helpers` | scoped | conforms | New bind helper next to existing bind helper |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | Core still QUALIFIED / FAILED_QUALIFY / ERROR_QUALIFY |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No JOB_STATES registry edits |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next / daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No gunicorn/worker config changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1133) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | needs-discussion | Two docs-only tip stubs used code() not docs() |
| `orch.git.flow-direction-inviolable` | universal | conforms | Publish stays on origin/sub/AST-1130/AST-1133-… |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under AST-1130 parent topology |
| `orch.git.merge-on-checkout` | universal | conforms | No illegal merge-on-checkout recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick/rebase/force on publish ref |
| `orch.git.no-dev-agent-branches` | universal | conforms | Uses sub/AST-1130/AST-1133-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in astral-AST-1130 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | No product-decision fork; plan decisions shipped |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match Files Changed and consult.py diff |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee remains Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Implementer stays assignee through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path product commits |

### Pattern conformance

- `pattern.batch.entity-claim-process-release` — **conforms**
- `pattern.state.entity-state-transitions` — **conforms**

### Plan adherence

Self-Assessment **Single-Component** matches (`consult.py` only for this ticket). Boundaries vs AST-1131/1132 / gaze_email / GDL held. Three-dot vs origin/dev carries sibling epic rollup — expected, not scope smuggle in AST-1133 product commits.

context_tokens≈48000
