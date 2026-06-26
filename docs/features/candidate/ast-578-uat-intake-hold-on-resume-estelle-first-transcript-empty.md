<!-- linear-archive: AST-578 archived 2026-06-23 -->

## Linear archive (AST-578)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-578/uat-intake-hold-on-resume-estelle-first-transcript-empty-active  
**Status at archive:** Done  
**Project:** Astral Candidate (inherited from AST-539)  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-539 — Candidate Intake Chat Session  
**Blocked by / blocks / related:** parent: AST-539

### Description

## Repro (Susan UAT AST-539 @ `5b96f9db`)

1. Reopen Intake when active session exists — no hold message; blank thread if transcript empty.
2. First visible chat bubble is synthetic RESUME user payload, not Estelle intro.

## Expected

* Hold copy while loading / re-initiating when active session lacks assistant message.
* Thread display hides `user` + `mode=initiate_candidate` entries; Estelle `assistant_message` is first visible bubble.

## Files

* `src/ui/frontend/src/components/IntakeChatModal.tsx`
* `tests/component/frontend/pages/test_CandidateIntake.test.tsx`

Parent: AST-539. Feature child AST-559 stays User Testing — fix via Bug workflow.

### Comments

#### radia — 2026-06-05T19:18:46.663Z
**Review** (`origin/dev...origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty` @ `b3f3d2f2`; product delta `cc691b93` + `b3f3d2f2`)

**No fix-now.** Plan stages 1–2 delivered: `isHiddenTranscriptEntry`, filtered `transcriptToMessages`, `showHold = !activeLoaded || starting || (hasSession && messages.length === 0)`; Vitest regressions for hidden RESUME row, hold on empty/assistant-less resume, hold clears when assistant exists. §3.3 clean for AST-578 delta (frontend-only).

**Advisory:** Three-dot diff vs `origin/dev` includes rolled-up AST-558/559/539 parent + prep-uat harness; ticket `scope-minor` still matches AST-578 commits. `INTAKE_HOLD_COPY` inline UX string — not a §3.2 state-list violation.

