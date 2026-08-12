# AST-1159 — Job Print Cover Letter live from-block (Print Cover Letter does not use candidate fromblock template)

<!-- linear-archive: AST-1159 archived 2026-08-07 -->

## Linear archive (AST-1159)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1159/job-print-cover-letter-live-from-block-print-cover-letter-does-not-use  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** AST-1157 — Print Cover Letter does not use candidate fromblock template  
**Blocked by / blocks / related:** parent: AST-1157

### Description

## What this implements

Owns `/candidate/cover/<job_id>` (JAR **Print Cover Letter**) so SomersetCover `fromBlock` always comes from live candidate from-block resolve/expand at print time, with Style D debug on the touched `debug=` path. Does **not** own profile validation UX (**AST-1158**), session Admin form chrome, resume print header, or SomersetCover CSS redesign.

## In scope

- [ ] `pattern.config.config-block` — consume `COVER_FROM_BLOCK_CONFIG` for template/source/separators (no new inline literals in emit)
- [ ] `astral.config.config-source-of-truth` — config owns from-block template/policy; builder/UI do not redefine
- [ ] `astral.standards.no-hardcoded-sets` — no ad-hoc name+email header composition beside the contract
- [ ] `astral.standards.dry-and-focused-functions` — reuse `resolve_cover_from_block` / `expand_cover_from_block_text`; no second header builder
- [ ] `astral.standards.debug-contract-gated` — Style D found/recorded + builder details only when `debug=True`
- [ ] `astral.standards.in-scope-only` — Print Cover Letter from-block vertical slice only
- [ ] `astral.layers.import-direction` — UI thin (`api_resume_html` → builder); resolve/emit in core

## Considered but excluded

- [ ] Profile from-block uniqueness / duplicate-error UX — `src/core/candidate.py` uniqueness gate + `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` (**AST-1158** / **AST-1160**)
- [ ] Session Admin Cover Letter form chrome — `AdminSessionCoverLetter.tsx` / session empty→resolve (**AST-1139**)
- [ ] Default token template / allowlist / authoring help — `COVER_FROM_BLOCK_CONFIG` keys owned by **AST-1147** / **AST-1149** (consume only)
- [ ] Resume Print header/contact strip — `_emit_html_document` / `_apply_contact_to_render_dict`
- [ ] SomersetCover CSS/DOM redesign — shared emit helper CSS stays as shipped
- [ ] Brief aliases (`RESUME_LOCATION`, `RESUME_EMAIL`, `CANDIDATE_MOBLE`, etc.) — never
- [ ] `tests/`, `docs/test-bible/**` — Betty

## Acceptance criteria

1. For a job with cover letter content, **Print Cover Letter** HTML includes a SomersetCover `fromBlock` whose text equals live resolve of that job’s candidate: saved profile from-block expanded, or default template expanded when the profile field is empty/whitespace.
2. With a non-empty saved profile from-block that uses allowlisted tokens and `|`, print shows expanded values and emit separators — not the pre-contract name+email-only header shape when the resolved text differs.
3. With an empty profile from-block, print matches expand of the config default template against current candidate name/contact (empty segments omitted per policy).
4. After changing the profile from-block (or token source fields) and saving, the next Print Cover Letter shows the new resolved text.
5. With `debug=True` on the touched print/build path, logs show from-block source and found/recorded text detail under Style D index headers; no new debug-contract lines when `debug=False`.

## Boundaries

Does **not** own Candidate Profile validation / duplicate-error UX (**AST-1158**), session Admin Cover Letter form chrome, resume Print header/contact strip, SomersetCover CSS redesign, default token template / allowlist / authoring help (AST-1147 / AST-1149), or brief aliases.

## Notes for planning

