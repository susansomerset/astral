# AST-1285 — State transition validation for candidates is broken

<!-- linear-archive: AST-1285 archived 2026-08-19 -->

## Linear archive (AST-1285)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1285/state-transition-validation-for-candidates-is-broken  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Admin operators need to move a candidate to a chosen state even when the current prior-states graph rejects the hop. Today Manage Candidates fails closed on illegal transitions, which blocks UAT and recovery when the configured transition rules are wrong or too tight. This epic ships an intentional admin workaround: warn with an are-you-sure confirm, then apply the hop if confirmed — without loosening automated/dispatch transition enforcement.

## Functional scope

* **Detect illegal admin hops.** When an admin changes a candidate's state from Manage Candidates (or the same admin candidate-data state override path), the product recognizes that the chosen target is not allowed from the candidate's current state under the existing candidate state registry.
* **Are-you-sure warning.** Before applying such a hop, show a warning confirmation that names the current state and the requested target and asks the operator to confirm they want to proceed anyway.
* **Confirmed override applies.** If the operator confirms, the candidate moves to the requested registered state; transition history still records the hop. If they cancel, the candidate state is unchanged and other edits in that save either succeed without the state change or the whole save is aborted consistently (no half-applied state).
* **Legal hops stay quiet.** Allowed transitions continue to apply with no extra confirm beyond any existing delete/danger confirms already in the UI.
* **Automation stays fail-closed.** Dispatch, stale aging, delete-as-DELETED flows, and other non-admin-override callers keep rejecting illegal hops — force/confirm is admin manual override only.
* **Unknown states still rejected.** Confirm-override does not invent or accept state names outside the candidate state registry.

## Architectural definition

* **Patterns to reuse**
  * `pattern.state.entity-state-transitions` — core still owns the write; data does not choose the next state; registry remains source of allowed vocabulary.
  * `pattern.ui.admin-endpoint` — admin-only mutator stays auth-gated; React does not own transition legality alone.
  * `pattern.config.config-block` — `CANDIDATE_STATES` / prior_states remain the config source of truth for what "illegal" means.
* **New patterns proposed**
  * Admin confirmed prior-states override (confirm UI + explicit override signal into the existing transition path). Flag for Archie approval before child plans treat it as catalog law; until approved, children implement the product behavior under the reuse patterns above.
