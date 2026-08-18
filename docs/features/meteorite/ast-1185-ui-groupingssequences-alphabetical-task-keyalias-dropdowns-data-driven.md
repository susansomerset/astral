# AST-1185 — UI groupings/sequences + alphabetical task key/alias dropdowns (data-driven)

<!-- linear-archive: AST-1185 archived 2026-08-17 -->

## Linear archive (AST-1185)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1186

### Description

## Purpose

Admin operators need groupings, within-section sequences, and task-key dropdowns to track live `agent_task` / config truth — not parallel hard-coded lists that drift when Meteorite Review, Gaze Review, or task aliases land. This epic is the UI/API honesty pass: confirm section headers and order come from grouping metadata, make every task-key dropdown alphabetical (including alias identities once they exist), and remove extraneous hard-coded sequences so alias-aware config can surface cleanly without UI inventing its own maps.

## Functional scope

* Confirm Admin surfaces that group dispatch/tasks by section (Scheduled Actions, Manage Tasks, and any peer Admin list that already consumes grouping metadata) render section headers and within-section order from `agent_task` grouping fields (`task_group_order`, `task_group_name`, `task_seq`) — not from hard-coded phase/seq inventories or React-only membership lists.
* Wherever Admin UIs present a task-key dropdown (or equivalent select of catalog task keys), populate options from the live catalog covering **all** `agent_task` keys (including `fetch_*` and peers) and sort them alphabetically by **task_key** string, including alias keys once [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key) has made aliases real catalog identities — not by `task_name` / friendly label.
* Audit and remove hard-coded or extraneous task-key lists, section-order lists, or sequence constants on the Admin API and frontend paths that feed those grouping and dropdown surfaces, so membership and order stay data-driven.
* Keep alias handling UI-honest: dropdowns and catalogs show alias identities as selectable keys without the frontend inventing a parallel alias→master map (resolution stays backend/config; this epic only ensures aliases appear and sort cleanly when present).

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — Admin catalog/list endpoints stay thin and auth'd; React renders resolved grouping/catalog payloads.
  * `pattern.config.config-block` — task-key membership and alias identity come from config/DB catalogs, not inline UI sets.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.layers.ui-config-driven-business-logic` — grouping/visibility/order rules resolved before React; no duplicate business lists in the frontend.
  * `astral.standards.no-hardcoded-sets` — no parallel hard-coded task-key or section-order sets on touched Admin paths.
  * `astral.config.config-source-of-truth` — catalog keys and related literals stay config/DB-backed.
  * `astral.ui.frontend-file-placement` — any React fixes stay in prescribed flat page/component locations.
  * `astral.patterns.require-auth-on-protected-endpoints` — Admin catalog endpoints remain `@require_auth`.
  * `astral.standards.in-scope-only` — do not take Gaze/Meteorite seed rename ([AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping)), `master_task_key` runtime ([AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key)), `meteorite_email` rename ([AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks)), or evaluate_meteorite fold-in ([AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check)).
  * `astral.standards.no-cross-contamination` / `astral.layers.import-direction` — honor layer bounds on any API enrichment touched for sorting/catalog honesty.

## Boundaries

* Does **not** rename Job Review → Gaze Review or create Meteorite Review seed membership ([AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping)) — this epic consumes whatever grouping metadata is live.
* Does **not** invent `master_task_key` / alias resolve plumbing ([AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key)) — only ensures aliases appear alphabetically in dropdowns once they exist as catalog keys.
* Does **not** rename `parse_meteorite_email` → `meteorite_email` or change AI payloads ([AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks)).
* Does **not** fold evaluate_meteorite tests/statutes ([AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check)).
* Does **not** change dispatch claim/eligibility, run_next chains, prompts, or scoring behavior beyond catalog presentation and hardcode removal on Admin grouping/dropdown paths.
* Does **not** invent React-only section labels that diverge from `agent_task` grouping metadata.
* Does **not** require changing non-Admin product pages (Jobs boards, Recommended, etc.) unless they expose the same Admin-style task-key dropdowns (default: Admin only — Open question #1).

## Acceptance criteria

* Scheduled Actions and Manage Tasks (and any other in-scope Admin surfaces from Open question #1) show section headers and within-section row order that match live `agent_task` grouping metadata for the keys they display.
* Every in-scope Admin task-key dropdown lists catalog keys alphabetically by task key; after [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key) lands, alias keys appear in that same alphabetical list as first-class options.
* Touched Admin API/frontend paths related to this epic contain no hard-coded task-key membership lists or hard-coded section/sequence inventories that restate grouping already on `agent_task` / config catalogs.
* Changing a row’s grouping metadata (or adding an alias catalog key) changes what operators see on those surfaces without a parallel frontend constant edit for membership or dropdown order.
* Alias → master resolution is not reimplemented in React; UI shows the alias key and relies on backend/config for execution identity.

## Dependencies and blockers

* Related intake: [AST-1181](https://linear.app/astralcareermatch/issue/AST-1181/generate-issues-for-meteorite-changes) (Backlog; out of scope for this define — sibling bullets live on [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks)–[AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check)).
* **Linear blockedBy (Archie):** [AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping) (Gaze/Meteorite Review seed) and [AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key) (alias catalog keys) — this epic waits until both are User Testing or Done before children run.
* Soft awareness: prior Organizing Tasks / Scheduled Actions work (**AST-739** / related) already wires DB grouping into Admin; this epic verifies and closes remaining hardcode/alpha gaps, especially with aliases.
* Sibling tickets [AST-1182](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks), [AST-1186](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check) are adjacent scope only.

## Open questions

none

## Proposed child tickets

#### 1!: **Admin catalog/API hardcode audit + alphabetical task_key lists - Ada**

Owns the inventory and fix on Admin API / enrichment paths that feed grouping metadata and task-key catalogs: remove extraneous hard-coded task lists/sequences on those paths, ensure dropdown consumers get a live catalog sorted alphabetically by task key (aliases included when present). Does **not** own React section rendering or dropdown UX polish (sibling #2). Does **not** implement alias resolve ([AST-1184](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key)) or seed Gaze/Meteorite sections ([AST-1183](https://linear.app/astralcareermatch/issue/AST-1183/gaze-review-rename-meteorite-review-sibling-agent-task-grouping)).
**Citations:** `pattern.ui.admin-endpoint`; `pattern.config.config-block`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.no-hardcoded-sets`; `astral.config.config-source-of-truth`; `astral.patterns.require-auth-on-protected-endpoints`.

