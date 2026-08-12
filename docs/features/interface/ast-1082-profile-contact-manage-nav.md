<!-- linear-archive: AST-1082 archived 2026-08-11 -->

## Linear archive (AST-1082)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1082/candidate-profile-contact-manage-ui-nav-title-patterns-cleanup-update  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1065 — Update candidate ui for contact info  
**Blocked by / blocks / related:** parent: AST-1065

### Description

## What this implements

Profile loads and saves columns + contact (websites list, username-or-URL for GitHub/LinkedIn, editable `full` with derived default, title_patterns / reason_codes, signature paths under contact). Remove duplicate title-patterns from candidate navigation. After shapes sibling. Does **not** own library migration (AST-1014), preamble UI (AST-1017), or Admin Manage Candidates contact editing.

## Acceptance criteria

- [X] On Candidate Profile, Contact Information (including signature/image, title_patterns, reason_codes) read and save against name columns + `contact.*` — not `profile.*`.
- [X] A candidate can add, edit, and remove websites entries on Profile; after save and reload, those entries persist under `contact.websites`.
- [X] GitHub and LinkedIn fields accept username or full URL and persist in the normalized URL form consistent with the library URL bases.
- [X] `full` appears as an editable Profile field; when empty/unset it defaults to the library-derived first+last join; an explicit override persists and reloads.
- [X] Candidate navigation no longer exposes a duplicate title-patterns surface; title patterns are edited only via Profile Contact.
- [X] Save then reopen Profile shows the same contact values from the library homes.

## Boundaries

Does **not** own shapes/field contracts (sibling AST-1081). Does **not** own library migration (AST-1014), preamble UI (AST-1017), or Admin Manage Candidates contact editing.

## In scope

