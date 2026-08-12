<!-- linear-archive: AST-1028 archived 2026-08-05 -->

## Linear archive (AST-1028)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1028/uat-keywords-emit-in-resume-body-instead-of-meta  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1019 — Take 2: Resume Render Format discrepancies  
**Blocked by / blocks / related:** parent: AST-1019

### Description

## What failed

Keywords / specialty line is rendered in the resume body header instead of only in ATS meta. Observed body text:

`Susan Somerset&nbsp;• Fractional TPM — Program Delivery, Cross-Functional Alignment, Cloud SaaS, AI-Assisted Engineering`

Expected meta shape (Susan):
`<meta name="description" content="<keywords>" />` in `<head>` — keywords must not appear as visible header chrome.

## Expected

Header stays `Name • Title` (markers applied). Candidate-specific keywords/tagline feed `meta name="description"` (field-derived template), not an extra visible header line.

## Repro

1. Session Resume Paste with a paste that carries title + keyword/tagline fields (UAT paste showing Fractional TPM + keyword list).
2. Parse → Open HTML.
3. Confirm keywords are not in the visible header; confirm `<meta name="description">` carries the candidate-specific keywords string.

## Parent AC (quoted inline)

> Document `<title>` is `{candidate_name} Resume` (item 1).
> Meta description is candidate-specific from paste name/title/tagline (item 2) — not the stale Product Manager / Cloud Platforms example string when paste differs.
> Contact is the golden centered flex line; header remains `Name • Title` with markers — fixture shows `Susan Somerset • Senior Technical Program Manager` with non-breaking spaces from `__`.

## Diagnosis

* **Hypothesis:** Emit is dumping keyword/tagline into the header/title chrome (or a visible subtitle) instead of / in addition to meta description.
* **Correct outcome:** Visible header is name • title only; keywords live in meta description per field-derived template.
* **Wrong fix to avoid:** Hide keywords with `display:none` CSS while leaving them in the body DOM; force the golden example meta string.
* **Related siblings / contracts:** AST-1021 title/meta emit; AST-993 header/meta contracts.

## Boundaries

* Does **not** redesign meta template beyond field-derived candidate-specific rules already specified.
* Does **not** change stylesheet golden rules (AST-1020).

### Comments

#### radia — 2026-07-29T03:54:55.860Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1028
**Publish ref:** d749c101592bca0114d0a6650cc610a3a9632742
**Overall:** CLEAN

Diff: `origin/dev...origin/sub/AST-1019/AST-1028-uat-keywords-meta` (product @ `d83b486b` / merge-tests tip `efec1f04` + this `docs()` append). No `src/` delta; product is `data/admin/agent_task.json` (plus prior AST-1027 stack on the sub).

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1028): origin/tests 99df7288` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests`/`resolve` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish to child `origin/sub/…` |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1019 |
| orch.git.merge-on-checkout | universal | conforms | No alternate merge inventiveness |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | Authoritative sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1019 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | UAT diagnosis matches fixture; no product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 title/tagline split Done-when matches tip |
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
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1028-….md` |
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

Stage 1 matches: title-only `candidate_title`, inserted `### candidate_tagline` before contact, specialty/keywords forbidden in title. Stage 2 builder lock holds — no `src/core/builder.py` in three-dot. Scope Single-Component matches. Parsed JSON: only `craft_resume_base.cache_prompt` changed in the AST-1028 code commit.

## Findings

None.

### What’s solid

Parse-side split so shared emit keeps `<h1>` as name • title and puts tagline into field-derived meta only — no CSS hide, no meta-literal force, no builder strip hack.

### Recommended actions

resolve-child → User Testing. Restart/deploy so startup applies repo JSON, then re-paste a title + specialty fixture.

**Notes:** no plan-rubric verdict attached. FIX-UAT mode.

— Radia
context_tokens≈38000

#### betty — 2026-07-29T03:51:55.631Z
## QA test manifest (AST-1028)

**Publish:** `origin/sub/AST-1019/AST-1028-uat-keywords-meta` @ `efec1f04` (`merge-tests(AST-1028): origin/tests 99df7288`)

**FIX-UAT:** no `docs/test-bible/**` change on `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` since AST-1027 — skipped full bible re-read.

### Classification

