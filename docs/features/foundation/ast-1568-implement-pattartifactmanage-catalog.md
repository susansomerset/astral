# AST-1568 — Implement patt.artifact.manage-catalog

<!-- linear-archive: AST-1568 archived 2026-09-09 -->

## Linear archive (AST-1568)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1568/implement-pattartifactmanage-catalog  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 3  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1566; blocks: AST-1569

### Description

## Purpose

Establish the **artifact catalog** — a single config-backed registry describing every versioned artifact key the platform may read or write. Downstream tickets (write-operative, read-current, read-operative, no-coat-check) need a stable catalog API to register and resolve keys. This ticket ships that foundation **for one key only**: the candidate `base_resume` artifact already in use.

## Functional scope

1. **Central registry** — One authoritative catalog structure in config holding per-key metadata: entity type, artifact type string, candidate-scoped flag, body shape contract, and owning component for ingestion when content is absent.
2. **Lookup and validation** — Runtime helpers to resolve a key to its catalog entry, reject unknown keys, and expose metadata callers need without hardcoding tuples in consumers.
3. **Pilot key (only)** — Register `candidate` **/ **`base_resume` as the sole catalog entry for this ticket. Job editable types (`job_resume`, `cover_letter`) and all other keys are **out of scope**.
4. **Scaffold verification** — Component test proves `base_resume` can be looked up and participates in a minimal save → read-current round-trip against the data layer (validates catalog + existing `save_artifact` / `get_current_artifact` wiring, not full write-operative product paths).

## Component scope

* `src/utils/config.py` — **modified** — `ARTIFACT_CATALOG` (or equivalent) registry block with the single `base_resume` entry (entity type `candidate`, candidate-scoped).
* `src/utils/artifact_catalog.py` — **new** — thin lookup/validation helpers (`get_catalog_entry`, `require_catalog_entry`, candidate-scoped flag accessor) so consumers do not scrape config internals.
* `tests/component/utils/test_artifact_catalog.py` — **new** — registry coverage + scaffold round-trip for `base_resume` only.

## Technical scope

* `src/utils/config.py` — New structured catalog mapping artifact type strings to metadata dicts (entity type, candidate_scoped bool, body shape name referencing existing `BUILD_CONFIG` artifact shapes where applicable, ingestion owner component id). Populate **only **`base_resume` for candidate.
* `src/utils/artifact_catalog.py` — Read-only accessors over the catalog; raise clear errors on unknown keys; no I/O.
* `tests/component/utils/test_artifact_catalog.py` — Assert `base_resume` resolves; exercise data-layer save + get_current_artifact using catalog-derived entity_type/artifact_type (scaffold only — no API or UI changes).

## Architectural definition

**Patterns to reuse**

* `patt.artifact.manage-catalog` — this ticket implements the catalog half of that draft pattern only (register + verify); read/write path wiring is AST-1569+. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* **Supersede conflicting patterns (Archie 2026-09-02):** Joan must treat `patt.artifact.manage-catalog` as **authoritative for** `base_resume` **/ catalog registration** and **supersede all conflicting patterns** that still assume ad hoc blob fields, coat-check registration for this key, or hard-coded artifact-type tuples outside the catalog. Cite conflicts explicitly in validate-plan findings; do not leave them as co-equal guidance.
* **Betty / tests:** revise existing bible/manifest coverage that touches `base_resume` so it adheres to this pattern (catalog lookup → artifact APIs for the pilot key; no new coat-check or blob-read expectations for `base_resume` in this slice).

**New patterns proposed**

* none — pattern already drafted on AST-1567; this ticket implements it.

**Applicable statutes**

