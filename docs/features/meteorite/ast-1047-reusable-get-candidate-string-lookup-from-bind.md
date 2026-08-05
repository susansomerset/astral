<!-- linear-archive: AST-1047 archived 2026-08-05 -->

## Linear archive (AST-1047)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1044 — Bind email to candidate  
**Blocked by / blocks / related:** parent: AST-1044; blocks: AST-1049; blocks: AST-1048

### Description

## What this implements

Owns the reusable core candidate lookup Susan named (`get_candidate`): given a string, match against configured contact info and names, return astral candidate id on an unambiguous hit; wire Manage Email’s From-address bind through that helper (including debug=True found/matched detail). Does **not** own Manage Email React chrome, strip/extract, or the Create → meteorite wire (siblings). Does **not** invent multi-candidate picker UX (ambiguous → no id).

## Citations

`pattern.config.config-block`; `pattern.layers.import-discipline`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.debug-contract-gated`; `astral.layers.core-vs-external-bright-line`.

## Acceptance criteria

1. A reusable core candidate lookup accepts a string, matches against configured contact info and names, and returns the astral candidate id on an unambiguous hit (and no id when none or ambiguous).
2. On Manage Email, a message whose **From** uniquely matches via that lookup shows a clear visual bind to that candidate.
3. With `debug=True` on touched match/create backend paths, found/matched/recorded outcomes use Style D index headers and `|` detail; with `debug=False`, no new debug-contract lines from those paths.

## Boundaries

Does **not** own Manage Email React chrome, strip/extract, or Create → meteorite wire (siblings). Does **not** invent multi-candidate picker UX.

## Notes for planning

Match homes: AST-1014 contact-blob emails + transitional profile.contact_email / profile.reply_email. Inbox bind uses From only (case-insensitive).

## Git branch (authoritative)

Parent `ftr/AST-1044-bind-email-to-candidate`; child `sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T19:24:05.157Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1047
**Publish ref:** `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind` @ `20e640f5` (product tip `0cefd0c2` + docs review)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind` — `src/utils/config.py` (M), `src/core/candidate.py` (M), `src/core/inbox.py` (M), `src/ui/api/api_inbox.py` (M), plan + Betty tests/bible.
**Notes:** Joan plan-rubric verdict attached (APPROVED). Three C4 stragglers (excluded at plan; in-scope on three-dot diff) — all score **conforms** on substance; no fix-now.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence / grade-vector logic in lookup path |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` / agent delegation |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched |
| astral.batch.batch-id-first | scoped | conforms | No batch/entity claim work |
| astral.batch.batch-id-format | scoped | conforms | No batch ids |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | Match homes only in `CANDIDATE_LOOKUP_CONFIG` |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets in config; OAuth untouched |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (`artifacts/**` / `scripts/spikes/**`) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan under `docs/features/` — not a misplaced spike |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan file `ast-1047-reusable-get-candidate-string-lookup-from-bind.md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer `code()`/`docs()` on src+features; Betty only tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | `test()`/`merge-tests()` are Betty; engineer did not touch tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Lookup/enrich in core; Gmail stays external via inbox |
| astral.layers.import-direction | scoped | conforms | ui→core+utils; core→core/external/utils; no ui→external/data |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers miss (`scripts`) |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Match resolved in core; API returns `candidate_match`; no React rules |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check / persistence |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | Keeps `@require_admin` on inbox routes |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new data-layer logging; UI/core warn on list failure |
| astral.standards.database-header-inventory | scoped | not-applicable | layers miss (`data`) |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when `debug=True`; truncate on query/From |
| astral.standards.dry-and-focused-functions | scoped | conforms | One lookup helper; inbox From bind calls it |
| astral.standards.in-scope-only | scoped | conforms | No React/Create/strip/picker — boundaries AST-1048/1049 held |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` / `truncate_debug_content` from utils |
| astral.standards.no-cross-contamination | scoped | conforms | Layered shapes; enrichment in core |
| astral.standards.no-hardcoded-sets | scoped | conforms | Email/name paths only in `CANDIDATE_LOOKUP_CONFIG` |
| astral.standards.public-then-helpers | scoped | conforms | New helper grouped with its public entrypoint in existing candidate.py layout |
| astral.standards.utils-data-late-import-only | scoped | conforms | Config-only utils change; no utils→data |
| astral.state.core-decides-transitions | scoped | conforms | No state machine |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss (`src/ui/frontend/**`) |
| astral.ui.naming-conventions | scoped | conforms | No new frontend files/routes; existing snake_case API |
| astral.ui.single-gunicorn-worker | scoped | conforms | Config block unrelated to gunicorn/workers |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1047)` @ `0cefd0c2` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child work on `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind` |
| orch.git.merge-on-checkout | universal | conforms | `origin/ftr/AST-1044-bind-email-to-candidate` ancestor before docs() |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1044` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Rename + dual-path decisions already in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match shipped code |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Meteorite child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible on publish ref |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit; no banned paths |

