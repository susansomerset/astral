# AST-242 — Manage Candidates — API Key

<!-- linear-archive: AST-242 archived 2026-06-03 -->

## Linear archive (AST-242)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-242/manage-candidates-api-key  
**Status at archive:** Done  
**Project:** Astral Administrator  
**Assignee:** susan  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

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

# Manage Candidates — API Key

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
* Never echo the key value back in any response; list endpoint returns truthiness only (see list view subissue)
* Update [database.py](<http://database.py>) module docstring per ASTRAL_CODE_RULES 1.1

**Layer:** src/data/database.py, src/core/candidate.py, ui/api/candidate.py

## Metadata

* URL: [AST-251](https://linear.app/astralcareermatch/issue/AST-251/database-schema-encryption-get-api-key-and-endpoint-wiring)
* Identifier: [AST-251](https://linear.app/astralcareermatch/issue/AST-251/database-schema-encryption-get-api-key-and-endpoint-wiring)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:15.353Z
* Updated: 2026-03-02T20:07:04.028Z

---

# Manage Candidates — API Key

**Scope:** Add masked API key input to the existing Manage Candidates edit modal.

* In ui/frontend/src/pages/Admin/ManageCandidates.tsx, add API key field to edit modal
* Masked input (`type="password"`) with a reveal toggle button
* Saves through existing PUT endpoint alongside other candidate fields
* Validation: key must be non-blank on save
* No key field in Add modal (key is added after candidate creation)

**Layer:** ui/frontend/src/pages/Admin/ManageCandidates.tsx

## Metadata

* URL: [AST-252](https://linear.app/astralcareermatch/issue/AST-252/edit-modal-api-key-field)
* Identifier: [AST-252](https://linear.app/astralcareermatch/issue/AST-252/edit-modal-api-key-field)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:16.746Z
* Updated: 2026-03-02T20:07:03.973Z

---

# Manage Candidates — API Key

**Scope:** Add a status-only column to the Manage Candidates list showing whether each candidate has an API key set.

* Add `api_key_status` computed value to list endpoint response (or compute client-side from candidate dict truthiness)
* List shows status only: 'Set' (green) or 'Not set' (amber) — never the key value
* Add column to DATA_SHAPES `candidates.list.manage` in src/utils/config.py, or handle as a client-side render column (same pattern as the existing `_actions` column)

**Layer:** src/utils/config.py, ui/frontend/src/pages/Admin/ManageCandidates.tsx

## Metadata

* URL: [AST-253](https://linear.app/astralcareermatch/issue/AST-253/list-view-api-key-status-indicator)
* Identifier: [AST-253](https://linear.app/astralcareermatch/issue/AST-253/list-view-api-key-status-indicator)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:17.705Z
* Updated: 2026-03-02T20:07:03.933Z

---

# Manage Candidates — API Key

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

## Metadata

* URL: [AST-254](https://linear.app/astralcareermatch/issue/AST-254/nav-cleanup-remove-and-rename-items)
* Identifier: [AST-254](https://linear.app/astralcareermatch/issue/AST-254/nav-cleanup-remove-and-rename-items)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:18.710Z
* Updated: 2026-03-02T20:07:03.893Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
