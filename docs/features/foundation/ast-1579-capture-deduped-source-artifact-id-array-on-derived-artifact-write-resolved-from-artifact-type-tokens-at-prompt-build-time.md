# AST-1579 — Capture deduped source-artifact-id array on derived-artifact write, resolved from artifact-type tokens at prompt-build time

<!-- linear-archive: AST-1579 archived 2026-09-24 -->

## Linear archive (AST-1579)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1579/capture-deduped-source-artifact-id-array-on-derived-artifact-write  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Ship the prompt-time **source-artifact-id harvest** that makes grade and derived-artifact explainability honest: when an agent run builds a prompt, parse the tokens actually embedded in that prompt, resolve every `artifact`-typed token to the then-current artifacts-table UUID via read-current, dedupe, and persist that array with the write of the derived result. This is the implement ticket for the seed-id half of draft `patt.artifact.traceability`, and it answers [AST-1571](https://linear.app/astralcareermatch/issue/AST-1571) Open Question 1’s storage shape for grade/analysis runs (sibling key beside the grade set — not per grade row). Without it, read-operative can fetch a pinned body but nothing records which pins seeded a grading or craft run, so later edits to a resume or context artifact silently rewrite “why did we give this a C.”

## Functional scope

1. **Prompt-token source-pin harvest** — From the prompt texts used for an agent run (the same slots already scanned for caller tokens — system / user / cache / nocache / live as applicable), parse `{$TOKEN}` names from the text (no hand-maintained shadow allowlist). Classify each name via `TOKEN_SOURCES.source_type`. For `artifact` entries only, resolve the catalog key’s then-current `artifact_uuid` via read-current for the run’s entity scope. Skip missing current rows (omit that id; do not coat-check or invent). Return a **deduped** list of UUID strings (`set()` semantics — same artifact type twice in one prompt yields one id).
2. **Persist on consult grade / analysis writes** — When a grading or analysis run stores its result set on the job (`*_grades` / `analysis_upshot` and their existing sibling score/notes/rubric keys), also store the harvested source-artifact-id array as a **sibling job_data key** next to that set (one array for the whole run — not per grade line).
3. **Persist on generative artifact-table writes** — When this same agent run lands a derived body through the operative artifact write path (`save_artifact` / tracker or candidate catalog write), pass the harvested array as `source_artifact_ids` on that new row. **Exception:** `job.artifacts.job_resume` keeps [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588) / [AST-1592](https://linear.app/astralcareermatch/issue/AST-1592) always-auto-cite-current-`base_resume` rule (caller/harvested lists must not override it).
4. **Explicit non-goals** — No `tokens_ready` claim qualifier ([AST-1580](https://linear.app/astralcareermatch/issue/AST-1580) Backlog). No versioned `agent_id` / `agent_task_id` lineage columns (still draft-only in `patt.artifact.traceability`). No reclassification of rubric / special_case tokens into `artifact`. No new `ARTIFACT_CONFIG` keys. No coat-check. No manual-edit inheritance of seed arrays on UI/Estelle saves (separate traceability arc). No read-operative consumer rewires beyond what already exists. No changing job_resume’s hardcoded base_resume auto-cite.

## Component scope

* `src/utils/config.py` — **modified** — reuse existing `_TOKEN_RE` / `TOKEN_SOURCES` / `get_artifact_key_for_token` / by-`source_type` getters; add only what harvest needs that is purely catalog/parse (e.g. list artifact token names referenced by one or more prompt texts). No resolve I/O here if that stays in core.
* `src/core/agent.py` — **modified** — at prompt-build time in the agent run path, invoke harvest over the run’s prompt texts + candidate (and job when needed) scope; carry the deduped id list with the run so persist callers can write it; thread into generative artifact lands that already call `save_job_artifact` / `save_candidate_data`.
* `src/core/candidate.py` — **modified** — expose or reuse a current-`artifact_uuid`-by-catalog-key resolve for harvest (body-only `get_candidate_current` is not enough); extend operative `save_candidate_data` str-path to accept and pass optional `source_artifact_ids` through to `database.save_artifact` when the write is generative from an agent run.
* `src/core/consult.py` — **modified** — when persisting `*_grades` / `analysis_upshot` (and existing sibling keys) via `tracker.save_job_data`, also write the sibling source-artifact-id array harvested for that run.
* `src/core/tracker.py` — **modified** — only if a thin pass-through or shared current-id helper is required for job-scoped harvest or for non-`job_resume` generative writes; do **not** weaken job_resume auto-cite.
* `canon/directives/draft/patt.artifact.traceability.md` — **modified** — one-line Implementation alignment that prompt-time token harvest + grade sibling persist + generative `source_artifact_ids` wiring is this epic; do not promote the draft.

## Technical scope

* `src/utils/config.py` — Parse helper(s) over prompt text(s) using the existing `{$TOKEN}` regex; filter to `source_type == "artifact"` via the typed catalog; map name → `artifact_key`. No DB calls. No second allowlist.
* `src/core/agent.py` — After task prompts are known for the run, harvest artifact pins (candidate id required for candidate-scoped keys; omit ids with no current row). Attach the deduped list to run context / return path so consult and craft-land can persist it without re-parsing. On generative `save_job_artifact` / `save_candidate_data` lands from this run, pass that list (except job_resume auto-cite remains authoritative).
* `src/core/candidate.py` — Current-uuid-by-key helper (catalog key → `get_current_artifact` → `artifact_uuid` or empty). Operative save accepts optional source ids and forwards them on insert; identical-to-current short-circuit behavior unchanged.
* `src/core/consult.py` — Grade/analysis `save_job_data` payloads gain one sibling key for the harvested array beside `{prefix}_grades` / `analysis_upshot` (exact key name is plan-child under existing `{prefix}_*` convention). Empty harvest → empty list, not omit-vs-null divergence invented ad hoc.
* `src/core/tracker.py` — Touch only if harvest or non-job_resume generative write needs a shared current-id or source pass-through; job_resume continues to ignore caller sources.
* `patt.artifact.traceability.md` — Note this epic implements seed-id capture at prompt build + the two persist surfaces above; agent/task lineage and manual inheritance remain implement-later.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.traceability` — seed `artifact_id[]` recorded with the derived write; this epic implements the prompt-time harvest + persist slice (not agent/task lineage, not manual inheritance). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.traceability.md>)
* `patt.artifact.read-current` — harvest resolves then-current UUIDs only via current-read / current row; never coat-check. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.write-operative` — generative artifact-table lands persist `source_artifact_ids` on the new current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.manage-catalog` — only `TOKEN_SOURCES` artifact entries whose `artifact_key` is in `ARTIFACT_CONFIG` are pinnable. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.read-operative` — **boundary only** (consumers resolve stored pins later; this epic writes the pins). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.config.config-block` — token typing and parse stay driven by the `TOKEN_SOURCES` config block. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.config.config-block.md>)

**New patterns proposed**

* none — implements the existing traceability draft’s seed-id array; does not invent a second provenance shape.

**Applicable statutes**

* `astral.config.config-source-of-truth` — harvest classification comes from `TOKEN_SOURCES`, not caller literals. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — no parallel pinnable-token allowlist beside the typed catalog. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — no tokens_ready, no lineage columns, no rubric retype, no coat-check. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.standards.data-raises-caller-logs` — data/current-row miss stays empty/omit at harvest; callers don’t invent ids. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>)
* `astral.standards.dry-and-focused-functions` — one harvest helper; consult/agent lands call it rather than re-implement parse+resolve. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
* `astral.standards.debug-contract-gated` — any new `debug=` on touched resolve/persist paths follow Style D. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>)
* `astral.layers.import-direction` — config parse stays above core I/O; core does not import UI. [current](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)

**Requesting a change to an existing pattern:** `patt.artifact.traceability` — current draft still says seed-id capture is a generic “implement ticket”; update Implementation to name this epic’s surfaces (prompt harvest, grade/analysis sibling key, generative `source_artifact_ids`) and keep agent/task lineage + manual inheritance as still later. Draft file linked above is the current text — not already amended.

## Acceptance criteria

1. Given an agent run whose prompt texts contain two `{$BASE_RESUME}` (or any same artifact-typed token twice) and no other artifact tokens, the harvested list is exactly one UUID — the candidate’s then-current `candidate.artifacts.base_resume` `artifact_uuid` — or `[]` if no current row. Fail: two identical UUIDs in the list, or a UUID that is not the current row’s id at harvest time.
2. `grep -rn 'source_type.*artifact\\|get_artifact_key_for_token\\|_TOKEN_RE' src/utils/config.py src/core/agent.py` shows harvest classification/parse reuses the typed catalog / existing token regex — not a new hard-coded pinnable-token set. Fail: a parallel allowlist of token names for pin capture.
3. After a consult grading run that saves `{prefix}_grades`, job_data also contains a sibling source-artifact-id array for that prefix/set whose contents equal the harvest for that run (empty list when harvest was empty). Fail: pins only on individual grade objects, or no sibling key when grades were written.
4. After `analysis_upshot` (or meteorite upshot equivalent) persist, the same sibling-array rule holds next to that analysis set. Fail: grades wired but analysis left without a sibling array contract.
5. A generative agent land through `save_candidate_data` (str path) or non-`job_resume` `save_job_artifact` that has a non-empty harvest persists those ids on the new artifacts row’s `source_artifact_ids`. Fail: harvest computed but `source_artifact_ids` stays `[]` on that row when harvest was non-empty.
6. A `job.artifacts.job_resume` generative write still stores only the auto-cited current `base_resume` id (or `[]`), ignoring harvested/caller lists. Fail: harvested extras appear on job_resume sources, or auto-cite removed.
7. No product code lands versioned agent/agent_task lineage columns; no `tokens_ready` claim changes; no new `ARTIFACT_CONFIG` keys; draft traceability gains only the Implementation alignment note (not promoted to active).

## Open questions

none

## Proposed child tickets

#### 1!: **Prompt-token source-pin harvest helper - Ada**

Owns parse + classify + current-uuid resolve + dedupe for one agent run’s prompt texts. Ships a reusable harvest entry point and any candidate current-uuid-by-key helper harvest needs. Does **not** write job_data siblings or change save signatures’ call sites beyond what’s required to unit the helper. Does **not** own consult persist or craft-land wiring (siblings #2 / #3).

**Citations:** `patt.artifact.traceability`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `patt.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.dry-and-focused-functions`; `astral.layers.import-direction`

**Scope:** `src/utils/config.py` — **modified** — reuse existing `_TOKEN_RE` / `TOKEN_SOURCES` / `get_artifact_key_for_token` / by-`source_type` getters; add only what harvest needs that is purely catalog/parse (e.g. list artifact token names referenced by one or more prompt texts). `src/core/agent.py` — **modified** — at prompt-build time in the agent run path, invoke harvest over the run’s prompt texts + candidate scope; expose the deduped list on the run. `src/core/candidate.py` — **modified** — expose or reuse a current-`artifact_uuid`-by-catalog-key resolve for harvest (body-only `get_candidate_current` is not enough). `src/utils/config.py` — Parse helper(s) over prompt text(s) using the existing `{$TOKEN}` regex; filter to `source_type == "artifact"`; map name → `artifact_key`. `src/core/agent.py` — After task prompts are known for the run, harvest artifact pins; attach the deduped list to run context. `src/core/candidate.py` — Current-uuid-by-key helper (catalog key → current row `artifact_uuid` or empty).

**Estimate: 3**

#### 2: **Persist harvested pins on consult grade/analysis writes - Hedy**

After #1: when consult persists `*_grades` / `analysis_upshot` sets via `save_job_data`, write the sibling source-artifact-id array from that run’s harvest next to the set (whole-run array, not per grade line). Does **not** re-own harvest logic. Does **not** thread artifact-table `source_artifact_ids` (sibling #3).

**Citations:** `patt.artifact.traceability`; `patt.artifact.read-operative` (boundary); `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`

**Scope:** `src/core/consult.py` — **modified** — when persisting `*_grades` / `analysis_upshot` (and existing sibling keys) via `tracker.save_job_data`, also write the sibling source-artifact-id array harvested for that run. `src/core/agent.py` — **modified** — only as needed so consult can read the run’s harvest list (no second parse). `src/core/consult.py` — Grade/analysis `save_job_data` payloads gain one sibling key for the harvested array beside `{prefix}_grades` / `analysis_upshot`; empty harvest → empty list.

**Estimate: 2**

#### 3: **Thread harvest into generative artifact-table writes - Katherine**

After #1: agent generative lands pass harvest into `save_job_artifact` / operative `save_candidate_data` → `save_artifact` as `source_artifact_ids`. Extend candidate operative save to accept optional sources. Leave `job.artifacts.job_resume` auto-cite untouched (still ignores caller/harvest lists). Align draft traceability Implementation one-liner. Does **not** own consult job_data siblings (#2).

**Citations:** `patt.artifact.traceability`; `patt.artifact.write-operative`; `patt.artifact.read-current`; `astral.standards.in-scope-only`; `astral.standards.data-raises-caller-logs`; `astral.layers.import-direction`

**Scope:** `src/core/agent.py` — **modified** — on generative `save_job_artifact` / `save_candidate_data` lands from this run, pass the harvest list (except job_resume auto-cite remains authoritative). `src/core/candidate.py` — **modified** — operative `save_candidate_data` str-path accepts and passes optional `source_artifact_ids` through to `database.save_artifact`. `src/core/tracker.py` — **modified** — only if a thin pass-through is required for non-`job_resume` generative writes; do **not** weaken job_resume auto-cite. `canon/directives/draft/patt.artifact.traceability.md` — **modified** — Implementation alignment note for this epic’s surfaces. `src/core/candidate.py` — Operative save accepts optional source ids and forwards them on insert. `src/core/tracker.py` — Touch only if needed; job_resume continues to ignore caller sources. `patt.artifact.traceability.md` — Note this epic implements seed-id capture surfaces; lineage + manual inheritance remain later.

**Estimate: 3**

**Monolith check:** Three functional capabilities → three children (harvest core; consult sibling persist; artifact-table thread). Intentional split so grade explainability can land without waiting on save-signature plumbing, and job_resume auto-cite stays isolated in #3.

**Scope partition check:** config parse helpers + agent harvest attach + candidate uuid helper → #1. consult (+ minimal agent handoff for reading harvest) → #2. agent craft-land pass-through + candidate save sources + optional tracker touch + traceability draft note → #3. No file claimed twice for the same change; tracker only if #3 needs it.

**Dependency note:** Relies on Done [AST-1578](https://linear.app/astralcareermatch/issue/AST-1578) token `source_type` typing, User Testing [AST-1570](https://linear.app/astralcareermatch/issue/AST-1570) read-current, and User Testing [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588) `artifacts.source_artifact_ids` column for the artifact-table persist path. Grade/analysis sibling keys do not require the column. Sibling Backlog [AST-1580](https://linear.app/astralcareermatch/issue/AST-1580) (`tokens_ready`) stays out.

---

## Original brief

## Decision

Answers [AST-1571](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative) Open Question 1 (pin storage shape) — Susan has already answered this directly in [AST-1571](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative)'s description; this ticket is the implementation.

When a prompt is built:

1. The tokens embedded in the prompt text are known (parsed from text, not a hand-maintained shadow list).
2. Each token is resolved against the token catalog (see "split token config" ticket) to determine source type.
3. For tokens typed `artifact`, read-current gives the UUID that will be stored as the operative id for that key — this becomes a source pin.
4. When the agent response is stored as a new derived artifact, the array of then-current artifact ids (one per distinct artifact-type token, **deduped** by artifact_id) is stored with the new artifact record.

## Storage shape

Sibling key next to the grade/analysis set (e.g. next to `*_grades` / `analysis_upshot`), not a per-grade-row field — a shared rubric or resume source applies to the whole grade set from one grading run, not per individual grade line.

## Dedupe rule

Because `current=1` is unique per (entity, artifact_type), two tokens of the same artifact type in one prompt always resolve to the identical UUID — dedupe is a `set()` on the array before write, not resolution logic. Necessary so "what was the base resume source artifact?" doesn't get a "which one?" answer.

## Why this matters

This is the mechanism behind "why did we give this a C" — read-operative ([AST-1571](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative)) later resolves these pins by exact artifact_id, never by re-resolving "current," so edits to a rubric/resume after the fact don't silently rewrite the explanation for old grades.

## Origin

Design discussion in chat, 2026-09-02, following from [AST-1569](https://linear.app/astralcareermatch/issue/AST-1569/implement-pattartifactwrite-operative) (write-operative) and [AST-1571](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative) (read-operative).

### Comments

#### chuckles — 2026-09-17T00:32:44.771Z
AST-1699 REVIEW — merge-child blocked; recalling Hedy for missing plan() label in sub--not-ftr range (plan already on ftr).

#### chuckles — 2026-09-17T00:27:13.048Z
AST-1700 REVIEW — Radia needs resolve on consult.py AST-1699 smuggle.

---

_Implementation detail may live in git history on `origin/dev`._