## Pattern conformance

| cited | verdict |
| -- | -- |
| `pattern.config.config-block` | conforms — `CANDIDATE_LOOKUP_CONFIG` |
| `pattern.layers.import-discipline` | conforms — ui→core; core owns match |
| `astral.config.config-source-of-truth` | conforms — match homes in config |
| `astral.standards.no-hardcoded-sets` | conforms — paths not inlined in core |
| `astral.standards.debug-contract-gated` | conforms — Style D gated |
| `astral.layers.core-vs-external-bright-line` | conforms — Gmail stays external |

## Plan adherence

Diff matches Stages 1–3 and Self-Assessment **Single-Component** / high / Medium. Dual library+transitional paths, fail-closed ambiguity, From bind via `parseaddr`, skip HTML-only get enrichment, and AST-1048/1049 boundaries hold. No picker / Create / nav rename smuggling.

## Findings

### fix-now
(none)

### discuss
1. **straggler** — `astral.debug.spikes-under-debug-dir` excluded at plan time but in-scope on diff (`docs/features/**`). Substance: **conforms**.
2. **straggler** — `astral.docs.features-single-file-per-ticket` excluded at plan time but in-scope on diff. Substance: **conforms** (one plan file).
3. **straggler** — `astral.git.engineer-test-tree-ban` excluded at plan time but in-scope on diff (Betty `tests/**` + bible). Substance: **conforms**.

### advisory
(none)

### What’s solid
- Unique-hit-only `get_candidate_id_for_query`; `get_candidate(id)` untouched.
- Core inbox `candidate_match` From enrichment; thin admin API + `ui_llm_debug`.

### Recommended actions
- Ada: acknowledge stragglers (no product change expected) → resolve-child → User Testing.

context_tokens≈48000

#### betty — 2026-07-29T19:19:26.501Z
## QA test manifest — AST-1047

**Publish:** `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind` @ `0cefd0c2`
**Delivery:** `merge-tests(AST-1047): origin/tests 968b737cfee91639b19b0bc0afbb57cb813b4654`

### Existing coverage (revised)
1. `tests/component/core/test_inbox.py` — **`TestListInboxMessages`** (list now asserts `candidate_match`; get path unchanged via **`TestGetMessageHtml`**)
2. `tests/component/ui/api/test_api_inbox.py` — **`TestAst1033InboxApi.test_list_messages_ok`** (asserts `list_inbox_messages(debug=…)`)

### Gaps (new)
3. `tests/component/utils/test_config.py::TestAst1047CandidateLookupConfig`
4. `tests/component/core/test_candidate.py::TestAst1047GetCandidateIdForQuery`
5. `tests/component/core/test_inbox.py::TestAst1047InboxFromBind`
6. `tests/component/ui/api/test_api_inbox.py::TestAst1033InboxApi::test_list_passes_ui_llm_debug`

### Broken / obsolete (revised this pass)
- **`TestListInboxMessages.test_returns_external_rows`** — expected exact external passthrough; product adds `candidate_match` per row.

### Integration
- No existing Admin inbox / candidate-lookup scenarios to revise; did not invent new integration coverage.

### Narrowed run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1047CandidateLookupConfig \
  tests/component/core/test_candidate.py::TestAst1047GetCandidateIdForQuery \
  tests/component/core/test_inbox.py \
  tests/component/ui/api/test_api_inbox.py \
  -q
