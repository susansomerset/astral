# AST-1458 — Job resume draft prompt is asking for bullet chars
**Component:** artifacts  
**Children:** AST-1465  
**Linear archived:** AST-1458 2026-09-09; AST-1465 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-24 15:02 | AST-1465 | docs | `4b0662d6f` | docs(AST-1465): plan — omit bullet marker glyphs from draft prompt |
| 2026-08-24 15:05 | AST-1465 | docs | `fa0380f61` | docs(AST-1465): Joan validate — Betty owns test lock |
| 2026-08-24 15:08 | AST-1465 | docs | `873cd3456` | docs(AST-1465): plan revise — Betty owns glyph test lock |
| 2026-08-24 15:10 | AST-1465 | docs | `122537eac` | docs(AST-1465): Joan validate round 2 — APPROVED |
| 2026-08-24 15:13 | AST-1465 | code | `3f62eca29` | code(AST-1465): omit bullet marker glyphs from draft prompt |
| 2026-08-24 15:13 | AST-1465 | docs | `5ed5d1186` | docs(AST-1465): review stub after Stage 1 |
| 2026-08-24 15:19 | AST-1465 | test | `e1dc62be3` | test(AST-1465): glyph lock on draft_job_resume prompt |
| 2026-08-24 15:21 | AST-1465 | merge-tests | `9a1bb3aac` | merge-tests(AST-1465): origin/tests e1dc62be362e072790f38ff44c03759eca97fa6e |
| 2026-08-24 15:26 | AST-1458/1465 | sync | `fce74d6fd` | sync(publish-ref): origin/sub/AST-1458/AST-1465-draft-job-resume-prompt-omit-bullet-marker-glyphs |
| 2026-08-24 15:31 | AST-1465 | docs | `ceafe9d70` | docs(AST-1465): Radia review — CLEAN |
| 2026-08-25 17:38 | AST-1458 | docs | `64125495e` | docs(AST-1458): mirror epic registry Threads |
| 2026-09-09 17:55 | AST-1465 | docs | `607dd8d9e` | docs(AST-1465): archive Linear issue content |
| 2026-09-09 18:06 | AST-1458 | docs | `fa2be7b32` | docs(AST-1458): archive Linear issue content |

## Epic — AST-1458
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1458/job-resume-draft-prompt-is-asking-for-bullet-chars · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: None / 1 · Blocked by / blocks / related: —_

### Purpose

The `draft_job_resume` Manage Tasks `user_prompt` currently embeds literal list-marker glyphs (`•`, `-`, `*`) when telling Judith that `accomplishments` entries must be bare strings in a JSON array. Susan wants those characters removed from the prompt text while keeping the same contract: accomplishment strings are plain text with no leading list markers. This is a prompt-wording-only fix in the repo seed catalog — no runtime validation, normalize, or builder changes.

### Functional scope

* Reword the `draft_job_resume` `user_prompt` so it no longer displays bullet/marker character literals; the instruction still requires `accomplishments` as an ordered array of plain strings (no markdown or list-prefix decoration in the JSON values).
* Leave all other draft-hop rules intact: nested `agent_payload.resume` + `deviations`, job-array experience contract, trace-to-base-materials discipline, and existing section-key alignment with the base resume.
* Does not change `craft_resume_base`, `finalize_job_resume`, `advise_job_resume`, or `check_job_resume` prompts unless Susan directs otherwise in a follow-up.

### Architectural definition

