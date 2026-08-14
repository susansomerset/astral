# AST-1367 — Topic Menu informs + Estelle allowlists

**Linear:** [AST-1367](https://linear.app/astralcareermatch/issue/AST-1367/topic-menu-informs-estelle-allowlists-add-ideal-day-to-the-set-of)
**Parent:** [AST-1360](https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc) — Add `ideal_day` to the set of candidate context (strengths, priorities, etc.)
**Publish ref:** `sub/AST-1360/AST-1367-topic-menu-informs-estelle-allowlists`
**Depends on:** [AST-1365](https://linear.app/astralcareermatch/issue/AST-1365/ideal-day-library-token-add-ideal-day-to-the-set-of-candidate-context) — `ideal_day` in `CANDIDATE_LIBRARY_CONFIG["context_keys"]` (must be on HEAD after `sync-child.sh` before build)

Extend the Topic Menu closed informs / deliverables catalog with `ideal_day`, and align Estelle preamble confirm / generate packet + patch allowlists (config + matching seed prompt wording) so Ideal Day can be summarized, revised, and targeted by topics — peer of strengths / priorities / deal_breakers / backstory. Core packet builders and `validate_topic` already read those config tuples; no new API. This ticket does **not** own Candidate Ideal Day UI (AST-1366) or JD / DO / LIKE craft rubric prompt text (AST-1368).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `ideal_day` to `TOPIC_MENU_CONFIG["informs"]` + equality/home asserts; add to `TOPIC_MENU_GEN_CONFIG["packet_context_keys"]` and `patchable_context_keys` | utils |
| `data/admin/agent_task.json` | Update `topic_menu_preamble_confirm` and `topic_menu_generate` `cache_prompt` strings so patch/informs vocabulary includes `ideal_day` | data (seed) |

**Out of scope (do not touch):**

| File / area | Owner |
|-------------|--------|
| `CANDIDATE_LIBRARY_CONFIG` / `TOKEN_SOURCES["IDEAL_DAY"]` / completeness gate | AST-1365 (already on tip) |
| `NAV_CONFIG`, `CandidateIdealDay.tsx`, routes | AST-1366 |
| `craft_do_rubric` / LIKE / Job Description craft rows | AST-1368 |
| `src/core/intake.py` / `src/core/candidate.py` | No code change — already iterate config |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Already documents `context.ideal_day`; topic_menu `informs` already ⊆ `TOPIC_MENU_CONFIG["informs"]` |
| `tests/` / `docs/test-bible/**` | Betty — note AST-1365 left `test_topic_menu_informs_exclude_ideal_day_until_sibling` asserting exclusion until this sibling |

## Stages

### Stage 0: Prerequisite gate (build-time, no commit)

**Done when:** After `sync-child.sh` for this publish ref, `ideal_day` is in `CANDIDATE_LIBRARY_CONFIG["context_keys"]` and still **absent** from `TOPIC_MENU_CONFIG["informs"]` (this ticket’s work).

1. Run sync-child as usual for this ticket.
2. Confirm library home from AST-1365 and that informs catalog is still pre-change:

```bash
python3 -c "
from src.utils.config import CANDIDATE_LIBRARY_CONFIG, TOPIC_MENU_CONFIG
assert 'ideal_day' in CANDIDATE_LIBRARY_CONFIG['context_keys']
assert 'ideal_day' not in TOPIC_MENU_CONFIG['informs']
"
```

3. If the library assert fails (AST-1365 not yet on `origin/dev` / `origin/ftr/AST-1360` ancestry): **stop**. Comment on **parent AST-1360** with the Stage-blocked format naming this ticket and the missing library key — do **not** add `ideal_day` to `CANDIDATE_LIBRARY_CONFIG` here, and do **not** merge sibling `sub/AST-1360/AST-1365-*` by hand.
4. If `ideal_day` is **already** in `TOPIC_MENU_CONFIG["informs"]` before Stage 1: **stop** and comment on this ticket — do not double-apply.

### Stage 1: Topic Menu informs + Estelle packet/patch allowlists (config)

**Done when:** `TOPIC_MENU_CONFIG["informs"]` includes `ideal_day` after `backstory`; load-time equality assert matches; context-informs home loop includes `ideal_day`; `TOPIC_MENU_GEN_CONFIG` packet and patch tuples include `ideal_day` after `deal_breakers`; `import src.utils.config` succeeds; `validate_topic` accepts a topic with `informs: ["ideal_day"]`; preamble packet snapshot / patch whitelist include the key without editing `intake.py`.

1. In `src/utils/config.py`, inside `TOPIC_MENU_CONFIG`, extend `"informs"` — append **`"ideal_day"` immediately after `"backstory"`**:

```python
"informs": (
    "rubrics",
    "base_resume",
    "strengths",
    "priorities",
    "deal_breakers",
    "backstory",
    "ideal_day",
),
```

2. Update the equality assert that locks the catalog to the same seven-string tuple (including `"ideal_day"` after `"backstory"`).

3. Update the library-home loop immediately below so it also asserts `ideal_day` ⊆ `CANDIDATE_LIBRARY_CONFIG["context_keys"]`:

```python
for _ctx in ("strengths", "priorities", "deal_breakers", "backstory", "ideal_day"):
    assert _ctx in CANDIDATE_LIBRARY_CONFIG["context_keys"], _ctx
```

   Keep the existing `assert "base_resume" in TOPIC_MENU_CONFIG["informs"]` line unchanged.

4. In `TOPIC_MENU_GEN_CONFIG["packet_context_keys"]`, insert **`"ideal_day"` immediately after `"deal_breakers"`** (before `"hopes"`):

```python
"packet_context_keys": (
    "raw_resume",
    "raw_profile",
    "raw_sample",
    "bio_summary",
    "backstory",
    "strengths",
    "priorities",
    "deal_breakers",
    "ideal_day",
    "hopes",
    "interests",
    "concerns",
),
```

5. In `TOPIC_MENU_GEN_CONFIG["patchable_context_keys"]`, insert **`"ideal_day"` in the same place** (immediately after `"deal_breakers"`, before `"hopes"`) so confirm revise and packet visibility stay aligned.

   ⚠️ **Decision:** Placement after `deal_breakers` mirrors AST-1365’s library insertion among gated prose peers and keeps packet/patch tuples identical in relative order. Do not add Ideal Day to `packet_contact_keys` or `packet_name_columns`. Do not invent a separate Ideal Day informs key (`ideal_day_rubric`, etc.) — parent closed catalog uses the library key string.

6. Do **not** edit `src/core/intake.py` or `src/core/candidate.py` — `build_preamble_packet_snapshot`, `_apply_library_patches`, generate’s `INFORMS_CATALOG`, and `validate_topic` already read these config tuples.

7. Do **not** change `TASK_CONFIG` response schemas for `topic_menu_preamble_confirm` / `topic_menu_generate`.

### Stage 2: Estelle seed prompt vocabulary (agent_task)

**Done when:** `topic_menu_preamble_confirm.cache_prompt` lists `ideal_day` among allowed `library_patches` context keys; `topic_menu_generate.cache_prompt` lists `ideal_day` among allowed informs targets; no other `agent_task.json` rows change; JSON still loads.

1. In `data/admin/agent_task.json`, find the object with `"task_key": "topic_menu_preamble_confirm"`.
2. In that row’s `cache_prompt`, extend the ONLY-these-keys clause so `ideal_day` sits with the other gated context keys — insert **`ideal_day` immediately after `deal_breakers`** in the comma-separated list:

   Current fragment ends: `… strengths, priorities, deal_breakers, hopes, interests, concerns.`  
   Replace with: `… strengths, priorities, deal_breakers, ideal_day, hopes, interests, concerns.`

3. Find the object with `"task_key": "topic_menu_generate"`.
4. In that row’s `cache_prompt`, extend the informs line:

   Current: `informs — non-empty list drawn ONLY from: rubrics, base_resume, strengths, priorities, deal_breakers, backstory`  
   Replace with: `informs — non-empty list drawn ONLY from: rubrics, base_resume, strengths, priorities, deal_breakers, backstory, ideal_day`

   ⚠️ **Decision:** Keep the explicit list in the generate prompt (AST-1075 pattern) and add `ideal_day` rather than rewriting the prompt to “ONLY from INFORMS_CATALOG” in this ticket. Runtime still injects `INFORMS_CATALOG` from config; the seed line must not contradict the catalog. Do **not** edit `craft_*` rows (AST-1368).

5. Bump only the edited rows’ `updated_at` to current UTC `YYYY-MM-DD HH:MM:SS` if the file’s existing convention updates that field on prompt edits; do not rotate `task_key_uuid`. Prefer a surgical edit so other rows stay byte-identical aside from unavoidable JSON serializer normalization of the touched objects.

6. Do **not** change `system_prompt` / `user_prompt` / unused cache slots on these rows.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1367
**Overall:** APPROVED
**Publish ref:** `sub/AST-1360/AST-1367-topic-menu-informs-estelle-allowlists` @ `8d0ac348894c317106e7c355bb6f626afe81174f`

## Traceability
AC5→Stage 0 (AST-1365 library gate) + Stage 1 (`TOPIC_MENU_CONFIG["informs"]`, `packet_context_keys`, `patchable_context_keys`) + Stage 2 (`topic_menu_preamble_confirm` / `topic_menu_generate` `cache_prompt` vocabulary aligned with config); runtime `validate_topic`, `build_preamble_packet_snapshot`, `_apply_library_patches`, and `INFORMS_CATALOG` injection unchanged — already config-driven.

### Findings

**acceptable** — Stage 0 correctly blocks build if `ideal_day` ∉ `context_keys` or is pre-present in `informs`; defers library work to AST-1365 only.

**acceptable** — `test_topic_menu_informs_exclude_ideal_day_until_sibling` on ftr (AST-1365) must flip at `test-child`; plan delegates to Betty — not a plan defect.

**acceptable** — `agent_task.json` surgical edit + optional `updated_at` bump matches `astral.seed.agent-tables-in-repo-json` / AST-1075 explicit-list pattern; no `TASK_CONFIG` or core intake edits needed.

**acceptable** — Linear assignee Katherine (not Joan); Chuckles spawn — no plan impact.

context_tokens≈52000

---

[plan-rubric] PROCEED (Commit: 8d0ac348894c317106e7c355bb6f626afe81174f) informs allowlists seed

## Review (build stub)

**Built:** `astral-AST-1360` @ `8d9db131` on `origin/sub/AST-1360/AST-1367-topic-menu-informs-estelle-allowlists`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `8d0ac348` | Plan doc |
| 1 | `5c41750e` | `ideal_day` in `TOPIC_MENU_CONFIG["informs"]` + GEN packet/patch allowlists |
| 2 | `8d9db131` | Estelle confirm/generate `cache_prompt` vocabulary includes `ideal_day` |

**Verify:** `python3 -m py_compile` on `src/utils/config.py` — pass; import asserts + `validate_topic(..., informs=["ideal_day"])` — pass.

**Note for Betty:** AST-1365 left `test_topic_menu_informs_exclude_ideal_day_until_sibling` asserting Ideal Day is *absent* from informs — that assertion must flip (or the test retire) now that this sibling landed; no test-tree edits in this build.

## Radia review

# Radia review — AST-1367

**Ticket:** AST-1367  
**Parent:** AST-1360  
**Publish ref:** `origin/sub/AST-1360/AST-1367-topic-menu-informs-estelle-allowlists` @ `cc543da36fe465f1a3a142e586dcdaaccfe6d168`  
**Diff baseline:** `origin/dev...origin/sub/AST-1360/AST-1367-topic-menu-informs-estelle-allowlists` (17 files, +1199/−14)  
**Status gate:** Tests Passed (spawn prompt; trusted)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1367  
**Publish ref:** `cc543da36fe465f1a3a142e586dcdaaccfe6d168`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent grading changes |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` routing |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no rubric vectors |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch ids |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no agent-response persistence |
| `astral.config.config-source-of-truth` | scoped | conforms | informs + GEN allowlists live in `config.py`; runtime reads config |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run-next edits |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | plan doc present |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty merge is test-tree only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | `code(AST-1367)` touches `src/utils/config.py` + seed JSON only |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no external layer |
| `astral.layers.import-direction` | scoped | conforms | utils-only product edits in 1367 commits |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no UI hardcoding; catalog config-driven |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult render |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API/auth |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | surgical two-row `agent_task.json` edit + `updated_at` bump |
| `astral.seed.archie-catalog-wins` | scoped | conforms | seed vocabulary aligned with config catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no hot-path seed logic |
| `astral.seed.define-approved` | scoped | not-applicable | no DEFINE seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no `src/data/` in 1367 commits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no schema |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug logging |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | minimal tuple/assert extensions |
| `astral.standards.in-scope-only` | scoped | conforms | no `intake.py` / `candidate.py` / craft / NAV edits in 1367 commits |
| `astral.standards.logging-via-utils` | scoped | conforms | no new logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | domain key `ideal_day` in catalog |
| `astral.standards.no-cross-contamination` | scoped | conforms | AST-1368 craft rows untouched; only Estelle topic-menu rows in seed |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | closed catalog remains config-owned with equality assert |
| `astral.standards.public-then-helpers` | scoped | not-applicable | no new helpers |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils→data imports |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run loop |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no frontend in 1367 commits |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | tip is `merge-tests(AST-1367)` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `sync` / `docs` / `test` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub + sync prerequisite |
| `orch.git.ftr-sub-topology` | universal | conforms | child `sub/AST-1360/...` |
| `orch.git.merge-on-checkout` | universal | conforms | `sync(publish-ref)` for Stage 0 ancestry |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear stack |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/...` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1360 epic |
| `orch.git.three-permanent-branches` | universal | conforms | diff vs `origin/dev` |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | stages 1–2 match plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via Betty merge |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | n/a |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path commits |

**Active set count:** 64 rows (per `canon/statutes/README.md` harvested table). No `violates` or `needs-discussion` rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Plan cites AST-1075 explicit-list pattern in prose only; no `canon/patterns/**` id |

## Plan adherence

**AST-1367 product commits (`5c41750e` + `8d9db131`):**

**Stage 1 (config):**
- `ideal_day` appended after `backstory` in `TOPIC_MENU_CONFIG["informs"]` ✓
- Equality assert updated to seven-string tuple ✓
- Library-home loop extended to include `ideal_day` ✓
- `ideal_day` inserted after `deal_breakers` in both `packet_context_keys` and `patchable_context_keys` ✓
- No `intake.py` / `candidate.py` edits in engineer commits ✓

**Stage 2 (seed):**
- `topic_menu_preamble_confirm.cache_prompt`: `ideal_day` after `deal_breakers` in patch allowlist ✓
- `topic_menu_generate.cache_prompt`: `ideal_day` appended to informs vocabulary line ✓
- Only those two rows contain `ideal_day` in `agent_task.json` on tip ✓
- `updated_at` bumped on edited rows only ✓
- No `craft_*` / joblist / GET / meteorite prompt edits ✓

**Stage 0:** `sync(publish-ref): origin/sub/AST-1360/AST-1366-…` brought AST-1365 library/token ancestry (`ideal_day` ∈ `context_keys`, absent from `informs` pre–Stage 1) — matches plan gate.

**Estimate (2):** Footprint matches — config tuple/assert edits + two seed prompt strings.

**Test manifest (Betty):** `TestAst1367IdealDayTopicMenuInforms`, revised `TestAst1074TopicMenuConfig`, `TestAst1075TopicMenuCatalogRows` (ideal_day in generate cache + confirm patch list), `test_validate_topic_accepts_ideal_day_inform`; obsolete `test_topic_menu_informs_exclude_ideal_day_until_sibling` removed on tip. Bible entry in `docs/test-bible/utils/config.md` aligned.

**Cross-ticket boundaries:** No AST-1368 craft edits; no AST-1366 NAV edits in 1367 commits. AST-1365 library/token changes appear in full diff vs `origin/dev` as prerequisite rollup, not 1367 scope creep.

**Joan straggler (C4):** Plan-rubric APPROVED attached; no Excluded-statute list.

## Findings

### fix-now

*(none)*

### discuss

*(none)*

### advisory

- **Sibling test/product skew on branch tip:** `merge-tests` ancestry includes `TestAst1366IdealDayCandidateNav` and `TestAst1368IdealDayCraftDoCachePrompt`, but this publish ref’s product tree lacks AST-1366 NAV and AST-1368 `craft_do_rubric` seed changes. Betty’s narrowed AST-1367 manifest is green; a broad `test_repo_admin_json` / branch-lock run may fail until siblings land on `ftr`. Expected parallel-child pattern — not an AST-1367 implementation defect.
- **Config vs seed alignment:** Runtime `INFORMS_CATALOG` injection and seed explicit lists both include `ideal_day` — good. Operators editing seed prompts later must keep confirm patch list and generate informs line in sync with `TOPIC_MENU_CONFIG["informs"]` (existing AST-1075 discipline).

## What’s solid

- Closed-catalog extension done config-first; load-time asserts prevent drift.
- Seed vocabulary mirrors config placement (`ideal_day` after `deal_breakers` in patch list; after `backstory` in informs catalog).
- No duplicate Ideal Day rows across craft tasks — correct boundary with AST-1368.
- Betty flipped the AST-1365 exclusion test and added `validate_topic` coverage for the new inform target.

## Frame diff

**AST-1367 frame:** Topic Menu informs + Estelle allowlists — **matches**.

**Rollup note:** Full three-dot diff vs `origin/dev` also carries AST-1365 library/gate stack (and docs/tests from siblings via `sync` + `merge-tests`); required for token resolution, not 1367 scope inflation.

## Notes

- §5f / §5g not triggered.
- `agent_task.json` diff vs `origin/dev` is surgical (two Estelle topic-menu rows only).
- C7 artifact complete.

context_tokens≈45000

---

```
[code-rubric] PROCEED (Commit: cc543da3) Topic Menu informs allowlists
```

## Resolution

**Date:** 2026-08-14  
**Radia:** CLEAN / PROCEED (`8bf4e974`) — no fix-now items.

**§9a:** `origin/dev` dry-run clean. `origin/ftr/AST-1360-ideal-day-candidate-context` initially conflicted on `data/admin/agent_task.json` + `src/utils/config.py` (sibling Ideal Day craft/UI already on ftr). Merged `origin/ftr/AST-1360-ideal-day-candidate-context` into this publish ref; ort auto-resolved keeping Ideal Day informs/GEN allowlists/Estelle seeds **and** sibling craft/nav changes. Re-ran §9a — both `origin/dev` and parent ftr clean.
