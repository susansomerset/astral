<!-- linear-archive: AST-1368 archived 2026-08-31 -->

## Linear archive (AST-1368)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1368/wire-ideal-day-into-jd-do-like-craft-prompts-add-ideal-day-to-the-set  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1360 — Add "ideal_day" to the set of candidate context (strengths, priorities, etc.)  
**Blocked by / blocks / related:** parent: AST-1360

### Description

## What this implements

Update Job Description, DO, and LIKE craft rubric agent_task prompts (and any shared cache/context blocks those three use) so Ideal Day is included with the other candidate context tokens.

## Citations

`astral.seed.archie-catalog-wins`; `astral.seed.agent-tables-in-repo-json`; `astral.standards.in-scope-only`.

## Acceptance criteria

- [X] 4. Craft tasks for Job Description, DO, and LIKE rubrics include Ideal Day in their candidate-context prompt material (same class of inclusion as Strengths/Priorities today).

## Boundaries

- [X] Does **not** touch GET/joblist/meteorite craft prompts. After Ideal Day library + token.

## Notes for planning

Parent AST-1360. Estimate: 2. After #1.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1360-ideal-day-candidate-context`,
child `sub/AST-1360/<child-segment>`. Created at dispatch-parent.

## QA test manifest

1. Craft DO Ideal Day + LIKE/JD caller-cache + out-of-scope omit: `tests/component/core/test_repo_admin_json.py::TestAst1368IdealDayCraftDoCachePrompt`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1368IdealDayCraftDoCachePrompt \
  -q
