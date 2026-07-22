# AST-936 — qa-child SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-936](https://linear.app/astralcareermatch/issue/AST-936/qa-child-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-936-qa-child`
- **Summary:** Scrub `team-chuckles/skills/qa-child/SKILL.md` so bible land / Chuckles `@Betty` wording names **finish-up** (not merge-parent) for parent close, and rollup language matches **merge-child** / **prep-uat** only (no Joan/`git.sh rollup`). Mid-pipeline Betty publish to **`origin/<publish-ref>`** stays the same intent — drop Joan **`store-qa-commit`** naming only. Docs/templates only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/qa-child/SKILL.md` | Vocabulary scrub per stages below (symlinked at `~/.cursor/skills/qa-child/SKILL.md`) | docs / skill |
| `docs/features/team-chuckles/ast-936-qa-child.md` | This plan (on publish ref) | docs |

**Repos:** other skills, `orientation`, `install.sh`, astral law docs (#17–#18), product `src/` / `tests/`, Betty worktree path rename (`astral-betty` / `astral-tests` stay — current Betty permanent trees per orientation, not retired `dev-ada`-style epic names).

**Commit home:** skill edits in **`team-chuckles`**. Plan doc only on this astral **`sub/*`** ref.

## Stage 1: Binding replacement map

**Done when:** The map below is the only allowed vocabulary for Stage 2 live procedure text.

1. Treat as **retired live vocabulary** in this file:
   - `Joan`, `store-qa-commit`, `git-store-*`, `Joan \`git.sh rollup\``, `Joan \`rollup\``, `Joan \`prep-uat-git\``, `JOAN_SESSION`
   - Operator parent-close / bible-land-to-dev named **`merge-parent`**
2. Apply this **binding map**:

| From (retired) | To (current law) |
|----------------|------------------|
| Betty publishes via Joan **`store-qa-commit`** | Betty commits on **`astral-tests`** (in **`$CHUCKLES_ROOT/astral-betty`** / **`$ASTRAL_TESTS`**), then publishes to **this ticket’s `origin/<publish-ref>`** (child → **`origin/sub/<parent-id>/…`**) by **`git push origin <sha>:<publish-ref>`** (or equivalent direct push of those SHAs only). **Same intent** as today — mid-pipeline bible/tests land on the child publish ref only. No Joan / no self-cherry-pick / never push bible to **`origin/ftr/`** or **`origin/dev`** during **`qa-child`** |
| **`merge-child` → Joan `git.sh rollup`** / “Joan **`rollup`** hits duplicate…” | **`merge-child`** (Chuckles runs `~/.cursor/skills/merge-child/SKILL.md` / `scripts/git/merge-child.sh`) merges **`sub/* → ftr/*`**. Describe rollup conflicts without Joan |
| Chuckles **`merge-child` → Joan `git.sh rollup` / `prep-uat` → Joan `prep-uat-git`** | Chuckles **`merge-child`** then **`prep-uat`** (skills/scripts as named in those skills — no Joan) |
| Betty is only writer on **`origin/dev` via Susan `merge-parent`** | Bible reaches **`origin/dev`** only after Chuckles **`finish-up`** (parent **PR Ready** → land). Mid-pipeline Betty still writes only to **`origin/sub/*`** (and **`origin/tests`** cumulative corpus per existing Betty rules if the skill already states that — do not invent new paths) |
| **Land preflight** “before parent PR Ready / **merge-parent**” | “before parent **PR Ready** / Chuckles **`finish-up`**” |
| “when Chuckles queues **`merge-parent`**” / “invokes before **`merge-parent`**” / “`@Betty` for … **merge-parent** bible conflicts” | Same triggers with **`finish-up`** / **prep-uat** / **merge-child** rollup wording; never teach merge-parent as the operator close skill |
| Gate “required for Joan **`push-dev`**” | Gate required before Chuckles **`finish-up`** lands **`ftr → dev`** (wording may cite `finish-up-land.sh` / finish-up skill — not Joan) |
| Frontmatter / header “Joan store-qa-commit to origin/sub/* only” | “publish bible/tests to origin/sub/* only (Betty push; no Joan)” |

⚠️ **Decision:** Do **not** rename **`astral-betty`** / **`astral-tests`** — those are Betty’s permanent worktrees under current orientation, not the retired engineer epic names (`dev-ada` / `astral-ada`). This ticket’s as-is/to-be is merge-parent→finish-up and Joan rollup→merge-child/prep-uat, with mid-pipeline publish intent unchanged.

⚠️ **Decision:** Do not change qa intake gates (Code Complete / `[qa-handoff]`), bible ownership, or sequential blockedBy order — vocabulary and operator/rollup naming only.

## Stage 2: Edit qa-child SKILL.md

**Done when:** Reading this skill alone teaches finish-up as parent-close land, merge-child/prep-uat as rollup, and Betty mid-pipeline publish without Joan.

1. Update YAML description / opening bullets that name Joan **`store-qa-commit`**.
2. Rewrite the “Who runs this” / publish paragraph (Joan store-qa-commit + merge-child → Joan rollup) per Stage 1.
3. Rewrite **Test Bible — sole authority and cumulative sub chain** rules 1–2, 7, and the publish-target table (Joan rows) per Stage 1.
4. Rewrite **Land preflight** heading + body + Chuckles `@Betty` / PR Ready paragraphs: **finish-up**, not merge-parent; no Joan **`push-dev`**.
5. Rewrite **§9** publish steps if they still say Joan / store-qa-commit — keep commit-on-`astral-tests` + push-to-publish-ref ceremony; keep Forbidden camping on `ftr/*`/`sub/*` **inside Betty’s permanent tree** if that remains current Betty law (Betty stays on `astral-tests`; engineers use epic worktree — do not conflate).
6. Grep-pass the rest of the file for leftover `Joan` / `merge-parent` / `store-qa-commit` / `git.sh rollup`.

## Stage 3: Grep gate and install note

**Done when:** Grep of this file for retired live tokens is clean except deliberate historical notes (prefer zero).

1. From `~/team-chuckles`, run:

```bash
rg -n -i 'joan|git-store|JOAN_SESSION|store-qa-commit|git\.sh rollup|merge-parent' skills/qa-child/SKILL.md
```

2. **Required:** zero live hits for Joan ops, `store-qa-commit`, `git.sh rollup`, and operator **`merge-parent`**. Allowed: `merge-parent.sh` only if noted as finish-up-land **internal** helper (prefer omitting entirely from qa-child).
3. Commit in **`team-chuckles`**: `code(AST-936): scrub qa-child Joan/merge-parent vocabulary`. No astral product commits beyond this plan doc on the sub ref.
4. Code Complete note: host needs `~/team-chuckles/install.sh` (or equivalent) for `~/.cursor/skills/qa-child` to pick up the commit.

## Execution contract

- This ticket only; stages in order.
- If Betty’s §9 pub worktree under `/tmp/` wording conflicts with “no Joan” after edits, stop and comment on **AST-909** — do not invent a new Betty publish topology.
- No product behavior change; mid-pipeline publish target remains **`origin/<publish-ref>`** for the child.

## Self-Assessment

**Scope:** `minor` — one skill markdown file in team-chuckles plus this plan doc.

**Conf:** `high` — ticket as-is/to-be matches the Joan/`merge-parent` residue still in land-preflight and bible-publish sections.

**Risk:** `low` — docs only; wrong operator naming could mis-route Betty land preflight until fixed, not product runtime.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — satisfied.
- Plan under `docs/features/team-chuckles/` — satisfied.
- No config/batch/state/import changes — N/A.
- Aligns qa-child with orientation “what never happens” and finish-up as sole Chuckles parent-close skill.

## Review (build stub)

**Publish ref:** `origin/sub/AST-909/AST-936-qa-child`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `52ee332` | Plan doc on astral sub |
| 1–3 | `team-chuckles@bfc0188` | Scrub `skills/qa-child/SKILL.md` — finish-up land; merge-child/prep-uat rollup; Betty §9 publish without Joan/`store-qa-commit` |

**Tip:** astral plan + stub (this commit); skill on `team-chuckles` `main` @ `bfc0188`.

