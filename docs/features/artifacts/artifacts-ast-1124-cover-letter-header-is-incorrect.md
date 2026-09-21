# AST-1124 — Cover Letter Header is incorrect
**Component:** artifacts  
**Children:** AST-1137, AST-1138, AST-1139  
**Linear archived:** AST-1124 2026-08-07; AST-1137 2026-08-07; AST-1138 2026-08-07; AST-1139 2026-08-07

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-02 13:37 | AST-1137 | docs | `22cbb7824` | docs(AST-1137): plan — candidate from-block text + contact defaults |
| 2026-08-02 13:41 | AST-1137 | code | `1abbc6cb8` | code(AST-1137): candidate from-block field + resolve defaults |
| 2026-08-02 13:44 | AST-1137 | merge-tests | `4917e54b1` | merge-tests(AST-1137): origin/tests 494d78b2b |
| 2026-08-02 13:44 | AST-1137 | test | `494d78b2b` | test(AST-1137): cover from-block resolve + config contract coverage |
| 2026-08-02 13:50 | AST-1137 | docs | `2f18e7a8e` | docs(AST-1137): Radia review — findings |
| 2026-08-02 14:17 | AST-1137 | resolve | `4a5e8d826` | resolve(AST-1137): — findings addressed |
| 2026-08-02 14:18 | AST-1137 | merge | `f5c67f2f7` | merge(AST-1137): origin/dev |
| 2026-08-02 14:21 | AST-1138 | docs | `270ab9bdb` | docs(AST-1138): plan — job cover SomersetCover fromBlock + golden CSS |
| 2026-08-02 14:39 | AST-1138 | code | `a2eabbc76` | code(AST-1138): job Print Cover Letter via SomersetCover fromBlock |
| 2026-08-02 14:39 | AST-1138 | docs | `b46d2b3ce` | docs(AST-1138): record build SHA on plan review stub |
| 2026-08-02 14:40 | AST-1138 | docs | `3adf49cdc` | docs(AST-1138): point plan review stub at tip SHA |
| 2026-08-02 14:40 | AST-1139 | docs | `f46f47a14` | docs(AST-1139): plan — session cover letter golden parity |
| 2026-08-02 14:43 | AST-1138 | test | `5427c2795` | test(AST-1138): job Print Cover Letter SomersetCover fromBlock coverage |
| 2026-08-02 14:46 | AST-1139 | code | `67a8d70e0` | code(AST-1139): session from-block empty-resolve config contract |
| 2026-08-02 14:47 | AST-1139 | code | `58ea65e52` | code(AST-1139): Admin Session empty from-block when candidate selected |
| 2026-08-02 14:47 | AST-1139 | docs | `84737c544` | docs(AST-1139): build review stub |
| 2026-08-02 14:47 | AST-1139 | code | `dbfb8a6bb` | code(AST-1139): session empty from-block resolve + Style D source |
| 2026-08-02 14:47 | AST-1139 | docs | `e8385e236` | docs(AST-1139): point build stub at tip SHA |
| 2026-08-02 14:49 | AST-1139 | test | `7ea884701` | test(AST-1139): session empty from-block resolve + Admin gating |
| 2026-08-02 14:49 | AST-1139 | merge-tests | `c2ffe7bad` | merge-tests(AST-1139): origin/tests 7ea884701 |
| 2026-08-02 14:55 | AST-1139 | docs | `33a6a6940` | docs(AST-1139): Radia review — findings |
| 2026-08-02 15:00 | AST-1139 | resolve | `b680cc68c` | resolve(AST-1139): — clean |
| 2026-08-02 15:18 | AST-1124 | prep-uat | `6ce544de2` | prep-uat(AST-1124): rebuild merge ticket log |
| 2026-08-07 18:25 | AST-1137 | docs | `8d578fcbf` | docs(AST-1137): archive Linear issue content |
| 2026-08-07 18:25 | AST-1138 | docs | `8aa51b587` | docs(AST-1138): archive Linear issue content |
| 2026-08-07 18:25 | AST-1139 | docs | `01157a5d2` | docs(AST-1139): archive Linear issue content |
| 2026-08-07 18:28 | AST-1124 | docs | `432300179` | docs(AST-1124): archive Linear issue content |

_AST-1138 shows a second, later set of identically-named `docs`/`code`/`test`/`resolve`/`merge-tests` commits also timestamped 2026-08-02T15:18 (`12f2d5a44` `230877a3b` `67e2edfaa` `6d9880a2d` `d24696913` `d43f71fe6` `f5c5dc166` `f6fa838f7`) — a clean republish of the same sub-branch after a `[merge-child] blocked` finding (its history had picked up a forbidden `Merge remote-tracking branch` commit); not separate work, omitted from the table above._

## Epic — AST-1124
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### Purpose