```

**Bible shasums** (`origin/sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts`):

* `docs/test-bible/core/repo_admin_json.md` `bde6139d8cb0785a48874d69354942a8ba2791ae`

### Comments

#### radia — 2026-08-14T19:06:14.064Z
[code-rubric] PROCEED (Commit: 90d0e59e) DO cache Ideal Day token

#### betty — 2026-08-14T19:03:32.932Z
`origin/sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts` @ `90d0e59e` · Ideal Day craft tests

#### ada — 2026-08-14T18:59:11.996Z
🛑 Stage 0 blocked: IDEAL_DAY token not on HEAD after sync-child (`5034b1f9`). Commented on parent AST-1360. Waiting for AST-1365 on ftr/dev — will not hand-merge sibling sub.

#### joan — 2026-08-14T18:58:11.553Z
[plan-rubric] PROCEED (Commit: 482e445504320fa4296ce1cf2cd7f1e3e7578a90) DO cache caller-chain

#### ada — 2026-08-14T18:56:15.822Z
[check-linear] blocked: non-fast-forward on publish ref

`git push origin HEAD:sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts` rejected (non-fast-forward).

Cause: epic worktree was on `sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface` when the plan commit landed; contaminated tip `bb728bef` was pushed to AST-1368’s publish ref (includes AST-1365 product/tests + AST-1366 plan).

Clean plan-only tip (parent `38cb7ba8` + plan doc only): `482e445504320fa4296ce1cf2cd7f1e3e7578a90`

Need Chuckles force-push (or equivalent) of that clean SHA onto `origin/sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts`. Ada will not force-push.

Local: on clean `sub/AST-1360/AST-1368-…` @ `482e4455`. AST-1366 local reset to `origin/…/AST-1366-…` @ `329b52c9`.

#### ada — 2026-08-14T18:55:38.438Z
`origin/sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts` @ `bb728beffd8d575a6967a8c69245cbf5b7224b99` · Ideal Day craft plan

---

# AST-1368 — Wire Ideal Day into JD / DO / LIKE craft prompts

**Linear:** [AST-1368](https://linear.app/astralcareermatch/issue/AST-1368/wire-ideal-day-into-jd-do-like-craft-prompts-add-ideal-day-to-the-set)
**Parent:** [AST-1360](https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc) — Add `ideal_day` to the set of candidate context (strengths, priorities, etc.)
**Publish ref:** `sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts`
**Depends on:** [AST-1365](https://linear.app/astralcareermatch/issue/AST-1365/ideal-day-library-token-add-ideal-day-to-the-set-of-candidate-context) — `TOKEN_SOURCES["IDEAL_DAY"]` → `context.ideal_day` (must be on HEAD after `sync-child.sh` before build)

Put Ideal Day into the same candidate-context prompt material that already carries Strengths / Priorities / Deal Breakers / Backstory for the Job Description, DO, and LIKE craft rubric hops. On tip, that material is the **`craft_do_rubric.cache_prompt`** block; LIKE and Job Description reuse it via `{$CALLER_CACHE_A}` through the live craft chain. Edit the seed catalog only — no Python, no UI, no GET / joblist / meteorite craft rows.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | On the `craft_do_rubric` row only: extend `cache_prompt` with an Ideal Day section + `{$IDEAL_DAY}` (peer of Strengths/Priorities/Deal Breakers/Back Story) | data (seed) |

**Out of scope (do not touch):**

| File / area | Why |
|-------------|-----|
| `craft_joblist_rubric` (even though its `cache_prompt` currently equals DO’s) | Parent / ticket boundaries: no joblist craft prompts |
| `craft_get_rubric`, `craft_evaluate_meteorite_rubric` | Boundaries: no GET / meteorite craft prompts |
| `craft_like_rubric` / `craft_jobdesc_rubric` prompt fields | They already set `cache_prompt` to `{$CALLER_CACHE_A}` (plus boundary `cache_prompt_b`); Ideal Day rides the caller cache once DO’s CACHE_A includes it |
| `grade_*` / consult prompts, `craft_resume_base` | Not JD/DO/LIKE craft |
| `src/utils/config.py` `TOKEN_SOURCES` / library keys | AST-1365 |
| Candidate Ideal Day UI / Topic Menu informs | AST-1366 / AST-1367 |
| `tests/` / bible | Betty |

## As-is (candidate-context inclusion today)

Live chain (from `run_next` on tip):

`craft_get_rubric` → `craft_do_rubric` → `craft_like_rubric` → `craft_evaluate_meteorite_rubric` → `craft_jobdesc_rubric` → `craft_joblist_rubric` → …

| Task | How Strengths/Priorities enter the hop |
|------|----------------------------------------|
| `craft_do_rubric` | Own `cache_prompt` lists BIO SUMMARY, STRENGTHS, PRIORITIES, DEAL BREAKERS, BACK STORY, BASE RESUME, LINKEDIN PROFILE TEXT with `{$…}` tokens |
| `craft_like_rubric` | `cache_prompt` = `{$CALLER_CACHE_A}` (resolved DO CACHE_A text) |
| `craft_jobdesc_rubric` | `cache_prompt` = `{$CALLER_CACHE_A}` (same chain; meteorite hop also forwards `{$CALLER_CACHE_A}`) |

⚠️ **Decision:** One seed edit on `craft_do_rubric.cache_prompt` is the correct inclusion class for all three named craft tasks. Duplicating Ideal Day into LIKE/JD rows would fight the caller-cache pattern; touching `craft_joblist_rubric` would violate in-scope-only.

## Stages

### Stage 0: Prerequisite gate (build-time, no commit)

**Done when:** After `sync-child.sh` for this publish ref, `TOKEN_SOURCES` contains `"IDEAL_DAY"` with `path` `context.ideal_day`.

1. Run sync-child as usual for this ticket.
2. Confirm Ideal Day token from AST-1365:

```bash
python3 -c "from src.utils.config import TOKEN_SOURCES; assert TOKEN_SOURCES['IDEAL_DAY']['path']=='context.ideal_day'"
```

3. If the assert fails (AST-1365 not yet on `origin/dev` / `origin/ftr/AST-1360` ancestry): **stop**. Comment on **parent AST-1360** with the Stage-blocked format naming this ticket and the missing token — do **not** add `IDEAL_DAY` to config here, and do **not** merge sibling `sub/AST-1360/AST-1365-*` by hand.

### Stage 1: Seed Ideal Day into DO candidate-context cache

**Done when:** `craft_do_rubric.cache_prompt` includes an Ideal Day section with `{$IDEAL_DAY}` immediately after the Back Story section and before Base Resume; no other `agent_task.json` rows change; JSON still loads; `craft_like_rubric` / `craft_jobdesc_rubric` / `craft_joblist_rubric` / GET / meteorite rows are byte-identical to pre-change (except unavoidable serializer normalization of the single edited string’s row if the dump touches only that object — prefer surgical edit so other rows are untouched).

1. In `data/admin/agent_task.json`, find the object with `"task_key": "craft_do_rubric"`.

2. Replace that row’s `cache_prompt` so the gated prose cluster gains Ideal Day **after Back Story, before Base Resume**. Exact target text (newlines and blank-line spacing must match the existing `\n\n\n` rhythm between sections):

```
{$FIRST_NAME}'s BIO SUMMARY:
{$BIO_SUMMARY}


