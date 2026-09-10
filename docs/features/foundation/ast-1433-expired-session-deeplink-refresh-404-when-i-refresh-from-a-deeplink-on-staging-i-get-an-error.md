# AST-1433 — Expired-session deeplink refresh 404 (When I refresh from a deeplink on staging I get an error)

<!-- linear-archive: AST-1433 archived 2026-09-09 -->

## Linear archive (AST-1433)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1433/expired-session-deeplink-refresh-404-when-i-refresh-from-a-deeplink-on  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-1424 — When I refresh from a deeplink on staging I get an error  
**Blocked by / blocks / related:** parent: AST-1424

### Description

## What this implements

Expired Stytch session + hard refresh or direct navigation to an in-app path (e.g. `/candidate/backstory`) must not return a white page of `{"error":"Not found"}`. Unauthenticated HTML navigations to client routes must reach an auth page (login, or the existing log-off screen if they had a session). After sign-in they can use the app again.

Approved ancestor (archived): AST-625 — `docs/features/foundation/ast-625-session-logoff-screen-and-expired-session-detection.md`. That work is frontend-only (`RequireAuth` / `LogOffScreen`); a document request never boots the SPA, so the JSON 404 is likely Flask answering the path before the gate runs.

## Citations

none — orphaned mini-parent AST-1424; ancestor AST-625 is archived. Patch the existing AST-625 feature doc (plan-fix never creates a new plan doc).

## Acceptance criteria

- [X] Refresh or paste of an in-app URL after session expiry never shows a white JSON `{"error":"Not found"}` page.
- [X] The user lands on login or the existing log-off screen.
- [X] After they authenticate, they can reach the app (return to the original path if cheap — not in this cut).

## Proposed change

- [X] Narrow `serve_react` JSON 404 to print-HTML prefixes (`/candidate/resume…`, `/candidate/cover…`); SPA `/candidate/backstory` serves `index.html`.
- [X] Vite proxy `/candidate/resume` and `/candidate/cover` only — not the whole `/candidate` prefix.
- [X] No RequireAuth / LogOffScreen / Stytch / `api_resume_html.py` edits.

## Boundaries

* Does not change Stytch session duration, Dashboard config, or idle policy (AST-625 / AST-624 boundary).
* Does not redesign LogOffScreen copy or add manual sign-out.
* Does not own candidate backstory content (the example path is just a deep client route).

## Notes for planning

Parent AST-1424 as-is/to-be/proposed steps are the bug definition. Engineer: Katherine (AST-625 / RequireAuth / AuthContext / SPA auth gate).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1424-refresh-from-deeplink-error`, child `sub/AST-1424/<this-id>-expired-session-deeplink-refresh-404`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-19T00:49:45.589Z
[code-rubric] PROCEED (Commit: 9103d105) narrow print guard SPA

#### katherine — 2026-08-19T00:46:06.855Z
`origin/sub/AST-1424/AST-1433-expired-session-deeplink-refresh-404` @ `9103d105` · [bug-repro] green

`test_candidate_backstory_serves_index` 1 passed; TestAst1117CandidateSpaGuard + TestAst1117ViteCandidateProxy 7 passed. Merged `origin/sub/AST-1424/AST-1435-test-gap-candidate-spa-guard` @ `f5d78297`.

#### joan — 2026-08-19T00:32:18.141Z
[board-joan] CANON: OK
Narrow AST-1117 guard restores §3.5; no statute/pattern amend.

#### betty — 2026-08-19T00:30:39.771Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/server.md — broken test — TestAst1117CandidateSpaGuard/ViteCandidateProxy assert blanket /candidate 404+proxy; repro GET /candidate/backstory → 200 index.html uncovered.

#### katherine — 2026-08-19T00:28:24.380Z
`origin/sub/AST-1424/AST-1433-expired-session-deeplink-refresh-404` @ `fb8db53f` · Narrow candidate SPA guard

---

_Implementation detail may live in git history on `origin/dev`._
