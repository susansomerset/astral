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

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1585
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1571/AST-1585-ui-contact-pilot-base-resume-operative-resolve` @ `0fcf6d4dc3483f065ad89cd257f9fbedd8a2f0d3`

## Traceability
AC2→S1 (Contact `resolve_pinned_base_resume` + dispatch UUID short-circuit; blob strip; `pin_required` on `artifacts.base_resume`) · AC3→S2+S3 (operative API pin-in/body-out; JAR fetch via `fetchOperativeBaseResume`; no candidate blob fallback on panel) · AC4→Explicit scope gate + Out-of-scope table (no database/candidate edits, no pin persist, no grade writers/new keys/read-current/coat-check/HTTP `artifact_id`)

## Findings

### discuss — Contact dispatch short-circuit debug parity
**Location:** Stage 1 step 5  
**Finding:** UUID / `pin_required` branches bypass the tracker handler; plan does not spell out that short-circuit rows must still emit the same Style D `debug_index`/`debug_detail` epilog the loop already uses for handler results.  
**Recommendation:** When implementing, append the row and run through the existing per-span debug block (or mirror `_contact_task_style_d`) so `debug=True` stays complete.

### acceptable — JAR pin source without in-epic writer
**Location:** Stage 3 Decision  
**Finding:** `job_data.base_resume_artifact_id` is read-only; no product writer until traceability — UAT needs fixture/out-of-band pin. Parent AC3 is “when a pin is supplied”; functional scope #3 matches.  
**Recommendation:** No plan change; Betty/UAT should seed a pin on a test job.

### acceptable — UI API routes through `contact.resolve_pinned_base_resume`
**Location:** Stage 2  
**Finding:** Handler lives in `api_candidate.py` but calls Contact wrapper (ownership gate + `get_operative_base_resume`) rather than importing candidate directly. Matches parent “same read-operative path” for UI and Estelle.  
**Recommendation:** Keep as planned.

context_tokens≈32000
```

## Review (build)

**Built @ `fca9711a`** — `origin/sub/AST-1571/AST-1585-ui-contact-pilot-base-resume-operative-resolve`

Stages 1–3 landed: Contact `resolve_pinned_base_resume` + Estelle raft strip + dispatch UUID/`pin_required` short-circuit; `GET /api/candidates/<id>/operative/base_resume?artifact_id=`; JAR Source base resume panel via `fetchOperativeBaseResume` (no blob fallback; pin read-only from `job_data.base_resume_artifact_id`).

