# AST-1124 — Cover Letter Header is incorrect

<!-- linear-archive: AST-1124 archived 2026-08-07 -->

## Linear archive (AST-1124)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Cover letter HTML is showing the wrong header treatment — resume-style identity chrome instead of the SomersetCover `fromBlock` header Susan expects for a printed letter. This epic restores the cover-letter header and verifies every cover style block against the golden markup and stylesheet she provided, so Print Cover Letter / cover-letter HTML matches that letter design now. The candidate decides what the from-block reads; the product defaults that text to the expected identity lines when they have not set their own.

## Functional scope

1. **fromBlock header on cover-letter HTML.** Cover-letter-only HTML presents the sender identity as a `fromBlock` (two-line shape in the brief: name + location on the first line, email + phone on the second, with line break between). It must not use the resume document’s name/title header and contact strip as the cover letter header.
2. **Candidate-controlled from-block text with defaults.** The candidate decides what the from-block reads. When they have not set their own text, the product defaults to the expected display: `Name • City, ST` then `email • phone` (omit empty segments/lines). Job cover render uses that candidate-owned text; Session Cover Letter may keep its form field but should default from the same candidate text / contact defaults when empty.
3. **Golden stylesheet parity for all cover style blocks.** The embedded cover stylesheet matches the provided rules for every listed block: `body`, `.cover-letter`, `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent` (including paragraphs), `.letterSignoff`, `.signature-img`, `@page` / `@page :first`, and the print media rules. Selectors and declarations match the golden; theme tokens (accent, fonts, text colors, page background) may still come from existing style config where the golden already uses CSS variables.
4. **Both cover-letter HTML surfaces.** Job Print Cover Letter (cover-only HTML) and Admin Session Cover Letter HTML both honor the same fromBlock + stylesheet contract.
5. **Debug on touched backend cover emit.** When `debug=True` on touched cover-letter render paths, log what was found and what was recorded for fromBlock source (candidate text vs default composition) and stylesheet/document path (Style D index headers and `|` detail lines per AST-538 / Code Rules). No debug-logging requirement on React/UI.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — from-block field contract, defaults, and shared cover golden rules belong in config, not scattered literals.
  * `pattern.layers.import-discipline` — config owns the contract; core cover emit applies it; UI edits the candidate field; no layer inversion.
  * `pattern.ui.admin-endpoint` — only if an admin/candidate save path is extended for the editable from-block; follow existing contact-field save patterns.
* **New patterns proposed** — none (candidate-owned cover header text + golden cover HTML parity; no new catalog shape).
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — from-block field and cover style contract live in config.
  * `astral.standards.in-scope-only` — cover-letter HTML + candidate from-block ownership only; do not reopen resume golden CSS.
  * `astral.standards.no-cross-contamination` — do not mix resume header/contact emit into cover-letter SomersetCover document.
  * `astral.standards.dry-and-focused-functions` — reuse existing session SomersetCover emit where DRY allows; do not fork a third letter renderer without cause.
  * `astral.layers.import-direction` — utils ↔ core ↔ ui direction preserved.
  * `astral.layers.ui-config-driven-business-logic` — any candidate edit UI for from-block is config-driven like other contact fields.
  * `astral.standards.debug-contract-gated` — Style D debug only when `debug=True` on touched backend paths.
  * `astral.standards.no-hardcoded-sets` — no ad-hoc cover field/style sets outside config.

## Boundaries

