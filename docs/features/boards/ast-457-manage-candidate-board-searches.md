# Manage Candidate Board Searches

**Linear:** [AST-457](https://linear.app/astralcareermatch/issue/AST-457/manage-candidate-board-searches)

**Parent epic:** [AST-379 — Design data flow for Astral Boards](https://linear.app/astralcareermatch/issue/AST-379/design-data-flow-for-astral-boards)

**Feature ref:** `ftr/AST-457` (origin only — see orientation-astral branch law.)

**Summary**

This ticket delivers the candidate-facing **Board Searches** screen: browse saved searches (label + board + timestamps only), create/edit/delete with either **criteria** mode or **user-supplied full deeplink URL** mode (mutually exclusive with a guarded mode switch), a **user `enabled`** flag so disabled rows are excluded from board gaze claim logic, normalized duplicate rejection and domain validation enforced on save (server-authoritative). Replace the sidebar **Title Patterns** entry with **Board Searches**; **`profile.title_patterns`** remains in **`DATA_SHAPES`** / config tokens (editable from **Candidate Profile** when that section ships there — do **not** remove the field from `TRACKER_CONFIG` / token map). Depends on Boards backend per Linear **AST-457** Dependencies: **AST-415** (boards read/list for picker), **AST-458** (`board_search` API — enabled/deeplink/duplicate validation and stored wire shape Katherine consumes), **AST-459** (gaze respects enabled + deeplink — UAT/end-to-end, not Katherine inline work). Katherine ships **thin API/UI glue** atop merged **`origin/dev`** primitives only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | NAV_CONFIG: swap **Title Patterns** item for **Board Searches** at `/candidate/board_searches` | utils |
| `src/ui/frontend/src/routes.tsx` | Route `candidate/board_searches`; drop `candidate/title_patterns` route + TitlePatterns import | ui |
| `src/ui/frontend/src/pages/CandidateBoardSearches.tsx` | **New** list + CRUD UX (tabs per ASTRAL_CODE_RULES §3.5 flat `pages/`) | ui |
| `src/ui/frontend/src/pages/CandidateTitlePatterns.tsx` | **Delete** (standalone Title Patterns page removed) | ui |
| `src/ui/api/api_candidate.py` | New blueprint routes under `/api/candidates/<id>/board_searches/*` delegating to **core** (no SQL here) | ui |
| `src/core/candidate.py` *(or sibling module if clearer)* | Thin orchestration wrappers calling **data layer** `board_search` helpers (list/create/update/delete + validation hooks) — **only if** helpers already exist post-merge | core |
| `src/ui/frontend/src/App.css` | Styles for list table, toolbar, modal/confirm aligned with existing `dep-*` patterns | ui |

**Explicitly out of scope for this ticket (do not add files or logic):**

- Changes under `tests/` (Betty/`qa-astral` revises manifests and removes or replaces **`test_CandidateTitlePatterns`** after Code Complete comment).
- Dispatcher / `gaze_board` internals exercised in UAT (**AST-459**), `dispatch_tasks`, ingest forks not owned here.
- **BOARD_CONFIG** population / ATS registry (**AST-415**).

---

## Preflight blocker (STOP without guessing)

Immediately after **`Plan Approved`** + merge **`origin/dev`** + **`origin/ftr/AST-457`** onto **`dev-kath`** for build:

1. Open `src/data/database.py` header inventory — confirm **`board_search`** table + data helpers exist (exact names wired by **AST-458** merge).
2. Confirm **read API** for adopted boards (**AST-415**) exists e.g. **`GET /api/boards`** (exact path/signatures taken from codebase after merge).

If **either** is missing → **STOP** (`build-astral`): Linear comment citing this plan step, loop Susan — **do not invent SQL or REST shapes**.

---

## Stage 1: Navigation / routing cleanup

**Done when:** Sidebar shows **Board Searches**, no **Title Patterns** nav item; direct navigation to **`/candidate/title_patterns`** is no longer routed (SPA falls through to catch‑all navigate like other unknown paths unless you intentionally add **`Navigate` to `/candidate/board_searches`** replace — omit extra redirect unless product asks).

1. In `src/utils/config.py`, under `NAV_CONFIG` candidate group, replace `{ "label": "Title Patterns", "path": "/candidate/title_patterns" }` with `{ "label": "Board Searches", "path": "/candidate/board_searches" }` (preserve ordering relative to sibling items unless Susan specified otherwise — default: keep adjacent position previously held by Title Patterns).
2. In `src/ui/frontend/src/routes.tsx`, remove import of `CandidateTitlePatterns` and remove route `candidate/title_patterns`. Import and register `CandidateBoardSearches` for `candidate/board_searches` (**create stub component in Stage 2 if needed to compile** — simplest: export placeholder `<p>` then flesh out Stage 3).
3. Delete `src/ui/frontend/src/pages/CandidateTitlePatterns.tsx`.

⚠️ **Decision:** Removing the standalone route **drops** isolated editing UX for regexes; **`profile.title_patterns`** remains for gazer (**`src/core/gazer.py`**) via **Candidate Profile** when that textarea is surfaced there in `DATA_SHAPES` (**already present** in config per `profile.title_patterns`). No schema deletion.

---

## Stage 2: Candidate board search REST surface (thin)

**Done when:** Authenticated caller can CRUD searches for **`GET /api/candidates/<candidate_id>/board_searches`** lifecycle with JSON errors surfaced to React.

Adapt **exact** handler names/signatures imported from **`src/core/*`** once visible after backend merge — the following REST contract is the **intent** Katherine wires; mutate names to match checked-in helpers without changing HTTP paths:

| Method | Path | Body | Success | Errors |
|--------|------|------|---------|--------|
| GET | `/api/candidates/<cid>/board_searches` | — | `{ "searches": [ ... ] }` | 404 candidate |
| POST | `/api/candidates/<cid>/board_searches` | `{label, board_id, enabled, mode: "criteria" \| "deeplink", criteria?: object|null, deeplink_url?: string|null}` | `{ "search": { ...saved row... } }` | 400 validation (duplicate normalized key, invalid domain deeplink vs board allow‑list returned from server message, malformed JSON criteria) |
| PATCH | `/api/candidates/<cid>/board_searches/<sid>` | same fields partial | `{ "search": {...} }` | 404 / 400 |
| DELETE | `/api/candidates/<cid>/board_searches/<sid>` | — | `{ "deleted": "<sid>" }` | 404 |

1. Add routes under existing `candidate_bp` in **`api_candidate.py`** with `@require_auth`, mirroring **`get_candidate` / 404** pattern used by other candidate subresources.
2. Each handler: sanitize `candidate_id` from URL, call merged core helper; return **JSON** errors as strings in `{"error":"..."}` for 400 consistent with **`update_candidate_data`** style.
3. **Do not** embed SQL strings in Flask module — delegates only.

⚠️ **Decision:** Duplicate rejection is **server-side normalized** comparison (**AST-458**). UI displays returned error verbatim in toast/error strip.

### Shipped contract (actual HTTP paths)

Stage 2 table above stays as **intent / historical**. What shipped aligns with **`api_boards.py`** (**AST-458** checked-in REST):

| Method | Shipped path | Notes |
|--------|----------------|-------|
| GET | **`GET /api/boards`** | Adopted boards for picker (**AST-415**). |
| GET | **`GET /api/boards/searches?candidate_id=`** | List searches for candidate. |
| POST | **`POST /api/boards/searches`** | Body includes `candidate_id`; same payload shape as Stage 2 `POST`. |
| PATCH | **`PATCH /api/boards/searches/<board_search_id>`** | Partial update. |
| DELETE | **`DELETE /api/boards/searches/<board_search_id>`** | Deletes one row. |

UI **`CandidateBoardSearches.tsx`** calls these routes; **`api_candidate.py`** was not extended with **`/api/candidates/<cid>/board_searches/*`** wrappers.

---

## Stage 3: Board catalog fetch for picker

**Done when:** Create/Edit form can populate board `<select>` from live registry.

1. From `CandidateBoardSearches.tsx`, **`GET`** the merged boards list endpoint (**exact path read from codebase** — typical prefix `/api/boards`).
2. Map options by stable **`board_id`** (DB FK) displaying human label (**`name`/`slug`/merged field**).

If endpoint missing at build → **STOP** (preflight should have caught; do not stub fake boards data in production code).

---

## Stage 4: `CandidateBoardSearches.tsx` — list UX

**Done when:** For selected candidate (**`CandidateContext`** `selectedId` like Profile), UI loads table with **exactly four** visible columns sortable/display only: **`label`, `board` (friendly name resolved from catalog map by `board_id`), `created_at`, `updated_at`**. Rows respect API order default (creation ascending unless backend specifies differently — mirror returned array order; **no extra client sort** unless backend unsorted mess requires `created_at desc` documented in-plan — default **preserve API ordering**).

1. Uses shared `api` client from **`src/ui/frontend/src/lib/api.ts`** with bearer token unchanged.
2. Empty state message when array length 0.
3. Toolbar: buttons **New search**, optional **Refresh** (re-fetch GET list).
4. Row actions column (not counted in the four data columns **per spec** definition): Edit / Delete icons or buttons styled like other list pages (**match `CompaniesWatchList`/`JobsRecommended` button classes**).

---

## Stage 5: Create / Edit UX — modes, clears, toggles

**Done when:** User can POST/PATCH with **criteria ↔ deeplink** exclusivity enforced in UI prior to submit + **`enabled`** toggle PATCH without touching operational batch status field.

### 5a Form fields

- **Label** (`str`, required trimmed non-empty).
- **Board** (required select `board_id` from Stage 3 catalog).
- **Enabled** checkbox (defaults **true** on create).
- **Mode** segmented control (**Criteria** vs **Deeplink**).

### 5b Criteria mode

- Render **criteria** editor as **`textarea`** bound to canonical **JSON.stringify**pretty of object (minimum viable). On save: `JSON.parse` in browser — if fails, block submit client-side toast **Invalid JSON**.
- Parsed object sent as **`criteria`**; **`deeplink_url`** payload key explicitly **`null`** on POST/PATCH after mode switch sanitization.

### 5c Deeplink mode

- Single **`input type="url"`** (textarea acceptable if URLs may exceed browser URL field limits — prefer **textarea rows=3** trimmed string). Send **`deeplink_url`**, **`criteria": null`**.
- Domain allow-list validation only **observed via 400 responses** (+ display message). No client duplication of BOARD_CONFIG hostname rules (**ASTRAL_CODE_RULES** — logic belongs server).

### 5d Mode switch guard

Changing mode while form dirty → **`window.confirm("Switching clears the current criteria/deeplink. Continue?")`** — abort if cancel. On proceed: wipe local opposing field state (**clear textarea / URL input**) before enabling submit.

⚠️ **Decision:** Confirmation uses native confirm to avoid new **`Modal.tsx`** coupling unless Modal already idiomatic elsewhere for destructive clears — optional swap to **`Modal`** only if codebase already wraps similar confirm (pick one pattern consistently within this page).

---

## Stage 6: Delete + error surfacing polish

**Done when:** Delete asks confirm, DELETE route fires, optimistic removal or reload list refreshes timestamps.

1. **`window.confirm`** on delete (consistent with Stage 5d choice).

2. Map HTTP errors → inline banner or toast (**reuse patterns from Candidate Profile**) with message body `error`.

---

## Stage 7: Styling polish

**Done when:** List + modal layout consistent with **`App.css`** section conventions (TOC entry added), uses existing grid/list classes; no inline style explosion beyond quick spacing already common in codebase.

---

## Self-Assessment

### Scope

**Single-Component** — Touches Flask candidate API blueprint, candidate core façade (glue only), and one React list page plus shared nav/routes/CSS; deletes obsolete Title Patterns shell.

### Confidence

**Medium** — Wire contract matches ticket dependencies (**AST‑415**, **AST‑458**, **AST‑459**) but **`origin/dev` merge timing determines exact helper names/endpoints**: preflight resolves drift; **`conf-low`** avoided because discovery steps are enumerated.

### Risk

**Medium** — Mis-wiring **`enabled`** or mis-binding deeplink payloads could silently exclude scans or scrape wrong URLs; mitigate by verbatim server errors and honoring merged core tests Betty adds.

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Reuses `api()`, `CandidateContext`, existing list/button classes; avoids parallel fetch clients.
- **§2.1 config:** Sidebar only via **`NAV_CONFIG`**; criteria payload does not stash magic sets in frontend.
- **§2.6 state machine:** Candidate **state transitions untouched** unless discovered conflict — escalate if accidental.
- **§3.3 imports:** UI Flask stays **thin** (no **`data`**/**`external`**).
- **§3.5 naming:** `CandidateBoardSearches.tsx`; route snake_case **`/candidate/board_searches`**.

No conflicts surfaced that require `conf-!!-NONE`.

---

## Revisions

Revision 1 — 2026-05-23

Driven by: Linear AST-457 issue description **Dependencies and blockers** list (`AST-415`, `AST-458`, `AST-459`).
Changes: Preflight blocker, Summary, Scope exclusions, Confidence, and Decision note now cite **458/459** instead of legacy AST-416/418 child references from earlier coordination drafts.

---

## Review

**Radia** — reviewed `origin/dev...origin/ftr/AST-457` (merge-base integration line; tip **`e8d4d4deaee3f9953854ceb79ec3e1ecf23a3bcd`**). **`origin/sub/AST-379/AST-457-manage-candidate-board-searches` is stale** (points at an ancestor already on `origin/dev`); Katherine’s publish tip for diff review is **`ftr/AST-457`** only.

### What's solid

| Area | Notes |
|------|--------|
| Navigation | `NAV_CONFIG` swaps Title Patterns → Board Searches; no hardcoded sidebar in React beyond route wiring. |
| List UX | `CandidateBoardSearches` exposes label, friendly board label, created, updated — action column separate; matches AC list shape. |
| Layering | `api_boards` → `boards` core → `database`; UI API does not import `data` / `external`. |
| Mutually exclusive payloads | POST/PATCH reject mixed criteria + deeplink; UI confirms before clearing on mode flip. |
| Authority | Duplicate detection + deeplink domain checks live server-side (`boards.save_board_search` / `update_board_search`). |
| Board catalog | `/api/boards` + `list_adopted_boards()` keep adopted filter in config resolution. |

### Issues

| Severity | Bucket | Finding |
|---------|--------|---------|
| **fix-now** | **D2** (`ASTRAL_CODE_RULES` §1.5 / rubric silent failure) | `database._parse_board_search_row`: on invalid stored `criteria` JSON, `except json.JSONDecodeError: pass` leaves the broken string — no stderr fallback, counter, or re-raise. Treat as swallowed parse error unless an approved rubric tradeoff comment exists. Prefer: leave invalid rows visible to API as error once, or log + coerce with explicit sentinel. |
| **discuss** | Plan fidelity | Approved plan Stage 2 documents **`/api/candidates/<id>/board_searches/*`** on `api_candidate.py`. Shipped **`/api/boards/searches`** (+ `candidate_id` query/body) and **`api_boards`**. Behavior is coherent; reconcile plan doc vs code for the next engineer / UAT binder. |
| **discuss** | Plan fidelity | Same plan appendix once said **no `tests/`** on this ticket; diff adds substantive backend + frontend tests (`test_board_search_integration.py`, `test_boards.py`, page test). Workflow likely superseded Betty ownership rules — confirm no double-count expectations. |
| **discuss** | Scope footprint | Latest commit message cites board gaze ingest, tracker/agent chain tokens, and admin task UI — broader than “thin glue.” Likely intentional integration debt; verify parent **AST-379** accepts **459** coupling in this slice. |
| **discuss** | UI resilience | `loadBoards()` uses `.catch(() => setBoards([]))` — network failures show an empty picker with **no toast** (silent empty). Consider surfacing fetch errors like `loadSearches`. |
| **advisory** | B1 polish | Core `extract_board_listings` / `run_board_search_gaze`: function-scoped `playwright`/core imports justified for lazy boundaries — consider a one-line comment (cycle break vs heavy dep) to match rubric. |
| **advisory** | API hygiene | `api_boards` imports **`_PATCH_UNSET`** and **`_BOARD_SEARCH_TASK_KEYS`** from `core.boards` (private symbols). Works, but brittle; prefer small public façade constants or literals in API layer. |

### Recommended actions

1. **`fix-now`:** Replace criteria JSON **`JSONDecodeError: pass`** with bounded behavior documented in §1.5 / §5b justification chain (fail row load, coerce to `{}` with explicit comment, or structured log).
2. **`discuss`:** Update this plan’s Stage 2 table **or** add a short “Shipped contract” section listing actual `/api/boards` paths.
3. **Process:** Repoint or delete stale **`origin/sub/AST-379/AST-457-manage-candidate-board-searches`** if sub-branch law still applies, so the next reviewer does not get an empty three-dot diff.

**Built by Katherine.** Branch `ftr/AST-457`.

---

## Resolution

**2026-05-24** (`resolve-astral`, Katherine) — closes Radia **`review-astral`** findings for **AST-457** vs parent **AST-379**.

| Review item | Outcome |
|-------------|---------|
| **D2 fix-now** — silent `JSONDecodeError` in **`_parse_board_search_row`** | **Structured `_log.error` + `ValueError`** so corrupt stored `criteria` fails loud (no silent `pass`). Aligns with **ASTRAL_CODE_RULES** §1.5 / rubric. |
| Discuss — Stage 2 plan vs **`/api/boards/searches`** | **Shipped contract** subsection added under Stage 2 documenting actual **`api_boards`** routes. |
| Discuss — Betty tests vs plan “no tests/” | **Documented here:** Betty owns **`tests/`** and bible updates per **`qa-astral`** / **`test-astral`**; Katherine does not ship test-tree edits on resolve. Earlier plan exclusion superseded when **AST-458** integration landed. |
| Discuss — gaze/tracker/agent “thin glue” | **Recorded:** coupling is intentional for **457** stacked with **455/459** on the same publish line; UAT breadth remains **AST-459** parent context. |
| Discuss — **`loadBoards`** silent empty | **`loadBoards`** now surfaces **`!r.ok` and network errors via toast**, matching **`loadSearches`**. |
| Advisory **B1** — lazy imports in **`extract_board_listings`** / **`run_board_search_gaze`** | **One-line rubric comments** on lazy imports (heavy Playwright stack + dispatcher import-graph). |
| Advisory — **`api_boards`** **`_PATCH_UNSET`** / **`_BOARD_SEARCH_TASK_KEYS`** | **Deferred:** small façade would touch **`api_boards`** surface without product behavior gain; tracked as hygiene follow-up if core exports a public sentinel. |

**Publish:** **`ftr/AST-457`** after cherry-pick of **`fix(AST-457): review feedback`** from **`dev-kath`**.