Reuse shared `resolve_cover_from_block` / `expand_cover_from_block_text` and `COVER_FROM_BLOCK_CONFIG` — fix whatever keeps Print Cover Letter from emitting live profile resolve. One vertical slice: load + resolve + emit.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1157-print-cover-letter-does-not-use-candidate-fromblock-template`, child `sub/AST-1157/AST-1159-job-print-cover-letter-live-from-block`. Created at dispatch-parent.

### Comments

#### joan — 2026-08-03T06:20:29.103Z
[plan-discuss] escalate
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1159
**Overall:** ESCALATE
**Publish ref:** `sub/AST-1157/AST-1159-job-print-cover-letter-live-from-block` @ `4fdc9fc4`

## Traceability

AC1→S0 (verification, no code change); AC2→S0; AC3→S0; AC4→S0; AC5→S1–S2. No orphan stages.

## Round=1 findings — both fix-nows cleared

**resolved — inert row-pass.** Stage 0 now states the parity proof, the `candidate_row=` / pass-`row` refactor is dropped and listed in the out-of-files table, and Files Changed is debug-only. `astral.standards.in-scope-only` conforms.

**resolved — Stage 2 alternatives.** The Style D stage is now one instruction: resolve emits `found_authoring=` + `recorded_text=`, builder adds only `from_block_recorded=`, public return stays `{"text", "source"}`. I checked the mechanics: `truncate_debug_content` returns `list[str]`, so the per-line loop is executable as written and matches the existing call sites the plan names (`src/core/inbox.py`, `src/core/contact.py`). The parenthetical about prefixing the first line is cosmetic latitude, not a fork — `acceptable`.

**resolved — Self-Assessment.** Conf `high` / Risk `low` now match an additive debug-only change.

## Escalation — the bug premise itself

Stage 0 concludes option (B): AC1–AC4 already hold, and the header in your Original brief is the default template expanding with empty `location` / `phone` segments dropped. I independently reached the same conclusion in round 1, and the plan's code-path proof is sound.

But that conclusion rests on one fact nobody on this side can check: whether the candidate profile you printed from actually has **Location** and **Phone** filled in. Stage 0 step 4 (call the route against a real row) is written as optional because the local `data/astral.db` has zero candidate, job, and company rows, so there is nothing here to print. The deployed data is only visible to you.

The two outcomes are very different:

- **If Location and Phone are empty on that profile** — the plan is right, there is no product defect, and this ticket is Style D debug visibility plus verification. It is otherwise approve-ready today.
- **If Location and Phone are filled** — then the contract is dropping segments that should have rendered, the reported symptom is unexplained, and Stages 1–2 would ship debug lines while Print Cover Letter still shows the same name+email header at UAT. That is a re-plan, not a tweak.

I can't resolve this from the repo, and it decides whether the epic ships a fix or ships logging, so per `orch.pipeline.call-susan-for-product-decisions` it comes to you rather than through another discuss round.

@susan — on the Candidate Profile you used for that Print Cover Letter, are **Contact Information → Location** and **Phone** filled in, or blank? (Profile writes them to `contact.location` / `contact.phone`, which is exactly where `{$LOCATION}` and `{$PHONE}` read — so blank fields legitimately produce the name+email header you pasted.) If they are blank, this plan is good to approve as-is. If they are filled, AST-1159 needs a re-plan against the real defect.

No statute violations remain in the plan text; layer, config, placement, DRY, debug-gating, boundary and test-tree checks all pass.

**Considered:** universal set (all `tier: universal` active statutes) plus scoped statutes matching layers `core`/`ui` and paths `src/**`; per-statute verdicts and the considered/excluded list scored in-session (plan-rubric.v1 R7, slim comment).

context_tokens≈72000

— Joan

#### hedy — 2026-08-03T06:17:26.127Z
[plan-discuss] round=1 reply

Plan tip: https://github.com/susansomerset/astral/blob/sub/AST-1157/AST-1159-job-print-cover-letter-live-from-block/docs/features/artifacts/ast-1159-job-print-cover-letter-live-from-block.md

Delta vs round=1 concern:
1. **fix-now Stage 1 inert row-pass** — Added Stage 0 diagnosis: shaped helper already carries `full` + same `contact` dict; allowlisted tokens are byte-identical to full-row resolve; parent name+email HTML matches default-template empty-segment drop. Dropped the `candidate_row=` / pass-`row` refactor under `in-scope-only`. Ticket product work is AC5 + verification.
2. **fix-now Stage 2 alternatives** — Single instruction: resolve emits `found_authoring=` + `recorded_text=` via `truncate_debug_content`; builder adds only `from_block_recorded=` from `from_res["text"]`; public return stays `{text, source}`. Alternatives deleted.
3. **discuss Conf** — Restated after Stage 0: Conf high (AC1–AC4 already hold; remaining work is unambiguous AC5 wire); Risk low (additive debug only).

Status left **Plan Discuss** for Joan re-validate.

#### joan — 2026-08-03T06:15:38.897Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1159
**Overall:** REVISE
**Publish ref:** `sub/AST-1157/AST-1159-job-print-cover-letter-live-from-block` @ `6907f824`

## Traceability

AC1→S1; AC2→S1; AC3→S1; AC4→S1; AC5→S2–S3. AC1–AC4 map only to Stage 1, and Stage 1 as written cannot change emitted output — see fix-now 1.

## Findings

**fix-now — Stage 1 (live DB-row resolve) is behaviorally inert; the root cause is unverified.**
Location: plan Stage 1 steps 2a–2c + ⚠️ Decision.
On the publish ref, `build_cover_letter` already loads the candidate fresh per request (`candidate_mod.get_candidate` → `database.get_candidate`, which returns a parsed dict, no cache), and `_candidate_for_cover_from_block(_coerce_candidate_blob(row))` already carries `full` (from the `_full` column) plus the *same* `candidate_data.contact` dict from that row. Every allowlisted token resolves from exactly those two places — `COVER_FROM_BLOCK_CONFIG["allowed_token_ids"]` is `FULL_NAME`/`LOCATION`/`CONTACT_EMAIL`/`PHONE`, and `TOKEN_SOURCES` maps them to `full`, `contact.location`, `contact.contact_email`, `contact.phone`. Passing `row` instead of the shaped dict therefore produces byte-identical `from_res["text"]`; the only extra keys the row path adds (`pronouns`, `context`, `artifacts`) are not on the allowlist. So the plan buys the Medium regression risk it names in Self-Assessment while changing nothing an operator can see, and AC1–AC4 would be "met" by a no-op.
Also note the reported symptom is exactly what the current contract produces when `contact.location` and `contact.phone` are empty: the default template `{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}` drops the empty segments and emits a name line + email line, which is the HTML in the parent's Original brief.
Recommendation: add a Stage 0 that reproduces `GET /candidate/cover/<job_id>` against the publish ref with the real candidate row and states the actual defect (or states that AC1–AC4 already hold on `dev` and that the epic is a debug-visibility + verification ticket). Keep the row-passing change only if Stage 0 shows a token or contact path the shaped helper genuinely drops; otherwise drop it under `astral.standards.in-scope-only` (unplanned refactor).

**fix-now — Stage 2 step 2 ships three alternative implementations instead of one instruction.**
Location: plan Stage 2, step 2 bullet `from_block_found=` and the "Minimum builder requirement" bullet.
The step reads "either … or … — prefer not expanding the public return shape … only if needed; simplest: …". `orch.pipeline.plan-is-bible` requires the engineer to execute stages as written and to *stop and escalate* on ambiguity, so a plan that offers a choice guarantees either drift or a stall at build time.
Recommendation: state one instruction. Suggested: `resolve_cover_from_block` emits `found_authoring=` and `recorded_text=` (both via `truncate_debug_content`) under its existing Style D index when `debug=True`; `build_cover_letter_from_job` adds exactly `from_block_recorded=truncate_debug_content(from_res["text"])` alongside the existing `from_block_source=` / `from_block_chars=`; public return stays `{"text", "source"}`. Delete the alternatives.

**discuss — Self-Assessment `Conf: high` does not match an unverified diagnosis.**
The justification cites that `resolve_cover_from_block` / `expand_cover_from_block_text` / `COVER_FROM_BLOCK_CONFIG` already exist on `dev` — true, but that is evidence the Print path already resolves, not evidence the plan closes the reported gap. Re-state Conf after Stage 0 lands.

**acceptable — fifth inline copy of `request.args.get("debug", "").lower() in ("1", "true", "yes")`.**
Stage 3 follows the shipped precedent in `api_contact` / `api_inbox` / `api_intake`, so it is consistent; `api_intake._debug_flag()` is a nicer shape if the engineer wants it, but a shared helper is not required by this ticket.

Layer, config, placement, DRY, pattern and boundary checks otherwise pass: UI stays thin and imports core/utils only, `@require_auth` is retained on `cover_for_job`, no new config literals, no test-tree or `docs/test-bible/**` paths, and the excluded-file table matches the parent Boundaries.

**Considered:** universal set (all `tier: universal` active statutes) plus scoped statutes matching layers `core`/`ui` and paths `src/**`; per-statute verdicts and the considered/excluded list are scored in-session (plan-rubric.v1 R7, slim comment).

context_tokens≈54000

— Joan

#### hedy — 2026-08-03T06:10:35.140Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1157/AST-1159-job-print-cover-letter-live-from-block/docs/features/artifacts/ast-1159-job-print-cover-letter-live-from-block.md

**Scope:** Single-Component — job Print Cover Letter load→resolve→emit in `builder.py` + thin `/candidate/cover` debug wire; Style D found/recorded on existing `resolve_cover_from_block`.

**Conf:** high — `resolve_cover_from_block` / expand / `COVER_FROM_BLOCK_CONFIG` already on `origin/dev`; plan closes live DB-row resolve + debug gaps on the Print path (no second header builder).

**Risk:** Medium — wrong resolve input shape would regress every Print Cover Letter header; mitigated by preferring the live `get_candidate` row with shaped-coerce fallback for direct callers.

---

_Implementation detail may live in git history on `origin/dev`._
