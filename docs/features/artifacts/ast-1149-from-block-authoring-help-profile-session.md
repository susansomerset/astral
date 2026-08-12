<!-- linear-archive: AST-1149 archived 2026-08-11 -->

## Linear archive (AST-1149)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1149/from-block-authoring-help-on-profile-session-allow-contact-info-tokens  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1145 — Allow contact info tokens and | chars in fromBlock  
**Blocked by / blocks / related:** parent: AST-1145

### Description

## What this implements

Owns user-visible help (and any config-driven placeholder/label copy) so Susan can see that From supports `{$FULL_NAME}` / `{$LOCATION}` / `{$CONTACT_EMAIL}` / `{$PHONE}`, that `|` authors as `•` in print, and what the default template looks like when unset. Does not own resolve math or HTML CSS. Parallel with resolve sibling once AST-1147 field labels/help strings exist.

## In scope

- [X] `pattern.ui.admin-endpoint` — persist via existing candidate profile data PUT; expose authoring chrome via existing `GET /api/ui_config` (no new route)
- [X] `astral.layers.import-direction` / `astral.layers.ui-config-driven-business-logic` — UI renders config-driven help/placeholder; no from-block resolve rules in the page
- [X] `astral.config.config-source-of-truth` — `authoring_help` / `session_authoring_help` (+ placeholder → `default_template`) live in / reference `COVER_FROM_BLOCK_CONFIG`
- [X] `astral.standards.no-hardcoded-sets` — token/separator authoring story not invented as React literals
- [X] `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — profile + session page/component wiring under existing frontend layout
- [X] `astral.standards.in-scope-only` — authoring help chrome only

## Considered but excluded

- [X] `astral.standards.debug-contract-gated` / Style D — AST-1148 resolve/emit path
- [X] `astral.standards.dry-and-focused-functions` / expand path — AST-1148
- [X] AST-1147 token template / allowlist / rewrite / empty-policy keys — already shipped; consume only
- [X] SomersetCover CSS/DOM / `{$SIGNATURE_IMAGE}` — out of epic
- [X] Brief aliases `RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE` — not registered
- [X] New admin or candidate save routes — not needed

## Acceptance criteria

- [X] 2. Saving a custom From block on the candidate profile persists the authoring text (tokens and `|`); a later cover emit resolves tokens and prints `•` instead of `|`. — **help/placeholder make the authoring contract visible.**
- [X] 3. A non-empty typed Session Cover Letter From runs the same token + `|`→`•` + empty-segment rules before emit. — **session help documents the same authoring rules.**

## Boundaries

Does not own resolve math or HTML CSS (AST-1148). Does not own config allowlist/template literals beyond consuming config-driven labels/help (AST-1147).

## Notes for planning

After AST-1147; parallel with AST-1148. Citations above. Plan: profile From is currently invisible (`fields[1]` under Cover Letter Signature) — move to own DATA_SHAPES section + config help.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock`, child `sub/AST-1145/AST-1149-from-block-authoring-help-profile-session`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-03T01:34:30.167Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

validate-sub-log fails on these subjects between origin/ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock and origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session:
- `f8a6525e Merge remote-tracking branch 'origin/sub/.../AST-1149-...' into sub/...`
- `2f56ef35 Merge remote-tracking branch 'origin/sub/.../AST-1148-...' into sub/...` (sibling sub merge — not via merge-child → ftr)
- `765c24af Merge remote-tracking branch 'origin/sub/.../AST-1149-...' into sub/...`

@Katherine Johnson — rewrite/republish `sub/AST-1145/AST-1149-from-block-authoring-help-profile-session` stacked on current `origin/ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock` with canonical `plan|code|merge-tests|test|docs|resolve` subjects only (no `Merge remote-tracking branch`). Do not merge sibling `sub/*` into this publish ref.

— Chuckles

#### radia — 2026-08-03T01:27:44.792Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1149
**Publish ref:** f8a6525e6b7a7965c0a26330f7802190b0c1e466
**Overall:** DISCUSS

