<!-- linear-archive: AST-1092 archived 2026-08-11 -->

## Linear archive (AST-1092)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1092/uat-profile-extra-binding-emails-resumemessages-email-labels  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1065 — Update candidate ui for contact info  
**Blocked by / blocks / related:** parent: AST-1065

### Description

## What failed

On Candidate Profile → Contact Information, the candidate can add websites, but cannot add **extra email addresses** for binding email sent to the platform. Existing email fields still use unclear labels (Contact Email / Reply Email) instead of purpose-named labels.

Archie (UAT): “You have the option to add websites but we need the candidate to be able to add "extra" email addresses for binding email sent to the platform. Also we should relabel the email fields as "Email for Resume" and "Email for Messages (if different)" … I consider this in scope for this ticket.”

## Expected

1. Profile Contact Information labels: `contact.contact_email` → **Email for Resume**; `contact.reply_email` → **Email for Messages (if different)**.
2. Candidate can add / edit / remove **extra** email addresses on Profile (same class of multi-entry UX as websites); those addresses participate in platform email **binding / lookup** (same vocabulary as `CANDIDATE_LOOKUP_CONFIG` email paths).
3. Save then reopen Profile shows the same email labels and extra-email list values from the library homes.

## Repro

1. Open Candidate → Profile → Contact Information on staging/`dev` after AST-1065 land.
2. Confirm websites Add/Remove exists; note there is no parallel control for extra binding emails.
3. Note Contact Email / Reply Email labels (not Resume / Messages).
4. Attempt to register an additional binding email beyond the two scalar fields — no Profile surface for it.

## Parent AC (quoted inline)

> On Candidate Profile, Contact Information (including signature/image, title_patterns, reason_codes) read and save against name columns + `contact.*` — not `profile.*`.
> A candidate can add, edit, and remove websites entries on Profile; after save and reload, those entries persist under `contact.websites`.
> Save then reopen Profile shows the same contact values from the library homes.

Archie UAT scope clarification (in-scope for this parent): extra binding emails + Resume/Messages labels.

## Diagnosis

* **Hypothesis:** Contact Information ships websites as `string_list` and two scalar emails (`contact.contact_email` / `contact.reply_email`) with legacy labels; bind/lookup only knows the configured email paths — there is no Profile multi-entry email list wired into that vocabulary, so candidates cannot register extra binding addresses the way they add websites.
* **Correct outcome:** Labels read Email for Resume / Email for Messages (if different); candidate can manage an extra-emails list on Profile; those values persist under the contact library home and are used for binding email sent to the platform; round-trip after save/reload.
* **Wrong fix to avoid:** Stuffing emails into `contact.websites`; Admin Manage Candidates contact editing; swallowing bind failures; inventing a Profile-only list that never registers on `CANDIDATE_LOOKUP_CONFIG` / uniqueness email paths; drive-by preamble/intake work.
* **Related siblings / contracts:** AST-1081 (shapes / `string_list`), AST-1082 (Profile manage + nav), AST-1014 (contact blob / name columns), AST-1045 uniqueness email vocabulary — extras must stay aligned with lookup/bind paths.

## Boundaries

* This bug does **not** change: preamble intake UI, Topic Menu, Admin Manage Candidates as a contact editor, candidate state machine, or unrelated contact keys (phone/GitHub/etc.) beyond what’s required for extra binding emails + the two label renames.
* "No more confusion" alone is **not** done — Parent AC round-trip + Correct outcome (labels + bindable extra emails) must hold.

## In scope

