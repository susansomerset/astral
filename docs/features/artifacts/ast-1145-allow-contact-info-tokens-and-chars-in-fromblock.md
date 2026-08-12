# AST-1145 — Allow contact info tokens and | chars in fromBlock

<!-- linear-archive: AST-1145 archived 2026-08-11 -->

## Linear archive (AST-1145)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-chars-in-fromblock  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Cover letters need a candidate-owned **From** block that can mix contact tokens with ordinary text (including authoring `|`), so each candidate can keep a reusable contact header across cover letters without hardcoding values that drift when phone, email, or location change. AST-1124 / AST-1137 already store a from-block and compose a bullet default; this epic upgrades that contract so the default (and saved custom text) are token-driven, with `|` converted to `•` at emit the same way resume authoring uses pipes as separators that print as bullets.

## Functional scope

* **Tokenized From block:** From-block text may include contact tokens using consistent `{$TOKEN}` form. Allowed tokens for this surface: `FULL_NAME`, `LOCATION`, `CONTACT_EMAIL`, `PHONE` (existing registry names — brief aliases `RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE` are **not** added). At cover emit, those tokens resolve to the candidate’s current values. Unrecognized `{$…}` tokens are left as-is for forward-compat (same as other text token surfaces).
* **Authoring** `|` **→ printed** `•`**:** Candidates may put `|` in From-block text as an authoring separator. At emit, `|` separators convert to `•` (matching the AST-1137 golden / resume separator convention). Free text other than `|` is preserved.
* **Empty token / segment drop:** When a token resolves empty, omit that segment **and** its adjacent separator so recruiters never see dangling `•`, bare pipes, or unresolved placeholders in the printed From block.
* **Default when unset:** If the candidate has no saved from-block, emit uses a config-owned default template equivalent to two lines — `{$FULL_NAME} | {$LOCATION}` / `{$CONTACT_EMAIL} | {$PHONE}` — resolved and `|`→`•`, with empty segments omitted.
* **Persist across cover letters:** Saving the From block writes it to the existing candidate profile contact from-block field so the same authoring text is reused on later job and session cover emits. Empty / whitespace means “unset → default template.”
* **Session-typed From:** Non-empty Admin Session Cover Letter From text runs the **same** token resolve + `|`→`•` + empty-segment rules before emit (not only candidate-saved / default paths).
* **Emit consumers:** Job Print Cover Letter and Admin Session Cover Letter both show the resolved From-block text inside the existing SomersetCover `fromBlock` region.
* **Debug (backend):** When `debug=True` on the resolve/emit path that expands from-block tokens, log Style D index headers plus working-detail lines (prefix: two spaces, pipe, two spaces) for template source (candidate vs default vs session), tokens found/resolved/empty, `|`→bullet rewrite applied, and resolved text length — not batch-only summaries.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — extend `COVER_FROM_BLOCK_CONFIG` for default token template, allowlisted tokens (`FULL_NAME` / `LOCATION` / `CONTACT_EMAIL` / `PHONE`), `|`→`•` rewrite, and empty-segment policy; no inline sets in core/UI.
  * `pattern.ui.admin-endpoint` — persist via existing candidate profile data PUT; no new route for from-block save.