{$FIRST_NAME}'s STRENGTHS:
{$STRENGTHS}


{$FIRST_NAME}'s PRIORITIES:
{$PRIORITIES}


{$FIRST_NAME}'s DEAL BREAKERS:
{$DEAL_BREAKERS}


{$FIRST_NAME}'s BACK STORY:
{$BACKSTORY}


{$FIRST_NAME}'s IDEAL DAY:
{$IDEAL_DAY}


{$FIRST_NAME}'s BASE RESUME:
{$BASE_RESUME}


{$FIRST_NAME}'s LINKEDIN PROFILE TEXT:
{$LINKEDIN_PROFILE_TEXT}
```

   Label style matches existing peers (`BACK STORY`, `DEAL BREAKERS` → `IDEAL DAY`). Token is exactly `{$IDEAL_DAY}` (AST-1365 registry).

3. **Edit discipline** (`astral.seed.agent-tables-in-repo-json` / prior AST-1252 noise lesson):
   - Change **only** `craft_do_rubric` → `cache_prompt`.
   - Do **not** rewrite the whole file through `json.dump` with `ensure_ascii=True` (that re-escapes unrelated prompts). Prefer a surgical string replace of the current DO `cache_prompt` value, or load/dump with `ensure_ascii=False` and identical 2-space indent **only if** a dry-run diff shows **no** unrelated row churn — if dry-run shows mass `\u2014` / punctuation churn, abort that approach and use surgical replace instead.
   - Do **not** change `run_next`, agent ids, other prompt fields, or `updated_at` unless the existing file tooling already requires a touch on that row (default: leave `updated_at` alone).

4. Do **not** edit `craft_like_rubric` or `craft_jobdesc_rubric` user_prompt instructional prose that mentions “strengths” / “priorities” in English. AC is candidate-context **material** (token block / caller cache), same class as today’s Strengths/Priorities inclusion — not a catalog rewrite of stage coaching copy.

5. Do **not** edit `craft_joblist_rubric.cache_prompt` even though it currently duplicates DO’s block.

6. Verify after edit:

```bash
python3 - <<'PY'
import json
from pathlib import Path
rows = json.loads(Path("data/admin/agent_task.json").read_text())
by = {r["task_key"]: r for r in rows}
cp = by["craft_do_rubric"]["cache_prompt"]
assert "{$IDEAL_DAY}" in cp
assert "IDEAL DAY" in cp
# Still after back story, before base resume
assert cp.index("{$BACKSTORY}") < cp.index("{$IDEAL_DAY}") < cp.index("{$BASE_RESUME}")
# Out-of-scope rows must not gain Ideal Day from this ticket
for k in ("craft_joblist_rubric", "craft_get_rubric", "craft_evaluate_meteorite_rubric"):
    blob = " ".join(str(by[k].get(f) or "") for f in (
        "cache_prompt", "cache_prompt_b", "cache_prompt_c", "cache_prompt_d",
        "nocache_prompt", "user_prompt", "system_prompt",
    ))
    assert "{$IDEAL_DAY}" not in blob, k
