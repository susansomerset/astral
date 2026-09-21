# AST-1308 — Email bind where email is in the To: field (alone)

<!-- linear-archive: AST-1308 archived 2026-08-19 -->

## Linear archive (AST-1308)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1308/email-bind-where-email-is-in-the-to-field-alone  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan is autoforwarding some job emails into the Astral inbox. Those messages still carry her candidate address on **To**, but **From** is the original sender — so today's From-only bind leaves them unbound, and gaze_email / Land Meteorite will not ingest them for her. This epic extends the existing inbox bind so a From miss may still attach the message to the right candidate via To, without changing successful From binds or inventing a second matching system.

## Functional scope

* From-first bind stays as it is: when the message **From** uniquely matches a candidate via the existing reusable lookup (same contact / extra-email homes as today), that candidate wins and To is not consulted.
* When From does not uniquely bind, Astral attempts the same lookup against **To** only when To has a **single remaining address** after ignoring the Astral inbox address. A unique candidate hit on that one address is a first-class bind — Manage Email, gaze_email ingest, Land Meteorite, and live Avail counts all treat it the same as a From bind.
* Multi-address To (after ignoring the Astral inbox) stays unbound — google-group and other multi-recipient noise is not teased apart.
* The Astral inbox address itself is never a bind hit. Any path that still rematches a message independently of the list payload uses the same From-then-To rule (no From-only leftover).
* When `debug=True` on touched bind paths, each message logs what was found and what was recorded: which header bound (`from` or `to`), the address used, and the candidate id or none/ambiguous. Style D index headers with universal `index N/M`, primary identifier, and outcome; working detail uses prefix `|`; payloads longer than 50 lines use first 15 / `<n lines omitted>` / last 15. No new debug-contract lines when `debug=False`. No debug-logging requirement on React.

## Architectural definition

* **Patterns to reuse**
  * `pattern.layers.import-discipline` — Gmail stays external (expose To on mailbox rows); core owns bind order and lookup; UI keeps rendering `candidate_match` and does not invent To rules.
  * `pattern.config.config-block` — lookup homes and the Astral inbox address stay config-owned; bind header order is not an inline set in callers.
  * `pattern.ui.admin-endpoint` — Manage Email remains the auth-gated admin surface; this epic does not add a second inbox API.
* **New patterns proposed**
  * none
* **Applicable statutes**
  * `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` — To is mailbox I/O; bind decision is core.
  * `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` — match homes and inbox identity from config.
  * `astral.layers.ui-config-driven-business-logic` — match eligibility resolved server-side; React does not parse To.
  * `astral.standards.debug-contract-gated` — Style D on touched `debug=` bind paths.
  * `astral.standards.dry-and-focused-functions` — one bind rule, reused by list enrichment, rematch, Avail, and ingest.
  * `astral.standards.in-scope-only` — To fallback only; no new mailbox product.
  * `universal` set — product code changes.

## Boundaries

* Does **not** change how From binds when From uniquely matches (including when To would match a different candidate).
* Does **not** attempt To-bind when To has more than one remaining address after ignoring the Astral inbox address.
* Does **not** bind from CC, BCC, Reply-To, Delivered-To, Resent-To, or X-Forwarded-* headers.
* Does **not** invent a second candidate lookup or new match homes.
* Does **not** require a new Manage Email column or chrome — existing match indicator is enough. Unmatched browse stays as it is.
* Does **not** change ingest, scrape, dedupe, create, archive, or unbound Trash beyond who counts as bound.
* Does **not** fix Land Meteorite job-record save (**AST-1292**) or other Meteorite ingest bugs.
* Must not break existing From-bind success on Manage Email, gaze_email (including in-flight UAT on **AST-1088**–**AST-1090** / **AST-1106**–**AST-1107**), Land Meteorite, or Avail counts.

## Acceptance criteria

