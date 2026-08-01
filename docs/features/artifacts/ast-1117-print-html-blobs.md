# AST-1117 — UAT: Print Resume and Print Cover Letter open recommended page not HTML

**Linear:** [AST-1117](https://linear.app/astralcareermatch/issue/AST-1117/uat-print-resume-and-print-cover-letter-open-recommended-page-not-html)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved) (AC reference only)

**Publish ref:** `origin/sub/AST-1091/AST-1117-print-html-blobs`

Print Resume / Print Cover Letter open `/candidate/resume|<job_id>` and `/candidate/cover/<job_id>`. On Vite local UAT those paths are **not** proxied to Flask, so the React app loads and the `*` route navigates to `/jobs/recommended`. Proxy `/candidate` to Flask and harden the Flask SPA catch-all so those paths never serve `index.html`.

## UAT fitness

- **AC restored:** After a successful `finalize_job_resume` hop … `job_data.artifacts.job_resume` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`. — and — After a successful `finalize_cover_letter` hop … `job_data.artifacts.cover_letter` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`. — and — A full successful daisy-chain … UAT surfaces that show Job Resume / Cover Letter / suggested answers resolve content via those ids without a manual PUT of the response body.
- **Correct outcome:** Each Print action opens a tab whose document is the resume or cover HTML resolved through the pins (printable HTML, not the recommended jobs shell).
- **Sibling check:** AST-1099 pin write and AST-1100 builder pin resolve (`_resolve_resume_sections` / `_resolve_cover_letter` already call `resolve_job_artifact_agent_data_body`) stay intact — this ticket does not change pin slots or builder resolve logic unless a Stage 3 verification proves pin-only bodies still fail after routing is fixed. AST-1116 (Cover Letter field-defs) is a separate surface.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Hiding Print when pins-only; opening a blank tab; re-storing full HTML/JSON on `job_data`; SPA-navigating inside the modal instead of serving HTML; swallowing builder errors; inventing a parallel print pipeline that bypasses existing `/candidate/*` HTML routes.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/vite.config.ts` | Proxy `/candidate` → Flask `:5001` (same target as `/api`) | ui |
| `src/ui/server.py` | In SPA catch-all `serve_react`, do **not** serve `index.html` for paths under `candidate/` — return 404 JSON if the HTML blueprint did not handle the request | ui |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| Pin write / pin keys | AST-1099 |
| Cover Letter ArtifactEditor field-defs | AST-1116 |
| Builder pin→body resolve (already AST-1100) | leave unless Stage 3 proves otherwise |
| Session cover/resume paste | excluded |
| Unrelated JAR / recommended chrome | excluded |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: Vite — proxy `/candidate` to Flask

**Done when:** `vite.config.ts` proxies `/candidate` to `http://localhost:5001`; local Vite UAT `window.open('/candidate/resume/…')` / cover hits Flask `resume_html_bp` instead of the SPA; no product URL changes required in the modal.

1. In `src/ui/frontend/vite.config.ts`, extend `server.proxy` so both `/api` and `/candidate` forward to Flask:

```ts
    proxy: {
      '/api': 'http://localhost:5001',
      '/candidate': 'http://localhost:5001',
    },
```

2. Do **not** change Print `window.open` paths in `JobAnalysisReportModal.tsx` / `MaterialsPreviewModal.tsx` (keep `/candidate/resume|cover/<job_id>`).
3. Do **not** add React Router routes for those paths (serving HTML is Flask’s job).

⚠️ **Decision:** Fix the miss by proxying the existing AST-605 HTML routes rather than relocating them under `/api/…`. Keeps print/PDF URLs stable; Vite was the hole (`/api` only).

## Stage 2: Flask — never SPA-fallback `/candidate/*`

**Done when:** `serve_react` returns 404 JSON for any `path` that starts with `candidate/` (case-sensitive prefix match on the catch-all `path` argument) instead of `index.html`; blueprint routes under `resume_html_bp` continue to return `text/html` when matched; `python3 -m py_compile src/ui/server.py` passes.

1. In `src/ui/server.py` `serve_react(path)`:

```python
def serve_react(path):
    """Catch-all: React static assets. Never steal /candidate/* HTML routes."""
    # Blueprint should match first; if not, do not serve SPA (would redirect to /jobs/recommended).
    if path == "candidate" or path.startswith("candidate/"):
        return jsonify({"error": "Not found"}), 404
    if (_DIST / path).is_file():
        return send_from_directory(_DIST, path)
    return send_from_directory(_DIST, "index.html")
```

2. Import `jsonify` from `flask` if not already imported (today: `request`, `send_from_directory` only — add `jsonify`).
3. Do **not** move or rename `resume_html_bp` routes.
4. Do **not** remove `@require_auth` from those routes.

## Stage 3: Verify pin-only HTML (no code unless broken)

**Done when:** With a job that has only pin strings on `job_resume` / `cover_letter` (no legacy body dicts), Flask `GET /candidate/resume/<job_id>` and `GET /candidate/cover/<job_id>` return `text/html` bodies that include resolved hop content (resume sections / cover prose). If both succeed via existing AST-1100 builder resolve, **commit nothing in this stage**. If either fails with 404/`ValueError` for pin-only while pin id is valid, **stop** and comment on AST-1117 with the exact exception — do not invent a second resolve path without that evidence.

1. Manually or via existing component harness: call `build_resume` / `build_cover_letter` (or the HTTP routes) against a pin-only job fixture.
2. Confirm `_resolve_resume_sections` / `_resolve_cover_letter` pin branches already on this tip remain the content path.
3. Only if broken: stop with Linear comment (parent AC + builder error); do not silently broaden scope.

## Self-Assessment

**Scope — Single-Component:** Vite proxy + Flask SPA catch-all guard for `/candidate/*` HTML print routes.

**Conf — high:** Symptom matches React `*` → `/jobs/recommended`; Vite proxy today is `/api` only; Flask already has `resume_html_bp` + AST-1100 pin resolve in builder.

**Risk — Medium:** Proxy misconfig could still 404 print tabs locally; overly broad catch-all exclusion could hide a real missing-route bug as JSON 404 (preferable to wrong recommended shell).

## Code rules check

| Rule | Notes |
|------|-------|
| `astral.layers.ui-config-driven-business-logic` | No new business rules in FE; routing only |
| `astral.layers.import-direction` | UI stays on existing core builders |
| `astral.standards.in-scope-only` | Print HTML delivery path only |
| `astral.batch.entity-agent-responses-latest-only` | Pins remain ids; bodies still from agent_data via builder |
| `astral.patterns.coat-check-never-store-empty` | No new job_data writes |
