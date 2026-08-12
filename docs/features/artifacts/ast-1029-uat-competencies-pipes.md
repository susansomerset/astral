<!-- linear-archive: AST-1029 archived 2026-08-05 -->

## Linear archive (AST-1029)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1029/uat-competencies-separators-print-as-pipes  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1019 — Take 2: Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-1019

### Description

## What failed

Core Competencies list prints pipe separators instead of bullet characters:

`<p class="competencies-list">AI-Assisted Delivery | Cross-Functional Execution | Risk and Dependency Management | …</p>`

## Expected

Competencies separators match golden / fixture treatment — bullet/`•` characters (with nbsp where markers require), not `|`.

## Repro

1. Session Resume Paste with Core Competencies lines (UAT paste that currently renders pipes).
2. Parse → Open HTML.
3. Inspect `.competencies-list` text — separators must be bullets, not `|`.

## Parent AC (quoted inline)

> Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on “close enough.”
> Structure already owned by AST-993 … Core Competencies one competencies list … nested `__` / `~~` markers end-to-end.

## Diagnosis

* **Hypothesis:** Emit (or upstream normalize) is using `|` as the competencies join character instead of `•` / marker-aware bullet join used by the golden fixture.
* **Correct outcome:** `.competencies-list` reads with bullet separators matching desired HTML / paste bullet convention.
* **Wrong fix to avoid:** CSS `content:` fake bullets while leaving `|` in the DOM text; only fix one surface (session vs base vs job-tailored).
* **Related siblings / contracts:** AST-1020 (uppercase/letter-spacing CSS already); AST-993 competencies list markup; Prior Experience same list style if shared.

## Boundaries

* Does **not** change competencies CSS chrome (AST-1020).
* Does **not** rewrite competency wording — separators only.

### Comments

#### chuckles — 2026-07-29T04:16:27.314Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed on `origin/sub/AST-1019/AST-1029-uat-competencies-pipes`:
- Forbidden subject: `Merge remote-tracking branch 'origin/ftr/ast-1019-take-2-resume-render-format-discrepancies' into sub/…` (`f974c469`)
- Sub was seeded from prep-uat AST-1023 tip (`9df034b6`), not current ftr (`672b2eea` resolve AST-1028), then ftr was merged in with the default remote-tracking message.

@Ada Lovelace — republish clean: reset/rebuild `sub/AST-1019/AST-1029-uat-competencies-pipes` from `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies`, re-apply only the AST-1029 plan→…→resolve commits (no `Merge remote-tracking branch` subject; redo `merge-tests` from Betty tip `5fc85d9a` if needed), force-with-lease push publish ref. Stay User Testing / assignee Ada.

— Chuckles

#### radia — 2026-07-29T04:14:22.958Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1029
**Publish ref:** b94e3b0bfd135dafba47e5c96969fa17848e0f61
**Overall:** CLEAN

