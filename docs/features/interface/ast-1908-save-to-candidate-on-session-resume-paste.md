# AST-1908 — Save to Candidate on Session Resume Paste

- **Parent:** [AST-1899 — Add Save to candidate button](https://linear.app/astral/issue/AST-1899)
- **Ticket:** [AST-1908](https://linear.app/astral/issue/AST-1908)
- **Publish ref:** `origin/sub/AST-1899/AST-1908-save-to-candidate-session-resume-paste`

The Session Resume Paste admin page parses a pasted resume into `{ resume_structure, base_resume }`, but the result never leaves the browser. This ticket adds a **Save to Candidate** button that PUTs the last parse to the existing `PUT /api/candidates/<selectedId>/data` route as the selected candidate's current `base_resume` artifact, plus the parse's section layout (sections only — accent kept). The route already normalizes sections, ingests/filters `base_resume`, and does the operative write (`save_candidate_data` → retire prior `current=1`, insert new row; identical body is a no-op). This ticket changes one page file only.

## Scope gate

This ticket's `## Scope` names exactly one file: `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` — new async save handler, `saving` state, a fourth `.btn secondary` button after Open HTML, `saving` added to the three existing buttons' disabled props, and the intro paragraph text. Every row below is that file; every change below is one of those kinds. No gap.

## Verified assumptions (read on `origin/ftr/AST-1899-add-save-to-candidate-button` @ `777c04a81`)

1. `run_session_resume_parse` (`src/core/candidate.py`) returns `resume_structure` from `split_craft_resume_base_payload` → `normalize_resume_structure`, so `resume_structure.sections` is a non-empty **dict** keyed by section id.
2. `update_candidate_data` (`src/ui/api/api_candidate.py`, `PUT /<candidate_id>/data`) replaces sections only when `isinstance(rs_in.get("sections"), dict)` and keeps the resolved `accent_color` when the body has none — matches item 1, so Functional scope 3 holds with no backend change.
3. Same route runs `ingest_legacy_label_content_base_resume` + `filter_base_resume_to_structure` on `base_resume`, then `save_candidate_data(candidate_id, TASK_CONFIG["craft_resume_base"]["artifact_key"], pilot_body)` — the operative write per `patt.artifact.write-operative`.
4. Error responses are `{"error": str}` with 400 (both validation and the catch-all `except`).
5. `ArtifactsBaseResumeContent.tsx` fetches `/api/candidates/<id>/data` and `/resume_structure` on mount — no `CandidateContext` cache to refresh after Save.
6. `api()` (`src/ui/frontend/src/lib/api.ts`) returns a raw `Response`; non-OK is handled by the caller (same as `handleOpenHtml`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | `saving` state; `handleSave`; Save to Candidate button; `saving` in the three existing buttons' `disabled`; intro copy | ui |

No other file. No `tests/` or `docs/test-bible/**` edits (Betty, `qa-child`).

## Stage 1: Save to Candidate button, handler, busy state, copy

**Done when:** With a candidate selected and a parse on the page, clicking **Save to Candidate** sends one `PUT /api/candidates/<selectedId>/data` with body `{"artifacts":{"resume_structure":{"sections":…},"base_resume":…}}`, shows **Saving…** while in flight with all four buttons disabled, then shows a success toast (or the server's `error` in a toast and the inline error line, with the parse still present). `npx tsc -b --noEmit` and `npm run lint` pass in `src/ui/frontend`.

All edits are in `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx`.

1. **State.** Directly after the line `const [opening, setOpening] = useState(false)`, add:

   ```tsx
   const [saving, setSaving] = useState(false)
   ```

2. **Handler.** Directly after the closing `}` of `async function handleOpenHtml() { … }` (before `return (`), add this function exactly:

   ```tsx
   async function handleSave() {
     if (!selectedId || !lastParse || saving || parsing || opening) return
     setSaving(true)
     setError(null)
     try {
       // Sections only — no accent_color — so the route replaces the layout and keeps the candidate's accent.
       // base_resume goes as parsed: the route's ingest/filter owns shaping (no client-side reshape).
       const r = await api(`/api/candidates/${selectedId}/data`, {
         method: "PUT",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({
           artifacts: {
             resume_structure: { sections: lastParse.resume_structure.sections },
             base_resume: lastParse.base_resume,
           },
         }),
       })
       if (!r.ok) {
         let msg = `HTTP ${r.status}`
         try {
           const data = await r.json()
           if (typeof data.error === "string" && data.error) msg = data.error
         } catch { /* non-JSON error body */ }
         setError(msg)
         setToast({ text: msg, variant: "error" })
         return
       }
       setToast({ text: "Saved parse as the candidate's base resume.", variant: "success" })
     } catch (e) {
       const msg = e instanceof Error ? e.message : "Save failed"
       setError(msg)
       setToast({ text: msg, variant: "error" })
     } finally {
       setSaving(false)
     }
   }
   ```

   ⚠️ **Decision:** `lastParse` is never cleared or modified by `handleSave` (success or failure) — AC 6 requires the parse to stay for retry, and the ticket says `lastParse` / `pasteText` local-storage behavior is unchanged.

   ⚠️ **Decision:** Error extraction is written inline, mirroring `handleOpenHtml`, rather than factoring a shared helper out of the existing handlers. Refactoring `handleParse` / `handleOpenHtml` is outside this ticket's Scope (`astral.standards.in-scope-only`).

   ⚠️ **Decision:** `handleParse` and `handleOpenHtml` early-return guards are **not** changed. The ticket's Scope describes `saving` disabling the buttons; the button `disabled` props (steps 3–5) are the gate. Only the new handler guards on all in-flight flags, matching how `handleOpenHtml` guards on `opening || parsing`.

   ⚠️ **Decision:** No confirm prompt (parent Functional scope 2 / Susan's answer on the parent).

3. **Parse button.** Change its `disabled` from `{!selectedId || !pasteText.trim() || parsing}` to:

   ```tsx
   disabled={!selectedId || !pasteText.trim() || parsing || saving}
   ```

4. **View Parsed JSON button.** Change its `disabled` from `{!lastParse || opening || parsing}` to:

   ```tsx
   disabled={!lastParse || opening || parsing || saving}
   ```

5. **Open HTML button.** Change its `disabled` from `{!lastParse || opening || parsing}` to:

   ```tsx
   disabled={!lastParse || opening || parsing || saving}
   ```

6. **Save to Candidate button.** Directly after the Open HTML `</button>` and before the row's closing `</div>`, add:

   ```tsx
   <button
     type="button"
     className="btn secondary"
     onClick={() => void handleSave()}
     disabled={!selectedId || !lastParse || parsing || opening || saving}
   >
     {saving ? "Saving…" : "Save to Candidate"}
   </button>
   ```

   ⚠️ **Decision:** No `title` tooltip on the new button. The ticket doesn't ask for one; don't add one.

7. **Intro copy.** Replace the two text lines inside the intro `<p>`:

   ```
   Paste a full resume, Parse to structure-keyed JSON, optionally View Parsed JSON, then Open HTML to Print → PDF.
   Uses the selected candidate's API key for Ruth's model; does not save to the database.
   ```

   with:

   ```
   Paste a full resume, Parse to structure-keyed JSON, optionally View Parsed JSON, then Open HTML to Print → PDF.
   Uses the selected candidate's API key for Ruth's model. Parse and Open HTML do not save; Save to Candidate writes
   the parse as the selected candidate's base resume and section layout.
   ```

   The `<p>` element, its `style`, and surrounding markup are unchanged.

8. **Compile and lint** (from `src/ui/frontend`):

   ```bash
   npx tsc -b --noEmit
   npm run lint
   ```

   Both must pass with no new errors in `AdminSessionResumePaste.tsx`.

9. **Self-check before commit** (from repo root):

   ```bash
   grep -n "does not save to the database" src/ui/frontend/src/pages/AdminSessionResumePaste.tsx   # expect no output
   grep -rn "session_resume/save" src/                                                              # expect no output
   git diff origin/dev --stat -- src/ui/api src/core src/data src/utils                             # expect empty
   ```

10. Commit `code(AST-1908): Save to Candidate on Session Resume Paste` with only `AdminSessionResumePaste.tsx` staged; push `HEAD:sub/AST-1899/AST-1908-save-to-candidate-session-resume-paste`.

## Canon alignment (plan-time)

- `patt.artifact.write-operative` — satisfied by reuse: the existing route calls `save_candidate_data` on `candidate.artifacts.base_resume` (retire+insert, identical no-op). No new write path.
- `patt.artifact.ui-consistency` §5 — body is `{ artifacts: { base_resume: … } }` via the existing candidate data API, no client `artifact_id`, no parallel key. The editor-component part doesn't apply (pattern Exception 3: session paste).
- `astral.standards.dry-and-focused-functions`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only` — id-only at plan time; build-child §8 checks them. The plan keeps the client free of section-id lists and experience field lists, and touches one file.

## Estimate

Confirm Chuckles estimate: 1 — agree


## Joan validate

```text
[plan-rubric]
**Ticket:** AST-1908
**Overall:** APPROVED
**Corpus:** bd68954dc854ca80fca1fc391821dff9ff288a7a
**Publish ref:** origin/sub/AST-1899/AST-1908-save-to-candidate-session-resume-paste @ d1d9a425231c686889a6dd04dc7b855d3723ec12

## Canon scores
patt.artifact.write-operative | A | | Stage 1 handler + Verified assumptions #3 — existing PUT → save_candidate_data; no parallel write path
patt.artifact.ui-consistency | A | | Stage 1 §2 body + Canon alignment — §5 save contract via candidate data API; Exception 3 (session paste)
astral.standards.dry-and-focused-functions | A | | Scope gate + ⚠️ inline error mirror vs refactor — reuses route/shaping; no client duplicate of ingest/filter
astral.layers.ui-config-driven-business-logic | A | | Handler sends parse as-is; sections-only structure; no React section/experience field lists
astral.standards.in-scope-only | A | | Files Changed + self-check §9 — single page file; explicit out-of-scope backend/tests

## Traceability
AC1→Stage1 §3–6 (+ Betty `test_AdminSessionResumePaste` per Boundaries); AC2→Stage1 §2; AC3→Stage1 §2 + Verified #3; AC4→Stage1 §2 (sections-only, no accent); AC5→Stage1 §2 (base_resume passthrough); AC6→Stage1 §2; AC7→Scope + self-check §9; AC8→Stage1 §7

## Findings
(none)

context_tokens≈14500
```

**Summary:** Plan matches parent Purpose, Functional/Technical scope, and child **## Scope** (one file). **Stage 1** maps all eight ACs; component/UAT coverage for AC1/3/5 stays on Betty/UAT as the ticket Boundaries state. Verified assumptions on `origin/ftr/AST-1899-add-save-to-candidate-button` support operative save, accent retention, and error JSON shape. **Canon Scope gap:** none material (`astral.ui.frontend-file-placement` / `astral.layers.import-direction` not required — modify-in-place only, no new files). **Discuss-only note (non-blocking):** `patt.artifact.ui-consistency` frontmatter still marks **draft** on `origin/dev` while the parent cites it as reuse authority; plan text aligns with Implementation §5 + Exception 3 regardless.
