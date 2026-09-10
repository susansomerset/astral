# AST-1445 — Extra emails (for binding) are not used for binding

<!-- linear-archive: AST-1445 archived 2026-09-09 -->

## Linear archive (AST-1445)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1445/extra-emails-for-binding-are-not-used-for-binding  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

An extra email saved on a candidate (example: `soosomerset@gmail.com` on Jolane) is not treated as a bind identity. Mail sent from that address on the candidate’s behalf does not bind to the candidate until the extra email is removed and the same address is set as Email for Messages (`contact.reply_email`).

## To-be

Extra emails participate in platform email binding/lookup the same way Email for Resume and Email for Messages do. Mail from an extra-email address on that candidate’s behalf binds to the candidate without moving the address into the messaging-email field.

## Proposed steps

1. Trace inbound bind/lookup (`get_candidate_id_for_query` / `CANDIDATE_LOOKUP_CONFIG` email paths) against `contact.extra_emails` — AST-1092 claimed extras were on the same lookup vocabulary as the two scalar emails.
2. If extras persist on Profile but lookup still only reads `contact_email` / `reply_email`, include `extra_emails` in the bind/lookup email pool.
3. Keep uniqueness (AST-1095 / AST-1045) treating extras as identity so two candidates cannot share the address while bind is opened.
4. Repro: extra email only (not Resume, not Messages) → mail on that candidate’s behalf binds.

## Original report

I added "[soosomerset@gmail.com](<mailto:soosomerset@gmail.com>)" to the extra emails for Jolane, and the email from [soosomerset@gmail.com](<mailto:soosomerset@gmail.com>) that was sent on Jolane's behalf did not bind until I removed the extra email and set it to the separate messaging email address.

### Comments

#### susan — 2026-08-19T16:20:51.244Z
1092

#### chuckles — 2026-08-19T15:41:59.104Z
Ancestor candidates (ranked; pick one or ask about a specific row):

1. AST-1092 — UAT extra binding emails + Resume/Messages labels (child of AST-1065, archived). Contract: extra emails on Profile participate in platform binding/lookup via `CANDIDATE_LOOKUP_CONFIG`. Closest match to this symptom.
2. AST-1065 — Update candidate UI for contact info (archived parent of AST-1092). Owns Profile contact save/round-trip; extra-email *binding* was a UAT add-on on the child, not original parent AC.
3. AST-1095 — UAT new email must be unique vs all root and extra emails (child of AST-1045, archived). Same `extra_emails` pool, but uniqueness-on-save, not inbound bind.
4. AST-1045 — Verify unique contact info (archived parent of AST-1095). Further from bind-on-inbound; only if the miss is uniqueness vocabulary rather than lookup paths.

---

_Implementation detail may live in git history on `origin/dev`._