* `astral.config.config-source-of-truth` — catalog lives in [config.py](<http://config.py>) as SoT. [config-source-of-truth](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — no new inline artifact type tuples outside the catalog. [no-hardcoded-sets](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — no scripts/debug scope. [in-scope-only](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)

## Acceptance criteria

1. Catalog contains exactly one pilot entry: candidate `base_resume`, with complete metadata.
2. Unknown artifact type strings fail fast via catalog helpers — no silent fallback.
3. Component test demonstrates lookup → save_artifact → get_current_artifact round-trip for `base_resume`.
4. No new runtime blob reads or coat-check registrations introduced (catalog-only scope).
5. [AST-1569](https://linear.app/astralcareermatch/issue/AST-1569/implement-pattartifactwrite-operative) can import catalog helpers without reaching into config internals.

## Open questions

none

## Proposed child tickets

Single-slice ticket under [AST-1566](https://linear.app/astralcareermatch/issue/AST-1566/draft-versioned-artifacts-pattern) — no `dispatch-parent` on [AST-1568](https://linear.app/astralcareermatch/issue/AST-1568/implement-pattartifactmanage-catalog). One inseparable foundation vertical: registry shape + helpers + `base_resume` pilot + scaffold test must land together before write-operative ([AST-1569](https://linear.app/astralcareermatch/issue/AST-1569/implement-pattartifactwrite-operative)) can depend on a stable catalog API.

#### 1: **Artifact catalog registry - Ada**

Ship `ARTIFACT_CATALOG` in config with **only** candidate `base_resume`, `artifact_catalog.py` helpers, and component scaffold test. Does **not** register job keys, wire UI/API read paths, grade pins, or coat-check retirement (siblings AST-1569–1572).

**Citations: **`patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`

**Scope: **`src/utils/config.py` (catalog block + `base_resume` entry); `src/utils/artifact_catalog.py` (new helpers); `tests/component/utils/test_artifact_catalog.py` (lookup + data-layer scaffold round-trip).

**Estimate: 3**

---

## Original brief

## Scope

Register artifact catalog metadata in config; process for new keys per draft pattern.

## Pattern

`canon/directives/draft/patt.artifact.manage-catalog.md` on `dev`

## Done when

Catalog registry supports new key registration; component test proves register → read/write round-trip scaffold.

### Comments

#### chuckles — 2026-09-02T19:35:59.383Z
@susan @Betty White origin/tests scrubbed (AST-1574).

- Dropped `1b236a3e6` (pull-merge pollution); tip rebuilt from `82423d73b` + additive cherry-picks + gate harden commit `f2524adf`.
- Durable marker: `origin/tests-clean-base` → `82423d73b`. `validate-tests-branch.sh` now walks tip `--not` that marker (no depth-20 blind spot).
- Re-cut: `origin/sub/AST-1568/AST-1573-artifact-catalog-registry` was built on the polluted tip — Betty should re-`merge-tests` from the cleaned `origin/tests` tip when that child next needs tests delivery. `validate-sub-log` currently ok (empty-range vs ftr).

#### chuckles — 2026-09-02T18:55:21.266Z
[check-linear] User Testing — config block name `ARTIFACT_CONFIG` (not `ARTIFACT_CATALOG` / `ARTIFACTS_CATALOG`); rename the landed pilot via `[bug]`/`[fix]` on this parent (@susan)

#### susan — 2026-09-02T18:54:34.739Z
\[bug\]

Please update the config.py and any current wiring to reflect the requested changes above.

#### susan — 2026-09-02T18:53:49.807Z
Also, please call it ARTIFACT_CONFIG, not ARTIFACTS_CATALOG.  \_CONFIG is our standard suffix for confg.py sections. @chuckles

#### chuckles — 2026-09-02T18:52:36.826Z
[check-linear] User Testing — catalog keys follow entity + `_data` path (e.g. `candidate.artifacts.base_resume`, `job.artifacts.cover_letter`, `candidate.context.strengths`); flat `base_resume` pilot needs rename — mark `[bug]`/`[fix]` on this parent to open the fix child (@susan)

#### susan — 2026-09-02T18:50:35.259Z
@chuckles I want the artifact catalog to use more hierarchy in the naming.  E.g. "candidate.artifacts.base_resume" or "job.artifacts.cover_letter" or "candidate.context.strengths", using the exising \_data path to determine the path for the artifact key.

#### chuckles — 2026-09-02T17:38:31.203Z
AST-1573 REVIEW — merge-child blocked; recalling @Betty White for polluted origin/tests / merge-tests bringing AST-1555 pull-merge into sub range.

#### chuckles — 2026-09-02T17:15:04.545Z
@susan Description updated: Joan treats `patt.artifact.manage-catalog` as superseding conflicting patterns for `base_resume`/catalog; Betty revises `base_resume` tests to that pattern. Proceeding to dispatch.

#### susan — 2026-09-02T17:06:50.423Z
Please have Joan use this draft pattern to SUPERCEDE ALL CONFLICTING PATTERNS, and have Betty revise her tests to adhere to this pattern for base_resume.

#### chuckles — 2026-09-02T17:04:23.447Z
[check-linear] Todo — Description scoped to candidate base_resume only (@susan)

#### susan — 2026-09-02T17:02:40.566Z
@chuckles This should start with the one artifact we are already using, which is the candidate's base_resume artifact.  The scope of this implementation is limited to only that artifact key.  Please update the description to reflect that specifically.

---

_Implementation detail may live in git history on `origin/dev`._