Cover letter HTML is showing the wrong header treatment — resume-style identity chrome instead of the SomersetCover `fromBlock` header Susan expects for a printed letter. This epic restores the cover-letter header and verifies every cover style block against the golden markup and stylesheet she provided, so Print Cover Letter / cover-letter HTML matches that letter design now. The candidate decides what the from-block reads; the product defaults that text to the expected identity lines when they have not set their own.

### Functional scope

1. **fromBlock header on cover-letter HTML.** Cover-letter-only HTML presents the sender identity as a `fromBlock` (two-line shape in the brief: name + location on the first line, email + phone on the second, with line break between). It must not use the resume document's name/title header and contact strip as the cover letter header.
2. **Candidate-controlled from-block text with defaults.** The candidate decides what the from-block reads. When they have not set their own text, the product defaults to the expected display: `Name • City, ST` then `email • phone` (omit empty segments/lines). Job cover render uses that candidate-owned text; Session Cover Letter may keep its form field but should default from the same candidate text / contact defaults when empty.
3. **Golden stylesheet parity for all cover style blocks.** The embedded cover stylesheet matches the provided rules for every listed block: `body`, `.cover-letter`, `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent` (including paragraphs), `.letterSignoff`, `.signature-img`, `@page` / `@page :first`, and the print media rules. Selectors and declarations match the golden; theme tokens (accent, fonts, text colors, page background) may still come from existing style config where the golden already uses CSS variables.
4. **Both cover-letter HTML surfaces.** Job Print Cover Letter (cover-only HTML) and Admin Session Cover Letter HTML both honor the same fromBlock + stylesheet contract.
5. **Debug on touched backend cover emit.** When `debug=True` on touched cover-letter render paths, log what was found and what was recorded for fromBlock source (candidate text vs default composition) and stylesheet/document path (Style D index headers and `|` detail lines per AST-538 / Code Rules). No debug-logging requirement on React/UI.

### Architectural definition

* **Patterns to reuse:** `pattern.config.config-block` (from-block field contract, defaults, and shared cover golden rules belong in config); `pattern.layers.import-discipline` (config owns the contract; core cover emit applies it; UI edits the candidate field); `pattern.ui.admin-endpoint` (only if an admin/candidate save path is extended, following existing contact-field save patterns).
* **New patterns proposed:** none.
* **Applicable statutes:** `astral.config.config-source-of-truth`; `astral.standards.in-scope-only` (cover-letter HTML + candidate from-block ownership only; do not reopen resume golden CSS); `astral.standards.no-cross-contamination` (do not mix resume header/contact emit into the cover-letter document); `astral.standards.dry-and-focused-functions` (reuse existing session SomersetCover emit where DRY allows); `astral.layers.import-direction`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.debug-contract-gated`; `astral.standards.no-hardcoded-sets`.

### Boundaries

* Does **not** change resume HTML, resume embedded CSS, or Resume Render Format golden work (AST-993 / AST-1019 and children).
* Does **not** own `{$SIGNATURE_IMAGE}` token placement or stopping image-above-signature stacking — that is AST-1123 (sibling epic). This epic may emit `.letterSignoff` / `.signature-img` rules and structure per the golden; token semantics stay on AST-1123.
* Does **not** redesign the cover-letter LLM chain or Manage Tasks prompts beyond what render needs for fromBlock / SomersetCover blocks.
* Does **not** invent a second signature-image storage field — from-block ownership is separate from signature image/text.
* Does **not** break existing job cover field content (Subject / Letter / signature) — those still appear in the letter body/signoff; only header chrome, from-block ownership/defaults, and stylesheet contract change to SomersetCover.

### Acceptance criteria

1. Opening Print Cover Letter (cover-only HTML) for a job with a cover letter shows a `fromBlock` header matching the brief's structure (identity lines with `<br>` between them), not a resume-style centered name/title + contact strip.
2. When the candidate has not set custom from-block text, that header defaults to `Name • City, ST` then `email • phone` from candidate contact (empty segments/lines omitted).
3. When the candidate has set their own from-block text, Print Cover Letter shows that text in `fromBlock` instead of the contact default.
4. The embedded `<style>` on cover-letter HTML includes rules for `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.letterSignoff`, and `.signature-img` that match the provided golden declarations (variable-backed colors/fonts allowed where the golden uses `var(--…)`).
5. Admin Session Cover Letter HTML uses `fromBlock` and matches the same stylesheet contract; empty session from-block input defaults from the candidate-owned text / contact defaults above.
6. Resume Print / session base resume HTML is unchanged by this epic (still resume header/contact, not `fromBlock`).
7. With `debug=True` on a touched cover emit path, debug output includes an index header and `|` detail for fromBlock source (candidate text vs default) and cover document path outcome.

### Dependencies and blockers

none. Related (do not block start): AST-1123 — signature-image token / placement; coordinate so signoff work does not fight this header/CSS golden.

### Open questions

none.

### Proposed child tickets

**1[!]: Candidate from-block text + contact defaults — Ada** — Owns the candidate-controlled from-block: config/field contract, persist + edit on the candidate (alongside existing cover signature contact fields), and default composition `Name • City, ST` / `email • phone` when unset. Does **not** own job SomersetCover document emit or session golden CSS parity.
**Citations:** `pattern.config.config-block`, `pattern.ui.admin-endpoint`, `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`.

**2: Job cover HTML — SomersetCover fromBlock + golden CSS — Hedy** — After #1: cover-only job HTML stops using resume header/contact as the cover header; emits SomersetCover `fromBlock` from candidate-owned text (fallback to defaults); applies the provided stylesheet for all cover style blocks; maps existing Subject / Letter / signature into letter body/signoff without dropping letter text; Style D debug on touched job cover emit. Does **not** own candidate from-block storage/UI, session Admin page, resume HTML, or AST-1123 token semantics.
**Citations:** `pattern.layers.import-discipline`, `astral.standards.in-scope-only`, `astral.standards.no-cross-contamination`, `astral.standards.debug-contract-gated`, `astral.layers.import-direction`, `astral.standards.dry-and-focused-functions`.

**3: Session cover letter golden parity — Katherine** — After #1: Admin Session Cover Letter HTML matches the same fromBlock formatting and stylesheet details as the brief; empty form from-block defaults from candidate-owned text / contact defaults; fix any drift vs job cover SomersetCover. Does **not** own job Print Cover Letter emit or AST-1123.
**Citations:** `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`, `astral.standards.debug-contract-gated`.

### Original brief

The cover letter does not use the fromBlock formatting correctly.

Please verify that ALL style blocks are using the style details provided below.

```
<div class="fromBlock">
        Susan Somerset • Oakland, CA<br>
        hire@susansomerset.com • 415-745-5238
      </div>
