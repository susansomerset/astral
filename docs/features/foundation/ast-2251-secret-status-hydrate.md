# AST-2251 — Status, hydrate, and migration

Linear: [AST-2251](https://linear.app/astralcareermatch/issue/AST-2251/status-hydrate-and-migration-manage-candidate-secrets-in-railway)
Parent: [AST-2246](https://linear.app/astralcareermatch/issue/AST-2246/manage-candidate-secrets-in-railway)
Publish ref: `sub/AST-2246/AST-2251-secret-status-hydrate`

After the Railway variable client (AST-2250). The candidate row keeps SET / NOT SET and an expiry timestamp; a read at or past that timestamp reports EXPIRED. Hydrate fills the existing `candidate_api_keys` map from the process environment (one Railway variable per candidate in production, one shared stub per secret id locally) and only for a reported SET. A one-shot script decrypts today's ciphertext, upserts those Railway variables, and clears the ciphertext. This ticket does not own the Railway HTTP client, the Admin UI, or the CSE call site.

## Scope check

This ticket's Scope names only:

- `src/data/database.py` — stop Fernet ciphertext writes; persist status + expires_at only
- `src/core/candidate.py` — set/clear updates status and expiry; hydrate builds `candidate_api_keys` from the process environment
- `scripts/migrations/migrate_candidate_api_keys_to_railway.py` — decrypt existing `api_keys`, upsert Railway variables, clear ciphertext
- `docs/features/candidate/CANDIDATE_DATA_MODEL.md` — vault variables plus status/expiry; ciphertext column narrative retired

Do not edit `src/external/railway.py`, `src/utils/config.py`, `env.example`, `src/ui/api/api_candidate.py`, `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, `src/external/google_cse.py`, `src/core/timesheets.py`, or `src/core/dispatcher.py`. AST-2252 owns the Admin contract. AST-2253 owns search call sites. The dispatch missing-key gate already treats a missing `candidate_api_keys` entry as unset (`src/core/dispatcher.py` around the `server_id and not (ctx.get("candidate_api_keys") or {}).get(server_id)` check). EXPIRED is implemented by leaving that server out of the map.

`src/ui/api/api_candidate.py` keeps calling `update_candidate_api_keys(candidate_id, [{server, key}])`. A non-empty key without `expires_at` raises `ValueError` from this ticket's function. AST-2252 adds `expires_at` on that call. Do not change the API file here.

Required candidate metadata columns stay as they are (`stat.entity.required-metadata`): `state`, `state_history`, `state_changed_at`, `batch_id`, `batch_created_at`, `created_at`, `updated_at`. No new column. No rename. No drop.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `api_keys` JSON becomes status records. Update path never encrypts. Read path never decrypts. | data |
| `src/core/candidate.py` | Set/clear builds status + expiry. Hydrate fills `candidate_api_keys` from environ and reports EXPIRED. | core |
| `scripts/migrations/migrate_candidate_api_keys_to_railway.py` | New script: decrypt, upsert, clear ciphertext. | scripts |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Status record and Railway variable names. Remove the Fernet-at-rest section. | docs |

## Stage 1: Status record in the candidate row

**Done when:** `update_candidate_api_keys` persists `[{server, status, expires_at}]` and does not call `encrypt_value`. `get_candidate` does not call `decrypt_value`. A stored `SET` row is visible on `candidate_secret_status`. The required metadata column names on `candidate` are unchanged.

1. In the `database.py` module header comment that mentions `api_keys`, replace the Fernet-ciphertext description with: `api_keys` is a JSON array of `{server, status, expires_at}` (AST-2251). `status` is `SET` or `NOT SET`. `expires_at` is `YYYY-MM-DD HH:MM:SS` UTC or JSON `null`. The array is not ciphertext. Leave `encrypt_value` and `decrypt_value` in place; only the migration script calls `decrypt_value`. Nothing in the key-update path calls `encrypt_value`.

2. Replace `_candidate_api_key_entries` and `_candidate_key_map_from_column` with one parser, `_candidate_secret_rows(raw) -> list[dict]`. Malformed JSON returns `[]`. Each kept dict is one of:
   - status row: `server` non-empty, `status` in `{"SET", "NOT SET"}`, no `key`. `expires_at` is a string or `None`.
   - legacy ciphertext row: `server` and `key` present, no `status`. Keep `key` on this internal row only so the migration can still see it. Do not decrypt here.

   Drop any other element.

3. Replace `update_candidate_api_keys(candidate_id, entries)` so it never encrypts. `entries` are already status edits from `candidate.py`: each is `{server, status, expires_at}` with `status` in `{"SET", "NOT SET"}` and no `key`. Blank `candidate_id` raises `ValueError("candidate_id is required")`. A duplicate `server` in `entries` raises `ValueError`. A missing candidate raises `LookupError`. Inside the write transaction, load the current rows with `_candidate_secret_rows`. For each edit, replace that server's row with `{"server", "status", "expires_at"}` only (drop any ciphertext `key` for that server). Leave every other row untouched, including untouched legacy `{server, key}` rows. `UPDATE` `api_keys` with `json.dumps` of that list and set `updated_at` to `_utc_now()`. Do not call `encrypt_value`. Do not add a `key` field on a status row.

4. In `_parse_candidate_row`, keep `d.pop("candidate_api_key", None)`. Replace the decrypt assignment with these four assignments and nothing else:
   - `rows = _candidate_secret_rows(d.pop("api_keys", None))`
   - `d["candidate_secret_status"]` = `{row["server"]: {"status": row["status"], "expires_at": row.get("expires_at")} for row in rows if "status" in row}` in row order.
   - `d["candidate_api_keys"]` = `{}`.
   - `d["_legacy_secret_ids"]` = `[row["server"] for row in rows if "key" in row and "status" not in row]`.
   Do not import `candidate` in this stage. Stage 2 adds the `hydrate_candidate_secrets(d)` call after these assignments.

⚠️ **Decision:** The `api_keys` column stays. AC 1 selects that column. The secret value is not a column and is not a JSON field. `EXPIRED` is not stored.

⚠️ **Decision:** Untouched legacy ciphertext rows stay on the JSON until the migration script or an edit of that same server. A set/clear of one server must not wipe another server's ciphertext before the script runs.

## Stage 2: Set, clear, and hydrate

**Done when:** A set with a catalog id and `expires_at` stores `SET` plus that timestamp and does not call Railway. A clear stores `NOT SET` and `expires_at` null. For two candidates with `SET` and `ASTRAL_RAILWAY_TOKEN` unset, `get_candidate(...)["candidate_api_keys"][secret_id]` is the same `CANDIDATE_SECRET_STUB_*` value, and `upsert_service_variable` is not called. With `expires_at` at or before now, that server is absent from `candidate_api_keys` and `candidate_secret_status[server]["status"]` is `EXPIRED`. A `SET` whose env var is missing logs one warning with the candidate id and the secret id and omits the server. `rg -n "Fernet" src/data/database.py` may still see `decrypt_value`; it must not see an `encrypt_value` call inside `update_candidate_api_keys`.

1. In `src/core/candidate.py`, add imports `os` and, from `src.utils.config`, `CANDIDATE_SECRET_CATALOG`, `CANDIDATE_SECRET_RAILWAY_CONFIG`, `candidate_secret_variable_name`, and `candidate_secret_local_stub_env`. `logger` is already `get_logger(__name__)`.

2. Replace `update_candidate_api_keys` so the wrapper owns set/clear. For each entry, in order:
   - `server` missing or blank → `ValueError`.
   - `server` not in `CANDIDATE_SECRET_CATALOG` → `ValueError` naming the id and `list(CANDIDATE_SECRET_CATALOG)`. Do not call `get_llm_server`. Catalog ids include the search secrets.
   - Duplicate `server` in this call → `ValueError`.
   - `key = str(entry.get("key") or "").strip()`.
   - Non-empty `key`: require `expires_at`. Strip it. Parse with `datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")`. On failure, `ValueError("expires_at must be YYYY-MM-DD HH:MM:SS")`. Append `{"server": server, "status": "SET", "expires_at": expires_at}` using the stripped timestamp string. Do not put `key` on the edit. Do not call Railway.
   - Empty `key`: append `{"server": server, "status": "NOT SET", "expires_at": None}`. `expires_at` on the incoming entry is ignored.
   - Then `database.update_candidate_api_keys(candidate_id, edits)`.

3. Add `hydrate_candidate_secrets(row: dict) -> None`. It mutates `row` and returns `None`.
   - Read `candidate_id` from `row.get("astral_candidate_id")` or `""`.
   - Pop `row["_legacy_secret_ids"]` (default `[]`). For each id, `logger.warning("%s secret %s still has ciphertext in api_keys — this server is unset until migration", candidate_id or "-", secret_id)`. Do not log the ciphertext. Do not decrypt. Do not add that id to `candidate_api_keys`.
   - Production when `CANDIDATE_SECRET_RAILWAY_CONFIG["token_env"]` is in `os.environ` and `os.environ[that name].strip()` is non-empty. Otherwise local. Do not import `src.external.railway`.
   - For each `secret_id` in `row["candidate_secret_status"]` (dict order):
     - Stored `NOT SET` → leave status `NOT SET`, leave `expires_at` as stored (`None` or the string). Omit from `candidate_api_keys`. No warning.
     - Stored `SET`: take `expires_at`. `None` or `""` means no date on file → reported status stays `SET` (migration rows). A string that does not parse with `"%Y-%m-%d %H:%M:%S"` → set reported status to `EXPIRED`, `logger.warning("%s secret %s expires_at is not YYYY-MM-DD HH:MM:SS — this server is unset", candidate_id or "-", secret_id)`, omit from the map. A parsed timestamp is UTC (`replace(tzinfo=timezone.utc)`). Reported status is `EXPIRED` when `datetime.now(timezone.utc) >= parsed`, and then omit from the map. No warning for a normal expiry.
     - Reported `SET`: env name is `candidate_secret_variable_name(secret_id, candidate_id)` in production and `candidate_secret_local_stub_env(secret_id)` locally. `try: value = os.environ[env_name]` / `except KeyError: value = ""`. If `value.strip()` is empty, `logger.warning("%s secret %s is SET but missing from the environment — this server is unset", candidate_id or "-", secret_id)` and omit it. Otherwise `row["candidate_api_keys"][secret_id] = value` (the raw environ string). Do not log `value`.
   - Write the reported status back onto `row["candidate_secret_status"][secret_id]["status"]`. Keep `expires_at` as stored.

4. In `_parse_candidate_row`, after the Stage 1 status assignment, call `hydrate_candidate_secrets`. Import it inside the function (`from src.core.candidate import hydrate_candidate_secrets`) so `database` does not import `candidate` at module import. Hydrate pops `_legacy_secret_ids` before returning, so parsed rows do not carry that key.

⚠️ **Decision:** Local vs production is whether `ASTRAL_RAILWAY_TOKEN` is set and non-empty. Hydrate only reads `os.environ`. It does not call `upsert_service_variable`, `delete_service_variable`, or `trigger_service_deploy`. The same stub env is shared by every candidate, which is how two candidates return one plaintext.

⚠️ **Decision:** `expires_at` null on a stored `SET` stays `SET` and hydrates. That is the migration row (no date was stored with the ciphertext). A timestamp, including one equal to now, reports `EXPIRED` and the map omits the server so the existing dispatch gate skips the task. Admin set always requires a timestamp; only migration writes null.

⚠️ **Decision:** Missing env on a reported `SET` is a warning (`stat.logging.warning`): candidate id, secret id, product consequence. Not the value. Not `logger.exception`. Not a warning for `NOT SET` or for a normal `EXPIRED`.

## Stage 3: Migration script

**Done when:** `python scripts/migrations/migrate_candidate_api_keys_to_railway.py` (no `--execute`) prints one line per ciphertext entry with candidate id, server, and Railway variable name, and does not print the plaintext. `--execute` upserts that variable, then rewrites the row so `api_keys` has no `key` field. A failed upsert leaves that row's ciphertext in place.

1. Add `scripts/migrations/migrate_candidate_api_keys_to_railway.py`. Shebang `#!/usr/bin/env python3`, `from __future__ import annotations`, `sys.path` insert of the repo root the same way as `migrate_legacy_candidate_states.py`. Argparse: `--execute` (default is dry-run). Docstring says copy the db first and that this calls Railway.

2. Add `database.list_candidate_api_key_columns() -> list[dict]` returning `{"astral_candidate_id", "api_keys"}` for every candidate row (`SELECT astral_candidate_id, api_keys FROM candidate`). Raw column text. Do not parse through `_parse_candidate_row` (that path no longer decrypts).

3. For each row, `rows = _candidate_secret_rows` is private. Parse in the script with the same rules, or add `database.candidate_secret_rows_from_column(raw) -> list` as a public alias of `_candidate_secret_rows`. Use the public alias. Ciphertext entries are those with `key` and without `status`.

4. For each ciphertext entry, in column order:
   - `name = candidate_secret_variable_name(server, candidate_id)`.
   - Dry-run: decrypt only to know it works. On `RuntimeError` or `ValueError`, print `undecryptable` plus candidate id and server. On success, print `would upsert` plus candidate id, server, and `name`. Never print the plaintext.
   - `--execute`: `decrypt_value`. On failure, remember `(server, "NOT SET", None)` and `logger.warning` from `get_logger` in the script: `"%s secret %s ciphertext would not decrypt — status NOT SET", candidate_id, server`. Do not upsert that server. On success, `upsert_service_variable(name=name, value=plaintext)` from `src.external.railway`. Do not catch `RailwayCallFailed` and do not log it again. If it raises, abort the process before writing this candidate's row (earlier candidates already committed stay committed; this row's `api_keys` is unchanged so a rerun upserts again). On success, remember `(server, "SET", None)`.

5. After every ciphertext entry for that candidate has been handled, build the replacement list: status rows that were already status rows stay as stored; each ciphertext server is replaced by `{server, status, expires_at}` from the remember-step (`SET`/`null` or `NOT SET`/`null`). `--execute` writes that list with the same `UPDATE` shape as `update_candidate_api_keys` (`api_keys`, `updated_at`) and commits per candidate. Dry-run does not write. Do not call `trigger_service_deploy`. Do not call `delete_service_variable`.

⚠️ **Decision:** One upsert per stored ciphertext key, then the row loses its `key` fields. No deploy trigger — this ticket's migration scope is decrypt, upsert, clear ciphertext. `upsert_service_variable` already sets `skipDeploys: true`. A later deploy (operator or AST-2252's admin set) is what puts the value in the process environment.

