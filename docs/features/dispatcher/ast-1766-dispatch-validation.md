<!-- linear-archive: AST-1766 archived 2026-10-02 -->

## Linear archive (AST-1766)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1766/dispatch-validation  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Low / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators can turn AUTO on or hit Run/Sweep on a Scheduled Actions row whose `task_key` prompts cannot be usefully filled for that row’s candidate — burning API calls and producing empty-token failures. This epic closes that hole: when the selected task’s current token set would render empty for the candidate on the `dispatch_task` record, AUTO and Run/Sweep are disabled, the server rejects AUTO-on and Run, and AUTO that is already on is forced off when the task or a related artifact becomes non-executable — so dispatch only runs when the prompts can actually be filled.

## Functional scope

* Detect, for a `dispatch_task` row, whether the current `agent_task` (all prompt fields) plus the bound agent’s system prompt would render empty for that row’s candidate — predicate **A**: any referenced **candidate-scoped** token (candidate-source and candidate-backed artifact tokens in `TOKEN_SOURCES`) resolves to a blank string. Chain tokens are ignored. Job (and other non-candidate entity) tokens are **out of scope for this epic’s validation**, but the helper’s shape must leave room to add entity-type contexts later without a rewrite.
* Enrich the Scheduled Actions list payload with that readiness signal so the UI can act without a second round-trip per row.
* Disable the AUTO toggle and the Run/Sweep control on rows that fail the check.
* Reject server-side attempts to turn AUTO on or POST `/run` when the same check fails — same class of gate as the existing candidate Anthropic API-key check.
* Force AUTO off when a row is no longer executable (candidate-scoped tokens would render empty), including when a new `agent_task` version lands (re-check that `task_key` for every candidate’s matching `dispatch_task` rows) and when a new candidate artifact version lands (re-check every related `dispatch_task` whose prompts reference tokens backed by that artifact).
* Leave Debug and other non-run controls alone; do not change eligibility / Available counts or the dispatcher claim-loop shape itself.
* Every `dispatch_task` row has a real `candidate_id` — there is no “meteorite global / missing candidate” carve-out (`astral.dispatch.entity-state-bound`).

## Component scope

* `src/utils/config.py` — **modified** — empty-render helper over `TOKEN_SOURCES` / `resolve_tokens`: inspects referenced tokens across all `agent_task` prompt segments plus agent system text; scores candidate-scoped tokens only in this epic; ignores `source: chain`; API shaped so a future caller can pass additional entity contexts (job/company/…) without replacing the helper.
* `src/ui/api/api_admin.py` — **modified** — list enrichment; AUTO-on create/update and `POST …/run` gates beside `_candidate_dispatch_api_key_error`; invoke force-AUTO-off when enrichment shows a row non-executable.
* `src/data/database.py` — **modified** — after a new current `agent_task` version is written, trigger revalidation for that `task_key` across candidates’ `dispatch_task` rows (force AUTO off when empty-render).
* `src/core/candidate.py` — **modified** — after a candidate artifact current version rotates (write-operative / current path), trigger revalidation for related `dispatch_task` rows whose prompts reference tokens backed by that artifact.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — honor the list flag: disable AUTO and Run/Sweep; Stop/Drain for already-running threads unchanged.

## Technical scope