```

```
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
```

#### Comments

##### chuckles — 2026-08-02T17:41:47.776Z
@susan

1. For job cover letters (no freeform from-block field): confirm fromBlock line composition should be `Name • City, ST` then `email • phone` from candidate contact, omitting empty segments/lines — or should it use a different contact source / order?

_(Resolved: yes, that composition — captured as the default in Functional scope item 2 / AC2.)_

_(Cursor-chats `[thread-missing]` / `[thread-orphan]` store.db relocation notes and the `[merge-child] blocked` republish note are process narration — the republish itself is in the Ledger footnote above.)_

### Files changed (plan vs actual)

_No product commit trail on the parent — the one `prep-uat(AST-1124)` commit rebuilds the merge ticket log. Implementation landed via the three sub-issues below._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1137 — Candidate from-block text + contact defaults
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1137/candidate-from-block-text-contact-defaults-cover-letter-header-is · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1124_

#### What this implements

Owns the candidate-controlled cover from-block: config field contract, persist + edit on Candidate Profile beside cover signature fields, and a shared resolve helper that returns custom text or the default `Name • City, ST` / `email • phone` composition when unset. Does **not** change job Print Cover Letter HTML emit or session Admin Cover Letter golden CSS (siblings AST-1138 / AST-1139 consume this contract).

#### Acceptance criteria

Parent AC2 (default composition), AC3 (custom text wins), partial AC7 (optional Style D on the resolve helper — emit-path debug remains AST-1138/1139).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `cover_letter_from_block` to `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`; add `COVER_FROM_BLOCK_CONFIG` (field path, separators, contact segment paths, name source); add Candidate Profile textarea beside Cover Letter Signature | utils |
| `src/core/candidate.py` | Add `resolve_cover_from_block(candidate, *, debug=False) -> dict` returning `{"text": str, "source": "candidate"|"default"}` using `COVER_FROM_BLOCK_CONFIG` + name columns + `contact`; optional Style D | core |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | No custom panel required — config-driven textarea via the existing profile field renderer; touch only if a hardcoded field allowlist would hide the new key | ui |

**Out of scope (siblings):** `src/core/builder.py` job/session cover HTML, `AdminSessionCoverLetter.tsx`, job cover CSS golden (AST-1138 / AST-1139).

#### Stage 1: Config contract

**Done when:** `COVER_FROM_BLOCK_CONFIG` and the `UI_CONFIG` profile field declare the from-block key and composition rules; no business logic yet.

Add `cover_letter_from_block` to `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`. Add module-level `COVER_FROM_BLOCK_CONFIG`: `contact_key: "cover_letter_from_block"`; `segment_separator: " • "`; `line_separator: "\n"`; `name_column: "full"` (primary display name; empty → `recompute_full_name(first, last)`); `line_1_contact_paths: ("location",)` (after name, join non-empty stripped segments); `line_2_contact_paths: ("contact_email", "phone")`; `sources: ("candidate", "default")` (allowed `source` values — no hardcoded sets in core). In `UI_CONFIG["detail"]["profile"]`, add a `{"key": "contact.cover_letter_from_block", "label": "Cover letter from-block", "type": "textarea"}` field beside the signature textarea (not required — empty = unset). Do **not** add the key to `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]` (that tuple doesn't list signature keys either). Do **not** change `BUILD_CONFIG["session_cover_letter"]` required `from_block` (session form field stays AST-1139).

⚠️ **Decision:** Field key is `contact.cover_letter_from_block` (not bare `from_block`) so it sits beside `cover_letter_signature*` and cannot be confused with session Admin `from_block` payload keys.

#### Stage 2: Resolve helper (core)

**Done when:** `resolve_cover_from_block` returns custom text or default two-line composition; empty segments/lines omitted; `source` is always one of `COVER_FROM_BLOCK_CONFIG["sources"]`.

`resolve_cover_from_block(candidate, *, debug=False) -> dict`: read `contact` from `candidate["candidate_data"]["contact"]`, or (if the caller passed a token-view shape with top-level `contact` and no `candidate_data`) from top-level `contact` + `first`/`last`/`full` — so job/session emit can pass either a DB row or a token view without a second adapter. Custom path: non-empty `contact[COVER_FROM_BLOCK_CONFIG["contact_key"]]` → `{"text": stripped, "source": "candidate"}` (strip outer whitespace only; preserve internal newlines). Default path: name from `candidate["full"]` or `recompute_full_name(first, last)`; line 1 = name + non-empty `line_1_contact_paths` segments joined by the separator; line 2 = non-empty `line_2_contact_paths` segments; join non-empty lines with `\n`; `{"text": composed, "source": "default"}` (composed may be `""`). `source` values must come from `COVER_FROM_BLOCK_CONFIG["sources"]` — no third source string. When `debug=True`: one Style D index header (identifier = candidate id) with outcome `success — from_block {source}`, then `|` detail lines for `source`, `text_chars`, and which line segments were non-empty on the default path. Does not call builder, write HTML, or mutate `contact`.

⚠️ **Decision:** Resolve lives in `candidate.py` (not `builder.py`) so job/session emit siblings import one contract without pulling cover HTML into the candidate library layer.

#### Stage 3: Profile edit path (UI)

**Done when:** Candidate Profile shows the from-block textarea and `PUT /api/candidates/<id>/data` persists `contact.cover_letter_from_block` via the existing merge save (no new endpoint). If `CandidateProfile.tsx` already renders `UI_CONFIG` profile fields generically, **no frontend code change** — Stage 1 config is sufficient; only extend a hardcoded skip-list if one exists. No new API validation (plain optional string; no JPEG-style checks) — `save_candidate_data` merge already persists arbitrary contact keys.

**Contract for siblings (non-goal for this ticket):** AST-1138 / AST-1139 **must** call `resolve_cover_from_block` when filling SomersetCover `fromBlock` / empty session from-block defaults. This ticket only guarantees the field + helper.

**Self-Assessment:** Single-Component — utils config + one core resolve helper + config-driven profile field; no builder/HTML emit. Conf high — mirrors the `cover_letter_signature` profile + library key pattern. Risk low — additive optional contact field; empty default is backward-compatible; job/session render unchanged until siblings wire the helper.

##### Comments

###### ada — 2026-08-02T20:37:28.843Z
Plan @ `22cbb782`. Single-Component — utils config + `resolve_cover_from_block` + config-driven profile textarea; no builder/HTML emit. Conf high; Risk low.

###### joan — 2026-08-02T20:39:51.953Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 config contract → child #1 field; Stage 2 resolve helper → defaults + custom-vs-default source for sibling emit; Stage 3 profile edit path → persist + edit beside cover signature. All in-scope statutes **conforms**. No `fix-now`.

###### betty — 2026-08-02T20:45:05.384Z
QA manifest AST-1137: from-block resolve + config contract coverage in `test_candidate.py` / `test_config.py`. Publish `@ 4917e54b` (`merge-tests(AST-1137): origin/tests 494d78b2`).

###### radia — 2026-08-02T20:51:10.863Z (code-rubric.v1)
**Overall: FIX-NOW.** Stages 1–3 match the plan and Self-Assessment Single-Component footprint: utils config + `resolve_cover_from_block` + config-driven profile textarea; no builder/HTML or session golden CSS (siblings AST-1138/1139); cross-ticket boundary held. **fix-now** (`astral.standards.debug-contract-gated` / §5f): `resolve_cover_from_block` (`src/core/candidate.py`) calls `logger.debug_index` / `debug_detail` under `if debug:` but never calls `logger.set_debug_flag(debug)` first. The module logger defaults `_debug_flag=False`, so the Style D helpers early-return even when callers pass `debug=True` — sibling emit paths (AST-1138/1139) would get silent debug. Fix: set the flag at function entry (same pattern as `save_candidate_data` / `get_candidate_id_for_query` in this module). **advisory:** `COVER_FROM_BLOCK_CONFIG["name_column"]` is declared but resolve hardcodes `candidate.get("full")` per the plan Stage 2 literal — AC-correct; optional later config read for true symmetry.

#### Resolution (2026-08-02, resolve-child)

**fix-now addressed:** `resolve_cover_from_block` now calls `logger.set_debug_flag(debug)` at entry (same pattern as `save_candidate_data`), so Style D `debug_index` / `debug_detail` emit when callers pass `debug=True`.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `COVER_FROM_BLOCK_CONFIG` + `contact.cover_letter_from_block` library/UI field | `1abbc6cb8` |
| ✓ | `src/core/candidate.py` | `resolve_cover_from_block` — custom text or default composition; `set_debug_flag` fix | `1abbc6cb8` (+ `4a5e8d826` fix-now) |
| | _tests_ | resolve + config contract coverage | `494d78b2b` — `test_candidate.py` / `test_config.py` + test-bible (Betty) |

### AST-1138 — Job cover HTML — SomersetCover fromBlock + golden CSS
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1138/job-cover-html-somersetcover-fromblock-golden-css-cover-letter-header · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1124_

#### What this implements

After AST-1137: Print Cover Letter (cover-only job HTML via `build_cover_letter` / `build_cover_letter_from_job`) stops using the resume document header/contact strip; emits SomersetCover `fromBlock` from `resolve_cover_from_block`; reuses the existing SomersetCover stylesheet/DOM (session emit) for all cover style blocks; maps job Subject / Letter / signature into letter subject/body/signoff without dropping letter text; Style D debug on the touched job cover emit path. Does **not** own candidate from-block storage/UI, session Admin page defaults/CSS parity (AST-1139), resume HTML, or AST-1123 token semantics.

#### Acceptance criteria

Parent AC1 (fromBlock header on Print Cover Letter), AC2/AC3 (default vs custom text, via AST-1137 resolve), AC4 (golden stylesheet), AC6 (resume HTML unchanged), AC7 (Style D debug).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["job_cover_somerset"]` — document title reuse + which session field keys job artifacts map into; optional empty-string defaults for fields job artifacts don't store (`letter_date`, `to_block`, `signoff_closing`) | utils |
| `src/core/builder.py` | Rename/generalize the session SomersetCover HTML helper for shared job+session use; add job→Somerset field mapper; rewrite `build_cover_letter_from_job` to call `resolve_cover_from_block` + shared SomersetCover emit (no resume `_emit_html_document` for cover-only); Style D debug for fromBlock source + document path | core |

