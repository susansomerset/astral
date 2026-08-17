# AST-1183 — Gaze Review rename + Meteorite Review sibling + agent_task grouping

<!-- linear-archive: AST-1183 archived 2026-08-17 -->

## Linear archive (AST-1183)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1185

### Description

## Purpose

Operators currently see meteorite and classic gaze/GDL tasks mixed under one **Job Review** section. Meteorite work needs its own visible section so mailbox → parse → qualify → evaluate → like/upshot tasks sit together, while the classic gaze review chain keeps a clear home under a renamed **Gaze Review** label. This epic is catalog/grouping truth in `agent_task` seed — not alias plumbing and not a UI hardcode audit (those are sibling tickets).

## Functional scope

* Rename the existing **Job Review** grouping/section label to **Gaze Review** for the classic gaze / job-review tasks that remain in that section (same section identity, new display name).
* Introduce a sibling grouping/section **Meteorite Review** with its own section order so it appears as a peer of Gaze Review (not nested inside it).
* Move meteorite-track `agent_task` rows into **Meteorite Review** with coherent within-section sequence so meteorite content groups together end-to-end. Proposed membership (current keys): `gaze_email`, `parse_meteorite_email` (or `meteorite_email` if [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks) has already renamed it), `qualify_meteorite`, `evaluate_meteorite`, `meteorite_like`, `meteorite_upshot`. Classic gaze/GDL rows stay under Gaze Review (`gaze`, `qualify_job_listings`, `fetch_jd`, `evaluate_jd`, `grade_do`, `grade_get`, `fetch_culture_pages`, `grade_like`, `analysis_upshot`).
* Keep repo `agent_task` seed and locked fixtures consistent with the new names/membership so boot / Revert-to-file apply the same grouping operators see in Admin.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` (this epic reshapes existing `agent_task` grouping metadata / seed content; it does not introduce a new code execution shape). UI continues to consume DB grouping fields already established by prior Organizing Tasks / Scheduled Actions work.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.seed.agent-tables-in-repo-json` — grouping changes ship in repo `agent_task` JSON, not one-off DB edits.
  * `astral.standards.no-hardcoded-sets` — section membership and order live on seed rows; do not invent parallel hard-coded Job/Gaze/Meteorite Review lists in product code on this ticket.
  * `astral.standards.in-scope-only` — do not take alias, UI hardcode audit, or meteorite_email rename work from siblings.
  * `astral.standards.names-not-ticket-ids` — section labels are product names (Gaze Review / Meteorite Review), not ticket-scoped strings.
  * `astral.standards.no-cross-contamination` / `astral.layers.import-direction` — if any thin API helper is touched only for seed/fixture alignment, honor layer bounds (prefer seed-only).

## Boundaries

* Does **not** rename the Ruth parse task to `meteorite_email` or change AI payloads ([AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks)).
* Does **not** add `master_task_key` / task aliases ([AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key)).
* Does **not** own the UI hardcode / alphabetical dropdown verification pass ([AST-1185](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven)) — this ticket makes the seed truth correct; that sibling confirms the UI is data-driven.
* Does **not** own evaluate_meteorite test/statute fold-in ([AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check)).
* Does **not** move `craft_evaluate_meteorite_rubric` out of Candidate Artifacts (craft rubric, not Job Review).
* Does **not** change dispatch trigger states, run_next chains, prompts, or scoring behavior beyond grouping metadata needed for section placement.
* Does **not** invent React-only section labels that diverge from `agent_task` seed.

## Acceptance criteria

* No current `agent_task` seed row still uses `task_group_name` **Job Review**.
* Classic gaze/GDL tasks listed under Functional scope show `task_group_name` **Gaze Review** with a shared section order that replaces the old Job Review order identity.
* Meteorite-track tasks in the proposed membership show `task_group_name` **Meteorite Review**, share one Meteorite Review section order distinct from Gaze Review, and sort together as one section in Admin surfaces that read grouping metadata.
* Repo seed and AST-756 (or equivalent) locked `agent_task` fixtures match the new names/membership.
* After seed apply, Scheduled Actions / Manage Tasks section headers show **Gaze Review** and **Meteorite Review** (not Job Review) for those rows — without requiring alias or dropdown work from siblings.

