# AST-583 — UAT: Intake Continue vs Start Over dialog

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-583/uat-intake-continue-vs-start-over-dialog  
**Parent:** https://linear.app/astralcareermatch/issue/AST-539/candidate-intake-chat-session  
**Publish ref:** `sub/AST-539/AST-583-intake-continue-vs-start-over` (origin only)

Susan UAT 2026-06-05 on **AST-539**: opening **Intake** when the candidate already has an **ACTIVE** intake session must prompt **"Would you like to continue your intake?"** with **Continue** (default) to resume the existing thread, or **Start Over** to archive via **AST-582** (`POST …/sessions/active/archive`) and then auto-start a fresh session. No backend changes — wire the page entry flow in `CandidateIntake.tsx` and cover with Vitest in `test_CandidateIntake.test.tsx`.

**Dependency:** **AST-582** archive API must be on the engineer tree (`origin/sub/AST-539/AST-582-archive-intake-to-intakes-old` merged via parent `ftr/`). Ticket description typo **AST-580** refers to **AST-582**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | Active-session probe; resume dialog; archive-then-open on Start Over | ui |
| `tests/component/frontend/pages/test_CandidateIntake.test.tsx` | Vitest: resume dialog, Continue, Start Over, dismiss | ui |

**Out of scope:** `IntakeChatModal.tsx` (resume/auto-start logic already correct), `src/core/intake.py`, `src/ui/api/api_intake.py`, `App.css` (reuse existing `user-prompt-*` / `modal-*` classes).

---

## Stage 1: Page entry — active session gate

**Done when:** Opening `/candidate/intake` with an ACTIVE session shows the resume prompt before the chat modal; **Continue** resumes without archive/create; **Start Over** archives then fresh auto-starts; no active session keeps the existing **Start Intake** materials confirm; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/pages/CandidateIntake.tsx`, add module-level constant after `intakeConfirmMessage`:

   ```typescript
   const RESUME_INTAKE_TITLE = "Resume Intake"
   const RESUME_INTAKE_MESSAGE = "Would you like to continue your intake?"
   ```

2. In the same file, add a small local component **above** `export default function CandidateIntake` (same visual pattern as `UserPrompt.tsx`, no global API change):

   ```typescript
   type IntakeResumeDialogProps = {
     onContinue: () => void
     onStartOver: () => void
     onDismiss: () => void
   }

   function IntakeResumeDialog({ onContinue, onStartOver, onDismiss }: IntakeResumeDialogProps) {
     return (
       <div className="modal-overlay user-prompt-overlay" role="presentation" onClick={onDismiss}>
         <div
           className="modal-card user-prompt-card"
           role="alertdialog"
           aria-labelledby="intake-resume-title"
           aria-describedby="intake-resume-message"
           onClick={e => e.stopPropagation()}
         >
           <div className="modal-header">
             <h2 id="intake-resume-title" className="modal-title">{RESUME_INTAKE_TITLE}</h2>
           </div>
           <div className="modal-body">
             <p id="intake-resume-message" className="user-prompt-message">{RESUME_INTAKE_MESSAGE}</p>
           </div>
           <div className="modal-footer">
             <button type="button" className="modal-btn cancel" onClick={onStartOver}>
               Start Over
             </button>
             <button type="button" className="modal-btn save" onClick={onContinue}>
               Continue
             </button>
           </div>
         </div>
       </div>
     )
   }
   ```

3. Add page state inside `CandidateIntake`:

   ```typescript
   const [resumeDialogOpen, setResumeDialogOpen] = useState(false)
   ```

4. Replace the existing `useEffect` body (lines 42–89) with this sequence — keep `cancelled` guard and `selectedId` early return:

   a. `setModalOpen(false)` and `setResumeDialogOpen(false)` when `selectedId` changes.

   b. `GET /api/candidates/${selectedId}` — same as today; load `materials` from `candidate_data.context`.

   c. If `!loaded.starting_resume_text.trim()` — same toast + `goProfile()`; **return** (no dialogs).

   d. `setMaterials(loaded)`.

   e. `GET /api/candidates/${selectedId}/intake/sessions/active`:
      - **200:** `setResumeDialogOpen(true)` — **do not** show `intakeConfirmMessage` / **Start Intake** confirm.
      - **404:** fall through to existing flow: `await confirm(intakeConfirmMessage(loaded), { title: "Start Intake", confirmLabel: "Continue" })` — on `true` → `setModalOpen(true)`; on `false` → `goProfile()`.
      - **Other errors:** toast `"Failed to load intake session"` (or reuse candidate load error pattern) + `goProfile()`.

   f. Do **not** open the modal until the user chooses on the resume dialog or passes the no-active **Start Intake** confirm.

5. Add three callbacks on `CandidateIntake`:

   ```typescript
   const openModalAfterResumeChoice = useCallback(() => {
     setResumeDialogOpen(false)
     setModalOpen(true)
   }, [])

   const handleResumeContinue = useCallback(() => {
     openModalAfterResumeChoice()
   }, [openModalAfterResumeChoice])

   const handleResumeStartOver = useCallback(async () => {
     if (!selectedId) return
     try {
       const r = await api(`/api/candidates/${selectedId}/intake/sessions/active/archive`, {
         method: "POST",
       })
       if (!r.ok) {
         const e = await r.json().catch(() => ({}))
         throw new Error((e as { error?: string }).error ?? "Failed to archive intake session")
       }
       openModalAfterResumeChoice()
     } catch (e) {
       setResumeDialogOpen(false)
       setToast({
         text: e instanceof Error ? e.message : "Failed to start over",
         variant: "error",
       })
       goProfile()
     }
   }, [selectedId, openModalAfterResumeChoice, goProfile])

   const handleResumeDismiss = useCallback(() => {
     setResumeDialogOpen(false)
     goProfile()
   }, [goProfile])
   ```

6. In the JSX return, render the resume dialog **before** the modal block:

   ```tsx
   {resumeDialogOpen && (
     <IntakeResumeDialog
       onContinue={handleResumeContinue}
       onStartOver={() => void handleResumeStartOver()}
       onDismiss={handleResumeDismiss}
     />
   )}
   ```

   Keep `IntakeChatModal` unchanged: `autoStart`, `materials`, `candidateId={selectedId}`.

7. **Continue path:** `IntakeChatModal` with `autoStart` loads active session via its existing `loadActiveSession` → no `POST …/sessions` (verified by existing test `resumes active session on open without auto-start POST`).

8. **Start Over path:** after archive POST succeeds, active GET returns 404 → modal `autoStart` triggers `createSession()` (existing effect).

⚠️ **Decision:** Local `IntakeResumeDialog` instead of extending `UserPrompt` — need two affirmative actions (**Continue** / **Start Over**) plus overlay dismiss; `useUserConfirm` is boolean-only and would conflate **Start Over** with **Cancel**.

⚠️ **Decision:** Skip **Start Intake** materials confirm when an active session exists — user already started intake; materials are on the candidate record.

⚠️ **Decision:** Do **not** change `IntakeChatModal.handleNewSession` (post-build **New intake session** button) in this ticket — UAT scope is **nav entry** only; that button remains create-without-archive until a follow-on if Susan wants parity.

9. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 2: Vitest regressions (§6c routed page)

**Done when:** New tests in `test_CandidateIntake.test.tsx` pass via:

```bash
cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

