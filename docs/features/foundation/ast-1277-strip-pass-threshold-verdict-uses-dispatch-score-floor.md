<!-- linear-archive: AST-1277 archived 2026-08-19 -->

## Linear archive (AST-1277)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1277/strip-pass-threshold-verdict-uses-dispatch-score-floor-remove-pass  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1275 — Remove "pass_threshold" from task_config  
**Blocked by / blocks / related:** parent: AST-1275; blocks: AST-1279

### Description

## What this implements

Remove every `TASK_CONFIG` `pass_threshold` (including `prefilter_company`). Scored verdict path reads `score_floor` from the candidate’s dispatch task row, with `0` meaning no numeric soft-fail. Dealbreaker/error paths unchanged. Does not own admin dropdown or canon retirement.

## Acceptance criteria

- [X] No `TASK_CONFIG` entry defines `pass_threshold` (roster, meteorite aliases, and `prefilter_company` included).
- [X] A scored consult/prefilter run soft-fails or passes using the candidate dispatch task’s `score_floor`, including when that value is `0` (always-pass on numeric floor; dealbreaker/error still fail).

## Boundaries

Does not own admin Score Floor dropdown (sibling Katherine). Does not own statute retirement / pattern authoring / Code Rules rewrite (sibling Hedy).

## In scope

- [X] `pattern.config.config-block` — delete `pass_threshold` keys from `TASK_CONFIG`; no resurrected task-config threshold; `dispatch_row_task_key` for consult≠dispatch rename (prefilter)
- [X] `pattern.batch.entity-claim-process-release` — claim floor normalizer shared; claim/count still reads row `score_floor`; verdict lookup via tracker trigger filter (no parallel hop parser)
- [X] `pattern.state.entity-state-transitions` — pass/fail/error state names unchanged
- [X] `astral.config.config-source-of-truth` — soft-fail floor from dispatch row / config helper, not hardcoded in core
- [X] `astral.patterns.render-verdict-orchestrates-consult` — scored verdict applies dispatch `score_floor`
- [X] `pattern.dispatch.score-floor` (proposed / plain-language until AST-1279 lands) — sole numeric floor; `0` allowed
- [X] `astral.standards.no-hardcoded-sets` — no leftover magic `6.0` / `0.0` task-config threshold
- [X] `astral.standards.in-scope-only`
- [X] `astral.standards.dry-and-focused-functions`
- [X] `astral.docs.features-single-file-per-ticket`
- [X] `astral.git.engineer-test-tree-ban`

## Considered but excluded

- [X] `astral.config.pass-threshold-vs-score-floor` — retiring; owned by AST-1279 (do not rewrite Code Rules §2.1 here)
- [X] `astral.layers.ui-config-driven-business-logic` — admin Score Floor dropdown is AST-1278
- [X] `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` — no new cross-layer edges beyond existing consult→tracker/config
- Universal `orch.*` — not listed per-child

## Notes for planning

Sole numeric floor is `dispatch_task.score_floor`. Explicit `0` is valid. No resurrected task-config threshold.

## Git branch (authoritative)

