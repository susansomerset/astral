# AST-1319 — Implement _RETRY for new meteorite states

<!-- linear-archive: AST-1319 archived 2026-08-19 -->

## Linear archive (AST-1319)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1319/implement-retry-for-new-meteorite-states  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

We had some errors with meteorite qualifications, and instead of retry, they went to METEORITE_ERROR_QUALIFY.  We need a retry state first.

### Comments

#### chuckles — 2026-08-12T14:48:33.069Z
Got it — ancestor locked: **AST-898** (`docs/features/consult/ast-898-new-retry-qualify-holding.md`).

## As-is / to-be

- **As-is:** Meteorite qualification errors land straight on `METEORITE_ERROR_QUALIFY` with no retry holding first.
- **To-be:** Mirror AST-898 for meteorite: `METEORITE_NEW` → `METEORITE_NEW_RETRY` (first strike) → `METEORITE_ERROR_QUALIFY` (second strike), same shape as `NEW` → `NEW_RETRY` → `ERROR_QUALIFY_JOB_LISTINGS`.

Move this ticket to **Todo** (assignee Chuckles) when that read is approved — bug-fix seeds git and starts plan-fix from there. No git / no spawn from this pass.

#### susan — 2026-08-12T14:46:55.880Z
898 is the one

#### chuckles — 2026-08-12T13:24:15.715Z
Resumed round (silent reassign ×2) — treated as “different candidates,” not a reject-all. Spent 4 greps; prior list 1–5 still valid if you want them.

## As-is / to-be (unchanged)

- **As-is:** Meteorite qualification errors land straight on `METEORITE_ERROR_QUALIFY` with no retry holding first.
- **To-be:** New meteorite states get a `_RETRY` holding so qualify can retry before the hard error state.

## New candidates this round (ranked)

1. **AST-898** (`docs/features/consult/ast-898-new-retry-qualify-holding.md`) — best pattern twin: regular `NEW` → `NEW_RETRY` → `ERROR_QUALIFY_JOB_LISTINGS`; meteorite still lacks `METEORITE_NEW` → `METEORITE_NEW_RETRY` → `METEORITE_ERROR_QUALIFY`.
2. **AST-1053** (`docs/features/meteorite/ast-1053-meteorite-gdl-parallel-job-states.md`) — explicit ⚠️ decision: do **not** add `METEORITE_NEW_RETRY` (only `METEORITE_PASSED_LIKE_RETRY` then); this bug is the later ask to reverse that carve-out for qualify.
3. **AST-642** (`docs/features/dispatcher/ast-642-per-entity-retry-vs-error-routing-in-mixed-batch-consult-auto-retry.md`) — foundation for per-entity first-strike retry vs second-strike error in mixed batches (what `NEW_RETRY` / qualify routing sits on).

## Still on the table from round 1 (if you prefer those)

AST-1155 · AST-1150 · AST-1060 · AST-1062 · AST-1156

Pick a row (or reject-all / new ask) and reassign, or Todo when ready for bug-fix.

#### chuckles — 2026-08-12T13:18:43.619Z
Resumed round: no new comment from you since the candidate list — treating reassignment alone as “still need a pick,” not a reject-all or a changed ask.

## As-is / to-be (unchanged)

- **As-is:** Meteorite qualification errors land straight on `METEORITE_ERROR_QUALIFY` with no retry holding first.
- **To-be:** New meteorite states get a `_RETRY` holding so qualify can retry before the hard error state.

## Candidates still on the table (same ranking — no fresh greps)

1. **AST-1155** — meteorite `*_RETRY` for GDL hops; qualify / `METEORITE_NEW` gap before `METEORITE_ERROR_QUALIFY`
2. **AST-1150** — parent epic (retry ≠ technical-fail)
3. **AST-1060** — registered `METEORITE_ERROR_QUALIFY` without an intervening retry state
4. **AST-1062** — batch technical → `METEORITE_ERROR_QUALIFY`
5. **AST-1156** — Skipped Retry map only (later layer)

Reply with a pick, a reject-all, or a different ask, then reassign Chuckles — or move to Todo when the ancestor + read look right for bug-fix.

#### chuckles — 2026-08-12T12:53:18.227Z
## As-is / to-be

- **As-is:** Meteorite qualification errors land straight on `METEORITE_ERROR_QUALIFY` with no retry holding first.
- **To-be:** New meteorite states get a `_RETRY` holding so qualify can retry before the hard error state.

## Ancestor candidates (ranked)

1. **AST-1155** (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`) — closest: shipped meteorite `*_RETRY` holdings for GDL graded hops; left qualify / `METEORITE_NEW` without a parallel first-strike retry before `METEORITE_ERROR_QUALIFY`.
2. **AST-1150** (`docs/features/consult/ast-1150-technical-fail-for-do-prompt.md`) — parent epic: incomplete/recoverable fails must retry, not technical-fail, for meteorite + regular.
3. **AST-1060** (`docs/features/meteorite/ast-1060-meteorite-qualified-qualify-meteorite-config-dispatch.md`) — registered `METEORITE_ERROR_QUALIFY` as the technical qualify outcome with no `METEORITE_NEW_RETRY` (or similar) in between.
4. **AST-1062** (`docs/features/meteorite/ast-1062-qualify-meteorite-batch-apply-meteorite-qualified.md`) — wired `qualify_meteorite` batch technical failures straight → `METEORITE_ERROR_QUALIFY`.
5. **AST-1156** (`docs/features/consult/ast-1156-skipped-retry-hop-correct-dispatchable-state.md`) — related but later layer: Skipped operator Retry maps `METEORITE_ERROR_QUALIFY` → `METEORITE_NEW`; not the consult first-strike `_RETRY` this bug names.

Pick one (or reject all / ask about a specific row) and move to Todo when ready for bug-fix.

---

_Implementation detail may live in git history on `origin/dev`._
