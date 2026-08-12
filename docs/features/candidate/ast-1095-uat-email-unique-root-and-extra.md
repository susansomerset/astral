<!-- linear-archive: AST-1095 archived 2026-08-11 -->

## Linear archive (AST-1095)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1095/uat-new-email-must-be-unique-vs-all-root-and-extra-emails  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1045 — Verify unique contact info  
**Blocked by / blocks / related:** parent: AST-1045

### Description

## What failed

When a new email is added for a candidate, uniqueness is not reliably enforced against the whole candidate table for both root email addresses (`contact.contact_email` / `contact.reply_email`) and extra emails (`contact.extra_emails`). AST-1065 UI scope clarified that adding an email must reject if that address already exists anywhere on any other candidate (root or extra).

## Expected

Adding any email (root field or an extra-email entry) hard-fails when that address (casefold) is already held by another candidate as a root email or as an extra email. The other candidate is unchanged. Caller gets a clear domain error suitable for toast/UI.

## Repro

1. Candidate A has root email `a@example.com` (and/or that address in `extra_emails`).
2. On Candidate B, add `a@example.com` as a new root email or as a new extra email.
3. Save contact.
4. Observe: save should refuse; today it may allow depending on which field/path was written.

## Parent AC (quoted inline)

> 1. Saving contact data for a candidate that would duplicate a uniqueness-scoped contact value already held by a different candidate is refused; the other candidate's data is unchanged.
> 2. A refused uniqueness save surfaces a clear error to the save caller suitable for UI/API display.
> 3. After enforcement, two live candidates cannot both hold the same uniqueness-scoped email (going forward).

## Diagnosis

* **Hypothesis:** Cross-candidate email uniqueness must treat root emails and `extra_emails` as one shared pool across the whole candidate table on every email-add / contact-save path. AST-1065 clarified root vs extra; the save gate may miss a path combination or a write path may bypass the gate.
* **Correct outcome:** Any new email value is unique across all candidates' root emails and extra emails; collision hard-fails with a clear domain error.
* **Wrong fix to avoid:** UI-only toast without backend refusal; checking only root-vs-root or only extra-vs-extra; catch-all swallow; Profile rewrite under AST-1065.
* **Related siblings / contracts:** AST-1079; AST-1080; soft-related AST-1065 (UI surfaces error only).

## Boundaries

- [X] Does not change Profile/Admin UI (AST-1065), contact library (AST-1014), Slack Contact uniqueness, or candidate state machine.
- [X] No-more-error alone is not done — Parent AC + Correct outcome must hold for root↔extra cross collisions.

## Acceptance criteria

- [X] 1. Adding a root email that casefold-matches another live candidate's root or `extra_emails` entry is refused; other candidate unchanged.
- [X] 2. Adding an `extra_emails` entry that casefold-matches another live candidate's root or `extra_emails` entry is refused; other candidate unchanged.
- [X] 3. Refused save raises the existing toast-ready domain `ValueError` for callers (UI/API).
- [X] 4. Uniqueness email pool is config-driven: `email_paths` ∪ `email_list_paths` under email compare (not extras-only-as-generic-list beside websites).

## In scope

- [X] Explicit shared email pool on `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` (`email_list_paths` by identity from lookup; `list_paths` websites-only)
- [X] Gate collect / within-dedupe / cross-collision walks `email_list_paths` with email compare (`src/core/candidate.py`)
- [X] Initiate coerce parity for `extra_emails` / websites before uniqueness gate
- [X] `astral.config.config-source-of-truth` — email pool membership + compare in config
- [X] `astral.standards.no-hardcoded-sets` — no inline extra-email uniqueness sets in core
- [X] `astral.standards.data-raises-caller-logs` — core raises; callers surface
- [X] `astral.standards.debug-contract-gated` — existing Style D on enforce when debug=True
- [X] `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` — gate stays in core
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/candidate/ast-1095-uat-email-unique-root-and-extra.md`

## Considered but excluded

- [X] Profile / Admin contact UI / toast redesign — AST-1065 (`src/ui/`)
- [X] Contact library schema / name columns — AST-1014
- [X] `get_candidate_id_for_query` match-semantics rework — already expands `email_list_paths` (AST-1092 / AST-1047)
- [X] Slack Contact / Estelle uniqueness — AST-1043 / AST-1046
- [X] Candidate state machine / batch dispatch — N/A
- [X] Legacy duplicate cleanup / migration — parent OQ#4

## Notes for planning

UAT bug under AST-1045 (User Testing). After AST-1079 / AST-1080 / AST-1092 vocabulary for extras.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1045-verify-unique-contact-info`, child `sub/AST-1045/AST-1095-uat-email-unique-root-and-extra`. Created at dispatch-parent / fix-uat.