## Plan adherence
- Diff matches the plan's 3 stages almost line-for-line: `COVER_FROM_BLOCK_CONFIG` gains `authoring_help`/`session_authoring_help`, own "Cover Letter From" `DATA_SHAPES` section (fixes the real `sec.fields[0]`-only visibility bug), `/api/ui_config` slice, `TabbedTextArea`/`FormFields` typed `help`/`placeholder`, `AdminSessionCoverLetter` config-driven intro + From help.
- No token/`|`/`•` literals invented in TSX; no resolve/emit or CSS touched (AST-1147/AST-1148 boundaries respected); no new routes.
- `SESSION_INTRO_FALLBACK` kept as fetch-failure-only fallback per plan §3.1 — not composed as the live copy.

**Discuss:**
1. Git topology — this sub also merged `origin/sub/AST-1145/AST-1148-...` directly (`2f56ef35`) alongside `origin/ftr/AST-1145-...` (`38caf363`). Traced the merge parent: it only pulled AST-1148's plan-stage commit, before AST-1148's own code existed — confirmed `git diff origin/dev...<tip> -- src/core/candidate.py src/core/builder.py` is empty, so no AST-1148 production code crossed over. No functional impact; flagging so future sibling syncs go through `merge-child` → `ftr` rather than a direct sub-to-sub merge.
2. Straggler (C4) — plan-time Considered-but-excluded lists `astral.standards.debug-contract-gated` and `astral.standards.dry-and-focused-functions` (deferred to AST-1148). Full-set sweep's `applies_when` (ui/utils layer, `src/**`) technically matches this diff too, scoring both `conforms` rather than `not-applicable` — no `debug=` surface or function-complexity growth in the touched lines. Not blocking.

**Pattern conformance:** `pattern.ui.admin-endpoint` — conforms (no new route; reuses `/api/ui_config` + existing candidate data `PUT`).

## Frame diff
(none) — description checkboxes already reflect this ticket's true scope; no adds/moves needed.

**What's solid:** Help/placeholder sourced only from `COVER_FROM_BLOCK_CONFIG`; new own-section `DATA_SHAPES` fix is the correct minimal move per the plan's ⚠️ Decision.

context_tokens≈11000
— Radia

#### betty — 2026-08-03T01:13:23.494Z
1. **Existing / keep:** AST-1139 Session empty-From gating (`AdminSessionCoverLetter — AST-1139`); AST-1025 filled-form paths; AST-1147 token-template config keys.
2. **Broken / revised:** `TestAst1137CoverFromBlockConfig` profile placement — from-block left **Cover Letter Signature** (now signature-only); own section covered by AST-1149.
3. **New:**
   - `TestAst1149CoverFromBlockAuthoringHelpConfig` — `authoring_help` / `session_authoring_help` + **Cover Letter From** DATA_SHAPES section (`placeholder`=`default_template`, `help`=`authoring_help`)
   - `TestSystemAuthRoutes::test_ui_config_includes_cover_from_block`
   - `CandidateProfile — AST-1149` (§6c page: tab help + placeholder + save)
   - `AdminSessionCoverLetter — AST-1149` (§6c page: ui_config intro / From help / placeholder; gating unchanged)
   - `TabbedTextArea` help-above-textarea unit
4. **Bible:** `docs/test-bible/utils/config.md` § AST-1149 (+ AST-1137 note); `docs/test-bible/frontend/pages.md` § AST-1149; `docs/test-bible/ui/api/api_system.md` § AST-1149.
5. **Run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1149CoverFromBlockAuthoringHelpConfig \
  tests/component/utils/test_config.py::TestAst1137CoverFromBlockConfig \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_cover_from_block \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminSessionCoverLetter.test.tsx \
  ../../../tests/component/frontend/components/test_TabbedTextArea.test.tsx
