# AST-1158 — Duplicate error on fromblock content on user profile

<!-- linear-archive: AST-1158 archived 2026-08-07 -->

## Linear archive (AST-1158)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1158/duplicate-error-on-fromblock-content-on-user-profile  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Candidate Profile is refusing (or toasting as duplicate) when operators save **Cover Letter From** text that another candidate already has — including the shared default token template. From-block is free-form authoring text for cover headers, not an identity handle; multiple candidates must be allowed to share the same from-block content. This restores profile save so from-block edits are not blocked by a uniqueness rule that does not belong on that field.

## Functional scope

* Saving Candidate Profile with a non-empty `cover_letter_from_block` (custom authoring text or the default token template) succeeds even when another live candidate already has the same from-block string.
* The contact uniqueness gate continues to treat only true identity fields as uniqueness tokens (emails, phone, GitHub, LinkedIn, websites, Slack user id, and the shared email pool including extra emails). From-block authoring text is explicitly **not** a uniqueness token — same class as signature / location / timezone / title patterns.
* Profile save still hard-fails with the existing toast-ready duplicate contact error when a real identity value collides across candidates; fixing from-block must not weaken that gate.
* When the touched save / uniqueness path runs with `debug=True`, Style D logs still show what uniqueness tokens were found and whether within-dedupe or cross-collision was recorded — without treating from-block text as a token.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: uniqueness vocabulary stays in `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` (sibling to lookup); from-block remains owned by `COVER_FROM_BLOCK_CONFIG` / library contact keys as non-identity authoring text.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth` (which fields are uniqueness tokens lives in config, not ad-hoc core lists); `astral.standards.no-hardcoded-sets` (do not invent an inline from-block uniqueness set); `astral.standards.in-scope-only` (profile from-block uniqueness only); `astral.standards.dry-and-focused-functions` (reuse the AST-1080 gate; do not fork a second save validator); `astral.standards.debug-contract-gated` (debug lines only when `debug=True`); `astral.layers.import-direction` (UI stays thin; gate remains core).

## Boundaries

* Does **not** own Print Cover Letter live from-block resolve/expand (**AST-1157**).
* Does **not** change default template, allowlist, `|`→`•` emit, authoring help, or session Admin Cover Letter chrome (AST-1145 / AST-1147–1149).
* Does **not** remove or soften uniqueness for emails, phone, GitHub, LinkedIn, websites, Slack user id, or extra emails (AST-1045 / AST-1079 / AST-1080 / AST-1095).
* Does **not** add a database UNIQUE constraint on from-block (there is none; do not invent one).
* Does **not** redesign Candidate Profile layout beyond whatever is required so save no longer false-fails on from-block content.

## Acceptance criteria

1. Two live candidates can each save the **same** non-empty Cover Letter From authoring string (including the default token template text); both profile saves succeed and GET shows that string on each candidate.
2. Saving a profile whose from-block matches another candidate’s from-block does **not** return the cross-candidate duplicate-contact error and does not toast as a uniqueness collision.
3. Saving a profile that reuses another candidate’s identity email / phone / GitHub / LinkedIn / website / Slack user id still fails with the existing toast-ready duplicate-contact error (from-block fix does not bypass the gate).
4. With `debug=True` on the touched uniqueness/save path, logs show found/recorded uniqueness-token behavior under Style D index headers and do not list from-block text as a uniqueness token; no new debug-contract lines when `debug=False`.

## Dependencies and blockers

none. Prior uniqueness epics (**AST-1045** / **AST-1079** / **AST-1080**) and from-block epics (**AST-1137** / **AST-1145**) are Done. Adjacent **AST-1157** (Print Cover Letter live from-block) is out of scope and not a blocker.

## Open questions

none.

## Proposed child tickets

#### 1: **Exclude from-block from contact uniqueness on profile save - Ada**

Owns making `contact.cover_letter_from_block` a non-uniqueness contact field end-to-end: uniqueness vocabulary must not treat it as an identity token, and Candidate Profile save must allow identical from-block text across candidates while keeping real identity collisions hard-fail. Does **not** own Print Cover Letter (**AST-1157**), from-block template/allowlist/help, or uniqueness rules for email/phone/GitHub/LinkedIn/websites/Slack.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`.

Monolith check: Functional scope has 4 capabilities and 1 proposed child — intentional; config vocabulary + save-gate behavior + profile UAT must ship as one vertical slice so uniqueness cannot drift between config and enforce.

---

## Original brief

We are dupe-checking the fromblock content, which is not correct.  there is no unique constraint on that column.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1158 (parent) | ftr/AST-1158-duplicate-error-on-fromblock-content-on-user-profile |
| AST-1160 | sub/AST-1158/AST-1160-exclude-from-block-from-contact-uniqueness-on-profile-save |

**Epic worktree:** `astral-AST-1158/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/10dac3fead6ecc1c00af26b7851d74a1/c5ba1f43-88da-4db5-a0d3-6240e56913cc/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/8b74b523-ca72-4dcd-b282-f75c108ad78b/store.db` |
| Radia | review | `/home/susan/.cursor/chats/10dac3fead6ecc1c00af26b7851d74a1/0ad06d7d-6feb-4777-95a1-136dd9397d01/store.db` |

### Comments

#### chuckles — 2026-08-03T06:32:33.083Z
[check-linear] Canceled — operator mistake, not a product bug

#### susan — 2026-08-03T06:31:22.381Z
@chuckles Please cancel this ticket.  It is not an error, I made a mistake.

#### chuckles — 2026-08-03T06:02:33.696Z
[check-linear] Discussion — not stuck; define in progress

#### chuckles — 2026-08-03T06:01:06.553Z
@susan Not stuck on the product — prior attempts died on MCP/tooling. Defining now.

— Chuckles

#### susan — 2026-08-03T05:55:18.995Z
@chuckles did this get stuck?

---

_Implementation detail may live in git history on `origin/dev`._
