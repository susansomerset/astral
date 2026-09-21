# AST-1065 — Update candidate ui for contact info

<!-- linear-archive: AST-1065 archived 2026-08-11 -->

## Linear archive (AST-1065)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The contact / context / artifacts library ([AST-1014](https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile) under [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake)) moves identity and comms into **name columns + a** `contact` **blob**. AST-1014 remapped backend homes; **the Profile UI was not updated**. This Interface epic corrects that so Candidate Profile represents the library and lets a user manage contact data end-to-end (including websites, username-or-URL GitHub/LinkedIn, editable `full` with derived default, and title_patterns / reason_codes on Contact) — and removes the duplicate title-patterns surface from candidate navigation.

## Functional scope

* **Profile speaks contact + columns.** Candidate Profile Contact Information binds to first / last / full / pronouns columns and `contact.*` fields — not legacy `profile.*` homes.
* **Manage contact data.** A candidate can view, edit, and save the user-facing contact set: contact email, reply email, phone, location, GitHub, LinkedIn, timezone, cover-letter signature text and image, websites (multi-entry list), title_patterns, and reason_codes.
* **Full name field.** `full` is a separate editable Profile field that **defaults to** the library-derived first+last join; the user may override it.
* **Username-or-URL entry.** GitHub and LinkedIn accept a username or a full URL; persisted form matches the library’s existing URL-base normalization.
* **Shape-driven surface.** Which fields appear and their field types come from config shapes / library vocabulary — React does not invent a parallel contact field list.
* **Nav cleanup.** Remove the duplicate title-patterns entry from candidate navigation (title patterns live on Profile Contact only).
* **Round-trip coherence.** After save, reopening Profile shows the same values from the library homes; token consumers that resolve from columns / contact see those updates.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — contact vocabulary and Profile field contracts stay in config (library keys + DATA_SHAPES), not hardcoded in React.
  * `pattern.ui.admin-endpoint` — any API touch stays thin, authenticated routes; business rules resolved server-side / in shapes.
* **New patterns proposed**
  * Optional: a reusable **multi-entry websites (or string-list) shape field type** if existing shape field types cannot express `contact.websites` — introduced by child #1; flag for Archie approval before reuse. If an existing shape type already fits, **none**.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — field keys and options live in config.
  * `astral.layers.ui-config-driven-business-logic` — Profile renders resolved shapes; does not own contact vocabulary.
  * `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — page/component placement and naming.
  * `astral.patterns.require-auth-on-protected-endpoints` — if any route is touched.
  * `astral.standards.in-scope-only` — no drive-by library or intake work.
  * `astral.docs.features-single-file-per-ticket` — one plan doc per child at plan time.

## Boundaries

* Does **not** re-implement the contact/context/artifacts library, migration, or token remaps — [AST-1014](https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile).
* Does **not** build mechanical preamble intake UI, PREAMBLE_CONFIG, or Ruth Valid/Try Again/Escalate — [AST-1017](https://linear.app/astralcareermatch/issue/AST-1017/mechanical-intake-front-door-ui-candidate-profile-preamble-to-intake) / siblings under [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake).
* Does **not** own Topic Menu or Estelle confirm — [AST-953](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation).
* Does **not** invent new contact blob keys beyond the library’s existing contact vocabulary.
* Does **not** expand **Admin Manage Candidates** into contact editing — Manage Candidates does not deal with contact info; Profile owns contact manage (Archie).
* Does **not** change the candidate state machine.

## Acceptance criteria

1. On Candidate Profile, Contact Information (including signature/image, title_patterns, reason_codes) read and save against name columns + `contact.*` — not `profile.*`.
2. A candidate can add, edit, and remove websites entries on Profile; after save and reload, those entries persist under `contact.websites`.
3. GitHub and LinkedIn fields accept username or full URL and persist in the normalized URL form consistent with the library URL bases.
4. `full` appears as an editable Profile field; when empty/unset it defaults to the library-derived first+last join; an explicit override persists and reloads.
5. Candidate navigation no longer exposes a duplicate title-patterns surface; title patterns are edited only via Profile Contact.
6. Save then reopen Profile shows the same contact values from the library homes.

## Dependencies and blockers

* **Blocked by:** [AST-1014](https://linear.app/astralcareermatch/issue/AST-1014/contact-context-artifacts-library-name-columns-candidate-profile) (User Testing) — library + remapped shapes/tokens must exist on the line this ships against.
* Soft related: [AST-952](https://linear.app/astralcareermatch/issue/AST-952/candidate-profile-preamble-to-intake); do not collide with [AST-1017](https://linear.app/astralcareermatch/issue/AST-1017/mechanical-intake-front-door-ui-candidate-profile-preamble-to-intake).
* Interface adjacency: [AST-1059](https://linear.app/astralcareermatch/issue/AST-1059/issue-with-the-rubric-grade-displays-on-the-jobs-list-pages) — no scope overlap.

## Open questions

none.

## Proposed child tickets

#### 1!: **Contact shapes + websites + full-name field contract - Ada**

Expose the full user-facing contact set (including websites, title_patterns, reason_codes) and the editable `full` column (derived default rule) in config shapes / field contracts so Profile can manage them without a hardcoded field list. Introduce a multi-entry websites (or string-list) shape field type only if no existing type fits — Archie approves that new type before reuse. Does **not** own Profile React behavior (#2) or nav cleanup (#2). Does **not** change the AST-1014 library schema beyond shape exposure of existing keys / full default behavior.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.layers.ui-config-driven-business-logic`.

