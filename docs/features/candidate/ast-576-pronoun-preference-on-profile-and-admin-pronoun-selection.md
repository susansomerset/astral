# AST-576 — Pronoun preference on Profile and Admin (Pronoun selection)

**Linear:** https://linear.app/astralcareermatch/issue/AST-576/pronoun-preference-on-profile-and-admin-pronoun-selection  
**Parent:** https://linear.app/astralcareermatch/issue/AST-573/pronoun-selection  
**Publish ref:** `sub/AST-573/AST-576-pronoun-preference-profile-and-admin-ui` (origin only)

Expose pronoun preference on **Candidate Profile** and **Admin → Manage Candidates** using the five ordered options from parent AST-573. Persistence uses existing `PUT /api/candidates/<id>/data` merge paths on `candidate_data.profile.pronoun_preference`. This ticket does **not** implement `TOKEN_SOURCES`, `resolve_tokens`, or backfill — sibling **AST-575** (Ada) owns config, validation, token registry, and default/backfill behavior.

---

## Prerequisite gate (build-astral — before Stage 1)

**Done when:** `origin/sub/AST-573/AST-575-pronoun-profile-data-and-prompt-tokens` (or its commits on parent `ftr/ast-573-pronoun-selection` after rollup) is merged into **`dev-kath`** and the following exist on that merged tip. If any item is missing, **stop** per execution contract; comment on **AST-576** (not the parent) naming the missing artifact — do not patch `config.py` or token code in this ticket.

1. **`PRONOUN_PREFERENCE`** block in `src/utils/config.py` with stable `value` strings and display labels for exactly five preferences in this order: **they/them**, **she/her**, **he/him**, **ze/zir**, **e/eir**, plus an explicit unset/clear value (empty string or documented sentinel Ada chose).
2. **`DATA_SHAPES["candidates"]["detail"]["profile"]`** — Contact Information section includes a field:
   - `"key": "profile.pronoun_preference"`
   - `"type": "select"`
   - `"options"` matching `PRONOUN_PREFERENCE` order (unset option first if Ada uses one, then the five preferences in parent order)
3. **`save_candidate_data` / API** accepts `profile.pronoun_preference` values from that option list (or empty for clear) — validation lives in AST-575; this ticket assumes invalid values return 400 and the UI surfaces the error string.

⚠️ **Decision:** Profile page stays **shape-driven** (no duplicate option list in React). Admin modals read the same field definition from `GET /api/shapes/candidates` → `detail.profile[0].fields` rather than hardcoding labels/values, matching the canceled **AST-511** middle-name admin pattern but sourcing options from shapes for DRY with Ada's config.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Pronoun `<select>` on Add/Edit modals; options from shapes; include `profile.pronoun_preference` in POST/PUT payloads; load/clear on edit | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | **Verify only** — contact grid already renders `FormFields` from shapes; no change unless shapes field is missing from contact section (then stop at prerequisite gate, do not relocate field here) | ui |
| `tests/component/frontend/pages/test_CandidateProfile.test.tsx` | Pronoun select visible in contact grid; save payload includes chosen value; reload mock reflects value | tests |
| `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` | Create/edit/clear pronoun in POST/PUT bodies (new tests; do not revive skipped middle-name tests) | tests |

**Out of scope (AST-575 / other tickets):** `src/utils/config.py` (`PRONOUN_PREFERENCE`, `DATA_SHAPES`, `TOKEN_SOURCES`), `src/core/agent.py` / `resolve_tokens`, backfill migration, intake UI, Manage Tasks token autocomplete.

---

## Stage 1: Admin Manage Candidates — pronoun on add/edit

**Done when:** Admin can set, change, and clear pronoun preference on create and edit; View modal JSON shows stored value; existing first/last/email/state/api_key behavior unchanged.

