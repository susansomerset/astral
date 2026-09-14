# Strengths ContextTextPage plain-text path

**Linear:** [AST-1634](https://linear.app/astralcareermatch/issue/AST-1634)
**Parent:** [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629) — Migrate candidate_data.context.strengths to use the artifact table
**Publish ref:** `sub/AST-1629/AST-1634-strengths-contexttextpage-plain-text-path`

Retarget Strengths-only UI load/save onto the operative API contract via `ContextTextPage` as the shared plain-text artifact editor (`body_shape: plain_text`). Parameterize the shared component the same way `ArtifactEditor` takes `bodyShape` for `resume_content` — without extending `ArtifactEditor`, without touching sibling context pages, and without inventing a parallel client storage key. Depends on catalog [AST-1632](https://linear.app/astralcareermatch/issue/AST-1632) and operative/API [AST-1633](https://linear.app/astralcareermatch/issue/AST-1633) (both already on `origin/ftr`).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/ui/frontend/src/pages/CandidateStrengths.tsx` — Strengths-only wire-up.
- `src/ui/frontend/src/components/ContextTextPage.tsx` — plain-text artifact editor parameterization.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no `candidate.py`, no `api_candidate.py`, no `ArtifactEditor.tsx`, no sibling context pages (`CandidatePriorities`, `CandidateDealBreakers`, …), no `database.py`, no other context leaves, no frontend catalog fetch.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ContextTextPage.tsx` | Optional `bodyShape` prop; when `"plain_text"`, keep context-leaf GET/PUT contract (operative hydrate/save on server) and refuse empty save client-side | ui |
| `src/ui/frontend/src/pages/CandidateStrengths.tsx` | Pass `bodyShape="plain_text"` with existing `contextKey="strengths"` | ui |

**Out of this ticket (do not touch):** `ArtifactEditor.tsx`; sibling `Candidate*.tsx` context pages; Ada/Hedy scopes; `tests/` / `docs/test-bible/**`.

## Stage 1: Parameterize ContextTextPage + wire Strengths

**Done when:** Strengths page loads the hydrated `candidate_data.context.strengths` string (current artifact via AST-1633 GET hydrate, or legacy blob on miss); Save PUTs `{ context: { strengths: <draft> } }` and the PUT response (or a fresh GET) shows the same text in the textarea; empty/whitespace Save is blocked client-side with an error toast and no PUT; `ArtifactEditor.tsx` is unmodified; sibling context pages still compile and behave as before (they omit `bodyShape`).

1. In `src/ui/frontend/src/components/ContextTextPage.tsx`, extend the props interface:

```tsx
interface ContextTextPageProps {
  title: string
  contextKey: string
  /** Catalog body_shape (ARTIFACT_CONFIG / BUILD_CONFIG artifact_shapes). Strengths: plain_text. Omit for legacy blob context pages. AST-1634 / patt.artifact.ui-consistency */
  bodyShape?: string
}
```

Destructure `bodyShape` on the component (default undefined). Do **not** add an `artifactKey` prop — for plain_text the API leaf slot remains `context[contextKey]` (Hedy PUT intercept), not `artifacts[…]`.

⚠️ **Decision:** Optional `bodyShape` only — siblings keep calling with `title` + `contextKey` and stay on the legacy library-merge path. Strengths is the first caller that passes `"plain_text"`. No frontend `ARTIFACT_CONFIG` fetch (same pilot rule as base_resume `bodyShape="resume_content"`).

2. Keep the existing load path unchanged in behavior: `GET /api/candidates/${selectedId}` → `coerceToString(c.candidate_data?.context?.[contextKey])` into `saved`/`draft`. When AST-1633 hydrate has a current Strengths row, that leaf is already the operative string; on miss, legacy blob (or empty) remains — do not add a second client fetch or clear the leaf on empty.

3. Keep the existing save payload shape for every caller, including `bodyShape === "plain_text"`:

```tsx
body: JSON.stringify({ context: { [contextKey]: draft } }),
```

Do **not** PUT under `artifacts`. Do **not** invent a client-side `artifact_id`. After a successful response, set `saved`/`draft` from `coerceToString(c.candidate_data?.context?.[contextKey]) || draft` (existing fallback) so editor reload matches parent AC6 / this ticket AC6.

⚠️ **Decision:** Strengths stays on the context-leaf API contract that AST-1633 intercepts into `save_candidate_data(candidate_id, "candidate.context.strengths", body)`. Switching the client to an `artifacts` payload would invent a parallel slot and break the sibling API contract.

4. When `bodyShape === "plain_text"`, refuse empty/whitespace saves before calling `api`:

```tsx
function handleSave() {
  /* v8 ignore next -- @preserve */
  if (!selectedId) return
  if (bodyShape === "plain_text" && !draft.trim()) {
    setToast({ text: `${title} cannot be empty`, variant: "error" })
    return
  }
  // existing PUT unchanged…
}
```

Also disable the primary Save button when `bodyShape === "plain_text" && !draft.trim()` (Cancel stays enabled). Callers without `bodyShape` keep today’s empty-save behavior (library merge).

⚠️ **Decision:** Client-side empty gate mirrors AST-1633 operative validation (`plain_text` must be a non-empty string) and `patt.artifact.write-operative` “skip write when empty” — avoid a guaranteed 400 toast for blank Strengths saves. Do not special-case other context keys.

5. In `src/ui/frontend/src/pages/CandidateStrengths.tsx`, pass the catalog shape literal:

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function Strengths() {
  return (
    <ContextTextPage
      title="Strengths"
      contextKey="strengths"
      bodyShape="plain_text"
    />
  )
}
```

Hardcode `bodyShape="plain_text"` to match `ARTIFACT_CONFIG["candidate.context.strengths"]["body_shape"]` (Ada AST-1632). Do not import or fetch config from the frontend.

6. Do **not** edit `ArtifactEditor.tsx`, any other `Candidate*.tsx` context page, or any non-frontend file. Verify by hand (or `git diff --name-only`) that this stage’s product diff is only the two Files Changed rows.

**Verify (hand):** with a candidate selected — open Strengths, edit text, Save → toast success and textarea still shows that text; refresh/re-enter page → same text when a current artifact row exists; clear textarea → Save disabled / empty toast, no network PUT; open Priorities (or another context page) → still loads/saves without `bodyShape`.

## Execution contract

- Execute steps in order within the stage; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Hedy scopes, edit sibling context pages, or extend `ArtifactEditor`.
- On ambiguity or drift — stop, comment on parent AST-1629 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.ui-consistency` | pattern — read in full; parameterize editor by `body_shape`; plain_text → ContextTextPage |
| `patt.artifact.read-current` | pattern — read in full; editor opens on GET hydrate leaf (no stale client blob invent) |
| `patt.artifact.write-operative` | pattern — read in full; Save goes through existing API contract that lands operative rows |

## Traceability

- Parent/child AC6 (editor reload) → Stage 1 §§2–3 + verify
- Parent/child AC7 / parent AC9 (UI path; ArtifactEditor untouched) → Stage 1 §§1, 5–6
- Parent AC7 (no backfill; legacy until re-save) → Stage 1 §2 miss path (hydrate leaves blob)
- Sibling freeze / other context pages → scope gate; no sibling page edits

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1634
**Overall:** APPROVED
**Corpus:** 0b920f4e7dfc842c1032277aa99ac34e1bd0f9b9
**Publish ref tip:** 4ee246c14722f591c99ab654ad27dbd08167fde0

## Canon scores

patt.artifact.ui-consistency | A | | Optional `bodyShape` on ContextTextPage; Strengths hardcodes `plain_text`; mirrors ArtifactEditor pilot pattern; no frontend catalog fetch; ArtifactEditor untouched
patt.artifact.read-current | A | | Single GET load from hydrated `context[contextKey]`; no client artifact_id or second fetch; miss leaves legacy blob per parent AC7
patt.artifact.write-operative | A | | Save keeps `{ context: { strengths } }` PUT → AST-1633 operative intercept; client empty gate before PUT matches server plain_text validation

## Traceability

AC6→Stage 1 §§2–3 + verify (save/reload same text); AC7→Stage 1 §§1, 5–6 (ContextTextPage only; ArtifactEditor diff empty); parent AC7→Stage 1 §2 miss path; parent AC9→scope gate + §6 (sibling pages omit `bodyShape`).

## Findings

### acceptable

- **Location:** Stage 1 §1 / `patt.artifact.ui-consistency`
- **Finding:** Pattern prose is ArtifactEditor/`artifacts[leaf]`-centric; this plan correctly applies the same `bodyShape` parameterization to ContextTextPage with `context[contextKey]` leaf per parent Technical scope and AST-1633 API intercept — not a parallel client slot.
- **Recommendation:** None — definition-faithful; pattern Abstract allows existing API leaf contracts.

### acceptable

- **Location:** Canon clerk
- **Finding:** Three frozen pattern ids live under `canon/directives/draft/` outside clerk `active/` roster; scored from draft files at epic worktree.
- **Recommendation:** No plan change.

context_tokens≈45000
```