**Out of scope (siblings):** `CandidateProfile.tsx` / `COVER_FROM_BLOCK_CONFIG` / `resolve_cover_from_block` implementation (AST-1137 — consume only); `AdminSessionCoverLetter.tsx` / session empty-form defaults (AST-1139); `build_resume` / `build_base_resume` / `_emit_html_document` resume header+contact path; AST-1123 token literal/policy changes; `tests/`, bible.

#### Stage 1: Config — job Somerset field map

**Done when:** `BUILD_CONFIG["job_cover_somerset"]` declares document title and the mapping from normalized job cover keys (`re_line`/`body`/`signature`) to Somerset session field keys.

```python
"job_cover_somerset": {
    "document_title_key": "session_cover_letter",  # reuse BUILD_CONFIG[…]["document_title"]
    "artifact_to_fields": {"re_line": "subject", "body": "letter", "signature": "signature"},
    "unset_fields": ("from_block", "letter_date", "to_block", "signoff_closing"),
},
```
`from_block` is listed under `unset_fields` as the **artifact** default (filled at emit from `resolve_cover_from_block`, not from the job artifact). No golden CSS duplicated into config — CSS stays in the shared emit helper.

⚠️ **Decision:** Job artifacts stay `Subject`/`Letter`/`signature` (normalize via existing `_cover_letter_fields_for_read`). Layout-only session keys (`letter_date`, `to_block`, `signoff_closing`) are empty on the job path; empty `letter_date` still emits the `.letterdate` div (same as session with a blank date) so the stylesheet selector stays exercised without inventing a date.