* `src/utils/config.py` — new helper: given prompt field texts (user, cache A–D, nocache, task `system_prompt`) plus agent system content, candidate token view, and task_key, resolve referenced **candidate-scoped** tokens (candidate-source + candidate-backed artifact); ignore `source: chain`; do not fail the check on empty job/company/other entity tokens in this epic; accept an optional extensibility hook (e.g. optional entity-context map or equivalent) so later epics can score other entity types without replacing the helper; return whether any scored token renders blank (and enough detail for a clear API error).
* `src/ui/api/api_admin.py` — modified `list_dtasks` enrichment: load current `agent_task` + agent + `build_candidate_token_view(candidate)`; set boolean empty-render flag from the helper; when flag is true and `auto_mode` is on, force AUTO off (persist); create/update AUTO-on and `run_dtask` return 400 when the check fails.
* `src/data/database.py` — modified `agent_task` current-version write path: after committing the new current row, call revalidation for that `task_key` across all `dispatch_task` rows with that key (force AUTO off when empty-render for that row’s candidate).
* `src/core/candidate.py` — modified operative current-artifact write path: after a new current artifact version for a candidate, find related `task_key`s whose prompts reference tokens for that artifact and revalidate those candidates’ `dispatch_task` rows (force AUTO off when empty-render).
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — modified row render/handlers: AUTO and Run/Sweep non-interactive + visually muted when the list flag is set; no client-side `resolve_tokens` / `TOKEN_SOURCES`.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.write-operative` — [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.write-operative.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.write-operative.md>) — artifact current rotation is the hook point for revalidation after a new artifact version (do not invent a parallel artifact write path).
* Otherwise `no established pattern applies` for the admin AUTO/Run control-gate itself; closest in-tree precedent is `_candidate_dispatch_api_key_error` (not a catalog pattern). Token resolution must use existing `TOKEN_SOURCES` / `resolve_tokens` — no second token map.

**New patterns proposed** — none.

**Applicable statutes**

* `astral.dispatch.entity-state-bound` — [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.dispatch.entity-state-bound.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.dispatch.entity-state-bound.md>) — every `dispatch_task` has a real `candidate_id` and bound entity_type/trigger_state; this gate always evaluates against that candidate (no missing-candidate carve-out).
* `stat.logging.info.api` — [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — completing-route API progress only when adding route-level logging.
* `stat.logging.warning` — [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>) — per-item why when enrichment, gate, or revalidation cannot evaluate a row.
* `stat.logging.error` — [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — thrown exceptions at the handler with facts + traceback.

## Acceptance criteria

 1. Predicate **A** (candidate-scoped): for a row whose prompts (all `agent_task` prompt fields + agent system) reference a candidate-source or candidate-backed artifact token that resolves to `""` for that row’s candidate, `GET /api/admin/dispatch_tasks` includes an explicit boolean on that row that is `true` for empty-render (field name chosen in plan). **Fail:** flag missing, or `false` while such a token resolves blank.
 2. On such a row, AUTO and Run/Sweep are disabled in the UI (not clickable; Run/Sweep visually muted). **Fail:** click still fires `PUT` `auto_mode: true` or `POST …/run`.
 3. `PUT …/dispatch_tasks/<id>` with `auto_mode: true` on a failing row returns HTTP 400 and does not persist AUTO on. **Fail:** 200 with AUTO stored on.
 4. `POST …/dispatch_tasks/<id>/run` on a failing row returns HTTP 400 with `started: false` (or equivalent) and does not start the thread. **Fail:** thread starts or `started: true`.
 5. A row that was AUTO on becomes AUTO off after list enrichment / revalidation once empty-render is true (persisted). **Fail:** `auto_mode` remains on after enrichment when the flag is true.
 6. Saving a new current `agent_task` version for a `task_key` revalidates every `dispatch_task` with that key and forces AUTO off on rows that now empty-render under the candidate-scoped predicate. **Fail:** AUTO stays on for a candidate whose candidate-scoped tokens now resolve empty after the version bump.
 7. Writing a new current candidate artifact version revalidates related `dispatch_task` rows (prompts that reference tokens backed by that artifact) and forces AUTO off when empty-render. **Fail:** AUTO stays on after the artifact rotate while a referenced candidate artifact token is blank.
 8. Grep of `AdminScheduledActions.tsx` shows no local `resolve_tokens` / `TOKEN_SOURCES` reimplementation. **Fail:** client-side resolver added for this gate.
 9. The empty-render helper ignores `source: chain`, does **not** treat empty `source: job` (or other non-candidate entity) tokens as a failing check in this epic, and exposes an extension point (optional entity-context argument or equivalent) so a later epic can score other entity types without replacing the helper. **Fail:** job emptiness flips the flag true in this epic’s behavior, or the helper is a sealed candidate-only function with no documented extension seam.
10. A row whose candidate-scoped tokens all resolve non-empty keeps AUTO and Run/Sweep enabled (subject to existing API-key and Sweep/min_count rules), even if prompts also reference job tokens that would be blank without a job context. **Fail:** controls disabled solely because job tokens are empty.

## Open questions

none

## Proposed child tickets

#### 1!!: **Empty-token predicate helper - Ada**

Owns the shared empty-render helper in config (all prompt fields + agent system; candidate-scoped scoring; ignore chain; extension seam for future entity contexts). Does not own API gates, force-off persistence, version hooks, or React.
**Citations:** `astral.dispatch.entity-state-bound`; patterns: none for the helper itself (`no established pattern applies` beyond `TOKEN_SOURCES` / `resolve_tokens` reuse).
**Scope:** `src/utils/config.py` — new empty-render helper over `TOKEN_SOURCES` / `resolve_tokens` across all `agent_task` prompt segments plus agent system text; scores candidate-scoped tokens only; ignores `source: chain`; optional entity-context extension seam for later entity types.
**Estimate: 3**

#### 2!: **List enrich, AUTO/Run gates, force AUTO off - Hedy**

Owns Scheduled Actions list enrichment, AUTO-on / Run API 400 gates, and persisting AUTO off when a row is non-executable. After #1. Does not own `agent_task` / artifact version hooks (sibling #3) or React (sibling #4).
**Citations:** `astral.dispatch.entity-state-bound`, `stat.logging.info.api`, `stat.logging.warning`, `stat.logging.error`; patterns: none (`no established pattern applies`; mirror `_candidate_dispatch_api_key_error`).
**Scope:** `src/ui/api/api_admin.py` — list enrichment boolean; create/update AUTO-on + `run_dtask` gates; force AUTO off when enrichment shows empty-render.
**Estimate: 5**

#### 3!: **Revalidate on agent_task + artifact version - Katherine**

Owns hooks: new current `agent_task` version → revalidate that `task_key` across candidates’ `dispatch_task` rows; new current candidate artifact version → revalidate related rows whose prompts reference that artifact’s tokens; both force AUTO off via the same empty-render path as #2. After #1 (and shares force-off behavior with #2). Does not own list UI.
**Citations:** `astral.dispatch.entity-state-bound`, `patt.artifact.write-operative`, `stat.logging.warning`, `stat.logging.error`.
**Scope:** `src/data/database.py` — after new current `agent_task` version, revalidate that `task_key` across `dispatch_task` rows (force AUTO off when empty-render); `src/core/candidate.py` — after candidate artifact current rotation, revalidate related `dispatch_task` rows (force AUTO off when empty-render).
**Estimate: 5**

#### 4: **Scheduled Actions disable AUTO and Run/Sweep - Ada**

Owns UI-only: read the list flag and disable AUTO + Run/Sweep (visual mute + no click); Stop/Drain and Debug unchanged. After #2.
**Citations:** `astral.dispatch.entity-state-bound`; patterns: none (`no established pattern applies`).
**Scope:** `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — disable AUTO and Run/Sweep from the list flag only.
**Estimate: 2**