* **Patterns to reuse** — no established pattern applies (Susan-owned prompt prose in repo seed JSON; no new reusable shape).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.seed.archie-catalog-wins` (lasting prompt content lives in committed `data/admin/agent_task.json`, not live DB edits alone); `astral.seed.agent-tables-in-repo-json` (`agent_task.json` is the authoritative seed for task prompt rows); `astral.standards.in-scope-only` (touch only the named prompt row and any test that locks its wording; no validator or builder drift).

### Acceptance criteria

1. The current `draft_job_resume` `user_prompt` in `data/admin/agent_task.json` contains no literal `` `•` ``, `` `-` ``, or `` `*` `` characters used to illustrate list-marker prefixes.
2. The same prompt still instructs Judith that `experience` is a job array and `accomplishments` is an ordered array of plain strings (semantic unchanged from Susan's intent).
3. Existing component tests for draft-hop prompt contract (`TestAst1270…`, `TestAst1349…` Manage Tasks assertions) pass without weakening array-only experience or nested-envelope requirements.
4. A manual or dispatched `draft_job_resume` run still accepts well-formed nested resume JSON (no new validation failures introduced by this wording-only change).

### Open questions

(none)

### Proposed child tickets

**1: draft_job_resume prompt — omit bullet marker glyphs — Katherine** — Reword the current `draft_job_resume` `user_prompt` so accomplishment guidance no longer embeds `` `•`/`-`/`*` `` literals; keep job-array experience rules, nested `resume`/`deviations` example, and trace-to-base-materials discipline unchanged. Add or extend a prompt contract test only if needed to prevent glyph regression.
**Citations:** `astral.seed.archie-catalog-wins`, `astral.standards.in-scope-only`
**Scope:** `data/admin/agent_task.json` — modify current `draft_job_resume` row `user_prompt` only. `tests/component/core/test_candidate.py` — modify only if a new assertion is required.
**Estimate: 1**

### Original brief

Just update the prompt to omit the characters

#### Comments

##### chuckles — 2026-08-24T22:05:55.579Z
AST-1465 REVIEW — Joan: move glyph-regression test assertions to Betty qa-child manifest; engineer Stage 1 limited to agent_task.json.

### Files changed (plan vs actual)

_No direct product commit trail on the parent — the epic worktree carries only a `sync(publish-ref)` housekeeping commit and the epic-registry Threads mirror / archive commits. Implementation landed entirely via the sub-issue below._

## Sub-issues

### AST-1465 — draft_job_resume prompt — omit bullet marker glyphs
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1465/draft-job-resume-prompt-omit-bullet-marker-glyphs-job-resume-draft · Status at archive: Archive · Project: Astral Artifacts · Assignee: katherine · Priority / estimate: None / 1 · Blocked by / blocks / related: parent: AST-1458_

#### What this implements

Reword the current `draft_job_resume` `user_prompt` so accomplishment guidance no longer embeds `` `•`/`-`/`*` `` literals; keep job-array experience rules, nested `resume`/`deviations` example, and trace-to-base-materials discipline unchanged. Add or extend a prompt contract test only if needed to prevent glyph regression.

#### Acceptance criteria

- [X] The current `draft_job_resume` `user_prompt` contains no literal `` `•` ``, `` `-` ``, or `` `*` `` characters used to illustrate list-marker prefixes.
- [X] The same prompt still instructs Judith that `experience` is a job array and `accomplishments` is an ordered array of plain strings.
- [X] Existing component tests for draft-hop prompt contract (`TestAst1270…`, `TestAst1349…`) pass without weakening array-only experience or nested-envelope requirements.
- [X] A manual or dispatched `draft_job_resume` run still accepts well-formed nested resume JSON.

#### Boundaries

Does not change `craft_resume_base`, `finalize_job_resume`, `advise_job_resume`, or `check_job_resume` prompts. No runtime validation, normalize, or builder changes.

#### Notes for planning

Prompt-only seed edit in `data/admin/agent_task.json`. Estimate 1. Glyph-regression test lock is Betty qa-child (engineer `code()` did not touch `tests/**`).

#### UAT fitness (plan doc)

**Correct outcome:** Manage Tasks → `draft_job_resume` user prompt reads cleanly without embedded marker glyphs in the accomplishments clause; Judith still receives the job-array + bare-string accomplishments contract and can return well-formed nested `agent_payload.resume` JSON. **Sibling check:** `craft_resume_base`, `finalize_job_resume`, `advise_job_resume`, `check_job_resume` prompts untouched; existing `TestAst1270NestedDraftJobResumeContract` and `TestAst1349ExperienceArrayContract` assertions for nested envelope, array-only experience, and pin policy remain green. **Not sufficient:** deleting the accomplishments clause or stripping markdown list-bullet rule lines from the prompt body alone is not done — semantic guidance must remain. **Wrong fix rejected:** adding normalize/validate rejection of leading markers in `candidate.py`, or changing builders — out of scope and would not fix the Manage Tasks display issue Susan reported.

#### Explicit scope gate

Ticket Scope names `data/admin/agent_task.json` (current `draft_job_resume` row `user_prompt`) and optionally `tests/component/core/test_candidate.py` when a new assertion is required. Per `astral.git.engineer-test-tree-ban`, engineer `code()` commits touch only `agent_task.json`; glyph-regression assertions (when needed) are Betty's via qa-child/merge-tests — not Stage 1 engineer work.

#### Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `data/admin/agent_task.json` | Reword accomplishments clause on current `draft_job_resume` `user_prompt` | seed | engineer (Stage 1) |
| `tests/component/core/test_candidate.py` | Glyph-regression assertions on draft `user_prompt` | tests | Betty (qa-child) |

#### Stage 1 — Prompt wording

Locate the `task_key == "draft_job_resume"`, `current == 1` row's `user_prompt` Experience bullet (substantively: "`accomplishments` is an ordered **array of strings** — bare text, no `•`/`-`/`*` prefixes"). Replace only the parenthetical accomplishments guidance so it no longer embeds `` `•` ``, `` `-` ``, or `` `*` `` as instructional literals, using a plain-language equivalent (wording is the planner's choice as long as semantics match Susan's intent) — do not edit any other task row, hop metadata field, or other prompt bullet (including the "The rest is bullets:" writing-style prose, which is not marker-prefix illustration). Optional local sanity: re-run the AST-1270/AST-1349 draft prompt contract tests to confirm they still pass without weakening. AC4 is satisfied by boundary declaration (wording-only edit, no validator/builder path changes) rather than a dedicated stage — post-merge manual/dispatch check is Susan/UAT, not a build-child gate.

#### Betty qa-child (glyph lock — not engineer Stage 1)

After Stage 1 lands, Betty's qa-child manifest extends `TestAst1270NestedDraftJobResumeContract.test_manage_tasks_prompt_nested_contract` with assertions that the draft `user_prompt` no longer contains the instructional glyph pattern `` `•`/`-`/`*` `` (or an equivalent concatenation of those three backtick-wrapped glyphs) while still containing `ordered **array of strings**` and `ordered array of job objects` wording — without weakening or removing any existing assertion in that test or in `TestAst1349ExperienceArrayContract.test_tailor_hop_prompts_teach_job_array_and_pin_policy`.

⚠️ **Decision:** assert the specific retired glyph pattern `` `•`/`-`/`*` `` rather than banning every `-` in the prompt — markdown rule bullets legitimately use `- ` and must not break the test.

#### Plan-discuss round=1 — Joan REVISE, then round 2 APPROVED

**fix-now — Stage 1 step 2 / Files Changed row for `tests/component/core/test_candidate.py`.** The initial plan assigned the implementer to add glyph-regression assertions directly under `tests/component/` — a violation of `astral.git.engineer-test-tree-ban` (engineer `code()` commits must not touch `tests/**`; Betty owns the test tree via qa-child/merge-tests, same pattern as AST-996/AST-997/AST-1270). **Recommendation:** restrict Stage 1 engineer work to `data/admin/agent_task.json` only; move the glyph assertions into a qa-child manifest item for Betty; engineer may run the listed component tests locally for sanity only.

**acceptable** — AC4/manual-dispatch verification: no runtime validation path changes, so AC4 is satisfied by boundary declaration rather than a dedicated stage; optional one-line note that post-merge manual/dispatch check is Susan/UAT, not a build gate. **acceptable** — parent statute citation vs matching (seed/tests layers unrecognized by the rubric's layer predicates; plan substance still conforms — durable edit in committed seed JSON, single row, no live-DB-only change).

**Katherine's round=1 reply (Revision 1):** engineer Stage 1 scope narrowed to `data/admin/agent_task.json` only; glyph-regression assertions and the Decision moved to the Betty qa-child section; AC4 noted as Susan/UAT, not a build gate; scope gate updated for the test-tree ban. Round 2: Joan confirmed the fix-now closed and approved — the prior violation was resolved with an explicit Owner-column split matching the AST-996/AST-997/AST-1270 precedent.

#### Radia review — code-rubric.v1, CLEAN

**Findings:** none fix-now, none discuss. **Advisory:** a pre-existing red test (`TestAst1349ExperienceArrayContract::test_uat_fixture_twin_matches_catalog_after_prompt_edits`, a catalog↔UAT-twin drift issue beyond glyph scope) was already failing on tip before this change — not part of the AST-1465 manifest, not blocking. **Plan adherence:** Stage 1 prompt reword + Betty's glyph lock matched the Joan-approved plan exactly; engineer `code()` touched only `data/admin/agent_task.json`; sibling prompts untouched.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `data/admin/agent_task.json` | Reword accomplishments clause, drop instructional `•`/`-`/`*` glyphs | `3f62eca29` — +1/-1 |
| | _tests_ | glyph lock on draft_job_resume prompt (retired glyph pattern absent, semantics preserved) | `e1dc62be3`; bible `docs/test-bible/core/candidate.md` @ `40cbce13c743251d97d4efab2a1f58bc92753351` |