- [X] `astral.layers.ui-config-driven-business-logic` — Profile renders `DATA_SHAPES` Contact Information / tab sections; no hardcoded contact field list in React
- [X] `astral.ui.frontend-file-placement` — edits stay in `CandidateProfile.tsx` under `src/ui/frontend/src/pages/`
- [X] `astral.ui.naming-conventions` — page/component naming unchanged; shape label copy only for GitHub/LinkedIn
- [X] `astral.config.config-source-of-truth` — username-or-URL field labels live in `DATA_SHAPES` (not React-only helper text)
- [X] `astral.standards.in-scope-only` — Profile load/save mapping + label/nav hygiene only
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/interface/ast-1082-profile-contact-manage-nav.md`

## Considered but excluded

- [X] `pattern.config.config-block` / shape field contracts + `string_list` FormFields type — AST-1081
- [X] `astral.patterns.require-auth-on-protected-endpoints` — no new routes; existing `PUT /api/candidates/<id>/data` unchanged
- [X] AST-1014 library migration / `normalize_contact_urls` / name-column schema — already on integration line
- [X] Empty-`full` recompute + `contact.websites` list coerce in `save_candidate_data` — AST-1081
- [X] Admin Manage Candidates `edit.manage` contact expansion — boundary: Profile owns contact manage
- [X] AST-1017 preamble / intake UI — out of epic boundaries
- [X] `astral.git.engineer-test-tree-ban` — tests/bible owned by Betty at Code Complete; engineer commits product + plan only

## Notes for planning

After shapes sibling (AST-1081). Nav title-patterns route already absent on tip — Stage 2 verifies; labels for username-or-URL are this ticket.

## Git branch (authoritative)

Parent `ftr/AST-1065-update-candidate-ui-for-contact-info`; child `sub/AST-1065/AST-1082-profile-contact-manage-nav`. Publish to `origin/<publish-ref>` only.

### Comments

#### katherine — 2026-07-31T00:34:08.276Z
Publish-ref rebuilt without pull merge: reset to `b4678507`, new `resolve(AST-1082): — clean` @ `ee30c9b2`. `validate-sub-log` exit 0.

#### chuckles — 2026-07-31T00:32:45.618Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed on `origin/sub/AST-1065/AST-1082-profile-contact-manage-nav` — commit `cdd683e4` (`Merge remote-tracking branch 'origin/dev' into sub/...`). @Katherine Johnson please rebuild/republish the sub tip without a git-pull merge (merge `origin/ftr/AST-1065-update-candidate-ui-for-contact-info` + `origin/dev` per orientation, keep vocabulary commits, push publish-ref). Stay User Testing.

— Chuckles

#### katherine — 2026-07-31T00:32:11.099Z
Radia discuss (C4 stragglers): acknowledged — no product fix. Resolution on plan @ `e4b88239` (`origin/sub/AST-1065/AST-1082-profile-contact-manage-nav`).

#### radia — 2026-07-31T00:24:58.350Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1082
**Publish ref:** `b46785074c9860e0c84e99355a4eeabe02597c71` (`origin/sub/AST-1065/AST-1082-profile-contact-manage-nav`)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1065/AST-1082-profile-contact-manage-nav` — layers `{core, ui, utils, docs}`; change_types `{add, modify}` (includes rolled-up AST-1081 + Betty tests on tip).

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1082)` on sub |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests`/`resolve` prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | Tip on `origin/sub/...` publish-ref |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1065/AST-1082-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | Merge origin/dev present; no illegal recipe |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1082 history |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub topology |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1065` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Plan stop→parent path; no product decision open |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match this ticket’s `code()` |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child under AST-1065 |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `test`/`merge-tests` own bible + tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Product commits on allowed paths |
| astral.agent.confidence-bounds | scoped | conforms | No graded/confidence path |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` work (core present via 1081 rollup) |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector work |
| astral.batch.batch-id-first | scoped | conforms | Not a batch path |
| astral.batch.batch-id-format | scoped | conforms | Not a batch path |
| astral.batch.claim-process-release | scoped | conforms | Not a batch path |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | scoped | conforms | Username-or-URL copy in `DATA_SHAPES` labels |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths `artifacts/**`/`scripts/spikes/**` absent |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan docs, not spike output |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One AST-1082 plan file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits stay off `src/` / features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` excludes test tree |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external I/O; core only via 1081 rollup |
| astral.layers.import-direction | scoped | conforms | Profile UI→api; labels in utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` in diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Renders shapes; no hardcoded contact field list |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult path |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No new routes; existing PUT |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new data-layer swallow |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` in diff |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single `editValuesFromCandidate` for load + post-save |
| astral.standards.in-scope-only | scoped | conforms | This ticket’s commits: Profile map + labels only |
| astral.standards.logging-via-utils | scoped | conforms | No new print/`logging` |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in Profile page + config labels |
| astral.standards.no-hardcoded-sets | scoped | conforms | No invented contact vocabulary in React |
| astral.standards.public-then-helpers | scoped | conforms | Mapping helper only |
| astral.standards.utils-data-late-import-only | scoped | conforms | Label strings only in config |
| astral.state.core-decides-transitions | scoped | conforms | Candidate state machine untouched |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | conforms | Edits `CandidateProfile.tsx` under `pages/` |
| astral.ui.naming-conventions | scoped | conforms | Page name unchanged; label copy in shapes |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker/deploy change |

## Pattern conformance

none cited (ticket cites astral statutes; covered in full-set sweep). Sibling `pattern.config.config-block` / `string_list` owned by AST-1081.

## Plan adherence

Stages 1–2 match. Self-Assessment Scope `Single-Component` matches this ticket’s footprint (`CandidateProfile.tsx` + label strings). AC5 satisfied by confirmed absence of Title Patterns nav (no route/nav edit). Boundaries vs AST-1081 shapes/core coerce held in `code(AST-1082)` commits.

## Findings

**discuss:** C4 stragglers — Joan Excluded (plan Files Changed = Profile + labels) but in-scope on three-dot via AST-1081 rollup + Betty tests/docs: `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.batch.batch-id-first`, `astral.batch.batch-id-format`, `astral.batch.claim-process-release`, `astral.batch.entity-agent-responses-latest-only`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.core-vs-external-bright-line`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.state.core-decides-transitions`, `astral.state.no-daisy-chain-in-run`. All scored **conforms**. No product fix — resolve-child acknowledge.

## Notes

- Plan-rubric verdict attached (APPROVED).
- §5f/§5g N/A for this ticket’s surface.
- `docs()` append pushed to publish-ref.

## What’s solid

`full` always on edit values so PUT cannot omit it beside first/last; websites coerced to `string[]` for `string_list`; labels for username-or-URL live in config.

context_tokens≈48000

#### betty — 2026-07-31T00:22:28.371Z
## QA test manifest

`merge-tests(AST-1082)` → `origin/sub/AST-1065/AST-1082-profile-contact-manage-nav` @ `9ab0d73f` (origin/tests `5e567d3d`).

### Classification

1. **Existing coverage:** `test_routes.test.tsx` (`candidate/title_patterns` absent); AST-1081 shapes/`string_list`/empty-full (already on tip).
2. **Broken / obsolete:** Profile GET mock omitted top-level `full` — revised in-place for load mapping.
3. **Gaps (this pass):** §6c Profile — PUT includes `full` (override + cleared `""`); `contact.websites` `[]` normalize + Add round-trip; no `profile` key; username-or-URL labels; Title Patterns tab on Profile. Config — GitHub/LinkedIn labels; Candidate NAV omits Title Patterns; Profile shapes keep `contact.title_patterns` section.

**Integration:** no existing Profile contact round-trip scenario — no revision.

### Manifest (run on publish tip after merge `origin/ftr/…`)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1082ProfileContactLabelsNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/test_routes.test.tsx
```