* **Applicable statutes**
  * `astral.state.core-decides-transitions` — override still goes through core transition, not a raw data-layer state poke.
  * `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — legality and vocabulary from config registry, not a parallel frontend allowlist.
  * `astral.layers.ui-config-driven-business-logic` — UI confirms; core/API decide legality and apply.
  * `astral.idioms.require-auth-on-protected-endpoints` (and matching patterns statute) — admin-only.
  * Universal standards that always apply to product code: `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.public-then-helpers`, `astral.standards.logging-via-utils`, `astral.standards.data-raises-caller-logs`, `astral.standards.no-cross-contamination`, `astral.layers.import-direction`.

## Boundaries

* Does **not** redesign the full candidate lifecycle vocabulary or happy-path stages (that shipped under AST-871 / AST-970).
* Does **not** change company or job transition enforcement.
* Does **not** add a general "skip validation" switch for batch/dispatch/automation.
* Does **not** remove fail-closed behavior for unconfirmed illegal admin hops.
* Does **not** build Candidate Progress reporting (AST-869) or Topic Menu-driven transitions (AST-953).
* Does **not** replace the dedicated Delete → DELETED confirm flow unless that hop is already unrestricted; this epic is about illegal prior-states hops needing a workaround.
* Out of scope unless Open question #1 says otherwise: rewriting/loosening `prior_states` edges so fewer hops are illegal (the workaround is the product ask; graph repair is a separate decision).

## Acceptance criteria

1. From Manage Candidates, an admin who chooses a registered target state that the registry rejects from the current state sees an are-you-sure warning that identifies from → to before the state changes.
2. Confirming the warning results in the candidate persisting in the chosen target state; canceling leaves the prior state unchanged.
3. An admin choosing an allowed target state still saves without that warning (aside from unrelated existing confirms).
4. Non-admin callers cannot force an illegal candidate state hop.
5. Automated/dispatch/stale paths still fail closed on illegal hops (no confirm path).
6. Successful forced admin hops appear in candidate transition history like other successful hops.
7. Requests for unknown state names still fail (no confirm-to-invent).

## Dependencies and blockers

* Related prior art (shipped): AST-871 / AST-970 candidate state registry and fail-closed admin override via transition.
* none blocking start once open questions are answered.

## Open questions

1. Is fixing/loosening the candidate `prior_states` graph itself in scope for this epic, or is the confirm-and-force workaround the entire product ask (graph repair deferred)?
   1. No
2. Should every illegal admin hop be forceable after confirm, or are any targets excluded (for example companions/error/stale states only via their normal paths)?
   1. Yes, let me override state transitions for all states
3. When a Manage Candidates save includes both field edits and an illegal state change, on cancel of the warning: discard the whole save, or apply non-state fields and skip only the state change?
   1. Skip only the state change

## Proposed child tickets

#### 1!: **Admin confirm-override for illegal candidate hops - Ada**

Own the admin-authorized path that can apply a registered candidate state even when prior-states would reject it, while keeping non-override callers fail-closed; record history on success; reject unknown states. Does **not** own the Manage Candidates warning UI (#2).
**Citations:** `pattern.state.entity-state-transitions`, `pattern.ui.admin-endpoint`, `astral.state.core-decides-transitions`, `astral.config.config-source-of-truth`, `astral.idioms.require-auth-on-protected-endpoints`.

#### 2: **Manage Candidates are-you-sure on illegal state - Hedy**

When an admin selects an illegal target state on Manage Candidates, show the are-you-sure warning (current → target) and only proceed on confirm using the override path from #1; cancel leaves state unchanged per Open question #3. Does **not** own core transition enforcement (#1).
**Citations:** `pattern.ui.admin-endpoint`, `astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`.

**Monolith check:** Functional scope has 6 capabilities; 2 proposed children (API/core override + admin UI confirm). Graph repair, if Susan pulls it into scope via Q1, becomes a third child or expands #1 — do not invent it until she answers.

**New patterns:** Child #1 introduces the admin confirmed prior-states override shape flagged above; #2 is the UI consumer.

---

## Original brief

Allow a warning popup with are you sure? When I set a candidate state that is considered an invalid transition.  The logic is broken and I need a workaround.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1285 (parent) | ftr/AST-1285-state-transition-validation |
| AST-1287 | sub/AST-1285/AST-1287-admin-confirm-override |
| AST-1288 | sub/AST-1285/AST-1288-manage-candidates-are-you-sure |

**Epic worktree:** `astral-AST-1285/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/815144989611d20deda4c22031b298bc/9b87228f-7c72-4159-9f66-da4c84208a75/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/815144989611d20deda4c22031b298bc/da19e9c9-62c0-487a-ab12-8dc1e16f1e5c/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/2376ad4b-3c3c-434d-b637-9e389416dfc8/store.db` |
| Radia | review | `/home/susan/.cursor/chats/815144989611d20deda4c22031b298bc/3996a281-c2de-4b20-9334-1cea158659e9/store.db` |

### Comments

#### cursor — 2026-08-08T20:20:51.106Z
Stopped before any cloud agent started!

#### unknown — 2026-08-08T20:20:36.254Z
This thread is for an agent session with cursor.

#### chuckles — 2026-08-08T19:59:29.854Z
@susan

1. Is fixing/loosening the candidate `prior_states` graph in scope, or is confirm-and-force the whole ask?
2. Forceable after confirm for every illegal admin hop, or any excluded targets?
3. On cancel of the warning when the save also has field edits: discard whole save, or apply non-state fields and skip only state?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
