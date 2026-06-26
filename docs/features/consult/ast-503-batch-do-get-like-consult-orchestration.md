<!-- linear-archive: AST-503 archived 2026-06-15 -->

## Linear archive (AST-503)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-503/batch-do-get-like-consult-orchestration-high-volume-encoded-batch  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-500 — High-volume encoded batch consult: migrate all stages, cache-first exhaustion runs  
**Blocked by / blocks / related:** parent: AST-500

### Description

## What this implements

Migrate **consult_do**, **consult_get**, and **consult_like** from per-job **render_verdict** / warm-gather paths to the same **encoded batch consult** pattern as qualify and evaluate: assemble **N** jobs per assessment, decode multi-line responses, apply per-job outcomes. Enable **batch_call_mode** and route through `_run_batch_consult` (or equivalent) so these stages participate in high-volume exhaustion (AST-502).

## Acceptance criteria

* With **N > 1** eligible jobs at a DO/GET/LIKE step, one assessment per chunk with **N** encoded lines in the envelope; per-job terminal/retry states match existing rules.
* Stages use **dispatch_task** batch_size / batch_call_mode (no hard-coded 500 default in code).
* Works with multi-chunk parallel exhaustion from AST-502 for large backlogs.

## Boundaries

* Encoder/rubric semantics unchanged (AST-351 wire format).
* Does not change qualify/evaluate (AST-501) or dispatcher chunking logic itself (AST-502).

## Git branch (authoritative)

`sub/AST-500/AST-503-…` under parent `ftr/AST-500-…`.

### Comments

#### radia — 2026-05-27T03:47:49.184Z
**Diff:** `origin/dev...origin/sub/AST-500/AST-503-batch-do-get-like-consult-orchestration` @ `47c0db92`.

- **Plan / code — OK:** `_consult_scored_dispatch_batch_encoded` mirrors evaluate-style prep filtering (missing company → `error_state` + skip, empty `_prep_live_content` with `NEED_WEBSITE_CONTENT` short-circuit retained, else `error_state`); `CONSULT {DO|GET|LIKE} ROWS` assembly + `_run_batch_consult` with `grade_*` agent task; `_apply_render_verdict_decoded_job` shares decode→grade/save/transition with refactored `render_verdict`; `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` includes `consult_*`; seed `batch_call_mode: 1` for those rows matches acceptance.
- **Discuss (envelope parity):** AST-501 strict envelope gate is keyed to `qualify_job_listings` / `evaluate_jd` only; batch DO/GET/LIKE call `do_task` as `grade_*` — prompts were fixed in config, but coercion/validation paths may still differ from qualify/evaluate; close the gap or document deliberate deferral if Susan wants identical hard rejections.
- **Advisory (metrics):** `run_consult_task` still maps `errors = max(0, total - passed - failed)`; merged `total` with pre-`do_task` skips can inflate `total_errors` vs actually graded rows — same pattern as `evaluate_jd_batch` not-ready handling; leave unless product wants skipped excluded from denominator.

**Radia doc cherry-pick:** `ce207d079e8ff0fc39ab6ef34122f10239fa5023` — `git cherry-pick ce207d079e8ff0fc39ab6ef34122f10239fa5023`. **`## Review`** on `docs/features/consult/ast-503-batch-do-get-like-consult-orchestration.md`.

