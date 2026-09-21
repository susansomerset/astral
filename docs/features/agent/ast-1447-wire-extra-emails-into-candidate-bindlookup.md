# AST-1447 — Wire extra emails into candidate bind/lookup

<!-- linear-archive: AST-1447 archived 2026-09-09 -->

## Linear archive (AST-1447)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1447/wire-extra-emails-into-candidate-bindlookup  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1445 — Extra emails (for binding) are not used for binding  
**Blocked by / blocks / related:** parent: AST-1445

### Description

## Purpose

Wire extra emails into inbound bind/lookup so they participate the same way Email for Resume and Email for Messages do.

## Context

Parent AST-1445 (orphaned mini-epic). Approved ancestor: AST-1092 (archived) — extra binding emails + Resume/Messages labels. Feature doc: `docs/features/interface/ast-1092-uat-extra-binding-emails-labels.md`.

## As-is

An extra email saved on a candidate is not treated as a bind identity. Mail sent from that address on the candidate’s behalf does not bind until the extra email is removed and the same address is set as Email for Messages (`contact.reply_email`).

## To-be

Extra emails participate in platform email binding/lookup the same way the two scalar emails do. Mail from an extra-email address on that candidate’s behalf binds without moving the address into the messaging-email field.

## Proposed change

- [X] In `get_candidate_id_for_query`, after scalar email/name/slack paths, expand `CANDIDATE_LOOKUP_CONFIG["email_list_paths"]` via `_iter_uniqueness_path_values`
- [X] Append list-email values with the same casefold rule as scalar emails
- [X] Do not put `extra_emails` on scalar `email_paths`; do not walk uniqueness `list_paths` (websites)
- [X] Leave Profile, uniqueness gate, save coerce, and inbox header order unchanged

## Proposed steps (parent hipshot — plan-fix owns the real work)

- [X] Trace inbound bind/lookup (`get_candidate_id_for_query` / `CANDIDATE_LOOKUP_CONFIG` email paths) against `contact.extra_emails`.
- [X] If extras persist but lookup only reads `contact_email` / `reply_email`, include `extra_emails` in the bind/lookup email pool.
- [X] Keep uniqueness (AST-1095 / AST-1045) treating extras as identity.
- [X] Repro: extra email only (not Resume, not Messages) → mail on that candidate’s behalf binds.

### Comments

#### radia — 2026-08-19T16:40:45.327Z
[code-rubric] PROCEED (Commit: c83eaa9c) extra emails bind lookup

#### joan — 2026-08-19T16:31:40.937Z
[board-joan]  CANON: OK
context_tokens≈14000

#### betty — 2026-08-19T16:30:17.658Z
[board-betty] TESTS: OK

#### katherine — 2026-08-19T16:28:20.834Z
`origin/sub/AST-1445/AST-1447-wire-extra-emails-into-bind-lookup` @ `0dfd7b20` · extra emails skipped in lookup

---

_Implementation detail may live in git history on `origin/dev`._