⚠️ **Decision:** Decrypted migration rows are stored `SET` with `expires_at` null so hydrate still serves them. Undecryptable rows become `NOT SET` and the ciphertext is dropped on the execute write. The plaintext is never logged.

## Stage 4: Data-model doc

**Done when:** `docs/features/candidate/CANDIDATE_DATA_MODEL.md` describes the status record and the Railway variable name, and it no longer says the API key is Fernet ciphertext at rest.

1. In the candidate table column list, replace the `candidate_api_key` bullet with: `api_keys` — JSON array of `{server, status, expires_at}`. `status` is `SET` or `NOT SET`. `expires_at` is UTC `YYYY-MM-DD HH:MM:SS` or null. The secret value is not in this column. Production variable name is `candidate_secret_variable_name(server, astral_candidate_id)` (`CANDIDATE_<SANITIZED_ID>_<SUFFIX>` from `CANDIDATE_SECRET_CATALOG`). Local hydrate reads `candidate_secret_local_stub_env(server)` instead, one value for every candidate. A read with `expires_at` set and `now >= expires_at` reports `EXPIRED` and omits that server from `candidate_api_keys`. `candidate_api_key` (singular) remains an unread legacy column; it is not written by the key path.

2. Delete the `## Encryption` section (`candidate_api_key` is Fernet-encrypted at rest … `clear_candidate_api_key()`).

