# AST-1044 — Bind email to candidate

<!-- linear-archive: AST-1044 archived 2026-08-05 -->

## Linear archive (AST-1044)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-952

### Description

## Purpose

Susan needs the Meteorite **Manage Email** admin surface to connect an inbox message at `astral.career.match@gmail.com` to a **known candidate**, show that bind visually, and let her press **Create** to start a `create_job` path that lands a meteorite job for that candidate. **AST-1031** already reads the inbox; **AST-1034** already creates jobs under `meteorite-<candidate_id>` from raw HTML. This epic is the missing bind + operator action between those two — and it introduces a reusable candidate lookup other surfaces can call later.

## Functional scope

* Astral provides a reusable candidate lookup: pass a string, match it against the candidate’s contact info and names, and return the astral candidate id when the match is unambiguous.
* For each inbox message shown on the Manage Email pane, Astral uses that lookup with the message **From** address and reports whether it matches a candidate (and which one).
* Match homes for contact (all of these): the **AST-1014** contact-blob email fields in `candidate_data`, plus today’s `profile.contact_email` / `profile.reply_email` during transition. Name fields included in the same reusable lookup. Inbox bind still uses **From only** as the query string (case-insensitive) — no Reply-To or other headers.
* The Manage Email admin pane (renamed from **Read email**) visually indicates when a message is matched to a candidate (enough identity for Susan to trust the bind before acting).
* When a message is matched, an active **Create** control initiates a `create_job` for that candidate using the meteorite job-create capability from **AST-1034**. Create runs a strip/extract step on the message content for this epic and includes the message **subject** in the content passed as job HTML — then feeds that result to meteorite create.
* When a message is not matched (no hit or ambiguous hit), **Create** is not available (no orphan meteorite jobs from unidentified senders).
* Match and create paths that accept `debug=True` emit backend debug contract detail (what was found/matched/recorded per message or create attempt — Style D index headers and `|` working detail; long HTML truncated per Code Rules / AST-538). No debug-logging requirement on React.

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — extend the auth-gated Manage Email admin HTTP + thin API; React renders match + Create from resolved payloads.
  * `pattern.layers.import-discipline` — UI never calls Gmail or data; core owns lookup, strip/extract, and create orchestration; reuse existing inbox/meteorite core entry points.
  * `pattern.config.config-block` — which contact/name fields the reusable lookup consults live in config, not inline string lists in callers.
* **New patterns proposed**
  * **Reusable string → candidate id lookup in core candidate** — a single core helper (Susan’s shape: `get_candidate`) takes a string, matches it against configured candidate contact info and names, and returns the astral candidate id on an unambiguous hit (none / ambiguous → no id). Manage Email From-bind is the first caller; other surfaces may reuse it later. Flag for Archie approval before plans treat it as catalog law; until approved, implement under this epic’s citations only.
* **Applicable statutes**
  * `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` — lookup/create in core; Gmail stays external; UI thin.
  * `astral.patterns.require-auth-on-protected-endpoints` — Manage Email APIs and Create remain protected admin/auth surfaces.
  * `astral.layers.ui-config-driven-business-logic` — match eligibility and Create enablement resolved server-side; React does not invent match rules.
  * `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — contact/name field keys and match rules from config.
  * `astral.standards.debug-contract-gated` — debug=True match/create paths.
  * `astral.standards.database-header-inventory` — no new tables; use AST-1014 contact homes + existing meteorite/job paths.
  * `universal` set — product code changes.

## Boundaries

* Does **not** re-implement Gmail inbox list/get (**AST-1031** Done) or invent a second mailbox client.
* Does **not** re-implement meteorite company lazy-ensure or the raw-HTML job-create API (**AST-1034** / children) — this epic **calls** that create path from Manage Email Create after strip/extract + subject inclusion.
* Does **not** auto-create jobs on inbox arrival — Create is an explicit operator action.
* Does **not** classify, reply, label, archive, delete, or otherwise mutate Gmail mailbox state beyond what is required to display and act on messages already readable today.
* Does **not** invent a full Meteorite routing/ingest pipeline (multi-step classify, attachment pipelines, employer resolution) — reusable lookup + bind + strip/extract + Create only.
* Does **not** create meteorite jobs for unmatched or ambiguous messages.
* Does **not** handle two candidates sharing the same email — that case is out of scope (product invariant: emails are unique across candidates). Ambiguous name hits return no id (no Create) rather than inventing a picker in this epic.
* Does **not** replace Profile/Admin contact editing (**AST-952** / **AST-1014** own contact library shape).
* Must not break existing inbox list/modal browse for unmatched messages (still browsable under Manage Email).
* Must not break non-meteorite job/company flows.

## Acceptance criteria

1. A reusable core candidate lookup accepts a string, matches against configured contact info and names, and returns the astral candidate id on an unambiguous hit (and no id when none or ambiguous).
2. On Manage Email, a message whose **From** uniquely matches via that lookup shows a clear visual bind to that candidate.
3. On Manage Email, a matched message exposes an active **Create** control; an unmatched or ambiguous message does not.
4. Pressing **Create** on a matched message strip/extracts the message content (including the **subject** in the content), creates a meteorite job for that candidate via the **AST-1034** create capability with that result as the JD HTML, and the operator can observe success (or a clear failure) without leaving the pane flow.
5. Admin nav/screen is labeled **Manage Email** (replacing **Read email**).
6. Unauthenticated callers cannot run match or Create endpoints/screens.
7. With `debug=True` on touched match/create backend paths, found/matched/recorded outcomes use Style D index headers and `|` detail; with `debug=False`, no new debug-contract lines from those paths.
8. Existing inbox browse (list + HTML body view) still works for unmatched messages after this epic.

## Dependencies and blockers

* **AST-1014** (Contact / context / artifacts library) — **hard blocker**. Match uses the contact node in `candidate_data` (plus transitional profile email fields). This epic does not start until that contact home is on the line Susan expects for UAT.
* **AST-1034** (Support meteorite jobs) — User Testing; Create must call its meteorite job-create path. Soft-gate UAT of Create until that epic is accepted on staging/`origin/dev` as Susan expects.
* **AST-1031** (Receive email) — Done; Manage Email extends that seed surface.

## Open questions

none

## Proposed child tickets

#### 1!: **Reusable get_candidate string lookup + From bind - Ada**

Owns the reusable core candidate lookup Susan named (`get_candidate`): given a string, match against configured contact info and names, return astral candidate id on an unambiguous hit; wire Manage Email’s From-address bind through that helper (including debug=True found/matched detail). Does **not** own Manage Email React chrome, strip/extract, or the Create → meteorite wire (children 2–3). Does **not** invent multi-candidate picker UX (ambiguous → no id).
**Citations:** `pattern.config.config-block`; `pattern.layers.import-discipline`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.debug-contract-gated`; `astral.layers.core-vs-external-bright-line`.

