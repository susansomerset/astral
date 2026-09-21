# AST-1275 — Remove "pass_threshold" from task_config

<!-- linear-archive: AST-1275 archived 2026-08-19 -->

## Linear archive (AST-1275)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1275/remove-pass-threshold-from-task-config  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

`pass_threshold` on `TASK_CONFIG` was discontinued and must not come back. The only numeric floor is `score_floor` on the candidate’s `dispatch_task` row — it owns eligibility and post-run pass vs fail. This epic removes every `pass_threshold` key, wires scored verdicts to that row’s `score_floor` (including `0`), fixes the admin Score Floor control so `0` is selectable, and replaces the mistaken pass-threshold statute with a score-floor pattern (no statute for this concept).

## Functional scope

1. Remove `pass_threshold` from every `TASK_CONFIG` entry that still has it — including roster consult (`grade_do` / `grade_get` / `grade_like`), meteorite aliases (`meteorite_grade_do` / `meteorite_grade_get` / `meteorite_like`), and `prefilter_company`.
2. For scored runs, decide pass vs fail using the `score_floor` on the candidate’s matching `dispatch_task` record (not a task-config constant). Explicit `0` is valid and must mean “no numeric soft-fail.”
3. Keep dealbreaker (F-with-confidence) and technical error fail paths; keep recording the computed score/grades.
4. Admin Edit Dispatch Task Score Floor control must offer `0` (and persist `0`) — Susan reports the dropdown still bottoms at `1`.
5. Retire statute `astral.config.pass-threshold-vs-score-floor` and all “pass_threshold vs score_floor” law wording in Code Rules §2.1. Author a **score_floor** pattern (project/product pattern — not a coding statute). There must be **no** pass-threshold pattern or statute left.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` (no resurrected task-config threshold literals). `pattern.batch.entity-claim-process-release` (claim/count already reads row `score_floor`). `pattern.state.entity-state-transitions` (pass/fail/error states unchanged as names).
* **New patterns proposed** — `pattern.dispatch.score-floor` (name flexible at authoring): `dispatch_task.score_floor` is the sole numeric floor for a scored step — dispatch eligibility and post-run pass/fail both read that row value; `0` allowed; no parallel `TASK_CONFIG` threshold. **Archie approval required** before implementation depends on the catalog id.
* **Applicable statutes** — `astral.config.config-source-of-truth` (floors live on dispatch rows / config blocks as appropriate — not hardcoded in core). `astral.patterns.render-verdict-orchestrates-consult` (verdict path applies the floor). `astral.standards.no-hardcoded-sets` (no magic `6.0` left behind). **Explicitly retiring:** `astral.config.pass-threshold-vs-score-floor` (must not remain as active law). Universal product set: `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`.

## Boundaries

* Does **not** reintroduce `pass_threshold` under another name on `TASK_CONFIG`.
* Does **not** turn score-floor rules into a coding statute — pattern only, per Susan.
* Does **not** remove F2 dealbreaker or technical error parking.
* Does **not** redesign meteorite trigger states or alias `master_task_key` work (AST-1184 / AST-1220–1222) beyond deleting `pass_threshold` keys those aliases still carry.
* Does **not** change NULL `score_floor` claim normalization except where required so explicit `0` is distinct from NULL (existing NULL→1.0 claim behavior stays unless a child discovers it blocks `0`).

## Acceptance criteria

1. No `TASK_CONFIG` entry defines `pass_threshold` (roster, meteorite aliases, and `prefilter_company` included).
2. A scored consult/prefilter run soft-fails or passes using the candidate dispatch task’s `score_floor`, including when that value is `0` (always-pass on numeric floor; dealbreaker/error still fail).
3. Admin Score Floor dropdown lists `0` and saving `0` persists `0` on the dispatch task row.
4. Statute `astral.config.pass-threshold-vs-score-floor` is retired/removed from the active catalog; Code Rules §2.1 no longer teaches pass_threshold; a score_floor **pattern** exists and is the cited authority.
5. No active pattern or statute remains whose subject is pass_threshold.

## Dependencies and blockers

* none.
* Adjacency: AST-1184 / AST-1220–1222 (User Testing) still mention alias `pass_threshold` copies — this epic deletes those keys; coordinate if those branches rewrite the same lines.

## Open questions

none

## Proposed child tickets

#### 1!: **Strip pass_threshold; verdict uses dispatch score_floor - Ada**

Remove every `TASK_CONFIG` `pass_threshold` (including `prefilter_company`). Scored verdict path reads `score_floor` from the candidate’s dispatch task row, with `0` meaning no numeric soft-fail. Dealbreaker/error paths unchanged. Does not own admin dropdown or canon retirement.
**Citations:** `pattern.config.config-block`, `pattern.batch.entity-claim-process-release`, `pattern.state.entity-state-transitions`, `astral.config.config-source-of-truth`, `astral.patterns.render-verdict-orchestrates-consult`, `pattern.dispatch.score-floor` (proposed)

#### 2!: **Admin Score Floor dropdown allows 0 - Katherine**

Fix Scheduled Actions / Edit Dispatch Task Score Floor options and save path so `0` appears and persists (Susan: control still mins at `1`). Does not own consult verdict math (child 1).
**Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `pattern.dispatch.score-floor` (proposed), `astral.layers.ui-config-driven-business-logic`

#### 3: **Retire pass-threshold statute; author score_floor pattern + Code Rules - Hedy**

Retire `astral.config.pass-threshold-vs-score-floor`, ensure no pass-threshold pattern/statute remains, add approved `pattern.dispatch.score-floor` (or Archie-final id), rewrite Code Rules §2.1 to match. After #1 (and dropdown AC if docs cite UI). No further runtime behavior beyond aligning law to shipped behavior.
**Citations:** `pattern.dispatch.score-floor` (proposed), `astral.config.config-source-of-truth`, `astral.docs.features-single-file-per-ticket`

**New patterns:** Child 3 introduces `pattern.dispatch.score-floor`; children 1–2 implement against that shape once Archie approves the id (or against this definition’s plain-language rule if approval lands in the same epic).

Monolith check: five functional capabilities → three children (runtime floor, admin `0`, canon/docs).

---

## Original brief

```
`"pass_threshold": 6.0,`
```

This is reestablishing/superseding a "score floor".  The dispatch task determines the score floor, and the meteorites don't use score floors (if it makes it past the initial review, it all gets analysis).

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1275 (parent) | ftr/AST-1275-remove-pass-threshold-from-task-config |
| AST-1277 | sub/AST-1275/AST-1277-strip-pass-threshold-verdict-uses-dispatch-score-floor |
| AST-1278 | sub/AST-1275/AST-1278-admin-score-floor-dropdown-allows-0 |
| AST-1279 | sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern |

**Epic worktree:** `astral-AST-1275/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/60c087c40855cbe6c7fd2eb43e871015/174f2531-859b-4821-8697-92320f1bdfb9/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/60c087c40855cbe6c7fd2eb43e871015/27a47267-a23a-44f2-883f-ce2dd0e347ba/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/60c087c40855cbe6c7fd2eb43e871015/9b509b87-c7a5-4146-93d3-a59ca3c1bf4e/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/c3d2c5eb-21d7-49df-bbda-25db26f9bddf/store.db` |
| Radia | review | `/home/susan/.cursor/chats/60c087c40855cbe6c7fd2eb43e871015/f0135b57-bafe-4b71-a0a8-f18f42de595c/store.db` |

### Comments

#### susan — 2026-08-08T00:59:32.667Z
There should be no pattern (or statute) that talks about pass threshold.  Only score floor, and it's a pattern (specific to the project, not a coding statute).

#### chuckles — 2026-08-08T00:58:57.431Z
@susan

1. Scope of keys — meteorite tasks only (`meteorite_grade_do` / `meteorite_grade_get` / `meteorite_like`), or also roster consult (`grade_do` / `grade_get` / `grade_like`)?
2. After removal — in-scope scored runs always pass (score informational; F2/error still fail), or another fail rule?
3. Statute `astral.config.pass-threshold-vs-score-floor` — revise globally, or meteorite exception only?
4. Leave `prefilter_company` `pass_threshold: 0.0` alone?
5. Linear project — put on **Astral Meteorite** (or other)? Ticket currently has no project.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
