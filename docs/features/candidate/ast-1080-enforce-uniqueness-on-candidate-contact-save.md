# AST-1080 — Enforce uniqueness on candidate contact save

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1080/enforce-uniqueness-on-candidate-contact-save-verify-unique-contact  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info  

**Publish ref (origin):** `sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save`  
**Parent integration ref:** `ftr/AST-1045-verify-unique-contact-info`

On the candidate contact **save** path, apply within-candidate dedupe and cross-candidate uniqueness using `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` (AST-1079): collapse duplicate identity tokens inside one candidate’s contact blob, hard-fail when a token is already held by a different live candidate, raise a toast-ready `ValueError`, and emit Style D debug when `debug=True`. Does **not** change the config vocabulary, library schema, or Profile/Admin UI.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Import uniqueness config; add private uniqueness helpers; call gate from `save_candidate_data`, `initiate_candidate`, and `initiate_prospect_candidate` after URL normalize / before DB write; Style D on touched debug paths | core |

---

## Stage 1: Uniqueness helpers + wire into contact write paths

**Done when:** Saving contact via `save_candidate_data` (and create via `initiate_candidate` / `initiate_prospect_candidate`) dedupes within-candidate uniqueness tokens in the contact blob, refuses cross-candidate collisions with a clear `ValueError` (existing API → HTTP 400 / toast), leaves the other candidate unchanged, and emits Style D found/recorded lines when `debug=True`. No config.py / UI / data-layer schema edits.

1. In `src/core/candidate.py`, add `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` to the existing `from src.utils.config import (...)` list. Update the module docstring **In-scope** line to mention contact uniqueness enforcement on save (AST-1080) next to `save_candidate_data`.

