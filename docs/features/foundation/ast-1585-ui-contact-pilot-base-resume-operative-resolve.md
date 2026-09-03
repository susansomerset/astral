# UI + Contact pilot base_resume operative resolve

**Linear:** [AST-1585](https://linear.app/astralcareermatch/issue/AST-1585/ui-contact-pilot-base-resume-operative-resolve-implement)
**Parent:** [AST-1571](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative) — Implement patt.artifact.read-operative
**Publish ref:** `sub/AST-1571/AST-1585-ui-contact-pilot-base-resume-operative-resolve`

After sibling AST-1584 (`get_operative_base_resume`), wire Contact Estelle and the job artifact-building UI (JAR + needed candidate/jobs API) onto the same pin→body read-operative path for pilot `candidate.artifacts.base_resume`. Remove blob dotted-path reads for that pinned content on those surfaces. Does **not** persist seed artifact ids (traceability), does **not** touch `candidate.py` / `database.py`, and does **not** add `artifact_id` on ordinary save responses.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/contact.py`
- `src/ui/api/api_jobs.py` and/or `src/ui/api/api_candidate.py`
- `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (and any thin report helper already used for job artifact tabs)

Every row in **Files Changed** is one of those paths (plus this plan doc). Technical kinds match: Contact calls the existing candidate pin→body helper (no blob fallback on that path); API exposes pin-in / body-out; JAR renders via that API when a pin is supplied.

**Depends on:** AST-1584 on epic tip (`get_operative_base_resume` already on `origin/ftr/AST-1571-read-operative`). Sync via `sync-child.sh` with `--ftr AST-1571-read-operative` before coding.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/contact.py` | Pin→body resolve for Estelle (helper call + ownership); strip blob `artifacts.base_resume` from token raft on operative path; dispatch short-circuit for pin UUID / refuse blob path | core |
| `src/ui/api/api_candidate.py` | `GET …/operative/base_resume?artifact_id=` → pin-in / body-out via same helper | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Thin fetch helper for operative base_resume JSON | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Artifacts pane: render pinned source base_resume via operative API when pin supplied; gap (no blob) when absent | ui |

**Out of this ticket (do not touch):** `src/data/database.py`; `src/core/candidate.py` (helper already shipped); `src/core/tracker.py`; `ARTIFACT_CONFIG` new keys; grade/analysis pin writers; ordinary-save HTTP `artifact_id` field; writing seed pins onto jobs (traceability); read-current editor hydrate; coat-check; `canon/directives/draft/patt.artifact.read-operative.md` (cite only). Engineer must not create or edit `tests/` or `docs/test-bible/**`.

## Stage 1: Contact — pin→body on Estelle operative path

**Done when:** Estelle’s token raft never dual-reads blob `artifacts.base_resume` for operative grounding; when a pin is supplied, Contact calls `get_operative_base_resume` (same helper UI uses) and injects that body for `{$BASE_RESUME}`; on miss / wrong owner, the raft has no base_resume (gap — no blob fallback); Contact task dispatch resolves a UUID param via the same helper and refuses bare `artifacts.base_resume` blob walks at the Contact layer.

1. In `src/core/contact.py` module docstring, append a one-line note: AST-1585 / `patt.artifact.read-operative` — Estelle pin→body for pilot `base_resume` via `get_operative_base_resume`.

2. Add import: `get_operative_base_resume` from `src.core.candidate` (alongside existing `get_candidate` import). Add `from src.data import database` only if needed for the ownership check in step 3 (core may import data).

3. Add public helper (place with other public Contact entrypoints, before `run_contact_estelle_turn`):

```python
def resolve_pinned_base_resume(
    astral_candidate_id: str,
    artifact_uuid: str,
    *,
    debug: bool = False,
) -> Optional[Any]:
    """Pin→body for pilot base_resume; None on miss / wrong owner / non-pilot.

    Calls candidate.get_operative_base_resume. No candidate_data blob fallback.
    """
```

   Implementation (literal contract):
   - `cid = (astral_candidate_id or "").strip()`; `uid = (artifact_uuid or "").strip()`; if either empty → `None`.
   - `row = database.get_artifact(uid)`; if `row is None` → `None`.
   - If `str(row.get("entity_id") or "").strip() != cid` → `None` (wrong owner).
   - `body = get_operative_base_resume(uid)` (re-applies pilot entity_type / artifact_type gate).
   - When `debug=True`: Style D found/recorded on `contact.resolve_pinned_base_resume` with identifier=`cid[:80]`, found=`artifact_uuid=…`, recorded=`hit=True|False` (no body dump beyond truncate if you log a short preview — prefer hit bool only).
   - Return `body` (may still be `None` if helper rejects type).

4. Add private UUID detector used by dispatch (module-level helper):

```python
_ARTIFACT_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

def _is_artifact_uuid(value: str) -> bool:
    return bool(_ARTIFACT_UUID_RE.match((value or "").strip()))
```

   (`re` is already imported in `contact.py`.)

5. In `run_contact_task_dispatch`, **before** calling the configured tracker handler, when `key == "get_candidate_data"`:

   a. If `_is_artifact_uuid(param)`: treat param as pin. Call `resolve_pinned_base_resume(cid, param.strip(), debug=debug)`. On body not `None` → append/return success row `{"ok": True, "task_key": "get_candidate_data", "result": body}` (same envelope shape as tracker success). On `None` → `{"ok": False, "error": "not_found", "task_key": "get_candidate_data"}`. Do **not** call the tracker handler for this span.

   b. If `param.strip() == "artifacts.base_resume"`: refuse blob dual-read on the Contact operative path — return `{"ok": False, "error": "pin_required", "task_key": "get_candidate_data"}` without calling tracker. (Estelle must pass the artifact uuid pin for historical base_resume.)

   c. All other `get_candidate_data` params → existing handler path unchanged.

6. Change `run_contact_estelle_turn` signature: add optional keyword-only `base_resume_artifact_id: Optional[str] = None` after `candidate_state` (before `debug`).

7. In `run_contact_estelle_turn`, in the “Candidate raft for tokens” block (after loading `candidate_data` from `get_candidate`), **before** `do_task`:

   a. Deep-copy or mutate a local dict so we do not write back to DB: ensure `candidate_data` is a dict copy (`dict(cd)` / copy artifacts dict).

   b. If `artifacts` is a dict and `"base_resume" in artifacts`: **delete** `artifacts["base_resume"]` (strip blob dual-read on this operative path).

   c. `pin = (base_resume_artifact_id or "").strip()`; if pin:
      - `body = resolve_pinned_base_resume(astral_candidate_id, pin, debug=debug)` when `astral_candidate_id` is a non-empty str; else treat as miss.
      - If `body is not None`: set `candidate_data.setdefault("artifacts", {})["base_resume"] = body`.
      - If miss: leave absent (gap — `{$BASE_RESUME}` resolves empty via existing token path). Do **not** call `hydrate_operative_base_resume_for_response` (that is read-current / AST-1570).

   d. Use this raft for both the primary `do_task` and the follow-up `do_task` in the same turn (same `candidate_data` variable already shared).

8. Do **not** change `handle_slack_event` to invent a pin (traceability / pin persist is OOS). Leaving `base_resume_artifact_id` unset is valid; strip + dispatch UUID short-circuit still remove blob dual-reads. Callers that hold a pin (tests, future wire) pass the kwarg.

⚠️ **Decision:** Contact ownership check lives in `resolve_pinned_base_resume` (entity_id must match `astral_candidate_id`) because AST-1584’s helper gates type only. UI API reuses this same Contact helper so UI and Estelle share one path (parent: “same read-operative path”).

⚠️ **Decision:** Refusing `get_candidate_data:artifacts.base_resume` at Contact dispatch (error `pin_required`) is intentional — that dotted path is the blob dual-read this ticket removes on the Contact surface. Live/current without a pin remains read-current (AST-1570), not this epic.

## Stage 2: Candidate API — pin-in / body-out

**Done when:** Authenticated `GET /api/candidates/<candidate_id>/operative/base_resume?artifact_id=<uuid>` returns `{"base_resume": <body>}` on hit, 404 on miss/wrong owner/unknown candidate, 400 when `artifact_id` missing/blank; the handler calls `resolve_pinned_base_resume` only (no blob, no `get_current_artifact`, no `artifact_id` on save responses).

1. In `src/ui/api/api_candidate.py`, import `resolve_pinned_base_resume` from `src.core.contact`.

2. Add route **after** `get_candidate_detail` (keep blueprint style of neighboring routes):

```python
@candidate_bp.route("/<candidate_id>/operative/base_resume", methods=["GET"])
@require_auth
def get_operative_base_resume_api(candidate_id):
    """AST-1585: pin→body for pilot base_resume (patt.artifact.read-operative)."""
```

3. Handler steps (literal):
   - If `get_candidate(candidate_id)` is missing → `jsonify({"error": f"Candidate not found: {candidate_id}"}), 404`.
   - `artifact_id = (request.args.get("artifact_id") or "").strip()`; if empty → `jsonify({"error": "artifact_id required"}), 400`.
   - `body = resolve_pinned_base_resume(candidate_id, artifact_id, debug=ui_llm_debug())` (use the same debug helper this module already uses for candidate writes; if `ui_llm_debug` is not imported, pass `debug=False` — do not invent a new debug gate).
   - If `body is None` → `jsonify({"error": "base_resume not found for pin"}), 404`.
   - Else → `jsonify({"base_resume": body}), 200`.

4. Do **not** add routes under `api_jobs.py` for this pilot (candidate-owned catalog key; JAR will call the candidate operative URL with `selectedId`). Leave `api_jobs.py` untouched unless a compile/import issue forces a one-line re-export — prefer zero edits there.

5. Do **not** add `artifact_id` to PUT `/data` responses or `_sanitize_candidate`.

⚠️ **Decision:** Endpoint lives on `api_candidate.py` (not `api_jobs.py`) because the pilot catalog key is `candidate.artifacts.base_resume` and the pin addresses a candidate-owned artifacts row. JAR already has `selectedId` from `useCandidate`.

## Stage 3: JAR — render pinned source base_resume via operative API

**Done when:** Job Analysis Report Artifacts pane can show the pinned pilot `base_resume` body fetched through `GET …/operative/base_resume?artifact_id=…` when a pin string is available on the loaded job; when no pin is available, the pane shows a gap message and never reads `candidate_data.artifacts.base_resume` / candidate detail blob for that panel.

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, add:

```typescript
/** AST-1585: read pin from job_data when a prior writer left one (this ticket never writes it). */
export function jobBaseResumeArtifactId(jobData: unknown): string | null {
  if (!jobData || typeof jobData !== "object" || Array.isArray(jobData)) return null
  const raw = (jobData as Record<string, unknown>).base_resume_artifact_id
  if (typeof raw !== "string") return null
  const pin = raw.trim()
  return pin || null
}

export async function fetchOperativeBaseResume(
  candidateId: string,
  artifactId: string,
  apiFn: (path: string, init?: RequestInit) => Promise<Response>,
): Promise<{ ok: true; base_resume: unknown } | { ok: false; error: string }> {
  const url =
    `/api/candidates/${encodeURIComponent(candidateId)}/operative/base_resume` +
    `?artifact_id=${encodeURIComponent(artifactId)}`
  const resp = await apiFn(url)
  const data = await resp.json().catch(() => ({}))
  if (!resp.ok) {
    const err =
      data && typeof data === "object" && typeof (data as { error?: unknown }).error === "string"
        ? (data as { error: string }).error
        : `HTTP ${resp.status}`
    return { ok: false, error: err }
  }
  return { ok: true, base_resume: (data as { base_resume?: unknown }).base_resume }
}
```

   Pass `api` from the modal (do not import `../lib/api` inside the helper if that creates a cycle — keep `apiFn` injected as above).

2. In `JobAnalysisReportModal.tsx`:
   - Import `jobBaseResumeArtifactId`, `fetchOperativeBaseResume` from `../lib/recommendedJobReport`.
   - Add state: `sourceBaseResume: unknown | null`, `sourceBaseResumeError: string | null`, `sourceBaseResumeLoading: boolean`.
   - When `job` + `selectedId` + Artifacts top-tab are active, resolve `pin = jobBaseResumeArtifactId(job.job_data)`:
     - If no pin: set `sourceBaseResume` null, clear error, do not fetch candidate detail for base_resume.
     - If pin: set loading, call `fetchOperativeBaseResume(selectedId, pin, api)`; on ok store `base_resume`; on fail store error string; never fall back to `candidates` context blob / `/api/candidates/:id` hydrate for this panel.
   - In `renderArtifactsPane`, above the existing generate/section chrome (or immediately inside the pane when `hasArtifactContent` / idle), render a read-only block:
     - Title text: `Source base resume` (plain heading/class consistent with `recommended-report-*` — no new design system).
     - No pin: `<p className="recommended-report-empty">No pinned base resume for this build.</p>`
     - Loading: brief loading line.
     - Error: `<p className="entity-error">…</p>` with the error string.
     - Hit: render `JSON.stringify(sourceBaseResume, null, 2)` inside a `<pre className="recommended-report-empty">` (or existing monospace class if one already wraps JSON in this modal). Read-only — no `ArtifactEditor`, no Save.

3. Do **not** write `base_resume_artifact_id` onto the job from this modal or any API in this ticket.

4. Do **not** change job_resume / cover_letter / proposed_answers editors or blob hydrate for those keys.

⚠️ **Decision:** Pin location for JAR is optional read of `job.job_data.base_resume_artifact_id` (string). This ticket never persists it — traceability owns seed-id arrays later. Until a writer exists, UAT sees the gap message; operative fetch is verified with a pin present on a fixture job or by temporarily setting that field out-of-band. Rejected alternatives: inventing job PUT of the pin (OOS); using read-current hydrate as a stand-in (violates “not live current”); reading candidate blob `artifacts.base_resume` for this panel (dual-read ban).

## Estimate

Confirm Chuckles estimate: 5 — agree

Cross-layer Contact + candidate API + JAR panel on a known helper; no schema; pin persist explicitly excluded. Five points matches multi-surface glue without new pattern invention.
