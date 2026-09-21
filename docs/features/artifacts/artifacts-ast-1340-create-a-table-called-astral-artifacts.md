# AST-1340 — Create a table called astral_artifacts
**Component:** artifacts  
**Children:** AST-1352, AST-1353, AST-1364  
**Linear archived:** AST-1340 2026-08-31; AST-1352 2026-08-31; AST-1353 2026-08-31; AST-1364 2026-08-31

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-12 16:58 | AST-1352 | docs | `d5137e658` | docs(AST-1352): plan — astral_artifacts table and current-flag writers |
| 2026-08-12 17:00 | AST-1352 | docs | `933ae0a06` | docs(AST-1352): Joan validate — APPROVED |
| 2026-08-12 17:03 | AST-1352 | code | `294e76fac` | code(AST-1352): astral_artifacts table and current-flag writers |
| 2026-08-12 17:03 | AST-1352 | docs | `34f2202a5` | docs(AST-1352): Review stub after build |
| 2026-08-12 17:07 | AST-1352 | merge-tests | `74712e64b` | merge-tests(AST-1352): origin/tests 7f7444a722bb9e5c40f4de623c188922c2d685f3 |
| 2026-08-12 17:07 | AST-1352 | test | `7f7444a72` | test(AST-1352): astral_artifacts table and current-flag writer coverage |
| 2026-08-12 17:10 | AST-1352 | docs | `43ea6a5ee` | docs(AST-1352): Radia review — clean |
| 2026-08-12 17:13 | AST-1353 | docs | `cced2c74f` | docs(AST-1353): plan — Save Base Resume writes base_resume snapshot |
| 2026-08-12 17:15 | AST-1353 | docs | `c2eaea18f` | docs(AST-1353): Joan validate — plan APPROVED |
| 2026-08-12 17:16 | AST-1353 | code | `6e5340399` | code(AST-1353): Save Base Resume snapshots astral_artifacts |
| 2026-08-12 17:16 | AST-1353 | docs | `d35402588` | docs(AST-1353): Review stub after build |
| 2026-08-12 17:20 | AST-1353 | test | `b8b8771db` | test(AST-1353): Save Base Resume astral_artifacts snapshot coverage |
| 2026-08-12 17:20 | AST-1353 | merge-tests | `de0e55986` | merge-tests(AST-1353): origin/tests b8b8771dbb168d448bd03fd2a1140ca9483cdc7f |
| 2026-08-12 17:22 | AST-1353 | docs | `fad1e233b` | docs(AST-1353): Radia review — clean |
| 2026-08-14 12:53 | AST-1364 | docs | `55e799ea1` | docs(AST-1364): plan-fix — rename astral_artifacts to artifacts |
| 2026-08-14 12:56 | AST-1364 | test | `508fefafa` / `6cf3d9b55` | test(AST-1364): bug-repro — artifacts rename API surface |
| 2026-08-14 12:57 | AST-1364 | code | `faac53143` | code(AST-1364): rename astral_artifacts table and API to artifacts |
| 2026-08-14 13:01 | AST-1364 | docs | `bba0a29b0` | docs(AST-1364): Radia review-fix — clean rebuild notes |
| 2026-08-14 13:01 | AST-1364 | merge-tests | `d811140dc` | merge-tests(AST-1364): origin/tests 508fefafaffc183024dcb971aea56ca0fc51b03d |
| 2026-08-14 13:56 | AST-1340/1364 | merge-child | `9f3f50224` | merge-child(): refresh-ftr — origin/dev into ftr/AST-1340 (keep AST-1364 bible) |
| 2026-08-14 17:50 | AST-1340 | docs | `c603bc94b` | docs(AST-1340): mirror epic registry Threads |
| 2026-08-31 14:14 | AST-1352 | docs | `364002c97` | docs(AST-1352): archive Linear issue content |
| 2026-08-31 14:14 | AST-1353 | docs | `e433af32a` | docs(AST-1353): archive Linear issue content |
| 2026-08-31 14:14 | AST-1364 | docs | `878a990c6` | docs(AST-1364): archive Linear issue content |
| 2026-08-31 14:18 | AST-1340 | docs | `47d81e7a9` | docs(AST-1340): archive Linear issue content |

