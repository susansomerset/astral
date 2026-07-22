# ASTRAL_TEAM_WORKFLOW.md (Skill doc consistency pass (pipeline shakedown))

**Linear:** [AST-947](https://linear.app/astralcareermatch/issue/AST-947/astral-team-workflowmd-skill-doc-consistency-pass-pipeline-shakedown)  
**Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)  
**Publish ref:** `sub/AST-909/AST-947-astral-team-workflow`

Rename operator parent-close from **merge-parent** to **finish-up** in `docs/ASTRAL_TEAM_WORKFLOW.md`: PR Ready status row and `launch.sh` merge note. Docs only — no product behavior change. Edit and publish on this astral **`sub/*`** (not team-chuckles).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/ASTRAL_TEAM_WORKFLOW.md` | PR Ready row: Chuckles **`finish-up`**; Local UI `launch.sh` note: pair **`prep-uat` / `finish-up`** | docs (astral law) |

**Out of scope (this ticket):** `docs/ASTRAL_GIT_WORKFLOW.md` (AST-946 / #17); team-chuckles skills; `launch.sh` itself; watcher/product/`src`/`tests`/bible; expanding the Chuckles skill index list beyond the two named residue sites.

**Commit homes:** law-doc edit + `code(AST-947)` commit on this astral **`origin/sub/AST-909/AST-947-astral-team-workflow`**. Plan doc on the same ref. No team-chuckles commit for this ticket.

---

## Stage 1: Rename merge-parent → finish-up in TEAM_WORKFLOW

**Done when:** `docs/ASTRAL_TEAM_WORKFLOW.md` has no live operator **`merge-parent`** naming; PR Ready row names Chuckles **`finish-up`**; `launch.sh` note pairs **`prep-uat` / `finish-up`**. Verification grep for `merge-parent` in that file is empty. Changes committed on the epic worktree sub checkout and pushed to **`origin/sub/AST-909/AST-947-astral-team-workflow`**.

1. Open `docs/ASTRAL_TEAM_WORKFLOW.md` in this epic worktree (`astral-AST-909/`). Do **not** edit `docs/ASTRAL_GIT_WORKFLOW.md` or any team-chuckles file.

2. In **Git and branches** / Local UI (currently ~line 21), replace:

   ```
   **Local UI dev:** repo-root **`launch.sh`** — Flask **`:5001`** + Vite **`:5173`**. Tracked; **do not delete** in merges (`prep-uat` / `merge-parent`). Restore from git if missing. Details: **`orientation`** § Local dev — `launch.sh`.
   ```

   with:

   ```
   **Local UI dev:** repo-root **`launch.sh`** — Flask **`:5001`** + Vite **`:5173`**. Tracked; **do not delete** in merges (`prep-uat` / `finish-up`). Restore from git if missing. Details: **`orientation`** § Local dev — `launch.sh`.
   ```

3. In **Linear status → skill (happy path)** table, PR Ready row (currently ~line 63), replace:

   ```
   | PR Ready | Susan sets **parent** → Chuckles **`merge-parent`** | Land **`origin/ftr/<parent-segment>`** on **`origin/dev`**; **parent + children** → **PR Ready** (children keep engineer **assignee**) |
   ```

   with:

   ```
   | PR Ready | Susan sets **parent** → Chuckles **`finish-up`** | Land **`origin/ftr/<parent-segment>`** on **`origin/dev`** (PR + ref cleanup per **finish-up**); move **parent + shipped children** → **Done** (children keep engineer **assignee**) |
   ```

   ⚠️ **Decision:** Keep the row’s “Susan sets parent → Chuckles …” actor shape; swap the skill name and correct the outcome to **Done** (finish-up’s real close — the old row incorrectly restated **PR Ready**). Do **not** rewrite unrelated rows (User Testing / dispatch assignee notes) in this ticket.

4. Verify:

   ```bash
   rg -n 'merge-parent' docs/ASTRAL_TEAM_WORKFLOW.md
   # expected: no matches
   rg -n 'finish-up' docs/ASTRAL_TEAM_WORKFLOW.md
   # expected: launch.sh note + PR Ready row
   ```

5. Compile/lint sanity (markdown law doc — confirm file non-empty and both replacements present):

   ```bash
   test -s docs/ASTRAL_TEAM_WORKFLOW.md
   rg -n 'prep-uat` / `finish-up|Chuckles \*\*`finish-up` docs/ASTRAL_TEAM_WORKFLOW.md
   ```

6. Commit on this sub checkout and publish:

   ```bash
   git add docs/ASTRAL_TEAM_WORKFLOW.md
   git commit -m "$(cat <<'EOF'
   code(AST-947): name finish-up as TEAM_WORKFLOW parent-close

   EOF
   )"
   git push origin HEAD:sub/AST-909/AST-947-astral-team-workflow
   ```

⚠️ **Decision:** Only the two ticket-named sites (launch.sh note + PR Ready row). Leave Coordinator skill index and Parent epics assignee prose alone — sibling/other tickets own broader consistency, and Boundaries forbid absorbing sibling rows.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-909) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — one astral law markdown file; two prose sites.

**Conf:** high — residue is exactly the two strings named in the ticket; replacement is finish-up per parent AC and orientation commit vocabulary.

**Risk:** low — docs only; wrong naming would mis-route Chuckles at PR Ready in the one-page map, not change scripts.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope only: listed law doc only.
- §1.3 DRY: single-name finish-up as operator parent-close (no dual merge-parent/finish-up).
- §2.1 / §2.4 / §2.6 / §3.3 / §3.5 / §3.6: N/A — docs only.

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Built:** `docs/ASTRAL_TEAM_WORKFLOW.md` on this publish ref
**Publish ref:** `origin/sub/AST-909/AST-947-astral-team-workflow` (this plan + stub; tip set after push)

Stage 1: launch.sh note and PR Ready row name finish-up (outcome Done); no live merge-parent operator naming.

