# AST-1157 — Print Cover Letter does not use candidate fromblock template
**Component:** artifacts  
**Children:** AST-1159  
**Linear archived:** AST-1157 2026-08-07; AST-1159 2026-08-07

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-07 18:26 | AST-1159 | docs | `30cfb4775` | docs(AST-1159): archive Linear issue content |
| 2026-08-07 18:28 | AST-1157 | docs | `e256714c5` | docs(AST-1157): archive Linear issue content |

_No product, test, or resolve commits exist for either ticket — the epic was canceled at the plan-discuss stage before any build landed (see Epic Comments and child Resolution below)._

## Epic — AST-1157
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1157/print-cover-letter-does-not-use-candidate-fromblock-template · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: related AST-1147, AST-1124, AST-1145, AST-1149_

### Purpose

Print Cover Letter still shows a name + email-only `fromBlock` instead of the candidate profile's current from-block contract (saved custom text, or the default token template when unset). After AST-1124 / AST-1145, operators expect Print to always resolve from the live candidate profile so header format and contact segments stay current.

### Functional scope

* When the operator opens **Print Cover Letter** for a job, the cover HTML `fromBlock` is produced at print time from the **live** candidate profile — not a stale or hard-coded name/email header.
* Resolution follows the established from-block contract: non-empty saved cover from-block wins; otherwise the config default token template is used; allowlisted tokens expand to current candidate values; authoring `|` becomes the emit separator; empty segments (and their adjacent separators) are dropped so print never shows dangling separators or unresolved allowlisted empties.
* Printed `fromBlock` shows **expanded** values (not literal `{$TOKEN}` strings). After the operator edits the profile from-block (or contact fields those tokens read), the next Print Cover Letter reflects that state without a server restart.
* When the print/build path runs with `debug=True`, debug output records what from-block source was chosen and what text was found vs recorded for emit (Style D / AST-538 contract).

### Architectural definition

* **Patterns to reuse:** `pattern.config.config-block` — from-block default template, allowlist, separators, and empty-segment policy stay in `COVER_FROM_BLOCK_CONFIG` (no new inline literals in emit).
* **New patterns proposed:** none.
* **Applicable statutes:** `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only` (Print Cover Letter from-block only); `astral.standards.dry-and-focused-functions` (reuse shared resolve/expand; do not fork a second header builder); `astral.standards.debug-contract-gated`; `astral.layers.import-direction` (UI thin; resolve/emit in core).

### Boundaries

* Does **not** change the default token template string, allowlist, or authoring help copy (AST-1147 / AST-1149).
* Does **not** own Candidate Profile validation / duplicate-error UX for from-block (sibling AST-1158).
* Does **not** redesign SomersetCover CSS/DOM, signature-image token behavior, resume Print header/contact strip, or Session Admin Cover Letter form chrome (session empty→candidate resolve stays as already shipped unless Print and session share one broken path — then fix the shared resolve, not session UI).
* Does **not** invent brief aliases (`RESUME_LOCATION`, `RESUME_EMAIL`, `CANDIDATE_MOBLE`, etc.).
* Must not break job cover body/subject/signature mapping or resume Print.

### Acceptance criteria

1. For a job with cover letter content, **Print Cover Letter** HTML includes a SomersetCover `fromBlock` whose text equals live resolve of that job's candidate: saved profile from-block expanded, or default template expanded when the profile field is empty/whitespace.
2. With a non-empty saved profile from-block that uses allowlisted tokens and `|`, print shows expanded values and emit separators — not the pre-contract name+email-only header shape when the resolved text differs.
3. With an empty profile from-block, print matches expand of the config default template against current candidate name/contact (empty segments omitted per policy).
4. After changing the profile from-block (or token source fields) and saving, the next Print Cover Letter shows the new resolved text.
5. With `debug=True` on the touched print/build path, logs show from-block source and found/recorded text detail under Style D index headers; no new debug-contract lines when `debug=False`.

### Dependencies and blockers

none. Prior from-block epics (AST-1124, AST-1145) are Done. Adjacent Discussion AST-1158 (profile from-block duplicate error) is out of scope and not a blocker.

