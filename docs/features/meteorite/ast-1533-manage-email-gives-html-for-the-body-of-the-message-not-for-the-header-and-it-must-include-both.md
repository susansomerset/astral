# AST-1533 — Manage Email gives HTML for the body of the message, not for the header, and it must include both.

<!-- linear-archive: AST-1533 archived 2026-09-09 -->

## Linear archive (AST-1533)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1533/manage-email-gives-html-for-the-body-of-the-message-not-for-the-header  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Manage Email’s message popup and the meteorite qualify path both see only the Gmail HTML body today. Operators cannot copy a faithful email snapshot, the modal’s white source pane fights the dark purple admin chrome, and Ruth’s `qualify_meteorite` hop lacks From/To/Subject (and Date when available) so qualification guesses from body text alone. This epic makes one shared header+body HTML shape the operator sees, copies, and the agent receives on email land — without changing non-email ingress.

## Functional scope

1. **Header+body email HTML** — Every email message opened on Manage Email is presented as HTML that includes both the email header fields and the message body, not body-only source.
2. **Copy control** — From that popup, the operator can copy the same header+body HTML to the clipboard in one action.
3. **Dark purple modal chrome** — The email popup’s reading surface uses the admin dark purple background (existing theme tokens), not a white page pane.
4. **Qualify sees headers** — On email land paths that feed meteorite qualification, the agent input includes the same header information (From, To, Subject, and Date when present on the message payload) together with the body — body alone is not enough.

## Component scope

* `src/utils/config.py` — **modified** — extend the inbox email HTML wrapper literals so header fields (not subject-only) are part of the shared template.
* `src/core/inbox.py` — **modified** — assemble header+body HTML for strip/land and for the message get path operators and landers share.
* `src/core/meteorite_email.py` — **modified** — bound email blob uses that same header+body HTML assembly instead of body (or subject-plain prepend) alone.
* `src/external/gmail.py` — **modified** — include Date on the full-message HTML payload when Gmail supplies it so header assembly can use it.
* `src/ui/api/api_inbox.py` — **modified** — message get response exposes the assembled header+body HTML for the Manage Email modal (thin pass-through of core).
* `src/ui/frontend/src/pages/AdminManageEmail.tsx` — **modified** — render assembled HTML, add copy control, keep Land Meteorite / list behavior otherwise.
* `src/ui/frontend/src/App.css` — **modified** — email popup reading surface uses dark purple theme background.

## Technical scope

* `config.py` — extend `INBOX_CREATE_JOB_CONFIG` (or adjacent inbox email HTML literals) so the wrapper carries From/To/Subject/(Date) plus body, still the single source for that shape.
* `inbox.py` — change strip/extract (or a shared helper it owns) to accept and embed those header fields; land-bound email and message-get assembly both call it so UI and qualify see one shape.
* `meteorite_email.py` — change bound-message blob build to use that shared header+body HTML assembly before `stage_meteorite` / land (no parallel subject-only prepend).
* `gmail.py` — extend full-message HTML payload with Date when available from Gmail headers.
* `api_inbox.py` — return the assembled header+body HTML field from core on message get.
* `AdminManageEmail.tsx` — show that assembled HTML in the popup; add a copy control that copies it; no change to land selection semantics.
* `App.css` — restyle `.email-html-source` (or successor) background to the dark purple admin tokens.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — inbox email HTML wrapper literals stay in config, not scattered strings. [https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>)
  * `pattern.layers.import-discipline` — Gmail I/O stays external; core owns HTML assembly and land blob shape; UI calls admin API only. [https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>)
  * `pattern.ui.admin-endpoint` — thin authenticated inbox get; React stays presentational. [https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>)
  * `pattern.ui.shared-button-roles` — copy control uses existing button role vocabulary. [https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.shared-button-roles.md](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.shared-button-roles.md>)
* **New patterns proposed**
  * none
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — wrapper/header field shape in config. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
  * `astral.layers.core-vs-external-bright-line` / `astral.layers.import-direction` — Gmail vs core assembly. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.core-vs-external-bright-line.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.core-vs-external-bright-line.md>) · [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
  * `astral.layers.ui-config-driven-business-logic` / `astral.idioms.require-auth-on-protected-endpoints` — admin get stays thin + auth’d. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) · [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>)
  * `astral.standards.in-scope-only` / `astral.standards.no-hardcoded-sets` / `astral.standards.no-cross-contamination` — email header HTML + Manage Email chrome only; no non-email ingress rewrite. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) · [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) · [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-cross-contamination.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-cross-contamination.md>)
  * `astral.standards.debug-contract-gated` — if land/get debug paths are touched, Style D only when `debug=True`. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>)
  * universal product-code set for any `src/` change.

## Acceptance criteria

1. Opening a message on Manage Email shows HTML that includes From, To, Subject, and Date when present, plus the body — not body-only.
2. A copy control on that popup puts the same header+body HTML on the clipboard.
3. The popup’s email reading surface uses the dark purple admin background (not white).
4. After email land into meteorite qualify, the agent input for that job includes those header fields together with the body (observable in stored/qualify content — not body-only).
5. Non-email meteorite ingress (paste / scrap / non-inbox callers) is unchanged by this epic.
6. Land Meteorite multi-select behavior on Manage Email remains available and is not regressed by the popup/copy work.

## Open questions

none

## Proposed child tickets

#### 1!: **Email header+body HTML for land/qualify - Ada**

Owns the shared header+body HTML assembly and wires every email land path that feeds `stage_meteorite` / qualify so Ruth sees From/To/Subject/(Date) with the body. Does not own Manage Email React chrome or the copy button.
**Citations: **`pattern.config.config-block`, `pattern.layers.import-discipline`, `astral.config.config-source-of-truth`, `astral.layers.core-vs-external-bright-line`, `astral.layers.import-direction`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`, `astral.standards.debug-contract-gated`
**Scope: **`src/utils/config.py` (extend inbox email HTML wrapper literals for From/To/Subject/(Date)+body); `src/core/inbox.py` (shared assemble/strip path for land + message get); `src/core/meteorite_email.py` (bound blob uses shared assembly); `src/external/gmail.py` (Date on full-message HTML payload when available); `src/ui/api/api_inbox.py` (expose assembled header+body HTML on message get)
**Estimate: 3**

#### 2: **Manage Email modal copy + dark purple - Katherine**

Owns the Manage Email popup: render the assembled header+body HTML from the inbox get API, add the copy control, and set the reading-surface background to dark purple theme tokens. Does not own land/qualify blob assembly (after #1).
**Citations: **`pattern.ui.admin-endpoint`, `pattern.ui.shared-button-roles`, `astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`
**Scope: **`src/ui/frontend/src/pages/AdminManageEmail.tsx` (render assembled HTML; copy control); `src/ui/frontend/src/App.css` (dark purple email popup reading surface)
**Estimate: 2**

---

## Original brief

Also, create a copy button and set the background for the email popup modal to the dark purple we use.

The header information for the email MUST ALSO be sent to the agent for meteorite qualification.  Just the body does not give enough information.

### Comments

#### chuckles — 2026-08-29T20:52:15.689Z
AST-1538 REVIEW — Radia discuss: merge-tests bundled AST-1534 test/bible from origin/tests; Katherine resolve.

---

_Implementation detail may live in git history on `origin/dev`._
