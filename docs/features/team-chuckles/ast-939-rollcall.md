# AST-939 — rollcall SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-939](https://linear.app/astralcareermatch/issue/AST-939/rollcall-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-939-rollcall`
- **Summary:** Scrub stale-refresh wording in `team-chuckles/skills/rollcall/SKILL.md` so engineers are pointed at current publish (merge + push to `origin/<publish-ref>`) and Chuckles at **merge-child** — not Joan `store-*-commit` / `git.sh rollup`. Docs only; no rollcall script/behavior change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/rollcall/SKILL.md` | Replace Joan stale-refresh vocabulary in §7 (and any leftover hits) | docs / skill |
| `docs/features/team-chuckles/ast-939-rollcall.md` | This plan (on publish ref) | docs |

**Exempt:** `publish_ref_stale.py` and other rollcall scripts (no Joan hits today; do not change behavior), other skills, astral law docs, product code.

**Commit home:** skill edit in **`team-chuckles`**. Plan doc only on this astral **`sub/*`** ref.

## Stage 1: Binding replacement

**Done when:** §7 “Read it” / action hints teach current publish + merge-child only.

1. In `~/team-chuckles/skills/rollcall/SKILL.md` §7 **Read it** bullet for **`STALE(dev+N)`** (currently names Joan **`store-*-commit`** and Joan stale refresh inside **`git.sh rollup`**), replace with:

| From | To |
|------|----|
| engineer refreshes on **`epic worktree`** (merge **`origin/dev`**) then Joan **`store-*-commit`** | engineer refreshes on epic worktree **`astral-<parent-id>/`**: merge **`origin/dev`** (+ **`origin/ftr/<parent-segment>`** when parent is **In Progress**), then **`git push origin HEAD:<publish-ref>`** (no Joan / no `git-store-*` / no self-cherry-pick) |
| or Chuckles **`merge-child`** when child is **User Testing** (Joan stale refresh inside **`git.sh rollup`**) | or Chuckles **`merge-child`** when child is **User Testing** (rollup **`sub/* → ftr/*`** per merge-child skill — no Joan / `git.sh rollup` naming) |

2. Keep **`NOT_ON_FTR` → merge-child`** and **Action hints** intent; scrub any Joan/`store-*`/`git.sh` residue if present (today: only the §7 STALE bullet).
3. Do **not** change table output format, thresholds (`N ≥ 15`, datt `dev+50`), or `publish_ref_stale.py`.

⚠️ **Decision:** Ticket scope is SKILL.md wording only — scripts stay untouched unless a new Joan string appears (verify with grep; current `publish_ref_stale.py` is clean).

## Stage 2: Edit and grep gate

**Done when:** Grep of the skill file is clean for retired live tokens.

1. Apply Stage 1 edit to `skills/rollcall/SKILL.md`.
2. From `~/team-chuckles`, run:

```bash
rg -n -i 'joan|git-store|JOAN_SESSION|store-.*commit|git\.sh rollup|merge-parent' skills/rollcall/SKILL.md
```

3. **Required:** zero hits for Joan ops, `store-*-commit`, `git.sh rollup`. `merge-child` / publish push wording must remain.
4. Commit in **`team-chuckles`**: `code(AST-939): scrub rollcall stale-refresh Joan vocabulary`.
5. Code Complete note: `install.sh` (or equivalent) on host for `~/.cursor/skills/rollcall`.

## Execution contract

- This ticket only.
- No product/watcher behavior change; no auto-run of refresh from rollcall.
- If another section still teaches Joan publish after §7 fix, scrub it in the same commit — do not leave contradictory stale-refresh advice.

## Self-Assessment

**Scope:** `minor` — one skill markdown file (effectively one STALE bullet) plus this plan doc.

**Conf:** `high` — ticket names the exact Joan `store-*-commit` / `git.sh rollup` residue; only one live hit in the skill today.

**Risk:** `low` — docs only; wrong hint text could mis-direct a refresh until fixed.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — satisfied.
- Plan under `docs/features/team-chuckles/` — satisfied.
- Aligns rollcall with orientation “what never happens” (no Joan/`git-store-*`/cherry-pick publish).
