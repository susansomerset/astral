# Astral skills audit (v3 rollout)

Audit of every Astral-related skill under `~/.cursor/skills/`. **Law:** [ASTRAL_GIT_WORKFLOW.md](ASTRAL_GIT_WORKFLOW.md). **Personas:** `~/.cursor/agents/*-AGENTS.md` (five child assignees) + `astral/AGENTS.md` (Chuckles only).

| Skill | Action | New name | Notes |
|-------|--------|----------|-------|
| `define-linear` | RENAME + EDIT | `define-parent` | Chuckles epic definition |
| `dispatch-linear` | RENAME + EDIT | `dispatch-parent` | Creates `<reponame>-<IssueID>/` worktree; no Joan |
| `rollup-child` | RENAME + EDIT | `merge-child` | sub → ftr; absorbs `git-rollup` logic |
| `finish-up` | RENAME + EDIT | `merge-parent` | ftr → dev; absorbs `git-push-dev` land |
| `plan-astral` | RENAME + EDIT | `plan-child` | Epic worktree; `plan()` commit |
| `build-astral` | RENAME + EDIT | `build-child` | `code()` commit; merge ftr on checkout |
| `qa-astral` | RENAME + EDIT | `qa-child` | `astral-tests` + `push-tests()` |
| `test-astral` | RENAME + EDIT | `test-child` | `test()` commit in epic worktree |
| `review-astral` | RENAME + EDIT | `review-child` | `docs()` commit |
| `resolve-astral` | RENAME + EDIT | `resolve-child` | `resolve()` commit |
| `orientation-astral` | RENAME + EDIT | `orientation` | Embeds git cheat sheet; no `dev-<agent>` |
| `validate-plan` | KEEP + EDIT | `validate-plan` | Update skill name refs |
| `prep-uat` | KEEP + EDIT | `prep-uat` | Must `git push origin dev` |
| `fix-uat` | KEEP + EDIT | `fix-uat` | Bug children from UAT comments; no fix-uat-dev/qa |
| `check-linear` | KEEP + EDIT | `check-linear` | Route to epic or tests worktree |
| `rollcall` | KEEP + EDIT | `rollcall` | New skill names; Chuckles AGENTS guard |
| `do-all-the-things` | KEEP + EDIT | `do-all-the-things` | Epic worktree spawns; no JOAN_SESSION |
| `audit-linear` | KEEP + EDIT | `audit-linear` | Light ref updates |
| `archive-linear` | KEEP + EDIT | `archive-linear` | Light ref updates |
| `yearbook-linear` | KEEP + EDIT | `yearbook-linear` | Light ref updates |
| `git-astral` | REMOVE | — | Logic → merge-child, merge-parent, prep-uat, orientation |
| `git-session-open` | REMOVE | — | Joan sunset |
| `git-store-plan-commit` | REMOVE | — | Direct commits on sub |
| `git-store-code-commit` | REMOVE | — | Direct commits on sub |
| `git-store-qa-commit` | REMOVE | — | Betty `push-tests()` |
| `git-store-test-commit` | REMOVE | — | Engineer `test()` |
| `git-store-review-commit` | REMOVE | — | Radia `docs()` |
| `git-store-resolve-commit` | REMOVE | — | Engineer `resolve()` |
| `git-store-bugfix-commit` | REMOVE | — | Bug children use child pipeline |
| `git-store-archive-commit` | REMOVE | — | Docs-only archive commit on dev |
| `git-rollup` | REMOVE | — | → `merge-child` |
| `git-land-ftr` | REMOVE | — | → `prep-uat` |
| `git-push-dev` | REMOVE | — | → `merge-parent` |
| `git-refresh-ftr` | REMOVE | — | merge origin/dev into ftr in epic worktree |
| `epic-sessions` | REMOVE | — | No JOAN_SESSION |
| `fix-uat-dev` | REMOVE | — | Bug children use `*-child` pipeline |
| `fix-uat-qa` | REMOVE | — | Same |
| `git-workflow` | NEVER CREATE | — | Git law lives in `orientation` + repo doc |

## New skills (created in rollout)

| Skill | Owner | Purpose |
|-------|-------|---------|
| `seed-agents-md` | Chuckles / hooks | Copy `~/.cursor/agents/<persona>-AGENTS.md` → epic worktree at status handoff |

## Git helpers (repo scripts, not skills)

| Script | Absorbed from | Used by |
|--------|---------------|---------|
| `scripts/git/merge-child.sh` | `git-rollup` | `merge-child` skill |
| `scripts/git/merge-parent.sh` | `git-push-dev` | `merge-parent` skill |
| `scripts/git/prep-uat-land.sh` | `git-land-ftr` | `prep-uat` skill |
| `scripts/agent-worktrees.sh` | legacy agent dirs | `dispatch-parent`, `orientation` |

## Out of scope

- `~/.cursor/skills-cursor/` (Cursor product skills)
- Pipeline ticket execution (AST-608, etc.)
- AST-598 bible breakdown