* Does **not** change resume HTML, resume embedded CSS, or Resume Render Format golden work ([AST-993](https://linear.app/astralcareermatch/issue/AST-993/resume-render-format-discrepancies) / [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) and children).
* Does **not** own `{$SIGNATURE_IMAGE}` token placement or stopping image-above-signature stacking — that is [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter) (sibling). This epic may emit `.letterSignoff` / `.signature-img` rules and structure per the golden; token semantics stay on [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter).
* Does **not** redesign the cover-letter LLM chain or Manage Tasks prompts beyond what render needs for fromBlock / SomersetCover blocks.
* Does **not** invent a second signature-image storage field — from-block ownership is separate from signature image/text.
* Does **not** break existing job cover field content (Subject / Letter / signature) — those still appear in the letter body/signoff; only header chrome, from-block ownership/defaults, and stylesheet contract change to SomersetCover.

## Acceptance criteria

1. Opening Print Cover Letter (cover-only HTML) for a job with a cover letter shows a `fromBlock` header matching the brief’s structure (identity lines with `<br>` between them), not a resume-style centered name/title + contact strip.
2. When the candidate has not set custom from-block text, that header defaults to `Name • City, ST` then `email • phone` from candidate contact (empty segments/lines omitted).
3. When the candidate has set their own from-block text, Print Cover Letter shows that text in `fromBlock` instead of the contact default.
4. The embedded `<style>` on cover-letter HTML includes rules for `.fromBlock`, `.toBlock`, `.letterdate`, `.lettersubject`, `.lettercontent`, `.letterSignoff`, and `.signature-img` that match the provided golden declarations (variable-backed colors/fonts allowed where the golden uses `var(--…)`).
5. Admin Session Cover Letter HTML uses `fromBlock` and matches the same stylesheet contract; empty session from-block input defaults from the candidate-owned text / contact defaults above.
6. Resume Print / session base resume HTML is unchanged by this epic (still resume header/contact, not `fromBlock`).
7. With `debug=True` on a touched cover emit path, debug output includes an index header and `|` detail for fromBlock source (candidate text vs default) and cover document path outcome.

## Dependencies and blockers

none.

Related (do not block start): [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter) — signature-image token / placement; coordinate so signoff work does not fight this header/CSS golden.

## Open questions

none.

## Proposed child tickets

#### 1!: **Candidate from-block text + contact defaults - Ada**

Owns the candidate-controlled from-block: config/field contract, persist + edit on the candidate (alongside existing cover signature contact fields), and default composition `Name • City, ST` / `email • phone` when unset. Does **not** own job SomersetCover document emit or session golden CSS parity. **Citations:** `pattern.config.config-block`, `pattern.ui.admin-endpoint`, `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`.

#### 2: **Job cover HTML — SomersetCover fromBlock + golden CSS - Hedy**

After #1: cover-only job HTML stops using resume header/contact as the cover header; emits SomersetCover `fromBlock` from candidate-owned text (fallback to defaults); applies the provided stylesheet for all cover style blocks; maps existing Subject / Letter / signature into letter body/signoff without dropping letter text; Style D debug on touched job cover emit. Does **not** own candidate from-block storage/UI, session Admin page, resume HTML, or [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter) token semantics. **Citations:** `pattern.layers.import-discipline`, `astral.standards.in-scope-only`, `astral.standards.no-cross-contamination`, `astral.standards.debug-contract-gated`, `astral.layers.import-direction`, `astral.standards.dry-and-focused-functions`.

#### 3: **Session cover letter golden parity - Katherine**

After #1: Admin Session Cover Letter HTML matches the same fromBlock formatting and stylesheet details as the brief; empty form from-block defaults from candidate-owned text / contact defaults; fix any drift vs job cover SomersetCover. Does **not** own job Print Cover Letter emit or [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter). **Citations:** `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`, `astral.standards.debug-contract-gated`.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1124 (parent) | ftr/AST-1124-cover-letter-header-is-incorrect |
| AST-1137 | sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults |
| AST-1138 | sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css |
| AST-1139 | sub/AST-1124/AST-1139-session-cover-letter-golden-parity |

**Epic worktree:** `astral-AST-1124/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/f7ffac3298a0695c4cb085be242377e5/3ad606b1-f5ad-4a31-bab2-ab5c37ab961f/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/f7ffac3298a0695c4cb085be242377e5/2c92dbce-c78d-41b0-b92f-482bc6e02321/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/f7ffac3298a0695c4cb085be242377e5/b1e9e136-1f23-45da-bb45-6aea5e3eddda/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/c3f11b73-c9b4-4d23-8f5c-e7834053c751/store.db` |
| Radia | review | `/home/susan/.cursor/chats/f7ffac3298a0695c4cb085be242377e5/bde6a1ba-e392-4032-acca-858f01eadff5/store.db` |

---

## Original brief

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

### Comments

#### chuckles — 2026-08-02T22:16:35.353Z
[merge-child] blocked: AST-1138 sub has `Merge remote-tracking branch` (validate-sub-log). @Hedy Lamarr to republish clean sub; AST-1137 + AST-1139 already on ftr. Chuckles keeps assignee until merge-child/prep-uat clean.

— Chuckles

#### chuckles — 2026-08-02T21:36:13.216Z
[thread-orphan] Hedy engineer Team UUID 3a2ce597-90fd-456c-9f6c-2eae470eb30b was reused as Chuckles sub-chuck drone session for AST-1138 (collision). Reminted Hedy Team → 2c92dbce-c78d-41b0-b92f-482bc6e02321 (`## Team` updated). Build-child continues on new UUID.

— Chuckles

#### chuckles — 2026-08-02T21:19:54.772Z
[thread-missing] Hedy engineer Team chat store.db missing on this host for prior UUID 331c643b-c37d-4d6b-a37b-64349cb46fa0. Minted new Team thread 56ef91f3-44ea-4d65-83d8-97770947ea35 → /home/susan/.cursor/chats/f7ffac3298a0695c4cb085be242377e5/56ef91f3-44ea-4d65-83d8-97770947ea35/store.db. ## Team updated via populate-team.

— Chuckles

#### chuckles — 2026-08-02T20:35:51.313Z
[thread-missing] Team chat store.db missing on this host for prior Ada/Katherine/Hedy/Betty/Radia Thread paths — reminted/relocated via populate-team. Ada → `b1e9e136-1f23-45da-bb45-6aea5e3eddda`.

— Chuckles

#### chuckles — 2026-08-02T17:41:47.776Z
@susan

1. For job cover letters (no freeform from-block field): confirm fromBlock line composition should be `Name • City, ST` then `email • phone` from candidate contact, omitting empty segments/lines — or should it use a different contact source / order?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
