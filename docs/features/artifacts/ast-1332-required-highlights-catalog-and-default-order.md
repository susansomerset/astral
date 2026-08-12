# AST-1332 — Required Highlights catalog and default order

**Linear:** https://linear.app/astralcareermatch/issue/AST-1332/required-highlights-catalog-and-default-order  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1326/make-highlights-a-required-resume-section  
**Publish ref:** `sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order`

Elevate `highlights` into the required resume-structure catalog and default structure: present + enabled, default format `bullet_list`, order immediately above Experience; coerce that placement on normalize/resolve so base_resume_content follows it. Does **not** own hop schema or agent_task prompt text (sibling AST-1333). Does **not** invent a new body format or HTML emit path (existing `bullet_list` emit stays).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `highlights` to `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` (before `experience`); add `"highlights": "bullet_list"` to `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`; insert `highlights` into `RESUME_STRUCTURE_DEFAULT["sections"]` with title Highlights, enabled True, format from the map, order immediately above Experience; renumber Experience and following default orders. | utils |
| `src/core/candidate.py` | After per-section validation in `normalize_resume_structure`, coerce section `order` values so when both `highlights` and `experience` are present, `highlights` sits immediately above `experience` in order-sorted section lists. Missing `highlights` / `enabled=False` continue to raise via the existing required-id checks (no separate mint path in normalize). | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Craft-base / simple-resume-parse `response_schema`, agent_task prompt seed JSON | AST-1333 |
| `src/core/builder.py` HTML emit by format | unchanged — `bullet_list` path already emits Highlights |
| `DATA_SHAPES` / `BUILD_CONFIG["…"]["base_resume_structure"]` legacy tab template | out of scope — live UI reads `artifacts.resume_structure` order via `/resume_structure` |
| `tests/`, `docs/test-bible/**` | Betty |

## Traceability (this child's AC only)

Parent ACs 4–5 (schema + agent_task prompts) are AST-1333. Do not implement them here.

| Child AC | Stage |
|----------|--------|
| 1 — structure missing `highlights` fails normalize like other required ids; `enabled=false` rejected | 1 (required membership) + existing normalize checks (no code change beyond tuple) |
| 2 — default / newly minted structures place Highlights immediately above Experience by `order` | 1 |
| 3 — existing structure with Highlights below Experience shows Highlights immediately above Experience after resolve/normalize | 2 |
| 4 — HTML emit stays `bullet_list` / closed formats — no new visual language | 1 (default format only; no builder edits) |

## Stage 1: Config — required catalog + default order + format

**Done when:** `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` includes `highlights` immediately before `experience`. `RESUME_STRUCTURE_KNOWN_SECTION_IDS` (composed from required + historical optional) is eleven ids with `highlights` in that same place. `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID["highlights"]` is `"bullet_list"`. `RESUME_STRUCTURE_DEFAULT["sections"]["highlights"]` exists with title `"Highlights"`, `enabled` True, `job_agent_editable` True, `format` from the map, and `order` strictly less than `experience`'s `order` with no other default section between them when sorted by `order`. Historical optional ids remain in DEFAULT and in `RESUME_STRUCTURE_HISTORICAL_OPTIONAL_SECTION_IDS` (not stripped). No `candidate.py` behavior change in this stage.

1. In `src/utils/config.py`, in the `# Per-candidate resume section catalog (AST-517 / AST-1303)` block, change `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` to this **exact** tuple (insert `highlights` before `experience`; do not reorder anything else):

   ```python
   RESUME_STRUCTURE_REQUIRED_SECTION_IDS = (
       "candidate_name",
       "candidate_title",
       "candidate_tagline",
       "candidate_contact_detail",
       "professional_summary",
       "core_competencies",
       "highlights",
       "experience",
   )
   ```

   Leave `RESUME_STRUCTURE_HISTORICAL_OPTIONAL_SECTION_IDS` and the `RESUME_STRUCTURE_KNOWN_SECTION_IDS` composition unchanged (still `*REQUIRED + *HISTORICAL`). Do **not** put `highlights` in the historical-optional tuple.

2. In `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID`, add this entry (keep all existing keys):

   ```python
   "highlights": "bullet_list",
   ```

