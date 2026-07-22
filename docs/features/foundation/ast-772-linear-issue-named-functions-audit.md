# AST-772 — Linear Issue Named Functions Audit

<!-- linear-archive: AST-772 archived 2026-07-22 -->

## Linear archive (AST-772)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-772/linear-issue-named-functions-audit  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-883

### Description

## Purpose

Linear issue ids in product symbol names (`_apply_ast738_…`, `_AST561_…`) encode ticket archaeology into runtime code — they age poorly, confuse reviewers, and violate Susan's hard rule surfaced during [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) review. This epic delivers a complete `src/` **inventory** (Discussion artifact), a keep / rename / remove decision per row, codifies the rule in `ASTRAL_CODE_RULES` so Radia can treat new violations as fix-now, and dispatches scoped child tickets only for approved renames and hot-path removals. Devs do **not** re-run the audit.

## Functional scope

* **Discussion-phase audit (this ticket):** Chuckles surveys all Python under `src/` for functions, helpers, classes, and module-level constants whose **names** embed a Linear-style issue id (`ast` + digits, `AST` + digits, or `_apply_astNNN` migration naming). Names containing `astral` (domain identifiers) are excluded.
* **Per-case disposition:** Each finding gets a Chuckles recommendation and a blank **Susan decision** field for Discussion review.
* **Policy codification:** After Susan approves, one child adds an explicit naming rule to `ASTRAL_CODE_RULES` (review fix-now for new `src/` symbols referencing AST-NNN).
* **Post-approval action items:** After Susan moves this parent to Todo, `dispatch-parent` creates one child per approved rename or hot-path removal — not a monolithic "fix all names" child. Renames should use **domain-descriptive** names (what the migration does, not which ticket shipped it).
* **Inventory (**`src/` **— March 2026 survey; all findings in** `database.py`**):**

| # | Location | Symbol | Kind | What it does | Chuckles recommendation | Susan decision |
| -- | -- | -- | -- | -- | -- | -- |
| 1 | `database.py` | `_AST561_TAKE_JD_PROMPT_LINE` | const | Prompt fragment for `take_jd` section in analysis upshot | **Rename** — domain name (e.g. `_ANALYSIS_UPSHOT_TAKE_JD_PROMPT_LINE`); drop ticket id |  |
| 2 | `database.py` | `_AST561_ANALYSIS_UPSHOT_USER_PROMPT_SEED` | const | Full Estelle user prompt body seeded when analysis upshot row has empty prompts | **Rename** + align with [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) row 5 (**Remove** auto prompt body) |  |
| 3 | `database.py` | `_patch_ast561_take_jd_into_prompt` | helper | Inserts `take_jd` prompt block into existing prompt text | **Rename** — e.g. `_patch_analysis_upshot_take_jd_into_prompt` |  |
| 4 | `database.py` | `_AST723_RUBRIC_VECTORS_MARKER` | const | HTML comment marker string (`AST-723_RUBRIC_VECTORS_TOKEN`) | **Rename** — domain marker constant; remove `AST-723` from string value |  |
| 5 | `database.py` | `_AST723_RUBRIC_TOKEN_REPLACEMENTS` | const | Tuple of legacy rubric token → `{$RUBRIC_VECTORS}` replacements | **Rename** — e.g. `_RUBRIC_VECTORS_TOKEN_REPLACEMENTS` |  |
| 6 | `database.py` | `_ast723_rubric_token_migration_applied` | module flag | Once-per-process guard for rubric token migration | **Rename** — e.g. `_rubric_vectors_token_migration_applied` |  |
| 7 | `database.py` | `_patch_ast723_rubric_tokens` | helper | Applies token replacements on prompt text | **Rename** — e.g. `_patch_rubric_vectors_tokens` |  |
| 8 | `database.py` | `_apply_ast723_rubric_vectors_token_migration` | migration | One-time UPDATE on current `agent_task` rows for rubric tokens | **Rename** + **Relocate** per [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) row 6 — script under `scripts/migrations/`, drop from schema-ensure hot path |  |
| 9 | `database.py` | `_apply_ast561_analysis_upshot_take_jd_migration` | migration | Seeds/patches analysis upshot prompts including `take_jd` | **Rename** + **Remove/relocate** per [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) row 5 |  |
| 10 | `database.py` | `_apply_ast469_select_job_page_run_next_migration` | migration | Sets `run_next = parse_job_list` on `select_job_page` when blank | **Rename** + **Relocate** per [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) row 7 |  |
| 11 | `database.py` | `_apply_ast738_task_grouping_metadata_seed` | seed/migration | Backfills `task_group_*` from `TASK_CONFIG` when grouping columns empty | **Rename** + **Remove** from hot path per [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) row 3 — Susan's explicit call-out for this symbol |  |

* **Zero other hits** in `src/core/`, `src/external/`, `src/utils/`, or `src/ui/` on current `dev`.
* **Adjacent (out of inventory, noted for awareness):** `scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py` (`AST438_TASK_KEYS`); test-tree names (`test_ast561_*`, `_SKIP_AST552_*`, etc.) — not `src/` product code.

## Boundaries

* Does **not** ask a dev agent to re-audit — inventory above is the Discussion artifact.
* Does **not** change runtime behavior until Susan approves per-row dispositions and children ship.
* Scope is `src/` **product Python only** — not test fixtures, not committed spike scripts under `scripts/spikes/`, not docs or plan filenames (`ast-NNN-slug` in `docs/features/` remains the traceability path per Code Rules).
* Does **not** flag domain identifiers (`astral_job_id`, `_ensure_jobs_astral_ids`, etc.) or arbitrary digit sequences unrelated to Linear ids.
* Must **not** break [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) / [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) seeding strategy — coordinate child renames/removals with those siblings so one migration path wins.

## Acceptance criteria

* Every row in the inventory table has a filled **Susan decision** (rename / remove / relocate / defer) before dispatch.
* Susan has reviewed Chuckles recommendations and confirmed or overridden each row.
* Approved renames and hot-path removals become scoped child tickets at dispatch — no child titled "run the AST-name audit."
* `ASTRAL_CODE_RULES` explicitly forbids Linear issue ids in `src/` symbol names; Radia treats new violations as fix-now.
* After children ship, `src/` contains **zero** symbols whose names embed `ast`/`AST` + ticket digits (verified by grep or test-bible check in review).
* Existing [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) relocation/removal decisions remain satisfied — no renamed symbol reintroduces removed auto-seed behavior.

## Dependencies and blockers

* [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit) — sibling; rows 3, 5–7, 9–11 overlap the same `database.py` migrations/seeds. Dispatch order should avoid conflicting edits on the same hot-path hooks.
* [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) — repo JSON upsert may subsume several migrations currently named after tickets; coordinate rename + relocate children with [AST-756](https://linear.app/astralcareermatch/issue/AST-756/create-repo-json-files-for-agent-and-agent-task) landing.
* none blocking Discussion completion.

## Open questions

(none)

---

## Original brief

AAAAAAAAAACK!!! NEVER CREATE FUNCTIONS REFERENCING THE AST ISSUE IDS IN THE SRC CODE OMG!!!

Do a complete audit of the whole src codebase and provide an inventory of any functions (helper or otherwise) where "AST" or three numbers (e.g. the issue id) are found in the function name.

Create a table much like you did in [AST-771](https://linear.app/astralcareermatch/issue/AST-771/seed-audit).

Lest I forget, this is an ABSOLUTE DEALBREAKER for code reviews. NEVER let this happen.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