### Bible shasums (`origin/sub/…` tip)

- `docs/test-bible/frontend/pages.md` `150abedb6732f1adeff3ec2f9077daa3892ba285`
- `docs/test-bible/utils/config.md` `0b6768e32b44d4d9a83ff78c5d70ef3333d080d6`

#### joan — 2026-07-31T00:16:19.486Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1082
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Profile Contact binds columns + `contact.*` (not `profile.*`) | Stage 1 `editValuesFromCandidate` + FormFields/TabbedTextArea shapes render |
| AC2 websites add/edit/remove; persist `contact.websites` | Stage 1 websites normalize to `string[]` + FormFields `string_list` (AST-1081) |
| AC3 GitHub/LinkedIn username-or-URL → normalized URL | Stage 1 smoke + existing `normalize_contact_urls`; Stage 2 labels |
| AC4 editable `full` empty→derived; override persists | Stage 1 always include `full` on values; empty clear → AST-1081 recompute |
| AC5 no duplicate title-patterns nav; edit via Profile Contact | Stage 2 NAV/routes hygiene (verify-or-remove); keep Profile Title Patterns section |
| AC6 save then reopen same values | Stage 1 load + post-Save remap via same helper |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 Profile load/save | Purpose Profile speaks contact; Functional scope manage contact + round-trip |
| Stage 2 labels + nav hygiene | Functional scope username-or-URL UX copy + nav cleanup |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Sub publish path only |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1065/AST-1082-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1065 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | API reject stop→parent comment path defined |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Interface scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded/confidence path |
| astral.config.config-source-of-truth | conforms | Username-or-URL copy in DATA_SHAPES labels; no React-only helpers |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src |
| astral.layers.import-direction | conforms | Profile UI→api only; config label edit in utils |
| astral.layers.ui-config-driven-business-logic | conforms | Renders shapes; no hardcoded contact field list |
| astral.patterns.require-auth-on-protected-endpoints | conforms | No new routes; existing PUT |
| astral.standards.data-raises-caller-logs | conforms | No data-layer work |
| astral.standards.debug-contract-gated | conforms | No new debug surface |
| astral.standards.dry-and-focused-functions | conforms | Single editValuesFromCandidate for load + post-save |
| astral.standards.in-scope-only | conforms | No 1081/1014/Admin/preamble creep |
| astral.standards.logging-via-utils | conforms | No new logging |
| astral.standards.no-cross-contamination | conforms | Stays in Profile page + config labels |
| astral.standards.no-hardcoded-sets | conforms | No invented contact vocabulary in React |
| astral.standards.public-then-helpers | conforms | Helper mapping only; no scattered public API |
| astral.standards.utils-data-late-import-only | conforms | Config label strings only |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.ui.frontend-file-placement | conforms | Edits CandidateProfile.tsx page only |
| astral.ui.naming-conventions | conforms | Page name unchanged; shape label copy only |
| astral.ui.single-gunicorn-worker | conforms | No worker/deploy change |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers ∩ plan empty
- astral.agent.grade-vector-validation — layers ∩ plan empty
- astral.batch.batch-id-first — layers ∩ plan empty
- astral.batch.batch-id-format — layers ∩ plan empty
- astral.batch.claim-process-release — layers ∩ plan empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan empty
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.core-vs-external-bright-line — layers ∩ plan empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan empty
- astral.standards.database-header-inventory — layers ∩ plan empty
- astral.state.core-decides-transitions — layers ∩ plan empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan empty

