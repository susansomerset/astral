# Statute schema

Machine + human contract for every file under `canon/statutes/**` (except this file, `AUTHORING.md`, and `README.md`).

## Frontmatter fields

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

Do **not** add undeclared frontmatter keys. Do **not** put `statement` or `rationale` in frontmatter — those live in the body.

## Enums

### `tier`

| Value | Meaning |
|-------|---------|
| `universal` | Consumers that load the universal set **must** include every `tier: universal` + `status: active` statute regardless of path/layer filters. Scope fields may still be present for documentation but do not exclude universals from that set. |
| `scoped` | Included only when the consumer’s change set matches `applies_when`. Plan-validation matching is defined in `canon/rubrics/plan/plan-rubric.v1.md` (AST-928); code-review full-set sweep is defined in `canon/rubrics/code/code-rubric.v1.md` (AST-929). This schema only labels the fields. |
### `checkable`

| Value | Meaning |
|-------|---------|
| `hook` | Suitable for a git/pre-commit hook later. Classification only — this schema does not implement hooks. |
| `ci` | Suitable for a CI job later. Classification only — this schema does not implement CI. |
| `judgment` | Enforced by human/agent review (Joan, Radia, engineer judgment). |

### `status`

| Value | Meaning |
|-------|---------|
| `active` | In force; consumers must consider it. |
| `retired` | Soft-retired; file remains for citations/history. Not in the active set. |

In-repo statutes are only `active` or `retired`. Drafts are not committed under `canon/statutes/` (see AUTHORING).

## Body sections (required order)

After frontmatter, every statute file uses these sections in this order:

1. `# Statement` — normative rule text (one statute = one enforceable rule).
2. `## Rationale` — the WHY (retrieval body).
3. `## Examples` with `### Conforming` and `### Violating` (at least one bullet each).
4. Optional `## Notes` — non-normative only.

## Non-normative frontmatter example

The following is **not** a real statute — illustrative shape only (`orch.example.demo` must not exist as a corpus file):

```yaml
---
id: orch.example.demo
title: Example demo statute
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: []
  paths: ["canon/statutes/**"]
  change_types: ["any"]
source_docs: []
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-01-01"
---

# Statement

Example normative text.

## Rationale

Why this rule exists.

## Examples

### Conforming

- Does the right thing.

### Violating

- Does the wrong thing.
```
