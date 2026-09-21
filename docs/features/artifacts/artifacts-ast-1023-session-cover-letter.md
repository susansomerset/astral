# AST-1023 — Session Cover Letter
**Component:** artifacts  
**Children:** AST-1024, AST-1025  
**Linear archived:** AST-1023 2026-08-05; AST-1024 2026-08-05; AST-1025 2026-08-05

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-07-28 20:02 | AST-1024 | docs | `b386eebbf` | docs(AST-1024): plan — session cover letter HTML builder + admin HTML API |
| 2026-07-28 20:09 | AST-1024 | docs | `0dde7c971` | docs(AST-1024): plan discuss round=1 — Stage 3 fields from config |
| 2026-07-28 20:14 | AST-1024 | docs | `677e73386` | docs(AST-1024): review stub after build |
| 2026-07-28 20:14 | AST-1024 | code | `db3915d40` | code(AST-1024): session cover letter HTML builder + admin HTML API |
| 2026-07-28 20:22 | AST-1024 | merge-tests | `053830d3b` | merge-tests(AST-1024): origin/tests 055e81c6f |
| 2026-07-28 20:22 | AST-1024 | test | `055e81c6f` | test(AST-1024): session cover letter HTML builder + admin API coverage |
| 2026-07-28 20:33 | AST-1024 | docs | `d5813c671` | docs(AST-1024): Radia review — findings |
| 2026-07-28 20:35 | AST-1024 | resolve | `18c1eadd4` | resolve(AST-1024): — clean |
| 2026-07-28 20:44 | AST-1025 | docs | `f42b582bf` | docs(AST-1025): plan — Admin Session Cover Letter page + session retention |
| 2026-07-28 20:49 | AST-1025 | code | `ac23db55a` | code(AST-1025): Admin Session Cover Letter page + session retention |
| 2026-07-28 20:50 | AST-1025 | docs | `7f8b06e67` | docs(AST-1025): review stub — build tip ac23db55 |
| 2026-07-28 20:53 | AST-1025 | test | `ab6e07a83` | test(AST-1025): Admin Session Cover Letter page + nav retention coverage |
| 2026-07-28 20:53 | AST-1025 | merge-tests | `f3061950c` | merge-tests(AST-1025): origin/tests ab6e07a83 |
| 2026-07-28 20:56 | AST-1025 | docs | `f7320b88f` | docs(AST-1025): Radia review — findings |
| 2026-07-28 20:58 | AST-1025 | resolve | `2469de013` | resolve(AST-1025): — clean |
| 2026-07-28 21:03 | AST-1023 | prep-uat | `9df034b69` | prep-uat(AST-1023): rebuild merge ticket log |
| 2026-08-05 14:54 | AST-1024 | docs | `f2edc50b2` | docs(AST-1024): archive Linear issue content |
| 2026-08-05 14:54 | AST-1025 | docs | `2c6d7782c` | docs(AST-1025): archive Linear issue content |
| 2026-08-05 14:58 | AST-1023 | docs | `a8ca0bb28` | docs(AST-1023): archive Linear issue content |

## Epic — AST-1023
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1023/session-cover-letter · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: High / — · Blocked by / blocks / related: —_

### Purpose

Susan needs a job-independent Session Cover Letter workbench — the cover-letter twin of AST-985 Session Resume Paste — so she can supply cover-letter field values, see Astral's styled cover-letter HTML in a new browser tab, and Print → PDF. Job-scoped cover-letter chains and candidate-bound profile injection stay where they are; this epic is a detached Admin convenience tool with browser session retention and no durable artifact write.

### Functional scope

* **Admin cover-letter field workbench:** A dedicated Admin screen where Susan enters the cover-letter field values (sender/from block, date, letter body, sign-off, and any subject/to fields that belong in the golden layout). Nav lives under **Admin**, parallel to Session Resume Paste — not inside Base Resume Content, JAR, or Materials Preview.
* **Session cover-letter payload (fields-only, mostly detached):** Susan enters field values (no paste → LLM parse in this epic). Values become an in-memory cover-letter payload aligned with the existing cover-letter artifact contract (Subject / Letter family and related emit fields), plus session-supplied from/contact and date blocks needed for the golden HTML. No job id required. **Signature:** when a candidate is selected and has a signature image on profile, use that image; otherwise print the typed name as on a professional electronic letter (no session upload). Letter body/from/date fields still come from the Admin form — not from candidate `artifacts.*`.
* **Golden-styled HTML + new tab:** Render a print-oriented HTML document matching the SomersetCover layout in the Original brief (cover-letter DOM + cover CSS, shared accent/font tokens as appropriate) and open it in a new browser tab for Print → PDF. No server-side PDF generation.
* **Session retention (no DB write):** Field values and last successful render payload are retained in the browser the same way Session Resume Paste / Data Management retain working state. Nothing is written to candidate or job artifacts in this epic.
* **Job-independent:** Does not enter BUILD_ARTIFACTS, job `cover_letter` persistence, or Recommended Job Report paths.

#### UI inventory (new vs reused)