#### 2!: **Manage Email match indicator + Create control - Hedy**

Owns rename **Read email** → **Manage Email** and the admin surface changes: show match bind on listed/selected messages, enable **Create** only when matched, keep unmatched browse working. Does **not** own the reusable lookup (child 1) or strip/extract + meteorite create wire (child 3 / **AST-1034**). After #1.
**Citations:** `pattern.ui.admin-endpoint`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.layers.import-direction`.

#### 3: **Strip/extract + create job from matched email via meteorite - Katherine**

Owns Create: strip/extract message content (include **subject** in the content), call the **AST-1034** meteorite job-create path with the matched candidate id and resulting HTML, surface success/failure on the pane, and debug=True create detail. Does **not** own lookup/match (child 1) or general Manage Email layout beyond the Create call path (child 2). After #1 and #2; blocked by **AST-1014** (match homes) and **AST-1034** create capability for this epic’s UAT line.
**Citations:** `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.standards.debug-contract-gated`.

**New patterns:** Child 1 introduces reusable string → candidate id lookup (`get_candidate`); children 2–3 consume From-bind via that helper.

**Monolith check:** Functional scope has 7 capability bullets; 3 proposed children (reusable lookup+From bind / Manage Email UI / strip-extract+create wire).

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1044 (parent) | ftr/AST-1044-bind-email-to-candidate |
| AST-1047 | sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind |
| AST-1048 | sub/AST-1044/AST-1048-manage-email-match-indicator-create-control |
| AST-1049 | sub/AST-1044/AST-1049-strip-extract-create-job-matched-email-meteorite |
| AST-1051 | sub/AST-1044/AST-1051-uat-create-button-on-manage-email-list-rows |

**Epic worktree:** `astral-AST-1044/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/855b864e026601b5ae78c61bdc1ff345/643a4613-9f42-428e-bd24-61eebbf8c9a5/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/855b864e026601b5ae78c61bdc1ff345/76c6db7e-d67f-401a-a1a0-6f5096f9b9b9/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/855b864e026601b5ae78c61bdc1ff345/a6c5b2b2-f473-4e03-8ab5-e68378b75acd/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/dfb49f98-08ec-4552-a640-3c0c319edde8/store.db` |
| Radia | review | `/home/susan/.cursor/chats/855b864e026601b5ae78c61bdc1ff345/a841fe6c-0779-484e-bf98-36da4ba4dc9a/store.db` |

---

## Original brief

When [astral.career.match@gmail.com](<mailto:astral.career.match@gmail.com>) receives an email, validate it against the known candidate data and visually indicate that the email has been matched to a candidate.  Then have a "create_job" event I can initiate by an active button "create" on the Manage Email pane.

This connects incoming email with candidates, and uses the work from [AST-1034](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs) to generate the job record for known candidates.

NOTE: I am not sure if we have already implemented the ticket that will introduce candidate_contact as a base field to the candidate table, but it is a blocker for this ticket.

### Comments

#### chuckles — 2026-07-29T20:39:49.830Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1051** | Create button on Manage Email list rows (not modal) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1051** — _Create button on Manage Email list rows (not modal)_
- **Issue reported:** On Manage Email, the **Create** control lives in the message popup/modal. The HTML body panel blocks or occludes that button, so Susan cannot reliably press Create while inspecting the message.
- **Should now:** Each matched inbox **list row** has its own active **Create** control. Susan can create a meteorite job from the list without depending on a Create button inside the HTML preview modal.
- **Quick check (this fix only):**
  1. Open Admin → Manage Email.
  2. Open (or select) a matched message so the HTML body modal/panel is visible.
  3. Try to press **Create** — the control is on the popup/modal and is blocked by the HTML text panel.
  4. Confirm Create is not available as a per-row control on the list items.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-29T20:25:46.700Z
@chuckles UI bug: I'd like the create button to be on the list items individually, not the popup modal (where the button is blocked by the HTML text panel).

#### chuckles — 2026-07-29T18:41:50.439Z
@susan open questions:

1. Match contact home: today’s `profile.contact_email` / `profile.reply_email`, AST-1014 contact-blob emails, or both? Is AST-1014 a hard blocker?
2. Which message identity fields count (From only vs Reply-To / other)? Equality rules?
3. Ambiguous match (two candidates, same email): refuse Create, pick one, or force choose?
4. Rename **Read email** → **Manage Email**, or keep label?
5. Confirm Create passes full message HTML body as `html_body` (no strip/extract in this epic)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
