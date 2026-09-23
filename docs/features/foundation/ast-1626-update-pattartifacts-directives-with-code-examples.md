# AST-1626 — update patt.artifacts.* directives with code examples

<!-- linear-archive: AST-1626 archived 2026-09-22 -->

## Linear archive (AST-1626)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1626/update-pattartifacts-directives-with-code-examples  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 3  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572

### Description

## Purpose

The artifact pattern drafts under `canon/directives/draft/` already state the law (Abstract / Arc / Applications / Exceptions / Implementation), and the Foundation implement wave (manage-catalog → write/read-operative → read-current → ui-consistency) has landed live call sites that follow that law. This epic makes each in-scope draft **teach the how** by adding concrete code examples harvested from those live paths, so plan/build/review agents stop guessing API shape from prose alone. Outcome: an engineer citing a `patt.artifact.*` draft can copy a correct invoke pattern without inventing helpers or reopening blob/coat-check paths. Plural ids (`patt.artifacts.*`) are renamed to singular `patt.artifact.*` to match the `artifacts` table and component naming.

## Functional scope

1. **Example enrichment** — Each in-scope draft directive gains worked code examples (fenced snippets + short call-site pointers) that show the correct implement shape for that pattern.
2. **Harvest from live code** — Examples come from existing pilot paths already on `origin/dev` (catalog resolve, operative write/read-current/read-operative, ui `bodyShape` editor). Do not invent new public APIs or alternate helper names in the drafts.
3. **Law unchanged** — Abstract, Arc, Applications, Exceptions, and normative Implementation rules stay authoritative. Examples illustrate those rules; they do not add new requirements, exceptions, or grandfather legacy blob/coat-check behavior.
4. **Singular rename** — Rename draft ids/paths `patt.artifacts.ui-consistency` and `patt.artifacts.traceability` to `patt.artifact.ui-consistency` and `patt.artifact.traceability` (file rename + frontmatter `id`), and update in-repo cites that point at the old plural paths for those two drafts only.
5. **Docs-only** — No product/runtime code, no test-tree changes, no draft→`active/` promotion, and no new pattern ids beyond the singular rename. Promotion (if wanted) is a separate Archie decision outside this epic.

## Component scope

* `canon/directives/draft/patt.artifact.manage-catalog.md` — **modified** — add worked examples for catalog register/lookup using the live config + helper path.
* `canon/directives/draft/patt.artifact.write-operative.md` — **modified** — add worked examples for retire+insert write via data-layer + entity-owned save.
* `canon/directives/draft/patt.artifact.read-current.md` — **modified** — add worked examples for current-row load (data-layer + entity wrapper + API/UI hydrate boundary).
* `canon/directives/draft/patt.artifact.read-operative.md` — **modified** — add worked examples for pin→body fetch by artifact uuid / scoped operative read.
* `canon/directives/draft/patt.artifact.no-coat-check.md` — **modified** — add worked forbidden vs required examples (lazy blob fetch vs pre-ingest / artifact read) drawn from live correct paths; no new ban surfaces.
* `canon/directives/draft/patt.artifacts.ui-consistency.md` — **deleted** — renamed to singular id path below.
* `canon/directives/draft/patt.artifact.ui-consistency.md` — **new** (rename from plural) — same body + worked examples for `bodyShape`-parameterized editor + leaf save/reload; frontmatter `id: patt.artifact.ui-consistency`.
* `canon/directives/draft/patt.artifacts.traceability.md` — **deleted** — renamed to singular id path below.
* `canon/directives/draft/patt.artifact.traceability.md` — **new** (rename from plural) — same body + worked examples for provenance fields that already exist on the live write path; frontmatter `id: patt.artifact.traceability`; mark still-unimplemented lineage as illustrative.

## Technical scope