3. In `RESUME_STRUCTURE_DEFAULT["sections"]`, insert a `highlights` entry **immediately before** the `experience` entry, and renumber `order` ints so the body sequence is contiguous and Highlights sits immediately above Experience. Use these **exact** orders for the affected body/contact rows (contact 0–3 unchanged):

   | id | order |
   |----|-------|
   | `candidate_name` | 0 |
   | `candidate_title` | 1 |
   | `candidate_tagline` | 2 |
   | `candidate_contact_detail` | 3 |
   | `professional_summary` | 4 |
   | `core_competencies` | 5 |
   | `highlights` | 6 |
   | `experience` | 7 |
   | `prior_experience` | 8 |
   | `education_certifications` | 9 |
   | `technical_skills` | 10 |

   The new `highlights` section dict must be:

   ```python
   "highlights": {
       "id": "highlights",
       "title": "Highlights",
       "enabled": True,
       "order": 6,
       "job_agent_editable": True,
       "format": RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID["highlights"],
   },
   ```

   Update the existing `experience` / `prior_experience` / `education_certifications` / `technical_skills` entries' `"order"` values to 7 / 8 / 9 / 10 respectively (titles, enabled, formats, job_agent_editable unchanged).

4. Do **not** edit `RESUME_STRUCTURE_BODY_FORMATS`, `RESUME_STRUCTURE_CONTACT_SECTION_IDS`, `RESUME_STRUCTURE_EXTRA_*`, `BUILD_CONFIG`, `DATA_SHAPES`, `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`, `TASK_CONFIG`, agent_task seed JSON, or `src/core/builder.py`.

5. Do **not** change `src/core/candidate.py` in this stage (Stage 2 adds order coercion). Leaving normalize without coerce for one commit is intentional — required membership alone already satisfies AC1 for omit / disable once Stage 1 lands (existing checks iterate `RESUME_STRUCTURE_REQUIRED_SECTION_IDS`).

⚠️ **Decision:** `highlights` joins **required**, not historical-optional. Open extras may still use other slugs; `highlights` is now a known required id (same path as `experience` for required + disable rules). KNOWN grows from ten to eleven ids; hop/schema field inventory remains AST-1333.

⚠️ **Decision:** Default format is `bullet_list` only — Abrams treatment. Operators may still pick another closed body format on save where the structure editor allows it; this ticket does not lock format the way `experience` locks `experience_detail`.

⚠️ **Decision:** Do not patch the legacy `DATA_SHAPES` `base_resume_structure` tab list. Persistence authority is `artifacts.resume_structure`; `/artifacts/base_resume_content` already orders from resolve/hydrate.

## Stage 2: Normalize — coerce Highlights immediately above Experience

**Done when:** Calling `normalize_resume_structure` on a structure that includes all required ids (including `highlights`) where `highlights.order` is greater than `experience.order` (or any other section sits between them when sorted by `(order, id)`) returns a structure where, in the order-sorted section list, `highlights` is immediately before `experience`. Omitting `highlights` still raises `ValueError` whose message contains `missing required`. `enabled=False` on `highlights` still raises `ValueError` whose message contains `cannot be disabled`. A default deep-copy from `default_resume_structure()` still normalizes with Highlights immediately above Experience. Relative order among sections other than the Highlights↔Experience adjacency is preserved (only `highlights` is moved; then orders are reassigned 0..n-1 in the new sequence).

1. In `src/core/candidate.py`, inside `normalize_resume_structure`, **after** the per-section loop that builds `out["sections"]` and **before** the final `if not out["sections"]` empty check / `return out`, add order coercion:

   ```python
   secs = out["sections"]
   if "highlights" in secs and "experience" in secs:
       ordered_ids = [
           sid
           for sid, _spec in sorted(
               secs.items(),
               key=lambda kv: (
                   kv[1]["order"] if isinstance(kv[1].get("order"), int) else 0,
                   kv[0],
               ),
           )
       ]
       ordered_ids = [sid for sid in ordered_ids if sid != "highlights"]
       exp_i = ordered_ids.index("experience")
       ordered_ids.insert(exp_i, "highlights")
       for i, sid in enumerate(ordered_ids):
           secs[sid]["order"] = i
   ```

   Use this algorithm literally (remove `highlights` from the sorted id list, insert it at the index of `experience`, then rewrite contiguous `order` ints). Do not invent a different adjacency rule (e.g. `experience.order - 1` without reshuffling).

