# AST-928 — Plan rubric — validate-plan rewrite with Plan Discuss loop

- **Linear:** [AST-928](https://linear.app/astralcareermatch/issue/AST-928/plan-rubric-validate-plan-rewrite-with-plan-discuss-loop)
- **Parent:** [AST-916](https://linear.app/astralcareermatch/issue/AST-916/review-rubrics-versioned-rubrics-for-plan-test-and-code-review)
- **Publish ref:** `origin/sub/AST-916/AST-928-plan-rubric-validate-plan`
- **Summary:** Land a versioned **plan-rubric** under `canon/rubrics/` and rewrite Joan’s `validate-plan` to execute it: `applies_when` matching against the plan’s Files Changed, per-statute verdicts, mandatory considered-and-excluded, parent-AC ↔ stage traceability, Plan Approved gated on an attached Joan verdict artifact, universal-tier on every plan. Plan Discuss loop mechanics stay as AST-924 (this ticket consumes them). Prove with one live canary including ≥1 Plan Discuss round trip. Does **not** own the code rubric (AST-929) or test rubric (second wave).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/rubrics/README.md` | New — rubric index, revision citation rule, pointer to plan rubric | docs |
| `canon/rubrics/plan/plan-rubric.v1.md` | New — versioned plan rubric Joan executes (matching, verdicts, artifact shape, gates) | docs |
| `canon/statutes/SCHEMA.md` | Amend scoped-tier note: matching algorithm owned by plan-rubric (cite `canon/rubrics/plan/plan-rubric.v1.md`), not bare “AST-916” | docs |
| `canon/statutes/README.md` | One-line pointer under Universal set / consumers → plan-rubric matching | docs |
| `~/team-chuckles/skills/validate-plan/SKILL.md` | Rewrite full-path procedure to execute plan-rubric.v1; keep UAT-thin mode; keep Plan Discuss tags/caps from AST-924; require verdict artifact before Plan Approved | skill (team-chuckles) |
| `~/team-chuckles/agents/joan-AGENTS.md` | Domain: execute plan-rubric; remove “plan-rubric grade vectors out of scope” from Never; cite rubric path + revision | agents (team-chuckles) |
| `docs/ASTRAL_TEAM_WORKFLOW.md` | Plan Ready / Plan Discuss row: Joan runs plan-rubric (cite revision); Plan Approved requires verdict artifact | astral docs |
| `docs/features/team-chuckles/ast-928-plan-rubric-validate-plan.md` | This plan | docs |

**Commit homes:** rubric + statute pointer + workflow + this plan on **`astral-AST-916/`** → `origin/sub/AST-916/AST-928-plan-rubric-validate-plan`. Skill + Joan AGENTS on **`team-chuckles` `main`** (symlink `~/.cursor/skills/validate-plan`).

**Out of scope (do not touch):**

| Ticket / owner | Owns |
|----------------|------|
| AST-929 | Code rubric + Radia full-set sweep |
| Betty second wave | Test rubric |
| AST-924 | Plan Discuss state machine / tags / 2-round cap (already Done — consume only) |
| AST-920 / AST-921 | Statute schema / corpus harvest (already Done — consume only) |
| AST-919 | Joan persona foundation (already Done — thin AGENTS update only) |
| Product `src/**`, `tests/**`, bible | No product / test-tree edits |

**Blocked-by (Done — do not re-implement):** AST-919, AST-920, AST-924.

---

## Binding decisions (planner — do not re-litigate in build)

⚠️ **Decision — Rubric storage:** Versioned rubrics live under product `canon/rubrics/` alongside `canon/statutes/` (parent open question answered yes). Plan rubric path: `canon/rubrics/plan/plan-rubric.v1.md`. Filename embeds revision (`v1`). Frontmatter carries `id`, `revision`, `status`. Future amendments bump to `plan-rubric.v2.md` (do not overwrite v1 history in place for citation integrity).

⚠️ **Decision — Matching algorithm (plan consumer):** Derive the change set **only** from the plan’s **Files Changed** table (not a git diff — Joan has no build tree yet):

1. **Plan layers** = set of Layer column values mapped to statute layer enum (`core`/`data`/`external`/`utils`/`ui`/`scripts`/`docs`). Map free-text layer cells: `docs` / `docs / features` / `astral docs` → `docs`; `skill (team-chuckles)` / `agents (team-chuckles)` / `skill` / `agents` → `docs` (team-chuckles markdown is docs-shaped for matching); `ui` / `core` / `data` / `external` / `utils` / `scripts` keep those names. Unrecognized layer → treat as `docs` and note in artifact Notes.
2. **Plan paths** = File column paths as written (normalize `~/team-chuckles/...` → still match globs that target skill/agent paths by also testing the basename-relative form `skills/**`, `agents/**` when the File path contains `/skills/` or `/agents/`).
3. **Plan change_types** = from Change column: contains `New` / `new` / `Create` → `add`; contains `Amend` / `Update` / `Rewrite` / `rewrite` / `Edit` → `modify`; otherwise `modify`. Always also treat the set as including the literal matches only — do **not** invent `delete` unless Change says delete/remove/retire.
4. For each leaf statute under `canon/statutes/**/*.md` with `status: active` (skip harness: `README.md`, `SCHEMA.md`, `AUTHORING.md`, `HARVEST.md`):
   - **`tier: universal`** → **always considered** (must receive a per-statute verdict). Scope fields do not exclude.
   - **`tier: scoped`** → considered iff **all** of:
     - `applies_when.layers` is `[]` **OR** intersects plan layers
     - `applies_when.paths` is `[]` **OR** any plan path matches any glob (gitignore-style `**` / `*` — Joan may use simple fnmatch/`Path.match` semantics documented in the rubric; empty path list = no path filter)
     - `applies_when.change_types` contains `"any"` **OR** intersects plan change_types
   - Else → **excluded** with a one-line reason naming which predicate failed.
5. Retired statutes are neither considered nor listed in excluded (ignore).

⚠️ **Decision — Per-statute verdict enum:** Exactly three values on considered statutes: `conforms` | `violates` | `needs-discussion`. Mapping to findings: `violates` → severity `fix-now`; `needs-discussion` → `discuss`; `conforms` → no finding row (still listed in Considered).

⚠️ **Decision — Verdict artifact + Plan Approved gate:** Before Joan may move status to **Plan Approved**, she must:

1. Post a Linear comment whose body includes the full **Plan rubric verdict** sections defined in `plan-rubric.v1.md` (tag line first: `[plan-rubric] revision=1`), **and**
2. Attach the same markdown to the ticket via Linear **`create_attachment`** (filename `plan-rubric-verdict-<TICKET>.md`, contentType `text/markdown`, title `Plan rubric verdict (rev 1)`).

If either is missing, do **not** flip to Plan Approved (treat as incomplete pass — post REVISE/discuss or fix the artifact and retry). REVISE / ESCALATE / REPLAN paths still post the partial verdict when scoring ran; attachment required only on APPROVED.

⚠️ **Decision — UAT-thin stays thin:** When UAT-thin mode is active (AST-965), **do not** run full plan-rubric statute scoring or require the plan-rubric attachment. UAT-thin keeps its checklist + `[validate-plan uat-thin]` prefix. Full rubric gate applies to the default (non-UAT-thin) path only.

⚠️ **Decision — Plan Discuss unchanged mechanically:** Enter/exit, tags (`[plan-discuss] round=N concern|reply`, `[plan-discuss] escalate`), 2-round cap, assignee flips remain AST-924 / AST-919. Rubric `violates` / fix-now findings drive REVISE into that loop. Do **not** redesign the state machine.

⚠️ **Decision — Traceability is mandatory fix-now:** Every Acceptance criterion bullet in the **parent** Description must map to ≥1 plan Stage (or an explicit “N/A — boundary” with quote). Every plan Stage must map back to ≥1 parent Purpose / Functional scope / AC bullet. Gaps → `violates` on the rubric’s traceability check (blocks APPROVED).

⚠️ **Decision — Proof canary:** Ticket Done-when requires one real scored plan + ≥1 Plan Discuss round. Use a disposable Team Chuckles canary under parent AST-916 (same pattern as AST-924 / AST-954), not a product child. Document evidence on AST-928.

---

## Stage 1: Versioned plan-rubric artifact + corpus pointers

**Done when:** `canon/rubrics/plan/plan-rubric.v1.md` and `canon/rubrics/README.md` exist on the publish tip; SCHEMA + statutes README point consumers at the matching algorithm in the rubric; no skill rewrite yet.

1. Create directory `canon/rubrics/plan/` (and parent `canon/rubrics/` if missing).
2. Write `canon/rubrics/README.md` with:
   - One paragraph: rubrics consume statutes/patterns; they do not define them.
   - Table of rubrics: `| id | path | executor | status |` with row `plan-rubric.v1` → `canon/rubrics/plan/plan-rubric.v1.md` → Joan / `validate-plan` → `active`.
   - Citation rule: review artifacts must name `plan-rubric.vN` (revision in filename + frontmatter).
   - Note: code rubric = AST-929; test rubric = deferred.
3. Write `canon/rubrics/plan/plan-rubric.v1.md` with this exact structure:

```markdown
---
id: plan-rubric.v1
title: Plan review rubric
revision: 1
status: active
executor: joan / validate-plan
approved_by: Archie
approved_at: "YYYY-MM-DD"
---

# Statement

Joan scores every non-UAT-thin plan against this rubric before Plan Approved.

## Matching algorithm

<paste the Binding Decision matching algorithm verbatim — numbered steps 1–5>

## Checks (grade vectors)

### R1 — Universal set
Every `tier: universal` + `status: active` statute is considered and receives a verdict.

### R2 — Scoped relevance
Scoped active statutes are considered or excluded per Matching algorithm; exclusions have one-line reasons.

### R3 — Per-statute verdict
Each considered statute is scored `conforms` | `violates` | `needs-discussion` against the plan text (Files Changed + Stages + Self-Assessment).

### R4 — Considered and excluded
Verdict artifact lists every considered id with verdict + one-line rationale, and every excluded id with one-line reason. Silent omission is a rubric fail.

### R5 — Requirements traceability
Bidirectional map: parent Acceptance criteria → plan stages; plan stages → parent Purpose / Functional scope / AC. Unmapped AC or orphan stage → `violates`.

### R6 — Definition fidelity + adversarial checklist
Retain the existing validate-plan definition / layer / config / placement / pattern / DRY / self-assessment checklist items as judgment aids under this check (do not delete them from the skill — fold under R6).

### R7 — Artifact + gate
Plan Approved forbidden unless `[plan-rubric] revision=1` comment body + Linear file attachment are present.

## Verdict artifact shape

Required sections (in order) inside the Linear comment / attachment body:

1. First line: `[plan-rubric] revision=1`
2. `**Rubric:** plan-rubric.v1`
3. `**Ticket:** AST-NNN`
4. `**Overall:** APPROVED | REVISE | REPLAN | ESCALATE`
5. `## Traceability` — two tables (AC→stages, stages→definition)
6. `## Statute verdicts` — considered rows: `id | verdict | one-line`
7. `## Considered and excluded` — same section title as today (Considered / Excluded lists)
8. Findings (if any) with fix-now / discuss / acceptable
9. Final line: `context_tokens≈N`

## Plan Discuss

REVISE with any fix-now / R3 `violates` / R5 fail enters or continues the AST-924 Plan Discuss loop. Cap 2; escalate with `[plan-discuss] escalate`.
```

   Set `approved_at` to the build date (ISO `YYYY-MM-DD`). Use Archie in prose.

4. In `canon/statutes/SCHEMA.md`, replace the scoped-tier sentence that says matching is “owned by AST-916” with: matching algorithm for plan validation is defined in `canon/rubrics/plan/plan-rubric.v1.md` (AST-928); code-review matching may be defined by the code rubric (AST-929).
5. In `canon/statutes/README.md` § Universal set, add one sentence pointing plan consumers to `canon/rubrics/plan/plan-rubric.v1.md` for scoped matching.
6. Commit on epic worktree: `code(AST-928): plan-rubric.v1 artifact + statute pointers`. Push `origin/HEAD:sub/AST-916/AST-928-plan-rubric-validate-plan`.

---

## Stage 2: Rewrite validate-plan to execute the rubric

**Done when:** `~/team-chuckles/skills/validate-plan/SKILL.md` full path runs plan-rubric.v1 (matching, R1–R7, artifact+attachment gate); UAT-thin section preserved; Plan Discuss §8 transitions unchanged in meaning; Joan AGENTS updated; team-chuckles committed.

1. In `~/team-chuckles/skills/validate-plan/SKILL.md`:
   - Remove language that says plan-rubric grade vectors / full rubric are out of scope (AST-916 / AST-928).
   - After identity / when-to-run intro, add a short **Plan rubric** pointer: default path executes `canon/rubrics/plan/plan-rubric.v1.md` from the epic worktree (or `git show origin/<publish-ref>:…` / `origin/dev` if needed). Cite revision in every full-path comment.
   - Keep **## UAT-thin mode** intact (AST-965). Add one sentence: UAT-thin does **not** run R1–R7 / does **not** require plan-rubric attachment.
   - Replace §4b “Statute relevance” thin stub with the rubric Matching algorithm (or “follow plan-rubric.v1 § Matching algorithm exactly”).
   - Rewrite §5 so adversarial checks are explicitly **R6**, and add ordered steps for R1–R5 before verdict.
   - Rewrite §6/§7/§8 so **APPROVED** requires R7 (comment + `create_attachment`). Document attachment filename `plan-rubric-verdict-<TICKET>.md`.
   - Keep Plan Discuss comment tags, round counting, assignee flips, REPLAN→Todo, ESCALATE→Susan exactly as current AST-924/919 behavior.
   - Preserve `context_tokens≈N` footer and `— Joan` signature.
2. In `~/team-chuckles/agents/joan-AGENTS.md`:
   - Domain: execute **plan-rubric.v1**; attach verdict artifact; Plan Discuss counterpart.
   - Never-list: **delete** the bullet that bans “plan-rubric grade vectors (AST-916 / AST-928)”. Replace with: do not author/amend rubric files or statutes (engineers/Archie own corpus); do not run code rubric (Radia / AST-929).
3. Run `~/team-chuckles/install.sh` (or the install path that refreshes `~/.cursor/agents/joan-AGENTS.md` + skills symlinks) on the chuckles host so the seeded persona matches.
4. Commit in **team-chuckles**: `code(AST-928): validate-plan executes plan-rubric.v1`. Push `team-chuckles` `main`.
5. Linear comment on AST-928 with team-chuckles commit SHA (substantive — SHA + one-line what changed). No status flip here.

---

## Stage 3: Workflow law touch + astral publish

**Done when:** `docs/ASTRAL_TEAM_WORKFLOW.md` names the plan-rubric gate; Stage 1+3 astral files are on `origin/sub/AST-916/AST-928-plan-rubric-validate-plan`.

1. In `docs/ASTRAL_TEAM_WORKFLOW.md` happy-path table, update the **Plan Ready** and **Plan Discuss** rows so the Joan / `validate-plan` cell states: execute `plan-rubric.v1`; Plan Approved requires Joan’s verdict artifact attachment.
2. Do not change status names or skill entry gates beyond that wording.
3. Commit on epic worktree: `code(AST-928): workflow notes plan-rubric gate`. Push publish ref.

---

## Stage 4: Canary proof (one scored plan + Plan Discuss round trip)

**Done when:** A disposable canary child under AST-916 (or Team Chuckles titled `AST-928 canary — plan-rubric`) has been scored end-to-end with **plan-rubric.v1**, including ≥1 completed Plan Discuss concern/reply round, then APPROVED (or escalate path documented if intentionally testing cap — prefer happy path APPROVED after one revise). Evidence comment on **AST-928** lists canary id, Linear comment links, and confirms attachment present. Zero product children burned.

1. Create Linear canary (Chuckles may create; Ada may request via comment if lacking permission): title `AST-928 canary — plan-rubric`; parent AST-916 if allowed else standalone Team Chuckles; assignee Ada; minimal plan stub path optional (description-only is OK if validate-plan can read a tiny stub committed on this publish ref under `docs/features/team-chuckles/ast-928-canary-stub.md` — if stub needed, add that file in this stage with two stages and one deliberate fix-now-worthy gap for round 1, then patch on reply).
2. Move canary to **Plan Ready**. Chuckles assigns Joan, seeds `joan-AGENTS.md`, spawns validate-plan (full path, not UAT-thin).
3. Expect **REVISE** → **Plan Discuss** with `[plan-discuss] round=1 concern` **and** a `[plan-rubric] revision=1` body (partial artifact OK on REVISE). If Joan APPROVED with no discuss round, **contrive**: Ada adds a deliberate plan defect, return to Plan Ready, re-run — Done-when requires ≥1 discuss round.
4. Engineer posts `[plan-discuss] round=1 reply`, patches stub/plan, Chuckles re-spawns Joan.
5. Joan **APPROVED** → Plan Approved with full verdict comment **and** `plan-rubric-verdict-AST-NNN.md` attachment. Confirm universal statutes all appear under Considered.
6. Comment on **AST-928** with canary id, round-trip evidence, attachment confirmation. Cancel/archive canary afterward.
7. If canary cannot be created (permissions): stop and comment on AST-928 `@susan` — do not mark Stage 4 done.

---

## Execution contract

- Stages in order; one commit home per stage notes above.
- Do not edit AST-929 files, test rubric, or Plan Discuss state vocabulary.
- Do not push `origin/dev`.
- Ambiguity → `🛑 Stage N blocked` on **AST-916** parent (or AST-928 if local), wait.

## Self-Assessment

**Scope:** `Single-Component` — docs/rubric under `canon/rubrics/`, validate-plan + Joan AGENTS in team-chuckles, light workflow/SCHEMA pointers; no product `src/`.

**Conf:** `high` — schema + corpus + Plan Discuss + Joan persona already Done; this ticket fills the matching algorithm and rubric execution hole SCHEMA explicitly reserved for AST-916/928.

**Risk:** `Medium` — a wrong matching rule silently excludes statutes (Radia’s AST-929 full sweep is the backstop); artifact gate mistakes could block Plan Approved pipeline until fixed.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY: rubric owns matching once; skill points at rubric rather than duplicating a second algorithm copy that can drift — skill may quote or “follow rubric § Matching” (prefer single source in rubric file).
- §2.1 / §2.4 / §2.6: N/A — no config, batch, or job state machine changes.
- §3.3 imports / §3.5 placement: N/A for product layers; team-chuckles skills stay in `~/team-chuckles/skills/`; rubrics under `canon/rubrics/` per parent storage decision.
- §3.6 debug spikes: N/A.
- No test-tree edits (Betty owns tests).
)