### Open questions

none.

### Proposed child tickets

**1: Job Print Cover Letter live from-block — Hedy** — Owns `/candidate/cover/<job_id>` (JAR **Print Cover Letter**) so SomersetCover `fromBlock` always comes from live candidate from-block resolve/expand at print time, with Style D debug on the touched `debug=` path. Does **not** own profile validation UX (AST-1158), session Admin form chrome, resume print header, or SomersetCover CSS redesign.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

Monolith check: Functional scope has 3 capabilities and 1 proposed child — intentional; load + resolve + emit must ship as one vertical slice for Print Cover Letter UAT.

### Original brief

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

#### Comments

##### susan — 2026-08-03T06:29:33.474Z
@chuckles Go ahead and cancel this ticket. Joan caught the problem as user-error in AST-1158. The issue was that the actual existing email for the test candidate was already saved to another record before the deduping was in place, so it was complaining about the email, not the fromblock at all.

##### chuckles — 2026-08-03T06:32:31.404Z
[check-linear] Canceled — user-error (email collision, not from-block)

_(The Linear "Status at archive" recorded above is Archive, matching the standard archive-purge label used across this rollup — the ticket's disposition at close, per Susan's comment, was cancellation as a misdiagnosis.)_

### Files changed (plan vs actual)

_No commit trail on the parent at all — the epic never reached build._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1159 — Job Print Cover Letter live from-block
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1159/job-print-cover-letter-live-from-block-print-cover-letter-does-not-use · Status at archive: Archive · Project: Astral Artifacts · Assignee: susan · Priority / estimate: Urgent / — · Blocked by / blocks / related: parent: AST-1157_

#### What this implements

Owns `/candidate/cover/<job_id>` (JAR **Print Cover Letter**) so SomersetCover `fromBlock` always comes from live candidate from-block resolve/expand at print time, with Style D debug on the touched `debug=` path. Does **not** own profile validation UX (AST-1158), session Admin form chrome, resume print header, or SomersetCover CSS redesign.

#### Acceptance criteria

Parent AC1–5 (live resolve on Print, token/`|`/empty-segment behavior, default-template match on empty from-block, live reflect of profile edits, Style D debug).

#### Boundaries

Does **not** own Candidate Profile validation / duplicate-error UX (AST-1158), session Admin Cover Letter form chrome, resume Print header/contact strip, SomersetCover CSS redesign, default token template / allowlist / authoring help (AST-1147 / AST-1149), or brief aliases.

#### Notes for planning

Reuse shared `resolve_cover_from_block` / `expand_cover_from_block_text` and `COVER_FROM_BLOCK_CONFIG` — fix whatever keeps Print Cover Letter from emitting live profile resolve. One vertical slice: load + resolve + emit.

#### Plan-discuss round 1 — REVISE (Joan, 2026-08-03T06:15:38.897Z)

**fix-now — Stage 1 (live DB-row resolve) is behaviorally inert; the root cause is unverified.** On the publish ref, `build_cover_letter` already loads the candidate fresh per request (`candidate_mod.get_candidate` → `database.get_candidate`, no cache), and `_candidate_for_cover_from_block(_coerce_candidate_blob(row))` already carries `full` (from the `_full` column) plus the *same* `candidate_data.contact` dict from that row. Every allowlisted token resolves from exactly those two places — `COVER_FROM_BLOCK_CONFIG["allowed_token_ids"]` is `FULL_NAME`/`LOCATION`/`CONTACT_EMAIL`/`PHONE`, and `TOKEN_SOURCES` maps them to `full`, `contact.location`, `contact.contact_email`, `contact.phone`. Passing `row` instead of the shaped dict therefore produces byte-identical `from_res["text"]` — the plan buys Medium regression risk while changing nothing an operator can see, and AC1–AC4 would be "met" by a no-op. **The reported symptom is exactly what the current contract produces when `contact.location` and `contact.phone` are empty:** the default template `{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}` drops the empty segments and emits a name line + email line — which is the HTML in the parent's Original brief. Recommendation: add a Stage 0 that reproduces `GET /candidate/cover/<job_id>` against the publish ref with the real candidate row and states the actual defect (or states that AC1–AC4 already hold on `dev` and the epic is a debug-visibility + verification ticket only). Keep the row-passing change only if Stage 0 shows a token or contact path the shaped helper genuinely drops; otherwise drop it under `in-scope-only`.

