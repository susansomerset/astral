# AST-329 Entity Page Revamp — Plan

## Context

AST-330 landed the `agent_responses` TABLE (full audit blobs), `agent_data` TABLE (individual content blocks by BLOCK_TYPE), and the `agent_responses` JSON **column** on entity rows (lightweight refs with `prompt_blocks` foreign keys into `agent_data`). This ticket wires the UI side: every entity modal gets a side-tabbed layout matching the Artifacts screen chrome, with a metadata first tab and time-ordered agent story tabs after.

Candidate is already a full-page experience — no changes.

---

## Data Architecture (§2.4.1)

The entity row's `agent_responses` column holds lightweight refs:

```json
[
  {
    "batch_id": "prefilter-3f8a-...",
    "task_key": "prefilter_company",
    "created_at": "2026-03-19 14:32:00",
    "entity_cost": 0.0042,
    "prompt_blocks": [
      {"type": "SYSTEM",   "id": "prefilter-3f8a-...-system-abc123"},
      {"type": "CACHE_A",  "id": "prefilter-3f8a-...-cache_a-def456"},
      {"type": "NO_CACHE", "id": "prefilter-3f8a-...-no_cache-ghi789"},
      {"type": "NO_CACHE", "id": "prefilter-3f8a-...-no_cache-jkl012"},
      {"type": "RESPONSE", "id": "prefilter-3f8a-...-response-mno345"}
    ]
  }
]
```

Each `id` is a primary key in `agent_data`. To display the block tabs, we collect all IDs across all entries and fetch in a single query. This is the §2.4.1-compliant path — the `agent_responses` TABLE's `runtime_prompt` blob (which uses different label names: `system_prompt`, `cached_context`, etc.) is **not** used for the block tab display.

Note: `_store_prompt_blocks` stores `user_content` (static task instructions) as a second `NO_CACHE` block alongside `nocache_content`. The display handles duplicate block types by appending a counter: `NO_CACHE`, `NO_CACHE (2)`.

---

## Design Decisions — All Confirmed

| # | Decision | Resolution |
|---|---|---|
| 1 | SideTabPanel: extend vs. new component | **Option A — extend SideTabPanel.** Add optional `renderContent` + make `onChange` optional. |
| 2 | Agent response tab ordering | **Oldest-first.** Tab label = `task_key` alone. |
| 3 | Agent response top tabs | **One tab per block in `prompt_blocks`.** Labels = BLOCK_TYPE (SYSTEM, CACHE_A, NO_CACHE, TASK, RESPONSE). Duplicate types get `(2)` suffix. Block content = plain text `pre-wrap`; RESPONSE = pretty JSON `<pre>`. |
| 4 | Company Summary tab layout | **Two-column.** Left: editable fields (name, website, job page, short name — editable until WATCH). Right: job state distribution + state history timeline. Save/Cancel in footer. |
| 5 | Job Info tab layout | **Two-column.** Left: metadata + Skip button. Right: state history timeline. Grade dots deferred. |
| 6 | Skip state | **`CANDIDATE_SKIPPED`** — new state in `JOB_STATES` + `SKIPPED_STATES`. |
| 7 | Modal width | **`size?: "wide"`** on Modal. Wide = `width: min(1060px, 92vw); max-height: 88vh`. |
| 8 | Candidate entity | **No changes.** Already a full page. |
| API payload | Strip or keep blobs | **Keep all.** Detail endpoints are one-at-a-time fetches. |

---

## Implementation Steps

### Step 0 — `src/utils/config.py`

Add `"CANDIDATE_SKIPPED": {}` to `JOB_STATES`. Add `"CANDIDATE_SKIPPED"` to `SKIPPED_STATES`.

---

### Step 1 — `src/data/database.py`

**1a.** Add `get_company_job_counts(short_name: str) -> dict[str, int]`:
```python
SELECT state, COUNT(*) FROM job WHERE company = ? GROUP BY state
```

**1b.** Add `get_agent_data_for_ids(ids: list[str]) -> dict[str, dict]`:
- Single query: `SELECT * FROM agent_data WHERE agent_data_id IN (...)`
- Returns `{agent_data_id: row_dict}` with `block_data` decompressed.
- Returns `{}` if `ids` is empty (no query issued).

