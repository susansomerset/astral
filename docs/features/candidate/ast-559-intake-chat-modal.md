<!-- linear-archive: AST-559 archived 2026-06-23 -->

## Linear archive (AST-559)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-559/intake-chat-modal-and-candidate-navigation-candidate-intake-chat  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-539 — Candidate Intake Chat Session  
**Blocked by / blocks / related:** parent: AST-539

### Description

## What this implements

Candidate **Intake** nav item above Profile, modal chat UI wired to intake session API: paste resume (required) and optional cover/LinkedIn before/during start, chat thread showing `assistant_message`, **Generate Profile** button gated on `ready_to_build`, one build per modal session, post-build close to review on existing Profile/context/search-term screens.

## Acceptance criteria

1. User can open Intake (nav above Profile) for a selected candidate, paste required resume text and optional cover/LinkedIn text, and start a session that displays Estelle's first interview message per the `initiate_candidate` shape (intro, material upshot, intake overview, proposed approach).
2. Each user reply advances the thread via `assistant_message`; Estelle responses include `ready_to_build`; **Generate Profile** is disabled until the latest response has `ready_to_build: true`.
3. While `ready_to_build: true`, the user can still send `candidate_response` turns and Estelle may ask further clarifications before generate is pressed.
4. **Generate Profile** sends `build_request` and persists all seven output areas as flat text strings verifiable on existing candidate UI/API.
5. After a successful build in a session, **Generate Profile** cannot be fired again in that same modal session; opening a new session allows a new build.
6. Closing and reopening the same intake session resumes the conversation (not a blank session).

## Boundaries

Does not implement backend session/agent/persistence (sibling Ada ticket). No Intake-modal cost/timesheet UI. Config-driven nav; no hardcoded agent ids in React.

## Notes for planning

Depends on Ada API contract. NAV_CONFIG entry above Profile. Follow existing modal/chat patterns and api client conventions.

## Git branch (authoritative)

Per **orientation-astral** § Branch law: parent **ftr/ast-539-candidate-intake-chat-session**, child **sub/AST-539/<child-id>-intake-chat-modal** (slug at dispatch).

### Comments

#### betty — 2026-06-05T18:01:34.277Z
**Tests Ready** — manifest for UAT UX delta (Katherine **`test-astral`**).

**Publish:** `origin/sub/AST-539/AST-559-intake-chat-modal` @ `7fac91b9`
**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `967e55e51b46e6251cb21876d60374db7e75ac4b24fbe5dd712fd05df0feac0d`

**Pre-run (engineer tree):** `git fetch origin` → `git merge origin/dev` → `git merge origin/ftr/ast-539-candidate-intake-chat-session` (when exists) → `git merge origin/sub/AST-539/AST-558-intake-session-api` → `git merge origin/sub/AST-539/AST-559-intake-chat-modal`

**Manifest:**

1. `cd src/ui/frontend && npx tsc -b --noEmit`
2. `cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx`

**Coverage (§6c + UX delta):**
- **Page:** empty candidate; **Start Intake** confirm gate (Continue opens modal / Cancel stays closed); missing resume toast + no confirm; routed page with auto-start (no modal paste, no Start interview)
- **Modal:** `autoStart` POST with persisted `materials`; resume active session without duplicate POST; `can_build` gate; Send while ready; single build; New session confirm

**Bible:** §7.13zr **AST-559** row + UAT delta note (confirm gate, auto-start from `context.*`).

If manifest or test is wrong: `[qa-handoff]` on this ticket, assign Betty — do not edit tests on publish ref.

#### chuckles — 2026-06-05T17:59:21.168Z
[check-linear]

@Betty White — **AST-559** is back at **Code Complete** after Katherine's UAT UX delta.

**Publish:** `origin/sub/AST-539/AST-559-intake-chat-modal` @ `b8c8d4a8`
**Changes:** confirm gate, auto-start from persisted context, no modal paste.

Please run **qa-astral** on this publish ref (bible + manifest), move to **Tests Ready**, reassign Katherine for **test-astral**. Parent **AST-539** stays **User Testing**.

— Chuckles

#### katherine — 2026-06-03T22:23:30.116Z
`origin/sub/AST-539/AST-559-intake-chat-modal` @ `b8c8d4a8` — UAT UX delta (confirm gate, auto-start from persisted context, no modal paste).