```
6. **Publish:** `origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session` @ `8ee82eb2` — `merge-tests(AST-1149): origin/tests f59289f77ca382937c6b2c2c1a766b7aeb9060a9`
7. **Bible shasums** (publish tip):
- `docs/test-bible/utils/config.md` `a339244187117483084f5a8d60cffb12b75da829`
- `docs/test-bible/frontend/pages.md` `c3f12d4711917a2e17e0e2801369d52644229b25`
- `docs/test-bible/ui/api/api_system.md` `8b11b6dac2282e02e4aea4355bb2fd9c989da283`

#### joan — 2026-08-03T01:03:20.044Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1149
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 unset → default two-line From with `•` | N/A — boundary (AST-1148 emit); Stage 1 surfaces `default_template` as profile/session placeholder only |
| AC2 saving custom From persists authoring text | Stages 1–2 — from-block gets its own `DATA_SHAPES` section so the textarea actually renders and can be saved via existing PUT; placeholder + help make the authoring contract visible |
| AC3 saved From with tokens and `|` emits resolved | N/A — boundary (AST-1148) |
| AC4 cleared From returns to default | N/A — boundary (AST-1148); help copy states empty → default |
| AC5 non-empty typed Session From, same rules | Stage 3 — session intro + From help/placeholder from config document the same rules |
| AC6 Style D debug on resolve/emit | N/A — boundary (AST-1148); correctly excluded |
| AC7 resume/signature unchanged; aliases not resolvable | Stage 1 §5 / Stage 2 §4 — no allowlist, template, or signature edits; no alias strings |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 config help + `DATA_SHAPES` section + `ui_config` slice | Functional scope “Persist across cover letters” / “Session-typed From”; Architectural `pattern.config.config-block`, `pattern.ui.admin-endpoint`; child #3 Proposed ticket |
| Stage 2 profile tab help + placeholder | Functional scope authoring `|` → printed `•` discoverability; parent AC2 |
| Stage 3 session help parity | Functional scope “Session-typed From”; parent AC5 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work in this plan |
| orch.git.commit-vocabulary | conforms | Publishes on the sub ref with standard engineer vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-1145/AST-1149-… |
| orch.git.ftr-sub-topology | conforms | Child ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | AST-1147 keys already merged into the publish tip; no illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1145/… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1145 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Parent Open questions closed; three Decisions recorded rather than improvised |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed table plus exact key/value and code-shape steps |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan entry only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Manual checks flagged as builder notes; tests/ and bible left to Betty |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No grading or confidence config touched |
| astral.config.config-source-of-truth | conforms | `authoring_help` / `session_authoring_help` in config; placeholder references `default_template` by reference, not a second literal |
| astral.config.pass-threshold-vs-score-floor | conforms | Scored-consult keys untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Plain config literals; no env or secret reads |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch or run_next edits |
| astral.dispatch.seed-auto-false | conforms | No dispatch_task seed rows |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src and the plan doc |
| astral.layers.import-direction | conforms | `api_system.py` imports utils config (ui → utils allowed); frontend talks to the API only |
| astral.layers.ui-config-driven-business-logic | conforms | React renders config strings; Stage 2 §4 and Stage 3 §2 forbid composing the allowlist or defaults in the page |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Extends the existing `@require_auth` `ui_config()`; no new route |
| astral.seed.agent-tables-in-repo-json | conforms | No agent seed tables touched |
| astral.seed.archie-catalog-wins | conforms | No catalog conflict |
| astral.seed.boot-only-not-hot-path | conforms | No seed boot path change |
| astral.seed.define-approved | conforms | No seed define work |
| astral.seed.operator-rows-stay-deleted | conforms | No operator seed rows |
| astral.seed.other-via-coverage-join | conforms | No coverage-join seed work |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work; UI surfaces errors as today |
| astral.standards.debug-contract-gated | conforms | Style D correctly deferred to AST-1148; no new debug lines |
| astral.standards.dry-and-focused-functions | needs-discussion | Stage 3 §1 keeps the AST-1139 static intro paragraph as a fallback while adding near-identical copy to `session_authoring_help` — two copies of the same user-facing text |
| astral.standards.in-scope-only | conforms | Authoring chrome only; AST-1147 values and AST-1148 resolve/emit explicitly out |
| astral.standards.logging-via-utils | conforms | No logging changes |
| astral.standards.names-not-ticket-ids | conforms | Config keys are semantic; ticket ids appear only in comments |
| astral.standards.no-cross-contamination | conforms | SomersetCover CSS, signature-image token, and resume header stay untouched |
| astral.standards.no-hardcoded-sets | needs-discussion | Token names live in config (not React), but the `authoring_help` prose restates `allowed_token_ids`, so the two can drift if the allowlist changes |
| astral.standards.public-then-helpers | conforms | No new public/helper surface; existing component structure preserved |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import introduced |
| astral.state.job-prior-states-enforced | conforms | No state registry work |
| astral.ui.frontend-file-placement | conforms | Edits existing flat `components/` and `pages/` files; no new files or subdirectories; styles unchanged |
| astral.ui.naming-conventions | conforms | PascalCase components; snake_case API paths unchanged |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn or RAILWAY_CONFIG change |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — applies_when.layers [core] does not intersect plan layers [ui, utils]
- astral.agent.grade-vector-validation — applies_when.layers [core] does not intersect plan layers
- astral.batch.batch-id-first — applies_when.layers [data, core] does not intersect plan layers
- astral.batch.batch-id-format — applies_when.layers [core, data] does not intersect plan layers
- astral.batch.claim-process-release — applies_when.layers [core, data] does not intersect plan layers
- astral.batch.entity-agent-responses-latest-only — applies_when.layers [core, data] does not intersect plan layers
- astral.debug.no-repo-root-artifacts-dir — applies_when.paths match no plan path
- astral.debug.spikes-under-debug-dir — applies_when.paths match no plan path
- astral.docs.features-single-file-per-ticket — applies_when.layers [docs] does not intersect plan layers
- astral.git.engineer-test-tree-ban — applies_when.paths (tests/bible) match no plan path
- astral.layers.core-vs-external-bright-line — applies_when.layers [core, external] does not intersect plan layers
- astral.layers.scripts-exempt-from-layer-rules — applies_when.layers [scripts] does not intersect plan layers
- astral.patterns.coat-check-never-store-empty — applies_when.layers [core] does not intersect plan layers
- astral.patterns.render-verdict-orchestrates-consult — applies_when.layers [core] does not intersect plan layers
- astral.standards.database-header-inventory — applies_when.layers [data] does not intersect plan layers
- astral.state.core-decides-transitions — applies_when.layers [core, data] does not intersect plan layers
- astral.state.no-daisy-chain-in-run — applies_when.layers [core] does not intersect plan layers

## Findings

No fix-now findings.

**discuss — Stage 3 §1, duplicated session intro copy.** The plan adds the full session paragraph to `session_authoring_help` in config *and* keeps the existing AST-1139 `<p>` literal in `AdminSessionCoverLetter.tsx` as a fallback. Because the config value is a plain literal it can never be absent; the fallback only covers an API failure. Recommendation: either drop the static paragraph and render a short neutral string on fetch failure, or add a one-line comment saying the literal is a fetch-failure fallback so a later reader does not edit the wrong copy.

**discuss — Stage 1 §1, help prose restates the allowlist.** `authoring_help` spells out `{$FULL_NAME}` / `{$LOCATION}` / `{$CONTACT_EMAIL}` / `{$PHONE}`, which duplicates AST-1147's `allowed_token_ids`. The plan records this as a deliberate Decision (one readable sentence beats assembling prose from a tuple), and both copies live in config, so no statute is violated. Recommendation: add a comment on `allowed_token_ids` pointing at `authoring_help` so a future allowlist change updates both.

**acceptable — child ticket AC numbering.** The AST-1149 description lists its second AC as "3." but the quoted text is parent AC5 (session-typed From). Content-wise the child covers parent AC2 and AC5, which is what the plan builds; only the label is off. Flagging so review and QA map to the right parent criteria later.

**acceptable — self-assessment.** `Single-Component` spans six files across utils and ui, which reads generous, but the change is one cohesive surface and every Conf justification checks out against the publish tip: AST-1147 keys are present at `COVER_FROM_BLOCK_CONFIG` (config.py L1183-1190), `TextTab` already carries `placeholder` but not `help`, and from-block really is `fields[1]` under "Cover Letter Signature" where `CandidateProfile` only reads `sec.fields[0]` — so it never renders today. Risk `low` is fair.

**R6 checklist.** Definition fidelity pass — help chrome only, resolve/emit and CSS left to siblings. Layer and import pass (`ui → utils` config import is allowed; frontend stays on the API). Config-as-source-of-truth pass. File placement pass — no new files, flat directories preserved. No batch, state-machine, or `do_task` concerns. Adversarial checks run against the publish tip: no `DATA_SHAPES` schema validator exists that new `placeholder` / `help` keys would trip; `/api/shapes/<entity>` returns the dict wholesale; the only positional profile consumer is `CandidateProfile` (`sections[0]` contact, `slice(1)` tabs), so inserting the new section after "Cover Letter Signature" adds a tab without shifting the contact grid; and Stage 2's `f.placeholder ?? (isResume && hasBaseResume ? … )` preserves the resume-lock placeholder because shapes define no placeholder for `context.raw_resume`.

context_tokens≈74000

— Joan

#### katherine — 2026-08-03T00:58:13.200Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session/docs/features/artifacts/ast-1149-from-block-authoring-help-profile-session.md

**Scope:** Single-Component — utils config + shapes + thin `/api/ui_config` exposure + profile/session help wiring; no resolve/emit.

**Conf:** high — AST-1147 keys are on ftr; TabbedTextArea already supports placeholder; visibility fix is a one-field DATA_SHAPES section split (today from-block is `fields[1]` and never renders).

**Risk:** low — additive help chrome; save/emit paths untouched; wrong help text confuses authoring but cannot break HTML emit.

Publish tip: `origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session` @ `765c24af`.

---

# AST-1149 — From-block authoring help on profile / session

**Linear:** https://linear.app/astralcareermatch/issue/AST-1149/from-block-authoring-help-on-profile-session-allow-contact-info-tokens  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock  
**Publish ref:** `sub/AST-1145/AST-1149-from-block-authoring-help-profile-session`

Owns user-visible authoring help (and config-driven placeholder/label copy) so Susan can see that Cover From supports `{$FULL_NAME}` / `{$LOCATION}` / `{$CONTACT_EMAIL}` / `{$PHONE}`, that `|` authors as `•` in print, and what the default template looks like when unset — on Candidate Profile and Admin Session Cover Letter. Consumes AST-1147 `COVER_FROM_BLOCK_CONFIG` keys (`default_template`, `allowed_token_ids`, separators). Does **not** implement resolve/emit math or SomersetCover CSS (AST-1148 / out of epic). Does **not** invent a new save route (existing candidate data PUT).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `authoring_help` + `session_authoring_help` to `COVER_FROM_BLOCK_CONFIG`. Move `contact.cover_letter_from_block` into its own `DATA_SHAPES` profile section with `placeholder` (= `default_template`) and `help` (= `authoring_help`). | utils |
| `src/ui/api/api_system.py` | Expose a small `cover_from_block` slice on `GET /api/ui_config` from `COVER_FROM_BLOCK_CONFIG` (help + default template) for Session Cover Letter. | ui |
| `src/ui/frontend/src/components/FormFields.tsx` | Extend `Field` with optional `placeholder?: string` and `help?: string` so shapes JSON is typed. | ui |
| `src/ui/frontend/src/components/TabbedTextArea.tsx` | Extend `TextTab` with optional `help?: string`; render muted help text above the textarea when present; pass `placeholder` through (already supported). | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | When building `textTabs`, pass `placeholder` and `help` from the section’s first field (shapes). Do not hardcode token names in the page. | ui |
| `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` | Load `/api/ui_config`, replace the intro help `<p>` with `cover_from_block.session_authoring_help`, and show `cover_from_block.authoring_help` under the From block field. Optional: From textarea `placeholder` = `default_template`. | ui |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `COVER_FROM_BLOCK_CONFIG` token template / allowlist / rewrite / empty policy keys | AST-1147 (already on ftr; consume only) |
| `resolve_cover_from_block` / builder emit / Style D | AST-1148 |
| SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` | out of epic |
| New admin/candidate routes | not in scope — existing `PUT /api/candidates/<id>/data` |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Config authoring chrome + profile shape visibility