* `patt.artifact.manage-catalog.md` — New Examples (or Implementation subsection) showing catalog entry resolve for a registered key and rejection of unknown keys via the live catalog/config accessors — no key inventory dump beyond what an example snippet needs.
* `patt.artifact.write-operative.md` — New examples showing data-layer `save_artifact` retire+insert and the entity-owned operative save that validates body shape then delegates — return uuid/pin called out in the snippet comments.
* `patt.artifact.read-current.md` — New examples showing `get_current_artifact` and the entity-owned current-read wrapper used by GET hydrate / editor load.
* `patt.artifact.read-operative.md` — New examples showing by-uuid `get_artifact` (or equivalent) and the pilot pin→body helper used for explainability / Contact-style operative resolve.
* `patt.artifact.no-coat-check.md` — New examples contrasting a forbidden mid-turn blob/coat-check style call with the required pre-load + read-current/read-operative sequence.
* `patt.artifact.ui-consistency.md` — Rename from `patt.artifacts.ui-consistency.md`; update frontmatter id; add examples showing page pass of `bodyShape` into shared `ArtifactEditor` and leaf artifacts PUT/GET for the pilot shape — no new frontend catalog fetch.
* `patt.artifact.traceability.md` — Rename from `patt.artifacts.traceability.md`; update frontmatter id; add examples showing how a generative write records seed artifact ids on the new row when the live column/kwarg exists; explicitly label any agent/task lineage still draft-only.
* In-repo cite sweep for those two renames — update docs/features, test-bible, and other draft/code comments that hard-path the old plural filenames (docs cites only; no product behavior change).

## Architectural definition

**Patterns to reuse**

* `patt.artifact.manage-catalog` — this epic documents the live register/lookup shape; does not change the process. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — examples must show retire+insert write, not in-place UPDATE. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — examples must show current-row load for edit/live display. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — examples must show pin→body (or scoped operative) fetch, not blob dotted-path reads. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.no-coat-check` — examples must reinforce ban on lazy fetch-if-missing. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.no-coat-check.md>)
* `patt.artifact.ui-consistency` (rename from `patt.artifacts.ui-consistency`) — examples must show body_shape-driven shared editor path. [current plural draft until rename lands](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifacts.ui-consistency.md>)
* `patt.artifact.traceability` (rename from `patt.artifacts.traceability`) — examples must not over-claim product wire still deferred. [current plural draft until rename lands](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifacts.traceability.md>)

**New patterns proposed**

* none — rename only; no new pattern shape.

**Applicable statutes**

* `astral.standards.in-scope-only` — docs-only epic; no product/test tree edits. [in-scope-only](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.standards.names-not-ticket-ids` — example snippets name symbols/paths, not ticket ids as runtime identifiers (ticket cites in draft prose already present may stay; new example code does not invent ticket-named APIs). [names-not-ticket-ids](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.names-not-ticket-ids.md>)
* `astral.config.config-source-of-truth` — catalog examples resolve through config/catalog SoT, not hardcoded key tuples in consumer prose. [config-source-of-truth](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)

## Acceptance criteria

1. **Examples present** — For every kept draft under Component scope, ```` rg -n '```' canon/directives/draft/patt.artifact.*.md ```` shows at least one fenced code block under that file’s Examples / Implementation examples subsection. Fail: any in-scope draft has zero fenced example blocks after the change.
2. **Live symbols only** — Every example call names a symbol that exists on `origin/dev` under `src/` (e.g. `save_artifact`, `get_current_artifact`, `get_artifact`, `save_candidate_data`, `get_candidate_current`, `get_operative_base_resume`, or the editor `bodyShape` prop). Fail: `rg` for an example-named function/path returns no definition under `src/`, or the snippet invents a helper not in tree.
3. **No product diff** — `git diff origin/dev -- src/ tests/` is empty on the publish ref for this epic. Fail: any `src/` or `tests/` file appears in the epic’s product diff.
4. **Law sections intact** — Abstract / Arc / Applications / Exceptions headings remain; normative Implementation rules are not deleted or replaced by examples-only text. Fail: a draft loses one of those section headings, or Examples become the only remaining guidance.
5. **Wrong-shape ruled out** — Each write/read draft’s examples include a one-line “do not” adjacent to the positive snippet (no in-place artifact UPDATE; no `*_data` blob read for catalog keys; no mid-turn coat-check). Fail: positive example only, with no greppable negative guidance in that file’s new example block.
6. **Stay draft + singular ids** — Files remain under `canon/directives/draft/`; `patt.artifacts.ui-consistency.md` and `patt.artifacts.traceability.md` are gone; singular replacements exist with matching frontmatter ids. Fail: plural paths still present, or singular ids missing.

## Open questions

none

## Proposed child tickets

#### 1!: *Core patt.artifact.* example enrichment - Ada*

