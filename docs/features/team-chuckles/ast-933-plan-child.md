# AST-933 — plan-child SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-933](https://linear.app/astralcareermatch/issue/AST-933/plan-child-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-933-plan-child`
- **Summary:** Scrub `team-chuckles/skills/plan-child/SKILL.md` so the self-cherry-pick ban and publish procedure match current law: epic worktree = `astral-<parent-id>/`, publish by commit + `git push origin HEAD:<publish-ref>`, no Joan/`git-store-*`/`astral-<agent>` checkout names. Docs only; no product change. Sibling skills and astral law docs are out of scope.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/plan-child/SKILL.md` | Vocabulary + publish-procedure scrub per stages below (symlinked at `~/.cursor/skills/plan-child/SKILL.md`) | docs / skill |
| `docs/features/team-chuckles/ast-933-plan-child.md` | This plan (on publish ref) | docs |

**Repos:** other skills (including datt AST-930), `orientation`, `install.sh`, astral `docs/ASTRAL_*.md` (#17–#18), product `src/` / `tests/`.

**Commit home:** skill edits in **`team-chuckles`**. Plan doc only on this astral **`sub/*`** ref.

## Stage 1: Binding replacement map

**Done when:** The map below is the only allowed vocabulary for Stage 2; live procedure text no longer teaches Joan publish or agent-named epic trees.

1. In `~/team-chuckles/skills/plan-child/SKILL.md`, treat as **retired live vocabulary**:
   - `Joan`, `store-plan-commit`, `git-store-*`, `git.sh store-plan-commit`, `JOAN_SESSION`
   - `astral-<agent>` / `astral-ada` / `astral-hedy` / `astral-kath` as the epic worktree path
   - Any publish path that is self-cherry-pick onto `origin/<publish-ref>`
2. Apply this **binding map** wherever those appear as live procedure:

| From (retired / contradictory) | To (current law) |
|--------------------------------|------------------|
| Work / checkout named **`astral-<agent>`** | Epic worktree **`$CHUCKLES_ROOT/astral-<parent-id>/`** (or `<reponame>-<parent-id>/`); stand-alone tickets without parent use the same pattern from orientation when applicable |
| Publish **via Joan `store-plan-commit`** / **`git.sh store-plan-commit … --session $epic worktree`** | On epic worktree: commit the plan file, then **`git push origin HEAD:<publish-ref>`**. Confirm **`origin/<publish-ref> @ <tip>`**. No Joan, no `git-store-*`, no self-cherry-pick |
| “published to **`origin/<publish-ref>`** via Joan (**build-child** §6)” (execution contract) | “published to **`origin/<publish-ref>`** per **build-child** publish steps (commit on epic worktree + push to publish ref; no Joan / self-cherry-pick)” |
| §9 line that both says “`ftr/*` / `sub/*` is never your persistent local checkout” **and** “commit on active sub-branch” without resolving | Single coherent rule: **in the epic worktree**, check out the ticket’s **`sub/<parent>/<child>`** (or stand-alone **`ftr/<segment>`**), merge **`origin/dev`** (+ parent **`origin/ftr/…`** when required), commit there, **`git push origin HEAD:<publish-ref>`**. Do **not** create missing refs; do **not** self-cherry-pick; do **not** push **`origin/dev`**; do **not** treat Linear **`gitBranchName`** as the publish ref |
| §4a **Forbidden** ban on any local branch named **`sub/…`** / checking out **`<publish-ref>`** in **`astral-<agent>`** | Rewrite Forbidden to match orientation “what never happens”: no self-cherry-pick; no creating **`ftr/*`/`sub/*`** that dispatch did not seed; no **`git push -u`** inventing refs; no camping on publish refs **outside** the epic worktree; no agent-named trees (`astral-ada`, etc.). **Allowed:** checking out the seeded **`sub/…`** (or **`ftr/…`**) **inside** **`astral-<parent-id>/`** for plan/build work |
| “Do not self-cherry-pick … in **`astral-<agent>`**” | “Do not self-cherry-pick … in the epic worktree (**`astral-<parent-id>/`**)” — **keep the ban** |

⚠️ **Decision:** Keep the self-cherry-pick ban (ticket as-is/to-be). Align worktree naming to **`astral-<parent-id>`** and publish to **`git push origin HEAD:<publish-ref>`**. Resolve the internal contradiction in §4a/§9 that forbids checking out `sub/*` while also requiring an active sub-branch commit — checkout of the seeded sub inside the epic worktree is the current happy path (same as datt spawn git lines).

⚠️ **Decision:** Do not change plan-doc structure, Linear status gates, self-assessment axes, or queue-mode rules — vocabulary and publish/worktree wording only.

## Stage 2: Edit plan-child SKILL.md

**Done when:** A reader following §4a + §9 alone cannot learn Joan publish, `astral-<agent>` epic trees, or self-cherry-pick publish; they can execute commit + push on `astral-<parent-id>/` with the seeded `sub/*`.

1. Replace every live **`astral-<agent>`** occurrence with epic worktree **`astral-<parent-id>/`** (or “epic worktree” when the path was already established in-section).
2. Rewrite **execution contract** publish sentence (currently “via Joan (**build-child** §6)”) per Stage 1 map.
3. Rewrite **§9** entirely for coherence:
   - Drop Joan / `store-plan-commit` / `git.sh store-plan-commit`.
   - Keep: plan-only commit message `docs(<ticket-id>): plan — …`; confirm tip; remain in epic worktree after push.
   - Spell publish as: `git push origin HEAD:<publish-ref>` (child example `HEAD:sub/<parent>/<child>`).
   - Keep “Do not self-cherry-pick.”
4. Rewrite **§4a Forbidden** per Stage 1 map so it does not ban the seeded `sub/*` checkout inside the epic worktree.
5. Rewrite **Re-running the plan** publish bullet (currently `git.sh store-plan-commit … --session $epic worktree` / `astral-<agent>`) to the same push path + epic worktree naming.
6. Do **not** edit other files. Do **not** soften the self-cherry-pick ban into an allowed publish method.

## Stage 3: Grep gate and install note

**Done when:** Grep of this file for retired live tokens is clean except deliberate historical notes (prefer zero hits).

1. From `~/team-chuckles`, run:

```bash
rg -n -i 'joan|git-store|JOAN_SESSION|store-plan-commit|git\.sh store-plan|astral-<agent>|astral-ada|astral-hedy|astral-kath|self-cherry-pick' skills/plan-child/SKILL.md
```

2. **Required:** `self-cherry-pick` may appear **only** as a **ban** (“never” / “do not” / Forbidden). No sentence may teach cherry-pick as the publish mechanism.
3. **Required:** zero live hits for `Joan`, `store-plan-commit`, `git-store`, `JOAN_SESSION`, `astral-ada` / `astral-hedy` / `astral-kath` / `astral-<agent>` as worktree paths.
4. Commit in **`team-chuckles`**: `code(AST-933): align plan-child publish path to astral-<parent-id>`. No astral product commits under this ticket beyond the plan doc already on the sub ref.
5. Note on Code Complete: host needs `~/team-chuckles/install.sh` (or equivalent) before `~/.cursor/skills/plan-child` reflects the commit.

## Execution contract

- Stages in order; this ticket only.
- If §4a Forbidden vs datt checkout lines still conflict after Stage 1 map, stop and comment on **AST-909** with the Stage N blocked format — do not invent a third publish model.
- No product behavior change.

## Self-Assessment

**Scope:** `minor` — one skill markdown file in team-chuckles plus this plan doc.

**Conf:** `high` — ticket as-is/to-be names the exact residue; current §4a/§9 still contain Joan + `astral-<agent>` + contradictory sub checkout bans.

**Risk:** `low` — docs only; wrong wording mis-teaches plan publish until fixed, not product runtime.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — satisfied.
- Plan path `docs/features/team-chuckles/` — satisfied.
- No config/batch/state/import changes — N/A.
- Aligns plan-child with orientation “what never happens” (no Joan/`git-store-*`/cherry-pick publish/agent-named epic trees).

## Review (build stub)

**Publish ref:** `origin/sub/AST-909/AST-933-plan-child`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `37bee03` | Plan doc on astral sub |
| 1–3 | `team-chuckles@ac108ad` | Align `skills/plan-child/SKILL.md` publish path to `astral-<parent-id>/` + push (no Joan/`store-plan-commit`/`astral-<agent>`) |

**Tip:** astral plan + stub (this commit); skill on `team-chuckles` `main` @ `ac108ad`.

