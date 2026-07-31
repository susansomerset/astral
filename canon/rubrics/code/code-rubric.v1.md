---
id: code-rubric.v1
title: Code review rubric
revision: 1
status: active
executor: radia / review-child
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Radia scores every Tests Passed child against this rubric before Review Posted.

## Full-set sweep algorithm

Radia does **not** use Joan’s considered-and-excluded list as the statute set. For every leaf file under `canon/statutes/**/*.md` with `status: active` (skip harness: `README.md`, `SCHEMA.md`, `AUTHORING.md`, `HARVEST.md`):

1. Derive the **diff change set** from `git diff origin/dev...origin/<publish-ref>` (fallback paths already in review-child §4):
   - **Diff paths** = changed file paths in the three-dot diff.
   - **Diff layers** = map each path: `src/core/**`→`core`, `src/data/**`→`data`, `src/external/**`→`external`, `src/utils/**`→`utils`, `src/ui/**`→`ui`, `scripts/**`→`scripts`, everything else under `docs/` / `canon/` / `~/team-chuckles` / skills / agents → `docs`.
   - **Diff change_types** = `add` if status is new file / `A`, `delete` if deleted / `D`, else `modify`.
2. For **each** active statute, append one row to **`## Statutes checked`** (mandatory — empty findings with no checked-list = incomplete review; do **not** set Review Posted).
3. Score the row:
   - **`tier: universal`** → always score `conforms` | `violates` | `needs-discussion` against the diff + plan (never `not-applicable`).
   - **`tier: scoped`** → if `applies_when` matches the diff change set → score `conforms` | `violates` | `needs-discussion`.
   - **`tier: scoped`** and predicate does **not** match → verdict **`not-applicable`** with one-line reason naming which predicate failed. Still listed. This is how “full set” is proven without pretending every statute applies to a docs-only diff.
4. Retired statutes: ignore (neither checked nor listed).
5. **Straggler callout (belt-and-suspenders):** If the ticket’s plan-rubric / Joan verdict attachment is present and lists a statute under Excluded, **and** this sweep scores that same id as anything other than `not-applicable`, add a **discuss** finding: `straggler — excluded at plan time but in-scope on diff` (or fix-now if also `violates`). Absence of a Joan artifact is not a block — note `no plan-rubric verdict attached` under Notes and continue.

**Scoped `applies_when` predicate** (prefer the shared wording in `canon/rubrics/plan/plan-rubric.v1.md` § Matching algorithm step 4 when that file is on the review tree; otherwise use this copy applied to **diff** layers/paths/change_types instead of plan Files Changed). Scoped matches iff **all** of:

- `applies_when.layers` is `[]` **OR** intersects diff layers
- `applies_when.paths` is `[]` **OR** any diff path matches any glob (gitignore-style `**` / `*` — simple fnmatch / `Path.match` semantics; empty path list = no path filter)
- `applies_when.change_types` contains `"any"` **OR** intersects diff change_types

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

Required sections (in order) inside the Linear comment (and optional mid-pipeline docs() append on the plan file):

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
