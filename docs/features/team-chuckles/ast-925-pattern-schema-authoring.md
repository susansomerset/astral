# AST-925 — Pattern schema + authoring / lifecycle

- **Linear:** [AST-925](https://linear.app/astralcareermatch/issue/AST-925/pattern-schema-authoring-lifecycle-pattern-libraries-citable-reusable)
- **Parent:** [AST-913](https://linear.app/astralcareermatch/issue/AST-913/pattern-libraries-citable-reusable-logic-catalog)
- **Publish ref:** `origin/sub/AST-913/AST-925-pattern-schema-authoring`
- **Summary:** Land the pattern-catalog foundation under product `canon/patterns/`: formal field schema, one-file-per-pattern format, domain-folder anatomy, propose → Archie approve → amend/retire lifecycle, and exactly one exemplar entry that records a proposed→approved cycle. Does **not** harvest the full recurring-shape set (AST-969), redefine statute schema/layout (AST-912 / AST-920), or wire consuming procedures (AST-914 / review rubrics).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/patterns/SCHEMA.md` | New — field definitions, enums, frontmatter + body contract | docs / patterns |
| `canon/patterns/AUTHORING.md` | New — folder anatomy, id rules, lifecycle (propose/approve/amend/retire) with Archie approval | docs / patterns |
| `canon/patterns/README.md` | New — corpus index, how to find `approved` patterns, domain map, pointer to SCHEMA + AUTHORING | docs / patterns |
| `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` | New exemplar — `status: approved` with lineage (`proposed_in` + `approved_by`) | docs / patterns |
| `docs/features/team-chuckles/ast-925-pattern-schema-authoring.md` | This plan | docs / features |

**Out of scope (do not touch):**

- Full harvest of recurring astral change shapes into many pattern files (**AST-969**).
- Statute schema, AUTHORING, or corpus under `canon/statutes/**` (**AST-912** / **AST-920** / **AST-921**).
- define-parent citation wiring, Joan/validate-plan, Review Rubrics consumers (**AST-914**, **AST-910**, **AST-916**).
- Any `src/**`, `tests/**`, hooks, CI, or runtime parsers. This ticket is docs-only under `canon/patterns/` (+ this plan).

---

## Mechanical rules (binding — implement exactly)

### Layout

```
canon/patterns/
  README.md
  SCHEMA.md
  AUTHORING.md
  <domain>/<id>.md
```

- **One file per pattern.** Filename equals the pattern `id` + `.md`.
- **Domains are folders** directly under `canon/patterns/` (lowercase kebab-case). Never flatten patterns as siblings of `SCHEMA.md`. Never create one-file-per-domain monoliths.
- **Reserved top-level names under `canon/patterns/`:** `README.md`, `SCHEMA.md`, `AUTHORING.md`, plus domain folders. Do not invent other top-level filenames without Archie approval and a schema/authoring update. Do **not** add `HARVEST.md` in this ticket (harvest crosswalk is AST-969).
- **No `orchestration/` vs `astral/` namespace split** under patterns — patterns are affirmative product/method packages; domain folders alone group them. Statutes keep their two namespaces; patterns do not mirror that split.

⚠️ **Decision:** Single-level `canon/patterns/<domain>/` (no `orchestration/` / `astral/` under patterns). Parent locked `canon/patterns/<domain>/`; statute namespaces solve a different problem (generic pipeline law vs product law). Pattern domains stay flat so AST-969 can add `batch/`, `state/`, `config/`, `layers/`, `ui/` without a second layout migration.

### Id format

- Pattern: `pattern.{domain}.{slug}`
- `domain` = folder name under `canon/patterns/` (lowercase kebab-case).
- `slug` = lowercase kebab-case, stable, meaning-bearing (not sequential numbers).
- **Id is immutable** for the life of the pattern. Amend keeps the same id. Retire keeps the file; `status` becomes `retired`.

Path and id stay aligned: `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` ↔ id `pattern.batch.entity-claim-process-release`.

⚠️ **Decision:** Three-segment dotted ids (`pattern.{domain}.{slug}`), not the informal two-segment example `pattern.entity-batch-processing` from the parent brief. Mirrors statute id↔path alignment (`astral.batch.*` style) so citations encode domain without a lookup table. Parent example was shorthand for the batch claim/process/release package.

### File format

Every pattern file is Markdown with **YAML frontmatter** then body sections in this exact order:

1. Frontmatter (required keys listed in SCHEMA — implement SCHEMA first, then copy the key list into the exemplar).
2. `# Problem` — recurring situation this pattern is for (why it exists).
3. `# Solution shape` — prescribed method package: steps, ownership boundaries, and invariants agents must follow. **Pointers only** — do not paste long code.
4. `## When not to use` — explicit anti-triggers (≥1 bullet).
5. Optional `## Notes` — non-normative only.

Do **not** put `problem` or `solution_shape` only in frontmatter. Frontmatter is the machine/citation contract; body sections are the human/agent readable package.

### Schema fields (frontmatter — lock in SCHEMA.md)

| Key | Type | Allowed values / shape | Required |
|-----|------|------------------------|----------|
| `id` | string | `pattern.{domain}.{slug}` matching filename stem | yes |
| `name` | string | short human title for the package of work | yes |
| `status` | enum | `proposed` \| `approved` \| `retired` | yes |
| `proposed_in` | string \| null | parent Linear ticket id that proposed this pattern (e.g. `AST-913`); `null` only if unknown legacy — prefer always set for new entries | yes |
| `approved_by` | string \| null | literal `Archie` when `status` is `approved` or `retired`; `null` when `status` is `proposed` | yes |
| `approved_at` | string \| null | ISO date `YYYY-MM-DD` when approved/retired; `null` when `status` is `proposed` | yes |
| `canonical_refs` | object[] | each item: `{path: <repo-relative string>, symbol: <string>}` — real implementations; may be `[]` only while `proposed` if refs are still being chosen; **approved** entries must have ≥1 | yes |
| `related_statutes` | string[] | statute ids this pattern must stay inside of (may be `[]` only if none apply; prefer ≥1 when a matching statute exists) | yes |
| `supersedes` | string \| null | prior pattern id this replaces | yes (`null` if none) |
| `superseded_by` | string \| null | successor id when retired/replaced | yes (`null` if none) |

Do **not** add undeclared frontmatter keys. Do **not** put `problem`, `solution_shape`, or `when_not_to_use` in frontmatter — those live in the body.

### Enums

#### `status`

| Value | Meaning |
|-------|---------|
| `proposed` | Catalog entry drafted; **not** yet Archie-approved. May land under `canon/patterns/` so lineage and review are visible. Implementation must **not** depend on this id until `approved`. |
| `approved` | Archie-approved; safe to cite from define-parent / plans. |
| `retired` | Soft-retired; file remains for citations/history. Not in the approved set. |

⚠️ **Decision:** Unlike statutes (in-repo only `active`/`retired`), patterns **allow `proposed` in-repo**. Parent lifecycle requires a visible propose→approve path; keeping proposed files out of the tree would hide the cycle AST-913 AC demands. Approved consumers (AST-914 later) load `status: approved` only.

### Archie lifecycle (AUTHORING.md must spell this out)

| Action | Who drafts | Who approves | What lands in git |
|--------|------------|--------------|-------------------|
| **Propose** | engineer / Chuckles via a parent architectural definition (explicitly flagged as expanding the pattern set) | — (proposal only) | new or updated file with `status: proposed`, `proposed_in` set to the parent ticket id, `approved_by: null`, `approved_at: null` |
| **Approve** | — | Archie | same `id`/path; set `status: approved`, `approved_by: Archie`, `approved_at` to approval date; keep `proposed_in` |
| **Amend** | any engineer / Chuckles | Archie | same `id`/path; body and/or frontmatter updated; if already approved, refresh `approved_at`; keep lineage fields unless this amend is a replacement retire |
| **Retire** | any engineer / Chuckles | Archie | keep file; set `status: retired`; set `superseded_by` to successor id or `null`; do **not** delete the file in the same change that retires it |

Public prose in `canon/patterns/**` uses the alias **Archie** only — never Susan’s real name. Linear assignee flips for approval still target Susan; AUTHORING states: “Archie = architect alias; Linear assignee Susan.” Runtime map: `team-chuckles/agents/identity-table.md`.

⚠️ **Decision:** Retire is soft-retire (file remains). Hard-delete is out of scope so citations and history stay resolvable.

### Approved-set discovery (README + SCHEMA)

Consumers that load “the approved pattern set” include **every** file under `canon/patterns/**` whose frontmatter has:

- `status: approved`

Proposed and retired files are excluded from that set. Selection algorithms for define-parent / review are **out of scope** — this ticket only labels the field and documents discovery.

### Exemplar (exact — Stage 2)

Create **exactly this one** file. It is the schema/lifecycle smoke entry — **not** the full harvest.

#### `canon/patterns/batch/pattern.batch.entity-claim-process-release.md`

```yaml
id: pattern.batch.entity-claim-process-release
name: Entity claim / process / release
status: approved
proposed_in: AST-913
approved_by: Archie
approved_at: "<build-date YYYY-MM-DD>"
canonical_refs:
  - path: src/data/database.py
    symbol: claim_job_batch
  - path: src/data/database.py
    symbol: clear_job_batch
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.4"
related_statutes:
  - astral.batch.claim-process-release
  - astral.batch.batch-id-first
  - astral.batch.batch-id-format
supersedes: null
superseded_by: null
```

**Body gists (write full sections; do not invent extra domains):**

- **Problem:** Dispatch and entity runners need a concurrency-safe way to select work, process it, and release the claim without racing other workers or losing auditability.
- **Solution shape:** Claim a batch with a `batch_id` (first parameter on claim/get/clear helpers), process only claimed rows, clear the batch in `finally` (or equivalent release). Core decides transitions; data owns claim/clear. Do not paste large code — point at `canonical_refs`.
- **When not to use:** One-off admin scripts that intentionally bypass dispatch locking; read-only queries that never mutate claimed rows; non-entity work with no batch table.

Replace `<build-date YYYY-MM-DD>` with the UTC date of the Stage 2 commit.

⚠️ **Decision:** One exemplar only (`pattern.batch.entity-claim-process-release`), landed already `approved` with `proposed_in: AST-913` so the propose→approve lineage is recorded on the entry without leaving a dangling `proposed` file. Full shape harvest (state machine, agent_responses, config blocks, admin endpoints, layer discipline, etc.) is **AST-969**.

---

## Stage 1: Schema + authoring guide + README

**Done when:** `canon/patterns/SCHEMA.md`, `AUTHORING.md`, and `README.md` exist on the publish ref; SCHEMA enumerates every frontmatter key/enum above; AUTHORING documents folder anatomy, id rules, and Archie propose/approve/amend/retire; README explains approved-set discovery and domain-folder layout; no pattern entry files yet.

1. Create directory `canon/patterns/` (no other top-level files than the three named below).
2. Write `canon/patterns/SCHEMA.md` containing:
   - Purpose one-liner (machine + human contract for pattern catalog entries — affirmative counterpart to statutes).
   - The field table from **Mechanical rules → Schema fields** (copy values exactly; do not add undeclared keys).
   - Enum definition for `status` (`proposed` / `approved` / `retired`) with the meanings above.
   - Explicit note: body sections are `# Problem`, `# Solution shape`, `## When not to use`, optional `## Notes`.
   - Frontmatter example using a fictional `pattern.example.demo` id (label it non-normative / not a real pattern).
   - Explicit note: catalog references canonical implementations; it does not duplicate code.
3. Write `canon/patterns/AUTHORING.md` containing:
   - Folder anatomy diagram matching **Mechanical rules → Layout**.
   - Id format rules (`pattern.{domain}.{slug}`).
   - One-file-per-pattern + domain-folder rules (forbid domain monoliths).
   - Lifecycle tables for propose / approve / amend / retire with Archie approval (alias wording).
   - Rule: implementation must not depend on a pattern id until `status: approved`.
   - Pointer: full harvest is AST-969; consumers (define-parent citations, review checks) are AST-914 / rubrics — do not describe their algorithms here beyond approved-set discovery.
   - Explicit: do not redefine `canon/statutes/` schema or layout.
4. Write `canon/patterns/README.md` containing:
   - What this tree is (citable reusable-logic / pattern catalog).
   - Links to `SCHEMA.md` and `AUTHORING.md`.
   - How consumers find the approved set: every file under `canon/patterns/**` whose frontmatter has `status: approved`.
   - Domain-folder rule: domains are folders; one file per pattern.
   - Placeholder section `## Exemplars` stating “populated in AST-925 Stage 2” (Stage 2 will replace this with the real list).

**Commit message:** `code(AST-925): pattern SCHEMA + AUTHORING + README`

---

## Stage 2: Exemplar pattern + README index

**Done when:** Exactly the one exemplar file listed in **Mechanical rules → Exemplar** exists with valid frontmatter (all required keys), `status: approved`, `proposed_in: AST-913`, `approved_by: Archie`, ≥1 `canonical_refs`, ≥1 `related_statutes`, body sections present, and README `## Exemplars` lists that entry with id, status, and relative path.

1. Create `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` at the exact path and frontmatter values specified above. Write Problem / Solution shape / When not to use bodies that match the gist lines; When not to use has ≥1 bullet.
2. Replace README `## Exemplars` placeholder with a table:

   | id | status | path |
   |----|--------|------|
   | `pattern.batch.entity-claim-process-release` | approved | `batch/pattern.batch.entity-claim-process-release.md` |

3. Do **not** add further patterns, domains, or a harvest crosswalk in this ticket.
4. Do **not** edit `canon/statutes/**`, `docs/ASTRAL_CODE_RULES.md`, `docs/ASTRAL_GIT_WORKFLOW.md`, or `docs/ASTRAL_TEAM_WORKFLOW.md`.

**Commit message:** `code(AST-925): exemplar pattern (batch claim-process-release)`

---

## Execution contract

- Execute stages in order; one commit per stage on epic worktree; publish each commit to `origin/sub/AST-913/AST-925-pattern-schema-authoring`.
- Do not add files, keys, domains, or exemplars beyond this plan.
- Ambiguity or drift → stop; comment on **parent** AST-913 with the Stage N blocked template from plan-child.
- No product runtime code. No tests. No hook/CI implementation.

---

## Self-Assessment

**Scope:** `Single-Component` — confined to the new `canon/patterns/` harness tree plus this plan doc; no `src/`, tests, statutes corpus edits, or consumer wiring.

**Conf:** `high` — parent locked storage (`canon/patterns/`), field anatomy, one-file-per-pattern, lifecycle statuses, and “≥1 exemplar / no full harvest”; this plan pins folder/id/frontmatter/lifecycle choices and mirrors the shipped AST-920 shape so build-child has no judgment calls.

**Risk:** `Medium` — a wrong schema or id shape would force AST-969 harvest rework and slow AST-914 citation consumption, but nothing in production runtime executes these files yet.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY / §2.1 config / §2.4 batch / §2.6 state machine / §3.3 imports: N/A to product code — the exemplar **cites** batch claim/process/release and related statutes as narrative sources only; no runtime duplication.
- §3.6: patterns live under `canon/patterns/` (committed product docs), not `debug/spikes/` or repo-root `artifacts/`.
- §4.2: plan lives at `docs/features/team-chuckles/ast-925-….md` per project folder mapping (Team Chuckles → `team-chuckles`).
- No undeclared files; engineer test-tree ban respected (no `tests/` or bible edits).
- Boundaries honored: no statute redefinition; no AST-969 harvest; no consumer procedure edits.
