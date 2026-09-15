# Bio Summary page + route

**Linear:** [AST-1650](https://linear.app/astralcareermatch/issue/AST-1650)
**Parent:** [AST-1647](https://linear.app/astralcareermatch/issue/AST-1647) — Migrate candidate bio summary to use the artifact table and remove from candidate profile page
**Publish ref:** `sub/AST-1647/AST-1650-bio-summary-page-route`

Stand up a dedicated Bio Summary `ContextTextPage` wrapper and register its route — same thin pattern as Strengths ([AST-1634](https://linear.app/astralcareermatch/issue/AST-1634) / `CandidateStrengths.tsx`). No `ArtifactEditor`. No `ContextTextPage` edits (already parameterized for `plain_text`). No sibling context page rewrites. Nav leaf lands with config sibling [AST-1648](https://linear.app/astralcareermatch/issue/AST-1648); operative GET hydrate / PUT intercept land with [AST-1649](https://linear.app/astralcareermatch/issue/AST-1649) — both already on this epic tip after sync.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/ui/frontend/src/pages/CandidateBioSummary.tsx` — **new** thin wrapper (`contextKey="bio_summary"`, `bodyShape="plain_text"`).
- `src/ui/frontend/src/routes.tsx` — register `candidate/bio_summary`.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no `candidate.py`, no `api_candidate.py`, no `ContextTextPage.tsx`, no `ArtifactEditor.tsx`, no sibling `Candidate*.tsx` context pages, no `database.py`.

**Already on tip (do not re-invent):**

- `ContextTextPage` optional `bodyShape` + `plain_text` empty-save gate (AST-1634).
- Candidate nav item Bio Summary → `/candidate/bio_summary` (AST-1648).
- PUT `{ context: { bio_summary } }` → operative save; GET hydrate overlays current row (AST-1649).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateBioSummary.tsx` | **New** thin page: title Bio Summary, `contextKey="bio_summary"`, `bodyShape="plain_text"` | ui |
| `src/ui/frontend/src/routes.tsx` | Import + register path `candidate/bio_summary` | ui |

**Out of this ticket (do not touch):** `ContextTextPage.tsx` / `ArtifactEditor.tsx`; sibling context pages (`CandidateStrengths`, `CandidatePriorities`, …); Ada config (`config.py`); Hedy core/API; `CandidateProfile.tsx`; `tests/` / `docs/test-bible/**`.

## Stage 1: Bio Summary page + route

**Done when:** With a candidate selected, navigating to `/candidate/bio_summary` (or Candidate nav → Bio Summary) renders `ContextTextPage` with Bio Summary title; load shows hydrated `context.bio_summary` (current artifact via AST-1649, or legacy blob / empty on miss); Save PUTs `{ context: { bio_summary: <draft> } }` and reload shows the same text; empty/whitespace Save is blocked by existing `plain_text` gate (no PUT); `git diff --name-only` for this stage’s product commit is only the two Files Changed rows — `ArtifactEditor.tsx` and `ContextTextPage.tsx` untouched.

1. Create `src/ui/frontend/src/pages/CandidateBioSummary.tsx` as a Strengths twin (mirror `CandidateStrengths.tsx` exactly, swap title / key):

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function BioSummary() {
  return (
    <ContextTextPage
      title="Bio Summary"
      contextKey="bio_summary"
      bodyShape="plain_text"
    />
  )
}
```

Hardcode `bodyShape="plain_text"` to match `ARTIFACT_CONFIG["candidate.context.bio_summary"]["body_shape"]` (Ada AST-1648). Do **not** import or fetch config from the frontend. Do **not** add an `artifactKey` prop — the API leaf stays `context.bio_summary` (Hedy PUT intercept).

⚠️ **Decision:** New thin page file rather than reusing `CandidateStrengths` with props — matches every other context leaf (`CandidatePriorities`, …) and parent Component scope (`CandidateBioSummary.tsx` — **new**). Do not parameterize Strengths into a generic factory this ticket.

2. In `src/ui/frontend/src/routes.tsx`, add the import with the other Candidate page imports (immediately after the Strengths import):

```tsx
import BioSummary from "./pages/CandidateBioSummary"
```

3. In the same file, under the `// Candidate` route block, register the path immediately after `candidate/strengths`:

```tsx
          { path: "candidate/bio_summary", element: <BioSummary /> },
```

⚠️ **Decision:** Place the route next to Strengths (both `plain_text` context artifacts). Do not reorder unrelated Candidate routes. Nav path string must match AST-1648’s `NAV_CONFIG` item `"/candidate/bio_summary"` exactly.

4. Do **not** edit `ContextTextPage.tsx`, `ArtifactEditor.tsx`, any other `Candidate*.tsx` context page, or any non-frontend file. Load/save behavior is entirely the existing `ContextTextPage` contract: `GET /api/candidates/${selectedId}` → `context[contextKey]`; `PUT` body `{ context: { [contextKey]: draft } }` — bio summary rides AST-1649 intercept/hydrate with no client changes.

**Verify (hand):** with a candidate selected — open Bio Summary via nav or `/candidate/bio_summary`; edit text; Save → success toast and textarea still shows that text; refresh/re-enter → same text when a current artifact row exists (or legacy blob until first operative save); clear textarea → Save disabled / empty toast, no network PUT; confirm `ArtifactEditor.tsx` and `ContextTextPage.tsx` have no diff in this ticket’s product commit; Strengths and other context pages still compile.

## Execution contract

- Execute steps in order within the stage; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files beyond the Files Changed table, touch Ada/Hedy scopes, edit sibling context pages, or extend `ContextTextPage` / `ArtifactEditor`.
- On ambiguity or drift — stop, comment on parent AST-1647 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.ui-consistency` | pattern — read in full; plain_text → ContextTextPage; hardcode bodyShape literal; no ArtifactEditor |
| `patt.artifact.read-current` | pattern — read in full; editor opens on GET hydrate leaf (no client blob invent / second fetch) |
| `patt.artifact.write-operative` | pattern — read in full; Save keeps context-leaf PUT → AST-1649 operative intercept |

## Traceability

- Ticket / parent AC7 (dedicated editor path) → Stage 1 §§1–3 + verify
- Ticket / parent AC8 / parent AC10 (UI path purity; ArtifactEditor + ContextTextPage diffs empty) → Stage 1 §4 + Files Changed
- Parent AC8 (no backfill; legacy until re-save) → existing ContextTextPage miss path + AST-1649 hydrate (no client clear)
- Sibling freeze / other context pages → scope gate; no sibling page edits
