# AST-1158 — Duplicate error on fromblock content on user profile
**Component:** artifacts  
**Children:** AST-1160  
**Linear archived:** AST-1158 2026-08-07; AST-1160 2026-08-07

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-07 18:26 | AST-1160 | docs | `e81533a26` | docs(AST-1160): archive Linear issue content |
| 2026-08-07 18:28 | AST-1158 | docs | `87132ac83` | docs(AST-1158): archive Linear issue content |

_No product, test, or resolve commits exist for either ticket — the child reached Plan Approved but the epic was canceled by Susan as an operator mistake before any build landed (see Epic Comments and child plan-discuss thread below)._

## Epic — AST-1158
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1158/duplicate-error-on-fromblock-content-on-user-profile · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: —_

### Purpose

Candidate Profile is refusing (or toasting as duplicate) when operators save **Cover Letter From** text that another candidate already has — including the shared default token template. From-block is free-form authoring text for cover headers, not an identity handle; multiple candidates must be allowed to share the same from-block content. This restores profile save so from-block edits are not blocked by a uniqueness rule that does not belong on that field.

### Functional scope

* Saving Candidate Profile with a non-empty `cover_letter_from_block` (custom authoring text or the default token template) succeeds even when another live candidate already has the same from-block string.
* The contact uniqueness gate continues to treat only true identity fields as uniqueness tokens (emails, phone, GitHub, LinkedIn, websites, Slack user id, and the shared email pool including extra emails). From-block authoring text is explicitly **not** a uniqueness token — same class as signature / location / timezone / title patterns.
* Profile save still hard-fails with the existing toast-ready duplicate contact error when a real identity value collides across candidates; fixing from-block must not weaken that gate.
* When the touched save / uniqueness path runs with `debug=True`, Style D logs still show what uniqueness tokens were found and whether within-dedupe or cross-collision was recorded — without treating from-block text as a token.

### Architectural definition

* **Patterns to reuse:** `pattern.config.config-block` — uniqueness vocabulary stays in `CANDIDATE_CONTACT_UNIQUENESS_CONFIG`; from-block remains owned by `COVER_FROM_BLOCK_CONFIG` / library contact keys as non-identity authoring text.
* **New patterns proposed:** none.
* **Applicable statutes:** `astral.config.config-source-of-truth` (which fields are uniqueness tokens lives in config, not ad-hoc core lists); `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only` (profile from-block uniqueness only); `astral.standards.dry-and-focused-functions` (reuse the AST-1080 gate; do not fork a second save validator); `astral.standards.debug-contract-gated`; `astral.layers.import-direction`.

### Boundaries

* Does **not** own Print Cover Letter live from-block resolve/expand (AST-1157).
* Does **not** change default template, allowlist, `|`→`•` emit, authoring help, or session Admin Cover Letter chrome (AST-1145 / AST-1147–1149).
* Does **not** remove or soften uniqueness for emails, phone, GitHub, LinkedIn, websites, Slack user id, or extra emails (AST-1045 / AST-1079 / AST-1080 / AST-1095).
* Does **not** add a database UNIQUE constraint on from-block (there is none; do not invent one).
* Does **not** redesign Candidate Profile layout beyond whatever is required so save no longer false-fails on from-block content.

### Acceptance criteria

1. Two live candidates can each save the **same** non-empty Cover Letter From authoring string (including the default token template text); both profile saves succeed and GET shows that string on each candidate.
2. Saving a profile whose from-block matches another candidate's from-block does **not** return the cross-candidate duplicate-contact error and does not toast as a uniqueness collision.
3. Saving a profile that reuses another candidate's identity email / phone / GitHub / LinkedIn / website / Slack user id still fails with the existing toast-ready duplicate-contact error (from-block fix does not bypass the gate).
4. With `debug=True` on the touched uniqueness/save path, logs show found/recorded uniqueness-token behavior under Style D index headers and do not list from-block text as a uniqueness token; no new debug-contract lines when `debug=False`.

