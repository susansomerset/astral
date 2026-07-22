# dispatch-parent SKILL.md (Skill doc consistency pass (pipeline shakedown))

**Linear:** [AST-932](https://linear.app/astralcareermatch/issue/AST-932/dispatch-parent-skillmd-skill-doc-consistency-pass-pipeline-shakedown)  
**Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)  
**Publish ref:** `sub/AST-909/AST-932-dispatch-parent`

Scrub retired Joan/`git-store-*`/self-cherry-pick publish language from `dispatch-parent` so engineer handoff and the child **Git branch** Description template match orientation's publish path (`git push origin HEAD:<publish-ref>` on the epic worktree sub checkout). Docs/templates only — no product behavior change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/dispatch-parent/SKILL.md` | Replace cherry-pick / `git-store-*` publish wording in §7 child Description template and §10 Engineer handoff with orientation-aligned push-to-publish-ref wording | skill (team-chuckles) |

**Out of scope (this ticket):** sibling skill rows (#1–#2, #4–#18); `docs/ASTRAL_GIT_WORKFLOW.md` / `docs/ASTRAL_TEAM_WORKFLOW.md` (#17–#18); renaming §2c `merge-parent` → `finish-up` (owned by orientation / finish-up / delete-merge-parent children); `install.sh`; watcher behavior; Astral `src/` / `tests/` / bible.

**Commit homes:** skill edit + commit land in the **team-chuckles** repo (`~/team-chuckles`). Plan doc only on this astral **`origin/sub/AST-909/AST-932-dispatch-parent`**. `~/.cursor/skills/dispatch-parent` is already a symlink to the team-chuckles skill dir — no `install.sh` required for the scrub to take effect on this host after the team-chuckles commit.

---

## Stage 1: Align dispatch-parent publish handoff with orientation

**Done when:** `~/team-chuckles/skills/dispatch-parent/SKILL.md` has zero live occurrences of `git-store-*`, `JOAN_SESSION`, `joan-uuid`, or instructions to cherry-pick / self-cherry-pick onto publish refs. The §7 **Git branch (authoritative)** template and the §10 **Engineer handoff** sentence both tell engineers to publish with `git push origin HEAD:<publish-ref>` from the epic worktree sub checkout. A verification grep (step 3) returns no residual hits except intentional historical/deprecation notes (none expected in this file after the scrub). Changes are committed on the team-chuckles default working branch and pushed to that repo's origin.

1. Open `~/team-chuckles/skills/dispatch-parent/SKILL.md`. Do **not** edit any other skill file in this stage.

2. In **§7 Create child tickets**, inside the Description fenced template, replace the **Git branch (authoritative)** closing sentence that currently reads (exact current text):

   ```
   Created at **dispatch-parent**. Engineers cherry-pick to **`origin/<ftr-ref>`** or
   **`origin/<sub-ref>`** — never Linear **`gitBranchName`** when it disagrees.
   ```

   with:

   ```
   Created at **dispatch-parent**. Engineers publish to **`origin/<sub-ref>`** (child)
   or **`origin/<ftr-ref>`** (standalone) by committing on the epic worktree sub
   checkout then **`git push origin HEAD:<publish-ref>`** — never Linear
   **`gitBranchName`** when it disagrees. Never **`git-store-*`**, Joan, or
   self-cherry-pick.
   ```

   Keep the preceding "Per **`orientation` § Branch law**…" lines in that template block unchanged.

3. In **§10 Verify and close**, replace the **Engineer handoff** paragraph that currently reads (exact current text):

   ```
   **Engineer handoff:** When children start **plan-child**, merge **`origin/dev`** into **`epic worktree`** per **orientation § Merge integration line**. Publish via **`git-store-*`** with **`epic worktree`** from the spawn prompt — **not** self-cherry-pick.
   ```

   with:

   ```
   **Engineer handoff:** When children start **plan-child**, merge **`origin/dev`** into the epic worktree per **orientation § Merge integration line**, and on each sub checkout merge **`origin/ftr/<parent-segment>`**. Publish each commit with **`git push origin HEAD:sub/<parent-id>/<child-segment>`** (or the ticket's **`<publish-ref>`** from the parent **Git** table) — **not** **`git-store-*`**, Joan, or self-cherry-pick.
   ```

4. Leave every other section unchanged. In particular do **not** rewrite §2c's `prep-uat / merge-parent` hot-file phrase in this ticket (sibling finish-up / orientation children own that rename).

5. From `~/team-chuckles`, run verification (must exit 0 with empty match set for live residue):

   ```bash
   cd ~/team-chuckles
   rg -n 'git-store|JOAN_SESSION|joan-uuid|self-cherry-pick|cherry-pick to' skills/dispatch-parent/SKILL.md
   ```

   Expected: no matches. If any match remains, fix it in this file only and re-run until clean. Do **not** treat the new "Never … self-cherry-pick" ban wording as a failure — if `rg` hits those ban lines because of the literal substring, narrow the pattern to:

   ```bash
   rg -n 'git-store|JOAN_SESSION|joan-uuid|Publish via \*\*`git-store|Engineers cherry-pick' skills/dispatch-parent/SKILL.md
   ```

   That narrowed pattern must return empty.

6. Commit and push in **team-chuckles** only (not astral):

   ```bash
   cd ~/team-chuckles
   git add skills/dispatch-parent/SKILL.md
   git commit -m "$(cat <<'EOF'
   code(AST-932): align dispatch-parent publish handoff with orientation

   EOF
   )"
   git push origin HEAD
   ```

   If the team-chuckles branch naming / push target differs from `HEAD` tracking, push to the branch already checked out for Team Chuckles skill work — do not create astral `sub/*` refs inside team-chuckles.

⚠️ **Decision:** Only scrub the two publish-path passages named above. Leaving §2c `merge-parent` wording alone avoids absorbing #13–#15 scope; parent AC for finish-up naming is owned by those children.

⚠️ **Decision:** Replacement publish text uses `git push origin HEAD:<publish-ref>` (same ceremony as current `plan-child` / `ASTRAL_GIT_WORKFLOW` Betty merge-tests push) rather than inventing a new helper script name — Joan/`git-store-*` is retired and must not be replaced with another agent-named store wrapper.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-909) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — one team-chuckles skill markdown file; two prose passages.

**Conf:** high — residue is already located (`Engineers cherry-pick` in §7 template; `Publish via git-store-*` in §10); replacement text is the same publish ceremony already documented in `plan-child` §9 and `ASTRAL_GIT_WORKFLOW.md`.

**Risk:** low — docs/templates only; a wrong sentence would mis-teach Chuckles/engineer handoff prose, not change product or git scripts.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope only: this plan touches only the listed skill file.
- §1.3 DRY: reuse orientation / plan-child publish wording; do not invent a second publish ceremony.
- §2.1 / §2.4 / §2.6: N/A — no config, batch, or state-machine changes.
- §3.3 / §3.5: N/A — no Python modules.
- §3.6 spikes: N/A — no spike output.

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Built:** team-chuckles `origin/main` @ `f3dd732ac63c4aa36a49370a66e81a9e2cab8391` (`skills/dispatch-parent/SKILL.md`)
**Publish ref:** `origin/sub/AST-909/AST-932-dispatch-parent` @ `8223327e9d7460236a50ec7b4a4a5bcc4cc0bce7` (this plan + stub)

Stage 1: §7 Git branch template and §10 Engineer handoff now teach `git push origin HEAD:<publish-ref>` — no Joan/`git-store-*`/cherry-pick publish. §2c `merge-parent` phrase left for sibling tickets.

## Tests (engineer)

**Manifest:** Betty docs-only / no pytest. Grep gate on `skills/dispatch-parent/SKILL.md` — only deliberate bans (`Never git-store-*` / self-cherry-pick); publish path `git push origin HEAD:<publish-ref>` confirmed. Plan Stage 1 + `team-chuckles@f3dd732` spot-check OK.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-909/AST-932-dispatch-parent`; skill deliverable `team-chuckles@f3dd732` (`skills/dispatch-parent/SKILL.md`).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stage 1 only: §7 Git branch template and §10 Engineer handoff now teach `git push origin HEAD:<publish-ref>` / `HEAD:sub/…`; no live Joan / `git-store-*` / cherry-pick publish. §2c `merge-parent` left per plan Decision (sibling tickets). |
| Grep gate | Broad `rg` hits only deliberate **Never …** bans; narrowed pattern (`Publish via git-store` / `Engineers cherry-pick` / `JOAN_SESSION` / `joan-uuid`) empty. Live symlink matches. |
| Scope / bible | Astral diff: plan + `docs/test-bible/README.md` docs-only note; no `src/` / pytest. Self-Assessment footprint matches. |
| Rules | §1.1 in-scope; docs under `docs/features/team-chuckles/`; §5a–§5g N/A. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | Linear AC still says repo-wide grep; this child correctly scoped to `dispatch-parent` only (siblings = other AST-909 rows). |

**Verdict:** Clean — `resolve-child` may proceed (no product/doc fixes required beyond this `docs()` commit).

