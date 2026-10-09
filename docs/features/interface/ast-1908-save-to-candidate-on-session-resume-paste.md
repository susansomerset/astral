<!-- linear-archive: AST-1908 archived 2026-10-08 -->

## Linear archive (AST-1908)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1908/save-to-candidate-on-session-resume-paste-add-save-to-candidate-button  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-1899 — Add Save to candidate button  
**Blocked by / blocks / related:** parent: AST-1899

### Description

## What this implements

Adds the **Save to Candidate** button to the Session Resume Paste page. It saves the last parse as the selected candidate's current base resume through the existing candidate data save, with busy/disabled states, toasts, and corrected intro copy. It does not touch the backend, the parse route, or the Base Resume Content editor.

## Citations

`patt.artifact.write-operative`, `patt.artifact.ui-consistency` (§5 save contract), `astral.standards.dry-and-focused-functions`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`.

## Scope

* `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx`: new async save handler. With `selectedId` and `lastParse` present, it PUTs `/api/candidates/<selectedId>/data` with body `{ artifacts: { resume_structure: { sections: lastParse.resume_structure.sections }, base_resume: lastParse.base_resume } }`: sections only, no `accent_color`, so the existing route replaces the candidate's sections and keeps the accent (Functional scope 3). `base_resume` (experience job array included) is sent exactly as parsed, with no client-side reshaping or filtering (Functional scope 4). The route's existing ingest/filter then keys content to the parse's enabled sections. On a non-OK response it reads the JSON `error` (falling back to `HTTP <status>`) into the inline error line and an error toast. On OK it shows a success toast. New `saving` state disables all three existing buttons plus Save while in flight (and Save is disabled while `parsing` / `opening`). New `.btn secondary` button in the existing row, after Open HTML. The intro paragraph text is modified per Functional scope 6. `lastParse` / `pasteText` local-storage behavior is unchanged.

## Acceptance criteria

1. **Button present and gated.** In `test_AdminSessionResumePaste.test.tsx`, **Save to Candidate** renders as the fourth button in the row (after Open HTML). It is disabled with no selected candidate, disabled with no `lastParse`, and disabled while Parse or Open HTML is in flight. It is enabled once a successful parse exists and a candidate is selected. Fail = missing, wrong position, or enabled in any of those disabled cases.
2. **Correct request.** Clicking Save sends exactly one `PUT /api/candidates/<selectedId>/data` whose JSON body is `{"artifacts":{"resume_structure":{"sections":<lastParse.resume_structure.sections>},"base_resume":<lastParse.base_resume>}}`. `base_resume` deep-equals `lastParse.base_resume`, and there is no `accent_color` or `artifact_id` key. Fail = a different route, a POST, a reshaped `base_resume`, extra keys, or a request to any `/api/admin/session_resume/*` save route.
3. **Persists as current base resume.** In UAT, parse a resume with candidate X selected, click Save, then open **Base Resume Content** for X: every parsed section appears with its parsed body. `SELECT COUNT(*) FROM artifacts WHERE entity_type='candidate' AND entity_id='<X>' AND artifact_type='base_resume' AND current=1` returns 1, and the prior current row (if any) now has `current=0`. Fail = editor shows the old resume, two current rows, or the prior row was updated in place.
4. **Layout replaced, accent kept.** After Save, X's section titles/order/enabled flags on Base Resume Content match `lastParse.resume_structure.sections`, and X's accent color is unchanged from before Save. Fail = X's old layout survives, a parsed section is missing, or the accent color changed.
5. **Experience clean.** After Save, `GET /api/candidates/<X>` returns `candidate_data.artifacts.base_resume.experience` deep-equal to `lastParse.base_resume.experience` (same job count, order, and `company`/`title`/`dates`/`location`/`accomplishments` values). The Base Resume Content experience editor shows one job per entry, with accomplishments as separate list items. Fail = a job is missing, merged, or reordered, a field is blank, accomplishments are collapsed into one string, or experience is absent.
6. **Feedback.** On 200, a success toast shows. On a mocked 400 `{"error":"boom"}`, the error toast and inline error both read `boom`, and **Save to Candidate** is enabled again with `lastParse` still present. Fail = no toast, generic message instead of the server's, or parse cleared.
7. **No backend change.** `git diff origin/dev...<ftr> --stat -- src/ui/api src/core src/data src/utils` is empty, and `grep -n "session_resume/save" -r src/` returns nothing. Fail = any backend diff or a new save route.
8. **Copy accurate.** The page intro no longer claims the page never saves: `grep -n "does not save to the database" src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` returns nothing, and the intro names Save to Candidate as the one action that writes. Fail = old sentence remains.

## Boundaries

Single-child epic — no siblings. Does not touch `src/ui/api/**`, `src/core/**`, `src/data/**`, `src/utils/**`, the session parse route, `ArtifactsBaseResumeContent.tsx`, or `ArtifactEditor.tsx`. Tests and test-bible pages are Betty's (`qa-child`).

## Notes for planning

Reuses the existing `PUT /api/candidates/<id>/data` operative save path as-is (Susan's answers on the parent: replace layout with the parse's sections; no confirm prompt — new artifact row, earlier versions `current = 0`). Parse and save share `_EXPERIENCE_JOB_ITEM_SCHEMA`, so experience passes through unreshaped.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1899-add-save-to-candidate-button`, child `sub/AST-1899/AST-1908-save-to-candidate-session-resume-paste`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-01T01:46:25.263Z
[code-rubric] PROCEED (Commit: 868c641) Existing PUT save, one page

#### betty — 2026-10-01T01:44:15.256Z
`origin/sub/AST-1899/AST-1908-save-to-candidate-session-resume-paste` @ `50c81b1ca` · 7 Vitest cases, bible block

#### chuckles — 2026-10-01T01:41:09.791Z
Delivery can go ahead (AST-1913). AST-1902 has landed on dev (PR #199, `1425567a9`), so the normal `merge-tests` route from `origin/tests` no longer adds AST-1902's `src/core/builder.py` change or its plan doc to AST-1899's diff against dev. AC7 holds.

- `origin/tests-clean-base` is back at `82423d73b`.
- `origin/tests` now has one commit that is not on dev: `58098c74c` (AST-1909's frontend test file `test_AdminTaskPrompts.test.tsx` and its bible entry, with no backend change). Betty decides whether it is acceptable for it to come along into the AST-1908 sub.
- `validate-tests-branch.sh` now gets past the marker check but still fails on local `tests` in `~/astral-tests`: `c2a2ca0f7` (unpushed `sync(publish-ref): origin/sub/AST-1898/AST-1911…`, 2 parents) is not a `merge-tests(AST-NNN):` merge. Betty needs to clean that up before she pushes.

#### chuckles — 2026-10-01T00:43:17.138Z
Delivery is on hold until AST-1902 lands on dev (Susan's call, AST-1913). Betty stays at Code Complete, and `betty-stage/AST-1908` @ `849ec23bf` stays as it is. After AST-1902 lands, Chuckles makes sure `origin/tests-clean-base` exists (restored at `82423d73b` if needed) and releases Betty to the normal `merge-tests` route.

#### betty — 2026-10-01T00:32:53.757Z
@susan — AST-1908 tests are ready but unpublished; two blockers on §9.

1. `validate-tests-branch.sh` can't pass for anyone: the `tests-clean-base` marker (AST-1574) is missing locally and on origin.
2. `origin/tests` carries `sync(ftr): origin/ftr/AST-1902…`, so `merge-tests` from any origin/tests SHA would bring AST-1902's `src/core/builder.py` + its plan doc onto AST-1899's sub — breaks AC7 (no backend diff) and in-scope-only.

Staged: `betty-stage/AST-1908` @ 849ec23bf (single parent = origin/tests; tests + bible only; 14/14 green, 7 new red on dev page). Local `tests` (unpushed AST-1911 + AST-1909 syncs) untouched. Holding Code Complete — need your call on delivery path.

#### betty — 2026-10-01T00:24:08.433Z
@susan — blocked: a concurrent Betty session (qa-fix AST-1909, session 57a48a05) shares ~/astral-tests. Its reset wiped my uncommitted AST-1908 tests; my reset then wiped its one uncommitted file (not recoverable; tests HEAD restored to its b8997f750, backup ref betty-bak/AST-1909-sync-20261001). Holding Code Complete — re-spawn me once AST-1909 is done. Manifest + 7 Vitest cases ready in-thread.

#### joan — 2026-10-01T00:18:55.669Z
[plan-rubric] PROCEED (Commit: d1d9a4252) one-file save wiring

#### hedy — 2026-10-01T00:16:13.723Z
`origin/sub/AST-1899/AST-1908-save-to-candidate-session-resume-paste` @ `d1d9a4252` · one-file page save plan

---

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

## Review stub (Hedy / build)

- **Commit:** `094161cd3` — `code(AST-1908): Save to Candidate on Session Resume Paste`
- **Branch:** `origin/sub/AST-1899/AST-1908-save-to-candidate-session-resume-paste`
- **Files:** `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` only (Stage 1 steps 1–7 as written).
- **Compile/lint:** `npx tsc -b --noEmit` clean; `npx eslint src/pages/AdminSessionResumePaste.tsx` clean. Full `npm run lint` reports 32 problems identical with and without this change (pre-existing, none in this file).
- **Self-check §9:** no "does not save to the database"; no `session_resume/save` in `src/`; empty backend diff vs `origin/dev`.
- **Canon note for review:** `astral.standards.dry-and-focused-functions` — `handleSave`'s non-OK error read mirrors `handleOpenHtml`'s block by the plan's ⚠️ Decision (no refactor of existing handlers under `astral.standards.in-scope-only`). Flagged so Radia can rule on it; not changed at build.

## Radia review

[code-rubric]
**Ticket:** AST-1908
**Publish ref:** 868c641836a20309d02d167a28feaf21fec8206e
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores
patt.artifact.write-operative | A | | Client PUT reuses existing `PUT /api/candidates/<id>/data` → server `save_candidate_data`; no parallel write path or `session_resume/save`
patt.artifact.ui-consistency | A | | `{ artifacts: { resume_structure: { sections }, base_resume } }`; no client `artifact_id`; Exception 3 (session paste, not ArtifactEditor fork)
astral.standards.dry-and-focused-functions | B | | `AdminSessionResumePaste.tsx` — non-OK JSON/`HTTP` handling duplicated in `handleSave` vs `handleOpenHtml`; plan ⚠️ defers extract under in-scope-only
astral.layers.ui-config-driven-business-logic | A | | Parse payload sent as-is; sections-only structure; no React section-id or experience field lists
astral.standards.in-scope-only | A | | Product delta is one page file; no backend `src/ui/api|core|data|utils` diff

## Column diff vs plan stage
astral.standards.dry-and-focused-functions | Joan A (plan: inline mirror intentional) | Radia B (two-call-site duplicate remains; bounded and documented)

## Frame diff
(none)

## Findings

### fix-now
(none)

### discuss
(none)

### advisory
- **Plan fidelity:** `AdminSessionResumePaste.tsx` matches Stage 1 steps 1–7 (handler body, disabled props, button row, intro copy); build stub self-checks (no backend stat, no `session_resume/save`, no stale intro line) align with AC7/AC8.
- **Estimate footprint:** Confirm **1** — one-page product change plus Betty’s manifest/tests/bible on the publish ref; fits the ticket.
- **Test carry:** Three-dot diff includes `tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx` (+7 cases) and `docs/test-bible/frontend/pages.md` — expected `qa-child` / `merge-tests` for this child, not sibling product scope.
- **UAT remainder:** AC3–AC5 (DB `current=1`, layout/accent, experience deep-equal) remain manual/UAT per Boundaries; component tests correctly cover AC1/2/6/8 only.
- **Canon Scope observation:** `patt.artifact.ui-consistency` frontmatter still **draft** in `canon/directives/active`; reuse matches Implementation §5 + Exception 3 — same non-blocking note Joan left at plan time.
- **Corpus note:** Joan plan artifact pinned `bd68954dc854ca80fca1fc391821dff9ff288a7a`; review corpus tip `e1f2699…` (clean). No change to the five frozen directives’ substance at review time.

## What's solid
- Operative save contract: single PUT, sections-only `resume_structure`, passthrough `base_resume`, success/error toasts + inline error on failure, `lastParse` retained (AC6).
- Busy gating: fourth button, `Saving…`, all four buttons disabled in flight; tests exercise Parse/Open HTML in-flight disables.
- Scope gate honored for product code; backend reuse matches parent epic intent.

## Recommended actions (downstream only — not executed in ASK mode)
- **resolve-child:** No canon fix required; optional **B→A** only if Hedy extracts a tiny shared `readApiError(r)` helper in the same file without touching `handleParse` — not required for PROCEED.
- **Chuckles:** Append this artifact; post slim upshot `--as radia`; move **Tests Passed → Review Posted**; route Hedy **resolve-child** then UT for AC3–5.

context_tokens≈24000
