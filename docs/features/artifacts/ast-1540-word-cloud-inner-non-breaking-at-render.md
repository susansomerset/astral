# AST-1540 — Word-cloud inner non-breaking at render

**Linear:** [AST-1540](https://linear.app/astralcareermatch/issue/AST-1540/word-cloud-inner-non-breaking-at-render-word-cloud-items-with-inner)  
**Parent:** [AST-1539](https://linear.app/astralcareermatch/issue/AST-1539/word-cloud-items-with-inner-characters-must-be-non-breaking)  
**Publish ref:** `sub/AST-1539/AST-1540-word-cloud-inner-non-breaking-at-render` (origin only)

AST-1528/AST-1536 glued word-cloud **bullet separators** with NBSP at render (`\u00a0•\u00a0`), but multi-word and hyphenated **items** still soft-wrap on ordinary spaces and ASCII hyphens inside the item. Extend the existing render-only glue helper so remaining breakable spaces and ASCII hyphens in the cloud emit string become non-breaking before HTML — without putting that encoding on generation, `_resume_site_markers`, or non-`word_cloud` formats.

## Explicit scope gate

Ticket **Scope** names `src/core/builder.py` only — **modified** render helper used by the `word_cloud` arm of body-section emit (today `_glue_word_cloud_bullet_separators`): after existing bullet-separator glue, convert remaining ordinary spaces to NBSP and remaining ASCII hyphens to non-breaking hyphens in that emit-only string. Do not put this conversion on `_resume_site_markers` / generation. Shared marker path stays left-only for non-cloud formats. All Files Changed / Stage steps stay inside that file (Betty owns any `tests/**` follow-up). Cover from-block, new digraphs, typography redesign, and non-`word_cloud` formats stay out.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/core/builder.py` | Extend `_glue_word_cloud_bullet_separators` (keep call site on `word_cloud` arm): after `\u00a0•\u00a0` glue, replace remaining ordinary `" "` → `\u00a0` and remaining ASCII `"-"` → `\u2011` | core | engineer (Stage 1) |
| `tests/component/core/test_builder.py` | Lock inner NBSP / non-breaking-hyphen on `word_cloud` emit; keep format-switch / left-only marker asserts green | tests | Betty (qa-child) |

## Stage 1: Inner non-breaking on cloud render glue

**Done when:** A `word_cloud` section whose items contain ordinary spaces and/or ASCII hyphens (no `__` / `~~` digraphs required) emits those characters as `\u00a0` and `\u2011` inside `p.competencies-list` on base Print / session Open HTML / job Print (shared `_emit_body_sections_html` path). Existing `\u00a0•\u00a0` bullet glue still holds. `_resume_site_markers` output is unchanged by this ticket (left-only / digraph contracts from AST-1536). Switching the same content to `free_prose` does not show cloud inner NBSP / `\u2011` encoding. Engineer `code()` commit contains **only** `src/core/builder.py`.

1. In `src/core/builder.py`, locate `_glue_word_cloud_bullet_separators` (immediately after `_resume_site_markers`; docstring today cites AST-1536). **Keep the function name and its single call site** in `_emit_body_sections_html` (`elif fmt == "word_cloud":` → `cloud_text = _glue_word_cloud_bullet_separators(str(text))` then `_emit_inline_emphasis_html(cloud_text)`). Do **not** add a parallel helper or a second call from `_apply_resume_text_markers`, `_mark_resume_value`, or any non-`word_cloud` format arm.

2. Extend the helper body so order of operations is exactly:

   a. Early return if `not text` (unchanged).  
   b. Load `emit_sep = COVER_FROM_BLOCK_CONFIG["emit_separator"]` and set `glued = "\u00a0•\u00a0"` (unchanged).  
   c. Apply existing bullet glue: `t = text.replace(emit_sep, glued).replace("\u00a0• ", glued)`.  
   d. **Then** convert remaining ordinary spaces: `t = t.replace(" ", "\u00a0")`.  
   e. **Then** convert remaining ASCII hyphens: `t = t.replace("-", "\u2011")`.  
   f. `return t`.

   Update the docstring to state: NBSP both sides of `•`, then remaining spaces → NBSP and ASCII hyphens → non-breaking hyphen, for `word_cloud` HTML emit only (AST-1536 / AST-1540).

   ⚠️ **Decision:** Extend `_glue_word_cloud_bullet_separators` in place (ticket Notes / DRY) rather than a second helper or a CSS `white-space` rule on `.competencies-list`. Character-level emit matches digraph history (`__` / `~~`) and keeps format-switch safe. Do **not** edit `_resume_site_markers`, `COVER_FROM_BLOCK_CONFIG`, cover from-block, header/contact joins, or non-cloud format arms. Do **not** convert en-dash / em-dash / soft hyphen — only ASCII `"-"` and ordinary `" "`.

3. Optional local sanity (no test-tree commit): after the edit, in a Python REPL or one-off, assert roughly:

   - `_glue_word_cloud_bullet_separators("Delivery | Alignment")` (or post-marker `"Delivery\u00a0• Alignment"` / `"Delivery • Alignment"`) yields full `\u00a0•\u00a0` between items **and** no ordinary `" "` left in the result.  
   - `_glue_word_cloud_bullet_separators("AI-Assisted Delivery • Cloud")` (after glue path) contains `AI\u2011Assisted\u00a0Delivery` and `\u00a0•\u00a0` (or equivalent glued bullet).  
   - `_resume_site_markers("A | B | C")` still returns left-only `"A\u00a0• B\u00a0• C"` (no change).  
   - `_resume_site_markers("AI~~Assisted__Delivery")` still expands digraphs only (`AI\u2011Assisted\u00a0Delivery`) — this ticket does not re-encode on the marker path.

   Existing component tests that only lock separator glue stay green; new inner-space / hyphen asserts are Betty’s qa-child — engineer does not patch `tests/**`.

## Betty qa-child (inner non-breaking lock — not engineer Stage 1)

After engineer Stage 1 lands, Betty’s **qa-child** manifest should extend `tests/component/core/test_builder.py` (and bible § as needed) to assert, on a `word_cloud` session/base emit path:

- Multi-word items without digraphs appear with `\u00a0` between words inside `p.competencies-list` (e.g. `Project\u00a0Management`).  
- ASCII-hyphenated items appear with `\u2011` (e.g. `AI\u2011Assisted`).  
- Existing AST-1528/AST-1536 separator glue and format-switch (`TestAst1536BugReproWordCloudFormatSwitch`) remain green — free_prose must **not** inherit inner cloud NBSP / `\u2011` from this helper.  
- `_resume_site_markers` left-only and digraph asserts unchanged.

Engineer never commits under `tests/**` (`astral.git.engineer-test-tree-ban`).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Traceability

1→Stage 1 (inner `" "` → `\u00a0`, `"-"` → `\u2011` after bullet glue in `_glue_word_cloud_bullet_separators`).  
2→Stage 1 (existing emit_sep / left-only → `\u00a0•\u00a0` steps unchanged).  
3→Stage 1 (helper remains word_cloud-arm-only; markers / generation untouched → format switch safe).  
4→Stage 1 (shared `_emit_body_sections_html` word_cloud arm → base / session / job).  
5→Stage 1 (no cover / non-cloud / digraph / config edits).

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1540
**Overall:** APPROVED
**Publish ref:** `sub/AST-1539/AST-1540-word-cloud-inner-non-breaking-at-render` @ `3b6622318208540c86fac5a9d7342c8e9c843959`

## Traceability

1→Stage 1 (`" "` → `\u00a0`, `"-"` → `\u2011` after bullet glue in `_glue_word_cloud_bullet_separators`). 2→Stage 1 (existing `emit_sep` / `\u00a0• ` → `\u00a0•\u00a0` unchanged). 3→Stage 1 (helper word_cloud-arm-only; `_resume_site_markers` / generation untouched). 4→Stage 1 (shared `_emit_body_sections_html` `word_cloud` arm). 5→Stage 1 (no cover / non-cloud / config / digraph edits).

## Findings

### acceptable — Procedure / assignee at fetch
- **Location:** Linear AST-1540
- **Finding:** Status `Plan Ready` but assignee was Katherine Johnson (not Joan) at `get-issue` time.
- **Recommendation:** Chuckles spawn is authoritative for this stdout-only pass; restore implementer after posting upshot per validate-plan §8.

### acceptable — Files Changed `tests/**` row
- **Location:** Files Changed table
- **Finding:** Row names `tests/component/core/test_builder.py` while ticket `## Scope` is `builder.py` only.
- **Recommendation:** Explicit scope gate + Betty qa-child section correctly partition engineer vs Betty ownership; Stage 1 commit boundary (`code()` only `src/core/builder.py`) is clear.

### acceptable — Parent cites `astral.layers.import-direction`; child citations omit it
- **Location:** Citations vs parent Architectural definition
- **Finding:** Child lists `pattern.layers.import-discipline` instead of repeating the statute id.
- **Recommendation:** No action — single-file core change still satisfies import-direction; pattern citation is sufficient for R6.

No `fix-now` or `discuss` findings on plan substance.

context_tokens≈42000

## Review (build)

**Built:** `origin/sub/AST-1539/AST-1540-word-cloud-inner-non-breaking-at-render` @ `bc5ad81a` — `_glue_word_cloud_bullet_separators` after `\u00a0•\u00a0` glue replaces remaining `" "` → `\u00a0` and `"-"` → `\u2011`; call site still `word_cloud` arm only.

**Out of build scope (Betty / qa-child):** inner NBSP / non-breaking-hyphen asserts on `word_cloud` emit; format-switch / left-only marker locks stay hers.

## Radia review

# Radia review — AST-1540

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1540  
**Publish ref:** `sub/AST-1539/AST-1540-word-cloud-inner-non-breaking-at-render` @ `fe3c62794030ad19cdbfa45c1ff3367c99bd88d5`  
**Overall:** CLEAN

**Diff change set:** `src/core/builder.py` (modify, layer `core`); `docs/features/artifacts/ast-1540-word-cloud-inner-non-breaking-at-render.md` (add, `docs`); `docs/test-bible/core/builder.md` (modify, `docs`); `tests/component/core/test_builder.py` (modify, tests tree); `docs/features/artifacts/ast-1528-word-cloud-nbsp-bullet-glue.md` (modify, `docs` — AST-1526 epic-registry mirror, orthogonal).

**Notes:** Joan `[plan-rubric]` APPROVED attached; no `Excluded` statute list in that artifact (straggler check N/A). Engineer `code(AST-1540)` @ `bc5ad81a` touches only `src/core/builder.py`; Betty `test(AST-1540)` @ `7a961801` owns tests/bible; `merge-tests(AST-1540)` @ `fe3c6279` present.

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no `src/agent` / agent-task diff paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no dispatcher / do_task diff |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grading diff |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch claim paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id diff |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/release diff |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity-agent-response diff |
| `astral.config.config-source-of-truth` | scoped | conforms | bullet glue still reads `COVER_FROM_BLOCK_CONFIG["emit_separator"]`; no new config keys |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env diff |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifact paths |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike paths |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch/seed diff |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run_next diff |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | AST-1540 plan lives at `docs/features/artifacts/ast-1540-…md` |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commit `7a961801` — tests + bible only, no `src/**` |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer `bc5ad81a` — `src/core/builder.py` only; tests landed in separate Betty commit |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core render helper only; no external I/O |
| `astral.layers.import-direction` | scoped | conforms | no import changes in `builder.py` diff |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no `scripts/**` diff |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | no `src/ui/**` diff |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check diff |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | `builder.py` emit path, not consult orchestration |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API/auth diff |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON diff |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no catalog diff |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no boot/seed hot-path diff |
| `astral.seed.define-approved` | scoped | not-applicable | no define/seed diff |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator-row diff |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage-join diff |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no `src/data/**` diff |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/migration diff |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug-contract emission added |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | extends `_glue_word_cloud_bullet_separators` in place per plan DRY decision |
| `astral.standards.in-scope-only` | scoped | conforms | single helper extension on `word_cloud` arm; markers/generation untouched |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no logging added |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | existing helper name retained |
| `astral.standards.no-cross-contamination` | scoped | conforms | no out-of-layer imports |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | no new behavior-driving sets; Unicode glue literals match prior AST-1536 pattern |
| `astral.standards.public-then-helpers` | scoped | conforms | private helper extended; single `word_cloud` call site unchanged |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no `src/utils/**` diff |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transition diff |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job-state diff |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run-chain diff |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no frontend diff |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI naming diff |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server worker diff |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1540)` @ `fe3c6279` records Betty SHA |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary correct |
| `orch.git.flow-direction-inviolable` | universal | conforms | child `sub/AST-1539/…` topology |
| `orch.git.ftr-sub-topology` | universal | conforms | publish ref matches parent/child convention |
| `orch.git.merge-on-checkout` | universal | conforms | no merge-law violation in diff |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no forbidden git ops in artifact |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent-named branches in diff |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | epic worktree pattern respected |
| `orch.git.three-permanent-branches` | universal | conforms | diff vs `origin/dev` only |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | scope matches approved parent/child plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | implementation matches Stage 1 order-of-ops and boundaries |
| `orch.pipeline.project-scoped-queues` | universal | conforms | N/A to code substance |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed gate |
| `orch.roles.archie-approves-statutes` | universal | conforms | N/A to diff |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns `tests/**` + bible manifest |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Katherine at Tests Passed |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | implementer retained |
| `orch.roles.pre-commit-path-bans` | universal | conforms | role boundaries observed in commit split |

**Active set count:** 64 rows (harvested corpus table in `canon/statutes/README.md`).

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | reuses `COVER_FROM_BLOCK_CONFIG["emit_separator"]` for bullet glue; no second separator vocabulary |
| `pattern.layers.import-discipline` | conforms | non-breaking treatment stays in core `builder.py` emit; no UI spacer logic |

---

## Plan adherence

Stage 1 landed exactly as specified: `_glue_word_cloud_bullet_separators` keeps name and sole call site (`elif fmt == "word_cloud":`); order is early return → `emit_sep` bullet glue → `" "` → `\u00a0` → `"-"` → `\u2011`; docstring updated; `_resume_site_markers` and non-cloud format arms untouched. Betty qa-child delivered `TestAst1540WordCloudInnerNonBreaking` (helper, markers left-only/digraphs, session cloud emit, free_prose isolation), revised `TestAst1528WordCloudNbspBulletGlue` and `TestAst1029UatCompetenciesBulletsEmit`, and bible manifest aligned. Estimate **2** matches footprint. Parent acceptance criteria 1–5 satisfied on diff evidence.

**C6 aids (§5a–§5g):** imports/layers/logging/debug/external/batch/UI-config — no issues on touched `builder.py` hunk.

---

## Frame diff

(none) — plan frame unchanged; implementation fills approved Stage 1 only.

---

## Findings

### advisory — Sibling doc mirror on publish ref
- **Location:** commit `5fa373a9` (`docs(AST-1526): mirror epic registry Threads`) on `origin/sub/AST-1539/AST-1540-word-cloud-inner-non-breaking-at-render`
- **Finding:** Appends Team Threads to `docs/features/artifacts/ast-1528-word-cloud-nbsp-bullet-glue.md` — orthogonal to AST-1540 product scope.
- **Recommendation:** Harmless epic-worktree housekeeping; optional cherry-pick hygiene on future rollups if sibling branches are still open. Not blocking.

### advisory — Bible shasum placeholder
- **Location:** `docs/test-bible/core/builder.md` AST-1540 section
- **Finding:** Manifest says “record via `git show … | shasum`” but no recorded hash in-file.
- **Recommendation:** Betty or Chuckles may record on next bible touch; not blocking review.

**fix-now:** none  
**discuss:** none

---

## What's solid

- Minimal, plan-faithful core change: three lines in the glue helper with correct operation order.
- Format-switch safety preserved: helper remains `word_cloud`-arm-only; tests lock `_resume_site_markers` and `free_prose` non-inheritance.
- Clean engineer/Betty commit split matches `astral.git.engineer-test-tree-ban` intent.
- Test coverage maps directly to parent acceptance criteria (inner space/hyphen, separator regression, format switch, default competencies UAT).

---

## Recommended actions (downstream — not Radia)

1. Chuckles: append this artifact to issue doc; `docs(AST-1540): Radia review — clean`; post slim upshot; → **Review Posted** → **resolve-child** queue (PROCEED).
2. Optional: record bible shasum on next Betty pass.

context_tokens≈72000

## Bug: AST-1552 — Word-cloud: breaking space after bullet (inner NBSP only)

### As-is

`_glue_word_cloud_bullet_separators` (AST-1536/1540) first glues separators to `\u00a0•\u00a0`, then converts **every** remaining ordinary `" "` to `\u00a0`. The space after each `•` (between the bullet and the first character of the next cloud item) is therefore non-breaking — Print/Open HTML has no soft-wrap opportunity after the bullet. Example emit: `AI\u2011Assisted\u00a0Delivery\u00a0•\u00a0Cloud`.

### To-be

Keep **inner** item ordinary spaces as `\u00a0` and ASCII hyphens as `\u2011`. Leave a **normal breaking** space between `•` and the first character of each following cloud item. Keep `\u00a0` immediately **before** each `•` (do not wrap onto a leading bullet). Example emit: `AI\u2011Assisted\u00a0Delivery\u00a0• Cloud` (ordinary `" "` after `•`).

### Repro

1. Base or session resume with a `word_cloud` section whose content includes multi-item text with ordinary spaces/hyphens inside items, e.g. after markers/`" • "` join: `AI-Assisted Delivery • Cloud` or pipe-authored `AI-Assisted Delivery | Cloud`.
2. Print / Open HTML — inspect `p.competencies-list` text.
3. **Broken today:** substring `\u00a0•\u00a0` between items (no ordinary space after `•`).
4. **Fixed:** substring `\u00a0• ` (NBSP, bullet, ordinary space) between items; inner item still has `AI\u2011Assisted\u00a0Delivery` (no ordinary `" "` / `"-"` left inside the item).

Fixture shape (no DB):

```json
{
  "artifacts": {
    "resume_structure": {
      "sections": {
        "core_competencies": {
          "id": "core_competencies",
          "title": "Core Competencies",
          "enabled": true,
          "order": 3,
          "format": "word_cloud"
        }
      }
    },
    "base_resume": {
      "core_competencies": "AI-Assisted Delivery • Stakeholder trust • Cloud"
    }
  }
}
```

### Root cause

AST-1540 applied a blanket `t.replace(" ", "\u00a0")` **after** building `\u00a0•\u00a0`. That correctly non-breaks inner item spaces, but the post-bullet character in the glued separator is already `\u00a0` from the AST-1536 glue step — so the cloud string ends with zero breaking spaces. The product intent (Susan UAT) needs a soft-wrap opportunity **after** the bullet while keeping mid-item non-breaking.

### Proposed change

All edits in `src/core/builder.py` only (parent Component/Technical scope — same `_glue_word_cloud_bullet_separators` render helper).

1. In `_glue_word_cloud_bullet_separators`, keep the existing order through hyphen conversion:

   - early return if `not text`
   - `emit_sep` / `glued = "\u00a0•\u00a0"`
   - `t = text.replace(emit_sep, glued).replace("\u00a0• ", glued)`
   - `t = t.replace(" ", "\u00a0")`
   - `t = t.replace("-", "\u2011")`

2. **Then** restore a breaking space after each bullet (AST-1552):  
   `t = t.replace("\u00a0•\u00a0", "\u00a0• ")`  
   so the separator becomes NBSP + `•` + ordinary `" "` while inner item `\u00a0` / `\u2011` from steps above remain.

3. Update the helper docstring to note: after inner space/hyphen non-breaking, restore ordinary space after `•` (AST-1552); NBSP before `•` unchanged.

4. Do **not** call this from `_resume_site_markers` / generation / non-`word_cloud` arms. Do **not** edit `COVER_FROM_BLOCK_CONFIG`, cover from-block, or change en/em/soft hyphens.

⚠️ **Decision:** Restore `\u00a0•\u00a0` → `\u00a0• ` **after** the blanket space→NBSP pass (do not change `glued` to `\u00a0• ` before that pass — a trailing ordinary space would be re-converted to NBSP). Prefer this one-line restore over splitting items and re-joining — same helper, minimal delta. Keep NBSP **before** `•` so lines still do not soft-wrap onto a leading bullet (Susan asked only for the post-bullet space to break).

### Blast radius

- **AST-1540 / AST-1528 / AST-1536 tests** that lock full `\u00a0•\u00a0` on `word_cloud` emit (`TestAst1540WordCloudInnerNonBreaking`, `TestAst1528WordCloudNbspBulletGlue` session HTML, `TestAst1029UatCompetenciesBulletsEmit`, possibly `TestAst1536BugReproWordCloudFormatSwitch` glue positive asserts) must expect `\u00a0• ` after the bullet while still locking inner `\u00a0` / `\u2011`. Betty **qa-fix** (if board says TESTS: REVISE) owns test-tree updates — engineer does not edit `tests/**`.
- **Original AST-1540 AC2** (“`\u00a0` between items” / both-sides glue) is **superseded for the post-bullet character** by this UAT bug; pre-bullet `\u00a0` and inner non-breaking remain.
- Markers / format-switch / cover paths unchanged if the helper stays word_cloud-arm-only.

### What must still hold

- AST-1540 AC1: inner ordinary spaces → `\u00a0`, ASCII hyphens → `\u2011` inside cloud items on Print/Open HTML.
- AST-1540 AC3 / AST-1536: saved/generated text and non-`word_cloud` formats (e.g. `free_prose` after format switch) do **not** inherit cloud inner NBSP / `\u2011` or this separator shape from the glue helper.
- AST-1540 AC4: base / session / job share `_emit_body_sections_html` `word_cloud` arm.
- AST-1540 AC5 / boundaries: cover from-block, `_resume_site_markers` left-only + digraphs, non-cloud formats unchanged in intent.
- AST-1027: `__` / `~~` on the shared marker path unchanged.

## Radia review — AST-1552

|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent diff in scoped fix |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no dispatch diff |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grading diff |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id diff |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/release diff |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity-agent diff |
| `astral.config.config-source-of-truth` | scoped | conforms | still uses `COVER_FROM_BLOCK_CONFIG["emit_separator"]`; no new config keys |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets diff |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch diff |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run_next diff |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | plan-fix patches existing `ast-1540-…md` per fix-lane convention |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty `0dffde8f` — tests + bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer `23483405` — `src/core/builder.py` only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core render helper only |
| `astral.layers.import-direction` | scoped | conforms | no import changes |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts diff |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | no UI diff in scoped fix |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check diff |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | builder emit, not consult |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API/auth diff |
| `astral.seed.*` (6 statutes) | scoped | not-applicable | no seed diff |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no data layer |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB diff |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug emission |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | one-line restore in existing helper per plan DRY decision |
| `astral.standards.in-scope-only` | scoped | conforms | scoped fix touches only `_glue_word_cloud_bullet_separators` |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no logging added |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | helper name retained |
| `astral.standards.no-cross-contamination` | scoped | conforms | no out-of-layer imports in scoped fix |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | no new behavior sets |
| `astral.standards.public-then-helpers` | scoped | conforms | private helper extended |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils diff |
| `astral.state.*` (3 statutes) | scoped | not-applicable | no state diff |
| `astral.ui.*` (3 statutes) | scoped | not-applicable | no UI diff in scoped fix |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1552)` @ `41ca076a` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `docs` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub on parent ftr |
| `orch.git.ftr-sub-topology` | universal | conforms | naming correct |
| `orch.git.merge-on-checkout` | universal | conforms | no merge-law violation in fix commits |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no forbidden git ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent branches |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | epic worktree pattern |
| `orch.git.three-permanent-branches` | universal | conforms | diff vs ftr base |
| `orch.pipeline.*` (4 statutes) | universal | conforms | fix addresses Susan UAT `[bug]` |
| `orch.roles.*` (6 statutes) | universal | conforms | role boundaries in commit split |

**Active set count:** 64 rows (harvested corpus).

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | reuses existing `emit_separator`; no second vocabulary |
| `pattern.layers.import-discipline` | conforms | spacer logic stays in core builder emit |

---

## Plan adherence

`plan-fix` **Proposed change** steps 1–4 implemented exactly:

1. Existing glue → space→NBSP → hyphen→`\u2011` order preserved.
2. Final `t.replace("\u00a0•\u00a0", "\u00a0• ")` after blanket space pass (per ⚠️ Decision).
3. Docstring updated (AST-1552).
4. Helper remains `word_cloud`-arm-only; markers/generation/config untouched.

Engineer/Betty ownership split matches board REVISE + `astral.git.engineer-test-tree-ban`.

---

## Frame diff

AST-1540 AC2 post-bullet character superseded: separator shape is now `\u00a0• ` (breaking space after bullet) while pre-bullet NBSP and inner non-breaking remain. Plan-fix blast radius documents this; revised tests reflect it.

---

## Findings

### advisory — Publish ref carries dev delta beyond ftr
- **Location:** `origin/sub/AST-1539/AST-1552-word-cloud-breaking-space-after-bullet` history (`sync(dev): origin/dev` @ `fe91f8fb` and intervening commits); full `ftr...sub` = 103 files
- **Finding:** Sub branch includes `origin/dev` commits not yet on `origin/ftr/AST-1539-…` (e.g. AST-1548 product on `src/core/agent.py`, `tracker.py`, etc.). AST-1552 product commits themselves are isolated (`23483405` builder only; `0dffde8f` tests only).
- **Recommendation:** Chuckles: before `merge-child`, either (a) merge `origin/dev` into `ftr` first then merge only AST-1552 delta, or (b) cherry-pick `d169eace`/`0dffde8f`/`23483405` (+ `merge-tests`) onto a clean sub stacked on current `ftr`. **Do not route to `resolve-child`** — product fix is correct; this is merge ops.

**fix-now:** none  
**discuss:** none

---

## What's solid

- Minimal, plan-faithful one-line restore with correct operation order (restore after blanket NBSP pass).
- [bug-repro] pins To-be concretely at helper + session HTML levels; would fail pre-fix.
- All `## What must still hold` items verified via existing + revised tests.
- Board REVISE bar cleared; Joan CANON OK.

---

## Chuckles branching note

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean) | Normal AST-1539 | → **Review Posted** → fix-lane clean shortcut → **User Testing** directly (`resolve-child` skipped) |
| Merge ops | — | Address advisory dev-delta on publish ref before `merge-child` into `ftr` |

context_tokens≈85000

---

```
[code-rubric] PROCEED (Commit: 23483405) Post-bullet space restored

