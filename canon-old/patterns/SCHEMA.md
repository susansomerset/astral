# Pattern schema

Machine + human contract for every file under `canon/patterns/**` (except this file, `AUTHORING.md`, and `README.md`). Patterns are the affirmative counterpart to statutes: statutes constrain what must not happen; patterns prescribe how recurring problems are solved here.

Catalog entries **reference** canonical implementations; they do **not** duplicate code.

## Frontmatter fields

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

## Enums

### `status`

| Value | Meaning |
|-------|---------|
| `proposed` | Catalog entry drafted; **not** yet Archie-approved. May land under `canon/patterns/` so lineage and review are visible. Implementation must **not** depend on this id until `approved`. |
| `approved` | Archie-approved; safe to cite from define-parent / plans. |
| `retired` | Soft-retired; file remains for citations/history. Not in the approved set. |

## Body sections (required order)

After frontmatter, every pattern file uses these sections in this order:

1. `# Problem` — recurring situation this pattern is for (why it exists).
2. `# Solution shape` — prescribed method package: steps, ownership boundaries, and invariants agents must follow. Pointers only — do not paste long code.
3. `## When not to use` — explicit anti-triggers (≥1 bullet).
4. Optional `## Notes` — non-normative only.

## Approved-set discovery

Consumers that load “the approved pattern set” include **every** file under `canon/patterns/**` whose frontmatter has `status: approved`. Proposed and retired files are excluded from that set.

## Non-normative frontmatter example

The following is **not** a real pattern — illustrative shape only (`pattern.example.demo` must not exist as a corpus file):

```yaml
---
id: pattern.example.demo
name: Example demo pattern
status: proposed
proposed_in: AST-000
approved_by: null
approved_at: null
canonical_refs: []
related_statutes: []
supersedes: null
superseded_by: null
---

# Problem

Example recurring situation.

# Solution shape

Example method package.

## When not to use

- Example anti-trigger.
```