* **New patterns proposed**
  * none — contact text tokens reuse the existing text-token registry / resolve path (not a SIGNATURE_IMAGE-style binary render token). No new alias names for the brief’s typos.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — default template, token allowlist, separator rewrite live in config.
  * `astral.standards.no-hardcoded-sets` — token names and separators not littered in emit code.
  * `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` — do not reopen resume header emit or unrelated pipe parsers.
  * `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — one expand path for candidate custom, default template, and session-typed From; job/session consume it.
  * `astral.standards.debug-contract-gated` — Style D on touched `debug=` resolve/emit.
  * `astral.layers.import-direction` — UI does not own token expansion business rules.

## Boundaries

* Does **not** change SomersetCover CSS/DOM chrome (`.fromBlock` layout stays AST-1124 / AST-1138 / AST-1139).
* Does **not** change cover `{$SIGNATURE_IMAGE}` render-token contract (AST-1125 / AST-1126).
* Does **not** register brief aliases `RESUME_LOCATION`, `RESUME_EMAIL`, or `CANDIDATE_MOBLE` / `CANDIDATE_MOBILE`.
* Does **not** add from-block content to LLM prompt packet / Manage Tasks token pickers (AST-1137 kept it out of packet contact keys).
* Does **not** invent a second profile storage key if `contact.cover_letter_from_block` already owns persistence.
* Does **not** alter resume HTML header/contact strip.
* Does **not** treat From-block `|` as consult/rubric pipe-grade encoding.

## Acceptance criteria

1. With no saved from-block, Print Cover Letter and Session Cover Letter (empty From + selected candidate) emit a two-line From block with `•` between non-empty name/location and email/phone segments (AST-1137 golden shape).
2. Saving a custom From block on the candidate profile persists the authoring text (tokens and `|`); a later cover emit resolves tokens and prints `•` instead of `|`.
3. A saved From block with allowed contact tokens and `|` emits with tokens replaced, `|` shown as `•`, and no dangling separators when a token is empty.
4. Clearing the saved From block (empty/whitespace) returns emit to the default template behavior.
5. A non-empty typed Session Cover Letter From runs the same token + `|`→`•` + empty-segment rules before emit.
6. With `debug=True` on the touched resolve/emit path, logs show Style D index plus working-detail lines for source and token outcomes as described in Functional scope.
7. Resume print/HTML and signature-image token behavior are unchanged; brief token aliases are not resolvable.

## Dependencies and blockers

* **AST-1124** (and children **AST-1137** / **AST-1138** / **AST-1139**) — candidate from-block field, `resolve_cover_from_block`, and SomersetCover fromBlock emit must be on the integration line this epic builds on. Soft gate: do not dispatch until that stack is safely on `origin/dev` or Susan explicitly overrides.
* none otherwise.

## Open questions

none

## Proposed child tickets

#### 1!: **From-block token template + config contract - Ada**

Owns config for the default from-block token template (`{$FULL_NAME} | {$LOCATION}` / `{$CONTACT_EMAIL} | {$PHONE}`), allowlisted token ids, `|`→`•` rewrite flag/literals, and empty-segment policy. Extends the existing from-block config block; does not implement resolve/emit behavior. Does not own profile chrome beyond config-driven field metadata if needed.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.

#### 2: **Resolve tokens in from-block + emit debug - Hedy**

Owns expanding allowlisted tokens, `|`→`•`, and empty-segment drop inside the shared from-block path used by job emit, session empty→candidate resolve, **and** non-empty session-typed From; Style D debug on the touched `debug=` path. Consumes child #1 config. Does not change SomersetCover CSS or signature-image tokens. After #1.
**Citations:** `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

#### 3: **From-block authoring help on profile / session - Katherine**

Owns user-visible help (and any config-driven placeholder/label copy) so Susan can see that From supports `{$FULL_NAME}` / `{$LOCATION}` / `{$CONTACT_EMAIL}` / `{$PHONE}`, that `|` authors as `•` in print, and what the default template looks like when unset. Does not own resolve math or HTML CSS. Parallel with #2 once #1 field labels/help strings exist.
**Citations:** `pattern.ui.admin-endpoint`; `astral.layers.import-direction` (UI config-driven; no business rules in the page).

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1145 (parent) | ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock |
| AST-1147 | sub/AST-1145/AST-1147-from-block-token-template-config-contract |
| AST-1148 | sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug |
| AST-1149 | sub/AST-1145/AST-1149-from-block-authoring-help-profile-session |

**Epic worktree:** `astral-AST-1145/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/456ab255351bf8f06119557d99151dde/0de17e01-7007-4f69-9332-c52c1473d120/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/456ab255351bf8f06119557d99151dde/efdcecf6-f294-4be1-b475-dd2506610338/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/456ab255351bf8f06119557d99151dde/152eee6b-c7bc-4d77-91d6-f96ac8f789e8/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/c3f11b73-c9b4-4d23-8f5c-e7834053c751/store.db` |
| Radia | review | `/home/susan/.cursor/chats/456ab255351bf8f06119557d99151dde/3be41f4a-e50d-4b92-a167-1a8c61c288ec/store.db` |

---

## Original brief

Add a "From" section to the cover letter, and use our default set of tokens and | to indicate the content to be displayed, so that the candidate could add other content if they wish.

When the user saves the Fromblock, then save that to the candidate_data profile content for future reference so that the change is persisted across coverletters.  If there's no fromblock saved for the candidate, just use our default from the golden layout:

```
Susan Somerset • Oakland, CA
hire@susansomerset.com • 415-745-5238
```

`{$FULL_NAME} | {RESUME_LOCATION}\n{$RESUME_EMAIL} | {$CANDIDATE_MOBLE}`

### Comments

#### chuckles — 2026-08-02T23:52:30.981Z
@susan

1. Printed separator: keep ` • ` (AST-1137 golden), switch default print to ` | `, or is `|` in the template only an authoring delimiter that becomes ` • ` at emit?
2. Token names: map brief `RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE` → existing `LOCATION` / `CONTACT_EMAIL` / `PHONE` with consistent `{$…}`, or add aliases as written (including the missing `$` / MOBLE spelling)?
3. Empty token + `|`: omit adjacent separator (segment drop), leave dangling separator, or leave unresolved `{$TOKEN}` literal?
4. Session-typed From (non-empty Admin field): same token + `|` rules before emit, or only candidate-saved / default template paths?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
