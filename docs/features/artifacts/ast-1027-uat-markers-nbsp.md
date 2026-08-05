<!-- linear-archive: AST-1027 archived 2026-08-05 -->

## Linear archive (AST-1027)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1027/uat-markers-not-11-andnbsp-in-html-emit  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1019 — Take 2: Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-1019

### Description

## What failed

Session Resume Paste → Open HTML emits skill / separator lines where `__` markers are not replaced 1:1 with `&nbsp;`. Example input:

`Program & Delivery: Jira__•__Confluence__•__Linear__• Jira__Align__•__Azure__DevOps__•__Asana__• Trello__•__JAMA__•__Pivotal__Tracker`

Actual HTML (skill-category):
`Jira&nbsp;• Confluence&nbsp;• Linear&nbsp;• Jira Align&nbsp;• Azure DevOps&nbsp;• Asana&nbsp;• Trello&nbsp;• JAMA&nbsp;• Pivotal Tracker`

Gaps: after each `•` a normal space remains; word-joins like `Jira__Align` become ordinary spaces instead of `&nbsp;`.

## Expected

Every `__` in the paste is replaced with `&nbsp;` (1:1). For the sample: `Jira&nbsp;•&nbsp;Confluence&nbsp;•&nbsp;…` and `Jira&nbsp;Align` (etc.).

## Repro

1. Open Session Resume Paste.
2. Paste fixture text that includes `__` around bullets and inside multi-word tokens (as above).
3. Parse → Open HTML; inspect skills / competencies / contact source for `__` → `&nbsp;` fidelity.

## Parent AC (quoted inline)

> Pasting the Original-brief input fixture through Session Resume Paste Parse → Open HTML yields an embedded `<style>` that carries the golden rules… — verifiable in HTML source and print/preview.
> Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on “close enough.”
> Structure already owned by AST-993 (must remain correct under the new styles): … nested `__` / `~~` markers end-to-end.

## Diagnosis

* **Hypothesis:** Marker expand for `__` is incomplete around `•` and multi-word joins — left-side nbsp applied inconsistently; right-side / intra-word `__` sometimes becomes a plain space.
* **Correct outcome:** HTML source shows `&nbsp;` everywhere the paste had `__`, matching golden contact/skills nbsp treatment.
* **Wrong fix to avoid:** CSS `white-space` hacks or post-hoc string replace only in one surface; skip shared builders.
* **Related siblings / contracts:** AST-1020 (stylesheet) — CSS-only; AST-1021 (emit/chrome); AST-993 marker contract must hold.

## Boundaries

* Does **not** change golden CSS rules or invent new marker syntax.
* "Looks close in the browser" alone is **not** done — source must be 1:1 `__` → `&nbsp;`.

### Comments

#### radia — 2026-07-29T03:39:15.905Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1027
**Publish ref:** f8f0f3247f21d3b239f2947d7f4412fa891ae5b9
**Overall:** CLEAN

Diff: `origin/dev...origin/sub/AST-1019/AST-1027-uat-markers-nbsp` (product @ `eedc91e4` / merge-tests tip `b16675cd` + this `docs()` append). No `src/` delta in the three-dot; product is `data/admin/agent_task.json`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1027): origin/tests b264fd61` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish to child `origin/sub/…` |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1019 |
| orch.git.merge-on-checkout | universal | conforms | No alternate merge inventiveness |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1019 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis matches Archie/Susan fixture; no product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 preserve-prompt Done-when matches tip |
| orch.pipeline.project-scoped-queues | universal | conforms | Single Artifacts bug child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Reviewed from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test` + `merge-tests`; Ada avoided test tree |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
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
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1027-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits only tests/bible (+ merge-tests) |
| astral.git.engineer-test-tree-ban | scoped | conforms | Ada code/docs omit tests/bible |
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

Stage 1 matches: `craft_resume_base` cache_prompt preserves `__`/`~~`, checklist rewritten, skills/contact/prior/competencies paste-faithful. Stage 2 builder lock holds — `src/core/builder.py` absent from three-dot. Scope Single-Component matches. Parsed JSON: only `craft_resume_base.cache_prompt` differs from parent tip (other task rows equal after parse despite raw unicode re-encoding in the file).

## Findings

None.

### What’s solid

