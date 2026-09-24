<!-- linear-archive: AST-1669 archived 2026-09-24 -->

## Linear archive (AST-1669)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1669/manage-candidates-slack-bind-dropdown-bind-new-slack-contacts-to  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1636 — Bind new Slack contacts to existing candidates by metadata before creating a prospect  
**Blocked by / blocks / related:** parent: AST-1636

### Description

## What this implements

Owns the Manage Candidates add/edit Slack username dropdown and persisting selected Slack id + username via the existing candidate write path. Consumes sibling #2's GET. Does not own resolve recognition or the poster helper.

## Citations

`stat.logging.info.api`, `stat.logging.error`.

## Scope

`src/ui/frontend/src/pages/AdminManageCandidates.tsx` — dropdown on add/edit; `src/ui/api/api_candidate.py` / existing candidate create+data PUT — only if bind payload must be accepted there. Candidate Profile Slack text fields unchanged.

## Acceptance criteria

- [X] 5\. Manage Candidates add/edit: unbound usernames in a dropdown; save with a selection persists `contact.slack_user_id` and `contact.slack_username`. Fail if already-bound usernames appear or selection does not stamp both fields.
- [X] 6\. After bind, unbound list omits that Slack user. Fail if they remain selectable for another candidate.
- [X] 7\. External poster pool lives in `src/external/slack.py`, invoked from core/API — not from React. Fail if `AdminManageCandidates.tsx` hardcodes Slack Web API URLs/tokens.

## Boundaries

