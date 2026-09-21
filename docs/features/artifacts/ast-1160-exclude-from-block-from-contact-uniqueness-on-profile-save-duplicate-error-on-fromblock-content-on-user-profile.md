# AST-1160 — Exclude from-block from contact uniqueness on profile save (Duplicate error on fromblock content on user profile)

<!-- linear-archive: AST-1160 archived 2026-08-07 -->

## Linear archive (AST-1160)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1160/exclude-from-block-from-contact-uniqueness-on-profile-save-duplicate  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1158 — Duplicate error on fromblock content on user profile  
**Blocked by / blocks / related:** parent: AST-1158

### Description

## What this implements

Owns making `contact.cover_letter_from_block` a non-uniqueness contact field end-to-end: uniqueness vocabulary must not treat it as an identity token, and Candidate Profile save must allow identical from-block text across candidates while keeping real identity collisions hard-fail. Does **not** own Print Cover Letter (**AST-1157**), from-block template/allowlist/help, or uniqueness rules for email/phone/GitHub/LinkedIn/websites/Slack.

## In scope

- [ ] `pattern.config.config-block` — uniqueness stays in `CANDIDATE_CONTACT_UNIQUENESS_CONFIG`; from-block owned by `COVER_FROM_BLOCK_CONFIG`
- [ ] `astral.config.config-source-of-truth` — which fields are uniqueness tokens lives in config; exclusion assert tied to `COVER_FROM_BLOCK_CONFIG["contact_key"]`
- [ ] `astral.standards.no-hardcoded-sets` — do not invent an inline from-block uniqueness set
- [ ] `astral.standards.in-scope-only` — profile from-block uniqueness exclusion only
- [ ] `astral.standards.dry-and-focused-functions` — reuse AST-1080 `_enforce_contact_uniqueness`; no second save validator
- [ ] `astral.standards.debug-contract-gated` — Style D only when `debug=True`; no new lines when `debug=False`
- [ ] `astral.layers.import-direction` — UI stays thin; gate remains core (`candidate.py` + `config.py` only)

## Considered but excluded

- [ ] Print Cover Letter live from-block resolve/expand — **AST-1157** (sibling / adjacent)
- [ ] `COVER_FROM_BLOCK_CONFIG` default template / allowlist / `|`→`•` / authoring help / session chrome — AST-1147–1149 (done)
- [ ] Softening uniqueness for email / phone / GitHub / LinkedIn / websites / Slack / extra emails — AST-1045 / AST-1079 / AST-1080 / AST-1095
- [ ] Redesigning full-blob / cross-path identity toasts that can surface after a From-block edit — parent Boundaries; escalate on AST-1158 if UX change wanted
- [ ] Database UNIQUE on from-block — none exists; do not invent
- [ ] New `non_uniqueness_contact_keys` config tuple — omission + assert against `contact_key` is the contract (no parallel deny-list)
- [ ] Unreachable defensive collector skip after import-time assert — comment-only invariant (Joan round=1)
- [ ] Candidate Profile layout redesign / Flask or React edits — not required for this gate
- [ ] `tests/` / `docs/test-bible/**` — Betty

## Acceptance criteria

- [ ] Two live candidates can each save the **same** non-empty Cover Letter From authoring string (including the default token template text); both profile saves succeed and GET shows that string on each candidate.
- [ ] Saving a profile whose from-block matches another candidate’s from-block does **not** return the cross-candidate duplicate-contact error and does not toast as a uniqueness collision.
- [ ] Saving a profile that reuses another candidate’s identity email / phone / GitHub / LinkedIn / website / Slack user id still fails with the existing toast-ready duplicate-contact error (from-block fix does not bypass the gate).
- [ ] With `debug=True` on the touched uniqueness/save path, logs show found/recorded uniqueness-token behavior under Style D index headers and do not list from-block text as a uniqueness token; no new debug-contract lines when `debug=False`.

## Boundaries

Does **not** own Print Cover Letter (**AST-1157**), from-block template/allowlist/help, or uniqueness rules for email/phone/GitHub/LinkedIn/websites/Slack. Does **not** add a database UNIQUE on from-block.

## Notes for planning