#### Stage 2: Share SomersetCover emit (DRY)

**Done when:** Session and job cover-only HTML both call one SomersetCover document helper; session public API behavior unchanged; helper docstring no longer claims "session-only".

Rename `_emit_session_cover_html_document` → `_emit_somerset_cover_html_document`; accept optional `document_title` (default: read from `BUILD_CONFIG["session_cover_letter"]["document_title"]`; job path overrides via `job_cover_somerset["document_title_key"]` — same string today, `SomersetCover`). Keep CSS/DOM exactly as today (the full golden rule set); only align a literal drift found while reading the helper, matching the parent Description golden. Point `build_session_cover_letter` at the renamed helper (behavior-identical). Keep `_session_cover_letter_paragraphs` name.

⚠️ **Decision:** Rename + thin title override beats copying the ~200-line CSS/DOM into a second job-only emitter (`astral.standards.dry-and-focused-functions`). AST-1139 can still tune session defaults without forking job CSS.

#### Stage 3: Job cover-only → SomersetCover + fromBlock

**Done when:** `build_cover_letter_from_job` returns SomersetCover HTML with `fromBlock` from the AST-1137 resolve; Subject/Letter/signature mapped; no resume `h1`/`.contact` chrome; resume builders untouched.

Add `_job_cover_somerset_fields(cover, from_block_text)` (builds the full `session_cover_letter` field dict, defaulting `unset_fields` to `""`, then `from_block` from the argument, then mapping `artifact_to_fields`). Add `_candidate_for_cover_from_block(cd)` (maps `_full`/`_first`/`_last` → `full`/`first`/`last`, passes through `contact`, copies the candidate id). Rewrite `build_cover_letter_from_job`'s success path: **remove** the `_apply_contact_to_render_dict` / `_apply_resume_text_markers` / `_merge_effective_style` / `_emit_html_document(..., include_cover=True, body_section_ids=[])` path; call `resolve_cover_from_block(_candidate_for_cover_from_block(cd), debug=debug)`, resolve the signature image the same way the session path does, build `fields` via `_job_cover_somerset_fields`, then `_emit_somerset_cover_html_document(fields, signature_image_src=sig_src, document_title=…)`. Preserve the existing `ValueError` when there is no cover content. Do **not** change `build_cover_letter`'s load/orchestration beyond still returning `build_cover_letter_from_job(...)`. Do **not** touch `build_resume` / `_emit_html_document` / `_emit_cover_sections_html` — materials resume+cover embed and Resume Print stay on the resume stylesheet; cover-only Print Cover Letter (`/candidate/cover/<job_id>`) is the sole consumer of this rewrite. Signature-image token replace stays inside the shared emit helper (AST-1126 session path) — do not reintroduce auto-image-above-name.