3. In the snake_case column list, add `api_keys` next to `candidate_api_key`. Do not remove `candidate_api_key` from that list; the column still exists.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Review stub (build-child)

**Built:** `425e4c8f97bfd76742ff24d016e9f75bc6e56ae9` on `sub/AST-2246/AST-2251-secret-status-hydrate`

Status column JSON: `550491218`. Hydrate: `42336fedf`. Migration: `8a5d9baa9`. Data model: `425e4c8f9`. No test-tree edits. Required candidate metadata columns were not added, renamed, or dropped. Missing-env and bad-expiry warnings name the candidate and the secret id and do not include the secret value.


## Joan validate

[plan-rubric]
**Ticket:** AST-2251
**Overall:** APPROVED
**Corpus:** 65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91
**Publish ref:** `sub/AST-2246/AST-2251-secret-status-hydrate` @ `54e0161e0600aa0e0414dd8115a30cf683c589c5`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.entity.required-metadata | A | | |
| stat.logging.warning | A | | |
| new candidate-secret pattern (pending Archie) | B | | |

## Traceability

`1 → Stage 3 (--execute clears ciphertext; legacy rows preserved until migrate); 2 → Stage 2 (EXPIRED omits server from candidate_api_keys; dispatch gate unchanged); 3 → Stage 2 (local via unset ASTRAL_RAILWAY_TOKEN, shared stub, no railway import); 4 → Stage 1–2 (update_candidate_api_keys never encrypt_value)`