#### betty — 2026-06-03T00:41:51.821Z
**Rollup bible reconcile** — `origin/sub/AST-539/AST-559-intake-chat-modal` @ `1dcd988a`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `8303a7042bdc8188265d82690bb728202b2938dd9397baff6dec59b06b90e71e`

**What changed:** §7.13zr epic table (**AST-558** + **AST-559** rows) replaces ftr’s backend-only §7.13zr; restored **§7.13zu** from cumulative `dev-betty` (was missing on sub tip). Rollup note documents fast-forward into `origin/ftr/ast-539-candidate-intake-chat-session`.

**Chuckles:** re-run **`rollup-child`** AST-559 → parent ftr (bible-only conflict should clear).

Status unchanged **User Testing**; Katherine remains assignee.

— Betty

#### betty — 2026-06-03T00:37:24.394Z
[check-linear]

**[qa-handoff] cleared** — mocks aligned to AST-558 **`IntakeSessionDto`** contract.

**Changes:**
- `test_CandidateIntake.test.tsx` — `/intake/sessions`, `/sessions/active`, `…/turns`, `…/build`; `transcript[].text`; `can_build` gate; session **POST** carries materials (no `PUT …/data` on start)
- `docs/ASTRAL_TEST_BIBLE.md` §7.13zr — manifest + handoff note

**Publish:** `origin/sub/AST-539/AST-559-intake-chat-modal` @ `71cb5fa7`  
**Bible shasum (publish ref):** `9320648eca43b17411ef69b6b6e0ca94598a0ce7`

**Manifest (Katherine — `test-astral`):**

1. `cd src/ui/frontend && npx tsc -b --noEmit`
2. `cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx`

**Pre-run:** `git fetch origin` → merge `origin/dev` → merge `origin/sub/AST-539/AST-558-intake-session-api` → merge `origin/sub/AST-539/AST-559-intake-chat-modal`

Reassigned Katherine for **`test-astral`**. Status stays **Tests Ready**.

#### katherine — 2026-06-03T00:33:06.552Z
[qa-handoff]

@Betty White — Product fix for Radia **fix-now** items is on `origin/sub/AST-539/AST-559-intake-chat-modal` @ `8ee65ee5`.

**Product changes:** `IntakeChatModal` now uses AST-558 paths (`/intake/sessions`, `/sessions/active`, `…/turns`, `…/build`) and maps flat `IntakeSessionDto` (`session_id`, `transcript[].text`, `can_build`, `build_completed`). Composer placeholder neutralized.

**Tests:** `test_CandidateIntake.test.tsx` mocks still target pre-558 contract (`/intake/session`, `IntakeTurnResponse`, `PUT …/data` on start). Manifest fails 6/9 after product fix. Please update mocks/fixtures to AST-558 shape and republish bible/manifest; reassign Katherine when Tests Ready.

**Pre-run (unchanged integration):** `git fetch origin` → merge `origin/dev` → merge `origin/sub/AST-539/AST-558-intake-session-api` (or parent ftr) → merge `origin/sub/AST-539/AST-559-intake-chat-modal`.

#### radia — 2026-06-03T00:28:47.054Z
## Review (Radia) — `origin/dev...origin/sub/AST-539/AST-559-intake-chat-modal`

**Doc:** `docs/features/candidate/ast-559-intake-chat-modal.md` § Review (Radia) @ `6f4abbb3`

### fix-now

1. **`IntakeChatModal.tsx` — REST paths vs shipped AST-558**  
   UI uses plan contract: `GET/POST /api/candidates/{id}/intake/session`, `POST …/intake/session/turn` with `{ mode }`. Ada's tip on `origin/sub/AST-539/AST-558-intake-session-api` exposes `POST …/intake/sessions` (materials in create body), `GET …/intake/sessions/active`, `POST …/intake/sessions/{session_id}/turns`, `POST …/intake/sessions/{session_id}/build`. Parent ftr integration will 404 until UI aligns with AST-558 or backend adds shims.

2. **`IntakeChatModal.tsx` — JSON DTO mapping**  
   UI expects `IntakeTurnResponse` (`assistant_message`, `session.messages[]` with `content`, `intake_session_id`). AST-558 `get_intake_session_dto` returns `session_id`, `transcript[]` with `text`, `can_build`, `status` — no turn wrapper. Thread stays empty without mapping even if paths were corrected.

