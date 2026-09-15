# Priorities ContextTextPage wire-up

**Linear:** [AST-1653](https://linear.app/astralcareermatch/issue/AST-1653)
**Parent:** [AST-1641](https://linear.app/astralcareermatch/issue/AST-1641) — Migrate candidate_data.context.priorities to use the artifact table
**Publish ref:** `sub/AST-1641/AST-1653-priorities-contexttextpage-wire-up`

Retarget Priorities-only UI load/save onto the operative API contract by passing `bodyShape="plain_text"` into the existing `ContextTextPage` (parameterized in AST-1634). No `ContextTextPage` edits. No `ArtifactEditor`. No sibling context pages. Depends on catalog [AST-1651](https://linear.app/astralcareermatch/issue/AST-1651) and operative/API hydrate [AST-1652](https://linear.app/astralcareermatch/issue/AST-1652) (both User Testing; merge via `sync-child` / `origin/ftr` when published).

## UAT fitness

- **AC restored:** Parent AC6 / child AC6 — Priorities page after save shows the same text. Parent AC9 / child AC7 — Priorities still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this ticket is empty.
- **Correct outcome:** With a candidate selected, Priorities loads the hydrated `candidate_data.context.priorities` string (current artifact via AST-1652 GET hydrate, or legacy blob / empty on miss); Save PUTs `{ context: { priorities: <draft> } }`; after save (and on re-enter) the textarea shows that same text; empty/whitespace Save is blocked client-side by the existing `plain_text` gate (no PUT).
- **Sibling check:** AST-1651 catalog key + `plain_text` shape + `TOKEN_SOURCES["PRIORITIES"]` artifact typing remain authoritative (config untouched here). AST-1652 PUT intercept + GET hydrate remain the server contract — this ticket only opts Priorities into `bodyShape="plain_text"` so empty-save mirrors operative validation. Strengths / Bio Summary `ContextTextPage` callers still pass their own `bodyShape`; legacy context pages that omit it stay unchanged. Verified by product diff limited to `CandidatePriorities.tsx` and by hand-checking sibling pages still compile.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done — editor reload must show the saved Priorities text when a current artifact row exists.
- **Wrong fix rejected:** Routing Priorities through `ArtifactEditor` / `resume_content` fails parent AC9. Editing `ContextTextPage.tsx` invents out-of-scope wiring (ticket Boundaries: already from AST-1629). Inventing a parallel client `artifacts` / `artifact_id` payload breaks the AST-1652 intercept contract.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/ui/frontend/src/pages/CandidatePriorities.tsx` — Priorities-only wire-up against existing ContextTextPage.

Every Files Changed row and every Stage step stays inside that one file. No `ContextTextPage.tsx` (Boundaries: untouched). No `ArtifactEditor.tsx`. No sibling `Candidate*.tsx` context pages. No `config.py`, no `candidate.py`, no `api_candidate.py`, no `database.py`, no routes/nav.

**Already on tip / sibling-owned (do not re-invent):**

- `ContextTextPage` optional `bodyShape` + `plain_text` empty-save gate (AST-1634).
- PUT `{ context: { priorities } }` → operative save; GET hydrate overlays current row (AST-1652).
- Catalog `candidate.context.priorities` + `body_shape: plain_text` (AST-1651).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidatePriorities.tsx` | Pass `bodyShape="plain_text"` with existing `contextKey="priorities"` | ui |

**Out of this ticket (do not touch):** `ContextTextPage.tsx`; `ArtifactEditor.tsx`; sibling context pages; Ada config (`config.py`); Hedy core/API; `tests/` / `docs/test-bible/**`.

**Build precondition:** After `sync-child.sh`, `ARTIFACT_CONFIG` must contain `candidate.context.priorities` and AST-1652 PUT/GET Priorities paths must be present (via `origin/ftr/AST-1641` or merged sibling tips). If missing, stop and comment on parent AST-1641 — do not invent catalog or API intercept here.

## Stage 1: Wire Priorities `bodyShape="plain_text"`

**Done when:** Priorities page loads hydrated `candidate_data.context.priorities` (current artifact via AST-1652, or legacy blob / empty on miss); Save PUTs `{ context: { priorities: <draft> } }` and reload shows the same text; empty/whitespace Save is blocked by existing `plain_text` gate (no PUT); `git diff --name-only` for this stage’s product commit is only `CandidatePriorities.tsx` — `ArtifactEditor.tsx` and `ContextTextPage.tsx` untouched.

1. Replace `src/ui/frontend/src/pages/CandidatePriorities.tsx` with the Strengths twin (mirror `CandidateStrengths.tsx` / `CandidateBioSummary.tsx`, swap title / key):

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function Priorities() {
  return (
    <ContextTextPage
      title="Priorities"
      contextKey="priorities"
      bodyShape="plain_text"
    />
  )
}
```

Hardcode `bodyShape="plain_text"` to match `ARTIFACT_CONFIG["candidate.context.priorities"]["body_shape"]` (Ada AST-1651). Do **not** import or fetch config from the frontend. Do **not** add an `artifactKey` prop — the API leaf stays `context.priorities` (Hedy PUT intercept).

⚠️ **Decision:** Only pass `bodyShape` — load/save stay on the existing context-leaf contract that AST-1652 intercepts into `save_candidate_data(candidate_id, "candidate.context.priorities", body)`. Switching the client to an `artifacts` payload would invent a parallel slot and break the sibling API contract. Do not edit `ContextTextPage.tsx` (ticket Boundaries).

2. Do **not** edit `ContextTextPage.tsx`, `ArtifactEditor.tsx`, any other `Candidate*.tsx` context page, routes, nav, or any non-frontend file. Verify by hand (or `git diff --name-only`) that this stage’s product diff is only the Files Changed row.

**Verify (hand):** with a candidate selected — open Priorities, edit text, Save → toast success and textarea still shows that text; refresh/re-enter → same text when a current artifact row exists (or legacy blob until first operative save); clear textarea → Save disabled / empty toast, no network PUT; confirm `ArtifactEditor.tsx` and `ContextTextPage.tsx` have no diff in this ticket’s product commit; Strengths and other context pages still compile.

## Execution contract

- Execute steps in order within the stage; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files beyond the Files Changed table, touch Ada/Hedy scopes, edit sibling context pages, or extend `ContextTextPage` / `ArtifactEditor`.
- On ambiguity or drift — stop, comment on parent AST-1641 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree
