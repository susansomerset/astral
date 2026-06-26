<!-- linear-archive: AST-584 archived 2026-06-23 -->

## Linear archive (AST-584)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-584/uat-start-over-opens-fresh-initiate-in-modal-not-close-to-profile  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-539 — Candidate Intake Chat Session  
**Blocked by / blocks / related:** parent: AST-539

### Description

## Repro (Susan UAT AST-539 @ `b7886c0d`)

**Start Over** on resume dialog closes/navigates like **Close Window** instead of staying in intake flow.

## Expected

1. Archive current session to `candidate_data.intakes_old` (AST-582 API).
2. Intake **modal opens** with working/hold message.
3. New `initiate_candidate` assembled and sent; Estelle fresh opener appears in thread.

## Fix scope

`CandidateIntake.tsx` Start Over handler + `IntakeChatModal` auto-start after archive. Vitest regressions.

Parent: AST-539.

### Comments

#### betty — 2026-06-06T01:14:00.906Z
Correction: bible shasum on publish ref is `c53cffc892f3baff8edc59b0817dcd6ed8ad0401` (not `7b787ebf…` — pre-fetch typo).

#### betty — 2026-06-06T01:13:56.461Z
## QA test manifest

**Publish ref:** `origin/sub/AST-539/AST-584-start-over-fresh-initiate-in-modal` @ `07b22c81`

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `7b787ebf27798840332b0eb7dbf2003ce74c670f` (§7.13zr **AST-584** row)

### Manifest (run in order)

1. **Typecheck**
   ```bash
   cd src/ui/frontend && npx tsc -b --noEmit
   ```

2. **Vitest — routed page + modal regressions (§6c + §7.13zr AST-584)**
   ```bash
   cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx
   ```

### New / updated coverage (AST-584)

| # | Test | Asserts |
| --- | --- | --- |
| 1 | `Start Over archive failure keeps resume dialog and does not open modal` | Archive 500 → resume dialog stays; no Candidate Intake modal |
| 2 | `Start Over treats archive 404 as success and opens fresh session` | Archive 404 + active cleared → fresh Estelle opener; no prior thread |
| 3 | `Start Over shows hold copy while initiate runs` | `HOLD_COPY` visible during delayed session POST |
| 4 | `IntakeChatModal freshStart ignores stale active GET and creates session` | `freshStart` + stale active mock → POST create; Prior thread absent |
| 5 | Existing `Start Over archives then auto-starts fresh session` | Regression — archive + create + fresh transcript |

### Existing bible-backed (same file — regression)

- **AST-583** resume dialog: Continue / Start Over / dismiss
- **AST-559** confirm gate, auto-start, build-once
- **AST-578** transcript filter, hold on empty / assistant-less resume

No pytest manifest — UI-only ticket.

— Betty