#### chuckles — 2026-05-27T03:34:49.197Z
QA test manifest (**docs/ASTRAL_TEST_BIBLE.md** §7.13zf + narrow block below):

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object tests/component/core/test_consult.py::TestRunConsultTask::test_ast503_routes_two_passed_jd_jobs_to_consult_do_batch`

2. Full encoded-batch slice with siblings (optional on your tip after `ftr` merge): use the **AST-501 + AST-502** command block in §7.13zf, then add the three **AST-503** nodes above.

Publish: `origin/sub/AST-500/AST-503-batch-do-get-like-consult-orchestration` @ `47c0db92`. Definitive bible on `origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs` @ `0ddd97c9` (sub/ftr **ASTRAL_TEST_BIBLE.md** blob match verified).

— Betty

#### hedy — 2026-05-27T03:03:54.169Z
**Published plan:** [docs/features/consult/ast-503-batch-do-get-like-consult-orchestration.md](https://github.com/susansomerset/astral/blob/sub/AST-500/AST-503-batch-do-get-like-consult-orchestration/docs/features/consult/ast-503-batch-do-get-like-consult-orchestration.md)

**Self-assessment (with justifications)**

- **Scope — scope-Single-Component:** Consult batch wrappers + dispatcher allow-list coupling + dispatch seed toggles + tests restricted to consult_do/consult_get/consult_like—not qualify/evaluate rewrites nor AST-502 core splitter.
- **Conf — conf-Medium:** Depends on AST-502’s multi-chunk contract and batch indices; merge order resolves most ambiguity if Chuckles stacks branches as documented.
- **Risk — risk-HIGH:** Wrong per-job grading or hydration breaks downstream candidate matching and JOB_STATES for closed-loop consult sales behavior.

---

# AST-503 — Batch DO / GET / LIKE consult orchestration

**Linear:** [AST-503](https://linear.app/astralcareermatch/issue/AST-503/batch-do-get-like-consult-orchestration-high-volume-encoded-batch)  
**Parent epic:** [AST-500](https://linear.app/astralcareermatch/issue/AST-500/high-volume-encoded-batch-consult-migrate-all-stages-cache-first)  
**Project:** Astral Consult  
**Publish ref:** `origin/sub/AST-500/AST-503-batch-do-get-like-consult-orchestration`

Move **`consult_do`**, **`consult_get`**, **`consult_like`** (**trigger states routed through `run_consult_task`**) from **per-job `render_verdict`** (**today `entities[0]` only**) to **`_run_batch_consult`**-style **`Pattern A`** mirroring **`qualify_job_listings` / `evaluate_jd`**:

1. Dispatcher already passes **`batch_call_mode`** + full **`entities`** when DB row says batch (**post-dispatcher coherence** assumes **AST-501/502** shipped order per epic).
2. **`assemble`** builds multi-job **`JOB …`/`JD …`** text with **indexed rows** aligning **`enumerate_array`/`JOB LISTINGS` patterns** (**zero-padded 000-based **`pos`** in prompt text only** — **IDs stay out of echoed live content patterns** reused from qualify/evaluate per **existing security posture** (`qualify_job_listings` assembler comment)).
3. **`process_fn`** embodies today’s **`render_verdict`** outcome mapping (**grading_mode scored vs binary**, hydration via **`_hydrate_grade_reasons_from_rubric`**, **`tracker.save_job_data`** keys **`do_grades` / `do_score` / optional `do_notes`** (use actual `save_prefix` from `TASK_CONFIG` per step), **`_transition_job_state_for_task`**).
4. **`dispatch_tasks.batch_call_mode`** set **`1`** for these steps (**seed + admin** path only — **no Python default replacing DB**).

**Boundaries:** **AST-351 wire format unchanged**; **AST-501** owns envelope strictness; **AST-502** owns multi-chunk fan-out — this ticket targets **batch assembly + consult routing** for DO/GET/LIKE.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add **`async def consult_do_batch`**, **`consult_get_batch`**, **`consult_like_batch`** (names illustrative — **match existing `*_batch` naming** beside **`evaluate_jd_batch`**) each mirroring qualify structure: **`task_key` literal**, **`_consult_orchestration`**, **`assemble` closure** (multi-job `_prep_live_content` fan-in), **`process` closure** (**extract private helper from `render_verdict` body** or **call shared `_apply_render_verdict_decoded_job(...)`**), **`return await _run_batch_consult(...)`**. Update **`run_consult_task`** branch **`elif task_key in ("consult_do", "consult_get", "consult_like"):`** to **`await <new batch fn>(batch_id, entities, ctx, debug)`** instead of **`render_verdict` on `entities[0]`**. | core |
| `src/utils/config.py` | Ensure **`TASK_CONFIG`** entries keyed **`grade_do`**, **`grade_get`**, and **`grade_like`** already declare **`grades_encoded_notes`** (**unchanged**) — verify **`response_schema` `jobs[]`** survives batch decode (**already post-decode shape**). | utils |
| `src/data/database.py` | **`_DISPATCH_TASK_SEED`** (or migration JSON): flip **`batch_call_mode`** **`1`** for **`consult_*` dispatch rows** aligning parent epic (**no hard-coded runtime table** beyond seed ownership). | data |
| `src/core/dispatcher.py` | Possibly **expand AST-502 chunk-runner allow-list** (**if narrower guard landed**) to include **`consult_do/get/like`** — coordinate with **`AST-502` implementation slice** (**single merge resolution** expectation). | core |
| `tests/component/core/test_consult.py` | Extend / add tests: mocked **`do_task`** sees **`batch_entities` length N** (**N mock jobs**) for **`consult_get_batch`** (**example**); assert **`assemble` textual indices** contiguous; golden decode path optional if heavy — **reuse existing consult batch fixtures**. | tests |

---

## Stage 1: Factor shared verdict application (avoid duplicate business logic)

**Done when:** A single callable (**e.g. `_apply_encoded_consult_job_outcome(agent_task_key, aid, decoded_job_row, cfg, ctx)`**) performs **everything** current **`render_verdict`** does **after successful decode**:

1. Locate **`render_verdict`** (**`consult.py`**): split into **(A) prep + `do_task` + parse** vs **(B) grade hydration + scoring + `save_job_data` + transition**.
2. Move **(B)** into helper consumed by **`render_verdict`** (single-job still uses helper) **and** by **`process_fn`** of new batch runners (**per response_job dict**).
3. **`render_verdict`** remains for **adhoc / admin one-off** paths (**API** / scripts) — **do not delete public symbol** without audit (**grep callers**).

⚠️ **Decision:** **Helper signature** accepts **`response_job` dict** matching **`_decode_payload` output** (`astral_job_id`, `grades`, optional `notes`).

---

## Stage 2: Multi-job live content assembly

**Done when:** **`assemble(jobs)`** builds deterministic multi-row prompt body:

1. **DO/GET/LIKE** each call **`_prep_live_content`** per job (**async**). **Batch runner must be `async`**: **mirror `evaluate_jd_batch` pattern** — **pre-await all preps** via **`asyncio.gather`** across jobs **before** **`_run_batch_consult`** inner **`do_task`** OR **sequential await** if ordering matters for coat-check side effects — **choose sequential** if **`_prep_live_content` mutates DB** with race risk; **pref gather** if **read-only** after initial job dict snapshot.

   ⚠️ **Decision:** **Sequential `for job in jobs: await _prep_live_content`** unless profiling proves safe — **correctness > speed** (**Susan rule**).

2. **Listing format:** Use section header per epic (**reuse `JOB LISTINGS`/JD patterns**):

   `"CONSULT <STEP> ROWS:\n"` + enumerated blocks **`f"{i:03d}: ..."`** tying index **i** to **`batch_entities[i]`**.

3. **`requires_company` jobs** (**LIKE**): **Exclude** upfront jobs failing company fetch (**same as render_verdict** `_fail` equivalents) → transition via **`error_state`** **without** poisoning batch (**filter list** **`eligible_jobs`**):

   ```
   ⚠️ **Decision:** Mimic **`evaluate_jd_batch` not-ready split**: **`ineligible`** list transitions individually before **`_run_batch_consult`** (**document states** mirrored from **`render_verdict`**).

