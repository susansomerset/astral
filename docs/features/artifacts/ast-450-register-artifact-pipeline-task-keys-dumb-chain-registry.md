<!-- linear-archive: AST-450 archived 2026-06-23 -->

## Linear archive (AST-450)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** High / 2  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-313; related: AST-300

### Description

## Purpose

Susan authors the resume / cover-letter / application-response pipelines in **Manage Tasks** using `run_next` and chain tokens (`{$CALLER_RESPONSE}`, `{$CACHE_BLOCK_A}`–`D`). The runtime is **dumb**: `do_task` runs one `task_key`, then follows `agent_task.run_next` with pass-through content — **no** ordered step lists, hop counts, or pipeline choreography in code.

Today only three Phase E keys exist (`craft_job_resume`, `craft_job_cover_letter`, `craft_application_responses`), and names/placement do not match the admin chain Susan is building. This ticket adds the **registry** so each hop exists in `TASK_CONFIG` and `sync_agent_tasks` can seed empty `agent_task` rows. [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) (prompt authoring) is blocked until this lands.

## Architectural constraint (non-negotiable)

* **Do not** add `RESUME_PIPELINE_STEPS`, step indices, “8-step” constants, cache-promotion-at-step-N, or any code that encodes chain length or order.
* **Do** register keys + minimal `response_schema` / entity metadata; chain order is **only** `run_next` in the DB (Susan via AdminTaskPrompts).
* **Entry points only** in code: which `task_key` dispatch invokes when a job hits `BUILD_ARTIFACTS` vs `CANDIDATE_REVIEW` (not the full chain).

## Task keys to register

Replace legacy names; each key gets a `TASK_CONFIG` entry and appears in `get_task_keys()` / startup `sync_agent_tasks`.

