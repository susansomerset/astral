# audit-linear SKILL.md (Skill doc consistency pass)

- **Linear:** [AST-940](https://linear.app/astralcareermatch/issue/AST-940/audit-linear-skillmd-skill-doc-consistency-pass-pipeline-shakedown)
- **Parent:** [AST-909](https://linear.app/astralcareermatch/issue/AST-909/skill-doc-consistency-pass-pipeline-shakedown)
- **Publish ref:** `origin/sub/AST-909/AST-940-audit-linear`
- **Summary:** Rewrite `team-chuckles/skills/audit-linear/SKILL.md` so after-land / Done / “does not …” wording names **finish-up** (not merge-parent) as the Chuckles parent-close path. Do **not** change the optional mid-epic audit `docs()` path (§7).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/audit-linear/SKILL.md` | Replace merge-parent as operator/after-land name with finish-up; keep §7 audit docs() | skill (team-chuckles) |

**Out of scope:** `finish-up` skill body (AST-943), `review-child`, astral law docs (#17–#18), other skills. Docs/templates only.

**Publish note:** Skill edits commit in **team-chuckles**. This plan doc lands only on **`origin/sub/AST-909/AST-940-audit-linear`**.

## Authority for the rewrite

1. **Ticket To-be:** after-land / Done path = finish-up. Does not change optional mid-epic audit `docs()` path.
2. **Parent clarification:** finish-up is only Chuckles parent-close after PR Ready. Mid-pipeline Radia `docs()` stays mid-pipeline — audit-linear’s optional §7 doc commit on `origin/ftr/<parent-segment>` is that optional mid-epic path; leave its ceremony intent.
3. Operator AC: name finish-up (not merge-parent) as the Chuckles parent-close skill.
4. **`orientation` § What never happens** / skill index: finish-up is the Chuckles close skill; `merge-parent.sh` is finish-up-land internal only (do not teach Susan/Chuckles “run merge-parent” as the operator action).

## Stage 1: Rename after-land / Done / “does not” merge-parent → finish-up

**Done when:** every live procedure or “does not …” line that named **merge-parent** as the human/Chuckles after-land or Done action says **finish-up** instead; §3 fallback “after merge-parent: ftr deleted” uses finish-up wording.

1. Open `~/team-chuckles/skills/audit-linear/SKILL.md`.

2. §3 Feature tip order, item 2 — change:

   - From: `After merge-parent: ftr deleted — use origin/dev …`
   - To: `After finish-up (ftr deleted / landed on origin/dev): use origin/dev tip if parent commits are reachable …`

   Keep the same git evidence command (`git log origin/dev --oneline --grep='<parent-id>'`).

3. **What this skill does NOT do** — change:

   - `Does not run prep-uat, merge-parent, or engineer fixes.` → `Does not run prep-uat, finish-up, or engineer fixes.`
   - `Does not mark parent Done — Susan merge-parent after PR Ready.` → `Does not mark parent Done — Chuckles finish-up after Susan moves parent to PR Ready.` (Chuckles is the finish-up actor; Susan sets PR Ready.)

4. Do **not** rename `prep-uat`, `merge-child`, or `review-child` references. Do **not** delete or rewrite §7 optional doc commit (`docs(<parent-id>): Radia audit — …` on `origin/ftr/<parent-segment>` per review-child §6) — that is the optional mid-epic audit `docs()` path this ticket explicitly preserves.

5. If `merge-parent` remains anywhere as a live operator instruction, convert to finish-up or to an explicit deprecation note (“`merge-parent.sh` is internal to finish-up-land only — do not invoke as the close skill”). Prefer zero live `merge-parent` hits.

⚠️ **Decision:** Actor for parent-close is **Chuckles finish-up** after Susan sets **PR Ready** — not “Susan merge-parent.” Optional §7 audit `docs()` on ftr stays mid-epic and is not moved into finish-up.

## Stage 2: AC grep + light retired-vocab sweep

**Done when:** grep for live `merge-parent` / Joan / store / `dev-ada` residue on this file is clean (or only deliberate deprecation), and §7 still documents optional mid-epic audit `docs()`.

1. Run:

   ```bash
   rg -n 'merge-parent|Joan|git-store|JOAN_SESSION|store-.*-commit|self-cherry-pick|dev-ada|dev-hedy|dev-katherine|<joan-uuid>' \
     ~/team-chuckles/skills/audit-linear/SKILL.md
   ```

   Expected: no live merge-parent-as-operator; no Joan/store; §7 still present with `docs(` / Radia audit.

2. If `astral-radia` appears as a persistent epic worktree checkout name conflicting with orientation’s “Not used: astral-ada / dev-<agent>” list, rewrite to read-only git in `$ASTRAL_MAIN` / shared astral root (Radia does not need a `dev-radia` camping branch). Do **not** invent a new publish ceremony — this skill stays read-only aside from optional §7 doc commit already defined via review-child.

3. Commit in **team-chuckles**: `code(AST-940): audit-linear after-land finish-up wording`. Do not commit skill changes into astral. Do not run `install.sh`.

## Execution contract

- Only `audit-linear/SKILL.md`; preserve §7 mid-epic audit docs path.
- If a change would remove or defer §7 to finish-up, stop and 🛑 on **AST-909**.
- After team-chuckles `code(AST-940)`, astral already holds this plan via `plan(AST-940)`.

## Self-Assessment

**Scope:** `minor` — vocabulary swap on one skill file; optional §7 left intact by design.

**Conf:** `high` — ticket names the exact as-is/to-be strings; only three `merge-parent` hits in the current file.

**Risk:** `low` — docs only; wrong rename could mis-teach who closes the parent, but Stage 1 pins Chuckles finish-up after PR Ready.

## Review

- **Branch:** `origin/sub/AST-909/AST-940-audit-linear`
- **Plan tip:** `fea2a01` (`plan(AST-940)`)
- **team-chuckles:** `origin/main` @ `d456957` — `code(AST-940): audit-linear after-land finish-up wording`
- **Built:** `~/team-chuckles/skills/audit-linear/SKILL.md` — after-land/Done → finish-up; mid-epic audit docs() §7 preserved; astral-radia camping path dropped.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-909/AST-940-audit-linear`; skill deliverable `team-chuckles@d456957` (`skills/audit-linear/SKILL.md`).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–2: §3 after-land → finish-up; “does not …” → finish-up / Chuckles after Susan PR Ready; Who-runs drops `astral-radia` camping; §7 optional mid-epic `docs(<parent-id>): Radia audit` preserved. |
| Grep gate | No live `merge-parent` / Joan / store. Only ban mention of `dev-radia` / `astral-radia`. Live symlink matches. |
| Scope / bible | Astral diff: plan + `docs/test-bible/README.md` docs-only note; no `src/` / pytest. Self-Assessment footprint matches. |
| Rules | §1.1 in-scope; docs under `docs/features/team-chuckles/`; §5a–§5g N/A. |

### Issues

None (**fix-now**).

### Recommended actions

| Severity | Item |
| --- | --- |
| **Advisory** | Linear AC still says repo-wide grep; this child correctly scoped to `audit-linear` only (siblings = other AST-909 rows). |

**Verdict:** Clean — `resolve-child` may proceed (no product/doc fixes required beyond this `docs()` commit).