## Findings

None fix-now.

**acceptable:** Stage 2 nav is verify-or-remove; tip already lacks Title Patterns nav — labels-only config change still meets AC5 when absence is confirmed. Self-assessment Conf high / Risk Medium honest (`full` always on PUT; websites coerce when non-array → `[]`).

**R6:** Definition fidelity pass for child #2. Shape-driven Profile (no parallel field list). Config labels for username-or-URL. File placement pass. Boundaries vs AST-1081/1014/1017/Admin respected. Depends on AST-1081 on ftr noted.

context_tokens≈42000

— Joan

#### katherine — 2026-07-31T00:14:18.352Z
Plan published: https://github.com/susansomerset/astral/blob/sub/AST-1065/AST-1082-profile-contact-manage-nav/docs/features/interface/ast-1082-profile-contact-manage-nav.md

**Scope:** Single-Component — Profile `editValuesFromCandidate` must include `full` (and normalize `contact.websites` to `string[]` on load); small `DATA_SHAPES` GitHub/LinkedIn label copy; nav duplicate already gone on tip.

**Conf:** high — concrete gap vs AST-1081 shapes already on `origin/ftr/AST-1065-…`; core normalize/empty-`full`/websites coerce already shipped.

**Risk:** Medium — omitting `full` on PUT while sending `first`/`last` continues to wipe explicit full-name overrides via save recompute.

---

# Candidate Profile contact manage UI + nav title-patterns cleanup