#### katherine — 2026-06-05T23:21:08.854Z
Plan: [`docs/features/candidate/ast-584-uat-start-over-opens-fresh-initiate-in-modal-not-close-to-profile.md`](https://github.com/susansomerset/astral/blob/sub/AST-539/AST-584-start-over-fresh-initiate-in-modal/docs/features/candidate/ast-584-uat-start-over-opens-fresh-initiate-in-modal-not-close-to-profile.md) on `origin/sub/AST-539/AST-584-start-over-fresh-initiate-in-modal` @ `2bbb3e05`.

**Root cause (planned fix):** `handleResumeStartOver` catch calls `goProfile()` — same navigation as overlay dismiss when archive fails or returns unexpected status. Secondary: `IntakeChatModal` `autoStart` skips `createSession` when stale `GET …/active` still returns 200 after archive.

**Scope:** `Single-Component` — `CandidateIntake.tsx` error path + `freshStart`/`startOverBusy`; `IntakeChatModal.tsx` force create after archive; Vitest regressions.

**Conf:** `high` — matches Susan’s repro @ `b7886c0d`; extends **AST-583** wiring with explicit failure-mode handling.

**Risk:** `Medium` — must not break **Continue** resume path; guarded by `freshStartMode` only on Start Over and call-count tests.

---

# AST-584 — UAT: Start Over opens fresh initiate in modal (not close to Profile)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-584/uat-start-over-opens-fresh-initiate-in-modal-not-close-to-profile  
**Parent:** https://linear.app/astralcareermatch/issue/AST-539/candidate-intake-chat-session  
**Publish ref:** `sub/AST-539/AST-584-start-over-fresh-initiate-in-modal` (origin only)

Susan UAT 2026-06-05 on **AST-539** @ `b7886c0d`: **Start Over** on the resume dialog navigates to Profile like overlay dismiss / **Close Window**, instead of archiving the active session and opening **IntakeChatModal** with hold copy plus a fresh `initiate_candidate` turn. **AST-583** wired the dialog and happy-path mocks pass; this ticket fixes production failure modes in the Start Over handler and modal auto-start after archive.

**Dependency:** **AST-582** archive API (`POST …/sessions/active/archive`) must be on the UAT tree (rolled on `origin/ftr/ast-539-candidate-intake-chat-session`). **Out of scope:** **AST-585** (in-flight initiate after modal close).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | Start Over: no `goProfile` on archive failure; treat archive 404 as cleared; `startOverBusy`; pass `freshStart` + remount `key` | ui |
| `src/ui/frontend/src/components/IntakeChatModal.tsx` | `freshStart` prop — force `createSession` after archive even if stale active GET | ui |
| `tests/component/frontend/pages/test_CandidateIntake.test.tsx` | Vitest: archive error stays on page; freshStart forces create; hold then Estelle opener | ui |

**Out of scope:** `src/core/intake.py`, `src/ui/api/api_intake.py`, `App.css`, **AST-585**.

---

## Stage 1: CandidateIntake — Start Over must not mimic dismiss

**Done when:** Clicking **Start Over** never navigates to Profile on archive failure; successful or idempotent archive opens intake modal on `/candidate/intake`; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/pages/CandidateIntake.tsx`, add state:

   ```typescript
   const [startOverBusy, setStartOverBusy] = useState(false)
   const [freshStartKey, setFreshStartKey] = useState(0)
   const [freshStartMode, setFreshStartMode] = useState(false)
   ```

2. Extend `IntakeResumeDialogProps` and `IntakeResumeDialog` with optional `busy?: boolean`. When `busy` is true:
   - Set `aria-busy="true"` on the alertdialog card.
   - Disable all three actions (`Start Over`, `Continue`, overlay dismiss via `onDismiss` guard — overlay `onClick` calls `onDismiss` only when `!busy`).
   - Footer buttons: `disabled={busy}`.

3. Replace `handleResumeStartOver` with:

   ```typescript
   const handleResumeStartOver = useCallback(async () => {
     if (!selectedId || startOverBusy) return
     setStartOverBusy(true)
     try {
       const r = await api(
         `/api/candidates/${selectedId}/intake/sessions/active/archive`,
         { method: "POST" },
       )
       if (!r.ok && r.status !== 404) {
         const e = await r.json().catch(() => ({}))
         throw new Error((e as { error?: string }).error ?? "Failed to archive intake session")
       }
       // 200 = archived; 404 = already no active session — both OK for fresh start
       const activeCheck = await api(`/api/candidates/${selectedId}/intake/sessions/active`)
       if (activeCheck.ok) {
         throw new Error("Active intake session still present after archive")
       }
       if (activeCheck.status !== 404) {
         throw new Error("Failed to verify intake session cleared")
       }
       setFreshStartMode(true)
       setFreshStartKey(k => k + 1)
       openModalAfterResumeChoice()
     } catch (e) {
       setToast({
         text: e instanceof Error ? e.message : "Failed to start over",
         variant: "error",
       })
       // Keep resume dialog open — do NOT goProfile (Susan: must stay in intake flow)
     } finally {
       setStartOverBusy(false)
     }
   }, [selectedId, startOverBusy, openModalAfterResumeChoice])
   ```

4. In `handleResumeContinue`, before `openModalAfterResumeChoice()`, set `setFreshStartMode(false)` so Continue keeps resume behavior.

5. Pass `busy={startOverBusy}` into `IntakeResumeDialog`.

6. Update `IntakeChatModal` render block:

   ```tsx
   {modalOpen && (
     <IntakeChatModal
       key={freshStartKey}
       open
       autoStart
       freshStart={freshStartMode}
       onClose={goProfile}
       candidateId={selectedId}
       materials={materials}
     />
   )}
   ```

⚠️ **Decision:** Archive POST **404** (`no active intake session`) is treated as success — page already showed resume dialog because GET active was 200; race or double-click must still open fresh modal, not error-navigate to Profile.

⚠️ **Decision:** Remove `goProfile()` from Start Over **catch** — only overlay dismiss and explicit modal **Close/Cancel** navigate to Profile. Matches Susan’s “stay in intake flow” vs **Close Window**.

7. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 2: IntakeChatModal — force fresh create after Start Over

**Done when:** With `freshStart={true}` and `autoStart`, modal shows hold copy, POSTs `…/sessions` once, and first visible assistant bubble is Estelle’s new opener (not prior thread).

1. In `src/ui/frontend/src/components/IntakeChatModal.tsx`, extend `IntakeChatModalProps`:

   ```typescript
   /** After parent archived active session — always POST create; do not resume stale active GET. */
   freshStart?: boolean
   ```

   Default `freshStart = false` in destructuring.

2. Replace the auto-start `useEffect` (lines ~152–164) guard with:

   ```typescript
   useEffect(() => {
     if (!open || !activeLoaded || !autoStart || autoStartAttempted.current) return
     if (hasSession && !freshStart) return
     autoStartAttempted.current = true
     setStarting(true)
     setBusy(true)
     createSession()
       .then(dto => applySessionDto(dto, setSessionId, setMessages, setReadyToBuild, setBuildCompleted))
       .catch(e => setToast({ text: e instanceof Error ? e.message : "Start failed", variant: "error" }))
       .finally(() => {
         setStarting(false)
         setBusy(false)
       })
   }, [open, activeLoaded, autoStart, freshStart, hasSession, createSession])
   ```

3. When `freshStart` is true and `loadActiveSession` returned 200 (stale row), **do not** call `applySessionDto` for resume — clear session display before create:

   In `loadActiveSession` `.then` block, after parsing body on 200 response, add:

   ```typescript
   if (freshStart) {
     setSessionId(null)
     setMessages([])
     setReadyToBuild(false)
     setBuildCompleted(false)
     return
   }
   ```

   Pass `freshStart` into the `loadActiveSession` useCallback dependency array.

⚠️ **Decision:** `freshStart` clears stale UI state but still relies on parent’s archive + active 404 check; modal create runs even if a stale GET slipped through (backend may briefly return old ACTIVE — create adds new session row per existing **AST-582** advisory).

4. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 3: Vitest regressions

**Done when:** New/updated tests pass:

```bash
cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

1. Update existing **`Start Over archives then auto-starts fresh session`** to pass `freshStart` through render (implicit via page — no change if page sets `freshStartMode`).

2. Add **`Start Over archive failure keeps resume dialog and does not navigate`**:
   - Mock archive POST → `{ ok: false, status: 500 }`.
   - Click **Start Over**.
   - Assert resume dialog still visible (`RESUME_DIALOG_NAME`).
   - Assert `navigate` mock (if available via router) was **not** called with `/candidate/profile` — use `renderWithProviders` router initial `/candidate/intake` and assert document still on intake route or dialog present after error toast.

3. Add **`Start Over treats archive 404 as success and opens fresh session`**:
   - Mock archive POST → 404 `{ error: "no active intake session" }`.
   - Active GET after archive → 404.
   - Session POST → new Estelle welcome.
   - Assert modal heading **Candidate Intake** and **Estelle welcomes you.** visible.

4. Add **`IntakeChatModal freshStart ignores stale active GET and creates session`** in `describe("IntakeChatModal")`:
   - `installIntakeMocks` with `activeSession` containing **Prior thread**.
   - Render `<IntakeChatModal open autoStart freshStart … />`.
   - Assert `sessionCreateBodies.length === 1` and **Prior thread** not in document; **Estelle welcomes you.** appears.

5. Add **`Start Over shows hold copy while initiate runs`** (page-level):
   - Delay session POST resolve in mock (or leave pending until assert hold).
   - After Start Over, assert `HOLD_COPY` visible before Estelle message.

---

## Self-Assessment

**Scope:** `Single-Component` — Two React files (`CandidateIntake.tsx`, `IntakeChatModal.tsx`) plus Vitest; no backend or config changes.

**Conf:** `high` — Susan’s repro matches `handleResumeStartOver` error path calling `goProfile()` and `autoStart` skipping when stale active GET returns 200; fixes follow **AST-583** patterns and existing modal props.

**Risk:** `Medium` — Wrong guard could regress **Continue** (resume without create) or allow double-create; mitigated by `freshStartMode` only set on Start Over path and Vitest call-count assertions.

---

## ASTRAL_CODE_RULES self-review

| Rule | Applicability |
|------|----------------|
| §1.3 DRY | Reuses existing `api()`, `IntakeChatModal` create path — no duplicate archive logic in modal. |
| §2.1 config | No new config keys; intake statuses remain in `INTAKE_CONFIG`. |
| §3.3 imports | UI-only; imports stay within `src/ui/frontend`. |
| §3.5 naming | Page in `pages/`, component in `components/` — no new folders. |
| §3.6 debug | No spike output. |

No conflicts requiring plan revision.

---

## Review (build)

**Built:** `origin/sub/AST-539/AST-584-start-over-fresh-initiate-in-modal` @ `83d83369`

**Product:** `CandidateIntake.tsx` — Start Over no longer calls `goProfile` on archive failure; treats archive 404 as success; `startOverBusy` + `freshStartMode`/`freshStartKey`. `IntakeChatModal.tsx` — `freshStart` prop clears stale active GET and forces `createSession` on auto-start.

**Out of build scope (Betty / qa-astral):** Plan Stage 3 Vitest regressions per `build-astral` test-tree ban.