#### 2: **Candidate Profile contact manage UI + nav title-patterns cleanup - Katherine**

Profile loads and saves columns + contact (websites list, username-or-URL for GitHub/LinkedIn, editable `full` with derived default, title_patterns / reason_codes, signature paths under contact). Remove duplicate title-patterns from candidate navigation. After #1. Does **not** own library migration (AST-1014), preamble UI (AST-1017), or Admin Manage Candidates contact editing.
**Citations:** `astral.layers.ui-config-driven-business-logic`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`.

**Monolith check:** Functional scope has 7 capabilities; 2 proposed children (shapes contract → Profile manage + nav). Admin Manage Candidates child removed per Archie (Manage Candidates does not deal with contact).

**New patterns:** optional websites/string-list shape field type — child #1; otherwise none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1065 (parent) | ftr/AST-1065-update-candidate-ui-for-contact-info |
| AST-1081 | sub/AST-1065/AST-1081-contact-shapes-websites-full |
| AST-1082 | sub/AST-1065/AST-1082-profile-contact-manage-nav |

* **AST-1092**: `sub/AST-1065/AST-1092-uat-extra-binding-emails-labels`

**Epic worktree:** `astral-AST-1065/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. Each entry is agent · role, then the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this list — not chat memory.

* **Ada** · engineer
  `/home/susan/.cursor/chats/d7d76b7fd235240874cc3c773cc8172d/25154617-537e-48ea-9861-0b7173e2fdaa/store.db`
* **Katherine** · engineer
  `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/4ba6534f-1749-4da8-ae4d-56c135cc9087/store.db`
* **Betty** · qa
  `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/57e42469-e51f-477c-85b3-fc1399e22dfb/store.db`
* **Radia** · review
  `/home/susan/.cursor/chats/d7d76b7fd235240874cc3c773cc8172d/fab81461-207b-4f88-8908-7982fdb0c6b4/store.db`

---

## Original brief

We need the candidate profile page to represent the new candidate data structure including candidate-contact and thr ability for a user to manage their contact data.

What do you suggest we do?

### Comments

#### chuckles — 2026-07-31T03:50:57.607Z
[fix-uat] answered — already on GitHub: `origin/dev` tip `93a01d2e` (AST-1092 resolve `9a2b7e4d`). Railway staging tracks `origin/dev` — re-test there, not local Chuckles `dev`.