- [X] Does not own poster helper (#1) or Contact resolve/unbound API (#2).

## Notes for planning

Consumes sibling #2's GET. Build used existing create/PUT only — no `api_candidate.py` change.

## Git branch (authoritative)

Parent `ftr/AST-1636-bind-slack-contacts`; child `sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown`. Created at dispatch-parent.

## QA test manifest

1. Routed Manage Candidates Slack bind (§6c): `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` — pattern `AST-1669`

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx \
  --testNamePattern='AST-1669'
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**

* `docs/test-bible/frontend/pages.md` — `d05e1b8a183582e509e13f39f2213bdbcab58660`

### Comments

#### radia — 2026-09-16T02:39:28.472Z
[code-rubric] PROCEED (Commit: d51bda97) Slack bind dropdown clean

#### betty — 2026-09-16T02:37:14.670Z
`origin/sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown` @ `d51bda97` · Slack bind dropdown tests ready

#### joan — 2026-09-16T02:29:27.048Z
[plan-rubric] PROCEED (Commit: 82fb3b202528a53fea3faf519054d65cde1f34d0) Slack bind dropdown plan sound

#### joan — 2026-09-16T02:29:21.108Z
[plan-rubric] PROCEED (Commit: 82fb3b202528a53fea3faf519054d65cde1f34d0) Slack bind UI plan sound

#### katherine — 2026-09-16T02:27:32.062Z
`origin/sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown` @ `82fb3b20` · plan ready

---

# AST-1669 — Manage Candidates Slack bind dropdown

**Linear:** [AST-1669](https://linear.app/astralcareermatch/issue/AST-1669/manage-candidates-slack-bind-dropdown-bind-new-slack-contacts-to)  
**Parent:** [AST-1636](https://linear.app/astralcareermatch/issue/AST-1636/bind-new-slack-contacts-to-existing-candidates-by-metadata-before) — Bind new Slack contacts to existing candidates by metadata before creating a prospect  
**Publish ref:** `sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown`

Child #3 of AST-1636: on Manage Candidates add/edit, offer unbound Slack usernames in a dropdown and persist the selected `contact.slack_user_id` + `contact.slack_username` through the existing candidate create / data PUT path. Consumes sibling AST-1668's admin GET. Does **not** own poster fetch, unbound filtering, resolve recognition, or Candidate Profile Slack text fields.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — dropdown on add/edit
- `src/ui/api/api_candidate.py` / existing candidate create+data PUT — **only if** bind payload must be accepted there
- Candidate Profile Slack text fields unchanged

**Out of scope (siblings):** `src/external/slack.py` poster helper; `src/core/contact.py` unbound/resolve/recognition; `src/ui/api/api_contact.py` unbound GET body.

**Depends on:** AST-1668 `GET /api/admin/contact/unbound_slack_users` → `{"users":[{"slack_user_id": str, "username": str}, …]}` (already on `origin/ftr/AST-1636-bind-slack-contacts` / this worktree).

**Canon Scope (read in full for plan):** `stat.logging.info.api`, `stat.logging.error`. Patterns: none (`no established pattern applies` on parent). React does not write `app_log` (`stat.logging.info.api` Notes). This ticket does **not** add or change API handlers — no new route progress info and no new handler `logger.exception` lines. Existing create/PUT error JSON (including contact-uniqueness `ValueError`) continues to surface via toast.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Load unbound Slack users; Slack username dropdown on add + edit; stamp both contact Slack fields on save; refresh unbound after bind | ui |

⚠️ **Decision — no `api_candidate.py`:** `POST /api/candidates` already stores `candidate_data.contact` via `initiate_candidate` (uniqueness enforced). `PUT /api/candidates/<id>/data` deep-merges `contact` leaves via `save_candidate_data(replace=False)`. Both already accept `slack_user_id` / `slack_username` under `contact`. Cross-candidate Slack-id collisions already hard-fail uniqueness. Do **not** edit `api_candidate.py`, core, or Candidate Profile.

No other files. Do **not** call Slack Web API URLs/tokens from React (parent AC 7).

## Stage 1: Manage Candidates Slack bind dropdown

**Done when:** Add and Edit modals show a Slack username `<select>` populated from `GET /api/admin/contact/unbound_slack_users` (plus the edit target's own current bind when present); saving with a selection persists both `contact.slack_user_id` and `contact.slack_username` through the existing create/PUT paths; after a successful bind, reloading the unbound list omits that user; no Slack Web API hardcoded in this file.

1. In `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, add types/state:
   - `type UnboundSlackUser = { slack_user_id: string; username: string }`
   - `unboundSlackUsers: UnboundSlackUser[]` (default `[]`)
   - Extend `addForm` and `editForm` with `slack_user_id: string` (selected option value; `""` = no selection). Do **not** store a free-text username field the admin can type.

2. Add `loadUnboundSlackUsers` (useCallback):
   - `api("/api/admin/contact/unbound_slack_users")` → parse JSON → take `users` array.
   - Keep only rows where `slack_user_id` and `username` are non-empty strings (trim). Map to `{ slack_user_id, username }`.
   - On network/non-OK: `setUnboundSlackUsers([])` and toast error (e.g. "Failed to load unbound Slack users") — do **not** block First/Last/Email/pronouns fields or close the modal.
   - Call when opening Add (`setAddOpen(true)` path / Add button) and when `openEdit` runs; also call after a successful add/edit save that stamped a Slack bind (so AC 6 is visible without a full page remount). Optional: also call once in the existing mount `useEffect` — fine either way as long as open-modal refresh happens.

3. Dropdown options for a modal:
   - Always include a blank option labeled `— none —` with `value=""`.
   - Then unbound rows: `value={slack_user_id}`, visible label = `username` (ticket: "dropdown labeled by Slack username").
   - ⚠️ **Decision — edit already bound:** When `openEdit` finds non-empty `contact.slack_user_id` on the target, set `editForm.slack_user_id` to that id. If that id is **not** in the unbound list (expected after bind), prepend **one** synthetic option `{ slack_user_id, username: contact.slack_username || slack_user_id }` so the current bind stays selectable/visible. Do **not** prepend other candidates' binds. AC 5 "already-bound usernames appear" means other candidates' binds must not appear as unbound choices.

4. UI — Add modal (`title="Add Candidate"`) and Edit modal: after Email (before pronouns), add:
   ```tsx
   <div className="dep-field">
     <label className="dep-field-label">Slack username</label>
     <select
       className="dep-input dep-select"
       value={…Form.slack_user_id}
       onChange={e => set…Form(p => ({ ...p, slack_user_id: e.target.value }))}
     >
       <option value="">— none —</option>
       {/* unbound (+ edit current-bind prepend from step 3) */}
     </select>
   </div>
   ```
   Reuse existing `dep-field` / `dep-input` / `dep-select` classes (same as PronounSelect / state select). No new CSS file.

5. Persist on save — stamp **both** fields from the selected unbound (or prepended) row; never username alone:
   - Helper (inline or local function): given `slack_user_id` selection and the option list used for that modal, if selection is non-empty find the matching row and return `{ slack_user_id, slack_username: username }`; if empty, return `null`.
   - **Add (`handleAddSave`):** keep existing required first/last checks. Build `contact` as today with `contact_email`. If helper returns a bind object, set `contact.slack_user_id` and `contact.slack_username` on that same `contact` object inside `candidate_data`. Reset `slack_user_id: ""` when clearing `addForm` after success.
   - **Edit (`handleEditSave`):** keep existing payload shape (`contact: { contact_email }`). If helper returns a bind object, add both Slack keys onto that `contact` object. ⚠️ **Decision — empty selection does not clear:** If selection is `""`, omit `slack_user_id` / `slack_username` from the PUT body so deep-merge leaves any existing bind intact. This ticket does not add an unbind/clear control.
   - Illegal-state confirm retry path must reuse the **same** payload (including Slack bind keys) — do not drop them on the confirm PUT.
   - Uniqueness collision (already-bound Slack id on another candidate) returns 400 from existing API — toast the error string; do not invent a second client-side uniqueness check.

6. Reset hygiene: when closing Add without save, or after successful add, reset `slack_user_id` with the rest of `addForm`. `openEdit` sets `slack_user_id` from contact (step 3). Do **not** change Candidate Profile (`CandidateProfile.tsx`) or shapes config Slack text fields.

7. Compile/lint before stage commit: from `src/ui/frontend`, run `npm run build` and `npm run lint` (or the repo's equivalent already used on this epic). Fix only issues introduced in this file.

## Execution contract

- Stages in order; steps in order; no extra files.
- Ambiguity / drift → comment on **parent** AST-1636 with the Stage blocked template; wait.
- Sibling contract: consume `GET /api/admin/contact/unbound_slack_users` only — no React Slack Web API.
- Acceptance mapped (parent AC owned by this child):
  - 5 → Stage 1 steps 3–5 (dropdown + both fields stamped; other-bound usernames not in unbound options).
  - 6 → Stage 1 step 2 refresh after bind + sibling unbound filter (GET omits newly bound id).
  - 7 → Stage 1 Files Changed + step 2 (admin GET only; no Slack URLs/tokens in TSX).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1669
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown` @ `82fb3b202528a53fea3faf519054d65cde1f34d0`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | X | | Plan touches no `src/ui/api/**` files; explicitly defers to existing create/PUT routes and forbids new progress info |
| stat.logging.error | X | | No handler-layer exception logging in footprint; API errors continue via existing JSON + toast |

## Traceability

5 → Stage 1 steps 3–5 (unbound `<select>`; both `contact.slack_user_id` + `contact.slack_username` stamped on add/edit save; synthetic edit-only option for current bind) · 6 → Stage 1 step 2 (reload unbound after successful bind + sibling GET filter omits bound ids) · 7 → Stage 1 Files Changed + step 2 (`GET /api/admin/contact/unbound_slack_users` only; no Slack Web API URLs/tokens in TSX)

## Findings

### discuss — Canon Scope all-X (scope observation, not blocking)
**Location:** Plan `## Scope gate` Canon Scope; `## Files Changed`
**Finding:** Parent locked `stat.logging.info.api` and `stat.logging.error` anticipating optional `api_candidate.py` work. Plan’s no-`api_candidate.py` decision is justified (`POST /api/candidates` + `PUT …/data` already deep-merge `contact`; Slack-id uniqueness already enforced server-side). Neither statute applies to the sole planned file (`AdminManageCandidates.tsx`).
**Recommendation:** No plan rewrite required. Radia’s column will also be all-X unless the diff accidentally touches API handlers.

### acceptable — Scope & no-api decision
**Location:** `## Scope gate`, Stage 1 ⚠️ Decision — no `api_candidate.py`
**Finding:** Single-file footprint matches ticket partition. Existing `handleAddSave` / `handleEditSave` contact payloads can accept Slack keys without backend edits.
**Recommendation:** None.

### acceptable — Edit edge cases
**Location:** Stage 1 steps 3 + 5
**Finding:** Synthetic prepend for edit target’s current bind; empty selection omits Slack keys (no accidental unbind); illegal-state confirm retry must preserve Slack bind keys — aligns with existing AST-1287 confirm path in `handleEditSave`.
**Recommendation:** None.

### acceptable — Sibling dependency
**Location:** Depends on AST-1668; Stage 1 step 2
**Finding:** `GET /api/admin/contact/unbound_slack_users` is present on the epic worktree (`api_contact.py` + `list_unbound_slack_users` in core). Plan contract matches sibling return shape.
**Recommendation:** None.

## R6 checklist (summary)

- Definition fidelity: pass — Manage Candidates dropdown + persist only; no resolve/poster/unbound-filter ownership creep.
- AC coverage: pass — child AC 5–7 mapped in Execution contract.
- DRY / scope creep: pass — reuses existing create/PUT, `dep-field`/`dep-select`, toast/error patterns.
- Self-assessment: pass — estimate 2 for one focused stage is honest.

context_tokens≈54000

---

[plan-rubric] PROCEED (Commit: 82fb3b202528a53fea3faf519054d65cde1f34d0) Manage Candidates Slack bind dropdown plan sound

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown` |
| Tip | `d240d8ae` |
| Branch | `sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown` |

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `d240d8ae` | Manage Candidates Slack bind dropdown on add/edit |

## Radia review

[code-rubric]
**Ticket:** AST-1669
**Publish ref:** `d51bda97f31e4bd56e777296069b76ebc306af9d` (`origin/sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown`)
**Corpus:** `fc0c368e5927a57f1561c057ce9a0ff4abe1fb13`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | X | | |
| stat.logging.error | X | | |

## Column diff vs plan stage

(aligned) — Joan and Radia both **X** on both directives; product commit touches only `AdminManageCandidates.tsx` (no `src/ui/api/**` handler changes).

## Frame diff

(none)

## Findings

### advisory — Three-dot diff vs `origin/dev` is epic-polluted
**Location:** `git diff origin/dev...origin/sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown`
**Finding:** Three-dot diff includes sibling epic files (`contact.py`, `slack.py`, `api_contact.py`, `config.py`) from stacked AST-1636 children. **AST-1669 product commit `d240d8ae` is single-file:** `AdminManageCandidates.tsx` (+132/−15).
**Recommendation:** Score footprint from ticket commits, not raw three-dot stat.

### advisory — Illegal-state confirm + bind keys untested
**Location:** `handleEditSave` confirm retry (`{ ...payload, confirm_state_override: true }`)
**Finding:** Code preserves Slack bind keys in the confirm PUT via `payload` spread (plan step 5). No Vitest exercises that branch with a bind selection.
**Recommendation:** Optional follow-up test — not blocking; primary bind paths are covered.

## What's solid

- **AC 5:** Add/edit modals show Slack username `<select>` from `GET /api/admin/contact/unbound_slack_users`; save stamps both `contact.slack_user_id` and `contact.slack_username` via existing POST/PUT paths.
- **AC 6:** `loadUnboundSlackUsers()` runs on modal open and after successful bind; tests assert second GET and pool shrink.
- **AC 7:** No `slack.com` / Slack Web API hosts in TSX; only admin GET consumed.
- **Edit edge cases:** Synthetic prepend for current bind when absent from unbound pool; empty selection omits Slack keys (no accidental unbind).
- **Scope:** No `api_candidate.py`, `contact.py`, or `CandidateProfile` changes — matches no-api plan decision.
- **Tests:** Four `AST-1669` Vitest cases cover add bind, edit prepend/empty-omit, AC6 refresh, and admin-GET-only pool source.
- **Estimate 2** fits one focused UI stage.

## Notes — Canon Scope (Joan observation confirmed)

Parent locked `stat.logging.info.api` / `stat.logging.error` anticipating optional API work. Plan’s no-`api_candidate.py` decision is correct (existing create/PUT already accept `contact` Slack keys; uniqueness server-side). Both directives are **X** for this diff — not mis-selected, not a scope gap requiring ESCALATE.

## Recommended actions (Chuckles downstream — not Radia lane)

- Append artifact to `docs/features/contact/ast-1669-manage-candidates-slack-bind-dropdown.md`, commit `docs(AST-1669): Radia review — clean`, push sub ref.
- Post slim upshot via `linear_proxy --as radia save-comment`; move **Review Posted** → **User Testing** (PROCEED, no fix-now items).

---

**Slim Linear upshot (Chuckles posts):**

```
[code-rubric] PROCEED (Commit: d51bda97) Slack bind dropdown clean
```
