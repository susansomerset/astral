# AST-585 — UAT: Complete in-flight initiate after modal close

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-585/uat-complete-in-flight-initiate-after-modal-close  
**Parent:** https://linear.app/astralcareermatch/issue/AST-539/candidate-intake-chat-session

**Publish ref (origin):** `sub/AST-539/AST-585-inflight-initiate-persist-after-close`  
**Parent integration ref:** `ftr/ast-539-candidate-intake-chat-session`

Susan UAT on **AST-539** @ `b7886c0d`: closing the Intake modal while **`POST …/sessions`** (initiate) or **`POST …/turns`** (candidate response) is still in flight leaves an active session with no Estelle reply; **Continue** reopens a blank thread. **AST-578** hold copy appears but never resolves because nothing polls and the synchronous Flask handler may not finish after the client disconnects. Fix: run intake model work in daemon background threads that survive HTTP teardown, return the session DTO as soon as the row is durable, guard duplicate session creates, and poll **`GET …/sessions/active`** from **`IntakeChatModal`** until an assistant message exists — without aborting in-flight fetches on unmount.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `INTAKE_CONFIG` keys: poll interval, initiate-failure user copy | utils |
| `src/core/intake.py` | Background initiate/turn completion; `awaiting_agent` on DTO; duplicate-active guard | core |
| `src/ui/api/api_intake.py` | Map duplicate-active to **409**; unchanged route shapes | ui |
| `src/ui/frontend/src/components/IntakeChatModal.tsx` | `mountedRef` guards; session poll; never abort fetch on unmount | ui |
| `tests/component/core/test_intake.py` | Background initiate/turn + duplicate guard + `awaiting_agent` | tests |
| `tests/component/ui/api/test_api_intake.py` | **409** on duplicate create; create returns before assistant | tests |
| `tests/component/frontend/pages/test_CandidateIntake.test.tsx` | Poll + unmount-safe create Vitest regressions | tests |

**Out of scope:** `CandidateIntake.tsx` (resume dialog already correct per **AST-583**), `src/data/database.py` schema changes, new REST routes, build/turn UX beyond polling for assistant completion.

---

## Stage 1: Config and core — background initiate + turn

**Done when:** `POST /sessions` returns **201** with an **ACTIVE** row and `awaiting_agent: true` before Estelle finishes; initiate and turn model calls complete in daemon threads and persist transcript even if the HTTP client disconnects; duplicate create while an **ACTIVE** session exists raises **409**; `cd src/ui/frontend && npx tsc -b --noEmit` not required this stage; `python -m pytest tests/component/core/test_intake.py -q` passes for updated cases.

1. In `src/utils/config.py`, inside `INTAKE_CONFIG`, add after `"session_status_archived"`:

   ```python
   "initiate_poll_interval_ms": 3000,
   "initiate_failure_message": (
       "We could not start the interview. Close Intake and use Start Over to try again."
   ),
   ```

2. In `src/core/intake.py`, add module imports at top (with existing imports): `import asyncio`, `import threading`.

3. In `src/core/intake.py`, add helper **above** `get_intake_session_dto`:

   ```python
   def _transcript_has_assistant(transcript: list) -> bool:
       return any((e or {}).get("role") == "assistant" for e in (transcript or []))

   def _session_awaiting_agent(transcript: list) -> bool:
       t = transcript or []
       if not _transcript_has_assistant(t):
           return True
       return (t[-1] or {}).get("role") == "user"
   ```

4. In `get_intake_session_dto`, extend `out` dict (after `build_completed`):

   ```python
   out["awaiting_agent"] = (
       status == INTAKE_CONFIG["session_status_active"]
       and _session_awaiting_agent(row.get("transcript") or [])
   )
   ```

5. In `src/core/intake.py`, extract initiate completion from `create_intake_session_and_start` into new async function `_complete_initiate_turn` placed **immediately above** `create_intake_session_and_start`:

   - Parameters: `intake_session_id: str`, `candidate_id: str`, `initiate_payload: str`, `*, debug: bool = False`.
   - Body: copy lines from current `create_intake_session_and_start` starting at `run = await _run_intake_task(... intake_initiate_candidate ...)` through `database.update_intake_session(...)` and `row = database.get_intake_session(...)` — **do not** return a DTO; return `None` on success.
   - On `not run["success"]`: call `database.update_intake_session` on the existing row with `transcript` = single assistant entry `{"role": "assistant", "text": INTAKE_CONFIG["initiate_failure_message"], "ready_to_build": False}`, `prompt_snapshot` unchanged (`row.get("prompt_snapshot")`), `last_ready_to_build=False`, `status=INTAKE_CONFIG["session_status_active"]`, `built_at=None`. Do **not** re-raise.

6. In `src/core/intake.py`, add sync scheduler **above** `create_intake_session_and_start`:

   ```python
   def _schedule_intake_coroutine(coro_factory, *, label: str) -> None:
       def _worker() -> None:
           asyncio.run(coro_factory())

       threading.Thread(target=_worker, daemon=True, name=label).start()
   ```

