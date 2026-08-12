<!-- linear-archive: AST-1030 archived 2026-08-05 -->

## Linear archive (AST-1030)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1030/uat-no-bullet-lead-emitted-as-list-item  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1019 — Take 2: Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-1019

### Description

## What failed

`<no bullet>` lead copy under a role is emitted as a `<li>` inside `<ul>` instead of a non-list lead paragraph. Observed Somerset Consulting role HTML starts:

```
<ul>
  <li>Solo practice delivering embedded technical program management…</li>
  <li>Diagnosed and mitigated blockers…</li>
  …
</ul>
```

(no preceding `<p class="role-description">` for the `<no bullet>` line).

## Expected

Lines marked `<no bullet>` render as role lead paragraph (`.role-description`), not list items. Following true bullets remain `<li>`.

## Repro

1. Paste experience block including a `<no bullet>…` lead line under a role (as in parent Original brief / UAT paste).
2. Parse → Open HTML.
3. Confirm lead text is `<p class="role-description">` (or equivalent non-li), then `<ul><li>…` for real bullets only.

## Parent AC (quoted inline)

> Experience roles, education indent/credentials, and Technical Skills category grid match golden spacing/typography (items 7–9).
> Structure already owned by AST-993 … Experience role articles (compact title/location, optional lead paragraph, bullets) …
> Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on “close enough.”

## Diagnosis

* **Hypothesis:** `<no bullet>` marker is ignored in role-body emit — lead sentence folded into the bullet list.
* **Correct outcome:** Lead paragraph outside `<ul>`; only genuine bullets are `<li>`.
* **Wrong fix to avoid:** Unstyle the first `<li>` with CSS so it "looks" like a paragraph; drop the lead text.
* **Related siblings / contracts:** AST-993 role layout / `<no bullet>` convention; AST-1021 residual emit.

## Boundaries

* Does **not** change role CSS spacing rules (AST-1020) except as needed if class hooks were wrong.
* Does **not** invent new marker syntax beyond existing `<no bullet>`.

### Comments

#### radia — 2026-07-29T04:32:26.613Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1030
**Publish ref:** b35e68bbb40c8ebda4c8bb8a7a3de79a37695395
**Overall:** CLEAN

