# AST-942 — orientation SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-942](https://linear.app/astralcareermatch/issue/AST-942/orientation-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-942-orientation`
- **Summary:** Update `team-chuckles/skills/orientation/SKILL.md` so the git **Flow** diagram ends at **finish-up** (not merge-parent as operator close). Keep the **What never happens** ban on Joan/`git-store-*`/`JOAN_SESSION`. Keep `merge-parent.sh` only as the finish-up-land internal helper row. Docs only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/orientation/SKILL.md` | Flow line + any leftover operator merge-parent naming; preserve never-list + script helper row | docs / skill |
| `docs/features/team-chuckles/ast-942-orientation.md` | This plan (on publish ref) | docs |

**Exempt:** other skills, astral `docs/ASTRAL_*.md` (#17–#18 — siblings), `install.sh`, product code, deleting `merge-parent.sh` (script stays; AST-944 deletes the skill).

**Commit home:** skill edit in **`team-chuckles`**. Plan doc only on this astral **`sub/*`** ref.

## Stage 1: Binding edits

**Done when:** Flow teaches finish-up as the sub→dev operator close; never-list unchanged in intent; `merge-parent.sh` is helper-only.

1. In **Flow** block, change:

```
sub   → ftr → dev   (merge-child, prep-uat, merge-parent)
```

to:

```
sub   → ftr → dev   (merge-child, prep-uat, finish-up)
```

⚠️ **Decision:** Keep `merge-child` and `prep-uat` on that line — they remain real intermediate Chuckles steps; only replace the terminal operator name **merge-parent → finish-up**.

2. **Keep** **What never happens** entries including:
   - Joan / `git-store-*` / `JOAN_SESSION`
   - Cherry-pick onto published branches  
   Do **not** weaken or remove this list.

3. **Keep** Git scripts table row:
   - `scripts/git/merge-parent.sh` | **called by finish-up-land**  
   Optionally clarify in the Skill column text only if needed: “internal helper of finish-up-land — not an operator skill.” Do **not** reintroduce a merge-parent skill as the close path.

4. Confirm commit vocabulary already has `finish-up()` and skill index already lists `finish-up` — leave unless a stray operator **merge-parent** remains elsewhere in this file.

5. Grep the whole file for live operator **merge-parent** (skill/human action). Allowed leftover: `merge-parent.sh` as finish-up-land helper only.

## Stage 2: Grep gate and install note

**Done when:** Grep is clean for retired live operator vocabulary except the deliberate helper-script note.

1. Apply Stage 1 to `skills/orientation/SKILL.md`.
2. From `~/team-chuckles`, run:

```bash
rg -n -i 'merge-parent|joan|git-store|JOAN_SESSION' skills/orientation/SKILL.md
```

3. **Required:**
   - Flow line contains **finish-up**, not operator merge-parent.
   - Never-list still bans Joan / `git-store-*` / `JOAN_SESSION`.
   - Any `merge-parent` hit is only `merge-parent.sh` + finish-up-land helper framing.
4. Commit in **`team-chuckles`**: `code(AST-942): orientation flow ends at finish-up`.
5. Code Complete note: host `install.sh` (or equivalent) for `~/.cursor/skills/orientation`.

## Execution contract

- This ticket only — do not edit astral law docs or delete the merge-parent skill (siblings).
- Do not change watcher behavior or invent new never-list items beyond aligning Flow.
- If Flow and skill-index already disagree after edit, stop and comment on **AST-909**.

## Self-Assessment

**Scope:** `minor` — one skill markdown (primarily the Flow one-liner) plus this plan doc.

**Conf:** `high` — ticket as-is/to-be matches the single Flow `merge-parent` residue; never-list and `merge-parent.sh` helper row already match the to-be.

**Risk:** `low` — docs only; wrong Flow label mis-teaches parent close until fixed.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — satisfied.
- Plan under `docs/features/team-chuckles/` — satisfied.
- Aligns orientation Flow with finish-up as sole Chuckles parent-close skill while preserving “what never happens.”

## Review (build stub)

**Publish ref:** `origin/sub/AST-909/AST-942-orientation`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `88905f2` | Plan doc on astral sub |
| 1–2 | `team-chuckles@cf7e7a5` | Flow ends at finish-up; keep never-list; `merge-parent.sh` helper-only |

**Tip:** astral plan + stub (this commit); skill on `team-chuckles` `main` @ `cf7e7a5`.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-909/AST-942-orientation`; skill deliverable `team-chuckles@cf7e7a5` (`skills/orientation/SKILL.md`).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–2: Flow `sub → ftr → dev` ends at **finish-up** (keeps merge-child, prep-uat); never-list still bans Joan/`git-store-*`/`JOAN_SESSION` + cherry-pick; `merge-parent.sh` clarified as finish-up-land internal helper only. |
| Grep gate | Only never-list Joan ban + `merge-parent.sh` helper row. No operator merge-parent. Live symlink matches. |
| Scope / bible | Astral diff: plan + `docs/test-bible/README.md` docs-only note; no `src/` / pytest. Self-Assessment footprint matches. |
| Rules | §1.1 in-scope; docs under `docs/features/team-chuckles/`; §5a–§5g N/A. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | Linear AC still says repo-wide grep; this child correctly scoped to `orientation` SKILL.md only (astral law docs = siblings AST-946/947). |

**Verdict:** Clean — `resolve-child` may proceed (no product/doc fixes required beyond this `docs()` commit).


## Resolution

**Date:** 2026-07-22

Radia review: **Clean** — no fix-now / discuss items. Advisory (ticket AC “repo-wide” vs child-scoped orientation grep) left for parent UAT.

- Skill deliverable remains `team-chuckles@cf7e7a5`.
- Radia `docs(AST-942)` intake: `cdb164e` on `origin/sub/AST-909/AST-942-orientation`.
- resolve: clean — User Testing.