2. Add private helpers **below** `normalize_contact_urls` and **above** `save_candidate_data` (public-then-helpers: keep public functions first; place new helpers with the other contact helpers near `normalize_contact_urls`, or at the bottom helper section if that file already groups helpers after publics — **match existing file organization**: `normalize_contact_urls` is already among early helpers; add the new helpers immediately after it).

   **`_uniqueness_compare_token(raw: Any, mode: str) -> str`**
   - If `raw` is not a `str`, return `""`.
   - Strip whitespace; if empty, return `""`.
   - If `mode == "casefold"`: return `stripped.casefold()`.
   - If `mode == "exact"`: return `stripped`.
   - Otherwise treat as `"casefold"` (defensive; config asserts only those two modes).

   **`_iter_uniqueness_path_values(source: Dict[str, Any], dotted_path: str) -> list[str]`**
   - Resolve values for one config path against either a full candidate row (has `candidate_data`) **or** a bare contact dict wrapped as `{"candidate_data": {"contact": contact}}` / a synthetic row.
   - Reuse `_lookup_path_value` for scalar/email/slack string paths (it already strips; callers still run compare-token).
   - For `list_paths` entries (`contact.websites`): walk `candidate_data.contact.websites` (or contact.websites on a contact-only view). If the value is a `list`, yield each element that is a non-empty `str` after strip; if a single `str`, yield that one; ignore other types.
   - Return a list of raw stripped strings (not yet casefold/exact compared).

   **`_collect_uniqueness_tokens_from_candidate(candidate: Dict[str, Any]) -> list[tuple[str, str]]`**
   - Read `CANDIDATE_CONTACT_UNIQUENESS_CONFIG`.
   - Emit `(compare_token, path)` for every non-empty token from:
     - each path in `email_paths` with `compare["email"]`
     - each path in `scalar_paths` with `compare["scalar"]`
     - each path in `list_paths` with `compare["list"]` (one token per list entry)
     - each path in `slack_user_id_paths` with `compare["slack_user_id"]`
   - Skip empty compare tokens.
   - Deterministic path order: email_paths, then scalar_paths, then list_paths (list index order), then slack_user_id_paths.

   **`_collect_uniqueness_tokens_from_contact(contact: Dict[str, Any]) -> list[tuple[str, str]]`**
   - Build a synthetic candidate row `{"candidate_data": {"contact": contact}}` and call `_collect_uniqueness_tokens_from_candidate`. (Write-side proposed contact has no transitional `profile.*`; those paths simply resolve empty — correct.)

   **`_dedupe_contact_within(contact: dict) -> list[str]`** (mutates `contact` in place)
   - Parent OQ#2: avoid adding the same contact info twice for one candidate — **collapse**, do not hard-fail.
   - Walk uniqueness paths in the same order as `_collect_uniqueness_tokens_from_candidate` against this contact.
   - Keep a `seen: set[str]` of compare tokens already retained.
   - For scalar/email/slack paths (`contact.<key>` only — skip paths that do not start with `contact.`): if the field’s compare token is non-empty and already in `seen`, set that field to `""` and append a short note like `cleared contact.reply_email (duplicate)`; else if non-empty, add to `seen`.
   - For `contact.websites` when it is a `list`: rebuild the list keeping first occurrence of each non-empty compare token; drop later duplicates and any entry whose token was already seen from an earlier scalar/email field; assign the rebuilt list back; note removals.
   - Return the list of human-readable notes (may be empty). Do **not** invent phone digit normalization or extra URL canonicalization beyond what `normalize_contact_urls` already did.

   **`_find_cross_candidate_contact_collision(candidate_id: str, contact: dict) -> Optional[tuple[str, str, str]]`**
   - Tokens from `_collect_uniqueness_tokens_from_contact(contact)`.
   - For each other row in `list_candidates(include_deleted=False)` whose `astral_candidate_id` ≠ `candidate_id` (string strip compare): collect tokens via `_collect_uniqueness_tokens_from_candidate` (includes transitional `profile.*` email paths on the other row).
   - If any compare token overlaps, return `(token_display, path, other_candidate_id)` where `token_display` is a truncated raw-ish form suitable for errors (use the colliding stripped value from **this** contact’s path, not the other candidate’s id in the user message — see step 3).
   - Else return `None`.

   **`_enforce_contact_uniqueness(candidate_id: str, contact: dict, *, debug: bool = False) -> None`**
   - Assumes `contact` is a `dict` already passed through `normalize_contact_urls`.
   - If `debug`: `logger.set_debug_flag(True)` is the caller’s job when they already set it; still emit Style D under this function when `debug` is True.
   - Step A — within-candidate: `notes = _dedupe_contact_within(contact)`. If `debug`: one `debug_index` with `func="enforce_contact_uniqueness"`, `identifier=candidate_id`, `outcome="recorded|within_dedupe"` (or `found|within_clean` when notes empty), and `debug_detail` lines for notes / token counts (truncate long payloads with `truncate_debug_content`).
   - Step B — cross-candidate: `hit = _find_cross_candidate_contact_collision(candidate_id, contact)`. If hit: if `debug`, emit `debug_index` with `outcome="found|cross_collision"` and detail including `path`, truncated value, and `other_candidate_id`. Then **`raise ValueError`** with exactly this message shape (toast-ready, no other candidate id in the user string):

     ```text
     This contact info is already used by another candidate ({value}).
     ```

     where `{value}` is the colliding stripped value truncated to **80** characters if longer. Do **not** persist after this raise.
   - If no collision and `debug`: `debug_index` with `outcome="recorded|cross_clear"`.

⚠️ **Decision — gate lives in core on write paths, not in UI or data:** Parent architecture + citations require core validation; `api_candidate` already maps exceptions to `{"error": str(e)}` 400 (toast-ready). Data layer stays raise-only / no log.

⚠️ **Decision — within = collapse, cross = hard-fail:** Locked parent OQs #2 and #3. Collapse prefers earlier paths in config order; websites list keeps first unique entries.

⚠️ **Decision — shared helper for initiate + save:** Create paths (`initiate_candidate`, `initiate_prospect_candidate`) also write contact blobs today; collisions on create must hard-fail the same way. Do not leave a bypass around `save_candidate_data`.