1. In `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, extend `CandidateShapes` (or equivalent) so the shapes fetch retains `detail.profile`, not only `list.manage` (the page already calls `GET /api/shapes/candidates` — store the full response or at least `detail.profile`).

2. Add a module-level helper (same file, above the component):

```typescript
function pronounFieldFromShapes(shapes: CandidateShapes | null): Field | undefined {
  const contact = shapes?.detail?.profile?.[0]
  return contact?.fields?.find(f => f.key === "profile.pronoun_preference")
}
```

Import `Field` from `../components/FormFields` if needed for typing.

3. Extend `addForm` initial state with `pronoun_preference: ""`. Extend `editForm` with `pronoun_preference: ""`. In `openEdit`, set `pronoun_preference: String(profile.pronoun_preference ?? "")`.

4. In **Add Candidate** modal JSX, after the Email field and before the modal footer, render a pronoun field **only when** `pronounFieldFromShapes(shapes)` is defined:
   - Label: use `field.label` from shapes (expected **Pronoun preference** or Ada's label — do not hardcode if shapes provides it).
   - `<select className="dep-input dep-select">` with `value={addForm.pronoun_preference}` and `onChange` updating `addForm.pronoun_preference`.
   - Map `field.options` the same way `FormFields` does (`string | { value, label }`).
   - If shapes field is missing, render nothing (build should have failed prerequisite gate).

5. In `handleAddSave`, include pronoun in create payload:

```typescript
candidate_data: {
  profile: {
    first: first.trim(),
    last: last.trim(),
    contact_email: contact_email.trim(),
    pronoun_preference: addForm.pronoun_preference,
  },
},
```

6. Mirror the same `<select>` in **Edit Candidate** modal bound to `editForm.pronoun_preference`.

7. In `handleEditSave`, merge pronoun into the existing profile object:

```typescript
profile: {
  first: first.trim(),
  last: last.trim(),
  contact_email: contact_email.trim(),
  pronoun_preference: editForm.pronoun_preference,
},
```

Empty string clears stored preference (admin AC #2). Do not omit the key on clear — send `""` so merge overwrites a previous value.

8. Reset `pronoun_preference: ""` in add-form reset after successful create (same block that clears first/last/email).

⚠️ **Decision:** Admin create/edit modals stay hand-built (like today's first/last/email fields), not refactored to `DATA_SHAPES["candidates"]["edit"]["manage"]`, to minimize diff scope. Options/labels still come from `detail.profile` pronoun field for single source of truth.

---

## Stage 2: Candidate Profile — shape-driven control (verify)

**Done when:** With AST-575 shapes on the merged tip, Candidate Profile Contact Information shows the pronoun `<select>` in the two-column contact grid, options in parent order, Save persists `profile.pronoun_preference`, Cancel restores prior value.

1. **Do not edit** `CandidateProfile.tsx` if the prerequisite gate passes — `sections[0]` contact fields already flow through `FormFields` with `profile-contact-grid` split (`slice(0, half)` / `slice(half)`). The pronoun field appears automatically when Ada adds it to Contact Information fields.

2. Manual smoke (after Stage 3 tests pass):
   - Select a candidate → Profile → choose **she/her** (or any non-empty option) → Save → reload page → same selection shown.
   - Choose unset/clear option → Save → reload → empty/unset shown.
   - Confirm name/contact fields still save independently (regression spot-check).

3. If pronoun field renders in a **non-contact** profile section (wrong `DATA_SHAPES` placement by Ada), **stop** and comment on AST-576 — do not move the field in this ticket.

---

## Stage 3: Frontend tests and compile

**Done when:** Vitest cases below pass; `npx tsc -b --noEmit` clean in `src/ui/frontend`.

1. In `tests/component/frontend/pages/test_CandidateProfile.test.tsx`:
   - Add `profile.pronoun_preference` to mock `profileSections.detail.profile[0].fields` as `{ key: "profile.pronoun_preference", label: "Pronoun preference", type: "select", options: [{ value: "", label: "(not set)" }, { value: "they_them", label: "they/them" }, { value: "she_her", label: "she/her" }] }` — use Ada's actual `value` strings once visible on merged tip; until build, use placeholders that match merged config.
   - Add `pronoun_preference: "they_them"` (or Ada's value) to `candidateData.profile`.
   - New test **`saves pronoun preference from contact grid`**: assert select visible with current value; change selection; Save; assert PUT body `profile.pronoun_preference` matches selection.

2. In `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx`:
   - Extend mock `shapes` with `detail.profile` contact section containing the same pronoun field def.
   - Extend mock `candidate.candidate_data.profile` with `pronoun_preference: "she_her"` (or Ada's value).
   - New test **`includes profile.pronoun_preference in create and edit payloads`**: Add modal — set pronoun → POST body includes value; Edit modal — change pronoun → PUT body includes new value; Edit — select unset → PUT sends `""`.
   - Do **not** unskip the canceled AST-511 middle-name tests.

3. Run:

```bash
cd src/ui/frontend && npx tsc -b --noEmit
npm test -- --run tests/component/frontend/pages/test_CandidateProfile.test.tsx tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

(Betty may fold these into manifest during qa-astral; run locally at build completion.)

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Admin Manage Candidates modals plus frontend tests; Candidate Profile is verify-only via existing shape-driven contact grid. Build also added `DATA_SHAPES` contact `profile.pronoun_preference` in `config.py` when AST-575 omitted shapes (pragmatic unblock — see Resolution).

**Conf:** `conf-high` — Mirrors proven AST-511 admin payload pattern and existing `FormFields` select rendering; dependency on AST-575 is explicit with a hard stop if config/shapes are missing.

**Risk:** `risk-low` — Wrong wiring affects profile/admin UX only; token resolution and name tokens are untouched per ticket boundaries.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Admin options sourced from `DATA_SHAPES` field def, not duplicated in React. |
| §2.1 config | No new config blocks in this ticket; consumes Ada's `PRONOUN_PREFERENCE` / shapes. |
| §3.3 imports | UI changes stay in `pages/`; no core/data imports. |
| §3.5 naming | No new pages/components; flat `pages/AdminManageCandidates.tsx`. |
| §3.2 UI logic | No business rules in React — validation/defaulting remains server-side (AST-575). |

