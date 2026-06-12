# AST-445 — Investigate suspicious local run of evaluate_jd: findings and fix plan

**Linear:** [AST-445 — Investigate suspicious local run of evaluate_jd: findings and fix plan](https://linear.app/astralcareermatch/issue/AST-445/investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan)  
**Parent:** [AST-441 — Investigate suspicious local run of evaluate_jd](https://linear.app/astralcareermatch/issue/AST-441/investigate-suspicious-local-run-of-evaluate-jd)  
**Feature ref:** `sub/AST-441/AST-445-investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan` (origin only)

## Summary

Phase 1 of **AST-441**: explain batch `evaluate_jd-34e38ddb-6801-4202-9634-808338f58fae` (38 claimed, 37 empty JD slots, 37 × `ERROR_EVALUATE_JD`), document claim → assembly → agent path, and publish a **binding fix plan** (§ Fix plan for AST-446) for a pre-agent JD readiness gate. **No product behavior change** in this ticket beyond investigation artifacts and doc updates.

---

## Execution contract

Stages in order. Do not change claim criteria, `DISPATCH_TASKS`, or `evaluate_jd_batch` behavior until **AST-446**. If local DB lacks batch evidence, use **AST-441** ticket body (`no_cache` block) as primary source and state uncertainty per job ID.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/consult/ast-445-evaluate-jd-investigation-findings.md` | **Deliverable:** findings + pipeline trace + verdict | docs |
| `scripts/spikes/ast445_evaluate_jd_batch_trace.py` | Optional CLI: load jobs by batch id / state, print JD lengths | scripts |
| `debug/spikes/AST-445/` | Optional JSON snapshots (gitignored) | debug |

No changes to `src/core/consult.py` in this ticket.

---

## Stage 1: Trace script (read-only)

**Done when:** `python3 scripts/spikes/ast445_evaluate_jd_batch_trace.py --help` exits 0.

1. Create `scripts/spikes/ast445_evaluate_jd_batch_trace.py` with `argparse`:
   - `--batch-id` optional (default `34e38ddb-6801-4202-9634-808338f58fae` from parent repro).
   - `--states` default `JD_READY,JD_READY_RETRY`.
   - `--out-dir` default `debug/spikes/AST-445/`.
2. Open `ASTRAL_CONFIG["db_dir"]/astral.db` via `sqlite3` + `src.utils.config` path insert (same pattern as **AST-438** spike).
3. For each job in batch (or last N jobs in those states if batch column unavailable):
   - Print `astral_job_id`, `state`, `len(job_data.job_description.strip())`, `updated_at`.
4. Write `summary.json` with counts: `total`, `empty_jd`, `nonempty_jd`, `max_len`, `min_len_nonempty`.
5. `python3 -m py_compile scripts/spikes/ast445_evaluate_jd_batch_trace.py`.

---

## Stage 2: Pipeline documentation

**Done when:** Findings doc § Pipeline trace is complete with code pointers.

1. Create `docs/features/consult/ast-445-evaluate-jd-investigation-findings.md`.
2. Document path with file:line references:
   - Claim: `dispatch_tasks` DB row for `evaluate_jd` (`list_dispatch_tasks()` / `dispatch_task_seed_templates()` in `src/data/database.py`) — `trigger_state` `JD_READY` (and retry path `JD_READY_RETRY` per consult mapping), **state-only** (no JD check). Do **not** cite removed `DISPATCH_TASKS` config.
   - Batch entry: `consult.run_consult_task` → `evaluate_jd_batch`.
   - Assembly: `evaluate_jd_batch` `assemble()` — `enumerate_array("JD LISTINGS", jd_texts, …)` using `job_data["job_description"]` **without** pre-check (`src/core/consult.py` ~646–651).
   - Agent call: `_run_batch_consult` → `do_task`; on partial response, `missing = sent_ids - received_ids` → `retry_state` or `error_state` (`ERROR_EVALUATE_JD`) (~474–487).
3. Paste or summarize **AST-441** `no_cache` excerpt: 37 empty slots + one populated `[index=010]`.
4. Run trace script if local DB available; merge counts into findings. If DB unavailable, state "evidence from AST-441 ticket only."

---

## Stage 3: Root-cause findings and verdict

**Done when:** Findings doc answers AC 1–3 from **AST-441** / **AST-445**.

1. **§ Root cause (plain language):**
   - Claim selected 38 jobs in `JD_READY_RETRY` based on state alone.
   - `job_description` was empty/whitespace in `job_data` for 37 jobs at assembly time.
   - Likely contributors (rank by evidence): manual state reset without re-scrape; JD never populated after list pass; coat-check not invoked on batch path. Per-job proof may be unavailable — say so explicitly.
2. **§ Verdict:**
   - Routing 37 "missing" IDs to `ERROR_EVALUATE_JD` when inputs were empty is **not acceptable** — operator sees agent/parse failure, not "not ready."
   - Desired: exclude not-ready jobs from prompt; observable non-error outcome (see fix plan).
3. Append findings doc to this plan under `## Investigation findings (generated)` or keep as sibling file linked from Linear comment.

---

## Stage 4: Fix plan for AST-446 (normative)

**Done when:** Section below is copied into findings doc and referenced by **AST-446** plan.

### Fix plan (binding for AST-446)

**Goal:** Pre-agent readiness gate in `evaluate_jd_batch` **after** claim, **before** `do_task`. Claim stays state-only.

| Item | Decision |
|------|----------|
| Readiness rule | `jd = (job.get("job_data") or {}).get("job_description") or ""`; ready iff `len(jd.strip()) >= 80` (tunable constant `MIN_JD_CHARS` in `evaluate_jd_batch` or `CONSULT_CONFIG["evaluate_jd"]`) |
| Not-ready outcome state | `PASSED_JOBLIST` — re-enters `scrape_jd` pipeline (`scrape_jd` claims `PASSED_JOBLIST`); **not** `ERROR_EVALUATE_JD`, **not** `FAILED_JD` |
| State machine (AST-446) | In `JOB_STATES`, add `"JD_READY"` and `"JD_READY_RETRY"` to `PASSED_JOBLIST.prior_states` (today only `VALID_TITLE` / `VALID_TITLE_RETRY` — transition from repro batch would raise `ValueError` without this) |
| Not-ready persistence | `tracker.save_job_data(aid, {"jd_readiness_skip": {"reason": "empty_or_short_jd", "chars": len(jd.strip()), "batch_id": batch_id}})` |
| Agent batch | Only `ready_jobs` passed to `_run_batch_consult`; if `ready_jobs` empty, return `{"success": True, "passed": 0, "failed": 0, "total": 0, "skipped": len(not_ready)}` without calling `do_task` |
| Logging | One INFO line per skipped job: title/id → `PASSED_JOBLIST` (readiness skip) |
| Tests | Fixture: 37 empty + 1 populated JD in `JD_READY_RETRY`; assert ≤1 agent call worth of grades, 0 × `ERROR_EVALUATE_JD` for empty inputs |

⚠️ **Decision:** Reuse `PASSED_JOBLIST` (scrape-eligible) with a **minimal** `prior_states` extension — not a new hold state — so operators can re-scrape without rubric/agent error semantics.

**AST-446** implements exactly this table unless Susan comments otherwise on **AST-445** before build.

---

## Revisions

```
Revision 1 — 2026-05-19
Driven by: Chuckles plan review (REVISE) on AST-445 — fix-now PASSED_JOBLIST prior_states; discuss dispatch_tasks DB path.
Changes: Fix plan adds JOB_STATES prior_states row; Stage 2 claim trace cites dispatch_tasks DB, not DISPATCH_TASKS config.
```

---

## Stage 5: Linear handoff

**Done when:** Comment on **AST-445** links findings doc path on branch; **AST-446** unblocked.

1. Post Linear comment with GitHub blob link to findings doc + one-paragraph verdict.
2. Note **AST-446** should read § Fix plan in findings doc.

---

## Self-Assessment

### Scope

**scope-Single-Component** — docs + optional spike script; no consult behavior change.

### Conf

**conf-high** — code path is localized; repro described on parent ticket.

### Risk

**risk-low** — read-only investigation; wrong findings corrected before **AST-446** build.

---

## Self-review vs ASTRAL_CODE_RULES

- Spike output under `debug/spikes/AST-445/` only.
- Fix plan defers state machine edits to **AST-446** with explicit reuse of existing states.

---

## Review

_Build stub — Radia appends findings at Review Posted._

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-441/AST-445-investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan`

### What's solid
| Area | Notes |
|------|--------|
| Acceptance | Findings doc: 37 empty JD slots at assembly; pipeline trace; `ERROR_EVALUATE_JD` on empty inputs **not acceptable**; binding **AST-446** fix plan in findings. |
| Boundaries | No `src/` product changes — investigation only. |
| Spike | Read-only `ast445_evaluate_jd_batch_trace.py` for local batch forensics. |

### Issues
| Severity | Item |
|----------|------|
| **fix-now** | 0 |
| **discuss** | 1 — **AST-446** should adopt findings gate (`min_jd_chars` 80, `PASSED_JOBLIST`, `prior_states`) — already documented; Susan confirm before build. |
| **advisory** | 0 |

### Recommended actions
| Action | Owner |
|--------|--------|
| Cherry-pick doc commit | Ada |
| Implement gate in **AST-446** per findings § Fix plan | Ada |

## Resolution

**2026-05-22 — Review Posted → User Testing (Ada)**

- **fix-now:** none — investigation deliverables only; gate implementation is **AST-446**.
- **Action:** Merged Radia doc commit `b3a53095` on `sub/AST-441/AST-445-investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan`; no product commits on this ticket.
- **Discuss:** **AST-446** implements findings § Fix plan (confirmed in Radia review).
