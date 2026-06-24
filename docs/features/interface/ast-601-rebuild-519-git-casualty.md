# AST-601 — Rebuild 519 (git casualty)

<!-- linear-archive: AST-601 archived 2026-06-23 -->

## Linear archive (AST-601)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-601/rebuild-519-git-casualty  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

[AST-519](https://linear.app/astralcareermatch/issue/AST-519) shipped per-candidate **Base Resume Content**: tabs driven by each candidate's enabled `resume_structure` sections (not the global template), a candidate API to read that catalog, and save paths that strip orphan keys from `artifacts.base_resume`. That work passed review and landed under parent [AST-477](https://linear.app/astralcareermatch/issue/AST-477), but later git merges reverted key product behavior on **origin/dev** — notably the **Base Resume Content** page still reads global shapes and legacy accent on `base_resume`, while sibling features (e.g. job report structure tabs) expect the restored API. This ticket recreates AST-519 capability on **origin/dev** so admins edit base resume content per candidate catalog without orphan tabs or cross-candidate bleed. Same rebuild pattern as [AST-599](https://linear.app/astralcareermatch/issue/AST-599) and [AST-600](https://linear.app/astralcareermatch/issue/AST-600).

## Functional scope

* Expose each candidate's resolved resume section catalog through the candidate admin API: enabled sections in catalog order, plus accent color from structure (not from global shapes).
* **Base Resume Content** shows one tab per **enabled** section for the selected candidate, in defined order; tab labels come from that candidate's structure titles.
* Editor loads and saves `artifacts.base_resume` string content keyed by section ids; keys not in the candidate's structure are not shown and are not persisted (orphan keys dropped on save — self-heal, not hard error).
* Accent color picker reads and writes `artifacts.resume_structure.accent_color` (not `artifacts.base_resume.accent_color`).
* Switching candidates reloads tabs independently — candidate B's catalog does not affect candidate A's editor.
* When job-level `resume_content` exists elsewhere in the product, its keys remain a subset of the same section ids; this ticket owns the **Base Resume Content** admin UI and candidate API portion only (builder/job artifact filtering stays with [AST-518](https://linear.app/astralcareermatch/issue/AST-518)).

## Boundaries

* Does **not** implement structure persistence or `craft_resume_base` schema changes — [AST-517](https://linear.app/astralcareermatch/issue/AST-517) (Done; must remain on dev).
* Does **not** own resume builder HTML merge or job artifact key filtering — [AST-518](https://linear.app/astralcareermatch/issue/AST-518).
* Does **not** implement job-scoped resume draft tabs in Job Analysis Report — [AST-553](https://linear.app/astralcareermatch/issue/AST-553) lineage (may consume the restored GET catalog endpoint but is out of scope here).
* Does **not** change global `DATA_SHAPES` templates except as legacy read shims already owned by AST-517.
* Does **not** reopen [AST-477](https://linear.app/astralcareermatch/issue/AST-477) parent scope — only restores AST-519 admin/API/UI behavior lost in merge.

## Acceptance criteria

1. Authenticated `GET` for a candidate's resume structure returns enabled sections in catalog order with labels and accent color (or null when absent).
2. **Base Resume Content** shows one tab per enabled section for the selected candidate, in defined order — not tabs from the global template alone.
3. Saving base resume content persists only keys allowed by that candidate's structure; orphan keys in the request body are dropped before merge.
4. Accent picker reads initial value from structure and saves to `artifacts.resume_structure.accent_color`.
5. A second candidate with a different section catalog shows different tabs; switching between candidates does not leak one catalog into the other.
6. No orphan section keys appear as editor tabs when structure and stored content disagree.
7. Component tests covering the AST-519 API and Base Resume Content UI contract pass on the merged branch.
8. Change lands on **origin/dev** via normal team git workflow.

## Dependencies and blockers

* **Reference spec:** [AST-519](https://linear.app/astralcareermatch/issue/AST-519) (Done — behavior to recreate).
* **Planning artifact:** `docs/features/candidate/ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md` (approved plan from original ship; dev agent may use as **plan-child** starting point).
* **Prerequisite on dev:** [AST-517](https://linear.app/astralcareermatch/issue/AST-517) per-candidate `artifacts.resume_structure` storage and `resolve_resume_structure()` (Done — verify present before implementation).
* None blocking start if AST-517 remains on dev.

## Open questions

None.

### Comments

#### chuckles — 2026-06-14T23:15:14.328Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-650** | craft_resume_base Generate succeeds but does not persist base_resume |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-14T23:11:10.811Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-601 (parent) | ftr/AST-601-rebuild-519-git-casualty |
| AST-616 | sub/AST-601/AST-616-base-resume-content-ui-rebuild-519 |
| AST-644 | sub/AST-601/AST-644-craft-resume-base-missing-structure |
| AST-650 | sub/AST-601/AST-650-craft-resume-base-generate-no-persist |

**Epic worktree:** `astral-AST-601/` — one active sub checked out at a time.

— Chuckles

#### chuckles — 2026-06-14T23:10:58.801Z
**Git (AST-650):** `origin/sub/AST-601/AST-650-craft-resume-base-generate-no-persist` seeded from `origin/ftr/AST-601-rebuild-519-git-casualty`.

— Chuckles

#### susan — 2026-06-14T23:09:20.308Z
Okay, it didn't fail this time, but it also didn't actually save to the candidate's base resume.

```
[
  {
    "agent_responses": "[{\"batch_id\": \"intake-intake_initiate_candidate-2b692c0d-f37c-4aca-98e4-0e983f111c53\", \"task_key\": \"intake_initiate_candidate\", \"created_at\": \"2026-06-09 00:18:14\", \"entity_cost\": 0.0006591, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_initiate_candidate-2b692c0d-f37c-4aca-98e4-0e983f111c53-system-a36231bceace4f5c\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_initiate_candidate-2b692c0d-f37c-4aca-98e4-0e983f111c53-no_cache-a7e59757b5f7dd05\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_initiate_candidate-2b692c0d-f37c-4aca-98e4-0e983f111c53-task-cd8521b44608a284\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_initiate_candidate-2b692c0d-f37c-4aca-98e4-0e983f111c53-response-57af5159ac3be074\"}]}, {\"batch_id\": \"intake-intake_candidate_response-c8c35559-fedf-4c4b-b457-70229893e2df\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 00:18:38\", \"entity_cost\": 0.0005599, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-c8c35559-fedf-4c4b-b457-70229893e2df-system-89e126971a1223e2\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-c8c35559-fedf-4c4b-b457-70229893e2df-no_cache-ea90fa82949228f8\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-c8c35559-fedf-4c4b-b457-70229893e2df-no_cache-bb459e4658024805\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-c8c35559-fedf-4c4b-b457-70229893e2df-task-2bed1f99579ddbdd\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-c8c35559-fedf-4c4b-b457-70229893e2df-response-5e5792a3a43d0528\"}]}, {\"batch_id\": \"intake-intake_candidate_response-5f8e8ba9-106c-401c-8553-d045a4d8d565\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 00:24:03\", \"entity_cost\": 0.0007746, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-5f8e8ba9-106c-401c-8553-d045a4d8d565-system-2a60c2208d70f11c\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-5f8e8ba9-106c-401c-8553-d045a4d8d565-no_cache-d4b6506086a55b71\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-5f8e8ba9-106c-401c-8553-d045a4d8d565-no_cache-ee8d4b732673b5a5\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-5f8e8ba9-106c-401c-8553-d045a4d8d565-task-a63cfb775e0db8c3\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-5f8e8ba9-106c-401c-8553-d045a4d8d565-response-fdafb04a691fde52\"}]}, {\"batch_id\": \"intake-intake_candidate_response-a1dc1119-a834-4237-95da-ee7f31bf2169\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 00:30:46\", \"entity_cost\": 0.0002085, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-a1dc1119-a834-4237-95da-ee7f31bf2169-system-ce69f6e38a4aabae\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-a1dc1119-a834-4237-95da-ee7f31bf2169-no_cache-56b7dc1bb4c783b3\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-a1dc1119-a834-4237-95da-ee7f31bf2169-no_cache-02542973f84328c2\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-a1dc1119-a834-4237-95da-ee7f31bf2169-task-0dcc9e2d8754013d\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-a1dc1119-a834-4237-95da-ee7f31bf2169-response-60d6f9ff43aad78e\"}]}, {\"batch_id\": \"intake-intake_candidate_response-b7d4f50e-c3f9-4b6e-97b7-25ff3473dd3a\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 00:36:56\", \"entity_cost\": 0.0002545, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-b7d4f50e-c3f9-4b6e-97b7-25ff3473dd3a-system-f0445fa52ffc3f9d\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-b7d4f50e-c3f9-4b6e-97b7-25ff3473dd3a-no_cache-ef6554cf7ff62201\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-b7d4f50e-c3f9-4b6e-97b7-25ff3473dd3a-no_cache-d21f401672e64bd4\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-b7d4f50e-c3f9-4b6e-97b7-25ff3473dd3a-task-1ece9f23ca1e1dcd\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-b7d4f50e-c3f9-4b6e-97b7-25ff3473dd3a-response-375ee48a6fe8c097\"}]}, {\"batch_id\": \"intake-intake_candidate_response-8892e3a9-89c8-4ca0-a9b1-0c41259b6bd9\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 00:46:42\", \"entity_cost\": 0.00036, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-8892e3a9-89c8-4ca0-a9b1-0c41259b6bd9-system-81a786a5577ee6a1\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-8892e3a9-89c8-4ca0-a9b1-0c41259b6bd9-no_cache-a6cc66a34dc1fcda\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-8892e3a9-89c8-4ca0-a9b1-0c41259b6bd9-no_cache-22ab4f68e8ac84f4\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-8892e3a9-89c8-4ca0-a9b1-0c41259b6bd9-task-756537ef9b6ad6ce\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-8892e3a9-89c8-4ca0-a9b1-0c41259b6bd9-response-c8be594263b7ce3f\"}]}, {\"batch_id\": \"intake-intake_candidate_response-3530531d-f733-422b-af35-fd88f4ecc9d2\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 00:52:36\", \"entity_cost\": 0.0003359, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-3530531d-f733-422b-af35-fd88f4ecc9d2-system-84a8bc6283791425\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-3530531d-f733-422b-af35-fd88f4ecc9d2-no_cache-3decfca67d3559e5\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-3530531d-f733-422b-af35-fd88f4ecc9d2-no_cache-815d35d53891e55d\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-3530531d-f733-422b-af35-fd88f4ecc9d2-task-988b87813782ddc7\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-3530531d-f733-422b-af35-fd88f4ecc9d2-response-dc23363b11e41600\"}]}, {\"batch_id\": \"intake-intake_candidate_response-674de279-dfd3-4293-9e14-01d936dce753\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 00:56:58\", \"entity_cost\": 0.0004824, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-674de279-dfd3-4293-9e14-01d936dce753-system-9f564245f26c8fe1\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-674de279-dfd3-4293-9e14-01d936dce753-no_cache-4695748bd558cc32\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-674de279-dfd3-4293-9e14-01d936dce753-no_cache-be74870534a464c1\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-674de279-dfd3-4293-9e14-01d936dce753-task-60289b7e3a4093f7\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-674de279-dfd3-4293-9e14-01d936dce753-response-489ad4240c07985e\"}]}, {\"batch_id\": \"intake-intake_candidate_response-bde3f385-cb94-440d-9ba7-f20cd45c9e66\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:01:16\", \"entity_cost\": 0.000481, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-bde3f385-cb94-440d-9ba7-f20cd45c9e66-system-5c192d6980b3b1ae\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-bde3f385-cb94-440d-9ba7-f20cd45c9e66-no_cache-69d7106a7247e84c\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-bde3f385-cb94-440d-9ba7-f20cd45c9e66-no_cache-9302598ec79a1148\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-bde3f385-cb94-440d-9ba7-f20cd45c9e66-task-f61cacef3cbc7f60\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-bde3f385-cb94-440d-9ba7-f20cd45c9e66-response-24c271e18e950d35\"}]}, {\"batch_id\": \"intake-intake_candidate_response-02c1b8ff-1f22-4221-809c-377c27d09dcb\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:04:56\", \"entity_cost\": 0.0003624, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-02c1b8ff-1f22-4221-809c-377c27d09dcb-system-4d1f6464c5179f6a\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-02c1b8ff-1f22-4221-809c-377c27d09dcb-no_cache-1832ac124e2de4b0\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-02c1b8ff-1f22-4221-809c-377c27d09dcb-no_cache-1d5368e54679ff53\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-02c1b8ff-1f22-4221-809c-377c27d09dcb-task-4010e9dc201bfab0\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-02c1b8ff-1f22-4221-809c-377c27d09dcb-response-cfc0ad702bfd515a\"}]}, {\"batch_id\": \"intake-intake_candidate_response-ca41d81e-6074-4999-bb24-d7c10dcc24df\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:09:52\", \"entity_cost\": 0.0004314, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-ca41d81e-6074-4999-bb24-d7c10dcc24df-system-a91712a8d572c72a\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-ca41d81e-6074-4999-bb24-d7c10dcc24df-no_cache-4fc4ee76c424d1b2\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-ca41d81e-6074-4999-bb24-d7c10dcc24df-no_cache-c5c06a0fbd5228f3\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-ca41d81e-6074-4999-bb24-d7c10dcc24df-task-9c2c0ed03dc07c08\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-ca41d81e-6074-4999-bb24-d7c10dcc24df-response-ee8c196d96c60b33\"}]}, {\"batch_id\": \"intake-intake_candidate_response-5618a01b-affd-4530-8b8b-636fbc6ccca0\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:17:24\", \"entity_cost\": 0.0004366, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-5618a01b-affd-4530-8b8b-636fbc6ccca0-system-8c8555c5ea8ad289\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-5618a01b-affd-4530-8b8b-636fbc6ccca0-no_cache-d1dddd27f663c295\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-5618a01b-affd-4530-8b8b-636fbc6ccca0-no_cache-2526459284e309dd\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-5618a01b-affd-4530-8b8b-636fbc6ccca0-task-7d17e40e69fd575a\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-5618a01b-affd-4530-8b8b-636fbc6ccca0-response-7d8f84c6c268ad56\"}]}, {\"batch_id\": \"intake-intake_candidate_response-bc462b3b-4923-4b47-9aff-ca59bb204a9b\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:18:37\", \"entity_cost\": 0.0003683, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-bc462b3b-4923-4b47-9aff-ca59bb204a9b-system-f514d733eb775389\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-bc462b3b-4923-4b47-9aff-ca59bb204a9b-no_cache-20c0b9de545faee7\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-bc462b3b-4923-4b47-9aff-ca59bb204a9b-no_cache-f585c3d9959ec498\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-bc462b3b-4923-4b47-9aff-ca59bb204a9b-task-82afb32d5fff7dba\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-bc462b3b-4923-4b47-9aff-ca59bb204a9b-response-bdccb1af3718a67f\"}]}, {\"batch_id\": \"intake-intake_candidate_response-0855a6cc-0e33-48c6-b1ce-855889cd2842\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:19:45\", \"entity_cost\": 0.0003793, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-0855a6cc-0e33-48c6-b1ce-855889cd2842-system-c8cf8831a47bc76c\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-0855a6cc-0e33-48c6-b1ce-855889cd2842-no_cache-9cc4707738902154\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-0855a6cc-0e33-48c6-b1ce-855889cd2842-no_cache-68fe440ca65dc579\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-0855a6cc-0e33-48c6-b1ce-855889cd2842-task-ed8b79b617d2b8f0\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-0855a6cc-0e33-48c6-b1ce-855889cd2842-response-bc0eab47db79d530\"}]}, {\"batch_id\": \"intake-intake_candidate_response-f01e61b7-3002-4b0f-9339-fc21a175195a\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:40:42\", \"entity_cost\": 0.0003924, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-f01e61b7-3002-4b0f-9339-fc21a175195a-system-b96dce80e53c39af\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-f01e61b7-3002-4b0f-9339-fc21a175195a-no_cache-a7c5a6ec57120495\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-f01e61b7-3002-4b0f-9339-fc21a175195a-no_cache-06ce1b164fc04fdd\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-f01e61b7-3002-4b0f-9339-fc21a175195a-task-f76a99702a56c6dc\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-f01e61b7-3002-4b0f-9339-fc21a175195a-response-e58960c8b3a0772c\"}]}, {\"batch_id\": \"intake-intake_candidate_response-1c09a6e2-6b82-42b8-ae99-99713d44eebc\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:45:29\", \"entity_cost\": 0.0004202, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-1c09a6e2-6b82-42b8-ae99-99713d44eebc-system-76498ac54cbb94f9\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-1c09a6e2-6b82-42b8-ae99-99713d44eebc-no_cache-09283ac9421a18a7\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-1c09a6e2-6b82-42b8-ae99-99713d44eebc-no_cache-1843e427539367a6\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-1c09a6e2-6b82-42b8-ae99-99713d44eebc-task-50c88d04823ceb00\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-1c09a6e2-6b82-42b8-ae99-99713d44eebc-response-3e5a64313255b68d\"}]}, {\"batch_id\": \"intake-intake_candidate_response-153c6d63-df45-4e59-b91e-8936512f3996\", \"task_key\": \"intake_candidate_response\", \"created_at\": \"2026-06-09 01:46:38\", \"entity_cost\": 0.0003999, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_candidate_response-153c6d63-df45-4e59-b91e-8936512f3996-system-451653ce2bb459be\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-153c6d63-df45-4e59-b91e-8936512f3996-no_cache-7c89e4f50907c49e\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_candidate_response-153c6d63-df45-4e59-b91e-8936512f3996-no_cache-822db074dfcf9e7a\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_candidate_response-153c6d63-df45-4e59-b91e-8936512f3996-task-6a80c9896478b4f5\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_candidate_response-153c6d63-df45-4e59-b91e-8936512f3996-response-b22dad9619d4dfa5\"}]}, {\"batch_id\": \"intake-intake_build_request-1c05f842-4a4c-4e85-bbdb-c07b76bbceba\", \"task_key\": \"intake_build_request\", \"created_at\": \"2026-06-09 01:47:48\", \"entity_cost\": 0.0005675, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"intake-intake_build_request-1c05f842-4a4c-4e85-bbdb-c07b76bbceba-system-49dd7f668d17d467\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_build_request-1c05f842-4a4c-4e85-bbdb-c07b76bbceba-no_cache-3101eded531ce208\"}, {\"type\": \"NO_CACHE\", \"id\": \"intake-intake_build_request-1c05f842-4a4c-4e85-bbdb-c07b76bbceba-no_cache-8193f3f6a58aa9bb\"}, {\"type\": \"TASK\", \"id\": \"intake-intake_build_request-1c05f842-4a4c-4e85-bbdb-c07b76bbceba-task-8b80365813513a90\"}, {\"type\": \"RESPONSE\", \"id\": \"intake-intake_build_request-1c05f842-4a4c-4e85-bbdb-c07b76bbceba-response-8059d92cd6125e82\"}]}, {\"batch_id\": \"user-craft_resume_base-8c282e32-6d98-4709-9891-4e9f265f7993\", \"task_key\": \"craft_resume_base\", \"created_at\": \"2026-06-09 02:16:40\", \"entity_cost\": 0.0112991, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"user-craft_resume_base-8c282e32-6d98-4709-9891-4e9f265f7993-system-2e34da60e7a972b2\"}, {\"type\": \"CACHE_A\", \"id\": \"user-craft_resume_base-8c282e32-6d98-4709-9891-4e9f265f7993-cache_a-b1b2fe5955d8bfdb\"}, {\"type\": \"NO_CACHE\", \"id\": \"user-craft_resume_base-8c282e32-6d98-4709-9891-4e9f265f7993-no_cache-d34dc4d8dc10a4c9\"}, {\"type\": \"NO_CACHE\", \"id\": \"user-craft_resume_base-8c282e32-6d98-4709-9891-4e9f265f7993-no_cache-8b36fb1e23b0f2fc\"}, {\"type\": \"TASK\", \"id\": \"user-craft_resume_base-8c282e32-6d98-4709-9891-4e9f265f7993-task-fccb36c2f56ed07c\"}, {\"type\": \"RESPONSE\", \"id\": \"user-craft_resume_base-8c282e32-6d98-4709-9891-4e9f265f7993-response-f7975260e021f33f\"}]}, {\"batch_id\": \"user-craft_resume_base-5bdeb39b-ecfb-4e76-b8d5-089cbde6c8e0\", \"task_key\": \"craft_resume_base\", \"created_at\": \"2026-06-14 23:04:51\", \"entity_cost\": 0.0333925, \"prompt_blocks\": [{\"type\": \"SYSTEM\", \"id\": \"user-craft_resume_base-5bdeb39b-ecfb-4e76-b8d5-089cbde6c8e0-system-a4fef10a4435ed45\"}, {\"type\": \"CACHE_A\", \"id\": \"user-craft_resume_base-5bdeb39b-ecfb-4e76-b8d5-089cbde6c8e0-cache_a-70d7605cfbf8f616\"}, {\"type\": \"NO_CACHE\", \"id\": \"user-craft_resume_base-5bdeb39b-ecfb-4e76-b8d5-089cbde6c8e0-no_cache-e494216eca22ba7a\"}, {\"type\": \"NO_CACHE\", \"id\": \"user-craft_resume_base-5bdeb39b-ecfb-4e76-b8d5-089cbde6c8e0-no_cache-8b508e012a362c10\"}, {\"type\": \"TASK\", \"id\": \"user-craft_resume_base-5bdeb39b-ecfb-4e76-b8d5-089cbde6c8e0-task-57999cf505ad0156\"}, {\"type\": \"RESPONSE\", \"id\": \"user-craft_resume_base-5bdeb39b-ecfb-4e76-b8d5-089cbde6c8e0-response-885b2e6b329e7470\"}]}]",
    "astral_candidate_id": "karfo",
    "candidate_api_key": null,
    "candidate_data": "{\"profile\": {\"first\": \"Justin\", \"last\": \"Karfo\", \"contact_email\": \"justin.karfo@gmail.com\", \"pronoun_preference\": \"he/him\", \"title_patterns\": \"(senior|staff|lead|principal|director)?\\\\s*(technical )?product manager\\n(senior|staff|lead|principal|director)?\\\\s*program manager\\n(general manager|expansion principal|head of product)\\n(senior|staff)?\\\\s*product management director\\n(senior|staff)?\\\\s*product lead\\n(vice president|vp)\\\\s*of product\\n(product|technical) product management\"}, \"context\": {\"starting_resume_text\": \"WEND-BOMA JUSTIN KARFO\\nSeattle, WA 98199 | 646-619-7499 | jkarfo@alumni.princeton.edu\\n\\nSUMMARY\\nPrinceton engineer. Wharton MBA. Principal-caliber product leader with 15+ years Big Tech (Amazon), growth investing (Goldman\\nSachs, Wendel), and zero-to-one experience (Via, Entrepreneurship). At Amazon, shipped ML-driven systems at $15B+ scale,\\nengineered $60M+ in savings, and led developer experience strategy for Alexa Smart Home. Earlier, worked in deploying $2.5B+ in\\ncapital across global markets. Fluent in French and English; operated across North America, Europe, and Africa.\\nEXPERIENCE\\nAMAZON.COM SERVICES LLC\\nSenior Product Manager \\u2013 Technical | Alexa Smart Home\\n\\nSeattle, USA\\nMay 2025 \\u2013 Aug 2025\\n\\u2022 Owned the product vision and roadmap for developer experience across API onboarding, SDKs, documentation, error handling,\\nsandbox, and support flows for Alexa Smart Home's partner ecosystem.\\n\\n\\u2022 Drove a cross-functional agenda, aligning Engineering, UX, Developer Relations, Go-to-Market, and Support, to reduce time-to-\\nfirst call and increase successful integrations, owning metrics including activation rate, dev NPS, and SDK adoption.\\n\\n\\u2022 Served as the authoritative voice of the developer community, translating partner research and field feedback into high-velocity\\nproduct decisions that set a new bar for API platform quality.\\nAMAZON.COM SERVICES LLC\\nManager, Product Management | Amazon Logistics (AMZL)\\n\\nSeattle, USA\\nJan 2022 \\u2013 May 2025\\n\\u2022 Directed a 7-person analytics team (6 BIEs, 1 Data Scientist) to deliver weekly network strategies across 400+ US & Canada\\ndelivery stations, stewarding $15B+ in annual operational resources.\\n\\u2022 Architected a step-change in planning capability, migrating from Excel-based processes to ML-driven forecasting, unlocking an\\n80% productivity gain and materially improving plan accuracy at scale.\\n\\u2022 Engineered $60M+ in cost savings through advanced automation and outlier detection, dramatically increasing model agility and\\nenabling faster, more confident resource allocation decisions.\\n\\u2022 Delivered compelling, data-driven narratives to senior leadership that translated complex analytical outputs into clear strategic\\nguidance, accelerating executive decision-making on high-stakes programs.\\n\\u2022 Synchronized cross-functional demand forecasts with capacity and supply plans, driving measurable improvements in\\noperational readiness and on-time delivery performance across the network.\\nAMAZON.COM SERVICES LLC\\nSenior Program Manager | Customer Trust & Partner Support (CTPS)\\n\\nNew York, USA\\nJan 2021 \\u2013 Jan 2022\\n\\u2022 Spearheaded the global Funds Disbursement Appeals Program (FDAP), a $200M+ risk-mining initiative that identified and\\nneutralized bad actors across Amazon's retail marketplace.\\n\\u2022 Directed a specialized team of 25 investigators and risk managers in anti-fraud and anti-counterfeit operations, establishing\\nglobal strategy, policy, and senior leadership stakeholder relationships.\\n\\u2022 Expanded program reach into India and Europe through strategic partnership with Legal and Public Policy, driving regulatory\\nupdates and funds-withholding mechanisms that reduced financial risk at global scale.\\nVIA TRANSPORTATION, INC.\\nExpansion Principal | Public Mobility Solutions\\n\\nNew York City, USA\\nAug 2019 \\u2013 Oct 2020\\n\\u2022 Owned full P&L accountability for four simultaneous Transportation-as-a-Service deployments (Fort Worth, West Sacramento,\\nLos Angeles, Cupertino), driving profitability, growth, and performance optimization.\\n\\u2022 Served as General Manager overseeing all logistical, technical, and operational dimensions of each city launch.\\n\\u2022 Cultivated strategic relationships with municipal governments and transportation agencies, ensuring policy alignment, service\\ndelivery excellence, and contract expansion opportunities.\\nWENDEL\\nPrivate Equity Associate\\n\\nCasablanca, Morocco\\nApr 2016 \\u2013 Apr 2017\\n\\u2022 Developed investment theses and built detailed financial models for two flagship transactions: a $170M majority stake in Tsebo\\n(pan-African facilities services) and a $30M position in PlaYce (African shopping mall venture).\\n\\u2022 Contributed to portfolio company transactions including IHS Towers' acquisition of Helios Towers Nigeria and Saham Finances'\\nrecapitalization.\\nEMERGING CAPITAL PARTNERS (ECP)\\nSenior Private Equity Analyst\\n\\nAbidjan, C\\u00f4te d'Ivoire / Nairobi, Kenya\\nMar 2015 \\u2013 Mar 2016\\n\\u2022 Led end-to-end financial modeling and due diligence for a $100M investment in an East African port logistics company.\\n\\n\\u2022 Provided financial analysis and strategic advisory support to two West African portfolio companies \\u2014 Eranove and Orabank \\u2014 to\\naccelerate their growth initiatives.\\nTHOMSON REUTERS\\nSenior Solutions Specialist\\n\\nLondon, UK\\nJul 2013 \\u2013 Jul 2014\\n\\u2022 Built the business case and led pricing strategy for Thomson Reuters' KYC platform, securing $60M+ in board-level funding\\napproval to commercialize the initiative.\\n\\u2022 Conducted financial analysis and due diligence supporting corporate venturing and new market growth initiatives within the\\nFinance & Risk division.\\nGOLDMAN SACHS INTERNATIONAL\\nGrowth Private Equity Investing, Analyst | Principal Strategic Investments\\nGroup\\n\\nLondon, UK\\nJun 2011 \\u2013 Jun 2013\\n\\u2022 Managed all stages of the growth equity investment lifecycle: sourcing, financial analysis, valuation, and deal execution \\u2014 for\\nminority investments up to $30M in high-growth enterprise and fintech firms.\\n\\u2022 Conducted comprehensive commercial and financial due diligence across 15+ companies, closing 3 investments and supporting\\nstrategic initiatives including follow-on funding rounds.\\n\\u2022 Collaborated with bankers on the \\u00a31.4B sale of the London Metal Exchange to the Hong Kong Stock Exchange; executed\\ntransactions including a $12.5M investment in Motif Investing and a $15.5M investment in InCapital.\\nEDUCATION\\nTHE WHARTON SCHOOL, UNIVERSITY OF PENNSYLVANIA\\nMaster of Business Administration; Finance and Entrepreneurship & Innovation\\n\\nPhiladelphia, PA\\n2017 \\u2013 2019\\n\\nPRINCETON UNIVERSITY\\nBachelor of Science in Engineering; Operations Research & Financial Engineering\\n\\nPrinceton, NJ\\n2007 \\u2013 2011\\n\\nADDITIONAL INFORMATION\\nLanguages: Native fluency in English, French, Moore, and Nankana (Burkina Faso)\\nInterests: Music, Traveling, Cinema, Chelsea FC, History, Industrial Policy, African Affairs, Investing, Technology\", \"linkedin_profile_text\": \"Experience\\n\\nStealth Startup logo\\nFounder\\n\\nStealth Startup\\n\\nAug 2025 - Present \\u00b7 11 mos\\n\\nAmazon logo\\nAmazon\\n\\n4 yrs 7 mos\\n\\nSr. Product Manager - Technical\\n\\nMay 2025 - Jul 2025 \\u00b7 3 mos\\n\\nPartner Quality and Developer Experience for Alexa Smart Home.\\n\\nManager, Product Management\\n\\nJun 2022 - May 2025 \\u00b7 3 yrs\\n\\nProduct & Analytics within Planning at Amazon Logistics (AMZL)\\n\\nSenior Program Manager\\n\\nJan 2021 - May 2022 \\u00b7 1 yr 5 mos\\n\\nBusiness Owner of the global Funds Disbursement Appeals Program (FDAP)\\n\\nVia logo\\nExpansion Principal\\n\\nVia\\n\\nJul 2019 - Oct 2020 \\u00b7 1 yr 4 mos\\n\\nGeneral Manager of the Fort Worth, West Sacramento, Los Angeles and Cupertino Partner Cities deployments\\n\\nCo-Founder & COO\\n\\nElivade\\n\\nAug 2018 - Sep 2020 \\u00b7 2 yrs 2 mos\\n\\nHR Tech platform to help employers hire & retain top talent at scale. \\n\\nSolon Capital Partners logo\\nVice President\\n\\nSolon Capital Partners\\n\\nApr 2018 - Jul 2019 \\u00b7 1 yr 4 mos\\n\\nBebe Burkinabe logo\\nCo-Founder\\n\\nBebe Burkinabe\\n\\nMar 2015 - Nov 2017 \\u00b7 2 yrs 9 mos\\n\\nConsumer healthcare startup in West Africa. Recipient of the Chuck Dell Prize.\\n\\nWendel logo\\nPrivate Equity Investor\\n\\nWendel\\n\\nMar 2016 - Jun 2017 \\u00b7 1 yr 4 mos\\n\\nEmerging Capital Partners - ECP logo\\nPrivate Equity Investor\\n\\nEmerging Capital Partners - ECP\\n\\nJan 2015 - Mar 2016 \\u00b7 1 yr 3 mos\\n\\nThomson Reuters logo\\nSolutions Group (FinTech incubator & investments)\\n\\nThomson Reuters\\n\\nJul 2013 - Oct 2014 \\u00b7 1 yr 4 mos\\n\\nGoldman Sachs logo\\nPrivate Equity Investor, Principal Strategic Investments Group\\n\\nGoldman Sachs\\n\\nJun 2010 - Jul 2013 \\u00b7 3 yrs 2 mos\\n\\nUnited Nations Development Program logo\\nConsultant, The Growing Inclusive Markets Initiative\\n\\nUnited Nations Development Program\\n\\nJun 2009 - Jun 2010 \\u00b7 1 yr 1 mo\\n\\nGoldman Sachs logo\\nFinancial Analyst\\n\\nGoldman Sachs \\u00b7 Internship\\n\\nMay 2008 - Aug 2008 \\u00b7 4 mos\\n\\nNew York City Metropolitan Area\\n\\nAfrican Leadership Academy logo\\nCurriculum Development / Student Recruitment and Selection Design\\n\\nAfrican Leadership Academy \\u00b7 Internship\\n\\nJun 2007 - Sep 2007 \\u00b7 4 mos\", \"sample_cover_text\": \"\", \"bio_summary\": \"Princeton-trained engineer and Wharton MBA with 15+ years bridging technology, investment, and operations. As a product leader at Amazon, he shipped ML-driven systems at $15B+ scale and drove $60M+ in savings. His career spans growth equity at Goldman Sachs, private equity across Africa, zero-to-one launches at Via, and founding two startups. Fluent in four languages and experienced across North America, Europe, and Africa.\", \"backstory\": \"Wend-Boma Justin Karfo started his career in growth equity at Goldman Sachs in London, then moved to Africa for private equity roles at Emerging Capital Partners and Wendel \\u2014 sourcing deals, building financial models, and advising portfolio companies. A desire to build rather than just invest led him to co-found Bebe Burkinabe, a consumer healthcare startup in West Africa, and later Elivade, an HR tech platform. He then took on operational leadership at Via, launching four TaaS deployments as General Manager. At Amazon, he scaled from Senior Program Manager (building a $200M+ risk-mining program) to Manager of Product Management (directing analytics for $15B+ logistics network), then to Senior PM-T for Alexa Smart Home. Now he's back to building as a founder at a stealth startup \\u2014 driven by the conviction that the most impactful work happens at the intersection of technical depth, market insight, and the grit to make something from nothing.\", \"strengths\": \"Built ML-driven forecasting and optimization systems at $15B+ scale, delivering $60M+ in savings and 80% productivity gains\\nArchitected and managed cross-functional programs spanning engineering, data science, legal, and policy across global markets\\nLed end-to-end deal execution: sourcing, financial modeling, due diligence, valuation for investments up to $170M\\nLaunched and scaled zero-to-one operations \\u2014 from P&L ownership to government partnerships to on-the-ground logistics\\nCommunicates complex analytical insights into clear strategic narratives for C-suite and board audiences\\nFluent in four languages (English, French, Moore, Nankana) and comfortable operating across US, Europe, and Africa\", \"priorities\": \"A role where I can combine product strategy, data, and business ownership \\u2014 ideally at an early- to growth-stage company where my full toolkit (PM, PE, ops, founder) is leveraged. I want measurable impact on product-market fit, revenue growth, or operational scale, with a high degree of autonomy. Global scope is a strong pull, especially if it involves emerging markets or multi-region deployment.\", \"deal_breakers\": \"Roles that are purely executional with no strategic input or ownership. Highly bureaucratic environments where decisions are slow and consensus-driven. Companies that don't value a product mindset or data-informed decision-making. Positions requiring relocation outside of Seattle or willingness to travel >30% long-term.\"}}",
    "created_at": "2026-06-09 00:11:37",
    "state": "LIVE_PROMPTS",
    "state_changed_at": "2026-06-09 00:11:37",
    "updated_at": "2026-06-09 01:47:48"
  }
]
```

#### chuckles — 2026-06-14T22:52:55.452Z
[check-linear] **Issue:** `craft_resume_base` **Generate** for karfo — DeepSeek returned a valid-looking `agent_payload` (name, summary, experience, etc.) but **omitted** the `resume_structure` key. Schema validation ran before any defaulting and hard-failed: `Missing required field 'resume_structure'`.

**Fix (AST-644, on `dev`):** In `normalize_craft_resume_base_agent_payload` (`src/core/candidate.py`), when `resume_structure` is missing or has empty `sections`, we inject `default_resume_structure()` **before** `_validate_response_schema` — same default path AST-517 already used at split time. Valid custom structure from the model is left untouched.

**Re-test:** prep-uat landed this ~20:49 UTC. Hard-refresh / restart local server on current `dev`, then **Generate** again on karfo. If it still fails, paste the new log line + whether `resume_structure` appears in the model JSON — different root cause.

#### susan — 2026-06-14T21:30:37.681Z
@chuckles This is still an issue.  Can you tell me what the issue was and how it was fixed?

#### chuckles — 2026-06-14T20:49:53.910Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-644** | craft_resume_base fails — model omits resume_structure |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-14T20:44:15.152Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-601 (parent) | ftr/AST-601-rebuild-519-git-casualty |
| AST-616 | sub/AST-601/AST-616-base-resume-content-ui-rebuild-519 |
| AST-644 | sub/AST-601/AST-644-craft-resume-base-missing-structure |

**Epic worktree:** `astral-AST-601/` — one active sub checked out at a time.

**Parent:** AST-601

— Chuckles

#### susan — 2026-06-14T20:40:57.952Z
Failed: Here's the log: \[2026-06-14 20:36:57\] INFO src.core.candidate: UI generate started task_key='craft_resume_base' ledger_task_key=user-craft_resume_base batch_id=user-craft_resume_base-f9b1481b-cf8f-40f8-b416-ca80ac59a6dd candidate_id=karfo

\[2026-06-14 20:36:57\] WARNING src.utils.config: Token {$SAMPLE_COVER_TEXT} resolved to empty (path=context.sample_cover_text, task=craft_resume_base)

\[2026-06-14 20:36:57\] INFO src.core.agent: run_next chain entry: task=craft_resume_base batch_id=user-craft_resume_base-f9b1481b-cf8f-40f8-b416-ca80ac59a6dd

\[2026-06-14 20:36:57\] INFO src.external.deepseek: LLM deepseek task=craft_resume_base 138.1s stop=end_turn tokens in=7605 out=12106

\[2026-06-14 20:36:57\] ERROR src.core.agent: do_task validation failed. task_key='craft_resume_base' error=Missing required field 'resume_structure'

\[2026-06-14 20:36:57\] ERROR src.core.candidate: artifact generation failed task_key='craft_resume_base' batch_id=user-craft_resume_base-f9b1481b-cf8f-40f8-b416-ca80ac59a6dd error=Missing required field 'resume_structure'

And here's the prompt response:

```
[karfo]
Validation failed: Missing required field 'resume_structure'

--- model response ---
{
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": {
    "candidate_name": "WEND-BOMA JUSTIN KARFO",
    "candidate_title": "Founder & Product Leader: Big Tech, Private Equity, and Zero-to-One Experience",
    "candidate_contact_detail": "Seattle, WA 98199 • 646-619-7499 • jkarfo@alumni.princeton.edu",
    "professional_summary": "A Princeton-trained engineer and Wharton MBA, Wend-Boma Justin Karfo brings over 15 years of experience at the intersection of technology, investment, and operations. His career spans Big Tech product leadership at Amazon, growth equity at Goldman Sachs, private equity across Africa, zero-to-one mobility deployments at Via, and founding two startups. He has deployed over $2.5B in capital globally and built ML-driven systems operating at $15B+ scale.\n\nAt Amazon, he led product and analytics for Amazon Logistics, where his team's ML-driven forecasting and automation delivered $60M+ in savings and an 80% productivity gain across a 400-station network. As Senior PM-T for Alexa Smart Home, he owned developer experience strategy, driving measurable improvements in activation rate and developer NPS. Earlier, he built a $200M+ global risk-mining program, managing 25 investigators across multiple continents. His investment background includes sourcing and executing deals for Goldman Sachs, Wendel, and Emerging Capital Partners, with experience in deal sizes up to $170M.\n\nFluent in four languages and having worked across North America, Europe, and Africa, Justin is driven by building products with measurable impact in global markets. He thrives in roles that demand full ownership of product strategy, data, and business outcomes — particularly in early- to growth-stage companies where his broad toolkit can directly shape product-market fit and operational scale.",
    "core_competencies": "Product Strategy & Roadmapping | Data-Driven Decision Making | ML-Driven Forecasting & Analytics | Cross-Functional Leadership | Financial Modeling & Investment Analysis | Private Equity & Venture Deals | P&L Management & Business Operations | Global Market Expansion | Risk Management & Compliance | Developer Experience (API/SDK/Docs) | Operational Excellence",
    "experience": "AMAZON.COM SERVICES LLC\nSenior Product Manager – Technical | Alexa Smart Home | May 2025 to Aug 2025 | Seattle, USA\n\nOwned the product vision and roadmap for Alexa Smart Home's developer experience, covering API onboarding, SDKs, documentation, error handling, sandbox, and support flows. Drove a cross-functional agenda across Engineering, UX, Developer Relations, Go-to-Market, and Support to reduce time-to-first-call and increase successful integrations, with direct ownership of metrics including activation rate, developer NPS, and SDK adoption. Served as the authoritative voice of the developer community, translating partner research and field feedback into high-velocity product decisions that set a new bar for API platform quality.\n\nAMAZON.COM SERVICES LLC\nManager, Product Management | Amazon Logistics (AMZL) | Jan 2022 to May 2025 | Seattle, USA\n\nDirected a 7-person analytics team (6 BIEs, 1 Data Scientist) to deliver weekly network strategies across 400+ US and Canada delivery stations, stewarding $15B+ in annual operational resources. Architected a step-change in planning capability, migrating from Excel-based processes to ML-driven forecasting, unlocking an 80% productivity gain and materially improving plan accuracy at scale. Engineered $60M+ in cost savings through advanced automation and outlier detection, dramatically increasing model agility and enabling faster, more confident resource allocation decisions. Delivered compelling, data-driven narratives to senior leadership, translating complex analytical outputs into clear strategic guidance that accelerated executive decision-making on high-stakes programs. Synchronized cross-functional demand forecasts with capacity and supply plans, driving measurable improvements in operational readiness and on-time delivery performance across the network.\n\nAMAZON.COM SERVICES LLC\nSenior Program Manager | Customer Trust & Partner Support (CTPS) | Jan 2021 to Jan 2022 | New York, USA\n\nSpearheaded the global Funds Disbursement Appeals Program (FDAP), a $200M+ risk-mining initiative that identified and neutralized bad actors across Amazon's retail marketplace. Directed a specialized team of 25 investigators and risk managers in anti-fraud and anti-counterfeit operations, establishing global strategy, policy, and senior leadership stakeholder relationships. Expanded program reach into India and Europe through strategic partnership with Legal and Public Policy, driving regulatory updates and funds-withholding mechanisms that reduced financial risk at global scale.\n\nVIA TRANSPORTATION, INC.\nExpansion Principal | Public Mobility Solutions | Aug 2019 to Oct 2020 | New York City, USA\n\nOwned full P&L accountability for four simultaneous Transportation-as-a-Service deployments (Fort Worth, West Sacramento, Los Angeles, Cupertino), driving profitability, growth, and performance optimization. Served as General Manager overseeing all logistical, technical, and operational dimensions of each city launch. Cultivated strategic relationships with municipal governments and transportation agencies, ensuring policy alignment, service delivery excellence, and contract expansion opportunities.\n\nWENDEL\nPrivate Equity Associate | Apr 2016 to Apr 2017 | Casablanca, Morocco\n\nDeveloped investment theses and built detailed financial models for two flagship transactions: a $170M majority stake in Tsebo (pan-African facilities services) and a $30M position in PlaYce (African shopping mall venture). Contributed to portfolio company transactions including IHS Towers' acquisition of Helios Towers Nigeria and Saham Finances' recapitalization.\n\nEMERGING CAPITAL PARTNERS (ECP)\nSenior Private Equity Analyst | Mar 2015 to Mar 2016 | Abidjan, Côte d'Ivoire / Nairobi, Kenya\n\nLed end-to-end financial modeling and due diligence for a $100M investment in an East African port logistics company. Provided financial analysis and strategic advisory support to two West African portfolio companies — Eranove and Orabank — to accelerate their growth initiatives.\n\nTHOMSON REUTERS\nSenior Solutions Specialist | Jul 2013 to Jul 2014 | London, UK\n\nBuilt the business case and led pricing strategy for Thomson Reuters' KYC platform, securing $60M+ in board-level funding approval to commercialize the initiative. Conducted financial analysis and due diligence supporting corporate venturing and new market growth initiatives within the Finance & Risk division.\n\nGOLDMAN SACHS INTERNATIONAL\nGrowth Private Equity Investing, Analyst | Principal Strategic Investments Group | Jun 2011 to Jun 2013 | London, UK\n\nManaged all stages of the growth equity investment lifecycle: sourcing, financial analysis, valuation, and deal execution — for minority investments up to $30M in high-growth enterprise and fintech firms. Conducted comprehensive commercial and financial due diligence across 15+ companies, closing 3 investments and supporting strategic initiatives including follow-on funding rounds. Collaborated with bankers on the £1.4B sale of the London Metal Exchange to the Hong Kong Stock Exchange; executed transactions including a $12.5M investment in Motif Investing and a $15.5M investment in InCapital.",
    "prior_experience": "",
    "education_certifications": "THE WHARTON SCHOOL, UNIVERSITY OF PENNSYLVANIA - Master of Business Administration; Finance and Entrepreneurship & Innovation (2017 – 2019)\nPRINCETON UNIVERSITY - Bachelor of Science in Engineering; Operations Research & Financial Engineering (2007 – 2011)",
    "technical_skills": ""
  }
}
```

This was the task instruction:

**TASK INSTRUCTIONS**

Parse and synthesize raw candidate content into a structured JSON representation with exactly 9 keyed segments. This is a SYNTHESIS task — you are blending multiple sources into enriched segments, not just copying text into buckets.

**Input sources (not all may be present):**

* **Bio Summary** - an "elevator pitch" for the candidate, to give you a sense of tone.
* **Resume text** — AUTHORITATIVE source of facts. Job titles, company names, team sizes, metrics, dates, certifications. When resume and LinkedIn conflict on facts, resume wins. Always.
* **LinkedIn profile** — Adds narrative context, personality, and framing. Enriches professional summary and experience sections. Does NOT override resume facts.
* **Experience Backstory** - Plain english what the candidate actually did at the job, what they liked, tolerated, and why they left.  BE CAREFUL not to incorporate any negativity into the new content.
* **Strengths list** — Structured entries with label, description, and priority (1-5). Priority scores tell you what to emphasize. Higher priority = more prominent in synthesis. Do NOT include priority scores or labels verbatim in output.
* **Priorities list** — Structured entries describing what the candidate WANTS in their next role. Context for emphasis in the professional summary. Do NOT include priority scores or labels verbatim in output.
* **Sample Cover Letter** - Plain text of a cover letter the candidate has sent for a real-world application in the past.

---

## OUTPUT SCHEMA

Respond ONLY with valid JSON. No preamble, no markdown fences, no explanation. The pipeline parses your response directly.

{

"agent_performance": {

```
"status": "success | failure",
"failure_note": "<failure_note>"
```

},

"agent_payload": {

```
"resume_structure": {
  "<key>": "<value>"
},
"candidate_name": "<candidate_name>",
"candidate_title": "<candidate_title>",
"candidate_contact_detail": "<candidate_contact_detail>",
"professional_summary": "<professional_summary>",
"core_competencies": "<core_competencies>",
"experience": "<experience>",
"prior_experience": "<prior_experience>",
"education_certifications": "<education_certifications>",
"technical_skills": "<technical_skills>"
```

}

}

---

## SEGMENT INSTRUCTIONS

### candidate_name

Extract the candidate's full name from the resume. Plain text, no titles or suffixes unless part of the formal name.

### candidate_title

Extract or synthesize the professional title/headline. Resume title is the anchor; if LinkedIn has a richer headline, blend the two. Keep it concise — under 15 words.

### candidate_contact_detail

Extract all contact information into a single string: email, phone, LinkedIn URL, location. Separate items with " • " (space-bullet-space). Clean and human-readable.

### professional_summary

**This is the primary synthesis segment.** Blend:

* Resume's professional summary (structure, core claims)
* LinkedIn's summary and/or sample cover letter (voice, personality, narrative framing)
* High-priority strengths (weave in the candidate's self-identified superpowers where it sounds natural and relevant)
* High-priority priorities (subtle signals about what they value)

Rules:

* 2-3 short paragraphs is ideal, 4 is the rare maximum.
* Match the dominant voice of the source material (first person if inputs use it, third person if they do)
* Every factual claim must trace to the resume or LinkedIn — no fabrication
* Do NOT paste strengths labels or priority labels verbatim; synthesize their substance naturally
* Capture the candidate's distinctive voice — if they're direct and pragmatic, your summary is too
* This should read like the best version of what the candidate would write about themselves

### core_competencies

Start with the resume's explicit core competencies section. Enrich with competency-level terms from strengths IF genuinely supported by resume/LinkedIn evidence. Present as a single string, items separated by " | ".
Rules:

* Only include competencies backed by evidence in the source material
* Keep as keyword/phrase list, not sentences
* Do NOT invent competencies

### experience

**The big segment.** Synthesize each role by blending resume facts with LinkedIn and backstory narrative.

Format each role as:

```
COMPANY NAME
Title | Start Year to End Year | Location / Work Mode
[Description paragraph and/or bullet points for that role]
```

Separate roles with a blank line.

Rules:

* **Resume is source of truth** for: company names, titles, dates, team sizes, metrics, achievements
* **LinkedIn + Backstory adds:** narrative framing, context about the role's significance, work environment color
* **Strengths add:** if a strength description references specific work that maps to a role, weave it in
* Preserve ALL quantified achievements exactly (percentages, dollar amounts, team sizes, timelines)
* Do NOT change company names, titles, or dates from the resume
* Do NOT fabricate achievements appearing in neither resume nor LinkedIn
* Do NOT inflate metrics — if the resume says 25, you say 25
* When LinkedIn provides richer context for a resume bullet, blend them — resume fact anchors it
* Include any introductory/summary text a role has (e.g. "Owner/operator of a boutique consultancy...")
* Maintain the same role order as the resume

### prior_experience

Extract the prior experience summary line from the resume, stripped of formatting codes. This is typically a condensed line listing earlier roles with durations.

Example: `"Project Manager (4 yrs) • Systems Analyst (6 yrs) • ETL Migration Specialist (2 yrs)"`

IF THIS SECTION IS NOT IN THE ORIGINAL RESUME TEXT, just return an empty string.

### education_certifications

Extract all education and certification entries. Each entry on its own line within the string. Include certification bodies, dates, institutions, degree/coursework details. Preserve facts exactly.

IF THIS SECTION IS NOT IN THE ORIGINAL RESUME TEXT, just return an empty string.

### technical_skills

Extract the full technical skills inventory. Preserve category groupings from the resume. Each category on its own line, items separated by " | ".
Example:

```
Project Management: Linear | Jira | Trello | Azure DevOps
Cloud & DevOps: AWS | Vercel | GitHub | CI/CD Pipelines
```

IF THIS SECTION IS NOT IN THE ORIGINAL RESUME TEXT, just return an empty string.

---

## FORMATTING RULES (GLOBAL)

1. **Strip ANY formatting artifacts** from source material: `!` line prefixes, `__` (replace with space), `~~` (replace with hyphen), markdown headers (#), and any other markup.
2. **JSON string escaping**: Use `\n` for newlines within values. Escape internal double quotes as `\"`.
3. **No trailing whitespace** in values.
4. **No HTML, markdown, or other markup** in values — plain text only

---

## QUALITY CHECKLIST

Before returning JSON, verify:

* Every key present with a non-empty string value
* candidate_name matches the resume exactly
* No metrics or team sizes differ from resume source
* No fabricated achievements or experience
* professional_summary captures the candidate's actual voice
* experience entries preserve all quantified achievements
* All formatting codes stripped clean
* The JSON is valid and parseable

**CRITICAL:** Your entire response must be valid parseable JSON. No markdown, no explanations, no text outside the JSON object.

#### chuckles — 2026-06-14T03:57:56.716Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-601 (parent) | ftr/AST-601-rebuild-519-git-casualty |
| AST-616 | sub/AST-601/AST-616-base-resume-content-ui-rebuild-519 |

**Epic worktree:** `astral-AST-601/` — one active sub checked out at a time.

**Parent:** AST-601

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
