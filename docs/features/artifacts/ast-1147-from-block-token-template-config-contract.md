# AST-1147 — From-block token template + config contract

**Linear:** https://linear.app/astralcareermatch/issue/AST-1147/from-block-token-template-config-contract-allow-contact-info-tokens  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock  
**Publish ref:** `sub/AST-1145/AST-1147-from-block-token-template-config-contract`

Owns the config contract for a tokenized cover from-block default: default authoring template (`{$FULL_NAME} | {$LOCATION}` / `{$CONTACT_EMAIL} | {$PHONE}`), allowlisted token ids, `|`→`•` rewrite literals, and empty-segment drop policy. Extends existing `COVER_FROM_BLOCK_CONFIG`. Does **not** implement resolve/emit (sibling AST-1148). Does **not** own profile/session help chrome (sibling AST-1149). Does **not** register brief aliases (`RESUME_LOCATION` / `RESUME_EMAIL` / `CANDIDATE_MOBLE`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `COVER_FROM_BLOCK_CONFIG` with default token template, allowlisted token ids, authoring/emit separator rewrite, and empty-segment policy. Keep AST-1137 keys intact for current resolve until AST-1148 migrates. Do not add brief aliases to `TOKEN_SOURCES` or this block. | utils |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `src/core/candidate.py` (`resolve_cover_from_block`) | AST-1148 |
| `src/core/builder.py` job/session from-block emit + Style D | AST-1148 |
| Profile/session help copy, placeholders, labels beyond this ticket | AST-1149 |
| SomersetCover CSS/DOM, `{$SIGNATURE_IMAGE}` | out of epic |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: Extend `COVER_FROM_BLOCK_CONFIG`

**Done when:** `COVER_FROM_BLOCK_CONFIG` declares the default token template, allowlist, `|`→`•` rewrite, and empty-segment policy as readable keys; AST-1137 keys still present and unchanged in meaning; no resolve/emit code changes; brief aliases absent from config.

1. In `src/utils/config.py`, locate module-level `COVER_FROM_BLOCK_CONFIG` (immediately after `CANDIDATE_LIBRARY_CONFIG`, AST-1137 block). **Keep** every existing key with its current value:
   - `"contact_key": "cover_letter_from_block"`
   - `"segment_separator": " • "`
   - `"line_separator": "\n"`
   - `"name_column": "full"`
   - `"line_1_contact_paths": ("location",)`
   - `"line_2_contact_paths": ("contact_email", "phone")`
   - `"sources": ("candidate", "default")`

2. Add these new keys to the **same** dict (AST-1147). Use exactly these names and values:

   | Key | Value | Meaning for AST-1148 consumers |
   |-----|-------|--------------------------------|
   | `"default_template"` | `"{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}"` | Authoring-form default when saved from-block is empty/whitespace. Two lines joined by `line_separator` (`\n`). Tokens use `{$TOKEN}` form. Authoring separator between segments is bare `\|` (spaces around `\|` as shown). |
   | `"allowed_token_ids"` | `("FULL_NAME", "LOCATION", "CONTACT_EMAIL", "PHONE")` | Only these registry names are expanded on the from-block surface. Order is documentation order matching the default template lines — not a sort requirement for resolve. |
   | `"authoring_separator"` | `"\|"` | Character candidates type as a segment separator in from-block text. |
   | `"emit_separator"` | `" • "` | What `|` becomes at emit (spaces match AST-1137 golden / existing `segment_separator`). |
   | `"empty_segment_policy"` | `"drop_with_adjacent_separator"` | When a token resolves empty (or a free-text segment is empty after strip), omit that segment **and** its adjacent authoring/emit separator so printed output never shows dangling `•`, bare `|`, or unresolved placeholders for allowlisted empties. |

3. Update the block’s leading comment from `# AST-1137: …` to mention both tickets, e.g.  
   `# AST-1137 / AST-1147: candidate from-block field + token default template / rewrite policy.`  
   Do not delete the AST-1137 attribution.

4. **Do not** add `RESUME_LOCATION`, `RESUME_EMAIL`, `CANDIDATE_MOBLE`, or `CANDIDATE_MOBILE` to:
   - `COVER_FROM_BLOCK_CONFIG["allowed_token_ids"]`
   - `TOKEN_SOURCES`
   - any new alias map inside this block

5. **Do not** change:
   - `CANDIDATE_LIBRARY_CONFIG` / `UI_CONFIG` profile field for `contact.cover_letter_from_block` (AST-1149 owns authoring help chrome)
   - `TOKEN_SOURCES` entries for `FULL_NAME` / `LOCATION` / `CONTACT_EMAIL` / `PHONE` (already correct paths)
   - `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]`
   - `BUILD_CONFIG["session_cover_letter"]`
   - `src/core/candidate.py`, `src/core/builder.py`, or any UI/TSX file

6. **Do not** implement resolve that reads `default_template` / `allowed_token_ids` / rewrite keys — that is AST-1148. This stage is declarative config only.

⚠️ **Decision:** Keep AST-1137 `line_*_contact_paths` / `segment_separator` keys alongside the new token-template keys. Current `resolve_cover_from_block` stays green until AST-1148 switches the default path to `default_template` + allowlist + rewrite. Removing path keys here would break emit mid-epic.

⚠️ **Decision:** `emit_separator` is `" • "` (spaced bullet), not bare `"•"`, so rewrite matches the AST-1137 golden and existing `segment_separator`. Sibling resolve must substitute `|` → `emit_separator` (not invent a third literal).

⚠️ **Decision:** `empty_segment_policy` is a single string enum value (`"drop_with_adjacent_separator"`), not a nested dict — AST-1148 implements the only allowed policy; if a second policy is ever needed, extend the string set in config then.

⚠️ **Decision:** No profile `placeholder` / `help` field metadata in this ticket. Ticket boundaries hand help chrome to AST-1149; config keys above are enough for emit to satisfy parent AC1’s config half.

## Contract for siblings (non-goals)

- **AST-1148** must consume `default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, and `empty_segment_policy` inside the shared from-block expand path (candidate custom, default template, session-typed From). Unrecognized `{$…}` tokens stay as-is (forward-compat). Style D debug lives there.
- **AST-1149** owns user-visible help that the default template / `|`→`•` story is discoverable on profile/session.
- This ticket only guarantees the keys exist with the values above.

## Self-Assessment

**Scope:** `minor` — one utils config block extension; no core/UI behavior change.

**Conf:** `high` — parent Open questions already map tokens and rewrite; AST-1137 block is the clear extension point; allowlist matches existing `TOKEN_SOURCES` names.

**Risk:** `low` — additive keys; existing resolve ignores unknown keys; no alias registration; siblings own consumption.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1145/AST-1147-from-block-token-template-config-contract`
**Tip:** `bcc95f9a`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `bcc95f9a` | Extend `COVER_FROM_BLOCK_CONFIG` with `default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, `empty_segment_policy`; keep AST-1137 keys |

## Code Rules check

- §1.1 / `in-scope-only`: config only; no resolve/emit/help chrome.
- §1.4 / `no-hardcoded-sets`: token ids, separators, template, and empty policy live in `COVER_FROM_BLOCK_CONFIG` for AST-1148 to read — not inline in core/UI.
- §2.1 / `astral.config.config-source-of-truth` / `pattern.config.config-block`: extend the named block; do not invent a second from-block config dict.
- §3.3 import direction: no new imports; utils-only edit.
- No cross-contamination into resume header emit or signature-image token contract.

---

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1147
**Publish ref tip:** `c5fec3213c17c3c01dc2b2c00e5814ccfad0c056`
**Overall:** DISCUSS

### What's solid

- Stage 1 matches: `COVER_FROM_BLOCK_CONFIG` gains `default_template`, `allowed_token_ids`, `authoring_separator`, `emit_separator`, `empty_segment_policy`; AST-1137 keys retained.
- No resolve/emit/help chrome; brief aliases absent; Self-Assessment **minor** matches utils-only footprint.
- Betty `test()` + one `merge-tests`; engineer `code()` is `config.py` only.

### Issues

**discuss (C4 straggler):** `astral.debug.no-repo-root-artifacts-dir` — Joan excluded; in-scope on three-dot vs origin/dev. Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; in-scope on three-dot vs origin/dev. Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on three-dot vs origin/dev. Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope on three-dot vs origin/dev. Scores **conforms**. No product action.

### Recommended actions

- Engineer: ack C4 stragglers (no src change) via `resolve-child`, then User Testing.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | No confidence / grade config touched |
| `astral.agent.do-task-delegation` | scoped | not-applicable | layers ∩ diff empty (['core']); paths miss diff (['src/core/**']) |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | layers ∩ diff empty (['core']); paths miss diff (['src/core/**']) |
| `astral.batch.batch-id-first` | scoped | not-applicable | layers ∩ diff empty (['data', 'core']); paths miss diff (['src/data/**', 'src/core/**']) |
| `astral.batch.batch-id-format` | scoped | not-applicable | layers ∩ diff empty (['core', 'data']); paths miss diff (['src/core/**', 'src/data/**']) |
| `astral.batch.claim-process-release` | scoped | not-applicable | layers ∩ diff empty (['core', 'data']); paths miss diff (['src/core/**', 'src/data/**']) |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | layers ∩ diff empty (['core', 'data']); paths miss diff (['src/core/**', 'src/data/**']) |
| `astral.config.config-source-of-truth` | scoped | conforms | Template/allowlist/rewrite/empty policy in COVER_FROM_BLOCK_CONFIG |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No scoring thresholds |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env; plain literals |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | conforms | docs/features/artifacts plan — not repo-root artifacts/ |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Combined plan under docs/features — not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | No dispatch/run_next edits |
| `astral.dispatch.seed-auto-false` | scoped | conforms | No dispatch_task seed rows |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | One docs/features/artifacts plan file for AST-1147 |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test/bible only; merge-tests exception ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() is config.py only; tests from Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | layers ∩ diff empty (['core', 'external']); paths miss diff (['src/core/**', 'src/external/**']) |
| `astral.layers.import-direction` | scoped | conforms | Utils-only additive keys; no new imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff empty (['scripts']); paths miss diff (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Config declares contract; UI/core not owning rules here |
| `astral.patterns.coat-check-never-store-empty` | scoped | not-applicable | layers ∩ diff empty (['core']); paths miss diff (['src/core/**']) |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | not-applicable | layers ∩ diff empty (['core']); paths miss diff (['src/core/**']) |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | No agent seed table edits |
| `astral.seed.archie-catalog-wins` | scoped | conforms | No catalog/seed conflict |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | No seed boot path change |
| `astral.seed.define-approved` | scoped | conforms | No seed define work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | No operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | No coverage-join seed work |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | layers ∩ diff empty (['data', 'core', 'ui']) |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers ∩ diff empty (['data']); paths miss diff (['src/data/**']) |
| `astral.standards.debug-contract-gated` | scoped | conforms | No Style D here; deferred to AST-1148 |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | No new functions; declarative keys only |
| `astral.standards.in-scope-only` | scoped | conforms | Config contract only; resolve/emit/help excluded |
| `astral.standards.logging-via-utils` | scoped | conforms | No logging changes |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Keys semantic; ticket ids only in comments |
| `astral.standards.no-cross-contamination` | scoped | conforms | No resume/signature/rubric pipe edits |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Token ids/separators/policy live in config |
| `astral.standards.public-then-helpers` | scoped | conforms | No new public/helper surface |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data import |
| `astral.state.core-decides-transitions` | scoped | not-applicable | layers ∩ diff empty (['core', 'data']); paths miss diff (['src/core/**', 'src/data/**']) |
| `astral.state.job-prior-states-enforced` | scoped | conforms | JOB_STATES untouched |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | layers ∩ diff empty (['core']); paths miss diff (['src/core/**']) |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No gunicorn/worker config changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1147) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary only |
| `orch.git.flow-direction-inviolable` | universal | conforms | Publish stays on origin/sub/AST-1145/AST-1147-… |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under AST-1145 parent topology |
| `orch.git.merge-on-checkout` | universal | conforms | No illegal merge-on-checkout recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick/rebase/force on publish ref |
| `orch.git.no-dev-agent-branches` | universal | conforms | Uses sub/AST-1145/AST-1147-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in astral-AST-1145 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Parent OQs closed; locked template values shipped |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 keys/values match Files Changed and diff |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Artifacts child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee remains Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Implementer stays assignee through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path product commits |

### Pattern conformance

- `pattern.config.config-block` — **conforms**

### Plan adherence

Diff matches Stage 1 exact key/value table. Boundaries vs AST-1148/1149 held. Three-dot also carries Betty corpus from origin/tests merge history — expected, not scope smuggle in AST-1147 `code()`.

context_tokens≈30000
