# AST-1578 — Split token config: add source-type field (data_field / artifact / special_case) to token catalog, decommission implicit token-list-only model

<!-- linear-archive: AST-1578 archived 2026-09-22 -->

## Linear archive (AST-1578)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1578/split-token-config-add-source-type-field-data-field-artifact-special  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1571

### Description

## Purpose

Prompt tokens stay config-driven for *which tokens exist*, but the catalog today is an undifferentiated list — every entry looks the same to claim gates, pin capture, and explainability. This epic adds an explicit `source_type` on each `TOKEN_SOURCES` entry (`data_field` / `artifact` / `special_case`) so downstream work can tell which tokens are pinnable ARTIFACT_CONFIG bodies, which are live blob fields, and which are non-data special cases — without folding the token list into `ARTIFACT_CONFIG` or inventing a second shadow allowlist.

## Functional scope

1. **Typed token catalog** — Every `TOKEN_SOURCES` entry carries a required `source_type` of exactly one of: `data_field` (live blob field, no versioning/pin), `artifact` (resolves against an `ARTIFACT_CONFIG` key via read-current; pinnable `artifact_id`), or `special_case` (non-data tokens such as chain hops like `CALLER_RESPONSE`).
2. **Artifact linkage** — Every `artifact`-typed entry also names the `ARTIFACT_CONFIG` registry key it references. Token catalog and artifact catalog remain separate registries; artifact tokens point at keys, they do not live inside `ARTIFACT_CONFIG`.
3. **Classify the live registry** — Every existing token name is classified under this model in this ticket (see Technical scope). Only tokens that both appear in `TOKEN_SOURCES` today *and* map to a registered `ARTIFACT_CONFIG` key are typed `artifact` here — no new token names and no new `ARTIFACT_CONFIG` keys.
4. **Decommission the implicit model** — Startup asserts fail import if any entry lacks a valid `source_type`, if any `artifact` entry lacks a key present in `ARTIFACT_CONFIG`, or if a non-artifact entry claims an artifact key. Untyped / half-typed catalogs are not shippable.
5. **Resolve path unchanged** — Existing `source` / `path` / resolver fields and `resolve_tokens` behavior stay as they are. Consumer rewires that actually fetch artifact bodies via read-current are out of scope (sibling base_resume consumer work). Prompt-parse helpers for claim/pin are out of scope (owned by `tokens_ready` / source-artifact-id siblings).
6. **Explicit non-goals** — No new `ARTIFACT_CONFIG` membership; no promotion of blob fields to catalog keys (catalog-key scope ticket); no `tokens_ready` claim qualifier; no source-artifact-id pin capture on write; no React/UI changes; no folding `TOKEN_SOURCES` into `ARTIFACT_CONFIG`.

## Component scope

* `src/utils/config.py` — **modified** — add `source_type` (and `artifact_key` on artifact entries) to every `TOKEN_SOURCES` entry; module-docstring / section comment for the typing contract; startup asserts; optional thin read-only getters that return tokens filtered by `source_type` or map an artifact token name → `ARTIFACT_CONFIG` key (no prompt parsing, no I/O).

## Technical scope

* `src/utils/config.py` — Extend each `TOKEN_SOURCES` value dict with required `source_type`. Classification for the current registry:
  * **artifact** — `BASE_RESUME` only, with `artifact_key` = `candidate.artifacts.base_resume` (sole current intersection of `TOKEN_SOURCES` and `ARTIFACT_CONFIG`). Keep existing `source` / `path` / `serialize` so resolve behavior is unchanged until consumer rewire siblings land.
  * **data_field** — all other `source: "candidate"` path tokens (names, contact, context, `COMPANY_SEARCH_TERMS`, etc.) — live blob / overlay fields, not versioned catalog keys.
  * **special_case** — `source: "chain"` (including `CALLER_*`, `SELECTED_AGENT`, `JOB_LIST_VISIBLE`); `source: "pronoun"`; `source: "rubric"` (including named rubric pins); `source: "config"`; `source: "output_type"`; `source: "job"` (`VISIBLE_JD`, `ANALYSIS_*`, `RESUME_SECTION_CATALOG`).
* `src/utils/config.py` — Startup asserts: every entry has `source_type` in `{data_field, artifact, special_case}`; every `artifact` entry has `artifact_key in ARTIFACT_CONFIG`; no non-artifact entry may carry `artifact_key`; allowed `source_type` values live as a config constant (not inline magic sets in callers).
* `src/utils/config.py` — Optional thin helpers (same module): list/filter token names by `source_type`; resolve artifact token → `artifact_key`. No agent_task prompt scanning (sibling ownership).

## Architectural definition

**Patterns to reuse**

