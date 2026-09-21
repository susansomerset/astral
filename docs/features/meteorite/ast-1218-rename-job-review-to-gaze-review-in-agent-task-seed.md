<!-- linear-archive: AST-1218 archived 2026-08-17 -->

## Linear archive (AST-1218)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1218/rename-job-review-to-gaze-review-in-agent-task-seed-gaze-review-rename  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1183 — Gaze Review rename + Meteorite Review sibling + agent_task grouping  
**Blocked by / blocks / related:** parent: AST-1183; blocks: AST-1219

### Description

## What this implements

Owns the section rename for rows that remain classic gaze/GDL under the old Job Review group: set `task_group_name` to **Gaze Review** (retain existing `task_group_order` `4000`), and surgically sync AST-756 fixture rows for those classic keys. Does **not** create Meteorite Review or move meteorite rows (sibling **AST-1219**). Does **not** touch aliases or UI hardcode audit.

## In scope

- [X] `astral.seed.agent-tables-in-repo-json` — classic `agent_task` rows rename in repo JSON (`data/admin/agent_task.json`)
- [X] `astral.standards.names-not-ticket-ids` — product section label **Gaze Review**
- [X] `astral.standards.in-scope-only` — classic rename only; meteorite move / aliases / UI audit out
- [X] `astral.standards.no-hardcoded-sets` — no parallel hard-coded Gaze/Job Review membership lists in `src/`
- [X] `astral.git.engineer-test-tree-ban` — no engineer edits under `tests/` / `docs/test-bible/**` (Betty after Code Complete)

## Considered but excluded

- [X] Meteorite Review group + move meteorite `agent_task` rows — **AST-1219**
- [X] `master_task_key` / task aliases — **AST-1184**
- [X] UI hardcode / alphabetical dropdown audit — **AST-1185**
- [X] `parse_meteorite_email` → `meteorite_email` rename — **AST-1182** / **AST-1212** (already live as `meteorite_email`)
- [X] evaluate_meteorite test/statute fold-in — **AST-1186**
- [X] Blind whole-file AST-756 `cp` — would overwrite pre-existing non-AST-1211 prompt drift; surgical classic-row label edits only
- [X] Reconciling catalog↔fixture prompt inequality outside AST-1211 keys — out of scope (13 unequal rows on tip including `meteorite_like`)
- [X] Closing or reopening `TestAst1211EvaluateCraftFixtureLockstep` — already satisfied post-`sync-child` / `origin/dev`; not this child’s job
- [X] Renaming meteorite-track rows off Job Review in this child — would invent Meteorite Review early or park them under Gaze Review

## Acceptance criteria

