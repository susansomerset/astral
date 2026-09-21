<!-- linear-archive: AST-1279 archived 2026-08-19 -->

## Linear archive (AST-1279)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1279/retire-pass-threshold-statute-author-score-floor-pattern-code-rules  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1275 — Remove "pass_threshold" from task_config  
**Blocked by / blocks / related:** parent: AST-1275

### Description

## What this implements

Retire `astral.config.pass-threshold-vs-score-floor`, ensure no pass-threshold pattern/statute remains, add approved `pattern.dispatch.score-floor` (or Archie-final id), rewrite Code Rules §2.1 to match. After siblings Ada + Katherine. No further runtime behavior beyond aligning law to shipped behavior.

## Acceptance criteria

- [X] 4. Statute `astral.config.pass-threshold-vs-score-floor` is retired/removed from the active catalog; Code Rules §2.1 no longer teaches pass_threshold; a score_floor **pattern** exists and is the cited authority.
- [X] 5. No active pattern or statute remains whose subject is pass_threshold.

## Boundaries

Does not own runtime strip/verdict (sibling Ada) or admin dropdown (sibling Katherine).

## In scope

- [X] `pattern.dispatch.score-floor` — author under `canon/patterns/dispatch/` as approved sole-floor pattern
- [X] `astral.config.pass-threshold-vs-score-floor` — soft-retire; remove from active statutes README index
- [X] `astral.config.config-source-of-truth` — Code Rules §2.1 still cites config/dispatch-row ownership; floor not hardcoded in core prose
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/foundation/ast-1279-…`
- [X] `docs/ASTRAL_CODE_RULES.md` §2.1 (+ §2.2 prose drop of `pass_threshold`) — teach score_floor pattern, not dual-floor statute
- [X] `canon/patterns/README.md` + `HARVEST.md` / `canon/statutes/README.md` + `HARVEST.md` — index honesty

## Considered but excluded

- [X] `src/core/**` / `src/utils/config.py` runtime — owned by AST-1277 (User Testing)
- [X] Admin Score Floor UI / `DISPATCH_SCORE_FLOOR_VALUES` edits — owned by AST-1278 (User Testing); pattern only *cites* those symbols
- [X] `tests/` / `docs/test-bible/**` — Betty; engineer ban
- [X] Historical `docs/features/**` plans that merely cite the old statute — leave as history
- [X] Universal `orch.*` — not listed per-child
- [X] Turning score-floor into a coding statute — parent boundary (pattern only)

## Notes for planning

Score-floor is a pattern (not a coding statute). No pass-threshold pattern or statute left.

## Git branch (authoritative)

Parent `ftr/AST-1275-remove-pass-threshold-from-task-config`; child `sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-08T03:50:26.568Z
[merge-child] blocked: validate-sub-log failed on origin/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern

```
BLOCKED: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>
```

`ftr..sub` range includes `Merge remote-tracking branch` subjects (`7aab460d` origin/dev, `396eb88d` ftr, plus unrelated AST-1274 history pulled via origin/dev). After cleaning those, also need a `test(AST-1279):` commit (docs-acceptance checklist is fine — Betty delivered bible-only).

@Hedy Lamarr — rebuild publish tip stacked on `origin/ftr/AST-1275-remove-pass-threshold-from-task-config` with only AST-1279 commits (no `Merge remote-tracking branch` in the range); keep plan/code/merge-tests/docs/resolve; add `test(AST-1279):` for the docs-acceptance checklist; force-push publish ref. Status stays User Testing.

— Chuckles

#### radia — 2026-08-08T03:48:22.599Z
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1279
**Overall:** CLEAN
**Publish ref tip:** `sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` @ `37d53882` (doc-only review commit on top of `7e85b510`)

Diff `origin/dev...origin/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern`. This child's own authored commits (`code(AST-1279)` ×3 + the bible entry merged via Betty's `merge-tests` line) touch only `canon/statutes/**`, `canon/patterns/**`, `docs/ASTRAL_CODE_RULES.md`, `docs/test-bible/**` — genuinely docs-only, no `src/**`. The `src/core/**` / `src/ui/**` content mechanically present in the three-dot diff arrived via the routine pre-coding `ftr/AST-1275` sync merge and is AST-1277/AST-1278's already-reviewed work, not new AST-1279 content.

Full active-set scored in-session — corpus is **64** `status: active` statutes (down from 65; this ticket's own retirement removed the 65th). No fix-now, no discuss.

**What's solid:**

- **Approval chain verified independently, not just cited.** Fetched [AST-1281](https://linear.app/astralcareermatch/issue/AST-1281/unblock-ast-1279-approve-patterndispatchscore-floor-or-reword-ac4) directly: Susan's comment reads "`pattern.dispatch.score-floor` is approved. proceed." (2026-08-08T02:54:35Z) — exact id match, timestamp precedes/matches the pattern file's `approved_at: "2026-08-08"`. `orch.pipeline.call-susan-for-product-decisions` and `orch.roles.archie-approves-statutes` (both universal) conform on the merits.
- **`pattern.dispatch.score-floor.md` is fully SCHEMA-compliant:** all 10 required frontmatter keys, no undeclared keys, correct body order, `canonical_refs` ≥1 with all 3 code symbols real on the merged tree.
- **Retired statute stub matches SCHEMA + corpus precedent:** `status: retired`, original `approved_by`/`approved_at` kept (flip-status-only, same shape as the three retired `astral.patterns.*` statutes), `superseded_by: null` correctly typed (successor is a pattern, not a statute — recorded in prose instead).
- **Index honesty checked, not assumed:** counted `canon/patterns/README.md`'s table — "Seven ... approved" is correct. `rg pass_threshold canon/patterns` on this tip: no live hits. Statutes README/HARVEST and patterns README/HARVEST all consistent.
- **Parent boundary honored:** lives under `canon/patterns/dispatch/`, not `canon/statutes/**` — did not turn score-floor into a coding statute; pattern's own `## When not to use` carries that anti-trigger.
- **Test-tree boundary held:** the only `docs/test-bible/**` change arrives via Betty's `merge-tests(AST-1279)` line; none of Hedy's `code(AST-1279)` commits touch it.
- Nice real-world statute validation for the record: Joan's first spawn correctly bounced with "not run — entry gate" while status was `Todo` (`orch.pipeline.status-gates-skill-entry`), and the approval question correctly routed to Susan via a gate ticket rather than self-stamped (`orch.pipeline.call-susan-for-product-decisions`).

**Not-applicable:** ~40 `src/**`/`scripts/**`-scoped statutes don't match this diff's own layer set (`docs` only) — outside scope for a docs-only child.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.dispatch.score-floor` | conforms | The pattern this ticket authors — `status: approved` with a real, independently-checked Archie/Susan approval, SCHEMA-complete frontmatter, canonical_refs real on tree. |

**Carryover advisory (Joan, non-blocking):** `canonical_refs` includes one docs pointer in a field SCHEMA describes as "real implementations" — the three code refs satisfy ≥1 on their own. Not this ticket's to fix.

## Frame diff

(none) — no scope drift; description checkboxes already match delivered behavior.

context_tokens≈46000

— Radia

#### betty — 2026-08-08T03:41:40.623Z
## QA test manifest

**Publish:** `origin/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` @ `7e85b510`
**merge-tests:** `merge-tests(AST-1279): origin/tests 70890b463e05ff4dec7a01600d935e5183460ebc`

**Docs-acceptance only** — no pytest / Vitest / zero-arg harness. Tip already has statute retired, `pattern.dispatch.score-floor` Archie-approved, CODE_RULES §2.1 sole-floor. Runtime strip / admin `0` stay under AST-1277 / AST-1278.

### 1. Existing coverage

None for this child’s stages (canon + CODE_RULES only).

### 2. Broken / obsolete

None.

### 3. Gaps (this pass)

None (no new component/integration tests).

### Docs-acceptance checklist (`test-child` on publish tip)

1. `canon/statutes/astral/config/astral.config.pass-threshold-vs-score-floor.md` — `status: retired`; Statement names `pattern.dispatch.score-floor`
2. Statutes README — no active harvested row for that id; HARVEST crosswalk `retired (AST-1279)`
3. `canon/patterns/dispatch/pattern.dispatch.score-floor.md` — `status: approved`, `approved_by: Archie`
4. Patterns README — id listed among approved; HARVEST / supporting package honest
5. `docs/ASTRAL_CODE_RULES.md` §2.1 — cites `pattern.dispatch.score-floor`; does not teach `pass_threshold` as a live TASK_CONFIG key
6. `rg pass_threshold canon/patterns` — anti-trigger / HARVEST only (no live pass-threshold pattern)

Bible map: `### AST-1279` in `docs/test-bible/README.md`; consult/config pointers updated.

### Bible shasums (`origin/<publish-ref>`)

- `docs/test-bible/README.md` `18873c9420ce44fa0001df9158941a4d5ddb9c2e`
- `docs/test-bible/core/consult.md` `c569e54afde98b126491c7785e7fc85c37c3e723`
- `docs/test-bible/utils/config.md` `5370b70704df750cad289a73e8364d48c45dfb5b`

— Betty

#### joan — 2026-08-08T03:36:32.373Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1279
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` @ `91667211` (unchanged since the ESCALATE pass — the blocker was a ruling, not a plan defect)
**Plan Discuss:** 0 completed rounds — the prior pass escalated from `Plan Ready` and never entered the loop.

## Traceability

AC4→S1–S3; AC5→S1 (parent Functional scope 5 → S1–S3; parent AC4→S1–S3; AC5→S1). No orphan stages.

**Considered:** full active corpus scored in-session; unchanged from the prior pass since neither the plan nor the corpus moved. No `violates` remain.

## Findings

**The escalation is resolved, and I checked the ruling rather than the hand-off.** [AST-1281](https://linear.app/astralcareermatch/issue/AST-1281/unblock-ast-1279-approve-patterndispatchscore-floor-or-reword-ac4) is `Done`, and Susan's comment there reads "`pattern.dispatch.score-floor` is approved. proceed." That is the **exact id** Stage 2 authors — no id drift to reconcile, so the parent's "or Archie-final id" escape hatch is not needed. Archie chose the **Approve now** branch, which means Stage 2's `status: approved` / `approved_by: Archie` frontmatter is now the correct thing to land rather than a self-stamp, AC4's "cited authority" is satisfiable, and no AC rewording is required. The approval landed 2026-08-08, matching the `approved_at: "2026-08-08"` the plan already writes.

On the optional second question: Susan did not separately address the Stage 1 soft-retire, but "proceed" over a gate ticket that spelled it out, on top of parent AC4 ordering the retirement outright, is authorization enough. My prior reading stands — keeping the original `approved_by: Archie` / `approved_at: "2026-07-23"` and flipping only `status` matches how the three retired `astral.patterns.*` statutes were recorded, so `orch.roles.archie-approves-statutes` is satisfied in both letter and practice.

**discuss — record where the approval lives.** The pattern's `## Notes` cites AST-1275 / AST-1277 / AST-1278 / AST-1279 lineage but not [AST-1281](https://linear.app/astralcareermatch/issue/AST-1281/unblock-ast-1279-approve-patterndispatchscore-floor-or-reword-ac4), where the approval is actually recorded. `proposed_in: AST-1275` satisfies SCHEMA's lineage requirement on its own, so this is not blocking — but a reader auditing the `approved_by: Archie` stamp six months from now has nowhere to go. Worth one clause in `## Notes` while Hedy is in the file.

**discuss — `canonical_refs` includes a docs section** (carried from the prior pass, unchanged). `{path: docs/ASTRAL_CODE_RULES.md, symbol: "§2.1"}` sits in a field SCHEMA describes as "real implementations"; the three code refs carry the `approved`-entry requirement on their own. Non-blocking.

**acceptable — re-verified that nothing drifted under the escalation.** The plan tip is still `91667211` with an empty diff against what I reviewed, and the corpus is unchanged where it matters: `canon/patterns/README.md` still reads "Six catalog entries below are `status: approved`; one is `status: proposed`" (so the six-to-seven edit is still correct arithmetic), the `canon/statutes/README.md` row is still at L48, `canon/patterns/**` still has zero `pass_threshold` hits, and the target statute is still `status: active` awaiting this retirement. Every finding from the ESCALATE comment therefore carries forward intact: SCHEMA-complete frontmatter with no undeclared keys, body sections in required order, all three code `canonical_refs` real on the epic branch, exhaustive Code Rules coverage at L84 / L100–106 / L119, correct `superseded_by: null` typing, and the parent's pattern-not-statute boundary honored in the pattern's own anti-triggers.

Proceed as written: Hedy lands Stage 2 at `status: approved` citing the [AST-1281](https://linear.app/astralcareermatch/issue/AST-1281/unblock-ast-1279-approve-patterndispatchscore-floor-or-reword-ac4) ruling.

— Joan

context_tokens≈128000

#### joan — 2026-08-08T02:15:08.854Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1279
**Overall:** ESCALATE
**Publish ref tip:** `sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` @ `91667211`
**Plan Discuss:** 0 completed rounds — escalating from Plan Ready before the discuss loop, so status stays `Plan Ready`.

## Traceability

AC4→S1–S3; AC5→S1 (parent Functional scope 5 → S1–S3; parent AC4→S1–S3; AC5→S1). No orphan stages.

**Considered:** full active corpus scored in-session. Plan layers `docs` (canon + `docs/**`), so the `src/**`-scoped set is excluded on layer/path; universal `orch.*` all considered, with `orch.roles.archie-approves-statutes` load-bearing here.

## Escalation — @susan

**Only Archie can settle the approval stamp on the new pattern, and the plan cannot be revised into compliance without that ruling.**

Stage 2 creates `canon/patterns/dispatch/pattern.dispatch.score-floor.md` directly at `status: approved` with `approved_by: Archie` and `approved_at: "2026-08-08"`. `canon/patterns/AUTHORING.md` § Lifecycle reserves that: **Propose** is what an engineer lands (`status: proposed`, `approved_by: null`, `approved_at: null`), and **Approve** has "Who drafts: — / Who approves: Archie". The parent's architectural definition says the same in as many words: "**Archie approval required** before implementation depends on the catalog id." There is no Archie approval recorded anywhere on AST-1275 or AST-1279, so as written an engineer would be stamping your approval.

The reason this is escalate rather than a revise: flipping to `proposed` does not satisfy this ticket's own AC4. `canon/patterns/SCHEMA.md` excludes `proposed` from the approved set and states "Implementation must **not** depend on this id until `approved`", while AC4 requires the pattern to exist and be **the cited authority** in Code Rules §2.1. Both branches are blocked without you:

- **Approve now** — you confirm `pattern.dispatch.score-floor` (id as written, or your preferred id), Hedy lands `status: approved` citing that approval, and §2.1 cites it as authority. Hedy's plan already anticipates either outcome and says she will flip only the frontmatter status fields on your word.
- **Land as proposed** — then AC4 needs rewording, because §2.1 would be citing a non-approved id.

While you are in there: the same ruling covers the Stage 1 retirement of `astral.config.pass-threshold-vs-score-floor`. `orch.roles.archie-approves-statutes` requires Archie approval for a retire, recorded in frontmatter. The plan keeps the original `approved_by: Archie` / `approved_at: "2026-07-23"` and flips only `status`, which matches how the three retired `astral.patterns.*` statutes were recorded, and parent AC4 orders the retirement outright — so I read that as authorized rather than defective. One line from you confirming it removes the ambiguity for Radia later.

## Findings

**discuss — `canonical_refs` includes a docs section.** `{path: docs/ASTRAL_CODE_RULES.md, symbol: "§2.1"}` sits in a field SCHEMA describes as "real implementations". The three code refs carry the requirement on their own; the docs entry is arguably a `related` pointer wearing the wrong hat. Non-blocking.

**acceptable — the corpus mechanics all check out against the tree, not just the prose.** The new pattern file carries all ten SCHEMA-required frontmatter keys with no undeclared extras, and its body is in the required order (`# Problem`, `# Solution shape`, `## When not to use`, `## Notes`). `canon/patterns/dispatch/` already exists. The `approved`-entry rule of ≥1 `canonical_refs` is met, and — contrary to what I expected before checking — all three code symbols are **real on the epic branch today**: `effective_dispatch_score_floor` (`config.py:2905`) and `_dispatch_score_floor_for_task` (`consult.py:155`) are already on `origin/ftr/AST-1275-…` from AST-1277, and `DISPATCH_SCORE_FLOOR_VALUES` is on `origin/dev`. Hedy's `Conf: high` justification that the siblings shipped the cited symbols is accurate, and AST-1278 is in User Testing, so the landing order this plan assumes actually holds.

**acceptable — index and prose edits are exhaustive.** I swept the tree: `canon/patterns/**` contains **zero** `pass_threshold` mentions today, so Stage 1 step 5's expectation of zero hits there is correct and will not trip its own stop-and-escalate clause. The only active statute teaching `pass_threshold` is the one being retired. In `docs/ASTRAL_CODE_RULES.md` the string appears at exactly three sites — the §2.1 TASK_CONFIG bullet (L84), the `#### pass_threshold vs dispatch_task.score_floor` subsection (L100–106), and the §2.2 parenthetical (L119) — and Stage 3 covers all three, so AC4's "no longer teaches pass_threshold" is genuinely reachable. The `canon/statutes/README.md` row (L48) and `HARVEST.md` crosswalk row (L17) exist in the shape the plan describes, and the patterns README count sentence is verbatim what the plan quotes, with the six-to-seven arithmetic right.

**acceptable — `superseded_by: null` is the correct call.** SCHEMA types that field as a successor **statute** id, so putting a pattern id there would be a type violation. Recording the successor in the Statement prose and in Code Rules instead is the right shape, and the plan says so explicitly.

**acceptable — parent boundary honored.** The parent forbids turning score-floor into a coding statute, and the pattern body itself carries that as an anti-trigger under `## When not to use`. No `src/**`, no `tests/`, no test-bible, and historical feature plans citing the old statute are deliberately left as history.

Nothing here is a `fix-now` that Hedy can act on alone — the plan is in good shape and waits only on your ruling. Status stays `Plan Ready`.

— Joan

context_tokens≈118000

#### joan — 2026-08-08T02:11:12.490Z
[validate-plan] not run — entry gate

Joan was spawned for AST-1279, but the `validate-plan` entry conditions are not met, so no rubric pass ran and no status was changed.

- **Status is `Todo`.** `validate-plan` enters only from `Plan Ready` or `Plan Discuss` (`orch.pipeline.status-gates-skill-entry`).
- **Assignee is Hedy.** Chuckles must assign Joan (and seed `Active/joan`) before a validation pass.

Worth flagging because the git side is ahead of the Linear side: a plan doc **is** published at `origin/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` @ `91667211` (`docs/features/foundation/ast-1279-retire-pass-threshold-statute-author-score-floor-pattern.md`), but this ticket has no plan-published comment, no plan attachment, and never left `Todo`. So the graduation step after `plan-child` looks incomplete rather than the plan being missing.

Also note AST-1279 is `blockedBy` **AST-1277** and **AST-1278**; AST-1277 reached `Plan Approved` but neither sibling has shipped, so `Todo` may well be intentional for now.

No status flip, no assignee change, no rubric verdict from me on this pass. Re-spawn once the ticket is `Plan Ready` with Joan assigned and I will run `plan-rubric.v1` against that tip.

— Joan

context_tokens≈104000

#### hedy — 2026-08-08T02:09:36.117Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern/docs/features/foundation/ast-1279-retire-pass-threshold-statute-author-score-floor-pattern.md

`origin/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` @ `91667211`

**Scope:** Single-Component — soft-retire the pass-threshold statute, author `pattern.dispatch.score-floor`, rewrite Code Rules §2.1/§2.2 prose; no `src/**`.

**Conf:** high — AUTHORING/SCHEMA paths are clear; AST-1277 already shipped `effective_dispatch_score_floor` / `_dispatch_score_floor_for_task` that the pattern cites; soft-retire matches existing corpus practice.

**Risk:** Medium — incomplete index cleanup or a wrong approval stamp would leave Joan/Radia citing dead dual-floor law; this ticket itself has no runtime regression surface.

---

# AST-1279 — Retire pass-threshold statute; author score_floor pattern + Code Rules

**Linear:** [AST-1279](https://linear.app/astralcareermatch/issue/AST-1279/retire-pass-threshold-statute-author-score-floor-pattern-code-rules)
**Parent:** [AST-1275](https://linear.app/astralcareermatch/issue/AST-1275/remove-pass-threshold-from-task-config) — Remove "pass_threshold" from task_config
**Publish ref:** `sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern`

Retire active statute `astral.config.pass-threshold-vs-score-floor`, author approved catalog pattern `pattern.dispatch.score-floor`, and rewrite Code Rules §2.1 (plus the one §2.2 prose mention) so law matches shipped AST-1277 / AST-1278 behavior: `dispatch_task.score_floor` is the sole numeric floor (claim + scored soft-fail), explicit `0` is valid, and no `pass_threshold` key / statute / pattern remains. Docs and canon only — no runtime product edits.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/statutes/astral/config/astral.config.pass-threshold-vs-score-floor.md` | Soft-retire (`status: retired`); statement notes successor pattern | canon / statutes |
| `canon/statutes/README.md` | Remove this id from the active harvested-corpus table | canon / statutes |
| `canon/statutes/HARVEST.md` | Mark crosswalk row retired (AST-1279) | canon / statutes |
| `canon/patterns/dispatch/pattern.dispatch.score-floor.md` | New — `status: approved` pattern (SCHEMA order) | canon / patterns |
| `canon/patterns/README.md` | Index the new approved pattern; bump approved count | canon / patterns |
| `canon/patterns/HARVEST.md` | Add crosswalk + supporting-package cite row | canon / patterns |
| `docs/ASTRAL_CODE_RULES.md` | §2.1: drop `pass_threshold` from TASK_CONFIG bullet; replace subsection with score_floor pattern; §2.2 drop `pass_threshold` from the example list | docs |

**Out of files (do not touch):** `src/**` (runtime owned by AST-1277 / AST-1278); `tests/` / `docs/test-bible/**` (Betty); sibling plan docs; historical feature plans that merely *cite* the retired statute (leave as historical); Linear text on sibling tickets.

---

## Stages

### Stage 1: Retire statute + index cleanup

**Done when:** `astral.config.pass-threshold-vs-score-floor` frontmatter has `status: retired` and the file still exists at its current path. `canon/statutes/README.md` harvested-corpus table no longer lists that id as an active row. `rg -n 'status: active' canon/statutes/astral/config/astral.config.pass-threshold-vs-score-floor.md` returns no matches. A catalog sweep of `canon/patterns/**` and `canon/statutes/**` finds no *active* statute and no pattern (any status) whose subject is `pass_threshold` / `pass-threshold` besides the retired statute file itself.

1. In `canon/statutes/astral/config/astral.config.pass-threshold-vs-score-floor.md`, change frontmatter only as follows (keep `id`, `title`, `tier`, `checkable`, `applies_when`, `source_docs`, `supersedes`, `approved_by`, `approved_at` unchanged):
   - `status: retired`
   - `superseded_by: null` (successor is a **pattern**, not a statute id — do not put `pattern.dispatch.score-floor` in `superseded_by`)

2. In the same file, replace the `# Statement` body (and Examples) so the retired file cannot be read as current law. Exact replacement after frontmatter:

   ```markdown
   # Statement

   **Retired (AST-1279).** Former rule that split `TASK_CONFIG.pass_threshold` (post-run grading) from `dispatch_task.score_floor` (claim gating only) is withdrawn. Authority for the numeric floor is pattern `pattern.dispatch.score-floor` — sole floor on the candidate’s `dispatch_task` row for both eligibility and scored soft-fail. Do not resurrect `pass_threshold` on `TASK_CONFIG`.

   ## Rationale

   Kept for citation history only. Active consumers must not treat this file as binding.

   ## Examples

   ### Conforming

   - (retired — see `pattern.dispatch.score-floor`)

   ### Violating

   - (retired — see `pattern.dispatch.score-floor`)
   ```

3. In `canon/statutes/README.md`, delete the harvested-corpus table row whose first column is `` `astral.config.pass-threshold-vs-score-floor` `` (the full markdown table row). Do not add a “retired” section; discovery is file frontmatter `status: active` (AUTHORING / README universal/scoped rules).

4. In `canon/statutes/HARVEST.md`, update the crosswalk row for `` `astral.config.pass-threshold-vs-score-floor` `` so the Status column becomes `create (AST-921), retired (AST-1279)` (keep id/tier/checkable/source/path columns).

5. Verify with ripgrep from repo root (expect **only** the retired statute file + historical docs/features / test-bible prose — not a second active statute or any `canon/patterns/**` file teaching `pass_threshold`):

   ```bash
   rg -n 'pass.threshold|pass_threshold' canon/statutes canon/patterns
   ```

   Allowed hits under `canon/`: the retired statute file (retirement wording) and zero matches under `canon/patterns/`. If any other `status: active` statute still teaches pass_threshold, **stop** and comment on the Linear **parent** (AST-1275) with the path — do not invent a second retirement in this ticket.

⚠️ **Decision:** Soft-retire (file remains) per `canon/statutes/AUTHORING.md`. `superseded_by` stays `null` because SCHEMA typed that field as a statute successor id; the replacement authority is recorded in the Statement prose and in Code Rules as `pattern.dispatch.score-floor`.

### Stage 2: Author `pattern.dispatch.score-floor` + pattern indexes

**Done when:** `canon/patterns/dispatch/pattern.dispatch.score-floor.md` exists with `status: approved`, SCHEMA-required frontmatter, and body sections in SCHEMA order. `canon/patterns/README.md` lists it under Harvested corpus as approved. `canon/patterns/HARVEST.md` has a crosswalk row and a supporting-package cite. No `pass_threshold` string appears in the new pattern file.

1. Create `canon/patterns/dispatch/pattern.dispatch.score-floor.md` with **exactly** this content (domain folder `dispatch/` already exists beside `pattern.dispatch.run-next-chain-authority.md`):

   ```markdown
   ---
   id: pattern.dispatch.score-floor
   name: dispatch_task.score_floor as sole numeric floor
   status: approved
   proposed_in: AST-1275
   approved_by: Archie
   approved_at: "2026-08-08"
   canonical_refs:
     - path: src/utils/config.py
       symbol: effective_dispatch_score_floor
     - path: src/utils/config.py
       symbol: DISPATCH_SCORE_FLOOR_VALUES
     - path: src/core/consult.py
       symbol: _dispatch_score_floor_for_task
     - path: docs/ASTRAL_CODE_RULES.md
       symbol: "§2.1"
   related_statutes:
     - astral.config.config-source-of-truth
     - astral.standards.no-hardcoded-sets
     - astral.idioms.render-verdict-orchestrates-consult
   supersedes: null
   superseded_by: null
   ---

   # Problem

   Scored consult / prefilter hops need one numeric floor for eligibility and post-run pass vs soft-fail. A parallel `TASK_CONFIG` threshold (`pass_threshold`) drifts from the candidate’s `dispatch_task` row and reintroduces magic floors.

   # Solution shape

   Treat `dispatch_task.score_floor` on the candidate’s matching row as the **sole** numeric floor for a scored step:

   - **Claim / count eligibility** and **scored soft-fail after the run** both read that row value (via `effective_dispatch_score_floor` / `_dispatch_score_floor_for_task` — pointers in `canonical_refs`).
   - Explicit `0` / `0.0` is valid and means no numeric soft-fail / no claim exclusion by floor.
   - `NULL` / missing normalizes to `1.0` for those paths (existing claim rule; same helper for verdict).
   - Do **not** put a numeric floor on `TASK_CONFIG`. Do **not** invent a coding statute for this concept — pattern only.
   - Dealbreaker (F-with-confidence) and technical-error fail paths stay outside the numeric floor.
   - Admin Score Floor options come from config (`DISPATCH_SCORE_FLOOR_VALUES` / labels API), including `0`.

   Point at `canonical_refs` — do not paste large code into this catalog entry.

   ## When not to use

   - Non-scored hops that do not consult `latest_score` / soft-fail math.
   - Resurrecting `pass_threshold` (or any synonym) on `TASK_CONFIG` as a second floor.
   - Turning this package into a coding statute under `canon/statutes/**`.

   ## Notes

   Proposed in parent AST-1275 architectural definition; runtime landed by AST-1277 / admin `0` by AST-1278; catalog + Code Rules by AST-1279. Retires the teaching of `astral.config.pass-threshold-vs-score-floor`.
   ```

2. In `canon/patterns/README.md`:
   - Update the Harvested corpus intro sentence so the approved count includes this entry (today: “Six catalog entries below are `status: approved`; one is `status: proposed`.” → seven approved, one proposed).
   - Append a table row: `` `| `pattern.dispatch.score-floor` | approved | `dispatch/pattern.dispatch.score-floor.md` |` `` after the existing `pattern.dispatch.run-next-chain-authority` row (or immediately above it if you prefer approved-before-proposed — either order is fine as long as the row exists once).

3. In `canon/patterns/HARVEST.md`:
   - Under **Supporting harvest packages**, add a row: `` `| dispatch score_floor (sole numeric floor) | `pattern.dispatch.score-floor` |` ``
   - Under **Crosswalk**, add: `` `| create (AST-1279) | `pattern.dispatch.score-floor` | dispatch | `dispatch/pattern.dispatch.score-floor.md` | AST-1275 / CODE_RULES §2.1 | approved — sole numeric floor; retires pass-threshold statute teaching |` ``

⚠️ **Decision:** Land `status: approved` with `approved_by: Archie` / `approved_at: "2026-08-08"`. Parent AST-1275 architectural definition named `pattern.dispatch.score-floor`, open questions none, and children 1–2 already shipped against that shape; ticket AC requires the pattern to be the cited authority (approved set). If Joan / Archie rejects the approval stamp during validate-plan, flip only the frontmatter status fields to `proposed` / `approved_by: null` / `approved_at: null` in a Plan Discuss revision — do not invent a different id.

### Stage 3: Rewrite Code Rules §2.1 (+ §2.2 prose)

**Done when:** `docs/ASTRAL_CODE_RULES.md` §2.1 no longer teaches `pass_threshold`; the old `#### pass_threshold vs dispatch_task.score_floor` subsection is gone and replaced by a score_floor subsection that cites **`pattern.dispatch.score-floor`** (not the retired statute). `rg -n 'pass_threshold' docs/ASTRAL_CODE_RULES.md` returns no matches. TASK_CONFIG bullet no longer lists `pass_threshold`.

1. In `docs/ASTRAL_CODE_RULES.md` §2.1 **Config blocks** → **TASK_CONFIG** bullet, replace the orchestration key list so it no longer includes `pass_threshold`. Exact old fragment to edit (keep surrounding sentence structure):

   - Remove `` `pass_threshold`, `` from the list that currently reads: pass/fail/error states, `save_prefix`, `pass_threshold`, readiness keys…

   After edit the orchestration clause must still list pass/fail/error states, `save_prefix`, readiness keys (`min_job_title_length`, `min_jd_chars`, `not_ready_state`), `requires_company`, and `fallback_batch_size` — **without** any threshold key.

2. In the same §2.1, replace the entire subsection headed `#### pass_threshold vs dispatch_task.score_floor` (including its `**Statute:** …` line and all three bullets) with:

   ```markdown
   #### dispatch_task.score_floor (sole numeric floor)

   **Pattern:** `pattern.dispatch.score-floor`

   - **`score_floor`** (on the candidate’s matching **`dispatch_task`** row) is the **only** numeric floor for a scored step: dispatch eligibility (claim/count) and post-run scored soft-fail / pass both read that row value via `effective_dispatch_score_floor` (explicit `0` valid; `NULL` → `1.0`).
   - Do **not** put a parallel floor on **TASK_CONFIG**. Do **not** cite retired statute `astral.config.pass-threshold-vs-score-floor`.
   - Dealbreaker and technical-error fails are unchanged; admin Score Floor options include `0` (`DISPATCH_SCORE_FLOOR_VALUES`).
   ```

3. In §2.2, edit the sentence that currently says core reads config for “grading_mode, vectors, pass_threshold, state transitions” — drop `pass_threshold` from that parenthetical (e.g. “grading_mode, vectors, state transitions”). Do not otherwise rewrite §2.2.

4. Confirm:

   ```bash
   rg -n 'pass_threshold|pass-threshold-vs-score-floor' docs/ASTRAL_CODE_RULES.md
   ```

   Expect: at most a mention of the **retired** statute id inside the new subsection’s “Do not cite” bullet (the template above includes that once). No teaching that `pass_threshold` is a live TASK_CONFIG key.

⚠️ **Decision:** Keep the retired statute id once in Code Rules as an explicit “do not cite” pointer so agents hunting the old name land on the pattern. Do not re-add a statute citation block for the retired id.

---

## Self-Assessment

**Scope:** Single-Component — canon statute/pattern indexes plus `docs/ASTRAL_CODE_RULES.md` §2.1/§2.2 prose; no `src/**`.

**Conf:** high — AUTHORING/SCHEMA paths are clear; sibling AST-1277 already shipped the symbols this pattern points at; retirement is a soft-retire already used elsewhere in the corpus.

**Risk:** Medium — wrong approved stamp or incomplete index cleanup would leave Joan/Radia citing dead law or a still-active contradictory statute; no runtime regression surface in this ticket itself.

## Rules self-review (§8)

- **§1.3 DRY:** Pattern points at existing helpers; no duplicated code blocks in the catalog.
- **§2.1 config:** Rewrite removes the obsolete dual-floor teaching; pattern aligns with config-owned `DISPATCH_SCORE_FLOOR_VALUES` / `effective_dispatch_score_floor`.
- **§2.4 batch / §2.6 state:** Unchanged; pattern explicitly leaves pass/fail/error state names alone.
- **§3.3 imports / §3.5 naming:** N/A (docs/canon only).
- **Test-tree ban:** Plan does not touch `tests/` or `docs/test-bible/**`.
- **No conflict requiring `conf-!!-NONE`.**

## Review (build)

**Built:** `origin/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` @ `01da708f`

**Stages:**
- Stage 1 `32ddaace` — soft-retire `astral.config.pass-threshold-vs-score-floor`; statutes README/HARVEST index cleanup
- Stage 2 `c7477da0` — approved `pattern.dispatch.score-floor` (Archie via AST-1281); patterns README/HARVEST
- Stage 3 `01da708f` — Code Rules §2.1 sole-floor subsection + TASK_CONFIG/§2.2 prose drop of `pass_threshold`

**Note:** Pattern `## Notes` cites AST-1281 for the Archie approval stamp (Joan discuss on APPROVED pass).

## Review (Radia)

[code-rubric] revision=2 — **Overall: CLEAN**

Diff `origin/dev...origin/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` @ tip. This child's own authored commits (`code(AST-1279)` ×3 + the `docs(AST-1279)` bible entry merged via Betty's line) touch only `canon/statutes/**`, `canon/patterns/**`, `docs/ASTRAL_CODE_RULES.md`, and `docs/test-bible/**` — genuinely docs-only, no `src/**`. The `src/core/**` / `src/ui/**` content mechanically present in this three-dot diff arrived via the routine pre-coding `ftr/AST-1275` sync merge and is AST-1277/AST-1278's already-reviewed work (CLEAN / DISCUSS-no-action-needed), not new AST-1279 content.

Full active-set scored in-session per code-rubric.v2 §5.0 — corpus is **64** `status: active` statutes (down from 65; this ticket's own retirement of `astral.config.pass-threshold-vs-score-floor` removed the 65th). No fix-now, no discuss.

**What's solid:**

- **Approval chain verified independently, not just cited.** Fetched [AST-1281](https://linear.app/astralcareermatch/issue/AST-1281/unblock-ast-1279-approve-patterndispatchscore-floor-or-reword-ac4) directly: Susan's comment reads verbatim "`pattern.dispatch.score-floor` is approved. proceed." (2026-08-08T02:54:35Z) — exact id match, timestamp precedes and matches the pattern file's `approved_at: "2026-08-08"`. `orch.pipeline.call-susan-for-product-decisions` and `orch.roles.archie-approves-statutes` (both universal) conform on the merits, not on trust.
- **`pattern.dispatch.score-floor.md` is fully SCHEMA-compliant:** all 10 required frontmatter keys, no undeclared keys, body in required order (`# Problem` / `# Solution shape` / `## When not to use` / `## Notes`), `canonical_refs` ≥1 with all 3 code symbols real on the merged tree (`effective_dispatch_score_floor`, `DISPATCH_SCORE_FLOOR_VALUES` in `config.py`; `_dispatch_score_floor_for_task` in `consult.py` — all confirmed during the AST-1277/1278 passes).
- **Retired statute stub matches SCHEMA + existing corpus precedent:** `status: retired`, original `approved_by`/`approved_at` kept (flip-status-only, same shape as the three retired `astral.patterns.*` statutes), `superseded_by: null` correctly typed (successor is a *pattern*, not a statute — recorded in prose instead, exactly as SCHEMA requires).
- **Index honesty checked, not assumed:** `canon/patterns/README.md`'s "Seven catalog entries ... approved" — counted the table, seven is correct. `rg pass_threshold canon/patterns` on this tip returns no live hits. Statutes README drops the row; HARVEST crosswalks on both sides annotated `retired (AST-1279)` / `create (AST-1279)`.
- **Parent boundary honored:** the new package lives under `canon/patterns/dispatch/`, not `canon/statutes/**` — this ticket did not turn score-floor into a coding statute, exactly as the parent's boundary required, and the pattern's own `## When not to use` carries that as an explicit anti-trigger.
- **Test-tree boundary held:** the only `docs/test-bible/**` change arrives via Betty's `merge-tests(AST-1279)` line (docs-acceptance, no pytest/Vitest); none of Hedy's `code(AST-1279)` commits touch it.
- Nice real-world statute validation, noted for the record rather than as a finding: Joan's first spawn attempt on this ticket correctly bounced with \"not run — entry gate\" while status was `Todo` (`orch.pipeline.status-gates-skill-entry` working as designed), and the pattern-approval question correctly routed to Susan via a gate ticket rather than being self-stamped (`orch.pipeline.call-susan-for-product-decisions` working as designed).

**Not-applicable (layer/path miss, noted for completeness):** the ~40 `src/**`/`scripts/**`-scoped statutes (agent/batch/state/standards/ui/most seed/layers families) don't match this diff's own layer set (`docs` only) — correctly not scored as violations, just outside scope for a docs-only child.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.dispatch.score-floor` | conforms | The pattern this ticket authors — verified `status: approved` with a real, independently-checked Archie/Susan approval (AST-1281), SCHEMA-complete frontmatter, canonical_refs real on tree. |

**Carryover advisory (Joan, non-blocking, still true):** `canonical_refs` includes one docs pointer (`docs/ASTRAL_CODE_RULES.md` §2.1) in a field SCHEMA describes as "real implementations" — the three code refs satisfy the ≥1 requirement on their own. Not this ticket's to fix; noted for a future pattern-schema pass.

## Frame diff

(none) — no scope drift; description checkboxes already match delivered behavior.

context_tokens≈46000

— Radia

## Resolution

**Date:** 2026-08-08  
**Review:** [code-rubric] revision=2 — **CLEAN** (no fix-now, no discuss).  
**Action:** No product changes. Appended this section; tip advanced with `resolve(AST-1279): — clean`.  
**Publish:** `origin/sub/AST-1275/AST-1279-retire-pass-threshold-statute-author-score-floor-pattern` (post-resolve tip).  
**§9a:** dry-run into `origin/dev` / `origin/ftr/AST-1275-remove-pass-threshold-from-task-config` (run at resolve).  
**Advisory carryover:** Joan/Radia docs `canonical_refs` note — left as-is (non-blocking; not this ticket).
