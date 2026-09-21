# AST-1198 — Rubric criteria prompts are not appearing in UI Artifacts

<!-- linear-archive: AST-1198 archived 2026-08-14 -->

## Linear archive (AST-1198)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1198/rubric-criteria-prompts-are-not-appearing-in-ui-artifacts  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators cannot review or edit rubric criteria prompts on the Artifacts criteria pages even when the candidate has criteria on file. That breaks the edit/regenerate loop for Job List Criteria and the sibling rubric Artifacts pages (same empty chrome, no console error). Restore visible, editable criteria prompts so staging UAT can trust what the product is grading against.

## Functional scope

* When a selected candidate has rubric criteria for an Artifacts criteria page, that page shows each criterion with its prompt text available to read and edit (not header-only chrome).
* The restored visibility applies across the rubric criteria Artifacts pages that share this editor behavior (Job List, Job Description, Meteorite, Company Watch, Get/Do/Like) — not Job List alone.
* Generate/Regenerate and save keep working for those pages; opening a page does not require a console error to explain a blank criteria body.

## Architectural definition

* **Patterns to reuse** — `pattern.ui.admin-endpoint` (authenticated candidate artifact GET/PUT/generate stay thin; display rules resolved server-side or from config, not invented only in React); `pattern.config.config-block` (rubric artifact keys, craft-task mapping, and owner-task mapping remain config-driven).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.layers.ui-config-driven-business-logic` (criteria load/display must not bury source-of-truth rules only in React); `astral.config.config-source-of-truth` (rubric key/task mapping from config); `astral.patterns.require-auth-on-protected-endpoints` (candidate artifact surfaces stay auth-gated); `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.no-cross-contamination`; `astral.standards.no-hardcoded-sets`; `astral.layers.import-direction`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.docs.features-single-file-per-ticket`; `astral.git.engineer-test-tree-ban`; `orch.roles.betty-owns-test-tree`; `orch.pipeline.plan-is-bible`; `orch.roles.engineer-assignee-through-resolve`; `orch.git.ftr-sub-topology`; `orch.git.flow-direction-inviolable`.

## Boundaries

* Does **not** redesign Artifacts nav, criterion editor chrome, or Generate/Regenerate UX beyond restoring missing criteria prompt visibility.
* Does **not** change consult grading, encoded rubric decode, or job-list grade-dot displays (AST-1059 family — already Done).
* Does **not** rewrite Manage Tasks / admin prompt bodies, or invent new rubric criteria for a candidate that has none.
* Does **not** expand into Recommended Job Modal Artifacts tab (job resume / cover letter) — this parent is candidate Artifacts **criteria** pages only.
* Must not break save/hydrate for table-backed rubric criteria (AST-723 era) or craft generate recovery.

## Acceptance criteria

1. For a candidate that has Job List Criteria on file, opening **Artifacts → Job List Criteria** shows each criterion with its prompt text visible/editable — not only the title bar and Regenerate control.
2. The same restored visibility holds for the other rubric criteria Artifacts pages (Company Watch, Job Description, Meteorite, Get, Do, Like) when that candidate has criteria for those pages.
3. Opening those pages produces no console error that is required to explain a blank criteria body.
4. Generate/Regenerate still runs for an eligible candidate state, and Save persists edited criterion prompt text so a reload still shows it.
5. A candidate with genuinely no criteria for a page still gets the empty/editor affordance already intended for that state (not a silent blank page that pretends data exists).

## Dependencies and blockers

none.

## Open questions

none for Archie approval.

## Investigation notes (Chuckles — Discussion triage)

Ordered for the implementer; full thread reply on the `@chuckles` ask.

1. **Likely:** `hydrate_rubric_artifacts_for_response` overwrites Artifacts GET from `rubric_vector`; empty/unbackfilled table → empty editor while legacy blob still has criteria (Susan dump). Verify GET `artifacts.joblist_rubric` vs `rubric_vector` for `somerset` / `qualify_job_listings`.
2. **Possible:** `.dep-page` `height` + `overflow: hidden` clips `.dep-body` (header/Regenerate visible, stack not).
3. **Weaker:** expand-one collapses textareas (`hidden` until expand) — labels should still show.

## Proposed child tickets

#### 1: **Restore rubric criteria prompts on Artifacts pages - Ada**