**Done when:** `COVER_FROM_BLOCK_CONFIG` carries profile + session help strings; `DATA_SHAPES` exposes from-block as its own profile tab section with `placeholder`/`help` bound to those strings; `/api/ui_config` returns a `cover_from_block` object Session can read. No resolve/emit code changes.

1. In `src/utils/config.py`, inside `COVER_FROM_BLOCK_CONFIG` (after the AST-1147 keys), add exactly these keys with these values:

   | Key | Value |
   |-----|-------|
   | `"authoring_help"` | `"Allowed tokens: {$FULL_NAME}, {$LOCATION}, {$CONTACT_EMAIL}, {$PHONE}. Type \| between segments; cover print shows •. Leave empty to use the default template (see placeholder)."` |
   | `"session_authoring_help"` | `"Enter cover-letter field values, then Open HTML to Print → PDF. Letter fields come from this form. From block supports {$FULL_NAME}, {$LOCATION}, {$CONTACT_EMAIL}, {$PHONE}; type \| for • in print. When a candidate is selected, leave From empty to use that candidate’s saved from-block or the default token template. Without a candidate, From is required. If a candidate is selected and has a profile signature image, the server may include it in the sign-off; otherwise name-only. This tool does not save to the database."` |

   Update the block comment to mention AST-1149 for authoring chrome (keep AST-1137 / AST-1147 attributions).