7. Rewrite `create_intake_session_and_start`:

   - After `_persist_source_materials` and before model work: if `fetch_active_intake_session(candidate_id)` returns a row, raise `ValueError("active intake session already exists for candidate")`.
   - Keep `intake_session_id = str(uuid.uuid4())`, `database.create_intake_session(intake_session_id, candidate_id, transcript=[])`.
   - Build `initiate_payload` via `_format_initiate_payload(...)` as today.
   - Call `_schedule_intake_coroutine(lambda: _complete_initiate_turn(intake_session_id, candidate_id, initiate_payload, debug=debug), label=f"intake-initiate-{intake_session_id[:8]}")`.
   - Return `get_intake_session_dto(database.get_intake_session(intake_session_id))` — **no** `batch_id` on immediate response.

8. In `src/core/intake.py`, extract turn completion into async `_complete_turn_response` **above** `post_intake_turn`:

   - Parameters: `intake_session_id: str`, `candidate_id: str`, `message: str`, `transcript_with_user: list`, `prompt_snapshot`, `*, debug: bool = False`.
   - Run `_run_intake_task` for `intake_candidate_response` with `_live_content_for_turn("candidate_response", message, transcript_with_user)` and existing `prompt_snapshot`.
   - On success: validate turn, append assistant to `transcript_with_user`, update session (same fields as current `post_intake_turn` success path).
   - On failure: append assistant entry with `text` = `INTAKE_CONFIG["initiate_failure_message"]`, `ready_to_build=False`, update session; do **not** re-raise.

9. Rewrite `post_intake_turn`:

   - Keep validation through `transcript = _append_transcript(..., role="user", ...)`.
   - **Immediately** `database.update_intake_session(intake_session_id, transcript=transcript, prompt_snapshot=row.get("prompt_snapshot"), last_ready_to_build=bool(row.get("last_ready_to_build")), status=INTAKE_CONFIG["session_status_active"], built_at=None)` so the user line survives disconnect.
   - Schedule `_schedule_intake_coroutine(lambda: _complete_turn_response(intake_session_id, row["candidate_id"], message.strip(), transcript, row.get("prompt_snapshot"), debug=debug), label=f"intake-turn-{intake_session_id[:8]}")`.
   - Return `get_intake_session_dto(database.get_intake_session(intake_session_id))` — transcript includes user only; `awaiting_agent: true`.

⚠️ **Decision:** Daemon `threading.Thread` + `asyncio.run` in worker (same pattern as `api_admin.py` backfill) decouples model latency from Werkzeug request lifetime. Single-worker Gunicorn (`RAILWAY_CONFIG`) keeps one process; daemon threads are acceptable for intake UAT fix.

