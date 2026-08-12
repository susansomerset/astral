<!-- linear-archive: AST-1081 archived 2026-08-11 -->

## Linear archive (AST-1081)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1081/contact-shapes-websites-full-name-field-contract-update-candidate-ui  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1065 — Update candidate ui for contact info  
**Blocked by / blocks / related:** parent: AST-1065; blocks: AST-1082

### Description

## What this implements

Expose the full user-facing contact set (including websites, title_patterns, reason_codes) and the editable `full` column (derived default rule) in config shapes / field contracts so Profile can manage them without a hardcoded field list. Introduce a multi-entry websites (or string-list) shape field type only if no existing type fits — Archie approves that new type before reuse. Does **not** own Profile React behavior (sibling Profile UI) or nav cleanup. Does **not** change the AST-1014 library schema beyond shape exposure of existing keys / full default behavior.

## Acceptance criteria

- [X] On Candidate Profile, Contact Information (including signature/image, title_patterns, reason_codes) read and save against name columns + `contact.*` — not `profile.*`. (shapes contract enabling this)
- [X] A candidate can add, edit, and remove websites entries on Profile; after save and reload, those entries persist under `contact.websites`. (websites field contract)
- [X] `full` appears as an editable Profile field; when empty/unset it defaults to the library-derived first+last join; an explicit override persists and reloads. (full field contract / derived default)

## Boundaries

Does **not** own Profile React behavior or nav cleanup (sibling). Does **not** own library migration (AST-1014). Does **not** expand Admin Manage Candidates into contact editing.

## In scope

- [X] `pattern.config.config-block` — contact vocabulary + Profile field contracts stay in `DATA_SHAPES` / `CANDIDATE_LIBRARY_CONFIG`
- [X] `astral.config.config-source-of-truth` — field keys and `string_list` type live in config shapes
- [X] `astral.layers.ui-config-driven-business-logic` — FormFields renders resolved shape types; no parallel contact field list in React
- [X] `astral.docs.features-single-file-per-ticket` — one plan doc at `docs/features/interface/ast-1081-…`
- [X] `astral.standards.in-scope-only` — shapes + FormFields type + empty-`full` / websites save coercion only
- [X] `astral.ui.naming-conventions` — `string_list` shape type string; FormFields component naming unchanged

## Considered but excluded

- [X] `astral.ui.frontend-file-placement` (Candidate Profile page / nav) — AST-1082 owns Profile manage UI + nav title-patterns cleanup
- [X] `astral.patterns.require-auth-on-protected-endpoints` — no new routes; existing candidate data PUT unchanged
- [X] AST-1014 library migration / name-column schema — already on integration line; this ticket only exposes shapes + empty-`full` save rule
- [X] Admin Manage Candidates `edit.manage` expansion — boundary: Profile owns contact manage
- [X] Username-or-URL GitHub/LinkedIn Profile UX copy — normalization already in core (`normalize_contact_urls`); Profile acceptance AC is sibling

## Notes for planning

Optional new websites/`string_list` shape field type — introduced here (parent-approved pattern); Archie approval before reuse elsewhere.

## Git branch (authoritative)

Parent `ftr/AST-1065-update-candidate-ui-for-contact-info`; child `sub/AST-1065/AST-1081-contact-shapes-websites-full`. Publish to `origin/<publish-ref>` only.

### Comments

#### chuckles — 2026-07-31T00:06:22.705Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed on `origin/sub/AST-1065/AST-1081-contact-shapes-websites-full` — commit `15471f09` subject is `Merge remote-tracking branch 'origin/dev' into sub/...` (forbidden pull-merge).

@Ada Lovelace — republish a clean sub tip (merge `origin/ftr/AST-1065-update-candidate-ui-for-contact-info` / `origin/dev` the legal way; no `Merge remote-tracking branch` subjects). Stay User Testing; assignee stays Ada.

— Chuckles