2. In `DATA_SHAPES["candidates"]["detail"]["profile"]`, **remove** the `contact.cover_letter_from_block` field from the **"Cover Letter Signature"** group (leave `contact.cover_letter_signature` there alone).

3. Immediately after the **"Cover Letter Signature"** group (before **"Signature Image"**), insert a new section:

   ```python
   {
       "label": "Cover Letter From",
       "fields": [
           {
               "key": "contact.cover_letter_from_block",
               "label": "Cover letter From block",
               "type": "textarea",
               "placeholder": COVER_FROM_BLOCK_CONFIG["default_template"],
               "help": COVER_FROM_BLOCK_CONFIG["authoring_help"],
           },
       ],
   },
   ```

   Do **not** mark required. Empty / whitespace remains “unset → default template” at resolve time (AST-1148).

4. In `src/ui/api/api_system.py`:
   - Import `COVER_FROM_BLOCK_CONFIG` alongside existing config imports.
   - In `ui_config()`, add to the jsonify payload:

     ```python
     "cover_from_block": {
         "default_template": COVER_FROM_BLOCK_CONFIG["default_template"],
         "authoring_help": COVER_FROM_BLOCK_CONFIG["authoring_help"],
         "session_authoring_help": COVER_FROM_BLOCK_CONFIG["session_authoring_help"],
     },
     ```

