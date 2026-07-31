# AST-1100 — Resolve artifact bodies from pinned agent_data_id for UAT surfaces

**Linear:** [AST-1100](https://linear.app/astralcareermatch/issue/AST-1100/resolve-artifact-bodies-from-pinned-agent-data-id-for-uat-surfaces-job)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved) (AC reference only)

**Publish ref:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`

After AST-1099 pins RESPONSE `agent_data_id` under `job_data.artifacts.job_resume` / `cover_letter` / `proposed_answers`, UAT surfaces (JAR Artifacts tabs, print/Materials Preview, job HTML builders) must load the hop body via existing `agent_data` read paths — no manual PUT of the response JSON onto the job row.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Remap `JOBS_RECOMMENDED_ARTIFACT_TABS` `artifact_key` values to the three pin slots | utils |
| `src/core/tracker.py` | Add pin→body resolve + display hydrate helpers (read-only overlay; coat-check empty) | core |
| `src/core/builder.py` | Prefer resolved pin bodies for job resume / cover letter HTML when legacy body dicts are absent | core |
| `src/ui/api/api_jobs.py` | Hydrate artifacts on job GET; accept PUT for remapped keys (map to existing body saves) | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Visibility helpers use remapped pin keys (after hydrate, values are bodies) | ui |
| `tests/component/frontend/fixtures/stateUiManifestFixture.ts` | Align fixture `artifact_key`s with remapped tabs (Betty may own; list for completeness — engineer does not edit `tests/` unless Betty already landed; if fixture blocks FE typecheck in-tree, stop and hand off) | — |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| Writing / mid-chain pin of `agent_data_id` | AST-1099 (already on `ftr`) |
| TASK_CONFIG `persist_in` | parent forbids |
| Unrelated JAR chrome / tab redesign beyond these three pointers | excluded |
| Session cover letter / session resume paste | excluded |
| `tests/` / `docs/test-bible/**` product coverage | Betty |

## Stage 1: Config — remap JAR artifact tab keys

**Done when:** `JOBS_RECOMMENDED_ARTIFACT_TABS` points Job Resume / Cover Letter / Application Questions at `job_resume` / `cover_letter` / `proposed_answers`; `shapes_key` for cover stays `"cover_letter"`; Job Resume keeps `use_resume_structure: True`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, change `JOBS_RECOMMENDED_ARTIFACT_TABS` to:

```python
JOBS_RECOMMENDED_ARTIFACT_TABS = [
    {
        "tab_id": "artifact_resume",
        "nav_label": "Job Resume",
        "artifact_key": "job_resume",
        "shapes_key": None,
        "use_resume_structure": True,
    },
    {
        "tab_id": "artifact_cover",
        "nav_label": "Cover Letter",
        "artifact_key": "cover_letter",
        "shapes_key": "cover_letter",
        "use_resume_structure": False,
    },
    {
        "tab_id": "artifact_application",
        "nav_label": "Application Questions",
        "artifact_key": "proposed_answers",
        "shapes_key": None,
        "use_resume_structure": False,
    },
]
```

⚠️ **Decision:** Remap to the AST-1099 pin slot names (not keep `resume_content` / `application_responses` as tab keys). Legacy body keys remain on the job for older rows and for PUT body-storage aliases in Stage 3; display hydrate (Stage 2) bridges pin → body for the remapped keys.

## Stage 2: Tracker — resolve pin id → body + display hydrate

**Done when:** Given a non-empty pin string, resolve returns the parsed RESPONSE body from `agent_data` (same parse spirit as mid-chain hydration); blank/missing id or missing row returns `None` without writing; hydrate returns a shallow-copied `artifacts` dict where each pin-slot string is replaced by the resolved body when resolve succeeds; `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py`, next to `pin_job_artifact_agent_data_id`, add:

   - `resolve_job_artifact_agent_data_body(agent_data_id: Any, *, debug: bool = False) -> Any`:
     - Coat-check: blank/None/whitespace → return `None` (optional Style D skip when `debug=True`: `artifact_resolve skipped reason=empty_agent_data_id`).
     - Load row via existing data API already used by core: `from src.data.database import get_agent_data` (or the same import path `agent.py` uses as `_get_agent_data_row`) — **one id**.
     - If row missing → `None` (skip reason `missing_agent_data_row`).
     - Take `block_data` (or `content`) text; if empty → `None`.
     - Parse with the same rules as `src.core.agent._parsed_response_from_stored_response_text` — **lazy-import** that helper from `src.core.agent` (cycle-safe) OR duplicate the tiny JSON/`agent_payload` unwrap inline in tracker to avoid import cycles. Prefer lazy-import of the existing helper.
     - When `debug=True`: Style D `artifact_resolve agent_data_id=<id> recorded` (or skip). No ungated `[DEBUG]` spam.

   - `hydrate_job_artifacts_for_display(artifacts: Any, *, debug: bool = False) -> Dict[str, Any]`:
     - If `artifacts` is not a dict → return `{}`.
     - Shallow-copy the dict.
     - For each pin key in `("job_resume", "cover_letter", "proposed_answers")`:
       - If value is a non-empty `str`: `body = resolve_job_artifact_agent_data_body(value, debug=debug)`; if `body is not None`, set `out[key] = body`.
       - If value is already a non-empty dict/list (legacy body still under `cover_letter`), leave it.
     - Do **not** call `save_job_data` — display overlay only; stored pins stay strings on disk.

2. Export / use only from core + ui (API). No new TASK_CONFIG fields.

⚠️ **Decision:** Hydrate is response-overlay only. Editing via PUT may replace a pin string with a body dict on that key (Stage 3); initial UAT after a successful chain must work with zero PUTs.

## Stage 3: API — hydrate on job GET; PUT aliases for remapped keys

**Done when:** `GET /api/jobs/<astral_job_id>` returns `job_data.artifacts` after `hydrate_job_artifacts_for_display`; PUT endpoints exist (or alias) so ArtifactEditor can save under remapped keys without 404; `python3 -m py_compile src/ui/api/api_jobs.py` passes.

1. In `src/ui/api/api_jobs.py`, locate the single-job GET handler that returns the job JSON used by `JobAnalysisReportModal` / `ArtifactEditor` (`GET /api/jobs/<id>`). After loading the job row and before `jsonify`:
   - Copy `job_data` if needed; replace `artifacts` with `hydrate_job_artifacts_for_display(get_job_artifacts(job) or artifacts_dict)`.
   - Do not persist the hydrated copy.

2. PUT aliases (ArtifactEditor posts to `/api/jobs/<id>/artifacts/<artifactKey>`):
   - Keep existing `resume_content` / `cover_letter` / `application_responses` routes.
   - Add (or generalize) routes so `job_resume` and `proposed_answers` accept the same body shapes:
     - `PUT .../artifacts/job_resume` → same implementation as `put_job_resume_content` (calls `save_job_artifact_resume_content`) **and/or** also write the dict onto `artifacts.job_resume` if you choose body-on-pin-key — **pick one**:
       - **Required choice:** `PUT job_resume` calls `save_job_artifact_resume_content` (legacy `resume_content` body store) **and** does not clear `job_resume` pin string if still present — wait: `save_job_artifact_resume_content` only merges `resume_content`. After remap, ArtifactEditor reads `job_resume` from hydrated GET. On save it PUTs to `job_resume`. Implement `PUT job_resume` to: validate dict body; `save_job_data(..., {"artifacts": {"job_resume": body}})` (body dict replaces pin — acceptable after human edit) **OR** save to `resume_content` and leave pin. **Use:** write the edited dict to `job_resume` via `save_job_data` (same key the tab reads). Mirror for `proposed_answers` (dict/list as today for application responses). `PUT cover_letter` already exists — leave it (dict overwrites pin string after edit).

3. Do not add new JAR routes beyond these aliases / hydrate.

## Stage 4: Builder — HTML preview resolves pins

**Done when:** `build_resume(job_id)` / cover-letter HTML path can render from a pin when `resume_content` / cover body dict is missing; `python3 -m py_compile src/core/builder.py` passes.

1. In `src/core/builder.py` `_resolve_resume_sections`:
   - After checking `artifacts.resume_content`, if missing/empty: if `artifacts.job_resume` is a non-empty string, `body = resolve_job_artifact_agent_data_body(...)` (lazy-import from tracker); if body is a non-empty dict, use it; else fall through to `base_resume`.
2. In `_resolve_cover_letter`:
   - If `artifacts.cover_letter` is a non-empty string pin, resolve to body; if dict with fields, normalize via existing `_cover_letter_fields_for_read` / `normalize_cover_letter_artifact` as appropriate; if resolve fails, keep existing sample_cover fallback.

## Stage 5: Frontend visibility helpers

**Done when:** Print / Materials Preview / `anyReportArtifactContent` gate on the remapped keys; hydrated GET bodies (dicts) still count as content; `artifactHasContent` also treats a non-empty string as content (pin present even if hydrate skipped); no other JAR chrome changes.

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`:
   - Update `artifactHasContent`: after the object/array branches, if `typeof raw === "string"` return `raw.trim().length > 0`.
   - `printResumeVisible` → `artifactHasContent(artifacts, "job_resume")` (fallback: also true if legacy `resume_content` has content — `artifactHasContent(..., "job_resume") || artifactHasContent(..., "resume_content")`).
   - `printCoverVisible` → keep `"cover_letter"` (pin or body).
   - `materialsPreviewVisible` → use the same resume/cover checks as above.
2. Do **not** redesign `JobAnalysisReportModal` section layout — it already iterates `report_artifact_tabs` from the manifest.

## Self-Assessment

**Scope — Single-Component:** Config tab remap + tracker resolve/hydrate + builder pin read + jobs API GET/PUT aliases + small FE visibility helpers for the three pin slots.

**Conf — high:** Reuses `get_agent_data` / `_parsed_response_from_stored_response_text` and existing JAR tab/ArtifactEditor wiring; AST-1099 already defines slot names and stops body-copy on finalize hops.

**Risk — Medium:** Wrong parse of RESPONSE text leaves tabs empty after a successful chain; GET hydrate bugs could mask stored pins; PUT overwrite of `cover_letter` pin with an edited dict is intentional after human edit.

## Code rules check

| Rule | Notes |
|------|-------|
| §1.3 DRY | One resolve helper; builder + API call it |
| §2.1 config | Tab keys only in `JOBS_RECOMMENDED_ARTIFACT_TABS` |
| §2.4.1 entity-agent-responses-latest-only | Body stays in `agent_data`; job holds pointer until edit |
| coat-check-never-store-empty | Resolve skips blank ids; hydrate does not write empties |
| §3.3 import-direction | UI → core → data; lazy imports for cycles |
| in-scope-only | Three UAT surfaces / three pin keys only |

## Review

**Branch:** `sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`  
**Code:** `b6be8d5e`  
**Publish tip reviewed:** `7eb0759b` (`merge-tests(AST-1100)`)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1100  
**Overall:** DISCUSS

### What’s solid
- Tab remap to AST-1099 pin slots; GET hydrate via core helper; PUT aliases under remapped keys with `@require_auth`.
- `resolve_job_artifact_agent_data_body` coat-checks blank/missing; Style D gated; lazy agent parse import documented.
- Builder prefers legacy body then pin resolve then fallback; FE visibility accepts pin strings + hydrated bodies.
- UI imports core only (no `src.data` / `src.external`); Betty owns tests/bible + fixture align.

### Issues
**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket` and `astral.debug.spikes-under-debug-dir`; ticket-scoped diff makes them in-scope. Both **conform**. No product fix-now.

### Recommended actions
- Engineer: no fix-now. Acknowledge stragglers on resolve-child / move to User Testing if no disagreement.
- Pointer overwrite on human PUT remains intentional (plan Medium risk).

### Notes
- Statute applies_when + product judgment used AST-1100 commit change set (formal `origin/dev...` three-dot may include epic ancestry).
- Plan-rubric verdict attached (Joan APPROVED). Active statute set count=57 (includes `astral.dispatch.seed-auto-false`).

context_tokens≈45000

— Radia
