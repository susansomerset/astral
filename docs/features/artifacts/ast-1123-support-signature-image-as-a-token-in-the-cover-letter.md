# AST-1123 — Support Signature_Image as a token in the cover letter

<!-- linear-archive: AST-1123 archived 2026-08-07 -->

## Linear archive (AST-1123)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Cover letters currently stack the candidate’s signature image *above* the entire signature block, so the handwritten image sits before the closing (“Sincerely,”) and the name/title. Susan needs cover-letter HTML render to place that image where a letter actually signs — between the closing and the candidate’s name and title — by supporting a cover-only `{$SIGNATURE_IMAGE}` token that resolves to the stored signature image. Resume and other surfaces stay untouched.

## Functional scope

1. **Cover-only token.** When rendering a cover letter, `{$SIGNATURE_IMAGE}` is replaced with the candidate’s validated signature image. The token is not honored on resume HTML or any non-cover render path.
2. **No auto-stack above signature text.** Cover letter HTML must not place the signature image above the signature text block as a separate unconditional prepend. Once the token path is live, the image appears only where the token is resolved (or not at all if there is no image / rejected image).
3. **Correct visual order.** With a normal signature text shape (closing, then name and title), resolving the token between those parts yields: closing → signature image → candidate name and title. The image must not sit above the closing.
4. **Safe image only.** Replacement uses the same acceptance rules already used for cover signature images (rejected or missing values produce no image element; no unsafe `src`).
5. **Debug on cover render.** When `debug=True` on touched cover-letter render paths, log what was found and what was recorded for the token/image step (token present or absent; image accepted, absent, or rejected; outcome), using Style D index headers and `|` detail lines per the AST-538 / Code Rules debug contract.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — token name and cover-only resolution contract belong in config, not scattered literals.
  * `pattern.layers.import-discipline` — config owns the contract; core cover emit performs replacement; no layer inversion.
* **New patterns proposed** — none (single cover-render token/placement fix; no new reusable catalog shape).
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — token and cover-render rules live in config.
  * `astral.standards.no-hardcoded-sets` — no ad-hoc token name sets outside config.
  * `astral.standards.in-scope-only` — cover letter render only; do not expand into resume or unrelated profile UI.
  * `astral.standards.no-cross-contamination` — keep cover emit changes isolated from resume emit.
  * `astral.layers.import-direction` — utils ↔ core direction preserved.
  * `astral.standards.debug-contract-gated` — Style D debug only when `debug=True` on touched backend cover paths.
  * `astral.standards.dry-and-focused-functions` — reuse existing safe-image validation; do not fork a second validator.

## Boundaries

* Does **not** change Candidate Profile upload/validation UI for the signature image (JPEG limits and storage stay as today).
* Does **not** add signature-image tokens to resume HTML, job resume, or session base resume.
* Does **not** redesign cover letter field shape (Subject / Letter / signature) or the cover-letter daisy chain beyond what is required for token placement at render.
* Does **not** invent a new signature-image storage field — uses the existing candidate contact signature image.
* Does **not** break existing `{$COVER_LETTER_SIGNATURE}` text injection for signature prose.
* **Resolved (was OQ1):** no `{$SIGNATURE_IMAGE}` token in cover signature content → **omit** the image (no fallback auto-insert between closing and name).
* **Resolved (was OQ2):** remove the image’s current default placement on cover render paths (including Admin Session Cover Letter auto-inject) and rely **only** on `{$SIGNATURE_IMAGE}` in cover letter signature content.

## Acceptance criteria

1. Rendering a job cover letter whose signature text contains `{$SIGNATURE_IMAGE}` between the closing and the name/title shows the signature image in that position — not above the closing.
2. The literal token string `{$SIGNATURE_IMAGE}` does not appear in the rendered cover HTML when a valid image is available.
3. When the candidate has no usable signature image, cover render does not emit a signature `<img>`, and the layout does not leave a broken image placeholder.
4. Cover letter HTML no longer places the signature image above the full signature text block as an unconditional prepend.
5. Resume (base / job / session) HTML render paths do not resolve or display `{$SIGNATURE_IMAGE}` as an image.
6. With `debug=True` on a touched cover render path, debug output includes an index header and `|` detail for token presence and image accepted / absent / rejected.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **Cover-letter SIGNATURE_IMAGE token contract - Ada**

Owns the config-side contract: register `{$SIGNATURE_IMAGE}` for cover-letter render resolution (cover-only; not a general LLM prompt binary injection), tied to the existing candidate signature-image source. Does **not** own HTML emit placement. **Citations:** `pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`.

#### 2: **Cover HTML emit — token replace and stop auto-above - Hedy**

After #1: cover HTML emit (job + session) stops unconditional/default image placement; replaces `{$SIGNATURE_IMAGE}` with a safe image at the token position only; if the token is absent, omit the image (no fallback insert); Style D debug on touched cover paths. Does **not** own profile upload UI or resume emit. **Citations:** `astral.standards.in-scope-only`, `astral.standards.no-cross-contamination`, `astral.standards.debug-contract-gated`, `astral.layers.import-direction`, `pattern.layers.import-discipline`.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1123 (parent) | ftr/AST-1123-support-signature-image-as-a-token-in-the-cover-letter |
| AST-1125 | sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract |
| AST-1126 | sub/AST-1123/AST-1126-cover-html-emit-token-replace-stop-auto-above |

**Epic worktree:** `astral-AST-1123/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | `/home/susan/.cursor/chats/c949585722c8f009c0bb68bfaec8882f/f961ae95-12a6-4b3f-ad15-95dbd2bccd72/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/c949585722c8f009c0bb68bfaec8882f/daf1a80f-7993-4d8b-b509-e3e74e1fdd3e/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/003557b9-f207-4f13-ba37-5e1fbe43db27/store.db` |
| Radia | review | `/home/susan/.cursor/chats/c949585722c8f009c0bb68bfaec8882f/d3ff29e3-ad11-4b2a-b54f-287ac048a05d/store.db` |

---

## Original brief

Right now, we are putting the signature ABOVE the Signature text, and it should fall BETWEEN the "Sincerely," and the Candidate's name and title.

Please allow when rendering the Cover letter (nowhere else) that {$SIGNATURE_IMAGE} is replaced with the image file correctly, and it does NOT appear above the signature text anymore.

### Comments

#### chuckles — 2026-08-02T17:37:41.571Z
@susan

1. If the candidate has a valid signature image but the cover signature text has **no** `{$SIGNATURE_IMAGE}` token — omit the image entirely, or fallback-insert between the first line (closing) and the remaining name/title lines?
2. Admin Session Cover Letter already places image between closing and name via separate fields — leave that path unchanged (no token), or require the same `{$SIGNATURE_IMAGE}` token there too?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
