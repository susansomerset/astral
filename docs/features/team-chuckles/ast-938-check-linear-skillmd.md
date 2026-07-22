# check-linear SKILL.md (Skill doc consistency pass (pipeline shakedown))

**Linear:** [AST-938](https://linear.app/astralcareermatch/issue/AST-938/check-linear-skillmd-skill-doc-consistency-pass-pipeline-shakedown)  
**Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)  
**Publish ref:** `sub/AST-909/AST-938-check-linear`

Scrub retired Susan-`merge-parent` / Joan `git.sh rollup` / cherry-pick-pollution-escape language from `check-linear`. Handoffs name **finish-up** for parent-close only; **§5c Gate C** matches current **merge-child** → **prep-uat** law. Docs/templates only — no product or watcher behavior change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/check-linear/SKILL.md` | §0a post-merge push (drop Joan/`merge-parent`/`origin/epic worktree`); §4c do-not-narrate list (drop cherry-picked); §5c Gate C + Procedure (merge-child only, no Joan rollup / ftr cherry-pick escape); Handoffs table parent-close → finish-up | skill (team-chuckles) |

**Out of scope (this ticket):** sibling skill rows; astral law docs (#17–#18); `install.sh`; watcher code; Astral `src/` / `tests/` / bible. Leave already-correct **`[wrap]` → finish-up** row and legitimate **`merge-child` / `prep-uat`** references unchanged.

**Commit homes:** skill edit + commit in **team-chuckles**. Plan doc only on this astral **`origin/sub/AST-909/AST-938-check-linear`**. `~/.cursor/skills/check-linear` is a symlink to the team-chuckles skill dir.

---

## Stage 1: Align check-linear handoffs + Gate C with orientation

**Done when:** `~/team-chuckles/skills/check-linear/SKILL.md` no longer teaches Joan `git.sh rollup`, `git-store-*`, `JOAN_SESSION`, merge-parent as the operator parent-close skill, or cherry-pick onto `ftr` as a Gate C escape. Parent-close handoff names **finish-up**. Gate C requires child tips on `origin/ftr` via **merge-child**. Verification grep (step 6) is clean for live residue. Changes committed and pushed in team-chuckles.

1. Open `~/team-chuckles/skills/check-linear/SKILL.md`. Do **not** edit any other skill file.

2. In **§0a** (currently ~line 152), replace:

   ```
   **After merge (when `origin/dev` advanced — e.g. merge-parent team sync):** **`git push origin <integration-branch>:refs/heads/<integration-branch>`** so **`origin/epic worktree`** matches your worktree. Joan **`sync-agents`** may have pushed already — push anyway if your tip is ahead of **`origin/epic worktree`**.
   ```

   with:

   ```
   **After merge (when `origin/dev` advanced — e.g. finish-up landed a parent on `origin/dev`):** if **`<integration-branch>`** is a permanent branch that tracks origin (**`dev`** or **`tests`**), and your tip is ahead of **`origin/<integration-branch>`**, **`git push origin HEAD:<integration-branch>`**. Do **not** push agent-named or epic-worktree scratch refs. Never Joan **`sync-agents`** / **`git-store-*`**.
   ```

3. In **§4c** “Do not put in the comment” (currently ~line 297), replace:

   ```
   - What you did this pass (merged, replied, scanned inbox, ran agent, cherry-picked, posted table)
   ```

   with:

   ```
   - What you did this pass (merged, replied, scanned inbox, ran agent, posted table)
   ```

4. In **§5c Gates** item 2 (currently ~line 366), replace:

   ```
   2. **Git Gate C:** child publish tips integrated on **`origin/ftr/<parent-segment>`** — via Joan **`git.sh rollup`**, or **`ftr`-only cherry-pick** when **`sub/*`** is polluted (**`orientation` § Publish preflight`** — **never** blind merge polluted **`sub/*`**).
   ```

   with:

   ```
   2. **Git Gate C:** every rollup-safe child's **`origin/sub/<parent-id>/…`** tip is already on **`origin/ftr/<parent-segment>`** via **`merge-child`** (`validate-sub-log` + `merge-child.sh`). Never Joan **`git.sh rollup`**, **`git-store-*`**, or cherry-pick onto **`ftr`**. If a **`sub/*`** tip is polluted, stop and fix per **`merge-child`** / orientation — never blind-merge polluted **`sub/*`**.
   ```

5. In **§5c Procedure** (currently ~line 370), replace:

   ```
   **Procedure:** **`~/.cursor/skills/merge-child/SKILL.md`** → **`~/.cursor/skills/prep-uat/SKILL.md`**. Skip **`prep-uat-git`** merge of polluted **`sub/*`** when UX delta was cherry-picked onto **`ftr`** already.
   ```

   with:

   ```
   **Procedure:** **`~/.cursor/skills/merge-child/SKILL.md`** → **`~/.cursor/skills/prep-uat/SKILL.md`**. Do **not** skip **`merge-child`** or substitute cherry-picking UX deltas onto **`ftr`**.
   ```

6. In **Handoffs** table (currently ~line 392), replace:

   ```
   | **Parent/standalone**, thread resolved | **§4a:** assignee → **Susan** | Susan **`merge-parent`** as status dictates |
   ```

   with:

   ```
   | **Parent/standalone**, thread resolved | **§4a:** assignee → **Susan** | Susan moves parent to **PR Ready** → Chuckles **`finish-up`** as status dictates |
   ```

   Do **not** change the already-correct **`[wrap]` → finish-up** row (~line 25) or other **`merge-child` / `prep-uat` / `fix-uat`** rows that already match current law.

7. From `~/team-chuckles`, verify (must be empty for live residue):

   ```bash
   cd ~/team-chuckles
   rg -n 'git-store|JOAN_SESSION|joan-uuid|git\.sh rollup|sync-agents|merge-parent|cherry-pick|origin/epic worktree|dev-ada|dev-hedy|dev-katherine' skills/check-linear/SKILL.md
   ```

   Expected: no matches. If ban wording (“Never … cherry-pick / Joan”) still hits, tighten the pattern until only empty output remains for *retired teaching*.

8. Commit and push in **team-chuckles** only:

   ```bash
   cd ~/team-chuckles
   git add skills/check-linear/SKILL.md
   git commit -m "$(cat <<'EOF'
   code(AST-938): align check-linear Gate C and handoffs with finish-up

   EOF
   )"
   git push origin HEAD
   ```

⚠️ **Decision:** Gate C requires **merge-child** integration only — drop Joan rollup and ftr cherry-pick pollution escape entirely (orientation never-list bans cherry-pick onto published branches).

⚠️ **Decision:** Parent/standalone handoff names **finish-up** after Susan sets **PR Ready** — not Susan running merge-parent herself. Mid-epic **merge-child** + **prep-uat** rows stay as Chuckles auto-path under §5c.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-909) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — one team-chuckles skill markdown file; §0a, §4c, §5c Gate C/Procedure, Handoffs table.

**Conf:** high — residue is located (Joan `git.sh rollup`, ftr cherry-pick escape, Susan `merge-parent` handoff, Joan `sync-agents` / `origin/epic worktree`); replacement matches merge-child → prep-uat and finish-up parent-close already used in this epic’s plans.

**Risk:** low — docs/templates only; wrong Gate C wording could mis-route Chuckles rollup, but no product/git scripts change in this ticket.

## Rules check (ASTRAL_CODE_RULES)

- §1.1 in-scope only: listed skill file only.
- §1.3 DRY: reuse merge-child / finish-up naming; do not invent a new rollup path.
- §2.1 / §2.4 / §2.6 / §3.3 / §3.5 / §3.6: N/A — docs/skill only.

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Built:** team-chuckles `origin/main` @ `d707c401f168d32c904167944941eb0df9f42e7d` (`skills/check-linear/SKILL.md`)
**Publish ref:** `origin/sub/AST-909/AST-938-check-linear` @ `0841175094b09ef84b2edba4f13b8e6b5f048af2` (this plan + stub)

Stage 1: §0a post-merge push, §4c narrate ban, §5c Gate C/Procedure, Handoffs parent-close → finish-up / merge-child only.

## Tests (engineer)

**Manifest:** Betty docs-only / no pytest. Grep gate on `skills/check-linear/SKILL.md` — only deliberate bans (`Never Joan` / `git-store-*` / rollup); Gate C = merge-child + prep-uat; parent-close = finish-up. Plan Stage 1 + `team-chuckles@d707c40` spot-check OK.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-909/AST-938-check-linear`; skill deliverable `team-chuckles@d707c40` (`skills/check-linear/SKILL.md`).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stage 1: §0a post-merge → finish-up land + permanent-branch push; §4c drops cherry-picked narrate; §5c Gate C = merge-child only (no Joan rollup / ftr cherry-pick escape); Handoffs parent-close → Susan PR Ready → Chuckles finish-up. |
| Grep gate | Live-residue patterns empty; remaining hits are deliberate **Never** bans only. Live symlink matches. |
| Scope / bible | Astral diff: plan + `docs/test-bible/README.md` docs-only note; no `src/` / pytest. Self-Assessment footprint matches. |
| Rules | §1.1 in-scope; docs under `docs/features/team-chuckles/`; §5a–§5g N/A. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | Linear AC still says repo-wide grep; this child correctly scoped to `check-linear` only (siblings = other AST-909 rows). |

**Verdict:** Clean — `resolve-child` may proceed (no product/doc fixes required beyond this `docs()` commit).

## Resolution

**Date:** 2026-07-22
**Radia:** `docs(AST-938): Radia review — clean` @ `e2e8887` — no fix-now. Advisory only (repo-wide AC vs child scope); no product/doc change required.
**Outcome:** `resolve(AST-938): — clean`