1. **Existing coverage:** AST-1010 header/meta + tagline body exclusion; AST-1021 title/meta; AST-1027 marker preserve; AST-996 job-array prompt.
2. **Broken / obsolete:** none — emit already correct when fields are split; bug was parse folding keywords into `candidate_title`.
3. **Gaps:** `craft_resume_base` title-only + `### candidate_tagline` prompt contract; UAT Fractional TPM + keyword tagline session emit.

**Integration:** no existing scenario asserts title/tagline split — no revision.

### Manifest (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1028CraftResumeBaseTitleTaglineSplit \
  tests/component/core/test_candidate.py::TestAst1027CraftResumeBaseMarkerPreserve \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract \
  tests/component/core/test_builder.py::TestAst1028UatKeywordsMetaEmit \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/core/test_builder.py::TestAst1021DocumentTitleChrome \
  -q
```

### Bible shasums (on publish tip)

- `docs/test-bible/core/candidate.md` `d262c5212b4d05cbb33f70980a2abe66df4e874a`
- `docs/test-bible/core/builder.md` `1d33a38c6eddd1a8b1e68fcb8e9ba9c78df037ac`

— Betty

#### ada — 2026-07-29T03:46:35.356Z
Plan: [`docs/features/artifacts/ast-1028-uat-keywords-meta.md`](https://github.com/susansomerset/astral/blob/sub/AST-1019/AST-1028-uat-keywords-meta/docs/features/artifacts/ast-1028-uat-keywords-meta.md) on `origin/sub/AST-1019/AST-1028-uat-keywords-meta` @ `a475761b`.

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` only; builder header/meta already correct when title vs tagline are split.

**Conf:** `high` — UAT Actual is title+keywords mash in `<h1>`; prompt has no `### candidate_tagline` while schema/builder already support the field.

**Risk:** `Medium` — prompt change hits all `craft_resume_base` consumers; mitigated by surgical title/tagline split language and no builder rewrite.

---

# UAT: keywords emit in resume body instead of meta

