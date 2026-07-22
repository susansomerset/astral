# finish-up SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-943](https://linear.app/astralcareermatch/issue/AST-943/finish-up-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-943-finish-up`
- **Summary:** Rewrite `team-chuckles/skills/finish-up/SKILL.md` so it is the **sole** Chuckles operator parent-close skill (no “replaces merge-parent skill” sibling framing). Keep **`scripts/git/merge-parent.sh`** named only as an **internal** step of `finish-up-land.sh`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/finish-up/SKILL.md` | Drop sibling/replace-merge-parent framing; clarify `merge-parent.sh` internal-only | skill (team-chuckles) |

**Out of scope:** deleting merge-parent skill (AST-944 — already **Code Complete**; skill dir absent on this host), `install.sh` (AST-945), astral law docs (#17–#18 / AST-946–947), other skills. Docs/templates only.

**Sequencing note (ticket):** “after #15 delete merge-parent skill.” AST-944 is **Code Complete** and `~/team-chuckles/skills/merge-parent/` is gone — build may proceed without waiting further on that sibling.

**Publish note:** Skill edits commit in **team-chuckles** `main`. This plan doc lands only on **`origin/sub/AST-909/AST-943-finish-up`**.

## Authority for the rewrite

1. **Ticket To-be:** sole operator parent-close skill; references `merge-parent.sh` as internal only.
2. **As-is residue:** line **Replaces: `merge-parent` for the happy path** still teaches a sibling skill relationship.
3. Parent AC: operator docs name finish-up (not merge-parent) as the Chuckles parent-close skill.
4. Existing procedure body (gate, `finish-up-land.sh`, Linear Done, blockers) stays — do not redesign land behavior.

## Stage 1: Sole-operator framing + internal `merge-parent.sh`

**Done when:** a reader of finish-up alone sees it as the only Chuckles parent-close skill; `merge-parent` appears only as the internal script path (or explicit “not a skill / retired” note); no “Replaces merge-parent” sibling pairing.

1. Open `~/team-chuckles/skills/finish-up/SKILL.md`.

2. Replace the **Replaces:** line (currently: “`merge-parent` for the happy path — always creates/updates the GitHub PR into `dev`”) with sole-operator wording, e.g.:

   - **Operator parent-close:** this skill is the **only** Chuckles procedure that lands `ftr → origin/dev`, opens/merges the GitHub PR into `dev`, deletes `origin/ftr` + `origin/sub/<parent>/*`, and moves parent/children to **Done** after Susan sets **PR Ready**.
   - Do **not** invoke a `merge-parent` skill (removed — AST-944).

3. In §2 land steps, keep step 2 calling **`merge-parent.sh`**, but label it **internal only**, e.g.:

   - **`merge-parent.sh`** (internal helper of `finish-up-land.sh` — not an operator skill) — merge `origin/ftr` into local `dev`, **`git push origin dev`**, delete **`origin/ftr`**.

4. Leave When / Watcher / Gate / Linear / conflict / blocked-handoff / Output / Does NOT sections intact except where they still say operators should run `merge-parent` as a skill.

5. Do **not** change `scripts/git/merge-parent.sh` or `finish-up-land.sh` under this ticket.

⚠️ **Decision:** Keep calling `merge-parent.sh` by filename (truthful to the land script). Ban teaching `merge-parent` as a discoverable/runnable skill.

## Stage 2: AC grep + commit

**Done when:** grep for live operator `merge-parent` (as a skill) is clean; `finish-up` + internal `merge-parent.sh` remain.

1. Run:

   ```bash
   rg -n 'merge-parent|Replaces' ~/team-chuckles/skills/finish-up/SKILL.md
   ```

   Expected: only `merge-parent.sh` + internal-only wording; no “Replaces: merge-parent” skill pairing.

2. Commit in **team-chuckles** on `main`: `code(AST-943): finish-up sole operator parent-close wording`. `git pull --ff-only origin main` before commit; push `origin main`. Do not commit skill changes into astral. Do not run `install.sh`.

## Execution contract

- Only `finish-up/SKILL.md`.
- If build discovers `merge-parent` skill reinstalled, stop and 🛑 on **AST-909** (AST-944 / install regression).
- After team-chuckles `code(AST-943)`, astral already holds this plan via `plan(AST-943)`.

## Self-Assessment

**Scope:** `minor` — framing/vocabulary on one skill file; land procedure unchanged.

**Conf:** `high` — as-is is a single **Replaces:** line plus one internal script step; AST-944 already removed the sibling skill.

**Risk:** `low` — docs only; wrong edit could confuse whether `merge-parent.sh` still runs inside finish-up-land (Stage 1 keeps it, labeled internal).

## Review

- **Branch:** `origin/sub/AST-909/AST-943-finish-up`
- **Plan tip:** `6e12b03` (`plan(AST-943)`)
- **team-chuckles:** `origin/main` @ `7615d50` — `code(AST-943): finish-up sole operator parent-close wording`
- **Built:** `~/team-chuckles/skills/finish-up/SKILL.md` — sole operator parent-close; `merge-parent.sh` labeled internal-only; Replaces-sibling framing removed.
