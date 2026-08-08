# AST-1096 — Restart intake gets a 500 error

<!-- linear-archive: AST-1096 archived 2026-08-07 -->

## Linear archive (AST-1096)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1096/restart-intake-gets-a-500-error  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Restarting an in-progress candidate intake (Start Over) is broken in UAT: the UI posts to archive the active session and gets a server error that surfaces as “method is not allowed,” so operators cannot clear an active thread and begin a fresh preamble/intake for a test user. This belongs now because AST-952 mechanical intake UAT depends on Start Over working, and the archive contract already exists in core and the React front door — only the HTTP surface is missing/regressing.

## Functional scope

1. An authenticated caller can archive the candidate’s **active** intake session through the existing Start Over path (`POST …/intake/sessions/active/archive`), so the prior thread is preserved in the candidate’s intake history and is no longer active.
2. When there is no active session, archive responds as “nothing to archive” (not a hard server failure), matching the UI’s existing Start Over tolerance for that case.
3. After a successful archive, a subsequent active-session check reports no active session, so Start Over can open a fresh preamble / new intake without leaving a stuck active thread.
4. Continue-on-active-session (resume without archiving) remains unchanged.

## Architectural definition

* **Patterns to reuse** — `pattern.ui.admin-endpoint` (thin `@require_auth` UI API that delegates business work; same shape as other candidate intake routes even though this is not an admin blueprint); `pattern.layers.import-discipline` (UI API → `src.core.intake` only; no UI→data).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.patterns.require-auth-on-protected-endpoints` (archive mutator must be auth-gated); `astral.layers.import-direction` (UI may call core, not data/external); `astral.layers.ui-config-driven-business-logic` (archive/status semantics stay in core/config, not React); `astral.standards.in-scope-only` (restore archive wiring only — no preamble/topic-menu redesign); `astral.standards.data-raises-caller-logs` (core raises; API maps to JSON status codes).

## Boundaries

* Does **not** change preamble script, Ruth validation, Topic Menu, or Estelle turn/build behavior.
* Does **not** redesign Start Over / Continue dialog UX (AST-583/AST-1017 already own that); only makes the archive call succeed.
* Does **not** alter `intakes_old` shape or Execution History / ledger semantics beyond the existing core archive contract (AST-582).
* Does **not** fix unrelated intake 500s (e.g. prior AST-590 merge-kwarg class of bugs) unless they still block this archive path.
* Must not break create-session, get-active, turns, or build routes.

## Acceptance criteria

1. With an active intake for a candidate, Start Over (or equivalent restart) completes without a 500 / “method is not allowed” error.
2. After Start Over succeeds, GET active session reports no active session; a new preamble/intake can start.
3. The prior conversation is retained on the candidate as an archived intake history entry (not silently deleted).
4. Continue still resumes the active session without archiving.
5. Unauthenticated archive calls are rejected.

## Dependencies and blockers

none. Adjacent UAT context: AST-952 (Candidate Profile Preamble to Intake) / AST-1017 Start Over path — this bug blocks restart during that UAT but is not blocked by those tickets finishing.

## Open questions

none.

## Proposed child tickets

#### 1: **Restore archive-active intake API for Start Over - Ada**

Wire the missing authenticated `POST …/intake/sessions/active/archive` surface to existing core `archive_active_intake_session` with correct success / not-found / auth outcomes so the current Candidate Intake Start Over flow can clear an active session and proceed to fresh preamble. Does **not** own React dialog redesign or preamble/topic-menu work.
**Citations:** `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.layers.import-direction`, `astral.standards.in-scope-only`.

**Monolith check:** Functional scope has four capabilities but one inseparable vertical slice (restore the archive HTTP contract the UI already calls; core archive already exists) — single child is intentional.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1096 (parent) | ftr/AST-1096-restart-intake-gets-a-500-error |
| AST-1097 | sub/AST-1096/AST-1097-restore-archive-active-intake-api |

**Epic worktree:** `astral-AST-1096/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/ded628bdf3bc4977223686361ddba02c/504e609f-6a13-478f-b335-0d14c54283cc/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/65070a5a-3a37-49c8-b758-729b5d08544b/store.db` |
| Radia | review | `/home/susan/.cursor/chats/ded628bdf3bc4977223686361ddba02c/6ed023ff-6ddf-4090-ad8b-13740f73078f/store.db` |

---

## Original brief

```
127.0.0.1 - - [30/Jul/2026 17:40:13] "GET /api/candidates/klech/intake/sessions/active HTTP/1.1" 200 -
127.0.0.1 - - [30/Jul/2026 17:40:15] "POST /api/candidates/klech/intake/sessions/active/archive HTTP/1.1" 500 -
127.0.0.1 - - [30/Jul/2026 17:40:16] "GET /api/shapes/candidates HTTP/1.1" 200 -
```

Trying to restart an intake conversation for a test user got "method is not allowed"

### Comments

#### chuckles — 2026-07-31T04:22:40.726Z
[thread-missing] Betty/Radia Team store.db paths from dispatch were empty on this host; populate-team reminted usable threads. Ada recovered from history. Continuing pipeline.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
