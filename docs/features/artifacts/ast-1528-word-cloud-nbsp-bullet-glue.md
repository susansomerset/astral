# AST-1528 — Word-cloud NBSP bullet glue

**Linear:** [AST-1528](https://linear.app/astralcareermatch/issue/AST-1528/word-cloud-nbsp-bullet-glue-resume-word-clouds-need-non-breaking)  
**Parent:** [AST-1526](https://linear.app/astralcareermatch/issue/AST-1526/resume-word-clouds-need-non-breaking-spaces)  
**Publish ref:** `sub/AST-1526/AST-1528-word-cloud-nbsp-bullet-glue` (origin only)

Resume `word_cloud` sections (Core Competencies, Prior Experience on that format, and any other body section with `format: word_cloud`) currently emit pipe-authored and space-bullet-space text as `\u00a0• ` — NBSP only on the left of `•`. Print/Open HTML can still wrap onto a leading bullet because the space after `•` is ordinary. Restore the historical `__•__` equivalence: NBSP-bullet-NBSP on the shared resume site-marker expand path so base Print, session Open HTML, and job resume Print all glue separators the same way. Cover-letter from-block stays on `candidate.expand_cover_from_block_text` and is not retargeted.

## Explicit scope gate

Ticket **Scope** names `src/core/builder.py` only — modified `_resume_site_markers` and/or `word_cloud` body emit so space-bullet-space becomes NBSP-bullet-NBSP for cloud (and any text already on that expand path); no new files. All Files Changed / Stage steps stay inside that file. Cover from-block, `COVER_FROM_BLOCK_CONFIG` values, new digraphs, and experience-array work stay out.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/core/builder.py` | Tighten `_resume_site_markers` space-bullet-space → NBSP-bullet-NBSP; keep `_emit_education_list_html` partition/join on the same glued shape | core | engineer (Stage 1) |
| `tests/component/core/test_builder.py` | Flip asymmetric `\u00a0• ` expectations (markers, compact titles, education, competencies HTML) to `\u00a0•\u00a0` where they assert separator glue | tests | Betty (qa-child) |

## Stage 1: Shared marker glue + education partition

**Done when:** Calling `_resume_site_markers` on a pipe-authored cloud line (e.g. `A | B | C`) and on a line that already contains `" • "` both yield `\u00a0•\u00a0` between items; `A__•__B` still yields `\u00a0•\u00a0` (AST-1027). Base / session / job resume HTML that emit `word_cloud` after `_apply_resume_text_markers` show that glued shape in the competencies text node. Education list rows that use the post-marker bullet still split credential vs rest. Cover from-block emit path and `COVER_FROM_BLOCK_CONFIG["emit_separator"]` are untouched. Engineer `code()` commit contains **only** `src/core/builder.py`.

1. In `src/core/builder.py`, locate `_resume_site_markers` (today ends with `t.replace(" • ", "\u00a0• ")` after the `|` → `emit_separator` join). Change that final tighten so every occurrence of the cover/resume authoring emit separator (`COVER_FROM_BLOCK_CONFIG["emit_separator"]`, currently `" • "`) becomes the glued form `"\u00a0•\u00a0"` (NBSP + `•` + NBSP) — not `"\u00a0• "` (left-only). Prefer replacing via the already-loaded `emit_sep` variable (or the same config key) rather than a second hard-coded `" • "` literal, so the search string stays tied to config; the replacement string is the historical `__•__` → NBSP-bullet-NBSP shape.

   Keep order of operations unchanged: `__` → `\u00a0`, `~~` → `\u2011`, then `|` join with `emit_sep`, then the glue replace. Do **not** add a cloud-only fork helper. Do **not** edit `COVER_FROM_BLOCK_CONFIG` in `src/utils/config.py` (cover `expand_cover_from_block_text` shares `emit_separator`; leaving the config value as `" • "` keeps cover alone).

2. In the same file, update `_emit_education_list_html` so its local `bullet` partition/join string matches the new post-marker shape `"\u00a0•\u00a0"` (today it is `"\u00a0• "`). Education body text already runs through `_apply_resume_text_markers` before emit; without this companion edit, credential/rest split breaks after Stage 1 step 1.

   ⚠️ **Decision:** Prefer one expand path in `_resume_site_markers` (ticket Notes / DRY) over a `word_cloud`-arm-only post-pass. The education partition update is inseparable blast inside `builder.py` from that shared tighten — same separator shape, not a new digraph or format. Do **not** change header `h1_inner` (`name\u00a0• title`) or `"\u00a0• ".join(parts)` contact join; those are not on the space-bullet-space → glue replace and are outside cloud separator intent.

3. Optional local sanity (no test-tree commit): after the edit, in a Python REPL or one-off, assert:

   - `_resume_site_markers("A | B | C")` contains `A\u00a0•\u00a0B\u00a0•\u00a0C`
   - `_resume_site_markers("A__•__B")` contains `A\u00a0•\u00a0B`
   - `_resume_site_markers("A • B")` contains `A\u00a0•\u00a0B`

   Existing component tests that still expect `\u00a0• ` (asymmetric) will fail until Betty’s qa-child — that is expected; engineer does not patch `tests/**`.

## Betty qa-child (separator glue lock — not engineer Stage 1)

After engineer Stage 1 lands, Betty’s **qa-child** manifest must update `tests/component/core/test_builder.py` assertions that lock the old left-only shape, including at least:

- `TestAst1027UatMarkerExpand` (keep `__•__` → `\u00a0•\u00a0`; add or extend a pipe-authored / `" • "` case that expects `\u00a0•\u00a0` both sides).
- Compact-title / education / competencies HTML asserts that currently expect `\u00a0• ` (regular space after `•`) where those strings came from `_resume_site_markers` — flip to `\u00a0•\u00a0`.
- Cover from-block / `COVER_FROM_BLOCK_CONFIG["emit_separator"] == " • "` tests must **remain** green (no config change).

Do **not** weaken AST-1027 digraph fidelity. Engineer never commits under `tests/**` (`astral.git.engineer-test-tree-ban`).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1528
**Overall:** APPROVED
Publish ref: `sub/AST-1526/AST-1528-word-cloud-nbsp-bullet-glue` @ `caf38f385447f6ddb72dc0809b458fe798977bc2`

## Traceability
1→Stage 1 (`|` join via `emit_sep` + final glue replace to `\u00a0•\u00a0`); 2→Stage 1 (unchanged `__`/`~~` order before glue — AST-1027); 3→Stage 1 (`_apply_resume_text_markers` on all three build paths: base, session, job); 4→Stage 1 (cover stays on `expand_cover_from_block_text`; education partition companion in `builder.py` only).

## Findings

### acceptable — procedural (Chuckles handoff)
- **Location:** Linear assignee
- **Finding:** Ticket is `Plan Ready` but assignee is Katherine Johnson, not Joan. Validation proceeded per spawn; Chuckles should restore implementer after posting upshot.
- **Recommendation:** No plan change.

### acceptable — blast radius (documented)
- **Location:** Stage 1 step 1, shared `_resume_site_markers`
- **Finding:** Global `emit_sep` → `\u00a0•\u00a0` replace also glues compact-title `title • company` strings (not only `word_cloud`). Betty qa-child section names compact-title asserts to flip; parent AC4 allows inseparable shared-path blast.
- **Recommendation:** No plan change — already documented.

### acceptable — Files Changed tests row
- **Location:** Files Changed table
- **Finding:** `tests/component/core/test_builder.py` is outside ticket `## Scope` but listed for Betty qa-child per `astral.git.engineer-test-tree-ban`; Explicit scope gate + engineer Stage 1 commit-only rule are correct.
- **Recommendation:** No plan change.

context_tokens≈18500

## Review (build)

**Built:** `origin/sub/AST-1526/AST-1528-word-cloud-nbsp-bullet-glue` @ `0301a6e4` — `_resume_site_markers` replaces `emit_sep` with `\u00a0•\u00a0`; `_emit_education_list_html` partitions on the same glued bullet. `COVER_FROM_BLOCK_CONFIG` untouched.

**Out of build scope (Betty / qa-child):** flip asymmetric `\u00a0• ` asserts in `tests/component/core/test_builder.py` per plan Betty section.

## Radia review

# Radia review — AST-1528

**Status gate:** Tests Passed (spawn prompt; not re-fetched)  
**Diff:** `origin/dev...origin/sub/AST-1526/AST-1528-word-cloud-nbsp-bullet-glue`  
**Tip SHA:** `93939313cd75e92b42e12a479060236098eaf7cb`  
**Change set:** 4 files — `src/core/builder.py` (core), `tests/component/core/test_builder.py` (tests), `docs/test-bible/core/builder.md`, `docs/features/artifacts/ast-1528-word-cloud-nbsp-bullet-glue.md` (docs). Layers: `core`, `docs`. Change types: `add`, `modify`.

---

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1528
**Publish ref:** origin/sub/AST-1526/AST-1528-word-cloud-nbsp-bullet-glue @ 93939313cd75e92b42e12a479060236098eaf7cb
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent/LLM paths in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no dispatcher/agent task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade/vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch/claim paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch id emission |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent-data writes |
| astral.config.config-source-of-truth | scoped | conforms | glue replace uses loaded `emit_sep` from `COVER_FROM_BLOCK_CONFIG`; config file untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no env/secrets |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no seed/dispatch |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run-next changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single issue doc `ast-1528-word-cloud-nbsp-bullet-glue.md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty touched tests + bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code()` commit `0301a6e4` is `src/core/builder.py` only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | change confined to `src/core/builder.py` |
| astral.layers.import-direction | scoped | conforms | no new imports; layer boundaries unchanged |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/` changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI/frontend |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render verdict |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API handlers |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog edits |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot/seed hot path |
| astral.seed.define-approved | scoped | not-applicable | no define/seed |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no `src/data/` |
| astral.standards.database-header-inventory | scoped | not-applicable | no DB/migrations |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug logging |
| astral.standards.dry-and-focused-functions | scoped | conforms | minimal tighten on shared expand path; education partition aligned in-place |
| astral.standards.in-scope-only | scoped | conforms | product + tests match plan; no cover/config/experience-array scope creep |
| astral.standards.logging-via-utils | scoped | conforms | no logging added |
| astral.standards.names-not-ticket-ids | scoped | conforms | no ticket-id symbol names |
| astral.standards.no-cross-contamination | scoped | conforms | three-dot diff is AST-1528-only (no AST-1524 file deltas vs `origin/dev`) |
| astral.standards.no-hardcoded-sets | scoped | conforms | search string tied to `emit_sep`; replacement shape is the specified glue literal |
| astral.standards.public-then-helpers | scoped | conforms | private helpers only; no API surface change |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils/data import changes |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state logic |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | no UI naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1528)` at tip after Betty `test()` commit |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1526/...` publish ref |
| orch.git.ftr-sub-topology | universal | conforms | child under parent `AST-1526` |
| orch.git.merge-on-checkout | universal | conforms | no merge violations observed |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops in diff |
| orch.git.no-dev-agent-branches | universal | conforms | no dev-agent branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | epic worktree pattern respected |
| orch.git.three-permanent-branches | universal | conforms | sub publish, not direct dev commit |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | blast radius pre-approved in plan/Joan |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches Stage 1 + Betty section |
| orch.pipeline.project-scoped-queues | universal | conforms | scoped child ticket |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no new statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns test + bible updates |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Katherine assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | engineer through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer isolated from `tests/**` |

**Sweep count:** 65 active statutes scored (18 universal, 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan / Joan verdict cite no `canon/patterns/**` ids |

## Plan adherence

Implementation matches Joan **APPROVED** Stage 1 exactly:

- `_resume_site_markers` final tighten uses `emit_sep` (not a second hard-coded `" • "` literal) and replaces with `\u00a0•\u00a0`; order of `__` / `~~` / `|` join unchanged.
- `_emit_education_list_html` partition string updated to match (`bullet = "\u00a0•\u00a0"`).
- `COVER_FROM_BLOCK_CONFIG` / cover from-block path untouched.
- Header `h1_inner` (`name\u00a0• title`) and contact `"\u00a0• ".join(parts)` correctly left asymmetric (outside glue replace).
- Documented blast radius (compact-title, education, meta tagline, competencies) applied consistently; Betty flipped legacy left-only asserts and added `TestAst1528WordCloudNbspBulletGlue`; bible § AST-1528 manifest matches.
- Estimate **2** fits footprint (2-line product change + targeted test/bible lock).

**Joan straggler:** no Excluded-statute list in Joan attachment → no straggler check required.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Branch history hygiene:** publish ref log includes `e180a0d8 test(AST-1524)` ancestor, but three-dot diff vs `origin/dev` has zero deltas on those files (content already aligned with dev). No scope smuggling in the reviewed diff; optional squash/rebase before finish-up if Susan wants a linear AST-1528-only history.
- **UAT note for parent AST-1526:** header name/title and contact-line bullets remain left-NBSP-only by design; word_cloud / marker-path separators are fully glued both sides. UAT should not expect global `\u00a0•\u00a0` everywhere in resume HTML.

## What's solid

- Correct DRY fix: one shared expand path instead of a `word_cloud`-only fork.
- `emit_sep`-driven replace ties search string to config without mutating cover emit config.
- Education partition companion prevents credential/rest split regression.
- `TestAst1528WordCloudNbspBulletGlue` scopes negative `\u00a0• ` check to `competencies-list` paragraph (avoids false fail on asymmetric header).
- AST-1027 digraph fidelity preserved; AST-1382 pipe→bullet repro tightened (no more `or` fallback accepting left-only glue).

## Frame diff

Resume site-marker expand: space-bullet-space (`emit_sep`) → NBSP-bullet-NBSP on `_resume_site_markers`; education list partition aligned. Tests + test-bible lock new glued shape across markers, compact-title, education, meta, competencies, and session word_cloud emit. Cover from-block unchanged.

## Notes

- `no plan-rubric Excluded list` — Joan Overall APPROVED only.
- C6 aids (imports, layers, silent failure, debug §5f, external §5g): not triggered; no violations.
- Product diff:

```1107:1108:src/core/builder.py
    # Glue both sides of • (old __•__ equivalence) — not left-only NBSP.
    t = t.replace(emit_sep, "\u00a0•\u00a0")
```

```1499:1499:src/core/builder.py
    bullet = "\u00a0•\u00a0"  # matches _resume_site_markers glue (AST-1528)
```

context_tokens≈22000
