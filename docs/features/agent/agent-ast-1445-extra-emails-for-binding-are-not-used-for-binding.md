# AST-1445 — Extra emails (for binding) are not used for binding

**Component:** agent  
**Children:** AST-1447  
**Linear archived:** AST-1445 2026-09-09; AST-1447 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-19 09:28 | AST-1447 | docs | `0dfd7b204` | plan-fix — extra emails missing from bind lookup |
| 2026-08-19 09:34 | AST-1447 | code | `6a1fc4f87` | expand extra emails in candidate bind lookup |
| 2026-08-19 09:40 | AST-1447 | docs | `c83eaa9c1` | Radia review — extra emails bind lookup |
| 2026-08-19 09:41 | AST-1447 | docs | `f99d1ba93` | Radia review follow-up — docs-acceptance |
| 2026-09-09 17:54 | AST-1447 | docs | `61d2a26f7` | archive Linear issue content |
| 2026-09-09 18:05 | AST-1445 | docs | `e0490e82e` | archive Linear issue content |

## Epic — AST-1445

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1445/extra-emails-for-binding-are-not-used-for-binding · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: Medium / —_

### As-is

An extra email saved on a candidate (example: `soosomerset@gmail.com` on Jolane) is not treated as a bind identity. Mail sent from that address on the candidate’s behalf does not bind to the candidate until the extra email is removed and the same address is set as Email for Messages (`contact.reply_email`).

### To-be

Extra emails participate in platform email binding/lookup the same way Email for Resume and Email for Messages do. Mail from an extra-email address on that candidate’s behalf binds to the candidate without moving the address into the messaging-email field.

### Proposed steps

1. Trace inbound bind/lookup (`get_candidate_id_for_query` / `CANDIDATE_LOOKUP_CONFIG` email paths) against `contact.extra_emails` — AST-1092 claimed extras were on the same lookup vocabulary as the two scalar emails.
2. If extras persist on Profile but lookup still only reads `contact_email` / `reply_email`, include `extra_emails` in the bind/lookup email pool.
3. Keep uniqueness (AST-1095 / AST-1045) treating extras as identity so two candidates cannot share the address while bind is opened.
4. Repro: extra email only (not Resume, not Messages) → mail on that candidate’s behalf binds.

### Original report

I added "[soosomerset@gmail.com](<mailto:soosomerset@gmail.com>)" to the extra emails for Jolane, and the email from [soosomerset@gmail.com](<mailto:soosomerset@gmail.com>) that was sent on Jolane's behalf did not bind until I removed the extra email and set it to the separate messaging email address.

#### Comments


##### susan — 2026-08-19T16:20:51.244Z

1092

##### chuckles — 2026-08-19T15:41:59.104Z

Ancestor candidates (ranked; pick one or ask about a specific row):

1. AST-1092 — UAT extra binding emails + Resume/Messages labels (child of AST-1065, archived). Contract: extra emails on Profile participate in platform binding/lookup via `CANDIDATE_LOOKUP_CONFIG`. Closest match to this symptom.
2. AST-1065 — Update candidate UI for contact info (archived parent of AST-1092). Owns Profile contact save/round-trip; extra-email *binding* was a UAT add-on on the child, not original parent AC.
3. AST-1095 — UAT new email must be unique vs all root and extra emails (child of AST-1045, archived). Same `extra_emails` pool, but uniqueness-on-save, not inbound bind.
4. AST-1045 — Verify unique contact info (archived parent of AST-1095). Further from bind-on-inbound; only if the miss is uniqueness vocabulary rather than lookup paths.

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1447 — Wire extra emails into candidate bind/lookup

_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1447/wire-extra-emails-into-candidate-bindlookup · Status at archive: Archive · Project: Astral Agent · Assignee: katherine · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1445_

#### Purpose

Wire extra emails into inbound bind/lookup so they participate the same way Email for Resume and Email for Messages do.

#### Context

Parent AST-1445 (orphaned mini-epic). Approved ancestor: AST-1092 (archived) — extra binding emails + Resume/Messages labels. Feature doc: `docs/features/interface/ast-1092-uat-extra-binding-emails-labels.md`.

#### As-is

An extra email saved on a candidate is not treated as a bind identity. Mail sent from that address on the candidate’s behalf does not bind until the extra email is removed and the same address is set as Email for Messages (`contact.reply_email`).

#### To-be

Extra emails participate in platform email binding/lookup the same way the two scalar emails do. Mail from an extra-email address on that candidate’s behalf binds without moving the address into the messaging-email field.

#### Proposed change

- [X] In `get_candidate_id_for_query`, after scalar email/name/slack paths, expand `CANDIDATE_LOOKUP_CONFIG["email_list_paths"]` via `_iter_uniqueness_path_values`
- [X] Append list-email values with the same casefold rule as scalar emails
- [X] Do not put `extra_emails` on scalar `email_paths`; do not walk uniqueness `list_paths` (websites)
- [X] Leave Profile, uniqueness gate, save coerce, and inbox header order unchanged

#### Proposed steps (parent hipshot — plan-fix owns the real work)

- [X] Trace inbound bind/lookup (`get_candidate_id_for_query` / `CANDIDATE_LOOKUP_CONFIG` email paths) against `contact.extra_emails`.
- [X] If extras persist but lookup only reads `contact_email` / `reply_email`, include `extra_emails` in the bind/lookup email pool.
- [X] Keep uniqueness (AST-1095 / AST-1045) treating extras as identity.
- [X] Repro: extra email only (not Resume, not Messages) → mail on that candidate’s behalf binds.

##### Comments


###### radia — 2026-08-19T16:40:45.327Z

[code-rubric] PROCEED (Commit: c83eaa9c) extra emails bind lookup

###### joan — 2026-08-19T16:31:40.937Z

[board-joan]  CANON: OK
context_tokens≈14000

###### betty — 2026-08-19T16:30:17.658Z

[board-betty] TESTS: OK

###### katherine — 2026-08-19T16:28:20.834Z

`origin/sub/AST-1445/AST-1447-wire-extra-emails-into-bind-lookup` @ `0dfd7b20` · extra emails skipped in lookup

---

_Implementation detail may live in git history on `origin/dev`._

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| + unplanned | `src/core/candidate.py` | — | `6a1fc4f87` |