4. **`NEED_WEBSITE_CONTENT` shortcut:** Preserve **no `error_state` overwrite** when website missing (**existing comment in `render_verdict`**).

---

## Stage 3: Wire **`run_consult_task` batches**

**Done when:**

1. **`run_consult_task`** maps **`consult_do/get/like`** to **`consult_*_batch(batch_id, entities, ctx, debug)`**.
2. **Summary normalization**: bottom of **`run_consult_task`** already converts **`passed/failed/total`** — confirm **batch functions return `_run_batch_consult` dict** + adapter like **`qualify_job_listings`** (**extend if totals need `skipped`** from pre-filtered jobs).
3. **Dispatcher**: once **`batch_call_mode=1`**, `_run_unified` **no longer hits `_warm_then_gather` per entity** (**AST-501** already defined) — **this ticket completes consult mapping**.

---

## Stage 4: DB seed **`batch_call_mode`**

**Done when:** Local seed aligns parent intent (**Susan-owned prod** may still ALTER manual — mention in Linear handoff):

1. Update **`database._DISPATCH_TASK_SEED`** (**or JSON migration if pattern changed**) **`batch_call_mode: 1`** rows for **`consult_do`/`consult_get`/`consult_like`** task_keys.
2. **Do not bake `batch_size=500`** — leave operator-tunable numbers **unless Susan pre-seeded explicit counts** (**reuse existing numeric literals only if row already depended on them**).

---

## Stage 5: Tests

**Done when:**

1. **Async test** mocking **`do_task`**: asserting **`ctx["batch_entities"]`** length **matches** mocked job count for **`consult_get_batch`** (**3** stubs).
2. **Filter regression**: **`requires_company`** failure eliminates job **before `do_task`**, transitions **`error_state`**, remaining jobs still graded (**simulate two jobs**, one lacking company).

---

## Self-Assessment

### Scope — **scope-Single-Component**