```

### Bible shasums (publish tip)
- `docs/test-bible/utils/config.md` `902d8b71dbcfa8599c91493f987088b20686c08ac7a6ea61c3a87c928d8f318f`
- `docs/test-bible/core/candidate.md` `26c74c31304c9b4b498dec53c8ea3b69310efc23c77ba4d01704e40d97f612cd`
- `docs/test-bible/core/inbox.md` `36d8e2c69101fe29003401d5fb593ab10b80179c05da68ba4135b4e01b610e65`
- `docs/test-bible/ui/api/api_inbox.md` `efa1c126ffc0885b22cb9d87dbe4827bbc49f5587877ba2597ea205f87d1cde1`

— Betty

#### chuckles — 2026-07-29T19:12:39.384Z
[thread-orphan] Joan session 2f96bb3a-9e52-4b2a-80a0-b832afadc55f relocated
found: `/home/susan/.cursor/chats/0ab2adc851c7f84d4ce4bb00f485d83d/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db`
expected: `/home/susan/.cursor/chats/855b864e026601b5ae78c61bdc1ff345/2f96bb3a-9e52-4b2a-80a0-b832afadc55f/store.db`

— Chuckles

#### joan — 2026-07-29T19:12:14.780Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1047
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `4cc37bb8`. Publish ref `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`. New-pattern catalog flag in parent is honored by implementing under epic citations without claiming statute law; helper named `get_candidate_id_for_query` to avoid colliding with existing `get_candidate(id)`.
**Implementer:** Ada (plan author / parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Reusable core string→id lookup; unambiguous only | Stages 1–2 |
| 2 Manage Email From match shows clear visual bind | Stage 3 supplies API `candidate_match` From-bind; **visual chrome N/A — boundary AST-1048** |
| 3 Create enabled only when matched | N/A — boundary: AST-1048 |
| 4 Create strip/extract + meteorite job | N/A — boundary: AST-1049 |
| 5 Nav rename Manage Email | N/A — boundary: AST-1048 |
| 6 Unauthenticated cannot match/Create | Stage 3 keeps `@require_admin` on inbox APIs |
| 7 `debug=True` Style D on match/create paths | Stages 2–3 (match/From-bind); create debug N/A — AST-1049 |
| 8 Unmatched browse still works | Stage 3 enrichment additive; no list filtering |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Reusable lookup; id on unique hit; none/ambiguous → no id | 1–2 |
| 2 From unique match shows clear visual bind | 3 API bind payload; visual N/A — AST-1048 (child Boundaries) |
| 3 `debug=True` Style D; `debug=False` quiet | 2–3 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 `CANDIDATE_LOOKUP_CONFIG` | Functional scope match homes; §2.1 / no-hardcoded-sets |
| 2 `get_candidate_id_for_query` | Purpose reusable lookup; AC1; Architectural new pattern under epic citations |
| 3 Inbox From enrichment + `debug` on API | From-bind wire; AC2 data contract; AC6/7 auth+debug |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1047):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No rogue topology |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1044` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | No open product questions; dual path + rename decisions documented |
| orch.pipeline.plan-is-bible | conforms | Binding execution contract; siblings excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | No agent/do_task changes |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Match homes only in `CANDIDATE_LOOKUP_CONFIG` |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets in config |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Lookup/enrich in core; Gmail stays external |
| astral.layers.import-direction | conforms | ui→core; core→data/external/utils |
| astral.layers.ui-config-driven-business-logic | conforms | Match resolved in core; API returns payload; no React rules |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Keeps `@require_admin` on inbox routes |
| astral.standards.data-raises-caller-logs | conforms | No new data-layer logging |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | One lookup helper; inbox calls it |
| astral.standards.in-scope-only | conforms | Explicitly excludes React/Create/strip/picker |
| astral.standards.logging-via-utils | conforms | Existing logger helpers |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | Field paths in config only |
| astral.standards.public-then-helpers | conforms | Public lookup near get/list; private path helper |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No state machine |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.naming-conventions | conforms | No new frontend files/routes |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.standards.database-header-inventory — layers `data` / paths miss (no new tables)
- astral.ui.frontend-file-placement — paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Child AC2 “visual bind” is owned by AST-1048 per Boundaries; this plan delivers the From-bind API contract (`candidate_match`) that 1048 will render.
2. Not overloading `get_candidate(id)` — rename to `get_candidate_id_for_query` is the right collision avoidance.
3. Dual library + transitional email/name paths until AST-1014 is universal — matches parent hard-blocker note.
4. Skip enriching HTML-only `get_message_html` — correct given current TypedDict (`id` + `html_body` only).
5. Name match is exact per configured path (first/last/full); From-bind uses email needle via `parseaddr` — sufficient for this epic’s inbox caller.
6. Self-assessment Single-Component / high / Medium — honest.

— Joan
context_tokens≈45000