1. A message whose **From** uniquely matches candidate A still binds to A, even if **To** uniquely matches candidate B or matches no one.
2. A message whose **From** does not uniquely match, and whose **To** (after ignoring the Astral inbox address) is a single remaining address that uniquely matches candidate A, binds to A on Manage Email, is eligible for that candidate's gaze_email run and Avail count, and can be Land Meteorite ingested for A.
3. A message whose **From** does not uniquely match and whose **To** is missing, has more than one remaining address after ignoring the Astral inbox, or does not uniquely match one candidate stays unbound: no ingest as matched, no Avail credit.
4. The configured Astral inbox address appearing on To never produces a candidate bind by itself.
5. With `debug=True` on touched bind paths, each message emits Style D found/recorded detail including which header bound and the address used; with `debug=False`, those paths emit no new debug-contract lines.
6. Unauthenticated callers still cannot run inbox list/match or Land Meteorite.

## Dependencies and blockers

none

Adjacent, not blocking: **AST-1292** (Land Meteorite job-record save) is a separate Discussion. From-bind pipeline **AST-1044** / candidate-bound gaze_email / Land Meteorite are already shipped; this epic extends them.

## Open questions

none

## Proposed child tickets

#### 1!: **Mailbox To on list and get payloads - Katherine**

Owns making inbox list/get rows carry the message **To** so bind can see it. Does **not** own the From-then-To decision or debug bind source (child 2).
**Citations:** `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.layers.core-vs-external-bright-line`.

#### 2: **From-then-To bind + debug source - Ada**

After #1, owns the single bind rule: From unique hit wins; otherwise To-bind only when To has a single remaining address after ignoring the Astral inbox; that unique hit binds; every consumer of `candidate_match` and every leftover rematch uses that rule; Style D records which header bound. Does **not** own exposing To on mailbox rows (child 1). Does **not** own ingest/scrape/create beyond who is bound.
**Citations:** `pattern.config.config-block`; `pattern.layers.import-discipline`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.debug-contract-gated`; `astral.standards.dry-and-focused-functions`; `astral.layers.ui-config-driven-business-logic`.

**New patterns:** none

**Monolith check:** Functional scope has 5 capability bullets; 2 proposed children (mailbox To vs bind rule). Not a monolith.

---

## Original brief

We are correctly binding where the email is recognized in the FROM field, but if that does not bind, attempt to bind to the TO address, because I'm autoforwarding certain emails to that inbox now, and the From is not from me when autoforwarded.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1308 (parent) | ftr/AST-1308-email-bind-where-email-is-in-the-to-field-alone |
| AST-1312 | sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads |
| AST-1313 | sub/AST-1308/AST-1313-from-then-to-bind-debug-source |

**Epic worktree:** `astral-AST-1308/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/dc27a0a772a2f21507705b44582cefd7/df2ef60b-5760-4e3a-ac9f-06f8809e7bbe/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/dc27a0a772a2f21507705b44582cefd7/7ce68021-2065-42e9-a1cc-da06cf3fe11a/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/e1f3e268-22c1-4a42-9fc4-d5a9ba136148/store.db` |
| Radia | review | `/home/susan/.cursor/chats/dc27a0a772a2f21507705b44582cefd7/af234b69-a48f-41fd-a99d-fb04e7132e44/store.db` |

### Comments

#### chuckles — 2026-08-11T19:14:13.546Z
@susan

Missing before dispatch:

* Open question 1 is still unanswered: when To lists more than one address (after ignoring the Astral inbox address), (a) bind if exactly one candidate uniquely matches among those addresses, or (b) attempt To-bind only when To has a single remaining address?

Reply on the ticket (or edit Open questions to none), then Todo + assignee Chuckles again.

— Chuckles

#### chuckles — 2026-08-11T17:58:54.632Z
@susan

1. When To lists more than one address (after ignoring the Astral inbox address), should we (a) bind if exactly one candidate uniquely matches among those addresses, or (b) attempt To-bind only when To has a single remaining address?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
