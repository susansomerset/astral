<!-- linear-archive: AST-1148 archived 2026-08-11 -->

## Linear archive (AST-1148)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1148/resolve-tokens-in-from-block-emit-debug-allow-contact-info-tokens-and  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1145 — Allow contact info tokens and | chars in fromBlock  
**Blocked by / blocks / related:** parent: AST-1145

### Description

## What this implements

Owns expanding allowlisted tokens, `|`→`•`, and empty-segment drop inside the shared from-block path used by job emit, session empty→candidate resolve, **and** non-empty session-typed From; Style D debug on the touched `debug=` path. Consumes sibling config contract (AST-1147). Does not change SomersetCover CSS or signature-image tokens. After AST-1147.

## In scope

- [X] `astral.standards.dry-and-focused-functions` — one shared `expand_cover_from_block_text` for candidate / default / session
- [X] `astral.standards.public-then-helpers` — public expand + resolve; local token/segment helpers below
- [X] `astral.standards.debug-contract-gated` — Style D index + working-detail on touched `debug=` expand/resolve path
- [X] `astral.standards.in-scope-only` — resolve/emit expansion only; no help chrome / CSS / aliases
- [X] `astral.standards.no-hardcoded-sets` — allowlist, separators, template, policy from `COVER_FROM_BLOCK_CONFIG`; paths from `TOKEN_SOURCES`
- [X] `astral.standards.no-cross-contamination` — no resume header, signature-image, or consult/rubric `|` parsers
- [X] `astral.config.config-source-of-truth` — consume AST-1147 keys; no second from-block config block
- [X] `astral.layers.import-direction` — core owns expand; UI unchanged

## Considered but excluded

- [X] `pattern.config.config-block` / declaring `COVER_FROM_BLOCK_CONFIG` keys — AST-1147 (already on ftr)
- [X] `pattern.ui.admin-endpoint` / profile-session help chrome — AST-1149
- [X] SomersetCover CSS/DOM / `{$SIGNATURE_IMAGE}` — out of epic (`src/core/builder.py` emit HTML chrome; `BUILD_CONFIG["cover_letter_render_tokens"]`)
- [X] Brief aliases `RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE` — not registered; left unresolved if authored
- [X] Calling `resolve_tokens()` for from-block — would expand non-allowlisted registry tokens; plan uses allowlist-gated `TOKEN_SOURCES` walk instead

## Acceptance criteria

1. [X] With no saved from-block, Print Cover Letter and Session Cover Letter (empty From + selected candidate) emit a two-line From block with `•` between non-empty name/location and email/phone segments (AST-1137 golden shape).
2. [X] Saving a custom From block on the candidate profile persists the authoring text (tokens and `|`); a later cover emit resolves tokens and prints `•` instead of `|`.
3. [X] A saved From block with allowed contact tokens and `|` emits with tokens replaced, `|` shown as `•`, and no dangling separators when a token is empty.
4. [X] Clearing the saved From block (empty/whitespace) returns emit to the default template behavior.
5. [X] A non-empty typed Session Cover Letter From runs the same token + `|`→`•` + empty-segment rules before emit.
6. [X] With `debug=True` on the touched resolve/emit path, logs show Style D index plus working-detail lines for source and token outcomes as described in parent Functional scope.
7. [X] Resume print/HTML and signature-image token behavior are unchanged; brief token aliases are not resolvable.

## Boundaries

- [X] Does not own config contract (AST-1147).
- [X] Does not own profile/session help chrome (sibling Authoring help AST-1149).
- [X] Does not change SomersetCover CSS or signature-image tokens.

## Notes for planning

After AST-1147. Plan: `docs/features/artifacts/ast-1148-resolve-tokens-in-from-block-emit-debug.md` on publish ref below.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock`, child `sub/AST-1145/<this-id>-resolve-tokens-in-from-block-emit-debug`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-03T01:37:56.839Z
[merge-child] blocked: missing merge-tests(AST-1148): on origin/sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug

Hygiene rewrite linearized the sub onto ftr and kept `test(AST-1148)` but dropped `merge-tests(AST-1148)`. Tip `154f0a37`.

@Betty White — re-deliver one `merge-tests(AST-1148):` onto current publish ref (no duplicate), force-with-lease/push per qa-child §9. Stay User Testing; assignee remains Hedy.

— Chuckles

#### chuckles — 2026-08-03T01:33:50.257Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` fails on `67232d90` subject `Merge remote-tracking branch 'origin/ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock' into sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug` in `ftr..sub`.