---

### Step 2 — `src/core/roster.py`

Add imports: `list_agent_responses`, `get_company_job_counts`, `get_agent_data_for_ids` from `src.data.database`.

Add helpers:

```python
def get_company_job_state_counts(short_name: str) -> dict:
    return get_company_job_counts(short_name)

def get_entity_agent_story(entity: dict) -> list:
    """Expand the entity's agent_responses column entries with their block data.
    Returns list of entries with blocks=[{type, block_data}] injected."""
    entries = entity.get("agent_responses") or []
    all_ids = [b["id"] for e in entries for b in (e.get("prompt_blocks") or [])]
    blocks_by_id = get_agent_data_for_ids(all_ids) if all_ids else {}
    result = []
    for entry in entries:
        type_counts: dict[str, int] = {}
        expanded = []
        for ref in (entry.get("prompt_blocks") or []):
            btype = ref["type"]
            type_counts[btype] = type_counts.get(btype, 0) + 1
            label = btype if type_counts[btype] == 1 else f"{btype} ({type_counts[btype]})"
            row = blocks_by_id.get(ref["id"])
            expanded.append({"type": btype, "label": label,
                              "block_data": row["block_data"] if row else None})
        result.append({**entry, "blocks": expanded})
    return result
```

---

### Step 3 — `src/ui/api/api_companies.py`

Import `get_company_job_state_counts`, `get_entity_agent_story` from `src.core.roster`.

In `detail(short_name)`:
```python
company["job_state_counts"] = get_company_job_state_counts(short_name)
company["agent_story"]      = get_entity_agent_story(company)
```

---

### Step 4 — `src/ui/api/api_jobs.py`

Import `get_entity_agent_story` from `src.core.roster`.

In `detail(astral_job_id)`:
```python
job["agent_story"] = get_entity_agent_story(job)
```

---

### Step 5 — `src/ui/frontend/src/components/Modal.tsx`

Add `size?: "wide"` to `ModalProps`. Apply `.modal-card--wide` CSS class when `size === "wide"`.

---

### Step 6 — `src/ui/frontend/src/components/SideTabPanel.tsx`

- Make `onChange` optional (`onChange?: (tabs: SideTab[]) => void`), default to no-op.
- Add `renderContent?: (tabId: string) => ReactNode` to props.
- In the content pane: if `renderContent` is provided, call `renderContent(activeTab.id)` instead of rendering `LabeledTextArea`.
- No changes to `SideTab` interface. No changes to existing callers (`ArtifactEditor` etc.) — `onChange` is still accepted, `renderContent` is absent, existing behavior unchanged.

---

### Step 7 — `src/ui/frontend/src/components/CompanyDetailModal.tsx`

Full rewrite. Props: `shortName: string | null`, `onClose`, `onSaved`.

Fetch-on-open: `GET /api/companies/<shortName>` when `shortName` changes.

`SideTabPanel` with `renderContent`:
- Tab `"summary"` → renders Summary content (Decision 4 layout).
- Tabs `entry.batch_id` (one per `agent_story` entry, oldest-first) → renders agent story content.

**Summary tab content:**
- Two-column: Left = detail fields (company_name, website, job_site, short_name — inputs when non-WATCH, spans when WATCH). Right = job state distribution table + state history timeline.
- Save/Cancel remain in Modal footer.

**Agent story tab content (per entry):**
- Header row: `task_key`, `created_at` timestamp, `entity_cost`.
- `TabBar` over `entry.blocks`: each block = one top tab, label = `block.label`.
- Active block content: `<pre className="agent-response-pre">{block.block_data}</pre>`.
- RESPONSE block: pretty-print as JSON if parseable, else plain text.

---

### Step 8 — Company list pages (4 files)

`CompaniesWatchList`, `CompaniesNewList`, `CompaniesInactiveList`, `CompaniesIgnored`:
- `viewing: Company | null` → `viewingId: string | null`
- `onRowClick={row => setViewingId(row.short_name)}`
- `<CompanyDetailModal shortName={viewingId} ... />`

---

### Step 9 — `src/ui/frontend/src/components/JobDetailModal.tsx`

