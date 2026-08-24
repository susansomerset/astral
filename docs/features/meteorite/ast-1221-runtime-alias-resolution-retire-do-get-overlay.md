<!-- linear-archive: AST-1221 archived 2026-08-17 -->

## Linear archive (AST-1221)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1221/runtime-alias-resolution-retire-doget-overlay-task-config-aliases-via  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1184 — Task config aliases via master_task_key  
**Blocked by / blocks / related:** parent: AST-1184; blocks: AST-1222

### Description

## What this implements

After #1: honor alias → master resolution wherever prompts/shared content are looked up; run alias dispatch keys with alias-owned orchestration; remove `METEORITE_GDL_OUTCOME_BY_TASK` use for Do/Get. Does **not** author the config contract (sibling #1) or seed/retarget meteorite rows (sibling #3).

## In scope

- [X] `pattern.layers.import-discipline` / `astral.layers.import-direction` — core consumes `resolve_task_key_for_content` / `is_task_alias` from utils; no reverse imports
- [X] `astral.agent.do-task-delegation` — alias invocation stays on `do_task`; prompts load from master's `agent_task`
- [X] `astral.standards.debug-contract-gated` — Style D alias→master detail only when `debug=True` on touched hops
- [X] `astral.standards.no-hardcoded-sets` — no new Do/Get overlay map; header/strict-envelope via resolve; delete `METEORITE_GDL_OUTCOME_BY_TASK`
- [X] `astral.standards.in-scope-only` — runtime resolve + overlay retirement only; no seed/UI/contract authorship
- [X] `astral.git.engineer-test-tree-ban` — no `tests/` / bible edits on this ticket

## Considered but excluded

- [X] `pattern.config.config-block` / proposed `pattern.config.task-alias` / alias `TASK_CONFIG` literals + resolve helpers — **AST-1220** (`src/utils/config.py`)
- [X] Alias `agent_task` seed + `METEORITE_DISPATCH_TASKS` / `SEED_CONFIG` Do/Get retarget — **AST-1222** (`astral.seed.agent-tables-in-repo-json`)
- [X] UI hardcode audit / alphabetical dropdowns — **AST-1185**
- [X] Gaze/Meteorite Review section rename — **AST-1183**

## Acceptance criteria

- [X] Invoking or dispatching `meteorite_grade_do` / `meteorite_grade_get` executes the master's prompts/content (no alias prompt override); operators do not maintain a second prompt body for that hop.
- [X] Alias entries for first consumers carry their own pass/fail/error (and related orchestration); `METEORITE_GDL_OUTCOME_BY_TASK` no longer supplies Do/Get meteorite outcomes.
- [X] If backend `debug=True` paths for these hops are touched: Style D index headers show found/recorded detail for the alias identity (and resolution to master is visible in detail when useful); no new ungated debug noise.

## Boundaries

Does **not** author the config contract (sibling #1). Does **not** seed/retarget meteorite rows (sibling #3). Does **not** own UI hardcode audit (AST-1185).

## Notes for planning

After AST-1220. Retire Do/Get overlay once aliases own meteorite outcomes.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1184-task-config-aliases-via-master-task-key`, child `sub/AST-1184/<this-id>-runtime-alias-resolution-retire-do-get-overlay`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-06T08:18:30.449Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log.sh` failed on `origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`:
- Bad commit: `af3998f0` — `Merge remote-tracking branch 'origin/dev' into sub/AST-1184/AST-1221-…`
- Tip `f876bcbe` resolve sits on top of that pull-merge.

@Hedy Lamarr — drop the origin/dev pull-merge from the sub log, restack on `origin/ftr/AST-1184-task-config-aliases-via-master-task-key` (fetch + merge ftr, never `git pull origin/dev` onto sub), keep resolve tip clean, push `origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`. Chuckles will re-run merge-child after.

— Chuckles

#### radia — 2026-08-06T08:16:01.393Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1221
**Publish ref:** `864e58c1` (`origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`)
**Overall:** CLEAN

## Plan adherence

- All three stages match the plan's binding code blocks verbatim, including both Revision 1 fixes that closed Joan's round-1 findings: `_is_strict_encoded_batch_consult` wraps the resolve and is used at **both** membership sites (re-grepped `agent.py` and confirmed exactly two call sites); `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` are untouched — chain-authority identity stays caller-keyed as the Decision requires.
- Repo grep gate is fully clean at tip: zero `METEORITE_GDL_OUTCOME_BY_TASK` references anywhere under `src/` — stricter than Joan's round-1 prediction that a couple of comments would survive.
- Commit hygiene holds: `code(AST-1221)` commits touch only `src/core/{agent,consult,dispatcher}.py` + `src/utils/config.py`; `test(AST-1221)`/`merge-tests(AST-1221)` touch only Betty's test-tree paths.

**Note:** this three-dot diff also carries AST-1220's already-reviewed changes (merged onto this branch via `origin/ftr/AST-1184-...` per `orch.git.merge-on-checkout`, since AST-1220 hasn't landed `dev` yet). AST-1220 was independently reviewed clean (Review Posted); this review's findings focus on AST-1221's own commits.

**Pattern conformance:** `pattern.layers.import-discipline` — conforms (core→utils only, no reverse imports). `astral.patterns.render-verdict-orchestrates-consult` / `astral.patterns.coat-check-never-store-empty` — conforms (untouched by this diff).

