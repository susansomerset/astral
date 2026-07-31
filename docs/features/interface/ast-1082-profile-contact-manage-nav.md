# Candidate Profile contact manage UI + nav title-patterns cleanup

**Linear:** [AST-1082](https://linear.app/astralcareermatch/issue/AST-1082/candidate-profile-contact-manage-ui-nav-title-patterns-cleanup-update)
**Parent:** [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info)
**Publish ref:** `sub/AST-1065/AST-1082-profile-contact-manage-nav`

Wire Candidate Profile load/save so Contact Information (name columns + `contact.*`, including `full`, websites list, GitHub/LinkedIn, title_patterns, reason_codes, signatures) round-trips against the library homes shipped by AST-1014 / AST-1081 — not legacy `profile.*`. Confirm candidate navigation has no duplicate title-patterns surface (title patterns edit only via Profile Contact). Does **not** own shapes/`string_list` (AST-1081), library migration (AST-1014), preamble UI (AST-1017), or Admin Manage Candidates contact editing.

**Depends on:** AST-1081 (User Testing) — shapes expose `full`, `contact.websites` (`string_list`), `contact.reason_codes`; FormFields renders `string_list`; core empty-`full` + websites coerce + `normalize_contact_urls` already on `origin/ftr/AST-1065-update-candidate-ui-for-contact-info`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Include `full` in edit values; normalize `contact.websites` to `string[]` on load so FormFields/`string_list` and PUT body preserve overrides and list edits | ui |
| `src/utils/config.py` | Update Profile Contact `DATA_SHAPES` labels for GitHub / LinkedIn to username-or-URL copy; confirm Candidate `NAV_CONFIG` has no Title Patterns item (remove only if present) | utils |

**Out of Files Changed (sibling / already shipped):** `FormFields.tsx` `string_list` renderer, `save_candidate_data` empty-`full` / websites coerce / `normalize_contact_urls` → **AST-1081** / **AST-1014**. Admin `edit.manage` → leave unchanged. No new API routes. No `tests/` / bible (Betty).

## Stage 1: Profile load/save — `full` + contact round-trip

**Done when:** Selecting a candidate on Profile shows `full` and all Contact Information / tabbed contact fields from columns + `contact.*`; Save PUT body includes top-level `full` plus `contact` (with `websites` as an array when the user edited the list); after Save toast and reload (or Cancel→re-fetch path via response remap), the same values reappear — including normalized GitHub/LinkedIn URLs and websites entries. No `profile` key is written.

1. In `src/ui/frontend/src/pages/CandidateProfile.tsx`, update `editValuesFromCandidate` so the returned object is:
   ```ts
   {
     first: c.first ?? "",
     last: c.last ?? "",
     full: c.full ?? "",
     pronouns: c.pronouns ?? "",
     contact: (() => {
       const raw = (d.contact as Record<string, unknown>) ?? {}
       const websites = Array.isArray(raw.websites)
         ? raw.websites.map(v => String(v))
         : []
       return { ...raw, websites }
     })(),
     context: (d.context as Record<string, unknown>) ?? {},
     artifacts: (d.artifacts as Record<string, unknown>) ?? {},
   }
   ```
   Keep using this helper for both initial GET map and post-Save response remap (existing `handleSave` / load `useEffect`).

2. Do **not** invent a client-side first+last join for display defaults. Empty/whitespace `full` → library recompute is owned by `save_candidate_data` (AST-1081). Sending `full: ""` on Save (user cleared the field) must remain possible so that path runs; omitting `full` while still sending `first`/`last` would recompute and wipe an intentional override — that is why `full` must always be present on the values object.

3. Do **not** add a hardcoded contact field list in React. Continue rendering `sections[0]` via `FormFields` + `profile-contact-grid` split and `sections.slice(1)` via `TabbedTextArea` (Title Patterns, signatures, bio, etc. already bind `contact.*` / `context.*` from shapes).

4. Do **not** edit `src/ui/api/api_candidate.py` or `src/core/candidate.py` in this ticket unless a literal step fails because the API rejects a key — then stop and comment on the parent with the 🛑 Stage format. Expected path: existing `PUT /api/candidates/<id>/data` → `save_candidate_data(body)` already accepts name columns + `contact`.

5. Manual smoke (builder): with shapes from AST-1081 on the tip —
   - Edit Full Name to a non–first+last string → Save → reopen → same override.
   - Clear Full Name → Save → reopen → derived first+last join.
   - Add/edit/remove Websites rows → Save → reopen → same `contact.websites`.
   - Enter GitHub / LinkedIn as bare username → Save → reopen → full URL with library bases (`https://github.com/…`, `https://www.linkedin.com/in/…`).
   - Edit Title Patterns / Reason Codes / signature text on Profile tabs → Save → reopen → same under `contact.*`.

⚠️ **Decision:** Always include `websites: []` (or the loaded list) on the contact object at load time so `string_list` edits and JSON.stringify always send a list when the user touches the control, and so a missing blob key does not leave `getByPath` undefined in a way that drops later list writes. Core still coerces/strips empties on save.

## Stage 2: Username-or-URL labels + nav title-patterns hygiene

**Done when:** Profile Contact labels for GitHub and LinkedIn state username-or-URL; Candidate sidebar has no Title Patterns nav item / route; title patterns remain editable only under Profile’s Title Patterns tab (`contact.title_patterns`).

1. In `src/utils/config.py` `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information fields, change labels only (keys/types unchanged):
   - `contact.github` label → `"GitHub (username or URL)"`
   - `contact.linkedin_url` label → `"LinkedIn (username or URL)"`
   Do not add FormFields `placeholder` support. Do not change `normalize_contact_urls` or URL bases.

2. Inspect `NAV_CONFIG` Candidate group and `src/ui/frontend/src/routes.tsx`:
   - If any item/path for Title Patterns / `candidate/title_patterns` exists, remove that nav item and matching route (and delete any orphan page component only if it exists solely for that route).
   - If already absent (current tip: Candidate items are Intake, Profile, Strengths, Priorities, Deal Breakers, Backstory, Writing Preferences; routes test already asserts `candidate/title_patterns` is false), make **no** nav/route edit — labels-only change satisfies this stage’s file touch for config; leave routes.tsx alone.

3. Do **not** remove the Profile `DATA_SHAPES` section `"label": "Title Patterns"` / `contact.title_patterns` textarea — that is the single edit surface AC requires.

⚠️ **Decision:** Username-or-URL UX copy lives in shape labels (config source of truth), not React-only helper text — AST-1081 explicitly deferred that copy to this sibling; normalization stays in core.

## Self-Assessment

**Scope:** `Single-Component` — Profile edit-values mapping plus small `DATA_SHAPES` label (and nav only if a duplicate still exists); no core/API rewrite, no Admin expand.

**Conf:** `high` — gap is concrete (`full` missing from `editValuesFromCandidate`); shapes/`string_list`/normalize already on ftr from AST-1081; nav duplicate already gone on tip.

**Risk:** `Medium` — omitting `full` on PUT while sending `first`/`last` would keep wiping overrides; wrong websites normalize could clobber non-list blob data (mitigated by only coercing when not an array → `[]`, matching FormFields).

## Code rules check

| Rule | Status |
|------|--------|
| §1.3 DRY | Single `editValuesFromCandidate` for load + post-save; no parallel field list |
| §2.1 config | Field keys/types stay in `DATA_SHAPES`; only label strings change here |
| §2.4 batch | N/A |
| §2.6 state machine | Untouched |
| §3.3 imports | Profile stays UI-only (`api` + FormFields) |
| §3.5 naming / file placement | Page stays `CandidateProfile.tsx`; no new page file |
| `astral.layers.ui-config-driven-business-logic` | Renders resolved shapes; no invented contact vocabulary |
| Boundaries | No AST-1081 shape/type work, no Admin contact, no preamble, no library migration, no engineer test-tree edits |

## Review (build)

**Built:** `origin/sub/AST-1065/AST-1082-profile-contact-manage-nav` @ `071960d900b69d20c73e278c901d209a9f3eba9d`

Stages 1–2: `editValuesFromCandidate` always includes `full` and normalizes `contact.websites` to `string[]`; `DATA_SHAPES` GitHub/LinkedIn labels say username-or-URL; Candidate `NAV_CONFIG` / routes already omit title-patterns (no nav edit). Tests deferred to Betty.