Full rewrite. Props: `jobId: string | null`, `onClose`.

Fetch-on-open: `GET /api/jobs/<jobId>`.

`SideTabPanel` with `renderContent`:
- Tab `"info"` → Info content (Decision 5 layout).
- Tabs `entry.batch_id` (agent story, oldest-first) → same agent story block-tab pattern as Company.

**Info tab content:**
- Two-column: Left = title, company, state, link (clickable), date scraped, date updated, Skip This Job button. Right = state history timeline.
- Skip button: `POST /api/jobs/bulk_state` with `{astral_job_ids: [job.astral_job_id], to_state: "CANDIDATE_SKIPPED"}` then `onClose()`. Hidden when `job.state === "CANDIDATE_SKIPPED"`.

---

### Step 10 — `src/ui/frontend/src/App.css`

Add Section 14 — Entity Pages:
- `.modal-card--wide` — wide modal dimensions
- `.agent-response-pre` — scrollable `<pre>` for block content
- `.agent-response-header` — task_key + timestamp + cost strip
- `.job-info-cols`, `.job-info-meta`, `.job-info-history` — Info tab two-column layout
- `.company-summary-cols`, `.company-summary-fields`, `.company-summary-right` — Summary tab two-column layout
- `.job-count-table` — company job state distribution
- `.skip-job-btn` — Skip button styling

---

## Files Changed

| File | Action |
|---|---|
| `src/utils/config.py` | Add `CANDIDATE_SKIPPED` to `JOB_STATES` + `SKIPPED_STATES` |
| `src/data/database.py` | Add `get_company_job_counts`, `get_agent_data_for_ids` |
| `src/core/roster.py` | Add `get_company_job_state_counts`, `get_entity_agent_story` |
| `src/ui/api/api_companies.py` | Attach `job_state_counts` + `agent_story` to detail endpoint |
| `src/ui/api/api_jobs.py` | Attach `agent_story` to detail endpoint |
| `src/ui/frontend/src/components/Modal.tsx` | Add `size="wide"` prop |
| `src/ui/frontend/src/components/SideTabPanel.tsx` | Add `renderContent`, make `onChange` optional |
| `src/ui/frontend/src/components/CompanyDetailModal.tsx` | Full rewrite |
| `src/ui/frontend/src/pages/CompaniesWatchList.tsx` | Pass `shortName` |
| `src/ui/frontend/src/pages/CompaniesNewList.tsx` | Pass `shortName` |
| `src/ui/frontend/src/pages/CompaniesInactiveList.tsx` | Pass `shortName` |
| `src/ui/frontend/src/pages/CompaniesIgnored.tsx` | Pass `shortName` |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Full rewrite |
| `src/ui/frontend/src/App.css` | Add Section 14 — Entity Pages |

---

## Code Rules Review

### §1.1 Scope and Isolation
Pass. Only files directly involved in entity page display. No new tables. `agent_data` is in the database.py header inventory.

### §1.3 DRY
Pass. `get_entity_agent_story` is a single shared function used by both company and job detail endpoints. Agent story tab rendering is a single shared React component used by both modals.

### §1.4 No Hardcoded Sets
Pass. `CANDIDATE_SKIPPED` is added to `JOB_STATES` and `SKIPPED_STATES` in config — not hardcoded in any component. Block type labels derive from the data, not a hardcoded array.

### §2.4.1 Entity Agent Responses
Pass. Uses the entity row's `agent_responses` column + `agent_data` block IDs — the §2.4.1-specified path. Does **not** use `runtime_prompt` blob from the `agent_responses` TABLE for block display.

### §2.6 State Machine
Pass. `CANDIDATE_SKIPPED` added to config. The Skip button calls the existing `bulk_state` endpoint — no new state transition logic.

### §2.9 Auth
Pass. No new unprotected endpoints. Existing `@require_auth` on detail endpoints covers the added fields.

### §3.2 Layer Rules
Pass. `get_entity_agent_story` lives in `src/core/roster.py` (core layer). API layer imports from core only. `get_agent_data_for_ids` lives in the data layer. No UI component imports from data or external layers.

