# AST-1677 — Move candidate_data.artifacts.resume_structure to artifact table

<!-- linear-archive: AST-1677 archived 2026-09-24 -->

## Linear archive (AST-1677)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1677/move-candidate-dataartifactsresume-structure-to-artifact-table  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

`candidate_data.artifacts.resume_structure` is still a library blob — the candidate-owned section catalog (ids, titles, enabled/order, `job_agent_editable`, page-break policy, accent) that every job-resume draft filters and prompts against. Sibling `base_resume` already lives on the artifacts table via `ARTIFACT_CONFIG` + write/read-operative; structure was left on the dict-path merge on purpose. This epic moves **resume_structure only** onto that same table path so structure gets versioned `current` rows, and so the interfaces fed into job artifact drafting (`RESUME_SECTION_CATALOG`, draft-section validation, job resume body filter) resolve from table-backed structure instead of blob SoT.

## Functional scope

1. **Catalog resume_structure** — Register `candidate.artifacts.resume_structure` in `ARTIFACT_CONFIG` with a new `body_shape` that names the existing structure dict contract (sections catalog + accent), not `resume_content` and not `plain_text`. No other catalog keys.
2. **Operative write** — Saving structure goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact` blind retire+insert). No in-place library blob UPDATE as SoT.
3. **Current read / hydrate** — GET/UI loads structure via read-current and overlays onto `candidate_data.artifacts.resume_structure` for the existing editor and `/resume_structure` contract. Miss → keep legacy blob until re-save (no coat-check).
4. **Retire blob authority** — Stop durable library-merge writes of `artifacts.resume_structure` as source of truth once the catalog owns the key; dict-path callers must not reintroduce blob SoT.
5. **Craft / parse land** — `craft_resume_base` and `parse_candidate_resume` land structure through the operative key (body still lands on `candidate.artifacts.base_resume` as today).
6. **Job drafting interfaces** — Update the interfaces that feed job artifact drafting so they resolve structure from the table-backed current (via hydrate / `resolve_resume_structure`), including `RESUME_SECTION_CATALOG` assembly, draft-job-resume section-key validation, and job resume content filtering. No parallel blob-only read path for those surfaces.
7. **No legacy backfill** — Do not migrate historical structure blobs in this epic. Existing catalogs stay in the blob until the operator (or craft/parse) re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check. No new craft task. No job/company catalog keys. No React chrome rewrite (Base Resume / JAR / ArtifactEditor keep the leaf slot key `resume_structure` and existing PUT/GET shapes). No change to `base_resume` / context-leaf operative paths except shared strip/hydrate bookkeeping for this key. No bulk migration job.

## Component scope

* `src/utils/config.py` — **modified** — `ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]` plus closed-set asserts; new `BUILD_CONFIG["artifact_shapes"]["resume_structure"]` (or equivalent named shape) for the structure dict contract; Persistence comment / any freeze-absent assert that still treats structure as non-catalog updated.
* `src/core/candidate.py` — **modified** — operative validate/save for the structure shape; hydrate overlay from `get_candidate_current`; gate durable library writes for `artifacts.resume_structure`; retarget craft/parse structure land; keep `resolve_resume_structure` honest against hydrated/current SoT.
* `src/core/agent.py` — **modified** — craft-persist path that today library-saves structure lands structure via operative key (body path unchanged).
* `src/ui/api/api_candidate.py` — **modified** — PUT intercept: pop library `artifacts.resume_structure`, operative save; GET hydrate overlays current structure for detail and `/resume_structure`.
* `src/core/consult.py` — **modified** — `build_job_token_context` / `RESUME_SECTION_CATALOG` assembly reads structure only through resolve/hydrate (no blob-only bypass).
* `src/core/tracker.py` — **modified** — job resume prepare/filter paths that consult structure use the same resolve/hydrate SoT (no blob-only bypass).
* `src/data/database.py` — **untouched** — existing `save_artifact` / `get_current_artifact` only.
* Frontend Base Resume / JAR / ArtifactEditor — **untouched** — leaf key and routes stay; API hydrate/intercept carries the cutover.

## Technical scope

* `src/utils/config.py` — New catalog entry: `entity_type: "candidate"`, `candidate_scoped: True`, `body_shape` naming the new structure shape, `ingestion_owner: "candidate"`. Add the shape under `BUILD_CONFIG["artifact_shapes"]` so startup asserts pass. Closed-set `ARTIFACT_CONFIG` keys include the new key. Do not register job-side structure keys.
* `src/core/candidate.py` — Operative str-path validates structure body (reuse / wrap existing normalize contract — kind of change: modified validation + save path); hydrate writes current structure into `artifacts.resume_structure` for display; refuse durable library SoT write for that leaf when catalog owns it; craft/parse helpers that today `save_candidate_data(..., {"artifacts": {"resume_structure": ...}})` switch to operative save for structure.
* `src/core/agent.py` — On craft land that persists structure + body: structure → operative key; body → existing `candidate.artifacts.base_resume` operative key (kind of change: modified persist branch).
* `src/ui/api/api_candidate.py` — PUT `/data`: pop `resume_structure` from library merge, call operative save; GET detail and GET `/resume_structure` see hydrated current (kind of change: modified intercept + hydrate calls).
* `src/core/consult.py` — `RESUME_SECTION_CATALOG` built from resolve-after-hydrate structure only (kind of change: modified token assembly; keep `TOKEN_SOURCES["RESUME_SECTION_CATALOG"]` as `special_case` unless a later ticket retypes it).
* `src/core/tracker.py` — `_prepare_job_resume_content` / structure filter callers use resolve-after-hydrate (kind of change: modified read path only).

## Architectural definition

**Patterns to reuse** (same artifact family as AST-1569 / AST-1629 — structure is the next `candidate.artifacts.*` leaf after `base_resume`):

* `patt.artifact.manage-catalog` — register `candidate.artifacts.resume_structure`; retire blob authority for that key. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — structure saves via blind retire+insert through entity-owned operative save. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — UI/GET hydrate and live structure from current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — pin→body remains available via generic path (no structure-only pin surface required this epic). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.ui-consistency` — editor keeps existing structure chrome; API contract preserves leaf key (no new React bodyShape fork this epic). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.ui-consistency.md>)

