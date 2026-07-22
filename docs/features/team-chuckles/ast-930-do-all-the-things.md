# AST-930 — datt SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-930](https://linear.app/astralcareermatch/issue/AST-930/datt-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-930-do-all-the-things`
- **Summary:** Scrub live retired vocabulary from `team-chuckles/skills/do-all-the-things/SKILL.md` only — replace `<joan-uuid>` / `git-store-*` / Joan publish language with honest epic-session + current publish law, and name **finish-up** (not merge-parent) as the Chuckles parent-close skill. Docs/templates only; no product or watcher behavior change. Sibling skills and astral law docs (#17–#18) are out of scope.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/do-all-the-things/SKILL.md` | Vocabulary + prompt-template scrub per stages below (symlinked at `~/.cursor/skills/do-all-the-things/SKILL.md`) | docs / skill |
| `docs/features/team-chuckles/ast-930-do-all-the-things.md` | This plan (already on publish ref) | docs |

**Repos:** `astral` product `src/`, `tests/`, other skills, `orientation`, `install.sh`, `docs/ASTRAL_GIT_WORKFLOW.md`, `docs/ASTRAL_TEAM_WORKFLOW.md`, Radia mid-pipeline docs path (siblings AST-931–AST-947).

**Commit home:** skill edits land in **`team-chuckles`** (then `install.sh` on host if needed). Plan doc only on this astral **`sub/*`** ref.

## Stage 1: Inventory and binding replacements

**Done when:** A short replacement table is applied as the only allowed vocabulary map for Stage 2 edits; grep of the file for retired tokens returns only intentional historical/deprecation notes called out in Stage 3.

1. In `~/team-chuckles/skills/do-all-the-things/SKILL.md`, treat these as **retired live vocabulary** (must not remain as procedural instructions or live prompt placeholders):
   - `<joan-uuid>`
   - `git-store-*`, `store-plan-commit`, `store-code-commit`, `store-qa-commit`, `JOAN_SESSION`
   - `Joan` as git operator / `Joan \`rollup\`` / `Joan \`git.sh …\`` / `closes Joan session`
   - `self-cherry-pick` as a publish path (ban stays; wording must not imply cherry-pick publish)
   - `dev-ada` / `dev-hedy` / `dev-katherine` as epic worktree checkout names (if present)
   - Operator parent-close named **`merge-parent`** (skill or human action)
2. Apply this **binding replacement map** everywhere those tokens appear as live procedure (not inside a one-line historical “as-is → to-be” note):

| From (retired) | To (current law) |
|----------------|------------------|
| `epic worktree=<joan-uuid>` | `epic worktree=$CHUCKLES_ROOT/astral-<PARENT-ID>/` |
| `--session <joan-uuid>` / `with --session <joan-uuid>` on plan/build/test/qa/review handoffs | Drop Joan session flag. After each commit: commit on the active epic worktree checkout, then `git push origin HEAD:<publish-ref>` for that ticket’s row in parent **## Git** (no `git-store-*`, no self-cherry-pick, never `origin/dev`) |
| `After each commit: matching git-store-* for <skill> with --session <joan-uuid>` | `After each commit: <skill> publish per orientation — commit on epic worktree, push to origin/<publish-ref> only` |
| `After each commit: plan-child … --session <joan-uuid>` | `After each commit: plan-child — commit plan on epic worktree, push to origin/<publish-ref>` |
| `After each commit: qa-child … --session <joan-uuid>` | `After each commit: qa-child publish per qa-child §9 — push to origin/<publish-ref> only` |
| `After doc commit: review-child with --session <joan-uuid>` | `After doc commit: review-child — push docs() to origin/<publish-ref> only` |
| `git checkout epic worktree` (literal broken instruction) | `git fetch origin && git checkout sub/<parent-id>/<child-segment> && git merge origin/dev` then, when parent is **In Progress**, `git merge origin/ftr/<parent-segment>` (same shape as orientation § Merge on checkout) |
| Prompt text “for git-store handoffs” | Prompt text for **AGENT_SESSION / `--resume` continuity** only (no git-store) |
| Chuckles table cell `dispatch, prep-uat, merge-parent` | `dispatch, prep-uat, finish-up` (Chuckles still on `$ASTRAL_MAIN` / `dev`) |
| Stage **12b** `merge-child` → **Joan `rollup`** | `merge-child` (run `~/.cursor/skills/merge-child/SKILL.md` / `scripts/git/merge-child.sh` — no Joan) |
| `merge-child/SKILL.md` (Joan **`git.sh rollup`**) | `merge-child/SKILL.md` (no Joan / `git.sh rollup` naming) |
| `prep-uat` / `merge-parent` as the post-sub integration close pair in §4d | `prep-uat` then later **finish-up** after parent **PR Ready** (do not name merge-parent as operator close) |
| §7 title/body “After Susan runs merge-parent” + `git.sh push-dev` / Joan session close | Rewrite: after Susan moves parent to **PR Ready**, Chuckles runs **`finish-up`** (`scripts/git/finish-up-land.sh` / `finish-up` skill). Drop “closes Joan session”. Keep sync-agents / blocked-worktree refresh intent only if still true without Joan; otherwise point at finish-up skill behavior |
| “Replace **`merge-parent`** or Susan UAT” under What this skill does not do | “Replace **`finish-up`** or Susan UAT” |
| “until Joan step re-runs clean” / “blocked Joan/Chuckles step” | “until the blocked Chuckles step (`merge-child` / `prep-uat` / `finish-up` / `refresh-ftr`) re-runs clean” |
| “Run Joan refresh” + framing refresh-ftr as Joan | “Run `./scripts/git/refresh-ftr.sh <parent-id>`” (Chuckles, no Joan) |

⚠️ **Decision:** Use path form `$CHUCKLES_ROOT/astral-<PARENT-ID>/` for `epic worktree=` in prompts, and keep `AGENT_SESSION=<Team row Thread…>` as the sole UUID for `--resume`. Do **not** keep a second UUID alias named `<joan-uuid>` or `<epic-session-uuid>` on the `epic worktree=` line — that was the false Joan identity. The Team **Thread** UUID remains the honest session id via `AGENT_SESSION` only.

⚠️ **Decision:** Do not invent new pipeline stages. Only rename/scrub vocabulary and fix broken checkout/publish lines so they match orientation’s “what never happens” list and current publish law.

## Stage 2: Edit prompt templates and procedure sections

**Done when:** Every headless prompt template and every procedure bullet in this file that previously taught Joan publish, `<joan-uuid>`, or operator **merge-parent** now teaches path + `AGENT_SESSION` + push-to-`origin/<publish-ref>` + **finish-up** for parent close; `git checkout epic worktree` no longer appears.

1. Fix the **Headless CLI flags** bash example at the top of the file: replace the broken `AGENT_SESSION=$(use epic worktree …` line with a clear assignment comment that `AGENT_SESSION` comes from parent **## Team** Thread for that agent × role (no shell substitution from Joan).
2. Rewrite **Session continuity** paragraph: keep mandatory `--resume "${AGENT_SESSION}"`; remove “git-store handoffs”; state that prompt still includes `epic worktree=` (path) and `AGENT_SESSION=` for resume continuity.
3. Update **Git — Chuckles vs agents** table per Stage 1 map (finish-up; agents commit + push directly on active `sub/*`).
4. Edit **all** Prompt templates blocks in place:
   - Dev-agent first-spawn
   - Dev-agent resume-spawn
   - check-linear resume-spawn
   - Betty first-spawn
   - Radia first-spawn  
   Apply Stage 1 replacements line-by-line. Keep FIX-UAT / resume-spawn discipline text otherwise intact.
5. Edit **§4 Pipeline stages** row **12b**, **§4d** partial-cherry-pick paragraph, **§4e** merge-child wording, **§4g** refresh wording, **§6** / **§6a** Joan references, **§7**, and **What this skill does not do** per Stage 1 map.
6. Do **not** change stage numbers, spawn parallelism rules, Team/Thread tables, or watcher-lock mechanics except where wording must drop Joan/merge-parent.

## Stage 3: Grep gate and install note

**Done when:** Grep over this single file for retired live tokens is clean except deliberate historical notes; Linear acceptance criteria for AST-930 are satisfiable from this file alone (sibling files unchecked — out of scope).

1. From `~/team-chuckles`, run:

```bash
rg -n -i 'joan-uuid|git-store|JOAN_SESSION|store-plan-commit|store-code-commit|store-qa-commit|self-cherry-pick|dev-ada|dev-hedy|dev-katherine|Joan `rollup`|Joan `git\.sh|closes Joan|merge-parent' skills/do-all-the-things/SKILL.md
```

2. Allowed leftovers only:
   - Mentions of `merge-parent.sh` as an **internal helper called by finish-up-land** (if any must remain for accuracy) — prefer pointing readers at finish-up skill rather than teaching merge-parent as operator action.
   - Legacy FIX-UAT `<details>` block may keep historical wording **only if** clearly marked obsolete; prefer scrubbing Joan/merge-parent there too so a naive grep stays clean.
3. Prefer **zero** hits for: `joan-uuid`, `git-store`, `JOAN_SESSION`, `Joan` as operator, live `merge-parent` skill name as Chuckles close path.
4. Commit the skill change in **`team-chuckles`** with message `code(AST-930): scrub datt SKILL.md retired Joan/merge-parent vocabulary`. Do not commit astral product code.
5. Note in the Code Complete Linear comment that host effect requires `~/team-chuckles/install.sh` (or equivalent) on the chuckles server — commit alone does not reload `~/.cursor/skills`.

## Execution contract

- Execute stages in order; do not edit sibling skills or astral law docs under this ticket.
- If a line’s intent is unclear between “historical note” and “live procedure,” stop and comment on **AST-909** with the Stage N blocked format — do not guess.
- No product behavior change; no watcher script edits.

## Self-Assessment

**Scope:** `minor` — one skill markdown file in team-chuckles plus this plan doc; no `src/` or pipeline behavior.

**Conf:** `high` — parent definition and AST-930 description spell the as-is/to-be map; current file still contains the exact retired tokens to replace.

**Risk:** `low` — docs/templates only; wrong wording could mis-teach Chuckles spawns until corrected, but cannot change product runtime.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only: single skill file — satisfied.
- §3.6 / docs placement: plan under `docs/features/team-chuckles/` — satisfied.
- No config, batch, state-machine, or import-layer changes — N/A.
- No conflict with orientation “what never happens” (Joan/`git-store-*`/`JOAN_SESSION`/cherry-pick publish/agent-named epic trees) — this plan removes contradictions from datt only.

## Review (build stub)

**Publish ref:** `origin/sub/AST-909/AST-930-do-all-the-things`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `402416b` | Plan doc on astral sub |
| 1–3 | `team-chuckles@242cfce` | Scrub `skills/do-all-the-things/SKILL.md` on `origin/main` (prompts + procedure; finish-up; no Joan/`git-store-*`/`<joan-uuid>`) |

**Tip:** astral plan `402416b` + review stub (this commit); skill live on `team-chuckles` `main` @ `242cfce`. Host needs `install.sh` only if skills are not symlinked from the repo (this host symlinks — already live).

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-909/AST-930-do-all-the-things` @ tip; skill deliverable `team-chuckles@242cfce` (`skills/do-all-the-things/SKILL.md`).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–3 applied: prompt templates use `$CHUCKLES_ROOT/astral-<PARENT-ID>/` + `AGENT_SESSION` only; publish lines push to `origin/<publish-ref>`; stage 12b / §4d–§4g / §6–§7 / “does not do” name `merge-child` / `finish-up` / `refresh-ftr` without Joan/`git-store-*`/`merge-parent` operator close. |
| Grep gate | On scrubbed file: retired live tokens absent; only remaining `self-cherry-pick` hits are explicit **Never** bans (plan allows). Live `~/.cursor/skills/do-all-the-things` symlink matches scrub. |
| Scope / bible | Astral diff is plan + `docs/test-bible/README.md` docs-only note; no `src/` / pytest. Self-Assessment **minor** / **high** / **low** matches footprint. |
| Rules | §1.1 in-scope; docs under `docs/features/team-chuckles/`; layer/debug/external §5a–§5g N/A. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | Linear acceptance text still says “repo-wide” grep; this child correctly scoped to datt only (siblings / law docs = other AST-909 rows). Parent UAT should confirm sibling scrub tickets closed the broader AC. |

**Verdict:** Clean — `resolve-child` may proceed (no product/doc fixes required beyond this `docs()` commit).


## Resolution

**Date:** 2026-07-22

Radia review: **Clean** — no fix-now / discuss items. Advisory (ticket AC “repo-wide” vs child-scoped datt grep) left for parent UAT; no product or skill change required on this child.

- Skill deliverable remains `team-chuckles@242cfce`.
- Radia `docs(AST-930)` intake: `a0268c5` on `origin/sub/AST-909/AST-930-do-all-the-things`.
- resolve: clean — User Testing.
