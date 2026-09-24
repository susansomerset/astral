# AST-1605 — Confirm that artifacts are compressed

<!-- linear-archive: AST-1605 archived 2026-09-24 -->

## Linear archive (AST-1605)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1605/confirm-that-artifacts-are-compressed  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Artifact bodies in the `artifact` table must use the same durable storage contract as `agent_data.block_data`: zlib-compressed on write, transparently decompressed on read, so callers always see plain JSON/text. Large operative resumes and cover letters should not sit as uncompressed TEXT when the agent audit trail already pays for compression. Outcome: every new `artifact_data` write is zlib on disk; reads and legacy plain TEXT rows still behave for operators and hydrate paths.

**Archie decisions:** (1) Revert the premature Task land on `origin/dev` (`08a2b32b`) and re-land through normal dispatch (ftr/sub). (2) No new canon statute — document the zlib contract in code comments / `database.py` header inventory only.

## Functional scope

* New artifact writes store `artifact_data` zlib-compressed using the same compress helpers as `agent_data`.
* Artifact reads (`get_current` / by-uuid / list) return deserialized plain values; compression is invisible above the data layer.
* Pre-existing uncompressed TEXT `artifact_data` rows remain readable without a mandatory rewrite migration.
* Header inventory / in-code comments state the zlib-transparent contract (no new statute).

## Component scope

* `src/data/database.py` — **modified** — `save_artifact` compresses before INSERT; `_artifact_row_dict` decompresses before deserialize; CREATE DDL uses BLOB for `artifact_data`; header inventory + comments note the zlib contract.

## Technical scope