— Chuckles

#### chuckles — 2026-07-31T03:50:50.473Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1092** | Profile extra binding emails + resume/messages email labels |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1092** — _Profile extra binding emails + resume/messages email labels_
- **Issue reported:** On Candidate Profile → Contact Information, the candidate can add websites, but cannot add **extra email addresses** for binding email sent to the platform. Existing email fields still use unclear labels (Contact Email / Reply Email) instead of purpose-named labels.
- **Should now:** 1. Profile Contact Information labels: `contact.contact_email` → **Email for Resume**; `contact.reply_email` → **Email for Messages (if different)**.
- **Quick check (this fix only):**
  1. Open Candidate → Profile → Contact Information on staging/`dev` after AST-1065 land.
  2. Confirm websites Add/Remove exists; note there is no parallel control for extra binding emails.
  3. Note Contact Email / Reply Email labels (not Resume / Messages).
  4. Attempt to register an additional binding email beyond the two scalar fields — no Profile surface for it.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-31T03:49:14.110Z
I can't test on your local dev.  you have to push to github.

#### chuckles — 2026-07-31T03:46:09.768Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1092** | Profile extra binding emails + resume/messages email labels |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1092** — _Profile extra binding emails + resume/messages email labels_
- **Issue reported:** On Candidate Profile → Contact Information, the candidate can add websites, but cannot add **extra email addresses** for binding email sent to the platform. Existing email fields still use unclear labels (Contact Email / Reply Email) instead of purpose-named labels.
- **Should now:** 1. Profile Contact Information labels: `contact.contact_email` → **Email for Resume**; `contact.reply_email` → **Email for Messages (if different)**.
- **Quick check (this fix only):**
  1. Open Candidate → Profile → Contact Information on staging/`dev` after AST-1065 land.
  2. Confirm websites Add/Remove exists; note there is no parallel control for extra binding emails.
  3. Note Contact Email / Reply Email labels (not Resume / Messages).
  4. Attempt to register an additional binding email beyond the two scalar fields — no Profile surface for it.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-31T03:26:00.147Z
I see the confusion now.  You have the option to add websites but we need the candidate to be able to add "extra" email addresses for binding email sent to the platform.  Also we should relabel the email fields as "Email for Resume" and "Email for Messages (if different)" so we are clearer about what two emails are for.  I consider this in scope for this ticket, we just didn't wireframe the solution upfront so there was some confusion.

#### chuckles — 2026-07-31T00:50:09.818Z
[check-linear] answered — Candidate → Profile → Contact Information (tabs: contact fields, websites, Title Patterns, reason codes). Not Admin Manage Candidates; Title Patterns nav item removed.

— Chuckles

#### susan — 2026-07-31T00:44:22.799Z
@chuckles Where should I be seeing the new candidate contact info in the UI?

#### chuckles — 2026-07-30T02:27:02.235Z
@susan — dispatch rejected; open questions still unanswered in the Description (no reply on the earlier @susan thread).

Missing before Todo + Chuckles again:
* Answers to Open questions 1–4 (or remove/resolve them in the Description)
* Confirm AST-1014 blocker is ok to proceed against (still blocks this parent in Linear)

— Chuckles

#### chuckles — 2026-07-30T01:07:40.380Z
@susan

1. Confirm this is a **follow-on** to AST-1014’s 1:1 Profile remaps — primary gap = websites + username-or-URL contact manage UX — not a re-do of 1014?
2. Is Admin Manage Candidates in scope beyond keeping create/edit on the same column/contact homes (no full contact editor in Admin)?
3. Is `full` name derived-only (first + last join from the library rule), or user-editable on Profile?
4. Should candidate-facing Contact Information include `title_patterns` / `reason_codes`, or leave those as separate ops/admin-ish sections?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
