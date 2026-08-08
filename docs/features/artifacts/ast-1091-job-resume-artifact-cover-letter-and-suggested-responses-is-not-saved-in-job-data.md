# AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data

<!-- linear-archive: AST-1091 archived 2026-08-07 -->

## Linear archive (AST-1091)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The build-artifacts daisy chain already stores hop responses in `agent_data`, but nothing on the job points at the published resume / cover letter / suggested-answers hops — so JAR and candidate review have no artifact to open even when the chain succeeded. This epic pins each published hop by saving that hop's `agent_data_id` under `job_data.artifacts`, using the same core before/after-`do_task` persist style already used elsewhere — not a new TASK_CONFIG `persist_in` dialect and not a second copy of the response body on the job row.

## Functional scope

After a successful `finalize_job_resume` hop for a job, `job_data.artifacts.job_resume` holds that hop's RESPONSE `agent_data_id` (whether or not `run_next` continues).

After a successful `finalize_cover_letter` hop for a job, `job_data.artifacts.cover_letter` holds that hop's RESPONSE `agent_data_id` (whether or not `run_next` continues).

After a successful `propose_application_responses` hop for a job, `job_data.artifacts.proposed_answers` holds that hop's RESPONSE `agent_data_id`.

Core components that already know the job and the hop outcome (before/after `do_task`, same spirit as existing consult/candidate persist) perform the write — not a new generic TASK_CONFIG destination field, and not duplicating the parsed JSON into `job_data`.

Readers that need the artifact body load `agent_data` by the stored id (existing agent_data read paths). Surfaces that show these three artifacts for UAT resolve through those ids.

Failed hops do not write or clear a good prior id with an empty value. When `debug=True` on the touched persist path, log which key was written and which `agent_data_id` was recorded (or why skipped).

## Architectural definition

* **Patterns to reuse**
  * `pattern.batch.entity-agent-responses` — RESPONSE rows in `agent_data` remain the content store; `job_data.artifacts.*` holds a pointer (`agent_data_id`), not a revived entity JSON `agent_responses` blob.
  * `pattern.layers.import-discipline` — core decides when to pin; data layer saves job_data / reads agent_data.
  * `pattern.config.config-block` — task keys and artifact slot names stay config/convention aligned; no new `persist_in` field.
* **New patterns proposed** — none. Explicit choice: do **not** introduce TASK_CONFIG `persist_in`.
* **Applicable statutes**
  * `astral.batch.entity-agent-responses-latest-only` — pin by `agent_data_id`; do not restore entity-row `agent_responses` mirrors.
  * `astral.standards.in-scope-only` — only the three artifact pointer slots + the core write path that sets them + reader resolve needed for UAT of those slots.
  * `astral.standards.dry-and-focused-functions` — extend existing post-`do_task` / tracker job_data merge patterns; no parallel persist framework.
  * `astral.standards.debug-contract-gated` / `astral.standards.logging-via-utils` — Style D found/recorded when `debug=True`.
  * `astral.standards.data-raises-caller-logs` — data raises; core logs.
  * `astral.patterns.coat-check-never-store-empty` — do not store empty ids.
  * `astral.layers.import-direction` — UI → core → data.

## Boundaries

Does not add TASK_CONFIG `persist_in` (or any new task-level destination dialect).
Does not migrate `save_prefix` grade writes, candidate craft persists, or `analysis_upshot` one-offs onto a shared config field.
Does not copy full hop JSON into `job_data.artifacts` for these three slots — pointer only.
Does not redesign Manage Tasks `run_next` graphs or rename task keys.
Does not change session cover letter / session resume paste.
Does not reintroduce entity JSON `agent_responses` columns.
Does not require changing unrelated JAR tabs or Materials Preview beyond resolving these three pointers for display/UAT.
Does not alter graduation to CANDIDATE_REVIEW beyond what is required so pin writes stay consistent with a successful chain.

## Acceptance criteria

1. After a successful `finalize_job_resume` hop (chain may continue), `job_data.artifacts.job_resume` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.
2. After a successful `finalize_cover_letter` hop (chain may continue), `job_data.artifacts.cover_letter` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.
3. After a successful `propose_application_responses` hop, `job_data.artifacts.proposed_answers` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.
4. A full successful daisy-chain that ran those three hops leaves all three pointer keys set; UAT surfaces that show Job Resume / Cover Letter / suggested answers resolve content via those ids without a manual PUT of the response body.
5. When `debug=True` on the touched persist path, each pin attempt logs key + `agent_data_id` (or skip reason); no new ungated `[DEBUG]` spam.
6. Failed or empty hops do not overwrite a good prior pointer with a blank value.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **Pin agent_data_id on job artifact slots after chain hops - Ada**

