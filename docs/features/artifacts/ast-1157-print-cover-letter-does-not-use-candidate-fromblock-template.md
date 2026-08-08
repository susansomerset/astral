# AST-1157 — Print Cover Letter does not use candidate fromblock template

<!-- linear-archive: AST-1157 archived 2026-08-07 -->

## Linear archive (AST-1157)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1157/print-cover-letter-does-not-use-candidate-fromblock-template  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1147; related: AST-1124; related: AST-1145; related: AST-1149

### Description

## Purpose

Print Cover Letter still shows a name + email-only `fromBlock` instead of the candidate profile’s current from-block contract (saved custom text, or the default token template when unset). After [AST-1124](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect) / [AST-1145](https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock), operators expect Print to always resolve from the live candidate profile so header format and contact segments stay current.

## Functional scope

* When the operator opens **Print Cover Letter** for a job, the cover HTML `fromBlock` is produced at print time from the **live** candidate profile — not a stale or hard-coded name/email header.
* Resolution follows the established from-block contract: non-empty saved cover from-block wins; otherwise the config default token template is used; allowlisted tokens expand to current candidate values; authoring `|` becomes the emit separator; empty segments (and their adjacent separators) are dropped so print never shows dangling separators or unresolved allowlisted empties.
* Printed `fromBlock` shows **expanded** values (not literal `{$TOKEN}` strings). After the operator edits the profile from-block (or contact fields those tokens read), the next Print Cover Letter reflects that state without a server restart.
* When the print/build path runs with `debug=True`, debug output records what from-block source was chosen and what text was found vs recorded for emit (Style D / AST-538 contract).

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: from-block default template, allowlist, separators, and empty-segment policy stay in `COVER_FROM_BLOCK_CONFIG` (no new inline literals in emit).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth` (config owns template/policy); `astral.standards.no-hardcoded-sets` (no ad-hoc header composition beside the contract); `astral.standards.in-scope-only` (Print Cover Letter from-block only); `astral.standards.dry-and-focused-functions` (reuse shared resolve/expand; do not fork a second header builder); `astral.standards.debug-contract-gated` (debug lines only when `debug=True`); `astral.layers.import-direction` (UI thin; resolve/emit in core).

## Boundaries

* Does **not** change the default token template string, allowlist, or authoring help copy ([AST-1147](https://linear.app/astralcareermatch/issue/AST-1147/from-block-token-template-config-contract-allow-contact-info-tokens) / [AST-1149](https://linear.app/astralcareermatch/issue/AST-1149/from-block-authoring-help-on-profile-session-allow-contact-info-tokens)).
* Does **not** own Candidate Profile validation / duplicate-error UX for from-block (sibling [AST-1158](https://linear.app/astralcareermatch/issue/AST-1158/duplicate-error-on-fromblock-content-on-user-profile)).
* Does **not** redesign SomersetCover CSS/DOM, signature-image token behavior, resume Print header/contact strip, or Session Admin Cover Letter form chrome (session empty→candidate resolve stays as already shipped unless Print and session share one broken path — then fix the shared resolve, not session UI).
* Does **not** invent brief aliases (`RESUME_LOCATION`, `RESUME_EMAIL`, `CANDIDATE_MOBLE`, etc.).
* Must not break job cover body/subject/signature mapping or resume Print.

## Acceptance criteria

1. For a job with cover letter content, **Print Cover Letter** HTML includes a SomersetCover `fromBlock` whose text equals live resolve of that job’s candidate: saved profile from-block expanded, or default template expanded when the profile field is empty/whitespace.
2. With a non-empty saved profile from-block that uses allowlisted tokens and `|`, print shows expanded values and emit separators — not the pre-contract name+email-only header shape when the resolved text differs.
3. With an empty profile from-block, print matches expand of the config default template against current candidate name/contact (empty segments omitted per policy).
4. After changing the profile from-block (or token source fields) and saving, the next Print Cover Letter shows the new resolved text.
5. With `debug=True` on the touched print/build path, logs show from-block source and found/recorded text detail under Style D index headers; no new debug-contract lines when `debug=False`.

## Dependencies and blockers

none. Prior from-block epics ([AST-1124](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect), [AST-1145](https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock)) are Done. Adjacent Discussion [AST-1158](https://linear.app/astralcareermatch/issue/AST-1158/duplicate-error-on-fromblock-content-on-user-profile) (profile from-block duplicate error) is out of scope and not a blocker.

## Open questions

none.

## Proposed child tickets

#### 1: **Job Print Cover Letter live from-block - Hedy**

Owns `/candidate/cover/<job_id>` (JAR **Print Cover Letter**) so SomersetCover `fromBlock` always comes from live candidate from-block resolve/expand at print time, with Style D debug on the touched `debug=` path. Does **not** own profile validation UX ([AST-1158](https://linear.app/astralcareermatch/issue/AST-1158/duplicate-error-on-fromblock-content-on-user-profile)), session Admin form chrome, resume print header, or SomersetCover CSS redesign.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

Monolith check: Functional scope has 3 capabilities and 1 proposed child — intentional; load + resolve + emit must ship as one vertical slice for Print Cover Letter UAT.

---

## Original brief

When I click "Print Cover Letter", I still get this header:

```
<div class="fromBlock">
        Susan Somerset<br>
        hire@susansomerset.com
      </div>
```

Not the candidate fromblock default:

```
{$FULL_NAME} | {$LOCATION}
{$CONTACT_EMAIL} | {$PHONE}
```

Print Cover Letter should ALWAYS get the latest fromblock format from the candidate profile.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| [AST-1157](https://linear.app/astralcareermatch/issue/AST-1157/print-cover-letter-does-not-use-candidate-fromblock-template) (parent) | ftr/AST-1157-print-cover-letter-does-not-use-candidate-fromblock-template |
| [AST-1159](https://linear.app/astralcareermatch/issue/AST-1159/job-print-cover-letter-live-from-block-print-cover-letter-does-not-use) | sub/AST-1157/AST-1159-job-print-cover-letter-live-from-block |

**Epic worktree:** `astral-AST-1157/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | `/home/susan/.cursor/chats/cfd26027279af5abe3ee8b7c1a5929e1/1764eafd-30f7-4454-99a9-12d7af8b6160/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/eaf122e7-4bb6-4b46-bca8-221e2685b087/store.db` |
| Radia | review | `/home/susan/.cursor/chats/cfd26027279af5abe3ee8b7c1a5929e1/7fe245ec-8efb-4d63-8958-ce3a27ae9f0b/store.db` |

### Comments

#### chuckles — 2026-08-03T06:32:31.404Z
[check-linear] Canceled — user-error (email collision, not from-block)

#### susan — 2026-08-03T06:29:33.474Z
@chuckles Go ahead and cancel this ticket.  Joan caught the problem as user-error in [AST-1158](https://linear.app/astralcareermatch/issue/AST-1158/duplicate-error-on-fromblock-content-on-user-profile).  The issue was that the actual existing email for the test candidate was already saved to another record before the deduping was in place, so it was complaining about the email, not the fromblock at all.

---

_Implementation detail may live in git history on `origin/dev`._
