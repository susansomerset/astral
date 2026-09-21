<!-- linear-archive: AST-1117 archived 2026-08-07 -->

## Linear archive (AST-1117)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1117/uat-print-resume-and-print-cover-letter-open-recommended-page-not-html  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data  
**Blocked by / blocks / related:** parent: AST-1091

### Description

## What this implements

Print Resume / Print Cover Letter open tabs that render Flask HTML from `/candidate/resume|<job_id>` and `/candidate/cover/<job_id>`, resolved through pinned artifact bodies — not the recommended-jobs SPA shell.

## In scope

- [X] `astral.layers.ui-config-driven-business-logic` — routing/proxy only; no new FE business rules
- [X] `astral.layers.import-direction` — HTML still from core builders via existing blueprint
- [X] `astral.standards.in-scope-only` — Print HTML delivery path only
- [X] `astral.batch.entity-agent-responses-latest-only` — pins stay ids; bodies via builder resolve
- [X] `astral.patterns.coat-check-never-store-empty` — no new job_data writes
- [X] Vite proxy `/candidate` → Flask (local UAT hole)
- [X] Flask SPA catch-all must not serve `index.html` for `candidate/*`

## Considered but excluded

- [X] Pin write — AST-1099
- [X] Cover Letter ArtifactEditor field-defs — AST-1116
- [X] Relocating HTML under `/api/…` / changing Print URLs — wrong fix (keep AST-605 paths)
- [X] Hiding Print when pins-only / blank tab / SPA navigate / swallow builder errors — wrong fixes
- [X] Session cover/resume paste — excluded
- [X] `tests/` / `docs/test-bible/**` — Betty
- [X] `astral.standards.database-header-inventory` — no `src/data/**`
- [X] `astral.layers.scripts-exempt-from-layer-rules` — no `scripts/**`

## Acceptance criteria

- [X] Print Resume opens a tab with resume HTML (pin-resolved body), not `/jobs/recommended`.
- [X] Print Cover Letter opens a tab with cover HTML (pin-resolved body), not `/jobs/recommended`.
- [X] Pin-on-job + builder pin resolve contracts still hold; no full HTML/JSON forced onto `job_data` as the pin replacement.

## Boundaries

Does not change pin write, Cover Letter field-defs (AST-1116), session paste, or unrelated recommended chrome.

## Notes for planning

Hypothesis: Vite proxies only `/api`; `/candidate/*` loads SPA → `*` redirects to recommended. Flask `resume_html_bp` + AST-1100 builder pin resolve already exist.

## Git branch (authoritative)

Per parent **## Git**: `sub/AST-1091/AST-1117-print-html-blobs`.

## What failed

Both **Print Resume** and **Print Cover Letter** open new browser tabs that land on the recommended page, not printable HTML blobs for the job resume / cover letter.

## Expected

Print Resume / Print Cover Letter open tabs that render the HTML document built from the pinned artifact bodies (`job_data.artifacts.job_resume` / `cover_letter` → `agent_data`), suitable for print/PDF.

## Repro

1. Open a recommended job whose daisy-chain left resume and cover pins set.
2. Click **Print Resume** — new tab shows the recommended page, not resume HTML.
3. Click **Print Cover Letter** — same: recommended page, not cover HTML.

## Parent AC (quoted inline)

> After a successful `finalize_job_resume` hop (chain may continue), `job_data.artifacts.job_resume` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.

> After a successful `finalize_cover_letter` hop (chain may continue), `job_data.artifacts.cover_letter` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.

> A full successful daisy-chain that ran those three hops leaves all three pointer keys set; UAT surfaces that show Job Resume / Cover Letter / suggested answers resolve content via those ids without a manual PUT of the response body.

## Diagnosis

* **Hypothesis:** Print buttons become visible from non-empty pin strings, but `/candidate/resume/<job_id>` and `/candidate/cover/<job_id>` (or the builders behind them) do not return the printable HTML blob for pin-only artifacts — the new tab falls through to the app/recommended shell instead of an HTML document.
* **Correct outcome:** Each Print action opens a tab whose document is the resume or cover HTML resolved through the pins.
* **Wrong fix to avoid:** Hide Print buttons when pins-only; open a blank tab; re-store full HTML/JSON on `job_data`; SPA navigate inside the modal instead of serving HTML; swallow builder errors.
* **Related siblings / contracts:** AST-1100 (pin resolve for surfaces / builders); AST-1099 (pin write). Cover Letter preview field-defs bug is separate.