⚠️ **Decision:** Immediate **201**/**200** responses may omit `batch_id` until background work finishes; clients must use `awaiting_agent` + poll, not block on POST body containing Estelle text.

---

## Stage 2: API duplicate guard + IntakeChatModal poll / unmount safety

**Done when:** Duplicate session create returns **409**; modal polls active session every `INTAKE_CONFIG["initiate_poll_interval_ms"]` while `awaiting_agent`; async handlers skip `setState` after unmount but never pass `AbortSignal`; `cd src/ui/frontend && npx tsc -b --noEmit` passes.

1. In `src/ui/api/api_intake.py`, in `create_session`, extend the `except ValueError` branch: if `str(e) == "active intake session already exists for candidate"`, return `jsonify({"error": str(e)}), 409` before the generic **400** return.

2. In `src/ui/frontend/src/components/IntakeChatModal.tsx`, extend `IntakeSessionDto`:

   ```typescript
   awaiting_agent?: boolean
   ```

3. In `IntakeChatModal`, add refs after `autoStartAttempted`:

   ```typescript
   const mountedRef = useRef(true)
   const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
   ```

4. Add `useEffect` tied to `open`:

   ```typescript
   useEffect(() => {
     mountedRef.current = true
     return () => {
       mountedRef.current = false
       if (pollRef.current) {
         clearInterval(pollRef.current)
         pollRef.current = null
       }
     }
   }, [open])
   ```

5. Wrap every `applySessionDto`, `setToast`, `setBusy`, `setStarting`, `setDraft`, `setActiveLoaded` call inside async `.then` / `catch` / `finally` blocks with `if (!mountedRef.current) return` **before** the state update. Do **not** add `AbortController` or `signal` to any `api()` call.

6. Add `pollActiveSession` callback (after `loadActiveSession`):

   ```typescript
   const pollActiveSession = useCallback(() => {
     void api(`/api/candidates/${candidateId}/intake/sessions/active`)
       .then(async r => {
         if (!r.ok) return
         const body = (await r.json()) as IntakeSessionDto
         if (!mountedRef.current) return
         if (!body.awaiting_agent) {
           applySessionDto(body, setSessionId, setMessages, setReadyToBuild, setBuildCompleted)
         }
       })
       .catch(() => {})
   }, [candidateId])
   ```

7. Add `useEffect` after existing effects:

   ```typescript
   useEffect(() => {
     if (!open || !hasSession) return
     const dtoAwaiting =
       messages.length === 0 ||
       (messages.length > 0 && messages[messages.length - 1].role === "user")
     if (!dtoAwaiting) return
     pollActiveSession()
     pollRef.current = setInterval(pollActiveSession, 3000)
     return () => {
       if (pollRef.current) {
         clearInterval(pollRef.current)
         pollRef.current = null
       }
     }
   }, [open, hasSession, messages, pollActiveSession])
   ```

   Use literal `3000` (matches config default; frontend does not import `INTAKE_CONFIG`).

8. In `loadActiveSession` success path, after `applySessionDto`, if `body.awaiting_agent` is true, set `setStarting(false)` and `setBusy(false)` so hold shows without a stuck busy composer.

9. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Poll predicate mirrors `awaiting_agent` server flag but uses visible `messages` so hidden `initiate_candidate` user rows do not block poll stop.

---

## Stage 3: Tests — core, API, Vitest

**Done when:** `python -m pytest tests/component/core/test_intake.py tests/component/ui/api/test_api_intake.py -q` and `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx` pass.

1. In `tests/component/core/test_intake.py`:

   - Update `test_create_session_persists_source_materials`: after `await create_intake_session_and_start(...)`, assert immediate `dto["awaiting_agent"] is True`, `len(dto["transcript"]) == 0`, then `await asyncio.sleep(0.05)` (or poll `get_intake_session` in a short loop ≤2s) until `_transcript_has_assistant` on DB row; assert final transcript length **2** and `ready_to_build` false on assistant entry.
   - Add `test_create_session_rejects_duplicate_active` — create once, second call raises `ValueError` matching `"already exists"`.
   - Add `test_background_initiate_failure_writes_assistant_error` — mock `do_task` failure for initiate; wait for background; assert assistant text equals `INTAKE_CONFIG["initiate_failure_message"]`.
   - Update `test_turn_appends_transcript_and_propagates_ready_to_build` — after `post_intake_turn`, immediate DTO has user line and `awaiting_agent True`; wait for background; final DTO has assistant and `awaiting_agent False`.

2. In `tests/component/ui/api/test_api_intake.py`:

   - Update `test_create_session_201_shape` mock to return DTO with `awaiting_agent: True`, empty `transcript`.
   - Add `test_create_session_duplicate_active_409` — mock `create_intake_session_and_start` raising `ValueError("active intake session already exists for candidate")`; assert **409**.

3. In `tests/component/frontend/pages/test_CandidateIntake.test.tsx`:

   - Extend `IntakeSessionDto` usage in `sessionDto()` helper with `awaiting_agent: false` default; set `awaiting_agent: true` in hold fixtures.
   - Add test **`polls active session until assistant arrives after empty resume`** inside `describe("IntakeChatModal")`:
     - Mock `GET …/sessions/active` to return empty transcript + `awaiting_agent: true` on first two calls, then transcript with assistant + `awaiting_agent: false` on third.
     - Use `vi.useFakeTimers()`; render modal open without `autoStart`.
     - `await waitFor` hold copy; `vi.advanceTimersByTime(3000)` twice; `await waitFor` Estelle text; `vi.useRealTimers()`.
   - Add test **`unmount during autoStart does not prevent session create fetch`**:
     - Mock `POST …/sessions` with `new Promise` resolve delayed 100ms.
     - Render with `autoStart`, then `rerender` with `open={false}` before resolve.
     - `await waitFor` expect POST called once; expect no `AbortSignal` on init (optional: assert `init?.signal` undefined).

4. Run the pytest and vitest commands above.

---

## Self-Assessment

**Scope:** `Single-Component` — Touches one UI component plus the existing `intake.py` orchestration path; no new tables or routes.

**Conf:** `Medium` — Background threading pattern exists in `api_admin.py`, but intake async + poll contract is new; approach matches Susan's expected/actual behavior.

**Risk:** `Medium` — Wrong thread scheduling could duplicate sessions or drop turns; mitigated by duplicate-active guard and immediate user-line persist before turn background work.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Shared `_schedule_intake_coroutine`, `_session_awaiting_agent`; no duplicate poll logic in page |
| §2.1 config | Failure copy + poll default in `INTAKE_CONFIG`; no magic agent ids in React |
| §2.4 batch | `_run_intake_task` / ledger unchanged; background only wraps existing batch path |
| §2.6 state machine | No candidate state machine changes |
| §3.3 imports | `core/intake.py` → data, agent, candidate, utils only; API → core |
| §3.5 naming | Plan paths match flat `components/` + `pages/` layout |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-539/AST-585-inflight-initiate-persist-after-close`  
**Tip:** `4c64e9aa`

**Built:** Stages 1–2 — `INTAKE_CONFIG` poll/failure keys; `intake.py` daemon-thread initiate/turn completion, `awaiting_agent` on DTO, duplicate-active guard; `api_intake.py` **409** on duplicate create; `IntakeChatModal.tsx` `mountedRef`, active-session poll (3s), no `AbortSignal` on unmount. Stage 3 pytest/Vitest deferred to Betty per build-astral test-tree ban.

**dev-kath SHAs:** `07401452` (core), `21f958d9` (API + modal publish slice); `158d9a10` align chore (dev-kath only, not on publish ref).