Touches **`consult`**, **`dispatcher` conditional allow-list coupling**, **`database` seed**, **tests** — **DO/GET/LIKE** only (**no qualify/evaluate logic rewrite** despite reading them for patterns).

### Conf — **conf-Medium**

Depends on **`AST-502` splitter** behaving for additional keys (**integration sequencing** manageable via merge order Chuckles directs).

### Risk — **HIGH**

Mis-modeled **state transitions / rubric hydration** regress **closed sales pipeline** (**candidate job matching correctness**).

---

## Plan vs ASTRAL_CODE_RULES cross-check

- **§2.7 render_verdict pattern**: **Retain** symmetry — **scores**, **`save_prefix`**, optional **`notes` tail** remain driven by **`TASK_CONFIG`**.
- **§2.8 Coat-check**: **_prep_live_content** rules honored (**no storing empty failures** unchanged).
- **§2.6**: **JOB_STATES** transitions only via **`_transition_job_state_for_task`** (**no dispatcher promotion**).

---

## Review

**Diff:** `origin/dev...origin/sub/AST-500/AST-503-batch-do-get-like-consult-orchestration` @ `47c0db92493a2a056c86617e34e3830b12b284c1`

### What's solid
- **`_consult_scored_dispatch_batch_encoded`** + thin **`consult_*_batch`** wrappers assemble **`CONSULT {DO|GET|LIKE} ROWS`** indexing, **`_run_batch_consult(agent_task=grade_*)`** for one encoded call, and reuse **`cfg_dispatch`**/`**_apply_render_verdict_decoded_job**` — matches plan Stages 1–3 (**sequential **`_prep_live_content`**, **`NEED_WEBSITE_CONTENT`** / missing-company exclusions).
- Dispatcher expands **`_CHUNK_EXHAUST_CONSULT_JOB_KEYS`** to include scored consult steps (**plan + AST-502 integration**); seed flips **`batch_call_mode`** to **`1`** for **`consult_*`** rows (**Stage 4**).
- **`render_verdict`** refactors decode → shared helper while preserving **`consult_do`**/`**dispatch`** keying for **`_render_pass_fail`**.

### Issues / follow-ups

| Severity | Bucket | Topic | Notes |
| -------- | ------ | ----- | ----- |
| discuss | Envelope parity | **`do_task` task_key uses `grade_*` in batches | AST-501 strict envelope whitelist covers **`qualify_job_listings` / `evaluate_jd`** only; prompts were tightened globally on **`grades_encoded_notes`**, but decoding still allows legacy coercion paths for **`grade_*`** unless blocked elsewhere — decide whether graded DO/GET/LIKE should reuse the strict gate for wire parity when **`batch_entities`** present (or explicitly document intentional deferral). |
| advisory | Metrics | **`run_consult_task` summary derives `errors = max(0, total - passed - failed)` | With **`skipped` pre-batch jobs**, **`total=len(jobs)`** can inflate **`total_errors` vs graded rows** — same pattern **`evaluate_jd_batch`** uses for not-ready splits; intentional unless product wants **`skipped`** excluded from denominator. |

### Recommended actions

No **fix-now** for **`resolve-astral`** from this pass unless Susan wants **`grade_*`** strict envelope symmetry.

---

## Resolution (`resolve-astral`)

**Date:** 2026-05-26  

**Against:** Radia `review-astral` § **Review** on `origin/sub/AST-500/AST-503-batch-do-get-like-consult-orchestration` @ **`47c0db92`**.

**Product / plan**

- **`fix-now`:** None — **`_consult_scored_dispatch_batch_encoded`**, seeded **`batch_call_mode`**, **`_CHUNK_EXHAUST_CONSULT_JOB_KEYS`**, **`render_verdict`** helper split, and component tests (**`AST-503`**) are as-reviewed; **`dev-hedy`** includes the **`docs(AST-503): Radia …`** tip before this appendix.
- **Discuss — strict envelope whitelist vs graded batch:** **`_strict_encoded_batch_consult_envelope_err`** intentionally remains **`qualify_job_listings` / `evaluate_jd`** (**AST-501**). Graded **`grade_*`** batches enforce envelope via **this ticket’s **`test_ast503_rejects_grade_do_*`** regressions plus prompt cleanup on **`grades_encoded_notes`** rather than widening the whitelist; **full decode-path symmetry** stays a **defer** unless Susan opens a focused follow-on.
- **Advisory — `run_consult_task` denominator vs skipped jobs:** Accepted as **`evaluate_jd_batch` parity**; no metric reshape in **`AST-503`**.
