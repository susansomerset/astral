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

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1311
**Publish ref:** `origin/sub/AST-1307/AST-1311-browser-tab-title-follows-selected-candidate` @ `0cfab525b4c1333b0f63fdaf369360a006d190c6`
**Overall:** CLEAN

**Diff:** `origin/dev` (`8577bd5f`)…`origin/sub/AST-1307/AST-1311-browser-tab-title-follows-selected-candidate` (no fetch; Ask mode — local tracking refs).
**Change set:** layers `{ui, docs}`; change_types `{add, modify}`.
**Paths:** `src/ui/frontend/src/lib/documentTitle.ts` (A), `src/ui/frontend/src/contexts/CandidateContext.tsx` (M), `docs/features/interface/ast-1311-browser-tab-title-follows-selected-candidate.md` (A), `docs/test-bible/frontend/{lib,contexts}.md` (M), `tests/component/frontend/{lib/test_documentTitle.test.ts,contexts/test_CandidateContext.test.tsx}` (A).

Active harvested registry: **64** rows (README footer says 65 — see Notes). Retired ignored.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | layers `{core,utils}` ∩ `{ui,docs}` empty |
| `astral.agent.do-task-delegation` | scoped | not-applicable | layers `{core}` ∩ `{ui,docs}` empty |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | layers `{core}` ∩ `{ui,docs}` empty |
| `astral.batch.batch-id-first` | scoped | not-applicable | layers `{data,core}` ∩ `{ui,docs}` empty |
| `astral.batch.batch-id-format` | scoped | not-applicable | layers `{core,data}` ∩ `{ui,docs}` empty |
| `astral.batch.claim-process-release` | scoped | not-applicable | layers `{core,data}` ∩ `{ui,docs}` empty |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | layers `{core,data}` ∩ `{ui,docs}` empty |
| `astral.config.config-source-of-truth` | scoped | conforms | `Astral` is presentation chrome (plan + Joan); not a config/state set |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets / env lookups |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no artifacts/debug paths (file cursorignored; inferred from id) |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no `debug/` spike paths (file cursorignored; inferred from id) |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | layers `{core,utils}` ∩ `{ui,docs}` empty |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | layers `{core,utils}` ∩ `{ui,docs}` empty |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single `docs/features/interface/ast-1311-….md` |
| `astral.git.betty-no-src-or-features` | scoped | conforms | `test`/`merge-tests` touch bible+tests only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | `code(AST-1311)` is the two `src/ui/frontend` files only |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | layers `{core,external}` ∩ `{ui,docs}` empty |
| `astral.layers.import-direction` | scoped | conforms | context → `../lib/documentTitle` only; no data/external |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers `{scripts}` ∩ `{ui,docs}` empty |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | renders list `full` only; no first+last / `candidateLabel` |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | layers `{core}` ∩ `{ui,docs}` empty |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | layers `{core}` ∩ `{ui,docs}` empty |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | no API routes; `CandidateProvider` still under `RequireAuth` |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | layers `{core,data,utils}` ∩ `{ui,docs}` empty |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | layers `{core,utils}` ∩ `{ui,docs}` empty |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | layers `{core,data,utils,scripts}` ∩ `{ui,docs}` empty |
| `astral.seed.define-approved` | scoped | conforms | no product seed invented |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | layers `{core,data,utils}` ∩ `{ui,docs}` empty |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | layers `{core,data,utils}` ∩ `{ui,docs}` empty |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no data-layer log/swallow in this diff |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers `{data}` ∩ `{ui,docs}` empty |
| `astral.standards.debug-contract-gated` | scoped | conforms | no `debug=` / contract emission; SPA chrome only |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | one formatter; apply + unmount both call it |
| `astral.standards.in-scope-only` | scoped | conforms | planned two `src` files; forbidden nav/Profile/builder/`index.html` untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | no `print` / `getLogger` |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `documentTitle` / `browserTabTitle` are domain names |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays in frontend `lib/` + `contexts/` |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | no state/enum sets; title literals are AC chrome |
| `astral.standards.public-then-helpers` | scoped | conforms | single public export; context layout unchanged |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | layers `{utils}` ∩ `{ui,docs}` empty |
| `astral.state.core-decides-transitions` | scoped | not-applicable | layers `{core,data}` ∩ `{ui,docs}` empty |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | layers `{core,data,utils}` ∩ `{ui,docs}` empty |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | layers `{core}` ∩ `{ui,docs}` empty |
| `astral.ui.frontend-file-placement` | scoped | conforms | helper in `lib/`; sync in existing `contexts/` |
| `astral.ui.naming-conventions` | scoped | conforms | camelCase lib module matches peers (`analysisUpshot.ts`) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no worker / server process change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1311)` @ `0cfab525` ← `f5dcc87c` |
| `orch.git.commit-vocabulary` | universal | conforms | `plan` / `docs` / `code` / `test` / `merge-tests` only |
| `orch.git.flow-direction-inviolable` | universal | conforms | three-dot vs `origin/dev`; publish ref is `sub/…` |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1307/AST-1311-browser-tab-title-follows-selected-candidate` |
| `orch.git.merge-on-checkout` | universal | conforms | epic worktree on publish ref = origin tip |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear docs→code→test→merge-tests; no rewrite signals |
| `orch.git.no-dev-agent-branches` | universal | conforms | not `dev-*` / agent-named |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | `/home/susan/astral-AST-1307/` |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branch |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | placement / `full`-only / no helmet decided in plan; code did not reopen |
| `orch.pipeline.plan-is-bible` | universal | conforms | formatter + two effects match Stage 1 verbatim |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Interface child; isolated review |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | spawn Status `Tests Passed` → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no `canon/statutes/**` in diff |
| `orch.roles.betty-owns-test-tree` | universal | conforms | bible + Vitest via `test` + `merge-tests` |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Katherine Johnson |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | implementer remains assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer `code` commit has no banned test-tree paths |