### Comments

#### ada — 2026-07-31T04:32:07.728Z
origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra @ 61f95c2c · §9a clean · ftr dry-run clean

#### ada — 2026-07-31T04:28:11.587Z
[check-linear] blocked: §9a dry-run into origin/dev conflicts; cannot absorb origin/dev onto this sub (validate-sub-log rejects pull-merge ancestry).

@chuckles — please merge origin/dev → origin/ftr/AST-1045-verify-unique-contact-info (product + test-tree as needed). Ada will rebuild origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra on the refreshed ftr tip and re-run §9a.

Conflict surfaces vs origin/dev today:
- src/utils/config.py (uniqueness list_paths / email_list_paths asserts)
- src/core/candidate.py (coerce helper vs inline)
- docs/test-bible/core/candidate.md, docs/test-bible/utils/config.md
- tests/component/core/test_candidate.py, tests/component/utils/test_config.py

Radia fix-now addressed on tip 36d40a7f (product scoped; get_candidate_id_for_query unchanged vs ftr). §9a into ftr: OK. validate-sub-log: OK. Stay Review Posted.

#### radia — 2026-07-31T04:20:13.811Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1095
**Publish ref:** `adb3f86a2b5b75e9950347cfe4630b77d150e053` (`origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra`)
**Overall:** FIX-NOW