2. Do **not** mint a missing `highlights` row inside `normalize_resume_structure`. Missing required ids continue to raise at the existing `missing = [...]` check (AC1). Minting for candidates with no / invalid structure remains `resolve_resume_structure` → `default_resume_structure()` (unchanged call sites).

3. Do **not** change `resolve_resume_structure`, `default_resume_structure`, `hydrate_resume_structure_from_base_resume`, `prepare_resume_structure_sections_for_save`, or UI/API modules. GET `/resume_structure` already sorts by `order` and exposes `required_ids` from config — after Stage 1 those lists include `highlights` automatically.

4. Do **not** edit builder emit, hop schemas, or agent_task prompts.

⚠️ **Decision:** Coerce on every successful normalize (including save and resolve-when-valid), not only on GET. That is what makes AC3 true without an operator reorder and without a separate UI rule.

⚠️ **Decision:** Reassign all section orders to `0..n-1` after moving Highlights. Tie-breaking and gaps from operator edits are normalized away; adjacency is the product rule, not preserving sparse order ints.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1332
**Overall:** APPROVED
**Publish ref:** `sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order` @ `17530d63a5a31f94f6a615bbdaeb2c7807437bc4`

## Traceability
AC1→S1+existing normalize checks; AC2→S1; AC3→S2 (`normalize_resume_structure` coerce on resolve/save); AC4→S1 default `bullet_list` + explicit builder out-of-scope (parent AC4–5 → AST-1333).

## Findings

### acceptable — No explicit Self-assessment line
- **Location:** `## Estimate` (end of plan)
- **Finding:** Peer artifacts plans usually include `**Self-assessment:**` scope/conf/risk; this plan only has Estimate confirm.
- **Recommendation:** Optional hygiene — add `Single-Component / high conf / low risk` before build; not blocking given explicit ⚠️ Decision blocks and two-file footprint.

