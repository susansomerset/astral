# Writing Preferences ContextTextPage wire-up

**Linear:** [AST-1666](https://linear.app/astralcareermatch/issue/AST-1666)
**Parent:** [AST-1645](https://linear.app/astralcareermatch/issue/AST-1645) — Migrate candidate_data.context.writing_preferences to use the artifact table
**Publish ref:** `sub/AST-1645/AST-1666-writing-preferences-contexttextpage-wire-up`

Retarget Writing Preferences-only UI load/save onto the operative API contract via existing `ContextTextPage` — same thin Strengths / Priorities / Deal Breakers / Ideal Day wire-up as [AST-1634](https://linear.app/astralcareermatch/issue/AST-1634) / [AST-1653](https://linear.app/astralcareermatch/issue/AST-1653) / [AST-1656](https://linear.app/astralcareermatch/issue/AST-1656) / [AST-1660](https://linear.app/astralcareermatch/issue/AST-1660) Stage 1, without re-parameterizing `ContextTextPage` (already done on AST-1629 / AST-1634). No `ArtifactEditor`. No sibling context page rewrites. Catalog lands with [AST-1664](https://linear.app/astralcareermatch/issue/AST-1664); operative GET hydrate / PUT intercept land with [AST-1665](https://linear.app/astralcareermatch/issue/AST-1665) — both User Testing; merge onto tip via `sync-child` / `origin/ftr/AST-1645-migrate-writing-preferences-artifact-table` (or sibling publish refs) before hand-verify.

## UAT fitness

- **AC restored:** Parent AC6 — "Editor reload — Writing Preferences page after save shows the same text. Fail: empty editor while a current artifact row exists." Parent AC9 — "UI path — Writing Preferences still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this ticket is empty. Fail: Writing Preferences routed through ArtifactEditor / resume_content."
- **Correct outcome:** With a candidate selected, Writing Preferences loads the hydrated `context.writing_preferences` string (current artifact via AST-1665, or legacy blob / empty on miss); Save keeps the same text in the textarea after success; empty/whitespace Save is refused client-side by the existing `plain_text` gate (no PUT); `ArtifactEditor.tsx` and `ContextTextPage.tsx` have zero product diff on this ticket.
- **Sibling check:** AST-1664 (`candidate.context.writing_preferences` + `plain_text` + `TOKEN_SOURCES["WRITING_PREFERENCES"]` artifact-typed) and AST-1665 (PUT intercept + GET hydrate + library SoT gate) remain authoritative — this ticket only passes `bodyShape="plain_text"` so the shared page uses the empty-save gate; load/save still ride `GET/PUT` `{ context: { writing_preferences } }`. Verify by merging sibling tips / `origin/ftr/AST-1645-migrate-writing-preferences-artifact-table` before hand-check; do not re-implement catalog or API here.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Re-editing `ContextTextPage.tsx` (already parameterized), routing Writing Preferences through `ArtifactEditor` / `resume_content`, inventing a client `artifacts` PUT slot, or clearing the leaf on miss — all violate parent Component scope and AST-1634 guidelines.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/ui/frontend/src/pages/CandidateWritingPreferences.tsx` — Writing Preferences-only wire-up against existing ContextTextPage.

Every Files Changed row and every Stage step stays inside that one file. No `config.py`, no `candidate.py`, no `api_candidate.py`, no `ContextTextPage.tsx`, no `ArtifactEditor.tsx`, no `routes.tsx`, no sibling `Candidate*.tsx` context pages, no `database.py`.

**Already on tip / sibling-owned (do not re-invent):**

- `ContextTextPage` optional `bodyShape` + `plain_text` empty-save gate (AST-1634).
- Route `candidate/writing_preferences` + nav leaf `/candidate/writing_preferences` (pre-existing; Ada AST-1664 does not own nav changes for this leaf).
- PUT `{ context: { writing_preferences } }` → operative save; GET hydrate overlays current row (AST-1665).

**Build precondition:** After `sync-child.sh`, `ARTIFACT_CONFIG` must contain `candidate.context.writing_preferences` and AST-1665 PUT/GET Writing Preferences paths must be present (via `origin/ftr/AST-1645-migrate-writing-preferences-artifact-table` or merged sibling tips `origin/sub/AST-1645/AST-1664-…` + `origin/sub/AST-1645/AST-1665-…`). If missing, stop and comment on parent AST-1645 — do not invent catalog or API intercept here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateWritingPreferences.tsx` | Pass `bodyShape="plain_text"` with existing `contextKey="writing_preferences"` | ui |

**Out of this ticket (do not touch):** `ContextTextPage.tsx` / `ArtifactEditor.tsx`; sibling context pages (`CandidateStrengths`, `CandidatePriorities`, `CandidateDealBreakers`, `CandidateIdealDay`, `CandidateBioSummary`, …); `routes.tsx`; Ada config (`config.py`); Hedy core/API; `tests/` / `docs/test-bible/**`.

## Stage 1: Wire Writing Preferences `plain_text` bodyShape

**Done when:** With a candidate selected, navigating to `/candidate/writing_preferences` (or Candidate nav → Writing Preferences) renders `ContextTextPage` with Writing Preferences title; load shows hydrated `context.writing_preferences` (current artifact via AST-1665, or legacy blob / empty on miss); Save PUTs `{ context: { writing_preferences: <draft> } }` and reload shows the same text; empty/whitespace Save is blocked by existing `plain_text` gate (no PUT); `git diff --name-only` for this stage’s product commit is only `CandidateWritingPreferences.tsx` — `ArtifactEditor.tsx` and `ContextTextPage.tsx` untouched.

1. In `src/ui/frontend/src/pages/CandidateWritingPreferences.tsx`, replace the one-liner with the Strengths twin shape (mirror `CandidateStrengths.tsx` / `CandidateIdealDay.tsx`, keep Writing Preferences title / key):

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function WritingPreferences() {
  return (
    <ContextTextPage
      title="Writing Preferences"
      contextKey="writing_preferences"
      bodyShape="plain_text"
    />
  )
}
```

Hardcode `bodyShape="plain_text"` to match `ARTIFACT_CONFIG["candidate.context.writing_preferences"]["body_shape"]` (Ada AST-1664). Do **not** import or fetch config from the frontend. Do **not** add an `artifactKey` prop — the API leaf stays `context.writing_preferences` (Hedy PUT intercept).

⚠️ **Decision:** Only add `bodyShape="plain_text"` — page, title, `contextKey`, and route already exist. Do not re-open `ContextTextPage.tsx` (parameterized on AST-1634). Do not touch `routes.tsx` or nav.

2. Do **not** edit `ContextTextPage.tsx`, `ArtifactEditor.tsx`, any other `Candidate*.tsx` context page, `routes.tsx`, or any non-frontend file. Load/save behavior is entirely the existing `ContextTextPage` contract: `GET /api/candidates/${selectedId}` → `context[contextKey]`; `PUT` body `{ context: { [contextKey]: draft } }` — writing_preferences rides AST-1665 intercept/hydrate with no client changes.

**Verify (hand):** with AST-1664 + AST-1665 on tip and a candidate selected — open Writing Preferences via nav or `/candidate/writing_preferences`; edit text; Save → success toast and textarea still shows that text; refresh/re-enter → same text when a current artifact row exists (or legacy blob until first operative save); clear textarea → Save disabled / empty toast, no network PUT; confirm `ArtifactEditor.tsx` and `ContextTextPage.tsx` have no diff in this ticket’s product commit; Strengths and other context pages still compile.

## Execution contract

- Execute steps in order within the stage; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files beyond the Files Changed table, touch Ada/Hedy scopes, edit sibling context pages, or extend `ContextTextPage` / `ArtifactEditor` / `routes.tsx`.
- On ambiguity or drift — stop, comment on parent AST-1645 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.ui-consistency` | pattern — read in full; plain_text → ContextTextPage; hardcode bodyShape literal; no ArtifactEditor |
| `patt.artifact.read-current` | pattern — read in full; editor opens on GET hydrate leaf (no client blob invent / second fetch) |
| `patt.artifact.write-operative` | pattern — read in full; Save keeps context-leaf PUT → AST-1665 operative intercept |

## Traceability

- Ticket / parent AC6 (editor reload) → Stage 1 §§1–2 + verify
- Ticket AC7 / parent AC9 (UI path; ArtifactEditor untouched) → Stage 1 §2 + Files Changed
- Parent AC7 (no backfill; legacy until re-save) → existing ContextTextPage miss path + AST-1665 hydrate (no client clear)
- Sibling freeze / other context pages → scope gate; no sibling page edits
- Parent AC1–5 / AC8 → N/A (AST-1664 / AST-1665)

## Review (build stub)

**Built:** `origin/sub/AST-1645/AST-1666-writing-preferences-contexttextpage-wire-up` @ `b5d1172b63c456c409d0eb0a9c203b9da3d25ae3`.

**Stages delivered:**
- Stage 1: Writing Preferences `plain_text` bodyShape — `b5d1172b63c456c409d0eb0a9c203b9da3d25ae3`.

**Betty:** at **Code Complete** — cover Writing Preferences ContextTextPage render + hydrated load, save PUT `{ context: { writing_preferences } }` + textarea reload, `plain_text` empty-save gate (Save disabled, no PUT), and source assert for `bodyShape="plain_text"` / no `ArtifactEditor`; `ContextTextPage.tsx` / `ArtifactEditor.tsx` untouched.

## Joan validate

[plan-rubric]
**Ticket:** AST-1666
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1645/AST-1666-writing-preferences-contexttextpage-wire-up` @ `0e7876182bfe0081e9d8851f55b924fd03101b8b`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.ui-consistency | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.write-operative | A | | |

## Traceability

AC6→S1§§1-2+verify; AC7→S1§§1-2+Files Changed — parent AC1–5/AC8 N/A (AST-1664/AST-1665); parent AC7 no-backfill via ContextTextPage miss path + AST-1665 hydrate (no client clear).

## Findings

### discuss

- **Location:** Linear assignee at fetch
- **Finding:** Assignee is Katherine Johnson, not Joan — validate-plan §1 expects Joan assigned before this pass.
- **Recommendation:** Chuckles assign Joan before status flip; restore Katherine after writeback per §8. Substance review completed below.

### R6 — Definition fidelity (checklist)

- Single-file scope (`CandidateWritingPreferences.tsx`); explicit scope gate; build precondition on AST-1664 + AST-1665 (both satisfied on tip).
- Correct delta vs tip: add `bodyShape="plain_text"` to mirror `CandidateStrengths.tsx` / `CandidateIdealDay.tsx`; keeps `contextKey="writing_preferences"` and existing PUT `{ context: { writing_preferences } }` contract AST-1665 intercepts.
- UAT fitness names AC6/AC7 (parent AC6/AC9), correct outcome vs stacktrace-only fix, rejects ArtifactEditor / `ContextTextPage` edits / parallel `artifacts` payload / client catalog fetch.
- `ContextTextPage` on tip already supports `bodyShape` empty-save gate and context-leaf PUT — plan does not over-scope.
- Self-assessment `Confirm Chuckles estimate: 2 — agree` is defensible (thin change + hand-verify + sibling compile check).
- Plan Discuss rounds completed: **0**.

context_tokens≈62000

## Radia review

[code-rubric]
**Ticket:** AST-1666
**Publish ref:** `87400633b8cf7a16e065c8985d50b236c3d0772d`
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.ui-consistency | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.write-operative | A | | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### discuss

- **Publish-ref three-dot diff vs ticket scope gate.** `origin/dev...origin/sub/AST-1645/AST-1666-writing-preferences-contexttextpage-wire-up` is 15 files / ~1164 lines; AST-1666 engineer commit `b5d1172b` touches only `src/ui/frontend/src/pages/CandidateWritingPreferences.tsx` (+9/−1). The wider diff carries prerequisite **AST-1664** catalog + **AST-1665** operative/API work (and their Betty `merge-tests` commits) stacked beneath this UI child — expected on a `blockedBy` epic tip after `sync-child` / ftr merge, not Katherine scope creep. Chuckles should note at merge-child that the three-dot diff is wider than the one-file explicit gate.

### advisory

- **blockedBy prerequisites satisfied on tip:** `candidate.context.writing_preferences` catalog + `WRITING_PREFERENCES` artifact token (AST-1664) and PUT intercept / GET hydrate (AST-1665) are present on the publish ref; the UI wire-up correctly defers to those siblings with no client catalog fetch or API reimplementation.

## What's solid

- Stage 1 delivers the planned delta verbatim: `CandidateWritingPreferences.tsx` mirrors `CandidateStrengths.tsx` / `CandidateIdealDay.tsx` — adds hardcoded `bodyShape="plain_text"` alongside existing `title="Writing Preferences"` and `contextKey="writing_preferences"`; `ContextTextPage.tsx` and `ArtifactEditor.tsx` have zero product diff on this branch.
- **patt.artifact.ui-consistency:** plain_text context leaf routes through shared `ContextTextPage`, not `ArtifactEditor` / `resume_content`.
- **patt.artifact.read-current:** load uses existing `GET /api/candidates/${selectedId}` → `context.writing_preferences` (hydrated by AST-1665); no client blob invent or second fetch.
- **patt.artifact.write-operative:** save uses existing `PUT { context: { writing_preferences: draft } }` contract (AST-1665 intercept); `plain_text` empty-save gate blocks whitespace-only PUT client-side.
- Betty Vitest (`test_CandidateWritingPreferences.test.tsx`) covers render + hydrated load, save PUT + textarea reload, empty gate (Save disabled, no PUT), and source asserts for `bodyShape="plain_text"` / no `ArtifactEditor`; integration correctly none.

## Recommended actions

- Chuckles: append artifact, `docs(AST-1666): Radia review — clean`, post slim upshot, → **Review Posted** → datt **PROCEED** to User Testing (parent AST-1645 last child on this wave).

context_tokens≈68000
