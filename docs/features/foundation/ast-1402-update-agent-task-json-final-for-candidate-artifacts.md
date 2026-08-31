# AST-1402 — Update agent_task json (final for candidate artifacts)

<!-- linear-archive: AST-1402 archived 2026-08-31 -->

## Linear archive (AST-1402)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1402/update-agent-task-json-final-for-candidate-artifacts  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. Re-fetch agent_task.txt from the Original brief URL with Linear auth (`Authorization: $LINEAR_KEY_CHUCKLES`, not Bearer). It is a 55-row current=1 export (same columns as catalog). Do not paste it over the file.
2. Surgical replace in `data/admin/agent_task.json` on `$ASTRAL_MAIN` (`dev`). Catalog stays **52** rows, existing array order, existing key order, trailing newline. Do not `ensure_ascii`-rewrite untouched prompts.
3. Leave 42 identical keys. Do **not** add the three attachment-only stubs (`bootstrap_candidate_context`, `meteorite_email`, `propose_application_responses`) — blank (unassigned) / ZZZ / task_seq 999, same skip as [AST-1399](https://linear.app/astralcareermatch/issue/AST-1399/sync-repo-seed-agentjson-and-agent-taskjson-update-agentjson-and-agent).
4. Replace the **10** Candidate Artifacts objects that differ with the matching attachment objects (verbatim, including new task_key_uuid / updated_at / prompts). `craft_do_rubric` / `craft_like_rubric` prompt bodies and uuids stay [AST-1399](https://linear.app/astralcareermatch/issue/AST-1399/sync-repo-seed-agentjson-and-agent-taskjson-update-agentjson-and-agent) (`0e38db78-…` / `d1329798-…`); only task_seq + updated_at change on those two.

   Manage Tasks order (task_seq → task_key → run_next):

   ```
   0     craft_resume_base                 (empty)
   0.1   simple_resume_parse               (empty)
   1     craft_get_rubric                  craft_do_rubric
   2     craft_do_rubric                   craft_like_rubric
   3     craft_like_rubric                 craft_evaluate_meteorite_rubric
   4     craft_evaluate_meteorite_rubric   craft_jobdesc_rubric
   5     craft_jobdesc_rubric              craft_prefilter_rubric
   6     craft_prefilter_rubric            craft_company_search_terms
   7     craft_company_search_terms        craft_joblist_rubric
   15    craft_joblist_rubric              (empty)
   ```

   REQUESTED_ARTIFACTS walk from craft_get_rubric becomes get → do → like → evaluate_meteorite → jobdesc → prefilter → company_search_terms → joblist (end). Today joblist sits before prefilter and company_search is terminal.

   Prompt/cache + uuid rewrite (copy attachment, do not paraphrase): `craft_joblist_rubric` (user_prompt 9223→16536, cache_prompt restyled, cache_prompt_b cleared), `craft_jobdesc_rubric` (cache_prompt_b → `{$CALLER_CACHE_B}`), `craft_prefilter_rubric` / `craft_company_search_terms` (cache_prompt_b section labels). Leave craft_joblist_rubric at seq **15** — do not renumber to 8.
5. `cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json` and `cmp -s` (fixture is a byte-twin today). No `src/`. No `agent.json`.
6. Commit on `dev` (Task — no ftr/sub). Compile/lint before commit. Push `origin/dev` so Railway seed upsert loads the chain.

## Done when

* Catalog still has 52 current rows; the three stubs are absent.
* The 10 Candidate Artifacts rows match the attachment objects.
* `expected-agent_task.json` is byte-identical to catalog.
* [AST-1400](https://linear.app/astralcareermatch/issue/AST-1400/gap-estellecraft-seed-asserts-repo-admin-json-bibletests) Do/Like uuid + prompt-length pins still hold.
* After restart, `apply_repo_admin_json_at_startup` loads this chain (`_apply_ast1113_craft_run_next_chain_migration` is already a no-op).

## Risks / open questions

* **Stubs:** attachment is 55 rows. Plan keeps 52. Say so if those three keys should be added.  
  * Add them.  no harm, and they might be needed for ui purposes.
* **task_seq 0.1** on simple_resume_parse is legal (task_seq REAL). Leaving it.
* Tests that pin old Candidate Artifacts run_next / uuids (if any beyond [AST-1400](https://linear.app/astralcareermatch/issue/AST-1400/gap-estellecraft-seed-asserts-repo-admin-json-bibletests)) live in the test tree — Chuckles will not edit `tests/`. Flag if something goes red.
  * Confirm if any such tests exist and remove them.  There should not be a test codifying daisy chain sequences.

---

## Original brief

Please update the agent_task.json file with the attached content:

[agent_task.txt](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/b706e20a-fe37-4886-b996-0aa6b8be785f/4374011d-0c3d-4a53-a701-5644cbed08c0)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
