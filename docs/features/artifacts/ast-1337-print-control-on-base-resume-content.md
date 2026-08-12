# AST-1337 — Print control on Base Resume Content

**Linear:** [AST-1337](https://linear.app/astralcareermatch/issue/AST-1337)
**Parent:** [AST-1314](https://linear.app/astralcareermatch/issue/AST-1314) — Add a Print button to Base Resume Content
**Publish ref:** `sub/AST-1314/AST-1337-print-control-on-base-resume-content`

Wire a **Print** control on Artifacts → Base Resume Content for the selected candidate. On success, open print-ready HTML in a new tab using the Session Resume Paste Open HTML flow (validate response, then open tab; no blank tab on failure). Source is the candidate’s **saved** base resume via existing `GET /candidate/resume/base?candidate_id=` + `build_base_resume` — not Admin session paste, not job Print routes, and not the unsaved editor buffer.

## UAT fitness

- **AC restored:** From parent AST-1314 / this ticket’s Acceptance criteria: (1) With a selected candidate that has saved printable base resume content, Susan can activate Print and get a new tab of print-ready HTML for that candidate’s base resume (structure order, section titles/formats, accent as already emitted by the base-resume builder). (2) She can use browser Print → PDF from that tab without a job id or leaving Artifacts for Session Resume Paste. (3) With no candidate selected, or when base resume content is missing/unusable, Print is unavailable or fails with a clear on-page error — and no blank HTML tab opens. (4) A failed HTML response never opens a success-looking blank/broken tab. (5) Job Print Resume / Print Cover Letter and Session Resume Paste behavior are unchanged.
- **Correct outcome:** From Base Resume Content, Print yields a usable print-ready HTML tab for the **selected candidate’s saved** base resume (same emit path as `/candidate/resume/base`), then browser Print → PDF works — not merely “no error toast.”
- **Sibling check:** This epic has a single child (AST-1337). Adjacent Highlights work (AST-1326) is out of scope and not required for Print. Verify by not editing Session Resume Paste, Recommended Job Report Print Resume/Cover, `api_resume_html.py` job/cover routes, or session admin HTML POST.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** `window.open("/candidate/resume/base?candidate_id=…")` like job Print — that can open a tab before the body is known (JSON 404 / empty / SPA miss looks like a broken success tab). Parent and ticket require Session-style **validate-then-open** (check `ok` + non-empty HTML, then blob URL tab). Also rejected: calling Admin `POST /api/admin/session_resume/html` or reading the in-editor dirty buffer — wrong source and out of boundaries.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Add Print (`btn secondary`): auth-fetch `GET /candidate/resume/base?candidate_id=…`, validate, open blob tab; on-page error + toast; disable when no candidate / in-flight | ui |

**Do not touch:** `AdminSessionResumePaste.tsx`, `AdminSessionCoverLetter.tsx`, `JobAnalysisReportModal.tsx`, `RecommendedJobReportHeader.tsx`, `api_resume_html.py`, `api_admin.py` session HTML, `builder.py`, `ArtifactEditor.tsx` (shared Generate/Save chrome — Print stays page-local), `routes.tsx`, vite proxy (already proxies `/candidate`), `tests/**`, `docs/test-bible/**`, canon pattern files.

## Stage 1: Print control + validate-then-open tab

**Done when:** On Artifacts → Base Resume Content with a candidate selected that has saved `artifacts.base_resume`, clicking **Print** opens a new tab of print-ready HTML (structure order / titles / formats / accent from the existing base builder). No candidate → Print disabled. Missing/unusable base content or non-OK/empty HTML → clear on-page error (and toast) and **no** new tab. Session Resume Paste and job Print Resume / Print Cover Letter behave as before (untouched files).

1. In `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`, keep existing accent / structure / `ArtifactEditor` wiring. Add local state:

   ```ts
   const [printing, setPrinting] = useState(false)
   const [printError, setPrintError] = useState<string | null>(null)
   ```

   Reuse the page’s existing `toast` / `setToast` / `clearToast` — do not add a second Toast.

2. Add `async function handlePrint()` (mirror `AdminSessionResumePaste.handleOpenHtml`, candidate-bound GET instead of admin POST):

   - If `!selectedId` or `printing`, return immediately.
   - `setPrinting(true)`; `setPrintError(null)`.
   - `const r = await api(\`/candidate/resume/base?candidate_id=${encodeURIComponent(selectedId)}\`)` — use shared `api` so Bearer auth is attached (`astral.idioms.require-auth-on-protected-endpoints`). Path is **not** under `/api/`; Vite already proxies `/candidate` (AST-1117).
   - If `!r.ok`: parse JSON `error` string when present (same try/catch pattern as Session Resume Paste), else `HTTP ${r.status}`; `setPrintError(msg)`; error toast; **return without** `window.open`.
   - `const html = await r.text()`; if `!html.trim()`: set error `"HTML response was empty"`, toast, **return without** opening a tab.
   - On success only:

     ```ts
     const blobUrl = URL.createObjectURL(
       new Blob([html], { type: "text/html;charset=utf-8" }),
     )
     const win = window.open(blobUrl, "_blank", "noopener,noreferrer")
     if (!win) {
       setToast({
         text: "Popup blocked — allow popups to open the HTML tab.",
         variant: "error",
       })
     }
     window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000)
     ```

   - `catch`: set on-page error + error toast from `e.message` (fallback `"Print failed"`).
   - `finally`: `setPrinting(false)`.

   ⚠️ **Decision:** Validate-then-blob via `api()` + `GET /candidate/resume/base`, not `window.open` of the HTML URL. Matches Session Open HTML and parent AC 3–4. Reuses existing `@require_auth` route + `build_base_resume` — no new endpoint, no admin session HTML, no job id.

   ⚠️ **Decision:** Do **not** preflight by reading ArtifactEditor tab state or unsaved buffer. Print always hits saved candidate content on the server (parent boundary: Save first, then Print). Enable Print whenever `selectedId` is set; missing content surfaces as 404/`Candidate missing artifacts.base_resume` (or empty HTML) with on-page error and no tab.

   ⚠️ **Decision:** Keep Print on this page only — do **not** add a header slot to `ArtifactEditor` (would touch every ArtifactEditor consumer). Place a small action row **above** `<ArtifactEditor … />` (after the accent bar when present).

3. Render the Print control:

   ```tsx
   <div style={{ display: "flex", gap: 8, padding: "8px 20px 0", alignItems: "center" }}>
     <button
       type="button"
       className="btn secondary"
       onClick={() => void handlePrint()}
       disabled={!selectedId || printing}
     >
       {printing ? "Opening…" : "Print"}
     </button>
   </div>
   {printError && (
     <p style={{ margin: "8px 20px 0", color: "var(--danger, #c44)", fontSize: 13 }}>
       {printError}
     </p>
   )}
   ```

   - Label: **Print** (not “Open HTML” — this is Base Resume Content, not Session Paste).
   - Class: `btn secondary` per `pattern.ui.shared-button-roles` and ticket notes (neutral alternate; not `primary`).
   - Disabled when `!selectedId || printing`.
   - In-flight label: **Opening…** (same operator cue as Session).

4. Do **not** edit `api_resume_html.py` / `build_base_resume` unless a literal compile/runtime break proves the route missing — it already exists with `@require_auth`, requires `candidate_id`, returns HTML or JSON 404. If the route is absent or signature differs from this plan, **stop** and comment on parent AST-1314 with the 🛑 Stage blocked format — do not invent a third emit path.

5. From `src/ui/frontend`, run `npm run build` (or at least `tsc -b`) and `npm run lint`. Fix only type/lint breaks caused by this file’s changes.

6. Smoke (manual / build-child): selected candidate with saved base resume → Print → HTML tab; no candidate → button disabled; candidate without base resume → error, no tab; confirm Session Paste and job Print files were not modified (`git diff --name-only` against stage start).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1337
**Overall:** APPROVED
**Publish ref:** `a4e72815be96abb568a17cc6efd7c0f35c273ee0` (`origin/sub/AST-1314/AST-1337-print-control-on-base-resume-content`)

## Traceability
AC1–5 → Stage 1 (validate-then-blob Print on saved base resume via `GET /candidate/resume/base`; AC5 via explicit do-not-touch boundary).

## Findings

### acceptable — deliberate Session mirror (DRY)
**Location:** Stage 1 `handlePrint`  
**Finding:** `handlePrint` closely mirrors `AdminSessionResumePaste.handleOpenHtml` (~40 lines).  
**Recommendation:** Acceptable for this ticket — parent requires Session-style validate-then-open; plan keeps scope to one page file and names the mirror explicitly. Optional future extract to `lib/` only if a third call site appears.

context_tokens≈38000
```

## Review (build)

**Built:** `origin/sub/AST-1314/AST-1337-print-control-on-base-resume-content` @ `c4f30b5152bd8f9ff882fb8cc99c41e1c0de9bae`

Stage 1: Print (`btn secondary`) on Base Resume Content — `api()` GET `/candidate/resume/base?candidate_id=…`, validate-then-blob tab; on-page error + toast; disabled without candidate. Tests deferred to Betty.

## Radia review

# Radia review — AST-1337

**Status gate:** Tests Passed (spawn prompt; not re-fetched).  
**Baseline:** `origin/dev`  
**Publish ref:** `origin/sub/AST-1314/AST-1337-print-control-on-base-resume-content` @ `63ba62d5be6b3bc15140a2cfe881d9d78be469aa`  
**Diff:** 4 files, +365 lines — `ArtifactsBaseResumeContent.tsx` (+63), Betty tests (+148), test-bible (+23), issue doc (+131)

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1337
**Publish ref:** `63ba62d5be6b3bc15140a2cfe881d9d78be469aa` (`origin/sub/AST-1314/AST-1337-print-control-on-base-resume-content`)
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent/LLM paths in diff |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` / dispatch changes |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grading/vector paths |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch/dispatcher changes |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/release helpers |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no agent-responses table |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config/schema changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env wiring |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts dir |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run-next chain |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single `docs/features/artifacts/ast-1337-…md` |
| `astral.git.betty-no-src-or-features` | scoped | conforms | test/bible edits are Betty lane; engineer `src/` is one planned page |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer product diff is `src/ui/frontend/.../ArtifactsBaseResumeContent.tsx` only |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no core/external layer changes |
| `astral.layers.import-direction` | scoped | conforms | UI page; top-level imports only; no `data`/`external` |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no `scripts/` changes |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no hardcoded candidate/job state strings added |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check persistence |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult/render paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | `handlePrint` uses shared `api()` → Bearer on `GET /candidate/resume/base` (`@require_auth` route) |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no boot seed |
| `astral.seed.define-approved` | scoped | not-applicable | no define/seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage join |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no `src/data/` |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/migrations |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no backend `debug=` surfaces |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | deliberate Session mirror; Joan plan accepted |
| `astral.standards.in-scope-only` | scoped | conforms | product scope = one page; boundaries respected |
| `astral.standards.logging-via-utils` | scoped | conforms | no `print()` / ad-hoc loggers in diff |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | runtime symbols are domain names; ticket id only in test titles |
| `astral.standards.no-cross-contamination` | scoped | conforms | Session Paste, job Print, `api_resume_html.py`, `ArtifactEditor` untouched |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | no new hardcoded enum sets |
| `astral.standards.public-then-helpers` | scoped | conforms | `handlePrint` follows existing page-local handler pattern |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no `src/utils/` changes |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job state |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run/daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | conforms | change in `src/ui/frontend/src/pages/` |
| `astral.ui.naming-conventions` | scoped | conforms | existing `ArtifactsBaseResumeContent.tsx` naming preserved |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server/worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | tip `63ba62d5` is `merge-tests(AST-1337)` |
| `orch.git.commit-vocabulary` | universal | conforms | pipeline commit shapes on branch |
| `orch.git.flow-direction-inviolable` | universal | conforms | `sub/AST-1314/…` vs `origin/dev` |
| `orch.git.ftr-sub-topology` | universal | conforms | child under parent `AST-1314` |
| `orch.git.merge-on-checkout` | universal | conforms | no rebase/cherry-pick in diff |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | three-dot diff is normal merge lineage |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/…`, not agent branch |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in `astral-AST-1314` worktree |
| `orch.git.three-permanent-branches` | universal | conforms | diff vs `origin/dev` only |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy invention |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 implemented per plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Artifacts child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | component tests + bible by Betty |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | implementer remains assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path commits in diff |

**Corpus count:** 64 active rows scored from `canon/statutes/README.md` § Harvested corpus + universal block (registry states 65).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.shared-button-roles` | conforms | `className="btn secondary"`; in-flight via label `Opening…` (matches Session Open HTML — secondary, not `in-flight` gold) |

Plan also cites `astral.idioms.require-auth-on-protected-endpoints` — scored under statutes, not patterns.

## Plan adherence

Stage 1 is faithful to the approved plan and parent AC1–5:

- **Validate-then-blob:** `handlePrint` mirrors `AdminSessionResumePaste.handleOpenHtml` — `api()` fetch, `!r.ok` → JSON error parse, empty-body guard, blob URL + `window.open`, popup-blocked toast, 60s revoke. No direct `window.open` of the HTML URL.
- **Source:** `GET /candidate/resume/base?candidate_id=…` (saved server content), not editor buffer or admin session POST.
- **Placement:** action row above `ArtifactEditor`, after accent bar; no `ArtifactEditor` header slot.
- **Boundaries:** Session Paste, job Print routes, `api_resume_html.py`, `builder.py` untouched in product diff.
- **Estimate 2:** footprint matches — one UI page + Betty tests/bible; no new API or builder work.

Betty landed `test_ArtifactsBaseResumeContent.test.tsx` AST-1337 cases and `docs/test-bible/frontend/pages.md` § AST-1337 — aligned with manifest intent (disabled w/o candidate, success blob, 404/empty never open tab).

**Joan straggler:** no Excluded-statute list in plan-rubric attachment → no straggler callout.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

**Stale `printError` on candidate switch**  
`ArtifactsBaseResumeContent.tsx` — `printError` is not cleared when `selectedId` changes (unlike structure state reset in the `selectedId` effect). If Print fails for candidate A, switching to B may show A’s error until the next Print attempt. Low severity; Session Paste has no analogous switch. Optional `setPrintError(null)` in the `selectedId` effect.

**Popup-blocked path**  
On `!win`, only toast fires — no `printError` line (same as Session Paste). Acceptable; operators still get feedback.

## What’s solid

- Session mirror is intentional and correctly wired to the existing `@require_auth` `/candidate/resume/base` route.
- Error paths never call `window.open` — matches AC3–4 and Betty’s negative tests.
- `btn secondary` + disabled when `!selectedId || printing` matches plan and `pattern.ui.shared-button-roles`.
- Cross-ticket boundaries clean — no scope smuggling from Session/job Print siblings.

## Recommended actions (downstream — not Radia)

1. **Susan UAT:** candidate with saved base resume → Print → browser Print/PDF; no candidate → disabled; missing base → on-page error + toast, no tab; confirm Session Paste and job Print unchanged.
2. **Optional resolve-child:** clear `printError` on `selectedId` change if UAT notices stale errors (advisory only).

## Frame diff

| Frame | At review |
|-------|-----------|
| Issue doc last engineer note | `Review (build)` @ `c4f30b51` — tests deferred |
| Tip under review | `63ba62d5` — includes Betty `merge-tests` + test/bible |
| New since build note | `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` (+148), `docs/test-bible/frontend/pages.md` § AST-1337 (+23) |
| Product delta vs plan | `ArtifactsBaseResumeContent.tsx` matches Stage 1 spec |

## Notes

- §5f (debug contract) and §5g (external cleanliness) not triggered — UI-only diff.
- No `[qa-handoff]` / engineer test disputes visible on issue doc.
- C7 complete — Chuckles may append, push `docs(AST-1337): Radia review — clean`, post upshot, move to **Review Posted** → **User Testing** (PROCEED).

context_tokens≈52000

---

```
[code-rubric] PROCEED (Commit: 63ba62d5) Print control clean
```
