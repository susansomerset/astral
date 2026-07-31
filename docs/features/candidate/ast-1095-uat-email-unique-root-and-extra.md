# UAT: new email must be unique vs all root and extra emails

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1095/uat-new-email-must-be-unique-vs-all-root-and-extra-emails  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info  

**Publish ref (origin):** `sub/AST-1045/AST-1095-uat-email-unique-root-and-extra`  
**Parent integration ref:** `ftr/AST-1045-verify-unique-contact-info`

UAT fix under AST-1045: treat every candidate email — root scalars (`contact.contact_email` / `contact.reply_email`, plus transitional `profile.*`) and list entries in `contact.extra_emails` — as **one shared uniqueness pool** across the live candidate table on every contact write path that already runs the AST-1080 gate. Collision hard-fails with the existing toast-ready `ValueError`. Does **not** change Profile/Admin UI, library schema, Slack Contact, or the candidate state machine.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): “Saving contact data for a candidate that would duplicate a uniqueness-scoped contact value already held by a different candidate is refused; the other candidate's data is unchanged.” / “A refused uniqueness save surfaces a clear error to the save caller suitable for UI/API display.” / “After enforcement, two live candidates cannot both hold the same uniqueness-scoped email (going forward).”
- **Correct outcome:** Adding any email (root field or an `extra_emails` entry) hard-fails when that address (casefold) is already held by another live candidate as a root email **or** as an extra email; the other candidate is unchanged; caller gets the existing domain error suitable for toast/UI.
- **Sibling check:** AST-1079 uniqueness vocabulary + AST-1080 save gate remain the home; AST-1092 added `extra_emails` / `email_list_paths` and parked extras under uniqueness `list_paths` next to websites — this ticket makes the **email** shared pool explicit (email scalars + email list paths under email compare) so root↔extra cannot drift if list compare or list membership changes. Soft-related AST-1065 still only surfaces the error.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** UI-only toast without backend refusal; checking only root-vs-root or only extra-vs-extra; catch-all swallow; Profile rewrite under AST-1065; stuffing extras into `websites` for uniqueness.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `email_list_paths` on `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` by identity from lookup; keep `contact.extra_emails` out of uniqueness `list_paths` (websites-only lists); update asserts/comments so email pool = `email_paths` ∪ `email_list_paths` under `compare["email"]` | utils |
| `src/core/candidate.py` | Collect / within-dedupe / cross-collision walk `email_list_paths` with email compare (skip those paths when walking `list_paths`); coerce `extra_emails` (and websites) on initiate paths before the gate, matching `save_candidate_data` | core |

**Out of Files Changed:** Profile/Admin UI (`src/ui/`), contact library schema (AST-1014), Slack Contact / Estelle, `get_candidate_id_for_query` match semantics (already expands `email_list_paths`), data-layer schema, tests/bible (Betty).

---

## Stage 1: Explicit shared email pool (config + gate)

**Done when:** Uniqueness config names `email_list_paths` (same object as lookup); uniqueness `list_paths` is non-email lists only (`contact.websites`); `_collect_uniqueness_tokens_from_*`, `_dedupe_contact_within`, and `_find_cross_candidate_contact_collision` treat root email paths and `email_list_paths` as one casefold email pool; `save_candidate_data` / `initiate_candidate` / `initiate_prospect_candidate` refuse cross-candidate root↔extra and extra↔root collisions with the existing toast message; initiate paths coerce `extra_emails` like save before the gate; other candidate rows are unchanged on refuse.

1. In `src/utils/config.py` `CANDIDATE_CONTACT_UNIQUENESS_CONFIG`:
   - Add `"email_list_paths": CANDIDATE_LOOKUP_CONFIG["email_list_paths"]` (same object identity — bind vocabulary and uniqueness share one list-email set).
   - Change `"list_paths"` to **only** `("contact.websites",)` — do **not** keep `contact.extra_emails` in `list_paths` (extras are email-pool members via `email_list_paths`, not generic list tokens beside websites).
   - Update the block comment: email uniqueness pool = `email_paths` ∪ `email_list_paths` with `compare["email"]`; `list_paths` are non-email list identity fields with `compare["list"]`.
   - Replace the assert that required every lookup `email_list_paths` entry ∈ uniqueness `list_paths` with:
     - `assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_list_paths"] is CANDIDATE_LOOKUP_CONFIG["email_list_paths"]`
     - each uniqueness `email_list_paths` entry starts with `"contact."` and key ∈ `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`
     - no uniqueness `email_list_paths` entry appears in uniqueness `list_paths` (no double registration)
   - Keep existing asserts that still apply (`email_paths` / `slack_user_id_paths` identity, compare modes, scopes, scalar/list path shapes).