| Key | Notes |
| -- | -- |
| `contemplate_job` | Resume chain **dispatch entry** at `BUILD_ARTIFACTS` (not step 1 in code — admin wires `run_next`) |
| `advise_job_resume` | Registry only |
| `draft_job_resume` | Replaces `craft_job_resume`; graded/structured schema TBD per product — minimal stub OK |
| `check_job_resume` | Registry only |
| `finalize_job_resume` | Output shape aligns with `BUILD_CONFIG.artifact_shapes.resume_content` when schema is defined |
| `draft_cover_letter` | Replaces `craft_job_cover_letter`; cover-letter object schema per [AST-309](https://linear.app/astralcareermatch/issue/AST-309/cover-letter-artifact-shape-json-object) |
| `check_cover_letter` | Registry only |
| `finalize_cover_letter` | Registry only |
| `propose_application_responses` | Replaces `craft_application_responses`; separate chain entry TBD in dispatch |

Susan’s intended **admin** chain (for prompt authoring in [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring), not for code):  
`contemplate_job` → `guide_resume_revisions` → `draft_job_resume` → `check_resume` → `finalize_job_resume` → … cover hops … → `propose_application_responses` (exact `run_next` wiring is Susan’s job after keys exist).

## Code changes (engineer)

1. `src/utils/config.py` — Add/rename `TASK_CONFIG` entries; remove or alias deprecated `craft_job_*` keys (grep repo; update all references).
2. **Dispatch entry only** — `consult.py` `_INPUT_STATE_TO_TASK` / `_DISPATCH_TASK_SEED`: `BUILD_ARTIFACTS` → `contemplate_job`; `CANDIDATE_REVIEW` → `draft_cover_letter`.
3. `run_*_artifact_chain_for_job` — If `BUILD_CONFIG.*_artifact_chain.first_task_key` remains, point resume entry to `contemplate_job` and cover entry to `draft_cover_letter` (entry key only, not a step list).
4. `database.py` **dispatch seed** — Match trigger_state rows to new entry keys.
5. **Tests** — Update references from `craft_job_resume` / `craft_job_cover_letter`; add smoke that new keys exist in `TASK_CONFIG` and `run_next` validation accepts them.
6. **Do not implement** cache-slot promotion, step-index logic, or pipeline step arrays.

## Cache / chain tokens (context for prompt authors)

No new cache subsystem in this ticket. Per-hop cache control stays: **system_prompt**, **cache_prompt**, **nocache_prompt** on each `agent_task` row; cross-hop pass-through via [AST-304](https://linear.app/astralcareermatch/issue/AST-304/add-parsable-chain-tokens-to-resolve-tokens) tokens. Document in a short comment or [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) thread: child prompts should use `{$CACHE_BLOCK_B/C/D}` **without** duplicating `--- CACHED CONTEXT ---` headers (see [AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task) Radia note).

## Acceptance criteria

* All nine keys above exist in `TASK_CONFIG` and sync to `agent_task` on startup.
* No `craft_job_resume`, `craft_job_cover_letter`, or `craft_application_responses` remain in runtime paths (unless brief alias period is explicitly documented in PR).
* `BUILD_ARTIFACTS` batch starts `contemplate_job`; `CANDIDATE_REVIEW` batch starts `draft_cover_letter`.
* `save_agent_task` / Manage Tasks Run Next dropdown lists all new keys.
* [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) unblocked: Susan can wire `run_next` and author prompts without “task_key not in TASK_CONFIG” errors.
* `python3 -m py_compile` and affected component tests green.

## Out of scope

* Prompt text ([AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring), Susan).
* Persistence / UI for final artifacts ([AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact), [AST-301](https://linear.app/astralcareermatch/issue/AST-301/build-cover-letter-artifact), children) beyond renaming dispatch entry keys.
* Application-response dispatch trigger (register key only unless product specifies trigger state now).

## Relations

* **Blocks:** [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)
* **Related:** [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact), [AST-301](https://linear.app/astralcareermatch/issue/AST-301/build-cover-letter-artifact), [AST-303](https://linear.app/astralcareermatch/issue/AST-303/daisy-chain-task-execution-in-do-task), [AST-304](https://linear.app/astralcareermatch/issue/AST-304/add-parsable-chain-tokens-to-resolve-tokens)

### Comments

#### chuckles — 2026-05-23T19:05:46.246Z
## Landed on origin/dev — Chuckles

- Local `dev` already contained `origin/ftr/AST-450` (prep-uat fast-forward); pushed **`origin/dev`** @ **`b0784a9a`**
- Deleted **`origin/ftr/AST-450`**
- **AST-450** **PR Ready** → **Done** (standalone; no children)

Commits on dev (7): plan, feat, tests, coverage gate, Radia review doc, Resolution section.

**AST-313** prompt authoring is unblocked on registry keys in `origin/dev`.

— Chuckles

#### chuckles — 2026-05-23T18:50:55.039Z
## UAT Ready — Chuckles

Standalone ticket (no child merges). Feature branch **`origin/ftr/AST-450`** @ **`b0784a9a`** is on **local `dev`** in the main worktree (fast-forward).

Restart the app if it is running, then test.

## Manual test steps

1. **Manage Tasks → Run Next dropdown:** All nine keys appear and are selectable: `contemplate_job`, `advise_job_resume`, `draft_job_resume`, `check_job_resume`, `finalize_job_resume`, `draft_cover_letter`, `check_cover_letter`, `finalize_cover_letter`, `propose_application_responses`.
2. **Legacy keys gone:** `craft_job_resume`, `craft_job_cover_letter`, and `craft_application_responses` do **not** appear in Run Next / task config (no runtime path errors when saving a task with a new key).
3. **Dispatch entry — resume:** A job at **`BUILD_ARTIFACTS`** starts the resume chain at **`contemplate_job`** (not `craft_job_resume`). Smoke via batch/dispatch UI or existing consult path you use for artifact builds.
4. **Dispatch entry — cover:** A job at **`CANDIDATE_REVIEW`** starts at **`draft_cover_letter`** (not `craft_job_cover_letter`).
5. **Dumb chain sanity:** Pick any registry-only hop (e.g. `advise_job_resume`), set **`run_next`** to another registered key in Admin — save succeeds (no “task_key not in TASK_CONFIG”). Full prompt content is **AST-313** (out of scope here).
6. **Optional CLI:** `python3 -c "from src.utils.config import TASK_CONFIG; assert set([...nine keys...]) <= set(TASK_CONFIG)"` — or trust component tests if you skip CLI.

**Unblocks:** [AST-313](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring) after you sign off and we **finish-up** to `origin/dev`.

If testing fails on `dev`:
```bash
git reset --hard origin/dev
```

— Chuckles

#### ada — 2026-05-23T18:49:09.541Z
Review feedback resolved. Branch `ftr/AST-450` ready for prep-uat. Commit: `b0784a9a` — ada

Radia thread: fix-now 0; advisory items logged in plan **Resolution** (2026-05-23). Unblocks sibling **AST-313** prompt authoring once **prep-uat** merges children per workflow.

#### radia — 2026-05-23T18:47:59.573Z
**Radia — `review-astral`** after **Tests Passed** (`Team Astral` / **Astral Artifacts**).

**Diff reviewed:** `origin/dev...origin/ftr/AST-450` ending at engineer **`abfdd73aea2e31eeac278bc5a2de202e09f5580b`** (nine-key registry + consult/dispatch/database updates + QA coverage).

**Counts:** fix-now **0** · discuss **0** · advisory **4**

**Combined doc (+ review table):** [ast-450-register-artifact-pipeline-task-keys-dumb-chain-registry.md @ Radia amend `57681373`](https://github.com/susansomerset/astral/blob/57681373/docs/features/artifacts/ast-450-register-artifact-pipeline-task-keys-dumb-chain-registry.md) — **`docs(AST-450): Radia review — artifact registry dumb-chain sign-off`**. Cherry-pick **`57681373`** onto your `dev-<agent>` when convenient (doc-only).

**Accepted / solid:** Nine **`TASK_CONFIG`** keys + **`BUILD_CONFIG`** first hops + **`consult._INPUT_STATE_TO_TASK`** / **`database._DISPATCH_TASK_SEED`** stay aligned with the **no step-list** dumb-chain mandate; **`craft_job_resume` / `craft_job_cover_letter` / `craft_application_responses`** are cleared from **`TASK_CONFIG`** and runtime **`src/*.py`** string literals.

**Engineer-facing advisories:** (see doc table — lazy-import commentary parity vs existing resume lazies; optional strictness reconciliation for **`finalize_job_resume`** stubs vs **`artifact_shapes`**; PEP 479 tick-test housekeeping; historical sibling markdown still referencing legacy names).

**Routing:** **`Review Posted`** — assignee unchanged (**Ada** continues **`resolve-astral`** / cleanups unless she opens a **`[review-handoff]`** thread).

#### ada — 2026-05-23T18:46:44.342Z
**Tests Passed** — Ada (test-astral)

**Publish (Betty QA SHA):** Cherry-picked `132f87c643255ecceddde03aa3098bd4fbc54df7` (`test(AST-450): restore LOCKED branch coverage for component gate`) onto `origin/ftr/AST-450` via pub worktree; pushed tip **`abfdd73aea2e31eeac278bc5a2de202e09f5580b`**.

**Integration:** Local `dev-ada` **`aa611723`** — merge `origin/ftr/AST-450` after fetch (no Ada product commits in this pass).

**Manifest (Betty)**

1. `python3 -m py_compile src/utils/config.py src/core/consult.py src/data/database.py tests/component/utils/test_config.py tests/component/core/test_agent.py` — pass  
2. `pytest tests/component/utils/test_config.py -q -k "Ast450 or Ast309CoverLetter or test_resolves_writing_preferences_from_context or test_resolves_cover_letter_signature_from_profile"` — **5 passed**  
3. `pytest tests/component/core/test_consult.py -q -k "candidate_review_to_cover or Ast371Resume or Ast369CoverLetter"` — **9 passed**  
4. `pytest tests/component/core/test_agent.py -q` — **124 passed**  
5. `./scripts/testing/run_component_tests.sh` — **exit 0** — pytest **834 passed**, **Per-file branch coverage OK (22 locked files)**; Vitest **65 files / 205 tests** passed, **Per-file frontend branch coverage OK**. Full gate first run hit **Vitest** `JobsRecommended` default **120s** timeout under suite load (`waitFor` on skip/API); reran identical command — **green** (**~30s** Vitest phase). Single-file rerun for `test_JobsRecommended.test.tsx` with `ASTRAL_VITEST_MAX_WORKERS=2` **~279ms** — starvation flake, not product.

@Betty White — FYI **JobsRecommended** may need the same per-test/`it(..., timeout)` treatment as AdminScheduledActions if CI sees the long-run flake.

#### betty — 2026-05-23T18:25:12.800Z
**[qa-handoff] — AST-450 (step 5 / `run_component_tests.sh`)**

- `pytest` branch gate: **`check_per_file_coverage.py`** OK — all **LOCKED_AT_100** files at **100%** branch (verified with full `pytest` + checker).
- Frontend: **`vitest run … --coverage`** run with **`ASTRAL_VITEST_MAX_WORKERS=2`** (matching script default); **`check_frontend_coverage.py`** OK. One flaky timeout in `AdminScheduledActions` (“handles empty state”) under parallel suite load — fixed by aligning per-test timeouts to **20s** with siblings.
- **Commit on `dev-betty`:** `132f87c643255ecceddde03aa3098bd4fbc54df7` — cherry-pick into `origin/ftr/AST-450` via pub worktree as usual [[memory: qa-astral]].

Ada: please rerun **`test-astral`**; step 5 should exit **0** once this SHA is on the feature branchstack.

#### ada — 2026-05-23T17:41:41.999Z
[qa-handoff]

@Betty White Re-ran **`test-astral`** manifest on a clean **`origin/dev` → `origin/ftr/AST-450` @ `1d22a1683247f00fddd037c34b4f9b811254f24e`** merge (`_verify-ast450` baseline; same tree as **`ff3d3e28`/`40d6663a`/`1d22a168`** lineage on `ftr`). Local integration branch **`dev-ada`** merge matches your latest test commit (`c518e8fd` merge parent includes `1d22a168`).

**Baseline (skills §§5–6)**

1. `python3 -m py_compile src/utils/config.py src/core/consult.py src/data/database.py tests/component/utils/test_config.py tests/component/core/test_agent.py` — **pass**
2. `pytest tests/component/utils/test_config.py -q -k "Ast450 or Ast309CoverLetter or test_resolves_writing_preferences_from_context or test_resolves_cover_letter_signature_from_profile"` — **5 passed**
3. `pytest tests/component/core/test_consult.py -q -k "candidate_review_to_cover or Ast371Resume or Ast369CoverLetter"` — **5 passed**
4. `pytest tests/component/core/test_agent.py -q` — **120 passed**
5. `./scripts/testing/run_component_tests.sh` — **pytest 799 passed** on pristine merge (**801 passed** after `dev-ada` merge in this tree), **`scripts/testing/check_per_file_coverage.py` exits non-zero** — **coverage gate**, not assertion failures:

```
Per-file branch coverage failures:
  - src/utils/config.py: branch coverage ~98%
  - src/core/tracker.py: branch coverage ~95.7%
  - src/core/consult.py: branch coverage ~96.7%
  - src/core/agent.py: branch coverage ~98.7%
  - src/ui/api/api_candidate.py: branch coverage ~52.3%
  - src/ui/api/api_jobs.py: branch coverage ~94.1%
```

**Why this looks like QA / toolchain or lock expectations**, not an AST-450 product regression:

- **`run_component_tests.sh`** always runs **`check_per_file_coverage.py`** after pytest; **`LOCKED_AT_100`** expects **100% branch** on those modules.
- Harness-only pytest failures from the prior **`[qa-handoff]`** are resolved; **`check_per_file_coverage`** is failing before Vitest (`run_component_tests.sh` stops at Python gate).

**Runner:** Darwin, **Python 3.12.13**, **`coverage` 7.14.0**, **pytest 9.0.3** (project **`.venv`** via `ensure_component_venv.sh`).

Please reconcile (CI vs macOS parity, **`LOCKED_AT_100`** drift, or tests needed for newly counted branches — I cannot edit **`scripts/testing/`** or tests per **`test-astral`**). Post an updated manifest if the gate moves; reassign me when **`Tests Ready`** comes back — I will treat **`Tests Passed`** as blocked until step 5 returns **exit 0** end-to-end.

— Ada

#### betty — 2026-05-23T17:37:50.266Z
Tests updated for `[qa-handoff]`.

Betty synced harness with `process_gazer_batch(..., ctx=...)` callers, PEP 479-safe scheduler tick mocks, JD readiness fixtures that referenced the wrong test class, and `ingest_jobs` count shape (`title_mismatch`). Coat-check `_fetch_website_content` fixture now stubs `save_company_data` so missing DB rows do not explode the first assertion.

Python component suite green here: `./scripts/testing/run_component_tests.sh` — please re-run **`test-astral`** full manifest after pulling **`origin/ftr/AST-450`** (latest test commit **`1d22a168`**).

— Betty

#### ada — 2026-05-23T17:10:16.150Z
[qa-handoff]

@Betty Ran **test-astral** manifest for AST-450 on a clean **`origin/dev` + `origin/ftr/AST-450` @ `40d6663a`** worktree merge (skill §5 baseline).

**Manifest steps 1–4 — pass**
1. `python3 -m py_compile src/utils/config.py src/core/consult.py src/data/database.py tests/component/utils/test_config.py tests/component/core/test_agent.py`
2. `pytest tests/component/utils/test_config.py -q -k "Ast450 or Ast309CoverLetter or test_resolves_writing_preferences_from_context or test_resolves_cover_letter_signature_from_profile"` — 5 passed
3. `pytest tests/component/core/test_consult.py -q -k "candidate_review_to_cover or Ast371Resume or Ast369CoverLetter"` — 5 passed
4. `pytest tests/component/core/test_agent.py -q` — 120 passed

**Manifest step 5 — fail:** `./scripts/testing/run_component_tests.sh` → **5 failed, 794 passed** (same failures on pristine merge tip above).

These look like **test / harness drift on `origin/dev`**, not AST-450 product regressions:

1. **`tests/component/core/test_consult.py` — `TestRemainingConsultBranches`**
   - `test_evaluate_runs_without_rubric_weights`, `test_runs_without_debug_logging`
   - `AttributeError`: `TestRemainingConsultBranches` has no **`_JD_READY_TEXT`**; another class elsewhere defines **`_JD_READY_TEXT`** (~line 1178). Fix: add shared constant / class attribute on **TestRemainingConsultBranches**.

2. **`tests/component/core/test_roster.py` — WATCH branch stubs**
   - `test_watch_and_unhandled_states`, `test_watch_failure_without_error_state`
   - **`TypeError`: `process_gazer_batch()` got unexpected keyword argument `ctx`**
   - **`src/core/roster.py`** calls `process_gazer_batch(..., ctx=ctx)`; inline **`_Gazer`** mocks only accept **`(bid, entities, debug=False)`**. Fix mocks to accept **`ctx`** (or `**kwargs`).

3. **`tests/component/core/test_tracker.py` — `TestIngestJobs::test_counts_new_and_duplicate_rows`**
   - **`ingest_jobs`** return includes **`title_mismatch`**; assertion expects only **`new`** / **`duplicates`**. Fix expectation to match current contract.

**(FYI)** On local **`dev-ada`** before this run, `./scripts/testing/run_component_tests.sh` also failed **`tests/component/core/test_roster.py::TestWebsiteContentBranches::test_handles_missing_culture_links_and_scrape_failures`** (6 failures total); that sixth failure **did not** reproduce on **`origin/dev` + ftr/AST-450** only — likely unpublished integration commits on **`dev-ada`**, not traced here.

Please patch the failing tests / update the bible or gate scope if intentional, post an updated manifest, and reassign me for a re-run.

— Ada

#### betty — 2026-05-23T16:37:50.128Z
QA manifest by Betty.

1. `python3 -m py_compile src/utils/config.py src/core/consult.py src/data/database.py tests/component/utils/test_config.py tests/component/core/test_agent.py`
2. `pytest tests/component/utils/test_config.py -q -k "Ast450 or Ast309CoverLetter or test_resolves_writing_preferences_from_context or test_resolves_cover_letter_signature_from_profile"`
3. `pytest tests/component/core/test_consult.py -q -k "candidate_review_to_cover or Ast371Resume or Ast369CoverLetter"`
4. `pytest tests/component/core/test_agent.py -q` (many `do_task` paths renamed to **`draft_job_resume`** / **`draft_cover_letter`** — run full module)
5. Full gate — `./scripts/testing/run_component_tests.sh` (`test-astral`)

**Tips:** QA commit uses **`TASK_CONFIG`** + tests only; **`origin/ftr/AST-450`** @ **`40d6663a`**.

#### ada — 2026-05-23T16:35:22.421Z
Built by Ada.

**Publish:** `origin/ftr/AST-450` @ `ff3d3e28` (feat commit on feature ref). Matching commit on integration branch `dev-ada`: `315b6e68`.

**Implemented:** Nine `TASK_CONFIG` keys (`contemplate_job` … `propose_application_responses`); removed `craft_job_*` from runtime config. `BUILD_CONFIG` resume/cover chains point at `contemplate_job` / `draft_cover_letter`. `consult._INPUT_STATE_TO_TASK`, `_DISPATCH_TASK_SEED`, `run_consult_task` branches, `_run_cover_letter*` use `draft_cover_letter` / `run_cover_letter_artifact_chain_for_job`. Phase E comment documents cache tokens → AST-313. `sync_agent_tasks` unchanged on startup (`server.py`).

**Betty:** component tests/docs still mention old `craft_job_*` task keys — manifest in plan doc §QA; not edited in this build per `build-astral` test-tree ban.

**Manual note:** `_validate_run_next` / Manage Tasks should accept all nine keys as edge targets (each ∈ `TASK_CONFIG`).

#### ada — 2026-05-23T16:34:06.263Z
Label review (build agent):

Conf: agree — patterns are established; stubs follow Phase E conventions.
Risk: agree — dispatch entry correctness is the main blast radius; Betty’s manifest covers consult paths.
Scope: agree — TASK_CONFIG + consult + dispatch seed + grep-driven updates matches scope-MAJOR-CHANGE.

Built by Ada (label gate complete; proceeding to implementation).

#### chuckles — 2026-05-23T16:31:12.695Z
## Plan Validation — Chuckles

**Verdict: APPROVED**

### Findings

**discuss** — Linear Description vs admin narrative
The ticket table uses `advise_job_resume` / `check_job_resume`; the narrative still mentions `guide_resume_revisions` / `check_resume`. The plan correctly implements **only the nine-key table** and documents the mismatch. Recommend a quick Description edit so **AST-313** and Manage Tasks labels stay consistent (no code change).

**discuss** — Acceptance criteria vs test ownership
Ticket AC says “affected component tests green”; the plan defers test updates to Betty’s post–Code Complete manifest (team rule). That is fine if we read AC as satisfied at **Tests Passed**, not **Code Complete**. Ada should list every `craft_job_*` grep hit in the build comment so Betty’s manifest is complete.

**discuss** — Terminal-hop persistence (existing behavior, not new code)
`do_task` already calls `persist_job_artifact_from_parsed` only when `run_next` is empty and `parsed` matches `resume_content` / `cover_letter` shapes. Susan should end each chain on `finalize_job_resume` / `finalize_cover_letter` (or ensure only those hops emit artifact-shaped JSON). Worth one sentence in **AST-313**; no plan change required.

**acceptable** — `BUILD_CONFIG.first_task_key` only
Entry keys (`contemplate_job`, `draft_cover_letter`) are dispatch/bootstrap, not step choreography. Matches the non-negotiable constraint.

**acceptable** — Stale `agent_task` rows for removed keys
Plan notes old SQLite rows may remain; invalid `run_next` targets fail on save. Susan re-authors in **AST-313**.

### Summary

Plan is faithful to **AST-450**’s definition: nine registry keys, grep migration off `craft_job_*`, dispatch entry updates only, no pipeline step arrays. Layers and config rules look right; self-assessment (`MAJOR` / Medium conf / Medium risk) matches the diff. Safe to build after dispatch comment on `origin/ftr/AST-450` if Susan wants branch hygiene.

— Chuckles

#### ada — 2026-05-23T16:29:02.108Z
Plan ready on `ftr/AST-450`.

**Plan doc:** `docs/features/artifacts/ast-450-register-artifact-pipeline-task-keys-dumb-chain-registry.md`

**GitHub:** https://github.com/susansomerset/astral/blob/ftr/AST-450/docs/features/artifacts/ast-450-register-artifact-pipeline-task-keys-dumb-chain-registry.md

**Self-assessment:**
- **Scope:** `scope-MAJOR-CHANGE` — `TASK_CONFIG` registry + consult/dispatch entry renames; grep across `src/`.
- **Conf:** `conf-Medium` — existing `run_next` / `BUILD_CONFIG` chain patterns; five keys are minimal stubs.
- **Risk:** `risk-Medium` — wrong dispatch entry breaks `BUILD_ARTIFACTS` / `CANDIDATE_REVIEW`.

**Note:** Plan follows the nine-key table in the ticket (not narrative `guide_resume_revisions` / `check_resume` names). `origin/ftr/AST-450` created from `origin/dev` for this plan.

— Ada

---

# AST-450 — Register artifact pipeline task keys (dumb chain registry)

**Linear:** [AST-450 — Register artifact pipeline task keys (dumb chain registry)](https://linear.app/astralcareermatch/issue/AST-450/register-artifact-pipeline-task-keys-dumb-chain-registry)  
**Feature ref:** `ftr/AST-450` (origin only)  
**Blocks:** [AST-313 — Artifact pipeline prompt authoring](https://linear.app/astralcareermatch/issue/AST-313/artifact-pipeline-prompt-authoring)

## Summary

Replace legacy Phase E `craft_job_*` task keys with nine registry keys Susan uses in **Manage Tasks** (`run_next` + chain tokens). The runtime stays **dumb**: `do_task` runs one `task_key`, then follows `agent_task.run_next` — **no** step lists, hop counts, or pipeline choreography in code. This ticket registers keys in `TASK_CONFIG`, seeds `agent_task` rows via `sync_agent_tasks`, and updates **dispatch entry points only** (`BUILD_ARTIFACTS`, `CANDIDATE_REVIEW`). Prompt text and `run_next` wiring remain Susan’s work in **AST-313**.

⚠️ **Decision:** The ticket’s narrative chain mentions `guide_resume_revisions` / `check_resume`; the authoritative **nine-key table** in the Linear description uses `advise_job_resume`, `check_job_resume`, etc. This plan implements **only the nine keys in that table**. Susan wires `run_next` in Admin after keys exist.

⚠️ **Decision:** No alias period for `craft_job_*` in `TASK_CONFIG` — remove legacy keys and update all references in one pass (grep-driven). Existing `agent_task` rows for old keys may remain in SQLite but are not valid `run_next` targets once removed from `TASK_CONFIG`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add nine `TASK_CONFIG` entries; remove `craft_job_resume`, `craft_job_cover_letter`, `craft_application_responses`; update `BUILD_CONFIG.resume_artifact_chain` / `cover_letter_artifact_chain` `first_task_key`. | utils |
| `src/core/consult.py` | `_INPUT_STATE_TO_TASK`: `BUILD_ARTIFACTS` → `contemplate_job`, `CANDIDATE_REVIEW` → `draft_cover_letter`; batch routing + `_prep_live_content` `scoring_task_key` strings; `_run_cover_letter_for_job` uses `draft_cover_letter` or `run_cover_letter_artifact_chain_for_job`. | core |
| `src/core/agent.py` | No chain logic changes; `run_resume_artifact_chain_for_job` / `run_cover_letter_artifact_chain_for_job` already read `BUILD_CONFIG` `first_task_key`. | core |
| `src/data/database.py` | `_DISPATCH_TASK_SEED`: replace `craft_job_resume` / `craft_job_cover_letter` rows with `contemplate_job` / `draft_cover_letter`. | data |
| `src/utils/config.py` (comment) | Short comment near Phase E block: cache tokens / `{$CACHE_BLOCK_B/C/D}` — no `--- CACHED CONTEXT ---` duplication (AST-303 Radia note); details for **AST-313**. | utils |

**Out of scope (do not touch):** `tests/`, `scripts/test_*.py`, `docs/ASTRAL_TEST_BIBLE.md` — Betty updates via **qa-astral** after **Code Complete**.

**Spike / investigation output:** none.

## Stage 1: `TASK_CONFIG` registry (nine keys)

**Done when:** `get_task_keys()` includes all nine keys below; none of `craft_job_resume`, `craft_job_cover_letter`, `craft_application_responses` remain in `TASK_CONFIG`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, **delete** the three `craft_job_*` entries under Phase E.
2. Add entries (phase `"E. Job Artifacts"`, `entity_type: "job"`, `requires_candidate_key: True`, `trigger_state: None` unless noted):

| `task_key` | `seq` | `response_schema` / notes |
|------------|-------|---------------------------|
| `contemplate_job` | 1 | Minimal stub: `astral_job_id`, `company`, `title` optional strings — dispatch entry; Susan authors prompts in **AST-313**. |
| `advise_job_resume` | 2 | Registry-only minimal stub (same minimal fields). |
| `draft_job_resume` | 3 | **Move** full schema from former `craft_job_resume`: `grades` list, twelve `vectors` names only, `grading_mode: "scored"`, `response_format: "json"`, `context_format: "grade_like_{index}"`. |
| `check_job_resume` | 4 | Registry-only minimal stub. |
| `finalize_job_resume` | 5 | Stub with fields aligned to `BUILD_CONFIG["artifact_shapes"]["resume_content"]` keys (`technical_skills`, etc. — copy exact keys from `artifact_shapes` on branch tip). |
| `draft_cover_letter` | 6 | **Move** full entry from former `craft_job_cover_letter` (`nocache_prompt`, `re_line` / `body` / `signature` schema). |
| `check_cover_letter` | 7 | Registry-only minimal stub. |
| `finalize_cover_letter` | 8 | Registry-only minimal stub (optional: mirror `artifact_shapes["cover_letter"]` field names as optional strings). |
| `propose_application_responses` | 9 | **Move** schema from former `craft_application_responses`. |

3. Add a 2–3 line comment above the Phase E block pointing prompt authors to **AST-313** for `{$CACHE_BLOCK_*}` usage (no duplicated cache headers per AST-303).

⚠️ **Decision:** `draft_job_resume` keeps scored vectors (not a blank stub) so existing consult/grade paths and **AST-428** vector-name-only config stay valid until Susan replaces prompts.

## Stage 2: `BUILD_CONFIG` entry keys only

**Done when:** `BUILD_CONFIG["resume_artifact_chain"]["first_task_key"] == "contemplate_job"` and `BUILD_CONFIG["cover_letter_artifact_chain"]["first_task_key"] == "draft_cover_letter"`.

1. In `src/utils/config.py` `BUILD_CONFIG`, set `resume_artifact_chain.first_task_key` to `"contemplate_job"`.
2. Set `cover_letter_artifact_chain.first_task_key` to `"draft_cover_letter"`.
3. Do **not** add arrays, step indices, or promotion logic.

## Stage 3: Dispatch routing (`consult.py` + `database.py`)

**Done when:** `run_consult_task(..., "BUILD_ARTIFACTS", ...)` routes to resume batch using `contemplate_job`; `run_consult_task(..., "CANDIDATE_REVIEW", ...)` routes to cover batch using `draft_cover_letter`; `_DISPATCH_TASK_SEED` matches.

1. In `src/core/consult.py` `_INPUT_STATE_TO_TASK`, set:
   - `"BUILD_ARTIFACTS": "contemplate_job"`
   - `"CANDIDATE_REVIEW": "draft_cover_letter"`
2. In `run_consult_task`, change `elif task_key == "craft_job_resume"` → `elif task_key == "contemplate_job"` (same body: `_run_craft_job_resume_batch` or rename function to `_run_build_artifacts_batch` — optional rename for clarity).
3. Change `elif task_key == "craft_job_cover_letter"` → `elif task_key == "draft_cover_letter"`.
4. In `_run_craft_job_resume_batch`, keep `run_resume_artifact_chain_for_job` (reads `BUILD_CONFIG` — no hardcoded first key).
5. In `_run_cover_letter_for_job` and `_run_craft_job_cover_letter_batch`, replace every `"craft_job_cover_letter"` string with `"draft_cover_letter"`; prefer `run_cover_letter_artifact_chain_for_job` in `_run_craft_job_cover_letter_batch` if it reduces duplication (same behavior as today).
6. In `src/data/database.py` `_DISPATCH_TASK_SEED`, replace:
   - `"craft_job_resume": {... trigger_state: BUILD_ARTIFACTS ...}` → `"contemplate_job": {...}`
   - `"craft_job_cover_letter": {... trigger_state: CANDIDATE_REVIEW ...}` → `"draft_cover_letter": {...}`
7. Grep `src/` for `craft_job_resume`, `craft_job_cover_letter`, `craft_application_responses` — update every hit (including `scoring_task_key=` and `do_task(` first args). **Do not** change `craft_joblist_rubric` / `craft_jobdesc_rubric`.

## Stage 4: Startup sync + admin validation

**Done when:** After app import, `sync_agent_tasks(get_task_keys())` inserts blank `agent_task` rows for new keys; saving `run_next` to any new key in Manage Tasks succeeds.

1. Confirm `src/ui/server.py` still calls `database.sync_agent_tasks(get_task_keys())` on startup (no code change unless missing).
2. Manually verify (document in build comment): `_validate_run_next` accepts edges between new keys because each target ∈ `TASK_CONFIG`.
3. **Do not** implement migration copying prompts from old `craft_*` rows to new keys — Susan re-authors in **AST-313**.

## Stage 5: Compile + publish

**Done when:** `python3 -m py_compile` on all changed `.py` files passes; branch published to `origin/ftr/AST-450`.

1. `python3 -m py_compile src/utils/config.py src/core/consult.py src/data/database.py` (add any other touched modules).
2. Commit on `dev-ada`: `feat(AST-450): register artifact pipeline task keys — registry and dispatch entries`.
3. Cherry-pick to `origin/ftr/AST-450` per **build-astral** §6.

## QA test manifest (Betty — post Code Complete)

1. `python3 -m py_compile src/utils/config.py src/core/consult.py src/data/database.py tests/component/utils/test_config.py tests/component/core/test_agent.py`
2. `pytest tests/component/utils/test_config.py -q -k "Ast450 or Ast309CoverLetter or test_resolves_writing_preferences_from_context or test_resolves_cover_letter_signature_from_profile"`
3. `pytest tests/component/core/test_consult.py -q -k "candidate_review_to_cover or Ast371Resume or Ast369CoverLetter"`
4. `pytest tests/component/core/test_agent.py -q` (key rename touches many `do_task` paths — full file quicker than brittle `-k`.)
5. Full gate before merge: `./scripts/testing/run_component_tests.sh` (`test-astral`).
## Execution contract (for the developer agent)

- **Forbidden:** `RESUME_PIPELINE_STEPS`, step-index constants, cache-promotion-at-step-N, ordered hop arrays, or any code that encodes chain length/order beyond `BUILD_CONFIG.first_task_key`.
- **Allowed:** Renaming dispatch batch helpers; grep-updating string literals; minimal `TASK_CONFIG` stubs.
- **Stop with 🛑** on Linear if Susan’s admin chain requires keys **not** in the nine-key table (e.g. `guide_resume_revisions`) without a Linear description update.

## Self-Assessment

### Scope

**scope-MAJOR-CHANGE** — Touches `TASK_CONFIG`, consult dispatch, dispatch DB seed, and grep-updates across `src/` (tests deferred to Betty).

### Conf

**conf-Medium** — Patterns exist (`run_next`, `BUILD_CONFIG` chains, `_DISPATCH_TASK_SEED`); exact stub shapes for five registry-only keys follow existing Phase E conventions.

### Risk

**risk-Medium** — Wrong dispatch entry key breaks `BUILD_ARTIFACTS` / `CANDIDATE_REVIEW` batches; mitigated by consult routing tests in Betty’s manifest.

## Self-review vs ASTRAL_CODE_RULES

- **§2.1** — All thresholds and chain entry keys in `config.py` / `BUILD_CONFIG`; no hardcoded pipeline steps.
- **§2.6** — No new job states; dispatch still state-driven via `dispatch_tasks` seed.
- **§3.3** — Consult imports agent helpers only; no new UI→database shortcuts.
- **§3.5** — New keys use `snake_case` per ticket table.

## Review

**Radia (`review-astral`).** Baseline **`origin/dev`**, feature **`origin/ftr/AST-450`**. Engineer tip reviewed: **`abfdd73aea2e31eeac278bc5a2de202e09f5580b`** (component gate restores LOCKED coverage + registry work below).

### Counts

- **fix-now:** 0
- **discuss:** 0
- **advisory:** 4

### What’s solid

- **Plan fidelity (`AST-450` scope):** All nine **`TASK_CONFIG`** keys are registered under Phase E with **`BUILD_CONFIG.resume_artifact_chain.first_task_key` → `contemplate_job`** and **`cover_letter_artifact_chain.first_task_key` → `draft_cover_letter`**; **`_INPUT_STATE_TO_TASK`** and **`_DISPATCH_TASK_SEED`** align (no orphaned legacy dispatch rows for the retired keys).
- **Dumb-chain constraint:** Diff shows **entry keys + `agent_task.run_next` only**—no pipeline step arrays or hop choreography added.
- **`draft_job_resume` / `draft_cover_letter` migration:** Former graded resume vectors and **`AST-309`** cover schema move cleanly; **`craft_job_resume` / `craft_job_cover_letter` / `craft_application_responses`** are absent from runtime **`src/*.py`** (remaining hits are **`_run_craft_*` helper names**, tests asserting legacy absent, and historical mentions in unrelated feature docs).
- **Consult routing improvement:** Replacing inlined **`do_task("craft_job_cover_letter")`** with **`run_cover_letter_artifact_chain_for_job`** keeps cover dispatch consistent with **`BUILD_CONFIG`** first-hop indirection (**`AST-300` / `AST-301`** pattern).
- **QA signal:** Expanded component coverage for consult agent/dispatch paths (`ASTRAL_TEST_BIBLE §7.13m` documents the matrix).

### Recommended actions

| Severity | Topic | Recommendation |
| --- | --- | --- |
| **Advisory** | Lazy imports (`consult.py`) | **`run_cover_letter_artifact_chain_for_job`** is imported inside **`_run_cover_letter_for_job`** / **`_run_craft_job_cover_letter_batch`** without a rationale comment—the same omission already existed for **`run_resume_artifact_chain_for_job`**. Prefer a one-line **`# consult ↔ agent` cycle-break** note on **all three** lazies during **`resolve-astral`** if Susan wants parity with **`ASTRAL_CODE_RULES` §1 import** scrutiny. |
| **Advisory** | **`finalize_job_resume` stub strictness** | **`TASK_CONFIG`** uses optional fields while **`BUILD_CONFIG["artifact_shapes"]["resume_content"]`** marks several keys **`required: True`**—expected for pre-prompt stubs, but converge when **`AST-313`** lands so authors do not perceive conflicting contracts. |
| **Advisory** | Dispatcher tick test (**`test_dispatcher.py`**) | PEP 479 **`StopIteration` → RuntimeError** guard fix is orthogonal to **`AST-450`** but low-risk; keep as a housekeeping note when summarizing blast radius to Susan. |
| **Advisory** | Historical sibling docs (`ast-309`, `ast-369`, **`ast-371`**, **`ast-428`**) | Still cite **`craft_job_*`** naming in narrative tables—informational backlog for doc gardeners; runtime is already migrated. |

### Engineer implementation note (Ada — Code Complete)

- **Branch:** `ftr/AST-450` on `origin`; validation against **`TASK_CONFIG`** / **`sync_agent_tasks`** paths matches the **`AST-313`** unblock goal.
- Detail SHAs preceding Radia doc commit remain on **`origin/ftr/AST-450`** engineering history (`abfdd73a` cited above).

_Radia doc amend SHA: appears in git tip after **`docs(AST-450): Radia review — …`** push._

## Resolution

**2026-05-23 — Review Posted → User Testing (Ada)**

- **fix-now:** 0 — no additional product changes; engineering tip **`abfdd73a`** per Radia review stands.
- **discuss:** none.
- **advisory:** noted for backlog — lazy-import rationale parity on consult ↔ agent helpers; **`finalize_job_resume`** stub vs **`artifact_shapes["resume_content"]`** **`required`** flags to converge when **AST-313** prompts land; PEP 479 guard in **`test_dispatcher.py`** as orthogonal housekeeping; historical feature docs still naming **`craft_job_*`** until doc gardeners sweep.
- **Plan doc:** Radia sign-off **`docs(AST-450): Radia review — artifact registry dumb-chain sign-off`** merged from **`origin/ftr/AST-450`** (`57681373`); this **Resolution** section records close-out vs that thread.
