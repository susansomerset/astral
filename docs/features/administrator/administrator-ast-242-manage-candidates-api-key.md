# AST-242 — Manage Candidates — API Key
**Component:** administrator  
**Children:** AST-251, AST-252, AST-253, AST-254 (documented inline; no per-ticket commit trail)  
**Linear archived:** AST-242 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-02 08:25 | AST-242 | — | `e19bef988` | Add Fernet encryption for candidate API keys |
| 2026-03-02 08:36 | AST-242 | — | `8ee0b6f03` | Enhance candidate API key handling and encryption logic |
| 2026-03-02 08:36 | AST-242 | — | `9bacc7eb6` | Refactor candidate API key management and enhance error handling |
| 2026-03-02 08:39 | AST-242 | merge | `53ae723de` | Merge pull request #26 from susansomerset/chuckles/ast-242-manage-candidates-api-key |
| 2026-03-02 08:58 | AST-242 | — | `b017eb864` | Add optional `has_api_key` field to Candidate interface |
| 2026-03-02 08:59 | AST-242 | merge | `5a162c7bf` | Merge pull request #27 from susansomerset/chuckles/ast-242-manage-candidates-api-key |

_Pre-`verb(AST-NNN)` era: feature commits do not name the ticket in the subject; they are reachable via the two named PR merges. Path convention was `ui/…`. Sub-issue tickets AST-251–254 have no individual commits._

## Epic — AST-242
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-242/manage-candidates-api-key · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: High / 3_

### Original brief

Add encrypted Anthropic API key management to the existing Manage Candidates screen. This is the only addition needed to complete Manage Candidates as a feature.

**Acceptance Criteria:**

**Candidate Table:**

* Add top-level column `candidate_api_key` (TEXT, encrypted at rest) to the candidate table
* `get_candidate()` returns this field alongside `candidate_id`, `state`, `candidate_data`
* `candidate.py` gets `get_api_key(candidate)` function: decrypts and returns key, raises `ValueError` if missing or blank — no fallback to system key

**Edit Modal (Manage Candidates screen):**

* Add API key field: masked input (password-style) with a reveal toggle
* Save replaces existing key — no clear action, replacement only
* Validation: key must be non-blank on save

**List View:**

* Add API key status indicator column: '🔑 Set' or '⚠️ Not set'
* No key value displayed in list — status only

**Nav Cleanup (include in this issue):**

* Remove Analysis Instructions from NAV_CONFIG and routes.tsx
* Remove Resume Framework from NAV_CONFIG and routes.tsx
* Rename 'Scheduled Actions' → 'Task Dispatcher' in NAV_CONFIG and routes.tsx
* Rename 'Performance Monitor' → 'Execution History' in NAV_CONFIG and routes.tsx

**Database:**