- [X] No current classic gaze/GDL `agent_task` seed row still uses `task_group_name` **Job Review** (sibling #2 owns meteorite-row moves).
- [X] Classic gaze/GDL tasks listed under parent Functional scope show `task_group_name` **Gaze Review** with shared section order `4000`.
- [X] Repo seed and locked AST-756 fixture rows for those classic keys match **Gaze Review**.

## Boundaries

* Does **not** create Meteorite Review or move meteorite rows (sibling #2).
* Does **not** touch aliases (**AST-1184**) or UI hardcode audit (**AST-1185**).
* Does **not** rename `parse_meteorite_email` (**AST-1182**).

## Notes for planning

Parent confirmed Open questions: membership and order `4000`/`4500` approved. Live seed keys: classic frozenset under Job Review today; meteorite frozenset includes `meteorite_email` (not `parse_meteorite_email`).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1183-gaze-review-rename-meteorite-review-sibling`, child `sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-06T07:39:03.511Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`2774498f Merge remote-tracking branch 'origin/dev' into sub/AST-1183/AST-1218-…` fails `validate-sub-log.sh`. @Ada Lovelace — rewrite publish tip without that pull-merge (stack via `sync-child` / merge `origin/ftr/AST-1183-gaze-review-rename-meteorite-review-sibling`, preserve plan/code/merge-tests/test/docs/resolve sequence), force-with-lease push, then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-08-06T07:36:07.129Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1218
**Publish ref:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `017e345d`
**Overall:** CLEAN

## Plan adherence

- Diff matches Stage 1 exactly: nine classic `agent_task` rows → `task_group_name: "Gaze Review"` (order still `"4000"`) in both `data/admin/agent_task.json` and the AST-756 fixture; the six meteorite-track rows are verified unchanged (still `Job Review`).
- Self-Assessment (`minor` / `Medium` / `low`) matches the actual footprint — two JSON files, zero `src/**` touched.
- `astral.git.engineer-test-tree-ban` respected: `tests/` + `docs/test-bible/` changes landed via Betty's `test(AST-1218)` → `merge-tests(AST-1218)` commits, not the engineer's `code(AST-1218)` commit (confirmed via `git log --stat`).

Full-set sweep (65 active statutes: 18 universal + 47 scoped) scored in-session against `git diff origin/dev...origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` — zero violates, zero needs-discussion. 6 scoped statutes matched the diff (`astral.seed.agent-tables-in-repo-json`, `astral.seed.define-approved`, `astral.git.engineer-test-tree-ban`, `astral.git.betty-no-src-or-features`, `astral.docs.features-single-file-per-ticket`, `astral.debug.spikes-under-debug-dir`) — all `conforms`. Remaining 41 scoped statutes `not-applicable` (diff touches only `data/admin/**` and `docs/**`/`tests/**`, no `src/**`). Zero `Job Review`/`Gaze Review` literals under `src/` on this tip.

**Straggler (C4):** Joan plan-rubric verdict attached (revision=1, APPROVED, "18 universal + 10 scoped … all conforms"); slim artifact names no Excluded list to cross-check — no straggler flagged.

## Pattern conformance

none cited

Findings: none.

## Frame diff

(none) — diff footprint matches Description In-scope / Files Changed exactly; no description update needed.

context_tokens≈95000

— Radia

#### betty — 2026-08-06T07:27:49.715Z
## QA test manifest (AST-1218)

**Publish:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `017e345d` (`merge-tests(AST-1218): origin/tests 5ef508c4dfdd3c66409a4637e77c1f08bf7bc3b1`)
**origin/tests SHA:** `5ef508c4`

### Classification

1. **Existing coverage (bible-backed):** meteorite rows stay **Job Review** — `TestAst1060QualifyMeteoriteCatalogRow`, `TestAst1089ParseMeteoriteEmailCatalogRow`, `TestAst1106GazeEmailCatalogRow`; AST-1211 lockstep — `TestAst1211EvaluateCraftFixtureLockstep`.
2. **Broken / obsolete (revised this pass):** `TestAst878FetchCulturePagesCatalogRow` — classic `fetch_culture_pages` `task_group_name` **Job Review** → **Gaze Review**.
3. **Gaps (new this pass):** `TestAst1218GazeReviewClassicGroupLabel` — all nine classic keys **Gaze Review**/`4000`; six meteorite keys **Job Review**/`4000`; no unexpected Gaze Review; fixture label lockstep for classic∪meteorite (label fields only).

**Not in manifest run:** full `TestAst1055MeteoriteCatalogRows` — group-name line still correct; class has pre-existing `meteorite_like` prompt-string drift on `origin/dev` ("more liberally") unrelated to this label rename. Leave for a prompt-owning ticket.

**Integration:** none revised (no existing scenarios assert Job/Gaze Review seed labels).

### Run (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1218GazeReviewClassicGroupLabel \
  tests/component/core/test_repo_admin_json.py::TestAst878FetchCulturePagesCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1106GazeEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1211EvaluateCraftFixtureLockstep \
  -q
```

### Bible shasum (publish tip)

- `docs/test-bible/core/repo_admin_json.md` — `c41f367f440c3a833f5f0a0914a7e482bdb212bd`

— Betty

#### joan — 2026-08-06T07:13:13.108Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1218
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `bc45ba07`
**Considered:** 18 universal + 10 scoped active statutes, all `conforms` (scored in-session; slim artifact per R7)

## Traceability

AC1→S1; AC2→S1; AC3→S1 (single stage; no orphan stage; no unmapped child AC; parent AC on meteorite membership is N/A-boundary per parent child-#1 text).

## Round=2 fix-now cleared — verified by execution, not by reading

I copied both JSON files out of tip `bc45ba07`, applied **only** the edit Stage 1 prescribes (nine classic `task_group_name` → `Gaze Review`, in each file, nothing else), and ran the step-6 script verbatim: **both files ok, `ast-1218 seed checks passed`**. The narrowed `AST1211 = {evaluate_meteorite, craft_evaluate_meteorite_rubric}` equality holds; the `METEORITE ∪ {craft…}` whole-row assertion that failed on `meteorite_like` is gone; `Done when` no longer demands global lockstep and now explicitly puts pre-existing prompt drift out of scope.

I also negative-tested the gate rather than assuming it: renaming `meteorite_like` alongside the classic rows makes the script raise on `('meteorite_like', 'Gaze Review')`, and the "unexpected Gaze Review on non-classic row" loop is meaningful because zero rows carry `Gaze Review` pre-edit. The verify step has teeth in both directions.

## Statute and fidelity notes

All three earlier concerns are closed at the source, not papered over. `orch.pipeline.plan-is-bible` → conforms: every `Done when` predicate is true on the build tree before the edit or made true by the edit itself. `orch.git.merge-on-checkout` → conforms: the Merge base section names `sync-child.sh`, and `origin/dev` is merged into the sub at `2774498f` with the sub now 0 commits behind `origin/dev`. `astral.seed.agent-tables-in-repo-json` → conforms and now matches on the layer predicate directly, since the `Layer` cell reads `data`.

Re-checked at the post-merge tip rather than trusting the earlier pass: still zero `Job Review` / `Gaze Review` literals anywhere under `src/`, so no product code is needed and `astral.standards.no-hardcoded-sets` holds. Across `tests/` and the bible, `TestAst878FetchCulturePagesCatalogRow` is the **only** classic-row `task_group_name` assertion this change breaks — lines asserting `Job Review` for `meteorite_like`, `qualify_meteorite`, `meteorite_email`, and `gaze_email` are all meteorite rows that stay put, and `test_AdminScheduledActions_AST1106.test.tsx` feeds its own mocked `task_group_name` rather than reading the seed, so it is unaffected. The plan names exactly that one test class for Betty at Code Complete, and `orch.roles.betty-owns-test-tree` / `astral.git.engineer-test-tree-ban` are respected — `docs/uat-fixtures/**` is in neither statute's path set, and the AST-1212 precedent (`099007f5`) has an engineer syncing seed + fixture in one commit.

Self-assessment is honest: `Conf` `high` → `Medium` with the specific reason named, which is the right call after two rounds of unverified file-state claims, and this round's assertions were tip-checked before publish.

**acceptable — informational for rollup:** the sub now leads `origin/dev` while `origin/ftr/AST-1183-…` is still behind it. Nothing for this child to do; it just means the ftr rollup happens from the sub side at merge-child.

context_tokens≈72000

— Joan

#### ada — 2026-08-06T07:10:47.945Z
[plan-discuss] round=2 reply

Revised plan on `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `bc45ba07`.

**fix-now (step-6 / Done when over-asserting equality):** Narrowed catalog↔fixture object equality to the AST-1211 pair only (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`). Dropped `METEORITE ∪ {craft…}` whole-row equality. Done when now asserts only: 53 current rows; classic `Gaze Review`/`4000`; meteorite `Job Review`/`4000`; no unexpected `Gaze Review`; AST-1211 pair remains equal. Merge base documents tip truth: **13/53** rows already differ (incl. `meteorite_like`); surgical sync must not “fix” that drift.

**Tip check before publish (on `1c006e77` tree):** AST-1211 keys equal ✓; `meteorite_like` unequal ✓ (old script would fail); simulated classic rename + narrowed step-6 script passes ✓.

**Conf:** `high` → `Medium` (second unverified file-state claim in two rounds; this round’s asserts were tip-checked).

Status left **Plan Discuss** (round cap noted — Joan gates Plan Approved).

#### joan — 2026-08-06T07:07:18.715Z
[plan-discuss] round=2 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1218
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `1c006e77`
**Considered:** 18 universal + 10 scoped active statutes (scored in-session; slim artifact per R7)

## Traceability

AC1→S1; AC2→S1; AC3→S1 (single stage; no orphan stage; parent AC on meteorite membership is N/A-boundary per parent child-#1 text).

## Round=1 items — all cleared

Verified on the new tip, not taken on trust: `origin/dev` is merged into the sub (`2774498f`), both `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` now have **53** current rows with 15 `Job Review` rows each, and `evaluate_meteorite` + `craft_evaluate_meteorite_rubric` are present in both — so `TestAst1211EvaluateCraftFixtureLockstep` is green on the build tree and the round=1 fix-now is genuinely resolved. Merge base section, `Layer` cell `data` (the seed statute now matches on the layer predicate instead of falling through to the `docs` fallback), and removal of the `assert … or True` no-op are all in.

## Findings

**fix-now — the new step-6 verify script asserts catalog↔fixture equality that is false before this child edits anything** (`orch.pipeline.plan-is-bible` → violates)

Stage 1 `Done when` now says *"meteorite-row objects (including `evaluate_meteorite`) remain object-equal between catalog and fixture"*, and step 6 encodes it as:

```python
for k in METEORITE | {"craft_evaluate_meteorite_rubric"}:
    assert cat[k] == fix[k], k
```

On tip `1c006e77`, `meteorite_like` is **not** object-equal between the two files — it differs in `cache_prompt`. Overall **13 of 53** current rows differ (four of them classic: `evaluate_jd`, `grade_do`, `grade_get`, `grade_like`, in `cache_prompt` / `user_prompt`). The two files are lockstep on the two keys AST-1211 actually locks, not globally; the revised script generalized that from two keys to seven.

So the verify gate fails on `AssertionError: meteorite_like` even when the nine classic label edits are performed perfectly. Under `orch.pipeline.plan-is-bible` the next agent's green paths are to copy the catalog `cache_prompt` onto the fixture's `meteorite_like` row — an out-of-scope prompt edit to a meteorite row that this plan's own boundary and AST-1219 both forbid — or to stall. This is the round=1 problem inverted: the premise moved from under-asserting preserved drift to over-asserting lockstep.

**Recommendation:** narrow the equality clause to the two keys AST-1211 locks (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`), which I confirmed are genuinely equal on this tip — or drop whole-object equality entirely and assert only what this child controls: 53 current rows in both files, classic keys `Gaze Review` / `4000` in both, meteorite keys `Job Review` / `4000` in both, and no other `task_group_name` rewritten. Per-field `task_group_name` comparison is safe; whole-row comparison is not. Worth re-checking the `Conf: high` line at the same time — the row counts were verified against the post-sync tip but this assertion was not, and it is the second premise in two rounds to bind build to an unverified file-state claim.

**Note — round cap.** This is round **2** of 2 (`plan-rubric.v1` § Plan Discuss). A further REVISE on the next pass hits the cap and I escalate to @susan instead of opening round 3, so the next revision needs the assertion checked against the actual tip before publishing.

**Verified accurate (no finding):** classic and meteorite frozensets still match the live post-sync seed exactly; `task_group_order` `4000` on every `Job Review` row in both files; `craft_evaluate_meteorite_rubric` present in both; the classic-only edit itself is correct and leaves `TestAst1211EvaluateCraftFixtureLockstep` green with no engineer `tests/` edits; step 5's "do not delete, add, or reshape `evaluate_meteorite` / `craft_evaluate_meteorite_rubric`" is the right guard; zero `Job Review` / `Gaze Review` literals under `src/`; Betty correctly named for the classic `TestAst878FetchCulturePagesCatalogRow` assertion flip; commit ritual and publish ref match the parent Git table. Scope `minor` / Risk `low` remain honest.

context_tokens≈60000

— Joan

#### ada — 2026-08-06T07:04:45.928Z
[plan-discuss] round=1 reply

Revised plan on `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `1c006e77`.

**fix-now (Done when / surgical sync vs TestAst1211):** Dropped the stale “fixture differs by missing `evaluate_meteorite`” premise. Added **Merge base (build inventory)** — counts bind to post-`sync-child` tip (merge `origin/dev`, then `origin/ftr/AST-1183-…` when published). Post-sync both JSON files are lockstep at **53** current rows with `evaluate_meteorite` / `craft_evaluate_meteorite_rubric` present (AST-1211 already closed). Stage 1 only rewrites the nine classic `task_group_name` values; does not reopen lockstep. `TestAst1211EvaluateCraftFixtureLockstep` is satisfied by that post-sync baseline — not this child’s close-out. Betty still owns classic Job Review → Gaze Review assertion updates at Code Complete.

**discuss (merge base):** Named explicitly: plan inventory / build edits assume `sync-child.sh` already attached `origin/dev` (+ ftr when present). No second merge ritual in Stage 1.

**discuss (Layer cell):** `data/admin` → `data` so seed statute layer matching is not falsely excluded.

**acceptable (verify script):** Removed `assert … or True`; both paths now require all meteorite keys, `len==53`, and meteorite-row object equality catalog↔fixture.

Status left **Plan Discuss** (Joan gates Plan Approved).

#### joan — 2026-08-06T07:01:09.388Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1218
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `6b410fc6`
**Considered:** 18 universal + 10 scoped active statutes (scored in-session; slim artifact per R7)

## Traceability

AC1→S1; AC2→S1; AC3→S1 (single stage; no orphan stage; parent AC on meteorite membership is N/A-boundary per parent child-#1 text "Does **not** create Meteorite Review or move meteorite rows (sibling #2)").

## Findings

**fix-now — Stage 1 `Done when` + "surgical fixture sync" decision contradict a landed test on this very tree** (`orch.pipeline.plan-is-bible` → violates)

The plan requires preserving the fixture drift: *"fixture vs catalog still differ only by the pre-existing missing `evaluate_meteorite`"* and step 5 *"Do not add missing `evaluate_meteorite` … to close pre-existing drift."*

But `tests/component/core/test_repo_admin_json.py::TestAst1211EvaluateCraftFixtureLockstep::test_fixture_includes_two_keys_object_equal_to_catalog` is present on this sub **and** on `origin/ftr/AST-1183-…`, and it asserts `len(fix) == 53` plus `evaluate_meteorite in fix`. The fixture on both refs has **51** current rows and no `evaluate_meteorite`, so that assertion cannot hold on the build tree — it is red before AST-1218 changes anything. AST-1211's fixture commit `ef4b8878` landed on `origin/dev` (fixture there: 53 current / 15 Job Review, `evaluate_meteorite` present) but `origin/ftr/AST-1183-…` is **26 commits behind** `origin/dev`, so `orch.git.merge-on-checkout` (merge the parent `ftr` tip) does not bring it.

Under `orch.pipeline.plan-is-bible` the plan text is binding, so at Code Complete / test-child the engineer faces a red test whose only green paths are (a) adding `evaluate_meteorite` to the fixture — which the plan forbids — or (b) merging `origin/dev`, after which the `Done when` drift clause becomes false because the two files no longer differ at all. Either way the binding text sends the next agent to improvise.

**Recommendation:** state the intended resolution explicitly rather than pinning the premise to the stale tip — drop or condition the "differ only by missing `evaluate_meteorite`" clause so it holds at 51 **and** 53 rows, and name who closes the `TestAst1211…` lockstep expectation (the `origin/dev` merge at resolve §9a bringing `ef4b8878`, or Betty at Code Complete). The classic-key edit itself needs no change: `evaluate_meteorite` is a meteorite row that stays `Job Review` in both files, so AST-1211's object-equality assertion survives this child either way.

**discuss — no merge base declared** (`orch.git.merge-on-checkout` → needs-discussion). The plan's file-state inventory was measured on the stale sub tip. Naming the merge step (`git merge origin/ftr/AST-1183-…`) and whether an `origin/dev` merge is expected would make the row counts in the plan verifiable at build time.

**discuss — Files Changed `Layer` cell `data/admin` is not a statute layer enum value.** Under plan-rubric.v1 § Matching algorithm step 1 an unrecognized layer falls back to `docs`, which mechanically excludes `astral.seed.agent-tables-in-repo-json` (layers `core`/`data`/`utils`) by the layer predicate even though the path `data/admin/**` matches. I considered the seed statutes on merit anyway (parent cites them; all conform). Writing the cell as `data` avoids the false exclusion for the next reader.

**acceptable — verify script tail.** The trailing `assert … or True` in step 6 is a no-op; the fixture check itself (`require_all_meteorite=False`) is correct and holds at both row counts.

**Verified accurate (no finding):** the classic and meteorite frozensets exactly match the live seed (15 current `Job Review` rows = 9 classic + 6 meteorite); `task_group_order` `4000` confirmed on every `Job Review` row; the cited `TestAst878FetchCulturePagesCatalogRow` exists and does assert `Job Review` for a classic row; there are **zero** `Job Review` / `Gaze Review` string literals anywhere under `src/`, so the no-hardcoded-sets citation holds and no product code is needed for the label; and the AST-1212 precedent for an engineer syncing seed + AST-756 fixture in one commit is real (`099007f5` touches both files). Self-assessment `minor` / `high` / `low` is honest for the change as scoped.

context_tokens≈46000

— Joan

#### ada — 2026-08-06T06:54:51.859Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed/docs/features/meteorite/ast-1218-rename-job-review-to-gaze-review-in-agent-task-seed.md

`origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `6b410fc64893a50aac3d85e43f0ff870af14a5ae`

**Scope:** minor — two JSON files; `task_group_name` on nine classic current rows (+ matching AST-756 fixture rows); no `src/`.

**Conf:** high — exact classic/meteorite frozensets from parent Functional scope match live seed; Archie approved `4000`/`4500`; same surgical seed/fixture pattern as AST-1212.

**Risk:** low — grouping label only; meteorite rows stay Job Review until AST-1219; dispatch/prompts/`run_next` untouched.

---

# AST-1218 — Rename Job Review to Gaze Review in agent_task seed

**Linear:** [AST-1218](https://linear.app/astralcareermatch/issue/AST-1218/rename-job-review-to-gaze-review-in-agent-task-seed-gaze-review-rename)
**Parent:** [AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping) — Gaze Review rename + Meteorite Review sibling + agent_task grouping
**Publish ref:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed`

Rename the classic gaze/GDL `agent_task` section label from **Job Review** to **Gaze Review** in repo seed (and the locked AST-756 fixture rows for those same keys). Retain shared `task_group_order` **`4000`**. Leave meteorite-track rows on **Job Review** for sibling **AST-1219**. Does **not** create Meteorite Review, move meteorite membership, touch aliases (**AST-1184**), UI hardcode audit (**AST-1185**), or `meteorite_email` rename (**AST-1182** / already landed as `meteorite_email`).

## Merge base (build inventory)

Before measuring or editing seed/fixture, **`sync-child.sh`** on this publish ref has already run (plan-child / build-child): fetch → checkout publish ref → merge **`origin/dev`** → merge **`origin/ftr/AST-1183-…`** when that ref exists on origin → merge **`origin/<publish-ref>`**. File counts and lockstep below are **post-sync**. Do not invent a second merge ritual in Stage 1.

Post-sync baseline (verified on tip after `origin/dev` attach): both `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` have **53** current rows; both include `evaluate_meteorite` and `craft_evaluate_meteorite_rubric`, and those **two** keys are object-equal catalog↔fixture (AST-1211 lockstep). The two files are **not** globally object-equal — on tip `1c006e77`, **13 of 53** current rows differ (including `meteorite_like.cache_prompt` and several classic prompt fields). This child does **not** reopen or “close” AST-1211 lockstep and does **not** reconcile unrelated prompt drift — classic-label edits only; `TestAst1211EvaluateCraftFixtureLockstep` stays green without engineer `tests/` edits. Betty updates classic **Job Review → Gaze Review** assertions (e.g. `TestAst878FetchCulturePagesCatalogRow`) at Code Complete.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Set `task_group_name` to `Gaze Review` on the nine classic current rows only; keep `task_group_order` `"4000"` and all other fields | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical sync of the same nine classic rows’ `task_group_name` only — **no** whole-file `cp` | docs |

**No changes expected:** `src/**`, frontend, dispatch/config, `tests/` / bible (Betty after Code Complete), meteorite-track seed rows (`gaze_email`, `meteorite_email`, `qualify_meteorite`, `evaluate_meteorite`, `meteorite_like`, `meteorite_upshot`).

## Stage 1: Classic seed rename + surgical AST-756 sync

**Done when:** Every current classic gaze/GDL row listed below has `task_group_name == "Gaze Review"` and `task_group_order == "4000"` in both `data/admin/agent_task.json` and the AST-756 fixture; every current meteorite-track row listed below still has `task_group_name == "Job Review"` and `task_group_order == "4000"`; no non-classic row was given `task_group_name == "Gaze Review"`; JSON remains a flat-row array; both files still have 53 current rows including `evaluate_meteorite` / `craft_evaluate_meteorite_rubric`; the AST-1211 pair (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`) remains object-equal catalog↔fixture. Do **not** require whole-row equality for other meteorite or classic keys (pre-existing prompt drift is out of scope).

**Classic keys (rename to Gaze Review — exact frozenset):**

`gaze`, `qualify_job_listings`, `fetch_jd`, `evaluate_jd`, `grade_do`, `grade_get`, `fetch_culture_pages`, `grade_like`, `analysis_upshot`

**Meteorite keys (leave `task_group_name` as Job Review — exact frozenset):**

`gaze_email`, `meteorite_email`, `qualify_meteorite`, `evaluate_meteorite`, `meteorite_like`, `meteorite_upshot`

1. Snapshot before edit (local `/tmp` only — do not commit):

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1218.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1218.json
```

2. In `data/admin/agent_task.json`, for each object with `current == 1` and `task_key` in the classic frozenset above, set **only**:

   - `task_group_name` → `"Gaze Review"`

   Leave `task_group_order` as `"4000"`. Do **not** change `task_seq`, prompts, `agent_id`, `run_next`, `task_key_uuid`, `task_name`, or any other field. Do **not** bump `updated_at` unless an existing seed tooling path already requires it for apply — prefer leaving timestamps untouched so the diff is the label only.

3. Do **not** edit any row whose `task_key` is in the meteorite frozenset. Those rows must still read `task_group_name: "Job Review"` after this stage.

4. Do **not** invent a `Meteorite Review` label, change any `task_group_order` to `4500`, or reorder `task_seq` values. Sibling **AST-1219** owns that move.

5. In `docs/uat-fixtures/AST-756/expected-agent_task.json`, apply the **same** classic-only `task_group_name` → `"Gaze Review"` edits for matching `current == 1` rows. Surgical per-row edits only — **no** `cp data/admin/agent_task.json docs/uat-fixtures/...`. Do **not** delete, add, or reshape `evaluate_meteorite` / `craft_evaluate_meteorite_rubric` (or any other non-classic row).

6. Verify with (assert only what this child controls + the two AST-1211 keys — **not** global catalog↔fixture equality):

```bash
python3 - <<'PY'
import json
from pathlib import Path

CLASSIC = {
    "gaze", "qualify_job_listings", "fetch_jd", "evaluate_jd", "grade_do",
    "grade_get", "fetch_culture_pages", "grade_like", "analysis_upshot",
}
METEORITE = {
    "gaze_email", "meteorite_email", "qualify_meteorite", "evaluate_meteorite",
    "meteorite_like", "meteorite_upshot",
}
AST1211 = {"evaluate_meteorite", "craft_evaluate_meteorite_rubric"}

def check(path: str) -> dict:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    by = {r["task_key"]: r for r in rows if r.get("current") == 1}
    assert len(by) == 53, (path, len(by))
    for k in CLASSIC:
        assert k in by, f"{path}: missing classic {k}"
        assert by[k]["task_group_name"] == "Gaze Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4000", (path, k, by[k]["task_group_order"])
    for k in METEORITE:
        assert k in by, f"{path}: missing meteorite {k}"
        assert by[k]["task_group_name"] == "Job Review", (path, k, by[k]["task_group_name"])
        assert by[k]["task_group_order"] == "4000", (path, k, by[k]["task_group_order"])
    for k, r in by.items():
        if k not in CLASSIC and r.get("task_group_name") == "Gaze Review":
            raise AssertionError(f"{path}: unexpected Gaze Review on {k}")
    print("ok", path)
    return by

cat = check("data/admin/agent_task.json")
fix = check("docs/uat-fixtures/AST-756/expected-agent_task.json")
# Only the AST-1211 lockstep keys — not METEORITE ∪ craft (meteorite_like prompts already drift)
for k in AST1211:
    assert cat[k] == fix[k], k
print("ast-1218 seed checks passed")
PY
```

⚠️ **Decision — leave meteorite rows on Job Review:** Child #1 AC is classic rename only. Parent’s “no Job Review remains” AC is the epic rollup after **AST-1219** moves meteorite membership to Meteorite Review. Renaming meteorite rows here would either invent Meteorite Review early or leave them under Gaze Review, both out of scope.

⚠️ **Decision — keep `task_group_order` `4000`:** Parent open questions closed; Archie approved Gaze Review order `4000` and Meteorite Review `4500` for sibling #2. This child retains the existing Job Review order identity as Gaze Review’s section order.

⚠️ **Decision — surgical fixture sync, no whole-file cp:** Post-sync both files have 53 current rows and AST-1211’s two keys are object-equal; other rows may already differ in prompts. Edit only the nine classic `task_group_name` values in each file. A whole-file `cp` would overwrite unrelated fixture prompt drift and is forbidden. Do not reopen AST-1211 lockstep; do not assert or “fix” non-AST-1211 catalog↔fixture inequality.

⚠️ **Decision — no `tests/` / bible edits:** Engineer pre-commit ban (`astral.git.engineer-test-tree-ban`). `TestAst1211EvaluateCraftFixtureLockstep` is already satisfied by the post-sync fixture (not this child’s job). Betty updates classic-row assertions (e.g. `TestAst878FetchCulturePagesCatalogRow` expecting Job Review → Gaze Review) at Code Complete; meteorite-row Job Review assertions stay until AST-1219.

**Ritual:** `code(AST-1218): Gaze Review classic agent_task group label`

## Self-Assessment

**Scope:** `minor` — two JSON files; `task_group_name` string on nine classic current rows (+ matching fixture rows); no product code layers.

**Conf:** `Medium` — classic/meteorite frozensets and `4000` order are solid; round=1→2 over-asserted global lockstep without tip-checking equality (13 unequal rows including `meteorite_like`). Round=2 verify script narrowed to AST-1211 keys + label fields and was executed against tip `1c006e77` (plus simulated classic rename) before publish.

**Risk:** `low` — display/grouping metadata only; dispatch triggers, prompts, and run_next unchanged; meteorite rows intentionally still Job Review until sibling #2; worst case is a wrong label on classic rows until corrected.

## Code rules check

- §1.1 in-scope-only: seed + fixture label only; no AST-1219 / AST-1184 / AST-1185 / AST-1182 work.
- `astral.seed.agent-tables-in-repo-json`: change ships in repo `agent_task` JSON (`data` layer).
- `astral.standards.names-not-ticket-ids`: product label **Gaze Review**, not a ticket-scoped string.
- `astral.standards.no-hardcoded-sets`: no parallel hard-coded Gaze/Job Review lists in `src/`; membership stays on seed rows.
- `astral.git.engineer-test-tree-ban`: plan forbids engineer edits under `tests/` / `docs/test-bible/**`.
- `orch.git.merge-on-checkout` / `orch.pipeline.plan-is-bible`: inventory and Done when bind to post-`sync-child` state; verify asserts only tip-true predicates (labels + AST-1211 pair), not global object equality.
- §2.1 / §2.4 / §2.6: N/A — no config blocks, batch claim, or state machine changes.
- §3.3 imports: N/A — no Python/TS edits.

## Revisions

Revision 1 — 2026-08-06
Driven by: Joan `[plan-discuss] round=1 concern` — fix-now on Stage 1 Done when / surgical-sync decision pinning stale “missing `evaluate_meteorite`” drift that contradicts `TestAst1211EvaluateCraftFixtureLockstep`; discuss on undeclared merge base; discuss on Files Changed Layer `data/admin` false-excluding seed statute; acceptable no-op verify assert.
Changes: Added **Merge base (build inventory)** binding counts to post-`sync-child` (origin/dev + ftr when present); rewrote Done when / step 5 / surgical-sync decision for lockstep-at-53 (AST-1211 already closed; this child does not reopen); named Betty for classic Gaze Review assertion updates and clarified TestAst1211 is not this child’s close-out; Layer `data/admin` → `data`; verify script requires all meteorite keys + 53 rows + meteor lockstep equality; removed `assert … or True` no-op.

Revision 2 — 2026-08-06
Driven by: Joan `[plan-discuss] round=2 concern` — fix-now on step-6 / Done when over-asserting catalog↔fixture object equality for `METEORITE ∪ {craft_evaluate_meteorite_rubric}` (fails on `meteorite_like` before any AST-1218 edit; 13 unequal rows on tip).
Changes: Narrowed Done when + step 6 to label fields this child controls + AST-1211 pair equality only; documented pre-existing non-global drift in Merge base; surgical-sync decision forbids “fixing” unrelated prompt drift; Conf `high` → `Medium`; ran proposed verify against tip (AST-1211 equal; old equality fails; simulated classic rename + narrowed script passes) before publish.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed`
**Plan path:** `docs/features/meteorite/ast-1218-rename-job-review-to-gaze-review-in-agent-task-seed.md`

**Built tip:** `debff822ff1c2e6758882c4fcb76176df5772b1e` (`debff822`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `debff822` | Gaze Review classic agent_task group label (+ surgical AST-756 fixture) |

## Review (Radia)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1218
**Publish ref:** `origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` @ `017e345d`
**Overall:** CLEAN

**Full-set sweep:** 65 active statutes (18 universal + 47 scoped) scored in-session against `git diff origin/dev...origin/sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed` (5 changed files: `data/admin/agent_task.json` M, `docs/uat-fixtures/AST-756/expected-agent_task.json` M, `docs/test-bible/core/repo_admin_json.md` M, `tests/component/core/test_repo_admin_json.py` M, `docs/features/meteorite/ast-1218-….md` A). All 18 universal `conforms`. 6 scoped statutes matched the diff change set and all score `conforms`: `astral.seed.agent-tables-in-repo-json` (non-empty JSON array, repo-wins seed intact), `astral.seed.define-approved` (Archie-approved membership/order via parent open questions + Joan Plan Approved), `astral.git.engineer-test-tree-ban` (test/bible edits landed via Betty's `test(AST-1218)`→`merge-tests(AST-1218)` commits, not the engineer's `code(AST-1218)` commit, confirmed via `git log --stat`), `astral.git.betty-no-src-or-features` (Betty's merge-tests commit touches only `tests/` + `docs/test-bible/`), `astral.docs.features-single-file-per-ticket` (one file at `docs/features/meteorite/…`), `astral.debug.spikes-under-debug-dir` (plan doc, not spike notes). Remaining 41 scoped statutes `not-applicable` — no diff path/layer intersects their `applies_when` (diff touches only `data/admin/**` and `docs/**`/`tests/**`, no `src/**`). Zero `Job Review`/`Gaze Review` literals under `src/` on this tip (verified via `git grep` on the publish ref). Zero findings.

**Straggler (C4):** Joan plan-rubric verdict attached (revision=1, APPROVED, "18 universal + 10 scoped … all conforms"); slim artifact names no Excluded list to cross-check — no straggler flagged.

**Pattern conformance:** none cited.

**Frame diff:** (none) — diff footprint matches Description In-scope / Files Changed exactly.

context_tokens≈85000

— Radia

## Resolution

**Date:** 2026-08-06
**Review:** Radia `[code-rubric] revision=1` — **Overall: CLEAN** (findings: none). Tip at intake: `7bd94058` (`docs(AST-1218): Radia review — clean`).

**Fix-now / discuss / advisory:** none — no product or plan changes required beyond this resolution stub.

**Outcome:** `resolve(AST-1218): — clean`; advance to **User Testing** (assignee Ada).