### Dependencies and blockers

none. Prior uniqueness epics (AST-1045 / AST-1079 / AST-1080) and from-block epics (AST-1137 / AST-1145) are Done. Adjacent AST-1157 (Print Cover Letter live from-block) is out of scope and not a blocker.

### Open questions

none.

### Proposed child tickets

**1: Exclude from-block from contact uniqueness on profile save — Ada** — Owns making `contact.cover_letter_from_block` a non-uniqueness contact field end-to-end: uniqueness vocabulary must not treat it as an identity token, and Candidate Profile save must allow identical from-block text across candidates while keeping real identity collisions hard-fail. Does **not** own Print Cover Letter (AST-1157), from-block template/allowlist/help, or uniqueness rules for email/phone/GitHub/LinkedIn/websites/Slack.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`.

Monolith check: Functional scope has 4 capabilities and 1 proposed child — intentional; config vocabulary + save-gate behavior + profile UAT must ship as one vertical slice so uniqueness cannot drift between config and enforce.

### Original brief

We are dupe-checking the fromblock content, which is not correct. there is no unique constraint on that column.

#### Comments

##### susan — 2026-08-03T05:55:18.995Z
@chuckles did this get stuck?

##### chuckles — 2026-08-03T06:01:06.553Z / 06:02:33.696Z
@susan Not stuck on the product — prior attempts died on MCP/tooling. Defining now. [check-linear] Discussion — not stuck; define in progress.

##### susan — 2026-08-03T06:31:22.381Z
@chuckles Please cancel this ticket. It is not an error, I made a mistake.

##### chuckles — 2026-08-03T06:32:33.083Z
[check-linear] Canceled — operator mistake, not a product bug.

### Files changed (plan vs actual)

_No commit trail on the parent at all — the epic never reached build._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1160 — Exclude from-block from contact uniqueness on profile save
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1160/exclude-from-block-from-contact-uniqueness-on-profile-save-duplicate · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1158_

#### What this implements

Owns making `contact.cover_letter_from_block` a non-uniqueness contact field end-to-end: uniqueness vocabulary must not treat it as an identity token, and Candidate Profile save must allow identical from-block text across candidates while keeping real identity collisions hard-fail. Does **not** own Print Cover Letter (AST-1157), from-block template/allowlist/help, or uniqueness rules for email/phone/GitHub/LinkedIn/websites/Slack.

#### Acceptance criteria

Parent AC1–4 (shared from-block text across candidates saves cleanly; no cross-candidate duplicate toast from from-block; real identity collisions still hard-fail; Style D debug excludes from-block as a token).

#### Boundaries

Does **not** own Print Cover Letter (AST-1157), from-block template/allowlist/help, or uniqueness rules for email/phone/GitHub/LinkedIn/websites/Slack. Does **not** add a database UNIQUE on from-block.

#### Notes for planning

Sibling of AST-1157 (Print live from-block) — adjacent, not a blocker. Parent uniqueness contract: AST-1045 / AST-1079 / AST-1080. Stage 0 on tip: identical from-block alone does not raise; the lock is a drift-proof assert + comment.

#### Plan-discuss round 1 — REVISE (Joan, 2026-08-03T06:16:41.268Z)

**fix-now — the plan's own baseline contradicts the parent Purpose, and there is no reproduction step.** Parent Purpose states Candidate Profile is **currently** refusing / toasting duplicate on from-block content. The plan's own baseline states from-block is already omitted from every uniqueness path tuple on tip. Joan verified this directly on the epic worktree: `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` (`config.py` 1444–1480) holds no from-block path, `_collect_uniqueness_tokens_from_candidate` (`candidate.py` 325–344) iterates only those tuples, and `_enforce_contact_uniqueness` (line 470) is the only site that raises the duplicate-contact error. So as written, Stage 1 would change **no runtime behavior** — AC1 and AC2 already passed before it landed; every AC would go green in UAT whether or not the reported bug was actually fixed.

One concrete mechanism was named for the plan to rule in or out first: Profile save posts the whole contact blob, and `save_candidate_data` re-runs the gate over the merged blob (`candidate.py` 795). A from-block-only edit therefore still hard-fails on any **pre-existing identity collision** — and cross-candidate matching in `_find_cross_candidate_contact_collision` keys on token *value* with no path binding, so e.g. one candidate's `contact.reply_email` equal to another's `contact_email` trips it. To an operator that reads exactly as "I changed the From block and got a duplicate error." If that is what produced the reported toast, AC1/AC2 would still fail in the field after the plan shipped.

Recommendation: add a Stage 0 that attempts the reported failure on tip and records the outcome. If it does not reproduce, say so explicitly and name what produced the reported toast (stale deploy vs. the full-blob identity path above). If it is the full-blob path, that is a scope question for AST-1158 — do not widen silently, and note that parent Boundaries forbid softening identity uniqueness.

**discuss — the defensive collector skip is unreachable by construction.** With the new import-time assert in place, the from-block path can never appear in the tuples the collector iterates, so the collector's from-block skip branch is permanently dead code. Recommendation: rely on the assert and document the invariant in a one-line comment, or justify a branch that can never fire.

**acceptable (no action):** assert placement sound (`COVER_FROM_BLOCK_CONFIG` precedes the uniqueness block); import-direction, debug-contract-gated, and names-not-ticket-ids all conform; Boundaries respected.

#### Plan-discuss round 1 reply (Ada, 2026-08-03T06:23:34.197Z)

1. **fix-now (reproduction):** Added Stage 0 with tip results — identical from-block + distinct identity → no raise; from-block text equal to another candidate's email → no raise; shared / cross-path identity on full-blob merge → existing toast. **Conclusion: the reported From-block toast does not reproduce as a from-block uniqueness token on tip.** Plausible explanation is an operator misread of a pre-existing identity collision surfaced by the full-blob save. Out of scope to soften that gate (parent Boundaries); escalate on AST-1158 if a UX change is wanted. Stage 1 reframed as a drift-proof lock only (not a runtime fix).
2. **discuss (dead skip):** removed the unreachable collector branch; Stage 1 core work is docstring + one-line invariant comment only, with the assert as sole enforcement.

#### R1 resolution — Plan Approved (Joan, 2026-08-03T06:25:28.718Z)

Both round-1 findings resolved: **fix-now** — Stage 0 now records the tip attempt with a four-case result table and states plainly that identical from-block alone does not raise, from-block is not a token source, and the toast an operator sees after a From-block edit is most plausibly a pre-existing identity collision on the full-blob save; Stage 1 is reframed as a drift-proof lock rather than a runtime fix, with identity-gate softening explicitly fenced out to AST-1158 — "the plan no longer claims credit for behavior that already holds." **discuss** — the unreachable collector skip is gone; the assert is sole enforcement, with a docstring/comment only.

**Standing discuss — the parent's reported symptom remains unexplained, and this child cannot close it.** Parent Purpose asserts a live from-block failure; Stage 0 shows that failure does not exist on tip as a from-block uniqueness token. This child is correctly bounded (parent Boundaries forbid softening identity uniqueness), so approving it would **not** mean Susan's original report was fixed. Carried forward into AST-1158 UAT: if the operator toast came from the full-blob cross-path identity match, it would still reproduce after this child landed, and the UX decision belonged to the parent — not to Ada on AST-1160.

R7 satisfied — status → Plan Approved. **Outcome:** Susan confirmed directly on the parent (see Epic Comments above) that the report was her own mistake, not a product bug, and canceled the epic before this Plan-Approved child was ever built.

#### Files changed (plan vs actual)

_No commit trail — the plan reached Plan Approved but was never built; the epic was canceled on Susan's own correction before any `code()` / `test()` / `resolve()` commit landed._