### discuss

- **§1.4 / ticket boundary:** composer `placeholder="Reply to Estelle…"` — hardcoded agent name; plan Self-review says no Estelle strings in React. Neutral copy or server-driven label?
- **Test coverage:** Plan Stage 4 nav-order test (Intake above Profile in `NavigationShell`) not in manifest — route/modal tests only.

### advisory

- **`docs/ASTRAL_TEST_BIBLE.md`** on publish tip includes sibling epic bible rows (AST-549/558/539) — expected on integrated sub ref, not Katherine product scope.

### What's solid

Nav + route shell, gating (`ready_to_build` / `build_completed` / build-once), session-resume intent, frontend layer hygiene, Vitest depth for modal flows.

**Verdict:** Structure and gating look good; **resolve-astral blocked on AST-558 contract alignment** before parent UAT.

#### betty — 2026-06-03T00:08:42.671Z
**Tests Ready** — manifest for `test-astral` (Katherine).

**Publish:** `origin/sub/AST-539/AST-559-intake-chat-modal` @ `f8dba7fe`  
**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `028af8f8765496b00cc5b9a9888989190d0047fe7981bd4b061755c9bb105c87`

**Pre-run (engineer tree):** `git fetch origin` → `git merge origin/dev` → `git merge origin/sub/AST-539/AST-558-intake-session-api` → `git merge origin/sub/AST-539/AST-559-intake-chat-modal`

**Manifest:**

1. `cd src/ui/frontend && npx tsc -b --noEmit`
2. `cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx`

**Coverage (§6c routed page):** `test_CandidateIntake.test.tsx` — empty candidate state; routed page renders modal with first-paint mocks; materials required before Start; persist + `POST …/intake/session`; resume via `GET …/intake/session` (404 vs active thread); **Generate Profile** gated on `ready_to_build`; Send while ready; single `build_request`; **New intake session** after build with confirm.

If manifest or test is wrong: `[qa-handoff]` on this ticket, assign Betty — do not edit tests on publish ref.

— Betty

#### katherine — 2026-06-02T22:32:02.086Z
Plan: `docs/features/candidate/ast-559-intake-chat-modal.md`

https://github.com/susansomerset/astral/blob/sub/AST-539/AST-559-intake-chat-modal/docs/features/candidate/ast-559-intake-chat-modal.md

**Scope:** `Single-Component` — Candidate frontend only (NAV_CONFIG Intake above Profile, `/candidate/intake` host page, `IntakeChatModal`, CSS, Vitest); defers session API to **AST-558**.

**Conf:** `Medium` — Established Modal/api/NAV patterns; REST contract in the plan must match Ada’s **AST-558** publish before Stage 3 wiring.

**Risk:** `Medium` — `ready_to_build` / `build_completed` gating errors would block or duplicate Generate Profile; plan uses server flags and disabled button state.

**Stages:** (1) nav + route shell, (2) modal layout/materials without API, (3) wire intake session endpoints (blocked until `origin/sub/AST-539/AST-558-intake-session-api` exists), (4) component tests.

Publish: `origin/sub/AST-539/AST-559-intake-chat-modal` @ `1507decc`.

---

# Intake chat modal and Candidate navigation (Candidate Intake Chat Session)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-559/intake-chat-modal-and-candidate-navigation-candidate-intake-chat  
**Parent:** https://linear.app/astralcareermatch/issue/AST-539/candidate-intake-chat-session  
**Blocked by:** https://linear.app/astralcareermatch/issue/AST-558/intake-session-api-agent-turns-and-build-persistence-candidate-intake (Ada — backend API must exist before Stage 3 wiring)

**Publish ref (origin):** `sub/AST-539/AST-559-intake-chat-modal`  
**Parent integration ref:** `ftr/ast-539-candidate-intake-chat-session`

