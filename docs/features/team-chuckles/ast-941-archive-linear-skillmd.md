# archive-linear SKILL.md (Skill doc consistency pass (pipeline shakedown))

**Linear:** [AST-941](https://linear.app/astralcareermatch/issue/AST-941/archive-linear-skillmd-skill-doc-consistency-pass-pipeline-shakedown)  
**Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)  
**Publish ref:** `sub/AST-909/AST-941-archive-linear`

Align `archive-linear` skill prose with the **current** `archive_linear.py` publish path (commit on `$ASTRAL_MAIN` `dev` → `git push origin HEAD:refs/heads/dev`). Drop Joan `store-archive-commit` / cherry-pick-to-`origin/dev` teaching and operator **merge-parent** naming. Docs/templates only — **do not** change `archive_linear.py` in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/archive-linear/SKILL.md` | Replace Joan/`store-archive-commit`/cherry-pick publish wording with script-matching push; rename merge-parent denial to finish-up; drop Joan failure language | skill (team-chuckles) |

**Out of scope (this ticket):** `archive_linear.py` / `linear_delete_issue.py` / `yearbook.py` behavior changes; sibling skill rows; astral law docs (#17–#18); `install.sh`; watcher code; Astral `src/` / `tests/` / bible.

**Commit homes:** skill edit + commit in **team-chuckles**. Plan doc only on this astral **`origin/sub/AST-909/AST-941-archive-linear`**. `~/.cursor/skills/archive-linear` is a symlink to the team-chuckles skill dir.

**Authoritative publish steps (already in script — skill must mirror these):**

1. Local commit on `$ASTRAL_MAIN` checked out on `dev` (`docs(AST-NNN): archive Linear issue content`).
2. `git fetch origin` + `git merge origin/dev`.
3. If SHA not yet ancestor of `origin/dev`: `git push origin HEAD:refs/heads/dev`.
4. Never cherry-pick; never Joan `git-store-*` / `store-archive-commit`.

---

## Stage 1: Align archive-linear skill prose with archive_linear.py

**Done when:** `~/team-chuckles/skills/archive-linear/SKILL.md` has no live Joan / `git-store-*` / `store-archive-commit` / cherry-pick publish / operator merge-parent teaching. Publish steps match `publish_archive_commit` in `archive_linear.py`. Verification grep (step 7) is clean. Changes committed and pushed in team-chuckles.

1. Open `~/team-chuckles/skills/archive-linear/SKILL.md`. Do **not** edit `archive_linear.py` or any other file.

2. In the YAML **description** frontmatter (currently ~lines 3–7), keep “publish to origin/dev” — that outcome is still correct. Do **not** introduce Joan or cherry-pick there.

3. Replace the **Who runs this** line (currently ~line 12):

   ```
   **Who runs this:** **Chuckles** — **`archive_linear.py`** (Linear GraphQL + **`linear_delete_issue.py`**; MCP has no delete). **Git:** Joan **`git.sh store-archive-commit`** on **`astral`** **`dev`** → **`origin/dev`**.
   ```

   with:

   ```
   **Who runs this:** **Chuckles** — **`archive_linear.py`** (Linear GraphQL + **`linear_delete_issue.py`**; MCP has no delete). **Git:** commit on **`$ASTRAL_MAIN`** (**`astral/`**) on **`dev`**, then **`git push origin HEAD:refs/heads/dev`** (script `publish_archive_commit`) — never Joan / **`git-store-*`** / cherry-pick.
   ```

4. In **§3 Per success** step 3 (currently ~line 65), replace:

   ```
   3. **Publish** — **`cherry-pick docs commit to `origin/dev` from `astral/` on `dev`
   ```

   with:

   ```
   3. **Publish** — from **`$ASTRAL_MAIN`** on **`dev`**: **`git fetch origin`**, **`git merge origin/dev`**, then if the archive SHA is not already an ancestor of **`origin/dev`**, **`git push origin HEAD:refs/heads/dev`**. Never cherry-pick; never Joan **`store-archive-commit`**.
   ```

5. Replace the Joan failure bullet (currently ~line 69):

   ```
   **If Joan blocks:** script stops that issue; do not delete. Report **`@susan`**.
   ```

   with:

   ```
   **If publish/push fails:** script stops that issue; do not delete. Report **`@susan`**.
   ```

6. In **§4 Report to Susan** (currently ~line 76), replace `Joan failure` with `publish/push failure` in the still-blocked identifiers bullet.

7. In **What Chuckles does NOT do** (currently ~lines 93–96), replace:

   ```
   - Does not run **`merge-parent`** or land **`ftr/*`**
   - Does not archive product code — only Linear text into **`docs/features/`**
   - Does not delete before **`origin/dev`** has the archive commit
   - Does not use **`store-plan-commit`** — archive lands on **`origin/dev`** only
   ```

   with:

   ```
   - Does not run **`finish-up`** (parent-close) or land **`ftr/*`** — archive is docs-to-**`origin/dev`** only
   - Does not archive product code — only Linear text into **`docs/features/`**
   - Does not delete before **`origin/dev`** has the archive commit
   - Does not use ticket **`sub/*` / `ftr/*`** publish refs or Joan **`git-store-*`** — archive lands on **`origin/dev`** only via direct push from **`dev`**
   ```

8. From `~/team-chuckles`, verify (must be empty for live residue):

   ```bash
   cd ~/team-chuckles
   rg -n 'git-store|store-archive|JOAN_SESSION|joan-uuid|Joan|cherry-pick|merge-parent|store-plan-commit' skills/archive-linear/SKILL.md
   ```

   Expected: no matches (ban wording that says “Never … cherry-pick / Joan” is allowed only if the narrowed pattern still hits — then tighten until retired *teaching* is gone).

9. Commit and push in **team-chuckles** only:

   ```bash
   cd ~/team-chuckles
   git add skills/archive-linear/SKILL.md
   git commit -m "$(cat <<'EOF'
   code(AST-941): align archive-linear publish prose with push to origin/dev

   EOF
   )"
   git push origin HEAD
   ```

⚠️ **Decision:** Mirror `archive_linear.py` `publish_archive_commit` exactly — do not invent a new publish ceremony or edit the script in this ticket (behavior already correct; skill is the drift).

⚠️ **Decision:** Replace “Does not run merge-parent” with “Does not run finish-up (parent-close)” so operator naming matches epic AC without implying archive should call finish-up.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-909) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — one team-chuckles skill markdown file; identity, §3 publish, failure/report, Does-NOT-do list.

**Conf:** high — script already pushes `HEAD:refs/heads/dev`; skill still teaches Joan cherry-pick; replacements are copy-from-script.

**Risk:** low — docs/templates only; wrong prose mis-teaches Chuckles archive publish, not product or the Python publisher (unchanged).

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope only: listed skill file only; no script edits.
- §1.3 DRY: skill mirrors existing `publish_archive_commit`; no second publish path.
- §2.1 / §2.4 / §2.6 / §3.3 / §3.5 / §3.6: N/A — docs/skill only.

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Built:** team-chuckles `origin/main` @ `6849251c1aec5d22731f3704286f89856660b676` (`skills/archive-linear/SKILL.md`)
**Publish ref:** `origin/sub/AST-909/AST-941-archive-linear` (this plan + stub; tip set after push)

Stage 1: skill prose matches `publish_archive_commit` push to origin/dev; Joan/cherry-pick/merge-parent scrubbed.

