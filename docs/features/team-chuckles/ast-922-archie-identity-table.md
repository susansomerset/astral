# AST-922 — Archie identity table + alias sweep

- **Linear:** [AST-922](https://linear.app/astralcareermatch/issue/AST-922/archie-identity-table-alias-sweep-agent-roles-joan-reborn-as-statute)
- **Parent:** [AST-910](https://linear.app/astralcareermatch/issue/AST-910/agent-roles-joan-reborn-as-statute-validator-archie-identity)
- **Publish ref:** `origin/sub/AST-910/AST-922-archie-identity-table`
- **Summary:** Reinstate Archie as the architect role alias: a role→runtime identity table (Archie→Susan first row; extension point for future rows); orientation/session-start resolution; public-facing skills/personas/docs use the alias for architect prose; document that Linear escalations keep `@susan` / assignee Susan so mentions stay functional. Does **not** own Joan persona (AST-919) or Todo-grab (AST-958).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/agents/identity-table.md` | **New** — role→runtime identity table + Linear-mention contract | agents |
| `~/team-chuckles/skills/orientation/SKILL.md` | Session-start: read identity table; resolve Archie→Susan; skill-index note | skill |
| `~/team-chuckles/README.md` | Personas section: point at identity table | docs |
| `~/team-chuckles/agents/chuckles-AGENTS.md` | Architect escalations use Archie in prose; keep `@susan` for Linear | agents |
| `~/team-chuckles/agents/ada-AGENTS.md` | Blocker line: Archie (not bare Susan) for architect escalations | agents |
| `~/team-chuckles/agents/hedy-AGENTS.md` | Same as Ada | agents |
| `~/team-chuckles/agents/katherine-AGENTS.md` | Same as Ada | agents |
| `~/team-chuckles/agents/betty-AGENTS.md` | Same pattern if architect-role Susan prose exists | agents |
| `~/team-chuckles/agents/radia-AGENTS.md` | Same pattern if architect-role Susan prose exists | agents |
| `~/team-chuckles/skills/define-parent/SKILL.md` | Architect prose → Archie; keep Linear assignee Susan / `@susan` | skill |
| `~/team-chuckles/skills/validate-plan/SKILL.md` | Normalize “Susan (Archie)” → Archie + Linear assignee Susan | skill |
| `~/team-chuckles/skills/dispatch-parent/SKILL.md` | Architect / approval-signal prose → Archie; keep Linear assignee ops | skill |
| `~/team-chuckles/skills/do-all-the-things/SKILL.md` | Product/architecture escalate prose → Archie; keep assignee→Susan ops | skill |
| `~/team-chuckles/skills/plan-child/SKILL.md` | “Susan-owned scope” / ask-once architect prose → Archie | skill |
| `~/team-chuckles/skills/qa-child/SKILL.md` | Out-of-scope escalate heading/prose → Archie; keep `@susan` | skill |
| `~/team-chuckles/skills/review-child/SKILL.md` | Plan-gap / exception approval prose → Archie | skill |
| `~/team-chuckles/skills/check-linear/SKILL.md` | Role prose only; **do not** change `assignee → Susan Somerset` API lines | skill |
| `~/team-chuckles/skills/prep-uat/SKILL.md` | UAT actor prose where it means architect handoff → Archie; keep assignee Susan | skill |
| `~/team-chuckles/skills/fix-uat/SKILL.md` | Same dual; keep `assignee Susan` stdout / API strings | skill |
| `~/team-chuckles/skills/finish-up/SKILL.md` | Role prose; keep Linear assignee Susan ops | skill |
| `~/team-chuckles/skills/rollcall/SKILL.md` | Role/queue prose; keep “assignee Susan” as Linear fact | skill |
| `~/team-chuckles/skills/rollcall/WAKE_CHEATSHEET.md` | Same dual | skill |
| `~/team-chuckles/docs/linear-state-consumers.md` | Actor columns: architect = Archie; assignee ops stay Susan | docs |
| `docs/ASTRAL_TEAM_WORKFLOW.md` | Roles table Architect → Archie; CALL SUSAN → CALL ARCHIE (`@susan` body); happy-path actor cells | astral docs |
| `docs/ASTRAL_GIT_WORKFLOW.md` | Permanent-branch / worktree Owner Susan → Archie where owner is architect | astral docs |
| `canon/statutes/AUTHORING.md` | Point Archie section at identity-table path (one cross-link sentence) | statutes |
| `docs/features/team-chuckles/ast-922-archie-identity-table.md` | This plan | astral docs |

**Commit homes:** team-chuckles edits on **`team-chuckles` `main`**; astral law docs + this plan on **`origin/sub/AST-910/AST-922-archie-identity-table`**. Same split as AST-919 / AST-933.

**Out of scope (do not touch):**

- Joan persona / validate-plan actor flip / `joan-AGENTS.md` / `MAX_JOAN_CONTEXT` (**AST-919**).
- Todo-grab assignee Chuckles (**AST-958**).
- Statute id renames (e.g. keep `orch.pipeline.call-susan-for-product-decisions` id).
- Product `src/**`, `tests/**`, bible, historical `docs/features/**` plans outside this file.
- Inventing a Linear user named Archie — there is none; runtime identity stays Susan.
- Host-ops prose that is not a role alias: “Susan’s MacBook”, `susan+*` emails, `LINEAR_KEY_*`, GitHub account docs in `UBUNTU_SETUP.md` / setup scripts (Category C below).
- Blind global `Susan`→`Archie` replace (would break Linear assignee instructions).
- AST-917 residue-purge coordination — sibling is **Canceled**; no double-sweep handoff required.

---

## Binding decisions (planner — do not re-litigate in build)

⚠️ **Decision — Dual contract (public alias vs Linear identity):**

| Surface | Use |
|---------|-----|
| **Public prose** (roles tables, skill narrative, AGENTS domain text, statute authoring) | **Archie** for the architect role |
| **Linear API / mentions** | **`assignee → Susan`** / **`Susan Somerset`**, comments **`@susan`** |
| **Chat with the human operator** in skill imperatives | Prefer **Archie** in repo prose; agents still talk to the human in Cursor — do not invent a second chat persona |

There is **no** Linear account named Archie. Escalations that must ping the architect always use `@susan` and/or assignee Susan. The identity table exists so agents know Archie = Susan at runtime.

⚠️ **Decision — Table location:** `~/team-chuckles/agents/identity-table.md` (installed via `install.sh` `link_tree agents` → `~/.cursor/agents/identity-table.md`). Markdown table, not JSON — agents read it; first row is Archie→Susan; extra rows are allowed later without schema churn. Do **not** seed this file into epic `AGENTS.md` (not a persona).

⚠️ **Decision — Sweep categories (mandatory filter for every edit):**

- **A — Replace:** Architect-role ownership / approval / escalate-to-architect narrative that currently says bare **Susan** (or “Susan (Archie)”) → **Archie**. Roles tables, branch owners, “only Susan can decide product/architecture”, “ask Susan once” when meaning architect approval, “CALL SUSAN” heading.
- **B — Keep:** Any instruction that performs Linear identity work: `assignee → Susan`, `Susan Somerset`, `@susan`, “Susan last commenter”, stdout strings that watchers parse for `assignee Susan`.
- **C — Keep:** Host/ops personal machine and email strings (`Susan’s MacBook`, `susan@…`, `susan+…`).
- **D — Out:** Historical feature plans, test bible, product code.

When a sentence needs both: write **`Archie (Linear: Susan / @susan)`** once, or **`assignee → Susan`** next to architect prose **Archie** — never leave “Susan (Archie)” (old order).

⚠️ **Decision — AUTHORING.md:** Already correct dual wording. Only add a one-line pointer to `~/.cursor/agents/identity-table.md` (or `team-chuckles/agents/identity-table.md`) under the existing **Archie** section — do not rewrite lifecycle tables.

⚠️ **Decision — Skill list is exhaustive for this ticket:** Only the Files Changed table above. If build discovers another **Category A** hit in a skill not listed, **stop and comment** on AST-922 (do not silently expand scope). Engineer AGENTS files not listed (betty/radia) are listed above only for the same one-line blocker pattern — skip the file if no Category A hit.

---

## Stage 1: Identity table + orientation resolution

**Done when:** `agents/identity-table.md` exists with Archie→Susan as row 0; orientation instructs every session to read it and resolve Archie→Susan; README points at it; `./install.sh` leaves `~/.cursor/agents/identity-table.md` reachable (symlink via existing `link_tree agents` — no install.sh logic change unless the link is missing).

1. Create `~/team-chuckles/agents/identity-table.md` with exactly this structure (extend later by appending rows — do not invent extra columns):

```markdown
# Role → runtime identity

Canonical map from **public role alias** → **runtime person**. Agents read this at session start (see orientation § Role alias resolution).

| Alias | Runtime identity | Linear displayName | Linear email | Notes |
|-------|------------------|--------------------|--------------|-------|
| Archie | Susan Somerset | susan | susan@susansomerset.com | Architect. Public prose uses **Archie** only. Linear assignee / `@susan` stay Susan — there is no Linear user “Archie”. |

## Linear mention contract

- **Public-facing repo files** (skills, AGENTS, law docs, statutes): architect role name = **Archie**.
- **Linear escalations and assignee flips** that must reach the architect: use **`@susan`** and/or **`assignee → Susan`** (displayName / email above).
- **Never** invent `@archie` or a Linear assignee named Archie.
- Future roles: append a row; do not fork a second table.
```

2. In `~/team-chuckles/skills/orientation/SKILL.md`, after **Session inputs** (before **Rules**), insert a new section **Role alias resolution**:

   - Read `~/.cursor/agents/identity-table.md` (source: `team-chuckles/agents/identity-table.md`).
   - When skills/docs say **Archie**, runtime person is the **Runtime identity** column (Susan).
   - Linear escalations use `@susan` / assignee Susan per the table’s mention contract.
   - Do not create a Linear user named Archie.

3. In the same orientation file, update **Session inputs** bullets that currently say “Susan’s opener” / “ask Susan once” for architect-operator meaning → **Archie** (Category A). Keep any `@susan` elsewhere in the file (Category B).

4. In `~/team-chuckles/README.md` Personas section, add one row/bullet: identity table path + one-line purpose (Archie→Susan).

5. Run `cd ~/team-chuckles && ./install.sh` (or confirm `test -f ~/.cursor/agents/identity-table.md` after install). No install.sh code change required if `link_tree agents` already covers new files.

## Stage 2: Astral law docs (Roles / owners / CALL)

**Done when:** `docs/ASTRAL_TEAM_WORKFLOW.md` Roles table lists Architect as Archie; CALL section title uses Archie while body keeps `@susan`; `docs/ASTRAL_GIT_WORKFLOW.md` permanent-branch/worktree Owner cells that meant architect Susan say Archie; AUTHORING has the identity-table cross-link. Category B Linear assignee sentences in TEAM_WORKFLOW happy-path that are API facts stay Susan.

1. In `docs/ASTRAL_TEAM_WORKFLOW.md`:
   - Roles table: **Architect** | **Archie** | Notes may say `Linear: Susan / @susan; identity-table`.
   - Rename heading **CALL SUSAN** → **CALL ARCHIE** (statute id `orch.pipeline.call-susan-for-product-decisions` **unchanged**).
   - Body under that heading: keep **`@susan`** as the Linear mention; one sentence that Archie is the public alias (per identity table).
   - Happy-path **Typical actor** cells where Susan means architect/approver → **Archie**; cells that are Linear assignee facts (e.g. prep-uat assigns Susan) stay **Susan**.
2. In `docs/ASTRAL_GIT_WORKFLOW.md`:
   - Permanent branches: `main` Owner **Archie** (was Susan).
   - Worktrees: `<reponame>/` Owner **Chuckles / Archie** (was Chuckles / Susan).
   - Leave commit-vocabulary / finish-up lines that say “after Susan sets PR Ready” as Linear-operator facts **or** rewrite to “after Archie sets PR Ready (Linear: Susan)” — prefer the dual form once per paragraph, not both bare Susan and bare Archie conflicting.
3. In `canon/statutes/AUTHORING.md` **Archie** section: add one sentence pointing at `team-chuckles/agents/identity-table.md` (runtime resolution). Do not change lifecycle tables.

## Stage 3: Personas + skills alias sweep (Category A only)

**Done when:** Every file in the Files Changed table for team-chuckles agents/skills/docs has been walked; Category A hits use Archie; Category B/C lines untouched; verification greps in Stage 4 pass.

1. **Personas** — for each of `chuckles`, `ada`, `hedy`, `katherine`, `betty`, `radia` AGENTS.md:
   - Replace Category A architect-escalation wording (e.g. “requires Susan or Chuckles”) with “requires Archie or Chuckles”.
   - Chuckles: keep `@susan` when blocked on product/architecture (Category B).
   - Skip a file entirely if it has no Category A hit.
2. **Skills listed in Files Changed** — edit only those paths. For each file:
   - Replace Category A prose per Binding Decision.
   - Normalize `Susan (Archie)` → `Archie` in narrative; keep adjacent `assignee → Susan` where it is an API step.
   - `define-parent`: “reassign Susan/Archie” → “reassign Archie (Linear assignee Susan)”; keep `assignee → Susan` / `@susan` open-questions path.
   - `validate-plan`: escalate assignee lines stay `assignee → Susan`; narrative “only Susan (Archie)” → “only Archie”.
   - `check-linear` / `fix-uat` / `prep-uat` / `finish-up` / `rollcall`: **do not** change watcher-parsed stdout or `assignee → Susan Somerset` API strings.
3. **`~/team-chuckles/docs/linear-state-consumers.md`:** actor/exit prose that names the architect → Archie; keep “assignee Susan” where it documents Linear assignee behavior.
4. Do **not** edit skills outside the Files Changed table. Do **not** edit `UBUNTU_SETUP.md` Category C content.

## Stage 4: Verification + publish commits

**Done when:** Greps below are clean for Category A leakage in scoped paths; team-chuckles commit(s) on `main`; astral Stage 2+plan already on publish ref from plan-child / build stages push astral files.

1. From `~/team-chuckles`, run (must return **no** hits that are Category A — allowlisted Category B/C strings are fine). Fail the stage if a hit is architect-role bare Susan without Archie/Linear dual nearby:

```bash
cd ~/team-chuckles
# Architect-role leakage candidates in scoped trees (review each hit)
rg -n '\bSusan\b' agents/*.md skills/orientation skills/define-parent \
  skills/validate-plan skills/dispatch-parent skills/do-all-the-things \
  skills/plan-child skills/qa-child skills/review-child skills/check-linear \
  skills/prep-uat skills/fix-uat skills/finish-up skills/rollcall \
  docs/linear-state-consumers.md README.md
```

   For each hit: classify A/B/C. Category A remaining → fix before commit. Category B/C → leave.

2. From epic worktree, confirm law docs:

```bash
rg -n 'Architect \| Susan|CALL SUSAN|\| `main` \| Susan' docs/ASTRAL_TEAM_WORKFLOW.md docs/ASTRAL_GIT_WORKFLOW.md
# expect empty after Stage 2
```

3. Commit team-chuckles:

```bash
cd ~/team-chuckles
git add agents/identity-table.md agents/*.md skills/orientation/SKILL.md \
  skills/define-parent/SKILL.md skills/validate-plan/SKILL.md \
  skills/dispatch-parent/SKILL.md skills/do-all-the-things/SKILL.md \
  skills/plan-child/SKILL.md skills/qa-child/SKILL.md skills/review-child/SKILL.md \
  skills/check-linear/SKILL.md skills/prep-uat/SKILL.md skills/fix-uat/SKILL.md \
  skills/finish-up/SKILL.md skills/rollcall/SKILL.md skills/rollcall/WAKE_CHEATSHEET.md \
  docs/linear-state-consumers.md README.md
git commit -m "$(cat <<'EOF'
code(AST-922): Archie identity table + public alias sweep

EOF
)"
git push origin HEAD:main
```

   If unrelated local dirty files exist in team-chuckles, **do not** include them — stage only paths from this ticket.

4. On epic worktree (astral), commit law doc edits (Stages 2) separately from the plan commit if build-child owns them:

```bash
# message shape
code(AST-922): Archie alias in TEAM/GIT workflow + AUTHORING pointer
```

   Publish: `git push origin HEAD:sub/AST-910/AST-922-archie-identity-table`.

---

## Self-Assessment

**Scope:** Single-Component — team-chuckles agents/skills/docs identity surface plus two astral law docs and one AUTHORING cross-link; no product `src/`.

**Conf:** high — parent AC and AUTHORING already define the Archie/Susan dual; AST-919 plan shows the team-chuckles vs astral commit-home split; Category A/B/C filter makes the sweep executable without inventing a Linear Archie user.

**Risk:** Medium — a mistaken Category B rewrite (changing `assignee → Susan` or watcher stdout) would break escalations and fix-uat handoff; Stage 4 grep + keep-list mitigate.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §1.1 in-scope only: Files Changed is exhaustive; Joan/Todo-grab/historical plans excluded.
- §1.3 DRY: one identity table; orientation + AUTHORING point at it — no second map.
- §2.1 config: table is team-chuckles agents markdown (not `src/utils/config.py`) — correct home for persona tooling; no product config keys.
- §2.4 / §2.6: N/A (no batch/state machine).
- §3.3 imports: N/A (docs/skills only).
- §3.5 naming: N/A for React; skill/doc paths follow existing team-chuckles layout.
- §3.6: no spike artifacts under `docs/features/`.
- Git: publish astral plan/law to `origin/sub/AST-910/AST-922-archie-identity-table` only; team-chuckles to `origin/main`; never push `origin/dev`.

## Built

**team-chuckles:** `origin/main` @ `3d5d0b622fd7be2727ff5f866f073cd00eb8c39d`
**astral publish ref:** `origin/sub/AST-910/AST-922-archie-identity-table` (this commit)

Stage 1: `agents/identity-table.md` + orientation § Role alias resolution + README row.
Stage 2: TEAM/GIT workflow Architect/owners/CALL ARCHIE + AUTHORING identity-table pointer.
Stage 3: Personas + scoped skills Category A sweep; Category B Linear assignee/`@susan` preserved.
Stage 4: Verification greps + dual-repo publish.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-910/AST-922-archie-identity-table` @ `ab7a772`  
**Live:** `team-chuckles` `main` @ `3d5d0b6`

### What’s solid

- Identity table + Linear mention contract; orientation § Role alias resolution; README row; install exposes `~/.cursor/agents/identity-table.md`.
- Astral Category A: Architect → Archie, CALL ARCHIE, GIT `main`/worktree owners → Archie with Linear Susan dual; AUTHORING pointer only (no statute rewrite).
- Category B preserved (`@susan` / `assignee → Susan`); no `Susan (Archie)` leftovers; betty/radia AGENTS correctly skipped (no Category A hits); no `src/` / pytest; boundaries vs AST-919 / AST-958 held in this tip’s intent.
- Self-Assessment **Single-Component** matches footprint.

### Issues

| Severity | Item |
|----------|------|
| **fix-now** | `~/team-chuckles/skills/orientation/SKILL.md` still has Category A owner cells that Stage 2 already fixed in `docs/ASTRAL_GIT_WORKFLOW.md`: worktree Owner `Chuckles / Susan` (→ `Chuckles / Archie`) and permanent-branch `main \| Susan` (→ `Archie`). File was in scope and edited for § Role alias resolution; Stage 4 required classifying every `\bSusan\b` hit in orientation. |
| **discuss** | `define-parent`: “Backlog is Susan-only intake” vs `linear-state-consumers` “Archie (intake; Linear: Susan)”. Dual-contract form preferred if Backlog ownership is architect-role. |
| **advisory** | Sibling merge: this tip’s `ASTRAL_TEAM_WORKFLOW` still has Plan Ready `Chuckles + Archie`, Plan Discuss `Chuckles (Joan actor)`, Coordinator `review-plan`; AST-919 tip has Joan rows + CALL SUSAN / Architect Susan. `merge-child` must reconcile both alias + Joan ownership — not Joan scope for this ticket, but both touched the same file. |
| **advisory** | `WAKE_CHEATSHEET.md` listed in Files Changed / Stage 4 `git add` but unchanged — remaining Susan hits are Category B (last commenter / assignee facts); OK. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Flip orientation worktree + `main` Owner cells to Archie (mirror GIT workflow) | Engineer (`resolve-child`) on `team-chuckles` `main` + note on publish tip if needed |
| Optional dual wording on define-parent Backlog intake | Engineer if discuss → yes |
| Reconcile TEAM_WORKFLOW at ftr merge (Joan + Archie) | Chuckles `merge-child` |

**ASTRAL_CODE_RULES:** §1.1 / §1.3 satisfied for landed pieces; product layers N/A.