**Linear:** [AST-1028](https://linear.app/astralcareermatch/issue/AST-1028/uat-keywords-emit-in-resume-body-instead-of-meta)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1028-uat-keywords-meta`

Session Resume Paste → Parse → Open HTML shows specialty / keyword text in the visible header (mashed into `candidate_title`, e.g. `Name • Fractional TPM — Program Delivery, …`) instead of only feeding ATS meta. Shared `_emit_html_document` already builds `<h1>` from `name • title` only and puts `candidate_tagline` solely into `<meta name="description">` via the AST-1010 field-derived template — but `craft_resume_base` `cache_prompt` has **no** `### candidate_tagline` segment (it jumps from `candidate_title` to `candidate_contact_detail`), so the model dumps the paste specialty line into `candidate_title`. Fix the parse prompt so title stays title-only and the specialty/keyword line lands in `candidate_tagline`.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Document `<title>` is `{candidate_name} Resume` (item 1).”* / *“Meta description is candidate-specific from paste name/title/tagline (item 2) — not the stale Product Manager / Cloud Platforms example string when paste differs.”* / *“Contact is the golden centered flex line; header remains `Name • Title` with markers — fixture shows `Susan Somerset • Senior Technical Program Manager` with non-breaking spaces from `__`.”*
- **Correct outcome:** Visible header `<h1>` is `Name • Title` only (markers applied). Specialty / keyword / tagline text from the paste does **not** appear in header or main body. When name, title, and tagline are all non-empty, `<meta name="description">` is the field-derived template `Resume of {name}, {title}, specializing in {tagline}` (tagline carries the candidate-specific keywords string) — not a hardcoded golden example.
- **Sibling check:** AST-1021 title/meta emit contract stays (`{name} Resume` title; same meta template). AST-1020 stylesheet unchanged. AST-993 / AST-1010 header join + tagline-as-contact-section (excluded from body) unchanged. AST-1027 marker preserve still required for `__` in title/tagline strings. Verify: no CSS edits; no change to meta template string shape; builder still excludes `candidate_tagline` from body via `RESUME_STRUCTURE_CONTACT_SECTION_IDS`.
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done — keywords must leave the visible header and land in meta via `candidate_tagline`.
- **Wrong fix rejected:** CSS `display:none` / hide a `.specialties` body node while leaving keywords in the DOM; forcing the golden HTML example meta literal; concatenating keywords into `<title>`; rewriting `_emit_html_document` to strip after the em-dash in `candidate_title` instead of teaching parse to split fields.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt`: add `### candidate_tagline` segment; tighten `### candidate_title` so specialty/keyword lines are **not** folded into title | data/admin (repo JSON → startup apply) |

**Out of scope (do not touch):** `src/core/builder.py` header/meta emit (AST-1010 / AST-1021 already correct when fields are split); embedded stylesheet (AST-1020); marker digraph rules (AST-1027); inventing a new meta template; `tests/`, bible (Betty).

## Root cause (plan-time)

In `data/admin/agent_task.json` → `craft_resume_base` → `cache_prompt`, **SEGMENT INSTRUCTIONS** list `### candidate_name`, then `### candidate_title` (“professional title/headline… under 15 words”), then immediately `### candidate_contact_detail` — **no** `### candidate_tagline`. Config schema already has optional `candidate_tagline` (`TASK_CONFIG` / artifact shapes / `RESUME_STRUCTURE_CONTACT_SECTION_IDS`). Builder `_emit_html_document` reads `candidate_tagline` for meta only and never emits a specialties line in `<header>` / `<main>`. UAT Actual (`Susan Somerset • Fractional TPM — Program Delivery, …`) matches title+keywords mashed into `candidate_title` (em-dash join), which the builder faithfully places in `<h1>`. Session parse uses `do_task("craft_resume_base")`; repo JSON applies at bootstrap via `apply_repo_admin_json_at_startup` — no new `database.py` migration.

Bug Description’s shorthand `content="<keywords>"` means keywords belong in meta **content**, not that meta should be bare keywords only — parent laundry-list item 2 / AST-1010 template remains authoritative.

## Stage 1: Teach `craft_resume_base` to split title vs tagline

**Done when:** The repo `craft_resume_base` `cache_prompt` has an explicit `### candidate_tagline` segment between `candidate_title` and `candidate_contact_detail`; `candidate_title` instructions forbid folding specialty / keyword / “specializing in …” lines into the title; when the paste has a title line and a separate specialty/keyword line (parent fixture: line after title before contact), those map to `candidate_title` and `candidate_tagline` respectively; file is valid JSON; only the `craft_resume_base` entry’s `cache_prompt` string changes for this stage.

1. In `data/admin/agent_task.json`, locate the object with `"task_key": "craft_resume_base"` and edit its `cache_prompt` string (surgical text inside the existing prompt — do not rewrite unrelated segment rules, experience job-array contract, or AST-1027 marker-preserve language).
2. **`### candidate_title`** — replace/extend so the model must:
   - Put **only** the professional title / job headline in `candidate_title` (paste title line is authoritative; LinkedIn blend still OK when no conflicting specialty line).
   - **Not** append specialty phrases, keyword lists, “specializing in …”, or em/en-dash–joined keyword tails to the title.
   - Keep it concise (under ~15 words) — title alone, not title + tagline.
3. **Insert `### candidate_tagline`** immediately after `### candidate_title` and before `### candidate_contact_detail`, with this meaning (wording may be tightened, must include these requirements):
   - Optional string: the specialty / keyword / focus line from the resume/paste (the line that sits between title and contact when present — parent fixture example: `Enterprise Implementation • Service Delivery • …`).
   - Copy paste separators and typography markers (`__`, `~~`, `•`) into the tagline value when present (AST-1027 preserve still applies).
   - Do **not** invent a tagline when the paste has none; omit or empty string is OK (schema `required: false`).
   - Do **not** put contact fields or section titles into tagline.
   - This field feeds ATS meta only in HTML emit — it must **not** be duplicated into `candidate_title` or body section strings.
4. If a **QUALITY CHECKLIST** (or similar) lists identity fields, add a bullet: title is title-only; specialty/keyword line is `candidate_tagline` when present in the paste.
5. Do **not** change `src/utils/config.py` schema keys (already has `candidate_tagline`) unless Stage 1 cannot land without it — if schema is missing from the applied Manage Tasks row and that blocks the model from returning the field, **stop** and comment on **bug** AST-1028 with the Stage blocked template (do not invent a new field name).
6. Do **not** edit other `task_key` rows in `agent_task.json`.
7. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Prompt-only split (not builder post-processing of mashed titles). Builder contracts for header/meta are already correct when fields are separate; changing emit to guess “everything after — is tagline” would fight paste fidelity and AST-1010 tests. Parent epic forbids Manage Tasks *redesign*; this is a surgical segment-instruction patch on `craft_resume_base` only. Startup applies repo JSON — no new migration.

## Stage 2: Builder emit lock + three-surface proof (manual / build verification)

**Done when:** With in-memory content where `candidate_title` is title-only and `candidate_tagline` holds the specialty line, `build_session_base_resume` / `build_base_resume` / `build_resume_from_job` HTML shows `<h1>` with `Name • Title` only (no specialty text in header/main), and `<meta name="description">` matches `Resume of {name}, {title}, specializing in {tagline}` from those fields. Confirm `_emit_html_document` header/meta source is unchanged from pre-ticket tip (no builder product edit required if Stage 1 is sufficient). Spike dumps only under `debug/spikes/AST-1028/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, confirm `git diff` does **not** touch `src/core/builder.py` header/meta emit unless a genuine emit bug is found (then **stop** and escalate on AST-1028 — do not silently expand scope).
2. Exercise session builder with sample blob: `candidate_name=Susan Somerset`, `candidate_title=Fractional TPM`, `candidate_tagline=Program Delivery, Cross-Functional Alignment, Cloud SaaS, AI-Assisted Engineering` — expect `<h1>` without the keyword string, and meta content containing that tagline via the field-derived template.
3. Negative check: blob with keywords only in `candidate_title` (pre-fix mash) still shows them in `<h1>` — documents that parse split is required; do not add builder strip logic.
4. Note for UAT: after deploy/restart so startup applies repo JSON, re-run Session Resume Paste Parse → Open HTML on a paste with title + specialty line; header must be name • title only; meta must carry the tagline via the AST-1010 template.
5. If Stage 1 prompt text cannot be applied without breaking JSON / `{$RESPONSE_SCHEMA}`, **stop**, comment on **bug** AST-1028 with the Stage blocked template, and wait.

## Self-Assessment

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` text in `data/admin/agent_task.json` only; builder header/meta left intact.

**Conf:** `high` — UAT Actual matches title+keywords mash; prompt has no `candidate_tagline` segment while schema/builder already support the field; same admin-JSON path as AST-1027.

**Risk:** `Medium` — prompt change hits all `craft_resume_base` consumers (session + craft); wrong wording could leave tagline empty or still mash title — mitigated by explicit split language and no builder rewrite.

## Code Rules self-review

- §1.3 DRY: one shared emit path remains `_emit_html_document`; prompt stops feeding it a mashed title.
- §1.1 / scope isolation: no CSS; no AST-1021 meta-template redesign; no AST-1020 stylesheet edits.
- §2.1: prompt lives in repo admin JSON (existing AST-782 path), not new config magic.
- §3.6: spikes under `debug/spikes/AST-1028/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1028-uat-keywords-meta`
**Plan path:** `docs/features/artifacts/ast-1028-uat-keywords-meta.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `d83b486b` | `craft_resume_base` cache_prompt: title-only + `### candidate_tagline` |
| 2 | — | Builder header/meta unchanged; session emit proof tagline in meta only |

**Tip:** `d83b486b` on `origin/sub/AST-1019/AST-1028-uat-keywords-meta`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1028
**Publish ref tip (pre-docs):** `efec1f04a96f9e063840f2e2c31e5b6b12af1883`
**Overall:** CLEAN

### What’s solid

- Stage 1: `candidate_title` title-only; new `### candidate_tagline` between title and contact; specialty/keywords stay out of title.
- Builder header/meta untouched (no `src/` in three-dot); emit already correct when fields are split.
- Semantic JSON change is only `craft_resume_base.cache_prompt`.

### Issues / findings

None (fix-now / discuss).

### Recommended actions

resolve-child → User Testing (restart/deploy so startup applies repo JSON, then re-paste).

## Resolution

**2026-07-29** — Radia **CLEAN**; no fix-now / discuss items.

- Product tip remains `d83b486b` (`craft_resume_base` title vs tagline split).
- Intake: Radia `docs(AST-1028)` @ `d749c101` on `origin/sub/AST-1019/AST-1028-uat-keywords-meta`.
- No product or test-tree changes on resolve.

**UAT note:** restart/deploy so startup applies repo `agent_task.json`, then Session Resume Paste → Parse → Open HTML on a title + specialty fixture; header must be name • title only; meta carries tagline via AST-1010 template.