1. Extend `IntakeMockState` in `test_CandidateIntake.test.tsx`:

   ```typescript
   type IntakeMockState = {
     // ...existing fields...
     archiveCalls?: number
   }
   ```

2. In `installIntakeMocks`, initialize `let archiveCalls = state.archiveCalls ?? 0` (use a counter incremented on archive POST). Add handler **before** the `throw new Error(unexpected…)` fallback:

   ```typescript
   if (
     url === `/api/candidates/${candidateId}/intake/sessions/active/archive` &&
     init?.method === "POST"
   ) {
     archiveCalls += 1
     active = null
     return jsonResponse({
       archived_session_id: "sess-archived",
       archived_at: "2026-06-05 12:00:00",
       intakes_old_count: 1,
     })
   }
   ```

   Return `{ archiveCalls, getArchiveCalls: () => archiveCalls, …existing returns }`.

3. Add constant near page describe block:

   ```typescript
   const RESUME_DIALOG_NAME = "Resume Intake"
   ```

4. Add test **`shows resume dialog when active session exists (not Start Intake confirm)`** in `describe("CandidateIntake page")`:

   - `installIntakeMocks({ activeSession: sessionDto({ transcript: [transcriptEntry("assistant", "Prior thread", "initiate_candidate")] }) })`.
   - `localStorage.setItem("astral_selected_candidate", candidateId)`.
   - `renderWithProviders(<CandidateIntake />, { router: { initialEntries: ["/candidate/intake"] } })`.
   - `await screen.findByRole("alertdialog", { name: RESUME_DIALOG_NAME })`.
   - `expect(screen.getByText(/Would you like to continue your intake/i)).toBeInTheDocument()`.
   - `expect(screen.queryByRole("alertdialog", { name: "Start Intake" })).not.toBeInTheDocument()`.
   - `expect(screen.queryByRole("heading", { name: "Candidate Intake" })).not.toBeInTheDocument()`.

5. Add test **`Continue resumes active session without archive or session create`**:

   - Same mock with active session + prior assistant message.
   - Open resume dialog → click **Continue** (`getByRole("button", { name: "Continue" })` within dialog).
   - `await waitFor` modal heading **Candidate Intake** + text **Prior thread**.
   - Assert `getArchiveCalls() === 0` and `sessionCreateBodies.length === 0`.

