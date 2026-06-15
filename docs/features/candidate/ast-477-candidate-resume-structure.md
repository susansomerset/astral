# AST-477 — Candidate Resume Structure

<!-- linear-archive: AST-477 archived 2026-06-15 -->

## Linear archive (AST-477)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-477/candidate-resume-structure  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** susan  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-533; related: AST-537; related: AST-313; blocks: AST-300

### Description

## Purpose

Candidates need different resume section layouts (titles, order, which sections exist) without forking the product per person. Today the Base Resume Content UI and job-tailored resume artifacts assume a single global section catalog (`base_resume_structure` in config). That forced heavy per-job pipeline work (AST-300/301) before the product model was right.

This feature defines a **candidate-owned resume structure** stored on the candidate record. The same structure drives (1) tabs on **Base Resume Content**, (2) keys/shape for `candidate_data.artifacts.base_resume`, and (3) keys/shape for `job_data.artifacts.resume_content` — one catalog, two content blobs (base vs job-specific), render-time HTML from templates plus JSON (no per-job HTML files).

## Functional scope

* **Per-candidate section catalog:** Ordered list of sections each candidate uses (stable section id, display title, enabled/disabled). Candidate and/or assisted setup (AI) can define titles and which sections apply; structure persists on the candidate.
* **Single structure, two content surfaces:** `base_resume` and per-job `resume_content` use the **same section ids**; only the text/content differs. Job artifacts never introduce section keys the candidate structure does not define.
* **Base Resume Content UI:** Side tabs / editor fields are generated from the candidate’s structure (not a global fixed nine-field list). Accent/highlight and other presentation tokens that belong at candidate level are owned here or referenced from structure metadata as Susan specifies during review.
* **Downstream alignment:** Resume HTML builder, agent task response shapes, and BUILD_CONFIG artifact shape docs must consume the candidate structure (or a resolved view of it), not a hardcoded global list.
* **Migration path:** Existing candidates with legacy `base_resume` keys or global-shape data remain editable or migratable without silent data loss (exact migration rules in open questions).

## Boundaries

