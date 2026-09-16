# Backstory ContextTextPage wire-up

**Linear:** [AST-1663](https://linear.app/astralcareermatch/issue/AST-1663)
**Parent:** [AST-1644](https://linear.app/astralcareermatch/issue/AST-1644) — Migrate candidate_data.context.backstory to use the artifact table
**Publish ref:** `sub/AST-1644/AST-1663-backstory-contexttextpage-wire-up`

Retarget Backstory-only UI load/save onto the operative API contract via existing `ContextTextPage` — same thin Strengths / Priorities / Deal Breakers / Ideal Day wire-up as [AST-1634](https://linear.app/astralcareermatch/issue/AST-1634) / [AST-1653](https://linear.app/astralcareermatch/issue/AST-1653) / [AST-1656](https://linear.app/astralcareermatch/issue/AST-1656) / [AST-1660](https://linear.app/astralcareermatch/issue/AST-1660) Stage 1, without re-parameterizing `ContextTextPage` (already done on AST-1629 / AST-1634). No `ArtifactEditor`. No sibling context page rewrites. Catalog lands with [AST-1661](https://linear.app/astralcareermatch/issue/AST-1661); operative GET hydrate / PUT intercept land with [AST-1662](https://linear.app/astralcareermatch/issue/AST-1662) — both User Testing; merge onto tip via `sync-child` / `origin/ftr/AST-1644-migrate-backstory-artifact-table` (or sibling publish refs) before hand-verify.

## UAT fitness

- **AC restored:** Parent AC6 — "Editor reload — Backstory page after save shows the same text. Fail: empty editor while a current artifact row exists." Parent AC9 / ticket AC7 — "UI path — `CandidateBackstory.tsx` passes `bodyShape=\"plain_text\"` into `ContextTextPage` (same shape as Strengths); `ArtifactEditor` diff for this ticket is empty. Fail: Backstory routed through ArtifactEditor / resume_content, or still missing `bodyShape`."
- **Correct outcome:** With a candidate selected, Backstory loads the hydrated `context.backstory` string (current artifact via AST-1662, or legacy blob / empty on miss); Save keeps the same text in the textarea after success; empty/whitespace Save is refused client-side by the existing `plain_text` gate (no PUT); `ArtifactEditor.tsx` and `ContextTextPage.tsx` have zero product diff on this ticket.
- **Sibling check:** AST-1661 (`candidate.context.backstory` + `plain_text` + `TOKEN_SOURCES["BACKSTORY"]` artifact-typed) and AST-1662 (PUT intercept + GET hydrate + library SoT gate) remain authoritative — this ticket only passes `bodyShape="plain_text"` so the shared page uses the empty-save gate; load/save still ride `GET/PUT` `{ context: { backstory } }`. Verify by merging sibling tips / `origin/ftr/AST-1644-migrate-backstory-artifact-table` before hand-check; do not re-implement catalog or API here.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Re-editing `ContextTextPage.tsx` (already parameterized), routing Backstory through `ArtifactEditor` / `resume_content`, inventing a client `artifacts` PUT slot, or clearing the leaf on miss — all violate parent Component scope and AST-1634 guidelines.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/ui/frontend/src/pages/CandidateBackstory.tsx` — Backstory-only wire-up against existing ContextTextPage.

Every Files Changed row and every Stage step stays inside that one file. No `config.py`, no `candidate.py`, no `api_candidate.py`, no `ContextTextPage.tsx`, no `ArtifactEditor.tsx`, no `routes.tsx`, no sibling `Candidate*.tsx` context pages, no `database.py`.

**Already on tip / sibling-owned (do not re-invent):**

- `ContextTextPage` optional `bodyShape` + `plain_text` empty-save gate (AST-1634).
- Route `candidate/backstory` + nav leaf `/candidate/backstory` (pre-existing; Ada AST-1661 does not own nav changes for this leaf).
- PUT `{ context: { backstory } }` → operative save; GET hydrate overlays current row (AST-1662).

**Build precondition:** After `sync-child.sh`, `ARTIFACT_CONFIG` must contain `candidate.context.backstory` and AST-1662 PUT/GET Backstory paths must be present (via `origin/ftr/AST-1644-migrate-backstory-artifact-table` or merged sibling tips `origin/sub/AST-1644/AST-1661-…` + `origin/sub/AST-1644/AST-1662-…`). If missing, stop and comment on parent AST-1644 — do not invent catalog or API intercept here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateBackstory.tsx` | Pass `bodyShape="plain_text"` with existing `contextKey="backstory"` | ui |

**Out of this ticket (do not touch):** `ContextTextPage.tsx` / `ArtifactEditor.tsx`; sibling context pages (`CandidateStrengths`, `CandidatePriorities`, `CandidateDealBreakers`, `CandidateIdealDay`, `CandidateBioSummary`, `CandidateWritingPreferences`, …); `routes.tsx`; Ada config (`config.py`); Hedy core/API; `tests/` / `docs/test-bible/**`.

## Stage 1: Wire Backstory `plain_text` bodyShape

**Done when:** With a candidate selected, navigating to `/candidate/backstory` (or Candidate nav → Backstory) renders `ContextTextPage` with Backstory title; load shows hydrated `context.backstory` (current artifact via AST-1662, or legacy blob / empty on miss); Save PUTs `{ context: { backstory: <draft> } }` and reload shows the same text; empty/whitespace Save is blocked by existing `plain_text` gate (no PUT); `git diff --name-only` for this stage’s product commit is only `CandidateBackstory.tsx` — `ArtifactEditor.tsx` and `ContextTextPage.tsx` untouched.

1. In `src/ui/frontend/src/pages/CandidateBackstory.tsx`, replace the one-liner with the Strengths twin shape (mirror `CandidateStrengths.tsx` / `CandidateIdealDay.tsx`, keep Backstory title / key):

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function Backstory() {
  return (
    <ContextTextPage
      title="Backstory"
      contextKey="backstory"
      bodyShape="plain_text"
    />
  )
}
```

Hardcode `bodyShape="plain_text"` to match `ARTIFACT_CONFIG["candidate.context.backstory"]["body_shape"]` (Ada AST-1661). Do **not** import or fetch config from the frontend. Do **not** add an `artifactKey` prop — the API leaf stays `context.backstory` (Hedy PUT intercept).

⚠️ **Decision:** Only add `bodyShape="plain_text"` — page, title, `contextKey`, and route already exist. Do not re-open `ContextTextPage.tsx` (parameterized on AST-1634). Do not touch `routes.tsx` or nav.

2. Do **not** edit `ContextTextPage.tsx`, `ArtifactEditor.tsx`, any other `Candidate*.tsx` context page, `routes.tsx`, or any non-frontend file. Load/save behavior is entirely the existing `ContextTextPage` contract: `GET /api/candidates/${selectedId}` → `context[contextKey]`; `PUT` body `{ context: { [contextKey]: draft } }` — backstory rides AST-1662 intercept/hydrate with no client changes.

**Verify (hand):** with AST-1661 + AST-1662 on tip and a candidate selected — open Backstory via nav or `/candidate/backstory`; edit text; Save → success toast and textarea still shows that text; refresh/re-enter → same text when a current artifact row exists (or legacy blob until first operative save); clear textarea → Save disabled / empty toast, no network PUT; confirm `ArtifactEditor.tsx` and `ContextTextPage.tsx` have no diff in this ticket’s product commit; Strengths and other context pages still compile.

## Execution contract

- Execute steps in order within the stage; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files beyond the Files Changed table, touch Ada/Hedy scopes, edit sibling context pages, or extend `ContextTextPage` / `ArtifactEditor` / `routes.tsx`.
- On ambiguity or drift — stop, comment on parent AST-1644 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.ui-consistency` | pattern — read in full; plain_text → ContextTextPage; hardcode bodyShape literal; no ArtifactEditor |
| `patt.artifact.read-current` | pattern — read in full; editor opens on GET hydrate leaf (no client blob invent / second fetch) |
| `patt.artifact.write-operative` | pattern — read in full; Save keeps context-leaf PUT → AST-1662 operative intercept |

## Traceability

- Ticket / parent AC6 (editor reload) → Stage 1 §§1–2 + verify
- Ticket AC7 / parent AC9 (UI path; ArtifactEditor untouched) → Stage 1 §2 + Files Changed
- Parent AC7 (no backfill; legacy until re-save) → existing ContextTextPage miss path + AST-1662 hydrate (no client clear)
- Sibling freeze / other context pages → scope gate; no sibling page edits
- Parent AC1–5 / AC8 → N/A (AST-1661 / AST-1662)

## Joan validate

[plan-rubric]
**Ticket:** AST-1663
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `69d7bd5ddd493bd41e28a5a42168ac7767ff228a` (`origin/sub/AST-1644/AST-1663-backstory-contexttextpage-wire-up`)

## Canon scores

| Id | Grade | Effort | One-line |
|----|-------|--------|----------|
| patt.artifact.ui-consistency | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.write-operative | A | | |

## Traceability

AC6→Stage 1 §§1–2 + verify (reload via PUT response + GET hydrate); AC7→Stage 1 §1 (`bodyShape="plain_text"`) + scope gate (ArtifactEditor untouched); parent AC7→ContextTextPage miss path + AST-1662 hydrate (no client clear); parent AC1–AC5, AC8→N/A (AST-1661 / AST-1662 siblings).

## Findings

### acceptable — current gap the plan closes

- **Location:** `CandidateBackstory.tsx` (tip) vs Stage 1
- **Finding:** Tip omits `bodyShape="plain_text"` while Strengths / Ideal Day already pass it; without it Backstory skips the client empty-save gate and fails ticket AC7 / parent AC9 until this stage lands.
- **Recommendation:** None — Stage 1 is the correct minimal fix.

### acceptable — build precondition

- **Location:** Explicit scope gate / UAT fitness sibling check
- **Finding:** Hand-verify depends on AST-1661 catalog + AST-1662 PUT/GET on tip via `sync-child` / ftr merge; plan blocks inventing catalog or API here.
- **Recommendation:** Follow Stage blocked template if siblings absent at build-child.

### acceptable — estimate vs diff size

- **Location:** Estimate confirm (2 points)
- **Finding:** Product diff is one prop on an existing page; 2 points reflects sibling-merge + round-trip hand-verify, not code volume — honest for this epic slice.
- **Recommendation:** None.

context_tokens≈52000

## Review (build stub)

**Built:** `origin/sub/AST-1644/AST-1663-backstory-contexttextpage-wire-up` @ `6d60fd477a9dd95d8ae944396eb0f3e7e291c0d0`.

**Stages delivered:**
- Stage 1: Wire Backstory `plain_text` bodyShape — `6d60fd477a9dd95d8ae944396eb0f3e7e291c0d0`.

**Betty:** at **Code Complete** — cover Backstory ContextTextPage render + hydrated load, save PUT `{ context: { backstory } }` + textarea reload, `plain_text` empty-save gate (Save disabled, no PUT), and source assert for `bodyShape="plain_text"` / no `ArtifactEditor`; `ContextTextPage.tsx` / `ArtifactEditor.tsx` untouched.