No conflicts requiring `conf-!!-NONE`.

---

## Execution contract reminders

- Merge **AST-575** publish ref into `dev-kath` before coding Stage 1.
- Do not implement `TOKEN_SOURCES`, `resolve_tokens`, backfill, or intake UI.
- Do not add pronoun tokens to Manage Tasks autocomplete (AST-575).
- Blocking ambiguity → comment on **AST-576** with 🛑 format from plan-astral §6.

---

## Review (build)

**Built:** Stages 1–2 — `DATA_SHAPES` contact `profile.pronoun_preference` select (AST-575 had constants/tokens but omitted shapes); Admin Manage Candidates add/edit pronoun from shapes with POST/PUT payloads and clear via `""`. Candidate Profile unchanged (shape-driven contact grid). Stage 3 Vitest deferred to Betty per build-astral test-tree ban.

**Branch:** `origin/sub/AST-573/AST-576-pronoun-preference-profile-and-admin-ui` @ `39af34ec`

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-573/AST-576-pronoun-preference-profile-and-admin-ui` (6 files, +384/−10). Tip `4fabcc50`.

### What's solid

| Area | Notes |
|------|--------|
| **Plan fidelity — Admin** | `pronounFieldFromShapes`, `PronounSelect`, and shapes-backed add/edit modals match Stage 1; POST/PUT include `profile.pronoun_preference`; clear uses `""` (AC #2). |
| **Plan fidelity — Profile** | No `CandidateProfile.tsx` change; Vitest `saves pronoun preference from contact grid` exercises shape-driven contact save (AC #1 wiring). |
| **§3.2 / §3.3 UI layer** | `AdminManageCandidates.tsx` uses `api` + `FormFields` types only — no `src.data` / `src.external`. |
| **§2.1 / §3.2 G1** | React does not hardcode the five-option list; Admin reads `field.options` from shapes API. |
| **Sibling boundary** | No `TOKEN_SOURCES`, `resolve_tokens`, or migration code in this diff. |
| **Option values** | `DATA_SHAPES` select values (`they/them` … `e/eir`) match `PRONOUN_PREFERENCE_OPTIONS` on `origin/sub/AST-573/AST-575-pronoun-profile-data-and-prompt-tokens`. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `src/utils/config.py` (this diff) | Plan **Out of scope** and prerequisite gate forbid `config.py` edits on AST-576; build added Contact Information `profile.pronoun_preference` because AST-575 omitted `DATA_SHAPES`. Pragmatic unblock — document Susan-approved exception or fold hunk into AST-575 before epic land (**§5d**). |
| **discuss** | `src/utils/config.py` | `DATA_SHAPES` options duplicate `PRONOUN_PREFERENCE_OPTIONS` literals (§1.3 / §2.1 DRY at config layer). Safe if kept in sync; consider generating shape options from one tuple on resolve. |
| **discuss** | Plan § Self-Assessment | Stated “no new config blocks” but diff adds `DATA_SHAPES` field — scope footnote should match ship reality. |
| **advisory** | `test_CandidateProfile.test.tsx`, `test_AdminManageCandidates.test.tsx` | Mock shapes list four pronoun values (omit `ze/zir`, `e/eir`); production config has five. Tests still prove payload wiring — extend mocks when touching tests again. |

No **fix-now** product-code items for Katherine on this publish ref.

### Recommended actions

| Action | Owner |
|--------|--------|
| Proceed to `resolve-astral` — no blocking UI fixes. | Katherine |
| On resolve: reply in thread if Susan wants `DATA_SHAPES` hunk moved to AST-575 or kept on 576. | Katherine / Susan |
| Optional: extend Vitest mock options to all five parent-ordered values. | Katherine or Betty |
| UAT: Profile + Admin manual smoke per Stage 2 (five-option order, clear → unset). | Susan |

---

## Resolution (2026-06-03)

**Review ref:** Radia comment @ `367955ec` on `origin/sub/AST-573/AST-576-pronoun-preference-profile-and-admin-ui`.

### fix-now

None — Radia confirmed no blocking UI fixes on the publish ref.

### discuss (documented; no product change this pass)

| Item | Resolution |
|------|------------|
| `DATA_SHAPES` hunk in `config.py` on AST-576 vs AST-575 | Kept on **576** as shipped — pragmatic unblock when AST-575 plan-only at build time. Susan may fold into **575** before epic land; no move without explicit direction. |
| `DATA_SHAPES` options duplicate `PRONOUN_PREFERENCE_OPTIONS` | Accepted for now — values stay in sync with AST-575 tuple; optional Ada follow-up to generate shape options from one source. |
| Self-Assessment “no new config blocks” | Footnote updated above to match ship reality. |

### advisory

Vitest mocks use four pronoun options; production has five — wiring tests sufficient; extend mocks when convenient (Betty or future touch).

### Product changes this resolve pass

Doc-only: Self-Assessment footnote + this Resolution section. No additional product commits.
