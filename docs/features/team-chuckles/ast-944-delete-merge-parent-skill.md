# Delete merge-parent skill (Skill doc consistency pass (pipeline shakedown))

**Linear:** [AST-944](https://linear.app/astralcareermatch/issue/AST-944/delete-merge-parent-skill-skill-doc-consistency-pass-pipeline)  
**Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)  
**Publish ref:** `sub/AST-909/AST-944-delete-merge-parent-skill`

Delete the deprecated **`team-chuckles/skills/merge-parent/`** skill so it is no longer discoverable. Keep astral **`scripts/git/merge-parent.sh`** as the finish-up-land internal helper. Coordinate with **AST-945** (`install.sh`) — do **not** edit `install.sh` here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/merge-parent/SKILL.md` | **Delete** (remove entire `skills/merge-parent/` directory) | skill (team-chuckles) |
| `~/.cursor/skills/merge-parent` | Remove leftover install symlink after the skill dir is gone (host cleanup; not a git path) | host symlink |

**Out of scope (this ticket):** `install.sh` (AST-945); `skills/finish-up/SKILL.md` (AST-943, blocked by this ticket); other sibling skill prose; astral `scripts/git/merge-parent.sh` (must remain); astral law docs (#17–#18); watcher/product/`src`/`tests`/bible.

**Commit homes:** skill deletion commit in **team-chuckles**. Plan doc only on this astral **`origin/sub/AST-909/AST-944-delete-merge-parent-skill`**.

**Why install.sh is not edited here:** `install.sh` already symlinks every `skills/*` entry in a loop — once `skills/merge-parent/` is gone, a fresh `install.sh` run will not install it. Explicit install scrub / any remaining install wording is **AST-945**.

---

## Stage 1: Delete merge-parent skill directory

**Done when:** `~/team-chuckles/skills/merge-parent/` does not exist; `~/.cursor/skills/merge-parent` is absent (no symlink/dir); `git -C ~/team-chuckles status` shows the deletion staged/committed; `test ! -e ~/astral/scripts/git/merge-parent.sh` is **false** (script still present — do not delete it). Changes pushed to team-chuckles origin.

1. Confirm the deprecated skill exists and is only the stub:

   ```bash
   ls -la ~/team-chuckles/skills/merge-parent/
   # Expect: SKILL.md only (deprecated pointer to finish-up)
   test -f ~/astral/scripts/git/merge-parent.sh   # must remain — stop if missing
   ```

2. Delete the skill directory from the team-chuckles repo (git rm so history records the removal):

   ```bash
   cd ~/team-chuckles
   git rm -r skills/merge-parent
   ```

   Do **not** delete `~/astral/scripts/git/merge-parent.sh`. Do **not** edit `install.sh`, `skills/finish-up/SKILL.md`, or any other skill.

3. Remove the live Cursor install symlink so the skill is not discoverable on this host before AST-945 / next `install.sh`:

   ```bash
   rm -f ~/.cursor/skills/merge-parent
   # if it was a directory somehow:
   rm -rf ~/.cursor/skills/merge-parent
   test ! -e ~/.cursor/skills/merge-parent
   ```

4. Verify:

   ```bash
   test ! -e ~/team-chuckles/skills/merge-parent
   test -f ~/astral/scripts/git/merge-parent.sh
   # install.sh still has no hardcoded merge-parent name — loop-only install:
   rg -n 'merge-parent' ~/team-chuckles/install.sh || true
   # expected: no matches
   ```

5. Commit and push in **team-chuckles** only:

   ```bash
   cd ~/team-chuckles
   git commit -m "$(cat <<'EOF'
   code(AST-944): delete deprecated merge-parent skill

   EOF
   )"
   git push origin HEAD
   ```

⚠️ **Decision:** Delete the whole `skills/merge-parent/` directory rather than emptying `SKILL.md` — Susan answered delete skill; a stub file would still be installable/discoverable via the install loop.

⚠️ **Decision:** Leave `install.sh` to AST-945 even though the ticket text mentions it — Notes say “Coordinate with #16”; Boundaries forbid owning sibling file rows; the loop already stops installing once the dir is gone.

⚠️ **Decision:** Keep `merge-parent.sh` untouched — parent Boundaries: operator-facing skill/docs naming only; land script stays finish-up-land helper.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-909) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — delete one team-chuckles skill directory + remove host symlink; no astral product files.

**Conf:** high — skill is a 20-line deprecated stub; install is a directory loop; `merge-parent.sh` retention is explicit in parent Boundaries; AST-945 owns install.sh.

**Risk:** low — docs/skill discovery only. Residual risk is other skills still *naming* the merge-parent skill (sibling tickets) or a stale host symlink if step 3 is skipped — mitigated by explicit symlink removal here.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope only: delete listed skill path; do not touch land script or sibling skills.
- §1.3 DRY: finish-up remains the sole operator parent-close skill after deletion.
- §2.1 / §2.4 / §2.6 / §3.3 / §3.5 / §3.6: N/A — no product code.

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Built:** team-chuckles `origin/main` @ `02ec02c5e3f0fbdbe7df296dbdb3fe613330936a` (deleted `skills/merge-parent/`)
**Publish ref:** `origin/sub/AST-909/AST-944-delete-merge-parent-skill` (this plan + stub; tip set after push)

Stage 1: removed deprecated merge-parent skill + host symlink; `scripts/git/merge-parent.sh` retained; `install.sh` left to AST-945.