| Kind | Screen / component | Role in this epic |
| -- | -- | -- |
| **New** | Session Cover Letter page under **Admin** nav | Field inputs, Open HTML, status/errors, session retention |
| **New** | Session-scoped storage for this tool's fields / last render inputs | Retain working state without DB |
| **Reused** | Cover-letter artifact field contract (Subject / Letter family) and builder cover emit family | Shape of letter content + HTML generation adapted for session/in-memory input |
| **Reused** | Admin auth + new-tab open pattern from Session Resume Paste / materials HTML | Authenticated HTML response; display outside SPA chrome |
| **Reused** | Toast / ordinary form controls | Success/error feedback |
| **Not used** | Job cover-letter daisy-chain / Manage Tasks prompts | Agent drafting stays on the job pipeline |
| **Optional read** | Selected candidate profile signature image only | When present, inject into sign-off; form fields remain source of letter content |
| **Not used** | Session Resume Paste page as the host UI | Sibling Admin tool; do not overload the resume paste screen unless Susan directs a merge |

### Architectural definition

* **Patterns to reuse:** `pattern.ui.admin-endpoint` (Admin HTML/API routes stay thin, authenticated, config-nav driven); `pattern.layers.import-discipline` (core owns HTML emit; UI API delegates; no ui→data); `pattern.config.config-block` (Admin nav entry via `NAV_CONFIG`; cover shape remains config-owned).
* **New patterns proposed:** Session-scoped cover-letter workbench (Admin field entry → in-memory cover payload → golden HTML tab, browser retention, no durable write, no candidate/job bind) — mirror of the AST-985 session-resume workbench for cover letters; catalog only after Archie approval.
* **Applicable statutes:** `astral.standards.in-scope-only` (do not touch resume Take 2 emit, job chains, or unrelated Admin tools); `astral.standards.no-cross-contamination` (session cover path must not leak into job/candidate persistence); `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` (extend builder/cover emit cleanly; prefer shared helpers over a second stylesheet island when safe); `astral.standards.debug-contract-gated` / `astral.standards.logging-via-utils` (any touched backend `debug=` cover emit/API path uses Style D index headers + `|` detail per AST-538; no React debug contract); `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic` / `astral.layers.import-direction`; `astral.config.config-source-of-truth`.

### Boundaries

* **No database persistence** of field values or HTML onto candidate or job artifacts — browser retention only.
* **No durable candidate bind** — does not write `artifacts.*` or profile. Letter fields come from the Admin form. **Exception (Archie):** optional read of the **selected** candidate's profile signature image when present; otherwise name-only sign-off. Form render must still succeed with no candidate selected.
* **No job coupling** — does not draft via `draft_cover_letter` / check / finalize chains; does not write `job_data.artifacts.cover_letter`.
* **Does not replace** job cover-letter editing in Job Analysis Report / materials preview.
* **Does not change** Manage Tasks prompts, TASK_CONFIG registry shape, or dispatch chains.
* **No server-side PDF** — HTML tab; user Print → PDF.
* **Does not own resume Take 2 golden work** (AST-1019 / children) — resume stylesheet/chrome stays on that epic; this epic owns cover-letter session UX + cover golden layout from the Original brief.
* **No new top-level** `artifacts/` **directory**.
* **Must not break** Session Resume Paste (AST-985/986/987), job cover HTML routes, Base Resume Content, or other Admin nav items.

### Acceptance criteria

1. From the new **Admin** Session Cover Letter screen, Susan can enter cover-letter field values and open a new tab showing styled cover-letter HTML consistent with the Original-brief SomersetCover layout (from block, date, letter body, sign-off; subject/to if included in scope).
2. Render succeeds without a job id; letter fields come from the Admin form. With no candidate selected, HTML still opens (name-only sign-off). With a selected candidate that has a profile signature image, that image appears in the sign-off.
3. Susan can Print → PDF from that tab; no server-generated PDF file is required.
4. Closing and reopening the tool within the same browser session restores the last entered field values (and last successful render inputs if retained); clearing site data wipes them.
5. Completing the flow does not create or update candidate or job cover-letter artifacts or any other durable store for this session.
6. Failed validation/render surfaces a clear error on the Admin screen and does not open a blank/broken HTML tab as success.
7. When `debug=True` on touched backend cover emit/API paths, logs show Style D per-index headers and `|` working detail for what was found/recorded (not counts-only).

### Dependencies and blockers

none. Foundations on `dev`: cover-letter artifact shape (AST-309 lineage), builder cover emit + HTML routes (AST-294 / AST-298 family), Admin session-resume workbench pattern (AST-985–987). Archie: session-only golden cover (no job `build_cover_letter` backfill this epic). AST-1019 resume Take 2 stays separate.

### Open questions

none.

### Proposed child tickets

**1[!]: Session cover letter HTML builder + admin HTML API — Ada** — Core session cover emit from in-memory field payload (no job load; no artifact persist) producing golden SomersetCover HTML; Admin `POST` HTML route under existing admin auth. Optional signature-image read from the **selected** candidate profile when present — otherwise name-only sign-off. Owns debug contract on touched backend paths. Does **not** own Admin React page or localStorage. Unblocks #2.
**Citations:** `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `astral.standards.debug-contract-gated`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`.

