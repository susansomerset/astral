# Ideal Day ContextTextPage wire-up

**Linear:** [AST-1660](https://linear.app/astralcareermatch/issue/AST-1660)
**Parent:** [AST-1643](https://linear.app/astralcareermatch/issue/AST-1643) — Migrate candidate_data.context.ideal_day to use the artifact table
**Publish ref:** `sub/AST-1643/AST-1660-ideal-day-contexttextpage-wire-up`

Retarget Ideal Day-only UI load/save onto the operative API contract via existing `ContextTextPage` — same thin Strengths / Priorities / Deal Breakers wire-up as [AST-1634](https://linear.app/astralcareermatch/issue/AST-1634) / [AST-1653](https://linear.app/astralcareermatch/issue/AST-1653) / [AST-1656](https://linear.app/astralcareermatch/issue/AST-1656) Stage 1, without re-parameterizing `ContextTextPage` (already done on AST-1629 / AST-1634). No `ArtifactEditor`. No sibling context page rewrites. Catalog lands with [AST-1658](https://linear.app/astralcareermatch/issue/AST-1658); operative GET hydrate / PUT intercept land with [AST-1659](https://linear.app/astralcareermatch/issue/AST-1659) — both User Testing; merge onto tip via `sync-child` / `origin/ftr/AST-1643-migrate-ideal-day-artifact-table` (or sibling publish refs) before hand-verify.

## UAT fitness

- **AC restored:** Parent AC6 — "Editor reload — Ideal Day page after save shows the same text. Fail: empty editor while a current artifact row exists." Parent AC9 — "UI path — Ideal Day still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this ticket is empty. Fail: Ideal Day forced through resume_content ArtifactEditor."
- **Correct outcome:** With a candidate selected, Ideal Day loads the hydrated `context.ideal_day` string (current artifact via AST-1659, or legacy blob / empty on miss); Save keeps the same text in the textarea after success; empty/whitespace Save is refused client-side by the existing `plain_text` gate (no PUT); `ArtifactEditor.tsx` and `ContextTextPage.tsx` have zero product diff on this ticket.
- **Sibling check:** AST-1658 (`candidate.context.ideal_day` + `plain_text` + `TOKEN_SOURCES["IDEAL_DAY"]` artifact-typed) and AST-1659 (PUT intercept + GET hydrate + library SoT gate) remain authoritative — this ticket only passes `bodyShape="plain_text"` so the shared page uses the empty-save gate; load/save still ride `GET/PUT` `{ context: { ideal_day } }`. Verify by merging sibling tips / `origin/ftr/AST-1643-migrate-ideal-day-artifact-table` before hand-check; do not re-implement catalog or API here.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Re-editing `ContextTextPage.tsx` (already parameterized), routing Ideal Day through `ArtifactEditor` / `resume_content`, inventing a client `artifacts` PUT slot, or clearing the leaf on miss — all violate parent Component scope and AST-1634 guidelines.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/ui/frontend/src/pages/CandidateIdealDay.tsx` — Ideal Day-only wire-up against existing ContextTextPage.

Every Files Changed row and every Stage step stays inside that one file. No `config.py`, no `candidate.py`, no `api_candidate.py`, no `ContextTextPage.tsx`, no `ArtifactEditor.tsx`, no `routes.tsx`, no sibling `Candidate*.tsx` context pages, no `database.py`.

**Already on tip / sibling-owned (do not re-invent):**

- `ContextTextPage` optional `bodyShape` + `plain_text` empty-save gate (AST-1634).
- Route `candidate/ideal_day` + nav leaf `/candidate/ideal_day` (pre-existing; Ada AST-1658 does not own nav changes for this leaf).
- PUT `{ context: { ideal_day } }` → operative save; GET hydrate overlays current row (AST-1659).

**Build precondition:** After `sync-child.sh`, `ARTIFACT_CONFIG` must contain `candidate.context.ideal_day` and AST-1659 PUT/GET Ideal Day paths must be present (via `origin/ftr/AST-1643-migrate-ideal-day-artifact-table` or merged sibling tips `origin/sub/AST-1643/AST-1658-…` + `origin/sub/AST-1643/AST-1659-…`). If missing, stop and comment on parent AST-1643 — do not invent catalog or API intercept here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateIdealDay.tsx` | Pass `bodyShape="plain_text"` with existing `contextKey="ideal_day"` | ui |

**Out of this ticket (do not touch):** `ContextTextPage.tsx` / `ArtifactEditor.tsx`; sibling context pages (`CandidateStrengths`, `CandidatePriorities`, `CandidateDealBreakers`, `CandidateBioSummary`, …); `routes.tsx`; Ada config (`config.py`); Hedy core/API; `tests/` / `docs/test-bible/**`.

## Stage 1: Wire Ideal Day `plain_text` bodyShape

**Done when:** With a candidate selected, navigating to `/candidate/ideal_day` (or Candidate nav → Ideal Day) renders `ContextTextPage` with Ideal Day title; load shows hydrated `context.ideal_day` (current artifact via AST-1659, or legacy blob / empty on miss); Save PUTs `{ context: { ideal_day: <draft> } }` and reload shows the same text; empty/whitespace Save is blocked by existing `plain_text` gate (no PUT); `git diff --name-only` for this stage’s product commit is only `CandidateIdealDay.tsx` — `ArtifactEditor.tsx` and `ContextTextPage.tsx` untouched.

1. In `src/ui/frontend/src/pages/CandidateIdealDay.tsx`, replace the one-liner with the Strengths twin shape (mirror `CandidateStrengths.tsx` / `CandidateDealBreakers.tsx`, keep Ideal Day title / key):

```tsx
import ContextTextPage from "../components/ContextTextPage"
export default function IdealDay() {
  return (
    <ContextTextPage
      title="Ideal Day"
      contextKey="ideal_day"
      bodyShape="plain_text"
    />
  )
}
```

Hardcode `bodyShape="plain_text"` to match `ARTIFACT_CONFIG["candidate.context.ideal_day"]["body_shape"]` (Ada AST-1658). Do **not** import or fetch config from the frontend. Do **not** add an `artifactKey` prop — the API leaf stays `context.ideal_day` (Hedy PUT intercept).

⚠️ **Decision:** Only add `bodyShape="plain_text"` — page, title, `contextKey`, and route already exist. Do not re-open `ContextTextPage.tsx` (parameterized on AST-1634). Do not touch `routes.tsx` or nav.

2. Do **not** edit `ContextTextPage.tsx`, `ArtifactEditor.tsx`, any other `Candidate*.tsx` context page, `routes.tsx`, or any non-frontend file. Load/save behavior is entirely the existing `ContextTextPage` contract: `GET /api/candidates/${selectedId}` → `context[contextKey]`; `PUT` body `{ context: { [contextKey]: draft } }` — ideal_day rides AST-1659 intercept/hydrate with no client changes.

**Verify (hand):** with AST-1658 + AST-1659 on tip and a candidate selected — open Ideal Day via nav or `/candidate/ideal_day`; edit text; Save → success toast and textarea still shows that text; refresh/re-enter → same text when a current artifact row exists (or legacy blob until first operative save); clear textarea → Save disabled / empty toast, no network PUT; confirm `ArtifactEditor.tsx` and `ContextTextPage.tsx` have no diff in this ticket’s product commit; Strengths and other context pages still compile.

## Execution contract

- Execute steps in order within the stage; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files beyond the Files Changed table, touch Ada/Hedy scopes, edit sibling context pages, or extend `ContextTextPage` / `ArtifactEditor` / `routes.tsx`.
- On ambiguity or drift — stop, comment on parent AST-1643 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.ui-consistency` | pattern — read in full; plain_text → ContextTextPage; hardcode bodyShape literal; no ArtifactEditor |
| `patt.artifact.read-current` | pattern — read in full; editor opens on GET hydrate leaf (no client blob invent / second fetch) |
| `patt.artifact.write-operative` | pattern — read in full; Save keeps context-leaf PUT → AST-1659 operative intercept |

## Traceability

- Ticket / parent AC6 (editor reload) → Stage 1 §§1–2 + verify
- Ticket AC7 / parent AC9 (UI path; ArtifactEditor untouched) → Stage 1 §2 + Files Changed
- Parent AC7 (no backfill; legacy until re-save) → existing ContextTextPage miss path + AST-1659 hydrate (no client clear)
- Sibling freeze / other context pages → scope gate; no sibling page edits
- Parent AC1–5 / AC8 → N/A (AST-1658 / AST-1659)

## Joan validate

[plan-rubric]
**Ticket:** AST-1660
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref tip:** `57067c0cdfeec052faa38f8ef2e24ab5e2184030` (`origin/sub/AST-1643/AST-1660-ideal-day-contexttextpage-wire-up`)

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.ui-consistency | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.write-operative | A | | |

### Traceability

AC6 (editor reload)→Stage 1 §§1–2 + verify; AC7 (ContextTextPage path; no ArtifactEditor)→Stage 1 §§1–2 + Files Changed; parent AC7 (no backfill)→AST-1659 hydrate miss path via existing GET load; parent AC1–5 / AC8→N/A (AST-1658 / AST-1659).

### Findings

None (`fix-now` / `discuss`).

**R6 notes (acceptable):** Tip `CandidateIdealDay.tsx` is the one-liner missing `bodyShape="plain_text"` while Strengths / Bio Summary / Priorities / Deal Breakers already pass it; plan adds only that prop, mirrors the established twin shape, keeps load/save on `GET/PUT { context: { ideal_day } }` with server-side hydrate/intercept (AST-1659), documents sibling merge precondition without re-scoping config or API, and explicitly forbids `ContextTextPage` / `ArtifactEditor` edits.

context_tokens≈55000


## Review (build stub)

**Built:** `origin/sub/AST-1643/AST-1660-ideal-day-contexttextpage-wire-up` @ `92566d3989ca778187855da1579c4bf681b922cb`.

**Stages delivered:**
- Stage 1: Wire Ideal Day `plain_text` bodyShape — `92566d3989ca778187855da1579c4bf681b922cb`.

**Notes:** Product diff is only `CandidateIdealDay.tsx` (`bodyShape="plain_text"`). `ContextTextPage.tsx` / `ArtifactEditor.tsx` untouched. Stacked `origin/ftr/AST-1643-migrate-ideal-day-artifact-table` (sync `--ftr AST-1643` misses the slug-named ref) so AST-1658 + AST-1659 are on tip for hand-verify.

## Radia review

[code-rubric]
**Ticket:** AST-1660
**Publish ref:** a801c3f04cb9c6e9e91473598456819ad96789ad
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.ui-consistency | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.write-operative | A | | |

### Column diff vs plan stage

(aligned)

### Frame diff

(none)

### Findings

#### fix-now

(none)

#### discuss

(none)

#### advisory

- **Location:** Three-dot diff vs `origin/dev` — stacked sibling product (`config.py`, `candidate.py`, `api_candidate.py`, …) and sibling issue docs
- **Finding:** Epic union via `merge(ftr)` / prior child tips brings AST-1658 catalog + AST-1659 operative paths into the diff vs `origin/dev`. AST-1660 `code()` commit touches only `CandidateIdealDay.tsx`.
- **Recommendation:** No AST-1660 product fix; prerequisite satisfied on tip for UAT hand-verify.

- **Location:** `docs/test-bible/frontend/pages.md` § AST-1660 bible shasum
- **Finding:** Shasum line still `*(filled after publish)*`.
- **Recommendation:** Chuckles sync on writeback — not a code gate.

- **Location:** Canon clerk / frozen list resolution
- **Finding:** `patt.artifact.ui-consistency` is draft; scored from `canon/directives/draft/patt.artifact.ui-consistency.md` at epic worktree, not `canon_clerk expand` payload.
- **Recommendation:** Corpus hygiene downstream; no scope gap on frozen list.

### Notes

- **Scope divergence (expected):** Product authorship is one file (`92566d39`). `tests/component/frontend/pages/test_CandidateIdealDay.test.tsx`, `docs/test-bible/frontend/pages.md`, and stacked sibling `src/` / `tests/` / `docs/` changes are Betty `merge-tests` + epic union — not AST-1660 scope creep in `code()` commits.
- **Estimate footprint:** Confirm **2** points still fits (single-page `bodyShape` wire-up + manifest tests).

### What's solid

- Stage 1 delivered verbatim: `CandidateIdealDay.tsx` mirrors `CandidateStrengths.tsx` twin shape — `title="Ideal Day"`, `contextKey="ideal_day"`, hardcoded `bodyShape="plain_text"`; no `artifactKey`, no config import, no `ArtifactEditor`.
- `ContextTextPage.tsx` and `ArtifactEditor.tsx` have zero diff vs `origin/dev` on this branch; load/save rides existing `GET/PUT { context: { ideal_day } }` with AST-1659 server hydrate/intercept.
- `test_CandidateIdealDay.test.tsx` covers render + hydrated load, save PUT + textarea reload (operative-shaped PUT response), `plain_text` empty-save gate (Save disabled, no PUT), and source assert for `bodyShape` / no `ArtifactEditor`.

### Recommended actions

(none downstream — artifact complete)

context_tokens≈35000

