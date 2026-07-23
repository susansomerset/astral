# AST-920 — Statute schema + authoring guide

- **Linear:** [AST-920](https://linear.app/astralcareermatch/issue/AST-920/statute-schema-authoring-guide-systemic-statutes-law-docs-graduate-to)
- **Parent:** [AST-912](https://linear.app/astralcareermatch/issue/AST-912/systemic-statutes-law-docs-graduate-to-a-statute-harness)
- **Publish ref:** `origin/sub/AST-912/AST-920-statute-schema-authoring-guide`
- **Summary:** Land the statute harness foundation under product `docs/statutes/`: formal field schema, one-file-per-statute format, domain-folder anatomy with orchestration vs astral namespaces, Archie-approved add/amend/retire lifecycle, and a handful of exemplar statutes (including ≥1 `universal` and ≥1 `checkable: hook`). Does **not** harvest the law corpus (AST-921), wire Joan/validate-plan/Radia consumers (AST-910 / AST-916), or invent pattern-catalog entries (AST-913).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/statutes/SCHEMA.md` | New — field definitions, enums, frontmatter contract | docs / statutes |
| `docs/statutes/AUTHORING.md` | New — folder anatomy, id rules, lifecycle (add/amend/retire) with Archie approval | docs / statutes |
| `docs/statutes/README.md` | New — corpus index, how to find `universal` tier, namespace map, pointer to SCHEMA + AUTHORING | docs / statutes |
| `docs/statutes/orchestration/pipeline/orch.pipeline.plan-is-bible.md` | New exemplar — `universal` / `judgment` | docs / statutes |
| `docs/statutes/orchestration/roles/orch.roles.archie-approves-statutes.md` | New exemplar — `universal` / `judgment` | docs / statutes |
| `docs/statutes/astral/layers/astral.layers.import-direction.md` | New exemplar — `scoped` / `judgment` | docs / statutes |
| `docs/statutes/astral/git/astral.git.engineer-test-tree-ban.md` | New exemplar — `scoped` / `hook` | docs / statutes |
| `docs/statutes/astral/batch/astral.batch.batch-id-first.md` | New exemplar — `scoped` / `ci` | docs / statutes |
| `docs/features/team-chuckles/ast-920-statute-schema-authoring-guide.md` | This plan | docs / features |

**Out of scope (do not touch):**

- Harvest / decomposition of `ASTRAL_CODE_RULES.md`, `ASTRAL_GIT_WORKFLOW.md`, `ASTRAL_TEAM_WORKFLOW.md` into the full corpus (**AST-921**).
- Updating law docs to cite statute ids (**AST-921**).
- Joan persona, validate-plan statute loading, Review Rubrics wiring (**AST-910**, **AST-916**, **AST-928**).
- Pattern catalog ids or files (**AST-913** / **AST-925**).
- Any `src/**`, `tests/**`, hooks, CI, or runtime parsers. This ticket is docs-only.

---

## Mechanical rules (binding — implement exactly)

### Layout

```
docs/statutes/
  README.md
  SCHEMA.md
  AUTHORING.md
  orchestration/<domain>/<id>.md    # generic pipeline / team-orchestration statutes
  astral/<domain>/<id>.md           # astral product-specific statutes
```

- **One file per statute.** Filename equals the statute `id` + `.md`.
- **Domains are folders** under a namespace (`orchestration/` or `astral/`). Never flatten statutes as siblings of `SCHEMA.md`. Never create one-file-per-domain monoliths.
- **Reserved top-level names under `docs/statutes/`:** `README.md`, `SCHEMA.md`, `AUTHORING.md`, `orchestration/`, `astral/`. Do not add other top-level entries in this ticket.

⚠️ **Decision:** Two explicit namespaces (`orchestration/` vs `astral/`) rather than “orchestration reserved + astral domains at top level.” Consumers (AST-916) can filter by path prefix; future non-astral products get a sibling namespace without reshuffling astral domains.

### Id format

- Pattern: `{namespace}.{domain}.{slug}`
- `namespace` ∈ {`orch`, `astral`} — short forms map 1:1 to folders `orchestration/` and `astral/`.
- `domain` = folder name under that namespace (lowercase kebab-case: `pipeline`, `roles`, `layers`, `git`, `batch`).
- `slug` = lowercase kebab-case, stable, meaning-bearing (not sequential numbers).
- Id is immutable for the life of the statute. Amend keeps the same id. Retire keeps the file; status becomes `retired`.

⚠️ **Decision:** Dotted semantic ids (not `STAT-0001`). Path and id stay aligned; citations stay readable without a lookup table.

### File format

Every statute file is Markdown with **YAML frontmatter** then body sections in this exact order:

1. Frontmatter (required keys listed in SCHEMA — implement SCHEMA first, then copy the key list into each exemplar).
2. `# Statement` — normative rule text (one statute = one enforceable rule).
3. `## Rationale` — the WHY (retrieval body).
4. `## Examples` with `### Conforming` and `### Violating` (at least one bullet each).
5. Optional `## Notes` — non-normative only.

Do **not** put the statement only in frontmatter. Frontmatter is the machine contract; `# Statement` is the human/agent readable rule.

### Schema fields (frontmatter — lock in SCHEMA.md)

| Key | Type | Allowed values / shape | Required |
|-----|------|------------------------|----------|
| `id` | string | `{orch\|astral}.{domain}.{slug}` matching filename stem | yes |
| `title` | string | short human title | yes |
| `tier` | enum | `universal` \| `scoped` | yes |
| `checkable` | enum | `hook` \| `ci` \| `judgment` | yes |
| `status` | enum | `active` \| `retired` | yes |
| `applies_when` | object | keys below | yes |
| `applies_when.layers` | string[] | empty = no layer filter; else subset of `core`/`data`/`external`/`utils`/`ui`/`scripts`/`docs` | yes (may be `[]`) |
| `applies_when.paths` | string[] | gitignore-style path globs; empty = no path filter | yes (may be `[]`) |
| `applies_when.change_types` | string[] | subset of `add`/`modify`/`delete`/`any`; use `["any"]` when always | yes |
| `source_docs` | string[] | repo-relative paths to narrative law/docs this came from (may be `[]` for harness-native statutes) | yes |
| `supersedes` | string \| null | prior statute id this replaces | yes (`null` if none) |
| `superseded_by` | string \| null | successor id when retired/replaced | yes (`null` if none) |
| `approved_by` | string | always the literal `Archie` for approved statutes | yes |
| `approved_at` | string | ISO date `YYYY-MM-DD` | yes |

Body carries `statement` / rationale / examples — **not** duplicated as frontmatter keys named `statement` or `rationale`.

⚠️ **Decision:** `status` is only `active` \| `retired` (no `draft` in-repo). Drafts live on the author’s branch or Linear until Archie approves; only approved statutes land under `docs/statutes/`.

⚠️ **Decision:** `checkable: hook` means “suitable for a git/pre-commit hook later,” `ci` for CI job later, `judgment` for human/agent review. This ticket does **not** implement hooks or CI — classification only.

### Tier semantics (for README + SCHEMA)

- **`universal`:** consumers that load “the universal set” **must** include every `tier: universal` + `status: active` statute regardless of path/layer filters. Scope fields may still be present for documentation but do not exclude universals from the universal set.
- **`scoped`:** included only when the consumer’s change set matches `applies_when` (exact matching algorithm is **AST-916** — this ticket only labels and documents the fields).

### Archie lifecycle (AUTHORING.md must spell this out)

| Action | Who drafts | Who approves | What lands in git |
|--------|------------|--------------|-------------------|
| **Add** | any engineer / Chuckles | Archie (Susan) | new file, `status: active`, `approved_by: Archie`, `approved_at` set |
| **Amend** | any engineer / Chuckles | Archie | same `id`/path; body and/or frontmatter updated; `approved_at` refreshed; keep `supersedes`/`superseded_by` unless the amend is a replacement retire (below) |
| **Retire** | any engineer / Chuckles | Archie | keep file; set `status: retired`; set `superseded_by` to successor id or `null`; do not delete the file in the same change that retires it |

Public prose in `docs/statutes/**` uses the alias **Archie** only — never Susan’s real name (AST-910 identity rule). Linear assignee flips for approval still target Susan; that procedure text belongs in AUTHORING as “Archie = architect alias; Linear assignee Susan.”

⚠️ **Decision:** Retire is soft-retire (file remains). Hard-delete is out of scope and forbidden in this ticket so citations and history stay resolvable.

### Exemplars (exact set — Stage 2)

Create **exactly these five** files with the frontmatter values below. Body text must be faithful to the cited law/docs but **must not** attempt full harvest of neighboring rules.

#### 1. `docs/statutes/orchestration/pipeline/orch.pipeline.plan-is-bible.md`

```yaml
id: orch.pipeline.plan-is-bible
title: Plan is the bible
tier: universal
checkable: judgment
status: active
applies_when:
  layers: []
  paths: ["docs/features/**"]
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_TEAM_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "<build-date YYYY-MM-DD>"
```

Statement gist: The ticket plan doc is binding for build/test/resolve; agents do not skip, reorder, expand, or improvise steps — ambiguity stops and escalates.

#### 2. `docs/statutes/orchestration/roles/orch.roles.archie-approves-statutes.md`

```yaml
id: orch.roles.archie-approves-statutes
title: Archie approves statute add/amend/retire
tier: universal
checkable: judgment
status: active
applies_when:
  layers: ["docs"]
  paths: ["docs/statutes/**"]
  change_types: ["add", "modify", "delete"]
source_docs: []
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "<build-date YYYY-MM-DD>"
```

Statement gist: No statute under `docs/statutes/` may be added, amended, or retired without Archie approval recorded in frontmatter (`approved_by` / `approved_at`).

#### 3. `docs/statutes/astral/layers/astral.layers.import-direction.md`

```yaml
id: astral.layers.import-direction
title: Layer import direction
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "external", "utils", "ui"]
  paths: ["src/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "<build-date YYYY-MM-DD>"
```

Statement gist: Imports obey CODE_RULES §3.3 one-line-per-layer rules (ui→core+utils; core→data+external+utils; external/data→utils; utils→utils only except the documented logging late-import exception).

#### 4. `docs/statutes/astral/git/astral.git.engineer-test-tree-ban.md`

```yaml
id: astral.git.engineer-test-tree-ban
title: Engineers must not commit test-tree paths
tier: scoped
checkable: hook
status: active
applies_when:
  layers: []
  paths:
    - "tests/**"
    - "docs/test-bible/**"
    - "docs/ASTRAL_TEST_BIBLE.md"
    - "scripts/test_*.py"
    - "scripts/testing/**"
  change_types: ["add", "modify", "delete"]
source_docs:
  - docs/ASTRAL_TEAM_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "<build-date YYYY-MM-DD>"
```

Statement gist: Engineer commits must not add/edit/delete Betty-owned test-tree paths; defective tests go via `[qa-handoff]`. Flagged `checkable: hook` because pre-commit already enforces this class of ban.

#### 5. `docs/statutes/astral/batch/astral.batch.batch-id-first.md`

```yaml
id: astral.batch.batch-id-first
title: Batch claim APIs take batch_id first
tier: scoped
checkable: ci
status: active
applies_when:
  layers: ["data", "core"]
  paths: ["src/data/**", "src/core/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "<build-date YYYY-MM-DD>"
```

Statement gist: Entity batch helpers use claim/get/clear with `batch_id` as the first parameter (CODE_RULES §2.4). Flagged `checkable: ci` as a future signature/lint candidate — not implemented here.

Replace `<build-date YYYY-MM-DD>` with the UTC date of the Stage 2 commit.

---

## Stage 1: Schema + authoring guide + README

**Done when:** `docs/statutes/SCHEMA.md`, `AUTHORING.md`, and `README.md` exist on the publish ref; SCHEMA enumerates every frontmatter key/enum above; AUTHORING documents folder anatomy, id rules, and Archie add/amend/retire; README explains how to list the universal set (`tier: universal` + `status: active`) and the `orchestration/` vs `astral/` split; no statute files yet.

1. Create directory `docs/statutes/` (no other top-level files than the three named below).
2. Write `docs/statutes/SCHEMA.md` containing:
   - Purpose one-liner (machine + human contract for statutes).
   - The field table from **Mechanical rules → Schema fields** (copy values exactly; do not add undeclared keys).
   - Enum definitions for `tier`, `checkable`, `status`.
   - Frontmatter example using a fictional `orch.example.demo` id (label it non-normative / not a real statute).
   - Explicit note: body sections are `# Statement`, `## Rationale`, `## Examples` (`### Conforming` / `### Violating`), optional `## Notes`.
3. Write `docs/statutes/AUTHORING.md` containing:
   - Folder anatomy diagram matching **Mechanical rules → Layout**.
   - Id format rules.
   - One-file-per-statute + domain-folder rules (forbid domain monoliths).
   - Lifecycle tables for add / amend / retire with Archie approval (alias wording).
   - “Drafts are not committed” rule (`status` only `active`|`retired` in-repo).
   - Pointer: full harvest is AST-921; consumers are AST-910 / AST-916 — do not describe their algorithms here beyond tier discovery.
4. Write `docs/statutes/README.md` containing:
   - What this tree is (statute harness corpus).
   - Links to `SCHEMA.md` and `AUTHORING.md`.
   - How consumers find universals: every file under `docs/statutes/**` whose frontmatter has `tier: universal` and `status: active`.
   - Namespace map: `orchestration/` = generic orchestration; `astral/` = astral-specific.
   - Placeholder section `## Exemplars` stating “populated in AST-920 Stage 2” (Stage 2 will replace this with the real list).

**Commit message:** `code(AST-920): statute SCHEMA + AUTHORING + README`

---

## Stage 2: Exemplar statutes + README index

**Done when:** Exactly the five exemplar files listed in **Mechanical rules → Exemplars** exist with valid frontmatter (all required keys), both namespaces present, ≥1 `tier: universal`, ≥1 `checkable: hook`, ≥1 `checkable: ci`, ≥1 `checkable: judgment`, and README `## Exemplars` lists all five with id, tier, checkable, and relative path.

1. Create the five statute files at the exact paths and frontmatter values specified above. Write Statement / Rationale / Examples bodies that match the gist lines; each Examples subsection has ≥1 conforming and ≥1 violating bullet.
2. Replace README `## Exemplars` placeholder with a table:

   | id | tier | checkable | path |
   |----|------|-----------|------|
   | `orch.pipeline.plan-is-bible` | universal | judgment | `orchestration/pipeline/…` |
   | `orch.roles.archie-approves-statutes` | universal | judgment | `orchestration/roles/…` |
   | `astral.layers.import-direction` | scoped | judgment | `astral/layers/…` |
   | `astral.git.engineer-test-tree-ban` | scoped | hook | `astral/git/…` |
   | `astral.batch.batch-id-first` | scoped | ci | `astral/batch/…` |

3. Do **not** add further statutes, domains, or namespaces in this ticket.
4. Do **not** edit `docs/ASTRAL_CODE_RULES.md`, `docs/ASTRAL_GIT_WORKFLOW.md`, or `docs/ASTRAL_TEAM_WORKFLOW.md`.

**Commit message:** `code(AST-920): exemplar statutes (universal + hook)`

---

## Execution contract

- Execute stages in order; one commit per stage on epic worktree; publish each commit to `origin/sub/AST-912/AST-920-statute-schema-authoring-guide`.
- Do not add files, keys, namespaces, or exemplars beyond this plan.
- Ambiguity or drift → stop; comment on **parent** AST-912 with the Stage N blocked template from plan-child.
- No product runtime code. No tests. No hook/CI implementation.

---

## Self-Assessment

**Scope:** `Single-Component` — confined to the new `docs/statutes/` harness tree plus this plan doc; no `src/`, tests, or consumer wiring.

**Conf:** `high` — parent locked storage (`docs/statutes/`), schema fields, one-file-per-statute, namespace split, and exemplar requirements; this plan pins folder/id/frontmatter/lifecycle choices so build-child has no judgment calls.

**Risk:** `Medium` — a wrong schema or namespace shape would force AST-921 harvest rework and slow Joan/rubric consumers (AST-910 / AST-916), but nothing in production runtime executes these files yet.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY / §2.1 config / §2.4 batch / §2.6 state machine / §3.3 imports: N/A to product code — exemplars **cite** those rules as narrative sources only; no runtime duplication.
- §3.6: statutes live under `docs/statutes/` (committed product docs), not `debug/spikes/` or `docs/features/` spike leftovers.
- §4.2: plan lives at `docs/features/team-chuckles/ast-920-….md` per project folder mapping (Team Chuckles → `team-chuckles`).
- No undeclared files; engineer test-tree ban respected (no `tests/` or bible edits).

## Tests (engineer)

**Manifest:** Betty docs-only / no pytest. Items 1–8 on publish tip (`docs/statutes/` layout, SCHEMA/AUTHORING/README, five exemplars, frontmatter, coverage flags, scope gate) — green. No product commits from test-child.

## Review

- **Publish ref:** `origin/sub/AST-912/AST-920-statute-schema-authoring-guide`
- **Build commits:** Stage 1 `code(AST-920): statute SCHEMA + AUTHORING + README`; Stage 2 `code(AST-920): exemplar statutes (universal + hook)`
- **Tip at Code Complete:** 37541d4a00460258daa486d8264cf0b2d40c3712 (Stage 2 exemplars; SCHEMA+AUTHORING at 8657ed2)
