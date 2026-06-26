# AST-500 — High-volume encoded batch consult: migrate all stages, cache-first exhaustion runs

<!-- linear-archive: AST-500 archived 2026-06-15 -->

## Linear archive (AST-500)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-500/high-volume-encoded-batch-consult-migrate-all-stages-cache-first  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Astral’s consult pipeline (screening job listings, screening job descriptions, then DO / GET / LIKE grading) was designed around **compact encoded agent answers** so many items can ride in **one model call**. In practice, much of that work still runs **one job per call**, which wastes money, time, and prompt-cache benefit. This epic makes **high-volume batching the real behavior** for every encoded consult step: send as many items as context allows per call, drain large backlogs in chunks, and **warm the prompt cache on the first chunk** so follow-on chunks run with better cache reuse. Susan’s goal is throughput at roster scale (e.g. hundreds of JDs per call, thousands per dispatch wave) without changing rubrics or pass/fail rules.

## Functional scope

1. **Single-call batching for encoded consult steps** — For job-listing qualification, JD evaluation, and DO / GET / LIKE grading, the product sends **one assessment request per batch chunk** that includes **all items in that chunk** (numbered positions starting at 000). The model returns **one structured response** whose payload contains **one encoded result line per item**, wrapped in the standard success/failure envelope (agent can signal it could not perform the task vs. grading outcomes in the payload).
2. **Configurable batch size** — Operators can set how many items each dispatch batch claims per consult step (via existing scheduled-task configuration). The product supports **large batches** (Susan’s design center: on the order of **500 items per call** where context allows), not the current de-facto one-item behavior for steps that are already encoded on the wire.
3. **Cache-first multi-chunk exhaustion** — When more items are ready than one batch allows (e.g. 2000 jobs with batch size 500): **run the first chunk to completion** so shared prompt content (system instructions, rubric, cached task material) is established; **then run remaining chunks in parallel** after a short warm-up interval so later chunks benefit from cache reads. Within a dispatch cycle, keep launching full-size chunks until that step’s eligible queue for the candidate is cleared or blocked by limits (context ceiling, explicit caps, or hard failures).
4. **Migrate DO / GET / LIKE to the same batch pattern** — These steps already use the compact encoded line format (including optional short notes on DO/GET/LIKE). They move from **per-job assessment** to the **same batch orchestration** as qualification and JD evaluation, including the same per-item outcomes: grades on the job record, scores where applicable, state transitions, and optional notes.
5. **Preserve existing grading semantics** — Per-item pass/fail or scored thresholds, rubric-driven “reason” text on grades, retry holding states for bad or incomplete model output, and company/website readiness rules (e.g. jobs that cannot get website content for LIKE stay out of the batch or go to the existing holding state) behave as today—only **how many items share one call** changes.
6. **Observable batch behavior** — Susan can confirm in logs and cost records that a multi-item dispatch produced **one assessment per chunk** (not one per job), that multi-line payloads decode to the right number of jobs, and that later parallel chunks show **meaningful cache reuse** compared to the first chunk.

## Boundaries

* **Does not** change rubric vectors, grade letters, confidence rules, or pass/fail thresholds.
* **Does not** change which consult step runs at which job state (dispatch still keys off the same trigger states).
* **Does not** batch company-side work (prefilter, find job page, gaze, board search, etc.) except where a small shared dispatcher improvement is unavoidable.
* **Does not** include switching LLM provider or tier (covered under [AST-491](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek) and agent configuration elsewhere).
* **Does not** replace adhoc / single-job admin test flows—they may still assess one entity at a time.
* **Does not** silently drop or truncate items when a batch exceeds context; the product must **fail loudly** and leave affected items in a recoverable state (retry or error), per existing consult retry discipline.
* Must remain **config-driven** for dispatch batch size and batch-vs-single-entity mode (no hard-coded dispatch tables in code).

## Acceptance criteria