6. Add test **`Start Over archives then auto-starts fresh session`**:

   - Same active-session mock.
   - Click **Start Over** in resume dialog.
   - `await waitFor` → `getArchiveCalls() === 1`, `sessionCreateBodies.length === 1`, visible **Estelle welcomes you.** (fresh create mock response).
   - Assert prior **Prior thread** is **not** in document after start-over completes.

7. Add test **`dismiss resume dialog does not open modal`**:

   - Active session mock.
   - `findByRole("alertdialog", { name: RESUME_DIALOG_NAME })`.
   - Click overlay: `userEvent.click(screen.getByRole("presentation"))` (the `modal-overlay` with `role="presentation"`).
   - `await waitFor` → no **Candidate Intake** heading, no resume dialog.

8. Regression: existing tests **`shows Start Intake confirm before modal`**, **`does not open modal when confirm is cancelled`**, **`redirects away when resume text is missing`** must still pass unchanged (no-active-session path).

---

## Self-Assessment

**Scope:** `Single-Component` — `CandidateIntake.tsx` page entry + Vitest in `test_CandidateIntake.test.tsx` only; no API/core changes.

**Conf:** `high` — **AST-582** archive route and `IntakeChatModal` resume/auto-start already ship on parent `ftr/`; this ticket adds one gate dialog and wires archive before modal open.

**Risk:** `Medium` — Wrong branching could skip archive on Start Over (duplicate ACTIVE rows) or show the wrong confirm when resuming; mitigated by explicit active GET before dialog and Vitest asserting archive/create call counts.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `IntakeChatModal` resume/create; local dialog copies `UserPrompt` markup only — no duplicate session logic. |
| §2.1 config | No new config keys; archive URL matches existing REST prefix. |
| §2.4 batch | N/A |
| §2.6 state machine | Candidate state machine untouched; intake session lifecycle delegated to **AST-582** archive + existing create. |
| §3.3 imports | Page → `api`, contexts, components only — no UI→data bend. |
| §3.5 naming | Page flat in `pages/`; tests in `test_CandidateIntake.test.tsx` per §6c. |

No conflicts — safe to implement as written.

---

## Review (build)

**Branch:** `origin/sub/AST-539/AST-583-intake-continue-vs-start-over`  
**Tip:** `57f25ba7`  
**Built:** Stage 1 only — `CandidateIntake.tsx` active-session gate, `IntakeResumeDialog`, Continue / Start Over / dismiss wiring. Stage 2 Vitest regressions deferred to Betty per build-astral test-tree ban.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-539/AST-583-intake-continue-vs-start-over` (tip `5ac9b230`)  
**Reviewed:** 2026-06-05

### What's solid

- **Plan fidelity:** Page entry probes `GET …/sessions/active` after materials load; **200** → resume dialog (skips Start Intake confirm); **404** → existing confirm path; non-404 errors toast + profile redirect. Matches UAT repro and plan Stage 1.
- **Continue / Start Over wiring:** Continue opens modal only (no archive/create — delegated to `IntakeChatModal` resume). Start Over `POST …/sessions/active/archive` then opens modal with `autoStart` so fresh session create runs after archive clears active. Error path toast + profile is bounded.
- **Tests:** Vitest covers dialog visibility, Continue (0 archive / 0 create + prior thread), Start Over (1 archive / 1 create + fresh welcome), overlay dismiss (no modal). Archive mock in `installIntakeMocks` matches **AST-582** response shape.
- **§3.3 / §3.5:** UI-only change; page flat in `pages/`; tests in `test_CandidateIntake.test.tsx` per §6c. No backend or debug-contract surface.
- **Self-Assessment alignment:** `scope-Single-Component` footprint matches diff (page + tests + bible row). No sibling-scope smuggle.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| advisory | `CandidateIntake.tsx` `IntakeResumeDialog` | Markup mirrors `UserPrompt` but renders inline (no `createPortal`). `position: fixed` overlay should cover viewport; if UAT sees stacking/clipping under nav, portal to `document.body` like `UserPromptProvider`. |
| advisory | `CandidateIntake.tsx` | Redundant second `GET …/sessions/active` when modal opens after page already probed active — harmless, not worth a follow-up unless latency matters. |

No **fix-now** or **discuss** items.

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| Proceed to `resolve-astral` (or UAT merge) | Katherine | No engineer fixes required from this review. |
| Portal dialog if UAT reports overlay clipping | Katherine | Optional polish only. |

---

## Resolution

**Resolved:** 2026-06-05  
**Publish ref:** `origin/sub/AST-539/AST-583-intake-continue-vs-start-over`

Radia review had no fix-now items. Shipped UI matches plan: active session → resume dialog; Continue resumes; Start Over archives via AST-582 API then fresh auto-start; dismiss returns to Profile. §9a dry-run clean into `origin/dev` and `origin/ftr/ast-539-candidate-intake-chat-session`.