3. Wire **`save_candidate_data`** after `normalize_contact_urls(contact)` and **before** building debug `steps` / calling `database.save_candidate`:

   ```python
   contact = blob.get("contact")
   if isinstance(contact, dict):
       normalize_contact_urls(contact)
       # Proposed contact after merge (merge=True) or replace payload (merge=False).
       if not replace:
           existing = database.get_candidate(candidate_id) or {}
           existing_cd = existing.get("candidate_data") or {}
           if not isinstance(existing_cd, dict):
               existing_cd = {}
           existing_contact = existing_cd.get("contact")
           if isinstance(existing_contact, dict):
               proposed = copy.deepcopy(existing_contact)
               # Same semantics as database._deep_merge for one contact overlay:
               for k, v in contact.items():
                   if (
                       k in proposed
                       and isinstance(proposed[k], dict)
                       and isinstance(v, dict)
                   ):
                       # nested dict rare under contact; still recurse shallowly
                       inner = copy.deepcopy(proposed[k])
                       for ik, iv in v.items():
                           inner[ik] = iv
                       proposed[k] = inner
                   else:
                       proposed[k] = v
           else:
               proposed = copy.deepcopy(contact)
       else:
           proposed = copy.deepcopy(contact)
       _enforce_contact_uniqueness(candidate_id, proposed, debug=debug)
       blob["contact"] = proposed  # persist deduped contact
   ```

   Use `copy` (already imported). Do **not** call `database._deep_merge` from core (private). The inline merge above must match deep-merge overwrite rules for contact’s flat keys + list replace for `websites`.

   If `contact` is not a dict (missing / wrong type), skip the gate (unchanged behavior).

4. Wire **`initiate_candidate`** and **`initiate_prospect_candidate`** after `normalize_contact_urls(contact)` and **before** `database.save_candidate`:

   ```python
   if isinstance(contact, dict):
       normalize_contact_urls(contact)
       _enforce_contact_uniqueness(astral_candidate_id, contact, debug=False)
   ```

   No `debug=` param on these create APIs today — pass `debug=False`. Do not expand their signatures.

5. Do **not** edit `src/utils/config.py`, `src/data/database.py`, UI/React, or Profile/Admin toast components (AST-1065). Do **not** silently merge two candidate records. Do **not** add legacy duplicate cleanup / migration. Do **not** change `get_candidate_id_for_query` match semantics.

**Done when (recheck):** Manual or REPL-level checks (Betty owns formal tests):

- Same email (case-insensitive) on candidate B’s save while A holds it → `ValueError` with the message above; A unchanged.
- `contact_email` and `reply_email` set to the same address on one save → reply cleared (or later path cleared), save succeeds, one retained value.
- Duplicate strings in `websites` → list collapsed; save succeeds.
- `debug=True` on `save_candidate_data` with contact changes → Style D index headers + `|` detail for within/cross steps (and existing library-write lines still work).

---

## Self-Assessment

**Scope:** `Single-Component` — `src/core/candidate.py` only; reads AST-1079 config; no UI/data schema.

**Conf:** `high` — config contract shipped; write path and API `ValueError`→400 pattern already exist; lookup already scans `list_candidates` for path values.

**Risk:** `Medium` — wrong collapse/collision logic can block legitimate saves or miss cross-candidate leaks; limited to contact write paths.

---

## Code Rules check (§8)

| Rule | Result |
|------|--------|
| §1.3 DRY | Token collection / compare shared; path vocabulary only from `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` |
| §1.4 no-hardcoded-sets | No inline unique-field lists in core |
| §2.1 config source of truth | Compare modes + paths from config |
| §1.5.1 debug-contract-gated | Style D only when `debug=True` on touched save gate |
| §2.4 batch / §2.6 state | N/A |
| §3.3 imports | Core → utils config + existing database; no UI/external |
| data-raises-caller-logs | Core raises `ValueError`; UI already logs/surfaces |

No conflicts requiring `conf-!!-NONE`.

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-1080 |
| Publish ref | `origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save` |
| Built | `a80e51c5c3e233afea30d0b73331072e8f0f2535` |
| Notes | Stage 1 — within collapse + cross hard-fail on `save_candidate_data` / initiate paths via AST-1079 config. |
