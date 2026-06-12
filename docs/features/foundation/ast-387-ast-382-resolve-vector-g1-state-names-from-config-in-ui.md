# Plan: AST-387 — Resolve Vector G1 (state names from config in UI)

**Linear:** https://linear.app/astralcareermatch/issue/AST-387/ast-382-resolve-vector-g1-state-names-from-config-in-ui  
**Feature branch:** `betty/ast-387-ast-382-resolve-vector-g1-state-names-from-config-in-ui`

## Summary

Remove hardcoded Astral job/company/candidate state string literals from React where notes grade **B**/**C** for **G1**. Source labels and transition payloads from **server-provided metadata** derived from `src/utils/config.py` (single source of truth), not duplicated constants in TS. Do **not** conflate with **AST-381** (DB snapshot).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | If needed, add a compact JSON-serializable structure (e.g. `UI_STATE_LABELS` or extend `UI_CONFIG`) exposing human labels for states already defined in `JOB_STATES` / `COMPANY_STATES` / `CANDIDATE_STATES` — **no new authoritative state lists**; only presentation metadata | utils |
| `src/ui/api/api_system.py` or dedicated `api_meta.py` | Endpoint e.g. `GET /api/ui_constants` returning `{ job_states: {...}, ... }` built from config (existing `nav_config` pattern is precedent) | ui |
| `src/ui/frontend/src/api.ts` | Add typed fetch for new endpoint | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Replace string literals with API-driven map | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Same | ui |
| `src/ui/frontend/src/components/CompanyDetailModal.tsx` | Same | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Same | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Same | ui |
| `src/ui/frontend/src/pages/CompaniesInactiveList.tsx` | Same | ui |
| `src/ui/frontend/src/pages/CompaniesIgnored.tsx` | Same | ui |

⚠️ **Decision:** Prefer **one** endpoint returning all UI-needed state metadata to avoid N+1 fetches on page load; cache in React context if already have app-level provider pattern.

## Stage 1: Server contract

**Done when:** Flask returns JSON whose keys are exactly the state strings from config (machine keys) plus optional `label` / `sort` fields; frontend types exported in `api.ts`.

1. Inspect `NAV_CONFIG` resolution in `api_system.py` for pattern to copy.
2. Implement read-only endpoint assembling dicts from `JOB_STATES`, `COMPANY_STATES`, `CANDIDATE_STATES` keys already in config — **iterate config keys**, do not hand-type state strings in Python beyond what config already contains.

## Stage 2: Frontend consumption

**Done when:** `rg "'PASSED_GET'|\"PASSED_GET\"|\"WATCH\""` (expand with actual literals from notes) across listed TSX files shows only non-domain strings (e.g. CSS keys) or API-fed references.

1. On each page, load constants once via hook or parent (e.g. `useEffect` + context).
2. Replace switch/if chains comparing to hardcoded states with lookups into fetched map.

## Stage 3: Regression pass

**Done when:** Jobs review / skipped / companies inactive/ignored screens render same labels as before for a seeded local DB.

1. Manual click-through with one company and one job per flow; screenshot optional.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — New API surface plus multiple TSX files.

**Conf:** `LOW` — API shape needs Susan/UX agreement on labels vs raw keys.

**Risk:** `Medium` — Wrong state string in a transition payload breaks tracker transitions; mitigate by typing API response against config-derived keys only.

## Plan vs ASTRAL_CODE_RULES

§2.1 / §2.6: State names originate in config; UI never introduces parallel state vocabulary.

## Review (stub)

**Branch:** `betty/ast-387-ast-382-resolve-vector-g1-state-names-from-config-in-ui`  
**Publish commit:** latest **Built by Betty** comment on the Linear issue.

## Resolution (2026-05-11 — f-resolve-linear, Betty)

**Radia `e-review-linear`:** fix-now **0**. **Resolve pass:** no additional product changes required (discuss/advisory items left for Susan / future tickets as appropriate).

Advanced to **User Testing** per `docs/ASTRAL_TEAM_WORKFLOW.md`.