* Pre-dispatch (Chuckles at dispatch / land prep): revert premature `code(AST-1605)` (`08a2b32b`) from `origin/dev` so staging no longer carries the Task-path land before the Enhancement child ships.
* `src/data/database.py` — modified write path: normalize payload to plain string/JSON text, then store via shared `_compress_payload` on INSERT (same helper as `save_agent_data`).
* `src/data/database.py` — modified read mapping: run stored column through `_decompress_payload` before JSON-parse / plain return so public getters stay caller-transparent; legacy TEXT still works.
* `src/data/database.py` — modified schema ensure CREATE: `artifact_data` typed BLOB for new tables (existing TEXT affinity tables still accept BLOB writes).
* `src/data/database.py` — modified module header inventory line for `artifact` to describe zlib/BLOB (inventory statute).

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` for the compression contract itself (in-force catalog has no active pattern that requires zlib on `artifact_data`). Draft artifact write/read patterns remain draft and are **not** cited as law here.
* **New patterns proposed** — `none`.
* **Applicable statutes** —
  * [`astral.standards.data-raises-caller-logs`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>) — data layer raises, does not log; compression stays inside data helpers.
  * [`astral.standards.database-header-inventory`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>) — header inventory must describe `artifact` / `artifact_data` storage shape when it changes.
  * [`astral.layers.import-direction`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>) — compression lives in `src/data/`; core/UI keep calling public getters/savers only.
* **Requesting change to existing drafts (not in force)** — draft [`patt.artifact.write-operative`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>) / [`patt.artifact.read-current`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>) / [`patt.artifact.read-operative`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>) may eventually name zlib-transparent `artifact_data` when Archie promotes or amends them; do **not** treat drafts as current law. Archie declined a new active statute for this epic.

## Acceptance criteria

* Fresh `save_artifact` then raw SQL `SELECT artifact_data` yields `bytes` that `zlib.decompress` back to the plain JSON/text written — fail if the column is still plain uncompressed TEXT for a new write.
* `get_current_artifact` / `get_artifact` / `list_artifacts` return the same deserialized body the caller passed (dict/string contract unchanged) — fail if callers receive zlib bytes or undecoded blobs.
* Insert a legacy plain TEXT `artifact_data` row by SQL; `get_artifact` still returns the deserialized body — fail if legacy rows error or return None solely because they are uncompressed.
* `database.py` header inventory (and/or adjacent comments on the save/read path) states zlib transparency for `artifact.artifact_data` like `agent_data.block_data` — fail if the only mention is deleted `docs/ASTRAL_CODE_RULES.md` history with no in-tree note.
* Grep `save_artifact` body for `_compress_payload` and `_artifact_row_dict` for `_decompress_payload` both hit — fail if either path bypasses the shared helpers with a parallel compress implementation.
* After pre-dispatch revert, `git merge-base --is-ancestor 08a2b32b origin/dev` fails (commit no longer an ancestor of `origin/dev`) until the Enhancement child re-lands — fail if the Task commit remains on `origin/dev` while this epic is still pre-dispatch.

## Open questions

none

## Proposed child tickets

#### 1: **Artifact zlib write/read in data layer - Ada**

Re-implement the `artifact` table storage contract on a normal `sub/*` publish ref after Chuckles reverts premature `08a2b32b` from `origin/dev`: compress on `save_artifact`, decompress in row mapping for all public readers, BLOB DDL + header inventory / comments. Does **not** add a new canon statute. Does **not** change core/UI call sites (transparency). Does **not** perform the `origin/dev` revert itself (Chuckles pre-dispatch).
**Citations:** `astral.standards.data-raises-caller-logs`; `astral.standards.database-header-inventory`; `astral.layers.import-direction`.
**Scope:** `src/data/database.py` — modified — compress on write via `_compress_payload`; decompress in `_artifact_row_dict` via `_decompress_payload`; CREATE `artifact_data` BLOB; header inventory zlib note.
**Estimate:** 2

Monolith check: Functional scope has 4 capabilities; M=1 intentional — one inseparable data-layer vertical (write + read + DDL/inventory); Archie declined the separate canon child.
Scope partition check: sole Component/Technical file `src/data/database.py` claimed by child #1.

---

## Original brief

## Execution plan

1. Confirm `agent_data.block_data` contract: zlib compress on write / decompress on read via `_compress_payload` / `_decompress_payload` in `src/data/database.py` (callers see plain text).
2. Mirror that on `artifact.artifact_data`: `save_artifact` stores zlib bytes; `_artifact_row_dict` (used by `get_current_artifact` / `get_artifact` / `list_artifacts`) decompresses then JSON-parses; legacy plain TEXT rows stay readable.
3. New table DDL: `artifact_data BLOB NOT NULL` (SQLite affinity; existing TEXT tables still accept BLOBs).
4. Document in `docs/ASTRAL_CODE_RULES.md` Data-layer bullet that artifacts use the same transparent zlib pattern as `agent_data`.
5. Verify round-trip: public readers return deserialized payloads; on-disk column is compressed bytes (smoke / existing artifact component tests).
6. Land on `origin/dev` from `$ASTRAL_MAIN` (Task — no ftr/sub / no drones).

## Done when

* New artifact writes store zlib-compressed `artifact_data` (same helpers as `agent_data`).
* Reads still return plain deserialized values to callers; legacy uncompressed TEXT rows still load.
* Code rules document the artifact compression contract.
* Change is on `origin/dev`.

## Risks / open questions

* `origin/dev` already has `code(AST-1605): zlib-compress artifact_data like agent_data` (`08a2b32b`) from an earlier Todo pass — Todo may be verify-only unless you want that commit reverted or adjusted.
  * That's this ticket, silly.
* No Betty test land in that commit (role hook); on-disk zlib was smoke-checked locally. Want a `tests/` assertion on `origin/tests`?
  * No.  We don't need to continually verify this change.

---

## Original brief

like agent_data

### Comments

#### chuckles — 2026-09-15T23:25:57.751Z
@susan
1. Approve adding a new active statute under `canon/statutes/astral/standards/` for zlib-transparent `agent_data.block_data` + `artifact.artifact_data` (replacing the deleted CODE_RULES Data-layer sentence), or document only in code comments / header inventory?

#### fable — 2026-09-15T23:23:49.422Z
Decision on Open question 1: revert the existing dev land and redo this properly through normal dispatch. This should not have been created and landed as a Task in the first place.

#### chuckles — 2026-09-15T12:08:58.808Z
[check-linear] answered — @susan

AST-1605’s artifact change is **app code**, not a one-shot SQL rewrite of the volume.

**Staging:** Railway runs the build that tracks `origin/dev`. Once `08a2b32b` (or later `dev` tip that contains it) is the deployed SHA, the next process start uses that `database.py`. New `save_artifact` calls zlib-compress `artifact_data` before INSERT; readers decompress via `_artifact_row_dict`. Existing plain TEXT rows stay readable (no backfill required).

**Production:** same behavior after that commit is on `main` (Archie release: `dev` → `main`). Until then prod keeps the old write path.

**Schema:** `_ensure_artifact_table` only creates/adopts the table if needed. Changing CREATE to `BLOB` affects **new** empty DBs; live staging/prod DBs that already have `artifact` keep their column affinity and simply start storing zlib bytes on new inserts — no ALTER / migrate-all-rows step.

#### susan — 2026-09-15T12:06:57.467Z
@chuckles how are the changes to the artifact table made in staging in production?

#### chuckles — 2026-09-15T00:51:15.894Z
@susan
1. `origin/dev` already contains `code(AST-1605)` (`08a2b32b`) from the prior Task path (outside ftr/sub). Keep that land and treat proposed child #1 as verify-only against current `dev`, or revert and re-land under normal dispatch refs?
2. Approve adding a new active statute under `canon/statutes/astral/standards/` for zlib-transparent `agent_data.block_data` + `artifact.artifact_data` (replacing the deleted CODE_RULES Data-layer sentence), or document only in code comments / header inventory?

---

_Implementation detail may live in git history on `origin/dev`._
