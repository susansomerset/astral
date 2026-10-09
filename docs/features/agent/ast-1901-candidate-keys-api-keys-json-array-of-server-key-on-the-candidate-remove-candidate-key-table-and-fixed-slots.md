# AST-1901 — Candidate keys: api_keys JSON array of {server, key} on the candidate — remove candidate_key table and fixed slots

<!-- linear-archive: AST-1901 archived 2026-10-08 -->

## Linear archive (AST-1901)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1901/candidate-keys-api-keys-json-array-of-server-key-on-the-candidate  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1851 — Support OpenRouter API models for agent work  
**Blocked by / blocks / related:** parent: AST-1851

### Description

Susan's UAT comment on AST-1851 (verbatim, 2026-09-30T22:37:25Z):

> \[bug\] @chuckles This implementation for the candidate key management is completely wrong.  It needs to be an array of JSON between model and key, not 4 hardcoded keys.  Candidate_key should not exist.

## As-is / to-be

* **As-is:** Candidate API keys live in a separate `candidate_key` table (AST-1878: one Fernet row per candidate × LLM server, `set/clear/list_candidate_server_key(s)`, hydrated as `candidate_api_keys {server_id: key}`). Admin shows four fixed key slots.
* **To-be:** The candidate has a JSON array of `{model, key}` entries, with any number of entries and no fixed slots. The `candidate_key` table does not exist. Routing, Invalid/Run gates and Manage Candidates read and edit that array.

## Suggested engineer

Hedy (AST-1878 built `candidate_key` and the candidate key hydrate). This also touches the AST-1880 admin/API surface (Ada) and the AST-1879 key lookup in routing (Katherine).

### Comments

#### radia — 2026-09-30T23:02:33.377Z
[code-rubric] PROCEED (Commit: 5835782f1) api_keys array; drop candidate_key

#### betty — 2026-09-30T22:57:15.070Z
[bug-repro]
`origin/sub/AST-1851/AST-1901-candidate-keys-json-array` @ `5e60627f8` · repro lands red, awaits fix

#### joan — 2026-09-30T22:48:34.259Z
[board-joan]  CANON: OK

#### betty — 2026-09-30T22:48:12.091Z
[board-betty] TESTS: REVISE
What: docs/test-bible/data/database/candidates.md + ui/api/api_candidate.md + frontend/pages.md — broken tests + missing repro coverage — the fix removes candidate_key and set/clear_candidate_server_key and changes api_keys from a dict to an array. That breaks `test_candidates.py::TestAst1878CandidateServerKeys` plus the hard-delete `counts["candidate_key"]`, `test_candidate.py` set/clear_candidate_api_key facades, 28 dict-shaped `api_keys` asserts in `test_api_candidate.py`, and the fixed-slot fixtures and PUT asserts in `test_AdminManageCandidates.test.tsx`. No test covers the new cases: the api_keys array round-trip, rejecting a duplicate server, schema setup dropping candidate_key, and the add-picker.

#### hedy — 2026-09-30T22:47:29.190Z
`origin/sub/AST-1851/AST-1901-candidate-keys-json-array` @ `a53106017` · api_keys array plan ready

#### susan — 2026-09-30T22:44:05.658Z
1B (avoid duplicate key storage), 2A (api_keys is perfect)

#### hedy — 2026-09-30T22:42:25.629Z
[plan-discuss] round=1 concern
@susan: two design questions before I can plan AST-1901. The ticket, the parent and the AST-1878 doc don't settle either one.

**1. Is each entry keyed by model or by LLM server?**
Your comment says "an array of JSON between model and key". The parent's functional scope 5 and AC 6 say "one API key per platform … two models on the same platform share that key". Today each server serves exactly one catalog model (kimi-k2.6 on Kimi, kimi-k2.6-openrouter on OpenRouter, claude on Anthropic, deepseek-v4 on DeepSeek), so the two readings behave the same now. They split as soon as a second model is added on the same server.
- **(A) Recommended: by model.** Entries look like `{"model": "<LLM_MODEL_CONFIG id>", "key": "…"}`. A task uses the entry whose `model` equals the agent's `model_id`. If there is no entry, the task is Invalid and there is no fallback to another model's key. This follows your wording, and it amends parent functional scope 5 and AC 6.
- (B) By server: `{"server": "<LLM_SERVER_CONFIG id>", "key": "…"}`. This keeps the parent's one-key-per-platform rule and only changes where the keys are stored.

**2. Where does the array live on the candidate?**
- **(A) Recommended: a dedicated JSON-array column on the `candidate` row** (working name `api_keys`). Each entry's `key` is stored Fernet-encrypted and the `model` is plaintext. `get_candidate` decrypts the keys, and outbound admin responses show which models have a key set but never the key itself. The legacy `candidate_api_key` column stays unused.
- (B) Reuse the legacy `candidate_api_key` column to hold the array.
- (C) Store it inside `candidate_data`. Not recommended: `candidate_data` feeds prompt tokens and exports, so keys could leak.

Both options drop the `candidate_key` table: stop creating it, remove its helpers, and remove the cascade delete. Unless you say otherwise, I'll also reject a second entry for the same model or server on save.

Reply with 1A/1B and 2A/2B/2C (or "recommended"), then assign this bug to Chuckles and I'll resume plan-fix.

---

_Implementation detail may live in git history on `origin/dev`._
