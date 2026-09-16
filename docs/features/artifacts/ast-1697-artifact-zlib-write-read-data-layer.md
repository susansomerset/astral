# AST-1697 — Artifact zlib write/read in data layer

**Linear:** [AST-1697](https://linear.app/astral/issue/AST-1697)  
**Parent:** [AST-1605](https://linear.app/astral/issue/AST-1605) — Confirm that artifacts are compressed  
**Publish ref:** `sub/AST-1605/AST-1697-artifact-zlib-write-read-data-layer`

Re-land the artifact-table zlib storage contract on a normal `sub/*` publish ref after Chuckles reverted premature `08a2b32b` from `origin/dev`. New `save_artifact` writes store zlib-compressed `artifact_data` via shared `_compress_payload`; `_artifact_row_dict` (used by `get_current_artifact` / `get_artifact` / `list_artifacts`) decompresses via `_decompress_payload` before JSON-parse so callers still see plain dict/string; CREATE DDL uses `BLOB`; header inventory notes the contract. No new canon statute; no core/UI call-site changes; no `origin/dev` revert in this ticket.

## UAT fitness

- **AC restored:** Parent / child Acceptance criteria for this data-layer vertical: (1) Fresh `save_artifact` then raw SQL `SELECT artifact_data` yields `bytes` that `zlib.decompress` back to the plain JSON/text written — fail if the column is still plain uncompressed TEXT for a new write. (2) `get_current_artifact` / `get_artifact` / `list_artifacts` return the same deserialized body the caller passed (dict/string contract unchanged) — fail if callers receive zlib bytes or undecoded blobs. (3) Insert a legacy plain TEXT `artifact_data` row by SQL; `get_artifact` still returns the deserialized body — fail if legacy rows error or return None solely because they are uncompressed. (4) `database.py` header inventory (and/or adjacent comments on the save/read path) states zlib transparency for `artifact.artifact_data` like `agent_data.block_data` — fail if the only mention is deleted `docs/ASTRAL_CODE_RULES.md` history with no in-tree note. (5) Grep `save_artifact` body for `_compress_payload` and `_artifact_row_dict` for `_decompress_payload` both hit — fail if either path bypasses the shared helpers with a parallel compress implementation. (Parent ancestry AC for `08a2b32b` is Chuckles pre-dispatch / Notes: behavioral undo via revert; not this child’s code stage.)
- **Correct outcome:** Every new `artifact_data` write is zlib on disk; public readers and hydrate paths still return plain deserialized JSON/text; pre-existing uncompressed TEXT rows remain readable without a rewrite migration.
- **Sibling check:** Sole child of AST-1605; Component/Technical scope is only `src/data/database.py`. No sibling contracts to re-verify beyond “callers of `save_artifact` / getters unchanged” (transparency — do not edit core/UI).
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done. Success is on-disk zlib for new writes **and** transparent public reads **and** legacy TEXT still loads **and** in-tree inventory/comments document the contract.
- **Wrong fix rejected:** Do **not** re-document in retired `docs/ASTRAL_CODE_RULES.md` (Archie: header inventory + adjacent comments only). Do **not** add a new canon statute. Do **not** invent a parallel compress/decompress helper — reuse `_compress_payload` / `_decompress_payload`. Do **not** change core/UI call sites. Do **not** perform the `origin/dev` revert in this ticket.

## Scope (from ticket — explicit gate)

`src/data/database.py` — modified — compress on write via `_compress_payload`; decompress in `_artifact_row_dict` via `_decompress_payload`; CREATE `artifact_data` BLOB; header inventory zlib note.

**Canon (patterns + placement statutes to read; all others id-only):**  
`astral.standards.data-raises-caller-logs`; `astral.standards.database-header-inventory`; `astral.layers.import-direction`. No active pattern requires zlib on `artifact_data`; drafts `patt.artifact.*` are **not** law.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory zlib/BLOB note; CREATE `artifact_data BLOB`; `save_artifact` → `_compress_payload`; `_artifact_row_dict` → `_decompress_payload` before JSON-parse | data |

No other files. Do not touch `tests/`, bible, canon drafts, or `docs/ASTRAL_CODE_RULES.md`.

## Stage 1: Zlib-transparent artifact_data (write + read + DDL + inventory)

**Done when:** New `save_artifact` stores zlib bytes in `artifact_data`; `_artifact_row_dict` returns the same deserialized body callers passed; CREATE DDL declares `artifact_data BLOB NOT NULL`; module header inventory describes zlib-transparent `artifact_data` like `agent_data.block_data`; legacy plain TEXT rows still map through `_decompress_payload` without error. Grep confirms `_compress_payload` in `save_artifact` and `_decompress_payload` in `_artifact_row_dict`.

1. In `src/data/database.py` module header inventory, update the `- artifact —` bullet so `artifact_data` is described as **BLOB (zlib-compressed JSON text like `agent_data.block_data`; legacy plain TEXT still readable)** — replace the current `artifact_data TEXT` wording. Keep the rest of that bullet (uuid, candidate_id, versioning, AST refs) intact.

2. In `_ensure_artifact_table` / `_create_artifact_ddl` inside `src/data/database.py`, change the CREATE column from `artifact_data TEXT NOT NULL` to `artifact_data BLOB NOT NULL`. Do not add a migration that rewrites existing rows; existing TEXT-affinity tables still accept BLOB writes (SQLite affinity).

3. In `save_artifact` in `src/data/database.py`:
   - Keep the None check and the plain-text normalize: `plain = artifact_data if isinstance(artifact_data, str) else json.dumps(artifact_data)`.
   - Set `payload = _compress_payload(plain)` (same shared helper `save_agent_data` uses for `block_data`). Do **not** call `zlib.compress` directly.
   - Pass `payload` into the existing INSERT bind for `artifact_data`.
   - Update the docstring to state that `artifact_data` is stored zlib-compressed (AST-1697 / AST-1605; like `agent_data`), transparent to callers.
   - Add a short inline comment on the compress line naming AST-1697 and the agent_data parallel.

4. In `_artifact_row_dict` in `src/data/database.py`:
   - Replace `raw = row[5]` with `plain = _decompress_payload(row[5])` (handles bytes/BLOB and legacy str/TEXT).
   - JSON-parse `plain` when possible: `artifact_data = json.loads(plain) if plain is not None else None`, and on `(TypeError, json.JSONDecodeError)` set `artifact_data = plain` (not the raw column).
   - Update the function docstring to say decompress + JSON-parse.
   - Add a short comment that AST-1697 mirrors agent_data zlib transparency; legacy TEXT still via `_decompress_payload`.

5. Do **not** edit `get_current_artifact`, `get_artifact`, or `list_artifacts` bodies — they already route through `_artifact_row_dict`. Do **not** add logging in the data layer (`astral.standards.data-raises-caller-logs`). Do **not** import from core/ui (`astral.layers.import-direction`).

6. Smoke-check locally (not Betty’s tree): after a `save_artifact` of a small dict, raw SQL `SELECT artifact_data` for that uuid should be `bytes` decompressible to the written JSON text; `get_artifact(uuid)` should return the deserialized dict. Optionally insert a plain TEXT row by SQL and confirm `get_artifact` still returns the body. If smoke fails when steps were followed literally, stop and comment the parent with the Stage blocked template — do not invent a second compress path.

⚠️ **Decision:** Reuse existing `_compress_payload` / `_decompress_payload` only (no artifact-specific helpers). Matches parent Architectural definition and AC grep gate; keeps one decompress semantics for legacy TEXT.

⚠️ **Decision:** Document zlib only in header inventory + adjacent save/read comments — not in retired `docs/ASTRAL_CODE_RULES.md` and not as a new statute (Archie).

## Estimate

Confirm Chuckles estimate: 2 — agree