**Linear:** [AST-1082](https://linear.app/astralcareermatch/issue/AST-1082/candidate-profile-contact-manage-ui-nav-title-patterns-cleanup-update)
**Parent:** [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info)
**Publish ref:** `sub/AST-1065/AST-1082-profile-contact-manage-nav`

Wire Candidate Profile load/save so Contact Information (name columns + `contact.*`, including `full`, websites list, GitHub/LinkedIn, title_patterns, reason_codes, signatures) round-trips against the library homes shipped by AST-1014 / AST-1081 — not legacy `profile.*`. Confirm candidate navigation has no duplicate title-patterns surface (title patterns edit only via Profile Contact). Does **not** own shapes/`string_list` (AST-1081), library migration (AST-1014), preamble UI (AST-1017), or Admin Manage Candidates contact editing.

**Depends on:** AST-1081 (User Testing) — shapes expose `full`, `contact.websites` (`string_list`), `contact.reason_codes`; FormFields renders `string_list`; core empty-`full` + websites coerce + `normalize_contact_urls` already on `origin/ftr/AST-1065-update-candidate-ui-for-contact-info`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Include `full` in edit values; normalize `contact.websites` to `string[]` on load so FormFields/`string_list` and PUT body preserve overrides and list edits | ui |
| `src/utils/config.py` | Update Profile Contact `DATA_SHAPES` labels for GitHub / LinkedIn to username-or-URL copy; confirm Candidate `NAV_CONFIG` has no Title Patterns item (remove only if present) | utils |

**Out of Files Changed (sibling / already shipped):** `FormFields.tsx` `string_list` renderer, `save_candidate_data` empty-`full` / websites coerce / `normalize_contact_urls` → **AST-1081** / **AST-1014**. Admin `edit.manage` → leave unchanged. No new API routes. No `tests/` / bible (Betty).

## Stage 1: Profile load/save — `full` + contact round-trip

**Done when:** Selecting a candidate on Profile shows `full` and all Contact Information / tabbed contact fields from columns + `contact.*`; Save PUT body includes top-level `full` plus `contact` (with `websites` as an array when the user edited the list); after Save toast and reload (or Cancel→re-fetch path via response remap), the same values reappear — including normalized GitHub/LinkedIn URLs and websites entries. No `profile` key is written.

1. In `src/ui/frontend/src/pages/CandidateProfile.tsx`, update `editValuesFromCandidate` so the returned object is:
   ```ts
   {
     first: c.first ?? "",
     last: c.last ?? "",
     full: c.full ?? "",
     pronouns: c.pronouns ?? "",
     contact: (() => {
       const raw = (d.contact as Record<string, unknown>) ?? {}
       const websites = Array.isArray(raw.websites)
         ? raw.websites.map(v => String(v))
         : []
       return { ...raw, websites }
     })(),
     context: (d.context as Record<string, unknown>) ?? {},
     artifacts: (d.artifacts as Record<string, unknown>) ?? {},
   }
   ```
   Keep using this helper for both initial GET map and post-Save response remap (existing `handleSave` / load `useEffect`).

2. Do **not** invent a client-side first+last join for display defaults. Empty/whitespace `full` → library recompute is owned by `save_candidate_data` (AST-1081). Sending `full: ""` on Save (user cleared the field) must remain possible so that path runs; omitting `full` while still sending `first`/`last` would recompute and wipe an intentional override — that is why `full` must always be present on the values object.

3. Do **not** add a hardcoded contact field list in React. Continue rendering `sections[0]` via `FormFields` + `profile-contact-grid` split and `sections.slice(1)` via `TabbedTextArea` (Title Patterns, signatures, bio, etc. already bind `contact.*` / `context.*` from shapes).

4. Do **not** edit `src/ui/api/api_candidate.py` or `src/core/candidate.py` in this ticket unless a literal step fails because the API rejects a key — then stop and comment on the parent with the 🛑 Stage format. Expected path: existing `PUT /api/candidates/<id>/data` → `save_candidate_data(body)` already accepts name columns + `contact`.

5. Manual smoke (builder): with shapes from AST-1081 on the tip —
   - Edit Full Name to a non–first+last string → Save → reopen → same override.
   - Clear Full Name → Save → reopen → derived first+last join.
   - Add/edit/remove Websites rows → Save → reopen → same `contact.websites`.
   - Enter GitHub / LinkedIn as bare username → Save → reopen → full URL with library bases (`https://github.com/…`, `https://www.linkedin.com/in/…`).
   - Edit Title Patterns / Reason Codes / signature text on Profile tabs → Save → reopen → same under `contact.*`.

⚠️ **Decision:** Always include `websites: []` (or the loaded list) on the contact object at load time so `string_list` edits and JSON.stringify always send a list when the user touches the control, and so a missing blob key does not leave `getByPath` undefined in a way that drops later list writes. Core still coerces/strips empties on save.

## Stage 2: Username-or-URL labels + nav title-patterns hygiene

**Done when:** Profile Contact labels for GitHub and LinkedIn state username-or-URL; Candidate sidebar has no Title Patterns nav item / route; title patterns remain editable only under Profile’s Title Patterns tab (`contact.title_patterns`).

1. In `src/utils/config.py` `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information fields, change labels only (keys/types unchanged):
   - `contact.github` label → `"GitHub (username or URL)"`
   - `contact.linkedin_url` label → `"LinkedIn (username or URL)"`
   Do not add FormFields `placeholder` support. Do not change `normalize_contact_urls` or URL bases.

2. Inspect `NAV_CONFIG` Candidate group and `src/ui/frontend/src/routes.tsx`:
   - If any item/path for Title Patterns / `candidate/title_patterns` exists, remove that nav item and matching route (and delete any orphan page component only if it exists solely for that route).
   - If already absent (current tip: Candidate items are Intake, Profile, Strengths, Priorities, Deal Breakers, Backstory, Writing Preferences; routes test already asserts `candidate/title_patterns` is false), make **no** nav/route edit — labels-only change satisfies this stage’s file touch for config; leave routes.tsx alone.

3. Do **not** remove the Profile `DATA_SHAPES` section `"label": "Title Patterns"` / `contact.title_patterns` textarea — that is the single edit surface AC requires.

⚠️ **Decision:** Username-or-URL UX copy lives in shape labels (config source of truth), not React-only helper text — AST-1081 explicitly deferred that copy to this sibling; normalization stays in core.

## Self-Assessment

**Scope:** `Single-Component` — Profile edit-values mapping plus small `DATA_SHAPES` label (and nav only if a duplicate still exists); no core/API rewrite, no Admin expand.

**Conf:** `high` — gap is concrete (`full` missing from `editValuesFromCandidate`); shapes/`string_list`/normalize already on ftr from AST-1081; nav duplicate already gone on tip.

**Risk:** `Medium` — omitting `full` on PUT while sending `first`/`last` would keep wiping overrides; wrong websites normalize could clobber non-list blob data (mitigated by only coercing when not an array → `[]`, matching FormFields).

## Code rules check

| Rule | Status |
|------|--------|
| §1.3 DRY | Single `editValuesFromCandidate` for load + post-save; no parallel field list |
| §2.1 config | Field keys/types stay in `DATA_SHAPES`; only label strings change here |
| §2.4 batch | N/A |
| §2.6 state machine | Untouched |
| §3.3 imports | Profile stays UI-only (`api` + FormFields) |
| §3.5 naming / file placement | Page stays `CandidateProfile.tsx`; no new page file |
| `astral.layers.ui-config-driven-business-logic` | Renders resolved shapes; no invented contact vocabulary |
| Boundaries | No AST-1081 shape/type work, no Admin contact, no preamble, no library migration, no engineer test-tree edits |

## Review (build)

**Built:** `origin/sub/AST-1065/AST-1082-profile-contact-manage-nav` @ `071960d900b69d20c73e278c901d209a9f3eba9d`

Stages 1–2: `editValuesFromCandidate` always includes `full` and normalizes `contact.websites` to `string[]`; `DATA_SHAPES` GitHub/LinkedIn labels say username-or-URL; Candidate `NAV_CONFIG` / routes already omit title-patterns (no nav edit). Tests deferred to Betty.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1082
**Publish ref tip at review:** `9ab0d73fce5065bb150e1bca5619f68b282e6875`
**Overall:** DISCUSS

### What’s solid

- Stage 1: `editValuesFromCandidate` always sends `full` + normalizes `contact.websites` to `string[]` on load and post-Save remap; still shape-driven FormFields/TabbedTextArea (no hardcoded contact field list).
- Stage 2: GitHub/LinkedIn username-or-URL labels in `DATA_SHAPES`; Candidate `NAV_CONFIG` has no Title Patterns item (verify-only; no nav edit needed).
- Boundaries vs AST-1081 / Admin / preamble held in this ticket’s `code()` commits.

### Findings

**discuss:** C4 stragglers — Joan Excluded several statutes (plan Files Changed was Profile + label-only config) that are in-scope on `origin/dev...` three-dot because AST-1081 sibling + Betty `merge-tests` are on the tip. Sweep scores them **conforms**; no product action — resolve-child acknowledge.

### Recommended actions

- Implementer: acknowledge straggler discuss; no `fix-now` product changes.

## Resolution

**Date:** 2026-07-31  
**Outcome:** clean — no product changes.

- **fix-now:** none.
- **discuss (C4 stragglers):** Acknowledged. Statutes Joan excluded at plan time are in-scope on `origin/dev...` tip via AST-1081 rollup + Betty `merge-tests`; Radia scored them **conforms**. Engineer `code(AST-1082)` commits stay Profile map + `DATA_SHAPES` labels only. No plan/product edit required.
- Publish tip rebuilt on `b4678507` without a `git pull` / `Merge remote-tracking origin/dev` commit (merge-child hygiene).