Full active-set sweep scored in-session: 65 active statutes (18 universal + 41 scoped-applicable against this diff's `{core, utils, docs}` layers / `src/core/{agent,consult,dispatcher}.py`, `src/utils/config.py`, `docs/features/**`, `docs/test-bible/**`, `tests/**` paths) — zero `violates`, zero `needs-discussion`. `python3 -m py_compile` clean on all four touched modules at tip.

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈85000

— Radia

#### betty — 2026-08-06T08:10:07.961Z
## QA test manifest

`origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay` @ `49c0cb65` (`merge-tests(AST-1221): origin/tests da9e765be66dfbb6a3375ff88e18e52f2981dfde`)

1. `tests/component/core/test_agent.py::TestAst1221RuntimeAliasAgent` — prompt fetch via master; strict-envelope membership via resolve
2. `tests/component/core/test_consult.py::TestAst1221RuntimeAliasConsult` — alias TASK_CONFIG orch + header resolve + render
3. `tests/component/core/test_consult.py::TestAst1054MeteoriteGdlOutcomeOverlay` — revised: overlay symbol deleted; shared `grade_do` always Gaze
4. `tests/component/utils/test_config.py::TestAst1220TaskAliasConfigContract` — revised: `not hasattr(METEORITE_GDL_OUTCOME_BY_TASK)`
5. `tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch` + `TestAst1210EvaluateMeteoriteTwinConfig` — overlay iterate / membership asserts retired
6. `tests/component/core/test_dispatcher.py::TestAst1221AliasChunkExhaust` — alias keys in `_CHUNK_EXHAUST_CONSULT_JOB_KEYS`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1221RuntimeAliasAgent \
  tests/component/core/test_consult.py::TestAst1221RuntimeAliasConsult \
  tests/component/core/test_consult.py::TestAst1054MeteoriteGdlOutcomeOverlay \
  tests/component/utils/test_config.py::TestAst1220TaskAliasConfigContract \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1210EvaluateMeteoriteTwinConfig \
  tests/component/core/test_dispatcher.py::TestAst1221AliasChunkExhaust \
  -q
```

**Broken / obsolete revised:** any assert that indexes / empties / iterates `METEORITE_GDL_OUTCOME_BY_TASK` (AST-1054 / AST-1220 interim).

**Bible shasum** (`origin/sub/...` tip):
- `docs/test-bible/utils/config.md` `46c94624393c608891b5363857b06bcdbcbe165a`
- `docs/test-bible/core/consult.md` `f9199e0c467e524d9d3debcbdbd09903fc93cec2`
- `docs/test-bible/core/agent.md` `935257ecf367e23085836e41d2c9861fd88e4088`
- `docs/test-bible/core/dispatcher.md` `fa34f9ca3609f14357d510c5f896e78546d6b42f`

Do **not** exercise meteorite Do/Get as operator-safe until AST-1222 retargets dispatch (shared keys still use Gaze outcomes).

— Betty

#### joan — 2026-08-06T08:00:06.378Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1221
**Overall:** APPROVED
**Publish-ref tip:** `daf6d3cb` (`origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`)
**Validated against build base:** `origin/ftr/AST-1184-task-config-aliases-via-master-task-key` @ `dcfb25d6` (unchanged since round 1, so the same anchors apply).

**Considered:** 56 active statutes (18 universal + 38 scoped), 9 scoped excluded — plan layers `{core, utils}`, paths `src/core/agent.py`, `src/core/consult.py`, `src/core/dispatcher.py`, `src/utils/config.py`, change_types `{modify, delete}`. Scored in-session. (Round 1 reported 57/8; on recount `astral.git.engineer-test-tree-ban` is excluded by the path predicate — `tests/**` matches no plan path — rather than considered. It conforms trivially either way; the plan takes no test-tree work.)

## Traceability

AC1→S1.2 (`_resolve_task_prompts` resolve), S2.5 (alias routing reaches `do_task`); AC2→S2.1–S2.2 (overlay read retired), S3.2 (symbol deleted); AC3→S1.3 (Style D gated). No orphan stages — S1.4 (strict-envelope gate) ↔ parent Functional scope §2 (invoking an alias runs the master's content, no divergence), S3.1 (exhaust keys) ↔ Functional scope §4 (aliases participate in dispatch).

## Round 1 items — both cleared

**fix-now → resolved.** Stage 1 step 4 now introduces `_is_strict_encoded_batch_consult` and uses it at both membership sites. I re-grepped the base to confirm the count: `_STRICT_ENCODED_BATCH_CONSULT_KEYS` is tested at exactly two places (`agent.py:99` inside the helper, `agent.py:2468` in `do_task`), so "both sites" is genuinely all of them — there is no third caller waiting to bite. With `strict_batch` now computed from the resolved key, the `agent_performance` back-fill and both `envelope_err` calls become live for `meteorite_grade_do` / `meteorite_grade_get`, which is what Stage 1's own Done-when requires. The frozenset body stays masters + twins, so no parallel meteorite set.

**discuss → resolved.** The choke-point claim is now correctly scoped: prompt-content resolve is one site, and `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` are documented as deliberately caller-keyed with the reason (chain authority, not content). The Conf justification was updated to match rather than left overstated.

## Findings

**discuss — the Stage 3 grep gate will report FAIL on comments the plan deliberately keeps.** `astral.standards.in-scope-only`.

Stage 3 step 3 runs `rg -n 'METEORITE_GDL_OUTCOME_BY_TASK' src/ && echo 'FAIL: symbol still referenced'`. On the base there are seven matches: two live (`consult.py:39` import, `consult.py:93` read), one docstring (`consult.py:2130`), two comments in `config.py` (589, 685), and the assignment plus assert loop (`config.py:2556`, `2561`). Stages 2–3 remove the live ones and rewrite the docstring, but step 2 explicitly *permits* leaving the alias-entry comment at `config.py:685` ("replaces `METEORITE_GDL_OUTCOME_BY_TASK`") as historical context, and `config.py:589` is a comparative note on a different entry that the plan never claims. So a correctly-executed plan still trips its own gate, and the engineer either deletes comments AST-1220 chose to keep or learns to ignore a red gate.

**Recommendation:** scope the gate to live references, or drop it and lean on the check immediately after it — `assert not hasattr(c, 'METEORITE_GDL_OUTCOME_BY_TASK')` already proves the symbol is gone, and a compile of `consult.py` proves the import is gone. Non-blocking: the authoritative check is already in the plan.

**acceptable — the alias runtime path is clean end-to-end, verified rather than assumed.** I walked the whole encoded dispatch path for an alias key looking for a lookup that would `KeyError` or silently fall back to Gaze: `_consult_scored_dispatch_batch_encoded` (header via resolve after step 4; `cfg_dispatch` from alias `TASK_CONFIG`; `agent_tk` = alias since the entry omits `agent_task`), `_prep_live_content` and `_transition_job_state_for_task` (`scored: True` present on both alias entries), `_run_batch_consult` (`_consult_orchestration_for_entity`, `_rubric_criteria_for_cfg` off `rubric_artifact`, then `do_task(task_key=alias)`), and `_apply_render_verdict_decoded_job` (cfg passed in). Every one is either identity-agnostic or reads a field AST-1220 actually shipped — I confirmed `meteorite_grade_do` / `meteorite_grade_get` carry `pass_state` / `fail_state` / `error_state` / `save_prefix` / `pass_threshold` / `grades_key` / `rubric_artifact` on `origin/ftr`, so the Stage 2 verify assertions will hold.

**acceptable — the two membership styles are inconsistent on purpose, and the precedent is real.** Stage 1 resolves for the strict-envelope gate while Stage 3 adds alias literals to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS`. That reads odd until you accept the stated line: response-shape behavior follows the content master, dispatch eligibility is an identity-level closed set. I checked the precedent claim — `_DISPATCH_BATCH_CALL_MODE_ONE` in `config.py` already lists both alias keys explicitly (shipped by AST-1220), so the explicit style matches what is in tree.

**acceptable — the chain-authority decision now hands AST-1222 a constraint, which is the right place for it.** Once alias `agent_task` rows exist, `_parent_hop_task_key_for_child` iterates every catalog key and matches on `run_next`, so an alias row seeded by copying the master wholesale would produce a duplicate `run_next` and trip the "ambiguous run_next parents" warning. The plan's requirement — grouping-only rows, no `run_next` — is written down and should be honored by Katherine's plan; it is not this ticket's code.

**acceptable — overlay-removal window unchanged and still disclosed.** The QA note bounding meteorite Do/Get as not operator-safe until AST-1222, with classic Gaze at `PASSED_JD` / `PASSED_DO` as the thing that must keep working, is the correct framing for the accepted sequencing.

**Self-assessment:** Honest. Scope is Single-Component and matches the four files. `Conf: high` now rests on claims I verified rather than on the overstated choke-point line. `Risk: Medium` is right — the residual risk is the pre-AST-1222 window, which is disclosed and bounded, not the resolve design.

This is a good plan: field-driven resolve at the two places response behavior is decided, explicit membership only where identity is the question, gated Style D, and no seed or UI creep. Approved — fix the grep gate opportunistically during build if it annoys you.

context_tokens≈62000

— Joan

#### hedy — 2026-08-06T07:53:36.699Z
[plan-discuss] round=1 reply

Patched plan @ `daf6d3cb` — [ast-1221-runtime-alias-resolution-retire-do-get-overlay.md](https://github.com/susansomerset/astral/blob/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay/docs/features/meteorite/ast-1221-runtime-alias-resolution-retire-do-get-overlay.md)

**fix-now (strict-envelope gate):** Stage 1 step 4 now adds `_is_strict_encoded_batch_consult(task_key)` (`resolve_task_key_for_content(task_key) in _STRICT_ENCODED_BATCH_CONSULT_KEYS`) and uses it at both sites — `do_task` ~2468 (`strict_batch = …`) and the top of `_strict_encoded_batch_consult_envelope_err`. Aliases get `agent_performance` back-fill + envelope checks; frozenset body stays masters + twins.

**discuss (choke-point claim):** Documented that `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` intentionally stay on caller identity — prompt-content resolve is only `_resolve_task_prompts`. Safe after AST-1222 grouping-only alias rows (no `run_next`); resolving those to master would wrongly inherit the master's chain. No code change at those two sites.

**Self-assessment / code-rules:** Conf justification + §1.3 / `run-next-is-chain-authority` notes updated. Status left **Plan Discuss**.

#### joan — 2026-08-06T07:50:26.493Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1221
**Overall:** REVISE
**Publish-ref tip:** `fd46f3e6` (`origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`)
**Validated against build base:** `origin/ftr/AST-1184-task-config-aliases-via-master-task-key` @ `dcfb25d6` — the sub is stacked on `dev` and carries only the plan commit, so I read every anchor from the ftr tree the build will actually merge onto.

**Considered:** 57 active statutes (18 universal + 39 scoped), 8 scoped excluded — plan layers `{core, utils}`, paths `src/core/agent.py`, `src/core/consult.py`, `src/core/dispatcher.py`, `src/utils/config.py`, change_types `{modify, delete}`. Wider scoped set than AST-1220 because the core layer pulls in the agent / batch / render-verdict / state families. Scored in-session.

## Traceability

AC1→S1.2 (`_resolve_task_prompts` resolve), S2.5 (alias routing so aliases reach `do_task`); AC2→S2.1–S2.2 (overlay read retired), S3.2 (symbol deleted); AC3→S1.3 (Style D gated). No orphan stages — S3.1 (exhaust keys) ↔ parent Functional scope §4 (aliases participate in dispatch).

## Findings

**fix-now — Stage 1 step 4 does not achieve Stage 1's own "Done when"; the strict-envelope gate stays closed for aliases.** `astral.standards.dry-and-focused-functions`.

Stage 1 declares aliases must "participate in the strict encoded-batch envelope gate," and step 4 resolves inside `_strict_encoded_batch_consult_envelope_err`. But `_STRICT_ENCODED_BATCH_CONSULT_KEYS` is tested in **two** places, and the plan only changes one. At `agent.py:2468` the caller computes the gate from the unresolved key:

```python
strict_batch = task_key in _STRICT_ENCODED_BATCH_CONSULT_KEYS
if strict_batch and isinstance(parsed, dict) and parsed.get("agent_payload") is not None and parsed.get("agent_performance") is None:
    parsed = {**parsed, "agent_performance": {}}          # skipped for aliases
envelope_err = _strict_encoded_batch_consult_envelope_err(task_key, parsed) if strict_batch else None
...
if strict_batch and not envelope_err:                      # skipped for aliases
    envelope_err = _strict_encoded_batch_consult_envelope_err(task_key, parsed)
```

For `meteorite_grade_do` / `meteorite_grade_get`, `strict_batch` is `False`, so the `agent_performance` back-fill never runs and the `if strict_batch else None` guard means your newly-resolving function is **never called** — step 4 is dead code for exactly the keys it was written for. The alias hops would then accept bare compact-line responses that the masters reject, which is a real behavioral divergence between an alias and its master on the encoded Do/Get path.

**Recommendation:** resolve once and use it in both places — e.g. a small `_is_strict_encoded_batch_consult(task_key)` helper wrapping `resolve_task_key_for_content(task_key) in _STRICT_ENCODED_BATCH_CONSULT_KEYS`, called at `2468` and at the top of `_strict_encoded_batch_consult_envelope_err`. One concept, one membership test. Keep the frozenset body as masters + twins, as you planned.

**discuss — "prompt resolve has one choke point" is not quite true, and the untouched sites become live for AST-1222.** `astral.dispatch.run-next-is-chain-authority`.

`agent.py` reads `agent_task` rows at three places, not one: `_resolve_task_prompts` (458), `_parent_hop_task_key_for_child` (788), and `_current_agent_task_run_next` (3097). The latter two stay keyed on the raw `task_key`. Both are harmless **today** — aliases have no `agent_task` row until AST-1222, so `get_agent_task(alias)` returns `None`, and Do/Get have no `run_next` chain, so `""` is the correct answer anyway. But `get_task_keys()` already includes the alias keys, and AST-1222 seeds grouping-only alias rows, at which point both functions start returning row-derived answers for aliases with nobody having reasoned about it.

**Recommendation:** state in the plan that these two intentionally stay on caller identity and why that is safe (alias rows carry grouping only, no `run_next`), so the sibling does not silently change chain-authority behavior. No code change required here — just stop claiming a single choke point.

**acceptable — the design crux checks out.** I verified the mechanism AC1 depends on rather than assuming it: all three `agent_task` reads in `consult.py` (1066, 1129, 2150) use `cfg.get("agent_task") or <task_key>`, so an alias that deliberately omits the field falls back to its own key, reaches `_resolve_task_prompts`, and resolves to the master's row. `render_verdict` needs nothing else from the alias entry that AST-1220 did not ship — `rubric_artifact`, `grades_key`, `save_prefix`, `pass_threshold` and the scored flags are all present, which is what makes that field duplication earn its keep.

**acceptable — Stage 2 step 5 handles the trap in its own rewrite.** Guarding the `_batch = {…}[task_key]` dict lookup with the master-only tuple before the alias `else` branch is necessary; an unguarded lookup would `KeyError` on alias keys. Good catch in the draft.

**acceptable — the overlay-removal window is disclosed and correctly bounded.** With the overlay gone and dispatch rows still on shared keys until AST-1222, meteorite Do/Get will take classic Gaze outcomes and most likely raise on `prior_states` in `transition_job_state` rather than silently mis-route — loud failure is the better of the two. The QA note plus "classic Gaze Do/Get at `PASSED_JD` / `PASSED_DO` must keep working" is the right framing.

**acceptable — retaining the unused `entity_state` parameter** on `_consult_orchestration_for_entity` keeps call sites 1126 / 1312 / 2149 / 2519 stable and is documented as deliberate. It should die once AST-1222 lands, but not on this ticket.

**Self-assessment:** Scope, and the dependency claim, are accurate — I confirmed AST-1220 is at User Testing and its contract is on `origin/ftr` (`master_task_key` present, overlay already `{}`), so "helpers and alias entries are shipped" is true and the Stage 1 stop-condition is the right safety net. Risk Medium is honest. The `Conf: high` justification leans on the "one choke point" claim, which is what produced the fix-now above; the resolve design itself is sound, so this should stay `high` once the gate is fixed.

The shape of this plan is good — field-driven resolve instead of parallel meteorite maps in both the header lookup and the envelope gate, gated Style D, no seed or UI creep. Fix the one gate, qualify the choke-point claim, and it approves.

context_tokens≈158000

— Joan

#### hedy — 2026-08-06T07:45:37.578Z
**Plan:** [ast-1221-runtime-alias-resolution-retire-do-get-overlay.md](https://github.com/susansomerset/astral/blob/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay/docs/features/meteorite/ast-1221-runtime-alias-resolution-retire-do-get-overlay.md) @ `fd46f3e6`

**Scope:** Single-Component — core `agent` / `consult` / `dispatcher` plus deleting `METEORITE_GDL_OUTCOME_BY_TASK` from utils; no seed/UI.

**Conf:** high — AST-1220 helpers + alias entries are shipped; overlay is one consult function; prompt resolve has one choke point (`_resolve_task_prompts`); alias routing mirrors existing `meteorite_like` / resolve patterns.

**Risk:** Medium — overlay gone before AST-1222 retarget means shared-key meteorite Do/Get temporarily use Gaze outcomes (accepted sequencing); wrong resolve would mis-load prompts or mis-route alias pass/fail once aliases are dispatched.

---

# AST-1221 — Runtime alias resolution + retire Do/Get overlay

**Linear:** [AST-1221](https://linear.app/astralcareermatch/issue/AST-1221/runtime-alias-resolution-retire-doget-overlay-task-config-aliases-via)
**Parent:** [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key) — Task config aliases via master_task_key
**Publish ref:** `origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`

After **AST-1220**: honor `master_task_key` → master resolution wherever prompts / shared agent_task content are loaded; run alias dispatch keys (`meteorite_grade_do` / `meteorite_grade_get`) with **alias-owned** `TASK_CONFIG` orchestration (pass/fail/error); remove `METEORITE_GDL_OUTCOME_BY_TASK` (symbol + consult overlay read path). Does **not** author the config contract (**AST-1220**), seed/retarget meteorite dispatch or `agent_task` rows (**AST-1222**), or own UI hardcode audit (**AST-1185**).

**Depends on AST-1220 (User Testing):** `is_task_alias` / `resolve_task_key_for_content`, alias `TASK_CONFIG` entries, empty overlay dict. Build expects those on the epic tree via `sync-child` merging `origin/ftr/AST-1184-…` once Chuckles lands AST-1220. If helpers are missing at Stage 1 start → stop, comment on parent, wait — do not re-implement the contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Resolve prompt/`agent_task` fetch via `resolve_task_key_for_content`; keep caller `task_key` as identity; Style D detail when alias resolves; `_is_strict_encoded_batch_consult` for both strict-envelope gate sites | core |
| `src/core/consult.py` | Retire overlay read; alias-aware scored Do/Get dispatch routing; header lookup via master resolve | core |
| `src/core/dispatcher.py` | Add alias keys to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` | core |
| `src/utils/config.py` | Delete `METEORITE_GDL_OUTCOME_BY_TASK` symbol + its value∈`JOB_STATES` assert loop | utils |

**No changes expected:** `data/admin/agent_task.json`, `METEORITE_DISPATCH_TASKS` / `SEED_CONFIG` meteorite SQL (still `grade_do` / `grade_get` until **AST-1222**), frontend, `tests/` / bible (Betty after Code Complete).

## Stage 1: Agent — prompt content resolve + debug detail

**Done when:** `_resolve_task_prompts` loads `agent_task` / `agent` rows for `resolve_task_key_for_content(task_key)` while `do_task` / preview still key storage, context, and `TASK_CONFIG` orchestration off the caller `task_key`; when `debug=True` and the key is an alias, Style D detail shows alias → master; `meteorite_grade_do` / `meteorite_grade_get` participate in the strict encoded-batch envelope gate; `python3 -m py_compile src/core/agent.py` succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/core/agent.py`, extend the existing config import (near other `TASK_CONFIG` helpers) to include `resolve_task_key_for_content` and `is_task_alias`.

2. Replace `_resolve_task_prompts` so content lookup uses the resolved master; keep the parameter name `task_key` as the **caller identity** (alias or master) for error messages that name the requested key:

```python
def _resolve_task_prompts(task_key: str):
    """Fetch and validate agent_task + agent rows for prompt/content lookup.

    Alias keys resolve to master_task_key for DB rows (AST-1221); caller identity
    stays the original task_key at do_task / preview call sites.
    """
    content_key = resolve_task_key_for_content(task_key)
    agent_task_row = get_agent_task(content_key)
    if not agent_task_row:
        raise ValueError(
            f"No agent_task row for '{content_key}'"
            + (f" (alias '{task_key}')" if content_key != (task_key or "").strip() else "")
            + ". Run sync_agent_tasks or configure via Manage Tasks."
        )
    agent_id = (agent_task_row.get("agent_id") or "").strip()
    if not agent_id:
        raise ValueError(
            f"agent_task '{content_key}' has no agent_id assigned. Configure via Manage Tasks."
        )
    agent_row = get_agent(agent_id)
    if not agent_row:
        raise ValueError(
            f"Agent '{agent_id}' referenced by task '{content_key}' not found."
        )
    return agent_row, agent_task_row
```

⚠️ **Decision — content resolve at `_resolve_task_prompts` only (prompt fetch):** Parent requires master's prompts/content with no alias prompt override; alias remains the identity operators see. `do_task` continues `TASK_CONFIG.get(task_key)` for schema / scored flags / `requires_candidate_key` (alias entries already carry those per **AST-1220** Radia advisory — do **not** invent a field-merge from master). `preview_prompt` / `simulated_chain_context_for_preview` inherit resolve automatically via `_resolve_task_prompts`.

⚠️ **Decision — `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` stay on caller identity:** These also call `get_agent_task`, but they are **not** prompt-content lookups — they read `run_next` / chain-parent identity (`astral.dispatch.run-next-is-chain-authority`). Leave them keyed on the raw `task_key`. Safe today (aliases have no `agent_task` row until **AST-1222**) and safe after **AST-1222** seeds grouping-only alias rows with no `run_next` (Do/Get have no chain; `get_agent_task(alias)` returning a grouping row with empty `run_next` yields `""`, same as today). Do **not** resolve these to master — that would silently attribute the master's `run_next` to the alias. Document only; no code change at those two sites on this ticket.

3. In `do_task`, immediately after the successful `TASK_CONFIG` lookup (and before `_resolve_task_prompts`), when `debug` is True and `is_task_alias(task_key)`:

```python
    if debug and is_task_alias(task_key):
        logger.set_debug_flag(True)
        master = resolve_task_key_for_content(task_key)
        logger.debug_index(
            func=f"do_task({task_key})",
            index=1,
            total=1,
            identifier=index or task_key,
            outcome="alias_resolve",
        )
        logger.debug_detail(
            f"alias={task_key} content_master={master} "
            f"orchestration=TASK_CONFIG[{task_key}] prompts=agent_task[{master}]"
        )
```

⚠️ **Decision — Style D only when `debug=True`:** Matches `astral.standards.debug-contract-gated`. No new ungated INFO noise. Index header uses the **alias** identity; detail names the master.

4. Strict encoded-batch gate — membership is tested in **two** places today (`do_task` ~line 2468 sets `strict_batch = task_key in _STRICT_ENCODED_BATCH_CONSULT_KEYS`, then only calls `_strict_encoded_batch_consult_envelope_err` when `strict_batch`). Resolving only inside the helper leaves aliases with `strict_batch=False` (helper never called; no `agent_performance` back-fill). Introduce one membership helper and use it in both places:

```python
def _is_strict_encoded_batch_consult(task_key: str) -> bool:
    """True when task_key (or its content master) is in the strict encoded-batch set."""
    return resolve_task_key_for_content(task_key) in _STRICT_ENCODED_BATCH_CONSULT_KEYS


def _strict_encoded_batch_consult_envelope_err(task_key: str, parsed: Any) -> Optional[str]:
    """Return error detail if encoded-batch consult response bypasses envelope rules; otherwise None."""
    if not _is_strict_encoded_batch_consult(task_key) or parsed is None:
        return None
    # ... remainder unchanged (same checks as today) ...
```

In `do_task` (~line 2468), replace the direct frozenset membership with the helper:

```python
    strict_batch = _is_strict_encoded_batch_consult(task_key)
```

Leave the subsequent `if strict_batch … agent_performance` back-fill and both `envelope_err = _strict_encoded_batch_consult_envelope_err(...)` calls unchanged — they already key off `strict_batch`.

⚠️ **Decision — one membership helper, both call sites:** `astral.standards.dry-and-focused-functions`. Do **not** add `meteorite_grade_do` / `meteorite_grade_get` literals to `_STRICT_ENCODED_BATCH_CONSULT_KEYS` — resolve covers them. Leave the frozenset body as masters + existing twins (`meteorite_like`, etc.).

5. Verify:

```bash
~/astral/.venv/bin/python -c "
from src.utils.config import resolve_task_key_for_content, is_task_alias
from src.core.agent import _is_strict_encoded_batch_consult
assert is_task_alias('meteorite_grade_do')
assert resolve_task_key_for_content('meteorite_grade_do') == 'grade_do'
assert resolve_task_key_for_content('grade_do') == 'grade_do'
assert _is_strict_encoded_batch_consult('meteorite_grade_do') is True
assert _is_strict_encoded_batch_consult('meteorite_grade_get') is True
assert _is_strict_encoded_batch_consult('grade_do') is True
assert _is_strict_encoded_batch_consult('prefilter_company') is False
"
~/astral/.venv/bin/python -m py_compile src/core/agent.py
```

**Ritual:** `code(AST-1221): agent prompt resolve via master_task_key`

## Stage 2: Consult — retire overlay + alias Do/Get dispatch routing

**Done when:** `METEORITE_GDL_OUTCOME_BY_TASK` is not imported or read in consult; `_consult_orchestration_for_entity` returns the alias/master `TASK_CONFIG` row with no entity-state overlay; `run_consult_task` / `_consult_scored_dispatch_batch_encoded` accept `meteorite_grade_do` / `meteorite_grade_get` and use alias orchestration + header via master resolve; classic `grade_do` / `grade_get` paths unchanged.

1. In `src/core/consult.py` imports from `src.utils.config`, **remove** `METEORITE_GDL_OUTCOME_BY_TASK`. Add `resolve_task_key_for_content` and `is_task_alias`.

2. Replace `_consult_orchestration_for_entity` (keep the name and `entity_state` parameter so call sites stay stable):

```python
def _consult_orchestration_for_entity(task_key: str, entity_state: Optional[str] = None) -> Dict[str, Any]:
    """TASK_CONFIG orchestration for dispatch/catalog task_key.

    AST-1221: meteorite Do/Get outcomes live on alias TASK_CONFIG entries
    (meteorite_grade_do / meteorite_grade_get). No METEORITE_GDL_OUTCOME_BY_TASK overlay.
    entity_state retained for call-site compatibility; unused.
    """
    return dict(_consult_orchestration(task_key))
```

Keep `_entity_state_is_meteorite` — still used by `_format_analysis_phase_text` (Analysis-JD meteorite override), unrelated to the Do/Get overlay.

3. Update the `evaluate_meteorite_batch` docstring to drop the “no METEORITE_GDL_OUTCOME_BY_TASK overlay needed” phrasing — say standalone twin with own `TASK_CONFIG` pass/fail/error (same pattern as `meteorite_like_batch` / alias Do/Get).

4. In `_consult_scored_dispatch_batch_encoded`, replace the header lookup:

```python
    hdr = _GRADE_DISPATCH_TO_HEADER.get(dispatch_task_key)
    if hdr is None:
        hdr = _GRADE_DISPATCH_TO_HEADER[resolve_task_key_for_content(dispatch_task_key)]
```

⚠️ **Decision — do not add alias keys to `_GRADE_DISPATCH_TO_HEADER`:** Field-driven via `resolve_task_key_for_content` → existing master entries (`grade_do`→`DO`, `grade_get`→`GET`). Avoids a parallel meteorite-only header map (`astral.standards.no-hardcoded-sets`). Leave `meteorite_like` in the map (twin, not an alias).

5. In `run_consult_task`, expand the scored grade branch so alias Do/Get keys route like masters. Replace the current `elif task_key in ("grade_do", "grade_get", "grade_like", "meteorite_like"):` block with:

```python
    elif (
        task_key in ("grade_do", "grade_get", "grade_like", "meteorite_like")
        or (
            is_task_alias(task_key)
            and resolve_task_key_for_content(task_key) in ("grade_do", "grade_get")
        )
    ):
        if len(entities) == 1:
            aid = entities[0]["astral_job_id"]
            orch = _consult_orchestration_for_entity(task_key, entities[0].get("state"))
            rv = await render_verdict(task_key, aid, ctx=ctx, debug=debug)
            if rv.get("success"):
                passed = 1 if rv.get("to_state") == orch.get("pass_state") else 0
                return {"total_processed": 1, "total_passed": passed, "total_failed": 1 - passed, "total_errors": 0}
            return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1}
        if task_key in ("grade_do", "grade_get", "grade_like", "meteorite_like"):
            _batch = {
                "grade_do": grade_do_batch,
                "grade_get": grade_get_batch,
                "grade_like": grade_like_batch,
                "meteorite_like": meteorite_like_batch,
            }[task_key]
            r = await _batch(batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index)
        else:
            # Alias Do/Get — same encoded path; dispatch_task_key is the alias identity.
            r = await _consult_scored_dispatch_batch_encoded(
                task_key, batch_id, entities, ctx=ctx, debug=debug, batch_chunk_index=batch_chunk_index,
            )
```

⚠️ **Decision — no thin `meteorite_grade_*_batch` wrappers:** Call `_consult_scored_dispatch_batch_encoded` directly for aliases (same pattern body as the thin wrappers would have). Masters keep existing wrappers. Do **not** retarget `METEORITE_DISPATCH_TASKS` here (**AST-1222**).

6. Verify:

```bash
~/astral/.venv/bin/python -c "
import ast, pathlib
src = pathlib.Path('src/core/consult.py').read_text()
assert 'METEORITE_GDL_OUTCOME_BY_TASK' not in src
from src.core.consult import _consult_orchestration_for_entity, _GRADE_DISPATCH_TO_HEADER
from src.utils.config import resolve_task_key_for_content
orch = _consult_orchestration_for_entity('meteorite_grade_do', 'METEORITE_PASSED_JD')
assert orch['pass_state'] == 'METEORITE_PASSED_DO'
assert orch['fail_state'] == 'METEORITE_FAILED_DO'
# classic Gaze unchanged
gaze = _consult_orchestration_for_entity('grade_do', 'PASSED_JD')
assert gaze['pass_state'] == 'PASSED_DO'
assert _GRADE_DISPATCH_TO_HEADER.get('meteorite_grade_do') is None
assert _GRADE_DISPATCH_TO_HEADER[resolve_task_key_for_content('meteorite_grade_do')] == 'DO'
"
~/astral/.venv/bin/python -m py_compile src/core/consult.py
```

**Ritual:** `code(AST-1221): consult retire Do/Get overlay + alias routing`

## Stage 3: Dispatcher exhaust set + delete overlay symbol

**Done when:** `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` includes `meteorite_grade_do` / `meteorite_grade_get`; `METEORITE_GDL_OUTCOME_BY_TASK` is gone from `config.py` (no empty dict left); no remaining product imports of that name under `src/`; compile clean.

1. In `src/core/dispatcher.py`, add the two alias keys to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` next to `grade_do` / `grade_get`:

```python
_CHUNK_EXHAUST_CONSULT_JOB_KEYS = frozenset({
    "qualify_job_listings",
    "qualify_meteorite",
    "evaluate_jd",
    "grade_do",
    "grade_get",
    "grade_like",
    "meteorite_like",
    "meteorite_grade_do",
    "meteorite_grade_get",
})
```

⚠️ **Decision — explicit frozenset membership (not resolve-at-runtime):** Matches how `meteorite_like` and Ada’s `_DISPATCH_BATCH_CALL_MODE_ONE` list alias keys. Exhaust eligibility is a closed dispatch set, not prompt content.

2. In `src/utils/config.py`, **delete** the `METEORITE_GDL_OUTCOME_BY_TASK` assignment and the assert that iterates `METEORITE_GDL_OUTCOME_BY_TASK.values()`. Keep `assert all(e["trigger_state"] in JOB_STATES for e in METEORITE_DISPATCH_TASKS)`.

Rewrite any residual comments that still describe a live Do/Get overlay — point at alias `TASK_CONFIG` entries + **AST-1221** retirement. Leave **AST-1220** comments on the alias entries that say consult resolve is AST-1221 as historical context, or shorten to “consult uses alias TASK_CONFIG outcomes”.

3. Repo grep gate (product tree only):

```bash
rg -n 'METEORITE_GDL_OUTCOME_BY_TASK' src/ && echo 'FAIL: symbol still referenced' || echo 'ok: no src references'
~/astral/.venv/bin/python -c "from src.utils import config as c; assert not hasattr(c, 'METEORITE_GDL_OUTCOME_BY_TASK')"
~/astral/.venv/bin/python -m py_compile src/utils/config.py src/core/consult.py src/core/dispatcher.py src/core/agent.py
```

⚠️ **Decision — delete the symbol, do not leave `{}`:** Parent + **AST-1220** excluded list assign deletion / consult import removal to this ticket. Tests/bible that still import the name are Betty’s after Code Complete — engineers do not patch `tests/`.

**QA note (ftr-internal):** Until **AST-1222** retargets `METEORITE_DISPATCH_TASKS` to alias keys, live meteorite Do/Get rows still claim as `grade_do` / `grade_get` and therefore use classic Gaze `TASK_CONFIG` outcomes (overlay gone). Do not exercise meteorite Do/Get as operator-safe until **AST-1222** lands (or full ftr rollup). Classic Gaze Do/Get at `PASSED_JD` / `PASSED_DO` must keep working.

**Ritual:** `code(AST-1221): delete METEORITE_GDL_OUTCOME_BY_TASK + alias exhaust keys`

## Self-Assessment

**Scope:** Single-Component — core agent/consult/dispatcher plus deleting one utils overlay symbol; no seed/UI.

**Conf:** high — **AST-1220** helpers and alias entries are shipped; overlay call site is a single function; prompt-content resolve is one choke point (`_resolve_task_prompts`) with chain/`run_next` readers intentionally caller-keyed; strict-envelope membership is one helper used at both gate sites; alias dispatch routing mirrors `meteorite_like` / resolve patterns already in-tree.

**Risk:** Medium — removing the overlay before **AST-1222** retarget means in-flight shared-key meteorite Do/Get temporarily use Gaze outcomes (accepted epic sequencing); wrong resolve would pull prompts from the wrong `agent_task` row or mis-route alias pass/fail once aliases are dispatched.

## Code rules check

- §1.3 DRY — one prompt-content resolve choke point; one `_is_strict_encoded_batch_consult` membership test for both gate sites; no duplicated alias→master maps in core.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new meteorite-only overlay; header via `resolve_task_key_for_content`; strict-envelope gate via resolve; exhaust frozenset lists domain keys (same pattern as existing twins).
- §1.5.1 / `astral.standards.debug-contract-gated` — alias resolve detail only when `debug=True`, Style D index + detail.
- §2.2 / `astral.agent.do-task-delegation` — alias invocation still goes through `do_task`; prompts from master’s `agent_task`.
- `astral.dispatch.run-next-is-chain-authority` — `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` stay on caller identity (no master resolve for chain authority).
- §3.3 / `pattern.layers.import-discipline` — core imports resolve helpers from utils; no reverse imports; no UI edits.
- `astral.standards.in-scope-only` — no seed/dispatch retarget (**AST-1222**), no config contract authorship (**AST-1220**), no UI audit (**AST-1185**).
- `astral.git.engineer-test-tree-ban` — no `tests/` / bible edits on this ticket.

## Revisions

### Revision 1 — 2026-08-06

Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ tip `fd46f3e6`).

Changes:

- **fix-now:** Stage 1 step 4 — add `_is_strict_encoded_batch_consult` wrapping `resolve_task_key_for_content(task_key) in _STRICT_ENCODED_BATCH_CONSULT_KEYS`; use it at `do_task` ~2468 (`strict_batch = …`) and at the top of `_strict_encoded_batch_consult_envelope_err` so aliases get `agent_performance` back-fill and envelope checks (not dead code).
- **discuss:** Document that `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` intentionally stay on caller identity (grouping-only alias rows, no `run_next`); stop claiming a single choke point for all `get_agent_task` reads.
- **Self-assessment / code-rules:** Conf justification and §1.3 / `run-next-is-chain-authority` notes updated to match.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`
**Plan path:** `docs/features/meteorite/ast-1221-runtime-alias-resolution-retire-do-get-overlay.md`

**Built tip:** `41c690642981dd66513285c37f120c77d919baa5` (`41c69064`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `3a606df4` | agent prompt resolve via master_task_key |
| 2 | `fe2a44df` | consult retire Do/Get overlay + alias routing |
| 3 | `41c69064` | delete METEORITE_GDL_OUTCOME_BY_TASK + alias exhaust keys |

## Radia review — [code-rubric] revision=1

**Rubric:** code-rubric.v1 · **Publish ref tip:** `49c0cb65`

**Overall: CLEAN**

**What's solid:**

- All three stages match the plan's binding code blocks verbatim, including the Revision 1 fix that closed Joan's round-1 fix-now: `_is_strict_encoded_batch_consult` wraps `resolve_task_key_for_content(...) in _STRICT_ENCODED_BATCH_CONSULT_KEYS` and is used at **both** membership sites (`agent.py` helper guard + `do_task`'s `strict_batch = …` line) — re-grepped `agent.py` and confirmed exactly two call sites, no third caller left on the unresolved key.
- `_parent_hop_task_key_for_child` / `_current_agent_task_run_next` are untouched in the diff — chain-authority identity stays caller-keyed as the plan's Decision requires (`astral.dispatch.run-next-is-chain-authority` intact, no shadow `run_next` inference for aliases).
- `_consult_orchestration_for_entity` is now a one-line pass-through (`entity_state` kept for call-site stability, documented unused); the entity-state overlay branch is gone, not just emptied.
- Header lookup (`_GRADE_DISPATCH_TO_HEADER`) resolves through `resolve_task_key_for_content` on miss rather than adding alias keys to the map — no new meteorite-only dict (`astral.standards.no-hardcoded-sets` holds). `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` alias literals match the existing explicit-membership precedent (`_DISPATCH_BATCH_CALL_MODE_ONE`), consistent with Joan's verified precedent check.
- `run_consult_task`'s alias branch guards the `_batch = {...}[task_key]` dict dispatch with the masters-only tuple before falling to the alias `else` — no `KeyError` risk for `meteorite_grade_do`/`get`.
- Style D alias→master debug block in `do_task` matches the file's own established shape (`_debug_conversational_turn`'s `debug_index(func=, index=1, total=1, identifier=, outcome=)` + `debug_detail(...)`), gated strictly on `debug and is_task_alias(task_key)` — no ungated noise.
- Repo grep gate is fully clean at tip: zero `METEORITE_GDL_OUTCOME_BY_TASK` references anywhere under `src/` (stricter than Joan's round-1 prediction that a couple of comments would survive) — symbol, import, docstring, and overlay/assert body are all gone, not just emptied.
- Commit hygiene: three `code(AST-1221)` commits touch only `src/core/{agent,consult,dispatcher}.py` + `src/utils/config.py`; `docs(AST-1221)` touches only the plan doc; `test(AST-1221)`/`merge-tests(AST-1221)` touch only `tests/`/`docs/test-bible/**` — `astral.git.engineer-test-tree-ban` and `astral.git.betty-no-src-or-features` both hold.
- No new imports cross a layer boundary — `agent.py`/`consult.py` add only `resolve_task_key_for_content`/`is_task_alias` from `src.utils.config` (core→utils, allowed).
- `python3 -m py_compile src/utils/config.py src/core/consult.py src/core/dispatcher.py src/core/agent.py` clean at tip.
- Full active-set sweep (65 active statutes: 18 universal + 41 scoped-applicable against this diff's `{core, utils, docs}` layers / `src/core/{agent,consult,dispatcher}.py`, `src/utils/config.py`, `docs/features/**`, `docs/test-bible/**`, `tests/**` paths) — zero `violates`, zero `needs-discussion`.

**Note:** this three-dot diff (`origin/dev...origin/sub/AST-1184/AST-1221-...`) also carries AST-1220's already-reviewed changes (merged onto this branch via `origin/ftr/AST-1184-...` per `orch.git.merge-on-checkout`, since AST-1220 hasn't landed on `dev` yet). AST-1220 was independently reviewed clean (Review Posted); this review's findings focus on AST-1221's own commits (`agent.py`, `consult.py`, `dispatcher.py`, and the `config.py` overlay-symbol deletion).

**Pattern conformance:** `pattern.layers.import-discipline` — conforms (core→utils only, no reverse imports). `astral.patterns.render-verdict-orchestrates-consult` / `astral.patterns.coat-check-never-store-empty` — conforms (untouched by this diff).

**Plan adherence:** All three stages match the plan's binding code blocks exactly, including both Revision 1 items (strict-envelope helper at both sites; documented caller-identity carve-out for the two `run_next` readers).

## Frame diff

(none — ticket description/AC unchanged; no findings to fold in)

context_tokens≈78000

— Radia

## Resolution — 2026-08-06

**Review tip:** `864e58c1` (`docs(AST-1221): Radia review — clean`) — Overall **CLEAN**.

- **fix-now:** none.
- **Discuss:** none requiring product change.
- **Advisory:** none.
- **Product / plan code:** unchanged this pass (resolve clean).
