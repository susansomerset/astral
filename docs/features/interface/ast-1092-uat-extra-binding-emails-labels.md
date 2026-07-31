# UAT: Profile extra binding emails + resume/messages email labels

**Linear:** [AST-1092](https://linear.app/astralcareermatch/issue/AST-1092/uat-profile-extra-binding-emails-resumemessages-email-labels)
**Parent:** [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info)
**Publish ref:** `sub/AST-1065/AST-1092-uat-extra-binding-emails-labels`

UAT fix: rename Profile Contact email field labels to purpose names, and let a candidate manage a multi-entry list of **extra** emails that persist under the contact library and participate in platform email **binding / lookup** (same vocabulary family as `CANDIDATE_LOOKUP_CONFIG`). Reuse existing `string_list` FormFields type (AST-1081). Does **not** stuff emails into `contact.websites`, expand Admin Manage Candidates contact editing, or touch preamble/intake.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): “On Candidate Profile, Contact Information … read and save against name columns + `contact.*` — not `profile.*`.” / “A candidate can add, edit, and remove websites entries on Profile; after save and reload, those entries persist under `contact.websites`.” / “Save then reopen Profile shows the same contact values from the library homes.” Archie UAT scope clarification on this parent: extra binding emails + Resume/Messages labels.
- **Correct outcome:** Labels read **Email for Resume** / **Email for Messages (if different)**; candidate can add/edit/remove an extra-emails list on Profile; those values persist under `contact.extra_emails` and bind via `get_candidate_id_for_query` the same way scalar contact/reply emails do; save then reopen shows the same list and labels.
- **Sibling check:** AST-1081 `string_list` + websites coerce remain; AST-1082 Profile `editValuesFromCandidate` pattern extended (not replaced); AST-1014 contact blob + AST-1045/1079/1080 uniqueness — extras register on lookup + uniqueness list vocabulary so bind and save-gate stay aligned.
- **Not sufficient:** Renaming labels alone, or a Profile-only list that never hits lookup/bind paths.
- **Wrong fix rejected:** Stuffing extras into `contact.websites`; Profile-only list omitted from `CANDIDATE_LOOKUP_CONFIG` / uniqueness; Admin Manage Candidates contact expand; inventing parallel React field list outside `DATA_SHAPES`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename Profile Contact email labels; add `extra_emails` to `contact_keys`; add `email_list_paths` on `CANDIDATE_LOOKUP_CONFIG`; add `contact.extra_emails` to uniqueness `list_paths`; expose `contact.extra_emails` `string_list` in `DATA_SHAPES` Contact Information; asserts | utils |
| `src/core/candidate.py` | Coerce `contact.extra_emails` like websites on save; expand `email_list_paths` in `get_candidate_id_for_query` | core |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Normalize `contact.extra_emails` to `string[]` on load/post-save remap (same as websites) | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `contact.extra_emails` + updated email label meanings | docs |

**Out of Files Changed:** Admin `edit.manage` / `list.manage` email labels (boundary: Profile owns this UAT surface). FormFields `string_list` renderer (already shipped). Preamble / intake / Topic Menu.

## Stage 1: Config — labels, library key, lookup + uniqueness vocabulary

**Done when:** Profile shapes show the new labels and a `string_list` for `contact.extra_emails`; `extra_emails` is in `contact_keys`; lookup exposes `email_list_paths`; uniqueness `list_paths` includes `contact.extra_emails`; import-time asserts pass.

1. In `src/utils/config.py` `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`, insert `"extra_emails"` after `"websites"` (keep tuple order otherwise unchanged).

2. In `CANDIDATE_LOOKUP_CONFIG`, after `email_paths`, add:
   ```python
   "email_list_paths": (
       "contact.extra_emails",
   ),
   ```
   Do **not** put `contact.extra_emails` into scalar `email_paths` — `_lookup_path_value` returns `""` for non-strings today.

3. In `CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"]`, add `"contact.extra_emails"` after `"contact.websites"` so each non-empty entry is a uniqueness token (existing list compare / AST-1080 enforcement).

4. After existing lookup/uniqueness asserts, add:
   - `assert isinstance(CANDIDATE_LOOKUP_CONFIG["email_list_paths"], tuple)`
   - For each path in `email_list_paths`: starts with `"contact."` and key is in `contact_keys`
   - Optionally assert `email_list_paths` entries also appear in uniqueness `list_paths` (same object membership or membership check) so bind and uniqueness cannot drift.