⚠️ **Decision:** Cover-only leaves the legacy `_emit_cover_sections_html` path for `build_resume` materials embed so Resume Print AC stays green without expanding into AST-1139/resume work. Parent AC #1 targets Print Cover Letter only.

#### Stage 4: Style D debug on job cover emit

**Done when:** `debug=True` on `build_cover_letter_from_job` emits one index header + `|` details for fromBlock source and cover document path; no new debug when `debug=False`.

Keep `func="builder.build_cover_letter_from_job"`; index outcome `success — somerset cover html`; `|` details: `from_block_source={source}` (must be `candidate`/`default`), `from_block_chars`, `document_path=somerset_cover` (literal distinguishing from the old resume-shell path), `cover_source`, field-presence bools for subject/letter/signature; keep existing signature image token/status lines and `html_chars`/preview. `resolve_cover_from_block(..., debug=debug)` may also emit its own index — acceptable; the builder index must still log fromBlock source so cover-path debugging is scannable without reading candidate logs alone. No React/UI debug.

**Self-Assessment:** Single-Component — config map + `builder.py` cover-only emit rewrite reusing the session SomersetCover helper; no UI. Conf high — AST-1137 resolve + AST-1024 SomersetCover emit already exist; this ticket is wiring and field mapping. Risk Medium — Print Cover Letter is user-visible; wrong mapping could drop Letter body or keep resume chrome, mitigated by reusing the battle-tested session emitter and leaving resume paths untouched.

##### Comments

###### hedy — 2026-08-02T21:22:02.228Z
Plan. Single-Component — config map + `builder.py` cover-only emit rewrite reusing session SomersetCover helper; no UI. Conf high; Risk Medium.

###### joan — 2026-08-02T21:24:03.118Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 config → child #2 field map; Stage 2 share SomersetCover emit → DRY reuse; Stage 3 job cover-only → fromBlock → AC1–3 emit side + no-cross-contamination; Stage 4 Style D → AC7. All in-scope statutes **conforms**. No `fix-now`.

###### betty — 2026-08-02T21:44:12.409Z
QA manifest AST-1138: job Print Cover Letter SomersetCover fromBlock coverage in `test_builder.py`. Publish `@ f5c5dc16` (`merge-tests(AST-1138): origin/tests 5427c279`).

###### radia — 2026-08-02T21:57:51.270Z (code-rubric.v1)
**Overall: DISCUSS.** Stages 1–4 match the plan: `job_cover_somerset` config map; `_emit_somerset_cover_html_document` rename + title override; `_candidate_for_cover_from_block` / `_job_cover_somerset_fields`; `build_cover_letter_from_job` uses `resolve_cover_from_block` + SomersetCover (no resume `_emit_html_document` shell); Style D with `set_debug_flag`, `from_block_source`, `document_path=somerset_cover`. Golden selectors present on the shared helper; `build_resume` / `_emit_html_document` retained for resume; session call site updated to the renamed helper; no second CSS fork; one `merge-tests(AST-1138)` (helpers landed in a follow-up `code(AST-1138)` before tests). No `fix-now` product finding beyond the usual C4 stragglers.

