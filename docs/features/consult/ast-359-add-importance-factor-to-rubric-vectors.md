<!-- linear-archive: AST-359 archived 2026-06-03 -->

## Linear archive (AST-359)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-359/add-importance-factor-to-rubric-vectors  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

# Add per-vector importance factor: UI input, config multiplier table, and visual ordering

## Context

We're moving toward a rubric scoring model where each vector carries an explicit importance value (1–10) that determines how much it contributes to the final score. This ticket sets up the foundation: the input mechanism, the config that translates importance into a numeric multiplier, and the UI affordances that make a rubric's importance arrangement visible at a glance.

This ticket does not change scoring behavior. It establishes the data and surfaces it; a downstream ticket consumes it.

## What we want

### 1\. Importance value on each vector

Every vector on every rubric gets an integer importance value in the range 1–10. Users pick this when authoring or editing a rubric. The default for new vectors should be a sensible middle value (suggest 5).

This applies everywhere a rubric defines vectors — wherever a user can add, edit, or reorder vectors today, the importance field appears alongside.

### 2\. Importance-to-multiplier table in config

Add a config-driven mapping that translates each integer 1–10 into a percentage multiplier. Example shape:

| Importance | Multiplier |
| -- | -- |
| 1 | 30% |
| 2 | 49% |
| 3 | 68% |
| 4 | 87% |
| 5 | 106% |
| 6 | 125% |
| 7 | 144% |
| 8 | 163% |
| 9 | 182% |
| 10 | 200% |

Two reasonable approaches and either is fine:

* A literal dict keyed by integer (most flexible — admin can hand-tune individual rows).
* A formula with two configured endpoints (floor% and ceiling%) that linearly interpolates the 10 values (simpler, less surface area).

Whichever we pick, the values need to be visible and editable at the config layer. The scoring ticket will consume this table; this ticket just stands it up with a default that we can tune later.

### 3\. Importance shown in vector labels

Wherever a vector name appears in a rubric-authoring or rubric-viewing context, the importance value shows alongside the name. Suggested format:

```
TITLE_MATCH (8)
TECHNICAL_SKILLS (10)
EDUCATION_FIT (3)
```

The exact visual treatment is up to design — a badge, a parenthetical, a separate column — but the importance value should be readable without the user having to click into the vector.

### 4\. Vectors sorted descending by importance

In the rubric authoring/viewing UI, vectors render sorted by importance, descending. Highest-importance vectors at the top, lowest at the bottom. Ties can break by alphabetical name or by insertion order; either is fine.

This replaces any current ordering logic the user controls manually. We are intentionally removing user-controlled ordering as a separate signal — importance is now the single source of truth for "how much does this matter" and the sort makes that visible.

## Behavioral notes

* Existing rubrics need a migration path: every existing vector needs an importance value assigned. A reasonable default is 5 across the board, with a follow-up admin pass to tune the values that matter. Whether the migration is automated or manual is an implementation call.
* Importance is purely informational at the end of this ticket. Nothing in the scoring pipeline reads it yet. The downstream scoring ticket picks that up.
* The importance value persists with the rubric definition, not with individual grading runs. Changing a vector's importance affects future scores, not historical ones.

## Out of scope

* Any change to how scores are calculated.
* Any UI for editing the importance-to-multiplier table itself (config-only for v1).
* Any change to grade values, confidence handling, or F/X semantics.

## Why this is worth doing first

The scoring redesign assumes importance is already on every vector and that the multiplier table exists. Building those pieces in their own ticket keeps the scoring change focused on math instead of getting tangled up with form fields, migrations, and sort order. It also lets us see the importance arrangement in the UI before any score depends on it, which gives us a chance to sanity-check the values we've assigned.

### Comments

#### chuckles — 2026-05-18T19:22:08.908Z
## finish-up (cleanup) — Chuckles

AST-359 is **Done**, not **PR Ready** — formal gate skipped for branch cleanup.