**Doc:** [ast-578 plan + review](https://github.com/susansomerset/astral/blob/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty/docs/features/candidate/ast-578-uat-intake-hold-on-resume-estelle-first-transcript-empty.md) @ `18afd1f6`

Katherine: `resolve-astral` — no code fixes required.

#### betty — 2026-06-05T19:10:07.715Z
**Status handoff:** Betty QA complete — please move to **Tests Ready** (assignee **Katherine**) if still **Code Complete**. MCP `save_issue` state update failed in this session.

**Ready for `test-astral`** on `origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty` @ `b3f3d2f2`.

#### betty — 2026-06-05T19:09:12.140Z
**Manifest** (`origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty` @ `b3f3d2f2`)

1. `cd src/ui/frontend && npx tsc -b --noEmit`
2. `cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx`

**Coverage (§7.13zr AST-578 row):** `IntakeChatModal` — hides `user` + `mode=initiate_candidate` transcript rows; shows `INTAKE_HOLD_COPY` while loading / when active session has no visible assistant message; hold clears once assistant bubble exists (`resumes active session` regression).

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `e5995ccb62dbc378119b109c9c5f6181dd2b14e59646cec8626e630ee763b350`

**Regression (optional, same epic):** §7.13zr **AST-558** pytest narrowed run if intake API touched in same pass.

#### katherine — 2026-06-05T19:05:38.001Z
Plan: [`docs/features/candidate/ast-578-uat-intake-hold-on-resume-estelle-first-transcript-empty.md`](https://github.com/susansomerset/astral/blob/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty/docs/features/candidate/ast-578-uat-intake-hold-on-resume-estelle-first-transcript-empty.md) on `origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty` @ `817a8378`.

Two-stage minimal UAT fix: (1) filter `user` + `mode=initiate_candidate` from thread display and broaden `showHold` to cover `!activeLoaded`, `starting`, or active session with zero visible assistant rows; (2) three Vitest regressions + tighten resume test. No backend changes.

**Self-assessment**
- **Scope:** `minor` — `IntakeChatModal.tsx` + existing page test file only.
- **Conf:** `high` — repro matches unfiltered `transcriptToMessages` and `showHold = starting && messages.length === 0` in shipped AST-559 code.
- **Risk:** `low` — display-only; API and composer paths untouched.

---

# UAT: Intake hold on resume, Estelle-first transcript, empty active session

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-578/uat-intake-hold-on-resume-estelle-first-transcript-empty-active  
**Parent:** https://linear.app/astralcareermatch/issue/AST-539/candidate-intake-chat-session

**Publish ref (origin):** `sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty`  
**Parent integration ref:** `ftr/ast-539-candidate-intake-chat-session`

Susan UAT bug on **AST-539** @ `5b96f9db`: reopening Intake with an active session shows a blank thread (no hold copy) when the transcript is empty or lacks an assistant turn, and the first visible bubble is the synthetic `initiate_candidate` user payload (`RESUME:…`) instead of Estelle's `assistant_message`. Fix display-only logic in `IntakeChatModal` — no backend or API changes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/IntakeChatModal.tsx` | Filter hidden transcript entries; broaden hold visibility | ui |
| `tests/component/frontend/pages/test_CandidateIntake.test.tsx` | Vitest regressions for hold + transcript filtering | ui |

**Not in scope:** `src/core/intake.py`, `src/ui/api/*`, `App.css` (`.intake-hold` already exists), **AST-559** sibling (stays User Testing).

---

## Stage 1: Transcript filtering and hold logic

**Done when:** `IntakeChatModal` hides `user` + `mode=initiate_candidate` entries from the thread, shows `INTAKE_HOLD_COPY` while loading or when an active session has no visible assistant message, and `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/components/IntakeChatModal.tsx`, add a module-level helper **above** `transcriptToMessages`:

   ```typescript
   function isHiddenTranscriptEntry(entry: IntakeTranscriptEntry): boolean {
     return entry.role === "user" && entry.mode === "initiate_candidate"
   }
   ```

2. Change `transcriptToMessages` to map only visible entries:

   ```typescript
   function transcriptToMessages(transcript: IntakeTranscriptEntry[]): IntakeChatMessage[] {
     return transcript
       .filter(entry => !isHiddenTranscriptEntry(entry))
       .map(entry => ({
         role: entry.role,
         content: entry.text,
         mode: entry.mode,
       }))
   }
   ```

3. Replace the `showHold` line (currently `const showHold = starting && messages.length === 0`) with:

   ```typescript
   const showHold =
     !activeLoaded || starting || (hasSession && messages.length === 0)
   ```

   `messages` is already the filtered visible list from `applySessionDto` → `transcriptToMessages`. No other state changes.

4. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Hold when `hasSession && messages.length === 0` covers resume with empty transcript or transcript containing only the hidden `initiate_candidate` user row (awaiting / re-awaiting Estelle). Do not show hold when `!hasSession` and not loading/starting — empty thread is correct before auto-start kicks in.

---

## Stage 2: Component test regressions

**Done when:** New/updated Vitest cases in `test_CandidateIntake.test.tsx` pass via `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx`.

1. In `tests/component/frontend/pages/test_CandidateIntake.test.tsx`, add constant near `defaultMaterials`:

   ```typescript
   const HOLD_COPY = "One moment while we review your details before we begin…"
   const INITIATE_USER_TEXT = "RESUME:\nSenior engineer resume body\n\nCOVER LETTER SAMPLE: cover optional\n\nLINKEDIN: (none)"
   ```

2. Add test **`hides initiate_candidate user payload; first bubble is assistant`** inside `describe("IntakeChatModal")`:

   - `installIntakeMocks` with `activeSession: sessionDto({ transcript: [ transcriptEntry("user", INITIATE_USER_TEXT, "initiate_candidate"), transcriptEntry("assistant", "Estelle intro here", "initiate_candidate") ] })`.
   - Render modal `open`, `candidateId`, `materials`, `onClose` (no `autoStart`).
   - `await waitFor(() => expect(screen.getByText("Estelle intro here")).toBeInTheDocument())`.
   - `expect(screen.queryByText(/RESUME:/)).not.toBeInTheDocument()`.
   - `expect(screen.queryByText(HOLD_COPY)).not.toBeInTheDocument()`.

3. Add test **`shows hold when active session has no assistant message`**:

   - `activeSession: sessionDto({ transcript: [ transcriptEntry("user", INITIATE_USER_TEXT, "initiate_candidate") ] })` (assistant row absent).
   - After load: `expect(screen.getByText(HOLD_COPY)).toBeInTheDocument()`.
   - `expect(screen.queryByText(/RESUME:/)).not.toBeInTheDocument()`.

4. Add test **`shows hold when active session transcript is empty`**:

   - `activeSession: sessionDto({ transcript: [] })`.
   - After load: `expect(screen.getByText(HOLD_COPY)).toBeInTheDocument()`.

5. Update existing test **`resumes active session on open without auto-start POST`** — add assertion that `HOLD_COPY` is not shown once `Prior thread` is visible (confirms hold clears when assistant exists).

6. Run `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx`.

---

## Self-Assessment

**Scope:** `minor` — Two frontend files only; display filter + hold predicate in one component.

**Conf:** `high` — Root cause is clear in current `showHold` and unfiltered `transcriptToMessages`; matches AST-558 transcript shape from `src/core/intake.py`.

**Risk:** `low` — Wrong hold/filter only affects Intake modal rendering; composer and API paths unchanged.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Helper `isHiddenTranscriptEntry` keeps filter in one place |
| §1.4 Hardcoded sets | No new enums; reuses existing `IntakeTurnMode` |
| §2.1 Config | No nav/config changes |
| §3.3 Imports | No new cross-layer imports |
| §3.5 Naming | Stays in `components/IntakeChatModal.tsx`; tests in existing page test file |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty`  
**Tip:** `cc691b93`  
**Built by:** Katherine (`build-astral`)  
**Status:** Stage 1 delivered — `IntakeChatModal` transcript filter + hold predicate. Stage 2 Vitest regressions await `qa-astral` / Betty.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty` @ `b3f3d2f2`  
**Reviewer:** Radia (`review-astral`)  
**AST-578 delta:** `cc691b93` (feat) + `b3f3d2f2` (test)

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | Stage 1–2 match approved plan: `isHiddenTranscriptEntry`, filtered `transcriptToMessages`, `showHold = !activeLoaded \|\| starting \|\| (hasSession && messages.length === 0)` |
| UAT repro | Hidden `user` + `initiate_candidate` rows; hold while loading, starting, or active session with no visible assistant bubble |
| Tests | Vitest cases for filter, hold on assistant-less transcript, hold on empty transcript, and hold cleared when assistant exists |
| §1.3 DRY | Single helper owns hide predicate |
| §3.3 layers | AST-578 product touch is frontend-only; no new cross-layer imports |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | No fix-now or discuss items |

### Recommended actions

| Action | Owner |
|--------|-------|
| No product changes required for AST-578 | Katherine — `resolve-astral` may proceed to close review (no fix-now) |
| Re-run Susan UAT on AST-539 intake reopen paths | Susan |

### Advisory

- **Publish-ref anatomy:** Three-dot diff vs `origin/dev` includes rolled-up **AST-558/559/539** parent work and prep-uat harness edits; ticket scope (`scope-minor`, two UI files) still matches the AST-578 commit range.
- **`INTAKE_HOLD_COPY`:** Inline UX string in the component — not a config state list; acceptable per §3.2.

---

## Resolution

**Date:** 2026-06-05  
**Engineer:** Katherine (`resolve-astral`)  
**Publish ref:** `origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty` @ `18afd1f6`

Radia review (**Review Posted** → **User Testing**): no fix-now or discuss items. Product delta (`cc691b93` feat + `b3f3d2f2` test) already on publish ref; no additional code changes in this resolve pass. Radia plan-doc review section merged via sub ref (`18afd1f6`). §9a dry-run: publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-539-candidate-intake-chat-session`.