**New patterns proposed:** none — new `artifact_shapes` entry is config shape reuse under manage-catalog, not a new pattern id.

**Applicable statutes:**

* `stat.logging.info` — info contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.warning` — warning contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error` — error contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.debug` — debug contract on any `debug=` surfaces this epic touches. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity` — entity/core info logging when candidate structure paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.api` — API info logging when api_candidate structure paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
* `astral.config.config-source-of-truth` — catalog key, body_shape, and token typing live in config. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — closed catalog / shape membership via config asserts. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — resume_structure only. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — utils/config + core + ui layering. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.git.engineer-test-tree-ban` — engineers do not own `tests/` / bible. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)
* `astral.standards.logging-via-utils` — logging through utils helpers. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)

Note: Artifact `patt.artifact.*` ids remain under `draft/` until promoted; logging `stat.logging.*` are active. Prefer AST-1576 (structure stayed library while body moved) inverted: this epic is the structure half — and AST-1629 / AST-1644 child plans as the operative migration template.

## Acceptance criteria

1. **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.artifacts.resume_structure' in ARTIFACT_CONFIG"` exits 0. Fail: KeyError/AssertionError or key absent.
2. **Body shape is structure, not resume_content/plain_text** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; e=ARTIFACT_CONFIG['candidate.artifacts.resume_structure']; assert e['body_shape'] not in ('resume_content','plain_text','cover_letter'); assert e['body_shape'] in BUILD_CONFIG['artifact_shapes']"` exits 0. Fail: shape reused from body/letter/plain_text or missing from `artifact_shapes`.
3. **Operative round-trip** — After save via operative API/helper, `database.get_current_artifact('candidate', <id>, 'resume_structure')` returns a row whose `artifact_data` matches the saved structure dict; a second distinct save creates a new uuid and retires prior `current=1`. Fail: no row, blob-only write, or in-place UPDATE of the same uuid’s body.
4. **Hydrate on GET** — GET candidate detail (and GET `/api/candidates/<id>/resume_structure`) shows current structure after operative save. Fail: response still serves only pre-save blob and ignores current row.
5. **No durable blob SoT on save** — Successful structure save calls operative `save_artifact`; a post-save library read of raw candidate_data without hydrate is not relied on as SoT (grep of save path: no sole `save_candidate_data(cid, {"artifacts": {"resume_structure": ...}})` as the durable write for this key). Fail: structure persists only via library merge.
6. **Craft/parse land structure operatively** — Successful `craft_resume_base` / `parse_candidate_resume` persist structure through `candidate.artifacts.resume_structure` operative key; body still through `candidate.artifacts.base_resume`. Fail: structure written only to library blob on those paths.
7. **Job drafting interfaces** — With only an artifacts-table current structure (legacy blob empty/missing), `build_job_token_context` still populates non-empty `RESUME_SECTION_CATALOG` from enabled sections, and draft-job-resume section validation / job resume structure filter accept that catalog. Fail: catalog empty or validation/filter still require a library blob and ignore current row.
8. **No backfill** — Candidates with only legacy blob structure and no artifact row still load that blob (or default) until re-save; no bulk migration script ships. Fail: deploy runs a backfill job or clears legacy blob on hydrate miss.
9. **Scope fence** — `rg -n "candidate\\.artifacts\\.resume_structure" src/utils/config.py` shows the registration; no new `job.artifacts.resume_structure` (or other new catalog keys) appear in `ARTIFACT_CONFIG`. Fail: extra keys registered this epic.

