# AST-1465 — draft_job_resume prompt — omit bullet marker glyphs

**Linear:** [AST-1465](https://linear.app/astralcareermatch/issue/AST-1465/draft-job-resume-prompt-omit-bullet-marker-glyphs)  
**Parent:** [AST-1458](https://linear.app/astralcareermatch/issue/AST-1458/job-resume-draft-prompt-is-asking-for-bullet-chars)  
**Publish ref:** `sub/AST-1458/AST-1465-draft-job-resume-prompt-omit-bullet-marker-glyphs` (origin only)

The current `draft_job_resume` Manage Tasks `user_prompt` embeds literal list-marker glyphs (`•`, `-`, `*`) when instructing Judith that `accomplishments` values must be bare strings in a JSON array. Susan wants those characters removed from the instructional text while preserving the same contract: `experience` is a job array; each job's `accomplishments` is an ordered array of plain strings with no list-marker decoration in the JSON values. This is a prompt-wording-only seed edit — no runtime validation, normalize, or builder changes.

## UAT fitness

- **AC restored:** "The current `draft_job_resume` `user_prompt` in `data/admin/agent_task.json` contains no literal `•`, `-`, or `*` characters used to illustrate list-marker prefixes." and "The same prompt still instructs Judith that `experience` is a job array and `accomplishments` is an ordered array of plain strings (semantic unchanged from Susan's intent)."
- **Correct outcome:** Manage Tasks → `draft_job_resume` user prompt reads cleanly without embedded marker glyphs in the accomplishments clause; Judith still receives the job-array + bare-string accomplishments contract and can return well-formed nested `agent_payload.resume` JSON.
- **Sibling check:** `craft_resume_base`, `finalize_job_resume`, `advise_job_resume`, and `check_job_resume` prompts untouched; existing `TestAst1270NestedDraftJobResumeContract` and `TestAst1349ExperienceArrayContract` assertions for nested envelope, array-only experience, and pin policy remain green (engineer does not weaken them; Betty extends for glyph lock).
- **Not sufficient:** Deleting the accomplishments clause or stripping markdown list bullets (`- ` rule lines) from the prompt body alone is **not** done — semantic guidance must remain.
- **Wrong fix rejected:** Adding normalize/validate rejection of leading markers in `candidate.py` or changing builders is out of scope (Boundaries) and would not fix the Manage Tasks display issue Susan reported.

## Explicit scope gate

Ticket **Scope** names `data/admin/agent_task.json` (current `draft_job_resume` row `user_prompt`) and optionally `tests/component/core/test_candidate.py` when a new assertion is required. Per `astral.git.engineer-test-tree-ban`, **engineer `code()` commits touch only** `data/admin/agent_task.json`. Glyph-regression assertions (when needed) are Betty's via **qa-child** / merge-tests — not Stage 1 engineer work.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `data/admin/agent_task.json` | Reword accomplishments clause on current `draft_job_resume` `user_prompt` | seed | engineer (Stage 1) |
| `tests/component/core/test_candidate.py` | Glyph-regression assertions on draft `user_prompt` (retired `` `•`/`-`/`*` `` pattern + preserved bare-string / job-array wording) | tests | Betty (qa-child) |

## Stage 1: Prompt wording (engineer)

**Done when:** Current `draft_job_resume` `user_prompt` omits instructional marker glyphs; wording still teaches job-array `experience` and bare-string `accomplishments`; no other task rows or hop metadata changed. Engineer `code()` commit contains **only** `data/admin/agent_task.json`.

1. In `data/admin/agent_task.json`, locate the row where `task_key` is `draft_job_resume` and `current` is `1`. In `user_prompt`, find the Experience bullet that currently reads (substance, not necessarily exact whitespace):

   ```
   - `experience` is an ordered array of job objects: `company`, `title`, `dates`, `location`, `accomplishments` (`accomplishments` is an ordered **array of strings** — bare text, no `•`/`-`/`*` prefixes).
   ```

   Replace only the parenthetical accomplishments guidance so it no longer embeds `` `•` ``, `` `-` ``, or `` `*` `` as instructional literals. Use plain-language equivalent, e.g. bare strings with no list-marker prefixes (wording is planner's choice as long as semantics match Susan's intent).

   **Do not** edit any other task row, hop metadata fields on this row, or other bullets in the prompt (including "The rest is bullets:" prose — that is writing-style guidance, not marker-prefix illustration).

2. Optional local sanity (no commit of test changes): run existing draft prompt contract tests; they must still pass without weakening:

   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_candidate.py::TestAst1270NestedDraftJobResumeContract::test_manage_tasks_prompt_nested_contract \
     tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_tailor_hop_prompts_teach_job_array_and_pin_policy
   ```

**AC4 note:** Post-merge manual or dispatched `draft_job_resume` check is Susan/UAT, not a build-child gate — wording-only seed edit; no validator/builder path changes.

## Betty qa-child (glyph lock — not engineer Stage 1)

After engineer Stage 1 lands, Betty's **qa-child** manifest must include extending `TestAst1270NestedDraftJobResumeContract.test_manage_tasks_prompt_nested_contract` (preferred — already loads draft `user_prompt`) with assertions that:

- The draft `user_prompt` does **not** contain the instructional glyph pattern `` `•`/`-`/`*` `` (or equivalent concatenation of those three backtick-wrapped glyphs).
- The draft `user_prompt` still contains `ordered **array of strings**` (or equivalent bare-string array wording) and `ordered array of job objects` so accomplishments semantics are preserved.

Do **not** weaken or remove existing assertions in `TestAst1270NestedDraftJobResumeContract` or `TestAst1349ExperienceArrayContract.test_tailor_hop_prompts_teach_job_array_and_pin_policy`.

⚠️ **Decision:** Assert the specific retired glyph pattern `` `•`/`-`/`*` `` rather than banning every `-` in the prompt — markdown rule bullets legitimately use `- ` and must not break the test. Betty owns the test-tree commit; engineer never commits under `tests/**`.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Revisions

Revision 1 — 2026-08-24  
Driven by: Chuckles / Joan REVIEW — "move glyph-regression test assertions to Betty qa-child manifest; engineer Stage 1 limited to agent_task.json" (`astral.git.engineer-test-tree-ban`).  
Changes: Files Changed / Stage 1 engineer scope = `data/admin/agent_task.json` only; glyph assertions + Decision moved to **Betty qa-child** section; AC4 noted as Susan/UAT not build gate; scope gate updated for test-tree ban.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1465
**Overall:** REVISE
**Publish ref:** `origin/sub/AST-1458/AST-1465-draft-job-resume-prompt-omit-bullet-marker-glyphs` @ `4b0662d6f7fecb5efed283cc33f3d9090ee48742`

### Traceability
AC1–AC2→Stage 1 §1 (reword `draft_job_resume` accomplishments clause); AC3→Stage 1 §§2–3 (extend contract test + run AST-1270/AST-1349); AC4→Stage 1 wording-only boundary (no validator/builder edits; manual/dispatch smoke implicit).

### Findings

#### fix-now — Stage 1 step 2 / Files Changed `tests/component/core/test_candidate.py`
**Location:** Stage 1 step 2; Files Changed row for `tests/component/core/test_candidate.py`
**Finding:** Plan assigns the implementer to add glyph-regression assertions under `tests/component/`. `astral.git.engineer-test-tree-ban` is in scope (plan path `tests/**`, change type `modify`; `layers: []` passes). Engineer `code()` commits must not touch `tests/**`; Betty owns the test tree via `qa-child` / `merge-tests` (same pattern as AST-996, AST-997, AST-1270 Joan/Radia notes: engineer `code()` has no `tests/`).
**Recommendation:** Restrict Stage 1 engineer work to `data/admin/agent_task.json` only. Move the `TestAst1270NestedDraftJobResumeContract` glyph assertions (retired `` `•`/`-`/`*` `` pattern + preserved `ordered **array of strings**` / `ordered array of job objects` wording) into a **qa-child manifest** item for Betty. Engineer may run the listed component tests locally for sanity; Betty lands and commits test changes.

#### acceptable — AC4 / manual dispatch verification
**Location:** Parent AC4; plan has no explicit smoke step
**Finding:** No runtime validation path changes; wording-only seed edit. AC4 is satisfied by boundary declaration, not a dedicated stage.
**Recommendation:** Optional one-line note in plan that post-merge manual/dispatch check is Susan/UAT, not a build gate. Not blocking.

#### acceptable — Parent statute citation vs matching
**Location:** Child cites `astral.seed.archie-catalog-wins` + `astral.standards.in-scope-only`; parent also cites `astral.seed.agent-tables-in-repo-json`
**Finding:** Plan layers map to `docs` per rubric (`seed` / `tests` unrecognized); scoped seed/`src/**` statutes exclude on layer/path predicates. Plan substance still conforms: durable edit in committed `data/admin/agent_task.json`, single row, no live-DB-only change.
**Recommendation:** None required for approval once test ownership is fixed.

**Considered (in-session):** 18 universal orchestration statutes → all `conforms`. Scoped in-scope: `astral.git.engineer-test-tree-ban` → `violates` (above). Remaining scoped active statutes excluded (layer/path/change_type predicates).

## Joan validate (round 2)

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1465
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1458/AST-1465-draft-job-resume-prompt-omit-bullet-marker-glyphs` @ `873cd34566c726062ab7b6828cae7b0f094077d1`

### Traceability
AC1–AC2→Stage 1 §1 (reword accomplishments clause, preserve job-array + bare-string semantics); AC3→Betty qa-child glyph lock + Stage 1 optional sanity run of AST-1270/AST-1349 (no weakening); AC4→Stage 1 AC4 note (Susan/UAT; no validator/builder edits).

### Findings

#### acceptable — Plan Discuss round 1 closed
**Location:** `[plan-discuss] round=1 reply` @ `873cd345`; plan `## Revisions` / Explicit scope gate / Files Changed Owner column
**Finding:** Prior `astral.git.engineer-test-tree-ban` violation is resolved. Engineer Stage 1 is `data/admin/agent_task.json` only; glyph-regression assertions moved to Betty **qa-child** with explicit Owner split — matches AST-996/AST-997/AST-1270 pattern (Betty owns `tests/**` commits).
**Recommendation:** None.

#### acceptable — AC4 manual/dispatch smoke
**Location:** Stage 1 AC4 note
**Finding:** Wording-only seed edit; no runtime path changes. Explicit UAT boundary is sufficient.
**Recommendation:** None.

**Considered (in-session):** 18 universal orchestration statutes → all `conforms`. Scoped in-scope: `astral.git.engineer-test-tree-ban` → `conforms` (engineer `code()` excludes `tests/**`; Betty qa-child owns glyph lock). Remaining scoped active statutes excluded on layer/path/change_type predicates.
