# AST-929 — Code rubric — Radia full-statute straggler sweep

- **Linear:** [AST-929](https://linear.app/astralcareermatch/issue/AST-929/code-rubric-radia-full-statute-straggler-sweep)
- **Parent:** [AST-916](https://linear.app/astralcareermatch/issue/AST-916/review-rubrics-versioned-rubrics-for-plan-test-and-code-review)
- **Publish ref:** `origin/sub/AST-916/AST-929-code-rubric-radia-sweep`
- **Summary:** Land a versioned **code-rubric** under `canon/rubrics/code/` and rewrite Radia’s `review-child` to execute it: **full-set statute sweep** (every active `universal` + every active `scoped` statute appears on a checked-list — belt-and-suspenders against plan-time exclusion), pattern conformance for cited pattern ids, plan adherence (built what was approved, no silent scope drift), review artifact that records statutes checked (findings-only is incomplete), findings still routed fix-now / discuss / advisory with **no** new fix authority. Prove with one real review whose artifact demonstrates the full checked-list. Does **not** own the plan rubric (AST-928) or test rubric (Betty second wave).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/rubrics/README.md` | Create if missing, else amend — add `code-rubric.v1` row; keep plan-rubric row/pointer if AST-928 already wrote it | docs |
| `canon/rubrics/code/code-rubric.v1.md` | New — versioned code rubric Radia executes (full-set sweep, checks, artifact shape, gates) | docs |
| `canon/statutes/SCHEMA.md` | Amend scoped-tier / matching note: code-review full-set sweep owned by `canon/rubrics/code/code-rubric.v1.md` (AST-929); do not undo AST-928 plan-rubric pointer if present | docs |
| `canon/statutes/README.md` | One sentence under Universal set / consumers: code review loads full active set per code-rubric.v1 | docs |
| `~/team-chuckles/skills/review-child/SKILL.md` | Rewrite §5 (and artifact/comment §6–§7) to execute code-rubric.v1; preserve worktree/publish/git rules from AST-935; fold existing §5a–§5g tables under rubric checks as judgment aids | skill (team-chuckles) |
| `~/team-chuckles/agents/radia-AGENTS.md` | Domain: execute code-rubric.v1; cite rubric path + revision; never grant product-fix authority | agents (team-chuckles) |
| `docs/ASTRAL_TEAM_WORKFLOW.md` | Tests Passed / Review Posted row: Radia runs code-rubric (cite revision); incomplete without statutes-checked artifact | astral docs |
| `docs/features/team-chuckles/ast-929-code-rubric-radia-sweep.md` | This plan | docs |

**Commit homes:** rubric + statute pointers + workflow + this plan on **`astral-AST-916/`** → `origin/sub/AST-916/AST-929-code-rubric-radia-sweep`. Skill + Radia AGENTS on **`team-chuckles` `main`** (symlink `~/.cursor/skills/review-child`).

**Out of scope (do not touch):**

| Ticket / owner | Owns |
|----------------|------|
| AST-928 | Plan rubric + validate-plan rewrite + Joan AGENTS |
| Betty second wave | Test rubric |
| AST-920 / AST-921 | Statute schema / corpus harvest (Done — consume only) |
| AST-913 / AST-925 | Pattern catalog files (do not invent) |
| Product `src/**`, `tests/**`, bible | No product / test-tree edits |

**Blocked-by (Done — do not re-implement):** AST-921.

---

## Binding decisions (planner — do not re-litigate in build)

⚠️ **Decision — Rubric storage:** Versioned rubrics live under product `canon/rubrics/` alongside `canon/statutes/` (parent open question answered yes; same home as AST-928). Code rubric path: `canon/rubrics/code/code-rubric.v1.md`. Filename embeds revision (`v1`). Frontmatter carries `id`, `revision`, `status`. Future amendments bump to `code-rubric.v2.md` (do not overwrite v1 in place).

⚠️ **Decision — Full-set sweep (the point of this ticket):** Radia does **not** use Joan’s considered-and-excluded list as the statute set. For every leaf file under `canon/statutes/**/*.md` with `status: active` (skip harness: `README.md`, `SCHEMA.md`, `AUTHORING.md`, `HARVEST.md`):

1. Derive the **diff change set** from `git diff origin/dev...origin/<publish-ref>` (fallback paths already in review-child §4):
   - **Diff paths** = changed file paths in the three-dot diff.
   - **Diff layers** = map each path: `src/core/**`→`core`, `src/data/**`→`data`, `src/external/**`→`external`, `src/utils/**`→`utils`, `src/ui/**`→`ui`, `scripts/**`→`scripts`, everything else under `docs/` / `canon/` / `~/team-chuckles` / skills / agents → `docs`.
   - **Diff change_types** = `add` if status is new file / `A`, `delete` if deleted / `D`, else `modify`.
2. For **each** active statute, append one row to **`## Statutes checked`** (mandatory — empty findings with no checked-list = incomplete review; do **not** set Review Posted).
3. Score the row:
   - **`tier: universal`** → always score `conforms` | `violates` | `needs-discussion` against the diff + plan (never `not-applicable`).
   - **`tier: scoped`** → if `applies_when` matches the diff change set (same layer/path/change_type intersection rules as AST-928 plan-rubric Binding Decision steps 4’s scoped predicate, applied to **diff** layers/paths/change_types instead of plan Files Changed) → score `conforms` | `violates` | `needs-discussion`.
   - **`tier: scoped`** and predicate does **not** match → verdict **`not-applicable`** with one-line reason naming which predicate failed. Still listed. This is how “full set” is proven without pretending every statute applies to a docs-only diff.
4. Retired statutes: ignore (neither checked nor listed).
5. **Straggler callout (belt-and-suspenders):** If the ticket’s plan-rubric / Joan verdict attachment is present and lists a statute under Excluded, **and** this sweep scores that same id as anything other than `not-applicable`, add a **discuss** finding: `straggler — excluded at plan time but in-scope on diff` (or fix-now if also `violates`). Absence of a Joan artifact is not a block — note `no plan-rubric verdict attached` under Notes and continue.

⚠️ **Decision — Verdict enum:** Exactly four values on checked statutes: `conforms` | `violates` | `needs-discussion` | `not-applicable`. Mapping to findings: `violates` → severity `fix-now`; `needs-discussion` → `discuss`; `conforms` / `not-applicable` → no finding row (still listed in Statutes checked). Advisory grandfather notes remain advisory (not a fourth severity).

⚠️ **Decision — Pattern conformance without AST-913 catalog:** Do **not** invent `canon/patterns/`. Pattern check = (a) every active `astral.patterns.*` statute is already in the full-set sweep; (b) any pattern id / `Pattern:` citation in the combined plan or Linear description must be named under `## Pattern conformance` with conforms/violates/needs-discussion/not-cited. If none cited → one line `none cited`. When AST-913 lands later, a future rubric revision may expand this check — out of scope here.

⚠️ **Decision — Plan adherence:** Keep existing review-child plan-fidelity / Self-Assessment / cross-ticket boundary lenses. Failures → fix-now (silent scope smuggle, missing planned file that was claimed Done) or discuss (Self-Assessment Scope mismatch). Do not invent new fix authority for Radia.

⚠️ **Decision — Findings routing unchanged:** fix-now / discuss / advisory only. Radia still never edits `src/` or `tests/`. Doc-only mid-pipeline `docs()` on publish ref stays as today (AST-935).

⚠️ **Decision — Incomplete review gate:** Before Radia may move status to **Review Posted**, the Linear comment **must** include:

1. First line tag `[code-rubric] revision=1`
2. Full **Code rubric verdict** sections defined in `code-rubric.v1.md`, including `## Statutes checked` with **one row per active statute** (count must equal active corpus count at review time — currently 56 per `canon/statutes/README.md`; verify with a quick count of `status: active` frontmatter files, do not hardcode 56 forever).
3. Rubric citation: `**Rubric:** code-rubric.v1`

If the checked-list is missing, truncated, or findings-only: **do not** set Review Posted — comment the incomplete artifact and leave status at Tests Passed (or stay without flipping).

⚠️ **Decision — README coexistence with AST-928:** Both children may create/amend `canon/rubrics/README.md`. On this ticket:

- If README missing → create it with code-rubric row **and** a plan-rubric row pointing at `canon/rubrics/plan/plan-rubric.v1.md` / AST-928 (status `active` if file exists on tree after merge, else `pending AST-928`).
- If README already exists (AST-928 landed via ftr merge) → **only** add/update the `code-rubric.v1` row; do not rewrite plan-rubric content or Ada’s citation rule.

⚠️ **Decision — SCHEMA coexistence:** If AST-928 already replaced the “owned by AST-916” sentence with a plan-rubric pointer, append (do not replace) a clause that code-review full-set sweep is defined in `canon/rubrics/code/code-rubric.v1.md`. If the AST-916 placeholder remains, replace it with both plan (AST-928) and code (AST-929) pointers in one sentence.

⚠️ **Decision — Proof canary:** Done-when requires one real review executed against the rubric with full-set sweep in the artifact. Use a disposable Team Chuckles canary (same pattern as AST-928 Stage 4), not a product child. Evidence comment on AST-929. Cancel/archive canary afterward.

---

## Stage 1: Versioned code-rubric artifact + corpus pointers

**Done when:** `canon/rubrics/code/code-rubric.v1.md` exists on the publish tip; `canon/rubrics/README.md` lists `code-rubric.v1`; SCHEMA + statutes README point code-review consumers at the full-set sweep; no skill rewrite yet.

1. Create directory `canon/rubrics/code/` (and parent `canon/rubrics/` if missing).
2. Write or amend `canon/rubrics/README.md`:
   - One paragraph: rubrics consume statutes/patterns; they do not define them.
   - Table: `| id | path | executor | status |` including row `code-rubric.v1` → `canon/rubrics/code/code-rubric.v1.md` → Radia / `review-child` → `active`.
   - Citation rule: review artifacts must name `code-rubric.vN` (revision in filename + frontmatter).
   - Preserve or stub plan-rubric row per Binding Decision README coexistence.
   - Note: test rubric = deferred second wave.
3. Write `canon/rubrics/code/code-rubric.v1.md` with this exact structure:

```markdown
---
id: code-rubric.v1
title: Code review rubric
revision: 1
status: active
executor: radia / review-child
approved_by: Archie
approved_at: "YYYY-MM-DD"
---

# Statement

Radia scores every Tests Passed child against this rubric before Review Posted.

## Full-set sweep algorithm

<paste Binding Decision — Full-set sweep steps 1–5 verbatim>

## Checks (grade vectors)

### C1 — Full active set on checked-list
Every `status: active` statute (universal + scoped) appears in `## Statutes checked`. Missing rows → incomplete review (no Review Posted).

### C2 — Universal scoring
Every `tier: universal` + `status: active` statute receives `conforms` | `violates` | `needs-discussion` (never `not-applicable`).

### C3 — Scoped relevance vs diff
Scoped active statutes are scored or marked `not-applicable` per Full-set sweep algorithm; `not-applicable` rows still carry a one-line reason.

### C4 — Straggler vs plan exclusion
When a Joan plan-rubric verdict is attached, any statute Joan excluded that this sweep scores as in-scope gets a discuss (or fix-now if violates) straggler finding.

### C5 — Pattern conformance
Cited pattern ids (plan / description) listed under `## Pattern conformance`; `astral.patterns.*` covered via C1–C3. No invented pattern catalog.

### C6 — Plan adherence + prior review lenses
Plan fidelity, Self-Assessment Scope match, cross-ticket boundaries, and the existing review-child §5a–§5g judgment tables (imports, layers, silent failure, fallbacks, logging, config/state in UI, batch/transitions, debug contract, external cleanliness) fold under this check as judgment aids — keep the tables in the skill under C6; do not delete them.

### C7 — Artifact + gate
Review Posted forbidden unless Linear comment starts with `[code-rubric] revision=1` and includes complete `## Statutes checked`.

## Verdict artifact shape

Required sections (in order) inside the Linear comment (and optional mid-pipeline docs() appendix on the plan file):

1. First line: `[code-rubric] revision=1`
2. `**Rubric:** code-rubric.v1`
3. `**Ticket:** AST-NNN`
4. `**Publish ref:** <publish-ref tip SHA>`
5. `**Overall:** CLEAN | FIX-NOW | DISCUSS` (FIX-NOW if any fix-now findings; else DISCUSS if any discuss; else CLEAN)
6. `## Statutes checked` — table: `id | tier | verdict | one-line` — **one row per active statute**
7. `## Pattern conformance` — cited ids or `none cited`
8. `## Plan adherence` — one short paragraph or bullets
9. Findings (if any) with fix-now / discuss / advisory + locations
10. Optional: What’s solid / Recommended actions (existing docs() shape)
11. Final line: `context_tokens≈N`

## Fix authority

Findings route fix-now / discuss / advisory only. Radia does not edit product or test-tree code.
```

   Set `approved_at` to the build date (ISO `YYYY-MM-DD`).

4. Amend `canon/statutes/SCHEMA.md` per Binding Decision SCHEMA coexistence (plan + code pointers; no field/enum changes).
5. Amend `canon/statutes/README.md` § Universal set: one sentence that code-review consumers load the **full** active set (universal + scoped) per `canon/rubrics/code/code-rubric.v1.md`, and that scoped `not-applicable` rows still appear on the checked-list.
6. Commit on epic worktree: `code(AST-929): code-rubric.v1 artifact + statute pointers`. Push `git push origin HEAD:sub/AST-916/AST-929-code-rubric-radia-sweep`.

---

## Stage 2: Rewrite review-child to execute the rubric

**Done when:** `~/team-chuckles/skills/review-child/SKILL.md` full path runs code-rubric.v1 (full-set sweep, C1–C7, incomplete-review gate); Radia AGENTS updated; team-chuckles committed and pushed; `~/team-chuckles/install.sh` run on the chuckles host so seeded persona/skills match.

1. In `~/team-chuckles/skills/review-child/SKILL.md`:
   - After identity / when-to-run intro, add a short **Code rubric** pointer: default path executes `canon/rubrics/code/code-rubric.v1.md` from the epic worktree (or `git show origin/<publish-ref>:…` / `origin/dev` if needed). Cite revision in every review comment.
   - Replace §5 “Perform the review” framing so the three lenses become **C6 judgment aids** under the rubric; the mandatory procedure is C1–C7.
   - Keep §4 baseline/ref resolution, §5f debug contract table, §5g external cleanliness table — move or clearly label them as **C6 aids** (do not drop the concrete check rows).
   - Add an explicit step: enumerate all active statute ids (read frontmatter under `canon/statutes/`), build `## Statutes checked`, then score. Document that a findings-only comment without the checked-list is incomplete.
   - Rewrite §7 so **Review Posted** requires C7 (tag + complete checked-list). If incomplete: comment only; leave Tests Passed.
   - Preserve: no assignee change; no product edits; mid-pipeline `docs()` publish via `git push origin HEAD:<publish-ref>`; epic worktree path rules from AST-935; `[review-handoff]` discuss loop behavior.
2. In `~/team-chuckles/agents/radia-AGENTS.md`:
   - Domain: execute **code-rubric.v1**; full-set sweep; cite revision in comments/docs.
   - Standards: statutes checked required; findings still fix-now/discuss/advisory only; never edit `src/` or `tests/`.
   - Trigger line may still say Tests Passed → review-child → Review Posted (assignee stays implementer; Radia queue is status-based).
3. Run `~/team-chuckles/install.sh` on the chuckles host.
4. Commit in **team-chuckles**: `code(AST-929): review-child executes code-rubric.v1`. Push `team-chuckles` `main`.
5. Linear comment on AST-929 with team-chuckles commit SHA (substantive — SHA + one-line what changed). No status flip here.

---

## Stage 3: Workflow law touch + astral publish

**Done when:** `docs/ASTRAL_TEAM_WORKFLOW.md` names the code-rubric gate on the Tests Passed → Review Posted path; Stage 1+3 astral files are on `origin/sub/AST-916/AST-929-code-rubric-radia-sweep`.

1. In `docs/ASTRAL_TEAM_WORKFLOW.md` happy-path table, update the **Tests Passed** row so the Radia / `review-child` cell states: execute `code-rubric.v1`; Review Posted requires statutes-checked artifact (`[code-rubric] revision=1`).
2. Do not change status names, assignee rules, or skill entry gates beyond that wording.
3. Commit on epic worktree: `code(AST-929): workflow notes code-rubric gate`. Push publish ref.

---

## Stage 4: Canary proof (one real review + full checked-list)

**Done when:** A disposable canary child under AST-916 (or Team Chuckles titled `AST-929 canary — code-rubric`) has been reviewed end-to-end with **code-rubric.v1**, the Linear comment includes `[code-rubric] revision=1` and a complete `## Statutes checked` table (row count = active statute count), and evidence is commented on **AST-929**. Zero product children burned.

1. Create Linear canary (Chuckles may create; Hedy may request via comment if lacking permission): title `AST-929 canary — code-rubric`; parent AST-916 if allowed else standalone Team Chuckles; assignee Hedy (or Radia for review stage); minimal doc-only tip on this publish ref under `docs/features/team-chuckles/ast-929-canary-stub.md` (two paragraphs, no `src/` — enough for a three-dot diff vs `origin/dev`).
2. Move canary through to **Tests Passed** (Betty may no-op / empty manifest with Chuckles help, or Chuckles sets Tests Passed for a docs-only canary — if process blocks, comment `@susan` / Chuckles for a one-shot canary status — do not invent a new pipeline). Prefer: docs-only stub + Chuckles moves canary to Tests Passed for rubric proof only.
3. Chuckles seeds `radia-AGENTS.md`, spawns `review-child` (or Radia runs queue) on the canary.
4. Confirm Linear comment on canary: tag `[code-rubric] revision=1`, `## Statutes checked` complete, Overall CLEAN or findings as earned. Confirm Review Posted only if C7 satisfied.
5. Comment on **AST-929** with canary id, comment link, active-statute row count observed, and confirmation that findings-only would have been rejected.
6. Cancel/archive canary afterward; leave stub file on publish ref or delete in a follow-up commit on this tip (either OK — note which in the evidence comment).
7. If canary cannot be created or Radia cannot be spawned (permissions): stop and comment on AST-929 `@susan` — do not mark Stage 4 done.

---

## Execution contract

- Stages in order; one commit home per stage notes above.
- Do not edit AST-928 plan-rubric body, validate-plan, Joan AGENTS, test rubric, or invent pattern catalog.
- Do not push `origin/dev`.
- Ambiguity → `🛑 Stage N blocked` on **AST-916** parent (or AST-929 if local), wait.

## Self-Assessment

**Scope:** `Single-Component` — docs/rubric under `canon/rubrics/code/`, review-child + Radia AGENTS in team-chuckles, light workflow/SCHEMA pointers; no product `src/`.

**Conf:** `high` — statute corpus (AST-921) Done; AST-928 already locked rubric storage + frontmatter shape + verdict vocabulary; this ticket’s distinct algorithm (full-set + not-applicable + straggler) is specified above without depending on Joan’s matcher.

**Risk:** `Medium` — a truncated checked-list would fake “reviewed”; incomplete-review gate and row-count check mitigate. Wrong `not-applicable` rules could hide a real scoped violation — full listing still makes silent omission visible in audit.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY: full-set algorithm lives once in `code-rubric.v1.md`; skill points at / quotes it rather than maintaining a second divergent copy.
- §2.1 / §2.4 / §2.6: N/A — no config, batch, or job state machine changes.
- §3.3 imports / §3.5 placement: N/A for product layers; team-chuckles skills stay in `~/team-chuckles/skills/`; rubrics under `canon/rubrics/` per parent storage decision.
- §3.6 debug spikes: N/A.
- No test-tree edits (Betty owns tests).
- Engineer test-tree ban / Radia no-src: preserved explicitly in Binding Decisions and Stage 2.


## Built

| Stage | Commit | Note |
|-------|--------|------|
| 1 | `b885312` | code-rubric.v1 + statute pointers |
| 2 | team-chuckles `7ec2c9e` | review-child + Radia AGENTS |
| 3 | `5ae8e01` | workflow code-rubric gate |
| 4 canary stub | `712aff5` | ast-929-canary-stub.md |
| Publish tip | `712aff5` | origin/sub/AST-916/AST-929-code-rubric-radia-sweep |

## Stage 4 canary evidence

- Canary: AST-968
- Verdict: `[code-rubric] revision=1` on AST-968 with 56-row Statutes checked (CLEAN)
- Stub left on publish tip
