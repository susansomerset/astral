# AST-511 — Middle name on Candidate Profile and Admin (Add Middle name to the candidate profile)

<!-- linear-archive: AST-511 archived 2026-06-03 -->

## Linear archive (AST-511)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-511/middle-name-on-candidate-profile-and-admin-add-middle-name-to-the  
**Status at archive:** Canceled  
**Project:** Astral Candidate  
**Assignee:** Katherine Johnson  
**Priority / estimate:** No priority / —  
**Parent:** AST-509  
**Blocked by / blocks / related:** blocked by AST-510

### Description

## What this implements

Expose middle name on the Candidate Profile contact section and Admin Manage Candidates create/edit flows so candidates and admins can enter, edit, clear, and save middle name through existing profile save paths.

## Acceptance criteria

2. The Candidate Profile contact section shows a middle name field between first and last name (or in an equivalent logical position in that section).
3. Admin Manage Candidates create and edit flows include middle name and persist it on the candidate record.

## Boundaries

* Does not change config DATA_SHAPES, token registry, or artifact display-name composition — sibling **Ada** ticket (**AST-510**).
* Does not add resume parsing for middle name.
* Does not change candidate state machine or nav gating.

## Notes for planning

* Candidate Profile likely picks up `profile.middle` from GET `/api/shapes/candidates` once **AST-510** lands; verify tabbed contact section renders the new field.
* AdminManageCandidates has hardcoded first/last in create and edit modals — wire middle there explicitly.

## Git branch (authoritative)

Per `orientation-astral` **§ Branch law**: parent `ftr/AST-509-add-middle-name-to-the-candidate-profile`, child `sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin`. Created at **dispatch-linear**.

### Comments

#### Katherine Johnson — 2026-05-27T23:52:05.409Z

Plan: [`docs/features/candidate/ast-511-middle-name-on-candidate-profile-and-admin.md`](https://github.com/susansomerset/astral/blob/sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin/docs/features/candidate/ast-511-middle-name-on-candidate-profile-and-admin.md)

**Self-assessment**
- **Scope:** `Single-Component` — Admin Manage Candidates wiring plus component tests; Candidate Profile stays shape-driven (verify only after AST-510).
- **Conf:** `Medium` — Admin changes are fully specified; Profile depends on sibling AST-510 landing `profile.middle` in DATA_SHAPES first (Linear blockedBy).
- **Risk:** `low` — Optional profile string on existing merge save paths; no state machine or artifact changes in this ticket.

Publish SHA on `origin/sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin`: `5b2cdf0e`.

#### Katherine Johnson — 2026-05-27T23:57:09.508Z

`origin/sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin` @ `f190970e` — Stage 3 component tests per plan doc for Betty.

#### Betty White — 2026-05-28T00:04:48.804Z

**Tests Ready** — `origin/sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin` @ `7924be35`

**Prerequisite:** **AST-510** (`origin/sub/AST-509/AST-510-middle-name-profile-data-and-display-name`) must be on your integration tip before Candidate Profile middle field works at runtime; Vitest mocks shapes locally.

**Manifest**

1. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx`
   - **§6c:** routed `CandidateProfile` page (middle save payload) + `AdminManageCandidates` (POST/PUT `profile.middle`, empty middle create).

**`docs/ASTRAL_TEST_BIBLE.md` shasum** on publish ref: `241bc064593d202e97af36b4b866d520722afa55` (§7.13zi — **AST-510** + **AST-511** rows).

If a line fails because the **test** or manifest is wrong: `[qa-handoff]` on this ticket, assign **Betty**, stay **Tests Ready**.

#### Katherine Johnson — 2026-05-28T00:14:07.978Z

[check-linear]

- **§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **already up to date**.
- **§0b / §1 / §2 (session project Astral Candidate):** Full thread on **AST-511** — newest author **Betty** (**Tests Ready** manifest @ `7924be35`). No comment **`@katherine`** me after my posts; nothing expecting a thread fix beyond the standard **`test-astral`** handoff.
- **Status:** **Tests Passed** on ticket; publish ref **`origin/sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin`** — no inbox code/doc action from this pass.
- **Sibling:** **AST-510** backend sub is prerequisite for live Profile middle field (Vitest mocks shapes locally per Betty note).

#### Radia Perlman — 2026-05-28T00:15:14.069Z

**Review** — `origin/dev...origin/sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin`

### What's solid
- **Plan fidelity:** Admin add/edit modals wire `middle` in form state, `openEdit` hydration, and create/update payloads; field order first → middle → last.
- **Candidate Profile:** correctly shape-driven — no `CandidateProfile.tsx` change; test mock adds `profile.middle` to shapes and asserts render + save payload.
- **§3.3 layer compliance:** UI-only diff; no `src/data` / `src/core` imports.
- **§2.1 config boundary:** no `config.py` or token/display changes (**AST-510** scope respected).
- **Tests:** create with middle, edit middle update, empty middle on create.

### fix-now / discuss
None.

### Advisory
- `docs/ASTRAL_TEST_BIBLE.md` on this sub includes §7.13zf–7.13zh entries not on **AST-510**'s sub — bible dedupe at **prep-uat** / parent merge (not engineer fix here).
- Add success toast still `"${first} ${last}"` without middle — pre-existing; out of scope unless Susan wants display polish.
- Doc commit on publish ref: `99a9069b` — cherry-pick onto `dev-kath` if desired.

**→ `resolve-astral`** after **AST-510** resolves (blocker).

---

Implementation was built on publish ref `sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin` but **never landed on `origin/dev`** — parent AST-509 canceled as pipeline proof-of-concept (2026-05-28).
