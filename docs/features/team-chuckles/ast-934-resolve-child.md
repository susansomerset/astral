# resolve-child SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-934](https://linear.app/astralcareermatch/issue/AST-934/resolve-child-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-934-resolve-child`
- **Summary:** Rewrite `team-chuckles/skills/resolve-child/SKILL.md` so resolve runs in `astral-<parent-id>/` on the active `sub/*`, publishes with `git push origin HEAD:sub/…`, keeps mid-pipeline Radia `docs()` intake via merge of `origin/<publish-ref>` (not engineer cherry-pick / Joan), and names **finish-up** (not merge-parent) only for end-of-epic land / merge-clean surprises.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/resolve-child/SKILL.md` | Align worktree, publish, Radia intake, and §9a surprise vocabulary with orientation + ASTRAL_GIT_WORKFLOW | skill (team-chuckles) |

**Out of scope:** `review-child` (AST-935 / #6), other skills, `orientation`, datt templates, `install.sh`, astral law docs (#17–#18). Docs/templates only — no product `src/` changes.

**Publish note:** Skill edits commit in **team-chuckles**. This plan doc lands only on **`origin/sub/AST-909/AST-934-resolve-child`**.

## Authority for the rewrite

1. **Ticket To-be:** keep Radia doc intake mid-pipeline (unchanged ceremony intent); rename parent-close surprises → **finish-up** only where that means end-of-epic land, not Radia findings.
2. **Parent clarification:** finish-up is only Chuckles parent-close after PR Ready. Radia findings stay mid-pipeline via review-child `docs()` + resolve-child intake. Renaming merge-parent→finish-up is vocabulary for end-of-epic / merge-clean wording — not shuttling Radia docs into finish-up.
3. **`orientation` § What never happens:** Cherry-pick onto published branches; Joan / `git-store-*` / `JOAN_SESSION`. Worktree = `<reponame>-<IssueID>/`; **Not used:** `astral-ada`, `dev-<agent>`.
4. **`orientation` § Merge on checkout** + ASTRAL_GIT_WORKFLOW: checkout `sub/<parent>/<child>` in epic worktree; merge `origin/ftr/<parent-segment>`; publish with `git push origin HEAD:sub/…`. Commit type **`resolve(<ticket-id>)`**.
5. Acceptance: resolve-child still documents Radia mid-pipeline `docs()` on the publish ref / epic worktree — **not** deferred to finish-up.

## Stage 1: Worktree + publish path (§ Who / §4 / §9)

**Done when:** resolve-child tells the engineer to work in `astral-<parent-id>/` on `sub/<parent>/<child>`, merge `origin/dev` + `origin/ftr/<parent-segment>` + `origin/<publish-ref>`, and publish with `git push origin HEAD:sub/…` — zero Joan / `git-store-*` / `store-resolve-commit` / `dev-ada`/`astral-<agent>` checkout instructions.

1. Open `~/team-chuckles/skills/resolve-child/SKILL.md`.

2. Replace **`astral-<agent>`** + **`git checkout epic worktree`** / persistent nameless epic line with:

   - Workspace = **`$CHUCKLES_ROOT/astral-<parent-id>/`** (e.g. `astral-AST-909/`).
   - Branch = ticket **`sub/<parent-id>/<child-segment>`** from parent **## Git** / spawn **`<publish-ref>`** (not Linear `gitBranchName`).
   - Attach order every resolve pass:

     ```bash
     git fetch origin
     git checkout sub/<parent-id>/<child-segment>
     git merge origin/dev
     git merge origin/ftr/<parent-segment>   # when parent In Progress
     git merge origin/<publish-ref>          # product + Betty test() + Radia docs() tip
     ```

   - Then **Merge-clean gate** vs `origin/dev` before §6.

3. Rewrite publish (sections that currently say “Publish via Joan” / `git.sh store-resolve-commit … --session $epic worktree`) to:

   ```bash
   git commit -m "resolve(<ticket-id>): — findings addressed"
   # or: resolve(<ticket-id>): — clean
   git push origin HEAD:sub/<parent-id>/<child-segment>
   ```

   Confirm tip with `git ls-remote` vs `git rev-parse HEAD`. On failure: `[check-linear] blocked:` + orientation merge-conflict routing — **no cherry-pick**, **never `@susan`** for hunks.

4. Delete live procedure mentions of: `Joan`, `git-store-*`, `JOAN_SESSION`, `store-resolve-commit`, `git.sh`, Joan `rollup` / `prep-uat-git` / `land-ftr` as engineer-facing publish. In §2 Outcome, rewrite **`prep-uat` (Chuckles → Joan)… Joan `prep-uat-git` / `land-ftr`** to Chuckles **`prep-uat`** only (no Joan).

5. Rewrite **Forbidden** so checking out the ticket `sub/*` in the epic worktree is **required**; still forbid creating new `ftr/`/`sub/` refs, cherry-picking onto publish refs, pushing `origin/dev`, and dragging other tickets’ commits onto this publish tip.

⚠️ **Decision:** Publish = direct push of the checked-out sub tip (same ceremony as the AST-931 build-child plan). Do not reintroduce Joan.

## Stage 2: Radia mid-pipeline `docs()` intake — keep intent, drop engineer cherry-pick (§5 + §4 cross-refs)

**Done when:** A reader of resolve-child alone still sees that Radia’s mid-pipeline `docs()` land on `origin/<publish-ref>` and the engineer must have those commits on the working line before User Testing — and the live intake step is **merge `origin/<publish-ref>`**, not `git cherry-pick` / not finish-up.

1. Keep §5’s **purpose**: engineer must absorb Radia’s plan-doc review commits before / while resolving fix-now items.

2. Replace the live **`git cherry-pick <sha>`** primary path with:

   - **Primary:** after §4 merges, Radia’s `docs(<ticket-id>): Radia review — …` commits are already on `origin/<publish-ref>`; merging that tip onto the checked-out sub **is** the intake.
   - **Conflict recovery only:** `git checkout <sha> -- docs/features/<project>/<slug>.md` where `<sha>` is already reachable from `origin/<publish-ref>`, then commit on the sub — not a publish cherry-pick.
   - **Do not** instruct `git cherry-pick` onto the sub as the happy path (orientation never-list).
   - **Do not** move Radia findings to finish-up; finish-up is end-of-epic only.

3. Update any prose that says “Apply §5 Radia doc cherry-picks onto epic worktree” to “confirm Radia `docs()` are present via `git merge origin/<publish-ref>` / `git log` on the sub.”

4. Leave §6–§8 / §10–§11 behavior (fix-now / discuss / advisory / qa-handoff / review-handoff / Resolution section / compile-lint / User Testing assignee rules) intact except where they embed retired git vocabulary.

⚠️ **Decision:** Ceremony intent preserved = Radia `docs()` still mid-pipeline on the publish ref and must be on the engineer’s line before User Testing. Mechanism = merge publish tip (already seeded by review-child), not engineer self-cherry-pick.

## Stage 3: §9a merge-clean surprises → finish-up vocabulary + AC grep

**Done when:** §9a describes catching prep-uat / **finish-up** (end-of-epic land) surprises while the engineer still owns the ticket; “merge-parent” appears only as a deliberate deprecation note if at all; AC grep on this file is clean.

1. In §9a intro (“catches prep-uat / merge-parent surprises…”), replace **merge-parent** with **finish-up** and one clarifying clause: finish-up = Chuckles parent-close after PR Ready / ftr→dev land — **not** the channel for Radia findings.

2. Keep the `merge-tree` dry-run vs `origin/dev` and vs `origin/ftr/<parent-segment>` as-is (behavior unchanged).

3. In §9a “If blocked” republish step: Joan → `git push origin HEAD:sub/…` (Stage 1).

4. In §11, keep `merge-child` / `prep-uat` naming; do not rename those to finish-up. finish-up is only the end-of-epic operator close.

5. Acceptance grep:

   ```bash
   rg -n 'Joan|git-store|JOAN_SESSION|store-resolve-commit|store-code-commit|self-cherry-pick|dev-ada|dev-hedy|dev-katherine|<joan-uuid>|astral-<agent>|git\.sh store|merge-parent' \
     ~/team-chuckles/skills/resolve-child/SKILL.md
   ```

   Expected: empty, or only explicit deprecation / historical notes — no live Joan, cherry-pick publish, `dev-ada`, or “merge-parent” as the operator surprise/close name. Confirm the file still states Radia mid-pipeline `docs()` intake (search for `docs(` / Radia / publish-ref).

6. Commit in **team-chuckles**: `code(AST-934): align resolve-child intake and finish-up wording`. Do not commit skill changes into astral. Do not run `install.sh` (AST-945).

## Execution contract

- Stages in order; only `resolve-child/SKILL.md`; no `review-child` edits.
- If Radia intake wording would delete mid-pipeline `docs()` entirely, stop and 🛑 on **AST-909** — that violates ticket AC.
- After team-chuckles `code(AST-934)` commit, astral publish ref already holds this plan via `plan(AST-934)`.

## Self-Assessment

**Scope:** `Single-Component` — one skill file in team-chuckles; plan doc only on astral `sub/*`.

**Conf:** `high` — residue is localized (Joan publish, cherry-pick §5, merge-parent in §9a, `astral-<agent>`); ticket + parent clarifications explicitly preserve Radia mid-pipeline intake while forbidding cherry-pick/Joan.

**Risk:** `low` — docs/templates only; main failure mode is accidentally dropping Radia intake or mis-naming finish-up as Radia’s channel — both guarded by Stage 2 decision + AC grep.

## Review

- **Branch:** `origin/sub/AST-909/AST-934-resolve-child`
- **Plan tip:** `9116482` (`plan(AST-934)`)
- **team-chuckles:** `origin/main` @ `9fc6810` — `code(AST-934): align resolve-child intake and finish-up wording`
- **Built:** `~/team-chuckles/skills/resolve-child/SKILL.md` — epic `astral-<parent-id>/` + `sub/*` + push; Radia `docs()` intake via merge of publish tip; §9a surprises → finish-up; Joan/cherry-pick/`merge-parent` operator language removed.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-909/AST-934-resolve-child`; skill deliverable `team-chuckles@9fc6810` (`skills/resolve-child/SKILL.md`).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–3: epic `astral-<parent-id>/` + `sub/*` + merge `dev`/`ftr`/`publish-ref` + `git push origin HEAD:sub/…`; §5 Radia intake = merge publish tip (conflict recovery via `checkout <sha> --` only); §9a surprises → **finish-up** (not merge-parent); mid-pipeline `docs()` explicitly not deferred to finish-up. |
| Grep gate | Acceptance pattern empty (no Joan / `git-store` / `merge-parent` / `dev-ada` / `astral-<agent>`). Cherry-pick hits are Forbidden / “do not” only. Live symlink matches. |
| Scope / bible | Astral diff: plan + `docs/test-bible/README.md` docs-only note; no `src/` / pytest. Self-Assessment footprint matches. |
| Rules | §1.1 in-scope; docs under `docs/features/team-chuckles/`; §5a–§5g N/A. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | Linear AC still says repo-wide grep; this child correctly scoped to `resolve-child` only (`review-child` = AST-935). |

**Verdict:** Clean — `resolve-child` may proceed (no product/doc fixes required beyond this `docs()` commit).