Parent `ftr/AST-1275-remove-pass-threshold-from-task-config`; child `sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-08T02:04:40.077Z
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1277
**Publish ref:** `sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor` @ `0cdf1e97` (post `merge-resume(AST-1277)` sync of the advanced `ftr/AST-1275` tip — AST-1278 landed + resolved mid-review)
**Overall:** DISCUSS

## Plan adherence

- Both of Joan's round-1 fix-nows verified against the shipped diff, not just the plan text: `dispatch_row_task_key` correctly maps `prefilter_company` → dispatch row key `prefilter`; `_dispatch_score_floor_for_task` takes newest-first (`id DESC` via `tracker.list_dispatch_tasks_for_candidate`) with the documented single fallback.
- `rg pass_threshold src/` returns no matches — Stage 1/2 done-when criteria fully met, exactly the seven enumerated `TASK_CONFIG` keys stripped; binary qualify/evaluate `_render_score(..., 0.0)` call sites untouched per plan step 5.
- `roster.py`'s prefilter soft-fail sets `verdict_state = cfg["fail_state"]` *before* the decomposed/legacy `new_state` branching — verified by reading the full function, matches plan step 4 exactly.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | `pass_threshold` keys deleted in place; new helpers added beside sibling score-floor helpers — no re-invented catalog. |
| `pattern.batch.entity-claim-process-release` | conforms | Claim/process/release shape untouched; only the floor value computation inside the existing claim path swapped to the shared normalizer. |
| `pattern.state.entity-state-transitions` | conforms | Core (`roster.py`) still decides `verdict_state`/`new_state`; no daisy-chaining introduced. |
| `pattern.dispatch.score-floor` (proposed) | not-applicable | Not yet under `canon/patterns/**` (AST-1279 owns authoring). Plan conforms to the parent's plain-language rule instead of building against an unapproved id — correctly deferred. |

## Findings

**discuss (straggler, C4) — no reply needed, already resolved at plan/parent level.** `astral.config.pass-threshold-vs-score-floor` is still `status: active` and its text forbids feeding `dispatch_task.score_floor` into the verdict path — the plan's own "Considered but excluded" list named it (owned by AST-1279), so this sweep's C4 belt-and-suspenders check surfaces it as a straggler, and on the merits it does score `violates`, by design. Not a code defect: parent AST-1275 AC4/AC5 explicitly orders retirement of this statute in blocking sibling AST-1279, and Joan's `[plan-rubric] revision=1` **APPROVED** verdict reviewed this exact "law sequencing" interval and accepted it on parent authority. Flagged here only so the interval stays visible in both the plan bible and this review — nothing for Ada or this ticket to fix.

**advisory — three more excluded-list ids matched generically.** `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.layers.ui-config-driven-business-logic` all matched this diff's `src/core/**` / `src/utils/config.py` paths (C4 mechanics) but all score `conforms` — no new cross-layer edges, no UI logic added to `config.py`. Noted for C4 completeness only, no action.

## Frame diff

(none) — no scope drift; description checkboxes already match delivered behavior.

**What's solid:** Full active-set (64 `status: active` statutes) scored in-session — no fix-now anywhere. Shared `effective_dispatch_score_floor` used by both claim (`dispatcher.py`) and verdict (`consult.py`/`roster.py`) — one normalizer, no drift risk. Test-tree boundary held: `test(AST-1277)` + `merge-tests(AST-1277)` are the only commits touching `tests/`/`docs/test-bible/**`.

**Notes:** Diff recomputed after syncing `origin/ftr/AST-1275` mid-review (`merge-resume(AST-1277)`, no conflicts) — the `src/ui/api_admin.py` / `AdminScheduledActions.tsx` / frontend-test content now riding in this three-dot diff is AST-1278's already-reviewed-CLEAN work arriving via that merge, not new AST-1277 content.

context_tokens≈52000

— Radia

#### betty — 2026-08-08T01:55:47.314Z
## QA test manifest

**Publish:** `origin/sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor` @ `138b239f`
**merge-tests:** `merge-tests(AST-1277): origin/tests 5727659e1601f2faee2eb1dabde94e0794956e6d`

### 1. Existing coverage (bible-backed)

1. `tests/component/core/test_consult.py::TestRenderScore` — soft-fail math still positional on `_render_score(..., score_floor)`
2. `tests/component/core/test_dispatcher.py::TestRunUnified::test_uses_default_score_floor_for_scored_states` — claim NULL→1.0 via shared normalizer

### 2. Broken / obsolete (revised this pass)

1. `TestRenderVerdict` scored cases (4) — empty table rubric broke hydrate after scored path always resolves floor; fixtures now mock `_rubric_criteria_for_cfg` + dispatch row floor
2. `TestAst726…::test_apply_render_verdict_always_persists_notes_including_empty` — same fixture revision

### 3. Gaps (this pass)

1. `tests/component/utils/test_config.py::TestAst1277ScoreFloorHelpers` — no `pass_threshold` on seven TASK_CONFIG keys; `effective_dispatch_score_floor` NULL/`0`/`6`; `dispatch_row_task_key` prefilter + identity
2. `tests/component/core/test_consult.py::TestAst1277DispatchScoreFloorVerdict` — lookup NULL→1.0, prefilter→`prefilter` newest-first `0`; apply soft-fail under high floor; pass at floor `0`

**Integration:** none revised (no existing scenarios assert TASK_CONFIG `pass_threshold` / scored floor source).

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1277ScoreFloorHelpers \
  tests/component/core/test_consult.py::TestAst1277DispatchScoreFloorVerdict \
  tests/component/core/test_consult.py::TestRenderVerdict \
  tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes::test_apply_render_verdict_always_persists_notes_including_empty \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_uses_default_score_floor_for_scored_states \
  -q
```

### Bible shasums (`origin/<publish-ref>`)

- `docs/test-bible/core/consult.md` `ccb4932707219e2a3e5177455f773ad26004f9dd`
- `docs/test-bible/utils/config.md` `02bfe34248f1ebbfa81a8cc290bb08baa80a4e4a`

— Betty

#### joan — 2026-08-08T01:45:31.119Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1277
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor` @ `46b341f3` (round-1 rubric ran at `87f191ce`)
**Plan Discuss:** 1 completed round (concern + reply); no round 2 opened.

## Traceability

AC1→S1; AC2→S2 (parent AC1→S1; AC2→S2; parent AC3/AC4/AC5 N/A — boundary, AST-1278 / AST-1279). No orphan stages.

**Considered:** full active corpus re-scored in-session against the revised change set (unchanged layers `utils` + `core`; paths `src/utils/config.py`, `src/core/{consult,roster,dispatcher}.py`). No `violates` remain.

## Findings

**Both round-1 fix-now items are closed — verified against source, not just against the reply.**

*Prefilter dispatch key.* Stage 1 step 3 adds `dispatch_row_task_key` in `config.py` as the inverse of `dispatch_task_grouping_catalog_key`, mapping both `prefilter` and `ROSTER_CONFIG["prefilter"]["task_key"]` to the dispatch row key `prefilter`, identity for everything else. Checked: `ROSTER_CONFIG["prefilter"]["task_key"]` is `"prefilter_company"` (`config.py:1934`), defined well above the proposed insertion point next to `dispatch_task_grouping_catalog_key` (`config.py:2991`), so the reference resolves. Neither helper name already exists in `src/`. Identity for the meteorite aliases is right — `meteorite_grade_do` / `meteorite_grade_get` / `meteorite_like` are the same string on both the dispatch row and in `TASK_CONFIG`, and prefilter is the only consult≠dispatch pair the scored paths touch. Stage 2's Done-when now names the reachable `0` on the `prefilter` row explicitly, which is the AC2 half that was previously unreachable.

*Tie-break ordering.* Stage 2 step 1 now states newest-first (`id DESC`) with the correct reason — `tracker.list_dispatch_tasks_for_candidate` walks `database.list_dispatch_tasks()`, which is `ORDER BY id DESC` — and explicitly bars consult from calling `database.list_dispatch_tasks_for_candidate`. Trigger filtering is delegated to the tracker helper's keyword-only `trigger_state=` (which owns `parse_dispatch_hop_label`), with a single documented fallback to the unfiltered list. That also closes the round-1 DRY discuss: no parallel hop parser in consult, and `dispatch_row_task_key` is the one rename point. The keyword-only call shape matches the helper's real signature.

**acceptable — the three remaining round-1 discuss items are now written into the bible where a reviewer will find them.** *Post-land floor expectations* states plainly that roster `grade_do` / `grade_get` / `grade_like` soft-fail against `1.0` rather than today's `6.0` until Susan sets floors, that there is no backfill in this ticket, and what the Susan/UAT action is. *Law sequencing* records the accepted interval where the tree contradicts still-active `astral.config.pass-threshold-vs-score-floor` until AST-1279 lands. *Pattern citations* notes `pattern.dispatch.score-floor` is not yet under `canon/patterns/**` and that the parent's `astral.patterns.render-verdict-orchestrates-consult` citation is retired in favour of `astral.idioms.render-verdict-orchestrates-consult`. All three are non-blocking and none is this child's to resolve.

**acceptable — revision hygiene.** The revision is doc-only (`git diff --name-only 87f191ce..46b341f3` = the plan file alone), so nothing landed in `src/` during Plan Discuss. `## Revisions` records the driver and the changes. Conf dropped `high` → `Medium` with an honest reason, which now matches the plan's actual complexity; Scope `Single-Component` and Risk `Medium` still read true.

**note — carried forward for build, not blocking.** The trigger preference passes the job's pre-transition state, which is the dispatch trigger for the `grade_*` hops; if a runtime hop label ever reaches it, the tracker filter yields nothing and the documented fallback takes the newest row for that `task_key`. That degradation is intentional and written down — worth a glance at test time rather than a plan change.

— Joan

context_tokens≈96000

#### ada — 2026-08-08T01:43:28.500Z
[plan-discuss] round=1 reply

Plan revised on `origin/sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor` @ `46b341f3`.

[Plan doc](https://github.com/susansomerset/astral/blob/sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor/docs/features/foundation/ast-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor.md)

**fix-now — prefilter key:** Added `dispatch_row_task_key` (maps `prefilter_company` / `prefilter` → dispatch row key `prefilter`; identity otherwise). Stage 2 / roster call still passes the consult key; lookup never queries migrated-away `prefilter_company` rows.

**fix-now — tie-break order:** Lookup uses `tracker.list_dispatch_tasks_for_candidate(..., trigger_state=)` (compound hop labels included). Multi-row tie-break is **newest first** (`id DESC` via tracker’s walk of `list_dispatch_tasks`) — dropped the false `id ASC` claim; consult does not call `database.list_dispatch_tasks_for_candidate`.

**discuss — NULL→1.0 verdict:** Documented under **Post-land floor expectations** — same normalizer as claim; roster GDL with NULL floors soft-fail at `1.0` (not historical `6.0`) until Susan sets floors; no backfill in this ticket; meteorite seeds already `0.0`.

**discuss — active law interval:** Plan now states parent-ordered contradiction of still-active `astral.config.pass-threshold-vs-score-floor` until AST-1279 lands; this child does not rewrite Code Rules.

**discuss — DRY trigger match / patterns:** Trigger filtering delegated to tracker helper; pattern citation note (plain-language until AST-1279; retired vs live render-verdict idiom id) added.

**Self-assessment:** Conf → `Medium` (prefilter key miss was real). Scope/Risk unchanged.

#### joan — 2026-08-08T01:40:58.697Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1277
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor` @ `87f191ce`

## Traceability

AC1→S1; AC2→S2 (parent AC1→S1; AC2→S2; parent AC3/AC4/AC5 N/A — boundary, AST-1278 / AST-1279). No orphan stages.

**Considered:** full active corpus scored in-session (universal `orch.*` set + scoped `core`/`utils` matches on `src/core/**`, `src/utils/config.py`).

## Findings

**fix-now — Stage 2 step 4: prefilter dispatch lookup key is wrong.** The plan calls `_dispatch_score_floor_for_task(candidate_id, "prefilter_company")`, but `prefilter_company` is the **TASK_CONFIG** key, not the dispatch row key. Dispatch rows use `task_key = "prefilter"`: `config.dispatch_task_grouping_catalog_key` exists specifically because "dispatch key differs from consult key" for prefilter, `_dispatch_entity_type_for_task_key` / `_dispatch_trigger_state_for_task_key` special-case `"prefilter"`, and `database.py` (AST-823 migration) does `UPDATE dispatch_task SET task_key = 'prefilter' … WHERE entity_type = 'company' AND task_key = 'prefilter_company'` — so no `prefilter_company` row survives. As written, the lookup matches zero rows, falls to the NULL normalizer, and prefilter soft-fails at a permanent `1.0`. Parent AC2 ("prefilter … using the candidate dispatch task's `score_floor`, including when that value is `0`") would be unmet, and AST-1278's `0` would be unreachable for prefilter. **Recommendation:** resolve the dispatch key from config rather than hardcoding the consult key, and say in the stage which key the lookup takes when the two differ (meteorite aliases are fine — `meteorite_grade_do` etc. are the same string on both sides).

**fix-now — Stage 2 step 1: tie-break ordering claim is inverted.** The plan says multiple same-`task_key` rows resolve to "the **first** row in the list order returned by `list_dispatch_tasks_for_candidate` (stable `id ASC` from data layer)". `tracker.list_dispatch_tasks_for_candidate` does not use the data-layer function of that name — it iterates `database.list_dispatch_tasks()`, which is `ORDER BY id DESC` (newest first). Only `database.list_dispatch_tasks_for_candidate` is `id ASC`, and that would be core reaching past its tracker wrapper. An engineer implementing the sentence literally gets the opposite row. **Recommendation:** state the intended row explicitly (newest vs oldest, and why), and prefer passing `trigger_state=` into the tracker helper — it already resolves compound hop labels via `parse_dispatch_hop_label`.

**discuss — NULL→`1.0` on the verdict path is new semantics with a production consequence.** The parent preserves NULL→`1.0` for **claim**; it says nothing about NULL for **verdict**. Roster `grade_do` / `grade_get` / `grade_like` dispatch rows are not seeded with a floor (only `METEORITE_DISPATCH_TASKS` carries explicit `0.0`), so on the day this lands those jobs grade against `1.0` instead of today's `6.0` until Susan sets floors in admin. That is a defensible read of the parent, but the plan should state the expected post-land floor values and whether any row backfill or Susan action is required before this ships. (`orch.pipeline.call-susan-for-product-decisions`)

**discuss — sequencing against still-active law.** `astral.config.pass-threshold-vs-score-floor` is `status: active` and forbids exactly this wiring ("Do not feed `dispatch_task.score_floor` into this path"). Parent AC4 retires it in AST-1279, which AST-1277 **blocks** — so this child lands first and the tree contradicts active law in the interval. Accepted on parent authority; the plan should say so where a reviewer will look, since the plan's §2.1 self-review only mentions not rewriting Code Rules.

**discuss — DRY on the trigger match.** `_dispatch_score_floor_for_task` re-implements trigger filtering that `tracker.list_dispatch_tasks_for_candidate(..., trigger_state=…)` already performs, including compound `{trigger}.{task_key}` hop labels. The plan's exact-equality compare misses those labels and silently falls through to the unfiltered set. (`astral.standards.dry-and-focused-functions`)

**discuss — pattern citations.** `pattern.dispatch.score-floor` is cited but not yet drafted under `canon/patterns/**` (AST-1279 owns authoring) — plain-language conformance is the only thing checkable now. Separately, the parent cites `astral.patterns.render-verdict-orchestrates-consult`, which is `status: retired`; the live id is `astral.idioms.render-verdict-orchestrates-consult`. Neither is this child's to fix.

**acceptable — verified against source.** The seven `pass_threshold` keys are exactly the ones enumerated (`prefilter_company` `0.0`; `grade_do` / `grade_get` / `grade_like` / `meteorite_grade_do` / `meteorite_grade_get` / `meteorite_like` `6.0`). The `dispatcher.py` claim-line replacement is numerically equivalent to today's ternary. Dropping the artifact `{rubric_key}_threshold` override is safe — `consult.py:1099` is the only `*_threshold` artifact reader in `src/` and nothing writes those keys. `roster._apply_prefilter_decoded_company_outcome` already has `candidate_id` from `ctx` and already local-imports the consult helpers, so step 4's wiring lands where the plan says. Helper placement, layer edges (`core`→`utils`, existing `roster`→`consult`), test-tree ban, and single-file-per-ticket docs all hold.

Self-assessment: `Single-Component` / `Medium` risk are honest. `high` conf is a touch generous given the prefilter key miss — the enumeration it rests on is right for `TASK_CONFIG` but not for the dispatch rows.

— Joan

context_tokens≈79000

#### ada — 2026-08-08T01:34:52.385Z
Plan published on `origin/sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor` @ `87f191ce`.

[Plan doc](https://github.com/susansomerset/astral/blob/sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor/docs/features/foundation/ast-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor.md)

**Scope:** Single-Component — strip seven `TASK_CONFIG` `pass_threshold` keys; scored soft-fail in consult (+ prefilter) reads candidate `dispatch_task.score_floor` via shared NULL→1.0 / keep-`0` normalizer; dispatcher claim reuses the helper.

**Conf:** high — keys and call sites are enumerated; claim already owns `score_floor`; AST-1278/1279 own admin `0` and law rewrite.

**Risk:** Medium — wrong row lookup or NULL→1.0 on prefilter changes who soft-fails vs historical `6.0`/`0.0` task-config thresholds; dealbreaker/error paths stay, but a bad floor still parks fail states.

---

# AST-1277 — Strip pass_threshold; verdict uses dispatch score_floor

**Linear:** [AST-1277](https://linear.app/astralcareermatch/issue/AST-1277/strip-pass-threshold-verdict-uses-dispatch-score-floor-remove-pass)  
**Parent:** [AST-1275](https://linear.app/astralcareermatch/issue/AST-1275/remove-pass-threshold-from-task-config) — Remove "pass_threshold" from task_config  
**Publish ref:** `sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor`

Remove every `TASK_CONFIG` `pass_threshold` key (roster consult, meteorite aliases, and `prefilter_company`). Scored soft-fail / pass after a run reads `score_floor` from the candidate’s matching `dispatch_task` row — explicit `0` means no numeric soft-fail; dealbreaker and technical-error paths stay. Does not own admin Score Floor dropdown (AST-1278) or statute/Code Rules retirement (AST-1279).

## Post-land floor expectations

Parent keeps NULL→`1.0` for **claim**; this child applies the **same** normalizer to **verdict** soft-fail (sole numeric floor). Roster `grade_do` / `grade_get` / `grade_like` dispatch rows are not seed-catalogued with an explicit floor (unlike `METEORITE_DISPATCH_TASKS` at `0.0`), so on the day this lands those hops soft-fail against **`1.0`**, not today’s TASK_CONFIG `6.0`, until Susan sets floors in admin (AST-1278 makes `0` selectable). **No row backfill in this ticket.** UAT / Susan action before expecting historical-6.0 behavior: set each candidate’s scored consult dispatch `score_floor` to the intended value (commonly `6.0` for roster GDL; `0` for always-pass numeric, e.g. prefilter / meteorite).

**Law sequencing (accepted):** `astral.config.pass-threshold-vs-score-floor` is still `status: active` and forbids feeding `score_floor` into the verdict path. Parent AC4 retires it in AST-1279, which this child **blocks**, so the tree contradicts that statute in the interval between landings. Parent authority accepts the interval; this child does not rewrite Code Rules or retire the statute.

**Pattern citations:** `pattern.dispatch.score-floor` is not yet under `canon/patterns/**` (AST-1279). Conform to the parent’s plain-language rule until that pattern lands. Parent citation `astral.patterns.render-verdict-orchestrates-consult` is retired; live id is `astral.idioms.render-verdict-orchestrates-consult` — not this child’s to fix in Linear text.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Delete all `pass_threshold` keys from `TASK_CONFIG`; add `effective_dispatch_score_floor` (NULL→1.0, keep explicit `0`); add `dispatch_row_task_key` (consult/catalog key → `dispatch_task.task_key`, prefilter only) | utils |
| `src/core/consult.py` | Resolve floor from candidate dispatch row via tracker helper + row key map; scored `_apply_render_verdict_decoded_job` uses it; rename `_render_score` threshold arg to `score_floor`; stop reading artifact/`pass_threshold` fallbacks | core |
| `src/core/roster.py` | Prefilter scored soft-fail uses the same dispatch `score_floor` (not hardcoded `0.0`); pass consult key `prefilter_company` into the helper (helper maps to dispatch key `prefilter`) | core |
| `src/core/dispatcher.py` | Claim-path floor assignment calls `effective_dispatch_score_floor` (same NULL/`0` rules; no behavior invent) | core |

**Out of files (do not touch):** `docs/ASTRAL_CODE_RULES.md` / statutes / pattern catalog (AST-1279); admin Score Floor UI (`AdminScheduledActions.tsx`, AST-1278); `tests/` and `docs/test-bible/**` (Betty); binary qualify/evaluate paths that discard `_render_score` state and only need an informational score (keep calling `_render_score` with literal `0.0` so state is unused-pass — those paths are not soft-fail consumers).

## Stages

### Stage 1: Strip TASK_CONFIG thresholds + shared floor helpers

**Done when:** `rg '"pass_threshold"' src/utils/config.py` returns no matches. `effective_dispatch_score_floor(None) == 1.0`, `effective_dispatch_score_floor(0) == 0.0`, `effective_dispatch_score_floor(0.0) == 0.0`, and `effective_dispatch_score_floor(6) == 6.0`. `dispatch_row_task_key("prefilter_company") == "prefilter"`, `dispatch_row_task_key("prefilter") == "prefilter"`, and `dispatch_row_task_key("grade_do") == "grade_do"` (meteorite aliases identity). Dispatcher job-claim floor assignment uses `effective_dispatch_score_floor` (same numeric outcomes as today’s inline ternary for scored rows).

1. In `src/utils/config.py`, delete the `"pass_threshold": …` entry from each of these `TASK_CONFIG` blocks only (leave every other key in those blocks untouched):
   - `prefilter_company` (currently `0.0`)
   - `grade_do`, `grade_get`, `grade_like` (currently `6.0`)
   - `meteorite_grade_do`, `meteorite_grade_get`, `meteorite_like` (currently `6.0`)
   Confirm with search: no remaining `"pass_threshold"` string under `src/utils/config.py`.

2. In `src/utils/config.py`, immediately after `dispatch_score_floor_option_labels` (near the existing score-floor helpers ~line 2907), add:

   ```python
   def effective_dispatch_score_floor(raw_score_floor: Optional[float]) -> float:
       """Normalize dispatch_task.score_floor for claim + scored soft-fail.

       Explicit 0 / 0.0 is valid (no numeric soft-fail / no claim exclusion by floor).
       NULL / missing → 1.0 (same claim rule dispatcher already applies on scored rows).
       """
       if raw_score_floor is None:
           return 1.0
       return float(raw_score_floor)
   ```

   Import `Optional` is already available in this module. Do not change `DISPATCH_SCORE_FLOOR_VALUES` or admin option labels (AST-1278).

3. In `src/utils/config.py`, next to `dispatch_task_grouping_catalog_key` (~line 2991; that helper maps dispatch→catalog), add the inverse used for row lookup:

   ```python
   def dispatch_row_task_key(task_key: str) -> str:
       """Map consult/catalog task_key to dispatch_task.task_key when they differ.

       ROSTER_CONFIG['prefilter']['task_key'] (`prefilter_company`) and the bare
       dispatch key `prefilter` both resolve to `prefilter` (AST-823 migrated rows).
       All other keys (including meteorite_grade_* aliases) are identity.
       """
       tk = (task_key or "").strip()
       if tk == "prefilter" or tk == ROSTER_CONFIG["prefilter"]["task_key"]:
           return "prefilter"
       return tk
   ```

   Do **not** invent other renames; prefilter is the only consult≠dispatch key pair this ticket needs.

4. In `src/core/dispatcher.py`, import `effective_dispatch_score_floor` from `src.utils.config`. Replace the scored job-claim floor line that currently does:

   ```python
   floor = float(task.get("score_floor")) if (is_scored and task.get("score_floor") is not None) else (1.0 if is_scored else None)
   ```

   with:

   ```python
   floor = effective_dispatch_score_floor(task.get("score_floor")) if is_scored else None
   ```

   Do **not** change the company-claim floor line (`float(task["score_floor"]) if … else None`) — company claim already treats NULL as ungated; that path is outside this ticket’s scored-verdict contract.

   ⚠️ **Decision:** Shared normalizer lives in `config.py` next to other dispatch score-floor helpers so claim and verdict cannot drift. Explicit `0` must not collapse to `1.0` (parent boundary: `0` distinct from NULL).

### Stage 2: Scored verdict + prefilter read dispatch score_floor

**Done when:** A scored job consult (`grading_mode == "scored"`) soft-fails when computed score `<` that candidate’s matching `dispatch_task.score_floor`, passes when `>=`, and with `score_floor == 0` never soft-fails on the numeric comparison (F2 dealbreaker and technical error paths unchanged). `_apply_render_verdict_decoded_job` does not read `cfg["pass_threshold"]` or `{rubric_key}_threshold` artifacts. Prefilter soft-fail looks up the dispatch row with `task_key == "prefilter"` (via `dispatch_row_task_key`), so an explicit `0` on that row is reachable. `rg pass_threshold src/` returns no matches.

1. In `src/core/consult.py`, add a helper (place with other private helpers near `_candidate_id_from_ctx` / before `_render_score`):

   ```python
   def _dispatch_score_floor_for_task(
       candidate_id: str,
       task_key: str,
       trigger_state: Optional[str] = None,
   ) -> float:
   ```

   Behavior (literal):
   - `cid = (candidate_id or "").strip()`; `raw_tk = (task_key or "").strip()`; `dispatch_tk = dispatch_row_task_key(raw_tk)`.
   - If `cid` empty or `dispatch_tk` empty → return `effective_dispatch_score_floor(None)` (i.e. `1.0`).
   - `ts = (trigger_state or "").strip()` or `None` if blank.
   - Call **`tracker.list_dispatch_tasks_for_candidate(cid, trigger_state=ts)`** when `ts` is not None; otherwise `tracker.list_dispatch_tasks_for_candidate(cid)`. Do **not** re-implement trigger / compound hop-label matching in consult — the tracker helper already uses `parse_dispatch_hop_label`.
   - From that list, keep rows whose `(row.get("task_key") or "").strip() == dispatch_tk`.
   - If `ts` was set and that filter yields zero rows, **fall back once**: `tracker.list_dispatch_tasks_for_candidate(cid)` (no trigger filter), then the same `task_key == dispatch_tk` keep.
   - If still zero matching rows → return `effective_dispatch_score_floor(None)`.
   - If one or more matching rows → use the **first** element of that filtered list. That first element is the **newest** row (`id DESC`): `tracker.list_dispatch_tasks_for_candidate` walks `database.list_dispatch_tasks()` which is `ORDER BY id DESC`. Do **not** claim `id ASC` and do **not** call `database.list_dispatch_tasks_for_candidate` from consult (core stays on the tracker wrapper).
   - Return `effective_dispatch_score_floor(chosen.get("score_floor"))`.

   Import `effective_dispatch_score_floor` and `dispatch_row_task_key` from `src.utils.config` in the existing config import block.

   ⚠️ **Decision — lookup over ctx injection:** Resolve from the DB row at verdict time rather than requiring dispatcher to stuff `score_floor` into `ctx`. Ad-hoc / single-job `render_verdict` has no claim context; the dispatch row is the sole authority. Missing row → NULL normalization (`1.0`), not a hard raise, so CLI/ad-hoc does not brick.

   ⚠️ **Decision — drop artifact `{rubric}_threshold` override:** Parent makes `dispatch_task.score_floor` the sole numeric floor. Stop reading `artifacts.get(f"{rubric_key}_threshold", …)`. Do not resurrect a TASK_CONFIG or artifact threshold. (No UI writer for those keys remains in `src/`.)

   ⚠️ **Decision — newest-row tie-break:** When multiple same-`task_key` rows remain after trigger preference / fallback, take the first tracker-returned match (= newest `id`). Prefer always passing `trigger_state=` from the job’s current state so multi-row collision is rare; compound hop labels are handled by the tracker helper, not by exact string equality in consult.

2. In `_render_score`, rename the parameter `pass_threshold: float` to `score_floor: float`. Update the three debug/detail strings and the comparison to use `score_floor` (same `score < score_floor` → `fail_state` math). Keep F2 dealbreaker branch first; keep score persistence/`pass_state` return shape identical.

3. In `_apply_render_verdict_decoded_job`, in the `mode == "scored"` branch, replace:

   ```python
   artifacts = (ctx or {}).get("candidate_data", {}).get("artifacts", {})
   threshold = artifacts.get(f"{rubric_key}_threshold", cfg.get("pass_threshold", 6.0))
   …
   to_state, score = _render_score(cfg, rubric_criteria, grades, float(threshold))
   ```

   with (same control flow otherwise):
   - `candidate_id = _candidate_id_from_ctx(ctx)` — if empty, also try `str((tracker.get_job(astral_job_id) or {}).get("astral_candidate_id") or (tracker.get_job(astral_job_id) or {}).get("candidate_id") or "")` so single-job paths without ctx still resolve.
   - `job_row = tracker.get_job(astral_job_id) or {}` (binary branch already loads a job row — reuse one fetch if already present in that function; do not double-fetch unnecessarily).
   - `floor = _dispatch_score_floor_for_task(candidate_id, dispatch_task_key, (job_row.get("state") or None))` — `dispatch_task_key` may be a consult or dispatch string; the helper maps via `dispatch_row_task_key` (identity for `grade_*` / `meteorite_grade_*`).
   - `to_state, score = _render_score(cfg, rubric_criteria, grades, floor)`
   - Keep `_require_complete_grade_set` before `_render_score` as today.

4. In `src/core/roster.py` `_apply_prefilter_decoded_company_outcome`, replace the informational-only score block that calls `_render_score(..., 0.0)` so soft-fail participates in the outcome:
   - Resolve `floor = _dispatch_score_floor_for_task(candidate_id, "prefilter_company")` (import the helper from `src.core.consult` alongside the existing `_render_score` import). The helper’s `dispatch_row_task_key` maps `prefilter_company` → dispatch row key **`prefilter`** — do **not** query for `task_key == "prefilter_company"` (those rows were migrated away in AST-823).
   - Keep the existing `_render_pass_fail("prefilter_company", grades)` call for X / no-confidence / empty-grade rules that `_render_score` does not cover.
   - When `verdict_state == cfg["pass_state"]` and `rubric_list` is non-empty: call `score_state, score = _render_score(task_cfg, rubric_list, grades, floor)`. Set `prefilter_score = float(score)` when `score is not None`. If `score_state == cfg["fail_state"]`, set `verdict_state = cfg["fail_state"]` **before** the decomposed/legacy `new_state` branching so numeric soft-fail parks as fail (same as dealbreaker fail). When `floor == 0.0`, `_render_score` never soft-fails on the numeric compare (dealbreaker inside `_render_score` still can).
   - Do not add a new `pass_threshold` (or alias name) on `TASK_CONFIG["prefilter_company"]`.

   ⚠️ **Decision — prefilter NULL floor:** Same normalizer as job consult (`NULL`→`1.0`). Historical `pass_threshold: 0.0` meant always-pass numeric; after this change, always-pass requires an explicit `score_floor` of `0` on the candidate’s **`prefilter`** dispatch row (AST-1278 makes `0` selectable). Do not special-case prefilter to treat NULL as `0`.

5. Leave binary qualify/evaluate call sites that do `_, score = _render_score(..., 0.0)` unchanged (informational score only; verdict remains `_render_pass_fail`). Update the module docstring line in `consult.py` that mentions “thresholds” from TASK_CONFIG so it says soft-fail floor comes from `dispatch_task.score_floor` (one-line docstring honesty — not a Code Rules edit).

6. Repo check before stage commit: `rg 'pass_threshold' src/` must return no matches. If any remain outside the planned files, **stop** and comment on the parent — do not expand scope.

## Self-Assessment

**Scope:** `Single-Component` — config strip plus consult/roster scored soft-fail wiring (and a one-line dispatcher DRY reuse of the normalizer); no UI, no statutes, no test-tree.

**Conf:** `Medium` — TASK_CONFIG key enumeration and claim normalizer are solid; round-1 caught a real consult≠dispatch key miss on prefilter and an inverted list-order claim, both now pinned in Stage 1–2.

**Risk:** `Medium` — wrong floor lookup or NULL→1.0 changes who soft-fails vs historical `pass_threshold` 6.0/0.0 (see Post-land floor expectations); dealbreaker/error paths are intentionally untouched but a bad floor still parks jobs in fail states.

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Shared `effective_dispatch_score_floor`; trigger filtering delegated to `tracker.list_dispatch_tasks_for_candidate(..., trigger_state=)` (no parallel hop-label parser in consult); `dispatch_row_task_key` is the single consult↔dispatch rename point.
- **§2.1 config SoT:** Deletes resurrected task-config thresholds; floors read from dispatch rows / normalizer — does **not** rewrite the outdated §2.1 pass-threshold subsection (AST-1279). Active statute `astral.config.pass-threshold-vs-score-floor` is contradicted in the land interval by parent order (see Post-land / Law sequencing).
- **§2.4 batch / §2.6 states:** Claim-process-release and pass/fail/error state **names** unchanged; only the numeric compare source changes.
- **§2.7 / `astral.idioms.render-verdict-orchestrates-consult`:** Still orchestrates; scored branch swaps floor source only.
- **§3.3 imports:** `consult` → `tracker` + `config`; `roster` → `consult` helpers (existing pattern); no new `ui`/`external` edges; no direct `database.list_dispatch_tasks_for_candidate` from consult.
- **§3.5 naming:** `score_floor` / `effective_dispatch_score_floor` / `dispatch_row_task_key` match existing dispatch vocabulary.
- **Test-tree ban:** No `tests/` or bible edits in this plan.

## Revisions

Revision 1 — 2026-08-08  
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric REVISE) — fix-now wrong prefilter dispatch lookup key (`prefilter_company` vs `prefilter`); fix-now inverted tie-break order claim (`id ASC` vs tracker/`list_dispatch_tasks` `id DESC`); discuss NULL→1.0 verdict semantics / Susan floor action; discuss active-law interval vs AST-1279; discuss DRY trigger match via tracker helper; discuss pattern citation status.  
Changes: Added `dispatch_row_task_key`; Stage 2 lookup uses tracker `trigger_state=` + newest-first tie-break; prefilter resolves through that map to dispatch key `prefilter`; documented post-land floor expectations and accepted statute-interval contradiction; Conf → Medium; self-review updated for DRY / idiom id.

## Review

- **Branch:** `sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor`
- **Tip:** `3e8a7c8c` (`3e8a7c8c21619f6e77a7be519909dd386a2d8161`)
- **Stages:** Stage 1 `8c1aea8b` (config/helpers/dispatcher); Stage 2 `3e8a7c8c` (consult + roster)

## Review (Radia)

[code-rubric] revision=2 — **Overall: DISCUSS**

Diff `origin/dev...origin/sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor` @ `106c74fa` (post `merge-resume` sync of the advanced `ftr/AST-1275` tip — AST-1278 landed + resolved while this review was in flight). Full active-set (64 statutes) scored in-session per code-rubric.v2 §5.0. No fix-now. One straggler discuss, three trivial path-match stragglers, both round-1 Joan fix-nows verified closed against source.

**What's solid:**

- Both of Joan's round-1 fix-nows verified against the shipped diff, not just the plan text: `dispatch_row_task_key` correctly maps `prefilter_company` → dispatch row key `prefilter` (`config.py`), and `_dispatch_score_floor_for_task` takes newest-first (`tracker.list_dispatch_tasks_for_candidate` walks `database.list_dispatch_tasks()` = `ORDER BY id DESC`) with a single documented fallback when `trigger_state=` yields zero rows.
- `rg pass_threshold src/` returns no matches on this branch — Stage 1/2 done-when criteria fully met, exactly the seven enumerated `TASK_CONFIG` keys stripped.
- Shared `effective_dispatch_score_floor` used by both claim (`dispatcher.py`) and verdict (`consult.py`/`roster.py`) — one NULL→1.0 / keep-`0` normalizer, no drift risk (`astral.standards.dry-and-focused-functions`, `astral.standards.no-hardcoded-sets` conform).
- Binary qualify/evaluate call sites (`_render_score(..., 0.0)`, informational-only) untouched, exactly per plan step 5 — only one `_render_score(` call site changed in `consult.py` (the scored verdict path).
- `roster.py`'s soft-fail block sets `verdict_state = cfg["fail_state"]` *before* the decomposed/legacy `new_state` branching, so numeric soft-fail parks the same way as dealbreaker fail — verified by reading the full function, not just the diff hunk.
- Test-tree boundary held: `test(AST-1277)` + `merge-tests(AST-1277)` are the only commits touching `tests/` / `docs/test-bible/**`; both `code(AST-1277)` commits are `src/`-only.

**Straggler (C4) — discuss, no reply needed (already resolved at plan/parent level):**

- `astral.config.pass-threshold-vs-score-floor` is still `status: active` and its text forbids exactly this wiring ("Do not feed `dispatch_task.score_floor` into this path"). The plan's own "Considered but excluded" list named it (owned by AST-1279), so this sweep's mechanical belt-and-suspenders check (C4) surfaces it as a straggler — and on the merits it does score `violates`, by design. This is not a code defect: parent AST-1275 AC4/AC5 explicitly orders retirement of this statute in the blocking sibling AST-1279, and Joan's `[plan-rubric] revision=1` **APPROVED** verdict reviewed this exact "law sequencing" interval and accepted it on parent authority. Nothing for this ticket (or Ada) to fix — flagged here only so the interval is visible in both the plan bible and this review, per Joan's own framing of the same finding.
- Three more excluded-list ids matched the diff's `src/core/**` / `src/utils/config.py` paths generically (`astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.layers.ui-config-driven-business-logic`) but all score `conforms` — no new cross-layer edges, no UI logic added to `config.py`. Noted for C4 completeness only.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | `pass_threshold` keys deleted in place from existing `TASK_CONFIG` blocks; new helpers added beside sibling score-floor helpers — no re-invented catalog. |
| `pattern.batch.entity-claim-process-release` | conforms | Claim/process/release shape untouched; only the floor value computation inside the existing claim path was swapped to the shared normalizer. |
| `pattern.state.entity-state-transitions` | conforms | Core (`roster.py`) still decides `verdict_state`/`new_state` and hands the target to `transition_company_state`; no daisy-chaining introduced. |
| `pattern.dispatch.score-floor` (proposed) | not-applicable | Not yet under `canon/patterns/**` (AST-1279 owns authoring). Plan explicitly conforms to the parent's plain-language rule instead of building against an unapproved id — correctly deferred, not an invalid citation. |

## Frame diff

(none) — no scope drift; description checkboxes already match delivered behavior.

context_tokens≈52000

— Radia

## Resolution

Revision 1 — 2026-08-08  
Driven by: Radia `[code-rubric] revision=2` Overall **DISCUSS** @ `0cdf1e97`.

- **fix-now:** none.
- **discuss (straggler C4 / active `astral.config.pass-threshold-vs-score-floor`):** no product change — already documented under plan Post-land / Law sequencing and Considered but excluded; retirement owned by AST-1279; Joan APPROVED the interval. Acknowledged; nothing to land on this tip.
- **advisory:** layer-match ids score conforms — no action.
- **Frame diff:** none.