* Does **not** implement the full [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) daisy-chain resume pipeline or per-job cover-letter epic ([AST-301](https://linear.app/astralcareermatch/issue/AST-301/build-cover-letter-artifact) canceled). Those re-scope after this definition is approved.
* Does **not** replace [AST-302](https://linear.app/astralcareermatch/issue/AST-302/job-state-machine-artifacts-and-candidate-states) job state machine (Done) — states and artifact save helpers remain; may adjust transitions only if definition requires.
* Does **not** author Manage Tasks prompts ([AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)) or HTML template typography (builder/CSS) beyond what structure metadata requires.
* Does **not** store rendered HTML per job on disk or in DB — JSON content + template render only.
* Cover letter may remain a separate small shape (`re_line`, `body`, `signature`) unless Susan folds cover blocks into structure in review.

## Acceptance criteria

1. A test candidate can have a custom section list (e.g. three sections with custom titles) saved on their record.
2. Base Resume Content shows one tab per enabled section for that candidate, in defined order.
3. When job-level `resume_content` exists, its keys are a subset of the same section ids; builder/UI do not show orphan keys.
4. A second candidate with a different section catalog does not affect the first.
5. Documentation in the ticket Description (post-approval) is sufficient for dispatch into child implementation tickets without re-deciding section ownership.

## Dependencies and blockers

* [AST-302](https://linear.app/astralcareermatch/issue/AST-302/job-state-machine-artifacts-and-candidate-states) (Done): artifact persistence helpers and candidate/job states — consume, do not redo.
* **Related:** [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) (resume artifact pipeline — blocked until this structure is approved and dispatched), [AST-301](https://linear.app/astralcareermatch/issue/AST-301/build-cover-letter-artifact) (canceled — architectural pivot), [AST-302](https://linear.app/astralcareermatch/issue/AST-302/job-state-machine-artifacts-and-candidate-states).
* [AST-296](https://linear.app/astralcareermatch/issue/AST-296/add-build-config-to-configpy) BUILD_CONFIG and [AST-294](https://linear.app/astralcareermatch/issue/AST-294/build-builderpy-resume-and-cover-letter-renderer) builder already on dev — structure work must align keys with those contracts or include explicit migration tickets.

## Open questions

1. Where does structure live in `candidate_data` (new `resume_structure` blob vs extend `artifacts`)?
   1. Extend Artifacts
2. Initial structure: default template for new candidates, clone from parse_resume output, or AI-assisted interview flow?
   1. instruct agent to include structure in craft_base_resume task response
3. Migration for existing `base_resume` objects keyed to global `base_resume_structure`?
   1. I think we can just regenerate the base resume content for existing candidates, no automated migration
4. Are contact/header fields (`candidate_name`, etc.) part of structure sections or fixed profile fields outside the catalog?
   1. They are part of the structure, but they are not editable by job_resume crafting agents.  However, they should be saved in the job_data so that if the candidate changes their contact info, they can see which contact info was included with the job resume.
5. Accent/highlight color: field on structure, on `base_resume`, or profile — single source for builder merge?
   1. Field on Structure
6. Cover letter: separate artifact shape forever, or optional “cover sections” in the same catalog?
   1. For now, same artifact shape forever, but it should be "Subject" and "Letter" so that the agent can specify the subject line.

---

## Original brief

Susan (2026-05-25): Create **Candidate Resume Structure** under **Astral Candidate** (not “format”). Drives tabs on **Base Resume Content** UI. Not a small ticket — define, then relate to [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact), [AST-301](https://linear.app/astralcareermatch/issue/AST-301/build-cover-letter-artifact), [AST-302](https://linear.app/astralcareermatch/issue/AST-302/job-state-machine-artifacts-and-candidate-states). Structure is always consistent between base and job-specific resume content; different candidates may have different sections. Cancel [AST-301](https://linear.app/astralcareermatch/issue/AST-301/build-cover-letter-artifact) family; keep [AST-302](https://linear.app/astralcareermatch/issue/AST-302/job-state-machine-artifacts-and-candidate-states) Done.

### Comments

#### chuckles — 2026-06-01T00:04:29.226Z
[check-linear]

**@susan** — AST-477 inbox pass (2026-05-31). Ready for another UAT round.

**Resolved on local `dev` @ `ba798d88`** (restart app from `/Users/susan/chuckles/astral`):

| UAT report | Fix | SHA |
|------------|-----|-----|
| `craft_resume_base` — Missing `candidate_name` | **AST-536** — `normalize_craft_resume_base_agent_payload` before schema validation (`candidate.py` + `agent.py`) | `d38b2b28` |
| `gaze` / `recheck_no_openings` — `No agent_task row` in dispatcher thread | **AST-533** hotfix — `_current_agent_task_run_next` uses `get_agent_task` only; returns `''` when row missing | `ba798d88` |

**`origin/ftr/AST-477-candidate-resume-structure`** remains @ `d38b2b28` (resume epic tip). Gaze guard lives on integration **`dev`** with AST-533 merge; not required on the ftr tip for resume-structure ACs.

**Children:** **AST-517** / **AST-518** / **AST-519** still **User Testing**; **AST-536** **Done**.

**Parent:** moved **UAT Concern → User Testing** (assignee stays you).

**Retest (resume epic):** Radia checklist in thread @ `24697f3d` — steps 1–11 (structure tabs, Generate, accent on structure, job key subset). Step 1 should pass after restart.

**If Generate still fails:** paste latest execution-history `agent_payload` JSON snippet.

**Dispatch noise:** **AST-537** tracks fuller regression tests for roster keys without `agent_task` rows.

— Chuckles

#### chuckles — 2026-05-31T22:53:10.070Z
[check-linear]

**@susan** — your **`gaze`** traceback is the same **AST-531** regression as **AST-533** (`_current_agent_task_run_next` required an `agent_task` row). **`gaze`** is a roster dispatch key, not a `TASK_CONFIG` / Manage Tasks key.

**Hotfix:** landed with **AST-533** triage — see **[AST-533](https://linear.app/astralcareermatch/issue/AST-533)** latest `[check-linear]` (`agent.py` + minimal test). Restart app and retry **gaze**.

**Test coverage ticket:** **[AST-537](https://linear.app/astralcareermatch/issue/AST-537)** filed under **AST-533** for fuller dispatch regression tests (your request for stubbed AI path).

— Chuckles

#### susan — 2026-05-31T22:45:57.770Z
@chuckles tasks are still failing:

```
[gaze] thread exited and cleared from registry
Exception in thread astral-task-5-gaze:
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/lib/python3.12/threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/lib/python3.12/threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 513, in _task_thread_target
    loop.run_until_complete(_dispatch_one(task))
  File "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/base_events.py", line 691, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/dispatcher.py", line 375, in _dispatch_one
    has_run_next_chain = bool(_current_agent_task_run_next(task_key))
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 1686, in _current_agent_task_run_next
    _, row = _resolve_task_prompts(task_key)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 317, in _resolve_task_prompts
    raise ValueError(f"No agent_task row for '{task_key}'. Run sync_agent_tasks or configure via Manage Tasks.")
ValueError: No agent_task row for 'gaze'. Run sync_agent_tasks or configure via Manage Tasks.
```

Fix this, then create another ticket to figure out how we can catch issues like this in the tests, if we need to stub an endpoint to mimic the AI call/response.

#### chuckles — 2026-05-31T22:40:40.702Z
[check-linear]

**@susan** — hotfix executed per your 2026-05-31 request.

- **Ada** shipped **AST-536** → `origin/ftr/AST-477-candidate-resume-structure` @ **`d38b2b28`** (`normalize_craft_resume_base_agent_payload` in `candidate.py`; wired in `agent.py` before schema validation).
- Local **`dev`** fast-forwarded to **`d38b2b28`** — restart the app and retry **Generate** on Base Resume Content.
- **AST-536** → **Done** (Ada comment on thread with SHA).

If validation still fails, paste the latest `agent_payload` snippet from execution history and we’ll extend the flatten paths.

— Chuckles

#### ada — 2026-05-31T22:40:16.262Z
**AST-536 hotfix published** — `d38b2b28` on `origin/ftr/AST-477-candidate-resume-structure`

Flatten nested section strings from `resume_structure` (section `content` / `resume_structure.content` / sibling content dicts) onto top-level `agent_payload` keys before `craft_resume_base` schema validation. `TestAst517ResumeStructure` green (29 tests).

#### susan — 2026-05-31T22:37:40.957Z
@chuckles Please execute the hot fix.

#### chuckles — 2026-05-31T19:54:34.878Z
[check-linear] Correction: UAT sub-issue is **AST-536** (not AST-534). — Chuckles

#### chuckles — 2026-05-31T19:54:30.471Z
[check-linear]

**@susan** — re your UAT log (`Missing required field 'candidate_name'` on **craft_resume_base**):

**Diagnosis:** Validation in `src/core/agent.py` runs on the **`agent_payload`** envelope *before* `split_craft_resume_base_payload` in `candidate.py`. `TASK_CONFIG["craft_resume_base"]` still marks **`candidate_name`**, **`candidate_title`**, **`candidate_contact_detail`**, and body sections as **`required: True`** at the top level (`config.py` ~L88–97). DeepSeek returned a large JSON payload that likely put contact text only inside **`resume_structure.sections`** (or omitted flat keys), so validation failed even though structure parsing would have worked.

**Recommendation:** Small **AST-517** hotfix, not a new epic child — I filed **[AST-534](https://linear.app/astralcareermatch/issue/AST-534)** (Backlog, Ada): pre-validate normalization **or** prompt alignment. Parallel track: refresh **craft_resume_base** prompt in Manage Tasks so the model must emit flat keys **and** `resume_structure` in `agent_payload`.

**Scope:** Inbox otherwise quiet on **AST-477** / children (**517–519** User Testing); no `[qa-handoff]`, no engineer @-mentions needing reply.

— Chuckles

#### susan — 2026-05-31T19:15:24.799Z
Got this in the log:
LLM deepseek task=craft_resume_base 220.8s stop=end_turn tokens in=12915 out=12779

do_task validation failed. task_key='craft_resume_base' error=Missing required field 'candidate_name'

artifact generation failed task_key='craft_resume_base' batch_id=user-craft_resume_base-e60f3c9d-3009-4ac9-8cdf-6f8d4f21ef0d error=Missing required field 'candidate_name'

Is this a quick fix, @chuckles? or should we create a new subissue?  the problem may be in the craft prompt, itself.

#### chuckles — 2026-05-29T03:54:14.546Z
## Manual test steps

**Prereq:** Local `dev` @ `00a8a4e1` (prep-uat merge). Restart app if already running.

### AST-517 — structure + craft_resume_base
1. Pick or create a test candidate. Run **craft_resume_base** (or parse resume flow) so the agent returns `resume_structure` + section content.
2. In DB or admin candidate JSON, confirm `artifacts.resume_structure` exists with ordered sections (ids, titles, enabled, `job_agent_editable` false on contact trio).
3. Confirm `artifacts.base_resume` keys match enabled section ids only.
4. Repeat with a **second** candidate using a different custom section list — confirm catalogs do not bleed across candidates (AC 1, 4).

### AST-519 — Base Resume Content UI
5. Open **Base Resume Content** for candidate A — tabs match **enabled** sections in structure order; labels match structure titles (AC 2).
6. Save content; PUT must not persist keys outside structure (try legacy orphan key in API if handy — should strip on save).
7. Change accent swatch — confirm `artifacts.resume_structure.accent_color` updates (not `base_resume.accent_color`).
8. Switch to candidate B — different tab set (AC 4).

### AST-518 — builder + job artifacts
9. For a job with `resume_content`, confirm keys are subset of candidate section ids; no orphan section in rendered resume HTML (AC 3).
10. Save job cover letter with **Subject** / **Letter** (legacy `re_line`/`body` still accepted on read if old data exists).
11. Contact/header sections on job snapshot: job resume shows contact frozen at save time when candidate contact later changes (AC parent Q4).

### Regression spot-check
12. Run bible §7.13zl narrowed manifests (Betty) — all green on `ftr` @ `24697f3d`.

**Note:** Full `run_component_tests.sh` on `ftr` reports ~75 failures from **orphan cross-epic test classes** on the rollup (AST-513/504/507/etc.) without matching product on the feature tip — not AST-477 manifest failures. Track cleanup separately.

`origin/ftr/AST-477-candidate-resume-structure` @ `24697f3d` · local `dev` merged (§8). Child `sub/*` deleted.

Reset after UAT: `git fetch origin && git reset --hard origin/dev` (only if you have not committed other work on `dev` you need to keep).

## Radia UAT reality-check — `origin/ftr/AST-477-candidate-resume-structure` @ `24697f3d`

**Scope:** Parent AST-477 + children AST-517, AST-518, AST-519 vs composite ftr.

### Parent acceptance criteria
| Criterion | Verdict |
|-----------|---------|
| 1 Custom section list saved on candidate | PASS |
| 2 Base Resume tabs per enabled section, order | PASS |
| 3 Job resume_content keys ⊆ structure; no orphans | PASS |
| 4 Second candidate isolated catalog | PASS |
| 5 Definition sufficient for dispatch | PASS (done) |

### Child stage checklist
**AST-517:** PASS — storage, craft_resume_base schema, parse persist.
**AST-518:** PASS — builder order, tracker filter, Subject/Letter shims.
**AST-519:** PASS — GET resume_structure, UI tabs, accent on structure.

### Issues → sub-issues
| Sev | Topic | Action |
|-----|-------|--------|
| discuss | Orphan pytest classes on ftr from other epics | Backlog cleanup — strip or relocate before next full-suite gate |
| advisory | Full suite not green on ftr tip | Use §7.13zl narrowed runs for this epic |

**Counts:** fix-now **0** · discuss **1** · advisory **1**

— Radia (via Chuckles orchestration)

— Chuckles

#### chuckles — 2026-05-29T00:11:26.937Z
Rollup unblocked: Betty reconciled bible + `test_candidate.py` on **AST-518** / **AST-519** publish refs; **518 → 519** merged onto `origin/ftr/AST-477-candidate-resume-structure` @ `24697f3d` (§7.13zl cumulative; all three `TestAst*` classes on ftr).

Ready for **prep-uat** when you want local `dev` + parent **User Testing**.

— Chuckles

#### chuckles — 2026-05-28T23:31:52.376Z
@susan **rollup-child blocked** after AST-517 merged onto `origin/ftr/AST-477-candidate-resume-structure` @ `541e5e55`.

**AST-518** / **AST-519** sub → ftr merges conflicted:
- `docs/ASTRAL_TEST_BIBLE.md`
- `tests/component/core/test_candidate.py`

Children are **User Testing**; prep-uat not run. Options: Betty bible chain on 518/519 publish refs then re-rollup, or Susan resolves ftr merge.

— Chuckles

#### hedy — 2026-05-28T23:26:31.685Z
[check-linear]

**Session scope:** Parent **AST-477** / Astral Candidate — assigned child ids **(none)** for Hedy.

**§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@hedy` team search (250, no status filter); Astral Candidate `@hedy` query — union is historical branch-name hits, not comment @-mentions. **14d** fallback scan: no `@hedy` in recent Team Astral comment bodies.

**§1:** Assignee-me in **Astral Candidate** — **0** tickets (children **AST-517** / **AST-518** → Ada, **AST-519** → Katherine).

**§2:** Full threads on **AST-477**, **AST-517**, **AST-518**, **AST-519** — **0** actionable comments for Hedy (latest activity: Chuckles git table, Betty QA manifests, Ada/Katherine plan/build notes; no `@hedy` or directed-at-Hedy replies after prior agent passes).

**Pipeline:** Inbox quiet; no plan/build/test/resolve work this pass (happy path).

#### ada — 2026-05-28T23:26:17.029Z
[check-linear]

**Session scope:** Parent **AST-477** / Astral Candidate — assigned **AST-517**, **AST-518**.

**§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b / §1:** `@ada` issue search (team + Astral Candidate project); assignee-me union includes **AST-517**, **AST-518**, **AST-513**, and historical hits. Full threads on **AST-517**, **AST-518**, **AST-477**, **AST-513**.

**§2:** **0** actionable comments — Betty’s QA manifests on **AST-517** / **AST-518** (post-Ada plan) do not `@ada` or request engineer reply; both tickets are **Tests Passed**. No thread nags or `@ada` replies needing code/doc fix.

**Pipeline:** Inbox quiet per check-linear §5. Next gate: Radia **`review-astral`** on **Tests Passed** (not engineer stage from this pass).

#### betty — 2026-05-28T23:25:19.680Z
[check-linear]

**Session scope:** Parent **AST-477** / Astral Candidate — assigned **AST-517**, **AST-518**, **AST-519**.

**§0a:** `dev-betty` @ `/Users/susan/chuckles/astral-betty`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b / §1:** `@betty` team search + Astral Candidate project union; assignee-me in session project. Full threads on **AST-517**, **AST-518**, **AST-519**, **AST-477** — **0** actionable comments (no `@betty` or directed-at-Betty replies after prior QA manifests).

**§5b:** Scanned assigned ids for **Tests Ready** + latest comment **`[qa-handoff]`** — none qualify (**AST-517**, **AST-518**, **AST-519** are **Tests Passed**; engineers Ada/Katherine own review stage). Team-wide **Tests Ready** in Astral Candidate: **0**. No handoffs to clear.

**Pipeline:** Inbox quiet; no manifest/test/bible work this pass.

#### ada — 2026-05-28T23:03:28.627Z
[check-linear]

**Session scope:** Parent **AST-477** / Astral Candidate — assigned **AST-517**, **AST-518** (publish refs per Chuckles git table).

**§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b / §1:** `@ada` issue search (team + Astral Candidate project); assignee-me in project. Union includes **AST-517**, **AST-518**, **AST-513**, and other historical @-mention hits.

**§2:** Full threads on **AST-517**, **AST-518**, **AST-477**, **AST-513** — **0** actionable comments after Ada’s plan posts (no `@ada` or directed-at-Ada replies needing code/doc fix). **AST-517** / **AST-518** remain **Plan Approved**; no thread nags.

**Pipeline:** No engineer stage work from this pass (inbox quiet per check-linear §5).

#### chuckles — 2026-05-28T22:57:48.118Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-477 (parent) | ftr/AST-477-candidate-resume-structure |
| AST-517 | sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base |
| AST-518 | sub/AST-477/AST-518-resume-builder-and-job-artifact-keys-from-candidate-structure |
| AST-519 | sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure |

**blockedBy:** AST-518, AST-519 → AST-517

— Chuckles

#### chuckles — 2026-05-25T01:23:54.720Z
Definition draft ready for review. Key decisions made:
- Per-candidate section catalog replaces global `base_resume_structure` as the driver for Base Resume Content tabs and job `resume_content` keys
- Same section ids for base vs job-specific content; HTML is render-time only
- **AST-300** blocked until this is approved/dispatched; **AST-301** family canceled per Susan pivot

**6 open questions** in Description (storage path, migration, contact fields, accent, cover letter scope).

Please review the Description and comment with changes or approval.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