**fix-now — Stage 2 step 2 ships three alternative implementations instead of one instruction.** `orch.pipeline.plan-is-bible` requires the engineer to execute stages as written and to stop and escalate on ambiguity — a plan offering a choice guarantees either drift or a stall at build time. Recommendation: state one instruction — `resolve_cover_from_block` emits `found_authoring=` and `recorded_text=` (via `truncate_debug_content`) under its existing Style D index when `debug=True`; `build_cover_letter_from_job` adds exactly `from_block_recorded=truncate_debug_content(from_res["text"])` alongside the existing `from_block_source=` / `from_block_chars=`; public return stays `{"text", "source"}`. Delete the alternatives.

**discuss — Self-Assessment `Conf: high` does not match an unverified diagnosis.** The justification cites that `resolve_cover_from_block` / `expand_cover_from_block_text` / `COVER_FROM_BLOCK_CONFIG` already exist on `dev` — true, but that is evidence the Print path already resolves, not evidence the plan closes the reported gap.

**acceptable — fifth inline copy of the debug-flag parse** follows shipped precedent in `api_contact` / `api_inbox` / `api_intake`; not required to change.

Layer, config, placement, DRY, pattern, and boundary checks otherwise passed.

#### Plan-discuss round 1 reply (Hedy, 2026-08-03T06:17:26.127Z)

1. **fix-now Stage 1 inert row-pass:** added a Stage 0 diagnosis — the shaped helper already carries `full` + the same `contact` dict; allowlisted tokens are byte-identical to a full-row resolve; the parent's name+email HTML matches the default-template empty-segment drop. Dropped the `candidate_row=` / pass-`row` refactor under `in-scope-only`. Ticket product work reduced to AC5 (debug) + verification.
2. **fix-now Stage 2 alternatives:** collapsed to a single instruction — resolve emits `found_authoring=` + `recorded_text=` via `truncate_debug_content`; builder adds only `from_block_recorded=` from `from_res["text"]`; public return stays `{text, source}`. Alternatives deleted.
3. **discuss Conf:** restated after Stage 0 — Conf high (AC1–AC4 already hold; remaining work is an unambiguous AC5 wire); Risk low (additive debug only).

#### Escalation — the bug premise itself (Joan, 2026-08-03T06:20:29.103Z)

Both round-1 fix-nows cleared. Joan independently reached the same conclusion as Stage 0: **AC1–AC4 already hold**, and the header in the Original brief is exactly the default template expanding with empty `location` / `phone` segments dropped.

That conclusion rests on one fact nobody on the engineering side could check: whether the candidate profile actually printed from had **Location** and **Phone** filled in. Stage 0's step 4 (call the route against a real row) was written as optional because the local `data/astral.db` had zero candidate/job/company rows to test against — the deployed data was only visible to Susan. The two outcomes were very different: if Location and Phone were empty on that profile, the plan was right, there was no product defect, and the ticket would ship as Style D debug visibility plus verification (approve-ready as-is); if they were filled, the contract was dropping segments that should have rendered, the reported symptom was unexplained, and Stages 1–2 would ship debug lines while Print Cover Letter kept showing the same header at UAT — a re-plan, not a tweak. Joan escalated to Susan directly per `orch.pipeline.call-susan-for-product-decisions` rather than running another discuss round, asking whether Contact Information → Location and Phone were filled in or blank on the profile used for that Print Cover Letter.

**Outcome:** Susan's answer (in the parent AST-1157 comments) confirmed the real defect was elsewhere — a duplicate-email validation collision from before contact deduping existed, tracked at AST-1158 — not a from-block/Print bug at all. The ticket was canceled on that basis; no Stage 0–2 code was built.

#### Files changed (plan vs actual)

_No commit trail — the plan reached ESCALATE and was canceled before any `code()` / `test()` / `resolve()` commit landed._