After successful `finalize_job_resume` / `finalize_cover_letter` / `propose_application_responses`, core (existing before/after-`do_task` persist style — not a new TASK_CONFIG field) writes `job_data.artifacts.job_resume` / `cover_letter` / `proposed_answers` as that hop's RESPONSE `agent_data_id`, including mid-chain when `run_next` continues. Debug found/recorded. Does not own JAR/UI resolve (#2).
**Citations:** `pattern.batch.entity-agent-responses`; `astral.batch.entity-agent-responses-latest-only`; `astral.patterns.coat-check-never-store-empty`; `astral.standards.debug-contract-gated`.

#### 2: **Resolve artifact bodies from pinned agent_data_id for UAT surfaces - Katherine**

Job Resume / Cover Letter / suggested-answers surfaces used in UAT load body content via the pinned `agent_data_id` on `job_resume` / `cover_letter` / `proposed_answers` (existing agent_data read paths). After #1.
**Citations:** `pattern.batch.entity-agent-responses`; `astral.layers.import-direction`; `astral.standards.in-scope-only`.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1091 (parent) | ftr/ast-1091-job-artifact-agent-data-pins |
| AST-1099 | sub/AST-1091/AST-1099-pin-agent-data-id |
| AST-1100 | sub/AST-1091/AST-1100-resolve-artifact-agent-data-id |
| AST-1116 | sub/AST-1091/AST-1116-cover-letter-field-defs |
| AST-1117 | sub/AST-1091/AST-1117-print-html-blobs |

* **AST-1116**: `sub/AST-1091/AST-1116-cover-letter-field-defs`
* **AST-1117**: `sub/AST-1091/AST-1117-print-html-blobs`

**Epic worktree:** `astral-AST-1091/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/5cc13278acb42d57019f3a6acc37a0d1/4fbb7a4e-78d7-4a01-bbe4-bcd5eec832ae/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/5cc13278acb42d57019f3a6acc37a0d1/d932eeee-45b9-4c9f-974b-524b195226a8/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/6ba8cdd3-ed3e-4ede-ac86-3c9a79eda600/store.db` |
| Radia | review | `/home/susan/.cursor/chats/5cc13278acb42d57019f3a6acc37a0d1/fbc84242-cfa3-42cc-8c8e-d4d51784a73d/store.db` |

---

## Original brief

The daisy chain is working great, but the responses are not saved to job_data.

### Comments

#### chuckles — 2026-08-01T01:01:46.338Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1116** | Cover Letter preview fails field definitions for cover_letter |
| **AST-1117** | Print Resume and Print Cover Letter open recommended page not HTML |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1116** — _Cover Letter preview fails field definitions for cover_letter_
- **Issue reported:** Previewing the Cover Letter artifact on the recommended/JAR UAT surface shows:
- **Should now:** Cover Letter preview loads field tabs and body content resolved from the pinned `job_data.artifacts.cover_letter` `agent_data_id` (via existing agent_data read paths).
- **Quick check (this fix only):**
  1. Open a recommended job that has completed the cover-letter hop (pin present on `job_data.artifacts.cover_letter`).
  2. Open the Cover Letter artifact / preview tab.
  3. Observe the red error: Failed to load field definitions for "cover_letter".

**AST-1117** — _Print Resume and Print Cover Letter open recommended page not HTML_
- **Issue reported:** Both **Print Resume** and **Print Cover Letter** open new browser tabs that land on the recommended page, not printable HTML blobs for the job resume / cover letter.
- **Should now:** Print Resume / Print Cover Letter open tabs that render the HTML document built from the pinned artifact bodies (`job_data.artifacts.job_resume` / `cover_letter` → `agent_data`), suitable for print/PDF.
- **Quick check (this fix only):**
  1. Open a recommended job whose daisy-chain left resume and cover pins set.
  2. Click **Print Resume** — new tab shows the recommended page, not resume HTML.
  3. Click **Print Cover Letter** — same: recommended page, not cover HTML.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-08-01T00:33:01.004Z
Both "Print Resume" and "Print Cover letter" just open new tabs to the recommended page, not the html blobs.

#### susan — 2026-08-01T00:31:35.803Z
`Failed to load field definitions for "cover_letter".`

When I tried to preview the cover letter artifact.

#### betty — 2026-07-31T06:13:42.310Z
[refresh-ftr] resolved: docs/test-bible/utils/config.md — Betty.

Also resolved sibling conflict `tests/component/utils/test_config.py` (Betty test tree; HEAD empty / origin/dev brought `TestAst1105`) so the merge could complete. Kept ftr AST-1099 + AST-1100 bible sections; retained AST-1105 from origin/dev. Pushed `origin/ftr/ast-1091-job-artifact-agent-data-pins` @ `dcfce070`.