**2: Admin Session Cover Letter page + session retention — Katherine** — New Admin nav page: field inputs for the cover-letter blocks, browser session retention, call #1 HTML API, open rendered HTML in a new tab (Session Resume Paste UX twin). Does **not** own core emit/CSS golden parity.
**Citations:** `pattern.ui.admin-endpoint`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`.

**New pattern:** Session cover-letter workbench introduced by #1+#2 (parallel to AST-985 session resume); downstream "save to candidate/job" can reuse the same payload/HTML contract later.

**Monolith check:** Functional scope has 5 capabilities; 2 children split backend session emit/API from Admin UI/retention/new-tab (layers + agents differ). Fields-only (Archie) — no parse API child.

### Original brief

Like we are parsing and creating a resume, create a Session Cover Letter where the candidate can specify the values for the fields, and create a styled cover letter for the candidate as an html blob so the candidate can choose to print it to PDF.

```
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SomersetCover</title>
  <style>
/* Susan Somerset Resume - Version 07 */
/* Compact styling with decorative headers, tighter spacing, and mixed fonts */

:root {
  --max-width: 800px;
  --accent-color: #3c2c6e;
  --header-color: #3c2c6e;
  --text-primary: #1a1a1a;
  --text-secondary: #444;
  --text-tertiary: #666;
  --border-light: #e0e0e0;
  --border-medium: #ccc;
  
  --header-font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  --body-font-family: Palatino, "Palatino Linotype", "Book Antiqua", serif;
  --list-font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 14px 20px 20px;
  background: #f5f5f5;
  font-family: var(--body-font-family);
  color: var(--text-primary);
  line-height: 1.6;
  font-size: 15px;
}
[… full resume typography / header / decorative-h2 / role / education / skills / mobile / print rules, identical to the AST-993/AST-1019 golden resume `<style>` block …]
  </style>
  <style>
    body {
      margin: 0;
      padding: 40px 20px;
      background: #f5f5f5;
      font-family: var(--body-font-family);
    }
    
    .cover-letter {
      max-width: 700px;
      margin: 0 auto;
      padding: 14px 35px 35px 35px;
      background: white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      color: var(--text-primary);
      line-height: 1.65;
    }
    
    .fromBlock {
      margin: 0 0 32px;
      padding-bottom: 20px;
      border-bottom: 2px solid var(--accent-color);
      font-size: 17px;
      color: var(--accent-color);
      text-align: left;
      line-height: 1.5;
      font-weight: 700;
    }
    
    .toBlock {
      margin: 16px 0 16px;
      font-size: 15px;
      color: var(--text-primary);
      text-align: left;
      line-height: 1.5;
      font-weight: 400;
    }
    
    .letterdate {
      margin: 40px 0 16px;
      font-size: 14px;
      color: var(--text-secondary);
      text-align: left;
    }
    
    .lettersubject {
      margin: 0 0 24px;
      font-size: 15px;
      font-weight: 400;
      color: var(--text-primary);
      text-align: left;
    }
    
    .lettercontent {
      margin: 0 0 24px;
      text-align: left;
    }
    
    .lettercontent p {
      margin: 0 0 16px;
      font-size: 15px;
      line-height: 1.65;
      color: var(--text-primary);
    }
    
    .lettercontent p:last-child {
      margin-bottom: 0;
    }
    
    .letterSignoff {
      margin: 24px 0 0;
      font-size: 15px;
      text-align: left;
      line-height: 1.5;
    }
    
    .signature-img {
      display: block;
      height: 61px;
      margin: 8px 0 -25px 0;
    }
    
    @page {
      margin-top: 1in;
    }
    
    @page :first {
      margin-top: 0.5in;
    }
    
    @page {
      orphans: 3;
      widows: 3;
    }
    
    @media print {
      body {
        background: #fff;
        padding: 0;
      }

      .cover-letter {
        box-shadow: none;
        padding: 0.5in;
      }
      
      /* Set orphans/widows on container and paragraphs */
      .lettercontent {
        orphans: 3;
        widows: 3;
      }
      
      .lettercontent p {
        orphans: 3;
        widows: 3;
        /* Allow breaking but protect against short breaks */
        page-break-inside: auto;
        break-inside: auto;
      }
    }
  </style>
  <meta name="description" content="Cover Letter - Susan Somerset" />