Sibling of **AST-1157** (Print live from-block) — adjacent, not a blocker. Parent uniqueness contract: AST-1045 / AST-1079 / AST-1080. Stage 0 on tip: identical from-block alone does not raise; lock is drift-proof assert + comment.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1158-duplicate-error-on-fromblock-content-on-user-profile`, child `sub/AST-1158/AST-1160-exclude-from-block-from-contact-uniqueness-on-profile-save`. Created at dispatch-parent.

### Comments

#### joan — 2026-08-03T06:25:28.718Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1160
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1158/AST-1160-exclude-from-block-from-contact-uniqueness-on-profile-save` @ `e1ee8421` (doc-only delta from `8e3c4dd8`; no `src/` commits at plan stage — verified)

**Statutes:** 18 universal + 38 scoped considered, 9 scoped excluded (layers/paths) — all `conforms`; `astral.standards.dry-and-focused-functions` moves from `needs-discussion` to `conforms` now that the dead collector skip is gone. Files Changed layers/paths are unchanged from revision 0, so the matched set is unchanged. Per-statute verdicts and the considered/excluded list are scored in-session per R7.

## Traceability

AC1→S0,S1; AC2→S0,S1; AC3→S0,S1; AC4→S1 — no unmapped AC; S0 maps to parent Purpose verification, S1 to Functional scope bullet 2 + Architectural definition, no orphan stage.

## Round 1 findings — both cleared

**fix-now (reproduction gap) → resolved.** Stage 0 now records the tip attempt with a four-case result table and states the conclusion plainly: identical from-block alone does not raise, from-block is not a token source, and the toast an operator sees after a From-block edit is most plausibly a pre-existing identity collision on the full-blob save. Stage 1 is reframed as a drift-proof lock rather than a runtime fix, and softening the identity gate is fenced out with a pointer to AST-1158. That is the honest resolution — the plan no longer claims credit for behavior that already holds.

**discuss (unreachable collector skip) → resolved.** Stage 1 step 3 is now docstring plus a one-line invariant comment, with the assert as sole enforcement, and it explicitly avoids importing `COVER_FROM_BLOCK_CONFIG` just to feed a comment (no unused import).

## Findings

**discuss — the parent's reported symptom remains unexplained, and this child cannot close it.** Parent Purpose asserts a live from-block failure; Stage 0 shows that failure does not exist on tip as a from-block uniqueness token. This child is correctly bounded (parent Boundaries forbid softening identity uniqueness), so approving it does **not** mean Susan's original report is fixed. Carry this into AST-1158 UAT: if the operator toast came from the full-blob cross-path identity match, it will still reproduce after this child lands, and the UX decision belongs to the parent. No action for Ada on AST-1160.

**acceptable (no action):** self-assessment is honest — `Risk: low` is now earned (deliverable is one import-time assert plus comments; identity paths untouched; assert fails closed on drift) and `Conf: high` rests on recorded Stage 0 evidence rather than an unverified premise; assert placement re-verified (`COVER_FROM_BLOCK_CONFIG` at `config.py` 1175 precedes the uniqueness block at 1444); `astral.layers.import-direction` conforms (core → utils only; utils gains no imports); `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets` conform (exclusion reads `contact_key`, no parallel deny-list); `astral.standards.debug-contract-gated` conforms (existing Style D untouched, nothing new when `debug=False`); `astral.standards.names-not-ticket-ids` conforms (ticket ids in prose only); Boundaries respected — no Print Cover Letter, template/allowlist, identity softening, DB UNIQUE, or `tests/` edits.

R7 satisfied — status → Plan Approved. Rounds completed: 1 of 2.

context_tokens≈65000

— Joan

#### ada — 2026-08-03T06:23:34.197Z
[plan-discuss] round=1 reply

Addressed Joan REVISE on tip `e1ee8421`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1158/AST-1160-exclude-from-block-from-contact-uniqueness-on-profile-save/docs/features/artifacts/ast-1160-exclude-from-block-from-contact-uniqueness-on-profile-save.md

**Delta**
1. **fix-now (reproduction):** Added Stage 0 with tip results — identical from-block + distinct identity → no raise; from-block text equal to other email → no raise; shared / cross-path identity on full-blob merge → existing toast. Conclusion: reported From-block toast does not reproduce as a from-block uniqueness token on tip; plausible operator misread is pre-existing identity collision on full-blob save. Out of scope to soften (parent Boundaries); escalate on AST-1158 if UX change wanted. Stage 1 reframed as drift-proof lock only.
2. **discuss (dead skip):** Removed unreachable collector `continue`; Stage 1 core work is docstring + one-line invariant comment only. Assert remains the enforcement.

**Self-assessment (updated)**
- **Scope:** Single-Component
- **Conf:** high — Stage 0 recorded; lock is assert + comment
- **Risk:** low — identity paths untouched; fail-closed on config drift