#### 2: **Admin UI grouping honesty + alphabetical dropdowns - Katherine**

After #1 (or against the fixed catalog contract): Scheduled Actions / Manage Tasks (and any other in-scope Admin pages) render sections from grouping metadata only, populate task-key dropdowns from the alphabetical catalog (including aliases when present), and drop any remaining React-side hard-coded membership/order lists for those surfaces. Does **not** invent alias→master maps in the frontend. Does **not** own seed section rename or config alias contract.
**Citations:** `astral.layers.ui-config-driven-business-logic`; `astral.ui.frontend-file-placement`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`.

**New patterns:** none.

**Monolith check:** Functional scope has 4 capabilities; 2 children span API/catalog honesty vs React presentation — intentional layer split (not a single mega-ticket).

---

## Original brief

From AST-1181:

* Confirm the UI reflects the groupings and sequences set in the agent_task table, and the UI populates an alphabetical listing of task keys (and aliases) wherever task_keys appear in dropdown lists
* Verify there are no hard-coded or extraneous lists or sequences relating to this; the grouping and ordering should all be data-driven, and the config should handle aliases cleanly

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1185 (parent) | ftr/AST-1185-ui-groupingssequences-alphabetical-task-keyalias-dropdowns |
| AST-1214 | sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists |
| AST-1215 | sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns |

**Epic worktree:** `astral-AST-1185/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/0d3733e86c41a06e8ff65e4be3f9b4b9/5f9cc2e2-5e81-474e-95df-18a4e3c1b6c3/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/0d3733e86c41a06e8ff65e4be3f9b4b9/e551dcc6-3078-4b99-b25c-4a54d9a6f641/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/5224bd60-a6f6-4f0b-bf16-c1394725348b/store.db` |
| Radia | review | `/home/susan/.cursor/chats/0d3733e86c41a06e8ff65e4be3f9b4b9/7bc42baf-d2d6-41b7-a2b1-4f0703dd6b3c/store.db` |

### Comments

#### susan — 2026-08-07T06:09:48.263Z
I have unblocked 1214.

#### chuckles — 2026-08-07T05:56:34.613Z
@susan Wave stopped — AST-1214 Plan Discuss with Joan `[plan-discuss] escalate` (past Plan Discuss cap; child assignee already Susan).

Archie’s no-hide / mailbox-fold call is applied in plan tip `876fdba4`. Joan says green-light these three plan edits to approve:

1. `_dispatch_task_key_form_meta` gate also admits `is_meteorite_email_mailbox_task_key(task_key)` (Done-when vs steps contradiction).
2. Stage 2 step 5 names both Avail sites (`api_admin.py:863–867` and `:886`).
3. Mailbox `trigger_state` shape — Joan recommends trigger-null only (match gaze_email); reject non-empty.

AST-1215 still blocked by AST-1214.

— Chuckles

#### chuckles — 2026-08-07T05:16:34.296Z
[check-linear] Understood and agree — no hide path. `parse_meteorite_email` is misnamed; fold into `meteorite_email` / rename to `catch_meteorite_email` (candidate entity; Avail = Gmail ping; FOR-candidate messages → Ruth live content). Not a separate schedulable gap key. Posted product call on AST-1214 → Ada; parent assignee → Chuckles for datt.

— Chuckles

#### susan — 2026-08-07T04:50:11.251Z
No hiding.  Never hiding.

First, we elected to rename gaze_email to meteorite_email.  parse_meteorite_email is misnamed.  meteorite_email should be a candidate entity type, and the available count is a ping to the astral gmail inbox, and when there are messages FOR THE CANDIDATE named on the dispatch_task record, we just load the emails into live content and send it off to Ruth to parse.  It isn't (and doesn't have to be) a separate task from meteorite_email.  And while we're at it, let's rename it again to catch_meteorite_email.

@chuckles Confirm you understand and agree, then resolve the questions on the blocked child tickets and reset this ticket to yourself to unblock the datt job.

#### chuckles — 2026-08-07T01:33:35.986Z
@susan Wave stopped — AST-1214 Plan Discuss with Joan `[plan-discuss] escalate` (assignee already Susan on the child).

Need your call on `parse_meteorite_email` as an eighth agent_task-only picker key (rename pending AST-1182). Joan’s options on AST-1214: (1) hide via ADMIN_CONFIG, (2) filter picker to helper-resolvable keys, (3) ship the 400. Prefer 1 or 2 before re-Todo + Chuckles.

AST-1215 still blocked by AST-1214.

— Chuckles

#### chuckles — 2026-08-07T00:32:31.564Z
[check-linear] Not ready to test — AST-1214 and AST-1215 still Todo. blockedBy AST-1183/AST-1184 are User Testing (gate cleared) but children never left Todo.

#### chuckles — 2026-08-07T00:32:30.730Z
[check-linear] Yes — linear-chuckles is up. AST-1185 In Progress; children AST-1214/AST-1215 still Todo (no plan/build wave started).

#### susan — 2026-08-07T00:13:46.474Z
@chuckles Are you running?

#### susan — 2026-08-06T15:15:23.587Z
@chuckles is this ready to test?

#### chuckles — 2026-08-06T02:39:06.289Z
@susan Open questions before Todo:

1. Dropdown surface scope: **all Admin task-key selects** vs Scheduled Actions + Manage Tasks only?
2. Soft awareness of AST-1183 / AST-1184, or Linear `blockedBy` until Gaze/Meteorite seed + aliases are live?
3. Confirm dropdown sort by **task_key** string (aliases as themselves), not `task_name`?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
