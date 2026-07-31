# Contact shapes + websites + full-name field contract

**Linear:** [AST-1081](https://linear.app/astralcareermatch/issue/AST-1081/contact-shapes-websites-full-name-field-contract-update-candidate-ui)
**Parent:** [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info)
**Publish ref:** `sub/AST-1065/AST-1081-contact-shapes-websites-full`

Expose the missing Profile contact field contracts (`full`, `contact.websites`, `contact.reason_codes`) in `DATA_SHAPES`, introduce a reusable `string_list` shape field type for multi-entry websites (no existing FormFields type fits a `list[str]`), and tighten the library-derived `full` default so empty/unset values recompute from first+last on save. Does **not** own Candidate Profile page layout/nav (AST-1082), Admin Manage Candidates contact expansion, or AST-1014 library schema changes beyond shape exposure and the empty-`full` save rule.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information (+ reason_codes section if not in Contact fields) with `full`, `contact.websites` (`string_list`), `contact.reason_codes` | utils |
| `src/ui/frontend/src/components/FormFields.tsx` | Add `string_list` to `Field.type`; render multi-entry add/edit/remove list of strings | ui |
| `src/ui/frontend/src/App.css` | Minimal styles for the `string_list` control under FormFields (reuse `dep-*` tokens) | ui |
| `src/core/candidate.py` | Empty/whitespace `full` → `recompute_full_name`; coerce/validate `contact.websites` as `list[str]` on save | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | One-line note: Profile edits `websites` as string list via `string_list` shape type; empty `full` recomputes on save | docs |

**Out of Files Changed (sibling / already shipped):** `CandidateProfile.tsx` load/save wiring and nav cleanup → **AST-1082**. `normalize_contact_urls` / name columns / `contact.*` blob homes → **AST-1014** (already on line). `DATA_SHAPES["candidates"]["edit"]["manage"]` Admin modal fields → leave unchanged (boundary: no Admin contact expand).

## Stage 1: DATA_SHAPES — expose full, websites, reason_codes

**Done when:** `GET /api/shapes/candidates` → `detail.profile` Contact Information includes editable `full`, `contact.websites` with `type: "string_list"`, and `contact.reason_codes`; existing contact keys remain on `contact.*` / name columns (no `profile.*`).

1. In `src/utils/config.py`, locate `DATA_SHAPES["candidates"]["detail"]["profile"]` → the section with `"label": "Contact Information"`.

2. Insert after the `last` field entry (before `contact.contact_email`):
   ```python
   {"key": "full", "label": "Full Name", "type": "text"},
   ```

3. Insert after `contact.linkedin_url` (before `contact.timezone`):
   ```python
   {"key": "contact.websites", "label": "Websites", "type": "string_list"},
   ```

4. Insert after `pronouns` (still inside Contact Information `fields`):
   ```python
   {"key": "contact.reason_codes", "label": "Reason Codes", "type": "textarea"},
   ```
   Keep the existing separate sections for Cover Letter Signature, Signature Image, and Title Patterns unchanged — they already bind `contact.*`. Do not add `profile.*` keys.

5. Do **not** change `list.manage` or `edit.manage` shapes (Admin Manage Candidates stays on its current narrow field set).

⚠️ **Decision:** Introduce shape field type `string_list` (not reuse `textarea`). `contact.websites` is a JSON list of URL strings per `CANDIDATE_DATA_MODEL` / `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`; newline-in-textarea would invent a second serialization and fight round-trip with the blob. Parent AST-1065 already flagged this optional new type for Archie approval before reuse — this ticket is the introduction site; reuse elsewhere needs the same approval bar.

⚠️ **Decision:** `reason_codes` stays a single `textarea` string (like `title_patterns`), not `string_list`. No library consumer or model entry defines it as `list[str]`; only `websites` is documented as a list.

## Stage 2: FormFields — `string_list` renderer

**Done when:** A field with `type: "string_list"` renders as an ordered list of text inputs with per-row Remove and an Add control; value round-trips as `string[]` through `onChange`; unknown/non-array current values treat as `[]`.

1. In `src/ui/frontend/src/components/FormFields.tsx`, extend `Field.type`:
   ```ts
   type: "text" | "textarea" | "select" | "toggle" | "string_list"
   ```

2. In `renderInput`, add `case "string_list":` before `default`:
   - Normalize `value` to `string[]`: if `Array.isArray(value)` use `value.map(v => String(v))`, else `[]`.
   - Render a vertical stack: for each index `i`, a row with `<input className="dep-input" type="text" value={items[i]} />` and a button labeled `Remove` that calls `onChange(items.filter((_, j) => j !== i))`.
   - Below the rows, a button labeled `Add website` (generic enough for reuse: label text **`Add`**) that calls `onChange([...items, ""])`.
   - On input change at index `i`, clone the array, set `next[i] = e.target.value`, `onChange(next)`.
   - Do **not** strip empty strings in the renderer (user may clear a row while editing); persistence coercion is core (Stage 3).

3. In `src/ui/frontend/src/App.css`, under the FormFields / DetailsEditPage section (~§10), add minimal rules for `.dep-string-list`, `.dep-string-list-row`, and `.dep-string-list-add` using existing CSS variables (`--border`, `--text-secondary`, etc.). No new design tokens. No card chrome.

4. Do **not** edit `CandidateProfile.tsx` in this ticket — AST-1082 owns Profile load/save of `full` / websites list / nav. Once shapes + FormFields ship, Profile’s existing Contact Information `FormFields` pass will render the new fields as soon as that sibling wires `full` into edit values and ensures `contact.websites` is present on the values object.

## Stage 3: Core save contract — empty `full` + websites list

**Done when:** `save_candidate_data` recomputes `full` whenever the submitted (or resulting) `full` is missing/blank; `contact.websites` on save is always a list of non-empty trimmed strings (or omitted when not in the contact payload); non-list `websites` raises `ValueError`.

1. In `src/core/candidate.py` `save_candidate_data`, after the existing block that recomputes `full` when `first`/`last` are in `col_kwargs` and `full` is absent, add (or fold into one helper) handling for empty override:
   - If `"full" in col_kwargs` and `not str(col_kwargs["full"]).strip()`:
     - Resolve `first` / `last` from `col_kwargs` with fallback to `database.get_candidate(candidate_id)` existing columns (same pattern as the omit-full branch).
     - Set `col_kwargs["full"] = recompute_full_name(str(first), str(last))`.
   - Non-empty stripped `full` remains an explicit override (persist as submitted string after `str(val)` — keep current assignment; optionally `.strip()` the stored override — **do strip** so `"  Ada Lovelace  "` stores `"Ada Lovelace"`).

2. Still in `save_candidate_data`, inside the existing `if isinstance(contact, dict):` block (after or before `normalize_contact_urls(contact)`):
   - If `"websites" in contact`:
     - If `contact["websites"] is None`: set `[]`.
     - Elif `isinstance(..., list)`: set `[str(x).strip() for x in contact["websites"] if str(x).strip()]`.
     - Else: `raise ValueError("contact.websites must be a list of strings")`.
   - Do **not** invent a max length or entry cap.

3. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`:
   - On the `first`/`last`/`full`/`pronouns` bullet, change the `full` sentence to: `` `full` is recomputed from first+last on save when omitted or empty/whitespace; a non-empty value is an explicit override. ``
   - On the `contact.websites` table row description, append: ` (JSON string list; Profile shape type string_list).`

## Self-Assessment

**Scope:** `Single-Component` — config shapes + FormFields field type + one save-path rule in `candidate.py`; no Profile page rewrite, no Admin expand, no library migration.

**Conf:** `high` — patterns already exist (`DATA_SHAPES` contact remap from AST-1014, `recompute_full_name`, FormFields switch); gap is missing keys + list type + empty-full branch.

**Risk:** `Medium` — wrong `full` recompute could overwrite intentional blank intent, but AC requires empty→derived; websites coercion rejects non-lists so bad clients fail closed rather than corrupt the blob.

## Code rules check

| Rule | Status |
|------|--------|
| §1.3 DRY | Single recompute helper reused; websites coercion only in `save_candidate_data` next to URL normalize |
| §2.1 config | Field keys/types only in `DATA_SHAPES` / existing `CANDIDATE_LIBRARY_CONFIG` vocabulary — no new React field list |
| §2.4 batch | N/A — not a batch task |
| §2.6 state machine | Untouched |
| §3.3 imports | FormFields stays UI-only; core still imports config/database only |
| §3.5 naming | `string_list` snake_case type string matches existing shape types (`signature_image`, `textarea`) |
| Boundaries | No `CandidateProfile.tsx`, no nav, no Admin `edit.manage` expansion, no new contact blob keys |

## Review (build)

**Built:** `origin/sub/AST-1065/AST-1081-contact-shapes-websites-full` @ `de354de123ab419a547a97587f7c870b4e14f090`

Stages 1–3: `DATA_SHAPES` Contact Information adds `full`, `contact.websites` (`string_list`), `contact.reason_codes`; FormFields `string_list` Add/Remove (label `Add`); `save_candidate_data` empty-`full` → `recompute_full_name` + websites list coerce. Profile page/nav deferred to AST-1082. Tests deferred to Betty.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1081
**Publish ref:** `996e815a93611f7ca157836f48d7b03605b368e7`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3 match the plan: `DATA_SHAPES` exposes `full` / `contact.websites` (`string_list`) / `contact.reason_codes`; FormFields renders `string_list` with Add/Remove; `save_candidate_data` empty/whitespace `full` → `recompute_full_name`, websites list coerce + `ValueError` on non-list.
- Boundaries held: no `CandidateProfile.tsx`, no Admin `edit.manage` expand, no new routes.
- One `merge-tests(AST-1081)` SHA; engineer `code()` commits stay off the test tree.

### Findings

**discuss:** straggler — `astral.git.engineer-test-tree-ban` excluded at plan time but in-scope on diff (`tests/**`, `docs/test-bible/**` via Betty). Product commits still clean; no engineer test-tree edit. No product action — note for resolve-child.

### Recommended actions

- Implementer: acknowledge straggler discuss; no `fix-now` product changes.
- AST-1082 owns Profile load/save / nav for the new shape fields.