— Betty

#### chuckles — 2026-07-31T06:10:44.813Z
[refresh-ftr] blocked: attempt 1/3

**Betty White (bible/test-tree):**
- `docs/test-bible/utils/config.md`

Merging `origin/dev` → `origin/ftr/ast-1091-job-artifact-agent-data-pins`. Conflict markers only around AST-1099 / AST-1100 epic bible sections (ftr has them; `origin/dev` side empty). Resolve + push reconciled merge commit to `origin/ftr/ast-1091-job-artifact-agent-data-pins` so refresh-ftr can re-run clean.

— Chuckles

#### chuckles — 2026-07-31T05:03:08.671Z
[thread-missing] Cursor chat `7ab26cb8-fe4e-4a56-9f9b-3ac72e62d839` (Katherine · engineer) has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/5cc13278acb42d57019f3a6acc37a0d1/7ab26cb8-fe4e-4a56-9f9b-3ac72e62d839/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

— Chuckles

#### chuckles — 2026-07-31T04:42:08.839Z
[thread-orphan] Joan session `da0027e7-276d-4fe2-a6e6-65c8eb77e24d` found under wrong workspace hash; relocated `/home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db` → `/home/susan/.cursor/chats/5cc13278acb42d57019f3a6acc37a0d1/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db`. Resuming same UUID.

— Chuckles

#### chuckles — 2026-07-31T04:38:23.250Z
[thread-missing] Cursor chat for Ada Team row had no local `store.db` on **chuckles** (prior UUIDs blob-search empty). Minted/resumed new Ada conversation `d932eeee-45b9-4c9f-974b-524b195226a8` and continuing (history from old UUIDs not recovered).

— Chuckles

#### chuckles — 2026-07-31T04:27:48.051Z
@susan Got it — pivoted hard.

Dropped `persist_in` and the debt-migration scope. Definition is now: pin RESPONSE `agent_data_id` on `job_data.artifacts.job_resume` / `cover_letter` / `proposed_answers` via existing core before/after-`do_task` persist style; body stays in `agent_data`. Two children (pin + UAT resolve).

— Chuckles

#### susan — 2026-07-31T04:26:41.168Z
Actually, I'm being wrong-headed about the whole thing.  Just persist the agent_data_id on the job_data.artifacts.{job_resume|cover_letter|proposed_answers}, don't create additional tech debt with persist_in at all, just use the existing patterns for persisting the data from the core components that know what they're doing before and after calling do_task.

#### chuckles — 2026-07-31T04:06:42.022Z
@susan Expanded for the debt pass — not just the three missing artifacts.

Inventory in scope: graded `save_prefix` writes, candidate craft post-`do_task` persists, `analysis_upshot` one-offs. Coat-check/scrape writers stay out.

Two OQs in the Description:
1. Graded map shape (`grades`/`score`/`notes`/`rubric` → keys like `do_grades`)
2. Whether rubric-craft + company-search-terms join `craft_resume_base` in this epic

— Chuckles

#### susan — 2026-07-31T04:04:48.982Z
I think we need to go ahead and identify and resolve the technical debt this introduces.  We have other dispatch task responses that are saved in job_data (grade_do, etc.) and candidate artifacts like craft_base_resume, which should use the persist_in pattern and decommission the explicit setting in the core components.

#### chuckles — 2026-07-31T03:58:32.334Z
@susan Adopted your split and path shape:

1. Two children — #1 TASK_CONFIG `persist_in` declarations only; #2 `agent.do_task` wiring.
2. Parse + persist orchestration: `agent.py`. Write: `database.py` after core shape/coat-check (data stays dumb; no validation in database).
3. Value is relative: `artifacts.resume_content` (not `job_data.…`) — entity from TASK_CONFIG `entity_type`.

OQs cleared. — Chuckles

#### chuckles — 2026-07-31T02:40:09.604Z
@susan Yes — TASK_CONFIG is the right home.

1. Optional persist target on the task (working name `job_artifact_key`) naming the `job_data.artifacts` key. Absent → skip persist, not an error. Same spirit as consult `save_prefix` for grade writes.
2. Not BUILD_CONFIG as a second task→artifact map (dual source of truth). `artifact_shapes` stay shape/writer contracts only.
3. Not `agent_task` DB rows — those own prompts / `run_next`, not product persist.

Definition updated to adopt that; OQ #1 is only the exact field name. — Chuckles

#### susan — 2026-07-31T02:36:39.724Z
Is this an opportunity to use task_config to specify where to save the output, and if it is not specified, that's not an error?  Where else would we make that specification.

---

_Implementation detail may live in git history on `origin/dev`._