* `pattern.config.config-block` — token typing lives in the `TOKEN_SOURCES` config block, not scattered caller literals. [current](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>)
* `patt.artifact.manage-catalog` — artifact-typed tokens reference registered catalog keys only; do not invent keys from blob paths. [draft](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.read-current` — defines what `artifact` typing means for later consumers (current row / pinnable id); this epic does not wire the read. [draft](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)

**New patterns proposed**

* none — this is a config-block field addition under the existing token registry, not a new reusable shape.

**Applicable statutes**

* `astral.config.config-source-of-truth` — behavior-driving token typing stays in `config.py`. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — allowed `source_type` values are a config constant; callers do not redefine the enum. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — no resolve rewire, no claim qualifier, no pin capture, no catalog-key promotions in this epic. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* Universal active set applies to product config changes (plan/code consumers load it); no additional orchestration statutes beyond the above for this config-only slice.

## Acceptance criteria

1. Importing `src.utils.config` exposes every `TOKEN_SOURCES` entry with a valid `source_type` of `data_field`, `artifact`, or `special_case`.
2. `BASE_RESUME` is `source_type: artifact` with `artifact_key` equal to `candidate.artifacts.base_resume` and that key exists in `ARTIFACT_CONFIG`.
3. No other current `TOKEN_SOURCES` name is typed `artifact` unless it also has a registered `ARTIFACT_CONFIG` key (today: none besides `BASE_RESUME`).
4. Startup asserts reject missing/invalid `source_type`, artifact entries without a catalog key, and non-artifact entries that carry `artifact_key`.
5. `TOKEN_SOURCES` remains a separate top-level registry from `ARTIFACT_CONFIG` (artifact tokens reference keys; they are not nested inside the artifact catalog).
6. Existing `resolve_tokens` outcomes for unchanged inputs are preserved (no consumer read-current rewire in this epic).
7. Admin token-list endpoints that already return token name lists still function (names unchanged).

## Open questions

none

## Proposed child tickets

#### 1: **Token catalog source_type typing - Ada**

Land `source_type` (+ `artifact_key` on artifact entries) on every `TOKEN_SOURCES` row per the classification above, config constant for allowed types, startup asserts, and optional thin by-type / artifact-key getters. Does **not** own prompt parsing, claim qualifiers, pin capture, resolve-path rewires, or new `ARTIFACT_CONFIG` keys.

**Citations:** `pattern.config.config-block`; `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`

**Scope:** `src/utils/config.py` — `source_type` / `artifact_key` on `TOKEN_SOURCES`; allowed-type constant; startup asserts; optional thin getters (prose above)

**Estimate: 3**

**Monolith check:** Six functional capabilities, one child — intentional single vertical slice: typing, classification, artifact linkage, and asserts must ship atomically so `TOKEN_SOURCES` never exists half-typed; prompt-parse / claim / pin work stays on sibling tickets that already depend on this field.

**Scope partition check:** sole Component/Technical file `src/utils/config.py` → child 1. No unclaimed or overlapping files.

---

## Original brief

## Decision

Tokens usable in prompts must stay config-driven for *which tokens exist*, but the token catalog needs a source-type field per entry, distinguishing:

* **data_field** — resolves against a live blob field (e.g. candidate first name); no versioning, no pin.
* **artifact** — resolves against an `ARTIFACT_CONFIG`-registered key via read-current; produces a pinnable `artifact_id`.
* **special_case** — non-data tokens such as `CALLER_RESPONSE`.

This replaces the current implicit model where the token list in `config.py` doesn't distinguish source type. It does **not** mean folding the token list into `ARTIFACT_CONFIG` — those are separate catalogs. Artifact-typed tokens reference `ARTIFACT_CONFIG` keys; they don't live inside it. `ARTIFACT_CONFIG` entries carry versioning/storage machinery (body_shape, retire+insert, current flag) that most data_field tokens will never need — collapsing the two would force that machinery onto fields that don't want it.

## Why

This typing is the prerequisite for:

* Resolving which tokens in a prompt need pin capture at write time (artifact-typed only).
* The `tokens_ready` claim qualifier (separate ticket) knowing which tokens to check availability for.
* Keeping data_field/special_case tokens resolved live (current at read time), while artifact tokens get pinned (current at build time, stored permanently).

## Scope note

Fidelity implication: only artifact-typed tokens are exactly reproducible for explainability ("why did we give this a C"). data_field tokens resolve to whatever's current at read time — approximately reproducible, not pinned. Worth tracking which data_field tokens actually show up in grading prompts as candidates for promotion to catalog keys (see separate "catalog-key scope" ticket).

## Origin

Design discussion in chat, 2026-09-02, working through Postgres migration data-storage design for patt.artifact.* pattern work ([AST-1566](https://linear.app/astralcareermatch/issue/AST-1566/draft-versioned-artifacts-pattern) epic, [AST-1571](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative) read-operative).

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
