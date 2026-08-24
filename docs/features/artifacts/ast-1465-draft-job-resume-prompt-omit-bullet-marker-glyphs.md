# AST-1465 — draft_job_resume prompt — omit bullet marker glyphs

**Linear:** [AST-1465](https://linear.app/astralcareermatch/issue/AST-1465/draft-job-resume-prompt-omit-bullet-marker-glyphs)  
**Parent:** [AST-1458](https://linear.app/astralcareermatch/issue/AST-1458/job-resume-draft-prompt-is-asking-for-bullet-chars)  
**Publish ref:** `sub/AST-1458/AST-1465-draft-job-resume-prompt-omit-bullet-marker-glyphs` (origin only)

The current `draft_job_resume` Manage Tasks `user_prompt` embeds literal list-marker glyphs (`•`, `-`, `*`) when instructing Judith that `accomplishments` values must be bare strings in a JSON array. Susan wants those characters removed from the instructional text while preserving the same contract: `experience` is a job array; each job's `accomplishments` is an ordered array of plain strings with no list-marker decoration in the JSON values. This is a prompt-wording-only seed edit — no runtime validation, normalize, or builder changes.

## UAT fitness

- **AC restored:** "The current `draft_job_resume` `user_prompt` in `data/admin/agent_task.json` contains no literal `•`, `-`, or `*` characters used to illustrate list-marker prefixes." and "The same prompt still instructs Judith that `experience` is a job array and `accomplishments` is an ordered array of plain strings (semantic unchanged from Susan's intent)."
- **Correct outcome:** Manage Tasks → `draft_job_resume` user prompt reads cleanly without embedded marker glyphs in the accomplishments clause; Judith still receives the job-array + bare-string accomplishments contract and can return well-formed nested `agent_payload.resume` JSON.
- **Sibling check:** `craft_resume_base`, `finalize_job_resume`, `advise_job_resume`, and `check_job_resume` prompts untouched; `TestAst1270NestedDraftJobResumeContract` and `TestAst1349ExperienceArrayContract` assertions for nested envelope, array-only experience, and pin policy remain green.
- **Not sufficient:** Deleting the accomplishments clause or stripping markdown list bullets (`- ` rule lines) from the prompt body alone is **not** done — semantic guidance must remain.
- **Wrong fix rejected:** Adding normalize/validate rejection of leading markers in `candidate.py` or changing builders is out of scope (Boundaries) and would not fix the Manage Tasks display issue Susan reported.

## Explicit scope gate

Ticket **Scope** names only `data/admin/agent_task.json` (current `draft_job_resume` row `user_prompt`) and `tests/component/core/test_candidate.py` (only if a new assertion is required). All planned file touches match.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Reword accomplishments clause on current `draft_job_resume` `user_prompt` | seed |
| `tests/component/core/test_candidate.py` | Add glyph-regression assertion to existing draft prompt contract test | tests |

## Stage 1: Prompt wording + contract test

**Done when:** Current `draft_job_resume` `user_prompt` omits instructional marker glyphs; existing AST-1270/AST-1349 prompt contract tests pass plus a new assertion locks the regression; component tests for the touched file pass.

1. In `data/admin/agent_task.json`, locate the row where `task_key` is `draft_job_resume` and `current` is `1`. In `user_prompt`, find the Experience bullet that currently reads (substance, not necessarily exact whitespace):

   ```
   - `experience` is an ordered array of job objects: `company`, `title`, `dates`, `location`, `accomplishments` (`accomplishments` is an ordered **array of strings** — bare text, no `•`/`-`/`*` prefixes).
   ```

   Replace only the parenthetical accomplishments guidance so it no longer embeds `` `•` ``, `` `-` ``, or `` `*` `` as instructional literals. Use plain-language equivalent, e.g. bare strings with no list-marker prefixes (wording is planner's choice as long as semantics match Susan's intent).

   **Do not** edit any other task row, hop metadata fields on this row, or other bullets in the prompt (including "The rest is bullets:" prose — that is writing-style guidance, not marker-prefix illustration).

2. In `tests/component/core/test_candidate.py`, extend `TestAst1270NestedDraftJobResumeContract.test_manage_tasks_prompt_nested_contract` (preferred — already loads draft `user_prompt` and asserts nested envelope + array contract) with assertions that:
   - The draft `user_prompt` does **not** contain the instructional glyph pattern `` `•`/`-`/`*` `` (or equivalent concatenation of those three backtick-wrapped glyphs).
   - The draft `user_prompt` still contains `ordered **array of strings**` (or equivalent bare-string array wording) and `ordered array of job objects` so accomplishments semantics are preserved.

   Do **not** weaken or remove existing assertions in `TestAst1270NestedDraftJobResumeContract` or `TestAst1349ExperienceArrayContract.test_tailor_hop_prompts_teach_job_array_and_pin_policy`.

3. Run component tests for the touched areas:

   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_candidate.py::TestAst1270NestedDraftJobResumeContract::test_manage_tasks_prompt_nested_contract \
     tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract::test_tailor_hop_prompts_teach_job_array_and_pin_policy
   ```

   All must pass before stage commit.

⚠️ **Decision:** Assert the specific retired glyph pattern `` `•`/`-`/`*` `` rather than banning every `-` in the prompt — markdown rule bullets legitimately use `- ` and must not break the test.

## Estimate

Confirm Chuckles estimate: 1 — agree
