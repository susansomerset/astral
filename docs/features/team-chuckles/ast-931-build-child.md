# build-child SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-931](https://linear.app/astralcareermatch/issue/AST-931/build-child-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-931-build-child`
- **Summary:** Rewrite `team-chuckles/skills/build-child/SKILL.md` so implementers work in the epic worktree `astral-<parent-id>/` on the active `sub/<parent>/<child>` branch and publish with `git push origin HEAD:sub/…` — no Joan / `git-store-*` / self-cherry-pick / `dev-ada`/`dev-hedy` checkout language.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/build-child/SKILL.md` | Full procedural rewrite of worktree + publish path; remove retired vocabulary | skill (team-chuckles) |

**Out of scope (sibling tickets own these):** other skills under `~/team-chuckles/skills/`, `orientation`, `do-all-the-things` templates, `install.sh`, `docs/ASTRAL_GIT_WORKFLOW.md`, `docs/ASTRAL_TEAM_WORKFLOW.md`. Do not edit them under AST-931.

**Publish note:** Skill source lives in **team-chuckles** (symlinked into `~/.cursor/skills`). Commit skill edits in the **team-chuckles** repo. This plan doc lands only on **`origin/sub/AST-909/AST-931-build-child`**. No Astral product `src/` changes.

## Authority for the rewrite

Match these sources literally when choosing replacement wording (do not invent a third publish ceremony):

1. **`orientation` § Worktree paths** — epic path is `<reponame>-<IssueID>/` (e.g. `astral-AST-593/`); **Not used:** `astral-ada`, `dev-<agent>`.
2. **`orientation` § Merge on checkout** — `git fetch origin` → `git checkout sub/<parent>/<child>` → `git merge origin/ftr/<parent-segment>`.
3. **`orientation` § What never happens** — bans Cherry-pick onto published branches; Joan / `git-store-*` / `JOAN_SESSION`.
4. **`docs/ASTRAL_GIT_WORKFLOW.md`** — engineer commits on the checked-out `sub/*` in the epic worktree; `git push origin HEAD:sub/<parent>/<child>` is the publish path (see Betty `merge-tests` and the retired-Joan note at end of that doc). Commit type for this skill’s implementation commits remains **`code(<ticket-id>)`**.
5. Ticket Description **To-be:** epic worktree = `astral-<parent-id>`; publish per orientation (no Joan / `git-store-*` / self-cherry-pick).

## Stage 1: Replace §5 worktree + publish ceremony

**Done when:** `build-child` §5 (and its publish bash block / Forbidden list) describes only `astral-<parent-id>/` + active `sub/*` checkout + `git push origin HEAD:sub/…`, with zero Joan / `git-store-*` / `dev-ada`/`dev-hedy` checkout instructions.

1. Open `~/team-chuckles/skills/build-child/SKILL.md`. Keep Input, Project scope, §0 Resume spawn, §1–§4, §6–§8, §10–§11 structure and Linear status gates unless a later stage step edits them. Focus this stage on **§5** and the publish paragraphs currently under §5 / §9 that still name Joan.

2. In §5 header/body, replace every instruction that says the engineer works in **`astral-<agent>`** or checks out a branch named **`epic worktree`** / **`dev-ada`** / **`dev-hedy`** / **`dev-katherine`** with:

   - Workspace = epic worktree **`$CHUCKLES_ROOT/astral-<parent-id>/`** (example: `astral-AST-909/`).
   - Checked-out branch = the ticket’s **`sub/<parent-id>/<child-segment>`** (from parent Description **## Git** table / spawn prompt **`<publish-ref>`** — not Linear `gitBranchName`).
   - On every checkout / before implement: run orientation merge-on-checkout:

     ```bash
     git fetch origin
     git checkout sub/<parent-id>/<child-segment>
     git merge origin/dev
     git merge origin/ftr/<parent-segment>   # when parent is In Progress
     ```

   - Then **`orientation` § Merge-clean gate**: `BEHIND=0` vs `origin/dev` and `origin/dev` is an ancestor of `HEAD` before coding.

3. Rewrite the **Publish** procedure in §5 to this only (no Joan wrapper):

   ```bash
   git commit -m "code(<ticket-id>): <concise summary>"
   git push origin HEAD:sub/<parent-id>/<child-segment>
   ```

   After push, confirm tip: `git ls-remote origin refs/heads/sub/<parent-id>/<child-segment>` matches `git rev-parse HEAD`. On push rejection / non-fast-forward: stop, post `[check-linear] blocked:` on the ticket with the git error, route per **`orientation` § Merge conflict routing`** — **do not** cherry-pick; **never `@susan`** for merge hunks.

4. Delete or rewrite these retired phrases wherever they appear in §5 (including Publish preflight / Forbidden):

   | Remove / ban as live procedure | Replace with |
   |-------------------------------|--------------|
   | `Joan` as git operator / publisher | engineer `git push origin HEAD:sub/…` |
   | `git.sh store-code-commit` / `store-*-commit` / `git.sh publish` | `git push origin HEAD:sub/<parent>/<child>` |
   | `JOAN_SESSION` / `--session $epic worktree` as Joan handoff | omit (session UUID is datt `--resume` only; not a git-store arg) |
   | `RESULT: … status=ok` / `joan blocked:` stdout checks | push exit code + `ls-remote` tip match |
   | “`sub/*` cherry-picks stack on `ftr`” | merge `origin/ftr/<parent-segment>` into the checked-out sub before coding; push the sub tip |
   | `git checkout epic worktree` (`dev-ada`, `dev-hedy`, …) | `git checkout sub/<parent>/<child>` in `astral-<parent-id>/` |
   | Forbidden: “do not checkout local `sub/*`” while camping on a nameless epic line | Allowed/required: checkout the ticket `sub/*` in the epic worktree; Forbidden: create new `ftr/`/`sub/` refs, cherry-pick onto publish refs, push `origin/dev`, force-push |

5. Keep the existing intent that **`plan-child` must already have pushed a docs-only `plan()` commit** to `origin/<publish-ref>` before build starts; attach that tip by being on the sub and merging as needed — **not** by Joan cherry-pick.

6. Keep UAT Bug / User Testing forbidden note (Bug children via `fix-uat`) — only fix vocabulary if it still says Joan or `dev-<agent>`.

⚠️ **Decision:** Publish is **direct push of the checked-out sub tip** (`git push origin HEAD:sub/…`), matching the half-migrated bash already present in §5 and the AST-909 spawn prompts. Do not reintroduce a second publish tool or a local `ftr/*` camping workflow.

## Stage 2: Sweep remainder of the skill + acceptance grep

**Done when:** A `rg` over `~/team-chuckles/skills/build-child/SKILL.md` for retired live vocabulary returns only deliberate historical/deprecation notes (or zero hits), and a reader of this single skill finds no procedure that contradicts orientation’s “what never happens” list.

1. Sweep the **entire** `SKILL.md` (not only §5) for:

   - `Joan`, `git-store`, `JOAN_SESSION`, `store-code-commit`, `store-plan-commit`, `store-qa-commit`, `git.sh`
   - `self-cherry-pick`, `cherry-pick` as an engineer publish step
   - `dev-ada`, `dev-hedy`, `dev-katherine`, `dev-radia` as worktree/branch checkout names
   - `astral-<agent>`, `astral-ada`, `astral-hedy` as the epic worktree path
   - `<joan-uuid>` as a live placeholder

2. For each hit: either delete it, or rewrite to the Stage 1 target wording. If a sentence is half-updated (e.g. still says “via Joan” above a correct `git push` block), make the prose match the bash — one ceremony only.

3. Fix §9 if it still says publish via Joan / `git.sh store-code-commit … --session $epic worktree`. It must say: commit `code(<ticket-id>)` on the active sub in `astral-<parent-id>/`, then `git push origin HEAD:sub/<parent>/<child>`.

4. Fix §1 / §6 / queue-mode prose that still says work “in `astral-<agent>` on `epic worktree`” — use epic worktree `astral-<parent-id>/` with the ticket `sub/*` checked out.

5. Do **not** change: Linear status gates (Plan Approved → Code Complete), test-tree ban, compile/lint steps, Review stub §10, “no Conf/Risk/Scope labels”, happy-path comment omission rules — unless they embed retired git vocabulary.

6. Acceptance check (run from any cwd; report output in the Code Complete comment only if non-empty unexpected hits):

   ```bash
   rg -n 'Joan|git-store|JOAN_SESSION|store-code-commit|store-plan-commit|store-qa-commit|self-cherry-pick|dev-ada|dev-hedy|dev-katherine|<joan-uuid>|astral-<agent>|git\.sh store' \
     ~/team-chuckles/skills/build-child/SKILL.md
   ```

   Expected: empty, or only lines that are explicit deprecation (“retired”, “do not use”, “never”) pointing at orientation’s never-list — no live procedure that tells the agent to run Joan / cherry-pick / check out `dev-ada`.

7. Commit in **team-chuckles** with subject `code(AST-931): align build-child publish to epic sub push` (or equivalent `code(AST-931): …`). Do not commit skill changes into the astral repo. Do not run `install.sh` unless the ticket/spawn explicitly requires it (sibling AST-945 owns install).

## Execution contract

- Stages in order; no product `src/` edits; no sibling skill files.
- If `~/team-chuckles/skills/build-child/SKILL.md` is missing or not the symlink source Susan expects, stop and comment on **AST-909** with the 🛑 blocked format.
- After Stage 2 commit on team-chuckles, push that repo’s branch per team-chuckles norms for this epic (same machine path `~/team-chuckles`); astral publish ref already holds this plan via `plan(AST-931)`.

## Self-Assessment

**Scope:** `Single-Component` — one skill file in team-chuckles; plan doc only on astral `sub/*`.

**Conf:** `high` — as-is residue is localized to §5/§9 Joan + `dev-ada`/`astral-<agent>` wording; to-be path is already spelled out in orientation merge-on-checkout + ASTRAL_GIT_WORKFLOW push examples + the ticket Description.

**Risk:** `low` — docs/templates only; wrong wording could mis-teach the next build agent, but cannot change Astral runtime behavior.

## Review

- **Branch:** `origin/sub/AST-909/AST-931-build-child`
- **Plan tip:** `4e6d68f` (`plan(AST-931)`)
- **team-chuckles:** `origin/main` @ `325a987` — `code(AST-931): align build-child publish to epic sub push`
- **Built:** `~/team-chuckles/skills/build-child/SKILL.md` — epic `astral-<parent-id>/` + `sub/*` + `git push origin HEAD:sub/…`; Joan / `git-store-*` / `dev-ada` checkout language removed (ban-list mentions of `dev-ada`/`dev-hedy`/`dev-katherine` remain as explicit “do not camp” wording).

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-909/AST-931-build-child`; skill deliverable `team-chuckles@325a987` (`skills/build-child/SKILL.md`).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–2: §5 worktree/publish rewritten to `$CHUCKLES_ROOT/astral-<parent-id>/` + checkout `sub/*` + merge `origin/dev` / `origin/ftr` + `git push origin HEAD:sub/…`; §9 matches; Joan / `git-store-*` / `RESULT: status=ok` / camping on nameless epic line removed. |
| Grep gate | Acceptance `rg` hits only the Forbidden “do not camp on … `dev-ada`/`dev-hedy`/`dev-katherine`” ban (plan-allowed). Live `~/.cursor/skills/build-child` symlink matches. |
| Scope / bible | Astral diff: plan + `docs/test-bible/README.md` docs-only note; no `src/` / pytest. Self-Assessment footprint matches. |
| Rules | §1.1 in-scope; docs under `docs/features/team-chuckles/`; §5a–§5g N/A. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | Linear AC still says repo-wide grep; this child correctly scoped to `build-child` only (siblings = other AST-909 rows). |

**Verdict:** Clean — `resolve-child` may proceed (no product/doc fixes required beyond this `docs()` commit).

## Resolution

**2026-07-22** — Radia verdict **Clean** (no fix-now). Advisory only (Linear AC repo-wide grep wording vs child-scoped `build-child`); no product/doc change. `docs(AST-931): Radia review — clean` already on tip via §4 merge. `resolve(AST-931): — clean`.
