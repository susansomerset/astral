# review-child SKILL.md (Skill doc consistency pass (pipeline shakedown))

**Linear:** [AST-935](https://linear.app/astralcareermatch/issue/AST-935/review-child-skillmd-skill-doc-consistency-pass-pipeline-shakedown)  
**Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)  
**Publish ref:** `sub/AST-909/AST-935-review-child`

Scrub retired Joan / `dev-radia` / implementer-cherry-pick / merge-parent-as-operator-close language from `review-child` while **keeping** mid-pipeline Radia `docs()` on the active publish/sub ref. Docs/templates only — no product behavior change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/review-child/SKILL.md` | Drop Joan/`dev-radia`/`astral-radia`/cherry-pick-handoff residue; rename parent-close sync to finish-up; keep Radia mid-pipeline `docs()` publish via `git push origin HEAD:<publish-ref>` | skill (team-chuckles) |

**Out of scope (this ticket):** sibling skill rows (including resolve-child AST-934 engineer intake); astral law docs (#17–#18); `install.sh`; watcher behavior; Astral `src/` / `tests/` / bible.

**Commit homes:** skill edit + commit land in **team-chuckles**. Plan doc only on this astral **`origin/sub/AST-909/AST-935-review-child`**. `~/.cursor/skills/review-child` is a symlink to the team-chuckles skill dir.

---

## Stage 1: Align review-child publish + worktree wording with orientation

**Done when:** `~/team-chuckles/skills/review-child/SKILL.md` has no live teaching of Joan / `git-store-*` / `JOAN_SESSION` / `dev-radia` / `astral-radia` as the Radia checkout / implementer cherry-pick of Radia SHAs / merge-parent as the Chuckles parent-close action. Mid-pipeline Radia `docs()` on **`origin/<publish-ref>`** remains explicit. Verification grep (step 5) is clean for live residue. Changes committed and pushed in team-chuckles.

1. Open `~/team-chuckles/skills/review-child/SKILL.md`. Do **not** edit any other skill file.

2. In the opening **Who runs this** line (currently ~line 11), replace:

   ```
   **Who runs this:** **Radia** — **`linear-radia`**, worktree **`astral-radia`** (or repo root per Susan). **Not** an engineer skill.
   ```

   with:

   ```
   **Who runs this:** **Radia** — **`linear-radia`**, epic worktree **`<reponame>-<parent-id>/`** for child tickets under a parent (or **`$ASTRAL_MAIN`** / **`astral/`** for standalone). **Not** an engineer skill. Never **`astral-radia`**, **`dev-radia`**, or other agent-named epic worktree checkouts.
   ```

3. In **§4** item 1 (currently ~line 53), replace the Implementers / Radia sync sentence that currently reads:

   ```
   **Implementers:** after **merge-parent** lands on **`origin/dev`**, merge **`origin/dev`** into **`epic worktree`** per **orientation § Merge integration line**, then **§ Merge-clean gate**, before **resolve-child** / the next ticket — do not rebase **`origin/dev`** onto **`epic worktree`**. **Radia:** when syncing **`dev-radia`** for review follow-ups, run the same merge + **§ Merge-clean gate** before doc-only commits.
   ```

   with:

   ```
   **Implementers:** after **finish-up** lands the parent on **`origin/dev`** (post–**PR Ready** parent close only — not Radia's mid-pipeline findings channel), merge **`origin/dev`** into the epic worktree per **orientation § Merge integration line**, then **§ Merge-clean gate**, before **resolve-child** / the next ticket — do not rebase **`origin/dev`** onto the epic worktree. **Radia:** when syncing the epic worktree (`<reponame>-<parent-id>/`) for review follow-ups, run the same merge + **§ Merge-clean gate** before mid-pipeline doc-only **`docs()`** commits on **`<publish-ref>`**.
   ```

4. In **§6 Combined doc (optional) + engineer handoff**, replace the three broken/residue bullets that currently read:

   ```
   - **Doc-only, one commit:** **What’s solid**, **Issues**, **Recommended actions** (table); message **`docs(AST-XXX): Radia review — <hint>`**; **publish via Joan**: **`commit on active sub-branch: `docs(<ticket-id>)` then `git push origin HEAD:sub/<parent>/<child>`

   - **Worktrees:** Radia commits on **`dev-radia`**, then **

   - **No `git merge radia-review`** handoffs — implementer **`git cherry-pick <sha>`** onto **`epic worktree`** from
   ```

   with these three complete bullets (preserve the surrounding “When plan exists and you commit” intro and the “If you do not commit…” sentence):

   ```
   - **Doc-only, one commit (mid-pipeline):** **What’s solid**, **Issues**, **Recommended actions** (table); message **`docs(AST-XXX): Radia review — <hint>`**; commit on the epic worktree sub checkout, then publish with **`git push origin HEAD:sub/<parent>/<child>`** (or **`origin/<publish-ref>`** from the parent **Git** table). Never Joan / **`git-store-*`** / self-cherry-pick. This mid-pipeline **`docs()`** path is **not** deferred to **finish-up**.

   - **Worktrees:** Radia works in **`<reponame>-<parent-id>/`** (child under a parent) or **`$ASTRAL_MAIN`** (standalone). Commit **`docs()`** on the active publish/sub checkout, then push to **`origin/<publish-ref>`**. Never **`dev-radia`**, **`astral-radia`**, or other agent-named epic worktree checkouts.

   - **No `git merge radia-review` handoffs** and **no implementer cherry-pick of Radia SHAs** from this skill — after Radia’s push, **`docs()`** already live on **`origin/<publish-ref>`**; **resolve-child** attaches that tip onto the epic worktree (sibling skill owns engineer intake).
   ```

5. From `~/team-chuckles`, verify (narrow pattern must be empty):

   ```bash
   cd ~/team-chuckles
   rg -n 'git-store|JOAN_SESSION|joan-uuid|publish via Joan|dev-radia|astral-radia|merge-parent|cherry-pick <sha>|Engineers cherry-pick|self-cherry-pick onto' skills/review-child/SKILL.md
   ```

   Expected: no matches. Ban wording that says “Never … cherry-pick / Joan / `dev-radia`” is allowed; if the pattern above still hits ban lines, tighten further until only empty output remains for *retired teaching* (live procedure must not instruct Joan, `dev-radia`, `astral-radia`, merge-parent-as-close, or implementer cherry-pick).

6. Commit and push in **team-chuckles** only:

   ```bash
   cd ~/team-chuckles
   git add skills/review-child/SKILL.md
   git commit -m "$(cat <<'EOF'
   code(AST-935): align review-child publish path; keep mid-pipeline docs()

   EOF
   )"
   git push origin HEAD
   ```

⚠️ **Decision:** Keep Radia mid-pipeline `docs()` on the publish ref explicit in §6 — parent AC and ticket Notes require it; finish-up is named only for post–PR Ready parent close in §4, never as the findings channel.

⚠️ **Decision:** Replace truncated §6 Worktrees / cherry-pick bullets entirely rather than patch mid-sentence — the current file ends those bullets mid-phrase and cannot be executed literally.

⚠️ **Decision:** Do not edit `resolve-child` here even though it still teaches cherry-pick intake — that is AST-934; this skill only stops *review-child* from instructing implementer cherry-pick.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-909) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — one team-chuckles skill markdown file; opening identity line, §4 sync sentence, §6 publish/worktree/handoff bullets.