_AST-1364's sub-branch was mechanically rebuilt once (contaminated with unrelated "Ideal Day" / AST-1369 history via a `sync(dev)`), documented in its own Review-fix note below. Two rows of cross-ticket noise excluded from the table above: an `advisory` in `docs/features/consult/ast-903-uat-craft-get-json-parse.md` mentioning "unrelated AST-1352 Threads mirror noise" is that ticket's own review commentary, not a commit in this family; a bare-path reference in `docs/features/candidate/ast-1597-artifact-table-rename-and-candidate-id.md` (line 50) cites `astral_artifacts` as a "pre-AST-1364 leftover" migration case it must also handle — a later ticket's own plan text, not an inbound link to retarget, so it is reported here and left untouched._

## Epic — AST-1340
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1340/create-a-table-called-astral-artifacts · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: High / 5 · Blocked by / blocks / related: —_

### Purpose

Operators can lose a carefully authored Base Resume Content blob by clicking Regenerate when they meant Print. Candidate `artifacts.base_resume` alone is not enough as a durable prior copy. This epic adds a versioned `astral_artifacts` store (same current-flag discipline as agent-task edits) and writes the saved `base_resume` artifact into it on Save Base Resume so the last intentional save remains recoverable even if the live candidate blob is overwritten.

### Functional scope

* The product can store versioned artifact rows in a table named `astral_artifacts`, with entity identity (`entity_type`, `entity_id`), `artifact_type`, an artifact blob, a current flag, and the usual row identity / timestamps.
* When an operator successfully saves Base Resume Content for a candidate, the product also records that candidate's `artifacts.base_resume` payload into `astral_artifacts` as `artifact_type` `base_resume` with `current = 1`, retiring any prior current row for the same entity + artifact type the way agent-task edits do.
* Prior (non-current) rows for that entity + artifact type remain in the table so a saved version is still preserved after a later overwrite of the live candidate artifact.
* This epic does not add UI to browse, restore, or print from `astral_artifacts`; preservation on Save is the deliverable.

### Architectural definition