## Radia review

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1585
**Publish ref:** origin/sub/AST-1571/AST-1585-ui-contact-pilot-base-resume-operative-resolve @ dc723224
**Overall:** CLEAN
```

## Statutes checked

Full active set (64 per `canon/statutes/README.md` § Harvested corpus). Diff layers: `core`, `data`, `ui`, `docs`; paths include `src/core/contact.py`, `src/ui/api/api_candidate.py`, `src/ui/frontend/**`, sibling `src/core/candidate.py` + `src/data/database.py`, `docs/**`, `tests/**`, `canon/directives/draft/**`.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No agent-confidence / config paths in AST-1585 product commits |
| astral.agent.do-task-delegation | scoped | conforms | Estelle `do_task` path unchanged; raft mutation is pre-task only |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector logic touched |
| astral.batch.batch-id-first | scoped | conforms | No batch-id write paths changed |
| astral.batch.batch-id-format | scoped | conforms | No batch-id formatting changed |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release paths changed |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No entity-agent-responses paths changed |
| astral.config.config-source-of-truth | scoped | conforms | Pilot identity delegated to `get_operative_base_resume` / `ARTIFACT_CONFIG` (sibling) |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring in diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No repo-root `artifacts/` dir changes |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No `debug/` spike paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No dispatcher paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run-next / chain paths |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/foundation/ast-1585-…md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch test-tree only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test-tree via Betty `test()` + `merge-tests()` — not engineer build commits |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Contact changes stay core; no external mixing |
| astral.layers.import-direction | scoped | conforms | `ui/api` → `core.contact`; `core.contact` → `core.candidate` + `data.database` (allowed) |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | JAR gap/fetch copy is panel-local per plan; no new state enums |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | Operative paths refuse blob dual-read; gap on miss |
| astral.idioms.render-verdict-orchestrates-consult | scoped | conforms | No consult/render orchestration changed |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `GET …/operative/base_resume` behind `@require_auth` |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON / bootstrap paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No dispatcher/catalog seed paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No boot/migration hot-path changes |
| astral.seed.define-approved | scoped | not-applicable | No define/seed approval paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data layer unchanged by 1585; Contact debug via `get_logger` when `debug=True` |
| astral.standards.database-header-inventory | scoped | conforms | Sibling `get_artifact` only; no schema/header drift in 1585 commits |
| astral.standards.debug-contract-gated | scoped | conforms | `resolve_pinned_base_resume` uses `debug_index`/`debug_detail`; dispatch short-circuits use `_dispatch_recorded_debug` + `truncate_debug_content` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shared `resolve_pinned_base_resume`; thin API + JAR helpers |
| astral.standards.in-scope-only | scoped | conforms | 1585 engineer commits: `contact.py`, `api_candidate.py`, JAR + `recommendedJobReport.tsx` only |
| astral.standards.logging-via-utils | scoped | conforms | No `print` / raw `logging`; uses `get_logger` |
| astral.standards.names-not-ticket-ids | scoped | conforms | Domain names (`resolve_pinned_base_resume`, `fetchOperativeBaseResume`, …) |
| astral.standards.no-cross-contamination | scoped | conforms | Ownership gate in Contact; wrong-owner → `None` |
| astral.standards.no-hardcoded-sets | scoped | conforms | No ad-hoc entity/type literals; pilot gate in sibling helper |
| astral.standards.public-then-helpers | scoped | conforms | `resolve_pinned_base_resume` public before dispatch/Estelle |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No `src/utils/**` changes in 1585 commits |
| astral.state.core-decides-transitions | scoped | conforms | No ad-hoc state writes |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job-state config paths |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No in-run chain changes |
| astral.ui.frontend-file-placement | scoped | conforms | Helpers in `lib/recommendedJobReport.tsx`; modal in `components/` |
| astral.ui.naming-conventions | scoped | conforms | Route/handler naming matches blueprint style |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No gunicorn/config UI paths |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1585): origin/tests a35223c5` present |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` on branch |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1571/AST-1585-…` topology |
| orch.git.ftr-sub-topology | universal | conforms | Child on `sub/<parent>/<child>` |
| orch.git.merge-on-checkout | universal | conforms | No rebase/cherry-pick signals |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Clean stacked history |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1571 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | Diff vs `origin/dev` only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-policy decisions smuggled in code |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | Foundation child within AST-1571 |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `tests/` + `docs/test-bible/` from Betty lane |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Katherine (engineer) |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-evasion patterns |

**Straggler (C4):** Joan `[plan-rubric] APPROVED` attached; no Excluded statute list — no straggler rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `patt.artifact.read-operative` (parent draft directive) | conforms | Contact + API + JAR wire pin→body; blob dual-read stripped; `pin_required` on dotted path; no coat-check / blob fallback |
| `patt.artifacts.traceability` (sibling draft) | conforms | Read-only `job_data.base_resume_artifact_id`; no product persist of seed ids |
| none cited in plan `Patterns to reuse` | — | Parent read-operative mandate satisfied across Contact/UI surfaces |

## Plan adherence

- **Stage 1 (Contact):** `resolve_pinned_base_resume` matches contract — ownership via `database.get_artifact` + `get_operative_base_resume`; `debug_index`/`debug_detail` when `debug=True`; UUID dispatch short-circuit + `pin_required` on `artifacts.base_resume`; `_dispatch_recorded_debug` refactors handler epilog for short-circuits too (addresses Joan discuss item); Estelle raft deep-copies, strips blob `base_resume`, injects pin body; `base_resume_artifact_id` kwarg added; `handle_slack_event` unchanged (no invented pin).
- **Stage 2 (API):** `GET /api/candidates/<id>/operative/base_resume?artifact_id=` with 400/404 semantics; calls `resolve_pinned_base_resume` with `ui_llm_debug()`; no `api_jobs.py` edits; no `artifact_id` on save responses.
- **Stage 3 (JAR):** `jobBaseResumeArtifactId` + `fetchOperativeBaseResume` in `recommendedJobReport.tsx`; modal Source base resume panel with gap/loading/error/JSON hit; no blob fallback; no pin write.
- **Estimate 5:** Footprint fits — three surfaces + Betty test-tree.
- **Cross-ticket:** AST-1584 helper on branch tip; 1585 does not edit `candidate.py` / `database.py` in engineer commits. No traceability persist, grade writers, or read-current hydrate substitution.
- **C6 lenses:** Layer imports clean; auth on protected endpoint; debug contract on touched `debug=` paths; no silent failure / inappropriate fallbacks on operative path.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Joan discuss resolved in build** — dispatch UUID / `pin_required` short-circuits now route through `_dispatch_recorded_debug` (same recorded epilog shape as handler path).
- **Branch stacking** — `origin/dev...publish-ref` includes full AST-1584 stack; normal for `blockedBy` sibling before ftr merge. 1585 engineer commits remain scope-clean.
- **Issue doc vs test-bible** — test-bible carries AST-1585 manifest (`contact.md`, `api_candidate.md`, `frontend/*`); issue doc stops at build stub — Chuckles may append qa pointer when writing back.
- **Double PK fetch** — `resolve_pinned_base_resume` calls `database.get_artifact` then `get_operative_base_resume` (which fetches again); matches plan literal contract, not a defect.
- **JAR `useEffect` deps** — `api` omitted from dependency array (stable import pattern elsewhere); optional eslint-hygiene if team cares.

## What's solid

- Single shared path: UI API and Estelle both use `contact.resolve_pinned_base_resume` — parent “same read-operative path” satisfied.
- Blob dual-read removal is explicit and tested: dispatch refuses `artifacts.base_resume`; Estelle raft strips blob before pin inject; JAR never hydrates candidate blob for Source panel.
- Betty coverage hits all three surfaces: `TestAst1585ContactPinnedBaseResume`, `TestAst1585OperativeBaseResumeApi`, JAR + `recommendedJobReport` helper tests.

## Frame diff

| Planned (AST-1585) | Landed |
|--------------------|--------|
| `src/core/contact.py` | ✓ (`bdd91ca8`) |
| `src/ui/api/api_candidate.py` | ✓ (`a75f0d48`) |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | ✓ (`fca9711a`) |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | ✓ (`fca9711a`) |
| `src/ui/api/api_jobs.py` untouched | ✓ |
| `candidate.py` / `database.py` untouched by 1585 engineer | ✓ (sibling on branch only) |
| Betty test-tree | ✓ (`a35223c5` + `dc723224 merge-tests`) |
| Issue doc qa manifest | (none) — test-bible holds manifest |

## Notes

- Joan plan-rubric verdict attached; no Excluded statutes.
- AST-1584 dependency on branch tip; prior Radia verdict PROCEED @ `cd309487`.
- Review diff: `git diff origin/dev...origin/sub/AST-1571/AST-1585-ui-contact-pilot-base-resume-operative-resolve` (21 files, +1648/−66).

context_tokens≈55000
```