## Dependencies and blockers

* Related intake: [AST-1181](https://linear.app/astralcareermatch/issue/AST-1181/generate-issues-for-meteorite-changes) (Backlog; out of scope for this define — sibling bullets live on [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks)–[AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check)).
* Soft awareness (not Linear blockedBy): [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks) may rename `parse_meteorite_email` → `meteorite_email`; Meteorite Review membership must track whichever key is live when this lands.
* Soft awareness: [AST-1088](https://linear.app/astralcareermatch/issue/AST-1088/gaze-email-config-null-candidate-dispatch-shell-gmail-archivetrash-add) / [AST-1089](https://linear.app/astralcareermatch/issue/AST-1089/ruth-little-brain-meteorite-email-parse-task-add-gaze-email-as-a) / [AST-1090](https://linear.app/astralcareermatch/issue/AST-1090/gaze-email-runner-bind-route-scrape-dedupe-create-mailbox-outcomes-add) / [AST-1106](https://linear.app/astralcareermatch/issue/AST-1106/uat-gaze-email-missing-from-scheduled-actions-default-view) / [AST-1107](https://linear.app/astralcareermatch/issue/AST-1107/uat-admin-task-name-should-equal-task-key-for-now) still User Testing under current Job Review grouping — fixture and catalog expectations that assert **Job Review** must move with this epic.
* Sibling Discussion tickets [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key)–[AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check) are adjacent scope only; none block this definition.

none as Linear blockedBy.

## Open questions

none (Archie confirmed membership + order `4000`/`4500`.)

## Proposed child tickets

#### 1!: **Rename Job Review to Gaze Review in agent_task seed - Ada**

Owns the section rename for rows that remain classic gaze/GDL under the old Job Review group: set `task_group_name` to **Gaze Review** (retain existing `task_group_order` `4000` unless Open question #2 changes it), and update fixtures/tests that assert the old label for those rows. Does **not** create Meteorite Review or move meteorite rows (sibling #2). Does **not** touch aliases or UI hardcode audit.
**Citations:** `astral.seed.agent-tables-in-repo-json`; `astral.standards.names-not-ticket-ids`; `astral.standards.in-scope-only`.

#### 2: **Meteorite Review group + move meteorite agent_task rows - Hedy**

After #1 (or coordinated on the same seed tip): create **Meteorite Review** (`task_group_order` per Open question #2, default `4500`), move the approved meteorite membership rows onto that group with coherent `task_seq`, and align fixtures/tests. Does **not** rename classic Job Review→Gaze Review rows (sibling #1). Does **not** implement `master_task_key` ([AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key)) or the data-driven UI audit ([AST-1185](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven)).
**Citations:** `astral.seed.agent-tables-in-repo-json`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`.

---

## Original brief

From AST-1181:

* Rename Job Review to Gaze Review as a grouping/section
* Add a sibling as "Meteorite Review"
* Update the grouping content in agent_task to group the meteorite content together

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| [AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping) (parent) | ftr/AST-1183-gaze-review-rename-meteorite-review-sibling |
| [AST-1218](https://linear.app/astralcareermatch/issue/AST-1218/rename-job-review-to-gaze-review-in-agent-task-seed-gaze-review-rename) | sub/AST-1183/AST-1218-rename-job-review-to-gaze-review-in-agent-task-seed |
| [AST-1219](https://linear.app/astralcareermatch/issue/AST-1219/meteorite-review-group-move-meteorite-agent-task-rows-gaze-review) | sub/AST-1183/AST-1219-meteorite-review-group-move-meteorite-agent-task-rows |

**Epic worktree:** `astral-AST-1183/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/cf26015a794391a60a3d67e0539bcb26/761584da-c4ac-4d0e-a79d-cf974f7020b8/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/cf26015a794391a60a3d67e0539bcb26/0783f4b0-e94a-4022-8cd7-dd652a51c0aa/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/4eb14290-e070-4bd9-ba26-1c625f57c720/store.db` |
| Radia | review | `/home/susan/.cursor/chats/cf26015a794391a60a3d67e0539bcb26/69220550-4ba4-49dd-b04e-4d59f7791b61/store.db` |

### Comments

#### chuckles — 2026-08-07T22:50:49.868Z
@susan — grouping-only `UPDATE`s from `origin/ftr/AST-1183-gaze-review-rename-meteorite-review-sibling` (prompts / other columns untouched). Safe to run after prompt rework; does not re-seed prompts.

```sql
-- AST-1183 cosmetic grouping only (prompts / other columns untouched)
-- SQLite agent_task — current=1 rows only
BEGIN;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 1 WHERE task_key = 'gaze' AND current = 1;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 2 WHERE task_key = 'qualify_job_listings' AND current = 1;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 3 WHERE task_key = 'fetch_jd' AND current = 1;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 4 WHERE task_key = 'evaluate_jd' AND current = 1;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 5 WHERE task_key = 'grade_do' AND current = 1;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 6 WHERE task_key = 'grade_get' AND current = 1;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 7 WHERE task_key = 'fetch_culture_pages' AND current = 1;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 8 WHERE task_key = 'grade_like' AND current = 1;
UPDATE agent_task SET task_group_name = 'Gaze Review', task_group_order = '4000', task_seq = 9 WHERE task_key = 'analysis_upshot' AND current = 1;
UPDATE agent_task SET task_group_name = 'Meteorite Review', task_group_order = '4500', task_seq = 1 WHERE task_key = 'gaze_email' AND current = 1;
UPDATE agent_task SET task_group_name = 'Meteorite Review', task_group_order = '4500', task_seq = 2 WHERE task_key = 'meteorite_email' AND current = 1;
UPDATE agent_task SET task_group_name = 'Meteorite Review', task_group_order = '4500', task_seq = 3 WHERE task_key = 'qualify_meteorite' AND current = 1;
UPDATE agent_task SET task_group_name = 'Meteorite Review', task_group_order = '4500', task_seq = 4 WHERE task_key = 'evaluate_meteorite' AND current = 1;
UPDATE agent_task SET task_group_name = 'Meteorite Review', task_group_order = '4500', task_seq = 5 WHERE task_key = 'meteorite_like' AND current = 1;
UPDATE agent_task SET task_group_name = 'Meteorite Review', task_group_order = '4500', task_seq = 6 WHERE task_key = 'meteorite_upshot' AND current = 1;
-- optional: live DB still on parse_meteorite_email (pre-rename)
UPDATE agent_task SET task_group_name = 'Meteorite Review', task_group_order = '4500', task_seq = 2 WHERE task_key = 'parse_meteorite_email' AND current = 1;
COMMIT;

-- verify
SELECT task_key, task_group_name, task_group_order, task_seq
FROM agent_task
WHERE current = 1
  AND task_group_name IN ('Gaze Review','Meteorite Review','Job Review')
ORDER BY CAST(task_group_order AS INTEGER), task_seq;
```

Note: later `origin/dev` merges rewrote `data/admin/agent_task.json` back to **Job Review**; the SQL matches the epic ftr tip. No UAT Bug children filed — this was a manual-apply ask, not a plan→qa fix wave.

— Chuckles

#### susan — 2026-08-07T22:49:19.657Z
Please give me copyable SQL `update agent_task` statements to effect these cosmetic changes.  We did a lot of prompt rework while this was in flight, so I'll just run it manually.

#### chuckles — 2026-08-06T08:14:35.631Z
[refresh-ftr] blocked: merge origin/dev into origin/ftr/AST-1183-gaze-review-rename-meteorite-review-sibling failed.

Conflict files:
- `docs/uat-fixtures/AST-756/expected-agent_task.json` — @Hedy Lamarr (product/docs fixture; meteorite grouping tip) / @Ada Lovelace (Gaze Review rename rows)

— Chuckles

#### chuckles — 2026-08-06T02:33:44.995Z
@susan

1. Confirm Meteorite Review membership: `gaze_email`, `parse_meteorite_email`/`meteorite_email`, `qualify_meteorite`, `evaluate_meteorite`, `meteorite_like`, `meteorite_upshot` — and that Gaze Review keeps only the classic gaze/GDL set in the Description.
2. Confirm section order: Gaze Review keeps order `4000`; Meteorite Review sits between Gaze Review and Job Artifacts at order `4500` (sibling panel, not nested).

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
