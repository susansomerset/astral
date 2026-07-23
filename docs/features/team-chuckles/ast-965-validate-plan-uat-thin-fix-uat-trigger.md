# AST-965 — validate-plan UAT-thin + fix-uat trigger (Deep think UAT issues)

- **Linear:** [AST-965](https://linear.app/astralcareermatch/issue/AST-965/validate-plan-uat-thin-fix-uat-trigger-deep-think-uat-issues)
- **Parent:** [AST-961](https://linear.app/astralcareermatch/issue/AST-961/deep-think-uat-issues)
- **Publish ref:** `origin/sub/AST-961/AST-965-validate-plan-uat-thin-fix-uat-trigger`
- **Summary:** Add Joan **UAT-thin** validate-plan mode (adversarial checklist that the plan restores quoted AC / Correct outcome, not silence of a stacktrace). Wire `fix-uat` so stacktrace-marked bugs run thin validate after Plan Ready before build; non-stacktrace UAT bugs skip validate-plan. Complete token-scope so full epic validate stays banned but thin UAT validate is allowed. Skills/docs only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/validate-plan/SKILL.md` | Add **UAT-thin mode** section (Draft C): activate trigger, skip list, still-do list, checklist, verdicts, `[validate-plan uat-thin]` comment prefix | skill (team-chuckles) |
| `~/team-chuckles/skills/fix-uat/SKILL.md` | Token-scope Exception for thin UAT validate; §5 pipeline order plan → thin validate → build for marked bugs; new thin-validate trigger steps (Draft A4 + D) | skill (team-chuckles) |
| `docs/features/team-chuckles/ast-965-validate-plan-uat-thin-fix-uat-trigger.md` | This plan | docs |

**Exempt / out of scope:**

| Ticket | Owns |
|--------|------|
| AST-963 | Diagnosis gate, Description template, `<!-- uat-validate: stacktrace -->` marker contract |
| AST-964 | `plan-child` **## UAT fitness** section authoring |

**Depends on (build order):** Linear **blockedBy AST-963** — do not ship fix-uat trigger until AST-963’s marker string exists in `fix-uat` §2.5 / Description template. UAT-thin checklist requires **## UAT fitness** (AST-964); if that section is missing at validate time, verdict is **REVISE** (do not invent fitness here).

**Commit homes:** both skill edits in **`team-chuckles`**. Plan doc only on this astral **`origin/sub/AST-961/AST-965-validate-plan-uat-thin-fix-uat-trigger`**. No Astral `src/` / `tests/`. Do not edit `plan-child` in this ticket.

---

## Stage 1: validate-plan UAT-thin mode (Draft C)

**Done when:** `validate-plan/SKILL.md` documents UAT-thin activation, skip/still-do, checklist, verdicts, and comment prefix; full epic path remains the default when UAT-thin is not activated.

1. In `~/team-chuckles/skills/validate-plan/SKILL.md`, after the **When to run / Output / One pass** intro block and **before** **`## Procedure`**, insert a new section:

```markdown
## UAT-thin mode (fix-uat stacktrace-shaped bugs only)

**Activate when:** spawn/prompt says `UAT-THIN VALIDATE` **or** ticket title starts with `UAT:` **and** Description contains `<!-- uat-validate: stacktrace -->`.

**Goal:** adversarial check that the plan restores AC, not that it silences a symptom.

**Skip (do not run in UAT-thin):** full ASTRAL_CODE_RULES read, full parent Purpose re-review beyond quoted AC, layer/config/file-placement deep dive unless the plan touches those layers.

**Still do:**
1. Identity + `get_issue` bug (Plan Ready).
2. Read bug Description: What failed, Expected, Parent AC, Diagnosis, Boundaries.
3. Read plan doc from `origin/<publish-ref>` (same as normal §4) — require **## UAT fitness** present.
4. Checklist only:

**UAT-thin checklist:**
- [ ] Plan cites Parent AC (quoted), not only "remove exception / fix stacktrace"
- [ ] Proposed stages achieve **Correct outcome** / Expected, not merely absence of the symptom
- [ ] **Wrong fix to avoid** from the bug is not what the plan implements
- [ ] No catch-and-ignore / delete-log-path / empty-success / bypass without explicit AC justification in UAT fitness
- [ ] Sibling check addressed (or "none" with reason)
- [ ] Boundaries respected

**Verdicts:** same APPROVED / REVISE / ESCALATE as full validate.
- **REVISE** if fitness missing or plan is symptom-only.
- **ESCALATE** if AC vs product intent is ambiguous (needs Susan).

**Comment prefix:** `[validate-plan uat-thin]` so logs/watchers can tell modes apart.
```

2. Keep the existing full Procedure (§1–§9) unchanged for non-UAT-thin runs. UAT-thin is an alternate path that **replaces** the heavy §3 / deep §5 work with the checklist above when activated — do not require Joan to execute the full adversarial statute pass in UAT-thin.
3. Marker string must stay exactly `<!-- uat-validate: stacktrace -->` (AST-963 contract).

⚠️ **Decision:** Insert UAT-thin as a top-level mode section before Procedure (Draft C placement) rather than a numbered § inside Procedure, so full-path numbering stays stable and Chuckles can point Joan at “UAT-thin mode only.”

---

## Stage 2: fix-uat token-scope Exception (Draft A1 remainder / AC6)

**Done when:** Token-scope **Do not** bans **full** epic `validate-plan` but explicitly allows thin UAT validate when stacktrace-shaped.

1. In `~/team-chuckles/skills/fix-uat/SKILL.md` **## Chuckles token scope**, update the **Do not** cell that mentions validate-plan:

   - **If** it still says bare **`validate-plan`**: replace with the two-bullet intent below.
   - **If** AST-963 already narrowed it to **Full** `validate-plan` epic review without an Exception: **add** the Exception line only.
   - **Target end state** (both bullets must be present):

     - Full `validate-plan` epic review, `audit-linear`, `do-all-the-things`
     - **Exception:** thin **UAT bug validate** (§5.5 below) when the bug is **stacktrace-shaped** (Description contains `<!-- uat-validate: stacktrace -->`)

2. Do not re-open megathread `list_comments` on parent. Do not allow full epic validate-plan.

---

## Stage 3: fix-uat pipeline + thin validate trigger (Draft A4 + D)

**Done when:** Stacktrace-marked bugs run plan → UAT-thin validate → build; non-marked UAT bugs keep plan → build with no validate-plan; REVISE/ESCALATE handling matches Draft A4.

1. In `fix-uat/SKILL.md` **### 5. Per bug — child pipeline**, change the headless chain description so that for each bug:

   - Always: **`plan-child`** first.
   - **If** bug Description contains `<!-- uat-validate: stacktrace -->`: run **UAT-thin validate-plan** (Stage 3 step 2) and **do not** spawn **`build-child`** until verdict **APPROVED**.
   - **Else** (non-stacktrace UAT bugs): **skip** validate-plan; proceed **`build-child`** as today.
   - Then continue **`qa-child` → `test-child` → `review-child` → `resolve-child`** unchanged.
   - **`merge-child`** when bug hits **User Testing** unchanged.

2. Insert new **`### 5.5 Thin validate after Plan Ready (stacktrace-shaped only)`** immediately after §5’s numbered list (before **`### 6. Re-prep when rollup-safe`**) with this procedure:

   After per-bug **`plan-child`** reaches **Plan Ready**, and **only if** the bug Description contains `<!-- uat-validate: stacktrace -->`:

   1. Run **`validate-plan`** in **UAT-thin mode** for that bug id — spawn/prompt must include:  
      `UAT-THIN VALIDATE <bug-id> — follow validate-plan UAT-thin mode only.`
   2. On **REVISE** — engineer re-plans; do **not** spawn **`build-child`** until **APPROVED**.
   3. On **ESCALATE** — `[fix-uat]` on parent `@susan`; clear Active; stop that bug.
   4. Non-stacktrace UAT bugs: **skip** validate-plan (unchanged speed path).

3. Do not change §1–§4 filing/dispatch, §6 re-prep/handoff, Token visibility, Output, or Watcher beyond what Stages 2–3 require.
4. Do not invent new Linear statuses or labels — marker HTML comment is the only detector.

⚠️ **Decision:** Section id **§5.5** (not §6b) so Re-prep stays §6 and token-scope Exception can point at a stable heading. Draft A4’s “§5.5 / §6b” is satisfied by §5.5 owning the thin-validate steps.

---

## Stage 4: Verify and commit (team-chuckles)

**Done when:** Both skills grep clean; commits pushed on team-chuckles; marker / fitness ownership remains with siblings.

1. Grep `validate-plan/SKILL.md` for: `UAT-thin mode`, `UAT-THIN VALIDATE`, `[validate-plan uat-thin]`, `## UAT fitness`, checklist items, `<!-- uat-validate: stacktrace -->`.
2. Grep `fix-uat/SKILL.md` for: `### 5.5`, `UAT-THIN VALIDATE`, Exception + Full validate-plan wording, stacktrace marker gate before build.
3. Confirm no Diagnosis template rewrite and no `plan-child` UAT fitness authoring in this ticket’s diff.
4. **Build gate:** if AST-963 skill changes are not yet on team-chuckles `main` (or the branch this host installs from), stop before claiming Code Complete — comment on AST-965 that blockedBy AST-963 must land first for the marker contract. Planning itself does not wait.
5. Commit in **`team-chuckles`** (two files ok in one commit, or one commit per file — prefer **one** commit):  
   `code(AST-965): UAT-thin validate-plan + fix-uat stacktrace trigger`
6. Push team-chuckles. Symlinks already cover both skills.
7. Append **Review** stub to this plan doc on the astral publish ref after build (build-child §10).

---

## Execution contract

- Stages in order; do not start Stage 2–3 assuming a different marker string than AST-963.
- If validate-plan / fix-uat headings drifted so insertion points are missing, stop and comment on **AST-961** with 🛑 Stage blocked format.
- No product/app code. No full validate-plan on every UAT bug.

---

## Self-Assessment

**Scope:** `Single-Component` — two closely coupled skill files (`validate-plan`, `fix-uat`) plus this plan; process/docs only.

**Conf:** `high` — parent Drafts C / A4 / D are binding; marker contract and fitness section are owned by siblings but referenced by exact strings already planned.

**Risk:** `Medium` — wrong trigger wiring could either skip thin validate on stacktrace bugs or force validate on every UAT bug; mitigated by marker-gated §5.5 and explicit non-stacktrace skip.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 Scope — only the two skills + plan; siblings’ core content not rewritten.
- §4.2 — single plan under `docs/features/team-chuckles/`.
- Product layers N/A. No `tests/` edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-961/AST-965-validate-plan-uat-thin-fix-uat-trigger`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `ea736ac` | Plan doc on astral sub |
| 1–3 | `team-chuckles@4ddc33b` | UAT-thin mode in validate-plan; fix-uat token-scope Exception + §5.5 trigger |

**Built:** `validate-plan` UAT-thin + `fix-uat` §5/§5.5 stacktrace gate; marker contract from AST-963 preserved.
**Tip:** astral plan + stub (this commit); skills on `team-chuckles` `main` @ `4ddc33b`.