**Conf:** high — residue is located (`publish via Joan`, truncated `dev-radia` / cherry-pick bullets, `merge-parent` in §4); replacement matches orientation publish push and finish-up parent-close naming already used elsewhere in this epic’s plans.

**Risk:** low — docs/templates only; wrong wording mis-teaches Radia/engineer handoff, not product or git scripts. Mitigated by keeping mid-pipeline `docs()` explicit so finish-up is not mistaken for Radia’s findings channel.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope only: listed skill file only.
- §1.3 DRY: reuse orientation / plan-child publish push ceremony; do not invent a store wrapper.
- §2.1 / §2.4 / §2.6 / §3.3 / §3.5 / §3.6: N/A — docs/skill only.

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Built:** team-chuckles `origin/main` @ `c01bd93dee7601a568033e49281deff856e84ae6` (`skills/review-child/SKILL.md`)
**Publish ref:** `origin/sub/AST-909/AST-935-review-child` @ `b344cff27315fe9f719255d95175c6c279e463ac` (this plan + stub)

Stage 1: Who-runs / §4 sync / §6 publish bullets — drop Joan/`dev-radia`/`astral-radia`/cherry-pick handoff; parent-close sync names finish-up; mid-pipeline Radia `docs()` kept via push to publish-ref.

## Tests (engineer)

**Manifest:** Betty docs-only / no pytest. Grep gate on `skills/review-child/SKILL.md` — only deliberate bans (`Never Joan` / `dev-radia` / `git-store-*` / self-cherry-pick); mid-pipeline `docs()` via `git push origin HEAD:sub/…` confirmed; finish-up only post–PR Ready. Plan Stage 1 + `team-chuckles@c01bd93` spot-check OK.