#### ada — 2026-07-29T19:09:39.126Z
Plan: [`docs/features/meteorite/ast-1047-reusable-get-candidate-string-lookup-from-bind.md`](https://github.com/susansomerset/astral/blob/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind/docs/features/meteorite/ast-1047-reusable-get-candidate-string-lookup-from-bind.md) on `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind` @ `4cc37bb8`.

**Scope:** Single-Component — `CANDIDATE_LOOKUP_CONFIG` + `get_candidate_id_for_query` + inbox From enrichment on existing admin inbox API; no React/Create/strip.

**Conf:** high — reuses `list_candidates`, stdlib `parseaddr`, existing `@require_admin` inbox blueprint, dual library+transitional email/name paths for pre/post AST-1014.

**Risk:** Medium — false unique match would mis-bind Create later; mitigated by exact configured-home match, fail-closed ambiguity, and not overloading existing `get_candidate(id)`.

---

# AST-1047 — Reusable get_candidate string lookup + From bind

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1047/reusable-get-candidate-string-lookup-from-bind-bind-email-to-candidate  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate  

**Publish ref (origin):** `sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`  
**Parent integration ref:** `ftr/AST-1044-bind-email-to-candidate`

Ship a **reusable core string → astral candidate id lookup** (Susan’s conceptual `get_candidate` helper) that matches configured contact-email and name fields, returns the id only on an **unambiguous** hit, and wire Manage Email’s **From** address through that helper on the existing inbox list/get API payloads (including `debug=True` found/matched Style D lines). Sibling AST-1048 owns React chrome / Create enablement UI; AST-1049 owns strip/extract + meteorite create.

Boundaries (do **not** implement): Manage Email React rename/chrome/Create button (AST-1048), strip/extract + meteorite create wire (AST-1049), multi-candidate picker UX, Gmail client reimplementation, Profile/Admin contact editors, mailbox mutation.

**Hard dependency note:** Parent names **AST-1014** contact-blob homes as the long-term email source. This tip may still have transitional `profile.*` email/name paths. The lookup config lists **both** library and transitional paths so matches work before/after 1014 lands on `origin/dev`; missing paths simply contribute no values.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_LOOKUP_CONFIG` (email/name dotted paths + casefold flag) | utils |
| `src/core/candidate.py` | Add `get_candidate_id_for_query(...)` + path/value helpers; `debug=` Style D found/matched lines | core |
| `src/core/inbox.py` | Enrich list (+ optional get) with From → lookup match payload; pass `debug` | core |
| `src/ui/api/api_inbox.py` | Pass `debug` via `ui_llm_debug`; leave `@require_admin`; no React | ui |

---

## Stage 1: Config — lookup field vocabulary

**Done when:** `CANDIDATE_LOOKUP_CONFIG` is importable from `src.utils.config` with the email/name path tuples below; no core/UI changes yet.

1. In `src/utils/config.py`, after `CANDIDATE_CONFIG` (or immediately after `CANDIDATE_LIBRARY_CONFIG` if that block already exists on this tree), add:

```python
# AST-1047: reusable string → candidate-id match homes (Manage Email From bind first caller).
CANDIDATE_LOOKUP_CONFIG = {
    # Dotted paths resolved against a full candidate row (top-level columns + candidate_data).
    "email_paths": (
        "contact.contact_email",   # AST-1014 contact blob
        "contact.reply_email",
        "profile.contact_email",   # transitional pre-1014
        "profile.reply_email",
    ),
    "name_paths": (
        "first", "last", "full",           # AST-1014 name columns when present
        "profile.first", "profile.last",   # transitional
    ),
    "match_casefold": True,  # case-insensitive compare for emails and names
}
```

2. If the top-of-file config inventory lists named `*_CONFIG` blocks, add a one-line `CANDIDATE_LOOKUP_CONFIG` entry next to other candidate config bullets.

⚠️ **Decision:** Field keys live only in this config block (§2.1 / no hardcoded sets in core). Dual library + transitional paths are intentional until 1014 is universal on `dev`; empty/missing path values are skipped, not errors.

---

## Stage 2: Core reusable lookup (Susan’s get_candidate shape)

**Done when:** Calling `get_candidate_id_for_query` with a string that uniquely matches one candidate’s configured email or name returns that `astral_candidate_id`; zero hits or two+ distinct candidate ids return `None`; existing `get_candidate(candidate_id)` ID fetch is **unchanged**; with `debug=True`, Style D found/matched lines emit; with `debug=False`, no new debug-contract lines.

1. In `src/core/candidate.py` (public section near `get_candidate` / `list_candidates`), **keep** existing:

```python
def get_candidate(candidate_id: str) -> Optional[Dict[str, Any]]:
    ...
```

Do **not** overload or rename it.

2. Add public:

```python
def get_candidate_id_for_query(
    query: str,
    *,
    debug: bool = False,
) -> Optional[str]:
```

**Behavior (literal):**

- Import `CANDIDATE_LOOKUP_CONFIG` from `src.utils.config`. Use existing `get_logger` / `truncate_debug_content` (add imports if missing).
- `raw = (query or "").strip()`. If empty → return `None` (optional debug: `found|empty_query`).
- **Normalize for matching:** use `email.utils.parseaddr(raw)` (stdlib). Let `addr = (parsed_email or "").strip()`.  
  - If `addr` contains `@`, the **match needle** is `addr`.  
  - Else the **match needle** is `raw` (name-style query).  
  - Never invent an email from a display name alone.
- `needle_cmp = needle.casefold() if CANDIDATE_LOOKUP_CONFIG["match_casefold"] else needle`.
- Scan `list_candidates(include_deleted=False)` (exclude DELETED).
- For each candidate, collect string values from all `email_paths` + `name_paths` via a private helper `_lookup_path_value(candidate, dotted_path) -> str`:
  - Split path on `.`.
  - If first segment is `contact` or `profile` (or any blob under `candidate_data`), read from `candidate["candidate_data"]` nested dicts.
  - If first segment is a top-level column (`first` / `last` / `full` / `pronouns` / `astral_candidate_id`), read from the candidate row first; if missing/empty, also try `candidate_data.profile.<seg>` only when that path is listed in config (do not invent extra homes).
  - Coerce to stripped `str`; skip `None` / non-strings / empty.
- A candidate **hits** when any collected value, after the same casefold rule, equals `needle_cmp`.
- Build the set of distinct `astral_candidate_id` strings among hits (skip blank ids).
- If `len(ids) == 1` → return that id. If `0` or `>= 2` → return `None`.

3. **Debug contract** (`debug=True` only), one index per call (batch of 1):

- `logger.set_debug_flag(True)` then `logger.debug_index(func="get_candidate_id_for_query", index=1, total=1, identifier=<needle truncated>, outcome=...)` where outcome is `found|matched` (unique id), `found|none`, `found|ambiguous`, or `found|empty_query`.
- `logger.debug_detail` lines: `query=`, `needle=`, and on match `candidate_id=`; on ambiguous `candidate_ids=` (sorted id list). Use `truncate_debug_content` on long strings.

⚠️ **Decision — name vs existing `get_candidate`:** Catalog already uses `get_candidate(candidate_id)` for ID fetch across UI/core. Overloading it for string lookup would break every caller that passes an id that happens to look like email/name text. The reusable string→id helper is therefore **`get_candidate_id_for_query`** — same responsibility Susan named “get_candidate” in the epic, without colliding. Do not rename the ID fetcher in this ticket.

⚠️ **Decision — ambiguous:** Multiple candidates matching the same needle → `None` (no picker). Parent invariant: emails unique across candidates; name collisions are fail-closed.

---

## Stage 3: From bind on Manage Email inbox API (no React)

**Done when:** `GET /api/admin/inbox/messages` (and message get if it returns the list row shape) includes a `candidate_match` object derived solely from each message’s `from_address` via `get_candidate_id_for_query`; unmatched/ambiguous → `matched: false` and null id; `@require_admin` unchanged; no React/nav rename.

1. In `src/core/inbox.py`, add a thin enricher used by list (and get if the get payload is the same message dict family):

```python
def _candidate_match_for_from(from_address: str, *, debug: bool = False) -> dict:
    cid = get_candidate_id_for_query(from_address or "", debug=debug)
    return {
        "matched": cid is not None,
        "astral_candidate_id": cid,
    }
```

Import `get_candidate_id_for_query` from `src.core.candidate`.

2. Change `list_inbox_messages` to accept `debug: bool = False`. After `external_list_inbox_messages()`, return a **new list** of dicts: each original message fields plus `"candidate_match": _candidate_match_for_from(msg["from_address"], debug=debug)`.

⚠️ **Decision:** Enrich in **core inbox** (not only in the Flask layer) so any future core caller of list gets the same From-bind contract. UI stays thin.

3. When `debug=True` on list enrichment, emit Style D **per message** in the enricher loop:

- `debug_index(func="inbox_from_bind", index=i, total=n, identifier=<message id>, outcome=found|matched` or `found|none`)  
- detail: `from_address=`, `astral_candidate_id=` when matched.  
  (Ambiguous and none both surface as `matched: false` / null id; outcome label `found|none` is enough — lookup already logged ambiguous internally when its own `debug=True` is set. Pass the same `debug` flag into `get_candidate_id_for_query` so lookup lines appear too.)

4. In `src/ui/api/api_inbox.py`:

- Import `ui_llm_debug` from `src.utils.deploy_status` (same pattern as other LLM/debug admin routes).
- `inbox_list_messages`: `debug = ui_llm_debug(explicit_debug=request.args.get("debug", "").lower() in ("1", "true", "yes"))` then `list_inbox_messages(debug=debug)`.
- Keep `@require_admin`. Do **not** change response envelope key `messages`.
- Do **not** edit `AdminReadEmail.tsx`, `NAV_CONFIG` label, or routes (AST-1048).

5. If `get_message_html` returns a payload that AST-1048 will also use for bind display on the selected message, add the same `candidate_match` key there by re-reading From from list metadata **only if** the get payload already includes `from_address`. If get payload is HTML-only today (`html_body` without From), **skip** enriching get — list enrichment is sufficient for the bind wire in this ticket.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files outside the Files Changed table.
- On ambiguity or codebase drift — **stops, comments on parent AST-1044**, waits.
- Commits per stage on the epic worktree; publishes to `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`.

Blocking comment format (parent AST-1044):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — config + candidate lookup helper + inbox From enrichment on existing admin inbox API; no React, no meteorite create, no schema migration.

**Conf:** high — reuses `list_candidates` / `get_candidate` row shape, stdlib `parseaddr`, existing `@require_admin` inbox blueprint, and AST-538 debug helpers; dual path config covers pre/post AST-1014.

**Risk:** Medium — a false unique match would enable Create in AST-1048/1049 for the wrong candidate; mitigated by exact string match on configured homes only, fail-closed ambiguity, and From-email extraction before compare. Wrong overload of `get_candidate(id)` avoided by Decision above.

---

## Code Rules self-review

| Rule / citation | Check |
|-----------------|--------|
| §2.1 / `astral.config.config-source-of-truth` / `no-hardcoded-sets` | Email/name homes only in `CANDIDATE_LOOKUP_CONFIG` |
| §1.5.1 / `debug-contract-gated` | Style D only when `debug=True`; truncate long From/query |
| §3.3 / import-direction / core-vs-external | UI → core only; Gmail stays in external via existing inbox |
| §1.3 DRY | One lookup helper; inbox From bind calls it — no second matcher in UI |
| Existing `get_candidate(id)` | Untouched ID fetch — no signature break |
| No picker / no Create UI | Ambiguous → `None`; React left to AST-1048 |

## Review (build stub)

**Publish ref:** `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`
**Plan path:** `docs/features/meteorite/ast-1047-reusable-get-candidate-string-lookup-from-bind.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `05e8a2b4` | `CANDIDATE_LOOKUP_CONFIG` email/name paths + casefold |
| 2 | `3ad56efc` | `get_candidate_id_for_query` + `_lookup_path_value`; Style D |
| 3 | `a530d025` | Inbox list `candidate_match` From bind; `api_inbox` `ui_llm_debug` |

**Tip:** `a530d0255a69308d63896541b621b49b0faf39b4` on `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1047
**Publish ref tip (pre-docs):** `0cefd0c2133867fcf5f6d0c3ec23d086c354908a`
**Overall:** DISCUSS

### What’s solid
- `CANDIDATE_LOOKUP_CONFIG` owns email/name homes; `get_candidate_id_for_query` returns id only on unique hit; existing `get_candidate(id)` untouched.
- Inbox list From→`candidate_match` enrichment in core; `api_inbox` stays thin + `@require_admin` + `ui_llm_debug`.
- Style D gated on `debug=True` (lookup + per-message `inbox_from_bind`); no React/Create/strip (AST-1048/1049).

### Issues
- **discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot diff includes `docs/features/**` + Betty `tests/**` / `docs/test-bible/**` so they score in-scope (all **conforms** on substance).

### Recommended actions
- Ada: acknowledge stragglers (no product change expected) → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `20e640f5` — **Overall:** DISCUSS; **fix-now:** none; **discuss:** statute straggler ×3 (all substance **conforms**); no advisory.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (`docs/features/**` + Betty tests/bible) — no code delta. Advanced to **User Testing**.