1. With batch size **N > 1** and **N** eligible jobs for JD evaluation, a single dispatch pass produces **one** assessment call for that chunk and a payload with **N** encoded lines (or explicit agent failure in the envelope); each job lands in pass, fail, retry, or error state per today’s rules—not left stuck in the trigger state.
2. The same single-call / multi-line behavior holds for **job-listing qualification** on a multi-listing batch.
3. **DO, GET, and LIKE** use the same batch orchestration; per-job grades, scores, notes (when present), and state transitions match current product behavior.
4. For a backlog larger than one batch (documented UAT scenario: **2000** items, batch size **500**), the product runs **chunk 1 first**, then **remaining chunks concurrently** after warm-up—not **2000** separate assessments.
5. Cost/timesheet evidence for parallel follow-on chunks shows **cache read** on shared prompt material materially higher than chunk 1’s cold read (acceptable via debug logging during UAT).
6. Scheduled-task configuration controls batch size per consult step without a code deploy.
7. Model responses respect the **outer envelope**; compact lines live inside `agent_payload`, not as a substitute for the envelope or as unrelated expanded JSON, for all providers in production use.

## Dependencies and blockers

* **Related:** [AST-491](https://linear.app/astralcareermatch/issue/AST-491) (DeepSeek / multi-provider)—UAT surfaced batch and envelope issues but is not a hard blocker once provider choice is stable for consult.
* **Informs:** Encoded consult wire format ([AST-351](https://linear.app/astralcareermatch/issue/AST-351/convert-consult-to-use-encoded-responses)) and dispatch batch-mode design ([AST-340](https://linear.app/astralcareermatch/issue/AST-340/retry-bad-responses))—already shipped in spirit; this epic **enforces** them in runtime.
* **None** required to start definition; implementation should not wait on unfinished consult epics unless a child ticket discovers a conflict.

## Open questions

1. **Default batch sizes** — Is **500** the target default for **all** encoded consult steps, or should qualification, JD evaluation, and DO/GET/LIKE each have different caps (e.g. smaller for fat JD+recap prompts)?
   1. No default batch sizes.  It's all driven by the dispatch task.
2. **Parallel fan-out** — For chunks 2…K after chunk 1, should **all** remaining chunks run at once (e.g. 3 parallel calls for 2000÷500), or is there a max concurrency Susan wants?
   1. Yes, run at once up to 500 concurrent.
3. **Exhaustion scope** — “Run to exhaustion”: drain everything claimed in **one scheduler tick**, or keep scheduling full batches on subsequent ticks until the trigger-state queue is empty for that candidate?
   1. drain everything on one scheduler tick, can't see a reason not to.
4. **Partial chunk failure** — If the model returns a valid envelope but **omits or garbles some positions** in a chunk, confirm we still use **per-job retry states** where configured (not fail the whole chunk to error unless envelope-level failure).
   1. Yes, still use RETRY states.
5. **Phasing for dispatch** — Prefer **one epic** with ordered child work (fix qualify/evaluate batching → chunk+parallel dispatcher → DO/GET/LIKE batch assembly), or **separate releasable milestones** Susan can UAT independently?
   1. One epic, please.

---

## Original brief

## Purpose

Move **all encoded consult stages** onto **true high-volume batching**: one API call carries **hundreds of items** (e.g. **500 JDs → 500 encoded lines** in `agent_payload`), not one job per `do_task`. When a backlog is larger than one batch (e.g. **2000 jobs**), **drain it in sequential batch chunks** on the **first wave** (batch 1 establishes **prompt cache** on shared system/rubric/cache blocks), then run **batches 2–4 asynchronously** once cache is warm — maximizing cache hit rate and throughput. Context windows are large enough for this; we will not beat that economics with per-job calls.

**In scope — migrate to Pattern A + encoded wire:**

| Stage | Today | Target |
| -- | -- | -- |
| `qualify_job_listings` | Intended batch; runtime often per-job | `batch_call_mode=1`, large `batch_size`, `_run_batch_consult` |
| `evaluate_jd` | Same | Same |
| `consult_do` / `consult_get` / `consult_like` | `render_verdict` per job, `batch_call_mode=0` | `_run_batch_consult` (or shared batch runner), `grades_encoded_notes`, multi-line payload |

Wire contract (unchanged): JSON **envelope** (`agent_performance` + `agent_payload`); **inner** payload = newline-delimited `000\|…` through `(N-1)\|…` (optional notes tail on DO/GET/LIKE). Decoder (`_decode_payload`) already supports N lines — **orchestration and dispatch** are the work.

## Product intent (@susan, 2026-05-27)

* Send **500 assessments in one call** when 500 jobs are ready; if **2000** are ready, run **batch 1 (500)** first, then **batches 2–4 in parallel** after the first call has established cache.
* **Run to exhaustion** within a dispatch cycle: keep pulling max-size batches until the claimed backlog for that stage is cleared (subject to token limits and sane caps).
* **Cache-first:** the first batch pays for full cached content; follow-on batches should ride **cache_read** on identical system + rubric + task cache blocks — never get better cache performance than maximizing shared content on the first call.

## Problem surfaced (evaluate_jd UAT)

* 16 jobs claimed but **16 parallel** `evaluate_jd_batch` / single `000\|` lines → per-job path, not one N-line response.
* Model skipped envelope or returned expanded JSON; bare-line tolerance on `dev` is a band-aid.
* Seed says `batch_call_mode: 1` for qualify/evaluate; **DO/GET/LIKE** still job-by-job despite encoded wire ([AST-351](https://linear.app/astralcareermatch/issue/AST-351/convert-consult-to-use-encoded-responses) deferred batch orchestration).

## Architecture direction

### 1\. Dispatch & consult routing

* `batch_call_mode = 1` on all encoded consult `dispatch_task` rows (qualify, evaluate, do, get, like).
* `batch_size` configurable per task (admin / DB); target **hundreds** where token budget allows (500 as design example; validate per model/tier).
* `run_consult_task`: route do/get/like through `_run_batch_consult` (batch `assemble_fn` + `process_fn`), retire per-job-only path except adhoc/single-entity tools.
* **No** `_warm_then_gather` **per job** for these tasks — warming is **per batch chunk**, not per entity.

### 2\. Cache-warm exhaustion (2000 → 4×500)

For a single dispatch run with more entities than `batch_size`:

1. **Split** claimed entities into chunks of `batch_size` (e.g. 4×500).
2. **Chunk 1:** one `do_task` / `_run_batch_consult` — **await completion** (establishes cache on shared blocks).
3. **Chunks 2…K:** launch **concurrent** batch consult calls (same `batch_id` family or sub-batch ids for audit), after `cache_warm_delay_seconds` or equivalent gate — reuse existing dispatcher timing idea at **batch** granularity.
4. **Decode + process** each chunk independently; reconcile IDs, retry/error states per existing `_run_batch_consult` rules.
5. **Repeat** on next scheduler tick until trigger_state queue empty.

Document max safe `batch_size` per task (JD length, rubric size, provider). Fail loud if a batch exceeds context — do not silent truncate.

### 3\. Live content assembly (DO/GET/LIKE)

* Batch assembler concatenates N per-job `_prep_live_content` sections (or equivalent) with stable **000…N−1** indices in `batch_entities`.
* LIKE / `requires_company` gates still apply **before** include in batch (skip or hold `NEED_WEBSITE_CONTENT` jobs out of batch).
* Per-job scoring/threshold/`{prefix}_notes` after decode — same as today’s `render_verdict` outcomes.

### 4\. Prompt / provider discipline

* Reconcile `grades_encoded*` (“no JSON” inner payload) vs `prompt_prefix` (outer envelope required) — all providers including DeepSeek.
* Remove or narrow bare-payload coerce once envelope compliance is reliable.

## Out of scope

* Changing rubric vectors, pass/fail rules, or grade letters.
* Non-consult dispatch (company gaze, prefilter, etc.) except where shared batch-runner refactor helps.
* Automatic provider switching ([AST-491](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek)).

## Acceptance criteria

1. **Qualify + evaluate:** one `do_task` per batch chunk of N>1; response has envelope + **N lines** in `agent_payload`; all N jobs processed or routed to retry/error.
2. **DO/GET/LIKE:** same batch pattern; `grades_encoded_notes` tails persisted per job when present.
3. **Volume:** with 2000 eligible jobs and `batch_size=500`, observability shows **1 sequential batch** then **3 parallel batches** (or documented equivalent), not 2000 API calls.
4. **Cache:** timesheets for chunks 2–K show meaningful **cache_read** vs chunk 1 on shared prompt blocks (debug logging acceptable for UAT).
5. **Config:** `dispatch_task` rows match seed intent; admin can tune `batch_size` without code change.
6. Tests: multi-line encoded envelope happy path; chunk splitter + async second wave (unit or component).

## References

* [AST-491](https://linear.app/astralcareermatch/issue/AST-491) — DeepSeek UAT surfaced batch regression.
* [AST-351](https://linear.app/astralcareermatch/issue/AST-351/convert-consult-to-use-encoded-responses) — encoded wire for do/get/like; batch orchestration explicitly deferred.
* [AST-340](https://linear.app/astralcareermatch/issue/AST-340/retry-bad-responses) — `batch_call_mode`, `_warm_then_gather` (repurpose at batch-chunk level).
* Code: `dispatcher._run_unified`, `_warm_then_gather`, `consult._run_batch_consult`, `render_verdict`, `agent._decode_payload`, `database._DISPATCH_TASK_SEED`.

### Comments

#### chuckles — 2026-05-28T18:41:32.292Z
`origin/dev` @ `b89a2871` — AST-500 + AST-491 finish-up landed; both `ftr/*` deleted.

Engineers: merge into `dev-<agent>` — `git fetch origin && git checkout dev-<agent> && git merge origin/dev` (not rebase unless Susan directs).

— Chuckles

#### chuckles — 2026-05-27T20:06:40.012Z
## Manual test steps (§8 complete)

Local **`dev`** now includes **`origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs`** @ **`9fe74470`** (merge commit on `dev`). **Restart app** if running.

1. **Dispatch config:** Admin → Scheduled Actions — confirm **`qualify_job_listings`**, **`evaluate_jd`**, **`consult_do`**, **`consult_get`**, **`consult_like`** have **`batch_call_mode = 1`**; set **`batch_size`** per task.
2. **AST-501 — single-call batch:** Queue **N > 1** jobs at JD evaluation (or qualify); one scheduler tick → **one** assessment per chunk; envelope + **N** encoded lines in **`agent_payload`**.
3. **AST-502 — exhaustion:** Backlog **> batch_size** (e.g. 2000 ÷ 500): chunk **0** first, then remaining chunks **in parallel** after warm delay.
4. **AST-503 — DO/GET/LIKE batch:** Multi-job PASSED_JD → **`consult_do_batch`** path; grades/notes/states match pre-change behavior.
5. **Cache (optional):** Timesheet **cache_read** on parallel chunks vs chunk 0.

**Manifest:** §7.13zf slice — **11 pytest nodes green** on merged `dev`.

**Note:** Merged `dev` keeps AST-491 envelope helpers; AST-500 **strict envelope** runs before coerce on batch consult tasks.

**Not pushed** to `origin/dev` — UAT gate. Reset after UAT fail: stay on merge commit or ask Chuckles.

— Chuckles

#### chuckles — 2026-05-27T04:56:29.323Z
## Radia UAT reality-check — `origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs` @ `9fe74470`

**Scope:** Parent definition + child plans **AST-501**, **AST-502**, **AST-503** vs composite on **`ftr/`** (rebuilt rollup; **`sub/AST-500/*`** deleted). Auditing **`origin/ftr`** — local **`dev`** §8 merge not applied (Susan WIP + bible conflict).

### Parent acceptance criteria
| Criterion | Verdict |
|-----------|---------|
| 1. N>1 JD eval → one call, N lines, per-job states | **PASS** — `_run_batch_consult` + `evaluate_jd_batch`; dispatcher routes `batch_call_mode=1` |
| 2. Same for qualify | **PASS** — `qualify_job_listings` batch path |
| 3. DO/GET/LIKE batch orchestration | **PASS** — seed `batch_call_mode: 1`; `consult_*_batch` + routing in `run_consult_task` |
| 4. 2000÷500: chunk 0 then parallel 2…K | **PASS** — `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` + head/tail `asyncio.gather` in `dispatcher.py` |
| 5. Cache read on follow-on chunks | **PARTIAL** — warm delay + design present; **needs Susan UAT** on timesheets |
| 6. Admin `batch_size` without deploy | **PASS** — existing dispatch_task admin; **UAT:** confirm live DB rows (seed backfill on new DB only) |
| 7. Outer envelope for all providers | **PASS** — agent decode/tests on ftr; provider-specific UAT with active brain |

### Child stage checklist
| Child | Verdict |
|-------|---------|
| **AST-501** | **PASS** — encoded batch qualify/evaluate; plans on ftr under `docs/features/consult/ast-501-…` |
| **AST-502** | **PASS** — chunk split, cache-warm head, parallel tail; component tests in diff |
| **AST-503** | **PASS** — `consult_do/get/like_batch`, batch map in `run_consult_task` |

### Composite integrity
- **`_DISPATCH_TASK_SEED`:** qualify, evaluate, consult_do/get/like all **`batch_call_mode: 1`** on ftr.
- **Bible §7.13zf** present on ftr with rows for 501–503.
- **Tests:** +`test_dispatcher` exhaustion, +`test_agent` envelope, consult batch coverage in diff.

### Issues → sub-issues
| Sev | Topic | Action |
|-----|-------|--------|
| discuss | Parallel chunk fan-out has **no explicit max concurrency** (e.g. 500) — only `len(chunks)-1` parallel API calls per tick | **None filed** — acceptable for design center 4×500; revisit if roster scales to many chunks |
| advisory | Existing prod DB may still have **`batch_call_mode=0`** on consult rows until admin save | UAT step 1 in prep-uat comment |

**Overall:** **READY FOR SUSAN UAT** on **`ftr@9fe74470`** (or worktree). No **fix-now** gaps vs definition on composite.

— Radia (via Chuckles orchestration)

#### chuckles — 2026-05-27T04:55:36.805Z
## Manual test steps

Prerequisites: app + DB on local **`dev`** after merging **`origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs`** @ **`9fe74470`**. Children **AST-501–503** stay **User Testing** (Hedy). **`sub/AST-500/*`** deleted from origin after rollup.

1. **Dispatch config:** Admin → Scheduled Actions — confirm **`qualify_job_listings`**, **`evaluate_jd`**, **`consult_do`**, **`consult_get`**, **`consult_like`** have **`batch_call_mode = 1`**; set **`batch_size`** per task (no code default).
2. **AST-501 — single-call batch:** Queue **N > 1** jobs at JD evaluation (or qualify); one scheduler tick → **one** assessment per chunk in logs/timesheets; response envelope + **N** encoded lines in **`agent_payload`**.
3. **AST-502 — exhaustion:** Backlog **> batch_size** (e.g. 2000 ÷ 500): chunk **0** completes first, then remaining chunks **in parallel** after warm delay; all jobs leave trigger state (pass/fail/retry/error).
4. **AST-503 — DO/GET/LIKE batch:** Multi-job PASSED_JD (or DO step) → **`consult_do_batch`** path; per-job grades/notes/state match pre-change behavior.
5. **Cache (optional):** Compare timesheet **cache_read** on parallel chunks vs chunk 0 for shared prompt blocks.

**Git (Chuckles):** Rebuilt **`ftr/`** from **`origin/dev`** + merges **501 → 502 → 503** (canonical §7.13zf). Manifest slice green on that tip.

**Local `dev` merge (§8):** Not applied here — your **`dev`** has uncommitted WIP + is **42 commits ahead of `origin/dev`**; merge conflict on bible. To UAT on a clean tree:

```bash
cd astral && git fetch origin
git stash push -m "WIP"   # if needed
git checkout dev && git merge origin/dev
git merge origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs
```

Or test from throwaway: `git worktree add ../astral-uat-500 origin/ftr/AST-500-…`

— Chuckles

#### chuckles — 2026-05-27T03:52:03.366Z
@susan **rollup-child blocked** merging `origin/sub/AST-500/AST-502-…` → `ftr/AST-500-…` after AST-501 rolled up cleanly:

- `docs/ASTRAL_TEST_BIBLE.md`
- `src/core/consult.py`

AST-501 is on `ftr/`; AST-502/503 subs not rolled yet. Children are **User Testing**. Resolve on `sub/AST-500/AST-502` (merge `origin/dev` + refresh vs `ftr` tip) or say the word and Chuckles will retry rollup + prep-uat.

— Chuckles

#### ada — 2026-05-27T03:44:13.837Z
[check-linear]

- **§0a:** `/Users/susan/chuckles/astral-ada` — `git fetch origin`, `git checkout dev-ada`, `git merge origin/dev` → **already up to date** with `origin/dev` (no conflicts this pass).
- **§0b:** `list_issues` `query: "@ada"`, **Team Astral**, **`includeArchived: true`**, paginated → **10** ids; unioned **Astral Consult** narrower pass (subset). **Fallback** not required (`hasNextPage: false` on team query).
- **§1:** Per session **assigned issue ids: (none)** — **no assignee add-on** beyond §0b (MCP `assignee: me` still breaks from this client when tested; not material when allowlist is empty).
- **§2–§4:** `list_comments` on the full §0b union (`AST-359`, `AST-376`, `AST-379`, `AST-453`, `AST-460`, `AST-461`, `AST-480`, `AST-489`, `AST-493`, `AST-494`). Spot-read **AST-500**–**503** threads (context only — **no `@ada`**; children **Hedy**). **No** comment that is (i) not by Ada, (ii) after Ada’s latest `[check-linear]` on that issue where one exists, and (iii) `@ada` / clearly awaiting Ada — **nothing to patch or chase** under this skill pass.
- **Publish refs (**`AST-501`–**503`):** Not merged here — pipeline handoff stays **Hedy** / **`test-astral`** unless Susan assigns Ada or names a stage after this check-linear.
- **§6:** Staying on **`dev-ada`**. Not invoking **`plan-astral`**, **`build-astral`**, **`test-astral`**, **`resolve-astral`**, **`review-astral`**.

#### chuckles — 2026-05-27T02:58:22.301Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-500 (parent) | `ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs` |
| AST-501 | `sub/AST-500/AST-501-encoded-batch-for-qualify-and-evaluate-jd` |
| AST-502 | `sub/AST-500/AST-502-dispatcher-multi-chunk-cache-warm-exhaustion` |
| AST-503 | `sub/AST-500/AST-503-batch-do-get-like-consult-orchestration` |

**Sequence:** AST-501 → AST-502 (`blockedBy`) → AST-503 (`blockedBy`). All assigned **Hedy**.

— Chuckles

#### chuckles — 2026-05-27T02:53:38.349Z
@susan — **define-linear** on [AST-500](https://linear.app/astralcareermatch/issue/AST-500): structured definition is prepended on the ticket; your earlier technical brief is under **Original brief**.

Please answer on the ticket (or here) so we can close **Open questions** and you can move to **Todo** when ready for dispatch:

1. **Default batch sizes** — Is **500** the target default for **all** encoded consult steps, or different caps per step (qualify vs evaluate vs DO/GET/LIKE)?
2. **Parallel fan-out** — After chunk 1 warms cache, run **all** remaining chunks at once (e.g. 3 parallel for 2000÷500), or cap concurrency?
3. **Exhaustion scope** — Drain the full eligible queue in **one scheduler tick**, or allow follow-on ticks until the trigger-state queue is empty?
4. **Partial chunk failure** — Confirm per-job **retry** states for omitted/garbled positions (not whole-chunk error unless envelope failure).
5. **Phasing** — One epic with ordered children, or separate UAT-able milestones?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
