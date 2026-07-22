# test-child SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-937](https://linear.app/astralcareermatch/issue/AST-937/test-child-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-937-test-child`
- **Summary:** Rewrite `team-chuckles/skills/test-child/SKILL.md` so Betty’s test delivery is described as orientation/`merge-tests` → `origin/<publish-ref>` (no Joan `store-qa-commit`), and the engineer runs in `astral-<parent-id>/` on the active `sub/*`, publishing `test()` with `git push origin HEAD:sub/…`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/test-child/SKILL.md` | Replace Joan/`astral-<agent>`/`epic worktree` checkout residue; document Betty + engineer publish per orientation | skill (team-chuckles) |

**Out of scope:** `qa-child` (AST-936), other skills, orientation, datt templates, `install.sh`, astral law docs. Docs/templates only — no product `src/` or test-tree edits under this ticket.

**Publish note:** Skill edits commit in **team-chuckles**. This plan doc lands only on **`origin/sub/AST-909/AST-937-test-child`**.

## Authority for the rewrite

1. **Ticket To-be:** Betty publish path per orientation (no Joan store).
2. **`docs/ASTRAL_GIT_WORKFLOW.md`:** Betty commits on `origin/tests`, then **`merge-tests(AST-NNN)`** merges that SHA onto the sub and **`git push origin HEAD:sub/<parent>/<child>`**. Engineer never uses Joan.
3. **`orientation` § What never happens:** Joan / `git-store-*` / `JOAN_SESSION`; cherry-pick onto published branches. Epic path = `<reponame>-<IssueID>/`; **Not used:** `dev-<agent>`, `astral-ada`.
4. **`orientation` § Merge on checkout:** engineer checks out `sub/<parent>/<child>` in the epic worktree, merges `origin/ftr/<parent-segment>`.
5. Existing half-migrated §7 bash already shows `git push origin HEAD:sub/…` — make prose match that ceremony only.

## Stage 1: Betty delivery wording + engineer worktree/publish (§ Who / §5 / §7)

**Done when:** test-child never instructs Joan `store-qa-commit` / `git-store-*`; Betty’s commits are described as landing on `origin/<publish-ref>` via Betty’s orientation publish (`merge-tests` + push to `sub/*`); engineer works in `astral-<parent-id>/` on `sub/*` and publishes with `git push`.

1. Open `~/team-chuckles/skills/test-child/SKILL.md`.

2. In **Who runs this** and §5 opening: replace **`astral-<agent>`** / **`git checkout epic worktree`** with epic worktree **`$CHUCKLES_ROOT/astral-<parent-id>/`** and active branch **`sub/<parent-id>/<child-segment>`** (parent **## Git** / spawn **`<publish-ref>`**, not Linear `gitBranchName`).

3. Rewrite the sentence that says Betty’s `qa-child` commits land via Joan **`store-qa-commit`** to:

   - Betty’s test-lane commits live on **`origin/tests`**; she delivers them onto **`origin/<publish-ref>`** with **`merge-tests(<ticket-id>)`** and **`git push origin HEAD:sub/<parent>/<child>`** (per ASTRAL_GIT_WORKFLOW) — **not** via Joan / `store-qa-commit` / `git-store-*`.
   - Those commits still do **not** appear on the engineer’s working line until the engineer merges **`origin/<publish-ref>`** (keep that warning — stale-merge → false `[qa-handoff]`).

4. Fix §5 attach order to:

   ```bash
   git fetch origin
   git checkout sub/<parent-id>/<child-segment>
   git merge origin/dev
   git merge origin/ftr/<parent-segment>   # when parent In Progress
   git merge origin/<publish-ref>          # Betty merge-tests tip + product tip
   ```

   Then Merge-clean gate before §6. Complete the currently truncated step-4 sentence about Betty/bible so it is one coherent paragraph ending in the merge of `origin/<publish-ref>`.

5. In §5 verify bullets: replace `git log …..epic worktree` with the checked-out sub / `HEAD` (same intent: empty product commits for this ticket while tests fail → behind publish tip → re-merge, do not patch `tests/`).

6. In §7: keep **`test(<ticket-id>): …`** commit type; rewrite “Publish via test-child (build-child §6)” / any Joan residue so the only publish ceremony is:

   ```bash
   git commit -m "test(<ticket-id>): <summary>"
   git push origin HEAD:sub/<parent-id>/<child-segment>
   ```

   Confirm tip with `ls-remote` vs `rev-parse`. On push failure: `[check-linear] blocked:` + merge-conflict routing — no cherry-pick, never `@susan` for hunks.

7. Delete live mentions of: `Joan`, `store-qa-commit`, `git-store-*`, `JOAN_SESSION`, `git.sh`, `dev-ada`/`dev-hedy`/`dev-katherine` as checkout names, `astral-<agent>` as the epic path.

⚠️ **Decision:** Betty’s path is described from the engineer’s POV as “already on `origin/<publish-ref>` after her `merge-tests` push.” Do not paste Betty’s full qa-child procedure into this skill — that is AST-936’s file. Do not reintroduce Joan.

## Stage 2: Consistency sweep + AC grep

**Done when:** `rg` over this skill for retired live vocabulary is clean (or only deliberate deprecation notes), and §§0–4 / §6 / §8 still work as engineer test-run procedure without contradicting orientation’s never-list.

1. Sweep the whole file for leftover Joan / store / `astral-<agent>` / `checkout epic worktree` / cherry-pick publish language.
2. Leave intact: test-tree ban, `[qa-handoff]` flow, status gates (Tests Ready → Tests Passed), FIX-UAT MODE stop, happy-path comment omission, Conf/Risk/Scope label ban, manifest-only run rules.
3. Acceptance grep:

   ```bash
   rg -n 'Joan|git-store|JOAN_SESSION|store-qa-commit|store-code-commit|self-cherry-pick|dev-ada|dev-hedy|dev-katherine|<joan-uuid>|astral-<agent>|git\.sh store' \
     ~/team-chuckles/skills/test-child/SKILL.md
   ```

   Expected: empty or explicit deprecation only.

4. Commit in **team-chuckles**: `code(AST-937): align test-child Betty publish without Joan`. Do not commit skill changes into astral. Do not run `install.sh` (AST-945).

## Execution contract

- Stages in order; only `test-child/SKILL.md`.
- If Betty delivery cannot be described without inventing a third publish tool, stop and 🛑 on **AST-909**.
- After team-chuckles `code(AST-937)`, astral already holds this plan via `plan(AST-937)`.

## Self-Assessment

**Scope:** `Single-Component` — one skill file in team-chuckles; plan doc only on astral `sub/*`.

**Conf:** `high` — ticket names the exact as-is (`store-qa-commit`) and to-be (orientation Betty publish); engineer push bash already exists in §7; worktree rewrite matches AST-931/AST-934 plans.

**Risk:** `low` — docs/templates only; wrong Betty wording could confuse engineers about where tests land, but cannot change runtime; Stage 1 pins `merge-tests` + merge `origin/<publish-ref>`.

## Review

- **Branch:** `origin/sub/AST-909/AST-937-test-child`
- **Plan tip:** `584b58d` (`plan(AST-937)`)
- **team-chuckles:** `origin/main` @ `ac131a9` — `code(AST-937): align test-child Betty publish without Joan`
- **Built:** `~/team-chuckles/skills/test-child/SKILL.md` — Betty delivery via `merge-tests` → `origin/<publish-ref>`; engineer on `astral-<parent-id>/` + `sub/*` + `git push`; Joan `store-qa-commit` removed.