**Monolith check:** Functional scope has 7 capabilities; 4 children — not a monolith.
**Scope partition check:** every Component/Technical item appears in exactly one child Scope line.

---

## Original brief

Disable autotoggle and run/Sweep buttons when the selected task_key's current set of tokens would render empty for the candidate indicated on the dispatch_task record.

### Comments

#### chuckles — 2026-09-23T01:49:56.370Z
AST-1780 REVIEW — Betty scope gate: publish tip includes AST-1781; recalling Hedy to rebuild tip from AST-1779 + AST-1780-only commits.

#### chuckles — 2026-09-22T01:39:00.901Z
@susan

1. **Job tokens at list / AUTO-on time:** Scheduled Actions rows have a candidate but not a single job. For prompts that reference `source: job` tokens, should empty-render at list/AUTO-on / force-off (a) score job tokens only when a job context is in hand (per claimed entity on Run / in the dispatch loop) and score candidate/artifact/config/rubric/etc. at list time, or (b) probe eligible job(s) for that row at list/revalidation time and fail if those job tokens would be blank? (Chain stays ignored either way.)

#### chuckles — 2026-09-22T01:27:22.604Z
@susan

1. **Empty predicate:** Does “tokens would render empty” mean (A) any **candidate-sourced** (and/or artifact) token referenced in the task prompts resolves to a blank string for that candidate, or (B) Manage Tasks `task_ready === false` (unresolved `{$…}` left after resolve — which does **not** catch blank values)? Recommend A unless you want exact Manage Tasks parity.
2. **Which prompt fields** are in the set: cache A–D only (Manage Tasks probe), or also system / user / nocache on the current `agent_task`?
3. **Rows with blank / missing `candidate_id`** (e.g. meteorite global): fail-closed (disable AUTO + Run/Sweep) or skip the token check and leave existing API-key / Available rules alone?
4. **AUTO already ON** when tokens later go empty: force OFF on list/enrichment, only block turning ON + Run/Sweep, or also auto-disable AUTO on the next list refresh?
5. **Job / chain tokens** at list time are often empty by design (`chain_entry`). Confirm the gate ignores `source: job` and `source: chain` (and `CALLER_*`) and only scores tokens the candidate can supply before a run starts.

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/d0cce58a5b66966a2fb93f49de7ad8f5/9f711285-0ec9-4f5a-a25b-4a50b601db0e/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/d0cce58a5b66966a2fb93f49de7ad8f5/b69546d5-52fb-44b6-bfce-45323094a92d/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/d0cce58a5b66966a2fb93f49de7ad8f5/858343f5-6c66-4dd7-a211-b352ca851b18/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/831f9ac7-5f09-4367-9a93-d7b5b2a05ab7/store.db` |
| Radia | review | `/home/susan/.cursor/chats/d0cce58a5b66966a2fb93f49de7ad8f5/969e07c8-d5f6-4818-b0e8-a153fdbc77f8/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1766 (parent) | ftr/AST-1766-dispatch-validation |
| AST-1779 | sub/AST-1766/AST-1779-empty-token-predicate-helper |
| AST-1780 | sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off |
| AST-1781 | sub/AST-1766/AST-1781-revalidate-on-agent-task-artifact-version |
| AST-1782 | sub/AST-1766/AST-1782-scheduled-actions-disable-auto-run-sweep |

**Epic worktree:** `astral-AST-1766/` — one active sub checked out at a time.