## Findings

### discuss — Canon Scope gap (layers / config)

- **Severity:** discuss
- **Location:** Stage 2 step 4 — `_parse_candidate_row` lazy-imports `hydrate_candidate_secrets` from `src.core.candidate`
- **Finding:** `astral.layers.import-direction` (data → utils only) and `astral.config.config-source-of-truth` / `astral.config.secrets-and-env-specific-from-environ` govern this footprint but are not on the frozen Citations list. The lazy data→core import mirrors an existing `database.py` pattern (`ensure_company_search_terms_table_synced`) but is still a layer stretch; catalog/env reads in hydrate match the parent secret pattern.
- **Recommendation:** Archie may amend Canon Scope for comparability with Radia; do not widen this pass. If build hits import-cycle pain, prefer hydrating from `candidate.get_candidate` / list wrappers without scoring off-list statutes here.

### discuss — Pattern not in corpus

- **Severity:** discuss
- **Location:** Citations / Stages 1–3
- **Finding:** Candidate-secret Railway + row status + environ hydrate is still “pending Archie” with no `canon/patterns/**` file.
- **Recommendation:** Same as sibling AST-2250 — plan text tracks the parent architectural proposal (status not stored as EXPIRED, no secret in row, production vs local naming, migration without deploy trigger).

### discuss — Migration deploy vs running process

