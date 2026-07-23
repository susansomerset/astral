# Pattern authoring guide

How to propose, approve, and maintain patterns under `canon/patterns/`. Field definitions live in [SCHEMA.md](SCHEMA.md). Full recurring-shape harvest lives under AST-969 (not this guide).

## Folder anatomy

```
canon/patterns/
  README.md
  SCHEMA.md
  AUTHORING.md
  <domain>/<id>.md
```

- **One file per pattern.** Filename equals the pattern `id` + `.md`.
- **Domains are folders** directly under `canon/patterns/` (lowercase kebab-case). Never flatten patterns as siblings of `SCHEMA.md`. Never create one-file-per-domain monoliths.
- **Reserved top-level names:** `README.md`, `SCHEMA.md`, `AUTHORING.md`, plus domain folders. Do not invent other top-level filenames without Archie approval and a schema/authoring update.
- **No `orchestration/` vs `astral/` namespace split** under patterns — domain folders alone group entries. Do not redefine `canon/statutes/` schema or layout.

## Id format

- Pattern: `pattern.{domain}.{slug}`
- `domain` = folder name under `canon/patterns/` (lowercase kebab-case).
- `slug` = lowercase kebab-case, stable, meaning-bearing (not sequential numbers).
- **Id is immutable** for the life of the pattern. Amend keeps the same id. Retire keeps the file; `status` becomes `retired`.

Path and id stay aligned: `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` ↔ id `pattern.batch.entity-claim-process-release`.

## File format

Markdown with YAML frontmatter (all SCHEMA-required keys) then body sections in SCHEMA order: `# Problem`, `# Solution shape`, `## When not to use`, optional `## Notes`.

## Archie

**Archie** is the architect alias used in public prose under `canon/patterns/**`. Linear assignee flips for approval target Susan; comments that need the architect use `@susan`. Do not put Susan’s real name in pattern files. Runtime map: `team-chuckles/agents/identity-table.md` (Archie → Susan).

## Lifecycle

| Action | Who drafts | Who approves | What lands in git |
|--------|------------|--------------|-------------------|
| **Propose** | engineer / Chuckles via a parent architectural definition (explicitly flagged as expanding the pattern set) | — (proposal only) | new or updated file with `status: proposed`, `proposed_in` set to the parent ticket id, `approved_by: null`, `approved_at: null` |
| **Approve** | — | Archie | same `id`/path; set `status: approved`, `approved_by: Archie`, `approved_at` to approval date; keep `proposed_in` |
| **Amend** | any engineer / Chuckles | Archie | same `id`/path; body and/or frontmatter updated; if already approved, refresh `approved_at`; keep lineage fields unless this amend is a replacement retire |
| **Retire** | any engineer / Chuckles | Archie | keep file; set `status: retired`; set `superseded_by` to successor id or `null`; do **not** delete the file in the same change that retires it |

Retire is **soft-retire** (file remains) so citations and history stay resolvable. Hard-delete is out of scope.

**Implementation must not depend on a pattern id until `status: approved`.**

## Harvest and consumers

- Full astral recurring-shape harvest into this tree is **AST-969** — do not redefine schema while harvesting.
- define-parent citation wiring and review conformance checks are **AST-914** / Review Rubrics — do not describe their selection algorithms here beyond: approved set = every `status: approved` file under `canon/patterns/**`.
