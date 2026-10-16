# AST-2252 — Admin set, clear, and expiry

Linear: [AST-2252](https://linear.app/astralcareermatch/issue/AST-2252/admin-set-clear-and-expiry-manage-candidate-secrets-in-railway)
Parent: [AST-2246](https://linear.app/astralcareermatch/issue/AST-2246/manage-candidate-secrets-in-railway)
Publish ref: `sub/AST-2246/AST-2252-admin-secret-expiry`

Manage Candidates shows SET / NOT SET / EXPIRED and the expiry, and the admin save writes a secret through Railway (upsert or delete, then one deploy) before the candidate row stores status and expiry only. GET never includes the secret. This ticket does not own the Railway client, row hydrate, or the CSE call site.

## Scope check

This ticket's Scope names only:

- `src/ui/api/api_candidate.py` — set/clear/expiry contract; GET returns status and expiry, never the secret
- `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — SET / NOT SET / EXPIRED, expiry field, set and clear

Do not edit `src/external/railway.py`, `src/utils/config.py`, `env.example`, `src/data/database.py`, `src/core/candidate.py`, `scripts/migrations/migrate_candidate_api_keys_to_railway.py`, `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, `src/external/google_cse.py`, `src/core/timesheets.py`, `src/core/roster.py`, or `scripts/spikes/ast489_google_cse_company_search_spike.py`.

Call `upsert_service_variable`, `delete_service_variable`, and `trigger_service_deploy` from the admin PUT. Those functions already exist (AST-2250). Call `update_candidate_api_keys` as it exists after AST-2251: a non-empty `key` plus `expires_at` stores `SET` and the timestamp and does not persist the key; an empty `key` stores `NOT SET` and `expires_at` null. Do not change those functions.

`candidate_secret_status` on a parsed row is the GET source. Hydrate already rewrites a past `expires_at` to reported status `EXPIRED` and leaves `expires_at` as stored. A server with no status row is NOT SET. Plaintext stays in `candidate_api_keys` until sanitize pops it.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_candidate.py` | PUT set/clear calls Railway then status write. GET `api_keys` is status and expiry, never the secret. | ui |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | List and edit show SET / NOT SET / EXPIRED and expiry. Set collects secret and expiry. Clear sends clear. Search catalog ids are on the form. | ui |

## Stage 1: Admin API set, clear, expiry, and GET

**Done when:** `PUT /api/candidates/<id>/data` with one non-empty `api_keys[].key` and `expires_at` calls `upsert_service_variable` once and `trigger_service_deploy` once when `ASTRAL_RAILWAY_TOKEN` is set and non-empty, then `update_candidate_api_keys` with that server, key, and `expires_at`. The JSON response has `status` and `expires_at` for that server and does not contain the secret string. The same PUT with `ASTRAL_RAILWAY_TOKEN` unset does not call Railway and still stores status and expiry. A clear (`key` `""`) calls `delete_service_variable` once and `trigger_service_deploy` once in production, then stores `NOT SET`.

1. In `src/ui/api/api_candidate.py`, add `import os`. From `src.utils.config` also import `CANDIDATE_SECRET_CATALOG`, `CANDIDATE_SECRET_RAILWAY_CONFIG`, and `candidate_secret_variable_name`. From `src.external.railway` import `RailwayCallFailed`, `delete_service_variable`, `trigger_service_deploy`, and `upsert_service_variable`. Keep `LLM_SERVER_CONFIG` for labels.

2. Replace `_sanitize_candidate`. Pop `candidate_api_keys`, `candidate_api_key`, `candidate_secret_status`, and `_legacy_secret_ids`. Build `c["api_keys"]` from the popped status dict in its existing order. Each element is `{"server", "label", "status", "expires_at"}` only. `label` is `LLM_SERVER_CONFIG[sid]["label"]` when that server is in `LLM_SERVER_CONFIG`, else `"Google CSE API key"` for `google_cse_api_key`, else `"Google CSE engine id"` for `google_cse_id`, else `sid`. `status` is the reported status string (`SET`, `NOT SET`, or `EXPIRED`). `expires_at` is the stored value (`str` or `None`). Do not copy any `key` field. Do not read `os.environ` here.

3. In `update_candidate_data`, replace the `api_keys` validation and the later `update_candidate_api_keys` call.
   - Docstring: `api_keys` is `[{server, key, expires_at}]`. Non-empty `key` sets that catalog id and requires `expires_at` `YYYY-MM-DD HH:MM:SS`. `key` `""` clears it. Duplicate `server` → 400. The secret is not returned.
   - Still require admin when `api_keys` is present.
   - `api_keys` must be a list or 400 `{"error": "api_keys must be an array of {server, key}"}`.
   - For each entry, `server` must be a key of `CANDIDATE_SECRET_CATALOG` and `key` must be a `str`, else 400 `{"error": "Invalid api_keys entry for server <sid>"}` using `repr(sid)`. Do not include `key` or `expires_at` in the error. Duplicate `server` → 400 `{"error": "Duplicate api_keys entry for server <sid>"}`.
   - If `key.strip()` is non-empty: `expires_at` must be a `str` whose strip is non-empty, else 400 `{"error": "expires_at is required"}`. `datetime.strptime(stripped, "%Y-%m-%d %H:%M:%S")` must succeed, else 400 `{"error": "expires_at must be YYYY-MM-DD HH:MM:SS"}`. Import `datetime` from `datetime` in this module.
   - Empty `key` ignores `expires_at`.
   - After the existing state-transition block, if `api_keys` is non-empty:
     - Production is `CANDIDATE_SECRET_RAILWAY_CONFIG["token_env"]` in `os.environ` and `os.environ[that name].strip()` non-empty. Same rule as `hydrate_candidate_secrets`.
     - Production: for each entry in request order, `name = candidate_secret_variable_name(server, candidate_id)`. Non-empty stripped key → `upsert_service_variable(name=name, value=stripped key)`. Empty key → `delete_service_variable(name=name)`. After every entry succeeds, call `trigger_service_deploy()` once. Then `update_candidate_api_keys(candidate_id, entries)` where each entry is `{"server", "key": stripped key, "expires_at": stripped expires_at}` for a set, and `{"server", "key": ""}` for a clear.
     - Not production: do not call `upsert_service_variable`, `delete_service_variable`, or `trigger_service_deploy`. Call `update_candidate_api_keys` with the same entry shape.
   - Catch `RailwayCallFailed` before the broad `except Exception`. Return `jsonify({"error": str(exc)}), 502`. Do not `logger.exception` and do not `logger.error`. The railway module already logged the fault. `str(exc)` is the operation and variable name only.
   - Leave the existing success `logger.info("%s | api %s completed: PUT %s", ...)` block as it is, including the keys-only condition that skips a second line when an artifact completion line already fired. Do not add another info line. Do not put `key` or `expires_at` in that message.

⚠️ **Decision:** One deploy after every upsert and delete in that PUT, not one deploy per secret. AC 2's single-secret set is one upsert and one deploy. A save that changes two secrets still deploys once.

⚠️ **Decision:** Railway runs before `update_candidate_api_keys`. A `RailwayCallFailed` leaves the row unchanged. A later database error can leave the variable updated and the deploy already triggered; the operator retries the save. Local (`ASTRAL_RAILWAY_TOKEN` unset or blank) never calls Railway. The typed secret is not stored; hydrate reads the shared stub only when status is SET.

⚠️ **Decision:** Search ids `google_cse_api_key` and `google_cse_id` are valid `server` values because they are in `CANDIDATE_SECRET_CATALOG`. `LLM_SERVER_CONFIG` remains the label source for model servers only.

## Stage 2: Manage Candidates status, expiry, set, and clear

**Done when:** The manage list shows each returned secret as `label STATUS` plus the expiry string when present, colored SET / NOT SET / EXPIRED. The edit modal shows that status and expiry, a password field, an expiry field, and Clear on SET or EXPIRED. Save with a typed secret sends `{server, key, expires_at}`. Clear sends `{server, key: ""}`. A blank secret field sends nothing for that server.

1. In `AdminManageCandidates.tsx`, extend `api_keys` on `Candidate` to `{ server: string; label: string; status?: string; expires_at?: string | null }`.

2. In the `/api/admin/agents/models` loader, after the deduped server list, append `{ server: "google_cse_api_key", label: "Google CSE API key" }` and `{ server: "google_cse_id", label: "Google CSE engine id" }` when that `server` is not already present.

3. Add `keyExpires` state `Record<string, string>`, reset to `{}` in `openEdit` next to `setKeyInputs({})`.

4. Replace `flattenCandidate`'s `api_key_status` join. It is unused for color. The column render below reads `row.api_keys`.

5. Replace the `api_key_status` column `render`. Signature `(val, row)`. Read `row.api_keys ?? []`. Empty array: `<span style={{ color: "var(--warning)", fontWeight: 600, fontSize: 12 }}>⚠️ Not set</span>`. Otherwise one span per entry, `key={server}`, `fontWeight: 600`, `fontSize: 12`, color `var(--success)` for `SET`, `var(--danger)` for `EXPIRED`, `var(--warning)` otherwise. Text is `` `${i ? ", " : ""}${label} ${status}` `` plus `` ` ${expires_at}` `` when `expires_at` is a non-empty string. `status` missing means `NOT SET`.

6. Replace `keyRows`. For each `keyServers` entry, status is the matching `storedKeys` entry's `status` or `"NOT SET"`, and `expires_at` is that entry's `expires_at` or `null`. Then append `storedKeys` whose `server` is not in `keyServers`, with `status` defaulting to `"NOT SET"`.

7. In the key field block, set the label to `` `${label} · ${status}` `` plus `` ` · ${expires_at}` `` when `expires_at` is a non-empty string. Under the password row, add a text input, class `dep-input`, `autoComplete="off"`, placeholder `YYYY-MM-DD HH:MM:SS UTC`, value `keyExpires[sid] ?? ""`, `onChange` writes `keyExpires[sid]`. Show the Clear button when `status` is `SET` or `EXPIRED`, `keyInputs[sid]` is empty, and `clearKeys[sid]` is not set. Clear still confirms, then `setClearKeys`. When `clearKeys[sid]` is set, the label suffix is ` · will clear on save`.

8. In `handleEditSave`, build `api_keys` as `{ server: string; key: string; expires_at?: string }[]`. For each `keyRows` server: if `clearKeys[sid]`, push `{ server: sid, key: "" }`. Else if `keyInputs[sid]` trims non-empty, require `keyExpires[sid]` trim to match `/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/`. On mismatch, `setToast({ text: "Expiry must be YYYY-MM-DD HH:MM:SS UTC", variant: "error" })` and return before `api()`. On match, push `{ server: sid, key: trimmed key, expires_at: trimmed expiry }`. Otherwise omit that server. Attach `payload.api_keys` only when the array is non-empty.

⚠️ **Decision:** Expiry is a UTC text field in `YYYY-MM-DD HH:MM:SS`, the same string `update_candidate_api_keys` parses. No `datetime-local` conversion.

⚠️ **Decision:** Leaving the secret blank does not change expiry. AST-2251 only writes `expires_at` on a non-empty key. Clear is the empty key. There is no expiry-only save.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2252
**Overall:** APPROVED
**Corpus:** 65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91
**Publish ref:** `sub/AST-2246/AST-2252-admin-secret-expiry` @ `7eb04bc6a9f9dfa8cedb54b1e434c17980e413fc`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | A | | |
| new candidate-secret pattern (pending Archie) | B | | |

## Traceability

`2 → Stage 1 (production PUT: upsert/delete then one trigger_service_deploy, then update_candidate_api_keys status-only); 3 → Stage 1 _sanitize_candidate (api_keys = label/status/expires_at, pops candidate_api_keys and plaintext)`

## Findings

### discuss — Canon Scope gap (layers)

- **Severity:** discuss
- **Location:** Stage 1 step 1 — `api_candidate.py` imports `src.external.railway`
- **Finding:** `astral.layers.import-direction` restricts ui → core + utils; direct ui → external calls exist elsewhere (e.g. telescope routes) but the statute is not on this child’s Citations list.
- **Recommendation:** Archie may add import-direction for Radia parity; not a reason to widen or score off-list here. Pattern matches established admin API → external I/O in this codebase.

### discuss — Pattern not in corpus

- **Severity:** discuss
- **Location:** Citations / Stage 1 decisions
- **Finding:** Candidate-secret pattern remains pending Archie approval with no canon file.
- **Recommendation:** Plan matches epic intent (Railway before row write, GET never returns secret, production vs local gate on `ASTRAL_RAILWAY_TOKEN`).

### discuss — Railway-before-row ordering

- **Severity:** discuss
- **Location:** Stage 1 decision (Railway then DB; 502 leaves row unchanged)
- **Finding:** A DB failure after a successful Railway write + deploy can leave the variable updated while status lags until retry.
- **Recommendation:** Acceptable trade documented in plan; operator retry is the recovery path—not a plan blocker.

### acceptable — AC 2 component test not in this diff

- **Severity:** acceptable
- **Location:** Child AC 2 / Scope check
- **Finding:** Full “Admin set” component test is Betty’s lane; this ticket wires the PUT path the test will assert against.
- **Recommendation:** None.

### acceptable — Depends on AST-2250 / AST-2251

- **Severity:** acceptable
- **Location:** Scope check
- **Finding:** Railway helpers and `update_candidate_api_keys` + `candidate_secret_status` behavior are assumed from prior siblings.
- **Recommendation:** Land #1 and #2 on ftr before build.

context_tokens≈48000
