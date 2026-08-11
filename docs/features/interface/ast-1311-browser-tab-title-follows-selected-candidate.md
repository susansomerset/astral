# Browser tab title follows selected candidate

**Linear:** [AST-1311](https://linear.app/astralcareermatch/issue/AST-1311/browser-tab-title-follows-selected-candidate)
**Parent:** [AST-1307](https://linear.app/astralcareermatch/issue/AST-1307/please-set-the-page-title-to-astral-full-name)
**Publish ref:** `sub/AST-1307/AST-1311-browser-tab-title-follows-selected-candidate`

Susan keeps several Astral tabs open; Chrome’s tab list currently says `Astral` on every one. This ticket sets `document.title` from the selected candidate’s existing `full` column so the chrome list reads `Astral - <Full Name>`, and falls back to `Astral` when there is no usable Full Name. It does not own picker labels, Profile editing, nav chrome, or exported HTML titles.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/documentTitle.ts` | New. Pure `browserTabTitle` formatter: `Astral` or `Astral - <Full Name>` | ui |
| `src/ui/frontend/src/contexts/CandidateContext.tsx` | Two `useEffect`s: apply title from selected `full`; reset to `Astral` on provider unmount | ui |

**Do not touch:** `index.html` (static `<title>Astral</title>` stays the pre-JS / unauthenticated default), `NavigationShell.tsx`, `candidateLabel.ts`, `routes.tsx`, `Login.tsx`, `Authenticate.tsx`, `LogOffScreen.tsx`, Profile / `candidate.py` / `builder.py`, `config.py`, `App.css`.

## Stage 1: Format helper + sync `document.title` from selected `full`

**Done when:** With a loaded selected candidate whose `full` is `Jolane Abrams`, `document.title` is exactly `Astral - Jolane Abrams`. Changing `selectedId` updates the title without a reload. After reload, once `/api/candidates` hydrates the persisted selection, the title shows that candidate’s `full`. Empty / missing / whitespace `full`, or no matching selected row, yields exactly `Astral`. Unmounting `CandidateProvider` (logout / login chrome) resets `document.title` to `Astral`. Route changes do not alter the title string (no pathname subscription).

1. Create `src/ui/frontend/src/lib/documentTitle.ts` with exactly this export (no other exports, no React import):

   ```ts
   export function browserTabTitle(fullName: string | null | undefined): string {
     const name = (fullName ?? "").trim()
     if (!name) return "Astral"
     return `Astral - ${name}`
   }
   ```

   Literals are `Astral` and space-hyphen-space (` - `). Do not read `first`, `last`, `astral_candidate_id`, or `candidateLabel` / `candidateOptionLabel` / `candidateBaseLabel`.

2. In `src/ui/frontend/src/contexts/CandidateContext.tsx`, add:

   ```ts
   import { browserTabTitle } from "../lib/documentTitle"
   ```

   Place it with the existing relative imports (after `fmt` / `AuthContext`).

3. In `CandidateProvider`, after the existing timezone `useEffect` (the one that calls `setFmtTimezone`), add two effects — do not fold them into the timezone effect:

   ```ts
   useEffect(() => {
     const selected = candidates.find(c => c.astral_candidate_id === selectedId)
     document.title = browserTabTitle(selected?.full)
   }, [selectedId, candidates])

   useEffect(() => {
     return () => {
       document.title = browserTabTitle(undefined)
     }
   }, [])
   ```

   The first effect applies the title whenever selection or the list changes (covers picker change, persisted `localStorage` id after `load()`, and Profile save’s existing `refresh()` which reloads `/api/candidates`). The second effect’s cleanup-only empty-deps run resets the title when `CandidateProvider` unmounts (`RequireAuth` swaps to `Login` / `LogOffScreen`; `Authenticate` never mounts the provider).

   ⚠️ **Decision:** Put the sync in `CandidateProvider`, not `NavigationShell` and not a new invisible component. This file already owns selected-candidate side effects (timezone). Parent forbids restyling / restructuring the nav shell (AST-1284 / AST-1286). `RequireAuth` only mounts `CandidateProvider` behind a session, so login / authenticate / log-off chrome keep `index.html`’s `Astral` unless a previous session left a title — the unmount cleanup clears that.

   ⚠️ **Decision:** Use the list payload’s top-level `full` only. Do not join `first`+`last` in React and do not reuse `candidateLabel` (picker: first+last, else id; collision labels append id). `full` is the Profile Full Name column (`CANDIDATE_DATA_MODEL`; empty-`full` → `recompute_full_name` on save in `candidate.py`). Re-joining in the SPA would invent a second name rule (`astral.layers.ui-config-driven-business-logic`). If `full` is missing or blank after load, AC 4 applies: title is `Astral`.

   ⚠️ **Decision:** Do not add `react-helmet`, a router `handle.title`, or a `location.pathname` dependency. Those invite page/route names into the tab (AC 5). Do not add a `config.py` / API key for the product word `Astral` — it already lives in `index.html`; this is presentation chrome, not a state set.

4. Do not edit `index.html`. Do not fetch `/api/candidates/:id` for the title. Do not call `setSelectedId` or change `STORAGE_KEY` / `load()` selection rules.

## Self-Assessment

**Scope:** `Single-Component` — one new `lib/` formatter and two effects in the existing candidate context; ui frontend only.

**Conf:** `high` — `CandidateInfo.full` is already on the `/api/candidates` list row; the timezone `useEffect` in the same provider is the side-effect pattern to copy; format and fallback are specified by parent AC.

**Risk:** `low` — only `document.title` changes; a wrong string is chrome, not persisted data. Unmount cleanup is what keeps AC 6 (login still `Astral`) after a session.

## Code rules check

| Rule | Status |
|------|--------|
| §1.3 DRY | Formatter is one function; both effects call it (apply + unmount reset) — no duplicated `Astral - ` literals in the context file |
| §2.1 config | No new config block. Product title string is presentation, already in `index.html`; name join stays in core `recompute_full_name` |
| §2.4 batch | N/A |
| §2.6 state machine | Untouched |
| §3.3 imports | New module is frontend-only; context already imports `lib/` |
| §3.5 naming / placement | `documentTitle.ts` + `browserTabTitle` are domain names (no ticket id). Helper in `lib/`; no new component/page/CSS |
| `astral.layers.ui-config-driven-business-logic` | React does not re-derive Full Name; it renders `full` from the payload |
| `astral.standards.in-scope-only` | Two files only; nav / Profile / builder / picker labels excluded |
| Boundaries | No `NavigationShell` edit, no `candidateLabel` reuse, no exported `<title>` in `builder.py` |

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1311
**Publish ref:** `sub/AST-1307/AST-1311-browser-tab-title-follows-selected-candidate` @ `c65d6626`
**Overall:** APPROVED

### Traceability

| Child AC | Plan stage(s) | Definition anchor |
|----------|---------------|-------------------|
| 1 — Selected Full Name `Jolane Abrams` → tab exactly `Astral - Jolane Abrams` | Stage 1 (`browserTabTitle`, apply effect) | Parent functional scope: `Astral - <Full Name>` |
| 2 — Candidate change updates title without reload | Stage 1 (apply effect on `[selectedId, candidates]`) | Parent: “stays in sync when the selected candidate changes” |
| 3 — Reload with persisted selection shows Full Name after load | Stage 1 (same effect after `load()` hydrates list + `localStorage` id) | Parent: “including a persisted selection on reload” |
| 4 — No selection or unformable Full Name → exactly `Astral` | Stage 1 (`browserTabTitle` empty trim → `Astral`; missing row → `undefined`) | Parent: “When no candidate is selected, or Full Name cannot be formed, the title is `Astral`” |
| 5 — Route navigation does not add route/page names | Stage 1 (no router/helmet/pathname deps; explicit non-goals) | Parent boundary: “Does not append the current route, page heading…” |
| 6 — Unauthenticated / sign-in chrome still `Astral` | Stage 1 (unmount cleanup; `Authenticate` outside provider; `index.html` static) | Parent boundary: favicon / unauthenticated chrome unchanged |

| Stage | Child AC / definition |
|-------|----------------------|
| Stage 1 | AC 1–6; parent Purpose + functional scope |

No orphan stages. All six child ACs mapped.

### Statute verdicts

| Statute / pattern | Verdict | Rationale |
|-------------------|---------|-----------|
| `astral.ui.frontend-file-placement` | conforms | Helper in `src/ui/frontend/src/lib/`; sync in existing `contexts/CandidateContext.tsx` |
| `astral.ui.naming-conventions` | conforms | `documentTitle.ts` / `browserTabTitle` domain names |
| `astral.layers.ui-config-driven-business-logic` | conforms | Reads list payload `full` only; explicit ban on first+last join and `candidateLabel` |
| `astral.standards.in-scope-only` | conforms | Two frontend files; nav / Profile / builder / picker excluded |
| `astral.standards.names-not-ticket-ids` | conforms | No ticket ids in identifiers |
| `astral.standards.dry-and-focused-functions` | conforms | Single formatter; apply + unmount both call it |
| `no established pattern applies` (parent) | conforms | Plan matches parent: one-place shell presentation, not a new catalog shape |

### Considered and excluded

**Considered:** in-scope statutes above.

**Excluded (boundary / out of child):**
- `pattern.ui.shared-button-roles`, `pattern.ui.icon-control`, `pattern.ui.admin-endpoint` — do not govern `document.title`
- `NavigationShell.tsx` / AST-1284 — parent forbids nav shell edits
- `candidateLabel.ts` — picker label, not Full Name
- Profile / `recompute_full_name` — AST-1081/1082; consumes `full` only
- `builder.py` exported HTML `<title>` — parent boundary
- `config.py` / API for product word `Astral` — presentation chrome in `index.html`
- `index.html`, `Login.tsx`, `Authenticate.tsx`, `LogOffScreen.tsx` — static unauthenticated chrome
- Universal `orch.*` — pipeline, not product scope

### Findings

| Sev | Location | Finding | Recommendation |
|-----|----------|---------|----------------|
| **acceptable** | Stage 1 apply effect | Brief `Astral` flash possible between auth + `/api/candidates` hydrate before `selected?.full` resolves | Matches AC 3 “after the app loads”; no plan change needed |
| **acceptable** | Plan traceability | Single stage covers all ACs | Appropriate for Single-Component scope |

**Tip verification:** `CandidateContext.tsx` already has `CandidateInfo.full`, timezone side-effect pattern at lines 64–69, and `load()` restoring `localStorage` selection — plan sites are accurate. `documentTitle.ts` does not exist yet (expected). `routes.tsx` mounts `CandidateProvider` only under `RequireAuth`; `authenticate` is outside that tree. `index.html` is `<title>Astral</title>`. `CandidateProfile.tsx` calls `refreshCandidate()` after save (line 113), so Full Name edits retrigger the apply effect as the plan assumes.

**Self-assessment:** Single-Component / high conf / low risk — honest and proportionate.

**Plan Discuss:** 0 completed rounds (Katherine plan comment only).

context_tokens≈14000
— Joan

## Review (build)

**Built:** `origin/sub/AST-1307/AST-1311-browser-tab-title-follows-selected-candidate` @ `acea55004bb8b60c94d98256cb936e5c5b873d7f`

Stage 1: `browserTabTitle` in `lib/documentTitle.ts`; `CandidateProvider` applies `document.title` from selected `full` and resets to `Astral` on unmount. Tests deferred to Betty.
