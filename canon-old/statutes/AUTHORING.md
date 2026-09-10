# Statute authoring guide

How to write, approve, and maintain statutes under `canon/statutes/`. Field definitions live in [SCHEMA.md](SCHEMA.md). Harvest completeness (crosswalk + narrative leftovers) lives in [HARVEST.md](HARVEST.md) (AST-921).

## Folder anatomy

```
canon/statutes/
  README.md
  SCHEMA.md
  AUTHORING.md
  orchestration/<domain>/<id>.md    # generic pipeline / team-orchestration statutes
  astral/<domain>/<id>.md           # astral product-specific statutes
```

- **One file per statute.** Filename equals the statute `id` + `.md`.
- **Domains are folders** under a namespace (`orchestration/` or `astral/`). Never flatten statutes as siblings of `SCHEMA.md`. Never create one-file-per-domain monoliths.
- **Reserved top-level names:** `README.md`, `SCHEMA.md`, `AUTHORING.md`, `HARVEST.md`, `orchestration/`, `astral/`. Do not invent other top-level entries without Archie approval and a schema/authoring update.

## Id format

- Pattern: `{namespace}.{domain}.{slug}`
- `namespace` ∈ {`orch`, `astral`} — maps 1:1 to folders `orchestration/` and `astral/`.
- `domain` = folder name under that namespace (lowercase kebab-case).
- `slug` = lowercase kebab-case, stable, meaning-bearing (not sequential numbers).
- **Id is immutable** for the life of the statute. Amend keeps the same id. Retire keeps the file; `status` becomes `retired`.

Path and id stay aligned: `canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md` ↔ id `astral.git.engineer-test-tree-ban`.

## File format

Markdown with YAML frontmatter (all SCHEMA-required keys) then body sections in SCHEMA order: `# Statement`, `## Rationale`, `## Examples` (`### Conforming` / `### Violating`), optional `## Notes`.

## Drafts are not committed

`status` in-repo is only `active` or `retired`. Drafts live on the author’s branch or Linear until Archie approves. Only approved statutes land under `canon/statutes/`.

## Archie

**Archie** is the architect alias used in public prose under `canon/statutes/**`. Linear assignee flips for approval target Susan; comments that need the architect use `@susan`. Do not put Susan’s real name in statute files. Runtime map: `team-chuckles/agents/identity-table.md` (Archie → Susan).

## Lifecycle

| Action | Who drafts | Who approves | What lands in git |
|--------|------------|--------------|-------------------|
| **Add** | any engineer / Chuckles | Archie | new file, `status: active`, `approved_by: Archie`, `approved_at` set |
| **Amend** | any engineer / Chuckles | Archie | same `id`/path; body and/or frontmatter updated; `approved_at` refreshed; keep `supersedes`/`superseded_by` unless this amend is a replacement retire |
| **Retire** | any engineer / Chuckles | Archie | keep file; set `status: retired`; set `superseded_by` to successor id or `null`; do **not** delete the file in the same change that retires it |

Retire is **soft-retire** (file remains) so citations and history stay resolvable. Hard-delete is out of scope.

## Harvest and consumers

- Full law-doc harvest into this tree is **AST-921** — do not redefine schema while harvesting.
- Joan / validate-plan / Review Rubrics consumers are **AST-910** / **AST-916** — do not describe their selection algorithms here beyond: universals = every `tier: universal` + `status: active` file under `canon/statutes/**`.