* candidate table: ALTER to add `candidate_api_key` TEXT column
* Encryption/decryption handled in [database.py](<http://database.py>) or [candidate.py](<http://candidate.py>) (encrypted at rest, decrypted once by `candidate.get_api_key()`)
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1

#### Comments

_No comments._

### Files changed (plan vs actual)

Sub-issue plans (below) → actual across PRs #26 / #27. Era path convention `ui/…`.

| | file | planned (sub) | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | 251 — `candidate_api_key` column, idempotent migration, `_encrypt_value` / `_decrypt_value` (Fernet), `save_candidate` encrypt, `get_candidate` returns it, docstring | `e19bef988` `8ee0b6f03` `9bacc7eb6` |
| ✓ | `src/core/candidate.py` | 251 — `get_api_key(candidate) -> str`, raises `ValueError` if missing/blank, no system-key fallback | `8ee0b6f03` `9bacc7eb6` |
| ✓ | `src/ui/api/candidate.py` | 251 — extend `PUT /api/candidates/<id>/data`: pop `api_key`, encrypt, pass to `save_candidate`; never echo the key back | `9bacc7eb6` (`ui/api/candidate.py`) |
| ✓ | `requirements.txt` | 251 — add `cryptography` (Fernet) | `e19bef988` |
| ✓ | `env.example` | 251 — `ASTRAL_ENCRYPTION_KEY` | `e19bef988` |
| ✓ | `src/ui/frontend/src/pages/Admin/ManageCandidates.tsx` | 252 — masked API key field + reveal toggle in edit modal, non-blank validation, no key field in Add modal; 253 — status-only column ('Set' green / 'Not set' amber) | `9bacc7eb6` `b017eb864` (`has_api_key` field) |
| ✓ | `src/utils/config.py` | 253 — status column in `DATA_SHAPES candidates.list.manage`; 254 — remove `Analysis Instructions` / `Resume Framework` from NAV_CONFIG, rename `Scheduled Actions` → `Task Dispatcher`, `Performance Monitor` → `Execution History` | `9bacc7eb6` |
| ✓ | `src/ui/frontend/src/routes.tsx` | 254 — remove matching routes; page component files may stay (dead code) | `9bacc7eb6` (`ui/frontend/src/routes.tsx`) |
| | _linear-import docs_ | — | `docs/linear-imports/admin-features{,-subissues}.csv` (`53ae723de`) |

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-251 — Database schema, encryption, get_api_key and endpoint wiring
_Linear: https://linear.app/astralcareermatch/issue/AST-251/database-schema-encryption-get-api-key-and-endpoint-wiring · Status: Done · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Add encrypted API key column to candidate table, build encryption helpers, add get_api_key core function, and wire save into existing PUT endpoint.

* ALTER candidate table: add `candidate_api_key` TEXT column
* Idempotent migration in `_ensure_candidate_schema()` in src/data/database.py
* Add `cryptography` (Fernet) to requirements
* Encryption key from env var (e.g. `ASTRAL_ENCRYPTION_KEY`)
* Two helper functions in [database.py](<http://database.py>): `_encrypt_value(plaintext) -> ciphertext`, `_decrypt_value(ciphertext) -> plaintext`
* `save_candidate()` encrypts `candidate_api_key` before writing
* `get_candidate()` returns `candidate_api_key` (encrypted) as part of the candidate dict — the raft carries it
* Add `get_api_key(candidate: dict) -> str` to src/core/candidate.py: decrypts `candidate_api_key` from the candidate dict, raises `ValueError` if missing or blank — no fallback to system key
* Extend existing `PUT /api/candidates/<id>/data` in ui/api/candidate.py: pop `api_key` from body (same pattern as `state` override), encrypt, pass to `save_candidate()` as `candidate_api_key` — no new endpoint
* Never echo the key value back in any response; list endpoint returns truthiness only
* Update [database.py](<http://database.py>) module docstring per ASTRAL_CODE_RULES 1.1

**Layer:** src/data/database.py, src/core/candidate.py, ui/api/candidate.py

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-252 — Edit modal — API key field
_Linear: https://linear.app/astralcareermatch/issue/AST-252/edit-modal-api-key-field · Status: Done · Priority: Medium · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Add masked API key input to the existing Manage Candidates edit modal.

* In ui/frontend/src/pages/Admin/ManageCandidates.tsx, add API key field to edit modal
* Masked input (`type="password"`) with a reveal toggle button
* Saves through existing PUT endpoint alongside other candidate fields
* Validation: key must be non-blank on save
* No key field in Add modal (key is added after candidate creation)

**Layer:** ui/frontend/src/pages/Admin/ManageCandidates.tsx

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-253 — List view — API key status indicator
_Linear: https://linear.app/astralcareermatch/issue/AST-253/list-view-api-key-status-indicator · Status: Done · Priority: Medium · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Add a status-only column to the Manage Candidates list showing whether each candidate has an API key set.

* Add `api_key_status` computed value to list endpoint response (or compute client-side from candidate dict truthiness)
* List shows status only: 'Set' (green) or 'Not set' (amber) — never the key value
* Add column to DATA_SHAPES `candidates.list.manage` in src/utils/config.py, or handle as a client-side render column (same pattern as the existing `_actions` column)

**Layer:** src/utils/config.py, ui/frontend/src/pages/Admin/ManageCandidates.tsx

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-254 — Nav cleanup — remove and rename items
_Linear: https://linear.app/astralcareermatch/issue/AST-254/nav-cleanup-remove-and-rename-items · Status: Done · Priority: Medium · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Remove obsolete nav items and rename placeholders to match their intended features.

* Remove from NAV_CONFIG in src/utils/config.py:
  * `Analysis Instructions` (path: `/admin/analysis_instructions`)
  * `Resume Framework` (path: `/admin/resume_framework`)
* Rename in NAV_CONFIG:
  * `Scheduled Actions` → `Task Dispatcher`
  * `Performance Monitor` → `Execution History`
* Remove matching routes from ui/frontend/src/routes.tsx
* Page component files can stay (dead code cleanup, no functional impact)

**Layer:** src/utils/config.py, ui/frontend/src/routes.tsx

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_
