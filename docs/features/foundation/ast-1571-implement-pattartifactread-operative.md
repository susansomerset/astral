# AST-1571 — Implement patt.artifact.read-operative

<!-- linear-archive: AST-1571 archived 2026-09-24 -->

## Linear archive (AST-1571)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1572

### Description

## Purpose

Ship **read-operative** for the pilot catalog key `candidate.artifacts.base_resume`: fetch the exact artifacts-table body by `artifact_id` **pin** so the UI can render the base_resume that seeded a job’s artifact build, and so Contact (Estelle via Slack) can answer against that same pinned body — not the latest edit and not a live `*_data` blob. Write-operative ([AST-1569](https://linear.app/astralcareermatch/issue/AST-1569)) returns pins; this epic owns the read. **Persisting** which source artifact ids seeded a derived write is **not** this pattern — document that under a new draft `patt.artifacts.traceability` here, implement later. Sibling **read-current** ([AST-1570](https://linear.app/astralcareermatch/issue/AST-1570)) owns edit/live display; **no-coat-check** ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572)) depends on both reads.

## Functional scope

1. **Operative read by pin (pilot)** — Given an `artifact_id`, load that artifacts-table row and return the deserialized `base_resume` body (or empty on miss). No coat-check. No fallback to candidate/job `*_data` blob dotted-path reads on the operative path.
2. **Entity-owned helper** — Candidate (and Contact via the same helper path) resolve pins in core — no separate artifact component (same ownership rule as write-operative).
3. **UI consumer** — Job artifact-building UI renders the pilot `base_resume` used for that job’s build via read-operative when a pin is supplied; remove blob dotted-path reads for that pinned content on those surfaces.
4. **Contact consumer** — Estelle (Slack Contact) uses the **same** read-operative path for pinned `base_resume` “as it was,” not live current.
5. **Traceability pattern (docs only)** — Author draft `patt.artifacts.traceability`: record generation circumstances — versioned `agent_id`, versioned `agent_task_id`, and the array of current artifact ids that seeded prompt tokens; subsequent manual edits (UI or Estelle) mark the new version as manual while inheriting originating task sources. **Implementing** that persist/wire is **out of scope** for this issue.
6. **Explicit non-goals** — No grade/analysis pin writers or grade explainability rewires. No wiring that persists source-artifact ids onto derived job artifacts (traceability). No new `ARTIFACT_CONFIG` keys. No read-current editor hydrate ([AST-1570](https://linear.app/astralcareermatch/issue/AST-1570)). No coat-check retirement ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572)). No HTTP exposure of `artifact_id` on ordinary candidate save responses (same rule as write-operative). No scoped-without-pin fetch as a substitute for read-current (`get_current_artifact` stays [AST-1570](https://linear.app/astralcareermatch/issue/AST-1570)). Pin-only for this epic’s new read path.

## Component scope

* `src/data/database.py` — **modified** — by-`artifact_uuid` fetch; deserialize `artifact_data`; empty on miss.
* `src/core/candidate.py` — **modified** — pilot read-operative helper (by pin → body) for `candidate.artifacts.base_resume`; shared by UI/API and Contact.
* `src/core/contact.py` — **modified** — Estelle paths that need pinned pilot `base_resume` call that helper (same path as UI); no blob dual-read on the operative path.
* `src/ui/api/api_jobs.py` and/or `src/ui/api/api_candidate.py` — **modified** — server path(s) the job-artifacts UI needs so it can render pinned pilot `base_resume` via core read-operative (no client→DB; do not add a one-off `artifact_id` field on ordinary save responses).
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (and any thin report helper it already uses for job artifact tabs) — **modified** — render source pilot `base_resume` for job artifact building via the operative API/helper path; drop blob dotted-path reads for that pinned content.
* `canon/directives/draft/patt.artifacts.traceability.md` — **new** — draft only (generation provenance + manual-edit inheritance); no product code.
* `canon/directives/draft/patt.artifact.read-operative.md` — **untouched** as narrative SoT (cite only).

## Technical scope

* `src/data/database.py` — SELECT by `artifact_uuid`; deserialize `artifact_data`; return structured result or empty. Data raises/returns per convention; no logging; no blob/coat-check.
* `src/core/candidate.py` — Public pin→body helper for the pilot key: call by-uuid fetch; return body or empty. Contact and API use this — not ad-hoc `candidate_data.artifacts.base_resume` walks on the operative path.
* `src/core/contact.py` — Where Estelle must ground an answer in a pinned pilot `base_resume`, call the candidate helper with the `artifact_id` she holds; on miss surface gap (no blob fallback on that path).
* UI API + `JobAnalysisReportModal` — When rendering the base_resume that seeded a job’s artifact build, resolve via read-operative (pin in / body out through existing API conventions). Exact request shape is `plan-child`; do not invent pin-persist onto the job here.
* `patt.artifacts.traceability.md` — Document versioned agent + agent_task ids, seed `artifact_id[]`, and manual-edit inheritance; flag implement-later.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.read-operative` — by-pin operative fetch; no coat-check / no blob fallback. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.write-operative` — pins originate from write return values. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.manage-catalog` — pilot key only: `candidate.artifacts.base_resume`. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.read-current` — **boundary only** ([AST-1570](https://linear.app/astralcareermatch/issue/AST-1570)). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)

**New patterns proposed**

* `patt.artifacts.traceability` — provenance for derived artifacts (versioned agent_id, versioned agent_task_id, seed artifact id array; manual UI/Estelle edits inherit originating task sources). **Draft this ticket; Archie approval before any implement ticket depends on it. Not implemented here.**

**Applicable statutes**

* `astral.standards.in-scope-only` — [in-scope-only](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.standards.database-header-inventory` — [database-header-inventory](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>)
* `astral.standards.data-raises-caller-logs` — [data-raises-caller-logs](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>)
* `astral.standards.debug-contract-gated` — [debug-contract-gated](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>) (touched Contact/`debug=` resolve)
* `astral.layers.import-direction` — [import-direction](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.config.config-source-of-truth` — [config-source-of-truth](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* Universal set applies to product code.

## Acceptance criteria

1. By-`artifact_uuid` data fetch returns the pilot body or empty; operative path never coat-checks or reads `*_data` blobs as fallback.
2. Candidate exposes a pin→body helper for `candidate.artifacts.base_resume`; Contact Estelle uses that same helper for pinned historical answers.
3. Job artifact-building UI can render a pinned pilot `base_resume` through the server operative path; blob dotted-path reads for that pinned content on those surfaces are gone.
4. Draft `canon/directives/draft/patt.artifacts.traceability.md` exists and covers versioned agent_id, versioned agent_task_id, seed artifact id array, and manual-edit inheritance — with no product persist/wire from that pattern in this ticket.
5. No grade/analysis pin writers; no new catalog keys; no read-current editor work; no coat-check retirement; no ordinary-save HTTP `artifact_id` field.

## Open questions

none

## Proposed child tickets

#### 1!: **get-by-uuid + candidate read-operative + traceability draft - Ada**

Data-layer fetch by `artifact_uuid`; candidate pin→body helper for pilot `base_resume`; author draft `patt.artifacts.traceability` (docs only). Does **not** own JAR UI or Contact Estelle call-site rewires.

**Citations: **`patt.artifact.read-operative`; `patt.artifact.manage-catalog`; `patt.artifacts.traceability` (new draft); `astral.standards.database-header-inventory`; `astral.standards.data-raises-caller-logs`; `astral.layers.import-direction`; `astral.config.config-source-of-truth`

**Scope: **`src/data/database.py`; `src/core/candidate.py`; `canon/directives/draft/patt.artifacts.traceability.md` (**new**)

**Estimate: 3**

#### 2: **UI + Contact pilot base_resume operative resolve - Katherine**

After #1: wire job artifact-building UI (JAR + needed jobs/candidate API) and Contact Estelle to the shared read-operative helper for pinned pilot `base_resume`; remove blob dotted-path reads for that pinned content on those paths. Does **not** persist seed artifact ids (traceability).

**Citations: **`patt.artifact.read-operative`; `astral.standards.in-scope-only`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`

**Scope: **`src/core/contact.py`; `src/ui/api/api_jobs.py` and/or `src/ui/api/api_candidate.py`; `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (and any thin report helper already used for job artifact tabs)

**Estimate: 5**

**Monolith check:** Core read + docs vs UI/Contact consumers → 2 children.

**Scope partition check:** database + candidate + traceability draft → child 1. contact + API + JAR → child 2.

---

## Original brief

## Scope

read-operative by artifact_id pin for explainability paths.

## Pattern

`canon/directives/draft/patt.artifact.read-operative.md`

## Depends on

write-operative

## Done when

Grade/analysis renderers resolve pins; blob dotted-path reads removed for pinned content.

### Comments

#### chuckles — 2026-09-03T01:14:22.612Z
[check-linear] Discussion — scope locked to candidate.artifacts.base_resume pilot; UI + Estelle same read-operative path; derived-source persist → patt.artifacts.traceability (named, OOS). Description + proposed children updated. (@susan)

#### susan — 2026-09-03T01:10:56.006Z
@chuckles the scope of this ticket is too broad. It only requires handling the pilot case of base_resume.  The ui will need to use it to render the base_resume used for a specific job's artifacts building, and the contact component (Estelle via slack) will use it by the same path.  The wiring of how we persist the source artifacts for derived artifacts is out of scope for this pattern, but we need a new pattern for patt.artifacts.traceability that will discuss recording the circumstances by which the artifact was originally generated, including  a versioned agent_id, a versioned agent_task_id and an array of current artifact id that were used to seed the tokens in the prompts. Subsequent manual edits via the ui or by Estelle can be indicated as such on the new versions of the content while inheriting the originating task sources.  Add this to the new pattern documentation, but consider it out of scope for this issue.

#### chuckles — 2026-09-03T00:20:05.876Z
@susan

1. **Pin storage shape** — Where should a grade/analysis record store `artifact_id`? (e.g. per-grade-row field, sibling key next to `*_grades` / `analysis_upshot`, map under `job_data.artifacts`, or other.) Name the field/envelope SoT for readers.
2. **Which writers / which keys this ticket** — Today only `candidate.artifacts.base_resume` is in `ARTIFACT_CONFIG`, and DO/GET/LIKE grades do not consume that body. Enumerate which runtime lands must **write** pins in AST-1571, and which catalog keys they pin — or confirm this epic ships read API + helpers only with one concrete wire you name.
3. **Rubric snapshots vs artifact pins** — Explainability today uses job-carried `*_rubric` JSON snapshots (AST-1063), while rubrics live on `rubric_vector`, not `ARTIFACT_CONFIG`. Does this ticket replace those embedded snapshots with `artifact_id` pins, leave snapshots alone until rubrics are cataloged, or something else?
4. **Contact historical answers** — Pattern Implementation lists Contact “as it was” answers. Include Contact pin resolve in this epic, or defer to AST-1572 / a follow-on?
5. **Scoped read without pin** — Ship the pattern’s optional scoped `(entity_type, entity_id, artifact_type[, candidate_id])` fetch this ticket, or pin-only for v1?

---

_Implementation detail may live in git history on `origin/dev`._