5. **Do not** change `allowed_token_ids`, `default_template`, `authoring_separator`, `emit_separator`, or `empty_segment_policy` values from AST-1147. **Do not** touch `src/core/candidate.py` or `src/core/builder.py`.

⚠️ **Decision:** Own `DATA_SHAPES` section (“Cover Letter From”) instead of sharing “Cover Letter Signature”. `CandidateProfile` maps each tab section to `sec.fields[0]` only — today from-block is `fields[1]` and never renders. A dedicated one-field section makes the textarea visible without rewriting TabbedTextArea into multi-field panels.

⚠️ **Decision:** Help copy lives in `COVER_FROM_BLOCK_CONFIG` (not hardcoded in TSX). Token names appear in those strings so the UI only renders config text — no React assembly of allowlists (import-direction / ui-config-driven). Slight string overlap with `allowed_token_ids` is intentional for a single user-facing sentence.

⚠️ **Decision:** Profile `placeholder` reuses `COVER_FROM_BLOCK_CONFIG["default_template"]` by reference so the unset default is not duplicated as a second literal.

## Stage 2: Profile tab shows help + placeholder

**Done when:** Candidate Profile “Cover Letter From” tab shows the from-block textarea with placeholder = default template and muted help listing tokens + `|`→`•` + empty→default. Save path unchanged (existing PUT).