#### joan — 2026-08-03T06:16:41.268Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1160
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1158/AST-1160-exclude-from-block-from-contact-uniqueness-on-profile-save` @ `8e3c4dd8`

**Statutes:** 18 universal + 38 scoped considered, 9 scoped excluded (layers/paths) — all `conforms` except the DRY item below (`needs-discussion`). Per-statute verdicts and the considered/excluded list are scored in-session per R7.

## Traceability

AC1→S1; AC2→S1; AC3→S1; AC4→S1 — no unmapped AC, no orphan stage (single-stage plan).

## Findings

**fix-now — the plan's own baseline contradicts the parent Purpose, and there is no reproduction step.** *Location: plan § Baseline (planner note) + Stage 1 step 4.*

Parent Purpose states Candidate Profile is **currently** refusing / toasting duplicate on from-block content. The plan states from-block is already omitted from every uniqueness path tuple on tip. I verified the plan's claim on the epic worktree: `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` (`src/utils/config.py` 1444–1480) holds no from-block path, `_collect_uniqueness_tokens_from_candidate` (`src/core/candidate.py` 325–344) iterates only those tuples, and `_enforce_contact_uniqueness` at line 470 is the only site that raises the duplicate-contact error. So as written, Stage 1 changes **no runtime behavior** — AC1 and AC2 already pass before it lands. Every AC goes green in UAT whether or not the reported bug is fixed.

One concrete mechanism the plan should rule in or out first: Profile save posts the whole contact blob, and `save_candidate_data` re-runs the gate over the merged blob (`candidate.py` 795). A from-block-only edit therefore still hard-fails on any **pre-existing identity collision** — and cross-candidate matching in `_find_cross_candidate_contact_collision` keys on token *value* with no path binding, so e.g. one candidate's `contact.reply_email` equal to another's `contact_email` trips it. To an operator that reads exactly as "I changed the From block and got a duplicate error." If that is what produced the reported toast, AC1/AC2 still fail in the field after this plan ships.

*Recommendation:* add a Stage 0 that attempts the reported failure on tip and records the outcome in the plan. If it does not reproduce, say so explicitly and name what produced the reported toast (stale deploy vs. the full-blob identity path above). If it is the full-blob path, that is a scope question for AST-1158 — do not widen silently, and note that parent Boundaries forbid softening identity uniqueness.

**discuss — the defensive collector skip is unreachable by construction.** *Location: Stage 1 step 3; statute `astral.standards.dry-and-focused-functions` → needs-discussion.*

With the new import-time assert in place, the from-block path can never appear in the tuples the collector iterates, so `path == f"contact.{COVER_FROM_BLOCK_CONFIG['contact_key']}"` can never be true — it is permanently dead. *Recommendation:* rely on the assert and document the invariant in a one-line comment at the collector, or state in the plan why a branch that cannot fire earns its keep.

**acceptable (no action):** assert placement is sound — `COVER_FROM_BLOCK_CONFIG` (config.py 1175) precedes the uniqueness block (1444), so Stage 1 step 2 has no import-order hazard; `astral.layers.import-direction` conforms (core → utils only, UI and data untouched); `astral.standards.debug-contract-gated` conforms (existing Style D stays under `debug`, no new lines when `debug=False`); ticket ids appear only in comments and docstrings, which `astral.standards.names-not-ticket-ids` carves out; Boundaries respected — no Print Cover Letter, template/allowlist, identity softening, DB UNIQUE, or `tests/` edits.

context_tokens≈48000

— Joan

#### ada — 2026-08-03T06:10:40.472Z
Plan published on `origin/sub/AST-1158/AST-1160-exclude-from-block-from-contact-uniqueness-on-profile-save` @ `8e3c4dd8`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1158/AST-1160-exclude-from-block-from-contact-uniqueness-on-profile-save/docs/features/artifacts/ast-1160-exclude-from-block-from-contact-uniqueness-on-profile-save.md

**Self-assessment**
- **Scope:** Single-Component — utils uniqueness vocabulary lock + core collector skip on the existing AST-1080 save gate; no UI/data/schema.
- **Conf:** high — tip already omits from-block from path tuples; plan makes exclusion explicit via `COVER_FROM_BLOCK_CONFIG["contact_key"]` assert and a defensive collector skip.
- **Risk:** Medium — a wrong change could weaken identity uniqueness or leave a false from-block collision; identity paths stay untouched.

---

_Implementation detail may live in git history on `origin/dev`._