Candidate **Intake** nav entry (above Profile) opens a wide modal chat: paste required resume and optional cover/LinkedIn source text, run Estelle-led intake turns via Ada’s session API, gate **Generate Profile** on `ready_to_build`, allow one `build_request` per modal session, then close to review on existing Profile/context/Company Search Terms screens. No backend session logic, no agent ids in React, no intake-modal cost UI.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Insert **Intake** nav item above Profile in `NAV_CONFIG` Candidate group | utils |
| `src/ui/frontend/src/routes.tsx` | Add `/candidate/intake` route | ui |
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | New page: mounts intake modal (route target for nav) | ui |
| `src/ui/frontend/src/components/IntakeChatModal.tsx` | Modal chat UI, materials form, thread, composer, Generate Profile | ui |
| `src/ui/frontend/src/App.css` | Styles for intake materials panel, message thread, composer, primary/secondary actions | ui |
| `tests/component/frontend/pages/test_CandidateIntake.test.tsx` | Vitest: nav route, materials validation, thread, ready gate, build-once, resume session | ui |

**Not in scope:** `src/core/*`, `src/data/*`, `src/ui/api/*` (Ada **AST-558**), prompt text files on parent, Execution History UI, post-build auto `parse_candidate_resume` / `craft_resume_base`.

---

## API contract (UI consumes — implemented by AST-558)

The UI must not invent alternate paths. If Ada’s shipped paths or JSON keys differ, **stop** on **AST-559** with a Linear comment naming the drift; do not adapt silently.

### Types (TypeScript in `IntakeChatModal.tsx` or `src/ui/frontend/src/lib/intakeTypes.ts` if the modal file exceeds ~400 lines)

```typescript
export type IntakeTurnMode = "initiate_candidate" | "candidate_response" | "build_request"

export interface IntakeChatMessage {
  role: "user" | "assistant"
  content: string
  mode?: IntakeTurnMode
}

export interface IntakeSession {
  intake_session_id: string
  messages: IntakeChatMessage[]
  ready_to_build: boolean
  build_completed: boolean
}

export interface IntakeTurnResponse {
  ready_to_build: boolean
  assistant_message: string
  build_completed: boolean
  session: IntakeSession
}
```

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/candidates/{candidate_id}/intake/session` | Return active session for resume-after-close, or `404` with `{ "error": "no_active_session" }` when none |
| `POST` | `/api/candidates/{candidate_id}/intake/session` | Create new session. Body: `{ "mode": "initiate_candidate" }` only after source materials saved (see Stage 2). Response: `IntakeTurnResponse` (first assistant message included) |
| `POST` | `/api/candidates/{candidate_id}/intake/session/turn` | Body: `{ "mode": "candidate_response" \| "build_request", "message": string }` — `message` required for `candidate_response`, omit or `""` for `build_request`. Response: `IntakeTurnResponse` |

**Source materials (not session-owned):** Persist on the candidate record before `initiate_candidate`, using existing save API:

- `PUT /api/candidates/{candidate_id}/data` with JSON body paths:
  - `context.starting_resume_text` (required non-empty before Start)
  - `context.sample_cover_text` (optional)
  - `context.linkedin_profile_text` (optional)

**Errors:** Non-OK responses expose `{ "error": string }` (existing API pattern). Show via `Toast` variant `error`; do not parse stack traces in UI.

⚠️ **Decision:** One active session per candidate (`GET` + `POST` create) matches parent AC #11 and AST-558 notes; **New session** after build is explicit `POST` create only (Stage 3), not automatic on reopen.

---

## Stage 1: Navigation and route shell

**Done when:** With a selected candidate, sidebar shows **Intake** above **Profile**; clicking it navigates to `/candidate/intake`, which renders the intake modal open; `npx tsc -b --noEmit` passes; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, inside the **Candidate** group `items` list, insert **before** the Profile entry:

   ```python
   {"label": "Intake", "path": "/candidate/intake"},
   ```

   Leave Profile and siblings unchanged.

2. In `src/ui/frontend/src/routes.tsx`, under `// --- Candidate ---`, add import:

   ```typescript
   import CandidateIntake from "./pages/CandidateIntake"
   ```

   Add route after profile routes:

   ```typescript
   { path: "candidate/intake", element: <CandidateIntake /> },
   ```

3. Create `src/ui/frontend/src/pages/CandidateIntake.tsx`:

   - Import `useNavigate` from `react-router-dom`, `useCandidate` from `../contexts/CandidateContext`, `IntakeChatModal` from `../components/IntakeChatModal`.
   - If `!selectedId`, render `<p className="entity-empty">Select a candidate to open Intake.</p>` (same class as other candidate pages).
   - Otherwise render `<IntakeChatModal open onClose={() => navigate("/candidate/profile")} candidateId={selectedId} />` only (no extra page chrome).