5. In `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information fields:
   - Change `contact.contact_email` label → `"Email for Resume"`
   - Change `contact.reply_email` label → `"Email for Messages (if different)"`
   - Immediately after `contact.reply_email`, insert:
     ```python
     {"key": "contact.extra_emails", "label": "Extra emails (binding)", "type": "string_list"},
     ```
   Do **not** change Admin `edit.manage` / `list.manage` labels in this ticket.

6. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`:
   - Update `contact.contact_email` / `contact.reply_email` row descriptions to Resume / Messages purpose wording.
   - Add table row for `contact.extra_emails`: JSON string list of additional binding emails; Profile shape type `string_list`; included in lookup `email_list_paths` + uniqueness `list_paths`.

⚠️ **Decision:** New library key `extra_emails` (not reuse `websites`). Archie UAT requires bindable extras; parent’s “no new keys” boundary yields to the in-scope UAT clarification on the bug. Key must be registered in library + lookup list paths + uniqueness list paths — never Profile-only.

⚠️ **Decision:** `email_list_paths` on `CANDIDATE_LOOKUP_CONFIG` (sibling to scalar `email_paths`) instead of overloading `email_paths` with list-valued entries. Keeps scalar path readers honest; bind expands lists explicitly.

## Stage 2: Core — save coerce + bind lookup expansion

**Done when:** Saving `contact.extra_emails` yields a list of non-empty trimmed strings (or `[]`); non-list raises `ValueError`; `get_candidate_id_for_query` matches needles present only in `extra_emails` when unique.

1. In `src/core/candidate.py` `save_candidate_data`, inside the `if isinstance(contact, dict):` block next to websites coerce, add the same pattern for `"extra_emails"`:
   - `None` → `[]`
   - `list` → `[str(x).strip() for x in … if str(x).strip()]`
   - else → `raise ValueError("contact.extra_emails must be a list of strings")`
   Do not invent a max length or entry cap.

2. In `get_candidate_id_for_query`, after collecting scalar values from `email_paths` / `name_paths` / `slack_user_id_paths`, also expand each path in `CANDIDATE_LOOKUP_CONFIG["email_list_paths"]`:
   - Prefer reusing `_iter_uniqueness_path_values(candidate, path)` (already understands uniqueness `list_paths`) **or** inline the same list-walk if that helper requires the path to be in uniqueness `list_paths` (it does — Stage 1 already added the path there).
   - Append each non-empty stripped entry to `values` with the same casefold rule as scalar emails.
   - Do **not** walk uniqueness `list_paths` wholesale (that would treat `contact.websites` as bind emails).

3. Do **not** change uniqueness enforcement algorithms beyond the config path addition (AST-1080 already iterates `list_paths`).

## Stage 3: Profile load/save round-trip for `extra_emails`

**Done when:** Profile Contact Information shows the new labels and Extra emails `string_list`; Add/Remove/edit round-trips under `contact.extra_emails` with no `profile` key; empty missing blob key loads as `[]`.

1. In `src/ui/frontend/src/pages/CandidateProfile.tsx` `editValuesFromCandidate`, normalize `extra_emails` beside websites:
   ```ts
   const extra_emails = Array.isArray(raw.extra_emails)
     ? raw.extra_emails.map(v => String(v))
     : []
   return {
     // …existing first/last/full/pronouns…
     contact: { ...raw, websites, extra_emails },
     // …
   }
   ```
   Keep using this helper for GET load and post-Save remap. Do **not** hardcode a contact field list in React — shapes continue to drive which fields render.

2. Manual smoke: rename visible; add two extra emails → Save → reopen → same list; send/bind path that uses `get_candidate_id_for_query` with an extra-only address returns that candidate when unique (or unit-level via existing lookup tests once Betty covers — engineer does not edit tests).

## Self-Assessment

**Scope:** `Single-Component` — config vocabulary + Profile list normalize + small lookup/save coerce; no Admin/preamble rewrite.

**Conf:** `high` — reuses `string_list`, websites coerce, uniqueness `list_paths`, and lookup casefold; gap is the missing key + list expansion in bind.

**Risk:** `Medium` — wrong lookup expansion could bind on websites or miss extras; uniqueness list registration prevents silent cross-candidate collisions on extras when AST-1080 runs.

## Code rules check

| Rule | Status |
|------|--------|
| §1.3 DRY | Coerce pattern mirrors websites; list walk reuses `_iter_uniqueness_path_values` |
| §2.1 config | Key, labels, lookup/uniqueness paths live in `config.py` |
| §2.4 / §2.6 | N/A / untouched |
| §3.3 imports | UI→api only; core reads config |
| Boundaries | No Admin contact expand, no websites-as-email, no preamble |