Add harvested code examples to the five singular drafts (`manage-catalog`, `write-operative`, `read-current`, `read-operative`, `no-coat-check`). Does **not** own the ui-consistency / traceability rename+examples (child #2). Docs-only; no product code; no draft promotion.

**Citations:** `patt.artifact.manage-catalog`; `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.read-operative`; `patt.artifact.no-coat-check`; `astral.standards.in-scope-only`; `astral.config.config-source-of-truth`

**Scope:**

* `canon/directives/draft/patt.artifact.manage-catalog.md` — **modified** — add worked examples for catalog register/lookup using the live config + helper path.
* `canon/directives/draft/patt.artifact.write-operative.md` — **modified** — add worked examples for retire+insert write via data-layer + entity-owned save.
* `canon/directives/draft/patt.artifact.read-current.md` — **modified** — add worked examples for current-row load (data-layer + entity wrapper + API/UI hydrate boundary).
* `canon/directives/draft/patt.artifact.read-operative.md` — **modified** — add worked examples for pin→body fetch by artifact uuid / scoped operative read.
* `canon/directives/draft/patt.artifact.no-coat-check.md` — **modified** — add worked forbidden vs required examples (lazy blob fetch vs pre-ingest / artifact read) drawn from live correct paths; no new ban surfaces.
* `patt.artifact.manage-catalog.md` — New Examples (or Implementation subsection) showing catalog entry resolve for a registered key and rejection of unknown keys via the live catalog/config accessors — no key inventory dump beyond what an example snippet needs.
* `patt.artifact.write-operative.md` — New examples showing data-layer `save_artifact` retire+insert and the entity-owned operative save that validates body shape then delegates — return uuid/pin called out in the snippet comments.
* `patt.artifact.read-current.md` — New examples showing `get_current_artifact` and the entity-owned current-read wrapper used by GET hydrate / editor load.
* `patt.artifact.read-operative.md` — New examples showing by-uuid `get_artifact` (or equivalent) and the pilot pin→body helper used for explainability / Contact-style operative resolve.
* `patt.artifact.no-coat-check.md` — New examples contrasting a forbidden mid-turn blob/coat-check style call with the required pre-load + read-current/read-operative sequence.

**Estimate: 3**

#### 2: **Rename plural drafts + example enrichment - Ada**

After #1: rename `patt.artifacts.ui-consistency` / `patt.artifacts.traceability` → singular `patt.artifact.*` (paths + frontmatter ids), add harvested examples, and sweep in-repo cites of the old plural paths. Does **not** re-edit the five core drafts. Docs-only; no product code; no draft promotion.

**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.traceability`; `astral.standards.in-scope-only`; `astral.standards.names-not-ticket-ids`

**Scope:**

* `canon/directives/draft/patt.artifacts.ui-consistency.md` — **deleted** — renamed to singular id path.
* `canon/directives/draft/patt.artifact.ui-consistency.md` — **new** (rename from plural) — same body + worked examples for `bodyShape`-parameterized editor + leaf save/reload; frontmatter `id: patt.artifact.ui-consistency`.
* `canon/directives/draft/patt.artifacts.traceability.md` — **deleted** — renamed to singular id path.
* `canon/directives/draft/patt.artifact.traceability.md` — **new** (rename from plural) — same body + worked examples for provenance fields that already exist on the live write path; frontmatter `id: patt.artifact.traceability`; mark still-unimplemented lineage as illustrative.
* `patt.artifact.ui-consistency.md` — Rename from `patt.artifacts.ui-consistency.md`; update frontmatter id; add examples showing page pass of `bodyShape` into shared `ArtifactEditor` and leaf artifacts PUT/GET for the pilot shape — no new frontend catalog fetch.
* `patt.artifact.traceability.md` — Rename from `patt.artifacts.traceability.md`; update frontmatter id; add examples showing how a generative write records seed artifact ids on the new row when the live column/kwarg exists; explicitly label any agent/task lineage still draft-only.
* In-repo cite sweep for those two renames — update docs/features, test-bible, and other draft/code comments that hard-path the old plural filenames (docs cites only; no product behavior change).

**Estimate: 2**

---

## Original brief

Now that we have live code that uses the artifact pattern correctly, let's be explicit in the pattern file to explain how to implement the pattern.

### Comments

#### chuckles — 2026-09-10T20:55:13.757Z
AST-1628 REVIEW — merge-child blocked; recalling Ada for pull-merge commit on sub (need sync(ftr) message, not Merge remote-tracking).

#### chuckles — 2026-09-10T20:11:22.208Z
@susan

1. Confirm the file set: keep **all seven** drafts listed in Component scope (`patt.artifact.*` five + `patt.artifacts.*` two), or narrow to (a) **only** the plural `patt.artifacts.*` named in the title, or (b) only patterns whose implement parents are already User Testing — dropping or deferring `patt.artifact.no-coat-check` (AST-1572 still Discussion) and/or `patt.artifacts.traceability` (lineage still mostly draft)?

---

_Implementation detail may live in git history on `origin/dev`._