⚠️ **Decision — email pool is first-class, not “extras happen to sit in list_paths”:** AST-1092 correctly registered extras for bind + parked them on uniqueness `list_paths`. UAT requires root and extra to be one **email** pool; parking extras next to websites makes email uniqueness depend on list compare and list membership. Promote `email_list_paths` onto the uniqueness block (by identity) and leave `list_paths` for non-email lists.

2. In `src/core/candidate.py`, update uniqueness helpers (same private helpers introduced by AST-1080 — do **not** add a second gate):

   **`_iter_uniqueness_path_values`**
   - Treat a path as list-valued when it is in `cfg["list_paths"]` **or** `cfg["email_list_paths"]` (same walk: `candidate_data` → segments → list/str entries). Scalar/email-scalar paths still use `_lookup_path_value`.

   **`_collect_uniqueness_tokens_from_candidate`**
   - Emit tokens in this order with these compare modes:
     1. `email_paths` → `compare["email"]`
     2. `email_list_paths` → `compare["email"]` (one token per non-empty list entry)
     3. `scalar_paths` → `compare["scalar"]`
     4. `list_paths` → `compare["list"]` (websites only after Stage 1 config)
     5. `slack_user_id_paths` → `compare["slack_user_id"]`
   - Do **not** also emit `email_list_paths` entries a second time via `list_paths`.

   **`_dedupe_contact_within`**
   - After scalar email / scalar / slack collapse into `seen`, process **email list** keys from `email_list_paths` (`contact.<key>` only) with `compare["email"]` using the same keep-first list rebuild as today’s list-path dedupe.
   - Then process remaining `list_paths` with `compare["list"]` as today.
   - Within one candidate, a root email and the same address in `extra_emails` still collapses (extra entry dropped / root kept when root is earlier in path order).

   **`_find_cross_candidate_contact_collision` / `_enforce_contact_uniqueness`**
   - No new public API. Collision detection continues to use the shared compare-token set from `_collect_*` — after the collect change, root↔extra and extra↔root across candidates hard-fail.
   - Keep the existing toast message shape exactly:
     `This contact info is already used by another candidate ({value}).`
   - Include `email_list_paths` when building `display_by_path` for contact.* paths (same pattern as today’s list_paths loop).
   - Style D: keep existing `enforce_contact_uniqueness` debug lines when `debug=True`; no new debug surface required beyond whatever already fires on the touched save path.

3. **Initiate coerce parity** — in `initiate_candidate` and `initiate_prospect_candidate`, when `contact` is a `dict`, before `normalize_contact_urls` / `_enforce_contact_uniqueness`, apply the same `websites` / `extra_emails` coerce block already used in `save_candidate_data` (`None`→`[]`, list→trimmed non-empty strings, else `ValueError` with the same messages). Do **not** leave create paths able to skip list-email tokens because coerce never ran.

4. Do **not** edit UI, `get_candidate_id_for_query` (already expands lookup `email_list_paths`), or invent a second uniqueness scan. Do **not** change the hard-fail vs collapse product rules (parent OQs stay locked).

⚠️ **Decision — core reads uniqueness config only for this pool:** After Stage 1, gate code must not special-case the string `"extra_emails"`; it walks `CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_list_paths"]`. Lookup remains the object identity source via the config alias.

⚠️ **Decision — no UI / no toast redesign:** Callers already surface `ValueError` → 400; AST-1065 owns display.

---

## Self-Assessment

**Scope:** `Single-Component` — uniqueness config vocabulary tweak + contact uniqueness helpers / initiate coerce in `src/core/candidate.py` only.

**Conf:** `high` — AST-1080 gate and AST-1092 `email_list_paths` already exist; this ticket makes the shared email pool explicit and closes root↔extra as a first-class contract on the save/initiate paths.

**Risk:** `Medium` — wrong pool wiring could miss cross-candidate email leaks or over-collapse within-candidate lists; limited to contact write paths already gated.

---

## Code Rules check (§8)

| Rule | Result |
|------|--------|
| §1.3 DRY | One collect/dedupe path; `email_list_paths` shared by identity with lookup |
| §1.4 no-hardcoded-sets | No inline `"extra_emails"` uniqueness sets in core — config paths only |
| §2.1 config source of truth | Email pool membership + compare mode live in `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` |
| §1.5.1 debug-contract-gated | Existing Style D on enforce when `debug=True`; no new ungated debug |
| §2.4 batch / §2.6 state | N/A |
| §3.3 imports | Core → utils config + existing database; no UI/external |
| data-raises-caller-logs | Core raises toast-ready `ValueError`; UI already surfaces |

No conflicts requiring `conf-!!-NONE`.