- [X] `astral.config.config-source-of-truth` — labels, `extra_emails` key, lookup `email_list_paths`, uniqueness `list_paths` in config
- [X] `astral.layers.ui-config-driven-business-logic` — Profile renders shape `string_list`; no hardcoded contact field list
- [X] `astral.ui.frontend-file-placement` — Profile page load/save normalize only
- [X] `astral.ui.naming-conventions` — shape labels; key `extra_emails`
- [X] `astral.standards.in-scope-only` — labels + bindable extras only
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/interface/ast-1092-uat-extra-binding-emails-labels.md`

## Considered but excluded

- [X] Admin Manage Candidates `edit.manage` / list email labels — Profile owns this UAT surface
- [X] FormFields `string_list` type introduction — AST-1081 already shipped
- [X] Stuffing extras into `contact.websites` — wrong fix on bug
- [X] Preamble / intake / Topic Menu — out of bug Boundaries
- [X] `astral.patterns.require-auth-on-protected-endpoints` — no new routes
- [X] `astral.git.engineer-test-tree-ban` — Betty owns tests at Code Complete

## Git branch (authoritative)

Parent `ftr/AST-1065-update-candidate-ui-for-contact-info`; child `sub/AST-1065/AST-1092-uat-extra-binding-emails-labels`. Publish to `origin/<publish-ref>` only.

### Comments

#### radia — 2026-07-31T03:42:41.325Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1092
**Publish ref:** `efdea153122e648410fd9b39ee2f0b7487b86fb0` (`origin/sub/AST-1065/AST-1092-uat-extra-binding-emails-labels`)
**Overall:** CLEAN

Diff: `origin/dev...origin/sub/AST-1065/AST-1092-uat-extra-binding-emails-labels` — layers `{core, ui, utils, docs}`; change_types `{add, modify}`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1092)` on sub |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | Tip on `origin/sub/...` publish-ref |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1065/AST-1092-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1092 history |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub topology |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1065` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Archie UAT scope already on bug; no open product call |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match product diff |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child under AST-1065 |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `test`/`merge-tests` own bible + tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Product commits on allowed paths |
| astral.agent.confidence-bounds | scoped | conforms | No graded/confidence path |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` work |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector work |
| astral.batch.batch-id-first | scoped | conforms | Not a batch path |
| astral.batch.batch-id-format | scoped | conforms | Not a batch path |
| astral.batch.claim-process-release | scoped | conforms | Not a batch path |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | scoped | conforms | Labels/key/lookup/uniqueness/shapes all in config |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths `artifacts/**`/`scripts/spikes/**` absent |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan + model docs, not spike output |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One AST-1092 plan file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits stay off `src/` / features |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code()` excludes test tree |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core save/bind only; no external I/O |
| astral.layers.import-direction | scoped | conforms | UI→api; core reads config |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` in diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Shape `string_list`; no hardcoded contact field list |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult path |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No new routes; existing PUT |
| astral.standards.data-raises-caller-logs | scoped | conforms | `ValueError` on non-list extra_emails |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` in diff |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shared coerce loop; reuses `_iter_uniqueness_path_values` |
| astral.standards.in-scope-only | scoped | conforms | Labels + bindable extras only; no Admin/preamble |
| astral.standards.logging-via-utils | scoped | conforms | No new print/`logging` |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in named layers/files |
| astral.standards.no-hardcoded-sets | scoped | conforms | Paths/keys in config; bind uses `email_list_paths` |
| astral.standards.public-then-helpers | scoped | conforms | Extends existing save/lookup helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data import change |
| astral.state.core-decides-transitions | scoped | conforms | Candidate state machine untouched |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | conforms | Profile page normalize only |
| astral.ui.naming-conventions | scoped | conforms | `extra_emails` key; shape labels only |
| astral.ui.single-gunicorn-worker | scoped | conforms | No worker/deploy change |

## Pattern conformance

none cited beyond astral statutes in ticket In scope (covered via full-set sweep). Reuses AST-1081 `string_list` (not reintroduced).

## Plan adherence

Stages 1–3 match. Self-Assessment Scope `Single-Component` matches the diff. Wrong fixes avoided (no websites-as-email; extras on lookup + uniqueness; Admin untouched).

## Findings

None.

## Notes

- `no plan-rubric verdict attached` — C4 straggler check N/A; not a block.
- §5f/§5g N/A.
- `docs()` append pushed to publish-ref.

## What’s solid

Separate `email_list_paths` keeps scalar readers honest; comment + code refuse walking all uniqueness list paths for bind; Profile always normalizes `extra_emails` to `string[]` for round-trip.

context_tokens≈42000

#### betty — 2026-07-31T03:40:20.769Z
## QA test manifest

`merge-tests(AST-1092)` → `origin/sub/AST-1065/AST-1092-uat-extra-binding-emails-labels` @ `46d2ae0b` (origin/tests `b07991e0`).

### Classification

1. **Existing coverage:** AST-1081 websites coerce / `string_list`; AST-1082 Profile full/websites (revised Add scope); AST-1047 lookup scalars.
2. **Broken / obsolete:** `TestAst1079ContactUniquenessConfig` `list_paths` websites-only — revised to include `contact.extra_emails`. AST-1082 websites Add used global Add — revised to Websites field scope.
3. **Gaps (this pass):** Resume/Messages + Extra emails labels/shape; library + `email_list_paths` + uniqueness align; save coerce; bind via extras only (not websites); §6c Profile extra_emails Add round-trip.

**FIX-UAT:** no `docs/test-bible/**` change on `origin/ftr/AST-1065-…` since last qa — no full bible re-read.

**Integration:** none — no revision.

### Manifest (run on publish tip after merge `origin/ftr/…`)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1092ExtraBindingEmailsConfig \
  tests/component/utils/test_config.py::TestAst1079ContactUniquenessConfig \
  tests/component/core/test_candidate.py::TestAst1092ExtraBindingEmails \
  tests/component/core/test_candidate.py::TestAst1081ContactShapesSaveContract \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx
```

### Bible shasums (`origin/sub/…` tip)

- `docs/test-bible/core/candidate.md` `0290de951c9fe9343cf225ef999da86e56c451c1`
- `docs/test-bible/utils/config.md` `d1b6f7d7b563f75a168da49b51300361460722c3`
- `docs/test-bible/frontend/pages.md` `45f3c2a9800cce1a853d769bf265b9fab63bf097`

#### katherine — 2026-07-31T03:32:41.847Z
Plan published: https://github.com/susansomerset/astral/blob/sub/AST-1065/AST-1092-uat-extra-binding-emails-labels/docs/features/interface/ast-1092-uat-extra-binding-emails-labels.md

**Scope:** Single-Component — `DATA_SHAPES` email label renames + new `contact.extra_emails` (`string_list`); lookup `email_list_paths` + uniqueness `list_paths`; save coerce + Profile normalize; bind expands list in `get_candidate_id_for_query`.

**Conf:** high — reuses AST-1081 `string_list` / websites coerce / uniqueness list walk; gap is missing key + list bind expansion.

**Risk:** Medium — forgetting lookup expansion leaves extras Profile-only (fails Correct outcome); walking all `list_paths` would wrongly bind websites.

---

# UAT: Profile extra binding emails + resume/messages email labels

**Linear:** [AST-1092](https://linear.app/astralcareermatch/issue/AST-1092/uat-profile-extra-binding-emails-resumemessages-email-labels)
**Parent:** [AST-1065](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info)
**Publish ref:** `sub/AST-1065/AST-1092-uat-extra-binding-emails-labels`

UAT fix: rename Profile Contact email field labels to purpose names, and let a candidate manage a multi-entry list of **extra** emails that persist under the contact library and participate in platform email **binding / lookup** (same vocabulary family as `CANDIDATE_LOOKUP_CONFIG`). Reuse existing `string_list` FormFields type (AST-1081). Does **not** stuff emails into `contact.websites`, expand Admin Manage Candidates contact editing, or touch preamble/intake.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): “On Candidate Profile, Contact Information … read and save against name columns + `contact.*` — not `profile.*`.” / “A candidate can add, edit, and remove websites entries on Profile; after save and reload, those entries persist under `contact.websites`.” / “Save then reopen Profile shows the same contact values from the library homes.” Archie UAT scope clarification on this parent: extra binding emails + Resume/Messages labels.
- **Correct outcome:** Labels read **Email for Resume** / **Email for Messages (if different)**; candidate can add/edit/remove an extra-emails list on Profile; those values persist under `contact.extra_emails` and bind via `get_candidate_id_for_query` the same way scalar contact/reply emails do; save then reopen shows the same list and labels.
- **Sibling check:** AST-1081 `string_list` + websites coerce remain; AST-1082 Profile `editValuesFromCandidate` pattern extended (not replaced); AST-1014 contact blob + AST-1045/1079/1080 uniqueness — extras register on lookup + uniqueness list vocabulary so bind and save-gate stay aligned.
- **Not sufficient:** Renaming labels alone, or a Profile-only list that never hits lookup/bind paths.
- **Wrong fix rejected:** Stuffing extras into `contact.websites`; Profile-only list omitted from `CANDIDATE_LOOKUP_CONFIG` / uniqueness; Admin Manage Candidates contact expand; inventing parallel React field list outside `DATA_SHAPES`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Rename Profile Contact email labels; add `extra_emails` to `contact_keys`; add `email_list_paths` on `CANDIDATE_LOOKUP_CONFIG`; add `contact.extra_emails` to uniqueness `list_paths`; expose `contact.extra_emails` `string_list` in `DATA_SHAPES` Contact Information; asserts | utils |
| `src/core/candidate.py` | Coerce `contact.extra_emails` like websites on save; expand `email_list_paths` in `get_candidate_id_for_query` | core |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Normalize `contact.extra_emails` to `string[]` on load/post-save remap (same as websites) | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `contact.extra_emails` + updated email label meanings | docs |

**Out of Files Changed:** Admin `edit.manage` / `list.manage` email labels (boundary: Profile owns this UAT surface). FormFields `string_list` renderer (already shipped). Preamble / intake / Topic Menu.

## Stage 1: Config — labels, library key, lookup + uniqueness vocabulary

**Done when:** Profile shapes show the new labels and a `string_list` for `contact.extra_emails`; `extra_emails` is in `contact_keys`; lookup exposes `email_list_paths`; uniqueness `list_paths` includes `contact.extra_emails`; import-time asserts pass.

1. In `src/utils/config.py` `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`, insert `"extra_emails"` after `"websites"` (keep tuple order otherwise unchanged).

2. In `CANDIDATE_LOOKUP_CONFIG`, after `email_paths`, add:
   ```python
   "email_list_paths": (
       "contact.extra_emails",
   ),
   ```
   Do **not** put `contact.extra_emails` into scalar `email_paths` — `_lookup_path_value` returns `""` for non-strings today.

3. In `CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"]`, add `"contact.extra_emails"` after `"contact.websites"` so each non-empty entry is a uniqueness token (existing list compare / AST-1080 enforcement).

4. After existing lookup/uniqueness asserts, add:
   - `assert isinstance(CANDIDATE_LOOKUP_CONFIG["email_list_paths"], tuple)`
   - For each path in `email_list_paths`: starts with `"contact."` and key is in `contact_keys`
   - Optionally assert `email_list_paths` entries also appear in uniqueness `list_paths` (same object membership or membership check) so bind and uniqueness cannot drift.

5. In `DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information fields:
   - Change `contact.contact_email` label → `"Email for Resume"`
   - Change `contact.reply_email` label → `"Email for Messages (if different)"`
   - Immediately after `contact.reply_email`, insert:
     ```python
     {"key": "contact.extra_emails", "label": "Extra emails (binding)", "type": "string_list"},
     ```
   Do **not** change Admin `edit.manage` / `list.manage` labels in this ticket.

6. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`:
   - Update `contact.contact_email` / `contact.reply_email` row descriptions to Resume / Messages purpose wording.
   - Add table row for `contact.extra_emails`: JSON string list of additional binding emails; Profile shape type `string_list`; included in lookup `email_list_paths` + uniqueness `list_paths`.

⚠️ **Decision:** New library key `extra_emails` (not reuse `websites`). Archie UAT requires bindable extras; parent’s “no new keys” boundary yields to the in-scope UAT clarification on the bug. Key must be registered in library + lookup list paths + uniqueness list paths — never Profile-only.

⚠️ **Decision:** `email_list_paths` on `CANDIDATE_LOOKUP_CONFIG` (sibling to scalar `email_paths`) instead of overloading `email_paths` with list-valued entries. Keeps scalar path readers honest; bind expands lists explicitly.

## Stage 2: Core — save coerce + bind lookup expansion

**Done when:** Saving `contact.extra_emails` yields a list of non-empty trimmed strings (or `[]`); non-list raises `ValueError`; `get_candidate_id_for_query` matches needles present only in `extra_emails` when unique.

1. In `src/core/candidate.py` `save_candidate_data`, inside the `if isinstance(contact, dict):` block next to websites coerce, add the same pattern for `"extra_emails"`:
   - `None` → `[]`
   - `list` → `[str(x).strip() for x in … if str(x).strip()]`
   - else → `raise ValueError("contact.extra_emails must be a list of strings")`
   Do not invent a max length or entry cap.

2. In `get_candidate_id_for_query`, after collecting scalar values from `email_paths` / `name_paths` / `slack_user_id_paths`, also expand each path in `CANDIDATE_LOOKUP_CONFIG["email_list_paths"]`:
   - Prefer reusing `_iter_uniqueness_path_values(candidate, path)` (already understands uniqueness `list_paths`) **or** inline the same list-walk if that helper requires the path to be in uniqueness `list_paths` (it does — Stage 1 already added the path there).
   - Append each non-empty stripped entry to `values` with the same casefold rule as scalar emails.
   - Do **not** walk uniqueness `list_paths` wholesale (that would treat `contact.websites` as bind emails).

3. Do **not** change uniqueness enforcement algorithms beyond the config path addition (AST-1080 already iterates `list_paths`).

## Stage 3: Profile load/save round-trip for `extra_emails`

**Done when:** Profile Contact Information shows the new labels and Extra emails `string_list`; Add/Remove/edit round-trips under `contact.extra_emails` with no `profile` key; empty missing blob key loads as `[]`.

1. In `src/ui/frontend/src/pages/CandidateProfile.tsx` `editValuesFromCandidate`, normalize `extra_emails` beside websites:
   ```ts
   const extra_emails = Array.isArray(raw.extra_emails)
     ? raw.extra_emails.map(v => String(v))
     : []
   return {
     // …existing first/last/full/pronouns…
     contact: { ...raw, websites, extra_emails },
     // …
   }
   ```
   Keep using this helper for GET load and post-Save remap. Do **not** hardcode a contact field list in React — shapes continue to drive which fields render.

2. Manual smoke: rename visible; add two extra emails → Save → reopen → same list; send/bind path that uses `get_candidate_id_for_query` with an extra-only address returns that candidate when unique (or unit-level via existing lookup tests once Betty covers — engineer does not edit tests).

## Self-Assessment

**Scope:** `Single-Component` — config vocabulary + Profile list normalize + small lookup/save coerce; no Admin/preamble rewrite.

**Conf:** `high` — reuses `string_list`, websites coerce, uniqueness `list_paths`, and lookup casefold; gap is the missing key + list expansion in bind.

**Risk:** `Medium` — wrong lookup expansion could bind on websites or miss extras; uniqueness list registration prevents silent cross-candidate collisions on extras when AST-1080 runs.

## Code rules check

| Rule | Status |
|------|--------|
| §1.3 DRY | Coerce pattern mirrors websites; list walk reuses `_iter_uniqueness_path_values` |
| §2.1 config | Key, labels, lookup/uniqueness paths live in `config.py` |
| §2.4 / §2.6 | N/A / untouched |
| §3.3 imports | UI→api only; core reads config |
| Boundaries | No Admin contact expand, no websites-as-email, no preamble |

## Review (build)

**Built:** `origin/sub/AST-1065/AST-1092-uat-extra-binding-emails-labels` @ `766cb39e8eb4772919282a589cc507c6bb59c8de`

Stages 1–3: `extra_emails` in library + lookup `email_list_paths` + uniqueness `list_paths`; Profile Resume/Messages labels + `string_list`; save coerce mirrors websites; bind expands list emails only (not websites); Profile load/remap normalizes `extra_emails` to `string[]`. Tests deferred to Betty.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1092
**Publish ref tip at review:** `46d2ae0b1dd5ac6a6676410ec9c4446eebe4327f`
**Overall:** CLEAN

### What’s solid

- Stages 1–3: config vocabulary (`extra_emails`, `email_list_paths`, uniqueness `list_paths`, Resume/Messages labels, shape `string_list`); save coerce shared with websites; bind expands list emails only (explicitly not websites); Profile normalize mirrors websites pattern.
- Import-time asserts keep bind list paths ⊆ uniqueness list paths and `contact_keys`.
- Boundaries held: no Admin expand, no websites-as-email, no new routes.

### Findings

None.

### Recommended actions

- Implementer: none for product; proceed resolve-child → User Testing.

## Resolution

**Date:** 2026-07-31  
**Outcome:** clean — no product changes.

- **fix-now:** none.
- **discuss / advisory:** none.
- Radia Overall **CLEAN**; Findings none. Intake of `docs(AST-1092): Radia review — clean` @ `efdea153` already on publish tip.
