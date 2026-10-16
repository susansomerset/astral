# AST-2059 — fix: show rubric modal reads rubric content from hydrated candidate detail

<!-- linear-archive: AST-2059 archived 2026-10-16 -->

## Linear archive (AST-2059)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2059/fix-show-rubric-modal-reads-rubric-content-from-hydrated-candidate  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2058 — the "show rubric" link on the job analysis tab does not open the rubric successfully.  
**Blocked by / blocks / related:** parent: AST-2058; blocks: AST-2060

### Description

## What this implements

The **show rubric** link on the Job Analysis tabs (and the agent story tab, which uses the same header) opens `RubricModal` with the vector's actual rubric prompt instead of `No rubric found for this vector.` Rubric content is read from the selected candidate's hydrated artifacts (`GET /api/candidates/<id>`, which already overlays the `rubric_vector` table), not from the unhydrated `CandidateContext` list payload.

## Scope

## Component scope

* `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` (modified): load rubric content from the hydrated candidate detail instead of the unhydrated list payload in `CandidateContext`.
* `src/ui/frontend/src/components/RubricModal.tsx` (modified, if needed): tell "still loading" apart from "no rubric found."

## Technical scope

* `AgentAnalysisHeader.tsx`: modified component function. Add a fetch, triggered when the modal opens, of the selected candidate's hydrated artifacts, and point the `liveList` derivation at it. The props stay the same, so `JobAnalysisReportModal` and `AgentStoryTab` need no changes. The API endpoint already exists, so no backend change is expected.
* `RubricModal.tsx`: possibly a modified props interface (a loading flag), so a pending fetch doesn't render the not-found fallback.

## Acceptance criteria

* Clicking **show rubric** on a graded vector shows that vector's criterion `content` for the selected candidate, matched by label or code the same way as today.
* The `No rubric found for this vector.` fallback appears only when the candidate really has no matching rubric row.
* No not-found flash while the content is loading.

## Boundaries

* No backend/API change. `hydrate_rubric_artifacts_for_response` and the candidate list route stay as they are.
* No change to the job-carried `{prefix}_rubric` snapshot (AST-1063 deliberately omits `content`).
* No change to grade-row labels/order (`rubricItems` precedence stays).

## Notes for planning

Root cause (see the AST-2058 Description): `CandidateContext` loads `GET /api/candidates` (raw `candidate_data`). Since AST-723 the rubrics live in `rubric_vector` and are hydrated into `artifacts` only on the single-candidate GET, so `liveList` is always empty and the job-carried snapshot has no `content`.

No ancestor was checked on AST-2058. Doc to patch, chosen by Chuckles as the closest owner of this code path: `docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md`.

## Git branch (authoritative)

Parent `ftr/AST-2058-show-rubric-content`; this child `sub/AST-2058/AST-2059-show-rubric-content`. Registry is authoritative.

### Comments

#### radia — 2026-10-08T21:52:30.785Z
[code-rubric] PROCEED (Commit: 61f1f40ea) Hydrated detail rubric content

#### ada — 2026-10-08T21:50:42.352Z
`origin/sub/AST-2058/AST-2059-show-rubric-content` @ `61f1f40ea` — lighter check (qa-fix skipped; Betty REVISE → AST-2060).

- `npx tsc -b --noEmit` ✅ · `npx eslint AgentAnalysisHeader.tsx RubricModal.tsx` ✅
- `npm run test:component -- test_AgentAnalysisHeader.test.tsx test_RubricModal.test.tsx` → **8/8 pass** (predicted 2–3 red did not occur).

Why green, for AST-2060: the `api` mock returns the list array with no `ok`, so the detail fetch resolves as failed and no content is found there. Modal content then falls back to the label row from the **list fixture**, which carries `content` (the real `GET /api/candidates` never does). These tests do not exercise the detail-fetch path or the "Loading rubric…" state yet.

#### joan — 2026-10-08T21:48:14.333Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T21:47:50.566Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md (Analysis / job surfaces row → test_AgentAnalysisHeader.test.tsx; RubricModal has no bible entry) — broken tests + missing repro coverage — the existing tests assert rubric content coming from the list payload, which is the bug path, and nothing checks the detail fetch or the loading state.

Detail (for qa-fix):
- **Will break:** `test_AgentAnalysisHeader.test.tsx` › "renders grades with rubric links and opens the modal" and "matches rubric rows by code and handles missing modal content". Both use one `mockedApi.mockResolvedValue` that returns the `/api/candidates` list array (no `ok`) for every call. After the fix, the `/api/candidates/c1` fetch gets that same array, so `contentLiveList` is `[]` and the modal shows the fallback text instead of "Rubric body" / "Body". Fix: route the mock by URL (list → array; `/api/candidates/c1` → `{ ok: true, candidate_data: { artifacts: { joblist_rubric: [...] } } }`), and await the content with `findByText` / `waitFor`.
- **Timing risk:** "opens the rubric modal with no matching row" checks the fallback with a synchronous `getByText` right after the click. With the fix, the modal shows "Loading rubric…" first, so this check should switch to `findByText`.
- **Missing repro test (bug-repro):** the list payload carries no rubric, the detail payload carries `content`, and the modal must show that content. This test should fail on the pre-fix tree.
- **Missing coverage:** `loading` → "Loading rubric…" in `test_RubricModal.test.tsx`; a `!r.ok` or rejected detail fetch ends on the fallback text, not stuck on loading. The stale-response guard is optional.
- **Holds:** AST-1771 order test (`rubricItems`, no modal); `RubricModal` fallback while content is `null` (`loading` defaults to false); `test_JobAnalysisReportModal.test.tsx` never clicks show rubric, so it is not touched.

#### ada — 2026-10-08T21:47:00.820Z
`origin/sub/AST-2058/AST-2059-show-rubric-content` @ `58a46f7f4` · fetch hydrated detail for content

---

_Implementation detail may live in git history on `origin/dev`._