- **Severity:** discuss
- **Location:** Stage 3 decisions (no `trigger_service_deploy`)
- **Finding:** Upserts run with `skipDeploys`; values appear in the process only after a later deploy. Epic admin flow always deploys after write; one-shot migration does not.
- **Recommendation:** Acceptable for AC 1 (column cleared) if operators expect a deploy after migration — call out in runbook when executing `--execute`; not a plan rewrite.

### acceptable — Hard dependency on AST-2250

- **Severity:** acceptable
- **Location:** Stage 2 imports from `src.utils.config` / catalog helpers
- **Finding:** Build assumes AST-2250 catalog symbols exist; ticket boundary and blockedBy order say “after Railway variable client.”
- **Recommendation:** Merge or roll up #1 before implementing #2.

### acceptable — Admin API unchanged until AST-2252

- **Severity:** acceptable
- **Location:** Scope check
- **Finding:** `expires_at` required on non-empty `key` in core wrapper; `api_candidate.py` unchanged — set-with-key without expiry fails until Admin sibling wires expiry.
- **Recommendation:** Matches dispatch partition; AC 2–3 testable via core/database paths and stubs.

context_tokens≈42000

## Radia review

[code-rubric]
**Ticket:** AST-2251
**Publish ref:** `cac5838cfe1e040cb155f38a72fa38eead53e27a` (`origin/sub/AST-2246/AST-2251-secret-status-hydrate`)
**Corpus:** `65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.entity.required-metadata | A | | |
| stat.logging.warning | A | | |
| new candidate-secret pattern (pending Archie) | A | | |

## Column diff vs plan stage

| slug | Joan | Radia | note |
|------|------|-------|------|
| new candidate-secret pattern (pending Archie) | B | A | Plan-stage B reflected pending corpus; diff delivers parent AST-2246 slice (status JSON, no ciphertext write, environ hydrate, migration upsert+clear, no deploy in script). |

(stat.entity.required-metadata, stat.logging.warning: aligned at A)

## Frame diff

- [x] **Acceptance criteria — AC 2:** Confirm dispatch missing-key behavior is unchanged and `EXPIRED` is satisfied by omitting the server from `candidate_api_keys` (no `dispatcher.py` edit on this sub).
- [x] **Acceptance criteria — AC 1:** After `--execute`, operators run a deploy (or accept stale env until deploy) so hydrated values match Railway upserts — Joan’s migration note.

## Findings

### advisory — Sibling product carry in three-dot diff

- **Location:** `src/external/railway.py`, `src/utils/config.py`, `env.example`, `docs/features/foundation/ast-2250-railway-variable-client.md`, `tests/component/external/test_railway.py`, `tests/component/utils/test_config.py` (AST-2250 paths)
- **Finding:** `origin/dev...origin/sub/AST-2246/AST-2251-secret-status-hydrate` includes AST-2250’s Railway client stack; expected when the sub branch rolls up the prior sibling for AST-2251’s migration import and catalog helpers.
- **Recommendation:** Note once in the issue doc; not a cross-ticket product scope violation for AST-2251.

### advisory — Off-list statutes (do not score)

- **Location:** `_parse_candidate_row` → lazy `hydrate_candidate_secrets`; `src/core/candidate.py` catalog/env reads
- **Finding:** `astral.layers.import-direction`, `astral.config.config-source-of-truth`, and `astral.config.secrets-and-env-specific-from-environ` govern the footprint but are not on the frozen Citations list; behavior matches Joan’s plan-stage discussion (lazy data→core hydrate, catalog in config, hard `os.environ` reads in hydrate only).
- **Recommendation:** Archie may widen parent Canon Scope at Discussion; do not insert ids on this pass.

### discuss — Migration upsert without deploy

- **Severity:** discuss
- **Location:** `scripts/migrations/migrate_candidate_api_keys_to_railway.py` (no `trigger_service_deploy`)
- **Finding:** `--execute` upserts with `skipDeploys`; running processes do not see new values until a later deploy. AC 1 is about clearing ciphertext in SQLite, not live env parity.
- **Question (@susan):** Should migration runbook require an explicit deploy step after `--execute`?
- **Default:** Document “deploy after `--execute`” in operator notes when Chuckles/UAT runs the script; no code change on this sub unless Susan wants deploy wired into the script.

### advisory — AC 2 vs dispatcher tests

- **Location:** `TestAst2251SecretStatusHydrate::test_expired_and_exact_now_omit_the_server`; manifest has no `test_dispatcher` row
- **Finding:** EXPIRED is asserted via absent `candidate_api_keys` entry and reported `candidate_secret_status`; plan states the existing dispatch gate already treats a missing map entry as unset.
- **Recommendation:** Tick frame-diff AC 2 row at `resolve-child` §10; optional future dispatcher pin test is Betty scope, not fix-now here.

## What's solid

- **Data:** `api_keys` persists `{server, status, expires_at}` only; `encrypt_value` is not called anywhere in `database.py` on tip; legacy `{server, key}` rows preserved until edit or migration; `candidate_secret_rows_from_column` / `list_candidate_api_key_columns` / `replace_candidate_secret_rows` match Stage 3.
- **Core:** `update_candidate_api_keys` validates catalog ids, requires `expires_at` on set, does not call Railway; `hydrate_candidate_secrets` implements production vs local token probe, EXPIRED at/after timestamp, shared stub, and the three warning shapes without secret material.
- **Migration:** Dry-run prints candidate/server/name only; execute path decrypts, upserts, rewrites rows; undecryptable → `NOT SET` with one warning; does not re-log `RailwayCallFailed`.
- **Docs/tests:** `CANDIDATE_DATA_MODEL.md` matches Stage 4; bible manifest lists five focused classes including migration and revised AST-1901 ciphertext tests.

## Recommended actions (downstream only — not in Radia lane)

- Chuckles: append this artifact to `docs/features/foundation/ast-2251-secret-status-hydrate.md`, commit `docs(AST-2251): Radia review — clean`, post slim upshot `--as radia`, move to **Review Posted**.
- If Susan affirms the migration **Default**, add a one-line operator note near the script docstring or epic runbook (engineer/`resolve-child` or UAT prep — not Radia).

```
[code-rubric] PROCEED (Commit: cac5838) Status hydrate migration clean
```

context_tokens≈38000

## Resolution

2026-10-16 — Radia overall CLEAN. No fix-now items.

Discuss "Migration upsert without deploy": Susan had not answered. Took the finding **Default** — no `trigger_service_deploy` in the script. One line in `scripts/migrations/migrate_candidate_api_keys_to_railway.py` tells the operator to deploy the Astral service after `--execute`.

Advisory items left as written: sibling AST-2250 files in the three-dot diff, off-list statutes not scored, AC 2 covered by the hydrate omission rather than a dispatcher test. Frame-diff AC 1 and AC 2 rows ticked.

## Bug: AST-2275 — dispatch validation misses vault-set OpenRouter key

### As-is

After Admin sets a candidate OpenRouter key through the Railway vault, Manage Candidates shows status SET, but scheduled-action / dispatch validation marks the task invalid for a missing OpenRouter key. Agent Ad Hoc fails with `Candidate somerset has no API key for server 'openrouter'`.

### To-be

When that candidate's OpenRouter key is SET via the vault, `_candidate_dispatch_api_key_error` and Agent Ad Hoc resolve a non-empty `candidate_api_keys["openrouter"]` for that candidate, so validation does not mark the task invalid for a missing OpenRouter key.

### Repro

1. On a host where `ASTRAL_RAILWAY_TOKEN` is set (production probe true), Admin PUT for candidate `somerset` with `api_keys: [{server: "openrouter", key: "<secret>", expires_at: "<future YYYY-MM-DD HH:MM:SS>"}]`. Railway upsert and deploy trigger succeed; row status is SET.
2. Before a new process has the injected env — or on the same process that never received `CANDIDATE_SOMERSET_OPENROUTER` in `os.environ` — open Scheduled Actions for a task whose agent server is `openrouter`, or POST `/admin/anthropic_ad_hoc` for `somerset` / OpenRouter.
3. Fail: `invalid_reason` / 400 cites a missing OpenRouter key; Ad Hoc returns `Candidate somerset has no API key for server 'openrouter'`. GET still shows OpenRouter status SET (hydrate leaves stored SET when the env value is missing).

### Root cause

Hydrate builds `candidate_api_keys` only from `os.environ` (per-candidate name in production, shared stub locally). Admin set (and `update_candidate_api_keys`) persist status SET and write Railway, but never put the plaintext into the **current** process environment. Until a redeployed process inherits the Railway variable — or a local stub is exported by hand — status stays SET while the map stays empty. Dispatch validation and Ad Hoc both read the map (`_candidate_dispatch_api_key_error`, `_candidate_server_key`), so they treat the key as missing while the UI shows SET.

### Proposed change

In `src/core/candidate.py`, inside `update_candidate_api_keys`, after the catalog / expiry checks and before `database.update_candidate_api_keys`:

1. Use the same production probe as `hydrate_candidate_secrets`: `token_env = CANDIDATE_SECRET_RAILWAY_CONFIG["token_env"]`; production when that name is in `os.environ` and `os.environ[token_env].strip()` is non-empty.
2. For each edit with a non-empty `key`: `env_name = candidate_secret_variable_name(server, candidate_id)` when production, else `candidate_secret_local_stub_env(server)`. Set `os.environ[env_name] = key` (the stripped plaintext already validated for SET).
3. For each clear (`key` empty): compute `env_name` the same way and `os.environ.pop(env_name, None)`.
4. Do not log `key` or `env_name` values beyond the existing warning shapes in hydrate. Do not call Railway here (Admin PUT still owns upsert/delete/deploy). Do not change hydrate's EXPIRED / missing-env rules.

After a successful Admin set on the current process, `database.get_candidate` → hydrate must include that server in `candidate_api_keys` when status is SET and `expires_at` is still in the future.

### Blast radius

- `src/core/candidate.py` — `update_candidate_api_keys` only; hydrate logic unchanged.
- Callers: `src/ui/api/api_candidate.py` Admin PUT (production Railway then this function; local skips Railway and still gets stub env from this change).
- Consumers of the map unchanged: `src/ui/api/api_admin.py` `_candidate_dispatch_api_key_error`, `src/core/dispatcher.py` missing-key gate, `src/core/agent.py` `_candidate_server_key` / Ad Hoc.
- Other workers / replicas still need the Railway deploy (or their own set) to inherit the variable; this ticket fixes the writer process and any process that runs `update_candidate_api_keys`.
- Not in scope: changing the date-select midnight expiry rule (AST-2265). A past `expires_at` still reports EXPIRED and omits the server — intentional parent AC 2.

### What must still hold

- Parent AC: EXPIRED (now ≥ expires_at) omits the server from `candidate_api_keys` and blocks dispatch the same as unset.
- Parent AC: local with Railway unset shares one stub value per secret id across candidates; no Railway call on hydrate.
- Parent AC: no Fernet encrypt on the key-update path; secret not stored in `api_keys` JSON.
- GET / sanitize never returns plaintext.
- Hydrate still warns (candidate id + secret id, not the value) when status is SET and the env value is missing — that path remains for rows SET without a matching environ entry (e.g. another replica before deploy).

## Radia review

[code-rubric]
**Ticket:** AST-2275
**Publish ref:** `7e321006f8a06a99e7126176d448ab70b787a0c4` (`origin/sub/AST-2246/AST-2275-dispatch-vault-openrouter`)
**Overall:** CLEAN

## Fix-specific checks

**[bug-repro]** — OK. Production probe + update_candidate_api_keys plants CANDIDATE_*_OPENROUTER; hydrate sees openrouter.

**## What must still hold** — OK. EXPIRED/local stub/no Fernet/GET/hydrate warning unchanged.

## Findings

Advisory only. ftr three-dot includes unrelated sibling carry; scored 2275 commit range. Env planted before DB commit accepted as rare retry case.

```
[code-rubric] PROCEED (Commit: 7e32100) Vault set plants process env
```

## Bug: AST-2283 — vault-set OpenRouter key still missing for scheduled actions and ad hoc

### As-is

After a vault set (including AST-2275's in-process plant), scheduled-action validation still marks the task invalid for a missing OpenRouter key, and Agent Ad Hoc still fails with `Candidate … has no API key for server 'openrouter'`, while Manage Candidates shows OpenRouter status SET.

### To-be

After Admin saves a non-empty OpenRouter key for that candidate (production Railway path), both `_candidate_dispatch_api_key_error` (scheduled actions / Run / Auto) and Ad Hoc resolve a non-empty `candidate_api_keys["openrouter"]` for that candidate — on the process that handled the save, and on the process that comes up after the deploy that follows the write — so those paths do not fail for a missing OpenRouter key.

### Repro

1. Production probe true (`ASTRAL_RAILWAY_TOKEN` set and non-empty). Candidate `somerset` OpenRouter status may already show SET from an earlier vault write.
2. In Manage Candidates, **re-type** a non-empty OpenRouter key, pick a future expiry date, save. (The UI only PUTs `api_keys` rows that changed; leaving the key blank does not re-enter the write path.)
3. Open Scheduled Actions for a task whose agent server is `openrouter`, and/or POST `/api/admin/adhoc/test` (Agent Ad Hoc) for `somerset` with an OpenRouter-backed agent.
4. Fail: `invalid_reason` / skipped dispatch cites a missing OpenRouter key; Ad Hoc returns `Candidate somerset has no API key for server 'openrouter'`. GET still shows OpenRouter status SET.

### Root cause

Production Admin PUT (`src/ui/api/api_candidate.py`) runs Railway upsert/delete, then **`trigger_service_deploy()`**, then `update_candidate_api_keys` (AST-2275 plant + status). Production uses a single gunicorn worker. The deploy restarts that worker and clears process-local `os.environ`, so the plant does not survive the deploy that the same PUT requested. Hydrate still builds `candidate_api_keys` only from environ; when the post-deploy process does not yet have `CANDIDATE_<ID>_OPENROUTER` (deploy signaled before plant/status finished, or the plant never ran because the worker was replaced first), the map stays empty while `candidate_secret_status` remains SET. Scheduled-action validation and Ad Hoc both gate on that map (`_candidate_dispatch_api_key_error`, `_candidate_server_key`). AST-2275 only covered the pre-restart writer process and does not reorder the Admin PUT relative to deploy.

### Proposed change

Scope (parent Component / Technical scope): `src/external/railway.py`, `src/ui/api/api_candidate.py`. Do not change hydrate's EXPIRED / missing-env rules. Do not read secrets back from Railway. Do not store ciphertext.

1. In `src/external/railway.py`, add `upsert_service_variables(variables: dict[str, str]) -> None` that one-shots the existing `variableCollectionUpsert` mutation with the full `variables` object, `skipDeploys: True`, same auth/target/`RailwayCallFailed` / redaction behavior as `upsert_service_variable`. Keep `upsert_service_variable(name=..., value=...)` as a thin wrapper that calls `upsert_service_variables({name: value})` (or equivalent one-key call) so existing callers and tests stay valid. Do not add a variable-read API.

2. In `src/ui/api/api_candidate.py`, inside the production `api_keys` branch of the candidate data PUT, replace the per-edit upsert + deploy + status order with:
   1. Build two collections from `api_key_edits` (same `candidate_secret_variable_name(server, candidate_id)` as today): `to_set` = `{env_name: stripped key}` for every non-empty key; `to_delete` = `[env_name, …]` for every clear.
   2. If `to_set` is non-empty: `upsert_service_variables(to_set)` once (all sets in one Railway call).
   3. For each name in `to_delete`: `delete_service_variable(name=name)` as today.
   4. Then `update_candidate_api_keys(candidate_id, api_key_edits)` — status + AST-2275 plant/pop — **before** any deploy trigger.
   5. Then, if `to_set` or `to_delete` is non-empty: `trigger_service_deploy()` once.
   6. Keep `RailwayCallFailed` → 502 without writing status when a Railway call fails before step 4. Local path (`ASTRAL_RAILWAY_TOKEN` unset/blank) stays: no Railway calls; only `update_candidate_api_keys`.

3. Do not change `_candidate_dispatch_api_key_error`, Ad Hoc resolve, or `hydrate_candidate_secrets` beyond what step 2 already guarantees via plant + post-deploy Railway env. Do not log key material or env values.

Done when: a production Admin set of OpenRouter (mocked Railway) calls upsert (batch) → `update_candidate_api_keys` → one `trigger_service_deploy`, in that order; after `update_candidate_api_keys` returns, `database.get_candidate` → hydrate includes `openrouter` in `candidate_api_keys` from the planted environ name; clear still deletes, plants pop, then one deploy.

### Blast radius

- `src/ui/api/api_candidate.py` — production `api_keys` PUT order and batched upsert only.
- `src/external/railway.py` — new multi-variable upsert helper; one-key wrapper behavior unchanged for callers.
- Consumers unchanged: `api_admin._candidate_dispatch_api_key_error`, `dispatcher` missing-key gate, `agent._candidate_server_key` / Ad Hoc.
- AST-2275 plant in `update_candidate_api_keys` stays; this ticket makes it run before the deploy the same PUT requests.
- Not in scope: date-select midnight expiry (AST-2265); migration script deploy policy; Railway variable read-back; multi-worker (production stays one worker).

### What must still hold

- Parent AC: Admin set records upsert + one deploy trigger and status/expiry only on the row (no ciphertext).
- Parent AC: EXPIRED (now ≥ expires_at) omits the server from `candidate_api_keys` and blocks dispatch like unset.
- Parent AC: local with Railway unset shares one stub per secret id; no Railway call on hydrate or on local Admin set.
- Parent AC: GET / sanitize never returns plaintext.
- AST-2275: set still plants (and clear pops) the process env name hydrate reads; hydrate still warns (candidate id + secret id, not the value) when status is SET and the env value is missing.
- `stat.logging.error` / `stat.logging.info.api`: Railway failures and Admin completion logs stay free of secret material.

## Radia review

[code-rubric]
**Ticket:** AST-2283
**Publish ref:** `3a24cd5075b770a78c1af744f9f7af62f13ce450` (`origin/sub/AST-2246/AST-2283-vault-key-still-missing`)
**Overall:** CLEAN

## Fix-specific checks

**[bug-repro]** — OK. Plant before deploy order + hydrate keeps OpenRouter.

**## What must still hold** — OK. Upsert + one deploy, EXPIRED/local/GET, AST-2275 plant, no-secret logging.

## Findings

Advisory only. Deletes-before-upserts order vs plan text; multi-key batch untested; post-restart env is UAT.

```
[code-rubric] PROCEED (Commit: 3a24cd5) Plant before deploy reorder
```