Root cause fix is prompt-side preserve so shared `_resume_site_markers` can expand 1:1; no CSS/chrome/builder rewrite.

### Recommended actions

resolve-child → User Testing. UAT still needs restart/deploy so startup applies repo JSON, then re-paste fixture.

**Notes:** no plan-rubric verdict attached.

— Radia
context_tokens≈42000

#### betty — 2026-07-29T03:35:14.789Z
## QA test manifest (AST-1027)

**Publish:** `origin/sub/AST-1019/AST-1027-uat-markers-nbsp` @ `b16675cd` (`merge-tests(AST-1027): origin/tests b264fd61`)

**FIX-UAT:** no `docs/test-bible/**` change on `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` since AST-1021 merge-tests — skipped full bible re-read.

### Classification

1. **Existing coverage:** AST-1007 nested/three-surface marker expand; AST-996 craft_resume_base job-array prompt contract.
2. **Broken / obsolete:** none — expand path was already correct; parse prompt was destroying digraphs.
3. **Gaps:** `craft_resume_base` cache_prompt preserve/`__`/`~~` no-strip contract; UAT skill-line expand (`Jira__•__…`, `Jira__Align`).

**Integration:** no existing scenario asserts marker preserve — no revision.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1027CraftResumeBaseMarkerPreserve \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract \
  tests/component/core/test_builder.py::TestAst1027UatMarkerExpand \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers \
  -q
```

### Bible shasums (on publish tip)

- `docs/test-bible/core/candidate.md` `b8ec19d85769635d6cf486753ec547486af38d3e`
- `docs/test-bible/core/builder.md` `94b889ab6c98fcb27ec900164c845f51c9778535`

— Betty

#### ada — 2026-07-29T03:28:37.082Z
Plan: [`docs/features/artifacts/ast-1027-uat-markers-nbsp.md`](https://github.com/susansomerset/astral/blob/sub/AST-1019/AST-1027-uat-markers-nbsp/docs/features/artifacts/ast-1027-uat-markers-nbsp.md) on `origin/sub/AST-1019/AST-1027-uat-markers-nbsp` @ `f28d8dbf`.

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` in `data/admin/agent_task.json` only; `_resume_site_markers` left intact.

**Conf:** `high` — UAT Actual matches `__` stripped by parse then asymmetric `" • "` rule; prompt line explicitly orders that strip; startup applies repo JSON.

**Risk:** `Medium` — prompt change hits all `craft_resume_base` consumers (session + craft); mitigated by surgical preserve language and no builder rewrite.

---

# UAT: __ markers not 1:1 &nbsp; in HTML emit