**In-session (R1–R4, not printed):** 56 statutes considered (18 universal + 38 scoped via `src/**`); 8 excluded (docs/ui/data/scripts paths). Cited statutes/patterns conform: `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, `astral.standards.in-scope-only`, `pattern.config.config-block`, `pattern.layers.import-discipline`. Orchestration universals conform. No `fix-now` / `discuss` statute violations. Plan Discuss round count: 0.

context_tokens≈42000

[plan-rubric] PROCEED (Commit: 17530d63a5a31f94f6a615bbdaeb2c7807437bc4) config coerce highlights order

## Review

- **Publish ref:** `sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order`
- **Tip:** `31c06b674f2cbf0c5ff4b72f88a2d55c5420d124`
- **Stages:** Stage 1 config catalog + default order; Stage 2 normalize Highlights↔Experience coerce

## Radia review

# Radia review — AST-1332

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1332  
**Publish ref:** `sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order` @ `5a74865a2ea8e9e1b52e36533943091d5a4c69f6`  
**Overall:** FIX-NOW

**Diff baseline:** `origin/dev...origin/sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order` (13 paths; merge-tests tip `5a74865a`)

**Change set (layers):** `src/utils/config.py`, `src/core/candidate.py` (in-scope); Betty `tests/**` + `docs/test-bible/core/candidate.md` (expected); **out-of-scope regression:** `Modal.tsx`, `JobAnalysisReportModal.tsx`, deleted `docs/features/interface/ast-1334-*.md`, removed AST-1334 frontend tests + bible section.

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent/LLM paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` / delegation |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grade-vector paths |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch/dispatcher |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/process/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity-agent-response paths |
| `astral.config.config-source-of-truth` | scoped | conforms | resume catalog extended in `config.py` only |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env wiring |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifact dirs |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run-next / chain |
| `astral.docs.features-single-file-per-ticket` | scoped | violates | diff **deletes** `docs/features/interface/ast-1334-*.md` present on `origin/dev` |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty commits tests/bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | product commits `111161d7` / `1bf6c7c9` test-tree-free |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core/utils only for product |
| `astral.layers.import-direction` | scoped | conforms | no new cross-layer imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no `scripts/` changes |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | ui diff is unintended revert, not new UI logic |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no render/verdict |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API/auth handlers |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no boot/seed hot path |
| `astral.seed.define-approved` | scoped | not-applicable | no define/seed flow |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator-row seed |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no data layer |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/migrations |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no backend `debug=` |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | coercion block matches plan; minimal |
| `astral.standards.in-scope-only` | scoped | violates | plan is `config.py` + `candidate.py`; diff also reverts AST-1334 ui + docs |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no logging added |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `highlights` is domain slug |
| `astral.standards.no-cross-contamination` | scoped | violates | rolls back shipped AST-1334 Modal/JAR/tests on `origin/dev` |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | catalog tuples/maps in config block |
| `astral.standards.public-then-helpers` | scoped | conforms | no helper reorder noise |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils→data imports |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job-state enforcement |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run/daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | unintended ui revert only |
| `astral.ui.naming-conventions` | scoped | not-applicable | unintended ui revert only |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server/worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single `merge-tests(AST-1332): origin/tests 1883ec76` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `merge-tests` / `docs` prefixes |
| `orch.git.flow-direction-inviolable` | universal | conforms | child on `sub/AST-1326/...`; tests via `origin/tests` |
| `orch.git.ftr-sub-topology` | universal | conforms | correct `sub/<parent>/<slug>` publish ref |
| `orch.git.merge-on-checkout` | universal | needs-discussion | `d63d0338 sync(publish-ref)` merge kept pre-AST-1334 `Modal.tsx` over `864bb872 sync(dev)` |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no cherry-pick/rebase signals |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent-named publish branches |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1326 epic worktree pattern |
| `orch.git.three-permanent-branches` | universal | conforms | sub + tests merge; no fourth permanent branch |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | plan ⚠️ decisions documented |
| `orch.pipeline.plan-is-bible` | universal | violates | AST-1332 stages delivered; diff also undoes AST-1334 work not in this plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | pipeline placement correct |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a to diff content |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test + bible on Betty SHA, merged once |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Ada (engineer) |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | engineer still assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no hook-evasion observed |

**Sweep count:** 64 active statutes scored (per `canon/statutes/README.md` harvested corpus; registry notes 65 — no extra leaf opened for this diff).

**Straggler (C4):** Joan plan-rubric APPROVED attached; no Excluded-statute list — no straggler callout.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | `highlights` catalog/default in `RESUME_STRUCTURE_*` blocks per plan |
| `pattern.layers.import-discipline` | conforms | no new cross-layer imports in product diff |

Joan cited both; no other pattern ids in plan.

---

## Plan adherence

**AST-1332 in-scope product (conforms):**

- Stage 1: `RESUME_STRUCTURE_REQUIRED_SECTION_IDS` gains `highlights` before `experience`; `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID["highlights"] = "bullet_list"`; DEFAULT `sections` entry with orders 6/7/8/9/10 renumber — matches plan verbatim.
- Stage 2: `normalize_resume_structure` coercion block matches plan algorithm literally (remove `highlights` from sorted list, insert at `experience` index, rewrite `0..n-1`).
- Boundaries respected: no `builder.py`, hop schema, agent_task, `DATA_SHAPES`, or `resolve_resume_structure` edits.
- Estimate **3** matches real footprint for intended scope.
- Betty coverage: `TestAst1332RequiredHighlightsCatalog`, `TestAst1332RequiredHighlightsNormalize`, sensible AST-1303/1306/1324 fixture pivots (`publications` as open extra now that `highlights` is required).

**Out-of-plan diff (fix-now):** `origin/dev` @ `5267c986` already ships AST-1334 (`fe131a0f` — `Modal` `showFooter`, `JobAnalysisReportModal` `showFooter={false}`, issue doc, frontend tests, bible). This branch **removes** that work:

| Path | vs `origin/dev` |
|------|-----------------|
| `src/ui/frontend/src/components/Modal.tsx` | drops `showFooter` prop + conditional footer |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | drops `showFooter={false}` |
| `docs/features/interface/ast-1334-*.md` | **deleted** |
| `docs/test-bible/frontend/components.md` | AST-1334 section removed |
| `tests/component/frontend/components/test_Modal.test.tsx` | AST-1334 case removed |
| `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` | AST-1334 describe block removed |

**Root cause:** `d63d0338 sync(publish-ref)` merged pre-AST-1334 sub tip (`baa485fa`) with `864bb872 sync(dev)`; conflict resolution kept the older `Modal.tsx` (no `showFooter`). `864bb872` had the correct dev tree (3 `showFooter` hits); tip `5a74865a` has 0.

**C6 lenses (§5a–§5g):** No import/layer/logging/debug/external/batch concerns on the **intended** AST-1332 product paths. UI regression is cross-ticket contamination, not new layer violations.

---

## Findings

### fix-now — AST-1334 regression smuggled into publish ref

- **Location:** `d63d0338` merge → `Modal.tsx`, `JobAnalysisReportModal.tsx`, `docs/features/interface/ast-1334-remove-recommended-job-report-modal-footer.md`, `docs/test-bible/frontend/components.md`, `tests/component/frontend/components/test_Modal.test.tsx`, `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`
- **Finding:** Three-dot diff vs `origin/dev` **reverts** AST-1334 (already on dev, parent AST-1329). AST-1332 plan explicitly scopes only `config.py` + `candidate.py`; sibling AST-1334 is unrelated.
- **Recommendation (resolve-child):** Re-merge `origin/dev` into publish ref; for conflicted ui/docs/test paths, **keep dev (AST-1334)** while retaining AST-1332 `config.py` / `candidate.py` / AST-1332 tests + bible. Re-run manifest green. Verify `Modal.tsx` still has `showFooter` and `JobAnalysisReportModal` still passes `showFooter={false}`.

### discuss — `sync(publish-ref)` merge resolution

- **Location:** `d63d0338 sync(publish-ref): origin/sub/AST-1326/AST-1332-required-highlights-catalog-and-default-order`
- **Finding:** Merge of `864bb872 sync(dev)` with `baa485fa` (sub tip branched before AST-1334 landed) took the wrong side for frontend files already on dev.
- **Question for downstream:** Should `sync(publish-ref)` after `sync(dev)` be gated on a quick `git diff origin/dev -- src/ui/...` smoke check when dev has landed sibling tickets since sub fork?

---

## What's solid

- AST-1332 config catalog and default order match Joan-approved plan exactly.
- Coercion algorithm in `normalize_resume_structure` is plan-literal and correctly gated on both ids present.
- Engineer product commits are test-tree-clean; Betty delivered one `merge-tests` SHA.
- AST-1332 test/bible coverage is well-scoped; fixture migrations from `highlights`-as-extra → `publications` are correct.

---

## Frame diff

**Drift:** Diff includes full AST-1334 rollback (ui + docs + tests) not present in AST-1332 plan frame. Intended frame (`config.py` + `candidate.py` + Betty tests) is otherwise aligned. Merge `origin/dev` and restore AST-1334 artifacts before User Testing.

---

## Notes

- Joan verdict present; no plan exclusions to reconcile.
- **Do not advance to User Testing** until AST-1334 regression is cleared — shipping this tip would undo a dev-landed sibling on ftr rollup.
- Downstream: Chuckles → **Review Posted** after doc writeback; datt → **resolve-child** (REVIEW path).

context_tokens≈38000

---

```
[code-rubric] REVIEW (Commit: 5a74865a) AST-1334 merge regression

## Resolution

**2026-08-12** — Ada · resolve-child after Radia FIX-NOW

- **fix-now (AST-1334 regression):** Restored from `origin/dev` (product + feature doc only):
  - `src/ui/frontend/src/components/Modal.tsx` (`showFooter` prop + conditional footer)
  - `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (`showFooter={false}`)
  - `docs/features/interface/ast-1334-remove-recommended-job-report-modal-footer.md`
- **AST-1332 product retained:** `src/utils/config.py` + `src/core/candidate.py` (required `highlights` + order coerce) unchanged.
- **Betty `[qa-handoff]` cleared:** tip `6649ab66` restored AST-1334 test-tree from `origin/dev` (`docs/test-bible/frontend/components.md` § AST-1334; `test_Modal.test.tsx`; `test_JobAnalysisReportModal.test.tsx`). Three-dot `origin/dev...HEAD` no longer diffs any AST-1334 paths. AST-1332 manifest re-run: **21 passed**.
- **discuss (sync merge gate):** Process question for Chuckles/orchestration — not a product change on this ticket; left unanswered in code.