1. In `src/ui/frontend/src/components/FormFields.tsx`, extend `Field`:

   ```ts
   placeholder?: string
   help?: string
   ```

2. In `src/ui/frontend/src/components/TabbedTextArea.tsx`:
   - Add optional `help?: string` to `TextTab`.
   - When `tab.help` is a non-empty string, render a muted paragraph (reuse the muted style pattern from `CandidateProfile` signature-image blurb: `color: "#8b949e"`, `marginBottom: 8`, `fontSize: 13`, `lineHeight: 1.5`) **above** `LabeledTextArea` / custom panel.
   - Keep passing `placeholder={tab.placeholder}` into `LabeledTextArea`.

3. In `src/ui/frontend/src/pages/CandidateProfile.tsx`, in the `textTabs` map, after resolving `const f = sec.fields[0]`, set:

   - `placeholder: f.placeholder ?? (isResume && hasBaseResume ? "Locked — base resume has been generated from this text" : undefined)`  
     (prefer shapes `placeholder` when present; keep the resume-lock override when `isResume && hasBaseResume`)
   - `help: typeof f.help === "string" && f.help.trim() ? f.help : undefined`

4. **Do not** add token names, `|`, or `•` as string literals in `CandidateProfile.tsx` / `TabbedTextArea.tsx` beyond rendering `f.help` / `f.placeholder` from shapes.

5. Manual check (builder note only; no product test tree edits): with a candidate selected, open Profile → “Cover Letter From” tab → see placeholder template and help; type `{$FULL_NAME} | {$LOCATION}` → Save → GET candidate shows `candidate_data.contact.cover_letter_from_block` with that authoring text.

## Stage 3: Session Cover Letter help parity

**Done when:** Admin Session Cover Letter intro and From-field help document the same token + `|`→`•` + empty→default authoring rules from config (not hardcoded page copy).

1. In `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx`:
   - On mount, `api("/api/ui_config")` → JSON; read `cover_from_block` object into state (default empty strings if missing so the page still renders).
   - Replace the static intro `<p>` body with `cover_from_block.session_authoring_help` when non-empty; if empty (config missing), keep the current AST-1139 intro text as fallback only.
   - For the `from_block` field label block, under the label span (or under the textarea), render muted `cover_from_block.authoring_help` when non-empty.
   - Set the From `textarea` `placeholder` to `cover_from_block.default_template` when non-empty.

2. **Do not** change Open HTML gating (`from_block` optional when candidate selected — AST-1139). **Do not** compose defaults in React. **Do not** call resolve helpers from the page.

3. Manual check: Session Cover Letter page shows updated intro + From help/placeholder matching config; Open HTML still works with empty From + candidate selected.

## Contract for siblings (non-goals)

- **AST-1148** still owns expand of allowlisted tokens, `|`→`•`, empty-segment drop, and Style D on emit. This ticket only makes the authoring contract visible.
- **AST-1147** already owns template/allowlist/rewrite keys; do not redefine them.
- Persist path remains AST-1137’s `contact.cover_letter_from_block` via existing candidate data PUT.

## Self-Assessment

**Scope:** `Single-Component` — utils config + shapes + thin ui_config exposure + profile/session help wiring; no resolve/emit.

**Conf:** `high` — AST-1147 keys are on ftr and merged into this publish tip; TabbedTextArea already supports placeholder; visibility fix is a one-field section split that matches Signature Image’s own-section pattern.

**Risk:** `low` — additive help chrome; save/emit paths untouched; wrong help text would confuse authoring but cannot break HTML emit.

## Code Rules check