</head>
<body>
  <main>
    <div class="cover-letter">
      <div class="fromBlock">
        Susan Somerset • Oakland, CA<br>
        hire@susansomerset.com • 415-745-5238
      </div>

      <div class="letterdate">July 27, 2026</div>
      <div class="lettercontent">
        <p>Dear Hiring Team,</p>
        <p>I have built numerous workflow automation and journey-orchestration solutions in my 15 years of consulting. Most recently, I used AI-development tools to design and build an agentic AI platform that inverts the job search to be candidate-forward, moving candidates through a complex staged engagement to find employment in a well-matched professional position.</p>
        <p>Each user advances as behavioral and transactional events fire over time, governed by the entry and exit criteria at each stage, the triggers that move someone forward or into a win-back track, and the suppression and frequency rules that keep email, push, and SMS from talking over each other. And no journey is more reliable than the unified profile beneath it that every segment and trigger reads from — the transition points can need more attention than the segments themselves.</p>
        <p>In my experience, when a company brings in a contract TPM mid-program, it's often because something isn't moving and the reason hasn't made itself clear yet. The right contractor embeds in the program, meaningfully discerns the hidden blockers, builds mutual trust and respect, and drives consensus on specific solutions so delivery can accelerate.</p>
        <p>What I bring in the first month isn't a stack of new stand-up meetings, but a clear read: the real state of the program, the top risks to your milestones, and a dependency map that makes visible what everyone feels but no one has yet drawn. I am up to speed in days, not weeks, connecting with critical stakeholders, ICs and executives alike, to triage what's actually blocking delivery and quickly gain buy-in to get the team moving toward aligned objectives.</p>
        <p>I'm remote-based out of Oakland, CA, and available on your timeline. Please let me know if this sounds like a good fit.</p>
      </div>
      <div class="letterSignoff">
        Best,<br>
        <img src="SomersetSignature.png" class="signature-img" alt="Signature"><br>
        Susan Somerset
      </div>

    </div>
  </main>