#### Resolution (2026-08-02)

DISCUSS, no fix-now. Publish tip at review: `ef7e0776`.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `BUILD_CONFIG["job_cover_somerset"]` artifact→Somerset field map | `a2eabbc76` |
| ✓ | `src/core/builder.py` | Shared `_emit_somerset_cover_html_document`; `build_cover_letter_from_job` → resolve fromBlock + SomersetCover (no resume shell); Style D | `a2eabbc76` |
| | _tests_ | job Print Cover Letter SomersetCover fromBlock coverage | `5427c2795` — `test_builder.py` + test-bible (Betty) |

### AST-1139 — Session cover letter golden parity
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1139/session-cover-letter-golden-parity-cover-letter-header-is-incorrect · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1124_

#### What this implements

After AST-1137: Admin Session Cover Letter HTML keeps SomersetCover `fromBlock` + the golden stylesheet contract; empty form `from_block` defaults via `resolve_cover_from_block` (candidate-owned text / contact defaults); UI allows Open HTML with empty from-block when a candidate is selected; Style D debug records fromBlock source + document path. Does **not** own job Print Cover Letter emit (AST-1138), candidate from-block storage/UI (AST-1137), or AST-1123 signature-image token semantics.

#### Acceptance criteria

Parent AC2/AC3 (default vs custom from-block on the session path), AC4 (golden stylesheet selectors), AC5 (empty session from-block defaulting), AC7 (Style D debug).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `BUILD_CONFIG["session_cover_letter"]["fields"]["from_block"]` gains `"empty_uses_candidate_resolve": True` (keep `"required": True"`); add `"from_block_sources": ("session", "candidate", "default")` on the block | utils |
| `src/core/builder.py` | `build_session_cover_letter`: load candidate before the from-block required check; when form `from_block` is empty and a candidate is present, fill from `resolve_cover_from_block`; track fromBlock source for Style D; call the shared SomersetCover emit helper; CSS drift fix only if listed golden declarations differ | core |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | Treat `from_block` as not blocking Open HTML when a candidate is selected; update help copy for empty-from-block defaults | ui |

**Out of scope (siblings):** `resolve_cover_from_block` / `COVER_FROM_BLOCK_CONFIG` / Candidate Profile from-block field (AST-1137 — consume only); `build_cover_letter_from_job` / job Print Cover Letter path (AST-1138); AST-1123 token policy; resume HTML / `_emit_html_document` resume header; `tests/`, bible; no new admin HTML route.

#### Stage 1: Config — session from-block defaulting contract

**Done when:** `session_cover_letter` declares that empty form `from_block` may resolve from the candidate, and names the allowed builder-level fromBlock source strings.

`from_block` field entry becomes `{"required": True, "empty_uses_candidate_resolve": True}`; sibling `"from_block_sources": ("session", "candidate", "default")` added on the same block (`session` = non-empty form text used as-is; `candidate`/`default` = `resolve_cover_from_block` outputs, matching `COVER_FROM_BLOCK_CONFIG["sources"]`). No other `required` flags change; no job config here (AST-1138); no new API route.

⚠️ **Decision:** Keep `required: True` so emitted HTML still expects a from-block after defaulting; `empty_uses_candidate_resolve` is the explicit gate for empty form + candidate (config source of truth — no bare `if key == "from_block"` policy without this flag).

#### Stage 2: Builder — empty from-block → resolve + debug + CSS parity

**Done when:** Empty session `from_block` with a valid `candidate_id` emits SomersetCover HTML using `resolve_cover_from_block` text; non-empty form text wins; no candidate + empty from-block still 400s; Style D logs fromBlock source + `document_path=somerset_cover`; listed CSS selectors match the parent golden declarations.