## Original brief

UAT bug filed by Chuckles from fix-uat.

### Comments

#### radia — 2026-08-01T00:59:35.481Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1117
**Publish ref:** `origin/sub/AST-1091/AST-1117-print-html-blobs` @ `56841f9d` (code `c2788bfd`; merge-tests `dcab534f`)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1117)` → `7da983d3` |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | Publish forward on origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1091/AST-1117-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in ticket commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1117 history |
| orch.git.no-dev-agent-branches | universal | conforms | Child sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in astral-AST-1091 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis locked; no open product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 implemented; Stage 3 no-code verify |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty test + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Implementer path was Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Assignee left with Katherine |
| orch.roles.pre-commit-path-bans | universal | conforms | Doc-only Radia commit; engineer off bans |
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/**` / config in ticket change set |
| astral.agent.do-task-delegation | scoped | not-applicable | no `src/core/**` |
| astral.agent.grade-vector-validation | scoped | not-applicable | no `src/core/**` |
| astral.batch.batch-id-first | scoped | not-applicable | no core/data paths |
| astral.batch.batch-id-format | scoped | not-applicable | no core/data paths |
| astral.batch.claim-process-release | scoped | not-applicable | no core/data paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no core/data paths (pins untouched) |
| astral.config.config-source-of-truth | scoped | conforms | No new config dialects; routing only |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | no core/data/config scoring paths |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no `artifacts/**` / spikes paths |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/` |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no core/config chain paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatcher/config seed paths |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1117-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty did not edit src/features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code commit left tests/bible to Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no core/external paths |
| astral.layers.import-direction | scoped | conforms | UI stays on existing HTML blueprint / builders |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Routing only; no new FE business rules |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | no `src/core/**` |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no `src/core/**` |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `resume_html_bp` `@require_auth` unchanged; no new open routes |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | paths do not match seed admin/bootstrap |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no dispatcher/config/admin seed paths |
| astral.seed.boot-only-not-hot-path | scoped | conforms | No new boot seed path |
| astral.seed.define-approved | scoped | conforms | No product seed invented |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no dispatcher/data/config seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no dispatcher/config/data seed paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new data-layer calls |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Minimal proxy + catch-all guard |
| astral.standards.in-scope-only | scoped | conforms | Print HTML delivery path only |
| astral.standards.logging-via-utils | scoped | conforms | No new logging surface |
| astral.standards.names-not-ticket-ids | scoped | conforms | Ticket ids only in comments (carve-out) |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in ui (+ Betty tests) |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new domain sets |
| astral.standards.public-then-helpers | scoped | conforms | Catch-all edit only |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no `src/utils/**` |
| astral.state.core-decides-transitions | scoped | not-applicable | no core/data paths |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no core/data/config state paths |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no `src/core/**` |
| astral.ui.frontend-file-placement | scoped | conforms | Vite config stays under `frontend/` |
| astral.ui.naming-conventions | scoped | conforms | Existing `/candidate/*` paths unchanged |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker changes |

## Pattern conformance

| cited | verdict |
|-------|---------|
| astral.layers.ui-config-driven-business-logic | conforms |
| astral.layers.import-direction | conforms |
| astral.standards.in-scope-only | conforms |
| astral.batch.entity-agent-responses-latest-only | conforms (pins untouched; N/A on core paths but cited intent holds) |
| astral.patterns.coat-check-never-store-empty | conforms (no new writes) |

## Plan adherence

FIX-UAT Stages 1–2 match: Vite `/candidate` proxy + Flask SPA catch-all 404 for `candidate/*`. Stage 3 no builder code (AST-1100 pin resolve already on tip). Self-Assessment Single-Component / high / Medium fits. Wrong fixes rejected (hide Print, relocate under `/api`, SPA-navigate).

## Findings

None.

## Notes

- FIX-UAT mode. `no plan-rubric verdict attached` — not a block (C4).
- Change set: AST-1117 commits on publish tip. Active statutes = 65.
- Docs append @ `56841f9d`.
- Session note: `linear-radia` MCP socket missing; comment posted via Radia Linear API key (viewer = Radia).

context_tokens≈36000

— Radia

#### betty — 2026-08-01T00:55:35.448Z
## QA test manifest

`origin/sub/AST-1091/AST-1117-print-html-blobs` @ `dcab534f` (`merge-tests(AST-1117): origin/tests 7da983d3239e15cd30ae1ef176fdf8beabfcdfef`)

### 1. Existing coverage (bible-backed)

1. `tests/component/ui/api/test_api_resume_html.py::TestResumeHtmlRoutes` — job resume HTML route
2. `tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute` — cover HTML route
3. JAR Print `window.open('/candidate/…')` + pin visibility — `docs/test-bible/frontend/lib.md` (AST-605 / AST-1100); no re-author this pass

### 2. Broken / obsolete

none

### 3. Gaps (new this pass)

1. `tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard` — catch-all 404 JSON for `candidate/*`, SPA fallback still for other paths
2. `tests/component/ui/test_server.py::TestAst1117ViteCandidateProxy` — `vite.config.ts` proxies `/candidate` → Flask `:5001`

**Bible shasum** (on publish tip):
- `docs/test-bible/ui/server.md` `a9b3e6dc7e03178126e14cd10d830b99f723ea25`

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard \
  tests/component/ui/test_server.py::TestAst1117ViteCandidateProxy \
  tests/component/ui/api/test_api_resume_html.py::TestResumeHtmlRoutes \
  tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

#### katherine — 2026-08-01T00:51:04.428Z
Plan published on `origin/sub/AST-1091/AST-1117-print-html-blobs` @ `ecc5edf1`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1091/AST-1117-print-html-blobs/docs/features/artifacts/ast-1117-print-html-blobs.md

**Approach:** Vite proxies only `/api` today — Print `window.open('/candidate/…')` loads the SPA, and `*` redirects to `/jobs/recommended`. Proxy `/candidate` → Flask; harden Flask `serve_react` so `candidate/*` never gets `index.html`. Builder pin resolve (AST-1100) stays; Stage 3 verifies only.

**Self-assessment**
- **Scope — Single-Component:** Vite proxy + Flask SPA catch-all guard for `/candidate/*`.
- **Conf — high:** Symptom matches React catch-all; HTML blueprint + pin resolve already ship.
- **Risk — Medium:** Local proxy misconfig still 404s print; catch-all 404 is better than wrong recommended shell.

---

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

## Review

**Branch:** `sub/AST-1091/AST-1117-print-html-blobs`  
**Code:** `c2788bfd`  
**Publish tip reviewed:** `dcab534f` (`merge-tests(AST-1117)`)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1117  
**Overall:** CLEAN

### What’s solid
- Vite proxies `/candidate` to Flask `:5001` alongside `/api` — Print `window.open` URLs stay on existing HTML routes.
- Flask SPA catch-all returns 404 JSON for `candidate/*` instead of `index.html` (avoids `/jobs/recommended` shell).
- `resume_html_bp` + `@require_auth` left intact; Stage 3 no builder code (AST-1100 pin resolve already present).
- Engineer stayed off tests/bible; Betty one-SHA merge-tests.

### Issues
None fix-now / discuss.

### Recommended actions
- Engineer: resolve-child → User Testing after Linear Review Posted lands.

### Notes
- FIX-UAT child. `no plan-rubric verdict attached` at review time — not a block.
- **Blocker at handoff:** `linear-radia` MCP unavailable in this session — Linear comment + Review Posted not posted from this run; docs() pushed. Re-run §7 when Radia MCP is back.
- Active statutes = 65. Ticket-scoped change set used for applies_when.

context_tokens≈36000

— Radia

## Resolution

**Date:** 2026-08-01  
**Publish tip before resolve:** `56841f9d` (Radia `docs(AST-1117)` on merge-tests `dcab534f` / code `c2788bfd`)

- **fix-now:** none — Radia overall CLEAN.
- **discuss / advisory:** none.
