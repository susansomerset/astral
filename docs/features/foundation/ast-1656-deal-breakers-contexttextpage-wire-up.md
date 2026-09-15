# Deal Breakers ContextTextPage wire-up

**Linear:** [AST-1656](https://linear.app/astralcareermatch/issue/AST-1656)
**Parent:** [AST-1642](https://linear.app/astralcareermatch/issue/AST-1642) — Migrate candidate_data.context.deal_breakers to use the artifact table
**Publish ref:** `sub/AST-1642/AST-1656-deal-breakers-contexttextpage-wire-up`

Retarget Deal Breakers-only UI load/save onto the operative API contract via existing `ContextTextPage` — same thin Strengths wire-up as [AST-1634](https://linear.app/astralcareermatch/issue/AST-1634) Stage 1 §5, without re-parameterizing `ContextTextPage` (already done on AST-1629 / AST-1634). No `ArtifactEditor`. No sibling context page rewrites. Catalog lands with [AST-1654](https://linear.app/astralcareermatch/issue/AST-1654); operative GET hydrate / PUT intercept land with [AST-1655](https://linear.app/astralcareermatch/issue/AST-1655) — both User Testing; merge onto tip via `sync-child` / `origin/ftr/AST-1642` (or sibling publish refs) before hand-verify.

## UAT fitness

- **AC restored:** Parent AC6 — "Editor reload — Deal Breakers page after save shows the same text. Fail: empty editor while a current artifact row exists." Parent AC9 — "UI path — Deal Breakers still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this ticket is empty. Fail: ArtifactEditor changed or Deal Breakers routed through resume_content editor."
- **Correct outcome:** With a candidate selected, Deal Breakers loads the hydrated `context.deal_breakers` string (current artifact via AST-1655, or legacy blob / empty on miss); Save keeps the same text in the textarea after success; empty/whitespace Save is refused client-side by the existing `plain_text` gate (no PUT); `ArtifactEditor.tsx` and `ContextTextPage.tsx` have zero product diff on this ticket.
- **Sibling check:** AST-1654 (`candidate.context.deal_breakers` + `plain_text` + `TOKEN_SOURCES["DEAL_BREAKERS"]` artifact-typed) and AST-1655 (PUT intercept + GET hydrate + library SoT gate) remain authoritative — this ticket only passes `bodyShape="plain_text"` so the shared page uses the empty-save gate; load/save still ride `GET/PUT` `{ context: { deal_breakers } }`. Verify by merging sibling tips / `origin/ftr/AST-1642` before hand-check; do not re-implement catalog or API here.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Re-editing `ContextTextPage.tsx` (already parameterized), routing Deal Breakers through `ArtifactEditor` / `resume_content`, inventing a client `artifacts` PUT slot, or clearing the leaf on miss — all violate parent Component scope and AST-1634 guidelines.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/ui/frontend/src/pages/CandidateDealBreakers.tsx` — Deal Breakers-only wire-up against existing ContextTextPage.

Every Files Changed row and every Stage step stays inside that one file. No `config.py`, no `candidate.py`, no `api_candidate.py`, no `ContextTextPage.tsx`, no `ArtifactEditor.tsx`, no `routes.tsx`, no sibling `Candidate*.tsx` context pages, no `database.py`.

**Already on tip / sibling-owned (do not re-invent):**

- `ContextTextPage` optional `bodyShape` + `plain_text` empty-save gate (AST-1634).
- Route `candidate/deal_breakers` + nav leaf `/candidate/deal_breakers` (pre-existing; Ada AST-1654 does not own nav changes for this leaf).
- PUT `{ context: { deal_breakers } }` → operative save; GET hydrate overlays current row (AST-1655).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateDealBreakers.tsx` | Pass `bodyShape="plain_text"` with existing `contextKey="deal_breakers"` | ui |

**Out of this ticket (do not touch):** `ContextTextPage.tsx` / `ArtifactEditor.tsx`; sibling context pages (`CandidateStrengths`, `CandidatePriorities`, `CandidateBioSummary`, …); `routes.tsx`; Ada config (`config.py`); Hedy core/API; `tests/` / `docs/test-bible/**`.

## Stage 1: Wire Deal Breakers `plain_text` bodyShape

**Done when:** With a candidate selected, navigating to `/candidate/deal_breakers` (or Candidate nav → Deal Breakers) renders `ContextTextPage` with Deal Breakers title; load shows hydrated `context.deal_breakers` (current artifact via AST-1655, or legacy blob / empty on miss); Save PUTs `{ context: { deal_breakers: <draft> } }` and reload shows the same text; empty/whitespace Save is blocked by existing `plain_text` gate (no PUT); `git diff --name-only` for this stage’s product commit is only `CandidateDealBreakers.tsx` — `ArtifactEditor.tsx` and `ContextTextPage.tsx` untouched.

1. In `src/ui/frontend/src/pages/CandidateDealBreakers.tsx`, replace the one-liner with the Strengths twin shape (mirror `CandidateStrengths.tsx`, keep Deal Breakers title / key):

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function DealBreakers() {
  return (
    <ContextTextPage
      title="Deal Breakers"
      contextKey="deal_breakers"
      bodyShape="plain_text"
    />
  )
}
```

Hardcode `bodyShape="plain_text"` to match `ARTIFACT_CONFIG["candidate.context.deal_breakers"]["body_shape"]` (Ada AST-1654). Do **not** import or fetch config from the frontend. Do **not** add an `artifactKey` prop — the API leaf stays `context.deal_breakers` (Hedy PUT intercept).

⚠️ **Decision:** Only add `bodyShape="plain_text"` — page, title, `contextKey`, and route already exist. Do not re-open `ContextTextPage.tsx` (parameterized on AST-1634). Do not touch `routes.tsx` or nav.

2. Do **not** edit `ContextTextPage.tsx`, `ArtifactEditor.tsx`, any other `Candidate*.tsx` context page, `routes.tsx`, or any non-frontend file. Load/save behavior is entirely the existing `ContextTextPage` contract: `GET /api/candidates/${selectedId}` → `context[contextKey]`; `PUT` body `{ context: { [contextKey]: draft } }` — deal_breakers rides AST-1655 intercept/hydrate with no client changes.

**Verify (hand):** with AST-1654 + AST-1655 on tip and a candidate selected — open Deal Breakers via nav or `/candidate/deal_breakers`; edit text; Save → success toast and textarea still shows that text; refresh/re-enter → same text when a current artifact row exists (or legacy blob until first operative save); clear textarea → Save disabled / empty toast, no network PUT; confirm `ArtifactEditor.tsx` and `ContextTextPage.tsx` have no diff in this ticket’s product commit; Strengths and other context pages still compile.

## Execution contract

- Execute steps in order within the stage; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files beyond the Files Changed table, touch Ada/Hedy scopes, edit sibling context pages, or extend `ContextTextPage` / `ArtifactEditor` / `routes.tsx`.
- On ambiguity or drift — stop, comment on parent AST-1642 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.ui-consistency` | pattern — read in full; plain_text → ContextTextPage; hardcode bodyShape literal; no ArtifactEditor |
| `patt.artifact.read-current` | pattern — read in full; editor opens on GET hydrate leaf (no client blob invent / second fetch) |
| `patt.artifact.write-operative` | pattern — read in full; Save keeps context-leaf PUT → AST-1655 operative intercept |

## Traceability

- Ticket / parent AC6 (editor reload) → Stage 1 §§1–2 + verify
- Ticket AC7 / parent AC9 (UI path; ArtifactEditor untouched) → Stage 1 §2 + Files Changed
- Parent AC7 (no backfill; legacy until re-save) → existing ContextTextPage miss path + AST-1655 hydrate (no client clear)
- Sibling freeze / other context pages → scope gate; no sibling page edits
- Parent AC1–5 / AC8 → N/A (AST-1654 / AST-1655)

## Joan validate

[plan-rubric]
**Ticket:** AST-1656
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** 667eceb71272ec99d7a8b5fe0dd00c53aa9d5c32

## Canon scores

patt.artifact.ui-consistency | A | | `bodyShape="plain_text"` hardcoded on Deal Breakers page; ContextTextPage path; ArtifactEditor untouched
patt.artifact.read-current | A | | Existing GET → `context.deal_breakers` leaf; no second fetch; no client clear on miss
patt.artifact.write-operative | A | | Save keeps `{ context: { deal_breakers: draft } }` PUT; AST-1655 intercept owns operative write

## Traceability

AC6→S1·1-2+verify | AC7/parent AC9→S1·1-2+Files Changed | parent AC7→ContextTextPage miss path+AST-1655 hydrate (no client change) | parent AC1-5,AC8→N/A (siblings #1/#2)

## Findings

### acceptable (procedural)

- **Location:** Linear assignee
- **Finding:** Ticket is **Plan Ready** with assignee **Katherine**; validate-plan §1 expects Joan assigned at spawn.
- **Recommendation:** Chuckles procedural hygiene only — does not block plan substance.

### acceptable

- **Location:** `CandidateDealBreakers.tsx` as-is on tip
- **Finding:** Page omits `bodyShape="plain_text"` today (one-liner without prop); without this change, empty Save can reach PUT and fail operative validation post-AST-1655. Plan's sole delta closes that gap.
- **Recommendation:** No plan revision; implement Stage 1 verbatim.

### acceptable

- **Location:** Build / hand-verify prerequisite
- **Finding:** Plan requires AST-1654 + AST-1655 on tip (via `sync-child` / ftr merge) before hand-check — correct ordering for editor-reload AC.
- **Recommendation:** Chuckles merge-child before Katherine hand-verify; no plan change.

### discuss

- **Location:** `## Estimate`
- **Finding:** Confirm line agrees to **2** points for a single-file, ~6-line mirror of AST-1634 Stage 1 §5 (Strengths already parameterized ContextTextPage on AST-1634).
- **Recommendation:** Acceptable if parent dispatch estimate is authoritative; optional Chuckles note that product diff is trivial — not a plan blocker.

### acceptable

- **Location:** Canon clerk resolution
- **Finding:** `patt.artifact.ui-consistency` is draft under `canon/directives/draft/`; scored from repo file, not `canon_clerk expand` active payload.
- **Recommendation:** Corpus hygiene downstream; grades cite draft pattern Arc/Implementation.

## R6 checklist (summary)

Definition fidelity: pass — single-file scope gate; mirrors AST-1634 Strengths twin exactly; does not re-open ContextTextPage / ArtifactEditor / routes.
DRY / scope: pass — reuses parameterized ContextTextPage; defers catalog/API to siblings; no sibling context page edits.
UAT fitness: pass — cites parent AC6/AC9, correct outcome vs symptom-only fix, sibling partition, wrong-fix rejection.
Self-assessment: pass — Estimate confirm present; no `!!-NONE` conf gap; complexity honestly bounded to one prop addition.

context_tokens≈88000

## Review (build stub)

**Built:** `origin/sub/AST-1642/AST-1656-deal-breakers-contexttextpage-wire-up` @ `62bbf1ff826437a8580a912ddec066d298f9ece3`.

**Stages delivered:**
- Stage 1: Wire Deal Breakers `plain_text` bodyShape — `62bbf1ff826437a8580a912ddec066d298f9ece3`.

**Notes:** Product diff is only `CandidateDealBreakers.tsx` (`bodyShape="plain_text"`). `ContextTextPage.tsx` / `ArtifactEditor.tsx` untouched. Hand-verify of editor reload (parent AC6) still needs AST-1654 + AST-1655 on tip (`origin/ftr/AST-1642` was absent at sync).

## Radia review

[code-rubric]
**Ticket:** AST-1656
**Publish ref:** 9462861853341ea4135479c0017f03e3451c4332
**Corpus:** 4a0e30e37a6c5898021b2e5718787edfb1b6c37a · `canon_clerk expand` unknown for frozen pattern ids under `canon/directives/draft/`; scored from repo files at publish tip
**Overall:** CLEAN

## Canon scores

patt.artifact.ui-consistency | A | | `bodyShape="plain_text"` hardcoded on Deal Breakers page; ContextTextPage path; mirrors `CandidateStrengths.tsx`; no frontend catalog fetch; `ArtifactEditor` untouched
patt.artifact.read-current | A | | Existing GET → `context.deal_breakers` leaf via `ContextTextPage`; no second fetch; no client clear on miss
patt.artifact.write-operative | A | | Save keeps `{ context: { deal_breakers: draft } }` PUT; client `plain_text` empty gate before PUT; AST-1655 intercept owns operative write

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### advisory

- **Location:** `patt.artifact.ui-consistency` / `ContextTextPage`
- **Finding:** Pattern prose is ArtifactEditor / `artifacts[leaf]`-centric; this diff correctly applies the same `bodyShape` hardcode pattern to `ContextTextPage` with `context[contextKey]` leaf per parent Technical scope and AST-1655 API intercept — not a parallel client slot.
- **Recommendation:** None — definition-faithful; mirrors AST-1634 precedent.

### advisory

- **Location:** Build stub / UAT prerequisite
- **Finding:** Parent AC6 editor-reload hand-verify still depends on AST-1654 catalog + AST-1655 operative hydrate/PUT on integrated ftr tip; build stub notes `origin/ftr/AST-1642` was absent at sync. Product change here is correct and sufficient for this ticket’s scope.
- **Recommendation:** Downstream: `merge-child` / ftr integration before parent UAT; not a resolve-child item on AST-1656 alone.

### advisory

- **Location:** `## Estimate` (Joan carry-forward)
- **Finding:** Confirm line agrees to **2** points for a single-file ~6-line mirror of AST-1634 Stage 1 §5 (Strengths twin).
- **Recommendation:** Acceptable if parent dispatch estimate is authoritative; optional Chuckles note that product diff is trivial — not a plan blocker.

### advisory

- **Location:** Canon clerk / frozen list
- **Finding:** Three frozen pattern ids live under `canon/directives/draft/` outside clerk `active/` roster; scored from draft files at epic worktree.
- **Recommendation:** Corpus hygiene downstream; scores from those files' Arc/Implementation.

## What's solid

- Stage 1 plan delivered verbatim in `62bbf1ff`: `CandidateDealBreakers.tsx` matches `CandidateStrengths.tsx` twin — `title="Deal Breakers"`, `contextKey="deal_breakers"`, `bodyShape="plain_text"`.
- Product commit touches only `src/ui/frontend/src/pages/CandidateDealBreakers.tsx`; `ContextTextPage.tsx`, `ArtifactEditor.tsx`, `routes.tsx`, backend files untouched on `src/**` three-dot diff.
- Betty coverage is tight: `test_CandidateDealBreakers.test.tsx` — render/load, PUT `{ context: { deal_breakers } }` + reload, empty Save disabled (no PUT), source asserts hardcoded `bodyShape="plain_text"` and no `ArtifactEditor`.
- Ticket AC7 / parent AC9 satisfied: Deal Breakers stays on ContextTextPage thin wrapper; ArtifactEditor diff empty.

## Scope notes (not findings)

- Three-dot diff vs `origin/dev` also includes `merge-tests` sibling artifacts (`test_candidate.py`, `test_api_candidate.py`, `test_config.py`, test-bible rows for AST-1654/1655/1652/1658, etc.); **`src/**` product surface is only `CandidateDealBreakers.tsx`.**
- `tests/` and `docs/test-bible/**` changes are expected Betty / test-child pipeline artifacts.
- Estimate **2** fits single-page wire-up + frontend component tests (Joan discuss on triviality is procedural, not a canon miss).

## Recommended actions

- Chuckles: append artifact, commit `docs(AST-1656): Radia review — clean`, post slim upshot, move to **Review Posted**.
- datt: **PROCEED** → **User Testing** (no resolve-child round needed).
- Downstream: ensure AST-1654 + AST-1655 land on ftr before parent AC6 hand-verify.

---