## Open questions

none

## Proposed child tickets

#### 1!!: **Catalog + resume_structure body shape - Ada**

Register `candidate.artifacts.resume_structure` in `ARTIFACT_CONFIG` and add the structure dict `body_shape` under `BUILD_CONFIG["artifact_shapes"]` with closed-set asserts. Does not wire operative save/hydrate or job drafting consumers (after this, #2/#3). No React.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`
**Scope:** `src/utils/config.py` — `ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]` plus closed-set asserts; new `BUILD_CONFIG["artifact_shapes"]["resume_structure"]` (or equivalent named shape) for the structure dict contract; Persistence comment / any freeze-absent assert that still treats structure as non-catalog updated.
**Estimate: 2**

#### 2!: **Operative save, hydrate, blob retirement + craft/parse land - Hedy**

Wire structure through candidate operative validation + `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `artifacts.resume_structure`; retarget craft/parse and agent craft-persist structure land to the operative key. No backfill helper. Does not own job drafting token/filter consumers (#3) or React chrome. After #1. Mirror AST-1576’s split (structure half now operative) and AST-1633-style blob retirement.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`
**Scope:** `src/core/candidate.py` — operative validate/save for the structure shape; hydrate overlay from `get_candidate_current`; gate durable library writes for `artifacts.resume_structure`; retarget craft/parse structure land; keep `resolve_resume_structure` honest against hydrated/current SoT. `src/core/agent.py` — craft-persist path that today library-saves structure lands structure via operative key (body path unchanged). `src/ui/api/api_candidate.py` — PUT intercept: pop library `artifacts.resume_structure`, operative save; GET hydrate overlays current structure for detail and `/resume_structure`.
**Estimate: 5**

#### 3: **Job drafting interface rewires - Katherine**

Point job artifact drafting interfaces at table-backed structure: `RESUME_SECTION_CATALOG` assembly in consult, and tracker job-resume prepare/filter paths that read structure — all via resolve/hydrate, no blob-only bypass. Does not own catalog (#1) or operative save/API (#2). After #2.
**Citations:** `patt.artifact.read-current`; `astral.standards.in-scope-only`; `astral.config.config-source-of-truth`
**Scope:** `src/core/consult.py` — `build_job_token_context` / `RESUME_SECTION_CATALOG` assembly reads structure only through resolve/hydrate (no blob-only bypass). `src/core/tracker.py` — job resume prepare/filter paths that consult structure use the same resolve/hydrate SoT (no blob-only bypass).
**Estimate: 3**

**Monolith check:** Functional scope has 7 ship capabilities (+ non-goals); 3 children partition catalog / operative+craft / job-drafting interfaces — not a single mega-ticket.

**Scope partition check:** Every Component/Technical file is claimed once — `config.py` → #1; `candidate.py` + `agent.py` + `api_candidate.py` → #2; `consult.py` + `tracker.py` → #3. Untouched rows (`database.py`, frontend) are explicit non-goals.

---

## Original brief

Make sure to update the interfaces that are sent to the job artifact drafting, etc.

### Comments

#### chuckles — 2026-09-16T22:32:29.352Z
[finish-up] blocked: merge — docs/test-bible/core/agent.md

@Betty White — bible conflict landing `origin/ftr/AST-1677-move-resume-structure-artifact-table` onto `origin/dev`. Reconcile `docs/test-bible/core/agent.md` (union both sides), publish to the ftr tip, then Chuckles will re-run finish-up.

#### chuckles — 2026-09-16T17:01:22.156Z
AST-1678 REVIEW — merge-child blocked; recalling Betty for duplicate merge-tests(AST-1678).

#### chuckles — 2026-09-16T16:57:50.964Z
AST-1678 REVIEW — merge-child blocked; recalling Betty (missing test()) and Ada (restack on refreshed ftr).

#### chuckles — 2026-09-16T16:49:23.700Z
AST-1678 REVIEW — Radia: strip AST-1670 sibling test commits from publish ref.

---

_Implementation detail may live in git history on `origin/dev`._