* **Patterns to reuse** — `pattern.layers.import-discipline` (data-layer table + writers; core orchestrates Save; UI does not call data). No approved catalog pattern yet encodes the agent-task / rubric_vector `current=1` retire-and-insert versioning shape; this epic must follow that established product discipline without inventing a second versioning model.
* **New patterns proposed** — `pattern.data.versioned-current-row` (working name): versioned rows keyed by natural identity with exactly one `current=1` active row per key, retire prior on write, retain history. Proposed because `astral_artifacts` generalizes the agent_task / rubric_vector current-flag approach to entity-scoped artifact blobs. Flag for Archie approval before later epics depend on the catalog id. **(Remained undrafted through the life of this epic — see each child's review below.)**
* **Applicable statutes** — `astral.standards.database-header-inventory`; `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line`; `astral.standards.in-scope-only`; `astral.standards.data-raises-caller-logs`; `astral.standards.no-cross-contamination`; `astral.docs.features-single-file-per-ticket`.

### Boundaries

* Does **not** wire Print, Regenerate, Generate, or any Artifacts UI to read or restore from `astral_artifacts` (Print remains AST-1314 / AST-1337).
* Does **not** change job-tailored resume / cover / suggested-response persistence, `agent_data`, or rubric_vector.
* Does **not** backfill historical `artifacts.base_resume` values into `astral_artifacts` for candidates who never Save after this ships — preservation starts at the next successful Save Base Resume.
* Does **not** make `astral_artifacts` the live editor source of truth; `candidate_data.artifacts.base_resume` remains what the Base Resume Content page reads and edits.
* Does **not** write `astral_artifacts` on craft hops / Generate / Regenerate — only on Save Base Resume for this epic.
* Must not break existing Base Resume Content save/load or Print-from-saved-content behavior.

### Acceptance criteria

1. Fresh and migrated databases expose an `astral_artifacts` table with entity identity, artifact type, artifact blob, current flag, UUID primary key, and created/updated timestamps, and the table is listed in the data-layer header inventory.
2. After a successful Save Base Resume for a candidate, exactly one `current = 1` row exists for that candidate + `artifact_type` `base_resume`, and its blob matches the saved `artifacts.base_resume` content.
3. A second successful Save for the same candidate retires the previous current row (`current = 0`) and inserts a new `current = 1` row; the retired row remains queryable in the table.
4. Overwriting live `artifacts.base_resume` without going through Save Base Resume (e.g. Regenerate) does not by itself clear or replace the last `current = 1` `astral_artifacts` row from the prior Save.
5. No new Artifacts UI controls are required to demonstrate the above (DB / API-level verification is enough for UAT of this epic).

### Dependencies and blockers

none. Adjacent Print epic AST-1314 / AST-1337 is User Testing and is not a blocker; this epic must not reopen Print wiring.

### Open questions

none

### Proposed child tickets

**1!: astral_artifacts table and current-flag writers — Ada** — Owns creating `astral_artifacts` (ensure/migrate), header inventory update, and data-layer save/read helpers that retire prior `current=1` and insert the new current row for a given entity + artifact type — matching agent-task edit versioning. Does **not** wire Save Base Resume (child 2).
**Citations:** `pattern.layers.import-discipline`; proposed `pattern.data.versioned-current-row`; `astral.standards.database-header-inventory`; `astral.layers.import-direction`; `astral.standards.data-raises-caller-logs`
**Estimate: 5**

**2: Save Base Resume writes base_resume snapshot — Katherine** — Owns calling the child-1 writer from the existing successful Save Base Resume path so `artifacts.base_resume` is recorded with `current = 1` for the candidate. Does **not** add restore/Print UI or change Generate/Regenerate writers. After #1.
**Citations:** `pattern.layers.import-discipline`; `astral.standards.in-scope-only`; `astral.layers.import-direction`
**Estimate: 2**

**New patterns:** Child 1 introduces the versioned current-row shape for `astral_artifacts`; downstream artifact types may reuse it once Archie approves the catalog entry.

**Monolith check:** Functional scope has 4 capability bullets; 2 children split schema/versioning vs Save wire — intentional, not a single mega-ticket.

### Original brief

Add a table with entity_type, entity_id, artifact_type, and a blob for the artifact, with a current flag, and the usual UUID, created_at, etc. Then, for Save Base Resume, save the artifacts.base_resume artifact type to that table wit the current flag = 1, as we do for editing agent tasks. No need to wire it into the UI, I just want to know we are preserving it in case the candidate accidentally clicks Regenerate instead of Print.

#### Comments

##### susan — 2026-08-14T18:22:11.364Z
\[bug\] So sorry, Chuckles! I meant for the table to be named "artifacts", not "astral_artifacts" because we don't have that prefix for job or company, etc.

### Files changed (plan vs actual)

_No direct product commit trail on the parent — the epic worktree only carries the `merge-child()` refresh-ftr commit and the epic-registry Threads mirror / `docs(AST-1340)` archive commits. Implementation landed entirely via the two proposed children below, plus the AST-1364 rename UAT bug filed after Susan's naming correction._

## Sub-issues

### AST-1352 — astral_artifacts table and current-flag writers
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1352/astral-artifacts-table-and-current-flag-writers-create-a-table-called · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / 5 · Blocked by / blocks / related: parent: AST-1340; blocks: AST-1353_

#### What this implements

Owns creating `astral_artifacts` (ensure/migrate), header inventory update, and data-layer save/read helpers that retire prior `current=1` and insert the new current row for a given entity + artifact type — matching agent-task edit versioning. Does **not** wire Save Base Resume (sibling).

#### Acceptance criteria

- [X] 1. Fresh and migrated databases expose an `astral_artifacts` table with entity identity, artifact type, artifact blob, current flag, UUID primary key, and created/updated timestamps, and the table is listed in the data-layer header inventory.
- [X] 2. After a successful Save Base Resume for a candidate, exactly one `current = 1` row exists for that candidate + `artifact_type` `base_resume`, and its blob matches the saved `artifacts.base_resume` content. *(Satisfied jointly with sibling once Save is wired; this child delivers the table + writers that make that row possible.)*
- [X] 3. A second successful Save for the same candidate retires the previous current row (`current = 0`) and inserts a new `current = 1` row; the retired row remains queryable in the table. *(Writer semantics owned here.)*

#### Boundaries

Does not wire Save Base Resume / Generate / Regenerate / Print UI. Does not change `candidate_data.artifacts.base_resume` as the live editor source of truth.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory bullet; `_astral_artifacts_schema_ensured`; `_ensure_astral_artifacts_table`; `save_astral_artifact`; `get_current_astral_artifact`; `list_astral_artifacts` | data |

**Do not touch:** `src/core/**`, `src/ui/**`, `src/utils/config.py`, `src/external/**`, Save Base Resume call sites, `candidate_data.artifacts.base_resume` writers/readers, canon pattern catalog files (proposed `pattern.data.versioned-current-row` is flagged for Archie on the parent — do not invent a catalog entry here).

#### Stage 1 & 2 — Table + current-flag writers

New table `astral_artifacts`: `astral_artifact_uuid TEXT PRIMARY KEY`, `entity_type`/`entity_id`/`artifact_type`/`artifact_data TEXT NOT NULL`, `current INTEGER NOT NULL DEFAULT 1`, `created_at`/`updated_at`; index `idx_astral_artifacts_entity_type_current` on `(entity_type, entity_id, artifact_type, current)`. `save_astral_artifact(entity_type, entity_id, artifact_type, artifact_data) -> str`: validates identity fields non-empty and `entity_type` against `ENTITY_TYPES`; normalizes `artifact_data` (string as-is, else `json.dumps`); retires prior current row via `UPDATE … SET current=0 … WHERE … AND current=1` (natural-key retire, not UUID lookup-first); always inserts a fresh UUID row even when the payload is byte-identical to the prior current (no fingerprint short-circuit, unlike rubric_vector); returns the new UUID. `get_current_astral_artifact` / `list_astral_artifacts(..., current_only=False)` round out the read side, ordered `created_at ASC` for stable history.

⚠️ **Decision:** PK name `astral_artifact_uuid` (not bare `id`) — matches `rubric_vector_uuid` / `task_key_uuid` style. ⚠️ **Decision:** Blob column is `artifact_data TEXT NOT NULL` (JSON text) — no zlib compression (that pattern is `agent_data.block_data` only). ⚠️ **Decision:** Do not register in `ALLOWED_CONFIG_TABLES` or config-upsert maps — this is not a Copy Output table. ⚠️ **Decision:** Retire by natural key with `UPDATE … WHERE … AND current=1`, not UUID lookup first — guarantees at most one current row even if a prior bug left duplicates. ⚠️ **Decision:** Always insert a new UUID row on save, even on byte-identical payload — matches agent_task's intentional-Save-snapshot versioning; no fingerprint short-circuit.

#### Plan review — Joan (plan-rubric.v1, APPROVED)

**acceptable** — no formal Scope/Conf/Risk self-assessment block, only an Estimate confirm; acceptable for this narrow data-layer-only footprint. **discuss** — the proposed `pattern.data.versioned-current-row` catalog entry is still undrafted (parent already flags Archie); plan correctly refuses to invent the pattern file here. **acceptable** — retire-by-natural-key vs UUID-first lookup is a sound, documented decision (duplicate-current safety).

#### Radia review — code-rubric.v1, CLEAN

Full 64-statute sweep (product commit `294e76fa`, `database.py` only, +175): all conforms/not-applicable, no violations. Plan adherence confirmed stage-by-stage including exact column set, index name, header inventory placement, no `ALLOWED_CONFIG_TABLES` registration, natural-key retire, always-insert-new-UUID, JSON read/write round-trip with raw-string fallback on decode failure.

**Advisory (not blocking):** the parent's proposed `pattern.data.versioned-current-row` catalog entry remains undrafted — implementation shape matches the intended idiom (`rubric_vector`/`agent_task` precedents in-file), but Archie/parent still owns the catalog harvest before downstream reuse citations. **Advisory:** no partial-unique-index hardening at the DB level against duplicate `current=1` rows — the retire `UPDATE` heals on save per plan decision; `get_current_astral_artifact` uses `LIMIT 1` if duplicates somehow exist pre-save — acceptable, optional hardening left for a future ticket if desired.

**What's solid:** clean one-file, one-commit engineer footprint; retire-by-natural-key semantics match plan decision and parent "exactly one current=1" intent; Betty coverage maps 1:1 to plan branches (ensure, round-trip, history, identical-payload new UUID, validation, string/JSON-text edge cases).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | Header inventory + ensure-table + `save_astral_artifact`/`get_current_astral_artifact`/`list_astral_artifacts` | `294e76fac` — +175 |
| | _tests_ | astral_artifacts table + current-flag writer coverage | `7f7444a72`; bible per Betty manifest |

### AST-1353 — Save Base Resume writes base_resume snapshot
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1353/save-base-resume-writes-base-resume-snapshot-create-a-table-called · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1340_

#### What this implements

Owns calling the sibling's `astral_artifacts` writer from the existing successful Save Base Resume path so `artifacts.base_resume` is recorded with `current = 1` for the candidate. Does **not** add restore/Print UI or change Generate/Regenerate writers. After the table/writer sibling.

#### Acceptance criteria

- [X] 2. After a successful Save Base Resume for a candidate, exactly one `current = 1` row exists for that candidate + `artifact_type` `base_resume`, and its blob matches the saved `artifacts.base_resume` content.
- [X] 3. A second successful Save for the same candidate retires the previous current row (`current = 0`) and inserts a new `current = 1` row; the retired row remains queryable in the table.
- [X] 4. Overwriting live `artifacts.base_resume` without going through Save Base Resume (e.g. Regenerate) does not by itself clear or replace the last `current = 1` `astral_artifacts` row from the prior Save.
- [X] 5. No new Artifacts UI controls are required to demonstrate the above (DB / API-level verification is enough for UAT of this epic).

#### Boundaries

Does not create the table or versioning helpers (sibling). Does not wire Print/Regenerate/Generate to read or restore from `astral_artifacts`. Does not backfill historical base_resume rows.

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `snapshot_saved_base_resume_astral_artifact`; extend module In-scope line | core |
| `src/ui/api/api_candidate.py` | After successful `save_candidate_data` when the PUT included `artifacts.base_resume`, call the new core helper | ui |

#### Stage 1 — Core snapshot helper + Save Base Resume wire

`snapshot_saved_base_resume_astral_artifact(candidate_id)`: re-reads the candidate via `database.get_candidate` (**not** the pre-save PUT payload — `save_candidate` deep-merges, so AC2 requires matching the saved live blob), raises if the candidate or `artifacts.base_resume` is missing after save, then calls `database.save_astral_artifact("candidate", candidate_id, "base_resume", base)`. Wired only from the `update_candidate_data` API handler, immediately after a successful `save_candidate_data` call whose body included `artifacts.base_resume` — not from `save_candidate_data` itself and not from craft/Generate writers that call `database.save_candidate` directly, so Regenerate cannot silently replace the last intentional Save snapshot. Snapshot failures are **not** caught separately — they fall through the existing `except Exception` → 400 JSON, so a failed preserve surfaces as a failed Save response rather than a silent drop.

⚠️ **Decision:** Snapshot after live persist and re-read, not the PUT fragment — AC2 needs the deep-merged result. ⚠️ **Decision:** Call only from the Save Base Resume API path — parent AC4/Boundaries. ⚠️ **Decision:** Artifact type string is the literal `"base_resume"` — no new config block for a single epic-scoped type.

#### Plan review — Joan (plan-rubric.v1, APPROVED)

**discuss** — `ArtifactEditor`'s debounced autosave uses the same PUT with `artifacts.base_resume`, so every successful autosave snapshots (and retires prior), not only explicit Save clicks — plan explicitly names Save/autosave as intentional; operators may accumulate more history rows than manual Save alone implies. No plan change required unless product later wants explicit-Save-only snapshots. **discuss** — a snapshot failure after a successful live persist returns 400 while `candidate_data` is already committed (no cross-table transaction) — a reasonable fail-closed surface for this epic, flagged as a partial-persist edge case for UAT rather than a silent drop. **acceptable** — literal `"base_resume"`/`"candidate"` strings are an acceptable epic-scoped contract; no new config block, `ENTITY_TYPES` validation stays in the data layer.

#### Radia review — code-rubric.v1, CLEAN

Full 64-statute sweep (product commit `6e534039`, two files, +30/-1): all conforms/not-applicable, no violations. Plan adherence: core helper matches the literal implementation spec; `base_resume_in_save` flag set inside the existing ingest/filter gate; snapshot call sits immediately after the successful persist with no separate catch; boundaries verified by tests confirming craft/Generate paths (`run_candidate_artifact_generation`, direct `save_candidate`) never call the snapshot helper.

**What's solid:** exactly two files touched for estimate 2; post-persist re-read correctly satisfies AC2 (deep-merged blob, not just the PUT fragment); AC4 boundary tested at both core and API layers; existing mocked PUT tests revised to stub the snapshot call so mocking `save_candidate_data` elsewhere doesn't regress; Betty manifest covers core helper, API wire, AC4, and the sibling writer.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/candidate.py` | `snapshot_saved_base_resume_astral_artifact` helper | `6e5340399` (with `api_candidate.py`) — +25/-1 |
| ✓ | `src/ui/api/api_candidate.py` | Wire snapshot call after successful Save PUT | `6e5340399` — see above, total +30/-1 |
| | _tests_ | Save Base Resume astral_artifacts snapshot coverage | `b8b8771db`; bible per Betty manifest |

### AST-1364 — Rename astral_artifacts table to artifacts
_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1364/rename-astral-artifacts-table-to-artifacts-create-a-table-called · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1340_

#### Susan comment (verbatim)

[bug] So sorry, Chuckles! I meant for the table to be named "artifacts", not "astral_artifacts" because we don't have that prefix for job or company, etc.

#### As-is

The versioned artifact store table (and its ensure/helpers/public writers) is named `astral_artifacts` / `*_astral_artifact*`, unlike entity tables such as `job` and `company` which have no `astral_` table-name prefix.

#### To-be

The SQLite table is named `artifacts`. Ensure helpers, schema flag, index, PK column, and public/data/core call sites use the same unprefixed naming so Save Base Resume still snapshots into this table with identical current-flag semantics.

#### Root cause

AST-1352 named the new table `astral_artifacts` (and mirrored that prefix into PK / API / core helper names). Product naming intent was the short table name `artifacts`, consistent with other entity tables.

#### Proposed change

Scope is rename only — same columns (except PK name), same retire-and-insert behavior, same Save wire. Do not change `candidate_data.artifacts.base_resume` (unrelated JSON path). Do not invent restore/Print UI.

⚠️ **Decision:** Drop the `astral_` prefix from the table, PK column, index, schema flag, ensure/helper names, and public writer/reader names, and update AST-1353 call sites to match — keeping `save_astral_artifact` while renaming only the SQL table would leave a permanent mismatch and force dual vocabulary in core/UI comments.

`_ensure_artifacts_table(conn)` handles three cases in order: table `artifacts` already exists (ensure the index, rename the PK column if it's still `astral_artifact_uuid`); table `astral_artifacts` exists (pre-rename DBs from AST-1352 UAT) — `ALTER TABLE … RENAME TO artifacts`, rename the PK column, drop the old index name, create the new one; neither exists — `CREATE TABLE artifacts` fresh with the renamed column set. Private helpers renamed (`_normalize_astral_artifact_identity` → `_normalize_artifact_identity`, `_astral_artifact_row_dict` → `_artifact_row_dict`, `_ASTRAL_ARTIFACT_SELECT` → `_ARTIFACT_SELECT`). Public API renamed with no dual aliases: `save_astral_artifact` → `save_artifact`, `get_current_astral_artifact` → `get_current_artifact`, `list_astral_artifacts` → `list_artifacts`. Core's `snapshot_saved_base_resume_astral_artifact` → `snapshot_saved_base_resume_artifact`, calling `database.save_artifact(...)`. `api_candidate.py`'s import/call and its AST-1353 comment updated to match. The plan instructed a full `src/**` grep for every remaining legacy symbol/name before Code Complete, explicitly leaving `tests/`/`docs/test-bible/` fixes for Betty after fix-board.

#### Blast radius

AST-1352's writers (`database.py`) are the primary rename surface. AST-1353's Save wire (`candidate.py` snapshot helper, `api_candidate.py` PUT path) must call the renamed public API or Save snapshots break — the sibling's own plan doc still documented the old names at the time of this fix; the product rename is owned here and does not rewrite that sibling plan's stages. Betty's component tests/bible needed a matching symbol/table-string update (flagged fix-board TESTS: REVISE, not fixed by the engineer). Existing local/staging DBs that already created `astral_artifacts` are covered by the RENAME path — no data loss of prior current/history rows.

#### Board review — Joan CANON: OK / Betty TESTS: REVISE

Joan: no active statute or approved pattern codifies the `astral_artifacts` table/API names; the patch updates `database.py` header inventory per `astral.standards.database-header-inventory` (conforming, no statute text change); `astral.debug.no-repo-root-artifacts-dir` governs repo-root filesystem paths, not this SQLite table name; the still-undrafted `pattern.data.versioned-current-row` has nothing to amend since it was never cataloged. Betty: flagged that `TestAst1352AstralArtifacts` / `TestAst1353*` / the conftest `_astral_artifacts_schema_ensured` reset still called the pre-rename symbols and would `AttributeError` until retargeted.

#### Radia review-fix — REVIEW → Chuckles rebuild, then PROCEED

**fix-now (Chuckles mechanical — done):** the publish ref had been contaminated with unrelated "Ideal Day" / AST-1369 history via a `sync(dev)`. Rebuilt `origin/sub/AST-1340/AST-1364-…` from `origin/ftr/AST-1340-…`, cherry-picking only this ticket's `docs()`/`test()`/`merge-tests()`/`code()` commits. **Product:** PROCEED after the clean rebuild — table/API rename confirmed; Betty's bug-repro pins the unprefixed public API. **Advisory:** the migration path (`RENAME TABLE`) was untested in Betty's repro (fresh-DB only) — UAT should exercise one staging DB that still has `astral_artifacts` to confirm the rename branch, not just the fresh-create branch.

#### What must still hold

Parent AST-1340/AST-1352 AC: exactly one `current=1` row per key after save; second save retires prior and keeps history listable; UUID PK + timestamps; table listed in header inventory (now under `artifacts`). AST-1353 AC: successful Save Base Resume PUT still records live `artifacts.base_resume`; craft/Generate/Regenerate still do not write the store. Data layer still raises (no logging) on bad identity/missing data; `entity_type` still validated against `ENTITY_TYPES`. No UI→data import. No backfill of historical `base_resume` for candidates who never Save.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | Table/column/index/helper/public-API rename with migration path for pre-existing `astral_artifacts` DBs | `faac53143` (with `candidate.py`, `api_candidate.py`) — +135/- across the three files |
| ✓ | `src/core/candidate.py` | `snapshot_saved_base_resume_artifact` rename + `database.save_artifact` call | `faac53143` — +10/- |
| ✓ | `src/ui/api/api_candidate.py` | Import/call + comment update | `faac53143` — +6/- |
| | _tests_ | artifacts rename API surface bug-repro | `508fefafa`/`6cf3d9b55`; bible per Betty flag (TestAst1352/1353 + conftest symbols retargeted) |