### §3.3 Import Rules
Pass. `api_companies.py` and `api_jobs.py` import from `src.core.roster` (core) — compliant. `roster.py` imports from `src.data.database` — compliant.

### §3.5 Naming
Pass. No new route paths. CSS classes kebab-case. New functions snake_case. Component files PascalCase.

---

## Code Review

**Commit:** `26c1d5a`
**Branch:** `dev-refactor-agent-data`
**Reviewed:** 2026-03-19

---

## What's Solid

- **Config changes clean.** `CANDIDATE_SKIPPED` added to both `JOB_STATES` and `SKIPPED_STATES` in config — not hardcoded anywhere else.
- **Modal + SideTabPanel extensions are backward-compatible.** `size="wide"` on Modal and `renderContent` / optional `onChange` on SideTabPanel are purely additive. Existing callers (ArtifactEditor etc.) unchanged. All `onChange` call sites switched to optional chaining (`onChange?.(...)`).
- **Company list pages updated consistently.** All 4 pages follow the identical pattern: `viewing: string | null`, `onRowClick` extracts `short_name`, `CompanyDetailModal shortName={viewing}`. Minimal, uniform diffs.
- **Fetch-on-open pattern is correct.** Both modals fetch fresh data when `shortName`/`jobId` changes, with loading/error state handling. CompanyDetailModal clears stale data when `shortName` becomes null.
- **CSS is well-organized.** Section 14 uses semantic class names (`entity-summary`, `entity-story-tab`), CSS custom properties throughout, flex-based layouts that play well with the wide modal constraint.
- **`get_company_job_counts` is clean.** Simple `GROUP BY state` aggregation, proper connection management, exact SQL from the plan.
- **`get_agent_data_for_ids` is efficient.** Single batch query with `IN (?)` placeholders, empty-list guard, `block_data` decompressed transparently. Returns keyed dict for O(1) lookups.
- **Skip button UX is good.** Three states: active, skipping (disabled + "Skipping…"), already-skipped (disabled + "Already Skipped"). `onClose()` triggers list reload in the parent.
- **`DetailRow` helper extracted.** Reduces repetition within the Company SummaryTab. Clean.
- **Agent story tab rendering.** `TabBar` for block sub-tabs, `textarea.readOnly` for content display, meta header strip with task_key/timestamp/performance — matches the plan's design intent.
- **Side-tab labels.** Summary/Info as first tab, then one tab per agent story entry with `task_key` as label, oldest-first ordering. Matches Decision 2.

---

## Issues

### Issue 1 — Wrong data source: `get_entity_agent_story` reads TABLE instead of entity column 🔴 fix now

The plan (§Data Architecture, Step 2) specifies reading from the entity's `agent_responses` JSON **column** — the lightweight refs that contain `prompt_blocks` with `{type, id}` references into `agent_data`. The implementation reads from `list_agent_responses(entity_type, entity_id)`, which queries the `agent_responses` **TABLE**.

The TABLE schema has columns: `id, task_key, entity_type, entity_id, status, failure_note, raw_response, parsed_response, runtime_prompt, request_id, created_at`. It does **not** have a `prompt_blocks` column.

So `r.get("prompt_blocks")` returns `None` for every row, `blocks` is always `[]`, and every agent story tab renders **"No prompt blocks recorded."** The entire block-tab display (SYSTEM, CACHE_A, NO_CACHE, TASK, RESPONSE sub-tabs) is silently non-functional.

The plan's signature is `get_entity_agent_story(entity: dict)` — accepting the already-fetched entity dict whose `agent_responses` column **does** contain `prompt_blocks`. The implementation changed the signature to `(entity_type: str, entity_id: str)`, bypassing the entity column entirely.

The API callers already have the entity dict in hand (`company` / `job`) and could pass it directly as the plan intended.

### Issue 2 — `AgentStoryTab` + interfaces duplicated across both modals 🔴 fix now — §1.3 DRY

`CompanyDetailModal.tsx` (lines 209-242) and `JobDetailModal.tsx` (lines 162-195) contain **identical** `AgentStoryTab` components. The `AgentBlock` and `AgentStoryEntry` interfaces are also duplicated at the top of both files.