Diff: `origin/dev...origin/sub/AST-1019/AST-1029-uat-competencies-pipes` (product @ `f90922c4` / merge-tests tip `52962126` + this `docs()` append). No `src/` delta; product is `data/admin/agent_task.json` (plus prior FIX-UAT stack on the sub).

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1029): origin/tests 5fc85d9a` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests`/`resolve` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish to child `origin/sub/…` |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1019 |
| orch.git.merge-on-checkout | universal | conforms | No alternate merge inventiveness |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1019 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis matches fixture; no product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 •-not-pipe Done-when matches tip |
| orch.pipeline.project-scoped-queues | universal | conforms | Single Artifacts bug child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Reviewed from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test` + `merge-tests`; engineer avoided test tree |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | No Chuckles assignee inventiveness in review |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Review Posted without reassign; implementer path preserved |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer product path is repo admin JSON + plan |
| astral.agent.confidence-bounds | scoped | not-applicable | layers/paths miss — no `src/core/**` / config |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.batch.batch-id-first | scoped | not-applicable | paths miss — no `src/data/**` / `src/core/**` |
| astral.batch.batch-id-format | scoped | not-applicable | paths miss — no `src/core/**` / `src/data/**` |
| astral.batch.claim-process-release | scoped | not-applicable | paths miss — no `src/core/**` / `src/data/**` |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | paths miss — no `src/core/**` / `src/data/**` |
| astral.config.config-source-of-truth | scoped | not-applicable | paths miss — no `src/**` |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | paths miss — no scored config/core/data |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | layers/paths miss — no `src/**` / `scripts/**` |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss — no repo-root `artifacts/**` |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/`; no spike pollution |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1029-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits only tests/bible (+ merge-tests) |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code/docs omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths miss — no `src/core/**` / external |
| astral.layers.import-direction | scoped | not-applicable | paths miss — no `src/**` |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss — no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths miss — no UI/config src |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss — no `src/ui/**` |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | paths miss — no `src/**` |
| astral.standards.database-header-inventory | scoped | not-applicable | paths miss — no `src/data/**` |
| astral.standards.debug-contract-gated | scoped | not-applicable | layers/paths miss — no `src/**` |
| astral.standards.dry-and-focused-functions | scoped | not-applicable | paths miss — no `src/**` / scripts |
| astral.standards.in-scope-only | scoped | not-applicable | paths miss — no `src/**` (product is `data/admin/`) |
| astral.standards.logging-via-utils | scoped | not-applicable | layers/paths miss — no `src/**` |
| astral.standards.no-cross-contamination | scoped | not-applicable | paths miss — no `src/**` |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | paths miss — no `src/**` |
| astral.standards.public-then-helpers | scoped | not-applicable | paths miss — no `src/**` |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss — no `src/utils/**` |
| astral.state.core-decides-transitions | scoped | not-applicable | paths miss — no `src/core/**` / `src/data/**` |
| astral.state.job-prior-states-enforced | scoped | not-applicable | paths miss — no state-machine paths |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths miss — no `src/core/**` |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss — no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss — no `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths miss — no worker/config/UI knobs |

## Pattern conformance

none cited

## Plan adherence

Stage 1 matches: `core_competencies` requires `•` / forbids `|` (including enrichment joins); `prior_experience` aligned; checklist bullet present. Stage 2 builder lock holds — no `src/core/builder.py` in three-dot. Scope Single-Component matches. Parsed JSON: only `craft_resume_base.cache_prompt` changed in the AST-1029 code commit.

## Findings

None.

### What’s solid

Prompt harden closes the AST-1027 soft-prefer gap so shared escape-only emit gets bullet-joined `.competencies-list` text — no CSS fake bullets, no builder `|`→`•` rewrite.

### Recommended actions

resolve-child → User Testing. Restart/deploy so startup applies repo JSON, then re-paste competencies fixture.

**Notes:** no plan-rubric verdict attached. FIX-UAT mode. Ticket assignee was already Radia at review start — left unchanged per review-child (no assignee field writes).

— Radia
context_tokens≈36000

#### betty — 2026-07-29T04:11:44.203Z
## QA test manifest (AST-1029)

**Publish:** `origin/sub/AST-1019/AST-1029-uat-competencies-pipes` @ `52962126` (`merge-tests(AST-1029): origin/tests 5fc85d9a`)

**FIX-UAT:** no `docs/test-bible/**` change on `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` since AST-1028 — skipped full bible re-read.

### Classification

1. **Existing coverage:** AST-1009 education/skills/prior markup; AST-1027 marker preserve; AST-1028 title/tagline; AST-996 job-array prompt.
2. **Broken / obsolete:** none — soft “prefer separators” language retired by prompt harden (asserted gone).
3. **Gaps:** `craft_resume_base` require `•` / forbid `|` for competencies + prior; session emit lock for bullet-joined `.competencies-list`.

**Integration:** no existing scenario asserts competencies separators — no revision.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1029CraftResumeBaseCompetenciesBullets \
  tests/component/core/test_candidate.py::TestAst1027CraftResumeBaseMarkerPreserve \
  tests/component/core/test_candidate.py::TestAst1028CraftResumeBaseTitleTaglineSplit \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract \
  tests/component/core/test_builder.py::TestAst1029UatCompetenciesBulletsEmit \
  tests/component/core/test_builder.py::TestAst1009EducationSkillsPrior \
  -q
```

### Bible shasums (on publish tip)

- `docs/test-bible/core/candidate.md` `3bf2d6cc8cef54d7457e7fdcf3c4e53ad5badcab`
- `docs/test-bible/core/builder.md` `904982e87f0191ec6b6a33d5f00fd68a1fc96b57`

— Betty

#### ada — 2026-07-29T04:06:43.881Z
Plan: [`docs/features/artifacts/ast-1029-uat-competencies-pipes.md`](https://github.com/susansomerset/astral/blob/sub/AST-1019/AST-1029-uat-competencies-pipes/docs/features/artifacts/ast-1029-uat-competencies-pipes.md) on `origin/sub/AST-1019/AST-1029-uat-competencies-pipes` @ `7af784ae`.

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` only; builder competencies emit is already escape-only.

**Conf:** `high` — UAT Actual is `|` in `.competencies-list`; AST-1027 soft “prefer” still leaves pipe as enrichment default.

**Risk:** `Medium` — prompt hits all `craft_resume_base` consumers; mitigated by forbidding `|` as item separators (not rewriting phrases) and no CSS/builder rewrite.

---

# UAT: competencies separators print as pipes

**Linear:** [AST-1029](https://linear.app/astralcareermatch/issue/AST-1029/uat-competencies-separators-print-as-pipes)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1029-uat-competencies-pipes`

Session Resume Paste → Parse → Open HTML shows Core Competencies joined with `|` (e.g. `AI-Assisted Delivery | Cross-Functional Execution | …`) instead of golden / fixture `•` bullets. Shared builder `_emit_body_sections_html` HTML-escapes `core_competencies` / `prior_experience` into `<p class="competencies-list">` with **no** separator rewrite — pipes arrive from `craft_resume_base`. AST-1027 already softened competencies to “prefer paste separators… rather than rewriting to `|`”, but that still allows the model to invent `|` when enriching from LinkedIn / strengths. Harden the prompt: **require** bullet joins and **forbid** pipe separators.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”* / *“Structure already owned by AST-993 … Core Competencies one competencies list … nested `__` / `~~` markers end-to-end.”*
- **Correct outcome:** `.competencies-list` text uses `•` separators matching the golden / fixture treatment (with NBSP where `__` markers require after AST-1027 preserve + builder expand) — not `|`.
- **Sibling check:** AST-1020 competencies CSS (uppercase / letter-spacing) unchanged. AST-1027 marker preserve still required. AST-1028 title/tagline split unchanged. Prior Experience uses the same `.competencies-list` markup — separator rules must stay consistent for that string when present. Verify: no CSS edits; builder competencies emit remains escape-only (no CSS `content:` fake bullets).
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done — DOM text must show bullets, not pipes.
- **Wrong fix rejected:** CSS `content:` / `::before` fake bullets while leaving `|` in the DOM; fixing only session surface and skipping base / job-tailored (all share `_emit_html_document`); rewriting competency **wording** rather than separators.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt`: harden `### core_competencies` (and align `### prior_experience`) — require `•` joins, forbid `|` separators | data/admin (repo JSON → startup apply) |

**Out of scope (do not touch):** `src/core/builder.py` competencies CSS or inventing CSS pseudo-bullets (AST-1020); marker digraph rules beyond separator choice (AST-1027); title/tagline (AST-1028); rewriting competency phrases; `tests/`, bible (Betty).

## Root cause (plan-time)

`_emit_body_sections_html` for `core_competencies` / `prior_experience` does `html.escape(str(text))` into `<p class="competencies-list">` — no `|`→`•` transform. After AST-1027, `### core_competencies` says *prefer* paste separators and *rather than* rewriting to `" | "` — soft language; the model still emits `|` when synthesizing/enriching (UAT Actual). Parent fixture / golden use `•` (often with `__` around tokens). Repo JSON applies at bootstrap via `apply_repo_admin_json_at_startup` — no new `database.py` migration.

## Stage 1: Harden competencies / prior separator rules in `craft_resume_base`

**Done when:** The repo `craft_resume_base` `cache_prompt` requires Core Competencies (and Prior Experience when present) to use `•` item separators — never `|` — whether copying from paste or synthesizing/enriching; paste `__` / `~~` / marked `•` forms are still preserved (AST-1027); file is valid JSON; only the `craft_resume_base` entry’s `cache_prompt` string changes for this stage.

1. In `data/admin/agent_task.json`, locate `"task_key": "craft_resume_base"` and edit its `cache_prompt` (surgical text — do not rewrite experience job-array, tagline, marker-preserve global rules, or unrelated segments).
2. **`### core_competencies`** — replace the soft “Prefer separators… rather than rewriting to `" | "`” sentence(s) with this meaning (wording may be tightened; must include these requirements):
   - Present as a **single string**.
   - Item separator is the bullet character `•` (plain ` • ` between items, or paste forms such as `__•__` / `__` around tokens + `•` — preserve markers when present).
   - **Do not** use `|` (pipe) as an item separator — not `" | "`, not bare `|`.
   - When the paste already uses `•` / marked bullets, copy those separators (and `__` / `~~`) unchanged.
   - When enriching or synthesizing a list (e.g. from LinkedIn strengths with evidence), **join with ` • `**, never `|`.
   - Still: evidence-backed only; keyword/phrase list; do not invent competencies; preserve `__` / `~~` when in the paste.
3. **`### prior_experience`** — ensure the condensed prior line uses the same bullet convention when listing roles (example already uses `•`); add an explicit **do not use `|` as separators** line so Prior Experience stays consistent with `.competencies-list` styling. Keep empty-string-when-absent behavior.
4. **QUALITY CHECKLIST** — add a bullet: `core_competencies` (and `prior_experience` when non-empty) use `•` separators, not `|`.
5. Do **not** change `_emit_body_sections_html` / CSS in `src/core/builder.py`.
6. Do **not** edit other `task_key` rows.
7. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Prompt harden only (not builder `|`→`•` rewrite, not CSS fake bullets). Emit is already faithful; soft “prefer” from AST-1027 left a pipe default for enrichment. Deterministic DOM fidelity for already-piped JSON would need a builder normalize — reject for this ticket to keep Single-Component / sibling pattern; if UAT still shows pipes after deploy+re-parse, escalate rather than silently adding emit rewrite mid-build. Startup applies repo JSON — no new migration.

## Stage 2: Builder emit lock + three-surface proof (manual / build verification)

**Done when:** With in-memory content whose `core_competencies` string already uses `•` separators, session / base / job-tailored HTML shows those bullets inside `.competencies-list` (escaped). Confirm builder does not introduce `|`. Negative note: in-memory content that still contains `|` will still render pipes (documents parse harden is required). Spike dumps only under `debug/spikes/AST-1029/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, confirm `git diff` does **not** touch `src/core/builder.py` competencies emit / CSS.
2. Exercise session builder with `core_competencies` like `AI-Assisted Delivery • Cross-Functional Execution • Risk and Dependency Management` — expect that text (HTML-escaped) in `.competencies-list`, no `|`.
3. Note for UAT: after deploy/restart so startup applies repo JSON, re-run Session Resume Paste Parse → Open HTML; `.competencies-list` must use bullets, not pipes.
4. If Stage 1 prompt text cannot be applied without breaking JSON / `{$RESPONSE_SCHEMA}`, **stop**, comment on **bug** AST-1029 with the Stage blocked template, and wait.

## Self-Assessment

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` text in `data/admin/agent_task.json` only; builder competencies emit left intact.

**Conf:** `high` — UAT Actual is `|` in `.competencies-list`; builder is escape-only; soft prefer language still names `" | "` as the thing not to rewrite to, which leaves pipe as the enrichment default.

**Risk:** `Medium` — prompt change hits all `craft_resume_base` consumers; over-strict wording could fight a rare paste that intentionally uses `|` inside a competency phrase — mitigated by forbidding `|` as **item separators** (space-pipe-space / pipe between items), not rewriting arbitrary characters inside phrases; checklist focuses on separators.

## Code Rules self-review

- §1.3 DRY: one shared emit path remains; prompt stops feeding it pipe-joined lists.
- §1.1 / scope isolation: no CSS; no builder separator rewrite; no AST-1020 chrome edits.
- §2.1: prompt lives in repo admin JSON (existing AST-782 path).
- §3.6: spikes under `debug/spikes/AST-1029/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1029-uat-competencies-pipes`
**Plan path:** `docs/features/artifacts/ast-1029-uat-competencies-pipes.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `f90922c4` | `craft_resume_base`: require `•` competencies/prior separators; forbid `|` |
| 2 | — | Builder competencies emit unchanged; session proof bullet list in `.competencies-list` |

**Tip:** `f90922c4` on `origin/sub/AST-1019/AST-1029-uat-competencies-pipes`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1029
**Publish ref tip (pre-docs):** `52962126030703df4509ace6abd6c61d77d36909`
**Overall:** CLEAN

### What’s solid

- Stage 1: `core_competencies` requires `•` joins and forbids `|`; `prior_experience` aligned; checklist bullet present.
- Builder competencies emit untouched (no `src/` in three-dot).
- Semantic JSON change is only `craft_resume_base.cache_prompt`.

### Issues / findings

None (fix-now / discuss).

### Recommended actions

resolve-child → User Testing (restart/deploy so startup applies repo JSON, then re-paste).

## Resolution

**2026-07-29** — Radia **CLEAN**; no fix-now / discuss items.

- Product tip remains `f90922c4` (`craft_resume_base` require `•` / forbid `|`).
- Intake: Radia `docs(AST-1029)` @ `b94e3b0b` on `origin/sub/AST-1019/AST-1029-uat-competencies-pipes`.
- No product or test-tree changes on resolve.

**UAT note:** restart/deploy so startup applies repo `agent_task.json`, then Session Resume Paste → Parse → Open HTML; `.competencies-list` must use `•`, not `|`.
