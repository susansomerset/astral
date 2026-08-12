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