#### radia — 2026-07-31T00:05:01.375Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1081
**Publish ref:** `1a4e44f840b33832db00688bf2524f03bb4ab122` (`origin/sub/AST-1065/AST-1081-contact-shapes-websites-full`)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1065/AST-1081-contact-shapes-websites-full` — layers `{core, ui, utils, docs}`; change_types `{add, modify}`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1081)` on sub |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | Tip on `origin/sub/...` publish-ref |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1065/AST-1081-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in child history |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1081 commits |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub topology, not agent/dev branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1065` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | `string_list` intro site; Archie reuse bar documented |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match product diff |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child under AST-1065 |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `test`/`merge-tests` own bible + tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Product commits stay on allowed paths |
| astral.agent.confidence-bounds | scoped | conforms | No graded/confidence path touched |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` / agent_task changes |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector work |
| astral.batch.batch-id-first | scoped | conforms | Not a batch path |
| astral.batch.batch-id-format | scoped | conforms | Not a batch path |
| astral.batch.claim-process-release | scoped | conforms | Not a batch path |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | scoped | conforms | Keys/types in `DATA_SHAPES`; no React field list |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env introduced |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths `artifacts/**`/`scripts/spikes/**` absent from diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan + model docs, not spike output |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file; model doc is existing amend |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits stay off `src/` / features (merge-tests ok) |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` commits exclude test tree |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core save rule only; no external I/O |
| astral.layers.import-direction | scoped | conforms | UI FormFields; core→config/database; utils config |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` in diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Shapes drive fields; FormFields renders type only |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult path |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No new routes; existing PUT unchanged |
| astral.standards.data-raises-caller-logs | scoped | conforms | `ValueError` on bad websites; caller owns log |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` in diff |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses `recompute_full_name`; coerce next to normalize |
| astral.standards.in-scope-only | scoped | conforms | No Profile/nav/Admin/1014 schema creep |
| astral.standards.logging-via-utils | scoped | conforms | No new print/`logging` path |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in named layers/files |
| astral.standards.no-hardcoded-sets | scoped | conforms | Type/keys in config; no inline contact vocabulary |
| astral.standards.public-then-helpers | scoped | conforms | Empty-full folded into existing save path |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data import change |
| astral.state.core-decides-transitions | scoped | conforms | Candidate state machine untouched |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | conforms | FormFields + App.css only |
| astral.ui.naming-conventions | scoped | conforms | `string_list` snake_case; FormFields naming unchanged |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker/deploy change |

## Pattern conformance

- `pattern.config.config-block` — conforms (contact vocabulary + field contracts in `DATA_SHAPES` / library config)
- Cited astral statutes above covered via full-set sweep

## Plan adherence

Stages 1–3 delivered as planned. Self-Assessment Scope `Single-Component` matches the diff footprint. Boundaries held vs AST-1082 (Profile page/nav) and AST-1014 (library schema). Child ACs that name Profile end-to-end correctly land as shapes/`string_list`/save contract here.

## Findings

**discuss:** straggler — Joan Excluded `astral.git.engineer-test-tree-ban` (plan had no test paths) but three-dot diff includes `tests/**` + `docs/test-bible/**` via Betty `merge-tests`. Sweep scores **conforms** (engineer product commits clean). No product fix required — resolve-child acknowledge.

## Notes

- Plan-rubric verdict attached (APPROVED). Straggler callout above is the only C4 hit.
- §5f/§5g N/A (no new debug-contract surface; no LLM external edits).
- `docs()` append on plan file; pushed to publish-ref.

## What’s solid

Empty/whitespace `full` recompute + strip override; websites list coerce with fail-closed non-list; FormFields `string_list` Add/Remove without client-side empty strip.

context_tokens≈52000

#### betty — 2026-07-30T23:59:47.982Z
## QA test manifest

`merge-tests(AST-1081)` → `origin/sub/AST-1065/AST-1081-contact-shapes-websites-full` @ `996e815a` (origin/tests `5c47ce43`).

### Classification

1. **Existing coverage:** `TestAst1014CandidateLibrary` (omit-full when first/last change; refuse `profile`; URL normalize).
2. **Broken / obsolete:** none — additive empty-full branch + websites coerce; FormFields type additive.
3. **Gaps (this pass):** empty/whitespace `full` recompute + strip override; `contact.websites` list coerce / ValueError; DATA_SHAPES `full` / `string_list` / `reason_codes` + Admin manage boundary; FormFields `string_list` Add/edit/Remove / non-array→[].

**§6c:** no `pages/` change this ticket — FormFields component coverage only (Profile page = AST-1082).

**Integration:** no existing scenario asserts these contracts — no revision.

### Manifest (run on publish tip after merge `origin/ftr/…`)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1081ContactShapesSaveContract \
  tests/component/core/test_candidate.py::TestAst1014CandidateLibrary \
  tests/component/utils/test_config.py::TestAst1081ContactShapesConfig \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_FormFields.test.tsx
```

### Bible shasums (`origin/sub/…` tip)

- `docs/test-bible/core/candidate.md` `ef22c20af661a9c10a24bc2489ad6ed0954b6c1c`
- `docs/test-bible/utils/config.md` `0e5f4b525cc5a3adaaa266f37a79c799e03b65e9`
- `docs/test-bible/frontend/components.md` `09b7a52f268d598c49c6fe60e606102e140c40b4`

#### joan — 2026-07-30T23:52:35.502Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1081
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Profile Contact binds columns + `contact.*` (not `profile.*`) | Stages 1–2 shapes + FormFields enable; Profile page wiring N/A — boundary AST-1082 |
| AC2 add/edit/remove websites; persist `contact.websites` | Stages 1–3 (`string_list` + save coercion); Profile host N/A — AST-1082 |
| AC3 GitHub/LinkedIn username-or-URL normalize | N/A — boundary (core normalize AST-1014; Profile UX AST-1082) |
| AC4 editable `full` with empty→derived default | Stages 1 + 3 (`full` shape + empty-`full` recompute) |
| AC5 nav duplicate title-patterns removed | N/A — boundary AST-1082 |
| AC6 save/reopen round-trip coherence | Stage 3 persistence contract; Profile reopen UX N/A — AST-1082 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 DATA_SHAPES | Purpose/Functional scope shape-driven contact surface; child AC1/AC2/AC4 contracts |
| Stage 2 FormFields `string_list` | Parent new-pattern websites/string-list; Functional scope multi-entry websites |
| Stage 3 empty `full` + websites coerce | Functional scope full-name default + websites persist; child AC2/AC4 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Sub publish / plan() vocabulary implied |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1065/AST-1081-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1065 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | string_list intro flagged for Archie reuse bar |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Interface scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/ edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded/confidence path touched |
| astral.agent.do-task-delegation | conforms | No do_task / agent_task changes |
| astral.agent.grade-vector-validation | conforms | No grade validation work |
| astral.batch.batch-id-first | conforms | Not a batch path |
| astral.batch.batch-id-format | conforms | Not a batch path |
| astral.batch.claim-process-release | conforms | Not a batch path |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | conforms | Field keys/types in DATA_SHAPES; no React field list |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env introduced |
| astral.debug.spikes-under-debug-dir | conforms | Production model doc amend, not spike output |
| astral.docs.features-single-file-per-ticket | conforms | One plan file; CANDIDATE_DATA_MODEL is existing model doc |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features |
| astral.layers.core-vs-external-bright-line | conforms | Core save rule only; no external I/O |
| astral.layers.import-direction | conforms | UI FormFields; core→config/database; utils config |
| astral.layers.ui-config-driven-business-logic | conforms | Shapes drive fields; FormFields renders type only |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys touched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult path |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new routes; existing PUT unchanged |
| astral.standards.data-raises-caller-logs | conforms | ValueError on bad websites; caller/UI owns log |
| astral.standards.debug-contract-gated | conforms | No new debug-contract surface |
| astral.standards.dry-and-focused-functions | conforms | Reuse recompute_full_name; coerce next to normalize |
| astral.standards.in-scope-only | conforms | No Profile/nav/Admin/1014 schema creep |
| astral.standards.logging-via-utils | conforms | No new logging path |
| astral.standards.no-cross-contamination | conforms | Stays in named layers/files |
| astral.standards.no-hardcoded-sets | conforms | Type/keys in config; no inline contact vocabulary |
| astral.standards.public-then-helpers | conforms | Fold empty-full into existing save helper path |
| astral.standards.utils-data-late-import-only | conforms | No utils→data import change |
| astral.state.core-decides-transitions | conforms | Candidate state machine untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.frontend-file-placement | conforms | FormFields + App.css only; no new page/subdir |
| astral.ui.naming-conventions | conforms | `string_list` snake_case type; PascalCase FormFields |
| astral.ui.single-gunicorn-worker | conforms | No worker/config deploy change |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.debug.spikes-under-debug-dir, astral.docs.features-single-file-per-ticket, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 2 button wording says labeled `Add website` then parenthetical bold `Add` for reuse — implement **`Add`** (generic FormFields control).

**acceptable:** Child ACs 1–2 are end-to-end Profile wording; ticket Boundaries + plan correctly split Profile React/nav to AST-1082 and deliver shapes/`string_list`/save contract here. Self-assessment Scope Single-Component / Conf high / Risk Medium is honest (empty-`full` intentional per AC).

**R6:** Definition fidelity pass for child #1. Config/source-of-truth pass. Layer/import pass. File placement pass. No state-machine/batch creep. DRY via existing `recompute_full_name`.

context_tokens≈48000

— Joan

#### ada — 2026-07-30T23:49:43.856Z
Plan published on `origin/sub/AST-1065/AST-1081-contact-shapes-websites-full` @ `b6e42b28`.

[Plan doc](https://github.com/susansomerset/astral/blob/sub/AST-1065/AST-1081-contact-shapes-websites-full/docs/features/interface/ast-1081-contact-shapes-websites-full-name-field-contract.md)

**Scope:** Single-Component — `DATA_SHAPES` contact fields (`full`, `websites`, `reason_codes`), new FormFields `string_list` type, and `save_candidate_data` empty-`full` + websites list coercion; Profile page/nav left to AST-1082.

**Conf:** high — extends AST-1014 shapes/`recompute_full_name`/FormFields switch; missing pieces are known keys + list type + empty-full branch.

**Risk:** Medium — empty-`full` recompute is intentional per AC (could surprise if blank-full were meant to stick); websites non-list payloads fail closed with ValueError.

---

# Contact shapes + websites + full-name field contract

**Linear:** [AST-1081](https://linear.app/astralcareermatch/issue/AST-1081/contact-shapes-websites-full-name-field-contract-update-candidate-ui)
**Parent:** [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info)
**Publish ref:** `sub/AST-1065/AST-1081-contact-shapes-websites-full`

Expose the missing Profile contact field contracts (`full`, `contact.websites`, `contact.reason_codes`) in `DATA_SHAPES`, introduce a reusable `string_list` shape field type for multi-entry websites (no existing FormFields type fits a `list[str]`), and tighten the library-derived `full` default so empty/unset values recompute from first+last on save. Does **not** own Candidate Profile page layout/nav (AST-1082), Admin Manage Candidates contact expansion, or AST-1014 library schema changes beyond shape exposure and the empty-`full` save rule.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information (+ reason_codes section if not in Contact fields) with `full`, `contact.websites` (`string_list`), `contact.reason_codes` | utils |
| `src/ui/frontend/src/components/FormFields.tsx` | Add `string_list` to `Field.type`; render multi-entry add/edit/remove list of strings | ui |
| `src/ui/frontend/src/App.css` | Minimal styles for the `string_list` control under FormFields (reuse `dep-*` tokens) | ui |
| `src/core/candidate.py` | Empty/whitespace `full` → `recompute_full_name`; coerce/validate `contact.websites` as `list[str]` on save | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | One-line note: Profile edits `websites` as string list via `string_list` shape type; empty `full` recomputes on save | docs |

**Out of Files Changed (sibling / already shipped):** `CandidateProfile.tsx` load/save wiring and nav cleanup → **AST-1082**. `normalize_contact_urls` / name columns / `contact.*` blob homes → **AST-1014** (already on line). `DATA_SHAPES["candidates"]["edit"]["manage"]` Admin modal fields → leave unchanged (boundary: no Admin contact expand).

## Stage 1: DATA_SHAPES — expose full, websites, reason_codes

**Done when:** `GET /api/shapes/candidates` → `detail.profile` Contact Information includes editable `full`, `contact.websites` with `type: "string_list"`, and `contact.reason_codes`; existing contact keys remain on `contact.*` / name columns (no `profile.*`).

1. In `src/utils/config.py`, locate `DATA_SHAPES["candidates"]["detail"]["profile"]` → the section with `"label": "Contact Information"`.

2. Insert after the `last` field entry (before `contact.contact_email`):
   ```python
   {"key": "full", "label": "Full Name", "type": "text"},
   ```

3. Insert after `contact.linkedin_url` (before `contact.timezone`):
   ```python
   {"key": "contact.websites", "label": "Websites", "type": "string_list"},
   ```

4. Insert after `pronouns` (still inside Contact Information `fields`):
   ```python
   {"key": "contact.reason_codes", "label": "Reason Codes", "type": "textarea"},
   ```
   Keep the existing separate sections for Cover Letter Signature, Signature Image, and Title Patterns unchanged — they already bind `contact.*`. Do not add `profile.*` keys.

5. Do **not** change `list.manage` or `edit.manage` shapes (Admin Manage Candidates stays on its current narrow field set).

⚠️ **Decision:** Introduce shape field type `string_list` (not reuse `textarea`). `contact.websites` is a JSON list of URL strings per `CANDIDATE_DATA_MODEL` / `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`; newline-in-textarea would invent a second serialization and fight round-trip with the blob. Parent AST-1065 already flagged this optional new type for Archie approval before reuse — this ticket is the introduction site; reuse elsewhere needs the same approval bar.

⚠️ **Decision:** `reason_codes` stays a single `textarea` string (like `title_patterns`), not `string_list`. No library consumer or model entry defines it as `list[str]`; only `websites` is documented as a list.

## Stage 2: FormFields — `string_list` renderer

**Done when:** A field with `type: "string_list"` renders as an ordered list of text inputs with per-row Remove and an Add control; value round-trips as `string[]` through `onChange`; unknown/non-array current values treat as `[]`.

1. In `src/ui/frontend/src/components/FormFields.tsx`, extend `Field.type`:
   ```ts
   type: "text" | "textarea" | "select" | "toggle" | "string_list"
   ```

2. In `renderInput`, add `case "string_list":` before `default`:
   - Normalize `value` to `string[]`: if `Array.isArray(value)` use `value.map(v => String(v))`, else `[]`.
   - Render a vertical stack: for each index `i`, a row with `<input className="dep-input" type="text" value={items[i]} />` and a button labeled `Remove` that calls `onChange(items.filter((_, j) => j !== i))`.
   - Below the rows, a button labeled `Add website` (generic enough for reuse: label text **`Add`**) that calls `onChange([...items, ""])`.
   - On input change at index `i`, clone the array, set `next[i] = e.target.value`, `onChange(next)`.
   - Do **not** strip empty strings in the renderer (user may clear a row while editing); persistence coercion is core (Stage 3).

3. In `src/ui/frontend/src/App.css`, under the FormFields / DetailsEditPage section (~§10), add minimal rules for `.dep-string-list`, `.dep-string-list-row`, and `.dep-string-list-add` using existing CSS variables (`--border`, `--text-secondary`, etc.). No new design tokens. No card chrome.

4. Do **not** edit `CandidateProfile.tsx` in this ticket — AST-1082 owns Profile load/save of `full` / websites list / nav. Once shapes + FormFields ship, Profile’s existing Contact Information `FormFields` pass will render the new fields as soon as that sibling wires `full` into edit values and ensures `contact.websites` is present on the values object.

## Stage 3: Core save contract — empty `full` + websites list

**Done when:** `save_candidate_data` recomputes `full` whenever the submitted (or resulting) `full` is missing/blank; `contact.websites` on save is always a list of non-empty trimmed strings (or omitted when not in the contact payload); non-list `websites` raises `ValueError`.

1. In `src/core/candidate.py` `save_candidate_data`, after the existing block that recomputes `full` when `first`/`last` are in `col_kwargs` and `full` is absent, add (or fold into one helper) handling for empty override:
   - If `"full" in col_kwargs` and `not str(col_kwargs["full"]).strip()`:
     - Resolve `first` / `last` from `col_kwargs` with fallback to `database.get_candidate(candidate_id)` existing columns (same pattern as the omit-full branch).
     - Set `col_kwargs["full"] = recompute_full_name(str(first), str(last))`.
   - Non-empty stripped `full` remains an explicit override (persist as submitted string after `str(val)` — keep current assignment; optionally `.strip()` the stored override — **do strip** so `"  Ada Lovelace  "` stores `"Ada Lovelace"`).

2. Still in `save_candidate_data`, inside the existing `if isinstance(contact, dict):` block (after or before `normalize_contact_urls(contact)`):
   - If `"websites" in contact`:
     - If `contact["websites"] is None`: set `[]`.
     - Elif `isinstance(..., list)`: set `[str(x).strip() for x in contact["websites"] if str(x).strip()]`.
     - Else: `raise ValueError("contact.websites must be a list of strings")`.
   - Do **not** invent a max length or entry cap.

3. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`:
   - On the `first`/`last`/`full`/`pronouns` bullet, change the `full` sentence to: `` `full` is recomputed from first+last on save when omitted or empty/whitespace; a non-empty value is an explicit override. ``
   - On the `contact.websites` table row description, append: ` (JSON string list; Profile shape type string_list).`

## Self-Assessment

**Scope:** `Single-Component` — config shapes + FormFields field type + one save-path rule in `candidate.py`; no Profile page rewrite, no Admin expand, no library migration.

**Conf:** `high` — patterns already exist (`DATA_SHAPES` contact remap from AST-1014, `recompute_full_name`, FormFields switch); gap is missing keys + list type + empty-full branch.

**Risk:** `Medium` — wrong `full` recompute could overwrite intentional blank intent, but AC requires empty→derived; websites coercion rejects non-lists so bad clients fail closed rather than corrupt the blob.

## Code rules check

| Rule | Status |
|------|--------|
| §1.3 DRY | Single recompute helper reused; websites coercion only in `save_candidate_data` next to URL normalize |
| §2.1 config | Field keys/types only in `DATA_SHAPES` / existing `CANDIDATE_LIBRARY_CONFIG` vocabulary — no new React field list |
| §2.4 batch | N/A — not a batch task |
| §2.6 state machine | Untouched |
| §3.3 imports | FormFields stays UI-only; core still imports config/database only |
| §3.5 naming | `string_list` snake_case type string matches existing shape types (`signature_image`, `textarea`) |
| Boundaries | No `CandidateProfile.tsx`, no nav, no Admin `edit.manage` expansion, no new contact blob keys |

## Review (build)

**Built:** `origin/sub/AST-1065/AST-1081-contact-shapes-websites-full` @ `de354de123ab419a547a97587f7c870b4e14f090`

Stages 1–3: `DATA_SHAPES` Contact Information adds `full`, `contact.websites` (`string_list`), `contact.reason_codes`; FormFields `string_list` Add/Remove (label `Add`); `save_candidate_data` empty-`full` → `recompute_full_name` + websites list coerce. Profile page/nav deferred to AST-1082. Tests deferred to Betty.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1081
**Publish ref:** `996e815a93611f7ca157836f48d7b03605b368e7`
**Overall:** DISCUSS

### What’s solid

- Stages 1–3 match the plan: `DATA_SHAPES` exposes `full` / `contact.websites` (`string_list`) / `contact.reason_codes`; FormFields renders `string_list` with Add/Remove; `save_candidate_data` empty/whitespace `full` → `recompute_full_name`, websites list coerce + `ValueError` on non-list.
- Boundaries held: no `CandidateProfile.tsx`, no Admin `edit.manage` expand, no new routes.
- One `merge-tests(AST-1081)` SHA; engineer `code()` commits stay off the test tree.

### Findings

**discuss:** straggler — `astral.git.engineer-test-tree-ban` excluded at plan time but in-scope on diff (`tests/**`, `docs/test-bible/**` via Betty). Product commits still clean; no engineer test-tree edit. No product action — note for resolve-child.

### Recommended actions

- Implementer: acknowledge straggler discuss; no `fix-now` product changes.
- AST-1082 owns Profile load/save / nav for the new shape fields.

## Resolution

**Date:** 2026-07-31  
**Outcome:** clean — no product changes.

- **fix-now:** none.
- **discuss (straggler):** Acknowledged. `astral.git.engineer-test-tree-ban` is correctly **conforms** on the tip — engineer `code(AST-1081)` commits exclude the test tree; `tests/**` + `docs/test-bible/**` arrive only via Betty `merge-tests(AST-1081)`. No plan/product edit required.
- Merged `origin/dev` onto the sub before publish (integration line advanced after review).