@Hedy Lamarr — rewrite publish ref so that range has no `Merge remote-tracking branch` subject (rebase `--onto origin/ftr/AST-1145-allow-contact-info-tokens-and-chars-in-fromblock` after that merge, or equivalent), force-with-lease push `sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug`, stay User Testing.

— Chuckles

#### radia — 2026-08-03T01:31:28.597Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1148
**Publish ref:** a74fef62c60c4fd949f1583c62b9ad9c617b4f00
**Overall:** CLEAN

## Plan adherence
- `expand_cover_from_block_text` matches plan Stage 1 exactly: separators/policy/allowlist/template read only from `COVER_FROM_BLOCK_CONFIG`, allowlist-gated `TOKEN_SOURCES` walk (not `resolve_tokens`, per the plan's ⚠️ Decision — confirmed no non-allowlisted registry token can leak).
- Traced all 3 call sites to confirm the single-expand invariant holds: job path (`build_cover_letter_from_job` → one `resolve_cover_from_block` call), session empty+candidate (`resolve_cover_from_block`, expands once internally), session-typed non-empty (`expand_cover_from_block_text` directly). No double-expand anywhere.
- `_candidate_for_cover_from_block` (builder.py, reused unchanged) never sets `candidate_data`, so expand correctly takes the token-view branch (`contact` top-level) — verified the shape contract rather than assuming it.

**Pattern conformance:** none cited (ticket's boundary notes reference sibling ticket ids, not canon pattern ids for this diff).

## Frame diff
(none) — description checkboxes already reflect this ticket's true scope; no adds/moves needed.

**What's solid:** Style D gives two distinct `debug_index` calls (resolve's own + expand's own), each `index=1/total=1` for a single-item operation, not a batch loop — both strictly gated behind `debug=True`. Raw session `from_block` text passed un-stripped into expand (plan requires preserving internal newlines); expand normalizes `\r\n` itself.

context_tokens≈14000
— Radia

#### betty — 2026-08-03T01:21:11.953Z
1. **Existing / keep:** AST-1138 / AST-1139 HTML golden paths (Name/City/email still hold via `default_template` expand); resume print unchanged.
2. **Broken / revised:** `TestAst1137ResolveCoverFromBlock` — default path now expands `default_template` (not path composition); Style D drops `line*_segments`, uses expand `tokens_*` / `separator_rewrite` details.
3. **New:**
   - `TestAst1148ExpandCoverFromBlock` — expand tokens/`|`/empty-drop; aliases left as-is; resolve custom+clear→default; expand Style D
   - `TestAst1148SessionTypedFromBlockExpand` — session-typed From expand; no-candidate empty-token drop; job custom token expand
4. **Bible:** `docs/test-bible/core/candidate.md` § AST-1148 (+ AST-1137 note); `docs/test-bible/core/builder.md` § AST-1148 (+ AST-1139 note).
5. **Run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1148ExpandCoverFromBlock \
  tests/component/core/test_candidate.py::TestAst1137ResolveCoverFromBlock \
  tests/component/core/test_builder.py::TestAst1148SessionTypedFromBlockExpand \
  tests/component/core/test_builder.py::TestAst1139SessionCoverEmptyFromBlock \
  tests/component/core/test_builder.py::TestAst1138JobCoverSomersetFromBlock \
  -q
```
6. **Publish:** `origin/sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug` @ `a74fef62` — `merge-tests(AST-1148): origin/tests 6f0230f82b551d3b7d5eae8f0171791d526f98c9`
7. **Bible shasums** (publish tip):
- `docs/test-bible/core/candidate.md` `94677b234e72d36fbb1645ab5aa424f1e3789722`
- `docs/test-bible/core/builder.md` `9feaff1ea283a0acacacbbacb6cebd19a800bded`

#### joan — 2026-08-03T01:10:47.452Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1148
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 unset → default two-line From with `•` | Stage 1 §5e — default path expands `default_template`; verified the template resolves the same contact paths the retired `line_*_contact_paths` composition used, so the AST-1137 golden shape is preserved |
| AC2 saved custom From resolves at emit, prints `•` | Stage 1 §5d/§5f — custom authoring text goes through the shared expand |
| AC3 tokens replaced, `|` → `•`, no dangling separators on empty | Stage 1 §4d–§4g — allowlist lookup, segment split, empty-segment drop, join with `emit_separator` |
| AC4 cleared From returns to default | Stage 1 §5c/§5e — custom wins only when it strips non-empty; otherwise `default_template` |
| AC5 non-empty session-typed From, same rules | Stage 2 §2 — `build_session_cover_letter` routes `source=session` through the same helper |
| AC6 Style D debug on the touched resolve/emit path | Stage 1 §4i and §5h — index header plus source / token / rewrite / length detail lines, gated on `debug=True` |
| AC7 resume + signature unchanged; aliases not resolvable | Stage 1 §4d and Stage 2 §5 — aliases absent from allowlist and `TOKEN_SOURCES` so they are left as-is; no resume, CSS, or signature-image edits |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 shared expand + resolve migration | Functional scope “Tokenized From block”, “Authoring `|` → printed `•`”, “Empty token / segment drop”, “Default when unset”, “Debug (backend)”; child #2 Proposed ticket |
| Stage 2 session-typed From uses the same expand | Functional scope “Session-typed From” and “Emit consumers”; parent AC5 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work proposed |
| orch.git.commit-vocabulary | conforms | Standard engineer vocabulary on the child sub ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-1145/AST-1148-… |
| orch.git.ftr-sub-topology | conforms | Child ref matches the parent Git table |
| orch.git.merge-on-checkout | conforms | Tip carries the ftr merge (`67232d90`) ahead of the plan commit |
| orch.git.no-cherry-pick-rebase-force | conforms | The plan proposes no rewrite; the earlier force-with-lease was Chuckles git authority with Susan approval, and I verified the current tip is clean |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1145/… only |
| orch.git.one-epic-worktree-per-parent | conforms | Single epic worktree; the race that caused the bad tip is already resolved |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Parent Open questions closed; four Decisions recorded, and the blocked publish was escalated to Susan rather than self-approved |
| orch.pipeline.plan-is-bible | conforms | Binding Files Changed table with literal algorithm steps and debug line shapes |
| orch.pipeline.project-scoped-queues | conforms | Single-child Artifacts scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan entry only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly hands golden-string updates to Betty |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No grading or confidence math touched |
| astral.agent.do-task-delegation | conforms | No `do_task` or agent call introduced; expansion is pure string work |
| astral.agent.grade-vector-validation | conforms | No graded task involved |
| astral.batch.batch-id-first | conforms | No batch claim signatures touched |
| astral.batch.batch-id-format | conforms | No batch_id minted |
| astral.batch.claim-process-release | conforms | Not a batch path; emit is request-scoped |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data or RESPONSE work |
| astral.config.config-source-of-truth | conforms | Separators, allowlist, template, and policy all read from `COVER_FROM_BLOCK_CONFIG`; token paths from `TOKEN_SOURCES`; no second config block |
| astral.config.pass-threshold-vs-score-floor | conforms | Scored-consult keys untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No env or secret reads |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch or run_next involvement |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src and the plan doc |
| astral.layers.core-vs-external-bright-line | conforms | Pure core string logic; no I/O and no external calls |
| astral.layers.import-direction | conforms | core → utils only (`config`, `formatting`, `logging`); UI unchanged |
| astral.patterns.coat-check-never-store-empty | conforms | Expand is emit-only and explicitly never persists or mutates the candidate |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Not a consult path |
| astral.seed.boot-only-not-hot-path | conforms | No seed or boot path touched |
| astral.seed.define-approved | conforms | No seed define work |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work; the one raise is a core `ValueError` on an unimplemented config policy |
| astral.standards.debug-contract-gated | conforms | Style D index plus working-detail lines fire only when `debug=True`; §4i states “No debug-contract lines when `debug=False`” |
| astral.standards.dry-and-focused-functions | needs-discussion | One shared expand for all three sources is right, but the plan adds a local token regex and a local dotted-path walker that duplicate config's private `_TOKEN_RE` (L5102) and `_walk_dot_path` (L5077) |
| astral.standards.in-scope-only | conforms | Two core files; CSS, signature image, help chrome, aliases, and resume header all explicitly out |
| astral.standards.logging-via-utils | conforms | Uses the existing `src/utils/logging.py` logger already bound in `candidate.py`; no print or bare logging |
| astral.standards.names-not-ticket-ids | conforms | `expand_cover_from_block_text` is semantic; ticket ids only in docstrings and comments |
| astral.standards.no-cross-contamination | conforms | Consult/rubric pipe parsers, resume HTML, and SomersetCover emit left alone |
| astral.standards.no-hardcoded-sets | conforms | No inline separators, allowlist, or template; the only literal is the guarded `empty_segment_policy` value it implements, which raises if config says otherwise |
| astral.standards.public-then-helpers | conforms | Public `expand_cover_from_block_text` in the public section; lookup and segment helpers nested below |
| astral.state.core-decides-transitions | conforms | No state transitions |
| astral.state.job-prior-states-enforced | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chaining |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — applies_when.paths match no plan path
- astral.debug.spikes-under-debug-dir — applies_when.paths match no plan path
- astral.dispatch.seed-auto-false — applies_when.paths (dispatcher.py, config.py) match no plan path
- astral.docs.features-single-file-per-ticket — applies_when.layers [docs] does not intersect plan layers [core]
- astral.git.engineer-test-tree-ban — applies_when.paths (tests/bible) match no plan path
- astral.layers.scripts-exempt-from-layer-rules — applies_when.layers [scripts] does not intersect [core]
- astral.layers.ui-config-driven-business-logic — applies_when.layers [ui, utils] does not intersect [core]
- astral.patterns.require-auth-on-protected-endpoints — applies_when.layers [ui] does not intersect [core]
- astral.seed.agent-tables-in-repo-json — applies_when.paths match no plan path
- astral.seed.archie-catalog-wins — applies_when.paths match no plan path
- astral.seed.operator-rows-stay-deleted — applies_when.paths match no plan path
- astral.seed.other-via-coverage-join — applies_when.paths match no plan path
- astral.standards.database-header-inventory — applies_when.layers [data] does not intersect [core]
- astral.standards.utils-data-late-import-only — applies_when.layers [utils] does not intersect [core]
- astral.ui.frontend-file-placement — applies_when.layers [ui] does not intersect [core]
- astral.ui.naming-conventions — applies_when.layers [ui] does not intersect [core]
- astral.ui.single-gunicorn-worker — applies_when.layers [ui, scripts, utils] does not intersect [core]

## Findings

No fix-now findings.

**discuss — Stage 1 §4g, free text mixed with an empty token.** The parent says "when a token resolves empty, omit that segment and its adjacent separator". The plan drops a segment only when the *whole expanded segment* is empty after strip, so an authored segment like `Phone: {$PHONE}` with no phone on file keeps the label and prints `Phone:` — arguably the dangling artifact the parent wanted to avoid. This changes no acceptance criterion, because the default template contains bare tokens only and AC1 through AC5 behave identically either way, and the alternative (dropping any segment containing an empty token) would silently delete text the candidate authored. Recommendation: add a fourth Decision stating the segment-level rule explicitly so Betty can pin the golden and Susan sees the mixed-segment behavior before it ships.

**discuss — Stage 1 §2 and §4d, duplicated private helpers.** The plan defines a local `_FROM_BLOCK_TOKEN_RE` and a local dotted-path walker rather than importing config's private `_TOKEN_RE` (config.py L5102) and `_walk_dot_path` (L5077). I checked for public equivalents and there are none, so the alternatives were importing privates across modules or promoting them in `config.py`, which is not in this ticket's Files Changed. The plan made the in-scope-correct call; flagging only so a later ticket can promote one public helper instead of carrying two copies.

**acceptable — two Style D index headers per resolve.** `resolve_cover_from_block` emits one index and the expand helper emits its own. §1.5.1 keys the header on function context, so two contexts is legitimate, and the split keeps token detail attached to the function that computed it. Slightly noisier logs for a single from-block, worth knowing when reading a debug run.

**acceptable — unrecognized aliases print literally.** Because non-allowlisted tokens are left as-is and a literal placeholder is non-empty, a candidate who types the brief's `{$CANDIDATE_MOBLE}` will see it printed verbatim in the cover letter. That is exactly the parent's forward-compat rule and satisfies AC7 ("aliases are not resolvable"); AST-1149's help copy is the mitigation.

**acceptable — self-assessment.** `Single-Component` / `high` / `Medium` is honest, and Medium is the right call for a user-visible emit path. I verified every Conf claim against the publish tip: AST-1147 keys are present, `resolve_cover_from_block` already does the dual-shape contact handling the plan reuses, and `_candidate_for_cover_from_block` (builder.py L639) yields exactly the `full`/`first`/`last`/`contact` shape Stage 2 passes to expand.

**R6 checklist.** Definition fidelity pass. Layer and import pass — expand stays in `candidate.py`, so the library layer gains no HTML and the builder call site stays thin. Config-as-source-of-truth pass. No batch, state-machine, or `do_task` concerns. Adversarial checks against the publish tip: the publish ancestry is clean at `d2d39504` with no AST-1149 plan commits; `TOKEN_SOURCES` maps `FULL_NAME`→`full`, `LOCATION`→`contact.location`, `CONTACT_EMAIL`→`contact.contact_email`, `PHONE`→`contact.phone`, all `source: candidate`, so the allowlist-gated walk resolves against the token view the plan builds; those are the same paths the retired `line_*_contact_paths` default composition read, so replacing it with `default_template` leaves AC1 output byte-identical; and the Decision to avoid `resolve_tokens` is well founded because that function (config.py L5122) expands every registry token and logs a warning per empty, which would both leak `{$GITHUB}`-class tokens onto the cover and spam the log.

context_tokens≈92000

— Joan

#### hedy — 2026-08-03T01:05:18.250Z
Plan on publish ref `sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug` @ `d2d39504` (Chuckles force-with-lease cleaned AST-1149 ancestry).

https://github.com/susansomerset/astral/blob/sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug/docs/features/artifacts/ast-1148-resolve-tokens-in-from-block-emit-debug.md

**Scope:** `Single-Component` — `src/core/candidate.py` shared expand + resolve migration; `src/core/builder.py` session-typed From call-site only.

**Conf:** `high` — AST-1147 config keys already on ftr; dual-shape contact handling and Style D patterns already exist; allowlist-gated `TOKEN_SOURCES` walk avoids `resolve_tokens` expanding non-surface registry tokens.

**Risk:** `Medium` — cover emit is user-visible; wrong empty-segment or allowlist behavior would print dangling `•` / wrong expansions. Mitigated by config-driven policy and one helper for candidate / default / session sources.

#### hedy — 2026-08-03T01:00:46.400Z
🛑 Plan publish blocked: epic worktree race with AST-1149

While committing the plan, the shared epic worktree was switched onto `sub/AST-1145/AST-1149-…`. The plan file contents are correct, but the first push to `origin/sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug` landed tip `9fe3f93c` whose ancestry incorrectly includes AST-1149 plan commits (`af0a76de`).

Clean tip ready locally (not on origin — needs non-FF replace):
- `d2d39504` — `docs(AST-1148): plan — resolve tokens in from-block emit debug`
- Ancestry: `67232d90` (ftr merge + AST-1147) → plan only
- AST-1149 commits **not** in ancestry

Proposed resolution: `@susan` approve `git push --force-with-lease=sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug:9fe3f93c origin d2d39504:sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug` (child publish ref only; not `dev`/`main`). Then I will finish Plan Ready (description frame, comment, attachment).

Also: local `sub/AST-1145/AST-1149-…` tip still has `9fe3f93c` (AST-1148 plan commit on top). Katherine should reset/sync that branch from `origin/sub/AST-1145/AST-1149-…` — I did not push that pollution to origin/1149.

---

# AST-1148 — Resolve tokens in from-block + emit debug

**Linear:** https://linear.app/astralcareermatch/issue/AST-1148/resolve-tokens-in-from-block-emit-debug-allow-contact-info-tokens-and  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock  
**Publish ref:** `sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug`

Owns expanding allowlisted contact tokens, `|`→`•`, and empty-segment drop inside the shared from-block path used by job Print Cover Letter emit, session empty→candidate resolve, **and** non-empty session-typed From. Consumes AST-1147 `COVER_FROM_BLOCK_CONFIG` keys (`default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, `empty_segment_policy`). Style D debug on the touched `debug=` expand/resolve path. Does **not** change SomersetCover CSS/DOM, signature-image tokens, profile/session help chrome (AST-1149), or register brief aliases.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add shared `expand_cover_from_block_text`; rewrite `resolve_cover_from_block` to select authoring text (saved custom or `default_template`) then expand via that helper; Style D token/source/rewrite details when `debug=True`. Stop using AST-1137 `line_*_contact_paths` composition for the default path (keys remain in config; do not delete). | core |
| `src/core/builder.py` | In `build_session_cover_letter`, when form `from_block` is non-empty (`source=session`), run the same expand helper before emit (pass candidate blob when loaded, else empty contact shape). Job path already consumes `resolve_cover_from_block` text — no second expand. Keep existing Style D `from_block_source` / `from_block_chars` lines. | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `COVER_FROM_BLOCK_CONFIG` key declarations | AST-1147 (already on ftr) |
| Profile/session help copy, placeholders, labels | AST-1149 |
| SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` | out of epic |
| Brief aliases `RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE` | never |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Shared expand helper + resolve migration

**Done when:** `expand_cover_from_block_text` expands allowlisted tokens, rewrites `|`→`emit_separator`, drops empty segments per config policy; `resolve_cover_from_block` returns expanded text for both custom and default paths using `default_template` (no more path-based default composition); Style D details fire only when `debug=True`.

1. In `src/core/candidate.py`, add imports to the existing config import block:
   - `TOKEN_SOURCES` from `src.utils.config`
   - Keep `COVER_FROM_BLOCK_CONFIG` (already imported)
   - Import `value_to_str` from `src.utils.formatting` (same helper `resolve_tokens` uses)

2. Add a module-level token regex matching config’s pattern (do **not** import private `_TOKEN_RE`):
   ```python
   _FROM_BLOCK_TOKEN_RE = re.compile(r"\{\$([A-Z_]+)\}")
   ```

3. After `recompute_full_name` (public section), add public:

   ```python
   def expand_cover_from_block_text(
       text: str,
       candidate: dict,
       *,
       source: str,
       debug: bool = False,
   ) -> str:
       """Expand from-block authoring text for emit (AST-1148).

       Allowlisted ``{$TOKEN}`` → candidate values; ``|`` → emit separator;
       empty segments dropped per COVER_FROM_BLOCK_CONFIG. Unrecognized
       ``{$…}`` left as-is. ``source`` is a debug label only (candidate/default/session).
       """
   ```

4. Implementation of `expand_cover_from_block_text` (literal behavior):

   a. `logger.set_debug_flag(debug)`.

   b. Read config (no hardcoded literals for separators/policy/allowlist/template):
      - `auth_sep = COVER_FROM_BLOCK_CONFIG["authoring_separator"]`  # `"|"`
      - `emit_sep = COVER_FROM_BLOCK_CONFIG["emit_separator"]`  # `" • "`
      - `line_sep = COVER_FROM_BLOCK_CONFIG["line_separator"]`  # `"\n"`
      - `policy = COVER_FROM_BLOCK_CONFIG["empty_segment_policy"]`
      - `allowed = COVER_FROM_BLOCK_CONFIG["allowed_token_ids"]`
      - If `policy != "drop_with_adjacent_separator"`: raise `ValueError` naming the unexpected policy (only this policy is implemented).

   c. Build a walkable token view from `candidate` (same dual-shape acceptance as today’s `resolve_cover_from_block`):
      - If `candidate` has dict `candidate_data`: start from `build_candidate_token_view(candidate)`.
      - Else treat as token-view / builder shape:  
        `view = {"first": …, "last": …, "full": …, "contact": top-level contact dict or {}, "_astral_candidate_id": …}`.
      - If `str(view.get("full") or "").strip()` is empty, set `view["full"] = recompute_full_name(first, last)` so `{$FULL_NAME}` matches AST-1137 name fallback.

   d. Define inner `_lookup_allowed(name: str) -> Optional[str]`:
      - If `name` not in `allowed`: return `None` (caller leaves `{$name}` as-is).
      - `spec = TOKEN_SOURCES.get(name)`; if missing or `spec.get("source") != "candidate"`: return `None` (leave as-is — do not invent values; brief aliases are absent from allowlist and TOKEN_SOURCES).
      - Walk `spec["path"]` on `view` with a tiny local dotted-path walker (do **not** call `resolve_tokens` — that would expand non-allowlisted registry tokens like `{$GITHUB}`).
      - Return `value_to_str(raw).strip()` when raw is present/non-empty; return `""` when empty/missing.

   e. Define inner `_expand_segment(segment: str) -> tuple[str, dict]` that replaces tokens via `_FROM_BLOCK_TOKEN_RE`:
      - For each match: if `_lookup_allowed(name) is None` → keep literal `match.group(0)` and count `left_as_is`; else substitute the looked-up string (may be `""`) and count `resolved` or `empty`.
      - Return `(expanded_segment, counts)`.

   f. Normalize newlines: `raw = (text or "").replace("\r\n", "\n")`.

   g. Per-line empty-segment drop (policy `drop_with_adjacent_separator`):
      - Split `raw` on `line_sep`.
      - For each line: split on `auth_sep` (`"|"`) into segments; for each segment run `_expand_segment`, then `.strip()`; **keep** only segments whose stripped expanded text is non-empty; join keepers with `emit_sep`.
      - Drop lines that become empty after join.
      - Join surviving lines with `line_sep`.
      - Result is the returned emit text (may be `""`).

   h. Do **not** mutate `candidate` / contact. Do **not** persist. Do **not** touch HTML.

   i. When `debug=True`, emit Style D:
      - One `debug_index`: `func="candidate.expand_cover_from_block_text"`, `index=1`, `total=1`, `identifier` = `view.get("_astral_candidate_id")` or `candidate.get("astral_candidate_id")` or `""`, `outcome=f"success — from_block {source}"`.
      - `debug_detail` lines (prefix contract via existing helper):
        - `source={source}`
        - `tokens_found={total {$TOKEN} matches in authoring text}`
        - `tokens_resolved={allowlisted non-empty substitutions}`
        - `tokens_empty={allowlisted empty substitutions}`
        - `tokens_left_as_is={non-allowlisted / unknown left as placeholders}`
        - `separator_rewrite={"yes" if auth_sep in raw else "no"}`
        - `text_chars={len(result)}`
      - No debug-contract lines when `debug=False`.

⚠️ **Decision:** Expand lives in `candidate.py` (not `builder.py`) so job resolve, session empty→resolve, and session-typed From share one path without pulling HTML into the library layer — same placement as AST-1137 resolve.

⚠️ **Decision:** Do **not** call `resolve_tokens()` for from-block text. Parent allowlist is a surface subset of `TOKEN_SOURCES`; `resolve_tokens` would expand every registry token (e.g. `{$GITHUB}`) and warn on empties. Walk `TOKEN_SOURCES` paths only for ids in `allowed_token_ids`.

⚠️ **Decision:** Segment-first algorithm (split lines → split on `authoring_separator` → expand tokens per segment → drop empty → join with `emit_separator`) implements `drop_with_adjacent_separator` literally. Do not regex-scrub dangling bullets after a blind global replace.

5. Rewrite `resolve_cover_from_block` body:

   a. Keep signature `resolve_cover_from_block(candidate: dict, *, debug: bool = False) -> dict` and return shape `{"text": str, "source": "candidate"|"default"}`.

   b. `logger.set_debug_flag(debug)`.

   c. Resolve contact + custom raw exactly as today (DB row `candidate_data.contact` **or** top-level `contact`; `contact_key` from config; custom wins when `isinstance(raw, str) and raw.strip()`).

   d. If custom: `authoring = raw.strip()` (outer strip only; preserve internal newlines), `source = COVER_FROM_BLOCK_CONFIG["sources"]` candidate entry (index 0 / `"candidate"`).

   e. Else: `authoring = COVER_FROM_BLOCK_CONFIG["default_template"]`, `source =` default entry (`"default"`). **Delete** the AST-1137 path-based `line_1_contact_paths` / `line_2_contact_paths` / `segment_separator` composition block — default emit now comes from expanding the template.

   f. `text = expand_cover_from_block_text(authoring, candidate, source=source, debug=debug)`.

   g. Return `{"text": text, "source": source}`.

   h. Style D on resolve: when `debug=True`, keep one index on `func="candidate.resolve_cover_from_block"` with outcome `success — from_block {source}` plus details `source={source}` and `text_chars={len(text)}` (expand emits the token/rewrite details under its own index). No debug when `debug=False`.

⚠️ **Decision:** Leave AST-1137 `line_*_contact_paths` / `segment_separator` / `name_column` keys in `COVER_FROM_BLOCK_CONFIG` untouched (AST-1147 contract). Resolve stops reading them; do not delete keys in this ticket.

## Stage 2: Session-typed From uses the same expand

**Done when:** Non-empty Admin Session Cover Letter `from_block` is expanded with the same token / `|`→`•` / empty-segment rules before SomersetCover emit; empty→`resolve_cover_from_block` path already expands via Stage 1; job Print Cover Letter unchanged beyond consuming expanded resolve text.

1. In `src/core/builder.py`, inside `build_session_cover_letter`, locate the `from_block` special case (non-empty form → `source=session`).

2. When `raw.strip()` is non-empty:
   - Set `from_block_source = cfg["from_block_sources"][0]` (`"session"`) as today.
   - Shape candidate for expand:
     - If `candidate_root` is non-empty: `shaped = _candidate_for_cover_from_block(candidate_root)`.
     - Else: `shaped = {"full": "", "first": "", "last": "", "contact": {}}` (tokens resolve empty and drop; free text / unrecognized placeholders still emit).
   - `normalized["from_block"] = candidate_mod.expand_cover_from_block_text(raw, shaped, source=from_block_source, debug=debug)`.
   - Do **not** strip `raw` before expand (preserve internal newlines; expand normalizes `\r\n` itself). Pass `raw` as authored (same string previously assigned to `normalized[key]`).

3. Empty form + `empty_uses_candidate_resolve` + candidate: keep calling `resolve_cover_from_block` (Stage 1 already expands). Do **not** double-expand the returned text.

4. Job `build_cover_letter_from_job`: keep single call to `resolve_cover_from_block(...); fields from from_res["text"]`. Do **not** call expand again on that text.

5. Do **not** change `_emit_somerset_cover_html_document`, SomersetCover CSS, signature-image token handling, resume builders, or profile persistence APIs.

6. Existing builder Style D success details (`from_block_source=…`, `from_block_chars=…`, `document_path=somerset_cover`) stay. Expand’s own Style D index/details cover token outcomes when `debug=True`.

⚠️ **Decision:** Session-typed From does not write through to `contact.cover_letter_from_block` (AST-1139 contract unchanged). Expand is emit-only.

## Contract for siblings (non-goals)

- **AST-1147** already declared config keys — this ticket only consumes them.
- **AST-1149** owns authoring help chrome so Susan can discover tokens / `|`→`•` / default template.
- Persistence of authoring text (tokens + `|`) on Candidate Profile remains the existing PUT path; this ticket only changes emit-time expansion.
- Betty owns test/bible updates for golden strings that previously assumed raw custom text or path-composed defaults.

## Self-Assessment

**Scope:** `Single-Component` — core candidate expand/resolve + one builder session call-site; no config key invention, no UI/CSS.

**Conf:** `high` — AST-1147 keys are on ftr; dual-shape contact handling and Style D patterns already exist in `resolve_cover_from_block` / session builder; allowlist-gated walk of `TOKEN_SOURCES` is a narrow, known pattern.

**Risk:** `Medium` — cover emit is user-visible; a wrong empty-segment or allowlist rule would print dangling `•` / unresolved tokens / expand non-allowlisted registry tokens. Mitigated by config-driven policy and shared helper for all three sources.

## Code Rules check

- §1.1 / `in-scope-only`: no CSS, signature-image, help chrome, alias registration, resume header.
- §1.3 / `dry-and-focused-functions` + `public-then-helpers`: one public expand; resolve + session call it; local lookup/segment helpers below public section.
- §1.4 / `no-hardcoded-sets`: separators, allowlist, template, policy from `COVER_FROM_BLOCK_CONFIG`; token paths from `TOKEN_SOURCES`.
- §1.5.1 / `debug-contract-gated`: Style D index + ` | ` details only when `debug=True`.
- §2.1 / config source of truth: no new config block; consume AST-1147 keys.
- §3.3 import direction: core → utils only; UI unchanged.
- No cross-contamination into consult/rubric `|` parsers or resume HTML.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug`
**Tip:** `4e90baf6`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `bc340226` | `expand_cover_from_block_text` + `resolve_cover_from_block` migrates to `default_template` expand |
| 2 | `4e90baf6` | Session-typed From calls shared expand before SomersetCover emit |

## Radia review — findings (rev 1)

**Overall: CLEAN** — no fix-now, no discuss.

**What's solid:**
- `expand_cover_from_block_text` reads separators / policy / allowlist / template only from `COVER_FROM_BLOCK_CONFIG`, walks `TOKEN_SOURCES` paths for allowlisted ids only (does not call `resolve_tokens`, per plan's ⚠️ Decision — confirmed no non-allowlisted registry token could leak).
- Single-expand invariant traced across all 3 call sites: job (`build_cover_letter_from_job` → one `resolve_cover_from_block` call), session empty+candidate (`resolve_cover_from_block`, expands once internally), session-typed non-empty (`expand_cover_from_block_text` directly, no double-expand). Grepped all `resolve_cover_from_block` / `expand_cover_from_block_text` call sites in `src/` to confirm.
- `_candidate_for_cover_from_block` (builder.py, reused unchanged) never sets `candidate_data`, so `expand_cover_from_block_text` correctly takes the token-view branch (`contact` top-level) rather than the DB-row branch — verified the shape contract instead of assuming it.
- Style D: two distinct `debug_index` calls (resolve's own + expand's own), each `index=1/total=1` for a single-item operation — not a batch loop, so this doesn't trip the "one header per batch item" rule; both gated strictly behind `debug=True`.
- Raw session `from_block` text is passed un-stripped into expand (plan explicitly requires preserving internal newlines); expand normalizes `\r\n` itself.

**Pattern conformance:** none cited (ticket's boundary notes reference sibling ticket ids, not canon pattern ids for this ticket's own diff).

— Radia

## Resolution

**Date:** 2026-08-03  
**Radia review tip:** `95686e02` (`docs(AST-1148): Radia review — findings`)  
**Outcome:** Clean sign-off — no fix-now, no discuss, no Frame diff adds. No product or plan-doc code changes in resolve; ship tip as reviewed after `resolve()` publish + §9a dry-runs.