Diff: `origin/dev...origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra` (same product delta as `origin/ftr...HEAD` for this tip). Paths: `src/core/candidate.py`, `src/utils/config.py`, plan doc, Betty test-tree. Layers: `core`, `utils`, `docs`. Change types: `add`, `modify`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No graded-confidence / consult work |
| astral.agent.do-task-delegation | scoped | conforms | No do_task orchestration rewrite |
| astral.agent.grade-vector-validation | scoped | needs-discussion | Tip also adds EMBEDDED_EVALUATE_JD_CRITERIA + craft merge (out of ticket; see findings) |
| astral.batch.batch-id-first | scoped | conforms | No batch claim API changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id work |
| astral.batch.claim-process-release | scoped | conforms | No batch processing |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_data RESPONSE work |
| astral.config.config-source-of-truth | scoped | conforms | Email pool membership intended in uniqueness config |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths {artifacts/**,scripts/spikes/**} no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan only |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single docs/features/candidate/ast-1095-….md |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty owns test-tree + merge-tests only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits exclude tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Gate stays in core; no external I/O |
| astral.layers.import-direction | scoped | conforms | Core → utils config + database |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} ∩ {core,utils,docs}=∅ |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No UI edits; DATA_SHAPES smuggle is config not UI layer |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult/render_verdict |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers {ui} ∩ {core,utils,docs}=∅ |
| astral.standards.data-raises-caller-logs | scoped | conforms | Uniqueness still raises toast-ready ValueError |
| astral.standards.database-header-inventory | scoped | not-applicable | layers {data} ∩ {core,utils,docs}=∅ |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug on enforce path |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shared list-dedupe helper for email + websites lists |
| astral.standards.in-scope-only | scoped | violates | Tip includes AST-1085/1087–1090 / DATA_SHAPES / full-name / craft hunks outside Files Changed |
| astral.standards.logging-via-utils | scoped | conforms | No new logging facade |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in src layered tree |
| astral.standards.no-hardcoded-sets | scoped | conforms | Uniqueness walk uses config paths; coerce keys match plan step 3 |
| astral.standards.public-then-helpers | scoped | conforms | Helpers remain with contact uniqueness helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data |
| astral.state.core-decides-transitions | scoped | conforms | No candidate state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job-state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No dispatch daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers {ui} ∩ {core,utils,docs}=∅ |
| astral.ui.naming-conventions | scoped | not-applicable | layers {ui} ∩ {core,utils,docs}=∅ |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single merge-tests(AST-1095) |
| orch.git.commit-vocabulary | universal | conforms | plan/docs/code/test/merge-tests/docs(review) |
| orch.git.flow-direction-inviolable | universal | conforms | Publish only to origin/sub/AST-1045/AST-1095-… |
| orch.git.ftr-sub-topology | universal | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | ftr merge clean before docs() |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None on tip |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub/AST-1045/AST-1095-… |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree astral-AST-1045 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT Correct outcome cites parent AC |
| orch.pipeline.plan-is-bible | universal | violates | Diff exceeds Files Changed; also edits get_candidate_id_for_query contrary to plan |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review |
| orch.pipeline.status-gates-skill-entry | universal | needs-discussion | Tip already has resolve() docs before Review Posted (Linear still Tests Passed) |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer Ada stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Role hooks respected on docs() |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| shared email pool on uniqueness config / gate | conforms (intent) | email_list_paths + gate walk present |

none cited under `astral.patterns.*` beyond statutes table.

## Plan adherence

Stage 1 uniqueness intent matches the plan (email_list_paths identity, websites-only list_paths, gate/initiate coerce). **Self-Assessment Single-Component is false on the tip:** `code(AST-1095)` vs `origin/ftr` also adds GAZE_EMAIL / METEORITE_EMAIL_PARSE / TASK_CONFIG rows, EMBEDDED_EVALUATE_JD_CRITERIA, DATA_SHAPES Profile field edits, save full-name rewrite, craft_jobdesc/evaluate_jd rubric merge, and `get_candidate_id_for_query` email_list expansion (plan: do not edit). ftr baseline lacked AST-1092 `email_list_paths` / `extra_emails` in contact_keys — those prerequisites are reasonable; the rest is smuggled ancestry.

## Findings

**fix-now:** `astral.standards.in-scope-only` / `orch.pipeline.plan-is-bible` — strip unrelated hunks from `src/utils/config.py` + `src/core/candidate.py` so the tip only contains Stage 1 uniqueness + minimal prerequisites for `email_list_paths` / `contact_keys` `extra_emails` (or merge AST-1092 onto ftr first, then rebuild a clean 1095 tip).

**fix-now:** Revert `get_candidate_id_for_query` changes unless plan/Linear scope is expanded (plan Explicitly excluded).

**discuss:** Premature `resolve(AST-1095)` docs claiming “no Radia fix-now” before this review — ignore that outcome; Linear was correctly still Tests Passed.

**discuss:** Joan plan-rubric verdict attachment absent (`no plan-rubric verdict attached`).

No other fix-now on the uniqueness helpers themselves once scope is cleaned.

## What’s solid

Shared email-pool wiring in uniqueness helpers is the right UAT fix shape once the tip is narrowed.

## Notes

Baseline for judgment: `origin/ftr/AST-1045-verify-unique-contact-info` (`fc00952c`) — tip is 7 commits ahead including this docs() review.

context_tokens≈52000

#### betty — 2026-07-31T04:13:32.418Z
QA manifest (FIX-UAT) — `origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra` @ `26f298af` (`merge-tests(AST-1095): origin/tests cd23193d`).

1. `tests/component/utils/test_config.py::TestAst1095EmailUniqueRootAndExtraConfig` — uniqueness `email_list_paths` identity; `list_paths` websites-only
2. `tests/component/utils/test_config.py::TestAst1079ContactUniquenessConfig` — revised (extras off `list_paths`)
3. `tests/component/utils/test_config.py::TestAst1092ExtraBindingEmailsConfig` — revised (extras via `email_list_paths`)
4. `tests/component/core/test_candidate.py::TestAst1095EmailUniqueRootAndExtra` — root↔extra / extra↔extra cross hard-fail; within collapse; initiate coerce + collision
5. `tests/component/core/test_candidate.py::TestAst1080ContactUniqueness` — base gate still green

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1095EmailUniqueRootAndExtraConfig \
  tests/component/utils/test_config.py::TestAst1079ContactUniquenessConfig \
  tests/component/utils/test_config.py::TestAst1092ExtraBindingEmailsConfig \
  tests/component/core/test_candidate.py::TestAst1095EmailUniqueRootAndExtra \
  tests/component/core/test_candidate.py::TestAst1080ContactUniqueness \
  -q
```

Bible sha256 @ publish tip:
- `docs/test-bible/utils/config.md` `7b72857a1f598be150bb5ac096e6e1b352e271665353046f4f3492b493e71176`
- `docs/test-bible/core/candidate.md` `6bffb4f066862910ae36472ced07ea33ec56e37ee289fafdf8ada29988cddd83`

— Betty

#### ada — 2026-07-31T04:11:38.955Z
`origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra` @ `673cfc32` (code `a5d8c1a2`).

Betty: existing `tests/component/utils/test_config.py` asserts still expect `contact.extra_emails` in uniqueness `list_paths` — product now uses `email_list_paths` (websites-only `list_paths`). Please revise those + add root↔extra matrix coverage on the gate.

#### ada — 2026-07-31T04:05:50.661Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra/docs/features/candidate/ast-1095-uat-email-unique-root-and-extra.md

`origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra` @ `df563130`

**Scope:** Single-Component — uniqueness config email-pool vocabulary + gate collect/dedupe/cross + initiate coerce in `src/utils/config.py` / `src/core/candidate.py`.

**Conf:** high — AST-1080 gate and AST-1092 `email_list_paths` already exist; this ticket makes root↔extra a first-class email pool under email compare.

**Risk:** Medium — wrong pool wiring can miss cross-candidate email leaks or over-collapse within-candidate lists; limited to gated contact write paths.

---

# UAT: new email must be unique vs all root and extra emails

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1095/uat-new-email-must-be-unique-vs-all-root-and-extra-emails  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info  

**Publish ref (origin):** `sub/AST-1045/AST-1095-uat-email-unique-root-and-extra`  
**Parent integration ref:** `ftr/AST-1045-verify-unique-contact-info`

UAT fix under AST-1045: treat every candidate email — root scalars (`contact.contact_email` / `contact.reply_email`, plus transitional `profile.*`) and list entries in `contact.extra_emails` — as **one shared uniqueness pool** across the live candidate table on every contact write path that already runs the AST-1080 gate. Collision hard-fails with the existing toast-ready `ValueError`. Does **not** change Profile/Admin UI, library schema, Slack Contact, or the candidate state machine.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): “Saving contact data for a candidate that would duplicate a uniqueness-scoped contact value already held by a different candidate is refused; the other candidate's data is unchanged.” / “A refused uniqueness save surfaces a clear error to the save caller suitable for UI/API display.” / “After enforcement, two live candidates cannot both hold the same uniqueness-scoped email (going forward).”
- **Correct outcome:** Adding any email (root field or an `extra_emails` entry) hard-fails when that address (casefold) is already held by another live candidate as a root email **or** as an extra email; the other candidate is unchanged; caller gets the existing domain error suitable for toast/UI.
- **Sibling check:** AST-1079 uniqueness vocabulary + AST-1080 save gate remain the home; AST-1092 added `extra_emails` / `email_list_paths` and parked extras under uniqueness `list_paths` next to websites — this ticket makes the **email** shared pool explicit (email scalars + email list paths under email compare) so root↔extra cannot drift if list compare or list membership changes. Soft-related AST-1065 still only surfaces the error.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** UI-only toast without backend refusal; checking only root-vs-root or only extra-vs-extra; catch-all swallow; Profile rewrite under AST-1065; stuffing extras into `websites` for uniqueness.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `email_list_paths` on `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` by identity from lookup; keep `contact.extra_emails` out of uniqueness `list_paths` (websites-only lists); update asserts/comments so email pool = `email_paths` ∪ `email_list_paths` under `compare["email"]` | utils |
| `src/core/candidate.py` | Collect / within-dedupe / cross-collision walk `email_list_paths` with email compare (skip those paths when walking `list_paths`); coerce `extra_emails` (and websites) on initiate paths before the gate, matching `save_candidate_data` | core |

**Out of Files Changed:** Profile/Admin UI (`src/ui/`), contact library schema (AST-1014), Slack Contact / Estelle, `get_candidate_id_for_query` match semantics (already expands `email_list_paths`), data-layer schema, tests/bible (Betty).

---

## Stage 1: Explicit shared email pool (config + gate)

**Done when:** Uniqueness config names `email_list_paths` (same object as lookup); uniqueness `list_paths` is non-email lists only (`contact.websites`); `_collect_uniqueness_tokens_from_*`, `_dedupe_contact_within`, and `_find_cross_candidate_contact_collision` treat root email paths and `email_list_paths` as one casefold email pool; `save_candidate_data` / `initiate_candidate` / `initiate_prospect_candidate` refuse cross-candidate root↔extra and extra↔root collisions with the existing toast message; initiate paths coerce `extra_emails` like save before the gate; other candidate rows are unchanged on refuse.

1. In `src/utils/config.py` `CANDIDATE_CONTACT_UNIQUENESS_CONFIG`:
   - Add `"email_list_paths": CANDIDATE_LOOKUP_CONFIG["email_list_paths"]` (same object identity — bind vocabulary and uniqueness share one list-email set).
   - Change `"list_paths"` to **only** `("contact.websites",)` — do **not** keep `contact.extra_emails` in `list_paths` (extras are email-pool members via `email_list_paths`, not generic list tokens beside websites).
   - Update the block comment: email uniqueness pool = `email_paths` ∪ `email_list_paths` with `compare["email"]`; `list_paths` are non-email list identity fields with `compare["list"]`.
   - Replace the assert that required every lookup `email_list_paths` entry ∈ uniqueness `list_paths` with:
     - `assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_list_paths"] is CANDIDATE_LOOKUP_CONFIG["email_list_paths"]`
     - each uniqueness `email_list_paths` entry starts with `"contact."` and key ∈ `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`
     - no uniqueness `email_list_paths` entry appears in uniqueness `list_paths` (no double registration)
   - Keep existing asserts that still apply (`email_paths` / `slack_user_id_paths` identity, compare modes, scopes, scalar/list path shapes).

⚠️ **Decision — email pool is first-class, not “extras happen to sit in list_paths”:** AST-1092 correctly registered extras for bind + parked them on uniqueness `list_paths`. UAT requires root and extra to be one **email** pool; parking extras next to websites makes email uniqueness depend on list compare and list membership. Promote `email_list_paths` onto the uniqueness block (by identity) and leave `list_paths` for non-email lists.

2. In `src/core/candidate.py`, update uniqueness helpers (same private helpers introduced by AST-1080 — do **not** add a second gate):

   **`_iter_uniqueness_path_values`**
   - Treat a path as list-valued when it is in `cfg["list_paths"]` **or** `cfg["email_list_paths"]` (same walk: `candidate_data` → segments → list/str entries). Scalar/email-scalar paths still use `_lookup_path_value`.

   **`_collect_uniqueness_tokens_from_candidate`**
   - Emit tokens in this order with these compare modes:
     1. `email_paths` → `compare["email"]`
     2. `email_list_paths` → `compare["email"]` (one token per non-empty list entry)
     3. `scalar_paths` → `compare["scalar"]`
     4. `list_paths` → `compare["list"]` (websites only after Stage 1 config)
     5. `slack_user_id_paths` → `compare["slack_user_id"]`
   - Do **not** also emit `email_list_paths` entries a second time via `list_paths`.

   **`_dedupe_contact_within`**
   - After scalar email / scalar / slack collapse into `seen`, process **email list** keys from `email_list_paths` (`contact.<key>` only) with `compare["email"]` using the same keep-first list rebuild as today’s list-path dedupe.
   - Then process remaining `list_paths` with `compare["list"]` as today.
   - Within one candidate, a root email and the same address in `extra_emails` still collapses (extra entry dropped / root kept when root is earlier in path order).

   **`_find_cross_candidate_contact_collision` / `_enforce_contact_uniqueness`**
   - No new public API. Collision detection continues to use the shared compare-token set from `_collect_*` — after the collect change, root↔extra and extra↔root across candidates hard-fail.
   - Keep the existing toast message shape exactly:
     `This contact info is already used by another candidate ({value}).`
   - Include `email_list_paths` when building `display_by_path` for contact.* paths (same pattern as today’s list_paths loop).
   - Style D: keep existing `enforce_contact_uniqueness` debug lines when `debug=True`; no new debug surface required beyond whatever already fires on the touched save path.

3. **Initiate coerce parity** — in `initiate_candidate` and `initiate_prospect_candidate`, when `contact` is a `dict`, before `normalize_contact_urls` / `_enforce_contact_uniqueness`, apply the same `websites` / `extra_emails` coerce block already used in `save_candidate_data` (`None`→`[]`, list→trimmed non-empty strings, else `ValueError` with the same messages). Do **not** leave create paths able to skip list-email tokens because coerce never ran.

4. Do **not** edit UI, `get_candidate_id_for_query` (already expands lookup `email_list_paths`), or invent a second uniqueness scan. Do **not** change the hard-fail vs collapse product rules (parent OQs stay locked).

⚠️ **Decision — core reads uniqueness config only for this pool:** After Stage 1, gate code must not special-case the string `"extra_emails"`; it walks `CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_list_paths"]`. Lookup remains the object identity source via the config alias.

⚠️ **Decision — no UI / no toast redesign:** Callers already surface `ValueError` → 400; AST-1065 owns display.

---

## Self-Assessment

**Scope:** `Single-Component` — uniqueness config vocabulary tweak + contact uniqueness helpers / initiate coerce in `src/core/candidate.py` only.

**Conf:** `high` — AST-1080 gate and AST-1092 `email_list_paths` already exist; this ticket makes the shared email pool explicit and closes root↔extra as a first-class contract on the save/initiate paths.

**Risk:** `Medium` — wrong pool wiring could miss cross-candidate email leaks or over-collapse within-candidate lists; limited to contact write paths already gated.

---

## Code Rules check (§8)

| Rule | Result |
|------|--------|
| §1.3 DRY | One collect/dedupe path; `email_list_paths` shared by identity with lookup |
| §1.4 no-hardcoded-sets | No inline `"extra_emails"` uniqueness sets in core — config paths only |
| §2.1 config source of truth | Email pool membership + compare mode live in `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` |
| §1.5.1 debug-contract-gated | Existing Style D on enforce when `debug=True`; no new ungated debug |
| §2.4 batch / §2.6 state | N/A |
| §3.3 imports | Core → utils config + existing database; no UI/external |
| data-raises-caller-logs | Core raises toast-ready `ValueError`; UI already surfaces |

No conflicts requiring `conf-!!-NONE`.

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-1095 |
| Publish ref | `origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra` |
| Built | `e47d94f4` (rebuild on `origin/ftr`; prior `a5d8c1a2`) |
| Notes | Stage 1 intent OK; Radia **FIX-NOW** — out-of-scope hunks on tip (see Resolution / Linear). |

## Resolution

**Date:** 2026-07-31  
**Review tip:** `adb3f86a` (`docs(AST-1095): Radia review — FIX-NOW scope creep`)  
**Publish tip:** (post-merge resolve) — Stage 1 uniqueness on refreshed `origin/ftr` (= `origin/dev` absorb).  
**Outcome:** findings addressed; §9a unblocked after ftr←dev refresh — merge refreshed ftr into sub with uniqueness kept (websites-only `list_paths`; no `get_candidate_id_for_query` email_list expansion).

| Finding | Disposition |
| -- | -- |
| fix-now — strip unrelated AST-1085/1087–1090 / DATA_SHAPES / full-name / craft hunks | Restored `config.py` + `candidate.py` from `origin/ftr`; re-applied uniqueness email pool + `contact_keys`/`email_list_paths` prereqs only |
| fix-now — revert `get_candidate_id_for_query` | Confirmed no hunk vs ftr (bind expansion not on tip) |
| discuss — premature resolve docs | Superseded by this Resolution |
| Betty `TestAst1092…labels_and_extra_emails_shape` | Cleared via ftr←dev (Profile DATA_SHAPES labels on base) |
| §9a into `origin/dev` / ftr | Cleared after ftr←dev refresh — merge refreshed ftr into sub; dry-runs clean |

### Radia — code-rubric.v1

`[code-rubric] revision=1` · **Overall:** FIX-NOW → addressed in product above.