# LIKE + JD still forward caller cache A
assert "{$CALLER_CACHE_A}" in (by["craft_like_rubric"]["cache_prompt"] or "")
assert "{$CALLER_CACHE_A}" in (by["craft_jobdesc_rubric"]["cache_prompt"] or "")
print("ok")
PY
```

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

**Rubric:** plan-rubric
**Ticket:** AST-1368
**Overall:** APPROVED
**Publish ref:** `sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts` @ `482e445504320fa4296ce1cf2cd7f1e3e7578a90`

### Traceability
AC4→Stage 1 (`craft_do_rubric.cache_prompt` gains `{$IDEAL_DAY}` peer section; LIKE + Job Description inherit via existing `{$CALLER_CACHE_A}` chain — verified in plan Stage 1 §6); Stage 0 gates `TOKEN_SOURCES["IDEAL_DAY"]` from AST-1365.

### Findings

**acceptable** — Prior contaminated publish tip (`bb728bef`, sibling product + wrong plan) is documented on-ticket; `origin/sub/…/AST-1368-…` tip is now plan-only `482e4455`. Chuckles should keep publish ref on that clean SHA before build.

**acceptable** — `craft_joblist_rubric.cache_prompt` will diverge from DO (still no `{$IDEAL_DAY}`) while DO gains it; parent in-scope-only excludes joblist — plan’s explicit non-touch is correct.

**acceptable** — Meteorite hop prompt rows unchanged; enriched candidate-context text may flow through `{$CALLER_CACHE_A}` as today for Strengths/Priorities — not a meteorite prompt edit.

**acceptable** — Linear assignee Joan Clarke (validator identity collision only); no plan impact.

context_tokens≈52000

## Review (build stub)

**Built:** `astral-AST-1360` @ `d261670c` on `origin/sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `482e4455` | Plan doc |
| sync | `7828ca89` | Merge `origin/ftr/AST-1360-ideal-day-candidate-context` (IDEAL_DAY token) |
| 1 | `d261670c` | `craft_do_rubric.cache_prompt` + Ideal Day / `{$IDEAL_DAY}` |

**Verify:** plan Stage 1 §6 asserts — pass; surgical one-line `agent_task.json` diff (no mass re-serialize).

**Note for Betty:** seed catalog only; LIKE/JD inherit Ideal Day via `{$CALLER_CACHE_A}`; joblist/GET/meteorite rows intentionally unchanged.

## Radia review

# Radia review — AST-1368

**Ticket:** AST-1368  
**Parent:** AST-1360  
**Publish ref:** `origin/sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts` @ `90d0e59e9bcf98a8e949ce6a122585e751af4ce1`  
**Diff baseline:** `origin/dev...origin/sub/AST-1360/AST-1368-wire-ideal-day-jd-do-like-craft-prompts` (12 files, +744/−9)  
**Status gate:** Tests Passed (spawn prompt; trusted)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1368  
**Publish ref:** `90d0e59e9bcf98a8e949ce6a122585e751af4ce1`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent grading payload changes |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` routing changes |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no rubric vector changes |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no agent-response persistence |
| `astral.config.config-source-of-truth` | scoped | conforms | `{$IDEAL_DAY}` uses AST-1365 registry; 1368 does not add config in its code commit |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | caller-cache chain preserved; single DO edit |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | `ast-1368-wire-ideal-day-jd-do-like-craft-prompts.md` present |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty merge is test-tree only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | `code(AST-1368)` touches seed JSON only; tests via `merge-tests` |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no external layer |
| `astral.layers.import-direction` | scoped | conforms | no new layer bends in 1368 commit |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | no UI |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult render |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API/auth |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | surgical `craft_do_rubric.cache_prompt` edit; no mass re-serialize |
| `astral.seed.archie-catalog-wins` | scoped | conforms | seed catalog is the change surface |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no hot-path seed logic |
| `astral.seed.define-approved` | scoped | not-applicable | no DEFINE seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no `src/data/` changes in 1368 commit |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no schema |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug logging |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | minimal one-field seed edit |
| `astral.standards.in-scope-only` | scoped | conforms | only `craft_do_rubric`; joblist/GET/meteorite/LIKE/JD rows untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | no new logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | domain token `{$IDEAL_DAY}`; ticket refs in docs/tests only |
| `astral.standards.no-cross-contamination` | scoped | conforms | no config/UI/Topic Menu smuggling in 1368 code commit |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | uses registered token, not inline prose |
| `astral.standards.public-then-helpers` | scoped | not-applicable | no Python in 1368 commit |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils→data imports |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run loop |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no frontend |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | tip is `merge-tests(AST-1368)` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `sync` / `docs` / `test` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub + ftr sync prerequisite |
| `orch.git.ftr-sub-topology` | universal | conforms | child `sub/AST-1360/...` |
| `orch.git.merge-on-checkout` | universal | conforms | `sync(ftr)` for Stage 0 gate |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear stack |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/...` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1360 epic |
| `orch.git.three-permanent-branches` | universal | conforms | diff vs `origin/dev` |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | seed-only implementation matches plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | `TestAst1368IdealDayCraftDoCachePrompt` + bible via Betty |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | n/a |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path product commits |