The plan's Code Rules Review (§1.3) specifically claims: "Agent story tab rendering is a single shared React component used by both modals." The implementation doesn't follow through — the component exists in two places. Extract `AgentStoryTab` (and its interfaces) to a shared file.

### Issue 3 — Skip endpoint doesn't update `state_history` ℹ️ advisory

`skip_job` calls `save_job(astral_job_id, state="CANDIDATE_SKIPPED")` without passing `state_history` or `state_changed_at`. Since `save_job` only updates these when explicitly provided, the CANDIDATE_SKIPPED transition won't appear in the StateTimeline component shown on the Info tab.

Pre-existing: `bulk_state` has the same gap. But the plan puts StateTimeline prominently on the Job Info tab, making the missing skip entry more visible. A follow-up to both endpoints to append to `state_history` would fix this consistently.

### Issue 4 — New `POST /<id>/skip` endpoint instead of plan's `bulk_state` approach ℹ️ advisory

The plan says: "Skip button: `POST /api/jobs/bulk_state` with `{astral_job_ids: [job.astral_job_id], to_state: 'CANDIDATE_SKIPPED'}`." The implementation adds a dedicated `POST /<id>/skip` endpoint instead. The new endpoint is cleaner for single-job skip and avoids array wrapping, but it's a plan deviation. Both approaches are functionally equivalent (both call `save_job` directly).

### Issue 5 — New database functions skip `_run_with_retry` ℹ️ advisory

`get_company_job_counts` and `get_agent_data_for_ids` manually manage connections without `_run_with_retry`. Other database functions (e.g., `list_agent_responses`) use `_run_with_retry` for transient SQLite locking errors. For read-only queries this is low-risk, but inconsistent with the existing pattern.

### Issue 6 — `prefilter_company_notes` dropped from Company modal ℹ️ advisory

The previous `CompanyDetailModal` displayed `prefilter_company_notes` as a detail row. The new SummaryTab omits it. If intentional (keeping the summary clean), fine — but it's a minor data regression for companies that have prefilter notes.

---

## Recommended Actions

| # | Severity | Action |
|---|----------|--------|
| 1 | Fix now | Revert `get_entity_agent_story` to the plan's approach: accept `entity: dict`, read `entity.get("agent_responses")` column, extract `prompt_blocks` IDs, batch-fetch from `agent_data`. Remove `list_agent_responses` import from roster.py. Update API callers to pass entity dict. |
| 2 | Fix now | Extract `AgentStoryTab`, `AgentBlock`, `AgentStoryEntry` to a shared component file. Import in both modals. |
| 3 | Advisory | Add `state_history` append + `state_changed_at` to `skip_job` (and optionally `bulk_state`) so StateTimeline reflects the skip transition. |
| 4 | Advisory | No action needed — dedicated skip endpoint is a reasonable deviation. |
| 5 | Advisory | Wrap `get_company_job_counts` and `get_agent_data_for_ids` inner functions with `_run_with_retry` for consistency. |
| 6 | Advisory | Add `prefilter_company_notes` back to SummaryTab, or confirm the omission is intentional. |

---

## Recheck — `155a11b`

**Reviewed:** 2026-03-19

All five addressed issues verified clean:

| # | Status | Notes |
|---|--------|-------|
| 1 | ✅ Resolved | `get_entity_agent_story(entity: dict)` now reads `entity.get("agent_responses")` column. `list_agent_responses` import removed from roster.py. API callers pass entity dict. Block-tab display is now functional. |
| 2 | ✅ Resolved | `AgentStoryTab.tsx` created with exported component + interfaces. Both modals import from shared file. `TabBar` import removed from both modals. |
| 3 | ✅ Resolved | `skip_job` appends `{to_state, timestamp}` to `state_history` and sets `state_changed_at`. Uses `datetime.now(timezone.utc)`. StateTimeline will now show skip transitions. |
| 5 | ✅ Resolved | Both `get_company_job_counts` and `get_agent_data_for_ids` restructured to `_run_with_retry` pattern. |
| 6 | ✅ Resolved | `prefilter_company_notes` restored to SummaryTab as a conditional `DetailRow`. |

No new issues introduced. No remaining blockers.