</body>
</html>
```

_(The elided middle section is the identical golden resume `<style>` block already captured in full in [artifacts-ast-993-resume-render-format-discrepancies.md](artifacts-ast-993-resume-render-format-discrepancies.md) and [artifacts-ast-1019-take-2-resume-render-format-discrepancies.md](artifacts-ast-1019-take-2-resume-render-format-discrepancies.md) — Susan's pasted page source carried it forward; it is not part of the cover-letter contract this epic implements.)_

#### Comments

##### chuckles — 2026-07-29T02:44:27.704Z
@susan Open questions on AST-1023 (Session Cover Letter):

1. Input mode — fields-only for v1, or also paste → LLM parse like Session Resume Paste?
2. Signature image — omit, session upload/data-URL, or optional pull from selected candidate profile?
3. Job cover HTML backfill — golden SomersetCover CSS/DOM for job `build_cover_letter` / materials tabs in this epic, or session-only?
4. Admin IA — separate Admin nav item (recommended) or tab/mode on Session Resume Paste?

_(Resolved into the definition above: fields-only for v1 (no parse API child); signature is an optional pull from the selected candidate's profile image, else name-only; session-only golden cover — no job `build_cover_letter` backfill this epic; separate Admin nav item.)_

### Files changed (plan vs actual)

_No product commit trail on the parent — the one `prep-uat(AST-1023)` commit rebuilds the merge ticket log. Implementation landed via AST-1024 (core emit + API) and AST-1025 (Admin page + retention)._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1024 — Session cover letter HTML builder + admin HTML API
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1024/session-cover-letter-html-builder-admin-html-api-session-cover-letter · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1023; unblocks AST-1025_

#### What this implements

Core session cover emit from an in-memory field payload (no job load; no artifact persist) producing golden SomersetCover HTML, plus an Admin `POST` HTML route under existing admin auth. Optional signature-image read from the **selected** candidate profile when a `candidate_id` is supplied — otherwise name-only sign-off. Owns Style D debug on touched backend paths. Does **not** own Admin React page, nav, or session retention.

#### Citations

`pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `astral.standards.debug-contract-gated`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`

#### Acceptance criteria

Parent AC1–3, 5–7 for the backend slice: Admin screen can render SomersetCover HTML from form fields; no job id required; no candidate/job artifact writes; failed validation returns a clear error, never a broken-success HTML; Style D debug on touched paths.

#### Boundaries

Does not own Admin React page, nav, or localStorage (sibling AST-1025). Does not touch job cover-letter emit/routes or artifact writers.

#### API contract (for AST-1025)

**`POST /api/admin/session_cover_letter/html`**
- Auth: `@require_admin`.
- Request JSON:
  ```json
  {
    "from_block": "Susan Somerset • Oakland, CA\nhire@susansomerset.com • 415-745-5238",
    "letter_date": "July 27, 2026",
    "to_block": "",
    "subject": "",
    "letter": "Dear Hiring Team,\n\nParagraph two…",
    "signoff_closing": "Best,",
    "signature": "Susan Somerset",
    "candidate_id": null
  }
  ```
  Field keys and required flags come from `BUILD_CONFIG["session_cover_letter"]["fields"]`. `candidate_id`: optional — omit/`null`/`""` → no candidate read (name-only sign-off); non-empty string → optional profile signature-image read only. Naming spine aligns with the cover artifact: `subject` ↔ `Subject`, `letter` ↔ `Letter`, `signature` ↔ `signature`; session also carries layout fields (`from_block`, `letter_date`, `to_block`, `signoff_closing`) that job artifacts do not store today.
- Success **200**: raw HTML body, `Content-Type: text/html; charset=utf-8`.
- Client / validation failures **400**: `{ "success": false, "error": "<clear message>" }` — never return success HTML on failure. Unknown/missing candidate when `candidate_id` is non-empty → **400** with a clear error (do not silently pretend no candidate).

**Detached rules (hard):** do not load a job or read `job_data.artifacts.cover_letter`; do not call `save_candidate`, job artifact writers, or any cover-letter chain task; letter field values come **only** from the request body — the candidate row (when id provided) is used **only** for `profile.cover_letter_signature_image` via existing `_safe_image_src`; do not change `/candidate/cover/<job_id>` or job cover emit DOM/CSS.

#### Stage 1: Config field contract

**Done when:** `BUILD_CONFIG["session_cover_letter"]` exists with document title and the field map below; no other config blocks changed.

```python
"session_cover_letter": {
    "document_title": "SomersetCover",
    "fields": {
        "from_block": {"required": True},
        "letter_date": {"required": True},
        "to_block": {"required": False},
        "subject": {"required": False},
        "letter": {"required": True},
        "signoff_closing": {"required": True},
        "signature": {"required": True},
    },
},
```
Do **not** add `NAV_CONFIG` entries (AST-1025). Do **not** change `artifact_shapes["cover_letter"]`.
⚠️ **Decision:** Config owns the session field keys so AST-1025 form + this API share one spine without hardcoding duplicate required lists in React and Flask.

#### Stage 2: Session SomersetCover builder (core)

**Done when:** `build_session_cover_letter` returns a standalone print-oriented HTML document whose DOM matches Original-brief SomersetCover blocks (`fromBlock`, optional `toBlock` / `lettersubject`, `letterdate`, `lettercontent`, `letterSignoff`); no job load; optional signature image only from selected candidate profile; empty/invalid required fields raise `ValueError` with clear messages; `debug=True` emits Style D headers + `|` detail.

1. Module docstring public list gains `build_session_cover_letter`. New public function immediately after `build_session_base_resume`: `build_session_cover_letter(fields: dict, *, candidate_id: Optional[str] = None, debug: bool = False) -> str`.
2. When `debug=True`, `_log.set_debug_flag(True)` before other work.
3. Validate `fields`: non-`dict` → `ValueError`; read `cfg = BUILD_CONFIG["session_cover_letter"]`, `field_defs = cfg["fields"]`; for each key coerce missing → `""`, require `str` else `ValueError(f"{key} must be a string")`, required + blank → `ValueError(f"{key} is required")`; ignore unknown extra keys.
4. Resolve optional signature image (read-only): `sig_src = None`; if `candidate_id` non-empty after strip, `get_candidate` (raise `ValueError` if not found), `_coerce_candidate_blob`, `sig_src = _safe_image_src(profile.get("cover_letter_signature_image"))` (may stay `None`); if `candidate_id` is `None`/non-str/blank, do **not** call `get_candidate`.
5. Emit via new helper `_emit_session_cover_html_document(fields, signature_image_src=sig_src) -> str`. Do **not** call `_emit_html_document`, `_emit_cover_sections_html`, or job cover builders.
6. `_emit_session_cover_html_document`: pull colors/fonts from `BUILD_CONFIG["default_style"]` the same way `_emit_html_document` does; `<title>`/meta description use `BUILD_CONFIG["session_cover_letter"]["document_title"]`; CSS is session-only SomersetCover rules from the Original brief (`:root` tokens; `body` / `.cover-letter` / `.fromBlock` / `.toBlock` / `.letterdate` / `.lettersubject` / `.lettercontent` / `.lettercontent p` / `.letterSignoff` / `.signature-img` at `height: 61px; margin: 8px 0 -25px 0`; `@page` / `@media print` rules from the brief's second `<style>` block) — do **not** copy the full resume body stylesheet or modify the `_emit_html_document` CSS string. Body: `<main><div class="cover-letter">` → required `.fromBlock` (newlines → `<br>`) → optional `.toBlock` → `.letterdate` → optional `.lettersubject` → `.lettercontent` (paragraphs, step 8) → `.letterSignoff` (step 9).
7. Paragraphize `letter`: normalize `\r\n`→`\n`, strip; split on blank lines (`re.split(r"\n\s*\n", text)`), keep non-empty stripped chunks as escaped `<p>` bodies with internal single newlines rendered as `<br>` (survives pasted single-newline breaks); if the split yields one chunk that still contains `\n`, split that chunk on `\n` into separate `<p>` tags (form textarea UX).
8. Sign-off (`letterSignoff`): `html.escape(signoff_closing)` + `<br>`; if `signature_image_src`, `<img src="..." class="signature-img" alt="Signature">` + `<br>` (attribute-escaped); then `html.escape(signature)` (typed name — always, including when image present).
9. `debug=True` Style D: header `func="builder.build_session_cover_letter"`, `index=1`, `total=1`, `identifier=candidate_id.strip() if candidate_id else "session"`, outcome success; detail lines for which required fields were non-empty, `to_block`/`subject` present/omitted, `candidate_id` used or not, `signature_image=accepted|absent_or_rejected|skipped_no_candidate`, `html_chars=…`, optional truncated preview via `debug_detail_block`. On validation failure before emit, use `_emit_builder_failure` with the same `func` name.
10. Return the HTML string. Forbidden: any `save_*` / artifact write / job fetch.

⚠️ **Decision:** Session-only golden cover DOM/CSS (Original brief), not a backfill of job `build_cover_letter`. Archie: no job cover upgrade this epic.

⚠️ **Decision:** Optional `candidate_id` is explicit in the request (Katherine passes selected id or omits). Server does not invent candidate context from Flask cookies/session beyond what the JSON body provides.

#### Stage 3: Admin HTML route

**Done when:** `POST /api/admin/session_cover_letter/html` is registered on `admin_bp`, requires admin auth, returns `text/html` on valid body and JSON `{success:false,error}` on bad input / `ValueError`; `py_compile` clean.

```python
@admin_bp.route("/session_cover_letter/html", methods=["POST"])
@require_admin
def session_cover_letter_html():
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        return jsonify({"success": False, "error": "JSON object body is required"}), 400
    # Field keys from config only — do not hardcode the key list here (Joan plan-discuss round=1).
    field_defs = BUILD_CONFIG["session_cover_letter"]["fields"]
    fields = {k: body.get(k, "") for k in field_defs}
    raw_cid = body.get("candidate_id")
    candidate_id = raw_cid.strip() if isinstance(raw_cid, str) else None
    if candidate_id == "":
        candidate_id = None
    try:
        html_out = build_session_cover_letter(fields, candidate_id=candidate_id, debug=ui_llm_debug())
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return Response(html_out, mimetype="text/html; charset=utf-8")
```
Do not register a new blueprint or change `server.py`. Do not alter `/api/admin/session_resume/*` or `/candidate/cover/<job_id>`.

⚠️ **Decision:** API builds `fields` by iterating `BUILD_CONFIG["session_cover_letter"]["fields"]` so config remains the single key spine (AST-1025 form + Flask + core). `candidate_id` stays outside that map. Required/type validation stays in core (Stage 2).

**Self-Assessment:** Single-Component — config field contract, one core session emit path beside `build_session_base_resume`, one Admin POST HTML route; job cover emit and React left untouched. Conf high — mirrors AST-987 session HTML pattern; SomersetCover DOM/CSS is specified in the parent Original brief; signature-image reuse of `_safe_image_src` is known. Risk Medium — mistaken reuse of job cover emit or a write path would contaminate job/candidate artifacts or change materials preview; the plan forbids those paths and keeps session CSS/DOM isolated.

#### Revisions

**Revision 1 — 2026-07-29** — Driven by Joan `[plan-discuss] round=1 concern` **REVISE**: Stage 1's ⚠️ Decision said config owns the session field keys so the API and AST-1025's form share one spine "without hardcoding duplicate required lists in React and Flask," but Stage 3 then built `fields` from an explicit hardcoded seven-key `body.get(...)` dict — reintroducing exactly the drift the Decision forbade (a config key added later would be silently dropped by the API; core would never see it). Joan cited `astral.config.config-source-of-truth`, `astral.standards.dry-and-focused-functions`, and `astral.standards.no-hardcoded-sets` as violated. **Fix:** Stage 3 now builds `fields = {k: body.get(k, "") for k in BUILD_CONFIG["session_cover_letter"]["fields"]}` (import `BUILD_CONFIG` from utils); `candidate_id` stays outside that map; required/type validation stays in core (Stage 2, unchanged).

##### Comments

###### ada — 2026-07-29T03:02:19.062Z
Plan @ `b386eebb`. Single-Component — config field contract, session SomersetCover emit in `builder.py`, one Admin POST HTML route; job cover emit and React left to siblings/out of scope. Conf high; Risk Medium.

###### joan — 2026-07-29T03:07:20.538Z → 03:10:44.703Z (plan-rubric.v1)
Round=1 **REVISE** — Stage 3 hardcoded seven-key `body.get` dict duplicated `BUILD_CONFIG["session_cover_letter"]["fields"]`, contradicting the Stage 1 Decision (`config-source-of-truth` / `dry-and-focused-functions` / `no-hardcoded-sets` violated). After Revision 1: **APPROVED** (tip `0dde7c97`) — Stage 3 now iterates config keys. All in-scope statutes **conforms**.

###### betty — 2026-07-29T03:23:15.152Z / 03:23:23.630Z
QA manifest AST-1024: session cover letter HTML builder + admin API coverage (`test_builder.py`, `test_api_admin.py`, `test_config.py`). Publish `@ 053830d3` (`merge-tests(AST-1024): origin/tests 055e81c6`).

###### radia — 2026-07-29T03:34:10.245Z (code-rubric.v1)
**Overall: DISCUSS** (procedural stragglers only). Stages 1–3 match the plan bible: config field spine, session-only SomersetCover emit, Admin POST under `@require_admin`; Stage 3 iterates `BUILD_CONFIG["session_cover_letter"]["fields"]` (Joan Revision 1); no job cover reuse, no artifact writes, optional candidate signature via `_safe_image_src` only; Style D gated on `debug=True` with index + `|` detail + `debug_detail_block`. All in-scope statutes **conforms**. **discuss (C4 stragglers):** `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` — Joan-excluded, in-scope on the code diff, each **conforms**. No **fix-now**.

#### Resolution (2026-07-29)

Radia tip `d5813c67` (docs-only, after product `053830d3`) · DISCUSS. fix-now: none — no product changes. discuss (C4 stragglers): acknowledged — substance already **conforms** (plan under `docs/features/`, single ticket file, Betty owns tests/bible; engineer `code()` was src-only). No product or plan-stage change.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Add `BUILD_CONFIG["session_cover_letter"]` field contract (keys + required flags + document title) | `db3915d40` |
| ✓ | `src/core/builder.py` | Add `build_session_cover_letter` + session-only SomersetCover emit helpers; update module public list | `db3915d40` |
| ✓ | `src/ui/api/api_admin.py` | Add `POST /api/admin/session_cover_letter/html` (`@require_admin`) — validate JSON, return `text/html` or JSON error | `db3915d40` |
| | _tests_ | builder + admin API + config coverage | `055e81c6f` — `test_builder.py` / `test_api_admin.py` / `test_config.py` + test-bible (Betty) |

### AST-1025 — Admin Session Cover Letter page + session retention
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1025/admin-session-cover-letter-page-session-retention-session-cover-letter · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1023; blockedBy (landed): AST-1024_

#### What this implements

New Admin nav page (second item under Session Resume): field inputs for the cover-letter blocks, browser session retention, call sibling HTML API, open rendered HTML in a new tab (Session Resume Paste UX twin). Does **not** own core emit/CSS golden parity.

#### Citations

`pattern.ui.admin-endpoint`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`

#### Acceptance criteria

Parent AC1 (Admin screen enter fields + open styled HTML), AC3 (Print → PDF, no server PDF), AC4 (session retention of fields, wiped by site-data clear), AC5 (no durable writes), AC6 (clear error, no broken-success tab).

#### Boundaries

Does not own core session cover emit or golden CSS. Does not upgrade job cover HTML. Does not merge into Session Resume Paste page (separate Admin nav item). After AST-1024.

#### Dependency contract (AST-1024 — call site only)

`POST /api/admin/session_cover_letter/html` (already on `origin/ftr/ast-1023-session-cover-letter` after merge): `@require_admin`; request JSON field keys from `BUILD_CONFIG["session_cover_letter"]["fields"]` — required `from_block`, `letter_date`, `letter`, `signoff_closing`, `signature`; optional `to_block`, `subject`; optional `candidate_id` (omit/`null`/`""` → name-only sign-off, non-empty string → optional server-side signature-image read); success 200 raw HTML; failure 400 `{success:false,error}` — never open the HTML tab on non-success.

#### Stage 1: Admin nav + route registration

**Done when:** Admin sidebar shows **Session Cover Letter** immediately after **Session Resume Paste**; navigating to `/admin/session_cover_letter` renders inside `AdminRoute`.

`NAV_CONFIG` Admin `items`, immediately after Session Resume Paste: `{"label": "Session Cover Letter", "path": "/admin/session_cover_letter"}`. `routes.tsx`: import `SessionCoverLetter`; child route `{ path: "admin/session_cover_letter", element: <AdminRoute><SessionCoverLetter /></AdminRoute> }` next to `admin/session_resume_paste`. New `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx`, default-export `SessionCoverLetter` — prefer implementing Stage 2 in the same build pass so the route is not empty in production.

⚠️ **Decision:** Separate Admin nav item (not nested inside Session Resume Paste), matching parent UI inventory and ticket Boundaries.

#### Stage 2: Session Cover Letter page + localStorage + Open HTML

**Done when:** From Admin → Session Cover Letter, Susan can enter field values, Open HTML opens a new tab with styled cover HTML on success; failed validation/render shows a clear error and does **not** open a blank/broken tab; leave/return within the same browser session restores field values and last successful render inputs via `localStorage`; clearing site data wipes them; no candidate/job artifact writes occur.

1. **Field spine (page-local mirror of config):**
   ```ts
   /** Must match BUILD_CONFIG["session_cover_letter"]["fields"] keys/required (AST-1024). */
   const SESSION_COVER_FIELDS = [
     { key: "from_block", label: "From block", required: true, rows: 3 },
     { key: "letter_date", label: "Date", required: true, rows: 1 },
     { key: "to_block", label: "To block", required: false, rows: 2 },
     { key: "subject", label: "Subject", required: false, rows: 1 },
     { key: "letter", label: "Letter body", required: true, rows: 12 },
     { key: "signoff_closing", label: "Sign-off closing", required: true, rows: 1 },
     { key: "signature", label: "Signature name", required: true, rows: 1 },
   ] as const
   ```
   Empty default: every key → `""`.
   ⚠️ **Decision:** Mirror keys/required in the page (Session Resume Paste also keeps client payload shape local). Server remains validation source of truth; React uses this list for labels, required UX, and JSON assembly. Do **not** add a new GET config endpoint in this ticket.
2. **localStorage retention** (`useLocalStorage`): key `session_cover_letter:fields` (`SessionCoverFields`, default all `""`, bound to every input, writes through on change); key `session_cover_letter:last_render` (`{fields, candidate_id} | null`, default `null`, set **only** after a successful Open HTML — 200 + non-empty HTML — **not** cleared on failure). Clearing site data wipes both.
3. **Selected candidate (optional signature only):** `useCandidate().selectedId`; helper line states letter fields come from the form, a selected candidate's profile signature image may be used server-side otherwise name-only, and the tool does not save to the database; Open HTML sets `candidate_id` to `selectedId` when non-empty, else `null`.
4. **UI layout** (clone Session Resume Paste patterns — `dep-btn`, `dep-input`): title `Session Cover Letter`; helper paragraph; one input/textarea per `SESSION_COVER_FIELDS` entry in order (label + ` (optional)` when not required; `rows===1` → `<input>`, else `<textarea>`, `spellCheck={false}` for letter body); **Open HTML** button (disabled when any required field is blank or `opening`); inline error `<p>`; `<Toast>`.
5. **Open HTML handler:** guard incomplete/opening → return; `setOpening(true)`, clear error; body = `{...fields, candidate_id: selectedId?.trim() || null}`; POST; `!r.ok` → parse `data.error`, inline error + Toast error, **no** tab, **no** `last_render` update; ok but empty HTML → error Toast, no tab, no update; on success: `setLastRender({fields: {...fields}, candidate_id: body.candidate_id})`, `URL.createObjectURL` blob → `window.open(blobUrl, "_blank", "noopener,noreferrer")` (null → "Popup blocked" Toast), `setTimeout(revokeObjectURL, 60_000)`; Toast success optional, always Toast on popup-blocked/error; `finally: setOpening(false)`.
6. **Hard rules:** no candidate/job save/parse/artifact API calls; no auto-open on mount or field change — only the Open HTML control; do not merge into `AdminSessionResumePaste.tsx`; do not change the AST-1024 route or builder emit.
7. **Verify by hand:** frontend typecheck on touched TS files; nav label + route load; Open HTML with required fields filled returns a tab; blank required field keeps the button disabled; forced 400 opens no tab.

**Self-Assessment:** Single-Component — Admin nav config + one React route/page with localStorage; no core/data changes. Conf high — direct twin of AST-987 Session Resume Paste UX against a landed AST-1024 HTML contract already merged on `ftr`. Risk Medium — Admin nav/routing surface; a bad Open HTML handler could open empty tabs or confuse users, but Session Resume Paste stays untouched and failures must stay on-page.

##### Comments

###### katherine — 2026-07-29T03:44:55.140Z
Plan @ `f42b582b`. Single-Component — Admin `NAV_CONFIG` + one React route/page with `localStorage`; no core/data changes. Conf high; Risk Medium.

###### joan — 2026-07-29T03:47:34.004Z (plan-rubric.v1)
**Overall: APPROVED.** Stages 1–2 map to parent AC1–6 (AC7 Style D backend debug is AST-1024's boundary). All in-scope statutes **conforms**. **acceptable:** page-local `SESSION_COVER_FIELDS` mirror of `BUILD_CONFIG` keys is an explicit Decision — server remains validation SoT, matches Session Resume Paste's client-shape pattern, no new GET config endpoint; `last_render` is a success snapshot (Open HTML itself uses live form fields — correct for a fields-only tool, unlike resume's `last_parse` which is the Open HTML payload); failure path never opens a tab and treats empty HTML as error (meets AC5); separate Admin nav item matches Boundaries. No `fix-now` / `discuss`.

###### betty — 2026-07-29T03:54:01.382Z
QA manifest AST-1025: nav (Session Cover Letter immediately after Session Resume Paste) + `test_AdminSessionCoverLetter.test.tsx` (§6c — render, Open HTML disabled until required fields, success posts fields + `candidate_id`, 400/empty HTML → error no tab, selected candidate forwards `candidate_id`, localStorage field restore on remount). Publish `@ f3061950` (`merge-tests(AST-1025): origin/tests ab6e07a8`).

###### radia — 2026-07-29T03:56:50.816Z (code-rubric.v1)
**Overall: DISCUSS** (procedural stragglers only). Stages 1–2 match plan: `NAV_CONFIG` + route under `AdminRoute`, page twin of Session Resume Paste; Open HTML failure path never opens a tab, empty HTML treated as error, `last_render` only on success; field/key mirror matches Joan-approved plan; engineer `code()` touched only planned files. All in-scope statutes **conforms**. **discuss (C4 stragglers, 14 statutes):** Joan-excluded at plan time, in-scope on the full three-dot diff (AST-1024 ancestry + features/test-tree) — all substance **conforms** (untouched or process-clean). No **fix-now**.

#### Resolution (2026-07-29)

Radia tip `f7320b88` (docs-only, after product/tests `f3061950`) · DISCUSS. fix-now: none. discuss (C4 stragglers): acknowledged — substance already **conforms**. advisory: none.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Add Admin `NAV_CONFIG` item for Session Cover Letter (after Session Resume Paste) | `ac23db55a` |
| ✓ | `src/ui/frontend/src/routes.tsx` | Register `/admin/session_cover_letter` under `AdminRoute` | `ac23db55a` |
| ✓ | `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | New page: field inputs, Open HTML, Toast, `useLocalStorage` retention, optional `candidate_id` | `ac23db55a` |
| | _tests_ | Admin page (§6c) + nav + retention | `ab6e07a83` — `test_AdminSessionCoverLetter.test.tsx` / `test_config.py` + test-bible (Betty) |