**Active set count:** 64 rows (per `canon/statutes/README.md` harvested table). No `violates` or `needs-discussion` rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Plan cites caller-cache chain pattern in prose only; no `canon/patterns/**` id |

## Plan adherence

**AST-1368 product commit (`d261670c`):** single surgical line on `craft_do_rubric.cache_prompt` — adds `{$FIRST_NAME}'s IDEAL DAY:\n{$IDEAL_DAY}\n\n\n` after `{$BACKSTORY}` and before `{$BASE_RESUME}`. Verified on tip: `task_key` is `craft_do_rubric`; token order `BACKSTORY < IDEAL_DAY < BASE_RESUME`; label style matches peers (`IDEAL DAY`).

**Stage 0 prerequisite:** `sync(ftr): origin/ftr/AST-1360-ideal-day-candidate-context` brings `TOKEN_SOURCES["IDEAL_DAY"]` → `context.ideal_day` before seed edit — matches plan gate; 1368 does not add config in its own code commit.

**Inheritance / boundaries (plan §6):**
- `craft_like_rubric` / `craft_jobdesc_rubric`: still `{$CALLER_CACHE_A}` only — LIKE + JD inherit at runtime ✓
- `craft_joblist_rubric`, `craft_get_rubric`, `craft_evaluate_meteorite_rubric`: no `{$IDEAL_DAY}` literal in prompt fields ✓
- `craft_joblist_rubric` retains legacy BACKSTORY block without Ideal Day — intentional per plan/Joan (joblist out of scope) ✓

**Edit discipline:** `agent_task.json` diff is one-line substitution; no mass `\u2014` churn or unrelated row changes.

**Estimate (2):** Footprint matches — one seed field + prerequisite sync + Betty tests.

**Full diff vs `origin/dev`:** Also includes AST-1365 stack (`config.py`, `candidate.py`, 1365 docs/tests) from ftr ancestry — expected rollup prerequisite, not 1368 scope creep. AST-1368’s stated Files Changed table is satisfied by its own commit.

**Test manifest:** Betty `TestAst1368IdealDayCraftDoCachePrompt` mirrors plan §6 asserts (token placement, CALLER_CACHE_A on LIKE/JD, out-of-scope omit). Bible entry in `docs/test-bible/core/repo_admin_json.md` aligned.

**Joan straggler (C4):** Plan-rubric APPROVED attached; no Excluded-statute list — nothing to straggle.

## Findings

### fix-now

*(none)*

### discuss

*(none)*

### advisory

- **Joblist divergence:** `craft_joblist_rubric.cache_prompt` still lists BACKSTORY (and peers) but not Ideal Day while DO now does — deliberate per parent in-scope-only. Joblist craft hops will not see Ideal Day until a future ticket touches that row. Susan may want to note for epic UAT if joblist rubric quality is compared to DO/LIKE/JD.
- **Meteorite chain:** `craft_evaluate_meteorite_rubric` forwards `{$CALLER_CACHE_A}`; resolved DO cache may now carry Ideal Day prose at runtime without a literal `{$IDEAL_DAY}` in meteorite rows. Joan flagged acceptable; same class as existing Strengths/Priorities flow-through.

## What’s solid

- Correct inclusion class: one DO `cache_prompt` edit propagates to LIKE + JD via existing caller-cache chain — no duplicate seed blocks.
- Surgical JSON edit honors `astral.seed.agent-tables-in-repo-json` / AST-1252 lesson.
- Stage 0 ftr sync cleanly gates token availability before seed references `{$IDEAL_DAY}`.
- Betty tests lock boundary rows and inheritance contract.

## Frame diff

**AST-1368 frame:** seed-only `craft_do_rubric.cache_prompt` extension — **matches**.

**Rollup note:** three-dot diff vs `origin/dev` also carries AST-1365 product + docs (prerequisite via `sync(ftr)`), not part of AST-1368’s planned Files Changed but required for token resolution on this branch tip.

## Notes

- §5f / §5g not triggered.
- Prior contaminated tip (`bb728bef`) superseded; clean build at `d261670c` per build stub.
- C7 artifact complete.

context_tokens≈42000

---

```
[code-rubric] PROCEED (Commit: 90d0e59e) DO cache Ideal Day token
```