- §1.1 / `in-scope-only`: help chrome only; no resolve/emit/CSS.
- §1.4 / `no-hardcoded-sets`: token/separator story rendered from config strings; React does not invent allowlists.
- §2.1 / `astral.config.config-source-of-truth`: `authoring_help` / `session_authoring_help` / placeholder live in or reference `COVER_FROM_BLOCK_CONFIG`.
- §3.2 / `astral.layers.ui-config-driven-business-logic` + §3.3 `import-direction`: UI renders config; no from-block expansion in the page.
- §3.5 `frontend-file-placement` / naming: edits stay in existing page/component files under `src/ui/frontend/src/pages|components`.
- `pattern.ui.admin-endpoint`: no new route; reuse `/api/ui_config` + existing candidate data PUT.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session`
**Tip:** `e61c58b9`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2c3dc706` | `COVER_FROM_BLOCK_CONFIG` authoring help + own DATA_SHAPES section + `/api/ui_config` slice |
| 2 | `727a1ecb` | Profile TabbedTextArea help/placeholder wiring |
| 3 | `e61c58b9` | Session Cover Letter config-driven intro + From help/placeholder |

## Radia review — findings (rev 1)

**Overall: DISCUSS** — no fix-now. Diff matches the plan almost line-for-line: help/placeholder stay in `COVER_FROM_BLOCK_CONFIG`, no token/`|`/`•` literals invented in TSX, no new routes, no resolve/emit touched.

**What's solid:**
- `COVER_FROM_BLOCK_CONFIG["authoring_help"]` / `["session_authoring_help"]` are the only source of the token/`|`→`•` prose; `CandidateProfile.tsx` / `TabbedTextArea.tsx` render `f.help` / `f.placeholder` without re-deriving it.
- `AdminSessionCoverLetter.tsx` keeps `SESSION_INTRO_FALLBACK` as a fetch-failure-only fallback (matches plan §3.1) — does not compose config in React.
- New "Cover Letter From" `DATA_SHAPES` section fixes the real `sec.fields[0]`-only bug (from-block was `fields[1]`, invisible) exactly per the plan's ⚠️ Decision.

**Discuss:**
1. **Git topology** — `sub/AST-1145/AST-1149-...` merged `origin/sub/AST-1145/AST-1148-...` directly (`2f56ef35`) in addition to `origin/ftr/AST-1145-...` (`38caf363`). Traced the merge parent: it landed only AST-1148's plan-stage commit (`d2d39504`), before AST-1148's own code commits existed, so no AST-1148 production code (`candidate.py` / `builder.py`) crossed into this diff — verified via `git diff origin/dev...<tip> -- src/core/candidate.py src/core/builder.py` (empty). No functional impact; flagging only so future siblings sync via `merge-child` → `ftr` rather than a direct sub-to-sub merge (`orch.git.merge-on-checkout` describes merging `ftr`, not a sibling's sub).
2. **Straggler (C4)** — plan-time Considered-but-excluded lists `astral.standards.debug-contract-gated` and `astral.standards.dry-and-focused-functions` (deferred to AST-1148). Full-set sweep's `applies_when` (ui/utils layer, `src/**`) technically matches this diff too, so both score `conforms` rather than `not-applicable` — no `debug=` surface and no function-complexity growth in the touched lines, so substance-wise there's nothing to fix; noting per rubric C4 belt-and-suspenders, not blocking.

**Pattern conformance:** `pattern.ui.admin-endpoint` — conforms (no new route; reuses `/api/ui_config` + existing candidate data `PUT`).

— Radia

## Resolution

**Date:** 2026-08-03  
**Review tip ingested:** `5aaa5c75` (`docs(AST-1149): Radia review — findings`)  
**Overall:** clean — Radia **DISCUSS** with **no fix-now**; Frame diff none.

| Item | Action |
|------|--------|
| Discuss 1 — sub↔sub merge of AST-1148 plan tip | Accepted; no product change. Confirmed tip still has empty `git diff origin/dev...HEAD -- src/core/candidate.py src/core/builder.py`. Future sibling sync via `merge-child` → `ftr`. |
| Discuss 2 — C4 stragglers (`debug-contract-gated`, `dry-and-focused-functions`) | Accepted; already `conforms` on substance — no `debug=` / no complexity growth. No src change. |

**§9a:** `origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session` dry-runs clean into `origin/dev` and `origin/ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock`.
