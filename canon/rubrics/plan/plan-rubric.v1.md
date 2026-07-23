---
id: plan-rubric.v1
title: Plan review rubric
revision: 1
status: active
executor: joan / validate-plan
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Joan scores every non-UAT-thin plan against this rubric before Plan Approved.

## Matching algorithm

Derive the change set **only** from the plan’s **Files Changed** table (not a git diff — Joan has no build tree yet):

1. **Plan layers** = set of Layer column values mapped to statute layer enum (`core`/`data`/`external`/`utils`/`ui`/`scripts`/`docs`). Map free-text layer cells: `docs` / `docs / features` / `astral docs` → `docs`; `skill (team-chuckles)` / `agents (team-chuckles)` / `skill` / `agents` → `docs` (team-chuckles markdown is docs-shaped for matching); `ui` / `core` / `data` / `external` / `utils` / `scripts` keep those names. Unrecognized layer → treat as `docs` and note in artifact Notes.
2. **Plan paths** = File column paths as written (normalize `~/team-chuckles/...` → still match globs that target skill/agent paths by also testing the basename-relative form `skills/**`, `agents/**` when the File path contains `/skills/` or `/agents/`).
3. **Plan change_types** = from Change column: contains `New` / `new` / `Create` → `add`; contains `Amend` / `Update` / `Rewrite` / `rewrite` / `Edit` → `modify`; otherwise `modify`. Always also treat the set as including the literal matches only — do **not** invent `delete` unless Change says delete/remove/retire.
4. For each leaf statute under `canon/statutes/**/*.md` with `status: active` (skip harness: `README.md`, `SCHEMA.md`, `AUTHORING.md`, `HARVEST.md`):
   - **`tier: universal`** → **always considered** (must receive a per-statute verdict). Scope fields do not exclude.
   - **`tier: scoped`** → considered iff **all** of:
     - `applies_when.layers` is `[]` **OR** intersects plan layers
     - `applies_when.paths` is `[]` **OR** any plan path matches any glob (gitignore-style `**` / `*` — Joan may use simple fnmatch / `Path.match` semantics; empty path list = no path filter)
     - `applies_when.change_types` contains `"any"` **OR** intersects plan change_types
   - Else → **excluded** with a one-line reason naming which predicate failed.
5. Retired statutes are neither considered nor listed in excluded (ignore).

## Checks (grade vectors)

### R1 — Universal set

Every `tier: universal` + `status: active` statute is considered and receives a verdict.

### R2 — Scoped relevance

Scoped active statutes are considered or excluded per Matching algorithm; exclusions have one-line reasons.

### R3 — Per-statute verdict

Each considered statute is scored `conforms` | `violates` | `needs-discussion` against the plan text (Files Changed + Stages + Self-Assessment).

Mapping to findings: `violates` → severity `fix-now`; `needs-discussion` → `discuss`; `conforms` → no finding row (still listed in Considered).

### R4 — Considered and excluded

Verdict artifact lists every considered id with verdict + one-line rationale, and every excluded id with one-line reason. Silent omission is a rubric fail.

### R5 — Requirements traceability

Bidirectional map: parent Acceptance criteria → plan stages; plan stages → parent Purpose / Functional scope / AC. Unmapped AC or orphan stage → `violates`.

### R6 — Definition fidelity + adversarial checklist

Retain the existing validate-plan definition / layer / config / placement / pattern / DRY / self-assessment checklist items as judgment aids under this check (see `validate-plan` skill §5 / R6).

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
7. `## Considered and excluded` — Considered / Excluded lists
8. Findings (if any) with fix-now / discuss / acceptable
9. Final line: `context_tokens≈N`

## Plan Discuss

REVISE with any fix-now / R3 `violates` / R5 fail enters or continues the AST-924 Plan Discuss loop. Cap 2; escalate with `[plan-discuss] escalate`.

## UAT-thin

UAT-thin mode (AST-965) does **not** run R1–R7 and does **not** require the plan-rubric attachment. Full rubric gate applies to the default (non-UAT-thin) path only.