4. Run `python3 -m py_compile src/utils/config.py` and `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Intake uses a dedicated route (config `path`) so `NAV_CONFIG` / `routes.tsx` stay in sync per **ASTRAL_CODE_RULES §2.1**; the route page is a thin host for the modal, not a second full-page editor.

---

## Stage 2: Intake modal — materials, layout, and API-free structure

**Done when:** `IntakeChatModal` renders materials textareas, empty-state Start button (disabled without resume), placeholder thread area, disabled **Generate Profile**, and a Send button; component accepts `candidateId` and `open` props; `tsc` passes. **No** live intake API calls in this stage — use local state only.

1. Create `src/ui/frontend/src/components/IntakeChatModal.tsx`:

   - Props: `{ open: boolean; onClose: () => void; candidateId: string }`.
   - Use `Modal` from `./Modal` with `size="wide"`, `title="Candidate Intake"`, **no** `onSave` prop (close uses modal X / Cancel only).
   - Import `api` from `../lib/api`, `Toast` from `./Toast`, `useCallback` / `useEffect` / `useState` / `useRef` from `react`.

2. **Load candidate source fields** on `open` + `candidateId` change:

   ```typescript
   api(`/api/candidates/${candidateId}`).then(r => r.json())
   ```

   Initialize local state `materials` from `candidate_data.context`:

   - `starting_resume_text` ← `context.starting_resume_text` or `""`
   - `sample_cover_text` ← `context.sample_cover_text` or `""`
   - `linkedin_profile_text` ← `context.linkedin_profile_text` or `""`

3. **Materials panel** (top of modal body, always visible until session started):

   - Three `<textarea className="intake-materials-field">` with labels matching Profile copy: **Original Resume Text** (required), **Sample Cover Letter** (optional), **LinkedIn Profile Text** (optional).
   - Bind to `materials` state.

4. **Thread region** (`<div className="intake-thread">`):

   - Map `messages: IntakeChatMessage[]` (state, initially `[]`).
   - User bubbles: `intake-msg intake-msg--user`; assistant: `intake-msg intake-msg--assistant`.
   - `useRef` on thread container; `useEffect` scroll to bottom when `messages` length changes.

5. **Composer** (`<div className="intake-composer">`):

   - `<textarea className="intake-composer-input">` bound to `draft` state.
   - **Send** button: disabled when `!session` or `draft.trim()` empty or `busy`.
   - **Generate Profile** button: `className="modal-btn save intake-generate-btn"`, `disabled={!readyToBuild || buildCompleted || busy}`.

6. **Footer actions** (inside modal body below composer, not Modal’s save footer):

   - **Start interview** — visible when `!session`; disabled when `!materials.starting_resume_text.trim()` or `busy`.
   - **New intake session** — visible when `session && buildCompleted`; calls handler stubbed in Stage 3.

7. In `src/ui/frontend/src/App.css`, append section **Intake chat modal**:

   - `.intake-materials-field` — full width, min-height 4rem, margin-bottom 0.75rem.
   - `.intake-thread` — flex 1, overflow-y auto, max-height  min(50vh, 480px), padding 0.5rem 0, border-top 1px solid var(--border, #333).
   - `.intake-msg` — max-width 85%, padding 0.5rem 0.75rem, margin-bottom 0.5rem, border-radius 6px.
   - `.intake-msg--user` — align-self flex-end, margin-left auto, background `rgba(255,255,255,0.06)`.
   - `.intake-msg--assistant` — align-self flex-start, background `rgba(255,255,255,0.03)`.
   - `.intake-composer` — display flex, gap 0.5rem, margin-top 0.75rem; `.intake-composer-input` flex 1 min-height 2.5rem.
   - `.intake-generate-btn` — margin-left auto when placed in a flex row with Send.

8. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 3: Wire session API and interaction logic

**Done when:** With **AST-558** API on `dev-kath` (merge `origin/sub/AST-539/AST-558-intake-session-api` or parent `ftr` after Ada publishes), manual flow works: start → chat → ready gate → build once → resume session on reopen; `tsc` passes.

**Pre-step (mandatory):** `git fetch origin`. If `git ls-remote origin refs/heads/sub/AST-539/AST-558-intake-session-api` is empty, **stop** — comment on **AST-559** that Stage 3 is blocked on Ada publish; do not mock production API in component code.

1. **`git merge origin/sub/AST-539/AST-558-intake-session-api`** on `dev-kath` when ref exists (else merge parent `ftr` if sibling landed there). Resolve conflicts only in files this ticket owns.

2. On modal open (`useEffect` when `open && candidateId`):

   - `GET /api/candidates/${candidateId}/intake/session`
   - If `200`: set `session`, `messages` from `session.messages`, `readyToBuild` from `session.ready_to_build`, `buildCompleted` from `session.build_completed`.
   - If `404`: leave `session` null (show materials + Start).

3. **`persistMaterials()`** helper — before start:

   ```typescript
   await api(`/api/candidates/${candidateId}/data`, {
     method: "PUT",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({
       context: {
         starting_resume_text: materials.starting_resume_text,
         sample_cover_text: materials.sample_cover_text,
         linkedin_profile_text: materials.linkedin_profile_text,
       },
     }),
   })
   ```

   On failure: toast error, return false.

4. **Start interview** (`handleStart`):

   - Set `busy` true.
   - `await persistMaterials()`; if false, abort.
   - `POST /api/candidates/${candidateId}/intake/session` with body `{ "mode": "initiate_candidate" }`.
   - On success: apply `IntakeTurnResponse` — append assistant message to thread, set `session`, `readyToBuild`, `buildCompleted` from response.
   - On failure: toast `error` from JSON.
   - `busy` false.

5. **Send** (`handleSend`):

   - Require `session` and non-empty `draft`.
   - `POST .../intake/session/turn` with `{ "mode": "candidate_response", "message": draft.trim() }`.
   - Optimistic UX: append user message locally, clear `draft`, then merge server `session.messages` from response (prefer server transcript to avoid drift).
   - Update `readyToBuild`, `buildCompleted` from response.

6. **Generate Profile** (`handleBuild`):

   - Guard: if `buildCompleted`, return (button already disabled).
   - `POST .../intake/session/turn` with `{ "mode": "build_request" }`.
   - On success: append assistant message if `assistant_message` non-empty; set `buildCompleted` true from response; toast success `"Profile generated — review on Profile and context screens."`
   - Keep **Generate Profile** disabled for remainder of session.

7. **New intake session** (`handleNewSession`):

   - Only when `buildCompleted`.
   - `useUserConfirm` from `./UserPrompt`: `"Start a new intake session? The previous conversation will remain stored but a new session will begin."`
   - On confirm: `POST .../intake/session` with `{ "mode": "initiate_candidate" }` after `persistMaterials()` (same as Start).
   - Reset local `messages` from response session; set `buildCompleted` false.

8. **Close behavior:** `onClose` from page navigates away; do not DELETE session. No localStorage for transcript (server is source of truth per AC #6).

9. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Prefer server-returned `session.messages` after each turn over append-only local merge, so resume-after-close matches backend ordering.

---

## Stage 4: Component tests

**Done when:** `npm run test:component -- test_CandidateIntake.test.tsx` passes; tests mock `api` only (no real HTTP).

1. Create `tests/component/frontend/pages/test_CandidateIntake.test.tsx` following `test_CandidateProfile.test.tsx` patterns (`vi.mock` api, `renderWithProviders`, `candidateId` from `page-mocks`).

2. **`installIntakeMocks`** — handle:

   - `GET /api/candidates` — list with selected candidate
   - `GET /api/candidates/${id}` — candidate with empty/prefilled context
   - `PUT /api/candidates/${id}/data` — success
   - `GET /api/candidates/${id}/intake/session` — 404 initially, or 200 with fixture session
   - `POST .../intake/session` and `POST .../turn` — return canned `IntakeTurnResponse`

3. Test cases (describe **`AST-559 intake chat modal`**):

   - **nav renders Intake** — render `NavigationShell` or mount route with `MemoryRouter` initial `/candidate/intake`; assert link **Intake** exists above Profile (query order in Candidate group).
   - **start disabled without resume** — open modal; **Start interview** disabled until resume textarea non-empty.
   - **start posts materials then initiate** — fill resume, click Start; assert `PUT` data then `POST` session with `initiate_candidate`; first assistant message visible.
   - **generate disabled until ready** — mock turn with `ready_to_build: false`; button disabled; then mock `ready_to_build: true`; enabled.
   - **build once** — click Generate; assert `build_request` turn; second click does not fire (disabled).
   - **resume session** — `GET session` returns existing messages; thread shows prior assistant line without Start panel (`session` non-null).

4. Run:

   ```bash
   cd src/ui/frontend && npm run test:component -- \
     ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx
   ```

---

## Self-Assessment

**Scope:** `Single-Component` — Frontend candidate UI only (`config.py` nav row, one page, one modal component, CSS, Vitest); no core/data/API implementation on this ticket.

**Conf:** `Medium` — Modal, `api` client, and `NAV_CONFIG` patterns are established; exact intake REST shapes depend on Ada **AST-558** matching the contract above.

**Risk:** `Medium` — Wrong `ready_to_build` / `build_completed` gating would block or duplicate profile generation; mitigated by server-authoritative flags and disabled button state.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.4 No hardcoded sets in UI | Nav label/path in `NAV_CONFIG` only; no Estelle/agent id strings in React |
| §2.1 Config source of truth | Intake nav entry in `NAV_CONFIG`; routes synced |
| §3.5 Frontend placement | Page in `pages/`, component in `components/`, styles in `App.css` |
| §1.3 DRY | Reuse `Modal`, `api`, `Toast`, `useCandidate`; reuse `PUT .../data` for source materials |
| Ticket boundary | No backend; no cost UI; no sibling AST-558 persistence logic |

No `conf-!!-NONE` conflicts identified.

---

## Review (build)

**Branch:** `origin/sub/AST-539/AST-559-intake-chat-modal`  
**Built by:** Katherine (`build-astral`)  
**Status:** Awaiting `qa-astral` / Betty component tests (Stage 4).

**Note:** Session API wired per contract in this doc (`/intake/session`, `/intake/session/turn`). Ada **AST-558** plan doc uses different paths (`/sessions`, `/sessions/<id>/turns`) — reconcile before UAT if backend ships AST-558 shape only.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-539/AST-559-intake-chat-modal` (tip `f8dba7fe`)  
**Reviewer:** Radia (`review-astral`)  
**Date:** 2026-06-02