Diff basis: required `origin/dev...origin/sub/AST-1019/AST-1030-uat-no-bullet-lead` reports **multiple merge bases** (git picked `ab6e07a8…`) and therefore a noisy three-dot (spurious `canon/**` adds). Product review uses AST-1030 commits + `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies...HEAD` for the real child delta. Product @ `f54d3519` / merge-tests tip `67718600` + this `docs()` append. No `src/` in the AST-1030 code commit.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1030): origin/tests 133c5cde` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests`/`resolve` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish to child `origin/sub/…` |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1019; no remote-tracking merge subject on tip lineage |
| orch.git.merge-on-checkout | universal | conforms | No alternate merge inventiveness in AST-1030 commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1019 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis matches fixture; no product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 `<no bullet>` preserve Done-when matches tip |
| orch.pipeline.project-scoped-queues | universal | conforms | Single Artifacts bug child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Reviewed from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits in AST-1030 product commits |
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
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1030-….md` |
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

Stage 1 matches: preserve literal `<no bullet>` on paste role leads in `accomplishments`; following bullets unmarked; do-not-invent; checklist bullet present. Stage 2 builder lock holds — AST-1030 code commit does not touch `src/core/builder.py`. Scope Single-Component matches. Parsed JSON: only `craft_resume_base.cache_prompt` changed.

## Findings

None.

### What’s solid

Parse-side preserve so shared `_split_role_accomplishments` can emit `.role-description` then `<li>` — no CSS first-li restyle, no first-line heuristic.

### Recommended actions

resolve-child → User Testing. Restart/deploy so startup applies repo JSON, then re-paste Somerset `<no bullet>` fixture.

**Notes:** no plan-rubric verdict attached. FIX-UAT mode. Three-dot vs `origin/dev` multiple-merge-base noise recorded above; product judgment uses AST-1030 commits + ftr…HEAD delta.

— Radia
context_tokens≈40000

#### betty — 2026-07-29T04:28:01.100Z
## QA test manifest (AST-1030)

**Publish:** `origin/sub/AST-1019/AST-1030-uat-no-bullet-lead` @ `67718600` (`merge-tests(AST-1030): origin/tests 133c5cde`)

**FIX-UAT:** no `docs/test-bible/**` change on `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` since AST-1029 — skipped full bible re-read.

### Classification

1. **Existing coverage:** AST-1008 experience golden layout (lead → `.role-description`); AST-1027 marker preserve; AST-1028 title/tagline; AST-1029 competencies bullets; AST-996 job-array prompt.
2. **Broken / obsolete:** none — emit path unchanged; prompt was the gap.
3. **Gaps:** `craft_resume_base` must preserve paste `<no bullet>` on role leads (do not invent); emit lock with/without prefix.

### Manifest (narrowed)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1030CraftResumeBaseNoBulletPreserve \
  tests/component/core/test_candidate.py::TestAst1027CraftResumeBaseMarkerPreserve \
  tests/component/core/test_candidate.py::TestAst1029CraftResumeBaseCompetenciesBullets \
  tests/component/core/test_candidate.py::TestAst1028CraftResumeBaseTitleTaglineSplit \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract \
  tests/component/core/test_builder.py::TestAst1030UatNoBulletLeadEmit \
  tests/component/core/test_builder.py::TestAst1008ExperienceGoldenLayout \
  -q
```

### Bible shasums (on publish ref)

- `docs/test-bible/core/candidate.md` `aaaa01c6a43db24c9581f1683a1b6f766494c5ab`
- `docs/test-bible/core/builder.md` `cc32ad0795bb7e451e280f7c528d17d0d5e3edc7`

#### ada — 2026-07-29T04:22:16.194Z
Plan: [`docs/features/artifacts/ast-1030-uat-no-bullet-lead.md`](https://github.com/susansomerset/astral/blob/sub/AST-1019/AST-1030-uat-no-bullet-lead/docs/features/artifacts/ast-1030-uat-no-bullet-lead.md) on `origin/sub/AST-1019/AST-1030-uat-no-bullet-lead` @ `f04c2080`.

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` only; builder `_split_role_accomplishments` already correct when `<no bullet>` survives parse.

**Conf:** `high` — AST-1008 emit path proven; experience prompt never mentions preserving the marker; UAT Actual matches stripped prefix → all `<li>`.

**Risk:** `Medium` — prompt hits all `craft_resume_base` consumers; mitigated by paste-only preserve / do-not-invent language. Sub rooted on current ftr (no `Merge remote-tracking branch`).

---

# UAT: `<no bullet>` lead emitted as list item

**Linear:** [AST-1030](https://linear.app/astralcareermatch/issue/AST-1030/uat-no-bullet-lead-emitted-as-list-item)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1030-uat-no-bullet-lead`

Session Resume Paste → Parse → Open HTML folds the Somerset Consulting `<no bullet>` lead into the role `<ul>` as the first `<li>`, with no preceding `<p class="role-description">`. Shared `_emit_experience_jobs_html` / `_split_role_accomplishments` already treat lines starting with `BUILD_CONFIG["experience_role_layout"]["lead_line_prefix"]` (`<no bullet>`) as lead paragraphs and all other non-empty lines as bullets — AST-1008 coverage proves that path when the prefix is present in `accomplishments`. `craft_resume_base` experience instructions never mention preserving the literal `<no bullet>` marker, so parse drops or normalizes it and the lead becomes an ordinary bullet line. Fix the parse prompt so lead lines keep the prefix.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Experience roles, education indent/credentials, and Technical Skills category grid match golden spacing/typography (items 7–9).”* / *“Structure already owned by AST-993 … Experience role articles (compact title/location, optional lead paragraph, bullets) …”* / *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”*
- **Correct outcome:** Under a role with a paste `<no bullet>…` lead, HTML shows `<p class="role-description">…</p>` (prefix stripped at emit) **outside** `<ul>`, then `<ul><li>…` only for genuine achievement bullets. The literal `<no bullet>` string must not appear in HTML.
- **Sibling check:** AST-1008 / AST-993 role layout and `lead_line_prefix` contract unchanged. AST-1020 role CSS spacing unchanged. AST-1027 marker preserve still applies inside lead/bullet text. Verify: no CSS “first-li looks like a paragraph” hacks; `_split_role_accomplishments` / emit logic unchanged unless Stage 1 proves a genuine emit bug.
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done — lead must be a non-`<li>` paragraph in source.
- **Wrong fix rejected:** CSS unstyling the first `<li>` while leaving lead text inside `<ul>`; dropping the lead; inventing a new marker syntax beyond existing `<no bullet>`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt`: `### experience` / `accomplishments` — preserve literal `<no bullet>` prefix on lead lines | data/admin (repo JSON → startup apply) |

**Out of scope (do not touch):** `src/core/builder.py` role emit / `_split_role_accomplishments` (already correct when prefix present); AST-1020 role CSS; new marker digraphs; `tests/`, bible (Betty).

## Root cause (plan-time)

In `_split_role_accomplishments`, only lines with `startswith(lead_prefix)` (`<no bullet>`) become `.role-description`; every other non-empty line becomes `<li>`. Parent Original-brief paste uses `<no bullet>Solo practice…` under Somerset Consulting. `### experience` in `craft_resume_base` describes `accomplishments` as “paragraph and/or bullets… organize into the field, do not rewrite” but **never** requires keeping the literal `<no bullet>` token — so the model emits a plain first paragraph/line and emit treats it as a bullet. Repo JSON applies at bootstrap via `apply_repo_admin_json_at_startup` — no new `database.py` migration.

**Git hygiene:** This child’s `origin/sub/…` must stay rooted on current `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` with only AST-1030 vocabulary commits. Do **not** leave subjects matching `Merge remote-tracking branch` (validate-sub-log / merge-child gate — see AST-1029 hygiene).

## Stage 1: Preserve `<no bullet>` in `craft_resume_base` experience accomplishments

**Done when:** The repo `craft_resume_base` `cache_prompt` `### experience` section requires that when the resume/paste marks a role lead with `<no bullet>`, that exact prefix remains on the corresponding line(s) inside that job’s `accomplishments` string (newline-separated from following bullets); ordinary bullet lines have no such prefix; file is valid JSON; only the `craft_resume_base` entry’s `cache_prompt` string changes for this stage.

1. In `data/admin/agent_task.json`, locate `"task_key": "craft_resume_base"` and edit its `cache_prompt` (surgical text — do not rewrite job-array field list, marker-preserve globals, competencies/tagline rules from siblings).
2. Under **`### experience`**, extend the `accomplishments` field description and/or Rules with this meaning (wording may be tightened; must include these requirements):
   - `accomplishments` is one newline-separated text block for that role.
   - When the paste/resume has a `<no bullet>…` lead line for the role, copy that line into `accomplishments` **including the literal prefix** `<no bullet>` (then the rest of the lead sentence). Do **not** strip, paraphrase away, or replace the marker.
   - Following achievement bullets are additional lines **without** the `<no bullet>` prefix.
   - Do **not** invent a `<no bullet>` lead when the paste has none.
   - The HTML builder turns prefixed lines into `.role-description` and other lines into `<li>` — the marker must survive parse for that split to work.
3. **QUALITY CHECKLIST** — add a bullet: when the paste uses `<no bullet>` on a role lead, that prefix appears unchanged on the corresponding `accomplishments` line(s).
4. Do **not** change `src/core/builder.py` `_split_role_accomplishments` / `_emit_experience_jobs_html` / `lead_line_prefix` config unless Stage 2 finds a genuine emit bug (then **stop** and escalate on AST-1030).
5. Do **not** edit other `task_key` rows.
6. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Prompt preserve only (not builder heuristics that treat the first accomplishments line as a lead without the marker, not CSS first-`<li>` restyle). Emit contract is already AST-1008-correct when the prefix is present; inventing “first line is always lead” would mis-classify roles that have only bullets. Startup applies repo JSON — no new migration.

## Stage 2: Builder emit lock + three-surface proof (manual / build verification)

**Done when:** With in-memory experience job array whose Somerset-style `accomplishments` starts with `<no bullet>Solo practice…` then bullet lines, session / base / job-tailored HTML shows `.role-description` for the lead and `<li>` only for bullets; `<no bullet>` absent from HTML. Confirm builder split/emit source unchanged from pre-ticket tip. Spike dumps only under `debug/spikes/AST-1030/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, confirm `git diff` does **not** touch `src/core/builder.py` role emit helpers.
2. Exercise session builder with the AST-1008-style Somerset job blob (prefix present) — expect `.role-description` then `<ul><li>…`.
3. Negative check: same lead text **without** `<no bullet>` prefix still becomes first `<li>` — documents that parse preserve is required; do not add first-line heuristics.
4. Note for UAT: after deploy/restart so startup applies repo JSON, re-run Session Resume Paste Parse → Open HTML on the parent fixture; Somerset lead must be a paragraph, not a list item.
5. If Stage 1 prompt text cannot be applied without breaking JSON / `{$RESPONSE_SCHEMA}`, **stop**, comment on **bug** AST-1030 with the Stage blocked template, and wait.

## Self-Assessment

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` text in `data/admin/agent_task.json` only; builder role lead/bullet split left intact.

**Conf:** `high` — builder + AST-1008 already implement `<no bullet>` → `.role-description`; prompt never mentions the marker; UAT Actual matches stripped prefix → all `<li>`.

**Risk:** `Medium` — prompt change hits all `craft_resume_base` consumers; model might over-apply `<no bullet>` — mitigated by “only when paste has it” and “do not invent” language.

## Code Rules self-review

- §1.3 DRY: one shared split/emit path remains; prompt stops destroying its lead marker input.
- §1.1 / scope isolation: no CSS; no AST-1020 spacing edits; no new marker syntax.
- §2.1: prompt lives in repo admin JSON (existing AST-782 path); `lead_line_prefix` stays config-driven.
- §3.6: spikes under `debug/spikes/AST-1030/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1030-uat-no-bullet-lead`
**Plan path:** `docs/features/artifacts/ast-1030-uat-no-bullet-lead.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `f54d3519` | `craft_resume_base`: preserve `<no bullet>` on experience accomplishments leads |
| 2 | — | Builder split/emit unchanged; Somerset lead → `.role-description` proof |

**Tip:** `f54d3519` on `origin/sub/AST-1019/AST-1030-uat-no-bullet-lead`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1030
**Publish ref tip (pre-docs):** `67718600c18cd8472ccaf45337ea5db08824d59a`
**Overall:** CLEAN

### What’s solid

- Stage 1: `### experience` / `accomplishments` preserves literal `<no bullet>` on paste leads; do-not-invent; checklist bullet present.
- Builder split/emit untouched (AST-1030 code commit is `data/admin/agent_task.json` only).
- Semantic JSON change is only `craft_resume_base.cache_prompt`.

### Issues / findings

None (fix-now / discuss).

### Recommended actions

resolve-child → User Testing (restart/deploy so startup applies repo JSON, then re-paste).

## Resolution

**2026-07-29** — Radia **CLEAN**; no fix-now / discuss items.

- Product tip remains `f54d3519` (`craft_resume_base` preserve `<no bullet>` on accomplishments leads).
- Intake: Radia `docs(AST-1030)` @ `b35e68bb` on `origin/sub/AST-1019/AST-1030-uat-no-bullet-lead`.
- No product or test-tree changes on resolve.

**UAT note:** restart/deploy so startup applies repo `agent_task.json`, then Session Resume Paste → Parse → Open HTML on Somerset `<no bullet>` fixture; lead must be `.role-description`, not first `<li>`.