One vertical slice: find why criterion prompt bodies do not appear on the shared Artifacts criteria editor path and restore load + display so all rubric criteria Artifacts pages show prompts when criteria exist. Does **not** own consult grading, job-list grade chrome, or Manage Tasks prompt prose.
**Citations:** `pattern.ui.admin-endpoint`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.ui.frontend-file-placement`, `orch.roles.betty-owns-test-tree`, `orch.pipeline.plan-is-bible`.

**Monolith check:** Functional scope has 3 capabilities; 1 child is intentional — one inseparable visibility bug on the shared criteria editor wire (response → editor tabs → collapsible prompt body); splitting load vs paint would not give Archie an independently UAT-able slice.

---

## Original brief

Full candidate dump moved to Linear attachment **AST-1198 original brief — full candidate dump** (Description exceeded Linear 250k).

```html
<div class="dep-header"><h1 class="dep-title">Job List Criteria</h1><div class="dep-actions"><button class="dep-btn save" style="margin-right: 8px;">Regenerate</button><span style="font-size: 12px; color: var(--text-muted);"></span></div></div>
```

Same for other rubrics.  no error in the console when the ui page opens.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1198 (parent) | ftr/AST-1198-rubric-criteria-prompts-ui-artifacts |
| AST-1200 | sub/AST-1198/AST-1200-restore-rubric-criteria-prompts |

**Epic worktree:** `astral-AST-1198/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/ef5ba7eb12fa817414b8422f1e933b37/584e7c98-ad4b-4983-8043-77cde181006d/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/33733181-9107-4df3-abc1-bfed5b42cd52/store.db` |
| Radia | review | `/home/susan/.cursor/chats/ef5ba7eb12fa817414b8422f1e933b37/a461aafa-a1f9-420d-8cbf-938abf5b0f43/store.db` |

### Comments

#### chuckles — 2026-08-06T01:16:05.122Z
[check-linear] Canceled — AST-1198 + AST-1200 (real issue: craft generate dies on navigate-away / UI-bound; open a new ticket for that if you want it fixed).

#### susan — 2026-08-06T00:29:27.644Z
@chuckles The issue is that the craft prompts fail if I navigate away while they're running.  it's ui-bound.  Cancel this ticket, please.

#### chuckles — 2026-08-06T00:15:39.715Z
[check-linear] Discussion — code triage for Ada (likely causes, ordered)

**1. Primary suspect — AST-723 hydrate overwrites blob (empty `rubric_vector`)**
- `GET /api/candidates/<id>` calls `hydrate_rubric_artifacts_for_response` (`src/core/candidate.py`), which **unconditionally** sets every key in `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` from `rubric_criteria_for_task` → `rubric_vector` (`current=1`).
- `ArtifactEditor` load (`ArtifactEditor.tsx` candidate effect) reads **only** `candidate_data.artifacts[<artifactKey>]` as an **array** after that hydrate — it never falls back to the legacy blob.
- Susan’s dump still has rich `joblist_rubric` / `do_rubric` / etc. lists **in the blob**, but if staging `rubric_vector` was never backfilled (or was cleared) while the blob still has criteria, GET returns `[]` for those keys and the editor paints empty.
- **Reproduce check:** Network tab on Job List Criteria → GET candidate → length of `candidate_data.artifacts.joblist_rubric` vs SQL `SELECT count(*), sum(length(content)) FROM rubric_vector WHERE candidate_id='somerset' AND task_key='qualify_job_listings' AND current=1`. If GET is `[]` and blob/table disagree, fix hydrate (blob fallback when table empty) and/or run `scripts/migrations/backfill_rubric_vectors.py` for that candidate — do **not** assume the UI alone is broken.

**2. Secondary — `.dep-page` layout can clip the body**
- `.dep-page` is `height: calc(100% - 40px); overflow: hidden; display: flex; flex-direction: column` (`App.css`). Header (`Regenerate`) stays visible; `.dep-body` is `flex: 1; overflow-y: auto`.
- Matches the pasted HTML (header only) **if** criteria tabs exist but the body height collapses. **Reproduce check:** Elements panel → computed height of `.dep-body` / `.artifact-editor-collapsible-stack` while the bug shows.

**3. Weaker — expand-one leaves textareas hidden**
- `resolvedExpandedTabId` starts `""`; `CollapsiblePanel` bodies use `hidden={!expanded}`. Prompt **textareas** stay collapsed until a chevron/label click — but **criterion row labels should still show**. Only treat this as the bug if labels are visible and she means the prompt body text is collapsed.

**4. Not indicated**
- Console errors (Susan: none).
- Manage Tasks / admin prompt prose (different surface).
- Job-list grade-dot chrome (AST-1059 family — Done).

**Dev start here:** confirm GET hydrate payload for `somerset` on one rubric page; branch on empty table vs clipped `.dep-body` before rewriting editor chrome.

— Chuckles

#### susan — 2026-08-06T00:14:23.064Z
@chuckles Let's look more deeply at the code while this ticket is in discussion.  Try to determine the likely issues with the code so that the dev doesn't have to hunt for it from scratch.

#### chuckles — 2026-08-06T00:06:17.271Z
[check-linear] Discussion — dump attached; definition landed; assignee Chuckles

#### susan — 2026-08-06T00:04:15.222Z
@chuckles Yes, please move the dump to a linear attachment, then reassign to yourself.

#### chuckles — 2026-08-06T00:00:29.557Z
@susan

1. AST-1198 Description is already ~322k characters (pasted candidate dump + header HTML). Linear rejects Description updates over 250k, so I cannot prepend the Chuckles definition while that dump stays inline.
2. OK to move the full dump to a Linear attachment and keep only the HTML snippet + your closing note under `## Original brief`, then land the definition?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
