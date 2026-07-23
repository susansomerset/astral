# Pattern catalog

Discrete, id’d, citable reusable-logic packages for Astral — the affirmative counterpart to the statute harness. Adding a method package means adding a pattern; citing reuse means pointing at a pattern id.

- **Schema (fields + enums):** [SCHEMA.md](SCHEMA.md)
- **Authoring + lifecycle:** [AUTHORING.md](AUTHORING.md)

## Layout

Domains are folders under `canon/patterns/`; one file per pattern. Filename stem equals the pattern `id` (`pattern.{domain}.{slug}`).

## Approved set

Consumers that load “the approved pattern set” include **every** file under `canon/patterns/**` whose frontmatter has:

- `status: approved`

Proposed and retired files are excluded from that set.

## Exemplars

| id | status | path |
|----|--------|------|
| `pattern.batch.entity-claim-process-release` | approved | `batch/pattern.batch.entity-claim-process-release.md` |
