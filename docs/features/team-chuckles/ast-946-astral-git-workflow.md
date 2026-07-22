# ASTRAL_GIT_WORKFLOW.md (Skill doc consistency pass)

- **Linear:** [AST-946](https://linear.app/astralcareermatch/issue/AST-946/astral-git-workflowmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-946-astral-git-workflow`
- **Summary:** Update `docs/ASTRAL_GIT_WORKFLOW.md` so operator-facing commit vocab and Chuckles tables name **`finish-up()`** (not `merge-parent()`) as the ftr→dev / parent-close action; mention `merge-parent.sh` only as an internal helper of finish-up-land. Do **not** change Radia `docs()` commit type or message conventions.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/ASTRAL_GIT_WORKFLOW.md` | Operator rename merge-parent → finish-up; internal-only note for `merge-parent.sh` | astral law doc |

**Out of scope:** `docs/ASTRAL_TEAM_WORKFLOW.md` (AST-947), team-chuckles skills, `scripts/git/merge-parent.sh` behavior, Radia `docs()` semantics. Docs only — no product `src/` / tests.

**Publish note:** This is an **astral** law-doc child (#17). Plan + later `code(AST-946)` both land on **`origin/sub/AST-909/AST-946-astral-git-workflow`**. No team-chuckles commit required for this ticket.

## Authority for the rewrite

1. **Ticket To-be:** operator action = `finish-up()`; `merge-parent.sh` internal-only if mentioned. Does not change Radia `docs()`.
2. Parent AC: operator docs name finish-up (not merge-parent) as the Chuckles parent-close skill; dual-naming of merge-parent vs finish-up as the human/Chuckles action is gone.
3. Existing retired note (`Joan git-store-* cherry-pick skills are retired`) may stay as deliberate historical/deprecation text.

## Stage 1: Operator tables — `merge-parent()` → `finish-up()`

**Done when:** Chuckles-owned merges table, Complete commit vocabulary row, and Skills map row name **`finish-up()`** / skill **`finish-up`** as the ftr→dev operator action; no live row teaches agents to run `merge-parent` as the close skill.

1. Open `docs/ASTRAL_GIT_WORKFLOW.md` on this sub (after merge-clean).

2. **§ Chuckles-owned merges** table — change the second row from `` `merge-parent(AST-NNN)` | ftr → dev `` to `` `finish-up(AST-NNN)` | ftr → dev (parent close after PR Ready) ``. Keep `merge-child(AST-NNN)` unchanged.

3. Immediately under that table (or as a one-line note in the same section), add: **`scripts/git/merge-parent.sh`** is invoked only by **`finish-up-land.sh`** (internal land helper) — agents and operators run the **`finish-up`** skill, not `merge-parent` as a skill/commit name.

4. **§ Complete commit vocabulary** — replace the `` `merge-parent()` | Chuckles | Yes | Ftr → dev `` row with `` `finish-up()` | Chuckles | Yes | Ftr → dev (parent close; after Susan sets PR Ready) ``. Keep `` `docs()` | Radia `` row and the `docs()` / `resolve()` message convention block **byte-identical in meaning** (no rename of Radia `docs()`).

5. Keep “Ten commit types. One owner each.” if the count remains ten after the rename (same slot, new name). If any prose still says the tenth type is `merge-parent()`, update that prose to `finish-up()`.

6. **§ Skills map** — change `` `merge-parent` / `prep-uat` | Ftr → dev; prep-uat pushes `origin/dev` `` to `` `finish-up` / `prep-uat` | finish-up lands ftr → `origin/dev` (parent close); prep-uat pushes `origin/dev` for staging UAT ``. Do not remove `prep-uat` or `merge-child` rows.

⚠️ **Decision:** The operator-facing commit/skill name is **`finish-up()`**. Any remaining `merge-parent` string in this file must be either (a) the internal script path `scripts/git/merge-parent.sh` with “internal only” wording, or (b) deliberate deprecation (“retired / do not use as operator action”).

## Stage 2: Full-file sweep + AC grep

**Done when:** `rg` shows no live operator `merge-parent()` / skill `merge-parent` as the Chuckles close action; Radia `docs()` conventions still present; Joan retirement note may remain.

1. Sweep the whole file for `merge-parent` (including flow diagrams or prose). Convert operator uses to `finish-up`; leave only internal-script or deprecation mentions.

2. Confirm these stay unchanged in intent:

   - Radia `` `docs(AST-NNN): Radia review — clean|findings` ``
   - Engineer/Betty sequence (`plan` … `resolve`, `merge-tests`)
   - “What never happens” cherry-pick / `dev-<agent>` bans
   - Opening line that Joan `git-*` skills are superseded (historical OK)

3. Acceptance grep:

   ```bash
   rg -n 'merge-parent' docs/ASTRAL_GIT_WORKFLOW.md
   ```

   Expected: only `merge-parent.sh` + internal-only wording, and/or explicit deprecation — **zero** rows teaching `merge-parent()` as the Chuckles operator commit/skill.

   ```bash
   rg -n 'finish-up|docs\(AST-NNN\): Radia review' docs/ASTRAL_GIT_WORKFLOW.md
   ```

   Expected: `finish-up` present in Chuckles tables; Radia `docs()` message conventions still present.

4. Commit on this sub: `code(AST-946): finish-up replaces merge-parent in git workflow law`. Push `git push origin HEAD:sub/AST-909/AST-946-astral-git-workflow`. No team-chuckles commit. No `install.sh`.

## Execution contract

- Only `docs/ASTRAL_GIT_WORKFLOW.md` (+ this plan already on the ref).
- Do not edit `ASTRAL_TEAM_WORKFLOW.md` or any skill under this ticket.
- If finish-up wording would remove or rename Radia `docs()`, stop and 🛑 on **AST-909**.

## Self-Assessment

**Scope:** `Single-Component` — one astral law markdown file on this publish ref.

**Conf:** `high` — ticket names exact as-is/to-be; three primary hit sites (Chuckles-owned merges, commit vocab, skills map) plus a file-wide `merge-parent` sweep.

**Risk:** `low` — docs only; mis-naming could confuse Chuckles land, but Stage 1 keeps `merge-parent.sh` as the documented internal helper under finish-up-land.