### Pattern conformance

none cited

Parent / Joan: “no established pattern applies.” Diff is one-place `document.title` chrome from list `full`. Does not match approved catalog `# Problem` shapes (batch claim, state transitions, config-block, import-discipline, admin-endpoint, shared-button, icon-control, score-floor).

### Plan adherence

Stage 1 landed as specified: `browserTabTitle` is the exact export; `CandidateProvider` has two new effects (not folded into timezone) on `[selectedId, candidates]` and unmount cleanup → `Astral`. Import is top-level with other `lib/` imports. `index.html` still `<title>Astral</title>`. `routes.tsx` still mounts `CandidateProvider` once under `RequireAuth` (Authenticate outside). No `candidateLabel`, no first+last join, no helmet/pathname, no Profile/builder/`config.py`/`NavigationShell`. Self-Assessment Single-Component / high / low matches the footprint. Relations: none — no sibling smuggle.

C6 §5a–§5g: top-level import; no UI→data/external; no new swallow; `?? ""` / missing-row → `Astral` is the AC; no logging; no hardcoded state sets; no batch/debug/external surfaces. §5f/§5g not triggered.

### Findings

(none)

### Frame diff

New `lib/documentTitle.ts` (`Astral` / `Astral - <trimmed full>`). `CandidateContext.tsx` applies `document.title` from selected list-row `full` and resets on provider unmount. Betty: `test_documentTitle.test.ts` + `CandidateProvider — AST-1311` cases; bible `frontend/lib.md` + `frontend/contexts.md`. Issue doc plan + Joan APPROVED + build stub.

### Notes

- Joan excluded `orch.*` at plan time (“pipeline, not product”). Code-rubric universals still scored `conforms` — not a C4 product straggler.
- Harvested table = 64 active ids; README says 65. Downstream canon hygiene, not this child.
- `astral.debug.*` files are `.cursorignore`’d; N/A from id + absence of artifacts/spike paths.
- Pre-existing bible header `tests/component/contexts/` vs real `tests/component/frontend/contexts/` — Betty optional; not in this `src` diff.
- Ask mode: no fetch, no `docs()`, no Linear write.

context_tokens≈28000
— Radia