### What's solid

- **Plan fidelity (UI structure):** `NAV_CONFIG` Intake above Profile, `/candidate/intake` route, thin `CandidateIntake` page hosting wide `IntakeChatModal`, materials panel + thread + composer + footer actions match Stages 1–2 layout.
- **Gating logic:** `ready_to_build` / `build_completed` / `busy` drive Generate Profile and Send disable states; build handler short-circuits when `buildCompleted`; tests assert one `build_request` turn.
- **Session resume:** `GET` on open hydrates thread when active session exists; Start hidden when `session` non-null (AC #6 intent).
- **Layer / rules (§3.2, §3.5):** Frontend-only diff — `api` client, `Modal`, `Toast`, `useUserConfirm`; no `src/data` / `src/core` smuggled onto this ticket.
- **Tests:** `test_CandidateIntake.test.tsx` covers routed page, materials validation, start flow, resume, ready gate, build-once, new session confirm — good manifest depth for Betty's bible entry.

### Issues

| Severity | Bucket | Location | Finding |
|----------|--------|----------|---------|
| **fix-now** | Plan fidelity / integration | `IntakeChatModal.tsx` (all intake `api()` calls) | **REST contract drift vs shipped AST-558.** UI calls plan paths (`GET/POST …/intake/session`, `POST …/intake/session/turn` with `{ mode }`). Ada's published API on `origin/sub/AST-539/AST-558-intake-session-api` uses `POST …/intake/sessions` (materials in create body), `GET …/intake/sessions/active`, `POST …/intake/sessions/<session_id>/turns` (`{ message }` only), `POST …/intake/sessions/<session_id>/build`. Parent ftr merge will 404 every intake call until UI aligns with AST-558 or backend adds shim routes. |
| **fix-now** | Plan fidelity / integration | `IntakeChatModal.tsx` types + `applyTurnResponse` | **JSON shape drift.** UI expects `IntakeTurnResponse` (`assistant_message`, nested `session.messages[]` with `content`, `intake_session_id`). AST-558 `get_intake_session_dto` returns flat `session_id`, `transcript[]` with `text` (not `content`), `can_build`, `status` — no turn wrapper. Thread will render empty even if paths were fixed without mapping. |
| **discuss** | §1.4 / ticket boundary | `IntakeChatModal.tsx` composer `placeholder="Reply to Estelle…"` | Hardcoded agent display name in React; plan Self-review claims no Estelle strings. Prefer neutral copy (`Reply…`) or config-driven label from server/nav if product wants agent name in UI. |
| **discuss** | Test coverage | `test_CandidateIntake.test.tsx` | Plan Stage 4 **nav renders Intake above Profile** (NavigationShell link order) not exercised — route/modal tests only. Optional follow-up unless Susan wants strict plan checklist parity. |
| **advisory** | Scope hygiene | `docs/ASTRAL_TEST_BIBLE.md` on publish tip | Large bible edits (AST-549/558/539 clusters) ride this branch; not Katherine product code but increases review surface — expected on integrated sub ref. |

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| Reconcile UI to **AST-558 shipped contract** (paths + DTO mapping) or get Ada to add backward-compatible shim matching this plan | Katherine (`resolve-astral`) | Plan build note already flagged drift; **stop silent adaptation** per plan API section. Store `session_id` from create/active GET for turn/build URLs. Map `transcript[].text` → display `content`. Use `can_build` or `ready_to_build` per DTO. |
| Neutralize composer placeholder (drop agent name) | Katherine | One-line copy change when touching modal. |
| Optional: NavigationShell Intake-above-Profile test | Katherine / Betty | Only if Susan wants Stage 4 nav-order AC in manifest. |

**Verdict:** UI structure and gating are sound for the ticket scope, but **integration with AST-558 is blocked** until REST/JSON alignment — treat as **fix-now** before parent UAT.

---

## Resolution (resolve-astral)

**Date:** 2026-06-02  
**Engineer:** Katherine (`resolve-astral`)  
**Publish:** `origin/sub/AST-539/AST-559-intake-chat-modal`

### fix-now (Radia review)

1. **REST paths aligned to AST-558 shipped contract**
   - `GET …/intake/sessions/active` — resume active session (404 = no session)
   - `POST …/intake/sessions` — create/start with materials in body (`starting_resume_text`, optional cover/LinkedIn)
   - `POST …/intake/sessions/{session_id}/turns` — `{ message }` for candidate replies
   - `POST …/intake/sessions/{session_id}/build` — generate profile (no turn body)

2. **DTO mapping** — `IntakeChatModal` consumes flat `IntakeSessionDto` (`session_id`, `transcript[]` with `text`, `can_build`, `build_completed`). UI maps `transcript[].text` → thread `content`; stores `session_id` for turn/build URLs. Generate Profile gated on server `can_build`.

### discuss (addressed)

- Composer placeholder neutralized to `Reply…` (no hardcoded agent name in React).

### deferred

- Stage 4 **nav order** test (Intake above Profile in `NavigationShell`) — optional per Radia; Betty may extend manifest if Susan wants strict plan parity.

### verification (2026-06-03)

- Betty **`[qa-handoff]` cleared** — mocks aligned to AST-558; publish @ `71cb5fa7`.
- Manifest green on `dev-kath` (`tsc` + 9/9 Vitest).
- §9a dry-run: `origin/sub/AST-539/AST-559-intake-chat-modal` clean into `origin/dev` and `origin/ftr/ast-539-candidate-intake-chat-session`.

---

## UAT delta (Susan AST-539, 2026-06-03)

**Built by:** Katherine (`build-astral`)  
**Publish:** `origin/sub/AST-539/AST-559-intake-chat-modal`

1. **Confirm before modal** — `CandidateIntake` validates persisted `context.*`, blocks without resume, warns on missing cover/LinkedIn, confirm dialog before modal opens; cancel → Profile.
2. **No modal paste / Start** — materials panel and Start interview removed from `IntakeChatModal`.
3. **Auto-start** — on confirm OK, modal shows hold copy then `POST …/intake/sessions` with persisted materials (no `PUT …/data` from modal).
4. **Resume** — `GET …/intake/sessions/active` unchanged; active session skips auto-start and shows existing transcript.
5. **Estelle intro** — first assistant turn rendered from session DTO `transcript` after POST returns.