`origin/ftr/AST-359-add-importance-factor-to-rubric-vectors` had **0 commits** ahead of `origin/dev` (product landed via PR #135 / `bb067070`). **Deleted** stale feature branch.

— Chuckles

#### chuckles — 2026-05-16T15:44:22.685Z
## Board hygiene — Chuckles

Marked **Done**: implementation already on `origin/dev` (emergency integration merge). No further pipeline work.

— Chuckles

#### radia — 2026-05-16T00:33:23.932Z
## Radia review (astral-review) — AST-359

**Git basis:** After `git fetch origin`, **`origin/radia/ast-359-add-importance-factor-to-rubric-vectors` does not exist** (Linear `gitBranchName`). Review used the **integrated `origin/dev`** tree for the AST-359 footprint (feat + UX fixes through **`0601d525`** — consult rubric importance + **ASTRAL_TEST_BIBLE §7.13g** + **`TestImportanceMultiplier`** / **`test_rubricDisplay.test.ts`**). Local workspace `HEAD` may differ from **`origin/dev`**; treat **`origin/dev`** as canonical for this pass.

**Counts:** fix-now **0** · discuss **0** · advisory **2**

### What’s solid (plan + ASTRAL_CODE_RULES)

- **Stages 1–2:** `ASTRAL_CONFIG["consult_importance"]` literal **`multipliers`** 1–10, bounds + default; **`importance_multiplier()`** with type/range/`KeyError`-safe messaging; **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** unions **`company_prefilter`**; **`normalize_rubric_artifacts_on_save`** applies **`ensure_criterion_grade_table`** then **`importance`** coercion with **`ValueError`** messages suitable for HTTP 400 (§2.1 / §1.4; utils↔core layering unchanged).
- **Stage 3 / ticket §4:** **`ArtifactEditor`**: rail sorted **importance desc** (tie: label); **`buildPayload`** keeps **storage list order**; ▲/▼ hidden in **`rubricMode`**; **focus/blur** rail freeze avoids row jump while editing importance (matches plan Rev 6).
- **Stage 4:** Shared **`formatRubricVectorHeader`** / **`rubricItemImportance`** in **`src/ui/frontend/src/lib/rubricDisplay.ts`**; **`AgentAnalysisHeader`** wires rubric rows + grades through those helpers.
- **Stage 8:** **`consult.py`** documents list-order **`_rubric_to_weights`** until **AST-358** — no scoring math change in this ticket.
- **Stage 6 (current dev):** Earlier plan text still says “tests deferred”; **`origin/dev`** now includes **§7.13g** bible map and **component tests** for multipliers + **`rubricDisplay`** — acceptable closure; only **advisory** to sync the combined plan doc’s Stage 6 paragraph with reality when someone next edits that file.
- **Rubric §5a:** No new **`print()`** / bare logging anti-patterns in the touched Python paths reviewed; TS **`catch`** on save surfaces a toast (not a silent D2 swallow).

### Advisory

1. **Backend normalization** clamps out-of-range integer importance to **[min,max]** on save (permitted by plan “clamp or 400”). UX-only: authors do not get an explicit “we clamped your value” message — fine unless Testing wants a visible hint.
2. **`SideTabPanel`** still always exposes ▲/▼ for generic callers; rubric policy remains correctly enforced in **`ArtifactEditor`** only — same cross-editor reuse caveat as prior review; document if new rubric UIs appear.

### Self-Assessment (plan §Self-Assessment)

**Scope / Conf / Risk** still match the merged footprint: persistence + UI + config data for multipliers, **no** `_render_score` behavior change.

— Radia

#### ada — 2026-05-16T00:24:54.740Z
**Ada — `astral-test` green (AST-359)**

**Git (§5):** `dev-ada` = `origin/dev` + merge `origin/betty/ast-359-add-importance-factor-to-rubric-vectors` (Betty bible handoff), then **`test(AST-359): cover agent resume chain + merge context branches`** on `dev-ada` (**`c369fafb`**).

**Publish:** cherry-picked that commit onto **`origin/ada/ast-359-add-importance-factor-to-rubric-vectors`** → tip **`1d5c6eec`** (new remote branch).

**Command (Betty manifest §6):** from repo root:

`./scripts/testing/run_component_tests.sh`

**Result:** **759** Python component tests passed; **`check_per_file_coverage.py`** → *Per-file branch coverage OK (22 locked files)*; frontend **`npm run test:component:coverage`** → **64** files / **183** tests passed; **`check_frontend_coverage.py`** OK.

**Note:** Initial run hit **`src/core/agent.py`** branch lock (92.7%) after resume-chain paths landed without tests — fixed by **`TestMergeChainContextForNextHop`** + **`TestRunResumeArtifactChainForJob`** in `tests/component/core/test_agent.py` (not rubric product code).

— Ada

#### ada — 2026-05-15T21:41:28.398Z
[qa-handoff]

**Blocker:** The published QA manifest cannot be executed against the current Git remote — the harness paths are not in the tree.

**What I checked (clone `astral-ada`, `git fetch origin`):**

1. **Command from manifest:** `./scripts/testing/run_component_tests.sh` — **missing** on `origin/dev`, `origin/main`, and `origin/betty/ast-359-add-importance-factor-to-rubric-vectors`. Under `scripts/` on those refs I only see the usual ops/scrape helpers (e.g. `setup_dev.sh`, `build_ready.sh`, …); there is **no** `scripts/testing/` directory.
2. **Repo root:** `origin/dev` has **no** top-level `tests/` directory at all (`git ls-tree origin/dev` → `.cursor`, `docs`, `scripts`, `src`, … only).
3. **Spot check for product tests:** `git grep TestImportanceMultiplier origin/dev` → **no hits**.

**Conclusion:** This is a **manifest / repo-shape** mismatch, not a failing product test run. I did not mark **Tests Passed** because nothing from the manifest could be run as written.

**Ask for Betty (`astral-qa-plan`):** Either (a) land the component-test tree + `run_component_tests.sh` on a ref engineers are told to merge before `astral-test`, and repoint the manifest at that ref, or (b) replace the manifest with commands that exist on `origin/dev` today.

**Engineer note:** Linear `gitBranchName` is `ada/ast-359-add-importance-factor-to-rubric-vectors` but **`origin/ada/ast-359-…` does not exist** on GitHub (only `origin/betty/ast-359-…` showed up in `git branch -r | grep 359`). If Ada’s feature line is supposed to be the merge target for test runs, it needs to be pushed or the handoff should name the canonical branch.

— Ada

#### betty — 2026-05-15T21:36:34.256Z
QA manifest by Betty.

**Branch:** `betty/ast-359-add-importance-factor-to-rubric-vectors` (new on `origin`; tip **`d8637557`** — `origin/dev` at merge-base plus **`docs/ASTRAL_TEST_BIBLE.md`** so the handoff carries a bible-backed map; there was no `chuckles/…ast-359…` ref on `origin`, and product is already merged on **`origin/dev`**.)

**Local `dev-betty`:** same bible delta as **`bae7961e`** (incremental §7.13g on the full bible already on Betty’s line).

**Run (engineer / `astral-test`):** from repo root, **`./scripts/testing/run_component_tests.sh`** (Appendix A in the bible).

**Numbered manifest** (existing coverage — no new tests required for this ticket; plan Stage 6 deferral is superseded by suites already in tree):

1. **Config — `consult_importance` / `importance_multiplier`:** `tests/component/utils/test_config.py` — `TestImportanceMultiplier`, `TestImportanceMultiplierEdges`.
2. **Core — rubric artifact normalization / importance coercion:** `tests/component/core/test_candidate.py` — `TestNormalizeRubricArtifactsOnSaveExtended`, `TestNormalizeImportanceValue`.
3. **Frontend — display helper:** `tests/component/frontend/lib/test_rubricDisplay.test.ts`.
4. **Frontend — editor / rail / metadata:** `tests/component/frontend/components/test_ArtifactEditor.test.tsx`, `test_SideTabPanel.test.tsx`, `test_LabeledTextArea.test.tsx`.
5. **Frontend — analysis header + rubric artifact pages:** `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx`; `tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx`, `test_ArtifactsJobListCriteria.test.tsx`, `test_ArtifactsJobDescCriteria.test.tsx`, `test_ArtifactsGetJobCriteria.test.tsx`, `test_ArtifactsDoJobCriteria.test.tsx`, `test_ArtifactsLikeJobCriteria.test.tsx`.

**Bible:** **`docs/ASTRAL_TEST_BIBLE.md` §7.13g** names the same paths for the next manifest.

**Broken / obsolete:** none flagged from diff vs plan — if anything fails, it is likely env/harness, not stale assumptions about importance.

— Betty

#### ada — 2026-05-07T20:30:24.003Z
[check-linear]

**AST-359** — follow-up thread (descending sort regression):

- Restored **importance descending** rail order (`tabsSortedForRail`; tie-break `label`), matching plan §3 / acceptance.
- **While importance `<select>` is focused:** snapshot current rail **`id`** sequence (`railOrderFreeze`) so rows **don’t jump** mid-picker.
- **`blur`** clears freeze → list **re-sorts**; **`buildPayload`** unchanged (**storage order**, AST-358-safe).

**Branch:** `chuckles/ast-359-add-importance-factor-to-rubric-vectors` · **Commit:** `f44d39dc`

**Files:** `ArtifactEditor.tsx`, `LabeledTextArea.tsx`, plan doc (**Revision 6** + Stage 3 / Resolution notes).

**Check:** `npx tsc -b --noEmit` clean.

#### chuckles — 2026-05-07T20:28:13.409Z
Susan — additional UX regression after the latest AST-359 UI tweaks:

**Descending sort by importance is gone** in the rubric criterion sidebar (or wherever vectors list). Per original acceptance criteria / plan §4, vectors should **still render sorted by importance, descending** (ties OK per label or stable order — whichever we documented).

Can we restore that ordering **alongside** the stable-row edit rail feedback (importance control moved off the compact header)? Sort-on-display vs destructive reorder while typing needs to stay sane — but losing descending-by-importance entirely shouldn’t happen.

@ada — can you fold this into the same branch / next commit?

— Susan

#### ada — 2026-05-07T20:24:18.712Z
[check-linear]

**AST-359 (Testing feedback thread)** — addressed Chuckles/Susan items directed at Katherine→Ada:

1. **Importance dropdown styling:** criterion panel uses `.artifact-criterion-meta-row` — same padding/border/`accent-gold` focus as **`admin-filters`** selects on **scheduled_actions** (Task filter pattern).
2. **Placement:** importance `<select>` removed from collapsible **sidebar** actions row; it sits in the **expanded panel** next to **Code** via **`LabeledTextArea`** (`importance` / `onImportanceChange`).
3. **Stable rail:** list renders **`tabs`** in **storage order** during edit (removed importance-sort rail); changing importance no longer re-sorts/jumps rows — header still shows **`formatRubricVectorHeader`**.

**Docs:** plan **Revision 5**, Stage 3 **Revision 5** note, Resolution §Testing UX fixes.

**Branch:** `chuckles/ast-359-add-importance-factor-to-rubric-vectors` · **Commit:** `e43a5836`

**Files:** `ui/frontend/src/components/ArtifactEditor.tsx`, `LabeledTextArea.tsx`, `App.css`, `docs/features/consult/ast-359-add-importance-factor-to-rubric-vectors.md`

**Checks:** `npx tsc -b --noEmit` (ui/frontend) clean.

#### chuckles — 2026-05-07T20:10:28.892Z
Susan — UI feedback after local testing on merged dev:

1. **Importance control styling:** Use the same styled dropdown pattern as **scheduled_actions** (select-by-Task) instead of the plain `<select>` currently used for importance.

2. **Placement:** Move the importance control **off the sidebar row header** and into the **expanded criterion panel**, next to **code** (not on the compact row). Changing the number currently re-sorts the list and **yanks the row to a new position**, which feels wrong. Importance shouldn’t feel like a live **comparative reorder** while you’re editing — keep ordering stable in the rail during edit; sorting/display semantics can stay as designed elsewhere if needed.

@ada — please pick these up on the AST-359 branch / follow-up commit.

_(Correction: routes to Ada — assignee on this ticket; earlier mention of Katherine was wrong.)_

— Susan

#### ada — 2026-05-07T19:48:54.738Z
Review feedback resolved. Branch `chuckles/ast-359-add-importance-factor-to-rubric-vectors` is ready for testing. Commit: `0ef36e47`

(Radia review: 0 fix-now; discuss/advisory captured in combined doc **Resolution** section.)

#### cursor — 2026-05-07T17:41:51.023Z
⚠️ No default repository configured. Set a default repository in the [Cursor dashboard](<https://www.cursor.com/dashboard?tab=cloud-agents>).

#### susan — 2026-05-07T17:41:11.570Z
@cursor Can you hear me?

#### unknown — 2026-05-07T17:40:57.649Z
This thread is for an agent session with cursor.

#### susan — 2026-05-06T21:52:22.773Z
**Code review (Radia)** — `origin/dev`…`chuckles/ast-359-add-importance-factor-to-rubric-vectors`

**Counts:** fix-now **0** · discuss **1** · advisory **1**

**What’s solid:** `ASTRAL_CONFIG["consult_importance"]` + **`importance_multiplier()`**; **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** includes **`company_prefilter`**; **`normalize_rubric_artifacts_on_save`** coerces **`importance`** with safe errors; **`tabsForDisplay`** sorts the rubric rail by importance while **`buildPayload`** keeps **storage order** (AST-358-safe); ▲/▼ hidden in rubric mode with per-vector importance select; **`rubricDisplay.ts`** centralizes labels (**§2.1**, **§3.3**).

**Discuss:** Stage **6** tests still deferred — OK only with agreed manual regression on rubric criteria pages + Company Watch.

**Advisory:** Reorder policy lives in **`ArtifactEditor`**; **`SideTabPanel`** only gained optional **`importance`** — any future rubric-like use of the panel should mirror the same gating.

**Combined doc** (Radia appendix committed & pushed):
https://github.com/susansomerset/astral/blob/bfed011d/docs/features/consult/ast-359-add-importance-factor-to-rubric-vectors.md

Cherry-pick **`bfed011d`** if you want only the doc commit on another line.

— Radia

#### susan — 2026-05-06T21:28:28.374Z
Built by Chuckles.

Branch: `chuckles/ast-359-add-importance-factor-to-rubric-vectors`

Commits: `3d70c20a` (feat(AST-359): rubric vector importance, multipliers, UI labels), `6e561d4b` / tip (docs handoff — see branch for latest SHA if additional doc-only commits land).

Stages 1–5, 7–8 per plan; Stage 6 tests still deferred. `_render_score` / `_rubric_to_weights` unchanged (list order until AST-358).

#### susan — 2026-05-06T21:23:58.671Z
Label review (build agent):

Conf: agree — current conf-high
Risk: agree — current risk-Medium
Scope: agree — current scope-MAJOR-CHANGE

Proceeding with **b-build-linear** implementation on `chuckles/ast-359-add-importance-factor-to-rubric-vectors`.

#### susan — 2026-05-06T21:20:56.950Z
yes, please skip the helper.

#### susan — 2026-05-06T21:20:29.412Z
**Ada — follow-up:** Plan **Stage 6** now explicitly deferred + files table row updated (`6fa1cfe9` on top of `e85038e3`).

#### susan — 2026-05-06T21:20:28.296Z
**Ada — follow-up:** Landed in plan **Revision 3** — commit `e85038e3800963b02ab9f8cdd300526245eb19bd` on `chuckles/ast-359-add-importance-factor-to-rubric-vectors`.

#### susan — 2026-05-06T21:20:27.603Z
**Commit (AST-359 plan branch):** `6fa1cfe963c13039f502266c5a9bb095e2df4911`

`docs(AST-359): plan — files table + scope note for deferred tests`

https://github.com/susansomerset/astral/commit/6fa1cfe963c13039f502266c5a9bb095e2df4911

#### susan — 2026-05-06T21:20:27.020Z
**Commit (AST-359 plan branch):** `e85038e3800963b02ab9f8cdd300526245eb19bd`

`docs(AST-359): plan — Stage 4 label format, Stage 5 scoring note, Stage 6 deferred (Rev 3)`

https://github.com/susansomerset/astral/commit/e85038e3800963b02ab9f8cdd300526245eb19bd

#### susan — 2026-05-06T21:19:57.808Z
**Ada — reply:** **AST-358** is the ticket that owns changing `_render_score` / `_rubric_to_weights` (and wiring importance + multipliers into the score math). AST-359 deliberately stops at persistence + UI + `ASTRAL_CONFIG` data so we don’t move live scores while rubrics are in flux. If you’d rather collapse 358 into 359 for one bigger blast radius, that’s a scope call for you — architecturally the split was “data surfaces first, math second.”

#### susan — 2026-05-06T21:19:57.129Z
**Ada — reply:** Noted — **Stage 6 tests skipped for now.** I’ll update the plan file to mark Stage 6 explicitly deferred / out of first implementation pass so **b-build-linear** doesn’t treat tests as mandatory when you approve.

#### susan — 2026-05-06T21:19:56.319Z
**Ada — reply:** Not quite yet for **this** ticket: **Stage 5** in the current plan is only “importance rides along in rubric JSON that hits prompts” — it still does **not** feed `_render_score`. The pipeline that combines grades, confidence, and (later) importance multipliers for the actual numeric score is what we’re deferring to **AST-358** so we don’t change pass/fail thresholds while the UI is still landing. If you want Stage 5 prose tightened so that reads unambiguously, say the word and I’ll patch the plan.

#### susan — 2026-05-06T21:19:54.766Z
**Ada — reply:** Understood for **Stage 4** viewing labels: render as `{importance} - {vector_label} ({vector_code})` with a sensible fallback when `code` is absent so the two-char codes read at a glance. I’ll fold that into the plan doc on the next plan-only commit on `chuckles/ast-359-add-importance-factor-to-rubric-vectors` before build, so the builder isn’t guessing.

#### susan — 2026-05-06T21:19:53.822Z
**Ada — reply:** Yes — the end state you want is exactly **AST-358**: `_rubric_to_weights` / `_render_score` stop using positional list order and instead use per-vector **importance** (and the multiplier map) together with the existing grade-density / confidence machinery. **AST-359** only buys time so UI + stored rubrics can’t silently reorder arrays and move scores before that cutover. I’ll treat your sentence as the acceptance check when we implement 358.

#### susan — 2026-05-06T21:19:50.567Z
**Ada — reply:** Single source of truth is still **one dict** under `ASTRAL_CONFIG["consult_importance"]["multipliers"]` (exact nesting as implemented). The optional `importance_multiplier(n)` line in the plan only meant “a tiny accessor if we want one place for bounds/KeyError messaging”—not a second table. If that reads like two sources of truth, we’ll skip the helper and read the dict directly everywhere.

#### susan — 2026-05-06T21:19:49.470Z
**Ada — reply:** Leaving this `[check-linear]` as the audit anchor. Newer comments below (Stages 4–8, tests skip) came in after this post — I’m replying to each of those individually as threads.

#### susan — 2026-05-06T21:19:49.151Z
**Ada — reply:** Incorporated in plan **Revision 2** (`22be42d3`): (1) **TASK_CONFIG** stays the home for task defs / `vectors` / schemas; we only extend **artifact criterion rows** in `candidate_data`, not a parallel rubric blob. (2) Multiplier map lives under **`ASTRAL_CONFIG`** (not `AGENT_CONFIG` — that block is model catalog only). (3) **`CONSULT_CONFIG`** is still in the codebase and still feeds **`RUBRIC_ARTIFACT_KEYS`** today; this ticket does not obviate it—any migration toward TASK_CONFIG + `dispatch_tasks` only is out of scope here. (4) **`_render_score`**: no behavior change in AST-359; **AST-358** consumes importance + multipliers for scoring.

#### susan — 2026-05-06T21:19:48.572Z
**Ada — reply:** Confirmed — this comment described the first proper full-file rewrite (`f940199b`). Your later plan-review notes then drove **Revision 2** in `22be42d3` (TASK_CONFIG vs artifacts, multipliers under `ASTRAL_CONFIG`, `_render_score` stays frozen until AST-358).

#### susan — 2026-05-06T21:19:45.435Z
**Ada — reply:** That pass really did only bolt on `## Self-Assessment` instead of doing the full **a-plan-linear** replace-from-scratch thing, so the thread was a bit misleading in hindsight. We corrected that with the full rewrites in `f940199b` / `22be42d3` (see the commit notes I just posted above). Thanks for the patience while the branch/worktree story was messy.

#### susan — 2026-05-06T21:19:41.258Z
**Commit (AST-359 plan branch):** `e100adebef30be5df18529abbc866f74e2fce0d7`

`merge origin/dev (check-linear pass)`

https://github.com/susansomerset/astral/commit/e100adebef30be5df18529abbc866f74e2fce0d7

#### susan — 2026-05-06T21:19:40.645Z
**Commit (AST-359 plan branch):** `22be42d379fd0395c8ea5f561cab63f04c0964da`

`docs(AST-359): plan — rewrite for TASK_CONFIG, ASTRAL_CONFIG, review notes`

https://github.com/susansomerset/astral/commit/22be42d379fd0395c8ea5f561cab63f04c0964da

#### susan — 2026-05-06T21:19:40.406Z
**Commit (AST-359 plan branch):** `e9e6143a4ab084c428c225821f52d621bd6a3f3c`

`merge origin/dev into ast-359 plan branch`

https://github.com/susansomerset/astral/commit/e9e6143a4ab084c428c225821f52d621bd6a3f3c

#### susan — 2026-05-06T21:19:39.865Z
**Commit (AST-359 plan branch):** `f940199b4038a1463acfe5f007835d3c373d8fe3`

`docs(AST-359): plan — full rewrite per a-plan-linear (re-run)`

https://github.com/susansomerset/astral/commit/f940199b4038a1463acfe5f007835d3c373d8fe3

#### susan — 2026-05-06T21:19:38.636Z
**Commit (AST-359 plan branch):** `b484ce1ab0b494a21244e8c55c4e93df83280065`

`docs(AST-359): plan — add Self-Assessment (Conf/Risk/Scope)`

https://github.com/susansomerset/astral/commit/b484ce1ab0b494a21244e8c55c4e93df83280065

#### susan — 2026-05-06T21:17:37.303Z
Stage 8: Do we have another related ticket for updating render_score and rubric to weights?  That feels like it should be included in the scope of this ticket, since it is part of the end-to-end flow.

#### susan — 2026-05-06T21:16:36.659Z
Stage 6 - Tests : Skip for now.

#### susan — 2026-05-06T21:15:25.666Z
Stage 5: If I'm reading this right, the scope of this ticket just ensures that the importance of the vector gets passed to the function calculating the score with the "grade density" already computed based on the grade and the confidence rating?

#### susan — 2026-05-06T21:13:44.508Z
Stage 4: While we are meddling with the vector labels, please display them as <importance rating> - <vector_label> (<vector_code>) so that the user can visually see if they've already used a two character code.

#### susan — 2026-05-06T21:12:01.182Z
"**⚠️ Decision — storage vs display:** `_rubric_to_weights` still uses **list order** in storage. UI keeps **canonical tab array in API order**; only the **rail render** (or `displayOrder` ids) sorts by importance. Autosave / `buildPayload` must not rewrite the full list into importance order until [AST-358](https://linear.app/astralcareermatch/issue/AST-358/replace-per-vector-grade-scores-with-universal-grade-values-per-vector)."

This is fine as long as we have confirmed that all position-based weighting logic has been replaced with the direct importance-related weight when rendering the score.

#### susan — 2026-05-06T21:09:51.269Z
"Add `importance_multiplier(n: int) -> float` (or equivalent) **only** if a single shared accessor keeps call sites readable; otherwise read `ASTRAL_CONFIG["consult_importance"]["multipliers"][n]` with validation. Utils must not import core/data/external."

What are we suggesting here?  Would we be potentially introducing multiple sources of the importance_multiplier value?

#### susan — 2026-05-06T19:30:12.939Z
[check-linear]

**Pass (Astral Consult + Ada):** Queried Todo / Plan Ready / Plan Approved / In Progress / Code Complete / Review Posted / Testing — **AST-359** only (Plan Ready).

**Actionable thread:** Your **plan review** (TASK_CONFIG vs tack-on, multiplier home, CONSULT_CONFIG direction, `_render_score`). Addressed by **replacing the plan doc from scratch** again per **a-plan-linear** step 6 + **Revisions §Revision 2**.

**Plan changes (summary):**
- **TASK_CONFIG / artifacts:** Clarified split — `TASK_CONFIG` owns task defs (`vectors`, schemas); **criterion rows** stay in `candidate_data.artifacts.*`; AST-359 only extends those rows + global tuning — **no** parallel rubric config.
- **Multipliers:** Moved spec to **`ASTRAL_CONFIG`** nested block (e.g. `consult_importance`); explicitly **not** `AGENT_CONFIG` (model catalog only).
- **CONSULT_CONFIG:** Stated it **still** drives `Rubric_artifact` / `RUBRIC_ARTIFACT_KEYS` today; **no** removal/refactor in this ticket.
- **`_render_score`:** Explicit **no behavior change** in AST-359; **AST-358** consumes importance + multipliers.

**Git:** `chuckles/ast-359-add-importance-factor-to-rubric-vectors` — plan commit `22be42d3`, then merge `origin/dev` (merge commit on branch). Plan: https://github.com/susansomerset/astral/blob/chuckles/ast-359-add-importance-factor-to-rubric-vectors/docs/features/consult/ast-359-add-importance-factor-to-rubric-vectors.md

**Post-inbox chain:** **e-push** / **d-resolve** / **b-build** not applicable (not PR Ready / Review Posted / Plan Approved).

**Second pass:** Re-listed issues + comments after posting — no further actionable items without your reply.

#### susan — 2026-05-06T19:27:52.322Z
Plan review notes from Susan:

This plan appears to be ignoring the extant patter for TASK_CONFIG in config.py and proposing a "tack on" of criteria content separate from that element.  Reconsider your approach.

I agree that a shape for importance multipliers as a setting is needed in config.py, but it should go in ASTRAL_CONFIG or AGENT_CONFIG, since I believe we have obviated CONSULT_CONFIG in lieu of TASK_CONFIG and dispatch_tasks in the database.

Would this not affect the render_score function, as well?  Or is that functionality covered in a separate ticket I have forgotten?

#### susan — 2026-05-05T17:48:59.971Z
**Plan re-run (a-plan-linear step 6):** The prior agent pass only **patched** the existing markdown. Per **a-plan-linear**, when the plan path already exists the planner must **replace the file from scratch** in one pass.

**What changed:** `docs/features/consult/ast-359-add-importance-factor-to-rubric-vectors.md` is now a **full rewrite** (same technical intent: config + normalization + UI + tests + docs; reorganized into numbered **Stages** with **Done when**; the old “storage vs display order” note is folded into **Stage 3** as a **⚠️ Decision**). Added **`## Revisions`** entry citing this correction.

**Git:** Branch `chuckles/ast-359-add-importance-factor-to-rubric-vectors` — plan commit `f940199b`, then **merge `origin/dev`** into the branch (`e9e6143a`) so the feature branch matches current `dev` before build. Plan file on branch: https://github.com/susansomerset/astral/blob/chuckles/ast-359-add-importance-factor-to-rubric-vectors/docs/features/consult/ast-359-add-importance-factor-to-rubric-vectors.md

**Linear:** Still **Plan Ready**; Conf/Risk/Scope unchanged (**conf-high**, **risk-Medium**, **scope-MAJOR-CHANGE**). **Ada** retained.

#### susan — 2026-05-04T21:26:26.272Z
[check-linear]

**Inbox (Astral Consult + Ada):** One pass across Todo / Plan Ready / Plan Approved / In Progress / Code Complete / Review Posted / Testing — only **AST-359**. `list_comments` shows **no thread**; zero actionable items.

**a-plan-linear (AST-359):** Plan already lived on `dev`; added missing **`## Self-Assessment`** (Scope `MAJOR-CHANGE`, Conf `high`, Risk `Medium` — see doc), pushed **`chuckles/ast-359-add-importance-factor-to-rubric-vectors`**, commit **`b484ce1ab0b494a21244e8c55c4e93df83280065`**. Linear → **Plan Ready**, labels **conf-high / risk-Medium / scope-MAJOR-CHANGE** (kept **Ada** + **Enhancement**), GitHub attachment on the feature branch per workflow.

**e-push-linear:** Not run — ticket is not **PR Ready**.

**d-resolve-linear:** Not run — ticket is not **Review Posted**.

**b-build-linear:** Not run — ticket is not **Plan Approved** (stops at Plan Ready for your review).

**Note:** `dev` is checked out in another worktree (`…/astral`), so branch prep used `origin/dev` + rebase onto `origin/main` without switching this clone to `dev`.

---

# AST-359 — Add Importance factor to rubric vectors

**Linear:** [AST-359 — Add Importance factor to rubric vectors](https://linear.app/astralcareermatch/issue/AST-359/add-importance-factor-to-rubric-vectors)  
**Project:** Astral Consult → `docs/features/consult/`  
**Feature branch:** `<agent>/ast-359-add-importance-factor-to-rubric-vectors`  
**Downstream:** This work **blocks AST-358** (scoring will consume per-vector importance + the multiplier table).

## Summary

Add integer **`importance`** (1–10) on each **rubric criterion row** stored under **`candidate_data.artifacts.<artifact_key>`**, add a **global** 1→10 importance→multiplier map as **literals** in **`ASTRAL_CONFIG`**, and extend the **ArtifactEditor** / read-only UI so authors and readers see importance, edit it, and view vectors sorted by importance—**without** changing **`_render_score`**, **`_rubric_to_weights`**, grade validation, or consult pass/fail thresholds. Missing `importance` on existing rows defaults to **5** on read and may be normalized on save.

---

## Execution contract

This file is the implementation script: follow stages in order; do not add files or behaviors not listed here. Ambiguity or repo drift → stop and comment on **AST-359** (🛑 Stage blocked template per **a-plan-linear**).

---

## Architecture: `TASK_CONFIG`, artifacts, and `CONSULT_CONFIG` (no parallel rubric store)

- **`TASK_CONFIG`** is the canonical place for **task definitions**: prompts, `response_schema`, **`vectors`** (names + grade_scores) for graded tasks such as `grade_get`, `grade_do`, `grade_like`, plus craft-rubric tasks. Do **not** invent a second rubric document or “tack on” a duplicate list of criteria outside that model.
- **Authoring payload** for consult rubrics already lives in **`candidate_data.artifacts`** (per-key arrays of `{ label, content, code?, … }`). Consult batch code joins those artifacts to tasks via **`CONSULT_CONFIG[*]["rubric_artifact"]`** and **`RUBRIC_ARTIFACT_KEYS`** (today: `frozenset` derived from **`CONSULT_CONFIG`** entries that declare `rubric_artifact`).
- **AST-359** extends **only** the **artifact row JSON** with **`importance`** and adds **global tuning numbers** (multipliers) for a **future** scoring pass (**AST-358**). It does **not** move orchestration off `CONSULT_CONFIG`, does **not** remove `CONSULT_CONFIG`, and does **not** duplicate full rubric text into a new config block beside `TASK_CONFIG`.

---

## Stage 1 — Global multiplier table and bounds (`ASTRAL_CONFIG`)

**Done when:** Importance 1→10 multipliers and default/min/max live under **`ASTRAL_CONFIG`** in `src/utils/config.py` as **literals** (not env vars). **`AGENT_CONFIG`** stays **model-catalog only**—do **not** place scoring multipliers there.

1. Under **`ASTRAL_CONFIG`**, add a small nested block (name up to implementer, e.g. **`consult_importance`**) containing at least:
   - **`multipliers`**: `dict[int, float]` for keys **1–10** (same convention as `CONFIDENCE_MULTIPLIERS`: `0.30` = 30%). Seed with the Linear issue table (1→0.30 … 10→2.00).
   - **`default_vector_importance`** = **5**, **`min`** = **1**, **`max`** = **10**.
2. **⚠️ Decision:** Keep multipliers as an explicit **literal dict** inside that block (hand-tunable); defer formula-based generation to a later ticket unless product insists.
3. Add **`importance_multiplier(n: int) -> float`** (or equivalent) **only** if a single shared accessor keeps call sites readable; otherwise read `ASTRAL_CONFIG["consult_importance"]["multipliers"][n]` with validation. Utils must not import core/data/external.

**Files:** `src/utils/config.py` only for this stage.

---

## Stage 2 — Artifact row shape + `normalize_rubric_artifacts_on_save`

**Done when:** Listed artifact keys accept **`importance`** on each criterion dict; missing → default from Stage 1; out-of-range → clamp or **400** with safe message; `company_prefilter` is included in the same normalization pass as consult rubrics.

**Canonical row** (`candidate_data.artifacts.<key>[i]`): existing fields unchanged plus **`importance`**: int **1–10**.

| `artifact_key`      | Page / task            |
|---------------------|------------------------|
| `company_prefilter` | Company Watch Criteria |
| `joblist_rubric`    | Job List Criteria      |
| `jobdesc_rubric`    | Job Description Criteria |
| `get_rubric`        | Get Job Criteria       |
| `do_rubric`         | Do Job Criteria        |
| `like_rubric`       | Like Job Criteria      |

1. Extend **`normalize_rubric_artifacts_on_save`** in **`src/core/candidate.py`**. Today **`RUBRIC_ARTIFACT_KEYS`** comes from **`CONSULT_CONFIG`** (`rubric_artifact`); **`company_prefilter`** is outside that set—add **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** = `RUBRIC_ARTIFACT_KEYS | {"company_prefilter"}` (or explicit frozenset) as the single driver for importance + existing grade-table behavior.
2. Keep HTTP **400** messages consistent with current validation style.

**Files:** `src/utils/config.py` if exporting the widened key set next to `RUBRIC_ARTIFACT_KEYS`; **`src/core/candidate.py`**.

---

## Stage 3 — Authoring UI (control, display sort, no manual reorder)

**Done when:** Per-vector importance 1–10 in editor; sidebar **display** sorted by importance descending; **▲/▼** reorder disabled for rubrics; **persisted array order** in JSON unchanged (so current scoring math is unchanged).

**Components:** `SideTabPanel.tsx` (`SideTab` + optional `allowReorder`), `ArtifactEditor.tsx`.

**⚠️ Decision — storage vs display:** **`_rubric_to_weights`** still uses **list order** in storage. UI keeps **canonical tab array in API order**; only the **rail render** (or `displayOrder` ids) sorts by importance. Autosave / `buildPayload` must not rewrite the full list into importance order until **AST-358**.

**Revision 5–6 (Testing):** **Importance** is edited beside **Code** in the expanded panel (not the compact header); dropdown styling matches **`admin-filters`**. The rail renders **importance descending** when the importance `<select>` is **not** focused; **`focus`** freezes visible **`id`** order until **`blur`** so the picker does not yank rows mid-edit. Collapsible headers still show **`formatRubricVectorHeader`**. **`buildPayload`** keeps **storage order**. Job/analysis read surfaces unchanged (**Stage 4**).

**Files:** `SideTabPanel.tsx`, `ArtifactEditor.tsx`, optional `App.css`.

---

## Stage 4 — Viewing UI (labels show importance)

**Done when:** Vector labels in analysis/job surfaces use Susan’s display shape so codes are obvious:

`{importance} - {vector_label} ({vector_code})`

Use a sensible fallback when `code` is missing (e.g. omit the parentheses block or show `(—)`). Prefer one helper (e.g. `formatVectorLabel` in `src/ui/frontend/src/lib/rubricDisplay.ts`) so all surfaces stay consistent.

**Files:** `AgentAnalysisHeader.tsx`, `JobsRecommended.tsx`, `JobsInReview.tsx`, optional `rubricDisplay.ts`.

---

## Stage 5 — Prompts

Rubric JSON embedded in prompts picks up **`importance`** automatically once stored. **This does not** feed **`_render_score`** or change how grades + confidence become a numeric score — that wiring is **AST-358** only. No special casing for tokens unless a follow-up asks.

---

## Stage 6 — Tests

**Deferred (Susan / Linear 2026-05-06):** skip automated tests for this ticket’s first implementation pass. Do **not** add or extend normalization test suites under AST-359 unless Susan re-opens this stage.

*(Previous text for reference when re-enabled: normalization tests for missing → default, bounds, `company_prefilter`; optional assert multiplier dict keys 1–10.)*

---

## Stage 7 — `CANDIDATE_DATA_MODEL.md`

Document **`importance`** on artifact criterion objects and point to **`ASTRAL_CONFIG["consult_importance"]`** (exact key as implemented).

---

## Stage 8 — `consult.py` (optional comment only)

One-line note near **`_rubric_to_weights` / `_render_score`**: list-order weighting unchanged until **AST-358**. **No** code path changes to **`_render_score`** in this ticket.

---

### `_render_score` and this ticket (explicit)

**No.** **`_render_score`** and **`_rubric_to_weights`** are **not** modified in behavior for AST-359. The issue and **AST-358** scope split is intentional: this ticket **persists and surfaces** importance + installs the multiplier **data** under `ASTRAL_CONFIG`; **AST-358** changes how weights/scores consume that data. If anything in the plan ever implied otherwise, treat this paragraph as overriding.

---

### Files changed (planned)

| File | Change |
|------|--------|
| `src/utils/config.py` | `ASTRAL_CONFIG` consult-importance block; optional export of `RUBRIC_CRITERIA_ARTIFACT_KEYS` |
| `src/core/candidate.py` | Normalization + `importance` + `company_prefilter` |
| `src/core/consult.py` | Optional one-line comment |
| `src/ui/frontend/src/components/SideTabPanel.tsx` | `importance`, reorder gate, display order |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Load/save/generate |
| `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` | Labels |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Labels |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Labels |
| `src/ui/frontend/src/lib/rubricDisplay.ts` | Optional shared formatter |
| `src/ui/frontend/src/App.css` | Minor styles |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Schema |
| `tests/...` | **None first pass** (Stage 6 deferred) |

---

## Self-review vs ASTRAL_CODE_RULES

- **§2.1 / §1.4:** Literals in `config.py`; multipliers grouped under **`ASTRAL_CONFIG`**, not env vars.
- **§3.3:** Utils/core layering unchanged; no new cross-layer imports.
- **§1.3:** One frontend label helper where practical.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Config + candidate + React + docs across one feature (tests deferred this pass).

**Conf:** `high` — Aligns with existing `TASK_CONFIG` / artifact split and `ASTRAL_CONFIG` grouping; Stage 3 pins list-order vs display.

**Risk:** `Medium` — Persisted re-order by importance would change weights; mitigated by explicit rule + tests.

---

## Revisions

Revision 1 — 2026-05-04  
Driven by: Process correction — **a-plan-linear** requires full replace when the plan path already exists.  
Changes: First full staged rewrite (sections → Stages + **Done when**).

Revision 2 — 2026-05-06  
Driven by: Susan plan review (Linear) — align with **`TASK_CONFIG`** / artifact model (no parallel rubric tack-on); put multipliers in **`ASTRAL_CONFIG`** (not **`AGENT_CONFIG`**); clarify **`CONSULT_CONFIG`** still sources `RUBRIC_ARTIFACT_KEYS` today; confirm **`_render_score`** unchanged here (**AST-358** consumes importance).  
Changes: **Full document replace** incorporating that feedback (this revision).

Revision 3 — 2026-05-06  
Driven by: Susan Linear thread — **Stage 4** label format (`{importance} - {label} ({code})`); **Stage 5** clarified prompts do not invoke scoring; **Stage 6** tests explicitly **skipped / deferred** for first build pass.  
Changes: Patch Stages 4–6 + this revision entry (no full replace).

Revision 4 — 2026-05-06  
Driven by: **b-build-linear** implementation pass (stages 1–5, 7–8; stage 6 still deferred).  
Changes: Config + normalization + UI + docs as staged above.

Revision 5 — 2026-05-07  
Driven by: Susan **Testing** feedback (Linear) — importance editor UX (off sidebar row; **`admin-filters`** styling; no row jump **while** editing importance).  
Changes: **Importance** beside **Code** in **`LabeledTextArea`**; initial pass used storage-order-only rail — **Revision 6** restores descending sort + focus freeze.

Revision 6 — 2026-05-07  
Driven by: Susan Testing — restore **descending-by-importance** rail (plan §3 / acceptance) **without** row-jump while the importance `<select>` is open.  
Changes: Rail renders **`tabsSortedForRail`** (importance desc, tie-break label). On importance **`focus`**, snapshot row **`id`** order into **`railOrderFreeze`**; **`blur`** clears freeze so list resorts. Payload/storage order unchanged.

---

## Review (build handoff)

**Branch:** `<agent>/ast-359-add-importance-factor-to-rubric-vectors`  
**Commits:** `3d70c20a` (feat bundle), `6e561d4b`, `6c3dd0b9` (docs / review stub)

## Review (Radia) — 2026-05-06

**Diff:** `origin/dev`…`<agent>/ast-359-add-importance-factor-to-rubric-vectors` @ **`5925a0ec`**.

### What’s solid

- **Plan fidelity:** `ASTRAL_CONFIG["consult_importance"]` literal table + **`importance_multiplier()`**; **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** includes **`company_prefilter`**; **`normalize_rubric_artifacts_on_save`** coerces **`importance`** with safe **`ValueError`** messages — matches Stages 1–2 and migration notes.
- **§2.1 / §1.4:** Bounds and multipliers live in **`config.py`** as literals; no env fallbacks for this feature.
- **§3.3:** **`rubricDisplay.ts`** keeps formatting in **`ui/`**; core imports stay within allowed layers.
- **Display vs storage order:** **`tabsForDisplay`** sorts the **collapsible rail** by importance while **`buildPayload` / `handleChange`** keep **`tabs`** in storage order — matches the plan’s “no `_rubric_to_weights` behavior change until AST-358” rule.
- **Reorder controls:** ▲/▼ hidden in **`rubricMode`** (`!fixedFields`); importance **`<select>`** added — manual order is no longer a separate signal for rubrics.

### Issues

| Severity | Topic | Detail |
|----------|--------|--------|
| *Discuss* | Stage 6 | Automated tests still **deferred** per plan — acceptable for this pass only if Susan signs off on manual regression on rubric pages + Company Watch. |
| *Advisory* | `SideTabPanel` diff | Interface adds **`importance?: number`** only; reorder policy is enforced in **`ArtifactEditor`** — fine, but future editors using **`SideTabPanel`** for rubric-like data should mirror the same **`rubricMode`** gating. |

### Recommended actions

1. Manual pass: edit importance on several vectors, save, reload — confirm persisted order unchanged in JSON while rail sorts descending.
2. Spot-check **`AgentAnalysisHeader`** / **Jobs\*** labels against **`formatRubricVectorHeader`** for typos and long labels.

**Counts:** fix-now **0** · discuss **1** · advisory **1**

— Radia

---

## Resolution (**f-resolve-linear** — 2026-05-07)

- **Fix-now:** none — Radia count **0**; no code changes required for review closure.
- **Discuss (Stage 6 / manual regression):** Accepted as stated on the ticket — automated tests remain deferred; **manual regression** on rubric criteria pages + Company Watch is the acceptance path during **Testing** (Susan).
- **Advisory (`SideTabPanel`):** Noted — reorder/importance policy stays documented here and enforced in **`ArtifactEditor`**; any future rubric-like reuse of **`SideTabPanel`** should mirror **`rubricMode`** gating.

No further commits beyond this resolution stub unless Testing finds defects.

### Testing UX fixes (**check-linear** — 2026-05-07)

- **Importance placement + styling:** Control is inside the expanded criterion body, next to **Code** (`LabeledTextArea`); `<select>` uses the same padding/border/focus treatment as **`admin-filters`** selects on **scheduled_actions**.

### Testing UX — descending sort restored (**check-linear** — 2026-05-07, follow-up)

- Rail again renders **importance descending** (tie-break: label). **`buildPayload`** still emits **`tabs`** in **storage order** (AST-358-safe).
- **Focus freeze:** Opening the importance dropdown snapshots rail **`id`** order; closing it (**`blur`**) clears the snapshot so the list resorts cleanly without jumps mid-picker.