**Linear:** [AST-1027](https://linear.app/astralcareermatch/issue/AST-1027/uat-markers-not-11-andnbsp-in-html-emit)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1027-uat-markers-nbsp`

Session Resume Paste → Parse → Open HTML loses `__` / `~~` digraphs because `craft_resume_base` instructs the model to strip them (`__` → space, `~~` → hyphen). Shared `_resume_site_markers` then never sees `__`, so only the legacy `" • "` → `"\u00a0• "` rule runs — matching the UAT Actual (nbsp left of `•`, regular spaces elsewhere, including `Jira Align`). Fix the parse prompt so markers survive into content; builder expand already converts `__` → NBSP / `~~` → non-breaking hyphen on all three surfaces.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Pasting the Original-brief input fixture through Session Resume Paste Parse → Open HTML yields an embedded `<style>` that carries the golden rules… — verifiable in HTML source and print/preview.”* / *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”* / *“Structure already owned by AST-993 (must remain correct under the new styles): … nested `__` / `~~` markers end-to-end.”*
- **Correct outcome:** After Parse → Open HTML on the fixture paste, HTML text nodes show NBSP (`\u00a0` / `&nbsp;` in serialized source) everywhere the paste had `__`, and non-breaking hyphens where it had `~~` — e.g. `Jira\u00a0•\u00a0Confluence` for `__•__` joins and `Jira\u00a0Align` for `Jira__Align` — matching golden contact/skills nbsp treatment.
- **Sibling check:** AST-1020 stylesheet unchanged (CSS-only). AST-1021 title/meta emit unchanged. AST-993 / AST-1007 marker contract in `_resume_site_markers` unchanged (still `__` → `\u00a0`, `~~` → `\u2011`, `" • "` → `"\u00a0• "`). Verify by string-search: no CSS edits; builder marker helper body unchanged; Open HTML still uses shared builders.
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done — markers must be 1:1 in HTML source.
- **Wrong fix rejected:** CSS `white-space` hacks, or a surface-local post-hoc replace that skips shared builders / leaves `craft_resume_base` still stripping `__`. Builder expand is already correct when `__` is present; the bug is parse destroying digraphs before emit.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt`: preserve `__` / `~~` in section strings; stop instructing strip-to-space/hyphen; align skills/prior/contact segment rules with paste-faithful separators | data/admin (repo JSON → startup apply) |

**Out of scope (do not touch):** `src/core/builder.py` `_resume_site_markers` substitutions (AST-1007 contract); embedded stylesheet (AST-1020); document title / meta (AST-1021); inventing new marker digraphs; CSS-only “looks close” patches; `tests/`, bible (Betty).

## Root cause (plan-time)

In `data/admin/agent_task.json` → `craft_resume_base` → `cache_prompt`, **FORMATTING RULES (GLOBAL)** item 1 currently says: strip `__` (replace with space) and `~~` (replace with hyphen). Quality checklist requires “All formatting codes stripped clean.” Session parse uses that prompt (`run_session_resume_parse` → `do_task("craft_resume_base")`). After strip, `_resume_site_markers` cannot expand `__`; the asymmetric `" • "` legacy rule alone produces the UAT Actual pattern. Repo JSON is applied at bootstrap (`apply_repo_admin_json_at_startup` → retires current `agent_task` rows and loads `data/admin/agent_task.json`), so updating the JSON is the deploy path — no separate `database.py` migration required for this ticket.

## Stage 1: Preserve `__` / `~~` in `craft_resume_base` cache_prompt

**Done when:** The repo `craft_resume_base` `cache_prompt` no longer tells the model to replace `__` with space or `~~` with hyphen; it explicitly requires those digraphs to be copied into section string values (and experience job string fields) when present in the resume/paste; checklist no longer demands “formatting codes stripped clean” for `__`/`~~`; skills/contact/prior instructions do not force rewriting marked `•` separators into `|` when the paste uses bullets + markers. File is valid JSON; only the `craft_resume_base` entry’s `cache_prompt` string changes (plus any minimal segment-instruction sentences listed below).

1. In `data/admin/agent_task.json`, locate the object with `"task_key": "craft_resume_base"` and edit its `cache_prompt` string as follows (surgical text edits inside the existing prompt — do not rewrite unrelated segment synthesis rules).
2. **FORMATTING RULES (GLOBAL) item 1** — replace the current strip rule with this meaning (wording may be tightened for clarity, but must include these requirements):
   - Still strip `!` line prefixes and markdown headers (`#…`).
   - **Preserve** the two-character digraphs `__` and `~~` **literally** in every section string value (including nested experience job fields). Do **not** replace `__` with a space or `~~` with a hyphen. The HTML builder expands them later (`__` → NBSP, `~~` → non-breaking hyphen).
   - Still no HTML tags or markdown emphasis syntax in values — digraphs `__` / `~~` are typography markers, not markdown.
3. **QUALITY CHECKLIST** — remove or rewrite the bullet “All formatting codes stripped clean” so it instead requires: when the resume/paste contains `__` or `~~`, those digraphs appear unchanged in the corresponding JSON string values.
4. **Segment instructions that currently fight markers** (edit only these sentences as needed):
   - **`technical_skills`:** Stop requiring items separated by `" | "` when the paste uses `•` / `__•__`. Require: preserve category lines and item separators **from the resume/paste** (including `__`, `~~`, and `•`); do not rewrite marked bullet separators into pipes.
   - **`prior_experience`:** Remove “stripped of formatting codes”; preserve `__` / `~~` / `•` from the paste line.
   - **`candidate_contact_detail`:** When the paste uses `__•__` (or `__` around contact parts), preserve those digraphs in the single contact string; do not expand them to ordinary spaces. (Plain `" • "` joins remain OK when the paste has no markers.)
   - **`core_competencies`:** Prefer paste separators; if the paste uses marked `•` / `__`, preserve them rather than forcing `" | "`.
5. Do **not** change `_resume_site_markers` in `src/core/builder.py`.
6. Do **not** edit other `task_key` rows in `agent_task.json`.
7. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Prompt preserve + existing shared builder expand (not a builder rewrite). Diagnosis matches: expand looks “incomplete” only because parse destroyed digraphs first. Parent epic forbids Manage Tasks *redesign*; this is a one-rule + checklist + separator-faithfulness patch on `craft_resume_base` only. Startup `apply_repo_admin_json_at_startup` publishes the JSON into DB — no new migration function.

## Stage 2: Builder contract lock + three-surface proof (manual / build verification)

**Done when:** With in-memory content that still contains `__` / `~~` (as after a correct parse), `build_session_base_resume` / `build_base_resume` / `build_resume_from_job` HTML shows NBSP for every `__` and non-breaking hyphen for every `~~` on skills/contact/competencies-style strings (same shared `_emit_html_document` path). Confirm `_resume_site_markers` source is unchanged from pre-ticket tip. Spike dumps only under `debug/spikes/AST-1027/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, confirm `git diff` does **not** touch `src/core/builder.py` marker helpers.
2. Exercise `_resume_site_markers` / session builder with the bug sample skill line containing `Jira__•__Confluence` and `Jira__Align` — expect `\u00a0` on both sides of `__•__` and between `Jira`/`Align`.
3. Note for UAT: after deploy/restart so startup applies repo JSON, re-run Session Resume Paste Parse → Open HTML on the parent fixture; HTML source must show 1:1 `__` → NBSP (not ordinary spaces on word joins).
4. If Stage 1 prompt text cannot be applied without breaking JSON / schema tokens (`{$RESPONSE_SCHEMA}` must remain), **stop**, comment on **bug** AST-1027 with the Stage blocked template, and wait.

## Self-Assessment

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` text in `data/admin/agent_task.json` only; builder marker expand left intact.

**Conf:** `high` — UAT Actual matches “`__` stripped then asymmetric `" • "` rule”; prompt line explicitly orders that strip; startup applies repo JSON.

**Risk:** `Medium` — prompt change affects all `craft_resume_base` consumers (session paste and candidate craft); wrong wording could leave markers stripped or reintroduce markdown noise — mitigated by explicit preserve language and narrow file scope.

## Code Rules self-review

- §1.3 DRY: one shared expand path remains `_resume_site_markers`; prompt stops destroying its inputs.
- §1.1 / scope isolation: no CSS; no AST-1021 chrome; no new marker syntax.
- §2.1: prompt lives in repo admin JSON (existing AST-782 path), not new config magic.
- §3.6: spikes under `debug/spikes/AST-1027/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1027-uat-markers-nbsp`
**Plan path:** `docs/features/artifacts/ast-1027-uat-markers-nbsp.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `eedc91e4` | `craft_resume_base` cache_prompt preserves `__` / `~~`; paste-faithful separators |
| 2 | — | Builder markers unchanged; session expand proof for sample skill/contact lines |

**Tip:** `eedc91e4` on `origin/sub/AST-1019/AST-1027-uat-markers-nbsp`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1027
**Publish ref tip (pre-docs):** `b16675cd6ff0d0fbfa26f0ba7c1e0e143304967d`
**Overall:** CLEAN

### What’s solid

- Stage 1: `craft_resume_base` `cache_prompt` preserves `__` / `~~`; checklist no longer demands strip-clean; skills/contact/prior/competencies keep paste separators.
- Builder `_resume_site_markers` untouched (three-dot has no `src/` product delta for this ticket’s intent).
- Semantic JSON diff is only that one `cache_prompt` field (other task rows equal after parse).

### Issues / findings

None (fix-now / discuss).

### Recommended actions

resolve-child → User Testing.

## Resolution

**2026-07-29** — Radia **CLEAN**; no fix-now / discuss items.

- Product tip remains `eedc91e4` (`craft_resume_base` preserve `__`/`~~`).
- Intake: Radia `docs(AST-1027)` @ `f8f0f324` on `origin/sub/AST-1019/AST-1027-uat-markers-nbsp`.
- No product or test-tree changes on resolve.

**UAT note:** restart/deploy so startup applies repo `agent_task.json`, then Session Resume Paste → Parse → Open HTML on the fixture; expect 1:1 `__` → `&nbsp;`.