1. **Shared emit helper name (ftr-aware):** after merging `ftr`, call `_emit_somerset_cover_html_document` if AST-1138 already landed it; otherwise keep calling `_emit_session_cover_html_document` (rename stays AST-1138's).
2. **Empty from-block defaulting:** resolve/load the candidate **before** required checks when `candidate_id` is non-empty. While iterating `field_defs` to build `normalized`: for `from_block`, non-empty raw → `normalized["from_block"] = raw` (preserve internal newlines), `from_block_source = "session"`; else if `empty_uses_candidate_resolve` and a candidate was loaded → shape via `_candidate_for_cover_from_block` (add if AST-1138 hasn't landed it — identical contract), call `resolve_cover_from_block`, `normalized["from_block"] = from_res["text"]`, `from_block_source = from_res["source"]` (do **not** raise required for an empty resolve — composition may legitimately be blank); else (empty form, no candidate) → existing required failure. Every other field keeps its existing required/assign behavior.
3. **Style D** (`debug=True`) on the success index: keep existing field/candidate/signature detail lines; add `from_block_source`, `from_block_chars`, `document_path=somerset_cover`. No new debug when `debug=False`.
4. **Golden CSS parity:** verify the session SomersetCover helper's rules for `body`, `.cover-letter`, `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent` (+ `p` / `p:last-child`), `.letterSignoff`, `.signature-img`, `@page` / `@page :first`, `@media print` against the parent golden — every listed declaration must be present with the same value (CSS variables allowed where golden uses `var(--…)`); as of `ftr` + AST-1137 the listed rules already matched. Edit **only** the drifting declaration in the helper's CSS string if any is found; do not touch resume `_emit_html_document` CSS or DOM structure for AST-1123 token placement.

⚠️ **Decision:** Form non-empty text is source `session` and does **not** write through to `contact.cover_letter_from_block` (Admin tool still does not persist). Empty form + candidate uses AST-1137 resolve only.

#### Stage 3: Admin Session UI — empty from-block when candidate selected

**Done when:** With a candidate selected, Open HTML is enabled even if From block is blank; without a candidate, From block remains required in the UI; help text states empty from-block uses candidate defaults.

`requiredComplete` treats `from_block` as satisfied when the field is non-empty **or** `selectedId` is non-empty; all other required fields keep the existing nonempty check. Help copy states: with a candidate selected, an empty From block uses that candidate's cover from-block text or the contact default; without a candidate, it's required (keep "does not save to the database"). Do **not** compose defaults in React; do **not** add a new API; `SESSION_COVER_FIELDS` keys/labels unchanged beyond copy.

**Self-Assessment:** Single-Component — session cover config flag + `build_session_cover_letter` defaulting/debug + Admin Session form gating; no job cover emit rewrite. Conf high — `resolve_cover_from_block` is on `ftr`; the session emitter and Admin form already exist; this ticket wires empty-form defaults and a CSS parity check. Risk Medium — Admin Session Cover Letter is user-visible; wrong required gating could block Open HTML or emit empty headers, mitigated by keeping the no-candidate required path and reusing the shared resolve helper.

##### Comments

###### katherine — 2026-08-02T21:40:42.434Z
Plan @ `f46f47a1`. Single-Component — session cover config flag + builder defaulting/debug + Admin form gating; no job cover rewrite. Conf high; Risk Medium. _(Noted for Chuckles: this publish tip briefly carried AST-1138 product commits because the epic worktree was on the sibling sub when the plan commit landed — the plan file itself was correct at the tip; resolved by the time of merge-child.)_

###### joan — 2026-08-02T21:43:29.839Z (plan-rubric.v1)
**Overall: APPROVED.** Stage 1 config → empty-uses-candidate-resolve contract; Stage 2 builder defaulting + CSS + debug → AC5/AC4/AC7, DRY reuse of AST-1137/1138 helpers; Stage 3 Admin UI → empty-form UX (composition stays in core). All in-scope statutes **conforms**. **advisory:** frontend `requiredComplete` hardcodes `from_block` + the candidate-selected exception per the plan Stage 3 literal (does not read `empty_uses_candidate_resolve` from a server payload) — accepted, matches the plan (no server payload exists for that flag).

###### betty — 2026-08-02T21:50:04.887Z
QA manifest AST-1139: empty-from-block resolve + Admin gating coverage in `test_builder.py` / frontend page test. Publish `@ c2ffe7ba` (`merge-tests(AST-1139): origin/tests 7ea88470`).

###### radia — 2026-08-02T21:55:27.767Z (code-rubric.v1)
**Overall: DISCUSS.** Self-Assessment Single-Component matches session config + builder defaulting/debug + Admin gating; job Print Cover Letter rewrite not introduced as new scope beyond repairing shared helpers already called from the `ftr` tip; CSS parity satisfied by the existing SomersetCover helper rules. **discuss** — AST-1138 shared helper completion appears on this tip: accepted as merge hygiene (helpers match plan Stage 2; AST-1138 retains job emit ownership on its own sub). **advisory:** UI hardcodes the `from_block` empty+candidate gate (matches plan Stage 3 — no server payload for `empty_uses_candidate_resolve`). No `fix-now`.

#### Resolution (2026-08-02)

Radia overall DISCUSS (`33a6a694`) — no fix-now. discuss (AST-1138 shared-helper completion on this tip): accepted as merge hygiene. advisory (UI hardcodes the empty+candidate gate): accepted, matches plan.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | `from_block` gains `empty_uses_candidate_resolve`; `from_block_sources` tuple | `67a8d70e0` |
| ✓ | `src/core/builder.py` | Empty from-block → `resolve_cover_from_block`; Style D `from_block_source` / `document_path`; CSS parity | `dbfb8a6bb` |
| ✓ | `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | `requiredComplete` allows empty `from_block` when a candidate is selected; help copy updated | `58ea65e52` |
| | _tests_ | empty from-block resolve + Admin gating coverage | `7ea884701` — `test_builder.py` + frontend page test + test-bible (Betty) |
